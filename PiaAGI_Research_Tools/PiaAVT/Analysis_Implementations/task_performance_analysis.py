# task_performance_analysis.py

import json
import argparse
from collections import defaultdict
from typing import List, Dict, Any, Optional
import statistics # For mean, median if needed later

def load_and_parse_log_data_jsonl(log_file_path: str) -> list:
    """
    Reads a JSONL file, parses each line into a dictionary, and returns a list of these dictionaries.
    Handles potential FileNotFoundError and json.JSONDecodeError.
    Skips empty lines. Sorts entries by timestamp.
    """
    parsed_logs = []
    try:
        with open(log_file_path, 'r') as f:
            for line_number, line in enumerate(f, 1):
                stripped_line = line.strip()
                if not stripped_line:
                    continue
                try:
                    parsed_logs.append(json.loads(stripped_line))
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from line {line_number} in {log_file_path}: {stripped_line} - {e}")
        parsed_logs.sort(key=lambda x: x.get("timestamp", float('inf')))
    except FileNotFoundError:
        print(f"Error: Log file not found at {log_file_path}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during log file processing: {e}")
        return []
    return parsed_logs

def analyze_task_performance(parsed_logs: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Analyzes parsed log data to reconstruct task performance metrics.
    Tasks are primarily identified via GOAL_CREATED and GOAL_STATUS_CHANGED events.

    Args:
        parsed_logs: A list of log entry dictionaries, sorted by timestamp.

    Returns:
        A dictionary where keys are task_ids (goal_ids) and values are dictionaries
        containing performance information for each task.
    """
    tasks_data = defaultdict(lambda: {
        "resources_consumed_conceptual": 0.0, # Initialize conceptual resource consumption
        "event_history": [] # To store relevant events for a task
    })

    for entry in parsed_logs:
        event_type = entry.get("event_type")
        event_data = entry.get("event_data", {})
        timestamp = entry.get("timestamp")
        task_id = event_data.get("goal_id") # Assuming goal_id serves as task_id

        if not task_id or timestamp is None:
            continue

        task = tasks_data[task_id]
        task["event_history"].append(entry) # Keep a log of all events for this task_id

        if event_type == "GOAL_CREATED":
            # Task identification: Checks if the goal type ends with "_TASK" (case-insensitive)
            # or contains "TASK". This provides flexibility.
            # Note: For specific analyses, one might want to adapt this to match exact
            # task-representing goal types logged by the agent (e.g., "EXTRINSIC_TASK", "LEARNING_TASK").
            if event_data.get("type", "").upper().endswith("_TASK") or "TASK" in event_data.get("type", ""):
                task["task_id"] = task_id
                task["description"] = event_data.get("description", "N/A")
                task["task_type"] = event_data.get("type", "UNKNOWN_TASK_TYPE")
                task["creation_time"] = timestamp
                task["initial_priority"] = event_data.get("initial_priority")
                # Ensure 'start_time' is not set here, only upon 'ACTIVE' state
                if "start_time" not in task: # Only set if not already set by an earlier ACTIVE state
                    if event_data.get("initial_status") == "ACTIVE": # If goal is created and immediately active
                         task["start_time"] = timestamp


        elif event_type == "GOAL_STATUS_CHANGED":
            new_state = event_data.get("new_state")
            if new_state == "ACTIVE" and "start_time" not in task:
                task["start_time"] = timestamp
            
            if new_state in ["ACHIEVED", "FAILED", "ABANDONED", "INVALIDATED"]: # Terminal states
                task["end_time"] = timestamp
                task["final_status"] = new_state
                if new_state == "FAILED" and event_data.get("reason"):
                    task["failure_reason"] = event_data.get("reason")

                # Calculate completion_time if start and end times are available
                if task.get("start_time") and task.get("end_time"):
                    task["completion_time_seconds"] = round(task["end_time"] - task["start_time"], 2)
                elif task.get("creation_time") and task.get("end_time"): # Fallback if no explicit start_time
                    task["completion_time_seconds_from_creation"] = round(task["end_time"] - task["creation_time"], 2)


        elif event_type == "AGENT_ACTION_EXECUTED_IN_ENV": # Conceptual resource tracking
            action_details = event_data.get("action_details", {})
            # Check if this action is associated with the current task_id
            # This requires action logs to include the goal_id they are serving.
            if action_details.get("parameters", {}).get("goal_id") == task_id:
                cost = action_details.get("cost", 0.0) # Example field
                resources_consumed = action_details.get("resources_consumed", 0.0) # Example field
                task["resources_consumed_conceptual"] += cost + resources_consumed
    
    # Post-processing to determine outcome string
    for task_id, data in tasks_data.items():
        if "final_status" in data:
            if data["final_status"] == "ACHIEVED":
                data["outcome"] = "SUCCESS"
            else:
                data["outcome"] = "FAILURE" # Includes FAILED, ABANDONED, INVALIDATED etc.
        elif data.get("start_time") and "end_time" not in data : # Started but not finished
             data["outcome"] = "IN_PROGRESS_OR_UNKNOWN" # Task might still be active or logging ended
        else: # Not started or no terminal status
            data["outcome"] = "UNKNOWN_OR_NOT_STARTED"

        # Ensure essential fields exist for all tasks that had at least one event
        data.setdefault("task_id", task_id)
        data.setdefault("description", "N/A - No GOAL_CREATED event or description missing")
        data.setdefault("task_type", "UNKNOWN")


    return dict(tasks_data)


def generate_task_performance_report(tasks_data: Dict[str, Dict[str, Any]]):
    """
    Generates and prints a summary report for task performance.
    """
    if not tasks_data:
        print("No task data to analyze.")
        return

    print("\n--- Task Performance Analysis Report ---")
    
    total_tasks = len(tasks_data)
    successful_tasks = 0
    failed_tasks = 0
    total_completion_time_success = 0.0
    total_completion_time_failure = 0.0
    num_success_with_time = 0
    num_failure_with_time = 0

    tasks_by_type = defaultdict(lambda: {"total": 0, "successful": 0, "failed": 0,
                                         "sum_completion_time_success": 0.0, "count_completion_time_success": 0,
                                         "sum_completion_time_failure": 0.0, "count_completion_time_failure": 0})
    failure_reasons_summary = defaultdict(int)
    total_resources_consumed_success = 0.0
    count_resources_success = 0

    for task_id, data in tasks_data.items():
        if "outcome" not in data or data["outcome"] == "UNKNOWN_OR_NOT_STARTED": # Skip tasks that didn't properly start/end
            if data.get("creation_time"): # Only count if it was at least created
                 tasks_by_type[data.get("task_type", "UNKNOWN")]["total"] +=1
            continue # Skip further processing for this task

        task_type = data.get("task_type", "UNKNOWN")
        tasks_by_type[task_type]["total"] += 1

        if data["outcome"] == "SUCCESS":
            successful_tasks += 1
            tasks_by_type[task_type]["successful"] += 1
            if "completion_time_seconds" in data:
                total_completion_time_success += data["completion_time_seconds"]
                num_success_with_time += 1
                tasks_by_type[task_type]["sum_completion_time_success"] += data["completion_time_seconds"]
                tasks_by_type[task_type]["count_completion_time_success"] += 1
            if data.get("resources_consumed_conceptual", 0.0) > 0:
                total_resources_consumed_success += data["resources_consumed_conceptual"]
                count_resources_success +=1

        elif data["outcome"] == "FAILURE":
            failed_tasks += 1
            tasks_by_type[task_type]["failed"] += 1
            if "completion_time_seconds" in data: # Time until failure
                total_completion_time_failure += data["completion_time_seconds"]
                num_failure_with_time += 1
                tasks_by_type[task_type]["sum_completion_time_failure"] += data["completion_time_seconds"]
                tasks_by_type[task_type]["count_completion_time_failure"] += 1
            if data.get("failure_reason"):
                failure_reasons_summary[data["failure_reason"]] += 1

    print(f"Total tasks identified (with start/end states or created as TASK type): {total_tasks}") # This might be slightly different from sum if some tasks never started
    print(f"  Successfully completed: {successful_tasks}")
    print(f"  Failed: {failed_tasks}")

    overall_success_rate = (successful_tasks / (successful_tasks + failed_tasks)) * 100 if (successful_tasks + failed_tasks) > 0 else 0
    print(f"  Overall Success Rate (completed tasks): {overall_success_rate:.2f}%")

    if num_success_with_time > 0:
        avg_comp_time_success = round(total_completion_time_success / num_success_with_time, 2)
        print(f"  Average Completion Time (Successful): {avg_comp_time_success}s")
    if num_failure_with_time > 0:
        avg_comp_time_failure = round(total_completion_time_failure / num_failure_with_time, 2)
        print(f"  Average Time to Failure (Failed): {avg_comp_time_failure}s")

    print("\n--- Performance by Task Type ---")
    for task_type, data in tasks_by_type.items():
        if data["total"] == 0 and data["successful"] == 0 and data["failed"] == 0 : continue # Skip if type was only from non-started tasks
        print(f"  Task Type: {task_type}")
        print(f"    Total Attempted/Tracked: {data['total']}")
        print(f"    Successful: {data['successful']}, Failed: {data['failed']}")
        type_success_rate = (data['successful'] / (data['successful'] + data['failed'])) * 100 if (data['successful'] + data['failed']) > 0 else 0
        print(f"    Success Rate: {type_success_rate:.2f}%")
        if data['count_completion_time_success'] > 0:
            avg_type_success_time = round(data['sum_completion_time_success'] / data['count_completion_time_success'], 2)
            print(f"    Avg. Success Time: {avg_type_success_time}s")
        if data['count_completion_time_failure'] > 0:
            avg_type_failure_time = round(data['sum_completion_time_failure'] / data['count_completion_time_failure'], 2)
            print(f"    Avg. Failure Time: {avg_type_failure_time}s")


    print("\n--- Resource Consumption (Conceptual) ---")
    if count_resources_success > 0:
        avg_resources = round(total_resources_consumed_success / count_resources_success, 2)
        print(f"  Average resources consumed for successful tasks: {avg_resources} units (conceptual)")
    else:
        print("  No resource consumption data logged for successful tasks.")

    print("\n--- Failure Analysis (Conceptual) ---")
    if failure_reasons_summary:
        print("  Common reasons for task failure:")
        for reason, count in sorted(failure_reasons_summary.items(), key=lambda item: item[1], reverse=True):
            print(f"    - \"{reason}\": {count} times")
    else:
        print("  No specific failure reasons recorded or no tasks failed with reasons.")

    print("\n--- Conceptual Correlation Insights (Future Work) ---")
    print("  Further analysis could correlate task performance with agent's emotional state during the task,")
    print("  concurrent goal load, or specific cognitive strategies employed.")
    print("  This requires aligning timestamps across different event types and more detailed contextual logging.")

    print("\n--- End of Report ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyzes task performance from PiaAVT JSONL log files.",
        epilog="Example: python task_performance_analysis.py /path/to/your/logfile.jsonl"
    )
    parser.add_argument(
        "log_file",
        help="Path to the JSONL log file to analyze."
    )
    args = parser.parse_args()

    if not args.log_file:
        parser.print_usage()
        print("Error: Log file path is required.")
        exit(1)

    print(f"Starting Task Performance Analysis for log file: {args.log_file}...")
    parsed_logs = load_and_parse_log_data_jsonl(args.log_file)

    if parsed_logs:
        print(f"\nSuccessfully parsed {len(parsed_logs)} log entries from {args.log_file}.")
        task_performance_data = analyze_task_performance(parsed_logs)

        if task_performance_data:
            # Filter out tasks that were not really processed (e.g., only ID, no other data)
            processed_tasks_data = {tid: tdata for tid, tdata in task_performance_data.items() if tdata.get("task_type") != "UNKNOWN" or "outcome" in tdata}
            if processed_tasks_data:
                 print(f"Successfully analyzed {len(processed_tasks_data)} tasks with relevant lifecycle events.")
                 generate_task_performance_report(processed_tasks_data)
            else:
                print("No tasks with sufficient lifecycle events (e.g., GOAL_CREATED as TASK type, or terminal status) found for detailed analysis.")
        else:
            print("Analysis returned no data for tasks.")
    else:
        print(f"Log parsing returned no data from {args.log_file}. Ensure the file exists, is not empty, and contains valid JSONL.")
