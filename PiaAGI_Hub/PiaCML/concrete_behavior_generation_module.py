from typing import Any, Dict, Optional

try:
    from .base_behavior_generation_module import BaseBehaviorGenerationModule
except ImportError:
    # Fallback for scenarios where the relative import might fail
    from base_behavior_generation_module import BaseBehaviorGenerationModule

class ConcreteBehaviorGenerationModule(BaseBehaviorGenerationModule):
    """
    A basic, concrete implementation of the BaseBehaviorGenerationModule.
    This version translates action plans into simple, structured dictionaries
    representing the behavior to be executed, often by passing through or slightly
    reformatting the input.
    """

    def __init__(self):
        self._supported_behavior_types = ["linguistic_output", "api_call", "log_message"]
        print("ConcreteBehaviorGenerationModule initialized.")

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
