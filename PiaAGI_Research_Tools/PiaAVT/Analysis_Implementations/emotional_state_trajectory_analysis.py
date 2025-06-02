# emotional_state_trajectory_analysis.py

import json
import tempfile
import os
import statistics

def load_and_parse_log_data_jsonl(log_file_path: str) -> list:
    """
    Reads a JSONL file, parses each line into a dictionary, and returns a list of these dictionaries.
    Handles potential FileNotFoundError and json.JSONDecodeError.
    """
    parsed_logs = []
    try:
        with open(log_file_path, 'r') as f:
            for line in f:
                stripped_line = line.strip()
                if not stripped_line:  # Skip empty lines
                    continue
                try:
                    parsed_logs.append(json.loads(stripped_line))
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from line: {stripped_line} - {e}")
                    # Optionally, skip corrupted lines or handle them differently
    except FileNotFoundError:
        print(f"Error: Log file not found at {log_file_path}")
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
    # Hypothetical JSONL log data
    log_data_str = """
    {"timestamp": 1678886400.1, "simulation_run_id": "sim_run_001", "agent_id": "agent_A", "event_type": "AGENT_ACTION", "event_data": {"action": "move_north"}}
    {"timestamp": 1678886402.3, "simulation_run_id": "sim_run_001", "agent_id": "agent_A", "event_type": "EMOTION_STATE_UPDATED", "event_data": {"current_vad": {"valence": 0.1, "arousal": 0.05, "dominance": 0.1}, "previous_vad": {"valence": 0.0, "arousal": 0.0, "dominance": 0.0}}}
    {"timestamp": 1678886403.5, "simulation_run_id": "sim_run_001", "agent_id": "agent_B", "event_type": "EMOTION_STATE_UPDATED", "event_data": {"current_vad": {"valence": -0.2, "arousal": 0.3, "dominance": 0.4}, "previous_vad": {"valence": -0.1, "arousal": 0.2, "dominance": 0.3}}}
    {"timestamp": 1678886405.0, "simulation_run_id": "sim_run_001", "agent_id": "agent_A", "event_type": "EMOTION_STATE_UPDATED", "event_data": {"current_vad": {"valence": 0.15, "arousal": 0.1, "dominance": 0.1}, "previous_vad": {"valence": 0.1, "arousal": 0.05, "dominance": 0.1}}}
    {"timestamp": 1678886406.0, "simulation_run_id": "sim_run_002", "agent_id": "agent_A", "event_type": "EMOTION_STATE_UPDATED", "event_data": {"current_vad": {"valence": 0.5, "arousal": 0.6, "dominance": 0.7}, "previous_vad": {"valence": 0.4, "arousal": 0.5, "dominance": 0.6}}}
    {"timestamp": 1678886407.8, "simulation_run_id": "sim_run_001", "agent_id": "agent_A", "event_type": "EMOTION_STATE_UPDATED", "event_data": {"current_vad": {"valence": 0.2, "arousal": 0.15, "dominance": 0.05}, "previous_vad": {"valence": 0.15, "arousal": 0.1, "dominance": 0.1}}}
    {"timestamp": 1678886408.2, "simulation_run_id": "sim_run_001", "agent_id": "agent_A", "event_type": "OTHER_EVENT", "event_data": {"info": "some other data"}}
    {"timestamp": 1678886409.5, "simulation_run_id": "sim_run_001", "agent_id": "agent_A", "event_type": "EMOTION_STATE_UPDATED", "event_data": {"NO_current_vad": {}}}

    """
    # Filter out empty lines from log_data_str before writing to ensure clean JSONL
    log_data_str_cleaned = "\n".join([line for line in log_data_str.splitlines() if line.strip()])


    temp_log_file_path = None # Initialize to prevent UnboundLocalError in finally if NamedTemporaryFile fails
    try:
        # Create a temporary file to write the log data
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".jsonl") as tmp_file:
            tmp_file.write(log_data_str_cleaned)
            temp_log_file_path = tmp_file.name
        
        print(f"Temporary log file created at: {temp_log_file_path}")

        # 1. Load and parse log data
        print("\nLoading and parsing log data...")
        parsed_data = load_and_parse_log_data_jsonl(temp_log_file_path)
        if not parsed_data:
            print("No data parsed, exiting.")
        else:
            print(f"Successfully parsed {len(parsed_data)} log entries.")

            # 2. Analyze emotional trajectory for a specific agent and simulation
            print("\nAnalyzing emotional trajectory for agent_A in sim_run_001...")
            analysis_results_A_sim1 = analyze_emotional_trajectory(
                parsed_data,
                target_agent_id="agent_A",
                target_simulation_run_id="sim_run_001"
            )
            # 3. Generate summary report
            generate_summary_report_emotional(analysis_results_A_sim1)

            # Example: Analyze for an agent across all simulations
            print("\nAnalyzing emotional trajectory for agent_B (all simulations)...")
            analysis_results_B = analyze_emotional_trajectory(
                parsed_data,
                target_agent_id="agent_B"
            )
            generate_summary_report_emotional(analysis_results_B)
            
            # Example: Analyze for a simulation across all agents
            print("\nAnalyzing emotional trajectory for sim_run_002 (all agents)...")
            analysis_results_sim2 = analyze_emotional_trajectory(
                parsed_data,
                target_simulation_run_id="sim_run_002"
            )
            generate_summary_report_emotional(analysis_results_sim2)

            # Example: Analyze all EMOTION_STATE_UPDATED events (no specific agent/sim)
            print("\nAnalyzing all EMOTION_STATE_UPDATED events...")
            analysis_all_emotions = analyze_emotional_trajectory(parsed_data)
            generate_summary_report_emotional(analysis_all_emotions)

            # Example: No matching logs
            print("\nAnalyzing for a non-existent agent...")
            analysis_no_match = analyze_emotional_trajectory(
                parsed_data,
                target_agent_id="agent_NonExistent"
            )
            generate_summary_report_emotional(analysis_no_match)

    finally:
        # Clean up the temporary file
        if temp_log_file_path and os.path.exists(temp_log_file_path):
            os.remove(temp_log_file_path)
            print(f"\nTemporary log file {temp_log_file_path} deleted.")
