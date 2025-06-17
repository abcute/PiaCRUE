import unittest
import time # Using time for simple timestamp generation
from collections import defaultdict
from PiaAGI_Research_Tools.PiaAVT.Analysis_Implementations.task_performance_analysis import analyze_task_performance

class TestTaskPerformanceAnalysis(unittest.TestCase):

    def create_mock_log_entry(self, timestamp, agent_id, sim_id, event_type, event_data):
        # Basic log structure, customize event_data for specific tests
        return {
            "simulation_run_id": sim_id,
            "timestamp": timestamp,
            "agent_id": agent_id,
            "event_type": event_type,
            "source_module": "TEST_MODULE_TASK_PERF",
            "event_data": event_data,
            "context_id": f"context_task_{timestamp}"
        }

    def test_successful_task_lifecycle(self):
        """Test a single task that is created, activated, and achieved."""
        ts = time.time()
        task_id = "task001"
        mock_logs = [
            self.create_mock_log_entry(ts, "agent1", "sim1", "GOAL_CREATED", {
                "goal_id": task_id,
                "description": "Perform calculation task",
                "type": "CALCULATION_TASK", # Ends with _TASK
                "initial_priority": 7.0
            }),
            self.create_mock_log_entry(ts + 1.0, "agent1", "sim1", "GOAL_STATUS_CHANGED", {
                "goal_id": task_id,
                "new_state": "ACTIVE",
                "reason": "Initiated by planner"
            }),
            self.create_mock_log_entry(ts + 5.0, "agent1", "sim1", "GOAL_STATUS_CHANGED", {
                "goal_id": task_id,
                "new_state": "ACHIEVED",
                "reason": "Calculation successful"
            })
        ]

        analyzed_tasks = analyze_task_performance(mock_logs)
        self.assertIn(task_id, analyzed_tasks)
        task_data = analyzed_tasks[task_id]

        self.assertEqual(task_data["task_id"], task_id)
        self.assertEqual(task_data["description"], "Perform calculation task")
        self.assertEqual(task_data["task_type"], "CALCULATION_TASK")
        self.assertEqual(task_data["outcome"], "SUCCESS")
        self.assertAlmostEqual(task_data["completion_time_seconds"], 4.0) # (ts+5) - (ts+1)
        self.assertEqual(task_data["creation_time"], ts)
        self.assertEqual(task_data["start_time"], ts + 1.0)
        self.assertEqual(task_data["end_time"], ts + 5.0)

    def test_failed_task_with_reason(self):
        """Test a task that fails and logs a reason."""
        ts = time.time()
        task_id = "task002"
        mock_logs = [
            self.create_mock_log_entry(ts, "agent1", "sim1", "GOAL_CREATED", {
                "goal_id": task_id, "type": "IO_TASK", "description": "File write"
            }),
            self.create_mock_log_entry(ts + 0.5, "agent1", "sim1", "GOAL_STATUS_CHANGED", {
                "goal_id": task_id, "new_state": "ACTIVE"
            }),
            self.create_mock_log_entry(ts + 2.5, "agent1", "sim1", "GOAL_STATUS_CHANGED", {
                "goal_id": task_id, "new_state": "FAILED", "reason": "Disk full"
            })
        ]
        analyzed_tasks = analyze_task_performance(mock_logs)
        self.assertIn(task_id, analyzed_tasks)
        task_data = analyzed_tasks[task_id]

        self.assertEqual(task_data["outcome"], "FAILURE")
        self.assertEqual(task_data["failure_reason"], "Disk full")
        self.assertAlmostEqual(task_data["completion_time_seconds"], 2.0) # (ts+2.5) - (ts+0.5)

    def test_multiple_tasks_for_aggregation(self):
        """Test processing of multiple tasks for later summary aggregation."""
        ts = time.time()
        mock_logs = [
            # Task 1: TypeA, Success
            self.create_mock_log_entry(ts, "a1", "s1", "GOAL_CREATED", {"goal_id": "T1", "type": "TypeA_TASK", "desc": "A1S"}),
            self.create_mock_log_entry(ts + 1, "a1", "s1", "GOAL_STATUS_CHANGED", {"goal_id": "T1", "new_state": "ACTIVE"}),
            self.create_mock_log_entry(ts + 5, "a1", "s1", "GOAL_STATUS_CHANGED", {"goal_id": "T1", "new_state": "ACHIEVED"}),
            # Task 2: TypeA, Success
            self.create_mock_log_entry(ts + 0.1, "a1", "s1", "GOAL_CREATED", {"goal_id": "T2", "type": "TypeA_TASK", "desc": "A2S"}),
            self.create_mock_log_entry(ts + 1.1, "a1", "s1", "GOAL_STATUS_CHANGED", {"goal_id": "T2", "new_state": "ACTIVE"}),
            self.create_mock_log_entry(ts + 6.1, "a1", "s1", "GOAL_STATUS_CHANGED", {"goal_id": "T2", "new_state": "ACHIEVED"}),
            # Task 3: TypeA, Failure
            self.create_mock_log_entry(ts + 0.2, "a1", "s1", "GOAL_CREATED", {"goal_id": "T3", "type": "TypeA_TASK", "desc": "A3F"}),
            self.create_mock_log_entry(ts + 1.2, "a1", "s1", "GOAL_STATUS_CHANGED", {"goal_id": "T3", "new_state": "ACTIVE"}),
            self.create_mock_log_entry(ts + 3.2, "a1", "s1", "GOAL_STATUS_CHANGED", {"goal_id": "T3", "new_state": "FAILED"}),
            # Task 4: TypeB, Success
            self.create_mock_log_entry(ts + 0.3, "a1", "s1", "GOAL_CREATED", {"goal_id": "T4", "type": "TypeB_TASK", "desc": "B1S"}),
            self.create_mock_log_entry(ts + 1.3, "a1", "s1", "GOAL_STATUS_CHANGED", {"goal_id": "T4", "new_state": "ACTIVE"}),
            self.create_mock_log_entry(ts + 4.3, "a1", "s1", "GOAL_STATUS_CHANGED", {"goal_id": "T4", "new_state": "ACHIEVED"}),
        ]
        analyzed = analyze_task_performance(mock_logs)
        self.assertEqual(len(analyzed), 4)

        successful_type_a_count = 0
        for task_data in analyzed.values():
            if task_data.get("task_type") == "TypeA_TASK" and task_data.get("outcome") == "SUCCESS":
                successful_type_a_count += 1
        self.assertEqual(successful_type_a_count, 2)

        failed_type_a_count = 0
        for task_data in analyzed.values():
            if task_data.get("task_type") == "TypeA_TASK" and task_data.get("outcome") == "FAILURE":
                failed_type_a_count += 1
        self.assertEqual(failed_type_a_count, 1)

        successful_type_b_count = 0
        for task_data in analyzed.values():
            if task_data.get("task_type") == "TypeB_TASK" and task_data.get("outcome") == "SUCCESS":
                successful_type_b_count += 1
        self.assertEqual(successful_type_b_count, 1)


    def test_incomplete_task_lifecycles(self):
        """Test tasks that are created but not completed or only activated."""
        ts = time.time()
        # Task A: GOAL_CREATED only
        task_A_id = "taskA_incomplete"
        logs_A = [
            self.create_mock_log_entry(ts, "agent2", "sim2", "GOAL_CREATED", {
                "goal_id": task_A_id, "type": "PARTIAL_TASK", "description": "Created only"
            })
        ]
        analyzed_A = analyze_task_performance(logs_A)
        self.assertIn(task_A_id, analyzed_A)
        self.assertEqual(analyzed_A[task_A_id]["outcome"], "UNKNOWN_OR_NOT_STARTED")

        # Task B: GOAL_CREATED, then GOAL_STATUS_CHANGED to "ACTIVE", but no terminal event
        task_B_id = "taskB_active_no_end"
        logs_B = [
            self.create_mock_log_entry(ts, "agent2", "sim2", "GOAL_CREATED", {
                "goal_id": task_B_id, "type": "PARTIAL_TASK", "description": "Active no end"
            }),
            self.create_mock_log_entry(ts + 1.0, "agent2", "sim2", "GOAL_STATUS_CHANGED", {
                "goal_id": task_B_id, "new_state": "ACTIVE"
            })
        ]
        analyzed_B = analyze_task_performance(logs_B)
        self.assertIn(task_B_id, analyzed_B)
        self.assertEqual(analyzed_B[task_B_id]["outcome"], "IN_PROGRESS_OR_UNKNOWN")
        self.assertEqual(analyzed_B[task_B_id]["start_time"], ts + 1.0)


    def test_conceptual_resource_consumption(self):
        """Test aggregation of conceptual resource costs from action events."""
        ts = time.time()
        task_id_res = "task_resource"
        other_task_id = "task_other_for_action"

        mock_logs = [
            self.create_mock_log_entry(ts, "aR", "sR", "GOAL_CREATED", {"goal_id": task_id_res, "type": "RESOURCE_TASK"}),
            self.create_mock_log_entry(ts + 1, "aR", "sR", "GOAL_STATUS_CHANGED", {"goal_id": task_id_res, "new_state": "ACTIVE"}),
            # Action 1 for this task
            self.create_mock_log_entry(ts + 2, "aR", "sR", "AGENT_ACTION_EXECUTED_IN_ENV", {
                "action_id": "act1", "action_type": "TOOL_USE",
                "action_details": {"tool_name": "X", "cost": 10.5, "parameters": {"goal_id": task_id_res}}
            }),
            # Action 2 for this task (using 'resources_consumed')
            self.create_mock_log_entry(ts + 3, "aR", "sR", "AGENT_ACTION_EXECUTED_IN_ENV", {
                "action_id": "act2", "action_type": "MOVE",
                "action_details": {"resources_consumed": 5.0, "parameters": {"goal_id": task_id_res}}
            }),
            # Action for a different task (should be ignored for task_id_res)
             self.create_mock_log_entry(ts + 3.5, "aR", "sR", "AGENT_ACTION_EXECUTED_IN_ENV", {
                "action_id": "act3", "action_type": "CALCULATE",
                "action_details": {"cost": 100.0, "parameters": {"goal_id": other_task_id}}
            }),
            self.create_mock_log_entry(ts + 4, "aR", "sR", "GOAL_STATUS_CHANGED", {"goal_id": task_id_res, "new_state": "ACHIEVED"}),
        ]

        analyzed = analyze_task_performance(mock_logs)
        self.assertIn(task_id_res, analyzed)
        task_data = analyzed[task_id_res]

        self.assertAlmostEqual(task_data.get("resources_consumed_conceptual", 0.0), 15.5) # 10.5 + 5.0

        # Test with no resource costs in actions
        task_id_no_res = "task_no_resource_cost"
        logs_no_res_cost = [
            self.create_mock_log_entry(ts, "aR", "sR", "GOAL_CREATED", {"goal_id": task_id_no_res, "type": "RESOURCE_TASK"}),
            self.create_mock_log_entry(ts + 1, "aR", "sR", "AGENT_ACTION_EXECUTED_IN_ENV", {
                 "action_id": "act4", "action_type": "THINK",
                 "action_details": {"parameters": {"goal_id": task_id_no_res}} # No cost field
            }),
             self.create_mock_log_entry(ts + 2, "aR", "sR", "GOAL_STATUS_CHANGED", {"goal_id": task_id_no_res, "new_state": "ACHIEVED"}),
        ]
        analyzed_no_res = analyze_task_performance(logs_no_res_cost)
        self.assertIn(task_id_no_res, analyzed_no_res)
        self.assertAlmostEqual(analyzed_no_res[task_id_no_res].get("resources_consumed_conceptual", 0.0), 0.0)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
