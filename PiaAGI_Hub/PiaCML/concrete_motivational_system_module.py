from typing import Any, Dict, List, Optional, Union
import uuid

try:
    from .base_motivational_system_module import BaseMotivationalSystemModule
except ImportError:
    from base_motivational_system_module import BaseMotivationalSystemModule

class ConcreteMotivationalSystemModule(BaseMotivationalSystemModule):
    """
    A basic, concrete implementation of the BaseMotivationalSystemModule.
    This version manages a list of goals, each represented as a dictionary
    with properties like id, description, type (intrinsic/extrinsic), priority,
    and status (e.g., 'pending', 'active', 'achieved', 'failed').
    """

    def __init__(self):
        self._goals: List[Dict[str, Any]] = []
        self._motivation_state: Dict[str, Any] = {
            "overall_drive_level": 0.7, # Conceptual
            "current_focus_theme": "general" # Conceptual
        }
        print("ConcreteMotivationalSystemModule initialized.")

    def _generate_goal_id(self) -> str:
        return f"goal_{str(uuid.uuid4())[:8]}"

    def manage_goals(self, action: str, goal_data: Optional[Dict[str, Any]] = None) -> Union[bool, str, List[Dict[str, Any]], None]:
        """
        Manages goals: add, remove, update status, or list goals.
        'goal_data' structure for 'add': {'description': str, 'type': str ('intrinsic'/'extrinsic'), 'priority': float, 'source': str (optional)}
        'goal_data' for 'update_status': {'id': str, 'status': str ('pending', 'active', 'achieved', 'failed', 'paused')}
        'goal_data' for 'remove': {'id': str}
        """
        print(f"ConcreteMotSys: Managing goals. Action: '{action}', Data: {goal_data}")

        if action == "add":
            if not goal_data or not all(k in goal_data for k in ['description', 'type', 'priority']):
                print("ConcreteMotSys: Add failed - missing required goal data.")
                return False # Or raise error

            new_goal_id = self._generate_goal_id()
            new_goal = {
                "id": new_goal_id,
                "description": goal_data['description'],
                "type": goal_data['type'], # 'intrinsic' or 'extrinsic'
                "priority": float(goal_data['priority']), # 0.0 (lowest) to 1.0 (highest)
                "status": goal_data.get('status', 'pending'), # e.g., pending, active, achieved, failed
                "source": goal_data.get('source', 'internal'),
                "details": goal_data.get('details', {}) # For any other info
            }
            self._goals.append(new_goal)
            # Sort goals by priority after adding, highest first
            self._goals.sort(key=lambda g: g.get('priority', 0.0), reverse=True)
            print(f"ConcreteMotSys: Added goal '{new_goal_id}': {new_goal['description']}")
            return new_goal_id

        elif action == "remove":
            if not goal_data or 'id' not in goal_data:
                print("ConcreteMotSys: Remove failed - no goal ID provided.")
                return False
            goal_id_to_remove = goal_data['id']
            original_len = len(self._goals)
            self._goals = [g for g in self._goals if g['id'] != goal_id_to_remove]
            removed = len(self._goals) < original_len
            if removed:
                print(f"ConcreteMotSys: Removed goal '{goal_id_to_remove}'.")
            else:
                print(f"ConcreteMotSys: Goal '{goal_id_to_remove}' not found for removal.")
            return removed

        elif action == "update_status":
            if not goal_data or not all(k in goal_data for k in ['id', 'status']):
                print("ConcreteMotSys: Update status failed - missing ID or new status.")
                return False
            goal_id_to_update = goal_data['id']
            new_status = goal_data['status']
            for goal in self._goals:
                if goal['id'] == goal_id_to_update:
                    goal['status'] = new_status
                    print(f"ConcreteMotSys: Updated status of goal '{goal_id_to_update}' to '{new_status}'.")
                    return True
            print(f"ConcreteMotSys: Goal '{goal_id_to_update}' not found for status update.")
            return False

        elif action == "list_all":
            return list(self._goals) # Return a copy

        print(f"ConcreteMotSys: Unknown action '{action}' for manage_goals.")
        return None


    def get_active_goals(self, N: int = 0, min_priority: float = 0.0) -> List[Dict[str, Any]]:
        """
        Returns active goals, optionally filtered by N (top N) and min_priority.
        Goals are already sorted by priority (highest first).
        """
        active_goals = [g for g in self._goals if g['status'] == 'active' and g.get('priority', 0.0) >= min_priority]

        if N > 0:
            return active_goals[:N]
        return active_goals

    def update_motivation_state(self, new_state_info: Dict[str, Any]) -> bool:
        """
        Updates the conceptual motivation state (e.g., overall drive, focus theme).
        Placeholder in this basic version.
        """
        print(f"ConcreteMotSys: update_motivation_state called with: {new_state_info}. (Placeholder)")
        if 'overall_drive_level' in new_state_info:
            self._motivation_state['overall_drive_level'] = new_state_info['overall_drive_level']
        if 'current_focus_theme' in new_state_info:
            self._motivation_state['current_focus_theme'] = new_state_info['current_focus_theme']
        return True

    def get_module_status(self) -> Dict[str, Any]:
        """Returns the current status of the Motivational System Module."""
        status_counts = {}
        for goal in self._goals:
            status_counts[goal['status']] = status_counts.get(goal['status'], 0) + 1

        return {
            "module_type": "ConcreteMotivationalSystemModule",
            "total_goals": len(self._goals),
            "goals_by_status": status_counts,
            "current_motivation_state": dict(self._motivation_state) # shallow copy
        }

if __name__ == '__main__':
    mot_sys = ConcreteMotivationalSystemModule()

    # Initial Status
    print("\n--- Initial Status ---")
    print(mot_sys.get_module_status())

    # Add goals
    print("\n--- Adding Goals ---")
    goal1_id = mot_sys.manage_goals(action="add", goal_data={
        "description": "Explore new dataset X",
        "type": "intrinsic",
        "priority": 0.8,
        "source": "curiosity_drive"
    })
    goal2_id = mot_sys.manage_goals(action="add", goal_data={
        "description": "Complete user request Y",
        "type": "extrinsic",
        "priority": 0.9,
        "source": "user_command"
    })
    goal3_id = mot_sys.manage_goals(action="add", goal_data={
        "description": "Refactor CML code",
        "type": "intrinsic",
        "priority": 0.7,
        "source": "self_improvement"
    })
    print("All goals after adding:", mot_sys.manage_goals(action="list_all"))
    print("Status after adding:", mot_sys.get_module_status())


    # Update goal status
    print("\n--- Updating Goal Status ---")
    mot_sys.manage_goals(action="update_status", goal_data={"id": goal2_id, "status": "active"})
    mot_sys.manage_goals(action="update_status", goal_data={"id": goal1_id, "status": "active"})
    mot_sys.manage_goals(action="update_status", goal_data={"id": goal3_id, "status": "paused"})
    print("Status after updates:", mot_sys.get_module_status())

    # Get active goals
    print("\n--- Getting Active Goals ---")
    active_goals = mot_sys.get_active_goals()
    print(f"Active goals ({len(active_goals)}):")
    for g in active_goals: print(f"  - {g['id']}: {g['description']} (Priority: {g['priority']})")
    assert len(active_goals) == 2
    assert active_goals[0]['id'] == goal2_id # Should be highest priority (0.9)

    top_1_active = mot_sys.get_active_goals(N=1)
    print("Top 1 active goal:", top_1_active[0]['description'] if top_1_active else "None")
    assert top_1_active[0]['id'] == goal2_id

    active_high_priority = mot_sys.get_active_goals(min_priority=0.85)
    print(f"Active goals with min_priority 0.85 ({len(active_high_priority)}):")
    assert len(active_high_priority) == 1
    assert active_high_priority[0]['id'] == goal2_id


    # Update motivation state (placeholder)
    print("\n--- Updating Motivation State ---")
    mot_sys.update_motivation_state({"overall_drive_level": 0.9, "current_focus_theme": "dataset_exploration"})
    print("Status after motivation state update:", mot_sys.get_module_status())

    # Remove a goal
    print("\n--- Removing a Goal ---")
    mot_sys.manage_goals(action="remove", goal_data={"id": goal3_id})
    print("Status after removing goal3:", mot_sys.get_module_status())
    assert mot_sys.get_module_status()['total_goals'] == 2

    print("\nExample Usage Complete.")
