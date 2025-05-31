import abc
from typing import List, Dict, Any

class PlanningAndDecisionMakingModule(abc.ABC):
    """
    Abstract base class for planning and decision-making modules.
    """

    @abc.abstractmethod
    def generate_possible_actions(self, current_state: Any, goals: List[Any]) -> List[Any]:
        """
        Generates a list of possible actions based on the current state and goals.

        Args:
            current_state: The current state of the agent or environment.
            goals: A list of current goals.

        Returns:
            A list of possible actions.
        """
        pass

    @abc.abstractmethod
    def evaluate_actions(self, actions: List[Any], current_state: Any, goals: List[Any]) -> Dict[Any, float]: # Action to score
        """
        Evaluates the generated actions, returning a score or preference for each.

        Args:
            actions: A list of actions to evaluate.
            current_state: The current state of the agent or environment.
            goals: A list of current goals.

        Returns:
            A dictionary mapping each action to its evaluation score or preference.
        """
        pass

    @abc.abstractmethod
    def select_action(self, evaluated_actions: Dict[Any, float]) -> Any:
        """
        Selects the best action to take based on their evaluation.

        Args:
            evaluated_actions: A dictionary of actions and their evaluations.

        Returns:
            The selected action.
        """
        pass

    @abc.abstractmethod
    def create_plan(self, goal: Any, current_state: Any) -> List[Any]:
        """
        Creates a sequence of actions (a plan) to achieve a given goal.

        Args:
            goal: The goal to achieve.
            current_state: The current state of the agent or environment.

        Returns:
            A list of actions representing the plan.
        """
        pass
