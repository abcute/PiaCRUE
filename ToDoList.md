# PiaAGI Project Upgrade ToDo List

- [x] Reorganize root `img/` directory: Moved all images to `docs/assets/img/` and updated all markdown references. Removed root `img/` directory. (Task completed on 2024-07-29)
- [x] Re-evaluate `conceptual_simulations` directory: Moved contents (`diagram_descriptions.md` to `docs/assets/`, `PiaAGI_Behavior_Example.py` to `Examples/`) and removed the directory as it's not a standalone tool following PiaXYZ naming. (Task completed on 2024-07-29)
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
- [x] Create textual descriptions for all diagrams requested in PiaAGI.md (Stored in docs/assets/diagram_descriptions.md). (Most descriptions integrated, manual insertion needed for Diagrams 8, 9, 10 in PiaAGI.md as per user instructions).
- [x] Create `PiaAGI_Hub/conceptual_simulations/` directory. (Directory later removed after refactoring file locations)
- [x] Develop initial conceptual Python script `Examples/PiaAGI_Behavior_Example.py` illustrating simplified module interactions. (Moved from `PiaAGI_Hub/conceptual_simulations/`)
- [ ] Manually integrate textual descriptions for Diagrams 8, 9, and 10 into PiaAGI.md (User task - content provided). Most other diagrams integrated.
- [ ] Develop a detailed specification document for the **Self-Model Module (Section 4.1.10)**, outlining its proposed data structures, core algorithms for metacognition, self-assessment, and the integration/application of its ethical framework.
- [ ] Outline a research plan for developing and testing the **Developmental Scaffolding methodology (Section 5.4, 6.1)** specifically for **Theory of Mind (ToM) acquisition (Section 3.2.2)** from PiaSeedling to PiaSapling stages. This plan should include potential simulation environments, interaction protocols, and evaluation metrics.
- [ ] Conduct a survey and report on existing Python libraries and frameworks that could be suitable for implementing key aspects of the PiaAGI cognitive architecture (e.g., for probabilistic reasoning, knowledge representation, symbolic AI, agent simulation, multi-agent systems).
- [ ] Begin drafting specific computational models for the **Motivational System (Section 3.3 and 4.1.6)**, focusing on how intrinsic goals (e.g., curiosity, competence) could be mathematically formulated and algorithmically implemented to drive agent behavior.
- [ ] Design a conceptual framework for the **Architectural Maturation (Section 3.2.1)** process, detailing how specific learning experiences or developmental milestones might trigger changes in module capacities or inter-module connectivity.
- [x] Create `PiaAGI_Research_Tools/cognitive_module_library/` directory. (Path updated from PiaAGI_Hub)
- [x] Define Abstract Base Class `BaseMemoryModule` in `PiaAGI_Research_Tools/cognitive_module_library/base_memory_module.py`. (Path updated)
- [x] Define Interface `LongTermMemoryModule` in `PiaAGI_Research_Tools/cognitive_module_library/long_term_memory_module.py`. (Path updated)
- [x] Define Interface `WorkingMemoryModule` in `PiaAGI_Research_Tools/cognitive_module_library/working_memory_module.py`. (Path updated)
- [x] Add `README.md` to `PiaAGI_Research_Tools/cognitive_module_library/`. (Path updated)
- [x] CML: Define Interface for `PerceptionModule` in `PiaAGI_Research_Tools/cognitive_module_library/perception_module.py` (Ref PiaAGI.md Sections 4.1.1, 4.3). (Path updated)
- [x] CML: Define Interface for `MotivationalSystemModule` in `PiaAGI_Research_Tools/cognitive_module_library/motivational_system_module.py` (Ref PiaAGI.md Sections 3.3, 4.1.6). (Path updated)
- [x] CML: Define Interface for `EmotionModule` in `PiaAGI_Research_Tools/cognitive_module_library/emotion_module.py` (Ref PiaAGI.md Sections 3.4, 4.1.7). (Path updated)
- [x] CML: Define Interface for `PlanningAndDecisionMakingModule` in `PiaAGI_Research_Tools/cognitive_module_library/planning_and_decision_making_module.py` (Ref PiaAGI.md Sections 4.1.8, 4.4). (Path updated)
- [x] CML: Define Interface for `SelfModelModule` in `PiaAGI_Research_Tools/cognitive_module_library/self_model_module.py` (Ref PiaAGI.md Section 4.1.10). (Path updated)

## Research Tools - Conceptual Next Steps

### PiaCML (Cognitive Module Library)
- [x] CML: Implement foundational interfaces/ABCs for PerceptionModule. (Base class/interface defined)
- [x] CML: Implement foundational interfaces/ABCs for MotivationalSystemModule. (Base class/interface defined)
- [x] CML: Implement foundational interfaces/ABCs for EmotionModule. (Base class/interface defined)
- [x] CML: Implement foundational interfaces/ABCs for PlanningAndDecisionMakingModule. (Base class/interface defined)
- [x] CML: Implement foundational interfaces/ABCs for SelfModelModule. (Base class/interface defined)
- [ ] Develop conceptual design for an integration example of combined CML modules (e.g., Perception-WM-LTM-Planning-BehaviorGeneration loop).
- [ ] Conceptually detail enhancements for 1-2 Concrete CML Modules (e.g., ConcreteLTM retrieval strategies, ConcreteMotivationalSystem intrinsic goal triggering).
- [ ] Define BaseWorldModel interface and ConcreteWorldModel structure, detailing components and interaction patterns with other CML modules.

### PiaSE (PiaAGI Simulation Environment)
- [ ] Detail the core simulation loop (time steps, agent perception/action phases, environment updates).
- [ ] Define a concrete Python API for agent perception and action within PiaSE.
- [ ] Conceptually design a simple initial environment (e.g., "TextBasedRoom") for PiaSE.
- [ ] Specify how a simple scenario would be defined and loaded in this TextBasedRoom.

### PiaAVT (PiaAGI Analysis & Visualization Toolkit)
- [ ] Define a standardized logging format/schema (e.g., JSON lines) for CML modules and PiaSE to output.
- [ ] Conceptually outline 2-3 basic analyses for early PiaAGI experiments (e.g., emotional valence over time, goal status changes).
- [ ] Sketch a simple visualization or textual summary for one basic analysis.

### PiaPES (PiaAGI Prompt Engineering Suite)
- [ ] Ensure prompt_engine_mvp.py classes can fully represent/serialize the detailed Cognitive_Module_Configuration from PiaAGI.md Appendix.
- [ ] Further conceptually detail the DevelopmentalCurriculumDesigner (PiaPES Section 2): structure, metadata, progression logic.
- [ ] Further conceptually detail the PromptEvaluationModule (PiaPES Section 9): inputs, outputs, integration with PiaSE/PiaAVT.

## Papers Directory Refinement - Next Steps
- [ ] Strategy: For AI_Cultural_Evolution.md: Research and select 1-2 actual relevant academic papers (2021-2024) using keywords [provided in planning step]; outline summaries per PAPER_TEMPLATE.md. (Strategy defined, research pending)
- [ ] Strategy: For AI_Narrative_Understanding.md: Research and select 1-2 actual relevant academic papers (2021-2024) using keywords [provided in planning step]; outline summaries per PAPER_TEMPLATE.md. (Strategy defined, research pending)
- [ ] Strategy: For AI_Ethical_Heuristics.md: Research and select 1-2 actual relevant academic papers (2021-2024) using keywords [provided in planning step]; outline summaries per PAPER_TEMPLATE.md. (Strategy defined, research pending)
- [ ] Briefly incorporate historical context of PiaC.md into PiaAGI.md (e.g., Section 1 or 2).
- [x] Explored and integrated Alita agent's MCP concepts into PiaAGI.md (Sections 3.6, 4.1, 4.5). Further specific detailing can be part of ongoing module refinement.
- [x] Ensured principles from Papers/Agent_Autonomous_Tool_Mastery.md are integrated into PiaAGI.md (Section 3.6, 4.1). Further elaboration can be part of ongoing module refinement.
- [x] Established Papers/PAPER_TEMPLATE.md for conceptual papers.

## Framework Philosophy and Consistency
- [x] Reviewed core documents; foundational viewpoint of 'agent as developing entity' is consistently articulated. To be maintained in future work.
- [ ] Further explore the implications of Chain-of-Thought (CoT) prompting, as discussed in `Papers/Chain_of_Thought_Alignment.md`, for PiaAGI's cognitive architecture (e.g., Planning, Self-Model) and developmental scaffolding strategies, reinforcing the "agent as human-like thinker" interaction paradigm.
- [ ] Expand upon the concepts outlined in `Papers/Human_Inspired_Agent_Blueprint.md` by conducting further research into each multidisciplinary area, identifying specific theories, models, and empirical findings that can concretely inform the design and development of PiaAGI's cognitive modules and overall architecture.

## Examples Directory Enhancement - Prioritized Development Plan
### Priority 1:
- [ ] Example: Examples/Cognitive_Configuration/Configuring_Emotion_Module.md (baseline states, reactivity, empathy).
- [ ] Example: Examples/Cognitive_Configuration/Configuring_Learning_Module.md (modes, rate adaptation, ethical heuristic updates).
- [ ] Example: Examples/Cognitive_Configuration/Configuring_Attention_Module.md (top-down/bottom-up biases).
- [ ] Example: Examples/Developmental_Scaffolding/Scaffolding_Ethical_Reasoning_Intro.md (PiaSapling, simple dilemmas).
### Priority 2:
- [ ] Example: Examples/Tool_Use/Adapting_Conceptual_Tools.md (agent modifies known conceptual tool).
- [ ] Example: Examples/Developmental_Scaffolding/Scaffolding_Intermediate_ToM.md (PiaSapling, false beliefs/intentions).
- [ ] Example: Examples/Developmental_Scaffolding/Cultivating_Intrinsic_Motivation.md (scenarios for curiosity/competence).
### Priority 3:
- [ ] Example: Examples/PiaPES_Usage/Generating_Prompt_With_PiaPES_Engine.md (ensure it uses a cognitive config example).
- [ ] Example: Examples/PiaPES_Usage/Defining_Developmental_Curriculum_PiaPES.md (conceptualizing curriculum object).
- [ ] Example: Examples/Cross_Stage_Development/Task_Summarization_Evolution.md (task for PiaSeedling, PiaSapling, PiaArbor).
### Priority 4:
- [ ] Example: Examples/Tool_Use/Agent_Requesting_New_Tool.md (agent identifies capability gap).
- [ ] Example: Examples/Tool_Use/Agent_Designing_Simple_Tool.md (PiaArbor designs tool - conceptual).
- [ ] Example: Examples/Internal_Metacognition/Self_Monitoring_PiaAVT_Principles.md (conceptual).
- [ ] Example: Examples/Internal_Metacognition/Internal_Experimentation_PiaSE_Principles.md (conceptual).
