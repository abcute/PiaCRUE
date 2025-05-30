# PiaAGI Simulation Environment (PiaSE)

This directory contains the PiaAGI Simulation Environment (PiaSE), a flexible and extensible platform for researchers and developers to instantiate, test, and evaluate PiaAGI agents and their components in controlled, dynamic, and reproducible settings.

## Directory Structure

-   `core_engine/`: Contains the main simulation loop, time management, event system, and core abstract classes.
-   `environments/`: Implementations of various simulation environments (e.g., GridWorld, physics-based).
-   `agents/`: Agent interfaces and example agent implementations.
-   `scenarios/`: Scripts and configurations for defining and running specific experimental scenarios.
-   `utils/`: Common utility functions and data structures used across PiaSE.
-   `tests/`: Unit tests for PiaSE components.

Refer to the main PiaAGI documentation and [`PiaAGI_Hub/PiaAGI_Simulation_Environment.md`](../PiaAGI_Simulation_Environment.md) for more details on the conceptual design and overall goals of PiaSE.

The components implemented in this initial phase include:
- Core interfaces (`PiaSEEvent`, `SimulationEngine`, `Environment`, `AgentInterface`)
- Updates to core interfaces to support learning agents.
- A `BasicSimulationEngine`
- A `GridWorld` environment
- Modifications to `GridWorld` to support rewards and goal-oriented tasks.
- A `BasicGridAgent`
- A `QLearningAgent` capable of learning in GridWorld.
- An example `grid_world_scenario.py`
- Unit tests for `GridWorld` and `BasicGridAgent`.
- Unit tests for `QLearningAgent`.
