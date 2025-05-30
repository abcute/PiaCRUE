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

    def appraise_situation(self, event_info: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Appraises an event and updates the internal emotional state (VAD).
        'event_info' might contain:
        - 'type': e.g., "goal_status", "external_event", "internal_thought"
        - 'goal_id': (if type is "goal_status")
        - 'goal_status': e.g., "achieved", "failed", "progressing", "threatened"
        - 'event_novelty': float (0 to 1)
        - 'event_intensity': float (0 to 1)
        - 'expectedness': float (0 to 1, where 1 is fully expected)
        - 'controllability': float (0 to 1, perceived ability to influence)
        """
        appraisal_details = {"event_info": event_info, "context": context, "vad_before": self._vad_state.copy()}
        print(f"ConcreteEmotionModule: Appraising situation: {event_info}")

        # Simplified appraisal rules:
        valence_change = 0.0
        arousal_change = 0.0
        dominance_change = 0.0

        event_type = event_info.get("type")
        intensity = event_info.get("event_intensity", 0.5)
        novelty = event_info.get("event_novelty", 0.3)
        expectedness = event_info.get("expectedness", 0.8) # Default to somewhat expected
        controllability = event_info.get("controllability", 0.5) # Default to somewhat controllable

        if event_type == "goal_status":
            goal_status = event_info.get("goal_status")
            if goal_status == "achieved":
                valence_change = 0.5 * intensity
                arousal_change = 0.3 * intensity
                dominance_change = 0.2 * intensity
            elif goal_status == "failed":
                valence_change = -0.6 * intensity
                arousal_change = 0.4 * intensity
                dominance_change = -0.3 * intensity
            elif goal_status == "threatened":
                valence_change = -0.4 * intensity
                arousal_change = 0.5 * intensity
                dominance_change = -0.2 * controllability # Less control -> less dominance

        elif event_type == "external_event":
            if novelty > 0.7 and intensity > 0.5: # Unexpected and intense
                arousal_change = 0.6 * intensity
                if not context or context.get("perceived_valence", "neutral") == "positive":
                     valence_change = 0.3 * intensity * novelty
                else: # Negative or neutral but still surprising
                     valence_change = -0.2 * intensity * novelty


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
        return {"new_vad_state": self._vad_state.copy(), "categorical_emotion": self._current_categorical_emotion}

    def get_current_emotion(self) -> Dict[str, Any]:
        """Returns the current emotional state (both VAD and categorical)."""
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

    def get_module_status(self) -> Dict[str, Any]:
        """Returns the current status of the Emotion Module."""
        return {
            "module_type": "ConcreteEmotionModule",
            "current_vad_state": self._vad_state.copy(),
            "current_categorical_emotion": self._current_categorical_emotion,
            "supported_categorical_emotions": list(self._supported_categorical_emotions),
            "appraisal_log_count": len(self._appraisal_log)
        }

if __name__ == '__main__':
    emotion_module = ConcreteEmotionModule(initial_vad_state=(0.1, 0.1, 0.0)) # Start slightly positive

    # Initial Status
    print("\n--- Initial Status ---")
    print(emotion_module.get_module_status())
    print("Initial emotion:", emotion_module.get_current_emotion())


    # Appraise goal achievement
    print("\n--- Appraise Goal Achieved ---")
    event_goal_achieved = {"type": "goal_status", "goal_id": "g1", "goal_status": "achieved", "event_intensity": 0.8}
    emotion_module.appraise_situation(event_goal_achieved)
    print("Emotion after goal achieved:", emotion_module.get_current_emotion())
    # Expected: VAD shifts positive, arousal up -> "joy"

    # Appraise external novel event (positive context)
    print("\n--- Appraise Novel Positive Event ---")
    event_surprise_good = {"type": "external_event", "description": "unexpected_gift", "event_intensity": 0.7, "event_novelty": 0.9}
    emotion_module.appraise_situation(event_surprise_good, context={"perceived_valence": "positive"})
    print("Emotion after good surprise:", emotion_module.get_current_emotion())
    # Expected: Arousal up, valence positive -> "surprise" or "joy"

    # Appraise goal failure
    print("\n--- Appraise Goal Failed ---")
    # Let VAD decay a bit first by appraising a neutral, expected event
    emotion_module.appraise_situation({"type": "external_event", "description": "routine_check", "event_intensity": 0.1, "event_novelty": 0.1, "expectedness": 0.9})
    print("Emotion after neutral event (decay):", emotion_module.get_current_emotion())

    event_goal_failed = {"type": "goal_status", "goal_id": "g2", "goal_status": "failed", "event_intensity": 0.9, "controllability": 0.2}
    emotion_module.appraise_situation(event_goal_failed)
    print("Emotion after goal failed:", emotion_module.get_current_emotion())
    # Expected: VAD shifts negative, arousal up, dominance potentially down -> "sadness", "anger", or "fear"

    # Express emotion
    print("\n--- Express Emotion ---")
    expression_info = emotion_module.express_emotion()
    print("Expression info:", expression_info)

    # Final Status
    print("\n--- Final Status ---")
    print(emotion_module.get_module_status())
    assert emotion_module.get_module_status()['appraisal_log_count'] == 4


    print("\nExample Usage Complete.")
