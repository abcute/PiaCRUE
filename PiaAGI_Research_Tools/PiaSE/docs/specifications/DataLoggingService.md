# PiaSE Data Logging Service Specification

## 1. Overview

The PiaSE Data Logging Service is responsible for capturing, formatting, and outputting data generated during simulations. This data is crucial for debugging, analysis (with tools like PiaAVT), reproducibility, and understanding agent behavior and development. The service aims to be flexible and configurable, allowing researchers to specify what data to log and in what format.

This specification should be used in conjunction with the `PiaAGI_Research_Tools/PiaAVT/Logging_Specification.md`, which defines the target data formats for PiaAVT.

## 2. Core Principles

*   **Comprehensive Capture:** Aim to log all relevant data, including agent perceptions, actions, internal state changes (if exposed), environment states, and simulation events.
*   **Standardized Formatting:** Adhere to the logging schemas defined in `PiaAVT/Logging_Specification.md` (e.g., JSONL) to ensure compatibility with analysis tools.
*   **Configurability:** Allow scenarios or engine configurations to specify the level of detail and types of data to be logged.
*   **Performance Consideration:** Logging should be implemented efficiently to minimize its impact on simulation performance, especially for large-scale or real-time simulations.
*   **Extensibility:** Allow for custom log handlers or formatters if needed in the future.

## 3. Data Sources for Logging

The Data Logging Service will gather data from various components within PiaSE:

*   **Core Simulation Engine:**
    *   Simulation lifecycle events (start, stop, pause, step number).
    *   Scenario parameters and configuration.
    *   Global errors or warnings.
*   **Environment (`Environment` interface):**
    *   Environment state at each step (or at configurable intervals).
    *   Specific environment events (e.g., object creation/destruction, dynamic changes).
    *   Data provided by `get_environment_info()`.
*   **Agents (`AgentInterface` interface):**
    *   `PerceptionData` received by the agent.
    *   `ActionCommand` submitted by the agent.
    *   `ActionResult` received by the agent after an action.
    *   `PiaSEEvent`s received by the agent.
    *   (Optionally) Internal state variables exposed by the agent through a dedicated logging interface or method (e.g., `agent.get_loggable_state() -> Dict`). This requires careful design to avoid breaking encapsulation.
*   **Scenario Scripts:**
    *   Custom scenario-specific events or milestones.

## 4. Logging Mechanism (Conceptual)

1.  **Logger Initialization:**
    *   The Core Simulation Engine will initialize and configure the Data Logging Service at the start of a simulation.
    *   Configuration might include:
        *   Log file path and naming convention.
        *   Logging level (e.g., DEBUG, INFO, WARNING).
        *   Specific data points to include or exclude.
        *   Output format (defaulting to JSONL as per PiaAVT spec).
2.  **Log Entry Creation:**
    *   Components (engine, environment, agents) will generate log entries as dictionaries or Pydantic models adhering to the `PiaAVT/Logging_Specification.md`.
    *   Each log entry should typically include:
        *   `timestamp`: Simulation time or wall-clock time.
        *   `simulation_step`: The current step number in the simulation.
        *   `event_type`: A string identifying the type of log entry (e.g., "AGENT_ACTION", "ENV_STATE", "PERCEPTION").
        *   `source_component`: (e.g., "engine", "environment", "agent_id_001").
        *   `data`: A dictionary containing the specific data for the event.
3.  **Log Processing and Output:**
    *   The Data Logging Service will receive these log entries.
    *   It will format them (e.g., serialize Pydantic models to JSON strings).
    *   It will write the formatted entries to the configured output (e.g., a JSONL file).

## 5. Key Data to Log (referencing PiaAVT/Logging_Specification.md)

The following are examples of data points that should be logged, aligning with typical needs for agent analysis:

*   **Simulation Info:**
    *   `event_type: "SIMULATION_START"`
        *   `data: {"scenario_name": "...", "engine_config": {...}}`
    *   `event_type: "SIMULATION_END"`
        *   `data: {"reason": "...", "total_steps": ...}`
*   **Agent Action:**
    *   `event_type: "AGENT_ACTION"`
    *   `agent_id: "agent_001"`
    *   `data: ActionCommand.model_dump()` (Pydantic's export to dict)
*   **Action Result:**
    *   `event_type: "ACTION_RESULT"`
    *   `agent_id: "agent_001"`
    *   `data: ActionResult.model_dump()`
*   **Agent Perception:**
    *   `event_type: "AGENT_PERCEPTION"`
    *   `agent_id: "agent_001"`
    *   `data: PerceptionData.model_dump()`
*   **Environment State (Full or Partial):**
    *   `event_type: "ENVIRONMENT_STATE"`
    *   `data: environment.get_state()` (or a summary)
*   **Agent Internal State (Optional, if agent provides it):**
    *   `event_type: "AGENT_INTERNAL_STATE"`
    *   `agent_id: "agent_001"`
    *   `data: {"mood": "curious", "current_goal": "explore", ...}` (example)
*   **Rewards (often part of ActionResult):**
    *   `event_type: "REWARD_ASSIGNED"`
    *   `agent_id: "agent_001"`
    *   `data: {"reward_value": 1.0, "reason": "goal_achieved"}`
*   **Custom Scenario Events:**
    *   `event_type: "SCENARIO_MILESTONE"`
    *   `data: {"milestone_name": "key_found", "details": {...}}`

## 6. Implementation Sketch

The `BasicSimulationEngine` could have a `logger` attribute, which is an instance of a `PiaSELogger` class.

```python
# Conceptual sketch for PiaSELogger
import json
import time
from pathlib import Path

class PiaSELogger:
    def __init__(self, log_file_path: Path, config: Optional[Dict] = None):
        self.log_file_path = log_file_path
        self.config = config or {}
        self._ensure_log_file_exists()

    def _ensure_log_file_exists(self):
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        # Could write a header or initial metadata if not JSONL per line
        # For JSONL, just ensure path exists.

    def log(self, simulation_step: int, event_type: str, source_component: str, data: Dict, wall_time: Optional[float] = None):
        if wall_time is None:
            wall_time = time.time()

        log_entry = {
            "wall_time": wall_time,
            "simulation_step": simulation_step,
            "event_type": event_type,
            "source_component": source_component,
            "data": data
        }
        try:
            with open(self.log_file_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"Error writing to log: {e}") # Basic error handling

# --- In BasicSimulationEngine ---
# self.logger = PiaSELogger(log_file_path=Path("simulation_logs/current_run.jsonl"))
#
# # When an action happens:
# self.logger.log(
#     simulation_step=self.current_step,
#     event_type="AGENT_ACTION",
#     source_component=agent_id,
#     data=action_command.model_dump()
# )
```

This logger would be passed around or made accessible to environments and agents if they need to log directly, or they could return loggable data to the engine which then calls the logger.

## 7. Future Considerations

*   **Asynchronous Logging:** For high-performance scenarios, logging might need to be done in a separate thread or process.
*   **Structured Logging Libraries:** Integrate with established Python logging libraries (e.g., `logging` module with custom formatters/handlers, or libraries like `structlog`).
*   **Multiple Log Outputs:** Support for logging to multiple destinations (e.g., file, console, network stream).
*   **Data Sampling/Throttling:** For very verbose data, implement mechanisms to sample data or log only changes.
*   **Log Rotation and Management:** Utilities for managing large log files.
*   **Direct Integration with PiaAVT:** Potentially, a mode where data is streamed directly to PiaAVT components if running in an integrated setup.
```
