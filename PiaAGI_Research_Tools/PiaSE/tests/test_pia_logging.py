import unittest
import os
import sys
import json
import time
import datetime

# Adjust path to import from the utils directory
# Assuming tests/ is a sibling of utils/ under PiaSE/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))

try:
    from pia_logging import PiaLogger
except ImportError as e:
    print(f"ImportError during test setup: {e}. Adjusting path for PiaLogger.")
    # Fallback for different execution contexts, e.g. if PiaSE is in PYTHONPATH
    # This assumes PiaAGI_Research_Tools is the top-level package recognized by Python.
    # Path from project root would be PiaAGI_Research_Tools.PiaSE.utils.pia_logging
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
    try:
        from PiaAGI_Research_Tools.PiaSE.utils.pia_logging import PiaLogger
    except ImportError as e2:
        print(f"Fallback ImportError: {e2}. PiaLogger could not be imported.")
        PiaLogger = None # Define as None to allow test structure parsing, but tests will fail.

class TestPiaLogger(unittest.TestCase):
    TEST_LOG_DIR = os.path.join(os.path.dirname(__file__), "temp_test_logs_pia_logging") # Ensure unique test log dir
    LOG_FILEPATH = os.path.join(TEST_LOG_DIR, "test_log.jsonl")

    def setUp(self):
        if PiaLogger is None:
            self.skipTest("PiaLogger module could not be imported. Skipping tests.")

        if not os.path.exists(self.TEST_LOG_DIR):
            os.makedirs(self.TEST_LOG_DIR)
        # Ensure the log file is clean before each test
        if os.path.exists(self.LOG_FILEPATH):
            os.remove(self.LOG_FILEPATH)

        # Suppress print statements from PiaLogger constructor and close for cleaner test output
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')


    def tearDown(self):
        if PiaLogger is not None: # Only close if it was opened
            sys.stdout.close()
            sys.stdout = self._original_stdout

        # Clean up the log file and directory after tests
        if os.path.exists(self.LOG_FILEPATH):
            os.remove(self.LOG_FILEPATH)
        if os.path.exists(self.TEST_LOG_DIR) and not os.listdir(self.TEST_LOG_DIR):
            try:
                os.rmdir(self.TEST_LOG_DIR)
            except OSError: # Might fail if another process (like a stray logger) holds it
                pass


    def read_log_entries(self):
        entries = []
        # Ensure stdout is restored for reading, in case of file errors during test
        sys.stdout = self._original_stdout
        print(f"\nAttempting to read log: {self.LOG_FILEPATH}")
        if os.path.exists(self.LOG_FILEPATH):
            with open(self.LOG_FILEPATH, 'r', encoding='utf-8') as f:
                for line in f:
                    print(f"Read line: {line.strip()}") # Debug print
                    entries.append(json.loads(line.strip()))
        else:
            print("Log file does not exist.")
        sys.stdout = open(os.devnull, 'w') # Re-suppress for next test
        return entries

    def test_log_entry_creation_and_format(self):
        with PiaLogger(self.LOG_FILEPATH, "sim1", "exp1", "agent1", "INFO") as logger:
            logger.info("Test.Component", "TEST_EVENT", {"data": "value1"})

        entries = self.read_log_entries()
        self.assertEqual(len(entries), 1)
        entry = entries[0]

        self.assertIn("timestamp", entry)
        self.assertEqual(entry["simulation_run_id"], "sim1")
        self.assertEqual(entry["experiment_id"], "exp1")
        self.assertEqual(entry["agent_id"], "agent1")
        self.assertEqual(entry["source_component_id"], "Test.Component")
        self.assertEqual(entry["log_level"], "INFO")
        self.assertEqual(entry["event_type"], "TEST_EVENT")
        self.assertEqual(entry["event_data"], {"data": "value1"})
        self.assertTrue(entry["timestamp"].endswith("Z"))

    def test_log_level_filtering_info_default(self):
        with PiaLogger(self.LOG_FILEPATH, "sim2", "exp2", "agent2") as logger: # min_log_level defaults to INFO
            logger.debug("Test.Debug", "DEBUG_ONLY", {"detail": "verbose"})
            logger.info("Test.Info", "INFO_MSG", {"msg": "normal info"})
            logger.warn("Test.Warn", "WARNING_MSG", {"warn": "careful"})

        entries = self.read_log_entries()
        self.assertEqual(len(entries), 2)
        if len(entries) == 2: # Avoid index error if previous assert fails
            self.assertEqual(entries[0]["event_type"], "INFO_MSG")
            self.assertEqual(entries[1]["event_type"], "WARNING_MSG")

    def test_log_level_filtering_trace(self):
        with PiaLogger(self.LOG_FILEPATH, "sim3", "exp3", "agent3", "TRACE") as logger:
            logger.trace("Test.Trace", "TRACE_DATA", {"x":1})
            logger.debug("Test.Debug", "DEBUG_DATA", {"y":2})

        entries = self.read_log_entries()
        self.assertEqual(len(entries), 2)

    def test_log_level_filtering_critical_only(self):
        with PiaLogger(self.LOG_FILEPATH, "sim4", "exp4", "agent4", "CRITICAL") as logger:
            logger.info("Test.Info", "INFO_CRIT", {})
            logger.warn("Test.Warn", "WARN_CRIT", {})
            logger.error("Test.Error", "ERR_CRIT", {})
            logger.critical("Test.Crit", "CRIT_MSG", {})

        entries = self.read_log_entries()
        self.assertEqual(len(entries), 1)
        if len(entries) == 1:
            self.assertEqual(entries[0]["event_type"], "CRIT_MSG")

    def test_convenience_methods(self):
        with PiaLogger(self.LOG_FILEPATH, "sim5", "exp5", "agent5", "DEBUG") as logger:
            logger.trace("C", "T", {})
            logger.debug("C", "D", {})
            logger.info("C", "I", {})
            logger.state("C", "S", {})
            logger.warn("C", "W", {})
            logger.error("C", "E", {})
            logger.critical("C", "C", {})

        entries = self.read_log_entries()
        self.assertEqual(len(entries), 6)
        if len(entries) == 6:
            levels_logged = [e['log_level'] for e in entries]
            self.assertEqual(levels_logged, ["DEBUG", "INFO", "STATE", "WARN", "ERROR", "CRITICAL"])

    def test_file_creation_in_subdir(self):
        subdir_log_path = os.path.join(self.TEST_LOG_DIR, "deeper_logs", "events.jsonl")
        if os.path.exists(subdir_log_path): os.remove(subdir_log_path)
        if os.path.exists(os.path.dirname(subdir_log_path)): os.rmdir(os.path.dirname(subdir_log_path)) # Clean deeper_logs if empty

        with PiaLogger(subdir_log_path, "sim_subdir", "exp_subdir", "agent_subdir") as logger:
            logger.info("Test.Sub", "SUBDIR_EVENT", {})

        self.assertTrue(os.path.exists(subdir_log_path))
        entries = []
        # Restore stdout temporarily for this read, as read_log_entries also fiddles with it
        original_stdout = sys.stdout
        sys.stdout = self._original_stdout
        print(f"\nAttempting to read subdir log: {subdir_log_path}")
        if os.path.exists(subdir_log_path):
            with open(subdir_log_path, 'r') as f:
                for line in f:
                    print(f"Read line from subdir: {line.strip()}")
                    entries.append(json.loads(line))
        else:
            print("Subdir log file does not exist.")
        sys.stdout = original_stdout # Put it back to what it was before this method

        self.assertEqual(len(entries), 1)
        if os.path.exists(subdir_log_path): os.remove(subdir_log_path)
        if os.path.exists(os.path.dirname(subdir_log_path)): os.rmdir(os.path.dirname(subdir_log_path))


    def test_log_file_closed_after_with_statement(self):
        logger_instance = PiaLogger(self.LOG_FILEPATH, "sim_ctx", "exp_ctx", "agent_ctx")
        with logger_instance as logger:
            logger.info("Test.CTX", "CTX_EVENT", {})
        self.assertTrue(logger_instance.log_file is None or logger_instance.log_file.closed)

    def test_direct_close_method(self):
        logger = PiaLogger(self.LOG_FILEPATH, "sim_direct", "exp_direct", "agent_direct")
        logger.info("Test.Direct", "DIRECT_EVENT", {})
        self.assertFalse(logger.log_file.closed)
        logger.close()
        self.assertTrue(logger.log_file is None or logger.log_file.closed)

        # Try logging after close (should print error to console, not write to file)
        logger.info("Test.Direct", "AFTER_CLOSE", {})
        entries_after_manual_close = self.read_log_entries()
        self.assertEqual(len(entries_after_manual_close), 1)


if __name__ == '__main__':
    unittest.main()
