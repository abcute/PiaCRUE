# PiaCML Usage Examples

This directory contains Python scripts that demonstrate how to instantiate and use various concrete modules from the PiaAGI Cognitive Module Library (PiaCML). These examples aim to showcase basic interactions between modules and provide a starting point for understanding their operability.

## Prerequisites

Before running these examples, ensure that:
1.  You have Python 3.8+ installed.
2.  You have cloned the PiaAGI repository.
3.  Your Python environment can correctly import modules from the `PiaAGI_Hub.PiaCML` path. The scripts include `sys.path` modifications to attempt to allow execution directly from the `PiaAGI_Hub/CML_Usage_Examples/` directory, assuming this directory is within the `PiaAGI_Hub` folder which is at the same level as the `PiaCML` folder.
    Alternatively, ensure `PiaAGI_Hub` is in your `PYTHONPATH`.

## Examples

Each script is designed to be run standalone:

1.  **`perception_action_cycle_example.py`**:
    *   **Purpose:** Demonstrates a simplified perception-to-action cycle.
    *   **Modules Used:** `ConcretePerceptionModule`, `ConcreteWorldModel`, `ConcreteWorkingMemoryModule`, `ConcreteMotivationalSystemModule`, `ConcretePlanningAndDecisionMakingModule`, `ConcreteBehaviorGenerationModule`, `ConcreteCommunicationModule`.
    *   **Flow:**
        1.  Initializes CML modules.
        2.  Defines and activates a goal in the Motivational System.
        3.  Simulates a perception event, processes it, and updates the World Model.
        4.  Adds the percept to Working Memory.
        5.  Retrieves the active goal.
        6.  Creates and evaluates a plan for the goal, using conceptual context from WM and World Model, and direct interaction with the World Model instance for evaluation.
        7.  Selects the best plan.
        8.  Generates a behavior specification for the first step of the plan.
        9.  Conceptually formats linguistic output.
    *   **To Run:** `python perception_action_cycle_example.py`

2.  **`internal_state_influence_example.py`**:
    *   **Purpose:** Shows how internal states (emotion, self-assessment) can influence goal management within the motivational system.
    *   **Modules Used:** `ConcreteEmotionModule`, `ConcreteSelfModelModule`, `ConcreteMotivationalSystemModule`, `ConcreteWorkingMemoryModule`.
    *   **Flow:**
        1.  Initializes modules.
        2.  Simulates a negative event (task failure), appraises it with the Emotion Module.
        3.  Self-Model conceptually evaluates the failure, leading to a confidence update.
        4.  The Motivational System reacts to the negative emotion and low confidence by (conceptually) de-prioritizing a challenging goal and adding a new goal to analyze the failure.
    *   **To Run:** `python internal_state_influence_example.py`

3.  **`attention_focus_example.py`**:
    *   **Purpose:** Demonstrates how attention can be directed by goals from the motivational system, and how this focus influences information processing for Working Memory.
    *   **Modules Used:** `ConcreteMotivationalSystemModule`, `ConcreteAttentionModule`, `ConcreteWorkingMemoryModule`, `ConcretePerceptionModule`.
    *   **Flow:**
        1.  Initializes modules.
        2.  Sets a high-priority goal in the Motivational System.
        3.  Directs the Attention Module's focus based on this goal.
        4.  Simulates a stream of perceived information (using `ConcretePerceptionModule` to generate percepts).
        5.  Filters the stream using the Attention Module.
        6.  Adds the filtered, relevant items to Working Memory, respecting its capacity.
        7.  Optionally sets focus within Working Memory to a relevant item.
    *   **To Run:** `python attention_focus_example.py`

These examples print detailed information to the console about the status and operations of each module, allowing you to trace the conceptual flow of information and control. They use the basic concrete implementations from PiaCML, which have their own internal print statements for further verbosity.
