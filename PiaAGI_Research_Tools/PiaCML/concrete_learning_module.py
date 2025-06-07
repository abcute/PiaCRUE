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
        print(f"ConcreteLearningModule '{self._module_id}' initialized. Message bus {bus_status_msg}.")

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
        # This state can be accessed by the `learn` method.

    def learn(self, data: Any, learning_paradigm: str, context: Dict[str, Any]) -> Optional[LearningOutcomePayload]:
        task_id = context.get('task_id', context.get('source_message_id', f"learning_task_{str(uuid.uuid4())[:8]}"))
        self._learning_tasks_status[task_id] = f"processing_{learning_paradigm}"
        # print(f"LM ({self._module_id}): Learning attempt. Task: {task_id}, Paradigm: '{learning_paradigm}'. Data: {str(data)[:100]}")

        # Conceptual learning logic & outcome determination
        status = "LEARNED" # Default status
        item_type: Optional[str] = None
        item_id: Optional[str] = None
        item_desc: Optional[str] = None
        confidence: Optional[float] = None
        learned_metadata: Dict[str, Any] = {}

        if learning_paradigm == "unsupervised_feature_extraction":
            item_type = "knowledge_concept_features"
            item_id = f"features_from_{context.get('percept_id', task_id)}"
            item_desc = f"Extracted features from {context.get('modality', 'unknown')} percept."
            confidence = 0.6 # Conceptual
            learned_metadata["extracted_features_count"] = len(data) if isinstance(data, list) else 1 # Dummy
        elif learning_paradigm == "reinforcement_from_action":
            item_type = "skill_adjustment" # Or "policy_update"
            if isinstance(data, ActionEventPayload):
                item_id = data.action_type # Learning about this action type
                item_desc = f"Adjusted strategy for action '{data.action_type}' based on status '{data.status}'."
                if data.status == "SUCCESS":
                    confidence = 0.75
                    learned_metadata["reinforcement_direction"] = "positive"
                elif data.status == "FAILURE":
                    status = "UPDATED" # Still learned something, but an update/adjustment
                    confidence = 0.65
                    learned_metadata["reinforcement_direction"] = "negative"
                else: # IN_PROGRESS, CANCELLED
                    status = "NO_CHANGE"
                    item_desc = f"No direct learning from action '{data.action_type}' status '{data.status}'."
                    confidence = 0.5
        elif learning_paradigm == "goal_outcome_evaluation":
            item_type = "strategy_evaluation"
            if isinstance(data, GoalUpdatePayload):
                item_id = f"strategy_for_goal_{data.goal_id}"
                item_desc = f"Evaluated strategies related to goal '{data.goal_id}' (status: {data.status})."
                confidence = 0.7 if data.status == "achieved" else 0.5
                learned_metadata["goal_status"] = data.status
                learned_metadata["goal_priority"] = data.priority
            else: # Should not happen if called correctly
                status = "FAILED_TO_LEARN"
                item_desc = "Invalid data type for goal_outcome_evaluation."
        else:
            status = "FAILED_TO_LEARN"
            item_desc = f"Unknown learning paradigm '{learning_paradigm}'."
            confidence = 0.1

        self._learned_items_log.append({
            "task_id": task_id, "paradigm": learning_paradigm, "status": status,
            "item_type": item_type, "item_id": item_id, "description": item_desc,
            "timestamp": time.time()
        })
        self._learning_tasks_status[task_id] = status

        # Publish LearningOutcome
        if self._message_bus and LearningOutcomePayload and GenericMessage:
            outcome_payload = LearningOutcomePayload(
                learning_task_id=task_id, status=status, learned_item_type=item_type,
                item_id=item_id, item_description=item_desc, confidence=confidence,
                source_message_ids=[context["source_message_id"]] if "source_message_id" in context else [],
                metadata=learned_metadata
            )
            outcome_message = GenericMessage(
                source_module_id=self._module_id,
                message_type="LearningOutcome",
                payload=outcome_payload
            )
            try:
                self._message_bus.publish(outcome_message)
                self._published_outcomes_count += 1
                # print(f"LM ({self._module_id}): Published LearningOutcome for task '{task_id}'.")
            except Exception as e:
                print(f"LM ({self._module_id}): Error publishing LearningOutcome: {e}")
            return outcome_payload
        return None # If no bus or core types

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
            'total_feedback_logs': len(self._feedback_log), # Not currently used by new handlers
            'handled_message_counts': dict(self._handled_message_counts),
            'published_outcomes_count': self._published_outcomes_count,
            'last_emotional_valence': self._last_emotional_state.current_emotion_profile.get("valence") if self._last_emotional_state else None,
            # 'all_tasks_status': dict(self._learning_tasks_status), # Can be too verbose
        }

    # process_feedback, consolidate_knowledge, apply_ethical_guardrails remain as stubs or simple loggers for now
    def process_feedback(self, feedback_data: Dict[str, Any], learning_context_id: Optional[str] = None) -> bool:
        self._feedback_log.append({'feedback': feedback_data, 'context_id': learning_context_id})
        return True
    def consolidate_knowledge(self, learned_item_ids: List[str], target_memory_system: str = "LTM") -> bool: return True
    def apply_ethical_guardrails(self, potential_learning_outcome: Any, context: Dict[str, Any]) -> bool: return True


if __name__ == '__main__':
    print("\n--- ConcreteLearningModule __main__ Test ---")

    received_learning_outcomes: List[GenericMessage] = []
    def learning_outcome_listener(message: GenericMessage):
        print(f" outcome_listener: Received LearningOutcome! Task: {message.payload.learning_task_id}, Status: {message.payload.status}, ItemType: {message.payload.learned_item_type}")
        received_learning_outcomes.append(message)

    async def main_test_flow():
        bus = MessageBus()
        lm_module_id = "TestLM001"
        learning_module = ConcreteLearningModule(message_bus=bus, module_id=lm_module_id)

        bus.subscribe(module_id="TestOutcomeListener", message_type="LearningOutcome", callback=learning_outcome_listener)

        print(learning_module.get_learning_status())

        print("\n--- Testing Subscriptions & LearningOutcome Publishing ---")
        # 1. PerceptData
        pd_payload = PerceptDataPayload(percept_id="p1", modality="visual", content=["feature1", "feature2"], source_timestamp=datetime.datetime.now())
        pd_msg = GenericMessage(source_module_id="TestPerceptSys", message_type="PerceptData", payload=pd_payload, message_id="percept_msg_1")
        bus.publish(pd_msg)
        await asyncio.sleep(0.01)
        assert learning_module._handled_message_counts["PerceptData"] == 1
        assert len(received_learning_outcomes) == 1
        assert received_learning_outcomes[0].payload.learned_item_type == "knowledge_concept_features"
        assert "percept_msg_1" in received_learning_outcomes[0].payload.source_message_ids
        received_learning_outcomes.clear()

        # 2. ActionEvent (Success)
        ae_payload_success = ActionEventPayload(action_command_id="cmd1", action_type="navigate", status="SUCCESS", outcome={"result":"arrived"})
        ae_msg_s = GenericMessage(source_module_id="TestExecSys", message_type="ActionEvent", payload=ae_payload_success, message_id="action_event_s1")
        bus.publish(ae_msg_s)
        await asyncio.sleep(0.01)
        assert learning_module._handled_message_counts["ActionEvent"] == 1
        assert len(received_learning_outcomes) == 1
        assert received_learning_outcomes[0].payload.learned_item_type == "skill_adjustment"
        assert received_learning_outcomes[0].payload.item_id == "navigate"
        assert received_learning_outcomes[0].payload.status == "LEARNED" # or UPDATED if logic changes
        assert received_learning_outcomes[0].payload.metadata.get("reinforcement_direction") == "positive"
        received_learning_outcomes.clear()

        # 3. ActionEvent (Failure)
        ae_payload_fail = ActionEventPayload(action_command_id="cmd2", action_type="grasp", status="FAILURE", outcome={"reason":"object_slipped"})
        ae_msg_f = GenericMessage(source_module_id="TestExecSys", message_type="ActionEvent", payload=ae_payload_fail, message_id="action_event_f1")
        bus.publish(ae_msg_f)
        await asyncio.sleep(0.01)
        assert learning_module._handled_message_counts["ActionEvent"] == 2
        assert len(received_learning_outcomes) == 1
        assert received_learning_outcomes[0].payload.item_id == "grasp"
        assert received_learning_outcomes[0].payload.status == "UPDATED" # Still learned, but an update
        assert received_learning_outcomes[0].payload.metadata.get("reinforcement_direction") == "negative"
        received_learning_outcomes.clear()

        # 4. EmotionalStateChange
        emo_payload = EmotionalStateChangePayload(current_emotion_profile={"valence":0.8, "arousal":0.5}, intensity=0.6)
        emo_msg = GenericMessage(source_module_id="TestEmoSys", message_type="EmotionalStateChange", payload=emo_payload)
        bus.publish(emo_msg)
        await asyncio.sleep(0.01)
        assert learning_module._handled_message_counts["EmotionalStateChange"] == 1
        assert learning_module._last_emotional_state is not None
        assert learning_module._last_emotional_state.intensity == 0.6
        # No LearningOutcome expected directly from emotion change, but it might affect next `learn` call.

        # 5. GoalUpdate (Achieved)
        gu_payload = GoalUpdatePayload(goal_id="g_learn", description="Learn new skill", priority=0.9, status="achieved", originator="User")
        gu_msg = GenericMessage(source_module_id="TestMotSys", message_type="GoalUpdate", payload=gu_payload, message_id="goal_update_ach1")
        bus.publish(gu_msg)
        await asyncio.sleep(0.01)
        assert learning_module._handled_message_counts["GoalUpdate"] == 1
        assert len(received_learning_outcomes) == 1 # Expect one from goal_outcome_evaluation
        assert received_learning_outcomes[0].payload.learned_item_type == "strategy_evaluation"
        assert received_learning_outcomes[0].payload.metadata.get("goal_status") == "achieved"
        received_learning_outcomes.clear()

        print("\n--- Final Learning Module Status ---")
        print(learning_module.get_learning_status())
        assert learning_module.get_learning_status()["published_outcomes_count"] == 4 # 1 percept, 2 action, 1 goal

        print("\n--- ConcreteLearningModule __main__ Test Complete ---")

    try:
        asyncio.run(main_test_flow())
    except RuntimeError as e:
        if " asyncio.run() cannot be called from a running event loop" in str(e):
            print("Skipping asyncio.run() as an event loop is already running.")
        else:
            raise
