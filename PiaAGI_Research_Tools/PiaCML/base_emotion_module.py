from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class BaseEmotionModule(ABC):
    """
    Abstract Base Class for the Emotion Module in the PiaAGI Cognitive Architecture.

    This module is responsible for generating, processing, and modulating emotional states.
    Emotions are complex psycho-physiological responses that significantly influence perception,
    cognition, decision-making, and social interaction. The Emotion Module provides the AGI
    with a computational equivalent of emotions, enabling more nuanced and adaptive behavior.

    It integrates inputs from various cognitive processes (e.g., appraisal of events,
    goal status from Motivational System, physiological states) to generate emotional responses.
    These responses can then modulate other cognitive functions and trigger expressive behaviors.

    Refer to PiaAGI.md Sections 3.4 (Computational Models of Emotion) and
    4.1.7 (Emotion Module) for more detailed context.
    """

    @abstractmethod
    def update_emotional_state(self, appraisal_info: Dict, event_source: Optional[str] = None) -> None:
        """
        Updates the AGI's emotional state based on cognitive appraisal of events or internal states.

        Appraisal information typically includes details about an event's relevance to goals,
        its pleasantness/unpleasantness, perceived control, and potential coping mechanisms.

        Args:
            appraisal_info (Dict): Information used for emotional appraisal.
                                   Example: {'event_type': 'goal_achieved', 'goal_id': 'g1',
                                             'significance': 0.8, 'pleasantness': 0.9}
                                   Example: {'event_type': 'threat_detected', 'source': 'perception',
                                             'perceived_danger': 0.7}
            event_source (Optional[str]): The module or process that triggered this update
                                          (e.g., "MotivationalSystem", "PerceptionModule", "SelfReflection").
        """
        pass

    @abstractmethod
    def get_current_emotional_state(self) -> Dict[str, float]:
        """
        Retrieves the current emotional landscape of the AGI.

        This typically returns a dictionary where keys are emotion labels (e.g., "joy", "sadness",
        "fear", "anger", "surprise", "disgust", "curiosity_level") and values are their
        current intensities (e.g., on a 0.0 to 1.0 scale).

        Returns:
            Dict[str, float]: The current intensity of various emotions.
        """
        pass

    @abstractmethod
    def express_emotion(self, emotion_to_express: str, intensity: float, target_channel: str, context: Optional[Dict] = None) -> Any:
        """
        Generates an expression of a specific emotion through a designated channel.

        This could be an internal signal to other modules (e.g., biasing decision-making)
        or an external behavioral output (e.g., linguistic expression, facial animation - if applicable).

        Args:
            emotion_to_express (str): The emotion to be expressed (e.g., "joy", "concern").
            intensity (float): The intensity of the expression.
            target_channel (str): The channel for expression (e.g., "internal_cognitive_bias",
                                  "communication_module", "behavioral_output").
            context (Optional[Dict]): Contextual information for tailoring the expression.

        Returns:
            Any: The result of the expression (e.g., a data structure for internal bias,
                 a command for the communication module).
        """
        pass

    @abstractmethod
    def regulate_emotion(self, strategy: str, target_emotion_details: Dict) -> bool:
        """
        Applies a specified emotion regulation strategy to modulate an emotional state.

        Strategies could include suppression, reappraisal, distraction, etc.

        Args:
            strategy (str): The emotion regulation strategy to apply (e.g., "cognitive_reappraisal",
                            "attentional_deployment", "response_modulation").
            target_emotion_details (Dict): Details about the emotion to regulate and the desired change.
                                           Example: {'emotion': 'fear', 'desired_intensity_change': -0.5}
                                           Example: {'emotion': 'anger', 'reappraisal_focus': 'positive_aspects'}


        Returns:
            bool: True if the regulation strategy was successfully initiated, False otherwise.
        """
        pass

    @abstractmethod
    def get_emotional_influence_on_cognition(self) -> Dict:
        """
        Assesses and returns how current emotions are likely influencing other cognitive processes.

        For example, high fear might narrow attentional focus, while positive affect might broaden it
        or enhance creativity.

        Returns:
            Dict: A dictionary describing the modulatory effects.
                  Example: {'attention_bias': 'narrowed_focus_on_threat',
                            'memory_retrieval_bias': 'negative_memories_more_accessible',
                            'decision_making_style': 'risk_averse'}
        """
        pass

    @abstractmethod
    def set_personality_profile(self, profile: Dict) -> None:
        """
        Sets or updates the baseline emotional dispositions and reactivity patterns of the AGI,
        based on a configurable personality profile.

        This influences default emotional thresholds, reactivity intensity, and regulation tendencies.

        Args:
            profile (Dict): Personality trait settings relevant to emotion.
                            Example: {'neuroticism': 0.7, 'extraversion': 0.4, 'agreeableness': 0.6,
                                      'default_mood': 'slightly_optimistic'}
        """
        pass

    @abstractmethod
    def get_status(self) -> Dict:
        """
        Returns the current operational status of the Emotion Module.

        Could include information like current dominant emotion, last significant emotional event,
        active regulation strategies.

        Returns:
            Dict: Status information.
        """
        pass

if __name__ == '__main__':
    # Conceptual illustration for BaseEmotionModule

    class ConceptualEmotion(BaseEmotionModule):
        def __init__(self):
            self.emotions = {"joy": 0.2, "sadness": 0.1, "fear": 0.05, "anger": 0.05, "curiosity_level": 0.5}
            self.personality = {"neuroticism": 0.5, "default_mood_offset": 0.05} # default mood is slightly positive
            self.last_event = None
            print(f"ConceptualEmotion initialized with baseline: {self.emotions}")

        def update_emotional_state(self, appraisal_info: Dict, event_source: Optional[str] = None) -> None:
            print(f"ConceptualEmotion: Updating emotional state from '{event_source}' with appraisal: {appraisal_info}")
            self.last_event = appraisal_info
            
            event_type = appraisal_info.get("event_type")
            pleasantness = appraisal_info.get("pleasantness", 0)
            significance = appraisal_info.get("significance", 0.5)
            perceived_danger = appraisal_info.get("perceived_danger", 0)

            # Simplified emotion update logic
            if event_type == "goal_achieved" and pleasantness > 0:
                self.emotions["joy"] = min(1.0, self.emotions.get("joy",0) + pleasantness * significance * 0.5)
                self.emotions["sadness"] = max(0.0, self.emotions.get("sadness",0) - pleasantness * significance * 0.2)
            elif event_type == "goal_failed" and pleasantness < 0:
                self.emotions["sadness"] = min(1.0, self.emotions.get("sadness",0) + abs(pleasantness) * significance * 0.5)
                self.emotions["joy"] = max(0.0, self.emotions.get("joy",0) - abs(pleasantness) * significance * 0.2)
            elif event_type == "threat_detected" and perceived_danger > 0:
                self.emotions["fear"] = min(1.0, self.emotions.get("fear",0) + perceived_danger * significance * 0.6)
            
            # Apply personality influences (e.g., neuroticism amplifies negative emotions)
            if pleasantness < 0 or perceived_danger > 0:
                 self.emotions["fear"] = min(1.0, self.emotions["fear"] * (1 + self.personality.get("neuroticism", 0.5) * 0.1))
                 self.emotions["sadness"] = min(1.0, self.emotions["sadness"] * (1 + self.personality.get("neuroticism", 0.5) * 0.1))
            
            # General decay and return to baseline (influenced by default_mood_offset)
            for emotion, value in self.emotions.items():
                if emotion != "curiosity_level": # curiosity might be managed differently
                    self.emotions[emotion] = max(0.0, value - 0.05) # Decay factor
                    self.emotions[emotion] = max(self.emotions[emotion], self.personality.get("default_mood_offset",0) if emotion == "joy" else 0)


            print(f"  New emotional state: {self.emotions}")

        def get_current_emotional_state(self) -> Dict[str, float]:
            print(f"ConceptualEmotion: Getting current emotional state: {self.emotions}")
            return self.emotions

        def express_emotion(self, emotion_to_express: str, intensity: float, target_channel: str, context: Optional[Dict] = None) -> Any:
            print(f"ConceptualEmotion: Expressing '{emotion_to_express}' (intensity {intensity}) via '{target_channel}'. Context: {context}")
            if target_channel == "internal_cognitive_bias":
                return {"bias_type": f"{emotion_to_express}_related_processing", "intensity_factor": intensity}
            elif target_channel == "communication_module":
                return f"Tell user: I am feeling {emotion_to_express} at intensity {intensity}."
            return None

        def regulate_emotion(self, strategy: str, target_emotion_details: Dict) -> bool:
            print(f"ConceptualEmotion: Regulating emotion using '{strategy}' for {target_emotion_details}")
            emotion = target_emotion_details.get('emotion')
            change = target_emotion_details.get('desired_intensity_change', 0)
            
            if emotion in self.emotions:
                current_intensity = self.emotions[emotion]
                self.emotions[emotion] = max(0.0, min(1.0, current_intensity + change))
                print(f"  Emotion '{emotion}' changed from {current_intensity:.2f} to {self.emotions[emotion]:.2f}")
                return True
            return False

        def get_emotional_influence_on_cognition(self) -> Dict:
            influence = {}
            if self.emotions.get("fear", 0) > 0.7:
                influence['attention_bias'] = 'prioritize_threat_stimuli'
            if self.emotions.get("joy", 0) > 0.6:
                influence['decision_making_style'] = 'more_optimistic_evaluation'
            print(f"ConceptualEmotion: Current cognitive influence: {influence}")
            return influence

        def set_personality_profile(self, profile: Dict) -> None:
            print(f"ConceptualEmotion: Setting personality profile: {profile}")
            self.personality.update(profile)
            # Potentially re-evaluate baseline emotions based on new profile
            self.emotions["joy"] = max(self.emotions["joy"], self.personality.get("default_mood_offset",0.05))


        def get_status(self) -> Dict:
            dominant_emotion = max(self.emotions, key=self.emotions.get)
            return {
                "module_type": "ConceptualEmotion",
                "dominant_emotion": dominant_emotion,
                "dominant_intensity": self.emotions[dominant_emotion],
                "full_state": self.emotions,
                "last_event_processed": self.last_event,
                "personality_settings": self.personality
            }

    # Conceptual usage:
    emotion_system = ConceptualEmotion()
    print(f"Initial status: {emotion_system.get_status()}")

    emotion_system.set_personality_profile({"neuroticism": 0.8, "default_mood_offset": 0.01})

    appraisal1 = {'event_type': 'goal_achieved', 'goal_id': 'g1', 'significance': 0.9, 'pleasantness': 0.8}
    emotion_system.update_emotional_state(appraisal1, event_source="MotivationalSystem")
    print(f"Current state: {emotion_system.get_current_emotional_state()}")

    appraisal2 = {'event_type': 'threat_detected', 'source': 'perception', 'perceived_danger': 0.6, 'significance': 0.7}
    emotion_system.update_emotional_state(appraisal2, event_source="PerceptionModule")
    
    print(f"Cognitive influence: {emotion_system.get_emotional_influence_on_cognition()}")
    
    emotion_system.express_emotion("joy", emotion_system.emotions["joy"], "communication_module")
    
    emotion_system.regulate_emotion("response_modulation", {'emotion': 'fear', 'desired_intensity_change': -0.3})
    print(f"Status after regulation: {emotion_system.get_status()}")


