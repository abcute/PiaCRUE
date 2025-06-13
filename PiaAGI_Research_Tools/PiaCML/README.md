<!-- PiaAGI AGI Research Framework Document -->
# PiaAGI Cognitive Module Library (PiaCML)

## Purpose

The Cognitive Module Library (CML) is a core component of the PiaAGI project. Its primary purpose is to define abstract interfaces and provide foundational Python implementations for the various cognitive modules outlined in the [PiaAGI Cognitive Architecture](../../PiaAGI.md#4-the-piaagi-cognitive-architecture).

This library aims to:
1.  **Standardize Interfaces:** Provide common Python Abstract Base Classes (ABCs) for each cognitive module.
2.  **Facilitate Modular Development:** Allow focused work on individual cognitive functions.
3.  **Support Simulation and Experimentation:** Enable construction of PiaAGI agents by composing these modules.
4.  **Promote Code Reusability:** Offer well-documented base components.
5.  **Align with Theory:** Ensure module designs map to `PiaAGI.md` theoretical descriptions.

## Current Abstract Interfaces & Concrete Implementations

CML provides abstract base classes (ABCs) and concrete MVP (Minimal Viable Product) implementations for core cognitive modules. The Concrete MVPs for key modules like `ConcreteSelfModelModule`, `ConcreteWorldModel`, and `ConcreteMotivationalSystemModule` have been enhanced to utilize detailed internal data structures (Python dataclasses). These structures are based on their respective specification documents (e.g., `Self_Model_Module_Specification.md`, `Motivational_System_Specification.md`) and direct Python dataclass definitions within the concrete implementations (e.g., `concrete_world_model.py`), forming a more robust foundation for future development.

**Key Modules (Interfaces Defined, with Concrete MVPs):**
*   **Perception Module:** (`PerceptionModule`, `ConcretePerceptionModule`)
    *   *[`PiaAGI.md`](../../PiaAGI.md) Sections:* [4.1.1](../../PiaAGI.md#41-core-modules-and-their-interactions), [4.3](../../PiaAGI.md#43-perception-and-world-modeling-conceptual)
*   **Working Memory Module (WM):** (`WorkingMemoryModule`, `ConcreteWorkingMemoryModule`)
    *   *[`PiaAGI.md`](../../PiaAGI.md) Sections:* [3.1.1](../../PiaAGI.md#311-memory-systems-ltm-wm-sensory-memory-and-their-agi-relevance), [4.1.2](../../PiaAGI.md#41-core-modules-and-their-interactions)
*   **Long-Term Memory Module (LTM):** (`LongTermMemoryModule`, `ConcreteLongTermMemoryModule`)
    *   *[`PiaAGI.md`](../../PiaAGI.md) Sections:* [3.1.1](../../PiaAGI.md#311-memory-systems-ltm-wm-sensory-memory-and-their-agi-relevance), [4.1.3](../../PiaAGI.md#41-core-modules-and-their-interactions)
*   **Attention Module:** (`BaseAttentionModule`, `ConcreteAttentionModule`)
    *   *[`PiaAGI.md`](../../PiaAGI.md) Sections:* [3.1.2](../../PiaAGI.md#312-attention-and-cognitive-control-central-executive-functions), [4.1.4](../../PiaAGI.md#41-core-modules-and-their-interactions)
*   **Learning Module:** (`BaseLearningModule`, `ConcreteLearningModule`)
    *   *Role:* Enables the agent to learn from experience, adapt knowledge and behaviors, and improve performance. It processes various inputs (percepts, action outcomes, goal statuses, feedback) through different conceptual learning paradigms.
    *   *Conceptual Learning Paradigms (in `ConcreteLearningModule`):*
        *   **Unsupervised Feature Extraction:** Identifies patterns in raw `PerceptData` (e.g., from visual or textual modalities) to form new feature representations or concept clusters, conceptually updating LTM-Semantic.
        *   **Reinforcement from Action:** Adjusts skill policies (conceptually in LTM-Procedural) based on the success or failure status of `ActionEventPayloads`. Reward signals are implicitly derived from action outcomes.
        *   **Goal Outcome Evaluation:** Evaluates strategies related to goal achievement or failure (from `GoalUpdatePayloads`), conceptually updating LTM-Procedural (strategy effectiveness) or LTM-Episodic (memory of the outcome).
        *   **Supervised Learning (Conceptual):** Designed to train/fine-tune internal models using labeled data, if provided. Updates models conceptually stored in LTM-Semantic or specialized model stores.
        *   **Observational Learning (Conceptual):** Allows learning new behaviors or skills by observing traces of another agent's actions and outcomes. Conceptually updates LTM-Procedural or LTM-Semantic (affordances, social norms).
        *   **Transfer Learning (Conceptual):** Adapts existing knowledge or skills from a source domain/task to a new target domain/task. Conceptually updates LTM for the target context.
        *   **Meta-Learning (Conceptual):** Adjusts internal learning parameters (e.g., learning rates) or strategy selection heuristics based on performance feedback. Conceptually updates Learning Module parameters or Self-Model learning preferences.
    *   *Operational Notes:* The `ConcreteLearningModule` is integrated with the message bus, receiving various events that trigger learning. It applies conceptual ethical guardrails to potential learning outcomes before publishing them as `LearningOutcomePayload` messages. It also includes conceptual logic for knowledge consolidation and is influenced by the agent's emotional state.
    *   *[`PiaAGI.md`](../../PiaAGI.md) Sections:* [3.1.3](../../PiaAGI.md#313-learning-theories-and-mechanisms-for-agi), [4.1.5](../../PiaAGI.md#41-core-modules-and-their-interactions)
*   **Motivational System Module:** (`MotivationalSystemModule`, `ConcreteMotivationalSystemModule`)
    *   *[`PiaAGI.md`](../../PiaAGI.md) Sections:* [3.3](../../PiaAGI.md#33-motivational-systems-and-intrinsic-goals), [4.1.6](../../PiaAGI.md#41-core-modules-and-their-interactions)
*   **Emotion Module:** (`EmotionModule`, `ConcreteEmotionModule`)
    *   *Role:* Manages the agent's emotional state, primarily using a VAD (Valence, Arousal, Dominance) model. It appraises incoming events from various sources (goals, percepts, actions) to update this VAD state and derive conceptual discrete emotions.
    *   *Conceptual Operational Flow (in `ConcreteEmotionModule`):*
        1.  Receives `GoalUpdatePayload`, `PerceptDataPayload`, and `ActionEventPayload` messages via the Message Bus.
        2.  Message handlers (`_handle_goal_update_for_appraisal`, etc.) extract relevant information and transform it into conceptual appraisal dimensions (e.g., event intensity, novelty, expectedness, goal_congruence, agency, norm_alignment, controllability).
        3.  The core `appraise_event` method takes these dimensions and calculates changes to the VAD state. This calculation considers the derived appraisal variables and can be (conceptually) influenced by the agent's personality profile (e.g., neuroticism affecting valence response, extraversion, arousal reactivity).
        4.  A helper method, `_map_vad_to_discrete_emotion`, provides a simplified mapping from the current VAD state to a discrete emotion label (e.g., "Joyful," "Sad," "Calm").
        5.  The VAD state undergoes a decay process, gradually returning towards neutral over time.
        6.  An `EmotionalStateChangePayload`, containing the updated VAD profile, the derived discrete emotion label, and an intensity value (typically current arousal), is published on the Message Bus.
    *   *Emphasis:* The current appraisal logic in `ConcreteEmotionModule` is a conceptual framework. While it processes various inputs and logs its internal calculations (derived appraisal variables, VAD changes), the specific weights and the precise impact of personality traits (beyond arousal reactivity) are placeholders designed for future empirical grounding and more sophisticated modeling.
    *   *[`PiaAGI.md`](../../PiaAGI.md) Sections:* [3.4](../../PiaAGI.md#34-computational-models-of-emotion), [4.1.7](../../PiaAGI.md#41-core-modules-and-their-interactions)
*   **Planning and Decision Making Module:** (`PlanningAndDecisionMakingModule`, `ConcretePlanningAndDecisionMakingModule`)
    *   *Role:* Formulates plans to achieve active goals from the Motivational System, considering the current world state, agent capabilities (from Self-Model), available knowledge (LTM), and contextual information (WM). It selects appropriate actions or sub-goals and dispatches them.
    *   *Conceptual Operational Flow (in `ConcretePlanningAndDecisionMakingModule`):*
        1.  **LTM Plan Retrieval:** Attempts to retrieve relevant pre-existing plans from LTM.
        2.  **Internal Plan Generation (Conceptual):** If no suitable LTM plan is found, it generates a few conceptual candidate plans (e.g., direct, cautious, exploratory).
        3.  **Plan Evaluation (Conceptual):** Each candidate plan undergoes a conceptual evaluation, logging simulated checks against:
            *   World Model (e.g., predicted success, resource estimation).
            *   Self-Model (e.g., ethical alignment, capability adequacy).
            *   Emotion Module (e.g., influence of current emotional state).
            *   LTM (e.g., outcomes of similar past plans).
            A conceptual evaluation score is assigned to each plan.
        4.  **Plan Selection:** The plan with the best conceptual evaluation score is selected.
        5.  **Ethical Review Trigger:** If the selected plan warrants it (based on conceptual checks or keywords), a formal `EthicalReviewRequest` is published.
        6.  **Dispatch:** Action commands for the selected plan are published.
    *   *Emphasis:* While many evaluation aspects in the current concrete implementation are conceptual (primarily logged to outline the process), this structured flow is designed to integrate more sophisticated, data-driven evaluations from other CMLs as they mature.
    *   *[`PiaAGI.md`](../../PiaAGI.md) Sections:* [4.1.8](../../PiaAGI.md#41-core-modules-and-their-interactions), [4.4](../../PiaAGI.md#44-action-selection-and-execution)
*   **Behavior Generation Module:** (`BaseBehaviorGenerationModule`, `ConcreteBehaviorGenerationModule`)
    *   *[`PiaAGI.md`](../../PiaAGI.md) Sections:* [4.1.9](../../PiaAGI.md#41-core-modules-and-their-interactions)
*   **Self-Model Module:** (`SelfModelModule`, `ConcreteSelfModelModule`)
    *   *[`PiaAGI.md`](../../PiaAGI.md) Sections:* [4.1.10](../../PiaAGI.md#41-core-modules-and-their-interactions)
*   **Theory of Mind Module (ToM):** (`BaseTheoryOfMindModule`, `ConcreteTheoryOfMindModule`)
    *   *[`PiaAGI.md`](../../PiaAGI.md) Sections:* [3.2.2](../../PiaAGI.md#322-theory-of-mind-tom-for-socially-aware-agi), [4.1.11](../../PiaAGI.md#41-core-modules-and-their-interactions)
*   **Communication Module:** (`BaseCommunicationModule`, `ConcreteCommunicationModule`)
    *   *[`PiaAGI.md`](../../PiaAGI.md) Sections:* [2.2](../../PiaAGI.md#22-communication-theory-for-agi-level-interaction), [4.1.12](../../PiaAGI.md#41-core-modules-and-their-interactions)
*   **World Model Module:** (`BaseWorldModel`, `ConcreteWorldModel`)
    *   *[`PiaAGI.md`](../../PiaAGI.md) Sections:* [4.3](../../PiaAGI.md#43-perception-and-world-modeling-conceptual)
*   **Base Memory Module:** (`BaseMemoryModule`, `ConcreteBaseMemoryModule`) - Foundational class for WM and LTM.
    *   *[`PiaAGI.md`](../../PiaAGI.md) Sections:* [3.1.1](../../PiaAGI.md#311-memory-systems-ltm-wm-sensory-memory-and-their-agi-relevance)

(Refer to individual Python files in this directory for specific interface methods and concrete class details. Note: Section links point to the main section in `PiaAGI.md`; specific sub-section numbers like 4.1.X are indicated in the text.)

## Future Development & Enhancements

PiaCML is envisioned to evolve significantly to fully support the PiaAGI framework's goals. Key future directions include:

1.  **Advanced Module Implementations:**
    *   Developing more sophisticated concrete implementations for all modules, moving beyond MVPs to versions that more accurately reflect the depth of psychological theories outlined in [`PiaAGI.md`](../../PiaAGI.md).
    *   **Self-Model:** Enhancing with robust metacognitive capabilities (e.g., self-monitoring of confidence, bias detection) and a dynamic, learnable ethical framework. Further conceptual details on how the `SelfModelModule` will represent, manage, and iteratively refine self-generated Meta-Cognitive Patterns (MCPs) within its `CapabilityInventory` have been elaborated in the [`Self_Model_Module_Specification.md`](./Self_Model_Module_Specification.md). This includes versioning, status tracking, and the self-correction loop for MCPs.
    *   **Long-Term Memory (LTM):** Implementing richer LTM structures, such as knowledge graphs for semantic LTM, and episodic memories that capture emotional valence and causal relationships.
    *   **Motivational System:** Creating computational models for intrinsic motivations (e.g., curiosity, competence, coherence) that can dynamically generate agent goals.
    *   **Emotion Module:** Designing appraisal mechanisms more deeply integrated with the World Model, Self-Model, and LTM to produce nuanced emotional responses.
    *   **Theory of Mind (ToM):** Building ToM modules capable of more complex inferences about other agents' mental states, aligned with developmental psychology.

2.  **Standardized Inter-Module Communication Design:**
    *   A detailed specification for the standardized communication system, including the chosen paradigm (message bus), core message structures (e.g., `PerceptData`, `LTMQuery`, `GoalUpdate`), and interaction protocols, *is available* in the [PiaCML Inter-Module Communication Design](./PiaCML_InterModule_Communication.md). The foundational `message_bus.py` and `core_messages.py` provide an MVP implementation of this. This system is crucial for effective module interaction.

3.  **Support for Architectural Maturation:**
    *   Conceptually exploring and defining how PiaCML module interfaces and implementations could support the idea of "architectural maturation" ([`PiaAGI.md` Section 3.2.1](../../PiaAGI.md#321-stages-of-cognitive-development-and-architectural-maturation)). This includes how module parameters (e.g., working memory capacity, learning rates) might change dynamically or how new conceptual pathways between modules could be formed or strengthened based on developmental progress or learning experiences. The [PiaCML Advanced Module Roadmap](./PiaCML_Advanced_Roadmap.md) further details this, including conceptual 'Architectural Maturation Hooks'.

4.  **Integration with Other PiaAGI Tools:**
    *   Ensuring seamless integration with PiaSE (for running agents built from CML modules), PiaPES (for configuring CML module parameters via prompts), and PiaAVT (for logging detailed traces from CML modules for analysis).

5.  **Continued Advanced Feature Implementation:**
    *   Continued implementation of the advanced features outlined in the module specification documents (e.g., [`Self_Model_Module_Specification.md`](./Self_Model_Module_Specification.md), [`Motivational_System_Specification.md`](./Motivational_System_Specification.md)) and the [`PiaCML_Advanced_Roadmap.md`](./PiaCML_Advanced_Roadmap.md) for modules like LTM, Emotion, and ToM.

### Advanced Module Development Roadmap

For a detailed phased development plan for advanced versions of key modules like the Self-Model, LTM, Motivational System, and Emotion Module, please see the [PiaCML Advanced Module Roadmap](./PiaCML_Advanced_Roadmap.md).

Contributions and collaborations are welcome as this library evolves to become the backbone for constructing advanced PiaAGI agents.

---
Return to [PiaAGI Core Document](../../PiaAGI.md) | [Project README](../../README.md)
```
