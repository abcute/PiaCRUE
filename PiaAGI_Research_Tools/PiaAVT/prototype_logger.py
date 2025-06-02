import json
import time
import os # For path joining in example

class PrototypeLogger:
    """
    A basic JSONL logger that appends log events to a specified file.
    Each log event is a JSON string on a new line, adhering to a
    simplified version of the PiaAGI Logging Specification.
    """

    def __init__(self, log_file_path: str):
        """
        Initializes the logger with the path to the log file.

        Args:
            log_file_path (str): The path to the log file where events will be stored.
                                 The directory will be created if it doesn't exist.
        """
        self.log_file_path = log_file_path
        # Ensure the directory for the log file exists
        log_dir = os.path.dirname(self.log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)


    def log_event(self,
                  event_type: str,
                  source_component_id: str,
                  event_data: dict,
                  timestamp: float = None,
                  simulation_run_id: str = "SIM_RUN_PROTOTYPE_001"):
        """
        Constructs a log entry from the provided details, serializes it to JSON,
        and appends it as a new line to the log file.

        Args:
            event_type (str): The type of event being logged (e.g., "MOTIVATION_UPDATE").
            source_component_id (str): The ID of the PiaAGI module or component logging the event
                                       (e.g., "MotivationalSystem", "CuriositySubmodule").
            event_data (dict): A dictionary containing event-specific details.
            timestamp (float, optional): The timestamp of the event.
                                         Defaults to current time if not provided.
            simulation_run_id (str, optional): The ID of the simulation run.
                                               Defaults to a placeholder if not provided.
        """
        if timestamp is None:
            timestamp = time.time()

        log_entry = {
            "timestamp": timestamp,
            "simulation_run_id": simulation_run_id,
            "source_component_id": source_component_id,
            "event_type": event_type,
            "event_data": event_data
        }

        try:
            json_log_entry = json.dumps(log_entry)
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(json_log_entry + '\n')
        except IOError as e:
            print(f"Error writing to log file {self.log_file_path}: {e}")
        except TypeError as e:
            print(f"Error serializing log entry to JSON: {e}. Log Entry: {log_entry}")


if __name__ == "__main__":
    # Example Usage
    # Define a log file path (e.g., in a 'logs' subdirectory)
    log_file_directory = "prototype_logs"
    log_file_name = "pia_avt_prototype_events.jsonl"

    # Ensure the path is OS-agnostic and create the directory if it doesn't exist
    # (Handled by logger's __init__ if the path includes a directory)
    # For local example, we can just use a local file or specify a relative path.
    # If running this script directly, 'prototype_logs' will be created in the same dir as the script.

    # Correct way to ensure log_file_directory exists if logger doesn't create parent dirs
    # For this example, the logger's __init__ handles creating the log_file_path's directory.
    # If log_file_path was just "file.jsonl", it would be in current dir.
    # If "somedir/file.jsonl", "somedir" would be created.

    # Let's put logs in a subdirectory of where the script is run, for tidiness
    script_dir = os.path.dirname(__file__) # Gets directory of the script if it's part of a larger execution
    if not script_dir: # If script is run from current directory __file__ might be just filename
        script_dir = "."

    # Create a logs directory within PiaAVT for this prototype's output
    # Full path from repo root: PiaAGI_Research_Tools/PiaAVT/prototype_logs/
    # Relative path from script: prototype_logs/
    log_dir_path = os.path.join(script_dir, "prototype_logs_output") # Changed name to avoid conflict if "prototype_logs" is a module/package

    # The logger now handles directory creation, so this explicit make is not strictly needed here
    # if not os.path.exists(log_dir_path):
    #    os.makedirs(log_dir_path)

    full_log_file_path = os.path.join(log_dir_path, log_file_name)

    logger = PrototypeLogger(log_file_path=full_log_file_path)

    print(f"Prototype logger initialized. Logging events to: {os.path.abspath(full_log_file_path)}")

    # Example Event 1: Motivation Update (Curiosity)
    logger.log_event(
        event_type="MOTIVATION_STATE_UPDATE", # Changed from MOTIVATION_UPDATE to be more specific
        source_component_id="MotivationalSystem.CuriositySubmodule",
        event_data={
            "motivation_type": "INTRINSIC_CURIOSITY",
            "target_identifier": "novel_object_XYZ",
            "current_intensity": 0.75,
            "change_delta": 0.1, # Positive delta means intensity increased
            "triggering_event_id": "perception_event_123"
        },
        simulation_run_id="SIM_RUN_EXAMPLE_001"
    )

    # Example Event 2: Goal Generated (Intrinsic Competence)
    logger.log_event(
        event_type="GOAL_CREATED",
        source_component_id="MotivationalSystem",
        event_data={
            "goal_id": "COMPETENCE_GOAL_001",
            "parent_goal_id": None,
            "description": "Improve proficiency in 'pathfinding_skill_lvl3'",
            "type": "INTRINSIC_COMPETENCE",
            "initial_priority": 0.6,
            "source_trigger_event_id": "task_failure_event_456",
            "target_skill_id": "pathfinding_skill_lvl3",
            "desired_proficiency_change": 0.2
        },
        simulation_run_id="SIM_RUN_EXAMPLE_001"
    )

    # Example Event 3: Intrinsic Reward Generated
    logger.log_event(
        event_type="INTRINSIC_REWARD_GENERATED",
        source_component_id="LearningModule.ReinforcementLearner",
        event_data={
            "reward_type": "CURIOSITY_SATISFACTION",
            "magnitude": 0.5,
            "associated_goal_id": "CURIOSITY_GOAL_EXPLORE_XYZ",
            "triggering_stimulus_id": "novel_object_XYZ_details_acquired"
        },
        timestamp=time.time() + 5, # Simulate a bit later
        simulation_run_id="SIM_RUN_EXAMPLE_001"
    )

    print(f"Logged 3 sample events to {os.path.abspath(full_log_file_path)}")

    # You can verify the log file content after running this script.
    # Example of reading it back (for verification):
    # if os.path.exists(full_log_file_path):
    #     print("\n--- Log File Content ---")
    #     with open(full_log_file_path, 'r', encoding='utf-8') as f:
    #         for line in f:
    #             print(json.loads(line)) # Deserialize and print
    #     print("--- End of Log File ---")
