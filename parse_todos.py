import re
import json

def parse_todo_list(markdown_content):
    lines = markdown_content.splitlines()

    structured_todos = []
    current_section = "General" # Default section if no header found before items

    # Regex to identify section headers (e.g., # Section, ## Subsection)
    header_pattern = re.compile(r"^(#+)\s+(.*)")
    # Regex to identify ToDo items
    todo_pattern = re.compile(r"^\s*-\s*\[([x ])\]\s*(.*)")

    # Skip the initial markdown code block if present
    in_code_block = False
    # Need to handle the case where the file might not have the ```markdown block
    start_processing_index = 0
    for i, line in enumerate(lines):
        if line.strip() == "```markdown":
            in_code_block = True
            continue
        if line.strip() == "```" and in_code_block:
            in_code_block = False
            start_processing_index = i + 1
            break

    # Process lines after any initial code block
    processed_lines = lines[start_processing_index:]

    for line in processed_lines:
        # Preserve leading/trailing whitespace for task text initially, strip after matching
        # Let's strip the line for header and general structure matching first
        stripped_line = line.strip()

        header_match = header_pattern.match(stripped_line)
        if header_match:
            current_section = header_match.group(2).strip()
            continue # Move to next line after identifying a header

        # For ToDo items, we need to match on the original line to preserve indentation if needed for context,
        # but the regex itself is designed for stripped-like content for the task item start.
        # The current regex `^\s*-\s*\[([x ])\]\s*(.*)` handles leading spaces for the list item itself.
        todo_match = todo_pattern.match(line) # Match on original line to respect `^\s*`
        if todo_match:
            status_char = todo_match.group(1)
            # The rest of the line is the task, strip it.
            text = todo_match.group(2).strip()

            completed = (status_char == 'x')

            # Handle potential non-task lines that might be part of a list item (e.g. multi-line descriptions)
            # For this task, we are only capturing the first line of the ToDo item.
            # Future enhancements could involve accumulating multi-line task descriptions.

            structured_todos.append({
                "section": current_section,
                "task": text,
                "completed": completed
            })

    return structured_todos

if __name__ == "__main__":
    try:
        with open("ToDoList.md", "r", encoding="utf-8") as f:
            actual_content = f.read()

        parsed_data = parse_todo_list(actual_content)

        print(json.dumps(parsed_data, indent=2))

    except FileNotFoundError:
        print("Error: ToDoList.md not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
