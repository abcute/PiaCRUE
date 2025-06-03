# Crafting & Problem-Solving World - Environment Design

## 1. Overview and Goals

*   **Purpose:** To provide a simulated environment where a PiaAGI agent can develop, practice, and demonstrate capabilities related to multi-step planning, tool acquisition and use, resource management, and procedural skill learning.
*   **Focus:** The environment will challenge the agent in areas such as:
    *   **Goal Decomposition:** Breaking down complex construction or acquisition goals into manageable sub-tasks.
    *   **Recipe Learning:** Discovering, learning, and utilizing crafting recipes that specify how to combine resources to create new items or tools.
    *   **Resource Management:** Efficiently gathering, storing, and utilizing finite resources.
    *   **Tool Functionality & Selection:** Understanding what tools are needed for specific tasks and how to use them.
    *   **Plan Adaptation:** Modifying plans based on resource availability, tool accessibility, or unexpected outcomes.

## 2. State Representation

The state of the Crafting & Problem-Solving World would be defined by:

*   `world_map`: A representation of the environment's spatial layout. This could be:
    *   A grid-based system (e.g., 2D array of cells).
    *   A graph-based system (nodes as locations, edges as connections).
*   `locations`: A dictionary where each key is a `location_id` (e.g., "forest_clearing", "mine_entrance", "workshop_A"). Each location object contains:
    *   `description`: Textual description of the location.
    *   `resources`: A dictionary of available raw resources and their quantities (e.g., `{"wood_log": 20, "stone_chunk": 15, "iron_ore_deposit": 1}`).
    *   `tools_present`: A list of tools currently available to be picked up at that location (e.g., `["worn_axe", "stone_pickaxe"]`).
    *   `crafting_stations`: A list of available crafting apparatus at this location (e.g., `["workbench", "furnace", "anvil"]`). Each station might enable specific recipes.
    *   `interactable_objects`: Other objects or features (e.g., "locked_chest", "blueprint_table", "broken_bridge").
*   `agent_inventory`: A dictionary representing the resources and tools currently held by the PiaAGI agent:
    *   `resources`: (e.g., `{"wood_plank": 5, "stone_brick": 10, "iron_ingot": 2}`).
    *   `tools`: (e.g., `["sturdy_axe", "repair_hammer"]`).
*   `known_recipes`: A list or dictionary of crafting recipes that the agent has learned or discovered. Each recipe would specify:
    *   `item_to_craft`: The name of the item produced.
    *   `required_resources`: A dictionary of resource types and quantities needed (e.g., `{"wood_plank": 3, "stone_brick": 2}`).
    *   `required_tool_in_inventory`: (Optional) A tool that must be in the agent's inventory (e.g., "hammer").
    *   `required_crafting_station`: (Optional) The type of crafting station required to perform the craft (e.g., "workbench").
    *   `required_skill_level`: (Optional) A minimum skill level in a relevant craft (e.g. "woodworking_level_2").
*   `active_goals`: A list of current construction, acquisition, or problem-solving goals assigned to or adopted by the agent (e.g., "craft_a_bridge_segment", "acquire_iron_pickaxe", "find_power_source_for_machine_X").
*   `agent_state`:
    *   `current_location`: The `location_id` where the agent currently is.
    *   `skill_levels`: (Optional) Agent's proficiency in various skills (e.g., `{"woodcrafting": 1.5, "mining": 0.8}`).

## 3. Agent Perceptions (`PerceptionData` structure)

The PiaAGI agent would receive perceptions structured as follows:

*   `custom_sensor_data`: A dictionary providing rich information about the agent's immediate context:
    *   `current_location_info`:
        *   `description`: Textual description.
        *   `available_resources`: Dictionary of resources and quantities at the current location.
        *   `tools_at_location`: List of tools available for pickup.
        *   `crafting_stations_present`: List of crafting stations.
        *   `exits`: Possible navigation targets from current location.
    *   `inventory_contents`: Dictionary of resources and tools the agent is carrying.
    *   `known_recipes_list`: A list of item names the agent knows how to craft.
    *   `active_goals_list`: Current goals the agent is pursuing.
    *   `feedback_on_last_action`: A message describing the outcome of the previous action (e.g., "Successfully gathered 5 wood logs.", "Crafting failed: missing 2 stone bricks.", "Navigation failed: path blocked.").
    *   `agent_status_update`: (Optional) Changes to skill levels, etc.
*   `(Conceptual) visual_percepts`: If the environment were visually rendered, this could be a list of `VisualPercept` objects, each describing a visible entity:
    *   `{"type": "resource_node", "id": "tree_1", "resource_type": "wood_log", "estimated_quantity": "high"}`
    *   `{"type": "tool_item", "id": "axe_on_ground", "tool_type": "axe"}`
*   `(Conceptual) textual_percepts`: Could include descriptions from examining objects more closely, or messages found in the world.

## 4. Agent Actions (`ActionCommand` structure)

The PiaAGI agent can interact with this world using actions like:

*   `action_type: "navigate"`
    *   `parameters: {"target_location_id": "string"}`.
*   `action_type: "gather_resource"`
    *   `parameters: {"resource_type": "string", "quantity_to_gather": "int", "tool_used": "optional[string]"}`. Some resources might require a specific tool (e.g., "axe" for "wood_log").
*   `action_type: "pickup_tool"`
    *   `parameters: {"tool_name": "string", "location_id": "optional[string]"}` (tool to pick up from current location).
*   `action_type: "drop_item"`
    *   `parameters: {"item_name": "string", "quantity": "int"}` (from inventory to current location).
*   `action_type: "craft_item"`
    *   `parameters: {"recipe_name": "string" (or item_name), "quantity": "int", "crafting_station_used": "optional[string]"}`. The agent must know the recipe.
*   `action_type: "use_tool_on_target"`
    *   `parameters: {"tool_in_inventory_name": "string", "target_object_id_or_type": "string", "action_verb": "optional[string]"}` (e.g., use "axe" on "tree_1" with action "chop"; use "key" on "locked_chest_1" with action "unlock").
*   `(Conceptual) action_type: "learn_recipe"`
    *   `parameters: {"source": "string" (e.g., "blueprint_A", "experimentation_result"), "recipe_details": "dict"}`. This action allows the agent to add a new recipe to its `known_recipes`.
*   `action_type: "construct_at_location"`
    *   `parameters: {"item_to_construct_name": "string", "location_id_or_feature_id": "string"}` (e.g. build "bridge_segment" at "river_crossing_point"). Requires resources and possibly tools.

## 5. Environment Dynamics

*   **Resource Depletion/Regeneration:** Resources at locations deplete when gathered. Some might regenerate slowly over time or under certain conditions.
*   **Crafting Logic:**
    *   Successfully executing `craft_item` consumes the specified resources from the agent's inventory.
    *   The crafted item(s) are added to the agent's inventory.
    *   Crafting fails if resources, tools, or required crafting stations are missing.
*   **Tool Requirements & Effects:**
    *   Some actions (e.g., gathering hard resources, crafting advanced items, construction) require specific tools to be in the agent's inventory and potentially "equipped" or "active".
    *   Using a tool might be the only way to interact with certain objects (e.g., "axe" to fell a "tree" object, "pickaxe" to mine "ore_deposit").
*   **Recipe Discovery:** New recipes can be learned by finding "blueprints" (items in the world), through successful "experimentation" (if supported), or by achieving milestones.
*   **Goal Introduction:** New goals can be assigned to the agent dynamically by the simulation engine or based on discoveries.
*   **(Optional) Advanced Dynamics:**
    *   Tool degradation (tools wear out with use and might need repair, which itself is a crafting task).
    *   Environmental events (e.g., a storm makes a location temporarily inaccessible).
    *   Simple physics (e.g., a constructed bridge needs support).

## 6. Scaffolding Opportunities

This environment offers rich possibilities for scaffolding PiaAGI's learning:

*   **Gradual Complexity:**
    *   Start with a limited set of basic resources and 1-2 step recipes.
    *   Gradually introduce more resource types, more complex (multi-step) recipes, and the need for specialized tools and crafting stations.
*   **Guided Discovery:**
    *   Provide initial core recipes directly.
    *   Place "blueprint" items that teach specific new recipes when found and "learned".
    *   Offer hints or partial recipes if the agent is stuck on a problem.
*   **Problem-Solving Challenges:**
    *   Introduce "broken" tools that the agent must learn to repair (requiring them to find/craft repair materials and possibly a repair kit recipe).
    *   Present goals that require a sequence of interdependent crafting tasks (e.g., "build a shelter" requires crafting tools -> gathering resources -> crafting building components -> assembling components).
    *   Create scenarios where a common resource becomes scarce, forcing the agent to find alternative solutions or new resource locations.
*   **Skill Development:** If skill levels are implemented, tasks can require minimum skill levels, encouraging the agent to "practice" simpler tasks to improve skills needed for more advanced ones.
*   **Feedback Granularity:** Vary the detail in feedback messages to guide learning. Initially, "Crafting failed: missing 2 stone bricks." Later, more general "Crafting failed." if the agent is expected to infer the cause.
