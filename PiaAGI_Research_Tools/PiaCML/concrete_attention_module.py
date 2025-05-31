from abc import ABC, abstractmethod # Keep for BaseAttentionModule import if it also imports them
from typing import Any, List, Dict, Optional

try:
    from .base_attention_module import BaseAttentionModule
except ImportError:
    # Fallback for scenarios where the relative import might fail
    from base_attention_module import BaseAttentionModule

class ConcreteAttentionModule(BaseAttentionModule):
    """
    A concrete implementation of the BaseAttentionModule.
    This implementation uses a simple dictionary to store the current attentional focus
    and applies basic rule-based filtering and load management.
    """
    def __init__(self):
        self._current_focus: Optional[Any] = None
        self._current_priority: float = 0.0
        self._active_filters: List[str] = []
        self._cognitive_load_level: float = 0.0
        print("ConcreteAttentionModule initialized.")

    def direct_attention(self, focus_target: Any, priority: float, context: Dict[str, Any] = None) -> bool:
        """Directs attention to a new target if priority is high enough or focus is None."""
        print(f"ConcreteAttentionModule: Attempting to direct attention to '{focus_target}' with priority {priority}.")
        # Simple logic: always shift if new priority is higher, or if no current focus.
        if self._current_focus is None or priority >= self._current_priority:
            self._current_focus = focus_target
            self._current_priority = priority
            # Example: context might influence active_filters
            if context and context.get('type') == 'top-down' and 'filter_low_salience' not in self._active_filters:
                # self._active_filters.append('filter_low_salience') # Example filter
                pass
            print(f"ConcreteAttentionModule: Attention directed to '{self._current_focus}' with priority {self._current_priority}.")
            return True
        print(f"ConcreteAttentionModule: Attention NOT shifted. Current focus '{self._current_focus}' (priority {self._current_priority}) retained.")
        return False

    def filter_information(self, information_stream: List[Dict[str, Any]], current_focus: Any = None) -> List[Dict[str, Any]]:
        """Filters information based on a simple relevance check to the current focus (if any)."""
        effective_focus = current_focus if current_focus is not None else self._current_focus
        print(f"ConcreteAttentionModule: Filtering {len(information_stream)} items based on focus: '{effective_focus}'.")
        if not effective_focus:
            return information_stream # No focus, no filtering

        filtered_stream = []
        for item in information_stream:
            # Extremely simple relevance: item must have a 'tags' list containing the focus string
            # or a 'content' string containing the focus string.
            # This is a placeholder for more sophisticated relevance checking.
            is_relevant = False
            if isinstance(effective_focus, str):
                if 'tags' in item and isinstance(item['tags'], list) and effective_focus in item['tags']:
                    is_relevant = True
                elif 'content' in item and isinstance(item['content'], str) and effective_focus in item['content']:
                    is_relevant = True
                elif item.get('id') == effective_focus: # Allow focus on item ID
                    is_relevant = True

            if is_relevant:
                filtered_stream.append(item)

        print(f"ConcreteAttentionModule: Filtered stream contains {len(filtered_stream)} items.")
        return filtered_stream

    def manage_cognitive_load(self, current_load: float, capacity_thresholds: Dict[str, float]) -> Dict[str, Any]:
        """Manages cognitive load by adjusting internal state or suggesting actions."""
        self._cognitive_load_level = current_load
        print(f"ConcreteAttentionModule: Managing cognitive load. Current: {current_load}, Thresholds: {capacity_thresholds}")

        action_taken = {'action': 'none', 'details': 'Load within acceptable limits.'}

        if current_load >= capacity_thresholds.get('overload', 0.9):
            action_taken = {'action': 'reduce_focus_strictness', 'details': 'Cognitive overload detected. Suggested narrowing attention or reducing task parallelism.'}
            # Example: self._active_filters.append('strict_filtering_on_overload')
            print(f"ConcreteAttentionModule: Overload detected. Action: {action_taken}")
        elif current_load >= capacity_thresholds.get('optimal', 0.7):
            action_taken = {'action': 'maintain_focus', 'details': 'Optimal load. Maintaining current attention strategy.'}
            print(f"ConcreteAttentionModule: Optimal load. Action: {action_taken}")

        return action_taken

    def get_attentional_state(self) -> Dict[str, Any]:
        """Returns the current attentional state."""
        state = {
            'current_focus': self._current_focus,
            'current_priority': self._current_priority,
            'active_filters': list(self._active_filters), # Return a copy
            'cognitive_load_level': self._cognitive_load_level,
            'module_type': 'ConcreteAttentionModule'
        }
        print(f"ConcreteAttentionModule: Returning state: {state}")
        return state

if __name__ == '__main__':
    attention_module = ConcreteAttentionModule()

    # Initial state
    print("\n--- Initial State ---")
    print(attention_module.get_attentional_state())

    # Direct attention
    print("\n--- Directing Attention ---")
    attention_module.direct_attention(focus_target="ProjectAlpha", priority=0.8, context={'type': 'top-down'})
    print(attention_module.get_attentional_state())
    attention_module.direct_attention(focus_target="UrgentTaskOmega", priority=0.7) # Lower priority
    print(attention_module.get_attentional_state()) # Should not change
    attention_module.direct_attention(focus_target="UrgentTaskOmega", priority=0.9) # Higher priority
    print(attention_module.get_attentional_state()) # Should change

    # Filter information
    print("\n--- Filtering Information ---")
    stream = [
        {'id': 'item1', 'content': "Details about ProjectAlpha.", 'tags': ["ProjectAlpha", "research"]},
        {'id': 'item2', 'content': "Random information.", 'tags': ["general"]},
        {'id': 'item3', 'content': "Update on UrgentTaskOmega.", 'tags': ["UrgentTaskOmega", "critical"]},
        {'id': 'item4', 'content': "Another detail for ProjectAlpha research.", 'tags': ["ProjectAlpha"]},
    ]
    # Focus is "UrgentTaskOmega"
    filtered = attention_module.filter_information(stream)
    print("Filtered items (focus UrgentTaskOmega):", [item['id'] for item in filtered])

    # Filter with explicit focus override
    filtered_override = attention_module.filter_information(stream, current_focus="ProjectAlpha")
    print("Filtered items (focus ProjectAlpha override):", [item['id'] for item in filtered_override])


    # Manage cognitive load
    print("\n--- Managing Cognitive Load ---")
    thresholds = {'optimal': 0.6, 'overload': 0.85}
    print(attention_module.manage_cognitive_load(current_load=0.5, capacity_thresholds=thresholds))
    print(attention_module.get_attentional_state())
    print(attention_module.manage_cognitive_load(current_load=0.75, capacity_thresholds=thresholds)) # Optimal
    print(attention_module.get_attentational_state())
    print(attention_module.manage_cognitive_load(current_load=0.9, capacity_thresholds=thresholds)) # Overload
    print(attention_module.get_attentional_state())

    print("\nExample Usage Complete.")
