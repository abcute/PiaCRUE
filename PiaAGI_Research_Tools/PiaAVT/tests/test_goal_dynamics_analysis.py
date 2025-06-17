import unittest
import time
from collections import defaultdict
from PiaAGI_Research_Tools.PiaAVT.Analysis_Implementations.Goal_Dynamics_Analysis import analyze_goal_lifecycles, generate_summary_report
# Assuming core_messages.py is structured such that these can be conceptually represented
# For actual testing with core_messages, you might need to import specific payload classes
# if analyze_goal_lifecycles expects them directly, but it seems to work with dicts.

class TestGoalDynamicsAnalysis(unittest.TestCase):

    def create_mock_log_entry(self, timestamp, event_type, event_data):
        return {
            "simulation_run_id": "sim_test_run",
            "timestamp": timestamp,
            "event_type": event_type,
            "source_module": "TEST_MODULE",
            "event_data": event_data,
            "context_id": "test_context"
        }

    def test_basic_goal_lifecycle_create_activate_achieve(self):
        """Test a single goal that is created, activated, and achieved."""
        ts = time.time()
        mock_logs = [
            self.create_mock_log_entry(ts, "GOAL_CREATED", {
                "goal_id": "G001",
                "description": "Test Goal 1",
                "type": "EXTRINSIC_TASK",
                "initial_priority": 5.0
            }),
            self.create_mock_log_entry(ts + 1, "GOAL_ACTIVATED", {
                "goal_id": "G001",
                "reason": "Sufficient resources"
            }),
            self.create_mock_log_entry(ts + 5, "GOAL_STATE_CHANGED", {
                "goal_id": "G001",
                "new_state": "ACHIEVED",
                "reason": "Task completed successfully"
            })
        ]
        analyzed_goals = analyze_goal_lifecycles(mock_logs)
        self.assertIn("G001", analyzed_goals)
        goal_data = analyzed_goals["G001"]

        self.assertEqual(goal_data["description"], "Test Goal 1")
        self.assertEqual(goal_data["type"], "EXTRINSIC_TASK")
        self.assertEqual(goal_data["creation_time"], ts)
        self.assertEqual(goal_data["initial_priority_value"], 5.0)
        self.assertEqual(goal_data["outcome"], "ACHIEVED")
        self.assertEqual(goal_data["end_time"], ts + 5)
        self.assertAlmostEqual(goal_data["duration_seconds"], 5.0)
        self.assertAlmostEqual(goal_data["active_duration_seconds"], 4.0) # (ts+5) - (ts+1)
        self.assertEqual(len(goal_data["state_history"]), 3) # CREATED, ACTIVE, ACHIEVED
        self.assertEqual(goal_data["state_history"][1]["state"], "ACTIVE")
        self.assertEqual(goal_data["state_history"][2]["state"], "ACHIEVED")

    def test_goal_with_priority_update_and_failure(self):
        """Test a goal that has its priority updated and then fails."""
        ts = time.time()
        mock_logs = [
            self.create_mock_log_entry(ts, "GOAL_CREATED", {
                "goal_id": "G002",
                "description": "Test Goal 2",
                "type": "INTRINSIC_CURIOSITY",
                "initial_priority": 3.0
            }),
            self.create_mock_log_entry(ts + 2, "GOAL_PRIORITY_UPDATED", {
                "goal_id": "G002",
                "new_priority": 7.0,
                "old_priority": 3.0,
                "reason": "Increased importance"
            }),
            self.create_mock_log_entry(ts + 3, "GOAL_ACTIVATED", {
                "goal_id": "G002",
                "reason": "Now high priority"
            }),
            self.create_mock_log_entry(ts + 7, "GOAL_STATE_CHANGED", {
                "goal_id": "G002",
                "new_state": "FAILED",
                "reason": "Resource conflict"
            })
        ]
        analyzed_goals = analyze_goal_lifecycles(mock_logs)
        self.assertIn("G002", analyzed_goals)
        goal_data = analyzed_goals["G002"]

        self.assertEqual(goal_data["outcome"], "FAILED")
        self.assertEqual(goal_data["final_failure_reason"], "Resource conflict")
        self.assertEqual(goal_data["current_priority"], 7.0)
        self.assertEqual(len(goal_data["priority_history"]), 2)
        self.assertEqual(goal_data["priority_history"][1]["new_priority"], 7.0)
        self.assertEqual(goal_data["priority_change_count"], 1)
        self.assertAlmostEqual(goal_data["total_priority_change_magnitude"], 4.0) # abs(7.0 - 3.0)
        self.assertAlmostEqual(goal_data["avg_priority_change_magnitude"], 4.0)
        self.assertAlmostEqual(goal_data["duration_seconds"], 7.0)
        self.assertAlmostEqual(goal_data["active_duration_seconds"], 4.0) # (ts+7) - (ts+3)


    def test_multiple_goals_for_summary_aggregation(self):
        """Test aggregation of data from multiple goals for summary report."""
        ts = time.time()
        mock_logs = [
            # Goal G003: Achieved
            self.create_mock_log_entry(ts, "GOAL_CREATED", {"goal_id": "G003", "type": "TYPE_A", "initial_priority": 2.0}),
            self.create_mock_log_entry(ts + 1, "GOAL_ACTIVATED", {"goal_id": "G003"}),
            self.create_mock_log_entry(ts + 5, "GOAL_STATE_CHANGED", {"goal_id": "G003", "new_state": "ACHIEVED"}),
            # Goal G004: Failed
            self.create_mock_log_entry(ts + 0.5, "GOAL_CREATED", {"goal_id": "G004", "type": "TYPE_B", "initial_priority": 8.0}),
            self.create_mock_log_entry(ts + 1.5, "GOAL_ACTIVATED", {"goal_id": "G004"}),
            self.create_mock_log_entry(ts + 3.5, "GOAL_STATE_CHANGED", {"goal_id": "G004", "new_state": "FAILED", "reason": "Timeout"}),
            # Goal G005: Active (no terminal state)
            self.create_mock_log_entry(ts + 1, "GOAL_CREATED", {"goal_id": "G005", "type": "TYPE_A", "initial_priority": 6.0}),
            self.create_mock_log_entry(ts + 2, "GOAL_ACTIVATED", {"goal_id": "G005"}),
            self.create_mock_log_entry(ts + 3, "GOAL_PRIORITY_UPDATED", {"goal_id": "G005", "new_priority": 7.5, "old_priority": 6.0})
        ]
        analyzed_goals = analyze_goal_lifecycles(mock_logs)
        self.assertEqual(len(analyzed_goals), 3)

        # Test data points that generate_summary_report would use
        achieved_count = sum(1 for g in analyzed_goals.values() if g.get("outcome") == "ACHIEVED")
        failed_count = sum(1 for g in analyzed_goals.values() if g.get("outcome") == "FAILED")

        self.assertEqual(achieved_count, 1)
        self.assertEqual(failed_count, 1)

        goals_by_type = defaultdict(lambda: {"count": 0, "achieved": 0, "failed": 0})
        for data in analyzed_goals.values():
            goal_type = data.get("type", "UNKNOWN")
            goals_by_type[goal_type]["count"] += 1
            if data.get("outcome") == "ACHIEVED":
                goals_by_type[goal_type]["achieved"] += 1
            elif data.get("outcome") == "FAILED":
                goals_by_type[goal_type]["failed"] += 1

        self.assertEqual(goals_by_type["TYPE_A"]["count"], 2)
        self.assertEqual(goals_by_type["TYPE_A"]["achieved"], 1)
        self.assertEqual(goals_by_type["TYPE_B"]["count"], 1)
        self.assertEqual(goals_by_type["TYPE_B"]["failed"], 1)

        self.assertEqual(analyzed_goals["G005"].get("priority_change_count",0), 1)


    def test_edge_cases_handling(self):
        """Test handling of edge cases like no relevant events or non-terminal goals."""
        ts = time.time()
        # 1. No relevant goal events
        mock_logs_empty = [
            self.create_mock_log_entry(ts, "SOME_OTHER_EVENT", {"data": "irrelevant"})
        ]
        analyzed_empty = analyze_goal_lifecycles(mock_logs_empty)
        self.assertEqual(len(analyzed_empty), 0)

        # 2. Goal created but never activated or terminated
        mock_logs_created_only = [
            self.create_mock_log_entry(ts, "GOAL_CREATED", {
                "goal_id": "G006",
                "description": "Created Only",
                "type": "TEST_EDGE",
                "initial_priority": 1.0
            })
        ]
        analyzed_created_only = analyze_goal_lifecycles(mock_logs_created_only)
        self.assertIn("G006", analyzed_created_only)
        g006_data = analyzed_created_only["G006"]
        self.assertNotIn("outcome", g006_data) # No terminal state
        self.assertNotIn("end_time", g006_data)
        self.assertNotIn("active_duration_seconds", g006_data) # Never activated
        self.assertEqual(g006_data["current_priority"], 1.0)
        self.assertEqual(len(g006_data["state_history"]), 1) # Only CREATED

        # 3. Goal activated but not terminated
        mock_logs_activated_not_terminated = [
            self.create_mock_log_entry(ts, "GOAL_CREATED", {"goal_id": "G007", "initial_priority": 2.0}),
            self.create_mock_log_entry(ts + 1, "GOAL_ACTIVATED", {"goal_id": "G007"})
        ]
        analyzed_activated = analyze_goal_lifecycles(mock_logs_activated_not_terminated)
        self.assertIn("G007", analyzed_activated)
        g007_data = analyzed_activated["G007"]
        self.assertNotIn("outcome", g007_data)
        self.assertIn("first_activation_time", g007_data)
        self.assertEqual(g007_data["current_state"], "ACTIVE")


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

# Note: generate_summary_report primarily prints.
# For more robust testing of the report itself, it would need to be refactored
# to return a structured dictionary of summary statistics, which could then be asserted against.
# The current tests for `analyze_goal_lifecycles` cover the data aggregation needed for the report.
