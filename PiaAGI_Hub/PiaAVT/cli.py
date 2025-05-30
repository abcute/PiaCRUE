# PiaAGI_Hub/PiaAVT/cli.py
import argparse
import sys
import os # For path manipulation in fallback import
from typing import Union, List # For type hinting _parse_field_path
import json # Ensure json is imported for parsing sequence definition

# Attempt to import PiaAVTAPI from the api module within the same package
try:
    from .api import PiaAVTAPI, DEFAULT_TIMESTAMP_FORMAT # Assuming DEFAULT_TIMESTAMP_FORMAT might be useful
except ImportError:
    # Fallback for running cli.py directly for development/testing
    print("CLI: Attempting fallback import for PiaAVTAPI. Ensure PiaAVT package structure is correct or use `python -m PiaAGI_Hub.PiaAVT.cli`.", file=sys.stderr)
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        from api import PiaAVTAPI, DEFAULT_TIMESTAMP_FORMAT
    except ImportError:
        sys.path.insert(0, current_script_dir)
        try:
            from api import PiaAVTAPI, DEFAULT_TIMESTAMP_FORMAT
        except ImportError as e_final:
            print(f"CLI Error: Could not import PiaAVTAPI. Final error: {e_final}", file=sys.stderr)
            sys.exit(1)


pia_api_instance: PiaAVTAPI | None = None

def _ensure_api_initialized_and_logs_loaded() -> bool:
    """Checks if the API is initialized and logs are loaded, prints error if not."""
    if not pia_api_instance:
        print("CLI Error: API not initialized. Please use the 'load' command first to load log data.", file=sys.stderr)
        return False
    if pia_api_instance.get_log_count() == 0:
        print("CLI Error: No logs loaded. Please use the 'load' command first.", file=sys.stderr)
        return False
    return True

def _parse_field_path(field_path_str: str) -> Union[str, List[str]]:
    """Converts a dot-notated string path to a list of keys if needed."""
    if '.' in field_path_str:
        return field_path_str.split('.')
    return field_path_str

def handle_load(args):
    """Handles the 'load' command."""
    global pia_api_instance
    if pia_api_instance is None:
        pia_api_instance = PiaAVTAPI()

    print(f"CLI: Loading logs from: {args.filepath}...")
    success = pia_api_instance.load_logs_from_json(args.filepath)
    if success:
        print(f"CLI: Successfully loaded {pia_api_instance.get_log_count()} log entries.")
    else:
        print(f"CLI: Failed to load logs from {args.filepath}.", file=sys.stderr)

def handle_stats(args):
    """Handles the 'stats' command."""
    if not _ensure_api_initialized_and_logs_loaded():
        return

    field_path = _parse_field_path(args.field_path)
    print(f"CLI: Calculating statistics for field path: {field_path}...")

    stats = pia_api_instance.get_stats_for_field(
        field_path,
        source=args.source,
        event_type=args.event_type,
        start_time_str=args.start_time,
        end_time_str=args.end_time
    )
    if stats:
        pia_api_instance.display_formatted_dict(stats, title=f"Statistics for '{args.field_path}'")
    else:
        print(f"CLI: No statistics found for field '{args.field_path}' with the given filters.")

def handle_plot(args):
    """Handles the 'plot' command."""
    if not _ensure_api_initialized_and_logs_loaded():
        return

    field_path = _parse_field_path(args.field_path)
    plot_title = args.title or f"Time Series for '{args.field_path}'"
    plot_ylabel = args.ylabel or args.field_path

    print(f"CLI: Generating plot for field path: {field_path}...")
    if args.output:
        print(f"  Attempting to save plot to: {args.output}")
    if args.no_show:
        print("  Plot display suppressed (--no_show).")

    pia_api_instance.plot_field_over_time(
        field_path,
        title=plot_title,
        y_label=plot_ylabel,
        source=args.source,
        event_type=args.event_type,
        start_time_str=args.start_time,
        end_time_str=args.end_time,
        output_file=args.output,
        show_plot=not args.no_show
    )

def handle_view_goals(args):
    """Handles the 'view_goals' command."""
    if not _ensure_api_initialized_and_logs_loaded():
        return

    logs = pia_api_instance.get_all_logs()
    try:
        index = int(args.log_index)
        if 0 <= index < len(logs):
            log_entry = logs[index]
            if log_entry.get("source") == "PiaCML.Motivation" and "active_goals" in log_entry.get("data", {}):
                print(f"CLI: Displaying goals from log entry at index {index} (Source: {log_entry.get('source')}, Event: {log_entry.get('event_type')})...")
                pia_api_instance.display_goals_from_log_entry(log_entry.get('data'))
            else:
                print(f"CLI: Log entry at index {index} (Source: {log_entry.get('source')}, Event: {log_entry.get('event_type')}) does not appear to be a standard goal log.")
                print("Displaying its 'data' field for inspection:")
                pia_api_instance.display_formatted_dict(log_entry.get('data', {}), title=f"Data for Log Entry {index}")
        else:
            print(f"CLI Error: Log index {index} is out of range (0 to {len(logs)-1}).", file=sys.stderr)
    except ValueError:
        print(f"CLI Error: Log index '{args.log_index}' must be an integer.", file=sys.stderr)
    except Exception as e:
        print(f"CLI Error: An unexpected error occurred while viewing goals: {e}", file=sys.stderr)

def handle_view_wm(args):
    """Handles the 'view_wm' command."""
    if not _ensure_api_initialized_and_logs_loaded():
        return

    logs = pia_api_instance.get_all_logs()
    try:
        index = int(args.log_index)
        if 0 <= index < len(logs):
            log_entry = logs[index]
            if log_entry.get("source") == "PiaCML.WorkingMemory" and "active_elements" in log_entry.get("data", {}):
                print(f"CLI: Displaying Working Memory state from log entry at index {index} (Source: {log_entry.get('source')}, Event: {log_entry.get('event_type')})...")
                pia_api_instance.display_wm_from_log_entry(log_entry.get('data'))
            else:
                print(f"CLI: Log entry at index {index} (Source: {log_entry.get('source')}, Event: {log_entry.get('event_type')}) does not appear to be a standard WM log.")
                print("Displaying its 'data' field for inspection:")
                pia_api_instance.display_formatted_dict(log_entry.get('data', {}), title=f"Data for Log Entry {index}")
        else:
            print(f"CLI Error: Log index {index} is out of range (0 to {len(logs)-1}).", file=sys.stderr)
    except ValueError:
        print(f"CLI Error: Log index '{args.log_index}' must be an integer.", file=sys.stderr)
    except Exception as e:
        print(f"CLI Error: An unexpected error occurred while viewing WM: {e}", file=sys.stderr)

def handle_list_logs(args):
    """Handles the 'list_logs' command."""
    if not _ensure_api_initialized_and_logs_loaded():
        return

    logs = pia_api_instance.get_all_logs()
    limit = args.limit if args.limit is not None and args.limit > 0 else len(logs)

    print(f"CLI: Displaying up to {limit} of {len(logs)} loaded log entries...")
    if not logs:
        print("No logs to display.")
        return

    for i, log_entry in enumerate(logs[:limit]):
        print(f"--- Log Entry {i} ---")
        print(f"  Timestamp: {log_entry.get('timestamp')}")
        print(f"  Source:    {log_entry.get('source')}")
        print(f"  Event Type: {log_entry.get('event_type')}")
        data_summary = str(log_entry.get('data', {}))
        if len(data_summary) > 100:
            data_summary = data_summary[:97] + "..."
        print(f"  Data:      {data_summary}")

    if limit < len(logs):
        print(f"... and {len(logs) - limit} more log(s) not shown.")

def handle_sequences(args):
    """Handles the 'sequences' command."""
    if not _ensure_api_initialized_and_logs_loaded():
        return

    print(f"CLI: Finding event sequences for definition: {args.definition_str}")
    print(f"  Max time between steps: {args.max_time}s")
    print(f"  Max intervening logs: {args.max_logs}")

    try:
        # Attempt to parse as JSON list of dicts
        sequence_definition = json.loads(args.definition_str)
        if not isinstance(sequence_definition, list) or \
           not all(isinstance(step, dict) and "event_type" in step for step in sequence_definition):
            raise ValueError("Definition must be a JSON list of objects, each with at least 'event_type'.")
    except json.JSONDecodeError:
        # Fallback: Try simple comma-separated event_types (no source)
        print("CLI Info: Could not parse definition as JSON. Trying as comma-separated event_types (no source matching).")
        event_types = [et.strip() for et in args.definition_str.split(',')]
        if not all(event_types):
             print("CLI Error: Invalid format for simple event type sequence. Use comma-separated values e.g., 'EventA,EventB'.", file=sys.stderr)
             return
        sequence_definition = [{"event_type": et} for et in event_types]
    except ValueError as e:
        print(f"CLI Error: Invalid sequence definition format. {e}", file=sys.stderr)
        print("  Use a JSON string like '[{\"event_type\":\"TypeA\"}, {\"event_type\":\"TypeB\",\"source\":\"SrcB\"}]'", file=sys.stderr)
        print("  Or a simple comma-separated list of event types like 'TypeA,TypeB,TypeC'", file=sys.stderr)
        return

    if not pia_api_instance:
        return

    formatted_output = pia_api_instance.get_formatted_event_sequences(
        sequence_definition,
        max_time_between_steps_seconds=args.max_time,
        max_intervening_logs=args.max_logs,
        allow_repeats_in_definition=args.allow_repeats
    )
    print(formatted_output)

def main():
    parser = argparse.ArgumentParser(
        description="PiaAVT Command-Line Interface. Use 'load' command first to load log data.",
        epilog="Example: python cli.py load path/to/logs.json then python cli.py stats data.reward"
    )
    subparsers = parser.add_subparsers(title="commands", dest="command",
                                       help="Available PiaAVT commands. Type a command followed by -h for more help (e.g., load -h).")

    # --- Load command ---
    load_parser = subparsers.add_parser("load", help="Load log data from a JSON file.")
    load_parser.add_argument("filepath", type=str, help="Path to the JSON log file.")
    load_parser.set_defaults(func=handle_load)

    # --- Stats command ---
    stats_parser = subparsers.add_parser("stats", help="Display descriptive statistics for a field in loaded logs.")
    stats_parser.add_argument("field_path", type=str,
                              help="Field path within log entry's 'data' (e.g., 'reward' or 'metrics.score'). Use dot notation for nested.")
    stats_parser.add_argument("--source", type=str, help="Filter by log source.")
    stats_parser.add_argument("--event_type", type=str, help="Filter by event type.")
    stats_parser.add_argument("--start_time", type=str, help=f"Filter logs from this ISO timestamp ({DEFAULT_TIMESTAMP_FORMAT}).")
    stats_parser.add_argument("--end_time", type=str, help=f"Filter logs up to this ISO timestamp ({DEFAULT_TIMESTAMP_FORMAT}).")
    stats_parser.set_defaults(func=handle_stats)

    # --- Plot command ---
    plot_parser = subparsers.add_parser("plot", help="Generate a time-series plot for a field in loaded logs.")
    plot_parser.add_argument("field_path", type=str,
                             help="Field path within log entry's 'data' for Y-axis. Use dot notation for nested.")
    plot_parser.add_argument("--output", type=str, help="Path to save the plot image (e.g., plot.png).")
    plot_parser.add_argument("--title", type=str, help="Title for the plot.")
    plot_parser.add_argument("--ylabel", type=str, help="Label for the Y-axis.")
    plot_parser.add_argument("--source", type=str, help="Filter by log source.")
    plot_parser.add_argument("--event_type", type=str, help="Filter by event type.")
    plot_parser.add_argument("--start_time", type=str, help=f"Filter logs from this ISO timestamp ({DEFAULT_TIMESTAMP_FORMAT}).")
    plot_parser.add_argument("--end_time", type=str, help=f"Filter logs up to this ISO timestamp ({DEFAULT_TIMESTAMP_FORMAT}).")
    plot_parser.add_argument("--no_show", action="store_true", help="Do not display the plot interactively (e.g., when saving to file).")
    plot_parser.set_defaults(func=handle_plot)

    # --- View Goals command ---
    view_goals_parser = subparsers.add_parser("view_goals", help="Display goals from a specific log entry (if applicable).")
    view_goals_parser.add_argument("log_index", type=int, help="Index of the log entry to inspect from loaded logs.")
    view_goals_parser.set_defaults(func=handle_view_goals)

    # --- View WM command ---
    view_wm_parser = subparsers.add_parser("view_wm", help="Display working memory state from a specific log entry (if applicable).")
    view_wm_parser.add_argument("log_index", type=int, help="Index of the log entry to inspect from loaded logs.")
    view_wm_parser.set_defaults(func=handle_view_wm)

    # --- List Logs command ---
    list_logs_parser = subparsers.add_parser("list_logs", help="List summaries of loaded log entries.")
    list_logs_parser.add_argument("--limit", type=int, default=10, help="Maximum number of log entries to display (default: 10).")
    list_logs_parser.set_defaults(func=handle_list_logs)

    # --- Sequences command ---
    seq_parser = subparsers.add_parser("sequences", aliases=['seq'],
                                       help="Find and display event sequences based on a definition.")
    seq_parser.add_argument("definition_str", type=str,
                              help="Sequence definition. Either a JSON string "
                                   "'[{\"event_type\":\"TypeA\"}, {\"event_type\":\"TypeB\",\"source\":\"SrcB\"}]' "
                                   "or a simple comma-separated list of event_types 'TypeA,TypeB,TypeC'.")
    seq_parser.add_argument("--max_time", type=float, default=None,
                              help="Maximum time in seconds between consecutive steps in a sequence.")
    seq_parser.add_argument("--max_logs", type=int, default=None,
                              help="Maximum number of intervening logs between steps in a sequence.")
    seq_parser.add_argument("--allow_repeats", action="store_true",
                              help="Allow repeats in definition matching (see API docs for nuances).")
    seq_parser.set_defaults(func=handle_sequences)

    if len(sys.argv) <= 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    if args.command != "load":
        if pia_api_instance is None:
             pass

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help(sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    # To run this CLI:
    # Create a dummy sample_logs.json first (e.g., using the example from PiaAVTAPI in api.py)
    # python PiaAGI_Hub/PiaAVT/cli.py load ./sample_logs.json
    # python PiaAGI_Hub/PiaAVT/cli.py stats data.reward --event_type Action
    # python PiaAGI_Hub/PiaAVT/cli.py plot data.valence --source PiaCML.Emotion --output emotion_plot.png --no_show
    # python PiaAGI_Hub/PiaAVT/cli.py list_logs --limit 5
    # python PiaAGI_Hub/PiaAVT/cli.py view_goals 8
    # python PiaAGI_Hub/PiaAVT/cli.py sequences "Write,Action" --max_logs 0
    # python PiaAGI_Hub/PiaAVT/cli.py sequences '[{"event_type":"Write"},{"event_type":"Action","source":"PiaSE.Agent0"}]' --max_logs 0
    main()
```
