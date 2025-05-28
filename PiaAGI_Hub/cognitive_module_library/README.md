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

This initial version of the CML provides abstract base classes for the following memory-related modules:

1.  **`base_memory_module.py` (`BaseMemoryModule`)**:
    *   **Purpose:** Defines the fundamental interface common to all memory systems within PiaAGI. It outlines core operations like storing information, retrieving it based on queries, managing memory capacity, and handling forgetting.
    *   **PiaAGI.md Sections:** 3.1.1 (Memory Systems), 4.1.2 (Working Memory Module), 4.1.3 (Long-Term Memory Module).

2.  **`long_term_memory_module.py` (`LongTermMemoryModule`)**:
    *   **Purpose:** Extends `BaseMemoryModule` to define the interface for Long-Term Memory. LTM is the AGI's vast repository for semantic knowledge, episodic experiences, and procedural skills. This interface includes methods specific to these LTM sub-components.
    *   **PiaAGI.md Sections:** 3.1.1 (LTM details), 4.1.3 (Long-Term Memory Module).

3.  **`working_memory_module.py` (`WorkingMemoryModule`)**:
    *   **Purpose:** Extends `BaseMemoryModule` to define the interface for Working Memory. WM is a limited-capacity system for temporarily holding and actively processing information relevant to current tasks. It also conceptually includes functions of the Central Executive (attention, coordination).
    *   **PiaAGI.md Sections:** 3.1.1 (WM details), 3.1.2 (Attention and Cognitive Control/Central Executive), 4.1.2 (Working Memory Module).

## Future Development

The CML will be expanded to include interfaces and foundational implementations for other core PiaAGI cognitive modules, such as:
*   Perception Module
*   Attention Module
*   Learning Module(s)
*   Motivational System Module
*   Emotion Module
*   Planning and Decision-Making Module
*   Behavior Generation Module
*   Self-Model Module
*   Theory of Mind (ToM) / Social Cognition Module
*   Communication Module

Contributions and collaborations are welcome as this library evolves.
```
