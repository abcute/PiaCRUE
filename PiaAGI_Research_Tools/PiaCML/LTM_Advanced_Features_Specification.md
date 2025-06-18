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
```
