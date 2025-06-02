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
    *   `basic_analyzer.py`: Filtering, descriptive statistics, time-series extraction. (Conceptual, path might need update if this is a specific file or integrated elsewhere)
    *   `event_sequencer.py`: Extracts defined event sequences. (Conceptual, path might need update if this is a specific file or integrated elsewhere)
    *   Implemented analyses: Goal Dynamics (Lifecycle), Emotional State Trajectory, Basic Task Performance Metrics, and a conceptual Intrinsic Motivation Trigger & Impact Analysis. These can be found in the `Analysis_Implementations/` directory.
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

Features: Log upload, global filters, overview/stats, time-series plotting, event sequence finder, raw log viewer.

## Future Development & Enhancements

PiaAVT is planned to evolve into a powerful toolkit for deep AGI analysis. Key future directions include:

1.  **Advanced Analytical Modules:**
    *   Further develop and fully implement the 'Intrinsic Motivation Trigger & Impact Analysis'. Refine and extend the existing implemented analyses (Goal Dynamics, Emotional Trajectory, Task Performance) with more advanced features and visualizations.
    *   **Causal Analysis:** Develop tools to help researchers infer potential causal relationships between agent actions, internal cognitive state changes (from PiaCML module logs), environmental events (from PiaSE logs), and observed outcomes.
    *   **Behavioral Pattern Mining:** Implement algorithms to automatically identify recurring sequences of behavior, decision patterns, or cognitive state transitions from extensive log data.
    *   **Ethical Reasoning Traceability:** Design analyses to visualize how an agent's ethical framework (from its Self-Model logs) influences its planning and decision-making processes, especially in scenarios involving ethical dilemmas. This could involve tracing which ethical rules were activated or prioritized.
    *   **Comparative Analysis:** Tools for statistically comparing behaviors, learning rates, or internal states across different agent versions, configurations, or developmental curricula.

2.  **Rich Cognitive Visualizations (Conceptual & Implementation):**
    *   **LTM Explorer:** Develop methods to visualize the structure and content of an agent's Long-Term Memory, such as rendering Semantic LTM as an interactive knowledge graph or Episodic LTM as a filterable, annotated timeline.
    *   **Self-Model Dashboard:** Create a visual summary of key Self-Model components, such as self-assessed capabilities, confidence levels in different knowledge domains, active values, and representations of its own personality traits.
    *   **World Model Viewer:** Tools to inspect and compare the agent's internal World Model with the ground truth from PiaSE, highlighting discrepancies or uncertainties.
    *   **Cognitive Architecture Flow:** Dynamic visualizations of information flow and activation patterns between different PiaCML modules during task execution.

3.  **Support for Meta-Cognitive Analysis (AGI Internalization of Tools):**
    *   **Extended Logging Specification:** Define new conceptual log event types in `Logging_Specification.md` that could capture indicators of an agent's meta-cognitive processes (e.g., `AGENT_SELF_CORRECTION_ATTEMPT`, `AGENT_INTERNAL_SCENARIO_GENERATION`, `AGENT_MCP_USAGE_LOG`).
    *   **Dedicated Analyses:** Develop specific analyses in PiaAVT to detect and quantify these meta-cognitive activities, helping researchers understand if and how an agent is learning to self-monitor, self-simulate, or encapsulate its own learned skills (inspired by `PiaAGI.md` Section 4.5).

4.  **Enhanced XAI (Explainable AI) Features:**
    *   Develop visualizations and summary methods that help explain *why* an agent made a particular decision or exhibited a specific behavior, by linking actions back to preceding internal states, goals, learned experiences, or ethical considerations.

5.  **Integration and Usability:**
    *   **Tighter PiaSE Integration:** Ensure PiaAVT can seamlessly ingest and correlate logs from complex, multi-faceted PiaSE scenarios.
    *   **PiaPES Feedback Loop:** Provide clear metrics and visualizations that PiaPES can use to evaluate the effectiveness of prompts and developmental curricula.
    *   **Scalability:** Investigate solutions for handling and analyzing very large log datasets from long-running simulations or numerous experimental runs.

PiaAVT's development will focus on providing increasingly deeper and more intuitive insights into the complex inner workings and developmental progress of PiaAGI agents.

---
Return to [PiaAGI Core Document](../../PiaAGI.md) | [Project README](../../README.md)
