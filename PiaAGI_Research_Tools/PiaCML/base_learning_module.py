from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class BaseLearningModule(ABC):
    """
    Abstract Base Class for a Learning Module within the PiaAGI Cognitive Architecture.

    This module is responsible for acquiring new knowledge and skills, adapting existing
    representations, and improving performance over time. It encompasses various
    learning paradigms (e.g., reinforcement, supervised, unsupervised, transfer,
    meta-learning) and interacts extensively with memory systems (LTM, WM),
    the Motivational System, the Emotion Module, and the Self-Model.

    Refer to PiaAGI.md Sections 3.1.3 (Learning Theories and Mechanisms for AGI)
    and 4.1.5 (Learning Module(s)) for more context.
    """

    @abstractmethod
    def learn(self, data: Any, learning_paradigm: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiates a learning process based on the provided data and specified paradigm.

        Args:
            data (Any): The input data for learning. This could be experiences,
                        labeled datasets, unlabeled data, observed behaviors, etc.
                        Its structure will vary based on the learning_paradigm.
            learning_paradigm (str): Specifies the type of learning to apply.
                                     Examples: "reinforcement", "supervised", "unsupervised",
                                     "observational", "transfer", "meta_learning".
            context (Dict[str, Any]): Additional context for the learning process.
                                      This might include:
                                      - For RL: reward signals, action space, state space.
                                      - For SL: labels, loss function definition.
                                      - For UL: desired number of clusters, feature weighting.
                                      - For OL: model agent's behavior, success criteria.
                                      - For TL: source domain/task, target domain/task.
                                      - For Meta: current learning performance, strategy parameters.
                                      - General: relevant goals (from MotivationalSystem),
                                                 emotional state (from EmotionModule),
                                                 current WM contents, LTM pointers.

        Returns:
            Dict[str, Any]: A dictionary containing the outcome of the learning process.
                            Example: {'status': 'success/failure/ongoing',
                                      'updates_to_ltm': List[str], # IDs or descriptions of LTM changes
                                      'updated_self_model_params': List[str], # Parameters changed
                                      'new_learning_strategy': Optional[str]}
        """
        pass

    @abstractmethod
    def process_feedback(self, feedback_data: Dict[str, Any], learning_context_id: Optional[str] = None) -> bool:
        """
        Processes explicit feedback to refine ongoing or completed learning tasks.
        This is particularly relevant for reinforcement learning or interactive supervised learning.

        Args:
            feedback_data (Dict[str, Any]): The feedback received.
                                            Example: {'type': 'reward', 'value': 1.0, 'target_behavior_id': 'xyz'}
                                                     {'type': 'correction', 'old_value': 'A', 'new_value': 'B'}
            learning_context_id (Optional[str]): An identifier for the specific learning
                                                 process or episode this feedback applies to.

        Returns:
            bool: True if the feedback was successfully processed and applied, False otherwise.
        """
        pass

    @abstractmethod
    def consolidate_knowledge(self, learned_item_ids: List[str], target_memory_system: str = "LTM") -> bool:
        """
        Manages the consolidation of newly learned information or skills into the
        specified memory system (typically Long-Term Memory). This might involve
        transforming representations, integrating with existing knowledge, and
        managing potential interference.

        Args:
            learned_item_ids (List[str]): A list of identifiers for the recently learned
                                          information or skill representations currently
                                          held (e.g., in a temporary buffer within the learning module or WM).
            target_memory_system (str): The memory system to consolidate into (e.g., "LTM_semantic", "LTM_episodic").

        Returns:
            bool: True if consolidation was successful or initiated, False otherwise.
        """
        pass

    @abstractmethod
    def get_learning_status(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Returns the current status of learning processes.

        Args:
            task_id (Optional[str]): If provided, returns status for a specific learning task.
                                     Otherwise, returns general status.
        Returns:
            Dict[str, Any]: A dictionary describing the learning status.
                            Example: {'active_tasks': 2, 'last_learned_concept_id': 'c123',
                                      'current_meta_strategy': 'adaptive_learning_rate'}
        """
        pass

    @abstractmethod
    def apply_ethical_guardrails(self, potential_learning_outcome: Any, context: Dict[str, Any]) -> bool:
        """
        Evaluates a potential learning outcome (e.g., a new belief, skill, or policy)
        against the AGI's ethical framework (from SelfModel) before it's fully integrated.
        This is a crucial step for value alignment.

        Args:
            potential_learning_outcome (Any): The knowledge, skill, or policy that has been learned
                                              but not yet fully committed.
            context (Dict[str, Any]): Contextual information, including the source of learning
                                      and relevant ethical principles from the SelfModel.

        Returns:
            bool: True if the outcome is ethically permissible and can be integrated,
                  False if it violates ethical guardrails and should be rejected or modified.
        """
        pass
