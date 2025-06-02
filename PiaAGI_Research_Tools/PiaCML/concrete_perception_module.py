from typing import Any, Dict, List, Optional
import time # Added for timestamping
import uuid # Not strictly needed by spec, but good for unique IDs if we were to generate them

try:
    from .base_perception_module import BasePerceptionModule
except ImportError:
    # Fallback for scenarios where the relative import might fail
    from base_perception_module import BasePerceptionModule

class ConcretePerceptionModule(BasePerceptionModule):
    """
    A basic, concrete implementation of the BasePerceptionModule.
    This version processes sensory input in three stages: raw processing,
    feature extraction, and structured percept generation.
    """

    def __init__(self):
        self._supported_modalities = ["text", "dict_mock"]
        self._processing_log: List[Dict[str, Any]] = [] # Log will store dicts for more info
        self._attentional_focus_settings: Optional[Dict] = None
        print("ConcretePerceptionModule initialized.")

    def process_sensory_input(self, raw_input: Any, modality: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Processes raw sensory input based on modality.
        """
        log_entry = {
            "stage": "process_sensory_input",
            "modality": modality,
            "raw_input_summary": str(raw_input)[:100],
            "context": context,
            "timestamp": time.time()
        }
        print(f"ConcretePerceptionModule (process_sensory_input): Modality '{modality}'. Input: {str(raw_input)[:100]}")

        processed_output: Any
        if modality == "text" and isinstance(raw_input, str):
            processed_output = str(raw_input).lower().strip()
        elif modality == "dict_mock" and isinstance(raw_input, dict):
            processed_output = raw_input # Pass dict through
        else:
            print(f"ConcretePerceptionModule: Modality '{modality}' not specifically handled for raw processing, returning as is.")
            processed_output = {'type': 'unprocessed_raw', 'data': raw_input}
            # Or simply: processed_output = raw_input

        log_entry["processed_output_summary"] = str(processed_output)[:100]
        self._processing_log.append(log_entry)
        return processed_output

    def extract_features(self, processed_input: Any, modality: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extracts features from processed sensory input.
        """
        log_entry = {
            "stage": "extract_features",
            "modality": modality,
            "processed_input_summary": str(processed_input)[:100],
            "context": context,
            "timestamp": time.time()
        }
        print(f"ConcretePerceptionModule (extract_features): Modality '{modality}'. Input: {str(processed_input)[:100]}")

        features: Dict[str, Any] = {}

        if modality == "text" and isinstance(processed_input, str):
            # processed_input is already lowercased and stripped text
            entities_found = []
            actions_found = []

            # Keyword spotting (from original logic)
            if "apple" in processed_input: entities_found.append({"type": "fruit", "name": "apple"})
            if "ball" in processed_input: entities_found.append({"type": "toy", "name": "ball"})
            if "user" in processed_input: entities_found.append({"type": "agent", "name": "user"})
            if "pia" in processed_input: entities_found.append({"type": "agent", "name": "PiaAGI"})

            if "give" in processed_input or "pass" in processed_input: actions_found.append({"type": "transfer", "verb": "give/pass"})
            if "see" in processed_input or "look" in processed_input: actions_found.append({"type": "observe", "verb": "see/look"})
            if "greet" in processed_input or "hello" in processed_input or "hi" in processed_input: actions_found.append({"type": "social_interaction", "verb": "greet"})

            features = {
                "entities": entities_found,
                "actions": actions_found,
                "sentiment_conceptual": "neutral" # Placeholder
            }
        elif modality == "dict_mock" and isinstance(processed_input, dict):
            # Example feature extraction for a "camera" like dict input
            if processed_input.get('sensor_type') == 'camera':
                objects = processed_input.get('objects_detected', [])
                features = {
                    'object_count': len(objects),
                    'raw_objects': objects,
                    'image_quality_conceptual': processed_input.get('image_quality', 'unknown')
                }
            else:
                features = {'raw_dict_features': list(processed_input.keys())} # Generic features for other dicts
        else:
            print(f"ConcretePerceptionModule: Feature extraction unsupported for modality '{modality}' or input type '{type(processed_input)}'.")
            features = {'error': 'feature_extraction_unsupported_for_modality_or_type'}

        log_entry["extracted_features_summary"] = str(features)[:100]
        self._processing_log.append(log_entry)
        return features

    def generate_structured_percept(self, features: Dict[str, Any], modality: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generates a structured percept from extracted features.
        """
        current_time = time.time()
        log_entry = {
            "stage": "generate_structured_percept",
            "modality": modality,
            "features_summary": str(features)[:100],
            "context": context,
            "timestamp": current_time
        }
        print(f"ConcretePerceptionModule (generate_structured_percept): Modality '{modality}'. Features: {str(features)[:100]}")

        percept = {
            "type": "unknown_percept",
            "modality": modality,
            "features_extracted": features,
            "timestamp": context.get('timestamp', current_time) if context else current_time,
            "metadata": context or {}
        }

        if modality == "text":
            percept["type"] = "linguistic_input_processed"
            if "actions" in features and features["actions"]:
                percept["primary_action_type"] = features["actions"][0]["type"]
        elif modality == "dict_mock" and features.get("raw_objects") is not None:
             percept["type"] = "structured_object_scene"
        elif 'error' in features:
            percept["type"] = "error_percept"
            percept["error_details"] = features['error']

        log_entry["generated_percept_type"] = percept["type"]
        self._processing_log.append(log_entry)
        print(f"ConcretePerceptionModule: Generated percept: {percept}")
        return percept

    def set_attentional_focus(self, focus_details: Dict) -> None:
        print(f"ConcretePerceptionModule: set_attentional_focus called with {focus_details}. Placeholder - no action taken.")
        self._attentional_focus_settings = focus_details

    def get_status(self) -> Dict[str, Any]:
        return {
            "module_type": "ConcretePerceptionModule",
            "supported_modalities": list(self._supported_modalities),
            "processing_log_count": len(self._processing_log),
            "attentional_focus_settings": self._attentional_focus_settings,
            "last_processed_summary": self._processing_log[-1]["generated_percept_type"] if self._processing_log and "generated_percept_type" in self._processing_log[-1] else "None"
        }

if __name__ == '__main__':
    perception_module = ConcretePerceptionModule()

    # Initial Status
    print("\n--- Initial Status ---")
    print(perception_module.get_status())

    # --- Process text input ---
    print("\n--- Process Text Input ---")
    text_input1 = "Hello Pia, see the red ball."
    context1 = {"source_id": "user_A", "timestamp": time.time()}

    processed_text1 = perception_module.process_sensory_input(text_input1, "text", context1)
    print("Processed Text 1:", processed_text1)

    features_text1 = perception_module.extract_features(processed_text1, "text", context1)
    print("Features Text 1:", features_text1)

    percept1 = perception_module.generate_structured_percept(features_text1, "text", context1)
    print("Percept 1:", percept1)
    assert percept1['type'] == "linguistic_input_processed"
    assert len(percept1['features_extracted']['entities']) == 2 # Pia, ball
    assert len(percept1['features_extracted']['actions']) == 2 # greet, see

    # --- Process dict_mock input ---
    print("\n--- Process Dict Mock Input ---")
    dict_input = {"sensor_type": "camera", "objects_detected": [{"id": "obj1", "class": "cup", "confidence": 0.9}], "image_quality": "good"}
    context2 = {"source_id": "camera_feed_01"}

    processed_dict1 = perception_module.process_sensory_input(dict_input, "dict_mock", context2)
    print("Processed Dict 1:", processed_dict1)

    features_dict1 = perception_module.extract_features(processed_dict1, "dict_mock", context2)
    print("Features Dict 1:", features_dict1)
    assert features_dict1.get('object_count') == 1

    percept2 = perception_module.generate_structured_percept(features_dict1, "dict_mock", context2)
    print("Percept 2:", percept2)
    assert percept2['type'] == "structured_object_scene"
    assert percept2['features_extracted']['object_count'] == 1

    # --- Process unsupported modality ---
    print("\n--- Process Unsupported Modality ---")
    audio_input = b"some_audio_bytes" # Representing raw audio
    context3 = {"source_id": "mic_01"}

    processed_audio = perception_module.process_sensory_input(audio_input, "audio", context3)
    print("Processed Audio:", processed_audio) # Should be {'type': 'unprocessed_raw', 'data': ...}

    features_audio = perception_module.extract_features(processed_audio, "audio", context3) # Modality is still "audio"
    print("Features Audio:", features_audio) # Should be {'error': ...}

    percept3 = perception_module.generate_structured_percept(features_audio, "audio", context3)
    print("Percept 3:", percept3)
    assert percept3['type'] == "error_percept"

    # --- Test Attentional Focus ---
    print("\n--- Setting Attentional Focus ---")
    focus_set = {"target_modality": "text", "keywords_boost": ["important", "urgent"]}
    perception_module.set_attentional_focus(focus_set)
    print(perception_module.get_status().get("attentional_focus_settings"))
    assert perception_module.get_status()['attentional_focus_settings'] == focus_set

    # Final Status
    print("\n--- Final Status ---")
    print(perception_module.get_status())
    assert perception_module.get_status()['processing_log_count'] == 9 # 3 stages for 3 inputs

    print("\nExample Usage Complete.")
