import unittest
import time
import os
import sys

# Adjust path to import from the parent directory (PiaCML)
# This goes two levels up from tests/ to PiaAGI_Research_Tools/
# Then one level up to the root of the project to allow PiaAGI_Research_Tools.PiaCML import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    from PiaAGI_Research_Tools.PiaCML.concrete_motivational_system_module import ConcreteMotivationalSystemModule, Goal
except ModuleNotFoundError:
    # Fallback if the above doesn't work (e.g. when CWD is already PiaAGI_Research_Tools)
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from concrete_motivational_system_module import ConcreteMotivationalSystemModule, Goal


class TestConcreteMotivationalSystemModule(unittest.TestCase):

    def setUp(self):
        self.mot_sys = ConcreteMotivationalSystemModule()
        self._original_stdout = sys.stdout
        # Suppress prints from the module during tests for cleaner output
        # sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        """Restore stdout after each test."""
        # sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_initial_state(self):
        """Test the initial state of the motivational system."""
        self.assertEqual(len(self.mot_sys.goals), 0)
        self.assertEqual(self.mot_sys.next_goal_id, 0)
        status = self.mot_sys.get_module_status()
        self.assertEqual(status["total_goals"], 0)

    def test_add_goal(self):
        """Test adding a new goal."""
        goal_id = self.mot_sys.add_goal(
            description="Test Goal 1",
            goal_type="EXTRINSIC_TASK",
            initial_priority=0.7,
            source_trigger={"type": "user_request"}
        )
        self.assertTrue(goal_id.startswith("goal_"))
        self.assertEqual(len(self.mot_sys.goals), 1)
        added_goal = self.mot_sys.goals[0]
        self.assertEqual(added_goal.id, goal_id)
        self.assertEqual(added_goal.description, "Test Goal 1")
        self.assertEqual(added_goal.type, "EXTRINSIC_TASK")
        self.assertEqual(added_goal.priority, 0.7)
        self.assertEqual(added_goal.status, "PENDING")
        self.assertIsNotNone(added_goal.creation_timestamp)
        self.assertEqual(added_goal.source_trigger, {"type": "user_request"})
        self.assertEqual(self.mot_sys.next_goal_id, 1)

    def test_get_goal(self):
        """Test retrieving a goal by ID."""
        goal_id = self.mot_sys.add_goal("Test Get Goal", "TEST_TYPE", 0.5)
        retrieved_goal = self.mot_sys.get_goal(goal_id)
        self.assertIsNotNone(retrieved_goal)
        self.assertEqual(retrieved_goal.id, goal_id)

        non_existent_goal = self.mot_sys.get_goal("goal_999")
        self.assertIsNone(non_existent_goal)

    def test_update_goal_status(self):
        """Test updating a goal's status."""
        goal_id = self.mot_sys.add_goal("Status Update Goal", "TEST_TYPE", 0.5)

        self.assertTrue(self.mot_sys.update_goal_status(goal_id, "ACTIVE"))
        goal = self.mot_sys.get_goal(goal_id)
        self.assertEqual(goal.status, "ACTIVE")

        self.assertFalse(self.mot_sys.update_goal_status("goal_999", "ACHIEVED"))

    def test_update_goal_priority(self):
        """Test updating a goal's priority."""
        goal_id = self.mot_sys.add_goal("Priority Update Goal", "TEST_TYPE", 0.5)

        self.assertTrue(self.mot_sys.update_goal_priority(goal_id, 0.9))
        goal = self.mot_sys.get_goal(goal_id)
        self.assertEqual(goal.priority, 0.9)

        self.assertFalse(self.mot_sys.update_goal_priority("goal_999", 0.1))

    def test_get_active_goals(self):
        """Test retrieving active and pending goals, sorted by priority."""
        g1_id = self.mot_sys.add_goal("G1 Active Low", "T", 0.3, initial_status="ACTIVE")
        g2_id = self.mot_sys.add_goal("G2 Pending High", "T", 0.9, initial_status="PENDING")
        g3_id = self.mot_sys.add_goal("G3 Active High", "T", 0.8, initial_status="ACTIVE")
        g4_id = self.mot_sys.add_goal("G4 Achieved Mid", "T", 0.5, initial_status="ACHIEVED") # Not active
        g5_id = self.mot_sys.add_goal("G5 Pending Mid", "T", 0.6, initial_status="PENDING")

        active_goals = self.mot_sys.get_active_goals()
        self.assertEqual(len(active_goals), 4) # G1, G2, G3, G5

        # Check sorting by priority (descending)
        self.assertEqual(active_goals[0].id, g2_id) # Prio 0.9
        self.assertEqual(active_goals[1].id, g3_id) # Prio 0.8
        self.assertEqual(active_goals[2].id, g5_id) # Prio 0.6
        self.assertEqual(active_goals[3].id, g1_id) # Prio 0.3

    def test_assess_curiosity_triggers_novel_event(self):
        """Test curiosity goal generation from a novel world event."""
        novel_event = {"type": "NOVEL_STIMULUS", "id": "obj_xyz", "novelty_score": 0.8}
        new_goal_ids = self.mot_sys.assess_curiosity_triggers(world_event=novel_event)

        self.assertEqual(len(new_goal_ids), 1)
        curiosity_goal = self.mot_sys.get_goal(new_goal_ids[0])
        self.assertIsNotNone(curiosity_goal)
        self.assertEqual(curiosity_goal.type, "INTRINSIC_CURIOSITY")
        self.assertTrue("Investigate novel event: obj_xyz" in curiosity_goal.description)
        self.assertEqual(curiosity_goal.priority, 8.0) # 0.8 * 10
        self.assertEqual(curiosity_goal.source_trigger, novel_event)

        # Test event below threshold
        low_novelty_event = {"type": "NOVEL_STIMULUS", "id": "obj_abc", "novelty_score": 0.5}
        new_goal_ids_low = self.mot_sys.assess_curiosity_triggers(world_event=low_novelty_event)
        self.assertEqual(len(new_goal_ids_low), 0)

    def test_assess_curiosity_triggers_knowledge_gap(self):
        """Test curiosity goal generation from knowledge gaps."""
        knowledge_snapshot = {
            "concept1": {"confidence": 0.25, "last_explored_ts": time.time() - 3600},
            "concept2": {"confidence": 0.6}, # Should not trigger
            "concept3": {"confidence": 0.4}  # Should trigger
        }
        new_goal_ids = self.mot_sys.assess_curiosity_triggers(knowledge_map_snapshot=knowledge_snapshot)
        self.assertEqual(len(new_goal_ids), 2)

        goal_ids_found = {g.source_trigger["concept_id"]: g.id for g in self.mot_sys.goals if g.type == "INTRINSIC_CURIOSITY"}

        self.assertIn("concept1", goal_ids_found)
        goal1 = self.mot_sys.get_goal(goal_ids_found["concept1"])
        self.assertEqual(goal1.priority, (1.0 - 0.25) * 10) # 7.5

        self.assertIn("concept3", goal_ids_found)
        goal3 = self.mot_sys.get_goal(goal_ids_found["concept3"])
        self.assertEqual(goal3.priority, (1.0 - 0.4) * 10) # 6.0

        # Test that existing pending/active curiosity goals are not re-added
        knowledge_snapshot_repeat = {"concept1": {"confidence": 0.20}} # concept1 already has a goal
        new_goal_ids_repeat = self.mot_sys.assess_curiosity_triggers(knowledge_map_snapshot=knowledge_snapshot_repeat)
        self.assertEqual(len(new_goal_ids_repeat), 0, "Should not re-add existing curiosity goal for concept1")


    def test_suggest_highest_priority_goal(self):
        """Test suggesting the highest priority active/pending goal."""
        self.assertIsNone(self.mot_sys.suggest_highest_priority_goal(), "Should be None for empty list")

        g1_id = self.mot_sys.add_goal("Low Prio", "T", 0.2, initial_status="ACTIVE")
        self.assertEqual(self.mot_sys.suggest_highest_priority_goal().id, g1_id)

        g2_id = self.mot_sys.add_goal("High Prio", "T", 0.9, initial_status="PENDING")
        self.assertEqual(self.mot_sys.suggest_highest_priority_goal().id, g2_id)

        g3_id = self.mot_sys.add_goal("Mid Prio Active", "T", 0.5, initial_status="ACTIVE")
        self.assertEqual(self.mot_sys.suggest_highest_priority_goal().id, g2_id) # g2 still highest

        self.mot_sys.update_goal_status(g2_id, "ACHIEVED") # g2 no longer active
        self.assertEqual(self.mot_sys.suggest_highest_priority_goal().id, g3_id) # g3 should now be highest

        self.mot_sys.update_goal_status(g3_id, "FAILED")
        self.assertEqual(self.mot_sys.suggest_highest_priority_goal().id, g1_id) # Only g1 left active

        self.mot_sys.update_goal_status(g1_id, "BLOCKED")
        self.assertIsNone(self.mot_sys.suggest_highest_priority_goal(), "Should be None if all active goals are blocked/failed/achieved")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
