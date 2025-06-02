import random
import time
from typing import List, Dict, Optional, Any, Tuple

from PiaAGI_Research_Tools.PiaSE.core_engine.basic_engine import BasicSimulationEngine
from PiaAGI_Research_Tools.PiaSE.environments.grid_world import GridWorld, GridObject
from PiaAGI_Research_Tools.PiaSE.core_engine.interfaces import Environment, AgentInterface, PerceptionData, ActionCommand, ActionResult, PiaSEEvent

# --- Agent Definition ---
class CuriosityGridAgent(AgentInterface):
    def __init__(self, agent_id: str, action_space: List[str]):
        self.agent_id = agent_id
        self.action_space = action_space # e.g., ["up", "down", "left", "right"]
        self.last_perception: Optional[PerceptionData] = None
        self.known_artifact_locations: List[Tuple[int, int]] = []
        print(f"CuriosityGridAgent '{self.agent_id}' initialized with action space: {self.action_space}")

    def set_id(self, agent_id: str):
        self.agent_id = agent_id

    def get_id(self) -> str:
        return self.agent_id

    def perceive(self, observation: PerceptionData, event: Optional[PiaSEEvent] = None):
        self.last_perception = observation
        if observation and observation.sensor_data:
            agent_pos = observation.sensor_data.get("agent_position")
            # objects_on_tile is now a list of dicts: [{"name": "...", "properties": {...}}]
            objects_on_tile = observation.sensor_data.get("objects_on_tile", [])

            if agent_pos:
                for obj_data in objects_on_tile:
                    if obj_data.get("name") == "artifact" and obj_data.get("properties", {}).get("is_unknown", True):
                        # Ensure agent_pos is a tuple for consistent storage and checking
                        current_pos_tuple = tuple(agent_pos) if isinstance(agent_pos, list) else agent_pos
                        if current_pos_tuple not in self.known_artifact_locations:
                            print(f"AGENT {self.agent_id}: Found an unknown artifact with ID {obj_data.get('properties',{}).get('id','N/A')} at {current_pos_tuple}! Expressing curiosity.")
                            self.known_artifact_locations.append(current_pos_tuple)
                            # In a real agent, this might trigger an "inspect" action or internal model update.
                            # For this scenario, discovering it is enough.
                            # The scenario logic will check self.known_artifact_locations.
                        break 

    def act(self) -> ActionCommand:
        chosen_action = random.choice(self.action_space)
        return ActionCommand(action_type=chosen_action, parameters={})

    def learn(self, feedback: ActionResult):
        pass

    def initialize_q_table(self, state: Any, action_space: list): pass 
    def get_q_value(self, state: Any, action: Any) -> float: return 0.0
    def update_q_value(self, state: Any, action: Any, reward: float, next_state: Any, learning_rate: float, discount_factor: float, action_space: list): pass


# --- Scenario Definition ---
SCENARIO_NAME = "Curiosity in the Unknown Artifact Grid World"
AGENT_ID_EXPLORER = "ExplorerAgent"

GRID_WIDTH = 10
GRID_HEIGHT = 10
AGENT_START_POS = (0, 0)
ARTIFACT_POSITIONS = [(3, 3), (7, 7), (5, 1)] 

def setup_environment(config: Optional[Dict] = None) -> Environment:
    print(f"Setting up '{SCENARIO_NAME}' environment...")
    
    artifacts = []
    for i, pos in enumerate(ARTIFACT_POSITIONS):
        artifacts.append(GridObject(name="artifact", position=pos, properties={"id": f"artifact_{i}", "is_unknown": True, "value": random.randint(10,100)}))

    goal_pos = (GRID_WIDTH -1, GRID_HEIGHT -1) # Dummy goal

    env = GridWorld(
        width=GRID_WIDTH,
        height=GRID_HEIGHT,
        agent_start_pos=AGENT_START_POS,
        goal_position=goal_pos,
        static_objects=artifacts
    )
    
    original_get_observation = env.get_observation
    def augmented_get_observation(agent_id: str) -> PerceptionData:
        perception = original_get_observation(agent_id)
        agent_pos_tuple = perception.sensor_data.get("agent_position") # GridWorld returns tuple
        objs_on_tile_details = []
        if agent_pos_tuple:
            # Combine static and dynamic objects for checking
            all_objects_on_grid = (env.static_objects or []) + (env.dynamic_objects or [])
            for obj in all_objects_on_grid:
                if obj.position == agent_pos_tuple: # Ensure comparison is tuple vs tuple
                    objs_on_tile_details.append({"name": obj.name, "properties": obj.properties})
        perception.sensor_data["objects_on_tile"] = objs_on_tile_details
        return perception
    env.get_observation = augmented_get_observation # Monkey-patching for scenario specific needs
    
    return env

def setup_agents(env: Environment, config: Optional[Dict] = None) -> List[AgentInterface]:
    print("Setting up agents...")
    action_space = env.get_action_space() 
    explorer_agent = CuriosityGridAgent(agent_id=AGENT_ID_EXPLORER, action_space=action_space)
    return [explorer_agent]

# --- Main Execution ---
def run_scenario(max_steps: int = 100, custom_config: Optional[Dict] = None):
    print(f"--- Starting Scenario: {SCENARIO_NAME} ---")
    
    engine = BasicSimulationEngine()
    
    environment = setup_environment(config=custom_config)
    agent_list = setup_agents(env=environment, config=custom_config)
    
    agents_dict = {agent.get_id(): agent for agent in agent_list}

    engine.initialize(
        environment=environment, 
        agents=agents_dict,
        scenario_config={"name": SCENARIO_NAME, "max_steps": max_steps}
    )
    
    artifacts_found_count = 0
    total_artifacts = len(ARTIFACT_POSITIONS)

    for i in range(max_steps):
        engine.run_step() 
        
        agent_instance = agents_dict.get(AGENT_ID_EXPLORER)
        if agent_instance and isinstance(agent_instance, CuriosityGridAgent):
            if len(agent_instance.known_artifact_locations) > artifacts_found_count:
                new_artifact_loc = agent_instance.known_artifact_locations[-1]
                artifacts_found_count = len(agent_instance.known_artifact_locations)
                print(f"SCENARIO: Agent {agent_instance.get_id()} officially discovered artifact at {new_artifact_loc} ({artifacts_found_count}/{total_artifacts} found).")
                if engine.logger:
                    engine.logger.log(
                        engine.current_step, 
                        "ARTIFACT_DISCOVERED", 
                        "scenario_logic", 
                        {"agent_id": agent_instance.get_id(), "location": list(new_artifact_loc), "count": artifacts_found_count} # Log location as list for JSON
                    )

        if artifacts_found_count == total_artifacts:
            print(f"\n*** {SCENARIO_NAME} COMPLETED: All {total_artifacts} artifacts found! ***")
            if engine.logger:
                engine.logger.log(engine.current_step, "SCENARIO_WIN", "scenario_logic", {"reason": "All artifacts found"})
            break
            
        if engine._are_all_agents_done():
             print(f"\n*** {SCENARIO_NAME} ENDED: All agents are done. ***")
             if engine.logger:
                engine.logger.log(engine.current_step, "SCENARIO_END", "scenario_logic", {"reason": "All agents done by environment state"})
             break
    else: 
        print(f"\n*** {SCENARIO_NAME} ENDED: Max steps ({max_steps}) reached. {artifacts_found_count}/{total_artifacts} artifacts found. ***")
        if engine.logger:
            engine.logger.log(engine.current_step, "SCENARIO_END", "scenario_logic", {"reason": "Max steps reached", "artifacts_found": artifacts_found_count})

    if engine.logger:
        engine.logger.close()
    print(f"--- Scenario: {SCENARIO_NAME} Finished ---")

if __name__ == "__main__":
    run_scenario(max_steps=200)

```
