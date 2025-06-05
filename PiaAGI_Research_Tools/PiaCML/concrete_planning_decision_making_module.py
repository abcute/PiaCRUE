from typing import Any, Dict, List, Optional, Deque
import uuid
from collections import deque
import asyncio
import time # For timestamps in __main__
from datetime import datetime, timezone # For timestamps in __main__

try:
    from .base_planning_and_decision_making_module import BasePlanningAndDecisionMakingModule
    from .message_bus import MessageBus
    from .core_messages import (
        GenericMessage, GoalUpdatePayload, ActionCommandPayload,
        PerceptDataPayload, LTMQueryResultPayload, EmotionalStateChangePayload,
        AttentionFocusUpdatePayload, LTMQueryPayload, MemoryItem # Added MemoryItem for LTMQueryResult
    )
except ImportError:
    print("Warning: Running ConcretePlanningAndDecisionMakingModule with stubbed imports.")
    class BasePlanningAndDecisionMakingModule: pass
    MessageBus = None # type: ignore
    GenericMessage = object # type: ignore
    GoalUpdatePayload = object # type: ignore
    ActionCommandPayload = object # type: ignore
    PerceptDataPayload = object # type: ignore
    LTMQueryResultPayload = object # type: ignore
    EmotionalStateChangePayload = object # type: ignore
    AttentionFocusUpdatePayload = object # type: ignore
    LTMQueryPayload = object # type: ignore
    MemoryItem = object # type: ignore


class ConcretePlanningAndDecisionMakingModule(BasePlanningAndDecisionMakingModule):
    """
    A concrete implementation of the PDM module, integrated with the message bus
    to receive various types of information and dispatch action commands.
    """
    MAX_PERCEPTS_HISTORY = 10 # Max number of recent percepts to store
    MAX_LTM_RESULTS_TO_STORE = 20 # Max number of LTM query results to store

    def __init__(self,
                 message_bus: Optional[MessageBus] = None,
                 module_id: str = f"PlanningDecisionMakingModule_{str(uuid.uuid4())[:8]}"):
        """
        Initializes the ConcretePlanningAndDecisionMakingModule.
        """
        self._module_id = module_id
        self._message_bus = message_bus

        # Internal state
        self._active_goals: List[GoalUpdatePayload] = []
        self._current_percepts: Deque[PerceptDataPayload] = deque(maxlen=self.MAX_PERCEPTS_HISTORY)
        self._ltm_query_results: Dict[str, LTMQueryResultPayload] = {} # query_id -> payload
        self._current_emotional_state: Optional[EmotionalStateChangePayload] = None
        self._current_attention_focus: Optional[AttentionFocusUpdatePayload] = None

        bus_status_msg = "not configured"
        if self._message_bus:
            subscriptions = [
                ("GoalUpdate", self._handle_goal_update_message),
                ("PerceptData", self._handle_percept_data_message),
                ("LTMQueryResult", self._handle_ltm_query_result_message),
                ("EmotionalStateChange", self._handle_emotional_state_change_message),
                ("AttentionFocusUpdate", self._handle_attention_focus_update_message),
            ]
            subscribed_types = []
            try:
                core_types_available = all([GenericMessage, GoalUpdatePayload, PerceptDataPayload,
                                            LTMQueryResultPayload, EmotionalStateChangePayload, AttentionFocusUpdatePayload,
                                            ActionCommandPayload, LTMQueryPayload]) # Check all used types

                if core_types_available:
                    for msg_type, callback in subscriptions:
                        self._message_bus.subscribe(
                            module_id=self._module_id,
                            message_type=msg_type,
                            callback=callback
                        )
                        subscribed_types.append(msg_type)
                    if subscribed_types:
                        bus_status_msg = f"configured and subscribed to: {', '.join(subscribed_types)}"
                    else:
                        bus_status_msg = "configured but no subscriptions were made (check core types and subscription list)"
                else:
                    bus_status_msg = "configured but one or more core message types for subscription are not available"
            except Exception as e:
                bus_status_msg = f"configured but FAILED to subscribe: {e}"

        print(f"ConcretePlanningAndDecisionMakingModule '{self._module_id}' initialized. Message bus {bus_status_msg}.")

    # --- Message Handler Methods ---
    def _handle_goal_update_message(self, message: GenericMessage):
        if not isinstance(message.payload, GoalUpdatePayload):
            print(f"PDM ({self._module_id}): Received GoalUpdate with unexpected payload: {type(message.payload)}")
            return
        payload: GoalUpdatePayload = message.payload
        # print(f"PDM ({self._module_id}): Received GoalUpdate for '{payload.goal_id}', Status: {payload.status}, Prio: {payload.priority}")
        self._active_goals = [g for g in self._active_goals if g.goal_id != payload.goal_id]
        if payload.status.upper() in ["NEW", "ACTIVE", "UPDATED", "PENDING"]:
            self._active_goals.append(payload)
            self._active_goals.sort(key=lambda g: g.priority, reverse=True)

    def _handle_percept_data_message(self, message: GenericMessage):
        if not isinstance(message.payload, PerceptDataPayload):
            print(f"PDM ({self._module_id}): Received PerceptData with unexpected payload: {type(message.payload)}")
            return
        self._current_percepts.append(message.payload)

    def _handle_ltm_query_result_message(self, message: GenericMessage):
        if not isinstance(message.payload, LTMQueryResultPayload):
            print(f"PDM ({self._module_id}): Received LTMQueryResult with unexpected payload: {type(message.payload)}")
            return
        payload: LTMQueryResultPayload = message.payload
        if len(self._ltm_query_results) >= self.MAX_LTM_RESULTS_TO_STORE and payload.query_id not in self._ltm_query_results:
            # Simple eviction: remove the oldest if full (Python dicts are ordered from 3.7+)
            try:
                oldest_query_id = next(iter(self._ltm_query_results))
                del self._ltm_query_results[oldest_query_id]
            except StopIteration: # Should not happen if len > 0
                pass
        self._ltm_query_results[payload.query_id] = payload

    def _handle_emotional_state_change_message(self, message: GenericMessage):
        if not isinstance(message.payload, EmotionalStateChangePayload):
            print(f"PDM ({self._module_id}): Received EmotionalStateChange with unexpected payload: {type(message.payload)}")
            return
        self._current_emotional_state = message.payload

    def _handle_attention_focus_update_message(self, message: GenericMessage):
        if not isinstance(message.payload, AttentionFocusUpdatePayload):
            print(f"PDM ({self._module_id}): Received AttentionFocusUpdate with unexpected payload: {type(message.payload)}")
            return
        self._current_attention_focus = message.payload

    # --- LTM Querying ---
    def request_ltm_data(self, query_content: Any, query_type: str,
                         target_memory_type: Optional[str] = None,
                         parameters: Optional[Dict[str, Any]] = None) -> Optional[str]:
        if not self._message_bus or not LTMQueryPayload or not GenericMessage:
            print(f"PDM ({self._module_id}): Message bus or LTMQueryPayload not available. Cannot request LTM data.")
            return None

        ltm_query_payload = LTMQueryPayload(
            requester_module_id=self._module_id,
            query_type=query_type,
            query_content=query_content,
            target_memory_type=target_memory_type,
            parameters=parameters or {}
        )
        ltm_query_message = GenericMessage(
            source_module_id=self._module_id,
            message_type="LTMQuery",
            payload=ltm_query_payload
        )
        self._message_bus.publish(ltm_query_message)
        print(f"PDM ({self._module_id}): Published LTMQuery (ID: {ltm_query_payload.query_id}) for type '{query_type}'.")
        return ltm_query_payload.query_id

    # --- Planning and Dispatch ---
    def develop_and_dispatch_plan(self, goal_payload: GoalUpdatePayload) -> bool:
        if not self._message_bus or not ActionCommandPayload or not GenericMessage:
            print(f"PDM ({self._module_id}): Message bus or ActionCommandPayload not available. Cannot dispatch plan.")
            return False

        print(f"\nPDM ({self._module_id}): Developing plan for goal '{goal_payload.goal_id}': {goal_payload.goal_description}")
        print(f"  Considering current state:")
        print(f"    Active Goals (count): {len(self._active_goals)}")
        if self._current_percepts:
            latest_percept = self._current_percepts[-1]
            print(f"    Latest Percept: Modality='{latest_percept.modality}', Content='{str(latest_percept.content)[:50]}...'")
        else: print(f"    Latest Percept: None")
        if self._current_emotional_state:
            print(f"    Emotion: VAD={self._current_emotional_state.current_emotion_profile}, Intensity={self._current_emotional_state.intensity}")
        else: print(f"    Emotion: None")
        if self._current_attention_focus:
            print(f"    Attention: Item='{self._current_attention_focus.focused_item_id}', Type='{self._current_attention_focus.focus_type}'")
        else: print(f"    Attention: None")

        action_payloads: List[ActionCommandPayload] = []
        action_prefix = "default_action"
        action_params = {"goal_id": goal_payload.goal_id, "description": goal_payload.goal_description}

        if self._current_emotional_state and self._current_emotional_state.current_emotion_profile.get("valence", 0) < -0.3:
            action_prefix = "cautious_action"
            action_params["caution_level"] = "medium"
            if self._current_emotional_state.current_emotion_profile.get("valence", 0) < -0.6:
                 action_params["caution_level"] = "high"
            print(f"  Emotional state (negative valence) influenced plan to be '{action_prefix}'.")

        if self._current_percepts:
            for p_idx in range(len(self._current_percepts) -1, -1, -1):
                p = self._current_percepts[p_idx]
                if isinstance(p.content, dict) and p.content.get("type") == "linguistic_analysis":
                    if "urgent" in p.content.get("text", "").lower():
                        action_prefix = "urgent_response_action"
                        action_params["urgency"] = "critical"
                        print(f"  Percept (urgent text) influenced plan to be '{action_prefix}'.")
                        break

        # Conceptual: If a very important goal and no specific plan, query LTM for similar situations
        if goal_payload.priority > 0.85 and "greet" not in goal_payload.goal_description.lower():
            # Avoid querying for simple/generic goals in this example
            ltm_query_key = f"plan_for_{goal_payload.goal_description.split()[0]}" # Query by first word
            if not self._ltm_query_results.get(ltm_query_key): # Check if we already have results for a similar query
                print(f"  Goal '{goal_payload.goal_id}' is high priority. Requesting LTM for similar plans.")
                query_id = self.request_ltm_data(query_content=goal_payload.goal_description, query_type="find_similar_plans", target_memory_type="procedural")
                if query_id : self._ltm_query_results[ltm_query_key] = LTMQueryResultPayload(query_id=query_id, results=[], success_status=False, error_message="Query sent, result pending") # Placeholder
                action_params["ltm_query_sent_for_similar_plans"] = True


        action_payloads.append(ActionCommandPayload(
            action_type=f"{action_prefix}_step1", parameters=action_params.copy(), priority=goal_payload.priority,
            expected_outcome_summary=f"Complete step 1 for {goal_payload.goal_description}"
        ))
        if goal_payload.priority > 0.7:
             action_payloads.append(ActionCommandPayload(
                action_type=f"{action_prefix}_step2", parameters=action_params.copy(), priority=goal_payload.priority - 0.1,
                expected_outcome_summary=f"Complete step 2 for {goal_payload.goal_description}"
            ))

        if not action_payloads:
            print(f"PDM ({self._module_id}): No actions generated for goal '{goal_payload.goal_id}'.")
            return False

        for ac_payload in action_payloads:
            action_message = GenericMessage(source_module_id=self._module_id, message_type="ActionCommand", payload=ac_payload)
            self._message_bus.publish(action_message)
            print(f"PDM ({self._module_id}): Published ActionCommand '{ac_payload.action_type}' (ID: {ac_payload.command_id}) for goal '{goal_payload.goal_id}'.")
        return True

    def process_highest_priority_goal(self) -> bool:
        if not self._active_goals: return False
        highest_priority_goal_payload = self._active_goals[0]
        print(f"\nPDM ({self._module_id}): Processing highest priority goal '{highest_priority_goal_payload.goal_id}' (Prio: {highest_priority_goal_payload.priority}).")
        return self.develop_and_dispatch_plan(highest_priority_goal_payload)

    def get_module_status(self) -> Dict[str, Any]:
        status = {
            "module_id": self._module_id,
            "module_type": "ConcretePlanningAndDecisionMakingModule (Message Bus Integrated)",
            "message_bus_configured": self._message_bus is not None,
            "active_goals_count": len(self._active_goals),
            "highest_priority_goal_id": self._active_goals[0].goal_id if self._active_goals else None,
            "recent_percepts_count": len(self._current_percepts),
            "ltm_results_count": len(self._ltm_query_results),
            "current_emotion_intensity": self._current_emotional_state.intensity if self._current_emotional_state else None,
            "current_attention_focus_item": self._current_attention_focus.focused_item_id if self._current_attention_focus else None,
        }
        if self._current_percepts: status["latest_percept_modality"] = self._current_percepts[-1].modality
        return status

if __name__ == '__main__':
    print("\n--- ConcretePlanningAndDecisionMakingModule __main__ Test ---")

    received_action_commands: List[GenericMessage] = []
    received_ltm_queries: List[GenericMessage] = []

    def action_command_listener(message: GenericMessage):
        print(f" action_command_listener: Received ActionCommand! ID: {message.message_id[:8]}, Type: {message.payload.action_type}, Params: {message.payload.parameters}")
        received_action_commands.append(message)

    def ltm_query_listener(message: GenericMessage):
        print(f" ltm_query_listener: Received LTMQuery! ID: {message.message_id[:8]}, Type: {message.payload.query_type}, Content: {message.payload.query_content}")
        received_ltm_queries.append(message)

    async def main_test_flow():
        bus = MessageBus()
        pdm_module_id = "TestPDM001"
        pdm_module = ConcretePlanningAndDecisionMakingModule(message_bus=bus, module_id=pdm_module_id)

        bus.subscribe(module_id="TestActionCommandListener", message_type="ActionCommand", callback=action_command_listener)
        bus.subscribe(module_id="TestLTMQueryListener", message_type="LTMQuery", callback=ltm_query_listener)

        print(pdm_module.get_module_status())

        print("\n--- Testing Subscriptions (Updating PDM's internal state) ---")
        goal_payload1 = GoalUpdatePayload(goal_id="g1", goal_description="Achieve high score", priority=0.9, status="ACTIVE", originator="TestMotSys")
        bus.publish(GenericMessage(source_module_id="MotSys", message_type="GoalUpdate", payload=goal_payload1))

        percept_payload1 = PerceptDataPayload(modality="text", content={"type":"linguistic_analysis", "text": "User seems urgent"}, source_timestamp=datetime.now(timezone.utc))
        bus.publish(GenericMessage(source_module_id="PercSys", message_type="PerceptData", payload=percept_payload1))

        ltm_res_payload1 = LTMQueryResultPayload(query_id="pdm_q1", results=[MemoryItem(content="some old plan info")], success_status=True)
        bus.publish(GenericMessage(source_module_id="LTMSys", message_type="LTMQueryResult", payload=ltm_res_payload1))

        emo_payload1 = EmotionalStateChangePayload(current_emotion_profile={"valence": -0.7, "arousal": 0.6}, intensity=0.65, triggering_event_id="ev1")
        bus.publish(GenericMessage(source_module_id="EmoSys", message_type="EmotionalStateChange", payload=emo_payload1))

        attn_payload1 = AttentionFocusUpdatePayload(focused_item_id="g1", focus_type="goal_directed", intensity=0.9, timestamp=datetime.now(timezone.utc))
        bus.publish(GenericMessage(source_module_id="AttnSys", message_type="AttentionFocusUpdate", payload=attn_payload1))

        await asyncio.sleep(0.05) # Allow messages to be processed by PDM

        assert len(pdm_module._active_goals) == 1 and pdm_module._active_goals[0].goal_id == "g1"
        assert len(pdm_module._current_percepts) == 1 and pdm_module._current_percepts[0].content["text"] == "User seems urgent"
        assert "pdm_q1" in pdm_module._ltm_query_results
        assert pdm_module._current_emotional_state is not None and pdm_module._current_emotional_state.intensity == 0.65
        assert pdm_module._current_attention_focus is not None and pdm_module._current_attention_focus.focused_item_id == "g1"
        print("  PDM internal state updated successfully by subscriptions.")

        print("\n--- Testing request_ltm_data ---")
        ltm_query_id = pdm_module.request_ltm_data(query_content="historic_data_for_g1", query_type="episodic_search")
        await asyncio.sleep(0.05)
        assert len(received_ltm_queries) == 1
        assert received_ltm_queries[0].payload.query_id == ltm_query_id
        assert received_ltm_queries[0].payload.query_content == "historic_data_for_g1"
        assert received_ltm_queries[0].payload.requester_module_id == pdm_module_id
        print("  LTMQuery successfully published by PDM via request_ltm_data.")

        print("\n--- Testing process_highest_priority_goal (with negative emotion & urgent percept) ---")
        pdm_module.process_highest_priority_goal() # Should process g1
        await asyncio.sleep(0.05)
        assert len(received_action_commands) >= 1 # Expecting at least one command
        first_cmd = received_action_commands[0].payload
        assert "urgent_response_action" in first_cmd.action_type # Urgency from percept should take precedence
        assert first_cmd.parameters.get("urgency") == "critical"
        assert first_cmd.parameters.get("caution_level") is None # Should not be cautious if urgent
        print(f"  ActionCommand '{first_cmd.action_type}' published, reflecting current PDM state (urgent).")
        received_action_commands.clear()
        received_ltm_queries.clear() # Clear LTM queries as well

        # Test with different PDM state (e.g., no urgent percept, but still negative emotion)
        print("\n--- Testing process_highest_priority_goal (negative emotion, no urgent percept) ---")
        pdm_module._current_percepts.clear() # Remove urgent percept
        pdm_module.process_highest_priority_goal() # Process g1 again
        await asyncio.sleep(0.05)
        assert len(received_action_commands) >= 1
        second_cmd = received_action_commands[0].payload
        assert "cautious_action" in second_cmd.action_type # Should be cautious due to emotion
        assert second_cmd.parameters.get("caution_level") == "high" # from valence -0.7
        print(f"  ActionCommand '{second_cmd.action_type}' published, reflecting current PDM state (cautious).")
        received_action_commands.clear()

        # Test with high priority goal that might trigger LTM query during planning
        print("\n--- Testing process_highest_priority_goal (high priority, triggers LTM query) ---")
        pdm_module._current_emotional_state = None # Neutral emotion
        pdm_module._ltm_query_results.clear() # No prior LTM results for this specific conceptual query
        goal_payload_high_prio = GoalUpdatePayload(goal_id="g_complex", goal_description="Solve complex problem", priority=0.9, status="ACTIVE", originator="Test")
        bus.publish(GenericMessage(source_module_id="MotSys", message_type="GoalUpdate", payload=goal_payload_high_prio))
        await asyncio.sleep(0.01) # Let goal be processed

        pdm_module.process_highest_priority_goal() # Process g_complex
        await asyncio.sleep(0.05)
        assert len(received_ltm_queries) == 1 # Should have sent an LTM query
        assert "info_related_to_Solve_complex_problem" in received_ltm_queries[0].payload.query_content
        assert len(received_action_commands) >=1 # Should still produce a plan, perhaps a preliminary one
        assert received_action_commands[0].payload.parameters.get("ltm_query_sent") is True
        print("  PDM sent LTM query during planning for high priority goal and dispatched preliminary actions.")

        print("\n--- ConcretePlanningAndDecisionMakingModule __main__ Test Complete ---")

    try:
        asyncio.run(main_test_flow())
    except RuntimeError as e:
        if " asyncio.run() cannot be called from a running event loop" in str(e):
            print("Skipping asyncio.run() as an event loop is already running (e.g. in Jupyter/IPython).")
            # In a real Jupyter environment, you might 'await main_test_flow()' directly if the cell is async.
        else:
            raise
