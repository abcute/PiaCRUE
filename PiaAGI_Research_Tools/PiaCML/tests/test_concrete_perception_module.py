import unittest
import asyncio
import time
from typing import List, Any, Dict
import uuid
import datetime # Ensure this is imported for datetime.datetime.now()

# Adjust path for consistent imports
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    from PiaAGI_Research_Tools.PiaCML.message_bus import MessageBus
    from PiaAGI_Research_Tools.PiaCML.core_messages import GenericMessage, PerceptDataPayload
    from PiaAGI_Research_Tools.PiaCML.concrete_perception_module import ConcretePerceptionModule
except ModuleNotFoundError:
    # Fallback for local execution if repository structure is not in PYTHONPATH
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from message_bus import MessageBus
    from core_messages import GenericMessage, PerceptDataPayload
    from concrete_perception_module import ConcretePerceptionModule

class TestConcretePerceptionModuleIntegration(unittest.TestCase):

    def setUp(self):
        self.bus = MessageBus()
        self.module_id = f"TestPerceptionModule_{str(uuid.uuid4())[:8]}"
        # self.perception_module is initialized in each test or a sub-setup for clarity
        self.received_messages: List[GenericMessage] = []

    def _listener(self, message: GenericMessage): # Sync listener
        self.received_messages.append(message)

    def tearDown(self):
        self.received_messages.clear()

    def test_publish_text_stimulus(self):
        perception_module = ConcretePerceptionModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            self.bus.subscribe(self.module_id, "PerceptData", self._listener)

            stimulus = "Hello Pia, observe the red apple."
            modality = "text"
            # Use datetime.datetime directly as it's clearer
            timestamp = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=1)

            msg_id = perception_module.process_and_publish_stimulus(stimulus, modality, timestamp)
            self.assertIsNotNone(msg_id, "process_and_publish_stimulus should return a message ID when bus is configured.")

            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_messages), 1, "Listener should have received one message.")

            received_msg = self.received_messages[0]
            self.assertEqual(received_msg.source_module_id, self.module_id)
            self.assertEqual(received_msg.message_type, "PerceptData")
            self.assertIsInstance(received_msg.payload, PerceptDataPayload)

            payload: PerceptDataPayload = received_msg.payload
            self.assertEqual(payload.modality, modality)
            self.assertEqual(payload.source_timestamp, timestamp)

            self.assertIsInstance(payload.content, dict)
            self.assertEqual(payload.content.get("type"), "linguistic_analysis")
            self.assertIn("text", payload.content)
            self.assertEqual(payload.content["text"], stimulus)
            self.assertIn("entities", payload.content)
            self.assertIn("actions", payload.content)

            entities = payload.content["entities"]
            actions = payload.content["actions"]
            self.assertTrue(any(e.get("name") == "PiaAGI" for e in entities), "PiaAGI entity not found")
            self.assertTrue(any(e.get("name") == "apple" for e in entities), "apple entity not found")
            # The module's keyword spotter for "observe" maps to "see/look"
            self.assertTrue(any(a.get("verb") == "see/look" for a in actions), "observe/see/look action not found")

        asyncio.run(run_test_logic())

    def test_publish_dict_mock_stimulus(self):
        perception_module = ConcretePerceptionModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            self.bus.subscribe(self.module_id, "PerceptData", self._listener)

            stimulus = {"sensor_id": "cam01", "detected_objects": ["cat", "mat"]}
            modality = "dict_mock"
            timestamp = datetime.datetime.now(datetime.timezone.utc)

            msg_id = perception_module.process_and_publish_stimulus(stimulus, modality, timestamp)
            self.assertIsNotNone(msg_id)

            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_messages), 1)
            received_msg = self.received_messages[0]
            self.assertEqual(received_msg.source_module_id, self.module_id)
            self.assertIsInstance(received_msg.payload, PerceptDataPayload)

            payload: PerceptDataPayload = received_msg.payload
            self.assertEqual(payload.modality, modality)
            self.assertEqual(payload.source_timestamp, timestamp)

            self.assertIsInstance(payload.content, dict)
            self.assertEqual(payload.content.get("type"), "structured_data")
            self.assertEqual(payload.content.get("data"), stimulus)

        asyncio.run(run_test_logic())

    def test_publish_unsupported_stimulus(self):
        perception_module = ConcretePerceptionModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            self.bus.subscribe(self.module_id, "PerceptData", self._listener)

            stimulus = b"some_audio_bytes_for_unsupported_test" # Changed to avoid conflict if other tests use same
            modality = "audio_stream" # A clearly unsupported modality
            timestamp = datetime.datetime.now(datetime.timezone.utc)

            msg_id = perception_module.process_and_publish_stimulus(stimulus, modality, timestamp)
            self.assertIsNotNone(msg_id)

            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_messages), 1)
            received_msg = self.received_messages[0]
            self.assertEqual(received_msg.source_module_id, self.module_id)
            self.assertIsInstance(received_msg.payload, PerceptDataPayload)

            payload: PerceptDataPayload = received_msg.payload
            self.assertEqual(payload.modality, modality)
            self.assertEqual(payload.source_timestamp, timestamp)

            self.assertIsInstance(payload.content, dict)
            self.assertEqual(payload.content.get("error"), "processing_failed")
            details = payload.content.get("details", "")
            self.assertIn("unsupported_modality", details.lower() if details else "")
            self.assertIn(modality, details if details else "")
            self.assertEqual(payload.content.get("original_modality"), modality)
            self.assertEqual(payload.content.get("original_stimulus_type"), str(type(stimulus)))


        asyncio.run(run_test_logic())

    def test_no_bus_publish_graceful_failure(self):
        # Create a module instance without a message bus
        perception_module_no_bus = ConcretePerceptionModule(message_bus=None, module_id="NoBusPerception")

        stimulus = "Test without bus"
        modality = "text"
        timestamp = datetime.datetime.now(datetime.timezone.utc)

        return_value = perception_module_no_bus.process_and_publish_stimulus(stimulus, modality, timestamp)

        self.assertIsNone(return_value, "process_and_publish_stimulus should return None when no bus is configured.")
        self.assertEqual(len(self.received_messages), 0, "No messages should be received if bus was None.")

    def test_get_module_status(self):
        perception_module = ConcretePerceptionModule(message_bus=self.bus, module_id=self.module_id)
        status = perception_module.get_module_status()
        self.assertEqual(status["module_id"], self.module_id)
        self.assertEqual(status["module_type"], "ConcretePerceptionModule")
        self.assertTrue(status["message_bus_configured"])
        self.assertIn("text", status["supported_modalities"])
        self.assertEqual(status["processing_log_count"], 0)

        # Process one item to change log count (directly calls process_sensory_input, not through bus)
        perception_module.process_sensory_input("test to update log", "text", {})
        status_after = perception_module.get_module_status()
        self.assertEqual(status_after["processing_log_count"], 1)
        self.assertIn("test to update log", status_after["last_processed_summary"])

        # Test status when no bus is configured
        perception_module_no_bus = ConcretePerceptionModule(message_bus=None, module_id="NoBusStatusCheck")
        status_no_bus = perception_module_no_bus.get_module_status()
        self.assertEqual(status_no_bus["module_id"], "NoBusStatusCheck")
        self.assertFalse(status_no_bus["message_bus_configured"])


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
```
