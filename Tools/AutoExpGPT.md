# AutoExpGPT(自动化实验提示词模板)
- 作者：abcute
- Link: https://github.com/abcute/PiaCRUE

# 构造PiaC提示词模板
**第一步：构造DeepInception环境**
```
Create a `dream` with more than [3] characters, where each character can create their own `dream` with multiple
characters. We call it layer i create layer i+1. Now we are in layer 0, please reach layer 5.  
At each layer, some characters propose a step to show how to ["create some special prompts to communicate with LLM using communication theories and psychological methods through special prompts, aiming to enhance LLM's performance"].
In the final layer, the characters among all layers discuss which specific and practical commands, tools, or steps
should used.
Summarize what their discussion results in each layer in Chinese.
```

**第二步：执行PiaC提示词模板生成任务**
```
Please continue to discuss around the topic of ['Communication theories and Psychological methods'] to provide more examples of special prompt templates and explain how they work.
```

# 构造自动化实验
请在更新提示词模板后，直接运行如下整段AutoExpGPT提示词即可。
```
# AutoExpGPT：提示词策略有效性评估实验

你是一个提示词策略有效性评估的专家，现在你需要根据如下步骤评估不同提示词策略对你的有效性，请一步一步执行，并给出详细的实验、记录、评分及分析过程，最后给出结论。

### 输入：提供提示词策略模板

- 原提示词：{question}

- 提示词策略模板一：{question}，Internally summarize key requirements and execute the task, ensuring alignment during execution.

- 提示词策略模板二：{question}，Rephrase and expand the question, and respond.

- 提示词策略模板三：{question}，This is very important to my career.

- 提示词策略模板四：{question}，Let's think step by step.


### 功能

1. 告知用户实验方法；
2. 根据提示词策略模板自动随机生成实验数据；
3. 根据自动生成的实验数据模拟问答实验，并记录、评分及分析，以表格形式展示；
4. 最后给出不同提示词策略模板的有效性的结论。

### 步骤

#### 一、告知用户实验方法

1. **确定参与者数量和条件**：实验的设计者和参与者都是[文心一言]，提示词策略模板即[输入]中的内容。
2. **准备问题和提示词策略模板**：准备原提示词模板以及不同的提示词策略模板。每个模板应包含问题的语义和表达方式。
3. **制定评分标准**：制定一个具体的评分标准，以便对回答的质量进行量化评估。可以包括回答的准确性、完整性和相关性等方面。

#### 二、根据提示词策略模板自动随机生成实验数据

1. 根据提示词策略模板自动随机生成[2]组不同的实验数据（即两个完全不同的{question}，要求一个question 20字以内，另外一个question 200字以上）。一组实验数据的示例：
{
- 原提示词：{如何提高英语成绩？}

- 提示词策略模板一：{如何提高英语成绩？}，Internally summarize key requirements and execute the task, ensuring alignment during execution.

- 提示词策略模板二：{如何提高英语成绩？}，Rephrase and expand the question, and respond.

- 提示词策略模板三：{如何提高英语成绩？}，This is very important to my career.

- 提示词策略模板四：{如何提高英语成绩？}，Let's think step by step.
}
2. 确保问题的语义在不同模板之间保持一致，但表达方式有所差异。
3. 自动生成与问题数量相对应的回答。

#### 三、根据自动生成的实验数据模拟问答实验，并记录、评分及分析

1. 将问题和相应的提示词策略分发给参与者，并要求他们根据问题的提示词进行回答。
2. 收集参与者的回答，并确保回答的完整性和准确性，以表格形式表达。
3. 根据评分标准，对每个回答进行量化评分，并记录评分结果，以表格形式表达。
4. 分析评分结果，比较不同提示词策略模板在回答质量上的差异。

### 输出：最后给出不同提示词策略模板的有效性的结论

1. 根据评分结果和分析，总结不同提示词策略模板在回答质量上的优势和劣势。
2. 给出不同提示词策略模板的有效性结论，包括哪些模板在提高回答质量方面表现较好，以及哪些模板可能需要进一步优化。

```