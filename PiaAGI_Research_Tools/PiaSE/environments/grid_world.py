import time
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass, field

# Assuming core_engine is one level up from environments directory
from ..core_engine.interfaces import Environment, PerceptionData, ActionCommand, ActionResult

@dataclass
class GridObject:
    name: str
    position: Tuple[int, int]
    properties: Dict[str, Any] = field(default_factory=dict) # e.g., {"can_be_taken": True, "value": 10}

class GridWorld(Environment):
    def __init__(self,
                 width: int,
                 height: int,
                 agent_start_pos: Optional[Tuple[int, int]] = None, # For the default agent
                 goal_position: Optional[Tuple[int, int]] = None,
                 walls: Optional[List[Tuple[int, int]]] = None,
                 static_objects: Optional[List[GridObject]] = None,
                 dynamic_objects: Optional[List[GridObject]] = None, # For future use
                 default_agent_id: str = "agent_0",
                 reward_goal: float = 10.0,
                 reward_move: float = -0.1,
                 reward_hit_wall: float = -1.0,
                 reward_stay: float = -0.05): # Added reward_stay

        if width <= 0 or height <= 0:
            raise ValueError("Grid width and height must be positive integers.")
        self.width = width
        self.height = height
        
        self.default_agent_id = default_agent_id
        self.initial_agent_start_pos = agent_start_pos if agent_start_pos is not None else (0, 0)

        if not self._is_valid_position(self.initial_agent_start_pos[0], self.initial_agent_start_pos[1]):
            print(f"Warning: Default agent start position {self.initial_agent_start_pos} is outside grid. Defaulting to (0,0).")
            self.initial_agent_start_pos = (0,0)

        self.goal_position = goal_position if goal_position is not None else (width - 1, height - 1)
        if not self._is_valid_position(self.goal_position[0], self.goal_position[1]):
            print(f"Warning: Goal position {self.goal_position} is outside grid. Defaulting to ({width-1},{height-1}).")
            self.goal_position = (width - 1, height - 1)

        self.walls: List[Tuple[int, int]] = []
        if walls:
            for x, y in walls:
                if self._is_valid_position(x, y):
                    if (x,y) == self.initial_agent_start_pos:
                        print(f"Warning: Wall at {x},{y} conflicts with agent start position. Agent may start on a wall.")
                    if (x,y) == self.goal_position:
                        print(f"Warning: Wall at {x},{y} conflicts with goal position. Goal may be unreachable.")
                    self.walls.append((x,y))
                else:
                    print(f"Warning: Wall coordinate ({x},{y}) is outside grid boundaries. Ignoring.")
        
        self.static_objects: List[GridObject] = copy.deepcopy(static_objects) if static_objects else []
        self.dynamic_objects: List[GridObject] = copy.deepcopy(dynamic_objects) if dynamic_objects else []

        self.agent_positions: Dict[str, Tuple[int, int]] = {}
        
        # Reward configuration
        self.reward_goal = reward_goal
        self.reward_move = reward_move
        self.reward_hit_wall = reward_hit_wall
        self.reward_stay = reward_stay # Store this

        self.valid_actions = ["up", "down", "left", "right", "stay"] # Added "stay"

        self.reset() # Initialize agent position and grid

    def _is_valid_position(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def _is_wall(self, x: int, y: int) -> bool:
        return (x, y) in self.walls

    def _is_obstacle(self, x: int, y: int) -> bool: # Considers walls and static objects that block movement
        if self._is_wall(x,y):
            return True
        for obj in self.static_objects + self.dynamic_objects:
            if obj.position == (x,y) and obj.properties.get("blocks_movement", False): # Assuming a property
                return True
        return False

    def reset(self) -> PerceptionData:
        # For now, reset places/resets the default agent. Multi-agent scenarios might need more.
        self.agent_positions = {} # Clear all agent positions
        
        start_pos_to_set = self.initial_agent_start_pos
        if self._is_obstacle(start_pos_to_set[0], start_pos_to_set[1]):
             print(f"Warning: Initial start position {start_pos_to_set} for default agent is an obstacle. Finding fallback.")
             # Basic fallback: find first non-obstacle cell
             found_fallback = False
             for r in range(self.height):
                 for c in range(self.width):
                     if not self._is_obstacle(c,r):
                         start_pos_to_set = (c,r)
                         found_fallback = True
                         break
                 if found_fallback: break
             if not found_fallback:
                 raise Exception("GridWorld Reset: No valid non-obstacle cell available to place the agent.")
        
        self.agent_positions[self.default_agent_id] = start_pos_to_set
        # print(f"GridWorld reset. Agent '{self.default_agent_id}' at {self.agent_positions[self.default_agent_id]}.")
        return self.get_observation(self.default_agent_id)

    def get_observation(self, agent_id: str) -> PerceptionData:
        if agent_id not in self.agent_positions:
            # If an agent_id is requested that was not the default_agent_id placed during reset,
            # we need a policy. For now, error or place at default if it's the default_agent_id.
            if agent_id == self.default_agent_id:
                 print(f"Warning: Default agent {agent_id} not in agent_positions during get_observation. Resetting position.")
                 self.agent_positions[agent_id] = self.initial_agent_start_pos # Attempt to recover
                 if self._is_obstacle(self.initial_agent_start_pos[0], self.initial_agent_start_pos[1]):
                     # Simplified fallback for this edge case, real one in reset is better
                     self.agent_positions[agent_id] = next(((c,r) for r in range(self.height) for c in range(self.width) if not self._is_obstacle(c,r)), (0,0) )

            else: # Truly unknown agent for this simple GridWorld that mostly manages one agent
                return PerceptionData(
                    timestamp=time.time(),
                    sensor_data={"error": f"Agent {agent_id} not found or initialized in this GridWorld."},
                    messages=[{"sender": "system", "content": f"Agent {agent_id} position unknown."}]
                )

        agent_pos = self.agent_positions[agent_id]
        
        # Basic grid view (e.g. local N*N patch or full grid)
        # For simplicity, let's provide a "local_view" and the full grid for now.
        # A true local_view would be more complex.
        grid_representation = [[0]*self.width for _ in range(self.height)]
        for r in range(self.height):
            for c in range(self.width):
                if self._is_wall(c,r):
                    grid_representation[r][c] = 1 # Wall
                # Could add numbers for objects if desired
                
        objs_on_tile_data = []
        for obj in self.static_objects + self.dynamic_objects:
            if obj.position == agent_pos:
                # Using dict() for properties if it's already a dict, or vars() if it's an object
                props = obj.properties if isinstance(obj.properties, dict) else vars(obj.properties)
                objs_on_tile_data.append({"name": obj.name, "properties": copy.deepcopy(props)})

        observation_dict = {
            "agent_position": agent_pos,
            "grid_view_full": grid_representation, # Example: full grid
            "objects_on_tile": objs_on_tile_data,
            "goal_position": self.goal_position
        }
        
        return PerceptionData(timestamp=time.time(), sensor_data=observation_dict)

    def get_action_space(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        return {action: {"parameters": {}} for action in self.valid_actions}

    def step(self, agent_id: str, action: ActionCommand) -> ActionResult:
        if agent_id not in self.agent_positions:
            # This should ideally not happen if agents are managed by the engine correctly
            message = f"Agent {agent_id} not found. Cannot perform action."
            return ActionResult(timestamp=time.time(), status="failure", message=message)

        current_x, current_y = self.agent_positions[agent_id]
        new_x, new_y = current_x, current_y
        action_name = action.action_type.lower() # Ensure lowercase for matching

        moved = False
        if action_name == "up": # Assuming 'up' corresponds to 'N' (decreasing y)
            new_y -= 1; moved = True
        elif action_name == "down": # Assuming 'down' corresponds to 'S' (increasing y)
            new_y += 1; moved = True
        elif action_name == "left": # Assuming 'left' corresponds to 'W' (decreasing x)
            new_x -= 1; moved = True
        elif action_name == "right": # Assuming 'right' corresponds to 'E' (increasing x)
            new_x += 1; moved = True
        elif action_name == "stay":
            pass # Position remains the same, moved = False
        else:
            message = f"Unknown action '{action_name}'. Agent stays."
            new_perception_snippet = self.get_observation(agent_id)
            return ActionResult(timestamp=time.time(), status="failure", message=message, new_perception_snippet=new_perception_snippet, details={"reward": self.reward_hit_wall, "is_terminal": False})

        reward = 0.0
        done = False
        status = "success"
        message = f"Action {action_name} executed."

        if moved:
            if self._is_valid_position(new_x, new_y) and not self._is_obstacle(new_x, new_y):
                self.agent_positions[agent_id] = (new_x, new_y)
                reward = self.reward_move
                if self.agent_positions[agent_id] == self.goal_position:
                    reward = self.reward_goal
                    done = True
                    message = f"Agent {agent_id} reached the goal at {self.goal_position}!"
            else: # Hit wall or obstacle
                reward = self.reward_hit_wall
                status = "failure" # Or success with penalty, depending on philosophy
                message = f"Agent {agent_id} hit an obstacle trying to move {action_name} to ({new_x},{new_y})."
        else: # Action was "stay"
            reward = self.reward_stay
            if self.agent_positions[agent_id] == self.goal_position: # Staying at goal
                reward = self.reward_goal # Or a smaller positive reward for staying at goal
                done = True # If goal is terminal
                message = f"Agent {agent_id} is at the goal."


        new_perception_snippet = self.get_observation(agent_id)
        
        return ActionResult(
            timestamp=time.time(),
            status=status,
            message=message,
            new_perception_snippet=new_perception_snippet,
            details={"reward": reward, "is_terminal": done}
        )

    def get_state(self) -> Dict[str, Any]:
        return {
            "grid_dimensions": (self.width, self.height),
            "walls": list(self.walls),
            "static_objects": [vars(obj) for obj in self.static_objects], # Convert GridObjects to dicts
            "dynamic_objects": [vars(obj) for obj in self.dynamic_objects],
            "agent_positions": dict(self.agent_positions),
            "goal_position": self.goal_position
        }

    def is_done(self, agent_id: str) -> bool:
        # This method is called by the engine to check if a specific agent is done.
        # The 'done' flag in ActionResult from step() is often the primary source for this.
        agent_pos = self.agent_positions.get(agent_id)
        if agent_pos and agent_pos == self.goal_position:
            return True
        return False

    def get_environment_info(self) -> Dict[str, Any]:
        return {
            "environment_name": "GridWorld_v1.1",
            "description": "A configurable grid-based environment for navigation.",
            "action_schema": self.get_action_space(), # Uses the new format
            "perception_schema": {
                "agent_position": {"type": "tuple", "item_type": "int"},
                "grid_view_full": {"type": "list", "item_schema": {"type": "list", "item_type": "int"}},
                "objects_on_tile": {"type": "list", "item_schema": {"type": "dict", "keys": {"name": "string", "properties": "dict"}}},
                "goal_position": {"type": "tuple", "item_type": "int"}
            },
            "reward_range": (self.reward_hit_wall, self.reward_goal) # Approx range
        }

    def add_agent(self, agent_id: str, start_position: Tuple[int, int], make_default: bool = False):
        """Adds an agent to the environment. If make_default, sets this agent as the default one."""
        if not self._is_valid_position(start_position[0], start_position[1]) or self._is_obstacle(start_position[0], start_position[1]):
            raise ValueError(f"Cannot add agent {agent_id} at invalid or obstacle position {start_position}.")
        self.agent_positions[agent_id] = start_position
        if make_default:
            self.default_agent_id = agent_id
            self.initial_agent_start_pos = start_position
        print(f"Agent {agent_id} added at {start_position}.")

    def add_object(self, grid_object: GridObject, is_static: bool = True):
        """Adds a static or dynamic object to the environment."""
        if not self._is_valid_position(grid_object.position[0], grid_object.position[1]):
            print(f"Warning: Object {grid_object.name} position {grid_object.position} is invalid. Not adding.")
            return
        if self._is_obstacle(grid_object.position[0], grid_object.position[1]):
             print(f"Warning: Position {grid_object.position} for object {grid_object.name} is already an obstacle. Overlapping or check logic.")

        if is_static:
            self.static_objects.append(grid_object)
        else:
            self.dynamic_objects.append(grid_object)

    def reconfigure(self, config: Dict[str, Any]) -> bool:
        """
        Reconfigures the GridWorld environment based on the provided configuration.
        """
        print(f"GridWorld: Attempting reconfiguration with: {list(config.keys())}")
        reconfigured_something = False

        if "width" in config and config["width"] != self.width:
            print(f"GridWorld Warning: 'width' reconfirguration ({config['width']}) post-init is not supported. Current width: {self.width}.")
        if "height" in config and config["height"] != self.height:
            print(f"GridWorld Warning: 'height' reconfiguration ({config['height']}) post-init is not supported. Current height: {self.height}.")

        if "goal_position" in config:
            new_goal = tuple(config["goal_position"])
            if self._is_valid_position(new_goal[0], new_goal[1]):
                self.goal_position = new_goal
                print(f"  Reconfigured goal_position to: {self.goal_position}")
                reconfigured_something = True
            else:
                print(f"  GridWorld Warning: Invalid new goal_position {new_goal} provided in reconfigure. Retaining old: {self.goal_position}")

        if "walls" in config:
            self.walls = [] # Replace existing walls
            new_walls = config["walls"]
            if isinstance(new_walls, list):
                for x, y in new_walls:
                    if self._is_valid_position(x, y):
                        self.walls.append(tuple(map(int,(x,y)))) # ensure tuple of ints
                    else:
                        print(f"  GridWorld Warning: Invalid wall coordinate ({x},{y}) in reconfigure. Ignoring.")
                print(f"  Reconfigured walls. New wall count: {len(self.walls)}")
                reconfigured_something = True
            else:
                print(f"  GridWorld Warning: 'walls' in reconfigure must be a list of tuples. Not applied.")

        if "static_objects" in config:
            new_static_objects_data = config["static_objects"]
            if isinstance(new_static_objects_data, list):
                self.static_objects = [] # Replace existing
                for obj_data in new_static_objects_data:
                    if isinstance(obj_data, dict) and "name" in obj_data and "position" in obj_data:
                         # Assuming GridObject can be created from dict like this
                        pos = tuple(map(int,obj_data["position"]))
                        if self._is_valid_position(pos[0], pos[1]):
                            self.static_objects.append(GridObject(name=obj_data["name"], position=pos, properties=obj_data.get("properties", {})))
                        else:
                            print(f"  GridWorld Warning: Invalid position {pos} for static object '{obj_data['name']}'. Not adding.")
                    elif isinstance(obj_data, GridObject): # If already GridObject instances
                        if self._is_valid_position(obj_data.position[0], obj_data.position[1]):
                            self.static_objects.append(copy.deepcopy(obj_data))
                        else:
                             print(f"  GridWorld Warning: Invalid position {obj_data.position} for static object '{obj_data.name}'. Not adding.")
                    else:
                        print(f"  GridWorld Warning: Invalid data format for static object in reconfigure. Skipping item: {obj_data}")
                print(f"  Reconfigured static_objects. New count: {len(self.static_objects)}")
                reconfigured_something = True
            else:
                 print(f"  GridWorld Warning: 'static_objects' in reconfigure must be a list. Not applied.")


        if "dynamic_objects" in config: # Similar handling as static_objects
            new_dynamic_objects_data = config["dynamic_objects"]
            if isinstance(new_dynamic_objects_data, list):
                self.dynamic_objects = [] # Replace existing
                for obj_data in new_dynamic_objects_data:
                    if isinstance(obj_data, dict) and "name" in obj_data and "position" in obj_data:
                        pos = tuple(map(int,obj_data["position"]))
                        if self._is_valid_position(pos[0], pos[1]):
                            self.dynamic_objects.append(GridObject(name=obj_data["name"], position=pos, properties=obj_data.get("properties", {})))
                        else:
                            print(f"  GridWorld Warning: Invalid position {pos} for dynamic object '{obj_data['name']}'. Not adding.")
                    elif isinstance(obj_data, GridObject):
                        if self._is_valid_position(obj_data.position[0], obj_data.position[1]):
                            self.dynamic_objects.append(copy.deepcopy(obj_data))
                        else:
                            print(f"  GridWorld Warning: Invalid position {obj_data.position} for dynamic object '{obj_data.name}'. Not adding.")
                    else:
                        print(f"  GridWorld Warning: Invalid data format for dynamic object in reconfigure. Skipping item: {obj_data}")

                print(f"  Reconfigured dynamic_objects. New count: {len(self.dynamic_objects)}")
                reconfigured_something = True
            else:
                print(f"  GridWorld Warning: 'dynamic_objects' in reconfigure must be a list. Not applied.")


        if "initial_agent_start_pos" in config:
            new_start_pos = tuple(config["initial_agent_start_pos"])
            # Basic validation, more robust check happens in reset()
            if isinstance(new_start_pos, tuple) and len(new_start_pos) == 2 and \
               all(isinstance(coord, int) for coord in new_start_pos) and \
               self._is_valid_position(new_start_pos[0], new_start_pos[1]):
                self.initial_agent_start_pos = new_start_pos
                print(f"  Reconfigured initial_agent_start_pos to: {self.initial_agent_start_pos}")
                reconfigured_something = True
            else:
                print(f"  GridWorld Warning: Invalid initial_agent_start_pos {new_start_pos} in reconfigure. Retaining old: {self.initial_agent_start_pos}")


        rewards_to_update = {
            "reward_goal": float, "reward_move": float,
            "reward_hit_wall": float, "reward_stay": float
        }
        for reward_key, reward_type in rewards_to_update.items():
            if reward_key in config:
                try:
                    setattr(self, reward_key, reward_type(config[reward_key]))
                    print(f"  Reconfigured {reward_key} to: {getattr(self, reward_key)}")
                    reconfigured_something = True
                except ValueError:
                    print(f"  GridWorld Warning: Invalid type for {reward_key} in reconfigure. Expected float. Value: {config[reward_key]}")

        if reconfigured_something:
            print("GridWorld: Calling reset() after reconfiguration.")
            self.reset()
        else:
            print("GridWorld: No applicable configuration changes found or applied.")

        return True # Indicate reconfiguration attempt was processed

# Need to import copy for deepcopy
import copy
```
