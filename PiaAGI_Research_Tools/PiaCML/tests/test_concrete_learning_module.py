import unittest
import asyncio
import uuid
import time # For self.learning_module._learned_items_log population
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
        self.learning_module = ConcreteLearningModule(message_bus=self.bus, module_id=self.module_id)

        self.received_learning_outcomes: List[GenericMessage] = []
        self.received_ltm_store_requests: List[GenericMessage] = []

        # Clear logs for each test
        if hasattr(self.learning_module, '_log'):
            self.learning_module._log.clear()

        # Subscribe listeners
        self.bus.subscribe(self.module_id, "LearningOutcome", self._learning_outcome_listener)
        self.bus.subscribe(self.module_id, "LTMStoreRequest", self._ltm_store_request_listener)

    def _learning_outcome_listener(self, message: GenericMessage):
        if isinstance(message.payload, LearningOutcomePayload):
            self.received_learning_outcomes.append(message)

    def _ltm_store_request_listener(self, message: GenericMessage):
        if message.message_type == "LTMStoreRequest" and isinstance(message.payload, dict):
            self.received_ltm_store_requests.append(message)

    def assert_log_contains(self, expected_substring):
        self.assertTrue(any(expected_substring in log_msg for log_msg in self.learning_module._log),
                        f"Log did not contain: '{expected_substring}'. Log content: {self.learning_module._log}")

    def tearDown(self):
        self.received_learning_outcomes.clear()
        self.received_ltm_store_requests.clear() # New

    # --- Test Subscription Handlers and learn() triggering ---
    def test_handle_percept_data_triggers_learning(self):
        # learning_module = ConcreteLearningModule(message_bus=self.bus, module_id=self.module_id) # Use self.learning_module
        async def run_test_logic():
            # self.bus.subscribe(self.module_id, "LearningOutcome", self._learning_outcome_listener) # Moved to setUp

            percept_payload = PerceptDataPayload(percept_id="p_learn1", modality="text", content="new patterns observed", source_timestamp=datetime.now(timezone.utc))
            msg = GenericMessage("PerceptSys", "PerceptData", percept_payload, message_id="percept_msg_learn1")

            self.bus.publish(msg)
            await asyncio.sleep(0.01)

            self.assertEqual(self.learning_module._handled_message_counts["PerceptData"], 1)
            self.assertEqual(len(self.received_learning_outcomes), 1)
            outcome_payload: LearningOutcomePayload = self.received_learning_outcomes[0].payload
            self.assertEqual(outcome_payload.status, "LEARNED")
            self.assertEqual(outcome_payload.learned_item_type, "knowledge_concept_features")
            self.assertIn("percept_msg_learn1", outcome_payload.source_message_ids)
            self.assertEqual(self.received_learning_outcomes[0].source_module_id, self.module_id)
        asyncio.run(run_test_logic())

    def test_handle_action_event_success_triggers_learning(self):
        # learning_module = ConcreteLearningModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            # self.bus.subscribe(self.module_id, "LearningOutcome", self._learning_outcome_listener)
            action_payload = ActionEventPayload(action_command_id="cmd_learn1", action_type="explore", status="SUCCESS", outcome={"found":"gold"})
            msg = GenericMessage("ExecSys", "ActionEvent", action_payload, message_id="action_event_learn_s1")

            self.bus.publish(msg)
            await asyncio.sleep(0.01)

            self.assertEqual(self.learning_module._handled_message_counts["ActionEvent"], 1)
            self.assertEqual(len(self.received_learning_outcomes), 1)
            outcome_payload: LearningOutcomePayload = self.received_learning_outcomes[0].payload
            self.assertEqual(outcome_payload.status, "LEARNED")
            self.assertEqual(outcome_payload.learned_item_type, "skill_adjustment")
            self.assertEqual(outcome_payload.item_id, "explore")
            self.assertEqual(outcome_payload.metadata.get("reinforcement_direction"), "positive")

            # Assert Meta-Learning Hook log
            self.assert_log_contains("Conceptual Meta-Learning Hook: Evaluating effectiveness of paradigm 'reinforcement_from_action'")
        asyncio.run(run_test_logic())

    def test_handle_action_event_failure_triggers_learning(self):
        # learning_module = ConcreteLearningModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            # self.bus.subscribe(self.module_id, "LearningOutcome", self._learning_outcome_listener)
            action_payload = ActionEventPayload(action_command_id="cmd_learn2", action_type="grasp", status="FAILURE", outcome={"reason":"slipped"})
            msg = GenericMessage("ExecSys", "ActionEvent", action_payload, message_id="action_event_learn_f1")

            self.bus.publish(msg)
            await asyncio.sleep(0.01)

            self.assertEqual(self.learning_module._handled_message_counts["ActionEvent"], 1) # Resets for each test
            self.assertEqual(len(self.received_learning_outcomes), 1)
            outcome_payload: LearningOutcomePayload = self.received_learning_outcomes[0].payload
            self.assertEqual(outcome_payload.status, "UPDATED")
            self.assertEqual(outcome_payload.learned_item_type, "skill_adjustment")
            self.assertEqual(outcome_payload.item_id, "grasp")
            self.assertEqual(outcome_payload.metadata.get("reinforcement_direction"), "negative")
        asyncio.run(run_test_logic())

    def test_handle_goal_update_achieved_triggers_learning(self):
        # learning_module = ConcreteLearningModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            # self.bus.subscribe(self.module_id, "LearningOutcome", self._learning_outcome_listener)
            goal_payload = GoalUpdatePayload("g_learn_ach", "Learn skill X", 0.9, "achieved", "User")
            msg = GenericMessage("MotSys", "GoalUpdate", goal_payload, message_id="goal_learn_ach1")

            self.bus.publish(msg)
            await asyncio.sleep(0.01)

            self.assertEqual(self.learning_module._handled_message_counts["GoalUpdate"], 1)
            self.assertEqual(len(self.received_learning_outcomes), 1)
            outcome_payload: LearningOutcomePayload = self.received_learning_outcomes[0].payload
            self.assertEqual(outcome_payload.learned_item_type, "strategy_evaluation")
            self.assertEqual(outcome_payload.status, "LEARNED")
            self.assertEqual(outcome_payload.metadata.get("goal_status"), "achieved")
        asyncio.run(run_test_logic())

    def test_handle_emotional_state_stores_emotion(self):
        # learning_module = ConcreteLearningModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            emo_payload = EmotionalStateChangePayload({"valence": -0.7, "arousal": 0.8}, intensity=0.75)
            msg = GenericMessage("EmoSys", "EmotionalStateChange", emo_payload)

            self.bus.publish(msg)
            await asyncio.sleep(0.01)

            self.assertEqual(self.learning_module._handled_message_counts["EmotionalStateChange"], 1)
            self.assertIsNotNone(self.learning_module._last_emotional_state)
            self.assertEqual(self.learning_module._last_emotional_state.intensity, 0.75)
            self.assertEqual(len(self.received_learning_outcomes), 0)
        asyncio.run(run_test_logic())

    # --- Test direct learn() call publishing ---
    def test_direct_learn_call_publishes_outcome(self):
        # learning_module = ConcreteLearningModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            # self.bus.subscribe(self.module_id, "LearningOutcome", self._learning_outcome_listener)

            context = {"source_message_id": "direct_call_src_id", "task_id":"direct_task_1"}
            # Use self.learning_module for the call
            self.learning_module.learn(data="direct learn data", learning_paradigm="direct_store_test", context=context)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_learning_outcomes), 1)
            outcome_payload: LearningOutcomePayload = self.received_learning_outcomes[0].payload
            self.assertEqual(outcome_payload.learning_task_id, "direct_task_1")
            self.assertEqual(outcome_payload.status, "FAILED_TO_LEARN") # This paradigm is not in the if/else
            self.assertIn("direct_call_src_id", outcome_payload.source_message_ids)
            self.assertEqual(self.received_learning_outcomes[0].source_module_id, self.module_id)
            # _published_outcomes_count is internal to module, check via status or direct access if needed for specific test logic
            # For this test, checking received_learning_outcomes is primary.
        asyncio.run(run_test_logic())

    def test_direct_learn_call_no_bus(self):
        learning_module_no_bus = ConcreteLearningModule(message_bus=None, module_id="NoBusLM")
        initial_outcomes_count = learning_module_no_bus._published_outcomes_count
        try:
            learning_module_no_bus.learn("data", "paradigm", {})
        except Exception as e:
            self.fail(f"learn() method raised an exception with no bus: {e}")

        self.assertEqual(learning_module_no_bus._published_outcomes_count, initial_outcomes_count)
        # self.received_learning_outcomes is tied to self.bus, so this check is not for learning_module_no_bus
        # self.assertEqual(len(self.received_learning_outcomes), 0)

    # --- Test get_learning_status ---
    def test_get_learning_status(self):
        # learning_module = ConcreteLearningModule(message_bus=self.bus, module_id=self.module_id)
        status = self.learning_module.get_learning_status()
        self.assertEqual(status["module_id"], self.module_id)
        self.assertTrue(status["message_bus_configured"])
        initial_published_count = status["published_outcomes_count"]
        initial_percept_handled = status["handled_message_counts"]["PerceptData"]


        # Simulate some activity
        async def run_activity():
            # self.bus.subscribe(self.module_id, "LearningOutcome", self._learning_outcome_listener) # Already in setUp
            pd_payload = PerceptDataPayload("p_stat", "text", "status data", datetime.now(timezone.utc))
            self.bus.publish(GenericMessage("Src", "PerceptData", pd_payload, message_id="status_pd_msg"))
            await asyncio.sleep(0.01)
        asyncio.run(run_activity())

        status_after = self.learning_module.get_learning_status()
        self.assertEqual(status_after["published_outcomes_count"], initial_published_count + 1)
        self.assertEqual(status_after["handled_message_counts"]["PerceptData"], initial_percept_handled + 1)

    # --- Tests for Advanced Logic from Recent Refactoring ---

    async def _run_async_test(self, coro): # Helper for running async code in tests if needed directly
        # This helper might not be necessary if all async interactions are via bus.publish and asyncio.sleep
        await coro

    def test_emotional_modulation_in_learn(self):
        async def run_test_logic():
            # Positive Emotion Influence
            self.learning_module._last_emotional_state = EmotionalStateChangePayload(current_emotion_profile={"valence": 0.8, "arousal": 0.7}, intensity=0.7)
            ae_success_pos_emo = ActionEventPayload(action_command_id="cmd_s_posemo", action_type="skill_pos_emo", status="SUCCESS")
            self.learning_module.learn(data=ae_success_pos_emo, learning_paradigm="reinforcement_from_action", context={"source_message_id":"ae_s_posemo"})
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_learning_outcomes), 1)
            outcome_pos_emo: LearningOutcomePayload = self.received_learning_outcomes[0].payload
            self.assertAlmostEqual(outcome_pos_emo.confidence, 0.75 + 0.05, places=2) # Base 0.75 + 0.05 emotional boost
            self.assertEqual(outcome_pos_emo.metadata.get("emotional_influence"), "positive_amplification")
            self.received_learning_outcomes.clear()

            # Negative Emotion Influence on Success
            self.learning_module._last_emotional_state = EmotionalStateChangePayload(current_emotion_profile={"valence": -0.8, "arousal": 0.7}, intensity=0.7)
            ae_success_neg_emo = ActionEventPayload(action_command_id="cmd_s_negemo", action_type="skill_neg_emo", status="SUCCESS")
            self.learning_module.learn(data=ae_success_neg_emo, learning_paradigm="reinforcement_from_action", context={"source_message_id":"ae_s_negemo"})
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_learning_outcomes), 1)
            outcome_neg_emo: LearningOutcomePayload = self.received_learning_outcomes[0].payload
            self.assertAlmostEqual(outcome_neg_emo.confidence, 0.75 - 0.05, places=2) # Base 0.75 - 0.05 emotional penalty
            self.assertEqual(outcome_neg_emo.metadata.get("emotional_influence"), "negative_amplification")
            self.received_learning_outcomes.clear()

            # Negative Emotion Influence on Failure
            ae_fail_neg_emo = ActionEventPayload(action_command_id="cmd_f_negemo", action_type="skill_fail_neg_emo", status="FAILURE")
            self.learning_module.learn(data=ae_fail_neg_emo, learning_paradigm="reinforcement_from_action", context={"source_message_id":"ae_f_negemo"})
            await asyncio.sleep(0.01)
            self.assertEqual(len(self.received_learning_outcomes), 1)
            outcome_fail_neg_emo: LearningOutcomePayload = self.received_learning_outcomes[0].payload
            self.assertAlmostEqual(outcome_fail_neg_emo.confidence, 0.65 - 0.05, places=2) # Base 0.65 for failure - 0.05 emotional penalty
            self.assertEqual(outcome_fail_neg_emo.metadata.get("emotional_influence"), "negative_amplification")

            self.learning_module._last_emotional_state = None # Reset
        asyncio.run(run_test_logic())

    def test_apply_ethical_guardrails_in_learn(self):
        async def run_test_logic():
            # REJECT Case: Harmful content keyword
            ae_harmful_data = ActionEventPayload(action_command_id="cmd_harm", action_type="generate_harmful_content_tactic", status="SUCCESS")
            self.learning_module.learn(data=ae_harmful_data, learning_paradigm="reinforcement_from_action", context={"source_message_id": "harm_test_msg"})
            await asyncio.sleep(0.01)
            self.assertEqual(len(self.received_learning_outcomes), 1)
            outcome_harmful: LearningOutcomePayload = self.received_learning_outcomes[0].payload
            self.assertEqual(outcome_harmful.status, "REJECTED_BY_ETHICS")
            self.received_learning_outcomes.clear()

            # REJECT Case: Sensitive item type with low confidence
            # Manually trigger learn with data that would result in low confidence before ethics check
            # For this, we'll use a "goal_outcome_evaluation" for a "failed" goal, which results in 0.4 confidence.
            goal_sensitive_low_conf = GoalUpdatePayload("g_sens_low", "Develop social_interaction_model for children", 0.9, "failed", "Test")
            self.learning_module.learn(data=goal_sensitive_low_conf, learning_paradigm="goal_outcome_evaluation", context={"source_message_id": "sens_low_conf_msg"})
            await asyncio.sleep(0.01)
            self.assertEqual(len(self.received_learning_outcomes), 1)
            outcome_sensitive_low: LearningOutcomePayload = self.received_learning_outcomes[0].payload
            self.assertEqual(outcome_sensitive_low.status, "REJECTED_BY_ETHICS") # Confidence 0.4, but type "social_interaction_model" (from item_id)
            self.received_learning_outcomes.clear()


            # PASS Case
            ae_safe = ActionEventPayload(action_command_id="cmd_safe", action_type="learn_helpful_skill", status="SUCCESS")
            self.learning_module.learn(data=ae_safe, learning_paradigm="reinforcement_from_action", context={"source_message_id": "safe_test_msg"})
            await asyncio.sleep(0.01)
            self.assertEqual(len(self.received_learning_outcomes), 1)
            outcome_safe: LearningOutcomePayload = self.received_learning_outcomes[0].payload
            self.assertEqual(outcome_safe.status, "LEARNED")
        asyncio.run(run_test_logic())

    def test_consolidate_knowledge_publishes_ltm_request(self):
        async def run_test_logic():
            # Clear logs specifically for this test logic part to check initial log message
            if hasattr(self.learning_module, '_log'):
                self.learning_module._log.clear()

            # Populate _learned_items_log with some items
            self.learning_module._learned_items_log = [
                {"task_id": "t1", "item_id": "skill_A", "item_type": "skill_adjustment", "status": "LEARNED", "final_confidence": 0.8, "timestamp": time.time()},
                {"task_id": "t2", "item_id": "concept_B", "item_type": "knowledge_concept_features", "status": "LEARNED", "final_confidence": 0.7, "timestamp": time.time()},
                {"task_id": "t3", "item_id": "skill_C", "item_type": "skill_adjustment", "status": "REJECTED_BY_ETHICS", "final_confidence": 0.6, "timestamp": time.time()}
            ]

            ids_to_consolidate = ["skill_A", "concept_B", "skill_C"] # skill_C should be filtered out
            summary_id = self.learning_module.consolidate_knowledge(learned_item_ids=ids_to_consolidate)
            await asyncio.sleep(0.01)

            self.assertIsNotNone(summary_id)
            self.assertEqual(len(self.received_ltm_store_requests), 1)
            ltm_req_payload = self.received_ltm_store_requests[0].payload
            self.assertEqual(ltm_req_payload.get("item_id"), summary_id)
            self.assertEqual(ltm_req_payload.get("item_type"), "learned_item_cluster")
            self.assertIn("skill_A", ltm_req_payload.get("content",{}).get("source_item_ids",[]))
            self.assertIn("concept_B", ltm_req_payload.get("content",{}).get("source_item_ids",[]))
            self.assertNotIn("skill_C", ltm_req_payload.get("content",{}).get("source_item_ids",[])) # Rejected item

            # Assert Lifelong Learning Hook log (should be one of the first)
            self.assert_log_contains("Conceptual Lifelong Learning: Initiating consolidation for 'summary'")
        asyncio.run(run_test_logic())

    def test_no_change_learning_path(self):
        async def run_test_logic():
            ae_inprogress = ActionEventPayload(action_command_id="cmd_ip", action_type="long_running_op", status="IN_PROGRESS")
            self.learning_module.learn(data=ae_inprogress, learning_paradigm="reinforcement_from_action", context={"source_message_id":"ip_msg"})
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_learning_outcomes), 1)
            outcome: LearningOutcomePayload = self.received_learning_outcomes[0].payload
            self.assertEqual(outcome.status, "OBSERVED_NO_CHANGE")
            self.assertAlmostEqual(outcome.confidence, 0.1, places=2)
        asyncio.run(run_test_logic())

    # --- Tests for New Learning Paradigm Placeholders and Logging Hooks ---

    def test_learn_paradigm_supervised(self):
        async def run_test_logic():
            self.learning_module._log.clear()
            context = {"source_message_id": "sl_test_msg", "model_id_to_update": "test_model_01"}
            self.learning_module.learn(
                data=[("input_feature_vector1", "label_A"), ("input_feature_vector2", "label_B")],
                learning_paradigm="supervised_from_labeled_data",
                context=context
            )
            await asyncio.sleep(0.01)
            self.assertEqual(len(self.received_learning_outcomes), 1)
            outcome: LearningOutcomePayload = self.received_learning_outcomes[0].payload
            self.assertEqual(outcome.status, "LEARNED")
            self.assertEqual(outcome.learned_item_type, "model_update_supervised")
            self.assertEqual(outcome.item_id, "test_model_01")
            self.assert_log_contains("Conceptual SL: Expects data as list of (input, label) pairs.")
            self.assert_log_contains("Conceptual SL: Would train/fine-tune an internal model")
            self.assert_log_contains("Conceptual Meta-Learning Hook: Evaluating effectiveness of paradigm 'supervised_from_labeled_data'")
        asyncio.run(run_test_logic())

    def test_learn_paradigm_observational(self):
        async def run_test_logic():
            self.learning_module._log.clear()
            context = {"source_message_id": "ol_test_msg", "demonstrator_id": "expert_agent_007"}
            observed_behavior_trace = [
                {"state": "start_loc", "action": "pickup_tool_X"},
                {"state": "has_tool_X", "action": "use_tool_X_on_object_Y"}
            ]
            self.learning_module.learn(
                data=observed_behavior_trace,
                learning_paradigm="observational_learning",
                context=context
            )
            await asyncio.sleep(0.01)
            self.assertEqual(len(self.received_learning_outcomes), 1)
            outcome: LearningOutcomePayload = self.received_learning_outcomes[0].payload
            self.assertEqual(outcome.status, "LEARNED")
            self.assertEqual(outcome.learned_item_type, "learned_behavior_from_observation")
            self.assertTrue(outcome.item_id.startswith("obs_learn_expert_agent_007"))
            self.assert_log_contains("Conceptual OL: Expects data as observed behavior trace")
            self.assert_log_contains("Conceptual OL: Would attempt to replicate behavior, infer underlying policy/skill")
            self.assert_log_contains("Conceptual Meta-Learning Hook: Evaluating effectiveness of paradigm 'observational_learning'")
        asyncio.run(run_test_logic())

    def test_learn_paradigm_transfer(self):
        async def run_test_logic():
            self.learning_module._log.clear()
            context = {
                "source_message_id": "tl_test_msg",
                "source_domain_knowledge_id": "chess_grandmaster_model",
                "target_domain_task_id": "checkers_novice_game"
            }
            new_problem_context = {"board_state": "checkers_initial_setup", "available_moves": 3}
            self.learning_module.learn(
                data=new_problem_context,
                learning_paradigm="transfer_learning_application",
                context=context
            )
            await asyncio.sleep(0.01)
            self.assertEqual(len(self.received_learning_outcomes), 1)
            outcome: LearningOutcomePayload = self.received_learning_outcomes[0].payload
            self.assertEqual(outcome.status, "LEARNED")
            self.assertEqual(outcome.learned_item_type, "knowledge_transfer_adaptation")
            self.assertEqual(outcome.item_id, "transfer_chess_grandmaster_model_to_checkers_novice_game")
            self.assert_log_contains("Conceptual TL: Expects data as new problem context.")
            self.assert_log_contains("Conceptual TL: Would adapt knowledge/skill from source domain for the target task")
            self.assert_log_contains("Conceptual Meta-Learning Hook: Evaluating effectiveness of paradigm 'transfer_learning_application'")
        asyncio.run(run_test_logic())

    def test_learn_paradigm_meta_learning_adjustment(self): # Renamed to avoid conflict if a "meta_learning" paradigm exists
        async def run_test_logic():
            self.learning_module._log.clear()
            context = {
                "source_message_id": "ml_adjust_test_msg",
                "evaluated_paradigm": "reinforcement_from_action",
                "performance_score": 0.3, # Low performance
                "old_lr_factor": 0.1,
                "new_lr_factor": 0.05 # Adjusting learning rate down
            }
            performance_metrics = {"accuracy_history": [0.5, 0.4, 0.3], "convergence_epochs": 50}
            self.learning_module.learn(
                data=performance_metrics,
                learning_paradigm="meta_learning_strategy_adjustment",
                context=context
            )
            await asyncio.sleep(0.01)
            self.assertEqual(len(self.received_learning_outcomes), 1)
            outcome: LearningOutcomePayload = self.received_learning_outcomes[0].payload
            self.assertEqual(outcome.status, "LEARNED")
            self.assertEqual(outcome.learned_item_type, "learning_strategy_meta_update")
            self.assertEqual(outcome.item_id, "meta_update_for_reinforcement_from_action")
            self.assert_log_contains("Conceptual MetaL: Expects data as performance metrics.")
            self.assert_log_contains("Conceptual MetaL: Would adjust internal learning parameters or strategy selection heuristics")
            # The meta-learning hook itself is part of all learn calls, so not specifically tested for *absence* here,
            # but its presence for this specific paradigm is implicitly part of the flow.
        asyncio.run(run_test_logic())

    def test_process_feedback_conceptual_log(self):
        self.learning_module._log.clear()
        self.learning_module.process_feedback(
            feedback_data={"type": "direct_critique", "critique_content": "The previous plan was inefficient."},
            learning_context_id="ctx_plan_alpha"
        )
        self.assert_log_contains("Conceptual: `process_feedback` received. Would parse feedback type")
        # Also check that it logged the feedback data itself
        self.assert_log_contains("Processing feedback for context 'ctx_plan_alpha': {'type': 'direct_critique'")


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

```
