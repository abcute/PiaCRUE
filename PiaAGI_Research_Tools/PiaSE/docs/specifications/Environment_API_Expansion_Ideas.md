# PiaSE Environment API Expansion Ideas & Utility Library Concepts

**Document Version:** 1.0
**Date:** 2024-08-09
**Author:** Jules (PiaAGI Assistant)
**Status:** Conceptual Draft

## 1. Introduction

This document outlines conceptual ideas for expanding the PiaSE Environment API (defined in `PiaAGI_Research_Tools/PiaSE/core_engine/interfaces.py`) and proposes a small library of reusable components/utilities that could assist in the development of diverse PiaSE environments. These ideas aim to enhance the richness of agent-environment interaction and streamline environment creation.

## 2. Conceptual API Expansions (for `interfaces.py`)

These are suggestions for new optional fields or helper Pydantic models that could be added to the existing data structures in `interfaces.py`.

### 2.1. Enhancements to `PerceptionData` and Related Models

*   **`DetectedObject` Model:**
    *   Consider adding:
        *   `relative_position: Optional[Tuple[float, float, float]] = None`
            *   *Description:* XYZ coordinates of the object relative to the perceiving agent's current position and orientation.
        *   `size_dimensions: Optional[Tuple[float, float, float]] = None`
            *   *Description:* Approximate width, height, depth of the object in environment units.

*   **`PerceptionData` Model:**
    *   Consider adding:
        *   `global_environmental_cues: Optional[Dict[str, Any]] = Field(default_factory=dict)`
            *   *Description:* Key-value pairs describing ambient environmental conditions.
            *   *Examples:* `{"time_of_day": "evening", "weather_condition": "rainy", "ambient_noise_level": "low", "temperature_celsius": 15}`.
        *   `agent_internal_physiological_proxy: Optional[Dict[str, Any]] = Field(default_factory=dict)`
            *   *Description:* Simplified indicators of the agent's own physical or simulated-physical state, if relevant to the environment (e.g., for survival scenarios). Differs from `AgentStatePercept.internal_stats` which might be more cognitive.
            *   *Examples:* `{"energy_level": 0.75, "damage_level": 0.1, "hunger_level": 0.3}`.

### 2.2. Enhancements to `ActionCommand`

*   **More Specific Action Parameter Models (Conceptual - for `generic_parameters` or new fields):**
    *   While `generic_parameters` offers flexibility, for very common complex actions, dedicated Pydantic models could improve clarity and validation.
    *   **`ScanAreaParams(BaseModel)`:**
        *   `scan_radius: float`
        *   `target_types: Optional[List[str]] = None` (e.g., ["entity:plant", "object:interactive"])
        *   `resolution_level: Optional[str] = "medium"` (e.g., "low", "medium", "high" detail)
        *   *Usage:* `ActionCommand(action_type="SCAN_AREA", generic_parameters=ScanAreaParams(...).model_dump())` or `ActionCommand(action_type="SCAN_AREA", scan_params=ScanAreaParams(...))`.
    *   **`GetObjectDetailsParams(BaseModel)`:**
        *   `target_object_id: str`
        *   `detail_level: Optional[str] = "full"` (e.g., "summary", "full", "interaction_history")
        *   *Usage:* Similar to `ScanAreaParams`.
    *   **`CommunicateActionParams(BaseModel)`:** (If agent communication is mediated via environment actions)
        *   `target_agent_id: str`
        *   `message_content: Union[str, Dict[str, Any]]` (Could be text or structured message)
        *   `communication_style: Optional[str] = "neutral"`
        *   `intent_hint: Optional[str] = None` (e.g., "inform", "query", "request_cooperation")

### 2.3. Enhancements to `ActionResult`

*   **Standardized Keys for `custom_details`:**
    *   For common outcomes, suggest standardized keys within the `custom_details` dictionary to improve interoperability for agents and analysis tools.
    *   **Example for `INTERACT` action (e.g., "open_door"):**
        *   `custom_details: {"state_change_on_object": {"object_id": "door1", "attribute_changed": "is_open", "old_value": False, "new_value": True}, "interaction_success_level": 0.9}`
    *   **Example for `SCAN_AREA` action:**
        *   `custom_details: {"scan_results": {"entities_detected": [{"id": "e1", "label": "tree", ...}, ...], "area_description_text": "Dense forest patch."}}`
    *   **Example for `COMMUNICATE` action:**
        *   `custom_details: {"communication_outcome": "message_delivered", "recipient_acknowledged": True}` or `{"communication_outcome": "recipient_not_found"}`.

## 3. Reusable Environmental Component/Utility Library (Conceptual)

This section outlines ideas for a potential utility library (`PiaAGI_Research_Tools/PiaSE/utils/env_utilities.py` or similar) that could provide common functionalities for building PiaSE environments.

### 3.1. `EntityManager`

*   **Purpose:** A helper class to manage a collection of entities (e.g., `WorldEntity`-like objects) within an environment.
*   **Conceptual Methods:**
    *   `__init__(self)`: Initializes an internal dictionary or list for entities.
    *   `add_entity(self, entity_id: str, entity_data: Any) -> bool`: Adds or updates an entity.
    *   `remove_entity(self, entity_id: str) -> bool`: Removes an entity.
    *   `get_entity(self, entity_id: str) -> Optional[Any]`: Retrieves an entity by ID.
    *   `get_all_entities(self) -> List[Any]`: Returns all entities.
    *   `find_entities_by_property(self, property_name: str, value: Any) -> List[Any]`: Finds entities matching a property.
    *   `find_entities_by_type(self, entity_type: str) -> List[Any]`: Finds entities of a specific type.
    *   `find_entities_in_radius(self, center_pos: Tuple[float,float,float], radius: float, position_property_name: str = "position") -> List[Any]`: Finds entities within a given radius.

### 3.2. `SpatialUtils`

*   **Purpose:** A collection of static methods or a class providing common spatial calculations, primarily for 2D or 3D grid/continuous environments.
*   **Conceptual Methods:**
    *   `calculate_distance(cls, pos1: Tuple, pos2: Tuple, dimensions: int = 2) -> float`: Calculates Euclidean distance.
    *   `is_within_bounds(cls, pos: Tuple, bounds: Tuple) -> bool`: Checks if a point is within given boundaries.
    *   `get_adjacent_cells(cls, pos: Tuple[int,int], grid_size: Tuple[int,int], include_diagonals: bool = False) -> List[Tuple[int,int]]`: For grid environments.
    *   `line_of_sight(cls, start_pos: Tuple, end_pos: Tuple, obstacles: List[Tuple_bounds_or_points]) -> bool`: (More complex) Conceptual method for LoS checking.

### 3.3. `SimpleEventScheduler`

*   **Purpose:** A simple discrete-time event scheduler that environments can use to trigger time-based events (e.g., weather changes, NPC actions, resource regeneration).
*   **Conceptual Methods:**
    *   `__init__(self)`: Initializes an event queue.
    *   `schedule_event(self, delay_steps: int, event_callable: Callable, *args, **kwargs) -> str`: Schedules a function to be called after `delay_steps`. Returns an event ID.
    *   `cancel_event(self, event_id: str) -> bool`: Cancels a scheduled event.
    *   `tick(self) -> List[Callable]`: Called by the environment in its `step` method. Decrements delays and returns a list of callables for events that are now due.

## 4. Conclusion

These API expansion ideas and utility concepts aim to provide a richer and more developer-friendly foundation for creating diverse and complex simulation environments within PiaSE. Further refinement and prioritization would be needed based on specific research goals and agent capabilities being tested.
```
