# PiaAGI_Hub/PiaAVT/examples/example_learning_progress.py

import json
import os
from datetime import datetime, timedelta

# Assuming PiaAVT is installed or PYTHONPATH is set up to find PiaAGI_Hub.PiaAVT
# For direct execution, ensure api.py and its dependencies are findable.
try:
    from PiaAGI_Hub.PiaAVT.api import PiaAVTAPI, DEFAULT_TIMESTAMP_FORMAT
except ImportError:
    print("Attempting fallback import for PiaAVTAPI. Ensure PiaAVT is in PYTHONPATH or installed.")
    # This is a simplified fallback, consider a proper package structure for robustness
    import sys
    # Add the parent directory of PiaAGI_Hub to sys.path if PiaAVT is not installed
    # This is a common pattern for examples within a project but not ideal for distribution
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pia_avt_dir = os.path.dirname(current_dir) # This should be PiaAVT directory
    pia_agi_hub_dir = os.path.dirname(pia_avt_dir) # This should be PiaAGI_Hub

    # Check if we are in examples directory, then PiaAVT, then PiaAGI_Hub
    if os.path.basename(current_dir) == "examples" and        os.path.basename(pia_avt_dir) == "PiaAVT" and        os.path.basename(pia_agi_hub_dir) == "PiaAGI_Hub":
        sys.path.insert(0, pia_agi_hub_dir) # Add PiaAGI_Hub to path
        from PiaAVT.api import PiaAVTAPI, DEFAULT_TIMESTAMP_FORMAT # Now this should work
    else: # If structure is different, this might fail
        raise ImportError("Could not resolve PiaAVTAPI import. Please ensure correct package structure and PYTHONPATH.")


def generate_sample_learning_logs(num_epochs: int = 50) -> list:
    """Generates sample log data simulating agent learning progress."""
    logs = []
    start_time = datetime.utcnow()
    current_reward = 10.0
    current_error = 0.8

    for i in range(num_epochs):
        timestamp = (start_time + timedelta(seconds=i * 10)).strftime(DEFAULT_TIMESTAMP_FORMAT)

        # Simulate improving reward and decreasing error
        current_reward += (0.5 - (i / num_epochs * 0.3)) + (hash(timestamp) % 100 / 200.0 - 0.25) # Add some noise
        current_error -= (0.01 - (i / num_epochs * 0.005)) + (hash(timestamp) % 100 / 5000.0 - 0.01)
        current_reward = max(0, min(current_reward, 25.0))
        current_error = max(0.05, min(current_error, 0.8))

        log_entry = {
            "timestamp": timestamp,
            "source": "PiaSE.TrainingLoop",
            "event_type": "EpochEnd",
            "data": {
                "epoch": i + 1,
                "average_reward": round(current_reward, 2),
                "error_rate": round(current_error, 3),
                "steps_taken": 100 + (hash(timestamp) % 20 - 10) # Some variation
            }
        }
        logs.append(log_entry)
    return logs

def main():
    print("--- PiaAVT Example: Analyzing Learning Progress ---")

    # 1. Generate sample log data
    sample_logs = generate_sample_learning_logs(num_epochs=30)
    temp_log_file = "temp_learning_logs.json"

    # 2. Save data to a temporary JSON file
    try:
        with open(temp_log_file, 'w') as f:
            json.dump(sample_logs, f, indent=2)
        print(f"Sample learning logs saved to {temp_log_file}")
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

    print(f"Successfully loaded {api.get_log_count()} log entries.")

    # 4. Use the API to calculate descriptive statistics for performance metrics
    print("\n--- Descriptive Statistics ---")
    reward_stats = api.get_stats_for_field(data_field_path="average_reward", event_type="EpochEnd")
    if reward_stats:
        api.display_formatted_dict(reward_stats, title="Average Reward Statistics")

    error_stats = api.get_stats_for_field(data_field_path="error_rate", event_type="EpochEnd")
    if error_stats:
        api.display_formatted_dict(error_stats, title="Error Rate Statistics")

    # 5. Use the API to plot the learning curves
    print("\n--- Plotting Learning Curves ---")

    # Plot Average Reward
    api.plot_field_over_time(
        data_field_path="average_reward",
        event_type="EpochEnd",
        title="Agent Learning Progress: Average Reward per Epoch",
        y_label="Average Reward",
        output_file="learning_curve_reward.png",
        show_plot=True # Set to False if running in a non-GUI environment or for automated tests
    )
    print("Reward learning curve plot generated as 'learning_curve_reward.png'.")

    # Plot Error Rate
    api.plot_field_over_time(
        data_field_path="error_rate",
        event_type="EpochEnd",
        title="Agent Learning Progress: Error Rate per Epoch",
        y_label="Error Rate",
        output_file="learning_curve_error.png",
        show_plot=True # Set to False for non-GUI
    )
    print("Error rate learning curve plot generated as 'learning_curve_error.png'.")

    # Example: Get time series data for 'steps_taken' and print first 5
    steps_ts_data = api.get_timeseries_for_field(data_field_path="steps_taken", event_type="EpochEnd")
    if steps_ts_data:
        print("\n--- Sample Time Series Data (Steps Taken per Epoch) ---")
        for i, (ts, val) in enumerate(steps_ts_data[:5]):
            print(f"Epoch (approx {i+1}), Time: {ts.strftime('%H:%M:%S')}, Steps: {val}")


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
