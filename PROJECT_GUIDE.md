<!-- PiaAGI AGI Research Framework Document -->
# Project Structure and Navigation Guide

Welcome to the PiaAGI project! This guide is designed to help you understand the structure of our repository and navigate its contents effectively as we pursue our **upgraded AGI research vision**.

The core idea of PiaAGI is to develop **Artificial General Intelligence (AGI)** by architecting **Personalized Intelligent Agents (Pia)** based on a **psycho-cognitively plausible framework**. This involves leveraging communication theory, deep psychological principles (such as cognitive architectures, developmental psychology, motivation, emotion, and personality modeling), advanced LLM technology, and agent-based systems. The project aims to share the comprehensive PiaAGI methodology, its AGI-focused cognitive architecture, prompt strategies for advanced agent guidance, developmental scaffolding techniques, practical examples, and a suite of research tools to help users understand, build, and experiment within this AGI framework.

For a comprehensive understanding of PiaAGI's theoretical foundations, AGI architecture, and core concepts, please refer to these primary documents:
*   **[`PiaAGI.md`](PiaAGI.md):** The extensively revised and detailed explanation of the PiaAGI framework for AGI development.
*   **[`README.md`](README.md):** Overall project overview, AGI vision, and entry point.

## Project Structure Overview

To help you quickly find the information you need, here is a description of the main files and directories in this project:

*   **`PiaAGI.md`**: This is the central document for understanding the PiaAGI framework. It details the theoretical underpinnings (Psychology, LLMs, and Agent technology for AGI), the psycho-cognitive architecture (Section 4), developmental stages (Section 3.2.1), core psychological principles for AGI functionality (Section 3), and specific methodologies for constructing Guiding Prompts and Developmental Scaffolding for AGI agents (Sections 5 & 6).

*   **`README.md`**: The main entry point and overview of the project. It provides a concise introduction to PiaAGI's AGI research vision, its cross-disciplinary nature, and links to other important documents and resources, including the new research tools.

*   **`PROJECT_GUIDE.md`**: This document (which you are currently reading). It provides a map to the repository's structure and guidance on how to navigate its contents, reflecting the project's AGI focus.

*   **`LICENSE`**: Contains the MIT License under which the PiaAGI project is released.

*   **`CONTRIBUTING.md`**: Provides guidelines for community members who wish to contribute to the project, particularly in areas advancing AGI research.

*   **`CODE_OF_CONDUCT.md`**: Outlines the code of conduct for all contributors and participants in the PiaAGI community.

*   **`PiaAGI_Research_Tools/`**: This **directory** is central to the project's AGI research toolkit. It contains:
    *   **Conceptual Design Documents:** Detailed Markdown files for a suite of Python-based tools envisioned to support AGI research within the PiaAGI framework:
        *   `PiaAGI_Simulation_Environment.md` (PiaSE): For creating dynamic environments to test and develop PiaAGI agents.
        *   `PiaAGI_Cognitive_Module_Library.md` (PiaCML): For building and experimenting with implementations of PiaAGI's cognitive modules.
        *   `PiaAGI_Agent_Analysis_Visualization_Toolkit.md` (PiaAVT): For logging, analyzing, and visualizing agent behavior and internal cognitive states.
        *   `PiaAGI_Prompt_Engineering_Suite.md` (PiaPES): For designing, managing, and evaluating complex Guiding Prompts and Developmental Scaffolding curricula.
    *   **`PiaPES/` sub-directory:** Houses implementations related to the Prompt Engineering Suite.
        *   `prompt_engine_mvp.py`: A Minimal Viable Product (MVP) of the PiaAGI Prompt Templating Engine, allowing for programmatic construction and rendering of PiaAGI prompts.
        *   `USAGE.md`: Instructions and examples for using the `prompt_engine_mvp.py`.
    *   The main `README.md` in this directory provides an overview of these tools. Researchers and developers interested in practical implementations and experimentation should focus here.

*   **`Papers/`**: This directory ([see its `README.md`](Papers/README.md) for a summary of contents) houses theoretical research papers, conceptual explorations, and in-depth analyses related to the PiaAGI framework and its AGI aspirations. These documents provide academic context and deeper insights into the methodologies.
    *   Key papers discuss the application of communication theories, psychological models, and ethical considerations relevant to building AGI.

*   **`Examples/`**: This directory contains various practical examples related to PiaAGI principles and foundational R-U-E prompting. The primary, fully documented foundational examples ('Viral Xiaohongshu Post Copywriting Expert,' 'PoetActor' examples) have been moved to **Appendix A of `PiaAGI.md`**. AGI-specific examples are detailed within the main body of `PiaAGI.md` (Section 7). The `Examples/` directory may still contain other illustrative scenarios or simpler templates like `PiaCRUE_Template.md` and `PiaCRUE_mini.md`.

*   **`Tools/` (Legacy Conceptual Directory)**: This directory previously offered methodologies and advanced prompt templates. Its role is now largely superseded by the more comprehensive and implementation-focused `PiaAGI_Research_Tools/` directory. It may still contain legacy conceptual documents like `AutoExpGPT.md`.

*   **`pia_crue_web_tool/`**: This directory contains a web-based application (with its own frontend and backend) designed to facilitate the practical use of the foundational PiaAGI (PiaCRUE) prompting framework. It serves as a hands-on tool for generating, testing, and managing these earlier-stage prompts.

*   **`img/`**: This directory stores image resources referenced by various Markdown documents within the project.

## How to Get Started with PiaAGI for AGI Development

If you are new to the PiaAGI project and interested in its AGI research aspects, you can begin your exploration with the following steps:

1.  **Grasp the AGI Vision and Core Framework**: Start by reading the main project [`README.md`](README.md) for a general overview of the AGI focus. Then, dedicate significant time to **[`PiaAGI.md`](PiaAGI.md)** to understand the core psycho-cognitive architecture (Section 4), the integrated psychological principles for AGI (Section 3), the concept of developmental stages (Section 3.2.1), and the advanced methodology for Guiding Prompts and Developmental Scaffolding (Sections 5 & 6).
2.  **Explore AGI-Centric Examples**: Review the advanced use cases in **[`PiaAGI.md`](PiaAGI.md) (Section 7)** which illustrate how the framework and prompting methodologies are applied to configure and guide agents with AGI-level capabilities.
3.  **Investigate the Research Toolkit**: Navigate to the **[`PiaAGI_Research_Tools/`](PiaAGI_Research_Tools/)** directory.
    *   Read the `README.md` there for an overview of the conceptualized Python tools.
    *   Study the design documents for PiaSE, PiaCML, PiaAVT, and PiaPES to understand their intended roles in AGI research.
    *   Examine the **PiaPES Prompt Templating Engine MVP** in `PiaAGI_Research_Tools/PiaPES/prompt_engine_mvp.py` and its `USAGE.md` for a practical starting point in programmatic prompt construction.
4.  **Delve into Theoretical Background**: If you are interested in the deeper theories underpinning PiaAGI, explore the research papers and conceptual discussions in the `Papers/` directory.
5.  **Understand Foundational Prompting (Optional):** For context on the evolution of PiaAGI, you can explore the foundational R-U-E examples in **Appendix A of `PiaAGI.md`**, other illustrative examples in the `Examples/` directory, and the `pia_crue_web_tool/`.

## Contributing and Feedback

We warmly welcome community contributions to the PiaAGI project, particularly those that advance its AGI research goals, help implement the research tools, or refine the cognitive architecture and developmental methodologies.

For detailed guidelines on how to contribute, please see our **[`CONTRIBUTING.md`](CONTRIBUTING.md)** file.

If you have any questions, suggestions, or feedback, please use the **GitHub Issues** section of this repository. We appreciate your input!

---
Return to [PiaAGI Core Document](PiaAGI.md) | [Project README](README.md)
