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
            prompt_data_for_form['role_name'] = getattr(role_obj, 'name', None)
            prompt_data_for_form['role_profile'] = getattr(role_obj, 'profile', None)
            # Convert lists to comma-separated strings for the form fields
            prompt_data_for_form['role_skills_focus_str'] = ', '.join(getattr(role_obj, 'skills_focus', None) or [])
            prompt_data_for_form['role_knowledge_domains_active_str'] = ', '.join(getattr(role_obj, 'knowledge_domains_active', None) or [])

            # For executors_json, create a dict of the role excluding CMC, skills_focus, knowledge_domains_active
            excluded_role_keys = {'cognitive_module_configuration', 'skills_focus', 'knowledge_domains_active', 'name', 'profile'}
            role_dict_for_json = {k: v for k, v in role_obj.__dict__.items() if k not in excluded_role_keys}
            # Ensure __type__ is present, even if other fields are stripped for the JSON blob
            role_dict_for_json['__type__'] = role_obj.__class__.__name__
            # If all specific fields are stripped and nothing else is in role_dict_for_json other than __type__,
            # then executors_json might just become {"__type__": "Executors", "role": {"__type__": "Role"}}. This is fine.

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
                    prompt_data_for_form['learning_rate_adaptation_enabled'] = bool(lc.learning_rate_adaptation) # Ensure boolean
        else: # Default empty values if no executors or role
            prompt_data_for_form['role_name'] = "DefaultRole"
            prompt_data_for_form['role_profile'] = ""
            prompt_data_for_form['role_skills_focus_str'] = ""
            prompt_data_for_form['role_knowledge_domains_active_str'] = ""
            prompt_data_for_form['executors_json'] = json.dumps({"__type__": "Executors", "role": {"__type__": "Role", "name": "DefaultRole"}}, indent=2)
            prompt_data_for_form['motivational_biases_text'] = ""
            # Other cognitive fields will be empty/default in the form (e.g. personality_openness etc. will be blank)


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

@app.route('/curriculum/create', methods=['GET'])
def route_create_curriculum_view():
    return render_template('curriculum_form.html', form_title="Create New Curriculum", form_mode="create")

@app.route('/curriculum/edit/<path:filename>', methods=['GET'])
def route_edit_curriculum_view(filename):
    filepath = os.path.join(PROMPT_DIR, filename)
    if not os.path.exists(filepath) or not filename.endswith('.curriculum.json'):
        flash(f"Error: Curriculum file '{filename}' not found for editing.", "error")
        return redirect(url_for('route_dashboard'))

    try:
        curriculum = load_template(filepath)
        if not curriculum or not isinstance(curriculum, DevelopmentalCurriculum):
            flash(f"Error: File '{filename}' is not a valid curriculum for editing.", "error")
            return redirect(url_for('route_dashboard'))

        # Pass curriculum.__dict__ directly as it contains all top-level fields
        # The form template will access them as curriculum_data.name, etc.
        # For steps, they are passed for read-only display in the template.
        return render_template('curriculum_form.html',
                               form_title=f"Edit Curriculum Metadata: {filename}",
                               form_mode="edit",
                               current_filename=filename,
                               curriculum_data=curriculum.__dict__)
    except Exception as e:
        app.logger.error(f"Error loading curriculum {filename} for edit view: {e}")
        flash(f"Error loading curriculum '{filename}' for editing: {str(e)}", "error")
        return redirect(url_for('route_dashboard'))

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

@app.route('/api/curricula', methods=['POST'])
def api_create_curriculum():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # filename for saving is expected in the data payload itself from the client
    filename_from_payload = data.get('filename')
    if not filename_from_payload:
        return jsonify({"error": "Filename is required in the JSON payload."}), 400

    if not filename_from_payload.endswith('.curriculum.json'):
        return jsonify({"error": "Filename must end with '.curriculum.json'"}), 400

    # Sanitize the filename part before the suffix
    base_filename_part = os.path.splitext(os.path.splitext(filename_from_payload)[0])[0]
    # Use sanitize_filename for the base part, but it appends .json, so remove it first
    sanitized_base = sanitize_filename(base_filename_part).replace(".json", "")
    if not sanitized_base or sanitized_base == "unnamed_prompt".replace(".json",""): # Check if sanitization resulted in empty or default
        # if original filename was also problematic, this might lead to "unnamed_prompt.curriculum.json"
        # which is acceptable, but truly empty/invalid needs a specific error
        if not base_filename_part.strip('.-'): # if original was just dots/hyphens
             return jsonify({"error": "Invalid base filename (e.g. just dots/hyphens)."}), 400
        # If sanitize_filename produced "unnamed_prompt", use that as the base
        if sanitized_base == "unnamed_prompt".replace(".json",""):
            sanitized_base = "unnamed_prompt"

    filename = sanitized_base + ".curriculum.json"

    filepath = os.path.join(PROMPT_DIR, filename)
    if os.path.exists(filepath):
        return jsonify({"error": f"Curriculum file '{filename}' already exists."}), 409

    # Preliminary validation of raw data
    required_top_level_fields = {"name": str, "description": str, "steps": list, "__type__": str}
    for field, field_type in required_top_level_fields.items():
        if field not in data:
            return jsonify({"error": f"Missing required top-level field in curriculum data: '{field}'."}), 400
        if not isinstance(data[field], field_type):
            return jsonify({"error": f"Field '{field}' must be of type {field_type.__name__}."}), 400

    if data["__type__"] != "DevelopmentalCurriculum":
        return jsonify({"error": "Invalid __type__ for curriculum data. Expected 'DevelopmentalCurriculum'."}), 400

    if not data["steps"]: # Must have at least one step, or allow empty? For now, let's allow empty.
        pass # Allow empty steps list

    for i, step in enumerate(data["steps"]):
        if not isinstance(step, dict):
            return jsonify({"error": f"Item at steps[{i}] is not a valid step object."}), 400
        required_step_fields = {"name": str, "order": (int, str), "prompt_reference": str, "__type__": str}
        for s_field, s_field_type in required_step_fields.items():
            if s_field not in step:
                return jsonify({"error": f"Missing required field '{s_field}' in step {i+1}."}), 400
            if not isinstance(step[s_field], s_field_type):
                 return jsonify({"error": f"Field '{s_field}' in step {i+1} must be of type {s_field_type}."}), 400
        if step["__type__"] != "CurriculumStep":
            return jsonify({"error": f"Invalid __type__ for step {i+1}. Expected 'CurriculumStep'."}), 400
        try:
            int(step["order"]) # Check if order is convertible to int
        except ValueError:
            return jsonify({"error": f"Field 'order' in step {i+1} must be an integer or string convertible to integer."}), 400


    try:
        reconstructed_json_str = json.dumps(data)
        curriculum_object = json.loads(reconstructed_json_str, object_hook=pia_agi_object_hook)

        if not isinstance(curriculum_object, DevelopmentalCurriculum):
             return jsonify({"error": "Error reconstructing curriculum object. Ensure data structure and __type__ hints are correct."}), 400

        save_template(curriculum_object, filepath)
        return jsonify({"message": f"Curriculum '{filename}' created successfully.", "filename": filename}), 201
    except json.JSONDecodeError as e: # Should be caught by initial parsing if not JSON
        app.logger.error(f"JSONDecodeError creating curriculum {filename}: {e}")
        return jsonify({"error": f"Invalid JSON format provided: {str(e)}"}), 400
    except (TypeError, KeyError, AttributeError, ValueError) as e: # Broader catch for hook issues
        app.logger.error(f"DataStructureError creating curriculum {filename}: {e}")
        return jsonify({"error": f"Error reconstructing curriculum object from data. Ensure all fields are correct and __type__ hints are valid. Details: {str(e)}"}), 400
    except Exception as e:
        app.logger.error(f"Error creating curriculum {filename}: {e}")
        return jsonify({"error": f"Failed to create curriculum: {str(e)}"}), 500

@app.route('/api/curricula/<path:filename>', methods=['PUT'])
def api_update_curriculum_metadata(filename):
    if not filename.endswith('.curriculum.json'):
        abort(400, description="Invalid curriculum filename format for update.")

    filepath = os.path.join(PROMPT_DIR, filename)
    if not os.path.exists(filepath):
        abort(404, description="Curriculum file not found to update.")

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data_to_update = request.get_json()

    try:
        curriculum_obj = load_template(filepath) # Renamed for clarity
        if not isinstance(curriculum_obj, DevelopmentalCurriculum): # Stricter check
            app.logger.error(f"Loaded file '{filename}' is not a valid DevelopmentalCurriculum object.")
            return jsonify({"error": "Loaded file is not a valid curriculum object."}), 500

        allowed_metadata_fields = ['name', 'description', 'target_developmental_stage', 'version', 'author']
        updated_fields_count = 0

        for field in allowed_metadata_fields:
            if field in data_to_update:
                setattr(curriculum_obj, field, data_to_update[field])
                updated_fields_count += 1

        # Preserve __type__ from the loaded object, do not allow client to change it via this metadata endpoint.
        curriculum_obj.__type__ = "DevelopmentalCurriculum"

        if updated_fields_count > 0:
            save_template(curriculum_obj, filepath)
            return jsonify({"message": f"Curriculum metadata for '{filename}' updated successfully.", "filename": filename}), 200
        else:
            return jsonify({"message": f"No recognized metadata fields provided for update in '{filename}'. No changes made."}), 200

    except json.JSONDecodeError as e:
        app.logger.error(f"JSONDecodeError (should not happen here if request.get_json() passed) updating curriculum metadata {filename}: {e}")
        return jsonify({"error": f"Invalid JSON format in request: {str(e)}"}), 400 # Should be caught by request.is_json
    except (TypeError, AttributeError) as e: # Errors during setattr if field is wrong type (should be caught by prompt_engine_mvp setter ideally)
        app.logger.error(f"TypeError/AttributeError updating curriculum metadata {filename}: {e}")
        return jsonify({"error": f"Error setting curriculum attribute. Details: {str(e)}"}), 400
    except Exception as e:
        app.logger.error(f"Error updating curriculum metadata {filename}: {e}")
        return jsonify({"error": f"Failed to update curriculum metadata: {str(e)}"}), 500


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
