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
# from PiaAGI_Hub.PiaSE.agents.basic_grid_agent import BasicGridAgent # Comment out or remove if only using QLearningAgent
from PiaAGI_Hub.PiaSE.agents.q_learning_agent import QLearningAgent
from PiaAGI_Hub.PiaSE.utils.visualizer import GridWorldVisualizer
from PiaAGI_Hub.PiaSE.core_engine.interfaces import PiaSEEvent
import matplotlib.pyplot as plt # For plot management

def run_grid_world_scenario():
    """
    Sets up and runs a scenario in the GridWorld environment
    with a QLearningAgent and a BasicSimulationEngine.
    """
    print("--- Starting Grid World Q-Learning Scenario ---")

    # 1. Instantiate Environment
    print("\n[SCENARIO] Initializing GridWorld environment...")
    grid_width = 5
    grid_height = 5
    # Define a goal position for the Q-learning agent
    goal = (grid_width - 1, grid_height - 1) # e.g., bottom-right corner
    walls = [(1,1), (1,2), (2,1), (3,3)] # Some walls
    start_pos_q_agent = (0,0)

    # Ensure goal is not a wall
    if goal in walls:
        print(f"[SCENARIO] Error: Goal position {goal} is a wall. Scenario cannot proceed logically.")
        return

    # Ensure start position is not a wall
    if start_pos_q_agent in walls:
        print(f"[SCENARIO] Error: Start position {start_pos_q_agent} for Q-agent is a wall. Scenario cannot proceed logically.")
        return


    grid_environment = GridWorld(
        width=grid_width,
        height=grid_height,
        walls=walls,
        goal_position=goal,
        agent_start_positions={"q_agent_1": start_pos_q_agent} # Define start for the Q-agent
    )
    print(f"[SCENARIO] GridWorld created. Size: {grid_width}x{grid_height}. Goal: {goal}. Walls: {walls}")
    print(f"[SCENARIO] Q-Agent start position: {start_pos_q_agent}")


    # 2. Instantiate Simulation Engine
    print("\n[SCENARIO] Initializing BasicSimulationEngine...")
    engine = BasicSimulationEngine(environment=grid_environment)
    print("[SCENARIO] BasicSimulationEngine created.")

    # 3. Instantiate QLearningAgent
    print("\n[SCENARIO] Creating QLearningAgent...")
    q_agent_id = "q_agent_1"
    # exploration_rate can be higher initially, e.g., 0.5, and then decayed over time.
    # For a fixed number of steps, a moderate value like 0.1-0.2 might be okay.
    q_agent = QLearningAgent(learning_rate=0.1, discount_factor=0.9, exploration_rate=0.2, default_q_value=0.0)
    print(f"[SCENARIO] Agent '{q_agent_id}' created with lr={q_agent.lr}, gamma={q_agent.gamma}, epsilon={q_agent.epsilon}")

    # 4. Register QLearningAgent with the Engine
    print("\n[SCENARIO] Registering QLearningAgent with the engine...")
    engine.register_agent(q_agent_id, q_agent)
    print(f"[SCENARIO] Agents registered. Current agents in engine: {list(engine.agents.keys())}")

    # 5. Instantiate Visualizer
    print("\n[SCENARIO] Initializing GridWorldVisualizer...")
    visualizer = GridWorldVisualizer(grid_environment)
    print("[SCENARIO] GridWorldVisualizer created.")
    plt.ion() # Turn on interactive mode for matplotlib for step-by-step rendering

    # 6. Initialize the Engine
    # This will now also call agent.initialize_q_table() and agent.perceive() for the QLearningAgent
    # using the logic added to BasicSimulationEngine.initialize()
    print("\n[SCENARIO] Initializing the simulation engine (calls env.reset, agent.perceive, agent.initialize_q_table)...")
    engine.initialize()
    print("[SCENARIO] Engine initialized.")
    print(f"[SCENARIO] Environment state after init: {engine.get_environment_state()}")
    print(f"[SCENARIO] Q-Agent initial Q-table for state {q_agent.current_state}: {q_agent.q_table.get(q_agent.current_state)}")

    # Initial render
    visualizer.render(title="Initial State", step_delay=0.5)


    # 7. Run the Simulation with manual loop for visualization
    num_simulation_steps = 200 # Adjusted for visualization speed
    print(f"\n[SCENARIO] Running simulation for up to {num_simulation_steps} steps with visualization...")

    for i in range(num_simulation_steps):
        print(f"\n--- Scenario Step {i+1}/{num_simulation_steps} ---")

        engine.run_step() # Engine's run_step processes one step for all agents

        visualizer.render(title=f"After Step {i+1}", step_delay=0.2)

        if grid_environment.is_done(q_agent_id): # Check if the Q-agent reached the goal
             print(f"Agent '{q_agent_id}' reached the goal at step {i+1}!")
             break

    print("\n[SCENARIO] Simulation loop finished.")

    # 8. Post-simulation information
    print("\n[SCENARIO] Final environment state:")
    final_state = engine.get_environment_state()
    print(final_state)
    print(f"Agent '{q_agent_id}' final position: {final_state['all_agent_positions'].get(q_agent_id)}")
    if final_state['all_agent_positions'].get(q_agent_id) == goal:
        print(f"Agent '{q_agent_id}' successfully reached its goal {goal}!")
    else:
        print(f"Agent '{q_agent_id}' did not reach its goal {goal}. Final position: {final_state['all_agent_positions'].get(q_agent_id)}")

    # Print Q-table information
    print("\n--- Q-Learning Agent's Q-Table (sample) ---")
    q_table_sample_count = 0
    for state, actions in list(q_agent.q_table.items()):
        if q_table_sample_count >= 10: # Print for first 10 states with non-default values
            # Check if any action has a non-default Q-value
            if any(q_val != q_agent.default_q for q_val in actions.values()):
                 print(f"State {state}:")
                 for action, q_val in actions.items():
                     if q_val != q_agent.default_q : # Only print actions that were updated
                         print(f"  Action {action}: {q_val:.3f}")
                 q_table_sample_count +=1
            if q_table_sample_count > 25: # Hard limit on total states printed to avoid excessive output
                print("... (output truncated, many states in Q-table)")
                break
        else: # Print first few states regardless of values
            print(f"State {state}:")
            for action, q_val in actions.items():
                print(f"  Action {action}: {q_val:.3f}")
            q_table_sample_count += 1


    # Example of Q-values for states near the goal
    # Note: State representation in Q-table is agent's position tuple, e.g., (x,y)
    if goal in q_agent.q_table:
       print(f"\nQ-values for goal state {goal}: {q_agent.q_table[goal]}")

    # Example: print Q-values for state (0,0) if it exists
    if (0,0) in q_agent.q_table:
        print(f"Q-values for start state (0,0): {q_agent.q_table[(0,0)]}")


    # Example of posting an event (optional)
    # print("\n[SCENARIO] Posting a sample event...")
    # sample_event = PiaSEEvent()
    # engine.post_event(sample_event)

    # Final render and keep plot open
    visualizer.render(title=f"Final State (Close window to exit)", step_delay=None)
    if plt.isinteractive():
        plt.ioff() # Turn off interactive mode

    print("\n--- Grid World Q-Learning Scenario Finished ---")

if __name__ == '__main__':
    run_grid_world_scenario()
