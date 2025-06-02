import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI, APIError, AuthenticationError, RateLimitError, APIConnectionError
from flask_cors import CORS
import sys # Added for path modification

# --- Add PiaAGI_Hub to sys.path to allow CML imports ---
# This assumes app.py is in PiaAGI_Hub/WebApp/backend/
# Adjust if the directory structure is different or if CML becomes a proper package
try:
    # Path to PiaAGI_Hub directory from the current file's location (backend)
    # PiaAGI_Hub/WebApp/backend/app.py -> PiaAGI_Hub/
    path_to_piaagi_hub = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if path_to_piaagi_hub not in sys.path:
        sys.path.insert(0, path_to_piaagi_hub)

    from PiaCML.concrete_perception_module import ConcretePerceptionModule
    from PiaCML.concrete_emotion_module import ConcreteEmotionModule
    from PiaCML.concrete_motivational_system_module import ConcreteMotivationalSystemModule
    from PiaCML.concrete_working_memory_module import ConcreteWorkingMemoryModule
except ImportError as e:
    print(f"Error importing CML modules: {e}. Ensure PiaAGI_Hub is in PYTHONPATH or sys.path is correct.")
    # Define dummy classes if import fails, so app can still run and show other routes
    class ConcretePerceptionModule: pass
    class ConcreteEmotionModule: pass
    class ConcreteMotivationalSystemModule: pass
    class ConcreteWorkingMemoryModule: pass
# --- End CML Import ---


# Load environment variables from .env file (if it exists)
load_dotenv()

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# --- CML Module Instantiations ---
# For V1 WebApp, using global instances. Consider session-based or request-based for more advanced use.
perception_module_instance = ConcretePerceptionModule() if 'ConcretePerceptionModule' in globals() else None
emotion_module_instance = ConcreteEmotionModule() if 'ConcreteEmotionModule' in globals() else None
motivational_system_instance = ConcreteMotivationalSystemModule() if 'ConcreteMotivationalSystemModule' in globals() else None
working_memory_instance = ConcreteWorkingMemoryModule(capacity=5) if 'ConcreteWorkingMemoryModule' in globals() else None
# --- End CML Module Instantiations ---

@app.route('/api/hello')
def hello_world():
    return jsonify({'message': 'Hello from Flask backend!'})

@app.route('/api/process_prompt', methods=['POST'])
def process_prompt():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400

        api_key = data.get('apiKey')
        prompt_content = data.get('prompt')
        test_question = data.get('testQuestion')
        llm_model = data.get('llmModel', 'gpt-3.5-turbo')

        if not api_key: return jsonify({"error": "API key is missing"}), 400
        if not prompt_content: return jsonify({"error": "Prompt content is missing"}), 400
        if not test_question: return jsonify({"error": "Test question is missing"}), 400

        client = OpenAI(api_key=api_key)
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
        app.logger.error(f"OpenAI Authentication Error: {e}")
        return jsonify({"error": "OpenAI API Key is invalid or expired."}), 401
    except RateLimitError as e:
        app.logger.error(f"OpenAI Rate Limit Error: {e}")
        return jsonify({"error": "OpenAI API rate limit exceeded. Please try again later."}), 429
    except APIConnectionError as e:
        app.logger.error(f"OpenAI API Connection Error: {e}")
        return jsonify({"error": "Could not connect to OpenAI. Please check your network."}), 500
    except APIError as e:
        app.logger.error(f"OpenAI API Error: {e}")
        return jsonify({"error": f"An OpenAI API error occurred: {e}"}), 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {e}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# --- Routes for ConcretePerceptionModule ---
@app.route('/cml/perception/process', methods=['POST'])
def cml_perception_process():
    if not perception_module_instance: return jsonify({"error": "PerceptionModule not initialized"}), 500
    try:
        data = request.json
        raw_input = data.get('raw_input')
        modality = data.get('modality')
        context = data.get('context', {})
        result = perception_module_instance.process_sensory_input(raw_input, modality, context)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cml/perception/status', methods=['GET'])
def cml_perception_status():
    if not perception_module_instance: return jsonify({"error": "PerceptionModule not initialized"}), 500
    try:
        return jsonify(perception_module_instance.get_module_status())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Routes for ConcreteEmotionModule ---
@app.route('/cml/emotion/appraise', methods=['POST'])
def cml_emotion_appraise():
    if not emotion_module_instance: return jsonify({"error": "EmotionModule not initialized"}), 500
    try:
        data = request.json
        event_info = data.get('event_info')
        context = data.get('context', {})
        result = emotion_module_instance.appraise_situation(event_info, context)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cml/emotion/current', methods=['GET'])
def cml_emotion_current():
    if not emotion_module_instance: return jsonify({"error": "EmotionModule not initialized"}), 500
    try:
        return jsonify(emotion_module_instance.get_current_emotion())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cml/emotion/express', methods=['GET']) # Or POST if context is sent
def cml_emotion_express():
    if not emotion_module_instance: return jsonify({"error": "EmotionModule not initialized"}), 500
    try:
        # context = request.json.get('context', {}) if request.is_json else {} # if context can be sent
        return jsonify(emotion_module_instance.express_emotion(context=None))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cml/emotion/status', methods=['GET'])
def cml_emotion_status():
    if not emotion_module_instance: return jsonify({"error": "EmotionModule not initialized"}), 500
    try:
        return jsonify(emotion_module_instance.get_module_status())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Routes for ConcreteMotivationalSystemModule ---
@app.route('/cml/motivation/manage', methods=['POST'])
def cml_motivation_manage():
    if not motivational_system_instance: return jsonify({"error": "MotivationalSystemModule not initialized"}), 500
    try:
        data = request.json
        action = data.get('action')
        goal_data = data.get('goal_data', {})
        result = motivational_system_instance.manage_goals(action, goal_data)
        return jsonify(result) if isinstance(result, (bool, str, list)) else (jsonify(result) if result is not None else jsonify({"status": "ok_no_return"}) )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cml/motivation/active_goals', methods=['GET'])
def cml_motivation_active_goals():
    if not motivational_system_instance: return jsonify({"error": "MotivationalSystemModule not initialized"}), 500
    try:
        N = request.args.get('N', default=0, type=int)
        min_priority = request.args.get('min_priority', default=0.0, type=float)
        result = motivational_system_instance.get_active_goals(N, min_priority)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cml/motivation/update_state', methods=['POST'])
def cml_motivation_update_state():
    if not motivational_system_instance: return jsonify({"error": "MotivationalSystemModule not initialized"}), 500
    try:
        data = request.json
        result = motivational_system_instance.update_motivation_state(data)
        return jsonify({"success": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cml/motivation/status', methods=['GET'])
def cml_motivation_status():
    if not motivational_system_instance: return jsonify({"error": "MotivationalSystemModule not initialized"}), 500
    try:
        return jsonify(motivational_system_instance.get_module_status())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Routes for ConcreteWorkingMemoryModule ---
@app.route('/cml/wm/add_item', methods=['POST'])
def cml_wm_add_item():
    if not working_memory_instance: return jsonify({"error": "WorkingMemoryModule not initialized"}), 500
    try:
        data = request.json
        item_content = data.get('item_content')
        salience = data.get('salience', 0.5)
        context = data.get('context', {})
        item_id = working_memory_instance.add_item_to_workspace(item_content, salience, context)
        return jsonify({"item_id": item_id, "current_size": len(working_memory_instance.get_workspace_contents())})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cml/wm/remove_item', methods=['POST'])
def cml_wm_remove_item():
    if not working_memory_instance: return jsonify({"error": "WorkingMemoryModule not initialized"}), 500
    try:
        data = request.json
        item_id = data.get('item_id')
        success = working_memory_instance.remove_item_from_workspace(item_id)
        return jsonify({"success": success, "current_size": len(working_memory_instance.get_workspace_contents())})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cml/wm/contents', methods=['GET'])
def cml_wm_contents():
    if not working_memory_instance: return jsonify({"error": "WorkingMemoryModule not initialized"}), 500
    try:
        return jsonify(working_memory_instance.get_workspace_contents())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cml/wm/set_focus', methods=['POST'])
def cml_wm_set_focus():
    if not working_memory_instance: return jsonify({"error": "WorkingMemoryModule not initialized"}), 500
    try:
        data = request.json
        item_id = data.get('item_id')
        success = working_memory_instance.set_active_focus(item_id)
        return jsonify({"success": success, "current_focus": working_memory_instance.get_active_focus()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cml/wm/get_focus', methods=['GET'])
def cml_wm_get_focus():
    if not working_memory_instance: return jsonify({"error": "WorkingMemoryModule not initialized"}), 500
    try:
        return jsonify(working_memory_instance.get_active_focus())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cml/wm/manage_capacity', methods=['POST']) # Explicit call if needed
def cml_wm_manage_capacity():
    if not working_memory_instance: return jsonify({"error": "WorkingMemoryModule not initialized"}), 500
    try:
        data = request.json
        new_item_salience = data.get('new_item_salience') # Optional
        working_memory_instance.manage_workspace_capacity_and_coherence(new_item_salience)
        return jsonify({"status": "capacity_managed", "current_size": len(working_memory_instance.get_workspace_contents())})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cml/wm/handle_forgetting', methods=['POST']) # Explicit call if needed
def cml_wm_handle_forgetting():
    if not working_memory_instance: return jsonify({"error": "WorkingMemoryModule not initialized"}), 500
    try:
        data = request.json
        strategy = data.get('strategy', 'default')
        working_memory_instance.handle_forgetting(strategy)
        return jsonify({"status": "forgetting_handled", "strategy": strategy, "contents": working_memory_instance.get_workspace_contents()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cml/wm/status', methods=['GET'])
def cml_wm_status():
    if not working_memory_instance: return jsonify({"error": "WorkingMemoryModule not initialized"}), 500
    try:
        return jsonify(working_memory_instance.get_module_status())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    # Note: For development, ensure PiaAGI_Hub is in PYTHONPATH or adjust sys.path more robustly
    # if this script is run directly and CML modules are not found.
    # The sys.path modification at the top should help for typical `flask run` scenarios.
    app.run(debug=True, port=port)
