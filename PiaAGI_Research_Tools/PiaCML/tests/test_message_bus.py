import unittest
from unittest.mock import MagicMock, call
import datetime
import uuid # Required for payload creation, though not directly for bus logic

# Adjust path for consistent imports
# This assumes tests are in PiaAGI_Research_Tools/PiaCML/tests/
# and modules are in PiaAGI_Research_Tools/PiaCML/
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    # Attempt to import directly from the package level due to __init__.py setup
    from PiaAGI_Research_Tools.PiaCML import (
        MessageBus,
        GenericMessage,
        PerceptDataPayload # Used in tests as an example payload
    )
except ModuleNotFoundError as e:
    print(f"Package-level import error in test_message_bus.py: {e}")
    print("Attempting direct local imports as fallback...")
    # Fallback if the above doesn't work (e.g. when CWD is PiaAGI_Research_Tools/PiaCML/tests)
    # This often means the test runner isn't picking up the package structure correctly.
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # Add PiaCML to path
    from message_bus import MessageBus
    from core_messages import GenericMessage, PerceptDataPayload


class TestMessageBus(unittest.TestCase):

    def setUp(self):
        self.bus = MessageBus()
        self.mock_callback_module1_typeA = MagicMock()
        self.mock_callback_module2_typeA = MagicMock()
        self.mock_callback_module1_typeB = MagicMock()
        self._original_stdout = sys.stdout
        # Suppress prints from the module during tests for cleaner output
        # sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        """Restore stdout after each test."""
        # sys.stdout.close()
        sys.stdout = self._original_stdout


    def test_subscribe_and_publish_single_subscriber(self):
        self.bus.subscribe("module1", "TypeA", self.mock_callback_module1_typeA)

        payload = PerceptDataPayload(modality="text", content="hello", source_timestamp=datetime.datetime.now(datetime.timezone.utc))
        message = GenericMessage(source_module_id="perception", message_type="TypeA", payload=payload)

        self.bus.publish(message)

        self.mock_callback_module1_typeA.assert_called_once_with(message)

    def test_publish_to_multiple_subscribers_same_type(self):
        self.bus.subscribe("module1", "TypeA", self.mock_callback_module1_typeA)
        self.bus.subscribe("module2", "TypeA", self.mock_callback_module2_typeA)

        payload = {"data": "test data for TypeA"}
        message = GenericMessage(source_module_id="source", message_type="TypeA", payload=payload)
        self.bus.publish(message)

        self.mock_callback_module1_typeA.assert_called_once_with(message)
        self.mock_callback_module2_typeA.assert_called_once_with(message)

    def test_publish_to_correct_message_type_subscribers_only(self):
        self.bus.subscribe("module1", "TypeA", self.mock_callback_module1_typeA)
        self.bus.subscribe("module1", "TypeB", self.mock_callback_module1_typeB)

        payload_A = {"data": "TypeA data"}
        message_A = GenericMessage(source_module_id="sourceA", message_type="TypeA", payload=payload_A)
        self.bus.publish(message_A)

        self.mock_callback_module1_typeA.assert_called_once_with(message_A)
        self.mock_callback_module1_typeB.assert_not_called()

        # Reset mock for next publish
        self.mock_callback_module1_typeA.reset_mock()

        payload_B = {"data": "TypeB data"}
        message_B = GenericMessage(source_module_id="sourceB", message_type="TypeB", payload=payload_B)
        self.bus.publish(message_B)

        self.mock_callback_module1_typeA.assert_not_called()
        self.mock_callback_module1_typeB.assert_called_once_with(message_B)

    def test_publish_no_subscribers(self):
        payload = {"data": "lonely data"}
        message = GenericMessage(source_module_id="source", message_type="TypeC", payload=payload)
        # No exception should be raised, and no callbacks called
        try:
            self.bus.publish(message)
        except Exception as e:
            self.fail(f"Publishing with no subscribers raised an exception: {e}")

        self.mock_callback_module1_typeA.assert_not_called()
        self.mock_callback_module2_typeA.assert_not_called()
        self.mock_callback_module1_typeB.assert_not_called()

    def test_unsubscribe(self):
        self.bus.subscribe("module1", "TypeA", self.mock_callback_module1_typeA)
        self.bus.unsubscribe("module1", "TypeA", self.mock_callback_module1_typeA)

        payload = {"data": "data for unsubscribed"}
        message = GenericMessage(source_module_id="source", message_type="TypeA", payload=payload)
        self.bus.publish(message)

        self.mock_callback_module1_typeA.assert_not_called()

    def test_unsubscribe_specific_callback(self):
        another_callback_for_module1 = MagicMock() # Different callback object
        self.bus.subscribe("module1", "TypeA", self.mock_callback_module1_typeA)
        self.bus.subscribe("module1", "TypeA", another_callback_for_module1)

        self.bus.unsubscribe("module1", "TypeA", self.mock_callback_module1_typeA) # Unsubscribe only the first one

        payload = {"data": "test for specific unsubscribe"}
        message = GenericMessage(source_module_id="source", message_type="TypeA", payload=payload)
        self.bus.publish(message)

        self.mock_callback_module1_typeA.assert_not_called()
        another_callback_for_module1.assert_called_once_with(message)

        # Check that unsubscribing a non-existent callback or module doesn't error
        self.bus.unsubscribe("module_unknown", "TypeA", MagicMock())
        self.bus.unsubscribe("module1", "TypeUnknown", MagicMock())
        self.bus.unsubscribe("module1", "TypeA", MagicMock()) # A callback that was never subscribed


    def test_avoid_duplicate_subscriptions(self):
        self.bus.subscribe("module1", "TypeA", self.mock_callback_module1_typeA)
        self.bus.subscribe("module1", "TypeA", self.mock_callback_module1_typeA) # Attempt duplicate

        self.assertEqual(len(self.bus.get_subscribers_for_type("TypeA")), 1)

        payload = {"data": "test for duplicate avoidance"}
        message = GenericMessage(source_module_id="source", message_type="TypeA", payload=payload)
        self.bus.publish(message)
        self.mock_callback_module1_typeA.assert_called_once() # Should only be called once

    def test_get_subscribers_for_type(self):
        self.assertEqual(len(self.bus.get_subscribers_for_type("TypeNonExistent")), 0)

        self.bus.subscribe("module1", "TypeX", self.mock_callback_module1_typeA)
        subscribers = self.bus.get_subscribers_for_type("TypeX")
        self.assertEqual(len(subscribers), 1)
        self.assertEqual(subscribers[0][0], "module1") # module_id
        self.assertEqual(subscribers[0][1], self.mock_callback_module1_typeA) # callback

        # Ensure it returns a copy
        subscribers_copy = self.bus.get_subscribers_for_type("TypeX")
        subscribers_copy.append(("fake_module", MagicMock()))
        self.assertEqual(len(self.bus.get_subscribers_for_type("TypeX")), 1) # Original should be unchanged


    def test_callback_exception_handling(self):
        faulty_callback = MagicMock(side_effect=Exception("Callback error!"))
        self.bus.subscribe("faulty_module", "TypeA", faulty_callback)
        self.bus.subscribe("module1", "TypeA", self.mock_callback_module1_typeA) # Good callback

        payload = {"data": "test data for exception"}
        message = GenericMessage(source_module_id="source", message_type="TypeA", payload=payload)

        # The bus publish method should catch the exception from faulty_callback
        # and still proceed to call other subscribers.
        # For this test, we primarily ensure the good callback is still invoked.
        # A more advanced test might involve capturing stdout/stderr if the bus prints errors.
        try:
            self.bus.publish(message)
        except Exception as e:
            self.fail(f"MessageBus.publish() raised an unexpected exception: {e}")

        faulty_callback.assert_called_once_with(message)
        self.mock_callback_module1_typeA.assert_called_once_with(message) # Ensure other callbacks are not affected

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
