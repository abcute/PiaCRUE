from typing import Any, Dict, List, Optional

try:
    from .base_world_model import BaseWorldModel
except ImportError:
    from base_world_model import BaseWorldModel

class ConcreteWorldModel(BaseWorldModel):
    """
    A basic, concrete implementation of the BaseWorldModel.
    It uses dictionaries to store entity states and environment properties.
    Prediction and uncertainty are handled with very simple placeholders.
    """

    def __init__(self):
        self._entities: Dict[str, Dict[str, Any]] = {} # entity_id -> {attributes}
        self._environment_properties: Dict[str, Any] = {"time_of_day": "noon", "weather_condition": "clear"}
        self._update_log: List[str] = []
        self._uncertainty_metric: float = 0.2 # Default low uncertainty
        print("ConcreteWorldModel initialized.")

    def update_model_from_perception(self, perception_output: Dict[str, Any]) -> bool:
        """
        Updates the world model based on perception.
        Focuses on merging 'entities' from perception output.
        """
        log_entry = f"Updating from perception: {str(perception_output)[:100]}"
        self._update_log.append(log_entry)
        print(f"ConcreteWorldModel: {log_entry}")

        perceived_entities = perception_output.get('entities', [])
        if not isinstance(perceived_entities, list):
            print("ConcreteWorldModel: 'entities' in perception_output is not a list. No update performed.")
            return False

        for entity_data in perceived_entities:
            if not isinstance(entity_data, dict) or 'id' not in entity_data:
                print(f"ConcreteWorldModel: Skipping invalid entity data: {entity_data}")
                continue

            entity_id = entity_data['id']
            if entity_id not in self._entities:
                self._entities[entity_id] = {}

            # Merge attributes, new data overwrites old for same attribute
            for key, value in entity_data.items():
                if key == 'id': continue # Don't overwrite id into attributes sub-dict
                self._entities[entity_id][key] = value
            print(f"ConcreteWorldModel: Updated/added entity '{entity_id}' with data: {entity_data}")

        # Conceptually, update uncertainty if many new entities are seen
        if len(perceived_entities) > 3: # Arbitrary threshold
            self._uncertainty_metric = min(1.0, self._uncertainty_metric + 0.1 * len(perceived_entities))

        return True

    def get_entity_state(self, entity_id: str, attribute: Optional[str] = None) -> Optional[Any]:
        """Retrieves entity state or a specific attribute."""
        entity = self._entities.get(entity_id)
        if entity is None:
            self._uncertainty_metric = min(1.0, self._uncertainty_metric + 0.05) # Queried unknown entity
            return None

        if attribute:
            return entity.get(attribute)
        return dict(entity) # Return a copy of the entity's full state

    def get_environment_property(self, property_name: str) -> Optional[Any]:
        """Retrieves an environment property."""
        return self._environment_properties.get(property_name)

    def predict_action_outcome(self, action: Dict[str, Any], current_world_state_summary: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Rudimentary prediction based on action type."""
        print(f"ConcreteWorldModel: Predicting outcome for action: {action}")
        action_type = action.get('type')
        predicted_changes = []
        success_prob = 0.7 # Default moderate success
        side_effects = []

        if action_type == 'move':
            agent_id = action.get('agent_id')
            target_location = action.get('target_location')
            if agent_id and target_location:
                predicted_changes.append({'entity_id': agent_id, 'attribute_changed': 'location', 'new_value': target_location})
                # Conceptual: if target_location is known to be hazardous, reduce success_prob
                if isinstance(target_location, str) and "lava" in target_location.lower():
                    success_prob = 0.2
                    side_effects.append("potential_damage_to_agent")
            else:
                success_prob = 0.1 # Invalid params for move

        elif action_type == 'interact_object':
            object_id = action.get('object_id')
            interaction_type = action.get('interaction_type', 'use')
            if object_id:
                predicted_changes.append({'entity_id': object_id, 'attribute_changed': 'state', 'new_value': f"interacted_with_{interaction_type}"})
            else:
                success_prob = 0.2
        else:
            side_effects.append("unknown_action_type_unpredictable_outcome")
            success_prob = 0.3


        return {
            "predicted_state_changes": predicted_changes,
            "success_probability": success_prob,
            "potential_side_effects": side_effects,
            "confidence_in_prediction": 0.5 # Low for this basic model
        }

    def get_uncertainty_level(self, area: Optional[str] = None) -> float:
        """Returns a conceptual uncertainty level."""
        # This is a very basic placeholder. A real model would have complex uncertainty tracking.
        if area and area in self._entities and 'uncertainty_score' in self._entities[area]:
             return self._entities[area]['uncertainty_score']
        return self._uncertainty_metric

    def get_module_status(self) -> Dict[str, Any]:
        """Returns module status."""
        return {
            "module_type": "ConcreteWorldModel",
            "entities_tracked": len(self._entities),
            "environment_properties_count": len(self._environment_properties),
            "overall_uncertainty_metric": self._uncertainty_metric,
            "update_log_count": len(self._update_log)
        }

if __name__ == '__main__':
    world_model = ConcreteWorldModel()

    # Initial Status
    print("\n--- Initial Status ---")
    print(world_model.get_module_status())
    print("Initial weather:", world_model.get_environment_property("weather_condition"))

    # Update from perception
    print("\n--- Update from Perception ---")
    perception1 = {
        "entities": [
            {"id": "objA", "type": "box", "color": "red", "location": [10, 20]},
            {"id": "agent1", "type": "robot", "status": "active", "location": [0,0]}
        ]
    }
    world_model.update_model_from_perception(perception1)
    print("Status after perception1:", world_model.get_module_status())

    perception2 = { # Update objA, add objB
        "entities": [
            {"id": "objA", "color": "blue", "state": "open"}, # Location should persist
            {"id": "objB", "type": "sphere", "radius": 5, "location": [5,5]}
        ]
    }
    world_model.update_model_from_perception(perception2)
    print("Status after perception2:", world_model.get_module_status())


    # Get entity states
    print("\n--- Get Entity States ---")
    objA_state = world_model.get_entity_state("objA")
    print("State of objA:", objA_state)
    assert objA_state['color'] == 'blue' and objA_state['state'] == 'open' and objA_state['location'] == [10,20]

    agent1_location = world_model.get_entity_state("agent1", "location")
    print("Location of agent1:", agent1_location)
    assert agent1_location == [0,0]

    print("State of non_existent_entity:", world_model.get_entity_state("non_existent"))


    # Predict action outcome
    print("\n--- Predict Action Outcome ---")
    move_action = {'type': 'move', 'agent_id': 'agent1', 'target_location': [15, 25]}
    prediction1 = world_model.predict_action_outcome(move_action)
    print("Prediction for move action:", prediction1)
    assert prediction1['predicted_state_changes'][0]['new_value'] == [15,25]

    interact_action = {'type': 'interact_object', 'object_id': 'objA', 'interaction_type': 'close'}
    prediction2 = world_model.predict_action_outcome(interact_action)
    print("Prediction for interact action:", prediction2)
    assert prediction2['predicted_state_changes'][0]['new_value'] == "interacted_with_close"


    # Get uncertainty
    print("\n--- Uncertainty ---")
    print("Overall uncertainty:", world_model.get_uncertainty_level())
    # Querying a non-existent entity should have slightly increased uncertainty
    initial_uncertainty = 0.2
    # 1 call to non_existent entity, 2 perception updates with >3 entities implies +0.1 each if it were implemented fully
    # current basic logic: 0.2 (initial) + 0.05 (non_existent) = 0.25
    # The perception update uncertainty logic was commented out, let's assume it's not complex now.
    # If many entities in perception1 (2) and perception2 (2) -> no auto increase.
    # So, only one increase due to get_entity_state("non_existent").
    assert world_model.get_uncertainty_level() == initial_uncertainty + 0.05


    # Final Status
    print("\n--- Final Status ---")
    final_status = world_model.get_module_status()
    print(final_status)
    assert final_status['entities_tracked'] == 3 # objA, agent1, objB
    assert final_status['update_log_count'] == 2

    print("\nExample Usage Complete.")
