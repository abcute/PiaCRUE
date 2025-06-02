import os
from flask import Flask, request, jsonify, abort
from dotenv import load_dotenv
from openai import OpenAI, APIError, AuthenticationError, RateLimitError, APIConnectionError
from flask_cors import CORS
import sys # Added for path modification
import configparser # Added for LLM configuration
import logging # Added for logging
import json # For PiaPES integration
import re # For PiaPES sanitize_filename

# --- Path Setup ---
# Add PiaAGI_Hub to sys.path to allow CML imports
# This assumes app.py is in PiaAGI_Hub/WebApp/backend/
# Adjust if the directory structure is different or if CML becomes a proper package
try:
# Path to PiaAGI_Hub directory from the current file's location (WebApp/backend)
path_to_piaagi_hub = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if path_to_piaagi_hub not in sys.path:
    sys.path.insert(0, path_to_piaagi_hub)

# Add PiaPES directory to sys.path for prompt_engine_mvp
PES_DIR = os.path.join(path_to_piaagi_hub, 'PiaPES')
if PES_DIR not in sys.path:
    sys.path.insert(0, PES_DIR)

# Add PiaSE directory to sys.path
PIASE_DIR = os.path.join(path_to_piaagi_hub, 'PiaSE')
if PIASE_DIR not in sys.path:
    # This typically would be PIASE_DIR itself, but if utils, core_engine are directly under it:
    sys.path.insert(0, PIASE_DIR)
    # If PiaSE components are within a src dir inside PiaSE, adjust accordingly e.g.
    # sys.path.insert(0, os.path.join(PIASE_DIR, 'src'))


# --- Matplotlib Configuration (early) ---
import matplotlib
matplotlib.use('Agg') # Use 'Agg' backend for Matplotlib to prevent GUI issues in server environment
import matplotlib.pyplot as plt


# --- CML Imports ---
try:
    from PiaCML.concrete_perception_module import ConcretePerceptionModule
    from PiaCML.concrete_emotion_module import ConcreteEmotionModule
    from PiaCML.concrete_motivational_system_module import ConcreteMotivationalSystemModule
    from PiaCML.concrete_working_memory_module import ConcreteWorkingMemoryModule
    logger.info("CML modules imported successfully.")
except ImportError as e:
    logger.error(f"Error importing CML modules: {e}. Using dummy classes. Ensure PiaAGI_Hub is in PYTHONPATH or sys.path is correct.")
    class ConcretePerceptionModule: pass
    class ConcreteEmotionModule: pass
    class ConcreteMotivationalSystemModule: pass
    class ConcreteWorkingMemoryModule: pass
# --- End CML Imports ---

# --- PiaPES Imports ---
try:
    from prompt_engine_mvp import (
        PiaAGIPrompt, BaseElement, DevelopmentalCurriculum,
        save_template, load_template,
        pia_agi_object_hook, PiaAGIEncoder
    )
    logger.info("PiaPES prompt_engine_mvp components imported successfully.")
except ImportError as e:
    logger.error(f"Error importing from prompt_engine_mvp: {e}. PiaPES functionalities will be unavailable. Ensure PiaPES is in sys.path.")
    # Define dummy classes if import fails, so app can still run and show other routes
    class PiaAGIPrompt: pass
    class BaseElement: pass
    class DevelopmentalCurriculum: pass
    class PiaAGIEncoder(json.JSONEncoder): pass # Minimal fallback
    def save_template(obj, path): logger.error("PiaPES dummy save_template called.")
    def load_template(path): logger.error("PiaPES dummy load_template called."); return None
    def pia_agi_object_hook(dct): logger.error("PiaPES dummy pia_agi_object_hook called."); return dct
# --- End PiaPES Imports ---

# --- PiaSE Imports ---
import time # For PiaSE run folder naming
try:
    from core_engine.basic_engine import BasicSimulationEngine # PiaSE/core_engine/basic_engine.py
    from environments.grid_world import GridWorld # PiaSE/environments/grid_world.py
    from agents.q_learning_agent import QLearningAgent # PiaSE/agents/q_learning_agent.py
    from utils.visualizer import GridWorldVisualizer # PiaSE/utils/visualizer.py
    logger.info("PiaSE components imported successfully.")
except ImportError as e:
    logger.error(f"Error importing PiaSE components: {e}. PiaSE functionalities will be unavailable. Ensure PiaSE is in sys.path and its internal structure is correct (e.g., __init__.py files).")
    # Define dummy classes if import fails
    class BasicSimulationEngine: pass
    class GridWorld: pass
    class QLearningAgent: pass
    class GridWorldVisualizer: pass
# --- End PiaSE Imports ---


# Load environment variables from .env file (if it exists)
load_dotenv()

app = Flask(__name__, static_folder='static') # Ensure static_folder is explicitly set
CORS(app) # Enable CORS for all routes
if 'PiaAGIEncoder' in globals(): # Check if PiaAGIEncoder was successfully imported
    app.json_encoder = PiaAGIEncoder # Use custom encoder for PiaPES objects
else:
    logger.warning("PiaAGIEncoder not available. Using default JSON encoder.")


# --- Setup Logging ---
logging.basicConfig(level=logging.INFO) # Ensure logging is configured early
logger = logging.getLogger(__name__) # app.logger can be used too once app is created

# --- LLM Configuration ---
llm_config = configparser.ConfigParser()
LLM_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'llm_config.ini')
if os.path.exists(LLM_CONFIG_PATH):
    llm_config.read(LLM_CONFIG_PATH)
    logger.info(f"LLM configuration loaded from {LLM_CONFIG_PATH}")
else:
    logger.warning(f"LLM configuration file not found at {LLM_CONFIG_PATH}. API keys must be provided in requests.")

def get_llm_api_key(provider='OpenAI'):
    """Retrieves API key from llm_config.ini for the given provider."""
    if not llm_config:
        return None
    try:
        return llm_config.get(provider, 'API_KEY', fallback=None)
    except configparser.NoSectionError:
        logger.warning(f"Provider section '{provider}' not found in LLM config.")
        return None
    except configparser.NoOptionError:
        logger.warning(f"API_KEY not found for provider '{provider}' in LLM config.")
        return None

def get_default_llm_model(provider='OpenAI'):
    """Retrieves default model name from llm_config.ini."""
    if not llm_config:
        return 'gpt-3.5-turbo' # Fallback default
    try:
        model = llm_config.get(provider, 'MODEL_NAME', fallback=None)
        if model:
            return model
        return llm_config.get('DEFAULT', 'DEFAULT_MODEL_NAME', fallback='gpt-3.5-turbo')
    except (configparser.NoSectionError, configparser.NoOptionError):
        logger.warning(f"Default model or provider section not fully configured in LLM config. Using fallback 'gpt-3.5-turbo'.")
        return 'gpt-3.5-turbo'

# --- CML Module Instantiations ---
# For V1 WebApp, using global instances. Consider session-based or request-based for more advanced use.
perception_module_instance = ConcretePerceptionModule() if 'ConcretePerceptionModule' in globals() else None
emotion_module_instance = ConcreteEmotionModule() if 'ConcreteEmotionModule' in globals() else None
motivational_system_instance = ConcreteMotivationalSystemModule() if 'ConcreteMotivationalSystemModule' in globals() else None
working_memory_instance = ConcreteWorkingMemoryModule(capacity=5) if 'ConcreteWorkingMemoryModule' in globals() else None
# --- End CML Module Instantiations ---

# --- PiaPES Configuration ---
PES_FILES_DIR = os.path.join(os.path.dirname(__file__), 'pes_files')
if not os.path.exists(PES_FILES_DIR):
    try:
        os.makedirs(PES_FILES_DIR)
        logger.info(f"Created directory for PiaPES files: {PES_FILES_DIR}")
    except OSError as e:
        logger.error(f"Could not create directory {PES_FILES_DIR}: {e}")
# --- End PiaPES Configuration ---

# --- PiaSE Configuration ---
# Base directory for serving files via /static/piase_runs/<run_id>/image.png
PIASE_RUNS_STATIC_DIR = 'piase_runs'
# Absolute path for saving files on the server
PIASE_RUNS_OUTPUT_DIR_ABSOLUTE = os.path.join(app.static_folder, PIASE_RUNS_STATIC_DIR)

if not os.path.exists(PIASE_RUNS_OUTPUT_DIR_ABSOLUTE):
    try:
        os.makedirs(PIASE_RUNS_OUTPUT_DIR_ABSOLUTE)
        logger.info(f"Created directory for PiaSE run outputs: {PIASE_RUNS_OUTPUT_DIR_ABSOLUTE}")
    except OSError as e:
        logger.error(f"Could not create directory {PIASE_RUNS_OUTPUT_DIR_ABSOLUTE}: {e}")
# --- End PiaSE Configuration ---


def sanitize_filename(name):
    """Sanitizes a string to be a safe filename component for PiaPES files."""
    name = str(name) # Ensure it's a string
    # Remove characters that are not alphanumeric, whitespace, hyphen, or underscore
    name = re.sub(r'[^\w\s-]', '', name).strip()
    # Replace whitespace and multiple hyphens/underscores with a single hyphen
    name = re.sub(r'[-\s_]+', '-', name)
    # Remove leading/trailing hyphens and dots
    name = name.strip('-.')
    # Prevent names that are just dots or empty after sanitization
    if not name or all(c == '.' for c in name):
        name = "unnamed_file" # Generic fallback
    return name
    # .json or .curriculum.json will be appended by the calling function

@app.route('/api/hello')
def hello_world():
    return jsonify({'message': 'Hello from Flask backend!'})

@app.route('/api/process_prompt', methods=['POST'])
def process_prompt():
    try:
        data = request.get_json()
        if not data:
            logger.warning("Received empty or invalid JSON payload for /api/process_prompt")
            return jsonify({"error": "Invalid JSON payload"}), 400

        prompt_content = data.get('prompt')
        test_question = data.get('testQuestion')
        
        # LLM configuration priority: Request -> Config File -> Default
        request_api_key = data.get('apiKey')
        config_api_key = get_llm_api_key() # Assuming OpenAI by default for this endpoint

        final_api_key = request_api_key if request_api_key else config_api_key

        if not final_api_key:
            logger.error("API key is missing. Not provided in request and not found in llm_config.ini.")
            return jsonify({"error": "API key is missing. Provide it in the request or configure it in llm_config.ini."}), 400
        
        # Model selection: Request -> Config File (provider specific or default) -> Hardcoded default
        llm_provider = llm_config.get('DEFAULT', 'LLM_PROVIDER', fallback='OpenAI') # Get default provider
        default_model_from_config = get_default_llm_model(provider=llm_provider)
        llm_model = data.get('llmModel', default_model_from_config)


        if not prompt_content: return jsonify({"error": "Prompt content is missing"}), 400
        if not test_question: return jsonify({"error": "Test question is missing"}), 400

        client = OpenAI(api_key=final_api_key)
        completion = client.chat.completions.create(
            model=llm_model,
            messages=[
                {"role": "system", "content": prompt_content},
                {"role": "user", "content": test_question}
            ]
        )
        llm_response = completion.choices[0].message.content
        return jsonify({"response": llm_response})

    except AuthenticationError as e:
        logger.error(f"OpenAI Authentication Error: {e}")
        return jsonify({"error": "OpenAI API Key is invalid or expired."}), 401
    except RateLimitError as e:
        logger.error(f"OpenAI Rate Limit Error: {e}")
        return jsonify({"error": "OpenAI API rate limit exceeded. Please try again later."}), 429
    except APIConnectionError as e:
        logger.error(f"OpenAI API Connection Error: {e}")
        return jsonify({"error": "Could not connect to OpenAI. Please check your network."}), 500
    except APIError as e:
        logger.error(f"OpenAI API Error: {e}")
        return jsonify({"error": f"An OpenAI API error occurred: {e}"}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred in /api/process_prompt: {e}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# --- Routes for ConcretePerceptionModule ---
@app.route('/cml/perception/process', methods=['POST'])
def cml_perception_process():
    if not perception_module_instance:
        logger.error("PerceptionModule not initialized for /cml/perception/process")
        return jsonify({"error": "PerceptionModule not initialized"}), 500
    try:
        data = request.json
        raw_input = data.get('raw_input')
        modality = data.get('modality')
        context = data.get('context', {})
        result = perception_module_instance.process_sensory_input(raw_input, modality, context)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in /cml/perception/process: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/cml/perception/status', methods=['GET'])
def cml_perception_status():
    if not perception_module_instance:
        logger.error("PerceptionModule not initialized for /cml/perception/status")
        return jsonify({"error": "PerceptionModule not initialized"}), 500
    try:
        return jsonify(perception_module_instance.get_module_status())
    except Exception as e:
        logger.error(f"Error in /cml/perception/status: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# --- Routes for ConcreteEmotionModule ---
@app.route('/cml/emotion/appraise', methods=['POST'])
def cml_emotion_appraise():
    if not emotion_module_instance:
        logger.error("EmotionModule not initialized for /cml/emotion/appraise")
        return jsonify({"error": "EmotionModule not initialized"}), 500
    try:
        data = request.json
        event_info = data.get('event_info')
        context = data.get('context', {})
        result = emotion_module_instance.appraise_situation(event_info, context)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in /cml/emotion/appraise: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/cml/emotion/current', methods=['GET'])
def cml_emotion_current():
    if not emotion_module_instance:
        logger.error("EmotionModule not initialized for /cml/emotion/current")
        return jsonify({"error": "EmotionModule not initialized"}), 500
    try:
        return jsonify(emotion_module_instance.get_current_emotion())
    except Exception as e:
        logger.error(f"Error in /cml/emotion/current: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/cml/emotion/express', methods=['GET']) # Or POST if context is sent
def cml_emotion_express():
    if not emotion_module_instance:
        logger.error("EmotionModule not initialized for /cml/emotion/express")
        return jsonify({"error": "EmotionModule not initialized"}), 500
    try:
        # context = request.json.get('context', {}) if request.is_json else {} # if context can be sent
        return jsonify(emotion_module_instance.express_emotion(context=None))
    except Exception as e:
        logger.error(f"Error in /cml/emotion/express: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/cml/emotion/status', methods=['GET'])
def cml_emotion_status():
    if not emotion_module_instance:
        logger.error("EmotionModule not initialized for /cml/emotion/status")
        return jsonify({"error": "EmotionModule not initialized"}), 500
    try:
        return jsonify(emotion_module_instance.get_module_status())
    except Exception as e:
        logger.error(f"Error in /cml/emotion/status: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# --- Routes for ConcreteMotivationalSystemModule ---
@app.route('/cml/motivation/manage', methods=['POST'])
def cml_motivation_manage():
    if not motivational_system_instance:
        logger.error("MotivationalSystemModule not initialized for /cml/motivation/manage")
        return jsonify({"error": "MotivationalSystemModule not initialized"}), 500
    try:
        data = request.json
        action = data.get('action')
        goal_data = data.get('goal_data', {})
        result = motivational_system_instance.manage_goals(action, goal_data)
        return jsonify(result) if isinstance(result, (bool, str, list, dict)) else (jsonify(result) if result is not None else jsonify({"status": "ok_no_return"}) )
    except Exception as e:
        logger.error(f"Error in /cml/motivation/manage: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/cml/motivation/active_goals', methods=['GET'])
def cml_motivation_active_goals():
    if not motivational_system_instance:
        logger.error("MotivationalSystemModule not initialized for /cml/motivation/active_goals")
        return jsonify({"error": "MotivationalSystemModule not initialized"}), 500
    try:
        N = request.args.get('N', default=0, type=int)
        min_priority = request.args.get('min_priority', default=0.0, type=float)
        result = motivational_system_instance.get_active_goals(N, min_priority)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in /cml/motivation/active_goals: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/cml/motivation/update_state', methods=['POST'])
def cml_motivation_update_state():
    if not motivational_system_instance:
        logger.error("MotivationalSystemModule not initialized for /cml/motivation/update_state")
        return jsonify({"error": "MotivationalSystemModule not initialized"}), 500
    try:
        data = request.json
        result = motivational_system_instance.update_motivation_state(data)
        return jsonify({"success": result})
    except Exception as e:
        logger.error(f"Error in /cml/motivation/update_state: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/cml/motivation/status', methods=['GET'])
def cml_motivation_status():
    if not motivational_system_instance:
        logger.error("MotivationalSystemModule not initialized for /cml/motivation/status")
        return jsonify({"error": "MotivationalSystemModule not initialized"}), 500
    try:
        return jsonify(motivational_system_instance.get_module_status())
    except Exception as e:
        logger.error(f"Error in /cml/motivation/status: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# --- Routes for ConcreteWorkingMemoryModule ---
@app.route('/cml/wm/add_item', methods=['POST'])
def cml_wm_add_item():
    if not working_memory_instance:
        logger.error("WorkingMemoryModule not initialized for /cml/wm/add_item")
        return jsonify({"error": "WorkingMemoryModule not initialized"}), 500
    try:
        data = request.json
        item_content = data.get('item_content')
        salience = data.get('salience', 0.5)
        context = data.get('context', {})
        item_id = working_memory_instance.add_item_to_workspace(item_content, salience, context)
        return jsonify({"item_id": item_id, "current_size": len(working_memory_instance.get_workspace_contents())})
    except Exception as e:
        logger.error(f"Error in /cml/wm/add_item: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/cml/wm/remove_item', methods=['POST'])
def cml_wm_remove_item():
    if not working_memory_instance:
        logger.error("WorkingMemoryModule not initialized for /cml/wm/remove_item")
        return jsonify({"error": "WorkingMemoryModule not initialized"}), 500
    try:
        data = request.json
        item_id = data.get('item_id')
        success = working_memory_instance.remove_item_from_workspace(item_id)
        return jsonify({"success": success, "current_size": len(working_memory_instance.get_workspace_contents())})
    except Exception as e:
        logger.error(f"Error in /cml/wm/remove_item: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/cml/wm/contents', methods=['GET'])
def cml_wm_contents():
    if not working_memory_instance:
        logger.error("WorkingMemoryModule not initialized for /cml/wm/contents")
        return jsonify({"error": "WorkingMemoryModule not initialized"}), 500
    try:
        return jsonify(working_memory_instance.get_workspace_contents())
    except Exception as e:
        logger.error(f"Error in /cml/wm/contents: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/cml/wm/set_focus', methods=['POST'])
def cml_wm_set_focus():
    if not working_memory_instance:
        logger.error("WorkingMemoryModule not initialized for /cml/wm/set_focus")
        return jsonify({"error": "WorkingMemoryModule not initialized"}), 500
    try:
        data = request.json
        item_id = data.get('item_id')
        success = working_memory_instance.set_active_focus(item_id)
        return jsonify({"success": success, "current_focus": working_memory_instance.get_active_focus()})
    except Exception as e:
        logger.error(f"Error in /cml/wm/set_focus: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/cml/wm/get_focus', methods=['GET'])
def cml_wm_get_focus():
    if not working_memory_instance:
        logger.error("WorkingMemoryModule not initialized for /cml/wm/get_focus")
        return jsonify({"error": "WorkingMemoryModule not initialized"}), 500
    try:
        return jsonify(working_memory_instance.get_active_focus())
    except Exception as e:
        logger.error(f"Error in /cml/wm/get_focus: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/cml/wm/manage_capacity', methods=['POST']) # Explicit call if needed
def cml_wm_manage_capacity():
    if not working_memory_instance:
        logger.error("WorkingMemoryModule not initialized for /cml/wm/manage_capacity")
        return jsonify({"error": "WorkingMemoryModule not initialized"}), 500
    try:
        data = request.json
        new_item_salience = data.get('new_item_salience') # Optional
        working_memory_instance.manage_workspace_capacity_and_coherence(new_item_salience)
        return jsonify({"status": "capacity_managed", "current_size": len(working_memory_instance.get_workspace_contents())})
    except Exception as e:
        logger.error(f"Error in /cml/wm/manage_capacity: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/cml/wm/handle_forgetting', methods=['POST']) # Explicit call if needed
def cml_wm_handle_forgetting():
    if not working_memory_instance:
        logger.error("WorkingMemoryModule not initialized for /cml/wm/handle_forgetting")
        return jsonify({"error": "WorkingMemoryModule not initialized"}), 500
    try:
        data = request.json
        strategy = data.get('strategy', 'default')
        working_memory_instance.handle_forgetting(strategy)
        return jsonify({"status": "forgetting_handled", "strategy": strategy, "contents": working_memory_instance.get_workspace_contents()})
    except Exception as e:
        logger.error(f"Error in /cml/wm/handle_forgetting: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/cml/wm/status', methods=['GET'])
def cml_wm_status():
    if not working_memory_instance:
        logger.error("WorkingMemoryModule not initialized for /cml/wm/status")
        return jsonify({"error": "WorkingMemoryModule not initialized"}), 500
    try:
        return jsonify(working_memory_instance.get_module_status())
    except Exception as e:
        logger.error(f"Error in /cml/wm/status: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# --- PiaPES API Endpoints ---

# Check if critical PiaPES components are available before defining routes
if 'PiaAGIPrompt' not in globals() or 'load_template' not in globals() or 'save_template' not in globals() or 'DevelopmentalCurriculum' not in globals():
    logger.error("Core PiaPES classes not imported. PiaPES API endpoints will not be available.")
else:
    @app.route('/api/pes/prompts', methods=['GET'])
    def api_list_pes_prompts():
        try:
            prompt_infos = []
            if not os.path.exists(PES_FILES_DIR):
                logger.warning(f"PiaPES files directory {PES_FILES_DIR} not found.")
                return jsonify([]) # Return empty list if dir doesn't exist

            for filename in os.listdir(PES_FILES_DIR):
                if filename.endswith('.json') and not filename.endswith('.curriculum.json'):
                    filepath = os.path.join(PES_FILES_DIR, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            name = data.get('objective', data.get('name', filename))
                            version = data.get('version', 'N/A')
                            prompt_infos.append({
                                "filename": filename,
                                "name": name,
                                "version": version
                            })
                    except Exception as e:
                        logger.warning(f"Could not parse metadata from PiaPES prompt {filename}: {e}")
                        prompt_infos.append({"filename": filename, "name": filename, "version": "Error reading"})
            return jsonify(prompt_infos)
        except Exception as e:
            logger.error(f"Error listing PiaPES prompts: {e}", exc_info=True)
            return jsonify({"error": "Failed to list PiaPES prompts"}), 500

    @app.route('/api/pes/prompts/<path:filename>', methods=['GET'])
    def api_get_pes_prompt(filename):
        if '..' in filename or filename.startswith('/'): # Basic security check
            logger.warning(f"Attempt to access potentially unsafe path: {filename}")
            abort(400, description="Invalid filename.")
            
        filepath = os.path.join(PES_FILES_DIR, filename)
        if not os.path.exists(filepath) or not filename.endswith('.json') or filename.endswith('.curriculum.json'):
            abort(404, description="PiaPES Prompt file not found or invalid type.")

        try:
            prompt = load_template(filepath) # Uses prompt_engine_mvp.load_template
            if prompt and isinstance(prompt, PiaAGIPrompt):
                return jsonify({"filename": filename, "prompt_data": prompt.__dict__})
            else:
                logger.error(f"Failed to load or parse PiaPES prompt template {filename}, or it's not a PiaAGIPrompt instance. Type: {type(prompt)}")
                abort(500, description="Failed to load or parse PiaPES prompt template.")
        except Exception as e:
            logger.error(f"Error getting PiaPES prompt {filename}: {e}", exc_info=True)
            return jsonify({"error": f"Failed to get PiaPES prompt: {str(e)}"}), 500

    @app.route('/api/pes/prompts', methods=['POST'])
    def api_create_pes_prompt():
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        data = request.get_json()
        raw_filename = data.pop('filename', None) # Pop filename if provided in JSON body

        if raw_filename:
            # Sanitize only the base name, then add .json
            base_name = os.path.splitext(raw_filename)[0]
            filename = sanitize_filename(base_name) + ".json"
        elif data.get('objective'):
            filename = sanitize_filename(data['objective'][:50]) + ".json"
        elif data.get('name'):
            filename = sanitize_filename(data['name'][:50]) + ".json"
        else:
            return jsonify({"error": "Filename must be provided (as 'filename') or derivable from 'objective' or 'name'."}), 400

        filepath = os.path.join(PES_FILES_DIR, filename)
        if os.path.exists(filepath):
            return jsonify({"error": f"PiaPES Prompt file '{filename}' already exists. Use PUT to update."}), 409

        try:
            if '__type__' not in data:
                data['__type__'] = 'PiaAGIPrompt'
            
            reconstructed_json_str = json.dumps(data)
            prompt_object = json.loads(reconstructed_json_str, object_hook=pia_agi_object_hook)

            if not isinstance(prompt_object, PiaAGIPrompt): # Check type after reconstruction
                 logger.error(f"Data for {filename} did not reconstruct into a PiaAGIPrompt. Type: {type(prompt_object)}")
                 return jsonify({"error": "Invalid PiaPES prompt data structure after reconstruction. Ensure correct __type__ hints and fields."}), 400
            
            save_template(prompt_object, filepath) # Uses prompt_engine_mvp.save_template
            return jsonify({"message": f"PiaPES Prompt '{filename}' created successfully.", "filename": filename}), 201
        except (json.JSONDecodeError, TypeError, KeyError, AttributeError) as e:
            logger.error(f"Error processing/reconstructing data for PiaPES prompt {filename}: {e}", exc_info=True)
            return jsonify({"error": f"Invalid prompt data structure. Details: {str(e)}"}), 400
        except Exception as e:
            logger.error(f"Error creating PiaPES prompt {filename}: {e}", exc_info=True)
            return jsonify({"error": f"Failed to create PiaPES prompt: {str(e)}"}), 500

    @app.route('/api/pes/prompts/<path:filename>', methods=['PUT'])
    def api_update_pes_prompt(filename):
        if '..' in filename or filename.startswith('/'):
            logger.warning(f"Attempt to access potentially unsafe path for PUT: {filename}")
            abort(400, description="Invalid filename.")

        filepath = os.path.join(PES_FILES_DIR, filename)
        if not os.path.exists(filepath) or not filename.endswith('.json') or filename.endswith('.curriculum.json'):
            abort(404, description="PiaPES Prompt file not found or invalid type for update.")

        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        data = request.get_json()

        try:
            if '__type__' not in data:
                data['__type__'] = 'PiaAGIPrompt'
            
            reconstructed_json_str = json.dumps(data)
            prompt_object = json.loads(reconstructed_json_str, object_hook=pia_agi_object_hook)

            if not isinstance(prompt_object, PiaAGIPrompt):
                 logger.error(f"Data for updating {filename} did not reconstruct into a PiaAGIPrompt. Type: {type(prompt_object)}")
                 return jsonify({"error": "Invalid PiaPES prompt data structure for update. Ensure correct __type__ hints and fields."}), 400

            save_template(prompt_object, filepath)
            return jsonify({"message": f"PiaPES Prompt '{filename}' updated successfully."})
        except (json.JSONDecodeError, TypeError, KeyError, AttributeError) as e:
            logger.error(f"Error processing/reconstructing data for updating PiaPES prompt {filename}: {e}", exc_info=True)
            return jsonify({"error": f"Invalid prompt data structure for update. Details: {str(e)}"}), 400
        except Exception as e:
            logger.error(f"Error updating PiaPES prompt {filename}: {e}", exc_info=True)
            return jsonify({"error": f"Failed to update PiaPES prompt: {str(e)}"}), 500

    @app.route('/api/pes/prompts/<path:filename>', methods=['DELETE'])
    def api_delete_pes_prompt(filename):
        if '..' in filename or filename.startswith('/'):
            logger.warning(f"Attempt to access potentially unsafe path for DELETE: {filename}")
            abort(400, description="Invalid filename.")

        filepath = os.path.join(PES_FILES_DIR, filename)
        if not os.path.exists(filepath) or not filename.endswith('.json') or filename.endswith('.curriculum.json'):
            abort(404, description="PiaPES Prompt file not found or invalid type for delete.")
        try:
            os.remove(filepath)
            return jsonify({"message": f"PiaPES Prompt '{filename}' deleted successfully."})
        except Exception as e:
            logger.error(f"Error deleting PiaPES prompt {filename}: {e}", exc_info=True)
            return jsonify({"error": f"Failed to delete PiaPES prompt: {str(e)}"}), 500

    @app.route('/api/pes/prompts/<path:filename>/render', methods=['GET'])
    def api_render_pes_prompt_markdown(filename):
        if '..' in filename or filename.startswith('/'):
            logger.warning(f"Attempt to access potentially unsafe path for render: {filename}")
            abort(400, description="Invalid filename.")

        filepath = os.path.join(PES_FILES_DIR, filename)
        if not os.path.exists(filepath) or not filename.endswith('.json') or filename.endswith('.curriculum.json'):
            abort(404, description="PiaPES Prompt file not found or invalid type for render.")
        try:
            prompt = load_template(filepath)
            if prompt and hasattr(prompt, 'render') and callable(getattr(prompt, 'render')):
                markdown_content = prompt.render()
                return jsonify({"filename": filename, "markdown": markdown_content})
            else:
                logger.error(f"Loaded PiaPES object from {filename} is not a valid prompt or has no render method.")
                abort(500, description="Failed to load or parse PiaPES prompt for rendering.")
        except Exception as e:
            logger.error(f"Error rendering PiaPES prompt {filename}: {e}", exc_info=True)
            return jsonify({"error": f"Failed to render PiaPES prompt: {str(e)}"}), 500

    # --- PiaPES Curriculum API Endpoints ---
    @app.route('/api/pes/curricula', methods=['GET'])
    def api_list_pes_curricula():
        try:
            curriculum_files = []
            if not os.path.exists(PES_FILES_DIR):
                logger.warning(f"PiaPES files directory {PES_FILES_DIR} not found.")
                return jsonify([])

            for filename in os.listdir(PES_FILES_DIR):
                if filename.endswith('.curriculum.json'):
                    filepath = os.path.join(PES_FILES_DIR, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            name = data.get('name', filename)
                            version = data.get('version', 'N/A')
                            curriculum_files.append({
                                "filename": filename,
                                "name": name,
                                "version": version
                            })
                    except Exception as e:
                        logger.warning(f"Could not parse metadata from PiaPES curriculum {filename}: {e}")
                        curriculum_files.append({"filename": filename, "name": filename, "version": "Error reading"})
            return jsonify(curriculum_files)
        except Exception as e:
            logger.error(f"Error listing PiaPES curricula: {e}", exc_info=True)
            return jsonify({"error": "Failed to list PiaPES curricula"}), 500

    @app.route('/api/pes/curricula/<path:filename>', methods=['GET'])
    def api_get_pes_curriculum(filename):
        if '..' in filename or filename.startswith('/'):
            logger.warning(f"Attempt to access potentially unsafe path for curriculum GET: {filename}")
            abort(400, description="Invalid filename.")
            
        if not filename.endswith('.curriculum.json'):
            abort(400, description="Invalid PiaPES curriculum filename format.")
        filepath = os.path.join(PES_FILES_DIR, filename)
        if not os.path.exists(filepath):
            abort(404, description="PiaPES Curriculum file not found.")

        try:
            curriculum = load_template(filepath)
            if curriculum and isinstance(curriculum, DevelopmentalCurriculum):
                return jsonify({"filename": filename, "curriculum_data": curriculum.__dict__})
            else:
                logger.error(f"Failed to load or parse PiaPES curriculum {filename}, or it's not a DevelopmentalCurriculum. Type: {type(curriculum)}")
                abort(500, description="Failed to load or parse PiaPES curriculum file, or incorrect type.")
        except Exception as e:
            logger.error(f"Error getting PiaPES curriculum {filename}: {e}", exc_info=True)
            return jsonify({"error": f"Failed to get PiaPES curriculum: {str(e)}"}), 500

    @app.route('/api/pes/curricula/<path:filename>/render', methods=['GET'])
    def api_render_pes_curriculum(filename):
        if '..' in filename or filename.startswith('/'):
            logger.warning(f"Attempt to access potentially unsafe path for curriculum render: {filename}")
            abort(400, description="Invalid filename.")

        if not filename.endswith('.curriculum.json'):
            abort(400, description="Invalid PiaPES curriculum filename format.")
        filepath = os.path.join(PES_FILES_DIR, filename)
        if not os.path.exists(filepath):
            abort(404, description="PiaPES Curriculum file not found.")
        try:
            curriculum = load_template(filepath)
            if curriculum and isinstance(curriculum, DevelopmentalCurriculum) and hasattr(curriculum, 'render'):
                markdown_content = curriculum.render()
                return jsonify({"filename": filename, "markdown": markdown_content})
            else:
                logger.error(f"Loaded PiaPES object from {filename} is not a valid curriculum or has no render method.")
                abort(500, description="Failed to load or parse PiaPES curriculum for rendering, or incorrect type.")
        except Exception as e:
            logger.error(f"Error rendering PiaPES curriculum {filename}: {e}", exc_info=True)
            return jsonify({"error": f"Failed to render PiaPES curriculum: {str(e)}"}), 500

    @app.route('/api/pes/curricula', methods=['POST'])
    def api_create_pes_curriculum():
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        data = request.get_json()

        raw_filename = data.get('filename')
        if not raw_filename:
            return jsonify({"error": "Filename is required in the JSON payload for curriculum."}), 400
        if not raw_filename.endswith('.curriculum.json'):
            return jsonify({"error": "Curriculum filename must end with '.curriculum.json'"}), 400
        
        base_name = os.path.splitext(os.path.splitext(raw_filename)[0])[0] # Remove .curriculum.json
        filename = sanitize_filename(base_name) + ".curriculum.json"

        filepath = os.path.join(PES_FILES_DIR, filename)
        if os.path.exists(filepath):
            return jsonify({"error": f"PiaPES Curriculum file '{filename}' already exists."}), 409

        # Basic validation (can be expanded based on DevelopmentalCurriculum structure)
        if '__type__' not in data or data['__type__'] != 'DevelopmentalCurriculum':
            data['__type__'] = 'DevelopmentalCurriculum' # Force if missing, or error out
            # return jsonify({"error": "Invalid __type__ for curriculum. Expected 'DevelopmentalCurriculum'."}), 400
        if 'name' not in data or 'steps' not in data:
             return jsonify({"error": "Missing 'name' or 'steps' in curriculum data."}), 400

        try:
            reconstructed_json_str = json.dumps(data)
            curriculum_object = json.loads(reconstructed_json_str, object_hook=pia_agi_object_hook)

            if not isinstance(curriculum_object, DevelopmentalCurriculum):
                logger.error(f"Data for {filename} did not reconstruct into a DevelopmentalCurriculum. Type: {type(curriculum_object)}")
                return jsonify({"error": "Error reconstructing PiaPES curriculum object."}), 400
            
            save_template(curriculum_object, filepath)
            return jsonify({"message": f"PiaPES Curriculum '{filename}' created successfully.", "filename": filename}), 201
        except (json.JSONDecodeError, TypeError, KeyError, AttributeError, ValueError) as e:
            logger.error(f"Error processing/reconstructing data for PiaPES curriculum {filename}: {e}", exc_info=True)
            return jsonify({"error": f"Invalid curriculum data structure. Details: {str(e)}"}), 400
        except Exception as e:
            logger.error(f"Error creating PiaPES curriculum {filename}: {e}", exc_info=True)
            return jsonify({"error": f"Failed to create PiaPES curriculum: {str(e)}"}), 500

    @app.route('/api/pes/curricula/<path:filename>', methods=['PUT'])
    def api_update_pes_curriculum_metadata(filename):
        if '..' in filename or filename.startswith('/'):
            logger.warning(f"Attempt to access potentially unsafe path for curriculum PUT: {filename}")
            abort(400, description="Invalid filename.")

        if not filename.endswith('.curriculum.json'):
            abort(400, description="Invalid PiaPES curriculum filename format for update.")
        filepath = os.path.join(PES_FILES_DIR, filename)
        if not os.path.exists(filepath):
            abort(404, description="PiaPES Curriculum file not found to update.")

        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        data_to_update = request.get_json()

        try:
            curriculum_obj = load_template(filepath)
            if not isinstance(curriculum_obj, DevelopmentalCurriculum):
                logger.error(f"Loaded file '{filename}' for curriculum update is not a DevelopmentalCurriculum.")
                return jsonify({"error": "Loaded file is not a valid PiaPES curriculum object."}), 500

            allowed_metadata_fields = ['name', 'description', 'target_developmental_stage', 'version', 'author']
            updated_fields_count = 0
            for field in allowed_metadata_fields:
                if field in data_to_update:
                    setattr(curriculum_obj, field, data_to_update[field])
                    updated_fields_count += 1
            
            # Ensure __type__ remains correct
            curriculum_obj.__type__ = "DevelopmentalCurriculum"

            if updated_fields_count > 0:
                save_template(curriculum_obj, filepath)
                return jsonify({"message": f"PiaPES Curriculum metadata for '{filename}' updated successfully.", "filename": filename}), 200
            else:
                return jsonify({"message": f"No recognized metadata fields provided for PiaPES curriculum update in '{filename}'. No changes made."}), 200
        except (json.JSONDecodeError, TypeError, AttributeError, ValueError) as e:
            logger.error(f"Error processing data for PiaPES curriculum metadata update {filename}: {e}", exc_info=True)
            return jsonify({"error": f"Invalid data for curriculum metadata update. Details: {str(e)}"}), 400
        except Exception as e:
            logger.error(f"Error updating PiaPES curriculum metadata {filename}: {e}", exc_info=True)
            return jsonify({"error": f"Failed to update PiaPES curriculum metadata: {str(e)}"}), 500
# --- End PiaPES API Endpoints ---

# --- PiaSE API Endpoints ---
# Conditionally define PiaSE endpoint if core components were imported
if not all(name in globals() for name in ['BasicSimulationEngine', 'GridWorld', 'QLearningAgent', 'GridWorldVisualizer']):
    logger.error("Core PiaSE classes not imported. PiaSE API endpoint '/api/piase/run_simulation' will not be available.")
else:
    @app.route('/api/piase/run_simulation', methods=['POST'])
    def piase_run_simulation():
        try:
            # For now, using a hardcoded scenario similar to PiaSE/WebApp/app.py
            # TODO: Accept scenario configuration from request JSON payload in a future iteration.
            # data = request.get_json()
            # grid_width = data.get('grid_width', 5)
            # ... other params ...

            grid_width = 5
            grid_height = 5
            goal_pos = (grid_width - 1, grid_height - 1)
            walls = [(1, 1), (1, 2), (2, 1), (3, 3)]
            start_pos_q_agent = (0, 0)
            agent_id = "q_agent_1" # Hardcoded agent ID

            # 1. Setup Environment
            # The GridWorld in PiaSE/environments/grid_world.py has changed its __init__ signature.
            # It now takes default_agent_id and uses that for agent_start_pos if not multi-agent.
            # Let's adapt to use the `add_agent` method for clarity or pass `agent_start_positions`
            environment = GridWorld(
                width=grid_width,
                height=grid_height,
                walls=walls,
                goal_position=goal_pos,
                # The GridWorld in the provided code uses `agent_start_pos` for a single default agent,
                # or expects agents to be added via `add_agent` or `agent_start_positions` for multi-agent.
                # Let's assume we are setting up for a specific agent.
                # We can use default_agent_id and initial_agent_start_pos, or add_agent.
                default_agent_id=agent_id, # Set default agent ID
                agent_start_pos=start_pos_q_agent # And its start position
            )
            # If GridWorld's __init__ expects `agent_start_positions` dict:
            # environment = GridWorld(width=grid_width, height=grid_height, walls=walls, goal_position=goal_pos,
            #                         agent_start_positions={agent_id: start_pos_q_agent})


            # 2. Setup Engine and Agent
            engine = BasicSimulationEngine() # Logger path will be default or set in initialize
            q_agent = QLearningAgent(exploration_rate=0.2, learning_rate=0.1, discount_factor=0.9)
            
            # Engine initialization now takes environment, agents dict, scenario_config, and log_path
            # We'll use a default log path within the run's unique directory.
            
            run_timestamp = time.strftime("%Y%m%d-%H%M%S")
            random_id = os.urandom(4).hex() # Short random ID to avoid collisions
            run_dir_name = f"run_{run_timestamp}_{random_id}"
            
            current_run_output_dir_absolute = os.path.join(PIASE_RUNS_OUTPUT_DIR_ABSOLUTE, run_dir_name)
            if not os.path.exists(current_run_output_dir_absolute):
                os.makedirs(current_run_output_dir_absolute)

            # Log path for PiaSE's internal logger (if used by BasicSimulationEngine)
            piase_log_file = os.path.join(current_run_output_dir_absolute, "piase_internal_log.jsonl")

            # Initialize engine
            # The BasicSimulationEngine's initialize method expects an agents dict.
            engine.initialize(
                environment=environment,
                agents={agent_id: q_agent},
                scenario_config={"name": "WebApp_DefaultGridScenario"},
                log_path=piase_log_file
            )
            
            # 3. Setup Visualizer for our API needs
            visualizer = GridWorldVisualizer(environment)
            image_urls = []
            text_log_api = ["PiaSE Simulation Log (WebApp API):"] # This is the log we build for the API response

            # Initial render
            img_filename_initial = "step_000.png"
            img_path_initial_absolute = os.path.join(current_run_output_dir_absolute, img_filename_initial)
            visualizer.render(title="Initial State", output_path=img_path_initial_absolute, step_delay=None)
            image_urls.append(f"/static/{PIASE_RUNS_STATIC_DIR}/{run_dir_name}/{img_filename_initial}")
            text_log_api.append("Initial state rendered.")

            # 4. Run Simulation Loop
            num_steps = 50 # TODO: Make configurable from request
            text_log_api.append(f"Starting simulation for up to {num_steps} steps...")
            agent_reached_goal = False

            for i in range(num_steps):
                step_log_entry = f"--- Step {i+1}/{num_steps} ---"
                text_log_api.append(step_log_entry)
                logger.info(f"[PiaSE Run {run_dir_name}] {step_log_entry}")

                engine.run_step()

                agent_current_pos = environment.agent_positions.get(agent_id)
                text_log_api.append(f"Agent {agent_id} action: {q_agent.last_action}, New position: {agent_current_pos}")

                img_filename = f"step_{i+1:03d}.png"
                img_path_absolute = os.path.join(current_run_output_dir_absolute, img_filename)
                visualizer.render(title=f"After Step {i+1}", output_path=img_path_absolute, step_delay=None)
                image_urls.append(f"/static/{PIASE_RUNS_STATIC_DIR}/{run_dir_name}/{img_filename}")

                if environment.is_done(agent_id):
                    text_log_api.append(f"Agent {agent_id} reached the goal at step {i+1}!")
                    logger.info(f"[PiaSE Run {run_dir_name}] Agent {agent_id} reached goal at step {i+1}.")
                    agent_reached_goal = True
                    break
            
            if not agent_reached_goal:
                 text_log_api.append(f"Simulation finished after {num_steps} steps. Goal not reached.")
                 logger.info(f"[PiaSE Run {run_dir_name}] Simulation finished, goal not reached.")
            else:
                 text_log_api.append("Simulation finished.")
                 logger.info(f"[PiaSE Run {run_dir_name}] Simulation finished, goal reached.")


            # Add Q-table sample to log (optional, can be large)
            text_log_api.append("\n--- Q-Learning Agent's Q-Table (sample) ---")
            q_table_sample_count = 0
            for state_key, actions_map in list(q_agent.q_table.items())[:10]: # Sample first 10 states
                if q_table_sample_count >= 5 : break # Limit log size further
                text_log_api.append(f"State {state_key}: {actions_map}")
                q_table_sample_count +=1
            
            plt.close(visualizer.fig) # Close the figure to free memory

            return jsonify({
                "message": "PiaSE simulation run completed.",
                "run_id": run_dir_name,
                "image_urls": image_urls,
                "text_log": "\n".join(text_log_api), # Join log list into a single string
                "summary": {
                    "agent_reached_goal": agent_reached_goal,
                    "total_steps_taken": i + 1 if agent_reached_goal else num_steps,
                    "final_agent_position": agent_current_pos
                }
            }), 200

        except ImportError: # Catch if dummy classes are in use due to failed PiaSE import
            logger.error("PiaSE components not available. Cannot run simulation.", exc_info=True)
            return jsonify({"error": "PiaSE components are not available. Simulation cannot be run."}), 501 # Not Implemented
        except Exception as e:
            logger.error(f"Error during PiaSE simulation: {e}", exc_info=True)
            return jsonify({"error": f"An unexpected error occurred during PiaSE simulation: {str(e)}"}), 500
# --- End PiaSE API Endpoints ---


if __name__ == '__main__':
    port = int(os.environ.get('FLASK_RUN_PORT', 5001)) # Changed default port to 5001 to avoid conflict with frontend dev server
    logger.info(f"Starting Flask app on port {port}")
    # The sys.path modifications at the top should help for typical `flask run` scenarios.
    app.run(debug=True, port=port)
