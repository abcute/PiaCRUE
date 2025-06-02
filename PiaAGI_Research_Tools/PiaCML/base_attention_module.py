from abc import ABC, abstractmethod
from typing import Any, List, Dict

class BaseAttentionModule(ABC):
    """
    Abstract base class for an Attention Module.

    The Attention Module is responsible for managing the agent's limited processing
    resources by selectively concentrating on relevant internal or external information.
    It helps in filtering information, directing focus, and managing cognitive load.
    """

    @abstractmethod
    def direct_attention(self, focus_target: Any, priority: float, context: Dict[str, Any] = None) -> bool:
        """
        Directs the agent's attention to a specific target.

        Args:
            focus_target: The target to focus on (e.g., an object, a task, a concept).
            priority: The priority level of the focus target.
            context: Additional contextual information that might influence attention direction
                     (e.g., {'type': 'top-down', 'source': 'goal_system'}).

        Returns:
            bool: True if attention was successfully shifted, False otherwise.
        """
        pass

    @abstractmethod
    def filter_information(self, information_stream: List[Dict[str, Any]], current_focus: Any = None) -> List[Dict[str, Any]]:
        """
        Filters an incoming stream of information based on the current attentional focus
        or a provided override focus.

        Args:
            information_stream: A list of information items (e.g., percepts, memory cues).
                                Each item is expected to be a dictionary.
            current_focus: Optional. If provided, overrides the module's internal current focus
                           for this filtering operation.

        Returns:
            List[Dict[str, Any]]: The filtered list of information items deemed relevant.
        """
        pass

    @abstractmethod
    def manage_cognitive_load(self, current_load: float, capacity_thresholds: Dict[str, float]) -> Dict[str, Any]:
        """
        Assesses the current cognitive load and takes or suggests actions to manage it.

        Args:
            current_load: A float representing the current cognitive load (e.g., 0.0 to 1.0).
            capacity_thresholds: A dictionary defining load thresholds,
                                 e.g., {'optimal': 0.7, 'overload': 0.9}.

        Returns:
            Dict[str, Any]: A dictionary describing the action taken or suggested,
                            e.g., {'action': 'reduce_focus', 'details': 'Overload detected'}.
        """
        pass

    @abstractmethod
    def get_attentional_state(self) -> Dict[str, Any]:
        """
        Retrieves the current internal state of the attention module.

        Returns:
            Dict[str, Any]: A dictionary representing the attentional state,
                            e.g., {'current_focus': ..., 'priority': ..., 'active_filters': [], 'load_level': ...}.
        """
        pass
