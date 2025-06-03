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

CML provides abstract base classes (ABCs) and some concrete MVP (Minimal Viable Product) implementations for core cognitive modules. These concrete implementations serve as initial examples and testbeds.

**Key Modules (Interfaces Defined, some with Concrete MVPs):**
*   **Memory Systems:**
    *   `BaseMemoryModule`, `LongTermMemoryModule` (LTM), `WorkingMemoryModule` (WM)
    *   Concrete MVPs: `ConcreteBaseMemoryModule`, `ConcreteLongTermMemoryModule`, `ConcreteWorkingMemoryModule`
    *   *PiaAGI.md Sections:* [3.1.1](../../PiaAGI.md#311-memory-systems-ltm-wm-sensory-memory-and-their-agi-relevance), [4.1.2](../../PiaAGI.md#41-core-modules-and-their-interactions) (WM), [4.1.3](../../PiaAGI.md#41-core-modules-and-their-interactions) (LTM)
*   **Perception:** `PerceptionModule`
    *   Concrete MVP: `ConcretePerceptionModule`
    *   *PiaAGI.md Sections:* [4.1.1](../../PiaAGI.md#41-core-modules-and-their-interactions), [4.3](../../PiaAGI.md#43-perception-and-world-modeling-conceptual)
*   **Motivation:** `MotivationalSystemModule`
    *   Concrete MVP: `ConcreteMotivationalSystemModule`
    *   *PiaAGI.md Sections:* [3.3](../../PiaAGI.md#33-motivational-systems-and-intrinsic-goals), [4.1.6](../../PiaAGI.md#41-core-modules-and-their-interactions)
*   **Emotion:** `EmotionModule`
    *   Concrete MVP: `ConcreteEmotionModule`
    *   *PiaAGI.md Sections:* [3.4](../../PiaAGI.md#34-computational-models-of-emotion), [4.1.7](../../PiaAGI.md#41-core-modules-and-their-interactions)
*   **Planning & Decision Making:** `PlanningAndDecisionMakingModule`
    *   Concrete MVP: `ConcretePlanningAndDecisionMakingModule`
    *   *PiaAGI.md Sections:* [4.1.8](../../PiaAGI.md#41-core-modules-and-their-interactions), [4.4](../../PiaAGI.md#44-action-selection-and-execution)
*   **Self-Model:** `SelfModelModule`
    *   Concrete MVP: `ConcreteSelfModelModule`
    *   *PiaAGI.md Sections:* [4.1.10](../../PiaAGI.md#41-core-modules-and-their-interactions)
*   **Learning:** `BaseLearningModule`
    *   Concrete MVP: `ConcreteLearningModule`
    *   *PiaAGI.md Sections:* [3.1.3](../../PiaAGI.md#313-learning-theories-and-mechanisms-for-agi), [4.1.5](../../PiaAGI.md#41-core-modules-and-their-interactions)
*   **Behavior Generation:** `BaseBehaviorGenerationModule`
    *   Concrete MVP: `ConcreteBehaviorGenerationModule`
    *   *PiaAGI.md Sections:* [4.1.9](../../PiaAGI.md#41-core-modules-and-their-interactions)
*   **Theory of Mind (ToM):** `BaseTheoryOfMindModule`
    *   Concrete MVP: `ConcreteTheoryOfMindModule`
    *   *PiaAGI.md Sections:* [3.2.2](../../PiaAGI.md#322-theory-of-mind-tom-for-socially-aware-agi), [4.1.11](../../PiaAGI.md#41-core-modules-and-their-interactions)
*   **Communication:** `BaseCommunicationModule`
    *   Concrete MVP: `ConcreteCommunicationModule`
    *   *PiaAGI.md Sections:* [2.2](../../PiaAGI.md#22-communication-theory-for-agi-level-interaction), [4.1.12](../../PiaAGI.md#41-core-modules-and-their-interactions)
*   **World Model:** `BaseWorldModel`
    *   Concrete MVP: `ConcreteWorldModel`
    *   *PiaAGI.md Sections:* [4.3](../../PiaAGI.md#43-perception-and-world-modeling-conceptual)
*   **Attention:** `BaseAttentionModule`
    *   Concrete MVP: `ConcreteAttentionModule`
    *   *PiaAGI.md Sections:* [3.1.2](../../PiaAGI.md#312-attention-and-cognitive-control-central-executive-functions), [4.1.4](../../PiaAGI.md#41-core-modules-and-their-interactions)


(Refer to individual Python files in this directory for specific interface methods and concrete class details.)

## Future Development & Enhancements

PiaCML is envisioned to evolve significantly to fully support the PiaAGI framework's goals. Key future directions include:

1.  **Advanced Module Implementations:**
    *   Developing more sophisticated concrete implementations for all modules, moving beyond MVPs to versions that more accurately reflect the depth of psychological theories outlined in `PiaAGI.md`.
    *   **Self-Model:** Enhancing with robust metacognitive capabilities (e.g., self-monitoring of confidence, bias detection) and a dynamic, learnable ethical framework. Further conceptual details on how the `SelfModelModule` will represent, manage, and iteratively refine self-generated Meta-Cognitive Patterns (MCPs) within its `CapabilityInventory` have been elaborated in the `Self_Model_Module_Specification.md`. This includes versioning, status tracking, and the self-correction loop for MCPs.
    *   **Long-Term Memory (LTM):** Implementing richer LTM structures, such as knowledge graphs for semantic LTM, and episodic memories that capture emotional valence and causal relationships.
    *   **Motivational System:** Creating computational models for intrinsic motivations (e.g., curiosity, competence, coherence) that can dynamically generate agent goals.
    *   **Emotion Module:** Designing appraisal mechanisms more deeply integrated with the World Model, Self-Model, and LTM to produce nuanced emotional responses.
    *   **Theory of Mind (ToM):** Building ToM modules capable of more complex inferences about other agents' mental states, aligned with developmental psychology.

2.  **Standardized Inter-Module Communication Design:**
    *   A detailed specification for the standardized communication system, including the chosen paradigm (message bus), core message structures (e.g., `PerceptData`, `LTMQuery`, `GoalUpdate`), and interaction protocols, is available in the [PiaCML Inter-Module Communication Design](./PiaCML_InterModule_Communication.md). This system is crucial for effective module interaction.

3.  **Support for Architectural Maturation:**
    *   Conceptually exploring and defining how PiaCML module interfaces and implementations could support the idea of "architectural maturation" ([`PiaAGI.md` Section 3.2.1](../../PiaAGI.md#321-stages-of-cognitive-development-and-architectural-maturation)). This includes how module parameters (e.g., working memory capacity, learning rates) might change dynamically or how new conceptual pathways between modules could be formed or strengthened based on developmental progress or learning experiences.

4.  **Integration with Other PiaAGI Tools:**
    *   Ensuring seamless integration with PiaSE (for running agents built from CML modules), PiaPES (for configuring CML module parameters via prompts), and PiaAVT (for logging detailed traces from CML modules for analysis).

### Advanced Module Development Roadmap

For a detailed phased development plan for advanced versions of key modules like the Self-Model, LTM, Motivational System, and Emotion Module, please see the [PiaCML Advanced Module Roadmap](./PiaCML_Advanced_Roadmap.md).

Contributions and collaborations are welcome as this library evolves to become the backbone for constructing advanced PiaAGI agents.

---
Return to [PiaAGI Core Document](../../PiaAGI.md) | [Project README](../../README.md)
```
