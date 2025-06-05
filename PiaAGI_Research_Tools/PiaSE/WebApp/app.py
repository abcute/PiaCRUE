from flask import Flask, render_template, url_for # Added url_for
import sys
import os
import time # For unique filenames

# --- Keep existing sys.path manipulation ---
# Assuming app.py is in PiaAGI_Hub/PiaSE/WebApp/
current_dir = os.path.dirname(os.path.abspath(__file__)) # WebApp directory
piase_dir = os.path.dirname(current_dir) # PiaSE directory
static_dir = os.path.join(current_dir, 'static') # Path to static folder in WebApp
if not os.path.exists(static_dir):
    os.makedirs(static_dir) # Ensure static directory exists

pia_agi_research_tools_dir = os.path.dirname(piase_dir) # PiaAGI_Research_Tools directory
project_root_for_import = os.path.dirname(pia_agi_research_tools_dir) # Parent of PiaAGI_Research_Tools
if project_root_for_import not in sys.path:
    sys.path.insert(0, project_root_for_import)
# --- End of sys.path manipulation ---

# Now import PiaSE components
from PiaAGI_Research_Tools.PiaSE.core_engine.basic_engine import BasicSimulationEngine
from PiaAGI_Research_Tools.PiaSE.environments.grid_world import GridWorld
from PiaAGI_Research_Tools.PiaSE.agents.q_learning_agent import QLearningAgent
from PiaAGI_Research_Tools.PiaSE.utils.visualizer import GridWorldVisualizer
import matplotlib
matplotlib.use('Agg') # Use 'Agg' backend for Matplotlib to prevent GUI issues in server environment
import matplotlib.pyplot as plt


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_scenario', methods=['POST'])
def run_scenario_route():
    try:
        # 1. Setup Environment
        grid_width = 5
        grid_height = 5
        goal = (grid_width - 1, grid_height - 1)
        walls = [(1, 1), (1, 2), (2, 1), (3, 3)]
        start_pos_q_agent = (0, 0)

        gw = GridWorld(
            width=grid_width,
            height=grid_height,
            walls=walls,
            goal_position=goal,
            agent_start_positions={"q_agent_1": start_pos_q_agent}
        )

        # 2. Setup Engine and Agent
        engine = BasicSimulationEngine(gw)
        q_agent = QLearningAgent(exploration_rate=0.2, learning_rate=0.1, discount_factor=0.9)
        engine.register_agent("q_agent_1", q_agent)

        # Initialize engine (sets up agent's action space, initial state)
        engine.initialize()

        # 3. Setup Visualizer and Output
        # Ensure a unique directory for this run's frames within static
        run_timestamp = time.strftime("%Y%m%d-%H%M%S")
        frames_subdir_name = f"run_{run_timestamp}" # More descriptive
        frames_output_dir_absolute = os.path.join(static_dir, 'frames', frames_subdir_name)
        if not os.path.exists(frames_output_dir_absolute):
            os.makedirs(frames_output_dir_absolute)

        visualizer = GridWorldVisualizer(gw)
        image_paths = []
        text_log = ["Scenario Log:"]

        # Initial render
        img_filename_initial = f"step_000.png"
        img_path_initial_absolute = os.path.join(frames_output_dir_absolute, img_filename_initial)
        visualizer.render(title="Initial State", output_path=img_path_initial_absolute, step_delay=None) # Use step_delay=None for saving
        image_paths.append(url_for('static', filename=os.path.join('frames', frames_subdir_name, img_filename_initial)))
        text_log.append("Initial state rendered.")


        # 4. Run Simulation Loop
        num_steps = 50 # Reduced for web scenario
        text_log.append(f"Starting simulation for up to {num_steps} steps...")
        for i in range(num_steps):
            step_info = f"--- Step {i+1}/{num_steps} ---"
            print(step_info) # For server log
            text_log.append(step_info)

            # Store state before step for Q-agent's learn method if needed (though current Q-agent uses internal state)
            # current_state_for_learning = q_agent.current_state

            engine.run_step() # Engine processes one step for all agents
                              # This includes: agent.perceive(S), agent.act() -> A, env.step(A) -> S', R, D
                              # agent.learn((R,S')), agent.perceive(S')

            text_log.append(f"Agent q_agent_1 action: {q_agent.last_action}, New position: {gw.agent_positions.get('q_agent_1')}")

            # Render and save image
            img_filename = f"step_{i+1:03d}.png"
            img_path_absolute = os.path.join(frames_output_dir_absolute, img_filename)
            visualizer.render(title=f"After Step {i+1}", output_path=img_path_absolute, step_delay=None) # Use step_delay=None for saving
            image_paths.append(url_for('static', filename=os.path.join('frames', frames_subdir_name, img_filename)))

            if gw.is_done("q_agent_1"):
                text_log.append(f"Agent q_agent_1 reached the goal at step {i+1}!")
                print(f"Agent q_agent_1 reached the goal at step {i+1}!")
                break

        text_log.append("\nSimulation finished.")
        print("Simulation finished.")

        # Add Q-table sample to log
        text_log.append("\n--- Q-Learning Agent's Q-Table (sample for visited states) ---")
        q_table_sample_count = 0
        for state_key_tuple, actions_map in list(q_agent.q_table.items()): # Use items()
            if q_table_sample_count >= 10 : break # Limit log size
            # Check if any action has a non-default Q-value for this state
            if any(q_val != q_agent.default_q for q_val in actions_map.values()):
                text_log.append(f"State {state_key_tuple}:")
                for action, q_val in actions_map.items():
                     if q_val != q_agent.default_q: # Only print actions that were updated
                        text_log.append(f"  Action {action}: {q_val:.3f}")
                q_table_sample_count +=1
        if not q_table_sample_count:
            text_log.append("No Q-values were significantly updated from default during this short run.")

        plt.close(visualizer.fig) # Close the figure to free memory

        # Render the results template
        return render_template('results.html', image_paths=image_paths, text_log=text_log)

    except Exception as e:
        import traceback
        error_html = f"<h1>Error during simulation:</h1><pre>{traceback.format_exc()}</pre>"
        print(f"Error during simulation: {traceback.format_exc()}") # Print to server log as well
        return error_html, 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
