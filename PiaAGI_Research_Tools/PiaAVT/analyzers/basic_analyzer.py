# PiaAGI_Hub/PiaAVT/analyzers/basic_analyzer.py
"""
Provides fundamental analysis tools for log data within the PiaAVT toolkit.

This module defines the `BasicAnalyzer` class, which offers methods to filter,
summarize, and extract insights from lists of log entries. It supports common
operations such as calculating descriptive statistics, generating time series,
and counting unique values for specified fields in the log data.

The definitions for `LogEntry` and `DEFAULT_TIMESTAMP_FORMAT` are assumed to be
consistent with those in `core.logging_system`. For standalone use or testing,
they are redefined here if not directly importable.
"""
from typing import List, Dict, Any, Optional, Union, Tuple
from collections import Counter
import statistics
from datetime import datetime

# Assuming LogEntry is defined similarly as in core.logging_system
# If core.logging_system.LogEntry is accessible, import it, otherwise redefine for clarity
# from PiaAGI_Hub.PiaAVT.core.logging_system import LogEntry, DEFAULT_TIMESTAMP_FORMAT
# For now, let's redefine for modularity in this step:
LogEntry = Dict[str, Any] # Should match the definition in core.logging_system
DEFAULT_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ" # Should match the definition in core.logging_system


class BasicAnalyzer:
    """
    Provides basic analysis capabilities for PiaAVT log data.

    This analyzer takes a list of log entries (assumed to be dictionaries)
    and offers methods to filter them, calculate descriptive statistics on
    numeric fields, extract time series data, and count unique values.
    It handles string-based timestamps and can access nested data within
    the 'data' field of log entries.

    Attributes:
        log_data (List[LogEntry]): The list of log entries this analyzer instance operates on.
    """

    def __init__(self, log_data: List[LogEntry]):
        """
        Initializes the BasicAnalyzer with a list of log entries.

        Args:
            log_data (List[LogEntry]): A list of dictionaries, where each dictionary
                                     represents a log entry.

        Raises:
            ValueError: If `log_data` contains items that are not dictionaries.
        """
        if not all(isinstance(entry, dict) for entry in log_data):
            raise ValueError("All items in log_data must be dictionaries (LogEntry).")
        self.log_data = log_data

    def filter_logs(self,
                    source: Optional[str] = None,
                    event_type: Optional[str] = None,
                    start_time: Optional[datetime] = None,
                    end_time: Optional[datetime] = None) -> List[LogEntry]:
        """
        Filters log entries based on source, event_type, and/or a time range.

        Log entries are filtered sequentially by the provided criteria.
        Timestamp filtering requires log entries to have a 'timestamp' field
        containing a string parsable by `DEFAULT_TIMESTAMP_FORMAT`.

        Args:
            source (Optional[str]): If provided, only logs with a matching 'source'
                                    field are returned.
            event_type (Optional[str]): If provided, only logs with a matching
                                        'event_type' field are returned.
            start_time (Optional[datetime]): If provided, only logs with a timestamp
                                             greater than or equal to `start_time`
                                             are returned.
            end_time (Optional[datetime]): If provided, only logs with a timestamp
                                           less than or equal to `end_time`
                                           are returned.

        Returns:
            List[LogEntry]: A new list containing only the log entries that match
                            all specified filter criteria.
        """
        filtered = self.log_data

        if source:
            filtered = [entry for entry in filtered if entry.get("source") == source]
        if event_type:
            filtered = [entry for entry in filtered if entry.get("event_type") == event_type]

        if start_time or end_time:
            temp_filtered = []
            for entry in filtered:
                timestamp_str = entry.get("timestamp")
                if not timestamp_str:
                    continue
                try:
                    entry_ts = datetime.strptime(timestamp_str, DEFAULT_TIMESTAMP_FORMAT)
                    if start_time and entry_ts < start_time:
                        continue
                    if end_time and entry_ts > end_time:
                        continue
                    temp_filtered.append(entry)
                except ValueError:
                    # Skip entries with unparseable timestamps if time filtering is active
                    continue
            filtered = temp_filtered

        return filtered

    def get_descriptive_stats(self,
                              data_field_path: Union[str, List[str]],
                              source: Optional[str] = None,
                              event_type: Optional[str] = None,
                              start_time: Optional[datetime] = None,
                              end_time: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
        """
        Calculates descriptive statistics for a numeric data field from filtered log entries.

        The target numeric field is specified by `data_field_path`, which can be a single
        key (string) or a path of keys (list of strings) to access nested values within
        the 'data' dictionary of each log entry. Only entries where this path leads to
        a numeric value (int or float) are included in the statistics.

        Args:
            data_field_path (Union[str, List[str]]): The key or list of keys defining the
                                                     path to the numeric field within the
                                                     'data' dictionary of log entries.
                                                     E.g., "reward" or ["performance", "score"].
            source (Optional[str]): Filter logs by source before calculating stats.
            event_type (Optional[str]): Filter logs by event_type before calculating stats.
            start_time (Optional[datetime]): Filter logs by start_time before calculating stats.
            end_time (Optional[datetime]): Filter logs by end_time before calculating stats.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the calculated statistics
                                      (keys: "count", "mean", "median", "min", "max",
                                      "stdev", "sum"). Returns `None` if no numeric
                                      data is found for the specified field and filters.
                                      'stdev' is 0.0 if count < 2.
        """
        logs_to_analyze = self.filter_logs(source, event_type, start_time, end_time)

        values: List[Union[int, float]] = []
        for entry in logs_to_analyze:
            data_dict = entry.get("data", {})
            if not isinstance(data_dict, dict):
                continue

            current_val = data_dict
            path_list = [data_field_path] if isinstance(data_field_path, str) else data_field_path

            try:
                for key in path_list:
                    current_val = current_val[key]
                if isinstance(current_val, (int, float)):
                    values.append(current_val)
            except (KeyError, TypeError):
                # Field not found in this entry's data or not a number, skip
                continue

        if not values:
            return None

        return {
            "count": len(values),
            "mean": statistics.mean(values) if values else None,
            "median": statistics.median(values) if values else None,
            "min": min(values) if values else None,
            "max": max(values) if values else None,
            "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
            "sum": sum(values) if values else None,
        }

    def get_time_series(self,
                        data_field_path: Union[str, List[str]],
                        source: Optional[str] = None,
                        event_type: Optional[str] = None,
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None) -> List[Tuple[datetime, Any]]:
        """
        Extracts time-series data (timestamp, value) for a specified field from filtered logs.

        The `data_field_path` specifies the key (string) or path of keys (list of strings)
        to access the desired value within the 'data' dictionary of each log entry.
        The timestamp from the log entry's 'timestamp' field is parsed into a datetime object.

        Args:
            data_field_path (Union[str, List[str]]): The key or path to the field within
                                                     the 'data' dictionary.
            source (Optional[str]): Filter logs by source before extracting data.
            event_type (Optional[str]): Filter logs by event_type before extracting data.
            start_time (Optional[datetime]): Filter logs by start_time.
            end_time (Optional[datetime]): Filter logs by end_time.

        Returns:
            List[Tuple[datetime, Any]]: A list of (datetime, value) tuples, sorted
                                        chronologically by timestamp. Returns an empty
                                        list if no data is found or if timestamps
                                        are unparseable.
        """
        logs_to_analyze = self.filter_logs(source, event_type, start_time, end_time)

        time_series_data: List[Tuple[datetime, Any]] = []
        for entry in logs_to_analyze:
            timestamp_str = entry.get("timestamp")
            data_dict = entry.get("data", {})
            if not timestamp_str or not isinstance(data_dict, dict):
                continue

            current_val = data_dict
            path_list = [data_field_path] if isinstance(data_field_path, str) else data_field_path

            try:
                for key in path_list:
                    current_val = current_val[key]

                entry_ts = datetime.strptime(timestamp_str, DEFAULT_TIMESTAMP_FORMAT)
                time_series_data.append((entry_ts, current_val))
            except (KeyError, TypeError, ValueError):
                # Field not found, not the expected type, or timestamp parse error
                continue

        # Sort by timestamp
        time_series_data.sort(key=lambda x: x[0])
        return time_series_data

    def count_unique_values(self,
                            field_name: str, # e.g., "source", "event_type", or a key within "data"
                            source: Optional[str] = None,
                            event_type: Optional[str] = None,
                            start_time: Optional[datetime] = None,
                            end_time: Optional[datetime] = None,
                            is_data_field: bool = False,
                            data_field_path: Optional[Union[str, List[str]]] = None
                           ) -> Counter:
        """
        Counts occurrences of unique values for a specified field in filtered log entries.

        The method can count values from a top-level field in the log entry (e.g., "source",
        "event_type") or from a field within the 'data' dictionary. If the target field's
        value is a list or dictionary itself, it's converted to its string representation
        to ensure hashability for counting.

        Args:
            field_name (str): The name of the top-level field to count values from if
                              `is_data_field` is False. If `is_data_field` is True,
                              this argument is effectively a placeholder, and
                              `data_field_path` is used instead.
            source (Optional[str]): Filter logs by source before counting.
            event_type (Optional[str]): Filter logs by event_type before counting.
            start_time (Optional[datetime]): Filter logs by start_time.
            end_time (Optional[datetime]): Filter logs by end_time.
            is_data_field (bool): If True, `data_field_path` is used to find the field
                                  within the 'data' dictionary. Defaults to False.
            data_field_path (Optional[Union[str, List[str]]]): The key or path to the
                                                               field within the 'data'
                                                               dictionary. Required if
                                                               `is_data_field` is True.

        Returns:
            collections.Counter: A Counter object mapping unique values to their frequencies.

        Raises:
            ValueError: If `is_data_field` is True but `data_field_path` is not provided.
        """
        logs_to_analyze = self.filter_logs(source, event_type, start_time, end_time)

        values_to_count = []
        for entry in logs_to_analyze:
            if is_data_field:
                if not data_field_path:
                    raise ValueError("data_field_path must be provided if is_data_field is True.")

                data_dict = entry.get("data", {})
                if not isinstance(data_dict, dict):
                    continue

                current_val = data_dict
                path_list = [data_field_path] if isinstance(data_field_path, str) else data_field_path
                try:
                    for key in path_list:
                        current_val = current_val[key]
                    # Ensure value is hashable for Counter
                    if isinstance(current_val, (list, dict)):
                        current_val = str(current_val)
                    values_to_count.append(current_val)
                except (KeyError, TypeError):
                    continue # Field not found or not hashable
            else:
                if field_name in entry:
                    val = entry[field_name]
                    if isinstance(val, (list, dict)):
                        val = str(val) # Ensure hashable for Counter
                    values_to_count.append(val)

        return Counter(values_to_count)

# Example Usage (primarily for demonstration or direct script testing)
# This section will typically not be run when PiaAVT is used as a library.
if __name__ == "__main__":
    sample_logs: List[LogEntry] = [ # type: ignore
        {"timestamp": "2024-01-15T10:00:00.000Z", "source": "PiaCML.Memory", "event_type": "Write", "data": {"size_kb": 10, "success": True}},
        {"timestamp": "2024-01-15T10:00:05.000Z", "source": "PiaSE.Agent0", "event_type": "Action", "data": {"action_name": "move", "reward": 0.5}},
        {"timestamp": "2024-01-15T10:00:10.000Z", "source": "PiaCML.Memory", "event_type": "Read", "data": {"query_time_ms": 150, "success": True}},
        {"timestamp": "2024-01-15T10:00:15.000Z", "source": "PiaSE.Agent0", "event_type": "Observation", "data": {"state_complexity": 25}},
        {"timestamp": "2024-01-15T10:00:20.000Z", "source": "PiaCML.Memory", "event_type": "Write", "data": {"size_kb": 12, "success": True}},
        {"timestamp": "2024-01-15T10:00:25.000Z", "source": "PiaSE.Agent0", "event_type": "Action", "data": {"action_name": "interact", "reward": 1.0}},
        {"timestamp": "2024-01-15T10:00:30.000Z", "source": "PiaCML.Emotion", "event_type": "Update", "data": {"valence": 0.7, "arousal": 0.4}},
        {"timestamp": "2024-01-15T10:00:35.000Z", "source": "PiaSE.Agent0", "event_type": "Action", "data": {"action_name": "move", "reward": -0.1}},
    ]

    analyzer = BasicAnalyzer(sample_logs)

    print("--- Value Counts ---")
    source_counts = analyzer.count_unique_values("source")
    print(f"Source counts: {source_counts}")

    event_type_counts = analyzer.count_unique_values("event_type", source="PiaCML.Memory")
    print(f"Event type counts for 'PiaCML.Memory': {event_type_counts}")

    action_name_counts = analyzer.count_unique_values(
        "action_name",
        event_type="Action",
        is_data_field=True,
        data_field_path="action_name"
    )
    print(f"Action name counts for 'Action' events: {action_name_counts}")


    print("\n--- Descriptive Stats ---")
    reward_stats = analyzer.get_descriptive_stats(data_field_path="reward", event_type="Action")
    if reward_stats:
        print(f"Reward stats for 'Action' events: {reward_stats}")
    else:
        print("No reward data found for 'Action' events.")

    memory_write_size_stats = analyzer.get_descriptive_stats(
        data_field_path="size_kb",
        source="PiaCML.Memory",
        event_type="Write"
    )
    if memory_write_size_stats:
        print(f"Memory write size (KB) stats: {memory_write_size_stats}")
    else:
        print("No memory write size data found.")

    print("\n--- Time Series ---")
    reward_series = analyzer.get_time_series(data_field_path="reward", event_type="Action")
    print("Reward time series for 'Action' events:")
    for ts, val in reward_series:
        print(f"  {ts.strftime('%H:%M:%S')} - {val}")

    valence_series = analyzer.get_time_series(
        data_field_path="valence",
        source="PiaCML.Emotion",
        event_type="Update"
    )
    print("\nValence time series for 'PiaCML.Emotion' 'Update' events:")
    for ts, val in valence_series:
        print(f"  {ts.strftime('%H:%M:%S')} - {val}")

    # Test filtering by time
    start_dt = datetime.strptime("2024-01-15T10:00:10.000Z", DEFAULT_TIMESTAMP_FORMAT)
    end_dt = datetime.strptime("2024-01-15T10:00:25.000Z", DEFAULT_TIMESTAMP_FORMAT)

    print(f"\n--- Filtered Time Series (between {start_dt} and {end_dt}) ---")
    filtered_reward_series = analyzer.get_time_series(
        data_field_path="reward",
        event_type="Action",
        start_time=start_dt,
        end_time=end_dt
    )
    print("Filtered Reward time series for 'Action' events:")
    for ts, val in filtered_reward_series:
        print(f"  {ts.strftime('%H:%M:%S')} - {val}")

    print(f"\n--- Filtered Value Counts (between {start_dt} and {end_dt}) ---")
    filtered_source_counts = analyzer.count_unique_values("source", start_time=start_dt, end_time=end_dt)
    print(f"Filtered Source counts: {filtered_source_counts}")

```
