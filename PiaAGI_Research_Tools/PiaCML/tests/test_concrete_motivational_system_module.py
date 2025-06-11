import unittest
import asyncio
import uuid
import time # For goal creation timestamps if needed, though not asserted directly
from typing import List, Any, Dict

# Adjust path for consistent imports
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    from PiaAGI_Research_Tools.PiaCML.message_bus import MessageBus
    from PiaAGI_Research_Tools.PiaCML.core_messages import GenericMessage, GoalUpdatePayload, ActionEventPayload, EmotionalStateChangePayload
    from PiaAGI_Research_Tools.PiaCML.concrete_motivational_system_module import ConcreteMotivationalSystemModule, Goal, CuriosityTrigger, CompetenceOpportunity
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from message_bus import MessageBus
    from core_messages import GenericMessage, GoalUpdatePayload, ActionEventPayload, EmotionalStateChangePayload
    from concrete_motivational_system_module import ConcreteMotivationalSystemModule, Goal, CuriosityTrigger, CompetenceOpportunity


class TestConcreteMotivationalSystemModuleIntegration(unittest.TestCase):

    def setUp(self):
        self.bus = MessageBus()
        self.module_id = f"TestMotSysModule_{str(uuid.uuid4())[:8]}"
        self.mot_sys = ConcreteMotivationalSystemModule(message_bus=self.bus, module_id=self.module_id) # Instantiated here
        self.received_goal_updates: List[GenericMessage] = []
        # Subscribe listener in setUp
        self.bus.subscribe(self.module_id, "GoalUpdate", self._goal_update_listener)


    def _goal_update_listener(self, message: GenericMessage):
        if isinstance(message.payload, GoalUpdatePayload):
            self.received_goal_updates.append(message)

    def tearDown(self):
        self.received_goal_updates.clear()
        if hasattr(self, 'mot_sys') and hasattr(self.mot_sys, '_log'): # Clear logs for next test
            self.mot_sys._log.clear()


    # --- Test Publishing GoalUpdate Messages ---
    def test_add_goal_publishes_goal_update(self):
        # mot_sys = ConcreteMotivationalSystemModule(message_bus=self.bus, module_id=self.module_id) # Use self.mot_sys
        mot_sys = self.mot_sys
        async def run_test_logic():
            # self.bus.subscribe(self.module_id, "GoalUpdate", self._goal_update_listener) # Moved to setUp

            desc = "Test Publish Add"
            g_type = "EXTRINSIC_TEST_ADD"
            prio = 0.85
            source_details = {"originator": "test_suite", "trigger_event": "manual_add"}

            goal_id = mot_sys.add_goal(
                description=desc, goal_type=g_type, initial_priority=prio,
                source_trigger=source_details, initial_status="PENDING"
            )
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_goal_updates), 1)
            msg = self.received_goal_updates[0]
            self.assertEqual(msg.source_module_id, self.module_id)
            self.assertEqual(msg.message_type, "GoalUpdate")

            payload: GoalUpdatePayload = msg.payload
            self.assertEqual(payload.goal_id, goal_id)
            self.assertEqual(payload.goal_description, desc)
            self.assertEqual(payload.priority, prio)
            self.assertEqual(payload.status, "PENDING")
            self.assertEqual(payload.originator, source_details["originator"]) # Checks refined originator logic
        asyncio.run(run_test_logic())

    def test_update_goal_status_publishes_goal_update(self):
        # mot_sys = ConcreteMotivationalSystemModule(message_bus=self.bus, module_id=self.module_id) # Use self.mot_sys
        mot_sys = self.mot_sys
        async def run_test_logic():
            # self.bus.subscribe(self.module_id, "GoalUpdate", self._goal_update_listener) # Moved to setUp
            goal_id = mot_sys.add_goal("Status Test Goal", "TYPE_STATUS", 0.5)
            self.received_goal_updates.clear() # Clear message from add_goal

            mot_sys.update_goal_status(goal_id, "ACTIVE")
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_goal_updates), 1)
            payload: GoalUpdatePayload = self.received_goal_updates[0].payload
            self.assertEqual(payload.goal_id, goal_id)
            self.assertEqual(payload.status, "ACTIVE")
            self.assertEqual(self.received_goal_updates[0].source_module_id, self.module_id)
        asyncio.run(run_test_logic())

    def test_update_goal_priority_publishes_goal_update(self):
        # mot_sys = ConcreteMotivationalSystemModule(message_bus=self.bus, module_id=self.module_id) # Use self.mot_sys
        mot_sys = self.mot_sys
        async def run_test_logic():
            # self.bus.subscribe(self.module_id, "GoalUpdate", self._goal_update_listener) # Moved to setUp
            goal_id = mot_sys.add_goal("Priority Test Goal", "TYPE_PRIO", 0.6)
            self.received_goal_updates.clear()

            mot_sys.update_goal_priority(goal_id, 0.92)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_goal_updates), 1)
            payload: GoalUpdatePayload = self.received_goal_updates[0].payload
            self.assertEqual(payload.goal_id, goal_id)
            self.assertEqual(payload.priority, 0.92)
        asyncio.run(run_test_logic())

    def test_methods_run_without_bus(self):
        mot_sys_no_bus = ConcreteMotivationalSystemModule(message_bus=None, module_id="NoBusMotSys")
        try:
            goal_id = mot_sys_no_bus.add_goal("No Bus Add", "NOBUS_TYPE", 0.1)
            mot_sys_no_bus.update_goal_status(goal_id, "ACTIVE")
            mot_sys_no_bus.update_goal_priority(goal_id, 0.2)
        except Exception as e:
            self.fail(f"Motivational system methods raised an exception with no bus: {e}")
        # self.received_goal_updates is tied to self.bus, so this check is not for mot_sys_no_bus
        # self.assertEqual(len(self.received_goal_updates), 0)

    # --- Test Subscribing to ActionEvent Messages ---
    def test_handle_action_event_achieved_updates_goal(self):
        # mot_sys = ConcreteMotivationalSystemModule(message_bus=self.bus, module_id=self.module_id) # Use self.mot_sys
        mot_sys = self.mot_sys
        async def run_test_logic():
            # self.bus.subscribe(self.module_id, "GoalUpdate", self._goal_update_listener) # Moved to setUp
            goal_id = mot_sys.add_goal("Action Test Goal Achieved", "ACTION_TEST", 0.7, initial_status="ACTIVE")
            self.received_goal_updates.clear() # Clear after add_goal

            action_event_payload = ActionEventPayload(
                action_command_id="cmd_test_achieved",
                action_type="TEST_ACTION",
                status="SUCCESS", # This should map to ACHIEVED for the goal
                outcome={"goal_id": goal_id, "details": "Action was very successful"}
            )
            action_event_msg = GenericMessage(
                source_module_id="TestExecutor", message_type="ActionEvent", payload=action_event_payload
            )
            self.bus.publish(action_event_msg)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_goal_updates), 1, "GoalUpdate not received after SUCCESS ActionEvent")
            payload: GoalUpdatePayload = self.received_goal_updates[0].payload
            self.assertEqual(payload.goal_id, goal_id)
            self.assertEqual(payload.status, "ACHIEVED")

            # Verify internal state too
            internal_goal = mot_sys.get_goal(goal_id)
            self.assertIsNotNone(internal_goal)
            self.assertEqual(internal_goal.status, "ACHIEVED")
        asyncio.run(run_test_logic())

    def test_handle_action_event_failed_updates_goal(self):
        # mot_sys = ConcreteMotivationalSystemModule(message_bus=self.bus, module_id=self.module_id) # Use self.mot_sys
        mot_sys = self.mot_sys
        async def run_test_logic():
            # self.bus.subscribe(self.module_id, "GoalUpdate", self._goal_update_listener) # Moved to setUp
            goal_id = mot_sys.add_goal("Action Test Goal Failed", "ACTION_TEST_FAIL", 0.7, initial_status="ACTIVE")
            self.received_goal_updates.clear()

            action_event_payload = ActionEventPayload(
                action_command_id="cmd_test_failed",
                action_type="TEST_ACTION_FAIL",
                status="FAILURE", # This should map to FAILED for the goal
                outcome={"goal_id": goal_id, "reason": "Resource depletion"}
            )
            action_event_msg = GenericMessage(
                source_module_id="TestExecutor", message_type="ActionEvent", payload=action_event_payload
            )
            self.bus.publish(action_event_msg)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_goal_updates), 1, "GoalUpdate not received after FAILURE ActionEvent")
            payload: GoalUpdatePayload = self.received_goal_updates[0].payload
            self.assertEqual(payload.goal_id, goal_id)
            self.assertEqual(payload.status, "FAILED")
            internal_goal = mot_sys.get_goal(goal_id)
            self.assertEqual(internal_goal.status, "FAILED")
        asyncio.run(run_test_logic())

    def test_handle_action_event_goal_id_in_outcome_new_status(self):
        # mot_sys = ConcreteMotivationalSystemModule(message_bus=self.bus, module_id=self.module_id) # Use self.mot_sys
        mot_sys = self.mot_sys
        async def run_test_logic():
            # self.bus.subscribe(self.module_id, "GoalUpdate", self._goal_update_listener) # Moved to setUp
            goal_id = mot_sys.add_goal("Action Test Goal Custom Status", "ACTION_TEST_CUSTOM", 0.7, initial_status="ACTIVE")
            self.received_goal_updates.clear()

            custom_status = "SUSPENDED_BY_ACTION"
            action_event_payload = ActionEventPayload(
                action_command_id="cmd_test_custom",
                action_type="TEST_ACTION_CUSTOM",
                status="SUCCESS", # Main action status could be success
                outcome={"goal_id": goal_id, "new_status": custom_status, "details": "Action led to suspension requirement"}
            )
            action_event_msg = GenericMessage(
                source_module_id="TestExecutor", message_type="ActionEvent", payload=action_event_payload
            )
            self.bus.publish(action_event_msg)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_goal_updates), 1, "GoalUpdate not received after ActionEvent with new_status in outcome")
            payload: GoalUpdatePayload = self.received_goal_updates[0].payload
            self.assertEqual(payload.goal_id, goal_id)
            self.assertEqual(payload.status, custom_status)
            internal_goal = mot_sys.get_goal(goal_id)
            self.assertEqual(internal_goal.status, custom_status)
        asyncio.run(run_test_logic())

    def test_get_module_status(self):
        # mot_sys = ConcreteMotivationalSystemModule(message_bus=self.bus, module_id=self.module_id) # Use self.mot_sys
        mot_sys = self.mot_sys
        mot_sys.add_goal("Goal 1 for status", "T1", 0.5) # This will publish a GoalUpdate
        self.received_goal_updates.clear() # Clear it for this specific test's purpose if needed, or ignore

        status = mot_sys.get_module_status()
        self.assertEqual(status["module_id"], self.module_id)
        self.assertTrue(status["message_bus_configured"])
        self.assertEqual(status["total_goals"], 1)
        self.assertEqual(status["goals_by_status"].get("PENDING"), 1)
        self.assertTrue(status["log_entries"] > 0) # Check that logging is happening

    # --- New Tests for Curiosity Logic ---
    def test_assess_curiosity_triggers_novel_stimulus(self):
        mot_sys = self.mot_sys
        world_event = {"type": "NOVEL_STIMULUS", "id": "stimulus_alpha", "novelty_score": 0.9, "complexity_score": 0.7}

        initial_goal_count = len(mot_sys.goals)
        self.received_goal_updates.clear()

        new_goal_ids = mot_sys.assess_curiosity_triggers(world_event=world_event)
        self.assertEqual(len(new_goal_ids), 1)
        self.assertEqual(len(mot_sys.goals), initial_goal_count + 1)

        new_goal = mot_sys.get_goal(new_goal_ids[0])
        self.assertIsNotNone(new_goal)
        self.assertEqual(new_goal.type, "INTRINSIC_CURIOSITY")
        self.assertTrue(new_goal.priority > 7.0) # Expected intensity > 0.7 for these scores (0.4532 * 10 = 4.532. Correcting this assertion)
        self.assertAlmostEqual(new_goal.priority, 4.532, places=3) # (0.4*0.9 + 0.2*0.7) * 1.03 * 10 = (0.36+0.14)*1.03*10 = 0.5*1.03*10 = 5.15. Previous calc was (0.4*0.8 + 0.2*0.6)*1.03*10 = 0.4532*10 = 4.532
        # Recalculating based on _calculate_curiosity_intensity:
        # Novelty 0.9, Complexity 0.7 -> base = (0.4*0.9) + (0.2*0.7) = 0.36 + 0.14 = 0.50
        # final_intensity = 0.50 * (1 + 0.3 * 0.1) = 0.50 * 1.03 = 0.515. Priority = 5.15
        self.assertAlmostEqual(new_goal.priority, 5.15, places=2)

        self.assertIn("Investigate novel stimulus: stimulus_alpha", new_goal.description)
        self.assertIn("Novelty: 0.90", new_goal.description)
        self.assertIn("Complexity: 0.70", new_goal.description)
        self.assertIn(f"Calculated Intensity: {new_goal.source_trigger['calculated_intensity']:.2f}", new_goal.description)

        self.assertEqual(new_goal.source_trigger["trigger_type"], "NOVEL_STIMULUS")
        self.assertEqual(new_goal.source_trigger["stimulus_id"], "stimulus_alpha")
        self.assertEqual(new_goal.source_trigger["novelty_score"], 0.9)
        self.assertEqual(new_goal.source_trigger["complexity_score"], 0.7)
        self.assertIn("calculated_intensity", new_goal.source_trigger) # Check presence
        self.assertAlmostEqual(new_goal.source_trigger["calculated_intensity"], 0.515, places=3)

        self.assertTrue(any("Novel stimulus 'stimulus_alpha' assessed for curiosity." in log for log in mot_sys._log))
        self.assertEqual(len(self.received_goal_updates), 1) # Check if add_goal published it

    def test_assess_curiosity_triggers_knowledge_gap(self):
        mot_sys = self.mot_sys
        knowledge_snapshot = {"concept_X": {"confidence": 0.2, "understanding_level": 0.1, "last_explored_ts": time.time() - 1000}}

        initial_goal_count = len(mot_sys.goals)
        self.received_goal_updates.clear()

        new_goal_ids = mot_sys.assess_curiosity_triggers(knowledge_map_snapshot=knowledge_snapshot)
        self.assertEqual(len(new_goal_ids), 1)

        new_goal = mot_sys.get_goal(new_goal_ids[0])
        self.assertIsNotNone(new_goal)
        self.assertEqual(new_goal.type, "INTRINSIC_CURIOSITY")
        # Intensity for (1-0.2)*0.6 = 0.48. Relevance factor: 1.03. Total: 0.48 * 1.03 = 0.4944. Priority = 4.944
        self.assertAlmostEqual(new_goal.priority, 4.944, places=3)
        self.assertIn("Explore knowledge gap for concept: concept_X", new_goal.description)
        self.assertIn("Current Confidence: 0.20", new_goal.description)
        self.assertIn(f"Calculated Intensity: {new_goal.source_trigger['calculated_intensity']:.2f}", new_goal.description)

        self.assertEqual(new_goal.source_trigger["trigger_type"], "KNOWLEDGE_GAP")
        self.assertEqual(new_goal.source_trigger["concept_id"], "concept_X")
        self.assertEqual(new_goal.source_trigger["current_confidence"], 0.2)
        self.assertEqual(new_goal.source_trigger["current_understanding"], 0.1) # From mock data
        self.assertIn("calculated_intensity", new_goal.source_trigger)
        self.assertAlmostEqual(new_goal.source_trigger["calculated_intensity"], 0.4944, places=4)
        self.assertTrue(any("Knowledge gap for concept 'concept_X' assessed for curiosity." in log for log in mot_sys._log))

    def test_assess_curiosity_low_intensity_no_goal(self):
        mot_sys = self.mot_sys
        world_event = {"type": "NOVEL_STIMULUS", "id": "stimulus_beta", "novelty_score": 0.1, "complexity_score": 0.1} # Low scores

        initial_goal_count = len(mot_sys.goals)
        new_goal_ids = mot_sys.assess_curiosity_triggers(world_event=world_event)
        self.assertEqual(len(new_goal_ids), 0)
        self.assertEqual(len(mot_sys.goals), initial_goal_count)
        self.assertTrue(any("Calculated intensity: 0.07" in log for log in mot_sys._log)) # (0.4*0.1 + 0.2*0.1) * (1+0.03) = 0.06 * 1.03 = 0.0618

    def test_generate_curiosity_satisfaction_reward(self):
        mot_sys = self.mot_sys
        curiosity_goal = Goal(id="cur_g1", description="Explore X", type="INTRINSIC_CURIOSITY", priority=5.0, status="ACHIEVED")

        # Test uncertainty reduction
        info_gain1 = {"type": "uncertainty_reduced", "concept_id": "concept_A", "old_confidence": 0.3, "new_confidence": 0.9}
        reward1 = mot_sys._generate_curiosity_satisfaction_reward(curiosity_goal, info_gain1)
        self.assertIsNotNone(reward1)
        self.assertEqual(reward1["type"], "INTRINSIC_CURIOSITY_SATISFACTION")
        self.assertAlmostEqual(reward1["magnitude"], 0.6) # (0.9 - 0.3) * 1.0
        self.assertEqual(reward1["goal_id"], "cur_g1")
        self.assertTrue(any("Conceptual intrinsic reward for curiosity generated: Magnitude 0.60" in log for log in mot_sys._log))

        # Test novelty integration
        info_gain2 = {"type": "novelty_integrated", "item_id": "item_B", "integration_level": 0.7}
        reward2 = mot_sys._generate_curiosity_satisfaction_reward(curiosity_goal, info_gain2)
        self.assertIsNotNone(reward2)
        self.assertAlmostEqual(reward2["magnitude"], 0.56) # 0.7 * 0.8

        # Test non-curiosity goal
        extrinsic_goal = Goal(id="ext_g1", description="Do task Y", type="EXTRINSIC_TASK", priority=8.0, status="ACHIEVED")
        reward3 = mot_sys._generate_curiosity_satisfaction_reward(extrinsic_goal, info_gain1)
        self.assertIsNone(reward3)
        self.assertTrue(any("Attempted to generate curiosity reward for non-curiosity goal: ext_g1" in log for log in mot_sys._log))

    # --- New Tests for Competence Logic ---

    def test_assess_competence_opportunities(self):
        mot_sys = self.mot_sys
        capability_snapshot = {
            "skill_nav_basic": {"proficiency_level": 0.3, "importance_for_goals": 0.8},
            "skill_comm_adv": {"proficiency_level": 0.9, "importance_for_goals": 0.7}, # Already proficient
            "skill_craft_simple": {"proficiency_level": 0.2, "importance_for_goals": 0.2} # Low importance, low intensity
        }

        initial_goal_count = len(mot_sys.goals)
        self.received_goal_updates.clear()

        new_goal_ids = mot_sys.assess_competence_opportunities(capability_inventory_snapshot=capability_snapshot, active_goals=[]) # No active goals for relevance calc simplicity

        # Expect 1 new goal for skill_nav_basic (0.6*(1-0.3) + 0.4*0.8 = 0.42 + 0.32 = 0.74 intensity > 0.35)
        # skill_comm_adv: proficiency 0.9 -> gap 0.1. intensity = 0.6*0.1 + 0.4*0.7 = 0.06 + 0.28 = 0.34 (below threshold)
        # skill_craft_simple: 0.6*(1-0.2) + 0.4*0.2 = 0.48 + 0.08 = 0.56 intensity. (Above threshold) --> Expect 2 goals

        # Re-evaluating skill_comm_adv: gap=0.1, importance=0.7 -> (0.6*0.1) + (0.4*0.7) = 0.06 + 0.28 = 0.34. Below threshold 0.35. Correct.
        # Re-evaluating skill_craft_simple: gap=0.8, importance=0.2 -> (0.6*0.8) + (0.4*0.2) = 0.48 + 0.08 = 0.56. Above threshold. Correct.
        self.assertEqual(len(new_goal_ids), 2, f"Expected 2 competence goals, got {len(new_goal_ids)}")

        found_nav_goal = False
        for goal_id in new_goal_ids:
            goal = mot_sys.get_goal(goal_id)
            self.assertIsNotNone(goal)
            self.assertEqual(goal.type, "INTRINSIC_COMPETENCE")
            if goal.target_skill_id == "skill_nav_basic":
                found_nav_goal = True
                # Intensity for skill_nav_basic: (0.6 * (1.0-0.3)) + (0.4 * 0.8) = (0.6*0.7) + 0.32 = 0.42 + 0.32 = 0.74. Priority = 7.4
                self.assertAlmostEqual(goal.priority, 7.4, places=1)
                self.assertIn("Improve skill: skill_nav_basic", goal.description)
                self.assertIn(f"(Current Prof: {goal.competence_details['current_proficiency']:.2f}, Target: {goal.competence_details['target_proficiency']:.2f}, Calculated Intensity: {goal.source_trigger['calculated_intensity']:.2f})", goal.description)

                # Assert source_trigger details
                self.assertEqual(goal.source_trigger["trigger_type"], "LOW_PROFICIENCY_OR_MASTERY_OPPORTUNITY")
                self.assertEqual(goal.source_trigger["skill_id"], "skill_nav_basic")
                self.assertEqual(goal.source_trigger["assessed_proficiency_at_trigger"], 0.3)
                self.assertEqual(goal.source_trigger["assessed_importance_at_trigger"], 0.8)
                self.assertAlmostEqual(goal.source_trigger["calculated_intensity"], 0.74, places=2)

                # Assert competence_details
                self.assertEqual(goal.competence_details["current_proficiency"], 0.3)
                self.assertEqual(goal.competence_details["target_proficiency"], 1.0) # Default target
                self.assertEqual(goal.competence_details["initial_importance_rating"], 0.8)

        self.assertTrue(found_nav_goal, "Competence goal for skill_nav_basic not found or details incorrect.")
        self.assertEqual(len(self.received_goal_updates), 2)

    def test_competence_goal_trigger_from_action_event_failure(self):
        mot_sys = self.mot_sys
        action_type_failed = "skill_complex_manipulation"
        action_event_payload = ActionEventPayload(
            action_command_id="cmd_fail_comp", action_type=action_type_failed, status="FAILURE",
            outcome={"reason": "gripper_accuracy_low", "task_importance": 0.7} # task_importance is conceptual
        )
        msg = GenericMessage("Executor", "ActionEvent", action_event_payload, message_id="action_fail_comp_msg")

        initial_goal_count = len(mot_sys.goals)
        self.received_goal_updates.clear()
        log_len_before = len(mot_sys._log)

        mot_sys._handle_action_event(msg) # Call directly as it's a handler

        # Proficiency 0.3 (assumed), importance 0.7 (from outcome)
        # Intensity = 0.6*(1-0.3) + 0.4*0.7 = 0.42 + 0.28 = 0.70. Priority = 7.0
        self.assertEqual(len(mot_sys.goals), initial_goal_count + 1)
        new_goal = mot_sys.goals[-1] # Assuming it's the last one added
        self.assertEqual(new_goal.type, "INTRINSIC_COMPETENCE")
        self.assertEqual(new_goal.target_skill_id, action_type_failed)
        self.assertAlmostEqual(new_goal.priority, 7.0, places=1)
        self.assertEqual(new_goal.source_trigger["trigger_type"], "TASK_PERFORMANCE_FEEDBACK")
        self.assertEqual(new_goal.source_trigger["action_type"], action_type_failed)
        self.assertEqual(new_goal.source_trigger["status"], "FAILURE")
        self.assertEqual(new_goal.competence_details["current_proficiency_assumed"], 0.3)
        self.assertEqual(len(self.received_goal_updates), 1) # GoalUpdate for the new competence goal

    def test_generate_competence_satisfaction_reward(self):
        mot_sys = self.mot_sys
        competence_goal = Goal(
            id="comp_g1", description="Improve skill_assembly", type="INTRINSIC_COMPETENCE",
            priority=6.0, status="ACHIEVED", target_skill_id="skill_assembly",
            competence_details={"current_proficiency": 0.4, "target_proficiency": 0.7}
        )

        # Test proficiency increase
        gain_details1 = {"type": "skill_proficiency_increased", "skill_id": "skill_assembly", "old_proficiency": 0.4, "new_proficiency": 0.7, "task_difficulty": 0.6}
        reward1 = mot_sys._generate_competence_satisfaction_reward(competence_goal, gain_details1)
        self.assertIsNotNone(reward1)
        self.assertEqual(reward1["type"], "INTRINSIC_COMPETENCE_SATISFACTION")
        # (0.7-0.4) * (1 + 0.6*0.5) = 0.3 * 1.3 = 0.39
        self.assertAlmostEqual(reward1["magnitude"], 0.39)
        self.assertEqual(reward1["goal_id"], "comp_g1")
        self.assertEqual(reward1["skill_id"], "skill_assembly")
        self.assertTrue(any("Conceptual intrinsic reward for competence generated: Magnitude 0.39" in log for log in mot_sys._log))

    def test_competence_reward_triggered_by_action_event_achieving_goal(self):
        mot_sys = self.mot_sys
        skill_to_improve = "precise_welding"
        # Add a competence goal for this skill
        competence_goal_id = mot_sys.add_goal(
            description=f"Master {skill_to_improve}",
            goal_type="INTRINSIC_COMPETENCE",
            initial_priority=7.0,
            target_skill_id=skill_to_improve,
            competence_details={"current_proficiency": 0.5, "target_proficiency": 0.9},
            initial_status="ACTIVE"
        )
        self.received_goal_updates.clear() # Clear GoalUpdate from add_goal
        log_len_before_event = len(mot_sys._log)

        # Simulate an ActionEvent that achieves this competence goal
        action_event_payload = ActionEventPayload(
            action_command_id="cmd_weld_success", action_type="perform_welding_task", status="SUCCESS",
            outcome={
                "goal_id": competence_goal_id,
                "new_status": "ACHIEVED", # Explicitly achieve the competence goal
                "skill_used": skill_to_improve,
                "competence_gain_details": { # Details for reward calculation
                    "type": "skill_proficiency_increased",
                    "skill_id": skill_to_improve,
                    "old_proficiency": 0.5,
                    "new_proficiency": 0.9,
                    "task_difficulty": 0.7
                }
            }
        )
        msg = GenericMessage("Executor", "ActionEvent", action_event_payload)
        mot_sys._handle_action_event(msg) # Directly call handler

        # Check that GoalUpdate for ACHIEVED was published
        self.assertEqual(len(self.received_goal_updates), 1)
        self.assertEqual(self.received_goal_updates[0].payload.status, "ACHIEVED")

        # Check that competence satisfaction reward was logged
        # Magnitude: (0.9-0.5) * (1 + 0.7*0.5) = 0.4 * 1.35 = 0.54
        self.assertTrue(any("Conceptual intrinsic reward for competence generated: Magnitude 0.54" in log for log in mot_sys._log[log_len_before_event:]), "Competence reward log not found.")

    def test_evaluate_and_generate_intrinsic_goals_dynamically(self):
        mot_sys = self.mot_sys
        mot_sys.goals.clear()
        self.received_goal_updates.clear()
        mot_sys._log.clear()

        # Mock world model methods used by assess_curiosity_triggers and assess_competence_opportunities
        # These are now part of the ConcreteMotivationalSystemModule itself.

        # Scenario 1: Curiosity trigger, no competence
        mot_sys._get_curiosity_triggers_from_world_state = unittest.mock.MagicMock(return_value=[
            CuriosityTrigger(trigger_id="ct1", description="Mysterious new object X", related_entity_id="entity_X", novelty_score=0.8, uncertainty_score=0.7, associated_goal_id=None)
        ])
        mot_sys._get_competence_opportunities_from_world_state = unittest.mock.MagicMock(return_value=[])

        summary = mot_sys.evaluate_and_generate_intrinsic_goals_dynamically()
        self.assertEqual(len(mot_sys.goals), 1)
        self.assertIn("ct1_curiosity_goal", list(mot_sys.goals.keys())[0]) # Check goal ID pattern
        self.assertIn("Generated 1 curiosity goals", summary)
        self.assertIn("Generated 0 competence goals", summary)
        self.assertTrue(any("Curiosity goal generated for trigger ct1" in log for log in mot_sys._log))
        self.assertEqual(len(self.received_goal_updates), 1)

        # Scenario 2: Competence opportunity, no curiosity
        mot_sys.goals.clear()
        self.received_goal_updates.clear()
        mot_sys._log.clear()
        mot_sys._get_curiosity_triggers_from_world_state.return_value = []
        mot_sys._get_competence_opportunities_from_world_state.return_value = [
            CompetenceOpportunity(opportunity_id="co1", description="Opportunity to learn skill Y", related_skill_id="skill_Y", potential_mastery_gain=0.75, current_mastery=0.3, associated_goal_id=None)
        ]

        summary = mot_sys.evaluate_and_generate_intrinsic_goals_dynamically()
        self.assertEqual(len(mot_sys.goals), 1)
        self.assertIn("co1_competence_goal", list(mot_sys.goals.keys())[0]) # Check goal ID pattern
        self.assertIn("Generated 0 curiosity goals", summary)
        self.assertIn("Generated 1 competence goals", summary)
        self.assertTrue(any("Competence goal generated for opportunity co1" in log for log in mot_sys._log))
        self.assertEqual(len(self.received_goal_updates), 1)

        # Scenario 3: Both present
        mot_sys.goals.clear()
        self.received_goal_updates.clear()
        mot_sys._log.clear()
        mot_sys._get_curiosity_triggers_from_world_state.return_value = [
            CuriosityTrigger(trigger_id="ct2", description="Another mystery", related_entity_id="entity_Y", novelty_score=0.7, uncertainty_score=0.6, associated_goal_id=None)
        ]
        mot_sys._get_competence_opportunities_from_world_state.return_value = [
            CompetenceOpportunity(opportunity_id="co2", description="Another skill", related_skill_id="skill_Z", potential_mastery_gain=0.8, current_mastery=0.2, associated_goal_id=None)
        ]
        summary = mot_sys.evaluate_and_generate_intrinsic_goals_dynamically()
        self.assertEqual(len(mot_sys.goals), 2)
        self.assertIn("Generated 1 curiosity goals", summary)
        self.assertIn("Generated 1 competence goals", summary)
        self.assertEqual(len(self.received_goal_updates), 2)


        # Scenario 4: None present
        mot_sys.goals.clear()
        self.received_goal_updates.clear()
        mot_sys._log.clear()
        mot_sys._get_curiosity_triggers_from_world_state.return_value = []
        mot_sys._get_competence_opportunities_from_world_state.return_value = []
        summary = mot_sys.evaluate_and_generate_intrinsic_goals_dynamically()
        self.assertEqual(len(mot_sys.goals), 0)
        self.assertIn("No new curiosity goals generated", summary)
        self.assertIn("No new competence goals generated", summary)
        self.assertEqual(len(self.received_goal_updates), 0)


    # --- Tests for Dynamic Goal Prioritization ---

    def test_get_active_goals_sorts_by_dynamic_priority(self):
        mot_sys = self.mot_sys
        # Clear any existing goals to ensure a clean slate for this specific test
        mot_sys.goals.clear()
        self.received_goal_updates.clear()

        # Goal 1: Extrinsic, high base priority (e.g., 8.0 -> intensity 0.8)
        # Dynamic Prio (approx): 0.2*0.5 (base_type) + 0.3*0.8 (intensity from prio) + 0.15*0 (urg) + 0.15*1 (val) + 0.1*0 (dep) - 0.1*0.1 (cost)
        # = 0.10 + 0.24 + 0 + 0.15 + 0 - 0.01 = 0.48. Scaled: 4.8
        g1_id = mot_sys.add_goal("Extrinsic Task High Base", "EXTRINSIC_TASK", initial_priority=8.0, source_trigger={"originator": "system"})

        # Goal 2: Curiosity, moderate base priority (e.g., 5.0), but high calculated_intensity (e.g., 0.9)
        # Dynamic Prio (approx): 0.2*0.3 (base_type) + 0.3*0.9 (intensity_intrinsic) + ... (others same as above)
        # = 0.06 + 0.27 + 0 + 0.15 + 0 - 0.01 = 0.47. Scaled: 4.7
        # Let's make intensity higher to outrank g1
        # Intensity 0.95: 0.06 + 0.3*0.95 + 0.15 - 0.01 = 0.06 + 0.285 + 0.15 - 0.01 = 0.485. Scaled: 4.85
        g2_id = mot_sys.add_goal("Curiosity High Intensity", "INTRINSIC_CURIOSITY", initial_priority=5.0, source_trigger={"calculated_intensity": 0.95, "trigger_type": "NOVEL_STIMULUS"})

        # Goal 3: Competence, low base priority (e.g., 3.0), moderate calculated_intensity (e.g., 0.6)
        # Dynamic Prio (approx): 0.2*0.35 (base_type) + 0.3*0.6 (intensity_intrinsic) + ...
        # = 0.07 + 0.18 + 0 + 0.15 + 0 - 0.01 = 0.39. Scaled: 3.9
        # This test relies on _calculate_dynamic_priority correctly using the 'calculated_intensity' from source_trigger for these intrinsic goals.
        g3_id = mot_sys.add_goal("Competence Moderate Intensity", "INTRINSIC_COMPETENCE", initial_priority=3.0, source_trigger={"calculated_intensity": 0.6, "trigger_type": "LOW_PROFICIENCY"}, target_skill_id="skill_x")

        # Expected order based on rough calculation: g2 (4.85), g1 (4.8), g3 (3.9)

        # Clear goal updates from adding goals
        self.received_goal_updates.clear()
        mot_sys._log.clear() # Clear log to check sorting logs

        active_goals_sorted = mot_sys.get_active_goals()

        self.assertEqual(len(active_goals_sorted), 3)
        self.assertEqual(active_goals_sorted[0].id, g2_id, "Curiosity goal with high intensity should be first.")
        self.assertEqual(active_goals_sorted[1].id, g1_id, "Extrinsic goal should be second.")
        self.assertEqual(active_goals_sorted[2].id, g3_id, "Competence goal should be third.")

        # Check logs for dynamic priority calculations (at least one to show it's working)
        self.assertTrue(any(f"Goal '{g1_id}'" in log and "NormDynP=" in log for log in mot_sys._log))
        self.assertTrue(any(f"Goal '{g2_id}'" in log and "NormDynP=" in log for log in mot_sys._log))
        self.assertTrue(any(f"Goal '{g3_id}'" in log and "NormDynP=" in log for log in mot_sys._log))
        self.assertTrue(any("Top 3 dynamically prioritized goals" in log for log in mot_sys._log))


    @unittest.mock.patch.object(ConcreteMotivationalSystemModule, '_get_urgency_factor')
    def test_dynamic_priority_influenced_by_mocked_factor(self, mock_get_urgency):
        mot_sys = self.mot_sys
        mot_sys.goals.clear()
        self.received_goal_updates.clear()
        mot_sys._log.clear()

        # Goal 1: Extrinsic, base priority 7.0. Intensity 0.7.
        # Default urg=0. DynPrio ~0.2*0.5 + 0.3*0.7 + 0.15*1 - 0.01 = 0.1 + 0.21 + 0.15 - 0.01 = 0.45. Scaled: 4.5
        g1_id = mot_sys.add_goal("Task A", "EXTRINSIC_TASK", 7.0)

        # Goal 2: Extrinsic, base priority 6.0. Intensity 0.6.
        # Default urg=0. DynPrio ~0.2*0.5 + 0.3*0.6 + 0.15*1 - 0.01 = 0.1 + 0.18 + 0.15 - 0.01 = 0.42. Scaled: 4.2
        g2_id = mot_sys.add_goal("Task B", "EXTRINSIC_TASK", 6.0)

        # Mock _get_urgency_factor to return a high value for g2_id
        def side_effect_urgency(goal, current_context):
            if goal.id == g2_id:
                return 0.9 # High urgency for g2
            return 0.0 # Default for others
        mock_get_urgency.side_effect = side_effect_urgency

        # Recalculate for g2 with urgency:
        # DynPrio_g2 ~0.1 + 0.18 + 0.15*0.9 (urg) + 0.15*1 - 0.01 = 0.1 + 0.18 + 0.135 + 0.15 - 0.01 = 0.555. Scaled: 5.55
        # Now g2 should be higher than g1 (4.5)

        active_goals_sorted = mot_sys.get_active_goals()
        self.assertEqual(len(active_goals_sorted), 2)
        self.assertEqual(active_goals_sorted[0].id, g2_id, "Task B (g2) should be higher priority due to mocked urgency.")
        self.assertEqual(active_goals_sorted[1].id, g1_id)

        # Ensure the mock was called
        self.assertTrue(mock_get_urgency.called)
        self.assertTrue(any(f"Urg=0.90(w:0.15)" in log for log in mot_sys._log if f"Goal '{g2_id}'" in log))
        self.assertTrue(any(f"Urg=0.00(w:0.15)" in log for log in mot_sys._log if f"Goal '{g1_id}'" in log))


    def test_suggest_highest_priority_goal_logs_conflict(self):
        mot_sys = self.mot_sys
        mot_sys.goals.clear()
        self.received_goal_updates.clear() # Clear updates from add_goal
        mot_sys._log.clear()

        # Create goals that will have very similar dynamic priorities
        # Goal 1: Extrinsic, Prio 7.0 -> Intensity 0.7. DynPrio ~ 4.5
        # (0.2*0.5 + 0.3*0.7 + 0.15*0 + 0.15*1 + 0.1*0 - 0.1*0.1 = 0.1 + 0.21 + 0.15 - 0.01 = 0.45)
        g1_id = mot_sys.add_goal("High Priority Task 1", "EXTRINSIC_TASK", 7.0, source_trigger={"originator":"test"})

        # Goal 2: Curiosity, Prio 3.0, Intensity 0.8. DynPrio ~ 4.4
        # (0.2*0.3 + 0.3*0.8 + 0.15*0 + 0.15*1 + 0.1*0 - 0.1*0.1 = 0.06 + 0.24 + 0.15 - 0.01 = 0.44)
        # To make them very close, let's adjust g2's intensity slightly
        # Let g2_intensity = 0.83: 0.06 + 0.3*0.83 + 0.15 - 0.01 = 0.06 + 0.249 + 0.15 - 0.01 = 0.449. Scaled: 4.49
        g2_id = mot_sys.add_goal("High Intensity Curiosity", "INTRINSIC_CURIOSITY", 3.0,
                                 source_trigger={"calculated_intensity": 0.83, "trigger_type": "KNOWLEDGE_GAP"})

        # Goal 3: Another Extrinsic, Prio 7.0 -> Intensity 0.7. DynPrio ~ 4.5
        g3_id = mot_sys.add_goal("High Priority Task 2", "EXTRINSIC_TASK", 7.0, source_trigger={"originator":"test"})

        # Clear logs from add_goal to focus on suggest_highest_priority_goal logs
        mot_sys._log.clear()

        # Expected order: g1 (4.5), g3 (4.5), g2 (4.49) - g1 and g3 are very close.
        # The sorting might put g1 or g3 first if scores are identical before float precision issues.

        suggested_goal = mot_sys.suggest_highest_priority_goal()
        self.assertIsNotNone(suggested_goal)

        # Check if the log message for potential conflict is present
        conflict_log_found = any("Potential goal conflict or similar high priority for goals" in log for log in mot_sys._log)
        self.assertTrue(conflict_log_found, "Conflict log message not found when top priorities are very close.")

        # Verify the top suggested goal is one of the conflicting ones
        self.assertIn(suggested_goal.id, [g1_id, g3_id])

    # --- Tests for Emotional Influence on Dynamic Priority ---

    def _get_goal_dyn_prio(self, goal_id: str, goals_with_scores: List[tuple[float, Goal]]) -> Optional[float]:
        """Helper to find a goal's dynamic priority from the list returned by get_active_goals."""
        for score, goal in goals_with_scores:
            if goal.id == goal_id:
                return score
        return None

    def test_dynamic_priority_positive_emotion_boost(self):
        mot_sys = self.mot_sys
        mot_sys.goals.clear()
        mot_sys._log.clear()

        # Set positive emotional state
        positive_emotion = EmotionalStateChangePayload(current_emotion_profile={"valence": 0.7, "arousal": 0.5, "dominance": 0.6})
        mot_sys._last_emotional_state = positive_emotion

        g1_id = mot_sys.add_goal("Task Alpha", "EXTRINSIC_TASK", initial_priority=5.0) # Intensity 0.5

        mot_sys._log.clear() # Clear add_goal logs
        goals_with_scores = mot_sys.get_active_goals(return_with_priority_scores=True)

        self.assertTrue(any(f"EmoState=(V=0.70, A=0.50, EmoModRaw=0.070, WeightedEmoMod=0.007)" in log for log in mot_sys._log), "Emotional modifier log not found or incorrect for positive emotion.")

        # We need a baseline to compare against. Let's calculate without emotion.
        mot_sys._last_emotional_state = None # Neutral emotion
        mot_sys._log.clear()
        goals_with_scores_neutral = mot_sys.get_active_goals(return_with_priority_scores=True)

        prio_g1_positive = self._get_goal_dyn_prio(g1_id, goals_with_scores)
        prio_g1_neutral = self._get_goal_dyn_prio(g1_id, goals_with_scores_neutral)

        self.assertIsNotNone(prio_g1_positive)
        self.assertIsNotNone(prio_g1_neutral)
        self.assertGreater(prio_g1_positive, prio_g1_neutral, "Positive emotion should boost dynamic priority.")

    def test_dynamic_priority_negative_emotion_dampen(self):
        mot_sys = self.mot_sys
        mot_sys.goals.clear()
        mot_sys._log.clear()

        negative_emotion = EmotionalStateChangePayload(current_emotion_profile={"valence": -0.8, "arousal": 0.6})
        mot_sys._last_emotional_state = negative_emotion

        g1_id = mot_sys.add_goal("Task Beta", "EXTRINSIC_TASK", initial_priority=6.0) # Intensity 0.6

        mot_sys._log.clear()
        goals_with_scores_negative = mot_sys.get_active_goals(return_with_priority_scores=True)
        self.assertTrue(any(f"EmoState=(V=-0.80, A=0.60, EmoModRaw=-0.080, WeightedEmoMod=-0.008)" in log for log in mot_sys._log), "Emotional modifier log not found or incorrect for negative emotion.")

        mot_sys._last_emotional_state = None
        mot_sys._log.clear()
        goals_with_scores_neutral = mot_sys.get_active_goals(return_with_priority_scores=True)

        prio_g1_negative = self._get_goal_dyn_prio(g1_id, goals_with_scores_negative)
        prio_g1_neutral = self._get_goal_dyn_prio(g1_id, goals_with_scores_neutral)

        self.assertIsNotNone(prio_g1_negative)
        self.assertIsNotNone(prio_g1_neutral)
        self.assertLess(prio_g1_negative, prio_g1_neutral, "Negative emotion should dampen dynamic priority.")

    def test_dynamic_priority_high_arousal_amplification(self):
        mot_sys = self.mot_sys
        mot_sys.goals.clear()
        mot_sys._log.clear()

        high_arousal_emotion = EmotionalStateChangePayload(current_emotion_profile={"valence": 0.1, "arousal": 0.85}) # Valence near neutral
        mot_sys._last_emotional_state = high_arousal_emotion

        g1_id = mot_sys.add_goal("Task Gamma", "EXTRINSIC_TASK", initial_priority=5.0) # Intensity 0.5

        mot_sys._log.clear()
        goals_with_scores_aroused = mot_sys.get_active_goals(return_with_priority_scores=True)
        # Expected EmoModRaw = (0.1 * 0.1 for V) + (0.85 * 0.05 for A) = 0.01 + 0.0425 = 0.0525. Weighted = 0.00525
        self.assertTrue(any(f"EmoState=(V=0.10, A=0.85, EmoModRaw=0.053, WeightedEmoMod=0.005)" in log for log in mot_sys._log), "Emotional modifier log not found or incorrect for high arousal.")


        mot_sys._last_emotional_state = None
        mot_sys._log.clear()
        goals_with_scores_neutral = mot_sys.get_active_goals(return_with_priority_scores=True)

        prio_g1_aroused = self._get_goal_dyn_prio(g1_id, goals_with_scores_aroused)
        prio_g1_neutral = self._get_goal_dyn_prio(g1_id, goals_with_scores_neutral)

        self.assertIsNotNone(prio_g1_aroused)
        self.assertIsNotNone(prio_g1_neutral)
        # High arousal adds a positive modifier, so priority should be higher
        self.assertGreater(prio_g1_aroused, prio_g1_neutral, "High arousal should slightly amplify/boost dynamic priority.")


    def test_dynamic_priority_boredom_boost_for_intrinsic(self):
        mot_sys = self.mot_sys
        mot_sys.goals.clear()
        mot_sys._log.clear()

        bored_emotion = EmotionalStateChangePayload(current_emotion_profile={"valence": 0.0, "arousal": 0.1})
        mot_sys._last_emotional_state = bored_emotion

        # Extrinsic goal with moderate intensity
        g_ext_id = mot_sys.add_goal("Extrinsic Task Delta", "EXTRINSIC_TASK", initial_priority=5.0) # Intensity 0.5
        # Intrinsic goal with slightly lower base parameters before emotional boost
        g_int_id = mot_sys.add_goal("Intrinsic Curiosity Epsilon", "INTRINSIC_CURIOSITY", initial_priority=3.0, source_trigger={"calculated_intensity": 0.4}) # Intensity 0.4

        mot_sys._log.clear()
        goals_with_scores_bored = mot_sys.get_active_goals(return_with_priority_scores=True)

        # Check log for intrinsic goal's emotional modifier
        # For intrinsic goal: EmoModRaw = 0.1 (boredom boost). Weighted = 0.01
        self.assertTrue(any(f"Goal '{g_int_id}'" in log and "EmoState=(V=0.00, A=0.10, EmoModRaw=0.100, WeightedEmoMod=0.010)" in log for log in mot_sys._log), "Boredom boost log not found for intrinsic goal.")
        # For extrinsic goal: EmoModRaw = 0.0. Weighted = 0.0
        self.assertTrue(any(f"Goal '{g_ext_id}'" in log and "EmoState=(V=0.00, A=0.10, EmoModRaw=0.000, WeightedEmoMod=0.000)" in log for log in mot_sys._log), "Extrinsic goal should not get boredom boost.")

        prio_g_int_bored = self._get_goal_dyn_prio(g_int_id, goals_with_scores_bored)
        prio_g_ext_bored = self._get_goal_dyn_prio(g_ext_id, goals_with_scores_bored)
        self.assertIsNotNone(prio_g_int_bored)
        self.assertIsNotNone(prio_g_ext_bored)

        # To make a stronger assertion, let's get neutral scores
        mot_sys._last_emotional_state = None
        mot_sys._log.clear()
        goals_with_scores_neutral = mot_sys.get_active_goals(return_with_priority_scores=True)
        prio_g_int_neutral = self._get_goal_dyn_prio(g_int_id, goals_with_scores_neutral)
        prio_g_ext_neutral = self._get_goal_dyn_prio(g_ext_id, goals_with_scores_neutral)

        self.assertIsNotNone(prio_g_int_neutral)
        self.assertGreater(prio_g_int_bored, prio_g_int_neutral, "Intrinsic goal priority should be higher in boredom state than neutral.")
        # Check if the boost was enough to change order (depends on other factors and weights)
        # For this test, we primarily check the boost was applied.
        # If prio_g_int_neutral was already > prio_g_ext_neutral, this test doesn't show reordering.
        # If prio_g_int_neutral < prio_g_ext_neutral, then we'd hope prio_g_int_bored > prio_g_ext_bored or closer.
        # This test is more about ensuring the specific boredom boost is logged and affects the intrinsic score positively.

    def test_calculate_curiosity_intensity_logic(self):
        mot_sys = self.mot_sys # Use the instance from setUp for logging consistency if needed
        mot_sys._log.clear() # Clear logs for this specific test

        active_goals_empty = [] # No active goals for these direct tests

        # Test case 1: NOVEL_STIMULUS
        trigger_novel = {"novelty_score": 0.8, "complexity_score": 0.6}
        # Expected: (0.4 * 0.8) + (0.2 * 0.6) = 0.32 + 0.12 = 0.44. Then relevance: 0.44 * (1 + 0.3 * 0.1) = 0.44 * 1.03 = 0.4532
        intensity_novel = mot_sys._calculate_curiosity_intensity("NOVEL_STIMULUS", trigger_novel, active_goals_empty)
        self.assertAlmostEqual(intensity_novel, 0.4532, places=4)
        self.assertTrue(any("Curiosity (NovelStimulus): novelty=0.80, complexity=0.60 -> base_intensity=0.44" in log for log in mot_sys._log))

        # Test case 1b: NOVEL_STIMULUS - clamping
        trigger_novel_high = {"novelty_score": 1.0, "complexity_score": 1.0} # Raw: 0.4*1 + 0.2*1 = 0.6. Relevance: 0.6 * 1.03 = 0.618
        intensity_novel_high = mot_sys._calculate_curiosity_intensity("NOVEL_STIMULUS", trigger_novel_high, active_goals_empty)
        self.assertAlmostEqual(intensity_novel_high, 0.618, places=3) # Should be clamped to 1.0 if formula results > 1

        trigger_novel_extreme = {"novelty_score": 2.0, "complexity_score": 2.0} # Raw: 0.4*2 + 0.2*2 = 0.8 + 0.4 = 1.2. Relevance: 1.2 * 1.03 = 1.236
        intensity_novel_extreme = mot_sys._calculate_curiosity_intensity("NOVEL_STIMULUS", trigger_novel_extreme, active_goals_empty)
        self.assertAlmostEqual(intensity_novel_extreme, 1.0, places=4) # Clamped
        self.assertTrue(any("Intensity clamped from 1.2360 to 1.0000" in log for log in mot_sys._log if "Curiosity:" in log))


        # Test case 2: PREDICTION_ERROR
        trigger_error = {"error_magnitude": 0.7}
        # Expected: 0.5 * 0.7 = 0.35. Relevance: 0.35 * 1.03 = 0.3605
        intensity_error = mot_sys._calculate_curiosity_intensity("PREDICTION_ERROR", trigger_error, active_goals_empty)
        self.assertAlmostEqual(intensity_error, 0.3605, places=4)
        self.assertTrue(any("Curiosity (PredictionError): error_mag=0.70 -> base_intensity=0.35" in log for log in mot_sys._log))

        # Test case 3: KNOWLEDGE_GAP
        trigger_gap = {"confidence": 0.3} # Uncertainty = 0.7
        # Expected: 0.6 * 0.7 = 0.42. Relevance: 0.42 * 1.03 = 0.4326
        intensity_gap = mot_sys._calculate_curiosity_intensity("KNOWLEDGE_GAP", trigger_gap, active_goals_empty)
        self.assertAlmostEqual(intensity_gap, 0.4326, places=4)
        self.assertTrue(any("Curiosity (KnowledgeGap): confidence=0.30, uncertainty=0.70 -> base_intensity=0.42" in log for log in mot_sys._log))

        # Test case 4: Empty trigger data
        intensity_empty = mot_sys._calculate_curiosity_intensity("NOVEL_STIMULUS", {}, active_goals_empty)
        # Expected: (0.4*0) + (0.2*0) = 0. Relevance: 0 * 1.03 = 0
        self.assertAlmostEqual(intensity_empty, 0.0, places=4)

        # Test case 5: Unknown trigger type
        intensity_unknown = mot_sys._calculate_curiosity_intensity("UNKNOWN_TRIGGER", {}, active_goals_empty)
        self.assertAlmostEqual(intensity_unknown, 0.0, places=4) # Base intensity remains 0, relevance factor doesn't change it from 0
        self.assertTrue(any("Unknown curiosity trigger_type: UNKNOWN_TRIGGER" in log for log in mot_sys._log))

    def test_calculate_competence_drive_intensity_logic(self):
        mot_sys = self.mot_sys
        mot_sys._log.clear()
        active_goals_empty = []

        # Test case 1: High proficiency gap, high importance
        skill_data1 = {"proficiency": 0.2, "importance": 0.9, "target_proficiency": 1.0}
        # Expected: gap = 0.8. Intensity = (0.6 * 0.8) + (0.4 * 0.9) = 0.48 + 0.36 = 0.84
        intensity1 = mot_sys._calculate_competence_drive_intensity("skill1", skill_data1, active_goals_empty)
        self.assertAlmostEqual(intensity1, 0.84, places=4)
        self.assertTrue(any("Competence (Skill: skill1): proficiency=0.20, target=1.00, importance=0.90 -> proficiency_gap=0.80, base_intensity=0.84" in log for log in mot_sys._log))

        # Test case 2: Low proficiency gap, low importance
        skill_data2 = {"proficiency": 0.8, "importance": 0.1, "target_proficiency": 0.9}
        # Expected: gap = 0.1. Intensity = (0.6 * 0.1) + (0.4 * 0.1) = 0.06 + 0.04 = 0.10
        intensity2 = mot_sys._calculate_competence_drive_intensity("skill2", skill_data2, active_goals_empty)
        self.assertAlmostEqual(intensity2, 0.10, places=4)

        # Test case 3: Current proficiency > target proficiency (gap should be 0)
        skill_data3 = {"proficiency": 0.9, "importance": 0.7, "target_proficiency": 0.8}
        # Expected: gap = 0. Intensity = (0.6 * 0.0) + (0.4 * 0.7) = 0.0 + 0.28 = 0.28
        intensity3 = mot_sys._calculate_competence_drive_intensity("skill3", skill_data3, active_goals_empty)
        self.assertAlmostEqual(intensity3, 0.28, places=4)
        self.assertTrue(any("proficiency_gap=0.00" in log for log in mot_sys._log if "Skill: skill3" in log))

        # Test case 4: Clamping (if raw calculation > 1.0)
        skill_data4 = {"proficiency": 0.1, "importance": 1.0, "target_proficiency": 1.0} # gap = 0.9
        # Expected: (0.6 * 0.9) + (0.4 * 1.0) = 0.54 + 0.4 = 0.94 (This is not > 1, let's use higher values if weights were different)
        # Assuming weights could lead to > 1. For current weights, max is 0.6*1 + 0.4*1 = 1.0.
        # To test clamping, we'd need to artificially make base_intensity > 1 or mock the calculation.
        # For now, verify it doesn't exceed 1.0 with max inputs.
        intensity4 = mot_sys._calculate_competence_drive_intensity("skill4", skill_data4, active_goals_empty)
        self.assertAlmostEqual(intensity4, 0.94, places=4)
        self.assertLessEqual(intensity4, 1.0)

        # Let's assume a hypothetical case where base_intensity could be > 1 to check clamping log
        # This requires temporarily overriding the calculation or checking the clamp function directly.
        # Since _calculate_competence_drive_intensity calls max(0.0, min(1.0, final_intensity)),
        # we can trust the clamp. A log message for clamping would appear if final_intensity != clamped_intensity.

        # Test case 5: Empty skill data
        intensity_empty = mot_sys._calculate_competence_drive_intensity("skill_empty", {}, active_goals_empty)
        # Defaults: proficiency=0, importance=0.5, target_proficiency=1.0. Gap = 1.0
        # Expected: (0.6 * 1.0) + (0.4 * 0.5) = 0.6 + 0.2 = 0.8
        self.assertAlmostEqual(intensity_empty, 0.8, places=4)

        # Test case 6: Zero importance
        skill_data_zero_imp = {"proficiency": 0.2, "importance": 0.0, "target_proficiency": 1.0} # gap = 0.8
        # Expected: (0.6 * 0.8) + (0.4 * 0.0) = 0.48
        intensity_zero_imp = mot_sys._calculate_competence_drive_intensity("skill_zero_imp", skill_data_zero_imp, active_goals_empty)
        self.assertAlmostEqual(intensity_zero_imp, 0.48, places=4)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
