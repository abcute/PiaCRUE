# PiaAGI Prompt Engineering Suite (PiaPES) - MVP

## Introduction

Welcome to the PiaAGI Prompt Engineering Suite (PiaPES). PiaPES is a collection of tools and conceptual designs aimed at supporting the structured creation, management, and application of "Guiding Prompts" and "Developmental Curricula" for the PiaAGI (Progressive Intelligence Architecture for Artificial General Intelligence) framework.

This directory focuses on the initial Python-based **Prompt Engine MVP (Most Viable Product)**, which provides the foundational classes and utilities for working with these prompt structures programmatically.

## Purpose

The primary purpose of PiaPES, and its `prompt_engine_mvp.py` component, is to:

*   Enable systematic and reproducible design of complex agent configurations.
*   Facilitate the creation of developmental sequences (curricula) to guide agent learning.
*   Provide a standardized way to define prompt structures that can be versioned, shared, and evaluated.
*   Support researchers and developers in crafting the detailed instructions and contexts necessary for guiding advanced AGI agents.

## Current Status

The `prompt_engine_mvp.py` script represents an initial implementation providing core functionalities. It is considered an MVP that demonstrates key concepts of the PiaPES design.

Key features of the current `prompt_engine_mvp.py` include:

*   **Structured Prompt & Curriculum Creation:** Python classes (`PiaAGIPrompt`, `Role`, `CognitiveModuleConfiguration`, `CurriculumStep`, `DevelopmentalCurriculum`, etc.) that mirror the conceptual PiaAGI prompt and curriculum structures.
*   **Placeholder Substitution:** A mechanism to embed placeholders (e.g., `{my_variable}`) in string attributes of prompt elements and fill them with specific data using the `fill_placeholders()` method.
*   **Rendering to Markdown:** The `render()` method on any prompt element generates a human-readable Markdown representation.
*   **Saving & Loading (JSON):**
    *   `save_template(element, filepath)`: Serializes prompt or curriculum objects to a JSON file, preserving their structure and type information. This is the recommended format for reliable storage and round-trip conversion.
    *   `load_template(filepath)`: Deserializes JSON files back into their corresponding Python objects.
*   **Exporting to Markdown (One-Way):**
    *   `export_to_markdown(element, filepath)`: Exports the rendered Markdown of a prompt or curriculum to a `.md` file, primarily for documentation or human review. This is a one-way export; these Markdown files cannot be directly loaded back into objects.
*   **Developmental Curriculum Design:** Classes (`DevelopmentalCurriculum`, `CurriculumStep`) to define sequences of prompts for agent development.
*   **Internal Versioning:** Key objects like `PiaAGIPrompt` and `DevelopmentalCurriculum` include an optional `version` attribute for tracking versions within the data.
*   **Unit Tests:** A suite of unit tests is available to verify the functionality of the prompt engine.

## How to Use

### `prompt_engine_mvp.py`

The `prompt_engine_mvp.py` script can be used as a library by importing its classes and functions into your own Python projects.

A typical workflow involves:
1.  Importing the necessary classes (e.g., `PiaAGIPrompt`, `Role`, `Requirements`).
2.  Instantiating these classes to define the structure of your prompt or curriculum.
3.  Optionally, using placeholders in string attributes.
4.  Calling `fill_placeholders(data_dict)` to populate any placeholders.
5.  Calling `render()` to get a Markdown string representation.
6.  Using `save_template()` to save the object to a JSON file or `export_to_markdown()` for a Markdown file.
7.  Using `load_template()` to load objects from JSON files.

**Example (Conceptual):**
```python
from PiaAGI_Hub.PiaPES.prompt_engine_mvp import PiaAGIPrompt, Requirements, save_template, load_template

# Create a prompt
my_prompt = PiaAGIPrompt(
    author="Test User",
    version="1.0",
    objective="A sample prompt.",
    requirements=Requirements(goal="Demonstrate basic usage.")
)

# Save it (JSON)
save_template(my_prompt, "my_prompt_template.json")

# Load it back
loaded_prompt = load_template("my_prompt_template.json")

if loaded_prompt:
    print(loaded_prompt.render())
```

For detailed examples and usage of all features, please refer to the [USAGE.md](./USAGE.md) file.

### Running Unit Tests

The unit tests verify the core functionalities of the `prompt_engine_mvp.py`. To run the tests, navigate to the parent directory of `PiaAGI_Hub` (or ensure `PiaAGI_Hub` is in your `PYTHONPATH`) and run:

```bash
python -m unittest discover PiaAGI_Hub/PiaPES/tests
```
or from within the `PiaAGI_Hub/PiaPES` directory:
```bash
python -m unittest discover tests
```

## Roadmap / Future Development

The `prompt_engine_mvp.py` script is the first step towards a more comprehensive PiaAGI Prompt Engineering Suite. The broader conceptual design, including features like a dedicated Prompt Editor/IDE, Cognitive Configuration GUI, advanced version control integration, a Prompt Evaluation Module, and enhanced Collaboration Features, is detailed in the main PiaPES design document.

## Links

*   **Detailed MVP Usage:** [PiaAGI_Hub/PiaPES/USAGE.md](./USAGE.md)
*   **Full Conceptual Design for PiaPES:** [PiaAGI_Hub/PiaAGI_Prompt_Engineering_Suite.md](../PiaAGI_Prompt_Engineering_Suite.md)
*   **Unit Tests:** [PiaAGI_Hub/PiaPES/tests/](./tests/)

---

This README provides an overview of the PiaPES MVP. We encourage users to explore the `prompt_engine_mvp.py` script and the detailed `USAGE.md` for practical application.
