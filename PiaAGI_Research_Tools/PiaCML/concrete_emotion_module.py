from typing import Any, Dict, List, Optional, Tuple

try:
    from .base_emotion_module import BaseEmotionModule
except ImportError:
    from base_emotion_module import BaseEmotionModule

class ConcreteEmotionModule(BaseEmotionModule):
    """
    A basic, concrete implementation of the BaseEmotionModule.
    This version uses a simplified appraisal mechanism based on event properties
    (e.g., goal status, unexpectedness) to update a dimensional emotional state
    (Valence, Arousal, Dominance - VAD) and map it to a categorical emotion label.
    """

    def __init__(self, initial_vad_state: Tuple[float, float, float] = (0.0, 0.0, 0.0)):
        # VAD state: Valence (-1 to 1), Arousal (0 to 1), Dominance (-1 to 1)
        self._vad_state: Dict[str, float] = {
            "valence": initial_vad_state[0], # Pleasure vs. Displeasure
            "arousal": initial_vad_state[1], # Activation level
            "dominance": initial_vad_state[2] # Sense of control
        }
        self._current_categorical_emotion: str = "neutral"
        self._appraisal_log: List[Dict[str, Any]] = []
        self._supported_categorical_emotions = ["neutral", "joy", "sadness", "anger", "fear", "surprise"] # Basic set
        self._personality_profile: Optional[Dict] = None
        self._last_regulation_attempt: Optional[Dict] = None
        self._reactivity_modifier_arousal: float = 1.0
        print("ConcreteEmotionModule initialized.")

    def _map_vad_to_categorical(self) -> str:
        """Very simple mapping from VAD to a categorical emotion label."""
        v, a, d = self._vad_state["valence"], self._vad_state["arousal"], self._vad_state["dominance"]

        # This is highly simplified. Real mappings are complex.
        if a < 0.2: return "neutral"
        if v > 0.5 and a > 0.5: return "joy" # High pleasure, high arousal
        if v < -0.5 and a > 0.5: # High displeasure, high arousal
            return "anger" if d > 0.3 else "fear" # Anger if feeling in control, else fear
        if v < -0.3 and a < 0.6: return "sadness" # Moderate displeasure, lower arousal
        if a > 0.7 and abs(v) < 0.3 : return "surprise" # High arousal, neutral valence (could be pos or neg surprise)

        return "neutral" # Default

    def update_emotional_state(self, appraisal_info: Dict[str, Any], event_source: Optional[str] = None) -> None:
        """
        Updates the VAD emotional state based on appraisal info.
        'appraisal_info' might contain:
        - 'type': e.g., "goal_status", "external_event", "internal_thought"
        - 'goal_id': (if type is "goal_status")
        - 'goal_status': e.g., "achieved", "failed", "progressing", "threatened"
        - 'event_novelty': float (0 to 1)
        - 'event_intensity': float (0 to 1)
        - 'expectedness': float (0 to 1, where 1 is fully expected)
        - 'controllability': float (0 to 1, perceived ability to influence)
        """
        appraisal_details = {"appraisal_info": appraisal_info, "event_source": event_source, "vad_before": self._vad_state.copy()}
        print(f"ConcreteEmotionModule: Updating emotional state: {appraisal_info}, Source: {event_source}")

        # Simplified appraisal rules:
        valence_change = 0.0
        raw_arousal_change = 0.0 # Store pre-modifier arousal change
        dominance_change = 0.0

        event_type = appraisal_info.get("type")
        intensity = appraisal_info.get("event_intensity", 0.5)
        novelty = appraisal_info.get("event_novelty", 0.3)
        expectedness = appraisal_info.get("expectedness", 0.8) # Default to somewhat expected
        controllability = appraisal_info.get("controllability", 0.5) # Default to somewhat controllable

        if event_type == "goal_status":
            goal_status = appraisal_info.get("goal_status")
            if goal_status == "achieved":
                valence_change = 0.5 * intensity
                raw_arousal_change = 0.3 * intensity
                dominance_change = 0.2 * intensity
            elif goal_status == "failed":
                valence_change = -0.6 * intensity
                raw_arousal_change = 0.4 * intensity
                dominance_change = -0.3 * intensity
            elif goal_status == "threatened":
                valence_change = -0.4 * intensity
                raw_arousal_change = 0.5 * intensity
                dominance_change = -0.2 * controllability # Less control -> less dominance

        elif event_type == "external_event":
            # Using event_source (previously context) to check for perceived_valence
            perceived_valence = "neutral"
            if isinstance(event_source, dict) and "perceived_valence" in event_source:
                perceived_valence = event_source["perceived_valence"]

            if novelty > 0.7 and intensity > 0.5: # Unexpected and intense
                raw_arousal_change = 0.6 * intensity
                if perceived_valence == "positive":
                     valence_change = 0.3 * intensity * novelty
                else: # Negative or neutral but still surprising
                     valence_change = -0.2 * intensity * novelty

        # Apply reactivity modifier to arousal change
        arousal_change = raw_arousal_change * self._reactivity_modifier_arousal

        # Apply changes (with clamping and some decay/return to baseline tendency)
        decay_factor = 0.7 # How much it returns to neutral each step if no strong input
        self._vad_state["valence"] = max(-1.0, min(1.0, self._vad_state["valence"] * decay_factor + valence_change))
        self._vad_state["arousal"] = max(0.0, min(1.0, self._vad_state["arousal"] * decay_factor + arousal_change))
        self._vad_state["dominance"] = max(-1.0, min(1.0, self._vad_state["dominance"] * decay_factor + dominance_change))

        self._current_categorical_emotion = self._map_vad_to_categorical()

        appraisal_details["vad_after"] = self._vad_state.copy()
        appraisal_details["new_categorical_emotion"] = self._current_categorical_emotion
        self._appraisal_log.append(appraisal_details)

        print(f"ConcreteEmotionModule: VAD updated to {self._vad_state}. Category: {self._current_categorical_emotion}")
        # Method now returns None

    def get_current_emotional_state(self) -> Dict[str, Any]:
        """Returns the current emotional state (both VAD and categorical)."""
        # This method matches 'get_current_emotional_state' from BaseEmotionModule ABC
        return {
            "vad_state": self._vad_state.copy(),
            "categorical_emotion": self._current_categorical_emotion
        }

    def express_emotion(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Returns a representation of the current emotional state for expression.
        In a more complex system, this might generate specific behavioral cues.
        Here, it just returns the internal state.
        """
        print(f"ConcreteEmotionModule: express_emotion called. Current state: {self._current_categorical_emotion}, VAD: {self._vad_state}")
        return {
            "emotion_to_express": self._current_categorical_emotion,
            "intensity_conceptual": self._vad_state['arousal'], # Use arousal as a proxy for intensity
            "valence": self._vad_state['valence'],
            "expression_modality_hints": ["vocal_tone_change", "textual_sentiment_modifier"] # Conceptual
        }

    def get_status(self) -> Dict[str, Any]:
        """Returns the current status of the Emotion Module."""
        # This method matches 'get_status' from BaseEmotionModule ABC
        return {
            "module_type": "ConcreteEmotionModule",
            "current_vad_state": self._vad_state.copy(),
            "current_categorical_emotion": self._current_categorical_emotion,
            "supported_categorical_emotions": list(self._supported_categorical_emotions),
            "appraisal_log_count": len(self._appraisal_log),
            "personality_profile": self._personality_profile,
            "last_regulation_attempt": self._last_regulation_attempt,
            "reactivity_modifier_arousal": self._reactivity_modifier_arousal
        }

    # --- New placeholder methods implementing BaseEmotionModule ABC ---
    # (Ensure these match the subtask spec exactly)

    def regulate_emotion(self, strategy: str, target_emotion_details: Dict) -> bool:
        print(f"ConcreteEmotionModule: regulate_emotion called with strategy '{strategy}' for {target_emotion_details}. Placeholder: No actual regulation applied.")
        self._last_regulation_attempt = {"strategy": strategy, "details": target_emotion_details} # Removed "status" field to match spec
        return False

    def get_emotional_influence_on_cognition(self) -> Dict:
        print(f"ConcreteEmotionModule: get_emotional_influence_on_cognition called. Placeholder: Returning influence map based on VAD.")
        influence = {}
        if self._vad_state["valence"] > 0.5 and self._vad_state["arousal"] > 0.5: # Joy
            influence['decision_making_style'] = 'more_optimistic'
            influence['learning_rate_modifier'] = 1.1 # Example
        elif self._vad_state["valence"] < -0.5 and self._vad_state["arousal"] > 0.5: # Fear/Anger
            influence['attention_bias'] = 'focus_on_potential_threats'
            influence['risk_aversion_factor'] = 1.5 # Example
        elif self._vad_state["arousal"] < 0.2: # Low arousal / neutral
            influence['cognitive_effort_level'] = 'baseline'
        # Removed print from here to match spec, was: print(f"ConcreteEmotionModule: Returning emotional influence: {influence}")
        return influence

    def set_personality_profile(self, profile: Dict) -> None:
        print(f"ConcreteEmotionModule: set_personality_profile called with {profile}. Storing profile.")
        self._personality_profile = profile
        if 'default_mood_valence' in profile and isinstance(profile['default_mood_valence'], (int, float)):
            # Adjust valence towards default mood, but don't completely override current state, maybe average?
            self._vad_state['valence'] = max(-1.0, min(1.0, (self._vad_state['valence'] + profile['default_mood_valence']) / 2.0))
        if 'reactivity_modifier_arousal' in profile and isinstance(profile['reactivity_modifier_arousal'], (int, float)):
            # Store this, it could be used by update_emotional_state to scale arousal changes
            self._reactivity_modifier_arousal = float(profile['reactivity_modifier_arousal'])
        self._current_categorical_emotion = self._map_vad_to_categorical()
        # Removed print from here to match spec, was: print(f"ConcreteEmotionModule: VAD valence adjusted by personality profile to {self._vad_state['valence']}. New categorical: {self._current_categorical_emotion}")
        # Removed else print from here to match spec

if __name__ == '__main__':
    emotion_module = ConcreteEmotionModule(initial_vad_state=(0.1, 0.1, 0.0)) # Start slightly positive

    # Initial Status
    print("\n--- Initial Status ---")
    print(emotion_module.get_status()) # Renamed
    print("Initial emotion:", emotion_module.get_current_emotional_state()) # Renamed


    # Update emotional state (goal achievement)
    print("\n--- Update Emotional State: Goal Achieved ---")
    event_goal_achieved = {"type": "goal_status", "goal_id": "g1", "goal_status": "achieved", "event_intensity": 0.8}
    emotion_module.update_emotional_state(event_goal_achieved, event_source="test_case")
    print("Emotion after goal achieved:", emotion_module.get_current_emotional_state()) # Renamed

    # Update emotional state (novel positive event)
    print("\n--- Update Emotional State: Novel Positive Event ---")
    event_surprise_good = {"type": "external_event", "description": "unexpected_gift", "event_intensity": 0.7, "event_novelty": 0.9}
    emotion_module.update_emotional_state(event_surprise_good, event_source={"perceived_valence": "positive"}) # Using dict for event_source example
    print("Emotion after good surprise:", emotion_module.get_current_emotional_state()) # Renamed

    # Update emotional state (goal failure)
    print("\n--- Update Emotional State: Goal Failed ---")
    emotion_module.update_emotional_state({"type": "external_event", "description": "routine_check", "event_intensity": 0.1, "event_novelty": 0.1, "expectedness": 0.9})
    print("Emotion after neutral event (decay):", emotion_module.get_current_emotional_state()) # Renamed

    event_goal_failed = {"type": "goal_status", "goal_id": "g2", "goal_status": "failed", "event_intensity": 0.9, "controllability": 0.2}
    emotion_module.update_emotional_state(event_goal_failed)
    print("Emotion after goal failed:", emotion_module.get_current_emotional_state()) # Renamed

    # Test new methods
    print("\n--- Test Regulate Emotion ---")
    regulation_success = emotion_module.regulate_emotion("mindfulness", {"target": "anger"})
    print(f"Regulation attempt success: {regulation_success}")
    print(f"Last regulation attempt in status: {emotion_module.get_status()['last_regulation_attempt']}") # Renamed

    print("\n--- Test Get Emotional Influence ---")
    influence = emotion_module.get_emotional_influence_on_cognition()
    print(f"Current emotional influence: {influence}")

    # Set VAD to trigger other branch in get_emotional_influence_on_cognition
    emotion_module._vad_state = {"valence": 0.6, "arousal": 0.6, "dominance": 0.5} # Joy-like
    emotion_module._current_categorical_emotion = emotion_module._map_vad_to_categorical()
    print(f"Manually set VAD to Joy-like: {emotion_module._vad_state}, Cat: {emotion_module._current_categorical_emotion}")
    influence_joy = emotion_module.get_emotional_influence_on_cognition()
    print(f"Emotional influence (Joy-like): {influence_joy}")


    print("\n--- Test Set Personality Profile ---")
    profile = {"name": "CautiousObserver", "default_mood_valence": -0.1, "base_arousal": 0.3}
    emotion_module.set_personality_profile(profile)
    print(f"Personality profile in status: {emotion_module.get_status()['personality_profile']}") # Renamed
    print(f"VAD after profile set: {emotion_module.get_current_emotional_state()['vad_state']}") # Renamed


    # Express emotion
    print("\n--- Express Emotion ---")
    expression_info = emotion_module.express_emotion()
    print("Expression info:", expression_info)

    # Final Status
    print("\n--- Final Status ---")
    print(emotion_module.get_status()) # Renamed
    # Appraisal log count will be different due to more calls to update_emotional_state
    # assert emotion_module.get_status()['appraisal_log_count'] == 4
    # Let's check it's greater than a few calls made
    assert emotion_module.get_status()['appraisal_log_count'] >= 5 # Renamed


    print("\nExample Usage Complete.")
