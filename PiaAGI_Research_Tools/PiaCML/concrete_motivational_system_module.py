from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
import time
import uuid # For module_id generation

try:
    from .motivational_system_module import MotivationalSystemModule # Corrected import
    from .message_bus import MessageBus
    from .core_messages import GenericMessage, GoalUpdatePayload, ActionEventPayload, EmotionalStateChangePayload # Added ActionEventPayload & EmotionalStateChangePayload
except ImportError:
    print("Warning: Running ConcreteMotivationalSystemModule with stubbed imports.")
    class MotivationalSystemModule: # Corrected stub class name
        def manage_goals(self, action: str, goal_data: Optional[Dict[str, Any]] = None) -> Any: pass
        def get_active_goals(self, N: int = 0, min_priority: float = 0.0) -> List[Dict[str, Any]]: return []
        def update_motivation_state(self, new_state_info: Dict[str, Any]) -> bool: return False

    try:
        from message_bus import MessageBus # type: ignore
        from core_messages import GenericMessage, GoalUpdatePayload, ActionEventPayload, EmotionalStateChangePayload # type: ignore
    except ImportError:
        MessageBus = None # type: ignore
        GenericMessage = object # type: ignore # So isinstance checks don't fail immediately
        GoalUpdatePayload = object # type: ignore
        ActionEventPayload = object # type: ignore
        EmotionalStateChangePayload = object # type: ignore


@dataclass
class Goal:
    id: str
    description: str
    type: str  # e.g., "EXTRINSIC_TASK", "INTRINSIC_CURIOSITY", "INTRINSIC_COMPETENCE"
    priority: float  # Higher values mean higher priority
    status: str  # e.g., "PENDING", "ACTIVE", "ACHIEVED", "FAILED", "BLOCKED"
    creation_timestamp: float = field(default_factory=time.time)
    source_trigger: Optional[Dict[str, Any]] = None # Describes what triggered the goal
    parent_id: Optional[str] = None
    # sub_goals: List[str] = field(default_factory=list) # Example for future extension

    # Fields for Competence Goals
    target_skill_id: Optional[str] = None
    target_task_domain: Optional[str] = None
    competence_details: Optional[Dict[str, Any]] = None # e.g., {"current_proficiency": 0.3, "target_proficiency": 0.8}

class ConcreteMotivationalSystemModule(MotivationalSystemModule): # Corrected base class
    """
    A concrete implementation of the BaseMotivationalSystemModule using a structured Goal dataclass.
    Manages a list of goals and includes basic mechanisms for intrinsic motivation (curiosity).
    Can publish GoalUpdate messages to a MessageBus and react to ActionEvents.
    """

    def __init__(self,
                 message_bus: Optional[MessageBus] = None,
                 module_id: str = f"ConcreteMotivationalSystemModule_{str(uuid.uuid4())[:8]}"):
        """
        Initializes the ConcreteMotivationalSystemModule.

        Args:
            message_bus: An optional instance of MessageBus for publishing goal updates
                         and receiving action events.
            module_id: A unique identifier for this module instance.
        """
        self.goals: List[Goal] = []
        self.next_goal_id: int = 0
        self._message_bus = message_bus
        self._module_id = module_id
        self._log: List[str] = [] # New log list
        self._last_emotional_state: Optional[EmotionalStateChangePayload] = None
        bus_status = "configured" if self._message_bus else "not configured"

        subscriptions_log = []
        if self._message_bus:
            self._message_bus.subscribe(
                module_id=self._module_id,
                message_type="ActionEvent",
                callback=self._handle_action_event
            )
            subscriptions_log.append("ActionEvent")

            self._message_bus.subscribe(
                module_id=self._module_id,
                message_type="EmotionalStateChange",
                callback=self._handle_emotional_state_change
            )
            subscriptions_log.append("EmotionalStateChange")

            # Conceptual: Future subscriptions for advanced curiosity triggers
            # self._message_bus.subscribe(module_id=self._module_id, message_type="PerceptData", callback=self._handle_percept_for_curiosity)
            # self._message_bus.subscribe(module_id=self._module_id, message_type="WorldModelPredictionError", callback=self._handle_prediction_error_for_curiosity)
            # self._message_bus.subscribe(module_id=self._module_id, message_type="SelfModelKnowledgeGap", callback=self._handle_knowledge_gap_for_curiosity)

        self._log_message(f"ConcreteMotivationalSystemModule '{self._module_id}' initialized. Message bus {bus_status}. Subscribed to: {', '.join(subscriptions_log) if subscriptions_log else 'None'}.")

    def _log_message(self, message: str):
        """Helper method for internal logging."""
        log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())} [{self._module_id}]: {message}"
        self._log.append(log_entry)
        # print(log_entry) # Optional: for real-time console monitoring


    def _generate_goal_id(self) -> str:
        """Generates a unique goal ID."""
        gid = f"goal_{self.next_goal_id}"
        self.next_goal_id += 1
        return gid

    def add_goal(self, description: str, goal_type: str, initial_priority: float,
                 source_trigger: Optional[Dict[str, Any]] = None,
                 parent_id: Optional[str] = None,
                 initial_status: str = "PENDING") -> str:
        """
        Adds a new goal to the system.

        Args:
            description: Textual description of the goal.
            goal_type: Type of goal (e.g., "EXTRINSIC_TASK", "INTRINSIC_CURIOSITY").
            initial_priority: Priority score (higher is more important).
            source_trigger: Optional dictionary describing what triggered the goal.
            parent_id: Optional ID of a parent goal.
            initial_status: Initial status of the goal, defaults to "PENDING".

        Returns:
            The ID of the newly created goal.
        """
        new_id = self._generate_goal_id()
        new_goal = Goal(
            id=new_id,
            description=description,
            type=goal_type,
            priority=initial_priority,
            status=initial_status,
            source_trigger=source_trigger,
            parent_id=parent_id
        )
        self.goals.append(new_goal)
        self._log_message(f"Added goal '{new_id}': {description} (Priority: {initial_priority}, Status: {new_goal.status}, Type: {goal_type})")

        if self._message_bus and GenericMessage and GoalUpdatePayload:
            payload = GoalUpdatePayload(
                goal_id=new_goal.id,
                goal_description=new_goal.description,
                priority=new_goal.priority,
                status=new_goal.status,
                originator=new_goal.source_trigger.get("originator", new_goal.type) if new_goal.source_trigger else new_goal.type,
                criteria_for_completion=getattr(new_goal, 'criteria_for_completion', None),
                associated_rewards_penalties=getattr(new_goal, 'associated_rewards_penalties', None),
                deadline=getattr(new_goal, 'deadline', None),
                parent_goal_id=new_goal.parent_id
            )
            goal_update_message = GenericMessage(
                source_module_id=self._module_id,
                message_type="GoalUpdate",
                payload=payload
            )
            self._message_bus.publish(goal_update_message)
            self._log_message(f"Published GoalUpdate for new goal '{new_id}'.")

        return new_id

    def get_goal(self, goal_id: str) -> Optional[Goal]:
        """Retrieves a goal by its ID."""
        for goal in self.goals:
            if goal.id == goal_id:
                return goal
        return None

    def update_goal_status(self, goal_id: str, new_status: str) -> bool:
        """Updates the status of an existing goal."""
        goal = self.get_goal(goal_id)
        if goal:
            old_status = goal.status
            goal.status = new_status
            self._log_message(f"Updated status of goal '{goal_id}' from '{old_status}' to '{new_status}'.")

            if self._message_bus and GenericMessage and GoalUpdatePayload:
                payload = GoalUpdatePayload(
                    goal_id=goal.id,
                    goal_description=goal.description,
                    priority=goal.priority,
                    status=goal.status,
                    originator=goal.source_trigger.get("originator", goal.type) if goal.source_trigger else goal.type,
                    criteria_for_completion=getattr(goal, 'criteria_for_completion', None),
                    associated_rewards_penalties=getattr(goal, 'associated_rewards_penalties', None),
                    deadline=getattr(goal, 'deadline', None),
                    parent_goal_id=goal.parent_id
                )
                goal_update_message = GenericMessage(
                    source_module_id=self._module_id,
                    message_type="GoalUpdate",
                    payload=payload
                )
                self._message_bus.publish(goal_update_message)
                self._log_message(f"Published GoalUpdate for status change of goal '{goal_id}'.")
            return True
        self._log_message(f"Goal '{goal_id}' not found for status update.")
        return False

    def update_goal_priority(self, goal_id: str, new_priority: float) -> bool:
        """Updates the priority of an existing goal and publishes an update."""
        goal = self.get_goal(goal_id)
        if goal:
            old_priority = goal.priority
            goal.priority = new_priority
            self._log_message(f"Updated priority of goal '{goal_id}' from {old_priority:.2f} to {new_priority:.2f}.")

            if self._message_bus and GenericMessage and GoalUpdatePayload:
                payload = GoalUpdatePayload(
                    goal_id=goal.id,
                    goal_description=goal.description,
                    priority=goal.priority,
                    status=goal.status,
                    originator=goal.source_trigger.get("originator", goal.type) if goal.source_trigger else goal.type,
                    criteria_for_completion=getattr(goal, 'criteria_for_completion', None),
                    associated_rewards_penalties=getattr(goal, 'associated_rewards_penalties', None),
                    deadline=getattr(goal, 'deadline', None),
                    parent_goal_id=goal.parent_id
                )
                goal_update_message = GenericMessage(
                    source_module_id=self._module_id,
                    message_type="GoalUpdate",
                    payload=payload
                )
                self._message_bus.publish(goal_update_message)
                self._log_message(f"Published GoalUpdate for priority change of goal '{goal_id}'.")
            return True
        self._log_message(f"Goal '{goal_id}' not found for priority update.")
        return False

    def get_active_goals(self, return_with_priority_scores: bool = False) -> Union[List[Goal], List[tuple[float, Goal]]]:
        """
        Returns a list of active/pending goals, sorted by dynamic priority.
        The Goal.priority field itself is the base/initial priority.

        Args:
            return_with_priority_scores: If True, returns list of (dynamic_priority, goal) tuples.
                                         Otherwise, returns list of Goal objects.
        Returns:
            List of Goal objects or List of (dynamic_priority, Goal) tuples, sorted by dynamic priority (descending).
        """
        active_statuses = {"PENDING", "ACTIVE"}
        relevant_goals = [g for g in self.goals if g.status in active_statuses]

        if not relevant_goals:
            return []

        goals_with_dynamic_priority: List[tuple[float, Goal]] = []
        # Create a stable list of goals to pass for context to _calculate_dynamic_priority
        # This avoids issues if _calculate_dynamic_priority itself modifies the list of goals (it shouldn't)
        all_current_active_pending_goals = list(relevant_goals)

        for goal in relevant_goals:
            # The dynamic priority is scaled 0-1. We can scale it up if needed for comparison with old system.
            # For sorting, the 0-1 scale is fine.
            # The operational_priority (0-10) was logged in _calculate_dynamic_priority,
            # but the returned normalized_priority (0-1) is used for sorting here.
            dyn_prio_normalized = self._calculate_dynamic_priority(goal, all_current_active_pending_goals, self._last_emotional_state)
            goals_with_dynamic_priority.append((dyn_prio_normalized, goal))

        # Sort by dynamic priority (the first element of the tuple), descending
        goals_with_dynamic_priority.sort(key=lambda x: x[0], reverse=True)

        # Log top few for debugging priority calculation
        if goals_with_dynamic_priority:
            self._log_message(f"Dynamically prioritized goals (Top 3 - NormDynP, ID, Type, BasePrioField):")
            for dyn_prio, goal_obj in goals_with_dynamic_priority[:3]:
                 self._log_message(f"  - {dyn_prio:.3f}: {goal_obj.id} ({goal_obj.type}, BasePrioField: {goal_obj.priority:.2f})")

        if return_with_priority_scores:
            return goals_with_dynamic_priority
        else:
            return [goal for dyn_prio, goal in goals_with_dynamic_priority] # Return only the Goal objects, sorted

    def assess_curiosity_triggers(self,
                                 knowledge_map_snapshot: Optional[Dict[str, Dict[str, Any]]] = None,
                                 world_event: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Assesses potential curiosity triggers from knowledge gaps or novel world events
        and generates intrinsic curiosity goals.

        Args:
            knowledge_map_snapshot: Snapshot of knowledge concepts and their confidence.
                                    e.g., `{"concept_X": {"confidence": 0.3, "last_explored_ts": ...}}`
            world_event: A dictionary describing a novel event.
                         e.g., `{"type": "NOVEL_STIMULUS", "id": "obj_123", "novelty_score": 0.9}`

        Returns:
            A list of IDs of newly created curiosity goals.
        """
        new_curiosity_goal_ids: List[str] = []
        active_goals = self.get_active_goals() # For relevance calculation
        curiosity_threshold = 0.3 # Configurable threshold

        # Trigger 1: Novel Stimulus from world_event
        # Expected world_event for NOVEL_STIMULUS:
        # {"type": "NOVEL_STIMULUS", "id": "stimulus_xyz", "novelty_score": 0.8, "complexity_score": 0.6, "last_encountered_ts": ...}
        if world_event and world_event.get("type") == "NOVEL_STIMULUS":
            trigger_data = world_event.copy()
            intensity = self._calculate_curiosity_intensity("NOVEL_STIMULUS", trigger_data, active_goals)
            self._log_message(f"Novel stimulus '{trigger_data.get('id')}' assessed for curiosity. Calculated intensity: {intensity:.2f}")
            if intensity > curiosity_threshold:
                desc = f"Investigate novel stimulus: {trigger_data.get('id', 'N/A')} (Novelty: {trigger_data.get('novelty_score',0):.2f}, Complexity: {trigger_data.get('complexity_score',0):.2f}, Calculated Intensity: {intensity:.2f})"
                source_trigger_details = {
                    "trigger_type": "NOVEL_STIMULUS",
                    "stimulus_id": trigger_data.get('id'), # Original stimulus ID
                    "novelty_score": trigger_data.get("novelty_score", 0.0), # Store actual value used
                    "complexity_score": trigger_data.get("complexity_score", 0.0), # Store actual value used
                    "calculated_intensity": intensity # Store the final calculated intensity for this trigger
                }
                # The initial_priority of the goal is derived from the calculated intensity.
                # Multiplying by 10.0 is a conceptual scaling to fit a 0-10 priority range if other goals use that,
                # but the normalized intensity (0-1) itself is the core driver.
                goal_id = self.add_goal(
                    description=desc,
                    goal_type="INTRINSIC_CURIOSITY",
                    initial_priority=intensity * 10.0, # Scale intensity to a broader priority range
                    source_trigger=source_trigger_details
                )
                new_curiosity_goal_ids.append(goal_id)

        # Trigger 2: Prediction Error from world_event (conceptual)
        # Expected world_event for PREDICTION_ERROR:
        # {"type": "PREDICTION_ERROR", "source_model": "WorldModel", "error_magnitude": 0.7, "details": "{...}", "last_encountered_ts": ...}
        if world_event and world_event.get("type") == "PREDICTION_ERROR":
            trigger_data = world_event.copy()
            intensity = self._calculate_curiosity_intensity("PREDICTION_ERROR", trigger_data, active_goals)
            self._log_message(f"Prediction error from '{trigger_data.get('source_model')}' assessed for curiosity. Calculated intensity: {intensity:.2f}")
            if intensity > curiosity_threshold:
                desc = f"Investigate prediction error from {trigger_data.get('source_model')} (ErrorMag: {trigger_data.get('error_magnitude',0):.2f}, Calculated Intensity: {intensity:.2f})"
                source_trigger_details = {
                    "trigger_type": "PREDICTION_ERROR",
                    "source_model": trigger_data.get('source_model'),
                    "error_magnitude": trigger_data.get("error_magnitude", 0.0), # Store actual value used
                    "details": trigger_data.get('details'), # Any additional details about the error
                    "calculated_intensity": intensity # Store the final calculated intensity
                }
                goal_id = self.add_goal(
                    description=desc,
                    goal_type="INTRINSIC_CURIOSITY",
                    initial_priority=intensity * 10.0, # Scale intensity
                    source_trigger=source_trigger_details
                )
                new_curiosity_goal_ids.append(goal_id)

        # Trigger 3: Knowledge Gap from knowledge_map_snapshot
        # Expected knowledge_map_snapshot item:
        # {"concept_id": "concept_X", "confidence": 0.3, "understanding_level": 0.2, "groundedness_score": 0.4, "last_explored_ts": ...}
        if knowledge_map_snapshot:
            for concept_id, data in knowledge_map_snapshot.items():
                trigger_data = data.copy()
                trigger_data["concept_id"] = concept_id # Ensure concept_id is in trigger_data

                # Avoid creating new goal if an active one for this concept already exists
                existing_goal_for_concept = any(
                    g.type == "INTRINSIC_CURIOSITY" and
                    g.source_trigger and g.source_trigger.get("trigger_type") == "KNOWLEDGE_GAP" and
                    g.source_trigger.get("concept_id") == concept_id and
                    g.status in ["PENDING", "ACTIVE"]
                    for g in self.goals
                )
                if existing_goal_for_concept:
                    self._log_message(f"Skipping knowledge gap goal for '{concept_id}', active one already exists.")
                    continue

                intensity = self._calculate_curiosity_intensity("KNOWLEDGE_GAP", trigger_data, active_goals)
                self._log_message(f"Knowledge gap for concept '{concept_id}' assessed for curiosity. Confidence: {data.get('confidence', 1.0):.2f}. Calculated intensity: {intensity:.2f}")
                if intensity > curiosity_threshold:
                desc = f"Explore knowledge gap for concept: {concept_id} (Current Confidence: {data.get('confidence',0):.2f}, Calculated Intensity: {intensity:.2f})"
                    source_trigger_details = {
                        "trigger_type": "KNOWLEDGE_GAP",
                        "concept_id": concept_id,
                    "current_confidence": data.get('confidence', 1.0), # Store actual confidence value used
                    "current_understanding": data.get('understanding_level', 0.0), # Store actual understanding if available
                    "calculated_intensity": intensity # Store the final calculated intensity
                    }
                goal_id = self.add_goal(
                    description=desc,
                    goal_type="INTRINSIC_CURIOSITY",
                    initial_priority=intensity * 10.0, # Scale intensity
                    source_trigger=source_trigger_details
                )
                    new_curiosity_goal_ids.append(goal_id)

        return new_curiosity_goal_ids

    def _calculate_curiosity_intensity(self, trigger_type: str, trigger_data: Dict, active_goals: List[Goal]) -> float:
        """
        Calculates the intensity of a curiosity drive based on the trigger type and its data.
        The intensity is a normalized value between 0.0 and 1.0.

        Args:
            trigger_type: The type of event that triggered curiosity (e.g., "NOVEL_STIMULUS", "PREDICTION_ERROR", "KNOWLEDGE_GAP").
            trigger_data: A dictionary containing specific details about the trigger.
                          - For "NOVEL_STIMULUS": expects "novelty_score" (0-1), "complexity_score" (0-1).
                          - For "PREDICTION_ERROR": expects "error_magnitude" (0-1).
                          - For "KNOWLEDGE_GAP": expects "confidence" (0-1, where low confidence means high uncertainty).
            active_goals: A list of currently active goals, used for assessing relevance (conceptual).

        Returns:
            A float representing the calculated curiosity intensity (0.0 to 1.0).
        """
        # Conceptual weights: These are placeholders and in a full implementation,
        # they should be configurable, learned, or derived from a more complex cognitive model.
        w_novelty = 0.4             # Weight for the novelty of a stimulus.
        w_complexity = 0.2          # Weight for the complexity of a stimulus.
        w_error_magnitude = 0.5     # Weight for the magnitude of a prediction error.
        w_uncertainty = 0.6         # Weight for uncertainty (1 - confidence) in a knowledge gap.
        w_relevance_to_goals = 0.3  # Weight for how relevant the trigger is to active goals.

        base_intensity = 0.0

        if trigger_type == "NOVEL_STIMULUS":
            novelty = trigger_data.get("novelty_score", 0.0)
            complexity = trigger_data.get("complexity_score", 0.0)
            # Formula: Weighted sum of novelty and complexity.
            base_intensity = (w_novelty * novelty) + (w_complexity * complexity)
            self._log_message(f"Curiosity (NovelStimulus): novelty={novelty:.2f}, complexity={complexity:.2f} -> base_intensity={base_intensity:.2f}")
        elif trigger_type == "PREDICTION_ERROR":
            error_mag = trigger_data.get("error_magnitude", 0.0)
            # Formula: Intensity is proportional to the error magnitude.
            base_intensity = w_error_magnitude * error_mag
            self._log_message(f"Curiosity (PredictionError): error_mag={error_mag:.2f} -> base_intensity={base_intensity:.2f}")
        elif trigger_type == "KNOWLEDGE_GAP":
            confidence = trigger_data.get("confidence", 1.0)  # Default to high confidence (low uncertainty) if not specified.
            uncertainty = 1.0 - confidence
            # Formula: Intensity is proportional to the uncertainty.
            base_intensity = w_uncertainty * uncertainty
            self._log_message(f"Curiosity (KnowledgeGap): confidence={confidence:.2f}, uncertainty={uncertainty:.2f} -> base_intensity={base_intensity:.2f}")
        else:
            self._log_message(f"Warning: Unknown curiosity trigger_type: {trigger_type}. Base intensity remains 0.")


        # Conceptual Modulators (currently placeholders):
        # 1. Relevance to Active Goals:
        #    If the curious item is relevant to current tasks, curiosity might be amplified.
        #    This would require a function to calculate `relevance_score` based on `trigger_data` and `active_goals`.
        relevance_score = 0.1  # Placeholder: Assume low default relevance.
        # Example: intensity = base_intensity * (1 + w_relevance_to_goals * relevance_score)
        # For now, this is a conceptual step and not directly applied to keep the current calculation simple.
        # self._log_message(f"Curiosity: relevance_score={relevance_score:.2f} (conceptual).")

        # 2. Recency Factor:
        #    More recent triggers or less recently explored items might be more curiosity-inducing.
        #    This would require tracking exploration history and timestamps.
        recency_factor = 1.0  # Placeholder: Assume neutral recency.
        # Example: intensity = intensity * recency_factor
        # For now, this is a conceptual step.
        # self._log_message(f"Curiosity: recency_factor={recency_factor:.2f} (conceptual).")

        # Apply conceptual modulators if they were fully implemented:
        # For now, we use the base_intensity and a simplified relevance application as in the original.
        # The original code had: intensity *= (1 + w_relevance_to_goals * relevance_score)
        # Let's keep that specific line for consistency with the previous version's direct effect.
        final_intensity = base_intensity * (1 + w_relevance_to_goals * relevance_score)
        self._log_message(f"Curiosity: base_intensity={base_intensity:.2f}, relevance_factor={(1 + w_relevance_to_goals * relevance_score):.2f} -> final_intensity_before_clamp={final_intensity:.2f}")

        # Ensure final intensity is clamped between 0.0 and 1.0.
        clamped_intensity = max(0.0, min(1.0, final_intensity))
        if final_intensity != clamped_intensity:
            self._log_message(f"Curiosity: Intensity clamped from {final_intensity:.2f} to {clamped_intensity:.2f}.")

        return clamped_intensity

    def _calculate_competence_drive_intensity(self, skill_id: str, skill_data: Dict, active_goals: List[Goal]) -> float:
        """
        Calculates the intensity of the competence drive for a given skill.
        The intensity is a normalized value between 0.0 and 1.0.

        Args:
            skill_id: The ID of the skill being assessed.
            skill_data: A dictionary containing details about the skill.
                        Expected keys:
                        - "proficiency": Current proficiency level (0.0 to 1.0).
                        - "importance": Importance of the skill (0.0 to 1.0), potentially goal-related.
                        - "target_proficiency": Desired proficiency level (0.0 to 1.0, optional, defaults to 1.0).
                        - "success_rate_trend": (Conceptual) Trend of success rate (-1 to 1, optional).
                        - "perceived_learnability": (Conceptual) Agent's belief about ease of learning (0-1, optional).
            active_goals: A list of currently active goals (conceptual, for future use in importance calculation).

        Returns:
            A float representing the calculated competence drive intensity (0.0 to 1.0).
        """
        # Conceptual weights: These are placeholders and in a full implementation,
        # they should be configurable, learned, or derived from a more complex cognitive model.
        w_gap = 0.6                 # Weight for the proficiency gap.
        w_importance = 0.4          # Weight for the skill's importance.
        # Conceptual modulator weights (currently not directly applied in the final calculation below but kept for clarity):
        w_success_trend = 0.1       # Weight for the trend of success rate with the skill.
        w_learnability = 0.2        # Weight for the perceived learnability of the skill.

        current_proficiency = skill_data.get("proficiency", 0.0)
        target_proficiency = skill_data.get("target_proficiency", 1.0)  # Default target is mastery.
        importance = skill_data.get("importance", 0.5)  # Default importance if not specified.

        # Calculate the gap between target and current proficiency.
        proficiency_gap = max(0.0, target_proficiency - current_proficiency)

        # Base formula: Weighted sum of proficiency gap and importance.
        base_intensity = (w_gap * proficiency_gap) + (w_importance * importance)
        self._log_message(f"Competence (Skill: {skill_id}): proficiency={current_proficiency:.2f}, target={target_proficiency:.2f}, importance={importance:.2f} -> proficiency_gap={proficiency_gap:.2f}, base_intensity={base_intensity:.2f}")

        # Conceptual Modulators (currently placeholders, not directly altering `base_intensity`):
        # 1. Success Rate Trend:
        #    If the agent is already improving (positive trend), the urgency might be slightly lower.
        #    If declining (negative trend), urgency might be higher.
        #    This would require data from a skill model or LTM.
        success_rate_trend = skill_data.get("success_rate_trend", 0.0) # Placeholder value.
        # Example conceptual application: intensity_modifier_trend = - (w_success_trend * success_rate_trend)
        # self._log_message(f"Competence: success_rate_trend={success_rate_trend:.2f} (conceptual).")


        # 2. Perceived Learnability:
        #    If a skill is perceived as easier to learn, the drive to engage might be higher (or lower if too trivial).
        #    If perceived very hard, it might reduce motivation if not coupled with high importance/reward.
        #    This would require input from a self-model or learning module.
        perceived_learnability = skill_data.get("perceived_learnability", 0.5) # Placeholder: neutral learnability.
        # Example conceptual application: intensity_modifier_learnability = w_learnability * (perceived_learnability - 0.5)
        # self._log_message(f"Competence: perceived_learnability={perceived_learnability:.2f} (conceptual).")

        # For now, the final intensity is the base_intensity.
        # In a more complex model, these conceptual modulators would be integrated.
        final_intensity = base_intensity
        self._log_message(f"Competence (Skill: {skill_id}): final_intensity_before_clamp={final_intensity:.2f} (modulators are conceptual).")

        # Ensure final intensity is clamped between 0.0 and 1.0.
        clamped_intensity = max(0.0, min(1.0, final_intensity))
        if final_intensity != clamped_intensity:
            self._log_message(f"Competence: Intensity clamped from {final_intensity:.2f} to {clamped_intensity:.2f}.")

        return clamped_intensity

    def assess_competence_opportunities(self, capability_inventory_snapshot: Dict[str, Dict[str, Any]], active_goals: List[Goal]) -> List[str]:
        """
        Assesses capability inventory for opportunities to generate competence goals.
        capability_inventory_snapshot: {"skill_id": {"proficiency_level": 0.4, "importance_for_goals": 0.8, "target_proficiency_override": 0.9 (optional)}}
        """
        new_competence_goal_ids: List[str] = []
        competence_threshold = 0.35 # Configurable threshold for generating a goal

        if not capability_inventory_snapshot:
            return new_competence_goal_ids

        for skill_id, skill_data_snapshot in capability_inventory_snapshot.items():
            # Map snapshot keys to keys expected by _calculate_competence_drive_intensity
            skill_data_for_calc = {
                "proficiency": skill_data_snapshot.get("proficiency_level", 0.0),
                "importance": skill_data_snapshot.get("importance_for_goals", 0.5), # Conceptual importance
                "target_proficiency": skill_data_snapshot.get("target_proficiency_override") # Optional override
            }

            intensity = self._calculate_competence_drive_intensity(skill_id, skill_data_for_calc, active_goals)
            self._log_message(f"Competence opportunity for skill '{skill_id}' assessed. Prof: {skill_data_for_calc['proficiency']:.2f}, Importance: {skill_data_for_calc['importance']:.2f}. Calculated intensity: {intensity:.2f}")

            if intensity > competence_threshold:
                # Avoid creating new goal if an active one for this skill already exists
                existing_goal_for_skill = any(
                    g.type == "INTRINSIC_COMPETENCE" and g.target_skill_id == skill_id and g.status in ["PENDING", "ACTIVE"]
                    for g in self.goals
                )
                if existing_goal_for_skill:
                    self._log_message(f"Skipping competence goal for skill '{skill_id}', active one already exists.")
                    continue

                target_prof = skill_data_for_calc.get("target_proficiency", 1.0)
                desc = f"Improve skill: {skill_id} (Current Prof: {skill_data_for_calc['proficiency']:.2f}, Target: {target_prof:.2f}, Calculated Intensity: {intensity:.2f})"
                source_trigger_details = { # Information about why this competence goal was triggered
                    "trigger_type": "LOW_PROFICIENCY_OR_MASTERY_OPPORTUNITY", # More descriptive
                    "skill_id": skill_id, # The skill in question
                    "assessed_proficiency_at_trigger": skill_data_for_calc['proficiency'], # Proficiency level that triggered assessment
                    "assessed_importance_at_trigger": skill_data_for_calc['importance'], # Importance that triggered assessment
                    "calculated_intensity": intensity # The final calculated intensity for this drive
                }
                # Specific details about the competence goal itself (current state, target state)
                competence_details_for_goal = {
                    "current_proficiency": skill_data_for_calc['proficiency'], # Current proficiency of the skill
                    "target_proficiency": target_prof, # The proficiency level the agent aims for
                    "initial_importance_rating": skill_data_for_calc['importance'] # Importance rating at time of goal creation
                }
                # The initial_priority of the goal is derived from the calculated intensity.
                goal_id = self.add_goal(
                    description=desc,
                    goal_type="INTRINSIC_COMPETENCE",
                    initial_priority=intensity * 10.0, # Scale intensity to a broader priority range
                    source_trigger=source_trigger_details,
                    # Storing target_skill_id and competence_details directly in the Goal object:
                    target_skill_id=skill_id,
                    competence_details=competence_details_for_goal
                )
                new_competence_goal_ids.append(goal_id)

        return new_competence_goal_ids


    def _generate_curiosity_satisfaction_reward(self, satisfied_goal: Goal, information_gain_details: Dict) -> Optional[Dict]:
        """
        Generates a conceptual intrinsic reward signal when a curiosity goal is satisfied.
        Args:
            satisfied_goal: The Goal object that was satisfied.
            information_gain_details: Dict describing the information gained.
                e.g., {"type": "uncertainty_reduced", "concept_id": "...", "old_confidence": 0.2, "new_confidence": 0.8}
                      {"type": "novelty_integrated", "item_id": "...", "integration_level": 0.9}
        Returns:
            A dictionary representing the conceptual reward, or None.
        """
        if satisfied_goal.type != "INTRINSIC_CURIOSITY":
            self._log_message(f"Attempted to generate curiosity reward for non-curiosity goal: {satisfied_goal.id} ({satisfied_goal.type})")
            return None

        reward_magnitude = 0.0
        gain_type = information_gain_details.get("type")

        if gain_type == "uncertainty_reduced":
            old_conf = information_gain_details.get("old_confidence", 0.0)
            new_conf = information_gain_details.get("new_confidence", 0.0)
            reward_magnitude = (new_conf - old_conf) * 1.0 # Scale factor of 1.0
        elif gain_type == "novelty_integrated":
            integration_level = information_gain_details.get("integration_level", 0.0)
            reward_magnitude = integration_level * 0.8 # Scale factor of 0.8
        else:
            self._log_message(f"Unknown information gain type '{gain_type}' for curiosity reward calculation for goal {satisfied_goal.id}.")
            reward_magnitude = 0.1 # Small default for satisfying a curiosity goal even if gain type is unclear

        clamped_reward = max(0.0, min(1.0, reward_magnitude)) # Ensure reward is between 0 and 1

        reward_signal = {
            "type": "INTRINSIC_CURIOSITY_SATISFACTION",
            "magnitude": clamped_reward,
            "goal_id": satisfied_goal.id,
            "goal_description": satisfied_goal.description,
            "trigger_details_at_creation": satisfied_goal.source_trigger, # Store what originally triggered it
            "satisfaction_details": information_gain_details
        }
        self._log_message(f"Conceptual intrinsic reward for curiosity generated: Magnitude {clamped_reward:.2f} for Goal ID '{satisfied_goal.id}'. Details: {str(information_gain_details)[:100]}")
        # In a full system, this reward_signal might be published on the message bus
        # for the Learning Module or other relevant components.
        return reward_signal

    # --- Placeholder Helper Functions for Dynamic Priority ---
    @staticmethod
    def _get_base_priority(goal_type: str) -> float:
        if goal_type == "EXTRINSIC_TASK": return 0.5
        if goal_type == "INTRINSIC_CURIOSITY": return 0.3
        if goal_type == "INTRINSIC_COMPETENCE": return 0.35
        return 0.2

    @staticmethod
    def _get_urgency_factor(goal: Goal, current_context: Optional[Dict] = None) -> float:
        # Example: if goal.deadline is approaching, increase urgency.
        # For now, placeholder.
        return 0.0

    @staticmethod
    def _get_value_alignment_score(goal: Goal, self_model_snapshot: Optional[Dict] = None) -> float:
        # Example: Check if goal.description aligns with self_model_snapshot.values
        # For now, placeholder (1.0 = neutral or perfectly aligned)
        return 1.0

    @staticmethod
    def _get_dependency_factor(goal: Goal, active_goals: List[Goal]) -> float:
        # Example: If other high-priority goals depend on this one.
        # For now, placeholder (0.0 = no strong dependencies increasing its priority)
        return 0.0

    @staticmethod
    def _get_estimated_cost(goal: Goal, planning_snapshot: Optional[Dict] = None) -> float:
        # Example: Higher cost (time, resources, risk) slightly reduces priority.
        # For now, placeholder (low cost)
        return 0.1

    def _handle_emotional_state_change(self, message: GenericMessage):
        """Handles EmotionalStateChange messages by updating the internal emotional state."""
        if not isinstance(message.payload, EmotionalStateChangePayload):
            self._log_message(f"ERROR: Received non-EmotionalStateChangePayload for EmotionalStateChange: {type(message.payload)}")
            return

        self._last_emotional_state = message.payload
        # Example: VAD profile: {'valence': 0.2, 'arousal': 0.6, 'dominance': 0.4}
        profile_summary = {
            "V": self._last_emotional_state.current_emotion_profile.get('valence', 'N/A'),
            "A": self._last_emotional_state.current_emotion_profile.get('arousal', 'N/A'),
            "D": self._last_emotional_state.current_emotion_profile.get('dominance', 'N/A')
        }
        self._log_message(f"Received and stored new emotional state. Profile (V,A,D): {profile_summary}. Primary: {self._last_emotional_state.primary_emotion}, Intensity: {self._last_emotional_state.intensity}")


    def _calculate_dynamic_priority(self, goal: Goal, all_active_goals_for_context: List[Goal], current_emotional_state: Optional[EmotionalStateChangePayload]) -> float:
        """Calculates a dynamic priority for a goal based on multiple factors, normalized to 0-1."""

        base_priority_for_type = ConcreteMotivationalSystemModule._get_base_priority(goal.type)

        intensity = 0.0
        # For intrinsic goals (Curiosity, Competence), the 'intensity' component of dynamic priority
        # is derived from their calculated drive intensity, which is stored in `goal.source_trigger.calculated_intensity`.
        # This `calculated_intensity` is already a normalized value (0-1).
        if goal.type in ["INTRINSIC_CURIOSITY", "INTRINSIC_COMPETENCE"]:
            if goal.source_trigger and "calculated_intensity" in goal.source_trigger:
                intensity = goal.source_trigger["calculated_intensity"]
                self._log_message(f"DynamicPrio for Intrinsic Goal '{goal.id}': Using calculated_intensity {intensity:.2f} from source_trigger.")
            else:
                intensity = 0.1 # Default low intensity if not found, though it should be there.
                self._log_message(f"Warning: Intrinsic Goal '{goal.id}' missing 'calculated_intensity' in source_trigger. Defaulting intensity to {intensity:.2f}.")
        elif goal.type == "EXTRINSIC_TASK":
            # For EXTRINSIC_TASK, `goal.priority` is the externally set importance (e.g., on a 0-10 scale).
            # We normalize this to a 0-1 scale to serve as the 'intensity' component in the dynamic priority formula.
            # A higher `goal.priority` value for an extrinsic task means it contributes more to its dynamic priority.
            intensity = goal.priority / 10.0 # Assuming goal.priority is on a 0-10 scale. Adjust if scale is different.
            self._log_message(f"DynamicPrio for Extrinsic Goal '{goal.id}': Using normalized goal.priority {intensity:.2f} (original: {goal.priority}).")
        else:
            # For other goal types, or if a more nuanced intensity calculation is needed.
            # Fallback to using the goal's `priority` field, normalized, if it makes sense for that type.
            intensity = goal.priority / 10.0 # Default assumption for unhandled types
            self._log_message(f"DynamicPrio for Goal '{goal.id}' (Type: {goal.type}): Defaulting intensity to normalized goal.priority {intensity:.2f}.")


        # These would ideally take more specific context snapshots (e.g., from WM, SM, Planner)
        urgency_factor = ConcreteMotivationalSystemModule._get_urgency_factor(goal, None)
        value_alignment_score = ConcreteMotivationalSystemModule._get_value_alignment_score(goal, None)
        dependency_factor = ConcreteMotivationalSystemModule._get_dependency_factor(goal, all_active_goals_for_context)
        estimated_cost = ConcreteMotivationalSystemModule._get_estimated_cost(goal, None)

        # Weights for combining factors
        w_base = 0.20
        w_int = 0.30
        w_urg = 0.15
        w_val = 0.15
        w_dep = 0.10
        w_cost = 0.10 # Cost is subtracted
        w_emo = 0.10  # Weight for emotional modifier

        dynamic_p_raw = (
            w_base * base_priority_for_type +
            w_int * intensity +
            w_urg * urgency_factor +
            w_val * value_alignment_score +
            w_dep * dependency_factor -
            w_cost * estimated_cost
        )

        emotional_modifier = 0.0
        log_emo_details = "None"
        if current_emotional_state and current_emotional_state.current_emotion_profile:
            V = current_emotional_state.current_emotion_profile.get('valence', 0.0)
            A = current_emotional_state.current_emotion_profile.get('arousal', 0.0)
            log_emo_details = f"V={V:.2f}, A={A:.2f}"

            if V > 0.5: # Positive affect
                emotional_modifier += V * 0.1
            elif V < -0.5: # Negative affect
                emotional_modifier -= abs(V) * 0.1

            if A > 0.7: # High arousal
                emotional_modifier += A * 0.05
            elif A < 0.2 and goal.type in ["INTRINSIC_CURIOSITY", "INTRINSIC_COMPETENCE"]: # Low arousal/boredom
                emotional_modifier += 0.1 # Specific boost for intrinsic goals

            dynamic_p_raw += w_emo * emotional_modifier
            log_emo_details += f", EmoModRaw={emotional_modifier:.3f}, WeightedEmoMod={(w_emo * emotional_modifier):.3f}"


        # Conceptual heuristic: If no high-priority extrinsic tasks are pressing, slightly boost intrinsic goals.
        is_intrinsic = goal.type in ["INTRINSIC_CURIOSITY", "INTRINSIC_COMPETENCE"]
        if is_intrinsic:
            has_high_priority_extrinsic = False
            # Check against base priority of other active goals for simplicity in this heuristic
            for g_other in all_active_goals_for_context:
                if g_other.id != goal.id and g_other.type == "EXTRINSIC_TASK" and \
                   g_other.status == "ACTIVE" and g_other.priority > 7.0: # Example threshold for "high base priority extrinsic"
                    has_high_priority_extrinsic = True
                    break
            if not has_high_priority_extrinsic:
                boost_amount = 0.05
                self._log_message(f"Goal '{goal.id}' ({goal.type}): Applying +{boost_amount:.2f} intrinsic boost (RawP before boost: {dynamic_p_raw:.3f}). No high-prio extrinsic tasks.")
                dynamic_p_raw += boost_amount

        normalized_priority = max(0.0, min(1.0, dynamic_p_raw))

        self._log_message(
            f"Goal '{goal.id}' ({goal.type}, InitialPrioField:{goal.priority:.2f}): "
            f"TypeBase={base_priority_for_type:.2f}(w:{w_base:.2f}), "
            f"Intensity={intensity:.2f}(w:{w_int:.2f}), "
            f"Urg={urgency_factor:.2f}(w:{w_urg:.2f}), "
            f"ValAlign={value_alignment_score:.2f}(w:{w_val:.2f}), "
            f"Dep={dependency_factor:.2f}(w:{w_dep:.2f}), "
            f"Cost={estimated_cost:.2f}(w:{w_cost:.2f}) " # Removed comma
            f"EmoState=({log_emo_details}) "
            f"-> RawDynP(post-boost if any)={dynamic_p_raw:.3f} -> NormDynP={normalized_priority:.3f}"
        )
        return normalized_priority

    # The _generate_competence_satisfaction_reward method was here.
    # It has been moved earlier in the file to avoid duplication.

    def suggest_highest_priority_goal(self) -> Optional[Goal]:
        """
        Suggests the highest priority goal based on dynamic calculation.
        Returns the Goal object.
        """
        active_goals_with_dyn_prio = self.get_active_goals(return_with_priority_scores=True)

        if not active_goals_with_dyn_prio: # This list now contains (dynamic_priority_score, Goal)
            self._log_message("No active goals to suggest.")
            return None

        highest_priority_score, highest_goal = active_goals_with_dyn_prio[0]

        if len(active_goals_with_dyn_prio) > 1:
            second_highest_priority_score, _ = active_goals_with_dyn_prio[1]
            if (highest_priority_score - second_highest_priority_score) < 0.05: # Using 0-1 scale for comparison
                top_goals_log = [
                    f"{g.id} (DynP:{p_score:.3f}, BaseP:{g.priority:.2f})" for p_score, g in active_goals_with_dyn_prio[:3]
                ]
                self._log_message(
                    f"Potential goal conflict or similar high dynamic priority for goals: {', '.join(top_goals_log)}. "
                    f"Highest suggested: {highest_goal.id} (DynP:{highest_priority_score:.3f}). "
                    "Further resolution might be needed."
                )

        self._log_message(f"Suggested highest priority goal: {highest_goal.id} with dynamic priority {highest_priority_score:.3f} (BasePrioField: {highest_goal.priority:.2f}, Type: {highest_goal.type})")
        return highest_goal

    def _handle_action_event(self, message: GenericMessage) -> None:
        """
        Handles ActionEvent messages from the message bus.
        Updates goal status based on action outcomes.
        Also, assesses if suboptimal performance should trigger competence goals.
        """
        if not isinstance(message.payload, ActionEventPayload):
            self._log_message(f"ERROR ({self._module_id}): Received non-ActionEventPayload: {type(message.payload)}") # Corrected print to log
            return

        payload: ActionEventPayload = message.payload
        self._log_message(f"Handling ActionEvent for command '{payload.action_command_id}', Action: '{payload.action_type}', Status: {payload.status}") # Corrected print to log

        goal_id_from_outcome: Optional[str] = None
        new_status_from_outcome: Optional[str] = None
        related_skill_id = payload.action_type # Default to action_type as skill_id

        if payload.outcome:
            goal_id_from_outcome = payload.outcome.get("goal_id")
            new_status_from_outcome = payload.outcome.get("new_status")
            # If outcome explicitly mentions skill_used, prefer that.
            related_skill_id = payload.outcome.get("skill_used", payload.action_type)


            if goal_id_from_outcome and not new_status_from_outcome:
                if payload.status == "SUCCESS": new_status_from_outcome = "ACHIEVED"
                elif payload.status == "FAILURE": new_status_from_outcome = "FAILED"

        if goal_id_from_outcome and new_status_from_outcome:
            goal = self.get_goal(goal_id_from_outcome)
            if goal:
                self._log_message(f"ActionEvent outcome suggests updating goal '{goal_id_from_outcome}' to status '{new_status_from_outcome}'.")
                self.update_goal_status(goal_id_from_outcome, new_status_from_outcome) # This will publish GoalUpdate

                if new_status_from_outcome == "ACHIEVED":
                    if goal.type == "INTRINSIC_CURIOSITY":
                        # Use skill_id if available in outcome, else default.
                        info_gain_item_id = payload.outcome.get("explored_item_id", related_skill_id)
                        info_gain = payload.outcome.get("information_gain_details", {"type": "exploration_completed", "item_id": info_gain_item_id})
                        self._generate_curiosity_satisfaction_reward(goal, info_gain)
                    elif goal.type == "INTRINSIC_COMPETENCE":
                        # Competence gain details might specify the skill and new proficiency.
                        comp_gain_skill_id = payload.outcome.get("competence_skill_id", goal.target_skill_id)
                        new_prof = payload.outcome.get("new_proficiency_level", goal.competence_details.get("target_proficiency",0.8) if goal.competence_details else 0.8)
                        comp_gain = payload.outcome.get("competence_gain_details", {"type": "skill_proficiency_increased", "skill_id": comp_gain_skill_id, "new_proficiency": new_prof})
                        self._generate_competence_satisfaction_reward(goal, comp_gain)
            else:
                self._log_message(f"WARNING: Goal '{goal_id_from_outcome}' from ActionEvent outcome not found.")
        elif not goal_id_from_outcome:
             self._log_message(f"No specific goal ID in ActionEvent outcome for command '{payload.action_command_id}'. Outcome: {payload.outcome}")


        # Competence goal trigger from task performance feedback
        is_suboptimal_performance = payload.status == "FAILURE" or \
                                  (payload.status == "SUCCESS" and payload.outcome and \
                                   (payload.outcome.get("efficiency") == "low" or payload.outcome.get("quality") == "poor"))

        if is_suboptimal_performance:
            self._log_message(f"ActionEvent indicates suboptimal performance for action/skill '{related_skill_id}'. Assessing for competence goal.")

            existing_competence_goal_for_skill = any(
                g.type == "INTRINSIC_COMPETENCE" and g.target_skill_id == related_skill_id and g.status in ["PENDING", "ACTIVE"]
                for g in self.goals
            )

            if not existing_competence_goal_for_skill:
                # Simulate skill data for intensity calculation. In a full system, this might come from SelfModel or LTM.
                # Importance could be related to the priority of the goal associated with the failed action, if available.
                task_importance = 0.6 # Default importance
                if goal_id_from_outcome: # If the failed action was tied to a known goal
                    failed_goal = self.get_goal(goal_id_from_outcome)
                    if failed_goal:
                        task_importance = failed_goal.priority / 10.0 # Normalize if priority is 0-10
                elif payload.priority: # Use action command priority if available
                    task_importance = payload.priority # Assuming it's already 0-1

                skill_data_for_trigger = {
                    "proficiency": 0.3, # Assume low proficiency due to failure/suboptimal performance
                    "importance": task_importance,
                    "target_proficiency": 0.8 # Default target for improvement
                }
                intensity = self._calculate_competence_drive_intensity(related_skill_id, skill_data_for_trigger, self.get_active_goals())

                if intensity > 0.35: # Threshold for this trigger type
                    desc = f"Improve skill '{related_skill_id}' due to task performance (Action: {payload.action_type}, Status: {payload.status}, Intensity: {intensity:.2f})"
                    source_trigger = {
                        "trigger_type": "TASK_PERFORMANCE_FEEDBACK",
                        "action_type": payload.action_type,
                        "action_command_id": payload.action_command_id,
                        "status": payload.status,
                        "related_skill_id": related_skill_id,
                        "calculated_intensity": intensity
                    }
                    competence_details_for_goal = {
                        "current_proficiency_assumed": skill_data_for_trigger["proficiency"],
                        "target_proficiency": skill_data_for_trigger["target_proficiency"],
                        "triggering_action_event_id": message.message_id
                    }
                    self.add_goal(
                        description=desc,
                        goal_type="INTRINSIC_COMPETENCE",
                        initial_priority=intensity * 10.0, # Scale intensity
                        source_trigger=source_trigger,
                        target_skill_id=related_skill_id,
                        competence_details=competence_details_for_goal
                    )
            else:
                self._log_message(f"Skipping competence goal for skill '{related_skill_id}' as an active one already exists.")


    def get_module_status(self) -> Dict[str, Any]:
        """Returns the current status of the Motivational System Module."""
        status_counts: Dict[str, int] = {}
        for goal in self.goals:
            status_counts[goal.status] = status_counts.get(goal.status, 0) + 1

        # Active goals sorted by current dynamic priority for status reporting
        active_goals_sorted = self.get_active_goals(return_with_priority_scores=True)
        top_active_goals_summary = [
            {"id": g.id, "type": g.type, "dynamic_priority": round(dp, 3), "base_priority_field": g.priority, "status": g.status}
            for dp, g in active_goals_sorted[:3] # Report top 3
        ]

        return {
            "module_id": self._module_id,
            "module_type": "ConcreteMotivationalSystemModule (Message Bus Integrated)",
            "total_goals": len(self.goals),
            "goals_by_status": status_counts,
            "top_active_goals_summary": top_active_goals_summary,
            "message_bus_configured": self._message_bus is not None,
            "next_goal_id_counter": self.next_goal_id,
            "log_entries": len(self._log)
        }

    def update_motivation_state(self, new_state_info: Dict[str, Any]) -> bool:
        """
        Placeholder for updating broader motivation state (e.g., drive levels).
        """
        self._log_message(f"update_motivation_state called with: {new_state_info}. (Placeholder)")
        return True

    def evaluate_and_generate_intrinsic_goals_dynamically(self,
                                                        knowledge_map_snapshot: Optional[Dict[str, Dict[str, Any]]],
                                                        capability_inventory_snapshot: Optional[Dict[str, Dict[str, Any]]],
                                                        current_world_event: Optional[Dict[str,Any]] = None) -> Dict[str, List[str]]:
        """
        Evaluates current state (knowledge, capabilities, world events) to dynamically
        generate intrinsic curiosity and competence goals.
        This method simulates being called periodically or by significant system events.
        """
        self._log_message("Starting dynamic evaluation for intrinsic goals...")

        new_curiosity_goal_ids: List[str] = []
        if knowledge_map_snapshot is not None or current_world_event is not None:
            self._log_message("Assessing curiosity triggers...")
            new_curiosity_goal_ids = self.assess_curiosity_triggers(knowledge_map_snapshot, world_event=current_world_event)
            if new_curiosity_goal_ids:
                self._log_message(f"Generated {len(new_curiosity_goal_ids)} new INTRINSIC_CURIOSITY goals: {new_curiosity_goal_ids}")

        new_competence_goal_ids: List[str] = []
        if capability_inventory_snapshot is not None:
            self._log_message("Assessing competence opportunities...")
            active_goals_list = self.get_active_goals() # get_active_goals already returns List[Goal] by default
            new_competence_goal_ids = self.assess_competence_opportunities(capability_inventory_snapshot, active_goals_list)
            if new_competence_goal_ids:
                self._log_message(f"Generated {len(new_competence_goal_ids)} new INTRINSIC_COMPETENCE goals: {new_competence_goal_ids}")

        self._log_message("Dynamic intrinsic goal evaluation complete.")
        return {"new_curiosity_goals": new_curiosity_goal_ids, "new_competence_goals": new_competence_goal_ids}


if __name__ == '__main__':
    import asyncio

    # Ensure MessageBus and core_messages are available for __main__
    # This is primarily for direct execution of this file.
    if MessageBus is None or GenericMessage is None or GoalUpdatePayload is None or ActionEventPayload is None:
        print("CRITICAL: MessageBus or core_messages not loaded correctly for __main__ test. Exiting.")
        exit(1)

    print("\n--- ConcreteMotivationalSystemModule __main__ Test ---")

    received_goal_updates: List[GenericMessage] = []
    def goal_update_listener(message: GenericMessage):
        print(f"\n goal_update_listener: Received GoalUpdate! ID: {message.message_id[:8]}")
        if isinstance(message.payload, GoalUpdatePayload):
            payload: GoalUpdatePayload = message.payload
            print(f"  Source: {message.source_module_id}")
            print(f"  Goal ID: {payload.goal_id}, Desc: '{payload.goal_description[:30]}...'")
            print(f"  Status: {payload.status}, Priority: {payload.priority:.2f}")
            print(f"  Originator: {payload.originator}")
            received_goal_updates.append(message)
        else:
            print(f"  ERROR: Listener received non-GoalUpdatePayload: {type(message.payload)}")


    async def main_test_flow():
        bus = MessageBus()
        module_id_for_test = "MotSysTest01"
        mot_sys = ConcreteMotivationalSystemModule(message_bus=bus, module_id=module_id_for_test)

        bus.subscribe(
            module_id="TestGoalListener",
            message_type="GoalUpdate",
            callback=goal_update_listener
        )
        print("\nTestGoalListener subscribed to GoalUpdate messages.")

        print("\n--- Initial Status ---")
        print(mot_sys.get_module_status())

        # --- Test Publishing on goal modifications ---
        print("\n--- Adding Goals (should publish GoalUpdates) ---")
        received_goal_updates.clear()
        g1_id = mot_sys.add_goal("Explore dataset Alpha", "INTRINSIC_CURIOSITY", 7.5, {"trigger": "new_data_signal", "originator": "CuriositySubsystem"})
        await asyncio.sleep(0.01) # Allow bus to process if async
        assert len(received_goal_updates) == 1, "GoalUpdate for add_goal (g1) not received"
        assert received_goal_updates[0].payload.goal_id == g1_id
        assert received_goal_updates[0].payload.status == "PENDING"
        assert received_goal_updates[0].source_module_id == module_id_for_test

        g2_id = mot_sys.add_goal("Process user request #123", "EXTRINSIC_TASK", 9.0, {"user_id": "user_x", "originator": "UserInteractionModule"})
        await asyncio.sleep(0.01)
        assert len(received_goal_updates) == 2, "GoalUpdate for add_goal (g2) not received"
        assert received_goal_updates[1].payload.goal_id == g2_id
        assert received_goal_updates[1].payload.originator == "UserInteractionModule"


        print("\n--- Updating Goal Status (should publish GoalUpdate) ---")
        received_goal_updates.clear()
        mot_sys.update_goal_status(g1_id, "ACTIVE")
        await asyncio.sleep(0.01)
        assert len(received_goal_updates) == 1, "GoalUpdate for status change not received"
        assert received_goal_updates[0].payload.goal_id == g1_id
        assert received_goal_updates[0].payload.status == "ACTIVE"

        print("\n--- Updating Goal Priority (should publish GoalUpdate) ---")
        received_goal_updates.clear()
        mot_sys.update_goal_priority(g2_id, 9.5)
        await asyncio.sleep(0.01)
        assert len(received_goal_updates) == 1, "GoalUpdate for priority change not received"
        assert received_goal_updates[0].payload.goal_id == g2_id
        assert received_goal_updates[0].payload.priority == 9.5


        # --- Test Subscribing to ActionEvent ---
        print("\n--- Simulating ActionEvent (goal success) ---")
        # Ensure g1 is in a state that can be achieved (e.g. ACTIVE)
        if mot_sys.get_goal(g1_id).status != "ACTIVE":
            mot_sys.update_goal_status(g1_id, "ACTIVE") # This will publish one update
            await asyncio.sleep(0.01) # let it publish
            received_goal_updates.clear() # Clear this update before testing the ActionEvent trigger

        action_event_success_payload = ActionEventPayload(
            action_command_id="cmd_abc_123",
            action_type="EXPLORE_DATASET",
            status="SUCCESS",
            outcome={"goal_id": g1_id, "new_status": "ACHIEVED", "details": "Exploration complete, insights found."}
        )
        action_event_msg_success = GenericMessage(
            source_module_id="ActionExecutorModule",
            message_type="ActionEvent",
            payload=action_event_success_payload
        )
        bus.publish(action_event_msg_success)
        await asyncio.sleep(0.01) # Allow _handle_action_event and subsequent publish

        assert len(received_goal_updates) > 0, "GoalUpdate not received after ActionEvent (SUCCESS)"
        if received_goal_updates: # Check the last message
            last_update = received_goal_updates[-1].payload
            assert last_update.goal_id == g1_id
            assert last_update.status == "ACHIEVED"
            print(f"  Listener correctly received GoalUpdate for '{g1_id}' status '{last_update.status}' triggered by ActionEvent.")


        print("\n--- Simulating ActionEvent (goal failure from outcome) ---")
        received_goal_updates.clear()
        # Ensure g2 is in a state that can be failed
        if mot_sys.get_goal(g2_id).status != "ACTIVE":
             mot_sys.update_goal_status(g2_id, "ACTIVE")
             await asyncio.sleep(0.01)
             received_goal_updates.clear()

        action_event_failure_payload = ActionEventPayload(
            action_command_id="cmd_def_456",
            action_type="PROCESS_USER_REQUEST",
            status="FAILURE", # Main status is failure
            outcome={"goal_id": g2_id, "new_status": "FAILED", "reason": "Resource unavailable"} # Specific new status in outcome
        )
        action_event_msg_failure = GenericMessage(
            source_module_id="ActionExecutorModule",
            message_type="ActionEvent",
            payload=action_event_failure_payload
        )
        bus.publish(action_event_msg_failure)
        await asyncio.sleep(0.01)

        assert len(received_goal_updates) > 0, "GoalUpdate not received after ActionEvent (FAILURE from outcome)"
        if received_goal_updates:
            last_update_fail = received_goal_updates[-1].payload
            assert last_update_fail.goal_id == g2_id
            assert last_update_fail.status == "FAILED"
            print(f"  Listener correctly received GoalUpdate for '{g2_id}' status '{last_update_fail.status}' triggered by ActionEvent.")


        print("\n--- Simulating ActionEvent (goal failure from status, no new_status in outcome) ---")
        g3_id = mot_sys.add_goal("Perform risky operation", "EXTRINSIC_TASK", 8.0, initial_status="ACTIVE")
        await asyncio.sleep(0.01)
        received_goal_updates.clear()

        action_event_failure_status_payload = ActionEventPayload(
            action_command_id="cmd_ghi_789",
            action_type="RISKY_OPERATION",
            status="FAILURE", # Main status implies goal failure
            outcome={"goal_id": g3_id, "reason": "Operation timed out"} # NO new_status in outcome
        )
        action_event_msg_failure_status = GenericMessage(
            source_module_id="ActionExecutorModule",
            message_type="ActionEvent",
            payload=action_event_failure_status_payload
        )
        bus.publish(action_event_msg_failure_status)
        await asyncio.sleep(0.01)

        assert len(received_goal_updates) > 0, "GoalUpdate not received after ActionEvent (FAILURE from status)"
        if received_goal_updates:
            last_update_fail_status = received_goal_updates[-1].payload
            assert last_update_fail_status.goal_id == g3_id
            assert last_update_fail_status.status == "FAILED" # Should map ActionEvent.status="FAILURE" to Goal.status="FAILED"
            print(f"  Listener correctly received GoalUpdate for '{g3_id}' status '{last_update_fail_status.status}' triggered by ActionEvent status.")


        print("\n--- Final Module Status ---")
        print(mot_sys.get_module_status())
        assert mot_sys.get_goal(g1_id).status == "ACHIEVED"
        assert mot_sys.get_goal(g2_id).status == "FAILED"
        assert mot_sys.get_goal(g3_id).status == "FAILED"

        print("\n--- ConcreteMotivationalSystemModule __main__ Test Complete ---")

    try:
        asyncio.run(main_test_flow())
    except RuntimeError as e:
        if " asyncio.run() cannot be called from a running event loop" in str(e):
            print("Skipping asyncio.run() as an event loop is already running (e.g. in Jupyter/IPython).")
        else:
            raise

    # Old __main__ content for reference:
    # mot_sys = ConcreteMotivationalSystemModule()
    # print("\n--- Initial Status ---")
    # print(mot_sys.get_module_status())
    # print("\n--- Adding Goals ---")
    # g1_id = mot_sys.add_goal("Explore dataset Alpha", "INTRINSIC_CURIOSITY", 7.5, {"trigger": "new_data_signal"})
    # ... rest of old main commented or removed for brevity ...
    # print("\nExample Usage Complete (Phase 1 Enhanced Motivational System).")
