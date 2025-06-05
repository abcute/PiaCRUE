# PiaAGI_Hub/PiaAVT/webapp/app.py
import streamlit as st
import sys
import os
import pandas as pd # For st.dataframe if used for stats
import json # For parsing sequence definition if added later

# Adjust Python path to import PiaAVTAPI
# This assumes the webapp/app.py is run from the PiaAGI_Hub/PiaAVT/ directory
# or that PiaAGI_Hub is in PYTHONPATH.
try:
    from PiaAVT.api import PiaAVTAPI
    from PiaAVT.core.logging_system import DEFAULT_TIMESTAMP_FORMAT # For parsing help
except ImportError:
    # Fallback for development: if webapp/ is current directory
    # or if PiaAVT/ is current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pia_avt_dir = os.path.dirname(current_dir) # Should be PiaAVT if app.py is in webapp/
    pia_agi_hub_dir = os.path.dirname(pia_avt_dir) # Should be PiaAGI_Hub

    if os.path.basename(current_dir) == "webapp" and os.path.basename(pia_avt_dir) == "PiaAVT":
         # If running from PiaAGI_Hub/PiaAVT/webapp/
        sys.path.insert(0, pia_agi_hub_dir)
        from PiaAVT.api import PiaAVTAPI
        from PiaAVT.core.logging_system import DEFAULT_TIMESTAMP_FORMAT
    elif os.path.basename(current_dir) == "PiaAVT":
        # If running from PiaAGI_Hub/PiaAVT/ (e.g. streamlit run webapp/app.py)
        sys.path.insert(0, pia_agi_hub_dir)
        from PiaAVT.api import PiaAVTAPI
        from PiaAVT.core.logging_system import DEFAULT_TIMESTAMP_FORMAT
    else:
        # If imports still fail, user needs to ensure PYTHONPATH is set,
        # or run streamlit from PiaAGI_Hub/PiaAVT directory.
        # Attempt a direct import that might work if PiaAVT is directly in PYTHONPATH
        # This is a last resort for when the script is run from an unexpected CWD.
        try:
            from api import PiaAVTAPI # For running from PiaAVT as CWD or PiaAVT in PYTHONPATH
            from core.logging_system import DEFAULT_TIMESTAMP_FORMAT
            # If this works, it implies PiaAVT directory itself is in PYTHONPATH or is CWD.
        except ImportError as e_final:
            st.error(f"PiaAVTAPI Import Error: Could not resolve imports. CWD: {os.getcwd()}, Script Dir: {current_dir}. Final error: {e_final}. Ensure PiaAGI_Hub is in PYTHONPATH or run from PiaAVT parent directory.")
            st.stop() # Stop execution if API cannot be loaded


# Initialize PiaAVTAPI in Streamlit's session state to persist across interactions
if 'pia_api' not in st.session_state:
    st.session_state.pia_api = PiaAVTAPI()
if 'log_file_name' not in st.session_state:
    st.session_state.log_file_name = None
if 'error_message' not in st.session_state:
    st.session_state.error_message = None
if 'uploaded_file_name_cache' not in st.session_state: # Cache for uploaded file name
    st.session_state.uploaded_file_name_cache = None


st.set_page_config(page_title="PiaAVT Dashboard", layout="wide")
st.title("PiaAVT - Agent Analysis Dashboard")

# --- Sidebar for Configuration ---
with st.sidebar:
    st.header("Configuration")

    uploaded_file = st.file_uploader("Upload Agent Log File (JSONL - one JSON object per line)", type=["jsonl", "json"])

    if uploaded_file is not None:
        if uploaded_file.name != st.session_state.uploaded_file_name_cache:
            st.session_state.error_message = None
            st.session_state.pia_api = PiaAVTAPI()

            temp_log_path = os.path.join(".", uploaded_file.name) # Consider a more robust temp file handling
            try:
                with open(temp_log_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                if st.session_state.pia_api.load_logs_from_jsonl(temp_log_path): # MODIFIED
                    st.session_state.log_file_name = uploaded_file.name
                    st.session_state.uploaded_file_name_cache = uploaded_file.name
                    if st.session_state.pia_api.get_log_count() > 0:
                        st.success(f"Loaded {st.session_state.pia_api.get_log_count()} logs from JSONL file '{uploaded_file.name}'.")
                    else:
                        st.warning(f"JSONL file '{uploaded_file.name}' processed, but no valid log entries were loaded. File might be empty or all lines had errors.")
                    # Reset filters on new file upload
                    st.session_state.filter_source = []
                    st.session_state.filter_event_type = []
                    st.session_state.filter_start_time = ""
                    st.session_state.filter_end_time = ""
                    st.session_state.filter_simulation_id = "" # Initialize new filter
                else:
                    st.session_state.log_file_name = None
                    st.session_state.uploaded_file_name_cache = None
                    st.error(f"Failed to load JSONL logs from '{uploaded_file.name}'. Ensure it's valid JSONL. Check console for API errors.") # MODIFIED
            except Exception as e:
                st.session_state.log_file_name = None
                st.session_state.uploaded_file_name_cache = None
                st.error(f"Error saving or loading uploaded JSONL file: {e}") # MODIFIED
            finally:
                if os.path.exists(temp_log_path):
                    os.remove(temp_log_path)
        elif not st.session_state.log_file_name and uploaded_file.name == st.session_state.uploaded_file_name_cache :
             st.warning(f"Previously failed to load {uploaded_file.name}. Try a different file or check logs.")


    if st.session_state.log_file_name:
        st.markdown("---")
        st.subheader("Global Filters")
        if 'filter_source' not in st.session_state: st.session_state.filter_source = []
        if 'filter_event_type' not in st.session_state: st.session_state.filter_event_type = []
        if 'filter_start_time' not in st.session_state: st.session_state.filter_start_time = ""
        if 'filter_end_time' not in st.session_state: st.session_state.filter_end_time = ""
        if 'filter_simulation_id' not in st.session_state: st.session_state.filter_simulation_id = "" # Add new filter

        analyzer = st.session_state.pia_api.get_analyzer()
        if analyzer:
            try:
                all_logs_for_filters = st.session_state.pia_api.get_all_logs()
                unique_sources = sorted(list(set(log.get('source', 'N/A') for log in all_logs_for_filters)))
                unique_event_types = sorted(list(set(log.get('event_type', 'N/A') for log in all_logs_for_filters)))

                st.session_state.filter_source = st.multiselect("Filter by Source(s)", options=unique_sources, default=st.session_state.filter_source)
                st.session_state.filter_event_type = st.multiselect("Filter by Event Type(s)", options=unique_event_types, default=st.session_state.filter_event_type)
            except Exception as e:
                st.error(f"Error populating filters: {e}")
        
        st.session_state.filter_simulation_id = st.text_input("Filter by Simulation ID", value=st.session_state.filter_simulation_id, placeholder="e.g., sim_run_001")
        st.session_state.filter_start_time = st.text_input(f"Filter by Start Timestamp ({DEFAULT_TIMESTAMP_FORMAT})", value=st.session_state.filter_start_time, placeholder="YYYY-MM-DDTHH:MM:SS.sssZ")
        st.session_state.filter_end_time = st.text_input(f"Filter by End Timestamp ({DEFAULT_TIMESTAMP_FORMAT})", value=st.session_state.filter_end_time, placeholder="YYYY-MM-DDTHH:MM:SS.sssZ")
    else:
        st.info("Upload a log file to enable filters and analysis.")

# --- Main Content Area ---
if st.session_state.log_file_name:
    if st.session_state.error_message:
        st.error(st.session_state.error_message)

    g_source_filter_list = st.session_state.filter_source if st.session_state.filter_source else []
    g_event_type_filter_list = st.session_state.filter_event_type if st.session_state.filter_event_type else []
    g_simulation_id_filter = st.session_state.filter_simulation_id.strip() if st.session_state.filter_simulation_id else None


    # For API methods expecting a single Optional string, we'll pass the first selected one or None.
    # This is a simplification for the PoC. Proper handling of multi-selection might involve
    # iterating API calls or modifying the API to accept lists for these filters.
    # For agent_id, we'll use the 'source' filter, assuming agent IDs might appear there.
    # This might need refinement based on actual log structure.
    g_agent_id_single_filter = g_source_filter_list[0] if len(g_source_filter_list) == 1 else None
    g_event_type_single_filter = g_event_type_filter_list[0] if len(g_event_type_filter_list) == 1 else None
    
    if len(g_source_filter_list) > 1:
        st.sidebar.warning("Multiple sources selected. For analyses requiring a single agent ID, the first selected source will be used if applicable. Other features might use all selected sources.")
    if len(g_event_type_filter_list) > 1:
        st.sidebar.warning("Multiple event types selected. Specific stats/plots might use the first selected type or all, depending on the feature.")


    tab_titles = [
        "📊 Overview & Stats", "📈 Time Series Plot", " S─S Event Sequences", 
        "🎯 Goal Dynamics", "😊 Emotional Trajectory", "💡 Intrinsic Motivation", "🚀 Task Performance",
        "📜 Raw Logs"
    ]
    tabs = st.tabs(tab_titles)

    with tabs[0]: # Overview & Stats
        st.header("Log Overview & Descriptive Statistics")
        st.write(f"**Loaded File:** {st.session_state.log_file_name}")
        st.write(f"**Total Entries (considering global filters if applicable to source/event counts):** {st.session_state.pia_api.get_log_count()}") # This count is pre-filter.

        analyzer = st.session_state.pia_api.get_analyzer()
        if analyzer:
            try:
                # For overview counts, it's better to apply all filters
                # The BasicAnalyzer.filter_logs needs to be called or similar logic.
                # For simplicity, the count_unique_values in BasicAnalyzer applies filters.
                # However, the multiselect needs careful handling.
                # Let's show unfiltered counts first, then filtered example for specific stats.

                all_logs_unfiltered = st.session_state.pia_api.get_all_logs()
                st.write(f"**Total Unfiltered Entries:** {len(all_logs_unfiltered)}")

                sources_count_unfiltered = analyzer.count_unique_values("source")
                st.write("**Unique Sources (unfiltered):**")
                st.json(dict(sources_count_unfiltered))

                events_count_unfiltered = analyzer.count_unique_values("event_type")
                st.write("**Unique Event Types (unfiltered):**")
                st.json(dict(events_count_unfiltered))
                st.caption("Note: Counts above are for the entire dataset. Filters apply to specific stats/plots below.")

            except Exception as e:
                st.error(f"Error displaying overview stats: {e}")

        st.subheader("Calculate Descriptive Statistics")
        stats_field_path = st.text_input("Field Path for Stats (e.g., data.reward or data.metrics.score)", key="stats_field")
        if st.button("Calculate Statistics", key="calc_stats_btn"):
            if stats_field_path:
                # The API's get_stats_for_field expects single source/event_type if provided
                stats = st.session_state.pia_api.get_stats_for_field(
                    data_field_path=stats_field_path,
                    source=g_agent_id_single_filter, # Using source filter as potential agent_id filter
                    event_type=g_event_type_single_filter,
                    start_time_str=st.session_state.filter_start_time or None,
                    end_time_str=st.session_state.filter_end_time or None
                )
                if stats:
                    st.write(f"**Statistics for '{stats_field_path}' (with global filters applied where applicable):**")
                    st.json(stats)
                else:
                    st.warning(f"No statistics found or error for field '{stats_field_path}' with current filters.")
            else:
                st.warning("Please enter a field path for statistics.")

    with tabs[1]:
        st.header("Time Series Plot")
        plot_field_path = st.text_input("Field Path to Plot (e.g., data.value or data.metrics.value)", key="plot_field")
        plot_title = st.text_input("Plot Title (Optional)", key="plot_title_input", placeholder="Defaults to field path")
        plot_ylabel = st.text_input("Y-Axis Label (Optional)", key="plot_ylabel_input", placeholder="Defaults to field path")

        if st.button("Generate Plot", key="gen_plot_btn"):
            if plot_field_path:
                import matplotlib.pyplot as plt

                ts_data = st.session_state.pia_api.get_timeseries_for_field(
                    plot_field_path,
                    source=g_agent_id_single_filter, # Using source filter as potential agent_id filter
                    event_type=g_event_type_single_filter,
                    start_time_str=st.session_state.filter_start_time or None,
                    end_time_str=st.session_state.filter_end_time or None
                )
                if ts_data:
                    fig, ax = plt.subplots(figsize=(10, 5))
                    timestamps = [item[0] for item in ts_data]
                    values = [item[1] for item in ts_data]

                    line, = ax.plot(timestamps, values, marker='o', linestyle='-') # Save line for mplcursors
                    ax.set_title(plot_title or f"Time Series for '{plot_field_path}'")
                    ax.set_xlabel("Time")
                    ax.set_ylabel(plot_ylabel or plot_field_path)
                    fig.autofmt_xdate()
                    ax.grid(True)

                    try:
                        plotter_instance = st.session_state.pia_api.timeseries_plotter
                        if plotter_instance._mplcursors_available:
                            import mplcursors
                            from matplotlib.dates import num2date
                            cursor = mplcursors.cursor(line, hover=True)
                            @cursor.connect("add")
                            def on_add(sel):
                                point_timestamp = num2date(sel.target[0])
                                point_value = sel.target[1]
                                artist_label = sel.artist.get_label()
                                label_prefix = f"{artist_label}\n" if artist_label and not artist_label.startswith('_') else ""
                                value_str = f"{point_value:.2f}" if isinstance(point_value, float) else str(point_value)
                                sel.annotation.set_text(
                                    f"{label_prefix}"
                                    f"Time: {point_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n"
                                    f"Value: {value_str}"
                                )
                                sel.annotation.get_bbox_patch().set(alpha=0.8)
                            if not line.get_label() or line.get_label().startswith('_'):
                                line.set_label(plot_ylabel or plot_field_path)
                    except Exception as e_mpl:
                        st.caption(f"Note: Interactive tooltips via mplcursors might not be available. Error: {e_mpl}")

                    st.pyplot(fig)
                    plt.close(fig)
                else:
                    st.warning(f"No time-series data found for '{plot_field_path}' with current filters.")
            else:
                st.warning("Please enter a field path to plot.")

    with tabs[2]: # Event Sequences
        st.header("Event Sequence Analysis")

        # Initialize session state for sequence inputs if not present
        if 'seq_def_input' not in st.session_state:
            st.session_state.seq_def_input = '[{"event_type":"Query"}, {"event_type":"Thinking"}, {"event_type":"Response"}]'
        if 'seq_max_time' not in st.session_state:
            st.session_state.seq_max_time = "" # Store as string, convert to float later
        if 'seq_max_logs' not in st.session_state:
            st.session_state.seq_max_logs = "" # Store as string, convert to int later
        if 'seq_allow_repeats' not in st.session_state:
            st.session_state.seq_allow_repeats = False

        st.session_state.seq_def_input = st.text_area(
            "Sequence Definition (JSON or comma-separated event_types)",
            value=st.session_state.seq_def_input,
            height=100,
            help='JSON: [{"event_type":"TypeA", "source":"SrcA"}, ...] or CSV: TypeA,TypeB,TypeC'
        )

        col1, col2 = st.columns(2)
        with col1:
            st.session_state.seq_max_time = st.text_input(
                "Max Time Between Steps (seconds, optional)",
                value=st.session_state.seq_max_time,
                key="seq_max_time_input"
            )
        with col2:
            st.session_state.seq_max_logs = st.text_input(
                "Max Intervening Logs (optional)",
                value=st.session_state.seq_max_logs,
                key="seq_max_logs_input"
            )

        st.session_state.seq_allow_repeats = st.checkbox(
            "Allow Repeats in Definition",
            value=st.session_state.seq_allow_repeats,
            key="seq_allow_repeats_cb"
        )

        if st.button("Find Event Sequences", key="find_seq_btn"):
            if not st.session_state.seq_def_input.strip():
                st.warning("Please provide a sequence definition.")
            else:
                seq_def_str = st.session_state.seq_def_input.strip()
                parsed_sequence_definition = None
                try:
                    # Attempt to parse as JSON list of dicts
                    # import json # Already imported at the top
                    parsed_sequence_definition = json.loads(seq_def_str)
                    if not isinstance(parsed_sequence_definition, list) or \
                       not all(isinstance(step, dict) and "event_type" in step for step in parsed_sequence_definition):
                        # If not list of dicts with event_type, try simple parsing
                        raise ValueError("Definition must be a JSON list of objects, each with at least 'event_type'.")
                except (json.JSONDecodeError, ValueError):
                    # Fallback: Try simple comma-separated event_types (no source)
                    st.caption("Interpreting definition as comma-separated event types (source matching not applied in this mode).")
                    event_types = [et.strip() for et in seq_def_str.split(',')]
                    if not all(event_types):
                        st.error("Invalid format for simple event type sequence. Use comma-separated values e.g., 'EventA,EventB'.")
                        parsed_sequence_definition = None # Explicitly set to None on error
                    else:
                        parsed_sequence_definition = [{"event_type": et} for et in event_types]

                if parsed_sequence_definition: # Only proceed if parsing was successful
                    max_time_val = None
                    if st.session_state.seq_max_time:
                        try:
                            max_time_val = float(st.session_state.seq_max_time)
                        except ValueError:
                            st.error("Invalid input for 'Max Time Between Steps'. Must be a number.")
                            max_time_val = "ERROR" # Sentinel to prevent API call

                    max_logs_val = None
                    if st.session_state.seq_max_logs:
                        try:
                            max_logs_val = int(st.session_state.seq_max_logs)
                            if max_logs_val < 0:
                                st.error("'Max Intervening Logs' must be non-negative.")
                                max_logs_val = "ERROR"
                        except ValueError:
                            st.error("Invalid input for 'Max Intervening Logs'. Must be an integer.")
                            max_logs_val = "ERROR"

                    if max_time_val != "ERROR" and max_logs_val != "ERROR":
                        with st.spinner("Analyzing sequences..."):
                            st.caption("Note: Event sequence analysis currently runs on all loaded logs, global filters are not applied to this feature yet.")

                            formatted_sequences = st.session_state.pia_api.get_formatted_event_sequences(
                                sequence_definition=parsed_sequence_definition,
                                max_time_between_steps_seconds=max_time_val,
                                max_intervening_logs=max_logs_val,
                                allow_repeats_in_definition=st.session_state.seq_allow_repeats
                            )
                        st.text_area("Found Sequences:", value=formatted_sequences, height=300, key="seq_results_text_area")
                else:
                    if not all(et.strip() for et in seq_def_str.split(',')):
                         st.error("Invalid sequence definition provided after attempting parsing.")

    with tabs[3]: # Goal Dynamics
        st.header("Goal Dynamics Analysis")
        if st.button("Run Goal Dynamics Analysis", key="run_goal_dynamics"):
            with st.spinner("Analyzing goal dynamics..."):
                results = st.session_state.pia_api.analyze_goal_dynamics()
                if results:
                    st.success("Goal dynamics analysis complete.")
                    st.subheader("Analysis Results")
                    
                    # Display summary statistics if available (conceptual)
                    # summary = results.get("summary_stats", {})
                    # if summary:
                    # st.write(f"Total Goals Analyzed: {summary.get('total_goals', 'N/A')}")
                    # Add more relevant summary points here based on actual output structure

                    goal_ids = list(results.keys())
                    if not goal_ids:
                        st.info("No goals found in the analysis results.")
                    else:
                        st.write(f"Found {len(goal_ids)} goals.")
                        
                        # Prepare data for potential dataframe or charts
                        goal_data_for_df = []
                        for goal_id, data in results.items():
                            if isinstance(data, dict): # Ensure data is a dictionary
                                goal_data_for_df.append({
                                    "Goal ID": goal_id,
                                    "Description": data.get("description", "N/A"),
                                    "Type": data.get("type", "N/A"),
                                    "Outcome": data.get("outcome", data.get("current_state", "N/A")),
                                    "Creation Time": data.get("creation_time"),
                                    "End Time": data.get("end_time"),
                                    "Duration (s)": data.get("duration_seconds")
                                })
                        if goal_data_for_df:
                            st.dataframe(pd.DataFrame(goal_data_for_df))

                        # Example: Bar chart of goal types
                        try:
                            goal_types = [data.get("type", "UNKNOWN") for data in results.values() if isinstance(data, dict)]
                            if goal_types:
                                type_counts = pd.Series(goal_types).value_counts()
                                st.subheader("Goal Counts by Type")
                                st.bar_chart(type_counts)
                        except Exception as e:
                            st.warning(f"Could not generate goal type chart: {e}")

                    st.subheader("Raw JSON Output (All Goals)")
                    st.json(results) # Display raw JSON for detailed inspection
                else:
                    st.error("Goal dynamics analysis failed or returned no data. Ensure logs are loaded and contain relevant goal events.")

    with tabs[4]: # Emotional Trajectory
        st.header("Emotional Trajectory Analysis")
        st.caption(f"Using global Simulation ID filter: '{g_simulation_id_filter if g_simulation_id_filter else 'None'}' and Agent ID (first selected Source): '{g_agent_id_single_filter if g_agent_id_single_filter else 'None'}'.")
        if st.button("Run Emotional Trajectory Analysis", key="run_emotion_traj"):
            with st.spinner("Analyzing emotional trajectory..."):
                results = st.session_state.pia_api.analyze_emotional_trajectory(
                    target_agent_id=g_agent_id_single_filter,
                    target_simulation_run_id=g_simulation_id_filter
                )
                if results:
                    st.success("Emotional trajectory analysis complete.")
                    st.subheader("Summary Statistics")
                    summary = results.get("summary_stats", {})
                    st.write(f"Agent ID: {results.get('agent_id', 'N/A')}, Simulation Run ID: {results.get('simulation_run_id', 'N/A')}")
                    st.write(f"Number of data points: {summary.get('count', 0)}")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Avg Valence", f"{summary.get('avg_valence', 0):.2f}", f"Std: {summary.get('std_valence', 0):.2f}")
                    col2.metric("Avg Arousal", f"{summary.get('avg_arousal', 0):.2f}", f"Std: {summary.get('std_arousal', 0):.2f}")
                    col3.metric("Avg Dominance", f"{summary.get('avg_dominance', 0):.2f}", f"Std: {summary.get('std_dominance', 0):.2f}")

                    trajectory = results.get("trajectory", [])
                    if trajectory:
                        st.subheader("Trajectory Plot (VAD)")
                        df_trajectory = pd.DataFrame(trajectory)
                        df_trajectory.set_index("timestamp", inplace=True) # Assuming timestamp is suitable for index
                        st.line_chart(df_trajectory[['valence', 'arousal', 'dominance']])
                        
                        st.subheader("Trajectory Data")
                        st.dataframe(df_trajectory)
                    else:
                        st.info("No trajectory data points found in the results.")
                    
                    st.subheader("Raw JSON Output")
                    st.json(results)
                else:
                    st.error("Emotional trajectory analysis failed or returned no data. Ensure logs are loaded and contain EMOTION_STATE_UPDATED events.")

    with tabs[5]: # Intrinsic Motivation
        st.header("Intrinsic Motivation Analysis")
        st.caption(f"Using global Simulation ID filter: '{g_simulation_id_filter if g_simulation_id_filter else 'None'}' and Agent ID (first selected Source): '{g_agent_id_single_filter if g_agent_id_single_filter else 'None'}'.")
        if st.button("Run Intrinsic Motivation Analysis", key="run_intrinsic_motiv"):
            with st.spinner("Analyzing intrinsic motivation..."):
                results = st.session_state.pia_api.analyze_intrinsic_motivation(
                    target_agent_id=g_agent_id_single_filter,
                    target_simulation_run_id=g_simulation_id_filter
                )
                if results:
                    st.success("Intrinsic motivation analysis complete.")
                    st.subheader("Summary Statistics")
                    summary = results.get("summary_stats", {})
                    st.write(f"Agent ID: {results.get('agent_id', 'N/A')}, Simulation Run ID: {results.get('simulation_run_id', 'N/A')}")
                    st.write(f"Total Intrinsic Goals: {summary.get('total_intrinsic_goals', 0)}")
                    if summary.get('common_trigger_types'):
                        st.write("Common Trigger Types:")
                        st.json(summary.get('common_trigger_types'))
                    if summary.get('common_impact_types'):
                        st.write("Common Impact Types:")
                        st.json(summary.get('common_impact_types'))

                    analyzed_goals = results.get("intrinsic_goals_analyzed", [])
                    if analyzed_goals:
                        st.subheader(f"Analyzed Intrinsic Goals ({len(analyzed_goals)})")
                        # Display as a DataFrame
                        df_goals = pd.DataFrame(analyzed_goals)
                        # Select and rename columns for better readability
                        display_columns = {
                            "goal_id": "Goal ID", "goal_type": "Type", 
                            "creation_timestamp": "Created At",
                            "trigger_characteristics_summary": "Trigger Summary",
                            "impact_summary": "Impact Summary"
                        }
                        df_display = df_goals[list(display_columns.keys())].rename(columns=display_columns)
                        st.dataframe(df_display)

                        for goal in analyzed_goals[:5]: # Show details for first 5
                            with st.expander(f"Details for Goal ID: {goal.get('goal_id')}"):
                                st.json(goal)
                    else:
                        st.info("No intrinsic goals found in the analysis results.")
                    
                    st.subheader("Raw JSON Output")
                    st.json(results)
                else:
                    st.error("Intrinsic motivation analysis failed or returned no data. Ensure logs are loaded and contain relevant GOAL_CREATED events of intrinsic types.")

    with tabs[6]: # Task Performance
        st.header("Task Performance Analysis")
        st.caption(f"Using global Simulation ID filter: '{g_simulation_id_filter if g_simulation_id_filter else 'None'}' and Agent ID (first selected Source): '{g_agent_id_single_filter if g_agent_id_single_filter else 'None'}'.")
        if st.button("Run Task Performance Analysis", key="run_task_perf"):
            with st.spinner("Analyzing task performance..."):
                results = st.session_state.pia_api.analyze_task_performance(
                    target_agent_id=g_agent_id_single_filter,
                    target_simulation_run_id=g_simulation_id_filter
                )
                if results:
                    st.success("Task performance analysis complete.")
                    st.subheader("Summary Statistics")
                    summary = results.get("summary_stats", {})
                    st.write(f"Agent ID: {results.get('agent_id', 'N/A')}, Simulation Run ID: {results.get('simulation_run_id', 'N/A')}")

                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total Tasks Analyzed", summary.get('total_tasks_analyzed', 0))
                    col2.metric("Success Rate", f"{summary.get('success_rate', 0):.1%}")
                    col3.metric("Failure Rate", f"{summary.get('failure_rate', 0):.1%}")
                    col4.metric("Avg. Duration (Success)", f"{summary.get('avg_duration_success_seconds', 0):.2f}s" if summary.get('avg_duration_success_seconds') is not None else "N/A")
                    
                    tasks = results.get("tasks", [])
                    if tasks:
                        st.subheader(f"Task Details ({len(tasks)})")
                        df_tasks = pd.DataFrame(tasks)
                        # Select and rename columns
                        task_cols = {
                            "task_id": "Task ID", "status": "Status", "start_time": "Start Time", 
                            "end_time": "End Time", "duration_seconds": "Duration (s)", 
                            "action_count": "Action Count", "involved_agent_ids": "Involved Agents",
                            "simulation_run_id": "Sim ID"
                        }
                        # Filter df_tasks for existing columns before rename
                        existing_cols_in_df = [col for col in task_cols.keys() if col in df_tasks.columns]
                        df_display_tasks = df_tasks[existing_cols_in_df].rename(columns=task_cols)
                        st.dataframe(df_display_tasks)

                        # Example: Bar chart of task statuses
                        try:
                            status_counts = df_tasks["status"].value_counts()
                            st.subheader("Task Counts by Status")
                            st.bar_chart(status_counts)
                        except Exception as e:
                            st.warning(f"Could not generate task status chart: {e}")
                    else:
                        st.info("No task data found in the results.")

                    st.subheader("Raw JSON Output")
                    st.json(results)
                else:
                    st.error("Task performance analysis failed or returned no data. Ensure logs are loaded and contain TASK_STATUS_UPDATE events.")

    with tabs[7]: # Raw Logs Tab
        st.header("Raw Log Data")
        st.write("Displaying a limited number of raw log entries.")
        if st.button("Show first 20 logs (raw JSON)", key="show_raw_logs_detail"):
            logs_to_show = st.session_state.pia_api.get_all_logs()[:20]
            st.json(logs_to_show)
        st.caption("Use the CLI for more comprehensive log listing and filtering if needed.")

else:
    st.info("Upload a JSON log file using the sidebar to begin analysis.")

# For running: streamlit run PiaAGI_Hub/PiaAVT/webapp/app.py
# (Ensure you are in the PiaAGI_Hub/PiaAVT directory or adjust paths if running from PiaAGI_Hub/)
```
