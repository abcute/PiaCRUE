<!-- PiaAGI AGI Research Framework Document -->
# PiaAGI Agent Analysis & Visualization Toolkit (PiaAVT)

This directory contains the PiaAGI Agent Analysis & Visualization Toolkit (PiaAVT), a Python-based toolkit designed to assist in understanding and evaluating PiaAGI agents by logging, analyzing, and visualizing their behavior, internal states, and developmental trajectories.

Refer to the main conceptual design document at [`PiaAGI_Agent_Analysis_Visualization_Toolkit.md`](../PiaAGI_Agent_Analysis_Visualization_Toolkit.md) for the overarching purpose, goals, and detailed conceptual features of PiaAVT.

## Logging Specification

PiaAVT processes logs adhering to a defined standard, crucial for interoperability with PiaCML modules and PiaSE.
Details: **[PiaAGI Logging Specification for PiaAVT](Logging_Specification.md)**.

## Current Features (Initial Build)

*   **Logging System (`core/logging_system.py`):** Ingestion, validation, storage of JSON logs. (Note: `prototype_logger.py` serves as the current reference implementation for generating logs for PiaAVT).
*   **Analyzers (`Analysis_Implementations/`):**
    *   `basic_analyzer.py`: Filtering, descriptive statistics, time-series extraction. (Core logic for basic stats, integrated into the API).
    *   `event_sequencer.py`: Extracts defined event sequences. (Core logic for sequence finding, integrated into the API).
    *   **Integrated Analyses**: The following analyses have their core logic in `Analysis_Implementations/` and are now primarily accessed via the `PiaAVTAPI` and the WebApp:
        *   Goal Dynamics (Lifecycle) Analysis
        *   Emotional State Trajectory Analysis
        *   Basic Task Performance Metrics Analysis
        *   Intrinsic Motivation Trigger & Impact Analysis (initial conceptual version integrated)
*   **Visualization Components (`visualizers/`):**
    *   `timeseries_plotter.py`: Matplotlib-based time-series plots.
    *   `state_visualizer.py`: Textual representations of agent states.
*   **API (`api.py`):** `PiaAVTAPI` facade for programmatic access.
*   **Command-Line Interface (`cli.py`):** CLI access to core functionalities.
*   **WebApp (`webapp/app.py`):** Streamlit Proof-of-Concept for interactive analysis (log upload, stats, plotting, sequences, raw log view).
*   **Examples (`examples/`):** Scripts demonstrating API and CLI usage. The main analysis scripts in `Analysis_Implementations/` also serve as usage examples via their `if __name__ == "__main__":` blocks. See also `conceptual_piase_log_generation.md` for how sample logs for these analyses could be produced from PiaSE.
*   **Unit Tests (`tests/`):** For core components.
*   **Requirements (`requirements.txt`):** Python dependencies.

## WebApp Setup and Usage

The PiaAVT WebApp (Streamlit) provides interactive log analysis.
1.  **Navigate to PiaAVT root:** `cd path/to/your/PiaAGI_Research_Tools/PiaAVT`
2.  **Virtual Environment (Recommended):** `python -m venv .venv` then activate it.
3.  **Install dependencies:** `pip install -r requirements.txt`
4.  **Run WebApp:** `streamlit run webapp/app.py`
    Access via the local URL provided by Streamlit (e.g., `http://localhost:8501`).

Features: 
*   Log upload and parsing.
*   Global filters for source, event type, simulation ID, and timestamps.
*   Overview & Statistics tab for general log metrics and custom field statistics.
*   Time Series Plot tab for visualizing numeric fields over time.
*   Event Sequences tab for finding and displaying user-defined event patterns.
*   **Goal Dynamics Analysis tab:** View goal lifecycles, types, outcomes, and counts by type.
*   **Emotional State Trajectory Analysis tab:** Analyze and plot agent emotional states (Valence, Arousal, Dominance) over time.
*   **Intrinsic Motivation Analysis tab:** Inspect intrinsically motivated goals, their conceptual triggers, and impacts.
*   **Task Performance Analysis tab:** Review task success/failure rates, durations, and other performance metrics.
*   Raw Logs tab for viewing raw JSON log entries.

## Future Development & Enhancements

PiaAVT is planned to evolve into a powerful toolkit for deep AGI analysis. Key future directions include:

1.  **Advanced Analytical Modules:**
    *   **Refine Integrated Analyses:** The initial versions of Goal Dynamics, Emotional Trajectory, Task Performance, and Intrinsic Motivation analyses are now integrated into the API and WebApp. Future work involves:
        *   Further developing and fully implementing the 'Intrinsic Motivation Trigger & Impact Analysis' beyond its current conceptual integration.
        *   Refining and extending all integrated analyses with more advanced features, deeper metrics, and enhanced visualizations.
    *   **Causal Analysis:** Develop tools to help researchers infer potential causal relationships between agent actions, internal cognitive state changes (from PiaCML module logs), environmental events (from PiaSE logs), and observed outcomes.
    *   **Behavioral Pattern Mining:** Implement algorithms to automatically identify recurring sequences of behavior, decision patterns, or cognitive state transitions from extensive log data.
    *   **Ethical Reasoning Traceability:** Design analyses to visualize how an agent's ethical framework influences decision-making.
    *   **Comparative Analysis:** Tools for statistically comparing behaviors and states across different agent versions or conditions.
    *   *(See conceptual design document: `Advanced_Analyses_Causal.md`)*
    *   *(See conceptual design document: `Advanced_Analyses_Behavioral_Patterns.md`)*
    *   *(See conceptual design document: `Advanced_Analyses_Ethical_Traceability.md`)*

2.  **Rich Cognitive Visualizations (Conceptual & Implementation):**
    *   **LTM Explorer:** Develop methods to visualize Long-Term Memory (semantic, episodic, procedural).
    *   **Self-Model Dashboard:** Create a visual summary of key Self-Model components (capabilities, ethics, personality).
    *   **World Model Viewer:** Tools to inspect the agent's internal World Model and compare it with ground truth.
    *   **Cognitive Architecture Flow:** Dynamic visualizations of information flow between PiaCML modules.
    *   *(See conceptual design document: `Visualizations_LTM_Explorer.md`)*
    *   *(See conceptual design document: `Visualizations_Self_Model_Dashboard.md`)*
    *   *(See conceptual design document: `Visualizations_World_Model_Viewer.md`)*

3.  **Support for Meta-Cognitive Analysis (AGI Internalization of Tools):**
    *   **Extended Logging Specification:** The `Logging_Specification.md` has been updated to include new event types for capturing indicators of an agent's meta-cognitive processes (e.g., `MCP_GENERATED`, `SELF_CORRECTION_INITIATED`, `AGENT_TOOL_USED`).
    *   **Dedicated Analyses:** Conceptual designs for specific analyses leveraging these new log types are detailed in `Advanced_Analyses_Meta_Cognition.md`. Future work involves implementing these analyses to detect and quantify meta-cognitive activities, helping researchers understand self-monitoring, self-simulation, and internalized tool use.

4.  **Enhanced XAI (Explainable AI) Features:**
    *   Develop visualizations and summary methods that help explain *why* an agent made a particular decision or exhibited a specific behavior, by linking actions back to preceding internal states, goals, learned experiences, or ethical considerations.

5.  **Integration and Usability:**
    *   **Tighter PiaSE Integration:** Ensure PiaAVT can seamlessly ingest and correlate logs from complex, multi-faceted PiaSE scenarios.
    *   **PiaPES Feedback Loop:** Provide clear metrics and visualizations that PiaPES can use to evaluate the effectiveness of prompts and developmental curricula.
    *   **Scalability:** Investigate solutions for handling and analyzing very large log datasets from long-running simulations or numerous experimental runs.

6.  **Conceptual Designs for Advanced Features:**
    *   The following documents outline conceptual designs for future advanced analysis and visualization capabilities in PiaAVT. These provide a roadmap for further development:
        *   [`Advanced_Analyses_Causal.md`](Advanced_Analyses_Causal.md): Details approaches for inferring causal relationships from agent logs to understand cause-and-effect dynamics.
        *   [`Advanced_Analyses_Behavioral_Patterns.md`](Advanced_Analyses_Behavioral_Patterns.md): Describes methods for automatically discovering recurring behavioral patterns, sequences, and anomalies.
        *   [`Advanced_Analyses_Ethical_Traceability.md`](Advanced_Analyses_Ethical_Traceability.md): Outlines how to trace and visualize the influence of the agent's ethical framework on its decision-making.
        *   [`Advanced_Analyses_Meta_Cognition.md`](Advanced_Analyses_Meta_Cognition.md): Conceptualizes dedicated analyses for meta-cognitive processes like self-correction, tool use, and internal simulation, based on extended logging specifications.
        *   [`Visualizations_LTM_Explorer.md`](Visualizations_LTM_Explorer.md): Proposes visualization tools for inspecting Semantic, Episodic, and Procedural Long-Term Memory.
        *   [`Visualizations_Self_Model_Dashboard.md`](Visualizations_Self_Model_Dashboard.md): Designs a dashboard to display key aspects of the agent's Self-Model, including capabilities, ethics, and personality.
        *   [`Visualizations_World_Model_Viewer.md`](Visualizations_World_Model_Viewer.md): Conceptualizes tools for inspecting the agent's World Model and comparing it against ground truth.

PiaAVT's development will focus on providing increasingly deeper and more intuitive insights into the complex inner workings and developmental progress of PiaAGI agents.

---
Return to [PiaAGI Core Document](../../PiaAGI.md) | [Project README](../../README.md)
