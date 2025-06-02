import unittest
import time # For PerceptionData, ActionResult timestamps, though not directly asserted here

from PiaAGI_Research_Tools.PiaSE.environments.text_based_room import TextBasedRoom
from PiaAGI_Research_Tools.PiaSE.core_engine.interfaces import ActionCommand, PerceptionData, ActionResult

# Sample data for testing
SAMPLE_ROOM_LAYOUT = {
    "study": {
        "description": "a quiet study",
        "exits": {"north": "hallway"},
        "objects": ["desk", "journal_on_floor"]
    },
    "hallway": {
        "description": "a short hallway",
        "exits": {"south": "study"},
        "objects": []
    }
}

SAMPLE_OBJECT_DETAILS = {
    "desk": {
        "description": "a sturdy oak desk",
        "is_container": True,
        "is_open": False,
        "contains": ["hidden_key"],
        "locked": True,
        "key_required": "small_key"
    },
    "journal_on_floor": {
        "description": "an old journal lying on the floor",
        "can_be_taken": True,
        "read_text": "The desk needs a small key."
    },
    "hidden_key": { # Starts inside the desk
        "description": "a small, ornate key",
        "can_be_taken": True
    },
    "small_key": { # Agent might acquire this elsewhere to use on desk
        "description": "a small, plain key",
        "can_be_taken": True
    }
}

AGENT_ID = "test_agent_01"

class TestTextBasedRoom(unittest.TestCase):

    def setUp(self):
        self.env = TextBasedRoom(
            room_layout=SAMPLE_ROOM_LAYOUT,
            object_details=SAMPLE_OBJECT_DETAILS,
            agent_start_room="study",
            agent_id=AGENT_ID
        )
        # self.env.reset() # Reset is called in __init__

    def test_initialization_and_reset(self):
        self.assertEqual(self.env.agent_states[AGENT_ID]["current_room"], "study")
        initial_perception = self.env.get_observation(AGENT_ID)
        self.assertIsInstance(initial_perception, PerceptionData)
        self.assertEqual(initial_perception.sensor_data["room_name"], "study")
        self.assertIn("study", initial_perception.sensor_data["description"])

    def test_action_go(self):
        # Go to hallway
        action_cmd = ActionCommand(action_type="go", parameters={"direction": "north"})
        action_result = self.env.step(AGENT_ID, action_cmd)

        self.assertEqual(action_result.status, "success")
        self.assertIn("moved north", action_result.message.lower())
        self.assertEqual(self.env.agent_states[AGENT_ID]["current_room"], "hallway")

        # Try invalid direction
        action_cmd_fail = ActionCommand(action_type="go", parameters={"direction": "west"})
        action_result_fail = self.env.step(AGENT_ID, action_cmd_fail)
        self.assertEqual(action_result_fail.status, "failure")
        self.assertIn("cannot go west", action_result_fail.message.lower())

    def test_action_look_around(self):
        action_cmd = ActionCommand(action_type="look", parameters={})
        action_result = self.env.step(AGENT_ID, action_cmd)
        self.assertEqual(action_result.status, "success")
        self.assertIn("you look around", action_result.message.lower())
        self.assertIsNotNone(action_result.new_perception_snippet)
        self.assertEqual(action_result.new_perception_snippet.sensor_data["room_name"], "study")

    def test_action_look_at_object(self):
        action_cmd = ActionCommand(action_type="look", parameters={"target": "desk"})
        action_result = self.env.step(AGENT_ID, action_cmd)
        self.assertEqual(action_result.status, "success")
        self.assertIn("you look at desk", action_result.message.lower())
        self.assertIn("sturdy oak desk", action_result.message.lower())
        self.assertIn("closed", action_result.message.lower()) # Desk starts closed

    def test_action_inventory(self):
        # Initially empty
        action_cmd = ActionCommand(action_type="inventory", parameters={})
        action_result = self.env.step(AGENT_ID, action_cmd)
        self.assertEqual(action_result.status, "success")
        self.assertIn("inventory is empty", action_result.message.lower())

        # Manually add an item to inventory for testing drop later
        self.env.agent_states[AGENT_ID]["inventory"].append("small_key")
        action_result_with_item = self.env.step(AGENT_ID, action_cmd)
        self.assertEqual(action_result_with_item.status, "success")
        self.assertIn("you have: small_key", action_result_with_item.message.lower())


    def test_action_take_and_drop(self):
        # Take journal
        action_cmd_take = ActionCommand(action_type="take", parameters={"item_name": "journal_on_floor"})
        action_result_take = self.env.step(AGENT_ID, action_cmd_take)
        self.assertEqual(action_result_take.status, "success", msg=action_result_take.message)
        self.assertIn("journal_on_floor", self.env.agent_states[AGENT_ID]["inventory"])
        self.assertNotIn("journal_on_floor", self.env.current_room_layout["study"]["objects"])

        # Drop journal
        action_cmd_drop = ActionCommand(action_type="drop", parameters={"item_name": "journal_on_floor"})
        action_result_drop = self.env.step(AGENT_ID, action_cmd_drop)
        self.assertEqual(action_result_drop.status, "success", msg=action_result_drop.message)
        self.assertNotIn("journal_on_floor", self.env.agent_states[AGENT_ID]["inventory"])
        self.assertIn("journal_on_floor", self.env.current_room_layout["study"]["objects"])

    def test_action_open_locked_and_unlocked_container(self):
        # Try to open locked desk
        action_cmd_open_locked = ActionCommand(action_type="open", parameters={"target_object": "desk"})
        action_result_open_locked = self.env.step(AGENT_ID, action_cmd_open_locked)
        self.assertEqual(action_result_open_locked.status, "failure", msg=action_result_open_locked.message)
        self.assertIn("desk is locked", action_result_open_locked.message.lower())

        # Manually give agent the key and unlock the desk for testing 'open' on unlocked
        self.env.agent_states[AGENT_ID]["inventory"].append("small_key")
        action_cmd_use_key = ActionCommand(action_type="use", parameters={"item_name": "small_key", "target_object": "desk"})
        self.env.step(AGENT_ID, action_cmd_use_key) # Unlock it

        # Now open the (unlocked) desk
        action_cmd_open_unlocked = ActionCommand(action_type="open", parameters={"target_object": "desk"})
        action_result_open_unlocked = self.env.step(AGENT_ID, action_cmd_open_unlocked)
        self.assertEqual(action_result_open_unlocked.status, "success", msg=action_result_open_unlocked.message)
        self.assertTrue(self.env.current_object_details["desk"]["is_open"])
        self.assertIn("inside, you see: hidden_key", action_result_open_unlocked.message.lower())

    def test_action_take_from_container(self):
        # Setup: Unlock and open desk
        self.env.agent_states[AGENT_ID]["inventory"].append("small_key")
        action_cmd_use_key = ActionCommand(action_type="use", parameters={"item_name": "small_key", "target_object": "desk"})
        self.env.step(AGENT_ID, action_cmd_use_key)
        action_cmd_open_desk = ActionCommand(action_type="open", parameters={"target_object": "desk"})
        self.env.step(AGENT_ID, action_cmd_open_desk)

        # Take hidden_key from desk
        action_cmd_take = ActionCommand(action_type="take", parameters={"item_name": "hidden_key"})
        action_result_take = self.env.step(AGENT_ID, action_cmd_take)

        self.assertEqual(action_result_take.status, "success", msg=action_result_take.message)
        self.assertIn("hidden_key", self.env.agent_states[AGENT_ID]["inventory"])
        self.assertNotIn("hidden_key", self.env.current_object_details["desk"]["contains"])
        self.assertIn("took the hidden_key from the desk", action_result_take.message.lower())

    def test_action_read(self):
        # Take journal first
        self.env.step(AGENT_ID, ActionCommand(action_type="take", parameters={"item_name": "journal_on_floor"}))

        action_cmd_read = ActionCommand(action_type="read", parameters={"item_name": "journal_on_floor"})
        action_result_read = self.env.step(AGENT_ID, action_cmd_read)
        self.assertEqual(action_result_read.status, "success", msg=action_result_read.message)
        self.assertIn("it reads: \"the desk needs a small key.\"", action_result_read.message.lower())
        self.assertTrue(self.env.agent_states[AGENT_ID]["flags"].get("read_journal_on_floor"))

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

```
