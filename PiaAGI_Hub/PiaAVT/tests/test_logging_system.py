# PiaAGI_Hub/PiaAVT/tests/test_logging_system.py

import unittest
import json
import os
from datetime import datetime

# Adjust import path based on how tests might be run
# This assumes tests are run from the PiaAGI_Hub/PiaAVT directory or project root with PiaAVT in PYTHONPATH
try:
    from core.logging_system import LoggingSystem, LogValidationError, DEFAULT_TIMESTAMP_FORMAT, LogEntry
except ImportError:
    # Fallback for running tests where 'core' is not directly in path, e.g. from project root
    # You might need to configure PYTHONPATH or use a test runner that handles this
    import sys
    # Assuming the tests directory is PiaAGI_Hub/PiaAVT/tests
    # Go up two levels to PiaAGI_Hub and add PiaAVT to path
    current_dir = os.path.dirname(os.path.abspath(__file__)) # .../PiaAVT/tests
    pia_avt_dir = os.path.dirname(current_dir) # .../PiaAVT
    # We need PiaAGI_Hub on the path to import PiaAVT.core... if core is not a top-level package
    # Or, more simply, ensure PiaAVT itself is in PYTHONPATH
    sys.path.insert(0, pia_avt_dir) # Add .../PiaAVT to path
    from core.logging_system import LoggingSystem, LogValidationError, DEFAULT_TIMESTAMP_FORMAT, LogEntry


class TestLoggingSystem(unittest.TestCase):

    def setUp(self):
        """Set up for each test method."""
        self.logging_system = LoggingSystem()
        self.valid_log_entry_1: LogEntry = {
            "timestamp": datetime.utcnow().strftime(DEFAULT_TIMESTAMP_FORMAT),
            "source": "TestSystem1",
            "event_type": "TestEvent1",
            "data": {"key1": "value1", "key2": 123}
        }
        self.valid_log_entry_2: LogEntry = {
            "timestamp": (datetime.utcnow()).strftime(DEFAULT_TIMESTAMP_FORMAT),
            "source": "TestSystem2",
            "event_type": "TestEvent2",
            "data": {"info": "another test", "value": 45.6}
        }
        self.test_log_file = "temp_test_logs.json"

    def tearDown(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_log_file):
            os.remove(self.test_log_file)

    def test_add_single_valid_log_entry(self):
        self.logging_system.add_log_entry(self.valid_log_entry_1)
        self.assertEqual(self.logging_system.get_log_count(), 1)
        self.assertEqual(self.logging_system.get_log_data()[0], self.valid_log_entry_1)

    def test_add_multiple_valid_log_entries(self):
        entries = [self.valid_log_entry_1, self.valid_log_entry_2]
        self.logging_system.add_log_entries(entries)
        self.assertEqual(self.logging_system.get_log_count(), 2)
        self.assertEqual(self.logging_system.get_log_data(), entries)

    def test_validate_log_entry_missing_field(self):
        invalid_entry = self.valid_log_entry_1.copy()
        del invalid_entry["source"]
        with self.assertRaisesRegex(LogValidationError, "Missing required field: 'source'"):
            self.logging_system.add_log_entry(invalid_entry)

    def test_validate_log_entry_invalid_timestamp_format(self):
        invalid_entry = self.valid_log_entry_1.copy()
        invalid_entry["timestamp"] = "2024/01/01 10:00:00" # Incorrect format
        with self.assertRaisesRegex(LogValidationError, "Invalid timestamp format"):
            self.logging_system.add_log_entry(invalid_entry)

    def test_validate_log_entry_invalid_timestamp_type(self):
        invalid_entry = self.valid_log_entry_1.copy()
        invalid_entry["timestamp"] = 1234567890 # Incorrect type
        with self.assertRaisesRegex(LogValidationError, "Timestamp must be a string"):
            self.logging_system.add_log_entry(invalid_entry)

    def test_validate_log_entry_invalid_source_type(self):
        invalid_entry = self.valid_log_entry_1.copy()
        invalid_entry["source"] = "" # Empty string
        with self.assertRaisesRegex(LogValidationError, "Log source must be a non-empty string"):
            self.logging_system.add_log_entry(invalid_entry)

    def test_validate_log_entry_invalid_event_type(self):
        invalid_entry = self.valid_log_entry_1.copy()
        invalid_entry["event_type"] = "" # Empty string
        with self.assertRaisesRegex(LogValidationError, "Log event_type must be a non-empty string"):
            self.logging_system.add_log_entry(invalid_entry)

    def test_validate_log_entry_invalid_data_type(self):
        invalid_entry = self.valid_log_entry_1.copy()
        invalid_entry["data"] = "not a dict" # Incorrect type
        with self.assertRaisesRegex(LogValidationError, "Log 'data' field must be a dictionary"):
            self.logging_system.add_log_entry(invalid_entry)

    def test_add_log_entries_validation_failure_all_or_nothing(self):
        invalid_entry = self.valid_log_entry_1.copy()
        del invalid_entry["timestamp"]
        entries = [self.valid_log_entry_2, invalid_entry] # Second one is invalid

        with self.assertRaises(LogValidationError):
            self.logging_system.add_log_entries(entries)
        self.assertEqual(self.logging_system.get_log_count(), 0, "No entries should be added if one fails validation")

    def test_load_logs_from_json_file_success(self):
        valid_logs = [self.valid_log_entry_1, self.valid_log_entry_2]
        with open(self.test_log_file, 'w') as f:
            json.dump(valid_logs, f)

        self.logging_system.load_logs_from_json_file(self.test_log_file)
        self.assertEqual(self.logging_system.get_log_count(), 2)
        # Timestamps might have fractional second differences if re-parsed, so check essential fields
        self.assertEqual(self.logging_system.get_log_data()[0]['source'], valid_logs[0]['source'])
        self.assertEqual(self.logging_system.get_log_data()[1]['data'], valid_logs[1]['data'])


    def test_load_logs_from_json_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            self.logging_system.load_logs_from_json_file("non_existent_file.json")

    def test_load_logs_from_json_file_invalid_json(self):
        with open(self.test_log_file, 'w') as f:
            f.write("this is not json")

        with self.assertRaises(json.JSONDecodeError):
            self.logging_system.load_logs_from_json_file(self.test_log_file)

    def test_load_logs_from_json_file_not_a_list(self):
        with open(self.test_log_file, 'w') as f:
            json.dump({"not": "a list"}, f) # JSON content is a dict, not a list

        with self.assertRaisesRegex(LogValidationError, "must contain a list of log entries"):
            self.logging_system.load_logs_from_json_file(self.test_log_file)

    def test_load_logs_from_json_file_contains_invalid_entry(self):
        invalid_log = self.valid_log_entry_1.copy()
        del invalid_log["data"] # Make it invalid
        logs_to_write = [self.valid_log_entry_2, invalid_log]

        with open(self.test_log_file, 'w') as f:
            json.dump(logs_to_write, f)

        with self.assertRaisesRegex(LogValidationError, "Missing required field: 'data'"):
            self.logging_system.load_logs_from_json_file(self.test_log_file)
        self.assertEqual(self.logging_system.get_log_count(), 0,
                         "No logs should be loaded if any entry in the file is invalid during strict validation.")

    def test_clear_logs(self):
        self.logging_system.add_log_entry(self.valid_log_entry_1)
        self.assertEqual(self.logging_system.get_log_count(), 1)
        self.logging_system.clear_logs()
        self.assertEqual(self.logging_system.get_log_count(), 0)
        self.assertEqual(self.logging_system.get_log_data(), [])

    def test_add_log_entry_no_validate(self):
        invalid_entry = {"bad": "data"} # Does not conform to LogEntry structure
        self.logging_system.add_log_entry(invalid_entry, validate=False)
        self.assertEqual(self.logging_system.get_log_count(), 1)
        self.assertEqual(self.logging_system.get_log_data()[0], invalid_entry)

    def test_add_log_entries_no_validate(self):
        invalid_entry = {"bad": "data"}
        entries = [self.valid_log_entry_1, invalid_entry]
        self.logging_system.add_log_entries(entries, validate=False)
        self.assertEqual(self.logging_system.get_log_count(), 2)
        self.assertEqual(self.logging_system.get_log_data(), entries)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
```
