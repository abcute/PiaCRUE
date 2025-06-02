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
        self._active_filters: List[Dict[str, Any]] = []
        self._cognitive_load_level: float = 0.0
        print("ConcreteAttentionModule initialized.")

    def direct_attention(self, focus_target: Any, priority: float, context: Dict[str, Any] = None) -> bool:
        """Directs attention to a new target if priority is high enough or focus is None."""
        print(f"ConcreteAttentionModule: Attempting to direct attention to '{focus_target}' with priority {priority}.")

        if context:
            if context.get('clear_filters'):
                self._active_filters = []
                print("ConcreteAttentionModule: Cleared active filters due to context.")
            if 'add_filter' in context and isinstance(context['add_filter'], dict):
                self._active_filters.append(context['add_filter'])
                print(f"ConcreteAttentionModule: Added filter: {context['add_filter']}.")

        # Simple logic: always shift if new priority is higher, or if no current focus.
        if self._current_focus is None or priority >= self._current_priority:
            self._current_focus = focus_target
            self._current_priority = priority
            print(f"ConcreteAttentionModule: Attention directed to '{self._current_focus}' with priority {self._current_priority}.")
            return True
        print(f"ConcreteAttentionModule: Attention NOT shifted. Current focus '{self._current_focus}' (priority {self._current_priority}) retained.")
        return False

    def filter_information(self, information_stream: List[Dict[str, Any]], current_focus: Any = None) -> List[Dict[str, Any]]:
        """Filters information based on a simple relevance check to the current focus (if any) and then applies active filters."""
        effective_focus = current_focus if current_focus is not None else self._current_focus
        print(f"ConcreteAttentionModule: Filtering {len(information_stream)} items based on focus: '{effective_focus}'. Active filters: {self._active_filters}")

        # Initial focus-based filtering
        if effective_focus:
            focused_stream = []
            for item in information_stream:
                is_relevant = False
                if isinstance(effective_focus, str):
                    if 'tags' in item and isinstance(item['tags'], list) and effective_focus in item['tags']:
                        is_relevant = True
                    elif 'content' in item and isinstance(item['content'], str) and effective_focus in item['content']:
                        is_relevant = True
                    elif item.get('id') == effective_focus:
                        is_relevant = True
                if is_relevant:
                    focused_stream.append(item)
        else:
            focused_stream = list(information_stream) # Work on a copy if no focus filtering

        # Apply active filters progressively
        if not self._active_filters:
            print(f"ConcreteAttentionModule: No active filters. Filtered stream (by focus only) contains {len(focused_stream)} items.")
            return focused_stream

        stream_after_active_filters = list(focused_stream) # Start with focus-filtered (or all if no focus)
        for f_idx, active_filter in enumerate(self._active_filters):
            print(f"ConcreteAttentionModule: Applying filter {f_idx + 1}/{len(self._active_filters)}: {active_filter}")
            next_filtered_stream = []
            filter_type = active_filter.get('type')
            filter_key = active_filter.get('key')

            for item in stream_after_active_filters:
                passes_filter = False
                if filter_type == 'value_equals':
                    filter_value = active_filter.get('value')
                    if item.get(filter_key) == filter_value:
                        passes_filter = True
                elif filter_type == 'value_gt':
                    filter_threshold = active_filter.get('threshold')
                    if item.get(filter_key, 0) > filter_threshold:
                        passes_filter = True
                elif filter_type == 'tag_present':
                    filter_tag = active_filter.get('tag')
                    if filter_tag in item.get('tags', []):
                        passes_filter = True
                else:
                    # If filter type is unknown or not implemented, item passes by default
                    # Or, you could choose to make it fail: passes_filter = False
                    print(f"ConcreteAttentionModule: Unknown filter type '{filter_type}', item passes by default.")
                    passes_filter = True

                if passes_filter:
                    next_filtered_stream.append(item)
            stream_after_active_filters = next_filtered_stream
            print(f"ConcreteAttentionModule: Stream size after filter {active_filter}: {len(stream_after_active_filters)}")

        print(f"ConcreteAttentionModule: Filtered stream (focus + active filters) contains {len(stream_after_active_filters)} items.")
        return stream_after_active_filters

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
