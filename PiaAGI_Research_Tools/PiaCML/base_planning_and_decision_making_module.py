import abc
from typing import List, Dict, Any, Optional

class BasePlanningAndDecisionMakingModule(abc.ABC):
    """
    Abstract base class for planning and decision-making modules.
    This module is responsible for generating plans to achieve goals,
    evaluating these plans, and selecting the most appropriate one for execution.
    It considers the current world state, agent's goals, and self-model constraints.
    """

    @abc.abstractmethod
    def generate_possible_actions(self, current_state: Any, goals: List[Any]) -> List[Any]:
        """
        Generates a list of possible actions based on the current state and goals.
        These actions are typically discrete steps or options available to the agent.

        Args:
            current_state: The current state of the agent or environment.
            goals: A list of current goals guiding action generation.

        Returns:
            A list of possible actions. Each action can be represented in various ways,
            depending on the specific planning approach (e.g., a string, a dictionary).
        """
        pass

    @abc.abstractmethod
    def create_plan(self, goal: Dict[str, Any], world_model_context: Dict[str, Any], self_model_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Creates a sequence of actions (a plan) to achieve a given goal.
        The plan is constructed considering the world model and self-model.

        Args:
            goal: A dictionary describing the goal to achieve.
                  Example: {'type': 'achieve_state', 'desired_state': {'location': 'kitchen'}}
            world_model_context: Information from the World Model relevant to planning.
                                 Example: {'map_data': ..., 'object_states': ...}
            self_model_context: Information from the Self-Model relevant to planning.
                                Example: {'agent_capabilities': [...], 'ethical_constraints': [...]}

        Returns:
            A list of dictionaries, where each dictionary represents an action or step in the plan.
            Example: [{'action_type': 'navigate', 'target': 'kitchen'}, {'action_type': 'find', 'object': 'apple'}]
            Returns an empty list if no plan can be created.
        """
        pass

    @abc.abstractmethod
    def evaluate_plan(self, plan: Dict[str, Any], world_model_context: Dict[str, Any], self_model_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates a single plan based on various criteria.
        Criteria can include feasibility, cost, expected utility, alignment with ethical constraints, etc.

        Args:
            plan: A dictionary representing the plan to be evaluated. (Note: The subtask implies a single plan dict,
                  but typically a plan is a list of actions. Assuming 'plan' here is one such list of actions
                  or a dictionary that encapsulates a plan). For consistency with `select_plan` which takes
                  a list of *evaluated_plans* (implying each plan was evaluated), this method should take one plan
                  (represented as List[Dict[str,Any]] if it's a sequence of actions) and return its evaluation.
                  However, the type hint is Dict[str, Any]. Let's assume a plan can be a dict for now.
                  Example: {'id': 'plan_A', 'steps': [...], 'estimated_cost': 10, 'expected_utility': 0.8}
            world_model_context: Information from the World Model.
            self_model_context: Information from the Self-Model.

        Returns:
            A dictionary containing the evaluation of the plan.
            Example: {'plan_id': 'plan_A', 'feasibility_score': 0.9, 'cost_score': 0.7, 'utility_score': 0.8, 'overall_score': 0.85}
        """
        pass

    @abc.abstractmethod
    def select_plan(self, evaluated_plans: List[Dict[str, Any]], selection_criteria: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Selects the best plan from a list of evaluated plans.

        Args:
            evaluated_plans: A list of dictionaries, where each dictionary is an output from `evaluate_plan`.
            selection_criteria (Optional[Dict[str, Any]]): Criteria to guide selection,
                e.g., prioritizing utility over cost, or specific constraints.
                Example: {'prioritize': 'utility_score', 'minimum_feasibility': 0.7}

        Returns:
            The selected plan's evaluation dictionary, or None if no suitable plan is found.
        """
        pass
