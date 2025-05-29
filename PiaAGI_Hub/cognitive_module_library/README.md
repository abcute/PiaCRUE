# PiaAGI Cognitive Module Library (CML)

## Purpose

The Cognitive Module Library (CML) is a core component of the PiaAGI project. Its primary purpose is to define abstract interfaces and, eventually, provide foundational Python implementations for the various cognitive modules outlined in the [PiaAGI Cognitive Architecture](../../PiaAGI.md#4-the-piaagi-cognitive-architecture).

This library aims to:
1.  **Standardize Interfaces:** Provide common Python Abstract Base Classes (ABCs) for each cognitive module, ensuring that different implementations of a module can be used interchangeably within the broader PiaAGI framework.
2.  **Facilitate Modular Development:** Allow researchers and developers to focus on specific cognitive functions by working on individual modules.
3.  **Support Simulation and Experimentation:** Enable the construction of PiaAGI agent simulations by composing these modules, as demonstrated conceptually in `PiaAGI_Hub/conceptual_simulations/PiaAGI_Behavior_Example.py`.
4.  **Promote Code Reusability:** Offer well-documented and tested base components that can be extended or used directly in more complex AGI implementations.
5.  **Align with Theory:** Ensure that module designs and interfaces are closely mapped to the theoretical descriptions in the main `PiaAGI.md` document.

## Current Modules (Abstract Interfaces)

This initial version of the CML provides abstract base classes for the following modules:

1.  **`base_memory_module.py` (`BaseMemoryModule`)**:
    *   **Purpose:** Defines the fundamental interface common to all memory systems within PiaAGI. It outlines core operations like storing information, retrieving it based on queries, managing memory capacity, and handling forgetting.
    *   **PiaAGI.md Sections:** 3.1.1 (Memory Systems), 4.1.2 (Working Memory Module), 4.1.3 (Long-Term Memory Module).

2.  **`long_term_memory_module.py` (`LongTermMemoryModule`)**:
    *   **Purpose:** Extends `BaseMemoryModule` to define the interface for Long-Term Memory. LTM is the AGI's vast repository for semantic knowledge, episodic experiences, and procedural skills. This interface includes methods specific to these LTM sub-components.
    *   **PiaAGI.md Sections:** 3.1.1 (LTM details), 4.1.3 (Long-Term Memory Module).

3.  **`working_memory_module.py` (`WorkingMemoryModule`)**:
    *   **Purpose:** Extends `BaseMemoryModule` to define the interface for Working Memory. WM is a limited-capacity system for temporarily holding and actively processing information relevant to current tasks. It also conceptually includes functions of the Central Executive (attention, coordination).
    *   **PiaAGI.md Sections:** 3.1.1 (WM details), 3.1.2 (Attention and Cognitive Control/Central Executive), 4.1.2 (Working Memory Module).

4.  **`perception_module.py` (`PerceptionModule`)**:
    *   **Purpose:** Responsible for receiving raw sensory input (e.g., text, vision, audio), processing it, extracting features, and generating a structured perceptual representation for other modules. Crucial for grounding internal representations in external reality.
    *   **PiaAGI.md Sections:** 4.1.1 (Perception Module), 4.3 (Perception and World Modeling).

5.  **`motivational_system_module.py` (`MotivationalSystemModule`)**:
    *   **Purpose:** Manages the AGI's goals, drives, and overall motivation. It selects and prioritizes goals, influencing decision-making and behavior based on intrinsic and extrinsic factors.
    *   **PiaAGI.md Sections:** 3.3 (Motivational Systems and Intrinsic Goals), 4.1.6 (Motivational System Module).

6.  **`emotion_module.py` (`EmotionModule`)**:
    *   **Purpose:** Generates, processes, and modulates emotional states. Emotions influence perception, cognition, decision-making, and social interaction, enabling more nuanced and adaptive behavior.
    *   **PiaAGI.md Sections:** 3.4 (Computational Models of Emotion), 4.1.7 (Emotion Module).

7.  **`planning_decision_making_module.py` (`PlanningAndDecisionMakingModule`)**:
    *   **Purpose:** Handles higher-level cognitive functions like evaluating courses of action, forming plans to achieve goals, and making choices among alternatives. Integrates information from the World Model, Motivational System, Perception, and Emotion Modules.
    *   **PiaAGI.md Sections:** 4.1.8 (Planning and Decision-Making Module), 4.4 (Action Selection and Execution).

8.  **`self_model_module.py` (`SelfModelModule`)**:
    *   **Purpose:** Maintains a dynamic representation of the AGI itself, including its capabilities, limitations, internal states, interaction history, performance, and ethical framework. Crucial for metacognition, self-awareness, and self-improvement.
    *   **PiaAGI.md Sections:** 4.1.10 (Self-Model Module).
4.  **[`PerceptionModule`](perception_module.py)**:
    *   **Purpose:** Handles the processing of raw sensory input from various modalities, transforming it into a format usable by other cognitive modules.
    *   **PiaAGI.md Sections:** 3.1.3 (Sensory Processing), 4.1.1 (Perception Module).

5.  **[`MotivationalSystemModule`](motivational_system_module.py)**:
    *   **Purpose:** Manages the agent's internal drives, needs, and goals. It is responsible for generating motivation and influencing goal selection.
    *   **PiaAGI.md Sections:** 3.2.1 (Drives, Needs, and Goals), 4.2.1 (Motivational System).

6.  **[`EmotionModule`](emotion_module.py)**:
    *   **Purpose:** Models and processes emotions, which play a crucial role in evaluating situations, influencing decision-making, and modulating behavior and cognitive processes.
    *   **PiaAGI.md Sections:** 3.2.2 (Emotional Processing), 4.2.2 (Emotion Module).

7.  **[`PlanningAndDecisionMakingModule`](planning_and_decision_making_module.py)**:
    *   **Purpose:** Responsible for generating possible actions, evaluating them, selecting an optimal action or sequence of actions (plan) to achieve current goals.
    *   **PiaAGI.md Sections:** 3.1.5 (Decision Making and Action Selection), 3.1.6 (Planning and Problem Solving), 4.1.5 (Planning and Decision-Making Module).

8.  **[`SelfModelModule`](self_model_module.py)**:
    *   **Purpose:** Maintains and updates the agent's internal representation of itself, including its own states, capabilities, beliefs, and history. This contributes to self-awareness and metacognitive abilities.
    *   **PiaAGI.md Sections:** 3.2.4 (Self-Reflection and Metacognition), 4.2.4 (Self-Model Module).

## Core Module Interfaces

(This section title can be considered if a more distinct separation from memory modules is desired in the future, but for now, the above list under "Current Modules" should suffice and maintain consistency.)

## Future Development

The CML will be expanded to include interfaces and foundational implementations for other core PiaAGI cognitive modules, such as:
*   Attention Module (potentially integrated more deeply with Perception and Working Memory)
*   Learning Module(s) (various types, e.g., reinforcement, supervised, unsupervised)
*   Attention Module
*   Learning Module(s)
*   Behavior Generation Module
*   Theory of Mind (ToM) / Social Cognition Module
*   Communication Module (for language processing and generation)
*   World Model (though this might be more of a data structure and service used by many modules)

Contributions and collaborations are welcome as this library evolves.
```
