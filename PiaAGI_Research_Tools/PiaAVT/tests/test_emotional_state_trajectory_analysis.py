import unittest
import time # Using time for simple timestamp generation
import statistics # For direct comparison if needed, though analysis script uses it
from PiaAGI_Research_Tools.PiaAVT.Analysis_Implementations.emotional_state_trajectory_analysis import analyze_emotional_trajectory

class TestEmotionalStateTrajectoryAnalysis(unittest.TestCase):

    def create_mock_log_entry(self, timestamp, agent_id, sim_id, event_type, event_data):
        return {
            "simulation_run_id": sim_id,
            "timestamp": timestamp,
            "agent_id": agent_id,
            "event_type": event_type,
            "source_module": "EMOTION_MODULE_TEST",
            "event_data": event_data,
            "context_id": f"context_{timestamp}"
        }

    def test_basic_trajectory_processing(self):
        """Test basic processing of a single agent's emotional trajectory."""
        ts = time.time()
        mock_logs = [
            self.create_mock_log_entry(ts, "agent1", "sim1", "EMOTION_STATE_UPDATED", {
                "current_vad": {"valence": 0.5, "arousal": 0.3, "dominance": 0.1},
                "previous_vad": None
            }),
            self.create_mock_log_entry(ts + 1, "agent1", "sim1", "EMOTION_STATE_UPDATED", {
                "current_vad": {"valence": 0.6, "arousal": 0.4, "dominance": 0.2},
                "previous_vad": {"valence": 0.5, "arousal": 0.3, "dominance": 0.1}
            }),
            self.create_mock_log_entry(ts + 2, "agent1", "sim1", "SOME_OTHER_EVENT", {"data": "ignore"}),
            self.create_mock_log_entry(ts + 3, "agent1", "sim1", "EMOTION_STATE_UPDATED", {
                "current_vad": {"valence": 0.7, "arousal": 0.5, "dominance": 0.3},
            }),
        ]

        results = analyze_emotional_trajectory(mock_logs, target_agent_id="agent1", target_simulation_run_id="sim1")

        self.assertEqual(results["agent_id"], "agent1")
        self.assertEqual(results["simulation_run_id"], "sim1")
        self.assertEqual(len(results["trajectory"]), 3)

        # Check trajectory points
        self.assertAlmostEqual(results["trajectory"][0]["valence"], 0.5)
        self.assertAlmostEqual(results["trajectory"][1]["arousal"], 0.4)
        self.assertAlmostEqual(results["trajectory"][2]["dominance"], 0.3)

        # Check summary stats
        stats = results["summary_stats"]
        self.assertEqual(stats["count"], 3)
        self.assertAlmostEqual(stats["avg_valence"], (0.5 + 0.6 + 0.7) / 3)
        self.assertAlmostEqual(stats["avg_arousal"], (0.3 + 0.4 + 0.5) / 3)
        self.assertAlmostEqual(stats["avg_dominance"], (0.1 + 0.2 + 0.3) / 3)

        valences = [0.5, 0.6, 0.7]
        self.assertAlmostEqual(stats["std_valence"], statistics.stdev(valences))

    def test_filtering_by_agent_id(self):
        """Test that analysis correctly filters by agent_id."""
        ts = time.time()
        mock_logs = [
            self.create_mock_log_entry(ts, "agentA", "simMulti", "EMOTION_STATE_UPDATED",
                                       {"current_vad": {"valence": 0.1, "arousal": 0.1, "dominance": 0.1}}),
            self.create_mock_log_entry(ts + 1, "agentB", "simMulti", "EMOTION_STATE_UPDATED",
                                       {"current_vad": {"valence": 0.9, "arousal": 0.9, "dominance": 0.9}}),
            self.create_mock_log_entry(ts + 2, "agentA", "simMulti", "EMOTION_STATE_UPDATED",
                                       {"current_vad": {"valence": 0.2, "arousal": 0.2, "dominance": 0.2}}),
        ]

        results_A = analyze_emotional_trajectory(mock_logs, target_agent_id="agentA")
        self.assertEqual(results_A["agent_id"], "agentA")
        self.assertEqual(len(results_A["trajectory"]), 2)
        self.assertAlmostEqual(results_A["summary_stats"]["avg_valence"], (0.1 + 0.2) / 2)

        results_B = analyze_emotional_trajectory(mock_logs, target_agent_id="agentB")
        self.assertEqual(results_B["agent_id"], "agentB")
        self.assertEqual(len(results_B["trajectory"]), 1)
        self.assertAlmostEqual(results_B["summary_stats"]["avg_valence"], 0.9)

    def test_handling_missing_or_incomplete_data(self):
        """Test graceful handling of missing VAD data or no relevant events."""
        ts = time.time()

        # Case 1: Missing current_vad field
        logs_missing_vad_field = [
            self.create_mock_log_entry(ts, "agentX", "simX", "EMOTION_STATE_UPDATED", {"some_other_data": 1})
        ]
        results1 = analyze_emotional_trajectory(logs_missing_vad_field)
        self.assertEqual(results1["summary_stats"]["count"], 0)
        self.assertEqual(len(results1["trajectory"]), 0)

        # Case 2: Incomplete current_vad (missing 'valence')
        logs_incomplete_vad = [
            self.create_mock_log_entry(ts, "agentY", "simY", "EMOTION_STATE_UPDATED",
                                       {"current_vad": {"arousal": 0.5, "dominance": 0.5}})
        ]
        results2 = analyze_emotional_trajectory(logs_incomplete_vad)
        self.assertEqual(results2["summary_stats"]["count"], 0)

        # Case 3: No EMOTION_STATE_UPDATED events at all
        logs_no_emotion_events = [
            self.create_mock_log_entry(ts, "agentZ", "simZ", "OTHER_EVENT_TYPE", {"data": "payload"})
        ]
        results3 = analyze_emotional_trajectory(logs_no_emotion_events)
        self.assertEqual(results3["summary_stats"]["count"], 0)

        # Case 4: VAD values are None
        logs_none_vad_values = [
            self.create_mock_log_entry(ts, "agentW", "simW", "EMOTION_STATE_UPDATED", {
                "current_vad": {"valence": None, "arousal": 0.5, "dominance": 0.5}
            }),
             self.create_mock_log_entry(ts+1, "agentW", "simW", "EMOTION_STATE_UPDATED", {
                "current_vad": {"valence": 0.5, "arousal": 0.5, "dominance": 0.5} # one valid
            })
        ]
        results4 = analyze_emotional_trajectory(logs_none_vad_values)
        self.assertEqual(results4["summary_stats"]["count"], 1) # Only the valid one should be counted
        self.assertAlmostEqual(results4["trajectory"][0]["valence"], 0.5)


    def test_data_type_and_structure_of_results(self):
        """Verify the overall structure and types of the returned analysis dictionary."""
        ts = time.time()
        mock_logs = [
            self.create_mock_log_entry(ts, "agentS", "simS", "EMOTION_STATE_UPDATED", {
                "current_vad": {"valence": 0.5, "arousal": 0.3, "dominance": 0.1}
            })
        ]
        results = analyze_emotional_trajectory(mock_logs, target_agent_id="agentS")

        self.assertIsInstance(results, dict)
        self.assertIn("agent_id", results)
        self.assertIn("simulation_run_id", results) # Will be None if not in logs or not targeted
        self.assertIn("trajectory", results)
        self.assertIn("summary_stats", results)

        self.assertEqual(results["agent_id"], "agentS")

        self.assertIsInstance(results["trajectory"], list)
        if results["trajectory"]: # If not empty
            point = results["trajectory"][0]
            self.assertIsInstance(point, dict)
            self.assertIn("timestamp", point)
            self.assertIn("valence", point)
            self.assertIn("arousal", point)
            self.assertIn("dominance", point)
            self.assertIsInstance(point["timestamp"], float) # or int, depending on time.time()
            self.assertIsInstance(point["valence"], float)

        self.assertIsInstance(results["summary_stats"], dict)
        expected_stats_keys = [
            "avg_valence", "std_valence", "avg_arousal", "std_arousal",
            "avg_dominance", "std_dominance", "count"
        ]
        for key in expected_stats_keys:
            self.assertIn(key, results["summary_stats"])
            if key != "count": # count is int
                 self.assertIsInstance(results["summary_stats"][key], float)
            else:
                 self.assertIsInstance(results["summary_stats"][key], int)

        # Test with no agent_id specified, should pick one up or use "Multiple_Agents"
        results_no_target = analyze_emotional_trajectory(mock_logs)
        self.assertEqual(results_no_target["agent_id"], "agentS") # Since only one agent is in logs

        # Test when target agent has no emotion logs
        results_wrong_agent = analyze_emotional_trajectory(mock_logs, target_agent_id="nonexistent_agent")
        self.assertEqual(results_wrong_agent["agent_id"], "nonexistent_agent")
        self.assertEqual(results_wrong_agent["summary_stats"]["count"], 0)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
