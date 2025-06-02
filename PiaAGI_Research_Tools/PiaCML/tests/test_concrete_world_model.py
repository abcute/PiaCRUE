import unittest
import time
from typing import Any, Dict, List 

from ..concrete_world_model import (
    ConcreteWorldModel,
    WorldEntity,
    SpatialData,
    TemporalEvent,
    SocialAgentModel,
    UncertaintyInfo,
    SelfStateSnapshot # PhysicsRule not directly tested here but imported for completeness
)

class TestConcreteWorldModel(unittest.TestCase):

    def setUp(self):
        """Initialize an instance of ConcreteWorldModel before each test."""
        self.world_model = ConcreteWorldModel(model_id="test_wm_01")

    def test_initialization(self):
        """Test that the world model is initialized correctly."""
        self.assertIsNotNone(self.world_model)
        self.assertEqual(self.world_model.model_id, "test_wm_01")
        self.assertEqual(len(self.world_model._entity_repository), 0)
        self.assertEqual(len(self.world_model._spatial_model), 0)
        self.assertEqual(len(self.world_model._temporal_model_events), 0)
        self.assertEqual(len(self.world_model._social_model), 0)
        self.assertIsInstance(self.world_model._self_state_snapshot, SelfStateSnapshot)
        initial_status = self.world_model.get_world_model_status()
        self.assertEqual(initial_status['entity_count'], 0)

    def test_update_and_get_entity(self):
        """Test adding, retrieving, and updating entities."""
        current_time = time.time()
        entity_data_perception = {
            "type": "entity_observation", "entity_id": "e1",
            "entity_type": "robot",
            "state": {"power": "on", "status": "idle"},
            "properties": {"color": "blue"},
            "affordances": ["move", "grasp"],
            "relationships": {"partOf": ["system_main"]},
            "location_id": "loc1"
        }
        
        # Add entity
        update_success = self.world_model.update_from_perception(entity_data_perception, timestamp=current_time)
        self.assertTrue(update_success)
        self.assertEqual(len(self.world_model._entity_repository), 1)

        # Retrieve entity
        retrieved_entity = self.world_model.get_entity_representation("e1")
        self.assertIsNotNone(retrieved_entity)
        self.assertIsInstance(retrieved_entity, WorldEntity)
        self.assertEqual(retrieved_entity.id, "e1")
        self.assertEqual(retrieved_entity.type, "robot")
        self.assertEqual(retrieved_entity.state["status"], "idle")
        self.assertEqual(retrieved_entity.properties["color"], "blue")
        self.assertIn("move", retrieved_entity.affordances)
        self.assertEqual(retrieved_entity.relationships["partOf"], ["system_main"])
        self.assertEqual(retrieved_entity.location_id, "loc1")
        self.assertEqual(retrieved_entity.last_observed_ts, current_time)

        # Update entity state
        state_update_data = {"state": {"status": "active", "task": "moving"}, "location_id": "loc2"}
        update_state_success = self.world_model.update_entity_state("e1", state_update_data, timestamp=current_time + 1)
        self.assertTrue(update_state_success)

        updated_entity = self.world_model.get_entity_representation("e1")
        self.assertIsNotNone(updated_entity)
        self.assertEqual(updated_entity.state["status"], "active")
        self.assertEqual(updated_entity.state["task"], "moving")
        self.assertEqual(updated_entity.location_id, "loc2")
        self.assertEqual(updated_entity.last_observed_ts, current_time + 1) # Assuming update_entity_state also updates this

    def test_query_world_state_entity(self):
        """Test querying for a specific entity using query_world_state."""
        entity_data = {
            "type": "entity_observation", "entity_id": "e_query", "entity_type": "sensor",
            "state": {"value": 10.5}, "properties": {}, "affordances": [], "relationships": {}
        }
        self.world_model.update_from_perception(entity_data)

        query_result = self.world_model.query_world_state({"type": "entity_state", "entity_id": "e_query"})
        self.assertTrue(query_result.get("success"))
        self.assertIsNotNone(query_result.get("data"))
        self.assertEqual(query_result["data"]["id"], "e_query")
        self.assertEqual(query_result["data"]["state"]["value"], 10.5)

        # Test query for non-existent entity
        query_non_existent = self.world_model.query_world_state({"type": "entity_state", "entity_id": "non_existent_e"})
        self.assertFalse(query_non_existent.get("success"))
        self.assertIn("not found", query_non_existent.get("error", "").lower())


    def test_query_world_state_all_entities(self):
        """Test querying for all entities."""
        entity_data1 = {"type": "entity_observation", "entity_id": "all_e1", "state": {"val": 1}}
        entity_data2 = {"type": "entity_observation", "entity_id": "all_e2", "state": {"val": 2}}
        self.world_model.update_from_perception(entity_data1)
        self.world_model.update_from_perception(entity_data2)

        query_result = self.world_model.query_world_state({"type": "all_entities"})
        self.assertTrue(query_result.get("success"))
        self.assertIsInstance(query_result.get("data"), list)
        self.assertEqual(len(query_result["data"]), 2)
        entity_ids_found = {e["id"] for e in query_result["data"]}
        self.assertIn("all_e1", entity_ids_found)
        self.assertIn("all_e2", entity_ids_found)

    def test_update_and_get_social_model(self):
        """Test adding and retrieving social agent models."""
        agent_id = "user007"
        social_info = {
            "type": "human_user", # This is now handled by update_social_model if agent is new
            "inferred_beliefs": {"mood": "happy"},
            "inferred_goals": [{"goal_name": "get_coffee", "priority": 0.9}],
            "relationship_to_self": "collaborator"
        }
        update_success = self.world_model.update_social_model(agent_id, social_info, timestamp=time.time())
        self.assertTrue(update_success)

        retrieved_model = self.world_model.get_social_model_for_agent(agent_id)
        self.assertIsNotNone(retrieved_model)
        self.assertIsInstance(retrieved_model, SocialAgentModel)
        self.assertEqual(retrieved_model.agent_id, agent_id)
        self.assertEqual(retrieved_model.type, "human_user")
        self.assertEqual(retrieved_model.inferred_beliefs["mood"], "happy")
        self.assertEqual(len(retrieved_model.inferred_goals), 1)
        self.assertEqual(retrieved_model.inferred_goals[0]["goal_name"], "get_coffee")

        # Update existing social model
        updated_social_info = {"inferred_beliefs": {"mood": "focused"}, "inferred_emotions": {"concentration": 0.8}}
        self.world_model.update_social_model(agent_id, updated_social_info, timestamp=time.time() + 1)
        updated_model = self.world_model.get_social_model_for_agent(agent_id)
        self.assertIsNotNone(updated_model)
        self.assertEqual(updated_model.inferred_beliefs["mood"], "focused") # Check if merged or updated
        self.assertEqual(updated_model.inferred_emotions["concentration"], 0.8)


    def test_manage_uncertainty(self):
        """Test setting and querying uncertainty information."""
        scope_key = "entity:e1:state.power"
        uncertainty_data_set = {
            "confidence": 0.75,
            "source": "inference_engine_v1",
            "details": "Based on indirect sensor readings."
        }
        
        # Set uncertainty
        set_result = self.world_model.manage_uncertainty(scope_key, uncertainty_data_set)
        self.assertIsNotNone(set_result) # manage_uncertainty now returns the UncertaintyInfo object
        self.assertIsInstance(set_result, UncertaintyInfo)
        self.assertEqual(set_result.confidence, 0.75)

        # Query uncertainty
        queried_uncertainty = self.world_model.manage_uncertainty(scope_key, query_uncertainty=True)
        self.assertIsNotNone(queried_uncertainty)
        self.assertIsInstance(queried_uncertainty, UncertaintyInfo)
        self.assertEqual(queried_uncertainty.scope_key, scope_key)
        self.assertEqual(queried_uncertainty.confidence, 0.75)
        self.assertEqual(queried_uncertainty.source, "inference_engine_v1")
        self.assertEqual(queried_uncertainty.details, "Based on indirect sensor readings.")

        # Query non-existent uncertainty
        non_existent_uncertainty = self.world_model.manage_uncertainty("non_existent_scope", query_uncertainty=True)
        self.assertIsNone(non_existent_uncertainty) # Should return None if not found

    def test_predict_future_state_placeholder(self):
        """Test the interface of predict_future_state."""
        action_sequence = [
            {"actor_id": "self", "verb": "move_to", "object_id": "loc_target"},
            {"actor_id": "self", "verb": "grasp", "object_id": "obj_graspable"}
        ]
        prediction = self.world_model.predict_future_state(action_sequence)
        self.assertIsInstance(prediction, dict)
        self.assertTrue(prediction.get("success")) # Current placeholder returns success=True
        self.assertIn("predicted_outcome_description", prediction)
        self.assertIn("predicted_effects_summary", prediction)
        self.assertIn("confidence", prediction)
        self.assertIsInstance(prediction["predicted_effects_summary"], list)

    def test_check_consistency_placeholder(self):
        """Test the interface of check_consistency."""
        consistency_report = self.world_model.check_consistency()
        self.assertIsInstance(consistency_report, dict)
        self.assertIn("consistent", consistency_report)
        self.assertIn("issues_found", consistency_report)
        self.assertIsInstance(consistency_report["issues_found"], list)
        self.assertIn("confidence_level", consistency_report)

    def test_get_world_model_status(self):
        """Test the status reporting method."""
        status = self.world_model.get_world_model_status()
        self.assertIsInstance(status, dict)
        self.assertEqual(status["model_id"], "test_wm_01")
        self.assertEqual(status["entity_count"], 0)
        self.assertEqual(status["spatial_data_count"], 0)
        # Add an entity to see if count changes
        entity_data = {"type": "entity_observation", "entity_id": "status_e1", "state": {}}
        self.world_model.update_from_perception(entity_data)
        updated_status = self.world_model.get_world_model_status()
        self.assertEqual(updated_status["entity_count"], 1)

    def test_add_spatial_data(self):
        """Test adding and retrieving spatial data."""
        current_time = time.time() # Not directly used by SpatialData but good for consistency
        spatial_data_perception = {
            "type": "spatial_observation", "spatial_id": "room101",
            "spatial_type": "area_room",
            "coordinates": None, # Rooms might not have a single coordinate point
            "orientation": None,
            "contains_entities": ["e1_in_room101"],
            "parent_area_id": "floor1"
        }
        update_success = self.world_model.update_from_perception(spatial_data_perception, timestamp=current_time)
        self.assertTrue(update_success)
        self.assertIn("room101", self.world_model._spatial_model)
        retrieved_spatial_data = self.world_model._spatial_model["room101"]
        self.assertIsInstance(retrieved_spatial_data, SpatialData)
        self.assertEqual(retrieved_spatial_data.id, "room101")
        self.assertEqual(retrieved_spatial_data.type, "area_room")
        self.assertIn("e1_in_room101", retrieved_spatial_data.contains_entities)

        query_result = self.world_model.query_world_state({"type": "spatial_data", "spatial_id": "room101"})
        self.assertTrue(query_result.get("success"))
        self.assertEqual(query_result["data"]["id"], "room101")


    def test_add_temporal_event(self):
        """Test adding and retrieving temporal events."""
        current_time = time.time()
        event_perception = {
            "type": "event_observation", 
            "event_id": "evt_light_on_001",
            "event_type": "state_change",
            "event_timestamp": current_time,
            "description": "Light L1 turned on.",
            "involved_entities": ["L1", "user_switch01"],
        }
        update_success = self.world_model.update_from_perception(event_perception, timestamp=current_time)
        self.assertTrue(update_success)
        self.assertEqual(len(self.world_model._temporal_model_events), 1)
        retrieved_event = self.world_model._temporal_model_events[0]
        self.assertIsInstance(retrieved_event, TemporalEvent)
        self.assertEqual(retrieved_event.id, "evt_light_on_001")
        self.assertIn("L1", retrieved_event.involved_entities)

        query_result = self.world_model.query_world_state(
            {"type": "events_in_timespan", "start_time": current_time -1, "end_time": current_time + 1}
        )
        self.assertTrue(query_result.get("success"))
        self.assertEqual(len(query_result.get("data", [])), 1)
        self.assertEqual(query_result["data"][0]["id"], "evt_light_on_001")

if __name__ == '__main__':
    unittest.main()
