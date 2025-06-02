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
    """

    DEFAULT_CAPACITY = 7 # Typical psychological estimate for WM capacity (e.g., Miller's Law)

    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        self._workspace: List[Dict[str, Any]] = [] # Items are dicts, e.g., {'id': unique_id, 'content': data, 'salience': 0.5}
        self._capacity: int = capacity
        self._current_focus_id: Optional[str] = None # ID of the item currently in focus
        self._item_counter: int = 0 # For generating simple unique IDs within WM
        self._last_alloc_priority: Optional[Dict] = None
        self._last_coord_attempt: Optional[Dict] = None
        print(f"ConcreteWorkingMemoryModule initialized with capacity {self._capacity}.")

    def _generate_wm_id(self) -> str:
        self._item_counter += 1
        return f"wm_item_{self._item_counter}"

    # --- BaseMemoryModule methods adapted for WM ---

    def store(self, information: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """
        Stores/adds information to the working memory workspace.
        Assigns a temporary WM ID.
        If WM is full, it might replace the least salient item.
        """
        wm_id = self._generate_wm_id()
        salience = context.get('salience', 0.5) if context else 0.5
        item = {'id': wm_id, 'content': information, 'salience': salience, 'context': context or {}}

        if len(self._workspace) >= self._capacity:
            self.manage_workspace_capacity_and_coherence(new_item_salience=salience) # Make space

        if len(self._workspace) < self._capacity: # Check again if space was made
            self._workspace.append(item)
            self._workspace.sort(key=lambda x: x.get('salience', 0.0)) # Keep sorted by salience (lowest first)
            print(f"ConcreteWM: Stored item '{wm_id}' with salience {salience}. Current size: {len(self._workspace)}/{self._capacity}")
            return wm_id
        else:
            print(f"ConcreteWM: Store failed. Workspace full for item '{wm_id}'. Size: {len(self._workspace)}/{self._capacity}")
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
        print(f"ConcreteWM: handle_forgetting called with strategy '{strategy}'. (Placeholder - primary mechanism is capacity management)")
        if strategy == 'decay_salience':
            for item in self._workspace:
                item['salience'] = max(0, item['salience'] * 0.9)
            self._workspace.sort(key=lambda x: x.get('salience', 0.0))


    def get_status(self) -> Dict[str, Any]:
        """Returns the current status of the Working Memory."""
        return {
            "module_type": "ConcreteWorkingMemoryModule",
            "current_size": len(self._workspace),
            "capacity": self._capacity,
            "current_focus_id": self._current_focus_id,
            "items_summary": [{'id': item['id'], 'salience': item.get('salience')} for item in self._workspace],
            "last_alloc_priority": self._last_alloc_priority,
            "last_coord_attempt": self._last_coord_attempt
        }

    # --- BaseWorkingMemoryModule specific abstract methods ---

    def add_item_to_workspace(self, item_content: Any, salience: float = 0.5, context: Dict[str, Any] = None) -> bool:
        """Adds an item to the workspace. Returns True on success, False on failure (e.g., full)."""
        # Ensure item_content is a dict for the store method
        content_dict = item_content if isinstance(item_content, dict) else {'data': item_content}
        # Prepare context for the store method, including salience
        store_context = {'salience': salience, **(context or {})}

        wm_id_or_error = self.store(content_dict, store_context)

        if wm_id_or_error != "error_workspace_full":
            print(f"ConcreteWM (add_item_to_workspace): Successfully added item. ID: {wm_id_or_error}")
            return True
        else:
            print(f"ConcreteWM (add_item_to_workspace): Failed to add item, workspace likely full or other store error.")
            return False

    def remove_item_from_workspace(self, item_id: str) -> bool:
        """Removes a specific item from the workspace by its WM ID."""
        original_len = len(self._workspace)
        self._workspace = [item for item in self._workspace if item['id'] != item_id]
        removed = len(self._workspace) < original_len
        if removed:
            if self._current_focus_id == item_id:
                self._current_focus_id = None
            print(f"ConcreteWM: Removed item '{item_id}'. Current size: {len(self._workspace)}/{self._capacity}")
        else:
            print(f"ConcreteWM: Item '{item_id}' not found for removal.")
        return removed

    def get_workspace_contents(self) -> List[Dict[str, Any]]:
        """Returns all items currently in the workspace."""
        return list(self._workspace)

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
                item['salience'] = item.get('salience', 0.5) + 0.1
                self._workspace.sort(key=lambda x: x.get('salience', 0.0))
                print(f"ConcreteWM: Active focus set to item '{item_id}'.")
                return True
        print(f"ConcreteWM: Item '{item_id}' not found in workspace to set focus.")
        return False

    def manage_workspace_capacity_and_coherence(self, new_item_salience: Optional[float] = None) -> None:
        print(f"ConcreteWM: Managing workspace capacity. Current size: {len(self._workspace)}/{self._capacity}")
        self._workspace.sort(key=lambda x: x.get('salience', 0.0))

        removed_count = 0
        num_to_remove = 0
        if new_item_salience is not None and len(self._workspace) >= self._capacity:
            if self._workspace and self._workspace[0].get('salience', 0.0) < new_item_salience:
                num_to_remove = 1
        else: # General capacity check, not necessarily for a new item
            num_to_remove = len(self._workspace) - self._capacity

        if num_to_remove > 0:
            for _ in range(min(num_to_remove, len(self._workspace))):
                removed_item = self._workspace.pop(0)
                removed_count +=1
                print(f"ConcreteWM: Removed item '{removed_item['id']}' (salience: {removed_item.get('salience')}) due to capacity management.")
                if self._current_focus_id == removed_item['id']:
                    self._current_focus_id = None

        if removed_count > 0:
            print(f"ConcreteWM: Capacity management removed {removed_count} items. New size: {len(self._workspace)}")
        pass

    # --- New placeholder methods from ABC ---
    def update_item_in_workspace(self, item_id: Any, new_content: Any = None, new_context: Dict[str, Any] = None) -> bool:
        """Updates an existing item within the workspace."""
        for item in self._workspace:
            if item['id'] == item_id:
                if new_content is not None:
                    item['content'] = new_content if isinstance(new_content, dict) else {'data': new_content}
                if new_context is not None:
                    item_ctx = item.get('context', {})
                    item_ctx.update(new_context)
                    item['context'] = item_ctx
                    if 'salience' in new_context:
                        item['salience'] = new_context['salience']
                        self._workspace.sort(key=lambda x: x.get('salience', 0.0))
                print(f"ConcreteWM: Updated item '{item_id}'.")
                return True
        print(f"ConcreteWM: Item '{item_id}' not found for update.")
        return False

    def clear_workspace(self) -> None:
        """Clears all items from the working memory workspace."""
        print("ConcreteWM: Clearing workspace.")
        self._workspace = []
        self._current_focus_id = None
        self._item_counter = 0

    def get_cognitive_load(self) -> float:
        """Returns an estimate of the current cognitive load on Working Memory."""
        if self._capacity == 0:
            return 1.0
        load = len(self._workspace) / self._capacity
        print(f"ConcreteWM: Current cognitive load: {load:.2f}")
        return load

    def allocate_attentional_resources(self, task_priority: Dict[str, Any]) -> bool:
        """Simulates Central Executive: allocating attention based on task_priority."""
        print(f"ConcreteWM (CE Placeholder): Allocating attentional resources based on: {task_priority}. No specific action taken.")
        self._last_alloc_priority = task_priority
        return True

    def coordinate_modules(self, task_goal: str, required_modules: List[str]) -> Dict[str, Any]:
        """Simulates Central Executive: coordinating modules for a task_goal."""
        print(f"ConcreteWM (CE Placeholder): Coordinating for goal '{task_goal}' using modules: {required_modules}. No specific action taken.")
        task_id = f"coord_task_{str(uuid.uuid4())[:8]}"
        self._last_coord_attempt = {'task_goal': task_goal, 'modules': required_modules, 'task_id': task_id }
        return {'status': 'coordination_conceptualized', 'task_id': task_id}

if __name__ == '__main__':
    wm = ConcreteWorkingMemoryModule(capacity=3)
    print("--- Initial WM Status ---")
    print(wm.get_status())

    # Add items (using specific WM method)
    print("\n--- Adding Items ---")
    # Using the new add_item_to_workspace which returns bool
    added1 = wm.add_item_to_workspace({'type': 'goal', 'content': 'Plan dinner'}, salience=0.7)
    added2 = wm.add_item_to_workspace({'type': 'percept', 'content': 'Fridge is empty'}, salience=0.9)
    added3 = wm.add_item_to_workspace({'type': 'reminder', 'content': 'Call mom'}, salience=0.5)
    print(f"Added1: {added1}, Added2: {added2}, Added3: {added3}")
    print(wm.get_status())

    # Add another item, should trigger capacity management
    added4_success = wm.add_item_to_workspace({'type': 'distraction', 'content': 'Squirrel!'}, salience=0.6)
    print(f"Added item for capacity check (should be True if space made): {added4_success}")
    print(wm.get_status())

    # Retrieve item IDs for focus setting (assuming IDs are wm_item_1, wm_item_2 etc.)
    # This is fragile if ID generation changes or items are reordered unpredictably before retrieval for ID
    # A better way would be to get IDs from the store/add method if they were returned or from get_workspace_contents
    # For now, let's assume 'Fridge is empty' (highest salience initially) is wm_item_2 if not displaced
    # and 'Squirrel!' (0.6) displaced 'Call mom' (0.5) and is now wm_item_4

    fridge_item_id = None
    squirrel_item_id = None
    plan_dinner_item_id = None

    for item in wm.get_workspace_contents():
        if isinstance(item['content'], dict) and item['content'].get('content') == 'Fridge is empty':
            fridge_item_id = item['id']
        if isinstance(item['content'], dict) and item['content'].get('content') == 'Squirrel!':
            squirrel_item_id = item['id']
        if isinstance(item['content'], dict) and item['content'].get('content') == 'Plan dinner':
            plan_dinner_item_id = item['id']


    # Set and get focus
    print("\n--- Focus Management ---")
    if fridge_item_id:
        wm.set_active_focus(fridge_item_id)
        focused_item = wm.get_active_focus()
        print("Focused item:", focused_item)
        if focused_item:
            assert focused_item['id'] == fridge_item_id
    else:
        print("Fridge item not found for focus test.")


    # Retrieve items
    print("\n--- Retrieving Items ---")
    print("All items:", wm.retrieve({}))
    if fridge_item_id:
        print(f"Item {fridge_item_id}:", wm.retrieve({'id': fridge_item_id}))
    print("Items with content_query {'key': 'type', 'value': 'goal'}:", wm.retrieve({'content_query': {'key': 'type', 'value': 'goal'}}))


    # Remove item
    print("\n--- Removing Item ---")
    if plan_dinner_item_id:
        wm.remove_item_from_workspace(plan_dinner_item_id)
    print(wm.get_status())
    if fridge_item_id and wm.get_active_focus(): # Check if focus exists
        assert wm.get_active_focus()['id'] == fridge_item_id

    # Test forgetting (salience decay)
    print("\n--- Testing Forgetting (Salience Decay) ---")
    for item in wm.get_workspace_contents(): print(f"Item {item['id']} salience: {item['salience']}")
    wm.handle_forgetting(strategy='decay_salience')
    print("Workspace after salience decay:")
    for item in wm.get_workspace_contents(): print(f"Item {item['id']} salience: {item['salience']}")

    # Add one more to trigger capacity based on new saliences
    added5_success = wm.add_item_to_workspace({'type': 'new_high_salience', 'content': 'Important!'}, salience=0.99)
    print(f"Added item (important): {added5_success}")
    print(wm.get_status())

    # Test new placeholder methods
    print("\n--- Testing New Placeholders ---")
    wm.update_item_in_workspace(squirrel_item_id if squirrel_item_id else "wm_item_4", new_content={'data': 'Super Squirrel!'}, new_context={'salience': 0.95, 'updated_by': 'test'})
    print("Item after update:", wm.retrieve({'id': squirrel_item_id if squirrel_item_id else "wm_item_4"}))

    print(f"Cognitive load: {wm.get_cognitive_load()}")

    wm.allocate_attentional_resources({'task_type': 'urgent_planning', 'priority_score': 0.9})
    wm.coordinate_modules(task_goal="Generate report", required_modules=["LTM", "Planning"])
    print(wm.get_status())

    wm.clear_workspace()
    print("After clear_workspace:", wm.get_status())
    assert wm.get_cognitive_load() == 0.0

    print("\nExample Usage Complete.")
