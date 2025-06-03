import unittest
import time
import os
import sys
import uuid # For generating query IDs
from unittest.mock import MagicMock

# Adjust path for consistent imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    from PiaAGI_Research_Tools.PiaCML import (
        ConcreteLongTermMemoryModule,
        MessageBus,
        GenericMessage,
        LTMQueryResultPayload, # For asserting results
        MemoryItem # For asserting results
        # LTMQueryPayload is not a defined dataclass yet, queries will be dicts
    )
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from concrete_long_term_memory_module import ConcreteLongTermMemoryModule
    try:
        from message_bus import MessageBus
        from core_messages import GenericMessage, LTMQueryResultPayload, MemoryItem
    except ImportError:
        MessageBus = None
        GenericMessage = None
        LTMQueryResultPayload = None
        MemoryItem = None


class TestConcreteLongTermMemoryModule(unittest.TestCase):

    def setUp(self):
        self.bus = MessageBus() if MessageBus else None # Real bus for testing subscription
        self.ltm_no_bus = ConcreteLongTermMemoryModule()
        self.ltm_with_bus = ConcreteLongTermMemoryModule(message_bus=self.bus)

        self._original_stdout = sys.stdout
        # Suppress prints from the module during tests for cleaner output
        # sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        """Restore stdout after each test."""
        # sys.stdout.close()
        sys.stdout = self._original_stdout

    # --- Episodic Memory Tests (using ltm_no_bus for direct calls) ---
    def test_add_episode_basic(self):
        initial_count = len(self.ltm_no_bus.episodic_memory)
        ep_id = self.ltm_no_bus.add_episode("Test event 1")
        self.assertTrue(ep_id.startswith("ep_"))
        self.assertEqual(len(self.ltm_no_bus.episodic_memory), initial_count + 1)
        # ... (rest of assertions from existing test) ...
        self.assertEqual(self.ltm_no_bus.episodic_memory[-1]["event_description"], "Test event 1")
        self.assertAlmostEqual(self.ltm_no_bus.episodic_memory[-1]["timestamp"], time.time(), delta=1)
        self.assertEqual(self.ltm_no_bus.episodic_memory[-1]["episode_id"], ep_id)


    def test_add_episode_with_details(self):
        ts = time.time() - 1000
        assoc_data = {"location": "lab", "mood": "curious"}
        causal_links = ["ep_0"]
        ep_id = self.ltm_no_bus.add_episode("Detailed event", timestamp=ts, associated_data=assoc_data, causal_links=causal_links)
        added_episode = self.ltm_no_bus.episodic_memory[-1]
        self.assertEqual(added_episode["timestamp"], ts)
        # ... (rest of assertions) ...
        self.assertEqual(added_episode["associated_data"], assoc_data)
        self.assertEqual(added_episode["causal_links"], causal_links)
        self.assertEqual(self.ltm_no_bus.next_episode_id, int(ep_id.split('_')[1]) + 1)


    def test_get_episode(self):
        ep_id1 = self.ltm_no_bus.add_episode("Event to get")
        retrieved_ep1 = self.ltm_no_bus.get_episode(ep_id1)
        self.assertIsNotNone(retrieved_ep1)
        # ... (rest of assertions) ...
        self.assertEqual(retrieved_ep1["episode_id"], ep_id1)
        self.assertEqual(retrieved_ep1["event_description"], "Event to get")
        self.assertIsNone(self.ltm_no_bus.get_episode("ep_999"))


    def test_find_episodes_by_keyword(self):
        self.ltm_no_bus.add_episode("A sunny day at the park.", associated_data={"activity": "picnic"})
        self.ltm_no_bus.add_episode("Heavy rain caused flooding in the city park.", associated_data={"damage": "significant"})
        # ... (rest of test setup and assertions from existing test, using self.ltm_no_bus) ...
        results_park = self.ltm_no_bus.find_episodes_by_keyword("park")
        self.assertEqual(len(results_park), 2)
        self.ltm_no_bus.add_episode("Routine check.", associated_data={"status": "all clear", "target": "park facilities"})
        results_assoc_park = self.ltm_no_bus.find_episodes_by_keyword("park", search_in_description=False, search_in_associated_data=True)
        self.assertEqual(len(results_assoc_park), 1)


    # --- Semantic Memory Tests (using ltm_no_bus for direct calls) ---
    def test_add_semantic_node(self):
        self.assertTrue(self.ltm_no_bus.add_semantic_node("node1", "Concept Alpha", "concept"))
        # ... (rest of assertions) ...
        self.assertIn("node1", self.ltm_no_bus.semantic_memory_graph)
        self.assertFalse(self.ltm_no_bus.add_semantic_node("node1", "Duplicate Concept", "concept"))

    def test_add_semantic_relationship(self):
        self.ltm_no_bus.add_semantic_node("src_node", "Source Node", "event")
        self.ltm_no_bus.add_semantic_node("tgt_node", "Target Node", "object")
        self.assertTrue(self.ltm_no_bus.add_semantic_relationship("src_node", "tgt_node", "affects", {"strength": 0.8}))
        # ... (rest of assertions) ...
        src_node_data = self.ltm_no_bus.semantic_memory_graph["src_node"]
        self.assertEqual(len(src_node_data["relationships"]), 1)
        self.assertFalse(self.ltm_no_bus.add_semantic_relationship("src_node", "non_existent_node", "related_to"))


    def test_get_semantic_node(self):
        self.ltm_no_bus.add_semantic_node("node_get", "Node To Get", "place", {"feature": "is_capital"})
        node_data = self.ltm_no_bus.get_semantic_node("node_get")
        # ... (rest of assertions) ...
        self.assertIsNotNone(node_data)
        self.assertEqual(node_data["label"], "Node To Get")
        self.assertIsNone(self.ltm_no_bus.get_semantic_node("node_does_not_exist"))


    def test_find_related_nodes(self):
        self.ltm_no_bus.add_semantic_node("center", "Center Node", "topic")
        self.ltm_no_bus.add_semantic_node("related1", "Related 1", "subtopic")
        # ... (rest of test setup and assertions from existing test, using self.ltm_no_bus) ...
        self.ltm_no_bus.add_semantic_relationship("center", "related1", "has_subtopic")
        all_related = self.ltm_no_bus.find_related_nodes("center")
        self.assertIn("related1", all_related)


    def test_get_semantic_relationships(self):
        self.ltm_no_bus.add_semantic_node("s1", "S1", "item")
        self.ltm_no_bus.add_semantic_node("t1", "T1", "item")
        # ... (rest of test setup and assertions from existing test, using self.ltm_no_bus) ...
        self.ltm_no_bus.add_semantic_relationship("s1", "t1", "connected_to", {"weight":10})
        all_rels_s1 = self.ltm_no_bus.get_semantic_relationships("s1")
        self.assertGreaterEqual(len(all_rels_s1), 1)


    # --- Test original high-level methods (using ltm_no_bus) ---
    def test_store_episodic_experience_uses_new_method(self):
        event_data = {'event_description': "High-level store test", 'user': 'tester'}
        ep_id = self.ltm_no_bus.store_episodic_experience(event_data)
        # ... (rest of assertions) ...
        retrieved_episode = self.ltm_no_bus.get_episode(ep_id)
        self.assertIsNotNone(retrieved_episode)

    def test_get_episodic_experience_uses_new_methods(self):
        ep_id = self.ltm_no_bus.add_episode("Keyword search via high-level call", associated_data={"key": "unique_ep_keyword"})
        # ... (rest of assertions) ...
        results_keyword = self.ltm_no_bus.get_episodic_experience(query={"keyword": "unique_ep_keyword"}, criteria={"search_in_associated_data": True})
        self.assertEqual(len(results_keyword), 1)

    def test_store_semantic_knowledge_uses_new_method(self):
        node_data = {"node_id": "sem_hl_1", "label": "High-level Semantic Store"}
        returned_id = self.ltm_no_bus.store_semantic_knowledge(node_data)
        # ... (rest of assertions) ...
        self.assertEqual(returned_id, "sem_hl_1")


    def test_get_semantic_knowledge_uses_new_methods(self):
        self.ltm_no_bus.add_semantic_node("sem_src", "Source Sem HL", "source")
        # ... (rest of assertions) ...
        results_id = self.ltm_no_bus.get_semantic_knowledge(query={"node_id": "sem_src"})
        self.assertEqual(len(results_id), 1)

    def test_procedural_memory_still_functional(self):
        skill_data = {'skill_name_key': 'test_proc_skill', 'description': 'A skill for testing backend.'}
        skill_id = self.ltm_no_bus.store_procedural_skill(skill_data)
        # ... (rest of assertions) ...
        retrieved_skill = self.ltm_no_bus.get_procedural_skill('test_proc_skill')
        self.assertIsNotNone(retrieved_skill)

    # --- New Tests for MessageBus Integration ---
    def test_initialization_with_bus(self):
        """Test LTM initialization with a message bus and subscription."""
        self.assertIsNotNone(self.ltm_with_bus.message_bus)
        subscribers = self.bus.get_subscribers_for_type("LTMQuery")
        self.assertTrue(
            any(sub[0] == "ConcreteLongTermMemoryModule_01" and
                sub[1] == self.ltm_with_bus.handle_ltm_query_message
                for sub in subscribers)
        )

    def test_handle_ltm_query_semantic_node_retrieval_via_bus(self):
        """Test semantic node retrieval via message bus query."""
        self.ltm_with_bus.add_semantic_node("node_bus_test", "Bus Test Node", "test_type")

        mock_querier_callback = MagicMock(name="querier_cb_semantic")
        self.bus.subscribe("TestQuerierModule", "LTMQueryResult", mock_querier_callback)

        query_id = str(uuid.uuid4())
        ltm_query_payload = { # Simulating LTMQueryPayload as dict
            "query_id": query_id,
            "query_type": "semantic_node_retrieval",
            "query_content": "node_bus_test", # node_id
            "requester_module_id": "TestQuerierModule"
        }
        query_message = GenericMessage(
            source_module_id="TestQuerierModule",
            message_type="LTMQuery",
            payload=ltm_query_payload
        )

        self.bus.publish(query_message)

        mock_querier_callback.assert_called_once()
        received_result_message: GenericMessage = mock_querier_callback.call_args[0][0]

        self.assertEqual(received_result_message.message_type, "LTMQueryResult")
        self.assertEqual(received_result_message.target_module_id, "TestQuerierModule")
        self.assertIsInstance(received_result_message.payload, LTMQueryResultPayload)

        payload: LTMQueryResultPayload = received_result_message.payload
        self.assertEqual(payload.query_id, query_id)
        self.assertTrue(payload.success_status)
        self.assertEqual(len(payload.results), 1)
        self.assertIsInstance(payload.results[0], MemoryItem)
        self.assertEqual(payload.results[0].item_id, "node_bus_test")
        self.assertEqual(payload.results[0].content.get("label"), "Bus Test Node")
        self.assertEqual(self.ltm_with_bus._subcomponent_status['semantic_graph']['bus_queries_handled'], 1)


    def test_handle_ltm_query_episodic_keyword_via_bus(self):
        """Test episodic keyword search via message bus query."""
        self.ltm_with_bus.add_episode("An episode about bus testing.", associated_data={"keywords": "bus, test"})

        mock_querier_callback = MagicMock(name="querier_cb_episodic")
        self.bus.subscribe("TestQuerierEpisodic", "LTMQueryResult", mock_querier_callback)

        query_id = str(uuid.uuid4())
        ltm_query_payload = {
            "query_id": query_id,
            "query_type": "episodic_keyword_search",
            "query_content": "bus testing",
            "requester_module_id": "TestQuerierEpisodic"
        }
        query_message = GenericMessage(
            source_module_id="TestQuerierEpisodic",
            message_type="LTMQuery",
            payload=ltm_query_payload
        )
        self.bus.publish(query_message)

        mock_querier_callback.assert_called_once()
        received_result_message: GenericMessage = mock_querier_callback.call_args[0][0]
        payload: LTMQueryResultPayload = received_result_message.payload

        self.assertTrue(payload.success_status)
        self.assertEqual(payload.query_id, query_id)
        self.assertEqual(len(payload.results), 1)
        self.assertTrue("An episode about bus testing." in payload.results[0].content.get("event_description"))
        self.assertEqual(self.ltm_with_bus._subcomponent_status['episodic_list']['bus_queries_handled'], 1)


    def test_handle_ltm_query_unsupported_type_via_bus(self):
        """Test LTM handling of unsupported query type via bus."""
        mock_querier_callback = MagicMock(name="querier_cb_unsupported")
        self.bus.subscribe("TestQuerierUnsupported", "LTMQueryResult", mock_querier_callback)

        query_id = str(uuid.uuid4())
        ltm_query_payload = {
            "query_id": query_id,
            "query_type": "magical_mystery_retrieval", # Unsupported
            "query_content": "anything",
            "requester_module_id": "TestQuerierUnsupported"
        }
        query_message = GenericMessage(source_module_id="TestQuerierUnsupported", message_type="LTMQuery", payload=ltm_query_payload)
        self.bus.publish(query_message)

        mock_querier_callback.assert_called_once()
        payload: LTMQueryResultPayload = mock_querier_callback.call_args[0][0].payload
        self.assertFalse(payload.success_status)
        self.assertIsNotNone(payload.error_message)
        self.assertIn("Unsupported LTM query_type", payload.error_message)
        self.assertEqual(len(payload.results), 0)

    def test_handle_ltm_query_malformed_payload_via_bus(self):
        """Test LTM handling of a malformed query payload (not a dict)."""
        mock_querier_callback = MagicMock(name="querier_cb_malformed")
        self.bus.subscribe("TestQuerierMalformed", "LTMQueryResult", mock_querier_callback)

        query_message = GenericMessage(
            source_module_id="TestQuerierMalformed",
            message_type="LTMQuery",
            payload="This is not a dictionary" # Malformed payload
        )
        self.bus.publish(query_message)
        mock_querier_callback.assert_called_once()
        payload: LTMQueryResultPayload = mock_querier_callback.call_args[0][0].payload
        self.assertFalse(payload.success_status)
        self.assertIsNotNone(payload.error_message)
        self.assertIn("Payload is not a dictionary", payload.error_message)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
