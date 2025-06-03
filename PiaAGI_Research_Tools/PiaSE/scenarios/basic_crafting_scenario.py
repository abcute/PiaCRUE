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

        # Simple plan/state machine
        self.current_subgoal: Optional[str] = None # e.g. "gather_wood", "craft_plank"
        self.subgoal_target_item: Optional[str] = None
        self.subgoal_target_location: Optional[str] = None


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

    def act(self) -> ActionCommand:
        if not self.current_perception or not self.current_perception.custom_sensor_data:
            return ActionCommand(action_type="idle", parameters={})

        inventory = self.current_perception.custom_sensor_data.get("inventory_contents", {})
        current_location = self.current_perception.custom_sensor_data.get("current_location_id")
        location_info = self.current_perception.custom_sensor_data.get("current_location_info", {})
        available_stations = location_info.get("crafting_stations", [])

        # Hardcoded recipes for this agent - a real agent would learn/query these
        # This should ideally come from the environment's known_recipes or agent's learning module
        recipes = { # Simplified version of what CraftingWorld has. Agent should learn this.
            "wooden_plank": {"inputs": {"wood": 1}, "station_required": None},
            "stick": {"inputs": {"wooden_plank": 1}, "station_required": "workbench"},
            "wooden_pickaxe": {"inputs": {"wooden_plank": 3, "stick": 2}, "station_required": "workbench"}
        }

        # 1. Check if goal item is already crafted
        if self._check_inventory(self.goal_item, 1):
            print(f"Agent {self.agent_id}: Goal '{self.goal_item}' achieved! Idling.")
            return ActionCommand(action_type="idle", parameters={})

        # 2. Try to craft goal item if not in inventory
        recipe_inputs = self._get_recipe_inputs(self.goal_item, recipes)
        if recipe_inputs:
            required_station = self._get_recipe_station(self.goal_item, recipes)
            if required_station and required_station not in available_stations:
                # Missing station, try to navigate to a location with the station (hardcoded for now)
                # A more robust agent would search its world model for the station.
                if "workshop" != current_location: # Assuming workshop has workbench
                    print(f"Agent {self.agent_id}: Need '{required_station}' for '{self.goal_item}', navigating to workshop.")
                    return ActionCommand(action_type="navigate", parameters={"target_location_id": "workshop"})
                else: # At workshop, but station still not listed? Environment error or agent perception issue.
                    print(f"Agent {self.agent_id}: At workshop but station '{required_station}' not available. Idling.")
                    return ActionCommand(action_type="idle", parameters={})


            # Check if all inputs for the goal item are available
            can_craft_goal = True
            for item, qty in recipe_inputs.items():
                if not self._check_inventory(item, qty):
                    can_craft_goal = False
                    # Need to craft/gather this prerequisite item
                    print(f"Agent {self.agent_id}: Need {qty} of '{item}' for '{self.goal_item}'.")

                    # Try to craft the prerequisite item
                    prereq_recipe_inputs = self._get_recipe_inputs(item, recipes)
                    if prereq_recipe_inputs:
                        prereq_station = self._get_recipe_station(item, recipes)
                        if prereq_station and prereq_station not in available_stations:
                            if "workshop" != current_location:
                                print(f"Agent {self.agent_id}: Need '{prereq_station}' for '{item}', navigating to workshop.")
                                return ActionCommand(action_type="navigate", parameters={"target_location_id": "workshop"})

                        can_craft_prereq = True
                        for sub_item, sub_qty in prereq_recipe_inputs.items():
                            if not self._check_inventory(sub_item, sub_qty):
                                can_craft_prereq = False
                                # Need to gather this sub_item
                                print(f"Agent {self.agent_id}: Need {sub_qty} of '{sub_item}' for '{item}'.")
                                # Where to find this sub_item? (Hardcoded for this agent)
                                if sub_item == "wood":
                                    if current_location != "forest":
                                        print(f"Agent {self.agent_id}: Navigating to forest to gather '{sub_item}'.")
                                        return ActionCommand(action_type="navigate", parameters={"target_location_id": "forest"})
                                    else:
                                        print(f"Agent {self.agent_id}: Gathering '{sub_item}' at forest.")
                                        return ActionCommand(action_type="gather_resource", parameters={"resource_type": sub_item, "quantity_to_gather": sub_qty})
                                # Add more gather locations if necessary
                                else:
                                    print(f"Agent {self.agent_id}: Don't know where to find '{sub_item}'. Idling.")
                                    return ActionCommand(action_type="idle", parameters={})
                        if can_craft_prereq:
                             print(f"Agent {self.agent_id}: Attempting to craft prerequisite '{item}'.")
                             return ActionCommand(action_type="craft_item", parameters={"item_name": item})

                    # If prerequisite is not craftable (e.g. raw material)
                    else: # It's a raw material
                        if item == "wood": # Hardcoded knowledge
                            if current_location != "forest":
                                print(f"Agent {self.agent_id}: Navigating to forest to gather '{item}'.")
                                return ActionCommand(action_type="navigate", parameters={"target_location_id": "forest"})
                            else:
                                print(f"Agent {self.agent_id}: Gathering '{item}' at forest.")
                                return ActionCommand(action_type="gather_resource", parameters={"resource_type": item, "quantity_to_gather": qty})
                        # Add more gather locations for other raw materials
                        else:
                            print(f"Agent {self.agent_id}: Don't know where to find raw material '{item}'. Idling.")
                            return ActionCommand(action_type="idle", parameters={})
                    break # Break from iterating recipe_inputs for the main goal_item

            if can_craft_goal:
                print(f"Agent {self.agent_id}: All prerequisites for '{self.goal_item}' available. Attempting to craft.")
                return ActionCommand(action_type="craft_item", parameters={"item_name": self.goal_item})

        print(f"Agent {self.agent_id}: No clear action towards '{self.goal_item}'. Idling.")
        return ActionCommand(action_type="idle", parameters={})

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
            "forest": {"resources": {"wood": 20}, "tools_present": []},
            "workshop": {"crafting_stations": ["workbench"], "resources": {}},
            "mine": {"resources": {"stone": 10}, "tools_present": []} # Added for completeness, not used by agent
        }
    }
    recipes = {
        "wooden_plank": {"inputs": {"wood": 1}, "station_required": None, "output_quantity": 4},
        "stick": {"inputs": {"wooden_plank": 1}, "station_required": "workbench", "output_quantity": 2},
        "wooden_pickaxe": {"inputs": {"wooden_plank": 3, "stick": 2}, "station_required": "workbench", "output_quantity": 1}
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
    max_steps = 20
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
        if step_num == max_steps -1:
             print("\nMax steps reached.")

    print("\n--- Basic Crafting Scenario Ended ---")
    print("Final State of Environment:")
    final_state = environment.get_state()
    print(f"  Agent Location: {final_state['agent_location']}")
    print(f"  Agent Inventory: {final_state['agent_inventory']}")
    print(f"  Forest Wood: {final_state['world_map_current_state']['forest']['resources'].get('wood',0)}")
    print(f"  Workshop Planks: {final_state['agent_inventory'].get('wooden_plank',0)}") # plank is in inventory
    print(f"  Workshop Sticks: {final_state['agent_inventory'].get('stick',0)}") # stick is in inventory

if __name__ == "__main__":
    run_basic_crafting_scenario()

```
