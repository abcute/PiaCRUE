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
    from PiaAGI_Research_Tools.PiaCML.core_messages import GenericMessage, GoalUpdatePayload, EmotionalStateChangePayload
    from PiaAGI_Research_Tools.PiaCML.concrete_emotion_module import ConcreteEmotionModule
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from message_bus import MessageBus
    from core_messages import GenericMessage, GoalUpdatePayload, EmotionalStateChangePayload
    from concrete_emotion_module import ConcreteEmotionModule

class TestConcreteEmotionModuleIntegration(unittest.TestCase):

    def setUp(self):
        self.bus = MessageBus()
        self.module_id = f"TestEmotionModule_{str(uuid.uuid4())[:8]}"
        # Module instantiated in each test method for a clean state
        self.received_emotional_state_changes: List[GenericMessage] = []

    def _emotional_state_change_listener(self, message: GenericMessage):
        if isinstance(message.payload, EmotionalStateChangePayload):
            self.received_emotional_state_changes.append(message)

    def tearDown(self):
        self.received_emotional_state_changes.clear()

    # --- Test Publishing EmotionalStateChange ---
    def test_appraise_event_publishes_emotional_state_change(self):
        emotion_module = ConcreteEmotionModule(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            self.bus.subscribe(self.module_id, "EmotionalStateChange", self._emotional_state_change_listener)

            event_details_1 = {
                "type": "TEST_EVENT_POSITIVE", "intensity": 0.7, "goal_congruence": 0.8,
                "goal_importance": 0.9, "triggering_message_id": "trigger_msg_001"
            }
            emotion_module.appraise_event(event_details_1)
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

            self.received_emotional_state_changes.clear()

            # Test without triggering_message_id
            event_details_2 = {"type": "TEST_EVENT_NEGATIVE", "intensity": 0.6, "goal_congruence": -0.7, "goal_importance": 0.5}
            emotion_module.appraise_event(event_details_2)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_emotional_state_changes), 1)
            payload2: EmotionalStateChangePayload = self.received_emotional_state_changes[0].payload
            self.assertTrue(payload2.current_emotion_profile["valence"] < 0) # Negative event
            self.assertIsNone(payload2.triggering_event_id)

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
        self.assertEqual(len(self.received_emotional_state_changes), 0)


    # --- Test Subscribing to GoalUpdate ---
    def test_handle_goal_update_for_appraisal_triggers_appraisal_and_publishes_change(self):
        emotion_module = ConcreteEmotionModule(message_bus=self.bus, module_id=self.module_id)
        initial_vad_state = emotion_module.get_emotional_state().copy()

        async def run_test_logic():
            self.bus.subscribe(self.module_id, "EmotionalStateChange", self._emotional_state_change_listener)

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
            current_vad_state = emotion_module.get_emotional_state()
            self.assertNotEqual(current_vad_state, initial_vad_state)

            # For an "achieved" high-priority goal, valence should increase significantly
            # Intensity for appraisal from goal: priority * 0.5 = 0.9 * 0.5 = 0.45
            # Goal congruence: 1.0 (achieved)
            # Goal importance: 0.9 (priority)
            # Expected valence change before decay: 1.0 * 0.9 * 0.45 approx 0.405
            self.assertTrue(current_vad_state["valence"] > initial_vad_state["valence"])
            self.assertTrue(current_vad_state["valence"] > 0.3) # Check for significant positive change
            self.assertTrue(payload.current_emotion_profile["valence"] > 0.3)

        asyncio.run(run_test_logic())

    def test_get_module_status(self):
        emotion_module = ConcreteEmotionModule(message_bus=self.bus, module_id=self.module_id)
        status = emotion_module.get_status()
        self.assertEqual(status["module_id"], self.module_id)
        self.assertTrue(status["message_bus_connected"])
        self.assertIn("current_vad_state", status)

        emotion_module_no_bus = ConcreteEmotionModule(message_bus=None, module_id="NoBusStatus")
        status_no_bus = emotion_module_no_bus.get_status()
        self.assertEqual(status_no_bus["module_id"], "NoBusStatus")
        self.assertFalse(status_no_bus["message_bus_connected"])


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
```
