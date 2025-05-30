from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseTheoryOfMindModule(ABC):
    """
    Abstract Base Class for a Theory of Mind (ToM) / Social Cognition Module
    within the PiaAGI Cognitive Architecture.

    This module is responsible for attributing mental states (e.g., beliefs, desires,
    intentions, emotions, knowledge) to other agents (and potentially to the self),
    and understanding that these can differ from the AGI's own states. It is
    fundamental for advanced social interaction, collaboration, prediction of
    others' behavior, and empathetic communication.

    Refer to PiaAGI.md Sections 3.2.2 (Theory of Mind (ToM) for Socially Aware AGI)
    and 4.1.11 (Theory of Mind (ToM) / Social Cognition Module) for more context.
    """

    @abstractmethod
    def infer_mental_state(self, agent_id: str, observable_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Infers the mental state of a specified agent based on observable data and context.

        Args:
            agent_id (str): The identifier of the agent whose mental state is being inferred.
            observable_data (Dict[str, Any]): Data observed about the agent's behavior,
                                              expressions, utterances, etc.
                                              Example: {'utterance': 'I want that apple.',
                                                        'expression': 'pointing',
                                                        'affective_cues': ['eager_tone']}
            context (Dict[str, Any], optional): Broader context for inference, such as
                                                interaction history, situational factors,
                                                current goals of the observer (AGI),
                                                or known social scripts.
                                                Example: {'interaction_history_summary': 'previously_denied_banana',
                                                          'situational_goal': 'collaborative_task_A'}

        Returns:
            Dict[str, Any]: A dictionary representing the inferred mental state.
                            The structure will depend on the complexity of the ToM model.
                            Example: {'belief_state': {'has_apple': False, 'wants_apple': True},
                                      'desire_state': {'goal': 'obtain_apple', 'strength': 0.9},
                                      'intention_state': {'action': 'request_apple', 'confidence': 0.8},
                                      'emotional_state_inferred': {'type': 'anticipation', 'intensity': 0.7},
                                      'confidence_of_inference': 0.75}
        """
        pass
