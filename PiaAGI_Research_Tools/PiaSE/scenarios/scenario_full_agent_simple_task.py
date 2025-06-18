import asyncio
import time # For example timestamps if needed directly
from datetime import datetime, timezone

# PiaSE Core
from PiaAGI_Research_Tools.PiaSE.core_engine.basic_engine import BasicSimulationEngine
from PiaAGI_Research_Tools.PiaSE.core_engine.events import PiaSEEvent
from PiaAGI_Research_Tools.PiaSE.core_engine.interfaces import PerceptionData, ActionCommand, ActionResult
from PiaAGI_Research_Tools.PiaSE.core_engine.logger import PiaSELogger # Assuming this logger is used by engine

# PiaSE Environments
from PiaAGI_Research_Tools.PiaSE.environments.text_based_room import TextBasedRoom, TextualPercept

# PiaSE Agents
from PiaAGI_Research_Tools.PiaSE.agents.pia_agi_agent import PiaAGIAgent

# PiaCML (for MessageBus and GenericMessage, potentially core_messages for manual PerceptionData construction)
from PiaAGI_Research_Tools.PiaCML.message_bus import MessageBus
from PiaAGI_Research_Tools.PiaCML.core_messages import GenericMessage, PerceptDataPayload # For constructing initial percept

def simple_bus_listener(message: GenericMessage):
    """A simple callback function to print messages from the agent's internal bus."""
    payload_str = str(message.payload)
    if len(payload_str) > 100:
        payload_str = payload_str[:97] + "..."
    print(f"SCENARIO_BUS_LISTENER :: Type={message.message_type}, From={message.source_module_id}, Payload={payload_str}")

async def main():
    print("--- Starting Full PiaAGI Agent Simple Task Scenario ---")

    # 1. Instantiate PiaAGI Agent
    # The agent will internally create its CML modules and its own message bus.
    pia_agent = PiaAGIAgent(agent_id="PiaAgent001")
    print(f"PiaAGIAgent '{pia_agent.get_id()}' instantiated.")

    # 2. Instantiate Environment
    text_room = TextBasedRoom(environment_id="SimpleTextRoom1")
    text_room.add_object("Note", {"description": "A small note lies on a table.", "content": "Objective: Respond coherently."})
    print(f"Environment '{text_room.get_id()}' instantiated with a note.")

    # 3. Instantiate Simulation Engine
    # The engine will use its own logger if path is provided.
    engine = BasicSimulationEngine(simulation_id="Sim_SimpleTaskDemo")
    print(f"Simulation Engine '{engine.simulation_id}' instantiated.")

    # 4. Simple Bus Listener for Demonstration
    # Access the agent's internal message bus and subscribe our listener.
    # This demonstrates that the bus is active and modules are (conceptually) using it.
    print("\n--- Subscribing scenario listener to agent's internal message bus ---")
    agent_bus = pia_agent.message_bus # Access the agent's bus instance

    # Message types the CML modules are likely to publish internally
    messages_to_listen_for = [
        "PerceptData",          # From PerceptionModule (internal representation)
        "LTMQuery",             # From various modules to LTM
        "LTMQueryResult",       # From LTM
        "GoalUpdate",           # From MotivationalSystem
        "EmotionalStateChange", # From EmotionModule
        "ActionCommand",        # From Planning to BehaviorGeneration (internal command)
        "SelfKnowledgeConfidenceUpdate", # From SelfModel
        "AttentionFocusUpdate", # From AttentionModule
        "ToMInferenceUpdate"    # From ToMModule
    ]
    for msg_type in messages_to_listen_for:
        agent_bus.subscribe(
            module_id="ScenarioObserver", # Conceptual ID for this listener
            message_type=msg_type,
            callback=simple_bus_listener
        )
    print(f"Scenario listener subscribed to {len(messages_to_listen_for)} message types on agent's bus.")


    # 5. Initialize the Engine
    # This sets up the environment and agent within the engine.
    # The PiaSELogger is typically instantiated by the engine if log_path is given.
    scenario_config = {
        "name": "SimpleTaskDemo",
        "description": "PiaAGIAgent receives an initial percept and runs for a few steps.",
        "max_steps": 10 # Example max steps
    }
    engine.initialize(
        environment=text_room,
        agents={"PiaAgent001": pia_agent}, # Use agent_id as key
        scenario_config=scenario_config,
        log_path="logs/scenario_full_agent_simple_task.jsonl" # Enable logging
    )
    print(f"\nEngine initialized. Log path: {engine.logger.log_file_path if engine.logger else 'N/A'}")

    # 6. Simulate an initial perception for the agent
    # In a real scenario, the first step of the engine might provide this.
    # Here, we manually trigger the agent's perceive method before the main loop starts
    # to give it something to think about.
    print("\n--- Manually providing initial perception to agent ---")
    initial_percept_text = "Hello Pia, what is your primary objective today?"
    # We need to wrap this in the PerceptionData structure the agent's perceive method expects.
    # The agent's PerceptionModule will then internally convert this to its own PerceptDataPayload message.

    # Constructing PerceptionData with a TextualPercept
    # The timestamp for the perception data itself
    perception_ts = datetime.now(timezone.utc).timestamp()
    initial_perception_data = PerceptionData(
        agent_id="PiaAgent001", # The agent this perception is for
        data=[TextualPercept(text=initial_percept_text, source="user_greeting")],
        timestamp=perception_ts,
        metadata={"source_interface": "simulated_user_input"}
    )

    pia_agent.perceive(initial_perception_data)
    print(f"Initial perception data sent to agent: '{initial_percept_text}'")
    print("(Note: Internal CML messages from this perception should appear above if bus listener is working)")

    # 7. Run the simulation for a few steps
    num_simulation_steps = 5
    print(f"\n--- Running simulation for {num_simulation_steps} steps ---")
    # The engine's run_simulation method will call agent.act() and environment.execute_action()
    # in a loop. pia_agent.act() will internally use its CML modules.
    # pia_agent.learn() will be called with ActionResult.
    await engine.run_simulation_async(num_steps=num_simulation_steps) # Use async version for bus

    print(f"\n--- Simulation finished after {engine.current_step} steps ---")

    # 8. (Optional) Inspect agent's final state or specific module status
    if hasattr(pia_agent, 'self_model') and hasattr(pia_agent.self_model, 'get_module_status'):
        print("\n--- PiaAgent's SelfModel Final Status ---")
        # print(pia_agent.self_model.get_module_status()) # Requires ConcreteSelfModelModule
        if CML_PLACEHOLDERS_USED:
             print("(SelfModel is a placeholder, status is generic)")
        else:
             print(pia_agent.self_model.get_module_status())


    if hasattr(pia_agent, 'emotion_module') and hasattr(pia_agent.emotion_module, 'get_emotional_state'):
        print("\n--- PiaAgent's EmotionModule Final State ---")
        # print(pia_agent.emotion_module.get_emotional_state()) # Requires ConcreteEmotionModule
        if CML_PLACEHOLDERS_USED:
             print("(EmotionModule is a placeholder, state is generic)")
        else:
             print(pia_agent.emotion_module.get_emotional_state())


if __name__ == "__main__":
    # Ensure logs directory exists
    import os
    if not os.path.exists("logs"):
        os.makedirs("logs")

    asyncio.run(main())

```
