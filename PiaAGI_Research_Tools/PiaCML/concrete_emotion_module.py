from typing import Any, Dict, List, Optional
import uuid # For module ID generation if needed, and triggering_event_id
import datetime # For payloads if not already imported by core_messages

try:
    from .base_emotion_module import BaseEmotionModule
    from .message_bus import MessageBus # Import MessageBus
    from .core_messages import GenericMessage, GoalUpdatePayload, EmotionalStateChangePayload # Import message types
except ImportError:
    # Fallback for standalone execution or if .base_emotion_module is not found in the current path
    print("Warning: Running ConcreteEmotionModule with stubbed imports (MessageBus, core_messages, BaseEmotionModule).")
    class BaseEmotionModule: # Minimal stub
        def update_emotional_state(self, appraisal_info: Dict[str, Any], event_source: Optional[str] = None) -> None: pass
        def get_current_emotional_state(self) -> Dict[str, Any]: return {}
        def express_emotion(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]: return {}
        def get_status(self) -> Dict[str, Any]: return {}
        def regulate_emotion(self, strategy: str, target_emotion_details: Dict) -> bool: return False
        def get_emotional_influence_on_cognition(self) -> Dict: return {}
        def set_personality_profile(self, profile: Dict) -> None: pass

    class MessageBus: # Minimal stub
        def subscribe(self, module_id: str, message_type: str, callback: Any, metadata_filter: Optional[Dict[str,Any]] = None): pass
        def publish(self, message: Any, dispatch_mode: str = "synchronous"): pass

    class GenericMessage: pass
    class GoalUpdatePayload: pass
    class EmotionalStateChangePayload: pass


class ConcreteEmotionModule(BaseEmotionModule):
    """
    A concrete implementation of the BaseEmotionModule focusing on a dimensional
    emotional state (Valence, Arousal, Dominance - VAD).
    Integrated with a MessageBus for receiving GoalUpdates and publishing EmotionalStateChanges.
    """

    def __init__(self,
                 initial_vad_state: Optional[Dict[str, float]] = None,
                 message_bus: Optional[MessageBus] = None,
                 module_id: str = f"ConcreteEmotionModule_{str(uuid.uuid4())[:8]}"):
        """
        Initializes the emotion module.

        Args:
            initial_vad_state: Optional dictionary to set the initial VAD state.
                               Defaults to {"valence": 0.0, "arousal": 0.0, "dominance": 0.0}.
            message_bus: Optional instance of the MessageBus for communication.
            module_id: A unique identifier for this module instance.
        """
        self._message_bus = message_bus
        self._module_id = module_id

        if initial_vad_state is None:
            self.current_emotion_state: Dict[str, float] = {"valence": 0.0, "arousal": 0.0, "dominance": 0.0}
        else:
            self.current_emotion_state: Dict[str, float] = {
                "valence": self._clamp_value(initial_vad_state.get("valence", 0.0)),
                "arousal": self._clamp_value(initial_vad_state.get("arousal", 0.0), 0.0, 1.0), # Arousal typically 0-1
                "dominance": self._clamp_value(initial_vad_state.get("dominance", 0.0))
            }

        self._reactivity_modifier_arousal: float = 1.0
        self._personality_profile: Optional[Dict[str, Any]] = None
        self._log: List[str] = [] # Initialize log

        bus_status_msg = "initialized without a message bus"
        if self._message_bus:
            subscriptions = [
                ("GoalUpdate", self._handle_goal_update_for_appraisal),
                ("PerceptData", self._handle_percept_data_for_appraisal), # New
                ("ActionEvent", self._handle_action_event_for_appraisal)   # New
            ]
            subscribed_types = []
            try:
                # Ensure core message types are available if using type hints for them in handlers
                # from .core_messages import PerceptDataPayload, ActionEventPayload # Already imported at top
                for msg_type, callback in subscriptions:
                    self._message_bus.subscribe(
                        module_id=self._module_id,
                        message_type=msg_type,
                        callback=callback
                    )
                    subscribed_types.append(msg_type)
                if subscribed_types:
                    bus_status_msg = f"initialized and subscribed to: {', '.join(subscribed_types)}"
                else: # Should not happen if subscriptions list is not empty
                    bus_status_msg = "initialized but no subscriptions made"
            except Exception as e:
                bus_status_msg = f"FAILED to subscribe: {e}"

        self._log_message(f"ConcreteEmotionModule '{self._module_id}' {bus_status_msg}.")


    def _log_message(self, message: str):
        """Helper method for internal logging."""
        log_entry = f"{datetime.datetime.now(datetime.timezone.utc).isoformat()} [{self._module_id}]: {message}"
        self._log.append(log_entry)
        # print(log_entry) # Optional for real-time debugging

    def _clamp_value(self, value: float, min_val: float = -1.0, max_val: float = 1.0) -> float:
        """Clamps a value between a minimum and maximum."""
        return max(min_val, min(value, max_val))

    def get_emotional_state(self) -> Dict[str, float]:
        """Returns a copy of the current VAD emotional state."""
        return self.current_emotion_state.copy()

    def _decay_emotions(self, decay_factor: float = 0.95) -> None:
        """
        Applies decay to the current emotional state, moving values towards neutral (0.0).
        Arousal might decay towards a baseline slightly above 0 if preferred.
        """
        self.current_emotion_state["valence"] = self._clamp_value(self.current_emotion_state["valence"] * decay_factor)
        # Arousal decays towards 0, but remains non-negative
        self.current_emotion_state["arousal"] = self._clamp_value(self.current_emotion_state["arousal"] * decay_factor, 0.0, 1.0)
        self.current_emotion_state["dominance"] = self._clamp_value(self.current_emotion_state["dominance"] * decay_factor)
        # print(f"Debug: Emotions decayed to V:{self.current_emotion_state['valence']:.2f} A:{self.current_emotion_state['arousal']:.2f} D:{self.current_emotion_state['dominance']:.2f}")

    def _handle_goal_update_for_appraisal(self, message: GenericMessage) -> None:
        """
        Handles GoalUpdate messages from the message bus and triggers appraisal.
        """
        if not isinstance(message.payload, GoalUpdatePayload):
            print(f"ERROR ({self._module_id}): Received non-GoalUpdatePayload for _handle_goal_update_for_appraisal: {type(message.payload)}")
            return

        payload: GoalUpdatePayload = message.payload
        print(f"INFO ({self._module_id}): Handling GoalUpdate: {payload.goal_id}, Status: {payload.status}, Priority: {payload.priority}")

        event_details: Dict[str, Any] = {
            "type": "GOAL_STATUS_UPDATE",
            "intensity": self._clamp_value(payload.priority * 0.5, 0.0, 1.0), # Scale priority to intensity (0-1)
            "goal_importance": self._clamp_value(payload.priority, 0.0, 1.0),
            "triggering_message_id": message.message_id # Pass message ID for traceability
        }

        status_to_congruence = {
            "achieved": 1.0,
            "failed": -1.0,
            "active": 0.1,  # Slightly positive as it's being pursued
            "suspended": -0.2, # Slightly negative as it's paused
            "new": 0.05, # Mildly positive for new goals
            "updated": 0.0, # Neutral for simple updates unless content implies more
            "progressing": 0.3, # From previous compatibility logic
            "threatened": -0.5   # From previous compatibility logic
        }
        event_details["goal_congruence"] = status_to_congruence.get(payload.status.lower(), 0.0)

        # Consider adding other appraisal dimensions if derivable from GoalUpdatePayload
        # For example, if a goal is "new", it might imply some novelty.
        if payload.status.lower() == "new":
            event_details["novelty"] = 0.6 # New goals are somewhat novel
            event_details["expectedness"] = 0.4 # And perhaps not fully expected

        self.appraise_event(event_details)

    def _handle_percept_data_for_appraisal(self, message: GenericMessage) -> None:
        """Handles PerceptData messages for emotional appraisal."""
        # Ensure PerceptDataPayload is imported if type checking: from .core_messages import PerceptDataPayload
        if not hasattr(message.payload, 'modality') or not hasattr(message.payload, 'content'): # Basic check for PerceptDataPayload structure
            self._log_message(f"ERROR: Received non-PerceptDataPayload for _handle_percept_data_for_appraisal: {type(message.payload)}")
            return

        payload = message.payload # Assuming it's PerceptDataPayload
        self._log_message(f"Handling PerceptData for appraisal: Modality='{payload.modality}', Content='{str(payload.content)[:100]}...'")

        event_details: Dict[str, Any] = {
            "type": f"PERCEPTION_{payload.modality.upper()}",
            "intensity": 0.5, # Default intensity for percepts
            "novelty": 0.5,   # Default novelty
            "expectedness": 0.5, # Default expectedness
            "triggering_message_id": message.message_id
        }

        if payload.modality == "sound" and isinstance(payload.content, dict) and payload.content.get("type") == "sudden_loud_noise":
            event_details["intensity"] = 0.9
            event_details["novelty"] = 0.8
            event_details["expectedness"] = 0.1 # Unexpected
            self._log_message(f"Appraisal derived from 'sudden_loud_noise': High intensity, novelty; Low expectedness.")
        elif payload.modality == "text" and isinstance(payload.content, dict):
            sentiment = payload.content.get("sentiment", "neutral")
            keywords = payload.content.get("keywords", [])
            if sentiment == "very_negative" or "warning" in keywords or "danger" in keywords:
                event_details["intensity"] = 0.8
                event_details["goal_congruence"] = -0.7 # Conceptual: implies general threat/negative impact
                event_details["expectedness"] = 0.3 # Negative events often less expected
                self._log_message(f"Appraisal derived from negative text/keywords: High intensity, negative congruence.")
            elif sentiment == "very_positive" or "congratulations" in keywords:
                event_details["intensity"] = 0.7
                event_details["goal_congruence"] = 0.6
                self._log_message(f"Appraisal derived from positive text/keywords: Positive congruence.")

        self.appraise_event(event_details)

    def _handle_action_event_for_appraisal(self, message: GenericMessage) -> None:
        """Handles ActionEvent messages for emotional appraisal."""
        # Ensure ActionEventPayload is imported if type checking: from .core_messages import ActionEventPayload
        if not hasattr(message.payload, 'action_type') or not hasattr(message.payload, 'status'): # Basic check
            self._log_message(f"ERROR: Received non-ActionEventPayload for _handle_action_event_for_appraisal: {type(message.payload)}")
            return

        payload = message.payload # Assuming it's ActionEventPayload
        self._log_message(f"Handling ActionEvent for appraisal: Type='{payload.action_type}', Status='{payload.status}'")

        # Conceptual mapping
        intensity = payload.outcome.get("action_priority", 0.5) if payload.outcome else 0.5 # Assuming outcome might contain priority
        goal_importance = payload.outcome.get("goal_priority", 0.5) if payload.outcome else 0.5

        goal_congruence = 0.0
        expectedness = 0.5 # Neutral expectedness by default

        if payload.status == "SUCCESS":
            goal_congruence = 0.8
            expectedness = 0.7 # Successful actions might be more expected if agent is competent
        elif payload.status == "FAILURE":
            goal_congruence = -0.8
            expectedness = 0.3 # Failures might be less expected
            intensity = max(intensity, 0.6) # Failures can be more intense emotionally

        event_details: Dict[str, Any] = {
            "type": f"ACTION_OUTCOME_{payload.action_type.upper()}",
            "intensity": self._clamp_value(intensity, 0.0, 1.0),
            "goal_congruence": goal_congruence,
            "goal_importance": self._clamp_value(goal_importance, 0.0, 1.0),
            "expectedness": expectedness,
            "triggering_message_id": message.message_id
        }
        self._log_message(f"Appraisal derived from ActionEvent: Congruence={goal_congruence}, Expectedness={expectedness}, Intensity={event_details['intensity']}.")
        self.appraise_event(event_details)

    def appraise_event(self, event_details: Dict[str, Any]) -> None:
        """
        Appraises an event and updates the VAD emotional state.
        If a message bus is configured, publishes an EmotionalStateChange message.

        Args:
            event_details: A dictionary containing details about the event. Example structure:
                {
                    "type": str, // e.g., "GOAL_PROGRESS", "PERCEPTION_SOUND", "ACTION_OUTCOME_NAVIGATE"
                    "intensity": float, // Perceived intensity of the event (0-1)
                    "novelty": float, // (0-1) - Optional, defaults if not present
                    "expectedness": float, // 0 (unexpected) to 1 (expected) - Optional, defaults
                    "goal_congruence": Optional[float], // -1 (obstructs) to 1 (achieves), 0 (neutral) - Optional
                    "goal_importance": Optional[float], // (0-1) Priority of the affected goal - Optional
                    "controllability": Optional[float], // (0-1) Agent's perceived control - Optional
                    "norm_alignment": Optional[float] // -1 (violates norms) to 1 (aligns) - Optional
                }
        """
        self._log_message(f"Appraising event: Type='{event_details.get('type', 'N/A')}', Intensity='{event_details.get('intensity', 'N/A')}'")

        valence_change = 0.0
        arousal_change = 0.0
        dominance_change = 0.0

        intensity = event_details.get("intensity", 0.1) # Default to low intensity if not specified

        # Valence updates
        if "goal_congruence" in event_details:
            goal_congruence = event_details.get("goal_congruence", 0.0)
            goal_importance = event_details.get("goal_importance", 0.5)
            valence_change += goal_congruence * goal_importance * intensity

        if "norm_alignment" in event_details:
            norm_alignment = event_details.get("norm_alignment", 0.0)
            valence_change += norm_alignment * 0.3 * intensity # Norm alignment has some impact

        # Arousal updates
        current_arousal_reactivity = self._reactivity_modifier_arousal # Could be influenced by personality
        base_arousal_from_intensity = intensity * 0.5
        arousal_change += base_arousal_from_intensity

        # More unexpected -> more arousal
        arousal_change += (1.0 - event_details.get("expectedness", 0.5)) * 0.5 * intensity
        # Novelty adds to arousal
        arousal_change += event_details.get("novelty", 0.0) * 0.3 * intensity

        if "goal_congruence" in event_details: # Significant goal events are arousing
            arousal_change += abs(event_details.get("goal_congruence", 0.0)) * \
                              event_details.get("goal_importance", 0.1) * \
                              intensity * 0.5 # Scaled by importance and intensity

        arousal_change *= current_arousal_reactivity # Apply overall reactivity

        # Dominance updates
        if "controllability" in event_details:
            controllability = event_details.get("controllability", 0.5)
            dominance_change += (controllability - 0.5) * 0.5 * intensity # More control -> more dominance

        # Apply changes to current_emotion_state
        self.current_emotion_state["valence"] += valence_change
        self.current_emotion_state["arousal"] += arousal_change
        self.current_emotion_state["dominance"] += dominance_change

        # Clamp values
        self.current_emotion_state["valence"] = self._clamp_value(self.current_emotion_state["valence"])
        self.current_emotion_state["arousal"] = self._clamp_value(self.current_emotion_state["arousal"], 0.0, 1.0) # Arousal 0-1
        self.current_emotion_state["dominance"] = self._clamp_value(self.current_emotion_state["dominance"])

        # print(f"Debug: VAD before decay: V:{self.current_emotion_state['valence']:.2f} A:{self.current_emotion_state['arousal']:.2f} D:{self.current_emotion_state['dominance']:.2f}")
        self._decay_emotions() # Apply decay after each appraisal update

        self._log_message(f"VAD updated to V:{self.current_emotion_state['valence']:.2f} A:{self.current_emotion_state['arousal']:.2f} D:{self.current_emotion_state['dominance']:.2f}")

        if self._message_bus and EmotionalStateChangePayload and GenericMessage: # Check core types too
            esc_payload = EmotionalStateChangePayload(
                current_emotion_profile=self.current_emotion_state.copy(),
                primary_emotion=None, # Optional for now
                intensity=self.current_emotion_state['arousal'], # Using arousal as overall intensity proxy
                triggering_event_id=event_details.get("triggering_message_id"),
                behavioral_impact_suggestions=[] # Optional for now
            )
            emotional_change_message = GenericMessage(
                source_module_id=self._module_id,
                message_type="EmotionalStateChange",
                payload=esc_payload
            )
            self._message_bus.publish(emotional_change_message)
            self._log_message(f"Published EmotionalStateChange message (triggered by: {esc_payload.triggering_event_id}).")


    def get_simulated_physiological_effects(self) -> Dict[str, Any]:
        """
        Returns a dictionary of conceptual physiological effects based on VAD state.
        """
        effects: Dict[str, Any] = {}
        valence = self.current_emotion_state["valence"]
        arousal = self.current_emotion_state["arousal"]
        # dominance = self.current_emotion_state["dominance"] # For future use

        if arousal > 0.7:
            effects["attention_focus"] = "narrowed"
        elif arousal > 0.4:
            effects["attention_focus"] = "normal" # Conceptual normal range
        else:
            effects["attention_focus"] = "broad"

        if valence < -0.5 and arousal > 0.6:
            effects["cognitive_bias"] = "threat_detection_priority"
        elif valence > 0.5 and arousal > 0.3:
            effects["cognitive_bias"] = "opportunity_seeking"

        if valence > 0.5 and arousal > 0.3: # Positive, somewhat aroused state
            effects["learning_rate_modifier_suggestion"] = 1.2
        elif valence < -0.4: # Negative states
            effects["learning_rate_modifier_suggestion"] = 0.8
        else: # Neutral or low arousal states
            effects["learning_rate_modifier_suggestion"] = 1.0

        # Example using dominance:
        # if dominance < -0.5: effects["action_tendency"] = "avoidance"
        # elif dominance > 0.5: effects["action_tendency"] = "approach"

        return effects

    # --- Compatibility/Update of methods from BaseEmotionModule ABC ---

    def update_emotional_state(self, appraisal_info: Dict[str, Any], event_source: Optional[str] = None) -> None:
        """
        Compatibility method. Delegates to appraise_event.
        The new `appraise_event` expects a more structured `event_details`.
        This method attempts to map `appraisal_info` to that structure.
        """
        self._log_message(f"`update_emotional_state` (compatibility) called. Delegating to `appraise_event`. Source: {event_source}")
        event_details = {
            "type": appraisal_info.get("type", "unknown"), # Retain original event type if available
            "intensity": appraisal_info.get("event_intensity", appraisal_info.get("intensity", 0.5)),
            "novelty": appraisal_info.get("event_novelty", appraisal_info.get("novelty", 0.0)),
            "expectedness": appraisal_info.get("expectedness", 1.0), # Default to expected if not specified
            "controllability": appraisal_info.get("controllability", 0.5), # Default to moderately controllable
            "triggering_message_id": appraisal_info.get("message_id") # If old system passed message_id
        }

        # Map goal_status to goal_congruence
        if appraisal_info.get("type") == "goal_status" or "goal_status" in appraisal_info :
            goal_status = appraisal_info.get("goal_status")
            if goal_status == "achieved": event_details["goal_congruence"] = 1.0
            elif goal_status == "failed": event_details["goal_congruence"] = -1.0
            elif goal_status == "progressing": event_details["goal_congruence"] = 0.3 # Mildly positive
            elif goal_status == "threatened": event_details["goal_congruence"] = -0.5
            event_details["goal_importance"] = appraisal_info.get("goal_importance", 0.5) # Assume default importance

        # Map event_source if it was used for perceived_valence (simplified)
        if isinstance(event_source, dict) and "perceived_valence" in event_source:
            if event_source["perceived_valence"] == "positive":
                event_details["norm_alignment"] = 0.5 # Assume positive event aligns with some norm/goal
            elif event_source["perceived_valence"] == "negative":
                event_details["norm_alignment"] = -0.5

        self.appraise_event(event_details)


    def get_current_emotional_state(self) -> Dict[str, Any]:
        """Returns the current VAD state. Per BaseEmotionModule, this can include categorical."""
        # For Phase 1, we focus on VAD. A mapping to categorical could be added here if needed.
        return {"vad_state": self.current_emotion_state.copy(), "categorical_emotion": "N/A_Phase1"}


    def express_emotion(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Returns a representation of the current VAD state for expression.
        Phase 1: Simplified to return VAD without categorical label.
        """
        self._log_message(f"express_emotion called. VAD: {self.current_emotion_state}")
        return {
            "vad_state": self.current_emotion_state.copy(),
            "intensity_conceptual": self.current_emotion_state['arousal'],
            "expression_modality_hints": ["vocal_tone_change_vad", "facial_expression_vad_based"] # Conceptual
        }

    def get_status(self) -> Dict[str, Any]:
        """Returns the current status of the Emotion Module."""
        return {
            "module_id": self._module_id,
            "module_type": "ConcreteEmotionModule (Message Bus Integrated)",
            "current_vad_state": self.current_emotion_state.copy(),
            "message_bus_connected": self._message_bus is not None,
            "personality_profile_active": self._personality_profile is not None,
            "reactivity_modifier_arousal": self._reactivity_modifier_arousal,
            "log_entries": len(self._log) # Added log entry count
        }

    def regulate_emotion(self, strategy: str, target_emotion_details: Dict[str, Any]) -> bool:
        """Placeholder for emotion regulation. Not implemented in Phase 1."""
        self._log_message(f"regulate_emotion called (Placeholder). Strategy: {strategy}, Target: {target_emotion_details}")
        return False

    def get_emotional_influence_on_cognition(self) -> Dict[str, Any]:
        """
        Returns conceptual influences on cognition based on the VAD state.
        This is similar to get_simulated_physiological_effects for Phase 1.
        """
        self._log_message("get_emotional_influence_on_cognition called.")
        return self.get_simulated_physiological_effects()

    def set_personality_profile(self, profile: Dict[str, Any]) -> None:
        """Sets a personality profile that might influence emotional responses and baseline VAD."""
        self._log_message(f"set_personality_profile called with {profile}.")
        self._personality_profile = profile

        # Adjust baseline VAD based on personality profile, if specified
        if 'default_mood_valence' in profile and isinstance(profile['default_mood_valence'], (int, float)):
            # Could average with current or set directly, here we average towards it
            self.current_emotion_state['valence'] = self._clamp_value(
                (self.current_emotion_state['valence'] + profile['default_mood_valence']) / 2.0
            )
        if 'default_mood_arousal' in profile and isinstance(profile['default_mood_arousal'], (int, float)):
            self.current_emotion_state['arousal'] = self._clamp_value(
                (self.current_emotion_state['arousal'] + profile['default_mood_arousal']) / 2.0, 0.0, 1.0
            )
        if 'default_mood_dominance' in profile and isinstance(profile['default_mood_dominance'], (int, float)):
            self.current_emotion_state['dominance'] = self._clamp_value(
                (self.current_emotion_state['dominance'] + profile['default_mood_dominance']) / 2.0
            )

        if 'reactivity_modifier_arousal' in profile and isinstance(profile['reactivity_modifier_arousal'], (int, float)):
            self._reactivity_modifier_arousal = float(profile['reactivity_modifier_arousal'])

        self._log_message(f"VAD state potentially adjusted by personality: {self.current_emotion_state}")


if __name__ == '__main__':
    import asyncio
    import time
    # Ensure PerceptDataPayload and ActionEventPayload are available for the __main__ if used directly
    # For this refactoring, they are not directly constructed in __main__ but handled by module.
    # However, if you were to add tests here that publish them, you'd need:
    # from .core_messages import PerceptDataPayload, ActionEventPayload # If running as part of package
    # Or define stubs if running standalone and they are not in the stub section.


    # Attempt to import MessageBus and core_messages from the local directory structure
    # This is for the __main__ block to find them if not installed as a package.
    try:
        from message_bus import MessageBus
        from core_messages import GenericMessage, GoalUpdatePayload, EmotionalStateChangePayload
        # Add PerceptDataPayload and ActionEventPayload if you plan to manually create and publish them in __main__
        # from core_messages import PerceptDataPayload, ActionEventPayload
    except ImportError:
        print("CRITICAL: Failed to import MessageBus or core_messages for __main__ test. Ensure they are in Python path or same directory.")
        # Fallback to stubs if they were defined above due to initial import error
        if 'MessageBus' not in globals(): # Re-define if initial import failed and stubs were used
            class MessageBus:
                def subscribe(self, module_id: str, message_type: str, callback: Any, metadata_filter: Optional[Dict[str,Any]] = None): print(f"StubBus: {module_id} subscribed to {message_type}")
                def publish(self, message: Any, dispatch_mode: str = "synchronous"): print(f"StubBus: Publishing {message.message_type}")
            class GenericMessage:
                def __init__(self, source_module_id, message_type, payload, message_id=None):
                    self.source_module_id = source_module_id
                    self.message_type = message_type
                    self.payload = payload
                    self.message_id = message_id or str(uuid.uuid4())
            class GoalUpdatePayload:
                def __init__(self, goal_id, goal_description, priority, status, originator):
                    self.goal_id = goal_id
                    self.goal_description = goal_description
                    self.priority = priority
                    self.status = status
                    self.originator = originator
            class EmotionalStateChangePayload: pass # Already stubbed if needed
            # class PerceptDataPayload: pass # Add if needed for __main__ tests
            # class ActionEventPayload: pass # Add if needed for __main__ tests


    print("--- ConcreteEmotionModule __main__ Test ---")

    # Listener for EmotionalStateChange messages
    received_emotional_states: List[GenericMessage] = []
    def emotional_state_listener(message: GenericMessage):
        print(f"\n émotion_state_listener: Received EmotionalStateChange! ID: {message.message_id[:8]}")
        if hasattr(message.payload, 'current_emotion_profile'): # Check if it's likely an EmotionalStateChangePayload
            payload = message.payload # type: ignore
            print(f"  Source: {message.source_module_id}")
            print(f"  VAD: {payload.current_emotion_profile}") # type: ignore
            print(f"  Intensity (Arousal): {payload.intensity:.2f}") # type: ignore
            print(f"  Triggering Event ID: {payload.triggering_event_id[:8] if payload.triggering_event_id else 'N/A'}") # type: ignore
            received_emotional_states.append(message)
        else:
            print(f"  ERROR: Listener received non-EmotionalStateChangePayload structured message: {type(message.payload)}")

    async def main_test_flow():
        # 1. Setup
        bus = MessageBus()
        emotion_module = ConcreteEmotionModule(message_bus=bus, module_id="EmotionModTest01")

        print("\n--- Initial Status ---")
        print(emotion_module.get_status())
        print("Initial VAD state:", emotion_module.get_emotional_state())

        bus.subscribe(
            module_id="TestListener",
            message_type="EmotionalStateChange",
            callback=emotional_state_listener
        )
        print("\nTestListener subscribed to EmotionalStateChange.")

        # 2. Simulate a GoalUpdate message
        print("\n--- Simulating GoalUpdate (Goal Achieved) ---")
        goal_achieved_payload = GoalUpdatePayload(
            goal_id="test_goal_001",
            goal_description="Test achieving a goal",
            priority=0.8, # High priority
            status="achieved",
            originator="TestSystem"
        )
        goal_achieved_message = GenericMessage(
            source_module_id="GoalSetterModule",
            message_type="GoalUpdate",
            payload=goal_achieved_payload
        )
        bus.publish(goal_achieved_message) # Default sync dispatch

        # Allow some time for bus processing if it were async, or for prints
        await asyncio.sleep(0.05)

        assert len(received_emotional_states) > 0, "EmotionalStateChange was not received by listener"
        if received_emotional_states:
            last_esc_payload = received_emotional_states[-1].payload
            assert isinstance(last_esc_payload, EmotionalStateChangePayload)
            assert last_esc_payload.triggering_event_id == goal_achieved_message.message_id
            # Check if VAD reflects positive change (valence > 0, arousal > 0)
            assert last_esc_payload.current_emotion_profile["valence"] > 0.2 # Increased from 0
            assert last_esc_payload.current_emotion_profile["arousal"] > 0.1 # Increased from 0
            print(f"Listener correctly received EmotionalStateChange triggered by {goal_achieved_message.message_id[:8]}.")


        print("\n--- Simulating GoalUpdate (Goal Failed, Async Dispatch) ---")
        received_emotional_states.clear()
        goal_failed_payload = GoalUpdatePayload(
            goal_id="test_goal_002",
            goal_description="Test failing a goal",
            priority=0.9, # High priority
            status="failed",
            originator="TestSystem"
        )
        goal_failed_message = GenericMessage(
            source_module_id="GoalSetterModule",
            message_type="GoalUpdate",
            payload=goal_failed_payload
        )
        bus.publish(goal_failed_message, dispatch_mode="asynchronous")

        await asyncio.sleep(0.1) # Give async tasks time to run

        assert len(received_emotional_states) > 0, "EmotionalStateChange (async) was not received"
        if received_emotional_states:
            last_esc_payload_async = received_emotional_states[-1].payload
            assert isinstance(last_esc_payload_async, EmotionalStateChangePayload)
            assert last_esc_payload_async.triggering_event_id == goal_failed_message.message_id
            assert last_esc_payload_async.current_emotion_profile["valence"] < -0.2 # Decreased from positive
            print(f"Listener correctly received async EmotionalStateChange triggered by {goal_failed_message.message_id[:8]}.")


        print("\n--- Appraise Event Directly (no bus trigger) ---")
        # This should still publish if bus is available
        received_emotional_states.clear()
        event_direct = {
            "type": "DIRECT_APPRAISAL", "intensity": 0.7, "novelty": 0.1, "expectedness": 0.8,
            "goal_congruence": 0.6, "goal_importance": 0.7, "controllability": 0.6,
            # No "triggering_message_id" for direct calls unless manually added
        }
        emotion_module.appraise_event(event_direct)
        await asyncio.sleep(0.05)

        assert len(received_emotional_states) > 0, "EmotionalStateChange (direct appraisal) was not received"
        if received_emotional_states:
            direct_esc_payload = received_emotional_states[-1].payload
            assert isinstance(direct_esc_payload, EmotionalStateChangePayload)
            assert direct_esc_payload.triggering_event_id is None # Because it wasn't in event_details
            print("Listener correctly received EmotionalStateChange from direct appraisal.")


        print("\n--- Test with NO MessageBus ---")
        emotion_module_no_bus = ConcreteEmotionModule(module_id="NoBusMod")
        print(emotion_module_no_bus.get_status())
        # This should not error and not try to publish
        emotion_module_no_bus.appraise_event({"type": "TEST_NO_BUS", "intensity": 0.5, "goal_congruence": 0.5, "goal_importance": 0.5})
        emotion_module_no_bus._log_message("Appraisal with no bus completed without error.")

        print("\n--- ConcreteEmotionModule __main__ Test Complete ---")

    # Run the async main function
    try:
        asyncio.run(main_test_flow())
    except RuntimeError as e:
        if " asyncio.run() cannot be called from a running event loop" in str(e):
            print("Skipping asyncio.run() as an event loop is already running (e.g. in Jupyter/IPython).")
            # You might need to await main_test_flow() directly if in such an environment.
            # loop = asyncio.get_event_loop()
            # loop.run_until_complete(main_test_flow())
        else:
            raise


    # Old __main__ content for reference or non-bus testing:
    # emotion_module = ConcreteEmotionModule()
    # print("\n--- Initial Status ---")
    # print(emotion_module.get_status())
    # print("Initial VAD state:", emotion_module.get_emotional_state())
    # ... (rest of old main commented out for brevity in diff, but kept in actual file if needed) ...
    # print("\nExample Usage Complete (Phase 1 Enhanced Emotion Module).")
