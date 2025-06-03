import unittest
import time
import os
import sys

# Adjust path to import from the parent directory (PiaCML)
# This goes two levels up from tests/ to PiaAGI_Research_Tools/
# Then one level up to the root of the project to allow PiaAGI_Research_Tools.PiaCML import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    from PiaAGI_Research_Tools.PiaCML.concrete_long_term_memory_module import ConcreteLongTermMemoryModule
except ModuleNotFoundError:
    # Fallback if the above doesn't work (e.g. when CWD is already PiaAGI_Research_Tools)
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from concrete_long_term_memory_module import ConcreteLongTermMemoryModule


class TestConcreteLongTermMemoryModule(unittest.TestCase):

    def setUp(self):
        self.ltm = ConcreteLongTermMemoryModule()
        self._original_stdout = sys.stdout
        # Suppress prints from the module during tests for cleaner output
        # sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        """Restore stdout after each test."""
        # sys.stdout.close()
        sys.stdout = self._original_stdout

    # --- Episodic Memory Tests ---
    def test_add_episode_basic(self):
        """Test basic episode addition."""
        initial_count = len(self.ltm.episodic_memory)
        ep_id = self.ltm.add_episode("Test event 1")
        self.assertTrue(ep_id.startswith("ep_"))
        self.assertEqual(len(self.ltm.episodic_memory), initial_count + 1)
        self.assertEqual(self.ltm.episodic_memory[-1]["event_description"], "Test event 1")
        self.assertAlmostEqual(self.ltm.episodic_memory[-1]["timestamp"], time.time(), delta=1) # Check if timestamp is recent
        self.assertEqual(self.ltm.episodic_memory[-1]["episode_id"], ep_id)

    def test_add_episode_with_details(self):
        """Test episode addition with all parameters."""
        ts = time.time() - 1000
        assoc_data = {"location": "lab", "mood": "curious"}
        causal_links = ["ep_0"] # Assuming ep_0 might exist or this is just data

        ep_id = self.ltm.add_episode("Detailed event", timestamp=ts, associated_data=assoc_data, causal_links=causal_links)
        added_episode = self.ltm.episodic_memory[-1]

        self.assertEqual(added_episode["timestamp"], ts)
        self.assertEqual(added_episode["associated_data"], assoc_data)
        self.assertEqual(added_episode["causal_links"], causal_links)
        self.assertEqual(self.ltm.next_episode_id, int(ep_id.split('_')[1]) + 1)

    def test_get_episode(self):
        """Test retrieving an episode by ID."""
        ep_id1 = self.ltm.add_episode("Event to get")
        ep_id2 = self.ltm.add_episode("Another event")

        retrieved_ep1 = self.ltm.get_episode(ep_id1)
        self.assertIsNotNone(retrieved_ep1)
        self.assertEqual(retrieved_ep1["episode_id"], ep_id1)
        self.assertEqual(retrieved_ep1["event_description"], "Event to get")

        retrieved_ep_non_existent = self.ltm.get_episode("ep_999")
        self.assertIsNone(retrieved_ep_non_existent)

        status = self.ltm.get_status()
        self.assertGreaterEqual(status['query_counts_overview']['episodic_list']['queries'], 2)


    def test_find_episodes_by_keyword(self):
        """Test finding episodes by keyword."""
        self.ltm.add_episode("A sunny day at the park.", associated_data={"activity": "picnic"})
        self.ltm.add_episode("Heavy rain caused flooding in the city park.", associated_data={"damage": "significant"})
        self.ltm.add_episode("The new park design is amazing.")

        # Search in description (default)
        results_park = self.ltm.find_episodes_by_keyword("park")
        self.assertEqual(len(results_park), 2) # "sunny day at the park", "city park"

        results_rain = self.ltm.find_episodes_by_keyword("rain")
        self.assertEqual(len(results_rain), 1)
        self.assertEqual(results_rain[0]["event_description"], "Heavy rain caused flooding in the city park.")

        results_non_existent = self.ltm.find_episodes_by_keyword("moonlanding")
        self.assertEqual(len(results_non_existent), 0)

        # Search in associated data
        self.ltm.add_episode("Routine check.", associated_data={"status": "all clear", "target": "park facilities"})
        results_assoc_park = self.ltm.find_episodes_by_keyword("park", search_in_description=False, search_in_associated_data=True)
        self.assertEqual(len(results_assoc_park), 1)
        self.assertEqual(results_assoc_park[0]["associated_data"]["target"], "park facilities")

        results_assoc_and_desc_park = self.ltm.find_episodes_by_keyword("park", search_in_description=True, search_in_associated_data=True)
        self.assertEqual(len(results_assoc_and_desc_park), 3)


    # --- Semantic Memory Tests ---
    def test_add_semantic_node(self):
        """Test adding semantic nodes."""
        self.assertTrue(self.ltm.add_semantic_node("node1", "Concept Alpha", "concept"))
        self.assertIn("node1", self.ltm.semantic_memory_graph)
        self.assertEqual(self.ltm.semantic_memory_graph["node1"]["label"], "Concept Alpha")

        # Test adding duplicate node
        self.assertFalse(self.ltm.add_semantic_node("node1", "Duplicate Concept", "concept"))
        self.assertEqual(self.ltm.semantic_memory_graph["node1"]["label"], "Concept Alpha") # Should not overwrite

    def test_add_semantic_relationship(self):
        """Test adding relationships between semantic nodes."""
        self.ltm.add_semantic_node("src_node", "Source Node", "event")
        self.ltm.add_semantic_node("tgt_node", "Target Node", "object")

        self.assertTrue(self.ltm.add_semantic_relationship("src_node", "tgt_node", "affects", {"strength": 0.8}))
        src_node_data = self.ltm.semantic_memory_graph["src_node"]
        self.assertEqual(len(src_node_data["relationships"]), 1)
        rel = src_node_data["relationships"][0]
        self.assertEqual(rel["type"], "affects")
        self.assertEqual(rel["target"], "tgt_node")
        self.assertEqual(rel["properties"]["strength"], 0.8)

        # Test adding relationship with non-existent node
        self.assertFalse(self.ltm.add_semantic_relationship("src_node", "non_existent_node", "related_to"))
        self.assertFalse(self.ltm.add_semantic_relationship("non_existent_node", "tgt_node", "related_to"))
        self.assertEqual(len(src_node_data["relationships"]), 1) # Should not have changed

    def test_get_semantic_node(self):
        """Test retrieving a semantic node."""
        self.ltm.add_semantic_node("node_get", "Node To Get", "place", {"feature": "is_capital"})

        node_data = self.ltm.get_semantic_node("node_get")
        self.assertIsNotNone(node_data)
        self.assertEqual(node_data["label"], "Node To Get")
        self.assertEqual(node_data["properties"]["feature"], "is_capital")

        non_existent_node = self.ltm.get_semantic_node("node_does_not_exist")
        self.assertIsNone(non_existent_node)

        status = self.ltm.get_status()
        self.assertGreaterEqual(status['query_counts_overview']['semantic_graph']['queries'], 2)


    def test_find_related_nodes(self):
        """Test finding related nodes."""
        self.ltm.add_semantic_node("center", "Center Node", "topic")
        self.ltm.add_semantic_node("related1", "Related 1", "subtopic")
        self.ltm.add_semantic_node("related2", "Related 2", "subtopic")
        self.ltm.add_semantic_node("unrelated", "Unrelated Node", "other")
        self.ltm.add_semantic_node("related_specific", "Related Specific", "property")

        self.ltm.add_semantic_relationship("center", "related1", "has_subtopic")
        self.ltm.add_semantic_relationship("center", "related2", "has_subtopic")
        self.ltm.add_semantic_relationship("center", "related_specific", "has_property")

        # Find all related nodes
        all_related = self.ltm.find_related_nodes("center")
        self.assertCountEqual(all_related, ["related1", "related2", "related_specific"])

        # Find by specific relationship type
        subtopics = self.ltm.find_related_nodes("center", "has_subtopic")
        self.assertCountEqual(subtopics, ["related1", "related2"])

        properties = self.ltm.find_related_nodes("center", "has_property")
        self.assertCountEqual(properties, ["related_specific"])

        non_existent_rel_type = self.ltm.find_related_nodes("center", "does_not_exist_type")
        self.assertEqual(len(non_existent_rel_type), 0)

        # Test on node with no relationships or non-existent node
        self.assertEqual(len(self.ltm.find_related_nodes("unrelated")), 0)
        self.assertEqual(len(self.ltm.find_related_nodes("non_existent_node_for_rels")), 0)

    def test_get_semantic_relationships(self):
        """Test retrieving full relationship dictionaries."""
        self.ltm.add_semantic_node("s1", "S1", "item")
        self.ltm.add_semantic_node("t1", "T1", "item")
        self.ltm.add_semantic_node("t2", "T2", "item")

        rel1_props = {"weight": 10}
        rel2_props = {"notes": "important"}
        self.ltm.add_semantic_relationship("s1", "t1", "connected_to", rel1_props)
        self.ltm.add_semantic_relationship("s1", "t2", "connected_to", rel2_props)
        self.ltm.add_semantic_relationship("s1", "t1", "depends_on") # Different type

        # Get all relationships for s1
        all_rels_s1 = self.ltm.get_semantic_relationships("s1")
        self.assertEqual(len(all_rels_s1), 3)

        # Get specific type
        connected_rels = self.ltm.get_semantic_relationships("s1", "connected_to")
        self.assertEqual(len(connected_rels), 2)
        # Check if full relationship dictionaries are returned
        found_t1 = any(r["target"] == "t1" and r["properties"] == rel1_props for r in connected_rels)
        found_t2 = any(r["target"] == "t2" and r["properties"] == rel2_props for r in connected_rels)
        self.assertTrue(found_t1 and found_t2)

        depends_rels = self.ltm.get_semantic_relationships("s1", "depends_on")
        self.assertEqual(len(depends_rels), 1)
        self.assertEqual(depends_rels[0]["target"], "t1")
        self.assertEqual(depends_rels[0]["properties"], {}) # Default empty properties

    # Test original high-level methods to ensure they use new implementations
    def test_store_episodic_experience_uses_new_method(self):
        """Ensure store_episodic_experience uses the new add_episode logic."""
        event_data = {'event_description': "High-level store test", 'timestamp': time.time(), 'user': 'tester'}
        ep_id = self.ltm.store_episodic_experience(event_data)
        self.assertTrue(ep_id.startswith("ep_"))
        retrieved_episode = self.ltm.get_episode(ep_id)
        self.assertIsNotNone(retrieved_episode)
        self.assertEqual(retrieved_episode['event_description'], "High-level store test")
        self.assertEqual(retrieved_episode['associated_data']['user'], 'tester')

    def test_get_episodic_experience_uses_new_methods(self):
        """Ensure get_episodic_experience uses new find/get logic."""
        ep_id = self.ltm.add_episode("Keyword search via high-level call", associated_data={"key": "unique_ep_keyword"})

        # Test via keyword
        results_keyword = self.ltm.get_episodic_experience(query={"keyword": "unique_ep_keyword"}, criteria={"search_in_associated_data": True})
        self.assertEqual(len(results_keyword), 1)
        self.assertEqual(results_keyword[0]["episode_id"], ep_id)

        # Test via id
        results_id = self.ltm.get_episodic_experience(query={"episode_id": ep_id})
        self.assertEqual(len(results_id), 1)
        self.assertEqual(results_id[0]["episode_id"], ep_id)

    def test_store_semantic_knowledge_uses_new_method(self):
        """Ensure store_semantic_knowledge uses new add_semantic_node logic."""
        node_data = {"node_id": "sem_hl_1", "label": "High-level Semantic Store", "node_type": "test_concept"}
        returned_id = self.ltm.store_semantic_knowledge(node_data)
        self.assertEqual(returned_id, "sem_hl_1")
        retrieved_node = self.ltm.get_semantic_node("sem_hl_1")
        self.assertIsNotNone(retrieved_node)
        self.assertEqual(retrieved_node["label"], "High-level Semantic Store")

    def test_get_semantic_knowledge_uses_new_methods(self):
        """Ensure get_semantic_knowledge uses new graph search logic."""
        self.ltm.add_semantic_node("sem_src", "Source Sem HL", "source")
        self.ltm.add_semantic_node("sem_tgt", "Target Sem HL", "target")
        self.ltm.add_semantic_relationship("sem_src", "sem_tgt", "points_to")

        # Test get by node_id
        results_id = self.ltm.get_semantic_knowledge(query={"node_id": "sem_src"})
        self.assertEqual(len(results_id), 1)
        self.assertEqual(results_id[0]["label"], "Source Sem HL")

        # Test get related
        results_related = self.ltm.get_semantic_knowledge(query={"find_related_to_node_id": "sem_src"}, criteria={"relationship_type": "points_to"})
        self.assertEqual(len(results_related), 1)
        self.assertEqual(results_related[0]["label"], "Target Sem HL")

    def test_procedural_memory_still_functional(self):
        """Test that procedural memory (using backend) is still functional."""
        skill_data = {'skill_name_key': 'test_proc_skill', 'description': 'A skill for testing backend.'}
        skill_id = self.ltm.store_procedural_skill(skill_data)
        self.assertIsNotNone(skill_id) # Backend should return an ID

        retrieved_skill = self.ltm.get_procedural_skill('test_proc_skill')
        self.assertIsNotNone(retrieved_skill)
        self.assertEqual(retrieved_skill['description'], 'A skill for testing backend.')

        status = self.ltm.get_status()
        self.assertEqual(status['query_counts_overview']['procedural_backend']['items'], 1)
        self.assertEqual(status['query_counts_overview']['procedural_backend']['queries'], 1)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
