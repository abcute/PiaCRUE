import unittest
import os
import sys

# Adjust sys.path to allow imports from PiaAGI_Hub
current_dir = os.path.dirname(os.path.abspath(__file__))
piase_dir = os.path.dirname(current_dir)  # PiaAGI_Hub/PiaSE/
piaagi_hub_dir = os.path.dirname(piase_dir)  # PiaAGI_Hub/
project_root_dir = os.path.dirname(piaagi_hub_dir)  # /app (parent of PiaAGI_Hub)

if project_root_dir not in sys.path:
    sys.path.insert(0, project_root_dir)

from PiaAGI_Hub.PiaSE.agents.basic_grid_agent import BasicGridAgent
from PiaAGI_Hub.PiaSE.core_engine.interfaces import PiaSEEvent
# from PiaAGI_Hub.PiaSE.environments.grid_world import GridWorld # Potentially for context

class TestBasicGridAgent(unittest.TestCase):
    def setUp(self):
        """Set up common BasicGridAgent instances."""
        self.random_agent = BasicGridAgent(policy="random")
        self.random_agent.set_id("RandomTestAgent")

        self.goal_pos = (5, 5)
        self.goal_oriented_agent = BasicGridAgent(policy="goal_oriented", goal=self.goal_pos)
        self.goal_oriented_agent.set_id("GoalTestAgent")
        
        self.valid_actions = ["N", "S", "E", "W", "Stay"]

    def test_initialization(self):
        """Test agent initialization."""
        self.assertEqual(self.random_agent.policy, "random")
        self.assertIsNone(self.random_agent.goal)
        self.assertEqual(self.random_agent.get_id(), "RandomTestAgent")

        self.assertEqual(self.goal_oriented_agent.policy, "goal_oriented")
        self.assertEqual(self.goal_oriented_agent.goal, self.goal_pos)
        self.assertEqual(self.goal_oriented_agent.get_id(), "GoalTestAgent")
        
        # Test warning for goal_oriented without goal
        no_goal_agent = BasicGridAgent(policy="goal_oriented") # Should print warning
        self.assertEqual(no_goal_agent.policy, "goal_oriented") # Policy remains
        self.assertIsNone(no_goal_agent.goal) # Goal is None


    def test_id_management(self):
        """Test set_id and get_id methods."""
        agent = BasicGridAgent()
        self.assertEqual(agent.get_id(), "UnnamedAgent") # Default ID
        agent.set_id("TestID123")
        self.assertEqual(agent.get_id(), "TestID123")

    def test_perceive(self):
        """Test if agent stores observation and handles events."""
        observation_data = {"agent_position": (1, 1), "grid_view": [[0]]}
        self.random_agent.perceive(observation_data)
        self.assertEqual(self.random_agent.current_observation, observation_data)

        event_data = PiaSEEvent() # Generic event
        # We can't easily check print output here without mocking stdout,
        # but we can ensure it runs without error.
        self.random_agent.perceive(observation_data, event=event_data)
        self.assertEqual(self.random_agent.current_observation, observation_data)


    def test_action_selection_random(self):
        """Test random action selection."""
        # Provide a mock observation, as act() might use it
        mock_obs = {"agent_position": (0,0)}
        self.random_agent.perceive(mock_obs)
        for _ in range(20): # Run a few times to increase chance of seeing all actions
            action = self.random_agent.act()
            self.assertIn(action, self.valid_actions)

    def test_action_selection_goal_oriented(self):
        """Test goal-oriented action selection."""
        # Agent goal is (5,5)
        test_cases = {
            # current_pos: expected_dominant_action (can be multiple if equidistant)
            (0,0): ["E", "S"], # Towards (5,5), E or S are primary moves
            (5,2): ["S"],       # Directly North of goal
            (2,5): ["E"],       # Directly West of goal
            (5,8): ["N"],       # Directly South of goal
            (8,5): ["W"],       # Directly East of goal
            (4,4): ["E","S"],   # Diagonal, E or S
            (6,6): ["W","N"],   # Diagonal, W or N
            (5,5): ["Stay"]     # At goal
        }

        for current_pos, expected_actions in test_cases.items():
            mock_obs = {"agent_position": current_pos, "grid_view": [[]]} # Grid view not used by basic agent
            self.goal_oriented_agent.perceive(mock_obs)
            action = self.goal_oriented_agent.act()
            self.assertIn(action, expected_actions, 
                          f"For pos {current_pos} to goal {self.goal_pos}, action {action} not in {expected_actions}")
            
    def test_action_selection_goal_oriented_no_goal(self):
        """Test goal-oriented agent acts randomly if no goal is set."""
        agent = BasicGridAgent(policy="goal_oriented", goal=None)
        agent.set_id("NoGoalAgent")
        agent.perceive({"agent_position": (0,0)})
        for _ in range(10):
            action = agent.act()
            self.assertIn(action, self.valid_actions)

    def test_action_selection_no_observation(self):
        """Test agent acts randomly if no observation has been perceived."""
        agent = BasicGridAgent()
        agent.set_id("NoObsAgent")
        # Agent has no self.current_observation
        for _ in range(10):
            action = agent.act()
            self.assertIn(action, self.valid_actions)
            
    def test_action_selection_bad_observation(self):
        """Test agent acts randomly if observation format is unexpected."""
        agent = BasicGridAgent()
        agent.set_id("BadObsAgent")
        
        # Missing 'agent_position'
        agent.perceive(observation={"grid_only": [[]]}) 
        for _ in range(5):
            action = agent.act()
            self.assertIn(action, self.valid_actions)

        # Not a dict
        agent.perceive(observation="This is not a dict")
        for _ in range(5):
            action = agent.act()
            self.assertIn(action, self.valid_actions)


    def test_learn(self):
        """Test the learn method (currently just prints)."""
        # We can't easily check print output here without mocking stdout,
        # but we can ensure it runs without error.
        self.random_agent.learn("Test feedback")
        self.goal_oriented_agent.learn({"reward": 10, "new_state": "some_state"})
        # Should not raise any errors


if __name__ == '__main__':
    unittest.main()
