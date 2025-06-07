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
        GenericMessage, PerceptDataPayload, GoalUpdatePayload, ActionEventPayload,
        EmotionalStateChangePayload, LearningOutcomePayload
    )
    from PiaAGI_Research_Tools.PiaCML.concrete_learning_module import ConcreteLearningModule
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from message_bus import MessageBus
    from core_messages import (
        GenericMessage, PerceptDataPayload, GoalUpdatePayload, ActionEventPayload,
        EmotionalStateChangePayload, LearningOutcomePayload
    )
    from concrete_learning_module import ConcreteLearningModule

class TestConcreteLearningModuleIntegration(unittest.TestCase):

    def setUp(self):
        self.bus = MessageBus()
        self.module_id = f"TestLearningModule_{str(uuid.uuid4())[:8]}"
        # Module instantiated per test method for a clean state
        self.received_learning_outcomes: List[GenericMessage] = []

    def _learning_outcome_listener(self, message: GenericMessage):
        if isinstance(message.payload, LearningOutcomePayload):
            self.received_learning_outcomes.append(message)

    def tearDown(self):
        self.received_learning_outcomes.clear()

    # --- Test Subscription Handlers and learn() triggering ---
    def test_handle_percept_data_triggers_learning(self):
        learning_module = ConcreteLearningModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            self.bus.subscribe(self.module_id, "LearningOutcome", self._learning_outcome_listener)

            percept_payload = PerceptDataPayload(percept_id="p_learn1", modality="text", content="new patterns observed", source_timestamp=datetime.now(timezone.utc))
            msg = GenericMessage("PerceptSys", "PerceptData", percept_payload, message_id="percept_msg_learn1")

            self.bus.publish(msg)
            await asyncio.sleep(0.01)

            self.assertEqual(learning_module._handled_message_counts["PerceptData"], 1)
            self.assertEqual(len(self.received_learning_outcomes), 1)
            outcome_payload: LearningOutcomePayload = self.received_learning_outcomes[0].payload
            self.assertEqual(outcome_payload.status, "LEARNED") # Default from current learn() logic
            self.assertEqual(outcome_payload.learned_item_type, "knowledge_concept_features")
            self.assertIn("percept_msg_learn1", outcome_payload.source_message_ids)
            self.assertEqual(self.received_learning_outcomes[0].source_module_id, self.module_id)
        asyncio.run(run_test_logic())

    def test_handle_action_event_success_triggers_learning(self):
        learning_module = ConcreteLearningModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            self.bus.subscribe(self.module_id, "LearningOutcome", self._learning_outcome_listener)
            action_payload = ActionEventPayload(action_command_id="cmd_learn1", action_type="explore", status="SUCCESS", outcome={"found":"gold"})
            msg = GenericMessage("ExecSys", "ActionEvent", action_payload, message_id="action_event_learn_s1")

            self.bus.publish(msg)
            await asyncio.sleep(0.01)

            self.assertEqual(learning_module._handled_message_counts["ActionEvent"], 1)
            self.assertEqual(len(self.received_learning_outcomes), 1)
            outcome_payload: LearningOutcomePayload = self.received_learning_outcomes[0].payload
            self.assertEqual(outcome_payload.status, "LEARNED") # Or UPDATED based on logic
            self.assertEqual(outcome_payload.learned_item_type, "skill_adjustment")
            self.assertEqual(outcome_payload.item_id, "explore")
            self.assertEqual(outcome_payload.metadata.get("reinforcement_direction"), "positive")
        asyncio.run(run_test_logic())

    def test_handle_action_event_failure_triggers_learning(self):
        learning_module = ConcreteLearningModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            self.bus.subscribe(self.module_id, "LearningOutcome", self._learning_outcome_listener)
            action_payload = ActionEventPayload(action_command_id="cmd_learn2", action_type="grasp", status="FAILURE", outcome={"reason":"slipped"})
            msg = GenericMessage("ExecSys", "ActionEvent", action_payload, message_id="action_event_learn_f1")

            self.bus.publish(msg)
            await asyncio.sleep(0.01)

            self.assertEqual(learning_module._handled_message_counts["ActionEvent"], 1)
            self.assertEqual(len(self.received_learning_outcomes), 1)
            outcome_payload: LearningOutcomePayload = self.received_learning_outcomes[0].payload
            self.assertEqual(outcome_payload.status, "UPDATED")
            self.assertEqual(outcome_payload.learned_item_type, "skill_adjustment")
            self.assertEqual(outcome_payload.item_id, "grasp")
            self.assertEqual(outcome_payload.metadata.get("reinforcement_direction"), "negative")
        asyncio.run(run_test_logic())

    def test_handle_goal_update_achieved_triggers_learning(self):
        learning_module = ConcreteLearningModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            self.bus.subscribe(self.module_id, "LearningOutcome", self._learning_outcome_listener)
            goal_payload = GoalUpdatePayload("g_learn_ach", "Learn skill X", 0.9, "achieved", "User")
            msg = GenericMessage("MotSys", "GoalUpdate", goal_payload, message_id="goal_learn_ach1")

            self.bus.publish(msg)
            await asyncio.sleep(0.01)

            self.assertEqual(learning_module._handled_message_counts["GoalUpdate"], 1)
            self.assertEqual(len(self.received_learning_outcomes), 1)
            outcome_payload: LearningOutcomePayload = self.received_learning_outcomes[0].payload
            self.assertEqual(outcome_payload.learned_item_type, "strategy_evaluation")
            self.assertEqual(outcome_payload.status, "LEARNED") # From successful goal
            self.assertEqual(outcome_payload.metadata.get("goal_status"), "achieved")
        asyncio.run(run_test_logic())

    def test_handle_emotional_state_stores_emotion(self): # No direct learning outcome published
        learning_module = ConcreteLearningModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            emo_payload = EmotionalStateChangePayload({"valence": -0.7, "arousal": 0.8}, intensity=0.75)
            msg = GenericMessage("EmoSys", "EmotionalStateChange", emo_payload)

            self.bus.publish(msg)
            await asyncio.sleep(0.01)

            self.assertEqual(learning_module._handled_message_counts["EmotionalStateChange"], 1)
            self.assertIsNotNone(learning_module._last_emotional_state)
            self.assertEqual(learning_module._last_emotional_state.intensity, 0.75)
            self.assertEqual(len(self.received_learning_outcomes), 0) # This handler doesn't call learn() directly
        asyncio.run(run_test_logic())

    # --- Test direct learn() call publishing ---
    def test_direct_learn_call_publishes_outcome(self):
        learning_module = ConcreteLearningModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            self.bus.subscribe(self.module_id, "LearningOutcome", self._learning_outcome_listener)

            context = {"source_message_id": "direct_call_src_id", "task_id":"direct_task_1"}
            learning_module.learn(data="direct learn data", learning_paradigm="direct_store_test", context=context)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_learning_outcomes), 1)
            outcome_payload: LearningOutcomePayload = self.received_learning_outcomes[0].payload
            self.assertEqual(outcome_payload.learning_task_id, "direct_task_1")
            # This paradigm is not in the if/else, so it will hit the "FAILED_TO_LEARN" path
            self.assertEqual(outcome_payload.status, "FAILED_TO_LEARN")
            self.assertIn("direct_call_src_id", outcome_payload.source_message_ids)
            self.assertEqual(self.received_learning_outcomes[0].source_module_id, self.module_id)
            self.assertEqual(learning_module._published_outcomes_count, 1)
        asyncio.run(run_test_logic())

    def test_direct_learn_call_no_bus(self):
        learning_module_no_bus = ConcreteLearningModule(message_bus=None, module_id="NoBusLM")
        initial_outcomes_count = learning_module_no_bus._published_outcomes_count
        try:
            learning_module_no_bus.learn("data", "paradigm", {})
        except Exception as e:
            self.fail(f"learn() method raised an exception with no bus: {e}")

        self.assertEqual(learning_module_no_bus._published_outcomes_count, initial_outcomes_count) # No bus, so no publish
        self.assertEqual(len(self.received_learning_outcomes), 0) # Listener is on self.bus

    # --- Test get_learning_status ---
    def test_get_learning_status(self):
        learning_module = ConcreteLearningModule(message_bus=self.bus, module_id=self.module_id)
        status = learning_module.get_learning_status()
        self.assertEqual(status["module_id"], self.module_id)
        self.assertTrue(status["message_bus_configured"])
        self.assertEqual(status["published_outcomes_count"], 0)
        self.assertEqual(status["handled_message_counts"]["PerceptData"], 0)

        # Simulate some activity
        async def run_activity():
            self.bus.subscribe(self.module_id, "LearningOutcome", self._learning_outcome_listener) # Need listener to consume
            pd_payload = PerceptDataPayload("p_stat", "text", "status data", datetime.now(timezone.utc))
            self.bus.publish(GenericMessage("Src", "PerceptData", pd_payload, message_id="status_pd_msg"))
            await asyncio.sleep(0.01)
        asyncio.run(run_activity())

        status_after = learning_module.get_learning_status()
        self.assertEqual(status_after["published_outcomes_count"], 1)
        self.assertEqual(status_after["handled_message_counts"]["PerceptData"], 1)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

```
