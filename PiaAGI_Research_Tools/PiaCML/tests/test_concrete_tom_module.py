import unittest
import os
import sys

# Adjust path to import from the parent directory (PiaCML)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from concrete_tom_module import ConcreteTheoryOfMindModule
except ImportError:
    # Fallback for different execution contexts
    if 'ConcreteTheoryOfMindModule' not in globals():
        from PiaAGI_Hub.PiaCML.concrete_tom_module import ConcreteTheoryOfMindModule

class TestConcreteTheoryOfMindModule(unittest.TestCase):

    def setUp(self):
        self.tom = ConcreteTheoryOfMindModule()
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_initial_get_agent_model(self):
        self.assertIsNone(self.tom.get_agent_model("agent_x"))

    def test_update_and_get_agent_model(self):
        agent_id = "agent_alpha"
        data1 = {"belief": "sky_is_blue"}
        self.tom.update_agent_model(agent_id, data1)
        model1 = self.tom.get_agent_model(agent_id)
        self.assertIsNotNone(model1)
        self.assertEqual(model1['belief'], "sky_is_blue")
        self.assertEqual(model1['interaction_count'], 0) # Defaulted by update

        data2 = {"preference": "likes_rain", "interaction_count": 1}
        self.tom.update_agent_model(agent_id, data2)
        model2 = self.tom.get_agent_model(agent_id)
        self.assertEqual(model2['belief'], "sky_is_blue") # Should merge, not overwrite all
        self.assertEqual(model2['preference'], "likes_rain")
        self.assertEqual(model2['interaction_count'], 1)

        # Test deep update for dictionaries
        data3 = {"belief": {"weather": "sunny", "temperature": "warm"}}
        self.tom.update_agent_model(agent_id, {"belief": {"weather": "cloudy"}})
        model3 = self.tom.get_agent_model(agent_id)
        self.assertEqual(model3['belief']['weather'], "cloudy") # existing dict updated
        # self.assertNotIn('temperature', model3['belief']) # if it was a shallow update, this would fail

    def test_infer_mental_state_new_agent_simple_desire(self):
        agent_id = "agent_beta"
        observables = {'utterance': "I really want that cookie!", 'expression': 'pointing', 'affective_cues': ['eager']}
        inferred = self.tom.infer_mental_state(agent_id, observables)

        self.assertIn('desire_state', inferred)
        self.assertEqual(inferred['desire_state'].get('goal'), "obtain_cookie")
        self.assertTrue(inferred['belief_state'].get("wants_cookie"))
        self.assertEqual(inferred['confidence_of_inference'], 0.5) # Default for this rule

        agent_model = self.tom.get_agent_model(agent_id)
        self.assertIsNotNone(agent_model)
        self.assertEqual(agent_model['interaction_count'], 1)
        self.assertEqual(len(agent_model['inferred_mental_states_log']), 1)

    def test_infer_mental_state_emotional_cue_happy(self):
        agent_id = "agent_gamma"
        observables = {'affective_cues': ['happy', 'laughing'], 'expression': 'smiling wide'}
        inferred = self.tom.infer_mental_state(agent_id, observables)
        self.assertEqual(inferred['emotional_state_inferred']['type'], 'positive_generic')
        self.assertGreaterEqual(inferred['confidence_of_inference'], 0.4)

    def test_infer_mental_state_emotional_cue_sad(self):
        agent_id = "agent_delta"
        observables = {'utterance': "Oh no...", 'affective_cues': ['sad']}
        inferred = self.tom.infer_mental_state(agent_id, observables)
        self.assertEqual(inferred['emotional_state_inferred']['type'], 'negative_generic')
        self.assertGreaterEqual(inferred['confidence_of_inference'], 0.4)

    def test_infer_mental_state_no_specific_rules_hit(self):
        agent_id = "agent_epsilon"
        observables = {'utterance': "The sky is blue today."}
        inferred = self.tom.infer_mental_state(agent_id, observables)
        # Check default emotional state and low confidence
        self.assertEqual(inferred['emotional_state_inferred']['type'], 'neutral')
        self.assertEqual(inferred['confidence_of_inference'], 0.3)
        # Check that an agent model was still created/updated
        agent_model = self.tom.get_agent_model(agent_id)
        self.assertIsNotNone(agent_model)
        self.assertEqual(agent_model['interaction_count'], 1)


    def test_multiple_inferences_update_log_and_count(self):
        agent_id = "agent_zeta"
        self.tom.infer_mental_state(agent_id, {'utterance': "First."})
        self.tom.infer_mental_state(agent_id, {'utterance': "Second."})
        agent_model = self.tom.get_agent_model(agent_id)
        self.assertEqual(agent_model['interaction_count'], 2)
        self.assertEqual(len(agent_model['inferred_mental_states_log']), 2)

if __name__ == '__main__':
    unittest.main()
