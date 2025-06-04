import unittest
from typing import Dict, Any
import sys
import os
import time # For creating GoalUpdatePayload with datetime if needed, though not directly used here
from unittest.mock import MagicMock, call

# Adjust path for consistent imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    from PiaAGI_Research_Tools.PiaCML import (
        ConcreteSelfModelModule,
        MessageBus,
        GenericMessage,
        GoalUpdatePayload, # For testing subscription
        SelfKnowledgeConfidenceUpdatePayload # For testing publishing
    )
except ModuleNotFoundError as e:
    # print(f"Package-level import error in test_concrete_self_model_module.py: {e}")
    # print("Attempting direct local imports as fallback...")
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from concrete_self_model_module import ConcreteSelfModelModule
    try:
        from message_bus import MessageBus
        from core_messages import GenericMessage, GoalUpdatePayload, SelfKnowledgeConfidenceUpdatePayload
    except ImportError:
        MessageBus = None
        GenericMessage = None
        GoalUpdatePayload = None
        SelfKnowledgeConfidenceUpdatePayload = None


class TestConcreteSelfModelModule(unittest.TestCase):

    def setUp(self):
        """Set up instances for each test."""
        self.bus = MessageBus() if MessageBus else None # Real bus for testing subscription
        self.mock_bus = MagicMock(spec=MessageBus) if MessageBus else None # Mock bus for testing publishing

        self.smm_no_bus = ConcreteSelfModelModule()
        self.smm_with_mock_bus = ConcreteSelfModelModule(message_bus=self.mock_bus)
        self.smm_with_real_bus = ConcreteSelfModelModule(message_bus=self.bus)

        self._original_stdout = sys.stdout
        # Comment out print suppression for easier debugging if tests fail
        # sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        """Restore stdout after each test."""
        # sys.stdout.close()
        sys.stdout = self._original_stdout

    # --- Existing tests adapted to use smm_no_bus ---
    def test_initial_confidence_dictionaries_exist(self):
        self.assertTrue(hasattr(self.smm_no_bus, 'knowledge_confidence'))
        self.assertIsInstance(self.smm_no_bus.knowledge_confidence, Dict)
        self.assertTrue(hasattr(self.smm_no_bus, 'capability_confidence'))
        self.assertIsInstance(self.smm_no_bus.capability_confidence, Dict)
        # Test new attribute for message handling
        self.assertTrue(hasattr(self.smm_no_bus, 'handled_goal_updates'))
        self.assertEqual(self.smm_no_bus.handled_goal_updates, [])


    def test_update_confidence_knowledge_no_bus(self): # Renamed
        item_id = "concept_alpha"
        self.assertTrue(self.smm_no_bus.update_confidence(item_id, "knowledge", 0.75, "initial_learning"))
        self.assertEqual(self.smm_no_bus.knowledge_confidence.get(item_id), 0.75)
        self.assertTrue(self.smm_no_bus.update_confidence(item_id, "knowledge", 0.85, "successful_application"))
        self.assertEqual(self.smm_no_bus.knowledge_confidence.get(item_id), 0.85)

    def test_update_confidence_capability_no_bus(self): # Renamed
        item_id = "skill_beta"
        self.assertTrue(self.smm_no_bus.update_confidence(item_id, "capability", 0.60, "training_completion"))
        self.assertEqual(self.smm_no_bus.capability_confidence.get(item_id), 0.60)
        self.assertTrue(self.smm_no_bus.update_confidence(item_id, "capability", 0.70, "consistent_success"))
        self.assertEqual(self.smm_no_bus.capability_confidence.get(item_id), 0.70)

    def test_update_confidence_invalid_type_no_bus(self): # Renamed
        self.assertFalse(self.smm_no_bus.update_confidence("item_gamma", "invalid_type", 0.5))

    def test_update_confidence_clamping_no_bus(self): # Renamed
        self.smm_no_bus.update_confidence("concept_clamp_high", "knowledge", 1.5, "test_high")
        self.assertEqual(self.smm_no_bus.knowledge_confidence.get("concept_clamp_high"), 1.0)
        self.smm_no_bus.update_confidence("concept_clamp_low", "knowledge", -0.5, "test_low")
        self.assertEqual(self.smm_no_bus.knowledge_confidence.get("concept_clamp_low"), 0.0)

    def test_get_confidence_no_bus(self): # Renamed
        self.smm_no_bus.update_confidence("concept_get", "knowledge", 0.88)
        self.assertEqual(self.smm_no_bus.get_confidence("concept_get", "knowledge"), 0.88)
        self.assertIsNone(self.smm_no_bus.get_confidence("non_existent_concept", "knowledge"))

    def test_log_self_assessment_no_bus(self): # Renamed
        self.smm_no_bus.update_confidence("concept_log", "knowledge", 0.91, "test_log")
        expected_log_k = "Self-assessment: Confidence in knowledge 'concept_log' is 0.91."
        self.assertEqual(self.smm_no_bus.log_self_assessment("concept_log", "knowledge"), expected_log_k)
        expected_log_k_non = "Self-assessment: Confidence in knowledge 'non_existent_k' is not found."
        self.assertEqual(self.smm_no_bus.log_self_assessment("non_existent_k", "knowledge"), expected_log_k_non)

    # --- New Tests for MessageBus Integration ---

    def test_initialization_with_bus_subscription(self):
        """Test SMM initialization with a message bus and subscription to GoalUpdate."""
        if not MessageBus: self.skipTest("MessageBus components not available")

        self.assertIsNotNone(self.smm_with_real_bus.message_bus)
        subscribers = self.bus.get_subscribers_for_type("GoalUpdate") # Using the real bus

        found_subscription = any(
            sub[0] == "ConcreteSelfModelModule_01" and
            sub[1] == self.smm_with_real_bus.handle_goal_update_message
            for sub in subscribers
        )
        self.assertTrue(found_subscription, "SMM did not subscribe to GoalUpdate messages.")

    def test_update_confidence_publishes_message(self):
        """Test that update_confidence publishes a SelfKnowledgeConfidenceUpdate message."""
        if not MessageBus or not GenericMessage or not SelfKnowledgeConfidenceUpdatePayload:
            self.skipTest("MessageBus or core message components not available")

        item_id = "concept_publish"
        item_type = "knowledge"
        initial_confidence = 0.6
        new_confidence = 0.8
        source = "test_source_publish"

        self.smm_with_mock_bus.update_confidence(item_id, item_type, initial_confidence, "initial_set") # Set initial
        self.mock_bus.reset_mock() # Reset after initial publish

        self.smm_with_mock_bus.update_confidence(item_id, item_type, new_confidence, source)

        self.mock_bus.publish.assert_called_once()
        args, _ = self.mock_bus.publish.call_args
        published_message: GenericMessage = args[0]

        self.assertIsInstance(published_message, GenericMessage)
        self.assertEqual(published_message.message_type, "SelfKnowledgeConfidenceUpdate")
        self.assertEqual(published_message.source_module_id, "ConcreteSelfModelModule_01")

        payload: SelfKnowledgeConfidenceUpdatePayload = published_message.payload
        self.assertIsInstance(payload, SelfKnowledgeConfidenceUpdatePayload)
        self.assertEqual(payload.item_id, item_id)
        self.assertEqual(payload.item_type, item_type)
        self.assertEqual(payload.new_confidence, new_confidence)
        self.assertEqual(payload.previous_confidence, initial_confidence)
        self.assertEqual(payload.source_of_update, source)

    def test_update_confidence_no_publish_if_no_bus(self):
        """Test that update_confidence does not publish if no bus is configured."""
        # self.smm_no_bus is initialized with message_bus=None
        # self.mock_bus is associated with smm_with_mock_bus, so it shouldn't be called by smm_no_bus

        self.smm_no_bus.update_confidence("concept_no_bus", "knowledge", 0.7, "no_bus_test")
        self.mock_bus.publish.assert_not_called() # Check the mock_bus of smm_with_mock_bus wasn't affected

    def test_handle_goal_update_message(self):
        """Test that SMM handles GoalUpdate messages from the bus."""
        if not MessageBus or not GenericMessage or not GoalUpdatePayload:
            self.skipTest("MessageBus or core message components not available")

        self.assertEqual(len(self.smm_with_real_bus.handled_goal_updates), 0)

        goal_payload = GoalUpdatePayload(
            goal_id="goal_test_123",
            goal_description="Test goal for SMM subscription",
            priority=0.7,
            status="ACTIVE",
            originator="TestMotivationalSystem"
        )
        goal_update_msg = GenericMessage(
            source_module_id="TestMotivationalSystem",
            message_type="GoalUpdate",
            payload=goal_payload
        )

        self.bus.publish(goal_update_msg) # Publish on the real bus smm_with_real_bus is subscribed to

        self.assertEqual(len(self.smm_with_real_bus.handled_goal_updates), 1)
        received_payload = self.smm_with_real_bus.handled_goal_updates[0]
        self.assertIsInstance(received_payload, GoalUpdatePayload)
        self.assertEqual(received_payload.goal_id, "goal_test_123")
        self.assertEqual(received_payload.status, "ACTIVE")

    def test_handle_goal_update_message_unexpected_payload(self):
        """Test SMM handles GoalUpdate with an unexpected payload type."""
        if not MessageBus or not GenericMessage :
            self.skipTest("MessageBus or GenericMessage not available")

        malformed_msg = GenericMessage(
            source_module_id="TestMalformedSource",
            message_type="GoalUpdate",
            payload="This is not a GoalUpdatePayload"
        )

        # Capture stdout to check for print warning
        captured_output = io.StringIO()
        sys.stdout = captured_output

        self.bus.publish(malformed_msg)

        sys.stdout = self._original_stdout # Restore stdout
        output_str = captured_output.getvalue()

        self.assertEqual(len(self.smm_with_real_bus.handled_goal_updates), 0) # Should not append if payload is wrong type
        self.assertIn("SelfModel received GoalUpdate with unexpected payload type: <class 'str'>", output_str)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
