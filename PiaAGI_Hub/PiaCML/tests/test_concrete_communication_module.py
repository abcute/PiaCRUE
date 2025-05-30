import unittest
import os
import sys

# Adjust path to import from the parent directory (PiaCML)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from concrete_communication_module import ConcreteCommunicationModule
except ImportError:
    if 'ConcreteCommunicationModule' not in globals(): # Fallback for different execution contexts
        from PiaAGI_Hub.PiaCML.concrete_communication_module import ConcreteCommunicationModule

class TestConcreteCommunicationModule(unittest.TestCase):

    def setUp(self):
        self.comm = ConcreteCommunicationModule()
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_initial_status(self):
        status = self.comm.get_module_status()
        self.assertEqual(status['active_dialogues_count'], 0)
        self.assertEqual(status['default_language'], 'en-US') # As per concrete impl
        self.assertIn('direct_inform', status['loaded_strategies_conceptual'])
        self.assertEqual(status['module_type'], 'ConcreteCommunicationModule')

    def test_process_incoming_text_weather_query(self):
        raw = "What is the weather in London like?"
        processed = self.comm.process_incoming_communication(raw, "text")
        self.assertEqual(processed['type'], 'user_utterance')
        self.assertEqual(processed['semantic_content']['intent'], 'query_weather')
        self.assertEqual(processed['semantic_content']['entities']['location'], 'London')

    def test_process_incoming_text_greeting(self):
        raw = "Hi there"
        processed = self.comm.process_incoming_communication(raw, "text")
        self.assertEqual(processed['semantic_content']['intent'], 'greeting')

    def test_process_incoming_text_provide_name(self):
        raw = "Hello, my name is Bob."
        processed = self.comm.process_incoming_communication(raw, "text")
        self.assertEqual(processed['semantic_content']['intent'], 'provide_name')
        self.assertEqual(processed['semantic_content']['entities']['name'], 'Bob')

    def test_process_incoming_unsupported_modality(self):
        raw = {"data": "some_audio_data"}
        processed = self.comm.process_incoming_communication(raw, "audio")
        self.assertEqual(processed['semantic_content']['intent'], 'unsupported_modality_or_type')


    def test_generate_outgoing_inform_weather(self):
        abstract_msg = {'intent_to_convey': 'inform_weather', 'data': {'location': 'Paris', 'forecast': 'rainy'}}
        generated = self.comm.generate_outgoing_communication(abstract_msg, "user1")
        self.assertEqual(generated['modality'], 'text')
        self.assertEqual(generated['content'], "The weather in Paris is rainy.")
        self.assertEqual(generated['metadata']['strategy_used'], 'direct_inform')

    def test_generate_outgoing_greet_back_with_name(self):
        abstract_msg = {'intent_to_convey': 'greet_back', 'data': {'name': 'Alice'}}
        generated = self.comm.generate_outgoing_communication(abstract_msg, "user_alice")
        self.assertEqual(generated['content'], "Hello, Alice!")
        self.assertEqual(generated['metadata']['strategy_used'], 'simple_greeting')

    def test_generate_outgoing_greet_back_no_name(self):
        abstract_msg = {'intent_to_convey': 'greet_back'}
        generated = self.comm.generate_outgoing_communication(abstract_msg, "user_anon")
        self.assertEqual(generated['content'], "Hello!")

    def test_generate_outgoing_unknown_intent(self):
        abstract_msg = {'intent_to_convey': 'fly_to_mars'}
        generated = self.comm.generate_outgoing_communication(abstract_msg, "user_x")
        self.assertEqual(generated['content'], "Sorry, I cannot process the intent: fly_to_mars.")

    def test_manage_dialogue_state_init_update_get(self):
        dialogue_id = "test_chat_001"
        init_result = self.comm.manage_dialogue_state(dialogue_id, action="initiate")
        self.assertEqual(init_result['status'], 'initiated')
        self.assertEqual(init_result['state']['turn_count'], 0)

        turn1_info = {"processed_input": "input1", "generated_output": "output1"}
        update_result1 = self.comm.manage_dialogue_state(dialogue_id, new_turn_info=turn1_info, action="update")
        self.assertEqual(update_result1['status'], 'updated')
        self.assertEqual(update_result1['turn_number'], 1)

        turn2_info = {"processed_input": "input2", "generated_output": "output2"}
        self.comm.manage_dialogue_state(dialogue_id, new_turn_info=turn2_info, action="update")

        history_result = self.comm.manage_dialogue_state(dialogue_id, action="get_history")
        self.assertEqual(len(history_result['history']), 2)
        self.assertEqual(history_result['history'][0], turn1_info)

        summary_result = self.comm.manage_dialogue_state(dialogue_id, action="get_summary")
        # Based on last turn (input2) not matching specific intent rules in concrete impl
        self.assertEqual(summary_result['topic'], 'unknown')
        self.assertEqual(summary_result['turn_count'], 2)

        # Test custom context
        custom_ctx_set = self.comm.manage_dialogue_state(dialogue_id, new_turn_info={'data': {'key1': 'val1'}}, action="set_custom_context")
        self.assertEqual(custom_ctx_set['custom_context']['key1'], 'val1')
        custom_ctx_get = self.comm.manage_dialogue_state(dialogue_id, action="get_custom_context")
        self.assertEqual(custom_ctx_get['custom_context']['key1'], 'val1')


        close_result = self.comm.manage_dialogue_state(dialogue_id, action="close")
        self.assertEqual(close_result['status'], 'closed')
        self.assertNotIn(dialogue_id, self.comm._dialogue_states)

        # Error on non-existent dialogue
        error_result = self.comm.manage_dialogue_state("non_existent_id", action="get_history")
        self.assertEqual(error_result['status'], 'error')


    def test_apply_communication_strategy_default(self):
        result = self.comm.apply_communication_strategy("any_goal", {}, {}, [])
        self.assertEqual(result['chosen_strategy'], "default_direct_inform")

    def test_apply_communication_strategy_specific(self):
        result = self.comm.apply_communication_strategy(
            "explain_complex_topic_A", {}, {}, ['RaR_Reasoning', 'direct_inform']
        )
        self.assertEqual(result['chosen_strategy'], "RaR_Reasoning")
        self.assertTrue(result['parameters']['emphasize_confidence_level'])

    def test_apply_communication_strategy_first_available(self):
        result = self.comm.apply_communication_strategy("other_goal", {}, {}, ['strat1', 'strat2'])
        self.assertEqual(result['chosen_strategy'], "strat1")


if __name__ == '__main__':
    unittest.main()
