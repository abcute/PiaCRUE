<!-- PiaAGI AGI Research Framework Document -->
# PiaAGI Agent Analysis & Visualization Toolkit (PiaAVT) - Conceptual Design

## 1. Purpose and Goals

**Purpose:**
The PiaAGI Agent Analysis & Visualization Toolkit (PiaAVT) is designed to provide researchers and developers with a comprehensive suite of tools to log, analyze, understand, and visualize the behavior, internal cognitive states, learning trajectories, and developmental progress of PiaAGI agents.

**Goals:**
*   **Deepen Understanding of AGI Behavior:** Enable researchers to go beyond observing input-output behavior and gain insights into the internal workings of PiaAGI agents.
*   **Evaluate Cognitive Module Performance:** Provide tools to assess the functioning and effectiveness of individual cognitive modules (from PiaCML) and their interactions within an agent.
*   **Track Learning and Development:** Allow for the longitudinal analysis of agent learning, adaptation, and progression through developmental stages ([Section 3.2.1 of `PiaAGI.md`](../PiaAGI.md#321-stages-of-cognitive-development-and-architectural-maturation)).
*   **Debug and Refine Agents:** Help developers identify bottlenecks, unintended behaviors, and areas for improvement in PiaAGI agent configurations.
*   **Facilitate Explainable AI (XAI):** Support the generation of explanations for agent decisions and actions by visualizing internal reasoning paths and state changes (linking to Self-Model outputs, [Section 4.1.10 of `PiaAGI.md`](../PiaAGI.md#41-core-modules-and-their-interactions)).
*   **Compare Agent Performance:** Enable quantitative and qualitative comparison of different PiaAGI agent versions or configurations under various conditions.
*   **Support Scientific Communication:** Provide tools for generating visualizations and summary statistics suitable for research publications and presentations.

## 2. Key Features and Functionalities

PiaAVT will consist of the following key features and functionalities:

### 2.1. Core Conceptual Analyses (Initial Set)

PiaAVT will be designed to perform a variety of analyses on agent logs. Below are three foundational conceptual analyses planned for early development, crucial for understanding core PiaAGI agent behavior and internal states. These analyses will leverage the [PiaAGI Logging Specification](Logging_Specification.md).

#### 2.1.1. Goal Lifecycle Tracking & Success Rate

*   **Purpose:** To understand how the agent manages its goals (from its Motivational System), its persistence, and its effectiveness in achieving them. This is vital for assessing core functionality, planning, and motivational dynamics.
*   **Input Log Data Requirements:**
    *   `timestamp`
    *   `agent_id`
    *   `event_type`: Specifically `GOAL_CREATED`, `GOAL_ACTIVATED`, `GOAL_STATUS_CHANGED` (with `old_status`, `new_status`), `GOAL_ACHIEVED`, `GOAL_FAILED`.
    *   `event_data`:
        *   From `GOAL_CREATED`: `goal_id`, `description`, `type` (e.g., intrinsic/extrinsic), `priority`, `source_trigger_event_id` (optional).
        *   From `GOAL_ACTIVATED`: `goal_id`.
        *   From `GOAL_STATUS_CHANGED`: `goal_id`, `old_status`, `new_status`.
        *   From `GOAL_ACHIEVED`: `goal_id`, `completion_time_ms` (optional, can be calculated).
        *   From `GOAL_FAILED`: `goal_id`, `reason` (optional).
*   **Conceptual Analysis Logic:**
    1.  Filter logs for relevant `event_type`s for a specific `agent_id` and `simulation_run_id`.
    2.  Group events by `goal_id`.
    3.  For each goal, reconstruct its lifecycle by ordering events by `timestamp` (creation, activation, status changes, final outcome).
    4.  Calculate metrics: total goals created/activated/achieved/failed, success rate (achieved / (achieved + failed)), average active duration for achieved vs. failed goals, distribution of goal types and priorities.
*   **Expected Insights & Output:**
    *   Summary statistics (tables or key values).
    *   Visualizations: Timelines per goal, bar charts for success/failure rates by goal type.
    *   Helps evaluate the `MotivationalSystemModule` and aspects of planning and execution.

#### 2.1.2. Emotional State Trajectory (VAD over Time)

*   **Purpose:** To visualize and understand the agent's affective dynamics (as modeled by its Emotion Module) throughout a simulation, correlating emotional shifts with significant events.
*   **Input Log Data Requirements:**
    *   `timestamp`
    *   `agent_id`
    *   `event_type`: `EMOTION_STATE_UPDATED`.
    *   `event_data`:
        *   `current_vad`: `{"valence": float, "arousal": float, "dominance": float}`.
        *   `current_discrete_emotion`: (Optional) string.
        *   `trigger_event_summary`: (Optional) string.
    *   (Optional) Timestamps and summaries of other significant events (e.g., `GOAL_FAILED`, `REWARD_SIGNAL_ISSUED`) for temporal correlation.
*   **Conceptual Analysis Logic:**
    1.  Filter `EMOTION_STATE_UPDATED` events.
    2.  Extract VAD (Valence, Arousal, Dominance) values for each entry.
    3.  Construct time series for V, A, and D against `timestamp`.
    4.  (Optional) Identify timestamps of other significant logged events to overlay or correlate.
*   **Expected Insights & Output (Visualization Sketch):**
    *   **Visualization Type:** Multiple line graphs on a shared time axis (one each for V, A, D).
    *   **Key Elements:**
        *   Title: "Agent Emotional Trajectory (Valence, Arousal, Dominance) - Run: [simulation_run_id]"
        *   X-axis: Simulation Time.
        *   Y-axis: Intensity / Level (for V, A, D values).
        *   Distinct lines for V, A, D with a clear legend.
        *   **Event Markers:** Vertical lines/symbols on the time axis at points of significant correlated events (e.g., `GOAL_FAILED`, salient `PERCEPTION_INPUT_PROCESSED`), with tooltips showing event details.
    *   **Textual Summary:**
        *   Overall profile: Average V, A, D; standard deviations; predominant discrete emotions.
        *   Significant shifts: List of largest V/A/D changes with timestamps and correlated event triggers.
        *   Emotional reactivity: Average V/A/D change after specific event types.
    *   Helps evaluate the `EmotionModule` and overall agent affective responsiveness.

#### 2.1.3. Basic Task Performance Metrics

*   **Purpose:** To provide high-level measures of the agent's effectiveness in completing defined tasks within PiaSE.
*   **Input Log Data Requirements:**
    *   `timestamp`
    *   `agent_id`
    *   `source_component_id`: To filter for PiaSE environment logs.
    *   `event_type`: `TASK_STATUS_UPDATE` (from PiaSE), `AGENT_ACTION_EXECUTED_IN_ENV`.
    *   `event_data`:
        *   From `TASK_STATUS_UPDATE`: `task_id`, `status` ("STARTED", "COMPLETED_SUCCESS", "COMPLETED_FAILURE", "ABORTED").
        *   From `AGENT_ACTION_EXECUTED_IN_ENV`: `agent_id_acting`, `action_details`.
*   **Conceptual Analysis Logic:**
    1.  Filter `TASK_STATUS_UPDATE` events.
    2.  For each unique `task_id`, find its "STARTED" and final status event to determine outcome and duration.
    3.  Count `AGENT_ACTION_EXECUTED_IN_ENV` events for the agent within the task's timeframe.
*   **Expected Insights & Output:**
    *   Summary table: Task success rates, average time to completion for successful tasks, average number of actions per successful task.
    *   Lists of failed tasks.
    *   Provides a baseline for overall agent competence and efficiency.

These initial analyses will form the core of PiaAVT's early functionality, providing essential feedback for PiaAGI development.

### 2.2. General Toolkit Features

*   **Data Logging Framework Integration:**
    *   Seamless integration with logging mechanisms from PiaSE and PiaCML.
    *   Ability to define and configure what data is logged (e.g., module states, inter-module communication, memory traces, goal states, emotional states, decision parameters).
    *   Support for various log data formats (e.g., structured text, CSV, HDF5, time-series databases).
*   **Behavioral Analysis Tools:**
    *   Metrics for task performance (e.g., success rates, completion times, efficiency).
    *   Analysis of action sequences and decision points.
    *   Tools for identifying behavioral patterns, anomalies, and emergent strategies.
    *   Statistical analysis of behavioral data.
*   **Internal State Visualization:**
    *   **Cognitive Architecture Graph:** Dynamic visualization of the active PiaAGI cognitive architecture ([Section 4 of `PiaAGI.md`](../PiaAGI.md#4-the-piaagi-cognitive-architecture)), showing active modules and information flow between them in real-time or during replay.
    *   **Memory Visualization:**
        *   Tools to inspect contents of LTM (e.g., semantic network graphs for Semantic LTM, timelines for Episodic LTM, [Section 4.1.3 of `PiaAGI.md`](../PiaAGI.md#41-core-modules-and-their-interactions)).
        *   Visualization of WM content and Central Executive focus over time.
    *   **Motivational System Visualization:** Display current goal hierarchies, goal priorities, intrinsic/extrinsic motivation levels, and generation of intrinsic reward signals ([Section 4.1.6 of `PiaAGI.md`](../PiaAGI.md#41-core-modules-and-their-interactions)).
    *   **Emotional State Visualization:** Track and display the agent's emotional state (e.g., valence/arousal graphs, discrete emotion timelines, [Section 4.1.7 of `PiaAGI.md`](../PiaAGI.md#41-core-modules-and-their-interactions)).
    *   **World Model Visualization:** Tools to inspect the agent's internal World Model ([Section 4.3 of `PiaAGI.md`](../PiaAGI.md#43-perception-and-world-modeling-conceptual)), including its representation of the environment, objects, and other agents (e.g., differences between agent's model and ground truth from PiaSE).
    *   **Self-Model Visualization:** Display key aspects of the Self-Model, such as confidence levels, self-assessed capabilities, and active ethical principles ([Section 4.1.10 of `PiaAGI.md`](../PiaAGI.md#41-core-modules-and-their-interactions)).
    *   **ToM Visualization:** Show inferred mental states of other agents ([Section 4.1.11 of `PiaAGI.md`](../PiaAGI.md#41-core-modules-and-their-interactions)).
*   **Learning Trajectory Analysis:**
    *   Plot learning curves for various skills and knowledge domains.
    *   Analyze changes in module parameters or LTM content over time.
    *   Tools for identifying learning plateaus, catastrophic forgetting events, or successful transfer learning.
*   **Developmental Stage Assessment:**
    *   Metrics and visualizations to help assess an agent's current developmental stage based on its manifested capabilities (linking to [Section 3.2.1 of `PiaAGI.md`](../PiaAGI.md#321-stages-of-cognitive-development-and-architectural-maturation)).
    *   Comparison of agent behavior against expected milestones for each stage.
*   **Query and Filtering Interface:**
    *   Allow users to query logged data for specific events, states, or patterns.
    *   Filter data based on time, module, agent, or experimental condition.
*   **Reporting and Export:**
    *   Generate summary reports with key metrics and visualizations.
    *   Export data and visualizations in various formats (e.g., CSV, PDF, PNG).
*   **Plugin Architecture:**
    *   Allow for custom analysis scripts and visualization plugins.

## 3. Target Users

*   **PiaAGI Developers & Researchers:** To understand, debug, and evaluate their agents.
*   **Cognitive Scientists/Psychologists:** To analyze how implemented cognitive models behave and evolve.
*   **AI Ethicists:** To scrutinize agent decision-making processes and value alignment.
*   **Students and Educators:** As a tool for learning about cognitive architectures and AGI.

## 4. High-level Architectural Overview

*   **Data Ingestion Layer:**
    *   Connectors for various log sources (PiaSE, PiaCML direct logging).
    *   Parser for different log formats.
    *   Data validation and preprocessing.
*   **Data Storage Layer:**
    *   Option for in-memory analysis for smaller datasets.
    *   Integration with time-series databases (e.g., InfluxDB, Prometheus) or document stores (e.g., MongoDB) for large-scale, persistent logging.
*   **Analysis Engine (Python-based):**
    *   Core library of analysis functions (statistical, pattern matching, machine learning for log analysis).
    *   Leverages scientific Python stack (NumPy, SciPy, Pandas, scikit-learn).
*   **Visualization Engine:**
    *   Plotting libraries (Matplotlib, Seaborn, Plotly, Bokeh) for static and interactive charts.
    *   Network visualization libraries (NetworkX, Gephi (via export)) for memory graphs, social networks.
    *   Potentially custom GUI components for specific visualizations (e.g., dynamic architecture graph).
*   **User Interface Layer:**
    *   Could range from a Jupyter Notebook interface for interactive analysis to a dedicated web application (e.g., using Dash/Streamlit or Flask/Django with a JavaScript frontend) for more complex visualizations and dashboards.
*   **API for Extensibility:**
    *   Python API to allow users to script analyses and develop custom visualization plugins.

**Potential Technologies:**
*   **Primary Language:** Python
*   **Data Handling & Analysis:** Pandas, NumPy, SciPy, scikit-learn, Apache Spark (for very large datasets).
*   **Visualization:** Matplotlib, Seaborn, Plotly, Bokeh, Dash/Streamlit.
*   **Databases (Optional):** InfluxDB, Prometheus, MongoDB, PostgreSQL (with TimescaleDB).
*   **GUI/Web:** Qt (via PyQt/PySide), Dash, Streamlit, or custom web frameworks.

## 5. Potential Integration Points with the PiaAGI Framework

*   **PiaAGI Simulation Environment (PiaSE):** PiaAVT is the primary consumer of logs generated by PiaSE. It will analyze agent-environment interactions, task performance, and events occurring within the simulation.
*   **Cognitive Module Library (PiaCML):** PiaAVT will analyze logs generated directly by PiaCML modules, providing insights into their internal states, processing dynamics, and learning progress. For example, visualizing the changing structure of a Semantic LTM graph or the activation patterns in a WM module.
*   **PiaAGI Agents:** PiaAVT helps visualize and understand the holistic behavior emerging from the interaction of modules within a complete PiaAGI agent.
*   **PiaAGI Prompt Engineering Suite (PiaPES):** PiaAVT can help evaluate the effectiveness of prompts and developmental scaffolding designed with PiaPES by analyzing the resulting agent behavior and developmental trajectories. For instance, comparing learning curves of agents trained with different scaffolding strategies.
*   **Developmental Stages ([Section 3.2.1 of `PiaAGI.md`](../PiaAGI.md#321-stages-of-cognitive-development-and-architectural-maturation)):** PiaAVT will provide tools to track an agent's progress against the defined developmental stages, visualizing the acquisition of milestone capabilities.
*   **Ethical Framework Analysis:** PiaAVT can be used to trace how ethical principles within the Self-Model ([Section 4.1.10 of `PiaAGI.md`](../PiaAGI.md#41-core-modules-and-their-interactions)) influence decision-making in the Planning Module ([Section 4.1.8 of `PiaAGI.md`](../PiaAGI.md#41-core-modules-and-their-interactions)), particularly when analyzing logs from ethical dilemma scenarios.

PiaAVT will be indispensable for making the complex internal dynamics of PiaAGI agents transparent, understandable, and amenable to scientific inquiry and iterative improvement.

---
Return to [PiaAGI Core Document](../PiaAGI.md) | [Project README](../README.md)
