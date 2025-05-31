<!-- PiaAGI AGI Research Framework Document -->
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

Key classes like `PiaAGIPrompt` and `DevelopmentalCurriculum` also include an optional `version` attribute (e.g., `version="1.0.beta"`) in their constructor, allowing for an internal way to track the version of the data structure itself.

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


## Saving and Loading Prompt Templates (JSON Format)

The Prompt Engine MVP includes functionality to save any prompt element (derived from `BaseElement`, including `PiaAGIPrompt` and `DevelopmentalCurriculum`) as a **JSON template** and load it back into its corresponding Python object. This method is recommended for reliable serialization and deserialization, ensuring that the object structure can be perfectly reconstructed.

The core functions for this (using JSON format) are:
*   `save_template(element: BaseElement, filepath: str)`: Serializes the provided prompt `element` into a JSON string and saves it to the specified `filepath`.
*   `load_template(filepath: str) -> Optional[BaseElement]`: Loads a JSON string from the given `filepath` and deserializes it back into the appropriate Python prompt object structure.

These functions use a custom JSON encoder and object hook that preserve the type information (`__type__`) of the prompt elements, allowing for accurate reconstruction of the original objects from the JSON data.

### Usage Example for Saving and Loading

Here's how to use the template saving and loading features:

```python
from prompt_engine_mvp import (
    PiaAGIPrompt, SystemRules, Requirements, UsersInteractors, Executors, Role,
    CognitiveModuleConfiguration, PersonalityConfig, MotivationalBias, EmotionalProfile, LearningModuleConfig,
    save_template, load_template # Import the new functions
)

# 1. Create or obtain a PiaAGIPrompt object (or any BaseElement derivative)
# For this example, let's create a relatively simple prompt
original_prompt = PiaAGIPrompt(
    author="Template Demo User",
    version="0.1.0",
    objective="A simple prompt to demonstrate save and load functionality.",
    system_rules=SystemRules(language="en"),
    requirements=Requirements(goal="Test template saving and loading."),
    initiate_interaction="Hello PiaAGI, is this template loaded correctly?"
)

# (Optional) You can fill placeholders if your template uses them before saving
# placeholder_data = {"some_key": "some_value"}
# original_prompt.fill_placeholders(placeholder_data)

# 2. Define a filepath for your template
template_filepath = "my_simple_template.json"

# 3. Save the prompt object as a template
try:
    save_template(original_prompt, template_filepath)
    print(f"Prompt template saved to: {template_filepath}")
except Exception as e:
    print(f"Error saving template: {e}")

# 4. Load the prompt object from the template file
loaded_prompt = None
try:
    loaded_prompt = load_template(template_filepath)
    if loaded_prompt:
        print(f"Prompt template loaded successfully from: {template_filepath}")
    else:
        print(f"Failed to load template from: {template_filepath}")
except Exception as e:
    print(f"Error loading template: {e}")

# 5. Use the loaded prompt object
if loaded_prompt and isinstance(loaded_prompt, PiaAGIPrompt):
    print("\n--- Rendered Loaded Prompt ---")
    print(loaded_prompt.render())

    # You can also access its attributes directly
    print(f"\nObjective of loaded prompt: {loaded_prompt.objective}")
    if loaded_prompt.requirements:
        print(f"Goal of loaded prompt: {loaded_prompt.requirements.goal}")

    # Verify (optional, for testing)
    assert loaded_prompt.objective == original_prompt.objective
    if loaded_prompt.requirements and original_prompt.requirements:
        assert loaded_prompt.requirements.goal == original_prompt.requirements.goal
    print("\nVerification: Loaded prompt content matches original (checked objective and goal).")

elif isinstance(loaded_prompt, BaseElement): # If it was some other BaseElement
    print("\n--- Loaded Element (Not PiaAGIPrompt) ---")
    # Access attributes common to BaseElement or specific to its type if known
    # For example, if you saved a Role object:
    # if isinstance(loaded_prompt, Role):
    # print(f"Loaded Role Name: {loaded_prompt.name}")
    pass

```

This functionality is crucial for building a library of reusable prompt components and for managing complex prompt configurations effectively.

**Note on Version Control:** While the internal `version` attribute helps track versions within the data, it is highly recommended to use an external version control system like **Git** to manage your `.json` template files. Since these files are text-based (JSON), Git can efficiently track changes, manage branches for experiments, and facilitate collaboration.


## Developmental Curriculum Designer

To support the structured development of PiaAGI agents, the prompt engine includes classes for designing developmental curricula. This allows for sequencing multiple `PiaAGIPrompt` templates to guide an agent's learning and maturation progressively.

The core classes for this are:

*   **`CurriculumStep(BaseElement)`:** Represents a single phase or step within a larger curriculum.
    *   `name: str`: Name of the curriculum step (e.g., "Introduction to Object Permanence").
    *   `order: int`: The sequence number for this step. Steps in a curriculum are sorted by this value.
    *   `prompt_reference: str`: A filepath pointing to a saved `PiaAGIPrompt` JSON template that defines the agent's configuration and task for this step.
    *   `conditions: Optional[str]`: Descriptive text outlining prerequisites for starting this step (e.g., "Agent has successfully completed 'Basic Interaction Module'", "Developmental Stage: PiaSeedling_LV2").
    *   `notes: Optional[str]`: Additional notes or observations for this step.

*   **`DevelopmentalCurriculum(BaseElement)`:** Represents the overall curriculum.
    *   `name: str`: Name of the curriculum (e.g., "Early Cognitive Development").
    *   `description: str`: A summary of the curriculum's objectives.
    *   `target_developmental_stage: str`: The overall developmental progression targeted by this curriculum (e.g., "PiaSeedling to PiaSprout").
    *   `steps: List[CurriculumStep]`: An ordered list of `CurriculumStep` objects.
    *   `author: Optional[str]`: Creator of the curriculum.
    *   `version: Optional[str]`: Version of the curriculum.
    *   It includes an `add_step(step: CurriculumStep)` method to add steps (which are then automatically sorted by their `order`).
    *   Its `fill_placeholders` method will also fill placeholders in the attributes of its contained steps.

Both `CurriculumStep` and `DevelopmentalCurriculum` objects can be saved and loaded using the `save_template()` and `load_template()` functions, just like `PiaAGIPrompt` objects, allowing entire curricula to be stored and shared as JSON files.

### Usage Example for Developmental Curriculum

```python
from prompt_engine_mvp import (
    PiaAGIPrompt, Requirements, CurriculumStep, DevelopmentalCurriculum,
    save_template, load_template # Make sure PiaAGIPrompt and Requirements are imported for the example prompts
)

# 1. Create and save prompt templates for each curriculum step
prompt_content_step1 = PiaAGIPrompt(
    author="CurriculumDev", version="1.0",
    objective="Step 1: Introduce basic concept '{concept_name}'.",
    requirements=Requirements(goal="Agent should identify '{concept_name}' in 3 out of 5 trials."),
    initiate_interaction="Let's learn about '{concept_name}'. What is it?"
)
prompt_filepath_step1 = "curriculum_prompt_s1.json"
save_template(prompt_content_step1, prompt_filepath_step1)
print(f"Saved prompt for Step 1 to: {prompt_filepath_step1}")

prompt_content_step2 = PiaAGIPrompt(
    author="CurriculumDev", version="1.0",
    objective="Step 2: Apply '{concept_name}' in a new context.",
    requirements=Requirements(goal="Agent should use '{concept_name}' to solve a simple puzzle."),
    initiate_interaction="Now, let's use '{concept_name}' to figure this out."
)
prompt_filepath_step2 = "curriculum_prompt_s2.json"
save_template(prompt_content_step2, prompt_filepath_step2)
print(f"Saved prompt for Step 2 to: {prompt_filepath_step2}")

# 2. Create CurriculumStep objects
step1 = CurriculumStep(
    name="Introduction to {main_topic}",
    order=1,
    prompt_reference=prompt_filepath_step1,
    conditions="Agent is initialized and responsive.",
    notes="Focus on core definition of {main_topic}."
)

step2 = CurriculumStep(
    name="Application of {main_topic}",
    order=2,
    prompt_reference=prompt_filepath_step2,
    conditions="Successful completion of 'Introduction to {main_topic}'. Agent demonstrates understanding.",
    notes="Observe problem-solving approach using {main_topic}."
)

# 3. Create the DevelopmentalCurriculum
learning_curriculum = DevelopmentalCurriculum(
    name="Learning about {main_topic_full}",
    description="A two-step curriculum to introduce and apply the concept of {main_topic_full}.",
    target_developmental_stage="PiaSeedling (Module 1)",
    author="Dr. Developer",
    version="1.0.0"
)

# 4. Add steps to the curriculum
learning_curriculum.add_step(step1)
learning_curriculum.add_step(step2) # Added in order, but add_step also sorts

# 5. Fill placeholders for the curriculum and its steps
# These placeholders can be in curriculum attributes or step attributes.
# Placeholders within the referenced prompts (prompt_content_step1, etc.) need separate filling
# when the prompt itself is loaded and used for a specific session.
curriculum_placeholders = {
    "main_topic": "Color Recognition",
    "main_topic_full": "Color Recognition and Application",
    "concept_name": "the color Blue" # This will fill placeholders in the prompt files when they are loaded and filled
}
learning_curriculum.fill_placeholders(curriculum_placeholders)
# Note: To fill placeholders in the actual prompt files referenced by steps,
# you would typically load the prompt (e.g., PiaAGIPrompt loaded_p = load_template(step.prompt_reference)),
# then call loaded_p.fill_placeholders(data_for_prompt), before using it.

# 6. Render the curriculum to Markdown
print("\n--- Rendered Developmental Curriculum ---")
rendered_curriculum = learning_curriculum.render()
print(rendered_curriculum)

# 7. Save the entire curriculum
curriculum_filepath = "my_learning_curriculum.json"
save_template(learning_curriculum, curriculum_filepath)
print(f"\nDevelopmental curriculum saved to: {curriculum_filepath}")

# 8. Load the curriculum back
loaded_curriculum = load_template(curriculum_filepath)
if loaded_curriculum and isinstance(loaded_curriculum, DevelopmentalCurriculum):
    print(f"Developmental curriculum loaded successfully from: {curriculum_filepath}")
    # Further verify by rendering or checking attributes
    # print(loaded_curriculum.render())
    assert loaded_curriculum.name == "Learning about Color Recognition and Application"
    assert len(loaded_curriculum.steps) == 2
    assert loaded_curriculum.steps[0].name == "Introduction to Color Recognition"
    print("SUCCESS: Loaded curriculum passes basic checks.")
else:
    print("ERROR: Failed to load or validate the curriculum from file.")

```
This structured approach to curriculum design is vital for guiding PiaAGI agents through complex learning pathways and for conducting systematic research into AGI development.


## Exporting to Markdown

For human readability, documentation, or sharing in a non-JSON format, prompt elements can be exported to Markdown.

The function for this is:
*   `export_to_markdown(element: BaseElement, filepath: str)`: Calls the `render()` method of the provided `element` (which can be a `PiaAGIPrompt`, `DevelopmentalCurriculum`, or any other `BaseElement` derivative) and writes the resulting Markdown string to the specified `filepath`.

### Usage Example for Markdown Export

```python
from prompt_engine_mvp import (
    PiaAGIPrompt, Requirements, DevelopmentalCurriculum, CurriculumStep,
    save_template, load_template, export_to_markdown # Import export_to_markdown
)

# Assume 'learning_curriculum' is a DevelopmentalCurriculum object from the previous example
# and 'original_prompt' is a PiaAGIPrompt object

# Exporting a PiaAGIPrompt object to Markdown
# Create a simple prompt for demonstration if not reusing 'original_prompt'
my_prompt_for_md = PiaAGIPrompt(objective="Prompt for Markdown export demo.", version="1.0-md")
export_to_markdown(my_prompt_for_md, "my_prompt_export.md")
print(f"Exported PiaAGIPrompt to my_prompt_export.md")

# Exporting a DevelopmentalCurriculum object to Markdown
# Ensure 'learning_curriculum' exists from prior examples, or create a simple one:
# Example:
# simple_step = CurriculumStep(name="MD Export Step", order=1, prompt_reference="N/A")
# my_curriculum_for_md = DevelopmentalCurriculum(name="MD Export Curriculum", description="Demo curriculum.", \
# target_developmental_stage="Test", steps=[simple_step], version="1.0-md-curr")
# if 'learning_curriculum' in locals(): # Check if it exists from other examples
#    export_to_markdown(learning_curriculum, "my_curriculum_export.md")
#    print(f"Exported DevelopmentalCurriculum to my_curriculum_export.md")
# else:
#    export_to_markdown(my_curriculum_for_md, "my_curriculum_export.md")
#    print(f"Exported simple DevelopmentalCurriculum to my_curriculum_export.md")

# (Using the 'loaded_prompt' and 'loaded_curriculum' from previous examples if available)
if 'loaded_prompt' in locals() and loaded_prompt:
    export_to_markdown(loaded_prompt, "loaded_prompt_from_json_export.md")
    print(f"Exported previously loaded PiaAGIPrompt to loaded_prompt_from_json_export.md")

if 'loaded_curriculum' in locals() and loaded_curriculum:
    export_to_markdown(loaded_curriculum, "loaded_curriculum_from_json_export.md")
    print(f"Exported previously loaded DevelopmentalCurriculum to loaded_curriculum_from_json_export.md")

```

**Important Considerations for Markdown Export:**
*   **One-Way Export:** Exporting to Markdown is primarily for human consumption or for use in documentation systems. The current MVP **does not support importing** a prompt structure back from a Markdown file.
*   **Data Integrity:** For saving and reliably reloading prompt objects with full data integrity, always use the `save_template()` (JSON) and `load_template()` (JSON) functions.

---
Return to [PiaAGI Core Document](../../PiaAGI.md) | [Project README](../../README.md)
