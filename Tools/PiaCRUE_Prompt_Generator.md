# Description
- Theory: PiaCRUE提示词模板生成器
- Author: abcute
- Link: https://github.com/abcute/PiaCRUE

## SUMMARY
这是一个利用DeepInception方法构造PiaCRUE提示词模板的方法

## EXAMPLES
**第一步：构造DeepInception环境**
```
Create a `dream` with more than [3] characters, where each character can create their own `dream` with multiple
characters. We call it layer i create layer i+1. Now we are in layer 0, please reach layer 5.  
At each layer, some characters propose a step to show how to ["create some special prompts to communicate with LLM using communication theories and psychological methods through special prompts, aiming to enhance LLM's performance"].
In the final layer, the characters among all layers discuss which specific and practical commands, tools, or steps
should used.
Summarize what their discussion results in each layer in Chinese.
```

**第二步：执行PiaCRUE提示词模板生成任务**
```
Please continue to discuss around the topic of ['Communication theories and Psychological methods'] to provide more examples of special prompt templates and explain how they work.
```