from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseBehaviorGenerationModule(ABC):
    """
    Abstract Base Class for a Behavior Generation Module within the PiaAGI Cognitive Architecture.

    This module is responsible for translating abstract action selections or plans,
    received from the Planning and Decision-Making Module, into concrete, executable
    behaviors. These behaviors can be linguistic (via the Communication Module),
    tool usage, or physical actions if the AGI is embodied.

    Refer to PiaAGI.md Section 4.1.9 (Behavior Generation Module (Action Execution))
    for more context.
    """

    @abstractmethod
    def generate_behavior(self, action_plan: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Translates an abstract action or plan into a concrete, executable behavior specification.

        Args:
            action_plan (Dict[str, Any]): The abstract action or plan from the
                                          Planning and Decision-Making module.
                                          Example: {'action_type': 'communicate',
                                                    'target_agent': 'user',
                                                    'message_content_abstract': {'concept': 'greeting'},
                                                    'constraints': ['formal_tone']}
                                                   {'action_type': 'use_tool',
                                                    'tool_id': 'calculator',
                                                    'parameters': {'expression': '2+2'}}
            context (Dict[str, Any], optional): Additional context that might influence
                                                behavior generation, such as current
                                                emotional state, environmental constraints,
                                                or specific role requirements.

        Returns:
            Dict[str, Any]: A specification of the generated behavior, ready for execution
                            or for an actuator/interface.
                            Example: {'behavior_type': 'linguistic_output',
                                      'content': "Hello, how may I assist you today?",
                                      'target_interface': 'chat_api'}
                                     {'behavior_type': 'api_call',
                                      'endpoint': 'calculator_tool_execute',
                                      'payload': {'expression': '2+2'},
                                      'expected_result_type': 'number'}
        """
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Returns the current status of the Behavior Generation Module.

        Returns:
            Dict[str, Any]: A dictionary describing the module's status.
                            Example: {'active_generation_tasks': 0,
                                      'supported_behavior_types': ['linguistic_output', 'api_call']}
        """
        pass
