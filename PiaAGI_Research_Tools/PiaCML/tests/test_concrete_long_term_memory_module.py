import unittest
import os
import sys
import uuid # For generating unique IDs in tests if needed

# Adjust path to import from the parent directory (PiaCML)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from concrete_long_term_memory_module import ConcreteLongTermMemoryModule
    from concrete_base_memory_module import ConcreteBaseMemoryModule # To inspect backend if necessary
except ImportError:
    if 'ConcreteLongTermMemoryModule' not in globals():
        from PiaAGI_Hub.PiaCML.concrete_long_term_memory_module import ConcreteLongTermMemoryModule
    if 'ConcreteBaseMemoryModule' not in globals():
        from PiaAGI_Hub.PiaCML.concrete_base_memory_module import ConcreteBaseMemoryModule


class TestConcreteLongTermMemoryModule(unittest.TestCase):

    def setUp(self):
        self.ltm = ConcreteLongTermMemoryModule()
        # Access the internal backend for some direct checks if needed, or to pre-seed
        self.backend_storage = self.ltm._storage_backend

        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_initial_status(self):
        status = self.ltm.get_status()
        self.assertEqual(status['module_type'], 'ConcreteLongTermMemoryModule')
        self.assertEqual(status['total_ltm_items_tracked'], 0)
        self.assertEqual(status['subcomponent_overview']['episodic']['items'], 0)
        self.assertEqual(status['subcomponent_overview']['semantic']['queries'], 0)

    def test_store_and_retrieve_episodic_event(self):
        event_data = {'description': "User logged in", 'user_id': "user123"}
        event_id = self.ltm.store_episodic_event(event_data, context={'source': 'auth_system'})

        self.assertIsNotNone(event_id)
        status = self.ltm.get_status()
        self.assertEqual(status['subcomponent_overview']['episodic']['items'], 1)

        # Retrieve by ID (generic retrieve, but context was set by store_episodic_event)
        retrieved_by_id = self.ltm.retrieve({'id': event_id})
        self.assertEqual(len(retrieved_by_id), 1)
        self.assertEqual(retrieved_by_id[0]['info'], event_data)
        self.assertEqual(retrieved_by_id[0]['ctx']['ltm_type'], 'episodic')
        self.assertEqual(retrieved_by_id[0]['ctx']['source'], 'auth_system')

        # Retrieve specifically using the typed method
        # This relies on the backend ConcreteBaseMemoryModule.retrieve supporting criteria['match_context']
        retrieved_typed = self.ltm.retrieve_episodic_events(query={'description': "User logged in"})
        self.assertEqual(len(retrieved_typed), 1)
        self.assertEqual(retrieved_typed[0]['id'], event_id)

        status_after_retrieve = self.ltm.get_status()
        self.assertEqual(status_after_retrieve['subcomponent_overview']['episodic']['queries'], 1)

    def test_store_and_retrieve_semantic_knowledge(self):
        knowledge_data = {'concept': 'cat', 'property': 'is_mammal'}
        knowledge_id = self.ltm.store_semantic_knowledge(knowledge_data)

        self.assertIsNotNone(knowledge_id)
        self.assertEqual(self.ltm.get_status()['subcomponent_overview']['semantic']['items'], 1)

        retrieved_typed = self.ltm.retrieve_semantic_knowledge(query={'concept': 'cat'})
        self.assertEqual(len(retrieved_typed), 1)
        self.assertEqual(retrieved_typed[0]['id'], knowledge_id)
        self.assertEqual(retrieved_typed[0]['info'], knowledge_data)
        self.assertEqual(retrieved_typed[0]['ctx']['ltm_type'], 'semantic')
        self.assertEqual(self.ltm.get_status()['subcomponent_overview']['semantic']['queries'], 1)

    def test_store_and_retrieve_procedural_skill(self):
        skill_data = {'action': 'jump', 'height': '2_meters'}
        skill_id = self.ltm.store_procedural_skill(skill_data)

        self.assertIsNotNone(skill_id)
        self.assertEqual(self.ltm.get_status()['subcomponent_overview']['procedural']['items'], 1)

        retrieved_typed = self.ltm.retrieve_procedural_skill(query={'action': 'jump'})
        self.assertEqual(len(retrieved_typed), 1)
        self.assertEqual(retrieved_typed[0]['id'], skill_id)
        self.assertEqual(retrieved_typed[0]['info'], skill_data)
        self.assertEqual(retrieved_typed[0]['ctx']['ltm_type'], 'procedural')
        self.assertEqual(self.ltm.get_status()['subcomponent_overview']['procedural']['queries'], 1)

    def test_generic_store_retrieve_delete(self):
        # Test generic store
        generic_id = self.ltm.store({'data': "generic_ltm_stuff"}, {'custom_tag': 'test'})
        self.assertIsNotNone(generic_id)
        # Check backend directly to confirm context
        raw_item = self.backend_storage.retrieve({'id': generic_id})[0]
        self.assertEqual(raw_item['ctx']['ltm_type'], 'generic_ltm')
        self.assertEqual(raw_item['ctx']['custom_tag'], 'test')

        # Test generic retrieve (by id)
        retrieved_items = self.ltm.retrieve({'id': generic_id})
        self.assertEqual(len(retrieved_items), 1)
        self.assertEqual(retrieved_items[0]['info']['data'], "generic_ltm_stuff")

        # Test generic delete
        delete_success = self.ltm.delete_memory(generic_id)
        self.assertTrue(delete_success)
        self.assertEqual(len(self.ltm.retrieve({'id': generic_id})), 0)
        # Note: subcomponent counts are not affected by generic delete in this impl.

    def test_multiple_types_do_not_interfere_on_typed_retrieval(self):
        event_id = self.ltm.store_episodic_event({'event_name': "Party"})
        fact_id = self.ltm.store_semantic_knowledge({'fact_name': "EarthIsRound"})
        skill_id = self.ltm.store_procedural_skill({'skill_action': "Sing"})

        episodic_results = self.ltm.retrieve_episodic_events(query={'event_name': "Party"})
        self.assertEqual(len(episodic_results), 1)
        self.assertEqual(episodic_results[0]['id'], event_id)

        semantic_results = self.ltm.retrieve_semantic_knowledge(query={'fact_name': "EarthIsRound"})
        self.assertEqual(len(semantic_results), 1)
        self.assertEqual(semantic_results[0]['id'], fact_id)

        procedural_results = self.ltm.retrieve_procedural_skill(query={'skill_action': "Sing"})
        self.assertEqual(len(procedural_results), 1)
        self.assertEqual(procedural_results[0]['id'], skill_id)

        self.assertEqual(self.ltm.get_status()['total_ltm_items_tracked'], 3)


    def test_manage_capacity_and_forgetting_placeholders(self):
        # These just test that the methods run without error as they are placeholders or simple delegates
        try:
            self.ltm.manage_capacity()
            self.ltm.handle_forgetting(strategy="test_strat")
            self.ltm.manage_ltm_subcomponents() # Also a placeholder
        except Exception as e:
            self.fail(f"Management or forgetting method raised an exception: {e}")

    def test_retrieve_empty_results_for_type(self):
        self.ltm.store_semantic_knowledge({'fact_name': "SkyIsBlue"})
        episodic_results = self.ltm.retrieve_episodic_events(query={'fact_name': "SkyIsBlue"}) # Wrong type
        self.assertEqual(len(episodic_results), 0)
        self.assertEqual(self.ltm.get_status()['subcomponent_overview']['episodic']['queries'], 1)


if __name__ == '__main__':
    unittest.main()
