import random
import time
from typing import List, Dict, Optional, Any, Tuple

from PiaAGI_Research_Tools.PiaSE.core_engine.basic_engine import BasicSimulationEngine
# Corrected import path for refactored GridWorld
from PiaAGI_Research_Tools.PiaSE.environments.grid_world import GridWorld, GridObject 
from PiaAGI_Research_Tools.PiaSE.agents.q_learning_agent import QLearningAgent
from PiaAGI_Research_Tools.PiaSE.core_engine.interfaces import Environment, AgentInterface, PerceptionData, ActionCommand, ActionResult, PiaSEEvent

# --- Environment Subclass for Competence ---
class CompetenceGridWorld(GridWorld):
    """A GridWorld that can change its goal position and add obstacles for competence assessment."""
    def __init__(self, width: int, height: int, default_agent_id: str = "q_learner", **kwargs):
        # Pass only relevant GridWorld params to super, not agent_id directly unless super supports it
        # The refactored GridWorld takes default_agent_id
        super().__init__(width, height, default_agent_id=default_agent_id, **kwargs)
        self.task_completion_reward_value = kwargs.get("reward_goal", 10.0) # Match reward_goal

    def set_goal_position(self, position: Tuple[int, int], agent_id: Optional[str] = None):
        if self._is_valid_position(position[0], position[1]) and not self._is_obstacle(position[0], position[1]):
            self.goal_position = position
            print(f"CompetenceGridWorld: Goal position set to {position}")
            # Resetting or other logic might be needed if goal change affects current episode state
        else:
            print(f"CompetenceGridWorld: Warning - Invalid or obstacle position {position} for goal. Not set.")

    def add_obstacles(self, obstacles: List[GridObject]):
        """Adds new obstacles to the grid. Obstacles are GridObjects with blocks_movement=True."""
        for obs_data in obstacles:
            if not self._is_valid_position(obs_data.position[0], obs_data.position[1]):
                print(f"Warning: Obstacle {obs_data.name} at {obs_data.position} is out of bounds. Ignoring.")
                continue
            if self._is_obstacle(obs_data.position[0], obs_data.position[1]):
                print(f"Warning: Position {obs_data.position} for obstacle {obs_data.name} is already an obstacle.")
                # Continue, or decide to replace/update. For now, just adds to static_objects if not wall.
            
            # Ensure it's marked as blocking if not already
            obs_data.properties["blocks_movement"] = True 
            
            # Avoid duplicating walls, but can add new GridObjects that are obstacles
            if not self._is_wall(obs_data.position[0], obs_data.position[1]):
                 # Check if an object with same name and pos already exists
                found = False
                for existing_obj in self.static_objects:
                    if existing_obj.name == obs_data.name and existing_obj.position == obs_data.position:
                        existing_obj.properties = obs_data.properties # Update properties
                        found = True
                        break
                if not found:
                    self.static_objects.append(obs_data)
                print(f"CompetenceGridWorld: Added/Updated obstacle {obs_data.name} at {obs_data.position}")
            else:
                print(f"CompetenceGridWorld: Position {obs_data.position} for obstacle {obs_data.name} is a wall. Not adding as GridObject.")


    # The step method override is removed as the base GridWorld.step should now be compliant
    # with ActionResult and its details field for reward and is_terminal.

# --- Scenario Definition ---
SCENARIO_NAME = "Grid World Competence Assessment"
AGENT_ID_Q = "q_learner_agent"

# Configuration
GRID_CONFIG = {"width": 5, "height": 5, "agent_start_pos": (0,0)}
AGENT_CONFIG = {"learning_rate": 0.1, "discount_factor": 0.9, "exploration_rate": 0.2}
MAX_EPISODES = 5
MAX_STEPS_PER_EPISODE = 100

TASKS = [
    {"name": "Task1_SimpleGoal", "goal": (4,4), "obstacles_to_add": []},
    {"name": "Task2_NewGoal", "goal": (0,4), "obstacles_to_add": []},
    {"name": "Task3_WithObstacle", "goal": (4,4), "obstacles_to_add": [GridObject("block1", (2,2), {"blocks_movement": True})]},
    {"name": "Task4_ChangedObstacle", "goal": (0,0), "obstacles_to_add": [GridObject("block2", (3,3), {"blocks_movement": True})]},
]

def setup_environment(task_config: Dict, existing_env: Optional[CompetenceGridWorld] = None) -> CompetenceGridWorld:
    if existing_env is None:
        print(f"Setting up CompetenceGridWorld environment for task: {task_config['name']}")
        env = CompetenceGridWorld(
            width=GRID_CONFIG["width"], 
            height=GRID_CONFIG["height"],
            agent_start_pos=GRID_CONFIG["agent_start_pos"], # For default agent
            goal_position=task_config["goal"], # Initial goal for this task
            walls=[], # Start with no walls, add through obstacles if needed
            static_objects=task_config.get("initial_static_objects", []), # For pre-existing objects in task
            default_agent_id=AGENT_ID_Q
        )
    else:
        env = existing_env
        print(f"Reconfiguring CompetenceGridWorld for task: {task_config['name']}")
    
    env.set_goal_position(task_config["goal"])
    if task_config.get("obstacles_to_add"):
        env.add_obstacles(task_config["obstacles_to_add"])
    
    # Important: Reset the environment to apply changes and get initial state for the agent
    # The reset in GridWorld now handles the default agent_id correctly.
    env.reset() 
    return env

def setup_agents(env: Environment, config: Optional[Dict] = None) -> List[AgentInterface]:
    # The QLearningAgent's action_space is now configured via agent.configure() by the engine.
    # So, we don't need to pass action_space to constructor.
    agent_config_to_use = config.get("agent_params", AGENT_CONFIG) if config else AGENT_CONFIG
    q_agent = QLearningAgent(
        learning_rate=agent_config_to_use["learning_rate"],
        discount_factor=agent_config_to_use["discount_factor"],
        exploration_rate=agent_config_to_use["exploration_rate"]
    )
    # Agent ID will be set by the engine during initialization from the dict keys.
    return [q_agent]


# --- Main Execution ---
def run_scenario(custom_config: Optional[Dict] = None):
    print(f"--- Starting Scenario: {SCENARIO_NAME} ---")
    
    engine = BasicSimulationEngine()
    
    # Initialize agent once
    # Agent's action space will be configured by engine using env.get_action_space()
    # and calling agent.configure() if available.
    q_agent = setup_agents(env=None, config=custom_config)[0] # env is not needed for this agent's __init__
    agents_dict = {AGENT_ID_Q: q_agent} # Engine expects a dict

    current_env: Optional[CompetenceGridWorld] = None
    total_reward_all_tasks = 0

    for task_idx, task in enumerate(TASKS):
        print(f"\n--- Starting Task {task_idx + 1}: {task['name']} ---")
        current_env = setup_environment(task_config=task, existing_env=current_env)
        
        # Re-initialize the engine for the new/modified environment configuration for the task
        # Agent state (Q-table) persists across tasks.
        engine.initialize(
            environment=current_env, 
            agents=agents_dict, # Pass the same agent instance(s)
            scenario_config={"name": f"{SCENARIO_NAME} - {task['name']}", "task_id": task_idx}
        )
        
        episode_reward = 0
        for step in range(MAX_STEPS_PER_EPISODE):
            engine.run_step() # Engine handles perceive, act, learn cycle for agent
            
            # Assuming reward is in ActionResult.details from GridWorld step
            # The logger in BasicSimulationEngine will log action_results including rewards.
            # For scenario summary, we might want to aggregate rewards here.
            # Accessing agent's last feedback is tricky; engine should provide this if needed for scenario logic,
            # or scenario relies on logger output.
            # For simplicity, let's assume the scenario doesn't track step-by-step reward here,
            # but focuses on task completion.

            if current_env.is_done(AGENT_ID_Q): # Check if agent reached goal for this task
                print(f"Task '{task['name']}' completed at step {step + 1}. Agent reached goal.")
                # The reward for reaching goal is handled by GridWorld and Q-agent learns from it.
                # We can log a specific scenario event.
                if engine.logger:
                    engine.logger.log(engine.current_step, "TASK_COMPLETED", "scenario_logic", {"task_name": task['name']})
                break 
        else: # Loop finished without break (max steps reached for task)
            print(f"Task '{task['name']}' max steps ({MAX_STEPS_PER_EPISODE}) reached.")
            if engine.logger:
                 engine.logger.log(engine.current_step, "TASK_MAX_STEPS", "scenario_logic", {"task_name": task['name']})
        
        # For overall scenario reporting, one might sum rewards if they were accessible here.
        # This simple scenario focuses on task completion.

    if engine.logger: # Ensure logger exists (it should if initialized)
        engine.logger.log(engine.current_step, "SCENARIO_END", "scenario_logic", {"reason": "All tasks processed"})
        engine.logger.close()
    print(f"--- Scenario: {SCENARIO_NAME} Finished ---")

if __name__ == "__main__":
    run_scenario()
```
