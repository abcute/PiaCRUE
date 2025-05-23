# Rephrase-and-Respond (RaR): A Method for Enhancing LLM Accuracy

**Original Source:** Gu, Quanquan; Deng, Yoeho; Zhang, Weitong; Chen, Zixiang (UCLA).
**Paper Link:** [https://arxiv.org/pdf/2311.04205.pdf](https://arxiv.org/pdf/2311.04205.pdf)
**Associated Project Page:** [https://uclaml.github.io/Rephrase-and-Respond](https://uclaml.github.io/Rephrase-and-Respond)
*Note: This document summarizes the "Rephrase-and-Respond" (RaR) prompting strategy, which aims to improve the accuracy of Large Language Model (LLM) responses by having the LLM first rephrase and expand upon the user's question.*

## Abstract
The Rephrase-and-Respond (RaR) method is a prompting strategy designed to enhance the accuracy of Large Language Models (LLMs) by instructing them to first rephrase and expand on a given question before answering. This approach, including its "One-step RaR" and "Two-step RaR" variations, helps the LLM better understand the query's nuances, leading to more precise responses. It aligns with the PiaCRUE project's PiaC principles of optimizing LLM communication by refining how queries are presented to the model.

## RaR Method and PiaC Ideology

The RaR method is an excellent application example of the PiaC (Personalized Intelligent Agent Customization) communication encoding ideas within the [PiaCRUE framework](../PiaCRUE.md). Specifically, it embodies the principle of having the AI optimize the original prompt to express it in a way the AI can better understand. This idea has various applications in everyday prompt engineering. For instance, one might solicit the AI's input when crafting a prompt:

```
Hello ChatGPT, how should I phrase my question to enable you to perform better? My question is "{question}". Please optimize my question's phrasing, provide an improved example, and then respond.
```

### One-step RaR
The core of the Rephrase-and-Respond (RaR) scheme is to have the Large Language Model rephrase and expand on the posed question to improve the accuracy of its answer. Based on this finding, researchers proposed a simple yet effective prompt: "Rephrase and expand the question, and respond" (abbreviated as RaR). This prompt directly enhances the quality of LLM responses, demonstrating a significant improvement in question processing.

![One-step RaR Diagram](../img/RaR.png)
*Caption: Diagram illustrating the One-step RaR process.*

### Two-step RaR
The research team also proposed a variation of RaR called "Two-step RaR" to fully leverage the capability of large models like GPT-4 to rephrase questions. This method follows two steps:
1.  First, for a given question, a dedicated "Rephrasing LLM" is used to generate a rephrased version of the question.
2.  Second, the original question and the rephrased question are combined to prompt a "Responding LLM" to generate the answer.

![Two-step RaR Diagram](../img/Two-stepRaR.png)
*Caption: Diagram illustrating the Two-step RaR process.*

## Examples

---
**One-step RaR:**
This prompt instructs the LLM to perform both rephrasing/expansion and answering in a single step.
```markdown
"{question}"
Rephrase and expand the question, and respond.
```

**Two-step RaR (Rephrasing Prompt):**
This is the prompt given to the "Rephrasing LLM" in the first step of the Two-step RaR method.
```markdown
"{question}"
Given the above question, rephrase and expand it to help you do better answering. Maintain all information in the original question.
```
*(Note: The output of this step would then be combined with the original question for the "Responding LLM".)*

**PiaC-inspired Query for Self-Optimization:**
This is an example of asking the LLM to help optimize the user's query, reflecting the underlying principle of RaR.
```markdown
My question is "{question}".
How should I phrase my question to enable you to perform better? Please optimize my question's phrasing, provide an improved example, and then respond.
```
