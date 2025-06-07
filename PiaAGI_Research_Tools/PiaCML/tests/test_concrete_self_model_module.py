import unittest
import asyncio
import uuid
from typing import List, Any, Dict
from datetime import datetime, timezone # For payloads

# Adjust path for consistent imports
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    from PiaAGI_Research_Tools.PiaCML.message_bus import MessageBus
    from PiaAGI_Research_Tools.PiaCML.core_messages import (
        GenericMessage, GoalUpdatePayload, ActionEventPayload,
        EmotionalStateChangePayload, PerceptDataPayload, SelfKnowledgeConfidenceUpdatePayload
    )
    from PiaAGI_Research_Tools.PiaCML.concrete_self_model_module import ConcreteSelfModelModule, SelfAttributes # Import data classes if needed for assertions
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from message_bus import MessageBus
    from core_messages import (
        GenericMessage, GoalUpdatePayload, ActionEventPayload,
        EmotionalStateChangePayload, PerceptDataPayload, SelfKnowledgeConfidenceUpdatePayload
    )
    from concrete_self_model_module import ConcreteSelfModelModule, SelfAttributes


class TestConcreteSelfModelModuleIntegration(unittest.TestCase):

    def setUp(self):
        self.bus = MessageBus()
        self.module_id = f"TestSelfModelModule_{str(uuid.uuid4())[:8]}"
        # Module instantiated per test method for a clean state
        self.received_confidence_updates: List[GenericMessage] = []

    def _confidence_update_listener(self, message: GenericMessage):
        if isinstance(message.payload, SelfKnowledgeConfidenceUpdatePayload):
            self.received_confidence_updates.append(message)

    def tearDown(self):
        self.received_confidence_updates.clear()

    # --- Test Subscription Handlers and Internal State Updates ---
    def test_handle_goal_update_updates_attributes(self):
        self_model = ConcreteSelfModelModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            goal1 = GoalUpdatePayload("g1", "Goal 1", 0.8, "ACTIVE", "TestSystem")
            goal2 = GoalUpdatePayload("g2", "Goal 2", 0.9, "PENDING", "TestSystem")
            bus_msg1 = GenericMessage("MotSys", "GoalUpdate", goal1)
            bus_msg2 = GenericMessage("MotSys", "GoalUpdate", goal2)

            self.bus.publish(bus_msg1)
            self.bus.publish(bus_msg2)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self_model.attributes.active_goals_summary), 2)
            # Goals are sorted by priority in the handler
            self.assertEqual(self_model.attributes.active_goals_summary[0]["goal_id"], "g2")
            self.assertEqual(self_model.attributes.active_goals_summary[1]["goal_id"], "g1")

            # Test update
            goal2_updated = GoalUpdatePayload("g2", "Goal 2 Updated", 0.7, "ACTIVE", "TestSystem")
            self.bus.publish(GenericMessage("MotSys", "GoalUpdate", goal_payload2_updated))
            await asyncio.sleep(0.01)

            self.assertEqual(len(self_model.attributes.active_goals_summary), 2)
            self.assertEqual(self_model.attributes.active_goals_summary[0]["goal_id"], "g1") # g1 now higher
            goal_g2_in_summary = next(g for g in self_model.attributes.active_goals_summary if g["goal_id"] == "g2")
            self.assertEqual(goal_g2_in_summary["priority"], 0.7)
            self.assertEqual(self_model._handled_message_counts["GoalUpdate"], 3)
        asyncio.run(run_test_logic())

    def test_handle_action_event_updates_performance_and_autobiography(self):
        self_model = ConcreteSelfModelModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            initial_autobiography_count = len(self_model.autobiography.entries)
            initial_confidence = self_model.attributes.confidence_in_capabilities

            action_event = ActionEventPayload(
                action_command_id="cmd_test_eval", action_type="test_skill_action", status="SUCCESS",
                outcome={"goal_id": "g_eval", "details": "Task completed effectively."}
            )
            bus_msg = GenericMessage("ExecSys", "ActionEvent", action_event)
            self.bus.publish(bus_msg)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self_model.autobiography.entries), initial_autobiography_count + 1)
            self.assertTrue("cmd_test_eval" in self_model.autobiography.entries[-1].description)
            self.assertTrue(self_model.attributes.confidence_in_capabilities > initial_confidence or initial_confidence == 1.0)
            self.assertEqual(self_model._handled_message_counts["ActionEvent"], 1)

            # Test failure
            action_event_fail = ActionEventPayload(
                action_command_id="cmd_test_fail", action_type="another_action", status="FAILURE",
                outcome={"goal_id": "g_eval_fail", "reason": "Critical error"}
            )
            initial_confidence_before_fail = self_model.attributes.confidence_in_capabilities
            self.bus.publish(GenericMessage("ExecSys", "ActionEvent", action_event_fail))
            await asyncio.sleep(0.01)
            self.assertEqual(len(self_model.autobiography.entries), initial_autobiography_count + 2)
            self.assertTrue(self_model.attributes.confidence_in_capabilities < initial_confidence_before_fail or initial_confidence_before_fail == 0.0)

        asyncio.run(run_test_logic())

    def test_handle_emotional_state_change_updates_attributes(self):
        self_model = ConcreteSelfModelModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            emo_profile = {"valence": 0.6, "arousal": 0.4, "dominance": 0.2}
            emo_payload = EmotionalStateChangePayload(current_emotion_profile=emo_profile, intensity=0.4)
            bus_msg = GenericMessage("EmoSys", "EmotionalStateChange", emo_payload)

            self.bus.publish(bus_msg)
            await asyncio.sleep(0.01)

            self.assertIsNotNone(self_model.attributes.current_emotional_summary)
            self.assertEqual(self_model.attributes.current_emotional_summary, emo_profile)
            self.assertEqual(self_model._handled_message_counts["EmotionalStateChange"], 1)
        asyncio.run(run_test_logic())

    def test_handle_percept_data_self_relevant_updates_log(self):
        self_model = ConcreteSelfModelModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            percept_content = "Log this for self-model analysis."
            percept_payload = PerceptDataPayload("p_self", "text", percept_content, datetime.now(timezone.utc))
            # Message targeted at self_model
            bus_msg = GenericMessage("PercSys", "PerceptData", percept_payload, metadata={"target_component": "self_model"})

            self.bus.publish(bus_msg)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self_model._self_related_percepts), 1)
            self.assertEqual(self_model._self_related_percepts[0].content, percept_content)
            self.assertEqual(self_model._handled_message_counts["PerceptData"], 1)

            # Message not targeted, should be ignored by this specific log
            percept_payload_other = PerceptDataPayload("p_other", "text", "General percept", datetime.now(timezone.utc))
            bus_msg_other = GenericMessage("PercSys", "PerceptData", percept_payload_other) # No specific metadata
            self.bus.publish(bus_msg_other)
            await asyncio.sleep(0.01)
            self.assertEqual(len(self_model._self_related_percepts), 1) # Count should not change
            # However, the handler might still increment the general "PerceptData" count if not filtering there for logging
            # The current handler only appends if targeted, so count remains 1. If it logged all percepts, it'd be 2.

        asyncio.run(run_test_logic())

    # --- Test Publishing SelfKnowledgeConfidenceUpdate ---
    def test_update_confidence_publishes_message(self):
        self_model = ConcreteSelfModelModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            self.bus.subscribe(self.module_id, "SelfKnowledgeConfidenceUpdate", self._confidence_update_listener)

            item_id = "k_concept_X"
            item_type = "knowledge"
            new_confidence = 0.88
            source = "successful_application"

            self_model.update_confidence(item_id, item_type, new_confidence, source)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_confidence_updates), 1)
            msg = self.received_confidence_updates[0]
            self.assertEqual(msg.source_module_id, self.module_id)
            self.assertEqual(msg.message_type, "SelfKnowledgeConfidenceUpdate")

            payload: SelfKnowledgeConfidenceUpdatePayload = msg.payload
            self.assertEqual(payload.item_id, item_id)
            self.assertEqual(payload.item_type, item_type)
            self.assertEqual(payload.new_confidence, new_confidence)
            self.assertEqual(payload.source_of_update, source)
            self.assertIsNone(payload.previous_confidence) # Initially None
        asyncio.run(run_test_logic())

    def test_update_confidence_no_bus(self):
        self_model_no_bus = ConcreteSelfModelModule(message_bus=None, module_id="NoBusSelfModel")
        try:
            self_model_no_bus.update_confidence("k_no_bus", "knowledge", 0.5, "test_no_bus_event")
        except Exception as e:
            self.fail(f"update_confidence raised an exception with no bus: {e}")
        self.assertEqual(len(self.received_confidence_updates), 0) # Listener is on self.bus

    # --- Test get_status ---
    def test_get_module_status(self):
        self_model = ConcreteSelfModelModule(message_bus=self.bus, module_id=self.module_id)
        status = self_model.get_module_status()
        self.assertEqual(status["module_id"], self.module_id)
        self.assertTrue(status["message_bus_configured"])
        self.assertEqual(status["active_goals_summary_count"], 0)
        self.assertEqual(status["self_related_percepts_count"], 0)
        self.assertEqual(status["autobiography_entries_count"], 0)

        # Simulate some activity
        async def run_activity():
            goal1 = GoalUpdatePayload("g1_status", "Goal Status", 0.8, "ACTIVE", "Test")
            self.bus.publish(GenericMessage("MotSys", "GoalUpdate", goal1))
            await asyncio.sleep(0.01)
        asyncio.run(run_activity())

        status_after_activity = self_model.get_module_status()
        self.assertEqual(status_after_activity["active_goals_summary_count"], 1)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
```
