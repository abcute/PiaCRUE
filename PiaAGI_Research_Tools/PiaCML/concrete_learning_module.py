from typing import Any, Dict, List, Optional
import uuid # For module_id generation
import time # For timestamps in __main__
import asyncio # For __main__

try:
    from .base_learning_module import BaseLearningModule
    from .message_bus import MessageBus
    from .core_messages import (
        GenericMessage, GoalUpdatePayload, PerceptDataPayload,
        ActionEventPayload, EmotionalStateChangePayload, LearningOutcomePayload
    )
except ImportError:
    print("Warning: Running ConcreteLearningModule with stubbed imports.")
    class BaseLearningModule: pass
    MessageBus = None # type: ignore
    GenericMessage = object # type: ignore
    GoalUpdatePayload = object # type: ignore
    PerceptDataPayload = object # type: ignore
    ActionEventPayload = object # type: ignore
    EmotionalStateChangePayload = object # type: ignore
    LearningOutcomePayload = object # type: ignore


class ConcreteLearningModule(BaseLearningModule):
    """
    A concrete implementation of the BaseLearningModule, integrated with a message bus
    to learn from various system events and publish learning outcomes.
    """

    def __init__(self,
                 message_bus: Optional[MessageBus] = None,
                 module_id: str = f"LearningModule_{str(uuid.uuid4())[:8]}"):
        self._module_id = module_id
        self._message_bus = message_bus
        self._learned_items_log: List[Dict[str, Any]] = [] # To store learning outcomes or summaries
        self._feedback_log: List[Dict[str, Any]] = [] # Not used by new handlers yet
        self._learning_tasks_status: Dict[str, str] = {} # task_id -> status

        self._handled_message_counts: Dict[str, int] = {
            "GoalUpdate": 0, "PerceptData": 0, "ActionEvent": 0, "EmotionalStateChange": 0
        }
        self._published_outcomes_count = 0
        self._last_emotional_state: Optional[EmotionalStateChangePayload] = None

        bus_status_msg = "not configured"
        if self._message_bus:
            core_types_ok = all([GenericMessage, GoalUpdatePayload, PerceptDataPayload,
                                 ActionEventPayload, EmotionalStateChangePayload, LearningOutcomePayload])
            if core_types_ok:
                try:
                    subscriptions = [
                        ("GoalUpdate", self._handle_goal_update_for_learning),
                        ("PerceptData", self._handle_percept_data_for_learning),
                        ("ActionEvent", self._handle_action_event_for_learning),
                        ("EmotionalStateChange", self._handle_emotional_state_for_learning)
                    ]
                    for msg_type, callback in subscriptions:
                        self._message_bus.subscribe(self._module_id, msg_type, callback)
                    bus_status_msg = f"configured and subscribed to: {', '.join(s[0] for s in subscriptions)}"
                except Exception as e:
                    bus_status_msg = f"FAILED to subscribe: {e}"
            else:
                bus_status_msg = "core message types missing for subscription"

        self._log: List[str] = []
        self._log_message(f"ConcreteLearningModule '{self._module_id}' initialized. Message bus {bus_status_msg}.")

    def _log_message(self, message: str):
        """Helper method for internal logging."""
        log_entry = f"{time.time():.2f} [{self._module_id}]: {message}"
        self._log.append(log_entry)
        # print(log_entry) # Optional: for real-time console monitoring

    # --- Message Handler Methods ---
    def _handle_goal_update_for_learning(self, message: GenericMessage): # Renamed
        if not isinstance(message.payload, GoalUpdatePayload): return
        payload: GoalUpdatePayload = message.payload
        self._handled_message_counts["GoalUpdate"] += 1
        # print(f"LM ({self._module_id}): GoalUpdate '{payload.goal_id}' status {payload.status}. Adapting conceptually.")
        # Conceptual: If goal achieved/failed, could adjust learning related to that goal.
        # For now, just logging and potentially using it in a more complex `learn` call later.
        if payload.status in ["achieved", "failed"]:
            self.learn(data=payload, learning_paradigm="goal_outcome_evaluation",
                       context={"source_message_id": message.message_id})


    def _handle_percept_data_for_learning(self, message: GenericMessage):
        if not isinstance(message.payload, PerceptDataPayload): return
        payload: PerceptDataPayload = message.payload
        self._handled_message_counts["PerceptData"] += 1
        # print(f"LM ({self._module_id}): PerceptData from '{payload.modality}'. Learning via feature extraction.")
        self.learn(data=payload.content, learning_paradigm="unsupervised_feature_extraction",
                   context={"source_message_id": message.message_id, "modality": payload.modality, "percept_id": payload.percept_id})

    def _handle_action_event_for_learning(self, message: GenericMessage):
        if not isinstance(message.payload, ActionEventPayload): return
        payload: ActionEventPayload = message.payload
        self._handled_message_counts["ActionEvent"] += 1
        # print(f"LM ({self._module_id}): ActionEvent '{payload.action_type}' status {payload.status}. Learning via reinforcement.")
        self.learn(data=payload, learning_paradigm="reinforcement_from_action",
                   context={"source_message_id": message.message_id, "action_command_id": payload.action_command_id})

    def _handle_emotional_state_for_learning(self, message: GenericMessage):
        if not isinstance(message.payload, EmotionalStateChangePayload): return
        payload: EmotionalStateChangePayload = message.payload
        self._handled_message_counts["EmotionalStateChange"] += 1
        # print(f"LM ({self._module_id}): EmotionalStateChange. V={payload.current_emotion_profile.get('valence')}, A={payload.current_emotion_profile.get('arousal')}")
        self._last_emotional_state = payload
        self._log_message(f"Emotional state updated: V={payload.current_emotion_profile.get('valence')}, A={payload.current_emotion_profile.get('arousal')}")

    def apply_ethical_guardrails(self, potential_learning_outcome: LearningOutcomePayload) -> bool:
        """
        Conceptually checks if a learning outcome is ethically problematic.
        Returns True if learning can proceed, False if it should be rejected.
        """
        self._log_message(f"Applying ethical guardrails to: {potential_learning_outcome.item_description[:100]} (Confidence: {potential_learning_outcome.confidence:.2f})")
        description_lower = (potential_learning_outcome.item_description or "").lower()
        item_type_lower = (potential_learning_outcome.learned_item_type or "").lower()

        harmful_keywords = ["harmful_content", "bias_amplification", "deception_strategy", "manipulation_tactic", "illegal_act"]
        sensitive_item_types = ["social_interaction_model", "persuasion_model", "user_preference_profile"]

        for keyword in harmful_keywords:
            if keyword in description_lower or keyword in item_type_lower:
                self._log_message(f"Ethical Guardrail REJECT: Outcome '{potential_learning_outcome.item_id}' rejected due to harmful keyword '{keyword}'.")
                return False

        if item_type_lower in sensitive_item_types and potential_learning_outcome.confidence is not None and potential_learning_outcome.confidence < 0.2:
            self._log_message(f"Ethical Guardrail REJECT: Outcome '{potential_learning_outcome.item_id}' for sensitive type '{item_type_lower}' has very low confidence ({potential_learning_outcome.confidence:.2f}). Rejected.")
            return False

        self._log_message(f"Ethical Guardrail PASS: Outcome '{potential_learning_outcome.item_id}' passed checks.")
        return True

    def learn(self, data: Any, learning_paradigm: str, context: Dict[str, Any]) -> Optional[LearningOutcomePayload]:
        task_id = context.get('task_id', context.get('source_message_id', f"learning_task_{str(uuid.uuid4())[:8]}"))
        self._learning_tasks_status[task_id] = f"processing_{learning_paradigm}"
        self._log_message(f"Learning attempt. Task: {task_id}, Paradigm: '{learning_paradigm}'. Data: {str(data)[:100]}")

        status = "LEARNED"
        item_type: Optional[str] = None
        item_id: Optional[str] = None
        item_desc: Optional[str] = None
        confidence: float = 0.5 # Default confidence
        learned_metadata: Dict[str, Any] = {}

        if learning_paradigm == "unsupervised_feature_extraction":
            item_type = "knowledge_concept_features"
            item_id = f"features_from_{context.get('percept_id', task_id)}"
            item_desc = f"Extracted features from {context.get('modality', 'unknown')} percept."
            confidence = 0.6
            learned_metadata["extracted_features_count"] = len(data) if isinstance(data, list) else 1
        elif learning_paradigm == "reinforcement_from_action":
            item_type = "skill_adjustment"
            if isinstance(data, ActionEventPayload):
                item_id = data.action_type
                item_desc = f"Outcome for action '{data.action_type}' (status: {data.status})."
                if data.status == "SUCCESS":
                    confidence = 0.75
                    learned_metadata["reinforcement_direction"] = "positive"
                elif data.status == "FAILURE":
                    status = "UPDATED"
                    confidence = 0.65
                    learned_metadata["reinforcement_direction"] = "negative"
                elif data.status in ["IN_PROGRESS", "CANCELLED"]: # Learning from NO_CHANGE
                    status = "OBSERVED_NO_CHANGE" # New status for this case
                    item_desc = f"Observed action '{data.action_type}' with status '{data.status}', no direct reinforcement."
                    confidence = 0.1 # Very low confidence for mere observation
                    learned_metadata["observation_details"] = f"Action status was {data.status}."
                else: # Other statuses
                    status = "NO_CHANGE"
                    item_desc = f"No direct learning from action '{data.action_type}' status '{data.status}'."
                    confidence = 0.3 # Slightly higher than IN_PROGRESS/CANCELLED if it's some other neutral outcome
        elif learning_paradigm == "goal_outcome_evaluation":
            item_type = "strategy_evaluation"
            if isinstance(data, GoalUpdatePayload):
                item_id = f"strategy_for_goal_{data.goal_id}"
                item_desc = f"Evaluated strategies related to goal '{data.goal_id}' (status: {data.status})."
                confidence = 0.7 if data.status == "achieved" else 0.4
                learned_metadata["goal_status"] = data.status
                learned_metadata["goal_priority"] = data.priority
            else:
                status = "FAILED_TO_LEARN"
                item_desc = "Invalid data type for goal_outcome_evaluation."
                confidence = 0.0
        else:
            status = "FAILED_TO_LEARN"
            item_desc = f"Unknown learning paradigm '{learning_paradigm}'."
            confidence = 0.0

        # Modulate Learning by Emotion
        emotional_adjustment = 0.0
        if self._last_emotional_state:
            valence = self._last_emotional_state.current_emotion_profile.get("valence", 0.0)
            arousal = self._last_emotional_state.current_emotion_profile.get("arousal", 0.0)
            if arousal > 0.6: # Only apply if arousal is high
                if valence > 0.5: # Positive emotion
                    emotional_adjustment = 0.05
                    learned_metadata["emotional_influence"] = "positive_amplification"
                elif valence < -0.5: # Negative emotion
                    emotional_adjustment = -0.05
                    learned_metadata["emotional_influence"] = "negative_amplification"

                if emotional_adjustment != 0.0:
                    confidence += emotional_adjustment
                    self._log_message(f"Emotional state (V:{valence:.2f}, A:{arousal:.2f}) influenced confidence by {emotional_adjustment:.2f} for '{item_id}'.")

        confidence = max(0.0, min(1.0, confidence)) # Clamp confidence

        # Prepare LearningOutcomePayload
        outcome_payload = LearningOutcomePayload(
            learning_task_id=task_id, status=status, learned_item_type=item_type,
            item_id=item_id, item_description=item_desc, confidence=confidence,
            source_message_ids=[context["source_message_id"]] if "source_message_id" in context else [],
            metadata=learned_metadata
        )

        # Apply Ethical Guardrails
        if not self.apply_ethical_guardrails(outcome_payload):
            self._log_message(f"Learning outcome for '{item_id}' rejected by ethical guardrails. Original status: {status}, Confidence: {confidence:.2f}")
            outcome_payload.status = "REJECTED_BY_ETHICS"
            # Confidence might be kept as is, or nulled, depending on policy. Let's keep it for now.
            # The fact it was rejected is the key.

        self._learned_items_log.append({
            "task_id": task_id, "paradigm": learning_paradigm, "status": outcome_payload.status, # Use potentially updated status
            "item_type": item_type, "item_id": item_id, "description": item_desc,
            "final_confidence": outcome_payload.confidence, # Log final confidence
            "timestamp": time.time()
        })
        self._learning_tasks_status[task_id] = outcome_payload.status


        if self._message_bus and LearningOutcomePayload and GenericMessage:
            outcome_message = GenericMessage(
                source_module_id=self._module_id,
                message_type="LearningOutcome",
                payload=outcome_payload # Use the (potentially modified by ethics) payload
            )
            try:
                self._message_bus.publish(outcome_message)
                self._published_outcomes_count += 1
                self._log_message(f"Published LearningOutcome for task '{task_id}', Status: {outcome_payload.status}, Item: {item_id}.")
            except Exception as e:
                self._log_message(f"Error publishing LearningOutcome: {e}")
            return outcome_payload
        return None

    def get_learning_status(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        if task_id:
            return {
                'task_id': task_id,
                'status': self._learning_tasks_status.get(task_id, 'unknown_task'),
                'module_id': self._module_id,
                'module_type': 'ConcreteLearningModule (Message Bus Integrated)'
            }
        return {
            'module_id': self._module_id,
            'module_type': 'ConcreteLearningModule (Message Bus Integrated)',
            'message_bus_configured': self._message_bus is not None,
            'active_tasks_count': len([s for s in self._learning_tasks_status.values() if "processing" in s]),
            'total_logged_learning_outcomes': len(self._learned_items_log),
            'total_feedback_logs': len(self._feedback_log),
            'handled_message_counts': dict(self._handled_message_counts),
            'published_outcomes_count': self._published_outcomes_count,
            'last_emotional_valence': self._last_emotional_state.current_emotion_profile.get("valence") if self._last_emotional_state else None,
            'last_emotional_arousal': self._last_emotional_state.current_emotion_profile.get("arousal") if self._last_emotional_state else None,
            'log_entries': len(self._log)
        }

    def process_feedback(self, feedback_data: Dict[str, Any], learning_context_id: Optional[str] = None) -> bool:
        self._log_message(f"Processing feedback for context '{learning_context_id}': {str(feedback_data)[:100]}")
        self._feedback_log.append({'feedback': feedback_data, 'context_id': learning_context_id, 'timestamp': time.time()})
        # Conceptual: This feedback could trigger a new `learn` call or adjust existing learned items.
        return True

    def consolidate_knowledge(self, learned_item_ids: List[str], consolidation_type: str = "summary") -> Optional[str]:
        self._log_message(f"Attempting '{consolidation_type}' consolidation for {len(learned_item_ids)} learned items: {learned_item_ids}")
        if not learned_item_ids:
            self._log_message("No item IDs provided for consolidation.")
            return None

        # Conceptual: Filter relevant items from _learned_items_log
        relevant_learnings = [log_item for log_item in self._learned_items_log if log_item.get("item_id") in learned_item_ids and log_item.get("status") not in ["REJECTED_BY_ETHICS", "FAILED_TO_LEARN"]]

        if not relevant_learnings:
            self._log_message(f"No valid, non-rejected/failed learned items found for IDs: {learned_item_ids}")
            return None

        if consolidation_type == "summary":
            summary_id = f"consol_{str(uuid.uuid4())[:8]}"
            # Create a simple description based on the types and number of items
            item_types_summary = {}
            for item in relevant_learnings:
                item_type = item.get("item_type", "unknown_type")
                item_types_summary[item_type] = item_types_summary.get(item_type, 0) + 1

            desc_parts = [f"{count}x {type_name}" for type_name, count in item_types_summary.items()]
            description = f"Consolidated summary of {len(relevant_learnings)} learned items: {', '.join(desc_parts)}."

            # Average confidence of consolidated items, or some other heuristic
            avg_confidence = sum(item.get("final_confidence", 0.0) for item in relevant_learnings) / len(relevant_learnings) if relevant_learnings else 0.0

            consolidated_content = {
                "summary_id": summary_id,
                "type": "learned_item_cluster", # Or "meta_knowledge", "derived_insight"
                "description": description,
                "confidence": round(max(0.0, min(1.0, avg_confidence + 0.1)), 2), # Slight boost for consolidation
                "source_item_ids": [item.get("item_id") for item in relevant_learnings],
                "consolidation_timestamp": time.time()
            }

            # Publish LTMStoreRequest (Conceptual)
            if self._message_bus and GenericMessage:
                ltm_store_payload_dict = {
                    "item_id": summary_id,
                    "item_type": consolidated_content["type"],
                    "content": consolidated_content,
                    "metadata": {"consolidation_type": consolidation_type, "source_module": self._module_id}
                }
                ltm_store_request_msg = GenericMessage(
                    source_module_id=self._module_id,
                    message_type="LTMStoreRequest", # Custom message type
                    payload=ltm_store_payload_dict
                )
                try:
                    self._message_bus.publish(ltm_store_request_msg)
                    self._log_message(f"Published LTMStoreRequest for consolidated item '{summary_id}'. Content: {str(consolidated_content)[:150]}")
                    return summary_id
                except Exception as e:
                    self._log_message(f"Error publishing LTMStoreRequest: {e}")
                    return None
            else:
                self._log_message("Message bus not available for LTMStoreRequest.")
                return None
        else:
            self._log_message(f"Consolidation type '{consolidation_type}' not yet implemented.")
            return None


if __name__ == '__main__':
    # Required for source_timestamp in PerceptDataPayload if constructing it directly in tests
    from datetime import datetime as dt

    print("\n--- ConcreteLearningModule __main__ Test ---")

    received_learning_outcomes: List[GenericMessage] = []
    received_ltm_store_requests: List[GenericMessage] = []

    def learning_outcome_listener(message: GenericMessage):
        # learning_module._log_message(f"outcome_listener: Received LearningOutcome! Task: {message.payload.learning_task_id}, Status: {message.payload.status}, ItemType: {message.payload.learned_item_type}, Conf: {message.payload.confidence:.2f}")
        received_learning_outcomes.append(message)

    def ltm_store_request_listener(message: GenericMessage):
        # learning_module._log_message(f"ltm_store_listener: Received LTMStoreRequest! Item ID: {message.payload.get('item_id')}")
        received_ltm_store_requests.append(message)

    async def main_test_flow():
        bus = MessageBus()
        lm_module_id = "TestLM001"
        learning_module = ConcreteLearningModule(message_bus=bus, module_id=lm_module_id)

        bus.subscribe(module_id="TestOutcomeListener", message_type="LearningOutcome", callback=learning_outcome_listener)
        bus.subscribe(module_id="TestLTMStoreListener", message_type="LTMStoreRequest", callback=ltm_store_request_listener)

        initial_status = learning_module.get_learning_status()
        print(initial_status)
        initial_log_count = initial_status.get('log_entries', 0)
        initial_published_outcomes = initial_status.get('published_outcomes_count', 0)


        print("\n--- Testing Basic Subscriptions (from original tests) ---")
        pd_payload = PerceptDataPayload(percept_id="p1", modality="visual", content=["f1"], source_timestamp=dt.now())
        bus.publish(GenericMessage(message_type="PerceptData", payload=pd_payload, message_id="p_msg1"))
        await asyncio.sleep(0.01)
        assert len(received_learning_outcomes) == 1
        first_outcome_for_consolidation = received_learning_outcomes[0].payload
        received_learning_outcomes.clear()


        print("\n--- Testing Emotional Influence ---")
        # Positive Emotion Influence
        learning_module._last_emotional_state = EmotionalStateChangePayload(current_emotion_profile={"valence": 0.8, "arousal": 0.7}, intensity=0.7)
        ae_success_pos_emo = ActionEventPayload(action_command_id="cmd_s_posemo", action_type="skill_pos_emo", status="SUCCESS")
        bus.publish(GenericMessage(message_type="ActionEvent", payload=ae_success_pos_emo, message_id="ae_s_posemo"))
        await asyncio.sleep(0.01)
        assert len(received_learning_outcomes) == 1
        outcome_pos_emo = received_learning_outcomes[0].payload
        assert outcome_pos_emo.confidence > 0.75 # Base for SUCCESS is 0.75, positive emotion should make it >
        assert outcome_pos_emo.metadata.get("emotional_influence") == "positive_amplification"
        learning_module._log_message(f"  Positive emotion test: Confidence {outcome_pos_emo.confidence:.3f} (expected >0.75)")
        second_outcome_for_consolidation = outcome_pos_emo
        received_learning_outcomes.clear()

        # Negative Emotion Influence
        learning_module._last_emotional_state = EmotionalStateChangePayload(current_emotion_profile={"valence": -0.8, "arousal": 0.7}, intensity=0.7)
        ae_success_neg_emo = ActionEventPayload(action_command_id="cmd_s_negemo", action_type="skill_neg_emo", status="SUCCESS")
        bus.publish(GenericMessage(message_type="ActionEvent", payload=ae_success_neg_emo, message_id="ae_s_negemo"))
        await asyncio.sleep(0.01)
        assert len(received_learning_outcomes) == 1
        outcome_neg_emo = received_learning_outcomes[0].payload
        assert outcome_neg_emo.confidence < 0.75 # Base for SUCCESS is 0.75, negative emotion should make it <
        assert outcome_neg_emo.metadata.get("emotional_influence") == "negative_amplification"
        learning_module._log_message(f"  Negative emotion test: Confidence {outcome_neg_emo.confidence:.3f} (expected <0.75)")
        received_learning_outcomes.clear()
        learning_module._last_emotional_state = None # Reset


        print("\n--- Testing Ethical Guardrails ---")
        # Guardrail REJECT case: Constructing a payload that would be built by `learn`
        # We then call `learn` with data that would produce such a description internally for the guardrail check.
        # The actual item_description is formed inside the `learn` method.
        # So we need to pass data to `learn` that leads to a problematic description.
        # For this test, we'll modify the action_type to be the problematic string.
        ae_harmful_data = ActionEventPayload(action_command_id="cmd_harm", action_type="learn_to_generate_harmful_content", status="SUCCESS")
        learning_module.learn(data=ae_harmful_data, learning_paradigm="reinforcement_from_action", context={"source_message_id": "harm_test_msg"})

        await asyncio.sleep(0.01)
        assert len(received_learning_outcomes) == 1
        outcome_harmful = received_learning_outcomes[0].payload
        assert outcome_harmful.status == "REJECTED_BY_ETHICS", f"Outcome status was {outcome_harmful.status}"
        learning_module._log_message(f"  Ethical guardrail REJECT test: Status '{outcome_harmful.status}' (expected REJECTED_BY_ETHICS)")
        received_learning_outcomes.clear()

        # Guardrail PASS case
        ae_safe = ActionEventPayload(action_command_id="cmd_safe", action_type="learn_safe_skill", status="SUCCESS")
        learning_module.learn(data=ae_safe, learning_paradigm="reinforcement_from_action", context={"source_message_id": "safe_test_msg"})
        await asyncio.sleep(0.01)
        assert len(received_learning_outcomes) == 1
        outcome_safe = received_learning_outcomes[0].payload
        assert outcome_safe.status == "LEARNED" # Default for success
        learning_module._log_message(f"  Ethical guardrail PASS test: Status '{outcome_safe.status}' (expected LEARNED)")
        third_outcome_for_consolidation = outcome_safe
        received_learning_outcomes.clear()


        print("\n--- Testing 'NO_CHANGE' Learning Path (IN_PROGRESS) ---")
        ae_inprogress = ActionEventPayload(action_command_id="cmd_ip", action_type="long_task", status="IN_PROGRESS")
        bus.publish(GenericMessage(message_type="ActionEvent", payload=ae_inprogress, message_id="ae_ip_msg"))
        await asyncio.sleep(0.01)
        assert len(received_learning_outcomes) == 1
        outcome_inprogress = received_learning_outcomes[0].payload
        assert outcome_inprogress.status == "OBSERVED_NO_CHANGE"
        assert outcome_inprogress.confidence == 0.1 # Specific low confidence for this state
        learning_module._log_message(f"  IN_PROGRESS action test: Status '{outcome_inprogress.status}', Confidence {outcome_inprogress.confidence:.2f}")
        received_learning_outcomes.clear()


        print("\n--- Testing Knowledge Consolidation ---")
        # Use item_ids from previous successful and non-rejected learning outcomes
        ids_to_consolidate = [
            first_outcome_for_consolidation.item_id,
            second_outcome_for_consolidation.item_id,
            third_outcome_for_consolidation.item_id
        ]
        ids_to_consolidate = [id_ for id_ in ids_to_consolidate if id_]

        if len(ids_to_consolidate) >= 2:
            summary_item_id = learning_module.consolidate_knowledge(learned_item_ids=list(set(ids_to_consolidate)), consolidation_type="summary") # Use set to avoid duplicates
            await asyncio.sleep(0.01)
            assert summary_item_id is not None
            assert len(received_ltm_store_requests) == 1
            ltm_req = received_ltm_store_requests[0].payload
            assert ltm_req.get("item_id") == summary_item_id
            assert ltm_req.get("item_type") == "learned_item_cluster"
            # Ensure all unique source IDs are present
            unique_source_ids_in_payload = set(ltm_req.get("content", {}).get("source_item_ids", []))
            assert unique_source_ids_in_payload == set(ids_to_consolidate)

            learning_module._log_message(f"  Knowledge consolidation test: LTMStoreRequest sent for '{summary_item_id}'.")
            received_ltm_store_requests.clear()
        else:
            learning_module._log_message("  Skipping knowledge consolidation test as not enough valid items were learned.")


        final_status = learning_module.get_learning_status()
        print("\n--- Final Learning Module Status ---")
        print(final_status)
        assert final_status["published_outcomes_count"] > initial_published_outcomes
        assert final_status["log_entries"] > initial_log_count

        print("\n--- ConcreteLearningModule __main__ Test Complete ---")

    try:
        asyncio.run(main_test_flow())
    except RuntimeError as e:
        if " asyncio.run() cannot be called from a running event loop" in str(e):
            print("Skipping asyncio.run() as an event loop is already running.")
        else:
            raise
