import random
from typing import List, Tuple, Dict, Optional, Any
# Adjusted import path
from PiaAGI_Research_Tools.PiaSE.core_engine.interfaces import AgentInterface, PerceptionData, ActionCommand, ActionResult, PiaSEEvent

class QLearningAgent(AgentInterface):
    def __init__(self,
                 learning_rate: float = 0.1,
                 discount_factor: float = 0.9,
                 exploration_rate: float = 0.1,
                 default_q_value: float = 0.0):
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = exploration_rate
        self.default_q = default_q_value
        self.q_table: Dict[Any, Dict[str, float]] = {} # Action type is str
        self.agent_id: Optional[str] = None
        
        self.current_state: Optional[Any] = None # Hashable representation of current environment state
        self.previous_state: Optional[Any] = None # Hashable representation of previous environment state
        
        self.action_space: List[str] = [] # List of action strings e.g. ["up", "down"]
        self.last_action: Optional[str] = None # The action_type string

    def set_id(self, agent_id: str):
        self.agent_id = agent_id

    def get_id(self) -> Optional[str]:
        return self.agent_id

    def initialize_q_table(self, state: Any, action_space: List[str]):
        self.action_space = action_space 
        if state not in self.q_table:
            self.q_table[state] = {action: self.default_q for action in self.action_space}

    def get_q_value(self, state: Any, action: str) -> float:
        if state not in self.q_table:
            if not self.action_space:
                 print(f"Warning: QLearningAgent {self.agent_id}: get_q_value called for state {state} but agent's action_space is not set. Returning default Q.")
                 return self.default_q
            self.initialize_q_table(state, self.action_space)
        return self.q_table[state].get(action, self.default_q)

    def update_q_value(self, state: Any, action: str, reward: float, next_state: Optional[Any],
                       learning_rate: float, discount_factor: float, action_space: List[str], 
                       is_terminal: bool = False):
        if state not in self.q_table:
            self.initialize_q_table(state, action_space) 

        max_future_q = 0.0
        if not is_terminal and next_state is not None:
            if next_state not in self.q_table:
                self.initialize_q_table(next_state, action_space)
            
            if self.q_table[next_state]: # If there are actions from next_state
                max_future_q = max(self.q_table[next_state].values())
            # else max_future_q remains 0.0 (e.g. if next_state is new and action_space was empty, though initialize_q_table should handle it)

        current_q = self.q_table[state].get(action, self.default_q)
        new_q = current_q + learning_rate * (reward + discount_factor * max_future_q - current_q)
        self.q_table[state][action] = new_q

    def _get_hashable_state(self, observation_sensor_data: Optional[Dict[str, Any]]) -> Optional[Any]:
        if observation_sensor_data is None:
            return None # Represents a terminal state or lack of observation

        if "agent_position" in observation_sensor_data:
            pos = observation_sensor_data["agent_position"]
            # Ensure position is a tuple if it's a list (JSON might make it a list)
            return tuple(pos) if isinstance(pos, list) else pos
        
        # Fallback for other types of observations: try to make a sorted tuple of items
        try:
            return tuple(sorted(observation_sensor_data.items()))
        except Exception as e:
            print(f"Warning: QLearningAgent {self.agent_id} could not convert observation_sensor_data to a standard hashable state: {e}. Using string representation.")
            return str(observation_sensor_data)

    def perceive(self, observation: PerceptionData, event: Optional[PiaSEEvent] = None):
        self.previous_state = self.current_state # Store S
        self.current_state = self._get_hashable_state(observation.sensor_data) # New S' becomes current_state S for next cycle

        if self.current_state is not None and self.current_state not in self.q_table and self.action_space:
             self.initialize_q_table(self.current_state, self.action_space)
        
        if event:
            # Q-learning agent might not directly use generic events unless they provide rewards or state changes
            # print(f"QLearningAgent {self.agent_id} perceived event: {event.event_type}")
            pass


    def act(self) -> ActionCommand:
        if self.current_state is None: # Should have been set by perceive
            if not self.action_space:
                # This is a critical error state for the agent.
                # It cannot act without knowing possible actions or its current state.
                print(f"ERROR: QLearningAgent {self.agent_id} has no current_state or action_space. Cannot choose an action. Defaulting to 'stay' or first known action if any.")
                chosen_action_str = self.action_space[0] if self.action_space else "stay" # A desperate guess
                self.last_action = chosen_action_str
                return ActionCommand(action_type=chosen_action_str, parameters={})

        if random.uniform(0, 1) < self.epsilon: # Explore
            chosen_action_str = random.choice(self.action_space) if self.action_space else "stay"
        else: # Exploit
            if self.current_state not in self.q_table or not self.q_table[self.current_state]:
                # If current state is unknown (e.g. perceive not called, or action space not set at perceive time)
                # Initialize it now if possible, or pick random.
                if self.action_space:
                    self.initialize_q_table(self.current_state, self.action_space)
                    # Check again if it was successfully initialized
                    if not self.q_table.get(self.current_state): # Should not happen if action_space is not empty
                         chosen_action_str = random.choice(self.action_space)
                    else: # Successfully initialized
                        q_values = self.q_table[self.current_state]
                        max_q = max(q_values.values())
                        best_actions = [action for action, q_val in q_values.items() if q_val == max_q]
                        chosen_action_str = random.choice(best_actions)
                else: # No action space, cannot exploit properly
                    chosen_action_str = "stay" # Default fallback
            else: # Current state is in Q-table and has entries
                q_values = self.q_table[self.current_state]
                max_q = max(q_values.values())
                best_actions = [action for action, q_val in q_values.items() if q_val == max_q]
                chosen_action_str = random.choice(best_actions)
        
        self.last_action = chosen_action_str
        return ActionCommand(action_type=chosen_action_str, parameters={})

    def learn(self, feedback: ActionResult):
        reward = feedback.details.get("reward", 0.0)
        is_terminal = feedback.details.get("is_terminal", False)
        
        next_observation_sensor_data = None
        if feedback.new_perception_snippet and feedback.new_perception_snippet.sensor_data:
            next_observation_sensor_data = feedback.new_perception_snippet.sensor_data
            
        # S is previous_state, A is last_action, R is reward, S' is hashable_next_state
        state_s = self.previous_state 
        action_a = self.last_action
        
        # Note: self.current_state was already updated to S' by perceive() before learn() is called.
        # So, next_state_s_prime for Q-learning update is actually self.current_state.
        # However, the plan was to use feedback.new_perception_snippet.sensor_data.
        # Let's reconcile: perceive(S') sets self.current_state = S'. learn() then uses this S'.
        # So, S is self.previous_state. A is self.last_action. R is from feedback. S' is self.current_state.
        
        hashable_next_state_s_prime = self.current_state # This IS S' because perceive(S') was called before learn(R)

        if state_s is None : # Cannot learn if we don't know state S
            # print(f"QLearningAgent {self.agent_id}: Cannot learn, previous_state (S) is None.")
            return
        if action_a is None: # Cannot learn if we don't know action A
            # print(f"QLearningAgent {self.agent_id}: Cannot learn, last_action (A) is None.")
            return
        if not self.action_space: # Action space needed for initializing Q-values for S'
            print(f"QLearningAgent {self.agent_id}: Cannot learn, action_space is not set.")
            return

        self.update_q_value(state_s, action_a, reward, hashable_next_state_s_prime,
                            self.lr, self.gamma, self.action_space, is_terminal=is_terminal)

    def configure(self, env_info: Dict[str, Any], action_space: List[str]): # Or Dict[str,Dict] if using new action_space format
        """ Configure agent with environment info, primarily the action space. """
        # The action_space from GridWorld is now Dict[str, {}], we need List[str] of keys
        if isinstance(action_space, dict):
            self.action_space = list(action_space.keys())
        elif isinstance(action_space, list): # Keep compatibility if old format is passed
            self.action_space = action_space
        else:
            print(f"Warning: QLearningAgent {self.agent_id} received action_space in unexpected format: {type(action_space)}. Expected list or dict.")
            self.action_space = []
            
        # Initialize Q-table for current_state if it exists and action space is now known
        if self.current_state is not None and self.current_state not in self.q_table and self.action_space:
            self.initialize_q_table(self.current_state, self.action_space)
        print(f"QLearningAgent {self.agent_id} configured with action space: {self.action_space}")

```
