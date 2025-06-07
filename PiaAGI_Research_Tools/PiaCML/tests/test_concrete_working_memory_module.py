import unittest
import asyncio
import uuid
import time # For timestamps
from typing import List, Any, Dict
from datetime import datetime, timezone # For payloads

# Adjust path for consistent imports
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    from PiaAGI_Research_Tools.PiaCML.message_bus import MessageBus
    from PiaAGI_Research_Tools.PiaCML.core_messages import (
        GenericMessage, PerceptDataPayload, LTMQueryResultPayload, GoalUpdatePayload,
        EmotionalStateChangePayload, AttentionFocusUpdatePayload, LTMQueryPayload, MemoryItem
    )
    from PiaAGI_Research_Tools.PiaCML.concrete_working_memory_module import ConcreteWorkingMemoryModule
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from message_bus import MessageBus
    from core_messages import (
        GenericMessage, PerceptDataPayload, LTMQueryResultPayload, GoalUpdatePayload,
        EmotionalStateChangePayload, AttentionFocusUpdatePayload, LTMQueryPayload, MemoryItem
    )
    from concrete_working_memory_module import ConcreteWorkingMemoryModule

class TestConcreteWorkingMemoryModuleIntegration(unittest.TestCase):

    def setUp(self):
        self.bus = MessageBus()
        self.wm_module_id = f"TestWMModule_{str(uuid.uuid4())[:8]}"
        # WM module instantiated in each test method for a clean state
        self.received_ltm_queries: List[GenericMessage] = []

    def _ltm_query_listener(self, message: GenericMessage):
        if isinstance(message.payload, LTMQueryPayload):
            self.received_ltm_queries.append(message)

    def tearDown(self):
        self.received_ltm_queries.clear()

    # --- Test Subscription Handlers and Workspace Updates ---
    def test_handle_percept_data_updates_workspace(self):
        wm_module = ConcreteWorkingMemoryModule(message_bus=self.bus, module_id=self.wm_module_id)
        async def run_test_logic():
            ts = datetime.now(timezone.utc)
            percept_payload = PerceptDataPayload(percept_id="p1", modality="text", content="User said hello", source_timestamp=ts)
            bus_msg = GenericMessage("PerceptSys", "PerceptData", percept_payload, message_id="percept_msg_id_1")

            self.bus.publish(bus_msg)
            await asyncio.sleep(0.01)

            workspace_items = wm_module.get_workspace_contents()
            self.assertEqual(len(workspace_items), 1)
            item = workspace_items[0]
            self.assertEqual(item["content"]["type"], "percept")
            self.assertEqual(item["content"]["modality"], "text")
            self.assertEqual(item["content"]["content"], "User said hello")
            self.assertEqual(item["content"]["id_from_source"], "p1")
            self.assertEqual(item["content"]["message_id"], "percept_msg_id_1")
            self.assertAlmostEqual(item["content"]["source_timestamp"].timestamp(), ts.timestamp(), delta=1)
            self.assertGreaterEqual(item["salience"], 0.8) # Default for percepts
            self.assertEqual(wm_module._handled_message_counts["PerceptData"], 1)
        asyncio.run(run_test_logic())

    def test_handle_ltm_query_result_updates_workspace(self):
        wm_module = ConcreteWorkingMemoryModule(message_bus=self.bus, module_id=self.wm_module_id)
        async def run_test_logic():
            results = [MemoryItem(item_id="res1", content="LTM data point", metadata={"source": "test_db"})]
            ltm_result_payload = LTMQueryResultPayload(query_id="q_wm_1", results=results, success_status=True)
            bus_msg = GenericMessage("LTMSys", "LTMQueryResult", ltm_result_payload)

            self.bus.publish(bus_msg)
            await asyncio.sleep(0.01)

            workspace_items = wm_module.get_workspace_contents()
            self.assertEqual(len(workspace_items), 1)
            item = workspace_items[0]
            self.assertEqual(item["content"]["type"], "ltm_result")
            self.assertEqual(item["content"]["query_id"], "q_wm_1")
            self.assertTrue(item["content"]["success"])
            self.assertTrue(len(item["content"]["results_summary"]) > 0)
            self.assertGreaterEqual(item["salience"], 0.7) # Default for LTM results
            self.assertEqual(wm_module._handled_message_counts["LTMQueryResult"], 1)
        asyncio.run(run_test_logic())

    def test_handle_goal_update_updates_workspace(self):
        wm_module = ConcreteWorkingMemoryModule(message_bus=self.bus, module_id=self.wm_module_id)
        async def run_test_logic():
            goal_payload = GoalUpdatePayload("g_wm", "Work on WM", 0.85, "ACTIVE", "MotSys")
            bus_msg = GenericMessage("MotSys", "GoalUpdate", goal_payload)

            self.bus.publish(bus_msg)
            await asyncio.sleep(0.01)

            workspace_items = wm_module.get_workspace_contents()
            self.assertEqual(len(workspace_items), 1)
            item = workspace_items[0]
            self.assertEqual(item["content"]["type"], "goal_info")
            self.assertEqual(item["content"]["goal_id"], "g_wm")
            self.assertEqual(item["content"]["priority"], 0.85)
            expected_salience = 0.6 + (0.85 * 0.4) # Salience logic from module
            self.assertAlmostEqual(item["salience"], expected_salience, places=2)
            self.assertEqual(wm_module._handled_message_counts["GoalUpdate"], 1)

            # Test update of existing goal
            goal_payload_updated = GoalUpdatePayload("g_wm", "Work on WM more", 0.9, "ACTIVE", "MotSys")
            bus_msg_updated = GenericMessage("MotSys", "GoalUpdate", goal_payload_updated)
            self.bus.publish(bus_msg_updated)
            await asyncio.sleep(0.01)

            workspace_items = wm_module.get_workspace_contents()
            self.assertEqual(len(workspace_items), 1) # Should update, not add new
            item_updated = workspace_items[0]
            self.assertEqual(item_updated["content"]["priority"], 0.9)
            self.assertEqual(item_updated["content"]["description"], "Work on WM more")

        asyncio.run(run_test_logic())

    def test_handle_emotional_state_change_updates_workspace(self):
        wm_module = ConcreteWorkingMemoryModule(message_bus=self.bus, module_id=self.wm_module_id)
        async def run_test_logic():
            emo_payload = EmotionalStateChangePayload({"v":0.1, "a":0.7}, 0.7)
            bus_msg = GenericMessage("EmoSys", "EmotionalStateChange", emo_payload)
            self.bus.publish(bus_msg)
            await asyncio.sleep(0.01)

            workspace_items = wm_module.get_workspace_contents()
            self.assertEqual(len(workspace_items), 1)
            item = workspace_items[0]
            self.assertEqual(item["content"]["type"], "emotion_state")
            self.assertEqual(item["content"]["intensity"], 0.7)
            self.assertAlmostEqual(item["salience"], 0.9, places=2) # Default for emotion
            self.assertEqual(wm_module._handled_message_counts["EmotionalStateChange"], 1)
        asyncio.run(run_test_logic())

    def test_handle_attention_focus_update_updates_workspace_and_boosts_salience(self):
        wm_module = ConcreteWorkingMemoryModule(message_bus=self.bus, module_id=self.wm_module_id)
        async def run_test_logic():
            # Add a target item first
            target_item_id_in_wm = wm_module.add_item_to_workspace(
                {"type": "goal_info", "goal_id": "focused_goal", "description": "Focus on this"},
                salience=0.5
            )
            initial_item = wm_module.get_item_by_id(target_item_id_in_wm)
            self.assertIsNotNone(initial_item)
            initial_salience = initial_item['salience']

            attn_payload = AttentionFocusUpdatePayload(focused_item_id="focused_goal", focus_type="goal_directed", intensity=0.8, timestamp=datetime.now(timezone.utc))
            bus_msg = GenericMessage("AttnSys", "AttentionFocusUpdate", attn_payload)
            self.bus.publish(bus_msg)
            await asyncio.sleep(0.01)

            workspace_items = wm_module.get_workspace_contents()
            # One for the item itself, one for the attention_focus event stored
            self.assertEqual(len(workspace_items), 2)

            attention_info_item = next((i for i in workspace_items if i["content"]["type"] == "attention_focus"), None)
            self.assertIsNotNone(attention_info_item)
            self.assertEqual(attention_info_item["content"]["focused_item_id"], "focused_goal")
            self.assertAlmostEqual(attention_info_item["salience"], 0.95, places=2)

            focused_goal_item = wm_module.get_item_by_id(target_item_id_in_wm)
            self.assertIsNotNone(focused_goal_item)
            expected_boosted_salience = min(1.0, initial_salience + (0.8 * 0.3))
            self.assertAlmostEqual(focused_goal_item['salience'], expected_boosted_salience, places=2)
            self.assertEqual(wm_module._handled_message_counts["AttentionFocusUpdate"], 1)
        asyncio.run(run_test_logic())

    # --- Test Publishing LTMQuery ---
    def test_trigger_ltm_query_publishes_message(self):
        wm_module = ConcreteWorkingMemoryModule(message_bus=self.bus, module_id=self.wm_module_id)
        async def run_test_logic():
            self.bus.subscribe(self.wm_module_id, "LTMQuery", self._ltm_query_listener) # WM subscribes to its own LTM queries for listener

            # Add a percept that might trigger a query
            percept_content = "raw text string that might need semantic details"
            wm_item_id = wm_module.add_item_to_workspace(
                {"type": "percept", "modality": "text", "content": percept_content},
                salience=0.7
            )

            query_id = wm_module.trigger_ltm_query_if_needed(wm_item_id, query_type="semantic_details")
            self.assertIsNotNone(query_id)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_ltm_queries), 1)
            msg = self.received_ltm_queries[0]
            self.assertEqual(msg.source_module_id, self.wm_module_id)
            self.assertEqual(msg.message_type, "LTMQuery")

            payload: LTMQueryPayload = msg.payload
            self.assertEqual(payload.query_id, query_id)
            self.assertEqual(payload.requester_module_id, self.wm_module_id)
            self.assertEqual(payload.query_content, percept_content)
            self.assertEqual(payload.query_type, "semantic_details")
            self.assertEqual(wm_module._ltm_queries_sent, 1)
        asyncio.run(run_test_logic())

    def test_trigger_ltm_query_no_query_needed(self):
        wm_module = ConcreteWorkingMemoryModule(message_bus=self.bus, module_id=self.wm_module_id)
        async def run_test_logic():
            self.bus.subscribe(self.wm_module_id, "LTMQuery", self._ltm_query_listener)
            # Add an item that is already detailed (e.g., an LTM result itself)
            wm_item_id = wm_module.add_item_to_workspace(
                {"type": "ltm_result", "query_id": "q_prev", "results_summary": []},
                salience=0.7
            )
            query_id = wm_module.trigger_ltm_query_if_needed(wm_item_id)
            self.assertIsNone(query_id)
            await asyncio.sleep(0.01)
            self.assertEqual(len(self.received_ltm_queries), 0)
            self.assertEqual(wm_module._ltm_queries_sent, 0)
        asyncio.run(run_test_logic())

    # --- Test No Bus Scenario ---
    def test_initialization_and_operation_without_bus(self):
        wm_no_bus = ConcreteWorkingMemoryModule(message_bus=None, module_id="NoBusWM")
        status = wm_no_bus.get_status()
        self.assertFalse(status["message_bus_configured"])

        # Add an item that could trigger a query
        item_id = wm_no_bus.add_item_to_workspace({"type": "percept", "content": "queryable content"}, 0.5)
        query_id = wm_no_bus.trigger_ltm_query_if_needed(item_id) # Should not crash
        self.assertIsNone(query_id)
        self.assertEqual(wm_no_bus._ltm_queries_sent, 0)

    # --- Test Capacity Management with Bus Inputs ---
    def test_workspace_capacity_management_with_bus_inputs(self):
        wm_module = ConcreteWorkingMemoryModule(message_bus=self.bus, module_id=self.wm_module_id, capacity=2)
        async def run_test_logic():
            # Publish 3 percepts, capacity is 2
            pd1 = PerceptDataPayload("p1", "text", "Percept 1 (low salience candidate)", datetime.now(timezone.utc))
            pd2 = PerceptDataPayload("p2", "text", "Percept 2 (mid salience candidate)", datetime.now(timezone.utc))
            pd3 = PerceptDataPayload("p3", "text", "Percept 3 (high salience)", datetime.now(timezone.utc))

            # Manually control salience via context for handler to pick up
            # The handler _handle_percept_data_message sets salience=0.8 by default.
            # To test eviction, we need to ensure items are added with different salience
            # or rely on oldest if salience is equal. Let's assume handler's default 0.8.
            # The capacity management removes the one with lowest salience. If all are 0.8, it's the oldest.

            self.bus.publish(GenericMessage("Src1", "PerceptData", pd1)) # Added first, salience 0.8
            await asyncio.sleep(0.005)
            self.bus.publish(GenericMessage("Src2", "PerceptData", pd2)) # Added second, salience 0.8
            await asyncio.sleep(0.005)

            self.assertEqual(len(wm_module.get_workspace_contents()), 2)

            self.bus.publish(GenericMessage("Src3", "PerceptData", pd3)) # Added third, salience 0.8. Should evict pd1.
            await asyncio.sleep(0.01)

            workspace_items = wm_module.get_workspace_contents()
            self.assertEqual(len(workspace_items), 2)
            item_contents_in_wm = [item["content"]["content"] for item in workspace_items]
            self.assertNotIn("Percept 1 (low salience candidate)", item_contents_in_wm)
            self.assertIn("Percept 2 (mid salience candidate)", item_contents_in_wm)
            self.assertIn("Percept 3 (high salience)", item_contents_in_wm)

        asyncio.run(run_test_logic())

    def test_get_module_status(self):
        wm_module = ConcreteWorkingMemoryModule(message_bus=self.bus, module_id=self.wm_module_id)
        status = wm_module.get_status()
        self.assertEqual(status["module_id"], self.wm_module_id)
        self.assertTrue(status["message_bus_configured"])
        self.assertEqual(status["current_size"], 0)
        self.assertEqual(status["capacity"], wm_module.DEFAULT_CAPACITY)
        self.assertEqual(status["ltm_queries_sent"], 0)
        self.assertEqual(status["processed_message_counts"]["PerceptData"], 0)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
```
