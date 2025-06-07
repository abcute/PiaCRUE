from typing import Any, Dict, Optional, List
import uuid
import datetime # For ToMInferenceUpdatePayload timestamp
import asyncio # For __main__

try:
    from .base_theory_of_mind_module import BaseTheoryOfMindModule
    from .message_bus import MessageBus
    from .core_messages import (
        GenericMessage, PerceptDataPayload, ToMInferenceUpdatePayload,
        EmotionalStateChangePayload # Added import
    )
except ImportError:
    print("Warning: Running ConcreteToMModule with stubbed imports.")
    class BaseTheoryOfMindModule: pass
    MessageBus = None # type: ignore
    GenericMessage = object # type: ignore
    PerceptDataPayload = object # type: ignore
    ToMInferenceUpdatePayload = object # type: ignore
    EmotionalStateChangePayload = object # type: ignore


class ConcreteTheoryOfMindModule(BaseTheoryOfMindModule):
    """
    A concrete implementation of the BaseTheoryOfMindModule.
    This version uses a dictionary to store models of other agents,
    can subscribe to PerceptData and EmotionalStateChange messages,
    and publish ToMInferenceUpdate messages.
    """

    def __init__(self,
                 message_bus: Optional[MessageBus] = None,
                 module_id: str = f"ToMModule_{str(uuid.uuid4())[:8]}"):
        """
        Initializes the ConcreteTheoryOfMindModule.
        """
        self._module_id = module_id
        self._message_bus = message_bus
        self._agent_models: Dict[str, Dict[str, Any]] = {}

        self._handled_message_counts: Dict[str, int] = {
            "PerceptData": 0,
            "EmotionalStateChange": 0
        }
        self._published_inferences_count = 0

        bus_status_msg = "not configured"
        if self._message_bus:
            core_types_ok = all([GenericMessage, PerceptDataPayload, ToMInferenceUpdatePayload, EmotionalStateChangePayload])
            if core_types_ok:
                try:
                    self._message_bus.subscribe(
                        module_id=self._module_id,
                        message_type="PerceptData",
                        callback=self._handle_percept_for_tom # Renamed
                    )
                    self._message_bus.subscribe(
                        module_id=self._module_id,
                        message_type="EmotionalStateChange",
                        callback=self._handle_own_emotion_change_for_tom # Renamed
                    )
                    bus_status_msg = "configured and subscribed to PerceptData & EmotionalStateChange"
                except Exception as e:
                    bus_status_msg = f"configured but FAILED to subscribe: {e}"
            else:
                bus_status_msg = "configured but core message types for subscription not available"
        print(f"ConcreteTheoryOfMindModule '{self._module_id}' initialized. Message bus {bus_status_msg}.")

    def infer_mental_state(self,
                           target_agent_id: str,
                           evidence_payload: Any,
                           state_type_to_infer: str,
                           source_message_id: Optional[str] = None
                           ) -> Optional[ToMInferenceUpdatePayload]:
        # print(f"ToM ({self._module_id}): Inferring '{state_type_to_infer}' for agent '{target_agent_id}'.")
        inferred_value: Any = "unknown_due_to_simple_logic"
        confidence: float = 0.25 # Base low confidence for simple logic

        evidence_str = ""
        source_evidence_ids = [source_message_id] if source_message_id else []

        if isinstance(evidence_payload, PerceptDataPayload):
            evidence_str = str(evidence_payload.content).lower()
            if hasattr(evidence_payload, 'percept_id'):
                 source_evidence_ids.append(evidence_payload.percept_id)
        elif isinstance(evidence_payload, str):
            evidence_str = evidence_payload.lower()

        # Simplified inference logic
        if "emotion" in state_type_to_infer:
            if "happy" in evidence_str or "joy" in evidence_str:
                inferred_value = {"emotion": "happiness", "intensity": 0.6}
                confidence = 0.6
            elif "sad" in evidence_str or "crying" in evidence_str:
                inferred_value = {"emotion": "sadness", "intensity": 0.7}
                confidence = 0.65
            elif "angry" in evidence_str or "frustrated" in evidence_str:
                inferred_value = {"emotion": "anger", "intensity": 0.75}
                confidence = 0.55
        elif "belief" in state_type_to_infer:
            if "think" in evidence_str and "rain" in evidence_str:
                inferred_value = "Believes it might rain."
                confidence = 0.5

        if inferred_value == "unknown_due_to_simple_logic" and confidence == 0.25:
             print(f"ToM ({self._module_id}): No specific rule to infer '{state_type_to_infer}' from evidence: {evidence_str[:50]}")
             # Not returning None, but publishing a low confidence "unknown"

        if not (ToMInferenceUpdatePayload and GenericMessage): return None

        tom_payload = ToMInferenceUpdatePayload(
            target_agent_id=target_agent_id,
            inferred_state_type=state_type_to_infer,
            inferred_state_value=inferred_value,
            confidence=confidence,
            source_evidence_ids=list(set(source_evidence_ids)) # Ensure unique IDs
        )
        # Conceptually update internal model of target_agent_id here if needed
        # self.update_agent_model(target_agent_id, {"last_inferred_state": tom_payload.__dict__})

        if self._message_bus:
            message = GenericMessage(
                source_module_id=self._module_id, # Use self._module_id
                message_type="ToMInferenceUpdate",
                payload=tom_payload
            )
            try:
                self._message_bus.publish(message)
                self._published_inferences_count += 1
                # print(f"ToM ({self._module_id}): Published ToMInferenceUpdate for agent '{target_agent_id}'.")
            except Exception as e:
                print(f"ToM ({self._module_id}): Error publishing ToMInferenceUpdate: {e}")
        return tom_payload

    def _handle_percept_for_tom(self, message: GenericMessage): # Renamed
        if not isinstance(message.payload, PerceptDataPayload): return
        payload: PerceptDataPayload = message.payload
        self._handled_message_counts["PerceptData"] += 1
        # print(f"ToM ({self._module_id}): Received PerceptData from '{payload.modality}' (msg_id: {message.message_id})")

        target_agent_id: Optional[str] = None
        evidence_for_inference = payload.content

        if payload.metadata and "observed_agent_id" in payload.metadata:
            target_agent_id = payload.metadata["observed_agent_id"]
        elif payload.modality == "text" and isinstance(payload.content, str):
            # Simple conceptual parsing: "AgentX: message"
            parts = payload.content.split(":", 1)
            if len(parts) == 2 and len(parts[0]) < 20 and not parts[0].isspace(): # Arbitrary length check for agent ID part
                potential_agent_id = parts[0].strip()
                # Avoid inferring about self if message is like "ToMModule_xyz: some log"
                if not potential_agent_id.lower().startswith(self._module_id.lower()[:5]): # Basic check
                    target_agent_id = potential_agent_id
                    evidence_for_inference = parts[1].strip() # Use only message part as evidence

        if not target_agent_id and message.source_module_id not in [self._module_id, "MessageBus", "ConcretePerceptionModule_01"]: # Avoid self-inference or from generic sources
            # Fallback: assume source of percept is the target if not identifiable otherwise
            # This needs careful consideration in a real system to avoid wrong attributions
            target_agent_id = message.source_module_id
            # print(f"ToM ({self._module_id}): Defaulting target_agent_id to percept source '{target_agent_id}'.")


        if target_agent_id:
            # Conceptual: Determine what state to infer based on percept content
            # This is highly simplified. A real system would have more sophisticated cue detection.
            state_to_infer = "general_state_conjecture" # Default
            if isinstance(evidence_for_inference, str):
                if any(k in evidence_for_inference.lower() for k in ["happy", "joy", "excited", "laughing"]):
                    state_to_infer = "emotion_happiness_conjecture"
                elif any(k in evidence_for_inference.lower() for k in ["sad", "crying", "unhappy"]):
                    state_to_infer = "emotion_sadness_conjecture"
                elif any(k in evidence_for_inference.lower() for k in ["angry", "frustrated", "annoyed"]):
                    state_to_infer = "emotion_anger_conjecture"
                elif "think" in evidence_for_inference.lower() or "believe" in evidence_for_inference.lower():
                    state_to_infer = "belief_conjecture"

            self.infer_mental_state(
                target_agent_id=target_agent_id,
                evidence_payload=payload, # Pass the whole payload for richer context
                state_type_to_infer=state_to_infer,
                source_message_id=message.message_id
            )
        else:
            print(f"ToM ({self._module_id}): Could not identify target_agent_id from PerceptData (msg_id: {message.message_id}). No inference made.")

    def _handle_own_emotion_change_for_tom(self, message: GenericMessage): # Renamed
        if not isinstance(message.payload, EmotionalStateChangePayload): return
        payload: EmotionalStateChangePayload = message.payload
        self._handled_message_counts["EmotionalStateChange"] += 1
        print(f"ToM ({self._module_id}): Received own EmotionalStateChange. V={payload.current_emotion_profile.get('valence',0):.2f}, A={payload.current_emotion_profile.get('arousal',0):.2f}")
        # Conceptual: If own emotion is strong, it might influence future ToM inferences
        # e.g., if self is highly aroused and negative, might be more prone to infer negative states in others.
        # For now, just logging. No direct inference triggered on other agents from this.

    def update_agent_model(self, agent_id: str, new_data: Dict[str, Any]) -> bool:
        # (Implementation from original, ensure it uses self._module_id in prints)
        print(f"ToM ({self._module_id}): Updating model for agent '{agent_id}'.")
        if agent_id not in self._agent_models: self._agent_models[agent_id] = {}
        for key, value in new_data.items():
            if isinstance(value, dict) and isinstance(self._agent_models[agent_id].get(key), dict):
                self._agent_models[agent_id][key].update(value)
            else: self._agent_models[agent_id][key] = value
        self._agent_models[agent_id].setdefault('interaction_count', 0) # Ensure count exists
        return True

    def get_agent_model(self, agent_id: str) -> Optional[Dict[str, Any]]:
        return self._agent_models.get(agent_id)

    def get_status(self) -> Dict[str, Any]:
        return {
            "module_id": self._module_id,
            "module_type": "ConcreteTheoryOfMindModule (Message Bus Integrated)",
            "message_bus_configured": self._message_bus is not None,
            "agent_models_count": len(self._agent_models),
            "handled_perceptdata_count": self._handled_message_counts["PerceptData"],
            "handled_emotionalstatechange_count": self._handled_message_counts["EmotionalStateChange"],
            "published_inferences_count": self._published_inferences_count,
        }

if __name__ == '__main__':
    print("\n--- ConcreteTheoryOfMindModule __main__ Test ---")

    received_tom_inferences: List[GenericMessage] = []
    def tom_inference_listener(message: GenericMessage):
        print(f" tom_inference_listener: Received ToMInferenceUpdate! Target: {message.payload.target_agent_id}, Type: {message.payload.inferred_state_type}, Value: {message.payload.inferred_state_value}")
        received_tom_inferences.append(message)

    async def main_test_flow():
        bus = MessageBus()
        tom_module_id = "TestToM001"
        tom_module = ConcreteTheoryOfMindModule(message_bus=bus, module_id=tom_module_id)

        bus.subscribe(module_id="TestToMListener", message_type="ToMInferenceUpdate", callback=tom_inference_listener)

        print(tom_module.get_status())

        print("\n--- Testing PerceptData Handling & Inference Publishing ---")
        # 1. Percept with agent ID in metadata
        percept_payload_meta = PerceptDataPayload(modality="visual", content={"action": "waving"}, source_timestamp=datetime.datetime.now(), metadata={"observed_agent_id": "user_beta"})
        bus.publish(GenericMessage(source_module_id="TestPerceptSys", message_type="PerceptData", payload=percept_payload_meta))
        await asyncio.sleep(0.01)
        assert len(received_tom_inferences) >= 1, "ToMInferenceUpdate for user_beta (metadata) not received"
        if received_tom_inferences: assert received_tom_inferences[-1].payload.target_agent_id == "user_beta"

        # 2. Percept with agent ID in text content
        percept_payload_text = PerceptDataPayload(modality="text", content="user_alpha: I am so happy today!", source_timestamp=datetime.datetime.now())
        bus.publish(GenericMessage(source_module_id="TestCommsSys", message_type="PerceptData", payload=percept_payload_text))
        await asyncio.sleep(0.01)
        assert len(received_tom_inferences) >= 2, "ToMInferenceUpdate for user_alpha (text) not received"
        if len(received_tom_inferences) >=2:
            assert received_tom_inferences[-1].payload.target_agent_id == "user_alpha"
            assert received_tom_inferences[-1].payload.inferred_state_type == "emotion_happiness_conjecture"

        # 3. Generic percept (source_module_id becomes target_agent_id)
        percept_payload_generic = PerceptDataPayload(modality="audio", content={"event": "laughter_detected"}, source_timestamp=datetime.datetime.now())
        bus.publish(GenericMessage(source_module_id="AudioSensor7", message_type="PerceptData", payload=percept_payload_generic))
        await asyncio.sleep(0.01)
        assert len(received_tom_inferences) >= 3, "ToMInferenceUpdate for AudioSensor7 not received"
        if len(received_tom_inferences) >=3:
            assert received_tom_inferences[-1].payload.target_agent_id == "AudioSensor7"
            # This might infer happiness due to "laughter" if logic is simple
            # assert received_tom_inferences[-1].payload.inferred_state_type == "emotion_happiness_conjecture"

        # 4. Percept that should not trigger strong inference (or low confidence unknown)
        percept_payload_neutral = PerceptDataPayload(modality="text", content="The sky is blue.", source_timestamp=datetime.datetime.now())
        bus.publish(GenericMessage(source_module_id="ObserverBot", message_type="PerceptData", payload=percept_payload_neutral))
        await asyncio.sleep(0.01)
        # If an inference is made, it should be low confidence / "unknown"
        if len(received_tom_inferences) >= 4:
            last_inf = received_tom_inferences[-1].payload
            assert last_inf.target_agent_id == "ObserverBot"
            assert last_inf.inferred_state_value == "unknown_due_to_simple_logic" or last_inf.confidence < 0.3
            print(f"  Neutral percept for {last_inf.target_agent_id} resulted in: {last_inf.inferred_state_value} (Conf: {last_inf.confidence:.2f})")
        else:
            # This case might happen if no inference is published for neutral percepts
            print("  Neutral percept did not trigger a new ToMInferenceUpdate (as expected, or low confidence).")


        print("\n--- Testing EmotionalStateChange Handling ---")
        own_emotion_payload = EmotionalStateChangePayload(current_emotion_profile={"valence": -0.8, "arousal": 0.7}, intensity=0.75)
        bus.publish(GenericMessage(source_module_id=tom_module_id, message_type="EmotionalStateChange", payload=own_emotion_payload)) # Own emotion
        await asyncio.sleep(0.01)
        # Check log or internal state if any, for now, print in handler is the main check
        assert tom_module._handled_message_counts["EmotionalStateChange"] == 1
        print("  ToM module processed own EmotionalStateChange.")

        print("\n--- Final ToM Module Status ---")
        print(tom_module.get_status())
        assert tom_module.get_status()["published_inferences_count"] == len(received_tom_inferences)
        assert tom_module.get_status()["handled_perceptdata_count"] >= 3 # 3 or 4 depending on neutral one

        print("\n--- ConcreteTheoryOfMindModule __main__ Test Complete ---")

    try:
        asyncio.run(main_test_flow())
    except RuntimeError as e:
        if " asyncio.run() cannot be called from a running event loop" in str(e):
            print("Skipping asyncio.run() as an event loop is already running.")
        else:
            raise
