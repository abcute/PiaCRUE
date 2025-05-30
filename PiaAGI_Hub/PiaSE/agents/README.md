# PiaSE Agents

This directory contains agent interfaces and example agent implementations for PiaSE.

-   `basic_grid_agent.py`: A concrete implementation of the `AgentInterface`. It can be configured with a "random" action policy or a simple "goal_oriented" policy for navigation in `GridWorld`.
-   `q_learning_agent.py`: Implements a `QLearningAgent` that uses Q-learning to learn optimal policies in environments that provide rewards. It manages a Q-table and uses an epsilon-greedy strategy for action selection.

Refer to the main [PiaSE README](../../README.md) for more context.
