import json
from collections import defaultdict
import sys

# This preamble was manually extracted from the beginning of the original ToDoList.md
# It includes the main title and the introductory markdown code block.
PREAMBLE = """# PiaAGI Project Upgrade ToDo List

```markdown
# PiaAGI

PiaAGI is a project that aims to upgrade the existing PiaA project to use the latest technologies and best practices.

## Goals

- Improve performance and scalability
- Enhance user experience
- Modernize the codebase
- Ensure long-term maintainability

## Roadmap

- [ ] Phase 1: Research and Planning
- [ ] Phase 2: Development and Testing
- [ ] Phase 3: Deployment and Launch
```"""

def reconstruct_todolist_markdown(deduplicated_list):
    grouped_by_section = defaultdict(list)

    # Preserve the order of sections as encountered in the de-duplicated list
    # This assumes the de-duplication process maintained a reasonable order
    ordered_section_names = []
    temp_sections_seen = set()

    for item in deduplicated_list:
        section = item['section']
        grouped_by_section[section].append(item)
        if section not in temp_sections_seen:
            ordered_section_names.append(section)
            temp_sections_seen.add(section)

    markdown_output = [PREAMBLE]

    first_real_section_written = False
    for section_name in ordered_section_names:
        items_in_section = grouped_by_section[section_name]

        if not items_in_section:  # Skip empty sections
            continue

        # Add a blank line before a new section header,
        # but not for the very first "General" section if it follows PREAMBLE directly.
        if first_real_section_written or section_name != "General":
            markdown_output.append("") # Ensures a blank line before the header

        if section_name != "General":
            markdown_output.append(f"## {section_name}")

        first_real_section_written = True # Mark that we've started writing main content

        for item in items_in_section:
            checkbox = "[x]" if item['completed'] else "[ ]"
            markdown_output.append(f"- {checkbox} {item['task']}")

    return "\n".join(markdown_output)

if __name__ == "__main__":
    json_input_str = ""
    try:
        json_input_str = sys.stdin.read()
        if not json_input_str.strip():
            print("Error: No JSON input provided to stdin.", file=sys.stderr)
            sys.exit(1)

        deduplicated_items = json.loads(json_input_str)
        new_markdown_content = reconstruct_todolist_markdown(deduplicated_items)

        # Print the reconstructed markdown to stdout
        # The agent will then use this output to overwrite the file.
        print(new_markdown_content)

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input. Details: {e}", file=sys.stderr)
        # It's helpful to see a snippet of what was received if it's not too long
        print(f"Received input snippet: {json_input_str[:1000]}...", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred during reconstruction: {e}", file=sys.stderr)
        sys.exit(1)
