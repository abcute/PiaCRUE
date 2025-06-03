import unittest
import time # Required for a more precise delta in time-based assertions if any
import os
import sys

# Adjust path for consistent imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    from PiaAGI_Research_Tools.PiaCML.concrete_emotion_module import ConcreteEmotionModule
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from concrete_emotion_module import ConcreteEmotionModule

class TestConcreteEmotionModule(unittest.TestCase):

    def setUp(self):
        self.emo_module = ConcreteEmotionModule()
        self._original_stdout = sys.stdout
        # Suppress prints from the module during tests for cleaner output
        # sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        """Restore stdout after each test."""
        # sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_initialization(self):
        """Test the initial VAD values."""
        initial_state = self.emo_module.get_emotional_state()
        self.assertEqual(initial_state["valence"], 0.0)
        self.assertEqual(initial_state["arousal"], 0.0)
        self.assertEqual(initial_state["dominance"], 0.0)
        status = self.emo_module.get_status()
        self.assertEqual(status["current_vad_state"]["valence"], 0.0)


    def test_clamp_value(self):
        """Test the _clamp_value helper method."""
        self.assertEqual(self.emo_module._clamp_value(0.5, -1.0, 1.0), 0.5)
        self.assertEqual(self.emo_module._clamp_value(1.5, -1.0, 1.0), 1.0)
        self.assertEqual(self.emo_module._clamp_value(-1.5, -1.0, 1.0), -1.0)
        self.assertEqual(self.emo_module._clamp_value(0.0, -0.5, 0.5), 0.0)
        self.assertEqual(self.emo_module._clamp_value(1.0, 0.0, 0.8), 0.8) # Test different min/max

    def test_decay_emotions(self):
        """Test the _decay_emotions method."""
        self.emo_module.current_emotion_state = {"valence": 0.8, "arousal": 0.7, "dominance": -0.6}
        self.emo_module._decay_emotions(decay_factor=0.9) # Decay by 10%

        self.assertAlmostEqual(self.emo_module.current_emotion_state["valence"], 0.8 * 0.9)
        self.assertAlmostEqual(self.emo_module.current_emotion_state["arousal"], 0.7 * 0.9)
        self.assertAlmostEqual(self.emo_module.current_emotion_state["dominance"], -0.6 * 0.9)

        # Test decay towards zero doesn't overshoot
        self.emo_module.current_emotion_state = {"valence": 0.01, "arousal": 0.01, "dominance": -0.01}
        self.emo_module._decay_emotions(decay_factor=0.5)
        self.assertAlmostEqual(self.emo_module.current_emotion_state["valence"], 0.005)
        self.assertAlmostEqual(self.emo_module.current_emotion_state["arousal"], 0.005)
        self.assertAlmostEqual(self.emo_module.current_emotion_state["dominance"], -0.005)

        # Test arousal clamping at 0
        self.emo_module.current_emotion_state = {"valence": 0.0, "arousal": -0.5, "dominance": 0.0} # Invalid arousal
        self.emo_module._decay_emotions(decay_factor=0.9) # Should be clamped by _clamp_value called within _decay if not already
        # Note: _decay_emotions itself calls _clamp_value for V and D, and specific for Arousal.
        # If arousal was -0.5, arousal * 0.9 = -0.45. Clamped to 0.0.
        self.assertEqual(self.emo_module.current_emotion_state["arousal"], 0.0)


    def test_appraise_event_positive_goal(self):
        """Test appraise_event with a positive goal event."""
        event = {
            "type": "GOAL_PROGRESS", "intensity": 0.7, "novelty": 0.1, "expectedness": 0.8,
            "goal_congruence": 0.9, "goal_importance": 0.8, "controllability": 0.6
        }
        self.emo_module.appraise_event(event)
        state = self.emo_module.get_emotional_state()
        # Expected changes:
        # Valence: initial(0) + (0.9 * 0.8 * 0.7)  (then decay)
        # Arousal: initial(0) + (0.7*0.5 + (1-0.8)*0.5*0.7 + 0.1*0.3*0.7 + abs(0.9)*0.8*0.7*0.5) (then decay)
        # Dominance: initial(0) + (0.6-0.5)*0.5*0.7 (then decay)
        self.assertGreater(state["valence"], 0.0) # Should be positive
        self.assertGreater(state["arousal"], 0.0) # Should be aroused
        self.assertGreater(state["dominance"], 0.0) # Should be slightly dominant

    def test_appraise_event_negative_goal_unexpected(self):
        """Test appraise_event with a negative, unexpected goal event."""
        event = {
            "type": "GOAL_OBSTRUCTION", "intensity": 0.8, "novelty": 0.7, "expectedness": 0.2,
            "goal_congruence": -0.8, "goal_importance": 0.9, "controllability": 0.3,
            "norm_alignment": -0.4
        }
        self.emo_module.appraise_event(event)
        state = self.emo_module.get_emotional_state()
        # Expected changes:
        # Valence: initial(0) + (-0.8 * 0.9 * 0.8) + (-0.4 * 0.3 * 0.8) (then decay)
        # Arousal: initial(0) + (0.8*0.5 + (1-0.2)*0.5*0.8 + 0.7*0.3*0.8 + abs(-0.8)*0.9*0.8*0.5) (then decay)
        # Dominance: initial(0) + (0.3-0.5)*0.5*0.8 (then decay)
        self.assertLess(state["valence"], 0.0)      # Should be negative
        self.assertGreater(state["arousal"], 0.3)   # Should be significantly aroused
        self.assertLess(state["dominance"], 0.0)    # Should be submissive

    def test_appraise_event_clamping(self):
        """Test that VAD values are clamped after appraisal."""
        # Event designed to push valence and arousal very high, dominance very low
        event = {
            "type": "EXTREME_EVENT", "intensity": 2.0, # Higher than 1 for test
            "novelty": 1.0, "expectedness": 0.0,
            "goal_congruence": 1.0, "goal_importance": 1.0, "controllability": 0.0
        }
        # Call multiple times to accumulate effect before decay fully neutralizes
        for _ in range(5):
            self.emo_module.appraise_event(event)

        state = self.emo_module.get_emotional_state()
        self.assertLessEqual(state["valence"], 1.0)
        self.assertGreaterEqual(state["valence"], -1.0)
        self.assertLessEqual(state["arousal"], 1.0)
        self.assertGreaterEqual(state["arousal"], 0.0) # Arousal min is 0
        self.assertLessEqual(state["dominance"], 1.0)
        self.assertGreaterEqual(state["dominance"], -1.0)

    def test_get_simulated_physiological_effects(self):
        """Test the simulated physiological effects based on VAD state."""
        # High arousal, negative valence (e.g., fear/stress)
        self.emo_module.current_emotion_state = {"valence": -0.7, "arousal": 0.8, "dominance": -0.5}
        effects = self.emo_module.get_simulated_physiological_effects()
        self.assertEqual(effects.get("attention_focus"), "narrowed")
        self.assertEqual(effects.get("cognitive_bias"), "threat_detection_priority")
        self.assertEqual(effects.get("learning_rate_modifier_suggestion"), 0.8)

        # High arousal, positive valence (e.g., excitement/joy)
        self.emo_module.current_emotion_state = {"valence": 0.8, "arousal": 0.75, "dominance": 0.6}
        effects = self.emo_module.get_simulated_physiological_effects()
        self.assertEqual(effects.get("attention_focus"), "narrowed") # Still narrowed due to high arousal
        self.assertEqual(effects.get("cognitive_bias"), "opportunity_seeking")
        self.assertEqual(effects.get("learning_rate_modifier_suggestion"), 1.2)

        # Low arousal (e.g., sadness or calmness)
        self.emo_module.current_emotion_state = {"valence": 0.2, "arousal": 0.1, "dominance": 0.0}
        effects = self.emo_module.get_simulated_physiological_effects()
        self.assertEqual(effects.get("attention_focus"), "broad")
        self.assertIsNone(effects.get("cognitive_bias")) # No strong bias
        self.assertEqual(effects.get("learning_rate_modifier_suggestion"), 1.0) # Neutral learning rate

    def test_compatibility_update_emotional_state(self):
        """Test the old update_emotional_state method for compatibility."""
        self.emo_module.current_emotion_state = {"valence": 0.0, "arousal": 0.0, "dominance": 0.0}
        # Old style appraisal_info
        appraisal_info = {"type": "goal_status", "goal_status": "achieved", "event_intensity": 0.9, "goal_importance": 0.7}
        self.emo_module.update_emotional_state(appraisal_info, event_source="test_compat")

        state = self.emo_module.get_emotional_state()
        # Check if it had an effect (valence should increase due to goal_achieved)
        # Expected valence change before decay: 1.0 (congruence) * 0.7 (importance) * 0.9 (intensity) = 0.63
        self.assertGreater(state["valence"], 0.3) # Allowing for some decay
        self.assertGreater(state["arousal"], 0.1)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
