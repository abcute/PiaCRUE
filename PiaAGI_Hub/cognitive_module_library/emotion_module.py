import abc
from typing import Dict, Any

class EmotionModule(abc.ABC):
    """
    Abstract base class for emotion modules.
    """

    @abc.abstractmethod
    def update_emotions(self, internal_states: Dict[str, Any], external_events: Dict[str, Any]) -> None:
        """
        Updates the emotional state based on internal cognitive states and external events.

        Args:
            internal_states: A dictionary representing internal cognitive states.
            external_events: A dictionary representing external events or stimuli.
        """
        pass

    @abc.abstractmethod
    def get_emotional_state(self) -> Dict[str, float]: # Assuming emotion intensities are floats
        """
        Returns the current emotional state.

        Returns:
            A dictionary where keys are emotion labels (e.g., "happiness", "sadness")
            and values are their intensities (e.g., float between 0 and 1).
        """
        pass

    @abc.abstractmethod
    def influence_cognition(self, cognitive_processes: Any) -> Any:
        """
        Modifies or influences other cognitive processes based on the current emotional state.

        Args:
            cognitive_processes: The cognitive processes or components to be influenced.
                                 This could be a specific module, a set of parameters, or data.

        Returns:
            The modified cognitive processes or the outcome of the influence.
        """
        pass
