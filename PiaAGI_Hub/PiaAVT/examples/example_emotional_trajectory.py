# PiaAGI_Hub/PiaAVT/examples/example_emotional_trajectory.py

import json
import os
from datetime import datetime, timedelta
import random

# Import PiaAVTAPI (handle potential import issues for examples)
try:
    from PiaAGI_Hub.PiaAVT.api import PiaAVTAPI, DEFAULT_TIMESTAMP_FORMAT
except ImportError:
    print("Attempting fallback import for PiaAVTAPI. Ensure PiaAVT is in PYTHONPATH or installed.")
    import sys
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pia_avt_dir = os.path.dirname(current_dir)
    pia_agi_hub_dir = os.path.dirname(pia_avt_dir)
    if os.path.basename(current_dir) == "examples" and        os.path.basename(pia_avt_dir) == "PiaAVT" and        os.path.basename(pia_agi_hub_dir) == "PiaAGI_Hub":
        sys.path.insert(0, pia_agi_hub_dir)
        from PiaAVT.api import PiaAVTAPI, DEFAULT_TIMESTAMP_FORMAT
    else:
        raise ImportError("Could not resolve PiaAVTAPI import. Please ensure correct package structure and PYTHONPATH.")

def generate_sample_emotion_logs(num_entries: int = 40) -> list:
    """Generates sample log data simulating agent emotional state changes."""
    logs = []
    start_time = datetime.utcnow()
    valence = 0.0  # Start neutral
    arousal = 0.1  # Start slightly calm

    for i in range(num_entries):
        timestamp = (start_time + timedelta(seconds=i * 5)).strftime(DEFAULT_TIMESTAMP_FORMAT)

        # Simulate some emotional dynamics
        if i % 10 == 0 and i > 0: # Simulate a significant event
            valence_change = random.uniform(-0.5, 0.5)
            arousal_change = random.uniform(0.1, 0.3)
        else: # Gradual changes
            valence_change = random.uniform(-0.1, 0.1)
            arousal_change = random.uniform(-0.05, 0.05)

        valence = max(-1.0, min(1.0, valence + valence_change))
        arousal = max(0.0, min(1.0, arousal + arousal_change))

        # Determine a dominant emotion based on valence/arousal (simplified)
        dominant_emotion = "neutral"
        if valence > 0.3 and arousal > 0.4:
            dominant_emotion = "joy"
        elif valence < -0.3 and arousal > 0.4:
            dominant_emotion = "anger" if valence < -0.5 else "fear" # simplistic distinction
        elif valence < -0.2:
            dominant_emotion = "sadness"
        elif arousal > 0.6:
            dominant_emotion = "surprise"


        log_entry = {
            "timestamp": timestamp,
            "source": "PiaCML.EmotionModule",
            "event_type": "StateUpdate",
            "data": {
                "valence": round(valence, 2),
                "arousal": round(arousal, 2),
                "dominant_emotion_estimated": dominant_emotion,
                "triggering_event_id": f"evt_{i:03d}" # Example of related data
            }
        }
        logs.append(log_entry)
    return logs

def main():
    print("--- PiaAVT Example: Analyzing Emotional Trajectory ---")

    # 1. Generate sample log data
    sample_logs = generate_sample_emotion_logs(num_entries=50)
    temp_log_file = "temp_emotion_logs.json"

    # 2. Save data to a temporary JSON file
    try:
        with open(temp_log_file, 'w') as f:
            json.dump(sample_logs, f, indent=2)
        print(f"Sample emotion logs saved to {temp_log_file}")
    except IOError as e:
        print(f"Error saving sample logs: {e}")
        return

    # 3. Use PiaAVTAPI to load these logs
    api = PiaAVTAPI()
    success = api.load_logs_from_json(temp_log_file)

    if not success:
        print("Failed to load logs into PiaAVT. Exiting example.")
        if os.path.exists(temp_log_file):
            os.remove(temp_log_file)
        return

    print(f"Successfully loaded {api.get_log_count()} emotion log entries.")

    # 4. Plot the trajectory of valence and arousal
    print("\n--- Plotting Emotional Trajectories ---")

    api.plot_field_over_time(
        data_field_path="valence",
        source="PiaCML.EmotionModule",
        event_type="StateUpdate",
        title="Agent Emotional Trajectory: Valence Over Time",
        y_label="Valence (-1 to 1)",
        output_file="emotion_trajectory_valence.png",
        show_plot=True # Set to False for non-GUI
    )
    print("Valence trajectory plot generated as 'emotion_trajectory_valence.png'.")

    api.plot_field_over_time(
        data_field_path="arousal",
        source="PiaCML.EmotionModule",
        event_type="StateUpdate",
        title="Agent Emotional Trajectory: Arousal Over Time",
        y_label="Arousal (0 to 1)",
        output_file="emotion_trajectory_arousal.png",
        show_plot=True # Set to False for non-GUI
    )
    print("Arousal trajectory plot generated as 'emotion_trajectory_arousal.png'.")

    # 5. Extract and display specific emotional state entries
    print("\n--- Specific Emotional State Details ---")
    all_emotion_logs = api.get_analyzer().filter_logs(source="PiaCML.EmotionModule", event_type="StateUpdate")

    if len(all_emotion_logs) >= 3:
        # Display first, middle, and last emotion log entries as examples
        indices_to_show = [0, len(all_emotion_logs) // 2, len(all_emotion_logs) - 1]
        for i, log_index in enumerate(indices_to_show):
            entry_to_display = all_emotion_logs[log_index]
            api.display_formatted_dict(
                entry_to_display['data'],
                title=f"Emotion State at {entry_to_display['timestamp']} (Entry {log_index+1})"
            )
            print("") # Add a newline for better separation
    else:
        print("Not enough emotion logs to display specific entries.")

    # Example of counting dominant emotions
    analyzer = api.get_analyzer()
    if analyzer:
        dominant_emotion_counts = analyzer.count_unique_values(
            field_name="dominant_emotion_estimated", # This is the key within 'data'
            source="PiaCML.EmotionModule",
            event_type="StateUpdate",
            is_data_field=True, # Specify that the field is within the 'data' dictionary
            data_field_path="dominant_emotion_estimated" # Provide the path within 'data'
        )
        if dominant_emotion_counts:
            api.display_formatted_dict(
                dict(dominant_emotion_counts),
                title="Dominant Emotion Counts"
            )


    # Clean up the temporary log file
    try:
        if os.path.exists(temp_log_file):
            os.remove(temp_log_file)
            print(f"Cleaned up {temp_log_file}")
    except IOError as e:
        print(f"Error cleaning up temp file: {e}")

    print("\n--- Example Complete ---")

if __name__ == "__main__":
    main()
```
