# PiaAGI Agent Analysis & Visualization Toolkit (PiaAVT)

This directory contains the PiaAGI Agent Analysis & Visualization Toolkit (PiaAVT), a Python-based toolkit designed to assist in understanding and evaluating PiaAGI agents.

PiaAVT provides tools to log, analyze, and visualize agent behavior, internal cognitive states (conceptualized), learning trajectories, and developmental progress.

Refer to the main conceptual design document at [../../PiaAGI_Hub/PiaAGI_Agent_Analysis_Visualization_Toolkit.md](../../PiaAGI_Hub/PiaAGI_Agent_Analysis_Visualization_Toolkit.md) for the overarching purpose and goals of PiaAVT.

## Current Features (Initial Build)

*   **Logging System (`core/logging_system.py`):**
    *   Standardized `LogEntry` structure (Python dictionary).
    *   Ingestion of logs from JSON files.
    *   Validation of log entries against required fields (timestamp, source, event_type, data) and formats.
    *   In-memory log storage.
*   **Basic Analyzer (`analyzers/basic_analyzer.py`):**
    *   Filter logs by source, event_type, and time range.
    *   Calculate descriptive statistics (mean, median, min, max, stddev, count, sum) for numeric data fields (supports nested paths within the `data` field of a log).
    *   Extract time-series data (timestamp, value) for specified fields.
    *   Count unique occurrences of values in log fields.
*   **Visualization Components (`visualizers/`):**
    *   `timeseries_plotter.py`: Generate line plots for time-series data using Matplotlib. Customizable titles, labels, and output to file.
    *   `state_visualizer.py`: Provide textual representations for agent states, such as:
        *   Formatting dictionaries into human-readable strings.
        *   Displaying current agent goals (from structured log data).
        *   Visualizing working memory contents (from structured log data).
*   **API (`api.py`):**
    *   A user-friendly facade (`PiaAVTAPI`) to simplify interaction with the toolkit.
    *   Methods for loading logs, accessing analysis functions, and triggering visualizations.
*   **Examples (`examples/`):**
    *   `example_learning_progress.py`: Demonstrates loading sample learning logs, calculating statistics, and plotting learning curves (e.g., reward/error over epochs).
    *   `example_emotional_trajectory.py`: Shows how to load and visualize simulated emotional state changes (e.g., valence/arousal over time) and inspect individual state snapshots.
*   **Unit Tests (`tests/`):**
    *   Tests for the logging system, basic analyzer, and core visualizer functionalities.

## Architecture Overview

PiaAVT is structured into several key components:

-   **`core/`**: Contains the `logging_system.py` module, which is responsible for the definition of log structures, ingestion from sources (currently JSON files), validation, and storage of log data.
-   **`analyzers/`**: Houses modules like `basic_analyzer.py` that perform data processing and statistical analysis on the ingested logs.
-   **`visualizers/`**: Includes modules for creating visual representations of data and agent states. `timeseries_plotter.py` uses Matplotlib for 2D plots, and `state_visualizer.py` provides textual summaries.
-   **`api.py`**: The `PiaAVTAPI` class acts as the main entry point to the toolkit, orchestrating the functionalities of the core, analyzer, and visualizer components.
-   **`examples/`**: Provides practical scripts showing how to use the `PiaAVTAPI` to perform common analysis and visualization tasks.
-   **`tests/`**: Contains `unittest`-based test suites for ensuring the reliability and correctness of the toolkit's components.

## Basic Usage

The primary way to interact with PiaAVT is through the `PiaAVTAPI` class found in `PiaAGI_Hub.PiaAVT.api`.

1.  **Import the API:**
    ```python
    from PiaAGI_Hub.PiaAVT.api import PiaAVTAPI
    ```
    *(Note: You might need to ensure `PiaAGI_Hub` is in your `PYTHONPATH` if PiaAVT is not formally installed as a package.)*

2.  **Initialize the API:**
    ```python
    api = PiaAVTAPI()
    ```

3.  **Load Log Data:**
    PiaAVT currently supports loading logs from JSON files, where the file contains a list of log entry dictionaries. Each log entry should ideally conform to the structure: `{"timestamp": "ISO_FORMAT_STR", "source": "module_name", "event_type": "event_description", "data": {...}}`.
    ```python
    log_file_path = "path/to/your/agent_logs.json"
    if api.load_logs_from_json(log_file_path):
        print(f"Loaded {api.get_log_count()} logs.")
    else:
        print(f"Failed to load logs from {log_file_path}.")
        # Handle error
    ```

4.  **Perform Analysis:**
    Once logs are loaded, you can use the analyzer (accessed via `api.get_analyzer()`) or direct API methods.
    ```python
    # Example: Get statistics for a 'reward' field in 'Action' events
    reward_stats = api.get_stats_for_field(
        data_field_path="reward",
        event_type="Action"
    )
    if reward_stats:
        api.display_formatted_dict(reward_stats, title="Reward Statistics")
    ```

5.  **Generate Visualizations:**
    ```python
    # Example: Plot 'reward' over time for 'Action' events
    api.plot_field_over_time(
        data_field_path="reward",
        event_type="Action",
        title="Agent Rewards Over Time",
        y_label="Reward Value",
        output_file="reward_plot.png", # Optional: to save the plot
        show_plot=True
    )
    ```

Refer to the scripts in the `examples/` directory for more detailed usage scenarios, including:
-   `example_learning_progress.py`: Analyzing and plotting learning metrics.
-   `example_emotional_trajectory.py`: Visualizing emotional state changes.

## Future Development

Future enhancements may include:
-   Support for more log input formats (e.g., CSV, direct streaming).
-   Advanced analysis techniques (e.g., anomaly detection, comparative analysis).
-   More sophisticated visualization types (e.g., interactive plots, network graphs for memory/social models).
-   A graphical user interface (GUI) for easier interaction.
-   Integration with databases for larger log datasets.

Contributions are welcome! Please see the main project's `CONTRIBUTING.md`.
```
