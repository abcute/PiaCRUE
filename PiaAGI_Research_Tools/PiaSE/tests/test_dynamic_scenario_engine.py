import unittest
import json
import tempfile
import os
from typing import Dict, Any, List, Optional, Union, Tuple # Added Tuple

# Adjust imports based on actual file structure
try:
    from ..core_engine.dynamic_scenario_engine import (
        CurriculumManager, AdaptationDecisionModule, MockPiaAVTInterface,
        DevelopmentalCurriculum, CurriculumStep # Assuming these are importable or placeholders in DSE module
    )
    DSE_IMPORTED_SUCCESSFULLY = True
except ImportError as e:
    print(f"TestDSE: Failed to import DSE components: {e}. Using local placeholders for tests.")
    DSE_IMPORTED_SUCCESSFULLY = False
    # Fallback placeholders if imports fail
    class DevelopmentalCurriculum:
        def __init__(self, name: str, steps: List[Any], description: str = "", target_developmental_stage: str = "", author: str = "", version: str = "", **kwargs):
            self.name = name
            self.description = description
            self.target_developmental_stage = target_developmental_stage
            self.steps = steps # List of CurriculumStep instances
            self.author = author
            self.version = version
            for key, value in kwargs.items(): setattr(self, key, value)

    class CurriculumStep:
        def __init__(self, name: str, order: int, prompt_reference: str,
                     completion_criteria: Optional[List[Dict[str,Any]]] = None,
                     adaptation_rules: Optional[List[Tuple[str, str]]] = None, # List of Tuples for rules
                     environment_config_overrides: Optional[Dict] = None, # Renamed from environment_config for consistency
                     agent_config_overrides: Optional[Dict] = None,
                     max_interactions: int = 1, # Renamed from max_step_interactions
                     **kwargs):
            self.name = name; self.order = order; self.prompt_reference = prompt_reference
            self.completion_criteria = completion_criteria if completion_criteria else []
            self.adaptation_rules = adaptation_rules if adaptation_rules else []
            self.environment_config_overrides = environment_config_overrides if environment_config_overrides else {}
            self.agent_config_overrides = agent_config_overrides if agent_config_overrides else {}
            self.max_interactions = max_interactions
            for key, value in kwargs.items(): setattr(self, key, value)


    class CurriculumManager:
        def __init__(self): self.current_curriculum:Optional[DevelopmentalCurriculum]=None; self.agent_progress:Dict[str, Dict[str,Any]]={}

        def load_curriculum_from_file(self, filepath: str) -> bool:
            try:
                with open(filepath, 'r') as f: data = json.load(f)
                step_data_list = data.get("steps", [])
                parsed_steps = []
                for step_data_item in step_data_list:
                    rules = step_data_item.get("adaptation_rules", [])
                    if rules and isinstance(rules, list) and all(isinstance(r, list) and len(r) == 2 for r in rules):
                         step_data_item["adaptation_rules"] = [tuple(r) for r in rules]
                    elif rules:
                        step_data_item["adaptation_rules"] = []
                    parsed_steps.append(CurriculumStep(**step_data_item))
                self.current_curriculum = DevelopmentalCurriculum(**{k:v for k,v in data.items() if k != "steps"}, steps=parsed_steps)
                if self.current_curriculum.steps: self.current_curriculum.steps.sort(key=lambda s: s.order)
                return True
            except Exception: return False

        def initialize_agent_progress(self, agent_id): self.agent_progress[agent_id] = {"current_step_order": -1, "completed_steps": [], "step_attempts": {}}

        def get_next_step(self, agent_id: str) -> Optional[CurriculumStep]:
            if not self.current_curriculum or not self.current_curriculum.steps or agent_id not in self.agent_progress: return None
            current_order = self.agent_progress[agent_id]["current_step_order"]
            if current_order == -1: return self.current_curriculum.steps[0]
            current_idx = -1
            for idx, step in enumerate(self.current_curriculum.steps):
                if step.order == current_order: current_idx = idx; break
            if current_idx != -1 and current_idx + 1 < len(self.current_curriculum.steps): return self.current_curriculum.steps[current_idx+1]
            return None

        def set_current_step(self, agent_id: str, step_order: int, increment_attempt: bool = True):
            if agent_id not in self.agent_progress: self.initialize_agent_progress(agent_id)
            target_step = self.get_step_by_name_or_order(step_order)
            if target_step:
                self.agent_progress[agent_id]["current_step_order"] = step_order
                self.agent_progress[agent_id].setdefault("step_attempts", {})
                current_attempts = self.agent_progress[agent_id]["step_attempts"].get(step_order, 0)
                if increment_attempt: self.agent_progress[agent_id]["step_attempts"][step_order] = current_attempts + 1
                else: self.agent_progress[agent_id]["step_attempts"].setdefault(step_order, 0) # Ensure it exists
                return target_step
            return None

        def complete_step(self, agent_id, order):
             if agent_id in self.agent_progress and order not in self.agent_progress[agent_id]["completed_steps"]:
                self.agent_progress[agent_id]["completed_steps"].append(order)

        def get_current_step_object(self, agent_id):
            if not self.current_curriculum or agent_id not in self.agent_progress: return None
            order = self.agent_progress[agent_id]["current_step_order"]
            if order == -1: return None
            return self.get_step_by_name_or_order(order)

        def get_step_attempts(self, agent_id, order): return self.agent_progress.get(agent_id, {}).get("step_attempts", {}).get(order, 0)

        def get_step_by_name_or_order(self, identifier: Union[str,int]) -> Optional[CurriculumStep]:
            if not self.current_curriculum: return None
            for step in self.current_curriculum.steps:
                if isinstance(identifier, int) and step.order == identifier: return step
                elif isinstance(identifier, str) and step.name == identifier: return step
            return None

    class MockPiaAVTInterface:
        def __init__(self): self.metrics: Dict[str, Dict[str,Any]] = {}; self.events: List[Any] = []
        def get_performance_metric(self, agent_id, metric_name, context=None): return self.metrics.get(agent_id, {}).get(metric_name)
        def check_event_occurred(self, agent_id, event_sig, time_window=None): return False # Not used in these tests
        def set_metric(self, agent_id, metric, value): self.metrics.setdefault(agent_id, {})[metric] = value

    class AdaptationDecisionModule:
        def __init__(self, avt_interface: MockPiaAVTInterface): self.avt_interface = avt_interface # Corrected avt_if to avt_interface

        def evaluate_step_completion(self, agent_id: str, current_step: CurriculumStep, avt_interface_override: Optional[MockPiaAVTInterface]=None) -> bool: # Added avt_interface_override
            avt_if_to_use = avt_interface_override if avt_interface_override else self.avt_interface
            if not current_step.completion_criteria: return False
            for crit in current_step.completion_criteria:
                val = avt_if_to_use.get_performance_metric(agent_id, crit["metric"])
                if val is None: return False
                expected = crit["value"]
                op = crit["operator"]
                if op == "==" and not (val == expected): return False
                if op == ">=" and not (val >= expected): return False
                # Add other ops if needed for tests
            return True

        def evaluate_adaptation_rules(self, agent_id: str, current_step: CurriculumStep, attempt_count: int, avt_interface_override: Optional[MockPiaAVTInterface]=None) -> str: # Added avt_interface_override
            avt_if_to_use = avt_interface_override if avt_interface_override else self.avt_interface
            if not current_step.adaptation_rules: return "PROCEED"
            for cond_str, action_str in current_step.adaptation_rules:
                parts = cond_str.split()
                if len(parts) == 3:
                    metric, op, expected_str = parts
                    actual_val = attempt_count if metric == "step_attempts" else avt_if_to_use.get_performance_metric(agent_id, metric)
                    if actual_val is None: continue

                    expected_val: Any = expected_str
                    try:
                        if '.' in expected_str: expected_val = float(expected_str)
                        elif expected_str.lower() == 'true': expected_val = True
                        elif expected_str.lower() == 'false': expected_val = False
                        else: expected_val = int(expected_str)
                    except ValueError: pass # Keep as string if not number/bool

                    if op == "==" and actual_val == expected_val: return action_str
                    if op == ">=" and actual_val >= expected_val: return action_str
                    # Add other ops if needed
            return "PROCEED"


class TestCurriculumManager(unittest.TestCase):
    def setUp(self):
        self.manager = CurriculumManager()
        self.agent_id = "test_agent"
        self.curriculum_data = {
            "name": "Test Curriculum", "description": "Desc",
            "target_developmental_stage": "Test Stage", "author": "Test", "version": "1.0",
            "steps": [
                {"order": 1, "name": "Step1", "prompt_reference": "p1.json", "max_interactions":10, "completion_criteria": [{"metric":"goal1", "operator":"==", "value":True}], "adaptation_rules":[]},
                {"order": 2, "name": "Step2", "prompt_reference": "p2.json", "max_interactions":5, "completion_criteria": [], "adaptation_rules":[]},
                {"order": 0, "name": "Step0", "prompt_reference": "p0.json", "max_interactions":5, "completion_criteria": [], "adaptation_rules":[]}
            ]
        }
        self.temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
        json.dump(self.curriculum_data, self.temp_file)
        self.temp_file.close()
        self.temp_filepath = self.temp_file.name

    def tearDown(self):
        os.remove(self.temp_filepath)

    def test_load_curriculum(self):
        loaded = self.manager.load_curriculum_from_file(self.temp_filepath)
        self.assertTrue(loaded)
        self.assertIsNotNone(self.manager.current_curriculum)
        self.assertEqual(self.manager.current_curriculum.name, "Test Curriculum")
        self.assertEqual(len(self.manager.current_curriculum.steps), 3)
        self.assertEqual(self.manager.current_curriculum.steps[0].name, "Step0") # Check sorting
        self.assertEqual(self.manager.current_curriculum.steps[1].name, "Step1")

    def test_agent_progress(self):
        self.manager.load_curriculum_from_file(self.temp_filepath)
        self.manager.initialize_agent_progress(self.agent_id)
        self.assertIn(self.agent_id, self.manager.agent_progress)
        self.assertEqual(self.manager.agent_progress[self.agent_id]["current_step_order"], -1)
        self.assertEqual(self.manager.get_step_attempts(self.agent_id, 0), 0)

    def test_step_progression(self):
        self.manager.load_curriculum_from_file(self.temp_filepath)
        self.manager.initialize_agent_progress(self.agent_id)

        step0 = self.manager.get_next_step(self.agent_id)
        self.assertIsNotNone(step0)
        self.assertEqual(step0.name, "Step0")
        # In the actual engine, set_current_step would be called after getting the next step
        self.manager.set_current_step(self.agent_id, step0.order)
        self.assertEqual(self.manager.get_current_step_object(self.agent_id).name, "Step0")


        step1 = self.manager.get_next_step(self.agent_id)
        self.assertIsNotNone(step1)
        self.assertEqual(step1.name, "Step1")
        self.manager.set_current_step(self.agent_id, step1.order) # 1st attempt at step1
        self.assertEqual(self.manager.get_step_attempts(self.agent_id, step1.order), 1)


        self.manager.complete_step(self.agent_id, step0.order)
        self.assertIn(step0.order, self.manager.agent_progress[self.agent_id]["completed_steps"])

        self.manager.set_current_step(self.agent_id, step1.order, increment_attempt=True) # 2nd attempt at step1
        self.assertEqual(self.manager.get_step_attempts(self.agent_id, step1.order), 2)

    def test_get_step_by_name_or_order(self):
        self.manager.load_curriculum_from_file(self.temp_filepath)
        step_by_order = self.manager.get_step_by_name_or_order(1)
        self.assertIsNotNone(step_by_order)
        self.assertEqual(step_by_order.name, "Step1")

        step_by_name = self.manager.get_step_by_name_or_order("Step2")
        self.assertIsNotNone(step_by_name)
        self.assertEqual(step_by_name.order, 2)

        self.assertIsNone(self.manager.get_step_by_name_or_order(99))
        self.assertIsNone(self.manager.get_step_by_name_or_order("NonExistentStep"))


class TestAdaptationDecisionModule(unittest.TestCase):
    def setUp(self):
        self.avt_mock = MockPiaAVTInterface()
        self.adm = AdaptationDecisionModule(self.avt_mock)
        self.agent_id = "test_agent"
         # If using DSE's placeholder for CurriculumStep, it needs all fields in constructor
        self.default_step_params = {"prompt_reference": "", "max_interactions":1} if not DSE_IMPORTED_SUCCESSFULLY else {}


    def test_evaluate_step_completion_success(self):
        step = CurriculumStep(name="TestComplete", order=1, completion_criteria=[{"metric": "task_done", "operator": "==", "value": True}], **self.default_step_params)
        self.avt_mock.set_metric(self.agent_id, "task_done", True)
        self.assertTrue(self.adm.evaluate_step_completion(self.agent_id, step, self.avt_mock))

    def test_evaluate_step_completion_failure(self):
        step = CurriculumStep(name="TestCompleteFail", order=1, completion_criteria=[{"metric": "score", "operator": ">=", "value": 100}], **self.default_step_params)
        self.avt_mock.set_metric(self.agent_id, "score", 90)
        self.assertFalse(self.adm.evaluate_step_completion(self.agent_id, step, self.avt_mock))

    def test_evaluate_step_completion_no_criteria(self):
        step = CurriculumStep(name="TestNoCriteria", order=1, completion_criteria=[], **self.default_step_params)
        self.assertFalse(self.adm.evaluate_step_completion(self.agent_id, step, self.avt_mock))

    def test_evaluate_adaptation_rules_proceed(self):
        step = CurriculumStep(name="TestAdaptProceed", order=1, adaptation_rules=[("some_metric > 10", "DO_X")], **self.default_step_params)
        self.avt_mock.set_metric(self.agent_id, "some_metric", 5)
        decision = self.adm.evaluate_adaptation_rules(self.agent_id, step, 1, self.avt_mock)
        self.assertEqual(decision, "PROCEED")

    def test_evaluate_adaptation_rules_trigger_step_attempts(self):
        # The DSE module's ADM uses 'step_attempts' as metric name for attempt count
        # The test placeholder ADM uses 'attempts_at_step' as metric name
        # For this test, we use "step_attempts" to match the actual DSE implementation.
        step = CurriculumStep(name="TestAdaptTriggerAttempts", order=1, adaptation_rules=[("step_attempts >= 2", "REPEAT_WITH_HINT")], **self.default_step_params)
        # No need to set "step_attempts" in avt_mock, it's passed directly as attempt_count
        decision = self.adm.evaluate_adaptation_rules(self.agent_id, step, 2, self.avt_mock)
        self.assertEqual(decision, "REPEAT_WITH_HINT")

    def test_evaluate_adaptation_rules_order_priority(self):
        step = CurriculumStep(name="TestAdaptOrder", order=1,
                              adaptation_rules=[
                                  ("score < 50", "FAIL_EARLY"),
                                  ("score < 80", "NEEDS_WORK")
                              ], **self.default_step_params)
        self.avt_mock.set_metric(self.agent_id, "score", 40)
        decision = self.adm.evaluate_adaptation_rules(self.agent_id, step, 1, self.avt_mock)
        self.assertEqual(decision, "FAIL_EARLY")


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

```
