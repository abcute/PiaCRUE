import unittest
import os
import sys
import datetime # Added
from unittest.mock import MagicMock # Added

# Adjust path for consistent imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    # Attempt to import directly from the package level due to __init__.py setup
    from PiaAGI_Research_Tools.PiaCML import (
        ConcretePerceptionModule,
        MessageBus,
        GenericMessage,
        PerceptDataPayload
    )
except ModuleNotFoundError as e:
    # print(f"Package-level import error in test_concrete_perception_module.py: {e}")
    # print("Attempting direct local imports as fallback...")
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # Add PiaCML to path
    from concrete_perception_module import ConcretePerceptionModule
    try:
        from message_bus import MessageBus
        from core_messages import GenericMessage, PerceptDataPayload
    except ImportError: # If they are truly missing during fallback
        MessageBus = None
        GenericMessage = None
        PerceptDataPayload = None


class TestConcretePerceptionModule(unittest.TestCase):

    def setUp(self):
        # Note: self.perception is initialized without a bus for some tests
        self.perception = ConcretePerceptionModule()
        self.mock_message_bus = MagicMock(spec=MessageBus)
        self.perception_with_bus = ConcretePerceptionModule(message_bus=self.mock_message_bus)

        self._original_stdout = sys.stdout
        # Comment out print suppression for easier debugging if tests fail
        # sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        # sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_initial_status(self):
        status = self.perception.get_module_status()
        self.assertEqual(status['module_type'], 'ConcretePerceptionModule')
        self.assertIn("text", status['supported_modalities'])
        self.assertIn("dict_mock", status['supported_modalities'])
        self.assertEqual(status['processing_log_count'], 0)
        self.assertEqual(status['last_processed_summary'], "None")
        self.assertIsNone(self.perception.message_bus) # Default no bus

    def test_initial_status_with_bus(self):
        status = self.perception_with_bus.get_module_status()
        self.assertIsNotNone(self.perception_with_bus.message_bus)


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

        entity_names_found = [e['name'] for e in processed_repr['entities']]
        self.assertIn("PiaAGI", entity_names_found)
        self.assertIn("user", entity_names_found)
        self.assertIn("apple", entity_names_found)
        self.assertIn("ball", entity_names_found)
        self.assertEqual(len(processed_repr['entities']), 4)

        action_verbs_found = [a['verb'] for a in processed_repr['actions']]
        self.assertIn("greet", action_verbs_found)
        self.assertIn("see/look", action_verbs_found)
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
        raw_data = [1, 2, 3]
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

    # --- Tests for MessageBus Integration ---
    def test_process_and_publish_stimulus_with_bus(self):
        """Test processing and publishing when message bus is configured."""
        # self.perception_with_bus is initialized with a mock_bus in setUp

        raw_stimulus_data = "Test stimulus for publishing"
        modality = "text"
        source_ts = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=10)

        message_id = self.perception_with_bus.process_and_publish_stimulus(raw_stimulus_data, modality, source_ts)

        self.assertIsNotNone(message_id)
        # Default GenericMessage ID is a UUID string
        self.assertIsInstance(message_id, str)

        self.mock_message_bus.publish.assert_called_once()
        args, kwargs = self.mock_message_bus.publish.call_args
        self.assertEqual(len(args), 1) # Should be called with one positional arg (the message)
        published_message = args[0]

        self.assertIsInstance(published_message, GenericMessage)
        self.assertEqual(published_message.message_type, "PerceptData")
        self.assertEqual(published_message.source_module_id, "ConcretePerceptionModule_01") # Default in module

        self.assertIsInstance(published_message.payload, PerceptDataPayload)
        self.assertEqual(published_message.payload.modality, modality)
        self.assertEqual(published_message.payload.content, f"processed_{raw_stimulus_data}")
        self.assertEqual(published_message.payload.source_timestamp, source_ts)

    def test_process_and_publish_stimulus_without_bus(self):
        """Test that publishing is skipped if no message bus is configured."""
        # self.perception is initialized without a bus in setUp
        raw_stimulus_data = "Another stimulus"
        modality = "dict_mock"
        source_ts = datetime.datetime.now(datetime.timezone.utc)

        # Suppress the "Warning: ... no message bus configured" print for this test
        original_stdout_test = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        message_id = self.perception.process_and_publish_stimulus(raw_stimulus_data, modality, source_ts)
        sys.stdout.close()
        sys.stdout = original_stdout_test # Restore stdout specifically for this test's suppression

        self.assertIsNone(message_id)
        # If self.perception had a mock bus, we could assert it wasn't called.
        # Here, we rely on the None return and the warning print (which we suppressed).


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
