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
*   **Analyzers (`analyzers/`):**
    *   `basic_analyzer.py`:
        *   Filter logs by source, event_type, and time range.
        *   Calculate descriptive statistics (mean, median, min, max, stddev, count, sum) for numeric data fields (supports nested paths within the `data` field of a log).
        *   Extract time-series data (timestamp, value) for specified fields.
        *   Count unique occurrences of values in log fields.
    *   `event_sequencer.py`:
        *   Extracts sequences of log entries matching a defined pattern of events (event_type and optional source).
        *   Supports constraints like maximum time between steps and maximum intervening logs.
        *   Provides formatted string output for found sequences.
*   **Visualization Components (`visualizers/`):**
    *   `timeseries_plotter.py`: Generate line plots for time-series data using Matplotlib. Customizable titles, labels, and output to file. Optionally uses `mplcursors` for interactive tooltips if available.
    *   `state_visualizer.py`: Provide textual representations for agent states, such as:
        *   Formatting dictionaries into human-readable strings.
        *   Displaying current agent goals (from structured log data).
        *   Visualizing working memory contents (from structured log data).
*   **API (`api.py`):**
    *   A user-friendly facade (`PiaAVTAPI`) to simplify interaction with the toolkit.
    *   Methods for loading logs, accessing analysis functions (including event sequencing), and triggering visualizations.
*   **Command-Line Interface (`cli.py`):**
    *   Provides command-line access to core PiaAVT functionalities like loading logs, generating stats, plotting, and finding event sequences.
*   **WebApp (`webapp/app.py`):**
    *   A Streamlit-based web application for interactive analysis and visualization (Proof of Concept).
    *   Features include log file upload, overview statistics, time-series plotting, and event sequence analysis.
*   **Examples (`examples/`):**
    *   `example_learning_progress.py`: Demonstrates API usage for analyzing learning metrics.
    *   `example_emotional_trajectory.py`: Shows API usage for visualizing emotional state changes.
    *   `example_cli_usage.sh`: A shell script demonstrating common CLI commands.
*   **Unit Tests (`tests/`):**
    *   `test_logging_system.py`, `test_basic_analyzer.py`, `test_event_sequencer.py`, `test_cli.py`, `test_visualizers.py`.

## Architecture Overview

PiaAVT is structured into several key components:

-   **`core/`**: Contains the `logging_system.py` module.
-   **`analyzers/`**: Houses modules like `basic_analyzer.py` and `event_sequencer.py`.
-   **`visualizers/`**: Includes `timeseries_plotter.py` and `state_visualizer.py`.
-   **`api.py`**: The `PiaAVTAPI` class, the main programmatic entry point.
-   **`cli.py`**: The command-line interface script.
-   **`webapp/`**: Contains the Streamlit web application (`app.py`).
-   **`examples/`**: Provides practical usage scripts.
-   **`tests/`**: Contains `unittest`-based test suites.

## Basic Usage (API)

The primary way to interact with PiaAVT programmatically is through the `PiaAVTAPI` class.
```python
from PiaAGI_Hub.PiaAVT.api import PiaAVTAPI
api = PiaAVTAPI()
if api.load_logs_from_json("path/to/logs.json"):
    # ... use api methods ...
    stats = api.get_stats_for_field("data.reward", event_type="Action")
    if stats: api.display_formatted_dict(stats, title="Reward Stats")
    # ... etc. ...
```
Refer to the scripts in the `examples/` directory for more detailed API usage.

## Command-Line Interface (CLI) Usage

PiaAVT includes a command-line interface (`cli.py`) for quick analysis and scripting.

1.  **Navigate to the PiaAVT directory:**
    ```bash
    cd PiaAGI_Hub/PiaAVT
    ```
2.  **Run commands using `python cli.py <command> [options]`:**
    *   **Load logs:** `python cli.py load path/to/your/logs.json`
    *   **Get stats:** `python cli.py stats data.reward --event_type Action`
    *   **Plot data:** `python cli.py plot data.value --output myplot.png --no_show`
    *   **Find sequences:** `python cli.py sequences "EventTypeA,EventTypeB" --max_time 10`
    *   **List logs:** `python cli.py list_logs --limit 5`

For detailed options for each command, use `python cli.py <command> -h`.
See `examples/example_cli_usage.sh` for more examples.

## WebApp Setup and Usage

PiaAVT includes a web application built with Streamlit for interactive data exploration.

### Dependencies

The web application requires the following core Python libraries:
-   `streamlit`
-   `pandas` (used by Streamlit for some data display, and potentially useful for future enhancements)
-   `matplotlib` (as it's used by the `TimeseriesPlotter`)

Optional for enhanced plot interactivity:
-   `mplcursors`

These dependencies should ideally be listed in a `requirements.txt` file for easier setup (future step). You can install them using pip:
```bash
pip install streamlit pandas matplotlib mplcursors
```

### Running the WebApp

1.  **Navigate to the PiaAVT directory:**
    Make sure your terminal's current working directory is `PiaAGI_Hub/PiaAVT/`. This is important for the application to correctly resolve internal imports (like the `PiaAVTAPI`).
    ```bash
    cd path/to/your/PiaAGI_Hub/PiaAVT
    ```
2.  **Run the Streamlit application:**
    Execute the following command:
    ```bash
    streamlit run webapp/app.py
    ```
    Streamlit will typically open the application in your default web browser.

### Basic Features

The WebApp provides an interactive way to use PiaAVT:

-   **Log File Upload:** Use the sidebar to upload your agent's JSON log file. The application will process this file using `PiaAVTAPI`.
-   **Overview & Stats Tab:**
    -   View basic information about the loaded logs (filename, total entries).
    -   See counts of unique sources and event types in the dataset.
    -   Interactively calculate and display descriptive statistics for specific data fields (e.g., `data.reward`).
-   **Time Series Plot Tab:**
    -   Generate line plots for numeric data fields over time.
    -   Customize plot titles and Y-axis labels.
    -   If `mplcursors` is installed, plots can offer interactive tooltips on data points.
-   **Event Sequences Tab:**
    -   Define event sequences using either a JSON string (for complex definitions with sources) or a simple comma-separated list of event types.
    -   Specify constraints like maximum time between steps or maximum intervening logs.
    -   View the formatted list of found sequences.
-   **Raw Logs Tab:**
    -   Provides a basic way to view the first few raw log entries in JSON format.

The WebApp is currently a Proof of Concept (PoC) and will be enhanced with more features and refined user experience in the future.

## Future Development

Future enhancements may include:
-   Support for more log input formats (e.g., CSV, direct streaming).
-   Advanced analysis techniques (e.g., anomaly detection, comparative analysis).
-   More sophisticated visualization types (e.g., interactive plots, network graphs for memory/social models).
-   A graphical user interface (GUI) for easier interaction (the WebApp is a first step).
-   Integration with databases for larger log datasets.
-   More robust CLI argument parsing, especially for complex inputs like sequence definitions.
-   Creation of a `requirements.txt` for easier dependency management.

Contributions are welcome! Please see the main project's `CONTRIBUTING.md`.
```
