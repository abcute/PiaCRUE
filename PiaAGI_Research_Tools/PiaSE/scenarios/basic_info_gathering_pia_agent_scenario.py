from typing import Dict, Any

from PiaAGI_Research_Tools.PiaSE.core_engine.basic_simulation_engine import BasicSimulationEngine
from PiaAGI_Research_Tools.PiaSE.environments.text_based_room import TextBasedRoom, RoomLayout, ObjectDetail
from PiaAGI_Research_Tools.PiaSE.agents.pia_agi_agent import PiaAGIAgent, CML_PLACEHOLDERS_USED

# Import ConcreteWorldModel if not using placeholders, otherwise PiaAGIAgent handles it.
if not CML_PLACEHOLDERS_USED:
    from PiaAGI_Research_Tools.PiaCML.concrete_world_model import ConcreteWorldModel
else: # PiaAGIAgent will use its placeholder for ConcreteWorldModel
    ConcreteWorldModel = None


def run_info_gathering_scenario():
    print("--- Starting Basic Info Gathering Scenario with PiaAGIAgent ---")
    if CML_PLACEHOLDERS_USED:
        print("*** NOTE: Running with PLACEHOLDER CML modules. Agent behavior will be very basic. ***")

    # 1. Environment Setup
    room_layout = RoomLayout(
        room_id="study",
        description="A quiet study with a large wooden desk and a bookshelf.",
        connections={"hallway": "A short hallway."},
        objects=["desk", "bookshelf", "journal_on_desk"]
    )
    hallway_layout = RoomLayout(
        room_id="hallway",
        description="A narrow hallway.",
        connections={"study": "The study door."}
    )
    object_details: Dict[str, ObjectDetail] = {
        "desk": ObjectDetail(name="desk", description="A large wooden desk.", properties={"is_container": True, "can_store": True, "is_open": False}),
        "bookshelf": ObjectDetail(name="bookshelf", description="A tall bookshelf filled with old books.", properties={"is_container": False}),
        "journal_on_desk": ObjectDetail(name="journal", description="A leather-bound journal lies on the desk.", properties={"is_readable": True, "is_portable": True, "location_in_room": "desk"}), # Initially on desk
        # "journal_in_desk": ObjectDetail(name="journal", description="A leather-bound journal.", properties={"is_readable": True, "is_portable": True}), # If it were in the desk
    }

    # Place journal on desk initially, not inside. Agent needs to navigate to desk, then take, then read.
    # If we wanted it inside: desk's initial_contents = ["journal_in_desk"]

    environment = TextBasedRoom(
        agent_start_room_id="hallway", # Start in hallway, must go to study
        room_layouts=[room_layout, hallway_layout],
        object_details=object_details
    )

    # 2. Agent Configuration
    # For MVP, planning might be very simple. The goal is to "FIND_AND_READ" "journal".
    # A sophisticated planner would decompose this. An MVP planner might directly try actions.
    # We'll assume the MotivationalSystem sets this goal, and Planning attempts to achieve it.

    cml_module_configs: Dict[str, Dict[str, Any]] = {
        "perception": {"config_detail": "basic_text_processing"},
        "working_memory": {"capacity": 7}, # Example config
        "ltm": {
            "initial_knowledge": [ # Conceptual, actual LTM module handles how this is stored/used
                {"fact_type": "item_property", "item_name": "journal", "property": "is_readable", "value": True},
                {"fact_type": "action_knowledge", "action": "read", "requires_item_held": True},
                {"fact_type": "action_knowledge", "action": "take", "makes_item_held": True},
            ]
        },
        "planning": { # The planning module will need to be smart enough for this scenario
            "goal_decomposition_rules": { # Conceptual rules for an advanced planner
                "FIND_AND_READ": ["NAVIGATE_TO_ITEM_LOCATION", "TAKE_ITEM", "READ_ITEM"]
            },
            "default_item_locations_belief": {"journal": "study"} # Agent might 'believe' or 'learn' this
        },
        "behavior_generation": {"config_detail": "maps_primitives_to_text_actions"},
        "world_model": {"config_detail": "represents_rooms_objects_inventory"},
        "motivation": {
            "initial_goals": [
                {"goal_id": "read_journal_main", "type": "FIND_AND_READ", "item_name": "journal", "priority": 10.0}
            ]
        },
        "attention": {"default_focus_on_task": True},
        # Minimal configs for others for now
        "learning": {"learning_rate": 0.01},
        "emotion": {"default_mood": "neutral"},
        "self_model": {"confidence_threshold": 0.5},
        "tom": {"max_other_agents_simulated": 1},
        "communication": {"default_language": "english"},
    }

    # 3. Agent Instantiation
    # If ConcreteWorldModel is a placeholder, PiaAGIAgent will instantiate its own placeholder version.
    # Otherwise, we can instantiate and pass a specific one if needed.
    world_model_instance = None
    if not CML_PLACEHOLDERS_USED and ConcreteWorldModel is not None:
        world_model_instance = ConcreteWorldModel(config=cml_module_configs.get("world_model"), agent_id="pia_agent_info")

    pia_agent = PiaAGIAgent(
        agent_id="pia_agent_info",
        cml_module_configs=cml_module_configs,
        shared_world_model=world_model_instance
    )

    # 4. Engine Setup
    engine = BasicSimulationEngine(environment=environment, current_step_limit=20) # Limit steps
    engine.register_agent(agent_id="pia_agent_info", agent=pia_agent)

    # 5. Run Simulation
    print(f"\n--- Running Info Gathering Simulation (PiaAGIAgent) for max {engine.current_step_limit} steps ---")
    print(f"Goal: Agent should try to find and read the 'journal'. Starts in 'hallway'. Journal is on 'desk' in 'study'.\n")

    engine.run_simulation()

    print("\n--- Info Gathering Scenario (PiaAGIAgent) Ended ---")
    final_obs = environment.get_observation("pia_agent_info")
    if final_obs.custom_sensor_data:
        print(f"Final Agent Location: {final_obs.custom_sensor_data.get('current_location_id')}")
        print(f"Final Agent Inventory: {final_obs.custom_sensor_data.get('inventory_contents')}")
    # Check if journal was read (conceptual, environment/agent needs to log this)
    # For now, we'd look at the console output from the (placeholder) CML modules.


if __name__ == "__main__":
    run_info_gathering_scenario()

```
