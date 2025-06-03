import unittest
from unittest.mock import MagicMock, call
import datetime
import uuid # Required for payload creation
import io # For capturing stdout
import contextlib # For redirect_stdout
import traceback # For checking traceback string

# Adjust path for consistent imports
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    from PiaAGI_Research_Tools.PiaCML import (
        MessageBus,
        GenericMessage,
        PerceptDataPayload
    )
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from message_bus import MessageBus
    from core_messages import GenericMessage, PerceptDataPayload

class TestMessageBus(unittest.TestCase):

    def setUp(self):
        self.bus = MessageBus()
        self.mock_callback_module1_typeA = MagicMock(name="cb_m1_typeA")
        self.mock_callback_module2_typeA = MagicMock(name="cb_m2_typeA")
        self.mock_callback_module1_typeB = MagicMock(name="cb_m1_typeB")

        # Suppress print statements from MessageBus during tests for cleaner test output,
        # unless a specific test needs to capture it.
        self._original_stdout = sys.stdout
        # Comment out the line below to see MessageBus print statements during tests
        sys.stdout = io.StringIO() # Default to capturing, tests can redirect if needed for assertion

    def tearDown(self):
        sys.stdout = self._original_stdout # Restore stdout

    def _create_test_message(self, message_type: str, payload_content: Any, source_module_id: str = "test_source") -> GenericMessage:
        if message_type == "PerceptData":
            payload = PerceptDataPayload(modality="text", content=payload_content, source_timestamp=datetime.datetime.now(datetime.timezone.utc))
        else:
            payload = {"data": payload_content}
        return GenericMessage(source_module_id=source_module_id, message_type=message_type, payload=payload)

    def test_subscribe_and_publish_single_subscriber(self):
        self.bus.subscribe("module1", "TypeA", self.mock_callback_module1_typeA)
        message = self._create_test_message("TypeA", "hello")
        self.bus.publish(message)
        self.mock_callback_module1_typeA.assert_called_once_with(message)

    def test_publish_to_multiple_subscribers_same_type(self):
        self.bus.subscribe("module1", "TypeA", self.mock_callback_module1_typeA)
        self.bus.subscribe("module2", "TypeA", self.mock_callback_module2_typeA)
        message = self._create_test_message("TypeA", "test data for TypeA")
        self.bus.publish(message)
        self.mock_callback_module1_typeA.assert_called_once_with(message)
        self.mock_callback_module2_typeA.assert_called_once_with(message)

    def test_publish_to_correct_message_type_subscribers_only(self):
        self.bus.subscribe("module1", "TypeA", self.mock_callback_module1_typeA)
        self.bus.subscribe("module1", "TypeB", self.mock_callback_module1_typeB)
        message_A = self._create_test_message("TypeA", "TypeA data")
        self.bus.publish(message_A)
        self.mock_callback_module1_typeA.assert_called_once_with(message_A)
        self.mock_callback_module1_typeB.assert_not_called()
        self.mock_callback_module1_typeA.reset_mock()
        message_B = self._create_test_message("TypeB", "TypeB data")
        self.bus.publish(message_B)
        self.mock_callback_module1_typeA.assert_not_called()
        self.mock_callback_module1_typeB.assert_called_once_with(message_B)

    def test_publish_no_subscribers(self):
        message = self._create_test_message("TypeC", "lonely data")
        try:
            self.bus.publish(message)
        except Exception as e:
            self.fail(f"Publishing with no subscribers raised an exception: {e}")
        self.mock_callback_module1_typeA.assert_not_called()

    def test_unsubscribe(self):
        self.bus.subscribe("module1", "TypeA", self.mock_callback_module1_typeA)
        self.bus.unsubscribe("module1", "TypeA", self.mock_callback_module1_typeA)
        message = self._create_test_message("TypeA", "data for unsubscribed")
        self.bus.publish(message)
        self.mock_callback_module1_typeA.assert_not_called()

    def test_unsubscribe_specific_callback_and_filter_handling(self):
        another_callback_for_module1 = MagicMock(name="another_cb_m1_typeA")
        filter_func1 = MagicMock(return_value=True, name="filter1")

        self.bus.subscribe("module1", "TypeA", self.mock_callback_module1_typeA, filter_func=None)
        self.bus.subscribe("module1", "TypeA", another_callback_for_module1, filter_func=filter_func1)

        # Unsubscribe the first one (without filter)
        # Current unsubscribe removes all matching (module_id, callback) regardless of filter.
        self.bus.unsubscribe("module1", "TypeA", self.mock_callback_module1_typeA)

        message = self._create_test_message("TypeA", "test for specific unsubscribe")
        self.bus.publish(message)

        self.mock_callback_module1_typeA.assert_not_called() # Should be removed
        # The other callback (another_callback_for_module1) with its filter should still be there
        # and since filter_func1 returns True, it should be called.
        filter_func1.assert_called_once_with(message)
        another_callback_for_module1.assert_called_once_with(message)

        # Reset and test unsubscribing the one with the filter
        another_callback_for_module1.reset_mock()
        filter_func1.reset_mock()
        self.bus.subscribe("module1", "TypeA", self.mock_callback_module1_typeA, filter_func=None) # Re-subscribe first one

        self.bus.unsubscribe("module1", "TypeA", another_callback_for_module1) # Unsubscribe the second one
        self.bus.publish(message)
        self.mock_callback_module1_typeA.assert_called_once_with(message) # First one should be called
        another_callback_for_module1.assert_not_called() # Second one removed
        filter_func1.assert_not_called() # Its filter should not be called

    def test_avoid_duplicate_subscriptions_with_filters(self):
        filter1 = MagicMock(return_value=True)
        filter2 = MagicMock(return_value=True)

        self.bus.subscribe("module1", "TypeA", self.mock_callback_module1_typeA, filter_func=filter1)
        self.bus.subscribe("module1", "TypeA", self.mock_callback_module1_typeA, filter_func=filter1) # Exact duplicate
        self.assertEqual(len(self.bus.get_subscribers_for_type("TypeA")), 1)

        self.bus.subscribe("module1", "TypeA", self.mock_callback_module1_typeA, filter_func=filter2) # Same cb, different filter
        self.assertEqual(len(self.bus.get_subscribers_for_type("TypeA")), 2)

        self.bus.subscribe("module1", "TypeA", self.mock_callback_module1_typeA, filter_func=None) # Same cb, no filter
        self.assertEqual(len(self.bus.get_subscribers_for_type("TypeA")), 3)

        message = self._create_test_message("TypeA", "test")
        self.bus.publish(message)
        # mock_callback_module1_typeA should be called 3 times because it's subscribed 3 ways (filter1, filter2, None)
        # and both mocked filters return True.
        self.assertEqual(self.mock_callback_module1_typeA.call_count, 3)
        filter1.assert_called_once_with(message)
        filter2.assert_called_once_with(message)


    def test_get_subscribers_for_type(self):
        self.assertEqual(len(self.bus.get_subscribers_for_type("TypeNonExistent")), 0)
        filter_fn = lambda msg: True
        self.bus.subscribe("module1", "TypeX", self.mock_callback_module1_typeA, filter_func=filter_fn)
        subscribers = self.bus.get_subscribers_for_type("TypeX")
        self.assertEqual(len(subscribers), 1)
        self.assertEqual(subscribers[0][0], "module1")
        self.assertEqual(subscribers[0][1], self.mock_callback_module1_typeA)
        self.assertEqual(subscribers[0][2], filter_fn)

    def test_improved_error_handling_in_callback(self):
        faulty_callback = MagicMock(side_effect=ValueError("Callback custom error!"))
        self.bus.subscribe("faulty_module", "TypeA", faulty_callback)
        self.bus.subscribe("module1", "TypeA", self.mock_callback_module1_typeA) # Good callback

        message = self._create_test_message("TypeA", "test data for error handling")

        # Capture stdout to check the error message
        captured_output = io.StringIO()
        sys.stdout = captured_output # Redirect stdout

        self.bus.publish(message)

        sys.stdout = self._original_stdout # Restore stdout

        output_str = captured_output.getvalue()

        faulty_callback.assert_called_once_with(message)
        self.mock_callback_module1_typeA.assert_called_once_with(message)

        self.assertIn("ERROR: Callback error in module 'faulty_module'", output_str)
        self.assertIn("message type 'TypeA'", output_str)
        self.assertIn(f"msg_id: {message.message_id}", output_str)
        self.assertIn("Exception: ValueError('Callback custom error!')", output_str)
        self.assertIn("Traceback (most recent call last):", output_str)
        # Check if the specific error message from the exception is in the output
        self.assertIn("Callback custom error!", output_str)


    def test_subscribe_with_filter_and_publish(self):
        filter_allow_specific_source = lambda msg: msg.source_module_id == "allowed_source"
        self.bus.subscribe("module1", "TypeFiltered", self.mock_callback_module1_typeA, filter_func=filter_allow_specific_source)

        msg_allowed = self._create_test_message("TypeFiltered", "allowed data", source_module_id="allowed_source")
        msg_denied = self._create_test_message("TypeFiltered", "denied data", source_module_id="denied_source")

        self.bus.publish(msg_allowed)
        self.mock_callback_module1_typeA.assert_called_once_with(msg_allowed)
        self.mock_callback_module1_typeA.reset_mock()

        self.bus.publish(msg_denied)
        self.mock_callback_module1_typeA.assert_not_called()

    def test_publish_with_multiple_filters_and_no_filter(self):
        filter_payload_contains_target = lambda msg: "target" in msg.payload.get("data", "")
        cb_with_filter = MagicMock(name="cb_with_filter")
        cb_no_filter = MagicMock(name="cb_no_filter")

        self.bus.subscribe("mod_filter", "MultiFilterTest", cb_with_filter, filter_func=filter_payload_contains_target)
        self.bus.subscribe("mod_no_filter", "MultiFilterTest", cb_no_filter, filter_func=None)

        msg_with_target = self._create_test_message("MultiFilterTest", {"data": "some target data"})
        msg_without_target = self._create_test_message("MultiFilterTest", {"data": "some other data"})

        self.bus.publish(msg_with_target)
        cb_with_filter.assert_called_once_with(msg_with_target)
        cb_no_filter.assert_called_once_with(msg_with_target)

        cb_with_filter.reset_mock()
        cb_no_filter.reset_mock()

        self.bus.publish(msg_without_target)
        cb_with_filter.assert_not_called() # Filter should block
        cb_no_filter.assert_called_once_with(msg_without_target) # No filter, should be called

    def test_asynchronous_dispatch_logging(self):
        message = self._create_test_message("TypeAsync", "async test")
        self.bus.subscribe("module_async", "TypeAsync", self.mock_callback_module1_typeA)

        captured_output = io.StringIO()
        sys.stdout = captured_output

        self.bus.publish(message, dispatch_mode="asynchronous")

        sys.stdout = self._original_stdout
        output_str = captured_output.getvalue()

        self.mock_callback_module1_typeA.assert_called_once_with(message) # Still called synchronously for PoC
        self.assertIn(f"INFO: Asynchronous dispatch requested for module_async on message '{message.message_id}' (actual async execution deferred for PoC).", output_str)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
