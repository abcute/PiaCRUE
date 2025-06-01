import unittest
import sys
import os
import matplotlib.pyplot as plt

# Simplified path adjustment
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))) # Adds project root (PiaAGI) to path

from PiaAGI_Hub.PiaSE.environments.grid_world import GridWorld
from PiaAGI_Hub.PiaSE.utils.visualizer import GridWorldVisualizer

class TestGridWorldVisualizer(unittest.TestCase):

    def setUp(self):
        self.grid_width = 5
        self.grid_height = 5
        self.walls = [(1, 1), (2, 2)]
        self.goal_pos = (self.grid_width - 1, self.grid_height - 1)
        self.start_pos_agent1 = (0,0)

        self.grid_world = GridWorld(
            width=self.grid_width,
            height=self.grid_height,
            walls=self.walls,
            goal_position=self.goal_pos,
            agent_start_positions={"agent1": self.start_pos_agent1}
        )
        self.grid_world.reset() # Ensures agent is placed

        self.visualizer = GridWorldVisualizer(self.grid_world)
        # Ensure plots don't try to display in a headless environment during tests
        # However, plt.ioff() might affect other tests if not managed carefully.
        # A better way is to use a non-interactive backend for testing if issues arise.
        # For now, we assume the default backend is non-interactive or plt.pause is very short.
        # plt.ioff() # This can be problematic if other tests need interactive mode

    def test_visualizer_instantiation(self):
        self.assertIsNotNone(self.visualizer)
        self.assertEqual(self.visualizer.env, self.grid_world)

    def test_render_runs_without_errors(self):
        # Test if render runs. Visual output is not checked in automated tests.
        try:
            # Using a very small step_delay to make plt.pause non-blocking
            self.visualizer.render(title="Test Render", step_delay=0.001)
            # Close the figure created by this render call to avoid state leakage
            plt.close(self.visualizer.fig)
        except Exception as e:
            self.fail(f"visualizer.render() raised an exception: {e}")

    def test_render_with_no_agents(self):
        empty_env = GridWorld(width=3, height=3, goal_position=(2,2)) # No agents defined
        vis_empty = GridWorldVisualizer(empty_env)
        try:
            vis_empty.render(title="Empty Env Test", step_delay=0.001)
            plt.close(vis_empty.fig)
        except Exception as e:
            self.fail(f"visualizer.render() with empty env raised an exception: {e}")

    def test_render_with_walls_and_goal(self):
        # This test primarily ensures that rendering with typical elements doesn't crash
        try:
            self.visualizer.render(title="Walls and Goal Test", step_delay=0.001)
            plt.close(self.visualizer.fig)
        except Exception as e:
            self.fail(f"visualizer.render() for walls/goal raised an exception: {e}")

    def tearDown(self):
        # Close all figures that might have been created during tests
        plt.close('all')

if __name__ == '__main__':
    # This is important to ensure that if any test uses plt.show() or plt.pause()
    # in a blocking way, the test runner can still proceed.
    # However, for automated tests, blocking is usually avoided.
    # The provided visualizer.render uses plt.pause which is non-blocking in non-interactive mode
    # or blocking for the specified duration in interactive mode.
    # step_delay=None in render *will* call plt.show() which is blocking.
    # For tests, always use a small float for step_delay.
    unittest.main()
