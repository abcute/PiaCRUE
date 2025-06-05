# PiaAGI Project - Consolidated ToDo List (November 2024)

This document tracks the overall progress, completed tasks from recent reviews, and planned future development for the PiaAGI project and its research tools suite.
Items marked with `[x]` are completed. Items marked with `[ ]` are pending.

## I. PiaAGI Framework & Core Document (`PiaAGI.md`)
- [ ] **[USER_TASK] Diagram Integration in `PiaAGI.md`:** Manually integrate textual descriptions for Diagrams 8 (Planning/Decision-Making), 9 (Self-Model Components), and 10 (Motivational System Components) into the `PiaAGI.md` document where the `DIAGRAM DESCRIPTION START/END` placeholders exist. (From IMPROVEMENT_TODOLIST #13)
    *   **File(s):** `PiaAGI.md`.
    *   **Action:** User to copy-paste the relevant diagram descriptions from `docs/assets/diagram_descriptions.md` into `PiaAGI.md`.
- [ ] Define a conceptual framework for Architectural Maturation (beyond CML hooks, possibly as a paper or core `PiaAGI.md` section). (Derived from old ToDoList - potentially superseded by CML Advanced Roadmap's hooks, but keeping if a broader framework doc is intended).
- [ ] Further explore Chain-of-Thought prompting principles and their deeper integration into PiaAGI's cognitive cycle or specific module operations. (Derived from old ToDoList)

## II. PiaCML (Cognitive Module Library) & Message Bus
### Message Bus & Integration (From User's New List)
- [ ] **Implement Core Inter-Module Communication System (Phase 2 Cont.):**
    - [ ] Integrate `ConcreteEmotionModule` with the Message Bus (publish "EmotionalStateChange", subscribe to relevant triggers).
    - [ ] Systematically review and refactor existing CML modules to replace direct inter-module calls with Message Bus communication where appropriate for improved decoupling.
    - [ ] Implement true asynchronous message dispatching capabilities in `MessageBus`.
    - [ ] Explore and implement further advanced features for `MessageBus` (e.g., enhanced routing options, more Quality of Service levels, advanced filtering).

### Advanced Module Features (Post-Phase 1 Prototypes) (From User's New List)
- [ ] **Self-Model Module (SMM) - Phase 2:** Integration with LTM (self-history, trajectory) and Motivational System (goal-driven self-assessment, predictive self-modeling).
- [ ] **Self-Model Module (SMM) - Phase 3:** Advanced Self-Adaptation and Meta-Learning (automated model refinement, meta-cognitive strategy generation, self-driven exploration).
- [ ] **Long-Term Memory (LTM) Module - Phase 2:** Implement active forgetting mechanisms and memory consolidation/abstraction processes.
- [ ] **Long-Term Memory (LTM) Module - Phase 3:** Implement prospective memory, counterfactual memory/reasoning, and explore integration with generative models for memory reconstruction.
- [ ] **Motivational System Module (MSM) - Phase 2:** Integration with Emotion Module (emotion-modulated motivation) and Self-Model (self-aware goal setting, adaptive goal generation).
- [ ] **Motivational System Module (MSM) - Phase 3:** Strategic long-term planning, value learning/alignment, and resilience/grit modeling.
- [ ] **Emotion Module (EM) - Phase 2:** Strengthen emotion-cognition feedback loops, implement basic emotional regulation mechanisms, and basic social signal interpretation.
- [ ] **Emotion Module (EM) - Phase 3:** Develop capacity for complex social emotions, sophisticated emotional regulation strategies, and explore emotion-driven creativity/problem-solving.

### Other Pending CML Tasks
- [ ] **[REFACTOR] PiaCML Conceptual Logic Implementation:** Many methods in the concrete CML modules (e.g., `ConcreteWorldModel.predict_future_state`, `ConcreteSelfModelModule.perform_ethical_evaluation`, various planning and learning methods) currently contain placeholder logic, print statements indicating "conceptual," or highly simplified algorithms. (From IMPROVEMENT_TODOLIST #11)
    *   **Impact:** The core cognitive functions described in `PiaAGI.md` and module specifications are not yet fully operational.
    *   **File(s):** Numerous `PiaAGI_Research_Tools/PiaCML/concrete_*.py` files.
    *   **Suggested Action:** This is a broad area for ongoing research and development. For the immediate term, ensure that all placeholder methods have clear `NotImplementedError` or detailed comments explaining their conceptual nature if they are not intended to be functional in the MVP. Prioritize implementing basic functional versions of the most critical methods needed for simple agent scenarios.
- [ ] **[TEST] PiaCML Test Coverage for Advanced Features:** Unit tests for PiaCML modules, while good for some basic aspects (e.g., MessageBus, SelfModel confidence), do not yet cover the more complex conceptual algorithms and data structures being defined (e.g., ethical reasoning logic, WorldModel consistency checks, advanced SelfModel data components). (From IMPROVEMENT_TODOLIST #12)
    *   **Impact:** As these advanced features are implemented, lack of tests will reduce confidence in their correctness.
    *   **File(s):** `PiaAGI_Research_Tools/PiaCML/tests/`.
    *   **Suggested Action:** As functional logic replaces placeholders in CML modules, develop corresponding unit tests. For complex interactions, integration tests will also be needed.
- [ ] Begin drafting/implementing more detailed computational models for the Motivational System, beyond current specifications, focusing on dynamic goal generation and interaction between intrinsic/extrinsic motivators. (Derived from old ToDoList, refined - check overlap with MSM Phase 2/3).

## III. PiaSE (PiaAGI Simulation Environment)
- [ ] **Full PiaAGI Agent Instantiation:** Develop examples and helper classes in PiaSE to demonstrate assembling and running a complete PiaAGI agent (composed of multiple PiaCML modules using the Message Bus). (From User's New List)
- [ ] **Environment API & Library Expansion:** (Derived from User's New List & old ToDoList `[/]`)
    - [ ] Define a more robust Environment API for richer perceptions and actions.
    - [ ] Conceptually design 1-2 new environment types (e.g., "Social Dialogue Sandbox," "Crafting & Problem-Solving World").
    - [ ] Implement one of the newly conceptualized environment types as a prototype.
- [ ] **Dynamic Scenario Engine for Scaffolding:** Enhance PiaSE's scenario manager to allow dynamic adjustments (complexity, hints, new challenges) based on agent performance (from PiaAVT) or curriculum triggers (from PiaPES). (From User's New List - This covers existing DSE work and future enhancements).
- [ ] **Human-in-the-Loop (HITL) Interface:** Conceptualize how a human user could interact with a PiaSE simulation in real-time (e.g., as a tutor, evaluator, or another agent). (From User's New List)

## IV. PiaPES (PiaAGI Prompt Engineering Suite)
*(No items from "User's New List" explicitly for PiaPES general features. Items related to PiaPES for Meta-Cognition are in section VIII)*.

## V. PiaAVT (Agent Analysis & Visualization Toolkit)
- [ ] **Implement Conceptual Analyses:** Implement the already designed conceptual analyses: Goal Lifecycle Tracking, Emotional State Trajectory, and Task Performance Metrics. (From User's New List - Note: some basic versions were integrated in previous cycle).
- [ ] **Advanced Analytical Modules:** (From User's New List)
    - [ ] *Causal Analysis:* Conceptualize tools to infer causal links between agent actions, internal states, and outcomes.
    - [ ] *Behavioral Pattern Mining:* Design algorithms to identify recurring behavioral or cognitive state patterns.
    - [ ] *Ethical Reasoning Traceability:* Conceptualize tools to visualize how the Self-Model's ethical framework influences decisions.
- [ ] **Rich Cognitive Visualizations - Conceptual Designs:** (From User's New List)
    - [ ] *LTM Explorer:* Conceptualize interactive graph/timeline visualizations for LTM.
    - [ ] *Self-Model Dashboard:* Design a view summarizing key Self-Model aspects (confidence, values, capabilities).
    - [ ] *World Model Viewer:* Conceptualize tools to inspect and compare agent's World Model with PiaSE ground truth.
- [ ] **Meta-Cognitive Development Analysis (Logging part moved to Cross-Cutting):** (From User's New List - Logging part covered in Cross-Cutting)
    - [ ] *Dedicated Analyses:* Conceptualize PiaAVT analyses to detect patterns indicative of these meta-cognitive processes (based on extended logging spec).

## VI. Unified WebApp
*(No items from "User's New List" explicitly for Unified WebApp general features)*.

## VII. Examples & General Documentation
- [ ] Perform ongoing/second-pass updates to all READMEs for continued accuracy, clarity, and completeness, reflecting latest changes and future plans. (Derived from old ToDoList, following initial pass)
- [ ] Create and maintain `README_CN.md` and other translated documentation versions as needed. (Derived from old ToDoList, marked as ongoing/pending true-up)

## VIII. General Project / Research / Meta Tasks
### Cross-Cutting Future Enhancements (From User's New List)
- [ ] **Tooling for AGI's Internalization of Developer Tools & Meta-Cognitive Patterns (MCPs):**
    - [ ] **PiaAVT Logging for Meta-Cognition:** Formally propose and document new event types in `Logging_Specification.md` related to AGI self-analysis, internal simulation, MCP generation, and cognitive reconfiguration. (Covers "Extend Logging Spec" from AVT new list)
    - [ ] **PiaAVT Analysis for Meta-Cognition:** Design and prototype at least one conceptual analysis in PiaAVT to detect patterns indicative of an AGI internalizing tool principles.
    - [ ] **PiaPES Scaffolding for Meta-Cognition:** Design a conceptual `DevelopmentalScaffolding` curriculum segment in PiaPES aimed at encouraging an AGI to reflect on its problem-solving processes or generalize solutions into MCP-like structures.
    - [ ] **PiaCML Self-Model for MCPs:** Conceptualize how the `SelfModelModule` in PiaCML would represent and manage self-generated MCPs and meta-cognitive skills.

### Other General & Research Tasks
- [ ] Outline a research plan for Theory of Mind (ToM) acquisition and scaffolding in early-stage PiaAGI agents, detailing experimental setups in PiaSE. (Derived from old ToDoList)
- [ ] Conduct a survey and review of existing Python libraries relevant to implementing advanced aspects of the PiaAGI cognitive architecture (e.g., probabilistic reasoning, knowledge graphs, advanced ML models for CML components). (Derived from old ToDoList)
- [ ] Integrate insights from `Papers/AGI_Interdisciplinary_Memorandum.md` into various tool designs and the core `PiaAGI.md` framework where applicable. (Derived from old ToDoList)
- [ ] Expand upon the concepts in `Papers/Human_Inspired_Agent_Blueprint.md` to create more detailed specifications or design documents for agent construction. (Derived from old ToDoList)

---
## IX. Recently Completed (Nov 2024 Review & Fix Cycle)
- [x] **[BUG] PiaAVT Log Format Mismatch:** Modified `PiaAVTAPI` and its underlying `LoggingSystem` (in `PiaAGI_Research_Tools/PiaAVT/core/logging_system.py`, `api.py`, `webapp/app.py`, `cli.py` and `PiaAGI_Research_Tools/WebApp/backend/app.py`) to correctly parse JSONL files (line-by-line), aligning with `prototype_logger.py` and `Logging_Specification.md`. This also addresses schema alignment for core fields. (Corresponds to IMPROVEMENT_TODOLIST #1 and #6).
- [x] **[BUG] Unified WebApp Frontend Proxy Port Incorrect:** Changed the proxy target port in `PiaAGI_Research_Tools/WebApp/frontend/vite.config.js` to `5001`. (From IMPROVEMENT_TODOLIST #2)
- [x] **[BUG] PiaSE WebApp Outdated Import Paths:** Updated import paths in `PiaAGI_Research_Tools/PiaSE/WebApp/app.py` to use `PiaAGI_Research_Tools` instead of `PiaAGI_Hub`. (From IMPROVEMENT_TODOLIST #3)
- [x] **[DOC] PiaPES Example Script Inconsistencies:** Corrected class names and `save_template` call style in `Examples/PiaPES_Usage/Generating_Prompt_With_PiaPES_Engine.md` to align with `prompt_engine_mvp.py` and `USAGE.md`. (From IMPROVEMENT_TODOLIST #4)
- [x] **[DOC] Unified WebApp Backend Path Comments:** Updated comments in `PiaAGI_Research_Tools/WebApp/backend/app.py` to consistently refer to `PiaAGI_Research_Tools`. (From IMPROVEMENT_TODOLIST #5)
- [x] **[CONSISTENCY] PiaSE `Environment` Interface Discrepancies:** Added `agent_id: Optional[str] = None` to `Environment.get_action_space()` and added `@abstractmethod def get_environment_info(self) -> Dict[str, Any]: pass` to the `Environment` ABC in `PiaAGI_Research_Tools/PiaSE/core_engine/interfaces.py`. Ensured concrete environments (`grid_world.py`, `text_based_room.py`) match the updated ABC. Added `reconfigure` method to `Environment` ABC and concrete implementations. (From IMPROVEMENT_TODOLIST #7)
- [x] **[BUG] BasicGridAgent Import Path:** Updated import path in `PiaAGI_Research_Tools/PiaSE/agents/basic_grid_agent.py` to use relative import `from ..core_engine.interfaces ...`. (From IMPROVEMENT_TODOLIST #8)
- [x] **[DOC] General README Updates (Initial Pass):** Performed a systematic pass over specified READMEs (`PiaAGI_Research_Tools/README.md`, `PiaCML/README.md`, `PiaSE/README.md`, `PiaPES/README.md`, `PiaAVT/README.md`, `Examples/README.md`, `Papers/README.md`) for accuracy, consistency, and clarity. (From IMPROVEMENT_TODOLIST #9)
- [x] **[ENHANCEMENT] PiaSE DSE Environment Reconfiguration:** Enhanced `BasicSimulationEngine`'s DSE loop in `PiaAGI_Research_Tools/PiaSE/core_engine/basic_engine.py` to parse `current_step_obj.environment_config` and `current_step_obj.agent_config_overrides`, calling `environment.reconfigure()` and `agent.configure()` respectively. (From IMPROVEMENT_TODOLIST #10)
