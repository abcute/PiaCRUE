import unittest
import asyncio
import uuid
import time # For LTM add_episode timestamps
from typing import List, Any, Dict

# Adjust path for consistent imports
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    from PiaAGI_Research_Tools.PiaCML.message_bus import MessageBus
    from PiaAGI_Research_Tools.PiaCML.core_messages import GenericMessage, LTMQueryPayload, LTMQueryResultPayload, MemoryItem
    from PiaAGI_Research_Tools.PiaCML.concrete_long_term_memory_module import ConcreteLongTermMemoryModule
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from message_bus import MessageBus
    from core_messages import GenericMessage, LTMQueryPayload, LTMQueryResultPayload, MemoryItem
    from concrete_long_term_memory_module import ConcreteLongTermMemoryModule

class TestConcreteLongTermMemoryModuleIntegration(unittest.TestCase):

    def setUp(self):
        self.bus = MessageBus()
        self.ltm_module_id = f"TestLTMModule_{str(uuid.uuid4())[:8]}"
        # LTM module instantiated in each test method to ensure clean state and data
        self.received_ltm_results: List[GenericMessage] = []
        self.test_querier_id = f"TestQuerier_{str(uuid.uuid4())[:8]}"

    def _ltm_query_result_listener(self, message: GenericMessage):
        if isinstance(message.payload, LTMQueryResultPayload):
            self.received_ltm_results.append(message)

    def tearDown(self):
        self.received_ltm_results.clear()

    # --- Test Handling LTMQuery and Publishing LTMQueryResult ---
    def test_handle_semantic_node_retrieval_query_found(self):
        ltm_module = ConcreteLongTermMemoryModule(message_bus=self.bus, module_id=self.ltm_module_id)
        async def run_test_logic():
            self.bus.subscribe(self.test_querier_id, "LTMQueryResult", self._ltm_query_result_listener)

            node_id_to_find = "test_node_1"
            ltm_module.add_semantic_node(node_id_to_find, "Test Node Label", "concept", {"color": "red"})

            query_payload = LTMQueryPayload(
                requester_module_id=self.test_querier_id,
                query_type="semantic_node_retrieval",
                query_content=node_id_to_find
            )
            query_message = GenericMessage(source_module_id=self.test_querier_id, message_type="LTMQuery", payload=query_payload)

            self.bus.publish(query_message)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_ltm_results), 1)
            result_msg = self.received_ltm_results[0]
            self.assertEqual(result_msg.source_module_id, self.ltm_module_id)
            self.assertEqual(result_msg.target_module_id, self.test_querier_id)
            self.assertEqual(result_msg.message_type, "LTMQueryResult")

            payload: LTMQueryResultPayload = result_msg.payload
            self.assertEqual(payload.query_id, query_payload.query_id)
            self.assertTrue(payload.success_status)
            self.assertIsNone(payload.error_message)
            self.assertEqual(len(payload.results), 1)
            self.assertIsInstance(payload.results[0], MemoryItem)
            self.assertEqual(payload.results[0].item_id, node_id_to_find)
            self.assertEqual(payload.results[0].content.get("label"), "Test Node Label")
            self.assertEqual(payload.results[0].content.get("properties", {}).get("color"), "red")
        asyncio.run(run_test_logic())

    def test_handle_semantic_node_retrieval_query_not_found(self):
        ltm_module = ConcreteLongTermMemoryModule(message_bus=self.bus, module_id=self.ltm_module_id)
        async def run_test_logic():
            self.bus.subscribe(self.test_querier_id, "LTMQueryResult", self._ltm_query_result_listener)
            query_payload = LTMQueryPayload(
                requester_module_id=self.test_querier_id,
                query_type="semantic_node_retrieval",
                query_content="non_existent_node"
            )
            query_message = GenericMessage(source_module_id=self.test_querier_id, message_type="LTMQuery", payload=query_payload)
            self.bus.publish(query_message)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_ltm_results), 1)
            payload: LTMQueryResultPayload = self.received_ltm_results[0].payload
            self.assertEqual(payload.query_id, query_payload.query_id)
            self.assertTrue(payload.success_status) # Query itself was valid type, even if no results
            self.assertEqual(len(payload.results), 0)
            self.assertIsNone(payload.error_message)
        asyncio.run(run_test_logic())

    def test_handle_episodic_keyword_search_query_found(self):
        ltm_module = ConcreteLongTermMemoryModule(message_bus=self.bus, module_id=self.ltm_module_id)
        async def run_test_logic():
            self.bus.subscribe(self.test_querier_id, "LTMQueryResult", self._ltm_query_result_listener)
            ltm_module.add_episode("A day at the sunny park with a dog.", timestamp=time.time()-100)
            ltm_module.add_episode("The cat chased a mouse in the park.", timestamp=time.time()-50)
            ltm_module.add_episode("Reading a book about dogs.", timestamp=time.time()-20)

            query_payload = LTMQueryPayload(
                requester_module_id=self.test_querier_id,
                query_type="episodic_keyword_search",
                query_content="park"
            )
            query_message = GenericMessage(source_module_id=self.test_querier_id, message_type="LTMQuery", payload=query_payload)
            self.bus.publish(query_message)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_ltm_results), 1)
            payload: LTMQueryResultPayload = self.received_ltm_results[0].payload
            self.assertEqual(payload.query_id, query_payload.query_id)
            self.assertTrue(payload.success_status)
            self.assertEqual(len(payload.results), 2) # "sunny park" and "city park"
            self.assertTrue(any("sunny park" in res.content.get("event_description","") for res in payload.results))
            self.assertTrue(any("city park" in res.content.get("event_description","") for res in payload.results))
        asyncio.run(run_test_logic())

    def test_handle_episodic_keyword_search_query_no_match(self):
        ltm_module = ConcreteLongTermMemoryModule(message_bus=self.bus, module_id=self.ltm_module_id)
        async def run_test_logic():
            self.bus.subscribe(self.test_querier_id, "LTMQueryResult", self._ltm_query_result_listener)
            ltm_module.add_episode("A quiet day indoors.")

            query_payload = LTMQueryPayload(
                requester_module_id=self.test_querier_id,
                query_type="episodic_keyword_search",
                query_content="non_existent_keyword_search"
            )
            query_message = GenericMessage(source_module_id=self.test_querier_id, message_type="LTMQuery", payload=query_payload)
            self.bus.publish(query_message)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_ltm_results), 1)
            payload: LTMQueryResultPayload = self.received_ltm_results[0].payload
            self.assertTrue(payload.success_status)
            self.assertEqual(len(payload.results), 0)
        asyncio.run(run_test_logic())

    def test_handle_unsupported_query_type(self):
        ltm_module = ConcreteLongTermMemoryModule(message_bus=self.bus, module_id=self.ltm_module_id)
        async def run_test_logic():
            self.bus.subscribe(self.test_querier_id, "LTMQueryResult", self._ltm_query_result_listener)
            query_payload = LTMQueryPayload(
                requester_module_id=self.test_querier_id,
                query_type="predict_future_event", # Unsupported
                query_content="will it rain?"
            )
            query_message = GenericMessage(source_module_id=self.test_querier_id, message_type="LTMQuery", payload=query_payload)
            self.bus.publish(query_message)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_ltm_results), 1)
            payload: LTMQueryResultPayload = self.received_ltm_results[0].payload
            self.assertFalse(payload.success_status)
            self.assertIsNotNone(payload.error_message)
            self.assertIn("Unsupported LTM query_type", payload.error_message)
        asyncio.run(run_test_logic())

    def test_handle_malformed_query_payload(self):
        ltm_module = ConcreteLongTermMemoryModule(message_bus=self.bus, module_id=self.ltm_module_id)
        async def run_test_logic():
            self.bus.subscribe(self.test_querier_id, "LTMQueryResult", self._ltm_query_result_listener)

            # Payload is not an LTMQueryPayload instance
            malformed_payload = {"some_unexpected_dict_key": "value", "query_id": "q_malformed"}
            query_message = GenericMessage(source_module_id=self.test_querier_id, message_type="LTMQuery", payload=malformed_payload)

            self.bus.publish(query_message)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_ltm_results), 1)
            payload: LTMQueryResultPayload = self.received_ltm_results[0].payload
            self.assertFalse(payload.success_status)
            self.assertIsNotNone(payload.error_message)
            self.assertIn("Payload is not an LTMQueryPayload instance", payload.error_message)
            # The LTM module tries to get query_id from the payload if it's a dict, even if malformed.
            self.assertEqual(payload.query_id, "q_malformed")
        asyncio.run(run_test_logic())

    def test_initialization_without_bus(self):
        ltm_no_bus = ConcreteLongTermMemoryModule(message_bus=None, module_id="LTM_NoBus")
        status = ltm_no_bus.get_status()
        self.assertFalse(status["message_bus_configured"])
        # Check if handle_ltm_query_message (if called directly by mistake) would fail gracefully
        # This is more of a module robustness check than a bus integration test.
        # For now, just checking initialization status is sufficient for this test name.
        self.assertIsNotNone(ltm_no_bus) # Basic check it initialized

    def test_get_module_status(self):
        ltm_module = ConcreteLongTermMemoryModule(message_bus=self.bus, module_id=self.ltm_module_id)
        ltm_module.add_semantic_node("s1", "S1", "t")
        ltm_module.add_episode("ep1")

        # Simulate a bus query being handled
        ltm_module._subcomponent_status['semantic_graph']['bus_queries_handled'] = 1

        status = ltm_module.get_status()
        self.assertEqual(status["module_id"], self.ltm_module_id)
        self.assertTrue(status["message_bus_configured"])
        self.assertEqual(status["direct_ltm_structures_status"]["semantic_graph_nodes"], 1)
        self.assertEqual(status["direct_ltm_structures_status"]["episodic_memory_count"], 1)
        self.assertEqual(status["query_counts_overview"]["semantic_graph"]["bus_queries_handled"], 1)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

```
