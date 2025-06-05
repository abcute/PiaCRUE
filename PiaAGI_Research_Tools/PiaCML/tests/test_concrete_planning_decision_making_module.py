import unittest
import os
import sys
import uuid # For plan IDs if needed, and message IDs implicitly
from unittest.mock import MagicMock, call
import time # For timestamps if needed for GoalUpdatePayload

# Adjust path for consistent imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    from PiaAGI_Research_Tools.PiaCML import (
        ConcretePlanningAndDecisionMakingModule,
        MessageBus,
        GenericMessage,
        GoalUpdatePayload, # For receiving goals
        ActionCommandPayload # For publishing actions
        # Goal dataclass might be imported if planner internally converts payload to Goal objects
    )
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from concrete_planning_decision_making_module import ConcretePlanningAndDecisionMakingModule
    try:
        from message_bus import MessageBus
        from core_messages import GenericMessage, GoalUpdatePayload, ActionCommandPayload
    except ImportError:
        MessageBus = None
        GenericMessage = None
        GoalUpdatePayload = None
        ActionCommandPayload = None

class TestConcretePlanningAndDecisionMakingModule(unittest.TestCase):

    def setUp(self):
        self.bus = MessageBus() if MessageBus else None# Real bus for testing subscription
        self.mock_bus = MagicMock(spec=MessageBus) if MessageBus else None # Mock bus for testing publishing

        self.planner_no_bus = ConcretePlanningAndDecisionMakingModule()
        self.planner_with_mock_bus = ConcretePlanningAndDecisionMakingModule(message_bus=self.mock_bus)
        self.planner_with_real_bus = ConcretePlanningAndDecisionMakingModule(message_bus=self.bus)

        self._original_stdout = sys.stdout
        # Comment out print suppression for easier debugging if tests fail
        # sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        # sys.stdout.close()
        sys.stdout = self._original_stdout

    # --- Existing tests adapted to use planner_no_bus ---
    def test_initial_status_no_bus(self): # Renamed
        status = self.planner_no_bus.get_module_status()
        self.assertEqual(status['module_type'], 'ConcretePlanningAndDecisionMakingModule')
        self.assertEqual(status['known_plan_templates_count'], 2) # Updated based on current implementation
        # These are no longer part of status for the bus-integrated version
        # self.assertEqual(status['evaluated_plans_count'], 0)
        # self.assertIsNone(status['last_selected_plan_id'])
        self.assertEqual(len(self.planner_no_bus.pending_goals), 0)


    def test_create_plan_from_template_no_bus(self): # Renamed
        goal = {"description": "achieve_goal_A"} # This still uses the old dict format for goal
        plans = self.planner_no_bus.create_plan(goal, {}, {})
        self.assertEqual(len(plans), 1)
        plan = plans[0]
        self.assertEqual(plan['goal_description'], "achieve_goal_A")
        self.assertEqual(len(plan['steps']), 2)

    def test_create_plan_default_no_bus(self): # Renamed
        goal = {"description": "non_existent_goal"}
        plans = self.planner_no_bus.create_plan(goal, {}, {})
        self.assertEqual(len(plans), 1)
        plan = plans[0]
        self.assertEqual(plan['steps'][0]['action_type'], "default_action_for_unknown_goal")

    def test_evaluate_plan_basic_score_no_bus(self): # Renamed
        plan = {"plan_id": "test_plan1", "steps": [{}, {}, {}]}
        # evaluate_plan is not directly used by the bus-integrated path for now
        evaluation = self.planner_no_bus.evaluate_plan(plan, {}, {})
        self.assertEqual(evaluation['plan_id'], "test_plan1")
        self.assertEqual(evaluation['score'], 70)

    def test_select_action_or_plan_no_bus(self): # Renamed
        eval_plan1 = {"plan_id": "p1", "score": 80}
        eval_plan2 = {"plan_id": "p2", "score": 95}
        selected_eval = self.planner_no_bus.select_action_or_plan([eval_plan1, eval_plan2])
        self.assertEqual(selected_eval['plan_id'], "p2")


    # --- New Tests for MessageBus Integration ---
    def test_initialization_with_bus_subscription(self):
        """Test Planner initialization with a message bus and subscription to GoalUpdate."""
        if not MessageBus: self.skipTest("MessageBus components not available")

        self.assertIsNotNone(self.planner_with_real_bus.message_bus)
        subscribers = self.bus.get_subscribers_for_type("GoalUpdate")

        found_subscription = any(
            sub[0] == "ConcretePlanningAndDecisionMakingModule_01" and
            sub[1] == self.planner_with_real_bus.handle_goal_update_message
            for sub in subscribers if sub # Check if sub is not None
        )
        self.assertTrue(found_subscription, "Planner did not subscribe to GoalUpdate messages.")

    def test_handle_goal_update_message(self):
        """Test that Planner receives and stores GoalUpdate messages."""
        if not MessageBus or not GenericMessage or not GoalUpdatePayload:
            self.skipTest("MessageBus or core message components not available")

        self.assertEqual(len(self.planner_with_real_bus.pending_goals), 0)

        goal_payload1 = GoalUpdatePayload(goal_id="g1", goal_description="Goal 1", priority=0.8, status="ACTIVE", originator="Test")
        msg1 = GenericMessage(source_module_id="TestMotSys", message_type="GoalUpdate", payload=goal_payload1)

        goal_payload2 = GoalUpdatePayload(goal_id="g2", goal_description="Goal 2", priority=0.9, status="PENDING", originator="Test")
        msg2 = GenericMessage(source_module_id="TestMotSys", message_type="GoalUpdate", payload=goal_payload2)

        self.bus.publish(msg1)
        self.bus.publish(msg2)

        self.assertEqual(len(self.planner_with_real_bus.pending_goals), 2)
        # Check if sorted by priority (g2 should be first)
        self.assertEqual(self.planner_with_real_bus.pending_goals[0].goal_id, "g2")
        self.assertEqual(self.planner_with_real_bus.pending_goals[1].goal_id, "g1")

        # Test duplicate handling (same id, same status - should not add)
        self.bus.publish(msg2) # Publish g2 again
        self.assertEqual(len(self.planner_with_real_bus.pending_goals), 2)

        # Test update (same id, different status - should replace)
        goal_payload2_updated = GoalUpdatePayload(goal_id="g2", goal_description="Goal 2 Updated", priority=0.95, status="ACTIVE", originator="Test")
        msg2_updated = GenericMessage(source_module_id="TestMotSys", message_type="GoalUpdate", payload=goal_payload2_updated)
        self.bus.publish(msg2_updated)
        self.assertEqual(len(self.planner_with_real_bus.pending_goals), 2)
        self.assertEqual(self.planner_with_real_bus.pending_goals[0].priority, 0.95) # g2 updated and still highest
        self.assertEqual(self.planner_with_real_bus.pending_goals[0].goal_description, "Goal 2 Updated")


    def test_develop_and_dispatch_plan_publishes_action_commands(self):
        """Test that develop_and_dispatch_plan publishes ActionCommand messages."""
        if not MessageBus or not GenericMessage or not ActionCommandPayload or not GoalUpdatePayload:
            self.skipTest("MessageBus or core message components not available")

        sample_goal_payload = GoalUpdatePayload(
            goal_id="g_plan_test", goal_description="Test plan dispatch",
            priority=0.8, status="ACTIVE", originator="Test"
        )

        success = self.planner_with_mock_bus.develop_and_dispatch_plan(sample_goal_payload)
        self.assertTrue(success)

        self.mock_bus.publish.assert_called() # Called at least once
        # Check details of the first call (conceptual step 1)
        args, _ = self.mock_bus.publish.call_args_list[0]
        published_message: GenericMessage = args[0]
        self.assertEqual(published_message.message_type, "ActionCommand")
        self.assertIsInstance(published_message.payload, ActionCommandPayload)
        self.assertEqual(published_message.payload.parameters["task"], "Step 1 for Test plan dispatch")
        self.assertEqual(published_message.payload.priority, 0.8)

        # Check if a second action was published (since priority > 0.7)
        self.assertGreaterEqual(self.mock_bus.publish.call_count, 2)
        args_step2, _ = self.mock_bus.publish.call_args_list[1]
        published_message_step2: GenericMessage = args_step2[0]
        self.assertEqual(published_message_step2.payload.parameters["task"], "Step 2 for Test plan dispatch")


    def test_process_one_pending_goal_publishes_actions(self):
        """Test process_one_pending_goal selects a goal and publishes actions."""
        if not MessageBus or not GenericMessage or not ActionCommandPayload or not GoalUpdatePayload:
            self.skipTest("MessageBus or core message components not available")

        # Add a goal to pending_goals (can be done via handle_goal_update or directly for isolated test)
        goal_payload = GoalUpdatePayload(
            goal_id="g_process_test", goal_description="Process this goal",
            priority=0.9, status="ACTIVE", originator="TestProcess"
        )
        # Simulate receiving this goal
        if self.planner_with_mock_bus.message_bus: # It has a mock bus, but handle_goal_update is for real bus
             self.planner_with_mock_bus.handle_goal_update_message(
                 GenericMessage(source_module_id="sim", message_type="GoalUpdate", payload=goal_payload)
             )
        else: # Fallback if direct add is needed because bus setup is complex
            self.planner_with_mock_bus.pending_goals.append(goal_payload)
            self.planner_with_mock_bus.pending_goals.sort(key=lambda g: g.priority, reverse=True)

        self.assertEqual(len(self.planner_with_mock_bus.pending_goals), 1)

        processed = self.planner_with_mock_bus.process_one_pending_goal()
        self.assertTrue(processed)
        self.assertEqual(len(self.planner_with_mock_bus.pending_goals), 0) # Goal should be removed

        self.mock_bus.publish.assert_called() # At least one action command published
        # Further checks on published message content could be added here, similar to above test

    def test_no_bus_scenarios(self):
        """Test behavior when no message bus is configured."""
        self.assertIsNone(self.planner_no_bus.message_bus)
        sample_goal_payload = GoalUpdatePayload(
            goal_id="g_no_bus", goal_description="No bus test",
            priority=0.5, status="ACTIVE", originator="TestNoBus"
        )
        # This should not error and return False as no bus to publish to
        self.assertFalse(self.planner_no_bus.develop_and_dispatch_plan(sample_goal_payload))

        # Add to pending_goals directly for planner_no_bus
        self.planner_no_bus.pending_goals.append(sample_goal_payload)
        self.assertFalse(self.planner_no_bus.process_one_pending_goal()) # Should also be false as it calls develop_and_dispatch_plan


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
