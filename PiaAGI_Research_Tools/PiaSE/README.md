<!-- PiaAGI AGI Research Framework Document -->
# PiaAGI Simulation Environment (PiaSE)

This directory contains the PiaAGI Simulation Environment (PiaSE), a flexible and extensible platform for researchers and developers to instantiate, test, and evaluate PiaAGI agents and their components in controlled, dynamic, and reproducible settings.

Refer to the main conceptual design document at [`PiaAGI_Simulation_Environment.md`](../PiaAGI_Simulation_Environment.md) for the overarching purpose, goals, and detailed conceptual features of PiaSE, including the core simulation loop, agent-environment API, and example environment designs like "TextBasedRoom."

## Current Status & Implemented Components

PiaSE has foundational elements and some MVP (Minimal Viable Product) implementations:
-   **Core Interfaces:** Defined for `PiaSEEvent`, `SimulationEngine`, `Environment`, `AgentInterface`.
-   **Simulation Engine:** A `BasicSimulationEngine` is implemented.
-   **Environments:**
    *   A `GridWorld` environment is implemented, supporting rewards and goal-oriented tasks.
    *   Conceptual design for a "TextBasedRoom" exists, suitable for more complex textual interactions.
-   **Agents:**
    *   A `BasicGridAgent`.
    *   A `QLearningAgent` capable of learning in the `GridWorld`.
-   **Visualization & Interaction:**
    *   A `GridWorldVisualizer` using Matplotlib.
    *   An example `grid_world_scenario.py` that saves visualization frames.
    *   A simple **WebApp interface** (`PiaAGI_Research_Tools/PiaSE/WebApp/`) to run scenarios (currently Q-Learning in GridWorld) and view visual progress and logs.
-   **Testing:** Unit tests for `GridWorld`, `BasicGridAgent`, `QLearningAgent`, and `GridWorldVisualizer`.
-   **Dependencies:** Listed in `requirements.txt` in the PiaSE root.

## PiaSE WebApp Deployment Guide

To run the PiaSE WebApp for visualizing GridWorld scenarios:

1.  **Navigate to the PiaSE Root Directory:** `cd path/to/your/PiaAGI_Research_Tools/PiaSE`
2.  **Install Dependencies:** `pip install -r requirements.txt` (preferably in a virtual environment).
3.  **Navigate to the WebApp Directory:** `cd WebApp`
4.  **Run the Flask Application:** `python app.py` or `flask run --host=0.0.0.0 --port=5001` (after setting `FLASK_APP=app.py`).
5.  **Access in Browser:** `http://127.0.0.1:5001/`.

For more details, see the [WebApp README](./WebApp/README.md).

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

4.  **Human-in-the-Loop (HITL) Interaction:**
    *   Designing and implementing interfaces that allow human users to:
        *   Act as tutors or mentors, providing real-time feedback, demonstrations, or guidance to the agent within PiaSE.
        *   Participate as other agents or entities in simulated social scenarios.
        *   Manually trigger environmental events or override agent actions for experimental purposes.

5.  **Standardized Logging for PiaAVT:**
    *   Ensuring PiaSE emits comprehensive logs that adhere to the `PiaAVT/Logging_Specification.md`, covering agent-environment interactions, task outcomes, and any data necessary for advanced analyses in PiaAVT (e.g., data to evaluate goal achievement, learning progress, or ethical decision-making).

6.  **Multi-Agent Support:**
    *   Formalizing support for running multiple independent or interacting PiaAGI agents within the same environment, including defining inter-agent communication channels and observation capabilities.

PiaSE aims to be a critical testbed for empirically validating the PiaAGI framework and fostering the development of increasingly sophisticated and autonomous agents.

---
Return to [PiaAGI Core Document](../../PiaAGI.md) | [Project README](../../README.md)
```
