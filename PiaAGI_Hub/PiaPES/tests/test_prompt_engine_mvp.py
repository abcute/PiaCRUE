import unittest
import os
import tempfile
import shutil
import json

# Adjust import path based on actual structure if run from different locations
# Assuming PiaAGI_Hub is in PYTHONPATH or tests are run from PiaAGI_Hub's parent dir
from PiaAGI_Hub.PiaPES.prompt_engine_mvp import (
    BaseElement,
    PiaAGIPrompt, SystemRules, Requirements, UsersInteractors, Executors, Role,
    CognitiveModuleConfiguration, PersonalityConfig, MotivationalBias, EmotionalProfile, LearningModuleConfig,
    Workflow, WorkflowStep, DevelopmentalScaffolding, CBTAutoTraining,
    CurriculumStep, DevelopmentalCurriculum,
    save_template, load_template, export_to_markdown
)

# Helper function for deep dictionary comparison
def compare_dicts(d1, d2, path=""):
    """Recursively compare two dictionaries. Returns True if equal, False otherwise."""
    if not isinstance(d1, dict) or not isinstance(d2, dict):
        if d1 == d2:
            return True
        else:
            # print(f"Value mismatch at {path}: {d1} != {d2}")
            return False

    if set(d1.keys()) != set(d2.keys()):
        # print(f"Key mismatch at {path}: {set(d1.keys())} != {set(d2.keys())}")
        return False

    for key in d1:
        new_path = f"{path}.{key}" if path else key
        if not compare_dicts(d1[key], d2[key], new_path):
            return False
    return True


class SimpleElement(BaseElement):
    def __init__(self, name: str, description: Optional[str] = None, items: Optional[list] = None):
        self.name = name
        self.description = description
        self.items = items if items else []

    def render(self, indent_level: int = 0) -> str:
        indent = "    " * indent_level
        output = f"{indent}Name: {self.name}\n"
        if self.description:
            output += f"{indent}Description: {self.description}\n"
        if self.items:
            output += f"{indent}Items:\n"
            for item in self.items:
                output += f"{indent}  - {item}\n"
        return output

class TestBaseElementMVP(unittest.TestCase):
    def test_fill_placeholders_simple_element(self):
        element = SimpleElement(name="Test {object}", description="This is a {quality} test.")
        element.fill_placeholders({"object": "Element", "quality": "good"})
        self.assertEqual(element.name, "Test Element")
        self.assertEqual(element.description, "This is a good test.")

    def test_render_simple_element(self):
        element = SimpleElement(name="Render Test", description="Description here.", items=["item1", "item2"])
        rendered_output = element.render()
        self.assertIn("Name: Render Test", rendered_output)
        self.assertIn("Description: Description here.", rendered_output)
        self.assertIn("  - item1", rendered_output)


class TestPromptEngineMVP(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        # print(f"Test directory created: {self.test_dir}")

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        # print(f"Test directory removed: {self.test_dir}")

    def _create_sample_cognitive_config(self) -> CognitiveModuleConfiguration:
        return CognitiveModuleConfiguration(
            personality_config=PersonalityConfig(ocean_openness=0.7, ocean_conscientiousness="{conscientiousness_level}"),
            motivational_bias_config=MotivationalBias(biases={"curiosity": "{curiosity_level}"}),
            emotional_profile_config=EmotionalProfile(baseline_valence="neutral"),
            learning_module_config=LearningModuleConfig(primary_learning_mode="RL")
        )

    def _create_sample_pia_agi_prompt(self, name_suffix="") -> PiaAGIPrompt:
        cognitive_config = self._create_sample_cognitive_config()
        role = Role(
            name=f"TestRole{name_suffix}",
            profile="A role for testing {purpose}",
            cognitive_module_configuration=cognitive_config
        )
        return PiaAGIPrompt(
            author=f"TestAuthor{name_suffix}",
            version=f"1.0.0{name_suffix}",
            objective=f"Test objective for prompt{name_suffix} with {{{{placeholder}}}}.", # Escaped placeholder
            requirements=Requirements(goal="Test goal: {goal_description}"),
            executors=Executors(role=role),
            initiate_interaction="Start test {test_name}."
        )

    def _create_sample_curriculum(self, name_suffix="") -> DevelopmentalCurriculum:
        # Create and save dummy prompt files for curriculum steps
        prompt1_path = os.path.join(self.test_dir, f"curr_prompt1{name_suffix}.json")
        prompt2_path = os.path.join(self.test_dir, f"curr_prompt2{name_suffix}.json")

        p1 = PiaAGIPrompt(objective="Step 1 objective", version="c1.0")
        p2 = PiaAGIPrompt(objective="Step 2 objective", version="c2.0")
        save_template(p1, prompt1_path)
        save_template(p2, prompt2_path)

        step1 = CurriculumStep(name="Step1{name_suffix}", order=1, prompt_reference=prompt1_path, notes="Notes for {step_note_placeholder}")
        step2 = CurriculumStep(name="Step2{name_suffix}", order=2, prompt_reference=prompt2_path)

        curriculum = DevelopmentalCurriculum(
            name=f"TestCurriculum{name_suffix}",
            description="A curriculum for {curriculum_purpose}",
            target_developmental_stage="TestStage",
            version=f"0.1{name_suffix}",
            author=f"CurriculumAuthor{name_suffix}"
        )
        curriculum.add_step(step1)
        curriculum.add_step(step2)
        return curriculum

    def test_pia_agi_prompt_initialization(self):
        prompt = self._create_sample_pia_agi_prompt("_init")
        self.assertEqual(prompt.author, "TestAuthor_init")
        self.assertEqual(prompt.version, "1.0.0_init")
        self.assertIsNotNone(prompt.requirements)
        self.assertIsNotNone(prompt.executors)
        self.assertIsNotNone(prompt.executors.role)
        self.assertEqual(prompt.executors.role.name, "TestRole_init")

    def test_pia_agi_prompt_fill_placeholders(self):
        prompt = self._create_sample_pia_agi_prompt("_ph")
        placeholders = {
            "placeholder": "actual_value", # For the escaped placeholder in objective
            "goal_description": "achieve placeholder success",
            "purpose": "placeholders",
            "conscientiousness_level": "0.8", # For cognitive config
            "curiosity_level": "high",       # For cognitive config
            "test_name": "placeholder_test"
        }
        prompt.fill_placeholders(placeholders)
        self.assertEqual(prompt.objective, "Test objective for prompt_ph with actual_value.")
        self.assertEqual(prompt.requirements.goal, "Test goal: achieve placeholder success")
        self.assertEqual(prompt.executors.role.profile, "A role for testing placeholders")
        self.assertEqual(prompt.executors.role.cognitive_module_configuration.personality_config.ocean_conscientiousness, "0.8")
        self.assertEqual(prompt.executors.role.cognitive_module_configuration.motivational_bias_config.biases["curiosity"], "high")
        self.assertEqual(prompt.initiate_interaction, "Start test placeholder_test.")

    def test_pia_agi_prompt_render(self):
        prompt = self._create_sample_pia_agi_prompt("_render")
        prompt.fill_placeholders({ # Fill some to make render more complete
            "placeholder": "val", "goal_description": "goal", "purpose": "purpose",
            "conscientiousness_level": "0.5", "curiosity_level": "mid", "test_name": "render_test"
        })
        markdown = prompt.render()
        self.assertIn("TestAuthor_render", markdown) # Author
        self.assertIn("1.0.0_render", markdown)   # Version
        self.assertIn("Test objective for prompt_render with val.", markdown) # Objective
        self.assertIn("Test goal: goal", markdown) # Requirement goal
        self.assertIn("Role: TestRole_render", markdown) # Role name
        self.assertIn("A role for testing purpose", markdown) # Role profile
        self.assertIn("Start test render_test", markdown) # Initiate interaction
        self.assertIn("Ocean Conscientiousness", markdown) # Cognitive Config
        self.assertIn("0.5", markdown) # Cognitive Config value

    def test_pia_agi_prompt_save_and_load_template(self):
        original_prompt = self._create_sample_pia_agi_prompt("_saveload")
        placeholders = {
            "placeholder": "saved_loaded", "goal_description": "save/load goal", "purpose": "save/load",
            "conscientiousness_level": "0.9", "curiosity_level": "very_high", "test_name": "saveload_test"
        }
        original_prompt.fill_placeholders(placeholders)

        filepath = os.path.join(self.test_dir, "prompt_template.json")
        save_template(original_prompt, filepath)
        self.assertTrue(os.path.exists(filepath))

        loaded_prompt = load_template(filepath)
        self.assertIsNotNone(loaded_prompt)
        self.assertIsInstance(loaded_prompt, PiaAGIPrompt)

        # Compare __dict__ for equality (requires careful handling of nested objects)
        # For BaseElement derivatives, their __dict__ should be comparable if attributes are simple types
        # or other BaseElement derivatives.
        self.assertTrue(compare_dicts(original_prompt.__dict__, loaded_prompt.__dict__), "Prompt dictionaries do not match after save/load.")


    def test_pia_agi_prompt_export_to_markdown(self):
        prompt = self._create_sample_pia_agi_prompt("_mdexport")
        prompt.fill_placeholders({
            "placeholder": "md_val", "goal_description": "md_goal", "purpose": "md_purpose",
            "conscientiousness_level": "0.6", "curiosity_level": "low", "test_name": "md_export_test"
        })

        filepath = os.path.join(self.test_dir, "prompt_export.md")
        export_to_markdown(prompt, filepath)
        self.assertTrue(os.path.exists(filepath))

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        expected_render = prompt.render()
        self.assertEqual(content, expected_render)

    def test_cognitive_configs_initialization_render_placeholders(self):
        # Test PersonalityConfig
        pc = PersonalityConfig(ocean_openness=0.1, ocean_neuroticism="{neuro_level}")
        pc.fill_placeholders({"neuro_level": "0.9"})
        self.assertEqual(pc.ocean_neuroticism, "0.9")
        self.assertIn("Ocean Openness", pc.render())
        self.assertIn("0.1", pc.render())

        # Test MotivationalBias
        mb = MotivationalBias(biases={"goal1": "value1", "goal2": "{goal_val}"})
        mb.fill_placeholders({"goal_val": "value2_filled"})
        self.assertEqual(mb.biases["goal2"], "value2_filled")
        self.assertIn("goal1", mb.render().lower()) # Render for dict is specific
        self.assertIn("value1", mb.render())

        # Test EmotionalProfile
        ep = EmotionalProfile(baseline_valence="{valence}", empathy_level_target="High")
        ep.fill_placeholders({"valence": "Positive"})
        self.assertEqual(ep.baseline_valence, "Positive")
        self.assertIn("Positive", ep.render())
        self.assertIn("High", ep.render())

        # Test LearningModuleConfig
        lc = LearningModuleConfig(primary_learning_mode="{mode}", learning_rate_adaptation=True)
        lc.fill_placeholders({"mode": "Supervised"})
        self.assertEqual(lc.primary_learning_mode, "Supervised")
        self.assertIn("Supervised", lc.render())
        self.assertIn("True", lc.render())

        # Test CognitiveModuleConfiguration (nesting)
        cmc = CognitiveModuleConfiguration(
            personality_config=pc,
            motivational_bias_config=mb,
            emotional_profile_config=ep,
            learning_module_config=lc
        )
        cmc_render = cmc.render()
        self.assertIn("Personality Config", cmc_render) # Check section headers
        self.assertIn("Motivational Bias", cmc_render)
        self.assertIn("Emotional Profile", cmc_render)
        self.assertIn("Learning Module Config", cmc_render)
        self.assertIn("Ocean Openness", cmc_render) # Check nested content
        self.assertIn("goal1", cmc_render.lower())
        self.assertIn("Positive", cmc_render)
        self.assertIn("Supervised", cmc_render)


    def test_developmental_curriculum_initialization_add_step(self):
        curriculum = DevelopmentalCurriculum(name="TestCurriculum", description="Desc", target_developmental_stage="StageX", version="1.0")
        self.assertEqual(curriculum.name, "TestCurriculum")
        self.assertEqual(len(curriculum.steps), 0)

        step1 = CurriculumStep(name="Step1", order=1, prompt_reference="p1.json")
        step0 = CurriculumStep(name="Step0", order=0, prompt_reference="p0.json")

        curriculum.add_step(step1)
        self.assertEqual(len(curriculum.steps), 1)
        self.assertEqual(curriculum.steps[0].name, "Step1")

        curriculum.add_step(step0) # Add out of order
        self.assertEqual(len(curriculum.steps), 2)
        self.assertEqual(curriculum.steps[0].name, "Step0") # Check if sorted
        self.assertEqual(curriculum.steps[1].name, "Step1")

    def test_developmental_curriculum_fill_placeholders(self):
        curriculum = self._create_sample_curriculum("_curr_ph")
        placeholders = {
            "name_suffix": "_filled",
            "step_note_placeholder": "filled_note",
            "curriculum_purpose": "testing placeholders in curriculum"
        }
        curriculum.fill_placeholders(placeholders)
        self.assertEqual(curriculum.name, "TestCurriculum_curr_ph") # Name doesn't have placeholder
        self.assertEqual(curriculum.description, "A curriculum for testing placeholders in curriculum")

        # Check placeholders in steps (assuming step names and notes had placeholders)
        # The sample curriculum has placeholders in step.name and step.notes
        self.assertEqual(curriculum.steps[0].name, "Step1_filled")
        self.assertEqual(curriculum.steps[0].notes, "Notes for filled_note")
        self.assertEqual(curriculum.steps[1].name, "Step2_filled")


    def test_developmental_curriculum_render(self):
        curriculum = self._create_sample_curriculum("_curr_render")
        curriculum.fill_placeholders({
            "name_suffix": "_rendered",
            "step_note_placeholder": "render_note",
            "curriculum_purpose": "render_purpose"
        })
        markdown = curriculum.render()
        self.assertIn("# Curriculum: TestCurriculum_curr_render", markdown)
        self.assertIn("A curriculum for render_purpose", markdown)
        self.assertIn("### Step 1: Step1_rendered", markdown)
        self.assertIn(f"- **Prompt Template:** {os.path.join(self.test_dir, 'curr_prompt1_curr_render.json')}", markdown)
        self.assertIn("- **Notes:** Notes for render_note", markdown)
        self.assertIn("### Step 2: Step2_rendered", markdown)

    def test_developmental_curriculum_save_and_load_template(self):
        original_curriculum = self._create_sample_curriculum("_curr_saveload")
        original_curriculum.fill_placeholders({
             "name_suffix": "_final",
             "step_note_placeholder": "final_note",
             "curriculum_purpose": "final_purpose"
        })

        filepath = os.path.join(self.test_dir, "curriculum_template.json")
        save_template(original_curriculum, filepath)
        self.assertTrue(os.path.exists(filepath))

        loaded_curriculum = load_template(filepath)
        self.assertIsNotNone(loaded_curriculum)
        self.assertIsInstance(loaded_curriculum, DevelopmentalCurriculum)

        self.assertTrue(compare_dicts(original_curriculum.__dict__, loaded_curriculum.__dict__), "Curriculum dictionaries do not match after save/load.")


    def test_developmental_curriculum_export_to_markdown(self):
        curriculum = self._create_sample_curriculum("_curr_mdexport")
        curriculum.fill_placeholders({
            "name_suffix": "_md", "step_note_placeholder": "md_note", "curriculum_purpose": "md_export"
        })

        filepath = os.path.join(self.test_dir, "curriculum_export.md")
        export_to_markdown(curriculum, filepath)
        self.assertTrue(os.path.exists(filepath))

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        expected_render = curriculum.render()
        self.assertEqual(content, expected_render)

if __name__ == '__main__':
    unittest.main()
