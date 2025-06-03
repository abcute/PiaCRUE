# Behavioral Pattern Mining Module for PiaAVT (Conceptual Design)

## 1. Introduction/Purpose of Behavioral Pattern Mining in PiaAVT

AGI agents, particularly those with complex cognitive architectures like PiaAGI, will generate vast amounts of log data detailing their actions, internal state changes, and interactions. Manually sifting through this data to find meaningful behavioral regularities, anomalies, or developmental trends is often intractable. The Behavioral Pattern Mining module in PiaAVT aims to provide tools and techniques to automatically discover and analyze these patterns.

The primary purposes of this module are:

*   **Understanding Agent Behavior:** To identify typical ways an agent responds to situations, sequences its actions, or transitions between internal states.
*   **Debugging and Anomaly Detection:** To flag unusual or unexpected behaviors that might indicate bugs, flawed reasoning, or unforeseen consequences of learning.
*   **Assessing Learning and Development:** To track how behaviors emerge, change, or stabilize over time as the agent learns and develops.
*   **Generating Hypotheses:** Discovered patterns can form the basis for hypotheses about the agent's underlying cognitive processes, strategies, and knowledge.
*   **Improving Agent Design:** Insights from behavioral patterns can inform refinements to the agent's architecture, algorithms, or learning environment.

This module will complement other analysis tools in PiaAVT by providing a more data-driven approach to uncovering complex behavioral structures.

## 2. Types of Behavioral Patterns to Identify

The module should be capable of identifying a diverse range of patterns:

*   **Frequent Sequences:**
    *   **Action Sequences:** Common sequences of `AGENT_ACTION_EXECUTED_IN_ENV` events, potentially conditioned on context (e.g., current task, environmental state). (e.g., "scan_area -> approach_object -> grasp_object" is frequent when 'exploration_goal' is active).
    *   **Cognitive State Transitions:** Typical progressions of internal states, e.g., `EMOTION_STATE_UPDATED` sequences (calm -> curious -> engaged) or `MOTIVATIONAL_STATE_UPDATED` (goal_A_active -> goal_B_active).
    *   **Task Phase Sequences:** Common sequences of `TASK_STATUS_UPDATE` events (e.g., STARTED -> SUBTASK_A_COMPLETED -> SUBTASK_B_COMPLETED -> COMPLETED_SUCCESS).
*   **Co-occurring Events (Association Rules):**
    *   Identifying events or states that frequently occur together or in close temporal proximity. (e.g., "If `COGNITIVE_LOAD_HIGH` and `CURRENT_TASK_COMPLEXITY_HIGH`, then `ERROR_RATE_INCREASED` is likely within the next N events").
    *   Correlations between specific `LTM_CONTENT_ACCESSED` events and subsequent `PLAN_ADOPTED` events.
*   **Interaction Loops:**
    *   **Agent-Environment Loops:** Recurring cycles of agent actions and specific environmental responses (e.g., agent pushes button -> light turns on -> agent observes light -> agent pushes button again).
    *   **Agent-Agent Loops (for multi-agent systems):** Common conversational patterns or sequences of reciprocal actions between agents.
*   **Behavioral Clusters:**
    *   Grouping similar episodes of behavior based on features extracted from log segments (e.g., action types, duration, intensity, accompanying internal states). This could reveal distinct behavioral "styles" or strategies.
    *   Clustering agent internal states to identify common cognitive or emotional "modes" of operation.
*   **Anomalous Patterns (Outliers):**
    *   **Anomalous Sequences:** Action or state sequences that are rare or deviate significantly from established frequent patterns.
    *   **Anomalous Event Parameters:** Events with unusual `event_data` values compared to the norm for that event type (e.g., an action with an extremely long execution time).
*   **Developmental Patterns:**
    *   **Emergence/Disappearance of Behaviors:** Tracking the frequency or characteristics of specific patterns over longer time scales (across multiple simulation runs or extended learning periods) to see when new behaviors appear or old ones are extinguished.
    *   **Changes in Behavioral Complexity:** Quantifying changes in the length, diversity, or structure of behavioral sequences over time.
    *   **Stabilization of Strategies:** Identifying when an agent's approach to a particular type of problem (represented by a behavioral pattern) becomes consistent.
*   **Contextual Patterns:**
    *   Identifying how patterns vary across different contexts (e.g., different environmental states, active goals, agent configurations, or presence of other agents).

## 3. Proposed Methodologies and Algorithms

A variety of data mining and machine learning techniques can be adapted:

*   **Sequence Mining Algorithms:**
    *   **GSP (Generalized Sequential Patterns), PrefixSpan, SPADE:** For discovering frequent subsequences in a database of sequences (e.g., sequences of agent actions, event types).
    *   **Applicability:** Core for finding frequent action sequences, state transitions.
    *   **Limitations:** Can generate a very large number of patterns; requires careful setting of support thresholds; may not capture context well without specialized sequence definitions.
*   **Association Rule Mining:**
    *   **Apriori, FP-Growth, Eclat:** To find "if-then" rules about co-occurring items in event baskets (e.g., "if event A and event B occur, then event C also occurs with X% probability").
    *   **Applicability:** Useful for finding correlations between discrete events or states within defined time windows.
    *   **Limitations:** Can also generate many rules; interpretation of "interestingness" (beyond support and confidence) is key; temporal aspects might need pre-processing.
*   **Clustering Algorithms:**
    *   **K-Means, Hierarchical Clustering:** For grouping similar items based on feature vectors. Behavioral episodes could be featurized (e.g., counts of action types, average emotional state, duration).
    *   **DBSCAN:** For density-based clustering, useful for finding clusters of arbitrary shape and identifying outliers.
    *   **Applicability:** Grouping similar behavioral episodes or agent internal state configurations.
    *   **Limitations:** Choice of distance metric and number of clusters (for K-Means) can be challenging; featurization of complex behaviors is non-trivial.
*   **Anomaly Detection Algorithms:**
    *   **Isolation Forest, One-Class SVM, Autoencoders:** For identifying data points that are different from the majority.
    *   **Statistical Process Control (SPC):** Monitoring key behavioral metrics over time and flagging deviations.
    *   **Applicability:** Finding unusual action sequences, rare state transitions, or outlier event parameters.
    *   **Limitations:** Defining "normal" can be difficult, especially for adaptive agents; high false positive rates are possible.
*   **Time-Series Analysis Techniques:**
    *   **Trend Analysis, Change Point Detection:** For analyzing how metrics derived from patterns (e.g., frequency of a specific sequence, complexity of behaviors) change over the agent's lifetime.
    *   **Applicability:** Tracking developmental patterns, learning curves related to specific behaviors.
    *   **Limitations:** Requires defining appropriate metrics to track over time.
*   **Graph Mining:**
    *   **Frequent Subgraph Mining:** If behaviors or interactions can be represented as graphs (e.g., agent-object interaction graphs, communication networks), this can find common structural patterns.
    *   **Applicability:** Analyzing social interaction patterns, complex tool use sequences.
    *   **Limitations:** Computationally expensive; graph representation of logs needs careful design.

**Hybrid Approaches:** Combining sequence mining with contextual filtering, or using clustering outputs as inputs for anomaly detection, will likely be necessary.

## 4. Required Log Data Specifications

Effective pattern mining relies heavily on the richness and structure of log data, as defined in `Logging_Specification.md`.

*   **Core Event Information:**
    *   `timestamp`: Essential for all temporal analyses and sequence construction.
    *   `event_type`: The primary discrete token for many sequence/association mining tasks.
    *   `agent_id`: To separate and compare patterns for different agents.
    *   `simulation_run_id`: To analyze patterns within specific runs or compare across runs.
*   **Agent Actions:**
    *   `AGENT_ACTION_EXECUTED_IN_ENV`:
        *   `event_data`: `action_name` (critical discrete token), `parameters` (can be used for contextualizing actions or defining more specific action types), `target_object_id`.
*   **Internal States:**
    *   `EMOTION_STATE_UPDATED`: `event_data.current_vad` (values might need discretization or abstraction for some algorithms).
    *   `MOTIVATIONAL_STATE_UPDATED`: `event_data.active_goals_summary` (e.g., list of active goal IDs or types).
    *   `AGENT_INTERNAL_STATE_UPDATED`: `event_data.state_variable`, `event_data.value` (for states like cognitive load, resource levels).
    *   `LTM_CONTENT_ACCESSED`: `event_data.knowledge_id_or_type`.
*   **Task Information:**
    *   `TASK_STATUS_UPDATE`: `event_data.task_id`, `event_data.status` (e.g., STARTED, COMPLETED_SUCCESS, FAILED), `event_data.task_type`.
    *   `TASK_PERFORMANCE_METRICS`: `event_data.metric_name`, `event_data.value`.
*   **Environmental Context:**
    *   `ENVIRONMENT_STATE_CHANGED`: `event_data.changed_aspect`, `event_data.new_value`. (Used to segment or contextualize behavioral patterns).
    *   `PERCEPTION_INPUT_PROCESSED`: `event_data.stimulus_type`, `event_data.novelty_score`.
*   **For Developmental Analysis:**
    *   Consistent logging format across long periods and multiple simulation runs.
    *   Logging of agent version or configuration changes if they occur mid-way.

**Data Preprocessing:** The module will need robust preprocessing capabilities, including:
*   **Event Discretization/Abstraction:** Converting continuous state values into discrete categories (e.g., "low/medium/high cognitive load").
*   **Sessionization/Episode Segmentation:** Breaking down continuous log streams into meaningful episodes for analysis (e.g., per task, per goal pursuit, per day-night cycle).
*   **Feature Engineering:** Creating relevant features from raw log data to feed into clustering or anomaly detection algorithms.

## 5. Conceptual Examples of Use Cases

*   **Use Case 1: Discovering Common Task Completion Strategies**
    *   **Goal:** Identify the most frequent sequences of actions agents use to successfully complete "Task_Type_X".
    *   **Method:**
        1.  Filter logs for episodes related to "Task_Type_X" that ended in "COMPLETED_SUCCESS".
        2.  Extract `AGENT_ACTION_EXECUTED_IN_ENV` events for these episodes.
        3.  Apply a sequence mining algorithm (e.g., PrefixSpan) to find frequent action subsequences.
    *   **PiaAVT Role:** Provide tools for filtering, sequence extraction, and running the mining algorithm. Visualize resulting patterns.
*   **Use Case 2: Identifying Antecedents to Goal Abandonment**
    *   **Goal:** What internal states or environmental events frequently precede an agent abandoning a "COMPLEX_GOAL"?
    *   **Method:**
        1.  Identify all `GOAL_STATE_CHANGED` events where `new_state` is "ABANDONED" for goals of type "COMPLEX_GOAL".
        2.  For each abandonment, extract a window of preceding events (e.g., internal states, perception events).
        3.  Use association rule mining (e.g., Apriori) to find events/states that have high confidence of appearing before abandonment.
    *   **PiaAVT Role:** Data extraction, rule mining, and presenting significant associations.
*   **Use Case 3: Detecting Anomalous Agent Behavior**
    *   **Goal:** Flag instances where an agent's behavior deviates significantly from its typical patterns in a stable environment.
    *   **Method:**
        1.  Train an anomaly detection model (e.g., Isolation Forest) on feature vectors representing "normal" behavioral episodes (e.g., sequences of action types, durations, frequencies of internal state changes).
        2.  Apply the model to new log data to identify episodes with high anomaly scores.
    *   **PiaAVT Role:** Feature engineering from logs, model training interface (potentially via scikit-learn), and highlighting anomalous episodes.
*   **Use Case 4: Tracking Emergence of a Learned Skill**
    *   **Goal:** Observe if and when an agent starts consistently using a newly learned "Stealth" skill (represented by a sequence like "check_visibility -> move_slowly -> use_cover").
    *   **Method:**
        1.  Define the target "Stealth" action sequence.
        2.  Over successive simulation runs or long time periods, calculate the frequency of this specific sequence.
        3.  Plot this frequency over time to observe its emergence and stabilization.
    *   **PiaAVT Role:** Sequence frequency counting, time-series plotting.

## 6. Challenges and Future Directions

*   **Defining "Interesting" Patterns:** A major challenge is avoiding the generation of an overwhelming number of trivial or irrelevant patterns. User guidance, context-awareness, and good metrics for pattern interestingness will be key.
*   **Scalability:** Pattern mining algorithms can be resource-intensive. Efficient implementations and potentially distributed processing will be needed for large logs.
*   **Contextualization:** Raw patterns are often not useful without understanding the context in which they occur. Integrating contextual information (e.g., current goal, environmental state) into the mining process is crucial.
*   **Temporal Granularity:** Choosing the right time windows or episode definitions for analysis.
*   **Abstracting Event Data:** Converting raw log data (especially continuous or high-cardinality `event_data`) into suitable discrete tokens for many algorithms.
*   **User Interface for Pattern Exploration:** Developing intuitive ways for users to define what they are looking for, browse discovered patterns, and drill down into specific instances.
*   **Actionability of Insights:** Helping users translate discovered patterns into actionable insights for agent development or debugging.

Future work will involve selecting a core set of robust algorithms, building flexible data preprocessing pipelines, and designing UIs that allow for interactive exploration of behavioral patterns and their significance.
