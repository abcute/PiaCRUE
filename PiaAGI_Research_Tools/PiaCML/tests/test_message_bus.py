import unittest
from unittest.mock import MagicMock, call
import datetime
import uuid
import io
import contextlib
import traceback
import asyncio # Added for async tests

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
    # Import MAX_CALLBACK_ERRORS from the source module
    from PiaAGI_Research_Tools.PiaCML.message_bus import MAX_CALLBACK_ERRORS
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from message_bus import MessageBus, MAX_CALLBACK_ERRORS
    from core_messages import GenericMessage, PerceptDataPayload

class TestMessageBus(unittest.TestCase):

    def setUp(self):
        self.bus = MessageBus()
        # Standard Mocks for sync callbacks
        self.mock_callback_module1_typeA = MagicMock(name="cb_m1_typeA")
        self.mock_callback_module2_typeA = MagicMock(name="cb_m2_typeA")
        self.mock_callback_module1_typeB = MagicMock(name="cb_m1_typeB")

        # Lists to capture calls for async tests
        self.async_call_tracker = []

        # Suppress print statements from MessageBus during tests
        self._original_stdout = sys.stdout
        # sys.stdout = io.StringIO() # Default to capturing; comment out to see prints

    def tearDown(self):
        sys.stdout = self._original_stdout # Restore stdout
        # Reset event loop policy if changed for a specific test (though not planned for these tests)

    def _create_test_message(self, message_type: str, payload_content: Any, source_module_id: str = "test_source", metadata: Optional[Dict[str, Any]] = None) -> GenericMessage:
        if message_type == "PerceptData": # Example specific payload
            payload_obj = PerceptDataPayload(modality="text", content=payload_content, source_timestamp=datetime.datetime.now(datetime.timezone.utc))
        else: # Generic dict payload
            payload_obj = {"data": payload_content}
        return GenericMessage(source_module_id=source_module_id, message_type=message_type, payload=payload_obj, metadata=metadata or {})

    # --- Existing Tests (Ensure they still pass or adapt if necessary) ---
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

    # --- New Tests for Asynchronous Dispatch ---
    async def _async_test_callback(self, message: GenericMessage):
        self.async_call_tracker.append(message)
        await asyncio.sleep(0.001) # Simulate some async work
        self.async_call_tracker.append(f"DONE_{message.message_id}")

    def _sync_test_callback_for_async_dispatch(self, message: GenericMessage):
        self.async_call_tracker.append(message)
        self.async_call_tracker.append(f"SYNC_DONE_{message.message_id}")

    async def _async_test_callback_raises_error(self, message: GenericMessage):
        self.async_call_tracker.append(f"ERROR_ATTEMPT_{message.message_id}")
        await asyncio.sleep(0.001)
        raise ValueError("Async callback error")

    def test_asynchronous_dispatch_async_callback(self):
        async def run_test():
            self.async_call_tracker.clear()
            self.bus.subscribe("async_mod", "AsyncType", self._async_test_callback)
            message = self._create_test_message("AsyncType", "async data")

            # Publish and give asyncio tasks a chance to run
            self.bus.publish(message, dispatch_mode="asynchronous")
            await asyncio.sleep(0.01) # Allow time for tasks created by create_task to run

            self.assertIn(message, self.async_call_tracker)
            self.assertIn(f"DONE_{message.message_id}", self.async_call_tracker)
            self.assertEqual(self.async_call_tracker.index(f"DONE_{message.message_id}"),
                             self.async_call_tracker.index(message) + 1)
        asyncio.run(run_test())

    def test_asynchronous_dispatch_sync_callback(self):
        async def run_test():
            self.async_call_tracker.clear()
            self.bus.subscribe("sync_for_async_mod", "AsyncSyncType", self._sync_test_callback_for_async_dispatch)
            message = self._create_test_message("AsyncSyncType", "sync data for async dispatch")

            self.bus.publish(message, dispatch_mode="asynchronous")
            await asyncio.sleep(0.01)

            self.assertIn(message, self.async_call_tracker)
            self.assertIn(f"SYNC_DONE_{message.message_id}", self.async_call_tracker)
        asyncio.run(run_test())

    def test_synchronous_dispatch_async_callback_warning(self):
        self.async_call_tracker.clear()
        # For this test, we want to capture stdout to check for the warning.
        original_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()

        self.bus.subscribe("async_mod_sync_dispatch", "SyncDispatchAsyncCb", self._async_test_callback)
        message = self._create_test_message("SyncDispatchAsyncCb", "async cb for sync dispatch")

        self.bus.publish(message, dispatch_mode="synchronous")
        # The async callback won't be awaited, so "DONE_..." won't be in tracker immediately (or ever if not run in a loop)
        # The primary check is that it's called and a warning is issued.
        # The call to an async function from sync code returns a coroutine object.
        # The current message_bus.py's sync path for an async callback *will* call it,
        # but it returns a coroutine that isn't awaited by publish.
        # The _execute_callback is async. The warning is in the sync path of publish.

        sys.stdout = original_stdout # Restore stdout
        output = captured_output.getvalue()

        self.assertIn(f"WARNING: Coroutine callback _async_test_callback for module 'async_mod_sync_dispatch' called in synchronous mode.", output)
        # self.assertIn(message, self.async_call_tracker) # This might not be reliable as it's not awaited.
                                                        # The callback *is* called, but it returns a coroutine.
                                                        # The current implementation of _execute_callback when called from sync path
                                                        # for an async function does not add to tracker before returning coroutine.
                                                        # Let's rely on the warning and the fact that it doesn't break.

    # --- New Tests for Error Handling & Suspension ---
    def test_subscriber_suspension_after_max_errors(self):
        sys.stdout = io.StringIO() # Capture prints for this test

        error_callback_tracker = []
        def error_callback(message: GenericMessage):
            error_callback_tracker.append(message.message_id)
            raise ValueError(f"Simulated error for {message.message_id}")

        self.bus.subscribe("error_prone_mod", "ErrorType", error_callback)
        good_callback_tracker = []
        self.bus.subscribe("stable_mod", "ErrorType", lambda msg: good_callback_tracker.append(msg.message_id) )

        for i in range(MAX_CALLBACK_ERRORS + 2):
            msg = self._create_test_message("ErrorType", f"error test {i+1}", source_module_id=f"err_src_{i}")
            self.bus.publish(msg)
            # print(f"Published msg {i+1}, ID: {msg.message_id}")
            # print(f"Error counts: {self.bus._error_counts}")
            # print(f"Suspended: {self.bus._suspended_subscribers}")


        self.assertEqual(len(error_callback_tracker), MAX_CALLBACK_ERRORS + 1) # Called MAX+1 times then suspended
        self.assertIn("error_prone_mod", self.bus._suspended_subscribers)
        self.assertEqual(self.bus._error_counts["error_prone_mod"], MAX_CALLBACK_ERRORS + 1)

        # Good subscriber should have received all messages
        self.assertEqual(len(good_callback_tracker), MAX_CALLBACK_ERRORS + 2)

        # Publish another message, error_prone_mod should not be called
        last_msg = self._create_test_message("ErrorType", "after suspension")
        self.bus.publish(last_msg)
        self.assertEqual(len(error_callback_tracker), MAX_CALLBACK_ERRORS + 1) # Still same count
        self.assertEqual(len(good_callback_tracker), MAX_CALLBACK_ERRORS + 3) # Good one still gets it

        captured_output_val = sys.stdout.getvalue()
        self.assertIn("WARNING: Module 'error_prone_mod' has exceeded MAX_CALLBACK_ERRORS", captured_output_val)
        sys.stdout = self._original_stdout


    def test_unsuspend_module(self):
        sys.stdout = io.StringIO() # Capture prints
        error_callback_tracker = []
        def error_callback(message: GenericMessage):
            error_callback_tracker.append(message.message_id)
            raise ValueError("Simulated error")

        self.bus.subscribe("mod_to_suspend", "SuspendTest", error_callback)
        for i in range(MAX_CALLBACK_ERRORS + 1):
            self.bus.publish(self._create_test_message("SuspendTest", f"data {i}"))

        self.assertIn("mod_to_suspend", self.bus._suspended_subscribers)
        self.assertEqual(self.bus._error_counts["mod_to_suspend"], MAX_CALLBACK_ERRORS + 1)

        self.bus.unsuspend_module("mod_to_suspend")
        self.assertNotIn("mod_to_suspend", self.bus._suspended_subscribers)
        self.assertEqual(self.bus._error_counts["mod_to_suspend"], 0) # Error count reset

        # Module should receive messages again
        msg_after_unsuspend = self._create_test_message("SuspendTest", "data after unsuspend")
        # For this test, let's make the callback stop erroring after unsuspend for simplicity
        error_callback_tracker.clear() # Clear previous calls
        original_side_effect = error_callback.__globals__['error_callback'].side_effect # type: ignore
        error_callback.__globals__['error_callback'].side_effect = None # type: ignore

        self.bus.publish(msg_after_unsuspend)
        self.assertEqual(len(error_callback_tracker), 1)
        self.assertEqual(error_callback_tracker[0], msg_after_unsuspend.message_id)

        error_callback.__globals__['error_callback'].side_effect = original_side_effect # Restore
        sys.stdout = self._original_stdout

    # --- New Tests for Metadata Filtering ---
    def test_metadata_filtering_match(self):
        callback_meta_match = MagicMock()
        self.bus.subscribe("meta_mod", "MetaTest", callback_meta_match, metadata_filter={"region": "europe", "priority": "high"})

        msg_match = self._create_test_message("MetaTest", "data1", metadata={"region": "europe", "priority": "high", "extra_info": "detail"})
        self.bus.publish(msg_match)
        callback_meta_match.assert_called_once_with(msg_match)

    def test_metadata_filtering_no_match_value(self):
        callback_meta_no_match = MagicMock()
        self.bus.subscribe("meta_mod2", "MetaTest", callback_meta_no_match, metadata_filter={"region": "europe", "priority": "high"})

        msg_no_match_prio = self._create_test_message("MetaTest", "data2", metadata={"region": "europe", "priority": "low"})
        self.bus.publish(msg_no_match_prio)
        callback_meta_no_match.assert_not_called()

    def test_metadata_filtering_no_match_key(self):
        callback_meta_no_match_key = MagicMock()
        self.bus.subscribe("meta_mod3", "MetaTest", callback_meta_no_match_key, metadata_filter={"region": "europe", "criticality": "high"})

        msg_no_match_key = self._create_test_message("MetaTest", "data3", metadata={"region": "europe", "priority": "high"})
        self.bus.publish(msg_no_match_key)
        callback_meta_no_match_key.assert_not_called()

    def test_metadata_filtering_message_no_metadata(self):
        callback_meta_msg_no_meta = MagicMock()
        self.bus.subscribe("meta_mod4", "MetaTest", callback_meta_msg_no_meta, metadata_filter={"region": "europe"})

        msg_no_metadata = self._create_test_message("MetaTest", "data4") # No metadata field in message
        self.bus.publish(msg_no_metadata)
        callback_meta_msg_no_meta.assert_not_called()

    def test_metadata_filtering_subscriber_no_filter(self):
        callback_no_meta_filter = MagicMock()
        self.bus.subscribe("no_meta_filter_mod", "MetaTest", callback_no_meta_filter) # No metadata_filter

        msg_with_meta = self._create_test_message("MetaTest", "data5", metadata={"region": "asia"})
        msg_without_meta = self._create_test_message("MetaTest", "data6")

        self.bus.publish(msg_with_meta)
        callback_no_meta_filter.assert_called_once_with(msg_with_meta)
        callback_no_meta_filter.reset_mock()

        self.bus.publish(msg_without_meta)
        callback_no_meta_filter.assert_called_once_with(msg_without_meta)

    def test_metadata_filtering_with_type_and_func_filter(self):
        callback_combined = MagicMock()
        type_filter = "CombinedFilterType"
        func_filter = lambda msg: "special_payload" in msg.payload.get("data", "")
        meta_filter = {"status": "active"}

        self.bus.subscribe("combo_mod", type_filter, callback_combined, filter_func=func_filter, metadata_filter=meta_filter)

        # Case 1: All match
        msg1 = self._create_test_message(type_filter, {"data":"special_payload_data"}, metadata={"status":"active", "source":"test"})
        self.bus.publish(msg1)
        callback_combined.assert_called_once_with(msg1)
        callback_combined.reset_mock()

        # Case 2: Type mismatch
        msg2 = self._create_test_message("WrongType", {"data":"special_payload_data"}, metadata={"status":"active"})
        self.bus.publish(msg2)
        callback_combined.assert_not_called()

        # Case 3: Func filter mismatch
        msg3 = self._create_test_message(type_filter, {"data":"normal_payload_data"}, metadata={"status":"active"})
        self.bus.publish(msg3)
        callback_combined.assert_not_called()

        # Case 4: Metadata filter mismatch
        msg4 = self._create_test_message(type_filter, {"data":"special_payload_data"}, metadata={"status":"inactive"})
        self.bus.publish(msg4)
        callback_combined.assert_not_called()

    # Re-add other existing tests from the original file, ensuring they are compatible
    # (Most should be, as they test fundamental pub/sub and basic filtering)
    def test_publish_to_correct_message_type_subscribers_only(self): # Copied from original
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

    def test_publish_no_subscribers(self): # Copied from original
        message = self._create_test_message("TypeC", "lonely data")
        try:
            self.bus.publish(message)
        except Exception as e:
            self.fail(f"Publishing with no subscribers raised an exception: {e}")
        self.mock_callback_module1_typeA.assert_not_called()

    def test_unsubscribe(self): # Copied from original (basic)
        # Note: unsubscribe now matches module_id, message_type, callback, filter_func, and metadata_filter
        # This basic test will still work if only module_id, message_type, callback are provided
        # and the subscription was made with no filters.
        self.bus.subscribe("module1", "TypeA", self.mock_callback_module1_typeA)
        # For precise unsubscription of this specific registration:
        self.bus.unsubscribe("module1", "TypeA", self.mock_callback_module1_typeA)
        message = self._create_test_message("TypeA", "data for unsubscribed")
        self.bus.publish(message)
        self.mock_callback_module1_typeA.assert_not_called()

    def test_get_subscribers_for_type(self): # Adapted for new tuple structure
        self.assertEqual(len(self.bus.get_subscribers_for_type("TypeNonExistent")), 0)
        filter_fn = lambda msg: True
        meta_filter_fn = {"key": "value"}
        self.bus.subscribe("module1", "TypeX", self.mock_callback_module1_typeA, filter_func=filter_fn, metadata_filter=meta_filter_fn)
        subscribers = self.bus.get_subscribers_for_type("TypeX")
        self.assertEqual(len(subscribers), 1)
        self.assertEqual(subscribers[0][0], "module1") # module_id
        self.assertEqual(subscribers[0][1], self.mock_callback_module1_typeA) # callback
        self.assertEqual(subscribers[0][2], filter_fn) # filter_func
        self.assertEqual(subscribers[0][3], meta_filter_fn) # metadata_filter

    def test_original_error_handling_in_callback_logging(self): # Renamed from test_improved_error_handling_in_callback
        faulty_callback = MagicMock(side_effect=ValueError("Callback custom error!"))
        self.bus.subscribe("faulty_module_orig", "TypeA_err", faulty_callback)

        message = self._create_test_message("TypeA_err", "test data for error handling")

        sys.stdout = captured_output = io.StringIO()
        self.bus.publish(message)
        sys.stdout = self._original_stdout
        output_str = captured_output.getvalue()

        faulty_callback.assert_called_once_with(message)
        self.assertIn("ERROR: Callback error in module 'faulty_module_orig'", output_str)
        self.assertIn("Exception: ValueError('Callback custom error!')", output_str)


if __name__ == '__main__':
    # If running specific async tests directly, you might need:
    # asyncio.run(TestMessageBus().test_asynchronous_dispatch_async_callback())
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
