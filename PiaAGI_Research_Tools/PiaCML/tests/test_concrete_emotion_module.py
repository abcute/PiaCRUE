import unittest
import asyncio
import uuid
from typing import List, Any, Dict
from datetime import datetime, timezone # For GoalUpdatePayload source_timestamp

# Adjust path for consistent imports
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    from PiaAGI_Research_Tools.PiaCML.message_bus import MessageBus
    from PiaAGI_Research_Tools.PiaCML.core_messages import (
        GenericMessage, GoalUpdatePayload, EmotionalStateChangePayload,
        PerceptDataPayload, ActionEventPayload # Added PerceptDataPayload and ActionEventPayload
    )
    from PiaAGI_Research_Tools.PiaCML.concrete_emotion_module import ConcreteEmotionModule
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from message_bus import MessageBus
    from core_messages import (
        GenericMessage, GoalUpdatePayload, EmotionalStateChangePayload,
        PerceptDataPayload, ActionEventPayload # Added PerceptDataPayload and ActionEventPayload
    )
    from concrete_emotion_module import ConcreteEmotionModule

class TestConcreteEmotionModuleIntegration(unittest.TestCase):

    def setUp(self):
        self.bus = MessageBus()
        self.module_id = f"TestEmotionModule_{str(uuid.uuid4())[:8]}"
        self.emotion_module = ConcreteEmotionModule(message_bus=self.bus, module_id=self.module_id) # Instantiated here
        self.received_emotional_state_changes: List[GenericMessage] = []
        # Subscribe the listener in setUp to make it active for all tests in this class
        self.bus.subscribe(self.module_id, "EmotionalStateChange", self._emotional_state_change_listener)


    def _emotional_state_change_listener(self, message: GenericMessage):
        if isinstance(message.payload, EmotionalStateChangePayload):
            self.received_emotional_state_changes.append(message)

    def tearDown(self):
        self.received_emotional_state_changes.clear()

    # --- Test Publishing EmotionalStateChange ---
    def test_appraise_event_publishes_emotional_state_change(self):
        # emotion_module = ConcreteEmotionModule(message_bus=self.bus, module_id=self.module_id) # Use self.emotion_module
        async def run_test_logic():
            # self.bus.subscribe(self.module_id, "EmotionalStateChange", self._emotional_state_change_listener) # Moved to setUp

            event_details_1 = {
                "type": "TEST_EVENT_POSITIVE", "intensity": 0.7, "goal_congruence": 0.8,
                "goal_importance": 0.9, "triggering_message_id": "trigger_msg_001"
            }
            self.emotion_module.appraise_event(event_details_1)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_emotional_state_changes), 1)
            msg1: GenericMessage = self.received_emotional_state_changes[0]
            self.assertEqual(msg1.source_module_id, self.module_id)
            self.assertEqual(msg1.message_type, "EmotionalStateChange")

            payload1: EmotionalStateChangePayload = msg1.payload
            self.assertIsInstance(payload1, EmotionalStateChangePayload)
            self.assertTrue(payload1.current_emotion_profile["valence"] > 0) # Positive event
            self.assertEqual(payload1.intensity, payload1.current_emotion_profile["arousal"])
            self.assertEqual(payload1.triggering_event_id, "trigger_msg_001")
            self.assertIsInstance(payload1.primary_emotion, str) # Check that a discrete emotion label is set
            self.assertTrue(len(payload1.primary_emotion) > 0) # Ensure it's not an empty string

            self.received_emotional_state_changes.clear()

            # Test without triggering_message_id
            event_details_2 = {"type": "TEST_EVENT_NEGATIVE", "intensity": 0.6, "goal_congruence": -0.7, "goal_importance": 0.5}
            self.emotion_module.appraise_event(event_details_2)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_emotional_state_changes), 1)
            payload2: EmotionalStateChangePayload = self.received_emotional_state_changes[0].payload
            self.assertTrue(payload2.current_emotion_profile["valence"] < 0) # Negative event
            self.assertIsNone(payload2.triggering_event_id)
            self.assertIsInstance(payload2.primary_emotion, str)
            self.assertTrue(len(payload2.primary_emotion) > 0)
            self.assertEqual(payload2.intensity, payload2.current_emotion_profile["arousal"])

        asyncio.run(run_test_logic())

    def test_appraise_event_runs_without_bus(self):
        emotion_module_no_bus = ConcreteEmotionModule(message_bus=None, module_id="NoBusEmotionMod")
        initial_state = emotion_module_no_bus.get_emotional_state().copy()
        try:
            event_details = {"type": "TEST_NO_BUS", "intensity": 0.5, "goal_congruence": 0.5, "goal_importance": 0.5}
            emotion_module_no_bus.appraise_event(event_details)
        except Exception as e:
            self.fail(f"appraise_event raised an exception with no bus: {e}")

        # Check that state changed but no messages were "received" (listener is on self.bus)
        self.assertNotEqual(emotion_module_no_bus.get_emotional_state(), initial_state)
        # self.received_emotional_state_changes is part of self, not emotion_module_no_bus's context
        # This test is more about ensuring no error, rather than checking a listener on a different bus.
        # To properly test no publish, one might inject a mock bus into emotion_module_no_bus and check no calls.


    # --- Test Subscribing to GoalUpdate ---
    def test_handle_goal_update_for_appraisal_triggers_appraisal_and_publishes_change(self):
        # emotion_module = ConcreteEmotionModule(message_bus=self.bus, module_id=self.module_id) # Use self.emotion_module
        initial_vad_state = self.emotion_module.get_emotional_state().copy()

        async def run_test_logic():
            # self.bus.subscribe(self.module_id, "EmotionalStateChange", self._emotional_state_change_listener) # Moved to setUp

            goal_payload = GoalUpdatePayload(
                goal_id="g_emo_test",
                goal_description="Goal to make Pia happy",
                priority=0.9, # High priority
                status="achieved", # Positive status
                originator="TestSystem"
            )
            goal_update_msg = GenericMessage(
                source_module_id="TestMotSys",
                message_type="GoalUpdate",
                payload=goal_payload,
                message_id="goal_update_msg_id_1"
            )

            self.bus.publish(goal_update_msg)
            await asyncio.sleep(0.01)

            # 1. Check that an EmotionalStateChange was published
            self.assertEqual(len(self.received_emotional_state_changes), 1)
            event_msg = self.received_emotional_state_changes[0]
            self.assertEqual(event_msg.source_module_id, self.module_id)

            payload: EmotionalStateChangePayload = event_msg.payload
            self.assertEqual(payload.triggering_event_id, "goal_update_msg_id_1")

            # 2. Check that the emotion module's state changed in a way consistent with the goal
            current_vad_state = self.emotion_module.get_emotional_state()
            self.assertNotEqual(current_vad_state, initial_vad_state)
            self.assertTrue(current_vad_state["valence"] > initial_vad_state["valence"])
            self.assertTrue(current_vad_state["valence"] > 0.3) # More specific check based on logic
            self.assertTrue(payload.current_emotion_profile["valence"] > 0.3)
            self.assertIsInstance(payload.primary_emotion, str)
            self.assertTrue(len(payload.primary_emotion) > 0)
            self.assertEqual(payload.intensity, payload.current_emotion_profile["arousal"])

        asyncio.run(run_test_logic())

    # --- New Tests for PerceptData and ActionEvent Handling ---

    def test_handle_percept_data_triggers_appraisal(self):
        async def run_test_logic():
            initial_valence = self.emotion_module.current_emotion_state["valence"]
            initial_arousal = self.emotion_module.current_emotion_state["arousal"]

            # Test Case 1: Sudden loud noise
            percept_loud_noise = PerceptDataPayload(
                percept_id="p_noise", modality="sound",
                content={"type": "sudden_loud_noise", "decibels": 90},
                source_timestamp=datetime.now(timezone.utc)
            )
            msg_noise = GenericMessage("SensorSys", "PerceptData", percept_loud_noise, message_id="noise_msg_1")
            self.bus.publish(msg_noise)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_emotional_state_changes), 1)
            esc_payload_noise: EmotionalStateChangePayload = self.received_emotional_state_changes[0].payload
            self.assertEqual(esc_payload_noise.triggering_event_id, "noise_msg_1")
            # Expect increased arousal, valence might be slightly negative or neutral from surprise
            self.assertTrue(esc_payload_noise.current_emotion_profile["arousal"] > initial_arousal)
            self.assertIsInstance(esc_payload_noise.primary_emotion, str)
            self.assertTrue(len(esc_payload_noise.primary_emotion) > 0)
            self.assertEqual(esc_payload_noise.intensity, esc_payload_noise.current_emotion_profile["arousal"])
            self.received_emotional_state_changes.clear()

            # Test Case 2: Negative text sentiment
            percept_neg_text = PerceptDataPayload(
                percept_id="p_text_warn", modality="text",
                content={"sentiment": "very_negative", "keywords": ["warning", "critical_failure"]},
                source_timestamp=datetime.now(timezone.utc)
            )
            msg_text = GenericMessage("CommSys", "PerceptData", percept_neg_text, message_id="text_msg_1")
            self.bus.publish(msg_text)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_emotional_state_changes), 1)
            esc_payload_text: EmotionalStateChangePayload = self.received_emotional_state_changes[0].payload
            self.assertEqual(esc_payload_text.triggering_event_id, "text_msg_1")
            # Expect decreased valence, increased arousal
            self.assertTrue(esc_payload_text.current_emotion_profile["valence"] < initial_valence) # Or less than the noise one
            self.assertTrue(esc_payload_text.current_emotion_profile["arousal"] > initial_arousal) # Could be different from noise arousal
            self.assertIsInstance(esc_payload_text.primary_emotion, str)
            self.assertTrue(len(esc_payload_text.primary_emotion) > 0)
            self.assertEqual(esc_payload_text.intensity, esc_payload_text.current_emotion_profile["arousal"])
        asyncio.run(run_test_logic())

    def test_handle_action_event_triggers_appraisal(self):
        async def run_test_logic():
            initial_valence = self.emotion_module.current_emotion_state["valence"]

            # Test Case 1: Successful action
            action_success = ActionEventPayload(
                action_command_id="cmd_act_s1", action_type="perform_task", status="SUCCESS",
                outcome={"result": "completed_flawlessly", "goal_priority": 0.8, "action_importance": 0.7},
                timestamp=datetime.now(timezone.utc)
            )
            msg_success = GenericMessage("ExecSys", "ActionEvent", action_success, message_id="action_s_msg_1")
            self.bus.publish(msg_success)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_emotional_state_changes), 1)
            esc_payload_success: EmotionalStateChangePayload = self.received_emotional_state_changes[0].payload
            self.assertEqual(esc_payload_success.triggering_event_id, "action_s_msg_1")
            self.assertTrue(esc_payload_success.current_emotion_profile["valence"] > initial_valence) # Positive change
            self.assertIsInstance(esc_payload_success.primary_emotion, str)
            self.assertTrue(len(esc_payload_success.primary_emotion) > 0)
            self.assertEqual(esc_payload_success.intensity, esc_payload_success.current_emotion_profile["arousal"])
            self.received_emotional_state_changes.clear()

            # Test Case 2: Failed action
            initial_valence_before_fail = self.emotion_module.current_emotion_state["valence"] # May have changed from success
            action_failure = ActionEventPayload(
                action_command_id="cmd_act_f1", action_type="another_task", status="FAILURE",
                outcome={"reason": "critical_system_error", "goal_priority": 0.9, "action_importance": 0.85},
                timestamp=datetime.now(timezone.utc)
            )
            msg_failure = GenericMessage("ExecSys", "ActionEvent", action_failure, message_id="action_f_msg_1")
            self.bus.publish(msg_failure)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_emotional_state_changes), 1)
            esc_payload_failure: EmotionalStateChangePayload = self.received_emotional_state_changes[0].payload
            self.assertEqual(esc_payload_failure.triggering_event_id, "action_f_msg_1")
            self.assertTrue(esc_payload_failure.current_emotion_profile["valence"] < initial_valence_before_fail) # Negative change
            self.assertIsInstance(esc_payload_failure.primary_emotion, str)
            self.assertTrue(len(esc_payload_failure.primary_emotion) > 0)
            self.assertEqual(esc_payload_failure.intensity, esc_payload_failure.current_emotion_profile["arousal"])
        asyncio.run(run_test_logic())


    def test_get_module_status(self):
        # emotion_module = ConcreteEmotionModule(message_bus=self.bus, module_id=self.module_id) # Use self.emotion_module
        status = self.emotion_module.get_status()
        self.assertEqual(status["module_id"], self.module_id)
        self.assertTrue(status["message_bus_connected"])
        self.assertIn("current_vad_state", status)

        emotion_module_no_bus = ConcreteEmotionModule(message_bus=None, module_id="NoBusStatus")
        status_no_bus = emotion_module_no_bus.get_status()
        self.assertEqual(status_no_bus["module_id"], "NoBusStatus")
        self.assertFalse(status_no_bus["message_bus_connected"])

    def test_map_vad_to_discrete_emotion_logic(self):
        # Direct test of the helper method
        test_cases = [
            ({"valence": 0.8, "arousal": 0.8, "dominance": 0.5}, "Joy_Excited"), # High V, High A
            ({"valence": 0.6, "arousal": 0.7, "dominance": 0.2}, "Joyful"),    # Mid-High V, Mid-High A
            ({"valence": 0.3, "arousal": 0.7, "dominance": 0.1}, "Pleased_Alert"),# Mid V, High A
            ({"valence": -0.7, "arousal": 0.8, "dominance": -0.3}, "Anger_Rage"),# Low V, High A
            ({"valence": -0.3, "arousal": 0.7, "dominance": -0.1}, "Distress_Fear"),# Mid-Low V, High A
            ({"valence": 0.0, "arousal": 0.8, "dominance": 0.0}, "High_Arousal_Neutral_Valence"), # Neutral V, High A

            ({"valence": -0.6, "arousal": 0.15, "dominance": -0.4}, "Sadness"), # Low V, Low A
            ({"valence": 0.0, "arousal": 0.1, "dominance": 0.0}, "Calm"),      # Neutral V, Low A
            ({"valence": 0.6, "arousal": 0.15, "dominance": 0.3}, "Content"),  # High V, Low A

            ({"valence": 0.6, "arousal": 0.4, "dominance": 0.3}, "Happy"),        # High V, Mid A
            ({"valence": 0.3, "arousal": 0.4, "dominance": 0.1}, "Pleased_Engaged"),# Mid V, Mid A
            ({"valence": -0.6, "arousal": 0.5, "dominance": -0.2}, "Frustration_Annoyance"),# Low V, Mid A
            ({"valence": -0.3, "arousal": 0.4, "dominance": -0.1}, "Displeasure"),  # Mid-Low V, Mid A
            ({"valence": 0.0, "arousal": 0.5, "dominance": 0.0}, "Neutral_Active") # Neutral V, Mid A
        ]

        for vad_state, expected_emotion in test_cases:
            with self.subTest(vad_state=vad_state):
                discrete_emotion = self.emotion_module._map_vad_to_discrete_emotion(vad_state)
                self.assertEqual(discrete_emotion, expected_emotion)

    def test_appraise_event_detailed_inputs_and_discrete_emotion(self):
        async def run_test_logic():
            # Scenario 1: Positive outcome, self-agency, high control
            self.received_emotional_state_changes.clear()
            self.emotion_module.current_emotion_state = {"valence": 0.0, "arousal": 0.0, "dominance": 0.0} # Reset VAD

            event_details_positive = {
                "type": "SELF_SUCCESS_MAJOR", "intensity": 0.8,
                "goal_congruence": 0.9, "goal_importance": 0.8,
                "agency": "self", "norm_alignment": 0.7,
                "controllability": 0.9, "expectedness": 0.7,
                "novelty": 0.3, "triggering_message_id": "event_self_success_1"
            }
            self.emotion_module.appraise_event(event_details_positive)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_emotional_state_changes), 1)
            payload_positive: EmotionalStateChangePayload = self.received_emotional_state_changes[0].payload

            # Assert VAD changes (conceptual, actual values depend on precise formula application in module)
            # Desirability = 0.9 * 0.8 = 0.72. Valence change dominated by this.
            # Norm_alignment = 0.7. Also positive.
            self.assertTrue(payload_positive.current_emotion_profile["valence"] > 0.5, f"Valence not strongly positive: {payload_positive.current_emotion_profile['valence']}")
            # Arousal: intensity 0.8, unexpectedness (1-0.7)=0.3, abs(desirability) 0.72, novelty 0.3
            # Arousal_change approx (0.8*0.4) + (0.3*0.4*0.8) + (0.72*0.2*0.8) + (0.3*0.1*0.8) = 0.32 + 0.096 + 0.1152 + 0.024 = ~0.55
            self.assertTrue(payload_positive.current_emotion_profile["arousal"] > 0.4,  f"Arousal not moderate-high: {payload_positive.current_emotion_profile['arousal']}") # After decay
            # Dominance: (0.9-0.5)*0.3*0.8 (control) + 0.1*0.8 (self-agency positive) = (0.4*0.24) + 0.08 = 0.096 + 0.08 = 0.176
            self.assertTrue(payload_positive.current_emotion_profile["dominance"] > 0.1,  f"Dominance not positive: {payload_positive.current_emotion_profile['dominance']}")

            # Assert discrete emotion and payload fields
            # For V > 0.5, A > 0.4, a positive high-arousal emotion is expected.
            # Example: if V=0.6, A=0.5 -> Happy. If V=0.6, A=0.7 -> Joyful
            self.assertIn(payload_positive.primary_emotion, ["Happy", "Joyful", "Joy_Excited", "Pleased_Engaged", "Pleased_Alert"],
                          f"Unexpected discrete emotion: {payload_positive.primary_emotion} for V={payload_positive.current_emotion_profile['valence']:.2f} A={payload_positive.current_emotion_profile['arousal']:.2f}")
            self.assertEqual(payload_positive.intensity, payload_positive.current_emotion_profile["arousal"])
            self.assertEqual(payload_positive.triggering_event_id, "event_self_success_1")


            # Scenario 2: Negative outcome, other-agency, low control, unexpected
            self.received_emotional_state_changes.clear()
            self.emotion_module.current_emotion_state = {"valence": 0.0, "arousal": 0.0, "dominance": 0.0} # Reset VAD

            event_details_negative = {
                "type": "OTHER_MAJOR_FAILURE", "intensity": 0.9,
                "goal_congruence": -0.7, "goal_importance": 0.8,
                "agency": "other", "norm_alignment": -0.5,
                "controllability": 0.2, "expectedness": 0.2, # highly unexpected (1-0.2 = 0.8)
                "novelty": 0.8, "triggering_message_id": "event_other_failure_1"
            }
            self.emotion_module.appraise_event(event_details_negative)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_emotional_state_changes), 1)
            payload_negative: EmotionalStateChangePayload = self.received_emotional_state_changes[0].payload

            # Assert VAD changes
            # Desirability = -0.7 * 0.8 = -0.56. Valence change dominated by this.
            # Norm_alignment = -0.5. Also negative.
            self.assertTrue(payload_negative.current_emotion_profile["valence"] < -0.4, f"Valence not strongly negative: {payload_negative.current_emotion_profile['valence']}")
            # Arousal: intensity 0.9, unexpectedness 0.8, abs(desirability) 0.56, novelty 0.8
            # Arousal_change approx (0.9*0.4) + (0.8*0.4*0.9) + (0.56*0.2*0.9) + (0.8*0.1*0.9) = 0.36 + 0.288 + 0.1008 + 0.072 = ~0.82
            self.assertTrue(payload_negative.current_emotion_profile["arousal"] > 0.6, f"Arousal not high: {payload_negative.current_emotion_profile['arousal']}") # After decay
            # Dominance: (0.2-0.5)*0.3*0.9 (control) = -0.3 * 0.27 = -0.081. Agency is "other".
            self.assertTrue(payload_negative.current_emotion_profile["dominance"] < -0.05, f"Dominance not negative: {payload_negative.current_emotion_profile['dominance']}")

            # Assert discrete emotion and payload fields
            # For V < -0.4, A > 0.6, a negative high-arousal emotion is expected
            self.assertIn(payload_negative.primary_emotion, ["Angry", "Frustrated", "Distress_Fear", "Anger_Rage"],
                           f"Unexpected discrete emotion: {payload_negative.primary_emotion} for V={payload_negative.current_emotion_profile['valence']:.2f} A={payload_negative.current_emotion_profile['arousal']:.2f}")
            self.assertEqual(payload_negative.intensity, payload_negative.current_emotion_profile["arousal"])
            self.assertEqual(payload_negative.triggering_event_id, "event_other_failure_1")

        asyncio.run(run_test_logic())

    def test_personality_influence_on_appraisal(self):
        async def run_test_logic():
            # Part 1: Setting profile and its effect on baseline VAD and reactivity
            self.emotion_module._log.clear()
            initial_reactivity = self.emotion_module._reactivity_modifier_arousal
            initial_valence = self.emotion_module.current_emotion_state["valence"]

            profile_data = {"reactivity_modifier_arousal": 1.5, "default_mood_valence": 0.1, "neuroticism": 0.8, "extraversion": 0.2}
            self.emotion_module.set_personality_profile(profile_data)

            self.assertEqual(self.emotion_module._reactivity_modifier_arousal, 1.5)
            # Check if valence was influenced (averaged towards default_mood_valence)
            expected_valence_after_set = (initial_valence + 0.1) / 2.0
            self.assertAlmostEqual(self.emotion_module.current_emotion_state["valence"], expected_valence_after_set, places=3)
            self.assertTrue(any(f"Personality: reactivity_modifier_arousal set to 1.5" in log for log in self.emotion_module._log))
            self.assertTrue(any(f"Personality: default_mood_valence 0.1 influencing VAD." in log for log in self.emotion_module._log))

            # Part 2: Influence on arousal during appraisal
            self.received_emotional_state_changes.clear()
            self.emotion_module.current_emotion_state = {"valence": 0.0, "arousal": 0.0, "dominance": 0.0} # Reset VAD
            self.emotion_module.set_personality_profile({"reactivity_modifier_arousal": 2.0}) # High reactivity

            event_details_arousal = {"type": "MILD_STIMULUS", "intensity": 0.5, "unexpectedness": 0.5, "novelty": 0.2, "triggering_message_id": "event_arousal1"}
            self.emotion_module.appraise_event(event_details_arousal)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_emotional_state_changes), 1)
            payload_high_reactivity: EmotionalStateChangePayload = self.received_emotional_state_changes[0].payload
            arousal_high_reactivity = payload_high_reactivity.current_emotion_profile["arousal"]
            # Check for log of personality application during appraisal
            self.assertTrue(any("Personality: Arousal reactivity modifier 2.0 was applied" in log for log in self.emotion_module._log))

            # Reset and test with low reactivity
            self.received_emotional_state_changes.clear()
            self.emotion_module._log.clear()
            self.emotion_module.current_emotion_state = {"valence": 0.0, "arousal": 0.0, "dominance": 0.0}
            self.emotion_module.set_personality_profile({"reactivity_modifier_arousal": 0.5}) # Low reactivity

            self.emotion_module.appraise_event(event_details_arousal) # Same event
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_emotional_state_changes), 1)
            payload_low_reactivity: EmotionalStateChangePayload = self.received_emotional_state_changes[0].payload
            arousal_low_reactivity = payload_low_reactivity.current_emotion_profile["arousal"]
            self.assertTrue(any("Personality: Arousal reactivity modifier 0.5 was applied" in log for log in self.emotion_module._log))

            self.assertGreater(arousal_high_reactivity, arousal_low_reactivity,
                             f"Arousal with high reactivity ({arousal_high_reactivity}) should be greater than with low reactivity ({arousal_low_reactivity}) for the same event.")

            # Conceptual check for neuroticism/extraversion logging (actual VAD change effect is placeholder)
            self.emotion_module.current_emotion_state = {"valence": 0.0, "arousal": 0.0, "dominance": 0.0}
            self.emotion_module.set_personality_profile({"neuroticism": 0.8, "extraversion": 0.8})
            self.emotion_module._log.clear()
            event_neg_desirability = {"type": "NEG_EVENT", "intensity": 0.5, "goal_congruence": -0.5, "goal_importance":1.0, "agency":"other"} # desirability = -0.5
            self.emotion_module.appraise_event(event_neg_desirability)
            await asyncio.sleep(0.01)
            self.assertTrue(any("Personality (Neuroticism > 0.7 & neg desirability): Amplifying negative valence impact" in log for log in self.emotion_module._log))

            self.emotion_module.current_emotion_state = {"valence": 0.0, "arousal": 0.0, "dominance": 0.0}
            self.emotion_module._log.clear()
            event_pos_desirability = {"type": "POS_EVENT", "intensity": 0.5, "goal_congruence": 0.5, "goal_importance":1.0, "agency":"other"} # desirability = 0.5
            self.emotion_module.appraise_event(event_pos_desirability)
            await asyncio.sleep(0.01)
            self.assertTrue(any("Personality (Extraversion > 0.7 & pos desirability): Amplifying positive valence impact" in log for log in self.emotion_module._log))

        asyncio.run(run_test_logic())

    def test_decay_emotions(self):
        self.emotion_module.current_emotion_state = {"valence": 0.8, "arousal": 0.7, "dominance": -0.6}

        # First decay
        self.emotion_module._decay_emotions(decay_factor=0.9)
        self.assertAlmostEqual(self.emotion_module.current_emotion_state["valence"], 0.8 * 0.9, places=3)
        self.assertAlmostEqual(self.emotion_module.current_emotion_state["arousal"], 0.7 * 0.9, places=3)
        self.assertAlmostEqual(self.emotion_module.current_emotion_state["dominance"], -0.6 * 0.9, places=3)

        # Second decay
        v_after_1 = self.emotion_module.current_emotion_state["valence"]
        a_after_1 = self.emotion_module.current_emotion_state["arousal"]
        d_after_1 = self.emotion_module.current_emotion_state["dominance"]
        self.emotion_module._decay_emotions(decay_factor=0.9)
        self.assertAlmostEqual(self.emotion_module.current_emotion_state["valence"], v_after_1 * 0.9, places=3)
        self.assertAlmostEqual(self.emotion_module.current_emotion_state["arousal"], a_after_1 * 0.9, places=3)
        self.assertAlmostEqual(self.emotion_module.current_emotion_state["dominance"], d_after_1 * 0.9, places=3)

        # Test clamping (arousal should not go below 0)
        self.emotion_module.current_emotion_state = {"valence": 0.1, "arousal": 0.05, "dominance": -0.05}
        self.emotion_module._decay_emotions(decay_factor=0.1) # Strong decay
        self.assertAlmostEqual(self.emotion_module.current_emotion_state["valence"], 0.01, places=3)
        self.assertAlmostEqual(self.emotion_module.current_emotion_state["arousal"], 0.005, places=3) # 0.05 * 0.1 = 0.005
        self.assertAlmostEqual(self.emotion_module.current_emotion_state["dominance"], -0.005, places=3)

        # Decay arousal to zero
        self.emotion_module.current_emotion_state["arousal"] = 0.001
        self.emotion_module._decay_emotions(decay_factor=0.1)
        self.assertAlmostEqual(self.emotion_module.current_emotion_state["arousal"], 0.0, places=3) # Clamped to 0

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
```
