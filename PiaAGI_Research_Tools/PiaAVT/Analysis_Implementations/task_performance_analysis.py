# task_performance_analysis.py

import json
import os # Keep os for path operations if needed
import statistics
import argparse # Added for command-line arguments
from collections import defaultdict

def load_and_parse_log_data_jsonl(log_file_path: str) -> list:
    """
    Reads a JSONL file, parses each line into a dictionary, and returns a list of these dictionaries.
    Handles potential FileNotFoundError and json.JSONDecodeError.
    Skips empty lines. Sorts entries by timestamp.

    Args:
        log_file_path (str): The path to the JSONL log file.

    Returns:
        list: A list of log entry dictionaries, sorted by 'timestamp'.
              Returns an empty list if the file is not found, parsing fails, or the file is empty.
    """
    parsed_logs = []
    try:
        with open(log_file_path, 'r') as f:
            for line_number, line in enumerate(f, 1):
                stripped_line = line.strip()
                if not stripped_line:  # Skip empty lines
                    continue
                try:
                    parsed_logs.append(json.loads(stripped_line))
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from line {line_number} in {log_file_path}: {stripped_line} - {e}")
        # Sort by timestamp to ensure chronological processing
        parsed_logs.sort(key=lambda x: x.get("timestamp", float('inf'))) # float('inf') for entries missing timestamp
    except FileNotFoundError:
        print(f"Error: Log file not found at {log_file_path}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during log file processing: {e}")
        return []
    return parsed_logs

def analyze_task_performance(parsed_logs: list, target_agent_id: str = None, target_simulation_run_id: str = None) -> dict:
    """
    Analyzes task performance from parsed log data.
    Filters for TASK_STATUS_UPDATE and AGENT_ACTION_EXECUTED_IN_ENV events.
    Optionally filters by agent_id and simulation_run_id.
    """
    # Filter logs by simulation_run_id first if provided
    if target_simulation_run_id:
        logs_to_process = [log for log in parsed_logs if log.get("simulation_run_id") == target_simulation_run_id]
        # When a specific sim_id is targeted, all tasks and actions will inherently be from this sim
    else:
        logs_to_process = list(parsed_logs) # Work on a copy

    # Global list of all action events, will be filtered per task's simulation_run_id later if no global sim target
    all_action_events = sorted(
        [log for log in logs_to_process if log.get("event_type") == "AGENT_ACTION_EXECUTED_IN_ENV" and "agent_id_acting" in log.get("event_data", {})],
        key=lambda x: x.get("timestamp")
    )

    # Task events should also be from the initially filtered logs_to_process
    task_events = sorted(
        [log for log in logs_to_process if log.get("event_type") == "TASK_STATUS_UPDATE" and "task_id" in log.get("event_data", {})],
        key=lambda x: x.get("timestamp")
    )
    
    tasks_data = {} # Using dict to store task progression by task_id

    for event in task_events:
        event_data = event.get("event_data", {})
        task_id = event_data.get("task_id")
        status = event_data.get("status")
        timestamp = event.get("timestamp")
        # Crucially, get the simulation_run_id from the task event itself.
        sim_id = event.get("simulation_run_id") 

        if not task_id or not status or timestamp is None or sim_id is None: # Ensure sim_id is present for the task event
            print(f"Skipping task event due to missing critical data: task_id={task_id}, status={status}, ts={timestamp}, sim_id={sim_id}")
            continue

        if task_id not in tasks_data:
            tasks_data[task_id] = {
                "task_id": task_id,
                "simulation_run_id": sim_id, # Store simulation_id for each task
                "start_time": None,
                "end_time": None,
                "duration_seconds": None,
                "status": "UNKNOWN", # Initial status
                "action_count": 0,
                "involved_agent_ids": set(), # Use a set to store unique agent IDs
                "log_timestamps": {"start": None, "end": None} # Store actual log timestamps for action filtering
            }

        current_task = tasks_data[task_id]

        if status == "STARTED" and current_task["start_time"] is None:
            current_task["start_time"] = timestamp
            current_task["log_timestamps"]["start"] = timestamp
            current_task["status"] = "STARTED"
        elif status in ["COMPLETED_SUCCESS", "COMPLETED_FAILURE", "ABORTED", "TIMED_OUT"]:
            if current_task["start_time"] is not None and current_task["end_time"] is None : # Only update if started and not already ended
                current_task["end_time"] = timestamp
                current_task["log_timestamps"]["end"] = timestamp
                current_task["status"] = status
                current_task["duration_seconds"] = round(timestamp - current_task["start_time"], 3)
        # Potentially handle other statuses or updates to an ongoing task if necessary

    # Correlate actions with tasks
    for task_id, task_info in tasks_data.items():
        if task_info["start_time"] is None: # Skip tasks that never officially started
            continue
        
        task_start_time = task_info["log_timestamps"]["start"]
        # If task is ongoing, count actions up to the latest log entry, otherwise up to its end time
        task_end_time = task_info["log_timestamps"]["end"] if task_info["log_timestamps"]["end"] is not None else float('inf')
        task_sim_id = task_info["simulation_run_id"] # Get the sim_id associated with THIS task

        # Filter actions for the current task's simulation_run_id
        # This is crucial when target_simulation_run_id is None (analyzing across all sims)
        # If target_simulation_run_id IS specified, all_action_events is already pre-filtered.
        relevant_action_events_for_task = all_action_events
        if not target_simulation_run_id: 
            relevant_action_events_for_task = [
                act for act in all_action_events if act.get("simulation_run_id") == task_sim_id
            ]
            
        for action in relevant_action_events_for_task:
            action_data = action.get("event_data", {})
            action_ts = action.get("timestamp")
            acting_agent = action_data.get("agent_id_acting")
            # action_sim_id = action.get("simulation_run_id") # Already filtered above

            if action_ts is None or acting_agent is None:
                continue

            # Action must be within the task's timeframe
            if task_start_time <= action_ts <= task_end_time:
                # If a target_agent_id is specified, only count their actions towards task_info["action_count"]
                if target_agent_id:
                    if acting_agent == target_agent_id:
                        task_info["action_count"] += 1
                    # Regardless of who the target_agent is, if any agent acts during task time, add them to involved_agent_ids
                    task_info["involved_agent_ids"].add(acting_agent)
                else: # No target agent, count all actions and list all involved agents
                    task_info["action_count"] += 1
                    task_info["involved_agent_ids"].add(acting_agent)
        
        # If target_agent_id was specified but they performed no actions for this task,
        # but the task itself is relevant (e.g. we are filtering for this agent's tasks),
        # we might still want to include the task but with 0 actions for that agent.
        # The current logic correctly sets action_count to 0 if target_agent didn't act.
        # However, if we only want tasks where target_agent was involved, we might filter tasks_list later.


    # Prepare final list of tasks and convert sets to lists
    tasks_list = []
    for task_id, task_info in tasks_data.items():
        if task_info["start_time"] is None: # Skip tasks that effectively didn't start
            continue
        
        # Filter tasks by target_agent_id's involvement if specified
        if target_agent_id and target_agent_id not in task_info["involved_agent_ids"] and task_info["action_count"] == 0:
            # If we are targeting an agent, and they were not involved in this task at all (no actions)
            # we might choose to exclude this task. For now, we include it but action_count for them is 0.
            # A stricter interpretation could be to filter here: `if target_agent_id and target_agent_id not in task_info["involved_agent_ids"]: continue`
            pass # Keeping task for now, action_count for target_agent will be 0.

        task_info["involved_agent_ids"] = sorted(list(task_info["involved_agent_ids"]))
        del task_info["log_timestamps"] # Remove temporary field
        tasks_list.append(task_info)
    
    tasks_list = sorted(tasks_list, key=lambda x: x["start_time"])


    # Calculate summary statistics
    total_tasks_analyzed = len([t for t in tasks_list if t["status"] not in ["UNKNOWN", "STARTED"]]) # Tasks with a terminal status
    completed_success = [t for t in tasks_list if t["status"] == "COMPLETED_SUCCESS"]
    completed_failure = [t for t in tasks_list if t["status"] in ["COMPLETED_FAILURE", "ABORTED", "TIMED_OUT"]] # Consider these as failures for rate

    success_rate = len(completed_success) / total_tasks_analyzed if total_tasks_analyzed > 0 else 0.0
    failure_rate = len(completed_failure) / total_tasks_analyzed if total_tasks_analyzed > 0 else 0.0
    
    avg_duration_success_seconds = None
    if completed_success:
        valid_durations = [t["duration_seconds"] for t in completed_success if t["duration_seconds"] is not None]
        if valid_durations:
            avg_duration_success_seconds = round(statistics.mean(valid_durations),3)

    avg_action_count_success = None
    if completed_success:
        action_counts = [t["action_count"] for t in completed_success]
        if action_counts:
             avg_action_count_success = round(statistics.mean(action_counts),1)


    # Determine overall agent_id and sim_id for the report header
    report_agent_id_header = target_agent_id if target_agent_id else "ALL_AGENTS"
    report_sim_id_header = target_simulation_run_id # This will be None if not specified

    if not target_simulation_run_id: # If we analyzed all simulations
        if tasks_list: # Try to infer from tasks analyzed
            unique_sim_ids_in_tasks = set(t["simulation_run_id"] for t in tasks_list)
            if len(unique_sim_ids_in_tasks) == 1:
                report_sim_id_header = unique_sim_ids_in_tasks.pop()
            else: # Multiple simulations were involved in the tasks
                report_sim_id_header = "ALL_SIMULATIONS (Multiple)"
        elif logs_to_process: # No tasks, but logs were there, try to infer from logs
            unique_sim_ids_in_logs = set(log.get("simulation_run_id") for log in logs_to_process if log.get("simulation_run_id"))
            if len(unique_sim_ids_in_logs) == 1:
                 report_sim_id_header = unique_sim_ids_in_logs.pop()
            elif not unique_sim_ids_in_logs:
                 report_sim_id_header = "N/A (No sim_id in logs)"
            else: # Multiple simulations in logs, but no tasks found from them
                report_sim_id_header = "ALL_SIMULATIONS (Multiple in logs, no tasks)"
        else: # No logs processed at all
            report_sim_id_header = "ALL_SIMULATIONS (No logs)"
    # If target_simulation_run_id was set, report_sim_id_header is already correctly that specific sim_id


    return {
        "agent_id": report_agent_id_header, # This is for the general report scope
        "simulation_run_id": report_sim_id_header, # This is for the general report scope
        "tasks": tasks_list, # Each task in this list has its own specific simulation_run_id
        "summary_stats": {
            "total_tasks_analyzed": total_tasks_analyzed, # Tasks that reached a terminal state
            "total_tasks_recorded": len(tasks_data), # All tasks that appeared in logs
            "tasks_started_not_completed": len([t for t in tasks_list if t["status"] == "STARTED"]),
            "success_rate": round(success_rate, 3),
            "failure_rate": round(failure_rate, 3),
            "avg_duration_success_seconds": avg_duration_success_seconds,
            "avg_action_count_success": avg_action_count_success,
            "count_completed_success": len(completed_success),
            "count_completed_failure": len(completed_failure), # Includes aborted, timed_out
        }
    }

def generate_summary_report_task_performance(analysis_results: dict):
    """
    Prints a textual summary of the task performance analysis results.
    """
    print("\n--- Task Performance Analysis Report ---")
    agent_id = analysis_results.get("agent_id", "N/A")
    sim_id = analysis_results.get("simulation_run_id", "N/A")
    
    print(f"Scope: Agent ID: {agent_id}, Simulation Run ID: {sim_id}")

    stats = analysis_results["summary_stats"]
    print("\nOverall Summary:")
    print(f"  Total Tasks Recorded (with any status update): {stats['total_tasks_recorded']}")
    print(f"  Total Tasks Analyzed (reached terminal status): {stats['total_tasks_analyzed']}")
    print(f"  Tasks Started but Not Completed: {stats['tasks_started_not_completed']}")
    print(f"  Successfully Completed: {stats['count_completed_success']} (Rate: {stats['success_rate']:.2%})")
    print(f"  Failed/Aborted/Timed Out: {stats['count_completed_failure']} (Rate: {stats['failure_rate']:.2%})")
    if stats['avg_duration_success_seconds'] is not None:
        print(f"  Avg. Duration (Successful Tasks): {stats['avg_duration_success_seconds']:.2f} seconds")
    else:
        print(f"  Avg. Duration (Successful Tasks): N/A")
    if stats['avg_action_count_success'] is not None:
        print(f"  Avg. Action Count (Successful Tasks, by {agent_id if agent_id != 'ALL_AGENTS' else 'any agent'}): {stats['avg_action_count_success']:.1f}")
    else:
        print(f"  Avg. Action Count (Successful Tasks): N/A")


    print("\nIndividual Task Details (first 10 tasks):")
    if not analysis_results["tasks"]:
        print("  No tasks found matching criteria.")
    else:
        for i, task in enumerate(analysis_results["tasks"][:10]):
            duration_str = f"{task['duration_seconds']:.2f}s" if task['duration_seconds'] is not None else "N/A (Ongoing or No End)"
            print(f"  Task {i+1}: {task['task_id']}")
            print(f"    Status: {task['status']}")
            print(f"    Start Time: {task['start_time']}, End Time: {task['end_time'] if task['end_time'] else 'N/A'}")
            print(f"    Duration: {duration_str}")
            print(f"    Action Count: {task['action_count']} (Involved Agents: {', '.join(task['involved_agent_ids']) if task['involved_agent_ids'] else 'None'}, Sim ID: {task['simulation_run_id']})")
        if len(analysis_results["tasks"]) > 10:
            print(f"  ... and {len(analysis_results['tasks']) - 10} more tasks.")
    print("--- End of Report ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyzes task performance from PiaAVT JSONL log files.",
        epilog="Example: python task_performance_analysis.py /path/to/your/logfile.jsonl --agent_id agent_A --sim_id sim_01"
    )
    parser.add_argument(
        "log_file",
        help="Path to the JSONL log file to analyze."
    )
    parser.add_argument(
        "--agent_id",
        help="Optional: Target agent ID to filter results for.",
        default=None
    )
    parser.add_argument(
        "--sim_id",
        help="Optional: Target simulation run ID to filter results for.",
        default=None
    )
    args = parser.parse_args()

    if not args.log_file:
        parser.print_usage()
        print("Error: Log file path is required.")
        exit(1)

    print(f"Starting Task Performance Analysis for log file: {args.log_file}...")
    if args.agent_id:
        print(f"Filtering for Agent ID: {args.agent_id}")
    if args.sim_id:
        print(f"Filtering for Simulation Run ID: {args.sim_id}")

    parsed_logs = load_and_parse_log_data_jsonl(args.log_file)

    if parsed_logs:
        print(f"\nSuccessfully parsed {len(parsed_logs)} log entries from {args.log_file}.")
        
        analysis_results = analyze_task_performance(
            parsed_logs,
            target_agent_id=args.agent_id,
            target_simulation_run_id=args.sim_id
        )
        
        generate_summary_report_task_performance(analysis_results)

        # Example: analyze all tasks in all simulations for comparison if desired
        # print("\n--- Analyzing all tasks in all simulations (for comparison) ---")
        # all_tasks_analysis_comparison = analyze_task_performance(parsed_logs)
        # generate_summary_report_task_performance(all_tasks_analysis_comparison)
    else:
        print(f"Log parsing returned no data from {args.log_file}. Ensure the file exists, is not empty, and contains valid JSONL.")
