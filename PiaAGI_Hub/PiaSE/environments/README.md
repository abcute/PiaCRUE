# PiaSE Environments

This directory holds implementations of various simulation environments for PiaSE.

-   `grid_world.py`: A concrete implementation of the `Environment` interface. It provides a 2D grid where agents can navigate, with support for walls and configurable agent starting positions.
    -   It now includes a configurable goal position, emits rewards based on agent actions (e.g., reaching the goal, hitting walls), and can signal task completion.
    -   It also implements `get_action_space` to inform agents of possible actions.

Refer to the main [PiaSE README](../../README.md) for more context.
