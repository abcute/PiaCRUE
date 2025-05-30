# PiaSE Core Engine

This directory contains the core components of the PiaAGI Simulation Environment (PiaSE).

-   `interfaces.py`: Defines the abstract base classes (ABCs) crucial for the simulation framework, including `PiaSEEvent`, `SimulationEngine`, `Environment`, and `AgentInterface`.
    -   The `Environment` ABC now includes `get_action_space`.
    -   The `AgentInterface` ABC now includes `initialize_q_table`, `get_q_value`, and `update_q_value` to support learning paradigms like Q-learning.
-   `basic_engine.py`: Provides a minimal concrete implementation of the `SimulationEngine` interface, managing a simple turn-based simulation loop.
    -   The engine now supports learning agents by passing reward and next state information to the agent's `learn` method and handling a `done` flag from the environment.

Refer to the main [PiaSE README](../../README.md) for more context.
