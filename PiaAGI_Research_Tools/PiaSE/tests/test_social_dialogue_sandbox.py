import unittest
import time
from typing import Dict, Any, List, Optional, Tuple

# Adjust imports to reach the PiaSE components from the tests directory
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PiaSE.core_engine.interfaces import PerceptionData, ActionCommand, ActionResult, TextualPercept
from PiaSE.environments.social_dialogue_sandbox import SocialDialogueSandbox, SimulatedInteractorProfile

class TestSocialDialogueSandbox(unittest.TestCase):

    def setUp(self):
        self.pia_agent_id = "PiaTestAgent"
        self.npc_agent_id_1 = "NPC_Alice"
        self.npc_agent_id_2 = "NPC_Bob"

        self.default_dialogue_config = {"topic": "General Test Chat", "max_turns": 10}

        self.npc_alice_profile_config = {
            "response_rules": {"hello": "Hi from Alice!", "weather": "Alice says it's sunny."},
            "default_response": "Alice ponders.",
            "personality_traits": {"openness": 0.8, "conscientiousness": 0.4},
            "current_simulated_emotion": "curious",
            "npc_goals": ["learn_about_Pia", "share_weather_info"]
        }
        self.npc_bob_profile_config = {
            "response_rules": {"hello": "Bob here, hello!", "food": "Bob likes pizza."},
            "default_response": "Bob nods.",
            "personality_traits": {"agreeableness": 0.9, "neuroticism": 0.2},
            "current_simulated_emotion": "calm",
            "npc_goals": ["be_friendly"]
        }

    def test_initialization_with_npc_profiles(self):
        agent_ids = [self.pia_agent_id, self.npc_agent_id_1, self.npc_agent_id_2]
        sim_configs = {
            self.npc_agent_id_1: self.npc_alice_profile_config,
            self.npc_agent_id_2: self.npc_bob_profile_config
        }
        env = SocialDialogueSandbox(
            dialogue_config=self.default_dialogue_config,
            agent_ids=agent_ids,
            simulated_interactor_configs=sim_configs
        )

        self.assertListEqual(env.all_agent_ids, agent_ids)
        self.assertEqual(env.dialogue_config, self.default_dialogue_config)
        self.assertIn(self.npc_agent_id_1, env.simulated_interactors)
        self.assertIn(self.npc_agent_id_2, env.simulated_interactors)

        alice_profile = env.simulated_interactors[self.npc_agent_id_1]
        self.assertEqual(alice_profile.interactor_id, self.npc_agent_id_1)
        self.assertEqual(alice_profile.personality_traits, self.npc_alice_profile_config["personality_traits"])
        self.assertEqual(alice_profile.current_simulated_emotion, self.npc_alice_profile_config["current_simulated_emotion"])
        self.assertEqual(alice_profile.npc_goals, self.npc_alice_profile_config["npc_goals"])
        self.assertEqual(alice_profile.response_rules["weather"], "Alice says it's sunny.")

    def test_reset_and_initial_npc_utterance(self):
        # NPC Alice starts first
        agent_ids = [self.npc_agent_id_1, self.pia_agent_id]
        sim_configs = {self.npc_agent_id_1: self.npc_alice_profile_config}
        env = SocialDialogueSandbox(
            dialogue_config=self.default_dialogue_config,
            agent_ids=agent_ids,
            simulated_interactor_configs=sim_configs
        )

        initial_perception = env.reset()

        self.assertEqual(len(env.dialogue_history), 1)
        self.assertEqual(env.dialogue_history[0]["speaker_id"], self.npc_agent_id_1)
        self.assertIn(env.dialogue_history[0]["utterance"], [
            self.npc_alice_profile_config["response_rules"].get("greeting"), # "Hello! I'm Alice."
            f"Hello, I'm {self.npc_agent_id_1}." # Default greeting from SimulatedInteractorProfile
        ])

        self.assertEqual(env.current_turn_holder, self.pia_agent_id) # Turn advanced to Pia
        self.assertIsNotNone(initial_perception)
        self.assertTrue(initial_perception.custom_sensor_data["is_my_turn"])
        self.assertEqual(initial_perception.custom_sensor_data["current_turn_holder"], self.pia_agent_id)

    def test_reset_agent_starts_first(self):
        agent_ids = [self.pia_agent_id, self.npc_agent_id_1]
        sim_configs = {self.npc_agent_id_1: self.npc_alice_profile_config}
        env = SocialDialogueSandbox(
            dialogue_config=self.default_dialogue_config,
            agent_ids=agent_ids,
            simulated_interactor_configs=sim_configs
        )
        initial_perception = env.reset()

        self.assertEqual(len(env.dialogue_history), 0) # PiaAGI starts, so no initial NPC utterance
        self.assertEqual(env.current_turn_holder, self.pia_agent_id)
        self.assertIsNotNone(initial_perception)
        self.assertTrue(initial_perception.custom_sensor_data["is_my_turn"])
        self.assertEqual(initial_perception.textual_percepts[0].text, "The dialogue has just begun. It's your turn.")

    def test_get_observation_content(self):
        agent_ids = [self.pia_agent_id, self.npc_agent_id_1]
        sim_configs = {self.npc_agent_id_1: self.npc_alice_profile_config}
        env = SocialDialogueSandbox(
            dialogue_config=self.default_dialogue_config,
            agent_ids=agent_ids,
            simulated_interactor_configs=sim_configs
        )
        env.reset() # Pia's turn

        # Manually add history: Pia speaks, then NPC speaks
        env.dialogue_history.append({"speaker_id": self.pia_agent_id, "utterance": "Hello Alice!"})
        env.dialogue_history.append({"speaker_id": self.npc_agent_id_1, "utterance": "Hi from Alice!"})
        env.current_turn_holder = self.pia_agent_id # Set turn back to Pia for observation

        observation = env.get_observation(self.pia_agent_id)

        self.assertEqual(observation.textual_percepts[0].text, "Hi from Alice!")
        self.assertEqual(observation.textual_percepts[0].source, self.npc_agent_id_1)
        self.assertTrue(observation.custom_sensor_data["is_my_turn"])

        npc_state = observation.custom_sensor_data["simulated_npc_state_conceptual"]
        self.assertIsNotNone(npc_state)
        self.assertEqual(npc_state["personality"], self.npc_alice_profile_config["personality_traits"])
        self.assertEqual(npc_state["emotion"], self.npc_alice_profile_config["current_simulated_emotion"])
        self.assertEqual(npc_state["goals"], self.npc_alice_profile_config["npc_goals"])

    def test_step_speak_action_agent_then_npc(self):
        agent_ids = [self.pia_agent_id, self.npc_agent_id_1]
        sim_configs = {self.npc_agent_id_1: self.npc_alice_profile_config}
        env = SocialDialogueSandbox(
            dialogue_config=self.default_dialogue_config,
            agent_ids=agent_ids,
            simulated_interactor_configs=sim_configs
        )
        env.reset() # Pia's turn

        action = ActionCommand(action_type="speak", parameters={"utterance": "Hello"})
        result = env.step(self.pia_agent_id, action)

        self.assertEqual(result.status, "success")
        self.assertEqual(len(env.dialogue_history), 2) # Pia's "Hello" + Alice's "Hi from Alice!"
        self.assertEqual(env.dialogue_history[0]["speaker_id"], self.pia_agent_id)
        self.assertEqual(env.dialogue_history[0]["utterance"], "Hello")
        self.assertEqual(env.dialogue_history[1]["speaker_id"], self.npc_agent_id_1)
        self.assertEqual(env.dialogue_history[1]["utterance"], "Hi from Alice!")
        self.assertEqual(env.current_turn_holder, self.pia_agent_id) # Turn returns to Pia

    def test_step_listen_action_agent_then_npc(self):
        agent_ids = [self.pia_agent_id, self.npc_agent_id_1]
        sim_configs = {self.npc_agent_id_1: self.npc_alice_profile_config}
        env = SocialDialogueSandbox(
            dialogue_config=self.default_dialogue_config,
            agent_ids=agent_ids,
            simulated_interactor_configs=sim_configs
        )
        env.reset() # Pia's turn

        action = ActionCommand(action_type="listen", parameters={})
        result = env.step(self.pia_agent_id, action)

        self.assertEqual(result.status, "success")
        self.assertEqual(len(env.dialogue_history), 1) # Only NPC's response to implied silence/previous state
        self.assertEqual(env.dialogue_history[0]["speaker_id"], self.npc_agent_id_1)
        # NPC responds to "last_real_utterance" which is "" if Pia just listened after reset.
        # So NPC gives its greeting.
        self.assertEqual(env.dialogue_history[0]["utterance"], self.npc_alice_profile_config["response_rules"]["greeting"])
        self.assertEqual(env.current_turn_holder, self.pia_agent_id)

    def test_step_wrong_turn(self):
        agent_ids = [self.npc_agent_id_1, self.pia_agent_id] # NPC starts
        sim_configs = {self.npc_agent_id_1: self.npc_alice_profile_config}
        env = SocialDialogueSandbox(
            dialogue_config=self.default_dialogue_config,
            agent_ids=agent_ids,
            simulated_interactor_configs=sim_configs
        )
        env.reset() # NPC speaks, turn is Pia's

        self.assertEqual(env.current_turn_holder, self.pia_agent_id)

        action = ActionCommand(action_type="speak", parameters={"utterance": "My turn yet?"})
        # NPC_Alice tries to speak when it's PiaTestAgent's turn
        result = env.step(self.npc_agent_id_1, action)

        self.assertEqual(result.status, "failure")
        self.assertIn("not agent NPC_Alice's turn", result.message)
        self.assertEqual(len(env.dialogue_history), 1) # Only NPC's initial utterance
        self.assertEqual(env.current_turn_holder, self.pia_agent_id) # Turn unchanged

    def test_npc_response_logic(self):
        agent_ids = [self.pia_agent_id, self.npc_agent_id_1]
        sim_configs = {self.npc_agent_id_1: self.npc_alice_profile_config}
        env = SocialDialogueSandbox(
            dialogue_config=self.default_dialogue_config,
            agent_ids=agent_ids,
            simulated_interactor_configs=sim_configs
        )
        env.reset() # Pia's turn

        # Test specific rule
        action1 = ActionCommand(action_type="speak", parameters={"utterance": "How is the weather, Alice?"})
        env.step(self.pia_agent_id, action1)
        self.assertEqual(env.dialogue_history[-1]["utterance"], "Alice says it's sunny.")

        # Test default response
        action2 = ActionCommand(action_type="speak", parameters={"utterance": "Tell me about philosophy."})
        env.step(self.pia_agent_id, action2)
        self.assertEqual(env.dialogue_history[-1]["utterance"], "Alice ponders.")

    def test_is_done_termination(self):
        # Test 1: max_turns
        short_dialogue_config = {"topic": "MaxTurnsTest", "max_turns": 1} # 1 exchange means 2 history entries
        agent_ids = [self.pia_agent_id, self.npc_agent_id_1]
        sim_configs = {self.npc_agent_id_1: self.npc_alice_profile_config}
        env = SocialDialogueSandbox(
            dialogue_config=short_dialogue_config,
            agent_ids=agent_ids,
            simulated_interactor_configs=sim_configs
        )
        env.reset()
        self.assertFalse(env.is_done())
        env.step(self.pia_agent_id, ActionCommand(action_type="speak", parameters={"utterance": "First turn"})) # Pia speaks, NPC responds
        self.assertEqual(len(env.dialogue_history), 2)
        self.assertTrue(env.is_done(), f"History length: {len(env.dialogue_history)}")

        # Test 2: goodbye keyword
        env = SocialDialogueSandbox(
            dialogue_config=self.default_dialogue_config, # Default max_turns is higher
            agent_ids=agent_ids,
            simulated_interactor_configs=sim_configs
        )
        env.reset()
        self.assertFalse(env.is_done())
        env.step(self.pia_agent_id, ActionCommand(action_type="speak", parameters={"utterance": "Okay, goodbye!"}))
        self.assertTrue(env.is_done())

    def test_get_action_space(self):
        agent_ids = [self.pia_agent_id, self.npc_agent_id_1]
        env = SocialDialogueSandbox(
            dialogue_config=self.default_dialogue_config,
            agent_ids=agent_ids,
            simulated_interactor_configs={self.npc_agent_id_1: self.npc_alice_profile_config}
        )
        env.reset() # Pia's turn

        pia_actions = env.get_action_space(self.pia_agent_id)
        self.assertEqual(len(pia_actions), 2)
        self.assertIn("speak", [a["action_type"] for a in pia_actions])
        self.assertIn("listen", [a["action_type"] for a in pia_actions])

        npc_actions = env.get_action_space(self.npc_agent_id_1)
        self.assertEqual(len(npc_actions), 0) # Not NPC's turn initially

        # Advance turn to NPC
        env.step(self.pia_agent_id, ActionCommand(action_type="listen", parameters={}))
        self.assertEqual(env.current_turn_holder, self.pia_agent_id) # NPC responded, turn is back to Pia

        # If we manually set turn to NPC (not standard flow, but for testing get_action_space)
        env.current_turn_holder = self.npc_agent_id_1
        npc_actions_now = env.get_action_space(self.npc_agent_id_1)
        self.assertEqual(len(npc_actions_now), 2) # NPCs also technically have same action space

    def test_get_environment_info(self):
        env = SocialDialogueSandbox(
            dialogue_config=self.default_dialogue_config,
            agent_ids=[self.pia_agent_id],
            simulated_interactor_configs={}
        )
        info = env.get_environment_info()
        self.assertEqual(info["environment_name"], "SocialDialogueSandbox_v0.1")
        self.assertIn("turn-based dialogue interactions", info["description"])
        self.assertIn("simulated_npc_state_conceptual", info["perception_schema"]["custom_sensor_data"])
        self.assertIn("speak", info["action_schema"])

    def test_get_state(self):
        env = SocialDialogueSandbox(
            dialogue_config=self.default_dialogue_config,
            agent_ids=[self.pia_agent_id, self.npc_agent_id_1],
            simulated_interactor_configs={self.npc_agent_id_1: self.npc_alice_profile_config}
        )
        env.reset()
        env.step(self.pia_agent_id, ActionCommand(action_type="speak", parameters={"utterance": "Test state"}))

        state = env.get_state()
        self.assertEqual(state["dialogue_config"], self.default_dialogue_config)
        self.assertEqual(len(state["dialogue_history"]), 2)
        self.assertEqual(state["turn_index"], 0) # Back to Pia after NPC response
        self.assertEqual(state["current_turn_holder"], self.pia_agent_id)
        self.assertEqual(state["simulated_interactor_configs_count"], 1)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
