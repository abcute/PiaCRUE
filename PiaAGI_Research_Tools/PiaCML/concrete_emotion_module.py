from typing import Any, Dict, List, Optional

try:
    from .base_emotion_module import BaseEmotionModule
except ImportError:
    # Fallback for standalone execution or if .base_emotion_module is not found in the current path
    class BaseEmotionModule: # Minimal stub
        def update_emotional_state(self, appraisal_info: Dict[str, Any], event_source: Optional[str] = None) -> None: pass
        def get_current_emotional_state(self) -> Dict[str, Any]: return {}
        def express_emotion(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]: return {}
        def get_status(self) -> Dict[str, Any]: return {}
        def regulate_emotion(self, strategy: str, target_emotion_details: Dict) -> bool: return False
        def get_emotional_influence_on_cognition(self) -> Dict: return {}
        def set_personality_profile(self, profile: Dict) -> None: pass


class ConcreteEmotionModule(BaseEmotionModule):
    """
    A concrete implementation of the BaseEmotionModule focusing on a dimensional
    emotional state (Valence, Arousal, Dominance - VAD).
    Phase 1 enhancements include a more detailed appraisal mechanism based on
    event properties and a basic decay function.
    """

    def __init__(self, initial_vad_state: Optional[Dict[str, float]] = None):
        """
        Initializes the emotion module.

        Args:
            initial_vad_state: Optional dictionary to set the initial VAD state.
                               Defaults to {"valence": 0.0, "arousal": 0.0, "dominance": 0.0}.
        """
        if initial_vad_state is None:
            self.current_emotion_state: Dict[str, float] = {"valence": 0.0, "arousal": 0.0, "dominance": 0.0}
        else:
            self.current_emotion_state: Dict[str, float] = {
                "valence": self._clamp_value(initial_vad_state.get("valence", 0.0)),
                "arousal": self._clamp_value(initial_vad_state.get("arousal", 0.0), 0.0, 1.0), # Arousal typically 0-1
                "dominance": self._clamp_value(initial_vad_state.get("dominance", 0.0))
            }

        # self.decay_rate = 0.05 # Optional, if used in a time-based decay not directly tied to appraise_event
        self._reactivity_modifier_arousal: float = 1.0 # Can be set by personality
        self._personality_profile: Optional[Dict[str, Any]] = None

        print("ConcreteEmotionModule (Phase 1 Enhanced) initialized.")

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


    def appraise_event(self, event_details: Dict[str, Any]) -> None:
        """
        Appraises an event and updates the VAD emotional state.

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

        print(f"ConcreteEmotionModule: VAD updated to V:{self.current_emotion_state['valence']:.2f} A:{self.current_emotion_state['arousal']:.2f} D:{self.current_emotion_state['dominance']:.2f}")


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
        print(f"ConcreteEmotionModule: `update_emotional_state` (compatibility) called. Delegating to `appraise_event`.")
        event_details = {
            "type": appraisal_info.get("type", "unknown"), # Retain original event type if available
            "intensity": appraisal_info.get("event_intensity", appraisal_info.get("intensity", 0.5)), # Check both keys
            "novelty": appraisal_info.get("event_novelty", appraisal_info.get("novelty", 0.0)),
            "expectedness": appraisal_info.get("expectedness", 1.0), # Default to expected if not specified
            "controllability": appraisal_info.get("controllability", 0.5) # Default to moderately controllable
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
        # print(f"ConcreteEmotionModule: express_emotion called. VAD: {self.current_emotion_state}")
        return {
            "vad_state": self.current_emotion_state.copy(),
            "intensity_conceptual": self.current_emotion_state['arousal'], # Using arousal as proxy
            "expression_modality_hints": ["vocal_tone_change_vad", "facial_expression_vad_based"] # Conceptual
        }

    def get_status(self) -> Dict[str, Any]:
        """Returns the current status of the Emotion Module."""
        return {
            "module_type": "ConcreteEmotionModule (Phase 1 Enhanced)",
            "current_vad_state": self.current_emotion_state.copy(),
            "personality_profile_active": self._personality_profile is not None,
            "reactivity_modifier_arousal": self._reactivity_modifier_arousal
            # Removed appraisal_log_count and categorical for Phase 1 focus
        }

    def regulate_emotion(self, strategy: str, target_emotion_details: Dict[str, Any]) -> bool:
        """Placeholder for emotion regulation. Not implemented in Phase 1."""
        print(f"ConcreteEmotionModule: regulate_emotion called (Placeholder). Strategy: {strategy}, Target: {target_emotion_details}")
        # Conceptual: Could try to shift VAD towards a target, e.g., reduce arousal.
        # Example: if strategy == "dampen_arousal": self.current_emotion_state["arousal"] *= 0.7
        # self._decay_emotions() # Apply decay after conceptual regulation
        return False # No actual regulation applied in this phase

    def get_emotional_influence_on_cognition(self) -> Dict[str, Any]:
        """
        Returns conceptual influences on cognition based on the VAD state.
        This is similar to get_simulated_physiological_effects for Phase 1.
        """
        # print(f"ConcreteEmotionModule: get_emotional_influence_on_cognition called.")
        return self.get_simulated_physiological_effects()

    def set_personality_profile(self, profile: Dict[str, Any]) -> None:
        """Sets a personality profile that might influence emotional responses and baseline VAD."""
        print(f"ConcreteEmotionModule: set_personality_profile called with {profile}.")
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

        print(f"ConcreteEmotionModule: VAD state potentially adjusted by personality: {self.current_emotion_state}")


if __name__ == '__main__':
    emotion_module = ConcreteEmotionModule()

    print("\n--- Initial Status ---")
    print(emotion_module.get_status())
    print("Initial VAD state:", emotion_module.get_emotional_state())

    print("\n--- Appraise Event: Positive Goal Achievement ---")
    event1 = {
        "type": "GOAL_PROGRESS", "intensity": 0.8, "novelty": 0.2, "expectedness": 0.9,
        "goal_congruence": 0.9, "goal_importance": 0.8, "controllability": 0.7
    }
    emotion_module.appraise_event(event1)
    # Expected: Valence increases, Arousal increases moderately, Dominance increases slightly.

    print("\n--- Appraise Event: Negative, Unexpected, Uncontrollable ---")
    event2 = {
        "type": "EXTERNAL_SENSOR", "intensity": 0.9, "novelty": 0.8, "expectedness": 0.1,
        "goal_congruence": -0.7, "goal_importance": 0.9, # Obstructs important goal
        "controllability": 0.1, "norm_alignment": -0.5 # Violates a norm
    }
    emotion_module.appraise_event(event2)
    # Expected: Valence decreases significantly, Arousal increases significantly, Dominance decreases.

    print("\n--- Appraise Event: Mildly Surprising, Neutral ---")
    event3 = {
        "type": "EXTERNAL_SENSOR", "intensity": 0.3, "novelty": 0.6, "expectedness": 0.5,
        # No goal_congruence, controllability, norm_alignment specified
    }
    emotion_module.appraise_event(event3)
    # Expected: Arousal increases mildly, Valence/Dominance minor changes.

    print("\n--- Several Decays (simulating time passing) ---")
    current_vad = emotion_module.get_emotional_state()
    print(f"VAD before extra decays: V:{current_vad['valence']:.2f} A:{current_vad['arousal']:.2f} D:{current_vad['dominance']:.2f}")
    for i in range(5):
        emotion_module._decay_emotions(decay_factor=0.8) # Stronger decay for test visibility
        # print(f"After decay {i+1}: {emotion_module.get_emotional_state()}")
    print("VAD after several decays:", emotion_module.get_emotional_state())

    print("\n--- Simulated Physiological Effects ---")
    # Manually set a state to test effects
    emotion_module.current_emotion_state = {"valence": -0.6, "arousal": 0.75, "dominance": -0.4}
    print(f"Manually set VAD to: {emotion_module.current_emotion_state}")
    effects = emotion_module.get_simulated_physiological_effects()
    print("Simulated effects:", effects)
    assert effects.get("attention_focus") == "narrowed"
    assert effects.get("cognitive_bias") == "threat_detection_priority"

    emotion_module.current_emotion_state = {"valence": 0.7, "arousal": 0.5, "dominance": 0.3}
    print(f"Manually set VAD to: {emotion_module.current_emotion_state}")
    effects_joy = emotion_module.get_simulated_physiological_effects()
    print("Simulated effects (joyful):", effects_joy)
    assert effects_joy.get("learning_rate_modifier_suggestion") == 1.2
    assert effects_joy.get("cognitive_bias") == "opportunity_seeking"


    print("\n--- Test Compatibility `update_emotional_state` (old method name) ---")
    emotion_module.current_emotion_state = {"valence": 0.0, "arousal": 0.0, "dominance": 0.0} # Reset
    compat_event = {"type": "goal_status", "goal_id": "g_compat", "goal_status": "achieved",
                    "event_intensity": 0.7, "goal_importance": 0.9}
    # This old method `update_emotional_state` will call the new `appraise_event`
    emotion_module.update_emotional_state(compat_event, event_source="compat_test_source")
    final_vad = emotion_module.get_emotional_state()
    print("VAD after compatibility call:", final_vad)
    # Check if valence increased significantly (0.9 congruence * 0.9 importance * 0.7 intensity approx 0.567)
    # This should be reflected in the final valence after decay.
    assert final_vad["valence"] > 0.3 # Allowing for decay from the initial positive impact

    print("\nExample Usage Complete (Phase 1 Enhanced Emotion Module).")
