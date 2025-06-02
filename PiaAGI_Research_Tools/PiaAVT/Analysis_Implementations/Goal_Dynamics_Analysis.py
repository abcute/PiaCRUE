import json
import time
from collections import defaultdict

# Hypothetical Log Data (JSONL format)
# This data would typically come from the PrototypeLogger or a similar system.
HYPOTHETICAL_LOG_DATA = """
{"timestamp": 1678886400.5, "simulation_run_id": "SIM_XYZ_001", "source_component_id": "MotivationalSystem", "event_type": "GOAL_GENERATED", "event_data": {"goal_id": "G001", "description": "Explore novel object A", "type": "INTRINSIC_CURIOSITY", "priority": 0.7, "source_motivation_trigger_id": "perception_event_123"}}
{"timestamp": 1678886401.0, "simulation_run_id": "SIM_XYZ_001", "source_component_id": "MotivationalSystem", "event_type": "GOAL_GENERATED", "event_data": {"goal_id": "G002", "description": "Achieve task X (extrinsic)", "type": "EXTRINSIC_TASK", "priority": 0.9, "source_motivation_trigger_id": "user_command_abc"}}
{"timestamp": 1678886402.3, "simulation_run_id": "SIM_XYZ_001", "source_component_id": "GoalManager", "event_type": "GOAL_STATE_CHANGED", "event_data": {"goal_id": "G001", "old_state": "PENDING", "new_state": "ACTIVE", "reason": "Sufficient cognitive resources available."}}
{"timestamp": 1678886402.5, "simulation_run_id": "SIM_XYZ_001", "source_component_id": "GoalManager", "event_type": "GOAL_STATE_CHANGED", "event_data": {"goal_id": "G002", "old_state": "PENDING", "new_state": "ACTIVE", "reason": "High priority task initiated."}}
{"timestamp": 1678886405.0, "simulation_run_id": "SIM_XYZ_001", "source_component_id": "GoalManager", "event_type": "GOAL_PRIORITY_UPDATED", "event_data": {"goal_id": "G001", "old_priority": 0.7, "new_priority": 0.75, "reason": "No immediate threats, curiosity heightened."}}
{"timestamp": 1678886410.2, "simulation_run_id": "SIM_XYZ_001", "source_component_id": "GoalManager", "event_type": "GOAL_STATE_CHANGED", "event_data": {"goal_id": "G001", "old_state": "ACTIVE", "new_state": "ACHIEVED", "reason": "Novel object explored, information gained."}}
{"timestamp": 1678886412.0, "simulation_run_id": "SIM_XYZ_001", "source_component_id": "GoalManager", "event_type": "GOAL_STATE_CHANGED", "event_data": {"goal_id": "G002", "old_state": "ACTIVE", "new_state": "SUSPENDED", "reason": "Precondition for task X not met yet."}}
{"timestamp": 1678886415.0, "simulation_run_id": "SIM_XYZ_001", "source_component_id": "MotivationalSystem", "event_type": "GOAL_GENERATED", "event_data": {"goal_id": "G003", "description": "Improve pathfinding skill", "type": "INTRINSIC_COMPETENCE", "priority": 0.6, "source_motivation_trigger_id": "task_failure_event_456"}}
{"timestamp": 1678886416.0, "simulation_run_id": "SIM_XYZ_001", "source_component_id": "GoalManager", "event_type": "GOAL_STATE_CHANGED", "event_data": {"goal_id": "G003", "old_state": "PENDING", "new_state": "ACTIVE"}}
{"timestamp": 1678886420.0, "simulation_run_id": "SIM_XYZ_001", "source_component_id": "GoalManager", "event_type": "GOAL_STATE_CHANGED", "event_data": {"goal_id": "G002", "old_state": "SUSPENDED", "new_state": "FAILED", "reason": "Timeout or persistent precondition failure."}}
"""

def load_and_parse_log_data(log_data_string: str) -> list:
    """
    Parses a string of JSONL log data into a list of dictionaries.
    Each line in the string is expected to be a valid JSON object.
    The list is sorted by timestamp.

    Args:
        log_data_string (str): A string containing multiple JSON log entries,
                               each on a new line.

    Returns:
        list: A list of log entry dictionaries, sorted by 'timestamp'.
              Returns an empty list if parsing fails or input is empty.
    """
    parsed_logs = []
    try:
        for line in log_data_string.strip().split('\n'):
            if line: # Ensure line is not empty
                parsed_logs.append(json.loads(line))
        # Sort by timestamp to ensure chronological processing
        parsed_logs.sort(key=lambda x: x.get("timestamp", 0))
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from log string: {e}")
        return [] # Or raise an exception
    except Exception as e:
        print(f"An unexpected error occurred during log parsing: {e}")
        return []
    return parsed_logs

def analyze_goal_lifecycles(parsed_logs: list) -> dict:
    """
    Analyzes parsed log data to reconstruct the lifecycle of each goal.

    Args:
        parsed_logs (list): A list of log entry dictionaries, sorted by timestamp.

    Returns:
        dict: A dictionary where keys are goal_ids and values are dictionaries
              containing the reconstructed lifecycle information for each goal.
              Example structure:
              {
                  "G001": {
                      "description": "Explore novel object A",
                      "type": "INTRINSIC_CURIOSITY",
                      "creation_time": 1678886400.5,
                      "current_priority": 0.75,
                      "priority_history": [{"timestamp": ..., "priority": ...}, ...],
                      "state_history": [{"timestamp": ..., "state": ..., "reason": ...}, ...],
                      "outcome": "ACHIEVED",
                      "end_time": 1678886410.2,
                      "duration_seconds": 9.7
                  }, ...
              }
    """
    # Using defaultdict to easily initialize new goal entries
    # In a real implementation, more robust data structures might be used.
    goals_data = defaultdict(lambda: {
        "priority_history": [],
        "state_history": [],
        "events_processed": 0 # For tracking if any event related to this goal was processed
    })

    for entry in parsed_logs:
        event_type = entry.get("event_type")
        event_data = entry.get("event_data", {})
        goal_id = event_data.get("goal_id")
        timestamp = entry.get("timestamp")

        if not goal_id or timestamp is None:
            continue # Skip entries without goal_id or timestamp

        current_goal = goals_data[goal_id]
        current_goal["events_processed"] += 1


        if event_type == "GOAL_GENERATED":
            current_goal["goal_id"] = goal_id # Store it explicitly
            current_goal["description"] = event_data.get("description", "N/A")
            current_goal["type"] = event_data.get("type", "UNKNOWN")
            current_goal["creation_time"] = timestamp
            initial_priority = event_data.get("priority", 0.0)
            current_goal["current_priority"] = initial_priority
            current_goal["priority_history"].append({"timestamp": timestamp, "priority": initial_priority})
            # Assume initial state is PENDING, then typically an ACTIVE event follows
            current_goal["state_history"].append({"timestamp": timestamp, "state": "GENERATED/PENDING"})
            current_goal["source_motivation_trigger_id"] = event_data.get("source_motivation_trigger_id")

        elif event_type == "GOAL_STATE_CHANGED":
            new_state = event_data.get("new_state")
            reason = event_data.get("reason")
            current_goal["state_history"].append({"timestamp": timestamp, "state": new_state, "reason": reason})
            current_goal["current_state"] = new_state # Keep track of latest state

            if new_state in ["ACHIEVED", "FAILED", "ABANDONED"]: # Terminal states
                current_goal["outcome"] = new_state
                current_goal["end_time"] = timestamp
                if "creation_time" in current_goal: # Ensure goal was generated
                    current_goal["duration_seconds"] = round(timestamp - current_goal["creation_time"], 2)

        elif event_type == "GOAL_PRIORITY_UPDATED":
            new_priority = event_data.get("new_priority")
            current_goal["current_priority"] = new_priority
            current_goal["priority_history"].append({
                "timestamp": timestamp,
                "priority": new_priority,
                "old_priority": event_data.get("old_priority"),
                "reason": event_data.get("reason")
            })

        # Ensure state_history and priority_history are sorted if logs weren't perfectly ordered for a given goal_id (though initial sort helps)
        # For this conceptual implementation, we assume chronological processing is sufficient after initial sort.

    return dict(goals_data) # Convert back to regular dict for output

def generate_summary_report(analyzed_goals_data: dict):
    """
    Generates and prints a conceptual summary report from the analyzed goal data.

    Args:
        analyzed_goals_data (dict): The output from analyze_goal_lifecycles.
    """
    if not analyzed_goals_data:
        print("No goal data to analyze.")
        return

    total_goals = len(analyzed_goals_data)
    achieved_count = 0
    failed_count = 0
    suspended_count = 0
    active_count = 0 # Or any other non-terminal state

    total_duration_completed = 0
    num_completed_goals_for_duration_avg = 0

    goals_by_type = defaultdict(int)

    print("\n--- Goal Dynamics Summary Report ---")
    print(f"Total unique goals identified: {total_goals}")

    for goal_id, data in analyzed_goals_data.items():
        if not data.get("events_processed"): # Skip if no events were processed for this goal_id
            print(f"Warning: Goal ID {goal_id} found but no relevant events processed. Initial data: {data}")
            continue

        goals_by_type[data.get("type", "UNKNOWN")] += 1

        outcome = data.get("outcome")
        if outcome == "ACHIEVED":
            achieved_count += 1
        elif outcome == "FAILED":
            failed_count += 1
        elif data.get("current_state") == "SUSPENDED": # Check current state if no terminal outcome
            suspended_count +=1
        elif data.get("current_state") == "ACTIVE": # Check current state
            active_count += 1
        # (Add more states as needed)

        if "duration_seconds" in data:
            total_duration_completed += data["duration_seconds"]
            num_completed_goals_for_duration_avg +=1

    print(f"\nOutcomes:")
    print(f"  - Achieved: {achieved_count}")
    print(f"  - Failed:   {failed_count}")
    print(f"  - Suspended (currently): {suspended_count}") # Based on last known state if not terminal
    print(f"  - Active (currently):    {active_count}") # Based on last known state if not terminal


    if num_completed_goals_for_duration_avg > 0:
        avg_duration = round(total_duration_completed / num_completed_goals_for_duration_avg, 2)
        print(f"\nAverage duration for completed (achieved/failed) goals: {avg_duration} seconds")
    else:
        print("\nNo goals completed to calculate average duration.")

    print("\nGoals by Type:")
    for goal_type, count in goals_by_type.items():
        print(f"  - {goal_type}: {count}")

    print("\nExample Goal Lifecycles (Conceptual):")
    # Print details for a couple of goals as examples
    example_goal_ids = list(analyzed_goals_data.keys())[:2] # Take first two goals
    for goal_id in example_goal_ids:
        if goal_id not in analyzed_goals_data or not analyzed_goals_data[goal_id].get("events_processed"):
            continue
        data = analyzed_goals_data[goal_id]
        print(f"\n  Goal ID: {data.get('goal_id', goal_id)}")
        print(f"    Description: {data.get('description', 'N/A')}")
        print(f"    Type: {data.get('type', 'N/A')}")
        print(f"    Creation Time: {data.get('creation_time', 'N/A')}")
        print(f"    Outcome: {data.get('outcome', data.get('current_state', 'N/A'))}")
        if "duration_seconds" in data:
            print(f"    Duration: {data['duration_seconds']}s")

        print("    State History:")
        for state_event in data.get("state_history", []):
            reason_str = f" (Reason: {state_event.get('reason')})" if state_event.get('reason') else ""
            print(f"      - {state_event.get('timestamp')}: {state_event.get('state')}{reason_str}")

        print("    Priority History:")
        for prio_event in data.get("priority_history", []):
            print(f"      - {prio_event.get('timestamp')}: Priority {prio_event.get('priority')}")

    print("\n--- End of Report ---")


if __name__ == "__main__":
    print("Starting conceptual Goal Dynamics Analysis...")

    parsed_logs = load_and_parse_log_data(HYPOTHETICAL_LOG_DATA)

    if parsed_logs:
        print(f"\nSuccessfully parsed {len(parsed_logs)} log entries.")
        analyzed_data = analyze_goal_lifecycles(parsed_logs)

        if analyzed_data:
            print(f"Successfully analyzed {len(analyzed_data)} goals.")
            generate_summary_report(analyzed_data)
        else:
            print("Analysis returned no data.")
    else:
        print("Log parsing returned no data.")

```
