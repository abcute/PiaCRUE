# PiaAGI Cognitive Module Library (CML)

## Purpose

The Cognitive Module Library (CML) is a core component of the PiaAGI project. Its primary purpose is to define abstract interfaces and, eventually, provide foundational Python implementations for the various cognitive modules outlined in the [PiaAGI Cognitive Architecture](../../PiaAGI.md#4-the-piaagi-cognitive-architecture).

This library aims to:
1.  **Standardize Interfaces:** Provide common Python Abstract Base Classes (ABCs) for each cognitive module, ensuring that different implementations of a module can be used interchangeably within the broader PiaAGI framework.
2.  **Facilitate Modular Development:** Allow researchers and developers to focus on specific cognitive functions by working on individual modules.
3.  **Support Simulation and Experimentation:** Enable the construction of PiaAGI agent simulations by composing these modules, as demonstrated conceptually in `PiaAGI_Hub/conceptual_simulations/PiaAGI_Behavior_Example.py`.
4.  **Promote Code Reusability:** Offer well-documented and tested base components that can be extended or used directly in more complex AGI implementations.
5.  **Align with Theory:** Ensure that module designs and interfaces are closely mapped to the theoretical descriptions in the main `PiaAGI.md` document.

## Current Abstract Interfaces

This initial version of the CML provides abstract base classes for the following modules:

1.  **`base_memory_module.py` (`BaseMemoryModule`)**:
    *   **Purpose:** Defines the fundamental interface common to all memory systems within PiaAGI. It outlines core operations like storing information, retrieving it based on queries, managing memory capacity, and handling forgetting.
    *   **PiaAGI.md Sections:** 3.1.1 (Memory Systems), 4.1.2 (Working Memory Module), 4.1.3 (Long-Term Memory Module).

2.  **`long_term_memory_module.py` (`LongTermMemoryModule`)**:
    *   **Purpose:** Extends `BaseMemoryModule` to define the interface for Long-Term Memory. LTM is the AGI's vast repository for semantic knowledge, episodic experiences, and procedural skills. This interface includes methods specific to these LTM sub-components.
    *   **PiaAGI.md Sections:** 3.1.1 (LTM details), 4.1.3 (Long-Term Memory Module).

3.  **`working_memory_module.py` (`WorkingMemoryModule`)**:
    *   **Purpose:** Extends `BaseMemoryModule` to define the interface for Working Memory. WM is a limited-capacity system for temporarily holding and actively processing information relevant to current tasks. It also conceptually includes functions of the Central Executive (attention, coordination).
    *   **PiaAGI.md Sections:** 3.1.1 (WM details), 3.1.2 (Attention and Cognitive Control/Central Executive), 4.1.2 (Working Memory Module).

4.  **`perception_module.py` (`PerceptionModule`)**:
    *   **Purpose:** Responsible for receiving raw sensory input (e.g., text, vision, audio), processing it, extracting features, and generating a structured perceptual representation for other modules. Crucial for grounding internal representations in external reality.
    *   **PiaAGI.md Sections:** 4.1.1 (Perception Module), 4.3 (Perception and World Modeling).

5.  **`motivational_system_module.py` (`MotivationalSystemModule`)**:
    *   **Purpose:** Manages the AGI's goals, drives, and overall motivation. It selects and prioritizes goals, influencing decision-making and behavior based on intrinsic and extrinsic factors.
    *   **PiaAGI.md Sections:** 3.3 (Motivational Systems and Intrinsic Goals), 4.1.6 (Motivational System Module).

6.  **`emotion_module.py` (`EmotionModule`)**:
    *   **Purpose:** Generates, processes, and modulates emotional states. Emotions influence perception, cognition, decision-making, and social interaction, enabling more nuanced and adaptive behavior.
    *   **PiaAGI.md Sections:** 3.4 (Computational Models of Emotion), 4.1.7 (Emotion Module).

7.  **`planning_decision_making_module.py` (`PlanningAndDecisionMakingModule`)**:
    *   **Purpose:** Handles higher-level cognitive functions like evaluating courses of action, forming plans to achieve goals, and making choices among alternatives. Integrates information from the World Model, Motivational System, Perception, and Emotion Modules.
    *   **PiaAGI.md Sections:** 4.1.8 (Planning and Decision-Making Module), 4.4 (Action Selection and Execution).

8.  **`self_model_module.py` (`SelfModelModule`)**:
    *   **Purpose:** Maintains a dynamic representation of the AGI itself, including its capabilities, limitations, internal states, interaction history, performance, and ethical framework. Crucial for metacognition, self-awareness, and self-improvement.
    *   **PiaAGI.md Sections:** 4.1.10 (Self-Model Module).

9.  **`learning_module.py` (`BaseLearningModule`)**:
    *   **Purpose:** Responsible for acquiring new knowledge and skills, adapting existing representations, and improving performance over time. It encompasses various learning paradigms and interacts with multiple cognitive modules.
    *   **PiaAGI.md Sections:** 3.1.3 (Learning Theories and Mechanisms for AGI), 4.1.5 (Learning Module(s)).

10. **`behavior_generation_module.py` (`BaseBehaviorGenerationModule`)**:
    *   **Purpose:** Translates abstract action selections or plans into concrete, executable behaviors, such as linguistic output (via Communication Module), tool use, or physical actions.
    *   **PiaAGI.md Sections:** 4.1.9 (Behavior Generation Module (Action Execution)).

11. **`tom_module.py` (`BaseTheoryOfMindModule`)**:
    *   **Purpose:** Enables the AGI to attribute mental states (beliefs, desires, intentions, emotions) to other agents and understand differing perspectives, crucial for advanced social interaction.
    *   **PiaAGI.md Sections:** 3.2.2 (Theory of Mind (ToM) for Socially Aware AGI), 4.1.11 (Theory of Mind (ToM) / Social Cognition Module).

12. **`communication_module.py` (`BaseCommunicationModule`)**:
    *   **Purpose:** Manages nuanced natural language interaction (NLU/NLG), implements advanced communication strategies (e.g., CSIM, RaR), and integrates with ToM, Emotion, and Self-Model modules.
    *   **PiaAGI.md Sections:** 2.2 (Communication Theory for AGI-Level Interaction), 4.1.12 (Communication Module).

## Concrete Implementations

This section lists available concrete implementations of the abstract module interfaces.

1.  **[`ConcreteBaseMemoryModule`](concrete_base_memory_module.py)** ([Tests](tests/test_concrete_base_memory_module.py)):
    *   **Implements:** `BaseMemoryModule`
    *   **Purpose:** Provides a basic, in-memory concrete implementation of the `BaseMemoryModule` interface. It uses a Python dictionary for storage and assigns a unique ID to each memory item.
    *   **Functionality:**
        *   Implements `store` (returns memory ID), `retrieve` (by ID or concept query) methods using dictionary lookups.
        *   Includes `delete_memory(memory_id)` for removing items by ID.
        *   Provides placeholders for `manage_capacity`, `handle_forgetting`.
        *   Includes additional placeholder methods: `update_memory_decay(memory_id, decay_factor)` and `find_similar_memories(query_embedding, top_n)`.
        *   Offers a `get_status` method reporting basic statistics (e.g., total items).
    *   **Usage:** Serves as a foundational example and can be used for simple simulations or as a starting point for more complex memory systems.

2.  **[`ConcreteAttentionModule`](concrete_attention_module.py)** ([Tests](tests/test_concrete_attention_module.py)):
    *   **Implements:** `BaseAttentionModule`
    *   **Purpose:** Provides a basic concrete implementation of the `BaseAttentionModule`. It uses a simple dictionary for current focus and rule-based logic for filtering and load management.
    *   **Functionality:**
        *   Implements `direct_attention` based on priority.
        *   Implements `filter_information` based on string/tag matching to current focus.
        *   Implements `manage_cognitive_load` with simple threshold checks.
        *   Implements `get_attentional_state` to report internal status.
    *   **Usage:** Suitable for initial simulations requiring basic attention mechanisms or as a template for more advanced implementations.

3.  **[`ConcreteLearningModule`](concrete_learning_module.py)** ([Tests](tests/test_concrete_learning_module.py)):
    *   **Implements:** `BaseLearningModule`
    *   **Purpose:** Provides a very basic concrete implementation of `BaseLearningModule`. It primarily logs learning attempts and feedback, with a conceptual 'direct_store' paradigm and placeholder ethical checks.
    *   **Functionality:**
        *   `learn`: Logs learning attempts; conceptually handles 'direct_store' and a 'supervised_dummy' paradigm.
        *   `process_feedback`: Logs feedback data.
        *   `consolidate_knowledge`: Placeholder.
        *   `get_learning_status`: Reports on logged attempts and simple task status.
        *   `apply_ethical_guardrails`: Basic placeholder checks.
    *   **Usage:** Suitable for initial simulations needing a mock learning module or as a very basic template for more sophisticated learning algorithm integrations.

4.  **[`ConcreteBehaviorGenerationModule`](concrete_behavior_generation_module.py)** ([Tests](tests/test_concrete_behavior_generation_module.py)):
    *   **Implements:** `BaseBehaviorGenerationModule`
    *   **Purpose:** Provides a basic concrete implementation of `BaseBehaviorGenerationModule`. It translates action plans into structured dictionaries representing executable behaviors.
    *   **Functionality:**
        *   `generate_behavior`: Maps action plans for 'communicate', 'use_tool', and 'log_internal_state' to behavior specification dictionaries. Includes original plan for traceability.
        *   `get_status`: Reports supported behavior types.
    *   **Usage:** Suitable for simulations where behavior execution is handled by interpreting the output dictionary, or as a base for modules interfacing with specific actuators or APIs.

5.  **[`ConcreteTheoryOfMindModule`](concrete_tom_module.py)** ([Tests](tests/test_concrete_tom_module.py)):
    *   **Implements:** `BaseTheoryOfMindModule`
    *   **Purpose:** Provides a very basic concrete implementation of `BaseTheoryOfMindModule`. It uses a dictionary to store agent models and simple rules for state inference.
    *   **Functionality:**
        *   `infer_mental_state`: Applies rudimentary rules based on utterance and expression keywords to infer desire, intention, or emotion. Logs inferences.
        *   `update_agent_model`: Stores or updates agent-specific data in an internal dictionary.
        *   `get_agent_model`: Retrieves the stored model for an agent.
    *   **Usage:** Suitable for initial simulations requiring a mock ToM, or as a starting point for developing more sophisticated mental state inference engines.

6.  **[`ConcreteCommunicationModule`](concrete_communication_module.py)** ([Tests](tests/test_concrete_communication_module.py)):
    *   **Implements:** `BaseCommunicationModule`
    *   **Purpose:** Provides a basic concrete implementation of `BaseCommunicationModule`. It uses keyword-based NLU, template-based NLG, and dictionary-based dialogue state management.
    *   **Functionality:**
        *   `process_incoming_communication`: Simple keyword matching for intent (e.g., weather, greeting) and entity extraction from text.
        *   `generate_outgoing_communication`: Template-filling for predefined intents.
        *   `manage_dialogue_state`: Tracks dialogue history and turn counts in a dictionary. Supports custom context.
        *   `apply_communication_strategy`: Placeholder that returns a default or the first available strategy.
        *   `get_module_status`: Reports active dialogues and conceptual strategies.
    *   **Usage:** Suitable for simple task-oriented dialogue simulations or as a foundation for more sophisticated conversational AI components.

7.  **[`ConcreteLongTermMemoryModule`](concrete_long_term_memory_module.py)** ([Tests](tests/test_concrete_long_term_memory_module.py)):
    *   **Implements:** `BaseLongTermMemoryModule` (and by extension `BaseMemoryModule`)
    *   **Purpose:** Provides a concrete implementation for LTM, differentiating between episodic, semantic, and procedural memory by using an internal `ConcreteBaseMemoryModule` and tagging data with an `ltm_type` in its context.
    *   **Functionality:**
        *   Implements `store_<type>`, `retrieve_<type>` methods for episodic, semantic, and procedural memories.
        *   Delegates basic store, retrieve, delete operations to the internal `ConcreteBaseMemoryModule`, adding `ltm_type` context.
        *   Tracks basic stats for each subcomponent (items stored, queries made).
        *   Includes placeholder for `manage_ltm_subcomponents`.
    *   **Usage:** Suitable for simulations needing distinct LTM functionalities and provides a clear example of composing memory modules. Assumes the underlying `ConcreteBaseMemoryModule`'s `retrieve` method can filter based on context criteria for typed retrievals.

8.  **[`ConcreteWorkingMemoryModule`](concrete_working_memory_module.py)** ([Tests](tests/test_concrete_working_memory_module.py)):
    *   **Implements:** `BaseWorkingMemoryModule` (and by extension `BaseMemoryModule`)
    *   **Purpose:** Provides a basic concrete implementation for Working Memory. It manages a capacity-limited list of items with unique WM-specific IDs and salience values.
    *   **Functionality:**
        *   Adapts `store`, `retrieve`, `delete_memory` from `BaseMemoryModule` for a transient, ID-based workspace.
        *   Implements `add_item_to_workspace`, `remove_item_from_workspace`, `get_workspace_contents`.
        *   Manages `set_active_focus` and `get_active_focus` on items within the workspace.
        *   `manage_workspace_capacity_and_coherence` enforces capacity by removing least salient items.
        *   `handle_forgetting` includes a conceptual 'decay_salience' strategy.
    *   **Usage:** Suitable for simulations requiring a basic, capacity-aware cognitive workspace with item salience and focus mechanisms.

9.  **[`ConcretePerceptionModule`](concrete_perception_module.py)** ([Tests](tests/test_concrete_perception_module.py)):
    *   **Implements:** `BasePerceptionModule`
    *   **Purpose:** Provides a basic concrete implementation of `BasePerceptionModule`. It performs simple keyword spotting on text inputs and wraps dictionary inputs.
    *   **Functionality:**
        *   `process_sensory_input`: For "text" modality, identifies predefined keywords for conceptual entities (apple, ball, user, Pia) and actions (give, see, greet). For "dict_mock" modality, it wraps the input dictionary. Other modalities are marked unsupported.
        *   `get_module_status`: Reports supported modalities and processing log count.
    *   **Usage:** Suitable for simulations requiring very basic NLU or mock sensory input processing, or as a template for integrating more sophisticated perception tools.

## Future Development

The CML will be expanded to include interfaces and foundational implementations for other core PiaAGI cognitive modules, such as:
*   Attention Module (potentially integrated more deeply with Perception and Working Memory)
*   World Model (though this might be more of a data structure and service used by many modules)

Contributions and collaborations are welcome as this library evolves.
