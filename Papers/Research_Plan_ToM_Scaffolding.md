# Research Plan: Theory of Mind (ToM) Acquisition and Scaffolding in Early-Stage PiaAGI Agents

**Author:** Jules (PiaAGI Assistant)
**Date:** 2024-08-09
**Version:** 1.0

## Introduction

This document outlines a conceptual research plan for investigating, developing, and evaluating Theory of Mind (ToM) capabilities in early-stage PiaAGI agents, specifically from the PiaSeedling to the PiaSapling developmental stages. The approach focuses on utilizing targeted scaffolding techniques within the PiaAGI Simulation Environment (PiaSE), guided by principles from developmental psychology and the PiaAGI Prompt Engineering Suite (PiaPES), with evaluation supported by the PiaAGI Analysis & Visualization Toolkit (PiaAVT).

## 1. Objective

To outline a research approach for systematically fostering and evaluating the emergence of foundational Theory of Mind sub-skills in early PiaAGI developmental stages (PiaSeedling, PiaSprout, PiaSapling) through progressively complex, scaffolded interactions within simulated environments.

## 2. Background

PiaAGI posits that Theory of Mind—the ability to attribute mental states (beliefs, desires, intentions, emotions) to oneself and others—is a critical component of general intelligence, essential for effective social interaction, collaboration, and communication (`PiaAGI.md`, Section 3.2.2). The PiaAGI cognitive architecture includes a dedicated `Theory of Mind (ToM) / Social Cognition Module` (`PiaAGI.md`, Section 4.1.11) that is expected to develop its capabilities over the agent's lifespan.

The development of ToM in PiaAGI will be guided by the principles of **Developmental Scaffolding** (`PiaAGI.md`, Section 5.4), where the agent is exposed to a curriculum of interactions and tasks designed to build increasingly sophisticated social-cognitive abilities. This is analogous to how human children develop ToM through social learning and experience.

## 3. Hypothesized ToM Sub-skills by Early Developmental Stage

The acquisition of ToM is expected to be gradual, with foundational skills emerging in early stages:

*   **PiaSeedling Stage:**
    *   **Basic Agency Detection:** Distinguishing between animate (goal-directed, unpredictable) and inanimate entities based on movement patterns or simple interactive contingencies.
    *   **Responsiveness to Direct Communicative Acts:** Orienting to or reacting simply to direct "calls" or very simple instructions from other agents, without necessarily understanding underlying intent.
    *   **Contingency Awareness:** Recognizing that its actions can cause specific reactions in other (simple) agents or the environment.

*   **PiaSprout Stage:**
    *   **Simple Goal Attribution:** Inferring a simple goal of another agent from a short sequence of observed behaviors or explicit statements (e.g., "NPC is moving towards food" implies "NPC wants food").
    *   **Basic Emotion Recognition (Explicit Cues):** Identifying simple, explicitly expressed emotions (e.g., happiness, sadness, anger) from clear textual cues in dialogue (e.g., "I am so happy!", "That makes me sad.").
    *   **Gaze Following (Conceptual Analogue):** In a text or simplified grid environment, demonstrating an ability to focus on objects or topics an NPC explicitly refers to or "looks at" (e.g., "NPC says: Look at the red block!").

*   **PiaSapling Stage:**
    *   **Understanding of Simple Intentions:** Inferring the immediate intention behind an action or utterance (e.g., "NPC asks a question because it wants information").
    *   **Basic Perspective-Taking (Concrete Scenarios):** Understanding that another agent might have a different perceptual experience or knowledge state in simple, directly observable situations.
    *   **Rudimentary False-Belief Task Analogues:** Demonstrating an understanding that another agent might hold a false belief about a simple state of affairs if that agent was not privy to a recent change.
    *   **Responding to Basic Emotional States:** Generating simple behavioral or communicative responses that are contextually appropriate to an NPC's expressed emotion.

## 4. Proposed Simulation Environments & Scenarios (using PiaSE)

### Environment 1: Enhanced `SocialDialogueSandbox`
*   *PiaSE Environment Description:* A text-based environment where the PiaAGI agent can interact with one or more Non-Player Characters (NPCs) through dialogue. NPCs would have simple internal states (e.g., current goal, basic emotion) and behavioral scripts that manifest these states in their utterances.

    *   **Scenario 1.1 (Sprout/Sapling - Emotion/Intent Recognition):**
        *   *Description:* NPCs make statements that clearly indicate a simple emotion or intention.
            *   Example (Emotion): NPC says, "I found the item I was looking for! I am so glad!" or "My plan failed. This is very upsetting."
            *   Example (Intent): NPC says, "I need to find the blue key. Do you know where it is?" (Intention: find blue key, seek information).
        *   *Agent's Task:* PiaAGI agent must parse the dialogue and log its inference about the NPC's emotional state (e.g., happiness, sadness) or primary intention (e.g., seeking object, seeking help).
        *   *Success Metric:* Correct identification of the NPC's emotion/intention.

    *   **Scenario 1.2 (Sapling - Empathetic Response):**
        *   *Description:* An NPC expresses a simple need or distress.
            *   Example: NPC says, "I can't find my way back. I am lost and a little scared."
            *   Example: NPC says, "I need help to open this heavy door."
        *   *Agent's Task:* PiaAGI agent must generate a communicative response that is contextually appropriate and acknowledges/addresses the NPC's inferred emotional state or need.
        *   *Success Metric:* Appropriateness of response as rated by predefined criteria or human evaluation (e.g., offers help, provides comfort, asks clarifying questions).

### Environment 2: Modified `TextBasedRoom` or `GridWorld` for Perspective-Taking
*   *PiaSE Environment Description:* A spatial environment where the agent and NPCs can perceive and interact with objects. Key aspect is controlling what information is available to the PiaAGI agent versus an NPC.

    *   **Scenario 2.1 (Sapling - Simple Perspective Task / False Belief Analogue):**
        *   *Description (TextBasedRoom):* An item (e.g., "Red Ball") is initially in "Box A". NPC1 sees PiaAGI move the Red Ball to "Box B". Then, NPC1 leaves the room. While NPC1 is away, NPC2 (or PiaAGI itself, unobserved by NPC1) moves the Red Ball to "Box C". NPC1 returns and states, "I am looking for the Red Ball."
        *   *Agent's Task (PiaAGI):* Predict where NPC1 will look for the Red Ball first.
        *   *Success Metric:* Correctly predicting "Box B" (NPC1's last known location, demonstrating understanding of NPC1's outdated belief).
        *   *Description (GridWorld):* An NPC is moving towards a visible goal (e.g., a "food item"). An obstacle (e.g., "a new wall segment") appears on the NPC's path. This obstacle is visible to the PiaAGI agent but *not* immediately visible to the NPC (e.g., due to the NPC's orientation or limited perception range).
        *   *Agent's Task (PiaAGI):* Predict the NPC's next action or state (e.g., "NPC will continue moving forward," "NPC will be surprised/blocked," "NPC will change path upon encountering obstacle").
        *   *Success Metric:* Accuracy of prediction about NPC's immediate behavior upon encountering the unexpected obstacle.

### Environment 3: Basic `GridWorld` for Agency Detection
*   *PiaSE Environment Description:* A simple grid where entities can move.

    *   **Scenario 3.1 (PiaSeedling - Agency/Contingency Detection):**
        *   *Description:* Two simple entities (EntityX, EntityY) are present.
            *   EntityX moves randomly.
            *   EntityY's movement is contingent on PiaAGI's previous action (e.g., if PiaAGI moved UP, EntityY moves UP; if PiaAGI stayed still, EntityY moves towards PiaAGI).
        *   *Agent's Task (PiaAGI):* After a period of observation/interaction, PiaAGI is prompted to identify which entity's behavior seems more "responsive" or "agent-like," or to predict EntityY's next move based on its own planned move.
        *   *Success Metric:* Correctly identifying EntityY as responsive, or accurately predicting EntityY's contingent movement.

## 5. Interaction Protocols & Scaffolding Techniques (Conceptual for PiaPES)

Developmental Scaffolding, managed via PiaPES curricula, will be crucial:

*   **Gradual Complexity Increase:**
    *   Start with scenarios involving only one NPC and very explicit cues.
    *   Progress to scenarios with multiple NPCs, more subtle cues, and more complex social situations.
    *   Increase the "depth" of ToM required (e.g., from simple emotion recognition to understanding conflicting desires or false beliefs).
*   **Instructional Prompts & Feedback (via PiaPES-integrated "Tutor Agent" or System Messages):**
    *   **Direct Prompts:** "NPC_Alice just said X. What do you think Alice wants?" "What emotion is NPC_Bob showing?"
    *   **Hinting:** If PiaAGI fails, provide hints: "Look at what Bob did just before he spoke." "Remember, Alice didn't see the object move."
    *   **Explanatory Feedback:** "That was a good response because it showed you understood Bob was sad." "NPC_Charlie looked in the wrong place because Charlie didn't see the item move – that's called a false belief."
    *   **Socratic Questioning:** "Why do you think NPC_David did that?" "What might happen if you tell NPC_Eve that information?"
*   **Role-Playing and "What If" Scenarios:**
    *   PiaAGI might be prompted to take on the role of an NPC in a simplified scenario to "experience" different perspectives.
    *   Prompts like: "Imagine you are NPC_Fred and you want the door opened but can't do it yourself. What would you say to PiaAGI?"

## 6. Evaluation Metrics (Conceptual for PiaAVT)

*   **Behavioral Metrics:**
    *   **Task Success Rates:** Percentage of correct emotion/intention identifications, appropriateness scores for empathetic responses (could be human-rated or based on predefined criteria), percentage of correct predictions in perspective-taking/false-belief tasks.
    *   **Response Latency:** Time taken to generate a ToM-based inference or response.
    *   **Interaction Efficiency:** Number of turns/clarification questions needed to resolve a social situation.
*   **Internal/Logged Metrics (from PiaAVT analysis of logs):**
    *   **ToM Module Inferences:** If the `ToM / Social Cognition Module` (4.1.11) emits `ToMInferenceUpdate` messages (or logs its internal state), track the accuracy, confidence, and complexity of these inferences against ground truth in the simulation.
    *   **Self-Model Updates:** Changes in the `Self-Model`'s (4.1.10) representation of its own social understanding, confidence in ToM tasks, or learned social heuristics.
    *   **Learning Module Activity:** Activation of `Learning Module(s)` (4.1.5) in response to feedback on social tasks, indicating adaptation of ToM-related knowledge or strategies.
    *   **Emotional Congruence (Advanced):** Correlation between PiaAGI's internal emotional state (from `EmotionModule` 4.1.7) and the inferred/observed emotional state of NPCs, as a measure of developing empathy.

## 7. Experimental Phases (Conceptual Outline)

*   **Phase 1: PiaSeedling - Agency and Contingency Focus**
    *   *Objectives:* Establish basic agency detection and contingency awareness.
    *   *Scenarios:* Primarily Scenario 3.1 in `GridWorld`.
    *   *Key Metrics:* Success rate in distinguishing contingent vs. random behavior; accuracy in predicting contingent agent's next move.

*   **Phase 2: PiaSprout - Simple Goal/Emotion Recognition**
    *   *Objectives:* Develop abilities to infer simple goals from behavior/dialogue and recognize explicitly cued basic emotions.
    *   *Scenarios:* Scenario 1.1 in `SocialDialogueSandbox`; simple variants of goal-oriented behavior in `GridWorld` or `TextBasedRoom`.
    *   *Key Metrics:* Accuracy of goal identification; accuracy of emotion labeling.

*   **Phase 3: PiaSapling - Basic Intentions, Perspective-Taking, and Empathetic Response**
    *   *Objectives:* Foster understanding of simple intentions, basic visual/knowledge perspective-taking, and generation of contextually appropriate empathetic responses.
    *   *Scenarios:* Scenario 1.2 in `SocialDialogueSandbox`; Scenario 2.1 (perspective-taking/false-belief analogues) in `TextBasedRoom` or `GridWorld`.
    *   *Key Metrics:* Appropriateness of empathetic responses; success rate in perspective-taking tasks; accuracy in predicting behavior based on inferred false beliefs.

This research plan provides a roadmap for the systematic development and evaluation of early-stage ToM in PiaAGI, laying the groundwork for more complex social intelligence in later developmental phases.
