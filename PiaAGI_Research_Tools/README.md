<!-- PiaAGI AGI Research Framework Document -->
# PiaAGI Research Tools Suite

This directory contains conceptual design documents and initial implementations for a suite of Python-based research tools. These tools are intended to support the development, experimentation, analysis, and iterative refinement of agents and cognitive architectures within the **PiaAGI framework**, ultimately aiming towards Artificial General Intelligence.

The suite is designed to be modular yet interconnected, allowing researchers to leverage individual tools or use them in concert to achieve complex AGI development and analysis workflows.

## Core Conceptualized Tools

1.  **[PiaAGI Simulation Environment (PiaSE)](PiaAGI_Simulation_Environment.md)**
    *   **Description:** A flexible and extensible platform for instantiating, testing, and evaluating PiaAGI agents and their components in controlled, dynamic, and reproducible settings. It supports the creation of diverse environments, scenario management, developmental scaffolding, and multi-agent simulations.
    *   **Current Status:** Includes conceptual designs for its core simulation loop, agent-environment API (using Pydantic models), and scenario definitions. MVP implementation includes a `BasicSimulationEngine`, `GridWorld` and `TextBasedRoom` environments, example agents (`QLearningAgent`, `InteractiveTextAgent`, `CuriosityGridAgent`), and a basic Flask WebApp for GridWorld visualization and scenario execution.
    *   **Future Directions:** Development of more diverse and dynamic environments (e.g., social dialogue, complex problem-solving), enhanced support for full PiaAGI agent instantiation, a more dynamic scenario engine for adaptive developmental scaffolding, and interfaces for human-in-the-loop interaction.

2.  **[PiaAGI Cognitive Module Library (PiaCML)](PiaAGI_Cognitive_Module_Library.md)**
    *   **Description:** A suite of well-defined, reusable, and extensible Python libraries and software components for constructing and experimenting with the core cognitive modules outlined in the PiaAGI cognitive architecture (e.g., memory systems, learning systems, motivational engine, emotion simulator, perception, planning, self-model, ToM, communication).
    *   **Current Status:** Defines Python abstract base classes (ABCs) and interfaces for over 12 core cognitive modules. Foundational concrete MVP classes exist for most of these, providing a basic layer for agent construction (e.g., `ConcreteSelfModelModule`, `ConcreteLongTermMemoryModule`, `ConcreteMotivationalSystemModule`).
    *   **Future Directions:** Phased implementation of more psychologically rich and computationally sophisticated versions of modules (especially Self-Model, LTM, Motivation, Emotion, ToM). Standardization of inter-module communication protocols. Exploration of mechanisms to support conceptual "architectural maturation."

3.  **[PiaAGI Agent Analysis & Visualization Toolkit (PiaAVT)](PiaAGI_Agent_Analysis_Visualization_Toolkit.md)**
    *   **Description:** A comprehensive toolkit to log, analyze, understand, and visualize the behavior, internal cognitive states, learning trajectories, and developmental progress of PiaAGI agents. It aims to provide deep insights into agent functioning and support explainable AI.
    *   **Current Status:** Features a detailed `Logging_Specification.md`, a prototype Python logger, conceptual and Python implementations for basic analyses (Goal Dynamics, Emotional State Trajectory, Intrinsic Motivation), time-series plotting, a basic API, a CLI, and a Streamlit WebApp for interactive log analysis.
    *   **Future Directions:** Development of advanced analytical modules (causal analysis, behavioral pattern mining, ethical reasoning traceability), richer cognitive visualizations (LTM graphs, Self-Model dashboards), and specific analyses/logging to track meta-cognitive development and the AGI's potential internalization of tool principles.

4.  **[PiaAGI Prompt Engineering Suite (PiaPES)](PiaAGI_Prompt_Engineering_Suite.md)**
    *   **Description:** A toolkit to assist researchers in the systematic design, construction, management, versioning, and evaluation of complex "Guiding Prompts" and "Developmental Scaffolding" curricula used to configure and guide PiaAGI agents.
    *   **Current Status:** Includes the `prompt_engine_mvp.py` for programmatic creation, JSON serialization, and Markdown rendering of structured Guiding Prompts and Developmental Curricula. A basic Flask web interface for managing these prompts and curricula is also part of its MVP. Extensive conceptual designs for advanced editor features, curriculum design, and evaluation modules are also detailed.
    *   **Future Directions:** Further development of the Developmental Curriculum Designer (for complex dependencies, adaptation logic), operationalizing the PiaPES-PiaSE-PiaAVT integration for prompt/curriculum evaluation, and deeper conceptualization of the Cognitive Configuration GUI.

## Foundational Components and Implementations

*   **PiaPES MVP:** An initial MVP for the Prompt Templating Engine can be found in `PiaPES/prompt_engine_mvp.py` ([Usage Guide](PiaPES/USAGE.md)) and its associated web application.
*   **PiaCML Interfaces & Concrete MVPs:** Initial Python interfaces and basic concrete implementations for core cognitive modules are defined in the `PiaCML/` directory ([PiaCML README](PiaCML/README.md)).
*   **PiaSE MVP:** Basic `GridWorld` and `TextBasedRoom` simulation environments, example agents, and a WebApp visualizer are available in `PiaSE/`.
*   **PiaAVT MVP:** Core logging tools, implemented basic analyses, a CLI, and a Streamlit WebApp are available in `PiaAVT/`.
*   **Unified WebApp:** A central Flask+React web application located in `WebApp/` provides an integrated interface for interacting with the MVPs of PiaCML, PiaPES, PiaSE, and basic PiaAVT functionalities.

These tools are envisioned to work synergistically, providing a comprehensive ecosystem for advancing research and development within the PiaAGI framework towards its ambitious goal of creating human-like Artificial General Intelligence. Each linked document provides a more detailed conceptual design and current status for the respective tool.

---
Return to [PiaAGI Core Document](../PiaAGI.md) | [Project README](../README.md)
```
