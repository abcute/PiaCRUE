from typing import Any, Dict, Optional, List
import uuid # For module_id generation

try:
    from .base_behavior_generation_module import BaseBehaviorGenerationModule
    from .message_bus import MessageBus
    from .core_messages import GenericMessage, ActionCommandPayload, ActionEventPayload # Added ActionEventPayload
except ImportError:
    print("Warning: Running ConcreteBehaviorGenerationModule with stubbed imports.")
    from base_behavior_generation_module import BaseBehaviorGenerationModule # type: ignore
    try:
        from message_bus import MessageBus # type: ignore
        from core_messages import GenericMessage, ActionCommandPayload, ActionEventPayload # type: ignore
    except ImportError:
        MessageBus = None # type: ignore
        GenericMessage = object # type: ignore
        ActionCommandPayload = object # type: ignore
        ActionEventPayload = object # type: ignore


class ConcreteBehaviorGenerationModule(BaseBehaviorGenerationModule):
    """
    A concrete implementation of the BaseBehaviorGenerationModule.
    Subscribes to ActionCommand messages and publishes ActionEvent messages.
    """

    def __init__(self,
                 message_bus: Optional[MessageBus] = None,
                 module_id: str = f"BehaviorGenerationModule_{str(uuid.uuid4())[:8]}"):
        """
        Initializes the ConcreteBehaviorGenerationModule.

        Args:
            message_bus: An optional instance of MessageBus.
            module_id: A unique identifier for this module instance.
        """
        self._module_id = module_id
        self._message_bus = message_bus
        self._supported_behavior_types = ["linguistic_output", "api_call", "log_message", "conceptual_step"]
        self.executed_commands_log: List[ActionCommandPayload] = []
        self._action_events_published = 0

        bus_status_msg = "not configured"
        if self._message_bus:
            # Ensure ActionCommandPayload and ActionEventPayload are available for type checking and creation
            if GenericMessage and ActionCommandPayload and ActionEventPayload:
                try:
                    self._message_bus.subscribe(
                        module_id=self._module_id,
                        message_type="ActionCommand",
                        callback=self.handle_action_command_message
                    )
                    bus_status_msg = "configured and subscribed to ActionCommand"
                except Exception as e:
                    bus_status_msg = f"configured but FAILED to subscribe to ActionCommand: {e}"
            else:
                bus_status_msg = "configured but core message types (ActionCommandPayload or ActionEventPayload) not available"

        print(f"ConcreteBehaviorGenerationModule '{self._module_id}' initialized. Message bus {bus_status_msg}.")

    def handle_action_command_message(self, message: GenericMessage):
        """
        Handles ActionCommand messages received from the message bus.
        Conceptually "executes" the command and publishes an ActionEvent.
        """
        if not isinstance(message.payload, ActionCommandPayload):
            print(f"BGM ({self._module_id}): Received ActionCommand with unexpected payload: {type(message.payload)}")
            return

        command_payload: ActionCommandPayload = message.payload
        print(f"BGM ({self._module_id}): Received ActionCommand: ID={command_payload.command_id}, Type='{command_payload.action_type}'")
        self.executed_commands_log.append(command_payload)

        status = "FAILURE"
        outcome_message = f"Action {command_payload.action_type} processing failed or type unsupported."

        if command_payload.action_type in self._supported_behavior_types:
            status = "SUCCESS"
            outcome_message = f"Action {command_payload.action_type} processed with status: {status}"
            # Conceptual execution log:
            # print(f"  BGM ({self._module_id}): Executing {command_payload.action_type} with params {command_payload.parameters}")
        else:
            print(f"  BGM ({self._module_id}): ActionType '{command_payload.action_type}' is not supported.")

        outcome_dict: Dict[str, Any] = {"message": outcome_message}
        if command_payload.parameters and "goal_id" in command_payload.parameters:
            outcome_dict["goal_id"] = command_payload.parameters["goal_id"]
            # print(f"  BGM ({self._module_id}): goal_id '{outcome_dict['goal_id']}' included in ActionEvent outcome.")


        if self._message_bus and ActionEventPayload and GenericMessage:
            action_event_payload = ActionEventPayload(
                action_command_id=command_payload.command_id,
                action_type=command_payload.action_type,
                status=status,
                outcome=outcome_dict
            )
            action_event_message = GenericMessage(
                source_module_id=self._module_id,
                message_type="ActionEvent",
                payload=action_event_payload
            )
            self._message_bus.publish(action_event_message)
            self._action_events_published += 1
            print(f"BGM ({self._module_id}): Published ActionEvent for command ID '{command_payload.command_id}', Status: {status}")
        else:
            print(f"BGM ({self._module_id}): MessageBus or ActionEventPayload not available. Cannot publish ActionEvent.")


    def generate_behavior(self, action_plan: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generates a behavior specification based on the action plan.
        For linguistic output, it might expect 'message_content' directly in the action_plan.
        For other types, it largely passes through relevant parts of the action_plan.
        """
        print(f"ConcreteBehaviorGenerationModule: Generating behavior for action plan: {action_plan}")

        action_type = action_plan.get("action_type")
        behavior_spec = {
            "behavior_type": "unknown",
            "details": {},
            "original_plan": action_plan # Include original plan for traceability
        }

        if action_type == "communicate":
            behavior_spec["behavior_type"] = "linguistic_output"
            # Expects that the CommunicationModule (or whatever formulated the abstract message)
            # has placed the final content to be communicated in a known field.
            # For this concrete module, let's assume it's 'final_message_content'.
            # If it's more abstract, this module would do more transformation.
            content = action_plan.get("final_message_content", "Error: No message content specified in plan.")
            behavior_spec["details"] = {
                "content": content,
                "target_interface": action_plan.get("target_interface", "default_chat_interface"),
                "recipient": action_plan.get("target_agent", "unknown_recipient")
            }
        elif action_type == "use_tool":
            behavior_spec["behavior_type"] = "api_call" # Or 'tool_use_command'
            behavior_spec["details"] = {
                "tool_id": action_plan.get("tool_id", "unknown_tool"),
                "parameters": action_plan.get("parameters", {}),
                "expected_result_type": action_plan.get("expected_result_type", "any")
            }
        elif action_type == "log_internal_state":
            behavior_spec["behavior_type"] = "log_message"
            behavior_spec["details"] = {
                "message": action_plan.get("log_content", "Generic log message."),
                "level": action_plan.get("log_level", "INFO")
            }
        else:
            print(f"ConcreteBehaviorGenerationModule: Unknown action_type '{action_type}'. Defaulting to 'unknown' behavior.")
            behavior_spec["details"] = {"error": f"Unsupported action_type: {action_type}"}

        if context: # Merge any relevant context into the details
            behavior_spec["details"]["generation_context"] = context

        print(f"ConcreteBehaviorGenerationModule: Generated behavior spec: {behavior_spec}")
        return behavior_spec

    def get_status(self) -> Dict[str, Any]:
        """Returns the current status of the Behavior Generation Module."""
        return {
            "module_id": self._module_id,
            "module_type": "ConcreteBehaviorGenerationModule (Message Bus Integrated)",
            "message_bus_configured": self._message_bus is not None,
            "supported_behavior_types": list(self._supported_behavior_types),
            "executed_commands_count": len(self.executed_commands_log),
            "action_events_published": self._action_events_published,
        }

if __name__ == '__main__':
    import asyncio
    from datetime import datetime, timezone # For timestamps in ActionCommand

    if not all([MessageBus, GenericMessage, ActionCommandPayload, ActionEventPayload]):
        print("CRITICAL: Core message types or MessageBus not loaded correctly for __main__ test. Exiting.")
        exit(1)

    print("\n--- ConcreteBehaviorGenerationModule __main__ Test ---")

    received_action_events: List[GenericMessage] = []
    def action_event_listener(message: GenericMessage):
        print(f"\n action_event_listener: Received ActionEvent! ID: {message.message_id[:8]}")
        if isinstance(message.payload, ActionEventPayload):
            payload: ActionEventPayload = message.payload
            print(f"  Source: {message.source_module_id}")
            print(f"  Command ID: {payload.action_command_id}")
            print(f"  Action Type: {payload.action_type}, Status: {payload.status}")
            print(f"  Outcome: {payload.outcome}")
            received_action_events.append(message)
        else:
            print(f"  ERROR: Listener received non-ActionEventPayload: {type(message.payload)}")

    async def main_test_flow():
        bus = MessageBus()
        bgm_module_id = "TestBGM001"
        # Note: The BGM module itself subscribes to ActionCommand, so we publish to bus.
        # It then publishes ActionEvent, which our listener will catch.
        bg_module = ConcreteBehaviorGenerationModule(message_bus=bus, module_id=bgm_module_id)

        bus.subscribe(
            module_id="TestActionEventCatchAllListener", # Listener's ID
            message_type="ActionEvent",
            callback=action_event_listener
        )
        print("\nTestActionEventCatchAllListener subscribed to ActionEvent messages.")
        print(bg_module.get_status())


        # 1. Test with a supported action type (and include goal_id)
        print("\n--- Publishing ActionCommand (Supported, with goal_id) ---")
        cmd_payload1 = ActionCommandPayload(
            action_type="linguistic_output",
            parameters={"message": "Hello world", "goal_id": "goal123"},
            priority=0.8
        )
        cmd_msg1 = GenericMessage(source_module_id="TestPlanner", message_type="ActionCommand", payload=cmd_payload1)
        bus.publish(cmd_msg1)
        await asyncio.sleep(0.05) # Allow time for processing and publishing ActionEvent

        assert len(received_action_events) == 1, "ActionEvent for cmd1 not received"
        if received_action_events:
            event1_payload = received_action_events[0].payload
            assert event1_payload.action_command_id == cmd_payload1.command_id
            assert event1_payload.status == "SUCCESS"
            assert event1_payload.outcome.get("goal_id") == "goal123"
            assert "processed with status: SUCCESS" in event1_payload.outcome.get("message", "")
            print("  Listener correctly received SUCCESS ActionEvent for supported command with goal_id.")
        received_action_events.clear()


        # 2. Test with an unsupported action type
        print("\n--- Publishing ActionCommand (Unsupported) ---")
        cmd_payload2 = ActionCommandPayload(action_type="perform_magic_trick", parameters={"object": "hat"})
        cmd_msg2 = GenericMessage(source_module_id="TestPlanner", message_type="ActionCommand", payload=cmd_payload2)
        bus.publish(cmd_msg2)
        await asyncio.sleep(0.05)

        assert len(received_action_events) == 1, "ActionEvent for cmd2 (unsupported) not received"
        if received_action_events:
            event2_payload = received_action_events[0].payload
            assert event2_payload.action_command_id == cmd_payload2.command_id
            assert event2_payload.status == "FAILURE"
            assert "unsupported" in event2_payload.outcome.get("message", "")
            assert "goal_id" not in event2_payload.outcome # No goal_id was sent
            print("  Listener correctly received FAILURE ActionEvent for unsupported command.")
        received_action_events.clear()

        # 3. Test with another supported action, no goal_id
        print("\n--- Publishing ActionCommand (Supported, no goal_id) ---")
        cmd_payload3 = ActionCommandPayload(action_type="log_message", parameters={"text": "System nominal"})
        cmd_msg3 = GenericMessage(source_module_id="TestPlanner", message_type="ActionCommand", payload=cmd_payload3)
        bus.publish(cmd_msg3)
        await asyncio.sleep(0.05)

        assert len(received_action_events) == 1, "ActionEvent for cmd3 not received"
        if received_action_events:
            event3_payload = received_action_events[0].payload
            assert event3_payload.status == "SUCCESS"
            assert "goal_id" not in event3_payload.outcome
            print("  Listener correctly received SUCCESS ActionEvent for supported command without goal_id.")
        received_action_events.clear()


        print("\n--- Final BGM Status ---")
        final_status = bg_module.get_status()
        print(final_status)
        assert final_status["action_events_published"] == 3
        assert final_status["executed_commands_count"] == 3


        print("\n--- ConcreteBehaviorGenerationModule __main__ Test Complete ---")

    try:
        asyncio.run(main_test_flow())
    except RuntimeError as e:
        if " asyncio.run() cannot be called from a running event loop" in str(e):
            print("Skipping asyncio.run() as an event loop is already running (e.g. in Jupyter/IPython).")
        else:
            raise

    # Old __main__ content (kept for reference, but new tests are primary)
    # behavior_module = ConcreteBehaviorGenerationModule()
    # print("\n--- Initial Status ---")
    # print(behavior_module.get_status())
    # print("\n--- Generating Linguistic Behavior ---")
    # linguistic_plan = { ... }
    # ... (rest of old main commented out)
    # print("\nExample Usage Complete.")
