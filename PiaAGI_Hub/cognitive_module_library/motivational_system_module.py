import abc
from typing import List, Dict, Any

class MotivationalSystemModule(abc.ABC):
    """
    Abstract base class for motivational system modules.
    """

    @abc.abstractmethod
    def update_drives(self, new_stimuli: Dict[str, Any]) -> None:
        """
        Updates the internal drives or needs based on new stimuli or internal states.

        Args:
            new_stimuli: A dictionary containing new stimuli or internal state changes.
        """
        pass

    @abc.abstractmethod
    def get_goals(self) -> List[Any]: # Assuming goals can be complex objects, not just strings
        """
        Returns a list of current goals, potentially prioritized.

        Returns:
            A list of current goals.
        """
        pass

    @abc.abstractmethod
    def get_motivation_level(self, goal_id: str) -> float:
        """
        Returns the motivation level for a specific goal.

        Args:
            goal_id: The identifier of the goal.

        Returns:
            The motivation level (e.g., a float between 0 and 1).
        """
        pass
