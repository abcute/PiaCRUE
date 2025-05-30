# PiaAGI: A Psycho-Cognitive Framework for Developing Artificial General Intelligence

PiaAGI (Personalized Intelligent Agent for AGI) is an advanced, **cross-disciplinary framework** aimed at the research and development of Artificial General Intelligence (AGI). It significantly evolves from earlier LLM interaction enhancement methodologies by proposing a **psycho-cognitively plausible architecture** for AGI. PiaAGI integrates deep principles from psychology (cognitive, developmental, personality, social), communication theory, LLM technology, and agent-based systems to foster agents with greater autonomy, adaptability, and ethically-informed behavior. Our core methodology, **comprehensively detailed in the revised `PiaAGI.md`**, outlines how "Personalized Intelligent Agents" (Pias) can be developed through structured prompting and developmental scaffolding, serving as a pathway towards AGI.

## Project Vision & AGI Ambition

The PiaAGI project is dedicated to:

*   **Architecting AGI Systems:** Moving beyond task-specific AI, PiaAGI provides a theoretical and practical blueprint for building agents with more general cognitive capabilities, as detailed in the PiaAGI Cognitive Architecture (see `PiaAGI.md`, Section 4).
*   **Fostering Deep Psychological Integration:** Systematically embedding models of memory, learning, motivation, emotion, personality, and developmental stages into agent design to achieve more robust and human-like intelligence (see `PiaAGI.md`, Section 3).
*   **Enabling Structured AGI Development:** Introducing a comprehensive methodology for configuring, guiding, and evaluating AGI agents through their developmental trajectory using "Guiding Prompts" and "Developmental Scaffolding" (see `PiaAGI.md`, Sections 5 & 6).
*   **Promoting Ethical and Value-Aligned AGI:** Integrating ethical reasoning and value alignment as core components of the agent's Self-Model and decision-making processes (see `PiaAGI.md`, Sections 3.1.3, 4.1.10, 8.2).
*   **Facilitating Cross-Disciplinary AGI Research:** Providing a common framework for AI researchers, psychologists, cognitive scientists, philosophers, and ethicists to collaborate on the multifaceted challenges of AGI.
*   **Developing Practical Tools for AGI Research:** Offering a suite of conceptual and implemented tools to support the design, simulation, analysis, and iteration of PiaAGI agents (see `PiaAGI_Research_Tools/`).

## Target Audience

This project is for anyone committed to the rigorous and ethical pursuit of Artificial General Intelligence, including:

*   **AGI Researchers & Cognitive Architects:** Seeking novel frameworks and tools for designing, building, and testing AGI systems with rich internal cognitive models.
*   **AI Developers & Engineers:** Interested in implementing and experimenting with psychologically-inspired agent architectures and advanced prompting techniques.
*   **Psychologists & Cognitive Scientists:** Wishing to explore computational instantiations of psychological theories and contribute to AGI models that reflect human cognition.
*   **AI Ethicists & Philosophers:** Investigating value alignment, machine ethics, consciousness, and the societal implications of advanced AGI.
*   **Product Managers & Visionaries:** Aiming to conceptualize and develop future products and services that will leverage true AGI capabilities.

## Quick Start / Navigating This Repository

To engage with the PiaAGI project, we recommend the following:

1.  **Understand the Core AGI Framework:** Begin by thoroughly reading **[`PiaAGI.md`](PiaAGI.md)**. This extensively revised document is the cornerstone of our AGI methodology, detailing the theoretical underpinnings, the psycho-cognitive architecture, developmental stages, and the advanced prompting/scaffolding techniques.
2.  **Explore the Project Structure:** Refer to **[`PROJECT_GUIDE.md`](PROJECT_GUIDE.md)** for a comprehensive overview of how this repository is organized and what you can find in each directory, including the new research tools.
3.  **Review AGI-Centric Examples:** Dive into the AGI use case examples in **[`PiaAGI.md`](PiaAGI.md) (Section 7)** to see how the framework is applied to complex AGI scenarios. Simpler examples demonstrating foundational R-U-E principles can now be found in **Appendix A of `PiaAGI.md`**.
4.  **Discover AGI Research Tools:** Explore the **[`PiaAGI_Hub/`](PiaAGI_Hub/)** directory. This new section contains:
    *   Conceptual design documents for a suite of Python-based tools:
        *   **PiaSE (PiaAGI Simulation Environment):** For testing agents in dynamic environments.
        *   **PiaCML (PiaAGI Cognitive Module Library):** For constructing agent cognitive modules. This library now includes defined interfaces for core modules such as Perception, Motivation, Emotion, Planning, Self-Model, and various memory systems. More details can be found in the [PiaAGI_Hub/cognitive_module_library/README.md](PiaAGI_Hub/cognitive_module_library/README.md).
        *   **PiaAVT (PiaAGI Agent Analysis & Visualization Toolkit):** For analyzing agent behavior and internal states.
        *   **PiaPES (PiaAGI Prompt Engineering Suite):** For designing Guiding Prompts and Developmental Scaffolding.
    *   An initial **MVP (Minimal Viable Product)** implementation for the **PiaPES Prompt Templating Engine** located in `PiaAGI_Hub/PiaPES/prompt_engine_mvp.py` with its `USAGE.md`.
5.  **Experiment with the PiaPES Web Interface (MVP):** For a basic graphical interface to manage prompts, navigate to `PiaAGI_Hub/PiaPES/web_app/` and follow the instructions in `PiaAGI_Hub/PiaPES/README.md` (specifically the "Web Interface (MVP)" section) to run the web application.
6.  **Utilize the Legacy Web Application:** For a hands-on experience with the foundational R-U-E prompting, explore the **PiaAGI Web Tool** (legacy PiaCRUE) by starting with its **[`pia_crue_web_tool/README.md`](pia_crue_web_tool/README.md)**.

## Core Components

*   **[`PiaAGI.md`](PiaAGI.md):** The main, extensively revised document detailing the PiaAGI framework, its psycho-cognitive architecture for AGI, developmental principles, ethical considerations, and advanced methodology for guiding AGI development.
*   **[`PiaAGI_Hub/`](PiaAGI_Hub/):** Contains conceptual designs for a suite of Python-based tools supporting AGI research (PiaSE, PiaCML, PiaAVT, PiaPES), including the PiaAGI Cognitive Module Library (CML) with defined interfaces for key cognitive functions, and initial MVP implementations (e.g., PiaPES Prompt Templating Engine).
*   **[`Papers/`](Papers/):** A collection of documents exploring theoretical concepts and related research relevant to PiaAGI's AGI focus.
*   **[`Examples/`](Examples/):** Contains various practical examples related to PiaAGI principles and foundational R-U-E prompting. The primary, fully documented foundational examples have been moved to **Appendix A of `PiaAGI.md`**. AGI-specific examples are detailed within the main body of `PiaAGI.md` (Section 7).
*   **[`pia_crue_web_tool/`](pia_crue_web_tool/):** The legacy web-based application for foundational R-U-E prompt generation.

## PiaAGI GPTs

*Note: These are external resources that leverage PiaAGI principles.*

1.  **[GPTs-PiaAGI Assistant](https://chat.openai.com/g/g-mGgqa0Aft-piacrue):** A GPT assistant trained on the PiaAGI framework, capable of answering questions about its concepts, methodologies, and AGI development approach.
2.  **[GPTs-PromptEngineer Pro](https://chat.openai.com/g/g-uBcGAkHGm-promptengineer-pro):** A GPT-based prompt optimization assistant.
3.  **[GPTs-AutoExpGPT](https://chat.openai.com/g/g-9pFb5GFXw-autoexpgpt):** A GPT for designing automated experiments to evaluate prompt strategies.

## License

This project is licensed under the MIT License. See the **[`LICENSE`](LICENSE)** file for details.

## Contributing

We enthusiastically welcome contributions to the PiaAGI project, particularly those that advance its AGI research goals! If you're interested, please see our **[`CONTRIBUTING.md`](CONTRIBUTING.md)** guide.

## Acknowledgements

We acknowledge the foundational work in structured prompting by LangGPT and the broader AI, psychology, and cognitive science research communities. Specific acknowledgements are detailed within the `PiaAGI.md` document (Section 12).
