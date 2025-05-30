from abc import ABC, abstractmethod
from typing import Any, Dict, List

class PerceptionModule(ABC):
    """
    Abstract Base Class for the Perception Module in the PiaAGI Cognitive Architecture.

    The Perception Module is responsible for receiving raw sensory input from various modalities
    (e.g., text, vision, audio), processing this input, extracting relevant features,
    and generating a structured perceptual representation that can be used by other
    cognitive modules, particularly Working Memory and the World Model.

    This module is crucial for grounding the AGI's internal representations in
    external reality.

    Refer to PiaAGI.md Sections 4.1.1 (Perception Module) and 4.3 (Perception and World Modeling)
    for more detailed context.
    """

    @abstractmethod
    def process_sensory_input(self, raw_data: Any, modality: str, metadata: Dict = None) -> Any:
        """
        Processes raw sensory data from a specific modality.

        This is the first step in the perception pipeline. For example, for text,
        this might involve basic cleaning or tokenization. For vision, it might be
        initial image normalization or segmentation.

        Args:
            raw_data (Any): The raw sensory input (e.g., a string of text, an image byte stream, audio data).
            modality (str): The sensory modality of the input (e.g., "text", "vision", "audio").
            metadata (Dict, optional): Additional metadata about the raw input,
                                       such as source, timestamp, sensor settings.

        Returns:
            Any: Processed input, ready for feature extraction. The type will depend on the modality.
        """
        pass

    @abstractmethod
    def extract_features(self, processed_input: Any, modality: str, config: Dict = None) -> Dict:
        """
        Extracts relevant features from the processed sensory input.

        For text, features might include entities, keywords, sentiment, semantic roles.
        For vision, features could be object bounding boxes, contours, textures, recognized objects.
        For audio, features might be MFCCs, pitch, speech segments.

        Args:
            processed_input (Any): The output from process_sensory_input.
            modality (str): The sensory modality.
            config (Dict, optional): Configuration for the feature extraction process,
                                     e.g., specific models to use, sensitivity thresholds.

        Returns:
            Dict: A dictionary of extracted features.
                  Example for text: {'entities': [...], 'sentiment': 0.8, 'keywords': [...]}
                  Example for vision: {'objects': [{'label': 'cup', 'bbox': [x,y,w,h]}], 'scene_type': 'indoor'}
        """
        pass

    @abstractmethod
    def generate_structured_percept(self, features: Dict, modality: str, context: Dict = None) -> Dict:
        """
        Combines extracted features into a structured, meaningful percept.

        This percept is what gets passed to other cognitive modules like Working Memory
        or the World Model. It should be a coherent representation of the perceived event or scene.

        Args:
            features (Dict): The output from extract_features.
            modality (str): The sensory modality.
            context (Dict, optional): Broader context to aid interpretation, e.g., current
                                      AGI goals, recent interaction history.

        Returns:
            Dict: A structured percept.
                  Example: {'type': 'user_utterance', 'modality': 'text',
                            'content': {'text': "Hello Pia", 'intent': 'greeting', 'sentiment': 0.9},
                            'timestamp': 12345.789, 'source_id': 'user_A'}
                  Example: {'type': 'visual_scene', 'modality': 'vision',
                            'elements': [{'object_id': 'obj1', 'label': 'cat', 'position': [10,20]}],
                            'relations': [{'type': 'on_top_of', 'subject': 'obj1', 'object': 'obj2'}]}
        """
        pass

    @abstractmethod
    def set_attentional_focus(self, focus_details: Dict) -> None:
        """
        Allows the Central Executive (via the Attention Module conceptually) to guide
        what the Perception module prioritizes or filters.

        Args:
            focus_details (Dict): Details about what to focus on or ignore.
                                  Example: {'modality': 'vision', 'ignore_areas': [[x,y,w,h]],
                                            'prioritize_objects': ['face', 'text_on_screen']}
        """
        pass

    @abstractmethod
    def get_status(self) -> Dict:
        """
        Returns the current status of the Perception Module.

        Could include information like active modalities, processing load, error rates.

        Returns:
            Dict: Status information.
        """
        pass

if __name__ == '__main__':
    # Conceptual illustration for PerceptionModule

    class ConceptualTextPerception(PerceptionModule):
        def __init__(self):
            print("ConceptualTextPerception initialized.")
            self.current_focus = {}

        def process_sensory_input(self, raw_data: Any, modality: str, metadata: Dict = None) -> Any:
            print(f"ConceptualTextPerception: Processing raw '{modality}' input: '{raw_data}'")
            if modality == "text":
                return str(raw_data).lower().strip() # Simple processing
            return raw_data

        def extract_features(self, processed_input: Any, modality: str, config: Dict = None) -> Dict:
            print(f"ConceptualTextPerception: Extracting features from: '{processed_input}'")
            features = {}
            if modality == "text":
                words = str(processed_input).split()
                features['word_count'] = len(words)
                features['keywords'] = [w for w in words if len(w) > 4] # Simple keyword extraction
                if "hello" in words or "hi" in words:
                    features['intent_type'] = 'greeting'
                elif "tell me about" in str(processed_input):
                    features['intent_type'] = 'query'
                    topic_idx = words.index("about") + 1 if "about" in words else -1
                    if topic_idx != -1 and topic_idx < len(words):
                        features['topic'] = words[topic_idx]

            print(f"ConceptualTextPerception: Extracted features: {features}")
            return features

        def generate_structured_percept(self, features: Dict, modality: str, context: Dict = None) -> Dict:
            print(f"ConceptualTextPerception: Generating structured percept from features: {features}")
            percept = {
                'type': features.get('intent_type', 'unknown_interaction'),
                'modality': modality,
                'features': features,
                'timestamp': context.get('timestamp', 0.0) if context else 0.0
            }
            if features.get('topic'):
                percept['topic'] = features['topic']
            print(f"ConceptualTextPerception: Generated percept: {percept}")
            return percept

        def set_attentional_focus(self, focus_details: Dict) -> None:
            print(f"ConceptualTextPerception: Setting attentional focus to: {focus_details}")
            self.current_focus = focus_details
            # In a real system, this would alter how process_sensory_input or extract_features behave.

        def get_status(self) -> Dict:
            return {'module_type': 'ConceptualTextPerception', 'active_focus': self.current_focus}

    # Conceptual usage:
    text_perception = ConceptualTextPerception()
    raw_text = "Hello Pia, tell me about dark matter."
    
    processed = text_perception.process_sensory_input(raw_text, "text")
    features = text_perception.extract_features(processed, "text")
    percept = text_perception.generate_structured_percept(features, "text", {'timestamp': 123.45})
    
    print(f"Final Percept: {percept}")
    print(f"Perception Status: {text_perception.get_status()}")
    
    text_perception.set_attentional_focus({'modality': 'text', 'ignore_keywords': ['pia']})
    print(f"Perception Status after focus set: {text_perception.get_status()}")
