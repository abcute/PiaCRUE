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
        *   **Curricula:** "View Details" link.
*   **Global Actions:**
    *   "Create New Prompt" button.

### 2.2 Prompt Creation / Editing View (`prompt_form.html`)

*   **Purpose:** To allow users to create new `PiaAGIPrompt` objects or edit existing ones through a web form.
*   **Form Fields:**
    *   **Basic Metadata:** `filename` (read-only on edit), `author`, `version`, `objective`, `target_agi`, `developmental_stage_target`, `date`.
    *   **System Rules:** Specific inputs for `language`, `output_format`. An "Advanced System Rules JSON" textarea for other/full JSON.
    *   **Requirements:** Specific inputs for `goal`, `background_context`. An "Advanced Requirements JSON" textarea.
    *   **Role (within Executors):** Specific inputs for `role_name`, `role_profile`. An "Advanced Executors JSON" textarea (for other role attributes like skills, knowledge, rules; Cognitive Config is separate).
    *   **Cognitive Module Configuration:** Dedicated fieldsets and inputs for:
        *   Personality (OCEAN scores: openness, conscientiousness, extraversion, agreeableness, neuroticism).
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
*   **Scope:** Creation and editing of curricula via the UI are not part of the MVP.

## 3. Non-Goals for Initial Version

*   **Advanced GUI for JSON sections:** Complex JSON structures (beyond those with specific fields) are still edited in textareas.
*   **Direct Git Integration through the UI.**
*   **Complex User Management & Granular Permissions.**
*   **Visual Curriculum Designer** or UI-based curriculum editing.
*   **Prompt Evaluation Triggering/Dashboard.**
*   **Importing from Markdown.**

## 4. Technology Stack (Proposal)

*   **Backend:** Python with Flask (using `prompt_engine_mvp.py`).
*   **Frontend:** HTML, CSS, JavaScript (vanilla JS for API calls and basic DOM manipulation).
*   **Data Storage:** JSON files on the server's filesystem (`prompt_files/`).
*   **Templating Engine:** Jinja2.

## 5. Page Mockups/Wireframes (Descriptive)

### 5.1 Dashboard Page (`index.html`)

*   **Layout:** Header, "Create New Prompt" button. Two main sections: "Available Prompts" and "Available Curricula".
*   **Prompts List:** Each item shows Name (from objective/name), Version, Filename, and links for "View/Render", "Edit", "Delete".
*   **Curricula List:** Each item shows Name, Version, Filename, and a link for "View Details".

### 5.2 Create/Edit Prompt Page (`prompt_form.html`)

*   **Layout:** Header ("Create New Prompt" or "Edit Prompt: [Filename]"). Single form.
*   **Sections (Fieldsets):**
    *   Basic Info (Filename, Author, Version, Objective, Target AGI, etc.).
    *   System Rules (specific fields + advanced JSON textarea).
    *   Requirements (specific fields + advanced JSON textarea).
    *   Users/Interactors (JSON textarea).
    *   Executor Role Details (specific fields for name/profile + advanced JSON textarea for other role attributes).
    *   Cognitive Module Configuration (dedicated subsections with specific inputs for Personality, Motivation, Emotion, Learning).
    *   Other major sections (Workflow, Scaffolding, CBT) as JSON textareas.
    *   Initiate Interaction.
*   **Buttons:** "Save Prompt". Error/Success message areas.

### 5.3 View Prompt Page (`view_prompt.html`)

*   **Layout:** Header ("Prompt Details: [Filename]"). Links to Dashboard and Edit.
*   Displays raw JSON data in a `<pre>` block.
*   Displays rendered Markdown output in a `<pre>` block.

### 5.4 View Curriculum Page (`view_curriculum.html`)

*   **Layout:** Header ("Curriculum: [Name/Filename]"). Link to Dashboard.
*   Displays curriculum metadata.
*   Lists steps, each showing order, name, prompt reference (link), conditions, notes.
*   Displays raw JSON and rendered Markdown for the curriculum.

## 6. Backend API Endpoints (Conceptual - Flask Routes)

*   **Prompts:**
    *   `GET /api/prompts`: Lists all prompts with details (filename, name, version).
    *   `POST /api/prompts`: Creates a new prompt from JSON body.
    *   `GET /api/prompts/<filename>`: Gets JSON data for a specific prompt.
    *   `PUT /api/prompts/<filename>`: Updates an existing prompt from JSON body.
    *   `DELETE /api/prompts/<filename>`: Deletes a prompt file.
    *   `GET /api/prompts/<filename>/render`: Gets rendered Markdown for a prompt.
*   **Curricula (Read-Only):**
    *   `GET /api/curricula`: Lists all curricula with details.
    *   `GET /api/curricula/<filename>`: Gets JSON data for a specific curriculum.
    *   `GET /api/curricula/<filename>/render`: Gets rendered Markdown for a curriculum.
*   **HTML Serving Routes:**
    *   `GET /`: Dashboard.
    *   `GET /create`: Prompt creation form.
    *   `GET /edit/<filename>`: Prompt editing form.
    *   `GET /view/<filename>`: Prompt view page.
    *   `GET /curriculum/view/<filename>`: Curriculum view page.

Error handling (404, 400, 500) is implemented for API endpoints. User feedback via Flask `flash` messages for page redirects and JavaScript-driven messages on forms.
```
