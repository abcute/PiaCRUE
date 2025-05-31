# PiaAGI Simulation Environment (PiaSE)

This directory contains the PiaAGI Simulation Environment (PiaSE), a flexible and extensible platform for researchers and developers to instantiate, test, and evaluate PiaAGI agents and their components in controlled, dynamic, and reproducible settings.

## Directory Structure

-   `core_engine/`: Contains the main simulation loop, time management, event system, and core abstract classes.
-   `environments/`: Implementations of various simulation environments (e.g., GridWorld, physics-based).
-   `agents/`: Agent interfaces and example agent implementations.
-   `scenarios/`: Scripts and configurations for defining and running specific experimental scenarios.
-   `utils/`: Common utility functions and data structures used across PiaSE.
-   `tests/`: Unit tests for PiaSE components.

Refer to the main PiaAGI documentation and [`PiaAGI_Hub/PiaAGI_Simulation_Environment.md`](../PiaAGI_Simulation_Environment.md) for more details on the conceptual design and overall goals of PiaSE.

The components implemented in this initial phase include:
- Core interfaces (`PiaSEEvent`, `SimulationEngine`, `Environment`, `AgentInterface`)
- Updates to core interfaces to support learning agents.
- A `BasicSimulationEngine`
- A `GridWorld` environment
- Modifications to `GridWorld` to support rewards and goal-oriented tasks.
- A `BasicGridAgent`
- A `QLearningAgent` capable of learning in GridWorld.
- A `GridWorldVisualizer` using Matplotlib to display `GridWorld` states.
- An example `grid_world_scenario.py` that saves visualization frames.
- Unit tests for `GridWorld`, `BasicGridAgent`, `QLearningAgent`, and `GridWorldVisualizer`.
- A simple WebApp interface to run scenarios and view results.

## PiaSE WebApp
PiaSE includes a simple web application to help visualize and interact with simulations.

### Purpose
The WebApp allows users to run a predefined PiaSE scenario (currently a Q-Learning agent in GridWorld) and view its step-by-step visual progress and textual logs directly in a web browser. This enhances the usability and understandability of the PiaSE framework.

### Location
The WebApp code is located in the `PiaAGI_Hub/PiaSE/WebApp/` directory.

### PiaSE WebApp Deployment Guide

To run the PiaSE WebApp, follow these steps:

1.  **Navigate to the PiaSE Root Directory:**
    Open your terminal and change to the `PiaAGI_Hub/PiaSE/` directory.
    ```bash
    cd path/to/your/PiaAGI_Hub/PiaSE
    ```

2.  **Install Dependencies:**
    Ensure all necessary Python packages are installed by running:
    ```bash
    pip install -r requirements.txt
    ```
    This file includes Flask, Matplotlib, NumPy, and other potential dependencies for PiaSE.

3.  **Navigate to the WebApp Directory:**
    Change to the WebApp directory:
    ```bash
    cd WebApp
    ```

4.  **Run the Flask Application:**
    You can run the development server in one of two main ways:

    *   **Method 1: Directly executing `app.py`** (if it contains `app.run(...)` in an `if __name__ == '__main__':` block):
        ```bash
        python app.py
        ```
    *   **Method 2: Using the `flask` command** (recommended for flexibility):
        First, set the `FLASK_APP` environment variable:
        ```bash
        # On Linux/macOS:
        export FLASK_APP=app.py
        # On Windows (Command Prompt):
        # set FLASK_APP=app.py
        # On Windows (PowerShell):
        # $env:FLASK_APP="app.py"
        ```
        Then, run the Flask development server:
        ```bash
        flask run --host=0.0.0.0 --port=5001
        ```
        The `--host=0.0.0.0` flag makes the server accessible from other devices on your network (use `127.0.0.1` for local access only). The port is set to `5001` in `app.py`.

5.  **Access in Browser:**
    Open your web browser and go to `http://127.0.0.1:5001/` (or `http://localhost:5001/`).

You should see the main page of the PiaSE WebApp, from where you can trigger a simulation run.

For more details about the WebApp's internal structure, see the [WebApp README](./WebApp/README.md).

## Dependencies
Dependencies for PiaSE, including the WebApp and visualizer, are listed in `requirements.txt` (located in the `PiaAGI_Hub/PiaSE/` directory).
To install them, navigate to the `PiaAGI_Hub/PiaSE/` directory and run:
```bash
pip install -r requirements.txt
```
It is highly recommended to use a Python virtual environment.
