<!-- PiaAGI AGI Research Framework Document -->
# PiaAGI Prompt Engineering Suite (PiaPES) - MVP

## Introduction

Welcome to the PiaAGI Prompt Engineering Suite (PiaPES). PiaPES is a collection of tools and conceptual designs aimed at supporting the structured creation, management, and application of "Guiding Prompts" and "Developmental Curricula" for the PiaAGI (Progressive Intelligence Architecture for Artificial General Intelligence) framework.

This directory focuses on the initial Python-based **Prompt Engine MVP (Most Viable Product)**, which provides the foundational classes and utilities for working with these prompt structures programmatically.

## Purpose

The primary purpose of PiaPES, and its `prompt_engine_mvp.py` component, is to:

*   Enable systematic and reproducible design of complex agent configurations.
*   Facilitate the creation of developmental sequences (curricula) to guide agent learning.
*   Provide a standardized way to define prompt structures that can be versioned, shared, and evaluated.
*   Support researchers and developers in crafting the detailed instructions and contexts necessary for guiding advanced AGI agents.

## Current Status

The `prompt_engine_mvp.py` script represents an initial implementation providing core functionalities. It is considered an MVP that demonstrates key concepts of the PiaPES design.

Key features of the current `prompt_engine_mvp.py` include:

*   **Structured Prompt & Curriculum Creation:** Python classes (`PiaAGIPrompt`, `Role`, `CognitiveModuleConfiguration`, `CurriculumStep`, `DevelopmentalCurriculum`, etc.) that mirror the conceptual PiaAGI prompt and curriculum structures.
*   **Placeholder Substitution:** A mechanism to embed placeholders (e.g., `{my_variable}`) in string attributes of prompt elements and fill them with specific data using the `fill_placeholders()` method.
*   **Rendering to Markdown:** The `render()` method on any prompt element generates a human-readable Markdown representation.
*   **Saving & Loading (JSON):**
    *   `save_template(element, filepath)`: Serializes prompt or curriculum objects to a JSON file, preserving their structure and type information. This is the recommended format for reliable storage and round-trip conversion.
    *   `load_template(filepath)`: Deserializes JSON files back into their corresponding Python objects.
*   **Exporting to Markdown (One-Way):**
    *   `export_to_markdown(element, filepath)`: Exports the rendered Markdown of a prompt or curriculum to a `.md` file, primarily for documentation or human review. This is a one-way export; these Markdown files cannot be directly loaded back into objects.
*   **Developmental Curriculum Design:** Classes (`DevelopmentalCurriculum`, `CurriculumStep`) to define sequences of prompts for agent development.
*   **Internal Versioning:** Key objects like `PiaAGIPrompt` and `DevelopmentalCurriculum` include an optional `version` attribute for tracking versions within the data.
*   **Unit Tests:** A suite of unit tests is available to verify the functionality of the prompt engine.

## How to Use

### `prompt_engine_mvp.py`

The `prompt_engine_mvp.py` script can be used as a library by importing its classes and functions into your own Python projects.

A typical workflow involves:
1.  Importing the necessary classes (e.g., `PiaAGIPrompt`, `Role`, `Requirements`).
2.  Instantiating these classes to define the structure of your prompt or curriculum.
3.  Optionally, using placeholders in string attributes.
4.  Calling `fill_placeholders(data_dict)` to populate any placeholders.
5.  Calling `render()` to get a Markdown string representation.
6.  Using `save_template()` to save the object to a JSON file or `export_to_markdown()` for a Markdown file.
7.  Using `load_template()` to load objects from JSON files.

**Example (Conceptual):**
```python
from PiaAGI_Hub.PiaPES.prompt_engine_mvp import PiaAGIPrompt, Requirements, save_template, load_template

# Create a prompt
my_prompt = PiaAGIPrompt(
    author="Test User",
    version="1.0",
    objective="A sample prompt.",
    requirements=Requirements(goal="Demonstrate basic usage.")
)

# Save it (JSON)
save_template(my_prompt, "my_prompt_template.json")

# Load it back
loaded_prompt = load_template("my_prompt_template.json")

if loaded_prompt:
    print(loaded_prompt.render())
```

For detailed examples and usage of all features, please refer to the [USAGE.md](./USAGE.md) file.

### Running Unit Tests

The unit tests verify the core functionalities of the `prompt_engine_mvp.py`. To run the tests, navigate to the parent directory of `PiaAGI_Hub` (or ensure `PiaAGI_Hub` is in your `PYTHONPATH`) and run:

```bash
python -m unittest discover PiaAGI_Hub/PiaPES/tests
```
or from within the `PiaAGI_Hub/PiaPES` directory:
```bash
python -m unittest discover tests
```

## Web Interface (MVP)

A basic Model-View-Controller (MVC) style web interface is available to provide a user-friendly way to interact with some of the core functionalities of the PiaPES `prompt_engine_mvp.py`.

### Purpose
The web interface aims to simplify the creation, viewing, editing, and management of PiaAGI prompts for users who may prefer a graphical interface.

### Running the Web Application
*(For detailed setup, see the "PiaPES WebApp Deployment Guide" section below.)*

1.  Navigate to the web application directory:
    ```bash
    cd PiaAGI_Hub/PiaPES/web_app
    ```
2.  Run the Flask application:
    ```bash
    python app.py
    ```
3.  Open your web browser and go to `http://127.0.0.1:5001/`.

### Basic Usage

#### Prompt Management
*   **Dashboard Listing:** The main page (`/`) lists available prompt templates (`*.json` files) and developmental curricula (`*.curriculum.json` files) from the `PiaAGI_Hub/PiaPES/web_app/prompt_files/` directory.
*   **Create New Prompt:**
    *   Accessible via the "Create New Prompt" button.
    *   The form provides specific input fields for common `PiaAGIPrompt` attributes like `objective`, `author`, `version`, `target_agi`, etc.
    *   **SystemRules:** Specific fields for `language` and `output_format` are provided, supplemented by an "Advanced System Rules JSON" textarea.
    *   **Requirements:** Specific fields for `goal` and `background_context`, supplemented by an "Advanced Requirements JSON" textarea.
    *   **Role (within Executors):** Specific fields for `role_name`, `role_profile`, as well as comma-separated text inputs for `skills_focus` and `knowledge_domains_active`. An "Advanced Executors JSON" textarea is available for other role attributes (like `role_specific_rules`) and the main Executors structure.
    *   **Cognitive Configurations (within Role):** Dedicated fields are provided for:
        *   Personality (OCEAN scores as number inputs).
        *   Motivational Biases (as a comma-separated key:value text input).
        *   Emotional Profile (text inputs for baseline valence, reactivity, empathy).
        *   Learning Module Config (text input for primary mode, checkbox for rate adaptation).
    *   **Workflow Steps:** A dynamic UI allows users to add, remove, and edit individual workflow steps. Each step has fields for `name`, `action_directive`, `module_focus` (comma-separated), `expected_outcome_internal`, and `expected_output_external`. An "Advanced Workflow JSON" textarea is also available for more complex configurations, which will be supplemented or overridden by UI-defined steps.
    *   **Developmental Scaffolding Context:** Specific input fields are provided for `current_developmental_goal` (textarea), `scaffolding_techniques_employed` (comma-separated text), and `feedback_level_from_overseer`. An "Advanced Dev. Scaffolding JSON" textarea allows for further customization.
    *   Other complex sections like `UsersInteractors` and `CBTAutoTraining` are managed via their respective JSON textareas.
    *   Users must provide a filename (ending in `.json`).
    *   Clicking "Save Prompt" creates the new JSON file.
*   **View/Render Prompt:**
    *   Accessible from the dashboard.
    *   Displays the prompt's filename, its raw JSON data, and its fully rendered Markdown output.
*   **Edit Existing Prompt:**
    *   Accessible from the dashboard. The form is pre-filled with existing data.
    *   Specific fields (including dynamic Workflow Steps and Developmental Scaffolding fields) and JSON textareas can be modified. Values from specific fields will override or supplement data in the corresponding "Advanced JSON" textareas upon saving.
    *   The filename is read-only during edit.
*   **Delete Prompt:**
    *   Accessible from the dashboard, with a confirmation step.
*   **Basic Prompt Template Management:**
    *   **Load from Template:** When creating a new prompt, an optional section at the top of the form allows you to select an existing prompt from a dropdown. Clicking "Load Template" will populate the form with the data from the selected prompt. You should then provide a new, unique filename for the prompt you are creating.
    *   **Save as New Template:** To save the current form's content as a new template/prompt (especially when editing an existing prompt), use the "Save as New Template" button. You must ensure the 'Filename' field has a new, unique name distinct from the original. In 'create' mode, if you load a template, modify it, and then change the 'Filename' field to a new name, the main 'Save Prompt' button achieves the same "save as new" behavior.

#### Curriculum Management
*   **Dashboard Listing:** Curricula (`*.curriculum.json` files) are listed on the dashboard with links to "View Details" and "Edit Metadata".
*   **Create New Curriculum:**
    *   Accessible via the "Create New Curriculum" button on the dashboard.
    *   A form allows defining curriculum metadata: `filename` (must end with `.curriculum.json`), `name`, `description`, `target_developmental_stage`, `version`, and `author`.
    *   Users can dynamically add/remove "Curriculum Steps". Each step includes fields for `step_name`, `step_order`, `step_prompt_reference` (a dropdown select populated with available prompt filenames), `step_conditions` (textarea), and `step_notes` (textarea).
    *   Saving creates a new `.curriculum.json` file.
*   **View Curriculum:**
    *   Displays curriculum metadata and a detailed list of its steps, including links to view referenced prompts.
    *   Also shows the raw JSON and rendered Markdown for the curriculum object.
*   **Edit Curriculum Metadata:**
    *   Accessible from the dashboard.
    *   Allows modification of curriculum metadata fields (`name`, `description`, etc.). The filename is read-only.
    *   **Important:** Step editing (adding, removing, or modifying existing steps) for an existing curriculum is **not** supported via this specific edit metadata form; steps are preserved as is. Full step management requires editing the JSON file directly or deleting and recreating the curriculum via the UI.

### Storage
Prompt and curriculum files managed by this web interface are stored as `.json` or `.curriculum.json` files in the `PiaAGI_Hub/PiaPES/web_app/prompt_files/` directory. The application will list any compatible files found there.

### Running Web Application Tests
Unit and integration tests for the Flask backend are located in `PiaAGI_Hub/PiaPES/web_app/tests/`. To run them:
1.  Ensure your current directory is the project root (e.g., `PiaAGI_Hub` or its parent).
2.  Run:
    ```bash
    python -m unittest discover PiaAGI_Hub/PiaPES/web_app/tests
    ```

### Further Design Details
For more detailed information on the conceptual design of this web interface, including API endpoints and page mockups, refer to the [PiaPES Web Interface Design Document](./web_interface_design.md).

---

## PiaPES WebApp Deployment Guide

### Introduction
This guide provides instructions to run the PiaPES WebApp locally for development and testing purposes.

### Prerequisites
*   Python 3.7+
*   Git (for cloning the repository, if you haven't already)
*   Access to a command line/terminal.

### Setup Steps

1.  **Clone the Repository (if not already done):**
    If you don't have the project, clone it from its source:
    ```bash
    git clone <repository_url>
    cd <path_to_PiaAGI_repository_root>/PiaAGI_Hub/PiaPES/web_app/
    ```
    If you already have the repository, navigate to the web application's directory:
    ```bash
    cd <path_to_PiaAGI_repository_root>/PiaAGI_Hub/PiaPES/web_app/
    ```
    *(Ensure `<path_to_PiaAGI_repository_root>` is replaced with the actual path to the root of the cloned PiaAGI project).*

2.  **Create a Python Virtual Environment:**
    It's highly recommended to use a virtual environment to manage dependencies. From within the `PiaAGI_Hub/PiaPES/web_app/` directory:
    ```bash
    python -m venv venv
    ```

3.  **Activate the Virtual Environment:**
    *   On Windows:
        ```bash
        venv\Scripts\activate
        ```
    *   On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```
    You should see `(venv)` at the beginning of your terminal prompt.

4.  **Install Dependencies:**
    Make sure you are still in the `PiaAGI_Hub/PiaPES/web_app/` directory where `requirements.txt` is located.
    ```bash
    pip install -r requirements.txt
    ```

### Running the Web Application

1.  Ensure your virtual environment is activated and you are in the `PiaAGI_Hub/PiaPES/web_app/` directory.
2.  Run the Flask application:
    ```bash
    python app.py
    ```
3.  You should see output similar to this in your terminal:
    ```
     * Serving Flask app 'app'
     * Debug mode: on
     * Running on http://127.0.0.1:5001/ (Press CTRL+C to quit)
    ```
4.  Open your web browser and navigate to `http://127.0.0.1:5001/`.

### Using the Application
*   The application's dashboard will show lists of prompts and curricula.
*   Prompt and curriculum files are stored as `.json` (for prompts) or `.curriculum.json` (for curricula) files in the `PiaAGI_Hub/PiaPES/web_app/prompt_files/` directory. The application will list any compatible files found there.
*   You can create new prompts and curricula using the web interface. These will be saved into the `prompt_files/` directory.
*   For more details on using the features, refer to the "Basic Usage" section under "Web Interface (MVP)" above.

### Stopping the Application
*   To stop the Flask development server, go to the terminal where it's running and press `Ctrl+C`.

### Troubleshooting
*   **Import Errors for `prompt_engine_mvp`:** If you encounter import errors related to `prompt_engine_mvp` when running `python app.py`, ensure:
    1.  You are running the command from the `PiaAGI_Hub/PiaPES/web_app/` directory.
    2.  The `prompt_engine_mvp.py` file is located at `PiaAGI_Hub/PiaPES/prompt_engine_mvp.py`.
    The `app.py` script includes logic to modify `sys.path` to correctly locate `prompt_engine_mvp.py` relative to its own position. This should generally handle imports correctly when `app.py` is run directly from its directory. If running from a different context or if `PiaAGI_Hub` is not in your `PYTHONPATH`, issues might arise.

## Roadmap / Future Development

The `prompt_engine_mvp.py` script is the first step towards a more comprehensive PiaAGI Prompt Engineering Suite. The broader conceptual design, including features like a dedicated Prompt Editor/IDE, Cognitive Configuration GUI, advanced version control integration, a Prompt Evaluation Module, and enhanced Collaboration Features, is detailed in the main PiaPES design document.

## Links

*   **Detailed MVP Usage:** [PiaAGI_Hub/PiaPES/USAGE.md](./USAGE.md)
*   **Full Conceptual Design for PiaPES:** [PiaAGI_Hub/PiaAGI_Prompt_Engineering_Suite.md](../PiaAGI_Prompt_Engineering_Suite.md)
*   **Unit Tests (Prompt Engine):** [PiaAGI_Hub/PiaPES/tests/](./tests/)
*   **Web Interface Design Document:** [PiaAGI_Hub/PiaPES/web_interface_design.md](./web_interface_design.md)

---

This README provides an overview of the PiaPES MVP. We encourage users to explore the `prompt_engine_mvp.py` script and the detailed `USAGE.md` for practical application.

---
Return to [PiaAGI Core Document](../../PiaAGI.md) | [Project README](../../README.md)
