[View English Version (查看英文版)](./README.md)
<!-- PiaAGI AGI Research Framework Document -->
# PiaAGI：一个用于发展通用人工智能的心理认知框架

PiaAGI (Personalized Intelligent Agent for AGI - 个性化智能体赋能通用人工智能) 是一个先进的、**跨学科框架**，旨在研究和开发通用人工智能 (AGI)。它通过提出一个**心理认知上貌似合理的AGI架构**，显著地从早期的LLM交互增强方法论发展而来。PiaAGI 整合了来自心理学（认知、发展、人格、社会）、传播理论、LLM技术和基于智能体的系统的深层原理，以培养具有更强自主性、适应性和符合伦理行为的智能体。我们的核心方法论——**在修订后的 `PiaAGI.md` 中有全面详述**——概述了如何通过结构化提示和发展性支架来开发“个性化智能体”(Pias)，以此作为通往AGI的一条路径。

## 项目愿景与AGI抱负

PiaAGI 项目致力于：

*   **构建AGI系统：** 超越特定任务型AI，PiaAGI为构建具有更通用认知能力的智能体提供了一个理论和实践蓝图，详见PiaAGI认知架构（参见 `PiaAGI.md`，第4节）。
*   **促进深层心理学整合：** 系统地将记忆、学习、动机、情感、人格和发展阶段的模型嵌入到智能体设计中，以实现更鲁棒和类人的智能（参见 `PiaAGI.md`，第3节）。
*   **实现结构化的AGI发展：** 引入一套全面的方法论，使用“引导提示”和“发展性支架”来配置、引导和评估AGI智能体在其发展轨迹中的表现（参见 `PiaAGI.md`，第5和第6节）。
*   **推动符合伦理和价值观的AGI：** 将伦理推理和价值对齐作为智能体自我模型和决策过程的核心组成部分（参见 `PiaAGI.md`，第3.1.3、4.1.10、8.2节）。
*   **促进跨学科AGI研究：** 为AI研究人员、心理学家、认知科学家、哲学家和伦理学家提供一个通用框架，以协作应对AGI的多方面挑战。
*   **开发实用的AGI研究工具：** 提供一套概念性和已实现的工具，以支持PiaAGI智能体的设计、模拟、分析和迭代（参见 `PiaAGI_Research_Tools/`）。

## 目标受众

本项目面向所有致力于严谨且合乎道德地追求通用人工智能的人士，包括：

*   **AGI研究员与认知架构师：** 寻求新颖的框架和工具，用于设计、构建和测试具有丰富内部认知模型的AGI系统。
*   **AI开发者与工程师：** 有兴趣实现和实验受心理学启发的智能体架构和先进的提示技术。
*   **心理学家与认知科学家：** 希望探索心理学理论的计算实例化，并为反映人类认知的AGI模型做出贡献。
*   **AI伦理学家与哲学家：** 研究价值对齐、机器伦理、意识以及先进AGI的社会影响。
*   **产品经理与远见者：** 旨在构思和开发未来将利用真正AGI能力的产品和服务。

## 快速入门 / 导航此存储库

要参与PiaAGI项目，我们建议如下：

1.  **理解核心AGI框架：** 首先通读 **[`PiaAGI.md`](PiaAGI.md)**。这份经过大幅修订的文档是我们AGI方法论的基石，详细介绍了理论基础、心理认知架构、发展阶段以及先进的提示/支架技术。
2.  **探索项目结构：** 参考 **[`PROJECT_GUIDE.md`](PROJECT_GUIDE.md)** 以全面了解此存储库的组织方式以及每个目录中的内容，包括新的研究工具。
3.  **回顾以AGI为中心的示例：** 深入研究 **[`PiaAGI.md`](PiaAGI.md) (第7节)** 中的AGI用例，了解该框架如何应用于复杂的AGI场景。现在可以在 **`PiaAGI.md` 的附录A** 中找到演示基本R-U-E原则的更简单示例。
4.  **发现AGI研究工具：** 探索 **[`PiaAGI_Research_Tools/`](PiaAGI_Research_Tools/)** 目录。这个新部分包含：
    *   一套基于Python的工具的概念设计文档：
        *   **PiaSE (PiaAGI Simulation Environment - PiaAGI模拟环境)：** 用于在动态环境中测试智能体。
        *   **PiaCML (PiaAGI Cognitive Module Library - PiaAGI认知模块库)：** 用于构建智能体认知模块。该库现在包括核心模块（如感知、动机、情感、规划、自我模型和各种记忆系统）的已定义接口。更多详情参见 [PiaAGI_Research_Tools/PiaCML/README.md](PiaAGI_Research_Tools/PiaCML/README.md)。
        *   **PiaAVT (PiaAGI Agent Analysis & Visualization Toolkit - PiaAGI智能体分析与可视化工具包)：** 用于分析智能体行为和内部状态。
        *   **PiaPES (PiaAGI Prompt Engineering Suite - PiaAGI提示工程套件)：** 用于设计引导提示和发展性支架。
    *   位于 `PiaAGI_Research_Tools/PiaPES/prompt_engine_mvp.py` 及其 `USAGE.md` 中的 **PiaPES提示模板引擎**的初步 **MVP（最小可行产品）** 实现。

## 核心组件

*   **[`PiaAGI.md`](PiaAGI.md)：** 主要的、经过大幅修订的文档，详细介绍了PiaAGI框架、其用于AGI的心理认知架构、发展原则、伦理考量以及用于指导AGI开发的先进方法论。
*   **[`PiaAGI_Research_Tools/`](PiaAGI_Research_Tools/)：** 包含一套支持AGI研究的基于Python的工具（PiaSE、PiaCML、PiaAVT、PiaPES）的概念设计，包括PiaAGI认知模块库（CML），其中包含关键认知功能的已定义接口，以及初步的MVP实现（例如PiaPES提示模板引擎）。
*   **[`Papers/`](Papers/)：** 探讨与PiaAGI的AGI焦点相关的理论概念和相关研究的文档集合。
*   **[`Examples/`](Examples/)：** 包含与PiaAGI原则和基础R-U-E提示相关的各种实际示例。主要的、完整记录的基础示例已移至 **`PiaAGI.md` 的附录A**。特定于AGI的示例在 `PiaAGI.md` 的主体部分（第7节）中有详细说明。

## 许可证

本项目根据MIT许可证授权。详情参见 **[`LICENSE`](LICENSE)** 文件。

## 贡献

我们热忱欢迎对PiaAGI项目的贡献，特别是那些推动其AGI研究目标的贡献！如果您有兴趣，请参阅我们的 **[`CONTRIBUTING.md`](CONTRIBUTING.md)** 指南。

## 致谢

我们感谢LangGPT在结构化提示方面的基础性工作，以及更广泛的AI、心理学和认知科学研究社区。具体的致谢详见 `PiaAGI.md` 文档（第12节）。

---
返回 [PiaAGI核心文档](PiaAGI.md) | [项目自述文件](README.md)
