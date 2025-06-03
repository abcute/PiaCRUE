# PiaAGI Agent Instantiation in PiaSE Guide

## Introduction

The purpose of this guide is to outline the conceptual design for instantiating a full PiaAGI agent within the PiaSE (PiaAGI Simulation Environment). A full agent is composed of multiple interconnected CML (Cognitive Module Library) modules, working together to perceive, learn, and act within a simulated environment. This guide details how such an agent class could be structured, how it would map to the `AgentInterface` required by PiaSE, and how it would be configured in a simulation scenario.

## Core `PiaAGIAgent` Class Design (Conceptual)

A central `PiaAGIAgent` class would serve as the primary container and orchestrator for all CML modules.

```python
from PiaSE.agent_interface import AgentInterface, PerceptionData, ActionCommand, PiaSEEvent # Hypothetical imports
from PiaCML import ( # Hypothetical imports for CML modules
    BasePerceptionModule, BaseWorkingMemoryModule, BaseLongTermMemoryModule,
    BasePlanningAndDecisionMakingModule, BaseBehaviorGenerationModule,
    BaseLearningModule, BaseSelfModelModule, BaseWorldModelModule,
    BaseMotivationalSystemModule, BaseEmotionModule
)
from typing import Dict, Any, Optional

class PiaAGIAgent(AgentInterface):
    def __init__(self, agent_id: str, cml_module_configs: Dict[str, Dict[str, Any]]):
        """
        Initializes the PiaAGI agent.

        Args:
            agent_id: A unique identifier for the agent.
            cml_module_configs: A dictionary where keys are module names (e.g., "PerceptionModule")
                                and values are dictionaries containing:
                                - "class": The concrete CML module class to instantiate.
                                - "params": A dictionary of parameters for the module's constructor.
        """
        super().__init__(agent_id)
        self.agent_id = agent_id

        # Instantiate CML modules based on configuration
        # Example for one module, repeat for all necessary modules
        if "PerceptionModule" in cml_module_configs:
            config = cml_module_configs["PerceptionModule"]
            self.perception_module: BasePerceptionModule = config["class"](**config["params"])
        else:
            self.perception_module = None # Or a default NullPerceptionModule

        if "WorkingMemoryModule" in cml_module_configs:
            config = cml_module_configs["WorkingMemoryModule"]
            self.working_memory_module: BaseWorkingMemoryModule = config["class"](**config["params"])
        else:
            self.working_memory_module = None

        if "LongTermMemoryModule" in cml_module_configs:
            config = cml_module_configs["LongTermMemoryModule"]
            self.ltm_module: BaseLongTermMemoryModule = config["class"](**config["params"])
        else:
            self.ltm_module = None

        if "WorldModelModule" in cml_module_configs:
            config = cml_module_configs["WorldModelModule"]
            self.world_model_module: BaseWorldModelModule = config["class"](**config["params"])
        else:
            self.world_model_module = None

        if "PlanningAndDecisionMakingModule" in cml_module_configs:
            config = cml_module_configs["PlanningAndDecisionMakingModule"]
            self.planning_module: BasePlanningAndDecisionMakingModule = config["class"](**config["params"])
        else:
            self.planning_module = None

        if "BehaviorGenerationModule" in cml_module_configs:
            config = cml_module_configs["BehaviorGenerationModule"]
            self.behavior_generation_module: BaseBehaviorGenerationModule = config["class"](**config["params"])
        else:
            self.behavior_generation_module = None

        if "LearningModule" in cml_module_configs:
            config = cml_module_configs["LearningModule"]
            self.learning_module: BaseLearningModule = config["class"](**config["params"]) # Potentially multiple learning modules
        else:
            self.learning_module = None

        if "SelfModelModule" in cml_module_configs:
            config = cml_module_configs["SelfModelModule"]
            self.self_model_module: BaseSelfModelModule = config["class"](**config["params"])
        else:
            self.self_model_module = None

        if "MotivationalSystemModule" in cml_module_configs:
            config = cml_module_configs["MotivationalSystemModule"]
            self.motivational_system_module: BaseMotivationalSystemModule = config["class"](**config["params"])
        else:
            self.motivational_system_module = None

        if "EmotionModule" in cml_module_configs:
            config = cml_module_configs["EmotionModule"]
            self.emotion_module: BaseEmotionModule = config["class"](**config["params"])
        else:
            self.emotion_module = None

        # ... and so on for all other core CML modules

        self._establish_inter_module_connections()

    def _establish_inter_module_connections(self):
        """
        Establishes necessary references between instantiated CML modules.
        This is highly dependent on the specific interfaces of the CML modules.
        """
        if self.working_memory_module and self.ltm_module:
            # Example: WM might need a reference to LTM for retrieval
            # self.working_memory_module.set_ltm_interface(self.ltm_module)
            pass
        if self.planning_module:
            # Planning module will likely need access to many other modules
            # self.planning_module.set_wm_interface(self.working_memory_module)
            # self.planning_module.set_ltm_interface(self.ltm_module)
            # self.planning_module.set_world_model_interface(self.world_model_module)
            # self.planning_module.set_self_model_interface(self.self_model_module)
            # self.planning_module.set_motivational_system_interface(self.motivational_system_module)
            pass
        # ... other connections as defined by CML module interaction patterns

    def perceive(self, observation: PerceptionData, event: Optional[PiaSEEvent] = None) -> None:
        """
        Processes incoming perception data from the environment.
        """
        if not self.perception_module or not self.working_memory_module or not self.world_model_module:
            # Log error or handle missing critical module
            return

        # 1. Perception module processes raw data
        processed_percepts = self.perception_module.process_observation(observation, event)

        # 2. Processed percepts are passed to Working Memory
        # The WM (potentially with its CE functions) integrates new percepts with existing content
        self.working_memory_module.update_from_perception(processed_percepts)

        # 3. World Model is updated based on new information in WM
        # This might be a direct call or mediated by WM/CE
        self.world_model_module.update_from_working_memory(self.working_memory_module.get_current_state())

        # (Optional) Trigger emotional appraisal based on percepts/WM changes
        if self.emotion_module:
            self.emotion_module.appraise(processed_percepts, self.working_memory_module.get_current_state())

    def act(self) -> ActionCommand:
        """
        Decides on an action to take in the environment.
        """
        if not self.planning_module or not self.behavior_generation_module:
            # Log error or return a default "no_action" command
            return ActionCommand(action_type="NO_OP")

        # 1. Motivational system (if present) updates goals in WM or influences planning
        if self.motivational_system_module:
            current_goals = self.motivational_system_module.get_active_goals(
                self.world_model_module.get_current_state(),
                self.self_model_module.get_self_representation() if self.self_model_module else None
            )
            # These goals would be available to the planning module, possibly via WM
            self.working_memory_module.update_goals(current_goals)


        # 2. Planning module generates a plan.
        # It interacts with WM (for current state, goals), LTM (for knowledge),
        # World Model (for predictions), Self Model (for capabilities/values), etc.
        plan = self.planning_module.generate_plan(
            self.working_memory_module.get_current_state(), # Includes goals
            self.ltm_module,
            self.world_model_module,
            self.self_model_module,
            self.emotion_module.get_current_affective_state() if self.emotion_module else None
        )

        # 3. Behavior Generation module converts the high-level plan into a concrete ActionCommand.
        action_command = self.behavior_generation_module.translate_plan_to_action(plan, self.world_model_module)

        return action_command

    def learn(self, feedback: Any) -> None: # `Any` should be a defined ActionResult type
        """
        Processes feedback from the environment/simulation about the last action.
        """
        if not self.learning_module:
            return

        # Route feedback to the learning module(s)
        # Learning module(s) will be responsible for:
        # - Updating LTM (e.g., new facts, skill refinement)
        # - Updating World Model (e.g., correcting predictions)
        # - Updating Self Model (e.g., adjusting confidence, learning new capabilities)
        # - Potentially influencing the Motivational System (e.g., goal satisfaction, curiosity reduction)
        # - Potentially influencing the Emotion Module (e.g., learning emotional responses)

        learning_outcomes = self.learning_module.process_feedback(
            feedback,
            self.working_memory_module.get_last_action_context(), # WM should store context of action that led to feedback
            self.world_model_module,
            self.ltm_module,
            self.self_model_module
        )

        # Apply updates based on learning_outcomes
        if self.ltm_module and "ltm_updates" in learning_outcomes:
            self.ltm_module.apply_updates(learning_outcomes["ltm_updates"])
        if self.world_model_module and "wm_updates" in learning_outcomes: # World Model updates
            self.world_model_module.apply_updates(learning_outcomes["wm_updates"])
        if self.self_model_module and "sm_updates" in learning_outcomes: # Self Model updates
            self.self_model_module.apply_updates(learning_outcomes["sm_updates"])

        # (Optional) Emotional state update based on learning/feedback
        if self.emotion_module:
            self.emotion_module.appraise_learning_outcome(feedback, learning_outcomes)


## Central Executive (CE) Realization

The Central Executive, as conceptualized in models like Baddeley's Working Memory model, is responsible for attentional control, cognitive flexibility, goal management, and coordinating subsidiary systems. In this `PiaAGIAgent` design:

*   **Orchestration:** A significant portion of CE functionality is realized by the `PiaAGIAgent` class itself. Its `perceive`, `act`, and `learn` methods define the high-level flow of information and control, orchestrating calls between different CML modules. For example, deciding when to invoke planning versus reactive behavior, or how to route perceptual information.
*   **Working Memory Module:** The `WorkingMemoryModule` itself would implement core CE functions like:
    *   Managing attentional focus (e.g., prioritizing certain information based on goals or salience).
    *   Maintaining and updating active goals.
    *   Coordinating information transfer between LTM and other modules.
    *   Buffering information for ongoing tasks.
*   **Planning Module:** Strategic planning and decision-making, key CE roles, are primarily handled by the `PlanningAndDecisionMakingModule`.
*   **Self-Model Module:** Metacognitive aspects of CE, such as self-monitoring and strategy selection, would involve the `SelfModelModule`.

Essentially, CE functions are distributed: the `PiaAGIAgent` provides the overarching structure, while specific modules (especially WM, Planning, Self-Model) implement detailed CE-like computations.

## Configuration in Scenarios

A PiaSE scenario script (e.g., a Python script or a YAML configuration file parsed by PiaSE) would need to:

1.  **Specify CML Module Implementations:** For each CML module slot in the `PiaAGIAgent` (e.g., `PerceptionModule`, `LongTermMemoryModule`), the scenario would define:
    *   The concrete class to use (e.g., `ConcreteTextPerceptionModule`, `GraphBasedLTMModule`).
    *   Specific initialization parameters for that class (e.g., LTM capacity, learning rate for the Learning Module, personality traits or ethical rules for the Self-Model, initial goals for the Motivational System).

    ```python
    # Example conceptual scenario configuration snippet
    agent_configs = {
        "agent_one": {
            "class": PiaAGIAgent, # The main agent class
            "cml_module_configs": {
                "PerceptionModule": {
                    "class": ConcreteTextPerceptionModule, # Specific CML class
                    "params": {"max_token_length": 512}
                },
                "WorkingMemoryModule": {
                    "class": ConcreteWorkingMemoryModule,
                    "params": {"capacity": 7, "executive_functions_enabled": True}
                },
                "LongTermMemoryModule": {
                    "class": SimpleKeyValueLTM,
                    "params": {"initial_facts": {"sky_is_blue": True}}
                },
                "PlanningAndDecisionMakingModule": {
                    "class": GoalOrientedPlanner,
                    "params": {"max_depth": 5}
                },
                # ... other modules like WorldModel, BehaviorGeneration, SelfModel, Motivation, Learning etc.
            }
        }
    }
    # PiaSE would then use these configs to instantiate the agent:
    # agent_one = agent_configs["agent_one"]["class"](
    # agent_id="agent_one",
    # cml_module_configs=agent_configs["agent_one"]["cml_module_configs"]
    # )
    ```

2.  **Instantiate `PiaAGIAgent`:** The PiaSE simulation engine would use these configurations to create an instance of `PiaAGIAgent`, passing the module configurations to its constructor.

## Example Data Flow for a Simple Task: "Agent sees a new object, decides to examine it"

1.  **Perception:**
    *   Environment (`TextBasedRoom`): "You see a small, ornate box on the table."
    *   `PiaAGIAgent.perceive()` is called with this observation.
    *   `PerceptionModule`: Processes the text, identifies "ornate box" as a salient object and "on the table" as its location. Generates structured percept: `{"object": "ornate_box", "location": "table", "is_new": True}`.
    *   `WorkingMemoryModule`: Receives the percept. Updates its current state: `{"objects_in_view": [{"id": "box1", "type": "ornate_box", "location": "table"}]}`. Notes "ornate_box" as new/requiring attention (CE function).
    *   `WorldModelModule`: Updates its representation: `{"table1": {"contains": ["box1"]}, "box1": {"type": "ornate_box", "properties": {"is_new": True}}}`.

2.  **Motivation & Goal Generation (Implicit/Explicit):**
    *   `MotivationalSystemModule` (if active and configured for curiosity): Detects a new, unexamined object ("ornate_box") in the World Model or WM. Generates an intrinsic goal: `{"goal_type": "EXAMINE", "target": "box1"}`.
    *   This goal is passed to `WorkingMemoryModule` or directly made available to `PlanningModule`.

3.  **Action Selection (`PiaAGIAgent.act()`):**
    *   `PlanningAndDecisionMakingModule`:
        *   Retrieves current state from `WorkingMemoryModule` (sees "box1").
        *   Retrieves active goals (e.g., `{"goal_type": "EXAMINE", "target": "box1"}` from Motivation/WM).
        *   Consults `LongTermMemoryModule` for knowledge about "ornate_box" (maybe none) or "examining" (e.g., "to examine, one must be near").
        *   Consults `WorldModelModule` to confirm location of "box1" and agent.
        *   Consults `SelfModelModule` to check capabilities (e.g., "can_manipulate_objects").
        *   Generates a plan: `[("APPROACH", "table1"), ("INTERACT", "box1", "examine")]`.
    *   `BehaviorGenerationModule`:
        *   Takes the first step of the plan: `("APPROACH", "table1")`.
        *   Translates this into a concrete `ActionCommand`: `{"action_type": "MOVE", "target_location": "coordinates_of_table1"}` or `{"action_type": "NAVIGATE_TO", "target_object_id": "table1"}`. If already at table, it might take `("INTERACT", "box1", "examine")` and translate to `{"action_type": "EXAMINE", "target_object_id": "box1"}`.

4.  **Learning (after action execution and feedback):**
    *   Assume agent executes `EXAMINE` and PiaSE provides feedback: `{"action_result": "SUCCESS", "new_observation": "The box is unlocked. Inside, you see a small key."}`.
    *   `PiaAGIAgent.learn()` is called.
    *   `LearningModule`:
        *   Receives feedback and the new observation.
        *   Updates `LongTermMemoryModule`: `{"box1": {"contains": "key1"}, "key1": {"type": "small_key"}}`. May also reinforce the "examine" action for "box" type objects if the outcome was positive.
        *   Updates `WorldModelModule` directly or via WM with the new information about "key1".
        *   Updates `SelfModelModule` if the examination was challenging and successful (e.g., increase confidence in examination skill).
        *   Updates `MotivationalSystemModule`: The "EXAMINE box1" goal might be marked as completed. New goals might arise based on "key1".

This flow illustrates the collaborative nature of the CML modules, orchestrated by the `PiaAGIAgent` class, to produce intelligent behavior.
---
PiaAGI_Research_Tools/PiaSE/Scenarios/Basic_Info_Gathering_Agent_Scenario.md
# PiaSE Scenario: Basic Information Gathering Agent

## Scenario Title

Basic Information Gathering Agent

## Objective

This scenario aims to demonstrate a PiaAGI agent using a core set of cognitive modules (Perception, Working Memory, Long-Term Memory, Planning, and Behavior Generation) to locate, retrieve, and read a specific item within a `TextBasedRoom` environment.

## PiaAGI Agent Configuration (Conceptual)

The PiaAGI agent for this scenario would be configured with the following CML modules:

*   **`PerceptionModule`**:
    *   **Concrete Class:** `ConcretePerceptionModule` (or a text-specialized version).
    *   **Configuration:** Optimized for processing textual descriptions of rooms, objects, and agent actions. Capable of identifying nouns (potential objects), verbs (potential actions), and spatial prepositions.
*   **`WorkingMemoryModule`**:
    *   **Concrete Class:** `ConcreteWorkingMemoryModule`.
    *   **Configuration:** Standard capacity. Central Executive functions active for managing current percepts, short-term goals (e.g., "find journal," "take journal"), and relevant LTM retrievals.
*   **`LongTermMemoryModule`**:
    *   **Concrete Class:** `ConcreteLongTermMemoryModule` (e.g., a simple semantic network or knowledge base).
    *   **Configuration:** Pre-populated with general knowledge relevant to the task, such as:
        *   "Journals are items."
        *   "Items can be picked up (taken)."
        *   "Journals can be read."
        *   "Reading provides information."
        *   "Containers (like 'desk drawer', 'chest') can hold items."
        *   "Containers need to be opened to access contents."
*   **`PlanningAndDecisionMakingModule`**:
    *   **Concrete Class:** `ConcretePlanningAndDecisionMakingModule`.
    *   **Configuration:** Capable of simple goal decomposition. For the goal "Read the journal," it should be able to generate a plan like:
        1.  IF journal location unknown THEN explore rooms to find journal.
        2.  IF journal found THEN navigate to journal's location.
        3.  IF journal in container THEN open container.
        4.  IF journal is accessible THEN take journal.
        5.  IF journal is held THEN read journal.
*   **`BehaviorGenerationModule`**:
    *   **Concrete Class:** `ConcreteBehaviorGenerationModule`.
    *   **Configuration:** Translates planned actions (e.g., "navigate to room B," "open desk_drawer," "take journal_item," "read journal_item") into valid `ActionCommand`s for the `TextBasedRoom` environment.
*   **`WorldModelModule`**:
    *   **Concrete Class:** `ConcreteWorldModel`.
    *   **Configuration:** Represents the state of the known environment, including:
        *   Rooms and their connections.
        *   Objects within rooms or containers, and their properties (e.g., `is_readable`, `is_container`, `is_open`).
        *   Agent's current location and inventory.
*   **Other Modules (Minimally Configured/Passive):**
    *   `MotivationalSystemModule`: May not be actively driving behavior if the goal "Read the journal" is explicitly given. If not, a simple "task completion" drive could be active.
    *   `EmotionModule`: Largely passive, though frustration could be modeled if the agent repeatedly fails.
    *   `SelfModelModule`: Basic representation of agent capabilities (e.g., "can move," "can take," "can read").
    *   `LearningModule`: Could be active to learn the journal's location or the contents of the journal, but not the primary focus for this scenario's objective.

## Environment

*   **Type:** `TextBasedRoom`
*   **Setup:**
    *   A small environment with 2-3 rooms (e.g., "Study," "Library," "Living Room").
    *   The target item, a "journal," is placed in a less obvious location, such as:
        *   Inside a container (e.g., a "desk drawer" in the Study).
        *   In a room different from the agent's starting room.
    *   Other distractor items might be present.
    *   Room descriptions provide clues about objects and potential exits.

## Task Description

The agent starts in a designated room (e.g., "Living Room").
The agent is given the explicit high-level goal: **"Read the journal."**

The agent must:
1.  Explore the environment if the journal's location is not immediately known.
2.  Identify the journal.
3.  If the journal is in a container, open the container.
4.  Take the journal.
5.  Execute the "read" action on the journal.

The scenario is successful when the agent performs the "read" action on the correct "journal" item.

## Key Interactions to Observe

*   **Perception & World Modeling:**
    *   How the agent parses room descriptions from the `TextBasedRoom` to identify objects, containers, and exits.
    *   How the `WorldModelModule` is updated with new information as the agent explores.
*   **Planning & Goal Decomposition:**
    *   How the `PlanningAndDecisionMakingModule` breaks down the high-level goal "Read the journal" into a sequence of sub-goals and actions (e.g., navigate, open, take, read).
    *   How the plan adapts if the journal is not found immediately or is inside a container.
*   **Navigation & Interaction:**
    *   Agent's movement between rooms.
    *   Agent's interaction with objects (e.g., `OPEN desk_drawer`, `TAKE journal from desk_drawer`).
*   **LTM Usage:**
    *   Evidence of the agent using pre-populated knowledge from LTM (e.g., knowing that journals are readable, or that containers might hold items).
*   **Action Execution:**
    *   Successful execution of the `READ journal` command and the subsequent information gain (if simulated by the environment).
*   **Error Handling (Optional Extension):**
    *   How the agent reacts if it tries to read a non-readable item.
    *   How it reacts if it tries to open a non-container object.
---
PiaAGI_Research_Tools/PiaSE/Scenarios/Motivated_Navigation_Agent_Scenario.md
# PiaSE Scenario: Simple Goal-Driven Navigation Agent with Motivation

## Scenario Title

Simple Goal-Driven Navigation Agent with Motivation

## Objective

This scenario aims to demonstrate a PiaAGI agent utilizing its Perception, Working Memory (WM), Long-Term Memory (LTM), Planning, Behavior Generation, World Model, and a simple Motivational System to navigate within a `GridWorld` environment. The scenario will explore both extrinsically defined goals and intrinsically generated goals.

## PiaAGI Agent Configuration (Conceptual)

The PiaAGI agent for this scenario would be configured with the following CML modules:

*   **`PerceptionModule`**:
    *   **Concrete Class:** `ConcretePerceptionModule`.
    *   **Configuration:** Processes grid-based perceptions (e.g., current cell (x,y), contents of adjacent cells, presence of obstacles or target markers).
*   **`WorkingMemoryModule`**:
    *   **Concrete Class:** `ConcreteWorkingMemoryModule`.
    *   **Configuration:** Standard capacity. Holds current location, immediate surroundings, and the active navigation goal.
*   **`LongTermMemoryModule`**:
    *   **Concrete Class:** `ConcreteLongTermMemoryModule`.
    *   **Configuration:** Stores learned spatial information about the `GridWorld` (e.g., visited cells, locations of obstacles, pathways). Initially, it might be empty or contain a partial map.
*   **`PlanningAndDecisionMakingModule`**:
    *   **Concrete Class:** `ConcretePlanningAndDecisionMakingModule`.
    *   **Configuration:** Implements a pathfinding algorithm (e.g., A*, Dijkstra's) to generate a sequence of moves towards the goal location provided by the Motivational System or an external directive. It uses information from the World Model and LTM.
*   **`BehaviorGenerationModule`**:
    *   **Concrete Class:** `ConcreteBehaviorGenerationModule`.
    *   **Configuration:** Translates planned navigation steps (e.g., "move north," "move to (3,4)") into valid `ActionCommand`s for the `GridWorld` environment (e.g., `{"action_type": "MOVE", "direction": "NORTH"}`).
*   **`WorldModelModule`**:
    *   **Concrete Class:** `ConcreteWorldModel`.
    *   **Configuration:** Represents the agent's current understanding of the `GridWorld`, including:
        *   The grid dimensions (if known).
        *   Agent's current coordinates (x,y).
        *   Properties of cells (e.g., traversable, obstacle, target_location, visited, unexplored).
*   **`MotivationalSystemModule`**:
    *   **Concrete Class:** `ConcreteMotivationalSystemModule`.
    *   **Configuration (Key for this scenario):**
        *   **Option A (Extrinsic Goal):** Can receive and prioritize an explicitly assigned goal, e.g., `{"goal_type": "REACH_LOCATION", "target_coordinates": (X, Y)}`.
        *   **Option B (Intrinsic Drive):**
            *   **Curiosity:** Configured with an intrinsic drive to explore. It identifies unexplored cells in the `WorldModelModule`'s representation and generates goals to visit them (e.g., `{"goal_type": "EXPLORE_CELL", "target_coordinates": (new_X, new_Y), "intensity": 0.7}`).
            *   **Competence/Achievement:** Configured with a drive to successfully navigate or reach waypoints. It might generate goals to re-attempt failed paths or reach challenging locations, with satisfaction upon success.
        *   The module outputs the currently active/highest priority goal to the `PlanningAndDecisionMakingModule` (likely via WM).

## Environment

*   **Type:** `GridWorld`
*   **Setup:**
    *   A 2D grid of varying size (e.g., 10x10 to 20x20).
    *   May contain obstacles (impassable cells).
    *   Specific cells can be designated as "target locations" or have properties like "unexplored."
    *   Agent has a starting position.
    *   Perception provides information about the agent's current cell and possibly adjacent cells.

## Task Description

The agent's primary task is to navigate the `GridWorld`. The specifics depend on the motivational configuration:

*   **Option A (Extrinsic Goal):**
    1.  The agent is given an explicit goal to navigate to a specific cell (X, Y) at the beginning of the simulation.
    2.  The `MotivationalSystemModule` adopts this as its primary active goal.
    3.  The agent must plan and execute a path to reach (X, Y).
    4.  Success is reaching (X, Y).

*   **Option B (Intrinsic Drive - e.g., Curiosity):**
    1.  The agent starts with no explicit target cell.
    2.  The `MotivationalSystemModule`'s "curiosity" drive is active. It scans the `WorldModelModule` (which is updated by perception and LTM) for unexplored cells.
    3.  It generates a goal to navigate to a nearby, accessible, unexplored cell. The selection criteria for "which" unexplored cell can vary (e.g., closest, one leading to largest unexplored region).
    4.  The agent plans and executes a path to this self-generated goal.
    5.  Upon reaching it, the cell is marked as explored. The `MotivationalSystemModule` might then generate a new exploration goal, or its "curiosity" for that specific cell is sated.
    6.  The scenario might run for a fixed number of steps or until a certain percentage of the grid is explored.

## Key Interactions to Observe

*   **Goal Generation & Prioritization (especially for Option B):**
    *   How the `MotivationalSystemModule` identifies potential goals (e.g., unexplored cells, designated targets).
    *   If multiple motivations/goals are possible, how one is selected or prioritized.
    *   The intensity or persistence of the motivation.
*   **Planning & Pathfinding:**
    *   The `PlanningAndDecisionMakingModule` generating a valid path to the goal, considering obstacles and known layout from the `WorldModelModule` and `LTM`.
    *   How plans are re-evaluated if new obstacles are discovered or the environment changes.
*   **Navigation & World Model Update:**
    *   Agent executing `MOVE` actions correctly.
    *   The `WorldModelModule` being updated with the agent's new position and information about newly perceived cells.
    *   The `LongTermMemoryModule` storing information about traversed paths and explored areas.
*   **Impact of Motivation (Optional Extension):**
    *   If the agent successfully reaches a goal, does the `MotivationalSystemModule` register satisfaction? Does this affect future goal generation (e.g., curiosity temporarily sated, competence drive reinforced)?
    *   If the agent fails or gets stuck, how does this impact motivation (e.g., frustration leading to goal abandonment, or increased drive to overcome the obstacle)?
    *   For intrinsic drives, observe the pattern of exploration – is it systematic, random, or guided by some heuristic emerging from the motivation?
---
