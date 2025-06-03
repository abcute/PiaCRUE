import time
from typing import Dict, Any, List, Optional, Tuple

from ..core_engine.interfaces import Environment, PerceptionData, ActionCommand, ActionResult, TextualPercept

class SimulatedInteractorProfile:
    def __init__(self, interactor_id: str, response_rules: Optional[Dict[str, str]] = None, default_response: Optional[str] = None):
        self.interactor_id = interactor_id
        # Simple rule: if keyword in last utterance, respond with value.
        self.response_rules = response_rules if response_rules else {"hello": "Hello to you too!", "name": f"My name is {interactor_id}."}
        self.default_response = default_response if default_response else "Interesting."

    def generate_response(self, last_utterance: str) -> str:
        if not last_utterance: # Handle initial greeting or if no prior context
            return self.response_rules.get("greeting", f"Hello, I'm {self.interactor_id}.")

        for keyword, response in self.response_rules.items():
            if keyword.lower() in last_utterance.lower():
                return response
        return self.default_response

class SocialDialogueSandbox(Environment):
    def __init__(self,
                 dialogue_config: Dict[str, Any], # e.g., {"topic": "general_chat", "max_turns": 20}
                 agent_ids: List[str], # IDs of all participants (PiaAGI and simulated)
                 simulated_interactor_configs: Optional[Dict[str, Dict]] = None # Configs for simulated ones
                ):
        super().__init__()
        self.dialogue_config = dialogue_config
        self.all_agent_ids = list(agent_ids) # Ensure it's a list copy

        self.simulated_interactors: Dict[str, SimulatedInteractorProfile] = {}
        if simulated_interactor_configs:
            for agent_id_key, config_val in simulated_interactor_configs.items():
                # Ensure the key from simulated_interactor_configs is actually in all_agent_ids
                if agent_id_key in self.all_agent_ids:
                    self.simulated_interactors[agent_id_key] = SimulatedInteractorProfile(
                        interactor_id=agent_id_key,
                        response_rules=config_val.get("response_rules"),
                        default_response=config_val.get("default_response")
                    )
                else:
                    print(f"Warning: Config provided for simulated interactor '{agent_id_key}' but this ID is not in the main agent_ids list.")


        # State
        self.dialogue_history: List[Dict[str, str]] = [] # List of {"speaker_id": str, "utterance": str}
        self.turn_index: int = 0
        self.current_turn_holder: Optional[str] = None

        self.action_schema = {
            "speak": {"parameters": {"utterance": {"type": "string"}}},
            "listen": {"parameters": {}} # Explicitly pass turn
        }
        self.reset()

    def reset(self) -> Optional[PerceptionData]:
        self.dialogue_history = []
        self.turn_index = 0
        if self.all_agent_ids:
            self.current_turn_holder = self.all_agent_ids[self.turn_index]
        else:
            self.current_turn_holder = None

        if self.current_turn_holder:
             # If the first turn holder is a simulated agent, let it speak.
            if self.current_turn_holder in self.simulated_interactors:
                sim_interactor = self.simulated_interactors[self.current_turn_holder]
                initial_utterance = sim_interactor.generate_response("") # Initial greeting
                self.dialogue_history.append({"speaker_id": self.current_turn_holder, "utterance": initial_utterance})
                self._advance_turn() # Move to the next agent

            if self.current_turn_holder: # If there's still a valid turn holder (e.g. not a 1-simulated-agent dialogue)
                return self.get_observation(self.current_turn_holder)
        return None


    def get_observation(self, agent_id: str) -> PerceptionData:
        if not self.all_agent_ids or agent_id not in self.all_agent_ids:
            return PerceptionData(timestamp=time.time(), custom_sensor_data={"error": "Agent not in dialogue."})

        text_percepts = []
        if not self.dialogue_history:
            # Initial state for the first agent to act (if not simulated)
            text_percepts.append(
                TextualPercept(text="The dialogue has just begun. It's your turn.", source="system")
            )
        else:
            last_entry = self.dialogue_history[-1]
            # Provide the last utterance. Agent's own perception module should filter if it's its own.
            text_percepts.append(
                TextualPercept(text=last_entry["utterance"], source=last_entry["speaker_id"])
            )

        # Add more context to observation if needed, e.g., a few turns of history
        # for entry in self.dialogue_history[-3:]: # Last 3 entries
        #     text_percepts.append(TextualPercept(text=entry["utterance"], source=entry["speaker_id"]))

        return PerceptionData(
            timestamp=time.time(),
            textual_percepts=text_percepts,
            custom_sensor_data={
                "dialogue_topic": self.dialogue_config.get("topic", "general"),
                "participants": list(self.all_agent_ids),
                "current_turn_holder": self.current_turn_holder,
                "is_my_turn": agent_id == self.current_turn_holder,
                "dialogue_history_preview": self.dialogue_history[-5:] # last 5 utterances
            },
            messages=[]
        )

    def _advance_turn(self):
        if not self.all_agent_ids:
            self.current_turn_holder = None
            return
        self.turn_index = (self.turn_index + 1) % len(self.all_agent_ids)
        self.current_turn_holder = self.all_agent_ids[self.turn_index]

    def step(self, agent_id: str, action: ActionCommand) -> ActionResult:
        timestamp = time.time()
        if agent_id != self.current_turn_holder:
            return ActionResult(
                timestamp=timestamp, status="failure",
                message=f"It's not agent {agent_id}'s turn. Current turn: {self.current_turn_holder}."
            )

        action_type = action.action_type
        params = action.parameters
        status = "failure"
        message = f"Action '{action_type}' not handled."

        performed_action_this_step = False

        if action_type == "speak":
            utterance = params.get("utterance")
            if isinstance(utterance, str) and utterance.strip(): # Ensure non-empty utterance
                self.dialogue_history.append({"speaker_id": agent_id, "utterance": utterance})
                status = "success"
                message = f"Agent {agent_id} spoke: \"{utterance}\""
                self._advance_turn()
                performed_action_this_step = True
            else:
                message = "Invalid or empty utterance provided."

        elif action_type == "listen":
            status = "success"
            message = f"Agent {agent_id} chose to listen."
            self._advance_turn()
            performed_action_this_step = True

        # If a real agent just spoke or listened, and now it's a simulated interactor's turn
        if performed_action_this_step and self.current_turn_holder in self.simulated_interactors:
            sim_interactor = self.simulated_interactors[self.current_turn_holder]
            # Simulated interactor responds to the last real utterance in history
            last_real_utterance = ""
            if self.dialogue_history:
                # Find last utterance not by a simulated agent, or just the very last one if all are real
                # For simplicity, just use the very last one for now.
                last_real_utterance = self.dialogue_history[-1]["utterance"]

            response_utterance = sim_interactor.generate_response(last_real_utterance)

            self.dialogue_history.append({"speaker_id": self.current_turn_holder, "utterance": response_utterance})
            message += f"\n{self.current_turn_holder} responded: \"{response_utterance}\""
            self._advance_turn() # Advance turn again after simulated agent speaks

        new_perception_snippet = None
        if self.current_turn_holder: # Get perception for the next agent whose turn it is
            new_perception_snippet = self.get_observation(self.current_turn_holder)

        return ActionResult(
            timestamp=timestamp,
            status=status,
            message=message,
            new_perception_snippet=new_perception_snippet,
            details={"dialogue_history_length": len(self.dialogue_history)}
        )

    def get_environment_info(self) -> Dict[str, Any]:
        return {
            "environment_name": "SocialDialogueSandbox_v0.1",
            "description": "A simple environment for turn-based dialogue interactions.",
            "action_schema": self.action_schema,
            "perception_schema": {
                "textual_percepts": [{"text": "string", "source": "string (speaker_id or system)"}],
                "custom_sensor_data": {
                    "dialogue_topic": "string",
                    "participants": "List[str]",
                    "current_turn_holder": "str",
                    "is_my_turn": "bool",
                    "dialogue_history_preview": "List[Dict[str,str]] (last 5 entries)"
                }
            }
        }

    def get_action_space(self, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if agent_id == self.current_turn_holder:
            return [
                {"action_type": "speak", "parameters": {"utterance": "Your response here"}},
                {"action_type": "listen", "parameters": {}}
            ]
        return [] # No actions if not their turn


    def get_state(self) -> Dict[str, Any]:
        return {
            "dialogue_config": self.dialogue_config,
            "all_agent_ids": list(self.all_agent_ids),
            "dialogue_history": list(self.dialogue_history),
            "turn_index": self.turn_index,
            "current_turn_holder": self.current_turn_holder,
            "simulated_interactor_configs_count": len(self.simulated_interactors)
        }

    def is_done(self, agent_id: Optional[str] = None) -> bool:
        if "max_turns" in self.dialogue_config and \
           len(self.dialogue_history) >= self.dialogue_config["max_turns"] * len(self.all_agent_ids): # Crude turn count
            return True
        # Check for end-of-dialogue keywords
        if self.dialogue_history:
            last_utterance = self.dialogue_history[-1]["utterance"].lower()
            if "goodbye" in last_utterance or "bye now" in last_utterance:
                return True
        return False

if __name__ == '__main__':
    # Example Usage
    test_config = {"topic": "Weather", "max_turns": 5} # Max 5 exchanges (Alice speaks, Bob speaks = 1 turn for history count)
    agent_ids_list = ["Alice", "Bob_Simulated"]
    sim_configs = {
        "Bob_Simulated": {
            "response_rules": {
                "weather": "The weather is quite sunny today!",
                "name": "I am Bob, a friendly simulated conversationalist.",
                "hello": "Hi there Alice!",
                "greeting": "Hello! I'm Bob." # For initial response
            },
            "default_response": "That's an interesting point."
        }
    }

    env = SocialDialogueSandbox(dialogue_config=test_config, agent_ids=agent_ids_list, simulated_interactor_configs=sim_configs)

    current_actor_id = env.current_turn_holder
    print(f"--- Dialogue Start --- Topic: {env.dialogue_config.get('topic')} ---")
    if env.dialogue_history: # If simulated agent spoke first
        entry = env.dialogue_history[-1]
        print(f"{entry['speaker_id']}: {entry['utterance']}")

    for i in range(test_config["max_turns"] * len(agent_ids_list) + 2): # Simulate a few turns
        if env.is_done():
            print(f"--- Dialogue Ended (is_done is True) ---")
            break

        current_actor_id = env.current_turn_holder
        if not current_actor_id:
            print("--- Dialogue Ended (no current turn holder) ---")
            break

        obs = env.get_observation(current_actor_id)
        print(f"\nTurn: {len(env.dialogue_history) // len(agent_ids_list) +1} - It's {current_actor_id}'s turn.")
        if obs.textual_percepts:
            print(f"  Perceives from {obs.textual_percepts[0].source}: \"{obs.textual_percepts[0].text}\"")

        if current_actor_id == "Alice": # Real agent's turn
            action_alice = None
            last_bob_utterance = ""
            if obs.textual_percepts and obs.textual_percepts[0].source == "Bob_Simulated":
                last_bob_utterance = obs.textual_percepts[0].text.lower()

            if "hello" in last_bob_utterance or not env.dialogue_history or len(env.dialogue_history) <=1 : # Alice's first real turn
                 action_alice = ActionCommand(action_type="speak", parameters={"utterance": "Hello Bob_Simulated, what's your name?"})
            elif "name is bob" in last_bob_utterance:
                action_alice = ActionCommand(action_type="speak", parameters={"utterance": "Nice to meet you Bob! How is the weather?"})
            elif "weather is quite sunny" in last_bob_utterance:
                 action_alice = ActionCommand(action_type="speak", parameters={"utterance": "Glad to hear it's sunny! Goodbye for now."})
            else:
                action_alice = ActionCommand(action_type="listen", parameters={}) # Just listen if unsure

            print(f"  Alice performs: {action_alice.action_type} {action_alice.parameters.get('utterance','')}")
            result = env.step("Alice", action_alice)
            print(f"  Action Result for Alice: Status: {result.status}")
            if "Bob_Simulated responded:" in result.message: # Show Bob's part of message clearly
                print(f"  {result.message.splitlines()[-1].strip()}") # Assumes Bob's response is last line

        elif current_actor_id in env.simulated_interactors:
            # Simulated interactor's turn is handled within the step method of the previous agent.
            # This loop structure means we might print "It's Bob's turn" but his action was already processed.
            # This is fine for a simple test; a real engine would manage this flow more cleanly.
             print(f"  (Simulated agent {current_actor_id} already responded in previous step's resolution.)")
             pass # Turn already advanced if Bob spoke.

    print("\n--- Final Dialogue History ---")
    for entry in env.dialogue_history:
        print(f"- {entry['speaker_id']}: {entry['utterance']}")
    print(f"Total turns in history: {len(env.dialogue_history)}")

```
