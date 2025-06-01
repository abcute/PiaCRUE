- [x] Reorganize root `img/` directory: Moved all images to `docs/assets/img/` and updated all markdown references. Removed root `img/` directory. (Task completed on 2024-07-29)
- [x] Re-evaluate `conceptual_simulations` directory: Moved contents (`diagram_descriptions.md` to `docs/assets/`, `PiaAGI_Behavior_Example.py` to `Examples/`) and removed the directory as it's not a standalone tool following PiaXYZ naming. (Task completed on 2024-07-29)
# PiaAGI Project Upgrade ToDo List
- [x] Create a new file named `PiaAGI.md` in the root of the repository. (Placeholder, original task)
- [x] Add the following content to `PiaAGI.md`: (Placeholder, original task)
  ```markdown
  # PiaAGI

  PiaAGI is a project that aims to upgrade the existing PiaA project to use the latest technologies and best practices.

  ## Goals

  - Improve performance and scalability
  - Enhance user experience
  - Modernize the codebase
  - Ensure long-term maintainability

  ## Roadmap

  - [ ] Phase 1: Research and Planning
  - [ ] Phase 2: Development and Testing
  - [ ] Phase 3: Deployment and Launch
  ```
- [x] Update the `README.md` file to include a link to the new `PiaAGI.md` file. (Placeholder, original task)
- [x] Update `PiaAGI.md` Section 3.1.1 Memory Systems.
- [x] Update `PiaAGI.md` Section 3.1.2 Attention and Cognitive Control.
- [x] Update `PiaAGI.md` Section 3.1.3 Advanced Learning Mechanisms.
- [x] Update `PiaAGI.md` Section 3.2.1 Stages of PiaAGI Development.
- [x] Update `PiaAGI.md` Section 3.2.2 Acquiring Theory of Mind.
- [x] Update `PiaAGI.md` Section 3.3 Motivational Systems and Intrinsic Goals.
- [x] Update `PiaAGI.md` Section 3.4 Computational Models of Emotion.
- [x] Update `PiaAGI.md` Section 3.5 Configurable Personality Traits.
- [x] Update `PiaAGI.md` with introduction for Section 4.
- [x] Create `PiaAGI.md` Section 4.1 Core Modules and Their Interactions.
- [x] Update `PiaAGI.md` Section 4.2 Information Flow and Processing.
- [x] Update `PiaAGI.md` Section 4.3 Perception and World Modeling (Conceptual).
- [x] Update `PiaAGI.md` Section 4.4 Action Selection and Execution.
- [x] Update `PiaAGI.md` Section 5 (all subsections).
- [x] Update `PiaAGI.md` Section 6 (all subsections).
- [x] Update `PiaAGI.md` Section 7 (all subsections).
- [x] Update `PiaAGI.md` Section 8 (all subsections).
- [x] Update `PiaAGI.md` Section 9 (all subsections).
- [x] Update `PiaAGI.md` Section 11 References.
- [x] Update `PiaAGI.md` Section 12 Acknowledgements.
- [x] Update `PiaAGI.md` Appendix.
- [ ] Define near-term (6-12 months) research and development goals based on the PiaAGI framework.
- [x] Create textual descriptions for all diagrams requested in `PiaAGI.md` (Stored in `docs/assets/diagram_descriptions.md`. Future task: Integrate these into `PiaAGI.md`.)
- [x] Create `PiaAGI_Hub/conceptual_simulations/` directory.
- [x] Develop initial conceptual Python script `PiaAGI_Hub/conceptual_simulations/PiaAGI_Behavior_Example.py` illustrating simplified module interactions.
- [ ] Refine and expand `PiaAGI_Behavior_Example.py` to include more module interactions or a slightly more complex scenario (e.g., involving the Emotion Module's influence).
- [ ] Integrate textual diagram descriptions from `docs/assets/diagram_descriptions.md` into the main `PiaAGI.md` document (requires careful manual editing or a more robust tool).
- [ ] Develop a detailed specification document for the **Self-Model Module (Section 4.1.10)**, outlining its proposed data structures, core algorithms for metacognition, self-assessment, and the integration/application of its ethical framework.
- [ ] Outline a research plan for developing and testing the **Developmental Scaffolding methodology (Section 5.4, 6.1)** specifically for **Theory of Mind (ToM) acquisition (Section 3.2.2)** from PiaSeedling to PiaSapling stages. This plan should include potential simulation environments, interaction protocols, and evaluation metrics.
- [ ] Conduct a survey and report on existing Python libraries and frameworks that could be suitable for implementing key aspects of the PiaAGI cognitive architecture (e.g., for probabilistic reasoning, knowledge representation, symbolic AI, agent simulation, multi-agent systems).
- [ ] Begin drafting specific computational models for the **Motivational System (Section 3.3 and 4.1.6)**, focusing on how intrinsic goals (e.g., curiosity, competence) could be mathematically formulated and algorithmically implemented to drive agent behavior.
- [ ] Design a conceptual framework for the **Architectural Maturation (Section 3.2.1)** process, detailing how specific learning experiences or developmental milestones might trigger changes in module capacities or inter-module connectivity.
- [x] Create `PiaAGI_Hub/cognitive_module_library/` directory.
- [x] Define Abstract Base Class `BaseMemoryModule` in `PiaAGI_Hub/cognitive_module_library/base_memory_module.py`.
- [x] Define Interface `LongTermMemoryModule` in `PiaAGI_Hub/cognitive_module_library/long_term_memory_module.py`.
- [x] Define Interface `WorkingMemoryModule` in `PiaAGI_Hub/cognitive_module_library/working_memory_module.py`.
- [x] Add `README.md` to `PiaAGI_Hub/cognitive_module_library/`.
- [x] CML: Define Interface for `PerceptionModule` in `PiaAGI_Hub/cognitive_module_library/perception_module.py` (Ref PiaAGI.md Sections 4.1.1, 4.3).
- [x] CML: Define Interface for `MotivationalSystemModule` in `PiaAGI_Hub/cognitive_module_library/motivational_system_module.py` (Ref PiaAGI.md Sections 3.3, 4.1.6).
- [x] CML: Define Interface for `EmotionModule` in `PiaAGI_Hub/cognitive_module_library/emotion_module.py` (Ref PiaAGI.md Sections 3.4, 4.1.7).
- [x] CML: Define Interface for `PlanningAndDecisionMakingModule` in `PiaAGI_Hub/cognitive_module_library/planning_and_decision_making_module.py` (Ref PiaAGI.md Sections 4.1.8, 4.4).
- [x] CML: Define Interface for `SelfModelModule` in `PiaAGI_Hub/cognitive_module_library/self_model_module.py` (Ref PiaAGI.md Section 4.1.10).

## CML Next Steps
- [ ] CML: Implement basic functionality for PerceptionModule.
- [ ] CML: Implement basic functionality for MotivationalSystemModule.
- [ ] CML: Implement basic functionality for EmotionModule.
- [ ] CML: Implement basic functionality for PlanningAndDecisionMakingModule.
- [ ] CML: Implement basic functionality for SelfModelModule.
- [ ] CML: Develop example usage of combined CML modules demonstrating basic interactions.
```

## Papers Directory Refinement
- [ ] Consider integrating key insights from `PiaC.md` more explicitly as historical context within relevant sections of `PiaAGI.md`.
- [ ] Review other documents in `Papers/` (beyond `PiaC.md`) for deeper alignment or integration possibilities with `PiaAGI.md` in the future, potentially summarizing them or incorporating their core ideas into the main framework document if highly relevant.
- [ ] Ensure all documents in `Papers/` consistently use relative links for images and cross-references to other project documents.
- [ ] Research and replace hypothetical paper summaries (`AI_Cultural_Evolution.md`, `AI_Narrative_Understanding.md`, `AI_Ethical_Heuristics.md`) with summaries of actual recent (2021-2024) relevant academic papers.
- [ ] Explore and detail the potential integration of Alita agent's Model Context Protocol (MCP) concepts (from `Papers/Alita_Agent.md`) into PiaAGI's tool creation (Section 3.6), Self-Model (Section 4.1.10), and Learning Module (Section 4.1.5) functionalities.
- [ ] Further elaborate on the core concept presented in `Papers/Agent_Autonomous_Tool_Mastery.md` and ensure its principles are deeply integrated and referenced throughout relevant sections of `PiaAGI.md` (especially concerning agent capabilities, autonomy, and developmental stages).
- [ ] Establish a standard template/guideline for conceptual papers in the `Papers/` directory, recommending the structure: Abstract, Summary of Core Concepts, and Implications for PiaAGI (similar to `Agent_Autonomous_Tool_Mastery.md`).

## Framework Philosophy and Consistency
- [ ] Review all core PiaAGI documents (especially `PiaAGI.md`, `README.md`, `PROJECT_GUIDE.md`, and relevant conceptual papers) to ensure the foundational viewpoint of "treating the agent as a developing, human-like cognitive entity" is consistently and clearly articulated where appropriate, particularly when discussing psychological analogies, agent development, and role cognition.
- [ ] Further explore the implications of Chain-of-Thought (CoT) prompting, as discussed in `Papers/Chain_of_Thought_Alignment.md`, for PiaAGI's cognitive architecture (e.g., Planning, Self-Model) and developmental scaffolding strategies, reinforcing the "agent as human-like thinker" interaction paradigm.
- [ ] Expand upon the concepts outlined in `Papers/Human_Inspired_Agent_Blueprint.md` by conducting further research into each multidisciplinary area, identifying specific theories, models, and empirical findings that can concretely inform the design and development of PiaAGI's cognitive modules and overall architecture.

## Examples Directory Enhancement (Post-Refactor)
- [ ] **Cognitive Configuration Examples:**
    - [ ] Develop an example for `Configuring_Emotion_Module.md` showing how to set baseline emotional states, reactivity, and empathy levels.
    - [ ] Create an example for `Configuring_Learning_Module.md` demonstrating how to set primary learning modes, rate adaptation, and ethical heuristic update rules.
    - [ ] Add an example illustrating the configuration of the `Attention_Module.md`, showing how to set biases for top-down vs. bottom-up attention.
- [ ] **Developmental Scaffolding Examples:**
    - [ ] Create a more advanced ToM scaffolding example for a PiaSapling agent, focusing on understanding false beliefs or intentions (e.g., `Scaffolding_Intermediate_ToM.md`).
    - [ ] Develop a scaffolding example for `Cultivating_Intrinsic_Motivation.md`, showing how to design scenarios that encourage curiosity or competence in an agent.
    - [ ] Design an example for `Scaffolding_Ethical_Reasoning_Intro.md`, presenting simple ethical dilemmas for a PiaSapling agent.
- [ ] **Tool Use and Creation Examples:**
    - [ ] Create an example `Adapting_Conceptual_Tools.md` where an agent modifies a known conceptual tool for a new but related task.
    - [ ] Conceptualize an example for `Agent_Requesting_New_Tool.md` where an agent identifies a capability gap and requests or describes a new tool it needs.
    - [ ] (Advanced) Design an example for `Agent_Designing_Simple_Tool.md` where a PiaArbor agent outlines the design for a new simple conceptual or software tool.
- [ ] **PiaPES Usage Examples:**
    - [ ] Provide a more concrete example of using `prompt_engine_mvp.py` to generate one of the refactored cognitive configuration prompts, including Python code and the resulting prompt string.
    - [ ] Illustrate how PiaPES could be used to define and manage a simple `DevelopmentalCurriculum` object.
- [ ] **Cross-Stage Examples:**
    - [ ] Develop a set of related examples showing how a prompt for a specific task (e.g., "summarize this text") would differ in complexity and cognitive configuration for a PiaSeedling, PiaSapling, and PiaArbor agent.
- [ ] **Internalizing Developer Tool Principles (PiaAGI.md Section 4.5):**
    - [ ] Create a conceptual example: `Self_Monitoring_with_PiaAVT_Principles.md` illustrating how an advanced agent might internally track its performance or cognitive biases.
    - [ ] Design a conceptual example: `Internal_Experimentation_with_PiaSE_Principles.md` showing how an agent might use its World Model for internal "what-if" scenario testing.
