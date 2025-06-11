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
    A concrete implementation of the Planning and Decision-Making (PDM) module,
    integrated with a message bus to receive various types of information (goals,
    percepts, LTM results, emotional state, attention focus) and dispatch
    ActionCommandPayloads.

    The core logic resides in the `develop_and_dispatch_plan` method, which follows
    a conceptual planning flow:
    1.  **LTM Plan Retrieval:** Attempts to retrieve a pre-existing plan from LTM relevant
        to the current high-priority goal.
    2.  **Conceptual Internal Plan Generation:** If no suitable LTM plan is found (or if an
        LTM plan is later deemed unsuitable), the module generates a few conceptual
        candidate plans. These might include:
        *   A direct, default sequence of actions.
        *   A "cautious" plan involving preliminary observation.
        *   An "exploratory" plan that might first query LTM for more context.
    3.  **Conceptual Plan Evaluation:** Each candidate plan (whether from LTM or internally
        generated) is subjected to a conceptual evaluation. This involves logging:
        *   Simulated World Model checks (e.g., predicted success, estimated resources).
        *   Simulated Self-Model checks (e.g., ethical considerations based on keywords,
            capability assessment based on plan complexity).
        *   Conceptual influence of the current emotional state.
        *   Conceptual outcomes of similar past plans (from LTM).
        A conceptual `evaluation_score` is assigned to each plan based on these checks.
    4.  **Conceptual Plan Selection:** The plan with the best `evaluation_score` is chosen.
        Reasons for rejecting other plans (especially LTM plans) are logged. If all plans
        are rejected, a minimal fallback action is generated.
    5.  **Ethical Review Trigger:** Before dispatching the selected plan, a formal
        `EthicalReviewRequest` may be published if the plan's nature or the conceptual
        ethical check during evaluation indicates a need for more thorough review.
    6.  **Dispatch:** ActionCommandPayloads for the selected plan are published to the message bus.

    Note: Many aspects of plan generation and evaluation are currently conceptual and
    primarily manifest as detailed logging statements. This structure is intended to
    outline how a more advanced planner would integrate diverse cognitive inputs.
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

        self._log: List[str] = []
        self._awaiting_plan_for_goal: Dict[str, str] = {} # goal_id -> ltm_query_id
        self._log_message(f"ConcretePlanningAndDecisionMakingModule '{self._module_id}' initialized. Message bus {bus_status_msg}.")

    def _log_message(self, message: str):
        """Helper method for internal logging."""
        log_entry = f"{time.time():.2f} [{self._module_id}]: {message}"
        self._log.append(log_entry)
        # print(log_entry) # Optional: print to console for real-time monitoring during tests

    # --- Message Handler Methods ---
    def _handle_goal_update_message(self, message: GenericMessage):
        if not isinstance(message.payload, GoalUpdatePayload):
            self._log_message(f"Received GoalUpdate with unexpected payload: {type(message.payload)}")
            return
        payload: GoalUpdatePayload = message.payload
        self._log_message(f"Received GoalUpdate for '{payload.goal_id}', Status: {payload.status}, Prio: {payload.priority}")
        self._active_goals = [g for g in self._active_goals if g.goal_id != payload.goal_id]
        if payload.status.upper() in ["NEW", "ACTIVE", "UPDATED", "PENDING"]:
            self._active_goals.append(payload)
            self._active_goals.sort(key=lambda g: g.priority, reverse=True)

    def _handle_percept_data_message(self, message: GenericMessage):
        if not isinstance(message.payload, PerceptDataPayload):
            self._log_message(f"Received PerceptData with unexpected payload: {type(message.payload)}")
            return
        self._current_percepts.append(message.payload)

    def _handle_ltm_query_result_message(self, message: GenericMessage):
        if not isinstance(message.payload, LTMQueryResultPayload):
            self._log_message(f"Received LTMQueryResult with unexpected payload: {type(message.payload)}")
            return
        payload: LTMQueryResultPayload = message.payload
        self._log_message(f"Received LTMQueryResult for QueryID: {payload.query_id}, Success: {payload.success_status}")

        if len(self._ltm_query_results) >= self.MAX_LTM_RESULTS_TO_STORE and payload.query_id not in self._ltm_query_results:
            try:
                oldest_query_id = next(iter(self._ltm_query_results))
                del self._ltm_query_results[oldest_query_id]
                self._log_message(f"Evicted oldest LTM query result: {oldest_query_id}")
            except StopIteration:
                pass
        self._ltm_query_results[payload.query_id] = payload

        # Check if this result was for a plan we were awaiting
        for goal_id, query_id in list(self._awaiting_plan_for_goal.items()): # Iterate over a copy for safe removal
            if query_id == payload.query_id:
                self._log_message(f"LTM Plan result received for QueryID '{payload.query_id}', which was awaited for GoalID '{goal_id}'.")
                # Conceptual: If goal is still active, could trigger re-planning.
                # For now, just log and remove from awaiting list.
                active_goal = next((g for g in self._active_goals if g.goal_id == goal_id), None)
                if active_goal:
                    self._log_message(f"Goal '{goal_id}' is still active. A re-plan could be triggered now that plan details are available.")
                del self._awaiting_plan_for_goal[goal_id]
                break


    def _handle_emotional_state_change_message(self, message: GenericMessage):
        if not isinstance(message.payload, EmotionalStateChangePayload):
            self._log_message(f"Received EmotionalStateChange with unexpected payload: {type(message.payload)}")
            return
        self._current_emotional_state = message.payload

    def _handle_attention_focus_update_message(self, message: GenericMessage):
        if not isinstance(message.payload, AttentionFocusUpdatePayload):
            self._log_message(f"Received AttentionFocusUpdate with unexpected payload: {type(message.payload)}")
            return
        self._current_attention_focus = message.payload

    # --- LTM Querying ---
    def request_ltm_data(self, query_content: Any, query_type: str,
                         target_memory_type: Optional[str] = None,
                         parameters: Optional[Dict[str, Any]] = None) -> Optional[str]:
        if not self._message_bus or not LTMQueryPayload or not GenericMessage:
            self._log_message("Message bus or LTMQueryPayload not available. Cannot request LTM data.")
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
            self._log_message("Message bus or ActionCommandPayload not available. Cannot dispatch plan.")
            return False

        self._log_message(f"Developing plan for goal '{goal_payload.goal_id}': {goal_payload.goal_description}")

        candidate_plans: List[Dict[str, Any]] = [] # Stores dicts like {"id": str, "source": str, "actions": List[ActionCommandPayload], "eval_score": float}

        # --- Step 1: Attempt to Retrieve Plan from LTM ---
        self._log_message("Attempting to retrieve plan from LTM...")
        ltm_action_payloads: List[ActionCommandPayload] = []
        ltm_plan_source = None
        relevant_ltm_query_id_for_plan = None

        for q_id, result_payload in self._ltm_query_results.items():
            if result_payload.query_metadata and result_payload.query_metadata.get("query_type") == "get_action_plan_for_goal":
                if goal_payload.goal_description in result_payload.query_metadata.get("original_query_content", ""): # Conceptual match
                    relevant_ltm_query_id_for_plan = q_id
                    self._log_message(f"Found potentially relevant LTM query result '{q_id}' for plan for goal '{goal_payload.goal_id}'.")
                    break

        if relevant_ltm_query_id_for_plan and self._ltm_query_results[relevant_ltm_query_id_for_plan].success_status:
            ltm_result = self._ltm_query_results[relevant_ltm_query_id_for_plan]
            if ltm_result.results and isinstance(ltm_result.results[0].content, list):
                potential_plan_steps = ltm_result.results[0].content
                if all(isinstance(step, dict) for step in potential_plan_steps):
                    self._log_message(f"Retrieved plan from LTM (QueryID: {relevant_ltm_query_id_for_plan}) with {len(potential_plan_steps)} steps.")
                    ltm_plan_source = f"ltm_retrieved (QueryID: {relevant_ltm_query_id_for_plan})"
                    for i, step_dict in enumerate(potential_plan_steps):
                        ltm_action_payloads.append(ActionCommandPayload(
                            action_type=step_dict.get("action_type", f"ltm_plan_step_{i+1}"),
                            parameters=step_dict.get("parameters", {"goal_id": goal_payload.goal_id}),
                            priority=goal_payload.priority - (i * 0.01),
                            expected_outcome_summary=step_dict.get("expected_outcome_summary", f"Complete LTM plan step {i+1} for {goal_payload.goal_description}")
                        ))
                    candidate_plans.append({
                        "id": f"ltm_plan_{relevant_ltm_query_id_for_plan}",
                        "source": ltm_plan_source,
                        "actions": ltm_action_payloads,
                        "eval_score": 0.0 # To be filled by evaluation
                    })
                else:
                    self._log_message(f"LTM result for plan (QueryID: {relevant_ltm_query_id_for_plan}) content is not a list of action dicts. Content: {str(potential_plan_steps)[:100]}")
            else:
                self._log_message(f"LTM query result for plan (QueryID: {relevant_ltm_query_id_for_plan}) had no results or results content was not a list.")
        else:
            self._log_message(f"No successful LTM plan found for goal '{goal_payload.goal_id}'.")


        # --- Step 2: Conceptual Internal Plan Generation (if no LTM plan or LTM plan is poor) ---
        # This phase is triggered if candidate_plans is empty (no LTM plan) or if LTM plan is later evaluated poorly.
        # For now, we'll generate internal candidates if no LTM plan was found.
        if not candidate_plans:
            self._log_message("No LTM plan retrieved. Starting conceptual internal plan generation.")
            plan_source = "internal_generation"

            # Candidate Plan 1: Direct (similar to original default)
            candidate_1_actions = []
            action_params_direct = {"goal_id": goal_payload.goal_id, "description": goal_payload.goal_description, "strategy": "direct"}
            candidate_1_actions.append(ActionCommandPayload(action_type=f"direct_action_step1", parameters=action_params_direct.copy(), priority=goal_payload.priority))
            if goal_payload.priority > 0.6: # Add a second step for higher priority goals
                 candidate_1_actions.append(ActionCommandPayload(action_type=f"direct_action_step2", parameters=action_params_direct.copy(), priority=goal_payload.priority - 0.1))
            candidate_plans.append({"id": "internal_direct_plan", "source": plan_source, "actions": candidate_1_actions, "eval_score": 0.0})
            self._log_message(f"Generated internal candidate 'direct_plan' with {len(candidate_1_actions)} steps.")

            # Candidate Plan 2: Cautious
            candidate_2_actions = []
            action_params_cautious = {"goal_id": goal_payload.goal_id, "description": goal_payload.goal_description, "strategy": "cautious"}
            candidate_2_actions.append(ActionCommandPayload(action_type="observe_surroundings", parameters=action_params_cautious.copy(), priority=goal_payload.priority))
            candidate_2_actions.append(ActionCommandPayload(action_type="cautious_action_step1", parameters=action_params_cautious.copy(), priority=goal_payload.priority - 0.05))
            candidate_plans.append({"id": "internal_cautious_plan", "source": plan_source, "actions": candidate_2_actions, "eval_score": 0.0})
            self._log_message(f"Generated internal candidate 'cautious_plan' with {len(candidate_2_actions)} steps.")

            # Candidate Plan 3: Exploratory (Query LTM for more context - if not already done for plan retrieval)
            if not relevant_ltm_query_id_for_plan and goal_payload.goal_id not in self._awaiting_plan_for_goal:
                candidate_3_actions = []
                action_params_exploratory = {"goal_id": goal_payload.goal_id, "description": goal_payload.goal_description, "strategy": "exploratory_ltm_query"}
                # This action would ideally trigger an LTMQuery via BGM or directly if PDM can do that
                candidate_3_actions.append(ActionCommandPayload(action_type="query_ltm_for_context", parameters={"query_topic": goal_payload.goal_description, "goal_id": goal_payload.goal_id}, priority=goal_payload.priority))
                candidate_3_actions.append(ActionCommandPayload(action_type="exploratory_action_step1", parameters=action_params_exploratory.copy(), priority=goal_payload.priority - 0.05))
                candidate_plans.append({"id": "internal_exploratory_plan", "source": plan_source, "actions": candidate_3_actions, "eval_score": 0.0})
                self._log_message(f"Generated internal candidate 'exploratory_plan' with {len(candidate_3_actions)} steps.")

        # Fallback: If LTM was queried for a plan and we are awaiting results, generate minimal default actions
        if goal_payload.goal_id in self._awaiting_plan_for_goal and not ltm_action_payloads:
            self._log_message(f"Awaiting LTM plan for goal '{goal_payload.goal_id}'. Generating minimal default actions for now.")
            plan_source = "default_pending_ltm"
            default_actions = [ActionCommandPayload(action_type="wait_for_ltm_plan", parameters={"goal_id": goal_payload.goal_id}, priority=goal_payload.priority)]
            # Add to candidate_plans or handle separately if this is the only option
            candidate_plans.append({"id": "internal_wait_plan", "source": plan_source, "actions": default_actions, "eval_score": 0.0})


        # --- Step 3: Conceptual Plan Evaluation ---
        self._log_message(f"Starting conceptual evaluation for {len(candidate_plans)} candidate plans.")
        if not candidate_plans: # Should not happen if default generation is a fallback
            self._log_message("No candidate plans (not even default) generated. This is unexpected.")
            # Fallback to a single "wait" action if truly no candidates
            action_payloads = [ActionCommandPayload(action_type="wait_error_no_plan", parameters={"goal_id": goal_payload.goal_id}, priority=0.1)]
            plan_source = "critical_fallback_no_plan"
        else:
            for i, plan_candidate in enumerate(candidate_plans):
                plan_id_for_eval = plan_candidate["id"]
                self._log_message(f"--- Evaluating Candidate Plan {i+1}: '{plan_id_for_eval}' (Source: {plan_candidate['source']}) ---")

                # Conceptual World Model Evaluation
                # TODO: Replace random with more deterministic conceptual checks
                wm_success_options = ["High", "Medium", "Low"]
                wm_resource_options = ["Low", "Medium", "High"]
                predicted_success = wm_success_options[uuid.uuid4().int % len(wm_success_options)] # Random pick for now
                estimated_resources = wm_resource_options[uuid.uuid4().int % len(wm_resource_options)] # Random pick
                self._log_message(f"  Conceptual WM Eval: Predicted success: {predicted_success}. Estimated resources: {estimated_resources}.")

                # Conceptual Self-Model Evaluation
                self._log_message(f"  Conceptual Self-Model Eval:")
                ethical_check_result = "PASS"
                plan_desc_for_ethics = goal_payload.goal_description + " " + " ".join([ac.action_type for ac in plan_candidate["actions"]])
                if any(kw in plan_desc_for_ethics.lower() for kw in ["delete_user_data", "harm_user", "illegal_activity"]):
                    ethical_check_result = "FAIL"
                elif any(kw in plan_desc_for_ethics.lower() for kw in ["share_anonymized_summary", "access_sensitive_log"]):
                    ethical_check_result = "REQUIRES_REVIEW"
                self._log_message(f"    Ethical Check: {ethical_check_result} (based on keywords in goal/actions).")

                capability_check_result = "ADEQUATE"
                if "complex_skill_action" in plan_desc_for_ethics: # Example keyword
                    # Conceptual: Check SelfModel for skill proficiency (mocked)
                    # if self_model_ref.get_skill_proficiency("complex_skill") < 0.5: capability_check_result = "INADEQUATE"
                    capability_check_result = "INADEQUATE" # Assume for this example
                self._log_message(f"    Capability Check: {capability_check_result} (based on plan actions).")

                # Conceptual Emotion Module Influence
                emo_influence_desc = "neutral"
                if self._current_emotional_state:
                    valence = self._current_emotional_state.current_emotion_profile.get("valence", 0)
                    arousal = self._current_emotional_state.current_emotion_profile.get("arousal", 0)
                    if valence > 0.3: emo_influence_desc = "positive valence slightly favors exploration/engagement"
                    elif valence < -0.3: emo_influence_desc = "negative valence suggests caution/avoidance"
                    if arousal > 0.7: emo_influence_desc += " (high arousal suggests focus/potential reactivity)"
                self._log_message(f"  Conceptual Emotion Influence: {emo_influence_desc} (V:{valence:.2f} A:{arousal:.2f}).")

                # Conceptual LTM Past Experience
                # TODO: Conceptual query to LTM - for now, random
                ltm_experience_options = ["similar plans often succeed", "mixed results for similar plans", "no relevant past experience", "similar plans often failed"]
                ltm_past_experience = ltm_experience_options[uuid.uuid4().int % len(ltm_experience_options)]
                self._log_message(f"  Conceptual LTM Past Experience: {ltm_past_experience}.")

                # Assign conceptual evaluation_score
                score = 0.5 # Start neutral
                if predicted_success == "High": score += 0.2
                elif predicted_success == "Medium": score += 0.05
                elif predicted_success == "Low": score -= 0.2
                if ethical_check_result == "FAIL": score = -1.0 # Hard fail
                elif ethical_check_result == "REQUIRES_REVIEW": score -= 0.15
                if capability_check_result == "INADEQUATE": score -= 0.3
                if "often succeed" in ltm_past_experience: score += 0.15
                elif "often failed" in ltm_past_experience: score -= 0.15

                plan_candidate["eval_score"] = round(score, 3)
                self._log_message(f"  Conceptual Evaluation Score for '{plan_id_for_eval}': {plan_candidate['eval_score']:.3f}")
                self._log_message(f"--- End Evaluation for Candidate Plan '{plan_id_for_eval}' ---")


            # --- Step 4: Conceptual Plan Selection ---
            self._log_message("Selecting plan based on conceptual evaluations...")
            # Filter out hard failures (e.g., ethical FAIL)
            valid_candidate_plans = [p for p in candidate_plans if p["eval_score"] > -0.5] # -1.0 was hard fail

            if not valid_candidate_plans:
                self._log_message("All candidate plans were conceptually rejected or scored too low. Generating critical fallback action.")
                action_payloads = [ActionCommandPayload(action_type="request_assistance_no_valid_plan", parameters={"goal_id": goal_payload.goal_id, "reason": "All plans failed conceptual evaluation"}, priority=goal_payload.priority)]
                plan_source = "critical_fallback_evaluation_reject"
            else:
                # Sort by evaluation score, highest first
                valid_candidate_plans.sort(key=lambda p: p["eval_score"], reverse=True)
                selected_plan_candidate = valid_candidate_plans[0]
                action_payloads = selected_plan_candidate["actions"]
                plan_source = selected_plan_candidate["source"]
                self._log_message(f"Selected plan '{selected_plan_candidate['id']}' with score {selected_plan_candidate['eval_score']:.3f}. Source: {plan_source}.")

                # If an LTM plan was evaluated but not selected
                if ltm_action_payloads and selected_plan_candidate["actions"] != ltm_action_payloads:
                    ltm_plan_eval = next((p for p in candidate_plans if p["actions"] == ltm_action_payloads), None)
                    if ltm_plan_eval: # Should exist if ltm_action_payloads is not empty
                         self._log_message(f"LTM plan '{ltm_plan_eval['id']}' was not selected (score: {ltm_plan_eval['eval_score']:.3f}).")


        # --- Step 5: Ethical Review Trigger Integration (Post-selection) ---
        # The initial, more basic ethical check was done during evaluation.
        # This is for the formal EthicalReviewRequest if the selected plan still warrants it.
        # For this refactor, we use the conceptual ethical_check_result from the selected plan if available,
        # or re-evaluate based on keywords for the selected plan.

        final_selected_plan_desc_for_ethics = goal_payload.goal_description + " " + " ".join([ac.action_type for ac in action_payloads])
        final_ethical_check_result_conceptual = "PASS" # Default
        # Re-check selected plan or use stored eval
        selected_plan_candidate_for_final_review = next((p for p in candidate_plans if p["actions"] == action_payloads), None)
        if selected_plan_candidate_for_final_review and "eval_score" in selected_plan_candidate_for_final_review: # Check if it went through new eval
            # A bit convoluted, ideally the ethical_check_result string is stored on the candidate plan object
            # For now, re-derive based on keywords for simplicity if not directly stored.
            if any(kw in final_selected_plan_desc_for_ethics.lower() for kw in ["delete_user_data", "harm_user", "illegal_activity"]):
                 final_ethical_check_result_conceptual = "FAIL" # Should have been filtered, but as safety
            elif any(kw in final_selected_plan_desc_for_ethics.lower() for kw in ["share_anonymized_summary", "access_sensitive_log", "privacy"]): # Added privacy
                 final_ethical_check_result_conceptual = "REQUIRES_REVIEW"

        perform_formal_ethical_review = (final_ethical_check_result_conceptual == "REQUIRES_REVIEW") or \
                                        any(keyword in final_selected_plan_desc_for_ethics.lower() for keyword in ["share", "modify_user_data", "sensitive_info"]) # Original keywords

        if not perform_formal_ethical_review and self._current_emotional_state and self._current_emotional_state.current_emotion_profile.get("arousal",0) > 0.7 and self._current_emotional_state.current_emotion_profile.get("valence",0) < -0.5:
            perform_formal_ethical_review = True
            self._log_message(f"High arousal/negative valence triggered formal ethical review for selected plan for goal '{goal_payload.goal_id}'.")


        if perform_formal_ethical_review:
            self._log_message(f"Selected plan for goal '{goal_payload.goal_id}' requires formal ethical review (Conceptual Check: {final_ethical_check_result_conceptual}). Publishing EthicalReviewRequest.")
            action_summary_for_review = [{"action": ac.action_type, "params": str(ac.parameters)[:100]} for ac in action_payloads[:3]] # Review first few steps
            proposal = {
                "action_type": "execute_selected_plan",
                "plan_summary": action_summary_for_review,
                "reason": f"Executing plan for goal: {goal_payload.goal_description} (ID: {goal_payload.goal_id})"
            }
            context_for_review = {
                "goal_id": goal_payload.goal_id, "goal_priority": goal_payload.priority,
                "emotional_state_summary": self._current_emotional_state.current_emotion_profile if self._current_emotional_state else None,
                "plan_source": plan_source,
                "conceptual_evaluation_score": selected_plan_candidate_for_final_review["eval_score"] if selected_plan_candidate_for_final_review else "N/A"
            }
            request_id = str(uuid.uuid4())
            ethical_review_payload_dict = {"request_id": request_id, "action_proposal": proposal, "context": context_for_review}
            review_request_message = GenericMessage(self._module_id, "EthicalReviewRequest", ethical_review_payload_dict)
            self._message_bus.publish(review_request_message)
            self._log_message(f"Published EthicalReviewRequest (ID: {request_id}). Plan source: {plan_source}. Conceptual evaluation score: {context_for_review['conceptual_evaluation_score']}.")
            # Note: In a real system, might wait for response or proceed with caution. Here, we proceed.

        # --- Step 6: Dispatch selected actions ---
        if not action_payloads: # Should ideally not happen if fallback exists
            self._log_message(f"CRITICAL: No actions selected or generated for goal '{goal_payload.goal_id}'. Dispatching nothing.")
            return False

        self._log_message(f"Dispatching {len(action_payloads)} actions from plan '{plan_source}' for goal '{goal_payload.goal_id}'.")
        for ac_payload in action_payloads:
            if "plan_source" not in ac_payload.parameters: # Ensure plan_source is in parameters
                 ac_payload.parameters["plan_source"] = plan_source
            action_message = GenericMessage(source_module_id=self._module_id, message_type="ActionCommand", payload=ac_payload)
            self._message_bus.publish(action_message)
            self._log_message(f"Published ActionCommand '{ac_payload.action_type}' (ID: {ac_payload.command_id}, PlanSource: {plan_source}) for goal '{goal_payload.goal_id}'.")
        return True

    def process_highest_priority_goal(self) -> bool:
        if not self._active_goals:
            self._log_message("No active goals to process.")
            return False
        highest_priority_goal_payload = self._active_goals[0]
        self._log_message(f"Processing highest priority goal '{highest_priority_goal_payload.goal_id}' (Prio: {highest_priority_goal_payload.priority}).")
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
            "awaiting_plan_for_goal_count": len(self._awaiting_plan_for_goal),
            "current_emotion_intensity": self._current_emotional_state.intensity if self._current_emotional_state else None,
            "current_attention_focus_item": self._current_attention_focus.focused_item_id if self._current_attention_focus else None,
            "log_entries": len(self._log)
        }
        if self._current_percepts: status["latest_percept_modality"] = self._current_percepts[-1].modality
        return status

if __name__ == '__main__':
    # Ensure datetime and timezone are available if not already imported at top level for main
    # from datetime import datetime, timezone # Already at top, but good to remember for standalone blocks

    print("\n--- ConcretePlanningAndDecisionMakingModule __main__ Test ---")

    received_action_commands: List[GenericMessage] = []
    received_ltm_queries: List[GenericMessage] = []
    received_ethical_review_requests: List[GenericMessage] = []

    def action_command_listener(message: GenericMessage):
        # pdm_module._log_message(f"action_command_listener: Received ActionCommand! ID: {message.message_id[:8]}, Type: {message.payload.action_type}, Params: {message.payload.parameters}")
        received_action_commands.append(message)

    def ltm_query_listener(message: GenericMessage):
        # pdm_module._log_message(f"ltm_query_listener: Received LTMQuery! ID: {message.message_id[:8]}, Type: {message.payload.query_type}, Content: {message.payload.query_content}")
        received_ltm_queries.append(message)

    def ethical_review_listener(message: GenericMessage):
        # pdm_module._log_message(f"ethical_review_listener: Received EthicalReviewRequest! ID: {message.payload.get('request_id')}")
        received_ethical_review_requests.append(message)


    async def main_test_flow():
        bus = MessageBus()
        pdm_module_id = "TestPDM001"
        pdm_module = ConcretePlanningAndDecisionMakingModule(message_bus=bus, module_id=pdm_module_id)

        bus.subscribe(module_id="TestActionCommandListener", message_type="ActionCommand", callback=action_command_listener)
        bus.subscribe(module_id="TestLTMQueryListener", message_type="LTMQuery", callback=ltm_query_listener)
        bus.subscribe(module_id="TestEthicalReviewListener", message_type="EthicalReviewRequest", callback=ethical_review_listener)


        print(pdm_module.get_module_status())
        initial_log_count = len(pdm_module._log)

        print("\n--- Test Case 1: Plan from LTM ---")
        received_action_commands.clear()
        ltm_plan_query_id = "ltm_plan_q1"
        goal_desc_for_ltm_plan = "achieve world peace"
        ltm_plan = [
            {"action_type": "negotiate_treaty", "parameters": {"parties": "all"}},
            {"action_type": "distribute_resources", "parameters": {"resource_type": "food", "amount": "ample"}}
        ]
        pdm_module._ltm_query_results[ltm_plan_query_id] = LTMQueryResultPayload(
            query_id=ltm_plan_query_id,
            results=[MemoryItem(item_id="plan_abc", content=ltm_plan, metadata={"plan_name": "WorldPeacePlanV1"})],
            success_status=True,
            query_metadata={"query_type": "get_action_plan_for_goal", "original_query_content": goal_desc_for_ltm_plan}
        )
        goal_ltm_plan = GoalUpdatePayload(goal_id="g_ltm_plan", goal_description=goal_desc_for_ltm_plan, priority=0.95, status="ACTIVE")
        bus.publish(GenericMessage(source_module_id="TestMotSys", message_type="GoalUpdate", payload=goal_ltm_plan))
        await asyncio.sleep(0.01)

        pdm_module.process_highest_priority_goal()
        await asyncio.sleep(0.01)

        assert len(received_action_commands) == 2, f"Expected 2 actions from LTM plan, got {len(received_action_commands)}"
        assert received_action_commands[0].payload.action_type == "negotiate_treaty"
        assert received_action_commands[1].payload.action_type == "distribute_resources"
        assert "ltm_retrieved" in received_action_commands[0].payload.parameters.get("plan_source", "")
        pdm_module._log_message("Test Case 1: Plan from LTM - PASSED.")
        received_action_commands.clear()


        print("\n--- Test Case 2: LTM Query for Plan ---")
        received_ltm_queries.clear()
        goal_desc_for_ltm_query = "solve_universal_equation"
        goal_ltm_query = GoalUpdatePayload(goal_id="g_ltm_query", goal_description=goal_desc_for_ltm_query, priority=0.85, status="ACTIVE")
        # Ensure no existing plan for this goal
        pdm_module._ltm_query_results = {k:v for k,v in pdm_module._ltm_query_results.items() if goal_desc_for_ltm_query not in v.query_metadata.get("original_query_content","")}
        pdm_module._awaiting_plan_for_goal.clear()

        bus.publish(GenericMessage(source_module_id="TestMotSys", message_type="GoalUpdate", payload=goal_ltm_query))
        await asyncio.sleep(0.01)
        pdm_module.process_highest_priority_goal()
        await asyncio.sleep(0.01)

        assert len(received_ltm_queries) == 1, f"Expected 1 LTM query for plan, got {len(received_ltm_queries)}"
        assert received_ltm_queries[0].payload.query_type == "get_action_plan_for_goal"
        assert received_ltm_queries[0].payload.query_content == goal_desc_for_ltm_query
        assert "g_ltm_query" in pdm_module._awaiting_plan_for_goal
        assert len(received_action_commands) >= 1 # Default actions should still be dispatched
        assert "(LTM query initiated)" in received_action_commands[0].payload.parameters.get("plan_source", "")
        pdm_module._log_message("Test Case 2: LTM Query for Plan - PASSED.")
        received_action_commands.clear()
        received_ltm_queries.clear()


        print("\n--- Test Case 3: Ethical Review Request ---")
        received_ethical_review_requests.clear()
        goal_desc_for_ethical_review = "delete user_archive_data for user_xyz"
        goal_ethical = GoalUpdatePayload(goal_id="g_ethical", goal_description=goal_desc_for_ethical_review, priority=0.9, status="ACTIVE")
        bus.publish(GenericMessage(source_module_id="TestMotSys", message_type="GoalUpdate", payload=goal_ethical))
        await asyncio.sleep(0.01)
        pdm_module.process_highest_priority_goal()
        await asyncio.sleep(0.01)

        assert len(received_ethical_review_requests) == 1, f"Expected 1 EthicalReviewRequest, got {len(received_ethical_review_requests)}"
        review_req_payload = received_ethical_review_requests[0].payload
        assert review_req_payload["action_proposal"]["reason"].startswith("Executing plan for goal: delete user_archive_data")
        assert "delete" in review_req_payload["action_proposal"]["plan_summary"][0]["action"] # Default action for delete
        assert len(received_action_commands) >= 1 # Actions still dispatched
        pdm_module._log_message("Test Case 3: Ethical Review Request - PASSED.")
        received_action_commands.clear()
        received_ethical_review_requests.clear()

        # Restore some state for any pre-existing tests that might run after if this were part of a larger suite
        # Example: Put back a generic goal
        goal_payload_generic = GoalUpdatePayload(goal_id="g_generic", goal_description="Perform generic task", priority=0.5, status="ACTIVE")
        bus.publish(GenericMessage(source_module_id="MotSys", message_type="GoalUpdate", payload=goal_payload_generic))
        await asyncio.sleep(0.01)

        final_log_count = len(pdm_module._log)
        assert final_log_count > initial_log_count
        print(f"\n--- Final PDM Status (Log entries: {final_log_count}) ---")
        print(pdm_module.get_module_status())
        print("\n--- ConcretePlanningAndDecisionMakingModule __main__ Test Complete ---")

    try:
        asyncio.run(main_test_flow())
    except RuntimeError as e:
        if " asyncio.run() cannot be called from a running event loop" in str(e):
            print("Skipping asyncio.run() as an event loop is already running (e.g. in Jupyter/IPython).")
            # In a real Jupyter environment, you might 'await main_test_flow()' directly if the cell is async.
        else:
            raise
