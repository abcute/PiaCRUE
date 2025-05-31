from .interfaces import SimulationEngine, AgentInterface, PiaSEEvent, Environment

class BasicSimulationEngine(SimulationEngine):
    """
    A basic implementation of the SimulationEngine.
    Manages the simulation loop and agent interactions.
    """
    def __init__(self, environment: Environment):
        self.environment = environment
        self.agents: dict[str, AgentInterface] = {}
        print(f"BasicSimulationEngine initialized with environment: {environment}")

    def initialize(self, **kwargs):
        """Initializes the simulation environment and all registered agents."""
        print(f"BasicSimulationEngine: Initializing environment with kwargs: {kwargs}")
        self.environment.reset() # Resets env and agent positions defined in env.
        print("BasicSimulationEngine: Environment reset.")

        action_space = self.environment.get_action_space()
        if not action_space:
            print("BasicSimulationEngine: Warning - Environment returned an empty action space.")
            # Depending on policy, agents might require a non-empty action space.

        for agent_id, agent in self.agents.items():
            # agent.set_id(agent_id) # ID is set during registration

            # Get initial observation for the agent
            # GridWorld get_observation returns a dict: {"agent_position": ..., "grid_view": ...}
            initial_observation_full = self.environment.get_observation(agent_id)

            # QLearningAgent uses a simplified state representation (e.g., agent_position)
            # for its Q-table keys. Other agents might use the full observation.
            # We need a consistent way to get the "state representation" for the Q-table.
            # For now, assuming QLearningAgent's perceive method handles the full observation
            # and extracts what it needs for self.current_state to be used as Q-table key.
            # The QLearningAgent's initialize_q_table uses the state representation directly.
            # Let's assume the agent's perceive method correctly sets up its internal state.

            agent.perceive(initial_observation_full) # Agent perceives its initial state S
                                                     # QLearningAgent's perceive will set self.current_state
                                                     # and initialize Q-table for this state if action_space is known.

            if hasattr(agent, 'initialize_q_table'):
                # The state representation for Q-table keys in our QLearningAgent is self.current_state
                # which is set by perceive().
                # So, we pass self.current_state (which should be the hashable part of initial_observation_full)
                # and the action_space.
                # QLearningAgent's perceive makes self.current_state = observation.
                # If observation is a dict, this might not be hashable.
                # Let's refine QLearningAgent's perceive to store a hashable state,
                # or ensure initial_observation_for_q_table is the hashable part.

                # For GridWorld, the observation is {'agent_position': (x,y), 'grid_view': grid}
                # The Q-table should use the hashable 'agent_position' tuple as state.
                initial_state_repr_for_q_table = initial_observation_full.get("agent_position")
                if initial_state_repr_for_q_table is None:
                     print(f"Warning: Could not derive a simple state representation (e.g. agent_position) for agent {agent_id} from observation {initial_observation_full}")
                     # Fallback or error, for now, Q-agent might handle it if it uses the whole dict and it's made hashable
                     initial_state_repr_for_q_table = tuple(sorted(initial_observation_full.items()))


                # Ensure agent.action_space is set before initializing Q-table for a state
                if hasattr(agent, 'action_space'): # QLearningAgent has this attribute
                    agent.action_space = action_space

                agent.initialize_q_table(initial_state_repr_for_q_table, action_space)
                print(f"BasicSimulationEngine: Initialized Q-table for agent '{agent_id}' with state {initial_state_repr_for_q_table} and action_space {action_space}")

            print(f"BasicSimulationEngine: Agent '{agent_id}' perceived initial state: {initial_observation_full}")

        print("BasicSimulationEngine: All agents initialized and perceived initial state.")


    def register_agent(self, agent_id: str, agent: AgentInterface):
        """Registers an agent with the simulation engine."""
        if agent_id in self.agents:
            print(f"BasicSimulationEngine: Warning - Agent with ID '{agent_id}' already registered. Overwriting.")
        agent.set_id(agent_id) # Set agent's ID
        self.agents[agent_id] = agent
        print(f"BasicSimulationEngine: Agent '{agent_id}' registered.")

    def run_step(self):
        """Runs a single step of the simulation."""
        if not self.agents:
            print("BasicSimulationEngine: No agents registered. Skipping step.")
            return

        print("\nBasicSimulationEngine: --- Starting new simulation step ---")
        for agent_id, agent in self.agents.items():
            if self.environment.is_done(agent_id):
                print(f"BasicSimulationEngine: Agent '{agent_id}' is done. Skipping.")
                continue

            # 1. Get observation for the agent
            observation = self.environment.get_observation(agent_id)
            print(f"BasicSimulationEngine: Providing observation to agent '{agent_id}': {observation}")
            agent.perceive(observation)

            # 2. Agent acts
            action = agent.act()
            print(f"BasicSimulationEngine: Agent '{agent_id}' performs action: {action}")

            # 3. Environment processes action and returns feedback/result
            # Assuming step now returns: new_observation, reward, done, info
            new_observation, reward, done, info = self.environment.step(agent_id, action)
            print(f"BasicSimulationEngine: Env step for agent '{agent_id}': Action: {action}, Reward: {reward}, Done: {done}")
            print(f"BasicSimulationEngine: New observation for agent '{agent_id}': {new_observation}")


            # 4. Agent learns from feedback (reward and new_observation)
            # The QLearningAgent expects feedback as (reward, next_state)
            # Other agents might have different learn signatures or just pass.
            agent.learn((reward, new_observation)) # Pass as a tuple

            # 5. Agent perceives the new state for the next iteration.
            # The event parameter is None here; events are handled by post_event.
            agent.perceive(new_observation, None)


            # Check if agent is done after the step
            if done: # Using 'done' from env.step()
                print(f"BasicSimulationEngine: Agent '{agent_id}' has completed its task.")
                # Optionally, handle agent removal or marking as inactive here.
                # For now, the simulation continues, and is_done() will prevent further actions if implemented correctly.

        print("BasicSimulationEngine: --- Simulation step finished ---")


    def run_simulation(self, num_steps: int):
        """Runs the simulation for a specified number of steps."""
        print(f"BasicSimulationEngine: Starting simulation for {num_steps} steps.")
        for step_num in range(num_steps):
            print(f"\nBasicSimulationEngine: === Running step {step_num + 1}/{num_steps} ===")
            self.run_step()
            # Potentially add a check here if all agents are done or simulation needs to end early
        print(f"BasicSimulationEngine: Simulation finished after {num_steps} steps.")

    def post_event(self, event: PiaSEEvent):
        """Posts an event to the simulation. For now, just prints it."""
        print(f"BasicSimulationEngine: Event posted: {event}")
        # Future: This could involve routing the event to specific agents
        # or modifying the environment directly.
        for agent in self.agents.values():
            # Assuming all agents might be interested in all events for now
            # A more sophisticated system would filter events based on agent subscriptions
            agent.perceive(observation=None, event=event)

    def get_environment_state(self):
        """Retrieves the current state of the environment."""
        print("BasicSimulationEngine: Retrieving environment state.")
        return self.environment.get_state()
