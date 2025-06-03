# PiaSE Scenario: Simple Goal-Driven Navigation Agent with Motivation

## Scenario Title

Simple Goal-Driven Navigation Agent with Motivation

## Objective

This scenario aims to demonstrate a PiaAGI agent utilizing its Perception, Working Memory (WM), Long-Term Memory (LTM), Planning, Behavior Generation, World Model, and a simple Motivational System to navigate within a `GridWorld` environment. The scenario will explore both extrinsically defined goals and intrinsically generated goals.

## PiaAGI Agent Configuration (Conceptual)

The PiaAGI agent for this scenario would be configured with the following CML modules:

*   **`PerceptionModule`**:
    *   **Concrete Class:** `ConcretePerceptionModule`.
    *   **Configuration:** Processes grid-based perceptions (e.g., current cell (x,y), contents of adjacent cells, presence of obstacles or target markers).
*   **`WorkingMemoryModule`**:
    *   **Concrete Class:** `ConcreteWorkingMemoryModule`.
    *   **Configuration:** Standard capacity. Holds current location, immediate surroundings, and the active navigation goal.
*   **`LongTermMemoryModule`**:
    *   **Concrete Class:** `ConcreteLongTermMemoryModule`.
    *   **Configuration:** Stores learned spatial information about the `GridWorld` (e.g., visited cells, locations of obstacles, pathways). Initially, it might be empty or contain a partial map.
*   **`PlanningAndDecisionMakingModule`**:
    *   **Concrete Class:** `ConcretePlanningAndDecisionMakingModule`.
    *   **Configuration:** Implements a pathfinding algorithm (e.g., A*, Dijkstra's) to generate a sequence of moves towards the goal location provided by the Motivational System or an external directive. It uses information from the World Model and LTM.
*   **`BehaviorGenerationModule`**:
    *   **Concrete Class:** `ConcreteBehaviorGenerationModule`.
    *   **Configuration:** Translates planned navigation steps (e.g., "move north," "move to (3,4)") into valid `ActionCommand`s for the `GridWorld` environment (e.g., `{"action_type": "MOVE", "direction": "NORTH"}`).
*   **`WorldModelModule`**:
    *   **Concrete Class:** `ConcreteWorldModel`.
    *   **Configuration:** Represents the agent's current understanding of the `GridWorld`, including:
        *   The grid dimensions (if known).
        *   Agent's current coordinates (x,y).
        *   Properties of cells (e.g., traversable, obstacle, target_location, visited, unexplored).
*   **`MotivationalSystemModule`**:
    *   **Concrete Class:** `ConcreteMotivationalSystemModule`.
    *   **Configuration (Key for this scenario):**
        *   **Option A (Extrinsic Goal):** Can receive and prioritize an explicitly assigned goal, e.g., `{"goal_type": "REACH_LOCATION", "target_coordinates": (X, Y)}`.
        *   **Option B (Intrinsic Drive):**
            *   **Curiosity:** Configured with an intrinsic drive to explore. It identifies unexplored cells in the `WorldModelModule`'s representation and generates goals to visit them (e.g., `{"goal_type": "EXPLORE_CELL", "target_coordinates": (new_X, new_Y), "intensity": 0.7}`).
            *   **Competence/Achievement:** Configured with a drive to successfully navigate or reach waypoints. It might generate goals to re-attempt failed paths or reach challenging locations, with satisfaction upon success.
        *   The module outputs the currently active/highest priority goal to the `PlanningAndDecisionMakingModule` (likely via WM).

## Environment

*   **Type:** `GridWorld`
*   **Setup:**
    *   A 2D grid of varying size (e.g., 10x10 to 20x20).
    *   May contain obstacles (impassable cells).
    *   Specific cells can be designated as "target locations" or have properties like "unexplored."
    *   Agent has a starting position.
    *   Perception provides information about the agent's current cell and possibly adjacent cells.

## Task Description

The agent's primary task is to navigate the `GridWorld`. The specifics depend on the motivational configuration:

*   **Option A (Extrinsic Goal):**
    1.  The agent is given an explicit goal to navigate to a specific cell (X, Y) at the beginning of the simulation.
    2.  The `MotivationalSystemModule` adopts this as its primary active goal.
    3.  The agent must plan and execute a path to reach (X, Y).
    4.  Success is reaching (X, Y).

*   **Option B (Intrinsic Drive - e.g., Curiosity):**
    1.  The agent starts with no explicit target cell.
    2.  The `MotivationalSystemModule`'s "curiosity" drive is active. It scans the `WorldModelModule` (which is updated by perception and LTM) for unexplored cells.
    3.  It generates a goal to navigate to a nearby, accessible, unexplored cell. The selection criteria for "which" unexplored cell can vary (e.g., closest, one leading to largest unexplored region).
    4.  The agent plans and executes a path to this self-generated goal.
    5.  Upon reaching it, the cell is marked as explored. The `MotivationalSystemModule` might then generate a new exploration goal, or its "curiosity" for that specific cell is sated.
    6.  The scenario might run for a fixed number of steps or until a certain percentage of the grid is explored.

## Key Interactions to Observe

*   **Goal Generation & Prioritization (especially for Option B):**
    *   How the `MotivationalSystemModule` identifies potential goals (e.g., unexplored cells, designated targets).
    *   If multiple motivations/goals are possible, how one is selected or prioritized.
    *   The intensity or persistence of the motivation.
*   **Planning & Pathfinding:**
    *   The `PlanningAndDecisionMakingModule` generating a valid path to the goal, considering obstacles and known layout from the `WorldModelModule` and `LTM`.
    *   How plans are re-evaluated if new obstacles are discovered or the environment changes.
*   **Navigation & World Model Update:**
    *   Agent executing `MOVE` actions correctly.
    *   The `WorldModelModule` being updated with the agent's new position and information about newly perceived cells.
    *   The `LongTermMemoryModule` storing information about traversed paths and explored areas.
*   **Impact of Motivation (Optional Extension):**
    *   If the agent successfully reaches a goal, does the `MotivationalSystemModule` register satisfaction? Does this affect future goal generation (e.g., curiosity temporarily sated, competence drive reinforced)?
    *   If the agent fails or gets stuck, how does this impact motivation (e.g., frustration leading to goal abandonment, or increased drive to overcome the obstacle)?
    *   For intrinsic drives, observe the pattern of exploration – is it systematic, random, or guided by some heuristic emerging from the motivation?
