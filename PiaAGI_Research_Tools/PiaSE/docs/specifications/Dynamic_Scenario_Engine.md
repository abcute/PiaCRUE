# PiaSE: Dynamic Scenario Engine for Developmental Scaffolding - Conceptual Design

## 1. Introduction and Goals

*   **Purpose:** To significantly enhance PiaSE's scenario management capabilities to support dynamic, adaptive scenarios. This engine is a core component for implementing PiaAGI's Developmental Scaffolding principles, allowing the simulation environment to intelligently guide an agent's learning and development over extended periods.
*   **Goals:**
    *   **Curriculum Execution:** Systematically execute sequences of learning experiences and tasks as defined in `DevelopmentalCurricula` designed within PiaPES.
    *   **Adaptive Scenarios:** Modify scenario parameters (environment complexity, task difficulty, agent configurations, hints, or even cognitive tools provided) in real-time or between simulation segments. This adaptation will be based on the agent's observed performance, its current developmental stage, and the logic embedded within the active curriculum.
    *   **Progression Management:** Manage and meticulously track an agent's progression through long-term developmental pathways, potentially spanning multiple simulated "days," "weeks," or distinct learning phases.
    *   **Research Enablement:** Facilitate empirical research into effective scaffolding strategies for Artificial General Intelligence (AGI) by providing a flexible platform for designing, deploying, and analyzing adaptive learning environments.

## 2. Core Components and Their Interactions

The Dynamic Scenario Engine (DSE) would be composed of several interconnected modules:

*   **`CurriculumManager`:**
    *   **Responsibilities:**
        *   Loading and parsing `DevelopmentalCurriculum` definitions (likely from JSON files exported by PiaPES).
        *   Maintaining and tracking the agent's progress within the loaded curriculum (e.g., current `CurriculumStep` ID, list of completed steps, achieved milestones or learning objectives, number of attempts per step).
        *   Selecting the next appropriate `CurriculumStep` based on the curriculum's sequential logic, branching conditions, or adaptation decisions.
    *   **State:** Stores the active `DevelopmentalCurriculum` object, the agent's current position/state within that curriculum, and a history of the agent's progression (e.g., performance on past steps, adaptations applied).
    *   **Interaction:**
        *   Interfaces with PiaPES (conceptually, by reading its output files).
        *   Provides the target `CurriculumStep` to the `ScenarioSetupModule`.
        *   Receives adaptation decisions from the `AdaptationDecisionModule` to guide step selection (e.g., repeat, branch, proceed).

*   **`ScenarioSetupModule` (Potentially an enhanced part of `BasicSimulationEngine`'s initialization/reset logic):**
    *   **Responsibilities:** Given a `CurriculumStep` object from the `CurriculumManager` and a target PiaAGI agent instance:
        *   Loads the PiaAGI Prompt (e.g., a detailed configuration script or LLM prompt) referenced in the `CurriculumStep`.
        *   Populates any placeholders within the prompt using dynamic values. These values might come from the curriculum's state (e.g., difficulty parameters), the agent's self-model, or performance history.
        *   Configures or re-configures the PiaAGI agent instance using the processed prompt. This could involve setting parameters for CML modules, loading specific knowledge into LTM, or initializing motivational states, as defined in `PiaAGI.md` and `PiaAGI_Prompt_Engineering_Suite.md`.
        *   Configures, reinitializes, or modifies the PiaSE `Environment` instance according to the `CurriculumStep`'s requirements (e.g., loading a specific map in `CraftingWorld`, setting up interactors in `SocialDialogueSandbox`, adjusting resource availability).
    *   **Interaction:** Receives `CurriculumStep` from `CurriculumManager`. Interacts directly with the PiaAGI agent object and the active `Environment` object.

*   **`AdaptationDecisionModule`:**
    *   **Responsibilities:** Evaluates conditions for scenario adaptation or curriculum progression based on the agent's performance and the rules defined in the curriculum.
        *   Receives the current `CurriculumStep` (which contains adaptation rules) from the `CurriculumManager`.
        *   Queries the `PiaAVTInterface` to obtain relevant agent performance metrics, learning indicators, or specific logged events from the recently completed simulation segment.
    *   **Logic:** Implements the conditional logic defined within the `adaptation_rules` of a `CurriculumStep`. Examples:
        *   "IF `piaavt_metric_task_completion_time` > `step_defined_threshold_time` AND `attempts_on_step` < 3 THEN `decision_provide_hint_script_A`."
        *   "IF `piaavt_metric_key_concept_understanding` < 0.6 THEN `decision_branch_to_remedial_step_R12`."
        *   "IF `piaavt_metric_successful_interaction_ratio` > 0.8 THEN `decision_proceed_to_next_step`."
    *   **Output:** Produces an adaptation decision object, e.g., `{"decision_type": "PROCEED_NEXT", "target_step_id": "Step_5B"}` or `{"decision_type": "REPEAT_MODIFIED", "modifications": [{"target": "environment", "method": "adjust_difficulty", "params": {"reduction": 0.1}}, {"target": "agent_config", "hint_level_override": 2}]}`.
    *   **Interaction:** Gets data from `CurriculumManager` and `PiaAVTInterface`. Sends its decision back to the `CurriculumManager`.

*   **`EnvironmentModifierInterface` (A new conceptual interface to be implemented by PiaSE `Environment` classes):**
    *   **Responsibilities:** Defines a standardized set of methods that `Environment` objects (like `CraftingWorld` or `SocialDialogueSandbox`) must expose to allow the DSE to dynamically alter the live environment or its setup parameters.
    *   **Example Methods:**
        *   `env.adjust_difficulty(parameter_name: str, new_value: Any)` (e.g., reduce enemy count, increase resource availability).
        *   `env.introduce_element(element_type: str, element_config: Dict)` (e.g., add a new tool, spawn a helpful NPC).
        *   `env.remove_element(element_id: str)`
        *   `env.provide_indirect_hint(hint_details: Dict)` (e.g., highlight an object, make a sound near a relevant item).
        *   `env.modify_interactor_behavior(interactor_id: str, new_behavior_profile: Dict)` (for social environments).
    *   **Interaction:** The `ScenarioSetupModule` or a dedicated part of the DSE would call these methods on the current environment instance based on decisions from the `AdaptationDecisionModule`.

*   **`PiaAVTInterface`:**
    *   **Responsibilities:** Provides a stable API for the `AdaptationDecisionModule` to query analyzed data from PiaAVT's data store. This decouples the DSE from the specifics of PiaAVT's internal data structures.
    *   **Queries might include:**
        *   `get_metric_value(agent_id, metric_name, time_window)`
        *   `check_event_occurrence(agent_id, event_type_pattern, time_window)`
        *   `get_agent_internal_state_summary(agent_id, state_variable_name)` (if PiaAVT can infer/track such things).
    *   **Assumptions:** PiaAVT is running (potentially asynchronously or in batch mode between steps), processing simulation logs generated by PiaSE, and making its analysis results accessible through this interface.

## 3. Workflow of a Dynamic Scenario

A typical operational loop for the DSE would be:

1.  **Curriculum Initialization:**
    *   An agent is selected for development.
    *   The `CurriculumManager` loads the relevant `DevelopmentalCurriculum` for that agent's type and current developmental stage (e.g., "PiaSapling - Basic Tool Use Curriculum").
    *   The agent's progress within this curriculum is initialized (or loaded if resuming).

2.  **Step Execution Cycle:**
    1.  **Step Selection:** `CurriculumManager` determines the current or next `CurriculumStep` based on progression history and curriculum logic.
    2.  **Scenario Setup:** `ScenarioSetupModule` receives the `CurriculumStep`.
        *   It fetches and processes the associated PiaAGI Prompt (from PiaPES specifications).
        *   It configures/re-configures the PiaAGI agent instance.
        *   It configures/resets the designated PiaSE `Environment` instance.
    3.  **Simulation Run:** The PiaSE `BasicSimulationEngine` (or a similar controller) runs the simulation for the configured step. This might be for a fixed number of simulation ticks, until a specific goal within the scenario is met by the agent, or until a human evaluator intervenes. All interactions, agent states, and environment events are logged (standard PiaSE logging which PiaAVT consumes).

3.  **Performance Evaluation & Adaptation Decision:**
    1.  Upon completion of the simulation segment for the step, the `AdaptationDecisionModule` is invoked.
    2.  It queries the `PiaAVTInterface` for performance data relevant to the just-completed activities (e.g., task success, efficiency metrics, errors, use of specific cognitive functions, emotional state trajectory).
    3.  It applies the `adaptation_rules` defined in the current `CurriculumStep` to this performance data.
    4.  It generates an adaptation decision (e.g., proceed, repeat, modify, branch, provide hint).

4.  **Progression and Modification Cycle:**
    1.  The `CurriculumManager` receives the adaptation decision.
    2.  **If "Proceed":** The `CurriculumManager` updates the agent's progress and selects the next step in the sequence. Loop back to Step Execution (2.1).
    3.  **If "Adapt/Repeat":**
        *   The `CurriculumManager` might log the attempt and decide to repeat the current step.
        *   The `ScenarioSetupModule` could be invoked to reconfigure the agent or environment based on modification parameters in the decision (e.g., simplify task, activate hint systems in the agent's cognitive configuration).
        *   Alternatively, the `EnvironmentModifierInterface` might be used to make immediate, less drastic changes to the *live* environment for an immediate retry if the curriculum step allows for such micro-adaptations.
        *   Loop back to Step Execution (2.2 or 2.3).
    4.  **If "Branch":** The `CurriculumManager` updates progress and selects a different, specified `CurriculumStep` (e.g., a remedial module or an advanced track). Loop back to Step Execution (2.1).
    5.  **If "Provide Hint":** A hint (could be a textual message, a modification to agent's WM, or an environment highlight via `EnvironmentModifierInterface`) is delivered. The agent might then re-attempt the last part of the step or the step might be subtly altered.

This cycle continues, allowing the agent to progress through the curriculum in an adaptive manner.

## 4. Data Model for `DevelopmentalCurriculum` (PiaPES) - Key Aspects for DSE

The DSE heavily relies on a well-defined `DevelopmentalCurriculum` structure from PiaPES. Key attributes of this structure relevant to the DSE include:

*   `curriculum_id`: Unique identifier.
*   `name`: Human-readable name.
*   `description`: Purpose and overview.
*   `target_developmental_stage`: (e.g., "PiaSeedling", "PiaSapling_ModuleFocus_ToM").
*   `steps: List[CurriculumStep]`: An ordered or graph-based sequence of learning steps.

Each `CurriculumStep` object within `steps` must contain fields like:

*   `step_id`: Unique identifier within the curriculum.
*   `order` or `prerequisites`: To define sequence or dependencies.
*   `prompt_reference`: Identifier for the PiaAGI Prompt to be used for this step (defines agent's base configuration, task, goals).
*   `environment_id`: Specifies which PiaSE environment to use (e.g., "CraftingWorld_v1", "SocialDialogueSandbox_FriendshipScenario").
*   `environment_config_overrides`: A dictionary of specific parameters to configure the chosen environment for this step (e.g., `{"map_file": "easy_map.json", "initial_resources": {"wood": 5}}` for CraftingWorld).
*   `agent_config_overrides`: Specific cognitive parameters for the agent that might override or supplement what's in the base prompt (e.g., `{"LearningModule": {"learning_rate": 0.01}, "SelfModelModule": {"active_hints": ["hint_type_A"]}}`).
*   `completion_criteria`: A list of conditions that signify successful completion of this step. These conditions must be verifiable by the `AdaptationDecisionModule`, often by querying PiaAVT.
    *   Examples: `{"metric": "task_goal_achieved", "value": true, "source": "PiaSE_Environment_Feedback"}`
    *   `{"metric": "PiaAVT_Analysis_X_Result", "operator": ">", "threshold": 0.85, "source": "PiaAVTInterface"}`
    *   `{"type": "manual_approval", "evaluator_role": "human_supervisor"}`
*   `adaptation_rules`: A list of `(condition, action)` tuples, where `condition` is a logical expression evaluated against PiaAVT metrics or step state, and `action` specifies what the DSE should do if the condition is true.
    *   Example Condition: `{"metric": "PiaAVT_Metric_A", "operator": "<", "value": 0.5, "window": "current_step"}`
    *   Example Action: `{"type": "APPLY_HINT_SCRIPT", "script_id": "Hint_Script_1_For_Step_X"}`
    *   Example Action: `{"type": "BRANCH_TO_STEP", "target_step_id": "Remedial_Step_R12"}`
    *   Example Action: `{"type": "MODIFY_ENVIRONMENT", "modifications": [{"method": "adjust_difficulty", "params": {"change": -0.1}}]}`
    *   Example Action: `{"type": "MODIFY_AGENT_CONFIG", "config_overrides": {"SelfModelModule": {"show_detailed_errors": true}}}`
*   `max_attempts`: Optional maximum number of times this step can be attempted before forcing a branch or curriculum failure.
*   `time_limit`: Optional time limit for this step within the simulation.

## 5. Interfacing with PiaPES and PiaAVT

*   **PiaPES:**
    *   The DSE is a primary consumer of the `DevelopmentalCurriculum` JSONs (or similar structured format) produced by the PiaPES `DevelopmentalCurriculumDesigner`.
    *   PiaPES must provide the capability for curriculum designers to specify the detailed `completion_criteria` and `adaptation_rules` within each `CurriculumStep`, using vocabulary and metric references that the DSE and PiaAVT can understand.
    *   PiaPES will also define the `PiaAGIPrompt` templates referenced by `prompt_reference`.

*   **PiaAVT:**
    *   The DSE (via `PiaAVTInterface`) needs a robust and efficient mechanism to query analysis results from PiaAVT.
    *   PiaAVT must be capable of processing the rich logs generated by PiaSE, performing the analyses specified by various PiaAGI components (including those relevant to curriculum milestones), and exposing these results.
    *   This could be via a REST API, a shared database, or message queues if near real-time adaptation is required. The specific metrics and event patterns PiaAVT tracks must be known to curriculum designers in PiaPES and to the `AdaptationDecisionModule`.

## 6. Challenges and Future Considerations

*   **Complexity of Adaptation Rules:** Designing effective, non-trivial `adaptation_rules` will be complex and is a research area in itself. Rules need to be robust enough to avoid negative feedback loops or premature advancement.
*   **PiaAVT Real-time Analysis:** If adaptations need to occur very frequently (e.g., within a single complex task), the latency of PiaAVT's analysis pipeline could be a bottleneck. Some metrics might need to be estimated or provided more directly by the environment or agent for rapid feedback.
*   **Agent State Management:** Deciding how much of an agent's internal state (WM, LTM, emotional state) persists or is reset/modified across adapted or repeated steps is crucial and complex. This needs to be configurable by the curriculum.
*   **Credit Assignment:** When an agent fails or succeeds, attributing this to the agent's capabilities, the task difficulty, or the appropriateness of the scaffolding is a hard problem.
*   **User Interface (UI/UX):** A sophisticated UI will be needed for:
    *   Monitoring the DSE's execution and the agent's progress through a curriculum.
    *   Visualizing why certain adaptations were triggered.
    *   Allowing human supervisors to potentially override DSE decisions or manually approve steps.
*   **Defining "Performance":** Establishing a comprehensive set of metrics in PiaAVT that truly reflect an AGI's learning and development (beyond simple task scores) is an ongoing challenge.
*   **Curriculum Authoring Tools:** The expressiveness required for `adaptation_rules` and `completion_criteria` will necessitate powerful authoring tools within PiaPES.
