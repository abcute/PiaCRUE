import time
from typing import List, Dict, Optional, Any

from PiaAGI_Research_Tools.PiaSE.core_engine.basic_engine import BasicSimulationEngine
from PiaAGI_Research_Tools.PiaSE.environments.text_based_room import TextBasedRoom
from PiaAGI_Research_Tools.PiaSE.core_engine.interfaces import Environment, AgentInterface, PerceptionData, ActionCommand, ActionResult, PiaSEEvent

# --- Agent Definition ---
class InteractiveTextAgent(AgentInterface):
    def __init__(self, agent_id: str = "interactive_agent"):
        self.agent_id = agent_id
        self.last_perception: Optional[PerceptionData] = None
        self.last_action_command: Optional[ActionCommand] = None # To store the last command for quit check
        print(f"InteractiveTextAgent '{self.agent_id}' initialized.")

    def set_id(self, agent_id: str):
        self.agent_id = agent_id
        print(f"InteractiveTextAgent ID set to: {self.agent_id}")

    def get_id(self) -> str:
        return self.agent_id

    def perceive(self, observation: PerceptionData, event: Optional[PiaSEEvent] = None):
        self.last_perception = observation
        print(f"\n--- {self.agent_id}'s Perception ---")
        if observation.sensor_data.get("description"):
            print(observation.sensor_data["description"])
        else:
            print(f"Received complex observation: {observation.sensor_data}")

        if observation.messages:
            for msg in observation.messages:
                print(f"[Message from {msg.get('sender', 'system')}]: {msg.get('content')}")

        if event:
            print(f"[Event Received]: Type: {event.event_type}, Data: {event.data}")
        print("-----------------------------")


    def act(self) -> ActionCommand:
        while True:
            try:
                action_input = input(f"Enter action for {self.agent_id} (e.g., 'go north', 'take key', 'look desk', or 'quit'): ")
                parts = action_input.strip().split()
                if not parts:
                    print("Please enter an action.")
                    continue

                action_type = parts[0].lower()

                if action_type == "quit":
                    self.last_action_command = ActionCommand(action_type="quit", parameters={})
                    return self.last_action_command

                parameters = {}
                if action_type == "go":
                    if len(parts) > 1:
                        parameters["direction"] = parts[1].lower()
                    else:
                        print("Go where? (e.g., go north)")
                        continue
                elif action_type == "look":
                    if len(parts) > 1:
                        parameters["target"] = " ".join(parts[1:]) # Allow multi-word targets
                    # No target means look around, which is fine
                elif action_type in ["take", "drop", "read", "open", "close"]:
                    if len(parts) > 1:
                        # For "open desk" or "take shiny key"
                        item_or_target_name = " ".join(parts[1:])
                        if action_type in ["open", "close"]:
                            parameters["target_object"] = item_or_target_name
                        else: # take, drop, read
                            parameters["item_name"] = item_or_target_name
                    else:
                        print(f"{action_type.capitalize()} what? (e.g., {action_type} key)")
                        continue
                elif action_type == "use":
                    if len(parts) > 1:
                        parameters["item_name"] = parts[1] # First word after "use" is item
                        if len(parts) > 3 and parts[2].lower() == "on":
                            parameters["target_object"] = " ".join(parts[3:])
                        # else use item by itself (target_object remains None)
                    else:
                        print("Use what? (e.g., use key on desk, or use potion)")
                        continue
                elif action_type == "inventory":
                    pass # No params needed

                self.last_action_command = ActionCommand(action_type=action_type, parameters=parameters)
                return self.last_action_command
            except EOFError: # Handle Ctrl+D for exiting
                print("\nExiting agent action loop (EOF).")
                self.last_action_command = ActionCommand(action_type="quit", parameters={})
                return self.last_action_command
            except Exception as e:
                print(f"Error processing action: {e}. Try again.")

    def learn(self, feedback: ActionResult):
        print(f"--- {self.agent_id}'s Feedback ---")
        print(f"Action Status: {feedback.status}")
        if feedback.message:
            print(f"Message: {feedback.message}")
        if feedback.details:
            print(f"Details: {feedback.details}")
        print("--------------------------")

    def initialize_q_table(self, state: Any, action_space: list): pass
    def get_q_value(self, state: Any, action: Any) -> float: return 0.0
    def update_q_value(self, state: Any, action: Any, reward: float, next_state: Any, learning_rate: float, discount_factor: float, action_space: list): pass


# --- Scenario Definition ---
SCENARIO_NAME = "The Lost Key"
AGENT_ID_PLAYER = "Player"

LOST_KEY_ROOM_LAYOUT = {
    "study": {
        "description": "a quiet study. A large wooden desk sits centrally. A bookshelf lines one wall.",
        "exits": {"north": "hallway"},
        "objects": ["desk", "bookshelf"]
    },
    "hallway": {
        "description": "a short, dusty hallway. A grandfather clock is against the far wall. It seems to have stopped.",
        "exits": {"south": "study"},
        "objects": ["grandfather_clock"]
    }
}

LOST_KEY_OBJECT_DETAILS = {
    "desk": {
        "description": "a sturdy oak desk with a single drawer.",
        "is_container": True,
        "is_open": False,
        "contains": ["old_document"],
        "locked": True,
        "key_required": "brass_key"
    },
    "bookshelf": {
        "description": "a tall bookshelf filled with dusty tomes. One book titled 'Chronicles of Time' looks slightly ajar.",
        "custom_properties": {"searchable": True}
    },
    "grandfather_clock": {
        "description": "an old grandfather clock. Its pendulum is still. The time reads 6:05.",
        "contains": ["brass_key"],
        "is_container": True,
        "is_open": False,
        "locked": False
    },
    "brass_key": {
        "description": "a small brass key.",
        "can_be_taken": True
    },
    "old_document": {
        "description": "a rolled-up parchment, tied with a faded ribbon.",
        "can_be_taken": True,
        "read_text": "The ancient formula is complete. The world will remember this day."
    }
}

def setup_environment(config: Optional[Dict] = None) -> Environment:
    print("Setting up 'The Lost Key' environment...")
    return TextBasedRoom(
        room_layout=LOST_KEY_ROOM_LAYOUT,
        object_details=LOST_KEY_OBJECT_DETAILS,
        agent_start_room="study",
        agent_id=AGENT_ID_PLAYER
    )

def setup_agents(env_info: Dict, config: Optional[Dict] = None) -> List[AgentInterface]:
    print("Setting up agents...")
    player_agent = InteractiveTextAgent(agent_id=AGENT_ID_PLAYER)
    return [player_agent]

# --- Main Execution ---
def run_scenario(max_steps: int = 50, custom_config: Optional[Dict] = None):
    print(f"--- Starting Scenario: {SCENARIO_NAME} ---")

    engine = BasicSimulationEngine()

    environment = setup_environment(config=custom_config)
    agent_list = setup_agents(env_info={}, config=custom_config)

    agents_dict = {agent.get_id(): agent for agent in agent_list}

    engine.initialize(
        environment=environment,
        agents=agents_dict,
        scenario_config={"name": SCENARIO_NAME, "max_steps": max_steps}
    )

    for i in range(max_steps):
        print(f"\n--- Scenario Step {engine.current_step + 1}/{max_steps} ---")
        engine.run_step()

        player_agent_instance = agents_dict.get(AGENT_ID_PLAYER)

        if player_agent_instance and isinstance(player_agent_instance, InteractiveTextAgent):
            if player_agent_instance.last_action_command and \
               player_agent_instance.last_action_command.action_type == "quit":
                print(f"\n*** {SCENARIO_NAME} EXITED by user. ***")
                engine.logger.log(engine.current_step, "SCENARIO_QUIT", "scenario_logic", {"reason": "User quit via action"})
                break

        # Check win condition
        if player_agent_instance and player_agent_instance.last_perception and \
           "old_document" in player_agent_instance.last_perception.sensor_data.get("inventory", []):
            print(f"\n*** {SCENARIO_NAME} COMPLETED: You found the old document! ***")
            engine.logger.log(engine.current_step, "SCENARIO_WIN", "scenario_logic", {"reason": "Agent obtained old_document"})
            break

        if engine._are_all_agents_done():
             print(f"\n*** {SCENARIO_NAME} ENDED: All agents are done (as per environment). ***")
             engine.logger.log(engine.current_step, "SCENARIO_END", "scenario_logic", {"reason": "All agents done by environment state"})
             break
    else:
        print(f"\n*** {SCENARIO_NAME} ENDED: Max steps ({max_steps}) reached. ***")
        engine.logger.log(engine.current_step, "SCENARIO_END", "scenario_logic", {"reason": "Max steps reached"})

    if engine.logger: # Ensure logger exists before closing
        engine.logger.close()
    print(f"--- Scenario: {SCENARIO_NAME} Finished ---")

if __name__ == "__main__":
    run_scenario(max_steps=50)

```
