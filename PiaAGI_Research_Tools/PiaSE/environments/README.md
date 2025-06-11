# PiaSE Environments

This directory holds implementations of various simulation environments for PiaSE.

-   `grid_world.py`: A concrete implementation of the `Environment` interface. It provides a 2D grid where agents can navigate, with support for walls and configurable agent starting positions.
    -   It now includes a configurable goal position, emits rewards based on agent actions (e.g., reaching the goal, hitting walls), and can signal task completion.
    -   It also implements `get_action_space` to inform agents of possible actions.

-   `social_dialogue_sandbox.py`: Implements the `Environment` interface for simulating turn-based social dialogues. It allows interaction between a PiaAGI agent and one or more rule-based simulated interactors (NPCs).
    -   Supports configurable NPC profiles including conceptual personality traits, emotional states, and goals.
    *   Provides perception data to the agent including the last utterance, speaker information, and conceptual NPC states.
    *   The agent can perform "speak" and "listen" actions.
    *   Designed to facilitate research into Theory of Mind, nuanced communication, and social reasoning.
    *   See the conceptual design in `PiaAGI_Research_Tools/PiaSE/docs/specifications/environments/social_dialogue_sandbox_design.md`.
    *   An example scenario can be found in `PiaAGI_Research_Tools/PiaSE/scenarios/basic_social_dialogue_scenario.py`.

Refer to the main [PiaSE README](../../README.md) for more context.
