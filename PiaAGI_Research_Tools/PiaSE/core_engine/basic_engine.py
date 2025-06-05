from .interfaces import (
    SimulationEngine,
    AgentInterface,
    PiaSEEvent,
    Environment,
    PerceptionData,
    ActionCommand,
    ActionResult,
)
from typing import Dict, List, Optional, Any, Union # Added Union
import time
from pathlib import Path

try:
    from .dynamic_scenario_engine import (
        CurriculumManager,
        AdaptationDecisionModule,
        MockPiaAVTInterface, # Using Mock for now
        DevelopmentalCurriculum, # These might be DSE's local placeholders
        CurriculumStep
    )
    DSE_COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"BasicEngine: DSE components not found, DSE functionality will be disabled: {e}")
    DSE_COMPONENTS_AVAILABLE = False
    # Define placeholders if DSE components are not available, so engine can still parse
    class CurriculumManager: pass
    class AdaptationDecisionModule: pass
    class MockPiaAVTInterface: pass
    class DevelopmentalCurriculum: pass
    class CurriculumStep: pass


# Placeholder PiaSELogger if not yet implemented in utils
# from ..utils.logger import PiaSELogger # Adjusted path, use placeholder for now

class PiaSELogger: # Basic Logger provided in prompt
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
        self.current_step: int = 0 # Overall simulation step
        self.logger: Optional[PiaSELogger] = None
        self.scenario_config: Optional[Dict] = None

        # DSE related attributes
        self.curriculum_manager: Optional[CurriculumManager] = None
        self.adaptation_module: Optional[AdaptationDecisionModule] = None
        self.avt_interface: Optional[MockPiaAVTInterface] = None # Using Mock for now
        self.agent_curricula: Dict[str, str] = {} # agent_id -> curriculum_filepath
        self.dse_active_for_agents: Dict[str, bool] = {} # agent_id -> True if DSE is managing

        print("BasicSimulationEngine initialized.")

    def initialize(
        self,
        environment: Environment,
        agents: Dict[str, AgentInterface],
        scenario_config: Optional[Dict] = None,
        log_path: str = "logs/simulation_log.jsonl",
        agent_curricula: Optional[Dict[str, str]] = None # agent_id -> curriculum_filepath
    ):
        """Initializes the simulation environment, agents, logger, and DSE components if curricula are provided."""
        print("BasicSimulationEngine: Initializing...")
        self.environment = environment
        self.agents = agents
        self.scenario_config = scenario_config if scenario_config else {}
        self.current_step = 0

        logger_config = self.scenario_config.get("logging_config", {})
        effective_log_path = logger_config.get("log_file_path", log_path) 
        self.logger = PiaSELogger(log_file_path=Path(effective_log_path), config=logger_config)
        
        self.log_event("SIMULATION_START", "engine", {
            "scenario_name": self.scenario_config.get("name", "UnknownScenario"),
            "engine_config": self.__class__.__name__,
            "environment_config": self.environment.__class__.__name__,
            "num_agents": len(self.agents)
        })

        try:
            env_info = self.environment.get_environment_info()
            self.log_event("ENVIRONMENT_INFO", "environment", env_info)
        except Exception as e:
            self.log_event("ERROR", "engine", {"message": f"Failed to get/log environment info: {e}"})

        for agent_id, agent in self.agents.items():
            agent.set_id(agent_id)
            try:
                action_space_info = self.environment.get_action_space(agent_id=agent_id)
                self.log_event("AGENT_ACTION_SPACE", agent_id, {"action_space": action_space_info})
                if hasattr(agent, 'configure'): # Optional configure method on agent
                    agent.configure(env_info=env_info if 'env_info' in locals() else {}, action_space=action_space_info)
            except Exception as e:
                 self.log_event("ERROR", agent_id, {"message": f"Failed to get/log action_space or configure agent: {e}"})

            # DSE Initialization for this agent
            if DSE_COMPONENTS_AVAILABLE and agent_curricula and agent_id in agent_curricula:
                if not self.curriculum_manager: # Initialize DSE components on first use
                    self.curriculum_manager = CurriculumManager()
                    self.avt_interface = MockPiaAVTInterface() # Replace with real one when ready
                    self.adaptation_module = AdaptationDecisionModule(self.avt_interface)

                self.agent_curricula[agent_id] = agent_curricula[agent_id]
                self.dse_active_for_agents[agent_id] = True

                if self.curriculum_manager.load_curriculum_from_file(self.agent_curricula[agent_id]):
                    self.curriculum_manager.initialize_agent_progress(agent_id)
                    first_step = self.curriculum_manager.get_next_step(agent_id) # Should get the very first step
                    if first_step:
                        self.curriculum_manager.set_current_step(agent_id, first_step.order, increment_attempt=False) # Sets attempts to 0 for first time
                        self.log_event("DSE_AGENT_CURRICULUM_START", agent_id, {
                            "curriculum_name": self.curriculum_manager.current_curriculum.name,
                            "first_step_name": first_step.name,
                            "first_step_order": first_step.order
                        })
                        # Conceptual: Apply first_step.agent_config_overrides or prompt to agent here
                        # Conceptual: Apply first_step.environment_config_overrides to environment here
                        print(f"DSE: Agent '{agent_id}' starting curriculum '{self.curriculum_manager.current_curriculum.name}' at step '{first_step.name}'.")
                    else:
                        self.log_event("DSE_ERROR", agent_id, {"message": "Failed to get first curriculum step."})
                        self.dse_active_for_agents[agent_id] = False # Disable DSE for this agent if first step fails
                else:
                    self.log_event("DSE_ERROR", agent_id, {"message": f"Failed to load curriculum: {self.agent_curricula[agent_id]}"})
                    self.dse_active_for_agents[agent_id] = False # Disable DSE if curriculum load fails
            else:
                self.dse_active_for_agents[agent_id] = False # Agent not managed by DSE

            # Initial perception for all agents
            initial_observation = self.environment.get_observation(agent_id)
            self.log_event("AGENT_PERCEPTION", agent_id, initial_observation.model_dump() if hasattr(initial_observation, 'model_dump') else initial_observation)
            agent.perceive(initial_observation)
            print(f"BasicSimulationEngine: Agent '{agent_id}' initialized. DSE Active: {self.dse_active_for_agents[agent_id]}")

        print("BasicSimulationEngine: Initialization complete.")


    def _run_agent_env_interaction_step(self, agent_id: str, agent: AgentInterface):
        """Runs a single environment interaction step for a given agent."""
        if self.environment.is_done(agent_id): # Check if env thinks agent is done for this interaction round
            return

        agent_step_start_time = time.time()
        observation = self.environment.get_observation(agent_id)
        self.log_event("AGENT_PERCEPTION", agent_id, observation.model_dump() if hasattr(observation, 'model_dump') else observation)
        agent.perceive(observation)

        action_command = agent.act()
        self.log_event("AGENT_ACTION", agent_id, action_command.model_dump() if hasattr(action_command, 'model_dump') else action_command)

        action_result = self.environment.step(agent_id, action_command)
        self.log_event("ACTION_RESULT", agent_id, action_result.model_dump() if hasattr(action_result, 'model_dump') else action_result)
        
        agent.learn(action_result)

        if action_result.new_perception_snippet:
            agent.perceive(action_result.new_perception_snippet)
            self.log_event("AGENT_IMMEDIATE_PERCEPTION", agent_id, action_result.new_perception_snippet.model_dump() if hasattr(action_result.new_perception_snippet, 'model_dump') else action_result.new_perception_snippet)

        self.log_event("AGENT_ENV_INTERACTION_TIMING", agent_id, {"duration_ms": (time.time() - agent_step_start_time) * 1000})


    def run_simulation(self, num_steps: int):
        """Runs the simulation, managing DSE lifecycle for relevant agents."""
        if not self.logger or not self.environment:
            print("BasicSimulationEngine: Engine not initialized. Cannot run simulation.")
            return
            
        self.log_event("SIMULATION_RUN_START", "engine", {"num_steps_configured": num_steps})
        print(f"BasicSimulationEngine: Starting simulation run for {num_steps} overall steps.")

        for i_step in range(num_steps):
            self.current_step = i_step + 1 # Global step counter
            step_start_time = time.time()
            self.log_event("GLOBAL_STEP_START", "engine", {"step_number": self.current_step})
            print(f"\nBasicSimulationEngine: --- Global Step {self.current_step} ---")

            all_agents_finished_curricula = True # Assume true until a DSE agent is found active

            for agent_id, agent in self.agents.items():
                if self.dse_active_for_agents.get(agent_id) and self.curriculum_manager and self.adaptation_module:
                    all_agents_finished_curricula = False # Found an active DSE agent
                    current_step_obj = self.curriculum_manager.get_current_step_object(agent_id)

                    if not current_step_obj:
                        self.log_event("DSE_AGENT_CURRICULUM_COMPLETE", agent_id, {"message": "No more steps in curriculum."})
                        self.dse_active_for_agents[agent_id] = False # Mark as inactive for DSE
                        print(f"DSE: Agent {agent_id} has completed all curriculum steps.")
                        continue # Move to next agent

                    self.log_event("DSE_STEP_ATTEMPT_START", agent_id, {
                        "step_name": current_step_obj.name,
                        "step_order": current_step_obj.order,
                        "attempt_count": self.curriculum_manager.get_step_attempts(agent_id, current_step_obj.order)
                    })
                    print(f"DSE: Agent {agent_id} attempting step '{current_step_obj.name}' (Order: {current_step_obj.order}, Attempt: {self.curriculum_manager.get_step_attempts(agent_id, current_step_obj.order)})")

                    # Conceptual: Configure agent/env based on current_step_obj overrides
                    # self.scenario_setup_module.configure_for_step(agent, self.environment, current_step_obj)
                    # For MVP, this is simplified; agent/env are mostly configured at scenario start.

                    # --- Environment Reconfiguration for DSE Step ---
                    environment_config = getattr(current_step_obj, 'environment_config', None)
                    if environment_config and isinstance(environment_config, dict) and environment_config:
                        self.log_event("DSE_ENV_RECONFIG_START", agent_id, {"step_name": current_step_obj.name, "config_keys": list(environment_config.keys())})
                        print(f"DSE: Agent {agent_id} attempting environment reconfiguration for step '{current_step_obj.name}'.")
                        try:
                            reconfigure_success = self.environment.reconfigure(environment_config)
                            self.log_event("DSE_ENV_RECONFIG_RESULT", agent_id, {"step_name": current_step_obj.name, "success": reconfigure_success})
                            if not reconfigure_success:
                                print(f"DSE Warning: Environment reconfiguration failed for agent {agent_id} at step '{current_step_obj.name}'. Proceeding with previous environment state.")
                                self.log_event("DSE_ENV_RECONFIG_FAILED", agent_id, {"step_name": current_step_obj.name, "message": "Environment.reconfigure() returned False."})
                            else:
                                print(f"DSE: Environment successfully reconfigured for agent {agent_id}, step '{current_step_obj.name}'.")
                        except Exception as e_reconfig:
                            print(f"DSE Error: Exception during environment reconfiguration for agent {agent_id}, step '{current_step_obj.name}': {e_reconfig}")
                            self.log_event("DSE_ENV_RECONFIG_ERROR", agent_id, {"step_name": current_step_obj.name, "error": str(e_reconfig)})
                            # Decide if this is a critical failure or if the simulation can proceed with old env state.
                            # For now, proceed with old state and log error.

                    # --- Agent Reconfiguration for DSE Step ---
                    agent_config = getattr(current_step_obj, 'agent_config_overrides', None)
                    if agent_config and isinstance(agent_config, dict) and agent_config:
                        self.log_event("DSE_AGENT_RECONFIG_START", agent_id, {"step_name": current_step_obj.name, "config_keys": list(agent_config.keys())})
                        print(f"DSE: Agent {agent_id} attempting agent reconfiguration for step '{current_step_obj.name}'.")
                        if hasattr(agent, 'configure') and callable(getattr(agent, 'configure')):
                            try:
                                agent.configure(config=agent_config) # Pass the config dictionary
                                self.log_event("DSE_AGENT_RECONFIG_APPLIED", agent_id, {"step_name": current_step_obj.name})
                                print(f"DSE: Agent {agent_id} configuration applied for step '{current_step_obj.name}'.")
                            except Exception as e_agent_reconfig:
                                print(f"DSE Error: Exception during agent reconfiguration for agent {agent_id}, step '{current_step_obj.name}': {e_agent_reconfig}")
                                self.log_event("DSE_AGENT_RECONFIG_ERROR", agent_id, {"step_name": current_step_obj.name, "error": str(e_agent_reconfig)})
                        else:
                            self.log_event("DSE_AGENT_RECONFIG_SKIP", agent_id, {"step_name": current_step_obj.name, "reason": "Agent has no callable 'configure' method."})
                            print(f"DSE Warning: Agent {agent_id} has no 'configure' method. Skipping agent reconfiguration for step '{current_step_obj.name}'.")

                    # Inner loop for environment interactions for this curriculum step attempt
                    # Max interactions for this attempt, e.g. from current_step_obj.max_duration or a default
                    max_interactions_for_attempt = getattr(current_step_obj, 'max_interactions', 1) # Default to 1 interaction if not specified

                    for _interaction_num in range(max_interactions_for_attempt):
                        if self.environment.is_done(agent_id): # If env says task for this step is done (e.g. goal reached)
                            self.log_event("DSE_STEP_ENV_DONE", agent_id, {"step_name": current_step_obj.name, "message": "Environment signaled task completion for step."})
                            break
                        self._run_agent_env_interaction_step(agent_id, agent)

                    # Mock AVT data update (replace with real integration)
                    if self.avt_interface and isinstance(self.avt_interface, MockPiaAVTInterface):
                        # Example: mock task success based on if agent is at goal in GridWorld
                        if hasattr(self.environment, 'agent_pos') and hasattr(self.environment, 'goal_pos'):
                            if getattr(self.environment, 'agent_pos') == getattr(self.environment, 'goal_pos'):
                                self.avt_interface.set_metric(agent_id, "task_success", 1)
                            else:
                                self.avt_interface.set_metric(agent_id, "task_success", 0)
                        else: # Default mock for other envs
                             self.avt_interface.set_metric(agent_id, "task_success", 1) # Assume success for testing flow

                    is_complete = self.adaptation_module.evaluate_step_completion(agent_id, current_step_obj)
                    decision_context = "COMPLETED" if is_complete else "NOT_COMPLETED"

                    if is_complete:
                        self.curriculum_manager.complete_step(agent_id, current_step_obj.order)
                        decision = "PROCEED"
                        self.log_event("DSE_STEP_COMPLETED", agent_id, {"step_name": current_step_obj.name, "step_order": current_step_obj.order})
                    else:
                        attempt_count = self.curriculum_manager.get_step_attempts(agent_id, current_step_obj.order)
                        decision = self.adaptation_module.evaluate_adaptation_rules(agent_id, current_step_obj, attempt_count)
                        self.log_event("DSE_ADAPTATION_EVAL", agent_id, {"step_name": current_step_obj.name, "attempt_count": attempt_count, "decision": decision})

                    print(f"DSE: Decision for agent {agent_id} on step '{current_step_obj.name}' (Context: {decision_context}): {decision}")

                    if decision == "PROCEED":
                        next_step_obj = self.curriculum_manager.get_next_step(agent_id)
                        if next_step_obj:
                            self.curriculum_manager.set_current_step(agent_id, next_step_obj.order)
                        else: # No next step, curriculum finished for this agent
                            self.dse_active_for_agents[agent_id] = False
                            self.log_event("DSE_AGENT_CURRICULUM_FINISHED", agent_id, {"curriculum_name": self.curriculum_manager.current_curriculum.name})
                            print(f"DSE: Agent {agent_id} finished curriculum.")
                    elif "BRANCH_TO_" in decision:
                        try:
                            target_identifier = decision.split("BRANCH_TO_")[-1]
                            # Try converting to int for order, else assume it's a name
                            try: target_identifier = int(target_identifier)
                            except ValueError: pass

                            branch_step = self.curriculum_manager.get_step_by_name_or_order(target_identifier)
                            if branch_step:
                                self.curriculum_manager.set_current_step(agent_id, branch_step.order)
                            else:
                                self.log_event("DSE_ERROR", agent_id, {"message": f"Branch target step '{target_identifier}' not found."})
                                self.dse_active_for_agents[agent_id] = False # Halt DSE for this agent
                        except Exception as e:
                             self.log_event("DSE_ERROR", agent_id, {"message": f"Error processing BRANCH_TO decision '{decision}': {e}"})
                             self.dse_active_for_agents[agent_id] = False
                    elif decision == "REPEAT_STEP":
                        self.curriculum_manager.set_current_step(agent_id, current_step_obj.order, increment_attempt=True) # Stays on same step, increments attempt
                        self.log_event("DSE_REPEAT_STEP", agent_id, {"step_name": current_step_obj.name})
                        # Conceptual: ScenarioSetupModule.apply_modifications if decision was REPEAT_MODIFIED
                    elif "APPLY_HINT" in decision:
                         self.log_event("DSE_APPLY_HINT", agent_id, {"step_name": current_step_obj.name, "hint_action": decision})
                         # Conceptual: Hint application logic. Agent might retry or environment might change.
                         # For MVP, just log and agent re-attempts current step.
                         self.curriculum_manager.set_current_step(agent_id, current_step_obj.order, increment_attempt=True)
                    elif decision == "FAIL_CURRICULUM":
                        self.log_event("DSE_CURRICULUM_FAILED", agent_id, {"curriculum_name": self.curriculum_manager.current_curriculum.name, "step_name": current_step_obj.name})
                        self.dse_active_for_agents[agent_id] = False # Stop DSE for this agent
                        print(f"DSE: Agent {agent_id} failed curriculum at step '{current_step_obj.name}'.")
                    else: # Unknown decision
                        self.log_event("DSE_UNKNOWN_DECISION", agent_id, {"decision": decision, "step_name": current_step_obj.name})
                        self.dse_active_for_agents[agent_id] = False # Halt on unknown
                else: # Non-DSE managed agent
                    all_agents_finished_curricula = False # If any non-DSE agent is still active
                    if not self.environment.is_done(agent_id):
                         self._run_agent_env_interaction_step(agent_id, agent)
                    else:
                        self.log_event("AGENT_TASK_DONE_SKIP", agent_id, {"message": "Agent already done (non-DSE check)."})


            self.log_event("GLOBAL_STEP_END", "engine", {"step_number": self.current_step, "duration_ms": (time.time() - step_start_time) * 1000})
            print(f"BasicSimulationEngine: --- Global Step {self.current_step} Finished ---")

            if self._are_all_agents_done_for_simulation(all_agents_finished_curricula):
                print("BasicSimulationEngine: All agents are done (or curricula complete). Ending simulation early.")
                self.log_event("SIMULATION_END", "engine", {"reason": "all_agents_done_or_curricula_complete", "total_steps": self.current_step})
                if self.logger: self.logger.close()
                return
        
        print(f"BasicSimulationEngine: Simulation finished after {self.current_step} global steps (max steps: {num_steps} reached).")
        self.log_event("SIMULATION_END", "engine", {"reason": "num_global_steps_reached", "total_steps": self.current_step})
        if self.logger: self.logger.close()

    def _are_all_agents_done_for_simulation(self, all_dse_agents_finished_curricula: bool) -> bool:
        if not self.environment: return True

        # If there are any DSE agents still active in their curricula, simulation is not done from DSE perspective
        if any(self.dse_active_for_agents.get(aid) for aid in self.agents.keys()):
            return False # At least one DSE agent is still actively progressing in a curriculum

        # If all DSE agents have finished their curricula (or no DSE agents exist),
        # then check the environment's perspective for non-DSE agents.
        if all_dse_agents_finished_curricula:
            for agent_id in self.agents.keys():
                if not self.dse_active_for_agents.get(agent_id): # Only check non-DSE agents here
                    if not self.environment.is_done(agent_id):
                        return False # A non-DSE agent is not done
            return True # All non-DSE agents are also done, or no non-DSE agents

        return False # Default: if not all DSE agents finished curricula, keep going


    def post_event(self, event: PiaSEEvent, source: str = "external"):
        """Posts an event to all agents and logs it."""
        # Simplified logging method within the class
        self.log_event(event_type=event.event_type, source_component=source, data=event.model_dump() if hasattr(event, 'model_dump') else event)

        if not self.environment:
            print("BasicSimulationEngine: Environment not initialized. Cannot post event to agents.")
            return

        for agent_id, agent in self.agents.items():
            if self.dse_active_for_agents.get(agent_id): # If DSE agent, is it done with curriculum?
                if not self.curriculum_manager.get_current_step_object(agent_id): # No current step means curriculum done
                    continue
            elif self.environment.is_done(agent_id): # Non-DSE agent check
                continue

            current_observation = self.environment.get_observation(agent_id)
            self.log_event("AGENT_EVENT_PERCEPTION_START", agent_id, {"event_type": event.event_type})
            agent.perceive(observation=current_observation, event=event)
            self.log_event("AGENT_EVENT_PERCEPTION_END", agent_id, {"event_type": event.event_type})

    def log_event(self, event_type: str, source_component: str, data: Dict, agent_id_for_log: Optional[str] = None):
        """Helper method to log events, using current_step."""
        if not self.logger: return

        # If data is a Pydantic model, dump it. Otherwise, assume it's a dict.
        log_data = data
        if hasattr(data, 'model_dump') and callable(data.model_dump):
            try:
                log_data = data.model_dump()
            except Exception: # Keep original if model_dump fails for some reason
                log_data = str(data) # Fallback to string

        # For AGENT_* events, source_component is usually the agent_id.
        # For engine/environment events, it's 'engine' or 'environment'.
        # This method standardizes that.
        effective_source = agent_id_for_log if agent_id_for_log else source_component

        self.logger.log(
            simulation_step=self.current_step,
            event_type=event_type,
            source_component=effective_source,
            data=log_data
        )

    def get_environment_state(self) -> Optional[Any]:
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
        if not self.environment:
            print("BasicSimulationEngine: Environment not initialized.")
            return None
        state = self.environment.get_state()
        self.log_event("GET_ENVIRONMENT_STATE", "engine_api", {"state_summary": str(state)[:500]}) # Max 500 chars for summary
        return state

    def get_logger(self) -> Optional[PiaSELogger]:
        return self.logger
