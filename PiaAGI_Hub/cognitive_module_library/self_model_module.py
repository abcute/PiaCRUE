import abc
from typing import Dict, Any, List # Added List for experiences if it's a list of events

class SelfModelModule(abc.ABC):
    """
    Abstract base class for self-model modules.
    """

    @abc.abstractmethod
    def update_self_representation(self, experiences: Any, internal_states: Dict[str, Any]) -> None:
        """
        Updates the agent's internal model of itself based on new experiences and states.

        Args:
            experiences: New experiences, which could be a single event, a list of events,
                         or structured data representing learning episodes.
            internal_states: A dictionary representing the agent's current internal states
                             (e.g., emotional state, cognitive load).
        """
        pass

    @abc.abstractmethod
    def get_self_representation(self) -> Dict[str, Any]:
        """
        Returns the current self-model.

        Returns:
            A dictionary representing the agent's beliefs about its capabilities,
            traits, current states, etc.
        """
        pass

    @abc.abstractmethod
    def get_self_awareness_level(self) -> float:
        """
        Returns a measure of the agent's current level of self-awareness.

        Returns:
            A float representing the level of self-awareness (e.g., between 0 and 1).
        """
        pass

    @abc.abstractmethod
    def predict_own_performance(self, task: Any) -> Any:
        """
        Predicts the agent's own performance or outcome on a given task.

        Args:
            task: A representation of the task for which performance is to be predicted.

        Returns:
            A prediction of performance, which could be a score, a probability of success,
            or expected outcome.
        """
        pass
