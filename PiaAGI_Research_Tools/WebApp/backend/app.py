import os
from flask import Flask, request, jsonify, abort
from dotenv import load_dotenv
from openai import OpenAI, APIError, AuthenticationError, RateLimitError, APIConnectionError
from flask_cors import CORS
import sys
import configparser
import logging
import json
import re
import inspect
import time
import tempfile
from werkzeug.utils import secure_filename
from datetime import datetime
import yaml # For loading YAML scenario definitions

# --- Path Setup ---
try:
    path_to_research_tools_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if path_to_research_tools_root not in sys.path: sys.path.insert(0, path_to_research_tools_root)
    for tool_subdir in ['PiaPES', 'PiaSE', 'PiaCML', 'PiaAVT']:
        abs_path = os.path.join(path_to_research_tools_root, tool_subdir)
        if abs_path not in sys.path: sys.path.insert(0, abs_path)
except Exception as e:
    logging.basicConfig(level=logging.ERROR); logging.error(f"Path setup error: {e}", exc_info=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# --- Dynamically Import Tool Modules & Define Availability Flags ---
def import_tool_module(module_name, from_list=None, class_defs_on_fail=None):
    available_flag_name = f"{module_name.split('.')[0].upper()}_AVAILABLE" # Use base module for flag
    try:
        if from_list:
            module = __import__(module_name, fromlist=from_list)
            for name in from_list:
                if hasattr(module, name):
                    globals()[name] = getattr(module, name)
                elif class_defs_on_fail and name in class_defs_on_fail: # Check if dummy provided for specific class
                     globals()[name] = class_defs_on_fail[name]
                     logger.warning(f"Specific class {name} from {module_name} not found, using dummy.")
                else:
                    logger.warning(f"Specific class {name} not found in {module_name} and no dummy provided.")


        else:
            globals()[module_name] = __import__(module_name)

        # Set main availability flag based on the primary module name (e.g. PiaCML_AVAILABLE)
        # This might need refinement if a module has critical and non-critical sub-components.
        base_module_name_for_flag = module_name.split('.')[0] # e.g., "PiaCML" from "PiaCML.message_bus"
        globals()[f"{base_module_name_for_flag.upper()}_AVAILABLE"] = True # Assume available if any part imports
        logger.info(f"Components from {module_name} imported successfully.")

    except ImportError as e:
        logger.error(f"Error importing {module_name} components: {e}. Functionalities will be limited.", exc_info=True)
        globals()[available_flag_name] = False
        if class_defs_on_fail: # Define all dummy classes passed for this module
            for class_name, dummy_class in class_defs_on_fail.items():
                globals()[class_name] = dummy_class
    except Exception as e_gen: # Catch other potential errors during import
        logger.error(f"Generic error importing {module_name}: {e_gen}", exc_info=True)
        globals()[available_flag_name] = False


# Define dummy classes for fallback
class DummyMessageBus: pass
class DummyPiaAGIPrompt: pass
class DummyDevelopmentalCurriculum: pass
class DummyCognitiveModuleConfiguration: pass
class DummyExecutor: pass
class DummyRole: pass
class DummyPiaAGIEncoder(json.JSONEncoder): pass
def dummy_save_template(obj,path): logger.error("PiaPES dummy save_template called.")
def dummy_load_template(path): logger.error("PiaPES dummy load_template called."); return None
def dummy_pia_agi_object_hook(dct): logger.error("PiaPES dummy pia_agi_object_hook called."); return dct
class DummyPiaAGIAgent: pass
class DummyBasicSimulationEngine: pass
class DummyGridWorld: pass
class DummyScenarioLoader: def __init__(self,d):pass; def list_scenarios(self):return[]; def load_scenario_config(self,id):return None
class DummyPiaAVTAPI: pass

# Import CML
cml_dummy_classes = {"MessageBus": DummyMessageBus} # Add more if specific CML classes are directly used and need dummies
concrete_cml_classes_to_import = [
    "ConcretePerceptionModule", "ConcreteWorkingMemoryModule", "ConcreteLongTermMemoryModule",
    "ConcreteAttentionModule", "ConcreteLearningModule", "ConcreteMotivationalSystemModule",
    "ConcreteEmotionModule", "ConcretePlanningAndDecisionMakingModule", "ConcreteBehaviorGenerationModule",
    "ConcreteSelfModelModule", "ConcreteTomModule", "ConcreteWorldModel", "ConcreteCommunicationModule"
]
for cml_class_name in concrete_cml_classes_to_import:
    import_tool_module(f"PiaCML.{cml_class_name.replace('Concrete','concrete_').lower()}", [cml_class_name], {cml_class_name: type(cml_class_name, (object,), {})})
import_tool_module("PiaCML.message_bus", ["MessageBus"], {"MessageBus": DummyMessageBus})


# Import PiaPES
pes_dummy_classes = {
    "PiaAGIPrompt": DummyPiaAGIPrompt, "DevelopmentalCurriculum": DummyDevelopmentalCurriculum,
    "CognitiveModuleConfiguration": DummyCognitiveModuleConfiguration, "Executor": DummyExecutor, "Role": DummyRole,
    "PiaAGIEncoder": DummyPiaAGIEncoder, "save_template": dummy_save_template,
    "load_template": dummy_load_template, "pia_agi_object_hook": dummy_pia_agi_object_hook
}
import_tool_module("prompt_engine_mvp", list(pes_dummy_classes.keys()), pes_dummy_classes)


# Import PiaSE
piase_dummy_classes = {"PiaAGIAgent": DummyPiaAGIAgent, "BasicSimulationEngine": DummyBasicSimulationEngine, "GridWorld": DummyGridWorld}
import_tool_module("agents.pia_agi_agent", ["PiaAGIAgent"], {"PiaAGIAgent": DummyPiaAGIAgent})
import_tool_module("core_engine.basic_engine", ["BasicSimulationEngine"], {"BasicSimulationEngine": DummyBasicSimulationEngine})
import_tool_module("environments.grid_world", ["GridWorld"], {"GridWorld": DummyGridWorld}) # Example environment
try:
    from PiaSE.scenarios.scenario_loader import ScenarioLoader
    logger.info("PiaSE ScenarioLoader imported successfully.")
    PIASE_SCENARIOLOADER_AVAILABLE = True
except ImportError:
    logger.warning("PiaSE ScenarioLoader not found. Using dummy.")
    ScenarioLoader = DummyScenarioLoader # Assign dummy class to global scope
    PIASE_SCENARIOLOADER_AVAILABLE = False


# Import PiaAVT
import_tool_module("api", ["PiaAVTAPI"], {"PiaAVTAPI":DummyPiaAVTAPI}) # From PiaAVT.api


load_dotenv()
app = Flask(__name__, static_folder='static')
CORS(app)
if globals().get("PROMPT_ENGINE_MVP_AVAILABLE") and 'PiaAGIEncoder' in globals() and callable(globals()['PiaAGIEncoder']):
    app.json_encoder = globals()['PiaAGIEncoder']
else:
    logger.warning("PiaAGIEncoder not available. Using default JSON encoder.")

llm_config = configparser.ConfigParser()
LLM_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'llm_config.ini')
if os.path.exists(LLM_CONFIG_PATH): llm_config.read(LLM_CONFIG_PATH); logger.info(f"LLM config loaded")
else: logger.warning(f"LLM config file not found at {LLM_CONFIG_PATH}.")

def get_llm_api_key(provider='OpenAI'):
    if not llm_config: return None
    try: return llm_config.get(provider, 'API_KEY', fallback=None)
    except: return None
def get_default_llm_model(provider='OpenAI'):
    if not llm_config: return 'gpt-3.5-turbo'
    try: return llm_config.get(provider, 'MODEL_NAME', fallback=llm_config.get('DEFAULT', 'DEFAULT_MODEL_NAME', fallback='gpt-3.5-turbo'))
    except: return 'gpt-3.5-turbo'

# Global CML instances for direct interaction endpoints (not for experiments)
perception_module_instance, emotion_module_instance, motivational_system_instance, working_memory_instance = None, None, None, None
if globals().get("PIACML_CONCRETE_PERCEPTION_MODULE_AVAILABLE"): perception_module_instance = globals()['ConcretePerceptionModule']()
if globals().get("PIACML_CONCRETE_EMOTION_MODULE_AVAILABLE"): emotion_module_instance = globals()['ConcreteEmotionModule']()
if globals().get("PIACML_CONCRETE_MOTIVATIONAL_SYSTEM_MODULE_AVAILABLE"): motivational_system_instance = globals()['ConcreteMotivationalSystemModule']()
if globals().get("PIACML_CONCRETE_WORKING_MEMORY_MODULE_AVAILABLE"): working_memory_instance = globals()['ConcreteWorkingMemoryModule'](capacity=5)


PES_FILES_DIR = os.path.join(os.path.dirname(__file__), 'pes_files'); os.makedirs(PES_FILES_DIR, exist_ok=True)
PIASE_SCENARIOS_DIR = os.path.join(path_to_research_tools_root, 'PiaSE', 'scenarios', 'definitions'); os.makedirs(PIASE_SCENARIOS_DIR, exist_ok=True)
PIASE_RUNS_STATIC_DIR = 'piase_runs'
PIASE_RUNS_OUTPUT_DIR_ABSOLUTE = os.path.join(app.static_folder, PIASE_RUNS_STATIC_DIR); os.makedirs(PIASE_RUNS_OUTPUT_DIR_ABSOLUTE, exist_ok=True)
current_experiments = {}

def sanitize_filename(name):
    name = str(name); name = re.sub(r'[^\w\s-]', '', name).strip(); name = re.sub(r'[-\s_]+', '-', name)
    name = name.strip('-.'); return name if name and not all(c == '.' for c in name) else "unnamed_file"

@app.route('/api/hello')
def hello_world(): return jsonify({'message': 'Hello!'})

@app.route('/api/process_prompt', methods=['POST'])
def process_prompt():
    # ... (existing process_prompt code - assuming it's fine) ...
    try:
        data = request.get_json();
        if not data: return jsonify({"error": "Invalid JSON"}), 400
        prompt_content = data.get('prompt'); test_question = data.get('testQuestion')
        final_api_key = data.get('apiKey') or get_llm_api_key()
        if not final_api_key: return jsonify({"error": "API key missing"}), 400
        llm_model = data.get('llmModel') or get_default_llm_model()
        if not prompt_content or not test_question: return jsonify({"error": "Missing prompt or question"}), 400
        client = OpenAI(api_key=final_api_key)
        completion = client.chat.completions.create(model=llm_model, messages=[{"role": "system", "content": prompt_content},{"role": "user", "content": test_question}])
        return jsonify({"response": completion.choices[0].message.content})
    except Exception as e: logger.error(f"Error in /api/process_prompt: {e}", exc_info=True); return jsonify({"error": str(e)}), 500


# --- Experiment Runner Endpoints ---
@app.route('/api/experiments/run', methods=['POST'])
def run_experiment():
    # ... (agent initialization and PiaSE simulation logic from previous steps - unchanged) ...
    if not all(globals().get(flag, False) for flag in ["PIACML_MESSAGE_BUS_AVAILABLE", "PROMPT_ENGINE_MVP_AVAILABLE", "AGENTS_PIA_AGI_AGENT_AVAILABLE", "CORE_ENGINE_BASIC_ENGINE_AVAILABLE"]): # Check specific critical components
        return jsonify({"error": "Core PiaAGI tools for experiment run not available."}), 503
    data = request.get_json();
    if not data: return jsonify({"error": "Missing JSON"}), 400
    agent_config_ref = data.get('agent_config_ref'); piase_scenario_ref = data.get('piase_scenario_ref')
    experiment_name = data.get('experiment_name', "WebApp Run"); logging_level_str = data.get('logging_level', 'INFO').upper()
    log_level_map = {"DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARNING": logging.WARNING, "ERROR": logging.ERROR}
    effective_log_level = log_level_map.get(logging_level_str, logging.INFO)
    if not agent_config_ref or not piase_scenario_ref: return jsonify({"error": "Missing refs"}), 400
    run_id = f"run_{time.strftime('%Y%m%d-%H%M%S')}_{os.urandom(4).hex()}"
    current_run_output_dir = os.path.join(PIASE_RUNS_OUTPUT_DIR_ABSOLUTE, run_id); os.makedirs(current_run_output_dir, exist_ok=True)
    run_log_path = os.path.join(current_run_output_dir, f"{run_id}_simulation.jsonl")
    current_experiments[run_id] = {"status": "INITIALIZING", "name": experiment_name, "log_path": run_log_path, "start_time": time.time()}
    try:
        logger.info(f"[{run_id}] Initializing agent: {agent_config_ref}")
        config_to_load = agent_config_ref if agent_config_ref.endswith('.json') else agent_config_ref + ".json"
        agent_config_filepath = os.path.join(PES_FILES_DIR, config_to_load)
        if not os.path.exists(agent_config_filepath): raise FileNotFoundError(f"Agent config not found: {agent_config_filepath}")
        loaded_prompt = globals()['load_template'](agent_config_filepath)
        if not isinstance(loaded_prompt, globals()['PiaAGIPrompt']): raise ValueError("Not a PiaAGIPrompt.")
        cg_params = {}; raw_cg_config = None
        if loaded_prompt.executors and loaded_prompt.executors[0].role and \
           hasattr(loaded_prompt.executors[0].role, 'cognitive_module_configuration') and \
           loaded_prompt.executors[0].role.cognitive_module_configuration:
            raw_cg_config = loaded_prompt.executors[0].role.cognitive_module_configuration
            for field, _ in globals()['CognitiveModuleConfiguration'].__annotations__.items():
                if hasattr(raw_cg_config, field):
                    val = getattr(raw_cg_config, field)
                    if val is not None: cg_params[field] = val.__dict__ if hasattr(val, '__dict__') else val
        msg_bus = globals()['MessageBus'](); cml_inst = {}; personality = cg_params.get('personality_config', {})
        concrete_module_classes = {name: globals()[name] for name in globals() if name.startswith("Concrete") and callable(globals()[name])}
        for m_key, m_class in concrete_module_classes.items():
            p_key_base = m_key.replace("Concrete","").replace("Module","").lower()
            p_keys_try = [f"{p_key_base}_config", f"{p_key_base}_module_config",
                           "motivational_bias_config" if p_key_base == "motivationalsystem" else None,
                           "emotional_profile_config" if p_key_base == "emotion" else None]
            const_params = {};
            for k_try in filter(None, p_keys_try):
                if k_try in cg_params: const_params = cg_params[k_try].copy(); break
            if m_key in ["ConcreteEmotionModule", "ConcreteSelfModelModule", "ConcreteMotivationalSystemModule", "ConcreteCommunicationModule"] and personality:
                const_params['personality_profile_params'] = personality
            const_params['message_bus'] = msg_bus
            sig = inspect.signature(m_class.__init__).parameters
            final_ps = {k:v for k,v in const_params.items() if k in sig}
            if 'message_bus' in sig and 'message_bus' not in final_ps: final_ps['message_bus'] = msg_bus
            try: cml_inst[p_key_base+"_module"] = m_class(**final_ps)
            except Exception as e_mi: raise Exception(f"Error init {m_key} with {list(final_ps.keys())}: {e_mi}")
        agent_inst = globals()['PiaAGIAgent'](agent_id=run_id, modules=cml_inst, message_bus=msg_bus)
        current_experiments[run_id]["agent_instance"] = agent_inst; current_experiments[run_id]["status"] = "AGENT_INITIALIZED"
        logger.info(f"[{run_id}] Agent assembled.")
        logger.info(f"[{run_id}] Loading scenario: {piase_scenario_ref}")
        env_inst = None; sc_cfg_eng = {"name": piase_scenario_ref, "max_steps": data.get("max_steps", 100)}
        if piase_scenario_ref == "default_gridworld":
            env_inst = globals()['GridWorld'](width=10, height=10, default_agent_id=run_id, agent_start_pos=(0,0))
        elif PIASE_SCENARIOLOADER_AVAILABLE:
            sc_def_path = os.path.join(PIASE_SCENARIOS_DIR, piase_scenario_ref) # Assuming ref is filename like "my_scenario.yaml"
            if os.path.exists(sc_def_path):
                loader = ScenarioLoader(PIASE_SCENARIOS_DIR) # scenarios_dir is the parent folder of definitions
                loaded_sc = loader.load_scenario_config(piase_scenario_ref) # scenario_id is filename
                if loaded_sc and loaded_sc.get("environment_type") == "GridWorld": # Example, expand for more types
                    env_ps = loaded_sc.get("environment_params", {})
                    if 'default_agent_id' not in env_ps: env_ps['default_agent_id'] = run_id
                    if 'agent_start_pos' not in env_ps: env_ps['agent_start_pos'] = (0,0)
                    env_inst = globals()['GridWorld'](**env_ps); sc_cfg_eng.update(loaded_sc)
                elif loaded_sc: # Some other environment type, needs specific handling
                     raise ValueError(f"Scenario '{piase_scenario_ref}' environment type '{loaded_sc.get('environment_type')}' not yet supported by WebApp.")
                else: raise ValueError(f"Scenario '{piase_scenario_ref}' failed to load or invalid structure.")
            else: raise FileNotFoundError(f"Scenario file not found: {sc_def_path}")
        else: raise ValueError("ScenarioLoader unavailable and scenario is not 'default_gridworld'.")

        if not env_inst: raise ValueError("Failed to init environment.")
        current_experiments[run_id]["scenario_config_actual"] = sc_cfg_eng
        sim_eng = globals()['BasicSimulationEngine']()
        sim_eng.initialize(environment=env_inst, agents={run_id: agent_inst}, scenario_config=sc_cfg_eng, log_path=run_log_path, log_level=effective_log_level)
        current_experiments[run_id]["engine"] = sim_eng; current_experiments[run_id]["status"] = "SIMULATION_READY"
        logger.info(f"[{run_id}] SimulationEngine initialized. Log: {run_log_path}")
        current_experiments[run_id]["status"] = "SIMULATION_RUNNING"
        logger.info(f"[{run_id}] Starting simulation (sync)...")
        max_s = sc_cfg_eng.get("max_steps", 100)
        for s_num in range(max_s):
            if sim_eng.is_simulation_done(): logger.info(f"[{run_id}] Sim ended early at step {s_num}."); break
            sim_eng.run_step()
        logger.info(f"[{run_id}] Simulation run completed."); current_experiments[run_id]["status"] = "SIMULATION_COMPLETED"; current_experiments[run_id]["end_time"] = time.time()
        return jsonify({"message":"Experiment completed.","run_id":run_id,"status_endpoint":f"/api/experiments/status/{run_id}","log_path":run_log_path}), 200
    except Exception as e:
        err_m = str(e); logger.error(f"[{run_id}] Error in run_experiment: {err_m}", exc_info=True)
        if run_id in current_experiments: current_experiments[run_id].update({"status":"ERROR", "error_message":err_m})
        status_code = 404 if isinstance(e, FileNotFoundError) else 400 if isinstance(e, (ValueError, AttributeError)) else 500
        return jsonify({"error": err_m}), status_code

@app.route('/api/experiments/status/<run_id>', methods=['GET'])
def get_experiment_status(run_id):
    exp = current_experiments.get(run_id)
    if not exp: return jsonify({"error": "Run not found"}), 404
    return jsonify({k: v for k, v in exp.items() if k not in ["agent_instance", "engine"]})

@app.route('/api/experiments/logs/<run_id>', methods=['GET'])
def get_experiment_logs(run_id):
    exp = current_experiments.get(run_id)
    log_p = exp.get("log_path") if exp else None
    if not log_p or not os.path.exists(log_p): return jsonify({"error": "Logs not found."}), 404
    try:
        lines_req = request.args.get('tail_lines', 100, int)
        with open(log_p, 'r', encoding='utf-8') as f: lines = f.readlines()
        return jsonify({"run_id":run_id, "log_content":"".join(lines[-lines_req:] if lines_req > 0 else lines)})
    except Exception as e: return jsonify({"error": f"Log read error: {str(e)}"}), 500

# --- CML State Endpoints ---
def get_latest_cml_state_from_log(run_id, relevant_event_types, data_extractor_func):
    exp = current_experiments.get(run_id); log_path = exp.get("log_path") if exp else None
    if not log_path or not os.path.exists(log_path): logger.warning(f"Log for {run_id} not found."); return None
    latest_state = None; last_timestamp = 0.0
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            for line in f:
                try: log_entry = json.loads(line); entry_ts = float(log_entry.get("timestamp",0))
                except (json.JSONDecodeError, ValueError): continue
                if log_entry.get("event_type") in relevant_event_types and log_entry.get("agent_id") == run_id and entry_ts >= last_timestamp:
                    extracted = data_extractor_func(log_entry)
                    if extracted: latest_state = extracted; last_timestamp = entry_ts
        return latest_state
    except Exception as e: logger.error(f"Error parsing log {log_path}: {e}", exc_info=True); return None

@app.route('/api/cml/msm/state/<run_id>', methods=['GET'])
def get_cml_msm_state(run_id):
    def extractor(log_entry): return log_entry.get("event_data", {}).get("current_msm_state", {}) if log_entry["event_type"] == "MOTIVATIONAL_SYSTEM_UPDATE" else None
    state = get_latest_cml_state_from_log(run_id, ["MOTIVATIONAL_SYSTEM_UPDATE"], extractor)
    if state: return jsonify({"run_id":run_id, "timestamp_of_state":state.get("timestamp",datetime.utcnow().isoformat()), **state})
    return jsonify({"error": "MSM state not found.", "run_id": run_id}), 404

@app.route('/api/cml/wm/state/<run_id>', methods=['GET'])
def get_cml_wm_state(run_id):
    def extractor(log_entry): return log_entry.get("event_data", {}).get("current_wm_state", {}) if log_entry["event_type"] == "WORKING_MEMORY_UPDATE" else None
    state = get_latest_cml_state_from_log(run_id, ["WORKING_MEMORY_UPDATE"], extractor)
    if state: return jsonify({"run_id":run_id, "timestamp_of_state":state.get("timestamp",datetime.utcnow().isoformat()), **state})
    return jsonify({"error": "WM state not found.", "run_id": run_id}), 404

@app.route('/api/cml/emotion/state/<run_id>', methods=['GET'])
def get_cml_emotion_state(run_id):
    def extractor(log_entry): return log_entry.get("event_data") if log_entry["event_type"] == "EMOTIONAL_STATE_CHANGE" else None
    state = get_latest_cml_state_from_log(run_id, ["EMOTIONAL_STATE_CHANGE"], extractor)
    if state: return jsonify({"run_id":run_id, "timestamp_of_state":state.get("timestamp",datetime.utcnow().isoformat()), "current_vad":state.get("vad_state",{}), "primary_discrete_emotion":state.get("discrete_emotion","neutral"), "intensity":state.get("intensity",0.0)})
    return jsonify({"error": "Emotion state not found.", "run_id": run_id}), 404

# --- AVT Analysis Endpoints ---
@app.route('/api/avt/analysis/goal_lifecycle_counts/<run_id>', methods=['GET'])
def get_avt_goal_counts(run_id):
    if not globals().get("API_AVAILABLE"): return jsonify({"error":"PiaAVT not available"}), 503 # Check specific AVT API flag
    exp = current_experiments.get(run_id); log_path = exp.get("log_path") if exp else None
    if not log_path or not os.path.exists(log_path): return jsonify({"error": "Log file not found."}), 404
    try:
        avt_api = globals()['PiaAVTAPI']()
        if not avt_api.load_logs_from_jsonl(log_path): return jsonify({"error": "AVT load failed."}), 500
        goal_dynamics = avt_api.analyze_goal_dynamics(); counts = {"GOAL_CREATED":0,"GOAL_ACTIVATED":0,"GOAL_ACHIEVED":0,"GOAL_FAILED":0,"GOAL_PENDING":0}
        if goal_dynamics and "goal_summary" in goal_dynamics:
            for _, summary in goal_dynamics["goal_summary"].items():
                counts["GOAL_CREATED"]+=1
                if summary["status_transitions"]: counts["GOAL_ACTIVATED"]+=1
                if summary["final_status"] == "ACHIEVED": counts["GOAL_ACHIEVED"]+=1
                elif summary["final_status"] == "FAILED": counts["GOAL_FAILED"]+=1
                else: counts["GOAL_PENDING"]+=1
        return jsonify({"run_id":run_id, "analysis_type":"goal_lifecycle_counts", "data":[{"event":k,"count":v} for k,v in counts.items()]})
    except Exception as e: logger.error(f"AVT goal_counts error for {run_id}: {e}", exc_info=True); return jsonify({"error":str(e)}),500

@app.route('/api/avt/analysis/vad_trajectory/<run_id>', methods=['GET'])
def get_avt_vad_trajectory(run_id):
    if not globals().get("API_AVAILABLE"): return jsonify({"error":"PiaAVT not available"}), 503
    exp = current_experiments.get(run_id); log_path = exp.get("log_path") if exp else None
    if not log_path or not os.path.exists(log_path): return jsonify({"error": "Log file not found."}), 404
    try:
        avt_api = globals()['PiaAVTAPI']()
        if not avt_api.load_logs_from_jsonl(log_path): return jsonify({"error": "AVT load failed."}), 500
        traj = avt_api.analyze_emotional_trajectory(); ts, v, a, d = [],[],[],[]
        if traj:
            for p in traj: ts.append(p.get("timestamp")); v.append(p.get("valence")); a.append(p.get("arousal")); d.append(p.get("dominance"))
        return jsonify({"run_id":run_id, "analysis_type":"vad_trajectory", "timestamps":ts, "valence":v, "arousal":a, "dominance":d})
    except Exception as e: logger.error(f"AVT vad_traj error for {run_id}: {e}", exc_info=True); return jsonify({"error":str(e)}),500

# --- SE Scenario Listing Endpoint ---
@app.route('/api/se/scenarios', methods=['GET'])
def list_se_scenarios():
    if not PIASE_SCENARIOLOADER_AVAILABLE: # Check if ScenarioLoader was imported
        logger.warning("PiaSE ScenarioLoader not available, returning mock scenarios.")
        return jsonify({"scenarios": [
            {"id": "default_gridworld", "name": "Default GridWorld", "description": "A simple 10x10 grid world for basic testing."},
            {"id": "mock_scenario_1.yaml", "name": "Mock Scenario 1", "description": "A mock scenario definition."}
        ]})
    try:
        loader = ScenarioLoader(scenarios_dir=PIASE_SCENARIOS_DIR)
        scenarios_list = loader.list_scenarios() # This should return list of dicts [{id, name, description}, ...]
        return jsonify({"scenarios": scenarios_list})
    except Exception as e:
        logger.error(f"Error listing PiaSE scenarios: {e}", exc_info=True)
        return jsonify({"error": f"Failed to list PiaSE scenarios: {str(e)}"}), 500


# --- Existing CML Routes for direct interaction (mostly unchanged) ---
# ... (cml direct interaction routes from previous version) ...
@app.route('/cml/perception/process', methods=['POST'])
def cml_perception_process():
    if not perception_module_instance or not hasattr(perception_module_instance, 'process_sensory_input'): return jsonify({"error": "PerceptionModule N/A"}), 500
    try: data = request.json; result = perception_module_instance.process_sensory_input(data.get('raw_input'), data.get('modality'), data.get('context', {})); return jsonify(result)
    except Exception as e: logger.error(f"Error: {e}", exc_info=True); return jsonify({"error": str(e)}), 500
@app.route('/cml/perception/status', methods=['GET'])
def cml_perception_status():
    if not perception_module_instance or not hasattr(perception_module_instance, 'get_module_status'): return jsonify({"error": "PerceptionModule N/A"}), 500
    try: return jsonify(perception_module_instance.get_module_status())
    except Exception as e: logger.error(f"Error: {e}", exc_info=True); return jsonify({"error": str(e)}), 500
@app.route('/cml/emotion/appraise', methods=['POST'])
def cml_emotion_appraise():
    if not emotion_module_instance or not hasattr(emotion_module_instance, 'appraise_situation'): return jsonify({"error": "EmotionModule N/A"}), 500
    try: data = request.json; result = emotion_module_instance.appraise_situation(data.get('event_info'), data.get('context', {})); return jsonify(result)
    except Exception as e: return jsonify({"error": str(e)}), 500
@app.route('/cml/emotion/current', methods=['GET'])
def cml_emotion_current():
    if not emotion_module_instance or not hasattr(emotion_module_instance, 'get_current_emotion'): return jsonify({"error": "EmotionModule N/A"}), 500
    try: return jsonify(emotion_module_instance.get_current_emotion())
    except Exception as e: return jsonify({"error": str(e)}), 500
@app.route('/cml/emotion/express', methods=['GET'])
def cml_emotion_express():
    if not emotion_module_instance or not hasattr(emotion_module_instance, 'express_emotion'): return jsonify({"error": "EmotionModule N/A"}), 500
    try: return jsonify(emotion_module_instance.express_emotion(context=None))
    except Exception as e: return jsonify({"error": str(e)}), 500
@app.route('/cml/emotion/status', methods=['GET'])
def cml_emotion_status():
    if not emotion_module_instance or not hasattr(emotion_module_instance, 'get_module_status'): return jsonify({"error": "EmotionModule N/A"}), 500
    try: return jsonify(emotion_module_instance.get_module_status())
    except Exception as e: return jsonify({"error": str(e)}), 500
@app.route('/cml/motivation/manage', methods=['POST'])
def cml_motivation_manage():
    if not motivational_system_instance or not hasattr(motivational_system_instance, 'manage_goals'): return jsonify({"error": "MSM N/A"}), 500
    try: data = request.json; result = motivational_system_instance.manage_goals(data.get('action'), data.get('goal_data', {})); return jsonify(result) if isinstance(result, (bool, str, list, dict)) else (jsonify(result) if result is not None else jsonify({"status": "ok_no_return"}) )
    except Exception as e: return jsonify({"error": str(e)}), 500
@app.route('/cml/motivation/active_goals', methods=['GET'])
def cml_motivation_active_goals():
    if not motivational_system_instance or not hasattr(motivational_system_instance, 'get_active_goals'): return jsonify({"error": "MSM N/A"}), 500
    try: N = request.args.get('N',0,int); min_p = request.args.get('min_priority',0.0,float); return jsonify(motivational_system_instance.get_active_goals(N, min_p))
    except Exception as e: return jsonify({"error": str(e)}), 500
@app.route('/cml/motivation/update_state', methods=['POST'])
def cml_motivation_update_state():
    if not motivational_system_instance or not hasattr(motivational_system_instance, 'update_motivation_state'): return jsonify({"error": "MSM N/A"}), 500
    try: data = request.json; return jsonify({"success": motivational_system_instance.update_motivation_state(data)})
    except Exception as e: return jsonify({"error": str(e)}), 500
@app.route('/cml/motivation/status', methods=['GET'])
def cml_motivation_status():
    if not motivational_system_instance or not hasattr(motivational_system_instance, 'get_module_status'): return jsonify({"error": "MSM N/A"}), 500
    try: return jsonify(motivational_system_instance.get_module_status())
    except Exception as e: return jsonify({"error": str(e)}), 500
@app.route('/cml/wm/add_item', methods=['POST'])
def cml_wm_add_item():
    if not working_memory_instance or not hasattr(working_memory_instance, 'add_item_to_workspace'): return jsonify({"error": "WM N/A"}), 500
    try: data = request.json; item_id = working_memory_instance.add_item_to_workspace(data.get('item_content'), data.get('salience',0.5), data.get('context',{})); return jsonify({"item_id": item_id, "current_size": len(working_memory_instance.get_workspace_contents())})
    except Exception as e: return jsonify({"error": str(e)}), 500
@app.route('/cml/wm/remove_item', methods=['POST'])
def cml_wm_remove_item():
    if not working_memory_instance or not hasattr(working_memory_instance, 'remove_item_from_workspace'): return jsonify({"error": "WM N/A"}), 500
    try: data = request.json; success = working_memory_instance.remove_item_from_workspace(data.get('item_id')); return jsonify({"success": success, "current_size": len(working_memory_instance.get_workspace_contents())})
    except Exception as e: return jsonify({"error": str(e)}), 500
@app.route('/cml/wm/contents', methods=['GET'])
def cml_wm_contents():
    if not working_memory_instance or not hasattr(working_memory_instance, 'get_workspace_contents'): return jsonify({"error": "WM N/A"}), 500
    try: return jsonify(working_memory_instance.get_workspace_contents())
    except Exception as e: return jsonify({"error": str(e)}), 500
@app.route('/cml/wm/set_focus', methods=['POST'])
def cml_wm_set_focus():
    if not working_memory_instance or not hasattr(working_memory_instance, 'set_active_focus'): return jsonify({"error": "WM N/A"}), 500
    try: data = request.json; success = working_memory_instance.set_active_focus(data.get('item_id')); return jsonify({"success": success, "current_focus": working_memory_instance.get_active_focus()})
    except Exception as e: return jsonify({"error": str(e)}), 500
@app.route('/cml/wm/get_focus', methods=['GET'])
def cml_wm_get_focus():
    if not working_memory_instance or not hasattr(working_memory_instance, 'get_active_focus'): return jsonify({"error": "WM N/A"}), 500
    try: return jsonify(working_memory_instance.get_active_focus())
    except Exception as e: return jsonify({"error": str(e)}), 500
@app.route('/cml/wm/manage_capacity', methods=['POST'])
def cml_wm_manage_capacity():
    if not working_memory_instance or not hasattr(working_memory_instance, 'manage_workspace_capacity_and_coherence'): return jsonify({"error": "WM N/A"}), 500
    try: data = request.json; working_memory_instance.manage_workspace_capacity_and_coherence(data.get('new_item_salience')); return jsonify({"status": "capacity_managed", "current_size": len(working_memory_instance.get_workspace_contents())})
    except Exception as e: return jsonify({"error": str(e)}), 500
@app.route('/cml/wm/handle_forgetting', methods=['POST'])
def cml_wm_handle_forgetting():
    if not working_memory_instance or not hasattr(working_memory_instance, 'handle_forgetting'): return jsonify({"error": "WM N/A"}), 500
    try: data = request.json; working_memory_instance.handle_forgetting(data.get('strategy','default')); return jsonify({"status": "forgetting_handled", "strategy": data.get('strategy','default'), "contents": working_memory_instance.get_workspace_contents()})
    except Exception as e: return jsonify({"error": str(e)}), 500
@app.route('/cml/wm/status', methods=['GET'])
def cml_wm_status():
    if not working_memory_instance or not hasattr(working_memory_instance, 'get_module_status'): return jsonify({"error": "WM N/A"}), 500
    try: return jsonify(working_memory_instance.get_module_status())
    except Exception as e: return jsonify({"error": str(e)}), 500

# --- PiaPES API Endpoints ---
# ... (PiaPES routes from previous version) ...
if globals().get("PROMPT_ENGINE_MVP_AVAILABLE"):
    @app.route('/api/pes/prompts', methods=['GET'])
    def api_list_pes_prompts():
        try:
            prompt_infos = []
            if not os.path.exists(PES_FILES_DIR): return jsonify([])
            for filename in os.listdir(PES_FILES_DIR):
                if filename.endswith('.json') and not filename.endswith('.curriculum.json'):
                    filepath = os.path.join(PES_FILES_DIR, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f: data = json.load(f)
                        prompt_infos.append({"filename": filename, "name": data.get('objective', data.get('name', filename)), "version": data.get('version', 'N/A')})
                    except Exception as e: prompt_infos.append({"filename": filename, "name": filename, "version": "Error reading"})
            return jsonify(prompt_infos)
        except Exception as e: return jsonify({"error": "Failed to list PiaPES prompts"}), 500
    @app.route('/api/pes/prompts/<path:filename>', methods=['GET'])
    def api_get_pes_prompt(filename):
        if '..' in filename or filename.startswith('/'): abort(400)
        filepath = os.path.join(PES_FILES_DIR, filename)
        if not (os.path.exists(filepath) and filename.endswith('.json') and not filename.endswith('.curriculum.json')): abort(404)
        try:
            prompt = globals()['load_template'](filepath)
            if prompt and isinstance(prompt, globals()['PiaAGIPrompt']): return jsonify({"filename": filename, "prompt_data": prompt.__dict__})
            abort(500)
        except Exception as e: return jsonify({"error": str(e)}), 500
    @app.route('/api/pes/prompts', methods=['POST'])
    def api_create_pes_prompt():
        if not request.is_json: return jsonify({"error": "Request must be JSON"}), 400
        data = request.get_json(); raw_filename = data.pop('filename', None)
        if raw_filename: filename = sanitize_filename(os.path.splitext(raw_filename)[0]) + ".json"
        elif data.get('objective'): filename = sanitize_filename(data['objective'][:50]) + ".json"
        elif data.get('name'): filename = sanitize_filename(data['name'][:50]) + ".json"
        else: return jsonify({"error": "Filename derivable from 'objective' or 'name' required."}), 400
        filepath = os.path.join(PES_FILES_DIR, filename)
        if os.path.exists(filepath): return jsonify({"error": f"File '{filename}' already exists."}), 409
        try:
            if '__type__' not in data: data['__type__'] = 'PiaAGIPrompt'
            obj = json.loads(json.dumps(data), object_hook=globals()['pia_agi_object_hook'])
            if not isinstance(obj, globals()['PiaAGIPrompt']): return jsonify({"error": "Invalid data structure."}), 400
            globals()['save_template'](obj, filepath)
            return jsonify({"message": f"Prompt '{filename}' created.", "filename": filename}), 201
        except Exception as e: return jsonify({"error": str(e)}), 500
    @app.route('/api/pes/prompts/<path:filename>', methods=['PUT'])
    def api_update_pes_prompt(filename):
        if '..' in filename or filename.startswith('/'): abort(400)
        filepath = os.path.join(PES_FILES_DIR, filename)
        if not (os.path.exists(filepath) and filename.endswith('.json') and not filename.endswith('.curriculum.json')): abort(404)
        if not request.is_json: return jsonify({"error": "Request must be JSON"}), 400
        data = request.get_json()
        try:
            if '__type__' not in data: data['__type__'] = 'PiaAGIPrompt'
            obj = json.loads(json.dumps(data), object_hook=globals()['pia_agi_object_hook'])
            if not isinstance(obj, globals()['PiaAGIPrompt']): return jsonify({"error": "Invalid data structure."}), 400
            globals()['save_template'](obj, filepath)
            return jsonify({"message": f"Prompt '{filename}' updated."})
        except Exception as e: return jsonify({"error": str(e)}), 500
    @app.route('/api/pes/prompts/<path:filename>', methods=['DELETE'])
    def api_delete_pes_prompt(filename):
        if '..' in filename or filename.startswith('/'): abort(400)
        filepath = os.path.join(PES_FILES_DIR, filename)
        if not (os.path.exists(filepath) and filename.endswith('.json') and not filename.endswith('.curriculum.json')): abort(404)
        try: os.remove(filepath); return jsonify({"message": f"Prompt '{filename}' deleted."})
        except Exception as e: return jsonify({"error": str(e)}), 500
    @app.route('/api/pes/prompts/<path:filename>/render', methods=['GET'])
    def api_render_pes_prompt_markdown(filename):
        if '..' in filename or filename.startswith('/'): abort(400)
        filepath = os.path.join(PES_FILES_DIR, filename)
        if not (os.path.exists(filepath) and filename.endswith('.json') and not filename.endswith('.curriculum.json')): abort(404)
        try:
            prompt = globals()['load_template'](filepath)
            if prompt and hasattr(prompt, 'render'): return jsonify({"filename": filename, "markdown": prompt.render()})
            abort(500)
        except Exception as e: return jsonify({"error": str(e)}), 500
    @app.route('/api/pes/curricula', methods=['GET'])
    def api_list_pes_curricula():
        try:
            cur_files = []
            if not os.path.exists(PES_FILES_DIR): return jsonify([])
            for fname in os.listdir(PES_FILES_DIR):
                if fname.endswith('.curriculum.json'):
                    fpath = os.path.join(PES_FILES_DIR, fname)
                    try:
                        with open(fpath, 'r', encoding='utf-8') as f: cdata = json.load(f)
                        cur_files.append({"filename": fname, "name": cdata.get('name',fname), "version": cdata.get('version','N/A')})
                    except: cur_files.append({"filename": fname, "name": fname, "version": "Error"})
            return jsonify(cur_files)
        except Exception as e: return jsonify({"error":"Failed to list curricula"}),500
    @app.route('/api/pes/curricula/<path:filename>', methods=['GET'])
    def api_get_pes_curriculum(filename):
        if '..' in filename or filename.startswith('/'): abort(400)
        if not filename.endswith('.curriculum.json'): abort(400)
        filepath = os.path.join(PES_FILES_DIR, filename)
        if not os.path.exists(filepath): abort(404)
        try:
            cur = globals()['load_template'](filepath)
            if cur and isinstance(cur, globals()['DevelopmentalCurriculum']): return jsonify({"filename": filename, "curriculum_data": cur.__dict__})
            abort(500)
        except Exception as e: return jsonify({"error": str(e)}),500
    @app.route('/api/pes/curricula/<path:filename>/render', methods=['GET'])
    def api_render_pes_curriculum(filename):
        if '..' in filename or filename.startswith('/'): abort(400)
        if not filename.endswith('.curriculum.json'): abort(400)
        filepath = os.path.join(PES_FILES_DIR, filename)
        if not os.path.exists(filepath): abort(404)
        try:
            cur = globals()['load_template'](filepath)
            if cur and hasattr(cur, 'render'): return jsonify({"filename": filename, "markdown": cur.render()})
            abort(500)
        except Exception as e: return jsonify({"error": str(e)}),500
    @app.route('/api/pes/curricula', methods=['POST'])
    def api_create_pes_curriculum():
        if not request.is_json: return jsonify({"error": "Request must be JSON"}), 400
        data = request.get_json(); raw_filename = data.get('filename')
        if not raw_filename or not raw_filename.endswith('.curriculum.json'): return jsonify({"error": "Filename ending with '.curriculum.json' is required."}), 400
        filename = sanitize_filename(os.path.splitext(os.path.splitext(raw_filename)[0])[0]) + ".curriculum.json"
        filepath = os.path.join(PES_FILES_DIR, filename)
        if os.path.exists(filepath): return jsonify({"error": f"File '{filename}' already exists."}), 409
        if '__type__' not in data: data['__type__'] = 'DevelopmentalCurriculum'
        if 'name' not in data or 'steps' not in data: return jsonify({"error": "Missing 'name' or 'steps'."}), 400
        try:
            obj = json.loads(json.dumps(data), object_hook=globals()['pia_agi_object_hook'])
            if not isinstance(obj, globals()['DevelopmentalCurriculum']): return jsonify({"error":"Invalid data structure."}), 400
            globals()['save_template'](obj, filepath)
            return jsonify({"message": f"Curriculum '{filename}' created.", "filename": filename}), 201
        except Exception as e: return jsonify({"error": str(e)}), 500
    @app.route('/api/pes/curricula/<path:filename>', methods=['PUT'])
    def api_update_pes_curriculum_metadata(filename):
        if '..' in filename or filename.startswith('/'): abort(400)
        if not filename.endswith('.curriculum.json'): abort(400)
        filepath = os.path.join(PES_FILES_DIR, filename)
        if not os.path.exists(filepath): abort(404)
        if not request.is_json: return jsonify({"error": "Request must be JSON"}), 400
        data = request.get_json()
        try:
            obj = globals()['load_template'](filepath)
            if not isinstance(obj, globals()['DevelopmentalCurriculum']): return jsonify({"error":"Not a curriculum."}),500
            count = 0
            for field in ['name','description','target_developmental_stage','version','author']:
                if field in data: setattr(obj, field, data[field]); count+=1
            obj.__type__ = "DevelopmentalCurriculum"
            if count > 0: globals()['save_template'](obj, filepath)
            return jsonify({"message": f"Curriculum metadata for '{filename}' updated."}), 200
        except Exception as e: return jsonify({"error": str(e)}),500
else:
    logger.warning("PiaPES API endpoints not defined.")

# --- PiaSE API Endpoints ---
if globals().get("CORE_ENGINE_BASIC_ENGINE_AVAILABLE"): # Check a key PiaSE component
    @app.route('/api/piase/run_simulation', methods=['POST'])
    def piase_run_simulation(): # Standalone test endpoint
        try:
            grid_w, grid_h, goal_p = 5,5,(4,4); walls, start_p, ag_id = [(1,1),(1,2),(2,1),(3,3)],(0,0),"q_agent_1"
            # Ensure QLearningAgent is imported or defined if used here
            QLearningAgent_class = globals().get('QLearningAgent') # Get from globals after import attempts
            GridWorld_class = globals().get('GridWorld')
            BasicSimulationEngine_class = globals().get('BasicSimulationEngine')
            GridWorldVisualizer_class = globals().get('GridWorldVisualizer')

            if not all([QLearningAgent_class, GridWorld_class, BasicSimulationEngine_class]): # GridWorldVisualizer is optional
                return jsonify({"error": "Required PiaSE classes (QLearningAgent, GridWorld, BasicSimulationEngine) not available."}), 503

            env = GridWorld_class(width=grid_w,height=grid_h,walls=walls,goal_position=goal_p,default_agent_id=ag_id,agent_start_pos=start_p)
            eng, q_ag = BasicSimulationEngine_class(), QLearningAgent_class(exploration_rate=0.2)
            ts, rnd_id = time.strftime("%Y%m%d-%H%M%S"), os.urandom(4).hex(); run_dir = f"run_{ts}_{rnd_id}"
            cur_run_out_abs = os.path.join(PIASE_RUNS_OUTPUT_DIR_ABSOLUTE, run_dir); os.makedirs(cur_run_out_abs, exist_ok=True)
            log_f = os.path.join(cur_run_out_abs, "piase_log.jsonl")
            eng.initialize(environment=env, agents={ag_id:q_ag}, scenario_config={"name":"WebAppDefault"}, log_path=log_f)
            
            viz = None
            if GridWorldVisualizer_class: # Check if visualizer class is available
                viz = GridWorldVisualizer_class(env)
            
            img_urls, txt_log = [],["Log:"];
            if viz:
                img_f_init = "s0.png"; img_p_init = os.path.join(cur_run_out_abs,img_f_init); viz.render(title="Init",output_path=img_p_init,step_delay=None)
                img_urls.append(f"/static/{PIASE_RUNS_STATIC_DIR}/{run_dir}/{img_f_init}"); txt_log.append("Init rendered.")
            
            steps, goal_reached, i_s = 50,False,0
            txt_log.append(f"Starting {steps} steps...")
            for i_s_loop in range(steps):
                i_s=i_s_loop; txt_log.append(f"Step {i_s+1}"); eng.run_step();
                cur_pos = env.agent_positions.get(ag_id); txt_log.append(f"Action: {q_ag.last_action if hasattr(q_ag, 'last_action') else 'N/A'}, Pos: {cur_pos}")
                if viz:
                    img_f=f"s{i_s+1}.png";img_p_abs=os.path.join(cur_run_out_abs,img_f);viz.render(title=f"S {i_s+1}",output_path=img_p_abs,step_delay=None)
                    img_urls.append(f"/static/{PIASE_RUNS_STATIC_DIR}/{run_dir}/{img_f}")
                if env.is_done(ag_id): txt_log.append("Goal!");goal_reached=True;break
            txt_log.append("Done." if goal_reached else f"Timeout after {steps} steps.")
            if viz and viz.fig: plt.close(viz.fig)
            return jsonify({"run_id":run_dir,"image_urls":img_urls,"text_log":"\n".join(txt_log),"summary":{"goal":goal_reached,"steps":i_s+1}}),200
        except Exception as e: logger.error(f"PiaSE sim error: {e}",exc_info=True); return jsonify({"error":str(e)}),500
else:
    logger.warning("PiaSE API /api/piase/run_simulation not defined.")

# --- PiaAVT API Endpoints ---
if globals().get("API_AVAILABLE"): # Check flag for PiaAVTAPI
    @app.route('/api/avt/analyze_log_basic', methods=['POST'])
    def avt_analyze_log_basic():
        if 'logFile' not in request.files: return jsonify({"error": "No log file"}), 400
        file = request.files['logFile']
        if file.filename == '': return jsonify({"error": "No selected file"}), 400
        if file and (file.filename.endswith('.json') or file.filename.endswith('.jsonl')):
            fname = secure_filename(file.filename); tmp_f = None
            try:
                tmp_f = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{fname}")
                file.save(tmp_f.name); tmp_f.close()
                avt = globals()['PiaAVTAPI']()
                if not avt.load_logs_from_jsonl(tmp_f.name): return jsonify({"error": "AVT load failed"}), 500
                if avt.get_log_count() == 0: return jsonify({"error": "No valid logs in file"}), 400
                anlyzr = avt.get_analyzer()
                if not anlyzr: return jsonify({"error": "AVT analyzer init failed"}), 500
                counts = anlyzr.count_unique_values('event_type')
                return jsonify({"message":"Analyzed","file":fname,"results":{"event_counts":dict(counts)}}),200
            except Exception as e: return jsonify({"error":str(e)}),500
            finally:
                if tmp_f and tmp_f.name and os.path.exists(tmp_f.name):
                    try: os.remove(tmp_f.name)
                    except: pass
        else: return jsonify({"error": "Invalid file type"}), 400
else:
    logger.warning("PiaAVT API /api/avt/analyze_log_basic not defined.")

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_RUN_PORT', 5001))
    logger.info(f"Starting Flask app on port {port}")
    app.run(debug=True, port=port)

[end of PiaAGI_Research_Tools/WebApp/backend/app.py]
