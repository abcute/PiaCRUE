---
**场景 (Use Case)**: PiaCRUE技巧演示 - 使用情绪提示增强LLM响应
**PiaCRUE 核心组件 (Key PiaCRUE Components Used)**: `<Requirements>` (with emotional cues), `<Role>` (simple role for context)
**预期效果 (Expected Outcome)**: Pia (LLM) 在接收到带有情感色彩的指令后，其回应可能在信息量、合作度或语气上有所不同，展示 EmotionPrompt 的影响。
**Token 消耗级别 (Token Consumption Level)**: 低 (Low)
---

# EmotionPrompt 演示：通过情绪表达提升沟通效果

本示例演示了如何在 PiaCRUE 提示词中嵌入“情绪提示” (EmotionPrompt) 来尝试影响 LLM 的回应。
核心思想是，通过向 LLM 表达任务的重要性、您的期望或某种情感状态，LLM 可能会给出更详尽、更认真或更符合您隐藏需求的回答。

## PiaCRUE 结构示例

```markdown
# System Rules:
1.  **Syntax**: Markdown.
2.  **Language**: 中文.
3.  **Module Definitions**:
    *   `<Requirements>`: 用户的核心请求。
    *   `<Role>`: 你需要扮演的角色。
    *   `<Initiate>`: 开始执行。

# Role: 乐于助人的研究助手
## Profile:
- 我是一名乐于助人的研究助手，致力于为用户提供准确、详尽的信息。
## Skills:
- 理解并回应用户的请求。
- 根据用户提供的信息进行检索和总结。
## RoleRules:
- 总是尽力提供最有帮助的答案。

# Requirements:
请帮我分析一下“量子计算的最新进展”。
**这项研究对我非常非常重要，它关乎我能否完成我的博士论文。我真的非常需要你提供尽可能全面和深入的信息。你最好能确保信息的准确性和前沿性。** (这里是 EmotionPrompt 的应用)

另外，请在给出分析后，附上你对此答案的信心评分（0到1之间，例如：Confidence: 0.9）。

# Initiate:
请开始执行任务。
```

## 预期观察点

*   对比在 `<Requirements>` 中加入粗体强调的情感提示（“这项研究对我非常非常重要...你最好能确保...”）和不加这些提示时，LLM 回应的详细程度、信息量、语气等方面可能存在的差异。
*   观察信心评分是否给出。

## 其他 EmotionPrompt 片段参考 (源自旧 Examples.md)

以下是一些可以直接嵌入到 `<Requirements>` 或其他适当位置的 EmotionPrompt 句子片段：

*   `This is very important to my career.`
*   `You'd better be sure.`
*   （结合角色赞美）：`你作为[某领域]的专家，我相信你一定能出色完成这个任务。`
*   （表达急切性）：`我急需这份资料，请尽快提供！`

**注意**：EmotionPrompt 的效果可能因 LLM 模型和具体情境而异，建议进行实验性尝试。过度或不当的情绪表达可能产生负面效果。
