from typing import Dict, Callable, List, Any, DefaultDict
from collections import defaultdict

# Attempt relative import, common for package structures
try:
    from .core_messages import GenericMessage
except ImportError:
    # Fallback for scenarios where the script might be run directly
    # or the environment setup makes relative imports tricky without full package install
    from core_messages import GenericMessage

class MessageBus:
    """
    A simple message bus for inter-module communication within PiaCML.
    Modules can subscribe to specific message types and publish messages to the bus.
    """
    def __init__(self):
        """
        Initializes the MessageBus.
        _subscribers is a dictionary where keys are message_types (str)
        and values are lists of tuples, each containing (module_id, callback_function).
        """
        # Stores subscribers: message_type -> list of (module_id, callback_function)
        self._subscribers: DefaultDict[str, List[tuple[str, Callable[[GenericMessage], None]]]] = defaultdict(list)
        # print("MessageBus initialized.") # Optional: for debugging initialization

    def subscribe(self, module_id: str, message_type: str, callback: Callable[[GenericMessage], None]):
        """
        Subscribes a module to a specific message type.

        Args:
            module_id: The identifier of the subscribing module.
            message_type: The type of message to subscribe to (e.g., "PerceptData").
            callback: The function to call when a message of this type is published.
                      The callback should accept a GenericMessage object.
        """
        # print(f"Module '{module_id}' attempting to subscribe to message type '{message_type}'") # Optional

        # Avoid duplicate subscriptions for the same module_id and callback to the same message_type
        for sub_module_id, sub_callback in self._subscribers[message_type]:
            if sub_module_id == module_id and sub_callback == callback:
                # print(f"Module '{module_id}' already subscribed to '{message_type}' with this callback.") # Optional
                return
        self._subscribers[message_type].append((module_id, callback))
        # print(f"Module '{module_id}' successfully subscribed to '{message_type}'.") # Optional

    def publish(self, message: GenericMessage):
        """
        Publishes a message to all subscribed modules for that message type.

        Args:
            message: The GenericMessage object to publish.
        """
        message_type = message.message_type
        # print(f"Publishing message type '{message_type}' from '{message.source_module_id}' with ID '{message.message_id}'") # Optional

        # Iterate over a copy of the subscriber list for safety,
        # in case a callback tries to subscribe/unsubscribe during iteration.
        subscribers_to_notify = list(self._subscribers.get(message_type, []))

        if not subscribers_to_notify:
            # print(f"No subscribers for message type '{message_type}'.") # Optional
            return

        for module_id, callback in subscribers_to_notify:
            try:
                # print(f"  Notifying module '{module_id}' for message type '{message_type}'") # Optional
                callback(message)
            except Exception as e:
                print(f"Error in callback for module '{module_id}' processing message type '{message_type}' (msg_id: {message.message_id}): {e}")
                # Potentially add more robust error handling or logging here,
                # e.g., logging the traceback.

    def unsubscribe(self, module_id: str, message_type: str, callback: Callable[[GenericMessage], None]):
        """
        Unsubscribes a module from a specific message type and callback.

        Args:
            module_id: The identifier of the unsubscribing module.
            message_type: The type of message to unsubscribe from.
            callback: The specific callback function to remove.
        """
        if message_type in self._subscribers:
            original_count = len(self._subscribers[message_type])
            self._subscribers[message_type] = [
                (sub_mod_id, sub_call) for sub_mod_id, sub_call in self._subscribers[message_type]
                if not (sub_mod_id == module_id and sub_call == callback)
            ]
            if len(self._subscribers[message_type]) < original_count:
                pass
                # print(f"Module '{module_id}' unsubscribed from '{message_type}' with specific callback.") # Optional
            # else:
                # print(f"Module '{module_id}' with callback not found for unsubscribe from '{message_type}'.") # Optional
        # else:
            # print(f"No subscribers for message type '{message_type}' to unsubscribe module '{module_id}'.") # Optional


    def get_subscribers_for_type(self, message_type: str) -> List[tuple[str, Callable[[GenericMessage], None]]]:
        """
        Returns a list of (module_id, callback) tuples for a given message type.
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
