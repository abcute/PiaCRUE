from typing import Dict, Callable, List, Any, DefaultDict, Optional
from collections import defaultdict
import traceback # Added

# Attempt relative import, common for package structures
try:
    from .core_messages import GenericMessage
except ImportError:
    # Fallback for scenarios where the script might be run directly
    # or the environment setup makes relative imports tricky without full package install
    from core_messages import GenericMessage

class MessageBus:
    """
    A message bus for inter-module communication within PiaCML.
    Modules can subscribe to specific message types and publish messages to the bus.
    Enhanced with filtering, conceptual asynchronous dispatch, and improved error handling.
    """
    def __init__(self):
        """
        Initializes the MessageBus.
        _subscribers is a dictionary where keys are message_types (str)
        and values are lists of tuples, each containing
        (module_id, callback_function, optional_filter_function).
        """
        # Stores subscribers: message_type -> list of (module_id, callback, filter_func)
        self._subscribers: DefaultDict[str, List[tuple[str, Callable[[GenericMessage], None], Optional[Callable[[GenericMessage], bool]]]]] = defaultdict(list)
        # print("MessageBus (Phase 2 Enhanced) initialized.") # Optional

    def subscribe(self,
                  module_id: str,
                  message_type: str,
                  callback: Callable[[GenericMessage], None],
                  filter_func: Optional[Callable[[GenericMessage], bool]] = None):
        """
        Subscribes a module to a specific message type, with an optional filter.

        Args:
            module_id: The identifier of the subscribing module.
            message_type: The type of message to subscribe to (e.g., "PerceptData").
            callback: The function to call when a message of this type is published
                      and passes the filter (if any).
            filter_func: An optional function that takes a GenericMessage and returns True
                         if the callback should be invoked, False otherwise.
        """
        # print(f"Module '{module_id}' attempting to subscribe to '{message_type}' with filter: {filter_func is not None}") # Optional

        # Avoid duplicate subscriptions for the same module_id, callback, AND filter_func
        for sub_module_id, sub_callback, sub_filter in self._subscribers[message_type]:
            if sub_module_id == module_id and sub_callback == callback and sub_filter == filter_func:
                # print(f"Module '{module_id}' already subscribed to '{message_type}' with this callback and filter.") # Optional
                return
        self._subscribers[message_type].append((module_id, callback, filter_func))
        # print(f"Module '{module_id}' successfully subscribed to '{message_type}'.") # Optional

    def publish(self, message: GenericMessage, dispatch_mode: str = "synchronous"):
        """
        Publishes a message to all relevant subscribed modules.

        Args:
            message: The GenericMessage object to publish.
            dispatch_mode: "synchronous" or "asynchronous". For PoC, "asynchronous"
                           is logged but executed synchronously.
        """
        message_type = message.message_type
        # print(f"Publishing message type '{message_type}' from '{message.source_module_id}' (mode: {dispatch_mode})") # Optional

        subscribers_to_notify = list(self._subscribers.get(message_type, []))

        if not subscribers_to_notify:
            # print(f"No subscribers for message type '{message_type}'.") # Optional
            return

        for module_id, callback, filter_func in subscribers_to_notify:
            try:
                if filter_func:
                    if not filter_func(message):
                        # print(f"  Filter skipped notification for module '{module_id}' on message '{message.message_id}'") # Optional
                        continue # Skip this callback if filter returns False

                if dispatch_mode == "asynchronous":
                    print(f"  INFO: Asynchronous dispatch requested for {module_id} on message '{message.message_id}' (actual async execution deferred for PoC).")
                    # In a real implementation:
                    # asyncio.create_task(callback(message)) or use a thread pool executor

                # print(f"  Notifying module '{module_id}' for message type '{message_type}'") # Optional
                callback(message)
            except Exception as e:
                err_type = type(e).__name__
                tb_str = traceback.format_exc()
                print(f"ERROR: Callback error in module '{module_id}' for message type '{message_type}' (msg_id: {message.message_id}). Exception: {err_type}('{e}'). Traceback:\n{tb_str}")
                # Future: Add notification to an admin/monitoring component or
                # mechanism to temporarily disable consistently failing callbacks.

    def unsubscribe(self, module_id: str, message_type: str, callback: Callable[[GenericMessage], None]):
        """
        Unsubscribes a module from a specific message type and callback.
        For this PoC, it removes all subscriptions matching module_id and callback,
        regardless of the filter function they were subscribed with.
        A more precise unsubscribe would also take the filter_func if needed.

        Args:
            module_id: The identifier of the unsubscribing module.
            message_type: The type of message to unsubscribe from.
            callback: The specific callback function to remove.
        """
        if message_type in self._subscribers:
            original_count = len(self._subscribers[message_type])
            # Remove entries where module_id and callback match. The filter is not considered for removal in this version.
            self._subscribers[message_type] = [
                (sub_mod_id, sub_call, sub_filter) for sub_mod_id, sub_call, sub_filter in self._subscribers[message_type]
                if not (sub_mod_id == module_id and sub_call == callback)
            ]
            if len(self._subscribers[message_type]) < original_count:
                pass
                # print(f"Module '{module_id}' (callback: {callback.__name__}) unsubscribed from '{message_type}'.") # Optional
        # else:
            # print(f"No subscribers for message type '{message_type}' to try unsubscribing module '{module_id}'.") # Optional

    def get_subscribers_for_type(self, message_type: str) -> List[tuple[str, Callable[[GenericMessage], None], Optional[Callable[[GenericMessage], bool]]]]:
        """
        Returns a list of (module_id, callback, filter_func) tuples for a given message type.
        Mainly for introspection or debugging.
        """
        return list(self._subscribers.get(message_type, [])) # Return a copy

if __name__ == '__main__':
    # Example Usage (manual test)
    from core_messages import PerceptDataPayload # Assuming core_messages.py is in the same directory for direct run
    import datetime
    import uuid

    print("--- MessageBus Example Usage ---")
    bus = MessageBus()

    # Define some callback functions
    def module_a_listener(message: GenericMessage):
        print(f"Module A received: Type='{message.message_type}', Payload='{message.payload}', Source='{message.source_module_id}'")

    def module_b_listener_percept(message: GenericMessage):
        if isinstance(message.payload, PerceptDataPayload):
            print(f"Module B (Percept Listener) received Percept: Modality='{message.payload.modality}', Content='{message.payload.content}'")
        else:
            print(f"Module B (Percept Listener) received unexpected payload type for PerceptData message: {type(message.payload)}")

    def module_b_listener_general(message: GenericMessage):
        print(f"Module B (General Listener) received: Type='{message.message_type}', Payload='{message.payload}'")


    # Subscribe modules
    bus.subscribe(module_id="ModA", message_type="SYSTEM_STATUS", callback=module_a_listener)
    bus.subscribe(module_id="ModB_Percept", message_type="PerceptData", callback=module_b_listener_percept)
    bus.subscribe(module_id="ModB_General", message_type="SYSTEM_STATUS", callback=module_b_listener_general)
    bus.subscribe(module_id="ModA", message_type="PerceptData", callback=module_a_listener) # ModA also listens to PerceptData

    # Publish some messages
    print("\n--- Publishing Messages ---")
    status_payload = {"status": "nominal", "load": 0.3}
    status_message = GenericMessage(source_module_id="SystemMonitor", message_type="SYSTEM_STATUS", payload=status_payload)
    bus.publish(status_message)

    percept_content = {"detected_objects": ["cat", "mat"], "confidence": 0.88}
    percept_payload_obj = PerceptDataPayload(
        percept_id=str(uuid.uuid4()),
        modality="visual",
        content=percept_content,
        source_timestamp=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(milliseconds=100)
    )
    percept_message = GenericMessage(source_module_id="VisionSystem", message_type="PerceptData", payload=percept_payload_obj)
    bus.publish(percept_message)

    # Test duplicate subscription avoidance
    print("\n--- Testing Duplicate Subscription ---")
    bus.subscribe(module_id="ModA", message_type="SYSTEM_STATUS", callback=module_a_listener) # Already subscribed
    # Check number of subscribers for SYSTEM_STATUS (should be 2: ModA's module_a_listener, ModB_General's module_b_listener_general)
    print(f"Subscribers for SYSTEM_STATUS: {len(bus.get_subscribers_for_type('SYSTEM_STATUS'))}") # Expected 2

    # Test unsubscribe
    print("\n--- Testing Unsubscribe ---")
    bus.unsubscribe(module_id="ModA", message_type="SYSTEM_STATUS", callback=module_a_listener)
    print(f"Subscribers for SYSTEM_STATUS after ModA unsub: {len(bus.get_subscribers_for_type('SYSTEM_STATUS'))}") # Expected 1
    bus.publish(status_message) # ModA should not receive this status_message now

    print("\nExample Usage Complete.")
