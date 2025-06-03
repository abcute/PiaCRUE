# PiaAGI Agent Instantiation in PiaSE Guide

## Introduction

The purpose of this guide is to outline the design and usage for instantiating a full PiaAGI agent within the PiaSE (PiaAGI Simulation Environment). A full agent is composed of multiple interconnected CML (Cognitive Module Library) modules, working together to perceive, learn, and act within a simulated environment. This guide details the `PiaAGIAgent` class structure, how it maps to the `AgentInterface` required by PiaSE, its configuration in scenarios, and the roles of its key components.

## Core `PiaAGIAgent` Class Design

The `PiaAGIAgent` class, located in `PiaAGI_Research_Tools/PiaSE/agents/pia_agi_agent.py`, serves as the primary container and orchestrator for all CML modules.

### Constructor (`__init__`)

The constructor initializes the agent and its cognitive modules:

```python
class PiaAGIAgent(AgentInterface):
    def __init__(self,
                 agent_id: str,
                 cml_module_configs: Optional[Dict[str, Optional[Dict]]] = None,
                 shared_world_model: Optional[BaseWorldModel] = None):
        # ... initialization logic ...
```

*   **`agent_id`**: A unique string identifier for the agent.
*   **`cml_module_configs`**: An optional dictionary where keys are CML module names (e.g., "perception", "ltm", "planning") and values are dictionaries containing specific configuration parameters for that module. These parameters are passed to the constructor of the respective concrete CML module. If a module's configuration is not provided, it may be instantiated with default settings or as a placeholder if the concrete class cannot be found.
*   **`shared_world_model`**: An optional instance of a class implementing `BaseWorldModel`. If provided, this instance is used as the agent's world model. If not provided, the `PiaAGIAgent` instantiates a `ConcreteWorldModel` (or its placeholder) using the configuration from `cml_module_configs.get("world_model")`.

### CML Module Instantiation and Inter-Module Connections

Inside the constructor, each CML module is instantiated. The `PiaAGIAgent` implementation attempts to import concrete CML module classes (e.g., `ConcretePerceptionModule`, `ConcreteWorkingMemoryModule`) from the `PiaAGI_Research_Tools.PiaCML` directory. If these imports fail, placeholder modules are used instead, allowing the agent to function structurally for testing or partial simulation.

Key inter-module connections are primarily established during the instantiation of the CML modules by **passing necessary references directly into their constructors**. For example:
*   The `world_model` instance is passed to the constructors of `PerceptionModule`, `LearningModule`, `MotivationalSystemModule`, `PlanningAndDecisionMakingModule`, and `TheoryOfMindModule`.
*   The `working_memory` instance is passed to `AttentionModule`, `PlanningAndDecisionMakingModule`, and `CommunicationModule`.
*   The `ltm` instance is passed to `LearningModule`, `PlanningAndDecisionMakingModule`, and `CommunicationModule`.
*   The `motivation_module` and `emotion_module` are passed to `PlanningAndDecisionMakingModule`.
*   The `self_model` is also intended to be passed to `PlanningAndDecisionMakingModule` (typically via a setter method like `set_self_model_reference` after both are initialized, due to mutual dependency considerations).

Some modules might also have dedicated setter methods for references if direct constructor injection isn't suitable for all connections (e.g., `working_memory.set_ltm_reference()`). This approach ensures that modules have the necessary access to other parts of the cognitive architecture they need to interact with.

## Mapping `AgentInterface` Methods to CML Operations

The `PiaAGIAgent` implements the standard `AgentInterface` methods (`perceive`, `act`, `learn`) by orchestrating operations across its CML modules.

*   **`perceive(self, observation: PerceptionData, event: Optional[PiaSEEvent] = None)`:**
    1.  The incoming `observation` is passed to `self.perception_module.process_sensory_input(observation)`.
    2.  The resulting `structured_percepts` are used to update `self.world_model.update_from_perception(structured_percepts)`.
    3.  `self.working_memory.update_workspace(...)` is called, integrating these percepts with current goals (from `self.motivation_module.get_active_goals()`) and emotional state (from `self.emotion_module.get_current_state()`).
    4.  If an `event` is provided, it's processed by `self.working_memory.process_event(event)`.
    5.  `self.attention_module.direct_attention(...)` is called, typically guided by salient information identified by the `WorkingMemoryModule` (e.g., `self.working_memory.get_salient_info()`).

*   **`act(self) -> ActionCommand`:**
    1.  Gathers necessary context:
        *   `current_wm_snapshot = self.working_memory.get_snapshot()`
        *   `active_goals = self.motivation_module.get_active_goals()`
        *   `world_model_state = self.world_model.get_current_snapshot()`
        *   `self_model_guidance = self.self_model.get_guidance()`
    2.  Invokes `self.planning_module.plan_for_goals(...)`, passing the gathered context. The planning module is expected to internally interact with LTM, World Model, Self-Model, Emotion, etc., as needed.
    3.  The `selected_plan_or_action_primitive` returned by planning is then passed to `self.behavior_generation.translate_to_env_action(...)` to produce a final `ActionCommand`.
    4.  If no plan is generated, a default "wait" `ActionCommand` is returned.

*   **`learn(self, feedback: ActionResult)`:**
    1.  The `feedback` is passed to `self.learning_module.process_feedback(...)`, along with current world model state and LTM access.
    2.  `self.self_model.update_from_experience(feedback)` allows the self-model to adapt.
    3.  If `feedback.details` contain specific `world_model_update_info`, `self.world_model.update_model(...)` is called.
    4.  `self.emotion_module.appraise_outcome(feedback)` updates emotional state.
    5.  `self.motivation_module.update_goal_status_from_feedback(feedback)` updates goal states.

## Central Executive (CE) Realization

The Central Executive's functions (coordination, attentional focus, goal management) are not implemented as a single, monolithic CML module. Instead, they are distributed:
*   **`PiaAGIAgent` Orchestration:** The `perceive`, `act`, and `learn` methods of `PiaAGIAgent` provide the high-level orchestration, deciding which modules to call in what sequence.
*   **`WorkingMemoryModule`:** This module is expected to manage the current conscious workspace, integrate information from various sources, maintain active goals, and implement lower-level executive functions like attentional filtering or task switching initiation.
*   **`AttentionModule`:** Works closely with Working Memory to direct focus.
*   **`PlanningAndDecisionMakingModule`:** Handles strategic thinking, goal decomposition, and selection of actions/plans.
*   **`MotivationalSystemModule`:** Manages goal priorities and generation.
*   **`SelfModelModule`:** Contributes metacognitive oversight and self-regulation.

## Key CML Modules and their Roles in `PiaAGIAgent`

The `PiaAGIAgent` orchestrates the following key CML modules:

*   **`PerceptionModule`**: Processes raw `PerceptionData` from the environment into a structured format suitable for internal use (e.g., identifying objects, events, textual content).
*   **`WorldModelModule`**: Maintains the agent's internal representation of the external environment's state, including objects, spatial relationships, and causal properties. Updated by perception and learning.
*   **`WorkingMemoryModule`**: Holds the currently active information, including processed percepts, retrieved LTM fragments, active goals, and emotional state. Acts as the "conscious workspace" and hosts some Central Executive functions.
*   **`LongTermMemoryModule (LTM)`**: Stores learned knowledge, skills, episodic memories, and semantic information. Queried by WM, Planning, and other modules. Updated by the Learning module.
*   **`AttentionModule`**: Directs the agent's focus towards salient information within working memory or incoming percepts, optimizing cognitive resource allocation.
*   **`MotivationalSystemModule`**: Generates, prioritizes, and manages the agent's goals (both intrinsic and extrinsic), providing the drive for action.
*   **`EmotionModule`**: Assesses situations and outcomes, generating emotional states that can influence perception, learning, decision-making, and motivation.
*   **`PlanningAndDecisionMakingModule`**: Formulates plans to achieve active goals, considering the current world state, agent capabilities (Self-Model), available knowledge (LTM), and context (WM).
*   **`BehaviorGenerationModule`**: Translates abstract plans or action intentions from the Planning module into concrete `ActionCommand`s executable by the environment.
*   **`SelfModelModule`**: Maintains a representation of the agent's own internal state, capabilities, beliefs about itself, values, and metacognitive assessments (e.g., confidence).
*   **`LearningModule`**: Responsible for updating the agent's knowledge (LTM), skills, and internal models (World Model, Self-Model) based on experience and feedback.
*   **`TheoryOfMindModule (ToM)`**: (More advanced) Models the mental states (beliefs, desires, intentions) of other agents.
*   **`CommunicationModule`**: (More advanced) Handles the generation and understanding of natural language or other communication modalities.

## Configuration in Scenarios

To use `PiaAGIAgent` in a PiaSE scenario, you need to provide configurations for its CML modules and instantiate it.

1.  **Define `cml_module_configs`:** This Python dictionary specifies parameters for each CML module. The exact parameters depend on the concrete implementation of each module.

    ```python
    # Example from 'basic_info_gathering_pia_agent_scenario.py'
    cml_module_configs: Dict[str, Dict[str, Any]] = {
        "perception": {"config_detail": "basic_text_processing"},
        "working_memory": {"capacity": 7},
        "ltm": {
            "initial_knowledge": [
                {"fact_type": "item_property", "item_name": "journal", "property": "is_readable", "value": True},
                {"fact_type": "action_knowledge", "action": "read", "requires_item_held": True},
            ]
        },
        "planning": {
            "goal_decomposition_rules": { # Conceptual for advanced planner
                "FIND_AND_READ": ["NAVIGATE_TO_ITEM_LOCATION", "TAKE_ITEM", "READ_ITEM"]
            },
            "default_item_locations_belief": {"journal": "study"}
        },
        "behavior_generation": {"config_detail": "maps_primitives_to_text_actions"},
        "world_model": {"config_detail": "represents_rooms_objects_inventory"}, # Config for the default ConcreteWorldModel if shared_world_model is None
        "motivation": {
            "initial_goals": [
                {"goal_id": "read_journal_main", "type": "FIND_AND_READ", "item_name": "journal", "priority": 10.0}
            ]
        },
        # Minimal configs for other modules for this scenario
        "attention": {"default_focus_on_task": True},
        "learning": {"learning_rate": 0.01},
        "emotion": {"default_mood": "neutral"},
        "self_model": {"confidence_threshold": 0.5},
        "tom": {},
        "communication": {},
    }
    ```
    *Note: The `PiaAGIAgent` currently uses placeholder modules if actual CML module imports fail. The configuration dictionary would still be passed to these placeholders.*

2.  **Instantiate `PiaAGIAgent`:**
    Create an instance of `PiaAGIAgent`, providing an `agent_id`, the `cml_module_configs`, and optionally, a pre-configured `shared_world_model`. If `shared_world_model` is not provided, the agent instantiates its own `ConcreteWorldModel` using the "world_model" entry from `cml_module_configs`.

    ```python
    from PiaAGI_Research_Tools.PiaSE.agents.pia_agi_agent import PiaAGIAgent
    # Assuming CML_PLACEHOLDERS_USED and ConcreteWorldModel are handled as in scenario files
    # For example:
    # if not CML_PLACEHOLDERS_USED:
    #     from PiaAGI_Research_Tools.PiaCML.concrete_world_model import ConcreteWorldModel
    # else:
    #     ConcreteWorldModel = None # PiaAGIAgent will use its placeholder

    agent_id = "pia_agent_1"

    # Option 1: Agent creates its own World Model
    # world_model_instance = None

    # Option 2: Provide a pre-configured shared World Model
    # (Ensure ConcreteWorldModel is the actual class or a compatible mock/placeholder)
    if ConcreteWorldModel: # Check if it's not None (due to placeholder logic)
         world_model_config = cml_module_configs.get("world_model", {})
         shared_world_model_instance = ConcreteWorldModel(config=world_model_config, agent_id=agent_id)
    else: # Fallback if ConcreteWorldModel couldn't be imported (agent will use its internal placeholder)
        shared_world_model_instance = None

    pia_agent = PiaAGIAgent(
        agent_id=agent_id,
        cml_module_configs=cml_module_configs,
        shared_world_model=shared_world_model_instance
    )

    # This agent instance can then be registered with the BasicSimulationEngine.
    ```

## Example Data Flow for a Simple Task: "Agent in hallway, goal to read journal in study"

This example is a simplified version of the `basic_info_gathering_pia_agent_scenario.py`.

1.  **Initialization:**
    *   `PiaAGIAgent` is initialized. `MotivationalSystemModule` has the goal: `{"type": "FIND_AND_READ", "item_name": "journal"}`. Agent starts in "hallway". Journal is on "desk" in "study".

2.  **First `act()` call:**
    *   `PiaAGIAgent.act()`:
        *   `WorkingMemoryModule.get_snapshot()`: Provides current state (e.g., location "hallway").
        *   `MotivationalSystemModule.get_active_goals()`: Returns `[{"type": "FIND_AND_READ", "item_name": "journal"}]`.
        *   `WorldModelModule.get_current_snapshot()`: Provides current world state.
        *   `SelfModelModule.get_guidance()`.
        *   `PlanningModule.plan_for_goals(...)`:
            *   Receives the "FIND_AND_READ" goal.
            *   Conceptual MVP Logic: Recognizes "journal" is not in inventory and not at current location "hallway". Believes "journal" is in "study" (from its config or LTM).
            *   Determines a high-level plan/action: `(NAVIGATE, "study")`.
        *   `BehaviorGenerationModule.translate_to_env_action((NAVIGATE, "study"))`: Returns `ActionCommand(action_type="navigate", parameters={"target_room_id": "study"})`.
    *   Agent executes this navigation action in `TextBasedRoom`.

3.  **First `perceive()` call (after navigating to study):**
    *   `PiaAGIAgent.perceive(observation_from_study, ...)`:
        *   `PerceptionModule.process_sensory_input(...)`: Parses text like "You are in the study. You see a desk. On the desk is a journal." into structured percepts: `[{"item": "desk"}, {"item": "journal", "location": "desk"}]`.
        *   `WorldModelModule.update_from_perception(...)`: Updates its state: "journal" is at "desk" in "study".
        *   `WorkingMemoryModule.update_workspace(...)`: Current percepts now include the journal. Goal is still active.
        *   `AttentionModule` might focus on "journal" as it's goal-relevant.

4.  **Second `act()` call:**
    *   `PiaAGIAgent.act()`:
        *   Context: In "study", "journal" visible on "desk", goal is "FIND_AND_READ journal".
        *   `PlanningModule.plan_for_goals(...)`:
            *   Conceptual MVP Logic: Sees "journal" is present but not held. Next step for "FIND_AND_READ" after navigation is "TAKE_ITEM".
            *   Determines plan/action: `(TAKE, "journal")`.
        *   `BehaviorGenerationModule.translate_to_env_action((TAKE, "journal"))`: Returns `ActionCommand(action_type="take", parameters={"item_name": "journal"})`.
    *   Agent executes "take journal".

5.  **Second `learn()` call (after taking journal):**
    *   `PiaAGIAgent.learn(feedback_from_take_action)`:
        *   `LearningModule` might reinforce "take" action for portable items.
        *   `SelfModelModule` might update confidence if successful.
        *   `WorldModelModule` is implicitly updated by the next perception (inventory change).
        *   `MotivationalSystemModule` might update sub-goal status (e.g., "FIND_ITEM" part is done).

6.  **Third `act()` call:**
    *   `PiaAGIAgent.act()`:
        *   Context: In "study", "journal" is in inventory. Goal "FIND_AND_READ journal".
        *   `PlanningModule.plan_for_goals(...)`:
            *   Conceptual MVP Logic: Journal is held. Final step for "FIND_AND_READ" is "READ_ITEM".
            *   Determines plan/action: `(READ, "journal")`.
        *   `BehaviorGenerationModule.translate_to_env_action((READ, "journal"))`: Returns `ActionCommand(action_type="read", parameters={"item_name": "journal"})`.
    *   Agent executes "read journal". Scenario goal achieved (conceptually).

This simplified flow illustrates how the `PiaAGIAgent` uses its modules to progress through a multi-step task, driven by a high-level goal from its motivational system. The actual sophistication depends on the concrete implementations of the CML modules, especially Planning and LTM.
```
