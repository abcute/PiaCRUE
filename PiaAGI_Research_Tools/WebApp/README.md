# PiaAGI Unified WebApp

## Overview

The PiaAGI Unified WebApp serves as a centralized interface for interacting with the various tools and modules within the PiaAGI Research Suite. Its primary purpose is to provide a user-friendly platform for experimenting with and managing:

*   **PiaCML (Cognitive Module Library):** Interacting with individual cognitive modules like Perception, Emotion, Motivation, and Working Memory.
*   **PiaPES (Prompt Engineering System):** Creating, managing, and viewing prompt templates and developmental curricula.
*   **PiaSE (Simulation Engine):** Running basic simulations (e.g., GridWorld scenarios) and viewing their outputs.
*   **PiaAVT (Analysis & Visualization Toolkit):** Performing basic log analysis (e.g., event counts from PiaSE logs) and providing a link to the more comprehensive standalone PiaAVT Streamlit application.
*   **LLM Interaction:** Serving as a testbed for LLM interactions, configured through the backend.

The WebApp consists of a **Flask backend** that serves APIs and manages tool interactions, and a **React frontend** that provides the user interface.

## Features

*   **CML Dashboard:** Interactive forms to send data to and receive responses from CML modules (Perception, Emotion, Motivation, Working Memory) via backend APIs.
*   **PES Interface:**
    *   List, view, create, and edit PiaAGIPrompt templates.
    *   List, view, create, and edit DevelopmentalCurriculum metadata and basic step structures.
    *   Render prompts and curricula to Markdown for easy inspection.
*   **SE Interface:**
    *   Run a default GridWorld simulation scenario via a backend API call.
    *   View textual logs and visual step-by-step outputs (images) from the simulation.
*   **AVT Interface (Basic):**
    *   Link to the standalone PiaAVT Streamlit application for detailed log analysis.
    *   Upload PiaSE log files (`.json`, `.jsonl`) for a simple, integrated analysis (e.g., event type counts displayed as a chart).
*   **LLM Testbed:** The `/api/process_prompt` endpoint (and other LLM-dependent features) utilize backend-configured LLM API keys.
*   **Settings Guidance:** Instructions on how to configure backend LLM API keys.

## Prerequisites

*   **Python:** Version 3.8+
*   **Node.js and npm:** Latest LTS version recommended (e.g., Node.js 18+ or 20+, npm 9+ or 10+).
*   **Git:** For cloning the repository.

## Setup and Running - Backend (Flask)

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

    *   **Manual `PYTHONPATH` (If Needed):** If the automatic modification is insufficient (e.g., due to how your IDE runs the script or if you restructure parts of the project), you might need to set the `PYTHONPATH` environment variable manually. 
        From the **root of the `PiaAGI_Research_Tools` directory**, you can set it to include the project root:
        *   On macOS/Linux:
            ```bash
            export PYTHONPATH=$(pwd) 
            # Or, to be very explicit and include each tool's parent if they are not directly in root:
            # export PYTHONPATH=$(pwd)/PiaCML:$(pwd)/PiaPES:$(pwd)/PiaSE:$(pwd)/PiaAVT:$(pwd) 
            ```
        *   On Windows (Command Prompt):
            ```bash
            set PYTHONPATH=%CD%
            ```
        *   On Windows (PowerShell):
            ```bash
            $env:PYTHONPATH = (Get-Location).Path
            ```
        Setting `PYTHONPATH` to the `PiaAGI_Research_Tools` directory itself should allow Python to find `PiaCML.module`, `PiaPES.module`, etc., assuming each tool directory (`PiaCML`, `PiaPES`, etc.) is a package (contains an `__init__.py`) or its submodules are structured to be importable when their parent is in the path. The backend currently adds the main `PiaAGI_Research_Tools` directory and then specific sub-tool directories like `PiaPES` and `PiaSE` to `sys.path`, which should cover most import needs.

5.  **LLM Configuration:**
    *   The backend uses an `llm_config.ini` file located in `PiaAGI_Research_Tools/WebApp/backend/` to manage LLM API keys and model preferences.
    *   A template file, originally from `PiaAGI_Research_Tools/PiaPES/web_app/llm_config.ini.template`, should have been copied to `PiaAGI_Research_Tools/WebApp/backend/llm_config.ini` during a previous setup step.
    *   If `llm_config.ini` does not exist in the backend directory, copy the template:
        ```bash
        # From PiaAGI_Research_Tools/WebApp/backend/
        # cp llm_config.ini.template llm_config.ini (if template was copied here before)
        # Or, if it's missing entirely, copy from PiaPES source (adjust path if needed)
        cp ../../PiaPES/web_app/llm_config.ini.template ./llm_config.ini
        ```
    *   Edit `llm_config.ini` with your actual API keys. For example, for OpenAI:
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

## Setup and Running - Frontend (React)

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
