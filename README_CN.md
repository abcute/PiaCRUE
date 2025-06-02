[English Version](./README.md)
<!-- PiaAGI AGI 研究框架文档 -->
# PiaAGI：一个用于发展通用人工智能的心理认知框架

PiaAGI（PiaAGI，个性化智能体赋能通用人工智能）是一个先进的、**跨学科框架**，旨在研究和开发通用人工智能（AGI）。它通过提出一个**心理认知上貌似合理的AGI架构**，显著地从早期的大语言模型（LLM）交互增强方法发展而来。PiaAGI整合了心理学（认知、发展、人格、社会）、传播理论、LLM技术和基于智能体的系统的深层原理，以培养具有更强自主性、适应性和合乎道德行为的智能体。我们的核心方法论，**在修订后的 `PiaAGI.md` 中有详尽阐述**，概述了如何通过结构化提示和发展支架来开发“个性化智能体”（Pias），以此作为通向AGI的途径。

## 项目愿景与AGI雄心

PiaAGI项目致力于：

*   **构建AGI系统：** PiaAGI超越了特定任务的人工智能，为构建具有更通用认知能力的智能体提供了理论和实践蓝图，详见PiaAGI认知架构（参见 `PiaAGI.md`，第4节）。
*   **促进深层心理整合：** 系统地将记忆、学习、动机、情感、人格和发展阶段模型嵌入智能体设计中，以实现更强大和更像人类的智能（参见 `PiaAGI.md`，第3节）。
*   **实现结构化AGI开发：** 引入一种全面的方法论，通过使用“引导提示”和“发展支架”来配置、指导和评估AGI智能体的发展轨迹（参见 `PiaAGI.md`，第5和第6节）。
*   **推广合乎道德和价值对齐的AGI：** 将伦理推理和价值对齐作为智能体自我模型和决策过程的核心组成部分进行整合（参见 `PiaAGI.md`，第3.1.3、4.1.10、8.2节）。
*   **促进跨学科AGI研究：** 为人工智能研究人员、心理学家、认知科学家、哲学家和伦理学家提供一个通用框架，以协作应对AGI的多方面挑战。
*   **开发AGI研究实用工具：** 提供一套概念性和已实现的工具，以支持PiaAGI智能体的设计、模拟、分析和迭代（参见 `PiaAGI_Research_Tools/`）。

## 目标受众

本项目面向所有致力于严谨和合乎道德地追求通用人工智能的人士，包括：

*   **AGI研究人员和认知架构师：** 寻求新颖的框架和工具，用于设计、构建和测试具有丰富内部认知模型的AGI系统。
*   **AI开发者和工程师：** 有兴趣实施和实验受心理学启发的智能体架构和先进的提示技术。
*   **心理学家和认知科学家：** 希望探索心理学理论的计算实例，并为反映人类认知的AGI模型做出贡献。
*   **AI伦理学家和哲学家：** 研究价值对齐、机器伦理、意识以及先进AGI的社会影响。
*   **产品经理和远见者：** 旨在构思和开发将利用真正AGI能力的未来产品和服务。

## 快速入门 / 导航此存储库

要参与PiaAGI项目，我们建议如下：

1.  **理解核心AGI框架：** 首先通读 **[`PiaAGI.md`](PiaAGI.md)**。这份经过广泛修订的文档是我们AGI方法论的基石，详细介绍了理论基础、心理认知架构、发展阶段以及先进的提示/支架技术。
2.  **探索项目结构：** 请参阅 **[`PROJECT_GUIDE.md`](PROJECT_GUIDE.md)**，以全面了解此存储库的组织方式以及您可以在每个目录中找到的内容，包括新的研究工具。
3.  **查阅以AGI为中心的示例：** 深入研究 **[`PiaAGI.md`](PiaAGI.md)（第7节）** 中的AGI用例示例，了解该框架如何应用于复杂的AGI场景。现在可以在 **`PiaAGI.md` 的附录A** 中找到演示基础R-U-E原则的更简单示例。
4.  **发现AGI研究工具：** 探索 **[`PiaAGI_Research_Tools/`](PiaAGI_Research_Tools/)** 目录。这个新部分包含：
    *   一套基于Python的工具的概念设计文档：
        *   **PiaSE (PiaAGI Simulation Environment):** 用于在动态环境中测试智能体。
        *   **PiaCML (PiaAGI Cognitive Module Library):** 用于构建智能体认知模块。该库现在包括12个以上核心认知模块（感知、记忆、动机、情感、规划、自我模型等）的已定义Python接口以及其中许多模块的基本具体MVP实现。更多详细信息可以在 [PiaAGI_Research_Tools/PiaCML/README.md](PiaAGI_Research_Tools/PiaCML/README.md) 中找到。
        *   **PiaAVT (PiaAGI Agent Analysis & Visualization Toolkit):** 用于分析智能体行为和内部状态。
        *   **PiaPES (PiaAGI Prompt Engineering Suite):** 用于设计引导提示和发展支架。
    *   多种工具已存在初步的 **MVP（最小可行产品）实现**，包括 **PiaPES提示模板引擎** (`PiaAGI_Research_Tools/PiaPES/prompt_engine_mvp.py`)，**PiaSE** (GridWorld环境，Q-Learning智能体) 和 **PiaAVT** (日志记录，基本分析，Streamlit Web应用程序) 的基本版本，以及 **PiaCML** 的基础接口和具体类。一个 **统一的WebApp** (`PiaAGI_Research_Tools/WebApp/`) 为与这些MVP交互提供了一个中央界面。

## 核心组件

*   **[`PiaAGI.md`](PiaAGI.md):** 主要的、经过广泛修订的文档，详细介绍了PiaAGI框架、其用于AGI的心理认知架构、发展原则、伦理考虑以及用于指导AGI开发的先进方法论。
*   **[`PiaAGI_Research_Tools/`](PiaAGI_Research_Tools/):** 包含支持AGI研究的工具套件（PiaSE、PiaCML、PiaAVT、PiaPES）的概念设计和Python MVP实现。这包括PiaAGI认知模块库（PiaCML），其中包含关键认知功能的已定义接口和基本具体类，PiaPES提示引擎，PiaSE和PiaAVT的基本版本，以及用于交互的统一WebApp。有关详细信息，请参阅其 [README.md](PiaAGI_Research_Tools/README.md)。
*   **[`Papers/`](Papers/):** 探索与PiaAGI的AGI焦点相关的理论概念和相关研究的文档集合。
*   **[`Examples/`](Examples/):** 包含与PiaAGI原则和基础R-U-E提示相关的各种实际示例。主要的、完整记录的基础示例已移至 **`PiaAGI.md` 的附录A**。AGI特定示例在 `PiaAGI.md` 的主体部分（第7节）中有详细说明。

## 许可证

本项目根据MIT许可证授权。有关详细信息，请参阅 **[`LICENSE`](LICENSE)** 文件。

## 贡献

我们热忱欢迎对PiaAGI项目的贡献，特别是那些推动其AGI研究目标的贡献！如果您有兴趣，请参阅我们的 **[`CONTRIBUTING.md`](CONTRIBUTING.md)** 指南。

## 致谢

我们感谢LangGPT在结构化提示方面的基础性工作以及更广泛的人工智能、心理学和认知科学研究社区。具体的致谢详见 `PiaAGI.md` 文档（第12节）。

---
返回 [PiaAGI核心文档](PiaAGI.md) | [项目自述文件](README.md)
