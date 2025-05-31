# PiaAGI_Hub/PiaAVT/tests/test_visualizers.py

import unittest
import os
from datetime import datetime
import matplotlib # Important for backend configuration in non-GUI environments
matplotlib.use('Agg') # Use a non-interactive backend for tests

# Adjust import path
try:
    from visualizers.timeseries_plotter import TimeseriesPlotter
    from visualizers.state_visualizer import StateVisualizer
except ImportError:
    import sys
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pia_avt_dir = os.path.dirname(current_dir)
    sys.path.insert(0, pia_avt_dir)
    from visualizers.timeseries_plotter import TimeseriesPlotter
    from visualizers.state_visualizer import StateVisualizer

class TestTimeseriesPlotter(unittest.TestCase):

    def setUp(self):
        self.plotter = TimeseriesPlotter()
        self.sample_data_numeric = [
            (datetime(2024, 1, 15, 10, 0, 0), 10),
            (datetime(2024, 1, 15, 10, 5, 0), 12),
            (datetime(2024, 1, 15, 10, 10, 0), 8),
        ]
        self.test_output_file = "temp_test_plot.png"

    def tearDown(self):
        if os.path.exists(self.test_output_file):
            os.remove(self.test_output_file)

    def test_plot_time_series_runs_without_error(self):
        try:
            self.plotter.plot_time_series(
                self.sample_data_numeric,
                title="Test Plot",
                show_plot=False # Important for non-GUI tests
            )
            # If it reaches here without exception, it's a basic success
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"plot_time_series raised an exception: {e}")

    def test_plot_time_series_creates_output_file(self):
        self.plotter.plot_time_series(
            self.sample_data_numeric,
            output_file=self.test_output_file,
            show_plot=False
        )
        self.assertTrue(os.path.exists(self.test_output_file))
        self.assertTrue(os.path.getsize(self.test_output_file) > 0) # Check file is not empty

    def test_plot_time_series_handles_empty_data(self):
        try:
            # Should print "No data provided to plot." and not raise an error
            self.plotter.plot_time_series([], title="Empty Data Plot", show_plot=False)
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"plot_time_series with empty data raised an exception: {e}")

    def test_plot_time_series_handles_non_numeric_data_gracefully(self):
        # The plotter should warn but not necessarily crash for non-numeric Y values.
        # Matplotlib might try to plot them or raise its own error depending on specifics.
        # Here we check that our plotter code doesn't crash before handing off to matplotlib.
        sample_data_non_numeric = [
            (datetime(2024, 1, 15, 10, 0, 0), 'A'),
            (datetime(2024, 1, 15, 10, 5, 0), 'B'),
        ]
        try:
            self.plotter.plot_time_series(
                sample_data_non_numeric,
                title="Non-Numeric Test",
                show_plot=False
            )
            self.assertTrue(True) # Runs without our code raising an error
        except Exception as e:
            self.fail(f"plot_time_series with non-numeric Y raised an exception: {e}")


class TestStateVisualizer(unittest.TestCase):

    def setUp(self):
        self.visualizer = StateVisualizer()

    def test_format_dict_as_text(self):
        sample_dict = {"key1": "value1", "key2": 123, "nested": {"n_key": "n_val"}}
        output = self.visualizer.format_dict_as_text(sample_dict, title="Sample Dict")
        self.assertIn("--- Sample Dict ---", output)
        self.assertIn('"key1": "value1"', output)
        self.assertIn('"key2": 123', output)
        self.assertIn('"nested": {', output)
        self.assertIn('"n_key": "n_val"', output)

    def test_format_dict_as_text_empty_dict(self):
        output = self.visualizer.format_dict_as_text({}, title="Empty Dict")
        self.assertIn("--- Empty Dict ---", output)
        self.assertIn("(No data provided or empty state)", output)

    def test_visualize_current_goals_valid_data(self):
        goals_data = {
            "active_goals": [
                {"id": "g1", "description": "Goal One", "priority": 0.9, "status": "active"},
                {"id": "g2", "description": "Goal Two", "priority": 0.7, "status": "pending"}
            ],
            "goal_hierarchy": {"g1": ["sg1.1", "sg1.2"]}
        }
        output = self.visualizer.visualize_current_goals(goals_data)
        self.assertIn("--- Current Agent Goals ---", output) # Default title
        self.assertIn("Active Goals:", output)
        self.assertIn("ID: g1", output)
        self.assertIn("Description: Goal One", output)
        self.assertIn("Goal Hierarchy:", output)
        self.assertIn("Parent: g1 -> Sub-goals: sg1.1, sg1.2", output)

    def test_visualize_current_goals_no_active_goals(self):
        goals_data = {"active_goals": [], "goal_hierarchy": {}}
        output = self.visualizer.visualize_current_goals(goals_data)
        self.assertIn("No active goals.", output)
        self.assertNotIn("Goal Hierarchy:", output) # Should not print if empty

    def test_visualize_current_goals_malformed_data(self):
        goals_data = {"some_other_key": "value"} # Missing 'active_goals'
        output = self.visualizer.visualize_current_goals(goals_data, title="Malformed Goals")
        self.assertIn("(No valid goal data)", output)

    def test_visualize_current_goals_none_data(self):
        output = self.visualizer.visualize_current_goals(None, title="None Goals")
        self.assertIn("(No valid goal data)", output)


    def test_visualize_working_memory_valid_data(self):
        wm_data = {
            "active_elements": [
                {"id": "e1", "content": "Element One", "salience": 0.8, "type": "percept"},
            ],
            "central_executive_focus": "e1",
            "capacity_used_percent": 50.0,
            "other_field": "test_val"
        }
        output = self.visualizer.visualize_working_memory(wm_data)
        self.assertIn("--- Working Memory State ---", output) # Default title
        self.assertIn("Active Elements:", output)
        self.assertIn("ID: e1", output)
        self.assertIn("Content: Element One", output)
        self.assertIn("Central Executive Focus: e1", output)
        self.assertIn("Capacity Used: 50.0%", output)
        self.assertIn("Additional WM Details:", output)
        self.assertIn('"other_field": "test_val"', output)


    def test_visualize_working_memory_no_active_elements(self):
        wm_data = {"active_elements": [], "capacity_used_percent": 10.0}
        output = self.visualizer.visualize_working_memory(wm_data)
        self.assertIn("No active elements", output)
        self.assertIn("Capacity Used: 10.0%", output)

    def test_visualize_working_memory_none_data(self):
        output = self.visualizer.visualize_working_memory(None, title="None WM")
        self.assertIn("(No valid WM data)", output)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
```
