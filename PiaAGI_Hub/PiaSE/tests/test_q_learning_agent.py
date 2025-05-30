import unittest
import os
import sys
import random

# Adjust sys.path to allow imports from PiaAGI_Hub
current_dir = os.path.dirname(os.path.abspath(__file__))
piase_dir = os.path.dirname(current_dir)  # PiaAGI_Hub/PiaSE/
piaagi_hub_dir = os.path.dirname(piase_dir)  # PiaAGI_Hub/
project_root_dir = os.path.dirname(piaagi_hub_dir)  # /app (parent of PiaAGI_Hub)

if project_root_dir not in sys.path:
    sys.path.insert(0, project_root_dir)

from PiaAGI_Hub.PiaSE.agents.q_learning_agent import QLearningAgent
from PiaAGI_Hub.PiaSE.core_engine.interfaces import PiaSEEvent
# from PiaAGI_Hub.PiaSE.environments.grid_world import GridWorld # For more complex state tests if needed

class TestQLearningAgent(unittest.TestCase):
    def setUp(self):
        self.action_space = ["N", "S", "E", "W", "Stay"]
        self.agent = QLearningAgent(
            learning_rate=0.1,
            discount_factor=0.9,
            exploration_rate=0.1,
            default_q_value=0.0
        )
        self.agent.set_id("test_q_agent")
        # It's important that action_space is set for most tests.
        # initialize_q_table sets it, or perceive can if action_space is already known and state is new.
        # For many tests, we'll call initialize_q_table with a dummy state.
        self.agent.initialize_q_table("dummy_initial_state", self.action_space)


    def test_initialization(self):
        self.assertEqual(self.agent.lr, 0.1)
        self.assertEqual(self.agent.gamma, 0.9)
        self.assertEqual(self.agent.epsilon, 0.1)
        self.assertEqual(self.agent.default_q, 0.0)
        self.assertEqual(self.agent.q_table, {"dummy_initial_state": {action: 0.0 for action in self.action_space}})
        self.assertIsNotNone(self.agent.q_table)

    def test_set_and_get_id(self):
        self.assertEqual(self.agent.get_id(), "test_q_agent")
        self.agent.set_id("new_id")
        self.assertEqual(self.agent.get_id(), "new_id")

    def test_initialize_q_table_and_action_space(self):
        state1 = "state1"
        self.agent.initialize_q_table(state1, self.action_space)
        self.assertIn(state1, self.agent.q_table)
        self.assertEqual(self.agent.q_table[state1], {action: 0.0 for action in self.action_space})
        self.assertEqual(self.agent.action_space, self.action_space)

        # Test that it doesn't overwrite existing different actions for the same state
        # (though current implementation re-initializes all actions for the state)
        self.agent.q_table[state1]["N"] = 5.0
        self.agent.initialize_q_table(state1, self.action_space) # Should re-init
        self.assertEqual(self.agent.q_table[state1]["N"], 0.0)


    def test_get_q_value_uninitialized_state(self):
        state_new = "new_state"
        action = "N"
        # Action space must be known for initialization to occur within get_q_value
        self.assertTrue(len(self.agent.action_space) > 0, "Agent action space should be set for this test.")

        q_value = self.agent.get_q_value(state_new, action)
        self.assertEqual(q_value, self.agent.default_q)
        self.assertIn(state_new, self.agent.q_table) # State should now be initialized
        self.assertEqual(self.agent.q_table[state_new], {act: self.agent.default_q for act in self.action_space})

    def test_update_q_value(self):
        state_s = "s1"
        action_a = "E"
        reward_r = 1.0
        next_state_s_prime = "s2"

        # Initialize s1 and s2 to ensure they exist with default values
        self.agent.initialize_q_table(state_s, self.action_space)
        self.agent.initialize_q_table(next_state_s_prime, self.action_space)

        # Manually set Q(s2, any_action) to make max_future_q predictable for test
        # Let's say Q(s2, "N") = 0.5 is the max
        self.agent.q_table[next_state_s_prime]["N"] = 0.5
        max_future_q = 0.5

        current_q_s_a = self.agent.get_q_value(state_s, action_a) # Should be default_q (0.0)

        self.agent.update_q_value(state_s, action_a, reward_r, next_state_s_prime,
                                  self.agent.lr, self.agent.gamma, self.action_space)

        expected_new_q = current_q_s_a + self.agent.lr * (reward_r + self.agent.gamma * max_future_q - current_q_s_a)
        self.assertAlmostEqual(self.agent.q_table[state_s][action_a], expected_new_q)

    def test_update_q_value_next_state_new(self):
        """Test Q-update when next_state is entirely new."""
        state_s = "s_current"
        action_a = "N"
        reward_r = 0.5
        next_state_s_prime_new = "s_brand_new" # This state is not in q_table yet

        self.agent.initialize_q_table(state_s, self.action_space)
        current_q_s_a = self.agent.get_q_value(state_s, action_a) # default 0.0

        # update_q_value should initialize s_brand_new
        self.agent.update_q_value(state_s, action_a, reward_r, next_state_s_prime_new,
                                  self.agent.lr, self.agent.gamma, self.action_space)

        # For a new next_state, max_future_q will be 0 (as all its actions have default_q 0.0)
        max_future_q = 0.0
        expected_new_q = current_q_s_a + self.agent.lr * (reward_r + self.agent.gamma * max_future_q - current_q_s_a)
        self.assertAlmostEqual(self.agent.q_table[state_s][action_a], expected_new_q)
        self.assertIn(next_state_s_prime_new, self.agent.q_table) # Check it was initialized


    def test_perceive(self):
        obs_dict = {"agent_position": (1,1), "grid_view": "mock_grid"}
        hashable_state = (1,1) # as per _get_hashable_state

        self.agent.perceive(obs_dict)
        self.assertEqual(self.agent.current_state, hashable_state)
        self.assertIn(hashable_state, self.agent.q_table)

        # Test perceive with a simple hashable observation
        obs_simple = "simple_state"
        self.agent.perceive(obs_simple)
        self.assertEqual(self.agent.current_state, obs_simple)
        self.assertIn(obs_simple, self.agent.q_table)

    def test_act_exploration(self):
        self.agent.epsilon = 1.0 # Force exploration
        self.agent.perceive("some_state_for_exploration") # Ensure current_state is not None
        chosen_actions = set()
        for _ in range(100): # Run multiple times
            action = self.agent.act()
            self.assertIn(action, self.action_space)
            chosen_actions.add(action)
        # Check if more than one action was chosen (probabilistic, but likely for 100 runs)
        self.assertTrue(len(chosen_actions) > 1, "Exploration should pick various actions.")


    def test_act_exploitation(self):
        self.agent.epsilon = 0.0 # Force exploitation
        state_exploit = "exploit_state"
        self.agent.initialize_q_table(state_exploit, self.action_space)
        self.agent.q_table[state_exploit]["N"] = 0.1
        self.agent.q_table[state_exploit]["S"] = 0.5 # Best action
        self.agent.q_table[state_exploit]["E"] = 0.2

        self.agent.perceive(state_exploit)
        action = self.agent.act()
        self.assertEqual(action, "S")

        # Test random choice among equally best actions
        self.agent.q_table[state_exploit]["W"] = 0.5 # Now S and W are equally best
        chosen_actions = set()
        for _ in range(50): # Multiple calls
            chosen_actions.add(self.agent.act())
        self.assertIn("S", chosen_actions)
        self.assertIn("W", chosen_actions)
        self.assertTrue(len(chosen_actions) <= 2) # Should only pick S or W


    def test_act_uninitialized_state(self):
        self.agent.epsilon = 0.0 # Force exploitation, but on new state it should init
        new_state_for_act = "new_state_for_act"
        self.agent.perceive(new_state_for_act) # This sets current_state and initializes it in Q-table

        self.assertIn(new_state_for_act, self.agent.q_table) # Should be initialized by perceive
        action = self.agent.act()
        self.assertIn(action, self.action_space) # Since all Q-values are default, it will pick randomly among them.

    def test_learn_method(self):
        # This tests if learn correctly calls update_q_value and changes Q-table
        # The sequence: perceive(S) -> act() -> learn((R,S')) -> perceive(S')
        state_s0 = "learn_s0"
        state_s1 = "learn_s1"

        # 1. Agent is in s0
        self.agent.perceive(state_s0) # Sets current_state to s0, initializes q_table[s0]
        self.assertTrue(self.agent.current_state == state_s0)

        # 2. Agent takes action (let's force one for predictability if epsilon is high)
        # Or rely on epsilon-greedy. Let's assume an action is taken.
        action_a0 = self.agent.act() # last_action is set to a0
        self.assertTrue(self.agent.last_action == action_a0)

        # 3. Environment gives reward and next state S'
        reward_r0 = 0.75

        # Initial Q(s0, a0) should be default (0.0)
        initial_q_s0_a0 = self.agent.get_q_value(state_s0, action_a0)
        self.assertEqual(initial_q_s0_a0, 0.0)

        # 4. Agent learns. learn uses self.current_state (s0) and self.last_action (a0)
        # and the feedback (reward_r0, state_s1)
        self.agent.learn((reward_r0, state_s1))

        # Check if Q(s0,a0) was updated
        # max_future_q for s1 will be 0 as s1 is new or has default values
        expected_q_s0_a0 = 0.0 + self.agent.lr * (reward_r0 + self.agent.gamma * 0.0 - 0.0)
        self.assertAlmostEqual(self.agent.q_table[state_s0][action_a0], expected_q_s0_a0)
        self.assertIn(state_s1, self.agent.q_table) # s1 should have been initialized by update_q_value


    def test_get_hashable_state(self):
        # Test with dict observation (GridWorld style)
        obs_dict = {"agent_position": (2,3), "grid_view": [[0,0],[0,1]]}
        self.assertEqual(self.agent._get_hashable_state(obs_dict), (2,3))

        # Test with simple tuple
        obs_tuple = (2,3)
        self.assertEqual(self.agent._get_hashable_state(obs_tuple), (2,3))

        # Test with string
        obs_str = "state_name"
        self.assertEqual(self.agent._get_hashable_state(obs_str), "state_name")

        # Test with list (should be converted to tuple)
        obs_list = [1, 2, "a"]
        self.assertEqual(self.agent._get_hashable_state(obs_list), (1, 2, "a"))

        # Test with more complex dict (should be converted to tuple of sorted items)
        obs_complex_dict = {"y": 1, "x":0, "name": "A"}
        self.assertEqual(self.agent._get_hashable_state(obs_complex_dict), (('name', 'A'), ('x',0), ('y',1)))


if __name__ == '__main__':
    unittest.main()
