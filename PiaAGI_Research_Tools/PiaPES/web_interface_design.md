<!-- PiaAGI AGI Research Framework Document -->
# PiaPES Web Interface - Conceptual Design

## 1. Introduction

### 1.1 Purpose

This document outlines the conceptual design for a basic web-based user interface (UI) for the PiaAGI Prompt Engineering Suite (PiaPES). The primary purpose of this web interface is to provide a user-friendly, operational platform for interacting with the core functionalities of PiaPES, particularly the `prompt_engine_mvp.py`. It aims to make the creation, management, and inspection of PiaAGI Guiding Prompts and Developmental Curricula more accessible, especially for users who may prefer a graphical interface over direct script interaction.

### 1.2 Target Users

*   **PiaAGI Researchers & Developers:** Individuals actively working on designing, testing, and refining prompts and curricula for PiaAGI agents.
*   **AI Prompt Engineers:** Users focusing on the practical aspects of prompt construction and management.

### 1.3 Scope

This design document focuses on the **initial, minimal viable product (MVP)** for the web interface. The scope is intentionally limited to core functionalities to ensure feasibility for an early release. More advanced features are considered out of scope for this initial version but may be incorporated in future iterations.

## 2. Core Functionalities

The web interface will provide the following core functionalities:

### 2.1 Dashboard / Listing View

*   **Purpose:** To provide an overview of all available prompt templates and developmental curricula.
*   **Display:**
    *   A list (e.g., table view) of prompt templates (`*.json` files) and curricula (`*.curriculum.json` files) found in a predefined local server directory (`prompt_files/`).
    *   **Information per item:**
        *   Filename.
        *   Prompt/Curriculum Name (extracted from 'objective' or 'name' field in JSON).
        *   Version (from 'version' field in JSON).
    *   **Actions per item:**
        *   **Prompts:** "View/Render" link, "Edit" link, "Delete" button.
        *   **Curricula:** "View Details" link, "Edit Metadata" link.
*   **Global Actions:**
    *   "Create New Prompt" button.
    *   "Create New Curriculum" button.

### 2.2 Prompt Creation / Editing View (`prompt_form.html`)

*   **Purpose:** To allow users to create new `PiaAGIPrompt` objects or edit existing ones through a web form.
*   **Form Fields:**
    *   **Basic Metadata:** `filename` (read-only on edit), `author`, `version`, `objective`, `target_agi`, `developmental_stage_target`, `date`.
    *   **System Rules:** Specific inputs for `language`, `output_format`. An "Advanced System Rules JSON" textarea.
    *   **Requirements:** Specific inputs for `goal`, `background_context`. An "Advanced Requirements JSON" textarea.
    *   **Role (within Executors):** Specific inputs for `role_name`, `role_profile`, and comma-separated text inputs for `skills_focus` and `knowledge_domains_active`. An "Advanced Executors JSON" textarea for other role attributes (e.g., `role_specific_rules`).
    *   **Cognitive Module Configuration (within Role):** Dedicated fieldsets and inputs for:
        *   Personality (OCEAN scores).
        *   Motivational Biases (comma-separated key:value pairs text input).
        *   Emotional Profile (baseline_valence, reactivity_to_failure, empathy_target).
        *   Learning Module Config (primary_mode, learning_rate_adaptation_enabled checkbox).
    *   **Workflow Steps:** A dynamic UI allows users to add, remove, and edit individual workflow steps. Each step has fields for `name`, `action_directive`, `module_focus` (comma-separated), `expected_outcome_internal`, and `expected_output_external`. An "Advanced Workflow JSON" textarea is also available for more complex configurations, which will be supplemented or overridden by UI-defined steps.
    *   **Developmental Scaffolding Context:** Specific input fields are provided for `current_developmental_goal` (textarea), `scaffolding_techniques_employed` (comma-separated text), and `feedback_level_from_overseer`. An "Advanced Dev. Scaffolding JSON" textarea allows for further customization.
    *   **Other Sections (as JSON textareas):** `UsersInteractors`, `CBT AutoTraining Protocol`.
    *   **Initiate Interaction:** Textarea.
*   **Data Handling:** JavaScript on the client-side merges data from specific fields (including dynamic steps) and their corresponding "Advanced JSON" textareas before submitting the complete prompt structure to the backend.
*   **Actions:** "Save Prompt" button, "Save as New Template" button.

### 2.3 Basic Prompt Template Management
*   **Load from Template (in Create Mode):**
    *   A dedicated fieldset at the top of the `prompt_form.html` (when creating a new prompt).
    *   Contains a dropdown (`loadTemplateSelect`) populated with existing prompt filenames.
    *   A "Load Selected Template" button (`loadTemplateButton`) fetches the selected prompt's data and populates the form fields.
    *   The main `filename` field of the form remains empty or gets a "copy_of..." suggestion, requiring the user to set a new filename.
*   **Save as New Template:**
    *   Achieved via the "Save as New Template" button on the prompt form (visible in both create and edit modes).
    *   This action ensures the prompt is saved as a new file, requiring the user to set a unique filename in the main `filename` field if it's not already different from an existing one.
    *   In 'create' mode, if a template is loaded, the user can simply change the suggested `filename` and use the main "Save Prompt" button.

### 2.4 Prompt Detail / Rendered View (`view_prompt.html`)

*   **Purpose:** To display the full content of a selected prompt and its rendered Markdown.
*   **Display:**
    *   Filename.
    *   Raw JSON data of the prompt.
    *   Rendered Markdown output of the prompt.
*   **Actions:** Links to "Edit this Prompt" and "Back to Dashboard".

### 2.4 Curriculum Viewing (Read-Only) (`view_curriculum.html`)

*   **Purpose:** To display the structure and content of `DevelopmentalCurriculum` objects.
*   **Display:**
    *   Curriculum metadata: Name, Description, Target Developmental Stage, Version, Author.
    *   A list of `CurriculumStep` objects, showing Order, Name, Conditions, Notes, and the `prompt_reference`.
    *   The `prompt_reference` (filename of the referenced prompt) is displayed, and ideally, is a link to view that prompt.
    *   Raw JSON and rendered Markdown for the curriculum object.

### 2.5 Curriculum Creation View (`curriculum_form.html` with `form_mode='create'`)
*   **Purpose:** To allow users to create new `DevelopmentalCurriculum` objects.
*   **Form Fields (Metadata):** `filename` (must end with `.curriculum.json`), `name`, `description`, `target_developmental_stage`, `version`, `author`.
*   **Dynamic Steps Section:**
    *   A container (`div#steps-container`) where users can dynamically add, define, and remove curriculum steps.
    *   Each step includes inputs for: `step_name`, `step_order` (defaults to current count), `step_prompt_reference` (a dropdown select populated with available prompt filenames), `step_conditions` (textarea), and `step_notes` (textarea).
*   **Actions:** "Add Curriculum Step" button, "Remove This Step" button (per step), "Save Curriculum" button (submits to `POST /api/curricula`).

### 2.6 Curriculum Editing View (`curriculum_form.html` with `form_mode='edit'`)
*   **Purpose:** To allow users to edit the metadata and steps of existing `DevelopmentalCurriculum` objects.
*   **Form Fields:** Same metadata fields as creation (`name`, `description`, etc.). The `filename` field is read-only.
*   **Dynamic Steps Section:**
    *   Existing steps are loaded and displayed in the same dynamic UI as the creation form, allowing modification, removal, and addition of new steps.
    *   `step_prompt_reference` for existing and new steps is a dropdown select populated with available prompt filenames.
*   **Actions:** "Add Curriculum Step" button, "Remove This Step" button (per step), "Save Curriculum" button (submits to `PUT /api/curricula/<filename>` with the full curriculum structure including updated steps).

## 3. Non-Goals for Initial Version

*   **Advanced GUI for JSON sections:** Complex JSON structures (beyond those with specific fields) are still edited in textareas.
*   **Direct Git Integration through the UI.**
*   **Complex User Management & Granular Permissions.**
*   **Visual Curriculum Designer.**
*   **Full UI-based editing of existing curriculum steps** (only metadata editing is supported for existing curricula; steps are preserved).
*   **Prompt Evaluation Triggering/Dashboard.**
*   **Importing from Markdown.**

## 4. Technology Stack (Proposal)

*   **Backend:** Python with Flask (using `prompt_engine_mvp.py`).
*   **Frontend:** HTML, CSS, JavaScript (vanilla JS for API calls and basic DOM manipulation).
*   **Data Storage:** JSON files on the server's filesystem (`prompt_files/`).
*   **Templating Engine:** Jinja2.

## 5. Page Mockups/Wireframes (Descriptive)

### 5.1 Dashboard Page (`index.html`)

*   **Layout:** Header, "Create New Prompt" button, "Create New Curriculum" button. Two main sections: "Available Prompts" and "Available Curricula".
*   **Prompts List:** Each item shows Name (from objective/name), Version, Filename, and links for "View/Render", "Edit", "Delete".
*   **Curricula List:** Each item shows Name, Version, Filename, and links for "View Details" and "Edit Metadata".

### 5.2 Create/Edit Prompt Page (`prompt_form.html`)

*   **Layout:** Header ("Create New Prompt" or "Edit Prompt: [Filename]"). Single form.
*   **Sections (Fieldsets):**
    *   Basic Info (Filename (readonly if editing), Author, Version, Objective, Target AGI, etc.).
    *   System Rules (specific fields for language/output + advanced JSON textarea).
    *   Requirements (specific fields for goal/context + advanced JSON textarea).
    *   Users/Interactors (JSON textarea).
    *   Executor Role Details (specific fields for name/profile, comma-separated skills_focus & knowledge_domains_active + advanced JSON textarea for other role attributes).
    *   Cognitive Module Configuration (dedicated subsections with specific inputs).
    *   **Workflow Steps:** A container (`div#workflow-steps-container`) for dynamically adding/editing/removing workflow steps. Each step has its own set of inputs (name, action_directive, etc.). An "Add Workflow Step" button is present. An "Advanced Workflow JSON" textarea is available.
    *   **Developmental Scaffolding Context:** Specific input fields for `current_developmental_goal`, `scaffolding_techniques_employed`, `feedback_level_from_overseer`. An "Advanced Dev. Scaffolding JSON" textarea is available.
    *   Other major sections (CBT) as JSON textareas.
    *   Initiate Interaction.
*   **Buttons:** "Save Prompt", "Save as New Template". Error/Success message areas.
*   **(If in 'create' mode):** A "Load from Template" fieldset at the top with a dropdown and "Load" button.

### 5.3 Basic Prompt Template Management (Part of Prompt Form on Create/Edit Page)
*   **Load from Template:**
    *   Visual: Positioned at the top of the "Create New Prompt" page. A fieldset containing a `select` dropdown listing available prompts and a "Load Selected Template" button.
    *   Interaction: Selecting a prompt and clicking "Load" populates the main form. Filename field is cleared or suggests a copy name.
*   **Save as New Template:**
    *   Visual: A distinct button, "Save as New Template", on the prompt form.
    *   Interaction: User must provide a new filename (if not already different from an existing one). Submits the current form data to create a new prompt file.

### 5.4 View Prompt Page (`view_prompt.html`)

*   **Layout:** Header ("Prompt Details: [Filename]"). Links to Dashboard and Edit.
*   Displays raw JSON data in a `<pre>` block.
*   Displays rendered Markdown output in a `<pre>` block.

### 5.4 View Curriculum Page (`view_curriculum.html`)

*   **Layout:** Header ("Curriculum: [Name/Filename]"). Link to Dashboard.
*   Displays curriculum metadata (Name, Description, Target Stage, Version, Author).
*   Lists steps, each showing Order, Name, Prompt Reference (as a link to its view page), Conditions, and Notes.
*   Displays raw JSON and rendered Markdown for the curriculum.

### 5.5 Create/Edit Curriculum Page (`curriculum_form.html`)
*   **Layout:** Header ("Create New Curriculum" or "Edit Curriculum Metadata: [Filename]"). Single form.
*   **Fields for Metadata:** Filename (readonly if editing), Name, Description, Target Stage, Version, Author.
*   **Steps Section (Both Create and Edit Mode):**
    *   Container `div#steps-container`.
    *   "Add Curriculum Step" button.
    *   Each dynamically added/edited step contains inputs for: Step Name, Order, Prompt Reference (as a dropdown select populated with available prompt filenames), Conditions, Notes, and a "Remove" button.
*   **Buttons:** "Save Curriculum". Error/Success message areas.


## 6. Backend API Endpoints (Conceptual - Flask Routes)

*   **Prompts:**
    *   `GET /api/prompts`: Lists all prompts with details (filename, name, version).
    *   `POST /api/prompts`: Creates a new prompt from JSON body.
    *   `GET /api/prompts/<filename>`: Gets JSON data for a specific prompt.
    *   `PUT /api/prompts/<filename>`: Updates an existing prompt from JSON body.
    *   `DELETE /api/prompts/<filename>`: Deletes a prompt file.
    *   `GET /api/prompts/<filename>/render`: Gets rendered Markdown for a prompt.
*   **Curricula:**
    *   `GET /api/curricula`: Lists all curricula with details (filename, name, version).
    *   `POST /api/curricula`: Creates a new curriculum from JSON body (expects full structure including steps).
    *   `GET /api/curricula/<filename>`: Gets JSON data for a specific curriculum.
    *   `PUT /api/curricula/<filename>`: Updates an existing curriculum from JSON body (expects full structure including steps for complete replacement/update).
    *   `GET /api/curricula/<filename>/render`: Gets rendered Markdown for a curriculum.
*   **HTML Serving Routes:**
    *   `GET /`: Dashboard.
    *   `GET /create`: Prompt creation form.
    *   `GET /edit/<filename>`: Prompt editing form.
    *   `GET /view/<filename>`: Prompt view page.
    *   `GET /curriculum/create`: Curriculum creation form.
    *   `GET /curriculum/edit/<filename>`: Curriculum editing form (for both metadata and steps).
    *   `GET /curriculum/view/<filename>`: Curriculum view page.

Error handling (404, 400, 500) is implemented for API endpoints. User feedback via Flask `flash` messages for page redirects and JavaScript-driven messages on forms.

---
Return to [PiaAGI Core Document](../../PiaAGI.md) | [Project README](../../README.md)
