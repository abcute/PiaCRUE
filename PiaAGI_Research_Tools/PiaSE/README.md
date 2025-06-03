<!-- PiaAGI AGI Research Framework Document -->
# PiaAGI Simulation Environment (PiaSE)

This directory contains the PiaAGI Simulation Environment (PiaSE), a flexible and extensible platform for researchers and developers to instantiate, test, and evaluate PiaAGI agents and their components in controlled, dynamic, and reproducible settings. PiaSE now emphasizes standardized interfaces using Pydantic models for robust agent-environment communication and includes diverse environments like `GridWorld` and the new `TextBasedRoom`.

## Directory Structure

-   `core_engine/`: Contains the main simulation loop, time management, event system, and core abstract classes.
-   `environments/`: Implementations of various simulation environments (e.g., `GridWorld`, `TextBasedRoom`).
-   `agents/`: Agent interfaces and example agent implementations.
-   `scenarios/`: Scripts and configurations for defining and running specific experimental scenarios.
-   `docs/specifications/`: Detailed design documents for PiaSE components.
-   `utils/`: Common utility functions and data structures used across PiaSE.
-   `tests/`: Unit tests for PiaSE components.

Refer to the main PiaAGI documentation and [`../PiaAGI_Simulation_Environment.md`](../PiaAGI_Simulation_Environment.md) for more details on the conceptual design and overall goals of PiaSE.

## Key Implemented Components

PiaSE has evolved to include a more robust and standardized set of components:

-   **Core Interfaces:** Refined `Environment` and `AgentInterface` abstract base classes. Data exchange relies on Pydantic models: `PerceptionData`, `ActionCommand`, and `ActionResult`. `PiaSEEvent` is also a Pydantic model.
-   **Simulation Engine:** A refactored `BasicSimulationEngine` that manages the simulation lifecycle with an enhanced main loop, clearer agent registration (via initialization), and integrated logging capabilities.
-   **Environments:**
    *   `GridWorld`: A configurable grid-based environment, now compliant with new interfaces and supporting static/dynamic objects.
    *   `TextBasedRoom`: A new interactive fiction-style environment for parsing text commands and interacting with objects in a narrative setting.
-   **Agents:**
    *   `QLearningAgent`: An agent capable of learning in `GridWorld`, updated to use the new Pydantic-based interfaces and refined learning logic.
    *   `InteractiveTextAgent`: A simple agent that allows users to input text commands to interact with the `TextBasedRoom` environment.
    *   `CuriosityGridAgent`: A basic agent for `GridWorld` that demonstrates simple exploration and artifact discovery.
-   **Visualization & WebApp:**
    *   `GridWorldVisualizer`: (Existing) Uses Matplotlib to display `GridWorld` states.
    *   A simple WebApp interface (existing) to run scenarios and view results, primarily for `GridWorld`.

## Implemented Scenarios

PiaSE now includes several example scenarios to demonstrate its capabilities:

*   **`grid_world_scenario.py`**: The original Q-Learning agent in a basic GridWorld. (Path: `PiaAGI_Research_Tools/PiaSE/scenarios/grid_world_scenario.py`)
*   **`text_based_the_lost_key.py`**: An interactive text adventure in the `TextBasedRoom` environment where the user plays as the agent to find a lost key and a document. (Path: `PiaAGI_Research_Tools/PiaSE/scenarios/text_based_the_lost_key.py`)
*   **`grid_world_curiosity_scenario.py`**: A scenario demonstrating a simple `CuriosityGridAgent` that explores a `GridWorld` and identifies predefined "artifact" locations. (Path: `PiaAGI_Research_Tools/PiaSE/scenarios/grid_world_curiosity_scenario.py`)
*   **`grid_world_competence_scenario.py`**: A scenario featuring a `QLearningAgent` in a `GridWorld` that adapts to changing goals and obstacles, demonstrating competence acquisition and adaptation over multiple tasks. (Path: `PiaAGI_Research_Tools/PiaSE/scenarios/grid_world_competence_scenario.py`)

To run these scenarios, navigate to the `PiaAGI_Research_Tools/PiaSE/` directory (if you are at the project root) and execute the desired scenario script using Python:
```bash
# Example from the project root directory:
cd PiaAGI_Research_Tools/PiaSE

# Example for the text-based scenario
python scenarios/text_based_the_lost_key.py

# Example for the competence scenario
python scenarios/grid_world_competence_scenario.py
```

## PiaSE WebApp
PiaSE includes a simple web application to help visualize and interact with simulations.

### Purpose
The WebApp allows users to run a predefined PiaSE scenario (currently a Q-Learning agent in GridWorld) and view its step-by-step visual progress and textual logs directly in a web browser. This enhances the usability and understandability of the PiaSE framework.

### Location
The WebApp code is located in the `PiaAGI_Research_Tools/PiaSE/WebApp/` directory.

### PiaSE WebApp Deployment Guide

To run the PiaSE WebApp, follow these steps:

1.  **Navigate to the PiaSE Root Directory:**
    Open your terminal. If you are at the root of the `PiaAGI_Research_Tools` project, navigate to PiaSE:
    ```bash
    cd PiaAGI_Research_Tools/PiaSE
    ```

2.  **Install Dependencies:**
    Ensure all necessary Python packages are installed by running:
    ```bash
    pip install -r requirements.txt 
    ```
    This file includes Flask, Matplotlib, NumPy, Pydantic, and other potential dependencies for PiaSE.

3.  **Navigate to the WebApp Directory:**
    From the `PiaAGI_Research_Tools/PiaSE/` directory:
    ```bash
    cd WebApp
    ```

4.  **Run the Flask Application:**
    You can run the development server in one of two main ways:

    *   **Method 1: Directly executing `app.py`**:
        ```bash
        python app.py
        ```
    *   **Method 2: Using the `flask` command**:
        First, set the `FLASK_APP` environment variable:
        ```bash
        # On Linux/macOS:
        export FLASK_APP=app.py
        # On Windows (Command Prompt):
        # set FLASK_APP=app.py
        # On Windows (PowerShell):
        # $env:FLASK_APP="app.py"
        ```
        Then, run the Flask development server:
        ```bash
        flask run --host=0.0.0.0 --port=5001
        ```
        The `--host=0.0.0.0` flag makes the server accessible from other devices on your network. The port is set to `5001` in `app.py`.

5.  **Access in Browser:**
    Open your web browser and go to `http://120.0.0.1:5001/` (or `http://localhost:5001/`).

You should see the main page of the PiaSE WebApp.

For more details about the WebApp's internal structure, see the [WebApp README](./WebApp/README.md).

## Dependencies
Key dependencies for PiaSE, including the WebApp and visualizer, are listed in `requirements.txt` (located in the current `PiaAGI_Research_Tools/PiaSE/` directory).
To install them, ensure you are in the `PiaAGI_Research_Tools/PiaSE/` directory and run:
```bash
pip install -r ./requirements.txt 
```
It is highly recommended to use a Python virtual environment. Key dependencies include:
- NumPy
- Pydantic (for data structures)
- Matplotlib (for visualization)
- Flask (for the WebApp)

## Future Development & Enhancements

PiaSE is envisioned to grow into a powerful platform for AGI research. Key future directions include:

1.  **Full PiaAGI Agent Integration:**
    *   Developing clear examples, helper classes, or integration layers within PiaSE to demonstrate how to instantiate, configure (potentially using PiaPES outputs), and run a complete PiaAGI agent composed of multiple interacting PiaCML modules.

2.  **Diverse and Dynamic Environments:**
    *   Moving beyond `GridWorld` to implement or integrate more complex environments.
    *   **Social Simulation Environments:** For testing ToM, communication, and emotional modeling (e.g., simulated dialogues, collaborative tasks).
    *   **Problem-Solving Worlds:** Environments that require multi-step planning, tool use, and creative problem-solving.
    *   **Multi-Modal Environments:** Conceptual support for environments that could provide visual or other forms of non-textual input to agents.
    *   Developing a more robust **Environment API** to support these richer interactions.

3.  **Advanced Developmental Scaffolding Engine:**
    *   Enhancing the scenario manager in PiaSE to become a **Dynamic Scenario Engine**. This engine would:
        *   Interface with PiaPES to load and interpret `DevelopmentalCurricula`.
        *   Adapt environmental parameters, task complexity, available information, or even simulated tutor behavior based on the agent's performance (metrics from PiaAVT) and its current position in a curriculum.
        *   Manage the state of an agent's progression through long-term developmental pathways.
    *   *(See current progress below under "Dynamic Scenario Engine (DSE) for Developmental Scaffolding")*

4.  **Human-in-the-Loop (HITL) Interaction:**
    *   Designing and implementing interfaces that allow human users to:
        *   Act as tutors or mentors, providing real-time feedback, demonstrations, or guidance to the agent within PiaSE.
        *   Participate as other agents or entities in simulated social scenarios.
        *   Manually trigger environmental events or override agent actions for experimental purposes.

5.  **Standardized Logging for PiaAVT:**
    *   Ensuring PiaSE emits comprehensive logs that adhere to the `PiaAVT/Logging_Specification.md`, covering agent-environment interactions, task outcomes, and any data necessary for advanced analyses in PiaAVT (e.g., data to evaluate goal achievement, learning progress, or ethical decision-making).

6.  **Multi-Agent Support:**
    *   Formalizing support for running multiple independent or interacting PiaAGI agents within the same environment, including defining inter-agent communication channels and observation capabilities.

### Dynamic Scenario Engine (DSE) for Developmental Scaffolding

PiaSE now includes an MVP (Minimum Viable Product) of a Dynamic Scenario Engine (DSE).

**Purpose:** The DSE is designed to run agents through predefined curricula, which are sequences of tasks or learning experiences. It allows for the dynamic adaptation of scenarios based on (currently simulated/mocked) agent performance metrics and attempt counts, facilitating developmental scaffolding.

**Key Components:**
*   **`CurriculumManager`**: Located in `PiaAGI_Research_Tools/PiaSE/core_engine/dynamic_scenario_engine.py`, this component is responsible for loading curriculum JSON files (defining steps, completion criteria, adaptation rules, and configurations) and tracking an agent's progress through them.
*   **`AdaptationDecisionModule`**: Also in `dynamic_scenario_engine.py`, this module evaluates an agent's performance against a curriculum step's `completion_criteria` and `adaptation_rules` to decide if the agent should proceed, repeat the step, branch to another step, or if a hint should be applied. It uses a `PiaAVTInterface` (currently mocked as `MockPiaAVTInterface`) to get performance data.

**Engine Integration:**
The `BasicSimulationEngine` (in `PiaAGI_Research_Tools/PiaSE/core_engine/basic_engine.py`) has been integrated with these DSE components. When initializing the engine, a mapping of agent IDs to curriculum filepaths can be provided. The engine's `run_simulation` loop then manages the DSE lifecycle for these agents, including:
*   Loading and starting curricula.
*   Executing curriculum steps (which may involve multiple agent-environment interactions, controlled by `max_interactions` in the curriculum step).
*   Invoking the `AdaptationDecisionModule` to evaluate progress and make decisions.
*   Updating agent progress in the `CurriculumManager`.
*   (Conceptually) Reconfiguring the agent and environment based on the current curriculum step's `agent_config_overrides` and `environment_config_overrides`.

**Example:**
A practical example demonstrating the DSE can be found in `PiaAGI_Research_Tools/PiaSE/scenarios/dynamic_scaffolding_scenario.py`. This scenario uses a `RuleBasedGridAgent` in `GridWorld` and a sample curriculum defined in `PiaAGI_Research_Tools/PiaSE/scenarios/curricula/simple_grid_curriculum.json`. The scenario script also shows how to manually update the `MockPiaAVTInterface` to simulate performance data that drives DSE decisions.

For more detailed information on the DSE's design, refer to the [Full DSE Design document](./docs/specifications/Dynamic_Scenario_Engine.md).

PiaSE aims to be a critical testbed for empirically validating the PiaAGI framework and fostering the development of increasingly sophisticated and autonomous agents.
---
Return to [PiaAGI Core Document](../../PiaAGI.md) | [Project README](../../README.md)
```
