# PiaSE Scenario: Basic Information Gathering Agent

## Scenario Title

Basic Information Gathering Agent

## Objective

This scenario aims to demonstrate a PiaAGI agent using a core set of cognitive modules (Perception, Working Memory, Long-Term Memory, Planning, and Behavior Generation) to locate, retrieve, and read a specific item within a `TextBasedRoom` environment.

## PiaAGI Agent Configuration (Conceptual)

The PiaAGI agent for this scenario would be configured with the following CML modules:

*   **`PerceptionModule`**:
    *   **Concrete Class:** `ConcretePerceptionModule` (or a text-specialized version).
    *   **Configuration:** Optimized for processing textual descriptions of rooms, objects, and agent actions. Capable of identifying nouns (potential objects), verbs (potential actions), and spatial prepositions.
*   **`WorkingMemoryModule`**:
    *   **Concrete Class:** `ConcreteWorkingMemoryModule`.
    *   **Configuration:** Standard capacity. Central Executive functions active for managing current percepts, short-term goals (e.g., "find journal," "take journal"), and relevant LTM retrievals.
*   **`LongTermMemoryModule`**:
    *   **Concrete Class:** `ConcreteLongTermMemoryModule` (e.g., a simple semantic network or knowledge base).
    *   **Configuration:** Pre-populated with general knowledge relevant to the task, such as:
        *   "Journals are items."
        *   "Items can be picked up (taken)."
        *   "Journals can be read."
        *   "Reading provides information."
        *   "Containers (like 'desk drawer', 'chest') can hold items."
        *   "Containers need to be opened to access contents."
*   **`PlanningAndDecisionMakingModule`**:
    *   **Concrete Class:** `ConcretePlanningAndDecisionMakingModule`.
    *   **Configuration:** Capable of simple goal decomposition. For the goal "Read the journal," it should be able to generate a plan like:
        1.  IF journal location unknown THEN explore rooms to find journal.
        2.  IF journal found THEN navigate to journal's location.
        3.  IF journal in container THEN open container.
        4.  IF journal is accessible THEN take journal.
        5.  IF journal is held THEN read journal.
*   **`BehaviorGenerationModule`**:
    *   **Concrete Class:** `ConcreteBehaviorGenerationModule`.
    *   **Configuration:** Translates planned actions (e.g., "navigate to room B," "open desk_drawer," "take journal_item," "read journal_item") into valid `ActionCommand`s for the `TextBasedRoom` environment.
*   **`WorldModelModule`**:
    *   **Concrete Class:** `ConcreteWorldModel`.
    *   **Configuration:** Represents the state of the known environment, including:
        *   Rooms and their connections.
        *   Objects within rooms or containers, and their properties (e.g., `is_readable`, `is_container`, `is_open`).
        *   Agent's current location and inventory.
*   **Other Modules (Minimally Configured/Passive):**
    *   `MotivationalSystemModule`: May not be actively driving behavior if the goal "Read the journal" is explicitly given. If not, a simple "task completion" drive could be active.
    *   `EmotionModule`: Largely passive, though frustration could be modeled if the agent repeatedly fails.
    *   `SelfModelModule`: Basic representation of agent capabilities (e.g., "can move," "can take," "can read").
    *   `LearningModule`: Could be active to learn the journal's location or the contents of the journal, but not the primary focus for this scenario's objective.

## Environment

*   **Type:** `TextBasedRoom`
*   **Setup:**
    *   A small environment with 2-3 rooms (e.g., "Study," "Library," "Living Room").
    *   The target item, a "journal," is placed in a less obvious location, such as:
        *   Inside a container (e.g., a "desk drawer" in the Study).
        *   In a room different from the agent's starting room.
    *   Other distractor items might be present.
    *   Room descriptions provide clues about objects and potential exits.

## Task Description

The agent starts in a designated room (e.g., "Living Room").
The agent is given the explicit high-level goal: **"Read the journal."**

The agent must:
1.  Explore the environment if the journal's location is not immediately known.
2.  Identify the journal.
3.  If the journal is in a container, open the container.
4.  Take the journal.
5.  Execute the "read" action on the journal.

The scenario is successful when the agent performs the "read" action on the correct "journal" item.

## Key Interactions to Observe

*   **Perception & World Modeling:**
    *   How the agent parses room descriptions from the `TextBasedRoom` to identify objects, containers, and exits.
    *   How the `WorldModelModule` is updated with new information as the agent explores.
*   **Planning & Goal Decomposition:**
    *   How the `PlanningAndDecisionMakingModule` breaks down the high-level goal "Read the journal" into a sequence of sub-goals and actions (e.g., navigate, open, take, read).
    *   How the plan adapts if the journal is not found immediately or is inside a container.
*   **Navigation & Interaction:**
    *   Agent's movement between rooms.
    *   Agent's interaction with objects (e.g., `OPEN desk_drawer`, `TAKE journal from desk_drawer`).
*   **LTM Usage:**
    *   Evidence of the agent using pre-populated knowledge from LTM (e.g., knowing that journals are readable, or that containers might hold items).
*   **Action Execution:**
    *   Successful execution of the `READ journal` command and the subsequent information gain (if simulated by the environment).
*   **Error Handling (Optional Extension):**
    *   How the agent reacts if it tries to read a non-readable item.
    *   How it reacts if it tries to open a non-container object.
