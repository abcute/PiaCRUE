from typing import Any, Dict, List, Optional
import datetime # Added for source_timestamp
import uuid # For module_id generation

try:
    from .base_perception_module import BasePerceptionModule
    from .message_bus import MessageBus # Added
    from .core_messages import GenericMessage, PerceptDataPayload # Added
except ImportError:
    # Fallback for scenarios where the relative import might fail
    from base_perception_module import BasePerceptionModule
    # If MessageBus and core_messages are also in the same flat directory for fallback:
    try:
        from message_bus import MessageBus
        from core_messages import GenericMessage, PerceptDataPayload
    except ImportError: # If they are truly missing during fallback
        MessageBus = None
        GenericMessage = None
        PerceptDataPayload = None


class ConcretePerceptionModule(BasePerceptionModule):
    """
    A basic, concrete implementation of the BasePerceptionModule.
    This version performs very simple keyword spotting for text inputs to extract
    conceptual 'objects' and 'actions'. For dictionary inputs (mocking other
    modalities), it wraps them in a standard perceptual representation.
    It can also publish processed percepts to a MessageBus.
    """

    def __init__(self,
                 message_bus: Optional[MessageBus] = None,
                 module_id: str = f"ConcretePerceptionModule_{str(uuid.uuid4())[:8]}"):
        """
        Initializes the ConcretePerceptionModule.

        Args:
            message_bus: An optional instance of MessageBus for publishing percepts.
            module_id: A unique identifier for this module instance.
        """
        self._supported_modalities = ["text", "dict_mock"] # dict_mock for pre-structured data
        self._processing_log: List[str] = []
        self._message_bus = message_bus
        self._module_id = module_id
        print(f"ConcretePerceptionModule '{self._module_id}' initialized. Message bus {'configured' if self._message_bus else 'not configured'}.")

    def process_sensory_input(self, raw_input: Any, modality: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Processes raw sensory input into a structured perceptual representation.
        """
        self._processing_log.append(f"Received input via {modality}: {str(raw_input)[:100]}")
        print(f"ConcretePerceptionModule: Processing input from modality '{modality}'.")

        percept = {
            "raw_input": raw_input,
            "modality": modality,
            "processed_representation": {}, # To be filled
            "metadata": context or {}
        }

        if modality == "text" and isinstance(raw_input, str):
            text_lower = raw_input.lower()
            entities_found = []
            actions_found = []

            # Very simple keyword spotting
            if "apple" in text_lower: entities_found.append({"type": "fruit", "name": "apple"})
            if "ball" in text_lower: entities_found.append({"type": "toy", "name": "ball"})
            if "user" in text_lower: entities_found.append({"type": "agent", "name": "user"})
            if "pia" in text_lower: entities_found.append({"type": "agent", "name": "PiaAGI"})

            if "give" in text_lower or "pass" in text_lower: actions_found.append({"type": "transfer", "verb": "give/pass"})
            if "see" in text_lower or "look" in text_lower: actions_found.append({"type": "observe", "verb": "see/look"})
            if "greet" in text_lower or "hello" in text_lower or "hi" in text_lower: actions_found.append({"type": "social_interaction", "verb": "greet"})

            percept["processed_representation"] = {
                "type": "linguistic_analysis",
                "text": raw_input,
                "entities": entities_found,
                "actions": actions_found,
                "sentiment_conceptual": "neutral" # Placeholder
            }
        elif modality == "dict_mock" and isinstance(raw_input, dict):
            # Assumes raw_input is already a somewhat structured dictionary
            percept["processed_representation"] = {
                "type": "structured_data",
                "data": raw_input
            }
        else:
            percept["processed_representation"] = {
                "type": "unsupported_modality",
                "error": f"Modality '{modality}' or input type not supported by this basic processor."
            }
            print(f"ConcretePerceptionModule: Unsupported modality '{modality}' or input type.")

        print(f"ConcretePerceptionModule: Generated percept: {percept}")
        return percept

    def process_and_publish_stimulus(self, raw_stimulus: Any, modality: str, source_timestamp: datetime.datetime) -> Optional[str]:
        """
        Processes a raw stimulus and publishes it as a PerceptData message via the message bus.

        Args:
            raw_stimulus: The raw input data.
            modality: The modality of the stimulus (e.g., "text", "visual").
            source_timestamp: The timestamp when the original stimulus was captured/generated.

        Returns:
            The message_id of the published GenericMessage if successful, otherwise None.
        """
        if not self._message_bus:
            print(f"Warning ({self._module_id}): No message bus configured. Cannot publish.")
            return None

        if not PerceptDataPayload or not GenericMessage: # Check if imports failed during fallback
            print(f"Error ({self._module_id}): Core message types not available. Cannot publish.")
            return None

        # Call process_sensory_input to get the structured_percept
        structured_percept = self.process_sensory_input(
            raw_stimulus,
            modality,
            {"source_timestamp_original": source_timestamp, "publisher_module_id": self._module_id}
        )

        processed_representation = structured_percept.get("processed_representation")
        content_payload: Dict[str, Any]

        # Check if processing failed or returned an error structure
        if not processed_representation or \
           (isinstance(processed_representation, dict) and "error" in processed_representation) or \
           (isinstance(processed_representation, dict) and "unsupported_modality" in processed_representation.get("type", "")):
            error_details = "Unknown processing error"
            if isinstance(processed_representation, dict):
                error_details = processed_representation.get("error", error_details)
            content_payload = {
                "error": "processing_failed",
                "details": error_details,
                "original_stimulus_type": str(type(raw_stimulus)),
                "original_modality": modality
            }
            print(f"Warning ({self._module_id}): Processing failed or resulted in error for modality '{modality}'. Payload will indicate error.")
        else:
            content_payload = processed_representation

        payload = PerceptDataPayload(
            modality=modality,
            content=content_payload, # This is the processed_representation or error dict
            source_timestamp=source_timestamp,
            metadata=structured_percept.get("metadata", {}) # Carry over any metadata from processing
        )

        msg = GenericMessage(
            source_module_id=self._module_id,
            message_type="PerceptData",
            payload=payload
        )

        try:
            self._message_bus.publish(msg)
            print(f"ConcretePerceptionModule ({self._module_id}): Published PerceptData message '{msg.message_id}' for modality '{modality}'.")
            return msg.message_id
        except Exception as e:
            print(f"Error ({self._module_id}): Failed to publish message: {e}")
            return None

    def get_module_status(self) -> Dict[str, Any]:
        """Returns the current status of the Perception Module."""
        return {
            "module_id": self._module_id,
            "module_type": "ConcretePerceptionModule",
            "supported_modalities": list(self._supported_modalities),
            "message_bus_configured": self._message_bus is not None,
            "processing_log_count": len(self._processing_log),
            "last_processed_summary": self._processing_log[-1] if self._processing_log else "None"
        }

if __name__ == '__main__':
    import asyncio
    import time

    # Ensure MessageBus and core_messages are available for __main__
    # These should be the actual classes, not stubs, if the script is run directly.
    # The try-except at the top handles cases where they might be imported differently.
    if MessageBus is None or GenericMessage is None or PerceptDataPayload is None:
        print("CRITICAL: MessageBus or core_messages not loaded correctly for __main__ test. Exiting.")
        exit(1)

    print("\n--- ConcretePerceptionModule __main__ Test ---")

    received_percepts: List[GenericMessage] = []
    def percept_listener(message: GenericMessage):
        print(f"\n percept_listener: Received PerceptData! ID: {message.message_id[:8]}")
        if isinstance(message.payload, PerceptDataPayload):
            payload: PerceptDataPayload = message.payload
            print(f"  Source: {message.source_module_id}")
            print(f"  Modality: {payload.modality}")
            print(f"  Content type: {type(payload.content)}")
            print(f"  Content: {str(payload.content)[:150]}...") # Print truncated content
            print(f"  Source Timestamp: {payload.source_timestamp}")
            received_percepts.append(message)
        else:
            print(f"  ERROR: Listener received non-PerceptDataPayload: {type(message.payload)}")

    async def main_test_flow():
        bus = MessageBus()
        # Use a specific module ID for testing
        test_module_id = "PerceptionTest01"
        perception_module = ConcretePerceptionModule(message_bus=bus, module_id=test_module_id)

        print("\n--- Initial Status ---")
        print(perception_module.get_module_status())

        bus.subscribe(
            module_id="TestListener",
            message_type="PerceptData",
            callback=percept_listener
        )
        print("\nTestListener subscribed to PerceptData messages.")

        # 1. Test successful text processing
        print("\n--- Processing and Publishing: Text Input (Success) ---")
        text_input_ok = "Hello Pia, please see the red ball."
        ts1 = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=2)
        msg_id1 = perception_module.process_and_publish_stimulus(text_input_ok, "text", ts1)
        assert msg_id1 is not None

        await asyncio.sleep(0.05) # Allow time for message dispatch if bus is async

        assert len(received_percepts) == 1, "Listener did not receive the first text percept."
        if received_percepts:
            p1: PerceptDataPayload = received_percepts[0].payload
            assert received_percepts[0].source_module_id == test_module_id
            assert p1.modality == "text"
            assert isinstance(p1.content, dict)
            assert p1.content.get("type") == "linguistic_analysis"
            assert "ball" in [e["name"] for e in p1.content.get("entities", [])]
            assert p1.source_timestamp == ts1
            print("  Listener correctly received and verified first text percept.")
        received_percepts.clear()

        # 2. Test successful dict_mock processing
        print("\n--- Processing and Publishing: Dict Mock Input (Success) ---")
        dict_input_ok = {"sensor": "cameraX", "data": [1, 2, 3]}
        ts2 = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=1)
        msg_id2 = perception_module.process_and_publish_stimulus(dict_input_ok, "dict_mock", ts2)
        assert msg_id2 is not None

        await asyncio.sleep(0.05)

        assert len(received_percepts) == 1, "Listener did not receive the dict_mock percept."
        if received_percepts:
            p2: PerceptDataPayload = received_percepts[0].payload
            assert p2.modality == "dict_mock"
            assert isinstance(p2.content, dict)
            assert p2.content.get("type") == "structured_data"
            assert p2.content.get("data") == dict_input_ok
            assert p2.source_timestamp == ts2
            print("  Listener correctly received and verified dict_mock percept.")
        received_percepts.clear()

        # 3. Test unsupported modality (should publish an error in content)
        print("\n--- Processing and Publishing: Unsupported Modality (audio) ---")
        audio_input_fail = b"some_audio_data_bytes"
        ts3 = datetime.datetime.now(datetime.timezone.utc)
        msg_id3 = perception_module.process_and_publish_stimulus(audio_input_fail, "audio", ts3)
        assert msg_id3 is not None

        await asyncio.sleep(0.05)

        assert len(received_percepts) == 1, "Listener did not receive the unsupported modality percept."
        if received_percepts:
            p3: PerceptDataPayload = received_percepts[0].payload
            assert p3.modality == "audio" # Modality is still original
            assert isinstance(p3.content, dict)
            assert p3.content.get("error") == "processing_failed"
            assert "unsupported_modality" in p3.content.get("details", "")
            assert p3.source_timestamp == ts3
            print("  Listener correctly received and verified unsupported modality percept (with error payload).")
        received_percepts.clear()

        # 4. Test with module that has no message bus
        print("\n--- Testing Module without Message Bus ---")
        perception_module_no_bus = ConcretePerceptionModule(message_bus=None, module_id="NoBusPerception")
        print(perception_module_no_bus.get_module_status())
        no_bus_msg_id = perception_module_no_bus.process_and_publish_stimulus("Test no bus", "text", datetime.datetime.now(datetime.timezone.utc))
        assert no_bus_msg_id is None
        print("  Attempt to publish with no bus correctly returned None.")

        print("\n--- Final Status of Test Module ---")
        print(perception_module.get_module_status())
        assert perception_module.get_module_status()['processing_log_count'] == 3 # three calls to process_and_publish

        print("\n--- ConcretePerceptionModule __main__ Test Complete ---")

    try:
        asyncio.run(main_test_flow())
    except RuntimeError as e:
        if " asyncio.run() cannot be called from a running event loop" in str(e):
            print("Skipping asyncio.run() as an event loop is already running (e.g. in Jupyter/IPython).")
        else:
            raise

    # Old __main__ content (for reference or non-bus testing)
    # perception_module = ConcretePerceptionModule()
    # print("\n--- Initial Status ---")
    # print(perception_module.get_module_status())

    # Process text input
    # print("\n--- Process Text Input ---")
    # text_input1 = "Hello Pia, see the red ball."
    # ... (rest of old main commented out)
    # print("\nExample Usage Complete.")
