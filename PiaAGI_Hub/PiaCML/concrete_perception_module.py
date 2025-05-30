from typing import Any, Dict, List, Optional

try:
    from .base_perception_module import BasePerceptionModule
except ImportError:
    # Fallback for scenarios where the relative import might fail
    from base_perception_module import BasePerceptionModule

class ConcretePerceptionModule(BasePerceptionModule):
    """
    A basic, concrete implementation of the BasePerceptionModule.
    This version performs very simple keyword spotting for text inputs to extract
    conceptual 'objects' and 'actions'. For dictionary inputs (mocking other
    modalities), it wraps them in a standard perceptual representation.
    """

    def __init__(self):
        self._supported_modalities = ["text", "dict_mock"] # dict_mock for pre-structured data
        self._processing_log: List[str] = []
        print("ConcretePerceptionModule initialized.")

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

    def get_module_status(self) -> Dict[str, Any]:
        """Returns the current status of the Perception Module."""
        return {
            "module_type": "ConcretePerceptionModule",
            "supported_modalities": list(self._supported_modalities),
            "processing_log_count": len(self._processing_log),
            "last_processed_summary": self._processing_log[-1] if self._processing_log else "None"
        }

if __name__ == '__main__':
    perception_module = ConcretePerceptionModule()

    # Initial Status
    print("\n--- Initial Status ---")
    print(perception_module.get_module_status())

    # Process text input
    print("\n--- Process Text Input ---")
    text_input1 = "Hello Pia, see the red ball."
    percept1 = perception_module.process_sensory_input(text_input1, "text", {"source_id": "user_A"})
    print("Percept 1:", percept1)
    assert len(percept1['processed_representation']['entities']) == 2 # Pia, ball
    assert len(percept1['processed_representation']['actions']) == 2 # greet, see

    text_input2 = "User give apple to Pia."
    percept2 = perception_module.process_sensory_input(text_input2, "text")
    print("Percept 2:", percept2)
    assert len(percept2['processed_representation']['entities']) == 3 # User, apple, Pia
    assert len(percept2['processed_representation']['actions']) == 1 # give

    # Process dict_mock input
    print("\n--- Process Dict Mock Input ---")
    dict_input = {"sensor_type": "camera", "objects_detected": [{"id": "obj1", "class": "cup", "confidence": 0.9}]}
    percept3 = perception_module.process_sensory_input(dict_input, "dict_mock")
    print("Percept 3:", percept3)
    assert percept3['processed_representation']['type'] == "structured_data"
    assert percept3['processed_representation']['data'] == dict_input

    # Process unsupported modality
    print("\n--- Process Unsupported Modality ---")
    audio_input = b"some_audio_bytes" # Representing raw audio
    percept4 = perception_module.process_sensory_input(audio_input, "audio")
    print("Percept 4:", percept4)
    assert percept4['processed_representation']['type'] == "unsupported_modality"

    # Final Status
    print("\n--- Final Status ---")
    print(perception_module.get_module_status())
    assert perception_module.get_module_status()['processing_log_count'] == 4

    print("\nExample Usage Complete.")
