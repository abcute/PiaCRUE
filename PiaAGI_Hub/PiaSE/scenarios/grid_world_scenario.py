import sys
import os

# Ensure the PiaAGI_Hub directory is in the Python path
# This allows for absolute imports from PiaAGI_Hub.PiaSE...
# Adjust the number of os.path.dirname based on the script's location relative to PiaAGI_Hub
# Assuming this script is in PiaAGI_Hub/PiaSE/scenarios/
# We need to go up three levels to reach PiaAGI_Hub's parent directory.
# Script location: /app/PiaAGI_Hub/PiaSE/scenarios/grid_world_scenario.py
# current_dir: /app/PiaAGI_Hub/PiaSE/scenarios
# piase_dir: /app/PiaAGI_Hub/PiaSE
# piaagi_hub_dir: /app/PiaAGI_Hub
# project_root_dir (parent of PiaAGI_Hub, which is /app): /app
current_dir = os.path.dirname(os.path.abspath(__file__))
piase_dir = os.path.dirname(current_dir)
piaagi_hub_dir = os.path.dirname(piase_dir)
project_root_dir = os.path.dirname(piaagi_hub_dir) # This should be /app

if project_root_dir not in sys.path:
    sys.path.insert(0, project_root_dir)

# Now that /app is in sys.path, the import "from PiaAGI_Hub..." should work.

from PiaAGI_Hub.PiaSE.core_engine.basic_engine import BasicSimulationEngine
from PiaAGI_Hub.PiaSE.environments.grid_world import GridWorld
from PiaAGI_Hub.PiaSE.agents.basic_grid_agent import BasicGridAgent
from PiaAGI_Hub.PiaSE.core_engine.interfaces import PiaSEEvent

def run_grid_world_scenario():
    """
    Sets up and runs a simple scenario in the GridWorld environment
    with BasicGridAgents and a BasicSimulationEngine.
    """
    print("--- Starting Grid World Scenario ---")

    # 1. Instantiate Environment
    print("\n[SCENARIO] Initializing GridWorld environment...")
    walls = [(1, 0), (1, 1), (1, 2), (5, 5), (5, 6), (6, 5), (6,6)]
    # Define agent start positions for the environment, so it knows where to place them on reset/init
    agent_initial_positions = {
        "Agent_Random": (0, 0),
        "Agent_GoalSeeker": (0, 4)
    }
    grid_environment = GridWorld(width=10, height=10, walls=walls, agent_start_positions=agent_initial_positions)
    print(f"[SCENARIO] GridWorld created. Size: {grid_environment.width}x{grid_environment.height}. Walls at: {grid_environment.walls}")
    print(f"[SCENARIO] Initial agent positions in environment config: {grid_environment.agent_start_positions}")


    # 2. Instantiate Simulation Engine
    print("\n[SCENARIO] Initializing BasicSimulationEngine...")
    engine = BasicSimulationEngine(environment=grid_environment)
    print("[SCENARIO] BasicSimulationEngine created.")

    # 3. Instantiate Agents
    print("\n[SCENARIO] Creating agents...")
    agent1_id = "Agent_Random"
    agent1 = BasicGridAgent(policy="random")
    # agent1.set_id(agent1_id) # Engine will call set_id upon registration

    agent2_id = "Agent_GoalSeeker"
    # Goal for Agent_GoalSeeker, e.g., bottom-right corner
    # Ensure goal is not a wall, or agent might get stuck based on simple logic
    goal_pos = (grid_environment.width - 1, grid_environment.height - 1) 
    if grid_environment.grid[goal_pos[1]][goal_pos[0]] == 1: # if goal is a wall
        print(f"[SCENARIO] Warning: Chosen goal {goal_pos} is a wall. Agent may not reach it.")
    agent2 = BasicGridAgent(policy="goal_oriented", goal=goal_pos)
    # agent2.set_id(agent2_id) # Engine will call set_id

    print(f"[SCENARIO] Agent '{agent1_id}' created with policy: {agent1.policy}")
    print(f"[SCENARIO] Agent '{agent2_id}' created with policy: {agent2.policy}, goal: {agent2.goal}")

    # 4. Register Agents with the Engine
    print("\n[SCENARIO] Registering agents with the engine...")
    engine.register_agent(agent1_id, agent1)
    engine.register_agent(agent2_id, agent2)
    print(f"[SCENARIO] Agents registered. Current agents in engine: {list(engine.agents.keys())}")
    
    # Ensure agent positions are correctly set in the environment after registration
    # The GridWorld init already uses agent_start_positions if provided.
    # If agents were added to the engine without pre-defining in GridWorld's agent_start_positions,
    # we might need to call grid_environment.add_agent() or ensure engine.initialize() handles it.
    # Our BasicSimulationEngine.initialize calls environment.reset(), which should handle agent placement.

    # 5. Initialize the Engine (e.g., reset environment, setup agents)
    print("\n[SCENARIO] Initializing the simulation engine (calls environment.reset)...")
    engine.initialize() # This calls environment.reset()
    print("[SCENARIO] Engine initialized.")
    print(f"[SCENARIO] Environment state after init: {engine.get_environment_state()}")


    # 6. Run the Simulation
    num_simulation_steps = 20
    print(f"\n[SCENARIO] Running simulation for {num_simulation_steps} steps...")
    engine.run_simulation(num_steps=num_simulation_steps)
    print("\n[SCENARIO] Simulation finished.")

    # 7. Post-simulation information
    print("\n[SCENARIO] Final environment state:")
    final_state = engine.get_environment_state()
    print(final_state)
    for agent_id in engine.agents.keys():
        print(f"Agent '{agent_id}' final position: {final_state['all_agent_positions'].get(agent_id)}")
        if agent_id == agent2_id and agent2.goal:
             if final_state['all_agent_positions'].get(agent_id) == agent2.goal:
                 print(f"Agent '{agent_id}' successfully reached its goal {agent2.goal}!")
             else:
                 print(f"Agent '{agent_id}' did not reach its goal {agent2.goal}. Final position: {final_state['all_agent_positions'].get(agent_id)}")


    # Example of posting an event
    print("\n[SCENARIO] Posting a sample event...")
    sample_event = PiaSEEvent() # Assuming PiaSEEvent can be generic
    # If PiaSEEvent has attributes: sample_event = PiaSEEvent(type="scenario_end", data={"message": "Simulation cycle complete"})
    engine.post_event(sample_event)

    print("\n--- Grid World Scenario Finished ---")

if __name__ == '__main__':
    run_grid_world_scenario()
