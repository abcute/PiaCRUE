# LTM Advanced Features Specification (Phase 2)

**Document Version:** 1.0
**Date:** 2024-08-09
**Author:** Jules (PiaAGI Assistant)
**Status:** Conceptual Design Draft
**Related Documents:**
*   `PiaAGI.md` (Sections 3.1.1, 4.1.3)
*   `PiaAGI_Research_Tools/PiaCML/PiaCML_Advanced_Roadmap.md`
*   `PiaAGI_Research_Tools/PiaCML/concrete_long_term_memory_module.py`
*   `PiaAGI_Research_Tools/PiaCML/core_messages.py`

## 1. Introduction

This document details the conceptual design for Phase 2 advanced features for the Long-Term Memory (LTM) Module within the PiaAGI Cognitive Module Library (PiaCML). These features include active forgetting mechanisms, memory consolidation processes, and memory abstraction capabilities, as outlined in the `PiaCML_Advanced_Roadmap.md`. The goal is to create a more dynamic, efficient, and human-like LTM that supports lifelong learning and complex reasoning.

## 2. Active Forgetting Mechanisms

Active forgetting is crucial for managing LTM capacity, maintaining relevance, and preventing interference from outdated or incorrect information.

*   **2.1. Criteria for Forgetting:**
    *   **Low Salience / Activation Strength:** Memories with persistently low activation (implying a need for an `activation_strength` attribute in memory items, updated upon access or rehearsal).
    *   **Infrequent Access:** Items with a low `access_count` and an old `last_accessed_timestamp` (tracked in `MemoryItem.metadata` or similar).
    *   **Low Relevance/Utility:** As assessed by the Self-Model Module (SMM). The SMM could flag items via a specific message (e.g., `LTMMaintenanceDirective` with `action="flag_for_pruning"`) if they are no longer relevant to current goals, the agent's self-concept, or are found to be erroneous.
    *   **Low Confidence / Poor Groundedness:** Knowledge items consistently assessed by SMM as having very low confidence or poor grounding.
    *   **Explicit "Unlearn" or "Deprecate" Signals:** From trusted sources (e.g., human supervisor, curriculum update) or internal self-correction processes.
    *   **Redundancy:** Highly similar or duplicate information where one representation is clearly superior or more comprehensive.

*   **2.2. Implementation of Forgetting:**
    *   **Level 1 (Reduced Accessibility):** Drastically reduce the `activation_strength` of the memory item. It would still exist but be far less likely to be retrieved by standard queries. Its `status` in metadata could change to "low_priority_candidate_for_archival".
    *   **Level 2 (Archival / Soft Delete):** Mark the item with `metadata.status = "archived"`. Archived items are not included in default LTM queries but might be accessible via specialized "deep search" or "archival retrieval" queries. This allows for potential recovery.
    *   **Level 3 (Actual Deletion - Use with Extreme Caution):** Physical removal of the memory item. This is generally risky due to potential unknown dependencies or future relevance. Should only be considered for demonstrably erroneous data or after a prolonged period in "archived" status.

*   **2.3. Process:**
    *   LTM could implement a periodic `maintenance_cycle()` (e.g., triggered during simulated low cognitive load periods).
    *   This cycle would:
        *   Iterate through a subset of memory items (e.g., those not accessed recently or with low activation).
        *   Apply forgetting criteria.
        *   Transition items through forgetting levels (e.g., from active -> low_priority -> archived).
    *   LTM would also listen for `LTMMaintenanceDirective` messages from SMM or other authorized modules to act on specific items.

*   **2.4. Interaction with Other Modules:**
    *   **Self-Model Module (SMM):** Key in identifying memories for potential forgetting based on relevance, confidence, and utility.
    *   **Learning Module (LM):** Might inform forgetting if a piece of knowledge is consistently leading to prediction errors (negative utility).

## 3. Memory Consolidation Processes

Memory consolidation strengthens important memories, integrates new information with existing knowledge, and supports abstraction. This is inspired by biological memory consolidation, including concepts like rehearsal and sleep-related processing.

*   **3.1. Triggers for Consolidation:**
    *   **Periodic:** Scheduled during simulated "low cognitive load" or "rest" phases (analogous to sleep).
    *   **Event-Driven:**
        *   After significant learning episodes (e.g., successful completion of a complex task, acquisition of a new critical skill, receipt of highly salient `LearningOutcome` message).
        *   When Working Memory (WM) signals it's holding important, novel information that needs robust LTM encoding. WM might send a `ConsolidationRequest` message with references to these WM items.
        *   High emotional valence associated with an episodic memory (from `EmotionalStateChangePayload` linked to an event) can flag it for prioritized consolidation.

*   **3.2. Episodic-to-Semantic Consolidation & Abstraction:**
    *   **Process:**
        1.  **Identify Related Episodes:** LTM (potentially assisted by LM's pattern recognition) analyzes recent, highly salient, or emotionally charged episodic memories. It looks for recurring entities, relationships, event sequences, or outcomes.
        2.  **Form/Strengthen Semantic Knowledge:**
            *   If multiple episodes demonstrate consistent properties or relationships (e.g., "Object X is consistently found in Location Y," "Action A consistently leads to Outcome B in Context C"), this information can be used to create or strengthen nodes and edges in the `semantic_memory_graph`.
            *   Example: If several episodes show the agent successfully using `Tool_Alpha` for `Task_Beta`, the semantic representation of `Tool_Alpha` can be updated with an increased `effectiveness_for_Task_Beta` property.
            *   Newly formed semantic concepts would store references (e.g., a list of `episode_id`s) to the source episodic memories in their metadata for traceability and evidential support.
        3.  **Generalize Procedural Knowledge:** From multiple instances of applying a skill (stored as procedural traces or linked to episodes), the LM can help LTM abstract more general rules, heuristics, or refined parameters for that skill, updating its representation in procedural memory.

*   **3.3. Strengthening Important Memories (Rehearsal Analogues):**
    *   **Selection:** Identify memories for strengthening based on:
        *   High salience / emotional valence.
        *   High frequency of access.
        *   Relevance to current high-priority goals (as indicated by MSM).
        *   Importance to the agent's self-concept (as indicated by SMM).
    *   **Mechanism:**
        *   "Re-activate" the memory trace internally (e.g., increase its `activation_strength`).
        *   Create new or strengthen existing associative links to other related memories (both episodic and semantic).
        *   Update `MemoryItem.metadata` (e.g., increment `rehearsal_count`, update `last_strengthened_ts`).

*   **3.4. Interface with Other Modules:**
    *   **Working Memory (WM):** Can send `ConsolidationRequest` messages with candidate items.
    *   **Learning Module (LM):** Plays a crucial role in pattern recognition for abstraction and generalization during consolidation. LTM may send batches of related memories to LM for analysis and receive back abstracted knowledge.
    *   **Self-Model Module (SMM):** Can guide consolidation by highlighting which types of memories or knowledge are currently most relevant to the agent's developmental goals or self-concept.
    *   **Emotion Module (EM):** Emotional tags on memories influence their likelihood of being selected for consolidation.

## 4. Memory Abstraction (as part of Consolidation)

Memory abstraction is the process of deriving generalized knowledge (semantic concepts, rules, schemas) from specific instances (episodic memories, individual experiences).

*   **4.1. Mechanism (Conceptual - often LM-driven, LTM stores results):**
    *   **Pattern Mining & Concept Formation:** The Learning Module analyzes collections of related `MemoryItem`s (e.g., episodes involving similar objects or actions) provided by LTM. It identifies common features, relationships, or outcomes. New semantic nodes representing these abstracted concepts or patterns are proposed.
    *   **Rule Induction:** For procedural knowledge, LM analyzes multiple successful (or unsuccessful) applications of a skill to induce more general rules, heuristics, or conditions of applicability.
    *   **Schema/Script Learning:** From recurring sequences of events in episodic memory, more abstract schemas or scripts (e.g., "typical_restaurant_visit_sequence") can be learned and stored semantically or procedurally.

*   **4.2. Storage and Linking in LTM:**
    *   Abstracted knowledge (new concepts, rules, schemas) is stored in the appropriate LTM sub-component (e.g., `semantic_memory_graph`, procedural memory).
    *   Crucially, these abstractions maintain links (e.g., in their metadata) back to the specific source instances (episodes, specific skill applications) that contributed to their formation. This allows for:
        *   **Explainability:** Tracing an abstract piece of knowledge back to its experiential roots.
        *   **Refinement:** If source instances are later re-evaluated or new conflicting instances are encountered, the abstraction can be updated or its confidence revised.
        *   **Contextual Application:** Understanding the contexts of source instances can help determine the appropriate applicability of the abstraction.

## 5. Data Structure Considerations for Advanced LTM

To support these advanced features, existing data structures like `MemoryItem` (from `core_messages.py`, often used as a basis for LTM storage) and internal LTM representations might need enhancements:

*   **For `MemoryItem` or internal LTM equivalents:**
    *   `activation_strength`: (Float) A dynamic value indicating current salience or ease of retrieval. Decays over time, boosted by access, rehearsal, or relevance.
    *   `status`: (String, e.g., "active", "low_priority_candidate_for_archival", "archived", "to_be_deleted") For managing forgetting lifecycle.
    *   `access_count`: (Integer)
    *   `last_accessed_timestamp`: (Float/DateTime)
    *   `creation_context`: (Dict) Details about why/how this memory was formed (e.g., source module, related goal/task).
    *   `consolidation_level`: (Float/String) Indicates how well integrated this memory is.
    *   `rehearsal_count`: (Integer)
    *   `emotional_valence_at_encoding`: (Float) Stored if available from EM during memory formation.
    *   `linked_abstractions`: (List[str]) IDs of semantic concepts/rules derived from this item.
    *   `source_instances`: (List[str]) For an abstracted item, IDs of specific memories it was derived from.

## 6. Open Questions and Future Directions

*   Developing efficient algorithms for large-scale pattern mining and abstraction from diverse memory types.
*   Balancing the computational cost of continuous consolidation and forgetting processes with ongoing agent operations.
*   How to robustly determine "relevance" or "utility" of memories for forgetting criteria, especially for long-term, less obvious utility.
*   Simulating "sleep states" or distinct offline/online processing modes for consolidation effectively.
*   Interaction between learned forgetting/consolidation strategies and programmed ones.

This conceptual design provides a roadmap for enhancing PiaAGI's LTM. Implementation will require careful consideration of performance, scalability, and tight integration with other CML modules.

## 7. LTM Phase 3: Advanced Reasoning and Prediction Support

This section outlines Phase 3 advanced features for the LTM Module, focusing on capabilities that support more sophisticated reasoning, planning, and learning by enabling the storage and retrieval of intentions (prospective memory), alternative scenarios (counterfactual memory), and leveraging generative models for memory operations.

### 7.1. Prospective Memory (Remembering to Act)

Prospective memory refers to the ability to remember to perform an intended action at a future point in time or when a specific trigger event occurs.

*   **7.1.1. Data Structures for Intentions:**
    *   A new data structure, `ProspectiveMemoryItem` (or an extension of `MemoryItem` with a specific type/category), would be needed within LTM.
    *   **Conceptual Fields for `ProspectiveMemoryItem`:**
        *   `intention_id`: (String) Unique identifier for the intention.
        *   `action_to_perform`: (Object/Dict) Description of the action to be taken (e.g., could be a simplified `ActionCommandPayload` structure, or a reference to a detailed plan/script stored in procedural LTM).
        *   `trigger_condition`: (Object/Dict) Specifies when the intention should be activated.
            *   `type`: (String) e.g., "temporal", "event_based", "state_based".
            *   `temporal_trigger_details`: (DateTime, Optional) Specific time for execution.
            *   `event_trigger_details`: (String, Optional) Description of an event to monitor (e.g., "receipt_of_message_type_X_from_module_Y", "entity_Z_enters_location_A"). This might involve LTM subscribing to specific bus messages or WM/CE monitoring specific world states.
            *   `state_trigger_details`: (String, Optional) Description of an internal or external state condition (e.g., "self_model.cognitive_load < 0.3", "world_model.weather_is_sunny").
        *   `creation_context`: (String) Why this intention was formed (e.g., "user_request_defer_action", "planning_module_subgoal_for_later", "self_generated_reminder").
        *   `priority`: (Float) Importance of this intention.
        *   `status`: (String) e.g., "pending", "triggered", "completed", "cancelled", "expired".
        *   `source_module_id`: (String) Module that originated the intention.

*   **7.1.2. Mechanisms for Monitoring Triggers:**
    *   **Temporal Triggers:** LTM could maintain an internal time-sorted queue of prospective memories with temporal triggers. During its own processing cycle or via a system clock tick, it checks if any intentions are due.
    *   **Event-Based Triggers:**
        *   LTM could subscribe to specific `GenericMessage` types on the Message Bus if the trigger condition directly maps to a message type (e.g., "UserLoginEvent").
        *   Alternatively, Working Memory (WM) / Central Executive (CE), which has a broader view of current events and states, could be responsible for monitoring more complex event or state-based triggers. Upon detecting a trigger, WM/CE would query LTM for any associated prospective memories.
    *   **State-Based Triggers:** Similar to event-based, WM/CE would monitor relevant state information (from World Model, Self-Model, etc.) and query LTM when conditions are met.

*   **7.1.3. Interaction with WM/CE, Planning, and Motivational System:**
    *   **Activation:** When an LTM-monitored trigger fires or WM/CE signals a trigger, LTM retrieves the `ProspectiveMemoryItem`.
    *   **Notification to WM/CE:** LTM (or WM/CE if it detected the trigger) makes the triggered intention available to WM/CE. This is akin to the intention "coming to mind" or becoming part of the agent's current conscious workspace. This could be via a new internal message type like `ProspectiveIntentionTriggeredPayload` or by WM directly pulling it.
    *   **Planning Integration:** The Planning Module, when formulating current plans, would need to consider these newly "active" intentions from WM/CE. The `action_to_perform` from the `ProspectiveMemoryItem` might be integrated as a new goal or constraint into the current planning cycle.
    *   **Motivational System Integration:** The `priority` of the `ProspectiveMemoryItem` would be fed into the Motivational System to influence its overall goal prioritization. A high-priority triggered intention could preempt current activities.
    *   **Updating Status:** Once the intention is acted upon or integrated into a plan, its `status` in LTM should be updated (e.g., to "completed" or "in_progress_via_plan_X").

*   **7.1.4. Creation of Prospective Memory Items:**
    *   **Planning Module:** If a plan involves an action that needs to be deferred.
    *   **Self-Model Module:** For self-generated reminders or developmental goals that are time/context-dependent.
    *   **User Interaction:** If a user requests a future action (e.g., "Remind me to check emails at 3 PM"). The Communication Module would process this and request LTM to store the intention.
    *   **Learning Module:** If a learned policy involves delayed actions based on certain conditions.

### 7.2. Counterfactual Memory & Reasoning Support

Counterfactual memory involves storing representations of "what if" scenarios—alternative pasts or futures based on different conditions or actions. LTM's role is to store and retrieve these, supporting reasoning about them.

*   **7.2.1. Representation of Counterfactual Scenarios:**
    *   Counterfactuals would likely be stored as specialized `MemoryItem`s or within a dedicated counterfactual knowledge structure in LTM (e.g., linked to Episodic LTM).
    *   **Conceptual Fields for a `CounterfactualMemoryItem`:**
        *   `cf_id`: (String) Unique ID for the counterfactual scenario.
        *   `base_episode_ref`: (String) ID of the actual episodic memory this counterfactual is derived from or related to.
        *   `altered_conditions`: (Object/Dict) Description of what was different from the base episode (e.g., `{"variable": "action_taken_at_step3", "original_value": "ActionA", "counterfactual_value": "ActionB"}`).
        *   `simulated_outcome`: (Object/Dict) The outcome that resulted from the simulation under altered conditions.
        *   `reasoning_trace_ref`: (String, Optional) Pointer to a more detailed trace of the simulation or reasoning that produced this counterfactual (could be stored in procedural or semantic LTM).
        *   `confidence_in_simulation`: (Float) How reliable the simulated outcome is considered.
        *   `purpose_of_generation`: (String) e.g., "planning_what_if", "learning_credit_assignment", "smm_regret_analysis".
        *   `generation_timestamp`: (DateTime).

*   **7.2.2. Generation of Counterfactuals (by other modules):**
    *   **Planning Module:** During "what-if" analysis or plan evaluation, the Planning module might simulate alternative action sequences and their outcomes. It would then request LTM to store these as counterfactuals linked to the plan or the situation.
    *   **Learning Module:** For credit assignment or regret-based learning, the LM might generate counterfactuals by simulating what would have happened if a different action had been taken in a past episode.
    *   **Self-Model Module:** During self-reflection, the SMM might generate counterfactuals about past decisions to understand alternative personal outcomes or to evaluate the effectiveness of its past choices.

*   **7.2.3. LTM Storage and Retrieval:**
    *   LTM needs methods to store `CounterfactualMemoryItem`s, ensuring they are linked to their `base_episode_ref` for context.
    *   Retrieval queries (`LTMQueryPayload`) would need to support fetching counterfactuals, e.g.:
        *   `query_type`: "retrieve_counterfactuals_for_episode", `query_content`: `{"episode_id": "ep123"}`.
        *   `query_type`: "find_counterfactuals_matching_conditions", `query_content`: `{"altered_condition_pattern": ..., "desired_outcome_pattern": ...}`.

*   **7.2.4. Agent's Use of Stored Counterfactuals:**
    *   **Learning:** The LM can analyze stored counterfactuals to refine policies (e.g., if doing ActionB instead of ActionA consistently led to better simulated outcomes, adjust policy towards ActionB).
    *   **Future Planning:** The Planning module can retrieve relevant past counterfactuals to inform new plan generation, helping to avoid previously simulated negative outcomes or to select actions that led to positive simulated outcomes.
    *   **Emotional Processing (via SMM & EM):** The SMM, by reviewing counterfactuals, could trigger conceptual "regret" (if a past action was suboptimal compared to a counterfactual) or "relief" (if a past action avoided a negative counterfactual outcome). These emotional tags, generated by EM based on SMM's interpretation, could further influence future decision-making.
    *   **Explainability:** Stored counterfactuals can help explain why an agent *didn't* choose a certain path, if that path was explored counterfactually and found to be suboptimal.

### 7.3. Integration with Generative Models for Memory Operations

This involves LTM interfacing with (hypothetical) internal or external generative models (e.g., LLMs, image generators, physics simulators adapted for generation) to enhance memory functions.

*   **7.3.1. Conceptual Architecture:**
    *   LTM itself would not typically *be* a generative model but would *interface* with one or more specialized Generative Model Services (GMS). These GMS could be other CML modules or external tools.
    *   When LTM needs a generative operation, it formulates a request to the appropriate GMS.
    *   **Request to GMS (Conceptual `GenerativeMemoryOperationPayload`):**
        *   `operation_type`: (String) e.g., "reconstruct_episode_gap", "augment_memory_context", "generate_plausible_scenario".
        *   `input_memory_item_refs`: (List[String]) IDs of LTM items providing context.
        *   `query_or_prompt`: (String/Dict) Specific instructions for the GMS.
        *   `constraints`: (Dict, Optional) e.g., desired level of detail, consistency checks.
    *   **Response from GMS (Conceptual `GenerativeMemoryOperationResultPayload`):**
        *   `generated_content`: (Any) The image, text, data structure generated.
        *   `plausibility_score`: (Float) GMS's confidence in the generation.
        *   `source_model_id`: (String) Identifier of the GMS used.

*   **7.3.2. Use Cases:**
    *   **Memory Reconstruction/Gap Filling:**
        *   **Trigger:** LTM retrieves an episodic memory that is sparse or has missing segments (e.g., due to imperfect perception or forgetting).
        *   **Process:** LTM sends the incomplete memory and related semantic/episodic context to a GMS with an `operation_type="reconstruct_episode_gap"`.
        *   **Output:** GMS returns plausible details to fill the gaps. LTM stores this generated content, clearly flagging it as "AI-generated_reconstruction" and linking it to the original memory, along with the `plausibility_score`.
    *   **Memory Augmentation/Elaboration:**
        *   **Trigger:** SMM or Planning requires richer contextual understanding of a stored memory.
        *   **Process:** LTM sends a memory item to GMS with `operation_type="augment_memory_context"` and a prompt (e.g., "Elaborate on the typical environmental conditions for this type of event based on semantic knowledge of X and Y.").
        *   **Output:** GMS provides additional contextual details, which LTM can link to the original memory (flagged as generated).
    *   **Plausible Scenario Generation (for Planning/Counterfactuals):**
        *   **Trigger:** Planning module needs to explore hypothetical future states, or SMM/LM needs to generate a counterfactual.
        *   **Process:** LTM (on behalf of Planning/SMM/LM) sends current state information, desired modifications, and relevant past episodes/semantic knowledge to GMS with `operation_type="generate_plausible_scenario"`.
        *   **Output:** GMS returns one or more plausible future/alternative scenarios. LTM stores these, potentially as `CounterfactualMemoryItem`s or temporary planning structures.

*   **7.3.3. Managing Generated Content in LTM:**
    *   **Distinction:** Generated content *must* be clearly distinguished from directly experienced or verifiably learned memories (e.g., using `metadata.is_generated=True`, `metadata.generation_source_model_id`, `metadata.plausibility_score`).
    *   **Confidence/Plausibility:** The `plausibility_score` from the GMS is stored. The SMM might further assess and adjust this score based on consistency with other knowledge.
    *   **Feedback Loop & Refinement:**
        *   If actions based on generated memory content lead to unexpected outcomes (positive or negative), this feedback is crucial.
        *   The Learning Module can analyze these outcomes to:
            *   Refine the LTM's "trust" or weighting for content from specific GMSs or for certain types of generated content.
            *   Potentially provide feedback to the GMS itself for its own internal refinement (if the GMS supports this).

## 8. Open Questions and Future Directions (Phase 3 Focus)

*   Developing robust and efficient trigger monitoring mechanisms for prospective memory, especially for complex event/state-based triggers.
*   Scalable storage and indexing for a potentially vast number of counterfactual memories, and efficient retrieval of the most relevant ones.
*   Defining appropriate query languages and interfaces for interacting with diverse internal/external Generative Model Services.
*   Ensuring the epistemological integrity of LTM when integrating AI-generated content; preventing "hallucinated" memories from being treated as ground truth.
*   Ethical implications of an agent acting on internally generated (but potentially flawed) memories or scenarios.
*   How does the agent learn to trust or distrust its own generative memory capabilities?

These Phase 3 features aim to significantly enhance LTM's role in supporting complex cognition, moving it beyond simple storage and retrieval towards active participation in reasoning, prediction, and self-guided learning.
