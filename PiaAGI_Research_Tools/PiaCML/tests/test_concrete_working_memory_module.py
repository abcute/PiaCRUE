import unittest
import os
import sys

# Adjust path to import from the parent directory (PiaCML)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from concrete_working_memory_module import ConcreteWorkingMemoryModule
except ImportError:
    if 'ConcreteWorkingMemoryModule' not in globals(): # Fallback for different execution contexts
        from PiaAGI_Hub.PiaCML.concrete_working_memory_module import ConcreteWorkingMemoryModule

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

    def test_add_item_and_get_contents(self):
        id1 = self.wm.add_item_to_workspace({'data': 'item1'}, salience=0.5)
        self.assertRegex(id1, r"wm_item_\d+")
        contents = self.wm.get_workspace_contents()
        self.assertEqual(len(contents), 1)
        self.assertEqual(contents[0]['id'], id1)
        self.assertEqual(contents[0]['content'], {'data': 'item1'})
        self.assertEqual(self.wm.get_status()['current_size'], 1)

    def test_store_method_as_add_item(self):
        id_store = self.wm.store({'data': 'item_via_store'}, context={'salience': 0.6})
        contents = self.wm.get_workspace_contents()
        self.assertEqual(len(contents), 1)
        self.assertEqual(contents[0]['id'], id_store)
        self.assertEqual(contents[0]['content'], {'data': 'item_via_store'})
        self.assertEqual(contents[0]['salience'], 0.6)


    def test_capacity_management_add_item(self):
        id1 = self.wm.add_item_to_workspace("item1", 0.1)
        id2 = self.wm.add_item_to_workspace("item2", 0.2)
        id3 = self.wm.add_item_to_workspace("item3", 0.3)
        self.assertEqual(self.wm.get_status()['current_size'], 3)

        # This item has higher salience than item1, item1 should be removed
        id4 = self.wm.add_item_to_workspace("item4", 0.4)
        self.assertNotEqual(id4, "error_workspace_full")

        contents = self.wm.get_workspace_contents()
        self.assertEqual(len(contents), 3)
        item_ids = [item['id'] for item in contents]
        self.assertNotIn(id1, item_ids)
        self.assertIn(id4, item_ids)

        # This item has lower salience than all in workspace, should not be added
        id5_fail = self.wm.add_item_to_workspace("item5_fail", 0.05)
        self.assertEqual(id5_fail, "error_workspace_full") # Assuming this is the error code for full
        self.assertEqual(len(self.wm.get_workspace_contents()), 3)
        self.assertNotIn(id5_fail, [item['id'] for item in self.wm.get_workspace_contents()])


    def test_remove_item_from_workspace(self):
        id1 = self.wm.add_item_to_workspace("item1")
        self.wm.add_item_to_workspace("item2")
        self.assertTrue(self.wm.remove_item_from_workspace(id1))
        self.assertEqual(self.wm.get_status()['current_size'], 1)
        self.assertFalse(self.wm.remove_item_from_workspace(id1)) # Already removed
        self.assertFalse(self.wm.remove_item_from_workspace("non_existent_id"))


    def test_delete_memory_as_remove_item(self):
        id1 = self.wm.add_item_to_workspace("item1_del")
        self.assertTrue(self.wm.delete_memory(id1))
        self.assertEqual(self.wm.get_status()['current_size'], 0)


    def test_set_and_get_active_focus(self):
        id1 = self.wm.add_item_to_workspace("item_focus_1", 0.5)
        id2 = self.wm.add_item_to_workspace("item_focus_2", 0.6)

        self.assertTrue(self.wm.set_active_focus(id1))
        focused_item = self.wm.get_active_focus()
        self.assertIsNotNone(focused_item)
        self.assertEqual(focused_item['id'], id1)
        self.assertGreater(focused_item['salience'], 0.5) # Salience boosted

        self.assertFalse(self.wm.set_active_focus("non_existent"))
        self.assertIsNotNone(self.wm.get_active_focus()) # Focus should remain on id1

    def test_remove_focused_item_clears_focus(self):
        id1 = self.wm.add_item_to_workspace("item_focus_rem", 0.7)
        self.wm.set_active_focus(id1)
        self.assertIsNotNone(self.wm.get_active_focus())
        self.wm.remove_item_from_workspace(id1)
        self.assertIsNone(self.wm.get_active_focus())


    def test_retrieve_by_id(self):
        id1 = self.wm.add_item_to_workspace({'name': "Pia"}, 0.5)
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
        id1 = self.wm.add_item_to_workspace("item_a")
        id2 = self.wm.add_item_to_workspace("item_b")
        all_items = self.wm.retrieve({})
        self.assertEqual(len(all_items), 2)
        item_ids = [item['id'] for item in all_items]
        self.assertIn(id1, item_ids)
        self.assertIn(id2, item_ids)


    def test_manage_capacity_method(self):
        # This method is mostly called internally by store/add_item, but test direct call
        self.wm.add_item_to_workspace("i1", 0.1)
        self.wm.add_item_to_workspace("i2", 0.2)
        self.wm.add_item_to_workspace("i3", 0.3)
        self.wm.add_item_to_workspace("i4", 0.05) # this should be in, replacing i1 if capacity was 3

        # If capacity is 3, i1 (0.1) should have been replaced by i4 (0.05) because i4 was added last and i1 was least salient
        # The current logic in ConcreteWM for store is: if full, call manage_workspace_capacity.
        # manage_workspace_capacity removes least salient if new_item_salience is higher than it.
        # Let's re-verify the logic.
        # Setup: cap=3. items: (i1,0.1), (i2,0.2), (i3,0.3)
        # Add (i4,0.4). i1 removed. items: (i2,0.2), (i3,0.3), (i4,0.4)
        # Add (i5,0.05). wm is full. item with salience 0.2 (i2) is lowest. 0.05 < 0.2, so i5 NOT added.

        # Reset for clear test of manage_capacity directly
        self.wm = ConcreteWorkingMemoryModule(capacity=2)
        id_a = self.wm.add_item_to_workspace("A", 0.5)
        id_b = self.wm.add_item_to_workspace("B", 0.6)
        id_c_fail = self.wm.add_item_to_workspace("C_fail", 0.1) # Fails as 0.1 < 0.5
        self.assertEqual(id_c_fail, "error_workspace_full")

        # Manually add a third item to exceed capacity for direct test
        self.wm._workspace.append({'id': 'temp_c', 'content': 'C_direct', 'salience': 0.1})
        self.assertEqual(len(self.wm._workspace), 3)

        self.wm.manage_capacity() # Should remove 'temp_c' (salience 0.1)

        contents = self.wm.get_workspace_contents()
        self.assertEqual(len(contents), 2)
        item_ids = [item['id'] for item in contents]
        self.assertIn(id_a, item_ids)
        self.assertIn(id_b, item_ids)
        self.assertNotIn('temp_c', item_ids)


    def test_handle_forgetting_decay_salience(self):
        id1 = self.wm.add_item_to_workspace("item_s1", salience=1.0)
        id2 = self.wm.add_item_to_workspace("item_s2", salience=0.5)

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
        self.assertEqual(contents[0]['id'], id2) # item_s2 should now be less salient
        self.assertEqual(contents[1]['id'], id1)


if __name__ == '__main__':
    unittest.main()
