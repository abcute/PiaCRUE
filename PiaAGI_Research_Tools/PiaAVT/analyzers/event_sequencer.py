# PiaAGI_Hub/PiaAVT/analyzers/event_sequencer.py

from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, timedelta

# Assuming LogEntry and DEFAULT_TIMESTAMP_FORMAT are defined consistently
# (e.g., in core.logging_system or a shared types module)
# For now, redefine locally for modularity or assume they will be imported via API
LogEntry = Dict[str, Any]
DEFAULT_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ" # Should match logging_system

# Module-level docstring
"""
Provides functionalities for analyzing sequences of events within PiaAVT log data.
This module helps in identifying and extracting patterns of interactions or
state changes based on the order and timing of specified event types and sources.
"""

class EventSequencer:
    """
    Analyzes log data to find and extract sequences of specified events.

    This can be useful for understanding common interaction patterns, debugging
    agent behavior flows, or verifying expected operational sequences.
    """

    def __init__(self, log_data: List[LogEntry]):
        """
        Initializes the EventSequencer with log data.

        Args:
            log_data (List[LogEntry]): A list of log entries, assumed to be
                                       sorted by timestamp if time-based sequencing is critical.
                                       The `extract_event_sequences` method will re-sort
                                       a copy if necessary for its internal logic.
        """
        if not all(isinstance(entry, dict) for entry in log_data):
            raise ValueError("All items in log_data must be dictionaries (LogEntry).")

        self.log_data = log_data

    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Helper to parse timestamp string to datetime object."""
        try:
            return datetime.strptime(timestamp_str, DEFAULT_TIMESTAMP_FORMAT)
        except (ValueError, TypeError):
            return None

    def _sort_logs_by_timestamp(self, logs: List[LogEntry]) -> List[LogEntry]:
        """Sorts logs by their timestamp field."""
        def get_timestamp_key(entry):
            ts_str = entry.get("timestamp")
            # Attempt to parse, default to a very early time if parsing fails or ts_str is None
            dt_obj = self._parse_timestamp(ts_str) if ts_str else datetime.min
            return dt_obj if dt_obj else datetime.min

        return sorted(logs, key=get_timestamp_key)


    def extract_event_sequences(
        self,
        sequence_definition: List[Dict[str, Optional[str]]],
        max_time_between_steps_seconds: Optional[float] = None,
        max_intervening_logs: Optional[int] = None,
        allow_repeats_in_definition: bool = False # This parameter's full potential might need more complex logic
    ) -> List[List[LogEntry]]:
        """
        Extracts sequences of log entries that match a defined pattern of events.

        Args:
            sequence_definition (List[Dict[str, Optional[str]]]):
                A list of dictionaries, where each dictionary defines a step in the sequence.
                Each dictionary must have 'event_type' and can optionally have 'source'.
                Example: [{"event_type": "UserQuery"},
                          {"event_type": "AgentThinking", "source": "AgentCore"},
                          {"event_type": "AgentResponse"}]
            max_time_between_steps_seconds (Optional[float]):
                The maximum allowed time (in seconds) between the timestamps of
                consecutive events in a matched sequence. If None, time is not checked.
            max_intervening_logs (Optional[int]):
                The maximum number of other log entries that can occur between two
                consecutive events in the defined sequence (based on original log order
                after sorting by time). If None, any number of intervening logs is allowed.
            allow_repeats_in_definition (bool):
                Currently, this parameter has limited effect due to the forward-only scan.
                A more complex state machine would be needed for full interpretation where
                a single log entry could satisfy multiple identical consecutive steps.
                The main effect now is preventing a log from matching if it's identical
                to the previous log *and* the step definition is identical to the previous.

        Returns:
            List[List[LogEntry]]: A list of found sequences. Each sequence is a list
                                  of the LogEntry objects that form it.
        """
        if not sequence_definition:
            return []

        sorted_logs = self._sort_logs_by_timestamp(list(self.log_data)) # Work with a sorted copy

        found_sequences: List[List[LogEntry]] = []
        num_logs = len(sorted_logs)
        seq_def_len = len(sequence_definition)

        for i in range(num_logs):
            current_match_attempt: List[LogEntry] = []
            current_seq_def_idx = 0
            last_matched_log_original_idx = i # Index in sorted_logs for the start of this attempt

            # Try to match the first step
            log_entry_i = sorted_logs[i]
            step_def_i = sequence_definition[current_seq_def_idx]

            match_i = True
            if step_def_i.get("event_type") and log_entry_i.get("event_type") != step_def_i["event_type"]:
                match_i = False
            if step_def_i.get("source") and log_entry_i.get("source") != step_def_i["source"]:
                match_i = False

            if not match_i:
                continue # This log cannot start a sequence

            current_match_attempt.append(log_entry_i)
            current_seq_def_idx += 1

            if current_seq_def_idx == seq_def_len: # Sequence of length 1 found
                found_sequences.append(list(current_match_attempt))
                continue

            # Try to match subsequent steps
            last_event_ts_for_window = self._parse_timestamp(log_entry_i.get("timestamp", ""))

            for j in range(i + 1, num_logs):
                log_entry_j = sorted_logs[j]

                # Constraint: Max intervening logs
                # This counts logs between `last_matched_log_original_idx` and `j`
                if max_intervening_logs is not None and (j - last_matched_log_original_idx - 1) > max_intervening_logs:
                    # This sequence attempt is broken because too many logs came between matched steps
                    break

                # Constraint: Max time between steps
                current_event_ts_for_window = self._parse_timestamp(log_entry_j.get("timestamp", ""))
                if max_time_between_steps_seconds is not None and last_event_ts_for_window and current_event_ts_for_window:
                    if (current_event_ts_for_window - last_event_ts_for_window).total_seconds() > max_time_between_steps_seconds:
                        # This sequence attempt is broken
                        break

                # Check if log_entry_j matches sequence_definition[current_seq_def_idx]
                step_def_j = sequence_definition[current_seq_def_idx]
                match_j = True
                if step_def_j.get("event_type") and log_entry_j.get("event_type") != step_def_j["event_type"]:
                    match_j = False
                if step_def_j.get("source") and log_entry_j.get("source") != step_def_j["source"]:
                    match_j = False

                if match_j:
                    # `allow_repeats_in_definition` check:
                    # If this definition is same as previous, and this log is same as previous in `current_match_attempt`
                    if not allow_repeats_in_definition and current_seq_def_idx > 0:
                        prev_step_def_in_seq = sequence_definition[current_seq_def_idx - 1]
                        if step_def_j == prev_step_def_in_seq and log_entry_j == current_match_attempt[-1]:
                            # This log already fulfilled an identical previous step definition.
                            # To truly allow a single log to match multiple identical consecutive definitions,
                            # the logic would need to not advance `j` or use a more complex state.
                            # This simple check prevents one log instance being used for two identical steps back-to-back.
                            continue # Skip this log for this step, try next log for current step_def_j

                    current_match_attempt.append(log_entry_j)
                    current_seq_def_idx += 1
                    last_matched_log_original_idx = j # Update for intervening log check
                    last_event_ts_for_window = current_event_ts_for_window # Update for time window check

                    if current_seq_def_idx == seq_def_len: # Full sequence matched
                        found_sequences.append(list(current_match_attempt))
                        break # Break from inner loop (j), start new search from i+1
            # End of inner loop (j)
        # End of outer loop (i)
        return found_sequences

    def format_sequences_for_display(self, sequences: List[List[LogEntry]]) -> str:
        """
        Formats a list of found event sequences into a human-readable string.

        Args:
            sequences (List[List[LogEntry]]): A list of sequences, where each sequence
                                             is a list of LogEntry objects.

        Returns:
            str: A string representation of the sequences.
        """
        if not sequences:
            return "No event sequences found."

        output_lines = [f"Found {len(sequences)} event sequence(s):"]
        for i, seq in enumerate(sequences):
            output_lines.append(f"\n--- Sequence {i + 1} ---")
            for j, entry in enumerate(seq):
                ts_str = entry.get('timestamp', 'N/A')
                src_str = entry.get('source', 'N/A')
                evt_str = entry.get('event_type', 'N/A')
                data_summary = str(entry.get('data', {}))
                if len(data_summary) > 70: # Truncate long data summaries
                    data_summary = data_summary[:67] + "..."
                output_lines.append(
                    f"  Step {j + 1}: [{ts_str}] {src_str} - {evt_str} | Data: {data_summary}"
                )
        return "\n".join(output_lines)

# Example Usage (can be moved to an example script or notebook later)
if __name__ == "__main__":
    sample_logs_for_seq: List[LogEntry] = [
        {"timestamp": "2024-01-15T10:00:00.000Z", "source": "User", "event_type": "Query", "data": {"text": "Hello"}},
        {"timestamp": "2024-01-15T10:00:01.000Z", "source": "Agent", "event_type": "Thinking", "data": {}},
        {"timestamp": "2024-01-15T10:00:02.000Z", "source": "Agent", "event_type": "Response", "data": {"text": "Hi there!"}}, # Seq1 ends
        {"timestamp": "2024-01-15T10:00:03.000Z", "source": "User", "event_type": "Query", "data": {"text": "Another Q"}},
        {"timestamp": "2024-01-15T10:00:04.000Z", "source": "Other", "event_type": "SystemMsg", "data": {}},
        {"timestamp": "2024-01-15T10:00:05.000Z", "source": "Agent", "event_type": "Thinking", "data": {}},
        {"timestamp": "2024-01-15T10:00:06.000Z", "source": "Agent", "event_type": "Response", "data": {"text": "Okay"}}, # Seq2 ends
        {"timestamp": "2024-01-15T10:00:10.000Z", "source": "User", "event_type": "Query", "data": {"text": "Delayed Q"}}, # Start of Seq3 (time gap > 3s to next)
        {"timestamp": "2024-01-15T10:00:15.000Z", "source": "Agent", "event_type": "Thinking", "data": {}}, # 5s gap
        {"timestamp": "2024-01-15T10:00:16.000Z", "source": "Agent", "event_type": "Response", "data": {"text": "Got it."}}, # Seq3 ends
        {"timestamp": "2024-01-15T10:00:17.000Z", "source": "Agent", "event_type": "Thinking", "data": {"id":1}},
        {"timestamp": "2024-01-15T10:00:18.000Z", "source": "Agent", "event_type": "Thinking", "data": {"id":2}},
        {"timestamp": "2024-01-15T10:00:19.000Z", "source": "User", "event_type": "Query", "data": {"text": "Final Q"}}, # No thinking/response after this Query
    ]

    sequencer = EventSequencer(sample_logs_for_seq)

    defined_sequence_1 = [
        {"event_type": "Query", "source": "User"},
        {"event_type": "Thinking", "source": "Agent"},
        {"event_type": "Response", "source": "Agent"},
    ]

    print("--- Test Case 1: Basic Sequence (no time/intervening limits) ---")
    sequences1 = sequencer.extract_event_sequences(defined_sequence_1)
    print(sequencer.format_sequences_for_display(sequences1))
    # Expected: 3 sequences will be found based on the data.

    print("\n--- Test Case 2: With Max Time Between Steps (3 seconds) ---")
    sequences2 = sequencer.extract_event_sequences(defined_sequence_1, max_time_between_steps_seconds=3.0)
    print(sequencer.format_sequences_for_display(sequences2))
    # Expected: 2 sequences. The one starting at 10:00:10 (Delayed Q) will be excluded because the
    # gap between "Delayed Q" (10s) and "Thinking" (15s) is 5s, which > 3s.

    print("\n--- Test Case 3: With Max Intervening Logs (0) ---")
    sequences3 = sequencer.extract_event_sequences(defined_sequence_1, max_intervening_logs=0)
    print(sequencer.format_sequences_for_display(sequences3))
    # Expected: 1 sequence (the first one: 00s, 01s, 02s).
    # The sequence starting "Another Q" (03s) has "SystemMsg" (04s) before "Thinking" (05s), so it's excluded.
    # The sequence starting "Delayed Q" (10s) also has no intervening logs for its valid part.

    print("\n--- Test Case 4: With Max Intervening Logs (1) ---")
    sequences4 = sequencer.extract_event_sequences(defined_sequence_1, max_intervening_logs=1)
    print(sequencer.format_sequences_for_display(sequences4))
    # Expected: 2 sequences. The first one, and the one starting "Another Q" (which has 1 intervening log).

    defined_sequence_repeated_thinking = [
        {"event_type": "Thinking", "source": "Agent"},
        {"event_type": "Thinking", "source": "Agent"},
    ]
    print("\n--- Test Case 5: Repeated 'Thinking' in definition (allow_repeats_in_definition=False) ---")
    # This tests if two *distinct* 'Thinking' logs can match two consecutive 'Thinking' definitions.
    sequences5 = sequencer.extract_event_sequences(defined_sequence_repeated_thinking, allow_repeats_in_definition=False)
    print(sequencer.format_sequences_for_display(sequences5))
    # Expected: One sequence: (10:00:17 Thinking, 10:00:18 Thinking)

    # To test allow_repeats_in_definition more directly for a single log matching multiple steps,
    # the internal logic would need to be more stateful, potentially not advancing 'j' if a repeat is allowed
    # and the log matches the current (repeated) step definition.
    # The current `allow_repeats_in_definition=False` primarily prevents a log that is *identical* to the
    # previous log in the *currently forming sequence* from matching if the *definition step* is also identical.
    # If sorted_logs[j] is a *new distinct log entry* that happens to be identical in content to sorted_logs[j-1],
    # it will still match the next step even if allow_repeats_in_definition is False, which is reasonable.
    # The key is whether the *same instance from sorted_logs* is used for multiple identical steps.
    # The current loop `for j in range(i + 1, num_logs)` ensures different log instances are always picked.

    print("\n--- Test Case 6: Sequence not found ---")
    defined_sequence_not_present = [
        {"event_type": "NonExistentEvent"},
        {"event_type": "Thinking"},
    ]
    sequences6 = sequencer.extract_event_sequences(defined_sequence_not_present)
    print(sequencer.format_sequences_for_display(sequences6))
    # Expected: "No event sequences found."

```
