import os
import sys
import json
import re
from flask import Flask, request, jsonify, abort, render_template, flash, redirect, url_for

# --- Add PiaPES directory to sys.path ---
# This allows importing prompt_engine_mvp
# Adjust the path depth as necessary depending on where the script is run from.
# Assuming this script is in PiaAGI_Hub/PiaPES/web_app/
PES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PES_DIR not in sys.path:
    sys.path.insert(0, PES_DIR)

# Now import from prompt_engine_mvp
try:
    from prompt_engine_mvp import (
        PiaAGIPrompt, BaseElement,
        save_template, load_template,
        # Import other classes if needed for direct instantiation from more complex JSON
        SystemRules, Requirements, UsersInteractors, Executors, Role,
        CognitiveModuleConfiguration, PersonalityConfig, MotivationalBias,
        EmotionalProfile, LearningModuleConfig, Workflow, WorkflowStep,
        DevelopmentalScaffolding, CBTAutoTraining,
        DevelopmentalCurriculum, CurriculumStep, # Added curriculum classes
        pia_agi_object_hook # Important for loading
    )
except ImportError as e:
    print(f"Error importing from prompt_engine_mvp: {e}", file=sys.stderr)
    print(f"Current sys.path: {sys.path}", file=sys.stderr)
    print(f"PES_DIR: {PES_DIR}", file=sys.stderr)
    # Fallback for local testing if the above path adjustment isn't perfect
    try:
        # This assumes prompt_engine_mvp.py is in the same directory as web_app's parent
        # (i.e. in PiaPES directory)
        from prompt_engine_mvp import (
            PiaAGIPrompt, BaseElement, save_template, load_template, pia_agi_object_hook,
            SystemRules, Requirements, Role, Executors, CognitiveModuleConfiguration
        )
        print("Successfully imported using fallback path logic.", file=sys.stderr)
    except ImportError:
        raise e # Re-raise the original error if fallback also fails

app = Flask(__name__)
PROMPT_DIR = os.path.join(os.path.dirname(__file__), 'prompt_files')

if not os.path.exists(PROMPT_DIR):
    os.makedirs(PROMPT_DIR)

def sanitize_filename(name):
    """Sanitizes a string to be a safe filename component."""
    # Remove characters that are not alphanumeric, whitespace, hyphen, or underscore
    name = re.sub(r'[^\w\s-]', '', str(name)).strip()
    # Replace whitespace and multiple hyphens/underscores with a single hyphen
    name = re.sub(r'[-\s_]+', '-', name)
    # Remove leading/trailing hyphens and dots
    name = name.strip('-.')
    # Prevent names that are just dots or empty after sanitization
    if not name or all(c == '.' for c in name):
        name = "unnamed_prompt"
    return name + ".json"

# --- HTML Serving Routes ---

@app.route('/')
def route_dashboard():
    return render_template('index.html')

@app.route('/create')
def route_create_prompt_view():
    return render_template('prompt_form.html', form_title="Create New Prompt")

@app.route('/edit/<path:filename>')
def route_edit_prompt_view(filename):
    filepath = os.path.join(PROMPT_DIR, filename)
    if not os.path.exists(filepath):
        flash(f"Error: Prompt file '{filename}' not found.", "error")
        return redirect(url_for('route_dashboard'))

    try:
        prompt = load_template(filepath)
        if not prompt:
            flash(f"Error: Could not load or parse prompt '{filename}'.", "error")
            return redirect(url_for('route_dashboard'))

        # Prepare data for the form
        prompt_data_for_form = {'filename': filename}

        # Populate simple attributes from PiaAGIPrompt root
        for key in ['target_agi', 'developmental_stage_target', 'author', 'version', 'date', 'objective', 'initiate_interaction']:
            prompt_data_for_form[key] = getattr(prompt, key, None)

        # SystemRules: specific fields + full JSON
        sr = getattr(prompt, 'system_rules', None)
        if sr:
            prompt_data_for_form['system_rules_language'] = sr.language
            prompt_data_for_form['system_rules_output_format'] = sr.output_format
            prompt_data_for_form['system_rules_json'] = json.dumps(sr.__dict__, cls=app.config['PiaAGIEncoder'], indent=2)
        else:
            prompt_data_for_form['system_rules_language'] = "English" # Default
            prompt_data_for_form['system_rules_output_format'] = "Natural language" # Default
            prompt_data_for_form['system_rules_json'] = ""


        # Requirements: specific fields + full JSON
        req = getattr(prompt, 'requirements', None)
        if req:
            prompt_data_for_form['requirements_goal'] = req.goal
            prompt_data_for_form['requirements_background_context'] = req.background_context
            prompt_data_for_form['requirements_json'] = json.dumps(req.__dict__, cls=app.config['PiaAGIEncoder'], indent=2)
        else:
            prompt_data_for_form['requirements_goal'] = ""
            prompt_data_for_form['requirements_background_context'] = ""
            prompt_data_for_form['requirements_json'] = ""

        # UsersInteractors, Workflow, Scaffolding, CBT: remain as full JSON for now
        for key in ['users_interactors', 'workflow_or_curriculum_phase',
                    'developmental_scaffolding_context', 'cbt_autotraining_protocol']:
            value = getattr(prompt, key, None)
            prompt_data_for_form[key + '_json'] = json.dumps(value.__dict__, cls=app.config['PiaAGIEncoder'], indent=2) if value else ""

        # Executors (Role specific fields) and CognitiveModuleConfiguration (specific fields)
        executors_obj = getattr(prompt, 'executors', None)
        role_obj = None
        if executors_obj and hasattr(executors_obj, 'role') and executors_obj.role: # Check if 'role' attribute exists
            role_obj = executors_obj.role
            prompt_data_for_form['role_name'] = role_obj.name
            prompt_data_for_form['role_profile'] = role_obj.profile

            # For executors_json, create a dict of the role excluding CMC, then wrap in Executors dict
            role_dict_for_json = {k: v for k, v in role_obj.__dict__.items() if k != 'cognitive_module_configuration'}
            if '__type__' not in role_dict_for_json: role_dict_for_json['__type__'] = role_obj.__class__.__name__

            executors_shell_for_json = {
                "__type__": executors_obj.__class__.__name__,
                "role": role_dict_for_json
            }
            prompt_data_for_form['executors_json'] = json.dumps(executors_shell_for_json, cls=app.config['PiaAGIEncoder'], indent=2)

            cmc = getattr(role_obj, 'cognitive_module_configuration', None)
            if cmc:
                if hasattr(cmc, 'personality_config') and cmc.personality_config:
                    pc = cmc.personality_config
                    prompt_data_for_form['personality_openness'] = pc.ocean_openness
                    prompt_data_for_form['personality_conscientiousness'] = pc.ocean_conscientiousness
                    prompt_data_for_form['personality_extraversion'] = pc.ocean_extraversion
                    prompt_data_for_form['personality_agreeableness'] = pc.ocean_agreeableness
                    prompt_data_for_form['personality_neuroticism'] = pc.ocean_neuroticism

                if hasattr(cmc, 'motivational_bias_config') and cmc.motivational_bias_config and cmc.motivational_bias_config.biases:
                    biases = cmc.motivational_bias_config.biases
                    prompt_data_for_form['motivational_biases_text'] = ", ".join([f"{k}:{v}" for k,v in biases.items()])
                else:
                    prompt_data_for_form['motivational_biases_text'] = ""

                if hasattr(cmc, 'emotional_profile_config') and cmc.emotional_profile_config:
                    ep = cmc.emotional_profile_config
                    prompt_data_for_form['emotional_baseline_valence'] = ep.baseline_valence
                    prompt_data_for_form['emotional_reactivity_to_failure'] = ep.reactivity_to_failure_intensity
                    prompt_data_for_form['emotional_empathy_target'] = ep.empathy_level_target

                if hasattr(cmc, 'learning_module_config') and cmc.learning_module_config:
                    lc = cmc.learning_module_config
                    prompt_data_for_form['learning_primary_mode'] = lc.primary_learning_mode
                    prompt_data_for_form['learning_rate_adaptation_enabled'] = bool(lc.learning_rate_adaptation)
        else: # Default empty values if no executors or role
            prompt_data_for_form['role_name'] = "DefaultRole"
            prompt_data_for_form['role_profile'] = ""
            prompt_data_for_form['executors_json'] = json.dumps({"__type__": "Executors", "role": {"__type__": "Role", "name": "DefaultRole"}}, indent=2)
            prompt_data_for_form['motivational_biases_text'] = ""
            # Other cognitive fields will be empty/default in the form


        return render_template('prompt_form.html',
                               form_title=f"Edit Prompt: {filename}",
                               prompt_data=prompt_data_for_form,
                               prompt_filename_for_edit=filename)
    except Exception as e:
        app.logger.error(f"Error loading prompt {filename} for edit: {e}")
        flash(f"Error loading prompt '{filename}': {str(e)}", "error")
        return redirect(url_for('route_dashboard'))

@app.route('/view/<path:filename>')
def route_view_prompt(filename):
    # Check if file exists, could also be done by relying on API to 404
    filepath = os.path.join(PROMPT_DIR, filename)
    if not os.path.exists(filepath):
        flash(f"Error: Prompt file '{filename}' not found.", "error")
        return redirect(url_for('route_dashboard'))
    return render_template('view_prompt.html', filename=filename)

@app.route('/curriculum/view/<path:filename>')
def route_view_curriculum(filename):
    filepath = os.path.join(PROMPT_DIR, filename)
    if not os.path.exists(filepath) or not filename.endswith('.curriculum.json'):
        flash(f"Error: Curriculum file '{filename}' not found.", "error")
        return redirect(url_for('route_dashboard'))
    # Pass curriculum object to template for direct rendering of details, JS can fetch full data if needed for interactivity
    try:
        curriculum = load_template(filepath)
        if not curriculum or not isinstance(curriculum, DevelopmentalCurriculum):
            flash(f"Error: File '{filename}' is not a valid curriculum.", "error")
            return redirect(url_for('route_dashboard'))
        return render_template('view_curriculum.html', filename=filename, curriculum=curriculum)
    except Exception as e:
        app.logger.error(f"Error loading curriculum {filename} for view: {e}")
        flash(f"Error loading curriculum '{filename}': {str(e)}", "error")
        return redirect(url_for('route_dashboard'))


# --- API Endpoints ---

@app.route('/api/prompts', methods=['GET'])
def api_list_prompts():
    try:
        prompt_infos = []
        for filename in os.listdir(PROMPT_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(PROMPT_DIR, filename)
                try:
                    with open(filepath, 'r') as f:
                        # Partially load JSON to get name/objective and version without full object reconstruction
                        data = json.load(f)
                        name = data.get('objective', data.get('name', filename)) # Use objective or name if available
                        version = data.get('version', 'N/A')
                        prompt_infos.append({
                            "filename": filename,
                            "name": name,
                            "version": version
                        })
                except Exception as e:
                    app.logger.warn(f"Could not parse metadata from {filename}: {e}")
                    prompt_infos.append({"filename": filename, "name": filename, "version": "Error reading"})
        return jsonify(prompt_infos)
    except Exception as e:
        app.logger.error(f"Error listing prompts: {e}")
        return jsonify({"error": "Failed to list prompts"}), 500

@app.route('/api/prompts/<path:filename>', methods=['GET'])
def api_get_prompt(filename):
    filepath = os.path.join(PROMPT_DIR, filename)
    if not os.path.exists(filepath):
        abort(404, description="Prompt file not found.")

    try:
        prompt = load_template(filepath)
        if prompt:
            # Return data in a structure expected by the form's JS
            return jsonify({"filename": filename, "prompt_data": prompt.__dict__})
        else:
            abort(500, description="Failed to load or parse prompt template.")
    except Exception as e:
        app.logger.error(f"Error getting prompt {filename}: {e}")
        return jsonify({"error": f"Failed to get prompt: {str(e)}"}), 500

@app.route('/api/prompts', methods=['POST'])
def create_prompt():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    filename_in_data = data.pop('filename', None) # Pop filename if provided in JSON body

    if filename_in_data:
        filename = sanitize_filename(os.path.splitext(filename_in_data)[0]) # Sanitize and add .json
    elif data.get('objective'):
        filename = sanitize_filename(data['objective'][:50]) # Max 50 chars from objective
    elif data.get('name'): # If 'name' field from a Role or other element is top-level
         filename = sanitize_filename(data['name'][:50])
    else:
        # Fallback if no suitable field for filename derivation
        return jsonify({"error": "Filename must be provided in JSON body as 'filename' or derivable from 'objective' or 'name'."}), 400

    filepath = os.path.join(PROMPT_DIR, filename)
    if os.path.exists(filepath):
        # If file exists and this is POST, it's a conflict unless it's an intentional "save as new"
        # For now, simple approach: POST is for new, if exists, conflict.
        return jsonify({"error": f"File '{filename}' already exists. Consider a different name or use PUT to update an existing file."}), 409

    try:
        # Reconstruct the object using the object_hook
        # This assumes the incoming JSON data is a valid __dict__ representation
        # including __type__ fields for all custom objects.
        # The client would typically send JSON from a previously loaded (and possibly modified) object.

        # For MVP, we trust the client to send a valid __dict__ structure
        # that pia_agi_object_hook can handle.
        # A more robust way would be to instantiate PiaAGIPrompt and manually populate fields
        # from 'data', which is safer against arbitrary JSON structures.

        # Attempt to reconstruct the object using the hook
        # First, ensure __type__ is present for the root object if not already
        if '__type__' not in data:
            data['__type__'] = 'PiaAGIPrompt' # Assume root is PiaAGIPrompt if not specified

        # The object_hook expects a dictionary.
        # We pass the entire data dict to json.loads(json.dumps(data)) to simulate loading it from a file string.
        # This is a bit of a workaround to reuse the existing object_hook logic.
        # A more direct approach would be to have a from_dict class method on BaseElement.
        reconstructed_json_str = json.dumps(data) # Ensures data is a string for loads
        prompt_object = json.loads(reconstructed_json_str, object_hook=pia_agi_object_hook)

        if not isinstance(prompt_object, BaseElement):
             return jsonify({"error": "Invalid prompt data structure after reconstruction. Ensure correct __type__ hints and fields."}), 400

        save_template(prompt_object, filepath)
        return jsonify({"message": f"Prompt '{filename}' created successfully.", "filename": filename}), 201
    except json.JSONDecodeError as e:
        app.logger.error(f"JSONDecodeError creating prompt {filename}: {e}")
        return jsonify({"error": f"Invalid JSON format provided: {str(e)}"}), 400
    except (TypeError, KeyError, AttributeError) as e: # Catch errors from object_hook or attribute access
        app.logger.error(f"DataStructureError creating prompt {filename}: {e}")
        return jsonify({"error": f"Invalid prompt data structure. Check __type__ hints and field completeness/names. Details: {str(e)}"}), 400
    except Exception as e:
        app.logger.error(f"Error creating prompt {filename}: {e}")
        return jsonify({"error": f"Failed to create prompt: {str(e)}"}), 500

@app.route('/api/prompts/<path:filename>', methods=['PUT'])
def api_update_prompt(filename):
    filepath = os.path.join(PROMPT_DIR, filename)
    if not os.path.exists(filepath):
        abort(404, description="Prompt file not found to update.")

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    try:
        # Similar to create, reconstruct the object from JSON data
        if '__type__' not in data:
            data['__type__'] = 'PiaAGIPrompt' # Assume root is PiaAGIPrompt

        reconstructed_json_str = json.dumps(data) # Ensures data is a string for loads
        prompt_object = json.loads(reconstructed_json_str, object_hook=pia_agi_object_hook)

        if not isinstance(prompt_object, BaseElement):
             return jsonify({"error": "Invalid prompt data structure after reconstruction. Ensure correct __type__ hints and fields."}), 400

        save_template(prompt_object, filepath)
        return jsonify({"message": f"Prompt '{filename}' updated successfully."})
    except json.JSONDecodeError as e:
        app.logger.error(f"JSONDecodeError updating prompt {filename}: {e}")
        return jsonify({"error": f"Invalid JSON format provided: {str(e)}"}), 400
    except (TypeError, KeyError, AttributeError) as e: # Catch errors from object_hook or attribute access
        app.logger.error(f"DataStructureError updating prompt {filename}: {e}")
        return jsonify({"error": f"Invalid prompt data structure. Check __type__ hints and field completeness/names. Details: {str(e)}"}), 400
    except Exception as e:
        app.logger.error(f"Error updating prompt {filename}: {e}")
        return jsonify({"error": f"Failed to update prompt: {str(e)}"}), 500

@app.route('/api/prompts/<path:filename>', methods=['DELETE'])
def api_delete_prompt(filename):
    filepath = os.path.join(PROMPT_DIR, filename)
    if not os.path.exists(filepath):
        abort(404, description="Prompt file not found to delete.")

    try:
        os.remove(filepath)
        return jsonify({"message": f"Prompt '{filename}' deleted successfully."})
    except Exception as e:
        app.logger.error(f"Error deleting prompt {filename}: {e}")
        return jsonify({"error": f"Failed to delete prompt: {str(e)}"}), 500

@app.route('/api/prompts/<path:filename>/render', methods=['GET'])
def api_render_prompt_markdown(filename):
    filepath = os.path.join(PROMPT_DIR, filename)
    if not os.path.exists(filepath):
        abort(404, description="Prompt file not found.")

    try:
        prompt = load_template(filepath)
        if prompt:
            markdown_content = prompt.render()
            return jsonify({"filename": filename, "markdown": markdown_content})
        else:
            abort(500, description="Failed to load or parse prompt template for rendering.")
    except Exception as e:
        app.logger.error(f"Error rendering prompt {filename}: {e}")
        return jsonify({"error": f"Failed to render prompt: {str(e)}"}), 500


@app.route('/api/curricula', methods=['GET'])
def api_list_curricula():
    try:
        curriculum_files = []
        for filename in os.listdir(PROMPT_DIR):
            if filename.endswith('.curriculum.json'): # Specific suffix for curricula
                filepath = os.path.join(PROMPT_DIR, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        name = data.get('name', filename) # Use curriculum name if available
                        version = data.get('version', 'N/A')
                        curriculum_files.append({
                            "filename": filename,
                            "name": name,
                            "version": version
                        })
                except Exception as e:
                    app.logger.warn(f"Could not parse metadata from curriculum {filename}: {e}")
                    curriculum_files.append({"filename": filename, "name": filename, "version": "Error reading"})
        return jsonify(curriculum_files)
    except Exception as e:
        app.logger.error(f"Error listing curricula: {e}")
        return jsonify({"error": "Failed to list curricula"}), 500

@app.route('/api/curricula/<path:filename>', methods=['GET'])
def api_get_curriculum(filename):
    if not filename.endswith('.curriculum.json'):
        abort(400, description="Invalid curriculum filename format.")

    filepath = os.path.join(PROMPT_DIR, filename)
    if not os.path.exists(filepath):
        abort(404, description="Curriculum file not found.")

    try:
        curriculum = load_template(filepath)
        if curriculum and isinstance(curriculum, DevelopmentalCurriculum): # Ensure it's the correct type
            return jsonify({"filename": filename, "curriculum_data": curriculum.__dict__})
        else:
            abort(500, description="Failed to load or parse curriculum file, or incorrect type.")
    except Exception as e:
        app.logger.error(f"Error getting curriculum {filename}: {e}")
        return jsonify({"error": f"Failed to get curriculum: {str(e)}"}), 500

@app.route('/api/curricula/<path:filename>/render', methods=['GET'])
def api_render_curriculum(filename):
    if not filename.endswith('.curriculum.json'):
        abort(400, description="Invalid curriculum filename format.")

    filepath = os.path.join(PROMPT_DIR, filename)
    if not os.path.exists(filepath):
        abort(404, description="Curriculum file not found.")

    try:
        curriculum = load_template(filepath)
        if curriculum and isinstance(curriculum, DevelopmentalCurriculum):
            markdown_content = curriculum.render()
            return jsonify({"filename": filename, "markdown": markdown_content})
        else:
            abort(500, description="Failed to load or parse curriculum for rendering, or incorrect type.")
    except Exception as e:
        app.logger.error(f"Error rendering curriculum {filename}: {e}")
        return jsonify({"error": f"Failed to render curriculum: {str(e)}"}), 500

if __name__ == '__main__':
    # Ensure the prompt_files directory exists
    if not os.path.exists(PROMPT_DIR):
        os.makedirs(PROMPT_DIR)
        print(f"Created directory: {PROMPT_DIR}")

    # Add PiaAGIEncoder to app config for use in render_template if needed for complex objects
    # (though direct JSON stringification is used in route_edit_prompt_view)
    app.config['PiaAGIEncoder'] = PiaAGIEncoder

    # Set a secret key for flashing messages
    app.secret_key = os.urandom(24)

    app.run(debug=True, port=5001)
