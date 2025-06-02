import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI, APIError, AuthenticationError, RateLimitError, APIConnectionError
from flask_cors import CORS
import sys
import time
import json # For parsing complex query_details if needed

# --- Add PiaAGI_Research_Tools to sys.path to allow CML imports ---
try:
    path_to_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if path_to_project_root not in sys.path:
        sys.path.insert(0, path_to_project_root)

    from PiaCML.concrete_perception_module import ConcretePerceptionModule
    from PiaCML.concrete_emotion_module import ConcreteEmotionModule
    from PiaCML.concrete_motivational_system_module import ConcreteMotivationalSystemModule
    from PiaCML.concrete_working_memory_module import ConcreteWorkingMemoryModule
    from PiaCML.concrete_attention_module import ConcreteAttentionModule
    from PiaCML.concrete_behavior_generation_module import ConcreteBehaviorGenerationModule
    from PiaCML.concrete_communication_module import ConcreteCommunicationModule
    from PiaCML.concrete_learning_module import ConcreteLearningModule
    from PiaCML.concrete_long_term_memory_module import ConcreteLongTermMemoryModule
    from PiaCML.concrete_planning_decision_making_module import ConcretePlanningAndDecisionMakingModule
    from PiaCML.concrete_self_model_module import ConcreteSelfModelModule
    from PiaCML.concrete_tom_module import ConcreteTheoryOfMindModule
    from PiaCML.concrete_world_model import ConcreteWorldModel
except ImportError as e:
    print(f"Error importing CML modules: {e}. Ensure PiaAGI_Research_Tools is in PYTHONPATH or sys.path is correct.")
    # Define dummy classes if import fails
    class ConcretePerceptionModule: pass
    class ConcreteEmotionModule: pass
    class ConcreteMotivationalSystemModule: pass
    class ConcreteWorkingMemoryModule: pass
    class ConcreteAttentionModule: pass
    class ConcreteBehaviorGenerationModule: pass
    class ConcreteCommunicationModule: pass
    class ConcreteLearningModule: pass
    class ConcreteLongTermMemoryModule: pass
    class ConcretePlanningAndDecisionMakingModule: pass
    class ConcreteSelfModelModule: pass
    class ConcreteTheoryOfMindModule: pass
    class ConcreteWorldModel: pass
# --- End CML Import ---

load_dotenv()
app = Flask(__name__)
CORS(app)

# --- CML Module Instantiations ---
perception_module_instance = ConcretePerceptionModule() if 'ConcretePerceptionModule' in globals() else None
emotion_module_instance = ConcreteEmotionModule() if 'ConcreteEmotionModule' in globals() else None
motivational_system_instance = ConcreteMotivationalSystemModule() if 'ConcreteMotivationalSystemModule' in globals() else None
working_memory_instance = ConcreteWorkingMemoryModule(capacity=5) if 'ConcreteWorkingMemoryModule' in globals() else None
attention_module_instance = ConcreteAttentionModule() if 'ConcreteAttentionModule' in globals() else None
behavior_generation_module_instance = ConcreteBehaviorGenerationModule() if 'ConcreteBehaviorGenerationModule' in globals() else None
communication_module_instance = ConcreteCommunicationModule() if 'ConcreteCommunicationModule' in globals() else None
learning_module_instance = ConcreteLearningModule() if 'ConcreteLearningModule' in globals() else None
long_term_memory_instance = ConcreteLongTermMemoryModule() if 'ConcreteLongTermMemoryModule' in globals() else None
planning_module_instance = ConcretePlanningAndDecisionMakingModule() if 'ConcretePlanningAndDecisionMakingModule' in globals() else None
self_model_instance = ConcreteSelfModelModule() if 'ConcreteSelfModelModule' in globals() else None
tom_module_instance = ConcreteTheoryOfMindModule() if 'ConcreteTheoryOfMindModule' in globals() else None
world_model_instance = ConcreteWorldModel() if 'ConcreteWorldModel' in globals() else None
# --- End CML Module Instantiations ---

@app.route('/api/hello')
def hello_world():
    return jsonify({'message': 'Hello from Flask backend!'})

# ... (existing /api/process_prompt route remains unchanged) ...
@app.route('/api/process_prompt', methods=['POST'])
def process_prompt():
    try:
        data = request.get_json()
        if not data: return jsonify({"error": "Invalid JSON payload"}), 400
        api_key = data.get('apiKey')
        prompt_content = data.get('prompt')
        test_question = data.get('testQuestion')
        llm_model = data.get('llmModel', 'gpt-3.5-turbo')
        if not all([api_key, prompt_content, test_question]):
            return jsonify({"error": "Missing required fields: apiKey, prompt, or testQuestion"}), 400
        client = OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model=llm_model,
            messages=[
                {"role": "system", "content": prompt_content},
                {"role": "user", "content": test_question}
            ]
        )
        return jsonify({"response": completion.choices[0].message.content})
    except AuthenticationError as e: return jsonify({"error": "OpenAI API Key is invalid or expired."}), 401
    except RateLimitError as e: return jsonify({"error": "OpenAI API rate limit exceeded."}), 429
    except APIConnectionError as e: return jsonify({"error": "Could not connect to OpenAI."}), 500
    except APIError as e: return jsonify({"error": f"An OpenAI API error occurred: {e}"}), 500
    except Exception as e: return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# --- Routes for ConcretePerceptionModule (Existing) ---
@app.route('/cml/perception/process_sensory_input', methods=['POST'])
def cml_perception_process_sensory_input():
    if not perception_module_instance: return jsonify({"error": "PerceptionModule not initialized"}), 500
    try:
        data = request.json
        result = perception_module_instance.process_sensory_input(data.get('raw_input'), data.get('modality'), data.get('metadata', data.get('context')))
        return jsonify(result)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/perception/extract_features', methods=['POST'])
def cml_perception_extract_features():
    if not perception_module_instance: return jsonify({"error": "PerceptionModule not initialized"}), 500
    try:
        data = request.json
        result = perception_module_instance.extract_features(data.get('processed_input'), data.get('modality'), data.get('config', data.get('context')))
        return jsonify(result)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/perception/generate_structured_percept', methods=['POST'])
def cml_perception_generate_structured_percept():
    if not perception_module_instance: return jsonify({"error": "PerceptionModule not initialized"}), 500
    try:
        data = request.json
        result = perception_module_instance.generate_structured_percept(data.get('features'), data.get('modality'), data.get('context', {}))
        return jsonify(result)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/perception/set_attentional_focus', methods=['POST'])
def cml_perception_set_attentional_focus():
    if not perception_module_instance: return jsonify({"error": "PerceptionModule not initialized"}), 500
    try:
        perception_module_instance.set_attentional_focus(request.json.get('focus_details'))
        return jsonify({"success": True, "message": "Attentional focus set."})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/perception/status', methods=['GET'])
def cml_perception_status():
    if not perception_module_instance: return jsonify({"error": "PerceptionModule not initialized"}), 500
    try: return jsonify(perception_module_instance.get_status())
    except Exception as e: return jsonify({"error": str(e)}), 500

# --- Routes for ConcreteEmotionModule (Existing) ---
@app.route('/cml/emotion/update_emotional_state', methods=['POST'])
def cml_emotion_update_emotional_state():
    if not emotion_module_instance: return jsonify({"error": "EmotionModule not initialized"}), 500
    try:
        data = request.json
        emotion_module_instance.update_emotional_state(data.get('appraisal_info'), data.get('event_source'))
        return jsonify({'success': True, 'new_state_snapshot': emotion_module_instance.get_current_emotional_state()})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/emotion/get_current_emotional_state', methods=['GET'])
def cml_emotion_get_current_emotional_state():
    if not emotion_module_instance: return jsonify({"error": "EmotionModule not initialized"}), 500
    try: return jsonify(emotion_module_instance.get_current_emotional_state())
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/emotion/express', methods=['GET'])
def cml_emotion_express():
    if not emotion_module_instance: return jsonify({"error": "EmotionModule not initialized"}), 500
    try: return jsonify(emotion_module_instance.express_emotion(context=None))
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/emotion/regulate_emotion', methods=['POST'])
def cml_emotion_regulate_emotion():
    if not emotion_module_instance: return jsonify({"error": "EmotionModule not initialized"}), 500
    try:
        data = request.json
        result = emotion_module_instance.regulate_emotion(data.get('strategy'), data.get('target_emotion_details'))
        return jsonify({'success': result, 'attempted_strategy': data.get('strategy')})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/emotion/get_emotional_influence_on_cognition', methods=['GET'])
def cml_emotion_get_emotional_influence():
    if not emotion_module_instance: return jsonify({"error": "EmotionModule not initialized"}), 500
    try: return jsonify(emotion_module_instance.get_emotional_influence_on_cognition())
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/emotion/set_personality_profile', methods=['POST'])
def cml_emotion_set_personality_profile():
    if not emotion_module_instance: return jsonify({"error": "EmotionModule not initialized"}), 500
    try:
        emotion_module_instance.set_personality_profile(request.json.get('profile'))
        return jsonify({"success": True, "message": "Personality profile updated."})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/emotion/status', methods=['GET'])
def cml_emotion_status():
    if not emotion_module_instance: return jsonify({"error": "EmotionModule not initialized"}), 500
    try: return jsonify(emotion_module_instance.get_status())
    except Exception as e: return jsonify({"error": str(e)}), 500

# --- Routes for ConcreteAttentionModule (Existing) ---
@app.route('/cml/attention/direct_attention', methods=['POST'])
def cml_attention_direct_attention():
    if not attention_module_instance: return jsonify({"error": "AttentionModule not initialized"}), 500
    try:
        data = request.json
        success = attention_module_instance.direct_attention(data.get('focus_target'), data.get('priority'), data.get('context'))
        return jsonify({"success": success})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/attention/filter_information', methods=['POST'])
def cml_attention_filter_information():
    if not attention_module_instance: return jsonify({"error": "AttentionModule not initialized"}), 500
    try:
        data = request.json
        filtered_stream = attention_module_instance.filter_information(data.get('information_stream'), data.get('current_focus'))
        return jsonify(filtered_stream)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/attention/manage_cognitive_load', methods=['POST'])
def cml_attention_manage_cognitive_load():
    if not attention_module_instance: return jsonify({"error": "AttentionModule not initialized"}), 500
    try:
        data = request.json
        action_result = attention_module_instance.manage_cognitive_load(data.get('current_load'), data.get('capacity_thresholds'))
        return jsonify(action_result)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/attention/get_attentional_state', methods=['GET'])
def cml_attention_get_attentional_state():
    if not attention_module_instance: return jsonify({"error": "AttentionModule not initialized"}), 500
    try: return jsonify(attention_module_instance.get_attentional_state())
    except Exception as e: return jsonify({"error": str(e)}), 500

# --- Routes for ConcreteBehaviorGenerationModule (Existing) ---
@app.route('/cml/behavior/generate_behavior', methods=['POST'])
def cml_behavior_generate_behavior():
    if not behavior_generation_module_instance: return jsonify({"error": "BehaviorGenerationModule not initialized"}), 500
    try:
        data = request.json
        result = behavior_generation_module_instance.generate_behavior(data.get('action_plan'), data.get('context'))
        return jsonify(result)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/behavior/status', methods=['GET'])
def cml_behavior_status():
    if not behavior_generation_module_instance: return jsonify({"error": "BehaviorGenerationModule not initialized"}), 500
    try: return jsonify(behavior_generation_module_instance.get_status())
    except Exception as e: return jsonify({"error": str(e)}), 500

# --- Routes for ConcreteCommunicationModule (Existing) ---
@app.route('/cml/communication/process_incoming', methods=['POST'])
def cml_communication_process_incoming():
    if not communication_module_instance: return jsonify({"error": "CommunicationModule not initialized"}), 500
    try:
        data = request.json
        result = communication_module_instance.process_incoming_communication(data.get('raw_input'), data.get('source_modality'), data.get('context'))
        return jsonify(result)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/communication/generate_outgoing', methods=['POST'])
def cml_communication_generate_outgoing():
    if not communication_module_instance: return jsonify({"error": "CommunicationModule not initialized"}), 500
    try:
        data = request.json
        result = communication_module_instance.generate_outgoing_communication(data.get('abstract_message'), data.get('target_recipient_id'), data.get('desired_effect'), data.get('context'))
        return jsonify(result)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/communication/manage_dialogue_state', methods=['POST'])
def cml_communication_manage_dialogue_state():
    if not communication_module_instance: return jsonify({"error": "CommunicationModule not initialized"}), 500
    try:
        data = request.json
        result = communication_module_instance.manage_dialogue_state(data.get('dialogue_id'), data.get('new_turn_info'), data.get('action'))
        return jsonify({'success': result})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/communication/apply_strategy', methods=['POST'])
def cml_communication_apply_strategy():
    if not communication_module_instance: return jsonify({"error": "CommunicationModule not initialized"}), 500
    try:
        data = request.json
        result = communication_module_instance.apply_communication_strategy(data.get('current_communication_goal'), data.get('recipient_model'), data.get('dialogue_context'), data.get('available_strategies'))
        return jsonify(result)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/communication/status', methods=['GET'])
def cml_communication_status():
    if not communication_module_instance: return jsonify({"error": "CommunicationModule not initialized"}), 500
    try: return jsonify(communication_module_instance.get_status())
    except Exception as e: return jsonify({"error": str(e)}), 500

# --- Routes for ConcreteLearningModule (Existing) ---
@app.route('/cml/learning/learn', methods=['POST'])
def cml_learning_learn():
    if not learning_module_instance: return jsonify({"error": "LearningModule not initialized"}), 500
    try:
        data = request.json
        result = learning_module_instance.learn(data.get('data'), data.get('learning_paradigm'), data.get('context'))
        return jsonify(result)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/learning/process_feedback', methods=['POST'])
def cml_learning_process_feedback():
    if not learning_module_instance: return jsonify({"error": "LearningModule not initialized"}), 500
    try:
        data = request.json
        success = learning_module_instance.process_feedback(data.get('feedback_data'), data.get('learning_context_id'))
        return jsonify({'success': success})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/learning/consolidate_knowledge', methods=['POST'])
def cml_learning_consolidate_knowledge():
    if not learning_module_instance: return jsonify({"error": "LearningModule not initialized"}), 500
    try:
        data = request.json
        success = learning_module_instance.consolidate_knowledge(data.get('learned_item_ids'), data.get('target_memory_system'))
        return jsonify({'success': success})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/learning/status', methods=['GET'])
def cml_learning_status():
    if not learning_module_instance: return jsonify({"error": "LearningModule not initialized"}), 500
    try:
        task_id = request.args.get('task_id')
        return jsonify(learning_module_instance.get_learning_status(task_id))
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/learning/apply_ethical_guardrails', methods=['POST'])
def cml_learning_apply_ethical_guardrails():
    if not learning_module_instance: return jsonify({"error": "LearningModule not initialized"}), 500
    try:
        data = request.json
        is_permissible = learning_module_instance.apply_ethical_guardrails(data.get('potential_learning_outcome'), data.get('context'))
        return jsonify({'is_permissible': is_permissible})
    except Exception as e: return jsonify({"error": str(e)}), 500

# --- Routes for ConcreteMotivationalSystemModule (Existing) ---
@app.route('/cml/motivation/manage', methods=['POST'])
def cml_motivation_manage():
    if not motivational_system_instance: return jsonify({"error": "MotivationalSystemModule not initialized"}), 500
    try:
        data = request.json
        result = motivational_system_instance.manage_goals(data.get('action'), data.get('goal_data', {}))
        return jsonify(result) if isinstance(result, (bool, str, list, dict)) else jsonify({"status": "ok_no_return", "result": result})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/motivation/active_goals', methods=['GET'])
def cml_motivation_active_goals():
    if not motivational_system_instance: return jsonify({"error": "MotivationalSystemModule not initialized"}), 500
    try:
        N = request.args.get('N', default=0, type=int)
        min_priority = request.args.get('min_priority', default=0.0, type=float)
        return jsonify(motivational_system_instance.get_active_goals(N, min_priority))
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/motivation/update_state', methods=['POST'])
def cml_motivation_update_state():
    if not motivational_system_instance: return jsonify({"error": "MotivationalSystemModule not initialized"}), 500
    try:
        success = motivational_system_instance.update_motivation_state(request.json)
        return jsonify({"success": success})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/motivation/status', methods=['GET'])
def cml_motivation_status():
    if not motivational_system_instance: return jsonify({"error": "MotivationalSystemModule not initialized"}), 500
    try: return jsonify(motivational_system_instance.get_status())
    except Exception as e: return jsonify({"error": str(e)}), 500

# --- Routes for ConcreteWorkingMemoryModule (Existing) ---
@app.route('/cml/wm/add_item', methods=['POST'])
def cml_wm_add_item():
    if not working_memory_instance: return jsonify({"error": "WorkingMemoryModule not initialized"}), 500
    try:
        data = request.json
        success = working_memory_instance.add_item_to_workspace(data.get('item_content'), data.get('salience', 0.5), data.get('context', {}))
        item_id = None; contents = working_memory_instance.get_workspace_contents()
        if success and contents: item_id = contents[-1].get('id')
        return jsonify({"success": success, "item_id": item_id, "current_size": len(contents)})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/wm/remove_item', methods=['POST'])
def cml_wm_remove_item():
    if not working_memory_instance: return jsonify({"error": "WorkingMemoryModule not initialized"}), 500
    try:
        data = request.json
        success = working_memory_instance.remove_item_from_workspace(data.get('item_id'))
        return jsonify({"success": success, "current_size": len(working_memory_instance.get_workspace_contents())})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/wm/contents', methods=['GET'])
def cml_wm_contents():
    if not working_memory_instance: return jsonify({"error": "WorkingMemoryModule not initialized"}), 500
    try: return jsonify(working_memory_instance.get_workspace_contents())
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/wm/set_focus', methods=['POST'])
def cml_wm_set_focus():
    if not working_memory_instance: return jsonify({"error": "WorkingMemoryModule not initialized"}), 500
    try:
        data = request.json
        success = working_memory_instance.set_active_focus(data.get('item_id'))
        return jsonify({"success": success, "current_focus": working_memory_instance.get_active_focus()})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/wm/get_focus', methods=['GET'])
def cml_wm_get_focus():
    if not working_memory_instance: return jsonify({"error": "WorkingMemoryModule not initialized"}), 500
    try: return jsonify(working_memory_instance.get_active_focus())
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/wm/manage_capacity', methods=['POST'])
def cml_wm_manage_capacity():
    if not working_memory_instance: return jsonify({"error": "WorkingMemoryModule not initialized"}), 500
    try:
        working_memory_instance.manage_workspace_capacity_and_coherence(request.json.get('new_item_salience'))
        return jsonify({"status": "capacity_managed", "current_size": len(working_memory_instance.get_workspace_contents())})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/wm/handle_forgetting', methods=['POST'])
def cml_wm_handle_forgetting():
    if not working_memory_instance: return jsonify({"error": "WorkingMemoryModule not initialized"}), 500
    try:
        strategy = request.json.get('strategy', 'default')
        working_memory_instance.handle_forgetting(strategy)
        return jsonify({"status": "forgetting_handled", "strategy": strategy, "contents": working_memory_instance.get_workspace_contents()})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/wm/status', methods=['GET'])
def cml_wm_status():
    if not working_memory_instance: return jsonify({"error": "WorkingMemoryModule not initialized"}), 500
    try: return jsonify(working_memory_instance.get_status())
    except Exception as e: return jsonify({"error": str(e)}), 500

# --- Routes for ConcreteLongTermMemoryModule ---
@app.route('/cml/ltm/store', methods=['POST'])
def cml_ltm_store():
    if not long_term_memory_instance: return jsonify({"error": "LTM not initialized"}), 500
    try:
        data = request.json
        item_id = long_term_memory_instance.store(data.get('information'), data.get('context'))
        return jsonify({"item_id": item_id})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/ltm/retrieve', methods=['POST'])
def cml_ltm_retrieve():
    if not long_term_memory_instance: return jsonify({"error": "LTM not initialized"}), 500
    try:
        data = request.json
        results = long_term_memory_instance.retrieve(data.get('query'), data.get('criteria'))
        return jsonify(results)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/ltm/delete_memory', methods=['POST'])
def cml_ltm_delete():
    if not long_term_memory_instance: return jsonify({"error": "LTM not initialized"}), 500
    try:
        success = long_term_memory_instance.delete_memory(request.json.get('memory_id'))
        return jsonify({"success": success})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/ltm/manage_capacity', methods=['POST'])
def cml_ltm_manage_capacity():
    if not long_term_memory_instance: return jsonify({"error": "LTM not initialized"}), 500
    try:
        long_term_memory_instance.manage_capacity()
        return jsonify({"success": True, "message": "LTM manage_capacity called."})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/ltm/handle_forgetting', methods=['POST'])
def cml_ltm_handle_forgetting():
    if not long_term_memory_instance: return jsonify({"error": "LTM not initialized"}), 500
    try:
        long_term_memory_instance.handle_forgetting(request.json.get('strategy', 'default'))
        return jsonify({"success": True, "message": "LTM handle_forgetting called."})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/ltm/store_semantic', methods=['POST'])
def cml_ltm_store_semantic():
    if not long_term_memory_instance: return jsonify({"error": "LTM not initialized"}), 500
    try:
        data = request.json
        item_id = long_term_memory_instance.store_semantic_knowledge(data.get('knowledge_item'), data.get('context'))
        return jsonify({"item_id": item_id}) # store_semantic_knowledge returns ID in concrete impl
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/ltm/get_semantic', methods=['POST'])
def cml_ltm_get_semantic():
    if not long_term_memory_instance: return jsonify({"error": "LTM not initialized"}), 500
    try:
        data = request.json
        results = long_term_memory_instance.get_semantic_knowledge(data.get('query'), data.get('criteria'))
        return jsonify(results)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/ltm/store_episodic', methods=['POST'])
def cml_ltm_store_episodic():
    if not long_term_memory_instance: return jsonify({"error": "LTM not initialized"}), 500
    try:
        data = request.json
        item_id = long_term_memory_instance.store_episodic_experience(data.get('event_data'), data.get('context'))
        return jsonify({"item_id": item_id}) # store_episodic_experience returns ID
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/ltm/get_episodic', methods=['POST'])
def cml_ltm_get_episodic():
    if not long_term_memory_instance: return jsonify({"error": "LTM not initialized"}), 500
    try:
        data = request.json
        results = long_term_memory_instance.get_episodic_experience(data.get('query'), data.get('criteria'))
        return jsonify(results)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/ltm/store_procedural', methods=['POST'])
def cml_ltm_store_procedural():
    if not long_term_memory_instance: return jsonify({"error": "LTM not initialized"}), 500
    try:
        data = request.json
        item_id = long_term_memory_instance.store_procedural_skill(data.get('skill_data'), data.get('context'))
        return jsonify({"item_id": item_id})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/ltm/get_procedural', methods=['POST'])
def cml_ltm_get_procedural():
    if not long_term_memory_instance: return jsonify({"error": "LTM not initialized"}), 500
    try:
        data = request.json
        skill_info = long_term_memory_instance.get_procedural_skill(data.get('skill_name'))
        return jsonify(skill_info if skill_info else {"error": "Skill not found"})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/ltm/consolidate_memory', methods=['POST'])
def cml_ltm_consolidate_memory():
    if not long_term_memory_instance: return jsonify({"error": "LTM not initialized"}), 500
    try:
        data = request.json
        long_term_memory_instance.consolidate_memory(data.get('type_to_consolidate', 'all'), data.get('intensity', 'normal'))
        return jsonify({"success": True, "message": "LTM consolidate_memory called."})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/ltm/status', methods=['GET'])
def cml_ltm_status():
    if not long_term_memory_instance: return jsonify({"error": "LTM not initialized"}), 500
    try: return jsonify(long_term_memory_instance.get_status())
    except Exception as e: return jsonify({"error": str(e)}), 500

# --- Routes for ConcretePlanningAndDecisionMakingModule ---
@app.route('/cml/planning/generate_possible_actions', methods=['POST'])
def cml_planning_generate_actions():
    if not planning_module_instance: return jsonify({"error": "PlanningModule not initialized"}), 500
    try:
        data = request.json
        actions = planning_module_instance.generate_possible_actions(data.get('current_state'), data.get('goals'))
        return jsonify(actions)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/planning/create_plan', methods=['POST'])
def cml_planning_create_plan():
    if not planning_module_instance: return jsonify({"error": "PlanningModule not initialized"}), 500
    try:
        data = request.json
        plan = planning_module_instance.create_plan(data.get('goal'), data.get('world_model_context'), data.get('self_model_context'))
        return jsonify(plan)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/planning/evaluate_plan', methods=['POST'])
def cml_planning_evaluate_plan():
    if not planning_module_instance: return jsonify({"error": "PlanningModule not initialized"}), 500
    try:
        data = request.json
        evaluation = planning_module_instance.evaluate_plan(data.get('plan'), data.get('world_model_context'), data.get('self_model_context'))
        return jsonify(evaluation)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/planning/select_plan', methods=['POST'])
def cml_planning_select_plan():
    if not planning_module_instance: return jsonify({"error": "PlanningModule not initialized"}), 500
    try:
        data = request.json
        selected_plan_eval = planning_module_instance.select_plan(data.get('evaluated_plans'), data.get('selection_criteria'))
        return jsonify(selected_plan_eval if selected_plan_eval else {"message": "No suitable plan selected."} )
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/planning/status', methods=['GET'])
def cml_planning_status():
    if not planning_module_instance: return jsonify({"error": "PlanningModule not initialized"}), 500
    try: return jsonify(planning_module_instance.get_status())
    except Exception as e: return jsonify({"error": str(e)}), 500

# --- Routes for ConcreteSelfModelModule ---
@app.route('/cml/self_model/get_representation', methods=['GET'])
def cml_self_model_get_representation():
    if not self_model_instance: return jsonify({"error": "SelfModel not initialized"}), 500
    try:
        aspect = request.args.get('aspect')
        query_details_str = request.args.get('query_details')
        query_details = json.loads(query_details_str) if query_details_str else None
        representation = self_model_instance.get_self_representation(aspect, query_details)
        return jsonify(representation)
    except json.JSONDecodeError: return jsonify({"error": "Invalid JSON format for query_details"}), 400
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/self_model/update_representation', methods=['POST'])
def cml_self_model_update_representation():
    if not self_model_instance: return jsonify({"error": "SelfModel not initialized"}), 500
    try:
        data = request.json
        success = self_model_instance.update_self_representation(data.get('aspect'), data.get('update_data'), data.get('source_of_update'))
        return jsonify({"success": success})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/self_model/evaluate_performance', methods=['POST'])
def cml_self_model_evaluate_performance():
    if not self_model_instance: return jsonify({"error": "SelfModel not initialized"}), 500
    try:
        data = request.json
        result = self_model_instance.evaluate_self_performance(data.get('task_description'), data.get('outcome'), data.get('criteria'))
        return jsonify(result)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/self_model/get_confidence', methods=['GET'])
def cml_self_model_get_confidence():
    if not self_model_instance: return jsonify({"error": "SelfModel not initialized"}), 500
    try:
        domain = request.args.get('domain')
        specific_query = request.args.get('specific_query')
        if not domain: return jsonify({"error": "Missing 'domain' parameter"}), 400
        confidence = self_model_instance.get_confidence_level(domain, specific_query)
        return jsonify({"domain": domain, "specific_query": specific_query, "confidence_level": confidence})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/self_model/check_ethical_consistency', methods=['POST'])
def cml_self_model_check_ethical_consistency():
    if not self_model_instance: return jsonify({"error": "SelfModel not initialized"}), 500
    try:
        data = request.json
        result = self_model_instance.check_ethical_consistency(data.get('proposed_action_or_plan'), data.get('context'))
        return jsonify(result)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/self_model/reflect_on_experience', methods=['POST'])
def cml_self_model_reflect_on_experience():
    if not self_model_instance: return jsonify({"error": "SelfModel not initialized"}), 500
    try:
        data = request.json
        result = self_model_instance.reflect_on_experience(data.get('experience_log'))
        return jsonify(result)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/self_model/get_cognitive_load_assessment', methods=['GET'])
def cml_self_model_get_cognitive_load():
    if not self_model_instance: return jsonify({"error": "SelfModel not initialized"}), 500
    try: return jsonify(self_model_instance.get_cognitive_load_assessment())
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/self_model/status', methods=['GET'])
def cml_self_model_status():
    if not self_model_instance: return jsonify({"error": "SelfModel not initialized"}), 500
    try: return jsonify(self_model_instance.get_status())
    except Exception as e: return jsonify({"error": str(e)}), 500

# --- Routes for ConcreteTheoryOfMindModule ---
@app.route('/cml/tom/infer_mental_state', methods=['POST'])
def cml_tom_infer_mental_state():
    if not tom_module_instance: return jsonify({"error": "ToMModule not initialized"}), 500
    try:
        data = request.json
        result = tom_module_instance.infer_mental_state(data.get('agent_id'), data.get('observable_data'), data.get('context'))
        return jsonify(result)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/tom/update_agent_model', methods=['POST'])
def cml_tom_update_agent_model():
    if not tom_module_instance: return jsonify({"error": "ToMModule not initialized"}), 500
    try:
        data = request.json
        success = tom_module_instance.update_agent_model(data.get('agent_id'), data.get('new_data'))
        return jsonify({"success": success})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/tom/get_agent_model', methods=['GET'])
def cml_tom_get_agent_model():
    if not tom_module_instance: return jsonify({"error": "ToMModule not initialized"}), 500
    try:
        agent_id = request.args.get('agent_id')
        if not agent_id: return jsonify({"error": "Missing 'agent_id' parameter"}), 400
        model = tom_module_instance.get_agent_model(agent_id)
        return jsonify(model if model else {"message": "Agent model not found."})
    except Exception as e: return jsonify({"error": str(e)}), 500

# --- Routes for ConcreteWorldModel ---
@app.route('/cml/world_model/update_from_perception', methods=['POST'])
def cml_world_model_update_from_perception():
    if not world_model_instance: return jsonify({"error": "WorldModel not initialized"}), 500
    try:
        data = request.json
        success = world_model_instance.update_from_perception(data.get('percept_data'), data.get('timestamp'))
        return jsonify({"success": success})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/world_model/query_world_state', methods=['POST'])
def cml_world_model_query_world_state():
    if not world_model_instance: return jsonify({"error": "WorldModel not initialized"}), 500
    try:
        data = request.json
        result = world_model_instance.query_world_state(data.get('query_params'))
        return jsonify(result)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/world_model/get_entity_representation', methods=['GET'])
def cml_world_model_get_entity_representation():
    if not world_model_instance: return jsonify({"error": "WorldModel not initialized"}), 500
    try:
        entity_id = request.args.get('entity_id')
        if not entity_id: return jsonify({"error": "Missing 'entity_id' parameter"}), 400
        representation = world_model_instance.get_entity_representation(entity_id)
        return jsonify(representation if representation else {"message": "Entity not found."})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/world_model/update_entity_state', methods=['POST'])
def cml_world_model_update_entity_state():
    if not world_model_instance: return jsonify({"error": "WorldModel not initialized"}), 500
    try:
        data = request.json
        success = world_model_instance.update_entity_state(data.get('entity_id'), data.get('new_state_info'), data.get('timestamp'))
        return jsonify({"success": success})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/world_model/predict_future_state', methods=['POST'])
def cml_world_model_predict_future_state():
    if not world_model_instance: return jsonify({"error": "WorldModel not initialized"}), 500
    try:
        data = request.json
        result = world_model_instance.predict_future_state(data.get('action_sequence'), data.get('current_state_override'), data.get('time_horizon'))
        return jsonify(result)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/world_model/get_social_model', methods=['GET'])
def cml_world_model_get_social_model():
    if not world_model_instance: return jsonify({"error": "WorldModel not initialized"}), 500
    try:
        agent_id = request.args.get('agent_id')
        if not agent_id: return jsonify({"error": "Missing 'agent_id' parameter"}), 400
        model = world_model_instance.get_social_model_for_agent(agent_id)
        return jsonify(model if model else {"message": "Social model not found."})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/world_model/update_social_model', methods=['POST'])
def cml_world_model_update_social_model():
    if not world_model_instance: return jsonify({"error": "WorldModel not initialized"}), 500
    try:
        data = request.json
        success = world_model_instance.update_social_model(data.get('agent_id'), data.get('new_social_info'), data.get('timestamp'))
        return jsonify({"success": success})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/world_model/manage_uncertainty', methods=['POST'])
def cml_world_model_manage_uncertainty():
    if not world_model_instance: return jsonify({"error": "WorldModel not initialized"}), 500
    try:
        data = request.json
        result = world_model_instance.manage_uncertainty(data.get('scope'), data.get('uncertainty_data'), data.get('query_uncertainty', False))
        return jsonify(result if data.get('query_uncertainty') else {"success": result is None} )
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/world_model/check_consistency', methods=['POST'])
def cml_world_model_check_consistency():
    if not world_model_instance: return jsonify({"error": "WorldModel not initialized"}), 500
    try:
        data = request.json
        result = world_model_instance.check_consistency(data.get('scope'))
        return jsonify(result)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/cml/world_model/status', methods=['GET'])
def cml_world_model_status():
    if not world_model_instance: return jsonify({"error": "WorldModel not initialized"}), 500
    try: return jsonify(world_model_instance.get_world_model_status())
    except Exception as e: return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    app.run(debug=True, port=port)
