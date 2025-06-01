# PiaAGI WebApp Interface

This project is a web application with a Python Flask backend and a React frontend. It provides tools for interacting with PiaAGI functionalities.

## Purpose

This WebApp serves two primary purposes:

1.  **PiaCRUE Prompting Tool:** Allows users to construct and test prompts for Large Language Models (LLMs) using the R-U-E (Requirements-Users-Executors) methodology. This interacts with the `/api/process_prompt` backend endpoint.
2.  **CML Module Interface:** Provides an interface to interact directly with the Python-based PiaAGI Cognitive Module Library (CML) modules running in the backend. This allows users to call methods on concrete CML module instances, observe their behavior, and understand their functionality. This interacts with the `/cml/...` backend endpoints.

## Prerequisites

*   Python (3.8 or newer recommended)
*   Node.js and npm (for the React frontend)
*   Git (for cloning the repository)

## Running the Application

The application consists of a Python Flask backend and a React (Vite) frontend. They need to be run separately.

### Backend (Flask)

1.  **Navigate to the Backend Directory:**
    Open your terminal and change to the backend directory:
    ```bash
    cd PiaAGI_Hub/WebApp/backend
    ```
    (If you are already in `PiaAGI_Hub/WebApp/`, just `cd backend`)

2.  **Create and Activate a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        venv\Scripts\activate
        ```

3.  **Install Dependencies:**
    Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Python Path (Important for CML):**
    The backend needs to import CML modules from `PiaAGI_Hub/PiaCML/`. The `app.py` attempts to adjust `sys.path` for this. If you encounter import errors for CML modules:
    *   Ensure you are running `flask run` from within the `PiaAGI_Hub/WebApp/backend/` directory.
    *   Alternatively, you can set the `PYTHONPATH` environment variable to include the `PiaAGI_Hub` directory. For example, from the root of the `PiaAGI` project:
        ```bash
        export PYTHONPATH=$PYTHONPATH:$(pwd)/PiaAGI_Hub
        ```
        (For Windows, use `set PYTHONPATH=%PYTHONPATH%;%CD%\PiaAGI_Hub`)

5.  **Run the Flask Development Server:**
    ```bash
    flask run
    ```
    By default, the backend will run on `http://localhost:5000`. You can specify a different port if needed (e.g., `flask run --port=5001`).

### Frontend (React + Vite)

1.  **Navigate to the Frontend Directory:**
    Open another terminal and change to the frontend directory:
    ```bash
    cd PiaAGI_Hub/WebApp/frontend
    ```
    (If you are already in `PiaAGI_Hub/WebApp/`, just `cd frontend`)


2.  **Install Dependencies:**
    Install the required Node.js packages:
    ```bash
    npm install
    ```

3.  **Run the Vite Development Server:**
    ```bash
    npm run dev
    ```
    The frontend will typically run on `http://localhost:5173`.

## Accessing the WebApp

*   Once both backend and frontend are running, open your web browser and navigate to the frontend URL (usually `http://localhost:5173`).
*   The React application should load, and it is typically preconfigured (in `vite.config.js` via the `proxy` setting) to send API requests (to `/api/...` and `/cml/...`) to the Flask backend running on `http://localhost:5000`.

---

PiaAGI - Advancing towards Artificial General Intelligence.
