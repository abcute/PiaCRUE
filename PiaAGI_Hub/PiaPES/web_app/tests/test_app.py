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
if PES_WEB_APP_DIR not in sys.path:
     sys.path.insert(0, PES_WEB_APP_DIR) # For PiaAGI_Hub.PiaPES.web_app.app


from PiaAGI_Hub.PiaPES.web_app.app import app
from PiaAGI_Hub.PiaPES.prompt_engine_mvp import (
    PiaAGIPrompt, SystemRules, Requirements, Executors, Role,
    save_template, load_template, pia_agi_object_hook
)


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
            "filename": "new_prompt.json", # Filename provided in body
            "objective": "Newly Created Prompt Objective",
            "version": "0.5",
            "author": "Create Test",
            "initiate_interaction": "Hello new world"
        }
        response = self.client.post('/api/prompts', json=new_prompt_data)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['filename'], "new_prompt.json") # Sanitized name
        self.assertTrue(os.path.exists(os.path.join(self.test_prompt_dir, "new_prompt.json")))

        loaded_prompt = load_template(os.path.join(self.test_prompt_dir, "new_prompt.json"))
        self.assertEqual(loaded_prompt.objective, new_prompt_data['objective'])


    def test_api_create_prompt_bad_request(self):
        response = self.client.post('/api/prompts', data="not json")
        self.assertEqual(response.status_code, 400)

        response = self.client.post('/api/prompts', json={}) # Missing filename/objective
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
            "objective": "Updated Prompt 1 Objective",
            "version": "1.0-updated", # Original was 1.0
            "author": "Test User Updated",
            "initiate_interaction": "Start prompt 1 updated"
            # Other fields might be nullified if not provided, depending on object hook logic
            # For a robust update, usually all fields are provided by client.
        }
        response = self.client.put(f'/api/prompts/{self.prompt1_filename}', json=update_data)
        self.assertEqual(response.status_code, 200)

        loaded_prompt = load_template(os.path.join(self.test_prompt_dir, self.prompt1_filename))
        self.assertEqual(loaded_prompt.objective, update_data['objective'])
        self.assertEqual(loaded_prompt.version, update_data['version'])
        self.assertEqual(loaded_prompt.author, update_data['author']) # Check if original author got updated

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

if __name__ == '__main__':
    # This is to ensure that if test_app.py is run directly, it uses the correct PROMPT_DIR.
    # However, typically tests are run via `python -m unittest discover`
    # The setUp method handles PROMPT_DIR patching for the app instance during tests.
    unittest.main()
