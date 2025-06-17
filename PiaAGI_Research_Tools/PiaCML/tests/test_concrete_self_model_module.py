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
    from PiaAGI_Research_Tools.PiaCML.concrete_self_model_module import (
        ConcreteSelfModelModule, SelfAttributes, EthicalRule, KnowledgeConcept # Import data classes
    )
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from message_bus import MessageBus
    from core_messages import (
        GenericMessage, GoalUpdatePayload, ActionEventPayload,
        EmotionalStateChangePayload, PerceptDataPayload, SelfKnowledgeConfidenceUpdatePayload
    )
    from concrete_self_model_module import ConcreteSelfModelModule, SelfAttributes, EthicalRule, KnowledgeConcept


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

            # Verify autobiography entry content for success
            last_entry_success = self_model.autobiography.entries[-1]
            self.assertIn(action_event.action_command_id, last_entry_success.description) # cmd_test_eval
            self.assertIn(action_event.status, last_entry_success.description) # SUCCESS
            self.assertEqual(last_entry_success.type, "performance_evaluation_success")
            self.assertTrue("Confidence adjusted" in last_entry_success.impact_on_self_model_summary)
            self.assertTrue(f"Confidence changed from {initial_confidence:.2f} to {self_model.attributes.confidence_in_capabilities:.2f}" in last_entry_success.impact_on_self_model_summary)


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

            # Verify autobiography entry content for failure
            last_entry_fail = self_model.autobiography.entries[-1]
            self.assertIn(action_event_fail.action_command_id, last_entry_fail.description)
            self.assertIn(action_event_fail.status, last_entry_fail.description)
            self.assertEqual(last_entry_fail.type, "performance_evaluation_failure")
            self.assertTrue("Confidence adjusted" in last_entry_fail.impact_on_self_model_summary)
            self.assertTrue(f"Confidence changed from {initial_confidence_before_fail:.2f} to {self_model.attributes.confidence_in_capabilities:.2f}" in last_entry_fail.impact_on_self_model_summary)

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


class TestConcreteSelfModelAdvancedLogic(unittest.TestCase):

    def setUp(self):
        # Using message_bus=None for these unit tests focusing on internal logic.
        self.self_model = ConcreteSelfModelModule(message_bus=None, module_id="TestSMAdvanced")
        self.standard_rules = [
            EthicalRule(rule_id="R001_Privacy", principle="User Privacy",
                        description="Must not share user data without explicit consent.", priority_level="critical",
                        applicability_contexts=["user_data_sharing", "pii_access"], implication="impermissible"),
            EthicalRule(rule_id="R002_Minimization", principle="Data Minimization",
                        description="Collect only strictly necessary data.", priority_level="medium",
                        applicability_contexts=["data_collection_design"], implication="requires_caution"),
            EthicalRule(rule_id="R003_Transparency", principle="Transparency",
                        description="Operations should be transparent to users when appropriate.", priority_level="medium", global_rule=True,
                        implication="requires_caution"),
            EthicalRule(rule_id="R004_Beneficence", principle="Beneficence",
                        description="Aim to benefit humanity and users.", priority_level="low",
                        implication="encouraged"),
            EthicalRule(rule_id="R005_NeutralOps", principle="Neutral Operations",
                        description="Standard ops without direct ethical valence.", priority_level="low",
                        implication="neutral"),
            EthicalRule(rule_id="R006_Harm", principle="Non-Maleficence",
                        description="Do not cause harm.", priority_level="critical", global_rule=True,
                        implication="impermissible")
        ]
        self.self_model.ethical_framework.rules = []
        self.self_model.knowledge_map.concepts = {}
        self.self_model._knowledge_confidence = {}
        self.self_model._log = []

    def test_perform_ethical_evaluation_empty_ruleset(self):
        """Test ethical evaluation with no rules defined."""
        self.self_model.ethical_framework.rules = []
        action = {"action_type": "any_action", "description": "A generic action."}
        eval_result = self.self_model.perform_ethical_evaluation(action)
        self.assertEqual(eval_result["outcome"], "PERMISSIBLE")
        self.assertTrue(any("no specific ethical rules were found to be directly applicable" in step for step in eval_result["reasoning"]))

    def test_perform_ethical_evaluation_global_rule_non_maleficence(self):
        """Test application of a global critical rule (Non-Maleficence)."""
        self.self_model.ethical_framework.rules = [
            next(rule for rule in self.standard_rules if rule.rule_id == "R006_Harm")
        ]
        action = {"action_type": "potential_harm_action", "description": "This action description implies Non-Maleficence is relevant and might cause harm."}
        eval_result = self.self_model.perform_ethical_evaluation(action)
        self.assertEqual(eval_result["outcome"], "IMPERMISSIBLE")
        self.assertTrue(any("R006_Harm" in step for step in eval_result["reasoning"]))
        self.assertTrue(any("Decisive rule: R006_Harm" in step for step in eval_result["reasoning"]))
        self.assertIn("R006_Harm", [r["rule_id"] for r in eval_result["detailed_relevant_rules"]])
        # Test specific reasoning steps
        self.assertIn("Starting ethical evaluation for action: potential_harm_action", eval_result["reasoning"][0])
        self.assertIn("Evaluating global rules.", eval_result["reasoning"][1])
        self.assertTrue("Rule R006_Harm (Non-Maleficence) matched based on keyword 'harm' in description" in eval_result["reasoning"][2] or \
                        "Rule R006_Harm (Non-Maleficence) matched based on principle keyword 'Non-Maleficence' in description" in eval_result["reasoning"][2])


    def test_perform_ethical_evaluation_rule_overriding(self):
        """Test that a critical rule overrides an encouraged rule."""
        self.self_model.ethical_framework.rules = [
            next(rule for rule in self.standard_rules if rule.rule_id == "R001_Privacy"),
            next(rule for rule in self.standard_rules if rule.rule_id == "R004_Beneficence")
        ]
        action = {"action_type": "share_beneficial_user_data", "description": "Share User Privacy data for Beneficence."}
        eval_result = self.self_model.perform_ethical_evaluation(action, context={"keywords": ["user_data_sharing"]})
        self.assertEqual(eval_result["outcome"], "IMPERMISSIBLE")
        self.assertTrue(any("R001_Privacy" in step for step in eval_result["reasoning"]))
        self.assertTrue(any("Decisive rule: R001_Privacy" in step for step in eval_result["reasoning"]))

        relevant_rule_ids = [r["rule_id"] for r in eval_result["detailed_relevant_rules"]]
        self.assertIn("R001_Privacy", relevant_rule_ids)
        self.assertIn("R004_Beneficence", relevant_rule_ids)

    def test_perform_ethical_evaluation_cautionary_outcome(self):
        """Test a rule leading to a 'REQUIRES_REVIEW' (cautionary) outcome."""
        self.self_model.ethical_framework.rules = [
            next(rule for rule in self.standard_rules if rule.rule_id == "R003_Transparency")
        ]
        action = {"action_type": "perform_opaque_logging", "description": "Log data without explicit user Transparency."}
        # R003 is global and matches on principle keyword 'Transparency' in description
        eval_result = self.self_model.perform_ethical_evaluation(action)
        self.assertEqual(eval_result["outcome"], "REQUIRES_REVIEW")
        self.assertTrue(any("R003_Transparency" in step for step in eval_result["reasoning"]))
        self.assertTrue(any("Highest priority implication is 'requires_caution'" in step for step in eval_result["reasoning"]))

    def test_perform_ethical_evaluation_original_cases(self):
        """Includes original test cases for broader coverage."""
        self.self_model.ethical_framework.rules = self.standard_rules # Use the full standard set
        self.self_model._log_message(f"Ethical rules for test: {[r.rule_id for r in self.self_model.ethical_framework.rules]}")

        action1 = {"action_type": "generate_public_good_report", "intent": "To promote beneficence by sharing insights.", "description": "Report on beneficence."}
        eval1 = self.self_model.perform_ethical_evaluation(action1)
        self.assertEqual(eval1["outcome"], "PERMISSIBLE")
        self.assertTrue(any("ENCOURAGED by rule(s): R004_Beneficence" in step for step in eval1["reasoning"]))

        action2 = {"action_type": "share_user_emails", "intent": "targeted_marketing_user_privacy", "description": "Share user emails for marketing."}
        eval2 = self.self_model.perform_ethical_evaluation(action2, context={"keywords": ["user_data_sharing"], "context_string": "external_pii_access"})
        self.assertEqual(eval2["outcome"], "IMPERMISSIBLE")
        self.assertTrue(any("Decisive rule: R001_Privacy" in step for step in eval2["reasoning"]))

        action3 = {"action_type": "design_new_data_collection_feature", "intent": "To gather more user interaction data for Data Minimization analysis.", "description": "Designing a feature to log user clicks."}
        eval3 = self.self_model.perform_ethical_evaluation(action3, context={"keywords": ["data_collection_design"]})
        self.assertEqual(eval3["outcome"], "REQUIRES_REVIEW")
        self.assertTrue(any("R002_Minimization" in step for step in eval3["reasoning"]))

        action4 = {"action_type": "optimize_internal_algorithm", "intent": "improve_system_efficiency", "description": "A neutral computation for performance. Will not cause harm."}
        eval4 = self.self_model.perform_ethical_evaluation(action4)
        self.assertEqual(eval4["outcome"], "PERMISSIBLE")
        self.assertTrue(any("aligning with neutral guidelines" in step for step in eval4["reasoning"]) or any("no specific ethical rules were found to be directly applicable or prohibitive" in step for step in eval4["reasoning"]))

        action5 = {"action_type": "obscure_data_source", "intent": "To simplify user interface, hiding complex transparency details.", "description": "This action relates to Transparency."}
        eval5 = self.self_model.perform_ethical_evaluation(action5) # R003 is global
        self.assertEqual(eval5["outcome"], "REQUIRES_REVIEW")
        self.assertTrue(any("R003_Transparency" in step for step in eval5["reasoning"]))

        action6 = {"action_type": "test_potentially_harmful_code", "intent": "stress_test_system_with_non-maleficence_override_attempt", "description": "This test might cause harm."}
        eval6 = self.self_model.perform_ethical_evaluation(action6) # R006 is global
        self.assertEqual(eval6["outcome"], "IMPERMISSIBLE")
        self.assertTrue(any("R006_Harm" in step for step in eval6["reasoning"]))

        action7 = {"action_type": "collect_and_share_user_feedback", "intent": "Improve service (Beneficence) but involves User Privacy.", "description": "Collect feedback for Beneficence, but be mindful of User Privacy."}
        eval7 = self.self_model.perform_ethical_evaluation(action7, context={"keywords": ["user_data_sharing"]})
        self.assertEqual(eval7["outcome"], "IMPERMISSIBLE")
        self.assertTrue(any("R001_Privacy" in step for step in eval7["reasoning"]))
        relevant_rule_ids = [r["rule_id"] for r in eval7["detailed_relevant_rules"]]
        self.assertIn("R001_Privacy", relevant_rule_ids)
        self.assertIn("R004_Beneficence", relevant_rule_ids)

    def test_assess_confidence_in_knowledge_precise_and_clamping(self):
        import time
        current_time = time.time()
        self.self_model.knowledge_map.concepts = {
            "C_test_increase": KnowledgeConcept(concept_id="C_test_increase", label="Frequent & Grounded", confidence_score=0.5, groundedness_score=0.8, access_frequency=20, last_accessed_ts=current_time - (1 * 24 * 60 * 60)),
            "D_test_precise": KnowledgeConcept(concept_id="D_test_precise", label="Concept D", confidence_score=0.5, groundedness_score=0.8, access_frequency=20, last_accessed_ts=current_time - (2 * 24 * 60 * 60)),
            "E_test_precise": KnowledgeConcept(concept_id="E_test_precise", label="Concept E", confidence_score=0.6, groundedness_score=0.1, access_frequency=1, last_accessed_ts=current_time - (70 * 24 * 60 * 60)),
            "F_test_clamp_high": KnowledgeConcept(concept_id="F_test_clamp_high", label="Clamp High", confidence_score=0.9, groundedness_score=0.9, access_frequency=30, last_accessed_ts=current_time),
            "G_test_clamp_low": KnowledgeConcept(concept_id="G_test_clamp_low", label="Clamp Low", confidence_score=0.1, groundedness_score=0.05, access_frequency=0, last_accessed_ts=current_time - (80 * 24 * 60 * 60))
        }

        # Precise adjustments
        # Concept D: Expected: 0.5 (base) + 0.1 (groundedness) + 0.05 (access_frequency) + 0.0 (age_factor for 2 days old) = 0.65
        new_conf_D = self.self_model.assess_confidence_in_knowledge("D_test_precise")
        self.assertAlmostEqual(new_conf_D, 0.65, places=2)
        self.assertEqual(self.self_model.knowledge_map.concepts["D_test_precise"].confidence_score, new_conf_D)

        # Concept E: Expected: 0.6 (base) - 0.1 (groundedness) - 0.02 (access_frequency) - 0.05 (age_factor for 70 days old) = 0.43
        new_conf_E = self.self_model.assess_confidence_in_knowledge("E_test_precise")
        self.assertAlmostEqual(new_conf_E, 0.43, places=2)
        self.assertEqual(self.self_model.knowledge_map.concepts["E_test_precise"].confidence_score, new_conf_E)

        # Clamping
        # Concept F: Expected: 0.9 (base) + 0.1 (groundedness) + 0.05 (access_frequency) + 0.05 (age_factor for recent) = 1.1 -> clamped to 1.0
        new_conf_F = self.self_model.assess_confidence_in_knowledge("F_test_clamp_high")
        self.assertAlmostEqual(new_conf_F, 1.0, places=2)
        self.assertEqual(self.self_model.knowledge_map.concepts["F_test_clamp_high"].confidence_score, 1.0)

        # Concept G: Expected: 0.1 (base) - 0.1 (groundedness) - 0.02 (access_frequency) - 0.05 (age_factor for 80 days old) = -0.07 -> clamped to 0.0
        new_conf_G = self.self_model.assess_confidence_in_knowledge("G_test_clamp_low")
        self.assertAlmostEqual(new_conf_G, 0.0, places=2)
        self.assertEqual(self.self_model.knowledge_map.concepts["G_test_clamp_low"].confidence_score, 0.0)

        # Original tests for coverage
        new_conf_increase = self.self_model.assess_confidence_in_knowledge("C_test_increase")
        self.assertIsNotNone(new_conf_increase)
         # C_test_increase: 0.5 (base) + 0.1 (groundedness) + 0.05 (access_frequency) + 0.05 (age for 1 day old) = 0.7
        self.assertAlmostEqual(new_conf_increase, 0.70, places=2)

        new_conf_non_existent = self.self_model.assess_confidence_in_knowledge("non_existent_concept")
        self.assertIsNone(new_conf_non_existent)
        self.assertTrue(any("Concept 'non_existent_concept' not found" in log_msg for log_msg in self.self_model._log))

    def test_integration_action_event_to_assess_confidence(self):
        # Simulate a successful ActionEvent
        action_type = "perform_complex_calculation"
        derived_concept_id = f"knowledge_about_action_{action_type}"

        action_payload = ActionEventPayload(action_command_id="cmd_calc", action_type=action_type, status="SUCCESS")
        # Directly call the handler (as bus is None)
        self.self_model._handle_action_event_message(GenericMessage(source_module_id="TestExec", message_type="ActionEvent", payload=action_payload))

        self.assertIn(derived_concept_id, self.self_model.knowledge_map.concepts)
        concept = self.self_model.knowledge_map.concepts[derived_concept_id]
        self.assertTrue(concept.confidence_score > 0.5) # Initial 0.5, then boosted by groundedness (0.3 -> +0) and freq (1 -> -0.02). Base 0.5 -> assess (0.5-0.02) = 0.48. Wait, success might imply high groundedness.
                                                        # If success implies high groundedness (e.g. 0.8), then 0.5 (base) + 0.1 (grounded) - 0.02 (freq) = 0.58.
        self.assertIn(derived_concept_id, self.self_model._knowledge_confidence)
        self.assertIn(f"Action success: Assessing confidence for conceptually related knowledge '{derived_concept_id}'", self.self_model._log[-2]) # -2 because assess_confidence logs too


    def test_integration_goal_update_to_ethical_logging(self):
        goal_payload_sensitive = GoalUpdatePayload(
            goal_id="g_sensitive",
            goal_description="Access and process complex sensitive user data for critical decision.",
            priority=0.9, status="ACTIVE", originator="TestPlanner"
        )
        self.self_model._handle_goal_update_message(GenericMessage(source_module_id="TestMot", message_type="GoalUpdate", payload=goal_payload_sensitive))

        self.assertTrue(any("may require ethical evaluation" in log_msg for log_msg in self.self_model._log))
        self.assertTrue(any(f"Goal '{goal_payload_sensitive.goal_id}'" in log_msg for log_msg in self.self_model._log))


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
```
