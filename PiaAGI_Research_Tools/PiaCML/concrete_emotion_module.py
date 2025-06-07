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

        if self._message_bus:
            self._message_bus.subscribe(
                module_id=self._module_id,
                message_type="GoalUpdate",
                callback=self._handle_goal_update_for_appraisal
            )
            print(f"ConcreteEmotionModule '{self._module_id}' initialized and subscribed to 'GoalUpdate' on the message bus.")
        else:
            print(f"ConcreteEmotionModule '{self._module_id}' initialized without a message bus.")


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


    def appraise_event(self, event_details: Dict[str, Any]) -> None:
        """
        Appraises an event and updates the VAD emotional state.
        If a message bus is configured, publishes an EmotionalStateChange message.

        Args:
            event_details: A dictionary containing details about the event. Example structure:
                {
                    "type": str, // e.g., "GOAL_PROGRESS", "EXTERNAL_SENSOR", "SOCIAL_INTERACTION"
                    "intensity": float, // Perceived intensity of the event (0-1)
                    "novelty": float, // (0-1)
                    "expectedness": float, // 0 (unexpected) to 1 (expected)
                    "goal_congruence": Optional[float], // -1 (obstructs) to 1 (achieves), 0 (neutral)
                    "goal_importance": Optional[float], // (0-1) Priority of the affected goal
                    "controllability": Optional[float], // (0-1) Agent's perceived control
                    "norm_alignment": Optional[float] // -1 (violates norms) to 1 (aligns)
                }
        """
        print(f"ConcreteEmotionModule: Appraising event: {event_details.get('type', 'N/A')}")

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

        print(f"ConcreteEmotionModule ({self._module_id}): VAD updated to V:{self.current_emotion_state['valence']:.2f} A:{self.current_emotion_state['arousal']:.2f} D:{self.current_emotion_state['dominance']:.2f}")

        if self._message_bus:
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
            print(f"INFO ({self._module_id}): Published EmotionalStateChange message (triggered by: {esc_payload.triggering_event_id}).")


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
        print(f"ConcreteEmotionModule ({self._module_id}): `update_emotional_state` (compatibility) called. Delegating to `appraise_event`.")
        event_details = {
            "type": appraisal_info.get("type", "unknown"), # Retain original event type if available
            "intensity": appraisal_info.get("event_intensity", appraisal_info.get("intensity", 0.5)), # Check both keys
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
        # print(f"ConcreteEmotionModule ({self._module_id}): express_emotion called. VAD: {self.current_emotion_state}")
        return {
            "vad_state": self.current_emotion_state.copy(),
            "intensity_conceptual": self.current_emotion_state['arousal'], # Using arousal as proxy
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
            "reactivity_modifier_arousal": self._reactivity_modifier_arousal
        }

    def regulate_emotion(self, strategy: str, target_emotion_details: Dict[str, Any]) -> bool:
        """Placeholder for emotion regulation. Not implemented in Phase 1."""
        print(f"ConcreteEmotionModule ({self._module_id}): regulate_emotion called (Placeholder). Strategy: {strategy}, Target: {target_emotion_details}")
        # Conceptual: Could try to shift VAD towards a target, e.g., reduce arousal.
        # Example: if strategy == "dampen_arousal": self.current_emotion_state["arousal"] *= 0.7
        # self._decay_emotions() # Apply decay after conceptual regulation
        return False # No actual regulation applied in this phase

    def get_emotional_influence_on_cognition(self) -> Dict[str, Any]:
        """
        Returns conceptual influences on cognition based on the VAD state.
        This is similar to get_simulated_physiological_effects for Phase 1.
        """
        # print(f"ConcreteEmotionModule ({self._module_id}): get_emotional_influence_on_cognition called.")
        return self.get_simulated_physiological_effects()

    def set_personality_profile(self, profile: Dict[str, Any]) -> None:
        """Sets a personality profile that might influence emotional responses and baseline VAD."""
        print(f"ConcreteEmotionModule ({self._module_id}): set_personality_profile called with {profile}.")
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

        print(f"ConcreteEmotionModule ({self._module_id}): VAD state potentially adjusted by personality: {self.current_emotion_state}")


if __name__ == '__main__':
    import asyncio
    import time

    # Attempt to import MessageBus and core_messages from the local directory structure
    # This is for the __main__ block to find them if not installed as a package.
    try:
        from message_bus import MessageBus
        from core_messages import GenericMessage, GoalUpdatePayload, EmotionalStateChangePayload
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


    print("--- ConcreteEmotionModule __main__ Test ---")

    # Listener for EmotionalStateChange messages
    received_emotional_states: List[GenericMessage] = []
    def emotional_state_listener(message: GenericMessage):
        print(f"\n émotion_state_listener: Received EmotionalStateChange! ID: {message.message_id[:8]}")
        if isinstance(message.payload, EmotionalStateChangePayload):
            payload: EmotionalStateChangePayload = message.payload
            print(f"  Source: {message.source_module_id}")
            print(f"  VAD: {payload.current_emotion_profile}")
            print(f"  Intensity (Arousal): {payload.intensity:.2f}")
            print(f"  Triggering Event ID: {payload.triggering_event_id[:8] if payload.triggering_event_id else 'N/A'}")
            received_emotional_states.append(message)
        else:
            print(f"  ERROR: Listener received non-EmotionalStateChangePayload: {type(message.payload)}")

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
        print("Appraisal with no bus completed without error.")

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
