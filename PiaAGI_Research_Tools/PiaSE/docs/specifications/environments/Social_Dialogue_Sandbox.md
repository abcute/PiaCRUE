# Social Dialogue Sandbox - Environment Design

## 1. Overview and Goals

*   **Purpose:** To create a simulated environment that facilitates the development and rigorous testing of a PiaAGI agent's advanced social intelligence capabilities. This includes its Theory of Mind (ToM), sophisticated communication strategies (like CSIM and RaR from PiaAGI.md), emotional intelligence, and the consistent expression of its configured personality.
*   **Focus:** The sandbox will emphasize:
    *   **Dialogue Coherence:** Maintaining sensible and contextually relevant conversation flow.
    *   **Empathetic Response:** Recognizing and appropriately responding to the emotional states of other interactors.
    *   **Understanding Implied Intent:** Going beyond literal interpretations to grasp underlying meanings or goals in dialogue.
    *   **Managing Social Goals:** Enabling the PiaAGI agent to pursue objectives such as building rapport, persuading others, or resolving conflicts effectively.

## 2. State Representation

The state of the Social Dialogue Sandbox at any given time would be defined by:

*   `agents_present`: A list of unique identifiers for all agents participating in the dialogue, including the PiaAGI agent and any simulated interactors.
*   `interactor_profiles`: A dictionary where each key is an `agent_id` of a simulated interactor, and the value is an object containing:
    *   `persona_id`: An identifier linking to a predefined persona template (e.g., "Curious_Child_Alex", "Skeptical_Adult_DrLee", "Friendly_Collaborator_Sam"). Personas would define baseline emotional dispositions, knowledge, and conversational style.
    *   `emotional_state`: The current internal emotional state of the interactor, potentially represented as a vector (e.g., valence, arousal, dominance) or discrete emotion types (e.g., happy, sad, angry, surprised, curious). This state is dynamic and influenced by the interaction.
    *   `goals`: The interactor's current conversational goals (e.g., "seek_information_about_X", "express_doubt_on_statement_Y", "offer_help_to_PiaAGI", "build_rapport"). These can also be dynamic.
    *   `knowledge_base_summary`: A brief description or link to a simplified knowledge base representing what the interactor generally knows or believes. This helps define the scope of their expertise and potential contributions or misunderstandings.
    *   `relationship_to_pia_agent`: A representation of the interactor's current disposition towards the PiaAGI agent (e.g., neutral, friendly, distrustful, curious, competitive). This is dynamic.
*   `dialogue_history`: A chronological log of all utterances made during the current session. Each entry would include:
    *   `speaker_id`: The identifier of the agent who spoke.
    *   `utterance_text`: The actual text of the utterance.
    *   `timestamp`: Simulation time of the utterance.
    *   (Conceptual) `targets`: List of agent IDs this utterance was directed to (if not broadcast).
*   `shared_context`: A representation of objects, topics, or information that has been explicitly mentioned and acknowledged by all participants, forming a common ground for the conversation.
*   `turn_holder`: The `agent_id` of the agent currently expected to speak or act.

## 3. Agent Perceptions (`PerceptionData` structure)

The PiaAGI agent would receive perceptions from the environment structured as follows (fitting into the broader `PerceptionData` model):

*   `textual_percepts`: A list containing the last utterance(s) directed at or overheard by the agent. Each element would be a `TextualPercept` with:
    *   `text`: The string content of the utterance.
    *   `speaker_id`: The identifier of the agent who made the utterance.
    *   `timestamp`: Simulation time of the utterance.
    *   *(Self-Correction/Clarification): While PiaAGI's internal `PerceptionModule` would generate a `semantic_summary` (NLU output like intent, entities, sentiment), the raw environment output for `TextualPercept` would primarily be the `text` and `speaker_id`. The environment itself doesn't interpret the text for the agent.*
*   `(Conceptual) non_verbal_cues`: If the environment is extended beyond pure text, this list could contain `VisualPercept` or `AuditoryPercept` objects.
    *   Example `VisualPercept`: `{"cue_type": "facial_expression", "speaker_id": "interactor_A", "detail": "slight_frown", "intensity": 0.4}`.
    *   Example `AuditoryPercept`: `{"cue_type": "speech_prosody", "speaker_id": "interactor_B", "detail": "hesitant_tone", "intensity": 0.6}`.
    *   These would require richer simulation capabilities beyond simple text exchange.
*   `custom_sensor_data`: A dictionary providing other relevant contextual information:
    *   `current_turn_holder`: The `agent_id` of who is expected to speak next.
    *   `active_participants`: A list of `agent_id`s currently in the conversation.
    *   `current_social_atmosphere`: (Conceptual) A high-level summary like "tense", "collaborative", "neutral", potentially derived from recent emotional expressions or goal conflicts.

## 4. Agent Actions (`ActionCommand` structure)

The PiaAGI agent can interact with the Social Dialogue Sandbox using actions like:

*   `action_type: "speak"`
    *   `parameters: {"utterance": "string", "target_agent_id": "Optional[string]"}`. If `target_agent_id` is provided, the utterance is a direct message; otherwise, it's broadcast to all present agents.
*   `action_type: "listen"`
    *   `parameters: {}`. Explicitly passes the turn or signifies the agent is waiting for another agent to speak. Useful for managing flow and avoiding interruptions.
*   `(Conceptual) action_type: "express_emotion"`
    *   `parameters: {"emotion_type": "string" (e.g., "smile", "nod", "show_concern_face"), "intensity": "float" (0.0-1.0)}`. This would allow the agent to attempt to convey emotion through non-verbal means, if the environment supports visualizing or interpreting such expressions for simulated interactors.
*   `(Conceptual) action_type: "query_social_context"`
    *   `parameters: {"query": "string" (e.g., "who_is_most_influential?", "what_is_interactor_A_goal?")}`. This is a more advanced action, allowing the agent to probe its understanding of the social dynamics if the environment supports revealing such meta-information (perhaps as a scaffolding mechanism).

## 5. Environment Dynamics

*   **Turn-Taking:** A mechanism manages whose turn it is to speak. This could be simple round-robin, based on who was last addressed, or more complex (e.g., allowing interruptions if an agent signals high urgency).
*   **Simulated Interactor Responses:** When it's a simulated interactor's turn:
    *   Their response is generated based on their persona, current emotional state, goals, and the dialogue history (especially PiaAGI's last utterance).
    *   This can range from simple rule-based systems (e.g., if PiaAGI asks a question, persona "Curious_Child" tries to answer) to using another LLM instance configured to role-play the persona.
*   **State Updates:**
    *   Interactor emotional states and goals are updated dynamically. For example, an empathetic response from PiaAGI might increase an interactor's "friendly" attribute in `relationship_to_pia_agent` and shift their emotional state towards positive valence. A dismissive remark might have the opposite effect.
    *   `dialogue_history` is appended with each new utterance.
    *   `shared_context` is updated if new information is accepted/understood by participants.
*   **Dynamic Events:** (Optional) The environment could introduce dynamic events, like a new agent joining the conversation or an external event that all agents perceive and react to.

## 6. Scaffolding Opportunities

This environment is designed to be highly configurable to support developmental scaffolding for PiaAGI:

*   **Persona Variation:** Introduce PiaAGI to a wide range of interactor personas (cooperative, shy, argumentative, knowledgeable, naive) and vary their conversational goals.
*   **Complexity Scaling:**
    *   Start with 1-on-1 dialogues before moving to group conversations.
    *   Begin with clear, explicit goals and gradually introduce more ambiguous or conflicting goals among interactors.
*   **Misunderstanding & Conflict:** Scenarios can be designed to specifically introduce misunderstandings, false beliefs (for ToM testing), or interpersonal conflicts that PiaAGI must navigate or attempt to resolve.
*   **Feedback Mechanisms:** The environment can provide explicit feedback (not directly from interactors, but as a meta-commentary for learning):
    *   "Interactor_A seems confused by your last statement because it contradicted their known belief X."
    *   "Your empathetic acknowledgement of Interactor_B's frustration has improved their disposition towards you."
    *   Tracking metrics like dialogue coherence, task success (if the dialogue has a goal), sentiment of interactors towards PiaAGI over time.
*   **Knowledge Constraints:** Limit or expand the knowledge bases of simulated interactors to test PiaAGI's ability to adapt its explanations or inquiries.
---
PiaAGI_Research_Tools/PiaSE/docs/specifications/environments/Crafting_Problem_Solving_World.md
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
---

## Conceptual Changes for `PiaAGI_Research_Tools/PiaSE/core_engine/interfaces.py`

The following is a conceptual draft of changes to be considered for `interfaces.py`. These are not being applied to the file by this subtask, but are provided as a design proposal.

```python
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field

# ... (other existing imports and BaseModel definitions like PiaSEEvent, ActionResult)

# NEW/MODIFIED PERCEPT TYPESS

class VisualPercept(BaseModel):
    """
    Represents a single visual percept - an object or feature identified in the visual field.
    Designed to be generic for different kinds of visual environments.
    """
    percept_id: str = Field(..., description="Unique identifier for this instance of the percept (e.g., 'tree_1_at_t5').")
    entity_type: str = Field(..., description="Classification of the entity (e.g., 'tree', 'rock', 'interactor_face', 'text_label').")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Properties of the entity (e.g., {'color': 'green', 'size': 'large', 'material': 'wood', 'expression': 'smile'}).")
    location_in_view: Optional[List[float]] = Field(None, description="Coordinates or bounding box within the agent's visual field (e.g., [x, y, w, h]).")
    timestamp: float = Field(..., description="Simulation time at which this percept was captured.")
    # Conceptual: could add confidence score if from an actual vision system

class AuditoryPercept(BaseModel):
    """
    Represents a single auditory percept - a sound event.
    """
    percept_id: str = Field(..., description="Unique identifier for this instance of the percept.")
    sound_type: str = Field(..., description="Classification of the sound (e.g., 'speech', 'footstep', 'item_drop', 'engine_hum').")
    source_id: Optional[str] = Field(None, description="Identifier of the agent or object that produced the sound, if known.")
    content: Optional[str] = Field(None, description="For speech, the transcribed text. For other sounds, a description.")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Properties of the sound (e.g., {'intensity': 'loud', 'pitch': 'high', 'prosody': 'hesitant_tone'}).")
    location_of_source: Optional[List[float]] = Field(None, description="Estimated location of the sound source.")
    timestamp: float = Field(..., description="Simulation time at which this percept was captured.")

class TextualPercept(BaseModel):
    """
    Represents a piece of text perceived by the agent, often from dialogue or reading.
    """
    percept_id: str = Field(..., description="Unique identifier for this instance of the percept.")
    text: str = Field(..., description="The content of the text.")
    source_type: str = Field(..., description="Origin of the text (e.g., 'dialogue_utterance', 'book_content', 'console_message').")
    speaker_or_author_id: Optional[str] = Field(None, description="Identifier of the agent who spoke or wrote the text, if applicable.")
    timestamp: float = Field(..., description="Simulation time at which this percept was captured.")
    # metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context like target audience for dialogue.")


# MODIFIED PerceptionData

class PerceptionData(BaseModel):
    """
    Container for all perceptual information relayed from the environment to an agent at a given step.
    """
    timestamp: float = Field(..., description="The simulation time at which these perceptions were generated.")

    # Environment-agnostic event that triggered this perception update (optional)
    triggering_event: Optional[PiaSEEvent] = None

    # New structured percept fields
    visual_percepts: Optional[List[VisualPercept]] = Field(default_factory=list, description="List of visual percepts from the current timestep.")
    auditory_percepts: Optional[List[AuditoryPercept]] = Field(default_factory=list, description="List of auditory percepts from the current timestep.")
    textual_percepts: Optional[List[TextualPercept]] = Field(default_factory=list, description="List of textual percepts from the current timestep.")

    # Renamed from sensor_data to custom_sensor_data for clarity
    custom_sensor_data: Dict[str, Any] = Field(default_factory=dict, description="Generic dictionary for other sensor readings or environment-specific data not fitting the common percept types (e.g., agent's internal state like hunger, raw data from specific sensors).")

    # Feedback on the last action performed by the agent
    last_action_result: Optional[ActionResult] = None

    # General message from the environment (e.g., narration, system messages)
    environment_message: Optional[str] = None

    # List of currently available actions (optional, can be used by simpler agents or for UI hints)
    available_actions: Optional[List[str]] = Field(default_factory=list)

    class Config:
        # For example, if PiaSEEvent or ActionResult are complex objects
        arbitrary_types_allowed = True

# ... (rest of the file, including AgentInterface, ActionCommand etc.)
```
