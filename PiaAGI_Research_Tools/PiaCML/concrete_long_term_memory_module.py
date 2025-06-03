from typing import Any, Dict, List, Optional
import time
import uuid # For LTM Query Result fallback query_id

try:
    from .base_long_term_memory_module import BaseLongTermMemoryModule
    from .concrete_base_memory_module import ConcreteBaseMemoryModule # Still used for procedural
    from .message_bus import MessageBus
    from .core_messages import GenericMessage, LTMQueryResultPayload, MemoryItem
    # LTMQueryPayload is not a defined dataclass yet in core_messages.py,
    # handle_ltm_query_message will expect a dict for query_payload.
except ImportError:
    # Fallback for scenarios where the relative import might fail
    from base_long_term_memory_module import BaseLongTermMemoryModule
    from concrete_base_memory_module import ConcreteBaseMemoryModule
    try:
        from message_bus import MessageBus
        from core_messages import GenericMessage, LTMQueryResultPayload, MemoryItem
    except ImportError:
        MessageBus = None
        GenericMessage = None
        LTMQueryResultPayload = None
        MemoryItem = None


class ConcreteLongTermMemoryModule(BaseLongTermMemoryModule):
    """
    A concrete implementation of the BaseLongTermMemoryModule.
    This version includes Phase 1 enhancements:
    - Direct in-memory list for episodic memory with keyword search.
    - Direct in-memory dictionary-based graph for semantic memory.
    Procedural memory and generic LTM functions may still use the backend.
    It also integrates with a MessageBus to handle LTMQuery messages.
    """

    def __init__(self, message_bus: Optional[MessageBus] = None):
        """
        Initializes the ConcreteLongTermMemoryModule.

        Args:
            message_bus: An optional instance of MessageBus for handling queries.
        """
        self._storage_backend = ConcreteBaseMemoryModule() # For procedural and generic

        self.episodic_memory: List[Dict[str, Any]] = []
        self.next_episode_id: int = 0
        self.semantic_memory_graph: Dict[str, Dict[str, Any]] = {}

        self.message_bus = message_bus
        if self.message_bus:
            if GenericMessage: # Check if import succeeded
                self.message_bus.subscribe(
                    module_id="ConcreteLongTermMemoryModule_01", # Example ID
                    message_type="LTMQuery",
                    callback=self.handle_ltm_query_message
                )
                bus_status = "subscribed to 'LTMQuery'"
            else:
                bus_status = "core_messages not imported, LTMQuery subscription skipped"
            print(f"ConcreteLongTermMemoryModule (Phase 1 Enhanced) initialized. Message bus {bus_status}.")
        else:
            print("ConcreteLongTermMemoryModule (Phase 1 Enhanced) initialized. Message bus not provided.")

        self._subcomponent_status = {
            "episodic_list": {"items": 0, "queries": 0, "bus_queries_handled": 0},
            "semantic_graph": {"nodes": 0, "edges": 0, "queries": 0, "bus_queries_handled": 0},
            "procedural_backend": {"items": 0, "queries": 0},
            "generic_backend": {"items": 0, "queries": 0}
        }


    def handle_ltm_query_message(self, message: GenericMessage):
        """
        Handles LTMQuery messages received from the message bus.
        The payload of the message is expected to be a dictionary matching
        the conceptual LTMQueryPayload structure.
        """
        if not self.message_bus or not GenericMessage or not LTMQueryResultPayload or not MemoryItem:
            print("LTM Error: MessageBus or core message types not available. Cannot process or respond to LTMQuery.")
            return

        # print(f"LTM received query via bus: {message.payload}") # Optional logging

        query_payload = message.payload
        results: List[MemoryItem] = []
        success = False
        error_msg = None

        # Default query_id for result, try to get from payload
        # If payload itself is not a dict, this will be an issue.
        query_id_for_result = str(uuid.uuid4()) # Fallback
        if isinstance(query_payload, dict):
            query_id_for_result = query_payload.get("query_id", query_id_for_result)
        elif hasattr(query_payload, "query_id"): # If it's an object with query_id
             query_id_for_result = query_payload.query_id


        if not isinstance(query_payload, dict): # Assuming LTMQueryPayload is passed as dict for now
            error_msg = f"Payload is not a dictionary, received type: {type(query_payload).__name__}."
            success = False
        else:
            query_type = query_payload.get("query_type")
            query_content = query_payload.get("query_content")
            # target_memory_type = query_payload.get("target_memory_type", "semantic") # Defaulting if needed

            try:
                if query_type == "semantic_node_retrieval" and isinstance(query_content, str):
                    self._subcomponent_status['semantic_graph']['bus_queries_handled'] += 1
                    node_data = self.get_semantic_node(query_content) # query_content is node_id
                    if node_data:
                        results.append(MemoryItem(item_id=query_content, content=node_data, metadata={"type": "semantic_node"}))
                    # success = True even if node_data is None, query itself was valid type
                    success = True
                elif query_type == "episodic_keyword_search" and isinstance(query_content, str):
                    self._subcomponent_status['episodic_list']['bus_queries_handled'] += 1
                    episodes = self.find_episodes_by_keyword(query_content)
                    for episode in episodes:
                        results.append(MemoryItem(item_id=episode["episode_id"], content=episode, metadata={"type": "episode"}))
                    success = True
                # Add more query_type handlers here based on LTMQuery spec as needed
                else:
                    error_msg = f"Unsupported LTM query_type: '{query_type}' or invalid query_content type."

                if error_msg: # If any error_msg was set by logic above.
                    success = False

            except Exception as e:
                # import traceback # Should be at top-level if used extensively
                # tb_str = traceback.format_exc()
                error_msg = f"Error processing LTM query '{query_type}': {str(e)}"
                print(f"LTM Error: {error_msg}") # Consider logging traceback for debug
                success = False

        ltm_result_payload = LTMQueryResultPayload(
            query_id=query_id_for_result,
            results=results,
            success_status=success,
            error_message=error_msg
        )
        result_message = GenericMessage(
            source_module_id="ConcreteLongTermMemoryModule_01", # Example ID
            message_type="LTMQueryResult",
            payload=ltm_result_payload,
            target_module_id=message.source_module_id # Respond to the original querier
        )
        self.message_bus.publish(result_message)
        # print(f"LTM published result for query_id '{query_id_for_result}' to '{message.source_module_id}'. Success: {success}")


    # --- Generic BaseMemoryModule methods (mostly for procedural/other) ---
    def store(self, information: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        ltm_context = context or {}
        ltm_context.setdefault('ltm_type', 'generic_ltm')
        memory_id = self._storage_backend.store(information, ltm_context)
        type_key = ltm_context['ltm_type'] + "_backend" if ltm_context['ltm_type'] in ["procedural", "generic"] else "generic_backend"
        if type_key not in self._subcomponent_status:
             self._subcomponent_status[type_key] = {"items": 0, "queries": 0}
        self._subcomponent_status[type_key]['items'] += 1
        return memory_id

    def retrieve(self, query: Dict[str, Any], criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        return self._storage_backend.retrieve(query, criteria)

    def delete_memory(self, memory_id: str) -> bool:
        # This needs to be smarter: check if ID is in episodic, semantic, or backend
        # For now, assuming it's for backend if not found in direct structures.

        # Check episodic
        original_len_episodic = len(self.episodic_memory)
        self.episodic_memory = [ep for ep in self.episodic_memory if ep["episode_id"] != memory_id]
        if len(self.episodic_memory) < original_len_episodic:
            self._subcomponent_status['episodic_list']['items'] = len(self.episodic_memory)
            print(f"ConcreteLTM: Deleted episode '{memory_id}'.")
            return True

        # Check semantic
        if memory_id in self.semantic_memory_graph:
            del self.semantic_memory_graph[memory_id]
            # Also remove relationships pointing to this node (more complex, not done for PoC)
            self._subcomponent_status['semantic_graph']['nodes'] = len(self.semantic_memory_graph)
            print(f"ConcreteLTM: Deleted semantic node '{memory_id}'. Relationships pointing to it might still exist.")
            return True

        # If not in direct structures, try backend
        print(f"ConcreteLTM: Attempting to delete ID '{memory_id}' from backend.")
        return self._storage_backend.delete_memory(memory_id)


    def manage_capacity(self) -> None:
        print("ConcreteLTM: manage_capacity called.")
        self._storage_backend.manage_capacity()
        self.manage_ltm_subcomponents()

    def handle_forgetting(self, strategy: str = 'default') -> None:
        print(f"ConcreteLTM: handle_forgetting called with strategy '{strategy}'.")
        self._storage_backend.handle_forgetting(strategy)

    def get_status(self) -> Dict[str, Any]:
        backend_status = self._storage_backend.get_status()
        self._subcomponent_status["episodic_list"]["items"] = len(self.episodic_memory)
        self._subcomponent_status["semantic_graph"]["nodes"] = len(self.semantic_memory_graph)
        edge_count = 0
        for node_data in self.semantic_memory_graph.values():
            edge_count += len(node_data.get("relationships", []))
        self._subcomponent_status["semantic_graph"]["edges"] = edge_count
        return {
            "module_type": "ConcreteLongTermMemoryModule (Phase 1 Enhanced w/ Bus)",
            "backend_storage_status": backend_status,
            "direct_ltm_structures_status": {
                "episodic_memory_count": self._subcomponent_status["episodic_list"]["items"],
                "semantic_graph_nodes": self._subcomponent_status["semantic_graph"]["nodes"],
                "semantic_graph_edges": edge_count,
            },
            "query_counts_overview": dict(self._subcomponent_status),
        }

    # --- Phase 1: Episodic Memory Methods ---
    def add_episode(self, event_description: str, timestamp: Optional[float] = None,
                    associated_data: Optional[Dict[str, Any]] = None,
                    causal_links: Optional[List[str]] = None) -> str:
        actual_timestamp = timestamp if timestamp is not None else time.time()
        episode_id = f"ep_{self.next_episode_id}"
        episode = {
            "episode_id": episode_id, "timestamp": actual_timestamp,
            "event_description": event_description, "associated_data": associated_data or {},
            "causal_links": causal_links or []
        }
        self.episodic_memory.append(episode)
        self.next_episode_id += 1
        self._subcomponent_status['episodic_list']['items'] = len(self.episodic_memory)
        return episode_id

    def get_episode(self, episode_id: str) -> Optional[Dict[str, Any]]:
        self._subcomponent_status['episodic_list']['queries'] += 1
        for episode in self.episodic_memory:
            if episode["episode_id"] == episode_id: return episode
        return None

    def find_episodes_by_keyword(self, keyword: str,
                                 search_in_description: bool = True,
                                 search_in_associated_data: bool = False) -> List[Dict[str, Any]]:
        self._subcomponent_status['episodic_list']['queries'] += 1
        found_episodes: List[Dict[str, Any]] = []
        keyword_lower = keyword.lower()
        for episode in self.episodic_memory:
            match = False
            if search_in_description and keyword_lower in episode["event_description"].lower(): match = True
            if not match and search_in_associated_data:
                for value in episode["associated_data"].values():
                    if isinstance(value, str) and keyword_lower in value.lower(): match = True; break
            if match: found_episodes.append(episode)
        return found_episodes

    # --- Phase 1: Semantic Memory Graph Methods ---
    def add_semantic_node(self, node_id: str, label: str, node_type: str,
                          properties: Optional[Dict[str, Any]] = None) -> bool:
        if node_id in self.semantic_memory_graph: return False
        self.semantic_memory_graph[node_id] = {
            "label": label, "node_type": node_type,
            "properties": properties or {}, "relationships": []
        }
        self._subcomponent_status['semantic_graph']['nodes'] = len(self.semantic_memory_graph)
        return True

    def add_semantic_relationship(self, source_node_id: str, target_node_id: str,
                                  relationship_type: str,
                                  relationship_properties: Optional[Dict[str, Any]] = None) -> bool:
        if source_node_id not in self.semantic_memory_graph or \
           target_node_id not in self.semantic_memory_graph: return False
        relationship = {
            "type": relationship_type, "target": target_node_id,
            "properties": relationship_properties or {}
        }
        self.semantic_memory_graph[source_node_id]["relationships"].append(relationship)
        return True

    def get_semantic_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        self._subcomponent_status['semantic_graph']['queries'] += 1
        return self.semantic_memory_graph.get(node_id)

    def find_related_nodes(self, node_id: str, relationship_type: Optional[str] = None) -> List[str]:
        self._subcomponent_status['semantic_graph']['queries'] += 1
        node_data = self.get_semantic_node(node_id) # Counts as one query via internal call
        if not node_data: return []
        related_node_ids: List[str] = []
        for rel in node_data.get("relationships", []):
            if relationship_type is None or rel["type"] == relationship_type:
                related_node_ids.append(rel["target"])
        return related_node_ids

    def get_semantic_relationships(self, node_id: str, relationship_type: Optional[str] = None) -> List[Dict[str, Any]]:
        self._subcomponent_status['semantic_graph']['queries'] += 1
        node_data = self.get_semantic_node(node_id) # Counts as one query
        if not node_data: return []
        relationships: List[Dict[str, Any]] = []
        for rel in node_data.get("relationships", []):
            if relationship_type is None or rel["type"] == relationship_type:
                relationships.append(rel)
        return relationships

    # --- Original High-Level Methods (Now using new direct implementations) ---
    def store_episodic_experience(self, event_data: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        description = event_data.get("event_description", str(event_data))
        timestamp = event_data.get("timestamp", (context or {}).get("timestamp"))
        associated_data = event_data.get("associated_data", {k:v for k,v in event_data.items() if k not in ["event_description", "timestamp"]})
        causal_links = event_data.get("causal_links")
        return self.add_episode(description, timestamp, associated_data, causal_links)

    def get_episodic_experience(self, query: Dict[str, Any], criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        keyword = query.get("keyword")
        if keyword:
            search_assoc = (criteria or {}).get("search_in_associated_data", False)
            return self.find_episodes_by_keyword(keyword, search_in_associated_data=search_assoc)
        if "episode_id" in query:
            episode = self.get_episode(query["episode_id"])
            return [episode] if episode else []
        return []

    def store_semantic_knowledge(self, knowledge_item: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        node_id = knowledge_item.get("node_id")
        label = knowledge_item.get("label")
        node_type = knowledge_item.get("node_type", "concept")
        if not node_id or not label: return "error_missing_id_or_label"
        properties = knowledge_item.get("properties", {})
        if context: properties.update(context)
        if self.add_semantic_node(node_id, label, node_type, properties): return node_id
        return f"error_adding_node_{node_id}"

    def get_semantic_knowledge(self, query: Dict[str, Any], criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        if "node_id" in query:
            node = self.get_semantic_node(query["node_id"])
            return [node] if node else []
        if "find_related_to_node_id" in query:
            source_node_id = query["find_related_to_node_id"]
            relationship_type = (criteria or {}).get("relationship_type")
            related_node_ids = self.find_related_nodes(source_node_id, relationship_type)
            return [self.get_semantic_node(nid) for nid in related_node_ids if self.get_semantic_node(nid)]
        return []

    # --- Procedural Memory (Still uses backend) ---
    def store_procedural_skill(self, skill_data: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        ltm_context = context or {}
        ltm_context['ltm_type'] = 'procedural'
        if 'skill_name_key' not in skill_data:
            skill_name_for_query = skill_data.get("skill_name", skill_data.get("id", f"proc_{len(self._storage_backend._storage)}"))
            skill_data['skill_name_key'] = skill_name_for_query
        memory_id = self._storage_backend.store(skill_data, ltm_context)
        self._subcomponent_status['procedural_backend']['items'] += 1
        return memory_id

    def get_procedural_skill(self, skill_name: str) -> Optional[Dict[str, Any]]:
        ltm_criteria = {'match_context': {'ltm_type': 'procedural'}}
        query = {'skill_name_key': skill_name}
        results = self._storage_backend.retrieve(query, ltm_criteria)
        self._subcomponent_status['procedural_backend']['queries'] += 1
        if results: return results[0].get('info', results[0])
        return None

    def manage_ltm_subcomponents(self) -> None:
        print("ConcreteLTM: manage_ltm_subcomponents() called - Placeholder.")

    def consolidate_memory(self, type_to_consolidate: str = 'all', intensity: str = 'normal') -> None:
        print(f"ConcreteLTM: consolidate_memory called for type '{type_to_consolidate}' with intensity '{intensity}'. Placeholder.")

if __name__ == '__main__':
    # Test with MessageBus
    bus = MessageBus() if MessageBus else None
    ltm_with_bus = ConcreteLongTermMemoryModule(message_bus=bus)
    print("\n--- Initial LTM Status (with Bus) ---")
    print(ltm_with_bus.get_status())

    # Example of how another module would query LTM via bus
    if bus and GenericMessage: # Check if imports were successful
        test_querier_id = "TestQuerierModule_01"

        # Add some data to LTM first
        ltm_with_bus.add_semantic_node("concept_alpha", "Alpha", "letter")
        ep_id = ltm_with_bus.add_episode("Bus test event")

        # Mock callback for the querier to receive results
        query_results_received = []
        def querier_result_handler(message: GenericMessage):
            print(f"{test_querier_id} received LTM Result: {message.payload}")
            query_results_received.append(message.payload)

        if bus.subscribe: # Check if bus is a real MessageBus instance
             bus.subscribe(test_querier_id, "LTMQueryResult", querier_result_handler)

        # 1. Query for semantic node
        semantic_query_id = str(uuid.uuid4())
        semantic_query_payload = {
            "query_id": semantic_query_id,
            "query_type": "semantic_node_retrieval",
            "query_content": "concept_alpha", # node_id
            "requester_module_id": test_querier_id
        }
        semantic_query_message = GenericMessage(
            source_module_id=test_querier_id,
            message_type="LTMQuery",
            payload=semantic_query_payload
        )
        print(f"\n{test_querier_id} publishing semantic query for 'concept_alpha' (Query ID: {semantic_query_id})")
        bus.publish(semantic_query_message)

        # Basic check (in real tests, use unittest assertions and time.sleep if truly async)
        time.sleep(0.1) # Allow a moment for synchronous bus to process
        assert len(query_results_received) == 1
        if query_results_received:
            assert query_results_received[0].query_id == semantic_query_id
            assert query_results_received[0].success_status == True
            assert len(query_results_received[0].results) == 1
            assert query_results_received[0].results[0].content.get("label") == "Alpha"

        # 2. Query for episodic keyword
        episodic_query_id = str(uuid.uuid4())
        episodic_query_payload = {
            "query_id": episodic_query_id,
            "query_type": "episodic_keyword_search",
            "query_content": "bus test",
            "requester_module_id": test_querier_id
        }
        episodic_query_message = GenericMessage(
            source_module_id=test_querier_id,
            message_type="LTMQuery",
            payload=episodic_query_payload
        )
        print(f"\n{test_querier_id} publishing episodic query for 'bus test' (Query ID: {episodic_query_id})")
        bus.publish(episodic_query_message)

        time.sleep(0.1)
        assert len(query_results_received) == 2
        if len(query_results_received) > 1:
            assert query_results_received[1].query_id == episodic_query_id
            assert query_results_received[1].success_status == True
            assert len(query_results_received[1].results) == 1
            assert "Bus test event" in query_results_received[1].results[0].content.get("event_description")

        print("\nLTM Bus interaction example complete.")
    else:
        print("\nMessageBus or GenericMessage not available, skipping bus interaction example.")

    # Original __main__ content for direct calls (can be run if bus is None)
    ltm_no_bus = ConcreteLongTermMemoryModule() # No bus
    # ... (rest of the original __main__ for direct calls can be pasted here if needed for separate testing) ...
    print("\n(Original direct call examples can be run by instantiating LTM without a bus)")
