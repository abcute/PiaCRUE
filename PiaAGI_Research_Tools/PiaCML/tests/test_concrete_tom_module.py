import unittest
import os
import sys
import datetime
from unittest.mock import MagicMock, call

# Adjust path for consistent imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    from PiaAGI_Research_Tools.PiaCML import (
        ConcreteTheoryOfMindModule,
        MessageBus,
        GenericMessage,
        PerceptDataPayload,
        ToMInferenceUpdatePayload
        # EmotionalStateChangePayload is handled as dict for now
    )
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from concrete_tom_module import ConcreteTheoryOfMindModule
    try:
        from message_bus import MessageBus
        from core_messages import GenericMessage, PerceptDataPayload, ToMInferenceUpdatePayload
    except ImportError:
        MessageBus = None
        GenericMessage = None
        PerceptDataPayload = None
        ToMInferenceUpdatePayload = None

class TestConcreteTheoryOfMindModule(unittest.TestCase):

    def setUp(self):
        self.bus = MessageBus() if MessageBus else None
        self.mock_bus = MagicMock(spec=MessageBus) if MessageBus else None

        self.tom_no_bus = ConcreteTheoryOfMindModule()
        self.tom_with_mock_bus = ConcreteTheoryOfMindModule(message_bus=self.mock_bus)
        self.tom_with_real_bus = ConcreteTheoryOfMindModule(message_bus=self.bus)

        self._original_stdout = sys.stdout
        # To see print statements from the module during tests, comment out the next line
        # sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        # sys.stdout.close()
        sys.stdout = self._original_stdout

    # --- Tests for original direct-call methods (using tom_no_bus) ---
    def test_initial_get_agent_model_no_bus(self):
        self.assertIsNone(self.tom_no_bus.get_agent_model("agent_x"))
        self.assertEqual(len(self.tom_no_bus.recent_inferences), 0)


    def test_update_and_get_agent_model_no_bus(self):
        agent_id = "agent_alpha"
        data1 = {"belief": "sky_is_blue"}
        self.tom_no_bus.update_agent_model(agent_id, data1)
        model1 = self.tom_no_bus.get_agent_model(agent_id)
        self.assertIsNotNone(model1)
        self.assertEqual(model1['belief'], "sky_is_blue")

    # --- New Tests for MessageBus Integration and Refactored infer_mental_state ---

    def test_initialization_with_bus_subscription(self):
        """Test ToMModule initialization with a bus and subscriptions."""
        if not MessageBus: self.skipTest("MessageBus components not available")

        self.assertIsNotNone(self.tom_with_real_bus.message_bus)
        percept_subscribers = self.bus.get_subscribers_for_type("PerceptData")
        emotion_subscribers = self.bus.get_subscribers_for_type("EmotionalStateChange")

        found_percept_sub = any(
            s[0] == "ConcreteTheoryOfMindModule_01" and
            s[1] == self.tom_with_real_bus.handle_percept_for_tom
            for s in percept_subscribers if s
        )
        found_emotion_sub = any(
            s[0] == "ConcreteTheoryOfMindModule_01" and
            s[1] == self.tom_with_real_bus.handle_own_emotion_change_for_tom
            for s in emotion_subscribers if s
        )
        self.assertTrue(found_percept_sub, "ToMModule did not subscribe to PerceptData.")
        self.assertTrue(found_emotion_sub, "ToMModule did not subscribe to EmotionalStateChange.")

    def test_infer_mental_state_publishes_message(self):
        """Test that infer_mental_state publishes a ToMInferenceUpdate message."""
        if not all([MessageBus, GenericMessage, ToMInferenceUpdatePayload]):
            self.skipTest("MessageBus or core message components not available")

        target_agent_id = "user_A"
        evidence = "User A said: I am very happy today!"
        state_to_infer = "emotion_happiness_conjecture"

        inference_payload = self.tom_with_mock_bus.infer_mental_state(target_agent_id, evidence, state_to_infer, "msg_evidence_1")

        self.assertIsNotNone(inference_payload)
        self.assertEqual(len(self.tom_with_mock_bus.recent_inferences), 1)
        self.assertEqual(self.tom_with_mock_bus.recent_inferences[0], inference_payload)

        self.mock_bus.publish.assert_called_once()
        args, _ = self.mock_bus.publish.call_args
        published_message: GenericMessage = args[0]

        self.assertEqual(published_message.message_type, "ToMInferenceUpdate")
        self.assertEqual(published_message.source_module_id, "ConcreteTheoryOfMindModule_01")

        payload: ToMInferenceUpdatePayload = published_message.payload
        self.assertIsInstance(payload, ToMInferenceUpdatePayload)
        self.assertEqual(payload.target_agent_id, target_agent_id)
        self.assertEqual(payload.inferred_state_type, state_to_infer)
        self.assertEqual(payload.inferred_state_value, {"emotion": "happiness", "intensity_qualitative": "moderate"})
        self.assertGreaterEqual(payload.confidence, 0.6)
        self.assertIn("msg_evidence_1", payload.source_evidence_ids)


    def test_infer_mental_state_no_publish_if_no_bus(self):
        """Test infer_mental_state does not attempt publish if no bus is configured."""
        self.assertIsNone(self.tom_no_bus.message_bus)
        self.tom_no_bus.infer_mental_state("user_B", "User B looks sad.", "emotion_sadness_conjecture")
        # No direct way to check mock_bus wasn't called by tom_no_bus as it doesn't have it.
        # This test relies on the internal `if self.message_bus:` check.
        self.assertEqual(len(self.tom_no_bus.recent_inferences), 1) # Should still make inference locally.


    def test_handle_percept_for_tom_triggers_inference_and_publish(self):
        """Test PerceptData message triggers inference and subsequent ToMInferenceUpdate publish."""
        if not all([MessageBus, GenericMessage, PerceptDataPayload, ToMInferenceUpdatePayload]):
            self.skipTest("MessageBus or core message components not available")

        # This mock will capture the ToMInferenceUpdate published by infer_mental_state
        # when triggered by the percept handler in tom_with_real_bus.
        mock_inference_listener = MagicMock(name="inference_listener")
        self.bus.subscribe("InferenceListener", "ToMInferenceUpdate", mock_inference_listener)

        percept_content = "User X mentioned they are feeling sad about the news."
        percept_payload = PerceptDataPayload(
            modality="text",
            content=percept_content,
            source_timestamp=datetime.datetime.now(datetime.timezone.utc),
            percept_id="percept_sad_news_001"
        )
        percept_message = GenericMessage(
            source_module_id="UserInteractionModule",
            message_type="PerceptData",
            payload=percept_payload,
            message_id="msg_user_interaction_001"
        )

        self.bus.publish(percept_message) # This should trigger tom_with_real_bus.handle_percept_for_tom

        self.assertIn(percept_payload, self.tom_with_real_bus.handled_percepts_for_tom)
        self.assertGreaterEqual(len(self.tom_with_real_bus.recent_inferences), 1)

        mock_inference_listener.assert_called_once()
        received_inference_msg: GenericMessage = mock_inference_listener.call_args[0][0]
        self.assertEqual(received_inference_msg.message_type, "ToMInferenceUpdate")

        inference_payload_published: ToMInferenceUpdatePayload = received_inference_msg.payload
        self.assertEqual(inference_payload_published.target_agent_id, "UserInteractionModule") # Based on current logic
        self.assertEqual(inference_payload_published.inferred_state_type, "emotion_sadness_conjecture")
        self.assertIn("msg_user_interaction_001", inference_payload_published.source_evidence_ids)
        self.assertIn("percept_sad_news_001", inference_payload_published.source_evidence_ids)


    def test_handle_own_emotion_change_for_tom(self):
        """Test ToMModule handles agent's own EmotionalStateChange messages."""
        if not MessageBus or not GenericMessage:
            self.skipTest("MessageBus or GenericMessage not available")

        own_emotion_payload = {"valence": -0.8, "arousal": 0.7, "dominance": -0.2} # e.g., agent is feeling fear/distress
        emotion_message = GenericMessage(
            source_module_id="OwnEmotionModule", # Should be agent's own emotion module
            message_type="EmotionalStateChange",
            payload=own_emotion_payload
        )

        self.bus.publish(emotion_message)
        self.assertIn(own_emotion_payload, self.tom_with_real_bus.handled_own_emotions_for_tom)
        # Further tests could check if this state biases future inferences, once that logic exists.

    def test_handle_percept_unexpected_payload(self):
        """Test ToM handles PerceptData message with an unexpected payload type."""
        if not MessageBus or not GenericMessage:
            self.skipTest("MessageBus or GenericMessage not available")

        malformed_msg = GenericMessage(
            source_module_id="TestMalformedSource",
            message_type="PerceptData",
            payload="This is not a PerceptDataPayload"
        )

        # Suppress print for this specific test of error path
        original_stdout_test = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        self.bus.publish(malformed_msg)
        sys.stdout.close()
        sys.stdout = original_stdout_test

        self.assertEqual(len(self.tom_with_real_bus.handled_percepts_for_tom), 0)
        self.assertEqual(len(self.tom_with_real_bus.recent_inferences), 0)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
