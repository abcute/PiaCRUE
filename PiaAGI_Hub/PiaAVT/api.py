# PiaAGI_Hub/PiaAVT/api.py

from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime

# Attempt to import from sibling directories core, analyzers, visualizers
# This structure assumes PiaAVT is used as a package or these paths are configured.
try:
    from .core.logging_system import LoggingSystem, LogEntry, DEFAULT_TIMESTAMP_FORMAT, LogValidationError
    from .analyzers.basic_analyzer import BasicAnalyzer
    from .visualizers.timeseries_plotter import TimeseriesPlotter
    from .visualizers.state_visualizer import StateVisualizer
except ImportError:
    # Fallback for environments where the relative import doesn't work (e.g., running script directly)
    # This might happen if PiaAVT is not installed as a package and PYTHONPATH isn't set up.
    # For robust use, PiaAVT should be structured and installed as a proper Python package.
    print("PiaAVT API: Attempting fallback imports. For proper package structure, ensure PiaAVT is installable.")
    from core.logging_system import LoggingSystem, LogEntry, DEFAULT_TIMESTAMP_FORMAT, LogValidationError
    from analyzers.basic_analyzer import BasicAnalyzer
    from visualizers.timeseries_plotter import TimeseriesPlotter
    from visualizers.state_visualizer import StateVisualizer


class PiaAVTAPI:
    """
    Main API Facade for interacting with the PiaAGI Agent Analysis & Visualization Toolkit.
    Provides a simplified interface to load data, perform analyses, and generate visualizations.
    """

    def __init__(self):
        self.logging_system = LoggingSystem()
        self.analyzer: Optional[BasicAnalyzer] = None
        self.timeseries_plotter = TimeseriesPlotter()
        self.state_visualizer = StateVisualizer()
        self._active_log_file: Optional[str] = None

    def load_logs_from_json(self, file_path: str, validate: bool = True) -> bool:
        """
        Loads log data from a specified JSON file.
        Returns True on success, False on failure.
        """
        try:
            self.logging_system.clear_logs() # Clear previous logs
            self.logging_system.load_logs_from_json_file(file_path, validate=validate)
            self.analyzer = BasicAnalyzer(self.logging_system.get_log_data())
            self._active_log_file = file_path
            print(f"API: Successfully loaded and initialized analyzer with logs from {file_path}")
            return True
        except (FileNotFoundError, json.JSONDecodeError, LogValidationError) as e:
            self.analyzer = None # Ensure analyzer is not stale
            self._active_log_file = None
            print(f"API Error: Failed to load logs from {file_path}. {e}")
            return False
        except Exception as e:
            self.analyzer = None
            self._active_log_file = None
            print(f"API Error: An unexpected error occurred loading logs from {file_path}. {e}")
            return False

    def get_log_count(self) -> int:
        """Returns the number of currently loaded log entries."""
        return self.logging_system.get_log_count()

    def get_all_logs(self) -> List[LogEntry]:
        """Returns all loaded log entries."""
        return self.logging_system.get_log_data()

    def get_active_log_file(self) -> Optional[str]:
        """Returns the path of the currently loaded log file, if any."""
        return self._active_log_file

    def get_analyzer(self) -> Optional[BasicAnalyzer]:
        """
        Returns the BasicAnalyzer instance for the currently loaded log data.
        Returns None if no logs are loaded or if loading failed.
        """
        if not self.analyzer:
            print("API Warning: No log data loaded. Please load logs using 'load_logs_from_json' first.")
        return self.analyzer

    # --- Direct Analysis & Visualization Methods (Facades) ---

    def get_stats_for_field(self,
                            data_field_path: Union[str, List[str]],
                            source: Optional[str] = None,
                            event_type: Optional[str] = None,
                            start_time_str: Optional[str] = None, # Expects ISO format string
                            end_time_str: Optional[str] = None    # Expects ISO format string
                           ) -> Optional[Dict[str, Any]]:
        """
        Facade to get descriptive statistics for a field.
        Converts time strings to datetime objects.
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
        Facade to get time series data for a field.
        Converts time strings to datetime objects.
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
        Facade to directly plot a field's time series.
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
        """Facade to display a dictionary nicely using StateVisualizer."""
        print(self.state_visualizer.format_dict_as_text(data_dict, title=title))

    def display_goals_from_log_entry(self, goals_log_data: Optional[Dict[str, Any]], title: str = "Agent Goals") -> None:
        """Facade to display goals using StateVisualizer."""
        print(self.state_visualizer.visualize_current_goals(goals_log_data, title=title))

    def display_wm_from_log_entry(self, wm_log_data: Optional[Dict[str, Any]], title: str = "Working Memory") -> None:
        """Facade to display working memory using StateVisualizer."""
        print(self.state_visualizer.visualize_working_memory(wm_log_data, title=title))


# Example Usage (demonstrates the API)
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
    import json
    with open(dummy_log_file, 'w') as f:
        json.dump(sample_log_content, f, indent=2)

    # --- API DEMO ---
    api = PiaAVTAPI()

    # Load logs
    if api.load_logs_from_json(dummy_log_file):
        print(f"Logs loaded. Count: {api.get_log_count()}")
        print(f"Active log file: {api.get_active_log_file()}")

        # Get analyzer and use it directly (optional)
        analyzer = api.get_analyzer()
        if analyzer:
            source_counts = analyzer.count_unique_values("source")
            print(f"\nSource counts via direct analyzer: {source_counts}")

        # Use facade methods for analysis
        print("\n--- Facade Analysis ---")
        reward_stats = api.get_stats_for_field(data_field_path="reward", event_type="Action")
        if reward_stats:
            api.display_formatted_dict(reward_stats, title="Reward Statistics (for Action events)")

        size_stats = api.get_stats_for_field(data_field_path="size_kb", source="PiaCML.Memory", event_type="Write")
        if size_stats:
            api.display_formatted_dict(size_stats, title="Memory Write Size Statistics")

        # Use facade for plotting
        print("\n--- Facade Plotting ---")
        api.plot_field_over_time(
            data_field_path="reward",
            event_type="Action",
            title="Agent Rewards Over Time",
            y_label="Reward Value",
            output_file="api_reward_plot.png", # Save the plot
            show_plot=True # Set to False for non-GUI environments
        )
        print("Plotting 'api_reward_plot.png' requested.")

        api.plot_field_over_time(
            data_field_path="valence",
            source="PiaCML.Emotion",
            title="Emotion Valence Over Time",
            y_label="Valence",
            output_file="api_valence_plot.png",
            show_plot=True
        )
        print("Plotting 'api_valence_plot.png' requested.")

        # Use facade for state visualization (using sample data from logs)
        all_logs = api.get_all_logs()
        goal_log_data = next((log['data'] for log in all_logs if log['event_type'] == "GoalUpdate"), None)
        if goal_log_data:
            print("\n--- Facade State Visualization (Goals) ---")
            api.display_goals_from_log_entry(goal_log_data)

        wm_log_data = next((log['data'] for log in all_logs if log['source'] == "PiaCML.WorkingMemory"), None)
        if wm_log_data:
            print("\n--- Facade State Visualization (Working Memory) ---")
            api.display_wm_from_log_entry(wm_log_data)

    else:
        print("Failed to load logs, API demo cannot proceed fully.")

    # Clean up dummy file
    import os
    if os.path.exists(dummy_log_file):
        os.remove(dummy_log_file)
    # You might want to keep the image files for inspection
    # if os.path.exists("api_reward_plot.png"): os.remove("api_reward_plot.png")
    # if os.path.exists("api_valence_plot.png"): os.remove("api_valence_plot.png")
    print("\nAPI Demo Complete.")

```
