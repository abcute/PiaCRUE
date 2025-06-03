# PiaSE: Human-in-the-Loop (HITL) Interface - Conceptual Design

## 1. Introduction and Goals

*   **Purpose:** To define a comprehensive framework for how human users can interact with, monitor, and influence PiaSE (PiaAGI Simulation Environment) simulations in real-time or near real-time. This interface is crucial for leveraging human intelligence and intuition in the AGI development process.
*   **Goals:**
    *   **Enable Richer Developmental Scaffolding:** Allow humans to provide nuanced guidance, feedback, and demonstrations that go beyond what can be easily automated in early developmental stages of PiaAGI.
    *   **Facilitate Interactive Debugging and Testing:** Provide tools for developers and researchers to closely inspect agent behavior, identify issues, and test hypotheses by intervening directly in simulations.
    *   **Allow Humans as Actors:** Enable humans to participate as integral parts of a simulation, for example, by playing the role of another agent in a social interaction, a user of a system PiaAGI is controlling, or a collaborator in a problem-solving task.
    *   **Support Collection of Human Evaluation Data:** Standardize how human judgments, ratings, and qualitative feedback on agent performance are collected during simulations for later analysis (e.g., by PiaAVT).

## 2. Roles for Human Interactors

A human participating in a PiaSE simulation via the HITL interface could assume one or more of the following roles:

*   **Tutor/Mentor:**
    *   Provides direct textual or structured feedback to the PiaAGI agent (e.g., "Good job exploring that area!", "That action was incorrect because it missed resource X.").
    *   Offers hints, suggestions, or strategic advice to the agent (e.g., "Try using the 'examine' command on the strange device.").
    *   Can demonstrate correct actions or sequences of actions, which the agent might observe and learn from.
    *   Has controls to pause, step through, and (conceptually, if supported by the environment and agent) rewind parts of the simulation to create "teachable moments."
*   **Evaluator:**
    *   Rates agent actions, decisions, outcomes, or overall behavior against predefined criteria or rubrics (e.g., on scales of effectiveness, safety, ethicality, coherence).
    *   Provides qualitative comments, annotations, or justifications for their ratings.
    *   Can flag critical incidents, unexpected behaviors, or potential ethical concerns for later review.
*   **Simulated User/Agent (Role-Player):**
    *   Takes on the role of a user interacting with the PiaAGI agent, for instance, in a simulated customer service scenario or a collaborative task.
    *   Acts as another intelligent agent in a multi-agent simulation, providing naturalistic, unscripted responses and actions that challenge or collaborate with the PiaAGI agent (e.g., in the `SocialDialogueSandbox`).
*   **Environment Controller/Oracle:**
    *   Can manually trigger specific environmental events or changes (e.g., "introduce a sudden obstacle," "make a resource available").
    *   Can directly modify parts of the environment state if needed for a specific experimental setup.
    *   Can act as an "oracle" by answering agent queries that are beyond the environment's autonomous knowledge or sensing capabilities (e.g., agent asks "What is the historical significance of this object?", human provides the answer).

## 3. Core HITL System Components (Conceptual)

The HITL system would involve components both within and external to the main PiaSE engine:

*   **`HITLInteractionManager` (Likely a module within the PiaSE `BasicSimulationEngine` or a closely integrated service):**
    *   **Responsibilities:**
        *   Manages network connections to one or more `HumanInterfaceClient`(s).
        *   Receives input data from these clients.
        *   Validates and routes human inputs to the appropriate target within the simulation (e.g., a specific agent, the environment, or the Dynamic Scenario Engine).
        *   Formats and sends relevant simulation data (agent perceptions, actions, environment state updates) to connected clients for display.
        *   Handles synchronization issues, such as pausing the simulation while waiting for human input if required by the interaction mode, or managing message queues if interactions are asynchronous.
*   **`HumanInterfaceClient` (External to PiaSE Engine, could be a standalone application or part of the PiaSE WebApp):**
    *   **Responsibilities:**
        *   Provides the actual user interface (graphical, web-based, or command-line) that the human uses to interact with the simulation.
        *   Displays simulation state information, agent perceptions, chosen actions, dialogue histories, etc., in a human-readable format.
        *   Provides input fields, buttons, forms, and other controls for the human to compose and send their interventions, feedback, or actions.
        *   Communicates with the `HITLInteractionManager` via defined API endpoints.
*   **`HITL_API_Endpoints` (Conceptual, exposed by the PiaSE Engine or `HITLInteractionManager`):**
    *   A set of network endpoints (e.g., using WebSockets for real-time bidirectional communication, or REST APIs for less frequent interactions) that the `HumanInterfaceClient` uses to connect and exchange data.
    *   **Example Endpoints:**
        *   `POST /hitl/input/agent/{agent_id}` (Data: input content, input type e.g., hint, command, feedback)
        *   `POST /hitl/input/environment` (Data: modification command, parameters)
        *   `GET /hitl/simulation_view/{agent_id}` (Params: display_config; Returns: formatted data for display)
        *   `POST /hitl/simulation/pause`
        *   `POST /hitl/simulation/resume`
        *   `POST /hitl/simulation/step`
        *   `POST /hitl/evaluation/submit/{agent_id}` (Data: evaluation scores, comments)
        *   `WS /hitl/stream/{agent_id}` (For continuous data streaming to the client)

## 4. PiaSE API Extensions for HITL

To properly integrate HITL capabilities, some existing PiaSE interfaces might need consideration for extensions:

*   **`AgentInterface` Considerations:**
    *   The existing `perceive(observation: PerceptionData, event: Optional[PiaSEEvent] = None)` method is a natural way to deliver many types of human input to the agent. The `HITLInteractionManager` can package human inputs (hints, feedback, user utterances) as `PiaSEEvent` objects.
        *   Example: `PiaSEEvent(event_type="HUMAN_FEEDBACK", data={"text": "That was a good approach to finding wood.", "rating": "positive"}, target_id=agent.get_id())`
        *   Example: `PiaSEEvent(event_type="HUMAN_USER_UTTERANCE", data={"text": "Can you tell me about your available tools?"}, source_id="human_user_1", target_id=agent.get_id())`
    *   A new optional method like `agent.handle_direct_human_command(command_data: Dict)` could be introduced for more explicit, potentially privileged interventions by a human tutor (e.g., forcing the agent to adopt a specific goal). However, routing through events is generally cleaner and more aligned with how agents perceive other stimuli.

*   **`Environment` Interface Considerations:**
    *   A new method like `environment.apply_external_intervention(intervention_data: Dict) -> ActionResult` could be added. This would allow humans in the "Environment Controller/Oracle" role to directly modify the environment state or trigger events.
        *   Example `intervention_data`: `{"action": "spawn_item", "item_type": "health_potion", "location": [x,y]}`
        *   Example `intervention_data`: `{"action": "answer_oracle_query", "query_id": "q123", "answer_text": "This artifact is from the 3rd era."}`

*   **`BasicSimulationEngine` Modifications:**
    *   Needs to instantiate and manage the `HITLInteractionManager`.
    *   Must include logic to pause the simulation if a human input is pending and the mode is synchronous, and resume upon receipt or timeout.
    *   Requires a mechanism to periodically (or on-demand) serialize and send relevant parts of the simulation state to connected `HumanInterfaceClient`(s). This should be configurable to avoid overwhelming the human or the network.

## 5. Data Flow Examples for HITL Roles

*   **Human as Tutor providing a hint to PiaAGI:**
    1.  Human types a hint (e.g., "Try looking in the blue container.") into their `HumanInterfaceClient`.
    2.  The Client formats this as a JSON payload (e.g., `{"type": "HINT", "agent_id": "pia_agent_main", "content": "Try looking in the blue container."}`) and sends it to an `HITL_API_Endpoints` like `POST /hitl/input/agent/pia_agent_main`.
    3.  The `HITLInteractionManager` receives this, validates it, and creates a `PiaSEEvent` (e.g., `event_type="HUMAN_HINT", data={"text": "Try looking in the blue container."}, target_id="pia_agent_main"`).
    4.  The `BasicSimulationEngine`'s `post_event()` method (or a similar distribution mechanism) ensures this event is passed to the `pia_agent_main`'s `perceive()` method during its next perception phase.

*   **Human as Evaluator rating an agent's action:**
    1.  The PiaSE simulation progresses. The `HumanInterfaceClient` displays the PiaAGI agent's last action (e.g., "Crafted wooden_axe") and its immediate outcome (e.g., "Success, wooden_axe added to inventory").
    2.  The human selects a rating (e.g., 4/5 stars) and types a comment ("Good use of resources, but took a bit long") in the Client.
    3.  The Client sends this evaluation data (e.g., `{"agent_id": "pia_agent_main", "action_id": "action_789", "rating": 4, "comment": "..."}`) to an endpoint like `POST /hitl/evaluation/submit/pia_agent_main`.
    4.  The `HITLInteractionManager` receives this data. It might log this evaluation directly (e.g., to a database that PiaAVT can access) and could also optionally inform the agent via a `PiaSEEvent` if direct feedback is part of the current learning scenario.

*   **Human as Simulated User in a Dialogue (e.g., with PiaAGI in `SocialDialogueSandbox`):**
    1.  PiaAGI agent performs a "speak" action. The `ActionCommand` is processed by the `SocialDialogueSandbox`. The environment updates its state, and the utterance is sent via the `HITLInteractionManager` to the `HumanInterfaceClient` for display to the human user.
    2.  The human (acting as another character) types their reply into the `HumanInterfaceClient`.
    3.  The Client sends the human's utterance (e.g. `{"action_type": "speak", "parameters": {"utterance": "Hello Pia, how are you today?"}, "acting_agent_id": "human_character_1"}`) to `POST /hitl/input/environment` (if the human is treated as an external entity acting upon the environment) or a specific agent endpoint.
    4.  The `SocialDialogueSandbox` processes this "speak" action from the human character. This utterance then becomes part of the `PerceptionData` for the PiaAGI agent in the next step.

## 6. User Interface (UI) Considerations for `HumanInterfaceClient`

The `HumanInterfaceClient` is critical for effective HITL interaction. Key features would include:

*   **Simulation State Display:** Clear visualization of the relevant environment state (e.g., a map for `GridWorld`, text log for `TextBasedRoom`, character statuses for `SocialDialogueSandbox`).
*   **Agent Data Display:** Presentation of the PiaAGI agent's current (or recent) perceptions, internal state summaries (if available and appropriate), chosen action, and the outcome of that action.
*   **Input Areas:**
    *   Text boxes for sending messages, hints, or commands.
    *   Structured forms for submitting evaluations or triggering specific events.
    *   Potentially, graphical tools for demonstrating paths or highlighting areas in a visual environment.
*   **Simulation Controls:** Buttons/commands to pause, resume, advance by one step, and possibly change simulation speed.
*   **(Advanced) Multi-Agent Support:** If multiple PiaAGI agents or human-controlled entities are in the simulation, the UI should allow the human to select which entity they are currently focused on or interacting with/as.
*   **Role-Specific Views:** The UI might adapt its layout and available tools based on the role the human has assumed (Tutor, Evaluator, Role-Player).

## 7. Challenges and Future Considerations

*   **Synchronization:** Effectively synchronizing simulation time (which can be very fast) with human interaction time (which is much slower) is a major challenge. Modes for mandatory pauses vs. asynchronous input will be needed.
*   **UI/UX Design:** Designing UIs that are informative but not overwhelming, and that allow for efficient yet expressive human input, is complex.
*   **Multiple Human Interactors:** Supporting scenarios with multiple humans interacting simultaneously (e.g., a team of evaluators, or multiple humans role-playing in a social simulation) adds significant complexity to the `HITLInteractionManager` and API.
*   **Protocol Definition:** Clear, versioned protocols for data exchange between the `HumanInterfaceClient` and the PiaSE engine are essential for modularity and future updates.
*   **Data Integration:** Ensuring that data collected via HITL (feedback, evaluations, human actions) is seamlessly logged and integrated into PiaAVT for comprehensive analysis and into the agent's learning loops (if applicable) is crucial.
*   **Cognitive Load on Humans:** Participating in HITL can be demanding. The system should be designed to minimize unnecessary cognitive load on human users.
*   **Security/Access Control:** If PiaSE is networked, appropriate security measures for HITL endpoints would be necessary.
