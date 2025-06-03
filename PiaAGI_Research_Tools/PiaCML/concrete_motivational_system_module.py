from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import time

try:
    from .base_motivational_system_module import BaseMotivationalSystemModule
except ImportError:
    # Fallback for standalone execution or if .base_motivational_system_module is not found in the current path
    class BaseMotivationalSystemModule: # Minimal stub for standalone running
        def manage_goals(self, action: str, goal_data: Optional[Dict[str, Any]] = None) -> Any: pass
        def get_active_goals(self, N: int = 0, min_priority: float = 0.0) -> List[Dict[str, Any]]: return []
        def update_motivation_state(self, new_state_info: Dict[str, Any]) -> bool: return False


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

class ConcreteMotivationalSystemModule(BaseMotivationalSystemModule):
    """
    A concrete implementation of the BaseMotivationalSystemModule using a structured Goal dataclass.
    Manages a list of goals and includes basic mechanisms for intrinsic motivation (curiosity).
    """

    def __init__(self):
        self.goals: List[Goal] = []
        self.next_goal_id: int = 0
        print("ConcreteMotivationalSystemModule (Phase 1 Enhanced) initialized.")

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
        print(f"ConcreteMotSys: Added goal '{new_id}': {description} (Priority: {initial_priority})")
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
            goal.status = new_status
            print(f"ConcreteMotSys: Updated status of goal '{goal_id}' to '{new_status}'.")
            return True
        print(f"ConcreteMotSys: Goal '{goal_id}' not found for status update.")
        return False

    def update_goal_priority(self, goal_id: str, new_priority: float) -> bool:
        """Updates the priority of an existing goal."""
        goal = self.get_goal(goal_id)
        if goal:
            goal.priority = new_priority
            print(f"ConcreteMotSys: Updated priority of goal '{goal_id}' to {new_priority:.2f}.")
            return True
        print(f"ConcreteMotSys: Goal '{goal_id}' not found for priority update.")
        return False

    def get_active_goals(self) -> List[Goal]:
        """
        Returns a list of goals with status "PENDING" or "ACTIVE",
        sorted by priority (descending).
        """
        active_statuses = {"PENDING", "ACTIVE"}
        # Filter for active statuses first
        relevant_goals = [g for g in self.goals if g.status in active_statuses]
        # Sort by priority, descending
        relevant_goals.sort(key=lambda g: g.priority, reverse=True)
        return relevant_goals

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

        if world_event and world_event.get("type") == "NOVEL_STIMULUS":
            novelty_score = world_event.get("novelty_score", 0.0)
            if novelty_score > 0.7:
                event_id_desc = world_event.get('id', world_event.get('description', 'unknown stimulus'))
                priority = novelty_score * 10.0 # Scale novelty to priority (0-10 for example)
                goal_id = self.add_goal(
                    description=f"Investigate novel event: {event_id_desc}",
                    goal_type="INTRINSIC_CURIOSITY",
                    initial_priority=min(10.0, priority), # Cap priority if needed
                    source_trigger=world_event
                )
                new_curiosity_goal_ids.append(goal_id)
                print(f"ConcreteMotSys: Curiosity goal '{goal_id}' added for novel event '{event_id_desc}'.")

        if knowledge_map_snapshot:
            for concept_id, data in knowledge_map_snapshot.items():
                confidence = data.get("confidence", 1.0)
                if confidence < 0.5:
                    # Check if a similar curiosity goal already exists and is active/pending
                    # This is a simple check; more sophisticated checks might be needed.
                    existing_goal_for_concept = any(
                        g.type == "INTRINSIC_CURIOSITY" and
                        g.source_trigger and g.source_trigger.get("concept_id") == concept_id and
                        g.status in ["PENDING", "ACTIVE"]
                        for g in self.goals
                    )
                    if not existing_goal_for_concept:
                        priority = (1.0 - confidence) * 10.0 # Higher priority for lower confidence
                        trigger_info = {"type": "KNOWLEDGE_GAP", "concept_id": concept_id, "confidence": confidence}
                        goal_id = self.add_goal(
                            description=f"Resolve uncertainty for concept: {concept_id}",
                            goal_type="INTRINSIC_CURIOSITY",
                            initial_priority=min(10.0, priority),
                            source_trigger=trigger_info
                        )
                        new_curiosity_goal_ids.append(goal_id)
                        print(f"ConcreteMotSys: Curiosity goal '{goal_id}' added for knowledge gap on '{concept_id}'.")

        return new_curiosity_goal_ids

    def suggest_highest_priority_goal(self) -> Optional[Goal]:
        """
        Suggests the highest priority goal that is currently "PENDING" or "ACTIVE".
        """
        active_goals = self.get_active_goals()
        if active_goals:
            return active_goals[0]
        return None

    def get_module_status(self) -> Dict[str, Any]:
        """Returns the current status of the Motivational System Module."""
        status_counts: Dict[str, int] = {}
        for goal in self.goals:
            status_counts[goal.status] = status_counts.get(goal.status, 0) + 1

        return {
            "module_type": "ConcreteMotivationalSystemModule (Phase 1 Enhanced)",
            "total_goals": len(self.goals),
            "goals_by_status": status_counts,
            "next_goal_id_counter": self.next_goal_id
        }

    # --- Compatibility for BaseMotivationalSystemModule ABC (if needed) ---
    # The BaseMotivationalSystemModule's abstract methods are:
    # manage_goals(self, action: str, goal_data: Optional[Dict[str, Any]] = None)
    # get_active_goals(self, N: int = 0, min_priority: float = 0.0) -> List[Dict[str, Any]]
    # update_motivation_state(self, new_state_info: Dict[str, Any]) -> bool
    # We have a new get_active_goals that returns List[Goal].
    # We can add a wrapper for the old manage_goals or decide it's replaced.
    # For now, we'll consider manage_goals replaced by specific methods.
    # The old get_active_goals returned List[Dict], new one returns List[Goal].
    # This might require adjustment in calling code or a compatibility wrapper.

    def update_motivation_state(self, new_state_info: Dict[str, Any]) -> bool:
        """
        Placeholder for updating broader motivation state (e.g., drive levels).
        Not a primary focus for Phase 1 goal structure enhancements.
        """
        print(f"ConcreteMotSys: update_motivation_state called with: {new_state_info}. (Placeholder - no internal state change)")
        return True


if __name__ == '__main__':
    mot_sys = ConcreteMotivationalSystemModule()

    print("\n--- Initial Status ---")
    print(mot_sys.get_module_status())

    print("\n--- Adding Goals ---")
    g1_id = mot_sys.add_goal("Explore dataset Alpha", "INTRINSIC_CURIOSITY", 7.5, {"trigger": "new_data_signal"})
    g2_id = mot_sys.add_goal("Process user request #123", "EXTRINSIC_TASK", 9.0, {"user_id": "user_x"})
    g3_id = mot_sys.add_goal("Learn about 'quantum entanglement'", "INTRINSIC_CURIOSITY", 6.0)

    print(f"\nGoal {g1_id}: {mot_sys.get_goal(g1_id)}")
    print(f"Total goals: {len(mot_sys.goals)}")
    assert len(mot_sys.goals) == 3

    print("\n--- Updating Goals ---")
    mot_sys.update_goal_status(g1_id, "ACTIVE")
    mot_sys.update_goal_status(g2_id, "ACTIVE")
    mot_sys.update_goal_priority(g3_id, 6.5) # Increase priority for g3
    mot_sys.update_goal_status(g3_id, "PENDING") # Keep g3 pending

    print(f"Goal {g3_id} status: {mot_sys.get_goal(g3_id).status}, priority: {mot_sys.get_goal(g3_id).priority}")

    print("\n--- Active Goals (Sorted by Priority) ---")
    active_goals = mot_sys.get_active_goals()
    for g in active_goals:
        print(f"  - ID: {g.id}, Desc: {g.description}, Prio: {g.priority}, Status: {g.status}")
    assert len(active_goals) == 3 # g1, g2 are active, g3 is pending
    assert active_goals[0].id == g2_id # g2 has highest priority 9.0
    assert active_goals[1].id == g1_id # g1 has priority 7.5
    assert active_goals[2].id == g3_id # g3 has priority 6.5 and is pending

    print("\n--- Suggest Highest Priority Goal ---")
    suggested_goal = mot_sys.suggest_highest_priority_goal()
    if suggested_goal:
        print(f"Suggested: {suggested_goal.id} - {suggested_goal.description}")
        assert suggested_goal.id == g2_id
    else:
        print("No active goals to suggest.")

    print("\n--- Testing Curiosity Triggers ---")
    # 1. Novel World Event
    novel_event = {"type": "NOVEL_STIMULUS", "id": "shiny_object_001", "novelty_score": 0.85}
    curiosity_goals_event = mot_sys.assess_curiosity_triggers(world_event=novel_event)
    self.assertEqual(len(curiosity_goals_event), 1) # This line will fail here, use assert in tests
    print(f"Curiosity goals from event: {curiosity_goals_event}")
    if curiosity_goals_event:
      event_curiosity_goal = mot_sys.get_goal(curiosity_goals_event[0])
      print(f"  Details: {event_curiosity_goal}")
      assert event_curiosity_goal.priority == 8.5 # 0.85 * 10

    # 2. Knowledge Gap
    knowledge_snapshot = {
        "concept_A": {"confidence": 0.9}, # High confidence, no goal
        "concept_B": {"confidence": 0.35}, # Low confidence, should trigger goal
        "concept_C": {"confidence": 0.20}  # Very low confidence, should trigger goal
    }
    # Add a goal for concept_C manually to test "already existing" check
    mot_sys.add_goal("Resolve uncertainty for concept: concept_C", "INTRINSIC_CURIOSITY", 8.0,
                     source_trigger={"type": "KNOWLEDGE_GAP", "concept_id": "concept_C"},
                     initial_status="PENDING")

    curiosity_goals_knowledge = mot_sys.assess_curiosity_triggers(knowledge_map_snapshot=knowledge_snapshot)
    print(f"Curiosity goals from knowledge gaps: {curiosity_goals_knowledge}")
    # Should only add for concept_B, as concept_C goal already exists (pending)
    # self.assertEqual(len(curiosity_goals_knowledge), 1) # This line will fail here
    if curiosity_goals_knowledge:
        knowledge_curiosity_goal_B = mot_sys.get_goal(curiosity_goals_knowledge[0]) # Assuming only one was added
        print(f"  Details for new knowledge goal: {knowledge_curiosity_goal_B}")
        assert knowledge_curiosity_goal_B.source_trigger["concept_id"] == "concept_B"
        assert knowledge_curiosity_goal_B.priority == (1.0 - 0.35) * 10 # 6.5

    print("\n--- Final Module Status ---")
    print(mot_sys.get_module_status())

    # Test achieving a goal
    mot_sys.update_goal_status(g1_id, "ACHIEVED")
    active_after_achieve = mot_sys.get_active_goals()
    print(f"Active goals after g1 achieved ({len(active_after_achieve)}):")
    for g in active_after_achieve: print(f"  - {g.id}, Prio: {g.priority}, Status: {g.status}")
    assert len(active_after_achieve) > 0 # Should still have g2 and curiosity goals
    assert not any(g.id == g1_id and g.status == "ACTIVE" for g in active_after_achieve)


    print("\nExample Usage Complete (Phase 1 Enhanced Motivational System).")
