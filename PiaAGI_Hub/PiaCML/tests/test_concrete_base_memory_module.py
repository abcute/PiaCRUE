import unittest
import os
import sys

# Adjust path to import from the parent directory (PiaCML)
# This assumes the test script is run from PiaAGI_Hub/PiaCML/tests/ or a similar context
# where PiaCML is one level up.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from concrete_base_memory_module import ConcreteBaseMemoryModule
except ImportError:
    print("Failed to import ConcreteBaseMemoryModule. Ensure it's in the PiaCML directory and sys.path is correct.")
    # As a fallback, try a more direct import if the above structure isn't perfect during execution
    # This might happen if tests are run from the root of the project with 'python -m unittest discover ...'
    # and PiaCML is in the python path.
    if 'ConcreteBaseMemoryModule' not in globals():
        from PiaAGI_Hub.PiaCML.concrete_base_memory_module import ConcreteBaseMemoryModule


class TestConcreteBaseMemoryModule(unittest.TestCase):

    def setUp(self):
        """Set up a new ConcreteBaseMemoryModule instance for each test."""
        self.memory = ConcreteBaseMemoryModule()
        # Suppress print statements from the module during tests
        # If needed, can be more sophisticated, e.g., patching sys.stdout
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')


    def tearDown(self):
        """Clean up after tests."""
        sys.stdout.close()
        sys.stdout = self._original_stdout


    def test_store_and_retrieve_by_id(self):
        """Test storing an item and retrieving it by its ID."""
        info = {'type': 'test_fact', 'data': 'Test data 1'}
        context = {'source': 'test_suite'}
        memory_id = self.memory.store(info, context)
        self.assertIsInstance(memory_id, str, "Store should return a string ID.")

        retrieved_items = self.memory.retrieve({'id': memory_id})
        self.assertEqual(len(retrieved_items), 1, "Should retrieve exactly one item by ID.")
        retrieved_item = retrieved_items[0]
        self.assertEqual(retrieved_item['id'], memory_id)
        self.assertEqual(retrieved_item['info'], info)
        self.assertEqual(retrieved_item['ctx'], context)

    def test_retrieve_by_concept(self):
        """Test retrieving items by a 'concept' in their information."""
        info1 = {'type': 'concept_test', 'concept': 'TopicA', 'value': 'Value1'}
        info2 = {'type': 'concept_test', 'concept': 'TopicB', 'value': 'Value2'}
        info3 = {'type': 'concept_test', 'concept': 'TopicA', 'value': 'Value3'}
        self.memory.store(info1)
        self.memory.store(info2)
        self.memory.store(info3)

        retrieved_topic_a = self.memory.retrieve({'concept': 'TopicA'})
        self.assertEqual(len(retrieved_topic_a), 2, "Should retrieve two items for TopicA.")
        # Check if the retrieved items actually contain TopicA
        for item in retrieved_topic_a:
            self.assertEqual(item['info']['concept'], 'TopicA')

        retrieved_topic_b = self.memory.retrieve({'concept': 'TopicB'})
        self.assertEqual(len(retrieved_topic_b), 1, "Should retrieve one item for TopicB.")
        self.assertEqual(retrieved_topic_b[0]['info']['concept'], 'TopicB')

    def test_retrieve_non_existent_id(self):
        """Test retrieving with a non-existent ID."""
        retrieved_items = self.memory.retrieve({'id': 'non_existent_id_123'})
        self.assertEqual(len(retrieved_items), 0, "Should return an empty list for a non-existent ID.")

    def test_retrieve_non_existent_concept(self):
        """Test retrieving with a non-existent concept."""
        self.memory.store({'type': 'fact', 'concept': 'ExistingConcept', 'data': 'data'})
        retrieved_items = self.memory.retrieve({'concept': 'NonExistentConcept'})
        self.assertEqual(len(retrieved_items), 0, "Should return an empty list for a non-existent concept.")

    def test_retrieve_empty_query_returns_all(self):
        """Test that an empty query retrieves all stored items."""
        info1 = {'data': 'item1'}
        info2 = {'data': 'item2'}
        self.memory.store(info1)
        self.memory.store(info2)

        retrieved_items = self.memory.retrieve({})
        self.assertEqual(len(retrieved_items), 2, "Empty query should retrieve all items.")

    def test_retrieve_unhandled_query_returns_empty(self):
        """Test that a query with unhandled fields returns an empty list."""
        self.memory.store({'data': 'item1'})
        retrieved_items = self.memory.retrieve({'unhandled_field': 'some_value'})
        self.assertEqual(len(retrieved_items), 0, "Query with unhandled fields should return empty list.")


    def test_delete_memory(self):
        """Test deleting a memory item."""
        info = {'data': 'item_to_delete'}
        memory_id = self.memory.store(info)

        # Ensure it's there
        self.assertEqual(len(self.memory.retrieve({'id': memory_id})), 1)

        delete_success = self.memory.delete_memory(memory_id)
        self.assertTrue(delete_success, "delete_memory should return True on successful deletion.")

        # Ensure it's gone
        self.assertEqual(len(self.memory.retrieve({'id': memory_id})), 0, "Item should be gone after deletion.")
        self.assertNotIn(memory_id, self.memory._storage, "ID should not be in internal storage after deletion.")


    def test_delete_non_existent_memory(self):
        """Test attempting to delete a non-existent memory item."""
        delete_success = self.memory.delete_memory('non_existent_id_456')
        self.assertFalse(delete_success, "delete_memory should return False for a non-existent ID.")

    def test_get_status(self):
        """Test the get_status method."""
        status_initial = self.memory.get_status()
        self.assertEqual(status_initial['total_items'], 0)
        self.assertEqual(status_initial['module_type'], 'ConcreteBaseMemoryModule')
        self.assertEqual(status_initial['storage_engine'], 'in-memory Python dictionary')

        self.memory.store({'data': 'itemA'})
        self.memory.store({'data': 'itemB'})

        status_after_stores = self.memory.get_status()
        self.assertEqual(status_after_stores['total_items'], 2)

        # Assume one of the stored items has a known ID for deletion test.
        # This is a bit fragile if store doesn't return predictable IDs or if we don't track them.
        # For this test, let's retrieve all and delete the first one found.
        all_items = self.memory.retrieve({})
        if all_items:
            item_id_to_delete = all_items[0]['id']
            self.memory.delete_memory(item_id_to_delete)
            status_after_delete = self.memory.get_status()
            self.assertEqual(status_after_delete['total_items'], 1)


    def test_placeholder_methods_run_without_error(self):
        """Test that placeholder methods can be called without raising errors."""
        memory_id = self.memory.store({'data': 'placeholder_test'})
        try:
            self.memory.manage_capacity()
            self.memory.handle_forgetting()
            self.memory.handle_forgetting(strategy='specific_strategy')
            self.memory.update_memory_decay(memory_id, 0.9)
            self.memory.update_memory_decay("non_existent_id", 0.9) # Test with non-existent ID
            self.memory.find_similar_memories([0.1, 0.2], 3)
        except Exception as e:
            self.fail(f"Placeholder method raised an unexpected exception: {e}")

if __name__ == '__main__':
    unittest.main()
