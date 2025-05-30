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

from PiaAGI_Hub.PiaPES.web_app.app import app
from PiaAGI_Hub.PiaPES.prompt_engine_mvp import (
    PiaAGIPrompt, SystemRules, Requirements, Executors, Role, CognitiveModuleConfiguration,
    PersonalityConfig, MotivationalBias, EmotionalProfile, LearningModuleConfig,
    DevelopmentalCurriculum, CurriculumStep, BaseElement,
    save_template, load_template, pia_agi_object_hook
)

def compare_dicts(d1, d2, path=""):
    if type(d1) != type(d2): return False
    if isinstance(d1, dict):
        if set(d1.keys()) != set(d2.keys()): return False
        for key in d1:
            if not compare_dicts(d1[key], d2[key], f"{path}.{key}" if path else key): return False
    elif isinstance(d1, list):
        if len(d1) != len(d2): return False
        for i, (item1, item2) in enumerate(zip(d1, d2)):
            if not compare_dicts(item1, item2, f"{path}[{i}]"): return False
    elif isinstance(d1, BaseElement): # Compare __dict__ for BaseElement instances
        if not compare_dicts(d1.__dict__, d2.__dict__, path): return False
    else: # Primitive types
        if d1 != d2: return False
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
        shutil.rmtree(self.class_test_prompt_dir)
        os.makedirs(self.class_test_prompt_dir)

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
        self.assertEqual(len(data), 2) # prompt1 and prompt2
        filenames_in_response = [item['filename'] for item in data]
        self.assertIn(self.prompt1_filename, filenames_in_response)
        self.assertIn(self.prompt2_filename, filenames_in_response)

    def test_api_get_prompt_exists(self):
        response = self.client.get(f'/api/prompts/{self.prompt1_filename}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['filename'], self.prompt1_filename)
        self.assertTrue(compare_dicts(data['prompt_data'], self.prompt1_data_dict))

    def test_api_create_prompt(self):
        new_prompt_payload = {
            "__type__": "PiaAGIPrompt", "filename": "created_prompt.json",
            "objective": "Created Prompt Objective", "version": "1.0-created", "author": "Creator",
            "system_rules": {"__type__": "SystemRules", "language": "de"},
            "requirements": {"__type__": "Requirements", "goal": "Creation goal"},
            "executors": {
                "__type__": "Executors", "role": {
                    "__type__": "Role", "name": "CreatorRole", "profile": "Profile for creation",
                    "skills_focus": ["created_skill1"], "knowledge_domains_active": ["created_domain1"],
                    "cognitive_module_configuration": {
                        "__type__": "CognitiveModuleConfiguration",
                        "personality_config": {"__type__": "PersonalityConfig", "ocean_openness": 0.1}
                    }
                }
            }
        }
        response = self.client.post('/api/prompts', json=new_prompt_payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        data = json.loads(response.data)
        created_filename = data['filename']
        self.assertEqual(created_filename, "created_prompt.json")
        loaded_prompt = load_template(os.path.join(app.PROMPT_DIR, created_filename))
        self.assertEqual(loaded_prompt.objective, new_prompt_payload['objective'])
        self.assertEqual(loaded_prompt.executors.role.skills_focus, ["created_skill1"])
        self.assertEqual(loaded_prompt.executors.role.cognitive_module_configuration.personality_config.ocean_openness, 0.1)

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

    def test_api_update_prompt_exists(self):
        update_payload = {
            "__type__": "PiaAGIPrompt", "objective": "Super Updated Objective", "version": "1.0-super-updated",
            "executors": {
                "__type__": "Executors", "role": {
                    "__type__": "Role", "name": "SuperRole", "profile": "Super Profile",
                    "skills_focus": ["super_skill"], "knowledge_domains_active": ["super_domain"],
                    "cognitive_module_configuration": {
                        "__type__": "CognitiveModuleConfiguration",
                        "personality_config": {"__type__": "PersonalityConfig", "ocean_neuroticism": 0.99}
                    }
                }
            }
        }
        response = self.client.put(f'/api/prompts/{self.prompt1_filename}', json=update_payload)
        self.assertEqual(response.status_code, 200, response.get_json())
        loaded_prompt = load_template(os.path.join(app.PROMPT_DIR, self.prompt1_filename))
        self.assertEqual(loaded_prompt.objective, "Super Updated Objective")
        self.assertEqual(loaded_prompt.executors.role.name, "SuperRole")
        self.assertEqual(loaded_prompt.executors.role.skills_focus, ["super_skill"])
        self.assertEqual(loaded_prompt.executors.role.cognitive_module_configuration.personality_config.ocean_neuroticism, 0.99)

    # ... (other existing prompt tests: not_found, bad_request, conflict, delete, render - assuming they are fine)

    def test_api_list_curricula(self):
        response = self.client.get('/api/curricula')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['filename'], self.curriculum1_filename)
        self.assertEqual(data[0]['name'], self.curriculum1_data_dict['name'])

    def test_api_get_curriculum_exists(self):
        response = self.client.get(f'/api/curricula/{self.curriculum1_filename}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(compare_dicts(data['curriculum_data'], self.curriculum1_data_dict))

    def test_api_get_curriculum_not_found(self):
        response = self.client.get('/api/curricula/non_existent.curriculum.json')
        self.assertEqual(response.status_code, 404)

    def test_api_render_curriculum_exists(self):
        response = self.client.get(f'/api/curricula/{self.curriculum1_filename}/render')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn(self.curriculum1_data_dict['name'], data['markdown'])

    def test_api_create_curriculum_valid(self):
        payload = {
            "__type__": "DevelopmentalCurriculum", "filename": "new.curriculum.json",
            "name": "New Curric", "description": "Desc", "target_developmental_stage": "Stage",
            "version": "1.0", "author": "Author",
            "steps": [{"__type__": "CurriculumStep", "name": "S1", "order": 1, "prompt_reference": "p1.json"}]
        }
        response = self.client.post('/api/curricula', json=payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        self.assertTrue(os.path.exists(os.path.join(app.PROMPT_DIR, "new.curriculum.json")))

    def test_api_create_curriculum_missing_fields(self):
        payload = {"__type__": "DevelopmentalCurriculum", "filename": "bad.curriculum.json", "name": "N"} # Missing steps, desc
        response = self.client.post('/api/curricula', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required top-level field", response.get_json()['error'])

    def test_api_create_curriculum_missing_step_fields(self):
        payload = {
            "__type__": "DevelopmentalCurriculum", "filename": "bad_step.curriculum.json",
            "name": "N", "description": "D", "steps": [{"__type__": "CurriculumStep", "order": 1}] # Missing name, ref
        }
        response = self.client.post('/api/curricula', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required field 'name' in step 1", response.get_json()['error'])

    def test_api_create_curriculum_invalid_filename(self):
        payload = {"__type__": "DevelopmentalCurriculum", "filename": "invalid.json", "name": "N", "description": "D", "steps": []}
        response = self.client.post('/api/curricula', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("must end with '.curriculum.json'", response.get_json()['error'])

    def test_api_create_curriculum_file_exists(self):
        payload = {"__type__": "DevelopmentalCurriculum", "filename": self.curriculum1_filename, "name": "N", "description": "D", "steps": []}
        response = self.client.post('/api/curricula', json=payload)
        self.assertEqual(response.status_code, 409)

    def test_api_create_curriculum_bad_json_structure(self):
        payload = {"__type__": "DevelopmentalCurriculum", "filename": "bad_struct.curriculum.json", "name": "N", "description": "D",
                   "steps": [{"__type__": "NotAStep", "name": "S", "order": 1, "prompt_reference": "p.json"}]}
        response = self.client.post('/api/curricula', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid __type__ for step 1", response.get_json()['error'])

    def test_api_update_curriculum_metadata_valid(self):
        update_payload = {"name": "Updated Name", "version": "2.0"}
        response = self.client.put(f'/api/curricula/{self.curriculum1_filename}', json=update_payload)
        self.assertEqual(response.status_code, 200, response.get_json())
        loaded = load_template(os.path.join(app.PROMPT_DIR, self.curriculum1_filename))
        self.assertEqual(loaded.name, "Updated Name")
        self.assertEqual(loaded.version, "2.0")
        self.assertEqual(len(loaded.steps), 2) # Steps unchanged

    def test_api_update_curriculum_metadata_not_found(self):
        response = self.client.put('/api/curricula/no.curriculum.json', json={"name": "N"})
        self.assertEqual(response.status_code, 404)

    def test_api_update_curriculum_metadata_payload_ignores_steps(self):
        update_payload = {"name": "New Name", "steps": [{"__type__": "CurriculumStep", "name": "Malicious"}]}
        response = self.client.put(f'/api/curricula/{self.curriculum1_filename}', json=update_payload)
        self.assertEqual(response.status_code, 200)
        loaded = load_template(os.path.join(app.PROMPT_DIR, self.curriculum1_filename))
        self.assertEqual(loaded.name, "New Name")
        self.assertEqual(loaded.steps[0].name, "Step 1: Intro to Prompt 1") # Steps unchanged

    def test_api_update_curriculum_metadata_corrupted_file(self):
        corrupted_file = "corrupt.curriculum.json"
        with open(os.path.join(app.PROMPT_DIR, corrupted_file), "w") as f: f.write("{bad json")
        response = self.client.put(f'/api/curricula/{corrupted_file}', json={"name": "N"})
        self.assertEqual(response.status_code, 500)
        self.assertIn("Failed to load existing curriculum", response.get_json()['error'])

    # HTML Routes for Curriculum
    def test_route_create_curriculum_view(self):
        response = self.client.get('/curriculum/create')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Create New Curriculum", response.data)

    def test_route_edit_curriculum_view_exists(self):
        response = self.client.get(f'/curriculum/edit/{self.curriculum1_filename}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.curriculum1_data_dict['name'].encode(), response.data)

    def test_route_edit_curriculum_view_not_found(self):
        response = self.client.get('/curriculum/edit/no.curriculum.json', follow_redirects=True)
        self.assertEqual(response.status_code, 200) # Redirects to dashboard
        self.assertIn(b"Error: Curriculum file 'no.curriculum.json' not found for editing.", response.data)

    # ... (keep other existing HTML route tests for prompts) ...
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
        self.assertIn(f"Edit Prompt: {self.prompt1_filename}".encode(), response.data)
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
