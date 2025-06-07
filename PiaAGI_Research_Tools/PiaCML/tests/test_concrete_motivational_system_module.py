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
        # Module instance created in each test method or a specific setup method for tests
        self.received_goal_updates: List[GenericMessage] = []

    def _goal_update_listener(self, message: GenericMessage):
        if isinstance(message.payload, GoalUpdatePayload):
            self.received_goal_updates.append(message)

    def tearDown(self):
        self.received_goal_updates.clear()

    # --- Test Publishing GoalUpdate Messages ---
    def test_add_goal_publishes_goal_update(self):
        mot_sys = ConcreteMotivationalSystemModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            self.bus.subscribe(self.module_id, "GoalUpdate", self._goal_update_listener)

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
        mot_sys = ConcreteMotivationalSystemModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            self.bus.subscribe(self.module_id, "GoalUpdate", self._goal_update_listener)
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
        mot_sys = ConcreteMotivationalSystemModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            self.bus.subscribe(self.module_id, "GoalUpdate", self._goal_update_listener)
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
        # These calls should not raise errors and no messages should be "published" (bus is None)
        try:
            goal_id = mot_sys_no_bus.add_goal("No Bus Add", "NOBUS_TYPE", 0.1)
            mot_sys_no_bus.update_goal_status(goal_id, "ACTIVE")
            mot_sys_no_bus.update_goal_priority(goal_id, 0.2)
        except Exception as e:
            self.fail(f"Motivational system methods raised an exception with no bus: {e}")
        self.assertEqual(len(self.received_goal_updates), 0) # Listener is on self.bus, not used by mot_sys_no_bus

    # --- Test Subscribing to ActionEvent Messages ---
    def test_handle_action_event_achieved_updates_goal(self):
        mot_sys = ConcreteMotivationalSystemModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            self.bus.subscribe(self.module_id, "GoalUpdate", self._goal_update_listener)
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
        mot_sys = ConcreteMotivationalSystemModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            self.bus.subscribe(self.module_id, "GoalUpdate", self._goal_update_listener)
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
        mot_sys = ConcreteMotivationalSystemModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            self.bus.subscribe(self.module_id, "GoalUpdate", self._goal_update_listener)
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
        mot_sys = ConcreteMotivationalSystemModule(message_bus=self.bus, module_id=self.module_id)
        mot_sys.add_goal("Goal 1 for status", "T1", 0.5)
        status = mot_sys.get_module_status()

        self.assertEqual(status["module_id"], self.module_id)
        self.assertTrue(status["message_bus_configured"])
        self.assertEqual(status["total_goals"], 1)
        self.assertEqual(status["goals_by_status"].get("PENDING"), 1)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
```
