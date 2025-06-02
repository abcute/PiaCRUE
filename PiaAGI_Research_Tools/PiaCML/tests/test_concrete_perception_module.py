import unittest
import os
import sys
import time

# Adjust path to import from the parent directory (PiaCML)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PiaAGI_Research_Tools.PiaCML.concrete_perception_module import ConcretePerceptionModule

class TestConcretePerceptionModule(unittest.TestCase):

    def setUp(self):
        self.perception = ConcretePerceptionModule()
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_initial_status(self):
        status = self.perception.get_status()
        self.assertEqual(status['module_type'], 'ConcretePerceptionModule')
        self.assertIn("text", status['supported_modalities'])
        self.assertIn("dict_mock", status['supported_modalities'])
        self.assertEqual(status['processing_log_count'], 0)
        self.assertEqual(status['last_processed_summary'], "None")
        self.assertIsNone(status['attentional_focus_settings'])

    # --- Tests for process_sensory_input ---
    def test_process_sensory_input_text(self):
        raw_text = "  Hello Pia!  "
        processed = self.perception.process_sensory_input(raw_text, "text")
        self.assertEqual(processed, "hello pia!")

    def test_process_sensory_input_dict(self):
        raw_dict = {"key": "value"}
        processed = self.perception.process_sensory_input(raw_dict, "dict_mock")
        self.assertEqual(processed, raw_dict)

    def test_process_sensory_input_other_modality(self):
        raw_data = [1, 2, 3]
        processed = self.perception.process_sensory_input(raw_data, "audio_stream")
        self.assertEqual(processed, {'type': 'unprocessed_raw', 'data': raw_data})

    # --- Tests for extract_features ---
    def test_extract_features_text(self):
        processed_text = "pia see user give apple and red ball"
        features = self.perception.extract_features(processed_text, "text")

        entity_names = {e['name'] for e in features['entities']}
        action_verbs = {a['verb'] for a in features['actions']}

        self.assertIn("PiaAGI", entity_names)
        self.assertIn("user", entity_names)
        self.assertIn("apple", entity_names)
        self.assertIn("ball", entity_names)
        self.assertEqual(len(features['entities']), 4)

        self.assertIn("see/look", action_verbs)
        self.assertIn("give/pass", action_verbs)
        self.assertEqual(len(features['actions']), 2)
        self.assertEqual(features['sentiment_conceptual'], 'neutral')

    def test_extract_features_dict_camera_mock(self):
        processed_dict = {"sensor_type": "camera", "objects_detected": [{"id": "obj1", "class": "cat"}, {"id": "obj2", "class": "dog"}]}
        features = self.perception.extract_features(processed_dict, "dict_mock")
        self.assertEqual(features['object_count'], 2)
        self.assertEqual(len(features['raw_objects']), 2)
        self.assertEqual(features['raw_objects'][0]['class'], 'cat')

    def test_extract_features_dict_other_mock(self):
        processed_dict = {"sensor_id": "xyz", "value_array": [10, 20, 15]}
        features = self.perception.extract_features(processed_dict, "dict_mock")
        self.assertIn('sensor_id', features['raw_dict_features'])
        self.assertIn('value_array', features['raw_dict_features'])

    def test_extract_features_unsupported(self):
        # Input from an "unprocessed_raw" type from process_sensory_input stage
        unprocessed_output = {'type': 'unprocessed_raw', 'data': [1,2,3]}
        features = self.perception.extract_features(unprocessed_output, "audio_stream") # modality is still audio_stream
        self.assertEqual(features, {'error': 'feature_extraction_unsupported_for_modality_or_type'})

        # Input as a direct list (not from process_sensory_input's specific "unprocessed_raw" dict)
        features_direct_list = self.perception.extract_features([1,2,3], "audio_stream")
        self.assertEqual(features_direct_list, {'error': 'feature_extraction_unsupported_for_modality_or_type'})


    # --- Tests for generate_structured_percept ---
    def test_generate_structured_percept_text(self):
        text_features = {
            "entities": [{"type": "agent", "name": "PiaAGI"}],
            "actions": [{"type": "greet", "verb": "hello"}],
            "sentiment_conceptual": "positive"
        }
        fixed_time = time.time()
        context = {"source_id": "user_A_text", "custom_key": "value", "timestamp": fixed_time}

        percept = self.perception.generate_structured_percept(text_features, "text", context)

        self.assertEqual(percept['type'], "linguistic_input_processed")
        self.assertEqual(percept['modality'], "text")
        self.assertEqual(percept['features_extracted'], text_features)
        self.assertEqual(percept['metadata'], context)
        self.assertAlmostEqual(percept['timestamp'], fixed_time, delta=0.01)
        self.assertEqual(percept['primary_action_type'], "greet") # Corrected: expecting action type

    def test_generate_structured_percept_dict_camera(self):
        dict_features = {'object_count': 1, 'raw_objects': [{'id': 'objX', 'class': 'tree'}]}
        context = {"camera_id": "cam007"}
        fixed_time = time.time()

        percept = self.perception.generate_structured_percept(dict_features, "dict_mock", context)

        self.assertEqual(percept['type'], "structured_object_scene")
        self.assertEqual(percept['modality'], "dict_mock")
        self.assertEqual(percept['features_extracted'], dict_features)
        self.assertEqual(percept['metadata'], context)
        self.assertAlmostEqual(percept['timestamp'], fixed_time, delta=0.01) # No timestamp in context, uses current time

    def test_generate_structured_percept_error_features(self):
        error_features = {'error': 'feature_extraction_failed'}
        percept = self.perception.generate_structured_percept(error_features, "unknown_modality")
        self.assertEqual(percept['type'], "error_percept")
        self.assertEqual(percept['error_details'], 'feature_extraction_failed')


    # --- Test for new placeholder method ---
    def test_set_attentional_focus_placeholder(self):
        focus_details = {"target_type": "text_keywords", "details": ["urgent", "critical"]}
        self.perception.set_attentional_focus(focus_details)
        status = self.perception.get_status()
        self.assertEqual(status['attentional_focus_settings'], focus_details)

    # --- Test processing log updates across stages ---
    def test_processing_log_multi_stage(self):
        self.perception.process_sensory_input("test text", "text")
        self.perception.extract_features("test text", "text")
        self.perception.generate_structured_percept({}, "text")

        status = self.perception.get_status()
        self.assertEqual(status['processing_log_count'], 3)
        # Check if last log entry is from generate_structured_percept
        self.assertEqual(status['last_processed_summary'], "linguistic_input_processed") # Type of percept

if __name__ == '__main__':
    unittest.main()
