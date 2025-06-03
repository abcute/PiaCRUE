import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple, Callable

# Assuming PiaPES prompt_engine_mvp.py is accessible for DevelopmentalCurriculum structures
# Adjust import path as necessary.
try:
    # Attempting to import from a potential PiaPES location
    from PiaAGI_Research_Tools.PiaPES.prompt_engine_mvp import DevelopmentalCurriculum, CurriculumStep
    PIAPES_FOUND = True
except ImportError:
    print("DSE: PiaPES DevelopmentalCurriculum/CurriculumStep not found. Using DSE's local placeholders.")
    PIAPES_FOUND = False
    class DevelopmentalCurriculum:
        def __init__(self, name: str, steps: List[Any], description: str = "", target_developmental_stage: str = "", author: str = "", version: str = "", **kwargs):
            self.name = name
            self.description = description
            self.target_developmental_stage = target_developmental_stage
            self.steps = steps # List of CurriculumStep instances
            self.author = author
            self.version = version
            # Allow other fields from JSON via kwargs if needed later
            for key, value in kwargs.items():
                setattr(self, key, value)

    class CurriculumStep:
        def __init__(self, name: str, order: int, prompt_reference: str,
                     completion_criteria: Optional[List[Dict[str,Any]]] = None,
                     adaptation_rules: Optional[List[Tuple[str, str]]] = None,
                     environment_config_overrides: Optional[Dict] = None,
                     agent_config_overrides: Optional[Dict] = None,
                     **kwargs):
            self.name = name
            self.order = order # Should be unique within a curriculum
            self.prompt_reference = prompt_reference
            self.completion_criteria = completion_criteria if completion_criteria else []
            self.adaptation_rules = adaptation_rules if adaptation_rules else []
            self.environment_config_overrides = environment_config_overrides if environment_config_overrides else {}
            self.agent_config_overrides = agent_config_overrides if agent_config_overrides else {}
            # Allow other fields from JSON via kwargs
            for key, value in kwargs.items():
                setattr(self, key, value)


class CurriculumManager:
    def __init__(self):
        self.current_curriculum: Optional[DevelopmentalCurriculum] = None
        # agent_id -> {"current_step_order": int, "completed_steps": List[int], "step_attempts": {step_order: count}}
        self.agent_progress: Dict[str, Dict[str, Any]] = {}

    def load_curriculum_from_file(self, filepath: str) -> bool:
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            # Ensure steps data is correctly formed for CurriculumStep placeholder if used
            step_data_list = data.get("steps", [])
            parsed_steps = []
            for step_data_item in step_data_list:
                # Ensure adaptation_rules is a list of tuples (pairs)
                rules = step_data_item.get("adaptation_rules", [])
                if rules and isinstance(rules, list) and all(isinstance(r, list) and len(r) == 2 for r in rules):
                     step_data_item["adaptation_rules"] = [tuple(r) for r in rules]
                elif rules: # Malformed, default to empty
                    print(f"Warning: Malformed adaptation_rules for step '{step_data_item.get('name', 'Unknown')}'. Defaulting to empty. Expected list of [condition, action] pairs.")
                    step_data_item["adaptation_rules"] = []

                parsed_steps.append(CurriculumStep(**step_data_item))

            self.current_curriculum = DevelopmentalCurriculum(
                name=data.get("name", "Unnamed Curriculum"),
                description=data.get("description", ""),
                target_developmental_stage=data.get("target_developmental_stage", ""),
                steps=parsed_steps,
                author=data.get("author", ""),
                version=data.get("version", "0.0.0")
            )
            if self.current_curriculum.steps:
                self.current_curriculum.steps.sort(key=lambda s: s.order)
            print(f"DSE: Curriculum '{self.current_curriculum.name}' loaded with {len(self.current_curriculum.steps)} steps.")
            return True
        except Exception as e:
            print(f"DSE: Error loading curriculum from {filepath}: {e}")
            self.current_curriculum = None
            return False

    def initialize_agent_progress(self, agent_id: str):
        if not self.current_curriculum:
            print("DSE: No curriculum loaded to initialize agent progress.")
            return
        self.agent_progress[agent_id] = {
            "current_step_order": -1,  # Indicates that the first step has not yet been started
            "completed_steps": [],
            "step_attempts": {}  # To store attempts for each step_order
        }
        print(f"DSE: Initialized progress for agent {agent_id}.")

    def get_next_step(self, agent_id: str) -> Optional[CurriculumStep]:
        if not self.current_curriculum or not self.current_curriculum.steps or agent_id not in self.agent_progress:
            return None

        current_order = self.agent_progress[agent_id]["current_step_order"]

        if current_order == -1: # Agent is starting the curriculum, or finished last step and needs the very first one.
            # This ensures that if current_order is -1 (initial state), it correctly picks the first step.
            return self.current_curriculum.steps[0]

        # Find the current step's index in the sorted list
        current_step_index = -1
        for idx, step in enumerate(self.current_curriculum.steps):
            if step.order == current_order:
                current_step_index = idx
                break

        if current_step_index != -1:
            if current_step_index + 1 < len(self.current_curriculum.steps):
                # Return the next step in sequence
                return self.current_curriculum.steps[current_step_index + 1]
        else: # current_order not found, could be an issue or end of a branch
            print(f"DSE Warning: Current step order {current_order} not found for agent {agent_id}. Cannot determine next step by sequence.")

        return None # No more steps in sequence or current step was invalid

    def set_current_step(self, agent_id: str, step_order: int, increment_attempt: bool = True) -> Optional[CurriculumStep]:
        if not self.current_curriculum or agent_id not in self.agent_progress:
            print(f"DSE: Cannot set current step. Curriculum or agent progress for {agent_id} not initialized.")
            return None

        target_step: Optional[CurriculumStep] = None
        for step in self.current_curriculum.steps:
            if step.order == step_order:
                target_step = step
                break

        if target_step:
            self.agent_progress[agent_id]["current_step_order"] = step_order
            if increment_attempt:
                self.agent_progress[agent_id].setdefault("step_attempts", {})
                current_attempts = self.agent_progress[agent_id]["step_attempts"].get(step_order, 0)
                self.agent_progress[agent_id]["step_attempts"][step_order] = current_attempts + 1
                print(f"DSE: Agent {agent_id} now on step '{target_step.name}' (Order: {step_order}, Attempt: {current_attempts + 1}).")
            else:
                # If not incrementing, ensure attempt count exists if step is being re-evaluated without new attempt
                self.agent_progress[agent_id].setdefault("step_attempts", {}).setdefault(step_order, 0)
                print(f"DSE: Agent {agent_id} set to step '{target_step.name}' (Order: {step_order}, Attempt count not incremented this call).")
            return target_step
        else:
            print(f"DSE: Error: Step order {step_order} not found in curriculum for agent {agent_id}.")
            self.agent_progress[agent_id]["current_step_order"] = -1 # Mark as invalid/no current step
            return None

    def complete_step(self, agent_id: str, step_order: int):
        if agent_id in self.agent_progress:
            if step_order not in self.agent_progress[agent_id]["completed_steps"]:
                self.agent_progress[agent_id]["completed_steps"].append(step_order)
            print(f"DSE: Agent {agent_id} marked step order {step_order} as completed.")

    def get_current_step_object(self, agent_id: str) -> Optional[CurriculumStep]:
        if not self.current_curriculum or agent_id not in self.agent_progress:
            return None
        current_order = self.agent_progress[agent_id]["current_step_order"]
        if current_order == -1:
            return None
        for step in self.current_curriculum.steps:
            if step.order == current_order:
                return step
        return None

    def get_step_attempts(self, agent_id: str, step_order: int) -> int:
        if agent_id not in self.agent_progress: return 0
        return self.agent_progress[agent_id].get("step_attempts", {}).get(step_order, 0)

    def get_step_by_name_or_order(self, identifier: Any) -> Optional[CurriculumStep]: # identifier can be str (name) or int (order)
        if not self.current_curriculum:
            return None
        for step in self.current_curriculum.steps:
            if isinstance(identifier, int) and step.order == identifier:
                return step
            elif isinstance(identifier, str) and step.name == identifier:
                return step
        return None


class PiaAVTInterface(ABC):
    @abstractmethod
    def get_performance_metric(self, agent_id: str, metric_name: str, context: Optional[Dict] = None) -> Any:
        pass

    @abstractmethod
    def check_event_occurred(self, agent_id: str, event_signature: Dict, time_window: Optional[int]=None) -> bool:
        pass

class MockPiaAVTInterface(PiaAVTInterface):
    def __init__(self):
        self.mock_metrics: Dict[str, Dict[str, Any]] = {}
        self.mock_events: List[Tuple[str, Dict[str, Any]]] = []

    def set_metric(self, agent_id: str, metric_name: str, value: Any):
        if agent_id not in self.mock_metrics:
            self.mock_metrics[agent_id] = {}
        self.mock_metrics[agent_id][metric_name] = value
        # print(f"MockPiaAVT: Set metric for {agent_id}: {metric_name} = {value}") # Reduce noise for engine integration

    def log_event(self, agent_id: str, event_signature: Dict):
        self.mock_events.append((agent_id, event_signature))
        # print(f"MockPiaAVT: Logged event for {agent_id}: {event_signature}") # Reduce noise


    def get_performance_metric(self, agent_id: str, metric_name: str, context: Optional[Dict] = None) -> Any:
        val = self.mock_metrics.get(agent_id, {}).get(metric_name, None)
        # print(f"MockPiaAVT: Queried metric for {agent_id}: {metric_name}. Returning: {val}") # Reduce noise
        return val

    def check_event_occurred(self, agent_id: str, event_signature: Dict, time_window: Optional[int]=None) -> bool:
        found = (agent_id, event_signature) in self.mock_events
        # print(f"MockPiaAVT: Checked event for {agent_id}: {event_signature}. Found: {found}") # Reduce noise
        return found


class AdaptationDecisionModule:
    def __init__(self, avt_interface: PiaAVTInterface): # avt_interface passed here
        self.avt_interface = avt_interface

    def evaluate_step_completion(self, agent_id: str, current_step: CurriculumStep) -> bool: # Removed avt_interface from args
        if not hasattr(current_step, 'completion_criteria') or not current_step.completion_criteria:
            # print(f"DSE ADM: No completion criteria for step '{current_step.name}', assuming not auto-completed.") # Reduce noise
            return False

        for criterion in current_step.completion_criteria:
            metric_name = criterion.get("metric")
            expected_value_str = str(criterion.get("value"))
            operator = criterion.get("operator", "==")

            actual_value = self.avt_interface.get_performance_metric(agent_id, metric_name) # Use self.avt_interface
            if actual_value is None: return False

            try:
                expected_value: Any
                if '.' in expected_value_str: expected_value = float(expected_value_str)
                elif expected_value_str.lower() == "true": expected_value = True
                elif expected_value_str.lower() == "false": expected_value = False
                elif expected_value_str.isdigit() or (expected_value_str.startswith('-') and expected_value_str[1:].isdigit()):
                    expected_value = int(expected_value_str)
                else: expected_value = expected_value_str

                match_eval = False
                actual_value_typed = actual_value
                if isinstance(expected_value, (int, float)) and isinstance(actual_value, (int,float,str)): # Check if actual can be cast
                    try: actual_value_typed = type(expected_value)(actual_value)
                    except (ValueError, TypeError): return False
                elif type(actual_value) != type(expected_value) and not (isinstance(actual_value, bool) or isinstance(expected_value, bool)): # Avoid direct type mismatch for non-numerics unless bool
                    if str(actual_value).lower() == str(expected_value).lower(): # attempt string comparison for bools like "true" == True
                         pass # Let it be evaluated by operators
                    else:
                        return False


                if operator == "==": match_eval = (actual_value_typed == expected_value)
                elif operator == "<": match_eval = (actual_value_typed < expected_value)
                elif operator == ">": match_eval = (actual_value_typed > expected_value)
                elif operator == "<=": match_eval = (actual_value_typed <= expected_value)
                elif operator == ">=": match_eval = (actual_value_typed >= expected_value)
                elif operator == "!=": match_eval = (actual_value_typed != expected_value)
                else: print(f"DSE ADM: Unknown operator '{operator}' in completion criteria."); return False

                if not match_eval: return False
            except ValueError as e:
                print(f"DSE ADM: Error converting value in completion criteria for metric '{metric_name}': {e}"); return False

        # print(f"DSE ADM: All completion criteria met for step '{current_step.name}' for agent {agent_id}.") # Reduce noise
        return True


    def evaluate_adaptation_rules(self, agent_id: str, current_step: CurriculumStep, attempt_count: int) -> str: # Removed avt_interface from args
        if not hasattr(current_step, 'adaptation_rules') or not current_step.adaptation_rules:
            return "PROCEED"

        for condition_str, action_str in current_step.adaptation_rules:
            parts = condition_str.split()
            if len(parts) == 3:
                metric_name, operator, value_str = parts[0], parts[1], parts[2]

                actual_value: Any
                if metric_name == "step_attempts":
                    actual_value = attempt_count
                else:
                    actual_value = self.avt_interface.get_performance_metric(agent_id, metric_name) # Use self.avt_interface

                if actual_value is None: continue

                try:
                    expected_value: Any
                    if '.' in value_str: expected_value = float(value_str)
                    elif value_str.lower() == "true": expected_value = True
                    elif value_str.lower() == "false": expected_value = False
                    elif value_str.isdigit() or (value_str.startswith('-') and value_str[1:].isdigit()): expected_value = int(value_str)
                    else: expected_value = value_str

                    actual_value_typed = actual_value
                    if isinstance(expected_value, (int, float)) and isinstance(actual_value, (int,float,str)):
                         try: actual_value_typed = type(expected_value)(actual_value)
                         except (ValueError, TypeError): continue
                    elif type(actual_value) != type(expected_value) and not (isinstance(actual_value, bool) or isinstance(expected_value, bool)):
                        if str(actual_value).lower() == str(expected_value).lower():
                            pass
                        else:
                            continue


                    match_eval = False
                    if operator == "==": match_eval = (actual_value_typed == expected_value)
                    elif operator == "<": match_eval = (actual_value_typed < expected_value)
                    elif operator == ">": match_eval = (actual_value_typed > expected_value)
                    elif operator == "<=": match_eval = (actual_value_typed <= expected_value)
                    elif operator == ">=": match_eval = (actual_value_typed >= expected_value)
                    elif operator == "!=": match_eval = (actual_value_typed != expected_value)
                    else: continue

                    if match_eval:
                        # print(f"DSE ADM: Adaptation rule met for {agent_id} on step '{current_step.name}': {condition_str}. Action: {action_str}") # Reduce noise
                        return action_str
                except ValueError: continue
            else:
                print(f"DSE ADM: Malformed condition string '{condition_str}' in step '{current_step.name}'. Skipping.")

        return "PROCEED"


class EnvironmentModifierInterface(ABC):
    @abstractmethod
    def adjust_difficulty(self, params: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def introduce_element(self, element_config: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def provide_indirect_hint(self, hint_details: Dict[str, Any]) -> bool:
        pass

# Example of how a main DSE orchestrator might look (conceptual)
# This would be part of or used by BasicSimulationEngine or a higher-level engine.
class DynamicScenarioOrchestrator:
    def __init__(self,
                 curriculum_manager: CurriculumManager,
                 adaptation_module: AdaptationDecisionModule,
                 # scenario_setup_module, # Would handle PiaAGI prompt loading & agent/env config
                 # pia_se_engine # The core simulation engine
                 ):
        self.curriculum_manager = curriculum_manager
        self.adaptation_module = adaptation_module
        # self.scenario_setup_module = scenario_setup_module
        # self.pia_se_engine = pia_se_engine
        print("DSE Orchestrator Initialized (Conceptual)")

    def run_agent_curriculum(self, agent_id: str, curriculum_filepath: str):
        if not self.curriculum_manager.load_curriculum_from_file(curriculum_filepath):
            print(f"DSE Orchestrator: Failed to load curriculum for agent {agent_id}.")
            return

        self.curriculum_manager.initialize_agent_progress(agent_id)

        current_step = self.curriculum_manager.set_current_step(agent_id, self.curriculum_manager.get_next_step(agent_id).order)

        while current_step:
            print(f"\nDSE Orchestrator: Agent {agent_id} starting step '{current_step.name}' (Order: {current_step.order})")

            # 1. SCENARIO SETUP (Conceptual - would involve ScenarioSetupModule)
            #    - Load prompt from current_step.prompt_reference
            #    - Configure agent (e.g. PiaAGIAgent) using prompt and step.agent_config_overrides
            #    - Configure environment using step.environment_config_overrides
            print(f"   Action: Setup agent and environment for prompt '{current_step.prompt_reference}'.")

            # 2. RUN SIMULATION STEP (Conceptual - would involve BasicSimulationEngine)
            #    - engine.run_simulation_segment(duration, or until step-specific goal)
            #    - This would generate logs that PiaAVT processes.
            print(f"   Action: Run simulation for step '{current_step.name}'.")
            # For testing, let's mock some performance data after a "run"
            if isinstance(self.adaptation_module.avt_interface, MockPiaAVTInterface):
                if current_step.name == "Easy Task":
                    self.adaptation_module.avt_interface.set_metric(agent_id, "task_success", 1) # 1 for true
                    self.adaptation_module.avt_interface.set_metric(agent_id, "completion_time", 50)
                elif current_step.name == "Hard Task":
                     self.adaptation_module.avt_interface.set_metric(agent_id, "task_success", 0) # 0 for false
                     self.adaptation_module.avt_interface.set_metric(agent_id, "consecutive_failures",
                                                                     self.curriculum_manager.get_step_attempts(agent_id, current_step.order))


            # 3. EVALUATE COMPLETION
            completed = self.adaptation_module.evaluate_step_completion(agent_id, current_step)
            if completed:
                self.curriculum_manager.complete_step(agent_id, current_step.order)
                decision = "PROCEED" # Usually proceed if completed, unless rules override
            else:
                # 4. EVALUATE ADAPTATION (if not completed, or if rules apply even on completion)
                decision = self.adaptation_module.evaluate_adaptation_rules(agent_id, current_step, self.curriculum_manager)

            print(f"   Decision for step '{current_step.name}': {decision}")

            # 5. HANDLE DECISION
            if decision == "PROCEED":
                next_step_obj = self.curriculum_manager.get_next_step(agent_id)
                if next_step_obj:
                    current_step = self.curriculum_manager.set_current_step(agent_id, next_step_obj.order)
                else:
                    print(f"DSE Orchestrator: Agent {agent_id} completed all steps in curriculum '{self.curriculum_manager.current_curriculum.name}'.")
                    current_step = None
            elif "BRANCH_TO_" in decision:
                target_step_order = int(decision.split("BRANCH_TO_")[-1])
                current_step = self.curriculum_manager.set_current_step(agent_id, target_step_order)
                if not current_step: print(f"DSE Orchestrator: Branch target step order {target_step_order} not found!")
            elif decision == "REPEAT_STEP": # Simplified, could have REPEAT_MODIFIED
                current_step = self.curriculum_manager.set_current_step(agent_id, current_step.order) # Re-triggers attempt count
                print(f"   Action: Repeating step '{current_step.name}'.")
            elif "APPLY_HINT_" in decision:
                hint_id = decision.split("APPLY_HINT_")[-1]
                print(f"   Action: Apply hint '{hint_id}'. (Environment/Agent modification would happen here).")
                # Agent might retry the step after hint
                current_step = self.curriculum_manager.set_current_step(agent_id, current_step.order)
            else: # Unknown decision or specific modifications needed
                print(f"DSE Orchestrator: Halting. Unhandled decision '{decision}' or further action needed.")
                current_step = None

        print(f"DSE Orchestrator: Curriculum run finished for agent {agent_id}.")


if __name__ == "__main__":
    print("--- DSE Component Test ---")
    # Test CurriculumManager
    cm = CurriculumManager()
    # Create a dummy curriculum JSON file for testing
    dummy_curriculum_data = {
        "name": "Test Curriculum",
        "description": "A sample curriculum for DSE testing.",
        "target_developmental_stage": "PiaSeedling",
        "author": "TestUser",
        "version": "1.0",
        "steps": [
            {"name": "Easy Task", "order": 1, "prompt_reference": "easy_prompt.txt",
             "completion_criteria": [{"metric": "task_success", "operator": "==", "value": "1"}],
             "adaptation_rules": [["consecutive_failures == 2", "APPLY_HINT_EASY"]]},
            {"name": "Hard Task", "order": 2, "prompt_reference": "hard_prompt.txt",
             "completion_criteria": [{"metric": "task_success", "operator": "==", "value": "1"}],
             "adaptation_rules": [["step_attempts >= 3", "BRANCH_TO_1"], ["task_success == 0", "REPEAT_STEP"]]}
        ]
    }
    dummy_filepath = "dummy_curriculum.json"
    with open(dummy_filepath, 'w') as f:
        json.dump(dummy_curriculum_data, f, indent=2)

    cm.load_curriculum_from_file(dummy_filepath)
    if cm.current_curriculum:
        print(f"Loaded curriculum: {cm.current_curriculum.name}")
        for s in cm.current_curriculum.steps:
            print(f"  Step {s.order}: {s.name}, Rules: {s.adaptation_rules}")

    # Test MockPiaAVTInterface and AdaptationDecisionModule
    mock_avt = MockPiaAVTInterface()
    adm = AdaptationDecisionModule(avt_interface=mock_avt)

    # Test Orchestrator
    orchestrator = DynamicScenarioOrchestrator(cm, adm)
    test_agent_id = "agent_dse_test"
    orchestrator.run_agent_curriculum(test_agent_id, dummy_filepath)

    # Example of how metrics would affect next run for "Hard Task"
    print("\n--- Second run for Hard Task (assuming it failed and repeated) ---")
    # Assume agent is on "Hard Task" (order 2) and failed once
    cm.agent_progress[test_agent_id]["current_step_order"] = 2
    # Previous run_agent_curriculum would have set step_attempts for order 2 to 1 via set_current_step.
    # Manually setting for this isolated re-evaluation:
    cm.agent_progress[test_agent_id]["step_attempts"][2] = cm.agent_progress[test_agent_id]["step_attempts"].get(2,0) +1 # Simulate another attempt

    current_step_for_agent = cm.get_current_step_object(test_agent_id)
    if current_step_for_agent:
        mock_avt.set_metric(test_agent_id, "task_success", 0) # Still failing
        # The get_step_attempts in ADM will use the value from cm.agent_progress
        decision = adm.evaluate_adaptation_rules(test_agent_id, current_step_for_agent, cm)
        print(f"Decision for '{current_step_for_agent.name}' on attempt {cm.get_step_attempts(test_agent_id, current_step_for_agent.order)}: {decision}")

        # Simulate one more failure to trigger branch
        cm.agent_progress[test_agent_id]["step_attempts"][2] +=1
        decision = adm.evaluate_adaptation_rules(test_agent_id, current_step_for_agent, cm)
        print(f"Decision for '{current_step_for_agent.name}' on attempt {cm.get_step_attempts(test_agent_id, current_step_for_agent.order)}: {decision}")


    import os
    if os.path.exists(dummy_filepath):
        os.remove(dummy_filepath)

```
