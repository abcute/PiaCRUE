# PiaCRUE Web Tool

This project is a web application with a Python Flask backend and a React frontend.

## Running the Application

### Backend (Flask)

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Create a virtual environment (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run the Flask development server:
    ```bash
    flask run
    ```
    The backend will typically run on `http://localhost:5000`.

### Frontend (React + Vite)

1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the Vite development server:
    ```bash
    npm run dev
    ```
    The frontend will typically run on `http://localhost:5173` and will proxy API requests to the backend.

---

PiaAGI - Personalized Intelligent Agent via Communicational Reasoning and UnErtaking, with a focus on AGI.
