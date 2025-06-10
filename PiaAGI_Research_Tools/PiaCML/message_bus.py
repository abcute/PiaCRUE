from typing import Dict, Callable, List, Any, DefaultDict, Optional
from collections import defaultdict
import traceback # Added
import asyncio
from datetime import datetime

# Attempt relative import, common for package structures
try:
    from .core_messages import GenericMessage
except ImportError:
    # Fallback for scenarios where the script might be run directly
    # or the environment setup makes relative imports tricky without full package install
    from core_messages import GenericMessage

MAX_CALLBACK_ERRORS = 3

class MessageBus:
    """
    A message bus for inter-module communication within PiaCML.
    Modules can subscribe to specific message types and publish messages to the bus.
    Enhanced with filtering, asynchronous dispatch, and improved error handling.
    """
    def __init__(self):
        """
        Initializes the MessageBus.
        _subscribers stores: message_type -> list of (module_id, callback, filter_func, metadata_filter)
        """
        # Stores subscribers: message_type -> list of (module_id, callback, filter_func, metadata_filter)
        self._subscribers: DefaultDict[str, List[tuple[str, Callable[[GenericMessage], Any], Optional[Callable[[GenericMessage], bool]], Optional[Dict[str, Any]]]]] = defaultdict(list)
        self._error_counts: DefaultDict[str, int] = defaultdict(int)
        self._suspended_subscribers: Dict[str, datetime] = {}
        # print("MessageBus (Enhanced) initialized.") # Optional

    def subscribe(self,
                  module_id: str,
                  message_type: str,
                  callback: Callable[[GenericMessage], Any], # Can be sync or async
                  filter_func: Optional[Callable[[GenericMessage], bool]] = None,
                  metadata_filter: Optional[Dict[str, Any]] = None):
        """
        Subscribes a module to a specific message type, with optional filters.

        Args:
            module_id: The identifier of the subscribing module.
            message_type: The type of message to subscribe to.
            callback: The function (sync or async) to call.
            filter_func: Optional function, message content based.
            metadata_filter: Optional dict, message metadata based.
        """
        # print(f"Module '{module_id}' attempting to subscribe to '{message_type}' with filter: {filter_func is not None}, metadata_filter: {metadata_filter is not None}") # Optional

        # Avoid duplicate subscriptions
        for sub_module_id, sub_callback, sub_filter, sub_meta_filter in self._subscribers[message_type]:
            if sub_module_id == module_id and sub_callback == callback and sub_filter == filter_func and sub_meta_filter == metadata_filter:
                # print(f"Module '{module_id}' already subscribed to '{message_type}' with this callback and filters.") # Optional
                return
        self._subscribers[message_type].append((module_id, callback, filter_func, metadata_filter))
        # print(f"Module '{module_id}' successfully subscribed to '{message_type}'.") # Optional

    async def _execute_callback(self, callback: Callable[[GenericMessage], Any], message: GenericMessage):
        """
        Executes a callback, awaiting it if it's an coroutine.
        Handles errors during execution.
        """
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(message)
            else:
                callback(message)
        except Exception as e:
            # This error will be caught by the caller (publish method)
            # and handled there for suspension logic.
            raise e

    def publish(self, message: GenericMessage, dispatch_mode: str = "synchronous"):
        """Publishes a message to all relevant subscribed modules.
        Handles different dispatch modes and error tracking/suspension.
        """
        message_type = message.message_type
        # print(f"Publishing message type '{message_type}' from '{message.source_module_id}' (mode: {dispatch_mode})") # Optional

        subscribers_to_notify = list(self._subscribers.get(message_type, []))

        if not subscribers_to_notify:
            # print(f"No subscribers for message type '{message_type}'.") # Optional
            return

        for module_id, callback, filter_func, metadata_filter in subscribers_to_notify:
            if module_id in self._suspended_subscribers:
                # print(f"Skipping suspended module '{module_id}' for message '{message.message_id}'.") # Optional
                continue

            try:
                if filter_func and not filter_func(message):
                    # print(f"  Filter skipped notification for module '{module_id}' on message '{message.message_id}'") # Optional
                    continue

                if metadata_filter:
                    if not message.metadata: # If message has no metadata, it cannot satisfy the filter
                        # print(f"  Metadata filter skipped for '{module_id}' (no metadata in message) on message '{message.message_id}'") # Optional
                        continue
                    match = all(item in message.metadata.items() for item in metadata_filter.items())
                    if not match:
                        # print(f"  Metadata filter skipped for '{module_id}' (metadata mismatch) on message '{message.message_id}'") # Optional
                        continue

                # print(f"  Notifying module '{module_id}' for message type '{message_type}'") # Optional
                if dispatch_mode == "asynchronous":
                    # print(f"  Dispatching asynchronously to '{module_id}' for message '{message.message_id}'.") # Optional
                    asyncio.create_task(self._execute_callback(callback, message))
                else: # Synchronous dispatch
                    if asyncio.iscoroutinefunction(callback):
                        print(f"WARNING: Coroutine callback {callback.__name__} for module '{module_id}' called in synchronous mode. This will block or not execute as intended. Consider using dispatch_mode='asynchronous'.")
                        # Directly calling an async function from sync code will return a coroutine object,
                        # not run it as awaited. This is a simplification to fix syntax errors.
                        # Proper handling of async callbacks in sync mode is complex and might require
                        # running an event loop or using threading if true synchronous execution is needed.
                        callback(message)
                    else: # This is for regular synchronous callbacks
                        callback(message) # Regular synchronous call
            except Exception as e:
                err_type = type(e).__name__
                tb_str = traceback.format_exc()
                print(f"ERROR: Callback error in module '{module_id}' for message type '{message_type}' (msg_id: {message.message_id}). Exception: {err_type}('{e}'). Traceback:\n{tb_str}")
                self._error_counts[module_id] += 1
                if self._error_counts[module_id] > MAX_CALLBACK_ERRORS:
                    if module_id not in self._suspended_subscribers:
                        self._suspended_subscribers[module_id] = datetime.now()
                        print(f"WARNING: Module '{module_id}' has exceeded MAX_CALLBACK_ERRORS ({MAX_CALLBACK_ERRORS}) and has been suspended.")

    def unsuspend_module(self, module_id: str):
        """Explicitly unsuspends a module."""
        if module_id in self._suspended_subscribers:
            del self._suspended_subscribers[module_id]
            self._error_counts[module_id] = 0 # Reset error count
            print(f"Module '{module_id}' has been unsuspended and error count reset.")
        else:
            print(f"Module '{module_id}' is not currently suspended.")


    def unsubscribe(self, module_id: str, message_type: str, callback: Callable[[GenericMessage], Any]):
        """
        Unsubscribes a module from a specific message type and callback.
        It removes subscriptions matching module_id and callback.
        The filter_func and metadata_filter are also considered for a more precise match,
        but for simplicity, if they are not provided to unsubscribe, it might remove
        a subscription that had filters if the module_id and callback match.
        For a fully precise unsubscribe, all original subscription parameters should be provided.
        """
        if message_type in self._subscribers:
            original_count = len(self._subscribers[message_type])
            # More precise unsubscription would require matching filter_func and metadata_filter as well.
            # For this version, we'll keep it simple: if callback and module_id match, remove.
            # This means if you subscribe the same callback with different filters, this might remove them all.
            self._subscribers[message_type] = [
                sub for sub in self._subscribers[message_type]
                if not (sub[0] == module_id and sub[1] == callback)
            ]
            if len(self._subscribers[message_type]) < original_count:
                pass
                # print(f"Module '{module_id}' (callback: {callback.__name__}) unsubscribed from '{message_type}'.") # Optional
        # else:
            # print(f"No subscribers for message type '{message_type}' to try unsubscribing module '{module_id}'.") # Optional

    def get_subscribers_for_type(self, message_type: str) -> List[tuple[str, Callable[[GenericMessage], Any], Optional[Callable[[GenericMessage], bool]], Optional[Dict[str, Any]]]]:
        """
        Returns a list of (module_id, callback, filter_func, metadata_filter) tuples for a given message type.
        """
        return list(self._subscribers.get(message_type, [])) # Return a copy

if __name__ == '__main__':
    # Example Usage (manual test)
    from core_messages import PerceptDataPayload # Assuming core_messages.py is in the same directory for direct run
    # import datetime # Already imported at top
    import uuid
    import time # For sleep

    print("--- MessageBus Example Usage ---")
    bus = MessageBus()

    # --- Define Callbacks ---
    def module_a_sync_listener(message: GenericMessage):
        print(f"Module A (Sync) received: Type='{message.message_type}', Payload='{message.payload}', Source='{message.source_module_id}', Metadata: {message.metadata}")

    async def module_b_async_listener(message: GenericMessage):
        print(f"Module B (Async) task started for msg: {message.message_id[:8]}")
        await asyncio.sleep(0.01) # Simulate async work
        print(f"Module B (Async) received: Type='{message.message_type}', Payload='{message.payload}', Source='{message.source_module_id}', Metadata: {message.metadata}")

    error_count_for_c = 0
    def module_c_error_listener(message: GenericMessage):
        global error_count_for_c
        error_count_for_c += 1
        print(f"Module C (ErrorSim) trying to process msg: {message.message_id[:8]}. Error attempt {error_count_for_c}.")
        if error_count_for_c <= MAX_CALLBACK_ERRORS + 1: # Will fail enough times to get suspended
             raise ValueError(f"Simulated processing error in Module C - attempt {error_count_for_c}")
        print(f"Module C (ErrorSim) processed message successfully after {error_count_for_c} attempts (now unsuspended).")


    def module_d_metadata_listener(message: GenericMessage):
        print(f"Module D (MetadataListener) received: Type='{message.message_type}', Payload='{message.payload}', Metadata: {message.metadata}")


    # --- Subscribe Modules ---
    print("\n--- Subscribing Modules ---")
    bus.subscribe(module_id="ModA", message_type="SYSTEM_STATUS", callback=module_a_sync_listener)
    bus.subscribe(module_id="ModB_Async", message_type="SYSTEM_STATUS", callback=module_b_async_listener)
    bus.subscribe(module_id="ModC_Error", message_type="SYSTEM_STATUS", callback=module_c_error_listener)

    # Metadata subscription
    bus.subscribe(module_id="ModD_MetaImportant", message_type="USER_COMMAND",
                  callback=module_d_metadata_listener,
                  metadata_filter={"importance": "high"})
    bus.subscribe(module_id="ModD_MetaAny", message_type="USER_COMMAND",
                  callback=module_d_metadata_listener) # Listens to any USER_COMMAND

    # --- Publish Messages ---
    print("\n--- Publishing Initial SYSTEM_STATUS (Sync) ---")
    status_payload = {"status": "nominal", "load": 0.3}
    status_message_sync = GenericMessage(
        source_module_id="SystemMonitor",
        message_type="SYSTEM_STATUS",
        payload=status_payload,
        metadata={"region": "eu-west-1", "priority": "medium"}
    )
    bus.publish(status_message_sync, dispatch_mode="synchronous")

    print("\n--- Publishing SYSTEM_STATUS (Async) ---")
    status_payload_async = {"status": "degraded", "load": 0.8}
    status_message_async = GenericMessage(
        source_module_id="SystemMonitor",
        message_type="SYSTEM_STATUS",
        payload=status_payload_async,
        metadata={"region": "us-east-1", "priority": "high"}
    )
    bus.publish(status_message_async, dispatch_mode="asynchronous")


    # --- Demonstrate Error Handling and Suspension ---
    print("\n--- Demonstrating Error Handling & Suspension for ModC_Error ---")
    # ModC_Error will fail for SYSTEM_STATUS messages
    print(f"MAX_CALLBACK_ERRORS = {MAX_CALLBACK_ERRORS}")
    for i in range(MAX_CALLBACK_ERRORS + 2): # Trigger suspension and one more
        print(f"\nPublishing error-triggering message attempt {i+1} for ModC_Error...")
        error_trigger_msg = GenericMessage(
            source_module_id="ErrorHandlerTester",
            message_type="SYSTEM_STATUS",
            payload={"test_attempt": i+1},
            metadata={"iteration": str(i+1)}
        )
        bus.publish(error_trigger_msg, dispatch_mode="synchronous") # ModB_Async will also get this
        if f"ModC_Error" in bus._suspended_subscribers:
            print(f"  CONFIRMED: ModC_Error is now in _suspended_subscribers at attempt {i+1}.")
        time.sleep(0.02) # Brief pause to allow async tasks to print if any

    print(f"\nError counts: {dict(bus._error_counts)}")
    print(f"Suspended subscribers: {bus._suspended_subscribers}")

    print("\n--- Publishing another SYSTEM_STATUS (ModC_Error should be suspended) ---")
    final_status_msg = GenericMessage(source_module_id="SystemMonitor", message_type="SYSTEM_STATUS", payload={"status": "final check"}, metadata={"final": "true"})
    bus.publish(final_status_msg, dispatch_mode="synchronous") # ModC should be skipped

    # --- Demonstrate Unsuspension ---
    print("\n--- Demonstrating Unsuspension for ModC_Error ---")
    bus.unsuspend_module("ModC_Error")
    print(f"Suspended subscribers after unsuspend: {bus._suspended_subscribers}")
    print(f"Error count for ModC_Error after unsuspend: {bus._error_counts.get('ModC_Error', 0)}")

    # ModC_Error's internal error_count_for_c is still high, so it might fail again if not reset,
    # but the bus's own error tracking for it is reset. Let's reset its internal counter for the test.
    error_count_for_c = 0 # Resetting global error counter for ModC for this test
    print("\n--- Publishing SYSTEM_STATUS again (ModC_Error should now process) ---")
    bus.publish(final_status_msg, dispatch_mode="synchronous")


    # --- Demonstrate Metadata Filtering ---
    print("\n--- Demonstrating Metadata Filtering for USER_COMMAND ---")
    cmd_high_importance = GenericMessage(
        source_module_id="Commander",
        message_type="USER_COMMAND",
        payload={"command": "shutdown", "args": ["now"]},
        metadata={"importance": "high", "user": "admin"}
    )
    cmd_low_importance = GenericMessage(
        source_module_id="Commander",
        message_type="USER_COMMAND",
        payload={"command": "query_status", "args": []},
        metadata={"importance": "low", "user": "guest"}
    )
    cmd_no_meta = GenericMessage(
        source_module_id="Commander",
        message_type="USER_COMMAND",
        payload={"command": "ping"}
        # No metadata
    )

    print("\nPublishing USER_COMMAND with 'importance': 'high': (ModD_MetaImportant and ModD_MetaAny should receive)")
    bus.publish(cmd_high_importance, dispatch_mode="synchronous")

    print("\nPublishing USER_COMMAND with 'importance': 'low': (Only ModD_MetaAny should receive)")
    bus.publish(cmd_low_importance, dispatch_mode="synchronous")

    print("\nPublishing USER_COMMAND with no metadata: (Only ModD_MetaAny should receive)")
    bus.publish(cmd_no_meta, dispatch_mode="synchronous")


    # --- Allow async tasks to complete ---
    # This is important if the script ends soon after publishing async messages.
    # In a long-running application, the event loop would manage this naturally.
    print("\n--- Waiting for async tasks to complete (approx 0.1s)... ---")
    # This is a simplistic way to wait. In a real app, you'd manage the asyncio loop.
    # If publish was async, we could gather tasks. Here, tasks are fire-and-forget.
    # We need to find a running loop or run one.
    async def main_async_wait():
        await asyncio.sleep(0.1) # Wait for tasks created by create_task

    # Check if an event loop is already running. If so, just sleep.
    # If not, run the main_async_wait.
    try:
        loop = asyncio.get_running_loop()
        print("Async loop already running. Main thread will sleep to allow tasks to proceed.")
        # If loop is running, tasks should be processing. We might not need to do anything special here
        # beyond a simple time.sleep if the main thread would otherwise exit.
        # However, create_task schedules on the current loop. If this __main__ is not async
        # and doesn't manage a loop, the tasks might not run as expected without explicit loop handling.
        # The print statements within async callbacks will show if they ran.
        # For this example, a simple time.sleep in the main thread might be enough for demonstration.
        time.sleep(0.2) # Increased time to allow more async tasks to show up
    except RuntimeError: # No running event loop
        print("No async loop running. Running a brief one for cleanup.")
        asyncio.run(main_async_wait())


    print("\n--- Final Check of Subscribers (ModB_Async should still be there for SYSTEM_STATUS) ---")
    system_status_subs = bus.get_subscribers_for_type('SYSTEM_STATUS')
    print(f"Subscribers for SYSTEM_STATUS: {len(system_status_subs)}")
    for sub in system_status_subs:
        print(f"  Module: {sub[0]}, Callback: {sub[1].__name__}")


    print("\nExample Usage Complete.")
