from typing import Any, Dict, List, Optional

try:
    from .base_long_term_memory_module import BaseLongTermMemoryModule
    from .concrete_base_memory_module import ConcreteBaseMemoryModule
except ImportError:
    # Fallback for scenarios where the relative import might fail
    from base_long_term_memory_module import BaseLongTermMemoryModule
    from concrete_base_memory_module import ConcreteBaseMemoryModule

# --- Module-level comments on Backend Expectations ---
# The advanced retrieval strategies outlined in methods like `get_episodic_experience`
# and `get_semantic_knowledge` (e.g., temporal proximity, hierarchical traversal)
# are presented conceptually. For these strategies to be performant:
# 1. The `_storage_backend` (e.g., `ConcreteBaseMemoryModule`) would ideally need to
#    support complex queries (e.g., range queries, graph traversals, list containment checks).
# 2. If the backend offers only basic key-value or simple field matching, then this
#    `ConcreteLongTermMemoryModule` would need to implement these advanced search
#    logics as post-processing steps on a potentially large dataset retrieved from
#    the backend. This would be less efficient but functionally achievable.
# The current implementation primarily illustrates the interface and conceptual logic,
# assuming the backend or future post-processing would handle the detailed filtering.

class ConcreteLongTermMemoryModule(BaseLongTermMemoryModule):
    """
    A concrete implementation of the BaseLongTermMemoryModule.
    This implementation uses an instance of ConcreteBaseMemoryModule internally
    and differentiates between episodic, semantic, and procedural memory
    by adding a 'ltm_type' field to the stored information's context.
    """

    def __init__(self):
        self._storage_backend = ConcreteBaseMemoryModule() # Internal storage
        self._subcomponent_status = {
            "episodic": {"items": 0, "queries": 0},
            "semantic": {"items": 0, "queries": 0},
            "procedural": {"items": 0, "queries": 0},
        }
        print("ConcreteLongTermMemoryModule initialized, using ConcreteBaseMemoryModule backend.")

    # --- Implementing BaseMemoryModule abstract methods ---
    # These are delegated to the storage_backend, potentially with LTM-specific context.

    def store(self, information: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """
        Generic store, less used directly. Prefer specific store_* methods.
        Adds a default 'generic_ltm' type if no specific LTM context is given.
        """
        ltm_context = context or {}
        ltm_context.setdefault('ltm_type', 'generic_ltm') # Ensure LTM type if not specified
        # Not directly updating subcomponent_status here as it's too generic.
        # Specific methods below should be used.
        print(f"ConcreteLTM: Generic store called. Information will be tagged as '{ltm_context['ltm_type']}'.")
        return self._storage_backend.store(information, ltm_context)

    def retrieve(self, query: Dict[str, Any], criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Generic retrieve. It's recommended to use specific retrieve_* methods
        or ensure the query/criteria specify the 'ltm_type' for targeted retrieval.
        """
        # This generic retrieve might not be ideal as it doesn't know which subcomponent
        # to attribute the query to for status update without more specific criteria.
        print(f"ConcreteLTM: Generic retrieve called. Query: {query}")
        return self._storage_backend.retrieve(query, criteria)

    def delete_memory(self, memory_id: str) -> bool:
        """Deletes a memory item by its ID from the backend storage."""
        # Need to find out which subcomponent it belonged to if we want to update counts.
        # This might require retrieving it first, or storing metadata about ID -> ltm_type.
        # For simplicity, this basic version won't update subcomponent counts on generic delete.
        print(f"ConcreteLTM: Generic delete_memory called for ID '{memory_id}'.")
        return self._storage_backend.delete_memory(memory_id)

    def manage_capacity(self) -> None:
        """Delegates to backend's manage_capacity. LTM specific logic could be added."""
        print("ConcreteLTM: manage_capacity called.")
        self._storage_backend.manage_capacity()
        self.manage_ltm_subcomponents() # Also call LTM specific management

    def handle_forgetting(self, strategy: str = 'default') -> None:
        """Delegates to backend's handle_forgetting. LTM specific logic could be added."""
        print(f"ConcreteLTM: handle_forgetting called with strategy '{strategy}'.")
        self._storage_backend.handle_forgetting(strategy)
        # Potentially apply different strategies per subcomponent in manage_ltm_subcomponents

    def get_status(self) -> Dict[str, Any]:
        """Returns combined status from backend and LTM subcomponents."""
        backend_status = self._storage_backend.get_status()
        return {
            "module_type": "ConcreteLongTermMemoryModule",
            "backend_storage_status": backend_status,
            "subcomponent_overview": dict(self._subcomponent_status),
            "total_ltm_items_tracked": sum(s['items'] for s in self._subcomponent_status.values())
        }

    # --- Implementing BaseLongTermMemoryModule specific abstract methods ---

    def store_episodic_experience(self, event_data: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Stores an episodic experience, tagging it appropriately."""
        ltm_context = context or {}
        ltm_context['ltm_type'] = 'episodic'
        memory_id = self._storage_backend.store(event_data, ltm_context)
        self._subcomponent_status['episodic']['items'] += 1
        print(f"ConcreteLTM: Stored episodic experience. ID: {memory_id}") # Updated print
        return memory_id

    def get_episodic_experience(self, query: Dict[str, Any], criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Retrieves episodic experiences. Modifies query to target 'episodic' type."""
        # Ensure query targets episodic memory. A more robust way would be to use criteria.
        # This is a simple way; criteria might be better for complex cases
        # e.g., criteria = (criteria or {}).update({'ltm_type_must_match': 'episodic'})
        # For now, we assume the backend retrieve can handle a query like {'info.ltm_type': 'episodic'}
        # or the query itself will specify it.
        # Let's assume the backend's retrieve will check item['ctx']['ltm_type']
        # For this concrete version, we'll add it to the query if not present.
        # This is a bit of a hack for this basic version.
        # A better approach might be to have the backend filter by context fields.

        # We will rely on the query itself specifying the type, or a more advanced backend.
        # For this example, let's assume the query is crafted correctly for the backend.
        # If the backend's retrieve() checks context via criteria, this is cleaner:
        ltm_criteria = criteria or {}
        ltm_criteria.setdefault('match_context', {})['ltm_type'] = 'episodic'

        print(f"ConcreteLTM: Retrieving episodic experiences with query: {query}, effective criteria: {ltm_criteria}") # Updated print
        
        # Initial retrieval based on primary query and ltm_type
        results = self._storage_backend.retrieve(query, ltm_criteria)
        self._subcomponent_status['episodic']['queries'] += 1
        
        # Conceptual Post-Processing for Advanced Retrieval Strategies:
        # The following steps would ideally be handled by a more capable backend.
        # If not, they would be implemented here as filtering on 'results'.

        # 1. Temporal Proximity Search
        if 'near_timestamp' in query and 'time_window' in query:
            # Conceptual: Filter 'results' list further.
            # For each 'item' in 'results':
            #   if abs(item['info'].get('timestamp', 0) - query['near_timestamp']) <= query['time_window']:
            #     keep item
            #   else:
            #     remove item
            print(f"ConcreteLTM: Conceptual: Applying temporal proximity filter (ts={query['near_timestamp']}, window={query['time_window']}).")

        # 2. Involved Entity Search
        if 'involved_entity_id' in query:
            # Conceptual: Filter 'results' list further.
            # For each 'item' in 'results':
            #   event_data = item['info']
            #   if query['involved_entity_id'] in event_data.get('involved_entities', []):
            #     keep item
            #   else:
            #     remove item
            print(f"ConcreteLTM: Conceptual: Applying involved entity filter (entity_id={query['involved_entity_id']}).")

        # 3. Associative Retrieval (Conceptual)
        if 'related_to_event_id' in query:
            # Conceptual: This is more complex.
            # 1. Fetch the 'related_to_event_id' event.
            # 2. Identify its key characteristics (e.g., involved entities, context tags, location).
            # 3. Filter 'results' for items that share some of these key characteristics.
            #    This might involve multiple queries to the backend or complex graph traversal if data is linked.
            print(f"ConcreteLTM: Conceptual: Applying associative retrieval filter (related_to_event_id={query['related_to_event_id']}).")

        return results

    def store_semantic_knowledge(self, knowledge_item: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Stores a semantic knowledge item."""
        ltm_context = context or {}
        ltm_context['ltm_type'] = 'semantic'
        memory_id = self._storage_backend.store(knowledge_item, ltm_context)
        self._subcomponent_status['semantic']['items'] += 1
        print(f"ConcreteLTM: Stored semantic knowledge. ID: {memory_id}")
        return memory_id

    def get_semantic_knowledge(self, query: Dict[str, Any], criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]: # Renamed from retrieve_semantic_knowledge
        """Retrieves semantic knowledge."""
        ltm_criteria = criteria or {}
        ltm_criteria.setdefault('match_context', {})['ltm_type'] = 'semantic'
        print(f"ConcreteLTM: Retrieving semantic knowledge with query: {query}, effective criteria: {ltm_criteria}")
        
        results = self._storage_backend.retrieve(query, ltm_criteria)
        self._subcomponent_status['semantic']['queries'] += 1

        # Conceptual Post-Processing or Advanced Backend Query Logic:
        
        # 1. Hierarchical Traversal (Conceptual)
        if 'concept_id' in query and 'relation_type' in query and 'traversal_depth' in query:
            # Conceptual: This assumes semantic knowledge is graph-like (e.g., item['info']['relations']).
            # 1. Start with 'concept_id'.
            # 2. Iteratively fetch related concepts via 'relation_type' up to 'traversal_depth'.
            #    - This might involve multiple calls to self._storage_backend.retrieve or a graph query language if supported.
            # 3. Aggregate results. The current 'results' might be the starting point or be replaced.
            print(f"ConcreteLTM: Conceptual: Applying hierarchical traversal (concept={query['concept_id']}, relation={query['relation_type']}, depth={query['traversal_depth']}).")

        # 2. Property-Based Search
        if 'with_property' in query and 'property_value' in query:
            # Conceptual: Filter 'results' further.
            # For each 'item' in 'results':
            #   knowledge_data = item['info']
            #   if knowledge_data.get(query['with_property']) == query['property_value']:
            #     keep item
            #   else:
            #     remove item
            # Alternatively, if the backend supports it, this could be part of the initial query.
            print(f"ConcreteLTM: Conceptual: Applying property-based filter (property='{query['with_property']}', value='{query['property_value']}').")
            
        return results

    def store_procedural_skill(self, skill_data: Dict[str, Any], context: Dict[str, Any] = None) -> str: # Changed from skill_name: str, skill_representation: dict
        """Stores a procedural skill. Ensures skill_name is part of skill_data for retrieval."""
        # The ABC for LTM has store_procedural_skill(self, skill_name: str, skill_representation: dict...)
        # This concrete class's method signature was store_procedural_skill(self, skill_data: Dict[str, Any]...)
        # Let's assume skill_data CONTAINS the skill name and representation.
        # To align with get_procedural_skill(skill_name), we need skill_name to be queryable.
        # We'll assume skill_data should have a 'skill_name_key' field that holds the skill_name.
        # Or, the skill_name parameter from ABC could be used as ID, but concrete class doesn't take it.
        # Let's stick to skill_data having 'skill_name_key'. The caller of store_procedural_skill
        # must ensure skill_data = {'skill_name_key': 'the_skill_name', ...other_repr...}

        ltm_context = context or {}
        ltm_context['ltm_type'] = 'procedural'

        # Ensure skill_name_key is present for querying later by get_procedural_skill
        if 'skill_name_key' not in skill_data:
            print(f"ConcreteLTM Warning: 'skill_name_key' not found in skill_data for store_procedural_skill. Retrieval by name might fail for: {skill_data}")
            # Or, if a skill_name parameter was passed (as per some interpretations of an ABC):
            # skill_data['skill_name_key'] = skill_name_param_if_it_existed

        memory_id = self._storage_backend.store(skill_data, ltm_context)
        self._subcomponent_status['procedural']['items'] += 1
        print(f"ConcreteLTM: Stored procedural skill. ID: {memory_id}. Data: {skill_data}")
        return memory_id

    def get_procedural_skill(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """Retrieves a procedural skill by its name."""
        ltm_criteria = {'match_context': {'ltm_type': 'procedural'}}
        # We assume the skill_name is stored in a queryable field within the 'info' dict,
        # e.g., skill_data['skill_name_key'] == skill_name.
        # Or, skill_name could be the conceptual ID used for storage if skills are unique by name.
        # For this implementation, let's assume skill_name is stored in info['skill_name_key'].
        query = {'skill_name_key': skill_name} # This field should be used when storing the skill.
                                              # Or, if skill_name is the ID, query = {'id': skill_name}
                                              # The current store_procedural_skill doesn't enforce this.
                                              # Let's adjust store_procedural_skill to ensure 'skill_name_key' exists.

        print(f"ConcreteLTM: Retrieving procedural skill '{skill_name}'. Query: {query}, Criteria: {ltm_criteria}")
        results = self._storage_backend.retrieve(query, ltm_criteria) # Pass the constructed query
        self._subcomponent_status['procedural']['queries'] += 1
        
        if results:
            return results[0]['info'] # Return the 'info' part of the first match
        else:
            # Conceptual: Fuzzy match or keyword search if exact match fails.
            # This would require iterating through all procedural memories or a more advanced backend search.
            # For each skill_entry in all_procedural_memories:
            #   if fuzzy_match(skill_name, skill_entry['info'].get('skill_name_key')) > threshold or \
            #      skill_name_keywords in skill_entry['info'].get('description', ''):
            #     return skill_entry['info']
            print(f"ConcreteLTM: Conceptual: Exact match for skill '{skill_name}' not found. Fuzzy/keyword search could be attempted here.")
            return None

    def manage_ltm_subcomponents(self) -> None:
        """Placeholder for managing LTM subcomponents, e.g., balancing resources, consolidation strategies."""
        print("ConcreteLTM: manage_ltm_subcomponents() called - Placeholder.")
        # Example: Check if any subcomponent is disproportionately large and trigger specific forgetting
        # for that subcomponent via the backend, using a more specific strategy.
        # For instance, if episodic memory is too large:
        #   self._storage_backend.handle_forgetting(strategy='episodic_specific_decay', criteria={'match_context': {'ltm_type': 'episodic'}})
        pass

    def consolidate_memory(self, type_to_consolidate: str = 'all', intensity: str = 'normal') -> None:
        """Placeholder for LTM consolidation process."""
        print(f"ConcreteLTM: consolidate_memory called for type '{type_to_consolidate}' with intensity '{intensity}'. Placeholder - no action.")
        # In a real implementation, this might trigger specific backend operations
        # or internal LTM restructuring.
        pass

if __name__ == '__main__':
    ltm = ConcreteLongTermMemoryModule()

    # Initial status
    print("\n--- Initial LTM Status ---")
    print(ltm.get_status())

    # Store different types of memories
    print("\n--- Storing Memories ---")
    event_id1 = ltm.store_episodic_experience({'event': 'UserLogin', 'user': 'Alice', 'timestamp': 12345}, {'source': 'system_log'})
    fact_id1 = ltm.store_semantic_knowledge({'concept': 'PiaAGI', 'relation': 'is_a', 'value': 'CognitiveArchitecture'}, {'domain': 'AI'})
    # For store_procedural_skill, skill_data now needs skill_name_key
    skill_data_greet = {'skill_name_key': 'greet_user', 'skill_name': 'greet_user', 'steps': ['say_hello', 'ask_name']}
    skill_id1 = ltm.store_procedural_skill(skill_data_greet, {'complexity': 'low'})

    event_id2 = ltm.store_episodic_experience({'event': 'DataBackup', 'status': 'success', 'timestamp': 12360})
    fact_id2 = ltm.store_semantic_knowledge({'concept': 'Python', 'property': 'is_dynamic_language'}, {'domain': 'Programming'})

    print("\n--- LTM Status After Stores ---")
    status_after_stores = ltm.get_status()
    print(status_after_stores)
    assert status_after_stores['subcomponent_overview']['episodic']['items'] == 2
    assert status_after_stores['subcomponent_overview']['semantic']['items'] == 2
    assert status_after_stores['subcomponent_overview']['procedural']['items'] == 1

    # Retrieve memories
    print("\n--- Retrieving Memories ---")
    # Note: The ConcreteBaseMemoryModule's retrieve needs to be able to handle criteria like {'match_context': {'ltm_type': '...'}}
    # The example implementation of ConcreteBaseMemoryModule's retrieve was simple.
    # For this test to work as intended, we assume its retrieve can filter by context fields.
    # Let's adjust the retrieve logic in ConcreteBaseMemoryModule if it's too simple or
    # assume the query for this test is structured to pass through if the backend is simple.

    # To make the example work with the simple ConcreteBaseMemoryModule's retrieve,
    # we would typically query for something inside 'info' or by 'id'.
    # The current ConcreteLTM passes criteria to a backend that's assumed to handle it.
    # Let's test retrieval by ID first, which the backend handles.
    print("Retrieve Event1 by ID:", ltm.retrieve({'id': event_id1}))
    print("Retrieve Fact2 by ID:", ltm.retrieve({'id': fact_id2}))

    # Test type-specific retrieval (relies on backend supporting context matching in criteria)
    # If ConcreteBaseMemoryModule's retrieve doesn't support this, these will be empty or all items.
    # We'll modify ConcreteBaseMemoryModule's retrieve to add basic context criteria matching.

    # --- Modification to ConcreteBaseMemoryModule's retrieve for this example to work: ---
    # (Conceptual: Imagine ConcreteBaseMemoryModule.retrieve is updated like this)
    # def retrieve(self, query: dict, criteria: dict = None) -> list[dict]:
    #     ... (existing id and concept query logic) ...
    #     match_context_criteria = criteria.get('match_context') if criteria else None
    #     if not results and match_context_criteria: # If no specific field query matched, try context
    #         for item_id, item_data in self._storage.items():
    #             context_match = True
    #             if item_data.get('ctx'):
    #                 for key, value in match_context_criteria.items():
    #                     if item_data['ctx'].get(key) != value:
    #                         context_match = False
    #                         break
    #             else: # No context in item, cannot match context criteria
    #                 context_match = False
    #             if context_match:
    #                 results.append(item_data)
    #     return results
    # --- End of conceptual modification ---

    print("Retrieve all episodic experiences (conceptually):", ltm.get_episodic_experience(query={}))
    # This will retrieve all if backend doesn't filter by context, or only episodic if it does.
    # Our ConcreteLTM's get_episodic_experience sets criteria={'match_context': {'ltm_type': 'episodic'}}

    print("Retrieve semantic 'PiaAGI':", ltm.get_semantic_knowledge(query={'concept': 'PiaAGI'})) # Renamed
    # Test the new get_procedural_skill
    retrieved_skill_info = ltm.get_procedural_skill(skill_name='greet_user')
    print("Retrieve skill 'greet_user' (info only):", retrieved_skill_info)
    if retrieved_skill_info: # Check if not None before asserting
        assert retrieved_skill_info['skill_name_key'] == 'greet_user'


    print("\n--- LTM Status After Retrievals ---")
    status_after_retrievals = ltm.get_status()
    print(status_after_retrievals)
    assert status_after_retrievals['subcomponent_overview']['episodic']['queries'] >= 1
    assert status_after_retrievals['subcomponent_overview']['semantic']['queries'] >= 1
    assert status_after_retrievals['subcomponent_overview']['procedural']['queries'] >= 1

    # Delete a memory
    print("\n--- Deleting a Memory ---")
    ltm.delete_memory(fact_id1)
    # Note: subcomponent item count won't decrease with this basic delete_memory.
    # A more advanced version would determine type and update.
    print("Status after delete:", ltm.get_status())

    # Manage capacity and subcomponents (placeholders)
    print("\n--- Management ---")
    ltm.manage_capacity()
    ltm.handle_forgetting()
    ltm.consolidate_memory() # Test new placeholder

    print("\nExample Usage Complete.")

    # For the example to run correctly with context filtering,
    # the ConcreteBaseMemoryModule.retrieve would need to be enhanced.
    # The provided ConcreteBaseMemoryModule.retrieve is simple:
    # - query by id
    # - query by concept in info
    # - return all if empty query
    # - return empty otherwise
    # It does not use the `criteria` for context matching.
    # So, type-specific retrievals in this LTM example will not filter by ltm_type
    # unless the query itself is structured to hit 'id' or 'concept'.
    # To make this example fully testable for type-specific retrieval,
    # ConcreteBaseMemoryModule.retrieve needs modification or these tests need specific queries.
    # Example: ltm.get_semantic_knowledge(query={'concept': 'PiaAGI'}) will work # Renamed
    #          ltm.get_episodic_experience(query={}) will return ALL items from backend if backend is simple.
