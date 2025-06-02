# PiaAGI_Hub/PiaAVT/tests/test_basic_analyzer.py

import unittest
from datetime import datetime
from collections import Counter
import sys # Ensure sys is imported for path manipulation
import os  # Ensure os is imported for path manipulation

# Adjust import path to project root (PiaAGI_Research_Tools)
project_root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root_path not in sys.path:
    sys.path.insert(0, project_root_path)

from PiaAGI_Research_Tools.PiaAVT.analyzers.basic_analyzer import BasicAnalyzer, LogEntry, DEFAULT_TIMESTAMP_FORMAT
# from PiaAGI_Research_Tools.PiaAVT.core.logging_system import LoggingSystem # If needed


class TestBasicAnalyzer(unittest.TestCase):

    def setUp(self):
        """Set up for each test method."""
        self.sample_logs: List[LogEntry] = [
            {"timestamp": "2024-01-15T10:00:00.000Z", "source": "SysA", "event_type": "EventX", "data": {"value": 10, "nested": {"item": "A"}}},
            {"timestamp": "2024-01-15T10:00:05.000Z", "source": "SysB", "event_type": "EventY", "data": {"value": 15, "info": "data1"}},
            {"timestamp": "2024-01-15T10:00:10.000Z", "source": "SysA", "event_type": "EventX", "data": {"value": 12, "nested": {"item": "B"}}},
            {"timestamp": "2024-01-15T10:00:15.000Z", "source": "SysC", "event_type": "EventZ", "data": {"value": 20, "info": "data2"}},
            {"timestamp": "2024-01-15T10:00:20.000Z", "source": "SysA", "event_type": "EventY", "data": {"value": 8, "nested": {"item": "A"}}},
            {"timestamp": "2024-01-15T10:00:25.000Z", "source": "SysB", "event_type": "EventX", "data": {"value": 18, "info": "data3"}},
            # Entry with a non-dict data field for testing robustness
            {"timestamp": "2024-01-15T10:00:30.000Z", "source": "SysD", "event_type": "EventW", "data": "not_a_dict"},
            # Entry missing 'data' field
            {"timestamp": "2024-01-15T10:00:35.000Z", "source": "SysE", "event_type": "EventV"},
        ]
        self.analyzer = BasicAnalyzer(self.sample_logs)

    def test_init_with_invalid_log_data(self):
        with self.assertRaisesRegex(ValueError, "All items in log_data must be dictionaries"):
            BasicAnalyzer([self.sample_logs[0], "not_a_log_entry"])

    def test_filter_logs_by_source(self):
        filtered = self.analyzer.filter_logs(source="SysA")
        self.assertEqual(len(filtered), 3)
        self.assertTrue(all(entry["source"] == "SysA" for entry in filtered))

    def test_filter_logs_by_event_type(self):
        filtered = self.analyzer.filter_logs(event_type="EventX")
        self.assertEqual(len(filtered), 3)
        self.assertTrue(all(entry["event_type"] == "EventX" for entry in filtered))

    def test_filter_logs_by_time_range(self):
        start_dt = datetime.strptime("2024-01-15T10:00:05.000Z", DEFAULT_TIMESTAMP_FORMAT)
        end_dt = datetime.strptime("2024-01-15T10:00:15.000Z", DEFAULT_TIMESTAMP_FORMAT)
        filtered = self.analyzer.filter_logs(start_time=start_dt, end_time=end_dt)
        self.assertEqual(len(filtered), 3) # Entries at :05, :10, :15
        # Check timestamps are within range
        for entry in filtered:
            entry_ts = datetime.strptime(entry["timestamp"], DEFAULT_TIMESTAMP_FORMAT)
            self.assertTrue(start_dt <= entry_ts <= end_dt)

    def test_filter_logs_by_start_time_only(self):
        start_dt = datetime.strptime("2024-01-15T10:00:20.000Z", DEFAULT_TIMESTAMP_FORMAT)
        filtered = self.analyzer.filter_logs(start_time=start_dt)
        # Should include :20, :25, :30, :35 (4 entries)
        self.assertEqual(len(filtered), 4)

    def test_filter_logs_no_match(self):
        filtered = self.analyzer.filter_logs(source="NonExistentSource")
        self.assertEqual(len(filtered), 0)

    def test_get_descriptive_stats_simple_field(self):
        stats = self.analyzer.get_descriptive_stats(data_field_path="value", source="SysA", event_type="EventX")
        self.assertIsNotNone(stats)
        self.assertEqual(stats["count"], 2) # 10 and 12
        self.assertAlmostEqual(stats["mean"], 11.0)
        self.assertAlmostEqual(stats["median"], 11.0)
        self.assertEqual(stats["min"], 10)
        self.assertEqual(stats["max"], 12)
        self.assertAlmostEqual(stats["stdev"], 1.4142135623730951)
        self.assertEqual(stats["sum"], 22)

    def test_get_descriptive_stats_all_logs_for_field(self):
        # Value field appears in 6 logs: 10, 15, 12, 20, 8, 18
        stats = self.analyzer.get_descriptive_stats(data_field_path="value")
        self.assertIsNotNone(stats)
        self.assertEqual(stats["count"], 6)
        expected_mean = (10 + 15 + 12 + 20 + 8 + 18) / 6
        self.assertAlmostEqual(stats["mean"], expected_mean)
        self.assertEqual(stats["sum"], 10 + 15 + 12 + 20 + 8 + 18)

    def test_get_descriptive_stats_nested_field(self):
        # This will try to get "item" but it's not numeric. The function should skip non-numeric.
        # Let's add a numeric nested field for a better test.
        self.sample_logs.append(
            {"timestamp": "2024-01-15T10:00:40.000Z", "source": "SysA", "event_type": "EventX",
             "data": {"value": 10, "nested": {"item": "A", "score": 100}}}
        )
        self.sample_logs.append(
            {"timestamp": "2024-01-15T10:00:45.000Z", "source": "SysA", "event_type": "EventX",
             "data": {"value": 12, "nested": {"item": "B", "score": 150}}}
        )
        analyzer_updated = BasicAnalyzer(self.sample_logs)
        stats = analyzer_updated.get_descriptive_stats(data_field_path=["nested", "score"], source="SysA", event_type="EventX")
        self.assertIsNotNone(stats)
        self.assertEqual(stats["count"], 2)
        self.assertAlmostEqual(stats["mean"], 125.0)
        self.assertEqual(stats["sum"], 250)


    def test_get_descriptive_stats_no_matching_data(self):
        stats = self.analyzer.get_descriptive_stats(data_field_path="non_existent_field")
        self.assertIsNone(stats)

    def test_get_descriptive_stats_field_not_numeric(self):
        # 'info' field contains strings
        stats = self.analyzer.get_descriptive_stats(data_field_path="info", source="SysB")
        self.assertIsNone(stats, "Should return None if all targeted field values are non-numeric")


    def test_get_time_series(self):
        ts_data = self.analyzer.get_time_series(data_field_path="value", source="SysA", event_type="EventX")
        self.assertEqual(len(ts_data), 2) # Two entries for SysA, EventX with 'value'
        self.assertEqual(ts_data[0][1], 10) # Value of first entry
        self.assertEqual(ts_data[1][1], 12) # Value of second entry
        self.assertTrue(isinstance(ts_data[0][0], datetime))
        self.assertTrue(ts_data[0][0] < ts_data[1][0], "Time series should be sorted")

    def test_get_time_series_nested(self):
        # Add data for nested time series
        self.sample_logs.append(
             {"timestamp": "2024-01-15T10:00:50.000Z", "source": "SysN", "event_type": "NestedT",
             "data": {"parent": {"child_value": 100}}}
        )
        self.sample_logs.append(
             {"timestamp": "2024-01-15T10:00:55.000Z", "source": "SysN", "event_type": "NestedT",
             "data": {"parent": {"child_value": 110}}}
        )
        analyzer_updated = BasicAnalyzer(self.sample_logs)
        ts_data = analyzer_updated.get_time_series(data_field_path=["parent", "child_value"], source="SysN")
        self.assertEqual(len(ts_data), 2)
        self.assertEqual(ts_data[0][1], 100)
        self.assertEqual(ts_data[1][1], 110)

    def test_get_time_series_no_data(self):
        ts_data = self.analyzer.get_time_series(data_field_path="non_existent_field")
        self.assertEqual(len(ts_data), 0)

    def test_count_unique_values_top_level_field(self):
        counts = self.analyzer.count_unique_values(field_name="source")
        expected_counts = Counter({"SysA": 3, "SysB": 2, "SysC": 1, "SysD":1, "SysE":1})
        self.assertEqual(counts, expected_counts)

    def test_count_unique_values_data_field(self):
        # Counts "item" under "nested" for SysA logs
        counts = self.analyzer.count_unique_values(
            field_name="item", # This is not used if is_data_field is True
            source="SysA",
            is_data_field=True,
            data_field_path=["nested", "item"]
        )
        # SysA entries: {"nested": {"item": "A"}}, {"nested": {"item": "B"}}, {"nested": {"item": "A"}}
        expected_counts = Counter({"A": 2, "B": 1})
        self.assertEqual(counts, expected_counts)

    def test_count_unique_values_data_field_not_found_path(self):
        counts = self.analyzer.count_unique_values(
            field_name="dummy",
            is_data_field=True,
            data_field_path=["nested", "non_existent_sub_key"]
        )
        self.assertEqual(len(counts), 0)

    def test_count_unique_values_requires_data_field_path(self):
        with self.assertRaisesRegex(ValueError, "data_field_path must be provided if is_data_field is True"):
            self.analyzer.count_unique_values(field_name="value", is_data_field=True, data_field_path=None)

    def test_count_unhashable_values_in_data_field(self):
        self.sample_logs.append(
            {"timestamp": "2024-01-15T10:01:00.000Z", "source": "SysX", "event_type": "Unhashable",
             "data": {"complex_val": [1, 2, 3]}} # List is unhashable
        )
        self.sample_logs.append(
            {"timestamp": "2024-01-15T10:01:05.000Z", "source": "SysX", "event_type": "Unhashable",
             "data": {"complex_val": [1, 2, 3]}} # Same unhashable list
        )
        self.sample_logs.append(
            {"timestamp": "2024-01-15T10:01:10.000Z", "source": "SysX", "event_type": "Unhashable",
             "data": {"complex_val": {"a":1}}} # Dict is unhashable
        )
        analyzer_updated = BasicAnalyzer(self.sample_logs)
        counts = analyzer_updated.count_unique_values(
            field_name="complex_val",
            source="SysX",
            is_data_field=True,
            data_field_path="complex_val"
        )
        # Unhashable items are converted to strings for counting
        expected_counts = Counter({"[1, 2, 3]": 2, "{'a': 1}":1})
        self.assertEqual(counts, expected_counts)

    # --- Tests for get_event_frequency ---
    def test_get_event_frequency_total_count(self):
        # EventX appears 3 times in sample_logs
        count = self.analyzer.get_event_frequency(target_event_type="EventX")
        self.assertEqual(count, 3)

        # EventX from SysA appears 2 times
        count_sys_a = self.analyzer.get_event_frequency(target_event_type="EventX", source="SysA")
        self.assertEqual(count_sys_a, 2)

        # Non-existent event
        count_none = self.analyzer.get_event_frequency(target_event_type="NonExistentEvent")
        self.assertEqual(count_none, 0)

    def test_get_event_frequency_grouped_top_level(self):
        # Count EventX occurrences, grouped by "source"
        counts = self.analyzer.get_event_frequency(target_event_type="EventX", group_by_field_path="source")
        expected = Counter({"SysA": 2, "SysB": 1}) # SysA has 2 EventX, SysB has 1 EventX
        self.assertEqual(counts, expected)

    def test_get_event_frequency_grouped_data_field(self):
        # Count "Action" events, grouped by "action_name" in event_data
        # Sample logs for "Action":
        # {"source": "PiaSE.Agent0", "event_type": "Action", "data": {"action_name": "move", "reward": 0.5}},
        # {"source": "PiaSE.Agent0", "event_type": "Action", "data": {"action_name": "interact", "reward": 1.0}},
        # {"source": "PiaSE.Agent0", "event_type": "Action", "data": {"action_name": "move", "reward": -0.1}},
        # For this test, we need to ensure sample_logs has 'Action' event_type
        action_logs = [
            {"timestamp": "2024-01-15T10:00:05.000Z", "source": "PiaSE.Agent0", "event_type": "Action", "data": {"action_name": "move", "reward": 0.5}},
            {"timestamp": "2024-01-15T10:00:25.000Z", "source": "PiaSE.Agent0", "event_type": "Action", "data": {"action_name": "interact", "reward": 1.0}},
            {"timestamp": "2024-01-15T10:00:35.000Z", "source": "PiaSE.Agent0", "event_type": "Action", "data": {"action_name": "move", "reward": -0.1}},
        ]
        analyzer = BasicAnalyzer(action_logs)
        counts = analyzer.get_event_frequency(
            target_event_type="Action",
            group_by_field_path="action_name",
            is_group_by_data_field=True
        )
        expected = Counter({"move": 2, "interact": 1})
        self.assertEqual(counts, expected)

    def test_get_event_frequency_grouped_nested_data_field(self):
        # Count "EventX" from "SysA", grouped by "data.nested.item"
        counts = self.analyzer.get_event_frequency(
            target_event_type="EventX",
            source="SysA", # Filter for SysA first
            group_by_field_path=["nested", "item"], # Path within event_data
            is_group_by_data_field=True
        )
        # SysA EventX logs: data: {"value": 10, "nested": {"item": "A"}}}, data: {"value": 12, "nested": {"item": "B"}}}
        expected = Counter({"A": 1, "B": 1})
        self.assertEqual(counts, expected)

    def test_get_event_frequency_with_filters(self):
        # Count "EventY", but only for source "SysA"
        count = self.analyzer.get_event_frequency(target_event_type="EventY", source="SysA")
        # SysA logs: EventX, EventX, EventY. So 1 EventY for SysA.
        self.assertEqual(count, 1)

    def test_get_event_frequency_group_by_invalid_path(self):
        counts = self.analyzer.get_event_frequency(
            target_event_type="EventX",
            group_by_field_path="data.non_existent.path", # Invalid path
            is_group_by_data_field=True # Path is relative to event_data
        )
        # All 3 "EventX" logs will result in "NoneOrInvalidPath" for grouping key
        self.assertEqual(counts, Counter({"NoneOrInvalidPath": 3}))

        counts_top_level_invalid = self.analyzer.get_event_frequency(
            target_event_type="EventX",
            group_by_field_path="non_existent_top_key"
        )
        self.assertEqual(counts_top_level_invalid, Counter({"NoneOrInvalidPath": 3}))

        counts_path_type_error = self.analyzer.get_event_frequency(
            target_event_type="EventW", # data is "not_a_dict"
            group_by_field_path="some_key",
            is_group_by_data_field=True
        )
        # The simplified logic will result in "NoneOrInvalidPath" because path traversal fails early.
        self.assertEqual(counts_path_type_error, Counter({"NoneOrInvalidPath":1}))


    # --- Tests for track_goal_lifecycle ---
    def test_track_goal_lifecycle_found(self):
        goal_logs = [
            {"timestamp": "2024-01-15T10:00:00.000Z", "source":"S", "event_type": "GOAL_CREATED", "event_data": {"goal_id": "g1", "desc": "Start G1"}},
            {"timestamp": "2024-01-15T10:00:05.000Z", "source":"S", "event_type": "UNRELATED_EVENT", "event_data": {}},
            {"timestamp": "2024-01-15T10:00:10.000Z", "source":"S", "event_type": "GOAL_STATUS_CHANGED", "event_data": {"goal_id": "g1", "status": "in_progress"}},
            {"timestamp": "2024-01-15T10:00:02.000Z", "source":"S", "event_type": "GOAL_ACTIVATED", "event_data": {"goal_id": "g1"}}, # Out of order timestamp
            {"timestamp": "2024-01-15T10:00:15.000Z", "source":"S", "event_type": "GOAL_ACHIEVED", "event_data": {"goal_id": "g1"}},
            {"timestamp": "2024-01-15T10:00:20.000Z", "source":"S", "event_type": "GOAL_CREATED", "event_data": {"goal_id": "g2"}}, # Different goal
        ]
        analyzer = BasicAnalyzer(goal_logs)
        lifecycle = analyzer.track_goal_lifecycle(goal_id="g1")
        self.assertEqual(len(lifecycle), 4)
        self.assertEqual(lifecycle[0]["event_type"], "GOAL_CREATED")
        self.assertEqual(lifecycle[1]["event_type"], "GOAL_ACTIVATED") # Check sorting
        self.assertEqual(lifecycle[2]["event_type"], "GOAL_STATUS_CHANGED")
        self.assertEqual(lifecycle[3]["event_type"], "GOAL_ACHIEVED")

    def test_track_goal_lifecycle_not_found(self):
        lifecycle = self.analyzer.track_goal_lifecycle(goal_id="non_existent_goal")
        self.assertEqual(len(lifecycle), 0)

    def test_track_goal_lifecycle_with_filters(self):
        goal_logs_for_filter = [
            {"timestamp": "2024-01-15T10:00:00.000Z", "source":"SysA", "event_type": "GOAL_CREATED", "event_data": {"goal_id": "g1"}},
            {"timestamp": "2024-01-15T10:00:05.000Z", "source":"SysB", "event_type": "GOAL_ACTIVATED", "event_data": {"goal_id": "g1"}},
            {"timestamp": "2024-01-15T10:00:10.000Z", "source":"SysA", "event_type": "GOAL_ACHIEVED", "event_data": {"goal_id": "g1"}},
        ]
        analyzer = BasicAnalyzer(goal_logs_for_filter)

        # Filter by source SysA
        lifecycle_sys_a = analyzer.track_goal_lifecycle(goal_id="g1", source="SysA")
        self.assertEqual(len(lifecycle_sys_a), 2)
        self.assertTrue(all(entry["source"] == "SysA" for entry in lifecycle_sys_a))
        self.assertEqual(lifecycle_sys_a[0]["event_type"], "GOAL_CREATED")
        self.assertEqual(lifecycle_sys_a[1]["event_type"], "GOAL_ACHIEVED")

        # Filter by time
        start_dt = datetime.strptime("2024-01-15T10:00:03.000Z", DEFAULT_TIMESTAMP_FORMAT)
        lifecycle_timed = analyzer.track_goal_lifecycle(goal_id="g1", start_time=start_dt)
        self.assertEqual(len(lifecycle_timed), 2) # SysB GOAL_ACTIVATED and SysA GOAL_ACHIEVED
        self.assertEqual(lifecycle_timed[0]["event_type"], "GOAL_ACTIVATED")


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
