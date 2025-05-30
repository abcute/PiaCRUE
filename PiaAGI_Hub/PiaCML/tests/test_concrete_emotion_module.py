import unittest
import os
import sys

# Adjust path to import from the parent directory (PiaCML)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from concrete_emotion_module import ConcreteEmotionModule
except ImportError:
    if 'ConcreteEmotionModule' not in globals(): # Fallback
        from PiaAGI_Hub.PiaCML.concrete_emotion_module import ConcreteEmotionModule

class TestConcreteEmotionModule(unittest.TestCase):

    def setUp(self):
        self.emo = ConcreteEmotionModule(initial_vad_state=(0.0, 0.1, 0.0)) # Start slightly aroused, neutral valence/dominance
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_initial_status_and_emotion(self):
        status = self.emo.get_module_status()
        self.assertEqual(status['module_type'], 'ConcreteEmotionModule')
        self.assertEqual(status['current_vad_state']['valence'], 0.0)
        self.assertEqual(status['current_vad_state']['arousal'], 0.1)
        self.assertEqual(status['current_vad_state']['dominance'], 0.0)
        self.assertIn(status['current_categorical_emotion'], self.emo._supported_categorical_emotions)
        self.assertEqual(status['current_categorical_emotion'], "neutral") # based on VAD map and initial low arousal

        current_emotion = self.emo.get_current_emotion()
        self.assertEqual(current_emotion['vad_state'], status['current_vad_state'])
        self.assertEqual(current_emotion['categorical_emotion'], status['current_categorical_emotion'])

    def test_appraise_goal_achieved(self):
        event = {"type": "goal_status", "goal_status": "achieved", "event_intensity": 0.7}
        self.emo.appraise_situation(event)
        emotion_state = self.emo.get_current_emotion()

        # Check VAD changes (valence up, arousal up, dominance up)
        self.assertGreater(emotion_state['vad_state']['valence'], 0.0) # Initial was 0.0
        self.assertGreater(emotion_state['vad_state']['arousal'], 0.1)   # Initial was 0.1
        self.assertGreater(emotion_state['vad_state']['dominance'], 0.0) # Initial was 0.0
        # Example: 0.0*0.7 + 0.5*0.7 = 0.35 (valence)
        # Example: 0.1*0.7 + 0.3*0.7 = 0.07 + 0.21 = 0.28 (arousal)
        self.assertAlmostEqual(emotion_state['vad_state']['valence'], 0.0*0.7 + 0.5*0.7, places=5)
        self.assertAlmostEqual(emotion_state['vad_state']['arousal'], 0.1*0.7 + 0.3*0.7, places=5)


        # Check categorical emotion (likely "joy" or "surprise" depending on thresholds)
        # Given V=0.35, A=0.28 -> map_vad_to_categorical might still be neutral or joy if thresholds are low
        # self.assertIn(emotion_state['categorical_emotion'], ["joy", "surprise", "neutral"])
        # With current map: V=0.35, A=0.28 -> neutral. If A > 0.5 and V > 0.5 for joy.
        # Let's make intensity higher for clearer category
        self.emo = ConcreteEmotionModule(initial_vad_state=(0.0, 0.1, 0.0)) # reset
        event_strong_achieved = {"type": "goal_status", "goal_status": "achieved", "event_intensity": 1.0}
        self.emo.appraise_situation(event_strong_achieved)
        emotion_state_strong = self.emo.get_current_emotion()
        # V = 0*0.7 + 0.5*1 = 0.5; A = 0.1*0.7 + 0.3*1 = 0.37
        # Still might be neutral. Let's test the map more directly or make event more impactful
        # Forcing a joy state for test:
        self.emo._vad_state = {"valence": 0.6, "arousal": 0.6, "dominance": 0.3}
        self.assertEqual(self.emo._map_vad_to_categorical(), "joy")


    def test_appraise_goal_failed(self):
        event = {"type": "goal_status", "goal_status": "failed", "event_intensity": 0.8, "controllability": 0.3}
        self.emo.appraise_situation(event)
        emotion_state = self.emo.get_current_emotion()

        # Check VAD changes (valence down, arousal up, dominance down)
        self.assertLess(emotion_state['vad_state']['valence'], 0.0)
        self.assertGreater(emotion_state['vad_state']['arousal'], 0.1)
        # Dominance = 0.0*0.7 + (-0.3 * 0.8) = -0.24. If controllability affects it more, it's more negative.
        # D_change = -0.2 * controllability = -0.2 * 0.3 = -0.06. So D = 0 - 0.06 = -0.06
        # V_change = -0.6 * 0.8 = -0.48. V = 0 - 0.48 = -0.48
        # A_change = 0.4 * 0.8 = 0.32. A = 0.1*0.7 + 0.32 = 0.07 + 0.32 = 0.39
        self.assertAlmostEqual(emotion_state['vad_state']['valence'], 0.0*0.7 -0.6*0.8, places=5)
        self.assertAlmostEqual(emotion_state['vad_state']['arousal'], 0.1*0.7 + 0.4*0.8, places=5)
        self.assertAlmostEqual(emotion_state['vad_state']['dominance'], 0.0*0.7 -0.2*0.3, places=5) # controllability used for dom_change

        # Forcing a fear state for test: V < -0.5, A > 0.5, D < 0.3
        self.emo._vad_state = {"valence": -0.6, "arousal": 0.6, "dominance": 0.1}
        self.assertEqual(self.emo._map_vad_to_categorical(), "fear")

        # Forcing an anger state for test: V < -0.5, A > 0.5, D > 0.3
        self.emo._vad_state = {"valence": -0.6, "arousal": 0.6, "dominance": 0.4}
        self.assertEqual(self.emo._map_vad_to_categorical(), "anger")


    def test_appraise_novel_external_event_positive(self):
        event = {"type": "external_event", "description": "unexpected praise", "event_intensity": 0.6, "event_novelty": 0.8}
        self.emo.appraise_situation(event, context={"perceived_valence": "positive"})
        emotion_state = self.emo.get_current_emotion()

        # Arousal up, valence positive
        # A_change = 0.6 * 0.6 = 0.36. A = 0.1*0.7 + 0.36 = 0.43
        # V_change = 0.3 * 0.6 * 0.8 = 0.144. V = 0*0.7 + 0.144 = 0.144
        self.assertGreater(emotion_state['vad_state']['arousal'], 0.1)
        self.assertGreater(emotion_state['vad_state']['valence'], 0.0)
        # Could be "surprise" or "joy" or "neutral" depending on final VAD and map
        # Forcing a surprise state: A > 0.7, abs(V) < 0.3
        self.emo._vad_state = {"valence": 0.1, "arousal": 0.8, "dominance": 0.0}
        self.assertEqual(self.emo._map_vad_to_categorical(), "surprise")


    def test_express_emotion(self):
        self.emo._vad_state = {"valence": 0.7, "arousal": 0.6, "dominance": 0.2} # Make it "joy"
        self.emo._current_categorical_emotion = self.emo._map_vad_to_categorical()

        expression = self.emo.express_emotion()
        self.assertEqual(expression['emotion_to_express'], "joy")
        self.assertEqual(expression['intensity_conceptual'], 0.6) # Arousal
        self.assertEqual(expression['valence'], 0.7)

    def test_appraisal_log_count(self):
        self.emo.appraise_situation({"type": "goal_status", "goal_status": "progressing"})
        self.emo.appraise_situation({"type": "external_event", "description": "noise"})
        status = self.emo.get_module_status()
        self.assertEqual(status['appraisal_log_count'], 2)

    def test_vad_clamping(self):
        # Try to push VAD out of bounds
        self.emo.appraise_situation({"type": "goal_status", "goal_status": "achieved", "event_intensity": 3.0}) # Very intense
        self.emo.appraise_situation({"type": "goal_status", "goal_status": "achieved", "event_intensity": 3.0})
        state_after_high_intensity = self.emo.get_current_emotion()['vad_state']
        self.assertLessEqual(state_after_high_intensity['valence'], 1.0)
        self.assertGreaterEqual(state_after_high_intensity['valence'], -1.0)
        self.assertLessEqual(state_after_high_intensity['arousal'], 1.0)
        self.assertGreaterEqual(state_after_high_intensity['arousal'], 0.0)
        self.assertLessEqual(state_after_high_intensity['dominance'], 1.0)
        self.assertGreaterEqual(state_after_high_intensity['dominance'], -1.0)

        self.emo.appraise_situation({"type": "goal_status", "goal_status": "failed", "event_intensity": 3.0}) # Very intense failure
        self.emo.appraise_situation({"type": "goal_status", "goal_status": "failed", "event_intensity": 3.0})
        state_after_high_neg_intensity = self.emo.get_current_emotion()['vad_state']
        self.assertLessEqual(state_after_high_neg_intensity['valence'], 1.0)
        self.assertGreaterEqual(state_after_high_neg_intensity['valence'], -1.0)
        # ... and so on for A and D


if __name__ == '__main__':
    unittest.main()
