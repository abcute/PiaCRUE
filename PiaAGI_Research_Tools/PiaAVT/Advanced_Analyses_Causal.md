# Causal Analysis Module for PiaAVT (Conceptual Design)

## 1. Introduction/Purpose of Causal Analysis in PiaAVT

Understanding *why* an AGI agent behaves a certain way, makes specific decisions, or undergoes particular internal changes is crucial for its development, debugging, and ethical oversight. While many analyses in PiaAVT can reveal correlations and patterns, a dedicated Causal Analysis module aims to provide tools and methodologies to help researchers infer potential causal relationships from observational log data.

The primary purpose of this module is not to definitively prove causation (which is often impossible from purely observational data without controlled experiments) but to:

*   Generate plausible causal hypotheses about the agent's functioning.
*   Identify factors that are likely to influence specific outcomes or changes.
*   Provide insights that can guide further investigation, agent design modifications, or targeted experiments.
*   Support explainability by constructing narratives of likely cause-and-effect chains.

This module will be particularly important for analyzing complex emergent behaviors and the impact of various internal cognitive processes (from PiaCML) and environmental interactions (from PiaSE) on the agent's overall performance and development.

## 2. Types of Causal Links to Investigate

PiaAVT's Causal Analysis module should aim to investigate a variety of relationships relevant to AGI. Examples include:

*   **Agent Action -> Environmental Outcome:**
    *   `AGENT_ACTION_EXECUTED_IN_ENV` -> `ENVIRONMENT_STATE_CHANGED` (e.g., action "pickup_object_X" leads to object_X no longer being at its original location).
    *   `AGENT_COMMUNICATION_SENT` -> `EXTERNAL_AGENT_RESPONSE_RECEIVED` (e.g., agent's message leads to a specific reply from another agent).
*   **Environmental Event -> Agent Internal State:**
    *   `ENVIRONMENT_EVENT_OCCURRED` (e.g., sudden loud noise) -> `EMOTION_STATE_UPDATED` (e.g., increase in arousal, negative valence).
    *   `PERCEPTION_INPUT_PROCESSED` (e.g., observing a novel object) -> `GOAL_CREATED` (e.g., intrinsic curiosity goal to explore).
    *   `USER_FEEDBACK_RECEIVED` (e.g., positive reinforcement) -> `AGENT_SELF_MODEL_UPDATED` (e.g., increased confidence in a skill).
*   **Internal State/Process -> Agent Behavior/Performance:**
    *   `AGENT_INTERNAL_STATE_UPDATED` (e.g., high cognitive_load) -> `TASK_PERFORMANCE_METRICS` (e.g., increased error rate, slower response time on a subsequent task).
    *   `LTM_QUERY_RESULT` (e.g., retrieval of relevant knowledge) -> `PLANNING_PROCESS_UPDATE` (e.g., successful plan generation, specific plan chosen).
    *   `EMOTION_STATE_UPDATED` (e.g., high frustration) -> `AGENT_BEHAVIOR_MODIFIED` (e.g., disengagement from current task, switch to different strategy).
    *   `MOTIVATIONAL_STATE_UPDATED` (e.g., high priority goal activated) -> `AGENT_ACTION_SELECTED`.
*   **Learning/Developmental Processes -> Capabilities:**
    *   `LEARNING_MODULE_UPDATE` (e.g., after skill practice) -> `SKILL_PROFICIENCY_ASSESSMENT` (e.g., improved score on a test task).
    *   `ETHICAL_RULE_ACTIVATED` -> `DECISION_OUTCOME_ASSESSED` (e.g., decision aligns with ethical principles).
*   **Cross-Modular Influences (within PiaCML):**
    *   `WORKING_MEMORY_STATE_CHANGED` (e.g., capacity exceeded) -> `ATTENTION_FOCUS_SHIFTED`.
    *   `EMOTION_STATE_UPDATED` -> `MOTIVATIONAL_SALIENCE_CALCULATED` (e.g., emotional state influences goal salience).

## 3. Proposed Methodologies and Algorithms

Inferring causality from observational time-series data is challenging. The module should explore a combination of techniques, clearly stating their assumptions and limitations.

*   **Granger Causality:**
    *   **Applicability:** Useful for time-series data where one variable's past values might predict another's future values. E.g., Do spikes in "cognitive load" (time-series A) systematically precede drops in "task performance scores" (time-series B)?
    *   **Method:** Vector Autoregression (VAR) models are fitted to see if lagged values of X improve the prediction of Y, beyond Y's own lagged values.
    *   **Limitations:**
        *   Assumes temporal precedence implies causality (post hoc ergo propter hoc fallacy if not careful).
        *   Sensitive to data stationarity, choice of lag length, and sampling frequency.
        *   Prone to confounding variables (a third variable Z might be causing both X and Y).
        *   Strictly about prediction, not necessarily mechanistic causality.
*   **Bayesian Networks (BNs):**
    *   **Applicability:** Modeling probabilistic dependencies between a set of variables. Can represent complex interactions and incorporate prior knowledge.
    *   **Method:** Structure learning algorithms (e.g., PC algorithm, Hill-Climbing) can learn the Directed Acyclic Graph (DAG) structure from data. Parameter learning then estimates conditional probabilities.
    *   **Limitations:**
        *   Learning BN structure from observational data is NP-hard; heuristics are used.
        *   Resulting graph may not be unique (equivalent models exist).
        *   Requires careful variable selection and discretization of continuous variables if needed.
        *   Susceptible to hidden confounders. Can represent "X causes Y" but doesn't prove it without intervention.
*   **Propensity Score Matching (PSM) / Inverse Probability of Treatment Weighting (IPTW):**
    *   **Applicability:** When trying to estimate the effect of a "treatment" (e.g., a specific agent action, learning strategy, or configuration) compared to a "control" (e.g., different action, no action, default strategy). Useful when controlled experiments are not feasible.
    *   **Method:**
        *   PSM: Matches agents/time-periods that received the treatment with those that didn't, based on a set of observed covariates (the propensity score).
        *   IPTW: Weights samples by the inverse probability of receiving the treatment they actually received, to create a pseudo-population where treatment assignment is independent of observed confounders.
    *   **Limitations:**
        *   Only accounts for *observed* confounders. Unobserved confounders can still bias results.
        *   Requires sufficient overlap in propensity scores between treated and control groups.
        *   "Treatment" definition must be clear from logs.
*   **Causal Inference with Counterfactual Reasoning (Conceptual Support):**
    *   **Applicability:** Answering "what if" questions (e.g., "What if the agent hadn't accessed knowledge X, would it still have succeeded?").
    *   **Method (PiaAVT Support):** PiaAVT itself won't perform full counterfactual inference, which often requires a structural causal model (SCM). However, it can support it by:
        *   Allowing users to define SCMs (perhaps graphically or via DSL) based on their domain knowledge and hypotheses.
        *   Extracting relevant data to parameterize such models.
        *   Integrating with external libraries (e.g., DoWhy, CausalNex) that can perform counterfactual queries on user-defined SCMs using the log data.
    *   **Limitations:** Heavily reliant on the correctness of the user-supplied causal model and assumptions.
*   **Difference-in-Differences (DiD):**
    *   **Applicability:** If an "intervention" (e.g., new algorithm update, environmental change) occurs at a specific time for a subset of agents or scenarios.
    *   **Method:** Compares the change in an outcome variable over time between the "treated" group and a "control" group that did not experience the intervention.
    *   **Limitations:** Requires a parallel trends assumption (i.e., both groups would have followed similar trends in the absence of treatment). Needs clear treatment/control groups and pre/post intervention data.

**General Limitation:** Correlation does not imply causation. All these methods provide evidence or generate hypotheses, but definitive causal claims usually require controlled experimentation where possible. The module must clearly communicate these limitations.

## 4. Required Log Data Specifications

To support the above methodologies, detailed and well-structured logs are essential. PiaAVT would rely on the `Logging_Specification.md` being rich enough. Key requirements include:

*   **Universal Requirements:**
    *   `timestamp`: High-precision, synchronized timestamps for all events.
    *   `event_id`: Unique identifier for each event, useful for tracing specific trigger-impact chains.
    *   `simulation_run_id`: To distinguish different simulation runs.
    *   `agent_id`: To attribute events and states to specific agents, especially in multi-agent scenarios.
*   **For Agent Action -> Environmental Outcome:**
    *   `AGENT_ACTION_EXECUTED_IN_ENV`:
        *   `event_data`: `action_name`, `parameters` (e.g., target_object_id, coordinates), `intended_outcome_description`.
    *   `ENVIRONMENT_STATE_CHANGED`:
        *   `event_data`: `changed_aspect` (e.g., "object_X_position"), `old_value`, `new_value`, `source_of_change` (e.g., "agent_Y_action_Z").
*   **For Environmental Event -> Agent Internal State:**
    *   `ENVIRONMENT_EVENT_OCCURRED`:
        *   `event_data`: `event_description` (e.g., "loud_noise"), `properties` (e.g., intensity, location).
    *   `PERCEPTION_INPUT_PROCESSED`:
        *   `event_data`: `stimulus_id`, `modality`, `detected_features`, `novelty_score`, `salience_score`.
    *   `EMOTION_STATE_UPDATED`:
        *   `event_data`: `current_vad` (valence, arousal, dominance), `delta_vad`, `triggering_event_ids_or_types`.
    *   `GOAL_CREATED`:
        *   `event_data`: `goal_id`, `type` (e.g., INTRINSIC_CURIOSITY), `source_trigger_event_id`, `initial_priority`.
    *   `AGENT_SELF_MODEL_UPDATED`:
        *   `event_data`: `updated_component` (e.g., "skill_X_confidence"), `old_value`, `new_value`, `reason_or_trigger_event_id`.
*   **For Internal State/Process -> Agent Behavior/Performance:**
    *   `AGENT_INTERNAL_STATE_UPDATED`:
        *   `event_data`: `state_variable` (e.g., "cognitive_load", "resource_level_X"), `value`. This needs to be logged frequently for time-series analysis.
    *   `LTM_QUERY_RESULT`:
        *   `event_data`: `query_content`, `retrieved_knowledge_ids_or_summary`, `success_status`, `relevance_score`.
    *   `PLANNING_PROCESS_UPDATE`:
        *   `event_data`: `status` (e.g., "started", "plan_generated", "failed"), `selected_plan_id_if_any`, `considered_options_count`.
    *   `TASK_PERFORMANCE_METRICS`: (Could be part of `TASK_STATUS_UPDATE` or a separate event)
        *   `event_data`: `task_id`, `metric_name` (e.g., "completion_time_sec", "error_count"), `value`.
*   **General Needs for Causal Discovery:**
    *   Logging of **confounders**: As many potential influencing factors as possible should be logged (e.g., agent's current resource levels, overall environmental complexity, active goals when an action is chosen).
    *   **Clear identifiers**: `event_id`, `goal_id`, `task_id`, `stimulus_id` that can be used to link related events across different log entries and components.

## 5. Conceptual Examples of Use Cases

*   **Use Case 1: Impact of Cognitive Load on Task Performance**
    *   **Question:** Does sustained high cognitive load (logged via `AGENT_INTERNAL_STATE_UPDATED`) lead to a decrease in task success rates or an increase in task completion times (logged via `TASK_PERFORMANCE_METRICS`) for subsequent tasks?
    *   **Method:** Granger causality analysis on time series of cognitive load and performance metrics. Bayesian Network to model dependencies.
    *   **PiaAVT Role:** Extract relevant time series, provide tools for Granger analysis, help visualize BN.
*   **Use Case 2: Effectiveness of a New Learning Strategy**
    *   **Question:** Does enabling a new "curiosity-driven exploration" strategy (treatment) lead to faster acquisition of a specific skill compared to a baseline strategy (control)?
    *   **Method:** Propensity Score Matching. Match agents/episodes based on initial skill levels, environmental complexity, etc., then compare skill improvement rates.
    *   **PiaAVT Role:** Extract covariate data, help identify treatment/control groups from logs (e.g., based on `AGENT_CONFIGURATION_UPDATED` or `STRATEGY_SELECTED` events), calculate outcome metrics.
*   **Use Case 3: Tracing Back Goal Failures**
    *   **Question:** A specific goal (`goal_id_X`) repeatedly fails. What are the likely preceding events or states that contribute to its failure?
    *   **Method:**
        *   Identify all `GOAL_STATE_CHANGED` to "FAILED" for `goal_id_X`.
        *   Use sequence analysis (from EventSequencer) to find common event patterns preceding failure.
        *   Construct a local Bayesian Network around the goal failure event, incorporating preceding agent states, actions, and environmental events.
    *   **PiaAVT Role:** Log querying, sequence analysis, BN visualization and data extraction for BN tools.

## 6. Challenges and Future Directions

*   **Scalability:** Causal discovery algorithms can be computationally intensive, especially with high-dimensional data from complex AGI agents.
*   **Hidden Confounders:** The "unknown unknowns" problem. Observational data can rarely capture all potential confounding variables.
*   **Model Validation:** Validating inferred causal links is difficult. Where possible, hypotheses generated by this module should be tested via controlled experiments in PiaSE.
*   **User Interface:** Designing an intuitive UI for users to specify causal queries, select variables, choose methods, and interpret results (which are often probabilistic and model-dependent).
*   **Assumptions Management:** Clearly documenting the assumptions underlying each causal inference method and helping users assess if these assumptions are met by their data.
*   **Integration with other PiaAVT Modules:** Causal analysis should leverage results from pattern mining, state visualization, and statistical analysis to help users formulate hypotheses.
*   **Incremental Causal Discovery:** Developing methods that can update causal models as new log data streams in.

Future work will focus on implementing robust versions of a few selected algorithms, providing strong support for data extraction and linking with external causal inference libraries, and developing effective visualizations for causal hypotheses.
