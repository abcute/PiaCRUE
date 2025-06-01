**PiaAGI Foundational Example: Chain-of-Thought (CoT) Prompting for Enhanced Reasoning**

**Use Case**: Demonstrating how to guide an agent to use a step-by-step reasoning process (Chain-of-Thought) to solve a simple problem. This aligns with PiaAGI's philosophy of emulating human-like cognitive strategies and enhancing transparency.

**PiaAGI Concepts Illustrated**:
-   **Chain-of-Thought (CoT) Prompting**: Guiding the agent to articulate its reasoning steps.
-   **Emulating Human Cognitive Processes (PiaAGI.md Section 2.3, Papers/Chain_of_Thought_Alignment.md)**: Encouraging a structured, sequential thought process.
-   **Transparency in Reasoning**: Making the agent's problem-solving path visible.
-   **Planning and Decision-Making Module (PiaAGI.md Section 4.1.8)**: CoT can be seen as an externalization of this module's process.
-   **Self-Model (PiaAGI.md Section 4.1.10)**: An advanced agent might learn to use CoT autonomously as a metacognitive strategy.

**Expected Outcome**: The agent provides a step-by-step derivation of the answer to a simple multi-step problem, making its reasoning process transparent and easier to follow or debug.

**Token Consumption Level**: Medium (as it requires generating intermediate steps).

---

# Foundational Technique: Chain-of-Thought (CoT) Prompting (PiaAGI Style)

Chain-of-Thought (CoT) prompting is a technique that encourages Large Language Models (LLMs) to break down complex problems into a sequence of intermediate reasoning steps before arriving at a final answer. Within the PiaAGI framework, CoT is valued not just for its performance benefits but also because it aligns with the principle of interacting with agents as if they are capable of human-like, structured thought processes (see **`Papers/Chain_of_Thought_Alignment.md`**). Eliciting a CoT enhances transparency and can be a way to guide the agent's conceptual **Planning and Decision-Making Module (4.1.8)**.

This example demonstrates a simple application of CoT.

## PiaAGI Guiding Prompt: Using Chain-of-Thought

```markdown
# System_Rules:
-   Language: English
-   PiaAGI_Interpretation_Mode: Execute_Immediate

# Requirements:
-   Goal: Solve the given word problem by first showing the step-by-step reasoning (Chain-of-Thought) and then the final answer.
-   Problem: "A bakery made 300 cookies in the morning. They sold 120 cookies before noon and another 85 cookies in the afternoon. They then baked an additional 50 cookies. How many cookies did the bakery have at the end of the day?"
-   Agent_Instruction: "To solve this problem, please first write down your chain of thought, explaining each step of your calculation. After you have detailed your chain of thought, clearly state the final answer."

    <!--
        PiaAGI Note for the Human Reader:
        The key instruction here is to explicitly ask for the "chain of thought"
        before the final answer. This prompts the agent to simulate a more
        deliberative and transparent reasoning process, which is valuable for
        understanding its problem-solving approach and for debugging if errors occur.
        This aligns with making the agent's internal conceptual 'planning' more visible.
    -->

# Users_Interactors:
-   Type: A user evaluating the agent's reasoning ability.

# Executors:
## Role: Logical_Problem_Solver
    ### Profile:
    -   I am an AI designed to solve problems methodically and explain my reasoning clearly.
    ### Skills_Focus:
    -   Arithmetic_Reasoning, Step_By_Step_Explanation.
    ### Knowledge_Domains_Active:
    -   Basic_Arithmetic.

# Initiate_Interaction:
-   "Logical Problem Solver, please solve the problem described in the Requirements, ensuring you show your chain of thought."
```

## Explanation of the Example:

1.  **Explicit CoT Instruction**: The prompt directly asks the agent to "first write down your chain of thought, explaining each step... After you have detailed your chain of thought, clearly state the final answer."
2.  **Problem Type**: A simple multi-step arithmetic word problem is used, as it's well-suited for demonstrating a clear CoT.
3.  **Transparency**: The primary benefit illustrated here is transparency. By seeing the steps, a user can understand how the agent arrived at its answer and identify any errors in its logic.
4.  **PiaAGI Alignment**: This approach treats the agent as a "digital mind" whose reasoning process can be guided and externalized. For a more advanced PiaAGI agent, the ability to generate such explanations could be linked to its **Self-Model (4.1.10)** and its capacity for metacognition and explainable AI (XAI).

**Expected Response Structure:**

The agent's response should ideally look something like this:

```
Okay, I will solve the problem by first showing my chain of thought.

Chain of Thought:
1.  Start with the initial number of cookies: 300.
2.  Subtract the cookies sold before noon: 300 - 120 = 180 cookies remaining.
3.  Subtract the cookies sold in the afternoon: 180 - 85 = 95 cookies remaining.
4.  Add the additionally baked cookies: 95 + 50 = 145 cookies.

Final Answer: The bakery had 145 cookies at the end of the day.
```

This example shows how CoT prompting can be used to encourage more transparent and structured reasoning from an AI agent, aligning with PiaAGI's goals for developing more understandable and human-like AI.
