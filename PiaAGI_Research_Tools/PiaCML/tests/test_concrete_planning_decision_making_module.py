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
        self.received_ethical_review_requests: List[GenericMessage] = [] # New

        self.pdm_module = ConcretePlanningAndDecisionMakingModule(message_bus=self.bus, module_id=self.pdm_module_id)
        # Subscribe listeners here if they are general enough for all tests in the class
        self.bus.subscribe(self.pdm_module_id, "ActionCommand", self._action_command_listener)
        self.bus.subscribe(self.pdm_module_id, "LTMQuery", self._ltm_query_listener)
        self.bus.subscribe(self.pdm_module_id, "EthicalReviewRequest", self._ethical_review_listener)


    def _action_command_listener(self, message: GenericMessage):
        if isinstance(message.payload, ActionCommandPayload):
            self.received_action_commands.append(message)

    def _ltm_query_listener(self, message: GenericMessage):
        if isinstance(message.payload, LTMQueryPayload):
            self.received_ltm_queries.append(message)

    def _ethical_review_listener(self, message: GenericMessage): # New
        # Assuming EthicalReviewRequest has a dict payload as per recent refactoring
        if message.message_type == "EthicalReviewRequest" and isinstance(message.payload, dict):
            self.received_ethical_review_requests.append(message)

    def tearDown(self):
        self.received_action_commands.clear()
        self.received_ltm_queries.clear()
        self.received_ethical_review_requests.clear() # New

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

    # --- Tests for Advanced Logic from Recent Refactoring ---

    def test_plan_retrieval_from_ltm(self):
        pdm_module = self.pdm_module # Use the one from setUp for consistent bus interactions
        async def run_test_logic():
            ltm_plan_query_id = "ltm_plan_q_world_peace"
            goal_desc_for_ltm_plan = "achieve lasting world peace"
            ltm_plan_steps = [
                {"action_type": "diplomacy_initiative", "parameters": {"target_region": "global"}},
                {"action_type": "resource_allocation", "parameters": {"type": "education", "scope": "global"}, "expected_outcome_summary": "Improved global understanding"}
            ]
            # Pre-populate LTM results
            pdm_module._ltm_query_results[ltm_plan_query_id] = LTMQueryResultPayload(
                query_id=ltm_plan_query_id,
                results=[MemoryItem(item_id="plan_wp_v1", content=ltm_plan_steps, metadata={"plan_name": "WorldPeacePlan"})],
                success_status=True,
                query_metadata={"query_type": "get_action_plan_for_goal", "original_query_content": goal_desc_for_ltm_plan}
            )

            goal = GoalUpdatePayload("g_world_peace", goal_desc_for_ltm_plan, 0.99, "ACTIVE", "UN")
            self.bus.publish(GenericMessage(pdm_module.get_module_status()["module_id"], "GoalUpdate", goal)) # Use module_id from status
            await asyncio.sleep(0.01)

            pdm_module.process_highest_priority_goal()
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_action_commands), 2, "Expected 2 actions from LTM plan.")
            self.assertEqual(self.received_action_commands[0].payload.action_type, "diplomacy_initiative")
            self.assertEqual(self.received_action_commands[0].payload.parameters.get("target_region"), "global")
            self.assertTrue("ltm_retrieved" in self.received_action_commands[0].payload.parameters.get("plan_source", ""))
            self.assertEqual(self.received_action_commands[1].payload.action_type, "resource_allocation")
            self.assertEqual(self.received_action_commands[1].payload.expected_outcome_summary, "Improved global understanding")
        asyncio.run(run_test_logic())

    def test_ltm_query_for_missing_plan(self):
        pdm_module = self.pdm_module
        async def run_test_logic():
            goal_desc = "resolve_quantum_paradox"
            goal = GoalUpdatePayload("g_quantum", goal_desc, 0.9, "ACTIVE", "PhysicsDept")

            # Ensure no relevant plan exists in LTM results for this goal
            pdm_module._ltm_query_results.clear()
            pdm_module._awaiting_plan_for_goal.clear()

            self.bus.publish(GenericMessage(pdm_module.get_module_status()["module_id"], "GoalUpdate", goal))
            await asyncio.sleep(0.01)
            pdm_module.process_highest_priority_goal()
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_ltm_queries), 1, "Expected an LTMQuery to be published.")
            ltm_query_payload: LTMQueryPayload = self.received_ltm_queries[0].payload
            self.assertEqual(ltm_query_payload.query_type, "get_action_plan_for_goal")
            self.assertEqual(ltm_query_payload.query_content, goal_desc)
            self.assertIn("g_quantum", pdm_module._awaiting_plan_for_goal)
            self.assertEqual(pdm_module._awaiting_plan_for_goal["g_quantum"], ltm_query_payload.query_id)

            self.assertTrue(len(self.received_action_commands) >= 1, "Expected default actions.")
            self.assertTrue("(LTM query initiated)" in self.received_action_commands[0].payload.parameters.get("plan_source", ""))
        asyncio.run(run_test_logic())

    def test_ethical_review_request_publication_for_sensitive_goal(self):
        pdm_module = self.pdm_module
        async def run_test_logic():
            goal_desc = "delete user_profile_for_user123" # Contains "delete" and "user"
            goal = GoalUpdatePayload("g_sensitive_delete", goal_desc, 0.8, "ACTIVE", "Admin")
            self.bus.publish(GenericMessage(pdm_module.get_module_status()["module_id"], "GoalUpdate", goal))
            await asyncio.sleep(0.01)
            pdm_module.process_highest_priority_goal()
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_ethical_review_requests), 1, "Expected an EthicalReviewRequest.")
            review_request_msg = self.received_ethical_review_requests[0]
            self.assertEqual(review_request_msg.message_type, "EthicalReviewRequest")
            payload = review_request_msg.payload
            self.assertIn("request_id", payload)
            self.assertEqual(payload["action_proposal"]["reason"], f"Executing plan for goal: {goal_desc} (ID: g_sensitive_delete)")
            self.assertTrue(len(payload["action_proposal"]["plan_summary"]) > 0) # Default plan summary
            self.assertEqual(payload["context"]["goal_id"], "g_sensitive_delete")
            self.assertTrue(len(self.received_action_commands) >= 1, "Actions should still be dispatched.")
        asyncio.run(run_test_logic())

    def test_handle_ltm_query_result_for_awaited_plan(self):
        pdm_module = self.pdm_module
        async def run_test_logic():
            goal_id_await = "g_await_plan"
            goal_desc_await = "design_new_propulsion_system"

            # Step 1: Trigger LTM query for a plan (similar to test_ltm_query_for_missing_plan)
            pdm_module._ltm_query_results.clear()
            pdm_module._awaiting_plan_for_goal.clear()
            goal_await = GoalUpdatePayload(goal_id_await, goal_desc_await, 0.88, "ACTIVE", "Engineering")
            self.bus.publish(GenericMessage(pdm_module.get_module_status()["module_id"], "GoalUpdate", goal_await))
            await asyncio.sleep(0.01)
            pdm_module.process_highest_priority_goal() # This will send the LTM Query
            await asyncio.sleep(0.01)

            self.assertIn(goal_id_await, pdm_module._awaiting_plan_for_goal)
            ltm_query_id_for_awaited_plan = pdm_module._awaiting_plan_for_goal[goal_id_await]
            initial_log_count = len(pdm_module._log)

            # Step 2: Simulate LTM sending back the result for this query
            ltm_plan_steps = [{"action_type": "research_theories"}, {"action_type": "simulate_designs"}]
            ltm_result_payload = LTMQueryResultPayload(
                query_id=ltm_query_id_for_awaited_plan,
                results=[MemoryItem(item_id="propulsion_plan_v1", content=ltm_plan_steps)],
                success_status=True,
                query_metadata={"query_type": "get_action_plan_for_goal", "original_query_content": goal_desc_await}
            )
            # Directly call the handler as if the message came from the bus
            pdm_module._handle_ltm_query_result_message(GenericMessage("LTMSys", "LTMQueryResult", ltm_result_payload))
            await asyncio.sleep(0.01) # Give handler time if it had async ops (though current one is sync)

            self.assertNotIn(goal_id_await, pdm_module._awaiting_plan_for_goal, "Goal ID should be cleared from awaiting list.")
            self.assertTrue(any(f"LTM Plan result received for QueryID '{ltm_query_id_for_awaited_plan}'" in log_msg for log_msg in pdm_module._log[initial_log_count:]))
            self.assertTrue(any(f"Goal '{goal_id_await}' is still active. A re-plan could be triggered" in log_msg for log_msg in pdm_module._log[initial_log_count:]))

        asyncio.run(run_test_logic())

    def test_internal_conceptual_plan_generation_and_selection(self):
        pdm_module = self.pdm_module
        async def run_test_logic():
            self.received_action_commands.clear()
            self.received_ltm_queries.clear()
            self.received_ethical_review_requests.clear()
            pdm_module._log.clear()
            pdm_module._ltm_query_results.clear()
            pdm_module._awaiting_plan_for_goal.clear()

            goal_desc = "investigate_strange_signal"
            goal = GoalUpdatePayload("g_internal_plan", goal_desc, 0.75, "ACTIVE", "ScienceTeam")

            # Publish goal to PDM
            self.bus.publish(GenericMessage(pdm_module.get_module_status()["module_id"], "GoalUpdate", goal))
            await asyncio.sleep(0.01) # Allow PDM to process goal update

            pdm_module.process_highest_priority_goal()
            await asyncio.sleep(0.01) # Allow PDM to process and dispatch

            # Assertions
            # 1. Check logs for internal plan generation
            self.assertTrue(any("No LTM plan retrieved. Starting conceptual internal plan generation." in log for log in pdm_module._log))
            self.assertTrue(any("Generated internal candidate 'internal_direct_plan'" in log for log in pdm_module._log))
            self.assertTrue(any("Generated internal candidate 'internal_cautious_plan'" in log for log in pdm_module._log))
            # Exploratory plan might not be generated if LTM query was already attempted or not deemed necessary by simple heuristic

            # 2. Check logs for conceptual evaluation of candidates
            self.assertTrue(any("Evaluating Candidate Plan" in log and "'internal_direct_plan'" in log for log in pdm_module._log))
            self.assertTrue(any("Conceptual WM Eval:" in log for log in pdm_module._log if "'internal_direct_plan'" in log)) # Check one detail for one plan
            self.assertTrue(any("Conceptual Self-Model Eval:" in log for log in pdm_module._log if "'internal_direct_plan'" in log))
            self.assertTrue(any("Conceptual Emotion Influence:" in log for log in pdm_module._log if "'internal_direct_plan'" in log))
            self.assertTrue(any("Conceptual LTM Past Experience:" in log for log in pdm_module._log if "'internal_direct_plan'" in log))
            self.assertTrue(any("Conceptual Evaluation Score for 'internal_direct_plan'" in log for log in pdm_module._log))

            self.assertTrue(any("Evaluating Candidate Plan" in log and "'internal_cautious_plan'" in log for log in pdm_module._log))

            # 3. Check logs for selection of an internal plan
            # The exact selected plan depends on random elements in conceptual eval, so check for general selection log
            selected_log_found = False
            selected_plan_id = None
            for log_entry in pdm_module._log:
                if "Selected plan '" in log_entry and "internal_" in log_entry: # Check if an internal plan was selected
                    selected_log_found = True
                    # Extract selected plan id for verifying dispatched actions (conceptual)
                    try:
                        selected_plan_id = log_entry.split("'")[1] # e.g., "Selected plan 'internal_direct_plan'..."
                    except IndexError:
                        pass # Should not happen if log format is consistent
                    break
            self.assertTrue(selected_log_found, "Log message for selecting an internal plan not found.")

            # 4. Verify dispatched actions correspond to a known internal plan's structure
            self.assertTrue(len(self.received_action_commands) >= 1, "No action commands received for selected internal plan.")

            if selected_plan_id: # If we successfully extracted the selected plan's ID from logs
                first_action_payload = self.received_action_commands[0].payload
                self.assertIn(selected_plan_id.replace("internal_", "").replace("_plan",""), first_action_payload.action_type,
                              f"Dispatched action type '{first_action_payload.action_type}' does not seem to match selected plan ID '{selected_plan_id}'")
                self.assertIn("internal_generation", first_action_payload.parameters.get("plan_source", ""),
                              "Plan source for dispatched action should indicate internal generation.")

        asyncio.run(run_test_logic())

    def test_ltm_plan_fails_conceptual_ethics_falls_back_to_internal(self):
        pdm_module = self.pdm_module
        async def run_test_logic():
            self.received_action_commands.clear()
            pdm_module._log.clear()
            pdm_module._ltm_query_results.clear()
            pdm_module._awaiting_plan_for_goal.clear()

            goal_desc = "achieve_goal_with_sensitive_ltm_plan"
            goal = GoalUpdatePayload("g_ltm_ethical_fail", goal_desc, 0.9, "ACTIVE", "TestSystem")

            # Setup LTM plan with a sensitive keyword
            ltm_plan_query_id = "q_sensitive_plan"
            sensitive_ltm_plan_steps = [
                {"action_type": "access_all_user_data", "parameters": {"reason": "analysis"}}, # Sensitive part
                {"action_type": "delete_user_data_for_compliance", "parameters": {"user_id": "user123"}} # Sensitive
            ]
            pdm_module._ltm_query_results[ltm_plan_query_id] = LTMQueryResultPayload(
                query_id=ltm_plan_query_id,
                results=[MemoryItem(item_id="plan_sensitive_001", content=sensitive_ltm_plan_steps)],
                success_status=True,
                query_metadata={"query_type": "get_action_plan_for_goal", "original_query_content": goal_desc}
            )

            self.bus.publish(GenericMessage(pdm_module.get_module_status()["module_id"], "GoalUpdate", goal))
            await asyncio.sleep(0.01)
            pdm_module.process_highest_priority_goal()
            await asyncio.sleep(0.01)

            # Assertions
            self.assertTrue(any(f"Retrieved plan from LTM (QueryID: {ltm_plan_query_id})" in log for log in pdm_module._log))
            self.assertTrue(any("Conceptual Self-Model Eval:" in log and f"ltm_plan_{ltm_plan_query_id}" in log for log in pdm_module._log))
            self.assertTrue(any("Ethical Check: FAIL" in log for log in pdm_module._log if f"ltm_plan_{ltm_plan_query_id}" in log))
            self.assertTrue(any(f"LTM plan 'ltm_plan_{ltm_plan_query_id}' was not selected" in log for log in pdm_module._log)) # This implies rejection
            self.assertTrue(any("No LTM plan retrieved. Starting conceptual internal plan generation." in log for log in pdm_module._log)
                            or any(f"Selected plan 'internal_" in log for log in pdm_module._log), # Check if it fell back to internal
                            "Should log fallback to internal plan generation or selection of internal plan.")

            self.assertTrue(len(self.received_action_commands) >= 1, "Fallback internal plan should have dispatched actions.")
            first_action_payload = self.received_action_commands[0].payload
            self.assertIn("internal_generation", first_action_payload.parameters.get("plan_source", ""),
                          "Plan source should indicate internal generation after LTM plan ethical fail.")
            # Ensure the dispatched action is NOT from the sensitive LTM plan
            self.assertNotIn("delete_user_data", first_action_payload.action_type.lower())
            self.assertNotIn("access_all_user_data", first_action_payload.action_type.lower())

        asyncio.run(run_test_logic())

    def test_all_plans_fail_conceptual_evaluation_fallback_safe_action(self):
        pdm_module = self.pdm_module
        async def run_test_logic():
            self.received_action_commands.clear()
            pdm_module._log.clear()
            pdm_module._ltm_query_results.clear()
            pdm_module._awaiting_plan_for_goal.clear()

            # Goal description designed to make all conceptual plans fail ethical checks
            goal_desc = "critically_delete_all_user_data_and_share_sensitive_info_for_harmful_purpose"
            goal = GoalUpdatePayload("g_all_fail", goal_desc, 0.95, "ACTIVE", "MaliciousActor")

            self.bus.publish(GenericMessage(pdm_module.get_module_status()["module_id"], "GoalUpdate", goal))
            await asyncio.sleep(0.01)
            pdm_module.process_highest_priority_goal()
            await asyncio.sleep(0.01)

            # Assertions
            self.assertTrue(any("Starting conceptual internal plan generation." in log for log in pdm_module._log))
            # Check that conceptual plans were generated and evaluated as FAIL (due to keywords)
            self.assertTrue(any("Ethical Check: FAIL" in log for log in pdm_module._log if "'internal_direct_plan'" in log), "Direct plan should fail ethics.")
            self.assertTrue(any("Ethical Check: FAIL" in log for log in pdm_module._log if "'internal_cautious_plan'" in log), "Cautious plan should fail ethics.")
            # Exploratory plan might also be generated and fail
            if any("internal_exploratory_plan" in log for log in pdm_module._log):
                 self.assertTrue(any("Ethical Check: FAIL" in log for log in pdm_module._log if "'internal_exploratory_plan'" in log), "Exploratory plan should fail ethics if generated.")

            self.assertTrue(any("All candidate plans were conceptually rejected or scored too low. Generating critical fallback action." in log for log in pdm_module._log))

            self.assertEqual(len(self.received_action_commands), 1, "Expected one fallback action.")
            fallback_action_payload = self.received_action_commands[0].payload
            self.assertEqual(fallback_action_payload.action_type, "request_assistance_no_valid_plan")
            self.assertIn("All plans failed conceptual evaluation", fallback_action_payload.parameters.get("reason", ""))
            self.assertEqual(fallback_action_payload.parameters.get("plan_source"), "critical_fallback_evaluation_reject")

        asyncio.run(run_test_logic())

    def test_conceptual_evaluation_prefers_higher_scoring_internal_plan(self):
        pdm_module = self.pdm_module
        async def run_test_logic():
            self.received_action_commands.clear()
            pdm_module._log.clear()
            pdm_module._ltm_query_results.clear()
            pdm_module._awaiting_plan_for_goal.clear()

            # Neutral goal description
            goal_desc = "achieve_neutral_goal_x"
            goal = GoalUpdatePayload("g_neutral_eval", goal_desc, 0.7, "ACTIVE", "TestSystem")

            # Set a slightly positive emotional state if it influences conceptual scoring
            pdm_module._current_emotional_state = EmotionalStateChangePayload(
                current_emotion_profile={"valence": 0.2, "arousal": 0.3, "dominance": 0.1},
                intensity=0.3
            )

            self.bus.publish(GenericMessage(pdm_module.get_module_status()["module_id"], "GoalUpdate", goal))
            await asyncio.sleep(0.01)

            # To make this test more deterministic without altering PDM code for testing:
            # We will rely on the fact that multiple conceptual plans are generated
            # and each gets a conceptual evaluation_score logged.
            # We will then check that a plan with a higher logged score is selected.
            # The randomness in evaluation means we can't predetermine *which* plan,
            # but we can check the principle.

            # For more robust testing of specific scoring, one might need to mock parts of the
            # conceptual evaluation within PDM, or make the evaluation scoring more deterministic.
            # Current PDM code uses uuid.uuid4().int % len(options) for some conceptual checks,
            # making it hard to guarantee one plan will score higher without many iterations or mocks.

            # The goal here is to see the selection process based on *some* logged difference.
            # We'll look for logs of multiple evaluations and then a selection log.

            pdm_module.process_highest_priority_goal()
            await asyncio.sleep(0.01)

            # Assertions
            self.assertTrue(any("Starting conceptual internal plan generation." in log for log in pdm_module._log))

            evaluated_plan_scores = {} # Store plan_id -> score
            for log_entry in pdm_module._log:
                if "Conceptual Evaluation Score for '" in log_entry:
                    try:
                        parts = log_entry.split("'")
                        plan_id = parts[1]
                        score_str = parts[2].split(": ")[1]
                        evaluated_plan_scores[plan_id] = float(score_str)
                    except (IndexError, ValueError):
                        continue # Ignore malformed log lines for this check

            self.assertTrue(len(evaluated_plan_scores) >= 2,
                            f"Expected at least 2 internal plans to be evaluated and have scores logged. Found: {evaluated_plan_scores}")

            selected_plan_id_from_log = None
            selected_plan_score_from_log = -float('inf')
            for log_entry in pdm_module._log:
                if "Selected plan '" in log_entry and "with score" in log_entry:
                    try:
                        parts = log_entry.split("'")
                        selected_plan_id_from_log = parts[1]
                        score_str = log_entry.split("with score ")[1].split(".")[0] # Get the number part
                        selected_plan_score_from_log = float(score_str + "." + log_entry.split("with score ")[1].split(".")[1][:3]) # Reconstruct float
                        break
                    except (IndexError, ValueError):
                        continue

            self.assertIsNotNone(selected_plan_id_from_log, "Could not find log entry for selected plan with score.")

            # Verify that the selected plan's score matches one of the evaluated scores
            # And that it is indeed the highest among the valid (score > -0.5) candidates.
            self.assertIn(selected_plan_id_from_log, evaluated_plan_scores, "Selected plan ID was not found in evaluated plan scores.")
            self.assertAlmostEqual(evaluated_plan_scores[selected_plan_id_from_log], selected_plan_score_from_log, places=3,
                                   msg="Score of selected plan in log does not match its evaluation score.")

            highest_valid_score = -float('inf')
            for plan_id, score in evaluated_plan_scores.items():
                if score > -0.5: # Considering valid plans
                    if score > highest_valid_score:
                        highest_valid_score = score

            self.assertAlmostEqual(selected_plan_score_from_log, highest_valid_score, places=3,
                                   msg=f"Selected plan score {selected_plan_score_from_log} is not the highest valid score {highest_valid_score} among conceptual evaluations. Scores: {evaluated_plan_scores}")

            self.assertTrue(len(self.received_action_commands) >= 1, "No actions dispatched for the selected plan.")
            # Further check if dispatched actions match 'selected_plan_id_from_log' if needed.
            first_action_of_selected = self.received_action_commands[0].payload
            self.assertIn(selected_plan_id_from_log.replace("internal_", "").replace("_plan",""), first_action_of_selected.action_type,
                          "Dispatched action doesn't seem to correspond to the logged selected plan.")

        asyncio.run(run_test_logic())

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
```
