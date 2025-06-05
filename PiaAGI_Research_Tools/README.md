<!-- PiaAGI AGI Research Framework Document -->
# PiaAGI Research Tools Suite

This directory contains conceptual design documents and initial implementations for a suite of Python-based research tools. These tools are intended to support the development, experimentation, analysis, and iterative refinement of agents and cognitive architectures within the **PiaAGI framework**, ultimately aiming towards Artificial General Intelligence.

The suite is designed to be modular yet interconnected, allowing researchers to leverage individual tools or use them in concert to achieve complex AGI development and analysis workflows.

## Core Conceptualized Tools

1.  **[PiaAGI Simulation Environment (PiaSE)](PiaAGI_Simulation_Environment.md)**
    *   **Description:** A flexible and extensible platform for instantiating, testing, and evaluating PiaAGI agents and their components in controlled, dynamic, and reproducible settings. It supports the creation of diverse environments, scenario management, developmental scaffolding, and multi-agent simulations.
    *   **Current Status:** Includes conceptual designs for its core simulation loop, agent-environment API (using Pydantic models for `PerceptionData`, `ActionCommand`, `ActionResult`), and scenario definitions. MVP implementation includes a `BasicSimulationEngine` with Dynamic Scenario Engine (DSE) components for curriculum-based learning, `GridWorld` and `TextBasedRoom` environments, example agents (like `QLearningAgent`, `PiaAGIAgent`), and a basic Flask WebApp for GridWorld visualization and scenario execution.
    *   **Future Directions:** Development of more diverse and dynamic environments (e.g., social dialogue, complex problem-solving), enhanced support for full PiaAGI agent instantiation, a more dynamic scenario engine for adaptive developmental scaffolding, and interfaces for human-in-the-loop interaction.

2.  **[PiaAGI Cognitive Module Library (PiaCML)](PiaAGI_Cognitive_Module_Library.md)**
    *   **Description:** A suite of well-defined, reusable, and extensible Python libraries and software components for constructing and experimenting with the core cognitive modules outlined in the PiaAGI cognitive architecture (e.g., memory systems, learning systems, motivational engine, emotion simulator, perception, planning, self-model, ToM, communication).
    *   **Current Status:** Defines Python abstract base classes (ABCs) and interfaces for over 12 core cognitive modules. Foundational concrete MVP classes exist for most, with key modules like `ConcreteSelfModelModule`, `ConcreteWorldModel`, and `ConcreteMotivationalSystemModule` enhanced with detailed internal data structures (Python dataclasses) based on comprehensive specification documents (e.g., `Self_Model_Module_Specification.md`, `Motivational_System_Specification.md`). An inter-module `MessageBus` and `CoreMessages` are implemented. An `Advanced_Roadmap.md` details future plans, including 'Architectural Maturation Hooks'.
    *   **Future Directions:** Phased implementation of more psychologically rich and computationally sophisticated versions of modules (especially Self-Model, LTM, Motivation, Emotion, ToM). Standardization of inter-module communication protocols. Exploration of mechanisms to support conceptual "architectural maturation."

3.  **[PiaAGI Agent Analysis & Visualization Toolkit (PiaAVT)](PiaAGI_Agent_Analysis_Visualization_Toolkit.md)**
    *   **Description:** A comprehensive toolkit to log, analyze, understand, and visualize the behavior, internal cognitive states, learning trajectories, and developmental progress of PiaAGI agents. It aims to provide deep insights into agent functioning and support explainable AI.
    *   **Current Status:** Features a detailed `Logging_Specification.md` (including meta-cognitive events) and a `prototype_logger.py` for generating JSONL logs. Initial Python implementations exist for basic analyses (Goal Dynamics, Emotional State Trajectory, Task Performance, Intrinsic Motivation), which are integrated into a `PiaAVTAPI` and a Streamlit WebApp. Note: The API and WebApp's current log ingestion (`core/logging_system.py`) expects a file containing a single JSON list of log objects, not yet direct JSONL line-by-line parsing; this is planned for enhancement.
    *   **Future Directions:** Development of advanced analytical modules (causal analysis, behavioral pattern mining, ethical reasoning traceability), richer cognitive visualizations (LTM graphs, Self-Model dashboards), and specific analyses/logging to track meta-cognitive development and the AGI's potential internalization of tool principles.

4.  **[PiaAGI Prompt Engineering Suite (PiaPES)](PiaAGI_Prompt_Engineering_Suite.md)**
    *   **Description:** A toolkit to assist researchers in the systematic design, construction, management, versioning, and evaluation of complex "Guiding Prompts" and "Developmental Scaffolding" curricula used to configure and guide PiaAGI agents.
    *   **Current Status:** Includes the `prompt_engine_mvp.py` for programmatic creation, JSON serialization (with type preservation for custom objects), and Markdown rendering of structured Guiding Prompts and Developmental Curricula (using `DevelopmentalCurriculum` and `CurriculumStep` classes). A basic Flask web interface for CRUD operations and management of these prompt and curriculum files is also part of its MVP.
    *   **Future Directions:** Further development of the Developmental Curriculum Designer (for complex dependencies, adaptation logic), operationalizing the PiaPES-PiaSE-PiaAVT integration for prompt/curriculum evaluation, and deeper conceptualization of the Cognitive Configuration GUI.

## Foundational Components and Implementations

*   **PiaPES MVP:** An initial MVP for the Prompt Templating Engine can be found in `PiaPES/prompt_engine_mvp.py` ([Usage Guide](PiaPES/USAGE.md)) and its associated web application, supporting structured prompt and curriculum design with JSON/Markdown support.
*   **PiaCML Interfaces & Concrete MVPs:** Initial Python interfaces and basic concrete implementations for core cognitive modules are defined in the `PiaCML/` directory ([PiaCML README](PiaCML/README.md)), with some MVPs using detailed dataclass-based internal state.
*   **PiaSE MVP:** Basic `GridWorld` and `TextBasedRoom` simulation environments, example agents, a WebApp visualizer, and a Dynamic Scenario Engine (DSE) for curricula are available in `PiaSE/`.
*   **PiaAVT MVP:** Core logging tools, implemented basic analyses, a CLI, and a Streamlit WebApp with integrated basic analyses are available in `PiaAVT/`. (Note: current API log loading expects JSON list, not direct JSONL).
*   **Unified WebApp:** A central Flask+React web application located in `WebApp/` provides an integrated interface for interacting with the MVPs of PiaCML (conceptual interaction), PiaPES (prompt/curriculum management), PiaSE (simulation run and result viewing), and basic PiaAVT (log upload and simple analysis via its API).

These tools are envisioned to work synergistically, providing a comprehensive ecosystem for advancing research and development within the PiaAGI framework towards its ambitious goal of creating human-like Artificial General Intelligence. Each linked document provides a more detailed conceptual design and current status for the respective tool.

---
Return to [PiaAGI Core Document](../PiaAGI.md) | [Project README](../README.md)
```
