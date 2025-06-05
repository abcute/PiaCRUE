from typing import Any, Dict, Optional, List # Added List

try:
    from .base_behavior_generation_module import BaseBehaviorGenerationModule
    from .message_bus import MessageBus
    from .core_messages import GenericMessage, ActionCommandPayload
except ImportError:
    # Fallback for scenarios where the relative import might fail
    from base_behavior_generation_module import BaseBehaviorGenerationModule
    try:
        from message_bus import MessageBus
        from core_messages import GenericMessage, ActionCommandPayload
    except ImportError:
        MessageBus = None # type: ignore
        GenericMessage = None # type: ignore
        ActionCommandPayload = None # type: ignore


class ConcreteBehaviorGenerationModule(BaseBehaviorGenerationModule):
    """
    A concrete implementation of the BaseBehaviorGenerationModule.
    This version can subscribe to ActionCommand messages from a MessageBus
    and conceptually execute them by logging their details.
    The original `generate_behavior` method can be used as a helper or for direct invocation.
    """

    def __init__(self, message_bus: Optional[MessageBus] = None):
        """
        Initializes the ConcreteBehaviorGenerationModule.

        Args:
            message_bus: An optional instance of MessageBus for subscribing to ActionCommands.
        """
        self._supported_behavior_types = ["linguistic_output", "api_call", "log_message", "conceptual_step"] # Added conceptual_step
        self.message_bus = message_bus
        self.executed_commands_log: List[ActionCommandPayload] = []

        bus_status_msg = "not configured"
        if self.message_bus:
            if GenericMessage and ActionCommandPayload: # Check if imports were successful
                try:
                    self.message_bus.subscribe(
                        module_id="ConcreteBehaviorGenerationModule_01", # Example ID
                        message_type="ActionCommand",
                        callback=self.handle_action_command_message
                    )
                    bus_status_msg = "configured and subscribed to ActionCommand"
                except Exception as e:
                    bus_status_msg = f"configured but FAILED to subscribe to ActionCommand: {e}"
            else:
                bus_status_msg = "configured but core message types for subscription not available"

        print(f"ConcreteBehaviorGenerationModule initialized. Message bus {bus_status_msg}.")

    def handle_action_command_message(self, message: GenericMessage):
        """
        Handles ActionCommand messages received from the message bus.
        Conceptually "executes" the command by logging its details.
        """
        if ActionCommandPayload and isinstance(message.payload, ActionCommandPayload):
            payload: ActionCommandPayload = message.payload
            # print(f"BehaviorModule received ActionCommand: ID={payload.command_id}, Type='{payload.action_type}', Params='{payload.parameters}'") # Optional logging

            # Conceptual execution:
            execution_details = f"Executed Action ID: {payload.command_id}, Type: {payload.action_type}"
            if payload.target_object_or_agent:
                execution_details += f", Target: {payload.target_object_or_agent}"
            execution_details += f", Parameters: {payload.parameters}, Priority: {payload.priority}"
            if payload.expected_outcome_summary:
                execution_details += f", Expected Outcome: {payload.expected_outcome_summary}"

            # For now, just log the "execution" and store the payload for testing
            # print(f"  DETAIL: {execution_details}") # Optional
            self.executed_commands_log.append(payload)

            # Future: This method would translate the ActionCommandPayload
            # into actual interactions with an environment or other systems.
            # It might also publish an "ActionOutcome" or "BehaviorEvent" message.
        else:
            print(f"BehaviorModule received ActionCommand with unexpected payload type: {type(message.payload)}")


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
            'active_generation_tasks': 0, # This basic version doesn't manage async tasks
            'supported_behavior_types': list(self._supported_behavior_types),
            'module_type': 'ConcreteBehaviorGenerationModule'
        }

if __name__ == '__main__':
    behavior_module = ConcreteBehaviorGenerationModule()

    # Initial status
    print("\n--- Initial Status ---")
    print(behavior_module.get_status())

    # Generate linguistic behavior
    print("\n--- Generating Linguistic Behavior ---")
    linguistic_plan = {
        "action_type": "communicate",
        "target_agent": "user_123",
        "final_message_content": "Hello from PiaAGI!",
        "target_interface": "main_chat"
    }
    linguistic_behavior = behavior_module.generate_behavior(linguistic_plan, context={"emotion_hint": "positive"})
    print("Linguistic Behavior Spec:", linguistic_behavior)
    assert linguistic_behavior["behavior_type"] == "linguistic_output"
    assert linguistic_behavior["details"]["content"] == "Hello from PiaAGI!"

    # Generate tool use behavior
    print("\n--- Generating Tool Use Behavior ---")
    tool_plan = {
        "action_type": "use_tool",
        "tool_id": "weather_api",
        "parameters": {"location": "London", "date": "today"},
        "expected_result_type": "json"
    }
    tool_behavior = behavior_module.generate_behavior(tool_plan)
    print("Tool Behavior Spec:", tool_behavior)
    assert tool_behavior["behavior_type"] == "api_call"
    assert tool_behavior["details"]["tool_id"] == "weather_api"

    # Generate log behavior
    print("\n--- Generating Log Behavior ---")
    log_plan = {
        "action_type": "log_internal_state",
        "log_content": "Reached milestone X in planning.",
        "log_level": "DEBUG"
    }
    log_behavior = behavior_module.generate_behavior(log_plan)
    print("Log Behavior Spec:", log_behavior)
    assert log_behavior["behavior_type"] == "log_message"
    assert log_behavior["details"]["level"] == "DEBUG"

    # Generate unknown behavior
    print("\n--- Generating Unknown Behavior ---")
    unknown_plan = {"action_type": "fly_to_moon"}
    unknown_behavior = behavior_module.generate_behavior(unknown_plan)
    print("Unknown Behavior Spec:", unknown_behavior)
    assert unknown_behavior["behavior_type"] == "unknown"

    # Final status
    print("\n--- Final Status ---")
    print(behavior_module.get_status())

    print("\nExample Usage Complete.")
