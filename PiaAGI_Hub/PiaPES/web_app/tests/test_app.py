import unittest
import os
import sys
import json
import shutil
import tempfile

# --- Adjust sys.path to allow importing 'app' and 'prompt_engine_mvp' ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

PES_WEB_APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PES_DIR = os.path.abspath(os.path.join(PES_WEB_APP_DIR, '..'))

if PES_DIR not in sys.path:
    sys.path.insert(0, PES_DIR)
if PES_WEB_APP_DIR not in sys.path:
     sys.path.insert(0, os.path.abspath(os.path.join(PES_WEB_APP_DIR, '..', '..'))) # Add PiaAGI_Hub


from PiaAGI_Hub.PiaPES.web_app.app import app # app object from your Flask app
from PiaAGI_Hub.PiaPES.prompt_engine_mvp import (
    PiaAGIPrompt, SystemRules, Requirements, Executors, Role, CognitiveModuleConfiguration,
    PersonalityConfig, MotivationalBias, EmotionalProfile, LearningModuleConfig,
    DevelopmentalCurriculum, CurriculumStep, BaseElement,
    save_template, load_template, pia_agi_object_hook
)

def compare_dicts(d1, d2, path=""):
    """Recursively compare two dictionaries, including handling of BaseElement objects by comparing their __dict__."""
    if type(d1) != type(d2):
        # print(f"Type mismatch at {path}: {type(d1)} vs {type(d2)}")
        return False

    if isinstance(d1, dict):
        if set(d1.keys()) != set(d2.keys()):
            # print(f"Key mismatch at {path}: {set(d1.keys())} vs {set(d2.keys())}")
            return False
        for key in d1:
            new_path = f"{path}.{key}" if path else key
            if not compare_dicts(d1[key], d2[key], new_path):
                return False
    elif isinstance(d1, list):
        if len(d1) != len(d2):
            # print(f"List length mismatch at {path}: {len(d1)} vs {len(d2)}")
            return False
        for i, (item1, item2) in enumerate(zip(d1, d2)):
            new_path = f"{path}[{i}]"
            if not compare_dicts(item1, item2, new_path):
                return False
    elif isinstance(d1, BaseElement):
        dict1_to_compare = d1.__dict__
        dict2_to_compare = d2.__dict__ if isinstance(d2, BaseElement) else d2
        if not compare_dicts(dict1_to_compare, dict2_to_compare, path): return False
    else:
        if d1 != d2:
            # print(f"Value mismatch at {path}: {d1} != {d2}")
            return False
    return True


class TestWebAppAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = 'test_secret_key'
        cls.class_test_prompt_dir = tempfile.mkdtemp(prefix="pia_pes_class_prompts_")
        cls.original_prompt_dir = app.PROMPT_DIR
        app.PROMPT_DIR = cls.class_test_prompt_dir
        cls.client = app.test_client()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.class_test_prompt_dir)
        app.PROMPT_DIR = cls.original_prompt_dir

    def setUp(self):
        # Clear and recreate files for each test
        for item in os.listdir(app.PROMPT_DIR):
            item_path = os.path.join(app.PROMPT_DIR, item)
            if os.path.isfile(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)

        self.prompt1_data_dict = {
            "__type__": "PiaAGIPrompt", "objective": "Test Prompt 1 Objective", "version": "1.0",
            "author": "Test User", "initiate_interaction": "Start prompt 1",
            "system_rules": {"__type__": "SystemRules", "language": "en"},
            "requirements": {"__type__": "Requirements", "goal": "Test goal 1"},
            "executors": {
                "__type__": "Executors",
                "role": {
                    "__type__": "Role", "name": "TestRole1", "profile": "Profile 1",
                    "skills_focus": ["skill1", "skill2"],
                    "knowledge_domains_active": ["domain1", "domain2"]
                }
            },
            "workflow_or_curriculum_phase": {
                "__type__": "Workflow",
                "steps": [
                    {"__type__": "WorkflowStep", "name": "Initial WF Step 1", "action_directive": "Initial Action 1", "module_focus": ["ModA"], "expected_outcome_internal": "StateA", "expected_output_external": "OutputA"},
                    {"__type__": "WorkflowStep", "name": "Initial WF Step 2", "action_directive": "Initial Action 2", "module_focus": ["ModB"], "expected_outcome_internal": "StateB", "expected_output_external": "OutputB"}
                ]
            },
            "developmental_scaffolding_context": {
                "__type__": "DevelopmentalScaffolding",
                "current_developmental_goal": "Initial Dev Goal",
                "scaffolding_techniques_employed": ["Technique1", "Technique2"],
                "feedback_level_from_overseer": "Medium"
            }
        }
        self.prompt1_filename = "test_prompt1.json"
        p1_obj = json.loads(json.dumps(self.prompt1_data_dict), object_hook=pia_agi_object_hook)
        save_template(p1_obj, os.path.join(app.PROMPT_DIR, self.prompt1_filename))

        self.prompt2_data_dict = {
            "__type__": "PiaAGIPrompt", "objective": "Test Prompt 2 Objective", "version": "1.1",
            "author": "Another User", "initiate_interaction": "Start prompt 2"
        }
        self.prompt2_filename = "test_prompt2.json"
        p2_obj = json.loads(json.dumps(self.prompt2_data_dict), object_hook=pia_agi_object_hook)
        save_template(p2_obj, os.path.join(app.PROMPT_DIR, self.prompt2_filename))

        self.curriculum1_filename = "test_curriculum1.curriculum.json"
        curriculum_steps_data = [
            {"__type__": "CurriculumStep", "name": "Step 1", "order": 1, "prompt_reference": self.prompt1_filename, "conditions": "C1", "notes": "N1"},
            {"__type__": "CurriculumStep", "name": "Step 2", "order": 2, "prompt_reference": self.prompt2_filename, "conditions": "C2", "notes": "N2"}
        ]
        self.curriculum1_data_dict = {
            "__type__": "DevelopmentalCurriculum", "name": "Test Curriculum Alpha", "version": "0.5c",
            "description": "A curriculum for testing.", "target_developmental_stage": "EarlyTest",
            "author": "Curric Test Author", "steps": curriculum_steps_data
        }
        steps_objs = [CurriculumStep(**s) for s in curriculum_steps_data]
        curriculum_obj = DevelopmentalCurriculum(name=self.curriculum1_data_dict["name"], description=self.curriculum1_data_dict["description"],
                                                 target_developmental_stage=self.curriculum1_data_dict["target_developmental_stage"],
                                                 version=self.curriculum1_data_dict["version"], author=self.curriculum1_data_dict["author"], steps=steps_objs)
        save_template(curriculum_obj, os.path.join(app.PROMPT_DIR, self.curriculum1_filename))

    def test_api_list_prompts(self):
        response = self.client.get('/api/prompts')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        filenames_in_response = [item['filename'] for item in data]
        self.assertIn(self.prompt1_filename, filenames_in_response)
        self.assertIn(self.prompt2_filename, filenames_in_response)

    def test_api_get_prompt_exists(self):
        response = self.client.get(f'/api/prompts/{self.prompt1_filename}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['filename'], self.prompt1_filename)
        self.assertTrue(compare_dicts(data['prompt_data'], self.prompt1_data_dict))

    def test_api_get_prompt_not_found(self):
        response = self.client.get('/api/prompts/non_existent_prompt.json')
        self.assertEqual(response.status_code, 404)

    def test_api_create_prompt(self):
        new_prompt_payload = {
            "__type__": "PiaAGIPrompt", "filename": "created_prompt.json",
            "objective": "Created Prompt Objective", "version": "1.0-created", "author": "Creator",
            "system_rules": {"__type__": "SystemRules", "language": "de"},
            "requirements": {"__type__": "Requirements", "goal": "Creation goal"},
            "executors": { "__type__": "Executors", "role": {
                    "__type__": "Role", "name": "CreatorRole", "profile": "Profile for creation",
                    "skills_focus": ["created_skill1"], "knowledge_domains_active": ["created_domain1"],
                    "cognitive_module_configuration": {
                        "__type__": "CognitiveModuleConfiguration",
                        "personality_config": {"__type__": "PersonalityConfig", "ocean_openness": 0.1}
                    }}},
            "workflow_or_curriculum_phase": {
                "__type__": "Workflow",
                "steps": [
                    {"__type__": "WorkflowStep", "name": "Created WF Step 1", "action_directive": "Action C1", "module_focus": ["ModC"], "expected_outcome_internal": "StateC", "expected_output_external": "OutputC"},
                ]
            },
            "developmental_scaffolding_context": {
                "__type__": "DevelopmentalScaffolding",
                "current_developmental_goal": "Created Dev Goal",
                "scaffolding_techniques_employed": ["TechniqueC"],
                "feedback_level_from_overseer": "High"
            }
        }
        response = self.client.post('/api/prompts', json=new_prompt_payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        data = json.loads(response.data)
        created_filename = data['filename']
        self.assertEqual(created_filename, "created_prompt.json") # Filename from payload, sanitized by backend
        loaded_prompt = load_template(os.path.join(app.PROMPT_DIR, created_filename))
        self.assertEqual(loaded_prompt.objective, new_prompt_payload['objective'])
        self.assertEqual(loaded_prompt.executors.role.skills_focus, ["created_skill1"])
        self.assertEqual(loaded_prompt.executors.role.cognitive_module_configuration.personality_config.ocean_openness, 0.1)
        self.assertIsNotNone(loaded_prompt.workflow_or_curriculum_phase)
        self.assertEqual(loaded_prompt.workflow_or_curriculum_phase.__type__, "Workflow")
        self.assertEqual(len(loaded_prompt.workflow_or_curriculum_phase.steps), 1)
        self.assertEqual(loaded_prompt.workflow_or_curriculum_phase.steps[0].name, "Created WF Step 1")
        self.assertEqual(loaded_prompt.workflow_or_curriculum_phase.steps[0].module_focus, ["ModC"])
        self.assertIsNotNone(loaded_prompt.developmental_scaffolding_context)
        self.assertEqual(loaded_prompt.developmental_scaffolding_context.current_developmental_goal, "Created Dev Goal")
        self.assertEqual(loaded_prompt.developmental_scaffolding_context.feedback_level_from_overseer, "High")

    def test_api_create_prompt_malformed_nested_type(self):
        malformed_payload = {
            "__type__": "PiaAGIPrompt", "filename": "malformed_create.json",
            "objective": "Malformed Nested", "version": "0.1",
            "executors": {"__type__": "Executors", "role": {"__type__": "Role", "name": "BadRole",
                          "cognitive_module_configuration": {"__type__": "CognitiveModuleConfiguration",
                                                             "personality_config": {"ocean_openness": 0.5}}}}} # Missing __type__
        response = self.client.post('/api/prompts', json=malformed_payload)
        self.assertEqual(response.status_code, 400, response.get_json())
        self.assertIn("Invalid prompt data structure", response.get_json().get("error", ""))

    def test_api_create_prompt_bad_request(self):
        response = self.client.post('/api/prompts', data="not json")
        self.assertEqual(response.status_code, 400)
        response = self.client.post('/api/prompts', json={})
        self.assertEqual(response.status_code, 400)

    def test_api_create_prompt_conflict(self):
        conflict_data = {"__type__": "PiaAGIPrompt", "filename": self.prompt1_filename, "objective": "C"}
        response = self.client.post('/api/prompts', json=conflict_data)
        self.assertEqual(response.status_code, 409)

    def test_api_update_prompt_exists(self):
        update_payload = {
            "__type__": "PiaAGIPrompt", "objective": "Super Updated Objective", "version": "1.0-super-updated",
            "executors": { "__type__": "Executors", "role": {
                    "__type__": "Role", "name": "SuperRole", "profile": "Super Profile",
                    "skills_focus": ["super_skill1", "super_skill2"],
                    "knowledge_domains_active": ["super_domain1"],
                    "cognitive_module_configuration": {
                        "__type__": "CognitiveModuleConfiguration",
                        "personality_config": {"__type__": "PersonalityConfig", "ocean_neuroticism": 0.99}
                    }}},
            "workflow_or_curriculum_phase": { # Update: Change step name, add a step
                "__type__": "Workflow",
                "steps": [
                    {"__type__": "WorkflowStep", "name": "Updated WF Step 1", "action_directive": "Updated Action 1", "module_focus": ["ModAUpdated"], "expected_outcome_internal": "StateAUpdated", "expected_output_external": "OutputAUpdated"},
                    {"__type__": "WorkflowStep", "name": "Initial WF Step 2", "action_directive": "Initial Action 2", "module_focus": ["ModB"], "expected_outcome_internal": "StateB", "expected_output_external": "OutputB"}, # Unchanged
                    {"__type__": "WorkflowStep", "name": "Added WF Step 3", "action_directive": "Added Action 3", "module_focus": ["ModNew"], "expected_outcome_internal": "StateNew", "expected_output_external": "OutputNew"}
                ]
            },
            "developmental_scaffolding_context": { # Update: Change goal and feedback
                "__type__": "DevelopmentalScaffolding",
                "current_developmental_goal": "Super Updated Dev Goal",
                "scaffolding_techniques_employed": ["Technique1", "TechniqueUpdated"], # Technique2 removed, TechniqueUpdated added
                "feedback_level_from_overseer": "VeryHigh"
            }
        }
        response = self.client.put(f'/api/prompts/{self.prompt1_filename}', json=update_payload)
        self.assertEqual(response.status_code, 200, response.get_json())
        loaded_prompt = load_template(os.path.join(app.PROMPT_DIR, self.prompt1_filename))
        self.assertEqual(loaded_prompt.objective, "Super Updated Objective")
        self.assertEqual(loaded_prompt.executors.role.name, "SuperRole")
        self.assertEqual(loaded_prompt.executors.role.skills_focus, ["super_skill1", "super_skill2"])
        self.assertEqual(loaded_prompt.executors.role.cognitive_module_configuration.personality_config.ocean_neuroticism, 0.99)

        self.assertIsNotNone(loaded_prompt.workflow_or_curriculum_phase)
        self.assertEqual(loaded_prompt.workflow_or_curriculum_phase.__type__, "Workflow")
        self.assertEqual(len(loaded_prompt.workflow_or_curriculum_phase.steps), 3)
        self.assertEqual(loaded_prompt.workflow_or_curriculum_phase.steps[0].name, "Updated WF Step 1")
        self.assertEqual(loaded_prompt.workflow_or_curriculum_phase.steps[0].module_focus, ["ModAUpdated"])
        self.assertEqual(loaded_prompt.workflow_or_curriculum_phase.steps[2].name, "Added WF Step 3")

        self.assertIsNotNone(loaded_prompt.developmental_scaffolding_context)
        self.assertEqual(loaded_prompt.developmental_scaffolding_context.current_developmental_goal, "Super Updated Dev Goal")
        self.assertEqual(loaded_prompt.developmental_scaffolding_context.scaffolding_techniques_employed, ["Technique1", "TechniqueUpdated"])
        self.assertEqual(loaded_prompt.developmental_scaffolding_context.feedback_level_from_overseer, "VeryHigh")


    def test_api_update_prompt_not_found(self):
        response = self.client.put('/api/prompts/non_existent_prompt.json', json=self.prompt1_data_dict)
        self.assertEqual(response.status_code, 404)

    # --- New Negative Tests for Workflow and Developmental Scaffolding ---
    def test_api_create_prompt_invalid_workflow_structure_steps_not_list(self):
        payload = {
            "__type__": "PiaAGIPrompt", "filename": "invalid_wf1.json", "objective": "Test",
            "workflow_or_curriculum_phase": {"__type__": "Workflow", "steps": "not-a-list"}
        }
        response = self.client.post('/api/prompts', json=payload)
        self.assertEqual(response.status_code, 400, response.get_json())
        self.assertIn("Field 'steps' must be of type list", response.get_json().get("error", ""))

    def test_api_create_prompt_invalid_workflow_structure_step_missing_type(self):
        payload = {
            "__type__": "PiaAGIPrompt", "filename": "invalid_wf2.json", "objective": "Test",
            "workflow_or_curriculum_phase": {
                "__type__": "Workflow",
                "steps": [{"name": "Step W/O Type", "action_directive": "Do"}] # Missing __type__
            }
        }
        response = self.client.post('/api/prompts', json=payload)
        self.assertEqual(response.status_code, 400, response.get_json())
        self.assertIn("Invalid __type__ for step 1", response.get_json().get("error", ""))

    def test_api_create_prompt_invalid_workflow_structure_step_missing_name(self):
        payload = {
            "__type__": "PiaAGIPrompt", "filename": "invalid_wf3.json", "objective": "Test",
            "workflow_or_curriculum_phase": {
                "__type__": "Workflow",
                "steps": [{"__type__": "WorkflowStep", "action_directive": "Do"}] # Missing name
            }
        }
        response = self.client.post('/api/prompts', json=payload)
        self.assertEqual(response.status_code, 400, response.get_json())
        # The backend might catch this as a general "Invalid prompt data structure" or more specifically.
        # For now, checking for 400 is the main goal. The exact message depends on app.py's validation depth.
        # self.assertIn("Missing required field 'name' in step", response.get_json().get("error", "")) # Example detailed check
        self.assertTrue(response.get_json().get("error", "").startswith("Invalid prompt data structure") or \
                        "Missing required field 'name' in step" in response.get_json().get("error", ""),
                        f"Unexpected error: {response.get_json().get('error', '')}")


    def test_api_create_prompt_invalid_dev_scaffolding_structure_missing_type(self):
        payload = {
            "__type__": "PiaAGIPrompt", "filename": "invalid_ds1.json", "objective": "Test",
            "developmental_scaffolding_context": {"current_developmental_goal": "Goal"} # Missing __type__
        }
        response = self.client.post('/api/prompts', json=payload)
        self.assertEqual(response.status_code, 400, response.get_json())
        self.assertIn("Invalid prompt data structure", response.get_json().get("error", ""))


    def test_api_create_prompt_invalid_dev_scaffolding_structure_techniques_not_list(self):
        payload = {
            "__type__": "PiaAGIPrompt", "filename": "invalid_ds2.json", "objective": "Test",
            "developmental_scaffolding_context": {
                "__type__": "DevelopmentalScaffolding",
                "scaffolding_techniques_employed": "not-a-list"
            }
        }
        response = self.client.post('/api/prompts', json=payload)
        self.assertEqual(response.status_code, 400, response.get_json())
        self.assertIn("Field 'scaffolding_techniques_employed' must be of type list", response.get_json().get("error", ""))

    def test_api_update_prompt_invalid_workflow_structure(self):
        payload = {"workflow_or_curriculum_phase": {"__type__": "Workflow", "steps": "not-a-list"}}
        response = self.client.put(f'/api/prompts/{self.prompt1_filename}', json=payload)
        self.assertEqual(response.status_code, 400, response.get_json())
        self.assertIn("Field 'steps' must be of type list", response.get_json().get("error", ""))

    def test_api_update_prompt_invalid_dev_scaffolding_structure(self):
        payload = {
            "developmental_scaffolding_context": {
                "__type__": "DevelopmentalScaffolding",
                "scaffolding_techniques_employed": "not-a-list"
            }
        }
        response = self.client.put(f'/api/prompts/{self.prompt1_filename}', json=payload)
        self.assertEqual(response.status_code, 400, response.get_json())
        self.assertIn("Field 'scaffolding_techniques_employed' must be of type list", response.get_json().get("error", ""))

    # --- End of New Negative Tests ---

    def test_api_delete_prompt_exists(self):
        response = self.client.delete(f'/api/prompts/{self.prompt1_filename}')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(os.path.exists(os.path.join(app.PROMPT_DIR, self.prompt1_filename)))

    def test_api_delete_prompt_not_found(self):
        response = self.client.delete('/api/prompts/non_existent_prompt.json')
        self.assertEqual(response.status_code, 404)

    def test_api_render_prompt_exists(self):
        response = self.client.get(f'/api/prompts/{self.prompt1_filename}/render')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn(self.prompt1_data_dict['objective'], data['markdown'])

    def test_api_render_prompt_not_found(self):
        response = self.client.get('/api/prompts/non_existent_prompt.json/render')
        self.assertEqual(response.status_code, 404)

    def test_route_dashboard(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Prompt Dashboard", response.data)

    def test_route_create_prompt_view(self):
        response = self.client.get('/create')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Create New Prompt", response.data)

    def test_route_edit_prompt_view_exists(self):
        response = self.client.get(f'/edit/{self.prompt1_filename}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.prompt1_data_dict['objective'].encode(), response.data)

    def test_route_edit_prompt_view_not_found(self):
        response = self.client.get('/edit/non_existent_prompt.json', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Error: Prompt file 'non_existent_prompt.json' not found.", response.data)

    def test_route_view_prompt_exists(self):
        response = self.client.get(f'/view/{self.prompt1_filename}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"Prompt Details: {self.prompt1_filename}".encode(), response.data)

    def test_route_view_prompt_not_found(self):
        response = self.client.get('/view/non_existent_prompt.json', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Error: Prompt file 'non_existent_prompt.json' not found.", response.data)

    # --- Curriculum Test Methods (New) ---
    def test_api_list_curricula(self):
        response = self.client.get('/api/curricula')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) >= 1)
        found = any(item['filename'] == self.curriculum1_filename for item in data)
        self.assertTrue(found, "Test curriculum not found in list.")
        for item in data:
            if item['filename'] == self.curriculum1_filename:
                self.assertEqual(item['name'], self.curriculum1_data_dict['name'])
                self.assertEqual(item['version'], self.curriculum1_data_dict['version'])

    def test_api_get_curriculum_exists(self):
        response = self.client.get(f'/api/curricula/{self.curriculum1_filename}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(compare_dicts(data['curriculum_data'], self.curriculum1_data_dict))

    def test_api_get_curriculum_not_found(self):
        response = self.client.get('/api/curricula/non_existent.curriculum.json')
        self.assertEqual(response.status_code, 404)
        self.assertIn("Curriculum file not found", response.get_json().get("description", ""))

    def test_api_render_curriculum_exists(self):
        response = self.client.get(f'/api/curricula/{self.curriculum1_filename}/render')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn(self.curriculum1_data_dict['name'], data['markdown'])
        self.assertIn(self.curriculum1_data_dict['steps'][0]['name'], data['markdown'])

    def test_api_render_curriculum_not_found(self):
        response = self.client.get('/api/curricula/non_existent.curriculum.json/render')
        self.assertEqual(response.status_code, 404)
        self.assertIn("Curriculum file not found", response.get_json().get("description", ""))

    def test_api_create_curriculum_valid(self):
        new_filename = "new_valid.curriculum.json"
        payload = {
            "__type__": "DevelopmentalCurriculum", "filename": new_filename, "name": "Valid New",
            "description": "d", "target_developmental_stage": "s", "version": "v", "author": "a",
            "steps": [{"__type__": "CurriculumStep", "name": "S1", "order": 1, "prompt_reference": "p1.json", "conditions":"cond", "notes":"note"}]
        }
        response = self.client.post('/api/curricula', json=payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        self.assertTrue(os.path.exists(os.path.join(app.PROMPT_DIR, new_filename)))
        loaded = load_template(os.path.join(app.PROMPT_DIR, new_filename))
        self.assertEqual(loaded.name, payload["name"])
        self.assertEqual(len(loaded.steps), 1)

    def test_api_create_curriculum_missing_fields(self):
        payload = {"__type__": "DevelopmentalCurriculum", "filename": "bad_req.curriculum.json", "name": "N"}
        response = self.client.post('/api/curricula', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required top-level field", response.get_json()['error'])

    def test_api_create_curriculum_missing_step_fields(self):
        payload = {"__type__": "DevelopmentalCurriculum", "filename": "bad_step.curriculum.json", "name": "N", "description":"D",
                   "steps": [{"__type__": "CurriculumStep", "order": 1}]}
        response = self.client.post('/api/curricula', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required field 'name' in step 1", response.get_json()['error'])

    def test_api_create_curriculum_invalid_filename(self):
        payload = {"__type__": "DevelopmentalCurriculum", "filename": "invalid.json", "name":"N", "description":"D", "steps":[]}
        response = self.client.post('/api/curricula', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("must end with '.curriculum.json'", response.get_json()['error'])

        bad_data_empty_base = { "__type__": "DevelopmentalCurriculum", "filename": ".curriculum.json", "name": "N", "description": "D", "steps": []}
        response = self.client.post('/api/curricula', json=bad_data_empty_base)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid base filename", response.get_json().get('error', ''))

    def test_api_create_curriculum_file_exists(self):
        payload = {"__type__": "DevelopmentalCurriculum", "filename": self.curriculum1_filename, "name": "N", "description":"D", "steps":[]}
        response = self.client.post('/api/curricula', json=payload)
        self.assertEqual(response.status_code, 409)

    def test_api_create_curriculum_bad_json_structure(self): # e.g. steps not a list, or step item not a dict
        payload = {"__type__": "DevelopmentalCurriculum", "filename": "bad_struct.curriculum.json", "name": "N", "description":"D",
                   "steps": "not-a-list"}
        response = self.client.post('/api/curricula', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Field 'steps' must be of type list", response.get_json()['error'])

        payload_step_type = {"__type__": "DevelopmentalCurriculum", "filename": "bad_struct2.curriculum.json", "name": "N", "description":"D",
                   "steps": [ "not-a-dict" ]}
        response = self.client.post('/api/curricula', json=payload_step_type)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Item at steps[0] is not a valid step object", response.get_json()['error'])

        payload_step_type_hint = {"__type__": "DevelopmentalCurriculum", "filename": "bad_struct3.curriculum.json", "name": "N", "description":"D",
                   "steps": [{"__type__": "NotValid", "name": "S", "order": 1, "prompt_reference": "p.json"}]}
        response = self.client.post('/api/curricula', json=payload_step_type_hint)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid __type__ for step 1", response.get_json()['error'])


    def test_api_update_curriculum_full_valid(self): # Renamed from metadata
        updated_data = {
            "__type__": "DevelopmentalCurriculum", "name": "Updated Curriculum Name", "version": "2.0-full",
            "description": "Fully updated desc.", "target_developmental_stage": "Advanced", "author": "Updater",
            "steps": [
                {"__type__": "CurriculumStep", "name": "New Step A", "order": 1, "prompt_reference": self.prompt1_filename, "conditions": "C_new", "notes": "N_new"},
                {"__type__": "CurriculumStep", "name": "New Step B", "order": 0, "prompt_reference": self.prompt2_filename, "conditions": "C_alt", "notes": "N_alt"}
            ]
        }
        response = self.client.put(f'/api/curricula/{self.curriculum1_filename}', json=updated_data)
        self.assertEqual(response.status_code, 200, response.get_json())
        loaded = load_template(os.path.join(app.PROMPT_DIR, self.curriculum1_filename))
        self.assertEqual(loaded.name, "Updated Curriculum Name")
        self.assertEqual(loaded.version, "2.0-full")
        self.assertEqual(len(loaded.steps), 2)
        self.assertEqual(loaded.steps[0].name, "New Step B")
        self.assertEqual(loaded.steps[1].notes, "N_new")

    def test_api_update_curriculum_invalid_step_data(self):
        payload = {"__type__": "DevelopmentalCurriculum", "name":"N", "description":"D",
                   "steps": [{"__type__": "CurriculumStep", "order":1}]}
        response = self.client.put(f'/api/curricula/{self.curriculum1_filename}', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required field 'name' in step 1", response.get_json()['error'])

    def test_api_update_curriculum_steps_not_a_list(self):
        payload = {"__type__": "DevelopmentalCurriculum", "name":"N", "description":"D", "steps": "not-a-list"}
        response = self.client.put(f'/api/curricula/{self.curriculum1_filename}', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Field 'steps' must be of type list", response.get_json()['error'])

    def test_api_update_curriculum_not_found(self):
        response = self.client.put('/api/curricula/no.curriculum.json', json={"name": "N"})
        self.assertEqual(response.status_code, 404)

    def test_api_update_curriculum_corrupted_file(self):
        corrupted_file = "corrupt.curriculum.json"
        with open(os.path.join(app.PROMPT_DIR, corrupted_file), "w") as f: f.write("{bad json")
        response = self.client.put(f'/api/curricula/{corrupted_file}', json={"name": "N"})
        self.assertEqual(response.status_code, 500)
        self.assertIn("Failed to load existing curriculum", response.get_json()['error'])

        valid_json_not_curriculum_path = os.path.join(app.PROMPT_DIR, "not_a_curriculum.curriculum.json")
        with open(valid_json_not_curriculum_path, "w") as f:
            json.dump({"__type__": "PiaAGIPrompt", "objective": "This is a prompt"}, f)
        response = self.client.put(f'/api/curricula/not_a_curriculum.curriculum.json', json={"name": "N"})
        self.assertEqual(response.status_code, 500)
        self.assertIn("Loaded file is not a valid curriculum object", response.get_json()['error'])


    # --- HTML Serving Routes for Curriculum ---
    def test_route_create_curriculum_view(self):
        response = self.client.get('/curriculum/create')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Create New Curriculum", response.data)

    def test_route_edit_curriculum_view_exists(self):
        response = self.client.get(f'/curriculum/edit/{self.curriculum1_filename}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.curriculum1_data_dict['name'].encode(), response.data)

    def test_route_edit_curriculum_view_not_found(self):
        response = self.client.get('/curriculum/edit/non_existent.curriculum.json', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Error: Curriculum file 'non_existent.curriculum.json' not found for editing.", response.data)

    def test_route_view_curriculum_exists(self):
        response = self.client.get(f'/curriculum/view/{self.curriculum1_filename}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.curriculum1_data_dict['name'].encode(), response.data)
        self.assertIn(self.curriculum1_data_dict['steps'][0]['name'].encode(), response.data)

    def test_route_view_curriculum_not_found(self):
        response = self.client.get('/curriculum/view/non_existent.curriculum.json', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Error: Curriculum file 'non_existent.curriculum.json' not found.", response.data)

if __name__ == '__main__':
    unittest.main()
