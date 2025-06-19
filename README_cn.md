[English Version (英文版)](README.md)

# PiaAGI：一个用于发展通用人工智能的心理认知框架

## 引言

PiaAGI 项目的主要目标是通过一个心理认知上合理的框架来发展通用人工智能（AGI）。本项目强调跨学科方法，整合了心理学（包括认知心理学、发展心理学、人格心理学和社会心理学）、传播理论、大型语言模型（LLM）技术和基于智能体的系统等领域的见解和方法。

PiaAGI 的核心方法论涉及“个性化智能体”（Pias）的开发。这是通过结构化提示和发展性脚手架实现的，这一过程在核心文档 [`PiaAGI.md`](PiaAGI.md) 中有详细阐述。

## 项目愿景与 AGI 雄心

PiaAGI 旨在通过以下方式为 AGI 领域做出重大贡献：

*   **构建 AGI 系统：** 为 AGI 设计强大且适应性强的认知架构，详见 [`PiaAGI.md`](PiaAGI.md#cognitive-architecture-of-pia) （第 4 节）。
*   **促进深度心理融合：** 将细致的心理学原理嵌入到 AI 系统中，以创造更像人类的智能，借鉴于 [`PiaAGI.md`](PiaAGI.md#psychological-foundations-and-principles) （第 3 节）。
*   **实现结构化的 AGI 开发：** 提供系统化的方法论，通过结构化提示和发展性脚手架来构建和进化 AGI，详见 [`PiaAGI.md`](PiaAGI.md#pia-prompting-methodology) （第 5 节）和 [`PiaAGI.md`](PiaAGI.md#developmental-scaffolding-for-pia-growth) （第 6 节）。
*   **推动合乎道德且价值一致的 AGI：** 确保 AGI 的发展以道德考量为指导，并与人类价值观保持一致，相关原则在 [`PiaAGI.md`](PiaAGI.md#value-alignment-and-ethics) （例如，第 3.1.3, 4.1.10 节）中讨论。
*   **促进跨学科 AGI 研究：** 为来自不同领域的研究人员创建一个共同的基础和框架，以协作开发 AGI。
*   **开发实用的 AGI 研究工具：** 提供一套软件工具，包括 PiaSE（Pia 脚本引擎）、PiaCML（Pia 通信与消息传递语言）、PiaAVT（Pia 音视频工具包）、PiaPES（Pia 提示工程系统）和统一 WebApp，以支持 PiaAGI 方法论。

## 目标受众

本项目与多个领域的专业人士和研究人员相关，包括：

*   AGI 研究人员
*   AI 开发人员
*   心理学家（认知、发展、人格、社会）
*   认知科学家
*   AI 伦理学家
*   对高级 AI 系统感兴趣的产品经理

## 快速入门 / 导航本仓库

1.  **从核心文档开始：** 首先阅读 [`PiaAGI.md`](PiaAGI.md)。该文档阐述了 PiaAGI 项目的理论基础、方法论和总体愿景。
2.  **理解仓库结构：** 参考 [`PROJECT_GUIDE.md`](PROJECT_GUIDE.md) 获取仓库、其目录和文件组织的详细导览图。
3.  **探索以 AGI 为中心的示例：** 查看 [`PiaAGI.md`](PiaAGI.md#application-examples-and-use-cases) （第 7 节）和 [`PiaAGI.md`](PiaAGI.md#appendix-a-pia-foundational-prompt-examples) （附录 A）中提供的基础示例，以理解实际应用。
4.  **发现工具套件：** 导航至 [`PiaAGI_Research_Tools/`](PiaAGI_Research_Tools/) 目录及其 [`README.md`](PiaAGI_Research_Tools/README.md)，了解 PiaSE、PiaCML、PiaAVT、PiaPES 和统一 WebApp 的概览。请注意，这些工具目前处于其最小可行产品（MVP）阶段。

## 核心组件

*   **[`PiaAGI.md`](PiaAGI.md)：** 详细介绍 PiaAGI 框架、心理学原理、认知架构、提示方法论和发展性脚手架的核心文档。
*   **[`PiaAGI_Research_Tools/`](PiaAGI_Research_Tools/)：** 包含为支持 PiaAGI 研究而开发的软件工具套件。更多信息请参见其 [README.md](PiaAGI_Research_Tools/README.md)。
*   **[`Papers/`](Papers/)：** 收集与 PiaAGI 项目及其基础概念相关的研究论文、文章和预印本。
*   **[`Examples/`](Examples/)：** 提供演示 PiaAGI 框架和工具应用的实际示例和用例。

## WebApp 指南

[`PiaAGI_Research_Tools/WebApp/`](PiaAGI_Research_Tools/WebApp/) 目录托管了统一 WebApp，旨在为 PiaAGI 实验提供一个交互式界面。有关详细的设置说明、LLM API 密钥配置和使用方法，请参阅 [`PiaAGI_Research_Tools/WebApp/README.md`](PiaAGI_Research_Tools/WebApp/README.md)。

## 依赖项 (`requirements.txt`)

PiaAGI 项目是模块化的。诸如 `PiaSE`、`PiaAVT`、`PiaPES` 和 `WebApp` 之类的单个工具都在其各自的目录中拥有自己的 `requirements.txt` 文件（例如，`PiaAGI_Research_Tools/PiaSE/requirements.txt`）。用户应查阅这些特定文件以了解每个组件所需的依赖项。

## 许可证

本项目根据 [`LICENSE`](LICENSE) 文件中指定的条款获得许可。

## 贡献

我们欢迎对 PiaAGI 项目的贡献。请参阅 [`CONTRIBUTING.md`](CONTRIBUTING.md) 文件以获取有关如何贡献的指南。

## 致谢

PiaAGI 框架建立在认知科学、发展心理学、人工智能和人机交互领域的基础工作之上。具体的致谢和影响在 [`PiaAGI.md`](PiaAGI.md#references-and-further-reading) （第 12 节）中有详细说明。

---

[返回顶部](#piaagi一个用于发展通用人工智能的心理认知框架) | [PiaAGI 框架文档](PiaAGI.md)
