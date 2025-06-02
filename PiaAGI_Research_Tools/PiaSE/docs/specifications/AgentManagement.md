# PiaSE Agent Management Specification

## 1. Overview

The PiaSE Agent Management system defines how PiaAGI agents are instantiated, managed throughout their lifecycle, and interact with the Core Simulation Engine and Environments. It relies on the `AgentInterface` abstract base class and the data structures defined in `PiaAGI_Research_Tools/PiaSE/core_engine/interfaces.py`.

## 2. Core Principles

*   **Standardized Interface:** All agents intended to run within PiaSE must implement the `AgentInterface`.
*   **Unique Identification:** Each agent instance within a simulation run must have a unique `agent_id`.
*   **Decoupling:** Agents are decoupled from the specifics of the simulation engine and environment, interacting solely through the defined interfaces and data structures.
*   **State Encapsulation:** Agents manage their own internal state (cognitive models, knowledge, etc.). The `AgentInterface` provides methods for interaction, not direct state manipulation from outside.

## 3. Key Components and Interfaces

### 3.1. `AgentInterface` Abstract Base Class

(Located in `PiaAGI_Research_Tools/PiaSE/core_engine/interfaces.py`)

This class mandates the implementation of the following methods for any compliant agent:

*   **`set_id(self, agent_id: str):`**
    *   Called by the simulation engine during agent registration to assign a unique identifier.
*   **`get_id(self) -> str:`**
    *   Returns the agent's unique identifier.
*   **`perceive(self, observation: PerceptionData, event: Optional[PiaSEEvent] = None):`**
    *   The primary method for the simulation engine to provide sensory information (`PerceptionData`) and asynchronous events (`PiaSEEvent`) to the agent.
    *   The agent is responsible for processing this input and updating its internal state/world model.
*   **`act(self) -> ActionCommand:`**
    *   Called by the simulation engine to request an action from the agent.
    *   The agent, based on its internal state and decision-making processes, returns an `ActionCommand` object specifying the action it wishes to perform.
*   **`learn(self, feedback: ActionResult):`**
    *   Called by the simulation engine after an agent's action has been processed by the environment.
    *   The `ActionResult` provides feedback (e.g., success/failure of the action, rewards, changes in state) that the agent can use for learning and adaptation.
*   **`initialize_q_table(self, state: Any, action_space: list):`** (Specific to Q-learning agents, may be part of a sub-interface or mixin in the future)
    *   Initializes or re-initializes the Q-table. This highlights that agents can have specialized initialization methods.
*   **`get_q_value(self, state: Any, action: Any) -> float:`** (Specific to Q-learning agents)
*   **`update_q_value(self, state: Any, action: Any, reward: float, next_state: Any, learning_rate: float, discount_factor: float, action_space: list):`** (Specific to Q-learning agents)

### 3.2. Data Structures

The agent interacts using `PerceptionData`, `ActionCommand`, `ActionResult`, and `PiaSEEvent` as defined in `interfaces.py`.

## 4. Agent Lifecycle in Simulation

1.  **Definition & Configuration:**
    *   Agent classes are defined (implementing `AgentInterface`).
    *   A scenario configuration specifies which agent classes to use, how many instances, their unique IDs, and any initial configuration parameters (e.g., specific cognitive module settings, initial knowledge, personality traits loaded via PiaPES).
2.  **Instantiation:**
    *   The Core Simulation Engine instantiates the agent object(s) based on the scenario configuration.
    *   Agent `__init__` method is called.
3.  **Registration and ID Assignment:**
    *   The engine calls `agent.set_id(unique_agent_id)` for each agent instance.
    *   The engine may also call other agent-specific initialization methods if defined (e.g., `initialize_q_table` or a more generic `setup(config_dict)`).
4.  **Initial Perception:**
    *   After the environment is reset, the engine provides the initial `PerceptionData` to each agent via `agent.perceive()`.
5.  **Simulation Loop (Agent's Perspective):**
    *   **Think/Decide:** The engine calls `agent.act()`. The agent performs its internal cognitive processing (which might have been triggered by the last `perceive` call) and returns an `ActionCommand`.
    *   **Action Submitted:** The engine takes the `ActionCommand` and passes it to the environment.
    *   **Receive Feedback:** The environment processes the action and returns an `ActionResult`. The engine passes this to `agent.learn(action_result)`.
    *   **Receive New Percepts/Events:** The engine provides updated `PerceptionData` (either from `ActionResult.new_perception_snippet` or a subsequent `environment.get_observation()`) and any relevant `PiaSEEvent`s to `agent.perceive()`.
    *   The loop (Think -> Act -> Feedback -> Perceive) continues.
6.  **Termination:**
    *   When the simulation ends (due to scenario completion, agent termination conditions, or external stop), the agent instances might be cleaned up.
    *   A method like `agent.on_simulation_end()` could be added to `AgentInterface` for agents needing to perform cleanup or save final state.

## 5. Agent Configuration

*   Agents should be configurable at instantiation. Their `__init__` method can accept parameters for:
    *   Cognitive module configurations (linking to PiaCML).
    *   Learning algorithm parameters (e.g., learning rate, discount factor).
    *   Initial knowledge or memory states.
    *   Personality profiles or role definitions (potentially loaded via PiaPES).
*   The scenario definition will be responsible for providing these configurations.

## 6. Future Considerations

*   **Agent Capabilities:** A mechanism for agents to declare their capabilities (e.g., types of actions they can perform, sensors they possess) which could be matched against environment requirements.
*   **Dynamic Agent Loading:** Loading agent code dynamically at runtime.
*   **Inter-Agent Communication:** Defining a formal interface or system for agents to send messages or signals to each other, potentially managed by the simulation engine or a dedicated communication module.
*   **Hierarchical Agents:** Support for agents composed of sub-agents.
*   **Standardized Agent State Saving/Loading:** A common mechanism for serializing and deserializing an agent's internal state for persistence or migration.
*   **Refined Agent Sub-typing:** Consider sub-interfaces for different types of agents (e.g., `LearningAgentInterface`, `ReactiveAgentInterface`) to better manage method signatures like Q-table methods.
```
