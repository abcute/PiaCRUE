from abc import ABC, abstractmethod
from dataclasses import dataclass
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union, ByteString # Added ByteString for bytes

class BaseDataModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True

# New Percept Types
class VisualPercept(BaseDataModel):
    image_url: Optional[str] = None
    raw_image_data: Optional[bytes] = None # Changed from ByteString to bytes
    detected_objects: Optional[List[Dict[str, Any]]] = None

class AuditoryPercept(BaseDataModel):
    sound_url: Optional[str] = None
    raw_sound_data: Optional[bytes] = None # Changed from ByteString to bytes
    transcribed_text: Optional[str] = None
    speaker_id: Optional[str] = None

class TextualPercept(BaseDataModel):
    text: str
    source: Optional[str] = None

class PerceptionData(BaseDataModel):
    timestamp: float
    visual_percepts: Optional[List[VisualPercept]] = None
    auditory_percepts: Optional[List[AuditoryPercept]] = None
    textual_percepts: Optional[List[TextualPercept]] = None
    custom_sensor_data: Dict[str, Any] = Field(default_factory=dict) # Renamed from sensor_data
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    agent_specific_data: Optional[Dict[str, Any]] = None

class ActionCommand(BaseDataModel):
    action_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)

class ActionResult(BaseDataModel):
    timestamp: float
    status: str  # e.g., "success", "failure", "pending"
    new_perception_snippet: Optional[PerceptionData] = None # Optional immediate perception update after action
    message: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict) # e.g., {"energy_consumed": 0.1, "reward_received": 10}

class PiaSEEvent(BaseDataModel): # Changed from @dataclass
    event_type: str
    data: Dict[str, Any] = Field(default_factory=dict)
    source_id: Optional[str] = None # Optional: Who generated the event
    target_id: Optional[str] = None # Optional: Specific agent/entity this event is for

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
    def step(self, agent_id: str, action: ActionCommand) -> ActionResult:
        """
        Processes an agent's action and updates the environment state.
        Returns the result of the action, e.g., new observation, reward.
        """
        pass

    @abstractmethod
    def get_observation(self, agent_id: str) -> PerceptionData:
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
    def get_action_space(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Gets the description of possible actions in the environment, potentially specific to an agent.
        Returns a dictionary where keys are action names and values describe parameters.
        """
        pass

    @abstractmethod
    def get_environment_info(self) -> Dict[str, Any]:
        """
        Provides general information about the environment setup.
        This can include environment name, description, action schema, perception schema, etc.
        (Ref: PiaAGI_Simulation_Environment.md for conceptual details)
        """
        pass

    @abstractmethod
    def reconfigure(self, config: Dict[str, Any]) -> bool:
        """
        Reconfigures the environment based on the provided configuration dictionary.
        This allows for dynamic changes to the environment's parameters, layout,
        or other characteristics during a simulation run, often guided by a
        Dynamic Scenario Engine (DSE) or a curriculum.

        Args:
            config (Dict[str, Any]): A dictionary containing the configuration parameters
                                     to apply. The specific keys and values expected
                                     will depend on the concrete environment implementation.

        Returns:
            bool: True if the reconfiguration was successful and applied, False otherwise.
        """
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
    def perceive(self, observation: PerceptionData, event: Optional[PiaSEEvent] = None): # Optional[PiaSEEvent]
        """
        Provides the agent with an observation from the environment and optional events.
        """
        pass

    @abstractmethod
    def act(self) -> ActionCommand:
        """
        Allows the agent to decide on an action based on its current state/perception.
        Returns the action to be performed in the environment.
        """
        pass

    @abstractmethod
    def learn(self, feedback: ActionResult):
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
