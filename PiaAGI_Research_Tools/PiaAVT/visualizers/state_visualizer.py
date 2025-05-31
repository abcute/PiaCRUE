# PiaAGI_Hub/PiaAVT/visualizers/state_visualizer.py
"""
Provides functionalities for creating textual visualizations of agent states.

This module defines the `StateVisualizer` class, which is designed to take
structured dictionary data (typically from a log entry's 'data' field) and
format it into human-readable textual summaries. This is useful for inspecting
complex internal states of an agent, such as its current goals or the contents
of its working memory, without needing graphical displays.

The methods often expect input data to follow certain structural conventions
to produce meaningful output.
"""
from typing import List, Dict, Any, Optional # List is not used in this file, but kept for consistency if it was intended for future use.
import json

class StateVisualizer:
    """
    Generates textual representations of various aspects of an agent's state.

    This class offers methods to format complex dictionary data into structured
    and human-readable strings. It's particularly useful for displaying snapshots
    of an agent's internal components like goals or working memory based on
    log data.
    """

    def __init__(self):
        """
        Initializes the StateVisualizer.
        Currently, no specific configuration is required at initialization.
        Future enhancements might include options for output formatting or verbosity.
        """
        # Future: Initialize with configuration for output formats, etc.
        pass

    def format_dict_as_text(self,
                            state_dict: Dict[str, Any],
                            title: str = "State Details",
                            indent: int = 2) -> str:
        """
        Formats a dictionary into a human-readable, pretty-printed string.

        This method uses JSON dumping with indentation for a structured view.
        It's a general utility for displaying any dictionary-based state information.

        Args:
            state_dict (Dict[str, Any]): The dictionary to format.
            title (str): A title for the formatted output section.
            indent (int): The indentation level for the JSON pretty printing.

        Returns:
            str: A string containing the formatted dictionary, prefixed with the title.
                 Returns a message indicating no data if `state_dict` is empty or None.
        """
        if not state_dict: # Handles None or empty dict
            return f"{title}: (No data provided or empty state)"

        header = f"--- {title} ---"
        try:
            # Pretty print JSON for a nice, readable dictionary structure
            formatted_state = json.dumps(state_dict, indent=indent, sort_keys=True, default=str)
        except TypeError as e:
            formatted_state = f"Could not serialize state to JSON: {e}\nRaw state: {str(state_dict)}"

        return f"{header}\n{formatted_state}\n{'-' * len(header)}"

    def visualize_current_goals(self,
                                goals_log_entry_data: Optional[Dict[str, Any]],
                                title: str = "Current Agent Goals") -> str:
        """
        Creates a textual summary of an agent's current goals.

        This method expects `goals_log_entry_data` to be a dictionary, typically
        from a log entry's 'data' field, with specific keys:
        - "active_goals" (List[Dict]): A list of currently active goals. Each goal
          dictionary might have keys like "id", "description", "priority", "status".
        - "goal_hierarchy" (Optional[Dict]): A dictionary representing parent-child
          relationships between goals (e.g., {"parent_id": ["child_id1", "child_id2"]}).

        Args:
            goals_log_entry_data (Optional[Dict[str, Any]]): The dictionary containing
                goal information. If None or malformed, a message indicating this
                will be returned.
            title (str): A title for the textual visualization.

        Returns:
            str: A formatted string summarizing the agent's goals.
        """
        if not goals_log_entry_data or not isinstance(goals_log_entry_data.get("active_goals"), list):
            return self.format_dict_as_text(state_dict={}, title=f"{title} (No valid goal data)")

        output_lines = [f"--- {title} ---"]

        active_goals = goals_log_entry_data.get("active_goals", [])
        if not active_goals:
            output_lines.append("No active goals.")
        else:
            output_lines.append("Active Goals:")
            for i, goal in enumerate(active_goals):
                goal_desc = f"  {i+1}. ID: {goal.get('id', 'N/A')}"
                goal_desc += f"\n     Description: {goal.get('description', 'N/A')}"
                goal_desc += f"\n     Priority: {goal.get('priority', 'N/A')}"
                goal_desc += f"\n     Status: {goal.get('status', 'N/A')}"
                output_lines.append(goal_desc)

        goal_hierarchy = goals_log_entry_data.get("goal_hierarchy")
        if isinstance(goal_hierarchy, dict) and goal_hierarchy:
            output_lines.append("\nGoal Hierarchy:")
            for parent_goal, sub_goals in goal_hierarchy.items():
                output_lines.append(f"  Parent: {parent_goal} -> Sub-goals: {', '.join(sub_goals) if sub_goals else 'None'}")

        output_lines.append(f"{'-' * len(title) * 2}") # Footer
        return "\n".join(output_lines)

    def visualize_working_memory(self,
                                 wm_log_entry_data: Optional[Dict[str, Any]],
                                 title: str = "Working Memory State") -> str:
        """
        Creates a textual summary of an agent's working memory (WM) contents.

        This method expects `wm_log_entry_data` to be a dictionary, typically from a
        log entry's 'data' field, with potential keys like:
        - "active_elements" (List[Dict]): A list of items currently in WM. Each item
          dictionary might have keys like "id", "content", "salience", "type".
        - "central_executive_focus" (Optional[str]): ID of the element currently in focus.
        - "capacity_used_percent" (Optional[float]): Percentage of WM capacity utilized.
        Other fields in `wm_log_entry_data` will be displayed as additional details.

        Args:
            wm_log_entry_data (Optional[Dict[str, Any]]): The dictionary containing
                WM information. If None or malformed, a message indicating this
                will be returned.
            title (str): A title for the textual visualization.

        Returns:
            str: A formatted string summarizing the working memory state.
        """
        if not wm_log_entry_data: # Handles None or empty dict
             return self.format_dict_as_text(state_dict={}, title=f"{title} (No valid WM data)")

        output_lines = [f"--- {title} ---"]

        active_elements = wm_log_entry_data.get("active_elements", [])
        if active_elements and isinstance(active_elements, list):
            output_lines.append("Active Elements:")
            for i, el in enumerate(active_elements):
                el_desc = f"  {i+1}. ID: {el.get('id', 'N/A')}"
                el_desc += f"\n     Content: {str(el.get('content', 'N/A'))[:100]}" # Truncate long content
                if len(str(el.get('content', ''))) > 100:
                    el_desc += "..."
                el_desc += f"\n     Salience: {el.get('salience', 'N/A')}"
                el_desc += f"\n     Type: {el.get('type', 'N/A')}"
                output_lines.append(el_desc)
        else:
            output_lines.append("No active elements or data malformed.")

        focus = wm_log_entry_data.get("central_executive_focus")
        if focus:
            output_lines.append(f"\nCentral Executive Focus: {focus}")

        capacity = wm_log_entry_data.get("capacity_used_percent")
        if capacity is not None:
            output_lines.append(f"Capacity Used: {capacity}%")

        # For any other fields, use the generic dict formatter
        other_data = {k: v for k, v in wm_log_entry_data.items() if k not in ["active_elements", "central_executive_focus", "capacity_used_percent"]}
        if other_data:
            output_lines.append("\nAdditional WM Details:")
            output_lines.append(json.dumps(other_data, indent=2, default=str))

        output_lines.append(f"{'-' * len(title) * 2}") # Footer
        return "\n".join(output_lines)

# Example Usage (primarily for demonstration or direct script testing)
# This section will typically not be run when PiaAVT is used as a library.
if __name__ == "__main__":
    visualizer = StateVisualizer()

    # --- Generic Dictionary Example ---
    sample_state = {
        "module_name": "PiaCML.Emotion",
        "parameters": {"learning_rate": 0.01, "decay_factor": 0.99},
        "current_emotion": {"valence": 0.6, "arousal": 0.3, "dominant": "joy"},
        "history_size": 100
    }
    print(visualizer.format_dict_as_text(sample_state, title="Emotion Module State"))
    print("\n" + "="*50 + "\n")

    # --- Goals Visualization Example ---
    goals_data = {
        "active_goals": [
            {"id": "g1", "description": "Achieve world peace by Friday", "priority": 0.99, "status": "active", "complexity": "very_high"},
            {"id": "g2", "description": "Find matching socks", "priority": 0.5, "status": "active", "complexity": "low"},
            {"id": "g3", "description": "Understand AGI", "priority": 0.9, "status": "pending_resources"}
        ],
        "goal_hierarchy": {"g1": ["sg1.1_diplomacy", "sg1.2_logistics"], "g3": ["sg3.1_read_papers", "sg3.2_run_sims"]},
        "last_updated": "2024-01-15T11:00:00Z"
    }
    print(visualizer.visualize_current_goals(goals_data))
    print("\n" + "="*50 + "\n")

    no_goals_data = {"active_goals": []}
    print(visualizer.visualize_current_goals(no_goals_data, title="Goals (None Active)"))
    print("\n" + "="*50 + "\n")

    # --- Working Memory Visualization Example ---
    wm_data = {
        "active_elements": [
            {"id": "p01", "content": {"type": "image_percept", "features": [0.1,0.2,0.9]}, "salience": 0.85, "type": "percept", "timestamp": "T1"},
            {"id": "ltm05", "content": "Concept: 'Cat' - related to 'Feline', 'Pet'", "salience": 0.77, "type": "retrieval", "timestamp": "T2"},
            {"id": "goal_ctx", "content": "Current goal: Identify animal in image", "salience": 0.9, "type": "context", "timestamp": "T0"}
        ],
        "central_executive_focus": "p01",
        "capacity_used_percent": 75.2,
        "recent_operations": ["retrieve_concept_Cat", "compare_features_p01_Cat"]
    }
    print(visualizer.visualize_working_memory(wm_data))
    print("\n" + "="*50 + "\n")

    empty_wm_data = {"active_elements": [], "capacity_used_percent": 0}
    print(visualizer.visualize_working_memory(empty_wm_data, title="Working Memory (Empty)"))

```
