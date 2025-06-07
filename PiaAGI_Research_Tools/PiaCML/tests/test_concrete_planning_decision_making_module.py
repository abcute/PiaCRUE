import unittest
import asyncio
import uuid
from collections import deque # For checking _current_percepts type
from typing import List, Any, Dict
import time # For timestamps
from datetime import datetime, timezone # For timestamps in payloads

# Adjust imports
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    from PiaAGI_Research_Tools.PiaCML.message_bus import MessageBus
    from PiaAGI_Research_Tools.PiaCML.core_messages import (
        GenericMessage, GoalUpdatePayload, PerceptDataPayload, LTMQueryResultPayload,
        EmotionalStateChangePayload, AttentionFocusUpdatePayload, ActionCommandPayload, LTMQueryPayload, MemoryItem
    )
    from PiaAGI_Research_Tools.PiaCML.concrete_planning_decision_making_module import ConcretePlanningAndDecisionMakingModule
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from message_bus import MessageBus
    from core_messages import (
        GenericMessage, GoalUpdatePayload, PerceptDataPayload, LTMQueryResultPayload,
        EmotionalStateChangePayload, AttentionFocusUpdatePayload, ActionCommandPayload, LTMQueryPayload, MemoryItem
    )
    from concrete_planning_decision_making_module import ConcretePlanningAndDecisionMakingModule

class TestConcretePlanningDecisionMakingModuleIntegration(unittest.TestCase):

    def setUp(self):
        self.bus = MessageBus()
        self.pdm_module_id = f"TestPDMModule_{str(uuid.uuid4())[:8]}"
        # Module instantiated per test method for a clean state
        self.received_action_commands: List[GenericMessage] = []
        self.received_ltm_queries: List[GenericMessage] = []

    def _action_command_listener(self, message: GenericMessage):
        if isinstance(message.payload, ActionCommandPayload):
            self.received_action_commands.append(message)

    def _ltm_query_listener(self, message: GenericMessage):
        if isinstance(message.payload, LTMQueryPayload):
            self.received_ltm_queries.append(message)

    def tearDown(self):
        self.received_action_commands.clear()
        self.received_ltm_queries.clear()

    # --- Test Subscription Handlers and Internal State Updates ---
    def test_handle_goal_update_updates_active_goals(self):
        pdm_module = ConcretePlanningAndDecisionMakingModule(message_bus=self.bus, module_id=self.pdm_module_id)
        async def run_test_logic():
            goal1 = GoalUpdatePayload("g1", "Goal 1", 0.8, "ACTIVE", "Test")
            goal2 = GoalUpdatePayload("g2", "Goal 2", 0.9, "PENDING", "Test")
            bus_msg1 = GenericMessage(self.pdm_module_id, "GoalUpdate", goal1)
            bus_msg2 = GenericMessage(self.pdm_module_id, "GoalUpdate", goal2)

            self.bus.publish(bus_msg1)
            self.bus.publish(bus_msg2)
            await asyncio.sleep(0.01)

            self.assertEqual(len(pdm_module._active_goals), 2)
            self.assertEqual(pdm_module._active_goals[0].goal_id, "g2") # Sorted by priority
            self.assertEqual(pdm_module._active_goals[1].goal_id, "g1")

            # Test update
            goal2_updated = GoalUpdatePayload("g2", "Goal 2 Updated", 0.7, "ACTIVE", "Test")
            bus_msg2_updated = GenericMessage(self.pdm_module_id, "GoalUpdate", goal_payload2_updated)
            self.bus.publish(bus_msg2_updated)
            await asyncio.sleep(0.01)

            self.assertEqual(len(pdm_module._active_goals), 2)
            self.assertEqual(pdm_module._active_goals[0].goal_id, "g1") # g1 now higher prio
            self.assertEqual(pdm_module._active_goals[1].goal_id, "g2")
            self.assertEqual(pdm_module._active_goals[1].priority, 0.7)

            # Test removal by status
            goal1_achieved = GoalUpdatePayload("g1", "Goal 1", 0.8, "ACHIEVED", "Test")
            bus_msg1_achieved = GenericMessage(self.pdm_module_id, "GoalUpdate", goal1_achieved)
            self.bus.publish(bus_msg1_achieved)
            await asyncio.sleep(0.01)
            self.assertEqual(len(pdm_module._active_goals), 1)
            self.assertEqual(pdm_module._active_goals[0].goal_id, "g2")

        asyncio.run(run_test_logic())

    def test_handle_percept_data_updates_current_percepts(self):
        pdm_module = ConcretePlanningAndDecisionMakingModule(message_bus=self.bus, module_id=self.pdm_module_id)
        async def run_test_logic():
            percept1 = PerceptDataPayload("p1", "text", "Percept 1", datetime.now(timezone.utc))
            bus_msg1 = GenericMessage(self.pdm_module_id, "PerceptData", percept1)
            self.bus.publish(bus_msg1)
            await asyncio.sleep(0.01)
            self.assertEqual(len(pdm_module._current_percepts), 1)
            self.assertEqual(pdm_module._current_percepts[0].percept_id, "p1")

            # Test deque maxlen
            for i in range(pdm_module.MAX_PERCEPTS_HISTORY + 5):
                p = PerceptDataPayload(f"p{i+2}", "text", f"Percept {i+2}", datetime.now(timezone.utc))
                self.bus.publish(GenericMessage(self.pdm_module_id, "PerceptData", p))
            await asyncio.sleep(0.01)
            self.assertEqual(len(pdm_module._current_percepts), pdm_module.MAX_PERCEPTS_HISTORY)
            self.assertEqual(pdm_module._current_percepts[-1].percept_id, f"p{pdm_module.MAX_PERCEPTS_HISTORY + 1}") # p2 to p11, last is p11
            self.assertEqual(pdm_module._current_percepts[0].percept_id, "p2")

        asyncio.run(run_test_logic())

    def test_handle_ltm_query_result_updates_results(self):
        pdm_module = ConcretePlanningAndDecisionMakingModule(message_bus=self.bus, module_id=self.pdm_module_id)
        async def run_test_logic():
            ltm_res1 = LTMQueryResultPayload("q1", [MemoryItem("m1","content1")], True)
            bus_msg1 = GenericMessage(self.pdm_module_id, "LTMQueryResult", ltm_res1)
            self.bus.publish(bus_msg1)
            await asyncio.sleep(0.01)
            self.assertIn("q1", pdm_module._ltm_query_results)
            self.assertEqual(pdm_module._ltm_query_results["q1"].results[0].item_id, "m1")
        asyncio.run(run_test_logic())

    def test_handle_emotional_state_change_updates_emotion(self):
        pdm_module = ConcretePlanningAndDecisionMakingModule(message_bus=self.bus, module_id=self.pdm_module_id)
        async def run_test_logic():
            emo_state = EmotionalStateChangePayload({"v":0.5, "a":0.3}, intensity=0.4)
            bus_msg = GenericMessage(self.pdm_module_id, "EmotionalStateChange", emo_state)
            self.bus.publish(bus_msg)
            await asyncio.sleep(0.01)
            self.assertIsNotNone(pdm_module._current_emotional_state)
            self.assertEqual(pdm_module._current_emotional_state.intensity, 0.4)
        asyncio.run(run_test_logic())

    def test_handle_attention_focus_update_updates_focus(self):
        pdm_module = ConcretePlanningAndDecisionMakingModule(message_bus=self.bus, module_id=self.pdm_module_id)
        async def run_test_logic():
            attn_focus = AttentionFocusUpdatePayload("item1", "goal_directed", 0.9, timestamp=datetime.now(timezone.utc))
            bus_msg = GenericMessage(self.pdm_module_id, "AttentionFocusUpdate", attn_focus)
            self.bus.publish(bus_msg)
            await asyncio.sleep(0.01)
            self.assertIsNotNone(pdm_module._current_attention_focus)
            self.assertEqual(pdm_module._current_attention_focus.focused_item_id, "item1")
        asyncio.run(run_test_logic())

    # --- Test Publishing LTMQuery ---
    def test_request_ltm_data_publishes_ltm_query(self):
        pdm_module = ConcretePlanningAndDecisionMakingModule(message_bus=self.bus, module_id=self.pdm_module_id)
        async def run_test_logic():
            self.bus.subscribe(self.pdm_module_id, "LTMQuery", self._ltm_query_listener)

            query_id = pdm_module.request_ltm_data("info about topic X", "semantic_search", target_memory_type="semantic")
            self.assertIsNotNone(query_id)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_ltm_queries), 1)
            msg = self.received_ltm_queries[0]
            self.assertEqual(msg.source_module_id, self.pdm_module_id)
            self.assertEqual(msg.message_type, "LTMQuery")

            payload: LTMQueryPayload = msg.payload
            self.assertEqual(payload.query_id, query_id)
            self.assertEqual(payload.requester_module_id, self.pdm_module_id)
            self.assertEqual(payload.query_content, "info about topic X")
            self.assertEqual(payload.query_type, "semantic_search")
            self.assertEqual(payload.target_memory_type, "semantic")
        asyncio.run(run_test_logic())

    # --- Test Publishing ActionCommand ---
    def test_process_goal_publishes_action_command(self):
        pdm_module = ConcretePlanningAndDecisionMakingModule(message_bus=self.bus, module_id=self.pdm_module_id)
        async def run_test_logic():
            self.bus.subscribe(self.pdm_module_id, "ActionCommand", self._action_command_listener)

            # Add a goal first
            goal = GoalUpdatePayload("g_act", "Goal for Action", 0.8, "ACTIVE", "Test")
            self.bus.publish(GenericMessage(self.pdm_module_id, "GoalUpdate", goal))
            await asyncio.sleep(0.01) # Ensure goal is processed

            pdm_module.process_highest_priority_goal()
            await asyncio.sleep(0.01)

            self.assertTrue(len(self.received_action_commands) >= 1)
            cmd_payload: ActionCommandPayload = self.received_action_commands[0].payload
            self.assertEqual(cmd_payload.parameters.get("goal_id"), "g_act")
            self.assertEqual(self.received_action_commands[0].source_module_id, self.pdm_module_id)
        asyncio.run(run_test_logic())

    def test_process_goal_action_varies_by_emotion(self):
        pdm_module = ConcretePlanningAndDecisionMakingModule(message_bus=self.bus, module_id=self.pdm_module_id)
        async def run_test_logic():
            self.bus.subscribe(self.pdm_module_id, "ActionCommand", self._action_command_listener)
            goal = GoalUpdatePayload("g_emo_plan", "Plan with emotion", 0.8, "ACTIVE", "Test")
            self.bus.publish(GenericMessage(self.pdm_module_id, "GoalUpdate", goal))

            # Publish negative emotion
            emo_state = EmotionalStateChangePayload({"valence": -0.7, "arousal": 0.6}, intensity=0.65) # Negative emotion
            self.bus.publish(GenericMessage(self.pdm_module_id, "EmotionalStateChange", emo_state))
            await asyncio.sleep(0.01)

            pdm_module.process_highest_priority_goal()
            await asyncio.sleep(0.01)

            self.assertTrue(len(self.received_action_commands) >= 1)
            cmd_payload: ActionCommandPayload = self.received_action_commands[0].payload
            self.assertTrue("cautious_action" in cmd_payload.action_type)
            self.assertEqual(cmd_payload.parameters.get("caution_level"), "high")
        asyncio.run(run_test_logic())

    def test_process_goal_action_varies_by_percept(self):
        pdm_module = ConcretePlanningAndDecisionMakingModule(message_bus=self.bus, module_id=self.pdm_module_id)
        async def run_test_logic():
            self.bus.subscribe(self.pdm_module_id, "ActionCommand", self._action_command_listener)
            goal = GoalUpdatePayload("g_percept_plan", "Plan with percept", 0.8, "ACTIVE", "Test")
            self.bus.publish(GenericMessage(self.pdm_module_id, "GoalUpdate", goal))

            # Publish urgent percept
            percept = PerceptDataPayload("p_urgent", "text", {"type":"linguistic_analysis", "text": "This is an urgent request!"}, datetime.now(timezone.utc))
            self.bus.publish(GenericMessage(self.pdm_module_id, "PerceptData", percept))
            await asyncio.sleep(0.01)

            pdm_module.process_highest_priority_goal()
            await asyncio.sleep(0.01)

            self.assertTrue(len(self.received_action_commands) >= 1)
            cmd_payload: ActionCommandPayload = self.received_action_commands[0].payload
            self.assertTrue("urgent_response_action" in cmd_payload.action_type)
            self.assertEqual(cmd_payload.parameters.get("urgency"), "critical")
        asyncio.run(run_test_logic())

    # --- Test No Bus Scenario ---
    def test_no_bus_operations_graceful(self):
        pdm_module_no_bus = ConcretePlanningAndDecisionMakingModule(message_bus=None, module_id="NoBusPDM")
        self.assertIsNone(pdm_module_no_bus.request_ltm_data("test", "test"))

        # Add a goal directly to its internal list for testing process_highest_priority_goal
        goal = GoalUpdatePayload("g_direct", "Direct Goal", 0.9, "ACTIVE", "Test")
        pdm_module_no_bus._active_goals.append(goal) # Manually set up state
        self.assertFalse(pdm_module_no_bus.process_highest_priority_goal()) # Should return False as it cannot publish
        self.assertEqual(len(self.received_action_commands), 0)
        self.assertEqual(len(self.received_ltm_queries), 0)

    def test_get_module_status(self):
        pdm_module = ConcretePlanningAndDecisionMakingModule(message_bus=self.bus, module_id=self.pdm_module_id)
        status = pdm_module.get_module_status()
        self.assertEqual(status["module_id"], self.pdm_module_id)
        self.assertTrue(status["message_bus_configured"])
        self.assertEqual(status["active_goals_count"], 0)
        self.assertEqual(status["recent_percepts_count"], 0)
        # ... other initial state checks

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
```
