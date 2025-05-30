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
    *   **Other Sections (as JSON textareas):** `UsersInteractors`, `Workflow/Curriculum Phase`, `Developmental Scaffolding Context`, `CBT AutoTraining Protocol`.
    *   **Initiate Interaction:** Textarea.
*   **Data Handling:** JavaScript on the client-side merges data from specific fields and their corresponding "Advanced JSON" textareas before submitting the complete prompt structure to the backend.
*   **Actions:** "Save Prompt" button (performs POST for new, PUT for existing).

### 2.3 Prompt Detail / Rendered View (`view_prompt.html`)

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
    *   A list of `CurriculumStep` objects, showing Order, Name, Conditions, Notes, and the `prompt_reference` filename.
    *   The `prompt_reference` is a link to the view page for that specific prompt template.
    *   Raw JSON and rendered Markdown for the curriculum object.

### 2.5 Curriculum Creation View (`curriculum_form.html` with `form_mode='create'`)
*   **Purpose:** To allow users to create new `DevelopmentalCurriculum` objects.
*   **Form Fields (Metadata):** `filename` (must end with `.curriculum.json`), `name`, `description`, `target_developmental_stage`, `version`, `author`.
*   **Dynamic Steps Section:**
    *   A container (`div#steps-container`) where users can dynamically add, define, and remove curriculum steps.
    *   Each step includes inputs for: `step_name`, `step_order` (defaults to current count), `step_prompt_reference` (filename of a prompt JSON), `step_conditions` (textarea), and `step_notes` (textarea).
*   **Actions:** "Add Curriculum Step" button, "Remove This Step" button (per step), "Save Curriculum" button (submits to `POST /api/curricula`).

### 2.6 Curriculum Editing View (Metadata Only) (`curriculum_form.html` with `form_mode='edit'`)
*   **Purpose:** To allow users to edit the metadata of existing `DevelopmentalCurriculum` objects.
*   **Form Fields:** Same metadata fields as creation (`name`, `description`, etc.). The `filename` field is read-only.
*   **Steps Management:** The UI for adding, removing, or editing steps is hidden or disabled. A message indicates that steps are preserved and not editable in this mode. Existing steps may be displayed in a read-only format.
*   **Actions:** "Save Curriculum" button (submits to `PUT /api/curricula/<filename>`).

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
    *   Other major sections (Workflow, Scaffolding, CBT) as JSON textareas.
    *   Initiate Interaction.
*   **Buttons:** "Save Prompt". Error/Success message areas.

### 5.3 View Prompt Page (`view_prompt.html`)

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
*   **Steps Section (Create Mode Only):**
    *   Container `div#steps-container`.
    *   "Add Curriculum Step" button.
    *   Each dynamically added step contains inputs for: Step Name, Order, Prompt Reference, Conditions, Notes, and a "Remove" button.
*   **Steps Section (Edit Mode):**
    *   A message indicating steps are not editable here.
    *   Read-only display of existing steps.
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
    *   `PUT /api/curricula/<filename>`: Updates metadata of an existing curriculum from JSON body (ignores steps).
    *   `GET /api/curricula/<filename>/render`: Gets rendered Markdown for a curriculum.
*   **HTML Serving Routes:**
    *   `GET /`: Dashboard.
    *   `GET /create`: Prompt creation form.
    *   `GET /edit/<filename>`: Prompt editing form.
    *   `GET /view/<filename>`: Prompt view page.
    *   `GET /curriculum/create`: Curriculum creation form.
    *   `GET /curriculum/edit/<filename>`: Curriculum metadata editing form.
    *   `GET /curriculum/view/<filename>`: Curriculum view page.

Error handling (404, 400, 500) is implemented for API endpoints. User feedback via Flask `flash` messages for page redirects and JavaScript-driven messages on forms.
