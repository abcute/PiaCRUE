# PiaAGI Unified WebApp - API Guide

This document outlines the backend API endpoints for the PiaAGI Unified WebApp.

## Experiment Runner API

These endpoints are used to configure, run, and manage PiaAGI experiments.

### 1. Initiate Experiment

*   **Endpoint:** `/api/experiments/run`
*   **Method:** `POST`
*   **Purpose:** Starts a new PiaAGI experiment run.
*   **Request Body (JSON):**
    ```json
    {
        "experiment_name": "Optional[str, 'My PiaAGI Experiment']",
        "agent_config_ref": "str", // Reference (e.g., path or ID) to agent configuration from PiaPES
        "prompt_or_curriculum_ref": "str", // Reference to PiaPES prompt or curriculum
        "piase_scenario_ref": "str", // Reference to PiaSE scenario
        "logging_level": "Optional[str, 'detailed']" // e.g., 'basic', 'detailed', 'debug'
    }
    ```
    *   `agent_config_ref`: A string identifier (e.g., a file path relative to a known PiaPES directory, or a unique ID managed by PiaPES) that points to the agent's cognitive configuration (PiaCML module settings, personality, etc.), typically part of or derived from a PiaPES prompt.
    *   `prompt_or_curriculum_ref`: A string identifier for the PiaPES Guiding Prompt or Developmental Curriculum to be used.
    *   `piase_scenario_ref`: A string identifier for the PiaSE scenario in which the agent will run.
*   **Response Body (JSON):**
    *   **Success (202 - Accepted):**
        ```json
        {
            "message": "Experiment run initiated successfully.",
            "run_id": "str", // Unique identifier for this experiment run
            "status_endpoint": "/api/experiments/status/<run_id>"
        }
        ```
    *   **Failure (400 - Bad Request):**
        ```json
        {
            "error": "str", // Description of the error (e.g., invalid references)
            "details": "Optional[dict]"
        }
        ```
    *   **Failure (500 - Internal Server Error):**
        ```json
        {
            "error": "str" // Description of the server-side error
        }
        ```

### 2. Get Experiment Status

*   **Endpoint:** `/api/experiments/status/<run_id>`
*   **Method:** `GET`
*   **Purpose:** Retrieves the current status of an ongoing or completed experiment run.
*   **URL Parameters:**
    *   `run_id`: The unique identifier for the experiment run.
*   **Response Body (JSON):**
    *   **Success (200 - OK):**
        ```json
        {
            "run_id": "str",
            "experiment_name": "Optional[str]",
            "status": "str", // e.g., 'PENDING', 'INITIALIZING', 'RUNNING', 'COMPLETED_SUCCESS', 'COMPLETED_FAILURE', 'ERROR'
            "start_time": "Optional[datetime_iso_string]",
            "end_time": "Optional[datetime_iso_string]",
            "progress_percentage": "Optional[int]", // If applicable
            "current_step_info": "Optional[str]", // e.g., "Running curriculum step 3/10"
            "log_summary_available": "bool", // True if basic logs can be fetched
            "results_summary_available": "bool", // True if PiaAVT has processed initial results
            "error_message": "Optional[str]" // If status is 'ERROR'
        }
        ```
    *   **Failure (404 - Not Found):**
        ```json
        {
            "error": "Experiment run not found."
        }
        ```

### 3. Get Basic Log Output

*   **Endpoint:** `/api/experiments/logs/<run_id>`
*   **Method:** `GET`
*   **Purpose:** Retrieves basic textual log output for a given experiment run. This is intended for quick viewing, not full PiaAVT analysis.
*   **URL Parameters:**
    *   `run_id`: The unique identifier for the experiment run.
*   **Query Parameters (Optional):**
    *   `tail_lines`: `int` (e.g., 100, to get the last N lines)
    *   `filter_level`: `str` (e.g., "INFO", "DEBUG", "ERROR")
*   **Response Body (JSON or plain text):**
    *   **Success (200 - OK):**
        ```json
        {
            "run_id": "str",
            "log_content": [
                "log line 1...",
                "log line 2..."
            ]
        }
        // Or could be plain text:
        // "log line 1...
log line 2...
"
        ```
    *   **Failure (404 - Not Found):**
        ```json
        {
            "error": "Logs for experiment run not found or run not completed."
        }
        ```

### 4. List Available PiaPES Prompts/Curricula (Conceptual)

*   **Endpoint:** `/api/pes/items`
*   **Method:** `GET`
*   **Purpose:** Lists available prompts and curricula that can be used in experiments.
*   **Response Body (JSON):**
    ```json
    {
        "prompts": [
            {"id": "prompt_xyz", "name": "Basic Research Agent Prompt v1.2", "description": "..."}
        ],
        "curricula": [
            {"id": "curriculum_abc", "name": "ToM Development Phase 1", "description": "..."}
        ]
    }
    ```

### 5. List Available PiaSE Scenarios (Conceptual)

*   **Endpoint:** `/api/se/scenarios`
*   **Method:** `GET`
*   **Purpose:** Lists available PiaSE scenarios for experiments.
*   **Response Body (JSON):**
    ```json
    {
        "scenarios": [
            {"id": "gridworld_task_a", "name": "GridWorld - Task A", "description": "Simple navigation task."},
            {"id": "textroom_puzzle_1", "name": "TextBasedRoom - Puzzle Alpha", "description": "..."}
        ]
    }
    ```
This API provides the basic hooks needed for the frontend to drive PiaAGI experiments.
The actual implementation within the WebApp backend (`app.py`) will involve:
- Defining these Flask routes.
- Creating handler functions for each route.
- Interfacing with PiaPES to load prompt/curriculum/agent configuration data.
- Interfacing with PiaSE to start and manage simulation runs.
- Managing state for ongoing runs (e.g., in memory, or a simple DB).
- Accessing logs (potentially simplified versions or pointers to full logs managed by PiaAVT).

## CML Module State APIs

These endpoints provide access to the internal states of specific PiaCML modules for visualization and analysis, typically after an experiment run. Accessing this data might rely on PiaAVT processing detailed logs or the simulation environment providing snapshots.

### 1. Get Motivational System Module (MSM) State

*   **Endpoint:** `/api/cml/msm/state/<run_id>`
*   **Method:** `GET`
*   **Purpose:** Retrieves the state of the Motivational System Module for a specific experiment run. This data is likely derived from logs processed by PiaAVT or a snapshot taken during/after the simulation.
*   **URL Parameters:**
    *   `run_id`: The unique identifier for the experiment run.
*   **Query Parameters (Optional):**
    *   `timestamp_start`: `float` (Unix timestamp, to get state within a time range)
    *   `timestamp_end`: `float` (Unix timestamp)
    *   `latest_only`: `bool` (Defaults to `true`, to get the most recent state or summary. If `false`, might return time-series data if available and supported by backend.)
*   **Response Body (JSON):**
    *   **Success (200 - OK):**
        ```json
        {
            "run_id": "str",
            "timestamp_of_state": "datetime_iso_string", // When this state snapshot was relevant
            "goal_hierarchy": { // Conceptual structure for a hierarchical goal view
                "goal_id": "root_goal_or_agent_id",
                "description": "Overall Agent Purpose",
                "priority": 1.0,
                "status": "ACTIVE", // ACTIVE, INACTIVE, ACHIEVED, FAILED
                "type": "ROOT", // ROOT, EXTRINSIC, INTRINSIC_COMPETENCE, INTRINSIC_CURIOSITY etc.
                "sub_goals": [
                    {
                        "goal_id": "g001",
                        "description": "Achieve Task X",
                        "priority": 0.9,
                        "status": "ACTIVE",
                        "type": "EXTRINSIC",
                        "current_intensity": "Optional[float]", // If applicable
                        "sub_goals": [
                            {
                                "goal_id": "g001_sub1",
                                "description": "Explore unknown_object_A",
                                "priority": 0.7,
                                "status": "PENDING",
                                "type": "INTRINSIC_CURIOSITY",
                                "current_intensity": 0.85
                            }
                        ]
                    },
                    {
                        "goal_id": "g002",
                        "description": "Maintain System Integrity",
                        "priority": 1.0,
                        "status": "ACTIVE",
                        "type": "INTRINSIC_SELF_PRESERVATION"
                    }
                ]
            },
            "active_goals_summary": [ // A flatter list for quick overview
                {"goal_id": "g001", "description": "Achieve Task X", "priority": 0.9, "type": "EXTRINSIC"},
                {"goal_id": "g002", "description": "Maintain System Integrity", "priority": 1.0, "type": "INTRINSIC_SELF_PRESERVATION"}
            ],
            "recent_intrinsic_rewards": [ // Optional, if logged and processed
                {"timestamp": "datetime_iso_string", "goal_id_triggered": "g001_sub1", "reward_type": "CURIOSITY_FULFILLED", "value": 0.5},
                {"timestamp": "datetime_iso_string", "goal_id_triggered": "g001", "reward_type": "COMPETENCE_INCREASE", "value": 0.3}
            ],
            "error_message": "Optional[str]" // If data is partial or some error occurred
        }
        ```
    *   **Failure (404 - Not Found):**
        ```json
        {
            "error": "Motivational system state not found for this run_id, or run not completed/processed."
        }
        ```
    *   **Failure (503 - Service Unavailable):**
        ```json
        {
            "error": "PiaAVT service currently unavailable or still processing data."
        }
        ```

**Assumptions for this API:**
*   PiaCML's Motivational System Module (MSM) is designed to expose or log this level of detail (goal structures, priorities, types, statuses, intrinsic reward events).
*   PiaAVT is capable of processing these logs and either storing snapshots or providing an aggregated/latest state view for a given `run_id`.
*   The WebApp backend will primarily act as a proxy or orchestrator, fetching this processed data from PiaAVT or a shared data store updated by PiaAVT/PiaSE.

### 2. Get Working Memory Module (WM) State

*   **Endpoint:** `/api/cml/wm/state/<run_id>`
*   **Method:** `GET`
*   **Purpose:** Retrieves the state of the Working Memory Module for a specific experiment run. This data is likely derived from logs processed by PiaAVT or a snapshot.
*   **URL Parameters:**
    *   `run_id`: The unique identifier for the experiment run.
*   **Query Parameters (Optional):**
    *   `timestamp`: `float` (Unix timestamp, to get state at a specific point in time. If not provided, defaults to latest available.)
*   **Response Body (JSON):**
    *   **Success (200 - OK):**
        ```json
        {
            "run_id": "str",
            "timestamp_of_state": "datetime_iso_string",
            "central_executive_focus": "Optional[str]", // Description or ID of the current primary focus
            "items": [ // List of items currently in Working Memory
                {
                    "item_id": "str", // Unique identifier for the WM item
                    "content_summary": "str", // Brief description or summary of the item
                    "type": "str", // e.g., 'percept', 'retrieved_ltm_chunk', 'intermediate_calculation', 'goal_representation'
                    "salience": "float", // Numerical value indicating current importance/activation
                    "source_module": "Optional[str]", // e.g., 'PerceptionModule', 'LTMModule'
                    "timestamp_added": "datetime_iso_string",
                    "attributes": { // Optional, for additional item-specific details
                        "is_newly_added": "bool",
                        "related_goal_id": "Optional[str]"
                    }
                }
            ],
            "capacity_used_percentage": "Optional[float]", // If WM has a defined capacity
            "error_message": "Optional[str]"
        }
        ```
    *   **Failure (404 - Not Found):**
        ```json
        {
            "error": "Working Memory state not found for this run_id or timestamp."
        }
        ```
    *   **Failure (503 - Service Unavailable):**
        ```json
        {
            "error": "PiaAVT service currently unavailable or still processing data for WM state."
        }
        ```

**Assumptions for this API:**
*   PiaCML's Working Memory Module (and Central Executive) logs or exposes detailed information about its current contents, item salience, and focus.
*   PiaAVT processes these logs to provide snapshots of WM state.

### 3. Get Emotion Module State

*   **Endpoint:** `/api/cml/emotion/state/<run_id>`
*   **Method:** `GET`
*   **Purpose:** Retrieves the state of the Emotion Module for a specific experiment run.
*   **URL Parameters:**
    *   `run_id`: The unique identifier for the experiment run.
*   **Query Parameters (Optional):**
    *   `timestamp`: `float` (Unix timestamp, for state at a specific time. Defaults to latest.)
    *   `include_appraisals`: `bool` (Defaults to `false`. If `true`, attempts to include recent appraisal details.)
*   **Response Body (JSON):**
    *   **Success (200 - OK):**
        ```json
        {
            "run_id": "str",
            "timestamp_of_state": "datetime_iso_string",
            "current_vad": { // Valence, Arousal, Dominance
                "valence": "float", // e.g., -1.0 to 1.0
                "arousal": "float", // e.g., 0.0 to 1.0
                "dominance": "float"  // e.g., -1.0 to 1.0 (or 0.0 to 1.0 depending on model)
            },
            "primary_discrete_emotion": "Optional[str]", // e.g., 'Joy', 'Sadness', 'Fear', 'Anger'
            "intensity": "Optional[float]", // Intensity of the primary discrete emotion, e.g., 0.0 to 1.0
            "recent_appraisals": "Optional[List[dict]]", // Included if include_appraisals=true and data is available
            // Example structure for an appraisal:
            // {
            //     "appraisal_id": "str",
            //     "timestamp": "datetime_iso_string",
            //     "event_trigger_summary": "str", // e.g., "Goal G001 achieved", "Unexpected obstacle detected"
            //     "appraised_vars": { // Key variables that were appraised
            //         "goal_congruence": "float", // e.g., positive for goal achievement
            //         "novelty": "float",
            //         "control": "float",
            //         "certainty": "float"
            //     },
            //     "resulting_emotion_tendency": "str" // e.g., "Joy-tendency"
            // }
            "error_message": "Optional[str]"
        }
        ```
    *   **Failure (404 - Not Found):**
        ```json
        {
            "error": "Emotion Module state not found for this run_id or timestamp."
        }
        ```
    *   **Failure (503 - Service Unavailable):**
        ```json
        {
            "error": "PiaAVT service currently unavailable or still processing data for Emotion state."
        }
        ```

**Assumptions for this API:**
*   PiaCML's Emotion Module logs or exposes its VAD state, primary discrete emotion, intensity, and potentially the key appraisal variables that led to recent emotional state changes.
*   PiaAVT processes these logs for retrieval.

## PiaAVT Data Endpoints (Conceptual via WebApp Backend)

These endpoints are designed to be exposed by the PiaAGI Unified WebApp backend. The backend, in turn, would query the PiaAVT service/library to get the actual analysis data. This provides a unified API for the frontend.

### 1. Get Goal Lifecycle Counts

*   **Endpoint:** `/api/avt/analysis/goal_lifecycle_counts/<run_id>`
*   **Method:** `GET`
*   **Purpose:** Retrieves aggregated counts of goal lifecycle events (created, activated, achieved, failed) for a specific experiment run.
*   **URL Parameters:**
    *   `run_id`: The unique identifier for the experiment run.
*   **Query Parameters (Optional):**
    *   `group_by_type`: `bool` (Defaults to `false`. If `true`, counts are broken down by goal type, e.g., 'EXTRINSIC', 'INTRINSIC_CURIOSITY').
*   **Response Body (JSON):**
    *   **Success (200 - OK):**
        ```json
        {
            "run_id": "str",
            "analysis_type": "goal_lifecycle_counts",
            "data": [ // If not grouped by type
                {"event": "GOAL_CREATED", "count": 50},
                {"event": "GOAL_ACTIVATED", "count": 45},
                {"event": "GOAL_ACHIEVED", "count": 30},
                {"event": "GOAL_FAILED", "count": 10}
            ]
            // Example if grouped_by_type=true:
            // "data": {
            //     "EXTRINSIC": [
            //         {"event": "GOAL_CREATED", "count": 20},
            //         {"event": "GOAL_ACHIEVED", "count": 15}
            //     ],
            //     "INTRINSIC_CURIOSITY": [
            //         {"event": "GOAL_CREATED", "count": 30},
            //         {"event": "GOAL_ACHIEVED", "count": 15}
            //     ]
            // }
        }
        ```
    *   **Failure (404 - Not Found):**
        ```json
        {
            "error": "Data for goal lifecycle counts not found for this run_id."
        }
        ```
    *   **Failure (503 - Service Unavailable):**
        ```json
        {
            "error": "PiaAVT service currently unavailable or still processing data."
        }
        ```

### 2. Get VAD Emotional Trajectory Data

*   **Endpoint:** `/api/avt/analysis/vad_trajectory/<run_id>`
*   **Method:** `GET`
*   **Purpose:** Retrieves time-series data for Valence, Arousal, and Dominance (VAD) emotional states over an experiment run.
*   **URL Parameters:**
    *   `run_id`: The unique identifier for the experiment run.
*   **Query Parameters (Optional):**
    *   `granularity_seconds`: `int` (e.g., 1, 5, 10. If provided, PiaAVT might resample/aggregate data to this granularity. Defaults to original log frequency or a sensible default.)
*   **Response Body (JSON):**
    *   **Success (200 - OK):**
        ```json
        {
            "run_id": "str",
            "analysis_type": "vad_trajectory",
            "timestamps": [ "float (unix_ts)", "float (unix_ts)", ... ],
            "valence": [ "float", "float", ... ],
            "arousal": [ "float", "float", ... ],
            "dominance": [ "float", "float", ... ]
        }
        ```
    *   **Failure (404 - Not Found):**
        ```json
        {
            "error": "VAD trajectory data not found for this run_id."
        }
        ```
    *   **Failure (503 - Service Unavailable):**
        ```json
        {
            "error": "PiaAVT service currently unavailable or still processing data."
        }
        ```

**Note on PiaAVT Interaction:**
The WebApp backend would internally call PiaAVT's analysis functions or API. PiaAVT itself is responsible for parsing the raw logs (from PiaSE) and performing these calculations. The endpoints above simplify frontend access.
