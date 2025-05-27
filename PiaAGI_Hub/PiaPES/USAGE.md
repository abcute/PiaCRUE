# PiaAGI Prompt Engine MVP - Usage Guide

This document describes the Minimal Viable Product (MVP) for the PiaAGI Prompt Templating Engine, a component of the PiaPES (PiaAGI Prompt Engineering Suite).

## Overview

The Prompt Engine MVP provides a Python-based system for:
1.  Defining structured PiaAGI prompt templates using Python classes.
2.  Embedding placeholders within these templates.
3.  Filling these placeholders with specific data.
4.  Rendering the complete, data-filled prompt into a formatted Markdown string.

This allows for systematic construction, management, and customization of complex prompts designed to configure and guide PiaAGI agents, particularly in AGI development and research contexts.

## Core Components

The engine is built around a set of Python classes mirroring the structure of a PiaAGI Guiding Prompt, as outlined in the `PiaAGI.md` document's Appendix. Key classes include:

*   `PiaAGIPrompt`: The main container for the entire prompt.
*   `SystemRules`: Defines system-level communication and processing rules.
*   `Requirements`: Specifies the task, goals, context, constraints, and success metrics.
*   `UsersInteractors`: Describes the entities the AGI will interact with.
*   `Executors`: Contains the `Role` definition.
*   `Role`: Defines the AGI's persona, skills, knowledge, and crucial cognitive configurations.
    *   `CognitiveModuleConfiguration`: A sub-component of `Role` that groups specific configurations for:
        *   `PersonalityConfig`: Sets OCEAN personality trait values.
        *   `MotivationalBias`: Defines intrinsic and extrinsic goal biases.
        *   `EmotionalProfile`: Configures baseline emotional states and reactivity.
        *   `LearningModuleConfig`: Specifies parameters for the learning systems.
*   `Workflow`: Outlines a sequence of operational or developmental steps.
    *   `WorkflowStep`: Defines individual steps within a workflow.
*   `DevelopmentalScaffolding`: Provides context if the prompt is part of a larger developmental curriculum.
*   `CBTAutoTraining`: Defines parameters for self-training or refinement scenarios.

All classes inherit from a `BaseElement` class that provides the placeholder filling and Markdown rendering logic.

## Placeholder System

Placeholders can be embedded in any string attribute of these classes using curly braces, e.g., `{topic}`, `{user_persona}`, `{skill_level}`. The `fill_placeholders(data: Dict[str, str])` method is used to substitute these with actual values.

## Rendering

The `render()` method on a `PiaAGIPrompt` object (or any `BaseElement`) will generate a Markdown formatted string representing the prompt structure and its content. Headers are used to delineate sections, and lists/dictionaries are formatted appropriately.

## Python Usage Example

The following example demonstrates how to use the `prompt_engine_mvp.py` script:

```python
from prompt_engine_mvp import (
    PiaAGIPrompt, SystemRules, Requirements, UsersInteractors, Executors, Role,
    CognitiveModuleConfiguration, PersonalityConfig, MotivationalBias, EmotionalProfile, LearningModuleConfig,
    Workflow, WorkflowStep, DevelopmentalScaffolding, CBTAutoTraining
)

# 1. Define a prompt template structure

# Define cognitive configurations
personality = PersonalityConfig(ocean_openness=0.8, ocean_conscientiousness=0.7, ocean_neuroticism="{neuro_level}")
motivation = MotivationalBias(biases={"IntrinsicGoal_Curiosity": "High", "ExtrinsicGoal_TaskCompletion": "{task_priority}"})
emotion = EmotionalProfile(baseline_valence="Neutral", empathy_level_target="High_Cognitive")
learning_config = LearningModuleConfig(primary_learning_mode="SL_From_Feedback")

cognitive_config = CognitiveModuleConfiguration(
    personality_config=personality,
    motivational_bias_config=motivation,
    emotional_profile_config=emotion,
    learning_module_config=learning_config
)

# Define a role
researcher_role = Role(
    name="AI Research Collaborator for {domain}", # Placeholder in role name
    profile="An AI assistant designed to help with scientific research and hypothesis generation in {domain}.",
    skills_focus=["Data_Analysis", "Literature_Review", "{custom_skill}"],
    knowledge_domains_active=["AI_Ethics", "Astrophysics", "{domain}"],
    cognitive_module_configuration=cognitive_config,
    role_specific_rules=["Always cite sources.", "Prioritize peer-reviewed literature for {domain} research."]
)

# Define main prompt sections
system_rules = SystemRules(language="en-UK", output_format="Detailed Markdown Report")
requirements = Requirements(
    goal="Collaboratively write a research paper on {topic}.",
    background_context="The paper is for the International Conference on AGI. Previous work by {user_name} on {user_expertise_area} is relevant.",
    constraints_and_boundaries=["Max 10 pages.", "Focus on novel approaches."],
    success_metrics=["Clarity of arguments.", "Novelty of contribution.", "User_satisfaction_score > 0.9"]
)
users = UsersInteractors(type="Human Researcher", profile="Expert in {user_expertise_area}, novice in AGI.")

executors = Executors(role=researcher_role)

workflow_steps = [
    WorkflowStep(name="Initial Brainstorming", action_directive="Generate 5 potential sub-topics for {topic} related to {domain}."),
    WorkflowStep(name="Literature Review", action_directive="Summarize 3 key papers for the chosen sub-topic.")
]
workflow = Workflow(steps=workflow_steps)

dev_scaffolding = DevelopmentalScaffolding(
    current_developmental_goal="Improve hypothesis generation skills (PiaSapling Stage 3) in the context of {domain}.",
    scaffolding_techniques_employed=["Example-based learning", "ZPD_Hinting_Allowed"]
)

cbt_training = CBTAutoTraining(
    training_scenario="Simulate generating a hypothesis for a known problem in {domain} and critique it.",
    self_critique_focus=["Logical Soundness", "Novelty", "Testability"]
)

# Create the main prompt object
prompt_template = PiaAGIPrompt(
    target_agi="PiaAGI_SciDev_Instance_002",
    developmental_stage_target="PiaSapling",
    author="{user_name}",
    version="1.1.0",
    date="2024-11-25",
    objective="To configure and guide PiaAGI for a collaborative research paper writing task on {topic}, focusing on {custom_skill} development within the {domain} field.",
    system_rules=system_rules,
    requirements=requirements,
    users_interactors=users,
    executors=executors,
    workflow_or_curriculum_phase=workflow,
    developmental_scaffolding_context=dev_scaffolding,
    cbt_autotraining_protocol=cbt_training,
    initiate_interaction="PiaAGI, let's begin our work on the research paper about {topic} in {domain}. Please start with the Initial Brainstorming phase."
)

# 2. Define placeholders and their values
placeholder_data = {
    "domain": "Quantum Physics",
    "topic": "Ethical Implications of Quantum Entanglement in AI",
    "user_name": "Dr. Quantum",
    "user_expertise_area": "Quantum Mechanics",
    "custom_skill": "Quantum_Ethics_Reasoning",
    "task_priority": "0.95", # for MotivationalBias
    "neuro_level": "0.15" # for PersonalityConfig
}

# 3. Fill placeholders
# The fill_placeholders method modifies the object in-place
prompt_template.fill_placeholders(placeholder_data)

# 4. Render the prompt to Markdown
markdown_output = prompt_template.render()

# Output the Markdown
print("\n--- PiaAGI Prompt MVP Output ---\n")
print(markdown_output)

# Example of how to access a filled value (demonstrative)
print("\n--- Example of accessing a filled value ---")
if prompt_template.requirements:
    print(f"Filled Goal: {prompt_template.requirements.goal}")
if prompt_template.executors and prompt_template.executors.role:
    print(f"Filled Role Name: {prompt_template.executors.role.name}")
    if prompt_template.executors.role.cognitive_module_configuration and \
       prompt_template.executors.role.cognitive_module_configuration.motivational_bias_config:
        print(f"Filled Motivational Bias: {prompt_template.executors.role.cognitive_module_configuration.motivational_bias_config.biases}")
    if prompt_template.executors.role.cognitive_module_configuration and \
       prompt_template.executors.role.cognitive_module_configuration.personality_config:
        print(f"Filled Personality Openness: {prompt_template.executors.role.cognitive_module_configuration.personality_config.ocean_openness}")
        print(f"Filled Personality Neuroticism: {prompt_template.executors.role.cognitive_module_configuration.personality_config.ocean_neuroticism}")

```

This MVP provides a foundational engine for creating, managing, and utilizing structured PiaAGI prompts. Future development within PiaPES can build upon this by adding features like a GUI for prompt editing, more sophisticated validation, integration with PiaSE for execution, and advanced curriculum management tools.
```
