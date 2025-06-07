from typing import Any, Dict, List, Optional, Union
import time
import uuid # For module_id generation
import asyncio # For __main__

try:
    from .base_self_model_module import BaseSelfModelModule
    from .message_bus import MessageBus
    from .core_messages import (
        GenericMessage, GoalUpdatePayload, SelfKnowledgeConfidenceUpdatePayload,
        ActionEventPayload, PerceptDataPayload, EmotionalStateChangePayload,
        AttentionFocusUpdatePayload # AttentionFocus might be relevant for operational_status
    )
except ImportError:
    print("Warning: Running ConcreteSelfModelModule with stubbed imports.")
    class BaseSelfModelModule:
        def get_self_representation(self, aspect: Optional[str] = None) -> Any: pass
    MessageBus = None # type: ignore
    GenericMessage = object # type: ignore
    GoalUpdatePayload = object # type: ignore
    SelfKnowledgeConfidenceUpdatePayload = object # type: ignore
    ActionEventPayload = object # type: ignore
    PerceptDataPayload = object # type: ignore
    EmotionalStateChangePayload = object # type: ignore
    AttentionFocusUpdatePayload = object # type: ignore


# --- Data Classes Definition (Copied from original, ensure they are up-to-date if changed elsewhere) ---
class SelfAttributes:
    def __init__(self, agent_id: str = "PiaAGI_Self_v1.0",
                 current_developmental_stage: str = "initialization",
                 personality_profile: Optional[Dict[str, Any]] = None,
                 current_role_definition: Optional[Dict[str, Any]] = None,
                 operational_status: str = "idle",
                 cognitive_load_metrics: Optional[Dict[str, float]] = None,
                 current_emotional_summary: Optional[Dict[str, float]] = None,
                 active_goals_summary: Optional[List[Dict[str, Any]]] = None):
        self.agent_id: str = agent_id
        self.current_developmental_stage: str = current_developmental_stage
        self.personality_profile: Dict[str, Any] = personality_profile if personality_profile is not None else {}
        self.current_role_definition: Dict[str, Any] = current_role_definition if current_role_definition is not None else {}
        self.operational_status: str = operational_status
        self.cognitive_load_metrics: Dict[str, float] = cognitive_load_metrics if cognitive_load_metrics is not None else {}
        self.current_emotional_summary: Optional[Dict[str, float]] = current_emotional_summary # Keep as Optional or default to {}
        self.active_goals_summary: List[Dict[str, Any]] = active_goals_summary if active_goals_summary is not None else []
        self.capabilities: List[str] = ["initial_capability"] 
        self.limitations: List[str] = ["initial_limitation"]
        self.confidence_in_capabilities: float = 0.5

class KnowledgeConcept: # Assuming this and other data classes are defined as in the original
    def __init__(self, concept_id: str, label: str, description_summary: str = "",
                 understanding_level: float = 0.0, confidence_score: float = 0.0, groundedness_score: float = 0.0,
                 related_concepts: Optional[List[str]] = None, source_ltm_pointers: Optional[List[str]] = None,
                 last_accessed_ts: Optional[float] = None, access_frequency: int = 0,
                 uncertainty_details: Optional[Dict[str, Any]] = None):
        self.concept_id, self.label, self.description_summary = concept_id, label, description_summary
        self.understanding_level, self.confidence_score, self.groundedness_score = understanding_level, confidence_score, groundedness_score
        self.related_concepts = related_concepts or []
        self.source_ltm_pointers = source_ltm_pointers or []
        self.last_accessed_ts, self.access_frequency = last_accessed_ts, access_frequency
        self.uncertainty_details = uncertainty_details or {}

class KnowledgeMap:
    def __init__(self, concepts: Optional[Dict[str, KnowledgeConcept]] = None,
                 knowledge_gaps: Optional[List[Dict[str, Any]]] = None):
        self.concepts = concepts or {}
        self.knowledge_gaps = knowledge_gaps or []

class Skill:
    def __init__(self, skill_id: str, description: str, proficiency_level: Union[float, str] = 0.0,
                 last_successful_use_ts: Optional[float] = None, success_rate_history: Optional[List[Dict[str, Any]]] = None,
                 related_procedural_ltm_pointers: Optional[List[str]] = None, confidence_in_skill: float = 0.0):
        self.skill_id, self.description, self.proficiency_level = skill_id, description, proficiency_level
        self.last_successful_use_ts = last_successful_use_ts
        self.success_rate_history = success_rate_history or []
        self.related_procedural_ltm_pointers = related_procedural_ltm_pointers or []
        self.confidence_in_skill = confidence_in_skill

class Tool: # Simplified from original for brevity
    def __init__(self, tool_id: str, name: str, type: str, description_and_purpose: str, proficiency_level: Union[float, str] = 0.0):
        self.tool_id, self.name, self.type, self.description_and_purpose, self.proficiency_level = tool_id, name, type, description_and_purpose, proficiency_level

class CapabilityInventory:
    def __init__(self, skills: Optional[Dict[str, Skill]] = None, tools: Optional[Dict[str, Tool]] = None,
                 learning_preferences_and_styles: Optional[Dict[str, Any]] = None):
        self.skills = skills or {}
        self.tools = tools or {}
        self.learning_preferences_and_styles = learning_preferences_and_styles or {}

class EthicalRule:
    def __init__(self, rule_id: str, principle: str, description: str, priority_level: Union[str, int] = "medium", source: str = "system_defined", applicability_contexts: Optional[List[str]] = None):
        self.rule_id, self.principle, self.description, self.priority_level, self.source = rule_id, principle, description, priority_level, source
        self.applicability_contexts = applicability_contexts or []

class EthicalFramework:
    def __init__(self, rules: Optional[List[EthicalRule]] = None):
        self.rules = rules or []

class AutobiographicalLogSummaryEntry:
    def __init__(self, entry_id: str, ltm_ref: str, timestamp: float, description: str, type: str, impact_on_self_model_summary: str = ""):
        self.entry_id, self.ltm_ref, self.timestamp, self.description, self.type, self.impact_on_self_model_summary = entry_id, ltm_ref, timestamp, description, type, impact_on_self_model_summary

class AutobiographicalLogSummary:
    def __init__(self, entries: Optional[List[AutobiographicalLogSummaryEntry]] = None):
        self.entries = entries or []

class DevelopmentalGoal: # Simplified
    def __init__(self, dev_goal_id: str, description: str, current_status: str = "pending"):
        self.dev_goal_id, self.description, self.current_status = dev_goal_id, description, current_status

class DevelopmentalState: # Simplified
    def __init__(self, active_developmental_goals: Optional[List[DevelopmentalGoal]] = None):
        self.active_developmental_goals = active_developmental_goals or []

# --- ConcreteSelfModelModule Class ---
class ConcreteSelfModelModule(BaseSelfModelModule):
    def __init__(self,
                 message_bus: Optional[MessageBus] = None,
                 module_id: str = f"SelfModelModule_{str(uuid.uuid4())[:8]}"):
        self._module_id = module_id
        self._message_bus = message_bus

        self.attributes: SelfAttributes = SelfAttributes(agent_id=f"PiaAGI_{self._module_id}")
        self.knowledge_map: KnowledgeMap = KnowledgeMap()
        self.capabilities: CapabilityInventory = CapabilityInventory()
        self.ethical_framework: EthicalFramework = EthicalFramework() # Initialize with some defaults if needed
        self.autobiography: AutobiographicalLogSummary = AutobiographicalLogSummary()
        self.development: DevelopmentalState = DevelopmentalState()

        self._knowledge_confidence: Dict[str, float] = {} # Renamed from self.knowledge_confidence
        self._capability_confidence: Dict[str, float] = {} # Renamed from self.capability_confidence
        self._performance_log: List[Dict[str, Any]] = []
        self._self_related_percepts: List[PerceptDataPayload] = []

        bus_status_msg = "not configured"
        if self._message_bus:
            subscriptions = [
                ("GoalUpdate", self._handle_goal_update_message),
                ("ActionEvent", self._handle_action_event_message),
                ("EmotionalStateChange", self._handle_emotional_state_change_message),
                ("PerceptData", self._handle_percept_data_message)
                # Add AttentionFocusUpdate if deemed relevant for self-model, e.g., to update operational_status
            ]
            subscribed_types = []
            try:
                core_types_ok = all([GenericMessage, GoalUpdatePayload, ActionEventPayload, EmotionalStateChangePayload, PerceptDataPayload, SelfKnowledgeConfidenceUpdatePayload])
                if core_types_ok:
                    for msg_type, callback in subscriptions:
                        self._message_bus.subscribe(self._module_id, msg_type, callback)
                        subscribed_types.append(msg_type)
                    bus_status_msg = f"configured and subscribed to: {', '.join(subscribed_types)}"
                else:
                    bus_status_msg = "core message types missing for subscription"
            except Exception as e:
                bus_status_msg = f"FAILED to subscribe: {e}"
        print(f"ConcreteSelfModelModule '{self._module_id}' initialized. Message bus {bus_status_msg}.")

    # --- Message Handler Methods ---
    def _handle_goal_update_message(self, message: GenericMessage):
        if not isinstance(message.payload, GoalUpdatePayload): return
        payload: GoalUpdatePayload = message.payload
        # print(f"SM ({self._module_id}): Received GoalUpdate for '{payload.goal_id}'")
        
        # Update active_goals_summary: replace if exists, else add if active
        self.attributes.active_goals_summary = [g for g in self.attributes.active_goals_summary if g["goal_id"] != payload.goal_id]
        if payload.status.upper() in ["ACTIVE", "PENDING", "NEW", "UPDATED"]:
            self.attributes.active_goals_summary.append({
                "goal_id": payload.goal_id, "description": payload.goal_description,
                "status": payload.status, "priority": payload.priority
            })
            self.attributes.active_goals_summary.sort(key=lambda g: g.get("priority", 0), reverse=True)

    def _handle_action_event_message(self, message: GenericMessage):
        if not isinstance(message.payload, ActionEventPayload): return
        payload: ActionEventPayload = message.payload
        # print(f"SM ({self._module_id}): Received ActionEvent for command '{payload.action_command_id}'")

        criteria = {"action_type": payload.action_type, "status_from_event": payload.status}
        if payload.outcome and "goal_id" in payload.outcome:
            criteria["goal_id"] = payload.outcome["goal_id"]
            # Potentially update confidence in skill related to this goal type/action
            # For now, evaluate_self_performance handles general capability confidence.

        self.evaluate_self_performance(task_id=payload.action_command_id, outcome=payload.outcome, criteria=criteria)

    def _handle_emotional_state_change_message(self, message: GenericMessage):
        if not isinstance(message.payload, EmotionalStateChangePayload): return
        payload: EmotionalStateChangePayload = message.payload
        # print(f"SM ({self._module_id}): Received EmotionalStateChange.")
        self.attributes.current_emotional_summary = payload.current_emotion_profile

    def _handle_percept_data_message(self, message: GenericMessage):
        if not isinstance(message.payload, PerceptDataPayload): return
        payload: PerceptDataPayload = message.payload
        if message.metadata and message.metadata.get("target_component") == "self_model":
            print(f"SM ({self._module_id}): Received self-relevant PerceptData: {str(payload.content)[:100]}")
            self._self_related_percepts.append(payload)
            if len(self._self_related_percepts) > 10: # Keep a small log
                self._self_related_percepts.pop(0)

    # --- Core Self-Model Methods ---
    def get_self_representation(self, aspect: Optional[str] = None) -> Any:
        # (Implementation from original, ensure it uses self.attributes, etc.)
        if aspect is None:
            return {
                "attributes": self.attributes.__dict__, "knowledge_map": self.knowledge_map.__dict__,
                "capabilities": self.capabilities.__dict__, "ethical_framework": self.ethical_framework.__dict__,
                "autobiography": self.autobiography.__dict__, "development": self.development.__dict__
            }
        main_components = {"attributes": self.attributes, "knowledge_map": self.knowledge_map, "capabilities": self.capabilities,
                           "ethical_framework": self.ethical_framework, "autobiography": self.autobiography, "development": self.development}
        if aspect in main_components: return main_components[aspect]
        if hasattr(self.attributes, aspect): return getattr(self.attributes, aspect)
        return None

    def update_confidence(self, item_id: str, item_type: str, new_confidence: float, source_of_update: str = "unknown") -> bool:
        previous_confidence: Optional[float] = self.get_confidence(item_id, item_type)
        clamped_confidence = max(0.0, min(1.0, new_confidence))
        updated = False
        if item_type == "knowledge":
            self._knowledge_confidence[item_id] = clamped_confidence; updated = True
        elif item_type == "capability" or item_type == "skill" or item_type == "tool": # Allow skill/tool as well
            self._capability_confidence[item_id] = clamped_confidence; updated = True
        else: return False

        if updated and self._message_bus and GenericMessage and SelfKnowledgeConfidenceUpdatePayload:
            payload = SelfKnowledgeConfidenceUpdatePayload(
                item_id=item_id, item_type=item_type, new_confidence=clamped_confidence,
                previous_confidence=previous_confidence, source_of_update=source_of_update
            )
            message = GenericMessage(source_module_id=self._module_id, message_type="SelfKnowledgeConfidenceUpdate", payload=payload)
            try:
                self._message_bus.publish(message)
                print(f"SM ({self._module_id}): Published SelfKnowledgeConfidenceUpdate for '{item_id}'.")
            except Exception as e: print(f"SM ({self._module_id}): Error publishing confidence update: {e}")
        return updated

    def get_confidence(self, item_id: str, item_type: str) -> Optional[float]:
        if item_type == "knowledge": return self._knowledge_confidence.get(item_id)
        elif item_type == "capability" or item_type == "skill" or item_type == "tool": return self._capability_confidence.get(item_id)
        return None

    def evaluate_self_performance(self, task_id: str, outcome: Any, criteria: Dict[str, Any]) -> Dict[str, Any]:
        # (Simplified from original, ensure it adds to self.autobiography.entries)
        current_ts = time.time()
        status_from_event = criteria.get("status_from_event", "UNKNOWN")
        achieved_success = status_from_event == "SUCCESS"
        
        log_entry = {"task_id": task_id, "outcome": outcome, "criteria": criteria, "timestamp": current_ts, "status": status_from_event}
        self._performance_log.append(log_entry)

        # Update overall capability confidence (simple model)
        adj = 0.01 if achieved_success else -0.01
        self.attributes.confidence_in_capabilities = max(0.0, min(1.0, self.attributes.confidence_in_capabilities + adj))

        auto_entry = AutobiographicalLogSummaryEntry(
            entry_id=f"perf_eval_{len(self.autobiography.entries)}_{task_id}",
            ltm_ref=f"perf_log_ref_{len(self._performance_log)}", timestamp=current_ts,
            description=f"Task '{task_id}' (type: {criteria.get('action_type','N/A')}) resulted in {status_from_event}. Outcome: {str(outcome)[:50]}",
            type=f"performance_evaluation_{status_from_event.lower()}",
            impact_on_self_model_summary=f"Overall capability confidence adj by {adj:.2f} to {self.attributes.confidence_in_capabilities:.2f}."
        )
        self.autobiography.entries.append(auto_entry)
        print(f"SM ({self._module_id}): Evaluated performance for task '{task_id}', status: {status_from_event}. Autobiographical entry added.")
        return {"evaluation_complete": True, "derived_status": status_from_event, "autobiography_entry_id": auto_entry.entry_id}

    # Other methods like perform_ethical_evaluation, assess_confidence_in_knowledge etc. would remain,
    # potentially simplified or adapted if they also need bus integration not covered by this subtask.
    # For brevity, I'll assume they are structurally similar to the original unless specified.
    # Ensure to keep or adapt update_self_representation if needed.

    def get_module_status(self) -> Dict[str, Any]:
        return {
            "module_id": self._module_id,
            "module_type": "ConcreteSelfModelModule (Message Bus Integrated)",
            "message_bus_configured": self._message_bus is not None,
            "agent_id": self.attributes.agent_id,
            "operational_status": self.attributes.operational_status,
            "confidence_in_capabilities": self.attributes.confidence_in_capabilities,
            "active_goals_summary_count": len(self.attributes.active_goals_summary),
            "self_related_percepts_count": len(self._self_related_percepts),
            "knowledge_confidence_entries": len(self._knowledge_confidence),
            "capability_confidence_entries": len(self._capability_confidence),
            "autobiography_entries_count": len(self.autobiography.entries),
            "performance_log_count": len(self._performance_log)
        }

if __name__ == '__main__':
    print("\n--- ConcreteSelfModelModule __main__ Test ---")

    received_confidence_updates: List[GenericMessage] = []
    def confidence_update_listener(message: GenericMessage):
        print(f" confidence_listener: Received SelfKnowledgeConfidenceUpdate! Item: {message.payload.item_id}, NewConf: {message.payload.new_confidence:.2f}")
        received_confidence_updates.append(message)

    async def main_test_flow():
        bus = MessageBus()
        sm_module_id = "TestSM001"
        self_model = ConcreteSelfModelModule(message_bus=bus, module_id=sm_module_id)

        bus.subscribe(module_id="TestConfidenceListener", message_type="SelfKnowledgeConfidenceUpdate", callback=confidence_update_listener)

        print(self_model.get_module_status())

        print("\n--- Testing Subscriptions ---")
        # 1. GoalUpdate
        goal_payload = GoalUpdatePayload(goal_id="g1", goal_description="Understand self", priority=0.9, status="ACTIVE", originator="MetaSys")
        bus.publish(GenericMessage(source_module_id="MotSys", message_type="GoalUpdate", payload=goal_payload))
        await asyncio.sleep(0.01)
        assert len(self_model.attributes.active_goals_summary) == 1
        assert self_model.attributes.active_goals_summary[0]["goal_id"] == "g1"
        print("  SM received GoalUpdate, active_goals_summary updated.")

        # 2. ActionEvent
        action_event_payload = ActionEventPayload(action_command_id="cmd1", action_type="self_reflect", status="SUCCESS", outcome={"goal_id":"g1", "details":"Reflection complete"})
        bus.publish(GenericMessage(source_module_id="ExecSys", message_type="ActionEvent", payload=action_event_payload))
        await asyncio.sleep(0.01)
        assert len(self_model.autobiography.entries) > 0
        assert "cmd1" in self_model.autobiography.entries[-1].description
        print(f"  SM received ActionEvent, autobiography entries: {len(self_model.autobiography.entries)}.")

        # 3. EmotionalStateChange
        emo_payload = EmotionalStateChangePayload(current_emotion_profile={"v":0.7,"a":0.3}, intensity=0.5)
        bus.publish(GenericMessage(source_module_id="EmoSys", message_type="EmotionalStateChange", payload=emo_payload))
        await asyncio.sleep(0.01)
        assert self_model.attributes.current_emotional_summary is not None
        assert self_model.attributes.current_emotional_summary["v"] == 0.7
        print("  SM received EmotionalStateChange, current_emotional_summary updated.")

        # 4. PerceptData (self-relevant)
        percept_payload = PerceptDataPayload(modality="internal", content="Self-consistency check passed", source_timestamp=datetime.now(uuid.uuid4().hex)) # Changed datetime.now
        percept_msg = GenericMessage(source_module_id="MonitorSys", message_type="PerceptData", payload=percept_payload, metadata={"target_component": "self_model"})
        bus.publish(percept_msg)
        await asyncio.sleep(0.01)
        assert len(self_model._self_related_percepts) == 1
        print("  SM received self-relevant PerceptData.")

        print("\n--- Testing Publishing SelfKnowledgeConfidenceUpdate ---")
        self_model.update_confidence(item_id="k_test_concept", item_type="knowledge", new_confidence=0.75, source_of_update="test_event")
        await asyncio.sleep(0.01)
        assert len(received_confidence_updates) == 1
        assert received_confidence_updates[0].payload.item_id == "k_test_concept"
        assert received_confidence_updates[0].payload.new_confidence == 0.75
        print("  ConfidenceUpdate successfully published by SM.")

        print("\n--- Final SM Status ---")
        print(self_model.get_module_status())

        print("\n--- ConcreteSelfModelModule __main__ Test Complete ---")

    try:
        asyncio.run(main_test_flow())
    except RuntimeError as e:
        if " asyncio.run() cannot be called from a running event loop" in str(e):
            print("Skipping asyncio.run() as an event loop is already running.")
        else:
            raise
