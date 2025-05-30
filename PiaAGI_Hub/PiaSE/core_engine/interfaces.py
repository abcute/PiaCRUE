from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class PiaSEEvent:
    """A generic event within the PiaSE simulation."""
    # Add specific event fields as needed, e.g., event_type, data
    pass

class SimulationEngine(ABC):
    """
    Abstract base class for a simulation engine.
    Defines the core lifecycle and interaction points of the simulation.
    """
    @abstractmethod
    def initialize(self, **kwargs):
        """Initializes the simulation engine and its components."""
        pass

    @abstractmethod
    def run_step(self):
        """Runs a single step or tick of the simulation."""
        pass

    @abstractmethod
    def run_simulation(self, num_steps: int):
        """Runs the simulation for a specified number of steps."""
        pass

    @abstractmethod
    def register_agent(self, agent_id: str, agent: 'AgentInterface'):
        """Registers an agent with the simulation engine."""
        pass

    @abstractmethod
    def post_event(self, event: PiaSEEvent):
        """Posts an event to the simulation, potentially affecting agents or the environment."""
        pass

    @abstractmethod
    def get_environment_state(self):
        """Retrieves the current state of the environment."""
        pass

class Environment(ABC):
    """
    Abstract base class for a simulation environment.
    Defines how agents interact with and perceive the simulated world.
    """
    @abstractmethod
    def reset(self):
        """Resets the environment to its initial state."""
        pass

    @abstractmethod
    def step(self, agent_id: str, action: any):
        """
        Processes an agent's action and updates the environment state.
        Returns the result of the action, e.g., new observation, reward.
        """
        pass

    @abstractmethod
    def get_observation(self, agent_id: str) -> any:
        """Gets the observation for a specific agent."""
        pass

    @abstractmethod
    def get_state(self) -> any:
        """Gets the overall current state of the environment."""
        pass

    @abstractmethod
    def is_done(self, agent_id: str) -> bool:
        """Checks if the simulation or the agent's task is completed."""
        pass

    @abstractmethod
    def get_action_space(self) -> list:
        """Gets the list of possible actions in the environment."""
        pass

class AgentInterface(ABC):
    """
    Abstract base class for an agent.
    Defines the core capabilities of an agent operating within the simulation.
    """
    @abstractmethod
    def set_id(self, agent_id: str):
        """Sets the unique identifier for the agent."""
        pass

    @abstractmethod
    def get_id(self) -> str:
        """Gets the unique identifier for the agent."""
        pass

    @abstractmethod
    def perceive(self, observation: any, event: PiaSEEvent = None):
        """
        Provides the agent with an observation from the environment and optional events.
        """
        pass

    @abstractmethod
    def act(self) -> any:
        """
        Allows the agent to decide on an action based on its current state/perception.
        Returns the action to be performed in the environment.
        """
        pass

    @abstractmethod
    def learn(self, feedback: any):
        """
        Allows the agent to learn from feedback received after an action.
        (e.g., reward, new state information)
        """
        pass

    @abstractmethod
    def initialize_q_table(self, state: any, action_space: list):
        """Initializes or re-initializes the Q-table for the agent."""
        pass

    @abstractmethod
    def get_q_value(self, state: any, action: any) -> float:
        """Retrieves the Q-value for a given state-action pair."""
        pass

    @abstractmethod
    def update_q_value(self, state: any, action: any, reward: float, next_state: any, learning_rate: float, discount_factor: float, action_space: list):
        """Updates the Q-value for a state-action pair using the Q-learning formula."""
        pass
