# World Model Viewer for PiaAVT (Conceptual Design)

## 1. Introduction/Purpose of the World Model Viewer

An AGI agent's World Model (WM) is its internal representation of the external environment, including objects, entities, their states, properties, relationships, and potentially the laws governing their behavior. The accuracy, completeness, and timeliness of the WM are critical for effective perception, planning, and action. The World Model Viewer in PiaAVT aims to provide researchers with tools to inspect, analyze, and evaluate the agent's WM.

The primary purposes of this module are:

*   **Understanding Agent's Perception of Reality:** To visualize what the agent "believes" about the current state of its environment.
*   **Debugging Perceptual and Modeling Errors:** To identify discrepancies between the agent's WM and the actual ground truth of the environment (provided by PiaSE logs).
*   **Assessing Situational Awareness:** To evaluate how well the agent understands relevant aspects of its current context.
*   **Analyzing Belief States:** For agents with probabilistic WMs, to inspect the agent's uncertainty about different environmental aspects.
*   **Supporting XAI:** To help explain why an agent chose a particular action based on its (possibly flawed) understanding of the world.

This viewer will be crucial for diagnosing issues related to perception, knowledge representation of the environment, and the agent's ability to maintain an accurate model of a dynamic world.

## 2. Key World Model Aspects for Visualization

The World Model Viewer should allow inspection of:

*   **Entities and Objects:** Their perceived existence, properties (e.g., color, size, material, state like "open/closed"), and spatial locations.
*   **Relationships between Entities:** How the agent models connections or associations between different entities (e.g., "object_A is on_top_of object_B," "agent_X is_near location_Y").
*   **Spatial Layout:** The agent's understanding of the environment's geometry, traversable areas, and the positions of entities within it (if applicable).
*   **Belief States/Uncertainty:** For probabilistic WMs, the agent's degree of belief or probability distributions over different states or properties.
*   **Temporal Dynamics:** How the agent's WM changes over time in response to its actions or environmental events.
*   **Social Aspects (Social Model):** The agent's representation of other agents' states, perceived goals, beliefs, or intentions (if the agent builds such models, often related to Theory of Mind capabilities).
*   **Discrepancies:** Differences between the agent's WM and the ground truth from PiaSE.

## 3. Viewer Component Designs

The World Model Viewer could be composed of several integrated components:

*   **A. Object/Entity Inspector:**
    *   **Concept:** A panel or view that displays detailed information about a selected object or entity as represented in the agent's WM.
    *   **Visualization:**
        *   List of properties and their current values (e.g., `object_id: "box_01"`, `color: "red"`, `state: "closed"`, `last_seen_timestamp: "..."`).
        *   List of perceived relationships with other entities (e.g., `related_to: [{"id": "table_01", "type": "on_top_of"}]`).
        *   Confidence scores for properties or existence, if the WM is probabilistic.
    *   **Interactions:** Users can select entities from a list or directly from a Spatial View (if available). Search functionality for entities by ID or property.
*   **B. Spatial View (2D/3D):**
    *   **Concept:** A visual representation of the environment (e.g., top-down 2D map, isometric 3D view) showing the positions and orientations of the agent itself and other known entities, according to the agent's WM.
    *   **Visualization:**
        *   Icons or simple geometric shapes representing different types of entities.
        *   Color-coding or visual cues to indicate entity states or properties (e.g., a red box for "dangerous object").
        *   Optionally, display areas of uncertainty or regions the agent has not recently observed.
    *   **Interactions:**
        *   Pan, zoom, rotate the view.
        *   Click on an entity in the view to populate the Object/Entity Inspector.
        *   Time-scrubbing: A slider to move back and forth in time, updating the spatial view to reflect the WM state at different logged timestamps.
*   **C. Belief State Visualization:**
    *   **Concept:** Tools to inspect the agent's probabilistic beliefs about specific aspects of the world.
    *   **Visualization:**
        *   For discrete state variables (e.g., "Door_A is Open/Closed/Locked"): Bar charts or pie charts showing probability distributions.
        *   For continuous variables (e.g., "Object_B's location_X"): Density plots or histograms.
        *   Heatmaps overlaid on the Spatial View to show probability distributions for an entity's location.
    *   **Interactions:** Users select a variable or proposition of interest. The visualization updates to show the agent's current belief state for it.
*   **D. World Model vs. Ground Truth Comparator:**
    *   **Concept:** A crucial tool for identifying WM inaccuracies. It compares the agent's WM state with the corresponding ground truth state from PiaSE logs.
    *   **Visualization Options:**
        *   **Side-by-Side Spatial View:** Display two synchronized Spatial Views: one for the agent's WM, one for PiaSE ground truth. Discrepancies (e.g., missing objects, misplaced objects, incorrect states) are highlighted in both views.
        *   **Overlay View:** Ground truth entities are overlaid onto the agent's WM Spatial View, with visual markers (e.g., color-coding, outlines) to indicate matches, mismatches, or agent-only/ground-truth-only entities.
        *   **Difference List/Table:** A textual list detailing discrepancies (e.g., "Agent believes Object_X is at (1,2), Ground Truth is (5,6)"; "Agent WM missing Object_Y, present in Ground Truth").
    *   **Interactions:**
        *   Synchronized time-scrubbing for both WM and ground truth views.
        *   Clicking on a discrepancy highlights it in all relevant views and provides details.
        *   Metrics: Display quantitative measures of WM accuracy (e.g., Jaccard index for object sets, RMSE for positional errors).
*   **E. Social Model View (Advanced):**
    *   **Concept:** Visualizes the agent's understanding of other agents, if its WM includes such social modeling (often related to Theory of Mind - ToM).
    *   **Visualization:**
        *   For each modeled external agent: Display what the primary agent believes about their goals, beliefs (nested beliefs like "Agent_A believes Agent_B wants X"), or potential next actions. This could be a simplified version of the Object/Entity Inspector, but for "social entities."
        *   Influence/Relationship Diagram: Show perceived relationships (e.g., "ally," "opponent," "neutral") between the primary agent and others, or between other agents.
    *   **Interactions:** Select an external agent to view their modeled state. Compare with ground truth if available for other agents' true states (complex).

## 4. Required Log Data Specifications

Accurate and detailed WM visualization requires specific logging from both the agent's WM module (within PiaCML) and the PiaSE simulation environment.

*   **From Agent's World Model Module (PiaCML):**
    *   **`EVENT_TYPE: WORLD_MODEL_SNAPSHOT` (Periodic or on significant change)**
        *   **`event_data`**: A structured representation of the agent's current understanding of the world.
            *   `timestamp`: (Timestamp) When this WM state was valid.
            *   `entities`: (List of Objects) Each object representing an entity:
                *   `entity_id`: (String) Unique ID.
                *   `entity_type`: (String) e.g., "object", "agent", "location_marker".
                *   `properties`: (Object) Key-value pairs, e.g., `{"color": "red", "state": "active", "size": [1,1,1]}`.
                *   `position`: (Object, Optional) e.g., `{"x": 10.2, "y": 5.1, "z": 0.0}`.
                *   `orientation`: (Object, Optional) e.g., `{"qx": 0, "qy": 0, "qz": 0, "qw": 1}`.
                *   `relationships`: (List of Objects, Optional) e.g., `[{"target_id": "entity_02", "type": "on_top_of"}]`.
                *   `belief_states`: (Object, Optional) For probabilistic properties, e.g., `{"state_is_open_prob": 0.8, "location_distribution_params": {...}}`.
                *   `last_observed_timestamp`: (Timestamp, Optional).
            *   `social_models`: (List of Objects, Optional) For each other agent:
                *   `target_agent_id`: (String)
                *   `believed_goals`: (List of Objects, Optional)
                *   `believed_beliefs`: (Object, Optional)
                *   `predicted_next_action_prob`: (Object, Optional)
    *   **`EVENT_TYPE: WORLD_MODEL_ENTITY_UPDATED`** (For incremental updates between snapshots)
        *   `event_data`: `{"entity_id": "...", "updated_properties": {...}, "timestamp": "..."}`.
    *   **`EVENT_TYPE: WORLD_MODEL_BELIEF_PROPAGATED` / `WORLD_MODEL_UNCERTAINTY_UPDATED`**
        *   `event_data`: `{"variable_id": "...", "new_belief_distribution": {...}, "reason_for_update": "...", "timestamp": "..."}`.
*   **From PiaSE (Simulation Environment - for Ground Truth):**
    *   **`EVENT_TYPE: ENVIRONMENT_STATE_GROUNDTRUTH` (Periodic, synchronized with agent logs)**
        *   **`event_data`**: Similar structure to `WORLD_MODEL_SNAPSHOT.entities`, but representing the objective truth of the simulation.
            *   `timestamp`: (Timestamp)
            *   `entities`: (List of Objects) Each with `entity_id`, `entity_type`, true `properties`, `position`, `orientation`.
            *   (Optionally, true internal states of other agents if needed for social model comparison, though this might be complex to manage).

## 5. Conceptual Examples of Use Cases

*   **Debugging Perception:** An agent consistently fails to pick up a specific object. The WM Viewer (Comparator mode) shows that the agent's WM has the object's position slightly offset from the ground truth, or believes it's occluded when it's not.
*   **Understanding Situational Awareness:** Before attempting a risky maneuver, a researcher uses the WM Viewer to see if the agent is aware of nearby obstacles or other agents, as per its WM. The Social Model View might show if it anticipates another agent's likely interference.
*   **Analyzing Belief Updates:** After an ambiguous sensory event, the Belief State Visualization shows the agent's probability distribution for "is_threat_present" shifting from low to moderate, explaining its subsequent cautious behavior.
*   **Tracking Model Accuracy Over Time:** By scrubbing through time in the Comparator View, a researcher can observe how the agent's WM accuracy degrades in unexplored areas or improves after exploration, providing insights into its WM maintenance strategies.

## 6. Interactivity and Comparison Features

*   **Time Synchronization:** A core feature is a global time slider that synchronizes all views (WM, Ground Truth, event timelines from other modules).
*   **Selection Linkage:** Selecting an entity in one view (e.g., Spatial View) should highlight it and display its details in the Object Inspector and potentially in other relevant analysis tabs.
*   **Difference Thresholds:** For the Comparator, allow users to set thresholds for highlighting discrepancies (e.g., only show positional errors greater than X units).
*   **Snapshot Management:** Allow users to save/load/compare specific WM snapshots of interest.
*   **Data Export:** Option to export parts of the WM (e.g., selected entity properties, discrepancy lists) for further external analysis.

The World Model Viewer will be an indispensable tool for gaining deep insights into how an AGI agent perceives and understands its operational environment, which is fundamental to its intelligence and behavior.
