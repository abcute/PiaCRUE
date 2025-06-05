import random
from typing import List, Tuple, Dict, Optional, Any

from ..core_engine.interfaces import AgentInterface, PiaSEEvent

class BasicGridAgent(AgentInterface):
    """
    A basic agent that can operate in a grid-like environment.
    It can follow a random policy or a simple goal-oriented policy.
    """

    def __init__(self, policy: str = "random", goal: Optional[Tuple[int, int]] = None):
        """
        Initializes the BasicGridAgent.

        Args:
            policy (str): The policy the agent should follow.
                          Can be "random" or "goal_oriented".
            goal (Optional[Tuple[int, int]]): The (x, y) coordinates of the agent's goal.
                                              Required if policy is "goal_oriented".
        """
        self.agent_id: str = "UnnamedAgent" # Default ID, should be set by engine
        self.policy: str = policy
        self.goal: Optional[Tuple[int, int]] = goal
        self.current_observation: Optional[Any] = None # Stores the latest observation

        if self.policy == "goal_oriented" and self.goal is None:
            print(f"Warning: BasicGridAgent policy is 'goal_oriented' but no goal was provided. Agent will act randomly.")

        self.available_actions = ["N", "S", "E", "W", "Stay"]
        print(f"BasicGridAgent '{self.agent_id}' initialized with policy: {self.policy}, goal: {self.goal}")

    def set_id(self, agent_id: str):
        """Sets the unique identifier for the agent."""
        self.agent_id = agent_id
        # print(f"Agent ID set to: {self.agent_id}")

    def get_id(self) -> str:
        """Gets the unique identifier for the agent."""
        return self.agent_id

    def perceive(self, observation: Any, event: Optional[PiaSEEvent] = None):
        """
        Provides the agent with an observation from the environment and optional events.

        Args:
            observation (Any): The observation from the environment.
                               Expected to be a dictionary containing at least 'agent_position'.
            event (Optional[PiaSEEvent]): An optional event that occurred.
        """
        self.current_observation = observation
        # print(f"Agent '{self.agent_id}' perceived observation: {observation}")
        if event:
            print(f"Agent '{self.agent_id}' received event: {event}")

    def act(self) -> str:
        """
        Decides on an action based on the agent's policy and current state/perception.

        Returns:
            str: The action to be performed (e.g., "N", "S", "E", "W", "Stay").
        """
        if self.current_observation is None:
            # print(f"Agent '{self.agent_id}' has no observation, acting randomly by default.")
            return random.choice(self.available_actions)

        # Ensure current_observation is a dictionary and has 'agent_position'
        if not isinstance(self.current_observation, dict) or 'agent_position' not in self.current_observation:
            print(f"Warning: Agent '{self.agent_id}' received an unexpected observation format: {self.current_observation}. Acting randomly.")
            return random.choice(self.available_actions)

        current_pos: Tuple[int, int] = self.current_observation['agent_position']

        if self.policy == "goal_oriented" and self.goal:
            # Simple goal-oriented logic: move towards the goal.
            # This doesn't consider obstacles, just direct line of sight.
            # A more advanced agent would use pathfinding (A*, etc.) based on grid_view.
            dx = self.goal[0] - current_pos[0]
            dy = self.goal[1] - current_pos[1]

            if abs(dx) > abs(dy): # Move horizontally
                if dx > 0:
                    return "E"
                elif dx < 0:
                    return "W"
            elif abs(dy) > abs(dx): # Move vertically
                if dy > 0:
                    return "S"
                elif dy < 0:
                    return "N"
            elif dx == 0 and dy == 0: # Agent is at the goal
                return "Stay" # Or some other action indicating goal reached

            # If dx == dy and not zero, can choose randomly or prioritize one axis
            # For simplicity, let's prioritize E/W then N/S if equally distant
            if dx > 0: return "E"
            if dx < 0: return "W"
            if dy > 0: return "S"
            if dy < 0: return "N"

            return "Stay" # Should ideally not be reached if goal is not current_pos

        # Default to random policy if not goal-oriented or goal not set/reached
        return random.choice(self.available_actions)

    def learn(self, feedback: Any):
        """
        Allows the agent to learn from feedback received after an action.
        For this basic agent, it just prints the feedback.

        Args:
            feedback (Any): Feedback from the environment. For BasicGridAgent, this is not used for learning.
                            It might be a tuple like (reward, new_observation) from the engine.
        """
        # BasicGridAgent does not learn from rewards in this version.
        # It can optionally print the feedback if needed for debugging.
        # print(f"Agent '{self.agent_id}' received feedback: {feedback}")
        pass

if __name__ == '__main__':
    # Example Usage:
    print("--- BasicGridAgent Example ---")

    # 1. Random Agent
    random_agent = BasicGridAgent(policy="random")
    random_agent.set_id("Rando1")
    print(f"Agent ID: {random_agent.get_id()}")

    # Simulate perception
    mock_obs_random = {"agent_position": (0, 0), "grid_view": [[0,0],[0,0]]}
    random_agent.perceive(mock_obs_random)

    # Simulate a few actions
    print(f"\n{random_agent.get_id()} (Random Policy) actions:")
    for _ in range(5):
        action = random_agent.act()
        print(f"Action: {action}")
        # In a real scenario, this action would be sent to the environment,
        # and the agent would then perceive the new state.
        # For this example, let's simulate a new position slightly based on action.
        # This is a very crude simulation of movement for testing perception.
        current_x, current_y = mock_obs_random["agent_position"]
        if action == "N": mock_obs_random["agent_position"] = (current_x, current_y - 1)
        elif action == "S": mock_obs_random["agent_position"] = (current_x, current_y + 1)
        elif action == "E": mock_obs_random["agent_position"] = (current_x + 1, current_y)
        elif action == "W": mock_obs_random["agent_position"] = (current_x - 1, current_y)
        random_agent.perceive(mock_obs_random) # Re-perceive the "new" state


    # 2. Goal-Oriented Agent
    goal_agent = BasicGridAgent(policy="goal_oriented", goal=(3, 3))
    goal_agent.set_id("Go Getter")
    print(f"\nAgent ID: {goal_agent.get_id()}, Goal: {goal_agent.goal}")

    mock_obs_goal = {"agent_position": (0, 0), "grid_view": [[0]*4 for _ in range(4)]} # 4x4 grid
    goal_agent.perceive(mock_obs_goal)

    print(f"\n{goal_agent.get_id()} (Goal-Oriented Policy) actions from {mock_obs_goal['agent_position']} towards {goal_agent.goal}:")
    for i in range(8): # Max steps to reach goal in 3,3 (or stay if reached)
        action = goal_agent.act()
        print(f"Step {i+1}: Position {mock_obs_goal['agent_position']}, Action: {action}")

        current_x, current_y = mock_obs_goal["agent_position"]
        if action == "N": mock_obs_goal["agent_position"] = (current_x, current_y - 1)
        elif action == "S": mock_obs_goal["agent_position"] = (current_x, current_y + 1)
        elif action == "E": mock_obs_goal["agent_position"] = (current_x + 1, current_y)
        elif action == "W": mock_obs_goal["agent_position"] = (current_x - 1, current_y)

        goal_agent.perceive(mock_obs_goal) # Agent perceives new position

        if mock_obs_goal["agent_position"] == goal_agent.goal and action == "Stay":
            print(f"Goal {goal_agent.goal} reached!")
            break

    # Test learn method
    goal_agent.learn("Achieved goal with 100 points.")

    # 3. Goal-Oriented Agent with no goal (should act random)
    no_goal_agent = BasicGridAgent(policy="goal_oriented")
    no_goal_agent.set_id("Lost Soul")
    no_goal_agent.perceive({"agent_position": (1,1)})
    print(f"\n{no_goal_agent.get_id()} (Goal-Oriented with no goal) actions:")
    for _ in range(3):
        print(f"Action: {no_goal_agent.act()}")

    # 4. Agent perceiving an event
    event_agent = BasicGridAgent()
    event_agent.set_id("Event Listener")
    sample_event = PiaSEEvent() # Assuming PiaSEEvent can be instantiated like this
    # If PiaSEEvent needs arguments, this would be: PiaSEEvent(type="some_event", data={})
    event_agent.perceive(observation={"agent_position": (0,0)}, event=sample_event)


    print("\n--- BasicGridAgent Example End ---")
