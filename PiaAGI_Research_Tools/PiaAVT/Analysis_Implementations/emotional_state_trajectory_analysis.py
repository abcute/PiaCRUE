# emotional_state_trajectory_analysis.py

import json
import os # Keep os for path operations if needed, but tempfile might not be.
import statistics
import argparse # Added for command-line arguments

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

def analyze_emotional_trajectory(parsed_logs: list, target_agent_id: str = None, target_simulation_run_id: str = None) -> dict:
    """
    Analyzes emotional state trajectory from parsed log data.
    Filters logs for EMOTION_STATE_UPDATED events and optionally by agent_id and simulation_run_id.
    Extracts timestamp and VAD values.
    Calculates summary statistics for VAD values.
    """
    trajectory = []
    relevant_logs = []

    # Filter for EMOTION_STATE_UPDATED events
    for log_entry in parsed_logs:
        if log_entry.get("event_type") == "EMOTION_STATE_UPDATED":
            relevant_logs.append(log_entry)

    # Filter by target_agent_id if provided
    if target_agent_id:
        relevant_logs = [log for log in relevant_logs if log.get("agent_id") == target_agent_id]

    # Filter by target_simulation_run_id if provided
    if target_simulation_run_id:
        relevant_logs = [log for log in relevant_logs if log.get("simulation_run_id") == target_simulation_run_id]

    # Extract VAD data and timestamps
    actual_agent_id_from_logs = target_agent_id
    actual_sim_id_from_logs = target_simulation_run_id
    
    # Determine unique agent_ids and sim_ids from the relevant logs if no target is specified
    # This helps in more accurate reporting when analyzing across all agents/simulations
    if not target_agent_id and relevant_logs:
        unique_agent_ids = set(log.get("agent_id") for log in relevant_logs if log.get("agent_id"))
        if len(unique_agent_ids) == 1:
            actual_agent_id_from_logs = unique_agent_ids.pop()
        elif len(unique_agent_ids) > 1:
            actual_agent_id_from_logs = "Multiple_Agents" # Or "N/A" or similar indicator
        # else, it remains None or the initially set target_agent_id (which is None here)

    if not target_simulation_run_id and relevant_logs:
        unique_sim_ids = set(log.get("simulation_run_id") for log in relevant_logs if log.get("simulation_run_id"))
        if len(unique_sim_ids) == 1:
            actual_sim_id_from_logs = unique_sim_ids.pop()
        elif len(unique_sim_ids) > 1:
            actual_sim_id_from_logs = "Multiple_Sim_Runs" # Or "N/A"
        # else, it remains None or the initially set target_simulation_run_id

    for log in relevant_logs:
        timestamp = log.get("timestamp")
        event_data = log.get("event_data", {})
        current_vad = event_data.get("current_vad")

        # Update agent_id and sim_id if they were not targeted and not yet set from unique values
        if target_agent_id is None and actual_agent_id_from_logs is None and log.get("agent_id"):
             # This case is less likely now with the pre-check, but as a fallback
            actual_agent_id_from_logs = log.get("agent_id")
        if target_simulation_run_id is None and actual_sim_id_from_logs is None and log.get("simulation_run_id"):
            actual_sim_id_from_logs = log.get("simulation_run_id")

        if timestamp is not None and current_vad is not None:
            valence = current_vad.get("valence")
            arousal = current_vad.get("arousal")
            dominance = current_vad.get("dominance")
            if None not in [valence, arousal, dominance]:
                trajectory.append({
                    "timestamp": timestamp,
                    "valence": valence,
                    "arousal": arousal,
                    "dominance": dominance
                })

    # Calculate summary statistics
    summary_stats = {
        "avg_valence": 0.0, "std_valence": 0.0,
        "avg_arousal": 0.0, "std_arousal": 0.0,
        "avg_dominance": 0.0, "std_dominance": 0.0,
        "count": len(trajectory)
    }

    if trajectory:
        valences = [t["valence"] for t in trajectory]
        arousals = [t["arousal"] for t in trajectory]
        dominances = [t["dominance"] for t in trajectory]

        summary_stats["avg_valence"] = statistics.mean(valences) if valences else 0.0
        summary_stats["std_valence"] = statistics.stdev(valences) if len(valences) > 1 else 0.0
        summary_stats["avg_arousal"] = statistics.mean(arousals) if arousals else 0.0
        summary_stats["std_arousal"] = statistics.stdev(arousals) if len(arousals) > 1 else 0.0
        summary_stats["avg_dominance"] = statistics.mean(dominances) if dominances else 0.0
        summary_stats["std_dominance"] = statistics.stdev(dominances) if len(dominances) > 1 else 0.0

    return {
        "agent_id": actual_agent_id_from_logs,
        "simulation_run_id": actual_sim_id_from_logs,
        "trajectory": trajectory,
        "summary_stats": summary_stats
    }

def generate_summary_report_emotional(analysis_results: dict):
    """
    Prints a textual summary of the emotional trajectory analysis results.
    """
    print("\n--- Emotional State Trajectory Analysis Report ---")
    agent_id = analysis_results.get("agent_id", "N/A")
    sim_id = analysis_results.get("simulation_run_id", "N/A")
    count = analysis_results["summary_stats"]["count"]

    print(f"Agent ID: {agent_id}")
    print(f"Simulation Run ID: {sim_id}")
    print(f"Number of EMOTION_STATE_UPDATED events processed: {count}")

    if count > 0:
        print("\nSummary Statistics (VAD):")
        stats = analysis_results["summary_stats"]
        print(f"  Valence: Avg={stats['avg_valence']:.3f}, StdDev={stats['std_valence']:.3f}")
        print(f"  Arousal: Avg={stats['avg_arousal']:.3f}, StdDev={stats['std_arousal']:.3f}")
        print(f"  Dominance: Avg={stats['avg_dominance']:.3f}, StdDev={stats['std_dominance']:.3f}")

        print("\nTrajectory Timestamps (first 5 if available):")
        for i, point in enumerate(analysis_results["trajectory"][:5]):
            print(f"  {i+1}. Timestamp: {point['timestamp']}, V: {point['valence']:.2f}, A: {point['arousal']:.2f}, D: {point['dominance']:.2f}")
        if count > 5:
            print(f"  ... and {count - 5} more points.")
    else:
        print("No relevant emotional state update events found for the specified criteria.")
    print("--- End of Report ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyzes emotional state trajectory from PiaAVT JSONL log files.",
        epilog="Example: python emotional_state_trajectory_analysis.py /path/to/your/logfile.jsonl --agent_id agent_A --sim_id sim_run_001"
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

    if not args.log_file: # Though argparse handles required arguments, this is a safeguard.
        parser.print_usage()
        print("Error: Log file path is required.")
        exit(1)

    print(f"Starting Emotional State Trajectory Analysis for log file: {args.log_file}...")
    if args.agent_id:
        print(f"Filtering for Agent ID: {args.agent_id}")
    if args.sim_id:
        print(f"Filtering for Simulation Run ID: {args.sim_id}")

    parsed_logs = load_and_parse_log_data_jsonl(args.log_file)

    if parsed_logs:
        print(f"\nSuccessfully parsed {len(parsed_logs)} log entries from {args.log_file}.")
        
        # Analyze emotional trajectory based on provided arguments
        analysis_results = analyze_emotional_trajectory(
            parsed_logs,
            target_agent_id=args.agent_id,
            target_simulation_run_id=args.sim_id
        )
        
        # Generate summary report
        generate_summary_report_emotional(analysis_results)
        
        # You can add more specific examples here if needed, for instance,
        # always running an "all events" analysis for comparison:
        # print("\nAnalyzing all EMOTION_STATE_UPDATED events (for comparison)...")
        # analysis_all_emotions = analyze_emotional_trajectory(parsed_logs)
        # generate_summary_report_emotional(analysis_all_emotions)

    else:
        print(f"Log parsing returned no data from {args.log_file}. Ensure the file exists, is not empty, and contains valid JSONL.")
