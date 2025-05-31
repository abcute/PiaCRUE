from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class BaseWorldModel(ABC):
    """
    Abstract Base Class for a World Model within the PiaAGI Cognitive Architecture.

    The World Model maintains an internal representation of the environment,
    including objects, agents, their states, relationships, and the dynamics
    that govern them. It's crucial for situational awareness, prediction,
    planning, and common-sense reasoning.

    Refer to PiaAGI.md Section 4.3 (Perception and World Modeling) for more context.
    """

    @abstractmethod
    def update_model_from_perception(self, perception_output: Dict[str, Any]) -> bool:
        """
        Updates the world model based on structured information from the Perception Module.

        Args:
            perception_output (Dict[str, Any]): The structured output from the
                                                Perception Module. This might include
                                                identified entities, their properties,
                                                detected events, etc.
                                                Example: {'entities': [{'id': 'obj1', 'type': 'apple', 'color': 'red'}],
                                                          'events': [{'type': 'movement', 'object_id': 'obj1'}]}

        Returns:
            bool: True if the model was successfully updated, False otherwise.
        """
        pass

    @abstractmethod
    def get_entity_state(self, entity_id: str, attribute: Optional[str] = None) -> Optional[Any]:
        """
        Retrieves the current state or a specific attribute of an entity in the world model.

        Args:
            entity_id (str): The unique identifier of the entity.
            attribute (Optional[str]): The specific attribute to retrieve (e.g., "location",
                                       "color", "is_open"). If None, returns the full state dict.

        Returns:
            Optional[Any]: The value of the attribute, the full entity state dict,
                           or None if the entity or attribute is not found.
        """
        pass

    @abstractmethod
    def get_environment_property(self, property_name: str) -> Optional[Any]:
        """
        Retrieves a general property of the environment model.

        Args:
            property_name (str): The name of the environment property to retrieve
                                 (e.g., "time_of_day", "weather_condition", "threat_level").

        Returns:
            Optional[Any]: The value of the property, or None if not found.
        """
        pass

    @abstractmethod
    def predict_action_outcome(self, action: Dict[str, Any], current_world_state_summary: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Predicts the likely outcome or changes to the world state if a given action is performed.
        This is a conceptual method; concrete implementations will vary greatly in sophistication.

        Args:
            action (Dict[str, Any]): A representation of the action to be performed.
                                     Example: {'type': 'move', 'agent_id': 'self', 'target_location': 'x,y'}
            current_world_state_summary (Optional[Dict[str, Any]]): A summary of the current
                                                                    world state relevant to the action,
                                                                    if not implicitly using the full model.

        Returns:
            Dict[str, Any]: A representation of the predicted outcome.
                            Example: {'predicted_state_changes': [{'entity_id': 'self', 'new_location': 'x,y'}],
                                      'success_probability': 0.9,
                                      'potential_side_effects': []}
        """
        pass

    @abstractmethod
    def get_uncertainty_level(self, area: Optional[str] = None) -> float:
        """
        Returns a conceptual measure of uncertainty within the world model.

        Args:
            area (Optional[str]): A specific area or aspect of the model for which
                                  to assess uncertainty (e.g., "entity_obj1_location",
                                  "weather_forecast"). If None, returns overall uncertainty.

        Returns:
            float: A value representing the uncertainty level (e.g., 0.0 for certain,
                   1.0 for completely uncertain).
        """
        pass

    @abstractmethod
    def get_module_status(self) -> Dict[str, Any]:
        """
        Returns the current status of the World Model module.

        Returns:
            Dict[str, Any]: A dictionary describing the module's status.
                            Example: {'entities_tracked': 150, 'last_update_timestamp': 12345.678,
                                      'overall_consistency_metric': 0.95}
        """
        pass
