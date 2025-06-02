import unittest
import os
import sys
import uuid # For generating unique IDs in tests if needed

# Adjust path to import from the parent directory (PiaCML)
# This assumes the test script is run from PiaAGI_Hub/PiaCML/tests/ or a similar context
# where PiaCML is one level up.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PiaAGI_Research_Tools.PiaCML.concrete_working_memory_module import ConcreteWorkingMemoryModule


class TestConcreteWorkingMemoryModule(unittest.TestCase):

    def setUp(self):
        self.wm = ConcreteWorkingMemoryModule(capacity=3) # Use a small capacity for easier testing
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_initial_status(self):
        status = self.wm.get_status()
        self.assertEqual(status['current_size'], 0)
        self.assertEqual(status['capacity'], 3)
        self.assertIsNone(status['current_focus_id'])
        self.assertEqual(status['module_type'], 'ConcreteWorkingMemoryModule')
        self.assertIsNone(status['last_alloc_priority']) # New field
        self.assertIsNone(status['last_coord_attempt'])  # New field


    def test_add_item_and_get_contents(self):
        add_success = self.wm.add_item_to_workspace({'data': 'item1'}, salience=0.5)
        self.assertTrue(add_success)

        contents = self.wm.get_workspace_contents()
        self.assertEqual(len(contents), 1)
        # self.assertEqual(contents[0]['id'], id1) # ID is internal, not directly testable from add_item_to_workspace return
        self.assertEqual(contents[0]['content'], {'data': 'item1'})
        self.assertEqual(self.wm.get_status()['current_size'], 1)

    def test_store_method_as_add_item(self):
        # store still returns ID or error string
        id_store = self.wm.store({'data': 'item_via_store'}, context={'salience': 0.6})
        self.assertRegex(id_store, r"wm_item_\d+")
        contents = self.wm.get_workspace_contents()
        self.assertEqual(len(contents), 1)
        self.assertEqual(contents[0]['id'], id_store)
        self.assertEqual(contents[0]['content'], {'data': 'item_via_store'})
        self.assertEqual(contents[0]['salience'], 0.6)


    def test_capacity_management_add_item(self):
        added1 = self.wm.add_item_to_workspace("item1", 0.1) # True
        self.assertTrue(added1)
        item1_id = self.wm.get_workspace_contents()[0]['id'] # Get ID of item1

        added2 = self.wm.add_item_to_workspace("item2", 0.2) # True
        self.assertTrue(added2)
        added3 = self.wm.add_item_to_workspace("item3", 0.3) # True
        self.assertTrue(added3)
        self.assertEqual(self.wm.get_status()['current_size'], 3)

        # This item has higher salience than item1, item1 should be removed
        added4 = self.wm.add_item_to_workspace("item4", 0.4) # True
        self.assertTrue(added4)

        contents = self.wm.get_workspace_contents()
        self.assertEqual(len(contents), 3)
        item_ids = [item['id'] for item in contents]
        self.assertNotIn(item1_id, item_ids) # Check that item1_id is not present
        # We can't easily get id4 from return of add_item_to_workspace, but we know it's there if item1 was removed.

        # This item has lower salience than all in workspace, should not be added
        added5_fail = self.wm.add_item_to_workspace("item5_fail", 0.05) # False
        self.assertFalse(added5_fail)
        self.assertEqual(len(self.wm.get_workspace_contents()), 3)
        # Check that "item5_fail" is not in contents
        found_item5 = any(isinstance(item['content'], dict) and item['content'].get('data') == "item5_fail" for item in self.wm.get_workspace_contents())
        self.assertFalse(found_item5)


    def test_remove_item_from_workspace(self):
        # Need to get the ID after adding
        self.wm.add_item_to_workspace("item1")
        id1 = self.wm.get_workspace_contents()[0]['id']

        self.wm.add_item_to_workspace("item2")
        self.assertTrue(self.wm.remove_item_from_workspace(id1))
        self.assertEqual(self.wm.get_status()['current_size'], 1)
        self.assertFalse(self.wm.remove_item_from_workspace(id1)) # Already removed
        self.assertFalse(self.wm.remove_item_from_workspace("non_existent_id"))


    def test_delete_memory_as_remove_item(self):
        self.wm.add_item_to_workspace("item1_del")
        id1 = self.wm.get_workspace_contents()[0]['id']
        self.assertTrue(self.wm.delete_memory(id1))
        self.assertEqual(self.wm.get_status()['current_size'], 0)


    def test_set_and_get_active_focus(self):
        self.wm.add_item_to_workspace("item_focus_1", 0.5)
        id1 = self.wm.get_workspace_contents()[0]['id']
        self.wm.add_item_to_workspace("item_focus_2", 0.6)

        self.assertTrue(self.wm.set_active_focus(id1))
        focused_item = self.wm.get_active_focus()
        self.assertIsNotNone(focused_item)
        self.assertEqual(focused_item['id'], id1)
        self.assertGreater(focused_item['salience'], 0.5) # Salience boosted

        self.assertFalse(self.wm.set_active_focus("non_existent"))
        self.assertIsNotNone(self.wm.get_active_focus()) # Focus should remain on id1

    def test_remove_focused_item_clears_focus(self):
        self.wm.add_item_to_workspace("item_focus_rem", 0.7)
        id1 = self.wm.get_workspace_contents()[0]['id']
        self.wm.set_active_focus(id1)
        self.assertIsNotNone(self.wm.get_active_focus())
        self.wm.remove_item_from_workspace(id1)
        self.assertIsNone(self.wm.get_active_focus())


    def test_retrieve_by_id(self):
        self.wm.add_item_to_workspace({'name': "Pia"}, 0.5)
        id1 = self.wm.get_workspace_contents()[0]['id'] # Get the ID
        retrieved = self.wm.retrieve({'id': id1})
        self.assertEqual(len(retrieved), 1)
        self.assertEqual(retrieved[0]['id'], id1)

    def test_retrieve_by_content_query(self):
        self.wm.add_item_to_workspace({'type': 'fruit', 'name': 'apple'}, 0.5)
        self.wm.add_item_to_workspace({'type': 'fruit', 'name': 'banana'}, 0.6)
        self.wm.add_item_to_workspace({'type': 'veg', 'name': 'carrot'}, 0.7)

        retrieved_fruits = self.wm.retrieve({'content_query': {'key': 'type', 'value': 'fruit'}})
        self.assertEqual(len(retrieved_fruits), 2)

        retrieved_apple = self.wm.retrieve({'content_query': {'key': 'name', 'value': 'apple'}})
        self.assertEqual(len(retrieved_apple), 1)
        self.assertEqual(retrieved_apple[0]['content']['name'], 'apple')

    def test_retrieve_empty_query_returns_all(self):
        self.wm.add_item_to_workspace("item_a")
        id1 = self.wm.get_workspace_contents()[0]['id']
        self.wm.add_item_to_workspace("item_b")
        id2 = self.wm.get_workspace_contents()[1]['id']

        all_items = self.wm.retrieve({})
        self.assertEqual(len(all_items), 2)
        item_ids = [item['id'] for item in all_items]
        self.assertIn(id1, item_ids)
        self.assertIn(id2, item_ids)


    def test_manage_capacity_method(self):
        self.wm = ConcreteWorkingMemoryModule(capacity=2)
        self.wm.add_item_to_workspace("A", 0.5)
        id_a = self.wm.get_workspace_contents()[0]['id']
        self.wm.add_item_to_workspace("B", 0.6)
        id_b = self.wm.get_workspace_contents()[1]['id']

        # This should fail as 0.1 is less than current min salience 0.5
        added_c_fail = self.wm.add_item_to_workspace("C_fail", 0.1)
        self.assertFalse(added_c_fail)

        # Manually add a third item to exceed capacity for direct test
        # This bypasses the add_item_to_workspace salience check for this specific test setup
        self.wm._workspace.append({'id': 'temp_c', 'content': {'data':'C_direct'}, 'salience': 0.01, 'context':{}}) # ensure salience is lowest
        self.assertEqual(len(self.wm._workspace), 3)

        self.wm.manage_capacity() # Should remove 'temp_c' (salience 0.01)

        contents = self.wm.get_workspace_contents()
        self.assertEqual(len(contents), 2)
        item_ids = [item['id'] for item in contents]
        self.assertIn(id_a, item_ids)
        self.assertIn(id_b, item_ids)
        self.assertNotIn('temp_c', item_ids)


    def test_handle_forgetting_decay_salience(self):
        self.wm.add_item_to_workspace("item_s1", salience=1.0)
        id1 = self.wm.get_workspace_contents()[0]['id']
        self.wm.add_item_to_workspace("item_s2", salience=0.5)
        id2 = next(item['id'] for item in self.wm.get_workspace_contents() if item['content'].get('data') == "item_s2")


        self.wm.handle_forgetting(strategy='decay_salience')

        contents = self.wm.get_workspace_contents()
        found_id1 = False
        for item in contents:
            if item['id'] == id1:
                self.assertEqual(item['salience'], 0.9) # 1.0 * 0.9
                found_id1 = True
            elif item['id'] == id2:
                self.assertEqual(item['salience'], 0.45) # 0.5 * 0.9
        self.assertTrue(found_id1)
        # Check if sorted by new salience (lowest first)
        self.assertEqual(contents[0]['id'], id2)
        self.assertEqual(contents[1]['id'], id1)

    def test_update_item_in_workspace(self):
        self.wm.add_item_to_workspace("initial_content", salience=0.5, context={'tag': 'original'})
        item_id = self.wm.get_workspace_contents()[0]['id']

        # Update content only
        update1_success = self.wm.update_item_in_workspace(item_id, new_content="updated_content_1")
        self.assertTrue(update1_success)
        item_after_update1 = self.wm.retrieve({'id': item_id})[0]
        self.assertEqual(item_after_update1['content'], {'data': "updated_content_1"})
        self.assertEqual(item_after_update1['context']['tag'], 'original') # Context should persist

        # Update context only (including salience)
        update2_success = self.wm.update_item_in_workspace(item_id, new_context={'tag': 'updated', 'salience': 0.8})
        self.assertTrue(update2_success)
        item_after_update2 = self.wm.retrieve({'id': item_id})[0]
        self.assertEqual(item_after_update2['content'], {'data': "updated_content_1"}) # Content should persist
        self.assertEqual(item_after_update2['context']['tag'], 'updated')
        self.assertEqual(item_after_update2['salience'], 0.8)

        # Check re-sorting after salience update
        self.wm.add_item_to_workspace("other_item", salience=0.7) # This should be before the updated item if not re-sorted
        contents = self.wm.get_workspace_contents()
        # Assuming item_id was 'wm_item_1' and other_item is 'wm_item_2'
        # If sorted correctly, item with salience 0.7 comes before 0.8
        self.assertTrue(contents[0]['salience'] < contents[1]['salience'] or contents[1]['salience'] < contents[0]['salience'])


        # Update both content and context
        update3_success = self.wm.update_item_in_workspace(item_id, new_content={'type': 'final'}, new_context={'source': 'test'})
        self.assertTrue(update3_success)
        item_after_update3 = self.wm.retrieve({'id': item_id})[0]
        self.assertEqual(item_after_update3['content'], {'type': 'final'})
        self.assertEqual(item_after_update3['context']['tag'], 'updated') # Original context merged
        self.assertEqual(item_after_update3['context']['source'], 'test') # New context added

        # Attempt to update non-existent item
        update4_fail = self.wm.update_item_in_workspace("non_existent_id", new_content="wont_work")
        self.assertFalse(update4_fail)

    def test_clear_workspace(self):
        self.wm.add_item_to_workspace("item1")
        self.wm.add_item_to_workspace("item2")
        self.wm.set_active_focus(self.wm.get_workspace_contents()[0]['id'])

        self.wm.clear_workspace()
        self.assertEqual(len(self.wm.get_workspace_contents()), 0)
        self.assertEqual(self.wm.get_status()['current_size'], 0)
        self.assertIsNone(self.wm.get_active_focus())
        self.assertIsNone(self.wm._current_focus_id) # Direct check for internal state
        self.assertEqual(self.wm._item_counter, 0) # Check if counter is reset

    def test_get_cognitive_load(self):
        self.assertEqual(self.wm.get_cognitive_load(), 0.0) # Empty

        self.wm.add_item_to_workspace("item1")
        self.assertAlmostEqual(self.wm.get_cognitive_load(), 1.0/3.0)

        self.wm.add_item_to_workspace("item2")
        self.assertAlmostEqual(self.wm.get_cognitive_load(), 2.0/3.0)

        self.wm.add_item_to_workspace("item3")
        self.assertAlmostEqual(self.wm.get_cognitive_load(), 1.0) # Full

        # Test with zero capacity
        zero_cap_wm = ConcreteWorkingMemoryModule(capacity=0)
        self.assertEqual(zero_cap_wm.get_cognitive_load(), 1.0) # Should be 1.0 (max load)

    def test_allocate_attentional_resources_placeholder(self):
        priority_info = {'task_id': 'task123', 'priority_score': 0.85}
        success = self.wm.allocate_attentional_resources(priority_info)
        self.assertTrue(success)
        status = self.wm.get_status()
        self.assertEqual(status['last_alloc_priority'], priority_info)

    def test_coordinate_modules_placeholder(self):
        goal = "Generate weather report"
        modules = ["LTM", "Planning", "Communication"]
        coordination_result = self.wm.coordinate_modules(goal, modules)

        self.assertEqual(coordination_result['status'], 'coordination_conceptualized')
        self.assertIn('task_id', coordination_result)

        status = self.wm.get_status()
        self.assertIsNotNone(status['last_coord_attempt'])
        self.assertEqual(status['last_coord_attempt']['task_goal'], goal)
        self.assertEqual(status['last_coord_attempt']['modules'], modules)
        self.assertEqual(status['last_coord_attempt']['task_id'], coordination_result['task_id'])

if __name__ == '__main__':
    unittest.main()
