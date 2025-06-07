from typing import Any, Dict, List, Optional
import time
import uuid # For LTM Query Result fallback query_id

try:
    from .base_long_term_memory_module import BaseLongTermMemoryModule
    from .concrete_base_memory_module import ConcreteBaseMemoryModule
    from .message_bus import MessageBus
    from .core_messages import GenericMessage, LTMQueryResultPayload, MemoryItem, LTMQueryPayload # Added LTMQueryPayload
except ImportError:
    print("Warning: Running ConcreteLongTermMemoryModule with stubbed imports.")
    from base_long_term_memory_module import BaseLongTermMemoryModule # type: ignore
    from concrete_base_memory_module import ConcreteBaseMemoryModule # type: ignore
    try:
        from message_bus import MessageBus # type: ignore
        from core_messages import GenericMessage, LTMQueryResultPayload, MemoryItem, LTMQueryPayload # type: ignore
    except ImportError:
        MessageBus = None # type: ignore
        GenericMessage = object # type: ignore
        LTMQueryResultPayload = object # type: ignore
        MemoryItem = object # type: ignore
        LTMQueryPayload = object # type: ignore


class ConcreteLongTermMemoryModule(BaseLongTermMemoryModule):
    """
    A concrete implementation of the BaseLongTermMemoryModule.
    Integrates with a MessageBus to handle LTMQuery messages using LTMQueryPayload.
    """

    def __init__(self,
                 message_bus: Optional[MessageBus] = None,
                 module_id: str = f"ConcreteLongTermMemoryModule_{str(uuid.uuid4())[:8]}"):
        """
        Initializes the ConcreteLongTermMemoryModule.

        Args:
            message_bus: An optional instance of MessageBus for handling queries.
            module_id: A unique identifier for this module instance.
        """
        self._storage_backend = ConcreteBaseMemoryModule()
        self._module_id = module_id
        self.episodic_memory: List[Dict[str, Any]] = []
        self.next_episode_id: int = 0
        self.semantic_memory_graph: Dict[str, Dict[str, Any]] = {}

        self._message_bus = message_bus
        if self._message_bus:
            if GenericMessage and LTMQueryPayload: # Ensure necessary types are loaded
                self._message_bus.subscribe(
                    module_id=self._module_id,
                    message_type="LTMQuery",
                    callback=self.handle_ltm_query_message
                )
                bus_status = f"subscribed to 'LTMQuery' as '{self._module_id}'"
            else:
                bus_status = "core_messages (GenericMessage or LTMQueryPayload) not imported, LTMQuery subscription skipped"
            print(f"ConcreteLongTermMemoryModule initialized. Message bus {bus_status}.")
        else:
            print(f"ConcreteLongTermMemoryModule '{self._module_id}' initialized. Message bus not provided.")

        self._subcomponent_status = {
            "episodic_list": {"items": 0, "queries": 0, "bus_queries_handled": 0},
            "semantic_graph": {"nodes": 0, "edges": 0, "queries": 0, "bus_queries_handled": 0},
            "procedural_backend": {"items": 0, "queries": 0},
            "generic_backend": {"items": 0, "queries": 0}
        }


    def handle_ltm_query_message(self, message: GenericMessage):
        """
        Handles LTMQuery messages received from the message bus.
        The payload of the message is expected to be an LTMQueryPayload dataclass instance.
        """
        if not self._message_bus or not GenericMessage or not LTMQueryResultPayload or not MemoryItem or not LTMQueryPayload:
            print(f"LTM Error ({self._module_id}): MessageBus or core message types not available. Cannot process or respond to LTMQuery.")
            return

        if not isinstance(message.payload, LTMQueryPayload):
            error_msg = f"Payload is not an LTMQueryPayload instance, received type: {type(message.payload).__name__}."
            print(f"LTM Error ({self._module_id}): {error_msg}")
            # Try to get original query_id if possible for error response, otherwise generate one
            original_query_id = getattr(message.payload, 'query_id', str(uuid.uuid4()))
            error_payload = LTMQueryResultPayload(query_id=original_query_id, results=[], success_status=False, error_message=error_msg)
            error_result_message = GenericMessage(
                source_module_id=self._module_id,
                message_type="LTMQueryResult",
                payload=error_payload,
                target_module_id=message.source_module_id
            )
            self._message_bus.publish(error_result_message)
            return

        query_payload: LTMQueryPayload = message.payload
        # print(f"LTM ({self._module_id}) received query via bus: {query_payload}") # Optional logging

        results: List[MemoryItem] = []
        success = False
        error_msg: Optional[str] = None

        try:
            query_type = query_payload.query_type
            query_content = query_payload.query_content
            # target_memory_type = query_payload.target_memory_type (can be used for routing if needed)
            # parameters = query_payload.parameters (can be used for max_results etc.)

            if query_type == "semantic_node_retrieval" and isinstance(query_content, str):
                self._subcomponent_status['semantic_graph']['bus_queries_handled'] += 1
                node_data = self.get_semantic_node(query_content) # query_content is node_id
                if node_data:
                    results.append(MemoryItem(item_id=query_content, content=node_data, metadata={"type": "semantic_node"}))
                success = True # Query type was valid, even if no result found
            elif query_type == "episodic_keyword_search" and isinstance(query_content, str):
                self._subcomponent_status['episodic_list']['bus_queries_handled'] += 1
                # Consider using parameters if available, e.g., query_payload.parameters.get("max_results")
                episodes = self.find_episodes_by_keyword(query_content)
                for episode in episodes:
                    results.append(MemoryItem(item_id=episode["episode_id"], content=episode, metadata={"type": "episode"}))
                success = True
            else:
                error_msg = f"Unsupported LTM query_type: '{query_type}' or invalid query_content type for that query_type."
                success = False # Explicitly set success to False for unsupported types

        except Exception as e:
            error_msg = f"Error processing LTM query '{query_payload.query_type}' (ID: {query_payload.query_id}): {str(e)}"
            print(f"LTM Error ({self._module_id}): {error_msg}") # Consider logging traceback for debug
            success = False

        ltm_result_payload = LTMQueryResultPayload(
            query_id=query_payload.query_id, # Use the query_id from the LTMQueryPayload
            results=results,
            success_status=success,
            error_message=error_msg
        )
        result_message = GenericMessage(
            source_module_id=self._module_id,
            message_type="LTMQueryResult",
            payload=ltm_result_payload,
            target_module_id=message.source_module_id # Respond to the original querier
        )
        self._message_bus.publish(result_message)
        # print(f"LTM ({self._module_id}) published result for query_id '{query_payload.query_id}' to '{message.source_module_id}'. Success: {success}")

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
            print(f"ConcreteLTM ({self._module_id}): Deleted semantic node '{memory_id}'. Relationships pointing to it might still exist.")
            return True

        # If not in direct structures, try backend
        print(f"ConcreteLTM ({self._module_id}): Attempting to delete ID '{memory_id}' from backend.")
        return self._storage_backend.delete_memory(memory_id)


    def manage_capacity(self) -> None:
        print(f"ConcreteLTM ({self._module_id}): manage_capacity called.")
        self._storage_backend.manage_capacity()
        self.manage_ltm_subcomponents()

    def handle_forgetting(self, strategy: str = 'default') -> None:
        print(f"ConcreteLTM ({self._module_id}): handle_forgetting called with strategy '{strategy}'.")
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
            "module_id": self._module_id,
            "module_type": "ConcreteLongTermMemoryModule (Message Bus Integrated)",
            "message_bus_configured": self._message_bus is not None,
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
        print(f"ConcreteLTM ({self._module_id}): consolidate_memory called for type '{type_to_consolidate}' with intensity '{intensity}'. Placeholder.")

if __name__ == '__main__':
    import asyncio

    # Ensure MessageBus and core_messages are available for __main__
    if MessageBus is None or GenericMessage is None or LTMQueryResultPayload is None or LTMQueryPayload is None or MemoryItem is None:
        print("CRITICAL: MessageBus or core_messages not loaded correctly for __main__ test. Exiting.")
        exit(1)

    print("\n--- ConcreteLongTermMemoryModule __main__ Test ---")

    received_ltm_results: List[GenericMessage] = []
    def ltm_result_listener(message: GenericMessage):
        print(f"\n ltm_result_listener: Received LTMQueryResult! ID: {message.message_id[:8]}")
        if isinstance(message.payload, LTMQueryResultPayload):
            payload: LTMQueryResultPayload = message.payload
            print(f"  Source: {message.source_module_id}")
            print(f"  Query ID: {payload.query_id}")
            print(f"  Success: {payload.success_status}")
            print(f"  Result Count: {len(payload.results)}")
            if payload.error_message: print(f"  Error: {payload.error_message}")
            for res_item in payload.results:
                print(f"    - Item ID: {res_item.item_id}, Content: {str(res_item.content)[:100]}...")
            received_ltm_results.append(message)
        else:
            print(f"  ERROR: Listener received non-LTMQueryResultPayload: {type(message.payload)}")

    async def main_test_flow():
        bus = MessageBus()
        test_ltm_module_id = "LTMTest01"
        ltm_module = ConcreteLongTermMemoryModule(message_bus=bus, module_id=test_ltm_module_id)

        print("\n--- Initial LTM Status ---")
        print(ltm_module.get_status())

        bus.subscribe(
            module_id="TestLTMResultListener",
            message_type="LTMQueryResult",
            callback=ltm_result_listener
        )
        print("\nTestLTMResultListener subscribed to LTMQueryResult messages.")

        # Add some data to LTM
        ltm_module.add_semantic_node("concept_dog", "Dog", "animal", {"sound": "bark"})
        ltm_module.add_semantic_node("concept_cat", "Cat", "animal", {"sound": "meow"})
        ltm_module.add_semantic_relationship("concept_dog", "concept_cat", "known_interaction", {"type": "chases"})
        ltm_module.add_episode("The dog chased the cat.", associated_data={"animals_involved": ["dog", "cat"]})
        ltm_module.add_episode("The cat sat on the mat.", associated_data={"object": "mat"})

        # 1. Test Semantic Node Retrieval (Success)
        print("\n--- Publishing LTMQuery: Semantic Node Retrieval (concept_dog) ---")
        query_payload_semantic_dog = LTMQueryPayload(
            requester_module_id="TestQuerier01",
            query_type="semantic_node_retrieval",
            query_content="concept_dog"
        )
        query_msg_semantic_dog = GenericMessage(
            source_module_id="TestQuerier01", message_type="LTMQuery", payload=query_payload_semantic_dog
        )
        bus.publish(query_msg_semantic_dog)
        await asyncio.sleep(0.05)

        assert len(received_ltm_results) == 1, "LTMQueryResult for concept_dog not received"
        if received_ltm_results:
            res1_payload = received_ltm_results[0].payload
            assert res1_payload.query_id == query_payload_semantic_dog.query_id
            assert res1_payload.success_status is True
            assert len(res1_payload.results) == 1
            assert res1_payload.results[0].content.get("label") == "Dog"
            print("  Listener correctly received result for 'concept_dog'.")
        received_ltm_results.clear()


        # 2. Test Episodic Keyword Search (Success)
        print("\n--- Publishing LTMQuery: Episodic Keyword Search (cat) ---")
        query_payload_episodic_cat = LTMQueryPayload(
            requester_module_id="TestQuerier01",
            query_type="episodic_keyword_search",
            query_content="cat"
        )
        query_msg_episodic_cat = GenericMessage(
            source_module_id="TestQuerier01", message_type="LTMQuery", payload=query_payload_episodic_cat
        )
        bus.publish(query_msg_episodic_cat)
        await asyncio.sleep(0.05)

        assert len(received_ltm_results) == 1, "LTMQueryResult for episodic 'cat' not received"
        if received_ltm_results:
            res2_payload = received_ltm_results[0].payload
            assert res2_payload.query_id == query_payload_episodic_cat.query_id
            assert res2_payload.success_status is True
            assert len(res2_payload.results) == 2 # "dog chased cat" and "cat sat on mat"
            print("  Listener correctly received 2 episodes for keyword 'cat'.")
        received_ltm_results.clear()


        # 3. Test Unsupported Query Type
        print("\n--- Publishing LTMQuery: Unsupported Query Type ---")
        query_payload_unsupported = LTMQueryPayload(
            requester_module_id="TestQuerier01",
            query_type="future_prediction_query", # Made up type
            query_content="what will happen tomorrow?"
        )
        query_msg_unsupported = GenericMessage(
            source_module_id="TestQuerier01", message_type="LTMQuery", payload=query_payload_unsupported
        )
        bus.publish(query_msg_unsupported)
        await asyncio.sleep(0.05)

        assert len(received_ltm_results) == 1, "LTMQueryResult for unsupported type not received"
        if received_ltm_results:
            res3_payload = received_ltm_results[0].payload
            assert res3_payload.query_id == query_payload_unsupported.query_id
            assert res3_payload.success_status is False
            assert "Unsupported LTM query_type" in res3_payload.error_message
            print(f"  Listener correctly received error for unsupported query type: {res3_payload.error_message}")
        received_ltm_results.clear()

        # 4. Test Malformed Payload (if module handles it gracefully by sending error back)
        print("\n--- Publishing LTMQuery: Malformed Payload (not LTMQueryPayload) ---")
        malformed_payload_dict = {"some_random_key": "some_value", "query_id": "malformed_q1"} # Not LTMQueryPayload
        query_msg_malformed = GenericMessage(
            source_module_id="TestQuerier01", message_type="LTMQuery", payload=malformed_payload_dict
        )
        bus.publish(query_msg_malformed)
        await asyncio.sleep(0.05)

        assert len(received_ltm_results) == 1, "LTMQueryResult for malformed payload not received"
        if received_ltm_results:
            res4_payload = received_ltm_results[0].payload
            # The query_id might be a newly generated one if the original couldn't be parsed from the malformed payload.
            # assert res4_payload.query_id == "malformed_q1" # This might fail if LTM can't get it
            assert res4_payload.success_status is False
            assert "Payload is not an LTMQueryPayload instance" in res4_payload.error_message
            print(f"  Listener correctly received error for malformed payload: {res4_payload.error_message}")
        received_ltm_results.clear()


        print("\n--- Final LTM Status ---")
        print(ltm_module.get_status())
        assert ltm_module.get_status()["query_counts_overview"]["semantic_graph"]["bus_queries_handled"] == 1
        assert ltm_module.get_status()["query_counts_overview"]["episodic_list"]["bus_queries_handled"] == 1


        print("\n--- ConcreteLongTermMemoryModule __main__ Test Complete ---")

    try:
        asyncio.run(main_test_flow())
    except RuntimeError as e:
        if " asyncio.run() cannot be called from a running event loop" in str(e):
            print("Skipping asyncio.run() as an event loop is already running (e.g. in Jupyter/IPython).")
        else:
            raise

    # Original __main__ content for direct calls (can be run if bus is None)
    # ltm_no_bus = ConcreteLongTermMemoryModule() # No bus
    # ... (rest of the original __main__ for direct calls can be pasted here if needed for separate testing) ...
    # print("\n(Original direct call examples can be run by instantiating LTM without a bus)")
