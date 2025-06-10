from abc import abstractmethod
from typing import Any, List, Dict
from .base_memory_module import BaseMemoryModule # Assuming base_memory_module.py is in the same directory

class WorkingMemoryModule(BaseMemoryModule):
    """
    Abstract Base Class for the Working Memory (WM) module in the PiaAGI Cognitive Architecture.

    Working Memory is conceptualized as a limited-capacity system responsible for temporarily
    holding, processing, and manipulating information relevant to the current cognitive tasks.
    It acts as a central hub for information from perception, LTM, and for intermediate
    results of reasoning and planning. The Central Executive is a key component of WM,
    responsible for attention, control, and coordination.

    Refer to PiaAGI.md Sections 3.1.1 (Memory Systems - WM), 3.1.2 (Attention and Cognitive Control - Central Executive),
    and 4.1.2 (Working Memory Module) for detailed context.
    """

    @abstractmethod
    def add_item_to_workspace(self, item: Any, source_module: str, context: Dict = None) -> bool:
        """
        Adds an item to the active workspace of Working Memory.

        Items can be diverse: processed perceptual chunks, retrieved LTM items,
        intermediate thoughts or hypotheses, goals, etc. The source module helps in
        tracking information flow and relevance. Context can include priority, saliency.

        Args:
            item (Any): The information item to add to the workspace.
                        Its structure will vary (e.g., a dict, a data object).
            source_module (str): The name of the module providing the item (e.g., "PerceptionModule", "LTMModule").
            context (Dict, optional): Additional context like priority, saliency, relation to current goal.
                                      Example: {'priority': 'high', 'saliency': 0.9, 'goal_id': 'goal_001'}

        Returns:
            bool: True if the item was successfully added, False otherwise (e.g., if WM is at capacity
                  and cannot make space).
        """
        # This would internally call the base `store` method after appropriate formatting for WM.
        pass

    @abstractmethod
    def get_workspace_contents(self, criteria: Dict = None) -> List[Any]:
        """
        Retrieves items currently active in the workspace, potentially filtered by criteria.

        Args:
            criteria (Dict, optional): Criteria to filter items, e.g., by source, type, recency.
                                       Example: {'source_module': 'LTMModule', 'max_age_seconds': 5}

        Returns:
            List[Any]: A list of items currently in the workspace matching the criteria.
        """
        # This would internally call the base `retrieve` method.
        pass

    @abstractmethod
    def update_item_in_workspace(self, item_id: Any, new_content: Any = None, new_context: Dict = None) -> bool:
        """
        Updates an existing item within the workspace. 
        This could involve changing its content, its saliency, or other contextual attributes.

        Args:
            item_id (Any): Identifier for the item to be updated in the workspace.
            new_content (Any, optional): The new content for the item.
            new_context (Dict, optional): The new context for the item.

        Returns:
            bool: True if update was successful, False otherwise.
        """
        pass
        
    @abstractmethod
    def remove_item_from_workspace(self, item_id: Any) -> bool:
        """
        Removes a specific item from the workspace, e.g., when it's no longer relevant
        or has been encoded into LTM.

        Args:
            item_id (Any): Identifier for the item to be removed.

        Returns:
            bool: True if removal was successful, False otherwise.
        """
        pass

    @abstractmethod
    def clear_workspace(self) -> None:
        """
        Clears all items from the working memory workspace.
        This might be used when switching tasks completely or resetting context.
        """
        pass

    @abstractmethod
    def get_cognitive_load(self) -> float:
        """
        Returns an estimate of the current cognitive load on Working Memory.
        This could be based on the number of items, complexity of items,
        processing demands, etc. Useful for the Central Executive and Self-Model.

        Returns:
            float: A value representing cognitive load (e.g., a percentage from 0.0 to 1.0).
        """
        pass

    # Methods related to the Central Executive (conceptual, as CE is part of WM)

    @abstractmethod
    def allocate_attentional_resources(self, task_priority: Dict) -> bool:
        """
        Simulates the Central Executive function of allocating attention to specific
        tasks or information streams based on priority.

        Args:
            task_priority (Dict): A dictionary specifying tasks and their priorities.
                                  Example: {'task_A_processing': 'high', 'background_monitoring': 'low'}
        Returns:
            bool: True if allocation was successful/updated.
        """
        pass

    @abstractmethod
    def coordinate_modules(self, task_goal: str, required_modules: List[str]) -> Dict:
        """
        Simulates the Central Executive's role in coordinating other cognitive modules
        to achieve a specific task goal. This is a high-level conceptual method.

        Args:
            task_goal (str): The goal to be achieved (e.g., "understand_user_query").
            required_modules (List[str]): List of module names needed for the task.

        Returns:
            Dict: A status or result from the coordination effort.
                  Example: {'status': 'coordination_initiated', 'task_id': 'task_123'}
        """
        pass
        
    # BaseMemoryModule methods that still need to be implemented by concrete classes
    # store, retrieve, manage_capacity, handle_forgetting, get_status
    # Their specific implementations for WM will differ significantly from LTM.
    # For example, WM's `store` is more like `add_item_to_workspace`, `retrieve` like `get_workspace_contents`.
    # `manage_capacity` is critical due to WM's limited size.
    # `handle_forgetting` in WM might be rapid decay or displacement.

# End of WorkingMemoryModule class definition
# No if __name__ == '__main__': block
