# PiaAGI_Hub/PiaAVT/api.py

from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
import json # Added import json for the __main__ block example

# Attempt to import from sibling directories core, analyzers, visualizers
# This structure assumes PiaAVT is used as a package or these paths are configured.
try:
    from .core.logging_system import LoggingSystem, LogEntry, DEFAULT_TIMESTAMP_FORMAT, LogValidationError
    from .analyzers.basic_analyzer import BasicAnalyzer
    from .analyzers.event_sequencer import EventSequencer
    from .visualizers.timeseries_plotter import TimeseriesPlotter
    from .visualizers.state_visualizer import StateVisualizer
except ImportError:
    # Fallback for environments where the relative import doesn't work (e.g., running script directly)
    # This might happen if PiaAVT is not installed as a package and PYTHONPATH isn't set up.
    # For robust use, PiaAVT should be structured and installed as a proper Python package.
    print("PiaAVT API: Attempting fallback imports. For proper package structure, ensure PiaAVT is installable.")
    from core.logging_system import LoggingSystem, LogEntry, DEFAULT_TIMESTAMP_FORMAT, LogValidationError
    from analyzers.basic_analyzer import BasicAnalyzer
    from analyzers.event_sequencer import EventSequencer
    from visualizers.timeseries_plotter import TimeseriesPlotter
    from visualizers.state_visualizer import StateVisualizer


class PiaAVTAPI:
    """
    Main API Facade for interacting with the PiaAGI Agent Analysis & Visualization Toolkit (PiaAVT).

    This class provides a high-level interface to the toolkit's functionalities,
    simplifying tasks such as loading log data, performing common analyses,
    and generating visualizations. It orchestrates the underlying components:
    LoggingSystem, BasicAnalyzer, EventSequencer, TimeseriesPlotter, and StateVisualizer.

    Attributes:
        logging_system (LoggingSystem): Instance for log ingestion and storage.
        analyzer (Optional[BasicAnalyzer]): Instance for basic log analysis; initialized after logs are loaded.
        event_sequencer (Optional[EventSequencer]): Instance for event sequence analysis; initialized after logs are loaded.
        timeseries_plotter (TimeseriesPlotter): Instance for generating time-series plots.
        state_visualizer (StateVisualizer): Instance for creating textual representations of agent states.
        _active_log_file (Optional[str]): Path to the currently loaded log file.
    """

    def __init__(self):
        """
        Initializes the PiaAVTAPI, setting up instances of internal components.
        """
        self.logging_system = LoggingSystem()
        self.analyzer: Optional[BasicAnalyzer] = None
        self.event_sequencer: Optional[EventSequencer] = None
        self.timeseries_plotter = TimeseriesPlotter()
        self.state_visualizer = StateVisualizer()
        self._active_log_file: Optional[str] = None

    def load_logs_from_json(self, file_path: str, validate: bool = True) -> bool:
        """
        Loads log data from a specified JSON file into the LoggingSystem.
        If successful, it initializes the BasicAnalyzer and EventSequencer with the loaded logs.
        Clears any previously loaded logs before loading new ones.

        Args:
            file_path (str): The path to the JSON log file. The file should contain a
                             list of log entry dictionaries.
            validate (bool): Whether to validate log entries during ingestion according
                             to the LoggingSystem's rules. Defaults to True.

        Returns:
            bool: True if logs were loaded and analyzers initialized successfully, False otherwise.
        """
        try:
            self.logging_system.clear_logs() # Clear previous logs
            self.logging_system.load_logs_from_json_file(file_path, validate=validate)
            loaded_logs = self.logging_system.get_log_data()
            self.analyzer = BasicAnalyzer(loaded_logs)
            self.event_sequencer = EventSequencer(loaded_logs)
            self._active_log_file = file_path
            print(f"API: Successfully loaded and initialized analyzers with logs from {file_path}")
            return True
        except (FileNotFoundError, json.JSONDecodeError, LogValidationError) as e:
            self.analyzer = None # Ensure analyzers are not stale
            self.event_sequencer = None
            self._active_log_file = None
            print(f"API Error: Failed to load logs from {file_path}. {e}")
            return False
        except Exception as e: # Catch any other unexpected errors during loading/init
            self.analyzer = None
            self.event_sequencer = None
            self._active_log_file = None
            print(f"API Error: An unexpected error occurred loading logs from {file_path}. {e}")
            return False

    def get_log_count(self) -> int:
        """
        Returns the total number of log entries currently loaded in the LoggingSystem.

        Returns:
            int: The count of loaded log entries.
        """
        return self.logging_system.get_log_count()

    def get_all_logs(self) -> List[LogEntry]:
        """
        Retrieves all log entries currently loaded in the LoggingSystem.

        Returns:
            List[LogEntry]: A list of all loaded log entries.
        """
        return self.logging_system.get_log_data()

    def get_active_log_file(self) -> Optional[str]:
        """
        Returns the file path of the log file that was last successfully loaded.

        Returns:
            Optional[str]: The path to the active log file, or None if no file is active
                           or if loading failed.
        """
        return self._active_log_file

    def get_analyzer(self) -> Optional[BasicAnalyzer]:
        """
        Provides access to the BasicAnalyzer instance associated with the currently loaded logs.
        This allows for more direct or advanced use of the analyzer's methods if needed,
        beyond the facade methods provided by this API class.

        Returns:
            Optional[BasicAnalyzer]: The BasicAnalyzer instance if logs are successfully loaded,
                                     otherwise None.
        """
        if not self.analyzer:
            print("API Warning: No log data loaded. Please load logs using 'load_logs_from_json' first.")
        return self.analyzer

    # --- Direct Analysis & Visualization Methods (Facades) ---

    def get_stats_for_field(self,
                            data_field_path: Union[str, List[str]],
                            source: Optional[str] = None,
                            event_type: Optional[str] = None,
                            start_time_str: Optional[str] = None,
                            end_time_str: Optional[str] = None
                           ) -> Optional[Dict[str, Any]]:
        """
        Retrieves descriptive statistics for a specified numeric field within the log data.
        This is a facade method that utilizes the BasicAnalyzer. Time strings are converted
        to datetime objects for filtering.

        Args:
            data_field_path (Union[str, List[str]]): The key (string) or path of keys (list of strings)
                                                     to the numeric field within each log entry's 'data'
                                                     dictionary (e.g., "reward" or ["performance", "score"]).
            source (Optional[str]): Filter logs by this source string before analysis.
            event_type (Optional[str]): Filter logs by this event_type string before analysis.
            start_time_str (Optional[str]): ISO format timestamp string (e.g., "2023-10-27T10:30:00.123Z")
                                           to filter logs starting from this time (inclusive).
            end_time_str (Optional[str]): ISO format timestamp string to filter logs up to this
                                         time (inclusive).

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing statistics (keys like "mean",
                                      "median", "min", "max", "count", "stdev", "sum"),
                                      or None if no data is found for the given parameters
                                      or an error occurs (e.g., analyzer not ready, bad time format).
        """
        if not self.analyzer:
            print("API Error: Analyzer not available. Load logs first.")
            return None

        start_dt: Optional[datetime] = None
        end_dt: Optional[datetime] = None
        try:
            if start_time_str:
                start_dt = datetime.strptime(start_time_str, DEFAULT_TIMESTAMP_FORMAT)
            if end_time_str:
                end_dt = datetime.strptime(end_time_str, DEFAULT_TIMESTAMP_FORMAT)
        except ValueError as e:
            print(f"API Error: Invalid timestamp format provided. Use {DEFAULT_TIMESTAMP_FORMAT}. Error: {e}")
            return None

        return self.analyzer.get_descriptive_stats(data_field_path, source, event_type, start_dt, end_dt)

    def get_timeseries_for_field(self,
                                 data_field_path: Union[str, List[str]],
                                 source: Optional[str] = None,
                                 event_type: Optional[str] = None,
                                 start_time_str: Optional[str] = None,
                                 end_time_str: Optional[str] = None
                                ) -> List[Tuple[datetime, Any]]:
        """
        Extracts time-series data (timestamp, value) for a specified field from the logs.
        This is a facade method that utilizes the BasicAnalyzer. Time strings are converted
        to datetime objects for filtering.

        Args:
            data_field_path (Union[str, List[str]]): The key (string) or path of keys (list of strings)
                                                     to the field within the log entry's 'data' dictionary.
            source (Optional[str]): Filter logs by this source string.
            event_type (Optional[str]): Filter logs by this event_type string.
            start_time_str (Optional[str]): ISO format timestamp string for start time filter (inclusive).
            end_time_str (Optional[str]): ISO format timestamp string for end time filter (inclusive).

        Returns:
            List[Tuple[datetime, Any]]: A list of (datetime, value) tuples, sorted chronologically.
                                        Returns an empty list if no data is found for the parameters
                                        or an error occurs (e.g., analyzer not ready, bad time format).
        """
        if not self.analyzer:
            print("API Error: Analyzer not available. Load logs first.")
            return []

        start_dt: Optional[datetime] = None
        end_dt: Optional[datetime] = None
        try:
            if start_time_str:
                start_dt = datetime.strptime(start_time_str, DEFAULT_TIMESTAMP_FORMAT)
            if end_time_str:
                end_dt = datetime.strptime(end_time_str, DEFAULT_TIMESTAMP_FORMAT)
        except ValueError as e:
            print(f"API Error: Invalid timestamp format provided. Use {DEFAULT_TIMESTAMP_FORMAT}. Error: {e}")
            return []

        return self.analyzer.get_time_series(data_field_path, source, event_type, start_dt, end_dt)

    def plot_field_over_time(self,
                             data_field_path: Union[str, List[str]],
                             title: Optional[str] = None,
                             y_label: Optional[str] = None,
                             source: Optional[str] = None,
                             event_type: Optional[str] = None,
                             start_time_str: Optional[str] = None,
                             end_time_str: Optional[str] = None,
                             output_file: Optional[str] = None,
                             show_plot: bool = True) -> None:
        """
        Generates and displays/saves a time-series plot for a specified field from the log data.
        This method combines data extraction (using `get_timeseries_for_field`) and plotting
        (via `TimeseriesPlotter`).

        Args:
            data_field_path (Union[str, List[str]]): Key or path to the field in the 'data' dictionary.
            title (Optional[str]): Title for the plot. If None, a default title is generated
                                   based on `data_field_path`.
            y_label (Optional[str]): Label for the Y-axis. If None, defaults to `data_field_path`.
            source (Optional[str]): Filter logs by this source string before plotting.
            event_type (Optional[str]): Filter logs by this event_type string before plotting.
            start_time_str (Optional[str]): ISO format timestamp string for start time filter.
            end_time_str (Optional[str]): ISO format timestamp string for end time filter.
            output_file (Optional[str]): If provided, the plot will be saved to this file path.
            show_plot (bool): If True (default), the plot will be displayed (e.g., in a GUI window
                              or inline in a notebook). Set to False for non-interactive environments
                              or when only saving the file.
        """
        ts_data = self.get_timeseries_for_field(data_field_path, source, event_type, start_time_str, end_time_str)
        if not ts_data:
            print("API: No time series data found to plot for the given parameters.")
            return

        _title = title or f"Time Series for '{str(data_field_path)}'"
        _y_label = y_label or str(data_field_path)

        self.timeseries_plotter.plot_time_series(ts_data,
                                                 title=_title,
                                                 y_label=_y_label,
                                                 output_file=output_file,
                                                 show_plot=show_plot)

    def display_formatted_dict(self, data_dict: Dict[str, Any], title: str = "Details") -> None:
        """
        Displays a dictionary in a formatted, human-readable textual representation.
        This is a facade for `StateVisualizer.format_dict_as_text`.

        Args:
            data_dict (Dict[str, Any]): The dictionary to be displayed.
            title (str): A title for the displayed output section. Defaults to "Details".
        """
        print(self.state_visualizer.format_dict_as_text(data_dict, title=title))

    def display_goals_from_log_entry(self, goals_log_data: Optional[Dict[str, Any]], title: str = "Agent Goals") -> None:
        """
        Displays agent goal information from a log entry's data payload in a textual format.
        This is a facade for `StateVisualizer.visualize_current_goals`.

        Args:
            goals_log_data (Optional[Dict[str, Any]]): The 'data' field of a log entry,
                                                       expected to contain goal information
                                                       (e.g., "active_goals", "goal_hierarchy").
            title (str): A title for the displayed output. Defaults to "Agent Goals".
        """
        print(self.state_visualizer.visualize_current_goals(goals_log_data, title=title))

    def display_wm_from_log_entry(self, wm_log_data: Optional[Dict[str, Any]], title: str = "Working Memory") -> None:
        """
        Displays agent working memory state from a log entry's data payload in a textual format.
        This is a facade for `StateVisualizer.visualize_working_memory`.

        Args:
            wm_log_data (Optional[Dict[str, Any]]): The 'data' field of a log entry,
                                                    expected to contain working memory information
                                                    (e.g., "active_elements", "capacity_used_percent").
            title (str): A title for the displayed output. Defaults to "Working Memory".
        """
        print(self.state_visualizer.visualize_working_memory(wm_log_data, title=title))

    def get_event_sequencer(self) -> Optional[EventSequencer]:
        """
        Provides access to the EventSequencer instance for the currently loaded logs.

        Returns:
            Optional[EventSequencer]: The EventSequencer instance, or None if no logs are loaded.
        """
        if not self.event_sequencer:
            print("API Warning: Event sequencer not available. Load logs first.")
        return self.event_sequencer

    def find_event_sequences(self,
                             sequence_definition: List[Dict[str, Optional[str]]],
                             max_time_between_steps_seconds: Optional[float] = None,
                             max_intervening_logs: Optional[int] = None,
                             allow_repeats_in_definition: bool = False
                            ) -> List[List[LogEntry]]:
        """
        Facade to find event sequences using EventSequencer.

        Args:
            sequence_definition (List[Dict[str, Optional[str]]]): Defines the sequence pattern.
                Each dict should have 'event_type' and optionally 'source'.
            max_time_between_steps_seconds (Optional[float]): Max time between consecutive steps.
            max_intervening_logs (Optional[int]): Max other logs between consecutive steps.
            allow_repeats_in_definition (bool): Policy for repeated definitions.
                See EventSequencer.extract_event_sequences for details.

        Returns:
            List[List[LogEntry]]: A list of found sequences (each sequence is a list of LogEntry),
                                  or an empty list if none found or an error occurs.
        """
        if not self.event_sequencer:
            print("API Error: Event sequencer not available. Load logs first.")
            return []
        try:
            return self.event_sequencer.extract_event_sequences(
                sequence_definition,
                max_time_between_steps_seconds,
                max_intervening_logs,
                allow_repeats_in_definition
            )
        except Exception as e:
            print(f"API Error: Error during event sequence extraction: {e}")
            return []

    def get_formatted_event_sequences(self,
                                      sequence_definition: List[Dict[str, Optional[str]]],
                                      max_time_between_steps_seconds: Optional[float] = None,
                                      max_intervening_logs: Optional[int] = None,
                                      allow_repeats_in_definition: bool = False
                                     ) -> str:
        """
        Finds event sequences using EventSequencer and returns them in a formatted string.

        Args:
            sequence_definition (List[Dict[str, Optional[str]]]): Defines the sequence pattern.
            max_time_between_steps_seconds (Optional[float]): Max time between steps.
            max_intervening_logs (Optional[int]): Max intervening logs.
            allow_repeats_in_definition (bool): Policy for repeated definitions.

        Returns:
            str: A human-readable string of the found sequences, or an error/empty message.
        """
        if not self.event_sequencer:
            # This specific message is fine here, as it's a direct user feedback from API.
            return "API Error: Event sequencer not available. Load logs first."

        sequences = self.find_event_sequences(
            sequence_definition,
            max_time_between_steps_seconds,
            max_intervening_logs,
            allow_repeats_in_definition
        )
        # The format_sequences_for_display method itself handles "No event sequences found."
        return self.event_sequencer.format_sequences_for_display(sequences)


# Example Usage (demonstrates the API)
# This section is intended for direct script execution demonstration and simple testing.
# It creates a dummy log file, loads it via the API, and showcases some API functionalities.
if __name__ == "__main__":
    # This example assumes you have a 'sample_logs.json' file in the same directory.
    # Create a dummy sample_logs.json for this example to run:
    sample_log_content = [
        {"timestamp": "2024-01-15T10:00:00.000Z", "source": "PiaCML.Memory", "event_type": "Write", "data": {"size_kb": 10, "success": True, "id": "mem001"}},
        {"timestamp": "2024-01-15T10:00:05.000Z", "source": "PiaSE.Agent0", "event_type": "Action", "data": {"action_name": "move", "reward": 0.5, "id": "act001"}},
        {"timestamp": "2024-01-15T10:00:10.000Z", "source": "PiaCML.Memory", "event_type": "Read", "data": {"query_time_ms": 150, "success": True, "id": "mem002"}},
        {"timestamp": "2024-01-15T10:00:15.000Z", "source": "PiaSE.Agent0", "event_type": "Observation", "data": {"state_complexity": 25, "id": "obs001"}},
        {"timestamp": "2024-01-15T10:00:20.000Z", "source": "PiaCML.Memory", "event_type": "Write", "data": {"size_kb": 12, "success": True, "id": "mem003"}},
        {"timestamp": "2024-01-15T10:00:25.000Z", "source": "PiaSE.Agent0", "event_type": "Action", "data": {"action_name": "interact", "reward": 1.0, "id": "act002"}},
        {"timestamp": "2024-01-15T10:00:30.000Z", "source": "PiaCML.Emotion", "event_type": "Update", "data": {"valence": 0.7, "arousal": 0.4, "id": "emo001"}},
        {"timestamp": "2024-01-15T10:00:35.000Z", "source": "PiaSE.Agent0", "event_type": "Action", "data": {"action_name": "move", "reward": -0.1, "id": "act003"}},
        {"timestamp": "2024-01-15T10:00:40.000Z", "source": "PiaCML.Motivation", "event_type": "GoalUpdate", "data": {
            "active_goals": [{"id": "g1", "description": "Explore", "priority": 0.8}], "id": "mot001"}
        },
        {"timestamp": "2024-01-15T10:00:45.000Z", "source": "PiaCML.WorkingMemory", "event_type": "State", "data": {
            "active_elements": [{"id": "e1", "content": "percept_A"}], "focus": "e1", "id": "wm001"}
        }
    ]
    dummy_log_file = "sample_logs.json"
    import json # json import was missing from the original prompt's __main__ block for this file
    with open(dummy_log_file, 'w') as f:
        json.dump(sample_log_content, f, indent=2)

    # --- API DEMO ---
    api = PiaAVTAPI()

    # 1. Load logs
    print(f"Attempting to load logs from: {dummy_log_file}")
    if api.load_logs_from_json(dummy_log_file):
        print(f"Logs loaded successfully. Total entries: {api.get_log_count()}")
        print(f"Active log file path: {api.get_active_log_file()}")

        # 2. Access analyzer directly (optional, for advanced use)
        print("\n--- Direct Analyzer Access Example ---")
        analyzer_instance = api.get_analyzer()
        if analyzer_instance:
            source_counts = analyzer_instance.count_unique_values("source")
            api.display_formatted_dict(dict(source_counts), title="Log Source Counts (via direct analyzer)")

        # 3. Use facade methods for analysis
        print("\n--- Facade Analysis Examples ---")
        # Example: Statistics for 'reward' field from 'Action' events
        reward_stats = api.get_stats_for_field(data_field_path="reward", event_type="Action")
        if reward_stats:
            api.display_formatted_dict(reward_stats, title="Reward Statistics (Action Events)")

        # Example: Statistics for 'size_kb' from 'PiaCML.Memory' source and 'Write' event type
        size_stats = api.get_stats_for_field(
            data_field_path="size_kb",
            source="PiaCML.Memory",
            event_type="Write"
        )
        if size_stats:
            api.display_formatted_dict(size_stats, title="Memory Write Size (KB) Statistics")

        # 4. Use facade for plotting
        print("\n--- Facade Plotting Examples ---")
        # Plotting reward over time
        api.plot_field_over_time(
            data_field_path="reward",
            event_type="Action",
            title="Agent Rewards Over Time (Action Events)",
            y_label="Reward Value",
            output_file="api_reward_plot.png",
            show_plot=False # Set to True for interactive display, False for automated runs
        )
        print(f"Plot 'api_reward_plot.png' requested. Check file if show_plot=False.")

        # Plotting emotion valence over time
        api.plot_field_over_time(
            data_field_path="valence",
            source="PiaCML.Emotion",
            title="Emotion Valence Over Time",
            y_label="Valence (-1 to 1)",
            output_file="api_valence_plot.png",
            show_plot=False
        )
        print(f"Plot 'api_valence_plot.png' requested. Check file if show_plot=False.")

        # 5. Use facade for state visualization (using sample data from the loaded logs)
        print("\n--- Facade State Visualization Examples ---")
        all_loaded_logs = api.get_all_logs()

        # Find a 'GoalUpdate' event to display goals
        goal_event_data = next((log['data'] for log in all_loaded_logs if log['event_type'] == "GoalUpdate"), None)
        if goal_event_data:
            api.display_goals_from_log_entry(goal_event_data, title="Agent Goals from Log")
        else:
            print("No 'GoalUpdate' event found in sample logs for goal display example.")

        # Find a 'PiaCML.WorkingMemory' state to display
        wm_event_data = next((log['data'] for log in all_loaded_logs if log['source'] == "PiaCML.WorkingMemory" and log['event_type'] == "State"), None)
        if wm_event_data:
            api.display_wm_from_log_entry(wm_event_data, title="Working Memory State from Log")
        else:
            print("No 'WorkingMemory State' event found in sample logs for WM display example.")

        # 6. Facade Event Sequence Analysis Example
        print("\n--- Facade Event Sequence Analysis ---")
        # Define a sequence that IS in the sample_log_content
        seq_def_present = [
            {"event_type": "Write", "source": "PiaCML.Memory"}, # Log 0: 10:00:00
            {"event_type": "Action", "source": "PiaSE.Agent0"}  # Log 1: 10:00:05
        ]
        print("Searching for sequence: PiaCML.Memory/Write -> PiaSE.Agent0/Action (0 intervening)")
        formatted_sequences = api.get_formatted_event_sequences(
            seq_def_present,
            max_intervening_logs=0 # Expect mem001->act001 and mem003->act002
        )
        print(formatted_sequences)

        print("\nSearching with time limit (max 3s between steps, 0 intervening):")
        # This should find no sequences, as the gap between Write and Action is 5s.
        formatted_sequences_timed = api.get_formatted_event_sequences(
            seq_def_present,
            max_time_between_steps_seconds=3.0,
            max_intervening_logs=0
        )
        print(formatted_sequences_timed)

    else:
        print(f"ERROR: Failed to load logs from {dummy_log_file}. API demo cannot proceed fully.")

    # Clean up the dummy log file and generated plots
    import os
    # In a real scenario, you might want to inspect the plots. For automated tests, removal is common.
    files_to_remove = [dummy_log_file, "api_reward_plot.png", "api_valence_plot.png"]
    for f_path in files_to_remove:
        if os.path.exists(f_path):
            try:
                os.remove(f_path)
                print(f"Cleaned up temporary file: {f_path}")
            except OSError as e:
                print(f"Error removing file {f_path}: {e}")

    print("\nAPI Demo Complete.")
```
