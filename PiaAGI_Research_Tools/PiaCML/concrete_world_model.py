from typing import Any, Dict, List, Optional, Union, Tuple
import time
import uuid
import asyncio # For __main__
import math
import copy

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
        query_type = query_params.get("query_type") # Changed "type" to "query_type" for clarity

        if query_type == "entity_state" and "entity_id" in query_params:
            entity_id = query_params["entity_id"]
            self._log_message(f"Query: Get entity state for '{entity_id}'.")
            entity = self.get_entity_representation(entity_id)
            return {"success": True, "data": entity.to_dict()} if entity else {"success": False, "error": f"Entity '{entity_id}' not found"}

        elif query_type == "all_entities":
            self._log_message("Query: Get all entities.")
            return {"success": True, "data": [e.to_dict() for e in self._entity_repository.values()]}

        elif query_type == "entities_by_type" and "entity_type" in query_params:
            entity_type_query = query_params["entity_type"]
            self._log_message(f"Query: Get entities by type '{entity_type_query}'.")
            result = [e.to_dict() for e in self._entity_repository.values() if e.type == entity_type_query]
            return {"success": True, "data": result}

        elif query_type == "entities_by_location" and "location_id" in query_params:
            location_id_query = query_params["location_id"]
            self._log_message(f"Query: Get entities by location_id '{location_id_query}'.")
            result = [e.to_dict() for e in self._entity_repository.values() if e.location_id == location_id_query]
            return {"success": True, "data": result}

        elif query_type == "recent_events":
            count = query_params.get("count", 5)
            self._log_message(f"Query: Get {count} recent events.")
            return {"success": True, "data": [e.to_dict() for e in self._temporal_model_events[-count:]]}

        elif query_type == "events_by_type" and "event_type" in query_params:
            event_type_query = query_params["event_type"]
            self._log_message(f"Query: Get events by type '{event_type_query}'.")
            result = [e.to_dict() for e in self._temporal_model_events if e.type == event_type_query]
            return {"success": True, "data": result}

        elif query_type == "events_by_involved_entities" and "entity_ids" in query_params:
            entity_ids_query = query_params["entity_ids"]
            if not isinstance(entity_ids_query, list):
                self._log_message("Query: Get events by involved entities - FAILED (entity_ids not a list).")
                return {"success": False, "error": "entity_ids must be a list"}
            self._log_message(f"Query: Get events by involved entities (any of: {entity_ids_query}).")
            result = [
                e.to_dict() for e in self._temporal_model_events
                if any(ent_id in e.involved_entities for ent_id in entity_ids_query)
            ]
            return {"success": True, "data": result}

        self._log_message(f"Query: Unsupported query type '{query_type}' or missing params.")
        return {"success": False, "error": f"Unsupported query_type '{query_type}' or missing parameters"}

    # --- Helper methods for prediction ---
    def _calculate_distance(self, pos1: List[float], pos2: List[float]) -> float:
        if len(pos1) != 3 or len(pos2) != 3:
            # self._log_message("Warning: _calculate_distance received invalid position format.") # Too noisy for common use
            return float('inf')
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2 + (pos1[2] - pos2[2])**2)

    def _linear_interpolate(self, pos1: List[float], pos2: List[float], fraction: float) -> List[float]:
        if len(pos1) != 3 or len(pos2) != 3:
            # self._log_message("Warning: _linear_interpolate received invalid position format.") # Too noisy
            return pos1 # Return start position if inputs are bad
        return [
            pos1[0] + (pos2[0] - pos1[0]) * fraction,
            pos1[1] + (pos2[1] - pos1[1]) * fraction,
            pos1[2] + (pos2[2] - pos1[2]) * fraction,
        ]

    def _vector_magnitude(self, vec: List[float]) -> float:
        if len(vec) != 3:
            # self._log_message("Warning: _vector_magnitude received invalid vector format.") # Too noisy
            return 0.0
        return math.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2)

    def predict_future_state(self, entity_id: str, time_horizon: float) -> Dict[str, Any]:
        self._log_message(f"Predicting future state for entity '{entity_id}' (Horizon: {time_horizon}s).")
        entity = self.get_entity_representation(entity_id)

        if not entity:
            self._log_message(f"Prediction failed: Entity '{entity_id}' not found.")
            # Adhere to the return type specification even for failure
            return {
                "predicted_entity_state_dict": {},
                "prediction_confidence": 0.0,
                "prediction_rule_applied": "entity_not_found"
            }

        # Use deepcopy to ensure original entity is not modified
        predicted_entity_dict = copy.deepcopy(entity.to_dict())
        # Ensure 'state' and 'properties' are dicts, even if empty in original
        if not isinstance(predicted_entity_dict.get("state"), dict):
            predicted_entity_dict["state"] = {}
        if not isinstance(predicted_entity_dict.get("properties"), dict):
            predicted_entity_dict["properties"] = {}

        current_confidence: float = 0.1 # Default: very_low
        current_rule_applied: str = "no_specific_rule_applied_current_state_assumed"

        # Rule 3: Static Entities (checked first as it's often a quick exit)
        self._log_message(f"[{entity_id}] Evaluating Rule 3 (Static Entities)...")
        STATIC_ENTITY_TYPES = ["building", "terrain_feature", "fixed_equipment", "location_marker"]
        is_static_prop = predicted_entity_dict.get("properties", {}).get("is_static") is True
        is_static_type = predicted_entity_dict.get("type") in STATIC_ENTITY_TYPES

        if is_static_prop or is_static_type:
            rule_reason = "is_static_prop" if is_static_prop else "is_static_type"
            self._log_message(f"[{entity_id}] Rule 3 applies ({rule_reason}). Entity type: {predicted_entity_dict.get('type')}.")
            current_rule_applied = "static_entity_no_change"
            current_confidence = 0.9 # High confidence in no change

            # Conceptual: check for instability
            damage_level = predicted_entity_dict.get("state", {}).get("damage_level", 0.0)
            if damage_level > 0.8:
                current_confidence = 0.3 # Low confidence (unstable)
                current_rule_applied = "static_entity_unstable"
                self._log_message(f"[{entity_id}] Static entity has high damage ({damage_level}), reducing confidence.")
            # No changes to predicted_entity_dict['state'] needed for position/location_id

        else: # Not static, proceed to other rules
            self._log_message(f"[{entity_id}] Rule 3 does not apply (Type: {predicted_entity_dict.get('type')}, is_static: {predicted_entity_dict.get('properties', {}).get('is_static')}).")

            # Rule 1: Mobile entity with a goal
            self._log_message(f"[{entity_id}] Evaluating Rule 1 (Mobile Entity with Goal)...")
            entity_state = predicted_entity_dict.get("state", {})
            current_action = entity_state.get("current_action")
            movement_speed = entity_state.get("movement_speed") # e.g., units per second
            goal_location_id = entity_state.get("goal_location_id")
            current_position = entity_state.get("position") # Assume [x,y,z]

            if current_action == "moving_to_goal" and movement_speed is not None and goal_location_id and isinstance(current_position, list) and len(current_position) == 3:
                self._log_message(f"[{entity_id}] Rule 1 conditions met: action='moving_to_goal', speed={movement_speed}, goal='{goal_location_id}', pos={current_position}.")

                goal_pos: Optional[List[float]] = None
                goal_entity = self._entity_repository.get(goal_location_id)
                if goal_entity and isinstance(goal_entity.state.get("position"), list) and len(goal_entity.state.get("position")) == 3:
                    goal_pos = goal_entity.state.get("position")
                    self._log_message(f"[{entity_id}] Goal '{goal_location_id}' is an entity, using its position: {goal_pos}.")
                elif goal_location_id in self._spatial_model and self._spatial_model[goal_location_id].coordinates:
                    goal_pos = list(self._spatial_model[goal_location_id].coordinates) # Ensure it's a list of floats
                    self._log_message(f"[{entity_id}] Goal '{goal_location_id}' is a spatial location, using its coords: {goal_pos}.")
                else:
                    self._log_message(f"[{entity_id}] Goal position for '{goal_location_id}' not found or invalid.")

                if goal_pos:
                    # Check for obstacles in relationships
                    is_blocked = False
                    if isinstance(predicted_entity_dict.get("relationships"), dict):
                        for rel_type, targets in predicted_entity_dict["relationships"].items():
                            if rel_type == "obstructs_path_to" and isinstance(targets, list): # Assuming specific format
                                for target_info in targets:
                                    if isinstance(target_info, dict) and target_info.get("target_id") == goal_location_id:
                                        obstacle_id = target_info.get("obstacle_id", "unknown_obstacle")
                                        self._log_message(f"[{entity_id}] Path to '{goal_location_id}' is blocked by '{obstacle_id}'.")
                                        is_blocked = True
                                        break
                            if is_blocked: break

                    if is_blocked:
                        predicted_entity_dict["state"]["current_action"] = "blocked"
                        # Position might change slightly if already moving, but for simplicity, assume no significant change here.
                        current_confidence = 0.7 # Confident about blockage
                        current_rule_applied = "mobile_entity_goal_blocked"
                        self._log_message(f"[{entity_id}] Prediction: Blocked. Action set to 'blocked'. Confidence: {current_confidence}.")
                    else:
                        distance_to_goal = self._calculate_distance(current_position, goal_pos)
                        travelable_distance = float(movement_speed) * time_horizon
                        self._log_message(f"[{entity_id}] Dist to goal: {distance_to_goal:.2f}, Travelable: {travelable_distance:.2f}.")

                        if travelable_distance >= distance_to_goal:
                            predicted_entity_dict["state"]["position"] = goal_pos
                            predicted_entity_dict["location_id"] = goal_location_id # Update symbolic location too
                            predicted_entity_dict["state"]["current_action"] = "at_goal" # Or "idle"
                            current_confidence = 0.6 # Medium-high confidence
                            current_rule_applied = "mobile_entity_reaches_goal"
                            self._log_message(f"[{entity_id}] Prediction: Reaches goal '{goal_location_id}'. Pos: {goal_pos}. Action: 'at_goal'. Confidence: {current_confidence}.")
                        else:
                            fraction_moved = travelable_distance / distance_to_goal if distance_to_goal > 0 else 0
                            new_pos = self._linear_interpolate(current_position, goal_pos, fraction_moved)
                            predicted_entity_dict["state"]["position"] = new_pos
                            # current_action remains "moving_to_goal"
                            current_confidence = 0.4 # Low-medium confidence
                            current_rule_applied = "mobile_entity_moves_towards_goal"
                            self._log_message(f"[{entity_id}] Prediction: Moves towards goal. New Pos: {new_pos}. Action remains 'moving_to_goal'. Confidence: {current_confidence}.")
                else: # No valid goal_pos
                    self._log_message(f"[{entity_id}] Rule 1 cannot apply: goal_pos for '{goal_location_id}' not determined.")
            else: # Rule 1 conditions not met
                self._log_message(f"[{entity_id}] Rule 1 conditions not met (Action: {current_action}, Speed: {movement_speed}, GoalID: {goal_location_id}, Pos: {current_position}).")


            # Rule 2: Basic physics (constant velocity) - apply if Rule 1 didn't apply or had low confidence
            rule1_low_confidence = current_rule_applied.startswith("mobile_entity_moves_towards_goal") # 0.4
            if current_rule_applied == "no_specific_rule_applied_current_state_assumed" or rule1_low_confidence:
                self._log_message(f"[{entity_id}] Evaluating Rule 2 (Constant Velocity Physics)... Current rule: {current_rule_applied}, Current Conf: {current_confidence}")
                velocity = entity_state.get("velocity") # [vx,vy,vz]
                # current_position is already fetched

                if isinstance(velocity, list) and len(velocity) == 3 and \
                   isinstance(current_position, list) and len(current_position) == 3:
                    self._log_message(f"[{entity_id}] Rule 2 conditions met: velocity={velocity}, position={current_position}.")

                    new_px = current_position[0] + velocity[0] * time_horizon
                    new_py = current_position[1] + velocity[1] * time_horizon
                    new_pz = current_position[2] + velocity[2] * time_horizon
                    predicted_entity_dict["state"]["position"] = [new_px, new_py, new_pz]

                    current_confidence = 0.5 # Medium confidence default for this rule
                    current_rule_applied = "physics_constant_velocity"

                    max_speed = predicted_entity_dict.get("properties", {}).get("max_speed")
                    if max_speed is not None:
                        speed_magnitude = self._vector_magnitude(velocity)
                        if speed_magnitude > float(max_speed):
                            self._log_message(f"[{entity_id}] Warning: Entity velocity magnitude {speed_magnitude:.2f} exceeds max_speed {max_speed:.2f}.")
                            current_confidence = 0.3 # Lower confidence due to exceeding max_speed
                            current_rule_applied = "physics_exceeds_max_speed"

                    self._log_message(f"[{entity_id}] Prediction: New position by velocity {predicted_entity_dict['state']['position']}. Confidence: {current_confidence}.")
                else: # Rule 2 conditions not met
                    self._log_message(f"[{entity_id}] Rule 2 conditions not met (Velocity: {velocity}, Position: {current_position}).")

        # Final packaging of the result
        return {
            "predicted_entity_state_dict": predicted_entity_dict,
            "prediction_confidence": current_confidence,
            "prediction_rule_applied": current_rule_applied
        }

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

        print("\n--- Testing Enhanced Queries ---")
        # Query entities by type 'fruit'
        query_fruit = world_model.query_world_state({"query_type": "entities_by_type", "entity_type": "fruit"})
        assert query_fruit["success"] and len(query_fruit["data"]) == 1 and query_fruit["data"][0]["id"] == "RedApple"
        print(f"  Query entities by type 'fruit': {len(query_fruit['data'])} found.")

        # Query entities by location 'loc_tabletop'
        query_loc_tabletop = world_model.query_world_state({"query_type": "entities_by_location", "location_id": "loc_tabletop"})
        assert query_loc_tabletop["success"] and len(query_loc_tabletop["data"]) == 1 and query_loc_tabletop["data"][0]["id"] == "box01"
        print(f"  Query entities by location 'loc_tabletop': {len(query_loc_tabletop['data'])} found.")

        # Query events by type 'action_outcome_MOVE_AGENT'
        query_move_events = world_model.query_world_state({"query_type": "events_by_type", "event_type": "action_outcome_MOVE_AGENT"})
        assert query_move_events["success"] and len(query_move_events["data"]) == 1 and query_move_events["data"][0]["involved_entities"][0] == "RedApple"
        print(f"  Query events by type 'action_outcome_MOVE_AGENT': {len(query_move_events['data'])} found.")

        # Query events involving 'RedApple' OR 'box01'
        query_involved_entities = world_model.query_world_state({"query_type": "events_by_involved_entities", "entity_ids": ["RedApple", "box01"]})
        assert query_involved_entities["success"] and len(query_involved_entities["data"]) == 2 # Both events should match
        print(f"  Query events by involved entities ['RedApple', 'box01']: {len(query_involved_entities['data'])} found.")

        # Query for a non-existent entity
        query_non_existent = world_model.query_world_state({"query_type": "entity_state", "entity_id": "ghost01"})
        assert not query_non_existent["success"]
        print(f"  Query for non-existent entity 'ghost01': Success={query_non_existent['success']}.")

        print("\n--- Testing Prediction ---")
        # Add position and velocity to RedApple for prediction
        world_model.update_entity_state("RedApple", {"state": {"position": [10, 5, 0], "velocity": [1, 0, 0]}})
        predicted_state_apple = world_model.predict_future_state("RedApple", time_horizon=5.0)
        # Expected: Rule 2 (physics_constant_velocity), Confidence 0.5
        assert predicted_state_apple is not None
        assert predicted_state_apple["prediction_rule_applied"] == "physics_constant_velocity", f"Apple rule: {predicted_state_apple['prediction_rule_applied']}"
        assert predicted_state_apple["prediction_confidence"] == 0.5, f"Apple confidence: {predicted_state_apple['prediction_confidence']}"
        assert predicted_state_apple["predicted_entity_state_dict"]["state"]["position"] == [15, 5, 0]
        print(f"  Predicted state for RedApple (with velocity): {predicted_state_apple['predicted_entity_state_dict']['state']['position']}, Rule: {predicted_state_apple['prediction_rule_applied']}, Confidence: {predicted_state_apple['prediction_confidence']}")

        # Predict for an entity without velocity (should return current with default low confidence)
        predicted_state_box = world_model.predict_future_state("box01", time_horizon=5.0)
        assert predicted_state_box is not None
        assert predicted_state_box["prediction_rule_applied"] == "no_specific_rule_applied_current_state_assumed"
        assert predicted_state_box["prediction_confidence"] == 0.1 # Default very_low
        assert predicted_state_box["predicted_entity_state_dict"]["state"].get("position") is None # No position initially
        print(f"  Predicted state for box01 (no vel/goal): Rule: {predicted_state_box['prediction_rule_applied']}, Confidence: {predicted_state_box['prediction_confidence']}")

        # Predict for non-existent entity
        predicted_non_existent = world_model.predict_future_state("ghost02", time_horizon=5.0)
        assert predicted_non_existent is not None # Now returns a dict
        assert predicted_non_existent["prediction_rule_applied"] == "entity_not_found"
        assert predicted_non_existent["prediction_confidence"] == 0.0
        assert not predicted_non_existent["predicted_entity_state_dict"] # Empty dict
        print(f"  Attempted prediction for non-existent 'ghost02': Rule: {predicted_non_existent['prediction_rule_applied']}.")

        # Test Static Entity Rule
        world_model.update_entity_state("TableTop", {"properties": {"is_static": True}})
        predicted_table = world_model.predict_future_state("TableTop", time_horizon=10.0)
        assert predicted_table["prediction_rule_applied"] == "static_entity_no_change"
        assert predicted_table["prediction_confidence"] == 0.9
        print(f"  Predicted state for TableTop (static): Rule: {predicted_table['prediction_rule_applied']}, Confidence: {predicted_table['prediction_confidence']}")

        world_model.update_entity_state("TableTop", {"state": {"damage_level": 0.9}})
        predicted_table_damaged = world_model.predict_future_state("TableTop", time_horizon=10.0)
        assert predicted_table_damaged["prediction_rule_applied"] == "static_entity_unstable"
        assert predicted_table_damaged["prediction_confidence"] == 0.3
        print(f"  Predicted state for TableTop (static, damaged): Rule: {predicted_table_damaged['prediction_rule_applied']}, Confidence: {predicted_table_damaged['prediction_confidence']}")
        # Reset damage for other tests
        world_model.update_entity_state("TableTop", {"state": {"damage_level": 0.0}})


        # Test Mobile Entity with Goal Rule
        # Create a goal location entity
        goal_loc_entity_id = "GoalSpot"
        world_model._entity_repository[goal_loc_entity_id] = WorldEntity(
            id=goal_loc_entity_id, type="location_marker",
            state={"position": [100, 100, 0]}, properties={}, affordances=[], relationships={}
        )

        # Update RedApple to move to goal
        world_model.update_entity_state("RedApple", {
            "state": {
                "current_action": "moving_to_goal",
                "goal_location_id": goal_loc_entity_id,
                "movement_speed": 10.0, # units/sec
                "position": [15, 5, 0] # Current position after previous prediction
            }
        })
        # Predict RedApple reaches goal
        dist_apple_to_goal = math.sqrt((100-15)**2 + (100-5)**2 + (0-0)**2) # approx 127.7
        time_to_reach = dist_apple_to_goal / 10.0 # approx 12.77s

        predicted_apple_reaches_goal = world_model.predict_future_state("RedApple", time_horizon=15.0) # Should reach
        assert predicted_apple_reaches_goal["prediction_rule_applied"] == "mobile_entity_reaches_goal", f"Apple goal rule: {predicted_apple_reaches_goal['prediction_rule_applied']}"
        assert predicted_apple_reaches_goal["prediction_confidence"] == 0.6
        assert predicted_apple_reaches_goal["predicted_entity_state_dict"]["state"]["position"] == [100,100,0]
        assert predicted_apple_reaches_goal["predicted_entity_state_dict"]["state"]["current_action"] == "at_goal"
        print(f"  Predicted RedApple reaches goal: Pos={predicted_apple_reaches_goal['predicted_entity_state_dict']['state']['position']}, Rule: {predicted_apple_reaches_goal['prediction_rule_applied']}")

        # Predict RedApple moves towards goal
        predicted_apple_towards_goal = world_model.predict_future_state("RedApple", time_horizon=5.0) # Should move towards
        assert predicted_apple_towards_goal["prediction_rule_applied"] == "mobile_entity_moves_towards_goal", f"Apple towards rule: {predicted_apple_towards_goal['prediction_rule_applied']}"
        assert predicted_apple_towards_goal["prediction_confidence"] == 0.4
        # Check if position changed from [15,5,0] towards [100,100,0]
        assert predicted_apple_towards_goal["predicted_entity_state_dict"]["state"]["position"] != [15,5,0]
        print(f"  Predicted RedApple moves towards goal: NewPos={predicted_apple_towards_goal['predicted_entity_state_dict']['state']['position']}, Rule: {predicted_apple_towards_goal['prediction_rule_applied']}")

        # Test blocked path
        # Add an obstacle relationship for RedApple
        world_model._entity_repository["RedApple"].relationships["obstructs_path_to"] = [
            {"type": "obstructs_path_to", "target_id": goal_loc_entity_id, "obstacle_id": "some_rock"}
        ]
        predicted_apple_blocked = world_model.predict_future_state("RedApple", time_horizon=5.0)
        assert predicted_apple_blocked["prediction_rule_applied"] == "mobile_entity_goal_blocked"
        assert predicted_apple_blocked["prediction_confidence"] == 0.7
        assert predicted_apple_blocked["predicted_entity_state_dict"]["state"]["current_action"] == "blocked"
        print(f"  Predicted RedApple blocked: Action={predicted_apple_blocked['predicted_entity_state_dict']['state']['current_action']}, Rule: {predicted_apple_blocked['prediction_rule_applied']}")
        # Clear relationship for next tests
        world_model._entity_repository["RedApple"].relationships = {}


        print("\n--- Final World Model Status ---")
        final_status = world_model.get_world_model_status()
        print(final_status)
        # Counts remain same, just testing query and prediction logic
        assert final_status["entity_count"] == 4
        assert final_status["event_count"] == 2
        assert final_status["handled_message_counts"]["PerceptData"] == 1
        assert final_status["handled_message_counts"]["LTMQueryResult"] == 1
        assert final_status["handled_message_counts"]["ActionEvent"] == 2


        print("\n--- ConcreteWorldModel __main__ Test Complete ---")

    try:
        # Ensure datetime is available for PerceptDataPayload's source_timestamp
        import datetime # Moved import here to be within async context if needed by older pythons with asyncio issues
        asyncio.run(main_test_flow())
    except RuntimeError as e:
        if " asyncio.run() cannot be called from a running event loop" in str(e):
            print("Skipping asyncio.run() as an event loop is already running.")
        else:
            raise
