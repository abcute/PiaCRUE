import unittest
import asyncio
import uuid
import time
from typing import List, Any, Dict
from datetime import datetime, timezone

# Adjust path for consistent imports
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    from PiaAGI_Research_Tools.PiaCML.message_bus import MessageBus
    from PiaAGI_Research_Tools.PiaCML.core_messages import (
        GenericMessage, PerceptDataPayload, LTMQueryResultPayload, ActionEventPayload, MemoryItem
    )
    from PiaAGI_Research_Tools.PiaCML.concrete_world_model import (
        ConcreteWorldModel, WorldEntity, TemporalEvent # Import internal classes for assertions
    )
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from message_bus import MessageBus
    from core_messages import (
        GenericMessage, PerceptDataPayload, LTMQueryResultPayload, ActionEventPayload, MemoryItem
    )
    from concrete_world_model import ConcreteWorldModel, WorldEntity, TemporalEvent

class TestConcreteWorldModelModuleIntegration(unittest.TestCase):

    def setUp(self):
        self.bus = MessageBus()
        self.module_id = f"TestWorldModelModule_{str(uuid.uuid4())[:8]}"
        # Module instantiated per test method for a clean state

    def tearDown(self):
        # Cleanup if necessary, though new bus/module per test is generally clean
        pass

    # --- Test Subscription Handlers and Internal State Updates ---
    def test_handle_percept_data_updates_entities(self):
        world_model = ConcreteWorldModel(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            ts = datetime.now(timezone.utc)
            percept_entities = [
                {"id": "obj1", "name": "Apple", "type": "fruit", "state": {"color": "red"}},
                {"name": "Desk", "type": "furniture"} # ID will be "Desk"
            ]
            percept_content = {"entities": percept_entities} # Simplified from actual perception module output for directness

            pd_payload = PerceptDataPayload(percept_id="p1", modality="visual", content=percept_content, source_timestamp=ts)
            bus_msg = GenericMessage("PerceptSys", "PerceptData", pd_payload, message_id="percept_msg1")

            self.bus.publish(bus_msg)
            await asyncio.sleep(0.01)

            self.assertEqual(world_model._handled_message_counts["PerceptData"], 1)

            apple_entity = world_model.get_entity_representation("Apple") # Name is preferred for ID
            self.assertIsNotNone(apple_entity)
            self.assertEqual(apple_entity.type, "fruit")
            self.assertEqual(apple_entity.state.get("source_percept_id"), "p1")
            self.assertEqual(apple_entity.state.get("raw_observed",{}).get("state",{}).get("color"), "red")

            desk_entity = world_model.get_entity_representation("Desk")
            self.assertIsNotNone(desk_entity)
            self.assertEqual(desk_entity.type, "furniture")

            # Test update
            updated_percept_entities = [{"id": "obj1", "name": "Apple", "type": "fruit", "state": {"color": "green"}}]
            updated_percept_content = {"entities": updated_percept_entities}
            pd_payload_update = PerceptDataPayload(percept_id="p2", modality="visual", content=updated_percept_content, source_timestamp=ts)
            bus_msg_update = GenericMessage("PerceptSys", "PerceptData", pd_payload_update, message_id="percept_msg2")
            self.bus.publish(bus_msg_update)
            await asyncio.sleep(0.01)

            apple_entity_updated = world_model.get_entity_representation("Apple")
            self.assertIsNotNone(apple_entity_updated)
            self.assertEqual(apple_entity_updated.state.get("raw_observed",{}).get("state",{}).get("color"), "green")
            self.assertEqual(apple_entity_updated.state.get("source_percept_id"), "p2") # Check if state merges or replaces

        asyncio.run(run_test_logic())

    def test_handle_ltm_query_result_updates_entities(self):
        world_model = ConcreteWorldModel(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            ltm_entity_content = {"node_type": "vehicle", "label": "SedanCar", "properties": {"color": "blue", "wheels": 4}}
            ltm_results = [
                MemoryItem(item_id="car001", content=ltm_entity_content, metadata={"type": "semantic_node"}, timestamp=datetime.now(timezone.utc))
            ]
            ltm_payload = LTMQueryResultPayload(query_id="q_ltm_wm1", results=ltm_results, success_status=True)
            bus_msg = GenericMessage("LTMSys", "LTMQueryResult", ltm_payload)

            self.bus.publish(bus_msg)
            await asyncio.sleep(0.01)

            self.assertEqual(world_model._handled_message_counts["LTMQueryResult"], 1)
            car_entity = world_model.get_entity_representation("car001")
            self.assertIsNotNone(car_entity)
            self.assertEqual(car_entity.type, "vehicle")
            self.assertEqual(car_entity.properties.get("label"), "SedanCar")
            self.assertEqual(car_entity.state.get("color"), "blue") # Properties from LTM might go into state or properties
            self.assertEqual(car_entity.state.get("wheels"), 4)

        asyncio.run(run_test_logic())

    def test_handle_action_event_updates_entities_and_temporal_log(self):
        world_model = ConcreteWorldModel(message_bus=self.bus, module_id=self.module_id)
        async def run_test_logic():
            # Initial entity for MOVE_AGENT
            agent_to_move_id = "agent_m1"
            world_model._entity_repository[agent_to_move_id] = WorldEntity(
                id=agent_to_move_id, type="robot_agent", state={"status":"idle"},
                properties={}, affordances=[], relationships={}, location_id="loc_start"
            )

            # 1. Test MOVE_AGENT
            action_event_move = ActionEventPayload(
                action_command_id="cmd_move_wm1", action_type="MOVE_AGENT", status="SUCCESS",
                outcome={"agent_id": agent_to_move_id, "new_location_id": "loc_finish"},
                timestamp=datetime.now(timezone.utc)
            )
            bus_msg_move = GenericMessage("ExecSys", "ActionEvent", action_event_move)
            self.bus.publish(bus_msg_move)
            await asyncio.sleep(0.01)

            self.assertEqual(world_model._handled_message_counts["ActionEvent"], 1)
            moved_agent = world_model.get_entity_representation(agent_to_move_id)
            self.assertIsNotNone(moved_agent)
            self.assertEqual(moved_agent.location_id, "loc_finish")
            self.assertEqual(len(world_model._temporal_model_events), 1)
            self.assertEqual(world_model._temporal_model_events[0].type, "action_outcome_MOVE_AGENT")

            # 2. Test CREATE_OBJECT
            action_event_create = ActionEventPayload(
                action_command_id="cmd_create_wm1", action_type="CREATE_OBJECT", status="SUCCESS",
                outcome={"object_id": "new_box01", "object_type": "container", "location_id": "loc_on_desk", "state": {"color":"brown"}},
                timestamp=datetime.now(timezone.utc)
            )
            bus_msg_create = GenericMessage("FabSys", "ActionEvent", action_event_create)
            self.bus.publish(bus_msg_create)
            await asyncio.sleep(0.01)

            self.assertEqual(world_model._handled_message_counts["ActionEvent"], 2)
            new_object = world_model.get_entity_representation("new_box01")
            self.assertIsNotNone(new_object)
            self.assertEqual(new_object.type, "container")
            self.assertEqual(new_object.location_id, "loc_on_desk")
            self.assertEqual(new_object.state.get("color"), "brown")
            self.assertEqual(len(world_model._temporal_model_events), 2)
            self.assertEqual(world_model._temporal_model_events[1].type, "action_outcome_CREATE_OBJECT")

        asyncio.run(run_test_logic())

    # --- Test No Bus Scenario ---
    def test_initialization_and_direct_methods_without_bus(self):
        world_model_no_bus = ConcreteWorldModel(message_bus=None, module_id="NoBusWM")
        status = world_model_no_bus.get_world_model_status() # Use the renamed get_world_model_status
        self.assertFalse(status["message_bus_configured"])
        self.assertEqual(status["module_id"], "NoBusWM")

        # Test direct update_from_perception (if it's still intended for direct use)
        # The refactored module relies on handlers. Direct update_from_perception might be deprecated
        # or only used internally. For this test, we assume it's still callable.
        try:
            percept_data = {"type": "entity_observation", "entity_id": "e_nobus", "entity_type": "test"}
            world_model_no_bus.update_from_perception(percept_data) # This method exists in the provided file
            entity = world_model_no_bus.get_entity_representation("e_nobus")
            self.assertIsNotNone(entity)
        except Exception as e:
            self.fail(f"Direct method call raised an exception with no bus: {e}")
        
        self.assertEqual(world_model_no_bus._handled_message_counts["PerceptData"], 0)


    # --- Test get_world_model_status ---
    def test_get_world_model_status(self):
        world_model = ConcreteWorldModel(message_bus=self.bus, module_id=self.module_id)
        initial_status = world_model.get_world_model_status()
        self.assertEqual(initial_status["module_id"], self.module_id)
        self.assertTrue(initial_status["message_bus_configured"])
        self.assertEqual(initial_status["entity_count"], 0)
        self.assertEqual(initial_status["event_count"], 0)
        self.assertEqual(initial_status["handled_message_counts"]["PerceptData"], 0)

        # Simulate a percept being handled
        async def run_activity():
            ts = datetime.now(timezone.utc)
            percept_payload = PerceptDataPayload(percept_id="p_status", modality="text", content={"entities": [{"name":"status_entity"}]}, source_timestamp=ts)
            bus_msg = GenericMessage("StatusTestSys", "PerceptData", percept_payload)
            self.bus.publish(bus_msg)
            await asyncio.sleep(0.01)
        asyncio.run(run_activity())

        updated_status = world_model.get_world_model_status()
        self.assertEqual(updated_status["entity_count"], 1)
        self.assertEqual(updated_status["handled_message_counts"]["PerceptData"], 1)


class TestConcreteWorldModelAdvancedLogic(unittest.TestCase):

    def setUp(self):
        self.world_model = ConcreteWorldModel(message_bus=None, module_id="TestWMLogic")
        # Ensure clean state for repositories for each test
        self.world_model._entity_repository = {}
        self.world_model._temporal_model_events = []
        self.world_model._log = [] # Clear logs too

    def test_predict_future_state(self):
        # Test case 1: Entity with velocity and position, no obstacle
        entity1_id = "car1"
        self.world_model._entity_repository[entity1_id] = WorldEntity(
            id=entity1_id, type="vehicle",
            state={"position": [0, 0, 0], "velocity": [10, 5, 0]},
            properties={}, affordances=[], relationships={}
        )
        prediction1 = self.world_model.predict_future_state(entity1_id, time_horizon=2.0)
        self.assertIsNotNone(prediction1)
        self.assertEqual(prediction1["state"]["position"], [20, 10, 0])
        self.assertEqual(prediction1["prediction_confidence"], "high")
        self.assertIn(f"Predicted new position for '{entity1_id}'", self.world_model._log[-1])

        # Test case 2: Entity without velocity
        entity2_id = "rock1"
        self.world_model._entity_repository[entity2_id] = WorldEntity(
            id=entity2_id, type="static_object",
            state={"position": [10, 10, 10]},
            properties={}, affordances=[], relationships={}
        )
        prediction2 = self.world_model.predict_future_state(entity2_id, time_horizon=2.0)
        self.assertIsNotNone(prediction2)
        self.assertEqual(prediction2["state"]["position"], [10, 10, 10]) # Position unchanged
        self.assertEqual(prediction2["prediction_confidence"], "low")
        self.assertIn(f"No specific prediction rules applicable for '{entity2_id}'", self.world_model._log[-1])

        # Test case 3: Entity with velocity but an obstacle
        entity3_id = "car2_blocked"
        self.world_model._entity_repository[entity3_id] = WorldEntity(
            id=entity3_id, type="vehicle",
            state={"position": [0, 0, 0], "velocity": [10, 0, 0]},
            properties={}, affordances=[], relationships={"obstacle": ["wall1"]}
        )
        prediction3 = self.world_model.predict_future_state(entity3_id, time_horizon=2.0)
        self.assertIsNotNone(prediction3)
        self.assertEqual(prediction3["state"]["position"], [0, 0, 0]) # Position unchanged
        self.assertEqual(prediction3["prediction_confidence"], "low") # Or "medium_uncertain" if logic changes
        self.assertIn(f"No specific prediction rules applicable for '{entity3_id}'", self.world_model._log[-1])


        # Test case 4: Non-existent entity
        prediction4 = self.world_model.predict_future_state("non_existent_entity", time_horizon=2.0)
        self.assertIsNone(prediction4)
        self.assertIn("Prediction failed: Entity 'non_existent_entity' not found", self.world_model._log[-1])

    def test_query_world_state_advanced_queries(self):
        # Populate entities
        self.world_model._entity_repository = {
            "e1": WorldEntity(id="e1", type="fruit", state={}, properties={}, affordances=[], relationships={}, location_id="loc1"),
            "e2": WorldEntity(id="e2", type="tool", state={}, properties={}, affordances=[], relationships={}, location_id="loc2"),
            "e3": WorldEntity(id="e3", type="fruit", state={}, properties={}, affordances=[], relationships={}, location_id="loc1"),
            "e4": WorldEntity(id="e4", type="animal", state={}, properties={}, affordances=[], relationships={}, location_id="loc3"),
        }
        # Populate events
        self.world_model._temporal_model_events = [
            TemporalEvent(id="evt1", type="perception_event", timestamp=time.time() - 10, description="Saw fruit", involved_entities=["e1", "e4"]),
            TemporalEvent(id="evt2", type="interaction_event", timestamp=time.time() - 5, description="Tool used", involved_entities=["e2", "agent01"]),
            TemporalEvent(id="evt3", type="perception_event", timestamp=time.time() - 2, description="Saw more fruit", involved_entities=["e3"]),
        ]

        # Test 1: Query entities by type
        query_fruit = self.world_model.query_world_state({"query_type": "entities_by_type", "entity_type": "fruit"})
        self.assertTrue(query_fruit["success"])
        self.assertEqual(len(query_fruit["data"]), 2)
        self.assertIn("Query: Get entities by type 'fruit'", self.world_model._log[-1])

        # Test 2: Query entities by location_id
        query_loc1 = self.world_model.query_world_state({"query_type": "entities_by_location", "location_id": "loc1"})
        self.assertTrue(query_loc1["success"])
        self.assertEqual(len(query_loc1["data"]), 2)
        entity_ids_in_loc1 = {e["id"] for e in query_loc1["data"]}
        self.assertEqual(entity_ids_in_loc1, {"e1", "e3"})
        self.assertIn("Query: Get entities by location_id 'loc1'", self.world_model._log[-1])

        # Test 3: Query events by event_type
        query_percept_events = self.world_model.query_world_state({"query_type": "events_by_type", "event_type": "perception_event"})
        self.assertTrue(query_percept_events["success"])
        self.assertEqual(len(query_percept_events["data"]), 2)
        self.assertIn("Query: Get events by type 'perception_event'", self.world_model._log[-1])

        # Test 4: Query events by involved_entities
        query_events_e1_or_e2 = self.world_model.query_world_state({"query_type": "events_by_involved_entities", "entity_ids": ["e1", "e2"]})
        self.assertTrue(query_events_e1_or_e2["success"])
        self.assertEqual(len(query_events_e1_or_e2["data"]), 2) # evt1 (e1), evt2 (e2)
        event_ids_e1_e2 = {e["id"] for e in query_events_e1_or_e2["data"]}
        self.assertEqual(event_ids_e1_e2, {"evt1", "evt2"})
        self.assertIn("Query: Get events by involved entities (any of: ['e1', 'e2'])", self.world_model._log[-1])

        query_events_e4_only = self.world_model.query_world_state({"query_type": "events_by_involved_entities", "entity_ids": ["e4"]})
        self.assertTrue(query_events_e4_only["success"])
        self.assertEqual(len(query_events_e4_only["data"]), 1) # evt1 (e1, e4)
        self.assertEqual(query_events_e4_only["data"][0]["id"], "evt1")


        # Test 5: Query with unknown query_type
        query_unknown = self.world_model.query_world_state({"query_type": "non_existent_query", "param": "value"})
        self.assertFalse(query_unknown["success"])
        self.assertIn("Unsupported query_type", query_unknown.get("error", ""))
        self.assertIn("Query: Unsupported query type 'non_existent_query'", self.world_model._log[-1])

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

```
