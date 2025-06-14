# emotional_trajectory_analysis.py

import json
import argparse
from collections import defaultdict
from typing import List, Dict, Any, Optional

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
        parsed_logs.sort(key=lambda x: x.get("timestamp", float('inf')))
    except FileNotFoundError:
        print(f"Error: Log file not found at {log_file_path}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during log file processing: {e}")
        return []
    return parsed_logs

def analyze_emotional_trajectory(parsed_logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyzes parsed log data to extract a chronological list of emotional states.

    Args:
        parsed_logs: A list of log entry dictionaries, sorted by timestamp.

    Returns:
        A list of dictionaries, where each dictionary represents an emotional state snapshot.
    """
    emotional_states_chronological: List[Dict[str, Any]] = []

    for entry in parsed_logs:
        event_type = entry.get("event_type")
        event_data = entry.get("event_data", {})
        timestamp = entry.get("timestamp")
        agent_id = entry.get("agent_id", "unknown_agent") # Get agent_id from top level if available

        if event_type == "EMOTION_STATE_UPDATED" and timestamp is not None:
            # Prioritize fields as per Logging_Specification.md example for EMOTION_STATE_UPDATED
            current_vad = event_data.get("current_vad")
            # Fallback if current_vad is not present but current_emotion_profile (from other modules) might be
            if current_vad is None:
                current_vad = event_data.get("current_emotion_profile", {}) # Ensure it's a dict

            valence = current_vad.get("valence")
            arousal = current_vad.get("arousal")
            dominance = current_vad.get("dominance") # May be None

            discrete_emotion = event_data.get("current_discrete_emotion")
            # Fallback for primary_emotion if current_discrete_emotion is not present
            if discrete_emotion is None:
                discrete_emotion = event_data.get("primary_emotion", "N/A")

            intensity = event_data.get("intensity") # Intensity of the discrete emotion

            # Ensure V, A are present, D is optional
            if valence is not None and arousal is not None:
                state_snapshot = {
                    "timestamp": timestamp,
                    "agent_id": agent_id,
                    "valence": valence,
                    "arousal": arousal,
                    "dominance": dominance, # Could be None
                    "discrete_emotion": discrete_emotion,
                    "intensity": intensity # Could be None
                }
                emotional_states_chronological.append(state_snapshot)
            else:
                print(f"Warning: EMOTION_STATE_UPDATED event at {timestamp} missing VAD data in 'current_vad' or 'current_emotion_profile'. Entry: {event_data}")

    return emotional_states_chronological

def generate_emotional_trajectory_report(emotional_states_chronological: List[Dict[str, Any]]):
    """
    Generates and prints a summary report for the emotional trajectory.

    Args:
        emotional_states_chronological: A list of emotional state snapshots.
    """
    if not emotional_states_chronological:
        print("No emotional state changes recorded or suitable data found.")
        return

    print("\n--- Emotional Trajectory Analysis Report ---")
    print(f"Total emotional state changes recorded: {len(emotional_states_chronological)}")

    # Print first few snapshots
    print("\nInitial Emotional States (first 5):")
    print("Timestamp           | Agent ID         | Valence | Arousal | Dominance | Discrete Emotion   | Intensity")
    print("--------------------|------------------|---------|---------|-----------|--------------------|-----------")
    for state in emotional_states_chronological[:5]:
        ts = state.get('timestamp', 'N/A')
        if isinstance(ts, float): ts = f"{ts:.2f}"
        dom = state.get('dominance')
        dom_str = f"{dom:.2f}" if dom is not None else "N/A"
        intensity_val = state.get('intensity')
        intensity_str = f"{intensity_val:.2f}" if intensity_val is not None else "N/A"
        print(f"{str(ts):<20}| {str(state.get('agent_id','N/A')):<16} | {state.get('valence', 0):<7.2f} | {state.get('arousal', 0):<7.2f} | {dom_str:<9} | {str(state.get('discrete_emotion','N/A')):<18} | {intensity_str:<9}")

    # Print last few snapshots
    if len(emotional_states_chronological) > 5:
        print("\nFinal Emotional States (last 5):")
        print("Timestamp           | Agent ID         | Valence | Arousal | Dominance | Discrete Emotion   | Intensity")
        print("--------------------|------------------|---------|---------|-----------|--------------------|-----------")
        for state in emotional_states_chronological[-5:]:
            ts = state.get('timestamp', 'N/A')
            if isinstance(ts, float): ts = f"{ts:.2f}"
            dom = state.get('dominance')
            dom_str = f"{dom:.2f}" if dom is not None else "N/A"
            intensity_val = state.get('intensity')
            intensity_str = f"{intensity_val:.2f}" if intensity_val is not None else "N/A"
            print(f"{str(ts):<20}| {str(state.get('agent_id','N/A')):<16} | {state.get('valence', 0):<7.2f} | {state.get('arousal', 0):<7.2f} | {dom_str:<9} | {str(state.get('discrete_emotion','N/A')):<18} | {intensity_str:<9}")

    # Conceptual Aggregates
    total_valence, total_arousal, total_dominance, total_intensity = 0.0, 0.0, 0.0, 0.0
    num_dominance_entries, num_intensity_entries = 0, 0
    discrete_emotion_counts = defaultdict(int)

    for state in emotional_states_chronological:
        total_valence += state.get('valence', 0.0)
        total_arousal += state.get('arousal', 0.0)
        if state.get('dominance') is not None:
            total_dominance += state['dominance']
            num_dominance_entries += 1
        if state.get('intensity') is not None:
            total_intensity += state['intensity']
            num_intensity_entries +=1
        if state.get('discrete_emotion') and state.get('discrete_emotion') != 'N/A':
            discrete_emotion_counts[state['discrete_emotion']] += 1

    num_states = len(emotional_states_chronological)
    if num_states > 0:
        print("\nAggregate Emotional Statistics:")
        print(f"  Average Valence: {total_valence/num_states:.3f}")
        print(f"  Average Arousal: {total_arousal/num_states:.3f}")
        if num_dominance_entries > 0:
            print(f"  Average Dominance (where available): {total_dominance/num_dominance_entries:.3f} (from {num_dominance_entries} entries)")
        else:
            print("  Average Dominance: N/A (no dominance data)")
        if num_intensity_entries > 0:
            print(f"  Average Intensity (where available): {total_intensity/num_intensity_entries:.3f} (from {num_intensity_entries} entries)")
        else:
            print("  Average Intensity: N/A (no intensity data)")


    if discrete_emotion_counts:
        print("\nDiscrete Emotion Frequencies:")
        for emotion, count in sorted(discrete_emotion_counts.items(), key=lambda item: item[1], reverse=True):
            print(f"  - {emotion}: {count} occurrences")
    else:
        print("\nNo discrete emotion data recorded.")

    print("\nNote: This data can be plotted to visualize VAD trajectories and discrete emotion occurrences over time.")
    print("--- End of Report ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyzes emotional trajectory from PiaAVT JSONL log files.",
        epilog="Example: python emotional_trajectory_analysis.py /path/to/your/logfile.jsonl"
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

    print(f"Starting Emotional Trajectory Analysis for log file: {args.log_file}...")
    parsed_logs = load_and_parse_log_data_jsonl(args.log_file)

    if parsed_logs:
        print(f"\nSuccessfully parsed {len(parsed_logs)} log entries from {args.log_file}.")
        emotional_trajectory_data = analyze_emotional_trajectory(parsed_logs)

        if emotional_trajectory_data:
            print(f"Successfully extracted {len(emotional_trajectory_data)} emotional state update events.")
            generate_emotional_trajectory_report(emotional_trajectory_data)
        else:
            print("No EMOTION_STATE_UPDATED events found in the logs.")
    else:
        print(f"Log parsing returned no data from {args.log_file}. Ensure the file exists, is not empty, and contains valid JSONL.")
