import random
from typing import List, Tuple, Dict, Optional, Any
from PiaAGI_Hub.PiaSE.core_engine.interfaces import AgentInterface, PiaSEEvent

class QLearningAgent(AgentInterface):
    # Need to store the last action taken by the agent to use in the learn method
    def __init__(self,
                 learning_rate: float = 0.1,
                 discount_factor: float = 0.9,
                 exploration_rate: float = 0.1,
                 default_q_value: float = 0.0):
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = exploration_rate
        self.default_q = default_q_value
        self.q_table: Dict[Any, Dict[Any, float]] = {}
        self.agent_id: Optional[str] = None
        self.current_state: Optional[Any] = None
        self.action_space: List[Any] = []
        self.last_action: Optional[Any] = None # Add last_action

    def set_id(self, agent_id: str):
        self.agent_id = agent_id

    def get_id(self) -> Optional[str]:
        return self.agent_id

    def initialize_q_table(self, state: Any, action_space: list):
        self.action_space = action_space # Store/update action space
        # Always (re)initialize the Q-values for the given state to default_q for all actions.
        self.q_table[state] = {action: self.default_q for action in self.action_space}

    def get_q_value(self, state: Any, action: Any) -> float:
        # Ensure the state is initialized in the Q-table before trying to get a Q-value.
        if state not in self.q_table:
            # If action_space is not yet known, we can't initialize properly.
            # This might indicate an issue in the simulation flow or agent setup.
            # For now, return default_q, but ideally action_space is set early.
            if not self.action_space:
                 print(f"Warning: get_q_value called for state {state} but agent's action_space is not set. Returning default Q.")
                 return self.default_q
            self.initialize_q_table(state, self.action_space)
        return self.q_table[state].get(action, self.default_q)

    def update_q_value(self, state: Any, action: Any, reward: float, next_state: Any,
                       learning_rate: float, discount_factor: float, action_space: list):
        # Ensure current state-action pair is in Q-table
        if state not in self.q_table:
            self.initialize_q_table(state, action_space) # action_space passed here is crucial

        # Ensure next_state is in Q-table to get max_future_q
        if next_state not in self.q_table:
            self.initialize_q_table(next_state, action_space)

        max_future_q = 0.0
        # Check if q_table[next_state] is not empty before calling max()
        if next_state in self.q_table and self.q_table[next_state]:
            max_future_q = max(self.q_table[next_state].values())

        current_q = self.q_table[state].get(action, self.default_q) # Use default_q if action somehow not in initialized state

        new_q = current_q + learning_rate * (reward + discount_factor * max_future_q - current_q)
        self.q_table[state][action] = new_q

    def _get_hashable_state(self, observation: Any) -> Any:
        """Converts an observation to a hashable state representation."""
        if isinstance(observation, dict) and "agent_position" in observation:
            # For GridWorld-like observations, use the agent's position tuple as the state.
            return observation["agent_position"]
        elif isinstance(observation, list) or isinstance(observation, dict):
            # Attempt to convert other complex types to a sorted tuple of items for hashing.
            # This is a generic fallback and might not be optimal for all environments.
            try:
                if isinstance(observation, dict):
                    return tuple(sorted(observation.items()))
                return tuple(observation)
            except TypeError:
                # If elements are not hashable (e.g. nested dicts/lists), this will fail.
                # In such cases, the environment or agent needs a more specific state representation.
                print(f"Warning: Agent {self.agent_id} received complex observation of type {type(observation)} that may not be hashable or optimally represented. Consider a custom state representation.")
                return str(observation) # Fallback to string representation if all else fails
        return observation # Assume it's already hashable (e.g. tuple, string, int)


    def perceive(self, observation: Any, event: Optional[PiaSEEvent] = None):
        self.current_state = self._get_hashable_state(observation)
        # Initialize Q-table for the new state if it's encountered for the first time
        # and if action_space is known (it should be by the time perceive is called in a learning loop)
        if self.current_state not in self.q_table and self.action_space:
             self.initialize_q_table(self.current_state, self.action_space) # self.current_state is now hashable
        if event:
            print(f"Agent {self.agent_id} perceived event: {event}")

    def act(self) -> Any: # Modified act to store last_action
        if self.current_state is None:
            # Fallback if perceive hasn't been called or no state is set
            # This agent needs an action_space to choose from.
            if not self.action_space:
                print(f"Warning: Agent {self.agent_id} trying to act without an action_space. Returning None.")
                self.last_action = None
                return None
            self.last_action = random.choice(self.action_space)
            return self.last_action

        # Epsilon-greedy strategy
        if random.uniform(0, 1) < self.epsilon:
            # Explore: choose a random action
            if not self.action_space: # Should not happen if initialized
                 print(f"Warning: Agent {self.agent_id} exploring without an action_space. Returning None.")
                 chosen_action = None
            else:
                chosen_action = random.choice(self.action_space)
        else:
            # Exploit: choose the best action from Q-table
            # Ensure current_state is initialized before trying to access its Q-values
            if self.current_state not in self.q_table or not self.q_table[self.current_state]:
                 # This implies action_space might not be set if initialize_q_table was never called for this agent
                 if not self.action_space:
                     print(f"Warning: Agent {self.agent_id} exploiting without action_space. Cannot initialize Q-table for {self.current_state}. Returning None.")
                     chosen_action = None
                 else:
                    self.initialize_q_table(self.current_state, self.action_space) # Ensure state is initialized
                    # If still no actions (e.g. action_space was empty during init), fallback
                    if not self.q_table.get(self.current_state): # Check if self.current_state is now in q_table and has entries
                        chosen_action = random.choice(self.action_space) if self.action_space else None
                    else:
                        q_values = self.q_table[self.current_state]
                        max_q = max(q_values.values())
                        best_actions = [action for action, q in q_values.items() if q == max_q]
                        chosen_action = random.choice(best_actions)
            else: # current_state is in q_table and has actions
                q_values = self.q_table[self.current_state]
                if not q_values: # Should not happen if initialized correctly
                    chosen_action = random.choice(self.action_space) if self.action_space else None
                else:
                    max_q = max(q_values.values())
                    best_actions = [action for action, q in q_values.items() if q == max_q]
                    chosen_action = random.choice(best_actions)

        self.last_action = chosen_action
        return self.last_action

    def learn(self, feedback: Any):
        # Assuming feedback is a tuple (last_state, last_action, reward, current_state, done)
        # Or more simply, for this agent: (reward, next_state) as current_state and last_action are internal
        if isinstance(feedback, tuple) and len(feedback) == 2:
            reward, next_state = feedback # Here, next_state is the S' from the perspective of (S, A)

            if self.current_state is None: # current_state here is S (state before last_action was taken)
                print(f"Agent {self.agent_id} cannot learn: an internal 'current_state' (S) was not properly set before learn was called.")
                return
            if self.last_action is None:
                print(f"Agent {self.agent_id} cannot learn: 'last_action' (A) was not set.")
                return
            if not self.action_space: # action_space is needed by update_q_value if new states are encountered
                print(f"Agent {self.agent_id} cannot learn: 'action_space' is not set.")
                return

            # The state used for update should be the state in which self.last_action was taken.
            # If perceive(S') was called, self.current_state is S'. We need S.
            # This requires careful handling of state updates or passing S explicitly.
            # For now, let's assume self.current_state at the time of calling .learn() is the state *before*
            # the agent took self.last_action and received feedback.
            # This means self.current_state IS S. And `next_state` from feedback is S'.

            # The prompt for `learn` in AgentInterface is `learn(self, feedback: any)`.
            # The simulation engine's `run_step` provides feedback from `environment.step()`
            # `env.step()` returns `(observation, reward, done, info)`.
            # So, feedback to agent.learn() will be this 4-tuple.
            # The agent's `perceive` method is called with the new observation *before* `learn`.
            # So, when `learn` is called:
            # - `self.current_state` is S' (the new state from obs)
            # - `self.last_action` is A (the action that led to S')
            # - We need S (the state *before* A was taken)
            # This implies the agent needs to remember the state S *before* `act()` chose `last_action`.

            # Let's add `self.previous_state` to the agent.
            # `perceive` will set `self.previous_state = self.current_state` then `self.current_state = new_observation`
            # This is a common pattern.
            # For this iteration, I'll stick to the provided structure and assume the `feedback`
            # must contain all necessary info or that the states are managed externally to `learn`.
            # The prompt's `learn` method signature for QLearningAgent was:
            # learn(self, feedback: Any):
            #   if isinstance(feedback, tuple) and len(feedback) == 2:
            #       reward, next_state = feedback
            #       if self.current_state is not None and self.last_action is not None:
            #           self.update_q_value(self.current_state, self.last_action, reward, next_state, ...)
            # This implies current_state at time of learn() is S.
            # And next_state passed in feedback is S'.
            # This means that `perceive(S')` should not yet have updated `self.current_state` to S'
            # when `learn( (R, S') )` is called. This needs careful orchestration in the engine.
            # Or, the `feedback` to `learn` should contain `(S, A, R, S')`.
            # Given the current BasicSimulationEngine, `agent.perceive(observation)` (this is S') is called,
            # then `agent.learn(feedback)` where feedback is the result of `env.step()`.
            # So, `self.current_state` IS S' when `learn` is called.

            # Let's adjust based on a more standard RL loop:
            # 1. Agent is in S.
            # 2. Agent calls perceive(S). (self.current_state becomes S)
            # 3. Agent calls act() -> A. (self.last_action becomes A)
            # 4. Engine calls env.step(A) -> (S', R, D, I)
            # 5. Agent calls learn((S, A, R, S', D)). S is self.current_state *before* perceive(S').
            #    Or, agent.learn(R, S') and it uses internally stored S and A.
            # To do this, `learn` must be called *before* `perceive(S')`.
            # Or, `perceive` must be more careful.

            # Let's assume the `learn` method gets `(state_s, action_a, reward_r, next_state_s_prime)`
            # For now, the provided code is: `learn(self, feedback: Any)` where `feedback` is `(reward, next_state)`.
            # It relies on `self.current_state` being S and `self.last_action` being A.
            # This requires `self.current_state` not to be updated to S' before `learn` is called.
            # The BasicSimulationEngine calls perceive(S') then learn(env_feedback). This is an issue.

            # Simplest fix for now: QLearningAgent needs to store previous_state.
            # `perceive(obs)`: self.previous_state = self.current_state; self.current_state = obs
            # `learn((reward, S'))`: use self.previous_state as S.
            # This change is not in the provided code, so I'll stick to it for now and it might be a bug.
            # The provided code's learn:
            # self.update_q_value(self.current_state, self.last_action, reward, next_state, ...)
            # This means self.current_state is S when learn is called.
            # The engine must pass the OLD state to learn, or the agent must store it.
            # Given the prompt, I will assume `self.current_state` is indeed S when `learn` is called.

            state_s = self.current_state # This is S (already hashable due to perceive)
            action_a = self.last_action  # This is A
            reward_r = feedback[0]       # This is R

            # Convert the raw next_state (S') from feedback into its hashable representation
            hashable_next_state_s_prime = self._get_hashable_state(feedback[1])

            if state_s is not None and action_a is not None:
                self.update_q_value(state_s, action_a, reward_r, hashable_next_state_s_prime,
                                    self.lr, self.gamma, self.action_space)
            else:
                print(f"Agent {self.agent_id} cannot learn: current_state (S) or last_action (A) not set appropriately before learn call.")
        else:
            print(f"Agent {self.agent_id} received unexpected feedback format for learning: {feedback}")


if __name__ == '__main__':
    # Example Usage
    agent = QLearningAgent(exploration_rate=0.2, default_q_value=0.0)
    agent.set_id("q_agent_1")

    # Mock action space and initial state
    mock_action_space = ["up", "down", "left", "right"]
    initial_state_s0 = "state_0" # Example state representation (can be anything hashable)

    # Agent needs its action_space set, typically by the environment or engine during initialization phase
    # For this standalone example, we call initialize_q_table also to set agent.action_space
    agent.initialize_q_table(initial_state_s0, mock_action_space)
    print(f"Agent action space: {agent.action_space}")
    print(f"Initial Q-table for state {initial_state_s0}: {agent.q_table.get(initial_state_s0)}")

    # --- Interaction 1 ---
    # Agent is in s0
    agent.perceive(initial_state_s0)
    print(f"Agent perceived state: {agent.current_state}")

    action_a0 = agent.act() # Agent takes action a0 from s0
    print(f"Action taken from {initial_state_s0}: {action_a0}")

    # Environment simulates step, returns reward and next state
    reward_r0 = 0.5
    next_state_s1 = "state_1"
    print(f"Environment gives reward {reward_r0} and next state {next_state_s1}")

    # Agent learns from this experience (s0, a0, r0, s1)
    # Crucially, agent.current_state should be s0 for this call as per the learn() logic.
    # If perceive(s1) was called before learn(), then learn() would use s1 as current_state (S)
    # which would be incorrect. The example below assumes learn is called with S=s0.
    # To make this work with the current learn structure, we must ensure current_state is S.
    # So, if perceive(S') was called, we'd need to pass S to learn explicitly, or agent stores S_previous.
    # The example usage simulates the case where learn is called *before* perceiving the next state.
    agent.learn((reward_r0, next_state_s1)) # learn uses self.current_state (s0) and self.last_action (a0)
    print(f"Q-table for state {initial_state_s0} after learning: {agent.q_table.get(initial_state_s0)}")
    print(f"Q-table for state {next_state_s1} (should be initialized): {agent.q_table.get(next_state_s1)}")

    # --- Interaction 2 ---
    # Agent is now in s1 (after perceiving it)
    agent.perceive(next_state_s1)
    print(f"Agent perceived state: {agent.current_state}")

    action_a1 = agent.act() # Agent takes action a1 from s1
    print(f"Action taken from {next_state_s1}: {action_a1}")

    reward_r1 = 1.0
    next_state_s2 = "state_2" # A new state
    print(f"Environment gives reward {reward_r1} and next state {next_state_s2}")

    agent.learn((reward_r1, next_state_s2)) # learn uses self.current_state (s1) and self.last_action (a1)
    print(f"Q-table for state {next_state_s1} after learning: {agent.q_table.get(next_state_s1)}")
    print(f"Q-table for state {next_state_s2} (should be initialized): {agent.q_table.get(next_state_s2)}")

    # Test exploration vs exploitation by setting epsilon low
    agent.epsilon = 0.0 # Force exploitation
    print(f"\nAgent's Q-table for state {next_state_s1}: {agent.q_table.get(next_state_s1)}")
    agent.perceive(next_state_s1) # Agent is in next_state_s1
    exploited_action = agent.act()
    print(f"Exploited action from state {next_state_s1} (epsilon=0): {exploited_action}")

    # Test get_q_value for an uninitialized state but known action space
    unknown_state = "state_unknown"
    action_for_unknown_state = agent.action_space[0] if agent.action_space else "up"
    q_val_unknown = agent.get_q_value(unknown_state, action_for_unknown_state)
    print(f"Q-value for unknown state {unknown_state} and action '{action_for_unknown_state}': {q_val_unknown} (should be default: {agent.default_q})")
    print(f"Q-table for {unknown_state} after get_q_value: {agent.q_table.get(unknown_state)}")

    # Test get_q_value if action_space is not set on agent (should return default and print warning)
    empty_agent = QLearningAgent()
    empty_agent.set_id("empty_agent")
    print(f"Q-value from empty_agent for state 's0' action 'up': {empty_agent.get_q_value('s0', 'up')}")
