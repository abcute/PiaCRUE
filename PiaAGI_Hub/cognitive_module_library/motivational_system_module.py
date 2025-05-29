from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class MotivationalSystemModule(ABC):
    """
    Abstract Base Class for the Motivational System Module in the PiaAGI Cognitive Architecture.

    This module is responsible for managing the AGI's goals, drives, and overall motivation.
    It plays a critical role in selecting and prioritizing goals, influencing decision-making,
    and driving behavior based on both intrinsic and extrinsic factors. It determines "what
    the AGI wants" and "how badly it wants it."

    The motivational system integrates signals from various sources, including physiological
    needs (if any), emotional states, cognitive assessments (e.g., curiosity, competence),
    and external rewards or instructions.

    Refer to PiaAGI.md Sections 3.3 (Motivational Systems and Intrinsic Goals) and
    4.1.6 (Motivational System Module) for more detailed context.
    """

    @abstractmethod
    def update_goals(self, goals_to_update: List[Dict], operation: str = "add") -> None:
        """
        Adds, removes, or modifies goals in the motivational system.

        Goals are typically represented as dictionaries with attributes like 'id',
        'description', 'priority', 'status' (e.g., active, suspended, achieved),
        'type' (e.g., 'intrinsic_curiosity', 'extrinsic_task'), 'criteria_for_satisfaction'.

        Args:
            goals_to_update (List[Dict]): A list of goal objects to add, update, or remove.
                                         For updates, 'id' must be present.
            operation (str): "add", "update", or "remove".
        """
        pass

    @abstractmethod
    def get_active_goals(self, priority_threshold: Optional[float] = None, top_n: Optional[int] = None) -> List[Dict]:
        """
        Retrieves a list of currently active goals, optionally filtered by priority or count.

        Args:
            priority_threshold (Optional[float]): If provided, only goals with priority
                                                  above this threshold are returned.
            top_n (Optional[int]): If provided, returns the top N highest priority goals.

        Returns:
            List[Dict]: A list of active goal objects.
        """
        pass

    @abstractmethod
    def get_goal_status(self, goal_id: str) -> Optional[Dict]:
        """
        Retrieves the current status and details of a specific goal.

        Args:
            goal_id (str): The unique identifier of the goal.

        Returns:
            Optional[Dict]: The goal object if found, otherwise None.
        """
        pass

    @abstractmethod
    def update_motivation_state(self, event_type: str, event_details: Dict) -> None:
        """
        Updates the overall motivational state based on internal or external events.

        This could be triggered by:
        - Changes in internal needs (e.g., 'energy_low', 'information_deficit').
        - Emotional states (e.g., 'fear_detected', 'joy_experienced').
        - Cognitive assessments (e.g., 'novelty_encountered', 'mastery_achieved').
        - External stimuli (e.g., 'reward_received', 'new_task_assigned').

        Args:
            event_type (str): The type of event that occurred.
            event_details (Dict): Specifics about the event.
                                  Example: {'source': 'EmotionModule', 'state': 'curiosity_high'}
                                  Example: {'source': 'Environment', 'reward_value': 10}
        """
        pass

    @abstractmethod
    def get_current_motivation_levels(self) -> Dict[str, float]:
        """
        Returns a snapshot of current key motivational drives and their strengths.

        Examples: {'curiosity': 0.8, 'achievement': 0.6, 'social_affiliation': 0.5, 'safety': 0.9}

        Returns:
            Dict[str, float]: A dictionary mapping drive names to their current intensity (e.g., 0.0 to 1.0).
        """
        pass

    @abstractmethod
    def set_intrinsic_rewards_config(self, config: Dict) -> None:
        """
        Configures parameters for how intrinsic rewards are generated or weighted.

        This might include setting weights for novelty, complexity, learning progress,
        or efficiency in problem-solving.

        Args:
            config (Dict): Configuration parameters.
                           Example: {'novelty_weight': 0.5, 'competence_gain_weight': 0.3}
        """
        pass

    @abstractmethod
    def evaluate_outcome_relevance(self, outcome_details: Dict, relevant_goal_ids: List[str]) -> Dict[str, float]:
        """
        Assesses how a specific outcome (e.g., result of an action) affects the
        motivation associated with one or more goals.

        This is crucial for reinforcement learning and goal adjustment.

        Args:
            outcome_details (Dict): Description of the outcome.
                                    Example: {'action_taken': 'query_db', 'result': 'success', 'info_gained': 5}
            relevant_goal_ids (List[str]): IDs of goals potentially affected by this outcome.

        Returns:
            Dict[str, float]: A dictionary mapping goal_id to a motivational impact score
                              (e.g., positive for progress, negative for setback).
        """
        pass

    @abstractmethod
    def get_status(self) -> Dict:
        """
        Returns the current operational status of the Motivational System Module.

        Could include information like number of active goals, processing load, configuration.

        Returns:
            Dict: Status information.
        """
        pass

if __name__ == '__main__':
    # Conceptual illustration for MotivationalSystemModule

    class ConceptualMotivation(MotivationalSystemModule):
        def __init__(self):
            self.goals = {}
            self.motivation_levels = {"curiosity": 0.7, "task_completion": 0.5}
            self.intrinsic_config = {}
            print("ConceptualMotivation initialized.")

        def update_goals(self, goals_to_update: List[Dict], operation: str = "add") -> None:
            print(f"ConceptualMotivation: Updating goals (operation: {operation}): {goals_to_update}")
            for goal in goals_to_update:
                goal_id = goal.get("id")
                if not goal_id:
                    print(f"  Skipping goal without ID: {goal}")
                    continue
                if operation == "add":
                    self.goals[goal_id] = goal
                    print(f"  Added goal: {goal_id}")
                elif operation == "update" and goal_id in self.goals:
                    self.goals[goal_id].update(goal)
                    print(f"  Updated goal: {goal_id}")
                elif operation == "remove" and goal_id in self.goals:
                    del self.goals[goal_id]
                    print(f"  Removed goal: {goal_id}")

        def get_active_goals(self, priority_threshold: Optional[float] = None, top_n: Optional[int] = None) -> List[Dict]:
            print(f"ConceptualMotivation: Getting active goals (threshold: {priority_threshold}, top_n: {top_n})")
            active = [g for g in self.goals.values() if g.get("status") == "active"]
            if priority_threshold is not None:
                active = [g for g in active if g.get("priority", 0) >= priority_threshold]
            
            active.sort(key=lambda g: g.get("priority", 0), reverse=True)
            
            if top_n is not None:
                active = active[:top_n]
            print(f"  Found active goals: {[g['id'] for g in active]}")
            return active

        def get_goal_status(self, goal_id: str) -> Optional[Dict]:
            print(f"ConceptualMotivation: Getting status for goal: {goal_id}")
            return self.goals.get(goal_id)

        def update_motivation_state(self, event_type: str, event_details: Dict) -> None:
            print(f"ConceptualMotivation: Updating motivation state due to event '{event_type}': {event_details}")
            if event_type == "novelty_encountered" and self.motivation_levels.get("curiosity", 0) < 0.9:
                self.motivation_levels["curiosity"] = min(0.95, self.motivation_levels.get("curiosity", 0) + 0.1)
                print(f"  Curiosity increased to: {self.motivation_levels['curiosity']}")
            elif event_type == "task_assigned":
                self.motivation_levels["task_completion"] = max(0.6, self.motivation_levels.get("task_completion", 0))
                print(f"  Task completion motivation set/kept high: {self.motivation_levels['task_completion']}")


        def get_current_motivation_levels(self) -> Dict[str, float]:
            print(f"ConceptualMotivation: Getting current motivation levels: {self.motivation_levels}")
            return self.motivation_levels

        def set_intrinsic_rewards_config(self, config: Dict) -> None:
            print(f"ConceptualMotivation: Setting intrinsic rewards config: {config}")
            self.intrinsic_config = config

        def evaluate_outcome_relevance(self, outcome_details: Dict, relevant_goal_ids: List[str]) -> Dict[str, float]:
            print(f"ConceptualMotivation: Evaluating outcome relevance: {outcome_details} for goals {relevant_goal_ids}")
            impact = {}
            for goal_id in relevant_goal_ids:
                if goal_id in self.goals:
                    # Simplified logic: positive impact if outcome is success and related to goal type
                    if outcome_details.get("result") == "success":
                        if self.goals[goal_id].get("type") == "knowledge_acquisition" and outcome_details.get("info_gained", 0) > 0:
                            impact[goal_id] = 0.2 # Positive impact
                            print(f"  Positive impact on goal {goal_id}")
                        elif self.goals[goal_id].get("type") == "task_completion_goal" :
                            impact[goal_id] = 0.3
                            self.goals[goal_id]["status"] = "achieved" # Mark as achieved
                            print(f"  Goal {goal_id} achieved!")
                    else:
                        impact[goal_id] = -0.1 # Negative impact for failures
                        print(f"  Negative impact on goal {goal_id}")
            return impact

        def get_status(self) -> Dict:
            return {
                "module_type": "ConceptualMotivation",
                "active_goals_count": len([g for g in self.goals.values() if g.get("status") == "active"]),
                "total_goals_count": len(self.goals),
                "current_drives": self.motivation_levels
            }

    # Conceptual usage:
    motivation_system = ConceptualMotivation()

    # Add goals
    goals_to_add = [
        {"id": "explore_environment", "description": "Explore the current environment for novelty", 
         "priority": 0.8, "status": "active", "type": "intrinsic_curiosity"},
        {"id": "learn_physics", "description": "Understand basic physics simulation", 
         "priority": 0.7, "status": "active", "type": "knowledge_acquisition"},
        {"id": "complete_assigned_task_1", "description": "User assigned task: summarize report",
         "priority": 0.9, "status": "active", "type": "task_completion_goal"}
    ]
    motivation_system.update_goals(goals_to_add, operation="add")
    
    print(f"Initial Status: {motivation_system.get_status()}")

    # Simulate an event
    motivation_system.update_motivation_state("novelty_encountered", {"source": "Perception", "details": "Found a new object"})
    print(f"Motivation Levels: {motivation_system.get_current_motivation_levels()}")

    # Get active goals
    active_goals = motivation_system.get_active_goals(top_n=2)
    print(f"Top 2 Active Goals: {active_goals}")

    # Simulate an outcome
    outcome = {"action_taken": "analyze_data", "result": "success", "info_gained": 10}
    relevance = motivation_system.evaluate_outcome_relevance(outcome, ["learn_physics"])
    print(f"Outcome relevance for 'learn_physics': {relevance}")

    outcome_task = {"action_taken": "summarize_report_action", "result": "success"}
    relevance_task = motivation_system.evaluate_outcome_relevance(outcome_task, ["complete_assigned_task_1"])
    print(f"Outcome relevance for 'complete_assigned_task_1': {relevance_task}")

    print(f"Status after task completion: {motivation_system.get_status()}")
    print(f"Goal 'complete_assigned_task_1' status: {motivation_system.get_goal_status('complete_assigned_task_1')}")

```
