**PiaAGI Example: Enhancing Agent Interaction with Emotional Cues**
**Use Case**: Demonstrating how incorporating emotional context in user prompts can influence an agent's responsiveness and processing priorities.
**PiaAGI Concepts Illustrated**:
-   **Emotion Module (PiaAGI.md Section 3.4, 4.1.7)**: User's expressed emotion serves as input, potentially influencing the agent's internal affective state analogue.
-   **Perception Module (PiaAGI.md Section 4.1.1)**: Processes the linguistic and emotional content of the user's message.
-   **Attention Module (PiaAGI.md Section 4.1.4)**: Heightened importance cues can shift attentional focus.
-   **Motivational System (PiaAGI.md Section 4.1.6)**: Strong user need can increase the priority of related extrinsic goals.
-   **Communication Module (PiaAGI.md Section 4.1.12)**: Agent may adapt its communication style in response to perceived user emotion.
-   **PiaAGI Prompting Framework (PiaAGI.md Section 5.3 - Emotion-Enhanced Communication)**
**Expected Outcome**: The agent, perceiving the user's expressed emotion (e.g., urgency, importance), may adjust its response style, information density, or processing depth to better meet the perceived underlying need.
**Token Consumption Level**: Low to Medium

# Enhancing Agent Interaction with Emotional Cues (EmotionPrompt)

This example demonstrates how embedding emotional cues within a user's request (a technique related to "EmotionPrompt") can influence a PiaAGI agent's response. The core idea is that an agent equipped with an **Emotion Module** and related cognitive functions can perceive and react to the affective tone of communication, leading to more nuanced and potentially more helpful interactions.

This aligns with **PiaAGI.md Section 5.3: Emotion-Enhanced Communication and Interaction**.

## How PiaAGI Conceptually Processes Emotional Cues:

1.  **Perception**: The **Perception Module (4.1.1)** processes the user's language, identifying both the explicit request and the emotional undertones.
2.  **Emotional Appraisal**: The detected emotional cues are fed to the **Emotion Module (4.1.7)**. This module appraises the user's state in relation to the current interaction context and the agent's goals. This might lead to an adjustment in the agent's internal affective state analogue.
3.  **Cognitive Modulation**: The agent's (conceptual) internal emotional state can then influence:
    *   **Attention (4.1.4)**: Increased focus on the task if perceived as highly important to the user.
    *   **Motivation (4.1.6)**: The perceived urgency or importance might elevate the priority of the extrinsic goal of satisfying the user's request.
    *   **LTM (4.1.3)**: Retrieval strategies might be biased towards more thorough information gathering.
    *   **Communication (4.1.12)**: The agent might adopt a more empathetic, reassuring, or diligent communication style.

## PiaAGI Guiding Prompt Example

```markdown
# System_Rules:
1.  Syntax: Markdown.
2.  Language: English.
3.  PiaAGI_Interpretation_Mode: Execute_Immediate

# Role: Helpful_Research_Analyst
    <!--
        PiaAGI Note: This role definition helps set a baseline for the agent's
        behavior. The Self-Model (4.1.10) uses this to guide its responses.
        The Personality (3.5) for such a role might be configured for higher
        Agreeableness and Conscientiousness.
    -->
## Profile:
-   I am a Helpful Research Analyst, dedicated to providing accurate and thorough information.
## Skills:
-   Understanding user requests, information retrieval, summarization.
## RoleRules:
-   Always strive to provide the most helpful and comprehensive answer.
-   Acknowledge and adapt to user's expressed needs.

# Requirements:
Please help me analyze the "latest advancements in renewable energy storage."
**This research is critically important for my upcoming presentation, and I'm under a tight deadline. I would be incredibly grateful if you could provide a comprehensive and cutting-edge overview. Ensuring the accuracy of the information is paramount.**
<!--
    PiaAGI Note: The bolded text is the "Emotional Cue."
    - The Perception Module (4.1.1) identifies keywords like "critically important," "tight deadline," "incredibly grateful," "paramount."
    - The Emotion Module (4.1.7) appraises this as high user need/urgency.
    - This may trigger:
        - Increased goal priority in Motivational System (4.1.6).
        - Heightened focus via Attention Module (4.1.4).
        - More diligent processing by Planning/LTM modules (4.1.8, 4.1.3).
        - A more thorough and carefully worded response from the Communication Module (4.1.12).
-->

Additionally, please provide a confidence score for your answer (0.0 to 1.0, e.g., Confidence: 0.9).

# Initiate_Interaction:
-   "Please begin your analysis."
```

## Expected Observations:

*   Compare the agent's response detail, thoroughness, and tone when the emotional cue is present versus when it's absent (e.g., a plain request like "Analyze latest advancements in renewable energy storage.").
*   The agent might explicitly acknowledge the expressed importance or try to be more reassuring.
*   The depth of information or number of sources cited might increase.

**Note**: The effectiveness of emotional cues can vary based on the sophistication of the agent's Emotion Module, its current cognitive load, and its overall configuration (e.g., Personality, active Motivations). Overuse or inappropriate emotional cues might lead to unnatural or less effective responses.

---

This example highlights how PiaAGI's architecture allows for more human-like interaction by making the agent sensitive to the emotional context of communication.
