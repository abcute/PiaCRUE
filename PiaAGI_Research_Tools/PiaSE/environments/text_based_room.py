# PiaAGI_Research_Tools/PiaSE/environments/text_based_room.py
from typing import Dict, Any, Optional, List

# Conceptual Pydantic-like models for data structures (not enforced here, for clarity)
# class PerceptionData(dict): pass # Replace with actual import if available
# class ActionCommand(dict): pass # Replace with actual import if available
# class ActionResult(dict): pass # Replace with actual import if available
# class EnvironmentInfo(dict): pass # Replace with actual import if available

class TextBasedRoom: # Will conceptually implement AbstractEnvironment
    def __init__(self, scenario_data: Optional[Dict[str, Any]] = None):
        self.room_layout: Dict[str, Dict[str, Any]] = {}
        self.object_details: Dict[str, Dict[str, Any]] = {}
        self.agent_states: Dict[str, Dict[str, Any]] = {} # agent_id -> {"current_room": str, "inventory": List[str]}
        self._load_scenario(scenario_data)
        print("TextBasedRoom environment initialized.")

    def _load_scenario(self, scenario_data: Optional[Dict[str, Any]] = None):
        # Load a default scenario if none provided
        if not scenario_data:
            scenario_data = self._get_default_scenario()

        self.room_layout = scenario_data.get("room_layout", {})
        self.object_details = scenario_data.get("object_details", {})
        # Initialize agents if defined in scenario, otherwise expect registration
        initial_agent_setup = scenario_data.get("agent_setup", {})
        if initial_agent_setup: # Simplified: assumes one agent from scenario
            agent_id = initial_agent_setup.get("agent_id", "agent_0")
            self.agent_states[agent_id] = {
                "current_room": initial_agent_setup.get("start_room", next(iter(self.room_layout.keys())) if self.room_layout else "limbo"),
                "inventory": list(initial_agent_setup.get("initial_inventory", []))
            }

    def _get_default_scenario(self) -> Dict[str, Any]:
        return {
            "room_layout": {
                "study": {
                    "description": "a quiet study. A large wooden desk sits centrally. A bookshelf lines one wall.",
                    "exits": {"north": "hallway"},
                    "objects": ["desk", "bookshelf"]
                },
                "hallway": {
                    "description": "a short, dusty hallway. A grandfather clock is against the far wall.",
                    "exits": {"south": "study"},
                    "objects": ["grandfather_clock", "key"] # Key added for testing take
                }
            },
            "object_details": {
                "desk": {"description": "a sturdy oak desk with a single drawer.", "is_container": True, "is_open": False, "contains": [], "locked": False},
                "bookshelf": {"description": "a tall bookshelf filled with dusty tomes.", "searchable": False},
                "grandfather_clock": {"description": "an old grandfather clock. Its pendulum is still."},
                "key": {"description": "a small brass key.", "takeable": True}
            },
            "agent_setup": {"agent_id": "agent_0", "start_room": "study", "initial_inventory": []}
        }

    def register_agent(self, agent_id: str, start_room_id: Optional[str] = None, initial_inventory: Optional[List[str]] = None):
        if agent_id in self.agent_states:
            print(f"Agent {agent_id} already registered.")
            return

        default_start_room = next(iter(self.room_layout.keys())) if self.room_layout else "limbo"
        self.agent_states[agent_id] = {
            "current_room": start_room_id or default_start_room,
            "inventory": initial_inventory or []
        }
        print(f"Agent {agent_id} registered, starting in {self.agent_states[agent_id]['current_room']}.")


    def get_environment_info(self) -> Dict[str, Any]: # Conceptual EnvironmentInfo
        return {
            "environment_name": "TextBasedRoom_Prototype",
            "description": "A prototype text-based room environment.",
            "action_schema": {
                "go": {"parameters": {"direction": "str (north, south, east, west)"}},
                "look": {"parameters": {"target": "Optional[str]"}},
                "take": {"parameters": {"item_name": "str"}}
            },
            "perception_schema": { # Simplified
                "room_description": "str",
                "visible_objects": "List[str]",
                "inventory": "List[str]",
                "messages": "List[str]"
            }
        }

    def get_perceptual_data_for_agent(self, agent_id: str) -> Dict[str, Any]: # Conceptual PerceptionData
        if agent_id not in self.agent_states:
            return {"error": "Agent not found"}

        agent_room_id = self.agent_states[agent_id]["current_room"]
        room_data = self.room_layout.get(agent_room_id)

        if not room_data:
            return {"room_description": "You are in a featureless void.", "visible_objects": [], "inventory": self.agent_states[agent_id]["inventory"], "messages": ["Error: Current room data not found."]}

        visible_object_names = [obj_id for obj_id in room_data.get("objects", []) if obj_id in self.object_details]

        perception = {
            "room_name": agent_room_id,
            "room_description": room_data["description"],
            "exits": list(room_data.get("exits", {}).keys()),
            "visible_objects": visible_object_names,
            "inventory": list(self.agent_states[agent_id]["inventory"]),
            "messages": [] # For environment messages to agent
        }
        return perception

    def apply_action_from_agent(self, agent_id: str, action_command: Dict[str, Any]) -> Dict[str, Any]: # Conceptual ActionResult
        if agent_id not in self.agent_states:
            return {"status": "failure", "message": "Agent not found."}

        action_type = action_command.get("action_type")
        params = action_command.get("parameters", {})
        agent_current_room_id = self.agent_states[agent_id]["current_room"]
        current_room_data = self.room_layout.get(agent_current_room_id)

        if not current_room_data:
             return {"status": "failure", "message": f"Critical error: Agent {agent_id} in unknown room {agent_current_room_id}."}

        if action_type == "go":
            direction = params.get("direction")
            if direction in current_room_data.get("exits", {}):
                new_room_id = current_room_data["exits"][direction]
                self.agent_states[agent_id]["current_room"] = new_room_id
                return {"status": "success", "message": f"You move {direction}. You are now in {new_room_id}."}
            else:
                return {"status": "failure", "message": f"You cannot go {direction} from here."}

        elif action_type == "look":
            target = params.get("target")
            if not target: # Look around room
                return {"status": "success", "message": self.get_perceptual_data_for_agent(agent_id).get("room_description", "You see nothing special.")}
            elif target in current_room_data.get("objects", []) and target in self.object_details:
                return {"status": "success", "message": self.object_details[target].get("description", f"You see a {target}.")}
            else:
                return {"status": "failure", "message": f"You don't see '{target}' here."}

        elif action_type == "take":
            item_name = params.get("item_name")
            room_objects = current_room_data.get("objects", []) # This needs to be a reference to the actual list in room_layout
            if item_name in room_objects and item_name in self.object_details:
                if self.object_details[item_name].get("takeable", False):
                    # To modify the original list in room_layout:
                    self.room_layout[agent_current_room_id]["objects"].remove(item_name)
                    self.agent_states[agent_id]["inventory"].append(item_name)
                    return {"status": "success", "message": f"You take the {item_name}."}
                else:
                    return {"status": "failure", "message": f"You cannot take the {item_name}."}
            else:
                return {"status": "failure", "message": f"You don't see a {item_name} here to take."}

        else:
            return {"status": "failure", "message": f"Unknown action type: {action_type}."}

    def reset_environment(self, scenario_data: Optional[Dict[str, Any]] = None) -> bool:
        self._load_scenario(scenario_data)
        print("TextBasedRoom environment reset.")
        return True
