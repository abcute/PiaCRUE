from .interfaces import (
    SimulationEngine,
    AgentInterface,
    PiaSEEvent,
    Environment,
    PerceptionData,
    ActionCommand,
    ActionResult,
)
from typing import Dict, List, Optional, Any
import time
from pathlib import Path

# Placeholder PiaSELogger if not yet implemented in utils
# from ..utils.logger import PiaSELogger # Adjusted path, use placeholder for now

class PiaSELogger:
    def __init__(self, log_file_path: Path, config: Optional[Dict] = None):
        self.log_file_path = log_file_path
        self.config = config or {}
        self._ensure_log_file_exists()
        print(f"Logger initialized for {self.log_file_path}")

    def _ensure_log_file_exists(self):
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        # For JSONL, just ensure path exists. File will be appended to.
        if not self.log_file_path.exists():
            self.log_file_path.touch()


import json # Added import for json

    def log(self, simulation_step: int, event_type: str, source_component: str, data: Dict, wall_time: Optional[float] = None):
        if wall_time is None:
            wall_time = time.time()

        log_entry = {
            "wall_time": wall_time,
            "simulation_step": simulation_step,
            "event_type": event_type,
            "source_component": source_component,
            "data": data
        }
        try:
            with open(self.log_file_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except NameError: # json not imported because this is a placeholder
             print(f"Placeholder Log: {log_entry}")
        except Exception as e:
            print(f"Error writing to log (placeholder): {e} - {log_entry}")


    def close(self):
        print(f"Logger closed for {self.log_file_path}")
        pass # Placeholder

class BasicSimulationEngine(SimulationEngine):
    """
    A basic implementation of the SimulationEngine.
    Manages the simulation loop, agent interactions, and logging.
    """
    def __init__(self):
        self.environment: Optional[Environment] = None
        self.agents: Dict[str, AgentInterface] = {}
        self.current_step: int = 0
        self.logger: Optional[PiaSELogger] = None
        self.scenario_config: Optional[Dict] = None
        print("BasicSimulationEngine initialized.")

    def initialize(
        self,
        environment: Environment,
        agents: Dict[str, AgentInterface],
        scenario_config: Optional[Dict] = None,
        log_path: str = "logs/simulation_log.jsonl",
    ):
        """Initializes the simulation environment, agents, and logger."""
        print("BasicSimulationEngine: Initializing...")
        self.environment = environment
        self.agents = agents
        self.scenario_config = scenario_config or {}
        self.current_step = 0

        # Instantiate Logger
        logger_config = self.scenario_config.get("logging_config", {})
        # Ensure log_path is correctly passed if overridden in scenario_config
        effective_log_path = logger_config.get("log_file_path", log_path)
        self.logger = PiaSELogger(log_file_path=Path(effective_log_path), config=logger_config)

        self.logger.log(
            self.current_step,
            "SIMULATION_START",
            "engine",
            {
                "scenario_name": self.scenario_config.get("name", "UnknownScenario"),
                "engine_config": self.__class__.__name__,
                "environment_config": self.environment.__class__.__name__,
                "num_agents": len(self.agents)
            },
        )

        # Environment and action space info logging
        try:
            env_info = self.environment.get_environment_info()
            self.logger.log(self.current_step, "ENVIRONMENT_INFO", "environment", env_info)
        except Exception as e:
            self.logger.log(self.current_step, "ERROR", "engine", {"message": f"Failed to get/log environment info: {e}"})

        # Agent initialization
        for agent_id, agent in self.agents.items():
            agent.set_id(agent_id)

            # Agent-specific configuration (e.g. Q-table init) should ideally be handled
            # by the agent itself upon receiving first perception or by the scenario script.
            # The engine provides initial perception.

            try:
                # Get agent-specific action space if method supports agent_id
                action_space_info = self.environment.get_action_space(agent_id=agent_id)
                self.logger.log(self.current_step, "AGENT_ACTION_SPACE", agent_id, {"action_space": action_space_info})
                 # Optional: if agent has a configure method
                if hasattr(agent, 'configure'):
                    agent.configure(env_info=env_info, action_space=action_space_info)

            except Exception as e:
                 self.logger.log(self.current_step, "ERROR", agent_id, {"message": f"Failed to get/log action_space or configure agent: {e}"})


            initial_observation = self.environment.get_observation(agent_id)
            self.logger.log(
                self.current_step, "AGENT_PERCEPTION", agent_id, initial_observation.model_dump()
            )
            agent.perceive(initial_observation)

            print(f"BasicSimulationEngine: Agent '{agent_id}' initialized and perceived initial state.")

        print("BasicSimulationEngine: Initialization complete.")

    def run_step(self):
        """Runs a single step of the simulation for all agents."""
        if not self.environment or not self.agents or not self.logger:
            print("BasicSimulationEngine: Engine not initialized. Skipping step.")
            return

        self.current_step += 1
        step_start_time = time.time()
        print(f"\nBasicSimulationEngine: --- Starting Step {self.current_step} ---")
        self.logger.log(self.current_step, "STEP_START", "engine", {"step_number": self.current_step})

        for agent_id, agent in self.agents.items():
            if self.environment.is_done(agent_id):
                # Log this only once or if status changes
                # self.logger.log(self.current_step, "AGENT_TASK_DONE_SKIP", agent_id, {"message": f"Agent {agent_id} already done."})
                continue

            agent_step_start_time = time.time()

            # Perception Phase
            observation = self.environment.get_observation(agent_id)
            self.logger.log(
                self.current_step, "AGENT_PERCEPTION", agent_id, observation.model_dump()
            )
            agent.perceive(observation)

            # Action Submission Phase
            action_command = agent.act()
            self.logger.log(
                self.current_step, "AGENT_ACTION", agent_id, action_command.model_dump()
            )

            # Environment Action Execution & State Update Phase
            action_result = self.environment.step(agent_id, action_command)
            self.logger.log(
                self.current_step, "ACTION_RESULT", agent_id, action_result.model_dump()
            )

            # Agent Feedback/Learning Phase
            agent.learn(action_result)

            # Immediate Consequence Perception (if any)
            if action_result.new_perception_snippet:
                agent.perceive(action_result.new_perception_snippet)
                self.logger.log(
                    self.current_step,
                    "AGENT_IMMEDIATE_PERCEPTION",
                    agent_id,
                    action_result.new_perception_snippet.model_dump(),
                )

            self.logger.log(self.current_step, "AGENT_STEP_TIMING", agent_id, {"duration_ms": (time.time() - agent_step_start_time) * 1000})

            if self.environment.is_done(agent_id):
                print(f"BasicSimulationEngine: Agent '{agent_id}' completed its task at step {self.current_step}.")
                self.logger.log(
                    self.current_step,
                    "AGENT_TASK_DONE",
                    agent_id,
                    {"message": f"Agent {agent_id} completed its task."},
                )

        # Optional: Log overall environment state (can be verbose)
        # env_state = self.environment.get_state()
        # self.logger.log(self.current_step, "ENVIRONMENT_STATE", "environment", {"state_summary": str(env_state)[:500]})

        self.logger.log(self.current_step, "STEP_END", "engine", {"step_number": self.current_step, "duration_ms": (time.time() - step_start_time) * 1000})
        print(f"BasicSimulationEngine: --- Step {self.current_step} Finished ---")

    def _are_all_agents_done(self) -> bool:
        if not self.environment: return True # Should not happen if initialized
        for agent_id in self.agents.keys():
            if not self.environment.is_done(agent_id):
                return False
        return True

    def run_simulation(self, num_steps: int):
        """Runs the simulation for a specified number of steps or until all agents are done."""
        if not self.logger:
            print("BasicSimulationEngine: Logger not initialized. Cannot run simulation.")
            return

        print(f"BasicSimulationEngine: Starting simulation run for {num_steps} steps.")
        self.logger.log(self.current_step, "SIMULATION_RUN_START", "engine", {"num_steps_configured": num_steps})

        for _ in range(num_steps):
            if self._are_all_agents_done():
                print("BasicSimulationEngine: All agents are done. Ending simulation early.")
                self.logger.log(self.current_step, "SIMULATION_END", "engine", {"reason": "all_agents_done", "total_steps": self.current_step})
                self.logger.close()
                return
            self.run_step()

        print(f"BasicSimulationEngine: Simulation finished after {self.current_step} steps (max steps reached: {num_steps}).")
        self.logger.log(self.current_step, "SIMULATION_END", "engine", {"reason": "num_steps_reached", "total_steps": self.current_step})
        self.logger.close()

    def post_event(self, event: PiaSEEvent, source: str = "external"):
        """Posts an event to all agents and logs it."""
        if not self.logger or not self.environment:
            print("BasicSimulationEngine: Engine not initialized. Cannot post event.")
            return

        print(f"BasicSimulationEngine: Event posted from '{source}': {event.event_type} - {event.data}")
        self.logger.log(self.current_step, "PIA_EVENT_POSTED", source, event.model_dump())

        for agent_id, agent in self.agents.items():
            if self.environment.is_done(agent_id): # Don't post events to done agents
                continue
            # Decide if fresh observation is needed with event. For now, providing current one.
            # This could be configurable or event-specific.
            current_observation = self.environment.get_observation(agent_id)
            # Log perception of event by agent
            self.logger.log(self.current_step, "AGENT_EVENT_PERCEPTION_START", agent_id, {"event_type": event.event_type})
            agent.perceive(observation=current_observation, event=event)
            self.logger.log(self.current_step, "AGENT_EVENT_PERCEPTION_END", agent_id, {"event_type": event.event_type})


    def get_environment_state(self) -> Optional[Any]:
        """Retrieves and logs a summary of the current state of the environment."""
        if not self.environment or not self.logger:
            print("BasicSimulationEngine: Engine not initialized. Cannot get environment state.")
            return None

        state = self.environment.get_state()
        # Log a summary to avoid overly large log entries by default
        state_summary = str(state)[:200] + "..." if len(str(state)) > 200 else str(state)
        self.logger.log(
            self.current_step,
            "GET_ENVIRONMENT_STATE",
            "engine_api",
            {"state_summary": state_summary},
        )
        return state

    def get_logger(self) -> Optional[PiaSELogger]:
        """Returns the logger instance."""
        return self.logger
