import unittest
import copy
from typing import Dict, Any, List

# Adjust imports to reach the PiaSE components from the tests directory
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PiaSE.core_engine.interfaces import ActionCommand
from PiaSE.environments.crafting_world import CraftingWorld

class TestCraftingWorld(unittest.TestCase):

    def setUp(self):
        self.agent_id = "test_agent"
        self.world_def_template = {
            "locations": {
                "forest": {"resources": {"wood": {"quantity": 10, "tool_required_to_gather": "axe"}}, "tools_present": ["axe"]},
                "mine": {"resources": {"stone": 20, "iron_ore": {"quantity": 5, "tool_required_to_gather": "pickaxe"}}, "tools_present": ["pickaxe"]},
                "workshop": {"crafting_stations": ["workbench", "forge"], "resources": {}, "tools_present": ["hammer", "saw"]},
                "field": {"resources": {"plant_fiber": 15}, "tools_present": []} # Resource without tool requirement
            }
        }
        self.recipes_template = {
            "wooden_plank": {"inputs": {"wood": 1}, "station_required": None, "output_quantity": 4},
            "stick": {"inputs": {"wooden_plank": 1}, "station_required": "workbench", "output_quantity": 2},
            "basic_axe": {"inputs": {"stick": 2, "stone": 3}, "station_required": "workbench", "tool_required": "hammer", "output_quantity": 1},
            "refined_wood": {"inputs": {"wooden_plank": 2}, "station_required": "workbench", "tool_required": "saw", "output_quantity": 1},
            "rope": {"inputs": {"plant_fiber": 3}, "station_required": None, "output_quantity": 1}
        }
        self.env = CraftingWorld(
            world_definition=copy.deepcopy(self.world_def_template),
            agent_start_location="forest",
            initial_recipes=copy.deepcopy(self.recipes_template),
            agent_id=self.agent_id
        )

    def test_initialization_with_tools_and_requirements(self):
        self.assertIn("axe", self.env.world_map["forest"]["tools_present"])
        self.assertEqual(self.env.world_map["forest"]["resources"]["wood"]["tool_required_to_gather"], "axe")
        self.assertEqual(self.env.known_recipes["basic_axe"]["tool_required"], "hammer")

    def test_action_pickup_tool(self):
        self.env.agent_location = "forest" # Axe is in the forest

        # Successful pickup
        action_pickup_axe = ActionCommand(action_type="pickup_tool", parameters={"tool_name": "axe"})
        result = self.env.step(self.agent_id, action_pickup_axe)

        self.assertEqual(result.status, "success")
        self.assertIn("Successfully picked up 'axe'", result.message)
        self.assertEqual(self.env.agent_inventory.get("axe"), 1)
        self.assertNotIn("axe", self.env.world_map["forest"]["tools_present"])

        # Attempt to pick up again (should fail as it's gone from location)
        result_again = self.env.step(self.agent_id, action_pickup_axe)
        self.assertEqual(result_again.status, "failure")
        self.assertIn("Tool 'axe' not found at 'forest'", result_again.message)

        # Attempt to pick up non-existent tool
        action_pickup_nonexistent = ActionCommand(action_type="pickup_tool", parameters={"tool_name": "laser_cutter"})
        result_nonexistent = self.env.step(self.agent_id, action_pickup_nonexistent)
        self.assertEqual(result_nonexistent.status, "failure")
        self.assertIn("Tool 'laser_cutter' not found at 'forest'", result_nonexistent.message)

        # Attempt to pick up with no tool_name
        action_pickup_notool = ActionCommand(action_type="pickup_tool", parameters={})
        result_notool = self.env.step(self.agent_id, action_pickup_notool)
        self.assertEqual(result_notool.status, "failure")
        self.assertIn("No tool_name specified", result_notool.message)


    def test_action_gather_resource_tool_logic(self):
        self.env.agent_location = "forest" # Wood (needs axe), stone (no tool needed here, let's add it)
        self.env.world_map["forest"]["resources"]["stone"] = 5 # Add stone that doesn't need a tool

        # 1. Gather stone (no tool needed)
        action_gather_stone = ActionCommand(action_type="gather_resource", parameters={"resource_type": "stone", "quantity_to_gather": 2})
        result_stone = self.env.step(self.agent_id, action_gather_stone)
        self.assertEqual(result_stone.status, "success")
        self.assertEqual(self.env.agent_inventory.get("stone"), 2)
        self.assertEqual(self.env.world_map["forest"]["resources"]["stone"], 3)

        # 2. Gather wood (needs axe, agent doesn't have it)
        action_gather_wood_no_axe = ActionCommand(action_type="gather_resource", parameters={"resource_type": "wood", "quantity_to_gather": 1})
        result_wood_no_axe = self.env.step(self.agent_id, action_gather_wood_no_axe)
        self.assertEqual(result_wood_no_axe.status, "failure")
        self.assertIn("requires tool 'axe'", result_wood_no_axe.message)
        self.assertEqual(self.env.agent_inventory.get("wood", 0), 0)

        # 3. Agent picks up axe
        action_pickup_axe = ActionCommand(action_type="pickup_tool", parameters={"tool_name": "axe"})
        self.env.step(self.agent_id, action_pickup_axe)
        self.assertEqual(self.env.agent_inventory.get("axe"), 1)

        # 4. Agent gathers wood (has axe)
        action_gather_wood_with_axe = ActionCommand(action_type="gather_resource", parameters={"resource_type": "wood", "quantity_to_gather": 3})
        result_wood_with_axe = self.env.step(self.agent_id, action_gather_wood_with_axe)
        self.assertEqual(result_wood_with_axe.status, "success")
        self.assertEqual(self.env.agent_inventory.get("wood"), 3)
        self.assertEqual(self.env.world_map["forest"]["resources"]["wood"]["quantity"], 7) # 10 - 3

    def test_action_craft_item_tool_logic(self):
        self.env.agent_location = "workshop" # Has workbench
        self.env.agent_inventory = {"wooden_plank": 5, "stick": 4, "stone": 3} # Agent has wood planks

        # 1. Craft basic_axe (needs hammer, agent has no tools yet)
        action_craft_axe_no_hammer = ActionCommand(action_type="craft_item", parameters={"item_name": "basic_axe"})
        result_axe_no_hammer = self.env.step(self.agent_id, action_craft_axe_no_hammer)
        self.assertEqual(result_axe_no_hammer.status, "failure")
        self.assertIn("requires tool 'hammer'", result_axe_no_hammer.message)

        # 2. Agent picks up hammer
        action_pickup_hammer = ActionCommand(action_type="pickup_tool", parameters={"tool_name": "hammer"})
        self.env.step(self.agent_id, action_pickup_hammer)
        self.assertEqual(self.env.agent_inventory.get("hammer"), 1)

        # 3. Craft basic_axe (has hammer, ingredients, at workbench)
        result_axe_with_hammer = self.env.step(self.agent_id, action_craft_axe_no_hammer) # Try same action again
        self.assertEqual(result_axe_with_hammer.status, "success")
        self.assertEqual(self.env.agent_inventory.get("basic_axe"), 1)
        self.assertEqual(self.env.agent_inventory.get("stick"), 2) # 4 - 2
        self.assertEqual(self.env.agent_inventory.get("stone"), 0) # 3 - 3 (should be removed)
        self.assertNotIn("stone", self.env.agent_inventory)


        # 4. Craft refined_wood (needs saw, agent has hammer and planks)
        action_craft_refined_no_saw = ActionCommand(action_type="craft_item", parameters={"item_name": "refined_wood"})
        result_refined_no_saw = self.env.step(self.agent_id, action_craft_refined_no_saw)
        self.assertEqual(result_refined_no_saw.status, "failure")
        self.assertIn("requires tool 'saw'", result_refined_no_saw.message)

        # 5. Agent picks up saw
        action_pickup_saw = ActionCommand(action_type="pickup_tool", parameters={"tool_name": "saw"})
        self.env.step(self.agent_id, action_pickup_saw)
        self.assertEqual(self.env.agent_inventory.get("saw"), 1)

        # 6. Craft refined_wood (has saw, planks, at workbench)
        result_refined_with_saw = self.env.step(self.agent_id, action_craft_refined_no_saw)
        self.assertEqual(result_refined_with_saw.status, "success")
        self.assertEqual(self.env.agent_inventory.get("refined_wood"), 1)
        # wooden_plank initial: 5 (used 3 for axe) -> 2. Used 2 for refined_wood -> 0
        self.assertNotIn("wooden_plank", self.env.agent_inventory)

        # 7. Craft rope (no tool, no station needed)
        self.env.agent_inventory["plant_fiber"] = 3
        action_craft_rope = ActionCommand(action_type="craft_item", parameters={"item_name": "rope"})
        result_rope = self.env.step(self.agent_id, action_craft_rope)
        self.assertEqual(result_rope.status, "success")
        self.assertEqual(self.env.agent_inventory.get("rope"),1)


    def test_get_observation_shows_tools(self):
        self.env.agent_location = "workshop" # Has hammer and saw
        obs = self.env.get_observation(self.agent_id)

        self.assertIn("hammer", obs.custom_sensor_data['current_location_info']['tools_present'])
        self.assertIn("saw", obs.custom_sensor_data['current_location_info']['tools_present'])

        found_text_percept = False
        for percept in obs.textual_percepts:
            if "Tools available here: hammer, saw" in percept.text or "Tools available here: saw, hammer" in percept.text :
                found_text_percept = True
                break
        self.assertTrue(found_text_percept, "Textual percept for tools not found or incorrect.")

    def test_get_action_space_shows_pickup_tool(self):
        self.env.agent_location = "mine" # Has pickaxe
        actions = self.env.get_action_space(self.agent_id)

        pickup_pickaxe_action = {"action_type": "pickup_tool", "parameters": {"tool_name": "pickaxe"}}
        self.assertIn(pickup_pickaxe_action, actions)

    def test_get_environment_info_schema_for_tools(self):
        info = self.env.get_environment_info()
        action_schema = info["action_schema"]
        self.assertIn("pickup_tool", action_schema)
        self.assertEqual(action_schema["pickup_tool"], {"tool_name": "string (name of tool to pick up)"})
        self.assertIn("note", action_schema["gather_resource"])
        self.assertIn("note", action_schema["craft_item"])

        perception_loc_info = info["perception_schema"]["custom_sensor_data"]["current_location_info"]
        self.assertIn("tools_present", perception_loc_info)


    def test_get_state_includes_tools(self):
        # Setup: Agent picks up axe, one tool remains in forest
        self.env.agent_location = "forest"
        self.env.step(self.agent_id, ActionCommand(action_type="pickup_tool", parameters={"tool_name": "axe"}))

        state = self.env.get_state()

        self.assertEqual(state["agent_inventory"].get("axe"), 1)
        self.assertNotIn("axe", state["world_map_current_state"]["forest"]["tools_present"]) # Axe picked up

        # Check another location for tools
        self.assertIn("hammer", state["world_map_current_state"]["workshop"]["tools_present"])


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
