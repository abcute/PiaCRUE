# LTM (Long-Term Memory) Explorer for PiaAVT (Conceptual Design)

## 1. Introduction/Purpose of the LTM Explorer

The Long-Term Memory (LTM) of a PiaAGI agent is a critical component, storing its knowledge, experiences, and learned skills. Understanding the content, structure, and evolution of LTM is essential for analyzing agent learning, knowledge representation, decision-making, and overall cognitive development. The LTM Explorer in PiaAVT aims to provide a suite of interactive visualization tools to enable researchers to inspect and analyze the different facets of an agent's LTM.

The primary purposes of the LTM Explorer are:

*   **Insight into Knowledge Structures:** To visualize how the agent organizes its semantic knowledge and procedural skills.
*   **Understanding Experiential Learning:** To allow researchers to replay and analyze the agent's episodic memory, understanding how specific experiences are stored and potentially utilized.
*   **Debugging Learning Processes:** To identify issues in knowledge acquisition, memory consolidation, or skill learning.
*   **Assessing Knowledge Quality:** To help evaluate the accuracy, completeness, and organization of the agent's knowledge.
*   **Supporting Explainability:** To trace how specific memories (semantic, episodic, or procedural) might have contributed to an agent's decisions or behaviors.

This module will offer distinct visualization approaches tailored to the different types of LTM components conceptualized for PiaAGI.

## 2. Visualization Design for Semantic LTM

Semantic LTM stores factual knowledge, concepts, and relationships between them (the agent's "knowledge graph").

*   **Visualization Metaphor:** Interactive Directed Graph or Network Diagram.
    *   **Nodes:** Represent concepts, entities, or objects (e.g., "DOG", "CHAIR", "AGENT_X"). Node appearance (size, color, shape) could represent concept type, activation level, or certainty.
    *   **Edges:** Represent relationships between concepts (e.g., "is_a", "has_property", "causes", "related_to"). Edge appearance (thickness, color, style, arrows) could represent relationship type, strength, or directionality.
*   **Key Features and Interactions:**
    *   **Search & Highlighting:** Allow users to search for specific concepts. Matching nodes and their immediate neighbors would be highlighted.
    *   **Node Expansion/Collapsing:** Users can click on a node to expand it, revealing its direct connections, or collapse it to hide them, managing visual complexity.
    *   **Filtering:**
        *   Filter nodes by concept type (e.g., show only "physical_object" concepts).
        *   Filter edges by relationship type (e.g., show only "is_a" relationships to see a class hierarchy).
        *   Filter by relationship strength or certainty scores if available.
    *   **Information Panel:** Clicking on a node or edge displays its properties, attributes, definitions, associated metadata (e.g., learning timestamp, source of knowledge) in a separate panel.
    *   **Layout Algorithms:** Provide options for different graph layout algorithms (e.g., force-directed, hierarchical) to optimize readability for different graph structures.
    *   **Pathfinding:** Allow users to select two nodes and find/highlight paths (shortest, all, specific types) between them.
    *   **Subgraph Extraction:** Select a set of nodes and extract them as a new, focused subgraph view.
    *   **Temporal Exploration (Advanced):** If LTM logs include creation/modification timestamps for concepts/relations, allow users to "slide" through time to see how the knowledge graph evolved.

## 3. Visualization Design for Episodic LTM

Episodic LTM stores sequences of events or experiences from the agent's "life."

*   **Visualization Metaphor:** Interactive Timeline or Event Sequence View.
    *   **Main Axis:** Represents time.
    *   **Events:** Displayed as markers, icons, or colored bars along the timeline. The visual representation could vary by event type or significance.
*   **Key Features and Interactions:**
    *   **Zoom & Pan:** Allow users to zoom in on specific periods or pan across the entire timeline.
    *   **Filtering:**
        *   Filter events by date/time range.
        *   Filter by `event_type` (e.g., show only `AGENT_ACTION_EXECUTED_IN_ENV` or `EMOTION_STATE_UPDATED` within episodes).
        *   Filter by involved entities (e.g., show episodes involving "object_Y" or "agent_Z").
        *   Filter by associated metadata (e.g., show only episodes with high emotional valence, or episodes related to a specific task).
    *   **Event Details:** Clicking on an event marker opens a panel showing the full `event_data` and any associated metadata (e.g., emotional tags, goal context, perceived stimuli).
    *   **Episode Segmentation:** Visually group related sequences of events into "episodes" (e.g., based on task ID, goal ID, or temporal proximity with a defined start/end). These episodes could be collapsible/expandable bars on the timeline.
    *   **Playback Control (Conceptual):** Buttons to "play," "pause," or "step through" an episode, sequentially highlighting events on the timeline and updating context displays.
    *   **Multi-Track Timeline:** Optionally, use different tracks on the timeline to represent different categories of events (e.g., one track for agent actions, one for environmental events, one for internal state changes).
    *   **Annotation Layer:** Allow users to add annotations or bookmarks to specific points or episodes on the timeline for later review.

## 4. Visualization Design for Procedural LTM

Procedural LTM stores learned skills, motor controls, and sequences of actions to achieve specific objectives.

*   **Visualization Metaphors:**
    *   **Flowcharts / State Transition Diagrams:** For representing skills with clear sequential steps, conditions, and loops. Nodes are actions or states, edges are transitions.
    *   **Skill Trees / Hierarchies:** If skills are organized hierarchically (e.g., complex skill "make_coffee" comprises sub-skills "grind_beans", "boil_water").
    *   **Action Sequence Templates:** Displaying a canonical or generalized sequence for a learned procedure.
*   **Key Features and Interactions:**
    *   **Skill Selection:** Users select a learned skill/procedure from a list.
    *   **Diagram Navigation:** Pan and zoom within the flowchart or skill tree.
    *   **Step Details:** Clicking on an action/state node shows its properties, preconditions, expected outcomes, and associated sub-skills or primitive actions.
    *   **Execution Trace Overlay (Advanced):** If specific execution instances of a procedure are logged, allow overlaying these traces onto the general skill diagram to see variations or common paths taken.
    *   **Success/Failure Annotation:** Visually distinguish steps or transitions that frequently lead to success or failure, based on aggregated execution logs.
    *   **Learning Progress (Advanced):** If skill learning logs track proficiency or changes in the procedure over time, visualize how the skill's representation (e.g., flowchart structure, transition probabilities) has evolved.

## 5. Required Log Data Specifications for each LTM type

Rich LTM visualizations require specific data to be logged by the PiaCML LTM module.

*   **For Semantic LTM Visualization:**
    *   **`EVENT_TYPE: LTM_CONCEPT_CREATED` / `LTM_CONCEPT_UPDATED`**
        *   `event_data`: `{"concept_id": "...", "concept_type": "...", "label": "...", "description": "...", "attributes": {"key1": "value1"}, "timestamp_learned": "..."}`
    *   **`EVENT_TYPE: LTM_RELATIONSHIP_CREATED` / `LTM_RELATIONSHIP_UPDATED`**
        *   `event_data`: `{"relationship_id": "...", "source_concept_id": "...", "target_concept_id": "...", "relationship_type": "is_a/has_part/causes", "weight_or_certainty": 0.9, "attributes": {"key1": "value1"}, "timestamp_learned": "..."}`
    *   **`EVENT_TYPE: LTM_GRAPH_SNAPSHOT` (Periodic or on-demand)**
        *   `event_data`: `{"graph_data": [{nodes}, {edges}], "timestamp": "..."}` (A full or partial dump of the knowledge graph). This is crucial for reconstructing the graph state.
*   **For Episodic LTM Visualization:**
    *   **`EVENT_TYPE: EPISODIC_MEMORY_STORED` / `EPISODE_SNAPSHOT_CAPTURED`**
        *   `event_data`:
            *   `episode_id`: (String) Unique ID for the episode.
            *   `start_timestamp`: (Timestamp)
            *   `end_timestamp`: (Timestamp)
            *   `summary_or_label`: (String) User/Agent generated label for the episode.
            *   `event_sequence_ids`: (List of Strings) Ordered list of `event_id`s that constitute this episode. (These events would be standard log entries like `AGENT_ACTION`, `PERCEPTION`, `EMOTION_STATE_UPDATED`).
            *   `context`: (Object) Key contextual elements at the start/during the episode (e.g., active goal, location).
            *   `associated_entities`: (List of Strings) IDs of agents, objects involved.
            *   `emotional_valence_avg`: (Float, Optional) Average emotional valence during the episode.
            *   `significance_score`: (Float, Optional) Agent-assessed importance of the episode.
    *   Individual log entries (`AGENT_ACTION_EXECUTED_IN_ENV`, `EMOTION_STATE_UPDATED`, `PERCEPTION_INPUT_PROCESSED`, etc.) must have precise `timestamp`s and clear `event_id`s to be linked by episodes.
*   **For Procedural LTM Visualization:**
    *   **`EVENT_TYPE: LTM_SKILL_LEARNED` / `LTM_PROCEDURE_UPDATED`**
        *   `event_data`:
            *   `skill_id`: (String)
            *   `skill_label`: (String)
            *   `skill_type`: (String, e.g., "sequential", "goal_driven").
            *   `representation`: (Object) Structured representation of the skill (e.g., list of steps with conditions/actions, state-transition table, PDDL-like structure).
            *   `preconditions`: (List of Strings/Objects).
            *   `postconditions_or_effects`: (List of Strings/Objects).
            *   `proficiency_score`: (Float, Optional).
    *   **`EVENT_TYPE: SKILL_EXECUTION_TRACE` / `PROCEDURE_STEP_EXECUTED`** (Logged during skill use)
        *   `event_data`:
            *   `execution_id`: (String) Unique ID for this instance of skill execution.
            *   `skill_id`: (String)
            *   `step_id_or_label`: (String) Identifier of the current step within the procedure.
            *   `step_parameters`: (Object, Optional) Parameters used for this step.
            *   `outcome`: (String, Enum, Optional) e.g., "SUCCESS", "FAILURE", "IN_PROGRESS".
            *   `timestamp`: (Timestamp).

## 6. Conceptual Examples of Use Cases

*   **Use Case 1 (Semantic LTM): Understanding Misconceptions**
    *   A researcher notices an agent making planning errors related to a specific tool. They use the Semantic LTM Explorer to search for the "tool_concept." They inspect its relationships and attributes, discovering the agent has an incorrect "has_property: can_fly" relationship, leading to the error.
*   **Use Case 2 (Episodic LTM): Analyzing a Traumatic Experience**
    *   An agent exhibits persistent negative emotional responses in certain situations. The researcher uses the Episodic LTM Explorer to filter for episodes with high negative emotional valence. They identify a past episode where a specific environmental stimulus was followed by a significant failure, providing a hypothesis for the agent's current aversion.
*   **Use Case 3 (Procedural LTM): Debugging a Faulty Skill**
    *   An agent frequently fails at a multi-step "navigation_skill." The researcher visualizes the skill as a flowchart in the Procedural LTM Explorer. By overlaying execution traces, they see that a specific conditional branch ("if_obstacle_detected") is almost never correctly taken, pointing to a flaw in the skill's learned logic or perceptual input for that condition.

## 7. Technical Considerations

*   **Graph Visualization Libraries:** For Semantic LTM, libraries like `Vis.js`, `Cytoscape.js` (for web via Streamlit components), or Python libraries like `NetworkX` (with Matplotlib/Plotly for rendering) could be used.
*   **Timeline Libraries:** For Episodic LTM, libraries like `Plotly Express` (timeline), or specialized timeline components for Streamlit.
*   **Flowchart/Diagramming Libraries:** For Procedural LTM, `Graphviz` (via Python bindings) or web-based libraries like `Mermaid.js` (if Streamlit supports rendering it) could be options.
*   **Scalability:**
    *   Large knowledge graphs or long episodic timelines can be challenging to render and navigate.
    *   Employ techniques like lazy loading, level-of-detail rendering, clustering/summarization of nodes/edges, and efficient backend data querying.
    *   Periodic snapshots or summaries of LTM might be more feasible to visualize than real-time, high-frequency updates for very dynamic LTMs.
*   **Data Abstraction:** The LTM Explorer will need to work with potentially complex and nested data structures from LTM logs. Adapters or mappers might be needed to transform raw log data into formats suitable for visualization libraries.
*   **Interactivity:** Ensuring smooth and intuitive user interaction for filtering, searching, expanding, and drilling down into details is crucial for usability.

The LTM Explorer will be a powerful suite of tools, but its development will require careful consideration of both the conceptual representations of memory and the practical aspects of visualizing large, dynamic datasets.
