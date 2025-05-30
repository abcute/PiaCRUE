#!/bin/bash

# PiaAGI_Hub/PiaAVT/examples/example_cli_usage.sh
# This script demonstrates common usage of the PiaAVT Command-Line Interface (cli.py).

# Ensure the script is run from the 'PiaAGI_Hub/PiaAVT/' directory or adjust path to cli.py accordingly.
# For simplicity, this example assumes it's run from PiaAGI_Hub/PiaAVT/
# If your current directory is 'examples/', you might call it as:
# cd .. && ./examples/example_cli_usage.sh

# Path to the CLI script
CLI_SCRIPT="./cli.py" # Assumes cli.py is in the current directory (PiaAVT/)
# If running from examples/ directory, use:
# CLI_SCRIPT="../cli.py"
# Or, more robustly, find the script relative to this example script's location:
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
CLI_SCRIPT_RELATIVE_TO_EXAMPLE="${SCRIPT_DIR}/../cli.py"

# Use the relative path if it exists, otherwise assume CWD is PiaAVT
if [ -f "$CLI_SCRIPT_RELATIVE_TO_EXAMPLE" ]; then
    CLI_SCRIPT="$CLI_SCRIPT_RELATIVE_TO_EXAMPLE"
    echo "Using CLI script at: $CLI_SCRIPT"
else
    echo "Assuming 'cli.py' is in the current working directory or PYTHONPATH."
    echo "If this fails, ensure you are in the 'PiaAGI_Hub/PiaAVT' directory or use 'python -m PiaAVT.cli'"
    # For python -m PiaAVT.cli, you'd need PiaAGI_Hub to be in PYTHONPATH
    # and PiaAVT to be a proper package with __main__.py or similar.
    # The current cli.py is a script, so direct execution is simpler for now.
fi


# 1. Create a dummy JSON log file
DUMMY_LOG_FILE="temp_cli_logs.json"
PLOT_OUTPUT_FILE="cli_example_plot.png"

echo "Creating dummy log file: $DUMMY_LOG_FILE"
cat << EOF > $DUMMY_LOG_FILE
[
    {"timestamp": "2024-03-01T10:00:00.000Z", "source": "SensorA", "event_type": "Reading", "data": {"temperature": 25.5, "humidity": 60}},
    {"timestamp": "2024-03-01T10:00:05.000Z", "source": "AgentCore", "event_type": "Decision", "data": {"action": "turn_left", "confidence": 0.9}},
    {"timestamp": "2024-03-01T10:00:10.000Z", "source": "SensorA", "event_type": "Reading", "data": {"temperature": 25.8, "humidity": 61}},
    {"timestamp": "2024-03-01T10:00:15.000Z", "source": "AgentCore", "event_type": "Action", "data": {"skill": "navigation", "result": "success"}},
    {"timestamp": "2024-03-01T10:00:20.000Z", "source": "SensorA", "event_type": "Reading", "data": {"temperature": 26.0, "humidity": 59}},
    {"timestamp": "2024-03-01T10:00:25.000Z", "source": "UserInteraction", "event_type": "Query", "data": {"text": "What is the temperature?"}},
    {"timestamp": "2024-03-01T10:00:30.000Z", "source": "AgentCore", "event_type": "Thinking", "data": {"module": "QA"}},
    {"timestamp": "2024-03-01T10:00:35.000Z", "source": "AgentCore", "event_type": "Response", "data": {"text": "The current temperature is 26.0 degrees."}}
]
EOF

echo -e "\n--- 1. Testing CLI: Load Logs ---"
python3 "$CLI_SCRIPT" load "$DUMMY_LOG_FILE"

echo -e "\n--- 2. Testing CLI: List Logs (first 3) ---"
python3 "$CLI_SCRIPT" list_logs --limit 3

echo -e "\n--- 3. Testing CLI: Get Statistics ---"
echo "Stats for 'temperature' from 'SensorA' readings:"
python3 "$CLI_SCRIPT" stats "data.temperature" --source "SensorA" --event_type "Reading"

echo -e "\n--- 4. Testing CLI: Plot Time Series ---"
echo "Plotting 'temperature' from 'SensorA' to $PLOT_OUTPUT_FILE (no interactive display)"
python3 "$CLI_SCRIPT" plot "data.temperature" --source "SensorA" --event_type "Reading" --output "$PLOT_OUTPUT_FILE" --title "Temperature Over Time (CLI)" --ylabel "Temperature (C)" --no_show
if [ -f "$PLOT_OUTPUT_FILE" ]; then
    echo "Plot successfully saved to $PLOT_OUTPUT_FILE"
else
    echo "Error: Plot file $PLOT_OUTPUT_FILE was not created."
fi

echo -e "\n--- 5. Testing CLI: Find Event Sequences ---"
# Define sequence: User Query -> Agent Thinking -> Agent Response
# JSON definition: '[{"event_type":"Query"},{"event_type":"Thinking"},{"event_type":"Response"}]'
# Simpler comma-separated for this example:
SEQUENCE_DEF_SIMPLE="Query,Thinking,Response"
echo "Finding sequence: $SEQUENCE_DEF_SIMPLE"
python3 "$CLI_SCRIPT" sequences "$SEQUENCE_DEF_SIMPLE" --max_logs 0
# Adding --max_logs 0 to make the sequence more specific for this test data

echo -e "\n--- 6. Testing CLI: View specific log entry data (e.g., entry 1 for AgentCore Decision) ---"
python3 "$CLI_SCRIPT" view_wm 1 # Index 1 is the AgentCore Decision log
# The view_wm and view_goals commands in cli.py have specific checks for source/event_type.
# If log entry 1 is not a WM log, it will display raw data.

echo -e "\n--- Cleaning up ---"
if [ -f "$DUMMY_LOG_FILE" ]; then
    rm "$DUMMY_LOG_FILE"
    echo "Removed dummy log file: $DUMMY_LOG_FILE"
fi
if [ -f "$PLOT_OUTPUT_FILE" ]; then
    rm "$PLOT_OUTPUT_FILE"
    echo "Removed plot output file: $PLOT_OUTPUT_FILE"
fi

echo -e "\nCLI Example Script Finished."

```
