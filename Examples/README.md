# PiaAGI Framework: AGI-Focused Examples

Welcome to the PiaAGI Examples directory! This section provides practical illustrations, detailed deep-dives, and templates to help you understand and apply the **PiaAGI AGI Research Framework**. The primary goal of these examples is to showcase how to conceptually structure "Guiding Prompts" to configure, guide, and develop PiaAGI agents with an emphasis on their psycho-cognitive architecture.

While the main [`PiaAGI.md`](../PiaAGI.md) document contains the core theoretical framework, AGI-specific use case examples (Section 7), and foundational R-U-E prompting examples (Appendix A), this directory offers supplementary and more granular materials.

The examples here aim to provide:

*   **Detailed Deep-Dives:** Focused explorations into configuring specific aspects of the PiaAGI psycho-cognitive architecture (e.g., Self-Model, Motivational System, Personality, Emotion Module) as outlined in `PiaAGI.md` (Section 4).
*   **Practical Templates:** Starting points for users wishing to experiment with "Guiding Prompts" to shape an agent's cognitive setup and developmental trajectory.
*   **Illustrations of Core Principles:** Concrete examples of applying PiaAGI concepts like developmental scaffolding for various cognitive functions (e.g., ethical reasoning, Theory of Mind) or initiating tool understanding.
*   **PiaPES Usage Examples:** Insights and practical demonstrations of how the PiaAGI Prompt Engineering Suite (PiaPES) (see [`PiaAGI_Research_Tools/PiaPES/`](../PiaAGI_Research_Tools/PiaPES/)) can be used to programmatically construct, manage, and serialize these advanced prompts.

## How to Use These Examples

*   **Contextual Learning:** Crucially, always refer to the main [`PiaAGI.md`](../PiaAGI.md) document to understand the theoretical underpinnings of the concepts demonstrated. Pay close attention to Sections 3 (Core Psychological Principles), 4 (Cognitive Architecture), 5 (Prompting Framework), and 6 (Methodology). These examples are applications of that core theory.
*   **Experimentation:** Adapt and test these examples in environments that can interpret PiaAGI's structured prompts. Observe how changes in prompt structure and content conceptually influence an agent's behavior and internal states.
*   **Building Blocks:** Use these examples as inspiration or foundational templates for developing your own sophisticated Guiding Prompts and Developmental Scaffolding curricula for PiaAGI agents.
*   **GitHub Rendering Note:** Some examples utilize YAML-like frontmatter for metadata. If you encounter rendering issues on GitHub, please ensure your local viewer or environment correctly parses Markdown with frontmatter. The core content of the examples remains valid Markdown.

## Example Categories and Files

This directory is structured into categories to help you find relevant examples.

### 1. Foundational Concepts & Refactored Examples

These examples illustrate core PiaAGI prompting techniques or are original examples refactored to align with the AGI framework.

*   **[`RoleDevelopment.md`](./Foundational_And_Refactored/RoleDevelopment.md)**: Demonstrates initializing an agent's Self-Model and role understanding, a foundational step in cognitive configuration.
*   **[`CBT-AutoTraining.md`](./Foundational_And_Refactored/CBT-AutoTraining.md)**: Illustrates a simulated Cognitive Behavioral Training loop for agent skill refinement, engaging the Self-Model and Learning Modules.
*   **[`EmotionPrompt_Demo.md`](./Foundational_And_Refactored/EmotionPrompt_Demo.md)**: Shows how emotional cues in user prompts can influence agent processing via its Emotion Module and other cognitive functions.
*   **[`PiaCRUE_mini.md`](./Foundational_And_Refactored/PiaCRUE_mini.md)**: A very basic R-U-E prompt structure, serving as a simple illustration. (Refer to `PiaAGI.md` Appendix A for more complete foundational R-U-E examples).
*   **[`Hybrid_Agent_Concept_Intro.md`](./Foundational_And_Refactored/Hybrid_Agent_Concept_Intro.md)**: Illustrates the five core characteristics of a PiaAGI Hybrid Agent in a simple, conceptual manner.
*   **[`RaR_Communication_Principle_Demo.md`](./Foundational_And_Refactored/RaR_Communication_Principle_Demo.md)**: Demonstrates the application of the Reasoning and Reassurance (RaR) communication principle in an agent's response.

### 2. Cognitive Module Configuration

Detailed prompts for setting up and tuning specific cognitive modules of a PiaAGI agent.

*   **[`Cognitive_Configuration/Configuring_Motivational_System.md`](./Cognitive_Configuration/Configuring_Motivational_System.md)**: Focuses on setting up intrinsic and extrinsic goals within the Motivational System.
*   **[`Cognitive_Configuration/Setting_Personality_Profile.md`](./Cognitive_Configuration/Setting_Personality_Profile.md)**: Demonstrates defining an agent's Big Five (OCEAN) personality traits.
*   **[`Cognitive_Configuration/Configuring_Emotion_Module.md`](./Cognitive_Configuration/Configuring_Emotion_Module.md)**: Shows how to tune baseline emotional states, reactivity, and empathy levels in the Emotion Module.

### 3. Developmental Scaffolding

Examples of Guiding Prompts that initiate and guide an agent's learning and development for specific capabilities.

*   **[`Developmental_Scaffolding/Scaffolding_Basic_ToM.md`](./Developmental_Scaffolding/Scaffolding_Basic_ToM.md)**: An introductory exercise for developing basic Theory of Mind (emotion recognition) in an early-stage agent.
*   **[`Developmental_Scaffolding/Scaffolding_Ethical_Reasoning_Intro.md`](./Developmental_Scaffolding/Scaffolding_Ethical_Reasoning_Intro.md)**: Guides a PiaSapling agent through analyzing a simple ethical dilemma to build its ethical reasoning capacity.

### 4. Tool Use and Understanding

Prompts designed to introduce tools (conceptual or otherwise) to an agent and guide its initial interactions.

*   **[`Tool_Use/Introducing_Conceptual_Tools.md`](./Tool_Use/Introducing_Conceptual_Tools.md)**: Teaches an agent to understand and apply a simple conceptual tool (e.g., the "5 Whys" checklist).

### 5. PiaPES Usage

Examples related to the PiaAGI Prompt Engineering Suite (PiaPES).

*   **[`PiaPES_Usage/Building_A_Role_Prompt_With_PiaPES.md`](./PiaPES_Usage/Building_A_Role_Prompt_With_PiaPES.md)**: Conceptually illustrates how the PiaPES Python engine could be used to programmatically construct a complex role definition prompt.
*   **[`PiaPES_Usage/Generating_Prompt_With_PiaPES_Engine.md`](./PiaPES_Usage/Generating_Prompt_With_PiaPES_Engine.md)**: Provides a more concrete Python script using `prompt_engine_mvp.py` to generate and serialize a Guiding Prompt.

*(This list will be expanded as more examples are developed, guided by the `ToDoList.md` in the project root.)*

## A Note on PiaCRUE

The PiaAGI framework is an evolution of the earlier PiaCRUE methodology. While PiaCRUE focused on enhancing LLM interaction through structured prompting, PiaAGI significantly expands this scope to address core AGI research challenges with a psycho-cognitively plausible architecture. Foundational R-U-E prompting examples, which originated with PiaCRUE, can now be found in Appendix A of [`PiaAGI.md`](../PiaAGI.md).

---

We encourage community contributions to expand this collection of AGI-focused examples, helping to advance the collective understanding and application of the PiaAGI framework. Please refer to the main project [`CONTRIBUTING.md`](../CONTRIBUTING.md).
