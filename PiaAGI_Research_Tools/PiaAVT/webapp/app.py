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

    uploaded_file = st.file_uploader("Upload Agent Log File (JSON)", type=["json"])

    if uploaded_file is not None:
        if uploaded_file.name != st.session_state.uploaded_file_name_cache:
            st.session_state.error_message = None
            st.session_state.pia_api = PiaAVTAPI()

            temp_log_path = os.path.join(".", uploaded_file.name)
            try:
                with open(temp_log_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                if st.session_state.pia_api.load_logs_from_json(temp_log_path):
                    st.session_state.log_file_name = uploaded_file.name
                    st.session_state.uploaded_file_name_cache = uploaded_file.name
                    st.success(f"Loaded {st.session_state.pia_api.get_log_count()} logs from '{uploaded_file.name}'.")
                    # Reset filters on new file upload
                    st.session_state.filter_source = []
                    st.session_state.filter_event_type = []
                    st.session_state.filter_start_time = ""
                    st.session_state.filter_end_time = ""
                else:
                    st.session_state.log_file_name = None
                    st.session_state.uploaded_file_name_cache = None
                    st.error(f"Failed to load logs from '{uploaded_file.name}'. Check console for API errors.")
            except Exception as e:
                st.session_state.log_file_name = None
                st.session_state.uploaded_file_name_cache = None
                st.error(f"Error saving or loading uploaded file: {e}")
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

    # For API methods expecting a single Optional string, we'll pass the first selected one or None.
    # This is a simplification for the PoC. Proper handling of multi-selection might involve
    # iterating API calls or modifying the API to accept lists for these filters.
    g_source_single = g_source_filter_list[0] if len(g_source_filter_list) == 1 else None
    g_event_type_single = g_event_type_filter_list[0] if len(g_event_type_filter_list) == 1 else None
    if len(g_source_filter_list) > 1:
        st.sidebar.warning("Multiple sources selected. Stats/plot will use data from ALL selected sources (if API supports) or first/none if not.")
    if len(g_event_type_filter_list) > 1:
        st.sidebar.warning("Multiple event types selected. Stats/plot will use data from ALL selected types (if API supports) or first/none if not.")


    tab_titles = ["📊 Overview & Stats", "📈 Time Series Plot", " S─S Event Sequences", "📜 Raw Logs"] # Added new tab & updated Raw Logs
    tabs = st.tabs(tab_titles)

    with tabs[0]:
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
                    source=g_source_single,
                    event_type=g_event_type_single,
                    start_time_str=st.session_state.filter_start_time or None,
                    end_time_str=st.session_state.filter_end_time or None
                )
                if stats:
                    st.write(f"**Statistics for '{stats_field_path}' (with global filters applied):**")
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
                    source=g_source_single,
                    event_type=g_event_type_single,
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

    with tabs[2]: # Log Listing
        st.header("Log Listing")
        # TODO: Implement log listing with pagination and full view of an entry
        st.write("Full log listing functionality to be implemented.")
        st.write("For now, use CLI: `python cli.py list_logs --limit N`")
        if st.button("Show first 10 logs (raw JSON)", key="show_raw_logs"):
            logs_to_show = st.session_state.pia_api.get_all_logs()[:10]
            st.json(logs_to_show)


    with tabs[3]: # Event Sequences
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

    with tabs[3]: # Raw Logs Tab (was Log Listing)
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
