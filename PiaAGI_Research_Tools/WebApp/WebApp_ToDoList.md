# PiaAGI Unified WebApp - Enhancements ToDo List

This document outlines planned enhancements for the PiaAGI Unified WebApp to improve its clarity, intuition, and ability to visualize the integrated PiaAGI framework.

## P1: Core Workflow Enhancements

- [ ] **Implement PiaAGI Experiment Runner (P1-Overall)**
    - [ ] `[P1-1]` Backend: Design API to accept PiaPES prompt/curriculum ref, PiaSE scenario ref, and PiaAGI agent configuration.
    - [ ] `[P1-2]` Backend: Implement logic to initialize a full PiaAGI agent (CML modules) based on the configuration.
    - [ ] `[P1-3]` Backend: Implement logic to run the configured PiaAGI agent in the specified PiaSE scenario, collecting logs.
    - [ ] `[P1-4]` Frontend: Design UI (new page/section) for "Experiment Runner" (prompt selection, scenario selection, run initiation).
    - [ ] `[P1-5]` Frontend: Display basic simulation results (textual logs, summary stats, links to detailed AVT analysis).
    - [ ] `[P1-6]` Frontend (Optional Stretch): Basic visualization of agent's primary actions/state changes during simulation.

## P2: Module-Specific Visualizations & Interface Improvements

- [ ] **CML Visualizations & Interaction Enhancements (P2-Overall)**
    - [ ] `[P2-1]` Working Memory Module:
        - [ ] Frontend: Display current WM items (list/tags).
        - [ ] Frontend: Show item salience and active focus.
        - [ ] Backend: Ensure WM API provides necessary data.
    - [ ] `[P2-2]` Motivational System Module:
        - [ ] Frontend: Visualize current goal hierarchy (tree/list), active goals, priorities/intensities.
        - [ ] Frontend: Display recent intrinsic rewards or significant motivation state changes.
        - [ ] Backend: Ensure MSM API provides necessary data.
    - [ ] `[P2-3]` Emotion Module:
        - [ ] Frontend: Display current VAD state (sliders/numerical) and primary discrete emotion.
        - [ ] Frontend (Optional): List key recent appraisals influencing emotion.
        - [ ] Backend: Ensure Emotion API provides necessary data.
- [ ] **SE Interface Enhancements (P2-Overall)**
    - [ ] `[P2-4]` Scenario Selection:
        - [ ] Backend: API endpoint to list available PiaSE scenarios.
        - [ ] Frontend: Dropdown on `SEPage` to select scenarios.
    - [ ] `[P2-5]` Agent Selection (Initial Simple Agents):
        - [ ] Frontend: Allow selection between different simple, hardcoded agents for PiaSE runs (if backend supports).
- [ ] **AVT Integration Enhancements (In-WebApp) (P2-Overall)**
    - [ ] `[P2-6]` Goal Lifecycle Count Plot:
        - [ ] Backend: Extend basic AVT analysis to return goal event counts.
        - [ ] Frontend: Display as a bar chart on `AVTPage`.
    - [ ] `[P2-7]` Basic VAD Trajectory Plot:
        - [ ] Backend: AVT API to provide simplified VAD time-series data if present in logs.
        - [ ] Frontend: Basic line plot of V, A, D over time on `AVTPage`.

## P3: General UI/UX and Conceptual Visualizations

- [ ] **PiaPES Visualization Enhancements (P3-Overall)**
    - [ ] `[P3-1]` Developmental Curriculum Flowchart:
        - [ ] Frontend: Implement simple flowchart/graph view for `DevelopmentalCurriculum` steps.
        - [ ] Backend: Ensure curriculum data is easily parsable.
    - [ ] `[P3-2]` Cognitive Configuration Summary (Conceptual):
        - [ ] Frontend: Display human-readable summary of cognitive configurations on "View Prompt" page.
- [ ] **UI/UX & Guidance (P3-Overall)**
    - [ ] `[P3-3]` Implement tooltips/info icons for complex settings in CML, PES, SE interfaces.
    - [ ] `[P3-4]` Add brief explanatory text on each main page (CML, PES, SE, AVT) about the tool's purpose and role.
    - [ ] `[P3-5]` High-Level Framework Diagram:
        - [ ] Frontend: Add static image/diagram of PiaAGI architecture to HomePage or "About/Framework" page.
        - [ ] Frontend: Briefly describe how WebApp tools relate to this architecture.
