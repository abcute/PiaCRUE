import unittest
import os
import sys
import json
import shutil
import tempfile

# --- Adjust sys.path to allow importing 'app' and 'prompt_engine_mvp' ---
# This assumes the tests are run from the root of the PiaAGI_Hub project or similar context
# For PiaAGI_Hub/PiaPES/web_app/tests/test_app.py
# To import PiaAGI_Hub.PiaPES.web_app.app
# To import PiaAGI_Hub.PiaPES.prompt_engine_mvp
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

PES_WEB_APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PES_DIR = os.path.abspath(os.path.join(PES_WEB_APP_DIR, '..'))

# Ensure both PiaPES and its parent (PiaAGI_Hub) are available for imports
if PES_DIR not in sys.path:
    sys.path.insert(0, PES_DIR) # For PiaAGI_Hub.PiaPES.prompt_engine_mvp
if PES_WEB_APP_DIR not in sys.path: #Should be PiaAGI_Hub
     sys.path.insert(0, os.path.abspath(os.path.join(PES_WEB_APP_DIR, '..', '..')))


from PiaAGI_Hub.PiaPES.web_app.app import app
from PiaAGI_Hub.PiaPES.prompt_engine_mvp import (
    PiaAGIPrompt, SystemRules, Requirements, Executors, Role, CognitiveModuleConfiguration,
    PersonalityConfig, MotivationalBias, EmotionalProfile, LearningModuleConfig,
    DevelopmentalCurriculum, CurriculumStep, BaseElement, # Added curriculum classes & BaseElement
    save_template, load_template, pia_agi_object_hook
)

# Helper function for deep dictionary comparison (if not already present or imported)
# This was defined in the prompt for previous test generation, assuming it's available or can be redefined.
# For brevity, I'll assume it's available. If not, it would need to be included here.
# def compare_dicts(d1, d2, path=""): ... (from previous test generation)
# Re-defining for completeness in this context if it's not imported from elsewhere
def compare_dicts(d1, d2, path=""):
    """Recursively compare two dictionaries. Returns True if equal, False otherwise."""
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
    else: # Primitive types
        if d1 != d2:
            # print(f"Value mismatch at {path}: {d1} != {d2}")
            return False
    return True


class TestWebAppAPI(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

        # Create a temporary directory for test prompt files
        self.test_prompt_dir = tempfile.mkdtemp(prefix="pia_pes_test_prompts_")
        app.config['PROMPT_DIR'] = self.test_prompt_dir

        # Ensure PROMPT_DIR in the app instance used by routes is updated
        # This might require direct patching if app.PROMPT_DIR is set at module level and not read from config
        # For this test, we assume app.PROMPT_DIR can be updated via app.config or direct assignment if needed.
        # The app.py reads PROMPT_DIR at module level, so we need to patch it.
        self.original_prompt_dir = app.PROMPT_DIR # Store original
        app.PROMPT_DIR = self.test_prompt_dir      # Patch it

        # Create sample prompt files
        self.prompt1_data = {
            "__type__": "PiaAGIPrompt", "objective": "Test Prompt 1 Objective", "version": "1.0",
            "author": "Test User", "initiate_interaction": "Start prompt 1"
        }
        self.prompt1_filename = "test_prompt1.json"
        p1_obj = json.loads(json.dumps(self.prompt1_data), object_hook=pia_agi_object_hook)
        save_template(p1_obj, os.path.join(self.test_prompt_dir, self.prompt1_filename))

        self.prompt2_data = {
            "__type__": "PiaAGIPrompt", "objective": "Test Prompt 2 Objective", "version": "1.1",
            "author": "Another User", "initiate_interaction": "Start prompt 2"
        }
        self.prompt2_filename = "test_prompt2.json"
        p2_obj = json.loads(json.dumps(self.prompt2_data), object_hook=pia_agi_object_hook)
        save_template(p2_obj, os.path.join(self.test_prompt_dir, self.prompt2_filename))

        # Create sample curriculum file
        self.curriculum1_filename = "test_curriculum1.curriculum.json"
        curriculum_steps_data = [
            {
                "__type__": "CurriculumStep", "name": "Step 1: Intro to Prompt 1", "order": 1,
                "prompt_reference": self.prompt1_filename, "conditions": "None", "notes": "First step"
            },
            {
                "__type__": "CurriculumStep", "name": "Step 2: Follow up with Prompt 2", "order": 2,
                "prompt_reference": self.prompt2_filename, "conditions": "Step 1 complete", "notes": "Second step"
            }
        ]
        self.curriculum1_data = {
            "__type__": "DevelopmentalCurriculum", "name": "Test Curriculum Alpha", "version": "0.5c",
            "description": "A curriculum for testing purposes.", "target_developmental_stage": "EarlyTest",
            "author": "Curric Test Author", "steps": curriculum_steps_data
        }
        # We need to instantiate the objects to save them correctly via save_template
        # as save_template expects BaseElement instances

        # Create CurriculumStep objects
        steps_objs = []
        for step_data in curriculum_steps_data:
            # Manually create CurriculumStep - this bypasses needing a from_dict on CurriculumStep for setup
            step_obj = CurriculumStep(name=step_data["name"], order=step_data["order"], prompt_reference=step_data["prompt_reference"])
            step_obj.conditions = step_data["conditions"]
            step_obj.notes = step_data["notes"]
            steps_objs.append(step_obj)

        # Create DevelopmentalCurriculum object
        curriculum_obj = DevelopmentalCurriculum(
            name=self.curriculum1_data["name"],
            description=self.curriculum1_data["description"],
            target_developmental_stage=self.curriculum1_data["target_developmental_stage"],
            version=self.curriculum1_data["version"],
            author=self.curriculum1_data["author"],
            steps=steps_objs
        )
        save_template(curriculum_obj, os.path.join(self.test_prompt_dir, self.curriculum1_filename))


    def tearDown(self):
        shutil.rmtree(self.test_prompt_dir)
        app.PROMPT_DIR = self.original_prompt_dir # Restore original PROMPT_DIR

    # --- Test API Endpoints ---

    def test_api_list_prompts(self):
        response = self.client.get('/api/prompts')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        filenames_in_response = [item['filename'] for item in data]
        self.assertIn(self.prompt1_filename, filenames_in_response)
        self.assertIn(self.prompt2_filename, filenames_in_response)
        for item in data:
            if item['filename'] == self.prompt1_filename:
                self.assertEqual(item['name'], self.prompt1_data['objective'])
                self.assertEqual(item['version'], self.prompt1_data['version'])

    def test_api_get_prompt_exists(self):
        response = self.client.get(f'/api/prompts/{self.prompt1_filename}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['filename'], self.prompt1_filename)
        self.assertEqual(data['prompt_data']['objective'], self.prompt1_data['objective'])
        self.assertEqual(data['prompt_data']['version'], self.prompt1_data['version'])

    def test_api_get_prompt_not_found(self):
        response = self.client.get('/api/prompts/non_existent_prompt.json')
        self.assertEqual(response.status_code, 404)

    def test_api_create_prompt(self):
        new_prompt_data = {
            "__type__": "PiaAGIPrompt",
            "filename": "new_prompt_full.json",
            "objective": "Newly Created Full Prompt Objective",
            "version": "0.6", "author": "Create Full Test", "initiate_interaction": "Start full",
            "system_rules": {"__type__": "SystemRules", "language": "fr", "output_format": "XML"},
            "requirements": {"__type__": "Requirements", "goal": "Full prompt goal"},
            "executors": {
                "__type__": "Executors",
                "role": {
                    "__type__": "Role", "name": "TestRoleFull", "profile": "A comprehensively defined role.",
                    "cognitive_module_configuration": {
                        "__type__": "CognitiveModuleConfiguration",
                        "personality_config": {"__type__": "PersonalityConfig", "ocean_openness": 0.8},
                        "motivational_bias_config": {"__type__": "MotivationalBias", "biases": {"curiosity": "high"}},
                        "emotional_profile_config": {"__type__": "EmotionalProfile", "baseline_valence": "positive"},
                        "learning_module_config": {"__type__": "LearningModuleConfig", "primary_learning_mode": " unsupervised"}
                    }
                }
            }
            # Add other fields as null or with default __type__ if needed for full completeness
        }
        response = self.client.post('/api/prompts', json=new_prompt_data_full)
        self.assertEqual(response.status_code, 201, response.get_json())
        data = json.loads(response.data)
        self.assertEqual(data['filename'], "new_prompt_full.json")

        loaded_prompt = load_template(os.path.join(self.test_prompt_dir, "new_prompt_full.json"))
        self.assertIsNotNone(loaded_prompt)
        self.assertEqual(loaded_prompt.objective, new_prompt_data_full['objective'])
        self.assertIsNotNone(loaded_prompt.executors)
        self.assertIsNotNone(loaded_prompt.executors.role)
        self.assertIsNotNone(loaded_prompt.executors.role.cognitive_module_configuration)
        self.assertEqual(loaded_prompt.executors.role.cognitive_module_configuration.personality_config.ocean_openness, 0.8)

    def test_api_create_prompt_malformed_nested_type(self):
        malformed_data = {
            "__type__": "PiaAGIPrompt", "filename": "malformed_prompt.json",
            "objective": "Malformed Test", "version": "0.1",
            "executors": {
                "__type__": "Executors",
                "role": {
                    "__type__": "Role", "name": "MalformedRole",
                    "cognitive_module_configuration": {
                        "__type__": "CognitiveModuleConfiguration",
                        "personality_config": {"ocean_openness": 0.5} # Missing __type__ for PersonalityConfig
                    }
                }
            }
        }
        response = self.client.post('/api/prompts', json=malformed_data)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Invalid prompt data structure", data.get("error", ""))


    def test_api_create_prompt_bad_request(self):
        response = self.client.post('/api/prompts', data="not json") # Not JSON
        self.assertEqual(response.status_code, 400)

        response = self.client.post('/api/prompts', json={}) # Missing filename/objective for filename derivation
        self.assertEqual(response.status_code, 400)


    def test_api_create_prompt_conflict(self):
        conflict_data = {
            "__type__": "PiaAGIPrompt",
            "filename": self.prompt1_filename, # Existing filename
            "objective": "Conflict Objective",
            "version": "3.0"
        }
        response = self.client.post('/api/prompts', json=conflict_data)
        self.assertEqual(response.status_code, 409)

    def test_api_update_prompt_exists(self):
        update_data = {
            "__type__": "PiaAGIPrompt",
            "__type__": "PiaAGIPrompt", # Ensure __type__ is at the root
            "objective": "Updated Full Prompt Objective",
            "version": "1.0-updated-full",
            "author": "Test User Updated Full",
            "initiate_interaction": "Start prompt 1 updated full",
            "system_rules": {"__type__": "SystemRules", "language": "es"},
            "requirements": {"__type__": "Requirements", "goal": "Updated full goal"},
            "executors": {
                "__type__": "Executors",
                "role": {
                    "__type__": "Role", "name": "UpdatedTestRoleFull",
                    "cognitive_module_configuration": {
                        "__type__": "CognitiveModuleConfiguration",
                        "personality_config": {"__type__": "PersonalityConfig", "ocean_openness": 0.2},
                        "motivational_bias_config": {"__type__": "MotivationalBias", "biases": {"novelty_seeking": "extreme"}}
                        # Ensure other cog configs are included or nulled if that's intended behavior
                    }
                }
            }
        }
        response = self.client.put(f'/api/prompts/{self.prompt1_filename}', json=update_data_full)
        self.assertEqual(response.status_code, 200, response.get_json())

        loaded_prompt = load_template(os.path.join(self.test_prompt_dir, self.prompt1_filename))
        self.assertIsNotNone(loaded_prompt)
        self.assertEqual(loaded_prompt.objective, update_data_full['objective'])
        self.assertEqual(loaded_prompt.version, update_data_full['version'])
        self.assertIsNotNone(loaded_prompt.executors.role.cognitive_module_configuration.motivational_bias_config)
        self.assertEqual(loaded_prompt.executors.role.cognitive_module_configuration.motivational_bias_config.biases.get("novelty_seeking"), "extreme")

    def test_api_update_prompt_not_found(self):
        response = self.client.put('/api/prompts/non_existent_prompt.json', json=self.prompt1_data)
        self.assertEqual(response.status_code, 404)

    def test_api_delete_prompt_exists(self):
        response = self.client.delete(f'/api/prompts/{self.prompt1_filename}')
        self.assertEqual(response.status_code, 200) # Or 204 if no content returned
        self.assertFalse(os.path.exists(os.path.join(self.test_prompt_dir, self.prompt1_filename)))

    def test_api_delete_prompt_not_found(self):
        response = self.client.delete('/api/prompts/non_existent_prompt.json')
        self.assertEqual(response.status_code, 404)

    def test_api_render_prompt_exists(self):
        response = self.client.get(f'/api/prompts/{self.prompt1_filename}/render')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("markdown", data)
        self.assertIn(self.prompt1_data['objective'], data['markdown']) # Check if objective is in rendered output

    def test_api_render_prompt_not_found(self):
        response = self.client.get('/api/prompts/non_existent_prompt.json/render')
        self.assertEqual(response.status_code, 404)

    # --- Test HTML Serving Routes ---
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
        self.assertIn(self.prompt1_data['objective'].encode(), response.data) # Check if objective is in form

    def test_route_edit_prompt_view_not_found(self):
        response = self.client.get('/edit/non_existent_prompt.json', follow_redirects=True)
        self.assertEqual(response.status_code, 200) # After redirect to dashboard
        self.assertIn(b"Error: Prompt file 'non_existent_prompt.json' not found.", response.data) # Check flashed message

    def test_route_view_prompt_exists(self):
        response = self.client.get(f'/view/{self.prompt1_filename}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"Prompt Details: {self.prompt1_filename}".encode(), response.data)

    def test_route_view_prompt_not_found(self):
        response = self.client.get('/view/non_existent_prompt.json', follow_redirects=True)
        self.assertEqual(response.status_code, 200) # After redirect to dashboard
        self.assertIn(b"Error: Prompt file 'non_existent_prompt.json' not found.", response.data)

    # --- Curriculum Test Methods ---
    def test_api_list_curricula(self):
        response = self.client.get('/api/curricula')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['filename'], self.curriculum1_filename)
        self.assertEqual(data[0]['name'], self.curriculum1_data['name'])
        self.assertEqual(data[0]['version'], self.curriculum1_data['version'])

    def test_api_get_curriculum_exists(self):
        response = self.client.get(f'/api/curricula/{self.curriculum1_filename}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['filename'], self.curriculum1_filename)
        # Compare a few key fields from the curriculum_data
        self.assertEqual(data['curriculum_data']['name'], self.curriculum1_data['name'])
        self.assertEqual(len(data['curriculum_data']['steps']), len(self.curriculum1_data['steps']))
        self.assertEqual(data['curriculum_data']['steps'][0]['name'], self.curriculum1_data['steps'][0]['name'])

    def test_api_get_curriculum_not_found(self):
        response = self.client.get('/api/curricula/non_existent.curriculum.json')
        self.assertEqual(response.status_code, 404)

    def test_api_render_curriculum_exists(self):
        response = self.client.get(f'/api/curricula/{self.curriculum1_filename}/render')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("markdown", data)
        self.assertTrue(len(data['markdown']) > 0)
        self.assertIn(self.curriculum1_data['name'], data['markdown'])
        self.assertIn(self.curriculum1_data['steps'][0]['name'], data['markdown'])

    def test_api_render_curriculum_not_found(self):
        response = self.client.get('/api/curricula/non_existent.curriculum.json/render')
        self.assertEqual(response.status_code, 404)

    def test_route_view_curriculum_exists(self):
        response = self.client.get(f'/curriculum/view/{self.curriculum1_filename}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.curriculum1_data['name'].encode(), response.data)
        self.assertIn(self.curriculum1_data['steps'][0]['name'].encode(), response.data)


    def test_route_view_curriculum_not_found(self):
        response = self.client.get('/curriculum/view/non_existent.curriculum.json', follow_redirects=True)
        self.assertEqual(response.status_code, 200) # After redirect
        self.assertIn(b"Error: Curriculum file 'non_existent.curriculum.json' not found.", response.data)


if __name__ == '__main__':
    # This is to ensure that if test_app.py is run directly, it uses the correct PROMPT_DIR.
    # However, typically tests are run via `python -m unittest discover`
    # The setUp method handles PROMPT_DIR patching for the app instance during tests.
    unittest.main()
