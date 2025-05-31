# PiaAGI_Hub/PiaAVT/tests/test_cli.py

import unittest
from unittest.mock import patch, MagicMock, ANY
import subprocess # For some integration-style tests
import sys
import os
import io
import json

# Adjust import path to locate cli.py
# This assumes tests are run from PiaAGI_Hub/PiaAVT/ or project root with PiaAVT in PYTHONPATH
try:
    from PiaAVT import cli # If PiaAVT is a package and cli.py is accessible
except ImportError:
    # Fallback: Add PiaAVT directory to sys.path
    current_dir = os.path.dirname(os.path.abspath(__file__)) # .../PiaAVT/tests
    pia_avt_dir = os.path.dirname(current_dir) # .../PiaAVT
    if pia_avt_dir not in sys.path:
        sys.path.insert(0, pia_avt_dir)
    import cli


# Helper to create a dummy log file for testing 'load'
DUMMY_LOG_FILE_FOR_CLI_TEST = "temp_cli_test_logs.json"
DUMMY_PLOT_OUTPUT_FOR_CLI_TEST = "temp_cli_plot_output.png"

def create_dummy_log_file(filepath=DUMMY_LOG_FILE_FOR_CLI_TEST, content=None):
    if content is None:
        content = [{"timestamp": "2024-03-01T10:00:00.000Z", "source": "Test", "event_type": "Data", "data": {"val": 1}}]
    with open(filepath, 'w') as f:
        json.dump(content, f)

def remove_dummy_log_file(filepath=DUMMY_LOG_FILE_FOR_CLI_TEST):
    if os.path.exists(filepath):
        os.remove(filepath)

def remove_dummy_plot_file(filepath=DUMMY_PLOT_OUTPUT_FOR_CLI_TEST):
    if os.path.exists(filepath):
        os.remove(filepath)

class TestCLI(unittest.TestCase):

    def setUp(self):
        # Redirect stdout and stderr to capture output from cli.main()
        self.captured_output = io.StringIO()
        self.captured_error = io.StringIO()
        sys.stdout = self.captured_output
        sys.stderr = self.captured_error

        # Ensure no leftover dummy files from previous runs
        remove_dummy_log_file()
        remove_dummy_plot_file()

    def tearDown(self):
        # Restore stdout and stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        # Clean up dummy files
        remove_dummy_log_file()
        remove_dummy_plot_file()

        # Reset the global API instance in cli module if it was set
        if hasattr(cli, 'pia_api_instance'):
            cli.pia_api_instance = None


    @patch('PiaAVT.cli.PiaAVTAPI') # Mock the API class itself
    def test_load_command_success(self, MockPiaAVTAPI):
        mock_api_instance = MockPiaAVTAPI.return_value
        mock_api_instance.load_logs_from_json.return_value = True
        mock_api_instance.get_log_count.return_value = 5

        create_dummy_log_file()
        sys.argv = ['cli.py', 'load', DUMMY_LOG_FILE_FOR_CLI_TEST]
        cli.main()

        mock_api_instance.load_logs_from_json.assert_called_once_with(DUMMY_LOG_FILE_FOR_CLI_TEST)
        output = self.captured_output.getvalue()
        self.assertIn(f"CLI: Loading logs from: {DUMMY_LOG_FILE_FOR_CLI_TEST}", output)
        self.assertIn("CLI: Successfully loaded 5 log entries.", output)
        self.assertIsNotNone(cli.pia_api_instance) # Check if global instance was set

    @patch('PiaAVT.cli.PiaAVTAPI')
    def test_load_command_failure(self, MockPiaAVTAPI):
        mock_api_instance = MockPiaAVTAPI.return_value
        mock_api_instance.load_logs_from_json.return_value = False

        sys.argv = ['cli.py', 'load', 'non_existent_file.json']
        cli.main()

        mock_api_instance.load_logs_from_json.assert_called_once_with('non_existent_file.json')
        output = self.captured_output.getvalue()
        self.assertIn("CLI: Failed to load logs", output)

    @patch('PiaAVT.cli.pia_api_instance') # Mock the global instance directly for commands after load
    def test_stats_command(self, mock_pia_api_instance):
        # Simulate that logs are loaded
        mock_pia_api_instance.get_log_count.return_value = 1
        mock_pia_api_instance.get_stats_for_field.return_value = {"mean": 10.0, "count": 2}

        sys.argv = ['cli.py', 'stats', 'data.value', '--source', 'Test']
        cli.main()

        # _parse_field_path in cli.py converts 'data.value' to ['data', 'value']
        # However, the mock is on get_stats_for_field which receives the parsed path.
        # The PiaAVTAPI.get_stats_for_field itself receives Union[str, List[str]]
        # and passes it to BasicAnalyzer.get_descriptive_stats which also takes Union[str, List[str]].
        # So, the mock should expect the format that BasicAnalyzer receives.
        # The cli._parse_field_path converts "data.value" to ["data", "value"]
        mock_pia_api_instance.get_stats_for_field.assert_called_once_with(
            ['data', 'value'],
            source='Test', event_type=None, start_time_str=None, end_time_str=None
        )
        mock_pia_api_instance.display_formatted_dict.assert_called_once_with(
            {"mean": 10.0, "count": 2}, title="Statistics for 'data.value'"
        )
        output = self.captured_output.getvalue()
        self.assertIn("CLI: Calculating statistics for field path: ['data', 'value']", output)


    @patch('PiaAVT.cli.pia_api_instance')
    def test_stats_command_single_field_path(self, mock_pia_api_instance):
        mock_pia_api_instance.get_log_count.return_value = 1

        sys.argv = ['cli.py', 'stats', 'reward'] # Test with non-dotted path
        cli.main()

        mock_pia_api_instance.get_stats_for_field.assert_called_once_with(
            'reward', # Should remain a string
            source=None, event_type=None, start_time_str=None, end_time_str=None
        )


    @patch('PiaAVT.cli.pia_api_instance')
    def test_plot_command(self, mock_pia_api_instance):
        mock_pia_api_instance.get_log_count.return_value = 1

        sys.argv = ['cli.py', 'plot', 'data.temp', '--output', DUMMY_PLOT_OUTPUT_FOR_CLI_TEST, '--no_show']
        cli.main()

        mock_pia_api_instance.plot_field_over_time.assert_called_once_with(
            ['data', 'temp'],
            title=f"Time Series for 'data.temp'",
            y_label='data.temp',
            source=None, event_type=None,
            start_time_str=None, end_time_str=None,
            output_file=DUMMY_PLOT_OUTPUT_FOR_CLI_TEST, show_plot=False
        )
        output = self.captured_output.getvalue()
        self.assertIn("CLI: Generating plot for field path: ['data', 'temp']", output)

    @patch('PiaAVT.cli.pia_api_instance')
    def test_list_logs_command(self, mock_pia_api_instance):
        mock_log_entry = {"timestamp": "2024-03-01T00:00:00.000Z", "source": "S", "event_type": "E", "data": {"d":1}}
        mock_pia_api_instance.get_log_count.return_value = 3 # Total logs
        mock_pia_api_instance.get_all_logs.return_value = [mock_log_entry] * 3

        sys.argv = ['cli.py', 'list_logs', '--limit', '2']
        cli.main()

        output = self.captured_output.getvalue()
        self.assertIn("CLI: Displaying up to 2 of 3 loaded log entries...", output)
        self.assertIn("--- Log Entry 0 ---", output)
        self.assertIn("--- Log Entry 1 ---", output)
        self.assertNotIn("--- Log Entry 2 ---", output)
        self.assertIn("... and 1 more log(s) not shown.", output)

    @patch('PiaAVT.cli.pia_api_instance')
    def test_view_goals_command(self, mock_pia_api_instance):
        mock_goal_log = {"timestamp": "T1", "source": "PiaCML.Motivation", "event_type": "GoalUpdate", "data": {"active_goals": [{"id":"g1"}]}}
        mock_other_log = {"timestamp": "T2", "source": "Other", "event_type": "Event", "data": {"info":"details"}}
        mock_pia_api_instance.get_log_count.return_value = 2
        mock_pia_api_instance.get_all_logs.return_value = [mock_goal_log, mock_other_log]

        sys.argv = ['cli.py', 'view_goals', '0'] # View the goal log
        cli.main()
        mock_pia_api_instance.display_goals_from_log_entry.assert_called_once_with({"active_goals": [{"id":"g1"}]})

        # Reset mock for next call & clear output buffer
        mock_pia_api_instance.display_formatted_dict.reset_mock()
        self.captured_output.seek(0)
        self.captured_output.truncate(0)

        sys.argv = ['cli.py', 'view_goals', '1'] # View the other log
        cli.main()
        mock_pia_api_instance.display_formatted_dict.assert_called_once_with(
            {"info":"details"}, title=ANY # title will be f"Data for Log Entry {index}"
        )
        self.assertIn("does not appear to be a standard goal log", self.captured_output.getvalue())


    @patch('PiaAVT.cli.pia_api_instance')
    def test_sequences_command_json_def(self, mock_pia_api_instance):
        mock_pia_api_instance.get_log_count.return_value = 1
        mock_pia_api_instance.get_formatted_event_sequences.return_value = "Formatted sequence output"

        json_def = '[{"event_type":"Query"},{"event_type":"Thinking","source":"Agent"}]'
        sys.argv = ['cli.py', 'sequences', json_def, '--max_time', '5.0']
        cli.main()

        expected_seq_def = [{"event_type":"Query"},{"event_type":"Thinking","source":"Agent"}]
        mock_pia_api_instance.get_formatted_event_sequences.assert_called_once_with(
            expected_seq_def,
            max_time_between_steps_seconds=5.0,
            max_intervening_logs=None,
            allow_repeats_in_definition=False
        )
        self.assertIn("Formatted sequence output", self.captured_output.getvalue())

    @patch('PiaAVT.cli.pia_api_instance')
    def test_sequences_command_simple_def(self, mock_pia_api_instance):
        mock_pia_api_instance.get_log_count.return_value = 1
        mock_pia_api_instance.get_formatted_event_sequences.return_value = "Simple sequence output"

        simple_def = "Query,Thinking,Response"
        sys.argv = ['cli.py', 'sequences', simple_def]
        cli.main()

        expected_seq_def = [{"event_type": "Query"}, {"event_type": "Thinking"}, {"event_type": "Response"}]
        mock_pia_api_instance.get_formatted_event_sequences.assert_called_once_with(
            expected_seq_def,
            max_time_between_steps_seconds=None,
            max_intervening_logs=None,
            allow_repeats_in_definition=False
        )
        self.assertIn("Simple sequence output", self.captured_output.getvalue())
        self.assertIn("Trying as comma-separated event_types", self.captured_output.getvalue())

    def test_cli_no_command(self):
        process = subprocess.run(
            [sys.executable, cli.__file__],
            capture_output=True, text=True, check=False # Allow non-zero exit code
        )
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("usage: cli.py [-h]", process.stderr)

    def test_cli_invalid_command(self):
        sys.argv = ['cli.py', 'nonexistentcommand']
        with self.assertRaises(SystemExit) as cm:
            cli.main()
        self.assertNotEqual(cm.exception.code, 0)
        self.assertIn("invalid choice: 'nonexistentcommand'", self.captured_error.getvalue())


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

```
