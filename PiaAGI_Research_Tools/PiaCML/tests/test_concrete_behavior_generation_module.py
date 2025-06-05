import unittest
import os
import sys
from unittest.mock import MagicMock # Added

# Adjust path for consistent imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    from PiaAGI_Research_Tools.PiaCML import (
        ConcreteBehaviorGenerationModule,
        MessageBus,               # Added
        GenericMessage,           # Added
        ActionCommandPayload      # Added
    )
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from concrete_behavior_generation_module import ConcreteBehaviorGenerationModule
    try:
        from message_bus import MessageBus
        from core_messages import GenericMessage, ActionCommandPayload
    except ImportError:
        MessageBus = None
        GenericMessage = None
        ActionCommandPayload = None


class TestConcreteBehaviorGenerationModule(unittest.TestCase):

    def setUp(self):
        self.bus = MessageBus() if MessageBus else None
        self.bhv_no_bus = ConcreteBehaviorGenerationModule()
        self.bhv_with_bus = ConcreteBehaviorGenerationModule(message_bus=self.bus)

        self._original_stdout = sys.stdout
        # Comment out print suppression for easier debugging if tests fail
        # sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        # sys.stdout.close()
        sys.stdout = self._original_stdout

    # --- Existing tests adapted to use bhv_no_bus ---
    def test_initial_status_no_bus(self): # Renamed
        status = self.bhv_no_bus.get_status()
        self.assertEqual(status['active_generation_tasks'], 0)
        self.assertIn("linguistic_output", status['supported_behavior_types'])
        self.assertEqual(status['module_type'], 'ConcreteBehaviorGenerationModule')
        self.assertIsNone(self.bhv_no_bus.message_bus) # Check bus not present
        self.assertEqual(len(self.bhv_no_bus.executed_commands_log), 0)


    def test_generate_linguistic_behavior_no_bus(self): # Renamed
        action_plan = {
            "action_type": "communicate",
            "final_message_content": "Test message"
        }
        behavior_spec = self.bhv_no_bus.generate_behavior(action_plan)
        self.assertEqual(behavior_spec['behavior_type'], "linguistic_output")
        self.assertEqual(behavior_spec['details']['content'], "Test message")

    def test_generate_tool_use_behavior_no_bus(self): # Renamed
        action_plan = {
            "action_type": "use_tool",
            "tool_id": "calculator",
        }
        behavior_spec = self.bhv_no_bus.generate_behavior(action_plan)
        self.assertEqual(behavior_spec['behavior_type'], "api_call")
        self.assertEqual(behavior_spec['details']['tool_id'], "calculator")

    def test_generate_unknown_action_type_no_bus(self): # Renamed
        action_plan = {"action_type": "perform_magic_trick"}
        behavior_spec = self.bhv_no_bus.generate_behavior(action_plan)
        self.assertEqual(behavior_spec['behavior_type'], "unknown")

    # --- New Tests for MessageBus Integration ---
    def test_initialization_with_bus_subscription(self):
        """Test BehaviorModule initialization with a message bus and subscription to ActionCommand."""
        if not MessageBus: self.skipTest("MessageBus components not available")

        self.assertIsNotNone(self.bhv_with_bus.message_bus)
        subscribers = self.bus.get_subscribers_for_type("ActionCommand")

        found_subscription = any(
            sub[0] == "ConcreteBehaviorGenerationModule_01" and
            sub[1] == self.bhv_with_bus.handle_action_command_message
            for sub in subscribers if sub # Check if sub is not None
        )
        self.assertTrue(found_subscription, "BehaviorModule did not subscribe to ActionCommand messages.")

    def test_handle_action_command_message(self):
        """Test that BehaviorModule receives and logs ActionCommand messages."""
        if not MessageBus or not GenericMessage or not ActionCommandPayload:
            self.skipTest("MessageBus or core message components not available")

        self.assertEqual(len(self.bhv_with_bus.executed_commands_log), 0)

        action_payload = ActionCommandPayload(
            action_type="test_action",
            parameters={"param1": "value1"},
            priority=0.7,
            target_object_or_agent="test_target"
        )
        test_message = GenericMessage(
            source_module_id="TestPlannerModule",
            message_type="ActionCommand",
            payload=action_payload
        )

        self.bus.publish(test_message) # Publish to the bus bhv_with_bus is subscribed to

        self.assertEqual(len(self.bhv_with_bus.executed_commands_log), 1)
        logged_payload = self.bhv_with_bus.executed_commands_log[0]

        self.assertIsInstance(logged_payload, ActionCommandPayload)
        self.assertEqual(logged_payload.command_id, action_payload.command_id) # Command ID should be the same
        self.assertEqual(logged_payload.action_type, "test_action")
        self.assertEqual(logged_payload.parameters, {"param1": "value1"})
        self.assertEqual(logged_payload.target_object_or_agent, "test_target")

    def test_handle_action_command_unexpected_payload(self):
        """Test BehaviorModule handles ActionCommand with an unexpected payload type."""
        if not MessageBus or not GenericMessage:
            self.skipTest("MessageBus or GenericMessage not available")

        malformed_msg = GenericMessage(
            source_module_id="TestMalformedSource",
            message_type="ActionCommand",
            payload="This is not an ActionCommandPayload"
        )

        # Suppress print for this specific test of error path
        original_stdout_test = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        self.bus.publish(malformed_msg)
        sys.stdout.close()
        sys.stdout = original_stdout_test

        # Log should not grow if payload is not ActionCommandPayload
        self.assertEqual(len(self.bhv_with_bus.executed_commands_log), 0)

    def test_no_bus_scenario_for_handler(self):
        """Test that module initialized without a bus does not process bus messages."""
        if not MessageBus: self.skipTest("MessageBus components not available")

        # self.bhv_no_bus is initialized with message_bus=None
        # Publish a message on a general bus; bhv_no_bus should not receive it.
        local_bus_for_no_bus_test = MessageBus()

        action_payload = ActionCommandPayload(action_type="action_for_nobus", parameters={})
        test_message = GenericMessage(
            source_module_id="TestPlanner",
            message_type="ActionCommand",
            payload=action_payload
        )
        local_bus_for_no_bus_test.publish(test_message)

        self.assertEqual(len(self.bhv_no_bus.executed_commands_log), 0) # Should remain empty


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
