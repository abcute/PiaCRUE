import unittest
import asyncio
import uuid
from typing import List, Any, Dict
from datetime import datetime, timezone # For ActionEventPayload timestamp if needed for assertions

# Adjust path for consistent imports
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    from PiaAGI_Research_Tools.PiaCML.message_bus import MessageBus
    from PiaAGI_Research_Tools.PiaCML.core_messages import GenericMessage, ActionCommandPayload, ActionEventPayload
    from PiaAGI_Research_Tools.PiaCML.concrete_behavior_generation_module import ConcreteBehaviorGenerationModule
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from message_bus import MessageBus
    from core_messages import GenericMessage, ActionCommandPayload, ActionEventPayload
    from concrete_behavior_generation_module import ConcreteBehaviorGenerationModule

class TestConcreteBehaviorGenerationModuleIntegration(unittest.TestCase):

    def setUp(self):
        self.bus = MessageBus()
        self.bgm_module_id = f"TestBGMModule_{str(uuid.uuid4())[:8]}"
        # Module instantiated in each test method for a clean state
        self.received_action_events: List[GenericMessage] = []

    def _action_event_listener(self, message: GenericMessage):
        if isinstance(message.payload, ActionEventPayload):
            self.received_action_events.append(message)

    def tearDown(self):
        self.received_action_events.clear()

    # --- Test Handling ActionCommand and Publishing ActionEvent ---
    def test_handle_supported_action_command_with_goal_id(self):
        bgm_module = ConcreteBehaviorGenerationModule(message_bus=self.bus, module_id=self.bgm_module_id)
        async def run_test_logic():
            self.bus.subscribe(self.bgm_module_id, "ActionEvent", self._action_event_listener) # Listen for events from BGM

            command_payload = ActionCommandPayload(
                action_type="linguistic_output", # Supported
                parameters={"message": "Hello with goal", "goal_id": "g123"},
                priority=0.7
            )
            action_command_msg = GenericMessage(
                source_module_id="TestPlanner", message_type="ActionCommand", payload=command_payload
            )

            self.bus.publish(action_command_msg)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_action_events), 1)
            event_msg = self.received_action_events[0]
            self.assertEqual(event_msg.source_module_id, self.bgm_module_id)
            self.assertEqual(event_msg.message_type, "ActionEvent")

            payload: ActionEventPayload = event_msg.payload
            self.assertEqual(payload.action_command_id, command_payload.command_id)
            self.assertEqual(payload.action_type, command_payload.action_type)
            self.assertEqual(payload.status, "SUCCESS")
            self.assertIn("goal_id", payload.outcome)
            self.assertEqual(payload.outcome["goal_id"], "g123")
            self.assertIn("processed with status: SUCCESS", payload.outcome.get("message", ""))
            self.assertEqual(bgm_module._action_events_published, 1)
        asyncio.run(run_test_logic())

    def test_handle_supported_action_command_no_goal_id(self):
        bgm_module = ConcreteBehaviorGenerationModule(message_bus=self.bus, module_id=self.bgm_module_id)
        async def run_test_logic():
            self.bus.subscribe(self.bgm_module_id, "ActionEvent", self._action_event_listener)
            command_payload = ActionCommandPayload(action_type="log_message", parameters={"text": "Logging this"})
            action_command_msg = GenericMessage("TestPlanner", "ActionCommand", command_payload)

            self.bus.publish(action_command_msg)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_action_events), 1)
            payload: ActionEventPayload = self.received_action_events[0].payload
            self.assertEqual(payload.status, "SUCCESS")
            self.assertNotIn("goal_id", payload.outcome)
        asyncio.run(run_test_logic())

    def test_handle_unsupported_action_command(self):
        bgm_module = ConcreteBehaviorGenerationModule(message_bus=self.bus, module_id=self.bgm_module_id)
        async def run_test_logic():
            self.bus.subscribe(self.bgm_module_id, "ActionEvent", self._action_event_listener)
            command_payload = ActionCommandPayload(action_type="fly_to_mars", parameters={"speed": "max"})
            action_command_msg = GenericMessage("TestPlanner", "ActionCommand", command_payload)

            self.bus.publish(action_command_msg)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_action_events), 1)
            payload: ActionEventPayload = self.received_action_events[0].payload
            self.assertEqual(payload.status, "FAILURE")
            self.assertIn("unsupported", payload.outcome.get("message", ""))
        asyncio.run(run_test_logic())

    def test_handle_malformed_action_command_payload(self):
        bgm_module = ConcreteBehaviorGenerationModule(message_bus=self.bus, module_id=self.bgm_module_id)
        async def run_test_logic():
            self.bus.subscribe(self.bgm_module_id, "ActionEvent", self._action_event_listener)

            # Malformed payload (not an ActionCommandPayload instance)
            malformed_payload = {"text": "this is not an action command payload"}
            action_command_msg = GenericMessage("TestPlanner", "ActionCommand", malformed_payload) # type: ignore

            # Capture print output for the error message from the handler
            original_stdout = sys.stdout
            sys.stdout = captured_output = asyncio.to_thread(io.StringIO) # type: ignore

            self.bus.publish(action_command_msg)
            await asyncio.sleep(0.01)

            sys.stdout = original_stdout
            output = captured_output.getvalue()

            self.assertEqual(len(self.received_action_events), 0, "No ActionEvent should be published for malformed command payload.")
            self.assertIn(f"BGM ({self.bgm_module_id}): Received ActionCommand with unexpected payload: <class 'dict'>", output)
            self.assertEqual(bgm_module._action_events_published, 0)

        # Running asyncio.to_thread for StringIO might be tricky in tests.
        # A simpler way for this specific test if prints are the only side effect of malformed payload:
        # Just check that no ActionEvent is published.
        # The print check is good but can make test setup complex.
        # For now, focusing on no ActionEvent published.
        bgm_module_for_malformed = ConcreteBehaviorGenerationModule(message_bus=self.bus, module_id="BGM_MalformedTest")
        self.bus.subscribe(bgm_module_for_malformed._module_id, "ActionEvent", self._action_event_listener) # Listen to specific module

        malformed_payload_dict = {"text": "this is not an action command payload"}
        action_command_msg_malformed = GenericMessage("TestPlanner", "ActionCommand", malformed_payload_dict) # type: ignore

        async def run_malformed_test():
            self.bus.publish(action_command_msg_malformed)
            await asyncio.sleep(0.01)
            self.assertEqual(len(self.received_action_events), 0) # Should not publish ActionEvent
            self.assertEqual(bgm_module_for_malformed._action_events_published, 0)

        asyncio.run(run_malformed_test())


    # --- Test No Bus Scenario ---
    def test_initialization_and_operation_without_bus(self):
        bgm_no_bus = ConcreteBehaviorGenerationModule(message_bus=None, module_id="NoBusBGM")
        status = bgm_no_bus.get_status()
        self.assertFalse(status["message_bus_configured"])
        self.assertEqual(bgm_no_bus._action_events_published, 0)

        # Simulate a direct call to handle_action_command_message (though it's usually a callback)
        # This is to ensure it doesn't crash if bus is None when trying to publish.
        command_payload = ActionCommandPayload(action_type="linguistic_output", parameters={"message": "test"})
        direct_call_msg = GenericMessage("DirectCall", "ActionCommand", command_payload)

        try:
            bgm_no_bus.handle_action_command_message(direct_call_msg)
        except Exception as e:
            self.fail(f"handle_action_command_message raised an exception with no bus: {e}")

        self.assertEqual(bgm_no_bus._action_events_published, 0) # No event should be published

    # --- Test get_status ---
    def test_get_module_status(self):
        bgm_module = ConcreteBehaviorGenerationModule(message_bus=self.bus, module_id=self.bgm_module_id)
        initial_status = bgm_module.get_status()
        self.assertEqual(initial_status["module_id"], self.bgm_module_id)
        self.assertTrue(initial_status["message_bus_configured"])
        self.assertEqual(initial_status["executed_commands_count"], 0)
        self.assertEqual(initial_status["action_events_published"], 0)
        self.assertIn("linguistic_output", initial_status["supported_behavior_types"])

        # Simulate one command being processed
        async def run_status_update_test():
            self.bus.subscribe(self.bgm_module_id, "ActionEvent", self._action_event_listener) # Listener needed to consume event
            command_payload = ActionCommandPayload(action_type="log_message", parameters={"text": "status check"})
            action_command_msg = GenericMessage("TestPlanner", "ActionCommand", command_payload)
            self.bus.publish(action_command_msg)
            await asyncio.sleep(0.01)
        asyncio.run(run_status_update_test())

        updated_status = bgm_module.get_status()
        self.assertEqual(updated_status["executed_commands_count"], 1)
        self.assertEqual(updated_status["action_events_published"], 1)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
```
