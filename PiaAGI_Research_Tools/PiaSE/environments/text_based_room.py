import time
import copy
from typing import Dict, Any, List, Optional, Tuple

from ..core_engine.interfaces import Environment, PerceptionData, ActionCommand, ActionResult

class TextBasedRoom(Environment):
    def __init__(self,
                 room_layout: Dict[str, Any],
                 object_details: Dict[str, Any],
                 agent_start_room: str,
                 agent_id: str = "agent_0"):
        super().__init__()
        self.base_room_layout = copy.deepcopy(room_layout)
        self.base_object_details = copy.deepcopy(object_details)
        
        self.agent_id = agent_id  # Assuming single agent for now in this environment's direct state
        self.agent_start_room = agent_start_room

        # These will be initialized on reset
        self.current_room_layout: Dict[str, Any] = {}
        self.current_object_details: Dict[str, Any] = {}
        self.agent_states: Dict[str, Any] = {} # agent_id -> {"current_room": "...", "inventory": []}

        self.action_schema = {
            "go": {"parameters": {"direction": {"type": "string", "choices": ["north", "south", "east", "west"]}}},
            "look": {"parameters": {"target": {"type": "string", "optional": True}}},
            "take": {"parameters": {"item_name": {"type": "string"}}},
            "drop": {"parameters": {"item_name": {"type": "string"}}},
            "open": {"parameters": {"target_object": {"type": "string"}}},
            "close": {"parameters": {"target_object": {"type": "string"}}}, # Added close
            "use": {"parameters": {"item_name": {"type": "string"}, "target_object": {"type": "string", "optional": True}}},
            "read": {"parameters": {"item_name": {"type": "string"}}},
            "inventory": {"parameters": {}} # Action to check inventory
        }
        
        self.reset()

    def reset(self) -> PerceptionData:
        self.current_room_layout = copy.deepcopy(self.base_room_layout)
        self.current_object_details = copy.deepcopy(self.base_object_details)
        
        self.agent_states = {
            self.agent_id: {
                "current_room": self.agent_start_room,
                "inventory": [],
                "flags": {} # For scenario-specific states
            }
        }
        # print(f"TextBasedRoom: Environment reset. Agent '{self.agent_id}' starts in '{self.agent_start_room}'")
        return self.get_observation(self.agent_id)

    def get_observation(self, agent_id: str) -> PerceptionData:
        if agent_id != self.agent_id:
            # Basic handling for unkown agent_id in a single agent environment
            return PerceptionData(timestamp=time.time(), sensor_data={"error": "Unknown agent ID"}, messages=[{"sender": "system", "content": f"Agent {agent_id} not recognized."}])

        agent_room_name = self.agent_states[agent_id]["current_room"]
        room_data = self.current_room_layout.get(agent_room_name)

        if not room_data:
            return PerceptionData(
                timestamp=time.time(),
                sensor_data={"error": f"Agent room '{agent_room_name}' not found in layout."},
                messages=[{"sender": "system", "content": "Error: Current room is invalid."}]
            )

        visible_text = f"You are in {room_data.get('description', 'an undescribed location')}."
        
        # Exits
        exits = room_data.get("exits", {})
        if exits:
            visible_text += " Exits are: " + ", ".join(exits.keys()) + "."
        else:
            visible_text += " There are no obvious exits."

        # Objects in room
        room_objects_names = room_data.get("objects", [])
        visible_objects_desc_list = [] # Renamed to avoid conflict
        if room_objects_names:
            visible_text += " You see:"
            for obj_name in room_objects_names:
                obj_detail = self.current_object_details.get(obj_name)
                if obj_detail:
                    desc = obj_detail.get('description', obj_name)
                    visible_objects_desc_list.append(f"- {desc}")
            if visible_objects_desc_list:
                visible_text += "\n" + "\n".join(visible_objects_desc_list)
            else: # Should not happen if room_objects_names is populated and details exist
                visible_text += " nothing of particular interest that is described."
        else:
            visible_text += " The room seems empty."


        sensor_data = {
            "room_name": agent_room_name,
            "description": visible_text, # This now contains the full descriptive text
            "objects_visible": [{"name": obj_name, "description": self.current_object_details.get(obj_name, {}).get('description', obj_name)} for obj_name in room_objects_names],
            "inventory": list(self.agent_states[agent_id]["inventory"]) # Send a copy
        }
        
        return PerceptionData(
            timestamp=time.time(),
            sensor_data=sensor_data,
            messages=[] # No specific messages here, they come from ActionResult or events
        )

    def _get_object_in_room(self, object_name: str, room_name: str) -> Optional[Dict]:
        room_data = self.current_room_layout.get(room_name)
        if room_data and object_name in room_data.get("objects", []):
            return self.current_object_details.get(object_name)
        return None

    def _get_object_in_inventory(self, object_name: str, agent_id: str) -> Optional[Dict]:
        if object_name in self.agent_states[agent_id]["inventory"]:
            return self.current_object_details.get(object_name)
        return None

    def step(self, agent_id: str, action: ActionCommand) -> ActionResult:
        if agent_id != self.agent_id:
            return ActionResult(timestamp=time.time(), status="failure", message="Unknown agent ID.")

        action_type = action.action_type
        params = action.parameters
        current_room_name = self.agent_states[agent_id]["current_room"]
        room_data = self.current_room_layout.get(current_room_name)

        status = "failure"
        message = f"Could not perform action: {action_type}"
        details = {}
        new_perception_snippet = None

        if action_type == "go":
            direction = params.get("direction")
            if direction in room_data.get("exits", {}):
                next_room_name = room_data["exits"][direction]
                self.agent_states[agent_id]["current_room"] = next_room_name
                status = "success"
                message = f"You moved {direction} to {next_room_name}."
            else:
                message = f"You cannot go {direction} from here."

        elif action_type == "look":
            target = params.get("target")
            if not target or target == current_room_name or target == "around": # Look around the room
                status = "success"
                # The message for "look around" is effectively the new observation.
                # We'll generate it via get_observation and place it in new_perception_snippet.
                # The ActionResult.message can be simpler.
                message = "You look around the room."
            else: # Look at a specific object
                obj_detail_room = self._get_object_in_room(target, current_room_name)
                obj_detail_inv = self._get_object_in_inventory(target, agent_id)
                obj_detail = obj_detail_room or obj_detail_inv

                if obj_detail:
                    status = "success"
                    message = f"You look at {target}: {obj_detail.get('description', 'It has no special description.')}"
                    if obj_detail.get("is_container") and obj_detail.get("is_open"):
                        message += " It is open."
                        contained_items = obj_detail.get("contains", [])
                        if contained_items:
                            message += " Inside, you see: " + ", ".join(contained_items) + "."
                        else:
                            message += " It is empty."
                    elif obj_detail.get("is_container") and not obj_detail.get("is_open"):
                         message += " It is closed."
                else:
                    message = f"You don't see '{target}' here."
        
        elif action_type == "inventory":
            inventory_items = self.agent_states[agent_id]["inventory"]
            if inventory_items:
                message = "You have: " + ", ".join(inventory_items) + "."
            else:
                message = "Your inventory is empty."
            status = "success"

        elif action_type == "take":
            item_name = params.get("item_name")
            obj_detail = self.current_object_details.get(item_name, {}) # Get details once

            # Check if item is loose in the room
            if item_name in self.current_room_layout[current_room_name].get("objects", []):
                if obj_detail.get("can_be_taken", False):
                    self.current_room_layout[current_room_name]["objects"].remove(item_name)
                    self.agent_states[agent_id]["inventory"].append(item_name)
                    status = "success"
                    message = f"You took the {item_name}."
                else:
                    message = f"You cannot take the {item_name}."
            else:
                # Check if item is in an open container in the room
                taken_from_container = False
                container_that_contained_item = None # To prevent modifying list while iterating
                
                for obj_name_in_room in self.current_room_layout[current_room_name].get("objects", []):
                    container_detail = self.current_object_details.get(obj_name_in_room)
                    if container_detail and container_detail.get("is_container") and container_detail.get("is_open"):
                        if item_name in container_detail.get("contains", []):
                            if obj_detail.get("can_be_taken", False): # Check original item's detail
                                container_that_contained_item = container_detail 
                                self.agent_states[agent_id]["inventory"].append(item_name)
                                status = "success"
                                message = f"You took the {item_name} from the {obj_name_in_room}."
                                taken_from_container = True
                                break 
                            else:
                                message = f"You cannot take the {item_name} (from {obj_name_in_room})."
                                status = "failure" # Explicitly set failure
                                taken_from_container = True # Found but can't take, stop further search
                                break
                
                if container_that_contained_item and status == "success":
                    container_that_contained_item["contains"].remove(item_name)

                if not taken_from_container and status != "failure": 
                    message = f"You don't see a {item_name} here to take."

        elif action_type == "drop":
            item_name = params.get("item_name")
            if item_name in self.agent_states[agent_id]["inventory"]:
                self.agent_states[agent_id]["inventory"].remove(item_name)
                self.current_room_layout[current_room_name].setdefault("objects", []).append(item_name)
                status = "success"
                message = f"You dropped the {item_name}."
            else:
                message = f"You don't have a {item_name} in your inventory."

        elif action_type == "open":
            target_object_name = params.get("target_object")
            obj_detail = self._get_object_in_room(target_object_name, current_room_name)
            if obj_detail:
                if obj_detail.get("is_container"):
                    if obj_detail.get("locked"):
                        message = f"The {target_object_name} is locked."
                    elif obj_detail.get("is_open"):
                        message = f"The {target_object_name} is already open."
                    else:
                        obj_detail["is_open"] = True
                        status = "success"
                        message = f"You opened the {target_object_name}."
                        contained_items = obj_detail.get("contains", [])
                        if contained_items:
                            message += " Inside, you see: " + ", ".join(contained_items) + "."
                        else:
                            message += " It is empty."
                else:
                    message = f"You cannot open the {target_object_name}."
            else:
                message = f"You don't see a {target_object_name} here."
        
        elif action_type == "close":
            target_object_name = params.get("target_object")
            obj_detail = self._get_object_in_room(target_object_name, current_room_name)
            if obj_detail:
                if obj_detail.get("is_container"):
                    if not obj_detail.get("is_open", False):
                        message = f"The {target_object_name} is already closed."
                    else:
                        obj_detail["is_open"] = False
                        status = "success"
                        message = f"You closed the {target_object_name}."
                else:
                    message = f"You cannot close the {target_object_name}."
            else:
                message = f"You don't see a {target_object_name} here."

        elif action_type == "read":
            item_name = params.get("item_name")
            obj_in_inv = self._get_object_in_inventory(item_name, agent_id)
            obj_in_room = self._get_object_in_room(item_name, current_room_name)
            target_obj_detail = obj_in_inv or obj_in_room 

            if target_obj_detail:
                read_text = target_obj_detail.get("read_text")
                if read_text:
                    status = "success"
                    message = f"It reads: \"{read_text}\"" # Escaped quotes for the message
                    self.agent_states[agent_id].setdefault("flags", {})[f"read_{item_name}"] = True
                else:
                    message = f"There is nothing to read on the {item_name}."
            else:
                message = f"You don't see a {item_name} to read here or in your inventory."

        elif action_type == "use":
            item_name_to_use = params.get("item_name")
            target_object_name = params.get("target_object") # Optional target

            item_detail_inv = self._get_object_in_inventory(item_name_to_use, agent_id)

            if not item_detail_inv:
                message = f"You don't have a {item_name_to_use} in your inventory."
            else:
                if target_object_name: 
                    target_obj_detail_room = self._get_object_in_room(target_object_name, current_room_name)
                    if target_obj_detail_room:
                        # Scenario 1: Unlock a locked object
                        if target_obj_detail_room.get("locked") and \
                           target_obj_detail_room.get("key_required") == item_name_to_use:
                            target_obj_detail_room["locked"] = False
                            status = "success"
                            message = f"You used the {item_name_to_use} on the {target_object_name}. It is now unlocked."
                            if item_detail_inv.get("consumes_on_use"):
                                self.agent_states[agent_id]["inventory"].remove(item_name_to_use)
                                message += f" The {item_name_to_use} was consumed."
                        # Scenario 2: Custom interaction defined in object_details
                        elif target_obj_detail_room.get("custom_interactions") and \
                             item_name_to_use in target_obj_detail_room.get("custom_interactions", {}):
                            interaction_config = target_obj_detail_room["custom_interactions"][item_name_to_use]
                            status = interaction_config.get("status", "success") # Default to success
                            message = interaction_config.get("message", f"You used the {item_name_to_use} on the {target_object_name}.")
                            
                            if "set_flag_on_target" in interaction_config: # Safely access
                                flag_info = interaction_config["set_flag_on_target"]
                                if "name" in flag_info:
                                    flag_name = flag_info["name"]
                                    flag_value = flag_info.get("value", True)
                                    target_obj_detail_room.setdefault("flags", {})[flag_name] = flag_value

                            if item_detail_inv.get("consumes_on_use"):
                                self.agent_states[agent_id]["inventory"].remove(item_name_to_use)
                                message += f" The {item_name_to_use} was consumed."
                        else:
                            message = f"You can't use the {item_name_to_use} on the {target_object_name} in that way."
                    else:
                        message = f"You don't see a {target_object_name} here to use the {item_name_to_use} on."
                else: # Use item without a target (standalone use)
                    if item_detail_inv.get("can_be_used_standalone"):
                        status = "success"
                        message = item_detail_inv.get("standalone_use_message", f"You used the {item_name_to_use}.")
                        if item_detail_inv.get("consumes_on_use"):
                             self.agent_states[agent_id]["inventory"].remove(item_name_to_use)
                             message += f" The {item_name_to_use} was consumed."
                        
                        if "set_flag_on_agent" in item_detail_inv: # Safely access
                            flag_config = item_detail_inv.get("set_flag_on_agent",{})
                            if "name" in flag_config : # ensure flag_name is not None
                                flag_name = flag_config.get("name")
                                flag_value = flag_config.get("value", True)
                                self.agent_states[agent_id].setdefault("flags", {})[flag_name] = flag_value
                    else:
                        message = f"You can't just use the {item_name_to_use} by itself like that."

        if status == "success":
            new_perception_snippet = self.get_observation(agent_id)


        return ActionResult(
            timestamp=time.time(),
            status=status,
            message=message,
            new_perception_snippet=new_perception_snippet,
            details=details
        )

    def get_state(self) -> Dict[str, Any]:
        return {
            "current_room_layout": copy.deepcopy(self.current_room_layout),
            "current_object_details": copy.deepcopy(self.current_object_details),
            "agent_states": copy.deepcopy(self.agent_states)
        }

    def is_done(self, agent_id: str) -> bool:
        # This environment doesn't have an intrinsic "done" condition for the agent by default.
        # Scenarios will define win/lose conditions that the engine checks.
        return False 

    def get_action_space(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        # In this env, action space is not agent-dependent beyond the agent_id check at start of methods
        return self.action_schema

    def get_environment_info(self) -> Dict[str, Any]:
        return {
            "environment_name": "TextBasedRoom_v1.0",
            "description": "A simple text-based adventure environment for navigation and interaction.",
            "action_schema": self.action_schema,
            "perception_schema": { # Describes structure of PerceptionData.sensor_data
                "room_name": {"type": "string"},
                "description": {"type": "string", "description": "Full text description of room, exits, and objects."},
                "objects_visible": {"type": "list", "item_schema": {"name": "string", "description": "string"}},
                "inventory": {"type": "list", "item_schema": "string"}
            }
        }

```
