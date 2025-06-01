import matplotlib.pyplot as plt
import numpy as np
from typing import Optional, Dict # Ensure Dict is imported for type hinting
import os # Added import for os module
import sys # Added import for sys module

# Attempt to import GridWorld with error handling for standalone execution
try:
    from PiaAGI_Hub.PiaSE.environments.grid_world import GridWorld
except ImportError:
    # This allows the file to be potentially run or imported in contexts
    # where the full PiaAGI_Hub structure isn't in sys.path yet,
    # though for actual use within PiaSE, the direct import should work.
    GridWorld = None
    print("Warning: GridWorld could not be imported. Visualizer might not work as expected if GridWorld is None.")


class GridWorldVisualizer:
    def __init__(self, grid_world_env: Optional[GridWorld]): # Type hint GridWorld as Optional
        if GridWorld is None and grid_world_env is not None:
            # This check is a bit redundant if the class is always instantiated with a GridWorld instance
            # from within the PiaSE framework where imports are resolved.
            # However, it's a safeguard for scenarios where GridWorld might fail to import for other reasons.
            raise ImportError("GridWorld class was not imported correctly, but an instance was provided. Check imports.")

        if grid_world_env is None:
            # This case could be handled if visualizer is meant to be more generic
            # or initialized without an environment initially. For now, require it.
            raise ValueError("GridWorldVisualizer requires a GridWorld environment instance.")

        if not isinstance(grid_world_env, GridWorld):
             # Check if the provided env is actually a GridWorld instance, if GridWorld was imported.
             # This handles cases where GridWorld is None due to import error vs. wrong type passed.
            if GridWorld is not None: # Only raise if GridWorld type is known
                raise TypeError(f"Expected grid_world_env to be an instance of GridWorld, got {type(grid_world_env)}")
            # If GridWorld itself is None, we can't be sure, but the user was warned.

        self.env = grid_world_env
        self.fig, self.ax = plt.subplots()
        self.agent_markers: Dict[str, plt.Text] = {} # To store agent text markers for updating

    def render(self, title: str = "", output_path: Optional[str] = None, step_delay: Optional[float] = 0.1):
        if self.env is None:
            print("Error: Environment not set for visualizer.")
            return None # Return None if path not saved

        self.ax.clear()

        # Grid and labels
        # Major ticks (for labels)
        self.ax.set_xticks(np.arange(0, self.env.width, 1))
        self.ax.set_yticks(np.arange(0, self.env.height, 1))
        # Labels for major ticks
        self.ax.set_xticklabels(np.arange(0, self.env.width))
        self.ax.set_yticklabels(np.arange(0, self.env.height))
        # Minor ticks (for gridlines) - positioned at -0.5, 0.5, 1.5, etc.
        self.ax.set_xticks(np.arange(-0.5, self.env.width, 1), minor=True)
        self.ax.set_yticks(np.arange(-0.5, self.env.height, 1), minor=True)

        self.ax.grid(which="minor", color="black", linestyle='-', linewidth=1) # Grid lines based on minor ticks
        self.ax.set_xlim(-0.5, self.env.width - 0.5)
        self.ax.set_ylim(-0.5, self.env.height - 0.5)
        self.ax.invert_yaxis()

        # Walls
        if self.env.walls:
            for wall_x, wall_y in self.env.walls:
                self.ax.add_patch(plt.Rectangle((wall_x - 0.5, wall_y - 0.5), 1, 1, facecolor='black'))

        # Goal
        if self.env.goal_position:
            goal_x, goal_y = self.env.goal_position
            self.ax.add_patch(plt.Rectangle((goal_x - 0.5, goal_y - 0.5), 1, 1, facecolor='gold', alpha=0.7))
            self.ax.text(goal_x, goal_y, 'G', ha='center', va='center', color='black', fontsize=10)


        # Agents
        env_state_agents = self.env.agent_positions # Direct access as per GridWorld implementation
        for agent_id, pos in env_state_agents.items():
            agent_x, agent_y = pos
            # Simple marker: First letter of agent_id or 'A'
            display_id = agent_id[0].upper() if agent_id else 'A'
            self.ax.text(agent_x, agent_y, display_id, ha='center', va='center', color='blue', fontsize=12, weight='bold')


        self.ax.set_title(title)

        saved_path = None # Initialize saved_path
        if output_path:
            try:
                self.fig.savefig(output_path)
                # print(f"Saved plot to {output_path}") # Optional: for debugging
                saved_path = output_path
            except Exception as e:
                print(f"Error saving plot to {output_path}: {e}")
        else: # No output_path, so handle interactive display based on step_delay
            if plt.isinteractive():
                plt.draw() # Update the plot

            if step_delay is not None and step_delay > 0:
                plt.pause(step_delay)
            elif step_delay is None: # For showing a single static plot at the end
                if plt.isinteractive():
                    plt.ioff()
                plt.show()

        # If saving, we generally don't want to call plt.show() or plt.pause()
        # as it might interfere with server operation or try to open GUI.
        # The 'Agg' backend should prevent GUI.
        # Consider plt.close(self.fig) after saving if generating many images in a loop without display.
        # For now, let app.py manage closing, or if visualizer is reused, it clears self.ax.

        return saved_path # Return the path where image was saved


if __name__ == '__main__':
    # This example usage assumes GridWorld can be imported or is defined above
    # For robust testing, this should be part of a test script or scenario

    # Adjust sys.path for standalone execution of this example
    # visualizer.py is in /app/PiaAGI_Hub/PiaSE/utils/visualizer.py
    current_script_dir = os.path.dirname(os.path.abspath(__file__)) # .../PiaSE/utils
    utils_dir_parent = os.path.dirname(current_script_dir) # .../PiaSE
    piase_dir_parent = os.path.dirname(utils_dir_parent) # .../PiaAGI_Hub
    project_root_for_example = os.path.dirname(piase_dir_parent) # /app (parent of PiaAGI_Hub)

    if project_root_for_example not in sys.path:
        sys.path.insert(0, project_root_for_example) # Add /app to sys.path
        print(f"Added to sys.path for example: {project_root_for_example}")

    # Re-attempt import if it failed initially
    if GridWorld is None:
        try:
            from PiaAGI_Hub.PiaSE.environments.grid_world import GridWorld
            print("GridWorld imported successfully for example.")
        except ImportError as e:
            print(f"Failed to import GridWorld for example even after path adjustment: {e}")


    if GridWorld:
        print("Attempting GridWorldVisualizer example...")
        plt.ion() # Turn on interactive mode for plt.pause()
        try:
            # Example:
            walls_example = [(1,1), (1,2), (2,1), (3,3)]
            goal_example = (4,4)
            start_pos_agent1 = (0,0)

            example_env = GridWorld(width=5, height=5, walls=walls_example, goal_position=goal_example,
                                    agent_start_positions={"agent1": start_pos_agent1})

            if "agent1" not in example_env.agent_positions: # Should be set by agent_start_positions
                 example_env.add_agent("agent1", start_pos_agent1)


            visualizer = GridWorldVisualizer(example_env)

            visualizer.render(title="Initial State", step_delay=1)

            actions = ["E", "E", "S", "S", "E", "E"] # Path to (4,4)
            agent_to_move = "agent1"

            for i, action in enumerate(actions):
                print(f"Taking action: {action} for {agent_to_move}")
                if example_env.is_done(agent_to_move):
                    print(f"Agent {agent_to_move} reached goal early at step {i}!")
                    break
                obs, reward, done, info = example_env.step(agent_to_move, action)
                visualizer.render(title=f"Step {i+1}: Action {action}, R: {reward:.1f}", step_delay=0.5)
                if done:
                    print(f"Agent {agent_to_move} reached the goal at step {i+1}!")
                    break

            print("Example finished. Plot will remain open if not in a headless environment.")
            visualizer.render(title="Final State (close window to exit)", step_delay=None) # Keeps window open

        except Exception as e:
            print(f"Error during GridWorldVisualizer example: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if plt.isinteractive():
                 plt.ioff() # Turn off interactive mode
            # plt.show() # Ensure plot is shown if not using step_delay=None in the last render
    else:
        print("GridWorld class not available, skipping visualizer example.")
