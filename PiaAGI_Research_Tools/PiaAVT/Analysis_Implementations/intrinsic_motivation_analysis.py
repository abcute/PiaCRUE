# intrinsic_motivation_analysis.py

import json
import os # Keep os for path operations if needed
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

def analyze_intrinsic_motivation(parsed_logs: list, target_agent_id: str = None, target_simulation_run_id: str = None) -> dict:
    """
    Analyzes intrinsic motivation dynamics from parsed log data. (Conceptual Outline)
    Filters for GOAL_CREATED events of intrinsic types.
    Conceptually outlines tracing triggers and impacts of these goals.
    """
    # -------------------------------------------------------------------------
    # 1. Pre-filtering and Data Preparation
    # -------------------------------------------------------------------------
    logs_to_process = list(parsed_logs) # Work on a copy

    # Filter by simulation_run_id if provided
    if target_simulation_run_id:
        logs_to_process = [log for log in logs_to_process if log.get("simulation_run_id") == target_simulation_run_id]

    # Filter by agent_id if provided (for GOAL_CREATED events, agent_id is who created the goal)
    # For other events (triggers, impacts), agent_id might refer to the acting agent.
    if target_agent_id:
        # This initial filter might be too broad for triggers/impacts not directly on target_agent,
        # but helps scope down GOAL_CREATED events. Refined filtering might be needed later.
        agent_specific_logs = [log for log in logs_to_process if log.get("agent_id") == target_agent_id]
        # However, triggers and impacts might involve other agents or be system events.
        # So, for now, we will primarily use target_agent_id for filtering GOAL_CREATED.
    else:
        agent_specific_logs = logs_to_process


    intrinsic_goal_events = sorted(
        [
            log for log in (agent_specific_logs if target_agent_id else logs_to_process)
            if log.get("event_type") == "GOAL_CREATED"
            and log.get("event_data", {}).get("type", "").startswith("INTRINSIC_")
        ],
        key=lambda x: x.get("timestamp")
    )

    # Store all logs in a way that's easy to search by event_id or timestamp for trigger/impact tracing
    # This is a simplified approach; a more robust system might use a database or indexed structure.
    events_by_id = {log.get("event_id"): log for log in logs_to_process if log.get("event_id")}
    # Sort all logs by timestamp for temporal proximity searches
    all_logs_sorted_by_time = sorted(logs_to_process, key=lambda x: x.get("timestamp", 0.0) or 0.0)


    analyzed_goals = []
    # Conceptual summary statistics
    total_intrinsic_goals = 0
    common_trigger_types = defaultdict(int)
    common_impact_types = defaultdict(int)

    # -------------------------------------------------------------------------
    # 2. Iterating Through Intrinsic Goals and Conceptual Analysis
    # -------------------------------------------------------------------------
    for goal_event in intrinsic_goal_events:
        goal_data = goal_event.get("event_data", {})
        goal_id = goal_data.get("goal_id")
        goal_type = goal_data.get("type")
        creation_timestamp = goal_event.get("timestamp")
        source_trigger_event_id = goal_data.get("source_trigger_event_id")

        if not goal_id or not goal_type:
            continue

        total_intrinsic_goals += 1
        current_goal_analysis = {
            "goal_id": goal_id,
            "goal_type": goal_type,
            "creation_timestamp": creation_timestamp,
            "potential_triggers": [],
            "observed_impacts": [],
            "trigger_characteristics_summary": "Conceptual: Details about triggers would be summarized here.",
            "impact_summary": "Conceptual: Details about impacts would be summarized here."
        }

        # --- Conceptual: Trace back to potential triggering events ---
        # This section would contain complex logic.
        #
        # Method 1: Using `source_trigger_event_id`
        if source_trigger_event_id and source_trigger_event_id in events_by_id:
            trigger_event = events_by_id[source_trigger_event_id]
            current_goal_analysis["potential_triggers"].append({
                "event_type": trigger_event.get("event_type"),
                "timestamp": trigger_event.get("timestamp"),
                "details": {"event_id": trigger_event.get("event_id"), "data": trigger_event.get("event_data")} # Simplified
            })
            common_trigger_types[trigger_event.get("event_type")] += 1
            # Conceptual: Further analyze `trigger_event.get("event_data")` for novelty scores, salience, etc.
            # e.g., if trigger_event.get("event_type") == "PERCEPTION_INPUT_PROCESSED":
            #   novelty = trigger_event.get("event_data", {}).get("novelty_score", 0)
            #   current_goal_analysis["trigger_characteristics_summary"] = f"Triggered by perception (novelty: {novelty})"

        # Method 2: Temporal proximity (e.g., events shortly before goal creation)
        # For example, look for PERCEPTION_INPUT_PROCESSED, MOTIVATIONAL_SALIENCE_CALCULATED,
        # or AGENT_INTERNAL_STATE_UPDATED for the same agent_id just before `creation_timestamp`.
        # This requires careful windowing and heuristics.
        #
        # pseudo-code for temporal proximity:
        # relevant_prior_events = []
        # for log in reversed(all_logs_sorted_by_time): # Search backwards from goal creation
        #   if log.get("timestamp") < creation_timestamp:
        #     if log.get("timestamp") >= creation_timestamp - LOOKBACK_WINDOW_SECONDS:
        #       if log.get("agent_id") == goal_event.get("agent_id"): # Or if system event
        #         if log.get("event_type") in ["PERCEPTION_INPUT_PROCESSED", "MOTIVATIONAL_SALIENCE_CALCULATED"]:
        #           # Add to potential_triggers, avoid duplicates if already found by ID
        #           pass # Add logic here
        #     else:
        #       break # Stop searching beyond the lookback window
        # current_goal_analysis["potential_triggers"].extend(conceptual_temporal_triggers)


        # --- Conceptual: Identify subsequent events indicating impact ---
        # This section would also contain complex logic.
        # Look for events after `creation_timestamp` that are related to this `goal_id` or agent.
        #
        # Examples:
        # - AGENT_ACTION_EXECUTED_IN_ENV: e.g., "explore", "interact_novel_object", "practice_skill"
        #   (requires mapping actions to intrinsic motivations)
        # - INTRINSIC_REWARD_GENERATED: with a matching `related_goal_id` or by temporal/agent correlation.
        # - GOAL_STATUS_UPDATE: for this `goal_id` showing progress or completion.
        #
        # pseudo-code for impact search:
        # relevant_impact_events = []
        # for log in all_logs_sorted_by_time:
        #   if log.get("timestamp") > creation_timestamp:
        #     if log.get("timestamp") <= creation_timestamp + LOOKFORWARD_WINDOW_SECONDS:
        #       # Filter by agent_id, or if related_goal_id matches, or by action type
        #       if log.get("event_type") == "AGENT_ACTION_EXECUTED_IN_ENV":
        #          action_type = log.get("event_data",{}).get("action_name")
        #          # if action_type in ["explore_area", "practice_X"] and log.get("agent_id") == goal_event.get("agent_id"):
        #          #    add to observed_impacts
        #          #    common_impact_types[log.get("event_type")] += 1
        #          pass
        #       elif log.get("event_type") == "INTRINSIC_REWARD_GENERATED":
        #          # if log.get("event_data",{}).get("related_goal_id") == goal_id:
        #          #    add to observed_impacts
        #          #    common_impact_types[log.get("event_type")] += 1
        #          pass
        #     else:
        #       # Potentially stop searching if too far in the future, depending on strategy
        #       pass # Or break if logs are strictly ordered and we are past window for all goals
        # current_goal_analysis["observed_impacts"].extend(conceptual_impacts)

        # For the purpose of this conceptual script, we'll add placeholder data if empty
        if not current_goal_analysis["potential_triggers"]:
             current_goal_analysis["potential_triggers"].append({"event_type": "CONCEPTUAL_TRIGGER", "timestamp": None, "details": "Placeholder for complex trigger analysis"})
             common_trigger_types["CONCEPTUAL_TRIGGER"] +=1
        if not current_goal_analysis["observed_impacts"]:
            current_goal_analysis["observed_impacts"].append({"event_type": "CONCEPTUAL_IMPACT", "timestamp": None, "action_type": "conceptual_action"})
            common_impact_types["CONCEPTUAL_IMPACT"] +=1


        analyzed_goals.append(current_goal_analysis)

    # -------------------------------------------------------------------------
    # 3. Finalizing Report Structure
    # -------------------------------------------------------------------------
    report_agent_id_header = target_agent_id if target_agent_id else "ALL_AGENTS"
    report_sim_id_header = target_simulation_run_id
    if not target_simulation_run_id:
        # Try to infer if all logs/goals belong to a single simulation
        sim_ids_in_goals = set(ig["creation_timestamp"] and ig_event.get("simulation_run_id") for ig_event in intrinsic_goal_events) # Re-extract from original events
        if len(sim_ids_in_goals) == 1:
            report_sim_id_header = sim_ids_in_goals.pop() if sim_ids_in_goals else "ALL_SIMULATIONS (None found)"
        elif not sim_ids_in_goals:
             report_sim_id_header = "ALL_SIMULATIONS (No intrinsic goals found to determine sim_id)"
        else:
            report_sim_id_header = "ALL_SIMULATIONS (Multiple)"


    return {
        "agent_id": report_agent_id_header,
        "simulation_run_id": report_sim_id_header,
        "intrinsic_goals_analyzed": analyzed_goals,
        "summary_stats": {
            "total_intrinsic_goals": total_intrinsic_goals,
            "common_trigger_types": dict(common_trigger_types), # Convert defaultdict to dict for output
            "common_impact_types": dict(common_impact_types)
        }
    }

def generate_summary_report_intrinsic_motivation(analysis_results: dict):
    """
    Prints a conceptual textual summary of the intrinsic motivation analysis.
    """
    print("\n--- Intrinsic Motivation Analysis Report (Conceptual) ---")
    agent_id = analysis_results.get("agent_id", "N/A")
    sim_id = analysis_results.get("simulation_run_id", "N/A")
    
    print(f"Scope: Agent ID: {agent_id}, Simulation Run ID: {sim_id}")

    stats = analysis_results["summary_stats"]
    print("\nOverall Summary:")
    print(f"  Total Intrinsic Goals Analyzed: {stats['total_intrinsic_goals']}")
    if stats['total_intrinsic_goals'] > 0:
        print(f"  Common Trigger Event Types: {stats['common_trigger_types']}")
        print(f"  Common Impact Event Types: {stats['common_impact_types']}")

    print("\nDetails of Intrinsic Goals (first 5):")
    if not analysis_results["intrinsic_goals_analyzed"]:
        print("  No intrinsic goals found matching criteria.")
    else:
        for i, goal_analysis in enumerate(analysis_results["intrinsic_goals_analyzed"][:5]):
            print(f"\n  Goal {i+1}: {goal_analysis['goal_id']} ({goal_analysis['goal_type']})")
            print(f"    Created: {goal_analysis['creation_timestamp']}")
            print(f"    Potential Triggers ({len(goal_analysis['potential_triggers'])}):")
            for trigger in goal_analysis['potential_triggers'][:2]: # Print first 2 triggers
                print(f"      - Type: {trigger['event_type']}, Timestamp: {trigger['timestamp']}, Details: {str(trigger['details'])[:100]}...")
            if len(goal_analysis['potential_triggers']) > 2:
                print("        ... and more triggers.")
            print(f"    Trigger Characteristics Summary: {goal_analysis['trigger_characteristics_summary']}")
            
            print(f"    Observed Impacts ({len(goal_analysis['observed_impacts'])}):")
            for impact in goal_analysis['observed_impacts'][:2]: # Print first 2 impacts
                 print(f"      - Type: {impact['event_type']}, Timestamp: {impact['timestamp']}, Details: {str(impact.get('action_type') or impact.get('reward_type'))[:100]}...")
            if len(goal_analysis['observed_impacts']) > 2:
                print("        ... and more impacts.")
            print(f"    Impact Summary: {goal_analysis['impact_summary']}")
            
        if len(analysis_results["intrinsic_goals_analyzed"]) > 5:
            print(f"\n  ... and {len(analysis_results['intrinsic_goals_analyzed']) - 5} more intrinsic goals.")
    print("--- End of Report ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyzes intrinsic motivation dynamics from PiaAVT JSONL log files (Conceptual).",
        epilog="Example: python intrinsic_motivation_analysis.py /path/to/your/logfile.jsonl --agent_id agent_X --sim_id sim_intrinsic_01"
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

    print(f"Starting Intrinsic Motivation Analysis for log file: {args.log_file}...")
    if args.agent_id:
        print(f"Filtering for Agent ID: {args.agent_id}")
    if args.sim_id:
        print(f"Filtering for Simulation Run ID: {args.sim_id}")

    parsed_logs = load_and_parse_log_data_jsonl(args.log_file)

    if parsed_logs:
        print(f"\nSuccessfully parsed {len(parsed_logs)} log entries from {args.log_file}.")
        
        analysis_results = analyze_intrinsic_motivation(
            parsed_logs,
            target_agent_id=args.agent_id,
            target_simulation_run_id=args.sim_id
        )
        
        generate_summary_report_intrinsic_motivation(analysis_results)

        # Example of calling with specific parameters for demonstration, if desired
        # print("\n--- Analyzing intrinsic motivation (all agents, specific sim_id from args if provided, else all) ---")
        # all_intrinsic_analysis_specific_sim = analyze_intrinsic_motivation(parsed_logs, target_simulation_run_id=args.sim_id)
        # generate_summary_report_intrinsic_motivation(all_intrinsic_analysis_specific_sim)

    else:
        print(f"Log parsing returned no data from {args.log_file}. Ensure the file exists, is not empty, and contains valid JSONL.")
