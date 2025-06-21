# PiaAGI Unified WebApp

## PiaAGI Framework Overview in WebApp (Conceptual)

To help users understand the context of the Unified WebApp and how its different tool interfaces (PiaCML, PiaPES, PiaSE, PiaAVT) relate to the broader PiaAGI project, a high-level overview is beneficial.

1.  **Placement ([P3-5]):**
    *   **HomePage/Dashboard:** A dedicated section on the WebApp's main landing page or dashboard.
    *   **"About/Framework" Page:** Alternatively, a separate "About" or "Framework Overview" page accessible from the main navigation.

2.  **Content ([P3-5]):**
    *   **Static Image/Diagram:**
        *   Display a high-level architectural diagram of the PiaAGI framework. This diagram should visually represent:
            *   The core PiaAGI agent cognitive architecture (key CML modules like Self-Model, LTM, Motivation, etc.).
            *   The surrounding research tools: PiaPES, PiaSE, and PiaAVT.
            *   How these tools interact with the agent and each other (e.g., PiaPES configures the agent, the agent runs in PiaSE, PiaAVT analyzes logs from PiaSE/agent).
        *   This could be one of the diagrams from the main `PiaAGI.md` document (e.g., a simplified version of "Diagram 2: PiaAGI Cognitive Architecture" combined with tool interactions, or "Diagram 1: PiaAGI Framework Foundational Influences" if focusing on the project's conceptual basis).
    *   **Explanatory Text:**
        *   A brief textual description accompanying the diagram, explaining the overall vision of PiaAGI.
        *   Short descriptions of each major component shown (Agent Core, PiaPES, PiaSE, PiaAVT).
        *   Crucially, explain how the different sections/pages of the Unified WebApp map to these components. For example:
            *   "Use the **PiaPES Interface** in this WebApp to design prompts and curricula that configure your agent's cognition."
            *   "The **Experiment Runner** allows you to deploy agents (configured via PiaPES) into **PiaSE Scenarios**."
            *   "View agent logs and analysis from **PiaAVT** in the results sections."
            *   "Conceptually explore **PiaCML Module** states through the dedicated visualization views."

3.  **Purpose:**
    *   Provides users with a mental model of the entire PiaAGI ecosystem.
    *   Clarifies the role and purpose of the Unified WebApp as an interface to this ecosystem.
    *   Helps users navigate the WebApp more effectively by understanding how different features connect to the underlying research tools and AGI development workflow.

This overview serves as an orienting guide, especially for users new to the PiaAGI project or the specific functionalities of the Unified WebApp.

## Overview

The PiaAGI Unified WebApp serves as a centralized interface for interacting with the various tools and modules within the PiaAGI Research Suite. Its primary purpose is to provide a user-friendly platform for experimenting with and managing:

*   **PiaCML (Cognitive Module Library):** Interacting with individual cognitive modules like Perception, Emotion, Motivation, and Working Memory.
*   **PiaPES (Prompt Engineering System):** Creating, managing, and viewing prompt templates and developmental curricula.
*   **PiaSE (Simulation Engine):** Running basic simulations (e.g., GridWorld scenarios) and viewing their outputs.
*   **PiaAVT (Analysis & Visualization Toolkit):** Performing basic log analysis (e.g., event counts from PiaSE logs) and providing a link to the more comprehensive standalone PiaAVT Streamlit application.
*   **LLM Interaction:** Serving as a testbed for LLM interactions, configured through the backend.

The WebApp consists of a **Flask backend** that serves APIs and manages tool interactions, and a **React frontend** that provides the user interface.

## Core Features

The Unified WebApp provides a central interface for interacting with the PiaAGI research tool suite. Its core conceptual features include:

*   **PiaAGI Experiment Orchestration:**
    *   **Experiment Runner:** Configure and initiate simulation runs by selecting:
        *   PiaPES Guiding Prompts or Developmental Curricula (defining agent tasks and cognitive setup).
        *   Agent Templates (for simpler agent definitions).
        *   PiaSE Scenarios (defining the environment and tasks).
        *   Logging levels for the simulation.
    *   **Run Management:** Track the status of ongoing and completed experiment runs.
*   **Results Visualization & Basic Analysis:**
    *   **Basic Log Viewer:** Display textual logs from simulation runs for immediate feedback.
    *   **Real-time Action/State Feed:** A simple feed of an agent's primary actions or significant state changes during a run.
    *   **Summary Statistics:** Show key performance indicators from experiment outcomes.
    *   **Link to PiaAVT:** Direct users to detailed analysis and visualization in the PiaAVT environment.
*   **Cognitive Module State Inspection (PiaCML Insights):**
    *   **Motivational System (MSM) Display:** Visualize goal hierarchies, active goals, priorities, and intrinsic reward events.
    *   **Working Memory (WM) Display:** Show current WM items, their salience, and the Central Executive's focus.
    *   **Emotion Module Display:** Visualize Valence-Arousal-Dominance (VAD) states, primary discrete emotions, and recent appraisal events.
*   **PiaPES Interface Enhancements:**
    *   **Curriculum Flowchart Viewer:** Visually represent the structure of `DevelopmentalCurriculum` steps.
    *   **Cognitive Configuration Summary:** Display human-readable summaries of agent cognitive setups from prompts.
    *   (Assumed from existing functionality: Managing PiaPES Guiding Prompts and Developmental Curricula - Create, Read, Update, Delete).
*   **Enhanced User Experience (UI/UX):**
    *   **Tooltips and Info Icons:** Contextual help for complex settings and parameters.
    *   **Explanatory Text:** Guidance on main pages and features.
    *   **Framework Overview:** An introductory section with a diagram explaining the PiaAGI architecture and the WebApp's role.
*   **LLM Configuration:**
    *   The backend provides a template (`llm_config.ini`) for researchers to configure LLM API keys if any backend processes directly require them. Individual tools interfaced via the WebApp (like a standalone PiaPES prompt generation tool) might have their own LLM configurations.

## Prerequisites

*   **Python:** Version 3.8+
*   **Node.js and npm:** Latest LTS version recommended (e.g., Node.js 18+ or 20+, npm 9+ or 10+).
*   **Git:** For cloning the repository.

## Setup and Running - Backend (Flask)

- For API details, see [`API_GUIDE.md`](API_GUIDE.md).

1.  **Navigate to Backend Directory:**
    ```bash
    cd PiaAGI_Research_Tools/WebApp/backend/
    ```

2.  **Create and Activate Python Virtual Environment:**
    *   On macOS/Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **PYTHONPATH Configuration (Crucial for Tool Imports):**
    The backend `app.py` needs to import modules from various PiaAGI tools (`PiaCML`, `PiaPES`, `PiaSE`, `PiaAVT`). The application attempts to modify `sys.path` at runtime to achieve this, assuming a standard project structure where `PiaAGI_Research_Tools` is the root containing all tool directories.

    *   **Automatic `sys.path` Modification:** The `app.py` script includes logic like:
        ```python
        # path_to_piaagi_hub is PiaAGI_Research_Tools/
        path_to_piaagi_hub = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) 
        # Adds PiaAGI_Research_Tools/ to sys.path
        # Then adds PiaAGI_Research_Tools/PiaPES, PiaAGI_Research_Tools/PiaSE etc. to sys.path
        ```
        This should work if you run the Flask app from `PiaAGI_Research_Tools/WebApp/backend/`.

    *   **Manual `PYTHONPATH` (If Needed):** If the automatic modification is insufficient (e.g., due to how your IDE runs the script or if you restructure parts of the project), you might need to set the `PYTHONPATH` environment variable manually **before starting the Flask server**. The most straightforward way is to ensure the **absolute path to your `PiaAGI_Research_Tools` directory** is included in `PYTHONPATH`.
        *   Example (assuming your terminal's current directory is `PiaAGI_Research_Tools`):
            *   macOS/Linux: `export PYTHONPATH="${PYTHONPATH}:$(pwd)"` (appends to existing PYTHONPATH)
            *   Windows (Command Prompt): `set PYTHONPATH=%PYTHONPATH%;%CD%` (appends)
            *   Windows (PowerShell): `$env:PYTHONPATH = "$env:PYTHONPATH;" + (Get-Location).Path` (appends)
        *   This allows Python to find top-level packages like `PiaCML`, `PiaPES`, etc., directly (e.g., `from PiaCML.some_module import ...`). The `app.py` also adds specific subdirectories, but having the root in `PYTHONPATH` is a good general practice for project-wide imports.

5.  **LLM Configuration (API Keys):**
    If the WebApp or underlying tools need to interact with Large Language Models (LLMs), you must configure API keys.
    *   The backend uses an `llm_config.ini` file located in `PiaAGI_Research_Tools/WebApp/backend/` to manage LLM API keys and model preferences.
    *   A template file, originally from `PiaAGI_Research_Tools/PiaPES/web_app/llm_config.ini.template`, should have been copied to `PiaAGI_Research_Tools/WebApp/backend/llm_config.ini` during a previous setup step.
    *   If `llm_config.ini` does not exist in the backend directory, copy the template:
        ```bash
        # From PiaAGI_Research_Tools/WebApp/backend/
        # cp llm_config.ini.template llm_config.ini (if template was copied here before)
        # Or, if it's missing entirely, copy from PiaPES source (adjust path if needed)
        cp ../../PiaPES/web_app/llm_config.ini.template ./llm_config.ini
        ```
    *   The backend uses an `llm_config.ini` file located in `PiaAGI_Research_Tools/WebApp/backend/` to manage LLM API keys and model preferences.
    *   **To configure LLM access:**
        1.  Copy the template file from `PiaAGI_Research_Tools/PiaPES/web_app/llm_config.ini.template` to the `PiaAGI_Research_Tools/WebApp/backend/` directory.
        2.  Rename the copied file to `llm_config.ini`.
            ```bash
            # Example command from PiaAGI_Research_Tools/WebApp/backend/
            cp ../../PiaPES/web_app/llm_config.ini.template ./llm_config.ini
            ```
        3.  Edit the newly created `PiaAGI_Research_Tools/WebApp/backend/llm_config.ini` with your actual API keys and preferred model names. For example, for OpenAI:
            ```ini
            [OpenAI]
            API_KEY = YOUR_OPENAI_API_KEY_HERE
            # MODEL_NAME = gpt-4o
            ```
    *   **Important:** The backend server must be restarted after any changes to `llm_config.ini` for the new settings to take effect.

6.  **Run the Backend Server:**
    ```bash
    flask run --port=5001
    ```
    The backend will typically start on `http://localhost:5001`.

### Agent Initialization Logic (Conceptual)

When the `/api/experiments/run` endpoint is called, the backend needs to initialize a PiaAGI agent based on the provided `agent_config_ref`. This process conceptually involves the following steps:

1.  **Load Agent Configuration:**
    *   The `agent_config_ref` is resolved to a full agent configuration definition. This typically involves using PiaPES functionalities to load a structured prompt or a specific agent preset file (e.g., a JSON or YAML file).
    *   This configuration file contains detailed parameters for various PiaCML modules, including:
        *   `SelfModelModule` settings (e.g., initial ethical guidelines, personality trait values from OCEAN model).
        *   `MotivationalSystemModule` settings (e.g., baseline intrinsic motivations like curiosity, competence, and their weights; initial extrinsic goals).
        *   `EmotionModule` settings (e.g., baseline emotional valence, reactivity parameters).
        *   `LTMModule` settings (e.g., pre-loaded knowledge bases or semantic network files).
        *   `WorkingMemoryModule` settings (e.g., capacity, decay rates).
        *   `LearningModule(s)` settings (e.g., learning rates, preferred learning algorithms).
        *   Other relevant module configurations (Attention, ToM, Communication, Perception, Behavior Generation, World Model).

2.  **Instantiate PiaCML Modules:**
    *   For each cognitive module defined in the configuration, the backend instantiates the corresponding concrete PiaCML class (e.g., `ConcreteSelfModelModule`, `ConcreteMotivationalSystemModule`).
    *   The parameters from the loaded configuration are passed to the constructors of these modules.
    *   Example (Conceptual Python snippet within a Flask handler):
        ```python
        # Assume 'agent_config' is a dictionary loaded via PiaPES
        # and 'PiaCML' contains the module classes

        self_model_config = agent_config.get('SelfModelModule', {})
        self_model = PiaCML.ConcreteSelfModelModule(**self_model_config)

        motivation_config = agent_config.get('MotivationalSystemModule', {})
        motivation_system = PiaCML.ConcreteMotivationalSystemModule(**motivation_config)

        # ... instantiate other modules similarly ...

        world_model_config = agent_config.get('WorldModelModule', {})
        world_model = PiaCML.ConcreteWorldModelModule(**world_model_config)

        # Ensure a shared MessageBus is created and passed to modules that need it
        message_bus = PiaCML.MessageBus()

        # Modules requiring the message bus would be instantiated like:
        # perception_module = PiaCML.ConcretePerceptionModule(message_bus=message_bus, **perception_config)
        # planning_module = PiaCML.ConcretePlanningAndDecisionMakingModule(message_bus=message_bus, **planning_config)
        ```

3.  **Assemble PiaAGI Agent:**
    *   The instantiated modules are assembled into a cohesive `PiaAGIAgent` instance. This `PiaAGIAgent` class (potentially defined in PiaSE or a shared core library) would manage the interactions between modules, possibly using a shared `MessageBus` as outlined in PiaCML's design.
    *   Conceptual Python snippet:
        ```python
        # Continuing from above...
        agent_modules = {
            "self_model": self_model,
            "motivation_system": motivation_system,
            "emotion_module": emotion_module, # assuming instantiated
            "ltm": ltm_module, # assuming instantiated
            "wm": wm_module, # assuming instantiated
            "learning_modules": learning_modules_list, # assuming instantiated
            "attention_module": attention_module, # assuming instantiated
            "tom_module": tom_module, # assuming instantiated
            "communication_module": comm_module, # assuming instantiated
            "perception_module": perception_module, # assuming instantiated with message_bus
            "behavior_generation_module": behavior_gen_module, # assuming instantiated
            "planning_module": planning_module, # assuming instantiated with message_bus
            "world_model": world_model, # assuming instantiated
            "message_bus": message_bus # Pass the shared bus
        }

        # The PiaAGIAgent class would take these modules
        pia_agent = PiaSE.PiaAGIAgent(agent_id="agent_for_run_id_X", modules=agent_modules)
        ```

4.  **Error Handling:**
    *   The logic must include robust error handling for scenarios like:
        *   Invalid `agent_config_ref`.
        *   Missing or malformed configuration parameters.
        *   Errors during module instantiation.
    *   Appropriate HTTP error responses should be returned to the client.

This initialized `pia_agent` object is then ready to be used in a PiaSE simulation run.

### Simulation Execution Logic (Conceptual)

Once a PiaAGI agent is initialized, the backend orchestrates its execution within a specified PiaSE scenario. This process conceptually involves:

1.  **Load PiaSE Scenario:**
    *   The `piase_scenario_ref` (from the `/api/experiments/run` request) is used to load the specific scenario definition. This could be a YAML or JSON file as described in the PiaSE documentation.
    *   PiaSE's `ScenarioLoader` (or equivalent utility) would parse this file to configure the environment, tasks, developmental scaffolding rules, and any specific entities or conditions for the simulation.

2.  **Initialize PiaSE Simulation Engine:**
    *   An instance of PiaSE's `BasicSimulationEngine` (or a more advanced engine if developed) is created.
    *   The loaded scenario configuration and the initialized `PiaAGIAgent` (from the Agent Initialization step) are provided to the engine.
    *   The `logging_level` parameter from the request can be used to configure the verbosity of logs generated by PiaSE and the agent.
    *   Conceptual Python snippet:
        ```python
        # Assume 'pia_agent' is the initialized agent object
        # Assume 'scenario_config' is loaded from piase_scenario_ref
        # Assume 'run_id' is available for tagging logs

        # Initialize the PiaSE environment based on scenario_config
        # This might involve PiaSE.EnvironmentFactory.create_environment(scenario_config.environment_type, scenario_config.environment_params)
        environment = PiaSE.initialize_environment_from_scenario(scenario_config)

        # The BasicSimulationEngine would take the agent, environment, and scenario details
        # It might also need a way to configure logging destination/run_id
        simulation_engine = PiaSE.BasicSimulationEngine(
            agent=pia_agent,
            environment=environment,
            scenario_config=scenario_config, # Including tasks, win/lose conditions
            run_id=run_id, # For tagging logs
            logging_level=logging_level
        )
        ```

3.  **Run Simulation Loop:**
    *   The backend calls a method on the `simulation_engine` (e.g., `run_simulation()`) to start the main simulation loop as detailed in the PiaSE documentation (Initialization, Main Loop with Perception, Cognition, Action, Feedback, Logging, Termination Check).
    *   This process can be long-running. For a web application, this should ideally be handled asynchronously (e.g., using Celery, RQ, or `asyncio` tasks if the Flask server supports it like Quart or Uvicorn-based setups) to prevent blocking API requests. The `/api/experiments/status/<run_id>` endpoint would then be used to poll for completion.
    *   Conceptual Python snippet:
        ```python
        # If synchronous (simpler, but blocks):
        # simulation_results = simulation_engine.run_simulation()

        # If asynchronous (preferred for web apps):
        # task = background_tasks.enqueue(simulation_engine.run_simulation)
        # store_task_id_for_run_id(run_id, task.id)
        # The status endpoint would then check on this task.id
        ```

4.  **Log Collection and Management:**
    *   **PiaSE Responsibility:** The PiaSE engine and the PiaCML modules within the agent are primarily responsible for generating detailed logs during the simulation. These logs should adhere to the `Logging_Specification.md` defined for PiaAVT.
    *   **Log Destination:** Logs should be written to a persistent location, tagged with the unique `run_id`. This could be:
        *   A designated directory on the server's file system (e.g., `/var/log/piaagi_runs/<run_id>/`).
        *   A centralized logging service or database if the project scales.
    *   **WebApp Backend Role:** The WebApp backend itself might not directly handle voluminous raw log streams. Instead, it:
        *   Configures PiaSE with the `run_id` so logs are correctly tagged and stored.
        *   Provides the `/api/experiments/logs/<run_id>` endpoint to fetch a *summary* or *tail* of these logs for quick inspection.
        *   Relies on PiaAVT to process the full, detailed logs from their persistent storage location for comprehensive analysis. The WebApp would then query PiaAVT's API for these analysis results.

5.  **Status Updates and Completion:**
    *   During the simulation, the engine could potentially update a shared status store (e.g., Redis, database) with progress information (current step, percentage complete), which the `/api/experiments/status/<run_id>` endpoint can query.
    *   Upon completion (success, failure, or error), the simulation engine records the final status, end time, and any summary metrics. This information is then made available via the status endpoint.

This conceptual logic ensures that the WebApp backend can manage PiaAGI experiments, leveraging the specialized capabilities of PiaSE for simulation and PiaAVT for in-depth log analysis.

## Setup and Running - Frontend (React)

### Experiment Runner UI (Conceptual)

A new page or section within the React frontend will be dedicated to running experiments. This "Experiment Runner" UI would conceptually consist of the following components and state management considerations:

1.  **Main Experiment Runner Page (`ExperimentRunnerPage.js`):**
    *   This page will serve as the main container for experiment configuration and initiation.
    *   It will likely fetch and display lists of available PiaPES items (prompts/curricula) and PiaSE scenarios upon loading.

2.  **Configuration Components:**
    *   **Experiment Name Input (`ExperimentNameInput.js`):**
        *   A simple text input field for the user to optionally name their experiment run.
    *   **PiaPES Item Selector (`PesItemSelector.js`):**
        *   Displays lists of available PiaPES prompts and developmental curricula fetched from the `/api/pes/items` backend endpoint.
        *   Uses dropdowns or searchable lists for selection. Allows the user to choose the primary guiding document (prompt or curriculum) for the agent's setup and tasks.
        *   The selected item here (`prompt_or_curriculum_ref`) often implicitly defines the agent's detailed cognitive configuration (PiaCML settings) as these are typically embedded within the PiaPES prompt structure.
        *   Stores the selected `prompt_or_curriculum_ref` in the local component state or global state.
    *   **Agent Template Selector (`AgentTemplateSelector.js` - for P2-5):**
        *   **Purpose:** To allow selection of pre-defined, simpler agent templates or archetypes, especially for initial testing or when not using a complex PiaPES prompt that fully specifies the agent. This addresses "Initial Simple Agents" from P2-5.
        *   **Display:** A dropdown listing available agent templates (e.g., "SimpleQAgent", "BasicReflexAgent", "PiaSeedling_DefaultConfig"). This list might be hardcoded initially or fetched from a new backend endpoint like `/api/agents/templates`.
        *   **Interaction with PiaPES Selector:**
            *   If a detailed PiaPES prompt (which defines agent config) is selected, this Agent Template selector might be disabled or hidden.
            *   If no detailed PiaPES prompt is chosen, or if the chosen prompt is very generic, this selector could provide the primary `agent_config_ref`.
        *   Stores the selected `agent_template_ref` (which then maps to an `agent_config_ref` for the backend).
    *   **PiaSE Scenario Selector (`SeScenarioSelector.js` - for P2-4):**
        *   Displays a list of available PiaSE scenarios fetched from the `/api/se/scenarios` backend endpoint.
        *   Uses a dropdown or searchable list for robust selection of the environment and task.
        *   Ensures the user can easily identify and choose the appropriate simulation context.
        *   Stores the selected `piase_scenario_ref`.
    *   **Logging Level Selector (`LoggingLevelSelector.js`):**
        *   A dropdown to select the desired logging verbosity (e.g., "basic", "detailed", "debug") for the simulation run.

3.  **Action Components:**
    *   **Run Experiment Button (`RunExperimentButton.js`):**
        *   Collects all selected references and parameters from the selector components.
        *   Makes a `POST` request to the `/api/experiments/run` backend endpoint.
        *   On successful initiation (202 Accepted), it might:
            *   Store the returned `run_id` and `status_endpoint`.
            *   Navigate the user to a "Run Status" page or display status inline.
            *   Disable the run button or other inputs while an experiment is being initiated or if there's an ongoing run that the UI should focus on.
        *   Handles API errors and displays appropriate messages to the user.

4.  **State Management (e.g., Redux, Zustand, or React Context API):**
    *   **Available Items State:**
        *   Stores lists of available PiaPES prompts, curricula, and PiaSE scenarios fetched from the backend.
        *   Actions/reducers for fetching and updating these lists.
    *   **Current Configuration State:**
        *   Stores the user's current selections for `experiment_name`, `agent_config_ref`, `prompt_or_curriculum_ref`, `piase_scenario_ref`, and `logging_level`.
    *   **Experiment Run State:**
        *   Manages the state of active or recent experiment runs.
        *   `run_id`: The ID of the currently active or most recently initiated run.
        *   `status`: The current status of the run (e.g., 'PENDING', 'RUNNING', 'COMPLETED_SUCCESS'), fetched periodically from the `/api/experiments/status/<run_id>` endpoint.
        *   `error_message`: Any error messages related to the run.
        *   `isLoading`: Boolean to indicate if a run is being initiated or status is being fetched.
    *   **Asynchronous Actions:**
        *   Thunks (for Redux) or equivalent async logic (for Zustand/Context) to handle API calls for:
            *   Fetching PES items and SE scenarios.
            *   Posting to `/api/experiments/run`.
            *   Periodically fetching status from `/api/experiments/status/<run_id>`.

5.  **Routing:**
    *   A new route for the `ExperimentRunnerPage` (e.g., `/experiments/run`).
    *   Potentially a dynamic route for displaying the status and results of a specific run (e.g., `/experiments/status/:runId`).

This structure provides a user-friendly way to configure and launch experiments, forming the core of the interactive research capabilities of the WebApp.

### Experiment Results Display UI (Conceptual)

After an experiment run is initiated (and ideally completed), the user needs to see the results. This UI could be part of the `ExperimentRunnerPage` (updating once a run ID is active) or a separate `ExperimentStatusPage` navigated to after a run starts.

1.  **Run Status Display (`RunStatusDisplay.js`):**
    *   **Polling:** Periodically fetches data from the `/api/experiments/status/<run_id>` endpoint.
    *   **Displays Key Information:**
        *   `run_id`
        *   `experiment_name`
        *   `status` (e.g., 'PENDING', 'INITIALIZING', 'RUNNING', 'COMPLETED_SUCCESS', 'COMPLETED_FAILURE', 'ERROR')
        *   `start_time`, `end_time`
        *   `progress_percentage` (if available)
        *   `current_step_info` (if available)
        *   `error_message` (if any)
    *   Shows a loading indicator while status is being fetched or the experiment is running.

2.  **Basic Log Viewer (`LogViewer.js`):**
    *   **Trigger:** Becomes active if the status endpoint indicates `log_summary_available: true`.
    *   **Functionality:**
        *   Fetches log data from `/api/experiments/logs/<run_id>`.
        *   Allows simple filtering (e.g., by log level if the API supports it) or searching.
        *   Displays log lines in a scrollable text area or a virtualized list for performance with many lines.
        *   Option to request more lines (if the API supports pagination or tailing).
    *   **Purpose:** Provides immediate, basic insight into the agent's actions and system events during the run.

3.  **Summary Statistics Display (`SummaryStatsDisplay.js`):**
    *   **Trigger:** Becomes active if the status endpoint indicates `results_summary_available: true`. This implies PiaAVT has done some initial processing.
    *   **Functionality:**
        *   Fetches summary statistics from a conceptual endpoint like `/api/avt/summary/<run_id>` (this API endpoint would need to be defined for the AVT integration).
        *   Displays key metrics in a clear, readable format (e.g., tables, key-value pairs). Examples:
            *   Task completion rate.
            *   Average time to goal.
            *   Number of errors or warnings.
            *   Key CML module state changes (e.g., "Curiosity drive peaked at step X").

4.  **Link to Detailed PiaAVT Analysis (`AvtLink.js`):**
    *   **Functionality:**
        *   Provides a prominent link or button: "View Detailed Analysis in PiaAVT".
        *   This link would navigate the user to the more comprehensive PiaAVT web interface (which might be a separate Streamlit/Dash app or an integrated section of the Unified WebApp if PiaAVT's UI is fully embedded).
        *   The URL could be constructed using the `run_id`, e.g., `https://<piaavt_host>/analysis?run_id=<run_id>` or `/tools/avt/analysis?run_id=<run_id>` if integrated.
    *   **Purpose:** Guides the user towards the richer analytical and visualization capabilities of PiaAVT for deeper investigation beyond basic logs and summaries.

5.  **Error Display:**
    *   If the experiment status is 'ERROR', displays the `error_message` clearly.
    *   May offer suggestions like "Check logs for details" or "Retry experiment".

**State Management Considerations:**
*   The `Experiment Run State` (mentioned in the Experiment Runner UI section) would also hold the fetched logs and summary statistics.
*   Actions/reducers for fetching logs and summary data.

This results display UI provides immediate feedback on experiment outcomes and serves as a gateway to more in-depth analysis with PiaAVT.

### Motivational System Module (MSM) Visualization UI (Conceptual)

This UI component or set of components would be responsible for fetching and displaying the state of an agent's Motivational System Module (MSM) for a given experiment run. It would typically be part of a detailed experiment results view or an agent inspection dashboard.

1.  **Main MSM Display Component (`MsmDisplay.js`):**
    *   **Data Fetching:**
        *   Takes a `run_id` as a prop.
        *   On mount or when `run_id` changes, it fetches data from the `/api/cml/msm/state/<run_id>` backend endpoint.
        *   Handles loading states and potential errors during data fetching.
    *   **Layout:**
        *   Might be organized into tabs or collapsible sections for "Goal Hierarchy", "Active Goals", and "Recent Intrinsic Rewards".

2.  **Goal Hierarchy Visualization (`GoalHierarchyTree.js`):**
    *   **Input:** The `goal_hierarchy` object from the API response.
    *   **Display:**
        *   Renders the goal hierarchy as an interactive tree structure (e.g., using libraries like `react-flow`, `rc-tree`, or a custom-built tree view).
        *   Each node in the tree represents a goal and displays:
            *   `goal_id` (perhaps as a tooltip or secondary info).
            *   `description`.
            *   `type` (e.g., "EXTRINSIC", "INTRINSIC_CURIOSITY").
            *   `priority` (e.g., as a number or a visual bar).
            *   `status` (e.g., "ACTIVE", "PENDING", "ACHIEVED", styled differently for clarity).
            *   `current_intensity` (if applicable, e.g., as a progress bar or numerical value).
        *   Allows collapsing/expanding nodes to navigate the hierarchy.
        *   Clicking a goal node might reveal more details or highlight it in other related views.

3.  **Active Goals Summary (`ActiveGoalsList.js`):**
    *   **Input:** The `active_goals_summary` array from the API response.
    *   **Display:**
        *   A clear, concise list or table of currently active goals.
        *   Columns for `description`, `type`, and `priority`.
        *   May be sortable by priority.

4.  **Recent Intrinsic Rewards Display (`IntrinsicRewardsFeed.js`):**
    *   **Input:** The `recent_intrinsic_rewards` array from the API response.
    *   **Display:**
        *   A list or feed-style display of recent intrinsic reward events.
        *   Each entry shows:
            *   `timestamp`.
            *   `goal_id_triggered` (or its description).
            *   `reward_type` (e.g., "CURIOSITY_FULFILLED").
            *   `value` of the reward.
        *   Could be color-coded or use icons to represent different reward types.

5.  **State Management Considerations:**
    *   A dedicated part of the global state (e.g., Redux slice, Zustand store slice) to hold MSM data for the currently inspected `run_id`.
    *   Actions/reducers for fetching MSM state, handling loading/error states, and updating the store.
    *   Selectors to provide memoized access to different parts of the MSM state for the UI components.

**User Interaction Ideas:**
*   Selecting a goal in the hierarchy could filter or highlight related logs or events in other parts of the results display.
*   Time-series visualization of a specific goal's intensity or priority over time (if `latest_only=false` is implemented and the backend provides such data).

This UI aims to provide researchers with a clear understanding of the agent's motivations, how they are structured, and how they change or are reinforced during an experiment.

### Basic Real-time Action/State Display (Conceptual)

This UI component aims to provide a simple, near-real-time textual feed of an agent's primary actions or significant state changes during an active simulation run. It's less detailed than full logs but offers immediate feedback. This could be part of the `ExperimentStatusPage` or an updating panel on the `ExperimentRunnerPage`.

1.  **Real-time Feed Component (`RealTimeFeed.js`):**
    *   **Data Source:**
        *   This is the trickiest part, as it implies a streaming or frequent polling mechanism beyond the basic `status` endpoint if that endpoint isn't designed to return a list of recent events.
        *   Option 1: The `/api/experiments/status/<run_id>` endpoint could be enhanced to return a small list of the N most recent significant events (e.g., agent actions, major goal changes).
        *   Option 2: A new endpoint like `/api/experiments/feed/<run_id>?since=<timestamp_or_sequence_id>` could provide new events since the last poll. (This is more robust for a feed).
        *   Option 3 (Advanced): WebSocket connection to the backend for pushing events to the frontend. (Most complex, but provides true real-time).
        *   For conceptual simplicity here, we'll assume the status endpoint can provide a list of recent, high-level events.
    *   **Display:**
        *   A scrollable list that displays new events as they arrive.
        *   Each event could be a simple string: `[Timestamp] Agent Action: Moved to (3,4)`, `[Timestamp] Goal Achieved: Explore_Object_A`, `[Timestamp] Emotional State Shift: Valence increased to 0.7`.
        *   New items appear at the top or bottom, with auto-scrolling if the user hasn't manually scrolled.
        *   Limit the number of displayed items to avoid performance issues (e.g., only show the latest 50-100 events).
    *   **Styling:**
        *   Different event types (action, goal, emotion) could have different colors or icons for quick visual parsing.

2.  **Backend Considerations (for this conceptual component):**
    *   The backend (PiaSE or the WebApp's simulation orchestration layer) would need to identify "primary actions" or "significant state changes" to push to this feed. This requires defining what constitutes a "significant event" for this view – it should be less verbose than full debug logs.
    *   If using polling, the backend needs an efficient way to retrieve only new events.

3.  **State Management:**
    *   The list of feed events would be part of the `Experiment Run State`.
    *   Actions to fetch new feed items and append them to the list.

**Purpose:**
*   Provides immediate visual confirmation that the simulation is running and the agent is active.
*   Offers a quick glance at the agent's behavior without needing to wait for full log processing or detailed AVT analysis.
*   Can be helpful for spotting obvious issues or interesting behaviors early on.

This feature, while labeled "optional stretch" in the ToDo list, adds considerable value to the user experience by making the simulation process more transparent.

### Working Memory (WM) Visualization UI (Conceptual)

This UI aims to provide a view into the agent's Working Memory (WM) at a specific point in time or as it updates during a simulation run (if real-time updates are supported by the backend API).

1.  **Main WM Display Component (`WorkingMemoryDisplay.js`):**
    *   **Data Fetching:**
        *   Takes `run_id` and optionally a `timestamp` as props.
        *   Fetches data from the `/api/cml/wm/state/<run_id>` endpoint.
        *   Could potentially poll this endpoint if a live view is desired and WebSockets are not used.
        *   Handles loading and error states.
    *   **Layout:**
        *   Displays `central_executive_focus` prominently.
        *   Shows `capacity_used_percentage` if available.
        *   Lists WM items using a dedicated item component.

2.  **WM Item Component (`WorkingMemoryItem.js`):**
    *   **Input:** A single item object from the `items` array in the API response.
    *   **Display:**
        *   `content_summary`: The main text.
        *   `type`: Shown perhaps with a specific color code or icon.
        *   `salience`: Visualized (e.g., by font size, opacity, a small bar indicator, or background intensity). Items with higher salience should stand out.
        *   `source_module`: Displayed if available.
        *   `timestamp_added`: Shown, perhaps relatively (e.g., "added 5s ago").
        *   `attributes`: Display relevant attributes like "newly added" or "related to goal X".
    *   **Styling:**
        *   Items could be displayed as cards, tags, or list entries.
        *   Visual distinction for the item(s) currently in the `central_executive_focus`.

3.  **Interactive Features (Conceptual):**
    *   **Sorting/Filtering:** Allow users to sort WM items by salience, time added, or type. Filter by type or source module.
    *   **Highlighting:** Items that are newly added or have high salience could be briefly highlighted.
    *   **Tooltips:** Hovering over an item could show more detailed information if available.

4.  **State Management:**
    *   Part of the global state for the inspected `run_id` would hold the current WM state.
    *   Actions for fetching and updating WM data.

This visualization helps researchers understand what information the agent is currently attending to and manipulating, offering insights into its short-term reasoning and decision-making processes.

### Emotion Module Visualization UI (Conceptual)

This UI component displays the agent's emotional state, providing insights into its affective dynamics during an experiment run.

1.  **Main Emotion Display Component (`EmotionDisplay.js`):**
    *   **Data Fetching:**
        *   Takes `run_id` and an optional `timestamp` as props.
        *   Fetches data from the `/api/cml/emotion/state/<run_id>` endpoint.
        *   Option to request `include_appraisals=true`.
        *   Handles loading and error states.
    *   **Layout:**
        *   Displays VAD (Valence, Arousal, Dominance) values.
        *   Shows primary discrete emotion and its intensity.
        *   Optionally lists recent appraisals if requested and available.

2.  **VAD Display Component (`VadDisplay.js`):**
    *   **Input:** The `current_vad` object from the API response.
    *   **Display Options:**
        *   **Sliders:** Three sliders (or gauges) representing Valence, Arousal, and Dominance. Each slider would typically range from -1 to 1 (for Valence/Dominance) or 0 to 1 (for Arousal).
        *   **Numerical Values:** Clearly display the numerical values next to sliders or in a separate summary.
        *   **2D Plot (Optional):** A 2D plot with Valence on one axis and Arousal on the other, showing the current emotion as a point on this plane. Dominance could be represented by point size or color.

3.  **Discrete Emotion Display (`DiscreteEmotion.js`):**
    *   **Input:** `primary_discrete_emotion` and `intensity` from the API response.
    *   **Display:**
        *   Shows the name of the primary discrete emotion (e.g., "Joy", "Fear").
        *   Visualizes intensity using a progress bar, color intensity, or numerical value.
        *   Could use icons associated with different emotions.

4.  **Recent Appraisals List (`AppraisalFeed.js`):**
    *   **Input:** The `recent_appraisals` array (if requested and available).
    *   **Display:**
        *   A list of recent appraisal events.
        *   Each entry shows:
            *   `timestamp_of_appraisal`.
            *   `event_trigger_summary` (what caused the appraisal).
            *   Key `appraised_vars` (e.g., "Goal Congruence: High (0.8)", "Novelty: Medium (0.5)").
            *   `resulting_emotion_tendency`.
    *   This provides context on *why* the emotional state might have changed.

5.  **State Management:**
    *   The global state for the inspected `run_id` would store the current emotion state data.
    *   Actions for fetching and updating this data.

This UI helps researchers correlate agent behavior and decisions with its internal affective state, offering a deeper understanding of the emotion model's impact.

### AVT Analysis Plot Display UI (Conceptual)

This UI component is responsible for displaying specific analytical plots generated by PiaAVT, embedded within the WebApp for convenient access. It would typically be part of a detailed experiment results view.

1.  **Main AVT Plot Display Component (`AvtPlotDisplay.js`):**
    *   **Props:** Takes `run_id` and `analysis_type` (e.g., 'goal_lifecycle_counts', 'vad_trajectory') as props.
    *   **Data Fetching:**
        *   Based on `analysis_type`, it calls the appropriate backend API endpoint:
            *   `/api/avt/analysis/goal_lifecycle_counts/<run_id>` for goal counts.
            *   `/api/avt/analysis/vad_trajectory/<run_id>` for VAD trajectory.
        *   Handles loading and error states.
    *   **Layout:** Renders the specific plot component based on the fetched data.

2.  **Goal Lifecycle Count Plot Component (`GoalLifecycleChart.js` - for P2-6):**
    *   **Input:** The `data` array/object from the `/api/avt/analysis/goal_lifecycle_counts/<run_id>` response.
    *   **Display:**
        *   Uses a charting library (e.g., Chart.js, Recharts, Nivo) to render a bar chart.
        *   **If not grouped by type:** Bars for "GOAL_CREATED", "GOAL_ACTIVATED", "GOAL_ACHIEVED", "GOAL_FAILED", showing their respective counts.
        *   **If grouped by type:** Grouped bar chart, where each group is a goal type (e.g., "EXTRINSIC"), and within each group, bars for different lifecycle events.
        *   Includes appropriate labels, titles, and legends.
        *   Tooltips on bars to show exact counts.

3.  **VAD Trajectory Plot Component (`VadTrajectoryChart.js` - for P2-7):**
    *   **Input:** The `timestamps`, `valence`, `arousal`, and `dominance` arrays from the `/api/avt/analysis/vad_trajectory/<run_id>` response.
    *   **Display:**
        *   Uses a charting library to render a multi-line time-series chart.
        *   X-axis: Time (derived from `timestamps`).
        *   Y-axis: Value (typically -1 to 1 for Valence/Dominance, 0 to 1 for Arousal).
        *   Three distinct lines for Valence, Arousal, and Dominance, each with a different color and clearly labeled in a legend.
        *   Interactive features like zoom, pan, and tooltips showing V/A/D values at specific timestamps would be beneficial.

4.  **State Management:**
    *   The global state for the inspected `run_id` could store the data for these plots to avoid re-fetching if the user navigates away and back.
    *   Actions for fetching the plot data.

These components allow users to quickly visualize key analytical insights from PiaAVT directly within the main WebApp interface, streamlining the research workflow.

### UI/UX Enhancements: Tooltips and Explanatory Text (Conceptual)

To improve the usability and accessibility of the PiaAGI Unified WebApp, especially for new users or those engaging with complex configurations, incorporating tooltips and explanatory text is crucial.

1.  **General Principles:**
    *   **Clarity and Conciseness:** Explanations should be brief and to the point.
    *   **Contextual Availability:** Information should be available where and when the user needs it, without cluttering the interface.
    *   **Progressive Disclosure:** Offer basic information directly, with options to expand for more details if needed.

2.  **Implementation Strategy:**
    *   **Tooltip Component (`Tooltip.js`):** A reusable React component that can wrap any UI element (buttons, input fields, labels) to display a text bubble on hover or click.
    *   **Info Icons (`InfoIcon.js`):** Small clickable "i" icons next to complex settings or section titles, which reveal more detailed explanations in a popover or modal.
    *   **Explanatory Text Sections:** Brief paragraphs on main pages or within complex forms to provide an overview of the functionality.

3.  **Key Areas for Tooltips and Explanations ([P3-3], [P3-4]):**

    *   **Experiment Runner Page:**
        *   **PiaPES Item Selector:**
            *   Tooltip: "Select a PiaPES Guiding Prompt or Developmental Curriculum to configure the agent and define its tasks."
        *   **Agent Template Selector:**
            *   Tooltip: "Choose a pre-defined agent archetype. May be overridden if the selected PiaPES item specifies a detailed agent configuration."
        *   **PiaSE Scenario Selector:**
            *   Tooltip: "Select the simulation environment and specific scenario for the experiment run."
        *   **Logging Level Selector:**
            *   Tooltip: "Determine the verbosity of logs generated during the simulation. 'Detailed' is recommended for thorough analysis."
        *   **Run Experiment Button (when disabled):**
            *   Tooltip: "Please select a PiaPES item, agent template (if applicable), and a PiaSE scenario to enable."
    *   **Module Visualization Pages (MSM, WM, Emotion):**
        *   **Page Introduction:** Brief text at the top of each visualization page explaining what module's state is being shown and its role in the PiaAGI framework (e.g., "The Motivational System Module (MSM) drives the agent's goal-oriented behavior. This view shows its active goals and internal drives for the selected run.").
        *   **Specific Metrics/Visuals:**
            *   Goal Hierarchy (MSM): Info icon explaining "priority", "status", "type", "intensity".
            *   VAD Display (Emotion): Info icon explaining Valence, Arousal, and Dominance dimensions.
            *   WM Item Salience: Tooltip: "Indicates the current importance or activation level of this item in Working Memory."
    *   **AVT Analysis Plot Display:**
        *   **Page Introduction:** Text explaining that these are specific analyses from PiaAVT.
        *   **Goal Lifecycle Chart:** Info icon explaining what each bar (created, activated, achieved, failed) represents.
        *   **VAD Trajectory Chart:** Info icon explaining the time-series nature of the emotional state display.
    *   **Main Tool Pages (Conceptual CML, PES, SE, AVT sections in WebApp):**
        *   As per P3-4, each main page corresponding to a PiaAGI tool (e.g., a page for managing PiaPES prompts, a page for browsing PiaSE scenarios) should have a brief introductory paragraph explaining the purpose of that tool suite component and its role within the broader PiaAGI ecosystem. For example, on a PiaPES management page:
            > "The PiaAGI Prompt Engineering Suite (PiaPES) provides tools to design, manage, and evaluate structured Guiding Prompts and Developmental Curricula. These are used to configure agent cognition and guide their learning pathways."

4.  **Content Management:**
    *   Tooltip and explanatory text content could be managed within the React components themselves for simplicity, or for larger applications, centralized in a JSON file or a simple internationalization (i18n) framework to facilitate updates and potential translations.

By strategically placing these informational elements, the WebApp can become much more intuitive and guide users effectively through the complexities of PiaAGI experimentation.

### PiaPES Visualization UI Enhancements (Conceptual)

These UI enhancements aim to make complex PiaPES structures, such as Developmental Curricula and detailed Cognitive Configurations within prompts, more understandable at a glance.

1.  **Developmental Curriculum Flowchart Viewer (`CurriculumFlowchart.js` - for P3-1):**
    *   **Purpose:** To visually represent the structure and progression of a `DevelopmentalCurriculum`.
    *   **Input:** A `DevelopmentalCurriculum` object (loaded from PiaPES, likely JSON).
    *   **Display:**
        *   Uses a graph visualization library (e.g., React Flow, Cytoscape.js, or even simpler custom CSS-based layouts for basic flowcharts) to render the curriculum steps as nodes and their sequential relationship as edges.
        *   Each node (representing a `CurriculumStep`) could display:
            *   `name` or a summary of the `prompt_reference`.
            *   Key `learning_objectives` as short bullet points or tags.
            *   `status` (e.g., "pending", "in_progress", "completed_success", "failed") if integrated with live agent progress tracking from PiaPES/PiaAVT.
        *   Edges could be styled or annotated to indicate prerequisite conditions if they are more complex than simple sequence.
    *   **Interaction:**
        *   Clicking on a node could expand to show more details of the `CurriculumStep` (e.g., full prompt reference, success criteria, associated PiaSE scenario).
        *   Pan and zoom capabilities for large curricula.
    *   **Location:** This could be a dedicated view on a PiaPES curriculum management page or a modal displayed when a user inspects a curriculum.

2.  **Cognitive Configuration Summary Viewer (`CognitiveConfigSummary.js` - for P3-2):**
    *   **Purpose:** To provide a human-readable summary of the `<Cognitive_Module_Configuration>` section within a PiaAGI Guiding Prompt.
    *   **Input:** The `Cognitive_Module_Configuration` object (dictionary) from a loaded `PiaAGIPrompt`.
    *   **Display:**
        *   Instead of showing raw JSON or parameter names/values directly, it translates them into more descriptive text.
        *   **Example for Personality:**
            *   Raw: `{"OCEAN_Openness": 0.9, "OCEAN_Conscientiousness": 0.3}`
            *   Summary Display:
                *   "**Personality:** Highly Open (Curious, Imaginative), Low Conscientiousness (Flexible, Spontaneous)"
        *   **Example for Motivation:**
            *   Raw: `{"IntrinsicGoal_Curiosity": "High", "ExtrinsicGoal_TaskCompletion": "Very_High"}`
            *   Summary Display:
                *   "**Motivation:** Driven by High Curiosity, Very High focus on Task Completion."
        *   **Example for Emotion:**
            *   Raw: `{"Baseline_Valence": "Mildly_Positive", "ReactivityToFailure_Intensity": "Low"}`
            *   Summary Display:
                *   "**Emotional Profile:** Generally Mildly Positive outlook, Low reactivity to failures."
    *   **Structure:** Could be a list of key-value pairs or a short paragraph for each configured module (Personality, Motivation, Emotion, Learning).
    *   **Location:** This component would be used on the "View Prompt" page within PiaPES, or any UI where a detailed prompt configuration is displayed, to offer a quick understanding of the agent's intended cognitive setup.

These visualization enhancements help users to more intuitively grasp the design and implications of their PiaPES artifacts, aiding in both creation and review processes.

1.  **Navigate to Frontend Directory:**
    In a new terminal window:
    ```bash
    cd PiaAGI_Research_Tools/WebApp/frontend/
    ```

2.  **Install Dependencies:**
    If this is the first time or if new dependencies were added (like `react-router-dom`, `chart.js`, `react-chartjs-2`), run:
    ```bash
    npm install
    ```

3.  **Run the Frontend Development Server:**
    ```bash
    npm run dev
    ```
    The frontend development server will typically start on `http://localhost:5173` (or another port if 5173 is busy, check your terminal output).

4.  **API Proxy and `VITE_API_BASE_URL`:**
    *   The Vite development server (`npm run dev`) is usually configured to proxy API requests (e.g., requests to `/api/...`) to the backend server. This is often set up in `vite.config.js`. If the backend runs on `http://localhost:5001`, the proxy should target this.
    *   The frontend components currently use `import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001'` to determine the backend URL.
    *   If you run the backend on a different port or need to override the default for any reason, you can set the `VITE_API_BASE_URL` environment variable before starting the frontend. Create a `.env` file in the `PiaAGI_Research_Tools/WebApp/frontend/` directory:
        ```env
        VITE_API_BASE_URL=http://localhost:YOUR_BACKEND_PORT
        ```
        Replace `YOUR_BACKEND_PORT` with the actual port your backend is running on.

## Accessing the WebApp

*   Once both backend and frontend servers are running, open your web browser and navigate to the address provided by the frontend development server (usually `http://localhost:5173`).

---
This README provides a comprehensive guide to setting up and running the unified WebApp.
Ensure all paths and commands are adjusted according to your specific environment if necessary.
