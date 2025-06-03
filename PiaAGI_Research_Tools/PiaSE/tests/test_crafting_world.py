import unittest
import copy

from PiaAGI_Research_Tools.PiaSE.core_engine.interfaces import ActionCommand
from PiaAGI_Research_Tools.PiaSE.environments.crafting_world import CraftingWorld

class TestCraftingWorld(unittest.TestCase):

    def setUp(self):
        self.world_def = {
            "locations": {
                "forest": {"resources": {"wood": 10}, "tools_present": ["old_axe"]},
                "mine": {"resources": {"stone": 5, "iron_ore": 3}},
                "workshop": {"crafting_stations": ["workbench"], "resources": {}},
                "clearing": {"resources": {}} # Empty location
            }
        }
        self.recipes = {
            "wooden_plank": {"inputs": {"wood": 1}, "station_required": None, "output_quantity": 4},
            "stick": {"inputs": {"wooden_plank": 1}, "station_required": "workbench", "output_quantity": 2},
            "wooden_pickaxe": {"inputs": {"wooden_plank": 3, "stick": 2}, "station_required": "workbench", "output_quantity": 1},
            "stone_hammer": {"inputs": {"stone": 3, "stick": 1}, "station_required": "workbench", "output_quantity": 1}
        }
        self.agent_id = "test_agent"
        self.env = CraftingWorld(
            world_definition=copy.deepcopy(self.world_def),
            agent_start_location="forest",
            initial_recipes=copy.deepcopy(self.recipes),
            agent_id=self.agent_id
        )

    def test_initialization(self):
        self.assertEqual(self.env.agent_location, "forest")
        self.assertEqual(self.env.agent_inventory, {})
        self.assertEqual(len(self.env.world_map), len(self.world_def["locations"]))
        self.assertEqual(self.env.world_map["forest"]["resources"]["wood"], 10)
        self.assertTrue("wooden_plank" in self.env.known_recipes)

    def test_reset(self):
        # Modify state
        self.env.agent_location = "mine"
        self.env.agent_inventory["wood"] = 5
        self.env.world_map["forest"]["resources"]["wood"] = 0

        obs = self.env.reset()

        self.assertEqual(self.env.agent_location, "forest") # Resets to start location
        self.assertEqual(self.env.agent_inventory, {})      # Resets inventory
        self.assertEqual(self.env.world_map["forest"]["resources"]["wood"], 10) # Resets world resources
        self.assertIsNotNone(obs)
        self.assertEqual(obs.custom_sensor_data["current_location_id"], "forest")

    def test_navigation_successful(self):
        action = ActionCommand(action_type="navigate", parameters={"target_location_id": "mine"})
        result = self.env.step(self.agent_id, action)

        self.assertEqual(result.status, "success")
        self.assertEqual(self.env.agent_location, "mine")
        self.assertEqual(result.new_perception_snippet.custom_sensor_data["current_location_id"], "mine")
        self.assertTrue("Successfully navigated to 'mine'." in result.message)

    def test_navigation_failed_invalid_location(self):
        initial_location = self.env.agent_location
        action = ActionCommand(action_type="navigate", parameters={"target_location_id": "unknown_place"})
        result = self.env.step(self.agent_id, action)

        self.assertEqual(result.status, "failure")
        self.assertEqual(self.env.agent_location, initial_location) # Agent should not move
        self.assertTrue("Location 'unknown_place' does not exist." in result.message)

    def test_gather_resource_successful(self):
        self.env.agent_location = "forest" # Ensure agent is at forest
        action = ActionCommand(action_type="gather_resource", parameters={"resource_type": "wood", "quantity_to_gather": 3})
        result = self.env.step(self.agent_id, action)

        self.assertEqual(result.status, "success")
        self.assertEqual(self.env.agent_inventory.get("wood"), 3)
        self.assertEqual(self.env.world_map["forest"]["resources"]["wood"], 7) # 10 - 3
        self.assertTrue("Successfully gathered 3 of 'wood'." in result.message)

    def test_gather_resource_partial_quantity(self):
        self.env.agent_location = "forest"
        action = ActionCommand(action_type="gather_resource", parameters={"resource_type": "wood", "quantity_to_gather": 15}) # Try to gather more than available
        result = self.env.step(self.agent_id, action)

        self.assertEqual(result.status, "success") # Still success, but gathers what's available
        self.assertEqual(self.env.agent_inventory.get("wood"), 10) # Gathered all 10
        self.assertEqual(self.env.world_map["forest"]["resources"]["wood"], 0)
        self.assertTrue("Successfully gathered 10 of 'wood'." in result.message)

    def test_gather_resource_failed_not_available(self):
        self.env.agent_location = "workshop" # Workshop has no 'wood' by default
        action = ActionCommand(action_type="gather_resource", parameters={"resource_type": "wood"})
        result = self.env.step(self.agent_id, action)

        self.assertEqual(result.status, "failure")
        self.assertEqual(self.env.agent_inventory.get("wood", 0), 0) # Inventory unchanged
        self.assertTrue("'wood' not available or depleted at 'workshop'." in result.message)

    def test_gather_resource_failed_depleted(self):
        self.env.agent_location = "forest"
        self.env.world_map["forest"]["resources"]["wood"] = 0 # Wood is depleted
        action = ActionCommand(action_type="gather_resource", parameters={"resource_type": "wood"})
        result = self.env.step(self.agent_id, action)

        self.assertEqual(result.status, "failure")
        self.assertEqual(self.env.agent_inventory.get("wood", 0), 0)
        self.assertTrue("'wood' not available or depleted at 'forest'." in result.message)


    def test_craft_item_successful_no_station(self):
        # Craft wooden_plank (wood:1 -> wooden_plank:4), no station needed
        self.env.agent_inventory["wood"] = 2
        action = ActionCommand(action_type="craft_item", parameters={"item_name": "wooden_plank"})
        result = self.env.step(self.agent_id, action)

        self.assertEqual(result.status, "success")
        self.assertEqual(self.env.agent_inventory.get("wood"), 1) # Consumed 1 wood
        self.assertEqual(self.env.agent_inventory.get("wooden_plank"), 4) # Produced 4 planks
        self.assertTrue("Successfully crafted 4 of 'wooden_plank'." in result.message)

    def test_craft_item_successful_with_station(self):
        # Craft stick (wooden_plank:1 -> stick:2), requires workbench
        self.env.agent_location = "workshop" # Go to workshop for workbench
        self.env.agent_inventory["wooden_plank"] = 3
        action = ActionCommand(action_type="craft_item", parameters={"item_name": "stick"})
        result = self.env.step(self.agent_id, action)

        self.assertEqual(result.status, "success")
        self.assertEqual(self.env.agent_inventory.get("wooden_plank"), 2) # Consumed 1 plank
        self.assertEqual(self.env.agent_inventory.get("stick"), 2)       # Produced 2 sticks
        self.assertTrue("Successfully crafted 2 of 'stick'." in result.message)

    def test_craft_item_failed_missing_resources(self):
        self.env.agent_inventory["wood"] = 0 # Not enough wood for wooden_plank
        action = ActionCommand(action_type="craft_item", parameters={"item_name": "wooden_plank"})
        result = self.env.step(self.agent_id, action)

        self.assertEqual(result.status, "failure")
        self.assertEqual(self.env.agent_inventory.get("wooden_plank", 0), 0) # No planks produced
        self.assertTrue("Missing resources for 'wooden_plank': wood (need 1)" in result.message)

    def test_craft_item_failed_missing_station(self):
        # Try to craft 'stick' (needs workbench) in 'forest' (no workbench)
        self.env.agent_location = "forest"
        self.env.agent_inventory["wooden_plank"] = 1 # Has resources
        action = ActionCommand(action_type="craft_item", parameters={"item_name": "stick"})
        result = self.env.step(self.agent_id, action)

        self.assertEqual(result.status, "failure")
        self.assertEqual(self.env.agent_inventory.get("stick", 0), 0) # No sticks produced
        self.assertTrue("Item 'stick' requires station 'workbench', which is not here." in result.message)

    def test_craft_item_failed_unknown_recipe(self):
        action = ActionCommand(action_type="craft_item", parameters={"item_name": "unknown_item"})
        result = self.env.step(self.agent_id, action)

        self.assertEqual(result.status, "failure")
        self.assertTrue("Recipe for 'unknown_item' unknown." in result.message)

    def test_craft_complex_item_wooden_pickaxe(self):
        # Goal: Craft wooden_pickaxe (planks:3, stick:2 from workbench)
        # 1. Gather wood (need 3 planks -> 3 wood; 2 sticks -> 2 planks -> 2 wood; Total 5 wood)
        self.env.agent_location = "forest"
        self.env.step(self.agent_id, ActionCommand(action_type="gather_resource", parameters={"resource_type": "wood", "quantity_to_gather": 5}))
        self.assertEqual(self.env.agent_inventory.get("wood"), 5)

        # 2. Craft wooden_planks (need 3 for pickaxe, 2 for sticks that make pickaxe = 5 planks)
        # Recipe: 1 wood -> 4 planks. So 2 wood crafts 8 planks.
        self.env.step(self.agent_id, ActionCommand(action_type="craft_item", parameters={"item_name": "wooden_plank"})) # Uses 1 wood, makes 4 planks
        self.env.step(self.agent_id, ActionCommand(action_type="craft_item", parameters={"item_name": "wooden_plank"})) # Uses 1 wood, makes 4 planks
        self.assertEqual(self.env.agent_inventory.get("wooden_plank"), 8)
        self.assertEqual(self.env.agent_inventory.get("wood"), 3) # 5 - 2 = 3 wood left

        # 3. Navigate to workshop
        self.env.step(self.agent_id, ActionCommand(action_type="navigate", parameters={"target_location_id": "workshop"}))
        self.assertEqual(self.env.agent_location, "workshop")

        # 4. Craft sticks (need 2 for pickaxe. Recipe: 1 plank -> 2 sticks)
        self.env.step(self.agent_id, ActionCommand(action_type="craft_item", parameters={"item_name": "stick"})) # Uses 1 plank, makes 2 sticks
        self.assertEqual(self.env.agent_inventory.get("stick"), 2)
        self.assertEqual(self.env.agent_inventory.get("wooden_plank"), 7) # 8 - 1 = 7 planks left

        # 5. Craft wooden_pickaxe
        action = ActionCommand(action_type="craft_item", parameters={"item_name": "wooden_pickaxe"})
        result = self.env.step(self.agent_id, action)

        self.assertEqual(result.status, "success", msg=f"Pickaxe craft failed: {result.message}")
        self.assertEqual(self.env.agent_inventory.get("wooden_pickaxe"), 1)
        self.assertEqual(self.env.agent_inventory.get("wooden_plank"), 4) # 7 - 3 = 4 planks left
        self.assertEqual(self.env.agent_inventory.get("stick"), 0) # 2 - 2 = 0 sticks left

    def test_get_observation(self):
        self.env.agent_location = "workshop"
        self.env.agent_inventory["wood"] = 5
        obs = self.env.get_observation(self.agent_id)

        self.assertEqual(obs.timestamp, self.env.current_step) # current_step is 0 initially
        self.assertEqual(obs.custom_sensor_data["current_location_id"], "workshop")
        self.assertTrue("workshop" in obs.custom_sensor_data["current_location_info"]["description"])
        self.assertEqual(obs.custom_sensor_data["inventory_contents"]["wood"], 5)
        self.assertTrue("wooden_plank" in obs.custom_sensor_data["known_recipes_list"])

        found_loc_desc = False
        found_inv_desc = False
        for tp in obs.textual_percepts:
            if "You are at 'workshop'" in tp.text:
                found_loc_desc = True
            if "Your inventory: wood(5)" in tp.text:
                found_inv_desc = True
        self.assertTrue(found_loc_desc)
        self.assertTrue(found_inv_desc)

    def test_get_action_space(self):
        # In forest
        self.env.agent_location = "forest"
        actions_forest = self.env.get_action_space(self.agent_id)
        can_navigate_to_mine = any(a["action_type"] == "navigate" and a["parameters"]["target_location_id"] == "mine" for a in actions_forest)
        can_gather_wood = any(a["action_type"] == "gather_resource" and a["parameters"]["resource_type"] == "wood" for a in actions_forest)
        can_craft_plank_in_forest = any(a["action_type"] == "craft_item" and a["parameters"]["item_name"] == "wooden_plank" for a in actions_forest) # Plank needs no station

        self.assertTrue(can_navigate_to_mine)
        self.assertTrue(can_gather_wood)
        self.assertTrue(can_craft_plank_in_forest)

        # In workshop (has workbench)
        self.env.agent_location = "workshop"
        actions_workshop = self.env.get_action_space(self.agent_id)
        can_craft_pickaxe_in_workshop = any(a["action_type"] == "craft_item" and a["parameters"]["item_name"] == "wooden_pickaxe" for a in actions_workshop)
        self.assertTrue(can_craft_pickaxe_in_workshop)

        cannot_gather_wood_in_workshop = not any(a["action_type"] == "gather_resource" and a["parameters"]["resource_type"] == "wood" for a in actions_workshop)
        self.assertTrue(cannot_gather_wood_in_workshop)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

```
