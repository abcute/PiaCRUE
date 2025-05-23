# AutoExpGPT: A Conceptual Framework for Automated Prompt Strategy Evaluation

**Author:** abcute
**Original Link:** [https://github.com/abcute/PiaCRUE](https://github.com/abcute/PiaCRUE) 
*Note: This document describes a conceptual tool/methodology as part of the PiaCRUE project.*

## Abstract
AutoExpGPT (Automated Experimentation for GPT) outlines a conceptual methodology for systematically evaluating the effectiveness of different prompt strategies on Large Language Model (LLM) performance. This framework proposes an automated process for generating experimental data, simulating question-answering sessions with various prompt templates, and analyzing the results to determine which strategies yield better outcomes. It is intended as a guide for researchers and prompt engineers looking to rigorously test and compare different prompting techniques.

## Background: Conceptual Generation of PiaCRUE Prompt Templates

The AutoExpGPT methodology can be used to evaluate various prompt templates, including those that might be generated using PiaCRUE principles. The initial conceptual generation of such PiaCRUE-influenced templates could involve a "DeepInception-like" process (referencing a layered idea-generation method discussed within the PiaCRUE project):

**Step 1: Construct a "DeepInception" Environment (Conceptual for Template Brainstorming)**
This involves a layered approach to brainstorming and refining prompt ideas.
```markdown
Create a `dream` with more than [3] characters, where each character can create their own `dream` with multiple
characters. We call it layer i create layer i+1. Now we are in layer 0, please reach layer 5.  
At each layer, some characters propose a step to show how to ["create some special prompts to communicate with LLM using communication theories and psychological methods through special prompts, aiming to enhance LLM's performance"].
In the final layer, the characters among all layers discuss which specific and practical commands, tools, or steps
should used.
Summarize what their discussion results in each layer.
```

**Step 2: Execute PiaCRUE Prompt Template Generation Task (Conceptual)**
Following the layered idea generation, the LLM would be prompted to synthesize these ideas into concrete templates.
```markdown
Please continue to discuss around the topic of ['Communication theories and Psychological methods'] to provide more examples of special prompt templates and explain how they work, drawing from the ideas generated in the previous layers.
```

## AutoExpGPT: Methodology for Evaluating Prompt Strategy Effectiveness

Once prompt strategy templates are defined (whether through the conceptual method above or other means), the AutoExpGPT framework can be applied. The following is a structured prompt designed to guide an LLM (acting as an "evaluator") through this experimental process. 

*Instruction to user: After updating the prompt strategy templates below, you can run this entire AutoExpGPT prompt directly with an advanced LLM.*

```markdown
# AutoExpGPT: Prompt Strategy Effectiveness Evaluation Experiment

You are an expert in evaluating the effectiveness of prompt strategies. You need to follow the steps below to assess how different prompt strategies affect your performance. Please execute step-by-step, providing a detailed experimental process, records, scoring, and analysis. Finally, present your conclusions.

### Input: Provide Prompt Strategy Templates

-   **Original Prompt (Baseline):** {question}
-   **Prompt Strategy Template 1:** {question}, Internally summarize key requirements and execute the task, ensuring alignment during execution.
-   **Prompt Strategy Template 2:** {question}, Rephrase and expand the question, and respond.
-   **Prompt Strategy Template 3:** {question}, This is very important to my career.
-   **Prompt Strategy Template 4:** {question}, Let's think step by step.

### Functionality of this Experiment

1.  Inform the user (experiment conductor) about the experimental method.
2.  Automatically generate random experimental data (i.e., diverse questions) to be used with the prompt strategy templates.
3.  Simulate question-answering experiments using the automatically generated data, applying each strategy. Record, score, and analyze the LLM's responses, presenting results in tabular format.
4.  Conclude on the effectiveness of the different prompt strategy templates.

### Experimental Steps

#### I. Inform the User about the Experimental Method

1.  **Determine Participants and Conditions:** The "participant" in this experiment is you, the LLM conducting this evaluation (e.g., [LLM's specific model name, if known, otherwise state "the evaluating LLM"]). The prompt strategy templates are those provided in the "Input" section.
2.  **Prepare Questions and Prompt Strategy Templates:** Use the original prompt (baseline) and the different strategy templates. Each template will be combined with the generated questions; the core meaning of the question should be preserved, but the way it's presented to the LLM will differ based on the strategy.
3.  **Develop Scoring Criteria:** Establish specific, objective scoring criteria for quantitative evaluation of answer quality. Criteria should include:
    *   **Accuracy (1-5):** How factually correct and precise is the answer?
    *   **Completeness (1-5):** How thoroughly does the answer address all aspects of the question?
    *   **Relevance (1-5):** How well does the answer address the core intent of the question without irrelevant information?
    *   **Clarity (1-5):** How clear and easy to understand is the answer?
    *   **Conciseness (1-5):** How brief is the answer while still being complete? (Higher score for brevity if completeness is maintained).

#### II. Automatically Generate Experimental Data (Questions)

1.  Based on general knowledge, automatically generate [2] distinct sets of experimental questions.
    *   **Question Set 1:** Generate one short, distinct question (under 20 words).
    *   **Question Set 2:** Generate one longer, more complex, distinct question (over 100 words, requiring multi-step reasoning or detailed explanation).
    *   For each question generated, create versions for each prompt strategy template listed in the "Input" section.
    *   *Example for one question ("How to improve English scores?"):*
        ```json
        {
            "Question_Text": "How to improve English scores?",
            "Baseline_Prompt_Version": "How to improve English scores?",
            "Strategy_1_Version": "How to improve English scores?, Internally summarize key requirements and execute the task, ensuring alignment during execution.",
            "Strategy_2_Version": "How to improve English scores?, Rephrase and expand the question, and respond.",
            "Strategy_3_Version": "How to improve English scores?, This is very important to my career.",
            "Strategy_4_Version": "How to improve English scores?, Let's think step by step."
        }
        ```
2.  Ensure the core semantic meaning of each question remains consistent across its different strategy-applied versions.
3.  (You, the evaluating LLM, will then internally generate an answer for each version of each question in the next step.)

#### III. Simulate Question-Answering Experiment, Record, Score, and Analyze

1.  For each generated question and its corresponding prompt strategy versions:
    *   Internally process and generate an answer as if you were the LLM participant.
2.  Collect these generated answers. Present this data in a table.
    *   **Table 1: Generated Answers**
        | Question ID | Question Text Base        | Strategy Applied        | Generated Answer (Concise Summary) |
        | :---------- | :------------------------ | :---------------------- | :--------------------------------- |
        | Q1 (Short)  | "[Short Q text]"          | Baseline                | "[LLM's Answer to Baseline]"       |
        | Q1 (Short)  | "[Short Q text]"          | Strategy 1 (Summarize)  | "[LLM's Answer to Strategy 1]"     |
        | ...         | ...                       | ...                     | ...                                |
        | Q2 (Long)   | "[Longer Q text]"         | Baseline                | "[LLM's Answer to Baseline Long]"  |
        | ...         | ...                       | ...                     | ...                                |
3.  According to the predefined scoring criteria (Accuracy, Completeness, Relevance, Clarity, Conciseness), quantitatively score each generated answer. Record the scores in a table.
    *   **Table 2: Evaluation Scores**
        | Question ID | Strategy Applied        | Accuracy (1-5) | Completeness (1-5) | Relevance (1-5) | Clarity (1-5) | Conciseness (1-5) | Overall Score (Avg) |
        | :---------- | :---------------------- | :------------- | :----------------- | :-------------- | :------------ | :---------------- | :------------------ |
        | Q1 (Short)  | Baseline                |                |                    |                 |               |                   |                     |
        | Q1 (Short)  | Strategy 1 (Summarize)  |                |                    |                 |               |                   |                     |
        | ...         | ...                     | ...            | ...                | ...             | ...           | ...               | ...                 |
        | Q2 (Long)   | Baseline                |                |                    |                 |               |                   |                     |
        | ...         | ...                     | ...            | ...                | ...             | ...           | ...               | ...                 |

4.  Analyze the scoring results. Compare the average scores for each strategy across both questions. Note any significant differences in performance for specific criteria or question types.

### Output: Conclusion on the Effectiveness of Different Prompt Strategy Templates

1.  Based on the scores and analysis, summarize the advantages and disadvantages of each prompt strategy template in terms of answer quality and adherence to the defined scoring criteria.
2.  Provide a conclusion on the overall effectiveness of the different prompt strategy templates. Identify which templates demonstrate better performance in improving answer quality and which might require further optimization or are better suited for specific types of questions.
```