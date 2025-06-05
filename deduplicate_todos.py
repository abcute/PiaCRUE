import json
import re
import sys

def normalize_task_text(text):
    # Lowercase
    text = text.lower()
    # Remove common markers like [user_task], [bug], [enhancement], etc., and task sources like (From IMPROVEMENT_TODOLIST #13)
    text = re.sub(r"^\s*\[.*?\]\s*", "", text) # Matches [TAG]
    text = re.sub(r"\s*\(from .*?\)\s*$", "", text) # Matches (From X) at the end
    # Remove task ID like markers, e.g., "#13)"
    text = re.sub(r"\s*#\d+\)\s*$", "", text)
    # Remove specific phrases like "(User task - content provided)"
    text = re.sub(r"\s*\(user task - content provided\)\s*$", "", text)
    # Remove specific phrases like "(Derived from old ToDoList - potentially superseded...)"
    text = re.sub(r"\s*\(derived from old todolist - .*?\)\s*$", "", text)
    # Remove specific phrases like "(Derived from old ToDoList)"
    text = re.sub(r"\s*\(derived from old todolist\)\s*$", "", text)
    # Remove specific phrases like "(From User's New List)"
    text = re.sub(r"\s*\(from user's new list\)\s*$", "", text)
    # Remove specific phrases like "(From User's New List - Note: some basic versions were integrated in previous cycle)"
    text = re.sub(r"\s*\(from user's new list - note: some basic versions were integrated in previous cycle\)\s*$", "", text)
    # Remove specific phrases like "(Covers \"Extend Logging Spec\" from AVT new list)"
    text = re.sub(r"\s*\(covers \"extend logging spec\" from avt new list\)\s*$", "", text)
    # Remove specific phrases like "(Derived from User's New List & old ToDoList `[/]`)"
    text = re.sub(r"\s*\(derived from user's new list & old todolist `\[/]`\)\s*$", "", text)
    # Remove specific phrases like "(From User's New List - This covers existing DSE work and future enhancements)"
    text = re.sub(r"\s*\(from user's new list - this covers existing dse work and future enhancements\)\s*$", "", text)


    # Remove leading/trailing whitespace
    text = text.strip()
    return text

def merge_duplicates(todo_list):
    grouped_tasks = {}

    for item in todo_list:
        normalized_text = normalize_task_text(item['task'])

        # Skip empty normalized strings if any happen due to aggressive regex
        if not normalized_text:
            continue

        if normalized_text not in grouped_tasks:
            grouped_tasks[normalized_text] = {
                'task': item['task'],
                'completed': item['completed'],
                'section': item['section'],
                # 'original_normalized': normalized_text # For debugging
            }
        else:
            existing_item_group = grouped_tasks[normalized_text]

            if item['completed']:
                existing_item_group['completed'] = True

            if len(item['task']) > len(existing_item_group['task']):
                existing_item_group['task'] = item['task']
                existing_item_group['section'] = item['section'] # Keep section of the chosen task

            # If tasks have same length, prefer the one that is NOT completed if the other is,
            # or just keep the existing one. This helps retain more descriptive pending tasks.
            elif len(item['task']) == len(existing_item_group['task']):
                if existing_item_group['completed'] and not item['completed']:
                    # If current chosen is completed, but this new one is not,
                    # prefer the non-completed one if text is same length (might be more up-to-date version)
                    existing_item_group['task'] = item['task']
                    existing_item_group['section'] = item['section']
                    # Completion status remains true if any was true
                    existing_item_group['completed'] = item['completed'] or existing_item_group['completed']


    deduplicated_list = list(grouped_tasks.values())
    return deduplicated_list

if __name__ == "__main__":
    json_input_str = ""
    try:
        json_input_str = sys.stdin.read()
        if not json_input_str.strip():
            print("Error: No JSON input provided to stdin.", file=sys.stderr)
            sys.exit(1)

        todo_items = json.loads(json_input_str)
        merged_list = merge_duplicates(todo_items)
        print(json.dumps(merged_list, indent=2))

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input. Details: {e}", file=sys.stderr)
        print(f"Received input: {json_input_str[:500]}...", file=sys.stderr) # Print first 500 chars of input
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)
