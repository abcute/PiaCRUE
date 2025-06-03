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
import time # Added import

# --- Module-level comments on Backend Expectations ---
# (Original comments retained for context, but new methods may bypass backend for specific types)
# The advanced retrieval strategies outlined in methods like `get_episodic_experience`
# and `get_semantic_knowledge` (e.g., temporal proximity, hierarchical traversal)
# are presented conceptually. For these strategies to be performant:
# 1. The `_storage_backend` (e.g., `ConcreteBaseMemoryModule`) would ideally need to
#    support complex queries (e.g., range queries, graph traversals, list containment checks).
# 2. If the backend offers only basic key-value or simple field matching, then this
#    `ConcreteLongTermMemoryModule` would need to implement these advanced search
#    logics as post-processing steps on a potentially large dataset retrieved from
#    the backend. This would be less efficient but functionally achievable.
# The Phase 1 enhancements implement direct in-memory structures for episodic and semantic
# memory, bypassing the generic backend for these types to illustrate specific features.

class ConcreteLongTermMemoryModule(BaseLongTermMemoryModule):
    """
    A concrete implementation of the BaseLongTermMemoryModule.
    This version includes Phase 1 enhancements:
    - Direct in-memory list for episodic memory with keyword search.
    - Direct in-memory dictionary-based graph for semantic memory.
    Procedural memory and generic LTM functions may still use the backend.
    """

    def __init__(self):
        self._storage_backend = ConcreteBaseMemoryModule() # For procedural and generic

        # Phase 1 Enhancements: Direct data structures
        self.episodic_memory: List[Dict[str, Any]] = []
        self.next_episode_id: int = 0
        # Semantic memory graph: {"node_id": {"label": "...", "node_type": "...", "properties": {}, "relationships": []}}
        self.semantic_memory_graph: Dict[str, Dict[str, Any]] = {}

        self._subcomponent_status = { # Updated to reflect new structures
            "episodic_list": {"items": 0, "queries": 0},
            "semantic_graph": {"nodes": 0, "edges": 0, "queries": 0},
            "procedural_backend": {"items": 0, "queries": 0}, # Remains backend-based
            "generic_backend": {"items": 0, "queries": 0} # For generic store/retrieve
        }
        print("ConcreteLongTermMemoryModule (Phase 1 Enhanced) initialized.")

    # --- Generic BaseMemoryModule methods (mostly for procedural/other) ---

    def store(self, information: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """
        Generic store, primarily for LTM types not handled by specific structures
        (e.g., procedural if not further specialized, or other future LTM types).
        Tags with 'generic_ltm' if no type is specified.
        """
        ltm_context = context or {}
        ltm_context.setdefault('ltm_type', 'generic_ltm')
        memory_id = self._storage_backend.store(information, ltm_context)

        type_key = ltm_context['ltm_type'] + "_backend" if ltm_context['ltm_type'] in ["procedural", "generic"] else "generic_backend"
        if type_key not in self._subcomponent_status: # Ensure key exists for other types
             self._subcomponent_status[type_key] = {"items": 0, "queries": 0}
        self._subcomponent_status[type_key]['items'] += 1

        print(f"ConcreteLTM: Generic store called. ID: {memory_id}. Tagged as '{ltm_context['ltm_type']}'.")
        return memory_id

    def retrieve(self, query: Dict[str, Any], criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Generic retrieve from the backend storage.
        It's recommended to use specific get_* methods for episodic/semantic.
        """
        print(f"ConcreteLTM: Generic retrieve from backend called. Query: {query}")
        # This generic retrieve might not update specific subcomponent query counts accurately
        # unless criteria specify the ltm_type handled by the backend.
        return self._storage_backend.retrieve(query, criteria)

    def delete_memory(self, memory_id: str) -> bool:
        """
        Deletes a memory item by its ID.
        For Phase 1, this primarily targets the backend. Deleting from new
        episodic/semantic structures would need separate logic or ID scheme.
        """
        # TODO: Extend to check if memory_id refers to an episode or semantic node
        # and remove from those structures if applicable. For now, assumes backend ID.
        print(f"ConcreteLTM: Generic delete_memory for ID '{memory_id}' (assumed backend).")
        was_deleted = self._storage_backend.delete_memory(memory_id)
        # If we knew its type, we could decrement the corresponding _backend status item count.
        return was_deleted

    def manage_capacity(self) -> None:
        """Manages capacity for backend and conceptual for new structures."""
        print("ConcreteLTM: manage_capacity called.")
        self._storage_backend.manage_capacity()
        # Conceptual: Add logic for managing episodic_memory list size (e.g., FIFO, LIFO)
        # Conceptual: Add logic for pruning semantic_memory_graph (e.g., remove isolated nodes)
        self.manage_ltm_subcomponents()

    def handle_forgetting(self, strategy: str = 'default') -> None:
        """Handles forgetting for backend and conceptual for new structures."""
        print(f"ConcreteLTM: handle_forgetting called with strategy '{strategy}'.")
        self._storage_backend.handle_forgetting(strategy)
        # Conceptual: Apply forgetting to self.episodic_memory and self.semantic_memory_graph
        # e.g., if strategy is 'decay_old_episodes', remove old items from self.episodic_memory.

    def get_status(self) -> Dict[str, Any]:
        """Returns combined status, including new direct LTM structures."""
        backend_status = self._storage_backend.get_status()
        self._subcomponent_status["episodic_list"]["items"] = len(self.episodic_memory)
        self._subcomponent_status["semantic_graph"]["nodes"] = len(self.semantic_memory_graph)
        # Edge count for semantic_graph would require iterating through all nodes' relationships.
        edge_count = 0
        for node_data in self.semantic_memory_graph.values():
            edge_count += len(node_data.get("relationships", []))
        self._subcomponent_status["semantic_graph"]["edges"] = edge_count

        return {
            "module_type": "ConcreteLongTermMemoryModule (Phase 1 Enhanced)",
            "backend_storage_status": backend_status,
            "direct_ltm_structures_status": {
                "episodic_memory_count": self._subcomponent_status["episodic_list"]["items"],
                "semantic_graph_nodes": self._subcomponent_status["semantic_graph"]["nodes"],
                "semantic_graph_edges": edge_count,
            },
            "query_counts_overview": dict(self._subcomponent_status),
            # Total items is more complex now (backend + direct structures)
        }

    # --- Phase 1: Episodic Memory Methods (New Implementation) ---

    def add_episode(self, event_description: str, timestamp: Optional[float] = None,
                    associated_data: Optional[Dict[str, Any]] = None,
                    causal_links: Optional[List[str]] = None) -> str:
        """
        Adds a new episode to the in-memory episodic list.

        Args:
            event_description: A string describing the event.
            timestamp: Optional float, uses current time if None.
            associated_data: Optional dictionary of related data.
            causal_links: Optional list of episode_ids this event is causally linked to.

        Returns:
            The generated episode_id.
        """
        actual_timestamp = timestamp if timestamp is not None else time.time()
        episode_id = f"ep_{self.next_episode_id}"

        episode = {
            "episode_id": episode_id,
            "timestamp": actual_timestamp,
            "event_description": event_description,
            "associated_data": associated_data or {},
            "causal_links": causal_links or []
        }
        self.episodic_memory.append(episode)
        self.next_episode_id += 1
        self._subcomponent_status['episodic_list']['items'] = len(self.episodic_memory) # Keep count updated
        print(f"ConcreteLTM: Added episode '{episode_id}': {event_description}")
        return episode_id

    def get_episode(self, episode_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves an episode by its ID from the in-memory list."""
        self._subcomponent_status['episodic_list']['queries'] += 1
        for episode in self.episodic_memory:
            if episode["episode_id"] == episode_id:
                return episode
        return None

    def find_episodes_by_keyword(self, keyword: str,
                                 search_in_description: bool = True,
                                 search_in_associated_data: bool = False) -> List[Dict[str, Any]]:
        """Finds episodes containing a keyword in description or associated data."""
        self._subcomponent_status['episodic_list']['queries'] += 1
        found_episodes: List[Dict[str, Any]] = []
        keyword_lower = keyword.lower()

        for episode in self.episodic_memory:
            match = False
            if search_in_description and keyword_lower in episode["event_description"].lower():
                match = True

            if not match and search_in_associated_data:
                for value in episode["associated_data"].values():
                    if isinstance(value, str) and keyword_lower in value.lower():
                        match = True
                        break

            if match:
                found_episodes.append(episode)
        return found_episodes

    # --- Phase 1: Semantic Memory Graph Methods (New Implementation) ---

    def add_semantic_node(self, node_id: str, label: str, node_type: str,
                          properties: Optional[Dict[str, Any]] = None) -> bool:
        """Adds a node to the in-memory semantic graph."""
        if node_id in self.semantic_memory_graph:
            print(f"ConcreteLTM: Semantic node '{node_id}' already exists. Update if needed or use different ID.")
            return False # Or implement update logic

        self.semantic_memory_graph[node_id] = {
            "label": label,
            "node_type": node_type,
            "properties": properties or {},
            "relationships": [] # List of {"type": str, "target": str, "properties": dict}
        }
        self._subcomponent_status['semantic_graph']['nodes'] = len(self.semantic_memory_graph)
        print(f"ConcreteLTM: Added semantic node '{node_id}' ({label}).")
        return True

    def add_semantic_relationship(self, source_node_id: str, target_node_id: str,
                                  relationship_type: str,
                                  relationship_properties: Optional[Dict[str, Any]] = None) -> bool:
        """Adds a directed relationship between two nodes in the semantic graph."""
        if source_node_id not in self.semantic_memory_graph or \
           target_node_id not in self.semantic_memory_graph:
            print(f"ConcreteLTM: Cannot add relationship. Source ('{source_node_id}') or target ('{target_node_id}') node does not exist.")
            return False

        relationship = {
            "type": relationship_type,
            "target": target_node_id,
            "properties": relationship_properties or {}
        }
        self.semantic_memory_graph[source_node_id]["relationships"].append(relationship)
        # self._subcomponent_status['semantic_graph']['edges'] will be updated by get_status
        print(f"ConcreteLTM: Added relationship from '{source_node_id}' to '{target_node_id}' of type '{relationship_type}'.")
        return True

    def get_semantic_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a node by its ID from the semantic graph."""
        self._subcomponent_status['semantic_graph']['queries'] += 1
        return self.semantic_memory_graph.get(node_id)

    def find_related_nodes(self, node_id: str, relationship_type: Optional[str] = None) -> List[str]:
        """Finds target node IDs related to a given node, optionally filtered by relationship type."""
        self._subcomponent_status['semantic_graph']['queries'] += 1
        node_data = self.get_semantic_node(node_id) # Use own method to count query
        if not node_data:
            return []

        related_node_ids: List[str] = []
        for rel in node_data.get("relationships", []):
            if relationship_type is None or rel["type"] == relationship_type:
                related_node_ids.append(rel["target"])
        return related_node_ids

    def get_semantic_relationships(self, node_id: str, relationship_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves full relationship dictionaries for a given node, optionally filtered by type."""
        self._subcomponent_status['semantic_graph']['queries'] += 1
        node_data = self.get_semantic_node(node_id) # Use own method to count query
        if not node_data:
            return []

        relationships: List[Dict[str, Any]] = []
        for rel in node_data.get("relationships", []):
            if relationship_type is None or rel["type"] == relationship_type:
                relationships.append(rel)
        return relationships

    # --- Original Methods (Potentially Deprecated or Re-routed for Episodic/Semantic) ---
    # For Phase 1, we'll assume calls to these for episodic/semantic should use the new methods.
    # Procedural memory methods will continue to use the backend.

    def store_episodic_experience(self, event_data: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """
        Phase 1: Stores an episodic experience using the new direct in-memory list.
        The 'context' arg is largely for compatibility; timestamp and key data are in event_data.
        """
        print("ConcreteLTM: store_episodic_experience called (Phase 1 - direct list).")
        # Extract relevant fields for add_episode if they are in event_data or context
        description = event_data.get("event_description", str(event_data))
        timestamp = event_data.get("timestamp", (context or {}).get("timestamp"))
        associated_data = event_data.get("associated_data", {k:v for k,v in event_data.items() if k not in ["event_description", "timestamp"]})
        causal_links = event_data.get("causal_links")
        return self.add_episode(description, timestamp, associated_data, causal_links)

    def get_episodic_experience(self, query: Dict[str, Any], criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Phase 1: Retrieves episodic experiences from the new direct in-memory list.
        Simple keyword search for now. 'query' could contain 'keyword'.
        'criteria' is largely ignored for this simplified version.
        """
        print("ConcreteLTM: get_episodic_experience called (Phase 1 - direct list search).")
        keyword = query.get("keyword")
        if keyword:
            # search_in_associated_data can be a conceptual extension via criteria
            search_assoc = (criteria or {}).get("search_in_associated_data", False)
            return self.find_episodes_by_keyword(keyword, search_in_associated_data=search_assoc)
        
        # If no keyword, conceptual: return all or based on other query fields (e.g. episode_id)
        if "episode_id" in query:
            episode = self.get_episode(query["episode_id"])
            return [episode] if episode else []
        
        # Default to returning a few recent ones if no specific query, or empty
        # return self.episodic_memory[-3:] # Example: return last 3
        return []


    def store_semantic_knowledge(self, knowledge_item: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """
        Phase 1: Stores a semantic knowledge item as a node in the new direct graph.
        Assumes knowledge_item contains 'node_id', 'label', 'node_type'.
        'context' can provide additional properties.
        Returns node_id if successful, or a placeholder/error string.
        """
        print("ConcreteLTM: store_semantic_knowledge called (Phase 1 - direct graph).")
        node_id = knowledge_item.get("node_id")
        label = knowledge_item.get("label")
        node_type = knowledge_item.get("node_type", "concept") # Default node_type
        
        if not node_id or not label:
            print("ConcreteLTM Error: store_semantic_knowledge requires 'node_id' and 'label' in knowledge_item.")
            return "error_missing_id_or_label"

        properties = knowledge_item.get("properties", {})
        if context: # Merge context into properties if any
            properties.update(context)

        if self.add_semantic_node(node_id, label, node_type, properties):
            return node_id
        return f"error_adding_node_{node_id}"


    def get_semantic_knowledge(self, query: Dict[str, Any], criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Phase 1: Retrieves semantic knowledge from the new direct graph.
        'query' can specify 'node_id' or 'find_related_to_node_id'.
        'criteria' can specify 'relationship_type'.
        """
        print("ConcreteLTM: get_semantic_knowledge called (Phase 1 - direct graph search).")
        if "node_id" in query:
            node = self.get_semantic_node(query["node_id"])
            return [node] if node else []
        
        if "find_related_to_node_id" in query:
            source_node_id = query["find_related_to_node_id"]
            relationship_type = (criteria or {}).get("relationship_type")

            # Option 1: Return full node data of related nodes
            related_node_ids = self.find_related_nodes(source_node_id, relationship_type)
            return [self.get_semantic_node(nid) for nid in related_node_ids if self.get_semantic_node(nid)]
            
            # Option 2: Return relationship data (as in get_semantic_relationships)
            # return self.get_semantic_relationships(source_node_id, relationship_type)
        return []

    def store_procedural_skill(self, skill_data: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Stores a procedural skill using the backend storage."""
        ltm_context = context or {}
        ltm_context['ltm_type'] = 'procedural'

        if 'skill_name_key' not in skill_data: # Ensure a queryable name field
            skill_name_for_query = skill_data.get("skill_name", skill_data.get("id", f"proc_{len(self._storage_backend._storage)}"))
            skill_data['skill_name_key'] = skill_name_for_query
            print(f"ConcreteLTM Warning: 'skill_name_key' not found in skill_data, auto-set to '{skill_name_for_query}'.")

        memory_id = self._storage_backend.store(skill_data, ltm_context)
        self._subcomponent_status['procedural_backend']['items'] += 1
        print(f"ConcreteLTM: Stored procedural skill. ID: {memory_id}. Data: {skill_data}")
        return memory_id

    def get_procedural_skill(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """Retrieves a procedural skill by its 'skill_name_key' from backend storage."""
        ltm_criteria = {'match_context': {'ltm_type': 'procedural'}}
        query = {'skill_name_key': skill_name}

        print(f"ConcreteLTM: Retrieving procedural skill '{skill_name}' from backend. Query: {query}, Criteria: {ltm_criteria}")
        results = self._storage_backend.retrieve(query, ltm_criteria)
        self._subcomponent_status['procedural_backend']['queries'] += 1
        
        if results:
            # Assuming retrieve returns list of {'id': ..., 'info': ..., 'ctx': ...}
            return results[0].get('info', results[0]) # Return the info part
        print(f"ConcreteLTM: Skill '{skill_name}' not found in procedural backend.")
        return None

    def manage_ltm_subcomponents(self) -> None:
        """Placeholder for managing LTM subcomponents specific logic."""
        print("ConcreteLTM: manage_ltm_subcomponents() called - Placeholder.")
        # E.g., if len(self.episodic_memory) > MAX_EPISODES, trigger pruning.
        pass

    def consolidate_memory(self, type_to_consolidate: str = 'all', intensity: str = 'normal') -> None:
        """Placeholder for LTM consolidation process across new structures."""
        print(f"ConcreteLTM: consolidate_memory called for type '{type_to_consolidate}' with intensity '{intensity}'. Placeholder.")
        # Conceptual: if 'episodic', might try to find patterns and form semantic nodes.
        # Conceptual: if 'semantic', might try to infer new relationships or prune weak ones.
        pass

if __name__ == '__main__':
    # --- Updated __main__ for Phase 1 Enhanced LTM ---
    ltm = ConcreteLongTermMemoryModule()
    print("\n--- Initial LTM Status (Phase 1 Enhanced) ---")
    print(ltm.get_status())

    # Test Episodic Memory
    print("\n--- Testing Episodic Memory ---")
    ep_id1 = ltm.add_episode("User logged in.", associated_data={"user_id": "alice123"})
    ep_id2 = ltm.add_episode("System backup started.", timestamp=time.time() - 3600)
    ltm.add_episode("User searched for 'PiaAGI'.", associated_data={"query": "PiaAGI"})

    print(f"Episode {ep_id1}: {ltm.get_episode(ep_id1)}")
    print(f"Episode ep_99 (non-existent): {ltm.get_episode('ep_99')}")

    keyword_search_user = ltm.find_episodes_by_keyword("user")
    print(f"Episodes found for 'user': {len(keyword_search_user)}")
    assert len(keyword_search_user) == 2
    keyword_search_piaagi_assoc = ltm.find_episodes_by_keyword("PiaAGI", search_in_description=False, search_in_associated_data=True)
    print(f"Episodes found for 'PiaAGI' in associated_data: {len(keyword_search_piaagi_assoc)}")
    assert len(keyword_search_piaagi_assoc) == 1


    # Test Semantic Memory
    print("\n--- Testing Semantic Memory ---")
    ltm.add_semantic_node("concept_piaagi", "PiaAGI", "Cognitive Architecture", {"version": "2.0"})
    ltm.add_semantic_node("concept_ltm", "Long-Term Memory", "Cognitive Module")
    ltm.add_semantic_node("concept_python", "Python", "Programming Language")

    ltm.add_semantic_relationship("concept_piaagi", "concept_ltm", "has_component")
    ltm.add_semantic_relationship("concept_ltm", "concept_piaagi", "part_of") # Example inverse
    ltm.add_semantic_relationship("concept_piaagi", "concept_python", "implemented_in_part_with", {"confidence": 0.8})

    print(f"Node 'concept_piaagi': {ltm.get_semantic_node('concept_piaagi')}")
    print(f"Node 'concept_non_existent': {ltm.get_semantic_node('concept_non_existent')}")

    related_to_piaagi = ltm.find_related_nodes("concept_piaagi")
    print(f"Nodes related to 'concept_piaagi': {related_to_piaagi}")
    assert "concept_ltm" in related_to_piaagi
    assert "concept_python" in related_to_piaagi

    piaagi_has_component_rels = ltm.get_semantic_relationships("concept_piaagi", "has_component")
    print(f"PiaAGI 'has_component' relationships: {piaagi_has_component_rels}")
    assert len(piaagi_has_component_rels) == 1 and piaagi_has_component_rels[0]["target"] == "concept_ltm"

    # Test Procedural Memory (still uses backend)
    print("\n--- Testing Procedural Memory (Backend) ---")
    skill_data_plan = {'skill_name_key': 'create_plan', 'steps': ['define_goal', 'find_resources', 'sequence_actions']}
    skill_id_plan = ltm.store_procedural_skill(skill_data_plan, {'domain': 'planning'})
    retrieved_plan_skill = ltm.get_procedural_skill('create_plan')
    print(f"Retrieved skill 'create_plan': {retrieved_plan_skill is not None}")
    assert retrieved_plan_skill is not None
    if retrieved_plan_skill: # Ensure it's not None before trying to access keys
      assert retrieved_plan_skill['skill_name_key'] == 'create_plan'

    print("\n--- LTM Status After Operations ---")
    final_status = ltm.get_status()
    print(final_status)
    assert final_status['direct_ltm_structures_status']['episodic_memory_count'] == 3
    assert final_status['direct_ltm_structures_status']['semantic_graph_nodes'] == 3
    assert final_status['direct_ltm_structures_status']['semantic_graph_edges'] == 3 # 1 forward, 1 inverse, 1 another
    assert final_status['query_counts_overview']['procedural_backend']['items'] == 1

    print("\nExample Usage Complete (Phase 1 Enhanced LTM).")
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
