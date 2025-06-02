# PiaAGI Framework: AGI-Focused Examples

Welcome to the PiaAGI Examples directory! This section provides practical illustrations, detailed deep-dives, and templates to help you understand and apply the **PiaAGI AGI Research Framework**. The primary goal of these examples is to showcase how to conceptually structure "Guiding Prompts" to configure, guide, and develop PiaAGI agents with an emphasis on their psycho-cognitive architecture.

While the main [`PiaAGI.md`](../PiaAGI.md) document contains the core theoretical framework, AGI-specific use case examples (Section 7), and foundational R-U-E prompting examples (Appendix A), this directory offers supplementary and more granular materials.

The examples here aim to provide:

*   **Detailed Deep-Dives:** Focused explorations into configuring specific aspects of the PiaAGI psycho-cognitive architecture (e.g., Self-Model, Motivational System, Personality, Emotion Module) as outlined in `PiaAGI.md` (Section 4).
*   **Practical Templates:** Starting points for users wishing to experiment with "Guiding Prompts" to shape an agent's cognitive setup and developmental trajectory.
*   **Illustrations of Core Principles:** Concrete examples of applying PiaAGI concepts like developmental scaffolding for various cognitive functions (e.g., ethical reasoning, Theory of Mind) or initiating tool understanding and creation.
*   **PiaPES Usage Examples:** Insights and practical demonstrations of how the PiaAGI Prompt Engineering Suite (PiaPES) (see [`PiaAGI_Research_Tools/PiaPES/`](../PiaAGI_Research_Tools/PiaPES/)) can be used to programmatically construct, manage, and serialize these advanced prompts and curricula.
*   **Cross-Stage Development:** Examples showing how tasks and agent capabilities evolve across different PiaAGI developmental stages.
*   **Internal Metacognition:** Conceptual explorations of advanced agents performing self-analysis and internal experimentation.


## How to Use These Examples

*   **Contextual Learning:** Crucially, always refer to the main [`PiaAGI.md`](../PiaAGI.md) document to understand the theoretical underpinnings of the concepts demonstrated. Pay close attention to Sections 3 (Core Psychological Principles), 4 (Cognitive Architecture), 5 (Prompting Framework), and 6 (Methodology). These examples are applications of that core theory.
*   **Experimentation:** Adapt and test these examples in environments that can interpret PiaAGI's structured prompts. Observe how changes in prompt structure and content conceptually influence an agent's behavior and internal states.
*   **Building Blocks:** Use these examples as inspiration or foundational templates for developing your own sophisticated Guiding Prompts and Developmental Scaffolding curricula for PiaAGI agents.
*   **GitHub Rendering Note:** Some examples utilize YAML-like frontmatter for metadata. If you encounter rendering issues on GitHub, please ensure your local viewer or environment correctly parses Markdown with frontmatter. The core content of the examples remains valid Markdown.

## Example Categories and Files

This directory is structured into categories to help you find relevant examples.

### 1. Foundational Concepts & Refactored Examples

These examples illustrate core PiaAGI prompting techniques or are original examples refactored to align with the AGI framework.

*   **[`Foundational_Examples/RoleDevelopment.md`](./Foundational_Examples/RoleDevelopment.md)**: Demonstrates initializing an agent's Self-Model and role understanding, a foundational step in cognitive configuration.
*   **[`Foundational_Examples/CBT-AutoTraining.md`](./Foundational_Examples/CBT-AutoTraining.md)**: Illustrates a simulated Cognitive Behavioral Training loop for agent skill refinement, engaging the Self-Model and Learning Modules.
*   **[`Foundational_Examples/EmotionPrompt_Demo.md`](./Foundational_Examples/EmotionPrompt_Demo.md)**: Shows how emotional cues in user prompts can influence agent processing via its Emotion Module and other cognitive functions.
*   **[`Foundational_Examples/PiaCRUE_mini.md`](./Foundational_Examples/PiaCRUE_mini.md)**: A very basic R-U-E prompt structure, serving as a simple illustration. (Refer to `PiaAGI.md` Appendix A for more complete foundational R-U-E examples).
*   **[`Foundational_Examples/Hybrid_Agent_Concept_Intro.md`](./Foundational_Examples/Hybrid_Agent_Concept_Intro.md)**: Illustrates the five core characteristics of a PiaAGI Hybrid Agent in a simple, conceptual manner.
*   **[`Foundational_Examples/RaR_Communication_Principle_Demo.md`](./Foundational_Examples/RaR_Communication_Principle_Demo.md)**: Demonstrates the application of the Reasoning and Reassurance (RaR) communication principle in an agent's response.
*   **[`Foundational_Examples/CoT_Prompting_PiaAGI_Style.md`](./Foundational_Examples/CoT_Prompting_PiaAGI_Style.md)**: Demonstrates Chain-of-Thought prompting to enhance reasoning transparency, framed with PiaAGI principles.
*   **[`Foundational_Examples/Rephrase_And_Respond_Demo.md`](./Foundational_Examples/Rephrase_And_Respond_Demo.md)**: Illustrates the 'One-step Rephrase-and-Respond' technique for improved query comprehension before answering.

### 2. Cognitive Module Configuration

Detailed prompts for setting up and tuning specific cognitive modules of a PiaAGI agent.

*   **[`Cognitive_Configuration/Configuring_Motivational_System.md`](./Cognitive_Configuration/Configuring_Motivational_System.md)**: Focuses on setting up intrinsic and extrinsic goals within the Motivational System.
*   **[`Cognitive_Configuration/Setting_Personality_Profile.md`](./Cognitive_Configuration/Setting_Personality_Profile.md)**: Demonstrates defining an agent's Big Five (OCEAN) personality traits.
*   **[`Cognitive_Configuration/Configuring_Emotion_Module.md`](./Cognitive_Configuration/Configuring_Emotion_Module.md)**: Shows how to tune baseline emotional states, reactivity, and empathy levels in the Emotion Module.
*   **[`Cognitive_Configuration/Configuring_Learning_Module.md`](./Cognitive_Configuration/Configuring_Learning_Module.md)**: Illustrates configuring learning modes, rate adaptation, and ethical heuristic updates in the Learning Module(s).
*   **[`Cognitive_Configuration/Configuring_Attention_Module.md`](./Cognitive_Configuration/Configuring_Attention_Module.md)**: Demonstrates setting parameters for the Attention Module, such as top-down focus versus bottom-up stimulus capture.

### 3. Developmental Scaffolding

Examples of Guiding Prompts that initiate and guide an agent's learning and development for specific capabilities.

*   **[`Developmental_Scaffolding/Scaffolding_Basic_ToM.md`](./Developmental_Scaffolding/Scaffolding_Basic_ToM.md)**: An introductory exercise for developing basic Theory of Mind (emotion recognition) in an early-stage agent.
*   **[`Developmental_Scaffolding/Scaffolding_Ethical_Reasoning_Intro.md`](./Developmental_Scaffolding/Scaffolding_Ethical_Reasoning_Intro.md)**: Guides a PiaSapling agent through analyzing a simple ethical dilemma to build its ethical reasoning capacity.
*   **[`Developmental_Scaffolding/Scaffolding_Intermediate_ToM.md`](./Developmental_Scaffolding/Scaffolding_Intermediate_ToM.md)**: Focuses on scaffolding Theory of Mind for understanding false beliefs in a PiaSapling/Early PiaArbor agent.
*   **[`Developmental_Scaffolding/Cultivating_Intrinsic_Motivation.md`](./Developmental_Scaffolding/Cultivating_Intrinsic_Motivation.md)**: Designs scenarios to cultivate intrinsic motivations like curiosity and competence.

### 4. Tool Use and Understanding

Prompts designed to introduce tools (conceptual or otherwise) to an agent, guide its initial interactions, and stimulate tool adaptation or creation.

*   **[`Tool_Use/Introducing_Conceptual_Tools.md`](./Tool_Use/Introducing_Conceptual_Tools.md)**: Teaches an agent to understand and apply a simple conceptual tool (e.g., the "5 Whys" checklist).
*   **[`Tool_Use/Adapting_Conceptual_Tools.md`](./Tool_Use/Adapting_Conceptual_Tools.md)**: Illustrates an agent adapting a known conceptual tool (e.g., SWOT analysis) for a new purpose.
*   **[`Tool_Use/Agent_Requesting_New_Tool.md`](./Tool_Use/Agent_Requesting_New_Tool.md)**: Shows an agent identifying a capability gap and formulating a request for a new tool.
*   **[`Tool_Use/Agent_Designing_Simple_Tool.md`](./Tool_Use/Agent_Designing_Simple_Tool.md)**: Conceptually illustrates a PiaArbor stage agent designing a simple new conceptual or software tool.

### 5. PiaPES Usage

Examples related to the PiaAGI Prompt Engineering Suite (PiaPES).

*   **[`PiaPES_Usage/Building_A_Role_Prompt_With_PiaPES.md`](./PiaPES_Usage/Building_A_Role_Prompt_With_PiaPES.md)**: Conceptually illustrates how the PiaPES Python engine could be used to programmatically construct a complex role definition prompt.
*   **[`PiaPES_Usage/Generating_Prompt_With_PiaPES_Engine.md`](./PiaPES_Usage/Generating_Prompt_With_PiaPES_Engine.md)**: Provides a concrete Python script using `prompt_engine_mvp.py` to generate and serialize a Guiding Prompt with detailed cognitive configurations.
*   **[`PiaPES_Usage/Defining_Developmental_Curriculum_PiaPES.md`](./PiaPES_Usage/Defining_Developmental_Curriculum_PiaPES.md)**: Conceptually illustrates how a `DevelopmentalCurriculum` object within PiaPES could be defined to sequence Guiding Prompts.

### 6. Cross-Stage Development

Examples showcasing how tasks or agent capabilities evolve across different PiaAGI developmental stages.

*   **[`Cross_Stage_Development/Task_Summarization_Evolution.md`](./Cross_Stage_Development/Task_Summarization_Evolution.md)**: Demonstrates how the approach to text summarization evolves with different Guiding Prompts and expected outcomes for PiaSeedling, PiaSapling, and PiaArbor stage agents.

### 7. Internal Metacognition (Advanced Concepts)

Conceptual explorations of highly advanced PiaAGI agents performing self-analysis and internal experimentation, internalizing principles from the PiaAGI Research Tools.

*   **[`Internal_Metacognition/Self_Monitoring_PiaAVT_Principles.md`](./Internal_Metacognition/Self_Monitoring_PiaAVT_Principles.md)**: Conceptually illustrates an agent internalizing PiaAVT-like principles for self-monitoring its cognitive performance and biases.
*   **[`Internal_Metacognition/Internal_Experimentation_PiaSE_Principles.md`](./Internal_Metacognition/Internal_Experimentation_PiaSE_Principles.md)**: Conceptually explores an agent using PiaSE-like principles for internal 'what-if' scenario analysis and hypothesis testing.

*(This list will be expanded as more examples are developed, guided by the `ToDoList.md` in the project root.)*

## A Note on PiaCRUE

The PiaAGI framework is an evolution of the earlier PiaCRUE methodology. While PiaCRUE focused on enhancing LLM interaction through structured prompting, PiaAGI significantly expands this scope to address core AGI research challenges with a psycho-cognitively plausible architecture. Foundational R-U-E prompting examples, which originated with PiaCRUE, can now be found in Appendix A of [`PiaAGI.md`](../PiaAGI.md).

---

We encourage community contributions to expand this collection of AGI-focused examples, helping to advance the collective understanding and application of the PiaAGI framework. Please refer to the main project [`CONTRIBUTING.md`](../CONTRIBUTING.md).

## Conceptual Examples

*   **`PiaAGI_Behavior_Example.py`**: A conceptual Python script illustrating simplified interactions between core PiaAGI cognitive modules. Useful for thought experiments and understanding architectural ideas.
