# PiaSE Scenario Definition Module Specification

## 1. Overview

The PiaSE Scenario Definition Module is responsible for defining, loading, and initializing specific experimental setups within the PiaSE framework. A scenario encompasses the choice of environment, its configuration, the agents involved, their configurations, and the conditions for starting, running, and terminating the simulation.

Initially, scenarios will be defined as Python scripts or modules, offering flexibility and direct access to PiaSE components. Future iterations might incorporate declarative formats like YAML or JSON, building upon the Python-based foundation.

## 2. Core Principles

*   **Programmable Setup:** Scenarios are defined using Python code, allowing for complex initialization logic and direct instantiation of environment and agent objects.
*   **Clear Structure:** Scenario files should follow a recognizable structure for clarity and maintainability.
*   **Parameterization:** Scenarios should be easily parameterizable (e.g., by modifying constants within the script or, in the future, by loading external configuration files).
*   **Self-Contained:** Each scenario script should contain all necessary information to set up and run a specific experiment, relying on the Core Simulation Engine to execute it.

## 3. Scenario Script Structure (Python-based)

A typical scenario Python script (`.py` file) located in `PiaAGI_Research_Tools/PiaSE/scenarios/` would generally include:

1.  **Imports:**
    *   Import necessary PiaSE components (Core Engine, specific Environment classes, specific Agent classes, interfaces, data structures).
    *   Import any other required libraries (e.g., `numpy`, `random`).

2.  **Configuration Variables (Optional but Recommended):**
    *   Define constants or variables at the top of the script for easy modification of scenario parameters (e.g., `NUM_AGENTS`, `GRID_SIZE`, `MAX_SIMULATION_STEPS`).

3.  **Environment Setup Function:**
    *   A function, e.g., `setup_environment(config: Optional[Dict] = None) -> Environment:`, that:
        *   Instantiates the chosen environment class (e.g., `GridWorld`, `TextBasedRoom`).
        *   Configures the environment (e.g., map layout, object placements, specific environmental conditions).
        *   Returns the configured environment instance.

4.  **Agent Setup Function:**
    *   A function, e.g., `setup_agents(env_info: Dict, config: Optional[Dict] = None) -> List[AgentInterface]:`, that:
        *   Takes environment information (e.g., from `env.get_environment_info()` or `env.get_action_space()`) which might be needed for agent initialization.
        *   Instantiates the chosen agent class(es).
        *   Configures each agent (e.g., learning parameters, initial knowledge, cognitive settings from PiaCML/PiaPES).
        *   Assigns temporary IDs if needed (final IDs are set by the engine during registration).
        *   Returns a list of configured agent instances.

5.  **Main Execution Block/Function:**
    *   A main function, e.g., `run_scenario(custom_config: Optional[Dict] = None):`, or code under `if __name__ == "__main__":` that:
        *   Instantiates the `BasicSimulationEngine` (or other chosen engine).
        *   Calls `setup_environment()` to get the environment.
        *   Calls `setup_agents()` to get the list of agents.
        *   Registers each agent with the engine using `engine.register_agent(agent_id, agent_instance)`. Agent IDs should be unique (e.g., "agent_0", "agent_1").
        *   Initializes the engine: `engine.initialize(environment=environment, agents=registered_agents_dict)`.
        *   Runs the simulation: `engine.run_simulation(num_steps=MAX_SIMULATION_STEPS)`.
        *   (Optional) Post-simulation analysis or data saving specific to the scenario.

## 4. Example Scenario Snippet (Conceptual)

```python
# In PiaAGI_Research_Tools/PiaSE/scenarios/my_custom_scenario.py

from PiaAGI_Research_Tools.PiaSE.core_engine.basic_engine import BasicSimulationEngine
from PiaAGI_Research_Tools.PiaSE.environments.grid_world import GridWorld # Example
from PiaAGI_Research_Tools.PiaSE.agents.q_learning_agent import QLearningAgent # Example
from PiaAGI_Research_Tools.PiaSE.core_engine.interfaces import Environment, AgentInterface
from typing import List, Dict, Optional

# --- Configuration ---
MAX_STEPS = 1000
GRID_WIDTH = 10
GRID_HEIGHT = 10

def setup_environment(config: Optional[Dict] = None) -> Environment:
    print("Setting up GridWorld environment...")
    # Dynamic config loading or default values
    width = config.get("grid_width", GRID_WIDTH) if config else GRID_WIDTH
    height = config.get("grid_height", GRID_HEIGHT) if config else GRID_HEIGHT
    
    env = GridWorld(width=width, height=height, goal_position=(width-1, height-1))
    # Further environment customization if needed
    # env.place_obstacle((2,2))
    return env

def setup_agents(env: Environment, config: Optional[Dict] = None) -> List[AgentInterface]:
    print("Setting up agents...")
    agents = []
    action_space = env.get_action_space() # For QLearningAgent initialization

    # Example: Single QLearningAgent
    q_agent = QLearningAgent(action_space=action_space, learning_rate=0.1, discount_factor=0.9)
    # Potentially load more complex configurations for the agent here
    agents.append(q_agent)
    return agents

def run_scenario(custom_config: Optional[Dict] = None):
    print(f"Starting scenario: My Custom Scenario with config: {custom_config}")
    
    engine = BasicSimulationEngine()
    
    environment = setup_environment(config=custom_config)
    agent_list = setup_agents(env=environment, config=custom_config)
    
    registered_agents = {}
    for i, agent_instance in enumerate(agent_list):
        agent_id = f"agent_{i}"
        # The engine will call agent.set_id(agent_id)
        registered_agents[agent_id] = agent_instance 
        # engine.register_agent(agent_id, agent_instance) # Old way, engine.initialize will handle it

    # Initialize the engine with environment and agents
    engine.initialize(environment=environment, agents=registered_agents, scenario_config=custom_config)
    
    # Run the simulation
    engine.run_simulation(num_steps=custom_config.get("max_steps", MAX_STEPS) if custom_config else MAX_STEPS)
    
    print("Scenario finished.")
    # Add any scenario-specific results saving or analysis here

if __name__ == "__main__":
    # Example of running with a custom configuration
    # config = {"grid_width": 5, "grid_height": 5, "max_steps": 500}
    # run_scenario(custom_config=config)
    run_scenario()

```

## 5. Scenario Loading and Execution by the Engine

*   The Core Simulation Engine itself will not directly "parse" these Python scenario files in the traditional sense.
*   Instead, a user or a higher-level script will execute the scenario Python file directly (e.g., `python my_custom_scenario.py`).
*   The scenario script itself orchestrates the setup and initiates the simulation run by calling the engine's methods.
*   The `BasicSimulationEngine.initialize()` method will receive the fully instantiated environment and agent objects from the scenario script.

## 6. Future Considerations

*   **Declarative Scenario Files (YAML/JSON):**
    *   Develop a schema for defining scenarios in YAML or JSON.
    *   Create a Python loader that parses these files and translates them into the Python calls needed to set up the environment and agents (effectively acting as a bridge to the Python-based setup functions). This would involve mapping string names to actual classes.
*   **Scenario Registry:** A system to discover and list available scenarios.
*   **GUI for Scenario Configuration:** A graphical interface to select scenarios and adjust their parameters before execution.
*   **Scenario Templates:** Pre-defined templates for common experimental setups.
*   **Integration with Developmental Curricula:** Mechanisms to link scenarios into sequences as part of a developmental curriculum defined in PiaPES, where the outcome of one scenario might influence the configuration of the next.
```
