from typing import Dict, Any

from PiaAGI_Research_Tools.PiaSE.core_engine.basic_simulation_engine import BasicSimulationEngine
from PiaAGI_Research_Tools.PiaSE.environments.text_based_room import TextBasedRoom, RoomLayout, ObjectDetail
from PiaAGI_Research_Tools.PiaSE.agents.pia_agi_agent import PiaAGIAgent, CML_PLACEHOLDERS_USED

# Import ConcreteWorldModel if not using placeholders, otherwise PiaAGIAgent handles it.
if not CML_PLACEHOLDERS_USED:
    from PiaAGI_Research_Tools.PiaCML.concrete_world_model import ConcreteWorldModel
else: # PiaAGIAgent will use its placeholder for ConcreteWorldModel
    ConcreteWorldModel = None


def run_comprehensive_info_gathering_scenario(): # Renamed function
    print("--- Starting Comprehensive Info Gathering Scenario with PiaAGIAgent ---") # Updated print
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
        "perception": {
            "supported_modalities_override": ["text", "simple_visual_cue"] # Conceptual
        },
        "working_memory": {
            "capacity": 15 # Increased from default
        },
        "ltm": { # Existing config seems reasonable, LTM constructor is simple
            "knowledge_domains": ["general_knowledge", "agent_domain", "scenario_specific_lore"], # Kept from original intent
            "initial_knowledge": [
                {"fact_type": "item_property", "item_name": "journal", "property": "is_readable", "value": True},
                {"fact_type": "action_knowledge", "action": "read", "requires_item_held": True},
                {"fact_type": "action_knowledge", "action": "take", "makes_item_held": True},
            ],
            "enable_episodic_memory_decay": False # Conceptual
        },
        "attention": {
            "default_focus_strategy": "goal_oriented_then_novelty", # Conceptual
            "salience_update_rate": 0.1 # Conceptual
        },
        "learning": {
            "default_learning_rate": 0.01,
            "enable_emotional_influence_on_learning": True, # Conceptual
            "ethical_guardrail_sensitivity": 0.8 # Conceptual
        },
        "motivation": {
            "initial_goals": [
                {"description": "Successfully find and read the journal.", "type": "EXTRINSIC_TASK", "initial_priority": 9.0, "initial_status": "ACTIVE", "item_name": "journal"},
                {"description": "Explore the study environment.", "type": "INTRINSIC_CURIOSITY", "initial_priority": 3.0, "initial_status": "PENDING"}
            ],
            "curiosity_settings": {"novelty_weight": 0.6, "relevance_to_active_goals_weight": 0.2} # Conceptual
        },
        "emotion": {
            "initial_vad_state": {"valence": 0.05, "arousal": 0.1, "dominance": 0.0}, # Slightly positive, calm
            "personality_profile": {"reactivity_modifier_arousal": 0.9, "default_mood_valence": 0.05} # Conceptual
        },
        "planning": { # Existing config is good, expanded slightly
            "goal_decomposition_rules": {
                "FIND_AND_READ": ["NAVIGATE_TO_ITEM_LOCATION", "TAKE_ITEM", "READ_ITEM"],
                "EXPLORE_ROOM": ["LOOK_AROUND", "INTERACT_WITH_INTERESTING_OBJECTS"]
            },
            "default_item_locations_belief": {"journal": "study"},
            "max_plan_depth": 5, # Conceptual
            "enable_re_planning_on_failure": True # Conceptual
        },
        "behavior_generation": {
            "behavior_mapping_accuracy": 0.98, # Conceptual
            "allow_improvisation_level": 0.1 # Conceptual
        },
        "self_model": {
            "initial_ethical_rules": [
                {"rule_id": "ScenarioRule001", "principle": "InformationIntegrity", "description": "Do not alter information in the journal.", "priority_level": "high", "implication": "impermissible"},
                {"rule_id": "ScenarioRule002", "principle": "ExplorationCaution", "description": "Be cautious when exploring new areas.", "priority_level": "medium", "implication": "requires_caution"}
            ],
            "initial_self_attributes": {"agent_id": "PiaPrime_InfoSeeker", "current_developmental_stage": "scenario_test_mode"}
        },
        "tom": { # Theory of Mind
            "default_inference_confidence_level": 0.35, # Conceptual
            "max_other_agents_to_model": 3 # Conceptual
        },
        "communication": {
            "default_communication_language": "en-US",
            "enable_contextual_strategy_switching": True, # Conceptual
            "max_dialogue_history_turns": 15
        },
        "world_model": { # Conceptual, assuming WM can process initial entities
            "initial_entities": [
                {"id": "study_desk_wm", "type": "desk", "state": {"description": "The main desk in the study."}, "location_id": "study"},
                {"id": "journal_wm", "type": "journal", "state": {"description": "A leather-bound journal, possibly readable."}, "location_id": "study_desk_wm"}
            ],
            "prediction_time_horizon_default_s": 5.0 # Conceptual
        }
    }

    print("\n--- Agent Configuration ---")
    for module_name_key, config_dict in cml_module_configs.items():
        # Convert module_name_key from snake_case to Title Case for printing
        module_display_name = module_name_key.replace('_', ' ').title()
        # Special handling for "ltm" to "Long Term Memory"
        if module_name_key == "ltm":
            module_display_name = "Long Term Memory"
        elif module_name_key == "tom":
            module_display_name = "Theory Of Mind"

        print(f"  {module_display_name}:")
        if config_dict:
            for key, value in config_dict.items():
                # For lists of dicts (like initial_knowledge, initial_goals, initial_ethical_rules, initial_entities), print a summary
                if isinstance(value, list) and value and all(isinstance(item, dict) for item in value):
                    print(f"    {key}: (list of {len(value)} dicts)")
                    for i, item_dict in enumerate(value[:2]): # Print first 2 items as sample
                        print(f"      - Item {i+1}: {str(item_dict)[:100]}{'...' if len(str(item_dict)) > 100 else ''}")
                    if len(value) > 2:
                        print(f"      ... and {len(value) - 2} more items.")
                else:
                    print(f"    {key}: {value}")
        else:
            print("    (default or no specific config)")
    print("-------------------------\n")

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
    run_comprehensive_info_gathering_scenario() # Renamed function call

```
