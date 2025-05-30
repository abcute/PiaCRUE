from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseCommunicationModule(ABC):
    """
    Abstract Base Class for a Communication Module within the PiaAGI Cognitive Architecture.

    This module manages all aspects of nuanced natural language interaction (and potentially
    other communication modalities). It handles Natural Language Understanding (NLU) by
    processing inputs from the Perception module, and Natural Language Generation (NLG)
    by constructing outputs for the Behavior Generation module. It implements advanced
    communication strategies (e.g., CSIM, RaR, CACE model elements from PiaAGI.md)
    and integrates information from ToM, Emotion, and Self-Model modules to tailor
    communication effectively.

    Refer to PiaAGI.md Sections 2.2 (Communication Theory for AGI-Level Interaction)
    and 4.1.12 (Communication Module) for more context.
    """

    @abstractmethod
    def process_incoming_communication(self, raw_input: Any, source_modality: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Processes incoming communication from an external agent or environment.
        This involves NLU for text, or analogous processing for other modalities.

        Args:
            raw_input (Any): The raw communication input (e.g., text string, audio stream handle, image data).
            source_modality (str): The modality of the input (e.g., "text", "speech", "visual_cue").
            context (Dict[str, Any], optional): Contextual information relevant to processing,
                                                such as sender ID, dialogue history pointers,
                                                current environmental state.
                                                Example: {'sender_id': 'user_001', 'dialogue_id': 'chat_123'}

        Returns:
            Dict[str, Any]: A structured representation of the processed communication.
                            Example for text:
                            {'type': 'user_utterance',
                             'semantic_content': {'intent': 'query_weather', 'entities': {'location': 'London'}},
                             'emotional_cues_detected': {'tone': 'inquisitive'},
                             'raw_input_ref': raw_input} # Reference to original input
                            This output would typically be sent to Working Memory and other relevant modules.
        """
        pass

    @abstractmethod
    def generate_outgoing_communication(self, abstract_message: Dict[str, Any], target_recipient_id: str, desired_effect: Optional[str] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generates a concrete communication output based on an abstract message representation.
        This involves NLG for text, or analogous generation for other modalities.

        Args:
            abstract_message (Dict[str, Any]): An internal representation of the message
                                               to be conveyed. This comes from higher-level
                                               cognitive processes (e.g., Planning, Self-Model).
                                               Example: {'intent_to_convey': 'inform_weather',
                                                         'data': {'location': 'London', 'forecast': 'sunny'},
                                                         'recipient_model_hints': {'knowledge_level': 'novice'}}
            target_recipient_id (str): Identifier for the intended recipient.
            desired_effect (Optional[str]): The intended effect of the communication on the recipient
                                            (e.g., "inform", "persuade", "reassure", "request_action").
                                            This helps in choosing appropriate strategies.
            context (Dict[str, Any], optional): Contextual information to guide generation,
                                                such as AGI's current emotional state (from EmotionModule),
                                                personality profile (from SelfModel), ToM inferences about
                                                the recipient, and active communication strategies.
                                                Example: {'agi_emotion': 'calm', 'strategy': 'RaR_reassurance_needed'}

        Returns:
            Dict[str, Any]: A structured representation of the generated communication,
                            ready to be passed to the BehaviorGenerationModule.
                            Example for text:
                            {'modality': 'text',
                             'content': "The weather in London is expected to be sunny.",
                             'metadata': {'tone_applied': 'neutral_informative',
                                          'strategy_used': 'direct_inform'}}
        """
        pass

    @abstractmethod
    def manage_dialogue_state(self, dialogue_id: str, new_turn_info: Optional[Dict[str, Any]] = None, action: str = "update") -> Dict[str, Any]:
        """
        Manages the state of a dialogue or communicative interaction.
        This includes tracking history, turns, topics, and relevant context.

        Args:
            dialogue_id (str): A unique identifier for the dialogue session.
            new_turn_info (Optional[Dict[str, Any]]): Information from the latest turn
                                                      (e.g., processed input, generated output,
                                                       speaker, timestamp) to update the state.
                                                       If None, could imply a query or end action.
            action (str): The action to perform on the dialogue state.
                          Examples: "initiate", "update", "get_history", "get_summary", "close".

        Returns:
            Dict[str, Any]: The result of the action.
                            For "update": {'status': 'updated', 'current_turn_number': 3}
                            For "get_history": {'history': [turn1_info, turn2_info, ...]}
                            For "get_summary": {'topic': 'weather_in_london', 'sentiment_trend': 'neutral'}
        """
        pass

    @abstractmethod
    def apply_communication_strategy(self, current_communication_goal: str, recipient_model: Dict[str, Any], dialogue_context: Dict[str, Any], available_strategies: List[str]) -> Dict[str, Any]:
        """
        Selects and configures parameters for a specific communication strategy
        (e.g., CSIM, RaR, CACE elements) based on the goal, recipient, and context.

        Args:
            current_communication_goal (str): The immediate goal of the communication
                                              (e.g., "build_rapport", "clarify_ambiguity",
                                               "convey_complex_info_sensitively").
            recipient_model (Dict[str, Any]): The ToM model of the recipient, including
                                              inferred knowledge, beliefs, emotional state.
            dialogue_context (Dict[str, Any]): The current state of the dialogue.
            available_strategies (List[str]): A list of communication strategies the
                                              module is capable of employing.

        Returns:
            Dict[str, Any]: A dictionary specifying the chosen strategy and any parameters
                            for its application. This might influence subsequent NLG.
                            Example: {'chosen_strategy': 'RaR_Reasoning',
                                      'parameters': {'level_of_detail': 'high',
                                                     'emphasize_confidence_level': True}}
                                     {'chosen_strategy': 'CSIM_Schema_Bridging',
                                      'parameters': {'analogy_to_use': 'concept_X_is_like_Y_in_their_domain'}}
        """
        pass

    @abstractmethod
    def get_module_status(self) -> Dict[str, Any]:
        """
        Returns the current status of the Communication Module.

        Returns:
            Dict[str, Any]: A dictionary describing the module's status.
                            Example: {'active_dialogues': 1,
                                      'default_language': 'en-US',
                                      'loaded_strategies': ['CSIM_basic', 'RaR_inform']}
        """
        pass
