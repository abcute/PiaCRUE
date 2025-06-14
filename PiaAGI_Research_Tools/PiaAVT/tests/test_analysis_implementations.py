import unittest
import time
from collections import defaultdict
from typing import Dict, Any, List

# Adjust imports to reach PiaAVT and PiaCML components from the tests directory
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PiaAVT.Analysis_Implementations.Goal_Dynamics_Analysis import analyze_goal_lifecycles, load_and_parse_log_data_jsonl as gda_load_logs
from PiaAVT.Analysis_Implementations.emotional_trajectory_analysis import analyze_emotional_trajectory, load_and_parse_log_data_jsonl as eta_load_logs
from PiaAVT.Analysis_Implementations.task_performance_analysis import analyze_task_performance, load_and_parse_log_data_jsonl as tpa_load_logs

# Assuming all load_and_parse_log_data_jsonl are identical, we can use one.
# For clarity in tests, we might call the specific one, or just use one if they are truly identical.
# For this implementation, we'll assume they are similar enough that one loader logic (from GDA) can be used for test data generation.

class TestGoalDynamicsAnalysis(unittest.TestCase):

    def test_analyze_goal_lifecycles_basic(self):
        sample_logs = [
            {"timestamp": 1678886400.0, "event_type": "GOAL_CREATED", "event_data": {"goal_id": "goal1", "description": "Test Goal 1", "type": "EXTRINSIC_TASK", "initial_priority": 0.7}},
            {"timestamp": 1678886401.0, "event_type": "GOAL_STATUS_CHANGED", "event_data": {"goal_id": "goal1", "new_state": "ACTIVE", "old_state": "PENDING"}},
            {"timestamp": 1678886402.0, "event_type": "GOAL_PRIORITY_UPDATED", "event_data": {"goal_id": "goal1", "new_priority": 0.8, "old_priority": 0.7, "reason": "Increased urgency"}},
            {"timestamp": 1678886405.0, "event_type": "GOAL_STATUS_CHANGED", "event_data": {"goal_id": "goal1", "new_state": "ACHIEVED", "old_state": "ACTIVE"}},
            {"timestamp": 1678886403.0, "event_type": "GOAL_CREATED", "event_data": {"goal_id": "goal2", "description": "Test Goal 2", "type": "INTRINSIC_CURIOSITY", "initial_priority": 0.5}},
            {"timestamp": 1678886404.0, "event_type": "GOAL_STATUS_CHANGED", "event_data": {"goal_id": "goal2", "new_state": "ACTIVE", "old_state": "PENDING"}},
            {"timestamp": 1678886406.0, "event_type": "GOAL_STATUS_CHANGED", "event_data": {"goal_id": "goal2", "new_state": "FAILED", "old_state": "ACTIVE", "reason": "Resource unavailable"}}
        ]
        sample_logs.sort(key=lambda x: x["timestamp"]) # Ensure sorted for analysis

        result = analyze_goal_lifecycles(sample_logs)

        self.assertIn("goal1", result)
        self.assertIn("goal2", result)

        goal1_data = result["goal1"]
        self.assertEqual(goal1_data["description"], "Test Goal 1")
        self.assertEqual(goal1_data["type"], "EXTRINSIC_TASK")
        self.assertEqual(goal1_data["creation_time"], 1678886400.0)
        self.assertEqual(goal1_data["current_priority"], 0.8)
        self.assertEqual(len(goal1_data["priority_history"]), 2) # Initial + Updated
        self.assertEqual(goal1_data["priority_history"][1]["priority"], 0.8)
        self.assertEqual(len(goal1_data["state_history"]), 3) # CREATED/PENDING, ACTIVE, ACHIEVED
        self.assertEqual(goal1_data["state_history"][-1]["state"], "ACHIEVED")
        self.assertEqual(goal1_data["outcome"], "ACHIEVED")
        self.assertEqual(goal1_data["end_time"], 1678886405.0)
        self.assertAlmostEqual(goal1_data["duration_seconds"], 5.0) # End - Creation
        self.assertAlmostEqual(goal1_data["active_duration_seconds"], 4.0) # End - Activation
        self.assertEqual(goal1_data["initial_priority_value"], 0.7)
        self.assertEqual(goal1_data["priority_change_count"], 1)
        self.assertAlmostEqual(goal1_data["avg_priority_change_magnitude"], 0.1)


        goal2_data = result["goal2"]
        self.assertEqual(goal2_data["type"], "INTRINSIC_CURIOSITY")
        self.assertEqual(goal2_data["outcome"], "FAILED")
        self.assertEqual(goal2_data["final_failure_reason"], "Resource unavailable")
        self.assertEqual(goal2_data["initial_priority_value"], 0.5)
        self.assertEqual(goal2_data["priority_change_count"], 0) # No GOAL_PRIORITY_UPDATED event for goal2

    def test_analyze_goal_lifecycles_empty_logs(self):
        self.assertEqual(analyze_goal_lifecycles([]), {})

    def test_analyze_goal_lifecycles_no_goal_events(self):
        sample_logs = [
            {"timestamp": 1678886400.0, "event_type": "OTHER_EVENT", "event_data": {"info": "details"}}
        ]
        self.assertEqual(analyze_goal_lifecycles(sample_logs), {})


class TestEmotionalTrajectoryAnalysis(unittest.TestCase):

    def test_analyze_emotional_trajectory_basic(self):
        sample_logs = [
            {"timestamp": 1700000000.0, "agent_id": "agent1", "event_type": "EMOTION_STATE_UPDATED", "event_data": {"current_vad": {"valence": 0.5, "arousal": 0.3, "dominance": 0.1}, "current_discrete_emotion": "Happy", "intensity": 0.6}},
            {"timestamp": 1700000001.0, "agent_id": "agent1", "event_type": "OTHER_EVENT", "event_data": {}},
            {"timestamp": 1700000002.0, "agent_id": "agent1", "event_type": "EMOTION_STATE_UPDATED", "event_data": {"current_emotion_profile": {"valence": -0.2, "arousal": 0.6}, "primary_emotion": "Anxious", "intensity": 0.7}}, # Using fallback fields
            {"timestamp": 1700000003.0, "agent_id": "agent2", "event_type": "EMOTION_STATE_UPDATED", "event_data": {"current_vad": {"valence": 0.1, "arousal": 0.1}, "current_discrete_emotion": "Calm", "intensity": 0.2}}
        ]
        result = analyze_emotional_trajectory(sample_logs)

        self.assertEqual(len(result), 3)

        self.assertEqual(result[0]["timestamp"], 1700000000.0)
        self.assertEqual(result[0]["agent_id"], "agent1")
        self.assertEqual(result[0]["valence"], 0.5)
        self.assertEqual(result[0]["arousal"], 0.3)
        self.assertEqual(result[0]["dominance"], 0.1)
        self.assertEqual(result[0]["discrete_emotion"], "Happy")
        self.assertEqual(result[0]["intensity"], 0.6)

        self.assertEqual(result[1]["timestamp"], 1700000002.0)
        self.assertEqual(result[1]["agent_id"], "agent1")
        self.assertEqual(result[1]["valence"], -0.2)
        self.assertEqual(result[1]["arousal"], 0.6)
        self.assertIsNone(result[1]["dominance"]) # Not in current_emotion_profile
        self.assertEqual(result[1]["discrete_emotion"], "Anxious")
        self.assertEqual(result[1]["intensity"], 0.7)

        self.assertEqual(result[2]["timestamp"], 1700000003.0)
        self.assertEqual(result[2]["agent_id"], "agent2")
        self.assertEqual(result[2]["valence"], 0.1)
        self.assertEqual(result[2]["discrete_emotion"], "Calm")


    def test_analyze_emotional_trajectory_empty_or_no_emotion_events(self):
        self.assertEqual(analyze_emotional_trajectory([]), [])
        sample_logs_no_emotion = [
            {"timestamp": 1700000001.0, "agent_id": "agent1", "event_type": "OTHER_EVENT", "event_data": {}}
        ]
        self.assertEqual(analyze_emotional_trajectory(sample_logs_no_emotion), [])

class TestTaskPerformanceAnalysis(unittest.TestCase):

    def test_analyze_task_performance_basic(self):
        sample_logs = [
            {"timestamp": 1700000100.0, "event_type": "GOAL_CREATED", "event_data": {"goal_id": "task_A", "description": "Perform Task A", "type": "EXTRINSIC_TASK", "initial_priority": 0.9}},
            {"timestamp": 1700000101.0, "event_type": "GOAL_STATUS_CHANGED", "event_data": {"goal_id": "task_A", "new_state": "ACTIVE"}},
            {"timestamp": 1700000102.0, "event_type": "AGENT_ACTION_EXECUTED_IN_ENV", "event_data": {"action_details": {"parameters": {"goal_id": "task_A"}, "cost": 5.0}}},
            {"timestamp": 1700000110.0, "event_type": "GOAL_STATUS_CHANGED", "event_data": {"goal_id": "task_A", "new_state": "ACHIEVED"}},

            {"timestamp": 1700000105.0, "event_type": "GOAL_CREATED", "event_data": {"goal_id": "task_B", "description": "Perform Task B", "type": "EXTRINSIC_TASK"}},
            {"timestamp": 1700000106.0, "event_type": "GOAL_STATUS_CHANGED", "event_data": {"goal_id": "task_B", "new_state": "ACTIVE"}},
            {"timestamp": 1700000107.0, "event_type": "AGENT_ACTION_EXECUTED_IN_ENV", "event_data": {"action_details": {"parameters": {"goal_id": "task_B"}, "resources_consumed": 2.5}}},
            {"timestamp": 1700000115.0, "event_type": "GOAL_STATUS_CHANGED", "event_data": {"goal_id": "task_B", "new_state": "FAILED", "reason": "Critical component missing"}}
        ]
        sample_logs.sort(key=lambda x: x["timestamp"])
        result = analyze_task_performance(sample_logs)

        self.assertIn("task_A", result)
        self.assertIn("task_B", result)

        task_a_data = result["task_A"]
        self.assertEqual(task_a_data["description"], "Perform Task A")
        self.assertEqual(task_a_data["task_type"], "EXTRINSIC_TASK")
        self.assertEqual(task_a_data["start_time"], 1700000101.0)
        self.assertEqual(task_a_data["end_time"], 1700000110.0)
        self.assertEqual(task_a_data["final_status"], "ACHIEVED")
        self.assertEqual(task_a_data["outcome"], "SUCCESS")
        self.assertAlmostEqual(task_a_data["completion_time_seconds"], 9.0)
        self.assertAlmostEqual(task_a_data["resources_consumed_conceptual"], 5.0)

        task_b_data = result["task_B"]
        self.assertEqual(task_b_data["task_type"], "EXTRINSIC_TASK")
        self.assertEqual(task_b_data["start_time"], 1700000106.0)
        self.assertEqual(task_b_data["end_time"], 1700000115.0)
        self.assertEqual(task_b_data["final_status"], "FAILED")
        self.assertEqual(task_b_data["outcome"], "FAILURE")
        self.assertEqual(task_b_data["failure_reason"], "Critical component missing")
        self.assertAlmostEqual(task_b_data["completion_time_seconds"], 9.0)
        self.assertAlmostEqual(task_b_data["resources_consumed_conceptual"], 2.5)

    def test_analyze_task_performance_empty_or_no_task_events(self):
        self.assertEqual(analyze_task_performance([]), {})
        sample_logs_no_task = [
            {"timestamp": 1700000001.0, "event_type": "SOME_OTHER_EVENT", "event_data": {}}
        ]
        # This will return data if task_id (goal_id) is present, but outcome will be UNKNOWN
        result = analyze_task_performance(sample_logs_no_task)
        # Check if it's empty or if it contains entries with UNKNOWN outcome
        if result:
            for task_id, data in result.items():
                 self.assertIn(data.get("outcome"), ["UNKNOWN_OR_NOT_STARTED", "IN_PROGRESS_OR_UNKNOWN"])
        else:
            self.assertEqual(result, {})


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
