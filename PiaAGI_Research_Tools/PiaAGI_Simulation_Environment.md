<!-- PiaAGI AGI Research Framework Document -->
# PiaAGI Simulation Environment (PiaSE) - Conceptual Design

## 1. Purpose and Goals

**Purpose:**
The PiaAGI Simulation Environment (PiaSE) is designed to provide a flexible and extensible platform for researchers and developers to instantiate, test, and evaluate PiaAGI agents ([Section 4 of `PiaAGI.md`](../PiaAGI.md#4-the-piaagi-cognitive-architecture)) and their components in controlled, dynamic, and reproducible settings.

**Goals:**
*   **Facilitate AGI Research:** Enable empirical investigation of AGI hypotheses related to learning, adaptation, social interaction, motivation, and emergent behavior within the PiaAGI framework.
*   **Testbed for PiaAGI Agents:** Allow for the deployment and rigorous testing of PiaAGI agents at various developmental stages ([Section 3.2.1 of `PiaAGI.md`](../PiaAGI.md#321-stages-of-cognitive-development-and-architectural-maturation)).
*   **Environment for Developmental Scaffolding:** Provide tools and functionalities to create and manage complex environments that can deliver the developmental scaffolding curricula described in [Section 5.4 of `PiaAGI.md`](../PiaAGI.md#54-developmental-scaffolding-a-cornerstone-of-piaagi-growth) and [Section 6.1 of `PiaAGI.md`](../PiaAGI.md#61-advanced-developmental-scaffolding-techniques-for-agi-cultivation).
*   **Reproducibility and Comparability:** Ensure experiments can be easily replicated, and results can be compared across different agent configurations or environmental conditions.
*   **Modular and Extensible:** Allow for the easy integration of new environments, tasks, sensors (simulated), actuators (simulated), and external AI models or services.
*   **Data Generation:** Generate rich datasets of agent-environment interactions, internal state changes, and performance metrics for analysis with tools like the PiaAGI Agent Analysis & Visualization Toolkit (PiaAVT).

## 2. Key Features and Functionalities

*   **Environment Engine:**
    *   Discrete and continuous environment types (e.g., grid worlds, physics-based 2D/3D environments, social simulation environments).
    *   Configurable environmental parameters, objects, and dynamics.
    *   Support for dynamic events and stochasticity.
    *   Ability to define and manage multiple interacting entities (other agents, simulated humans).
*   **Agent Interface:**
    *   Standardized API for PiaAGI agents to perceive the environment (multi-modal sensory input, [Section 4.1.1 of `PiaAGI.md`](../PiaAGI.md#41-core-modules-and-their-interactions)) and act upon it (behavioral outputs, [Section 4.1.9 of `PiaAGI.md`](../PiaAGI.md#41-core-modules-and-their-interactions)).
    *   Support for various action spaces (discrete, continuous, linguistic).
*   **Scenario and Task Management:**
    *   GUI and/or scripting interface to design and configure experimental scenarios and tasks.
    *   Define specific goals, rewards (if applicable), and success conditions for agents.
    *   Implement complex tasks requiring long-term planning, learning, and adaptation.
*   **Developmental Scaffolding Tools:**
    *   Mechanisms to introduce environmental changes or new tasks based on agent developmental stage ([Section 3.2.1 of `PiaAGI.md`](../PiaAGI.md#321-stages-of-cognitive-development-and-architectural-maturation)) or performance.
    *   Tools to simulate tutors or mentors providing feedback or guidance as part of a curriculum ([Section 5.4 of `PiaAGI.md`](../PiaAGI.md#54-developmental-scaffolding-a-cornerstone-of-piaagi-growth)).
*   **Multi-Agent Simulation:**
    *   Support for deploying multiple PiaAGI agents (or other AI agents) within the same environment.
    *   Configurable communication channels between agents.
    *   Tools to study emergent collective behaviors and inter-agent learning/collaboration ([Section 2.2 of `PiaAGI.md`](../PiaAGI.md#22-communication-theory-for-agi-level-interaction)).
*   **Data Logging and Recording:**
    *   Comprehensive logging of agent-environment interactions, agent's internal states (if exposed via API), events, and performance metrics.
    *   Ability to replay simulations.
*   **Extensibility:**
    *   Plugin architecture for new environment types, tasks, sensors, and actuators.
    *   Python API for scripting and controlling simulations.

## 3. Target Users

*   **AGI Researchers:** To test theories of general intelligence, learning, and cognition.
*   **PiaAGI Developers:** To debug, evaluate, and iteratively improve PiaAGI agents and their cognitive modules.
*   **Cognitive Scientists/Psychologists:** To model and simulate psychological theories of development, learning, and social interaction.
*   **AI Ethicists:** To study value alignment and ethical behavior of AGI agents in controlled scenarios.

## 4. High-level Architectural Overview

*   **Core Simulation Engine (Python-based):**
    *   Manages the simulation loop, time progression, and state updates.
    *   Event-driven architecture.
    *   Physics engine integration (e.g., PyBullet, MuJoCo if 3D physics needed, or simpler 2D physics).
    *   Networking capabilities for distributed simulations (optional).

    #### Core Simulation Loop

    The simulation progresses in discrete time steps or events. A typical loop might look like this:

    **A. Initialization Phase:**
    1.  **Load Configuration:** Load environment parameters, agent configurations, scenario details, and developmental curricula.
    2.  **Instantiate Environment:** Create the environment object(s) based on configuration.
    3.  **Instantiate Agents:** Create agent object(s), initialize their internal states, cognitive modules (PiaCML), and world models. Position agents in the environment.
    4.  **Set Initial Conditions:** Apply any scenario-specific starting conditions.

    **B. Main Simulation Loop (runs for a defined number of steps or until termination criteria are met):**
        For each time step / event:
        1.  **Environment Pre-Update (Optional):** Handle autonomous environmental changes or scheduled events (e.g., weather changes, resource regeneration).
        2.  **Agent Perception Phase:**
            *   For each agent:
                *   The environment provides sensory information to the agent based on its current state, location, and sensory capabilities (e.g., visual, auditory, textual). This is mediated by the Agent-Environment API.
                *   The agent's PerceptionModule processes this raw data.
        3.  **Agent Cognitive Phase (Internal Processing):**
            *   For each agent:
                *   The agent updates its internal World Model based on new perceptions.
                *   Motivational systems, emotional states, and learning modules process information.
                *   The agent engages its planning and decision-making modules to select an action or a sequence of actions. This may involve internal simulation or "thought".
        4.  **Agent Action Submission Phase:**
            *   For each agent:
                *   The agent submits its chosen action(s) to the environment via the Agent-Environment API.
        5.  **Environment Action Execution & State Update Phase:**
            *   The environment processes actions from all agents.
            *   Resolve conflicting actions (if any).
            *   Update the environment state based on agent actions and environment dynamics (physics, rules).
            *   Calculate action results (e.g., success/failure, consequences, rewards if applicable).
        6.  **Agent Feedback/Observation Phase:**
            *   For each agent:
                *   The environment provides feedback on the outcome of their action(s). This becomes part of the next perception cycle.
        7.  **Data Logging:**
            *   Log agent perceptions, actions, internal states (if exposed), environmental states, and any relevant metrics for analysis with PiaAVT.
        8.  **Termination Check:** Evaluate if scenario goals are met, maximum time steps reached, or other termination conditions satisfied. If so, break loop.
        9.  **Developmental Scaffolding Check (Optional):**
            *   Evaluate if conditions are met to trigger changes in the environment, task, or feedback mechanisms as per the active developmental curriculum.

    **C. Finalization Phase:**
    1.  **Save Final State:** Save the final state of the environment and agents.
    2.  **Generate Summary Report:** Compile overall performance metrics and scenario outcomes.
    3.  **Clean Up:** Release resources.

*   **Environment Abstraction Layer:**
    *   Defines a common interface for different types of environments.
    *   Allows for easy creation of new environments (e.g., `GridWorld`, `SocialDilemmaSim`, `PhysicsPlayground`).
        ```markdown
        Conceptually, this layer would define an abstract class, say `AbstractEnvironment`, with methods such
        as:
        *   `load_configuration(self, config_data: Dict) -> bool:` Loads environment-specific settings.
        *   `step(self, current_time_step: int) -> None:` Advances the environment's autonomous dynamics by one step.
        *   `get_current_state_snapshot(self, scope: Optional[str] = None) -> Dict:` Returns a snapshot of the environment's state.
        *   `reset_environment(self, scenario_config: Optional[Dict] = None) -> bool:` Resets the environment to an initial or specified state.
        *   `get_perceptual_data_for_agent(self, agent_id: str) -> PerceptionData:` Gathers and returns perception data for a specific agent. (Refers to the `PerceptionData` Pydantic model).
        *   `apply_action_from_agent(self, agent_id: str, action_command: ActionCommand) -> ActionResult:` Applies an agent's action and returns the result. (Refers to `ActionCommand` and `ActionResult` Pydantic models).
        *   `get_environment_info(self) -> EnvironmentInfo:` Returns the environment's schema and capabilities. (Refers to `EnvironmentInfo` Pydantic model).

        Specific environments like `GridWorld` or the conceptual `TextBasedRoom` would then implement this interface, providing concrete logic for these methods.
        ```
*   **Agent Management System:**
    *   Handles instantiation, lifecycle, and communication for one or more agents.
    *   Provides the standardized perception/action interface to agents.
        ```markdown
        Its key responsibilities include:
        *   **Agent Registration:** Managing the addition and removal of agents from the simulation.
        *   **Lifecycle Management:** Handling agent initialization, and potentially suspension/resumption or termination if the simulation supports it.
        *   **Perception Delivery:** For each agent, invoking the current environment's `get_perceptual_data_for_agent()` method and ensuring the `PerceptionData` is delivered to that agent (e.g., by calling a hypothetical `agent.receive_perception(data: PerceptionData)` method on the agent object).
        *   **Action Reception & Dispatch:** Receiving `ActionCommand` objects from agents (e.g., via a hypothetical `agent.get_chosen_action() -> ActionCommand` method) and dispatching them to the current environment's `apply_action_from_agent()` method.
        *   **Communication Relay (for multi-agent scenarios):** If agents communicate directly, this system might relay messages or manage shared communication channels.
        *   **ID Management:** Assigning and tracking unique IDs for agents within the simulation instance.
        *   **Synchronization:** Ensuring agent actions and perceptions are processed in a consistent order, especially in multi-agent settings (e.g., turn-based, real-time with event queues). This ties into the Core Simulation Engine's timing model.
        ```

    #### Agent-Environment API

    This API defines how agents perceive and interact with the environment. It's a crucial part of the "Agent Management System."

    **Core Interface (Conceptual Python):**

    ```python
    class EnvironmentInterface:
        def get_environment_info(self) -> dict:
            """Provides general information about the environment setup."""
            # Example: {"name": "TextBasedRoom", "version": "0.1", "description": "...", "max_agents": 1}
            raise NotImplementedError

        def get_perceptions(self, agent_id: str) -> dict:
            """
            Called by an agent to get its current sensory input from the environment.
            The structure of the returned dict is environment-specific.
            """
            raise NotImplementedError

        def submit_action(self, agent_id: str, action_command: dict) -> dict:
            """
            Called by an agent to submit an action to the environment.
            The structure of action_command and the returned result_data is environment-specific.
            Returns: A dictionary containing the outcome of the action.
            """
            raise NotImplementedError

        # Optional methods for more complex interactions:
        # def subscribe_to_event(self, agent_id: str, event_type: str, callback_url: str): pass
        # def query_environment_state(self, agent_id: str, query: dict) -> dict: pass
    ```

    **Data Structures (Refined with Pydantic-style Definitions):**

    To provide a more precise definition of the data exchanged between the agent and the environment, we can use Pydantic-style models. These also serve as a clear schema.

    *   **`PerceptionData` (from `get_perceptions`):**
        ```python
        from typing import List, Optional, Dict, Any
        from pydantic import BaseModel, Field # Assuming pydantic is a conceptual choice for schema definition

        class Message(BaseModel):
            sender: str = Field(..., description="ID of the message sender (e.g., 'system', 'agent_2')")
            content: str = Field(..., description="Text content of the message")
            timestamp: Optional[float] = Field(None, description="Timestamp of the message")

        class PerceptionData(BaseModel):
            timestamp: float = Field(..., description="Timestamp of this perception bundle")
            # General perceptions - highly environment-dependent
            raw_observations: Dict[str, Any] = Field(default_factory=dict, description="Environment-specific raw observations, e.g., sensor readings")

            # Example for a text-based or explicit communication environment
            visible_text: Optional[str] = Field(None, description="Primary textual description of the current scene/situation")
            messages: List[Message] = Field(default_factory=list, description="List of messages received since last perception update")

            # Example for an agent with an inventory
            inventory_update: Optional[Dict[str, Any]] = Field(None, description="Updates to the agent's inventory, e.g., {'added': ['item_x'], 'removed': ['item_y']}")

            # Feedback related to the agent's own state
            self_stats_feedback: Optional[Dict[str, Any]] = Field(None, description="Feedback on agent's internal stats, e.g., {'energy_level': 0.8, 'health': 1.0}")

            # For environments with explicit objects
            visible_entities: Optional[List[Dict[str, Any]]] = Field(None, description="List of entities currently perceivable by the agent, e.g., [{'id': 'obj1', 'type': 'box', 'properties': {'color': 'red'}}]" )

            # Action feedback from previous turn (if not part of a separate call)
            last_action_result: Optional[Dict[str, Any]] = Field(None, description="Simplified result of the last action, if directly tied to perception. Often handled by ActionCommandResult.")

        # Example Usage (conceptual):
        # perception = PerceptionData(
        #     timestamp=1678886400.5,
        #     visible_text="In a room.",
        #     messages=[Message(sender="system", content="A door opens.")],
        #     self_stats_feedback={"energy": 0.9}
        # )
        ```

    *   **`ActionCommand` (to `submit_action`):**
        ```python
        from typing import Dict, Any, Optional
        from pydantic import BaseModel, Field # Assuming pydantic

        class ActionCommand(BaseModel):
            action_type: str = Field(..., description="The type of action to perform, e.g., 'move', 'interact', 'communicate'")
            parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the action, e.g., {'direction': 'north', 'target_id': 'door_1'}")
            # Optional fields for more complex action specifications
            sequence_id: Optional[str] = Field(None, description="Identifier if this action is part of a sequence")
            execution_priority: Optional[float] = Field(None, description="Priority for this action if multiple can be submitted")

        # Example Usage (conceptual):
        # action_cmd = ActionCommand(action_type="move", parameters={"direction": "east", "speed": "normal"})
        # action_cmd_interact = ActionCommand(action_type="interact", parameters={"target_id": "lever_A", "interaction_type": "pull"})
        ```

    *   **`ActionResult` (from `submit_action`):**
        ```python
        from typing import Dict, Any, Optional, List
        from pydantic import BaseModel, Field # Assuming pydantic

        class ActionResult(BaseModel):
            status: str = Field(..., description="Status of the action execution (e.g., 'success', 'failure', 'in_progress', 'invalid_action')")
            message: Optional[str] = Field(None, description="Human-readable message about the action's outcome")

            # Specific outcomes or changes resulting from the action
            state_changes_summary: Optional[Dict[str, Any]] = Field(None, description="Summary of key state changes in the environment or agent caused by the action")
            rewards_obtained: Optional[Dict[str, float]] = Field(None, description="Any rewards or penalties incurred, e.g., {'score': 10, 'energy_cost': -0.1}")

            # Optionally, a snippet of new perception data immediately resulting from action.
            # However, full perception updates are typically handled by a subsequent get_perceptions() call.
            immediate_perception_snippet: Optional[Dict[str, Any]] = Field(None, description="A small, immediate perceptual update directly resulting from the action, if applicable.")

            error_details: Optional[str] = Field(None, description="Details if the action status is 'failure'")

        # Example Usage (conceptual):
        # result_success = ActionResult(status="success", message="Moved north successfully.", state_changes_summary={"agent_location": [10,11]})
        # result_fail = ActionResult(status="failure", message="Cannot move north, path blocked.", error_details="Wall encountered")
        ```

    *   **`EnvironmentInfo` (from `get_environment_info`):**
        ```python
        from typing import Dict, Any, Optional, List
        from pydantic import BaseModel, Field # Assuming pydantic

        class ActionSchema(BaseModel):
            description: Optional[str] = None
            parameters: Dict[str, Any] = Field(default_factory=dict, description="Dictionary of parameter names to their type or allowed values/schema. E.g., {'direction': {'type': 'string', 'enum': ['N','S','E','W']}}")

        class PerceptionFieldSchema(BaseModel):
            type: str = Field(..., description="Data type of the perception field (e.g., 'string', 'integer', 'list[object]')")
            description: Optional[str] = None
            is_optional: bool = False # Default to required unless specified

        class EnvironmentInfo(BaseModel):
            environment_name: str
            description: str
            version: Optional[str] = None
            action_schema: Dict[str, ActionSchema] = Field(..., description="Defines available actions and their parameters")
            perception_schema: Dict[str, PerceptionFieldSchema] = Field(..., description="Defines the structure of data returned by get_perceptions()")
            max_agents: Optional[int] = 1
            time_model: str = Field(..., description="Model of time progression (e.g., 'discrete_steps', 'real_time_ms')")
            custom_properties: Optional[Dict[str, Any]] = None

        # Example Usage (conceptual, partial):
        # env_info = EnvironmentInfo(
        #     environment_name="TextWorldDeluxe",
        #     description="...",
        #     action_schema={
        #         "move": ActionSchema(parameters={"direction": {"type": "string", "enum": ["N","S","E","W"]}}),
        #         "examine": ActionSchema(parameters={"target": {"type": "string"}})
        #     },
        #     perception_schema={
        #         "current_room_description": PerceptionFieldSchema(type="string"),
        #         "visible_objects": PerceptionFieldSchema(type="list[string]", is_optional=True)
        #     },
        #     time_model="discrete_steps"
        # )
        ```

*   **Scenario Definition Module:**
    *   Parses scenario/task definitions (e.g., from XML, JSON, or Python scripts).
    *   Initializes environment and agents according to the scenario.
        ```markdown
        The process managed by this module typically involves:
        1.  **Parsing & Validation:** Reading the scenario definition file (e.g., the YAML example for "The Lost Key") and validating its structure and content against a predefined schema (e.g., ensuring all required fields like `environment_type`, `initial_state`, `win_conditions` are present and correctly formatted).
        2.  **Environment Instantiation:** Dynamically instantiating the correct environment class (e.g., `TextBasedRoom`, `GridWorld`) based on the `environment_type` specified in the scenario. This uses the Environment Abstraction Layer.
        3.  **Environment Configuration:** Applying the `initial_state` data from the scenario file to the instantiated environment object (e.g., setting up room layouts, object properties, entity locations).
        4.  **Agent(s) Instantiation & Setup:**
            *   Creating instances of the agent(s) specified in the `agent_setup` section.
            *   If the scenario includes `initial_agent_config` (which might be a PiaPES prompt reference or direct settings), this module would ensure these configurations are passed to the agent during its initialization.
            *   Placing agents in their defined `start_room` or initial positions.
            *   Setting up their `initial_inventory` or other starting attributes.
        5.  **Goal & Condition Registration:** Communicating the `win_conditions` and `lose_conditions` from the scenario file to the Core Simulation Engine, which will monitor them during the simulation loop.
        6.  **Event Trigger Setup:** If the scenario defines specific event triggers (like the conceptual example in "The Lost Key"), this module configures the Core Simulation Engine or the environment itself to monitor for these triggers and execute their responses.
        ```
*   **Data Logging Service:**
    *   Collects and stores data from various sources within the simulation.
    *   Outputs logs in standard formats (e.g., CSV, HDF5, databases).
        ```markdown
        Key aspects of this service include:
        *   **Interface Adherence:** The service should implement a well-defined `LoggerInterface` (conceptual), allowing different logging backends (console, file, database) to be plugged in.
        *   **Configurable Detail Levels:** Users should be able to configure the verbosity of logs (e.g., "DEBUG", "INFO", "CRITICAL_EVENTS_ONLY") globally or per module/agent.
        *   **Standardized Log Format:** All log entries must adhere to the format specified in `PiaAGI_Research_Tools/PiaAVT/Logging_Specification.md` to ensure compatibility with the PiaAVT toolkit. This typically involves JSONL (JSON Lines) with common fields like `timestamp`, `source_type` (e.g., "AGENT", "ENVIRONMENT", "SIMULATOR"), `source_id`, `event_type`, and a flexible `payload` dictionary.
        *   **Data Categories to Log (Examples):**
            *   `SIMULATOR_EVENT`: e.g., scenario_start, scenario_end, step_begin, max_steps_reached.
            *   `ENVIRONMENT_STATE_CHANGE`: e.g., object_moved, door_opened, resource_updated.
            *   `AGENT_PERCEPTION`: The full `PerceptionData` object received by an agent.
            *   `AGENT_ACTION_SUBMITTED`: The full `ActionCommand` object submitted by an agent.
            *   `AGENT_ACTION_RESULT`: The full `ActionResult` object received by an agent.
            *   `AGENT_INTERNAL_STATE` (Optional, if exposed by agent): Snapshots of key internal variables from CML modules (e.g., SelfModel confidence, EmotionModule VAD state, active goals from MotivationalSystem). Requires careful consideration of data volume and agent encapsulation.
            *   `AGENT_REWARD_PENALTY`: For reinforcement learning scenarios, specific reward/penalty signals received.
            *   `AGENT_LEARNING_EVENT`: e.g., model_update_in_LearningModule, new_knowledge_consolidated_in_LTM.
        *   **Output Destinations:** Configurable outputs, minimally to local files (e.g., `.jsonl`). Conceptually, could extend to databases or streaming platforms for larger-scale experiments.
        *   **Timestamping:** All log entries must be accurately timestamped, using either simulation time steps or wall-clock time as appropriate for the simulation mode.
        ```
*   **Visualization Interface (Optional but Recommended):**
    *   Real-time or post-hoc visualization of the environment and agent states (e.g., using Pygame, Matplotlib, or web-based frameworks).

**Potential Technologies:**
*   **Primary Language:** Python
*   **Physics:** PyBullet, Box2D, or custom solutions.
*   **Multi-Agent:** Libraries like `mesa` for agent-based modeling or custom frameworks.
*   **GUI:** PyQt, Kivy, or a web-based interface (e.g., Flask/Django with Three.js for 3D).
*   **Data Handling:** Pandas, NumPy, HDF5.

## 5. Potential Integration Points with the PiaAGI Framework

*   **PiaAGI Agent Core:** PiaSE will directly host and interact with instantiations of PiaAGI agents, providing them with perceptual input ([Section 4.1.1 of `PiaAGI.md`](../PiaAGI.md#41-core-modules-and-their-interactions)) and receiving action commands ([Section 4.1.9 of `PiaAGI.md`](../PiaAGI.md#41-core-modules-and-their-interactions)).
*   **Cognitive Module Library (PiaCML):** Components from PiaCML can be used to build the PiaAGI agents that run within PiaSE. The simulation environment will provide the necessary stimuli and feedback for these modules to operate and learn.
*   **World Model ([Section 4.3 of `PiaAGI.md`](../PiaAGI.md#43-perception-and-world-modeling-conceptual)):** PiaSE provides the "ground truth" environment against which an agent's internal World Model is developed, updated, and validated. Discrepancies between PiaSE state and agent's World Model can drive learning.
*   **Learning Modules ([Section 3.1.3 of `PiaAGI.md`](../PiaAGI.md#313-learning-theories-and-mechanisms-for-agi), [Section 4.1.5 of `PiaAGI.md`](../PiaAGI.md#41-core-modules-and-their-interactions)):** PiaSE provides the experiential data (observations, actions, feedback, rewards) necessary for all forms of learning defined in PiaAGI.
*   **Motivational System ([Section 3.3 of `PiaAGI.md`](../PiaAGI.md#33-motivational-systems-and-intrinsic-goals), [Section 4.1.6 of `PiaAGI.md`](../PiaAGI.md#41-core-modules-and-their-interactions)):** Environmental challenges, opportunities, and feedback within PiaSE can trigger and shape the agent's intrinsic and extrinsic motivations.
*   **Developmental Scaffolding ([Section 5.4 of `PiaAGI.md`](../PiaAGI.md#54-developmental-scaffolding-a-cornerstone-of-piaagi-growth), [Section 6.1 of `PiaAGI.md`](../PiaAGI.md#61-advanced-developmental-scaffolding-techniques-for-agi-cultivation)):** PiaSE is the primary platform for implementing developmental curricula. Its tools will allow researchers to design sequences of environments and tasks that progressively challenge the PiaAGI agent, fostering its cognitive development through stages.
*   **PiaAGI Prompt Engineering Suite (PiaPES):** Prompts designed with PiaPES can be used to configure the PiaAGI agent's initial state (Self-Model, personality, role) before it is deployed in a PiaSE scenario.
*   **Agent Analysis & Visualization Toolkit (PiaAVT):** Data logs generated by PiaSE will be a primary input for PiaAVT, allowing for detailed analysis of agent behavior and internal states.

## 6. Conceptual Design: TextBasedRoom Environment Example

This section outlines a conceptual example of a simple environment within PiaSE: the "TextBasedRoom."

### 6.1 Overview

The TextBasedRoom is designed as a basic environment for testing fundamental agent capabilities such as navigation, object interaction, simple puzzle solving, and understanding textual descriptions. It simulates a classic text adventure game format.

### 6.2 State Representation (Internal)

PiaSE would maintain the state of the TextBasedRoom internally. This is not directly exposed to the agent but forms the basis for perceptions.

*   **`room_layout`**: Defines rooms, their descriptions, and connections.
    ```json
    {
        "study": {
            "description": "a dimly lit study. There is a large desk and a bookshelf.",
            "exits": {"north": "hallway", "west": "library"},
            "objects": ["desk", "bookshelf"]
        },
        "hallway": {
            "description": "a dusty hallway. A grandfather clock stands in the corner.",
            "exits": {"south": "study", "east": "kitchen"},
            "objects": ["clock"]
        }
    }
    ```
*   **`object_details`**: Defines properties of objects within rooms.
    ```json
    {
        "desk": {
            "description": "a large oak desk.",
            "is_container": true,
            "is_open": false,
            "contains": ["journal", "pen"],
            "custom_properties": {"locked": true, "key_required": "small_silver_key"}
        },
        "journal": {
            "description": "a leather-bound journal.",
            "can_be_taken": true,
            "read_text": "Day 1: The key to the old chest is hidden where time stands still."
        }
    }
    ```
*   **`agent_states`**: Tracks agent-specific information.
    ```json
    {
        "agent_1": {
            "current_room": "study",
            "inventory": ["torch"],
            "flags": {"has_read_journal": false}
        }
    }
    ```

### 6.3 Agent Perceptions (via get_perceptions())

PiaSE translates the internal state into perceptions for the agent. For TextBasedRoom, this would primarily be textual descriptions.

Example Perception JSON for `agent_1` in the "study":
```json
{
    "timestamp": 1678886400.5,
    "room_name": "Study",
    "description": "You are in a dimly lit study. There is a large desk and a bookshelf. Exits are north and west.",
    "objects_visible": [
        {"name": "desk", "description": "a large oak desk."},
        {"name": "bookshelf", "description": "a tall bookshelf."}
    ],
    "inventory": ["torch"],
    "messages": []
}
```

### 6.4 Agent Actions (via submit_action())

Agents can submit actions like:
*   `look`: (Optional target) Provides a detailed description of the room or an object.
*   `go <direction>`: Moves the agent to an adjacent room.
*   `take <object>`: Adds an object to the agent's inventory if takeable.
*   `drop <object>`: Removes an object from inventory and places it in the room.
*   `open <object>` / `close <object>`: Changes state of openable containers.
*   `use <item_from_inventory> on <target_object>`: E.g., `use key on desk`.
*   `read <object>`: If the object has readable text.

Action commands would follow the structure defined in the Agent-Environment API, e.g.:
```json
{ "action_type": "go", "parameters": { "direction": "north" } }
```
```json
{ "action_type": "take", "parameters": { "item_name": "journal" } }
```

The environment processes these, updates its internal state, and returns an Action Result.

### 6.5 Environment Dynamics

*   Objects can change state (e.g., locked/unlocked, open/closed).
*   Some actions might trigger scripted events (e.g., finding an item triggers a message).
*   Time can advance, but in a simple TextBasedRoom, it's often event-driven by agent actions.

### 6.6 Scenario Definition Format ("The Lost Key" Example)

To make environments reusable and experiments configurable, PiaSE needs a way to define specific scenarios. Here’s a conceptual YAML format for defining a scenario in the TextBasedRoom.

```yaml
scenario_name: "The Lost Key"
environment_type: "TextBasedRoom"
version: "1.0"

description: >
  The agent must find a lost key to open a locked desk drawer
  and retrieve a hidden document.

# Initial Environment Setup (Overrides or extends base TextBasedRoom definitions)
initial_state:
  rooms:
    study:
      description: "a quiet study. A large wooden desk sits centrally. A bookshelf lines one wall."
      exits: { north: "hallway" }
      objects: ["desk", "bookshelf"]
    hallway:
      description: "a short, dusty hallway. A grandfather clock is against the far wall."
      exits: { south: "study" }
      objects: ["grandfather_clock"]

  object_details:
    desk:
      description: "a sturdy oak desk with a single drawer."
      is_container: true
      is_open: false
      contains: ["old_document"] # Initially hidden
      custom_properties: { locked: true, key_required: "brass_key" }
    bookshelf:
      description: "a tall bookshelf filled with dusty tomes."
      custom_properties: { searchable: true } # A clue might be here
    grandfather_clock:
      description: "an old grandfather clock. Its pendulum is still."
      custom_properties: { "hidden_item": "brass_key" } # Key is hidden here
    old_document:
      description: "a rolled-up parchment."
      can_be_taken: true
      read_text: "The formula is E=mc^2."

  agent_setup:
    agent_id: "PiaAgent_001"
    start_room: "study"
    initial_inventory: ["flashlight"]
    # Initial internal state overrides for the agent (PiaPES might set this)
    # initial_agent_config:
    #   self_model: { "mood": "curious" }
    #   goals: [{ "type": "find_item", "item_name": "old_document"}]

# Goal and Termination Conditions
win_conditions:
  - type: "item_in_inventory"
    agent_id: "PiaAgent_001"
    item_name: "old_document"
  - type: "flag_set" # Example alternative
    agent_id: "PiaAgent_001"
    flag_name: "document_secured"

lose_conditions:
  - type: "max_steps_reached"
    steps: 200
  # - type: "agent_state_condition"
  #   agent_id: "PiaAgent_001"
  #   condition: "energy <= 0" # If energy was a mechanic

# (Optional) Developmental Scaffolding Hooks / Event Triggers
# events:
#   - trigger:
#       type: "action_taken"
#       action_type: "look"
#       target: "bookshelf"
#       count: 3 # e.g. if agent looks at bookshelf 3 times
#     response:
#       type: "message_to_agent"
#       agent_id: "PiaAgent_001"
#       content: "You notice a faint shimmer behind one of the larger books on the middle shelf."
#   - trigger:
#       type: "item_found"
#       item_name: "brass_key"
#     response:
#       type: "log_milestone"
#       milestone_name: "key_found_by_agent"

```

#### Key Aspects of this Scenario Definition Format:
*   **Metadata:** Basic info like name, environment type.
*   **Initial State:** Defines the specific layout, object properties, and agent starting conditions for this scenario, potentially overriding defaults from a base environment definition.
*   **Goal and Termination:** Clearly defines what constitutes success or failure.
*   **Extensibility:** Could include hooks for more complex event triggers or scaffolding (commented out above for brevity but shows potential).

#### How PiaSE would use this:
1.  PiaSE's Scenario Definition Module would parse this YAML.
2.  It would instantiate the specified `environment_type` (TextBasedRoom).
3.  It would then apply all `initial_state` configurations to this environment instance.
4.  It would set up the agent(s) as defined.
5.  The simulation loop would run, checking against `win_conditions` and `lose_conditions` at appropriate times.
6.  (Optional) Event triggers would be monitored and responses executed.

This simulation environment will be a critical tool for the empirical validation and iterative refinement of the PiaAGI framework and its constituent agents.

---
Return to [PiaAGI Core Document](../PiaAGI.md) | [Project README](../README.md)
