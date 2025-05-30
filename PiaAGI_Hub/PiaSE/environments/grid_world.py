from typing import List, Tuple, Dict, Optional, Any
from PiaAGI_Hub.PiaSE.core_engine.interfaces import Environment

class GridWorld(Environment):
    """
    A simple grid world environment for agents to navigate.
    The grid is represented by (x, y) coordinates, where (0,0) is the top-left.
    """

    def __init__(self,
                 width: int,
                 height: int,
                 walls: Optional[List[Tuple[int, int]]] = None,
                 agent_start_positions: Optional[Dict[str, Tuple[int, int]]] = None):
        if width <= 0 or height <= 0:
            raise ValueError("Grid width and height must be positive integers.")
        self.width = width
        self.height = height
        self.grid: List[List[int]] = [[0 for _ in range(width)] for _ in range(height)] # 0 for empty, 1 for wall

        self.walls: List[Tuple[int, int]] = []
        if walls:
            self._add_walls(walls)

        self.agent_positions: Dict[str, Tuple[int, int]] = {}
        self.agent_start_positions: Dict[str, Tuple[int, int]] = agent_start_positions if agent_start_positions is not None else {}
        
        # Initialize agents to their start positions or a default (0,0) if not specified
        # This part might be better handled by a separate agent registration in the engine
        # For now, we'll use it to ensure agents have a starting point if defined at construction
        for agent_id, pos in self.agent_start_positions.items():
            if self._is_valid_position(pos[0], pos[1]) and self.grid[pos[1]][pos[0]] == 0:
                self.agent_positions[agent_id] = pos
            else:
                print(f"Warning: Invalid start position {pos} for agent {agent_id}. Using default (0,0) or first available.")
                # Fallback to (0,0) or first valid non-wall position if (0,0) is a wall
                if self._is_valid_position(0,0) and self.grid[0][0] == 0:
                     self.agent_positions[agent_id] = (0,0)
                     self.agent_start_positions[agent_id] = (0,0) # Update start position too
                else:
                    # Find first available
                    found_fallback = False
                    for r in range(self.height):
                        for c in range(self.width):
                            if self.grid[r][c] == 0:
                                self.agent_positions[agent_id] = (c,r)
                                self.agent_start_positions[agent_id] = (c,r)
                                found_fallback = True
                                break
                        if found_fallback:
                            break
                    if not found_fallback:
                        raise Exception(f"Cannot place agent {agent_id}, no valid empty cells in the grid.")


        print(f"GridWorld initialized: {width}x{height}. Agents at: {self.agent_positions}")

    def _add_walls(self, walls: List[Tuple[int, int]]):
        for x, y in walls:
            if self._is_valid_position(x, y):
                self.grid[y][x] = 1 # 1 represents a wall
                self.walls.append((x,y))
            else:
                print(f"Warning: Wall coordinate ({x},{y}) is outside grid boundaries. Ignoring.")

    def _is_valid_position(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def reset(self, agent_id_to_reset: Optional[str] = None) -> Any:
        """
        Resets the environment.
        If agent_id_to_reset is provided, resets only that agent.
        Otherwise, resets all known agents to their starting positions.
        Returns the observation for the reset agent(s).
        """
        if agent_id_to_reset:
            if agent_id_to_reset in self.agent_start_positions:
                start_pos = self.agent_start_positions[agent_id_to_reset]
                if self._is_valid_position(start_pos[0], start_pos[1]) and self.grid[start_pos[1]][start_pos[0]] == 0:
                    self.agent_positions[agent_id_to_reset] = start_pos
                else:
                    # Fallback if start_pos is invalid (e.g. a wall was added later)
                    print(f"Warning: Start position {start_pos} for agent {agent_id_to_reset} is invalid. Using (0,0) or first valid.")
                    self.agent_positions[agent_id_to_reset] = (0,0) # Default, consider a safer fallback
                    # A safer fallback would be to find the first available non-wall cell
                    if self.grid[0][0] == 1: # if (0,0) is a wall
                        found = False
                        for r in range(self.height):
                            for c in range(self.width):
                                if self.grid[r][c] == 0:
                                    self.agent_positions[agent_id_to_reset] = (c,r)
                                    found = True
                                    break
                            if found: break
                        if not found: raise Exception(f"No valid cell for agent {agent_id_to_reset} to reset to.")
                print(f"GridWorld: Agent {agent_id_to_reset} reset to {self.agent_positions[agent_id_to_reset]}.")
                return self.get_observation(agent_id_to_reset)
            else:
                print(f"GridWorld: Warning - Cannot reset agent {agent_id_to_reset}, no start position defined.")
                return None # Or raise error
        else:
            # Reset all agents
            for agent_id in list(self.agent_positions.keys()): # Iterate over a copy of keys if modifying dict
                 start_pos = self.agent_start_positions.get(agent_id, (0,0)) # Default to (0,0) if not in start_positions
                 if self._is_valid_position(start_pos[0], start_pos[1]) and self.grid[start_pos[1]][start_pos[0]] == 0:
                    self.agent_positions[agent_id] = start_pos
                 else:
                    # Fallback logic as above
                    self.agent_positions[agent_id] = (0,0)
                    if self.grid[0][0] == 1:
                        found = False
                        for r in range(self.height):
                            for c in range(self.width):
                                if self.grid[r][c] == 0:
                                    self.agent_positions[agent_id] = (c,r)
                                    found = True
                                    break
                            if found: break
                        if not found: raise Exception(f"No valid cell for agent {agent_id} to reset to.")

            print(f"GridWorld: All agent positions reset. Current positions: {self.agent_positions}")
            # Return observation for the "first" agent if any, or overall state
            if self.agent_positions:
                first_agent_id = list(self.agent_positions.keys())[0]
                return self.get_observation(first_agent_id)
            return self.get_state()


    def step(self, agent_id: str, action: str) -> Tuple[Any, float]:
        """
        Processes an agent's action and updates the environment state.
        Action can be "N" (North), "S" (South), "E" (East), "W" (West), "Stay".
        Returns the new observation for the agent and a conceptual reward.
        """
        if agent_id not in self.agent_positions:
            raise ValueError(f"Agent {agent_id} not found in the environment.")

        current_x, current_y = self.agent_positions[agent_id]
        new_x, new_y = current_x, current_y

        if action == "N":
            new_y -= 1
        elif action == "S":
            new_y += 1
        elif action == "E":
            new_x += 1
        elif action == "W":
            new_x -= 1
        elif action == "Stay":
            pass # Position remains the same
        else:
            print(f"Warning: Unknown action '{action}' for agent {agent_id}. Agent stays.")

        # Check if the new position is valid and not a wall
        if self._is_valid_position(new_x, new_y) and self.grid[new_y][new_x] == 0:
            self.agent_positions[agent_id] = (new_x, new_y)
        else:
            # Agent hits a wall or boundary, stays in the current position
            # print(f"Agent {agent_id} tried to move to ({new_x},{new_y}), but it's a wall or boundary. Stays at ({current_x},{current_y}).")
            pass


        observation = self.get_observation(agent_id)
        reward = 0.0 # Conceptual reward, can be expanded later

        # print(f"GridWorld: Agent {agent_id} action '{action}'. New pos: {self.agent_positions[agent_id]}. Reward: {reward}")
        return observation, reward

    def get_observation(self, agent_id: str) -> Dict[str, Any]:
        """
        Gets the observation for a specific agent.
        Returns the agent's current position and the full grid state.
        """
        if agent_id not in self.agent_positions:
            # This case should ideally be handled by ensuring agent is registered/reset first.
            # If an agent is registered with the engine but not yet given a position by GridWorld's init
            # or reset, we might need a default position or error.
            # For now, let's assume if get_observation is called, agent_id should be in self.agent_positions
            # or an error should be raised earlier.
            # Fallback: if agent_id is known to start_positions but not yet in agent_positions (e.g. before first reset)
            if agent_id in self.agent_start_positions:
                start_pos = self.agent_start_positions[agent_id]
                if self._is_valid_position(start_pos[0], start_pos[1]) and self.grid[start_pos[1]][start_pos[0]]==0:
                     self.agent_positions[agent_id] = start_pos
                else: # Fallback if start pos is bad.
                    self.agent_positions[agent_id] = (0,0) # Default, or find first valid.
                    if self.grid[0][0] == 1:
                        found = False
                        for r in range(self.height):
                            for c in range(self.width):
                                if self.grid[r][c] == 0:
                                    self.agent_positions[agent_id] = (c,r)
                                    found = True
                                    break
                            if found: break
                        if not found: raise Exception(f"No valid cell for agent {agent_id} to get observation from.")

            else: # Agent truly unknown
                 raise ValueError(f"Agent {agent_id} not found in the environment and no start position known.")


        return {
            "agent_position": self.agent_positions[agent_id],
            "grid_view": [row[:] for row in self.grid] # Return a copy of the grid
        }

    def get_state(self) -> Dict[str, Any]:
        """
        Gets the overall current state of the environment.
        Returns the full grid state and all agent positions.
        """
        return {
            "grid": [row[:] for row in self.grid], # Return a copy
            "all_agent_positions": dict(self.agent_positions) # Return a copy
        }

    def is_done(self, agent_id: str) -> bool:
        """
        Checks if the simulation or the agent's task is completed.
        For now, always returns False (no specific end condition).
        """
        # This could be expanded, e.g., if agent reaches a goal, or max steps reached.
        # The 'agent_id' parameter allows for agent-specific 'done' conditions.
        return False

    def add_agent(self, agent_id: str, start_position: Optional[Tuple[int, int]] = None) -> None:
        """
        Adds a new agent to the environment or updates its start position.
        This is useful if agents are not all known at GridWorld construction.
        """
        if agent_id in self.agent_start_positions and start_position is None:
            # Agent already exists, and no new position given, just ensure it's in current positions.
            if agent_id not in self.agent_positions:
                 self.agent_positions[agent_id] = self.agent_start_positions[agent_id]
            return

        default_pos = (0, 0)
        # Find first available if (0,0) is a wall or invalid
        if not self._is_valid_position(0,0) or self.grid[0][0] == 1:
            found_fallback = False
            for r in range(self.height):
                for c in range(self.width):
                    if self.grid[r][c] == 0:
                        default_pos = (c,r)
                        found_fallback = True
                        break
                if found_fallback:
                    break
            if not found_fallback:
                raise Exception(f"Cannot add agent {agent_id}, no valid empty cells in the grid.")


        final_position = start_position if start_position is not None else default_pos

        if self._is_valid_position(final_position[0], final_position[1]) and \
           self.grid[final_position[1]][final_position[0]] == 0:
            self.agent_start_positions[agent_id] = final_position
            self.agent_positions[agent_id] = final_position
            print(f"GridWorld: Agent {agent_id} added/updated to start at {final_position}.")
        else:
            print(f"Warning: Invalid start position {final_position} for agent {agent_id}. Using default {default_pos}.")
            self.agent_start_positions[agent_id] = default_pos
            self.agent_positions[agent_id] = default_pos

if __name__ == '__main__':
    # Example Usage:
    print("--- GridWorld Example ---")
    # Initialize with some walls and specific agent start positions
    walls_list = [(1,1), (1,2), (2,1)]
    agent_starts = {"agent1": (0,0), "agent2": (2,2)}
    
    try:
        gw = GridWorld(width=4, height=4, walls=walls_list, agent_start_positions=agent_starts)
    except ValueError as e:
        print(f"Error during GridWorld init: {e}")
        exit()

    print("\nInitial State:")
    print(gw.get_state())

    print("\nObservation for agent1:")
    print(gw.get_observation("agent1"))

    print("\nTaking some steps for agent1:")
    actions = ["S", "E", "E", "N", "W", "Stay"]
    for action in actions:
        obs, reward = gw.step("agent1", action)
        print(f"Action: {action}, New Pos: {obs['agent_position']}, Reward: {reward}")
        # print(f"Grid view: {obs['grid_view']}") # Can be verbose

    print("\nFinal state for agent1:")
    print(gw.get_observation("agent1"))

    print("\nResetting agent1:")
    gw.reset("agent1")
    print(gw.get_observation("agent1"))
    
    print("\nAdding a new agent 'agent3' at (3,0)")
    gw.add_agent("agent3", (3,0))
    print(gw.get_observation("agent3"))
    obs, reward = gw.step("agent3", "S")
    print(f"Agent3 Action: S, New Pos: {obs['agent_position']}, Reward: {reward}")


    print("\nResetting all agents:")
    gw.reset()
    print("State after global reset:")
    print(gw.get_state())

    print("\nTrying to move agent2 into a wall:")
    # agent2 starts at (2,2). Wall at (1,2) and (2,1)
    print(f"Agent2 current pos: {gw.get_observation('agent2')['agent_position']}")
    obs_a2, _ = gw.step("agent2", "N") # try to move to (2,1) which is a wall
    print(f"Agent2 tried N. New pos: {obs_a2['agent_position']}") # Should be (2,2)
    obs_a2, _ = gw.step("agent2", "W") # try to move to (1,2) which is a wall
    print(f"Agent2 tried W. New pos: {obs_a2['agent_position']}") # Should be (2,2)
    obs_a2, _ = gw.step("agent2", "S") # try to move to (2,3) which is valid
    print(f"Agent2 tried S. New pos: {obs_a2['agent_position']}") # Should be (2,3)


    print("\n--- GridWorld Example with no initial agent positions ---")
    gw_no_agents = GridWorld(width=3, height=3)
    print(f"Initial state (no agents): {gw_no_agents.get_state()}")
    # Add agent after construction
    gw_no_agents.add_agent("agent_new", (1,1))
    print(f"State after adding agent: {gw_no_agents.get_state()}")
    obs_new, _ = gw_no_agents.step("agent_new", "N")
    print(f"Agent_new tried N. New pos: {obs_new['agent_position']}")


    print("\n--- GridWorld Example with agent starting on a wall (should fallback) ---")
    # (1,1) is a wall
    gw_bad_start = GridWorld(width=3, height=3, walls=[(1,1)], agent_start_positions={"a1": (1,1)})
    print(f"State for gw_bad_start: {gw_bad_start.get_state()}") # a1 should be at (0,0) or other fallback
    obs_bad, _ = gw_bad_start.step("a1", "S")
    print(f"a1 tried S. New pos: {obs_bad['agent_position']}")

    print("\n--- GridWorld Example: All cells are walls ---")
    try:
        gw_all_walls = GridWorld(width=2, height=1, walls=[(0,0), (1,0)], agent_start_positions={"a1": (0,0)})
    except Exception as e:
        print(f"Caught expected error for all-wall grid: {e}")

    print("--- GridWorld Example End ---")
