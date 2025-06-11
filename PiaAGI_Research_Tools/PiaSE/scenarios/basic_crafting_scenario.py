from typing import List, Dict, Any, Optional

from PiaAGI_Research_Tools.PiaSE.core_engine.interfaces import (
    AgentInterface,
    ActionCommand,
    PerceptionData,
    ActionResult,
    PiaSEEvent,
)
from PiaAGI_Research_Tools.PiaSE.core_engine.basic_simulation_engine import BasicSimulationEngine
from PiaAGI_Research_Tools.PiaSE.environments.crafting_world import CraftingWorld

class RuleBasedCraftingAgent(AgentInterface):
    """
    A simple rule-based agent for the CraftingWorld.
    Tries to achieve a specific crafting goal.
    """
    def __init__(self, agent_id: str, goal_item: str):
        self.agent_id = agent_id
        self.goal_item = goal_item
        self.current_perception: Optional[PerceptionData] = None
        self.knowledge: Dict[str, Any] = {"recipes": {}} # Will store known recipes from perception

        # Simple plan/state machine (less used with recursive logic, but can be for high-level state)
        self.current_subgoal: Optional[str] = None
        self.subgoal_target_item: Optional[str] = None
        self.subgoal_target_location: Optional[str] = None

        # Tool knowledge (hardcoded)
        self.tool_locations: Dict[str, str] = {
            "axe": "forest",
            "hammer": "workshop",
            "pickaxe": "mine" # Assuming pickaxe might be needed for other things
        }
        # Agent's understanding of what tool is needed for what.
        # In a more advanced agent, this would be learned or part of detailed recipe/resource knowledge.
        self.resource_tool_requirements: Dict[str, str] = {
            "wood": "axe",
            "iron_ore": "pickaxe"
        }


    def set_id(self, agent_id: str):
        self.agent_id = agent_id

    def get_id(self) -> str:
        return self.agent_id

    def perceive(self, observation: PerceptionData, event: Optional[PiaSEEvent] = None):
        self.current_perception = observation
        if observation.custom_sensor_data and "known_recipes_list" in observation.custom_sensor_data:
            # In a real agent, it would learn recipes dynamically. Here, we assume CraftingWorld provides all.
            # We'd need to parse the full recipe details if the agent had to learn them.
            # For this simple agent, knowing the *names* is enough to try crafting.
            pass


    def _check_inventory(self, item: str, quantity: int) -> bool:
        if not self.current_perception or not self.current_perception.custom_sensor_data:
            return False
        inventory = self.current_perception.custom_sensor_data.get("inventory_contents", {})
        return inventory.get(item, 0) >= quantity

    def _get_recipe_inputs(self, item_name: str, all_recipes: Dict[str, Dict]) -> Optional[Dict[str, int]]:
        recipe = all_recipes.get(item_name)
        return recipe.get("inputs") if recipe else None

    def _get_recipe_station(self, item_name: str, all_recipes: Dict[str, Dict]) -> Optional[str]:
        recipe = all_recipes.get(item_name)
        return recipe.get("station_required") if recipe else None

    def _get_recipe_tool(self, item_name: str, all_recipes: Dict[str, Dict]) -> Optional[str]:
        """Helper to get the required tool for a recipe."""
        recipe = all_recipes.get(item_name)
        return recipe.get("tool_required") if recipe else None

    def act(self) -> ActionCommand:
        if not self.current_perception or not self.current_perception.custom_sensor_data:
            print(f"Agent {self.agent_id}: No perception data, idling.")
            return ActionCommand(action_type="idle", parameters={})

        inventory = self.current_perception.custom_sensor_data.get("inventory_contents", {})
        current_location = self.current_perception.custom_sensor_data.get("current_location_id")
        location_info = self.current_perception.custom_sensor_data.get("current_location_info", {})
        available_stations = location_info.get("crafting_stations", [])

        # Agent uses recipes provided by the environment through perception.
        # In a more complex agent, this would be part of its LTM.
        all_known_recipes = self.current_perception.custom_sensor_data.get("known_recipes_list", [])
        # For this agent, we'll assume it can reconstruct recipe details from their names if needed,
        # or that the environment provides full recipe details if it tries to craft.
        # For simplicity, we'll use a hardcoded map if full details aren't in perception.
        # This should ideally be populated from initial_recipes or learned.
        recipes = self.knowledge.get("recipes")
        if not recipes and self.current_perception.custom_sensor_data.get("initial_recipes_conceptual"): # Check if env passes this
            recipes = self.current_perception.custom_sensor_data["initial_recipes_conceptual"]
            self.knowledge["recipes"] = recipes
        elif not recipes: # Fallback to scenario's definition for this agent
             recipes = {
                "wooden_plank": {"inputs": {"wood": 1}, "station_required": None, "output_quantity": 4},
                "stick": {"inputs": {"wooden_plank": 1}, "station_required": "workbench", "output_quantity": 2},
                "wooden_pickaxe": {"inputs": {"wooden_plank": 3, "stick": 2}, "station_required": "workbench", "tool_required": "hammer"}
            } # Agent has its own copy/understanding

        # 1. Check if goal item is already crafted
        if self._check_inventory(self.goal_item, 1):
            print(f"Agent {self.agent_id}: Goal '{self.goal_item}' achieved! Idling.")
            return ActionCommand(action_type="idle", parameters={})

        # 2. Try to craft goal item if not in inventory
        # This is a recursive-like process: to craft X, I need A and B.
        # To get A, I might need to craft it or gather it. To gather A, I might need tool T.

        return self._get_action_for_item(self.goal_item, 1, recipes, inventory, current_location, location_info)


    def _get_action_for_item(self, item_name: str, quantity_needed: int, recipes: Dict, inventory: Dict, current_location: str, location_info: Dict) -> ActionCommand:
        """
        Recursive helper to determine the next action to obtain a specific item.
        Considers crafting, gathering, and tool requirements.
        """
        available_stations = location_info.get("crafting_stations", [])
        tools_present_at_location = location_info.get("tools_present", [])

        # I. Do I have enough of the item already?
        if self._check_inventory(item_name, quantity_needed):
            # This case should ideally be handled by the caller before calling this function for a specific item.
            # However, if called directly, it means no action needed for *this* item.
            print(f"Agent {self.agent_id}: Already have enough '{item_name}'. (This message might indicate redundant check).")
            return ActionCommand(action_type="idle", parameters={"reason": f"Sufficient {item_name} already present."})

        # II. Can I craft this item?
        item_recipe = recipes.get(item_name)
        if item_recipe:
            print(f"Agent {self.agent_id}: Considering crafting '{item_name}'.")
            # A. Check for required crafting station
            required_station = item_recipe.get("station_required")
            if required_station and required_station not in available_stations:
                target_station_location = "workshop" # Agent's hardcoded knowledge
                if current_location != target_station_location:
                    print(f"Agent {self.agent_id}: Need station '{required_station}' for '{item_name}', navigating to '{target_station_location}'.")
                    return ActionCommand(action_type="navigate", parameters={"target_location_id": target_station_location})
                else: # At the right location, but station not perceived (or wrong station)
                    print(f"Agent {self.agent_id}: At '{current_location}' but station '{required_station}' not available for '{item_name}'. Idling.")
                    return ActionCommand(action_type="idle", parameters={"reason": f"Station {required_station} missing."})

            # B. Check for required tool for crafting
            required_crafting_tool = item_recipe.get("tool_required")
            if required_crafting_tool:
                if not self._check_inventory(required_crafting_tool, 1):
                    print(f"Agent {self.agent_id}: Need tool '{required_crafting_tool}' to craft '{item_name}'.")
                    tool_loc = self.tool_locations.get(required_crafting_tool)
                    if tool_loc and current_location != tool_loc:
                        print(f"Agent {self.agent_id}: Navigating to '{tool_loc}' to get '{required_crafting_tool}'.")
                        return ActionCommand(action_type="navigate", parameters={"target_location_id": tool_loc})
                    elif tool_loc and current_location == tool_loc: # At tool location
                        if required_crafting_tool in tools_present_at_location:
                             print(f"Agent {self.agent_id}: Picking up '{required_crafting_tool}' at '{current_location}'.")
                             return ActionCommand(action_type="pickup_tool", parameters={"tool_name": required_craft_ing_tool})
                        else: # At tool location, but tool not here (or already picked up by someone else)
                             print(f"Agent {self.agent_id}: Tool '{required_crafting_tool}' not found at '{current_location}' (expected). Idling.")
                             return ActionCommand(action_type="idle", parameters={"reason": f"Tool {required_crafting_tool} missing at source."})
                    else: # Don't know where the tool is
                        print(f"Agent {self.agent_id}: Don't know where to find tool '{required_crafting_tool}'. Idling.")
                        return ActionCommand(action_type="idle", parameters={"reason": f"Location of tool {required_crafting_tool} unknown."})

            # C. Check for ingredients
            for ingredient, needed_qty in item_recipe["inputs"].items():
                if not self._check_inventory(ingredient, needed_qty):
                    print(f"Agent {self.agent_id}: Need ingredient '{ingredient}' ({needed_qty}) for '{item_name}'. Recursively getting it.")
                    return self._get_action_for_item(ingredient, needed_qty, recipes, inventory, current_location, location_info)

            # If all checks pass (station, tool, ingredients), then craft
            print(f"Agent {self.agent_id}: All requirements met for '{item_name}'. Attempting to craft.")
            return ActionCommand(action_type="craft_item", parameters={"item_name": item_name})

        # III. If not craftable, is it a raw material I know how to gather?
        # This agent's hardcoded knowledge about raw materials and their locations/tool needs
        raw_material_locations = {"wood": "forest", "stone": "mine", "iron_ore": "mine"} # Add more as needed

        if item_name in self.resource_tool_requirements: # It's a resource that needs a tool
            required_gathering_tool = self.resource_tool_requirements[item_name]
            print(f"Agent {self.agent_id}: Resource '{item_name}' requires tool '{required_gathering_tool}'.")
            if not self._check_inventory(required_gathering_tool, 1):
                print(f"Agent {self.agent_id}: Missing tool '{required_gathering_tool}' for '{item_name}'.")
                tool_loc = self.tool_locations.get(required_gathering_tool)
                if tool_loc and current_location != tool_loc:
                    print(f"Agent {self.agent_id}: Navigating to '{tool_loc}' to get '{required_gathering_tool}'.")
                    return ActionCommand(action_type="navigate", parameters={"target_location_id": tool_loc})
                elif tool_loc and current_location == tool_loc: # At tool location
                     if required_gathering_tool in tools_present_at_location:
                        print(f"Agent {self.agent_id}: Picking up '{required_gathering_tool}' at '{current_location}'.")
                        return ActionCommand(action_type="pickup_tool", parameters={"tool_name": required_gathering_tool})
                     else:
                        print(f"Agent {self.agent_id}: Tool '{required_gathering_tool}' not found at '{current_location}' (expected). Idling.")
                        return ActionCommand(action_type="idle", parameters={"reason": f"Tool {required_gathering_tool} missing at source."})
                else:
                    print(f"Agent {self.agent_id}: Don't know where to find tool '{required_gathering_tool}'. Idling.")
                    return ActionCommand(action_type="idle", parameters={"reason": f"Location of tool {required_gathering_tool} unknown."})

            # If tool is present, check location for gathering
            resource_loc = raw_material_locations.get(item_name)
            if resource_loc and current_location != resource_loc:
                print(f"Agent {self.agent_id}: Navigating to '{resource_loc}' to gather '{item_name}'.")
                return ActionCommand(action_type="navigate", parameters={"target_location_id": resource_loc})
            elif resource_loc and current_location == resource_loc: # At correct location with tool
                print(f"Agent {self.agent_id}: Gathering '{item_name}' at '{current_location}' (has tool '{required_gathering_tool}').")
                return ActionCommand(action_type="gather_resource", parameters={"resource_type": item_name, "quantity_to_gather": quantity_needed})

        elif item_name in raw_material_locations: # Raw material that doesn't need a specific tool (according to agent's knowledge)
            resource_loc = raw_material_locations[item_name]
            if current_location != resource_loc:
                print(f"Agent {self.agent_id}: Navigating to '{resource_loc}' to gather '{item_name}'.")
                return ActionCommand(action_type="navigate", parameters={"target_location_id": resource_loc})
            else: # At correct location
                print(f"Agent {self.agent_id}: Gathering '{item_name}' at '{current_location}'.")
                return ActionCommand(action_type="gather_resource", parameters={"resource_type": item_name, "quantity_to_gather": quantity_needed})

        # IV. Cannot craft and don't know how to gather
        print(f"Agent {self.agent_id}: Don't know how to obtain '{item_name}'. Idling.")
        return ActionCommand(action_type="idle", parameters={"reason": f"Cannot obtain {item_name}"})


    def learn(self, feedback: ActionResult):
        # This simple agent does not learn from feedback in a meaningful way,
        # but it could print messages or update confidence.
        print(f"Agent {self.agent_id} received feedback: {feedback.status} - {feedback.message}")
        if feedback.new_perception_snippet:
            self.perceive(feedback.new_perception_snippet)

    # Dummy Q-table methods for interface compliance
    def initialize_q_table(self, state: any, action_space: list): pass
    def get_q_value(self, state: any, action: any) -> float: return 0.0
    def update_q_value(self, state: any, action: any, reward: float, next_state: any, learning_rate: float, discount_factor: float, action_space: list): pass


def run_basic_crafting_scenario():
    print("--- Starting Basic Crafting Scenario ---")

    world_def = {
        "locations": {
            "forest": {"resources": {"wood": {"quantity": 20, "tool_required_to_gather": "axe"}}, "tools_present": ["axe"]},
            "workshop": {"crafting_stations": ["workbench"], "resources": {}, "tools_present": ["hammer"]},
            "mine": {"resources": {"stone": 10, "iron_ore": {"quantity": 5, "tool_required_to_gather": "pickaxe"}}, "tools_present": ["pickaxe"]}
        }
    }
    recipes = {
        "wooden_plank": {"inputs": {"wood": 1}, "station_required": None, "output_quantity": 4},
        "stick": {"inputs": {"wooden_plank": 1}, "station_required": "workbench", "output_quantity": 2},
        "wooden_pickaxe": {"inputs": {"wooden_plank": 3, "stick": 2}, "station_required": "workbench", "tool_required": "hammer", "output_quantity": 1}
    }

    # Initialize Environment
    environment = CraftingWorld(
        world_definition=world_def,
        agent_start_location="forest", # Start in forest to get wood
        initial_recipes=recipes,
        agent_id="crafter_0"
    )

    # Initialize Agent
    agent = RuleBasedCraftingAgent(agent_id="crafter_0", goal_item="wooden_pickaxe")

    # Initialize Simulation Engine
    engine = BasicSimulationEngine(environment=environment)
    engine.register_agent(agent_id="crafter_0", agent=agent)

    # Run Simulation
    max_steps = 30 # Increased max steps for more complex logic with tools
    print(f"\nRunning simulation for max {max_steps} steps. Goal: Craft a wooden_pickaxe.\n")
    for step_num in range(max_steps):
        print(f"--- Step {step_num + 1} ---")
        engine.run_step()

        # Check if goal is achieved (optional, for early exit)
        current_obs = environment.get_observation("crafter_0") # get latest obs
        if current_obs.custom_sensor_data:
            inventory = current_obs.custom_sensor_data.get("inventory_contents", {})
            if agent.goal_item in inventory:
                print(f"\nGoal '{agent.goal_item}' achieved by agent '{agent.agent_id}' in inventory!")
                break
        if step_num == max_steps -1: # Corrected off-by-one for max_steps message
             print("\nMax steps reached.")

    print("\n--- Basic Crafting Scenario Ended ---")
    print("Final State of Environment:")
    final_state = environment.get_state()
    print(f"  Agent Location: {final_state['agent_location']}")
    print(f"  Agent Inventory: {final_state['agent_inventory']}")

    forest_resources = final_state['world_map_current_state']['forest']['resources']
    if isinstance(forest_resources.get('wood'), dict):
        print(f"  Forest Wood: {forest_resources['wood'].get('quantity',0)}")
    else: # Should not happen with new setup, but good fallback
        print(f"  Forest Wood: {forest_resources.get('wood',0)}")

    # Print tools the agent has
    agent_tools = {item: qty for item, qty in final_state['agent_inventory'].items() if item in agent.tool_locations}
    print(f"  Agent Tools: {agent_tools}")


if __name__ == "__main__":
    run_basic_crafting_scenario()

```
