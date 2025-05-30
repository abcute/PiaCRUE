# PiaAGI_Hub/PiaAVT/tests/test_event_sequencer.py

import unittest
from datetime import datetime

# Adjust import path
try:
    from analyzers.event_sequencer import EventSequencer, LogEntry, DEFAULT_TIMESTAMP_FORMAT
except ImportError:
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__)) # .../PiaAVT/tests
    pia_avt_dir = os.path.dirname(current_dir) # .../PiaAVT
    sys.path.insert(0, pia_avt_dir)
    from analyzers.event_sequencer import EventSequencer, LogEntry, DEFAULT_TIMESTAMP_FORMAT

class TestEventSequencer(unittest.TestCase):

    def setUp(self):
        """Set up for each test method."""
        self.sample_logs: List[LogEntry] = [
            {"timestamp": "2024-01-15T10:00:00.000Z", "source": "User", "event_type": "Query", "data": {"id": 1}},
            {"timestamp": "2024-01-15T10:00:01.000Z", "source": "Agent", "event_type": "Thinking", "data": {"id": 2}},
            {"timestamp": "2024-01-15T10:00:02.000Z", "source": "Agent", "event_type": "Response", "data": {"id": 3}}, # Seq1
            {"timestamp": "2024-01-15T10:00:03.000Z", "source": "User", "event_type": "Query", "data": {"id": 4}},
            {"timestamp": "2024-01-15T10:00:04.000Z", "source": "System", "event_type": "Notification", "data": {"id": 5}}, # Intervening
            {"timestamp": "2024-01-15T10:00:05.000Z", "source": "Agent", "event_type": "Thinking", "data": {"id": 6}},
            {"timestamp": "2024-01-15T10:00:06.000Z", "source": "Agent", "event_type": "Response", "data": {"id": 7}}, # Seq2
            {"timestamp": "2024-01-15T10:00:10.000Z", "source": "User", "event_type": "Query", "data": {"id": 8}}, # Start Seq3
            {"timestamp": "2024-01-15T10:00:15.000Z", "source": "Agent", "event_type": "Thinking", "data": {"id": 9}}, # 5s gap
            {"timestamp": "2024-01-15T10:00:16.000Z", "source": "Agent", "event_type": "Response", "data": {"id": 10}},# Seq3
            {"timestamp": "2024-01-15T10:00:17.000Z", "source": "Agent", "event_type": "Thinking", "data": {"id": 11}},
            {"timestamp": "2024-01-15T10:00:18.000Z", "source": "Agent", "event_type": "Thinking", "data": {"id": 12}},# Repeated Thinking for another test
            {"timestamp": "2024-01-15T10:00:19.000Z", "source": "User", "event_type": "Query", "data": {"id": 13}},
            # Log with bad timestamp for sorting robustness
            {"timestamp": "INVALID_TS", "source": "User", "event_type": "Query", "data": {"id": 14}},
        ]
        self.sequencer = EventSequencer(self.sample_logs)
        self.defined_sequence_QTR = [
            {"event_type": "Query", "source": "User"},
            {"event_type": "Thinking", "source": "Agent"},
            {"event_type": "Response", "source": "Agent"},
        ]

    def test_init_with_invalid_log_data(self):
        with self.assertRaisesRegex(ValueError, "All items in log_data must be dictionaries"):
            EventSequencer([self.sample_logs[0], "not_a_log_entry"]) # type: ignore

    def test_sort_logs_with_invalid_timestamps(self):
        # Ensure _sort_logs_by_timestamp handles invalid timestamps gracefully (puts them at beginning)
        # The log with "INVALID_TS" (id:14) should be first after sorting
        sorted_logs = self.sequencer._sort_logs_by_timestamp(list(self.sequencer.log_data))
        self.assertEqual(sorted_logs[0]["data"]["id"], 14)
        # And the rest should be in order
        parsed_ts_log1 = self.sequencer._parse_timestamp(sorted_logs[1]["timestamp"])
        parsed_ts_log2 = self.sequencer._parse_timestamp(sorted_logs[2]["timestamp"])
        self.assertIsNotNone(parsed_ts_log1)
        self.assertIsNotNone(parsed_ts_log2)
        if parsed_ts_log1 and parsed_ts_log2: # mypy check
             self.assertTrue(parsed_ts_log1 <= parsed_ts_log2)


    def test_extract_basic_sequence(self):
        sequences = self.sequencer.extract_event_sequences(self.defined_sequence_QTR)
        self.assertEqual(len(sequences), 3)
        # Check ids of the first sequence
        self.assertEqual([s["data"]["id"] for s in sequences[0]], [1, 2, 3])
        # Check ids of the second sequence
        self.assertEqual([s["data"]["id"] for s in sequences[1]], [4, 6, 7])
         # Check ids of the third sequence
        self.assertEqual([s["data"]["id"] for s in sequences[2]], [8, 9, 10])


    def test_extract_sequence_with_source_filter(self):
        seq_def_agent_only_thinking = [{"event_type": "Thinking", "source": "Agent"}]
        sequences = self.sequencer.extract_event_sequences(seq_def_agent_only_thinking)
        # Expected thinking: id 2, 6, 9, 11, 12
        self.assertEqual(len(sequences), 5)
        self.assertTrue(all(s[0]["source"] == "Agent" and s[0]["event_type"] == "Thinking" for s in sequences))

    def test_max_time_between_steps(self):
        # Max 3 seconds between steps. Seq3 (id:8,9,10) has a 5s gap (10->15), so it should be excluded.
        sequences = self.sequencer.extract_event_sequences(self.defined_sequence_QTR, max_time_between_steps_seconds=3.0)
        self.assertEqual(len(sequences), 2)
        self.assertEqual([s["data"]["id"] for s in sequences[0]], [1, 2, 3])
        self.assertEqual([s["data"]["id"] for s in sequences[1]], [4, 6, 7])

    def test_max_intervening_logs_zero(self):
        # Seq2 (id:4,6,7) has an intervening log (id:5), so it should be excluded.
        sequences = self.sequencer.extract_event_sequences(self.defined_sequence_QTR, max_intervening_logs=0)
        self.assertEqual(len(sequences), 2) # Seq1 (1,2,3) and Seq3 (8,9,10) have 0 intervening logs
        self.assertEqual([s["data"]["id"] for s in sequences[0]], [1, 2, 3])
        self.assertEqual([s["data"]["id"] for s in sequences[1]], [8, 9, 10])


    def test_max_intervening_logs_one(self):
        # Seq2 (id:4,6,7) has one intervening log, so it should be included.
        sequences = self.sequencer.extract_event_sequences(self.defined_sequence_QTR, max_intervening_logs=1)
        self.assertEqual(len(sequences), 3)

    def test_empty_log_data(self):
        empty_sequencer = EventSequencer([])
        sequences = empty_sequencer.extract_event_sequences(self.defined_sequence_QTR)
        self.assertEqual(len(sequences), 0)

    def test_empty_sequence_definition(self):
        sequences = self.sequencer.extract_event_sequences([])
        self.assertEqual(len(sequences), 0)

    def test_sequence_not_found(self):
        defined_sequence_not_present = [{"event_type": "NonExistentEvent"}]
        sequences = self.sequencer.extract_event_sequences(defined_sequence_not_present)
        self.assertEqual(len(sequences), 0)

    def test_allow_repeats_in_definition_false(self):
        # This tests that two *distinct* log entries matching the same definition step are found
        seq_def_repeated_thinking = [
            {"event_type": "Thinking", "source": "Agent"},
            {"event_type": "Thinking", "source": "Agent"},
        ]
        # Logs 11 and 12 are "Thinking" from "Agent"
        sequences = self.sequencer.extract_event_sequences(seq_def_repeated_thinking, allow_repeats_in_definition=False)
        self.assertEqual(len(sequences), 1)
        self.assertEqual([s["data"]["id"] for s in sequences[0]], [11, 12])

    def test_allow_repeats_in_definition_true(self):
        # Current logic for allow_repeats_in_definition=True doesn't change outcome for *distinct consecutive logs*.
        # It would matter more if a single log instance could match multiple identical steps.
        seq_def_repeated_thinking = [
            {"event_type": "Thinking", "source": "Agent"},
            {"event_type": "Thinking", "source": "Agent"},
        ]
        sequences = self.sequencer.extract_event_sequences(seq_def_repeated_thinking, allow_repeats_in_definition=True)
        self.assertEqual(len(sequences), 1) # Still expects distinct logs for each step
        self.assertEqual([s["data"]["id"] for s in sequences[0]], [11, 12])

    def test_format_sequences_for_display_no_sequences(self):
        formatted_str = self.sequencer.format_sequences_for_display([])
        self.assertEqual(formatted_str, "No event sequences found.")

    def test_format_sequences_for_display_with_sequences(self):
        sequences_found = self.sequencer.extract_event_sequences(self.defined_sequence_QTR)
        formatted_str = self.sequencer.format_sequences_for_display(sequences_found)
        self.assertIn("Found 3 event sequence(s):", formatted_str)
        self.assertIn("--- Sequence 1 ---", formatted_str)
        self.assertIn("Step 1: [2024-01-15T10:00:00.000Z] User - Query", formatted_str)
        self.assertIn("Step 3: [2024-01-15T10:00:02.000Z] Agent - Response", formatted_str)
        self.assertIn("--- Sequence 3 ---", formatted_str)
        self.assertIn("Data: {'id': 10}", formatted_str) # Check data from last step of last seq

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
```
