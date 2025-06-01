# PiaSE WebApp

This directory contains a simple Flask-based web application to run and visualize scenarios from the PiaAGI Simulation Environment (PiaSE).

## Purpose

The primary purpose of this WebApp is to provide a user-friendly interface to:
- Trigger predefined PiaSE simulations (currently, a Q-learning agent in GridWorld).
- View the visual progression of the simulation as a series of images.
- See basic textual logs and results from the simulation.

This makes PiaSE more accessible and easier to understand, especially for those who may not want to run Python scripts directly.

## Structure

-   `app.py`: The main Flask application file containing routes and logic to run simulations.
-   `templates/`: Contains HTML templates.
    -   `index.html`: The main page with a button to start the simulation.
    -   `results.html`: The page to display simulation outputs (images and logs).
-   `static/`: Intended for static files like CSS, JavaScript, and generated simulation images.
    -   `frames/`: Subdirectory where timestamped folders of simulation images are saved.

## Setup and Running

1.  **Ensure Dependencies are Met:**
    This WebApp relies on PiaSE and its dependencies. Make sure you have installed all necessary packages by running the following command from the `PiaAGI_Hub/PiaSE/` directory:
    ```bash
    pip install -r requirements.txt
    ```
    This will install Flask, Matplotlib, NumPy, and any other core PiaSE dependencies.

2.  **Running the WebApp:**
    Navigate to the `PiaAGI_Hub/PiaSE/WebApp/` directory in your terminal.
    You can run the Flask development server using one of the following methods:

    *   **Directly running `app.py` (if `if __name__ == '__main__':` block is present with `app.run()`):**
        ```bash
        python app.py
        ```
    *   **Using the `flask` command-line interface:**
        Set the `FLASK_APP` environment variable to point to the application file:
        ```bash
        # On Linux/macOS
        export FLASK_APP=app.py
        # On Windows (cmd)
        # set FLASK_APP=app.py
        # On Windows (PowerShell)
        # $env:FLASK_APP="app.py"

        # Then run flask
        flask run --host=0.0.0.0 --port=5001
        ```
        The application will typically be available at `http://0.0.0.0:5001/` or `http://127.0.0.1:5001/` in your web browser. The `--host=0.0.0.0` makes it accessible from other devices on your network.

## How it Works

-   The main page (`index.html`) provides a button to start a simulation.
-   Clicking the button sends a POST request to the `/run_scenario` route in `app.py`.
-   The Flask backend then:
    -   Sets up a PiaSE `GridWorld` environment, a `QLearningAgent`, and the `BasicSimulationEngine`.
    -   Runs the simulation for a predefined number of steps.
    -   Uses `GridWorldVisualizer` to save images of the simulation state at each step into a unique timestamped folder within `static/frames/`.
    -   Collects these image paths and any textual log data.
    -   Renders the `results.html` template, passing the image paths and log data to it.
-   The `results.html` page then displays the images and the log.

Refer to the main [PiaSE README](../../README.md) for more context on the overall PiaSE project.
