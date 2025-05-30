import unittest
import os
import sys

# Adjust path to import from the parent directory (PiaCML)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from concrete_motivational_system_module import ConcreteMotivationalSystemModule
except ImportError:
    if 'ConcreteMotivationalSystemModule' not in globals(): # Fallback
        from PiaAGI_Hub.PiaCML.concrete_motivational_system_module import ConcreteMotivationalSystemModule

class TestConcreteMotivationalSystemModule(unittest.TestCase):

    def setUp(self):
        self.mot_sys = ConcreteMotivationalSystemModule()
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_initial_status(self):
        status = self.mot_sys.get_module_status()
        self.assertEqual(status['module_type'], 'ConcreteMotivationalSystemModule')
        self.assertEqual(status['total_goals'], 0)
        self.assertEqual(status['goals_by_status'], {})
        self.assertEqual(status['current_motivation_state']['overall_drive_level'], 0.7) # Default

    def test_add_goal(self):
        goal_data = {"description": "Test Goal 1", "type": "extrinsic", "priority": 0.5}
        goal_id = self.mot_sys.manage_goals(action="add", goal_data=goal_data)
        self.assertIsInstance(goal_id, str)
        self.assertTrue(goal_id.startswith("goal_"))

        status = self.mot_sys.get_module_status()
        self.assertEqual(status['total_goals'], 1)
        self.assertEqual(status['goals_by_status'].get('pending'), 1)

        all_goals = self.mot_sys.manage_goals(action="list_all")
        self.assertEqual(all_goals[0]['description'], "Test Goal 1")

    def test_add_goal_missing_data(self):
        result = self.mot_sys.manage_goals(action="add", goal_data={"description": "Incomplete"})
        self.assertFalse(result)

    def test_update_goal_status(self):
        goal_id = self.mot_sys.manage_goals(action="add", goal_data={"description": "Update Me", "type": "intrinsic", "priority": 0.8})
        update_success = self.mot_sys.manage_goals(action="update_status", goal_data={"id": goal_id, "status": "active"})
        self.assertTrue(update_success)

        all_goals = self.mot_sys.manage_goals(action="list_all")
        self.assertEqual(all_goals[0]['status'], "active")
        self.assertEqual(self.mot_sys.get_module_status()['goals_by_status'].get('active'), 1)

    def test_update_goal_status_non_existent(self):
        update_fail = self.mot_sys.manage_goals(action="update_status", goal_data={"id": "fake_id", "status": "active"})
        self.assertFalse(update_fail)

    def test_remove_goal(self):
        goal_id = self.mot_sys.manage_goals(action="add", goal_data={"description": "Delete Me", "type": "extrinsic", "priority": 0.1})
        self.assertEqual(self.mot_sys.get_module_status()['total_goals'], 1)
        remove_success = self.mot_sys.manage_goals(action="remove", goal_data={"id": goal_id})
        self.assertTrue(remove_success)
        self.assertEqual(self.mot_sys.get_module_status()['total_goals'], 0)

    def test_remove_goal_non_existent(self):
        remove_fail = self.mot_sys.manage_goals(action="remove", goal_data={"id": "fake_id"})
        self.assertFalse(remove_fail)

    def test_get_active_goals_ordering_and_filtering(self):
        g1_id = self.mot_sys.manage_goals("add", {"description": "G1_Active_Low", "type": "t", "priority": 0.3, "status": "active"})
        g2_id = self.mot_sys.manage_goals("add", {"description": "G2_Pending_High", "type": "t", "priority": 0.9, "status": "pending"})
        g3_id = self.mot_sys.manage_goals("add", {"description": "G3_Active_High", "type": "t", "priority": 0.8, "status": "active"})
        g4_id = self.mot_sys.manage_goals("add", {"description": "G4_Active_Mid", "type": "t", "priority": 0.5, "status": "active"})

        active_goals = self.mot_sys.get_active_goals()
        self.assertEqual(len(active_goals), 3)
        self.assertEqual(active_goals[0]['id'], g3_id) # Highest priority active
        self.assertEqual(active_goals[1]['id'], g4_id)
        self.assertEqual(active_goals[2]['id'], g1_id)

        top_2 = self.mot_sys.get_active_goals(N=2)
        self.assertEqual(len(top_2), 2)
        self.assertEqual(top_2[0]['id'], g3_id)

        min_p_goals = self.mot_sys.get_active_goals(min_priority=0.6)
        self.assertEqual(len(min_p_goals), 1)
        self.assertEqual(min_p_goals[0]['id'], g3_id)

        no_active = self.mot_sys.get_active_goals(min_priority=1.0) # No goals with priority 1.0 or more
        self.assertEqual(len(no_active),0)


    def test_update_motivation_state_placeholder(self):
        initial_state = self.mot_sys.get_module_status()['current_motivation_state']
        update_success = self.mot_sys.update_motivation_state({
            "overall_drive_level": 0.95,
            "current_focus_theme": "testing"
        })
        self.assertTrue(update_success)
        new_state = self.mot_sys.get_module_status()['current_motivation_state']
        self.assertEqual(new_state['overall_drive_level'], 0.95)
        self.assertEqual(new_state['current_focus_theme'], "testing")

        # Test partial update
        self.mot_sys.update_motivation_state({"overall_drive_level": 0.8})
        partial_update_state = self.mot_sys.get_module_status()['current_motivation_state']
        self.assertEqual(partial_update_state['overall_drive_level'], 0.8)
        self.assertEqual(partial_update_state['current_focus_theme'], "testing") # Should persist


    def test_list_all_goals(self):
        g1 = self.mot_sys.manage_goals(action="add", goal_data={"description":"g1","type":"t","priority":0.1})
        g2 = self.mot_sys.manage_goals(action="add", goal_data={"description":"g2","type":"t","priority":0.9})
        all_goals = self.mot_sys.manage_goals(action="list_all")
        self.assertEqual(len(all_goals), 2)
        # Check if sorted by priority (desc)
        self.assertEqual(all_goals[0]['id'], g2)


if __name__ == '__main__':
    unittest.main()
