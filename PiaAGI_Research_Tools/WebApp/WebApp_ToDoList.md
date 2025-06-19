# PiaAGI Unified WebApp - Enhancements ToDo List

This document outlines planned enhancements for the PiaAGI Unified WebApp to improve its clarity, intuition, and ability to visualize the integrated PiaAGI framework.

## P1: Core Workflow Enhancements

- [ ] **Implement PiaAGI Experiment Runner (P1-Overall)**
    - <思考>This is the absolute core functionality of the Unified WebApp. Without the ability to configure, run, and see basic results of an experiment, the WebApp serves little purpose in integrating the PiaAGI tool suite. All sub-tasks here are critical for an MVP.</思考>
    - <优先级>高</优先级>
    - [ ] `[P1-1]` Backend: Design API to accept PiaPES prompt/curriculum ref, PiaSE scenario ref, and PiaAGI agent configuration.
        - <思考>Essential backend foundation for the experiment runner.</思考>
        - <优先级>高</优先级>
    - [ ] `[P1-2]` Backend: Implement logic to initialize a full PiaAGI agent (CML modules) based on the configuration.
        - <思考>Core logic for bringing an agent to life based on user specs.</思考>
        - <优先级>高</优先级>
    - [ ] `[P1-3]` Backend: Implement logic to run the configured PiaAGI agent in the specified PiaSE scenario, collecting logs.
        - <思考>Core logic for executing the simulation and gathering data.</思考>
        - <优先级>高</优先级>
    - [ ] `[P1-4]` Frontend: Design UI (new page/section) for "Experiment Runner" (prompt selection, scenario selection, run initiation).
        - <思考>Essential frontend for users to define and start experiments.</思考>
        - <优先级>高</优先级>
    - [ ] `[P1-5]` Frontend: Display basic simulation results (textual logs, summary stats, links to detailed AVT analysis).
        - <思考>Critical for users to see the outcome of their experiments.</思考>
        - <优先级>高</优先级>
    - [ ] `[P1-6]` Frontend (Optional Stretch): Basic visualization of agent's primary actions/state changes during simulation.
        - <思考>While labeled "optional stretch," some basic, near-real-time feedback on agent activity during a run (or immediately post-run) would significantly enhance usability and understanding, even if it's simple. However, it's less critical than displaying final logs and stats.</思考>
        - <优先级>中</优先级>

## P2: Module-Specific Visualizations & Interface Improvements

- [ ] **CML Visualizations & Interaction Enhancements (P2-Overall)**
    - <思考>Visualizing the internal state of CML modules is key to understanding agent cognition. These provide a window into the "mind" of the agent.</思考>
    - <优先级>中</优先级>
    - [ ] `[P2-1]` Working Memory Module:
        - [ ] Frontend: Display current WM items (list/tags).
        - [ ] Frontend: Show item salience and active focus.
        - [ ] Backend: Ensure WM API provides necessary data.
        - <思考>WM is central to active cognition. Visualizing its contents and focus is highly valuable for debugging and understanding immediate processing.</思考>
        - <优先级>中</优先级>
    - [ ] `[P2-2]` Motivational System Module:
        - [ ] Frontend: Visualize current goal hierarchy (tree/list), active goals, priorities/intensities.
        - [ ] Frontend: Display recent intrinsic rewards or significant motivation state changes.
        - [ ] Backend: Ensure MSM API provides necessary data.
        - <思考>Understanding the agent's motivations and goals is crucial for interpreting its behavior. This has high diagnostic value.</思考>
        - <优先级>高</优先级>
    - [ ] `[P2-3]` Emotion Module:
        - [ ] Frontend: Display current VAD state (sliders/numerical) and primary discrete emotion.
        - [ ] Frontend (Optional): List key recent appraisals influencing emotion.
        - [ ] Backend: Ensure Emotion API provides necessary data.
        - <思考>Emotion is a key modulator in PiaAGI. Visualizing it helps understand its influence on cognition and behavior.</思考>
        - <优先级>中</优先级>
- [ ] **SE Interface Enhancements (P2-Overall)**
    - <思考>Improving the interface for selecting scenarios and agents makes the experiment setup process more flexible and user-friendly.</思考>
    - <优先级>中</优先级>
    - [ ] `[P2-4]` Scenario Selection:
        - [ ] Backend: API endpoint to list available PiaSE scenarios.
        - [ ] Frontend: Dropdown on `SEPage` to select scenarios.
        - <思考>Essential for allowing users to choose different test environments.</思考>
        - <优先级>中</优先级>
    - [ ] `[P2-5]` Agent Selection (Initial Simple Agents):
        - [ ] Frontend: Allow selection between different simple, hardcoded agents for PiaSE runs (if backend supports).
        - <思考>Allows for comparative studies and testing of different agent archetypes. Depends on backend support for multiple agent types.</思考>
        - <优先级>中</优先级>
- [ ] **AVT Integration Enhancements (In-WebApp) (P2-Overall)**
    - <思考>Integrating some basic AVT plots directly into the WebApp provides immediate analytical feedback without needing to switch tools.</思考>
    - <优先级>中</优先级>
    - [ ] `[P2-6]` Goal Lifecycle Count Plot:
        - [ ] Backend: Extend basic AVT analysis to return goal event counts.
        - [ ] Frontend: Display as a bar chart on `AVTPage`.
        - <思考>Provides a quick overview of goal-oriented performance.</思考>
        - <优先级>中</优先级>
    - [ ] `[P2-7]` Basic VAD Trajectory Plot:
        - [ ] Backend: AVT API to provide simplified VAD time-series data if present in logs.
        - [ ] Frontend: Basic line plot of V, A, D over time on `AVTPage`.
        - <思考>Offers a visual summary of emotional dynamics over time.</思考>
        - <优先级>中</优先级>

## P3: General UI/UX and Conceptual Visualizations

- [ ] **PiaPES Visualization Enhancements (P3-Overall)**
    - <思考>Visualizing complex PiaPES structures like curricula can greatly aid understanding and design.</思考>
    - <优先级>低</优先级>
    - [ ] `[P3-1]` Developmental Curriculum Flowchart:
        - [ ] Frontend: Implement simple flowchart/graph view for `DevelopmentalCurriculum` steps.
        - [ ] Backend: Ensure curriculum data is easily parsable.
        - <思考>Makes complex learning sequences much easier to grasp.</思考>
        - <优先级>低</优先级>
    - [ ] `[P3-2]` Cognitive Configuration Summary (Conceptual):
        - [ ] Frontend: Display human-readable summary of cognitive configurations on "View Prompt" page.
        - <思考>Improves clarity when reviewing detailed agent setups.</思考>
        - <优先级>低</优先级>
- [ ] **UI/UX & Guidance (P3-Overall)**
    - <思考>General usability improvements are important for long-term adoption and efficient use of the WebApp.</思考>
    - <优先级>中</优先级>
    - [ ] `[P3-3]` Implement tooltips/info icons for complex settings in CML, PES, SE interfaces.
        - <思考>Essential for making advanced configurations accessible and reducing errors. High impact for usability.</思考>
        - <优先级>中</优先级>
    - [ ] `[P3-4]` Add brief explanatory text on each main page (CML, PES, SE, AVT) about the tool's purpose and role.
        - <思考>Helps orient users, especially new ones. Good usability feature.</思考>
        - <优先级>中</优先级>
    - [ ] `[P3-5]` High-Level Framework Diagram:
        - [ ] Frontend: Add static image/diagram of PiaAGI architecture to HomePage or "About/Framework" page.
        - [ ] Frontend: Briefly describe how WebApp tools relate to this architecture.
        - <思考>Provides conceptual context for users. Useful, but less critical for immediate operation than functional features.</思考>
        - <优先级>低</优先级>
