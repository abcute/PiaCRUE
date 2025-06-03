from typing import Any, Dict, List, Optional, Union
import uuid

try:
    from .base_working_memory_module import BaseWorkingMemoryModule
except ImportError:
    from base_working_memory_module import BaseWorkingMemoryModule

class ConcreteWorkingMemoryModule(BaseWorkingMemoryModule):
    """
    A concrete implementation of the BaseWorkingMemoryModule.
    This implementation manages a list of items in a workspace with a defined capacity.
    It uses simple strategies for adding, removing, and focusing on items.
    The BaseMemoryModule methods (store, retrieve, delete) are adapted for a
    transient, ID-based workspace rather than a persistent LTM-like backend.
    Includes Proof-of-Concept hooks for dynamic capacity configuration.
    """

    DEFAULT_CAPACITY = 7 # Typical psychological estimate for WM capacity (e.g., Miller's Law)

    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        self._workspace: List[Dict[str, Any]] = [] # Items are dicts, e.g., {'id': unique_id, 'content': data, 'salience': 0.5}
        self._capacity: int = capacity # This remains as the primary operational capacity for now.
        self._current_focus_id: Optional[str] = None # ID of the item currently in focus
        self._item_counter: int = 0 # For generating simple unique IDs within WM

        # Architectural Maturation Hook: Dynamic Capacity Parameters
        self.capacity_params: Dict[str, int] = {
            "max_items": capacity, # Initialize max_items with the constructor's capacity
            "max_item_complexity": 5 # Default complexity value
        }
        print(f"ConcreteWorkingMemoryModule initialized with operational capacity {self._capacity} and params {self.capacity_params}.")

    def set_capacity_parameters(self, params: Dict[str, int]) -> None:
        """
        Sets new capacity parameters for working memory.
        For this PoC, it just stores the parameters.
        Future implementations would make WM behavior (e.g., _capacity) adhere to these.
        Example params: {"max_items": 20, "max_item_complexity": 10}
        """
        if not isinstance(params, dict):
            print("Error: params must be a dictionary.") # Or raise TypeError
            return

        updated_any = False
        for key, value in params.items():
            if key in self.capacity_params:
                if isinstance(value, int) and value >= 0:
                    self.capacity_params[key] = value
                    updated_any = True
                    # If 'max_items' is updated, conceptually, self._capacity might also be updated here
                    # For this PoC, we'll keep them separate to show the hook mechanism.
                    # if key == "max_items":
                    #     self._capacity = value
                    #     print(f"ConcreteWM: Operational capacity _capacity also updated to {self._capacity} via max_items.")
                else:
                    print(f"Warning: Invalid value '{value}' for '{key}'. Must be a non-negative integer. Not updated.")
            else:
                 print(f"Warning: Unknown capacity parameter '{key}'. Not updated.") # Strict checking

        if updated_any:
            print(f"ConcreteWM: capacity_params updated to: {self.capacity_params}")

    def get_capacity_parameters(self) -> Dict[str, int]:
        """Returns a copy of the current capacity parameters of working memory."""
        return self.capacity_params.copy()

    def _generate_wm_id(self) -> str:
        self._item_counter += 1
        return f"wm_item_{self._item_counter}"

    # --- BaseMemoryModule methods adapted for WM ---

    def store(self, information: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """
        Stores/adds information to the working memory workspace.
        This is equivalent to add_item_to_workspace. Assigns a temporary WM ID.
        If WM is full, it might replace the least salient item (rudimentary).
        """
        wm_id = self._generate_wm_id()
        salience = context.get('salience', 0.5) if context else 0.5
        item = {'id': wm_id, 'content': information, 'salience': salience, 'context': context or {}}

        if len(self._workspace) >= self._capacity:
            self.manage_workspace_capacity_and_coherence(new_item_salience=salience) # Make space

        if len(self._workspace) < self._capacity: # Check again if space was made
            self._workspace.append(item)
            print(f"ConcreteWM: Stored item '{wm_id}' with salience {salience}. Current size: {len(self._workspace)}/{self._capacity}")
            return wm_id
        else:
            print(f"ConcreteWM: Store failed. Workspace full for item '{wm_id}'. Size: {len(self._workspace)}/{self._capacity}")
            # In a more robust system, this might raise an error or return a specific failure code/ID.
            return "error_workspace_full"


    def retrieve(self, query: Dict[str, Any], criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Retrieves items from WM.
        Query by 'id', or if 'content_query' is in query, do a simple search in item content.
        """
        results: List[Dict[str, Any]] = []
        query_id = query.get('id')
        content_query = query.get('content_query') # e.g. {'key': 'name', 'value': 'Pia'}

        if query_id:
            for item in self._workspace:
                if item['id'] == query_id:
                    results.append(item)
                    break # IDs are unique
        elif content_query and isinstance(content_query, dict) and 'key' in content_query and 'value' in content_query:
            key_to_search = content_query['key']
            value_to_search = content_query['value']
            for item in self._workspace:
                if isinstance(item['content'], dict) and item['content'].get(key_to_search) == value_to_search:
                    results.append(item)
        elif not query: # Empty query returns all
             return list(self._workspace)

        print(f"ConcreteWM: Retrieved {len(results)} items for query: {query}")
        return results

    def delete_memory(self, memory_id: str) -> bool:
        """Removes an item by its WM ID. Equivalent to remove_item_from_workspace."""
        return self.remove_item_from_workspace(memory_id)

    def manage_capacity(self) -> None:
        """Generic capacity management, calls the more specific WM version."""
        self.manage_workspace_capacity_and_coherence()

    def handle_forgetting(self, strategy: str = 'default') -> None:
        """
        For WM, forgetting is often implicit due to capacity limits (displacement)
        or explicit removal. This could implement decay of salience over time.
        Placeholder for now, actual removal happens in manage_workspace_capacity_and_coherence.
        """
        print(f"ConcreteWM: handle_forgetting called with strategy '{strategy}'. (Placeholder - primary mechanism is capacity management)")
        if strategy == 'decay_salience':
            for item in self._workspace:
                item['salience'] = max(0, item['salience'] * 0.9) # Decay by 10%
            # Sort by salience to ensure least salient are removed first if needed
            self._workspace.sort(key=lambda x: x.get('salience', 0.0))


    def get_status(self) -> Dict[str, Any]:
        """Returns the current status of the Working Memory."""
        return {
            "module_type": "ConcreteWorkingMemoryModule",
            "current_size": len(self._workspace),
            "capacity": self._capacity,
            "current_focus_id": self._current_focus_id,
            "items_summary": [{'id': item['id'], 'salience': item.get('salience')} for item in self._workspace]
        }

    # --- BaseWorkingMemoryModule specific abstract methods ---

    def add_item_to_workspace(self, item_content: Any, salience: float = 0.5, context: Dict[str, Any] = None) -> str:
        """Adds an item to the workspace. This is the primary way to add to WM."""
        # This method is essentially what 'store' now does.
        return self.store(item_content if isinstance(item_content, dict) else {'data': item_content},
                          context={'salience': salience, **(context or {})})


    def remove_item_from_workspace(self, item_id: str) -> bool:
        """Removes a specific item from the workspace by its WM ID."""
        original_len = len(self._workspace)
        self._workspace = [item for item in self._workspace if item['id'] != item_id]
        removed = len(self._workspace) < original_len
        if removed:
            if self._current_focus_id == item_id:
                self._current_focus_id = None # Clear focus if focused item is removed
            print(f"ConcreteWM: Removed item '{item_id}'. Current size: {len(self._workspace)}/{self._capacity}")
        else:
            print(f"ConcreteWM: Item '{item_id}' not found for removal.")
        return removed

    def get_workspace_contents(self) -> List[Dict[str, Any]]:
        """Returns all items currently in the workspace."""
        return list(self._workspace) # Return a copy

    def get_active_focus(self) -> Optional[Dict[str, Any]]:
        """Returns the item currently in active focus, if any."""
        if self._current_focus_id:
            for item in self._workspace:
                if item['id'] == self._current_focus_id:
                    return item
        return None

    def set_active_focus(self, item_id: str) -> bool:
        """Sets a specific item in the workspace as the active focus."""
        for item in self._workspace:
            if item['id'] == item_id:
                self._current_focus_id = item_id
                # Optionally boost salience of focused item
                item['salience'] = item.get('salience', 0.5) + 0.1 # Boost a little
                self._workspace.sort(key=lambda x: x.get('salience', 0.0)) # Re-sort
                print(f"ConcreteWM: Active focus set to item '{item_id}'.")
                return True
        print(f"ConcreteWM: Item '{item_id}' not found in workspace to set focus.")
        return False

    def manage_workspace_capacity_and_coherence(self, new_item_salience: Optional[float] = None) -> None:
        """
        Manages WM capacity by removing least salient items if over capacity.
        If new_item_salience is provided, it tries to make space for an item of that salience.
        Coherence aspects (e.g., resolving contradictions) are placeholder here.
        """
        print(f"ConcreteWM: Managing workspace capacity. Current size: {len(self._workspace)}/{self._capacity}")
        self._workspace.sort(key=lambda x: x.get('salience', 0.0)) # Sort by salience, lowest first

        removed_count = 0
        # How many items to remove?
        # If making space for a new item, remove one if full.
        # If just managing, remove items until at or below capacity.
        num_to_remove = 0
        if new_item_salience is not None and len(self._workspace) >= self._capacity:
             # Try to remove one item if its salience is less than the new item's
            if self._workspace and self._workspace[0].get('salience', 0.0) < new_item_salience:
                num_to_remove = 1
        else:
            num_to_remove = len(self._workspace) - self._capacity

        if num_to_remove > 0:
            for _ in range(min(num_to_remove, len(self._workspace))): # Ensure we don't pop from empty list
                removed_item = self._workspace.pop(0) # Remove least salient
                removed_count +=1
                print(f"ConcreteWM: Removed item '{removed_item['id']}' (salience: {removed_item.get('salience')}) due to capacity management.")
                if self._current_focus_id == removed_item['id']:
                    self._current_focus_id = None

        if removed_count > 0:
            print(f"ConcreteWM: Capacity management removed {removed_count} items. New size: {len(self._workspace)}")

        # Placeholder for coherence management
        # print("ConcreteWM: Coherence management placeholder.")
        pass

if __name__ == '__main__':
    wm = ConcreteWorkingMemoryModule(capacity=3)
    print("--- Initial WM Status ---")
    print(wm.get_status())

    # Add items (using specific WM method)
    print("\n--- Adding Items ---")
    id1 = wm.add_item_to_workspace({'type': 'goal', 'content': 'Plan dinner'}, salience=0.7)
    id2 = wm.add_item_to_workspace({'type': 'percept', 'content': 'Fridge is empty'}, salience=0.9)
    id3 = wm.add_item_to_workspace({'type': 'reminder', 'content': 'Call mom'}, salience=0.5)
    print(wm.get_status())

    # Add another item, should trigger capacity management
    id4_attempt = wm.add_item_to_workspace({'type': 'distraction', 'content': 'Squirrel!'}, salience=0.6) # Higher than 'Call mom'
    print(f"ID4 attempt result: {id4_attempt}") # Should succeed if 'Call mom' (0.5) was removed
    print(wm.get_status())

    # Check if 'Call mom' (id3) is gone, and id4 is present
    found_id3 = any(item['id'] == id3 for item in wm.get_workspace_contents())
    found_id4 = any(item['id'] == id4_attempt for item in wm.get_workspace_contents())
    print(f"Found id3 ('Call mom')?: {found_id3}") # Should be False
    print(f"Found id4 ('Squirrel!')?: {found_id4}") # Should be True


    # Set and get focus
    print("\n--- Focus Management ---")
    wm.set_active_focus(id2) # Focus on 'Fridge is empty'
    focused_item = wm.get_active_focus()
    print("Focused item:", focused_item)
    if focused_item:
        assert focused_item['id'] == id2

    # Retrieve items
    print("\n--- Retrieving Items ---")
    print("All items:", wm.retrieve({}))
    print("Item id2:", wm.retrieve({'id': id2}))
    print("Items with content_query {'key': 'type', 'value': 'goal'}:", wm.retrieve({'content_query': {'key': 'type', 'value': 'goal'}}))


    # Remove item
    print("\n--- Removing Item ---")
    wm.remove_item_from_workspace(id1) # Remove 'Plan dinner'
    print(wm.get_status())
    assert wm.get_active_focus()['id'] == id2 # Focus should persist if not removed item

    # Test forgetting (salience decay)
    print("\n--- Testing Forgetting (Salience Decay) ---")
    # Manually check salience before (from id2, id4_attempt)
    for item in wm.get_workspace_contents(): print(f"Item {item['id']} salience: {item['salience']}")
    wm.handle_forgetting(strategy='decay_salience')
    print("Workspace after salience decay:")
    for item in wm.get_workspace_contents(): print(f"Item {item['id']} salience: {item['salience']}")

    # Add one more to trigger capacity based on new saliences
    id5 = wm.add_item_to_workspace({'type': 'new_high_salience', 'content': 'Important!'}, salience=0.99)
    print(wm.get_status())


    print("\nExample Usage Complete.")
