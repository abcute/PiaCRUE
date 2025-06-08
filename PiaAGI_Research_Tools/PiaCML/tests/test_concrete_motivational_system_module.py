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
    from PiaAGI_Research_Tools.PiaCML.core_messages import GenericMessage, GoalUpdatePayload, ActionEventPayload
    from PiaAGI_Research_Tools.PiaCML.concrete_motivational_system_module import ConcreteMotivationalSystemModule, Goal
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from message_bus import MessageBus
    from core_messages import GenericMessage, GoalUpdatePayload, ActionEventPayload
    from concrete_motivational_system_module import ConcreteMotivationalSystemModule, Goal


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
        self.assertTrue(new_goal.priority > 7.0) # Expected intensity > 0.7 for these scores
        self.assertIn("Investigate novel stimulus: stimulus_alpha", new_goal.description)
        self.assertEqual(new_goal.source_trigger["trigger_type"], "NOVEL_STIMULUS")
        self.assertEqual(new_goal.source_trigger["novelty_score"], 0.9)
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
        # Intensity for (1-0.2)*0.6 = 0.48. Times (1+0.3*0.1) approx 0.49. Priority = 4.9
        self.assertTrue(new_goal.priority > 4.0 and new_goal.priority < 6.0)
        self.assertIn("Explore knowledge gap for concept: concept_X", new_goal.description)
        self.assertEqual(new_goal.source_trigger["trigger_type"], "KNOWLEDGE_GAP")
        self.assertEqual(new_goal.source_trigger["concept_id"], "concept_X")
        self.assertEqual(new_goal.source_trigger["current_confidence"], 0.2)
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
                self.assertTrue(goal.priority > 7.0) # Intensity 0.74 * 10
                self.assertIn("Improve skill: skill_nav_basic", goal.description)
                self.assertEqual(goal.source_trigger["trigger_type"], "LOW_PROFICIENCY")
                self.assertEqual(goal.competence_details["current_proficiency"], 0.3)
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


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
```
