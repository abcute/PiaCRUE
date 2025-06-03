from typing import Any, Dict, List, Optional, Tuple
import copy

from PiaAGI_Research_Tools.PiaSE.core_engine.interfaces import (
    Environment,
    PerceptionData,
    ActionCommand,
    ActionResult,
    TextualPercept,
)

class CraftingWorld(Environment):
    """
    A simple crafting and problem-solving world environment.
    Agents can navigate, gather resources, and craft items based on recipes.
    """

    def __init__(
        self,
        world_definition: Dict[str, Any],
        agent_start_location: str,
        initial_recipes: Dict[str, Dict],
        agent_id: str = "agent_0",
    ):
        """
        Initializes the CraftingWorld.

        Args:
            world_definition: A dictionary describing locations, resources, and crafting stations.
                Example: {
                    "locations": {
                        "forest": {"resources": {"wood": 10}, "tools_present": ["old_axe"]},
                        "mine": {"resources": {"stone": 5, "iron_ore": 3}},
                        "workshop": {"crafting_stations": ["workbench"], "resources": {}}
                    }
                }
            agent_start_location: The ID of the agent's starting location.
            initial_recipes: A dictionary of recipes known at the start.
                Example: {
                    "wooden_plank": {"inputs": {"wood": 1}, "station_required": None, "output_quantity": 4},
                    "stick": {"inputs": {"wooden_plank": 1}, "station_required": "workbench", "output_quantity": 2},
                    "wooden_pickaxe": {"inputs": {"wooden_plank": 3, "stick": 2}, "station_required": "workbench", "output_quantity": 1}
                }
            agent_id: The ID of the agent in this environment.
        """
        self.world_definition_pristine = copy.deepcopy(world_definition)
        self.agent_start_location_pristine = agent_start_location
        self.initial_recipes_pristine = copy.deepcopy(initial_recipes)
        self.agent_id = agent_id

        self.current_step = 0
        self.world_map: Dict[str, Dict[str, Any]] = {}
        self.agent_location: str = ""
        self.agent_inventory: Dict[str, int] = {}
        self.known_recipes: Dict[str, Dict] = {}

        self.reset()

    def reset(self) -> PerceptionData:
        """Resets the environment to its initial state and returns the initial observation."""
        self.current_step = 0
        self.world_map = copy.deepcopy(self.world_definition_pristine["locations"])
        self.agent_location = self.agent_start_location_pristine
        self.agent_inventory = {} # Start with an empty inventory
        self.known_recipes = copy.deepcopy(self.initial_recipes_pristine)

        print(f"CraftingWorld: Environment reset. Agent '{self.agent_id}' at '{self.agent_location}'.")
        return self.get_observation(self.agent_id)

    def get_observation(self, agent_id: str) -> PerceptionData:
        """Gets the observation for the specified agent."""
        if agent_id != self.agent_id:
            # This environment is single-agent for now
            return PerceptionData(timestamp=self.current_step, messages=[{"error": "Agent ID mismatch"}])

        location_data = self.world_map.get(self.agent_location, {})

        text_percepts = [
            TextualPercept(text=f"You are at '{self.agent_location}'.", source="environment_description"),
        ]
        if location_data.get("resources"):
            res_list = ", ".join([f"{k}({v})" for k, v in location_data["resources"].items() if v > 0])
            if res_list:
                 text_percepts.append(TextualPercept(text=f"Resources here: {res_list}.", source="environment_description"))
            else:
                text_percepts.append(TextualPercept(text="No resources at this location.", source="environment_description"))

        if location_data.get("crafting_stations"):
            text_percepts.append(TextualPercept(text=f"Crafting stations here: {', '.join(location_data['crafting_stations'])}.", source="environment_description"))

        if self.agent_inventory:
            inv_list = ", ".join([f"{k}({v})" for k, v in self.agent_inventory.items()])
            text_percepts.append(TextualPercept(text=f"Your inventory: {inv_list}.", source="agent_status"))
        else:
            text_percepts.append(TextualPercept(text="Your inventory is empty.", source="agent_status"))

        custom_data = {
            "current_location_id": self.agent_location,
            "current_location_info": {
                "description": f"You are at {self.agent_location}", # Could be more detailed
                "resources": location_data.get("resources", {}),
                "tools_present": location_data.get("tools_present", []),
                "crafting_stations": location_data.get("crafting_stations", []),
                "exits": list(self.world_map.keys()) # Simplistic: all locations are exits from all others
            },
            "inventory_contents": self.agent_inventory.copy(),
            "known_recipes_list": list(self.known_recipes.keys()),
        }

        return PerceptionData(
            timestamp=self.current_step,
            textual_percepts=text_percepts,
            custom_sensor_data=custom_data,
            messages=[]
        )

    def step(self, agent_id: str, action: ActionCommand) -> ActionResult:
        """Processes an agent's action and updates the environment state."""
        self.current_step += 1
        status = "failure"
        message = "Unknown action or agent ID."

        if agent_id != self.agent_id:
            return ActionResult(timestamp=self.current_step, status="failure", message="Agent ID mismatch.")

        action_type = action.action_type
        params = action.parameters
        message = f"Action '{action_type}' processed."

        if action_type == "navigate":
            target_location = params.get("target_location_id")
            if target_location in self.world_map:
                self.agent_location = target_location
                status = "success"
                message = f"Successfully navigated to '{target_location}'."
            else:
                message = f"Navigation failed: Location '{target_location}' does not exist."

        elif action_type == "gather_resource":
            resource_type = params.get("resource_type")
            quantity_to_gather = params.get("quantity_to_gather", 1) # Default to 1 if not specified

            location_resources = self.world_map[self.agent_location].get("resources", {})

            if resource_type in location_resources and location_resources[resource_type] > 0:
                actual_gathered = min(quantity_to_gather, location_resources[resource_type])

                location_resources[resource_type] -= actual_gathered
                self.agent_inventory[resource_type] = self.agent_inventory.get(resource_type, 0) + actual_gathered
                status = "success"
                message = f"Successfully gathered {actual_gathered} of '{resource_type}'."
            else:
                message = f"Gathering failed: '{resource_type}' not available or depleted at '{self.agent_location}'."

        elif action_type == "craft_item":
            item_name = params.get("item_name")
            recipe = self.known_recipes.get(item_name)

            if not recipe:
                message = f"Crafting failed: Recipe for '{item_name}' unknown."
            else:
                # Check station
                required_station = recipe.get("station_required")
                current_location_stations = self.world_map[self.agent_location].get("crafting_stations", [])
                if required_station and required_station not in current_location_stations:
                    message = f"Crafting failed: Item '{item_name}' requires station '{required_station}', which is not here."
                else:
                    # Check resources
                    can_craft = True
                    missing_resources = {}
                    for res, req_qty in recipe["inputs"].items():
                        if self.agent_inventory.get(res, 0) < req_qty:
                            can_craft = False
                            missing_resources[res] = req_qty - self.agent_inventory.get(res, 0)

                    if can_craft:
                        # Consume resources
                        for res, req_qty in recipe["inputs"].items():
                            self.agent_inventory[res] -= req_qty
                            if self.agent_inventory[res] == 0:
                                del self.agent_inventory[res] # Clean up if zero

                        # Add crafted item
                        output_qty = recipe.get("output_quantity", 1)
                        self.agent_inventory[item_name] = self.agent_inventory.get(item_name, 0) + output_qty
                        status = "success"
                        message = f"Successfully crafted {output_qty} of '{item_name}'."
                    else:
                        missing_str = ", ".join([f"{k} (need {v})" for k,v in missing_resources.items()])
                        message = f"Crafting failed: Missing resources for '{item_name}': {missing_str}."
        else:
            message = f"Action type '{action_type}' not recognized or implemented."
            status = "failure"

        return ActionResult(
            timestamp=self.current_step,
            status=status,
            message=message,
            new_perception_snippet=self.get_observation(agent_id) # Provide updated perception
        )

    def get_environment_info(self) -> Dict[str, Any]:
        """Returns a dictionary with information about the environment."""
        return {
            "name": "CraftingWorld",
            "description": "A simple environment for crafting items from resources found in different locations.",
            "action_schema": {
                "navigate": {"target_location_id": "string (ID of a location)"},
                "gather_resource": {"resource_type": "string (name of resource)", "quantity_to_gather": "int (optional, default 1)"},
                "craft_item": {"item_name": "string (name of item to craft)"},
            },
            "perception_schema": {
                "custom_sensor_data": {
                    "current_location_id": "string",
                    "current_location_info": {"description", "resources", "tools_present", "crafting_stations", "exits"},
                    "inventory_contents": "dict (item_name: quantity)",
                    "known_recipes_list": "list of strings"
                },
                "textual_percepts": "list of TextualPercept objects describing current state/location"
            }
        }

    def get_action_space(self, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns a list of possible actions and their parameters for the agent."""
        # This can be made more dynamic based on agent's location and inventory
        actions = []

        # Navigate actions
        for loc_id in self.world_map.keys():
            if loc_id != self.agent_location:
                 actions.append({"action_type": "navigate", "parameters": {"target_location_id": loc_id}})

        # Gather actions
        current_loc_data = self.world_map.get(self.agent_location, {})
        if current_loc_data.get("resources"):
            for res_type, qty in current_loc_data["resources"].items():
                if qty > 0:
                    actions.append({"action_type": "gather_resource", "parameters": {"resource_type": res_type, "quantity_to_gather": 1}})

        # Craft actions
        for recipe_name, recipe_details in self.known_recipes.items():
            # Basic check: is station available if required? More checks could be done (e.g. has any input material)
            req_station = recipe_details.get("station_required")
            if not req_station or (req_station in current_loc_data.get("crafting_stations",[])):
                 actions.append({"action_type": "craft_item", "parameters": {"item_name": recipe_name}})

        if not actions: # Fallback if no specific actions identified
            actions.append({"action_type": "idle", "parameters": {}})

        return actions

    def get_state(self) -> Dict[str, Any]:
        """Gets the overall current state of the environment."""
        return {
            "current_step": self.current_step,
            "world_map_current_state": self.world_map,
            "agent_location": self.agent_location,
            "agent_inventory": self.agent_inventory,
            "known_recipes": self.known_recipes,
        }

    def is_done(self, agent_id: Optional[str] = None) -> bool:
        """Checks if the simulation or the agent's task is completed."""
        # For now, this environment runs indefinitely or until max_steps in engine
        return False

if __name__ == '__main__':
    # Example Usage
    world_def = {
        "locations": {
            "forest": {"resources": {"wood": 10}, "tools_present": []},
            "river": {"resources": {"water": 100, "stone": 5}},
            "workshop": {"crafting_stations": ["workbench"], "resources": {}}
        }
    }
    recipes = {
        "wooden_plank": {"inputs": {"wood": 1}, "station_required": None, "output_quantity": 4},
        "refined_stone": {"inputs": {"stone": 2}, "station_required": "workbench", "output_quantity": 1}
    }

    env = CraftingWorld(world_definition=world_def, agent_start_location="forest", initial_recipes=recipes)
    obs = env.reset()
    print("Initial Observation:")
    # print(obs.json(indent=2)) #Pydantic v2
    print(obs.model_dump_json(indent=2))


    action1 = ActionCommand(action_type="gather_resource", parameters={"resource_type": "wood", "quantity_to_gather": 2})
    print(f"\nExecuting Action 1: {action1.action_type} {action1.parameters}")
    result1 = env.step("agent_0", action1)
    print(f"Result 1: {result1.status} - {result1.message}")
    # print(result1.new_perception_snippet.json(indent=2)) #Pydantic v2
    print(result1.new_perception_snippet.model_dump_json(indent=2))


    action2 = ActionCommand(action_type="navigate", parameters={"target_location_id": "workshop"})
    print(f"\nExecuting Action 2: {action2.action_type} {action2.parameters}")
    result2 = env.step("agent_0", action2)
    print(f"Result 2: {result2.status} - {result2.message}")
    # print(result2.new_perception_snippet.json(indent=2)) #Pydantic v2
    print(result2.new_perception_snippet.model_dump_json(indent=2))


    action3 = ActionCommand(action_type="craft_item", parameters={"item_name": "wooden_plank"})
    print(f"\nExecuting Action 3: {action3.action_type} {action3.parameters}")
    result3 = env.step("agent_0", action3)
    print(f"Result 3: {result3.status} - {result3.message}")
    # print(result3.new_perception_snippet.json(indent=2)) #Pydantic v2
    print(result3.new_perception_snippet.model_dump_json(indent=2))


    action4 = ActionCommand(action_type="craft_item", parameters={"item_name": "refined_stone"}) # Should fail (no stone)
    print(f"\nExecuting Action 4: {action4.action_type} {action4.parameters}")
    result4 = env.step("agent_0", action4)
    print(f"Result 4: {result4.status} - {result4.message}")
    # print(result4.new_perception_snippet.json(indent=2)) #Pydantic v2
    print(result4.new_perception_snippet.model_dump_json(indent=2))

    print("\nFinal State:")
    print(env.get_state())

    print("\nAction Space from workshop:")
    print(env.get_action_space())

    env.agent_location = "river"
    print("\nAction Space from river:")
    print(env.get_action_space())

    env.agent_inventory["stone"] = 2
    env.agent_location = "workshop"
    action5 = ActionCommand(action_type="craft_item", parameters={"item_name": "refined_stone"}) # Should succeed now
    print(f"\nExecuting Action 5: {action5.action_type} {action5.parameters}")
    result5 = env.step("agent_0", action5)
    print(f"Result 5: {result5.status} - {result5.message}")
    print(result5.new_perception_snippet.model_dump_json(indent=2))

```
