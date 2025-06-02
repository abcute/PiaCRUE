import unittest
import os
import sys

# Adjust path to import from the environments directory
# Assuming tests/ is a sibling of environments/ under PiaSE/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'environments')))

try:
    from text_based_room import TextBasedRoom
except ImportError as e:
    print(f"ImportError: {e}. Attempting fallback import for TextBasedRoom.")
    # Fallback for different execution contexts, e.g. if PiaSE is in PYTHONPATH
    # This assumes PiaAGI_Research_Tools is the top-level package recognized by Python.
    # The path from project root would be PiaAGI_Research_Tools.PiaSE.environments.text_based_room
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
    try:
        from PiaAGI_Research_Tools.PiaSE.environments.text_based_room import TextBasedRoom
    except ImportError as e2:
        print(f"Fallback ImportError: {e2}. TextBasedRoom could not be imported.")
        TextBasedRoom = None # Define as None to allow test structure parsing, but tests will fail.


class TestTextBasedRoom(unittest.TestCase):
    def setUp(self):
        if TextBasedRoom is None:
            self.skipTest("TextBasedRoom module could not be imported. Skipping tests.")
        self.env = TextBasedRoom() # Uses default scenario
        self.agent_id = "agent_0" # Default agent from scenario
        # Suppress print statements from the environment during tests
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        if TextBasedRoom is not None: # Only close if it was opened
            sys.stdout.close()
            sys.stdout = self._original_stdout

    def test_initial_perception(self):
        perception = self.env.get_perceptual_data_for_agent(self.agent_id)
        self.assertEqual(perception["room_name"], "study")
        self.assertIn("study", perception["room_description"].lower())
        self.assertIn("desk", perception["visible_objects"])

    def test_action_go_valid(self):
        action = {"action_type": "go", "parameters": {"direction": "north"}}
        result = self.env.apply_action_from_agent(self.agent_id, action)
        self.assertEqual(result["status"], "success")
        self.assertIn("hallway", result["message"].lower())
        self.assertEqual(self.env.agent_states[self.agent_id]["current_room"], "hallway")

    def test_action_go_invalid(self):
        action = {"action_type": "go", "parameters": {"direction": "south"}} # No south exit from study
        result = self.env.apply_action_from_agent(self.agent_id, action)
        self.assertEqual(result["status"], "failure")
        self.assertIn("cannot go south", result["message"].lower())
        self.assertEqual(self.env.agent_states[self.agent_id]["current_room"], "study") # Still in study

    def test_action_look_room(self):
        action = {"action_type": "look", "parameters": {}}
        result = self.env.apply_action_from_agent(self.agent_id, action)
        self.assertEqual(result["status"], "success")
        self.assertIn("study", result["message"].lower()) # Checks room description

    def test_action_look_object_valid(self):
        action = {"action_type": "look", "parameters": {"target": "desk"}}
        result = self.env.apply_action_from_agent(self.agent_id, action)
        self.assertEqual(result["status"], "success")
        self.assertIn("oak desk", result["message"].lower())

    def test_action_look_object_invalid(self):
        action = {"action_type": "look", "parameters": {"target": "window"}} # Window not in default study
        result = self.env.apply_action_from_agent(self.agent_id, action)
        self.assertEqual(result["status"], "failure")
        self.assertIn("don't see 'window'", result["message"].lower())

    def test_action_take_object_valid(self):
        # Agent needs to be in hallway to take the key
        self.env.agent_states[self.agent_id]["current_room"] = "hallway"

        action = {"action_type": "take", "parameters": {"item_name": "key"}}
        result = self.env.apply_action_from_agent(self.agent_id, action)
        self.assertEqual(result["status"], "success")
        self.assertIn("you take the key", result["message"].lower())
        self.assertIn("key", self.env.agent_states[self.agent_id]["inventory"])
        self.assertNotIn("key", self.env.room_layout["hallway"]["objects"])

    def test_action_take_object_not_takeable(self):
        # Desk is not takeable by default
        action = {"action_type": "take", "parameters": {"item_name": "desk"}}
        result = self.env.apply_action_from_agent(self.agent_id, action)
        self.assertEqual(result["status"], "failure")
        self.assertIn("cannot take the desk", result["message"].lower())

    def test_action_take_object_not_present(self):
        action = {"action_type": "take", "parameters": {"item_name": "sword"}}
        result = self.env.apply_action_from_agent(self.agent_id, action)
        self.assertEqual(result["status"], "failure")
        self.assertIn("don't see a sword", result["message"].lower())

    def test_get_environment_info(self):
        info = self.env.get_environment_info()
        self.assertEqual(info["environment_name"], "TextBasedRoom_Prototype")
        self.assertIn("go", info["action_schema"])
        self.assertIn("visible_objects", info["perception_schema"])

    def test_reset_environment(self):
        self.env.agent_states[self.agent_id]["current_room"] = "hallway" # Change state
        self.env.agent_states[self.agent_id]["inventory"].append("test_item")

        # Use the environment's internal method to get a fresh default scenario for testing reset
        custom_scenario = self.env._get_default_scenario()
        custom_scenario["room_layout"]["study"]["description"] = "A very different study."
        custom_scenario["agent_setup"]["initial_inventory"] = ["map"] # Test different initial inventory

        self.env.reset_environment(scenario_data=custom_scenario)

        perception = self.env.get_perceptual_data_for_agent(self.agent_id)
        self.assertEqual(self.env.agent_states[self.agent_id]["current_room"], "study") # Reset to start_room
        self.assertEqual(self.env.agent_states[self.agent_id]["inventory"], ["map"]) # Reset inventory
        self.assertIn("very different study", perception["room_description"].lower())

    def test_register_new_agent(self):
        new_agent_id = "agent_1"
        self.env.register_agent(new_agent_id, start_room_id="hallway", initial_inventory=["lantern"])
        self.assertIn(new_agent_id, self.env.agent_states)
        self.assertEqual(self.env.agent_states[new_agent_id]["current_room"], "hallway")
        self.assertIn("lantern", self.env.agent_states[new_agent_id]["inventory"])

        # Test registering an existing agent (should print but not alter)
        self.env.register_agent(self.agent_id)
        self.assertEqual(self.env.agent_states[self.agent_id]["current_room"], "study") # Should remain in original start room


if __name__ == '__main__':
    unittest.main()
