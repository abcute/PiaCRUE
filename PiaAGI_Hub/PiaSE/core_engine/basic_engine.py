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
        """Initializes the simulation environment."""
        print(f"BasicSimulationEngine: Initializing environment with kwargs: {kwargs}")
        self.environment.reset()
        # Potentially initialize agents if needed, or they are initialized externally
        print("BasicSimulationEngine: Environment reset.")

    def register_agent(self, agent_id: str, agent: AgentInterface):
        """Registers an agent with the simulation engine."""
        if agent_id in self.agents:
            print(f"BasicSimulationEngine: Warning - Agent with ID '{agent_id}' already registered. Overwriting.")
        agent.set_id(agent_id)
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
            # Assuming step might return observation, reward, done, info or just affect the state
            feedback = self.environment.step(agent_id, action)
            print(f"BasicSimulationEngine: Environment feedback for agent '{agent_id}': {feedback}")

            # 4. Agent learns from feedback (optional)
            if feedback is not None: # Agent might not always get direct feedback to learn from
                agent.learn(feedback)

            # Check if agent is done after the step
            if self.environment.is_done(agent_id):
                print(f"BasicSimulationEngine: Agent '{agent_id}' finished its task in this step.")
        
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
