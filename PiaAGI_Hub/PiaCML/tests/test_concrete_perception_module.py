import unittest
import os
import sys

# Adjust path to import from the parent directory (PiaCML)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from concrete_perception_module import ConcretePerceptionModule
except ImportError:
    if 'ConcretePerceptionModule' not in globals(): # Fallback for different execution contexts
        from PiaAGI_Hub.PiaCML.concrete_perception_module import ConcretePerceptionModule

class TestConcretePerceptionModule(unittest.TestCase):

    def setUp(self):
        self.perception = ConcretePerceptionModule()
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_initial_status(self):
        status = self.perception.get_module_status()
        self.assertEqual(status['module_type'], 'ConcretePerceptionModule')
        self.assertIn("text", status['supported_modalities'])
        self.assertIn("dict_mock", status['supported_modalities'])
        self.assertEqual(status['processing_log_count'], 0)
        self.assertEqual(status['last_processed_summary'], "None")

    def test_process_text_input_entities_and_actions(self):
        raw_text = "Hello Pia, can user see the big red apple and the small ball?"
        context = {"session": "s1"}
        percept = self.perception.process_sensory_input(raw_text, "text", context)

        self.assertEqual(percept['raw_input'], raw_text)
        self.assertEqual(percept['modality'], "text")
        self.assertEqual(percept['metadata'], context)

        processed_repr = percept['processed_representation']
        self.assertEqual(processed_repr['type'], "linguistic_analysis")
        self.assertEqual(processed_repr['text'], raw_text)

        # Check entities (order might vary, so check for presence)
        entity_names_found = [e['name'] for e in processed_repr['entities']]
        self.assertIn("PiaAGI", entity_names_found) # "pia" becomes "PiaAGI"
        self.assertIn("user", entity_names_found)
        self.assertIn("apple", entity_names_found)
        self.assertIn("ball", entity_names_found)
        self.assertEqual(len(processed_repr['entities']), 4)

        # Check actions
        action_verbs_found = [a['verb'] for a in processed_repr['actions']]
        self.assertIn("greet", action_verbs_found) # "Hello"
        self.assertIn("see/look", action_verbs_found) # "see"
        self.assertEqual(len(processed_repr['actions']), 2)

        status = self.perception.get_module_status()
        self.assertEqual(status['processing_log_count'], 1)
        self.assertTrue(raw_text[:50] in status['last_processed_summary'])


    def test_process_text_input_no_keywords(self):
        raw_text = "The sky is blue."
        percept = self.perception.process_sensory_input(raw_text, "text")
        processed_repr = percept['processed_representation']
        self.assertEqual(len(processed_repr['entities']), 0)
        self.assertEqual(len(processed_repr['actions']), 0)


    def test_process_dict_mock_input(self):
        raw_dict = {"sensor": "temp_sensor", "value": 25, "unit": "celsius"}
        percept = self.perception.process_sensory_input(raw_dict, "dict_mock")

        self.assertEqual(percept['raw_input'], raw_dict)
        self.assertEqual(percept['modality'], "dict_mock")
        processed_repr = percept['processed_representation']
        self.assertEqual(processed_repr['type'], "structured_data")
        self.assertEqual(processed_repr['data'], raw_dict)

    def test_process_unsupported_modality(self):
        raw_data = [1, 2, 3] # e.g. some list data from an unknown sensor
        percept = self.perception.process_sensory_input(raw_data, "custom_list_sensor")
        processed_repr = percept['processed_representation']
        self.assertEqual(processed_repr['type'], "unsupported_modality")
        self.assertIn("error", processed_repr)

    def test_processing_log_updates(self):
        self.perception.process_sensory_input("first input", "text")
        self.perception.process_sensory_input({"data": "second"}, "dict_mock")
        status = self.perception.get_module_status()
        self.assertEqual(status['processing_log_count'], 2)
        self.assertTrue("second" in status['last_processed_summary'])


if __name__ == '__main__':
    unittest.main()
