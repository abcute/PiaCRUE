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
        self.bus = MessageBus() # Real bus for testing subscription
        self.wm_no_bus = ConcreteWorkingMemoryModule(capacity=3) # For tests not needing a bus
        self.wm_with_bus = ConcreteWorkingMemoryModule(capacity=3, message_bus=self.bus)

        self._original_stdout = sys.stdout
        # Comment out print suppression for easier debugging if tests fail
        # sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        # sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_initial_status(self):
        # Test instance without bus
        status_no_bus = self.wm_no_bus.get_status()
        self.assertEqual(status_no_bus['current_size'], 0)
        self.assertEqual(status_no_bus['capacity'], 3)
        self.assertIsNone(status_no_bus['current_focus_id'])
        self.assertEqual(status_no_bus['module_type'], 'ConcreteWorkingMemoryModule')
        self.assertIsNone(self.wm_no_bus.message_bus)
        self.assertEqual(len(self.wm_no_bus.received_percepts), 0)

        # Test instance with bus
        status_with_bus = self.wm_with_bus.get_status()
        self.assertEqual(status_with_bus['current_size'], 0)
        self.assertEqual(status_with_bus['capacity'], 3)
        self.assertIsNotNone(self.wm_with_bus.message_bus)
        self.assertEqual(len(self.wm_with_bus.received_percepts), 0)
        # Check subscription
        subscribers = self.bus.get_subscribers_for_type("PerceptData")
        self.assertTrue(any(sub[0] == "ConcreteWorkingMemoryModule_01" and sub[1] == self.wm_with_bus.handle_percept_data_message for sub in subscribers))

    # --- Tests for MessageBus Integration ---
    def test_handle_percept_data_message(self):
        """Test that WM receives and stores PerceptData messages from the bus."""
        self.assertEqual(len(self.wm_with_bus.received_percepts), 0)

        source_ts = datetime.datetime.now(datetime.timezone.utc)
        payload_content = {"info": "test percept from bus"}
        percept_payload = PerceptDataPayload(
            modality="test_modality",
            content=payload_content,
            source_timestamp=source_ts
        )
        test_message = GenericMessage(
            source_module_id="TestPerceptionModule",
            message_type="PerceptData",
            payload=percept_payload
        )

        self.bus.publish(test_message) # Publish to the bus WM is subscribed to

        self.assertEqual(len(self.wm_with_bus.received_percepts), 1)
        received_msg = self.wm_with_bus.received_percepts[0]

        self.assertIsInstance(received_msg, GenericMessage)
        self.assertEqual(received_msg.message_id, test_message.message_id)
        self.assertEqual(received_msg.message_type, "PerceptData")
        self.assertIsInstance(received_msg.payload, PerceptDataPayload)
        self.assertEqual(received_msg.payload.content, payload_content)

    def test_no_subscription_if_bus_is_none(self):
        """Test that WM does not attempt to subscribe if no bus is provided."""
        # self.wm_no_bus was initialized with message_bus=None
        # Publish a message on a new bus; wm_no_bus should not receive it.
        local_bus = MessageBus() # A bus wm_no_bus knows nothing about

        source_ts = datetime.datetime.now(datetime.timezone.utc)
        percept_payload = PerceptDataPayload(
            modality="text",
            content="message for no-bus WM",
            source_timestamp=source_ts
        )
        test_message = GenericMessage(
            source_module_id="TestPerceptionModule",
            message_type="PerceptData",
            payload=percept_payload
        )
        local_bus.publish(test_message)

        self.assertEqual(len(self.wm_no_bus.received_percepts), 0) # Should remain empty

    def test_handle_malformed_message_gracefully(self):
        """Test that the callback handles messages not matching expected structure."""
        malformed_message = GenericMessage(
            source_module_id="TestPerceptionModule",
            message_type="PerceptData", # Correct type, but payload might be wrong
            payload="This is just a string, not PerceptDataPayload"
        )
        self.bus.publish(malformed_message)
        self.assertEqual(len(self.wm_with_bus.received_percepts), 1) # Message is still "received"
        # Check the content of the received message in this error case
        error_entry = self.wm_with_bus.received_percepts[0]
        self.assertIsInstance(error_entry, dict) # The handler appends a dict on error
        self.assertEqual(error_entry.get("error"), "AttributeError processing message")
        self.assertTrue("This is just a string" in error_entry.get("raw_message", ""))


    def test_initial_status_no_bus_instance(self): # Renamed for clarity
    def test_initial_status_no_bus_instance(self): # Renamed for clarity
        status = self.wm_no_bus.get_status() # Using wm_no_bus
        self.assertEqual(status['current_size'], 0)
        self.assertEqual(status['capacity'], 3)
        self.assertIsNone(status['current_focus_id'])
        self.assertEqual(status['module_type'], 'ConcreteWorkingMemoryModule')

    def test_add_item_and_get_contents(self):
        id1 = self.wm_no_bus.add_item_to_workspace({'data': 'item1'}, salience=0.5) # Using wm_no_bus
        self.assertRegex(id1, r"wm_item_\d+")
        contents = self.wm_no_bus.get_workspace_contents() # Using wm_no_bus
        self.assertEqual(len(contents), 1)
        self.assertEqual(contents[0]['id'], id1)
        self.assertEqual(contents[0]['content'], {'data': 'item1'})
        self.assertEqual(self.wm_no_bus.get_status()['current_size'], 1) # Using wm_no_bus

    def test_store_method_as_add_item(self):
        id_store = self.wm_no_bus.store({'data': 'item_via_store'}, context={'salience': 0.6}) # Using wm_no_bus
        contents = self.wm_no_bus.get_workspace_contents() # Using wm_no_bus
        self.assertEqual(len(contents), 1)
        self.assertEqual(contents[0]['id'], id_store)
        self.assertEqual(contents[0]['content'], {'data': 'item_via_store'})
        self.assertEqual(contents[0]['salience'], 0.6)


    def test_capacity_management_add_item(self):
        id1 = self.wm_no_bus.add_item_to_workspace("item1", 0.1) # Using wm_no_bus
        id2 = self.wm_no_bus.add_item_to_workspace("item2", 0.2) # Using wm_no_bus
        id3 = self.wm_no_bus.add_item_to_workspace("item3", 0.3) # Using wm_no_bus
        self.assertEqual(self.wm_no_bus.get_status()['current_size'], 3) # Using wm_no_bus

        # This item has higher salience than item1, item1 should be removed
        id4 = self.wm_no_bus.add_item_to_workspace("item4", 0.4) # Using wm_no_bus
        self.assertNotEqual(id4, "error_workspace_full")

        contents = self.wm_no_bus.get_workspace_contents() # Using wm_no_bus
        self.assertEqual(len(contents), 3)
        item_ids = [item['id'] for item in contents]
        self.assertNotIn(id1, item_ids)
        self.assertIn(id4, item_ids)

        # This item has lower salience than all in workspace, should not be added
        id5_fail = self.wm_no_bus.add_item_to_workspace("item5_fail", 0.05) # Using wm_no_bus
        self.assertEqual(id5_fail, "error_workspace_full") # Assuming this is the error code for full
        self.assertEqual(len(self.wm_no_bus.get_workspace_contents()), 3) # Using wm_no_bus
        self.assertNotIn(id5_fail, [item['id'] for item in self.wm_no_bus.get_workspace_contents()]) # Using wm_no_bus


    def test_remove_item_from_workspace(self):
        id1 = self.wm_no_bus.add_item_to_workspace("item1") # Using wm_no_bus
        self.wm_no_bus.add_item_to_workspace("item2") # Using wm_no_bus
        self.assertTrue(self.wm_no_bus.remove_item_from_workspace(id1)) # Using wm_no_bus
        self.assertEqual(self.wm_no_bus.get_status()['current_size'], 1) # Using wm_no_bus
        self.assertFalse(self.wm_no_bus.remove_item_from_workspace(id1)) # Already removed Using wm_no_bus
        self.assertFalse(self.wm_no_bus.remove_item_from_workspace("non_existent_id")) # Using wm_no_bus


    def test_delete_memory_as_remove_item(self):
        id1 = self.wm_no_bus.add_item_to_workspace("item1_del") # Using wm_no_bus
        self.assertTrue(self.wm_no_bus.delete_memory(id1)) # Using wm_no_bus
        self.assertEqual(self.wm_no_bus.get_status()['current_size'], 0) # Using wm_no_bus


    def test_set_and_get_active_focus(self):
        id1 = self.wm_no_bus.add_item_to_workspace("item_focus_1", 0.5) # Using wm_no_bus
        id2 = self.wm_no_bus.add_item_to_workspace("item_focus_2", 0.6) # Using wm_no_bus

        self.assertTrue(self.wm_no_bus.set_active_focus(id1)) # Using wm_no_bus
        focused_item = self.wm_no_bus.get_active_focus() # Using wm_no_bus
        self.assertIsNotNone(focused_item)
        self.assertEqual(focused_item['id'], id1)
        self.assertGreater(focused_item['salience'], 0.5) # Salience boosted

        self.assertFalse(self.wm_no_bus.set_active_focus("non_existent")) # Using wm_no_bus
        self.assertIsNotNone(self.wm_no_bus.get_active_focus()) # Focus should remain on id1 Using wm_no_bus

    def test_remove_focused_item_clears_focus(self):
        id1 = self.wm_no_bus.add_item_to_workspace("item_focus_rem", 0.7) # Using wm_no_bus
        self.wm_no_bus.set_active_focus(id1) # Using wm_no_bus
        self.assertIsNotNone(self.wm_no_bus.get_active_focus()) # Using wm_no_bus
        self.wm_no_bus.remove_item_from_workspace(id1) # Using wm_no_bus
        self.assertIsNone(self.wm_no_bus.get_active_focus()) # Using wm_no_bus


    def test_retrieve_by_id(self):
        id1 = self.wm_no_bus.add_item_to_workspace({'name': "Pia"}, 0.5) # Using wm_no_bus
        retrieved = self.wm_no_bus.retrieve({'id': id1}) # Using wm_no_bus
        self.assertEqual(len(retrieved), 1)
        self.assertEqual(retrieved[0]['id'], id1)

    def test_retrieve_by_content_query(self):
        self.wm_no_bus.add_item_to_workspace({'type': 'fruit', 'name': 'apple'}, 0.5) # Using wm_no_bus
        self.wm_no_bus.add_item_to_workspace({'type': 'fruit', 'name': 'banana'}, 0.6) # Using wm_no_bus
        self.wm_no_bus.add_item_to_workspace({'type': 'veg', 'name': 'carrot'}, 0.7) # Using wm_no_bus

        retrieved_fruits = self.wm_no_bus.retrieve({'content_query': {'key': 'type', 'value': 'fruit'}}) # Using wm_no_bus
        self.assertEqual(len(retrieved_fruits), 2)

        retrieved_apple = self.wm_no_bus.retrieve({'content_query': {'key': 'name', 'value': 'apple'}}) # Using wm_no_bus
        self.assertEqual(len(retrieved_apple), 1)
        self.assertEqual(retrieved_apple[0]['content']['name'], 'apple')

    def test_retrieve_empty_query_returns_all(self):
        id1 = self.wm_no_bus.add_item_to_workspace("item_a") # Using wm_no_bus
        id2 = self.wm_no_bus.add_item_to_workspace("item_b") # Using wm_no_bus
        all_items = self.wm_no_bus.retrieve({}) # Using wm_no_bus
        self.assertEqual(len(all_items), 2)
        item_ids = [item['id'] for item in all_items]
        self.assertIn(id1, item_ids)
        self.assertIn(id2, item_ids)


    def test_manage_capacity_method(self):
        # This test used self.wm which is now self.wm_no_bus. Adapting.
        # Reset for clear test of manage_capacity directly
        wm_for_cap_test = ConcreteWorkingMemoryModule(capacity=2) # Local instance for this test
        id_a = wm_for_cap_test.add_item_to_workspace("A", 0.5)
        id_b = wm_for_cap_test.add_item_to_workspace("B", 0.6)
        id_c_fail = wm_for_cap_test.add_item_to_workspace("C_fail", 0.1) # Fails as 0.1 < 0.5
        self.assertEqual(id_c_fail, "error_workspace_full")

        # Manually add a third item to exceed capacity for direct test
        wm_for_cap_test._workspace.append({'id': 'temp_c', 'content': 'C_direct', 'salience': 0.1})
        self.assertEqual(len(wm_for_cap_test._workspace), 3)

        wm_for_cap_test.manage_capacity() # Should remove 'temp_c' (salience 0.1)

        contents = wm_for_cap_test.get_workspace_contents()
        self.assertEqual(len(contents), 2)
        item_ids_cap_test = [item['id'] for item in contents]
        self.assertIn(id_a, item_ids_cap_test)
        self.assertIn(id_b, item_ids_cap_test)
        self.assertNotIn('temp_c', item_ids_cap_test)


    def test_handle_forgetting_decay_salience(self):
        id1 = self.wm_no_bus.add_item_to_workspace("item_s1", salience=1.0) # Using wm_no_bus
        id2 = self.wm_no_bus.add_item_to_workspace("item_s2", salience=0.5) # Using wm_no_bus

        self.wm_no_bus.handle_forgetting(strategy='decay_salience') # Using wm_no_bus

        contents = self.wm_no_bus.get_workspace_contents() # Using wm_no_bus
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

    # --- Tests for Architectural Maturation Hooks (Capacity Parameters) ---

    def test_capacity_params_initialization(self):
        """Test that capacity_params is initialized correctly."""
        self.assertTrue(hasattr(self.wm_no_bus, 'capacity_params')) # Using wm_no_bus
        self.assertIsInstance(self.wm_no_bus.capacity_params, dict)
        # setUp uses capacity=3 for self.wm instances
        self.assertEqual(self.wm_no_bus.capacity_params.get("max_items"), 3)
        self.assertEqual(self.wm_no_bus.capacity_params.get("max_item_complexity"), 5) # Default value

        # Test with default capacity in constructor
        wm_default_cap = ConcreteWorkingMemoryModule() # Default capacity is 7
        self.assertEqual(wm_default_cap.capacity_params.get("max_items"), ConcreteWorkingMemoryModule.DEFAULT_CAPACITY)
        self.assertEqual(wm_default_cap.capacity_params.get("max_item_complexity"), 5)


    def test_set_capacity_parameters(self):
        """Test setting capacity parameters."""
        # Using wm_no_bus for this test as it's about the direct method call
        # Test setting valid parameters
        params1 = {"max_items": 20, "max_item_complexity": 10}
        self.wm_no_bus.set_capacity_parameters(params1)
        self.assertEqual(self.wm_no_bus.capacity_params["max_items"], 20)
        self.assertEqual(self.wm_no_bus.capacity_params["max_item_complexity"], 10)

        # Test setting only one parameter
        params2 = {"max_items": 15}
        self.wm_no_bus.set_capacity_parameters(params2)
        self.assertEqual(self.wm_no_bus.capacity_params["max_items"], 15)
        self.assertEqual(self.wm_no_bus.capacity_params["max_item_complexity"], 10) # Should retain previous value

        params3 = {"max_item_complexity": 7}
        self.wm_no_bus.set_capacity_parameters(params3)
        self.assertEqual(self.wm_no_bus.capacity_params["max_items"], 15) # Should retain previous value
        self.assertEqual(self.wm_no_bus.capacity_params["max_item_complexity"], 7)

        # Test with invalid values (should be ignored, values not updated)
        initial_max_items = self.wm_no_bus.capacity_params["max_items"]
        initial_complexity = self.wm_no_bus.capacity_params["max_item_complexity"]

        self.wm_no_bus.set_capacity_parameters({"max_items": -5}) # Negative value
        self.assertEqual(self.wm_no_bus.capacity_params["max_items"], initial_max_items)

        self.wm_no_bus.set_capacity_parameters({"max_item_complexity": "not_an_int"}) # Non-integer
        self.assertEqual(self.wm_no_bus.capacity_params["max_item_complexity"], initial_complexity)

        self.wm_no_bus.set_capacity_parameters({"max_items": 5.5}) # Float, should be ignored
        self.assertEqual(self.wm_no_bus.capacity_params["max_items"], initial_max_items)


        # Test with unknown parameter keys (should be ignored)
        self.wm_no_bus.set_capacity_parameters({"unknown_param": 100, "max_items": 25})
        self.assertNotIn("unknown_param", self.wm_no_bus.capacity_params)
        self.assertEqual(self.wm_no_bus.capacity_params["max_items"], 25) # Known param should update

        # Test with non-dict input
        self.wm_no_bus.set_capacity_parameters("not_a_dict") # Should print error, params not change
        self.assertEqual(self.wm_no_bus.capacity_params["max_items"], 25) # Check it didn't change


    def test_get_capacity_parameters(self):
        """Test getting capacity parameters and that it returns a copy."""
        # Using wm_no_bus
        current_params = self.wm_no_bus.get_capacity_parameters()
        self.assertEqual(current_params, self.wm_no_bus.capacity_params)

        # Modify the returned dictionary
        current_params["max_items"] = 1000

        # Ensure the internal dictionary is not affected
        self.assertNotEqual(self.wm_no_bus.capacity_params["max_items"], 1000)
        # Initial value from setUp for wm_no_bus (capacity=3)
        self.assertEqual(self.wm_no_bus.capacity_params["max_items"], 3)


if __name__ == '__main__':
    unittest.main()
