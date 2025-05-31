import unittest
import os
import sys

# Adjust path to import from the parent directory (PiaCML)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from concrete_world_model import ConcreteWorldModel
except ImportError:
    if 'ConcreteWorldModel' not in globals(): # Fallback
        from PiaAGI_Hub.PiaCML.concrete_world_model import ConcreteWorldModel

class TestConcreteWorldModel(unittest.TestCase):

    def setUp(self):
        self.wm = ConcreteWorldModel()
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w') # Suppress prints

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_initial_status_and_properties(self):
        status = self.wm.get_module_status()
        self.assertEqual(status['module_type'], 'ConcreteWorldModel')
        self.assertEqual(status['entities_tracked'], 0)
        self.assertEqual(status['environment_properties_count'], 2) # time_of_day, weather_condition
        self.assertEqual(status['overall_uncertainty_metric'], 0.2) # Default

        self.assertEqual(self.wm.get_environment_property("time_of_day"), "noon")
        self.assertIsNone(self.wm.get_environment_property("non_existent_prop"))

    def test_update_model_from_perception_add_entities(self):
        perception_data = {
            "entities": [
                {"id": "e1", "type": "chair", "color": "brown"},
                {"id": "e2", "type": "table", "material": "wood"}
            ]
        }
        update_success = self.wm.update_model_from_perception(perception_data)
        self.assertTrue(update_success)

        status = self.wm.get_module_status()
        self.assertEqual(status['entities_tracked'], 2)

        e1_state = self.wm.get_entity_state("e1")
        self.assertIsNotNone(e1_state)
        self.assertEqual(e1_state['type'], "chair")
        self.assertEqual(e1_state['color'], "brown")

    def test_update_model_from_perception_merge_entities(self):
        perception1 = {"entities": [{"id": "objX", "value": 10, "static_prop": "A"}]}
        self.wm.update_model_from_perception(perception1)

        perception2 = {"entities": [{"id": "objX", "value": 20, "new_prop": "B"}]} # Update value, add new_prop
        self.wm.update_model_from_perception(perception2)

        objX_state = self.wm.get_entity_state("objX")
        self.assertEqual(objX_state['value'], 20)
        self.assertEqual(objX_state['static_prop'], "A") # Should persist
        self.assertEqual(objX_state['new_prop'], "B")
        self.assertEqual(self.wm.get_module_status()['entities_tracked'], 1)

    def test_update_model_invalid_perception_data(self):
        initial_entities_count = self.wm.get_module_status()['entities_tracked']

        # Test with 'entities' not being a list
        perception_invalid1 = {"entities": {"id": "e1", "type": "chair"}}
        self.assertFalse(self.wm.update_model_from_perception(perception_invalid1))
        self.assertEqual(self.wm.get_module_status()['entities_tracked'], initial_entities_count)

        # Test with entity data not being a dict or missing 'id'
        perception_invalid2 = {"entities": ["not_a_dict"]}
        self.assertTrue(self.wm.update_model_from_perception(perception_invalid2)) # Returns True, but skips invalid
        self.assertEqual(self.wm.get_module_status()['entities_tracked'], initial_entities_count)

        perception_invalid3 = {"entities": [{"type": "chair_no_id"}]}
        self.assertTrue(self.wm.update_model_from_perception(perception_invalid3)) # Returns True, but skips invalid
        self.assertEqual(self.wm.get_module_status()['entities_tracked'], initial_entities_count)


    def test_get_entity_state_specific_attribute(self):
        perception = {"entities": [{"id": "item1", "name": "Test Item", "state": "active"}]}
        self.wm.update_model_from_perception(perception)

        name_attr = self.wm.get_entity_state("item1", "name")
        self.assertEqual(name_attr, "Test Item")

        state_attr = self.wm.get_entity_state("item1", "state")
        self.assertEqual(state_attr, "active")

        self.assertIsNone(self.wm.get_entity_state("item1", "non_existent_attr"))

    def test_get_entity_state_non_existent_increases_uncertainty(self):
        initial_uncertainty = self.wm.get_uncertainty_level()
        self.wm.get_entity_state("phantom_id")
        self.assertGreater(self.wm.get_uncertainty_level(), initial_uncertainty)


    def test_predict_action_outcome_move(self):
        action = {'type': 'move', 'agent_id': 'ag1', 'target_location': [10,20]}
        prediction = self.wm.predict_action_outcome(action)
        self.assertEqual(len(prediction['predicted_state_changes']), 1)
        change = prediction['predicted_state_changes'][0]
        self.assertEqual(change['entity_id'], 'ag1')
        self.assertEqual(change['attribute_changed'], 'location')
        self.assertEqual(change['new_value'], [10,20])
        self.assertEqual(prediction['success_probability'], 0.7) # Default for valid move

    def test_predict_action_outcome_move_to_lava(self):
        action = {'type': 'move', 'agent_id': 'ag1', 'target_location': "lava_pit"}
        prediction = self.wm.predict_action_outcome(action)
        self.assertEqual(prediction['success_probability'], 0.2)
        self.assertIn("potential_damage_to_agent", prediction['potential_side_effects'])


    def test_predict_action_outcome_interact(self):
        action = {'type': 'interact_object', 'object_id': 'door1', 'interaction_type': 'open'}
        prediction = self.wm.predict_action_outcome(action)
        self.assertEqual(prediction['predicted_state_changes'][0]['new_value'], "interacted_with_open")

    def test_predict_action_outcome_unknown_action(self):
        action = {'type': 'levitate', 'object_id': 'rock1'}
        prediction = self.wm.predict_action_outcome(action)
        self.assertEqual(len(prediction['predicted_state_changes']), 0)
        self.assertEqual(prediction['success_probability'], 0.3)
        self.assertIn("unknown_action_type_unpredictable_outcome", prediction['potential_side_effects'])

    def test_get_uncertainty_level_specific_entity_placeholder(self):
        # This test assumes future enhancement where entities might have individual uncertainty scores
        self.wm._entities["e_uncertain"] = {"uncertainty_score": 0.88}
        self.assertEqual(self.wm.get_uncertainty_level("e_uncertain"), 0.88)
        # Test fallback to overall if specific not found or no score
        self.assertEqual(self.wm.get_uncertainty_level("e_no_score"), self.wm._uncertainty_metric)


if __name__ == '__main__':
    unittest.main()
