import unittest
import os
import sys

# Adjust path to import from the parent directory (PiaCML)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    from PiaAGI_Research_Tools.PiaCML.concrete_communication_module import ConcreteCommunicationModule
    from PiaAGI_Research_Tools.PiaCML.message_bus import MessageBus
    from PiaAGI_Research_Tools.PiaCML.core_messages import GenericMessage
except ImportError:
    # Fallback for scenarios where the relative import might fail
    # This structure might be simplified if path issues are resolved consistently across tests
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from concrete_communication_module import ConcreteCommunicationModule
    try:
        from message_bus import MessageBus
        from core_messages import GenericMessage
    except ImportError:
        MessageBus = None
        GenericMessage = None


import uuid # For module_id
from typing import List, Dict, Any # For type hints

class TestConcreteCommunicationModule(unittest.TestCase):

    def setUp(self):
        self.bus = MessageBus() if MessageBus else None # Handle case where MessageBus might be None due to import error
        self.module_id = f"TestCommModule_{str(uuid.uuid4())[:8]}"
        # Instantiate with bus and module_id
        self.comm = ConcreteCommunicationModule(message_bus=self.bus, module_id=self.module_id)

        self.received_processed_inputs: List[GenericMessage] = []
        self.received_deliver_content: List[GenericMessage] = [] # New

        if self.bus:
            self.bus.subscribe(self.module_id, "IncomingCommunicationProcessed", self._processed_input_listener)
            self.bus.subscribe(self.module_id, "DeliverCommunicationContent", self._deliver_content_listener) # New

        self._original_stdout = sys.stdout
        # Comment out to see module's internal print/log statements during tests
        # sys.stdout = open(os.devnull, 'w')

    def _processed_input_listener(self, message: GenericMessage):
        if message.message_type == "IncomingCommunicationProcessed":
            self.received_processed_inputs.append(message)

    def _deliver_content_listener(self, message: GenericMessage): # New
        if message.message_type == "DeliverCommunicationContent" and isinstance(message.payload, dict):
            self.received_deliver_content.append(message)

    def tearDown(self):
        # if not isinstance(sys.stdout, io.TextIOWrapper): # Avoid closing if not a file
        #    sys.stdout.close()
        sys.stdout = self._original_stdout
        self.received_processed_inputs.clear()
        self.received_deliver_content.clear() # New


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

    def test_publish_processed_input(self):
        if not self.bus or not GenericMessage:
            self.skipTest("MessageBus or GenericMessage not available for this test.")

        raw_input_data = "Test input for publishing"
        source_modality = "test_modality"
        dialogue_id = "dialogue_test_123"
        original_msg_id = "orig_msg_abc"

        # 1. Get processed output
        processed_output = self.comm.process_incoming_communication(raw_input_data, source_modality)

        # 2. Call the new publish method
        published_message_id = self.comm.publish_processed_input(
            processed_output,
            source_dialogue_id=dialogue_id,
            original_message_id=original_msg_id
        )
        self.assertIsNotNone(published_message_id)

        # 3. Verify the listener received the message
        self.assertEqual(len(self.received_processed_inputs), 1)
        received_message = self.received_processed_inputs[0]

        self.assertEqual(received_message.message_type, "IncomingCommunicationProcessed")
        self.assertEqual(received_message.source_module_id, self.module_id)

        payload = received_message.payload
        self.assertIsInstance(payload, dict)
        self.assertEqual(payload.get("type"), processed_output.get('type'))
        self.assertEqual(payload.get("semantic_content"), processed_output.get('semantic_content'))
        self.assertEqual(payload.get("raw_input_ref"), raw_input_data)
        self.assertEqual(payload.get("processing_modality"), source_modality)
        self.assertEqual(payload.get("source_dialogue_id"), dialogue_id)
        self.assertEqual(payload.get("original_message_id"), original_msg_id)

        # Check internal log for publish message
        self.assertTrue(any(f"Published 'IncomingCommunicationProcessed' message (ID: {published_message_id})" in log_msg for log_msg in self.comm._log))

    def test_publish_processed_input_no_bus(self):
        comm_no_bus = ConcreteCommunicationModule(message_bus=None) # Explicitly no bus
        processed_output = comm_no_bus.process_incoming_communication("test", "text")
        result_id = comm_no_bus.publish_processed_input(processed_output)
        self.assertIsNone(result_id)
        self.assertTrue(any("ERROR: Message bus or GenericMessage not available" in log_msg for log_msg in comm_no_bus._log))

    # --- Tests for Part 2: Outgoing Communication Flow ---

    def test_handle_generate_outgoing_command_publishes_deliver_content(self):
        if not self.bus or not GenericMessage:
            self.skipTest("MessageBus or GenericMessage not available for this test.")

        # Ensure asyncio event loop is handled correctly if bus publish is async
        # For the current synchronous bus, direct call is fine.
        # If bus becomes async, this test would need to be run within asyncio.run()
        # or use self.loop.run_until_complete for older Python versions.

        command_payload_dict = {
            "abstract_message": {'intent_to_convey': 'inform_weather', 'data': {'location': 'Mars', 'forecast': 'cold and dusty'}},
            "target_recipient_id": "MarsRover7",
            "desired_effect": "inform_rover_operator",
            "source_dialogue_id": "diag_mars_ops_42",
            "original_request_id": "cmd_req_mars_weather_001"
        }
        command_message = GenericMessage(
            source_module_id="TestPlannerModule", # Simulating another module sending this command
            message_type="GenerateOutgoingCommunicationCommand",
            payload=command_payload_dict
        )

        # Publishing the command to the bus should trigger _handle_generate_outgoing_command
        self.bus.publish(command_message)

        # For a synchronous bus, the handler and subsequent publish should have occurred immediately.
        # If the bus were async, await asyncio.sleep(0.01) might be needed here.

        self.assertEqual(len(self.received_deliver_content), 1, "DeliverCommunicationContent message was not received.")
        received_msg = self.received_deliver_content[0]

        self.assertEqual(received_msg.message_type, "DeliverCommunicationContent")
        self.assertEqual(received_msg.source_module_id, self.module_id) # Comm module should be the source

        deliver_payload = received_msg.payload
        self.assertEqual(deliver_payload.get("content"), "The weather in Mars is cold and dusty.")
        self.assertEqual(deliver_payload.get("modality"), "text")
        self.assertEqual(deliver_payload.get("target_recipient_id"), "MarsRover7")
        self.assertEqual(deliver_payload.get("source_dialogue_id"), "diag_mars_ops_42")
        self.assertEqual(deliver_payload.get("original_command_id"), "cmd_req_mars_weather_001")
        self.assertTrue(any(f"Published 'DeliverCommunicationContent' message (ID: {received_msg.message_id})" in log_msg for log_msg in self.comm._log))

    def test_handle_generate_outgoing_command_malformed_payload(self):
        if not self.bus or not GenericMessage:
            self.skipTest("MessageBus or GenericMessage not available for this test.")

        malformed_command_payload = {
            # Missing 'abstract_message' and 'target_recipient_id'
            "desired_effect": "cause_confusion"
        }
        command_message = GenericMessage(
            source_module_id="TestBadActorModule",
            message_type="GenerateOutgoingCommunicationCommand",
            payload=malformed_command_payload # type: ignore
        )

        initial_log_count = len(self.comm._log)
        self.bus.publish(command_message)

        self.assertEqual(len(self.received_deliver_content), 0, "No DeliverCommunicationContent message should be published for malformed command.")

        # Check logs for error message
        found_error_log = False
        for log_msg in self.comm._log[initial_log_count:]:
            if "ERROR: Command payload missing 'abstract_message' or 'target_recipient_id'" in log_msg:
                found_error_log = True
                break
        self.assertTrue(found_error_log, "Error message for malformed payload not found in logs.")


if __name__ == '__main__':
    unittest.main()
