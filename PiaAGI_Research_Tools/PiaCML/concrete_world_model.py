from typing import Any, Dict, List, Optional, Union, Tuple
import time
import uuid
import asyncio # For __main__

try:
    from .base_world_model import BaseWorldModel
    from .message_bus import MessageBus
    from .core_messages import (
        GenericMessage, PerceptDataPayload, LTMQueryResultPayload, ActionEventPayload, MemoryItem,
        LTMQueryPayload # Though WM doesn't send LTM queries in this subtask, good to have for context
    )
except ImportError:
    print("Warning: Running ConcreteWorldModel with stubbed imports.")
    class BaseWorldModel: pass
    MessageBus = None # type: ignore
    GenericMessage = object # type: ignore
    PerceptDataPayload = object # type: ignore
    LTMQueryResultPayload = object # type: ignore
    ActionEventPayload = object # type: ignore
    MemoryItem = object # type: ignore
    LTMQueryPayload = object # type: ignore


# --- Data Classes Definition (Copied from original, ensure they are up-to-date) ---
class WorldEntity:
    def __init__(self, id: str, type: str, state: Dict[str, Any],
                 properties: Dict[str, Any], affordances: List[str],
                 relationships: Dict[str, List[str]],
                 last_observed_ts: Optional[float] = None,
                 location_id: Optional[str] = None):
        self.id: str = id
        self.type: str = type
        self.state: Dict[str, Any] = state # Current, potentially dynamic, state attributes
        self.properties: Dict[str, Any] = properties # More static properties
        self.affordances: List[str] = affordances
        self.relationships: Dict[str, List[str]] = relationships
        self.last_observed_ts: Optional[float] = last_observed_ts if last_observed_ts is not None else time.time()
        self.location_id: Optional[str] = location_id

    def to_dict(self) -> Dict[str, Any]: return self.__dict__

class SpatialData: # Unchanged for this task
    def __init__(self, id: str, type: str, coordinates: Optional[Tuple[float,float,float]] = None, orientation: Optional[Tuple[float,float,float,float]] = None, contains_entities: Optional[List[str]] = None, parent_area_id: Optional[str] = None):
        self.id, self.type, self.coordinates, self.orientation, self.parent_area_id = id, type, coordinates, orientation, parent_area_id
        self.contains_entities = contains_entities or []
    def to_dict(self) -> Dict[str, Any]: return self.__dict__

class TemporalEvent: # Unchanged for this task
    def __init__(self, id: str, type: str, timestamp: float, description: str, involved_entities: Optional[List[str]] = None, preceded_by_event_id: Optional[str] = None, followed_by_event_id: Optional[str] = None, causal_links: Optional[Dict[str, List[str]]] = None):
        self.id, self.type, self.timestamp, self.description = id, type, timestamp, description
        self.involved_entities = involved_entities or []
        self.preceded_by_event_id, self.followed_by_event_id = preceded_by_event_id, followed_by_event_id
        self.causal_links = causal_links or {'causes': [], 'effects': []}
    def to_dict(self) -> Dict[str, Any]: return self.__dict__

class SocialAgentModel: pass # Unchanged, assume defined as before
class PhysicsRule: pass # Unchanged, assume defined as before
class SelfStateSnapshot: pass # Unchanged, assume defined as before
class UncertaintyInfo: pass # Unchanged, assume defined as before

# --- ConcreteWorldModel Class ---
class ConcreteWorldModel(BaseWorldModel):
    def __init__(self,
                 message_bus: Optional[MessageBus] = None,
                 module_id: str = f"WorldModel_{str(uuid.uuid4())[:8]}"):
        self._module_id = module_id # Renamed from model_id for consistency
        self._message_bus = message_bus
        self.last_updated_timestamp: float = time.time()

        self._entity_repository: Dict[str, WorldEntity] = {}
        self._spatial_model: Dict[str, SpatialData] = {}
        self._temporal_model_events: List[TemporalEvent] = []
        self._social_model: Dict[str, SocialAgentModel] = {} # Not directly used by new handlers
        self._physics_rules: List[PhysicsRule] = [] # Not directly used by new handlers
        self._self_state_snapshot: SelfStateSnapshot = SelfStateSnapshot() # Not directly used by new handlers
        self._uncertainty_map: Dict[str, UncertaintyInfo] = {} # Not directly used by new handlers
        self._log: List[str] = []

        self._handled_message_counts: Dict[str, int] = {
            "PerceptData": 0, "LTMQueryResult": 0, "ActionEvent": 0
        }

        bus_status_msg = "not configured"
        if self._message_bus:
            core_types_ok = all([GenericMessage, PerceptDataPayload, LTMQueryResultPayload, ActionEventPayload, MemoryItem])
            if core_types_ok:
                try:
                    self._message_bus.subscribe(self._module_id, "PerceptData", self._handle_percept_data_message)
                    self._message_bus.subscribe(self._module_id, "LTMQueryResult", self._handle_ltm_query_result_message)
                    self._message_bus.subscribe(self._module_id, "ActionEvent", self._handle_action_event_message)
                    bus_status_msg = "configured and subscribed to PerceptData, LTMQueryResult, ActionEvent"
                except Exception as e: bus_status_msg = f"FAILED to subscribe: {e}"
            else: bus_status_msg = "core message types missing for subscription"
        self._log_message(f"ConcreteWorldModel '{self._module_id}' initialized. Message bus {bus_status_msg}.")

    def _log_message(self, message: str): self._log.append(f"{time.time():.2f} [{self._module_id}]: {message}")
    def _update_timestamp(self): self.last_updated_timestamp = time.time()

    # --- Message Handler Methods ---
    def _handle_percept_data_message(self, message: GenericMessage):
        if not isinstance(message.payload, PerceptDataPayload): return
        payload: PerceptDataPayload = message.payload
        self._handled_message_counts["PerceptData"] += 1
        self._log_message(f"Handling PerceptData (MsgID: {message.message_id}, PerceptID: {payload.percept_id}, Modality: {payload.modality})")

        if isinstance(payload.content, dict) and "entities" in payload.content:
            entities_data = payload.content["entities"]
            if isinstance(entities_data, list):
                for entity_dict in entities_data:
                    if not isinstance(entity_dict, dict): continue
                    entity_id = entity_dict.get("name", entity_dict.get("id", str(uuid.uuid4()))) # Prefer name, then id, then new UUID
                    entity_type = entity_dict.get("type", "unknown_from_percept")

                    observed_state = {"source_percept_id": payload.percept_id, "raw_observed": entity_dict}
                    # Could refine state further based on entity_dict keys

                    if entity_id in self._entity_repository:
                        entity = self._entity_repository[entity_id]
                        entity.state.update(observed_state) # Merge new observations
                        entity.last_observed_ts = payload.source_timestamp.timestamp() if payload.source_timestamp else time.time()
                        if entity_dict.get("location_id"): entity.location_id = entity_dict.get("location_id")
                        self._log_message(f"Updated entity '{entity_id}' from percept.")
                    else:
                        self._entity_repository[entity_id] = WorldEntity(
                            id=entity_id, type=entity_type, state=observed_state,
                            properties=entity_dict.get("properties", {"original_details": entity_dict}), # Store original dict as a property
                            affordances=entity_dict.get("affordances", []), relationships={},
                            last_observed_ts=payload.source_timestamp.timestamp() if payload.source_timestamp else time.time(),
                            location_id=entity_dict.get("location_id")
                        )
                        self._log_message(f"Created new entity '{entity_id}' from percept.")
                    self._update_timestamp()

    def _handle_ltm_query_result_message(self, message: GenericMessage):
        if not isinstance(message.payload, LTMQueryResultPayload): return
        payload: LTMQueryResultPayload = message.payload
        self._handled_message_counts["LTMQueryResult"] += 1
        self._log_message(f"Handling LTMQueryResult (QueryID: {payload.query_id}, Success: {payload.success_status}, Results: {len(payload.results)})")

        if payload.success_status:
            for item in payload.results:
                if isinstance(item, MemoryItem) and isinstance(item.content, dict):
                    # Conceptual: Check if item.content or item.metadata suggests an entity
                    item_type_from_meta = item.metadata.get("type")
                    if item_type_from_meta == "semantic_node" or item_type_from_meta == "entity_detail_from_ltm":
                        entity_id = item.item_id
                        content_dict = item.content
                        entity_type = content_dict.get("node_type", content_dict.get("type", "unknown_from_ltm"))

                        state = content_dict.get("properties", content_dict.get("state", {}))
                        state["ltm_source_query_id"] = payload.query_id
                        properties = {"label": content_dict.get("label", entity_id), "ltm_metadata": item.metadata}

                        if entity_id in self._entity_repository:
                            entity = self._entity_repository[entity_id]
                            entity.state.update(state)
                            entity.properties.update(properties) # Merge properties
                            entity.last_observed_ts = item.timestamp.timestamp() if item.timestamp else time.time()
                            self._log_message(f"Updated entity '{entity_id}' from LTM result.")
                        else:
                            self._entity_repository[entity_id] = WorldEntity(
                                id=entity_id, type=entity_type, state=state, properties=properties,
                                affordances=content_dict.get("affordances", []), relationships=content_dict.get("relationships", {}),
                                last_observed_ts=item.timestamp.timestamp() if item.timestamp else time.time(),
                                location_id=content_dict.get("location_id")
                            )
                            self._log_message(f"Created new entity '{entity_id}' from LTM result.")
                        self._update_timestamp()

    def _handle_action_event_message(self, message: GenericMessage):
        if not isinstance(message.payload, ActionEventPayload): return
        payload: ActionEventPayload = message.payload
        self._handled_message_counts["ActionEvent"] += 1
        ts = payload.timestamp.timestamp() if payload.timestamp else time.time()
        self._log_message(f"Handling ActionEvent (CmdID: {payload.action_command_id}, Type: {payload.action_type}, Status: {payload.status})")

        # Add to temporal model
        event_id = f"evt_action_{payload.action_command_id}_{payload.status.lower()}"
        involved: List[str] = []
        if payload.outcome and payload.outcome.get("agent_id"): involved.append(payload.outcome["agent_id"])
        if payload.outcome and payload.outcome.get("object_id"): involved.append(payload.outcome["object_id"])
        
        temporal_event = TemporalEvent(
            id=event_id, type=f"action_outcome_{payload.action_type}", timestamp=ts,
            description=f"Action '{payload.action_type}' (CmdID: {payload.action_command_id}) resulted in {payload.status}. Outcome: {str(payload.outcome)[:100]}",
            involved_entities=involved
        )
        self._temporal_model_events.append(temporal_event)

        # Update entity states based on outcome
        if payload.status == "SUCCESS" and payload.outcome:
            if payload.action_type.upper() == "MOVE_AGENT" or "MOVE_TO" in payload.action_type.upper() : # Flexible check
                agent_id = payload.outcome.get("agent_id", payload.outcome.get("entity_id"))
                new_loc_id = payload.outcome.get("new_location_id", payload.outcome.get("location_id"))
                if agent_id and new_loc_id and agent_id in self._entity_repository:
                    self._entity_repository[agent_id].location_id = new_loc_id
                    self._entity_repository[agent_id].last_observed_ts = ts
                    self._log_message(f"Entity '{agent_id}' moved to '{new_loc_id}' due to ActionEvent.")
                    self._update_timestamp()
            
            elif payload.action_type.upper() == "CREATE_OBJECT":
                obj_id = payload.outcome.get("object_id")
                obj_type = payload.outcome.get("object_type", "unknown_created_object")
                obj_loc = payload.outcome.get("location_id")
                obj_state = payload.outcome.get("state", {})
                obj_props = payload.outcome.get("properties", {})
                if obj_id:
                    if obj_id not in self._entity_repository:
                        self._entity_repository[obj_id] = WorldEntity(
                            id=obj_id, type=obj_type, state=obj_state, properties=obj_props,
                            affordances=[], relationships={}, last_observed_ts=ts, location_id=obj_loc
                        )
                        self._log_message(f"New entity '{obj_id}' created due to ActionEvent.")
                        self._update_timestamp()
                    else: # Object already existed, update its state if provided
                        self._entity_repository[obj_id].state.update(obj_state)
                        self._entity_repository[obj_id].properties.update(obj_props)
                        self._entity_repository[obj_id].last_observed_ts = ts
                        if obj_loc: self._entity_repository[obj_id].location_id = obj_loc
                        self._log_message(f"Entity '{obj_id}' state updated due to CREATE_OBJECT ActionEvent.")
                        self._update_timestamp()


    # --- Existing Methods (ensure they use self._module_id in logs if applicable) ---
    # For brevity, I'm assuming methods like update_from_perception, query_world_state, etc.,
    # are kept and will be adapted to use the new internal structures if they weren't already.
    # The primary change is how data *enters* the WM (via handlers).
    # update_entity_state and get_entity_representation are core and used.

    def get_entity_representation(self, entity_id: str) -> Optional[WorldEntity]:
        self._log_message(f"Getting entity representation for {entity_id}")
        return self._entity_repository.get(entity_id)

    def update_entity_state(self, entity_id: str, new_state_info: Dict[str, Any], timestamp: Optional[float] = None) -> bool:
        # (This method is used internally by handlers now or can be called directly)
        ts = timestamp if timestamp is not None else time.time()
        entity = self._entity_repository.get(entity_id)
        if entity:
            self._log_message(f"Updating entity '{entity_id}' state with {new_state_info}")
            entity.state.update(new_state_info.get("state", {}))
            entity.properties.update(new_state_info.get("properties", {}))
            if "location_id" in new_state_info: entity.location_id = new_state_info["location_id"]
            entity.last_observed_ts = ts
            self._update_timestamp()
            return True
        self._log_message(f"Entity '{entity_id}' not found for state update.")
        return False

    # Placeholder for other methods from original like query_world_state, predict_future_state etc.
    # They would need to be reviewed to ensure they use the new _entity_repository etc. correctly.
    def query_world_state(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        self._log_message(f"Querying world state with params: {query_params}")
        # Basic implementation, can be expanded
        if query_params.get("type") == "entity_state" and "entity_id" in query_params:
            entity = self.get_entity_representation(query_params["entity_id"])
            return {"success": True, "data": entity.to_dict()} if entity else {"success": False, "error": "Entity not found"}
        if query_params.get("type") == "all_entities":
            return {"success": True, "data": [e.to_dict() for e in self._entity_repository.values()]}
        if query_params.get("type") == "recent_events":
            count = query_params.get("count", 5)
            return {"success": True, "data": [e.to_dict() for e in self._temporal_model_events[-count:]]}
        return {"success": False, "error": "Unsupported query"}


    def get_world_model_status(self) -> Dict[str, Any]: # Renamed from get_status for clarity
        self._log_message("Getting world model status.")
        return {
            'module_id': self._module_id,
            'message_bus_configured': self._message_bus is not None,
            'last_updated_timestamp': self.last_updated_timestamp,
            'entity_count': len(self._entity_repository),
            'spatial_data_count': len(self._spatial_model), # Not currently updated by handlers
            'event_count': len(self._temporal_model_events),
            'handled_message_counts': dict(self._handled_message_counts),
            'log_entry_count': len(self._log)
        }

if __name__ == '__main__':
    print("\n--- ConcreteWorldModel __main__ Test ---")

    async def main_test_flow():
        bus = MessageBus()
        wm_module_id = "TestWorldModel001"
        world_model = ConcreteWorldModel(message_bus=bus, module_id=wm_module_id)

        print(world_model.get_world_model_status())

        print("\n--- Testing Subscriptions ---")
        # 1. PerceptData with entities
        percept_content_entities = {
            "type": "visual_scene", # Example, not directly used by WM handler's entity parsing
            "entities": [
                {"id": "apple01", "name": "RedApple", "type": "fruit", "state": {"color": "red"}},
                {"name": "TableTop", "type": "surface", "properties": {"material": "wood"}} # ID will be 'TableTop'
            ]
        }
        pd_payload1 = PerceptDataPayload(percept_id="p1", modality="visual", content=percept_content_entities, source_timestamp=datetime.datetime.now())
        bus.publish(GenericMessage(source_module_id="TestPerceptSys", message_type="PerceptData", payload=pd_payload1))
        await asyncio.sleep(0.01)

        assert "RedApple" in world_model._entity_repository
        assert world_model._entity_repository["RedApple"].type == "fruit"
        assert world_model._entity_repository["RedApple"].state.get("source_percept_id") == "p1"
        assert "TableTop" in world_model._entity_repository
        print("  WM processed PerceptData with entities.")

        # 2. LTMQueryResult with entity data
        ltm_item_content = {"node_type": "furniture", "label": "OldChair", "properties": {"material": "oak"}}
        ltm_results_payload = LTMQueryResultPayload(query_id="q_ltm1", results=[
            MemoryItem(item_id="chair05", content=ltm_item_content, metadata={"type": "semantic_node"})
        ], success_status=True)
        bus.publish(GenericMessage(source_module_id="TestLTMSys", message_type="LTMQueryResult", payload=ltm_results_payload))
        await asyncio.sleep(0.01)

        assert "chair05" in world_model._entity_repository
        assert world_model._entity_repository["chair05"].type == "furniture"
        assert world_model._entity_repository["chair05"].properties.get("label") == "OldChair"
        print("  WM processed LTMQueryResult with entity data.")

        # 3. ActionEvent - MOVE_AGENT
        action_event_move = ActionEventPayload(
            action_command_id="cmd_move1", action_type="MOVE_AGENT", status="SUCCESS",
            outcome={"agent_id": "RedApple", "new_location_id": "loc_floor"} # RedApple is not an agent, but test entity update
        )
        bus.publish(GenericMessage(source_module_id="TestExecSys", message_type="ActionEvent", payload=action_event_move))
        await asyncio.sleep(0.01)

        assert world_model._entity_repository["RedApple"].location_id == "loc_floor"
        assert len(world_model._temporal_model_events) == 1
        assert world_model._temporal_model_events[0].type == "action_outcome_MOVE_AGENT"
        print("  WM processed MOVE_AGENT ActionEvent, updated entity location and added temporal event.")

        # 4. ActionEvent - CREATE_OBJECT
        action_event_create = ActionEventPayload(
            action_command_id="cmd_create1", action_type="CREATE_OBJECT", status="SUCCESS",
            outcome={"object_id": "box01", "object_type": "container", "location_id": "loc_tabletop", "state": {"color":"blue"}}
        )
        bus.publish(GenericMessage(source_module_id="TestFabSys", message_type="ActionEvent", payload=action_event_create))
        await asyncio.sleep(0.01)

        assert "box01" in world_model._entity_repository
        assert world_model._entity_repository["box01"].type == "container"
        assert world_model._entity_repository["box01"].location_id == "loc_tabletop"
        assert world_model._entity_repository["box01"].state.get("color") == "blue"
        assert len(world_model._temporal_model_events) == 2
        print("  WM processed CREATE_OBJECT ActionEvent, created new entity and added temporal event.")

        print("\n--- Final World Model Status ---")
        final_status = world_model.get_world_model_status()
        print(final_status)
        assert final_status["entity_count"] == 4 # RedApple, TableTop, chair05, box01
        assert final_status["event_count"] == 2
        assert final_status["handled_message_counts"]["PerceptData"] == 1
        assert final_status["handled_message_counts"]["LTMQueryResult"] == 1
        assert final_status["handled_message_counts"]["ActionEvent"] == 2

        print("\n--- ConcreteWorldModel __main__ Test Complete ---")

    try:
        asyncio.run(main_test_flow())
    except RuntimeError as e:
        if " asyncio.run() cannot be called from a running event loop" in str(e):
            print("Skipping asyncio.run() as an event loop is already running.")
        else:
            raise
