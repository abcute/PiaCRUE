# PiaAGI_Research_Tools/PiaSE/utils/pia_logging.py
import json
import datetime
import os
from typing import Dict, Any, Optional

class PiaLogger:
    LOG_LEVELS = {
        "TRACE": 0,
        "DEBUG": 1,
        "INFO": 2,
        "STATE": 3,
        "WARN": 4,
        "ERROR": 5,
        "CRITICAL": 6
    }

    def __init__(self,
                 output_filepath: str,
                 simulation_run_id: str,
                 experiment_id: str,
                 agent_id: str,
                 min_log_level: str = "INFO"):

        self.output_filepath = output_filepath
        self.simulation_run_id = simulation_run_id
        self.experiment_id = experiment_id
        self.agent_id = agent_id

        self.min_log_level_val = self.LOG_LEVELS.get(min_log_level.upper(), self.LOG_LEVELS["INFO"])

        try:
            # Ensure directory exists
            dir_name = os.path.dirname(self.output_filepath)
            if dir_name and not os.path.exists(dir_name): # Check if dir_name is not empty
                os.makedirs(dir_name, exist_ok=True)
            self.log_file = open(self.output_filepath, 'a', encoding='utf-8')
        except IOError as e:
            print(f"Error opening log file {self.output_filepath}: {e}")
            self.log_file = None # Indicate failure to open

        print(f"PiaLogger initialized. Logging to: {self.output_filepath}, Min Level: {min_log_level}")

    def _get_timestamp(self) -> str:
        return datetime.datetime.utcnow().isoformat(timespec='microseconds') + "Z"

    def log(self, source_component_id: str, log_level: str, event_type: str, event_data: Dict[str, Any]):
        log_level_upper = log_level.upper()
        current_log_level_val = self.LOG_LEVELS.get(log_level_upper, self.LOG_LEVELS["INFO"])

        if current_log_level_val < self.min_log_level_val:
            return # Skip logging if below minimum level

        if not self.log_file or self.log_file.closed:
            # Fallback to print if file is not available, but indicate it's a log attempt
            print(f"PiaLogger Error: Log file not open. Event: {event_type}, Data: {event_data}")
            return

        log_entry = {
            "timestamp": self._get_timestamp(),
            "simulation_run_id": self.simulation_run_id,
            "experiment_id": self.experiment_id,
            "agent_id": self.agent_id,
            "source_component_id": source_component_id,
            "log_level": log_level_upper,
            "event_type": event_type,
            "event_data": event_data
        }

        try:
            json_log_entry = json.dumps(log_entry)
            self.log_file.write(json_log_entry + '\n')
            self.log_file.flush() # Ensure it's written immediately, good for tailing
        except TypeError as e:
            print(f"PiaLogger Error: Error serializing log entry to JSON: {e}. Entry: {log_entry}")
        except IOError as e:
            print(f"PiaLogger Error: Error writing to log file {self.output_filepath}: {e}")

    def trace(self, source_component_id: str, event_type: str, event_data: Dict[str, Any]):
        self.log(source_component_id, "TRACE", event_type, event_data)

    def debug(self, source_component_id: str, event_type: str, event_data: Dict[str, Any]):
        self.log(source_component_id, "DEBUG", event_type, event_data)

    def info(self, source_component_id: str, event_type: str, event_data: Dict[str, Any]):
        self.log(source_component_id, "INFO", event_type, event_data)

    def state(self, source_component_id: str, event_type: str, event_data: Dict[str, Any]):
        self.log(source_component_id, "STATE", event_type, event_data)

    def warn(self, source_component_id: str, event_type: str, event_data: Dict[str, Any]):
        self.log(source_component_id, "WARN", event_type, event_data)

    def error(self, source_component_id: str, event_type: str, event_data: Dict[str, Any]):
        self.log(source_component_id, "ERROR", event_type, event_data)

    def critical(self, source_component_id: str, event_type: str, event_data: Dict[str, Any]):
        self.log(source_component_id, "CRITICAL", event_type, event_data)

    def close(self):
        if self.log_file and not self.log_file.closed:
            try:
                self.log_file.close()
                print(f"PiaLogger closed log file: {self.output_filepath}")
            except IOError as e:
                print(f"PiaLogger Error: Error closing log file {self.output_filepath}: {e}")
        self.log_file = None # Mark as unusable

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

if __name__ == '__main__':
    # Example Usage
    log_dir = "temp_logs" # Relative to where script is run
    # For robust path, use os.path.join(os.path.dirname(__file__), "temp_logs") if script is in utils/

    # If running this __main__ block directly from utils/
    # current_script_dir = os.path.dirname(os.path.abspath(__file__))
    # log_dir = os.path.join(current_script_dir, "temp_logs")

    # If running from project root (e.g. python -m PiaAGI_Research_Tools.PiaSE.utils.pia_logging)
    # This will create temp_logs in the project root.
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger_filepath = os.path.join(log_dir, "pia_simulation_log.jsonl")

    # Test with context manager
    print(f"Example logs will be written to: {os.path.abspath(logger_filepath)}")
    with PiaLogger(output_filepath=logger_filepath,
                   simulation_run_id="sim_run_001",
                   experiment_id="exp_test_logger",
                   agent_id="agent_test_007",
                   min_log_level="DEBUG") as logger:

        logger.info("PiaSE.CoreEngine", "SIMULATION_START", {"scenario_id": "scn_A"})
        logger.debug("PiaCML.Perception", "PERCEPT_RECEIVED", {"data_size": 1024})
        logger.trace("PiaCML.Perception", "LOW_LEVEL_DETAIL", {"detail": "parsing_input_char_by_char"}) # Should not log
        logger.warn("PiaSE.Environment", "LOW_RESOURCE_WARNING", {"resource": "water", "level": 0.05})
        logger.error("PiaCML.LTM", "RETRIEVAL_FAILURE", {"query": "concept_X", "error_code": 5001})
        logger.state("PiaCML.SelfModel", "CONFIDENCE_UPDATE", {"domain": "navigation", "new_confidence": 0.75})

    # Test direct close
    logger_no_ctx = PiaLogger(output_filepath=logger_filepath,
                              simulation_run_id="sim_run_002",
                              experiment_id="exp_test_logger_no_ctx",
                              agent_id="agent_test_008",
                              min_log_level="INFO")
    logger_no_ctx.info("PiaSE.AgentManager", "AGENT_REGISTERED", {"new_agent_id": "agent_B"})
    logger_no_ctx.debug("PiaSE.AgentManager", "AGENT_PING_SENT", {"target_agent_id": "agent_B"}) # Should not log
    logger_no_ctx.close()

    print(f"\nLogs written to {logger_filepath}. Check its content.")
    # Example: Read back and print for verification
    if os.path.exists(logger_filepath):
        print("\n--- Log File Content ---")
        with open(logger_filepath, 'r', encoding='utf-8') as f:
            for line in f:
                print(line.strip())
