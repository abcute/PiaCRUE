import unittest
import os
import sys

# Adjust sys.path to allow imports from PiaAGI_Hub
# Assuming this test script is in PiaAGI_Hub/PiaSE/tests/
# We need to go up three levels to reach PiaAGI_Hub's parent directory (/app)
current_dir = os.path.dirname(os.path.abspath(__file__))
piase_dir = os.path.dirname(current_dir)  # PiaAGI_Hub/PiaSE/
piaagi_hub_dir = os.path.dirname(piase_dir)  # PiaAGI_Hub/
project_root_dir = os.path.dirname(piaagi_hub_dir)  # /app (parent of PiaAGI_Hub)

if project_root_dir not in sys.path:
    sys.path.insert(0, project_root_dir)

from PiaAGI_Hub.PiaSE.environments.grid_world import GridWorld

class TestGridWorld(unittest.TestCase):
    def setUp(self):
        """Set up a common GridWorld instance for tests."""
        self.width = 10
        self.height = 8
        self.walls = [(2, 2), (3, 3)]
        self.agent_start_positions = {"agent1": (0, 0), "agent2": (1, 1)}
        self.grid_world = GridWorld(
            width=self.width,
            height=self.height,
            walls=self.walls,
            agent_start_positions=self.agent_start_positions,
            goal_position=(self.width - 1, self.height - 1) # Explicitly set goal
        )
        self.goal_pos = (self.width - 1, self.height - 1)
        # Add an agent that wasn't in the initial start positions for some tests
        self.grid_world.add_agent("agent3", (5,5))


    def test_initialization(self):
        """Test basic GridWorld initialization."""
        self.assertEqual(self.grid_world.width, self.width)
        self.assertEqual(self.grid_world.height, self.height)
        for wx, wy in self.walls:
            self.assertEqual(self.grid_world.grid[wy][wx], 1, f"Wall missing at ({wx},{wy})")
        self.assertIn("agent1", self.grid_world.agent_positions)
        self.assertEqual(self.grid_world.agent_positions["agent1"], (0,0))
        self.assertIn("agent2", self.grid_world.agent_positions)
        self.assertEqual(self.grid_world.agent_positions["agent2"], (1,1))
        self.assertIn("agent3", self.grid_world.agent_positions)
        self.assertEqual(self.grid_world.agent_positions["agent3"], (5,5))

    def test_add_agent_updates_start_positions(self):
        """Test if add_agent also updates agent_start_positions."""
        self.grid_world.add_agent("agent4", (6,6))
        self.assertIn("agent4", self.grid_world.agent_start_positions)
        self.assertEqual(self.grid_world.agent_start_positions["agent4"], (6,6))


    def test_agent_movement_valid(self):
        """Test valid agent movements."""
        # Agent1 starts at (0,0)
        # Move South to (0,1)
        obs, reward, done, info = self.grid_world.step("agent1", "S")
        self.assertEqual(self.grid_world.agent_positions["agent1"], (0, 1))
        self.assertEqual(obs["agent_position"], (0, 1))
        # self.assertEqual(reward, 0.0) # Reward is now -0.1 for normal move

        # Move East to (1,1)
        obs, reward, done, info = self.grid_world.step("agent1", "E")
        self.assertEqual(self.grid_world.agent_positions["agent1"], (1, 1))
        self.assertEqual(obs["agent_position"], (1, 1))

        # Move North to (1,0)
        obs, reward, done, info = self.grid_world.step("agent1", "N")
        self.assertEqual(self.grid_world.agent_positions["agent1"], (1, 0))
        self.assertEqual(obs["agent_position"], (1, 0))

        # Move West to (0,0)
        obs, reward, done, info = self.grid_world.step("agent1", "W")
        self.assertEqual(self.grid_world.agent_positions["agent1"], (0, 0))
        self.assertEqual(obs["agent_position"], (0, 0))

        # Stay
        obs, reward, done, info = self.grid_world.step("agent1", "Stay")
        self.assertEqual(self.grid_world.agent_positions["agent1"], (0, 0))
        self.assertEqual(obs["agent_position"], (0, 0))

    def test_agent_movement_boundary_collision(self):
        """Test agent movement against boundaries."""
        # Agent1 at (0,0)
        # Try to move North (invalid)
        self.grid_world.step("agent1", "N")
        self.assertEqual(self.grid_world.agent_positions["agent1"], (0, 0))
        # Try to move West (invalid)
        self.grid_world.step("agent1", "W")
        self.assertEqual(self.grid_world.agent_positions["agent1"], (0, 0))

        # Move agent3 to boundary (width-1, height-1) = (9,7)
        self.grid_world.agent_positions["agent3"] = (self.width - 1, self.height - 1)
        # Try to move South (invalid)
        self.grid_world.step("agent3", "S")
        self.assertEqual(self.grid_world.agent_positions["agent3"], (self.width - 1, self.height - 1))
        # Try to move East (invalid)
        self.grid_world.step("agent3", "E")
        self.assertEqual(self.grid_world.agent_positions["agent3"], (self.width - 1, self.height - 1))


    def test_agent_movement_wall_collision(self):
        """Test agent movement against walls."""
        # Agent2 at (1,1). Wall at (2,2)
        # Move agent2 to (1,2) next to wall (2,2)
        self.grid_world.agent_positions["agent2"] = (1,2)
        # Try to move East into wall (2,2)
        obs, reward, done, info = self.grid_world.step("agent2", "E") # Action to (2,2) - wall
        self.assertEqual(self.grid_world.agent_positions["agent2"], (1, 2)) # Should not move
        self.assertEqual(obs["agent_position"], (1,2))

        # Move agent2 to (2,1) above wall (2,2)
        self.grid_world.agent_positions["agent2"] = (2,1)
        # Try to move South into wall (2,2)
        obs, reward, done, info = self.grid_world.step("agent2", "S") # Action to (2,2) - wall
        self.assertEqual(self.grid_world.agent_positions["agent2"], (2, 1)) # Should not move
        self.assertEqual(obs["agent_position"], (2,1))


    def test_get_observation(self):
        """Test the format and content of get_observation."""
        agent_id = "agent1"
        observation = self.grid_world.get_observation(agent_id)
        self.assertIsInstance(observation, dict)
        self.assertIn("agent_position", observation)
        self.assertIn("grid_view", observation)
        self.assertEqual(observation["agent_position"], self.agent_start_positions[agent_id])
        self.assertEqual(len(observation["grid_view"]), self.height)
        self.assertEqual(len(observation["grid_view"][0]), self.width)
        # Check if grid_view is a copy
        observation["grid_view"][0][0] = 99
        self.assertNotEqual(self.grid_world.grid[0][0], 99, "grid_view should be a copy, not a direct reference.")


    def test_get_state(self):
        """Test the format and content of get_state."""
        state = self.grid_world.get_state()
        self.assertIsInstance(state, dict)
        self.assertIn("grid", state)
        self.assertIn("all_agent_positions", state)
        self.assertEqual(len(state["grid"]), self.height)
        self.assertEqual(len(state["grid"][0]), self.width)
        self.assertEqual(state["all_agent_positions"]["agent1"], self.agent_start_positions["agent1"])
        self.assertEqual(state["all_agent_positions"]["agent3"], (5,5))
        # Check if grid is a copy
        state["grid"][0][0] = 99
        self.assertNotEqual(self.grid_world.grid[0][0], 99, "state['grid'] should be a copy.")
        # Check if all_agent_positions is a copy
        state["all_agent_positions"]["agent1"] = (100,100)
        self.assertNotEqual(self.grid_world.agent_positions["agent1"], (100,100), "state['all_agent_positions'] should be a copy.")


    def test_reset_single_agent(self):
        """Test resetting a single agent's position."""
        agent_id = "agent1"
        # Move agent1
        self.grid_world.step(agent_id, "S")
        self.assertNotEqual(self.grid_world.agent_positions[agent_id], self.agent_start_positions[agent_id])
        # Reset agent1
        self.grid_world.reset(agent_id_to_reset=agent_id)
        self.assertEqual(self.grid_world.agent_positions[agent_id], self.agent_start_positions[agent_id])

    def test_reset_all_agents(self):
        """Test resetting all agents' positions."""
        # Move agent1 and agent2
        self.grid_world.step("agent1", "S")
        self.grid_world.step("agent2", "S")
        self.grid_world.step("agent3", "N") # agent3 started at (5,5)

        self.assertNotEqual(self.grid_world.agent_positions["agent1"], self.agent_start_positions["agent1"])
        self.assertNotEqual(self.grid_world.agent_positions["agent2"], self.agent_start_positions["agent2"])
        self.assertNotEqual(self.grid_world.agent_positions["agent3"], (5,5)) # original start for agent3 via add_agent

        # Reset all
        self.grid_world.reset()
        self.assertEqual(self.grid_world.agent_positions["agent1"], self.agent_start_positions["agent1"])
        self.assertEqual(self.grid_world.agent_positions["agent2"], self.agent_start_positions["agent2"])
        self.assertEqual(self.grid_world.agent_positions["agent3"], (5,5)) # Check it resets to its defined start pos

    def test_is_done(self):
        """Test the is_done method (currently always False)."""
        self.assertFalse(self.grid_world.is_done("agent1"))

    def test_invalid_start_position_fallback(self):
        """Test agent placement fallback if start position is a wall."""
        gw_bad_start = GridWorld(width=3, height=1, walls=[(1,0)], agent_start_positions={"a1": (1,0)})
        # (1,0) is a wall. Agent "a1" should be placed at a fallback, e.g., (0,0) or first available (0,0) then (2,0)
        self.assertNotEqual(gw_bad_start.agent_positions["a1"], (1,0))
        self.assertTrue(gw_bad_start.agent_positions["a1"] == (0,0) or gw_bad_start.agent_positions["a1"] == (2,0))
        self.assertEqual(gw_bad_start.grid[gw_bad_start.agent_positions["a1"][1]][gw_bad_start.agent_positions["a1"][0]], 0) # Must be on empty cell

    def test_no_valid_cells_for_agent(self):
        """Test scenario where no valid cell exists for an agent."""
        with self.assertRaises(Exception):
            GridWorld(width=1, height=1, walls=[(0,0)], agent_start_positions={"a1": (0,0)})

    def test_rewards_and_done_at_goal(self):
        """Test reward and done flag when agent reaches the goal."""
        agent_id = "agent1"
        # Manually place agent next to goal for a direct move
        # Goal is (9,7)
        self.grid_world.agent_positions[agent_id] = (self.goal_pos[0] - 1, self.goal_pos[1]) # (8,7)
        self.grid_world.agent_start_positions[agent_id] = (self.goal_pos[0] - 1, self.goal_pos[1]) # Update start for consistency if reset happens

        obs, reward, done, info = self.grid_world.step(agent_id, "E") # Move to goal (9,7)

        self.assertEqual(self.grid_world.agent_positions[agent_id], self.goal_pos)
        self.assertEqual(reward, 10.0, "Reward should be +10.0 for reaching goal.")
        self.assertTrue(done, "Done should be True when goal is reached.")

    def test_rewards_for_wall_hit(self):
        """Test reward for hitting a wall."""
        agent_id = "agent2" # Starts at (1,1)
        # Wall at (2,2)
        self.grid_world.agent_positions[agent_id] = (2,1) # Position agent next to wall (2,2)
        self.grid_world.agent_start_positions[agent_id] = (2,1)

        obs, reward, done, info = self.grid_world.step(agent_id, "S") # Attempt to move into wall (2,2)

        self.assertEqual(self.grid_world.agent_positions[agent_id], (2,1)) # Position should not change
        self.assertEqual(reward, -1.0, "Reward should be -1.0 for hitting a wall.")
        self.assertFalse(done, "Done should be False if wall hit and not at goal.")

    def test_rewards_for_boundary_hit(self):
        """Test reward for hitting a boundary."""
        agent_id = "agent1" # Starts at (0,0) by default in setUp or after reset
        self.grid_world.reset(agent_id) # Ensure agent1 is at (0,0)

        obs, reward, done, info = self.grid_world.step(agent_id, "N") # Attempt to move North from (0,0)

        self.assertEqual(self.grid_world.agent_positions[agent_id], (0,0)) # Position should not change
        self.assertEqual(reward, -1.0, "Reward should be -1.0 for hitting a boundary.")
        self.assertFalse(done, "Done should be False if boundary hit.")

    def test_rewards_for_normal_move(self):
        """Test reward for a valid move not reaching the goal."""
        agent_id = "agent1" # Starts at (0,0)
        self.grid_world.reset(agent_id)

        # Ensure this move does not land on the goal
        next_pos = (0,1)
        if next_pos == self.goal_pos: # If goal is (0,1) in a tiny grid, this test needs adjustment
            self.skipTest("Goal position interferes with normal move test, try larger grid or different goal for this test.")

        obs, reward, done, info = self.grid_world.step(agent_id, "S") # Move to (0,1)

        self.assertEqual(self.grid_world.agent_positions[agent_id], next_pos)
        self.assertEqual(reward, -0.1, "Reward should be -0.1 for a normal valid move.")
        self.assertFalse(done, "Done should be False for a normal move not reaching goal.")

    def test_rewards_for_stay_action(self):
        """Test reward for 'Stay' action when not at goal."""
        agent_id = "agent1"
        self.grid_world.reset(agent_id) # agent1 at (0,0)

        if (0,0) == self.goal_pos:
             self.skipTest("Agent starts at goal, cannot test 'Stay' reward for non-goal state.")

        obs, reward, done, info = self.grid_world.step(agent_id, "Stay")
        self.assertEqual(self.grid_world.agent_positions[agent_id], (0,0))
        self.assertEqual(reward, -0.05, "Reward should be -0.05 for 'Stay' action when not at goal.")
        self.assertFalse(done)


    def test_is_done_method(self):
        """Explicitly test the is_done() method."""
        agent_id = "agent1"
        self.grid_world.reset(agent_id)
        self.assertFalse(self.grid_world.is_done(agent_id), "is_done should be False when not at goal.")

        # Move agent to goal
        self.grid_world.agent_positions[agent_id] = self.goal_pos
        self.assertTrue(self.grid_world.is_done(agent_id), "is_done should be True when at goal.")

        # Move agent away from goal
        self.grid_world.agent_positions[agent_id] = (0,0)
        self.assertFalse(self.grid_world.is_done(agent_id), "is_done should be False when moved away from goal.")

        # Test with an agent ID not in agent_positions (should be False)
        self.assertFalse(self.grid_world.is_done("unknown_agent"), "is_done should be False for unknown agent.")


if __name__ == '__main__':
    unittest.main()
