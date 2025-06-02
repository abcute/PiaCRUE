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
        status = self.emo.get_status() # Renamed
        self.assertEqual(status['module_type'], 'ConcreteEmotionModule')
        self.assertEqual(status['current_vad_state']['valence'], 0.0)
        self.assertEqual(status['current_vad_state']['arousal'], 0.1)
        self.assertEqual(status['current_vad_state']['dominance'], 0.0)
        self.assertIn(status['current_categorical_emotion'], self.emo._supported_categorical_emotions)
        self.assertEqual(status['current_categorical_emotion'], "neutral") # based on VAD map and initial low arousal

        current_emotion = self.emo.get_current_emotional_state() # Renamed
        self.assertEqual(current_emotion['vad_state'], status['current_vad_state'])
        self.assertEqual(current_emotion['categorical_emotion'], status['current_categorical_emotion'])
        self.assertIsNone(status.get('personality_profile'))
        self.assertIsNone(status.get('last_regulation_attempt'))
        self.assertEqual(status.get('reactivity_modifier_arousal'), 1.0) # Default value

    def test_update_emotional_state_goal_achieved(self): # Renamed
        event = {"type": "goal_status", "goal_status": "achieved", "event_intensity": 0.7}
        return_value = self.emo.update_emotional_state(event) # Renamed, check return
        self.assertIsNone(return_value) # update_emotional_state should return None
        emotion_state = self.emo.get_current_emotional_state() # Renamed

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
        self.emo.update_emotional_state(event_strong_achieved) # Renamed this call
        emotion_state_strong = self.emo.get_current_emotional_state() # Renamed
        # V = 0*0.7 + 0.5*1 = 0.5; A = (0.1*0.7 + 0.3*1) * 1.0 (default reactivity) = 0.37
        # Calculations for VAD need to be precise based on the implementation (decay, then add)
        # Initial VAD: (0.0, 0.1, 0.0)
        # Valence change part: 0.5 * 1.0 = 0.5. New valence = 0.0 * 0.7 + 0.5 = 0.5
        # Raw Arousal change part: 0.3 * 1.0 = 0.3. New arousal = 0.1 * 0.7 + 0.3 * 1.0 = 0.07 + 0.3 = 0.37
        self.assertAlmostEqual(emotion_state_strong['vad_state']['valence'], 0.5)
        self.assertAlmostEqual(emotion_state_strong['vad_state']['arousal'], 0.37)
        # Still might be neutral. Let's test the map more directly or make event more impactful
        # Forcing a joy state for test:
        self.emo._vad_state = {"valence": 0.6, "arousal": 0.6, "dominance": 0.3}
        self.assertEqual(self.emo._map_vad_to_categorical(), "joy")


    def test_update_emotional_state_goal_failed(self): # Renamed
        event = {"type": "goal_status", "goal_status": "failed", "event_intensity": 0.8, "controllability": 0.3}
        self.emo.update_emotional_state(event) # Renamed
        emotion_state = self.emo.get_current_emotional_state() # Renamed

        # Check VAD changes (valence down, arousal up, dominance down)
        self.assertLess(emotion_state['vad_state']['valence'], 0.0)
        self.assertGreater(emotion_state['vad_state']['arousal'], 0.1)
        # Dominance = 0.0*0.7 + (-0.3 * 0.8) = -0.24. If controllability affects it more, it's more negative.
        # D_change = -0.2 * controllability = -0.2 * 0.3 = -0.06. So D = 0 - 0.06 = -0.06
        # V_change = -0.6 * 0.8 = -0.48. V = 0 - 0.48 = -0.48
        # A_change = 0.4 * 0.8 = 0.32. A = 0.1*0.7 + 0.32 = 0.07 + 0.32 = 0.39
        self.assertAlmostEqual(emotion_state['vad_state']['valence'], 0.0*0.7 -0.6*0.8, places=5)
        self.assertAlmostEqual(emotion_state['vad_state']['arousal'], 0.1*0.7 + (0.4*0.8) * 1.0, places=5) # Added reactivity_modifier_arousal (default 1.0)
        # Dominance for "failed" goal: initial_D * decay + (-0.3 * intensity)
        self.assertAlmostEqual(emotion_state['vad_state']['dominance'], 0.0*0.7 - 0.3*0.8, places=5)

        # Forcing a fear state for test: V < -0.5, A > 0.5, D < 0.3
        self.emo._vad_state = {"valence": -0.6, "arousal": 0.6, "dominance": 0.1}
        self.assertEqual(self.emo._map_vad_to_categorical(), "fear")

        # Forcing an anger state for test: V < -0.5, A > 0.5, D > 0.3
        self.emo._vad_state = {"valence": -0.6, "arousal": 0.6, "dominance": 0.4}
        self.assertEqual(self.emo._map_vad_to_categorical(), "anger")


    def test_update_emotional_state_novel_external_event_positive(self): # Renamed
        event = {"type": "external_event", "description": "unexpected praise", "event_intensity": 0.6, "event_novelty": 0.8}
        # context becomes event_source
        self.emo.update_emotional_state(event, event_source={"perceived_valence": "positive"}) # Renamed
        emotion_state = self.emo.get_current_emotional_state() # Renamed

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

    def test_appraisal_log_count(self): # Name implies old method, but logic relies on internal list updated by new method
        self.emo.update_emotional_state({"type": "goal_status", "goal_status": "progressing"})
        self.emo.update_emotional_state({"type": "external_event", "description": "noise"})
        status = self.emo.get_status() # Renamed
        self.assertEqual(status['appraisal_log_count'], 2)

    def test_vad_clamping(self):
        # Try to push VAD out of bounds
        self.emo.update_emotional_state({"type": "goal_status", "goal_status": "achieved", "event_intensity": 3.0}) # Very intense
        self.emo.update_emotional_state({"type": "goal_status", "goal_status": "achieved", "event_intensity": 3.0})
        state_after_high_intensity = self.emo.get_current_emotional_state()['vad_state'] # Renamed
        self.assertLessEqual(state_after_high_intensity['valence'], 1.0)
        self.assertGreaterEqual(state_after_high_intensity['valence'], -1.0)
        self.assertLessEqual(state_after_high_intensity['arousal'], 1.0)
        self.assertGreaterEqual(state_after_high_intensity['arousal'], 0.0) # Arousal is clamped at 0 min
        self.assertLessEqual(state_after_high_intensity['dominance'], 1.0)
        self.assertGreaterEqual(state_after_high_intensity['dominance'], -1.0)

        self.emo.update_emotional_state({"type": "goal_status", "goal_status": "failed", "event_intensity": 3.0}) # Very intense failure
        self.emo.update_emotional_state({"type": "goal_status", "goal_status": "failed", "event_intensity": 3.0})
        state_after_high_neg_intensity = self.emo.get_current_emotional_state()['vad_state'] # Renamed
        self.assertLessEqual(state_after_high_neg_intensity['valence'], 1.0)
        self.assertGreaterEqual(state_after_high_neg_intensity['valence'], -1.0)
        # ... and so on for A and D

    # --- New tests for placeholder methods ---

    def test_regulate_emotion_placeholder(self):
        strategy = "reappraisal"
        details = {"target_emotion": "anger", "goal": "reduce_intensity"}
        return_value = self.emo.regulate_emotion(strategy, details)
        self.assertFalse(return_value) # Placeholder returns False

        status = self.emo.get_status() # Renamed
        self.assertIsNotNone(status['last_regulation_attempt'])
        self.assertEqual(status['last_regulation_attempt']['strategy'], strategy)
        self.assertEqual(status['last_regulation_attempt']['details'], details)
        # self.assertEqual(status['last_regulation_attempt']['status'], "attempted_placeholder") # Status key removed from module

    def test_get_emotional_influence_on_cognition_placeholder(self):
        # Test initial (likely neutral or low arousal) state
        # Initial VAD: (0.0, 0.1, 0.0) -> arousal < 0.2
        initial_influence = self.emo.get_emotional_influence_on_cognition()
        self.assertEqual(initial_influence.get('cognitive_effort_level'), 'baseline')
        self.assertEqual(len(initial_influence), 1)


        # Test Joy-like state
        self.emo._vad_state = {"valence": 0.7, "arousal": 0.7, "dominance": 0.3}
        self.emo._current_categorical_emotion = self.emo._map_vad_to_categorical()
        joy_influence = self.emo.get_emotional_influence_on_cognition()
        self.assertEqual(joy_influence.get('decision_making_style'), 'more_optimistic')
        self.assertEqual(joy_influence.get('learning_rate_modifier'), 1.1)

        # Test Fear/Anger-like state
        self.emo._vad_state = {"valence": -0.6, "arousal": 0.8, "dominance": -0.4}
        self.emo._current_categorical_emotion = self.emo._map_vad_to_categorical()
        fear_influence = self.emo.get_emotional_influence_on_cognition()
        self.assertEqual(fear_influence.get('attention_bias'), 'focus_on_potential_threats')
        self.assertEqual(fear_influence.get('risk_aversion_factor'), 1.5)

        # Test another low arousal state to ensure it hits the baseline condition
        self.emo._vad_state = {"valence": 0.8, "arousal": 0.15, "dominance": 0.0} # Low arousal, positive valence
        self.emo._current_categorical_emotion = self.emo._map_vad_to_categorical()
        low_arousal_positive_influence = self.emo.get_emotional_influence_on_cognition()
        self.assertEqual(low_arousal_positive_influence.get('cognitive_effort_level'), 'baseline')


    def test_set_personality_profile_placeholder(self):
        initial_vad = self.emo.get_current_emotional_state()['vad_state'].copy() # Renamed & val=0.0, aro=0.1, dom=0.0
        initial_reactivity = self.emo.get_status()['reactivity_modifier_arousal'] # Renamed & Should be 1.0

        # Profile 1: Adjusts valence and reactivity
        profile1 = {
            "name": "TestProfile1",
            "default_mood_valence": 0.5,
            "reactivity_modifier_arousal": 1.5
        }
        self.emo.set_personality_profile(profile1)
        status1 = self.emo.get_status() # Renamed
        self.assertEqual(status1['personality_profile'], profile1)

        # Check valence update: (initial_valence + profile_valence) / 2 = (0.0 + 0.5) / 2 = 0.25
        vad_after_profile1 = self.emo.get_current_emotional_state()['vad_state'] # Renamed
        self.assertAlmostEqual(vad_after_profile1['valence'], 0.25, places=5)
        self.assertEqual(status1['reactivity_modifier_arousal'], 1.5)

        # Test reactivity modifier effect
        # Initial arousal: 0.1 (from setUp). After profile1 set, valence is 0.25, arousal still 0.1
        # Event that would cause raw_arousal_change of 0.4
        event_for_arousal = {"type": "goal_status", "goal_status": "threatened", "event_intensity": 0.8} # raw_arousal_change = 0.5 * 0.8 = 0.4
        # Expected arousal = current_arousal * decay + raw_arousal_change * reactivity_modifier
        # current_arousal for this event is vad_after_profile1['arousal'] which is still initial_vad['arousal'] (0.1) as set_personality_profile doesn't change arousal directly
        # arousal = 0.1 * 0.7 + 0.4 * 1.5 = 0.07 + 0.6 = 0.67
        self.emo.update_emotional_state(event_for_arousal)
        vad_after_event_with_profile1 = self.emo.get_current_emotional_state()['vad_state'] # Renamed
        self.assertAlmostEqual(vad_after_event_with_profile1['arousal'], 0.1 * 0.7 + (0.5 * 0.8) * 1.5, places=5)


        # Profile 2: No valence adjustment, different reactivity
        self.emo = ConcreteEmotionModule(initial_vad_state=(0.0, 0.1, 0.0)) # Reset for clean test
        profile2 = {"name": "TestProfile2", "reactivity_modifier_arousal": 0.5}
        self.emo.set_personality_profile(profile2)
        status2 = self.emo.get_status() # Renamed
        self.assertEqual(status2['personality_profile'], profile2)
        self.assertAlmostEqual(self.emo.get_current_emotional_state()['vad_state']['valence'], initial_vad['valence'], places=5) # Renamed & Valence unchanged
        self.assertEqual(status2['reactivity_modifier_arousal'], 0.5)

        # Test reactivity modifier effect (0.5)
        # arousal = 0.1 * 0.7 + 0.4 * 0.5 = 0.07 + 0.2 = 0.27
        self.emo.update_emotional_state(event_for_arousal) # Same event
        vad_after_event_with_profile2 = self.emo.get_current_emotional_state()['vad_state'] # Renamed
        self.assertAlmostEqual(vad_after_event_with_profile2['arousal'], 0.1 * 0.7 + (0.5 * 0.8) * 0.5, places=5)

        # Profile 3: Only default mood, reactivity should remain from profile2 (or be default if reset)
        # Let's reset to ensure we test default reactivity if not set by profile
        self.emo = ConcreteEmotionModule(initial_vad_state=(0.0, 0.1, 0.0)) # Reset
        self.assertEqual(self.emo.get_status()['reactivity_modifier_arousal'], 1.0) # Renamed & Check default

        profile3 = {"name": "TestProfile3", "default_mood_valence": -0.3}
        self.emo.set_personality_profile(profile3)
        status3 = self.emo.get_status() # Renamed
        self.assertEqual(status3['personality_profile'], profile3)
        self.assertAlmostEqual(self.emo.get_current_emotional_state()['vad_state']['valence'], (initial_vad['valence'] - 0.3) / 2.0, places=5) # Renamed
        self.assertEqual(status3['reactivity_modifier_arousal'], 1.0) # Should remain default 1.0

        # Test with default reactivity (1.0)
        # arousal = 0.1 * 0.7 + 0.4 * 1.0 = 0.07 + 0.4 = 0.47
        self.emo.update_emotional_state(event_for_arousal) # Same event
        vad_after_event_with_profile3 = self.emo.get_current_emotional_state()['vad_state'] # Renamed
        # Note: The valence for this event is -0.4 * 0.8 = -0.32.
        # Initial valence after profile3: (0.0 - 0.3)/2 = -0.15
        # Valence after event: -0.15 * 0.7 + (-0.4 * 0.8) = -0.105 - 0.32 = -0.425
        self.assertAlmostEqual(vad_after_event_with_profile3['valence'], -0.15 * 0.7 + (-0.4*0.8), places=5)
        self.assertAlmostEqual(vad_after_event_with_profile3['arousal'], 0.1 * 0.7 + (0.5 * 0.8) * 1.0, places=5)


if __name__ == '__main__':
    unittest.main()
