import unittest
import os
import sys
import datetime
from unittest.mock import MagicMock, call

# Adjust path for consistent imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    from PiaAGI_Research_Tools.PiaCML import (
        ConcreteAttentionModule,
        MessageBus,
        GenericMessage,
        GoalUpdatePayload,
        AttentionFocusUpdatePayload,
        EmotionalStateChangePayload # Added formal import
    )
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from concrete_attention_module import ConcreteAttentionModule
    try:
        from message_bus import MessageBus
        from core_messages import (
            GenericMessage, GoalUpdatePayload, AttentionFocusUpdatePayload,
            EmotionalStateChangePayload # Added formal import
        )
    except ImportError:
        MessageBus = None
        GenericMessage = None
        GoalUpdatePayload = None
        AttentionFocusUpdatePayload = None
        EmotionalStateChangePayload = None # Added

class TestConcreteAttentionModule(unittest.TestCase):

    def setUp(self):
        self.bus = MessageBus() if MessageBus else None
        self.mock_bus = MagicMock(spec=MessageBus) if MessageBus else None

        self.attn_no_bus = ConcreteAttentionModule()
        self.attn_with_mock_bus = ConcreteAttentionModule(message_bus=self.mock_bus)
        self.attn_with_real_bus = ConcreteAttentionModule(message_bus=self.bus)

        self._original_stdout = sys.stdout
        # To see print statements from the module during tests, comment out the next line
        # sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        # sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_initial_state_no_bus(self):
        state = self.attn_no_bus.get_attentional_state()
        self.assertIsNone(state['current_focus_payload'])
        self.assertEqual(state['active_filters_count'], 0)
        self.assertEqual(state['cognitive_load_level'], 0.0)
        self.assertEqual(state['module_type'], 'ConcreteAttentionModule')
        self.assertIsNone(self.attn_no_bus.message_bus)

    def test_set_attention_focus_internal_state_no_bus(self):
        """Test set_attention_focus updates internal state correctly without a bus."""
        success = self.attn_no_bus.set_attention_focus("TaskA", "goal_directed", 0.8)
        self.assertTrue(success)
        current_focus_payload = self.attn_no_bus.current_focus
        self.assertIsNotNone(current_focus_payload)
        self.assertEqual(current_focus_payload.focused_item_id, "TaskA")
        self.assertEqual(current_focus_payload.focus_type, "goal_directed")
        self.assertEqual(current_focus_payload.intensity, 0.8)
        self.assertIsInstance(current_focus_payload.timestamp, datetime.datetime)

        state = self.attn_no_bus.get_attentional_state()
        self.assertEqual(state['current_focus_payload']['focused_item_id'], "TaskA")

    def test_filter_information_no_focus_no_bus(self):
        stream = [{'id': '1', 'content': 'info1'}]
        filtered = self.attn_no_bus.filter_information(stream)
        self.assertEqual(len(filtered), 1)

    def test_filter_information_with_focus_no_bus(self):
        self.attn_no_bus.set_attention_focus("apple", "concept", 0.8)
        stream = [
            {'id': '1', 'content': 'An apple a day.'},
            {'id': '2', 'content': 'A banana for lunch.'}
        ]
        filtered = self.attn_no_bus.filter_information(stream)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['id'], '1')

    def test_manage_cognitive_load_no_bus(self):
        thresholds = {'optimal': 0.7, 'overload': 0.9}
        result = self.attn_no_bus.manage_cognitive_load(0.5, thresholds)
        self.assertEqual(result['action'], 'none')


    # --- New Tests for MessageBus Integration ---
    def test_initialization_with_bus_subscription(self):
        """Test AttentionModule initialization with a bus and subscriptions."""
        if not MessageBus: self.skipTest("MessageBus components not available")

        self.assertIsNotNone(self.attn_with_real_bus.message_bus)
        goal_subscribers = self.bus.get_subscribers_for_type("GoalUpdate")
        emotion_subscribers = self.bus.get_subscribers_for_type("EmotionalStateChange")

        found_goal_sub = any(s[0] == "ConcreteAttentionModule_01" and s[1] == self.attn_with_real_bus.handle_goal_update_for_attention for s in goal_subscribers if s)
        found_emotion_sub = any(s[0] == "ConcreteAttentionModule_01" and s[1] == self.attn_with_real_bus.handle_emotion_update_for_attention for s in emotion_subscribers if s)

        self.assertTrue(found_goal_sub, "AttentionModule did not subscribe to GoalUpdate.")
        self.assertTrue(found_emotion_sub, "AttentionModule did not subscribe to EmotionalStateChange.")

    def test_set_attention_focus_publishes_message(self):
        """Test set_attention_focus publishes an AttentionFocusUpdate message."""
        if not MessageBus or not GenericMessage or not AttentionFocusUpdatePayload:
            self.skipTest("MessageBus or core message components not available")

        item_id = "focus_item_publish"
        focus_type = "test_driven"
        intensity = 0.75
        trigger_id = "msg_trigger_xyz"

        self.attn_with_mock_bus.set_attention_focus(item_id, focus_type, intensity, trigger_id)

        self.mock_bus.publish.assert_called_once()
        args, _ = self.mock_bus.publish.call_args
        published_message: GenericMessage = args[0]

        self.assertEqual(published_message.message_type, "AttentionFocusUpdate")
        self.assertEqual(published_message.source_module_id, "ConcreteAttentionModule_01")

        payload: AttentionFocusUpdatePayload = published_message.payload
        self.assertIsInstance(payload, AttentionFocusUpdatePayload)
        self.assertEqual(payload.focused_item_id, item_id)
        self.assertEqual(payload.focus_type, focus_type)
        self.assertEqual(payload.intensity, intensity)
        self.assertEqual(payload.source_trigger_message_id, trigger_id)

    def test_set_attention_focus_no_publish_if_no_bus(self):
        """Test set_attention_focus does not publish if no bus is configured."""
        if not MessageBus: self.skipTest("MessageBus components not available")

        self.attn_no_bus.set_attention_focus("item_no_bus", "type_no_bus", 0.5)
        # mock_bus is associated with attn_with_mock_bus, so this implicitly checks
        # that the no_bus instance doesn't somehow access/use it.
        self.mock_bus.publish.assert_not_called()


    def test_handle_goal_update_for_attention_shifts_focus(self):
        """Test GoalUpdate message leads to attention shift and publish."""
        if not all([MessageBus, GenericMessage, GoalUpdatePayload, AttentionFocusUpdatePayload]):
            self.skipTest("MessageBus or core message components not available")

        # This mock will capture the AttentionFocusUpdate published by set_attention_focus
        # when triggered by the goal update handler.
        mock_attention_subscriber = MagicMock(name="attention_focus_listener")
        self.bus.subscribe("AttentionListener", "AttentionFocusUpdate", mock_attention_subscriber)

        high_prio_goal_payload = GoalUpdatePayload(
            goal_id="urgent_task_001", goal_description="High priority goal",
            priority=0.9, status="ACTIVE", originator="TestMotSys"
        )
        goal_update_msg = GenericMessage(
            source_module_id="TestMotSys", message_type="GoalUpdate",
            payload=high_prio_goal_payload, message_id="goal_msg_1"
        )

        self.bus.publish(goal_update_msg) # This should trigger attn_with_real_bus.handle_goal_update_for_attention

        self.assertIn(high_prio_goal_payload, self.attn_with_real_bus.handled_goal_updates_for_attention)

        # Check that set_attention_focus was called and published an AttentionFocusUpdate
        mock_attention_subscriber.assert_called_once()
        received_focus_update_msg: GenericMessage = mock_attention_subscriber.call_args[0][0]
        self.assertEqual(received_focus_update_msg.message_type, "AttentionFocusUpdate")

        focus_payload: AttentionFocusUpdatePayload = received_focus_update_msg.payload
        self.assertEqual(focus_payload.focused_item_id, f"goal_{high_prio_goal_payload.goal_id}")
        self.assertEqual(focus_payload.focus_type, "goal_directed_trigger")
        self.assertEqual(focus_payload.intensity, high_prio_goal_payload.priority)
        self.assertEqual(focus_payload.source_trigger_message_id, "goal_msg_1")


    def test_handle_emotion_update_for_attention_modulates_focus(self):
        """Test EmotionalStateChange message modulates attention intensity and publishes."""
        if not all([MessageBus, GenericMessage, AttentionFocusUpdatePayload]):
            self.skipTest("MessageBus or core message components not available")

        mock_attention_subscriber = MagicMock(name="emotion_attn_listener")
        self.bus.subscribe("EmotionAttentionListener", "AttentionFocusUpdate", mock_attention_subscriber)

        # Initial focus
        self.attn_with_real_bus.set_attention_focus("initial_item", "background", 0.4, "init_msg")
        mock_attention_subscriber.reset_mock() # Reset after initial focus publish

        emotion_profile_data = {"valence": -0.5, "arousal": 0.8, "dominance": 0.0} # High arousal
        # Create the EmotionalStateChangePayload instance
        # Assuming intensity in the payload is also relevant, let's use arousal for it as per module logic example
        high_arousal_emotion_payload_obj = EmotionalStateChangePayload(
            current_emotion_profile=emotion_profile_data,
            intensity=emotion_profile_data["arousal"]
        )
        emotion_update_msg = GenericMessage(
            source_module_id="TestEmotionSys", message_type="EmotionalStateChange",
            payload=high_arousal_emotion_payload_obj, # Use the dataclass instance
            message_id="emotion_msg_1"
        )

        self.bus.publish(emotion_update_msg)
        await asyncio.sleep(0.01) # Allow message to be processed

        # The handler stores the .current_emotion_profile dict
        self.assertIn(emotion_profile_data, self.attn_with_real_bus.handled_emotion_updates_for_attention)

        mock_attention_subscriber.assert_called_once()
        received_focus_update_msg: GenericMessage = mock_attention_subscriber.call_args[0][0]
        self.assertEqual(received_focus_update_msg.message_type, "AttentionFocusUpdate")

        focus_payload: AttentionFocusUpdatePayload = received_focus_update_msg.payload
        self.assertEqual(focus_payload.focused_item_id, "initial_item") # Focus item should be maintained
        self.assertEqual(focus_payload.focus_type, "emotion_triggered_intensity_increase")
        expected_intensity = min(1.0, 0.4 + 0.1 + (0.8 - 0.7) * 0.5) # 0.4 + 0.1 + 0.05 = 0.55
        self.assertAlmostEqual(focus_payload.intensity, expected_intensity)
        self.assertEqual(focus_payload.source_trigger_message_id, "emotion_msg_1")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
