from typing import Any, Dict, Optional, List
import uuid # Though not directly used in ToMInferenceUpdatePayload default_factory for ID
import datetime # For ToMInferenceUpdatePayload timestamp

try:
    from .base_theory_of_mind_module import BaseTheoryOfMindModule
    from .message_bus import MessageBus
    from .core_messages import GenericMessage, PerceptDataPayload, ToMInferenceUpdatePayload
    # EmotionalStateChangePayload will be treated as Dict for now
except ImportError:
    from base_theory_of_mind_module import BaseTheoryOfMindModule
    try:
        from message_bus import MessageBus
        from core_messages import GenericMessage, PerceptDataPayload, ToMInferenceUpdatePayload
    except ImportError:
        MessageBus = None # type: ignore
        GenericMessage = None # type: ignore
        PerceptDataPayload = None # type: ignore
        ToMInferenceUpdatePayload = None # type: ignore


class ConcreteTheoryOfMindModule(BaseTheoryOfMindModule):
    """
    A concrete implementation of the BaseTheoryOfMindModule.
    This version uses a dictionary to store models of other agents,
    can subscribe to PerceptData and EmotionalStateChange messages,
    and publish ToMInferenceUpdate messages.
    """

    def __init__(self, message_bus: Optional[MessageBus] = None):
        """
        Initializes the ConcreteTheoryOfMindModule.

        Args:
            message_bus: An optional instance of MessageBus for communication.
        """
        self._agent_models: Dict[str, Dict[str, Any]] = {}
        self.message_bus = message_bus
        self.handled_percepts_for_tom: List[PerceptDataPayload] = []
        self.handled_own_emotions_for_tom: List[Dict] = [] # Assuming dict for EmotionalStateChangePayload
        self.recent_inferences: List[ToMInferenceUpdatePayload] = []

        bus_status_msg = "not configured"
        if self.message_bus:
            if GenericMessage and PerceptDataPayload and ToMInferenceUpdatePayload: # Check core imports
                try:
                    self.message_bus.subscribe(
                        module_id="ConcreteTheoryOfMindModule_01", # Example ID
                        message_type="PerceptData",
                        callback=self.handle_percept_for_tom
                    )
                    self.message_bus.subscribe(
                        module_id="ConcreteTheoryOfMindModule_01",
                        message_type="EmotionalStateChange", # Assuming this is the message type string
                        callback=self.handle_own_emotion_change_for_tom
                    )
                    bus_status_msg = "configured and subscribed to PerceptData & EmotionalStateChange"
                except Exception as e:
                    bus_status_msg = f"configured but FAILED to subscribe: {e}"
            else:
                bus_status_msg = "configured but core message types for subscription not available"

        print(f"ConcreteTheoryOfMindModule initialized. Message bus {bus_status_msg}.")

    def infer_mental_state(self,
                           target_agent_id: str,
                           evidence_payload: Any, # Could be PerceptDataPayload, string, dict etc.
                           state_type_to_infer: str,
                           source_message_id: Optional[str] = None
                           ) -> Optional[ToMInferenceUpdatePayload]:
        """
        Conceptually infers a mental state and publishes it.
        For PoC, uses simple keyword checks on evidence if it's a string.
        """
        # print(f"ToM: Attempting to infer '{state_type_to_infer}' for agent '{target_agent_id}' based on evidence: {str(evidence_payload)[:100]}")

        inferred_value: Any = "unknown"
        confidence: float = 0.3 # Default low confidence

        # Simplified inference logic for PoC
        evidence_str = ""
        if isinstance(evidence_payload, PerceptDataPayload):
            evidence_str = str(evidence_payload.content).lower()
        elif isinstance(evidence_payload, str):
            evidence_str = evidence_payload.lower()

        source_evidence_ids = [source_message_id] if source_message_id else []
        if hasattr(evidence_payload, 'percept_id'): # If evidence is PerceptDataPayload like
            source_evidence_ids.append(evidence_payload.percept_id)


        if state_type_to_infer == "emotion_sadness_conjecture":
            if "sad" in evidence_str or "crying" in evidence_str:
                inferred_value = {"emotion": "sadness", "intensity_qualitative": "moderate"}
                confidence = 0.6
        elif state_type_to_infer == "emotion_happiness_conjecture":
             if "happy" in evidence_str or "joy" in evidence_str or "laughing" in evidence_str:
                inferred_value = {"emotion": "happiness", "intensity_qualitative": "moderate"}
                confidence = 0.65
        elif state_type_to_infer == "belief_about_weather":
            if "raining" in evidence_str:
                inferred_value = "Believes it is raining"
                confidence = 0.7
        else:
            # print(f"ToM: No specific rule to infer '{state_type_to_infer}' from this evidence.")
            return None # Or publish with low confidence "unknown" state

        if not (ToMInferenceUpdatePayload and GenericMessage): # Check imports
            print("Error: ToMInferenceUpdatePayload or GenericMessage not available. Cannot create/publish inference.")
            return None

        tom_payload = ToMInferenceUpdatePayload(
            target_agent_id=target_agent_id,
            inferred_state_type=state_type_to_infer,
            inferred_state_value=inferred_value,
            confidence=confidence,
            source_evidence_ids=source_evidence_ids
        )
        self.recent_inferences.append(tom_payload)
        # print(f"ToM: Inference made: {tom_payload}")

        if self.message_bus:
            message = GenericMessage(
                source_module_id="ConcreteTheoryOfMindModule_01", # Example ID
                message_type="ToMInferenceUpdate",
                payload=tom_payload
            )
            try:
                self.message_bus.publish(message)
                # print(f"ToM: Published ToMInferenceUpdate for agent '{target_agent_id}'.")
            except Exception as e:
                print(f"ToM: Error publishing ToMInferenceUpdate: {e}")

        return tom_payload

    def handle_percept_for_tom(self, message: GenericMessage):
        """Handles PerceptData messages for ToM processing."""
        if PerceptDataPayload and isinstance(message.payload, PerceptDataPayload):
            payload: PerceptDataPayload = message.payload
            self.handled_percepts_for_tom.append(payload)
            # print(f"ToM: Received PerceptData from '{payload.modality}' (msg_id: {message.message_id})")

            # Conceptual: Analyze percept for social cues.
            # Example: If text percept contains "I am sad", infer sadness.
            if payload.modality == "text" and isinstance(payload.content, str):
                if "sad" in payload.content.lower() or "unhappy" in payload.content.lower():
                    # Assuming the source of percept is the target agent for ToM inference
                    # This is a simplification; target_agent_id might come from elsewhere.
                    target_id = message.source_module_id # Or parse from content if it's like "UserX said: I am sad"
                    if target_id == "ConcretePerceptionModule_01": target_id = "unknown_user_from_direct_percept"

                    self.infer_mental_state(
                        target_agent_id=target_id,
                        evidence_payload=payload.content, # Pass the content string as evidence
                        state_type_to_infer="emotion_sadness_conjecture",
                        source_message_id=message.message_id
                    )
        else:
            print(f"ToM: Received PerceptData with unexpected payload type: {type(message.payload)}")

    def handle_own_emotion_change_for_tom(self, message: GenericMessage):
        """Handles agent's own EmotionalStateChange messages for ToM processing (e.g., for empathy modeling)."""
        # Assuming EmotionalStateChangePayload is a dict for now, as per prompt.
        if isinstance(message.payload, dict) and "valence" in message.payload and "arousal" in message.payload:
            payload: dict = message.payload
            self.handled_own_emotions_for_tom.append(payload)
            # print(f"ToM: Received own EmotionalStateChange: V={payload.get('valence')}, A={payload.get('arousal')}")
            # Future: Agent's own emotional state can bias ToM inferences (e.g., projection, empathy level).
            # This could trigger self.infer_mental_state about *another* agent if contextually relevant.
            # E.g., if I am sad, I might infer others are more likely to be sad (projection),
            # or I might be more sensitive to sadness cues in others (empathy).
        else:
            print(f"ToM: Received EmotionalStateChange with unexpected payload structure: {type(message.payload)}")


    def update_agent_model(self, agent_id: str, new_data: Dict[str, Any]) -> bool:
        """
        Updates the stored model for a specific agent.
        Merges new_data into the agent's model.
        """
        print(f"ConcreteToMModule: Updating model for agent '{agent_id}' with data: {new_data}")
        if agent_id not in self._agent_models:
            self._agent_models[agent_id] = {}
            print(f"ConcreteToMModule: Created new model for agent '{agent_id}'.")

        # Simple dictionary update/merge
        for key, value in new_data.items():
            if isinstance(value, dict) and isinstance(self._agent_models[agent_id].get(key), dict):
                self._agent_models[agent_id][key].update(value)
            else:
                self._agent_models[agent_id][key] = value

        # Ensure interaction_count is present if not already
        self._agent_models[agent_id].setdefault('interaction_count', 0)

        print(f"ConcreteToMModule: Model for '{agent_id}' updated. Current model: {self._agent_models[agent_id]}")
        return True

    def get_agent_model(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves the model for a specific agent."""
        print(f"ConcreteToMModule: Retrieving model for agent '{agent_id}'.")
        return self._agent_models.get(agent_id) # Returns None if agent_id not found

if __name__ == '__main__':
    tom_module = ConcreteTheoryOfMindModule()

    # Initial state
    print("\n--- Initial State (No Models) ---")
    print("Model for user1:", tom_module.get_agent_model("user1"))

    # Update agent model directly
    print("\n--- Updating Agent Model (user1) ---")
    tom_module.update_agent_model("user1", {"known_preference": "likes_tea", "last_mood": "neutral"})
    print("Model for user1 after update:", tom_module.get_agent_model("user1"))
    tom_module.update_agent_model("user1", {"known_preference": "likes_coffee", "interaction_count": 5}) # Overwrite and add
    print("Model for user1 after second update:", tom_module.get_agent_model("user1"))


    # Infer mental state for a new agent (user2)
    print("\n--- Inferring Mental State (user2) ---")
    observables_user2 = {'utterance': "I want that shiny red ball!", 'expression': 'pointing', 'affective_cues': ['excited']}
    inferred_user2 = tom_module.infer_mental_state("user2", observables_user2, context={'situation': 'playground'})
    print("Inferred state for user2:", inferred_user2)
    print("Model for user2 after inference:", tom_module.get_agent_model("user2"))

    # Another inference for user2
    observables_user2_sad = {'utterance': "I lost the ball.", 'affective_cues': ['sad', 'crying']}
    inferred_user2_sad = tom_module.infer_mental_state("user2", observables_user2_sad)
    print("Second inferred state for user2:", inferred_user2_sad)
    print("Model for user2 after second inference:", tom_module.get_agent_model("user2"))

    # Infer mental state for existing agent (user1)
    print("\n--- Inferring Mental State (user1) ---")
    observables_user1 = {'utterance': "I am happy today.", 'expression': 'smiling', 'affective_cues': ['happy']}
    inferred_user1 = tom_module.infer_mental_state("user1", observables_user1)
    print("Inferred state for user1:", inferred_user1)
    print("Model for user1 after inference:", tom_module.get_agent_model("user1"))


    # Get non-existent agent model
    print("\n--- Get Non-existent Model (user3) ---")
    print("Model for user3:", tom_module.get_agent_model("user3"))

    print("\nExample Usage Complete.")
