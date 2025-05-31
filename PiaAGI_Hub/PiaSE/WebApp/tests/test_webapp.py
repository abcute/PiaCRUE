import unittest
import sys
import os

# Minimal path adjustment - assumes WebApp is in PYTHONPATH or test is run from PiaSE/WebApp
# For robust testing, PYTHONPATH should be configured correctly in the execution environment.
# test_webapp.py is in PiaAGI_Hub/PiaSE/WebApp/tests/
# We want to add PiaAGI_Hub/PiaSE/WebApp/ to sys.path to import 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app import app
except ImportError as e_main:
    print(f"Initial import failed: {e_main}")
    # Fallback: Adjust path assuming PiaAGI_Hub is the root for PiaAGI_Hub.PiaSE.WebApp.app
    # This means adding the parent of PiaAGI_Hub to sys.path
    # Current __file__ is /app/PiaAGI_Hub/PiaSE/WebApp/tests/test_webapp.py
    current_file_dir = os.path.dirname(os.path.abspath(__file__)) # .../WebApp/tests
    webapp_dir = os.path.dirname(current_file_dir) # .../WebApp
    piase_dir = os.path.dirname(webapp_dir) # .../PiaSE
    pia_agi_hub_dir = os.path.dirname(piase_dir) # .../PiaAGI_Hub
    project_root = os.path.dirname(pia_agi_hub_dir) # /app

    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        print(f"Added project root {project_root} to sys.path for fallback import.")

    # Now, the import should be relative to a point where PiaAGI_Hub is visible
    # But app.py itself is not a module in that sense, it's a script.
    # For Flask testing, it's common to import the 'app' object directly from the script.
    # The initial sys.path.insert to '..' should make 'app.py' importable as 'app'.
    # If that fails, it means the PiaSE modules used by app.py are not found.

    # Let's ensure the PiaSE imports within app.py can work by adding project_root
    # Then re-try importing 'app' from the WebApp directory.
    # The app.py already has its own sys.path manipulation, this is for the test runner.

    # The key is that 'app.py' needs to be found, AND 'app.py' itself needs to find 'PiaAGI_Hub.PiaSE...'
    # The second part is handled by app.py's own sys.path logic.
    # The first part (test_webapp.py finding app.py) is handled by adding '..' to path.
    try:
        from app import app
    except ImportError as e_fallback:
        print(f"Fallback import also failed: {e_fallback}")
        print("Ensure that PiaAGI_Hub (the parent of PiaSE) is in your PYTHONPATH, or that tests are run with a configured environment.")
        raise # Re-raise the last error if all attempts fail

class WebAppTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Ensure 'app' is imported before tests run, or skip all tests.
        if 'app' not in globals():
            raise unittest.SkipTest("Flask 'app' object could not be imported. Skipping WebApp tests.")

        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False # Example if using Flask-WTF; not used here but good practice
        cls.client = app.test_client()

        # app.root_path is typically the directory containing the app module (WebApp)
        cls.static_frames_path = os.path.join(app.root_path, 'static', 'frames')


    def test_index_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"PiaSE Scenario Runner", response.data) # Check for bytes content

    def test_run_scenario_post_succeeds_and_creates_frames_dir(self):
        initial_run_dirs_count = 0
        # Ensure the base 'frames' directory exists before counting subdirectories
        if not os.path.exists(self.static_frames_path):
            os.makedirs(self.static_frames_path, exist_ok=True) # Create if it doesn't exist

        if os.path.exists(self.static_frames_path):
            try:
                initial_run_dirs_count = len([
                    name for name in os.listdir(self.static_frames_path)
                    if os.path.isdir(os.path.join(self.static_frames_path, name))
                ])
            except FileNotFoundError:
                 pass

        response = self.client.post('/run_scenario')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Simulation Results", response.data) # Check for bytes content

        final_run_dirs_count = 0
        if os.path.exists(self.static_frames_path):
            final_run_dirs_count = len([
                name for name in os.listdir(self.static_frames_path)
                if os.path.isdir(os.path.join(self.static_frames_path, name))
            ])

        self.assertGreater(final_run_dirs_count, initial_run_dirs_count,
                           f"A new run directory should have been created in {self.static_frames_path}. Initial: {initial_run_dirs_count}, Final: {final_run_dirs_count}")

if __name__ == '__main__':
    unittest.main()
