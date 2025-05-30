import textwrap
from typing import Dict, List, Optional, Any, Union
import json

class BaseElement:
    """Base class for all prompt elements to handle placeholder filling."""
    def _fill_placeholders_str(self, text: Optional[str], data: Dict[str, str]) -> Optional[str]:
        if text is None:
            return None
        for key, value in data.items():
            text = text.replace(f"{{{key}}}", str(value))
        return text

    def _fill_placeholders_list(self, items: Optional[List[str]], data: Dict[str, str]) -> Optional[List[str]]:
        if items is None:
            return None
        return [self._fill_placeholders_str(item, data) for item in items if item is not None]

    def _fill_placeholders_dict(self, items: Optional[Dict[str, Any]], data: Dict[str, str]) -> Optional[Dict[str, Any]]:
        if items is None:
            return None
        new_dict = {}
        for k, v in items.items():
            if isinstance(v, str):
                new_dict[k] = self._fill_placeholders_str(v, data)
            elif isinstance(v, list):
                new_dict[k] = self._fill_placeholders_list(v, data) # type: ignore
            elif isinstance(v, dict):
                new_dict[k] = self._fill_placeholders_dict(v, data)
            else:
                new_dict[k] = v # For non-string/list/dict values, like numbers or booleans
        return new_dict
        
    def fill_placeholders(self, data: Dict[str, str]):
        """Recursively fills placeholders in the element and its children."""
        for attr_name, attr_value in self.__dict__.items():
            if isinstance(attr_value, str):
                setattr(self, attr_name, self._fill_placeholders_str(attr_value, data))
            elif isinstance(attr_value, list) and all(isinstance(item, str) for item in attr_value):
                setattr(self, attr_name, self._fill_placeholders_list(attr_value, data))
            elif isinstance(attr_value, dict):
                setattr(self, attr_name, self._fill_placeholders_dict(attr_value, data))
            elif isinstance(attr_value, BaseElement):
                attr_value.fill_placeholders(data)
            elif isinstance(attr_value, list) and all(isinstance(item, BaseElement) for item in attr_value):
                for item in attr_value:
                    item.fill_placeholders(data)
        return self

    def _render_value(self, value: Any, indent_level: int) -> str:
        indent = "    " * indent_level
        if value is None:
            return ""
        if isinstance(value, list):
            if not value: return ""
            rendered_list = ""
            for item in value:
                if isinstance(item, BaseElement):
                    rendered_list += item.render(indent_level) # Children elements handle their own indent
                elif isinstance(item, str): # Simple string list
                    rendered_list += f"{indent}- {item}\n"
                else: # Other types in list
                    rendered_list += f"{indent}- {str(item)}\n"
            return rendered_list
        elif isinstance(value, dict):
            if not value: return ""
            rendered_dict = ""
            for k, v in value.items():
                if isinstance(v, BaseElement):
                    rendered_dict += f"{indent}{k}:\n"
                    rendered_dict += v.render(indent_level + 1)
                elif isinstance(v, (str, int, float, bool)):
                     rendered_dict += f"{indent}{k}: {v}\n"
                elif v is None:
                    pass # Skip None values in dict
                else: # Fallback for other types
                    rendered_dict += f"{indent}{k}: {str(v)}\n"
            return rendered_dict
        elif isinstance(value, BaseElement):
            return value.render(indent_level) 
        else: # Primitives like str, int, bool
            return f"{indent}{value}\n"


    def render(self, indent_level: int = 0) -> str:
        """Renders the element to Markdown, handling None values gracefully."""
        output = ""
        indent = "    " * indent_level
        
        # Special handling for class name as header if it's not a sub-element being rendered by a parent
        class_name = self.__class__.__name__
        # Avoid redundant headers if a parent is already rendering this element under its attribute name
        if indent_level == 0 or not any(isinstance(getattr(self, attr, None), type(self)) for attr in self.__dict__):
             if class_name not in ["PiaAGIPrompt", "SystemRules", "Requirements", "Users", "Executors", "Role", "Workflow", "RoleDevelopment", "CBTAutoTraining", "DevelopmentalScaffolding", "CognitiveModuleConfiguration", "PersonalityConfig", "MotivationalBias", "EmotionalProfile"]:
                pass # Don't print generic BaseElement class name or other structural classes if they are top-level
             elif class_name != "PiaAGIPrompt": # PiaAGIPrompt is the root, no header for it.
                output += f"{indent}# {class_name.replace('_', ' ')}\n"


        for attr_name, attr_value in self.__dict__.items():
            if attr_value is None or (isinstance(attr_value, (list, dict)) and not attr_value):
                continue

            formatted_attr_name = attr_name.replace('_', ' ').title()
            
            if isinstance(attr_value, BaseElement):
                # Render child BaseElement, it will handle its own header if necessary
                output += f"{indent}## {formatted_attr_name}\n"
                rendered_child = attr_value.render(indent_level + 1)
                if rendered_child.strip(): # Add only if child has content
                     output += rendered_child
            elif isinstance(attr_value, list) and all(isinstance(item, BaseElement) for item in attr_value):
                output += f"{indent}## {formatted_attr_name}\n"
                for item in attr_value:
                    rendered_item = item.render(indent_level + 1)
                    if rendered_item.strip():
                        output += rendered_item
            elif isinstance(attr_value, dict):
                output += f"{indent}## {formatted_attr_name}\n"
                rendered_dict_items = ""
                for k, v in attr_value.items():
                    key_str = str(k).replace('_', ' ').title()
                    if isinstance(v, str) and v.strip():
                         rendered_dict_items += f"{indent}    - **{key_str}:** {v}\n"
                    elif isinstance(v, (int, float, bool)):
                         rendered_dict_items += f"{indent}    - **{key_str}:** {str(v)}\n"
                if rendered_dict_items.strip():
                    output += rendered_dict_items
            elif isinstance(attr_value, list):
                output += f"{indent}## {formatted_attr_name}\n"
                rendered_list_items = ""
                for item_val in attr_value:
                    if isinstance(item_val, str) and item_val.strip():
                        rendered_list_items += f"{indent}    - {item_val}\n"
                if rendered_list_items.strip():
                    output += rendered_list_items
            elif isinstance(attr_value, (str, int, float, bool)) and str(attr_value).strip():
                output += f"{indent}## {formatted_attr_name}\n{indent}    {attr_value}\n"
        return output

# --- Core PiaAGI Prompt Structure Elements ---

class SystemRules(BaseElement):
    def __init__(self,
                 syntax: Optional[str] = "Markdown for general interaction, YAML/JSON for specific config blocks if used",
                 language: Optional[str] = "English",
                 output_format: Optional[str] = "Natural language",
                 logging_level: Optional[str] = "Brief",
                 piaagi_interpretation_mode: Optional[str] = "Execute_Immediate"):
        self.syntax = syntax
        self.language = language
        self.output_format = output_format
        self.logging_level = logging_level
        self.piaagi_interpretation_mode = piaagi_interpretation_mode

class Requirements(BaseElement):
    def __init__(self,
                 goal: Optional[str] = None,
                 background_context: Optional[str] = None,
                 constraints_and_boundaries: Optional[List[str]] = None,
                 success_metrics: Optional[List[str]] = None):
        self.goal = goal
        self.background_context = background_context
        self.constraints_and_boundaries = constraints_and_boundaries if constraints_and_boundaries else []
        self.success_metrics = success_metrics if success_metrics else []

class UsersInteractors(BaseElement): # Renamed from Users to match Appendix
    def __init__(self,
                 type: Optional[str] = None,
                 profile: Optional[str] = None,
                 interaction_history_summary: Optional[str] = None):
        self.type = type
        self.profile = profile
        self.interaction_history_summary = interaction_history_summary

# --- Cognitive Configuration Sub-Elements ---
class PersonalityConfig(BaseElement):
    def __init__(self,
                 ocean_openness: Optional[float] = None,
                 ocean_conscientiousness: Optional[float] = None,
                 ocean_extraversion: Optional[float] = None,
                 ocean_agreeableness: Optional[float] = None,
                 ocean_neuroticism: Optional[float] = None):
        self.ocean_openness = ocean_openness
        self.ocean_conscientiousness = ocean_conscientiousness
        self.ocean_extraversion = ocean_extraversion
        self.ocean_agreeableness = ocean_agreeableness
        self.ocean_neuroticism = ocean_neuroticism

class MotivationalBias(BaseElement):
    def __init__(self, biases: Optional[Dict[str, Union[str, float]]] = None):
        # e.g., {"IntrinsicGoal_Curiosity": "High", "ExtrinsicGoal_TaskCompletion": 0.8}
        self.biases = biases if biases else {}

class EmotionalProfile(BaseElement):
    def __init__(self,
                 baseline_valence: Optional[str] = None,
                 reactivity_to_failure_intensity: Optional[str] = None,
                 empathy_level_target: Optional[str] = None):
        self.baseline_valence = baseline_valence
        self.reactivity_to_failure_intensity = reactivity_to_failure_intensity
        self.empathy_level_target = empathy_level_target
        
class LearningModuleConfig(BaseElement):
    def __init__(self,
                 primary_learning_mode: Optional[str] = None,
                 learning_rate_adaptation: Optional[Union[str, bool]] = None,
                 ethical_heuristic_update_rule: Optional[str] = None):
        self.primary_learning_mode = primary_learning_mode
        self.learning_rate_adaptation = learning_rate_adaptation
        self.ethical_heuristic_update_rule = ethical_heuristic_update_rule

class CognitiveModuleConfiguration(BaseElement):
    def __init__(self,
                 personality_config: Optional[PersonalityConfig] = None,
                 motivational_bias_config: Optional[MotivationalBias] = None,
                 emotional_profile_config: Optional[EmotionalProfile] = None,
                 learning_module_config: Optional[LearningModuleConfig] = None):
        self.personality_config = personality_config if personality_config else PersonalityConfig()
        self.motivational_bias_config = motivational_bias_config if motivational_bias_config else MotivationalBias()
        self.emotional_profile_config = emotional_profile_config if emotional_profile_config else EmotionalProfile()
        self.learning_module_config = learning_module_config if learning_module_config else LearningModuleConfig()

class Role(BaseElement):
    def __init__(self,
                 name: str, # Role Name is now a direct attribute
                 profile: Optional[str] = None,
                 skills_focus: Optional[List[str]] = None,
                 knowledge_domains_active: Optional[List[str]] = None,
                 cognitive_module_configuration: Optional[CognitiveModuleConfiguration] = None,
                 role_specific_rules: Optional[List[str]] = None):
        self.name = name # Added name directly to Role
        self.profile = profile
        self.skills_focus = skills_focus if skills_focus else []
        self.knowledge_domains_active = knowledge_domains_active if knowledge_domains_active else []
        self.cognitive_module_configuration = cognitive_module_configuration if cognitive_module_configuration else CognitiveModuleConfiguration()
        self.role_specific_rules = role_specific_rules if role_specific_rules else []

    def render(self, indent_level: int = 0) -> str:
        # Custom render for Role to include its name prominently
        indent = "    " * indent_level
        output = f"{indent}## Role: {self.name}\n"
        
        # Render other attributes, skipping 'name' as it's already rendered
        for attr_name, attr_value in self.__dict__.items():
            if attr_name == 'name' or attr_value is None or (isinstance(attr_value, (list, dict)) and not attr_value):
                continue

            formatted_attr_name = attr_name.replace('_', ' ').title()
            if isinstance(attr_value, BaseElement):
                output += f"{indent}### {formatted_attr_name}\n" # Use H3 for sub-sections of Role
                rendered_child = attr_value.render(indent_level + 2) # Increase indent for children
                if rendered_child.strip():
                     output += rendered_child
            elif isinstance(attr_value, list) and all(isinstance(item, BaseElement) for item in attr_value):
                # This case might not be typical for Role if complex objects are directly attributes
                output += f"{indent}### {formatted_attr_name}\n"
                for item in attr_value:
                    rendered_item = item.render(indent_level + 2)
                    if rendered_item.strip():
                        output += rendered_item
            elif isinstance(attr_value, dict):
                output += f"{indent}### {formatted_attr_name}\n"
                rendered_dict_items = ""
                for k, v in attr_value.items():
                    key_str = str(k).replace('_', ' ').title()
                    if isinstance(v, str) and v.strip():
                         rendered_dict_items += f"{indent}    - **{key_str}:** {v}\n"
                    elif isinstance(v, (int, float, bool)):
                         rendered_dict_items += f"{indent}    - **{key_str}:** {str(v)}\n"
                if rendered_dict_items.strip():
                    output += rendered_dict_items
            elif isinstance(attr_value, list):
                output += f"{indent}### {formatted_attr_name}\n"
                rendered_list_items = ""
                for item_val in attr_value:
                    if isinstance(item_val, str) and item_val.strip():
                        rendered_list_items += f"{indent}    - {item_val}\n"
                if rendered_list_items.strip():
                    output += rendered_list_items
            elif isinstance(attr_value, (str, int, float, bool)) and str(attr_value).strip():
                 output += f"{indent}### {formatted_attr_name}\n{indent}    {attr_value}\n"
        return output

class Executors(BaseElement):
    def __init__(self, role: Optional[Role] = None): # Simplified to one role for MVP
        self.role = role

class WorkflowStep(BaseElement):
    def __init__(self,
                 name: str,
                 action_directive: Optional[str] = None,
                 module_focus: Optional[List[str]] = None,
                 expected_outcome_internal: Optional[str] = None,
                 expected_output_external: Optional[str] = None):
        self.name = name
        self.action_directive = action_directive
        self.module_focus = module_focus if module_focus else []
        self.expected_outcome_internal = expected_outcome_internal
        self.expected_output_external = expected_output_external

    def render(self, indent_level: int = 0) -> str:
        indent = "    " * indent_level
        output = f"{indent}**{self.name}:**\n"
        if self.action_directive:
            output += f"{indent}    - Action Directive: {self.action_directive}\n"
        if self.module_focus:
            output += f"{indent}    - Module Focus: {', '.join(self.module_focus)}\n"
        if self.expected_outcome_internal:
            output += f"{indent}    - Expected Internal Outcome: {self.expected_outcome_internal}\n"
        if self.expected_output_external:
            output += f"{indent}    - Expected External Output: {self.expected_output_external}\n"
        return output

class Workflow(BaseElement):
    def __init__(self, steps: Optional[List[WorkflowStep]] = None):
        self.steps = steps if steps else []

class DevelopmentalScaffolding(BaseElement):
    def __init__(self,
                 current_developmental_goal: Optional[str] = None,
                 scaffolding_techniques_employed: Optional[List[str]] = None,
                 feedback_level_from_overseer: Optional[str] = None):
        self.current_developmental_goal = current_developmental_goal
        self.scaffolding_techniques_employed = scaffolding_techniques_employed if scaffolding_techniques_employed else []
        self.feedback_level_from_overseer = feedback_level_from_overseer

class CBTAutoTraining(BaseElement): # Simplified for MVP
    def __init__(self,
                 training_scenario: Optional[str] = None,
                 execution_loop: Optional[str] = None, # e.g. "Perform 5 times"
                 self_critique_focus: Optional[List[str]] = None,
                 refinement_mechanism: Optional[str] = None,
                 success_threshold: Optional[str] = None):
        self.training_scenario = training_scenario
        self.execution_loop = execution_loop
        self.self_critique_focus = self_critique_focus if self_critique_focus else []
        self.refinement_mechanism = refinement_mechanism
        self.success_threshold = success_threshold
        
# --- Main Prompt Class ---
class PiaAGIPrompt(BaseElement):
    def __init__(self,
                 target_agi: Optional[str] = None,
                 developmental_stage_target: Optional[str] = None,
                 author: Optional[str] = None,
                 version: Optional[str] = None,
                 date: Optional[str] = None,
                 objective: Optional[str] = None,
                 system_rules: Optional[SystemRules] = None,
                 requirements: Optional[Requirements] = None,
                 users_interactors: Optional[UsersInteractors] = None,
                 executors: Optional[Executors] = None,
                 workflow_or_curriculum_phase: Optional[Workflow] = None, # Named to match Appendix
                 developmental_scaffolding_context: Optional[DevelopmentalScaffolding] = None, # Named to match Appendix
                 cbt_autotraining_protocol: Optional[CBTAutoTraining] = None, # Named to match Appendix
                 initiate_interaction: Optional[str] = None):
        # Metadata
        self.target_agi = target_agi
        self.developmental_stage_target = developmental_stage_target
        self.author = author
        self.version = version
        self.date = date
        self.objective = objective
        
        # Core Sections
        self.system_rules = system_rules if system_rules else SystemRules()
        self.requirements = requirements if requirements else Requirements()
        self.users_interactors = users_interactors if users_interactors else UsersInteractors()
        self.executors = executors if executors else Executors() # Contains Role
        self.workflow_or_curriculum_phase = workflow_or_curriculum_phase if workflow_or_curriculum_phase else Workflow()
        self.developmental_scaffolding_context = developmental_scaffolding_context if developmental_scaffolding_context else DevelopmentalScaffolding()
        self.cbt_autotraining_protocol = cbt_autotraining_protocol if cbt_autotraining_protocol else CBTAutoTraining()
        self.initiate_interaction = initiate_interaction

    def render(self, indent_level: int = 0) -> str:
        """Renders the full prompt to Markdown."""
        output = f"<!--\n"
        if self.target_agi: output += f"  - Target AGI: {self.target_agi}\n"
        if self.developmental_stage_target: output += f"  - Developmental Stage Target: {self.developmental_stage_target}\n"
        if self.author: output += f"  - Author: {self.author}\n"
        if self.version: output += f"  - Version: {self.version}\n"
        if self.date: output += f"  - Date: {self.date}\n"
        if self.objective: output += f"  - Objective: {self.objective}\n"
        output += "-->\n\n"

        # Render each main section
        if self.system_rules:
            output += "# System_Rules\n"
            output += self.system_rules.render(indent_level=1) + "\n" # Indent content under section
        if self.requirements and (self.requirements.goal or self.requirements.background_context or self.requirements.constraints_and_boundaries or self.requirements.success_metrics) :
            output += "# Requirements\n"
            output += self.requirements.render(indent_level=1) + "\n"
        if self.users_interactors and (self.users_interactors.type or self.users_interactors.profile or self.users_interactors.interaction_history_summary):
            output += "# Users_Interactors\n"
            output += self.users_interactors.render(indent_level=1) + "\n"
        if self.executors and self.executors.role:
            output += "# Executors\n"
            output += self.executors.render(indent_level=1) + "\n" # Executor itself renders its Role
        if self.workflow_or_curriculum_phase and self.workflow_or_curriculum_phase.steps:
            output += "# Workflow_Or_Curriculum_Phase\n"
            output += self.workflow_or_curriculum_phase.render(indent_level=1) + "\n"
        if self.developmental_scaffolding_context and (self.developmental_scaffolding_context.current_developmental_goal or self.developmental_scaffolding_context.scaffolding_techniques_employed or self.developmental_scaffolding_context.feedback_level_from_overseer):
            output += "# Developmental_Scaffolding_Context\n"
            output += self.developmental_scaffolding_context.render(indent_level=1) + "\n"
        if self.cbt_autotraining_protocol and (self.cbt_autotraining_protocol.training_scenario or self.cbt_autotraining_protocol.self_critique_focus): # Check if it has content
            output += "# CBT_AutoTraining_Protocol\n"
            output += self.cbt_autotraining_protocol.render(indent_level=1) + "\n"
        if self.initiate_interaction:
            output += "# Initiate_Interaction\n"
            output += f"    {self.initiate_interaction}\n"
            
        return output.strip()
# --- Export to Markdown Function ---

def export_to_markdown(element: BaseElement, filepath: str):
    """
    Exports a PiaAGI prompt element (or any BaseElement derivative) to a Markdown file.
    """
    if not isinstance(element, BaseElement):
        print(f"Error: Element to export must be a BaseElement derivative. Got: {type(element)}")
        return

    markdown_string = element.render()
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_string)
        print(f"Element successfully exported to Markdown: {filepath}")
    except IOError as e:
        print(f"Error writing Markdown file to {filepath}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during Markdown export to {filepath}: {e}")

# --- End of Export to Markdown Function ---

if __name__ == '__main__':
    # Simple Usage Example
    
    # 1. Define a prompt template structure
    # Define cognitive configurations
    personality = PersonalityConfig(ocean_openness=0.8, ocean_conscientiousness=0.7)
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
        name="AI Research Collaborator",
        profile="An AI assistant designed to help with scientific research and hypothesis generation.",
        skills_focus=["Data_Analysis", "Literature_Review", "{custom_skill}"],
        knowledge_domains_active=["AI_Ethics", "Astrophysics"],
        cognitive_module_configuration=cognitive_config,
        role_specific_rules=["Always cite sources.", "Prioritize peer-reviewed literature."]
    )

    # Define main prompt sections
    system_rules = SystemRules(language="en-UK", output_format="Detailed Markdown Report")
    requirements = Requirements(
        goal="Collaboratively write a research paper on {topic}.",
        background_context="The paper is for the International Conference on AGI.",
        constraints_and_boundaries=["Max 10 pages.", "Focus on novel approaches."],
        success_metrics=["Clarity of arguments.", "Novelty of contribution.", "User_satisfaction_score > 0.9"]
    )
    users = UsersInteractors(type="Human Researcher", profile="Expert in {user_expertise_area}, novice in AGI.")
    
    executors = Executors(role=researcher_role)

    workflow_steps = [
        WorkflowStep(name="Initial Brainstorming", action_directive="Generate 5 potential sub-topics for {topic}."),
        WorkflowStep(name="Literature Review", action_directive="Summarize 3 key papers for the chosen sub-topic.")
    ]
    workflow = Workflow(steps=workflow_steps)
    
    dev_scaffolding = DevelopmentalScaffolding(
        current_developmental_goal="Improve hypothesis generation skills (PiaSapling Stage 3).",
        scaffolding_techniques_employed=["Example-based learning", "ZPD_Hinting_Allowed"]
    )

    # Create the main prompt object
    prompt_template = PiaAGIPrompt(
        target_agi="PiaAGI_SciDev_Instance_001",
        developmental_stage_target="PiaSapling",
        author="Dr. Example",
        version="1.0.0-maintest", # Specific version for testing
        date="2024-11-24",
        objective="To configure and guide PiaAGI for a collaborative research paper writing task on {topic}, focusing on {custom_skill} development.",
        system_rules=system_rules,
        requirements=requirements,
        users_interactors=users,
        executors=executors,
        workflow_or_curriculum_phase=workflow,
        developmental_scaffolding_context=dev_scaffolding,
        initiate_interaction="PiaAGI, let's begin our work on the research paper about {topic}. Please start with the Initial Brainstorming phase."
    )

    # 2. Define placeholders and their values
    placeholder_data = {
        "topic": "Ethical Implications of Self-Improving AGI",
        "user_expertise_area": "Philosophy of Mind",
        "custom_skill": "Ethical_Reasoning_Analysis",
        "task_priority": "0.9" # for MotivationalBias
    }

    # 3. Fill placeholders
    filled_prompt = prompt_template.fill_placeholders(placeholder_data)

    # 4. Render the prompt to Markdown
    markdown_output = filled_prompt.render()

    print("\n--- PiaAGI Prompt MVP Output ---\n")
    print(markdown_output)

    # Example of how to access a filled value (demonstrative)
    print("\n--- Example of accessing a filled value ---")
    if filled_prompt.requirements:
        print(f"Filled Goal: {filled_prompt.requirements.goal}")
    if filled_prompt.executors and filled_prompt.executors.role and \
       filled_prompt.executors.role.cognitive_module_configuration and \
       filled_prompt.executors.role.cognitive_module_configuration.motivational_bias_config:
        mb_biases = filled_prompt.executors.role.cognitive_module_configuration.motivational_bias_config.biases
        print(f"Filled Motivational Bias: {mb_biases}")

    print("\n--- Testing Template Save/Load ---")
    template_filepath = "prompt_template_test.json"

    # Save the filled prompt as a template
    save_template(filled_prompt, template_filepath)
    print(f"Prompt saved to {template_filepath}")

    # Load the prompt from the template file
    loaded_prompt = load_template(template_filepath)
    print(f"Prompt loaded from {template_filepath}")

    # Verify by rendering the loaded prompt or checking specific fields
    if loaded_prompt:
        print("\n--- Rendered Loaded Prompt ---")
        print(loaded_prompt.render())
        
        # Example check
        if loaded_prompt.requirements and filled_prompt.requirements:
            assert loaded_prompt.requirements.goal == filled_prompt.requirements.goal
            print("\nSUCCESS: Loaded prompt goal matches original prompt goal.")
        
        assert loaded_prompt.version == filled_prompt.version # Check version attribute
        print(f"SUCCESS: Loaded prompt version '{loaded_prompt.version}' matches original prompt version.")

        if loaded_prompt.executors and loaded_prompt.executors.role and \
           loaded_prompt.executors.role.cognitive_module_configuration and \
           loaded_prompt.executors.role.cognitive_module_configuration.motivational_bias_config and \
           filled_prompt.executors and filled_prompt.executors.role and \
           filled_prompt.executors.role.cognitive_module_configuration and \
           filled_prompt.executors.role.cognitive_module_configuration.motivational_bias_config:
            
            loaded_biases = loaded_prompt.executors.role.cognitive_module_configuration.motivational_bias_config.biases
            original_biases = filled_prompt.executors.role.cognitive_module_configuration.motivational_bias_config.biases
            assert loaded_biases == original_biases
            print("SUCCESS: Loaded motivational biases match original.")

    else:
        print("ERROR: Failed to load prompt from template.")

    print("\n\n--- Testing Developmental Curriculum ---")

    # 1. Create and save a couple of simple PiaAGIPrompt templates
    prompt_step1_content = PiaAGIPrompt(
        author="CurriculumDesigner",
        version="1.0.1-step1", # Specific version for step prompt
        objective="Objective for Step 1: Introduce {concept_A}",
        initiate_interaction="Explain {concept_A} in simple terms."
    )
    prompt_step1_filepath = "prompt_curriculum_step1.json"
    save_template(prompt_step1_content, prompt_step1_filepath)
    print(f"Saved Step 1 prompt template to {prompt_step1_filepath}")

    prompt_step2_content = PiaAGIPrompt(
        author="CurriculumDesigner",
        version="1.0.2-step2", # Specific version for step prompt
        objective="Objective for Step 2: Elaborate on {concept_A} and introduce {concept_B}",
        initiate_interaction="Now, how does {concept_A} relate to {concept_B}?"
    )
    prompt_step2_filepath = "prompt_curriculum_step2.json"
    save_template(prompt_step2_content, prompt_step2_filepath)
    print(f"Saved Step 2 prompt template to {prompt_step2_filepath}")

    # 2. Create CurriculumSteps
    step1 = CurriculumStep(
        name="Introduction to {concept_A_name}",
        order=1,
        prompt_reference=prompt_step1_filepath,
        conditions="Agent is at PiaSeedling stage.",
        notes="Focus on basic understanding of {concept_A_name}."
    )

    step2 = CurriculumStep(
        name="Relating {concept_A_name} to {concept_B_name}",
        order=2,
        prompt_reference=prompt_step2_filepath,
        conditions="Successful completion of Step 1.",
        notes="Encourage agent to find connections."
    )
    
    step0 = CurriculumStep( # To test ordering
        name="Pre-computation of {something_else}",
        order=0,
        prompt_reference="utility_prompt.json", # Assuming this exists or is placeholder
        notes="A utility step for {something_else}"
    )

    # 3. Create DevelopmentalCurriculum
    curriculum = DevelopmentalCurriculum(
        name="Learning {concept_A_name} and {concept_B_name}",
        description="A curriculum to teach an agent about two related concepts, {concept_A_name} and {concept_B_name}, and their connections.",
        target_developmental_stage="PiaSeedling to PiaSprout",
        author="AI Tutor Developer",
        version="0.9.5-curriculumtest" # Specific version for curriculum
    )
    curriculum.add_step(step1)
    curriculum.add_step(step2)
    curriculum.add_step(step0) # Added out of order, should be sorted

    # 4. Fill placeholders in the curriculum
    curriculum_placeholders = {
        "concept_A_name": "Abstraction",
        "concept_B_name": "Generalization",
        "concept_A": "the concept of Abstraction", # For prompt_step1_content
        "concept_B": "the concept of Generalization", # For prompt_step2_content
        "something_else": "environment variables"
    }
    curriculum.fill_placeholders(curriculum_placeholders)
    
    # Note: Filling placeholders in prompts referenced by curriculum steps
    # would typically be a separate step when the step is 'activated' or prepared for execution.
    # For example, one might load the prompt_template from step.prompt_reference,
    # fill its placeholders, and then use it.
    # The curriculum's fill_placeholders only affects the curriculum and step attributes themselves.

    # 5. Render the curriculum
    print("\n--- Rendered Curriculum ---")
    rendered_curriculum = curriculum.render()
    print(rendered_curriculum)

    # 6. Save the curriculum
    curriculum_filepath = "developmental_curriculum_test.json"
    save_template(curriculum, curriculum_filepath)
    print(f"\nCurriculum saved to {curriculum_filepath}")

    # 7. Load the curriculum
    loaded_curriculum = load_template(curriculum_filepath)
    print(f"Curriculum loaded from {curriculum_filepath}")

    if loaded_curriculum and isinstance(loaded_curriculum, DevelopmentalCurriculum):
        print("\n--- Rendered Loaded Curriculum ---")
        print(loaded_curriculum.render())

        assert loaded_curriculum.name == "Learning Abstraction and Generalization"
        assert len(loaded_curriculum.steps) == 3
        assert loaded_curriculum.steps[0].name == "Pre-computation of environment variables" # Check order
        assert loaded_curriculum.steps[1].name == "Introduction to Abstraction"
        assert loaded_curriculum.steps[1].prompt_reference == prompt_step1_filepath
        assert loaded_curriculum.steps[2].notes == "Encourage agent to find connections."
        assert loaded_curriculum.version == curriculum.version # Check curriculum version
        print(f"SUCCESS: Loaded curriculum version '{loaded_curriculum.version}' matches original curriculum version.")
        print("SUCCESS: Loaded curriculum passes integrity checks.")
    else:
        print("ERROR: Failed to load or validate the curriculum.")

    # Test Markdown export
    print("\n\n--- Testing Markdown Export ---")
    if loaded_prompt:
        export_to_markdown(loaded_prompt, "loaded_prompt_export.md")
    else:
        print("Skipping Markdown export for prompt_template as it was not loaded.")

    if loaded_curriculum and isinstance(loaded_curriculum, DevelopmentalCurriculum):
        export_to_markdown(loaded_curriculum, "loaded_curriculum_export.md")
    else:
        print("Skipping Markdown export for curriculum as it was not loaded or is not a DevelopmentalCurriculum.")


# --- Template Saving and Loading Functions ---

class PiaAGIEncoder(json.JSONEncoder):
    """Custom JSON encoder for PiaAGI elements."""
    def default(self, obj):
        if isinstance(obj, BaseElement):
            # Create a dictionary that includes the type and all attributes
            data = {'__type__': obj.__class__.__name__}
            data.update(obj.__dict__)
            return data
        return super().default(obj)

def pia_agi_object_hook(dct: Dict[str, Any]) -> Any:
    """Custom object hook for deserializing PiaAGI elements."""
    if '__type__' in dct:
        class_name = dct.pop('__type__')
        cls = globals().get(class_name)
        if cls and issubclass(cls, BaseElement):
            # Create instance without calling __init__ initially
            instance = cls.__new__(cls) 
            
            # For each item in dct, if it's a dictionary that represents a nested custom object,
            # recursively call this hook (or allow json.loads to do it).
            # If it's a list of such dictionaries, process each one.
            processed_dct = {}
            for key, value in dct.items():
                if isinstance(value, dict): # Potentially a nested object
                    processed_dct[key] = pia_agi_object_hook(value)
                elif isinstance(value, list): # Potentially a list of nested objects
                    processed_dct[key] = [pia_agi_object_hook(item) if isinstance(item, dict) else item for item in value]
                else:
                    processed_dct[key] = value
            
            instance.__dict__.update(processed_dct) # Populate attributes
            return instance
    return dct

def save_template(element: BaseElement, filepath: str):
    """
    Saves a PiaAGI prompt element (or any BaseElement derivative) to a JSON file.
    """
    with open(filepath, 'w') as f:
        json.dump(element, f, cls=PiaAGIEncoder, indent=4)

def load_template(filepath: str) -> Optional[BaseElement]:
    """
    Loads a PiaAGI prompt element from a JSON file.
    Returns the deserialized object, or None if an error occurs.
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f, object_hook=pia_agi_object_hook)
        if isinstance(data, BaseElement):
            return data
        # If the root object isn't a BaseElement (e.g. loading a simple dict),
        # this indicates an issue or incorrect file.
        # For this use case, we expect a BaseElement derivative.
        print(f"Warning: Loaded data from {filepath} is not a PiaAGI BaseElement derivative. Type: {type(data)}")
        return None
    except FileNotFoundError:
        print(f"Error: Template file not found at {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {filepath}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while loading template from {filepath}: {e}")
        return None

# --- End of Template Saving and Loading Functions ---


# --- Developmental Curriculum Classes ---

class CurriculumStep(BaseElement):
    """Represents a single step in a developmental curriculum."""
    def __init__(self,
                 name: str,
                 order: int,
                 prompt_reference: str, # Filepath to a PiaAGIPrompt template
                 conditions: Optional[str] = None, # Descriptive conditions
                 notes: Optional[str] = None):
        self.name = name
        self.order = order
        self.prompt_reference = prompt_reference
        self.conditions = conditions
        self.notes = notes

    def render(self, indent_level: int = 0) -> str:
        indent = "    " * indent_level
        output = f"{indent}### Step {self.order}: {self.name}\n"
        output += f"{indent}- **Prompt Template:** {self.prompt_reference}\n"
        if self.conditions:
            output += f"{indent}- **Conditions:** {self.conditions}\n"
        if self.notes:
            output += f"{indent}- **Notes:** {self.notes}\n"
        # Potentially load and render the referenced prompt if needed,
        # but for now, keep it as a reference.
        # Example:
        # try:
        #     referenced_prompt = load_template(self.prompt_reference)
        #     if referenced_prompt:
        #         output += f"{indent}    <details><summary>View Prompt Details</summary>\n"
        #         output += referenced_prompt.render(indent_level + 2)
        #         output += f"{indent}    </details>\n"
        # except Exception as e:
        #     output += f"{indent}    (Could not load/render prompt: {e})\n"
        return output

class DevelopmentalCurriculum(BaseElement):
    """Represents a developmental curriculum composed of multiple steps."""
    def __init__(self,
                 name: str,
                 description: str,
                 target_developmental_stage: str,
                 steps: Optional[List[CurriculumStep]] = None,
                 version: Optional[str] = None,
                 author: Optional[str] = None):
        self.name = name
        self.description = description
        self.target_developmental_stage = target_developmental_stage
        self.steps = steps if steps else []
        self.version = version
        self.author = author
        self.sort_steps()

    def add_step(self, step: CurriculumStep):
        self.steps.append(step)
        self.sort_steps()

    def sort_steps(self):
        self.steps.sort(key=lambda s: s.order)

    def fill_placeholders(self, data: Dict[str, str]):
        """Fills placeholders in the curriculum's attributes and its steps."""
        super().fill_placeholders(data) # Fill placeholders for curriculum's own string attributes
        for step in self.steps:
            step.fill_placeholders(data) # Propagate to each step
        return self

    def render(self, indent_level: int = 0) -> str:
        indent = "    " * indent_level
        output = f"{indent}# Curriculum: {self.name}\n"
        if self.author:
            output += f"{indent}**Author:** {self.author}\n"
        if self.version:
            output += f"{indent}**Version:** {self.version}\n"
        output += f"{indent}**Description:** {self.description}\n"
        output += f"{indent}**Target Developmental Stage:** {self.target_developmental_stage}\n\n"
        
        output += f"{indent}## Curriculum Steps\n"
        if not self.steps:
            output += f"{indent}No steps defined for this curriculum.\n"
        else:
            for step in self.steps:
                output += step.render(indent_level + 1)
        return output

# --- End of Developmental Curriculum Classes ---

```
