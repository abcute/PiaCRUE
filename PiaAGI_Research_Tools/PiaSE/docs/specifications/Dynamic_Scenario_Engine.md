# PiaSE: Dynamic Scenario Engine for Developmental Scaffolding - Conceptual Design

## 1. Introduction and Goals

*   **Purpose:** To significantly enhance PiaSE's scenario management capabilities to support dynamic, adaptive scenarios. This engine is a core component for implementing PiaAGI's Developmental Scaffolding principles, allowing the simulation environment to intelligently guide an agent's learning and development over extended periods.
*   **Goals:**
    *   **Curriculum Execution:** Systematically execute sequences of learning experiences and tasks as defined in `DevelopmentalCurricula` (JSON format, conceptually designed in PiaPES).
    *   **Adaptive Scenarios:** Modify scenario parameters (environment complexity, task difficulty, agent configurations, hints, or even cognitive tools provided) in real-time or between simulation segments. This adaptation is based on the agent's observed performance (via `PiaAVTInterface`), its current developmental stage, and the logic embedded within the active curriculum.
    *   **Progression Management:** Manage and meticulously track an agent's progression through long-term developmental pathways, potentially spanning multiple simulated "days," "weeks," or distinct learning phases. This includes tracking attempts per step.
    *   **Research Enablement:** Facilitate empirical research into effective scaffolding strategies for Artificial General Intelligence (AGI) by providing a flexible platform for designing, deploying, and analyzing adaptive learning environments.

## 2. Core Components and Their Interactions

The Dynamic Scenario Engine (DSE) is composed of several interconnected modules, primarily found in `PiaAGI_Research_Tools/PiaSE/core_engine/dynamic_scenario_engine.py`.

*   **`CurriculumManager`:**
    *   **Responsibilities:**
        *   Loading and parsing `DevelopmentalCurriculum` definitions from JSON files.
        *   Maintaining and tracking agent progress: `agent_progress: Dict[agent_id, {"current_step_order": int, "completed_steps": List[int], "step_attempts": {step_order: count}}]`.
        *   Selecting the next `CurriculumStep` based on sequential order or branching decisions from the `AdaptationDecisionModule`.
        *   Key Methods: `load_curriculum_from_file()`, `initialize_agent_progress()`, `get_next_step()`, `set_current_step()`, `complete_step()`, `get_current_step_object()`, `get_step_attempts()`, `get_step_by_name_or_order()`.
    *   **State:** Stores the loaded `current_curriculum` and the `agent_progress` dictionary.
    *   **Interaction:** Provides current step information to the main simulation engine and `AdaptationDecisionModule`; updates agent progress based on decisions.

*   **`ScenarioSetupModule` (Conceptual - Currently part of `BasicSimulationEngine`'s DSE integration logic):**
    *   **Responsibilities:** Given a `CurriculumStep` and an agent:
        *   (Future) Load and process a `PiaAGIPrompt` referenced in the `CurriculumStep`.
        *   Apply `agent_config_overrides` from the `CurriculumStep` to the agent (e.g., updating motivational goals, as seen in `dynamic_scaffolding_scenario.py` where the agent's `configure` method is used).
        *   Apply `environment_config_overrides` from the `CurriculumStep` to the current PiaSE `Environment` instance (e.g., reconfiguring `GridWorld` with new `goal_pos`, `obstacles` as demonstrated in `dynamic_scaffolding_scenario.py`).
    *   **Interaction:** Triggered by the main engine when a new curriculum step begins or needs modification.

*   **`AdaptationDecisionModule`:**
    *   **Responsibilities:** Evaluates conditions for adaptation or progression. Receives data from `CurriculumManager` (current step logic, attempt counts) and `PiaAVTInterface` (agent performance metrics).
    *   **Logic:** Implements rules defined in a `CurriculumStep`'s `adaptation_rules` (list of `[condition_string, action_string]` tuples) and checks `completion_criteria` (list of `{"metric": ..., "operator": ..., "value": ...}` dictionaries).
        *   Conditions like `"step_attempts >= 3"` or `"metric_name == value"` are parsed and evaluated.
    *   **Output:** Returns a decision string (e.g., "PROCEED", "REPEAT_STEP", "BRANCH_TO_X", "APPLY_HINT_Y", "FAIL_CURRICULUM").
    *   **Key Methods:** `evaluate_step_completion()`, `evaluate_adaptation_rules()`.
    *   **Interaction:** Initialized with a `PiaAVTInterface`. Called by the main simulation engine after a curriculum step attempt.

*   **`EnvironmentModifierInterface` (Conceptual Interface):**
    *   **Responsibilities:** Defines methods that `Environment` objects could implement to allow dynamic changes by the DSE (e.g., `env.adjust_difficulty(params)`, `env.introduce_element(element_config)`). Not yet implemented in base environments.
    *   **Interaction:** Would be called by the DSE orchestrator or `ScenarioSetupModule` based on adaptation decisions.

*   **`PiaAVTInterface` (ABC, with `MockPiaAVTInterface` implementation):**
    *   **Responsibilities:** Provides an API for the `AdaptationDecisionModule` to query agent performance metrics and event occurrences.
    *   **Key Methods:** `get_performance_metric()`, `check_event_occurred()`.
    *   **MVP Status:** Currently, `MockPiaAVTInterface` is used, requiring scenario scripts or test harnesses to manually call `set_metric()` to simulate AVT providing data (as seen in `dynamic_scaffolding_scenario.py`).

## 3. Workflow of a Dynamic Scenario within `BasicSimulationEngine`

The `BasicSimulationEngine` has been enhanced to manage the DSE lifecycle.

1.  **Curriculum Initialization (in `engine.initialize()`):**
    *   If `agent_curricula` (a dict mapping `agent_id` to curriculum filepaths) is provided to `engine.initialize()`, the DSE components (`CurriculumManager`, `AdaptationDecisionModule`, `MockPiaAVTInterface`) are instantiated.
    *   For each agent with an assigned curriculum:
        *   The curriculum JSON is loaded via `curriculum_manager.load_curriculum_from_file()`.
        *   `curriculum_manager.initialize_agent_progress()` is called.
        *   The first step is fetched using `curriculum_manager.get_next_step()` and then set as current using `curriculum_manager.set_current_step()`, which also records the first attempt.
        *   Conceptual: The `environment_config` and `agent_config_overrides` from this first step are applied. In `dynamic_scaffolding_scenario.py`, the agent's `configure()` method is called with `agent_config_overrides`, and the environment is expected to be reconfigured by the engine based on `environment_config`.

2.  **Step Execution Cycle (within `engine.run_simulation()`):**
    *   The main simulation loop iterates for a total number of global steps.
    *   For each DSE-managed agent:
        1.  **Get Current Step:** `current_step_obj = curriculum_manager.get_current_step_object(agent_id)`. If no step, curriculum is done for this agent.
        2.  **Log Attempt:** DSE logs the start of the step attempt, including attempt number.
        3.  **(Conceptual) Scenario Reconfiguration:** Before running interactions, the engine (conceptually via `ScenarioSetupModule`) would apply `current_step_obj.environment_config` to the environment and `current_step_obj.agent_config_overrides` to the agent. The `dynamic_scaffolding_scenario.py` shows how an agent's `configure()` method can be used for this.
        4.  **Inner Interaction Loop:** The engine runs a number of standard agent-environment interaction steps (perception, action, learning via `_run_agent_env_interaction_step()`). This loop runs for `current_step_obj.max_interactions` times or until `environment.is_done(agent_id)` signals completion for that specific attempt.
        5.  **(MVP) Performance Data Simulation:** After interactions for a step attempt, in the `dynamic_scaffolding_scenario.py`, the scenario script manually updates `engine.avt_interface.set_metric()` based on the environment state (e.g., if agent reached goal coordinates). This simulates PiaAVT providing data.

3.  **Performance Evaluation & Adaptation Decision (within `engine.run_simulation()`):**
    1.  **Check Completion:** `is_complete = adaptation_module.evaluate_step_completion(agent_id, current_step_obj)`.
    2.  **Get Adaptation Rule:** If complete, decision is usually "PROCEED". If not, `decision = adaptation_module.evaluate_adaptation_rules(agent_id, current_step_obj, attempt_count)`. `attempt_count` is retrieved via `curriculum_manager.get_step_attempts()`.

4.  **Handle DSE Decision (within `engine.run_simulation()`):**
    *   **"PROCEED":** `curriculum_manager.complete_step()`; then `next_step = curriculum_manager.get_next_step()`. If `next_step`, it's set via `curriculum_manager.set_current_step()`. If no next step, curriculum is finished.
    *   **"REPEAT_STEP":** `curriculum_manager.set_current_step(agent_id, current_step_obj.order, increment_attempt=True)` (stays on same step, increments attempt count).
    *   **"BRANCH_TO_X":** `branch_target = curriculum_manager.get_step_by_name_or_order(X)`; then `curriculum_manager.set_current_step(agent_id, branch_target.order)`.
    *   **"APPLY_HINT_Y":** A `PiaSEEvent` with hint data (from `current_step_obj.hints`) can be posted via `engine.post_event()`. The agent then re-attempts the current step (attempt count incremented).
    *   **"FAIL_CURRICULUM":** DSE becomes inactive for the agent.
    *   The loop continues to the next global step or next agent.

## Integration with `BasicSimulationEngine`

The `BasicSimulationEngine` (`PiaAGI_Research_Tools/PiaSE/core_engine/basic_engine.py`) has been updated to integrate and manage the DSE components.

*   **Initialization:**
    *   The `initialize` method of `BasicSimulationEngine` now accepts an optional `agent_curricula: Dict[str, str]` parameter. This dictionary maps agent IDs to their curriculum JSON filepaths.
    *   If `agent_curricula` is provided, the engine instantiates `CurriculumManager`, `AdaptationDecisionModule`, and `MockPiaAVTInterface`.
    *   It then iterates through the `agent_curricula`, loads each curriculum, initializes agent progress, and sets the first step for each DSE-managed agent.

    ```python
    # Conceptual snippet from a scenario script:
    # from PiaAGI_Research_Tools.PiaSE.core_engine.basic_simulation_engine import BasicSimulationEngine
    # from PiaAGI_Research_Tools.PiaSE.environments.grid_world import GridWorld
    # from MyAgents.rule_based_grid_agent import RuleBasedGridAgent # Example agent

    # env = GridWorld(...)
    # agent = RuleBasedGridAgent("agent1", ...)

    # curriculum_filepath = "PiaAGI_Research_Tools/PiaSE/scenarios/curricula/simple_grid_curriculum.json"
    # agent_curricula_map = {agent.get_id(): curriculum_filepath}

    # engine = BasicSimulationEngine()
    # engine.initialize(
    #     environment=env,
    #     agents={agent.get_id(): agent},
    #     agent_curricula=agent_curricula_map,
    #     scenario_config={"name": "MyDSEScenario"},
    #     log_path="logs/my_dse_scenario.jsonl"
    # )
    # engine.run_simulation(num_steps=200)
    ```

*   **`run_simulation` Loop:**
    *   The main simulation loop in `BasicSimulationEngine` now distinguishes between DSE-managed agents and non-DSE agents.
    *   For DSE-managed agents, it orchestrates the curriculum step lifecycle: setting up the step (conceptually applying environment/agent configs), running a specified number of environment interactions (`max_interactions` from `CurriculumStep`), evaluating step completion and adaptation rules, and then handling the DSE's decision (proceed, repeat, branch, etc.).
    *   This DSE logic is embedded within the global step loop, meaning one curriculum step attempt (including its `max_interactions`) typically occurs within one global simulation step for that agent. If `max_interactions` is large, a single curriculum step attempt could span what seems like multiple "turns" of agent activity.

## 4. Data Model for `DevelopmentalCurriculum` (PiaPES) - Key Aspects for DSE

The DSE relies on a structured `DevelopmentalCurriculum` (loaded from JSON). Key fields within a `CurriculumStep` that are utilized by the DSE MVP include:

*   `order`: Determines sequence.
*   `name`: Human-readable identifier.
*   `prompt_reference`: (Conceptual) Points to a detailed prompt for agent/environment setup for the step.
*   `max_interactions`: (Newer field, used by `BasicSimulationEngine`) Specifies how many agent-environment interaction cycles (perceive-act-learn) constitute one attempt at this step.
*   `completion_criteria: List[Dict]`: Defines conditions for successfully completing the step (e.g., `[{"metric": "reached_goal_1", "operator": "==", "value": true}]`).
*   `adaptation_rules: List[Tuple[str, str]]`: Defines conditional adaptations (e.g., `[["step_attempts >= 3", "PROCEED"], ["metric_X < 10", "APPLY_HINT_01"]]`).
*   `environment_config_overrides: Dict`: Specifies parameters to reconfigure the environment for this step (e.g., `GridWorld`'s `goal_pos`, `obstacles`).
*   `agent_config_overrides: Dict`: Specifies parameters to reconfigure the agent for this step (e.g., changing motivational goals, as seen in `dynamic_scaffolding_scenario.py` where `agent.configure()` is called with these overrides).
*   `hints: Dict`: (Optional) Contains data for hints that can be triggered by adaptation rules (e.g., `{"HINT_01": {"type": "EVENT", "event_type": "ENVIRONMENT_HINT", "data": {"message": "..."}}}`).

The `simple_grid_curriculum.json` provides a concrete example of this structure.

## 5. Interfacing with PiaPES and PiaAVT

*   **PiaPES:** The DSE's `CurriculumManager` loads curriculum JSONs. While placeholders for `DevelopmentalCurriculum` and `CurriculumStep` are available within `dynamic_scenario_engine.py`, ideally these would align with or be the actual classes defined in PiaPES if PiaPES is used as the curriculum authoring tool.
*   **PiaAVT:** The `AdaptationDecisionModule` uses a `PiaAVTInterface`. The current implementation includes a `MockPiaAVTInterface` where performance metrics must be manually set (e.g., by the scenario script, as shown in `dynamic_scaffolding_scenario.py`) to simulate PiaAVT's output. A real integration would involve PiaAVT analyzing logs and providing these metrics through a live interface.

## 6. Challenges and Future Considerations

*   **ScenarioSetupModule Implementation:** A dedicated `ScenarioSetupModule` needs full implementation to robustly handle loading `PiaAGIPrompt` files (from PiaPES) and applying complex configurations to both agents (especially full `PiaAGIAgent`) and environments at the start of each curriculum step, based on `prompt_reference`, `agent_config_overrides`, and `environment_config_overrides`.
*   **Real PiaAVT Integration:** Connecting to a live PiaAVT instance for real-time or near real-time performance metrics.
*   **Complex Rule/Condition Engine:** The current MVP parsing of conditions in `AdaptationDecisionModule` is simple. A more robust solution (e.g., using a dedicated rule engine or a small DSL) would be needed for complex logic.
*   **Environment Modifier Implementation:** Environments need to implement the `EnvironmentModifierInterface` to allow DSE to make dynamic changes (e.g., `adjust_difficulty`, `provide_indirect_hint`).
*   **Agent State Persistence/Reset:** Defining how much of an agent's state (LTM, emotional state, etc.) persists between curriculum steps versus what is reset or reconfigured by the step's prompt needs careful design.
*   **User Interface:** A UI for authoring curricula (PiaPES) and for monitoring DSE execution and agent development will be crucial for usability.
```
