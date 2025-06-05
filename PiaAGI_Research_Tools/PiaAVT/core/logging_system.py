# PiaAGI_Hub/PiaAVT/core/logging_system.py
"""
Core module for logging and data ingestion within the PiaAVT toolkit.

This module defines the standard structure for log entries, provides a system
for ingesting logs (currently from JSON files), validating their format and content,
and storing them in memory. It forms the foundation for data analysis and
visualization tasks performed by other components of the PiaAVT.

Key Components:
    LogEntry (TypeAlias): Defines the expected dictionary structure for a single log entry.
    DEFAULT_TIMESTAMP_FORMAT (str): The standard ISO 8601-like format for timestamps.
    LogValidationError (Exception): Custom exception raised for issues during log validation.
    LoggingSystem (class): Manages log ingestion, validation, storage, and access.
"""
import json
from typing import List, Dict, Any, Optional # Retain Optional for consistency if used elsewhere, though not in current file directly
from datetime import datetime

# Define a standard log entry structure (can be expanded)
# For now, we'll use a dictionary, but Pydantic models are a good future enhancement for validation.
LogEntry = Dict[str, Any]
"""
Type alias for a log entry. Expected to be a dictionary with at least
the fields defined in `LoggingSystem.required_fields`.
Example:
    {
        "timestamp": "2023-10-27T10:30:00.123Z",
        "source": "module.submodule",
        "event_type": "SpecificEvent",
        "data": {"key": "value", "metric": 123}
    }
"""

# --- Configuration ---
# Consider moving to a dedicated config file or class later
DEFAULT_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
"""
Default string format for timestamps used in log entries and parsing.
Follows a common ISO 8601 representation (YYYY-MM-DDTHH:MM:SS.sssZ).
"""

class LogValidationError(ValueError):
    """
    Custom exception raised when a log entry fails validation.
    This can occur due to missing required fields, incorrect data types,
    or invalid formats (e.g., for timestamps).
    Inherits from ValueError.
    """
    pass

class LoggingSystem:
    """
    Manages the ingestion, validation, and storage of agent log data.

    This class provides the core functionality for handling log entries within PiaAVT.
    It defines a standard structure for logs, validates incoming entries against this
    structure, and stores them in an in-memory list. Logs can be added individually,
    in batches, or loaded from JSON files.

    Attributes:
        log_data (List[LogEntry]): An in-memory list storing all validated log entries.
        required_fields (List[str]): A list of field names that must be present in
                                     every log entry.
    """

    def __init__(self):
        """
        Initializes the LoggingSystem with an empty log store and updated required fields.
        """
        self.log_data: List[LogEntry] = []
        self.required_fields: List[str] = [
            "timestamp", "simulation_run_id", "experiment_id", "agent_id",
            "source_component_id", "log_level", "event_type", "event_data"
        ]
        # Optional: Define expected data types for fields for more robust validation
        # self.field_types = {
        #     "timestamp": str,
        #     "simulation_run_id": str,
        #     "experiment_id": str,
        #     "agent_id": str,
        #     "source_component_id": str,
        #     "log_level": str,
        #     "event_type": str,
        #     "event_data": dict
        # }

    def _validate_log_entry(self, entry: Dict[str, Any]) -> LogEntry:
        """
        Validates a single log entry against required fields and basic format rules.

        This internal method checks for:
        - Presence of all fields listed in `self.required_fields`.
        - Correct type and format for the 'timestamp' field.
        - Non-empty strings for 'simulation_run_id', 'experiment_id', 'agent_id',
          'source_component_id', 'log_level', and 'event_type' fields.
        - 'event_data' field must be a dictionary.

        Args:
            entry (Dict[str, Any]): The log entry dictionary to validate.

        Returns:
            LogEntry: The validated log entry (unchanged if validation passes).

        Raises:
            LogValidationError: If any validation check fails.
        """
        # Check for required fields
        for field in self.required_fields:
            if field not in entry:
                raise LogValidationError(f"Missing required field: '{field}' in log entry: {entry}")

        # Validate timestamp format
        timestamp_str = entry.get("timestamp")
        if not isinstance(timestamp_str, str):
            raise LogValidationError(f"Timestamp must be a string. Found: {type(timestamp_str)} in entry: {entry}")
        try:
            datetime.strptime(timestamp_str, DEFAULT_TIMESTAMP_FORMAT)
        except ValueError:
            raise LogValidationError(
                f"Invalid timestamp format for '{timestamp_str}'. "
                f"Expected format: {DEFAULT_TIMESTAMP_FORMAT} (e.g., 2023-10-27T10:30:00.123Z)"
            )

        # Validate new string fields
        string_fields_to_check = [
            "simulation_run_id", "experiment_id", "agent_id",
            "source_component_id", "log_level", "event_type"
        ]
        for field_name in string_fields_to_check:
            field_value = entry.get(field_name)
            if not isinstance(field_value, str) or not field_value.strip():
                raise LogValidationError(
                    f"Log field '{field_name}' must be a non-empty string. Found: '{field_value}' in entry: {entry}"
                )

        # Validate event_data field (should be a dictionary)
        event_data_dict = entry.get("event_data")
        if not isinstance(event_data_dict, dict):
            raise LogValidationError(f"Log 'event_data' field must be a dictionary. Found: {type(event_data_dict)} in entry: {entry}")

        # Add more specific field type checks here if self.field_types is defined
        # for field, expected_type in self.field_types.items():
        #     if field in entry and not isinstance(entry[field], expected_type):
        #         raise LogValidationError(f"Field '{field}' has incorrect type. Expected {expected_type}, got {type(entry[field])}")

        return entry

    def add_log_entry(self, entry: LogEntry, validate: bool = True) -> None:
        """
        Adds a single log entry to the internal storage.

        By default, the entry is validated before being added. If validation is
        disabled, the entry is added as-is (use with caution).

        Args:
            entry (LogEntry): The log entry to add.
            validate (bool): If True (default), the entry is validated.
                             If False, validation is skipped.

        Raises:
            LogValidationError: If `validate` is True and the entry fails validation.
        """
        if validate:
            validated_entry = self._validate_log_entry(entry)
            self.log_data.append(validated_entry)
        else:
            self.log_data.append(entry) # Use with caution, assumes data is pre-validated

    def add_log_entries(self, entries: List[LogEntry], validate: bool = True) -> None:
        """
        Adds multiple log entries to the internal storage.

        If `validate` is True (default), all entries in the batch are validated first.
        If any entry fails validation, a `LogValidationError` is raised, and no entries
        from that batch are added (all-or-nothing behavior for validated additions).
        If `validate` is False, all entries are added as-is.

        Args:
            entries (List[LogEntry]): A list of log entries to add.
            validate (bool): If True (default), entries are validated.
                             If False, validation is skipped.

        Raises:
            LogValidationError: If `validate` is True and any entry in the batch
                                fails validation.
        """
        validated_batch: List[LogEntry] = []
        if validate:
            for i, entry in enumerate(entries):
                try:
                    validated_batch.append(self._validate_log_entry(entry))
                except LogValidationError as e:
                    raise LogValidationError(f"Validation failed for entry at index {i}: {e}")
            self.log_data.extend(validated_batch)
        else:
            self.log_data.extend(entries) # Use with caution

    def load_logs_from_jsonl_file(self, file_path: str, validate: bool = True) -> None:
        """
        Loads log entries from a JSONL (JSON Lines) file.

        Each line in the JSONL file is expected to be a valid JSON object
        representing a single log entry. These entries are then added
        via `add_log_entries`, respecting the `validate` flag.
        If a line cannot be parsed as JSON, an error is printed, and that line is skipped.

        Args:
            file_path (str): The path to the JSONL file containing log entries.
            validate (bool): If True (default), entries loaded from the file are validated.
                             If False, validation is skipped.

        Raises:
            FileNotFoundError: If the specified `file_path` does not exist.
            LogValidationError: If `validate` is True and any successfully parsed
                                log entry from the file fails validation.
            Exception: Catches other potential errors during file operations or processing.
        """
        loaded_entries: List[LogEntry] = []
        try:
            with open(file_path, 'r') as f:
                for i, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue  # Skip empty lines
                    try:
                        entry = json.loads(line)
                        loaded_entries.append(entry)
                    except json.JSONDecodeError as e_json:
                        print(f"Error decoding JSON from line {i+1} in {file_path}: {e_json}\nProblematic line: '{line}'")
                        # Optionally, decide if you want to stop processing or continue
                        continue

            if not loaded_entries:
                print(f"No valid log entries found or loaded from {file_path}.")
                return

            self.add_log_entries(loaded_entries, validate=validate)
            print(f"Successfully processed {len(loaded_entries)} potential log entries from JSONL file {file_path}.")
            # Note: add_log_entries will print its own success/error or raise LogValidationError

        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            raise
        except LogValidationError as e_val: # Catch validation errors from add_log_entries
            print(f"Error processing log entries from JSONL file {file_path}: {e_val}")
            raise # Re-raise to signal failure at a higher level if needed
        except Exception as e: # Catch other unexpected errors
            print(f"An unexpected error occurred while loading logs from JSONL file {file_path}: {e}")
            raise

    def get_log_data(self) -> List[LogEntry]:
        """
        Returns all log entries currently stored in the LoggingSystem.

        Returns:
            List[LogEntry]: A list containing all stored log entries.
                           Returns an empty list if no logs are stored.
        """
        return self.log_data

    def clear_logs(self) -> None:
        """
        Clears all log entries from the internal storage.
        Resets `log_data` to an empty list.
        """
        self.log_data = []

    def get_log_count(self) -> int:
        """
        Returns the total number of log entries currently stored.

        Returns:
            int: The number of log entries.
        """
        return len(self.log_data)

# Example Usage (primarily for demonstration or direct script testing)
# This section will typically not be run when PiaAVT is used as a library.
if __name__ == "__main__":
    logging_system = LoggingSystem()

    # Example valid log entries
    log1 = {
        "timestamp": "2024-01-15T10:00:00.000Z",
        "simulation_run_id": "sim_run_001",
        "experiment_id": "exp_LTM_retrieval_A",
        "agent_id": "agent_alpha",
        "source_component_id": "PiaCML.Memory.LTM",
        "log_level": "INFO",
        "event_type": "MemoryRetrieval",
        "event_data": {"query": "concept:AGI", "status": "success", "retrieved_items": 3}
    }
    log2 = {
        "timestamp": "2024-01-15T10:00:05.123Z",
        "simulation_run_id": "sim_run_001",
        "experiment_id": "exp_LTM_retrieval_A",
        "agent_id": "agent_alpha",
        "source_component_id": "PiaSE.Environment",
        "log_level": "DEBUG",
        "event_type": "AgentAction",
        "event_data": {"agent_id_ref": "agent_alpha", "action": "move_forward", "outcome": "success"}
    }

    # Example invalid log entry (missing 'simulation_run_id' field)
    invalid_log_missing_field = {
        "timestamp": "2024-01-15T10:00:10.000Z",
        "experiment_id": "exp_motivation_B",
        "agent_id": "agent_beta",
        "source_component_id": "PiaCML.Motivation",
        "log_level": "WARN",
        "event_type": "GoalUpdated",
        "event_data": {"goal_id": "g001", "status": "achieved"}
    }

    # Example invalid log entry (incorrect timestamp format)
    invalid_log_timestamp_format = {
        "timestamp": "15-01-2024 10:00:00", # Incorrect format
        "simulation_run_id": "sim_run_002",
        "experiment_id": "exp_emotion_C",
        "agent_id": "agent_gamma",
        "source_component_id": "PiaCML.Emotion",
        "log_level": "ERROR",
        "event_type": "StateChange",
        "event_data": {"emotion": "joy", "intensity": 0.7}
    }

    try:
        logging_system.add_log_entry(log1)
        logging_system.add_log_entry(log2)
        print(f"Added {logging_system.get_log_count()} logs successfully.")
    except LogValidationError as e:
        print(f"Error adding log: {e}")

    try:
        print("\nAttempting to add invalid log (missing field 'simulation_run_id')...")
        logging_system.add_log_entry(invalid_log_missing_field)
    except LogValidationError as e:
        print(f"Caught expected error: {e}")

    try:
        print("\nAttempting to add invalid log (bad timestamp)...")
        logging_system.add_log_entry(invalid_log_timestamp_format)
    except LogValidationError as e:
        print(f"Caught expected error: {e}")

    # Example of loading from a file (requires a test_logs.jsonl file)
    # Create a dummy JSONL file for testing
    dummy_logs_for_file = [log1, log2, invalid_log_missing_field] # Include one invalid to test line skipping
    dummy_file_path = "test_logs.jsonl"
    with open(dummy_file_path, 'w') as f_dummy:
        for log_entry in dummy_logs_for_file:
            f_dummy.write(json.dumps(log_entry) + '\n')

    print(f"\nAttempting to load logs from {dummy_file_path}...")
    # Clear existing logs to test file loading in isolation
    logging_system.clear_logs()
    print(f"Logs cleared. Current count: {logging_system.get_log_count()}")
    try:
        logging_system.load_logs_from_jsonl_file(dummy_file_path)
        # The load method itself prints success/failure per line for JSON errors,
        # and add_log_entries (called by load_logs_from_jsonl_file) prints validation errors.
        print(f"Total logs after loading from file: {logging_system.get_log_count()}")
    except Exception as e: # Catch other exceptions like FileNotFoundError or validation errors re-raised
        print(f"Error loading from file: {e}")

    # Clean up dummy file
    import os
    os.remove(dummy_file_path)

    print("\nFinal log data:")
    for entry in logging_system.get_log_data():
        print(entry)
