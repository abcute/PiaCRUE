# PiaSE Environment Abstraction Layer (HAL) Specification

## 1. Overview

The PiaSE Environment Abstraction Layer (HAL) defines how diverse simulation environments are structured, managed, and interact with the PiaSE Core Simulation Engine and PiaAGI Agents. It ensures that new environments can be integrated into PiaSE with a consistent interface, promoting modularity and extensibility.

The HAL is primarily defined by the `Environment` abstract base class in `PiaAGI_Research_Tools/PiaSE/core_engine/interfaces.py`.

## 2. Core Principles

*   **Standardized Interaction:** All environments must implement the `Environment` interface.
*   **State Encapsulation:** Each environment is responsible for managing its own internal state. The HAL provides methods to expose necessary information (observations, state summaries) without revealing internal implementation details.
*   **Action Handling:** Environments define the actions they support and are responsible for processing `ActionCommand` objects received from agents and returning `ActionResult` objects.
*   **Configurability:** Environments should be configurable at initialization, allowing scenarios to define specific parameters, layouts, or conditions.

## 3. Key Components and Interfaces

### 3.1. `Environment` Abstract Base Class

(Located in `PiaAGI_Research_Tools/PiaSE/core_engine/interfaces.py`)

This class mandates the implementation of the following methods for any compliant environment:

*   **`reset(self) -> PerceptionData:`**
    *   Resets the environment to its defined initial state for a given scenario.
    *   Returns the initial `PerceptionData` for the primary agent (or a default agent if multiple exist and one is not specified).
    *   *Note: The conceptual design mentioned `reset` returning nothing, but returning initial perception for the (main) agent is more practical for starting the simulation loop.*

*   **`step(self, agent_id: str, action: ActionCommand) -> ActionResult:`**
    *   Processes an `ActionCommand` submitted by the specified `agent_id`.
    *   Updates the environment's internal state based on the action and internal dynamics.
    *   Returns an `ActionResult` detailing the outcome, including status, messages, and any immediate new perception data.

*   **`get_observation(self, agent_id: str) -> PerceptionData:`**
    *   Constructs and returns the current `PerceptionData` for the specified `agent_id`. This data should be based on the agent's sensory capabilities within the environment (e.g., location, line of sight, specific sensors).

*   **`get_state(self) -> Any:`**
    *   Returns a representation of the overall current state of the environment. This might be used for logging, debugging, or by a centralized controller. The exact format can be environment-specific but should be serializable.
    *   This is distinct from `get_observation`, which is agent-specific and filtered by sensory capabilities.

*   **`is_done(self, agent_id: str) -> bool:`**
    *   Checks if the simulation episode has concluded for the specified `agent_id` (e.g., agent achieved a goal, a terminal state is reached, or max steps exceeded for that agent's task).
    *   The core engine might use this or a global termination condition.

*   **`get_action_space(self, agent_id: Optional[str] = None) -> Dict[str, Any]:`**
    *   Returns a description of the valid actions available in the environment.
    *   This can be agent-specific if different agents have different capabilities.
    *   The structure should ideally be a dictionary describing action types and their parameter schemas (e.g., similar to the `action_schema` in `PiaAGI_Simulation_Environment.md`). Example:
        ```json
        {
            "go": {"parameters": {"direction": {"type": "string", "choices": ["north", "south", "east", "west"]}}},
            "take": {"parameters": {"item_name": {"type": "string"}}}
        }
        ```

*   **`get_environment_info(self) -> Dict[str, Any]:`** (New, inspired by conceptual design)
    *   Provides general information about the environment setup, such as its name, version, description, and potentially schemas for actions and perceptions if not fully covered by `get_action_space`.
    *   Example:
        ```json
        {
            "environment_name": "TextBasedRoom_v1",
            "description": "A simple text-based adventure environment.",
            "action_schema": { ... }, // As from get_action_space or more detailed
            "perception_schema": { // Describes structure of PerceptionData.sensor_data
                "visible_text": {"type": "string"},
                "objects_visible": {"type": "list", "item_schema": {"name": "string", "description": "string"}}
            }
        }
        ```

### 3.2. Data Structures (Pydantic Models)

(Located in `PiaAGI_Research_Tools/PiaSE/core_engine/interfaces.py`)

*   **`PerceptionData`**: Standardized format for sensory information provided to agents.
    *   `timestamp: float`
    *   `sensor_data: Dict[str, Any]` (e.g., `{"visual": np.array, "text": "description"}`)
    *   `messages: List[Dict[str, Any]]`
    *   `agent_specific_data: Optional[Dict[str, Any]]`
*   **`ActionCommand`**: Standardized format for actions submitted by agents.
    *   `action_type: str`
    *   `parameters: Dict[str, Any]`
*   **`ActionResult`**: Standardized format for the outcome of an action.
    *   `timestamp: float`
    *   `status: str` (e.g., "success", "failure")
    *   `new_perception_snippet: Optional[PerceptionData]`
    *   `message: Optional[str]`
    *   `details: Dict[str, Any]`

## 4. Environment Lifecycle in Simulation

1.  **Instantiation:** The Core Simulation Engine instantiates an environment based on scenario configuration.
2.  **Initialization:** The engine calls `env.reset()` to set up the initial state. The agent receives initial `PerceptionData`.
3.  **Execution Loop:**
    *   Agent calls `env.get_observation()` (or this is pushed by the engine).
    *   Agent decides on an `ActionCommand`.
    *   Engine calls `env.step(agent_id, action_command)`.
    *   Environment updates its state and returns `ActionResult`.
    *   Agent receives `ActionResult` (which might contain immediate perception updates or trigger a new `get_observation` call).
4.  **Termination:** The loop continues until `env.is_done()` is true for relevant agents or global termination conditions are met.

## 5. Implementing New Environments

To add a new environment to PiaSE:
1.  Create a new Python class that inherits from `Environment`.
2.  Implement all abstract methods defined in the `Environment` interface, using the specified Pydantic data models for inputs and outputs.
3.  Design the internal state representation specific to the new environment.
4.  Define the logic for how agent actions modify the state and what perceptions are generated.
5.  Ensure the environment is configurable through its `__init__` method, allowing scenarios to customize it.

## 6. Future Considerations

*   **Asynchronous Environments:** Support for environments that update independently of agent actions.
*   **Multi-Agent Synchronization:** More complex mechanisms for managing turns and simultaneous actions in multi-agent environments.
*   **Standardized Environment Configuration Files:** While scenarios will orchestrate setup, having a common way to define environment parameters (e.g., via YAML or JSON files loaded by the environment itself) could be beneficial.
```
