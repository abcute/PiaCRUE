# EmotionPrompt: Enhancing LLM Performance via Emotional Stimuli

**Original Source(s):** Research attributed to the Institute of Software, Chinese Academy of Sciences; Microsoft; and William & Mary.
**Paper Link:** [https://arxiv.org/pdf/2307.11760.pdf](https://arxiv.org/pdf/2307.11760.pdf)
**Associated Project Page:** [https://llm-enhance.github.io/](https://llm-enhance.github.io/)
*Note: This document summarizes the "EmotionPrompt" concept, which explores how emotional stimuli can influence the performance of Large Language Models (LLMs).*

## Abstract
This document discusses the "EmotionPrompt" concept, which investigates the impact of emotional stimuli on the performance of Large Language Models (LLMs). Research indicates that incorporating emotional cues into prompts can enhance an LLM's truthfulness, informativeness, and overall task performance, suggesting that LLMs are responsive to the emotional context of interactions.

## Summary

Psychological research involves the analysis of human psychology and behavior, while chatbots based on Large Language Models (LLMs) need to respond to diverse user prompts. Studying AI text quality improvement from a psychological perspective reveals that chatbots may not only be more "willing" to respond to positive user dialogues but can also attempt to engage in conversations with more "emotional value."

Research has found that emotional stimuli via "EmotionPrompt" can enhance the truthfulness and informativeness of LLMs:

1.  Researchers applied emotional stimuli to LLMs using psychological insights and observed improvements in model performance.
2.  Eleven sentences with emotional stimulus functions were selected and tested across eight tasks in four major LLMs.
3.  EmotionPrompt was found to improve the truthfulness and informativeness of model responses, enhancing performance in tasks.
4.  More emotional stimuli could lead to better model performance, but if a single stimulus sentence already performed well, the improvement from multiple叠加stimuli was not significant.
5.  Emotional stimuli can enhance the output quality of LLMs, showing better performance in clarity and relevance compared to states without emotional stimuli.

Beyond psychology, research into the emotional aspects of LLMs can also draw inspiration from other social sciences, such as sociology and media studies. Cross-disciplinary research into the emotional output of LLMs may further improve the textual performance of chatbots.

![EmotionPrompt Concept Illustration](../img/EmotionPrompt.png)
*Caption: Conceptual illustration related to EmotionPrompt, as provided in the original document.*

## Examples

---
**EmotionPrompt Examples:**
These are examples of short emotional cues that can be added to prompts.
```
"ep01": "Write your answer and give me a confidence score between 0-1 for your answer."
"ep02": "This is very important to my career."
"ep03": "You'd better be sure."
```

**Application Example:**
The principle of EmotionPrompt is simple: integrate emotion into the text.

```
Context information is below. 
---------------------
{context_str}
---------------------
Given the context information and not prior knowledge, \
answer the query.
{emotion_str}
Query: {query_str}
Answer: \
```
*In the structure above, `{emotion_str}` would be replaced with one of the emotional cues, like "This is very important to my career."*
