import unittest
import os
import sys
import time

# Adjust path to import from the parent directory (PiaCML)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from concrete_world_model import ConcreteWorldModel
except ImportError:
    # Fallback for different execution contexts
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from PiaAGI_Research_Tools.PiaCML.concrete_world_model import ConcreteWorldModel


class TestConcreteWorldModel(unittest.TestCase):

    def setUp(self):
        self.world_model = ConcreteWorldModel(model_id="test_wm_001")
        self._original_stdout = sys.stdout
        # sys.stdout = open(os.devnull, 'w') # Suppress prints if module is too verbose

    def tearDown(self):
        # sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_initial_status(self):
        status = self.world_model.get_world_model_status()
        self.assertEqual(status['model_id'], "test_wm_001")
        self.assertEqual(status['entity_count'], 0)
        self.assertEqual(status['event_count'], 0)
        self.assertEqual(status['social_models_count'], 0)
        self.assertTrue(status['last_updated_timestamp'] <= time.time())

    def test_update_from_perception_entity(self):
        ts_before = self.world_model.last_updated_timestamp
        percept_data = {"type": "entity_observation", "entity_id": "e1", "state": {"color": "red"}}
        success = self.world_model.update_from_perception(percept_data, timestamp=12345.0)
        self.assertTrue(success)

        entity_e1 = self.world_model.get_entity_representation("e1")
        self.assertIsNotNone(entity_e1)
        self.assertEqual(entity_e1['state']['color'], "red")
        self.assertEqual(entity_e1['last_observed_ts'], 12345.0)
        self.assertTrue(self.world_model.last_updated_timestamp > ts_before)
        self.assertEqual(self.world_model.get_world_model_status()['entity_count'], 1)

    def test_update_from_perception_unknown_type(self):
        success = self.world_model.update_from_perception({"type": "unknown_percept"}, timestamp=12346.0)
        self.assertFalse(success) # Basic impl only handles entity_observation

    def test_query_world_state_entity_and_all(self):
        self.world_model.update_from_perception({"type": "entity_observation", "entity_id": "e1", "state": {"color": "red"}})
        self.world_model.update_from_perception({"type": "entity_observation", "entity_id": "e2", "state": {"size": "large"}})

        query_e1 = self.world_model.query_world_state({"type": "entity_state", "entity_id": "e1"})
        self.assertTrue(query_e1['success'])
        self.assertEqual(query_e1['data']['state']['color'], "red")

        query_all = self.world_model.query_world_state({"type": "all_entities"})
        self.assertTrue(query_all['success'])
        self.assertEqual(len(query_all['data']), 2)

        query_non_existent = self.world_model.query_world_state({"type": "entity_state", "entity_id": "e3"})
        self.assertFalse(query_non_existent['success'])
        self.assertIn("not found", query_non_existent.get('error', '').lower())

        query_unsupported = self.world_model.query_world_state({"type": "unsupported_query"})
        self.assertFalse(query_unsupported['success'])
        self.assertIn("unsupported query type", query_unsupported.get('error', '').lower())


    def test_get_and_update_entity_state(self):
        self.world_model._entity_repository["e_test"] = {'id': 'e_test', 'state': {'val': 1}, 'type': 'test_obj', 'last_observed_ts': 0, 'last_updated_internal_ts': 0}

        retrieved = self.world_model.get_entity_representation("e_test")
        self.assertEqual(retrieved['state']['val'], 1)

        update_success = self.world_model.update_entity_state("e_test", {"val": 2, "new_prop": True}, timestamp=100.0)
        self.assertTrue(update_success)

        updated_entity = self.world_model.get_entity_representation("e_test")
        self.assertEqual(updated_entity['state']['val'], 2)
        self.assertTrue(updated_entity['state']['new_prop'])
        self.assertEqual(updated_entity['last_updated_internal_ts'], 100.0)

        update_fail = self.world_model.update_entity_state("non_existent", {"val": 3})
        self.assertFalse(update_fail)

    def test_predict_future_state_placeholder(self):
        actions = [{"actor_id": "self", "verb": "move_to", "object_id": "loc1"}]
        prediction = self.world_model.predict_future_state(actions)
        self.assertTrue(prediction['success'])
        self.assertIn("Conceptual prediction", prediction['predicted_outcome_description'])
        self.assertEqual(len(prediction['predicted_effects_summary']), 1)
        self.assertIn("Entity self might be at loc1", prediction['predicted_effects_summary'][0])

        prediction_no_actions = self.world_model.predict_future_state([])
        self.assertFalse(prediction_no_actions['success'])


    def test_get_and_update_social_model(self):
        self.assertIsNone(self.world_model.get_social_model_for_agent("agent1"))

        update1_success = self.world_model.update_social_model("agent1", {"mood": "happy"}, timestamp=200.0)
        self.assertTrue(update1_success)

        model1 = self.world_model.get_social_model_for_agent("agent1")
        self.assertIsNotNone(model1)
        self.assertEqual(model1['mood'], "happy")
        self.assertEqual(model1['last_updated_ts'], 200.0)
        self.assertEqual(self.world_model.get_world_model_status()['social_models_count'], 1)

        update2_success = self.world_model.update_social_model("agent1", {"goal_estimate": "find_food"})
        self.assertTrue(update2_success)
        model2 = self.world_model.get_social_model_for_agent("agent1")
        self.assertEqual(model2['mood'], "happy") # Should persist
        self.assertEqual(model2['goal_estimate'], "find_food")


    def test_manage_uncertainty_placeholder(self):
        scope_key = "entity_e1"
        # Query initial (default) uncertainty
        uncertainty1 = self.world_model.manage_uncertainty(scope_key, query_uncertainty=True)
        self.assertIsNotNone(uncertainty1)
        self.assertEqual(uncertainty1.get('confidence', 0.0), 0.0) # Default for unknown scope

        # Update uncertainty
        update_data = {"confidence": 0.75, "source": "perception_high_res"}
        update_result = self.world_model.manage_uncertainty(scope_key, uncertainty_data=update_data)
        self.assertIsNone(update_result) # Should return None on successful update

        # Query updated uncertainty
        uncertainty2 = self.world_model.manage_uncertainty(scope_key, query_uncertainty=True)
        self.assertEqual(uncertainty2['confidence'], 0.75)
        self.assertEqual(uncertainty2['source'], "perception_high_res")
        self.assertTrue(uncertainty2['last_updated_ts'] <= time.time())

        # Test update without data (should be an error or no-op)
        error_update = self.world_model.manage_uncertainty(scope_key, uncertainty_data=None)
        self.assertIsNotNone(error_update) # Expecting error dict
        self.assertIn('error', error_update)


    def test_check_consistency_placeholder(self):
        consistency_report = self.world_model.check_consistency()
        self.assertTrue(consistency_report['consistent'])
        self.assertEqual(len(consistency_report['issues_found']), 0)
        self.assertGreaterEqual(consistency_report['confidence_level'], 0.0)

    def test_get_world_model_status_updates(self):
        initial_status = self.world_model.get_world_model_status()

        self.world_model.update_from_perception({"type": "entity_observation", "entity_id": "e1", "state": {}})
        self.world_model.update_social_model("agentX", {"data": "some"})
        # _temporal_model_events is not directly updated by public methods in this concrete version yet

        updated_status = self.world_model.get_world_model_status()
        self.assertEqual(updated_status['entity_count'], initial_status['entity_count'] + 1)
        self.assertEqual(updated_status['social_models_count'], initial_status['social_models_count'] + 1)
        # self.assertEqual(updated_status['event_count'], initial_status['event_count'] + Y) # If events were added

if __name__ == '__main__':
    unittest.main()
