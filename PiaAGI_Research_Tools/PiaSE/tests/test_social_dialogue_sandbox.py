import unittest
import time # For timestamp comparisons if needed, though often mocked or ignored in unit tests

# Adjust relative imports based on actual file structure
try:
    from ..environments.social_dialogue_sandbox import SocialDialogueSandbox, SimulatedInteractorProfile
    from ..core_engine.interfaces import ActionCommand, PerceptionData, TextualPercept, ActionResult
except ImportError:
    # Minimal placeholders if direct import fails (e.g. running script standalone)
    # This setup is more for local testing of the test script itself.
    # For CI/CD, ensure paths are correctly handled via PYTHONPATH.
    print("Warning: TestSocialDialogueSandbox using placeholder imports. Ensure correct PYTHONPATH for full testing.")
    class BaseDataModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        def model_dump_json(self, indent=None): # Pydantic v2 compatibility
            import json
            return json.dumps(self.__dict__, indent=indent)


    class TextualPercept(BaseDataModel): pass
    class PerceptionData(BaseDataModel):
        def __init__(self, timestamp: float, textual_percepts: list = None, custom_sensor_data: dict = None, messages: list = None, **kwargs):
            super().__init__(timestamp=timestamp, textual_percepts=textual_percepts or [], custom_sensor_data=custom_sensor_data or {}, messages=messages or [], **kwargs)

    class ActionCommand(BaseDataModel): pass
    class ActionResult(BaseDataModel):
         def __init__(self, timestamp: float, status: str, message: str = "", new_perception_snippet=None, details=None, **kwargs):
            super().__init__(timestamp=timestamp, status=status, message=message, new_perception_snippet=new_perception_snippet, details=details or {}, **kwargs)

    class SimulatedInteractorProfile:
        def __init__(self, interactor_id: str, response_rules=None, default_response: str = "Hmm."):
            self.interactor_id = interactor_id
            self.response_rules = response_rules or {}
            self.default_response = default_response
        def generate_response(self, text: str) -> str:
            if not text: return self.response_rules.get("greeting", self.default_response)
            for keyword, response in self.response_rules.items():
                if keyword.lower() in text.lower():
                    return response
            return self.default_response

    class SocialDialogueSandbox:
        # Highly simplified placeholder matching some key aspects of the real one for tests to parse
        def __init__(self, dialogue_config, agent_ids, simulated_interactor_configs=None):
            self.dialogue_config = dialogue_config
            self.all_agent_ids = list(agent_ids)
            self.simulated_interactors = {}
            if simulated_interactor_configs:
                for agent_id, config in simulated_interactor_configs.items():
                    if agent_id in self.all_agent_ids:
                        self.simulated_interactors[agent_id] = SimulatedInteractorProfile(
                            interactor_id=agent_id,
                            response_rules=config.get("response_rules"),
                            default_response=config.get("default_response")
                        )
            self.reset()

        def reset(self):
            self.dialogue_history = []
            self.turn_index = 0
            self.current_turn_holder = self.all_agent_ids[0] if self.all_agent_ids else None

            # Simplified reset logic from actual implementation for placeholder
            if self.current_turn_holder and self.current_turn_holder in self.simulated_interactors:
                sim_interactor = self.simulated_interactors[self.current_turn_holder]
                initial_utterance = sim_interactor.generate_response("")
                self.dialogue_history.append({"speaker_id": self.current_turn_holder, "utterance": initial_utterance})
                self._advance_turn()

            if self.current_turn_holder:
                return self.get_observation(self.current_turn_holder)
            return None


        def get_observation(self, agent_id):
            text_percepts = []
            if not self.dialogue_history:
                text_percepts.append(TextualPercept(text="The dialogue has just begun. It's your turn.", source="system"))
            else:
                last_entry = self.dialogue_history[-1]
                text_percepts.append(TextualPercept(text=last_entry["utterance"], source=last_entry["speaker_id"]))

            return PerceptionData(
                timestamp=time.time(),
                textual_percepts=text_percepts,
                custom_sensor_data={
                    "is_my_turn": agent_id == self.current_turn_holder,
                    "current_turn_holder": self.current_turn_holder,
                    "participants": self.all_agent_ids,
                    "dialogue_topic": self.dialogue_config.get("topic")
                }
            )

        def _advance_turn(self):
            if not self.all_agent_ids: return
            self.turn_index = (self.turn_index + 1) % len(self.all_agent_ids)
            self.current_turn_holder = self.all_agent_ids[self.turn_index]

        def step(self, agent_id, action: ActionCommand):
            if agent_id != self.current_turn_holder:
                return ActionResult(timestamp=time.time(), status="failure", message=f"It's not agent {agent_id}'s turn.")

            if action.action_type == "speak":
                self.dialogue_history.append({"speaker_id": agent_id, "utterance": action.parameters["utterance"]})
                self._advance_turn()
                if self.current_turn_holder in self.simulated_interactors:
                    sim_resp = self.simulated_interactors[self.current_turn_holder].generate_response(action.parameters["utterance"])
                    self.dialogue_history.append({"speaker_id": self.current_turn_holder, "utterance": sim_resp})
                    self._advance_turn()
                return ActionResult(timestamp=time.time(), status="success", new_perception_snippet=self.get_observation(self.current_turn_holder) if self.current_turn_holder else None)
            elif action.action_type == "listen":
                self._advance_turn() # Agent listens, turn passes
                if self.current_turn_holder in self.simulated_interactors: # Sim agent auto-responds
                    sim_resp = self.simulated_interactors[self.current_turn_holder].generate_response("") # Responds to silence or generic
                    self.dialogue_history.append({"speaker_id": self.current_turn_holder, "utterance": sim_resp})
                    self._advance_turn()
                return ActionResult(timestamp=time.time(), status="success", new_perception_snippet=self.get_observation(self.current_turn_holder) if self.current_turn_holder else None)
            return ActionResult(timestamp=time.time(), status="failure", message="Unknown action")

        def get_environment_info(self): return {}
        def get_action_space(self, agent_id=None): return []
        def get_state(self): return {"history_len": len(self.dialogue_history)}
        def is_done(self, agent_id=None): return len(self.dialogue_history) >= self.dialogue_config.get("max_turns", 100) * len(self.all_agent_ids)


class TestSocialDialogueSandbox(unittest.TestCase):

    def setUp(self):
        self.agent1_id = "Alice"
        self.agent2_id = "Bob_Sim"
        self.agent_ids = [self.agent1_id, self.agent2_id] # Alice starts

        self.dialogue_config = {"topic": "Test Chat", "max_turns": 10}
        self.sim_configs = {
            self.agent2_id: {
                "response_rules": {
                    "hello": "Hi there, Alice!",
                    "weather": "It's fine, thanks for asking.",
                    "bye": "Goodbye, Alice!",
                    "greeting": f"I am {self.agent2_id}, ready to chat." # For when sim starts
                },
                "default_response": "That's interesting, Alice."
            }
        }
        self.env = SocialDialogueSandbox(
            dialogue_config=self.dialogue_config,
            agent_ids=self.agent_ids,
            simulated_interactor_configs=self.sim_configs
        )

    def test_initialization(self):
        # Alice is first, no simulated agent speaks on reset if first agent is not simulated.
        self.assertEqual(self.env.current_turn_holder, self.agent1_id)
        self.assertEqual(len(self.env.dialogue_history), 0)
        self.assertIn(self.agent2_id, self.env.simulated_interactors)

    def test_initialization_sim_agent_starts(self):
        # Test case where simulated agent is first
        env_sim_starts = SocialDialogueSandbox(
            dialogue_config=self.dialogue_config,
            agent_ids=[self.agent2_id, self.agent1_id], # Bob_Sim starts
            simulated_interactor_configs=self.sim_configs
        )
        self.assertEqual(env_sim_starts.current_turn_holder, self.agent1_id) # Bob spoke, turn advanced to Alice
        self.assertEqual(len(env_sim_starts.dialogue_history), 1) # Bob should have made an initial utterance
        self.assertEqual(env_sim_starts.dialogue_history[0]["speaker_id"], self.agent2_id)
        self.assertEqual(env_sim_starts.dialogue_history[0]["utterance"], self.sim_configs[self.agent2_id]["response_rules"]["greeting"])


    def test_reset(self):
        action = ActionCommand(action_type="speak", parameters={"utterance": "Hello Bob_Sim"})
        self.env.step(self.agent1_id, action)
        self.assertNotEqual(len(self.env.dialogue_history), 0)

        self.env.reset()
        self.assertEqual(self.env.current_turn_holder, self.agent1_id)
        # Alice is not simulated, so history should be empty after reset
        self.assertEqual(len(self.env.dialogue_history), 0)


    def test_speak_action_and_turn_taking(self):
        self.assertEqual(self.env.current_turn_holder, self.agent1_id)
        obs_alice = self.env.get_observation(self.agent1_id)
        self.assertTrue(obs_alice.custom_sensor_data["is_my_turn"])

        action_alice = ActionCommand(action_type="speak", parameters={"utterance": "Hello Bob_Sim"})
        result_alice = self.env.step(self.agent1_id, action_alice)

        self.assertEqual(result_alice.status, "success")
        self.assertEqual(len(self.env.dialogue_history), 2)
        self.assertEqual(self.env.dialogue_history[0]["speaker_id"], self.agent1_id)
        self.assertEqual(self.env.dialogue_history[0]["utterance"], "Hello Bob_Sim")
        self.assertEqual(self.env.dialogue_history[1]["speaker_id"], self.agent2_id)
        self.assertEqual(self.env.dialogue_history[1]["utterance"], "Hi there, Alice!") # From Bob's response rules

        self.assertEqual(self.env.current_turn_holder, self.agent1_id) # Turn back to Alice
        obs_alice_turn2 = self.env.get_observation(self.agent1_id)
        self.assertTrue(obs_alice_turn2.custom_sensor_data["is_my_turn"])
        self.assertEqual(obs_alice_turn2.textual_percepts[0].text, "Hi there, Alice!")

    def test_listen_action(self):
        self.assertEqual(self.env.current_turn_holder, self.agent1_id)
        action_listen = ActionCommand(action_type="listen")
        result = self.env.step(self.agent1_id, action_listen)

        self.assertEqual(result.status, "success")
        # Alice listens, Bob (sim) should respond to effectively "silence" or give a generic response.
        self.assertEqual(len(self.env.dialogue_history), 1)
        self.assertEqual(self.env.dialogue_history[0]["speaker_id"], self.agent2_id)
        # Check Bob's response to Alice listening (empty last utterance for generate_response)
        expected_bob_response_to_listen = self.env.simulated_interactors[self.agent2_id].generate_response("")
        self.assertEqual(self.env.dialogue_history[0]["utterance"], expected_bob_response_to_listen)

        self.assertEqual(self.env.current_turn_holder, self.agent1_id) # Turn should be Alice's again

    def test_wrong_turn(self):
        self.assertEqual(self.env.current_turn_holder, self.agent1_id)
        action_bob = ActionCommand(action_type="speak", parameters={"utterance": "Trying to speak out of turn."})
        result_bob = self.env.step(self.agent2_id, action_bob)

        self.assertEqual(result_bob.status, "failure")
        self.assertIn(f"It's not agent {self.agent2_id}'s turn", result_bob.message)
        self.assertEqual(len(self.env.dialogue_history), 0)
        self.assertEqual(self.env.current_turn_holder, self.agent1_id)

    def test_simulated_interactor_response_logic(self):
        action_alice_weather = ActionCommand(action_type="speak", parameters={"utterance": "How's the weather, Bob_Sim?"})
        self.env.step(self.agent1_id, action_alice_weather)
        self.assertEqual(self.env.dialogue_history[1]["utterance"], "It's fine, thanks for asking.")

        action_alice_other = ActionCommand(action_type="speak", parameters={"utterance": "Tell me a joke."})
        self.env.step(self.agent1_id, action_alice_other)
        self.assertEqual(self.env.dialogue_history[3]["utterance"], self.sim_configs[self.agent2_id]["default_response"])

    def test_max_turns_is_done(self):
        # max_turns is 10 for dialogue_config, meaning 10 utterances PER agent effectively.
        # The is_done() in SocialDialogueSandbox is `len(history) >= max_turns * len(agents)`
        # So for 2 agents, max_turns=2 means history length of 4 makes it done.
        self.env.dialogue_config["max_turns"] = 2

        # Turn 1: Alice speaks, Bob (sim) responds (history length 2)
        self.env.step(self.agent1_id, ActionCommand(action_type="speak", parameters={"utterance": "First line from Alice."}))
        self.assertFalse(self.env.is_done())
        self.assertEqual(len(self.env.dialogue_history), 2)

        # Turn 2: Alice speaks, Bob (sim) responds (history length 4)
        self.env.step(self.agent1_id, ActionCommand(action_type="speak", parameters={"utterance": "Second line from Alice."}))
        self.assertEqual(len(self.env.dialogue_history), 4)
        self.assertTrue(self.env.is_done()) # Max turns reached (2 turns * 2 agents = 4 history items)

    def test_goodbye_is_done(self):
        self.assertFalse(self.env.is_done())
        action_alice_bye = ActionCommand(action_type="speak", parameters={"utterance": "Okay, bye now!"})
        self.env.step(self.agent1_id, action_alice_bye) # Alice says bye, Bob (sim) responds with his "bye"
        self.assertEqual(self.env.dialogue_history[1]["utterance"], "Goodbye, Alice!")
        self.assertTrue(self.env.is_done())


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

```
