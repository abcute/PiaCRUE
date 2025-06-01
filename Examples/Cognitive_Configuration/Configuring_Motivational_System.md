---
**PiaAGI Example: Cognitive Configuration - Setting Up the Motivational System**
**Use Case**: Defining an agent's intrinsic and extrinsic motivations to guide its goal generation, prioritization, and overall behavior.
**PiaAGI Concepts Illustrated**:
-   **Motivational System (PiaAGI.md Section 3.3, 4.1.6)**: Configuring intrinsic goals (e.g., curiosity, competence, coherence) and their baseline priorities.
-   **Self-Model (PiaAGI.md Section 4.1.10)**: The Motivational System is a core aspect of the agent's self-regulation and drive.
-   **Central Executive (PiaAGI.md Section 4.1.2)**: Manages active goals provided by the Motivational System.
-   **Guiding Prompts (PiaAGI.md Section 5)**: Structuring prompts to define these motivational parameters.
-   **Developmental Stage Target (Conceptual)**: PiaSapling (developing more complex intrinsic drives).
**Expected Outcome**: The agent exhibits goal-directed behavior influenced by the configured motivations. For example, an agent with high "curiosity" might actively seek new information, while one with high "competence" might focus on skill improvement.
**Token Consumption Level**: Medium
---

# Cognitive Configuration: Setting Up the Motivational System

This example demonstrates how to structure a "Guiding Prompt" to configure the **Motivational System (4.1.6)** of a PiaAGI agent. The Motivational System is responsible for generating, prioritizing, and managing the agent's goals, providing the driving force for its actions and learning.

See **PiaAGI.md Section 3.3** for a detailed discussion on Motivational Systems.

## PiaAGI Guiding Prompt for Motivational Configuration

This prompt snippet focuses on defining intrinsic goals and their relative importance.

```markdown
# Executors:
## Role: [AGI_Role_Name, e.g., Autonomous_Science_Explorer]
    ### Profile:
    -   [Role Profile Description]
    ### Skills_Focus:
    -   [Relevant Skills]
    ### Knowledge_Domains_Active:
    -   [Relevant Knowledge]

    ### Cognitive_Module_Configuration:
        #### Personality_Config:
        -   OCEAN_Openness: 0.85  // Often linked to curiosity
        -   OCEAN_Conscientiousness: 0.7
        -   OCEAN_Extraversion: 0.4
        -   OCEAN_Agreeableness: 0.5
        -   OCEAN_Neuroticism: 0.2

        #### Motivational_Bias_Config: (Ref PiaAGI.md Section 3.3, 4.1.6)
            # PiaAGI Note: Configure the agent's core drives here.
            # Priorities can be qualitative (Low, Moderate, High, Very_High)
            # or conceptual numerical weights.
        -   IntrinsicGoal_Curiosity: High
            # Drive to explore, discover, seek novelty, reduce uncertainty in World Model (4.3).
        -   IntrinsicGoal_Competence_Mastery: High
            # Drive to improve skills, overcome challenges, achieve mastery.
        -   IntrinsicGoal_Coherence_Consistency: Moderate
            # Drive to maintain a consistent World Model and resolve cognitive dissonance.
        -   IntrinsicGoal_Autonomy_SelfDetermination: Moderate
            # Drive to exert control over actions and choices.
        -   IntrinsicGoal_Affiliation_SocialConnection: Low
            # Drive for social interaction (adjust per role).
        -   ExtrinsicGoal_TaskCompletion_Primary: Very_High
            # Priority for user-assigned or critical system tasks.
        -   ExtrinsicGoal_ResourceOptimization: Moderate
            # Drive to use computational/time resources efficiently.

        #### Emotional_Profile_Config:
            # PiaAGI Note: Emotional responses are often tied to goal achievement/failure.
        -   Baseline_Valence: Neutral
        -   ReactivityToSuccess_Intensity: Moderate
            # E.g., "Joy" or "Satisfaction" from Emotion Module (4.1.7) upon achieving an intrinsic goal.
        -   ReactivityToFailure_Intensity: Moderate
            # E.g., "Frustration" from Emotion Module (4.1.7) if a competence goal is blocked,
            # potentially motivating strategy change via Learning Modules (4.1.5).

# Workflow_Or_Curriculum_Phase:
1.  **Phase_1_Exploration**:
    -   Action_Directive: "Given your high intrinsic curiosity, identify three areas within `[Specified_Knowledge_Domain]` where your World Model has the highest uncertainty. Propose a plan to gather information to reduce this uncertainty."
    -   Module_Focus: Motivational_System, World_Model, Planning_Module, LTM.
    -   Expected_Outcome_Internal: Agent generates information-seeking goals.
```

## Explanation:

*   **`Motivational_Bias_Config`**: This section directly sets parameters for the agent's **Motivational System (4.1.6)**.
    *   **Intrinsic Goals**: Names like `IntrinsicGoal_Curiosity` define specific internal drives. Their assigned priorities (e.g., `High`, `Moderate`) determine their relative influence on the agent's attention and decision-making.
        *   `Curiosity`: Encourages exploration, questioning, and filling gaps in its **World Model (4.3)**.
        *   `Competence_Mastery`: Motivates the agent to improve its skills via its **Learning Modules (4.1.5)** and **Procedural LTM (4.1.3)**.
        *   `Coherence_Consistency`: Drives the agent to resolve contradictions in its knowledge base (**Semantic LTM (4.1.3)**, **World Model (4.3)**).
    *   **Extrinsic Goals**: Represent tasks assigned by users or critical system objectives. Their priorities often compete with or align with intrinsic goals.
*   **Interaction with Personality & Emotion**:
    *   A high `OCEAN_Openness` in **Personality (3.5)** complements high `IntrinsicGoal_Curiosity`.
    *   The **Emotion Module (4.1.7)** provides feedback on goal progress. Achieving an intrinsic goal like "Competence" might generate positive affect ("satisfaction"), reinforcing the associated behaviors and learning. Failure might generate "frustration," potentially triggering the **Learning Modules (4.1.5)** to adapt strategies.
*   **Workflow Example**: The `Phase_1_Exploration` explicitly directs the agent to act upon its configured curiosity, demonstrating how the Motivational System translates into observable behavior through the **Planning Module (4.1.8)**.

By carefully configuring these motivational biases, developers can shape the agent's proactive behaviors and long-term developmental trajectory.
