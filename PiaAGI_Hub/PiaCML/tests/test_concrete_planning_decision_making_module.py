import unittest
import os
import sys

# Adjust path to import from the parent directory (PiaCML)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import Any, Dict, List, Optional # For MockWorldModel

try:
    from concrete_planning_decision_making_module import ConcretePlanningAndDecisionMakingModule
    from base_world_model import BaseWorldModel # For type hinting and Mock
    # from concrete_world_model import ConcreteWorldModel # Not strictly needed for these tests
except ImportError:
    if 'ConcretePlanningAndDecisionMakingModule' not in globals(): # Fallback
        from PiaAGI_Hub.PiaCML.concrete_planning_decision_making_module import ConcretePlanningAndDecisionMakingModule
    if 'BaseWorldModel' not in globals():
        from PiaAGI_Hub.PiaCML.base_world_model import BaseWorldModel
    # if 'ConcreteWorldModel' not in globals():
    #     from PiaAGI_Hub.PiaCML.concrete_world_model import ConcreteWorldModel

# --- MockWorldModel for testing interaction ---
class MockWorldModel(BaseWorldModel):
    def __init__(self):
        self.properties = {"world_complexity_level": 0.5} # Default complexity
        self.predictions = []
        self.env_property_calls = 0
        self.predict_calls = 0
        self.last_actions_predicted = []

    def update_model_from_perception(self, perception_output: Dict[str, Any]) -> bool: return True
    def get_entity_state(self, entity_id: str, attribute: Optional[str] = None) -> Optional[Any]: return None

    def get_environment_property(self, property_name: str) -> Optional[Any]:
        self.env_property_calls += 1
        return self.properties.get(property_name)

    def predict_action_outcome(self, action: Dict[str, Any], current_world_state_summary: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.predict_calls += 1
        self.last_actions_predicted.append(action)
        # Default good prediction
        prediction = {"success_probability": 0.9, "potential_side_effects": [], "action_simulated": action.get("action_type")}
        # Allow overriding for specific tests
        if hasattr(self, 'override_prediction_logic') and callable(self.override_prediction_logic):
            override = self.override_prediction_logic(action)
            if override:
                prediction.update(override)

        self.predictions.append(prediction)
        return prediction

    def get_uncertainty_level(self, area: Optional[str] = None) -> float: return 0.0
    def get_module_status(self) -> Dict[str, Any]: return {"mock": True, "properties": self.properties, "predict_calls": self.predict_calls}


class TestConcretePlanningAndDecisionMakingModule(unittest.TestCase):

    def setUp(self):
        self.pdm = ConcretePlanningAndDecisionMakingModule()
        self.mock_wm_instance = MockWorldModel() # Instantiate mock world model
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w') # Suppress prints from module

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_initial_status(self):
        status = self.pdm.get_module_status()
        self.assertEqual(status['module_type'], 'ConcretePlanningAndDecisionMakingModule')
        self.assertEqual(status['known_plan_templates_count'], 3) # Based on concrete impl
        self.assertEqual(status['evaluated_plans_count'], 0)
        self.assertIsNone(status['last_selected_plan_id'])

    def test_create_plan_from_template(self):
        goal = {"description": "achieve_goal_A"}
        plans = self.pdm.create_plan(goal, {}, {})
        self.assertEqual(len(plans), 1)
        plan = plans[0]
        self.assertEqual(plan['goal_description'], "achieve_goal_A")
        self.assertEqual(len(plan['steps']), 2) # From template
        self.assertTrue(plan['plan_id'].startswith("plan_achieve_goal_A_"))

    def test_create_plan_default(self):
        goal = {"description": "non_existent_goal"}
        plans = self.pdm.create_plan(goal, {}, {})
        self.assertEqual(len(plans), 1)
        plan = plans[0]
        self.assertEqual(plan['goal_description'], "non_existent_goal")
        self.assertEqual(len(plan['steps']), 1)
        self.assertEqual(plan['steps'][0]['action_type'], "default_action_for_unknown_goal")
        self.assertTrue(plan['plan_id'].startswith("plan_default_"))

    def test_evaluate_plan_basic_score(self):
        plan = {"plan_id": "test_plan1", "steps": [{}, {}, {}]} # 3 steps
        evaluation = self.pdm.evaluate_plan(plan, {}, {}, world_model_instance=None) # Test without WM
        self.assertEqual(evaluation['plan_id'], "test_plan1")
        self.assertAlmostEqual(evaluation['score'], 70.00) # 100 - 3*10
        self.assertEqual(evaluation['risks_considered_from_context'], 0.0)
        self.assertEqual(len(evaluation['ethical_flags_from_context']), 0)
        self.assertIsNone(evaluation['world_complexity_factor_applied']) # No WM
        self.assertIsNone(evaluation['step_predictions_conceptual'])    # No WM

    def test_evaluate_plan_high_risk(self):
        plan = {"plan_id": "test_plan_risky", "steps": [{}]} # 1 step (base score 90)
        world_context = {"perceived_risk_level": 0.8}
        evaluation = self.pdm.evaluate_plan(plan, world_context, {}, world_model_instance=None)
        self.assertAlmostEqual(evaluation['score'], 45.00) # 90 * 0.5

    def test_evaluate_plan_ethical_flags(self):
        plan = {"plan_id": "test_plan_ethical", "steps": [{}]} # 1 step (base score 90)
        self_context = {"ethical_flags_raised": ["concern1"]}
        evaluation = self.pdm.evaluate_plan(plan, {}, self_context, world_model_instance=None)
        self.assertAlmostEqual(evaluation['score'], 9.00) # 90 * 0.1

    def test_evaluate_plan_with_world_model_interaction(self):
        plan = {"plan_id": "test_plan_wm", "steps": [{"action_type": "step1"}, {"action_type": "step2"}]} # 2 steps, base score 80

        # Test with normal complexity (default in mock_wm_instance)
        self.mock_wm_instance.properties["world_complexity_level"] = 0.5
        evaluation = self.pdm.evaluate_plan(plan, {}, {}, world_model_instance=self.mock_wm_instance)

        self.assertEqual(self.mock_wm_instance.env_property_calls, 1)
        self.assertEqual(self.mock_wm_instance.predict_calls, 2) # For 2 steps
        self.assertAlmostEqual(evaluation['score'], 80.00) # Normal complexity factor 1.0, good predictions
        self.assertEqual(evaluation['world_complexity_factor_applied'], 1.0)
        self.assertIsNotNone(evaluation['step_predictions_conceptual'])
        self.assertEqual(len(evaluation['step_predictions_conceptual']), 2)

    def test_evaluate_plan_with_high_complexity_from_wm(self):
        self.mock_wm_instance.properties["world_complexity_level"] = 0.9 # High complexity

        plan = {"plan_id": "test_plan_complex", "steps": [{"action_type": "step_complex"}]} # 1 step, base score 90
        evaluation = self.pdm.evaluate_plan(plan, {}, {}, world_model_instance=self.mock_wm_instance)

        self.assertAlmostEqual(evaluation['score'], 72.00) # 90 * 0.8 (complexity factor)
        self.assertEqual(evaluation['world_complexity_factor_applied'], 0.8)

    def test_evaluate_plan_with_low_success_prediction_from_wm(self):
        # Setup mock to return low success probability for the first step
        def predict_logic_low_success(action):
            if action.get("action_type") == "risky_step":
                return {"success_probability": 0.4} # Low success
            return {"success_probability": 0.9} # Default good for others
        self.mock_wm_instance.override_prediction_logic = predict_logic_low_success
        self.mock_wm_instance.predict_calls = 0 # Reset calls for this specific test

        plan = {"plan_id": "test_plan_low_succ", "steps": [{"action_type": "risky_step"}, {"action_type": "safe_step"}]} # 2 steps, base score 80
        evaluation = self.pdm.evaluate_plan(plan, {}, {}, world_model_instance=self.mock_wm_instance)

        # Expected score: 80 (base) * 1.0 (complexity from mock default) * 0.9 (low success penalty for one step) = 72
        self.assertAlmostEqual(evaluation['score'], 72.00)
        self.assertEqual(self.mock_wm_instance.predict_calls, 2)

    def test_evaluate_plan_with_side_effects_prediction_from_wm(self):
        # Setup mock to return side effects for one step
        def predict_logic_side_effects(action):
            if action.get("action_type") == "side_effect_step":
                return {"potential_side_effects": ["minor_issue"]}
            return {} # Default no side effects, good success
        self.mock_wm_instance.override_prediction_logic = predict_logic_side_effects
        self.mock_wm_instance.predict_calls = 0

        plan = {"plan_id": "test_plan_side_eff", "steps": [{"action_type": "side_effect_step"}, {"action_type": "normal_step"}]} # 2 steps, base 80
        evaluation = self.pdm.evaluate_plan(plan, {}, {}, world_model_instance=self.mock_wm_instance)

        # Expected score: 80 (base) * 1.0 (complexity) * 0.95 (side effect penalty) = 76
        self.assertAlmostEqual(evaluation['score'], 76.00)
        self.assertEqual(self.mock_wm_instance.predict_calls, 2)


    def test_select_action_or_plan_empty_list(self):
        self.assertIsNone(self.pdm.select_action_or_plan([]))

    def test_select_action_or_plan_selects_highest_score(self):
        eval_plan1 = {"plan_id": "p1", "score": 80.0}
        eval_plan2 = {"plan_id": "p2", "score": 95.0}
        eval_plan3 = {"plan_id": "p3", "score": 70.0}

        # Ensure the mock_wm_instance's predict_calls are reset if they were used in setup for these evaluations
        # For this test, we are providing evaluations directly.
        selected_eval = self.pdm.select_action_or_plan([eval_plan1, eval_plan2, eval_plan3])
        self.assertIsNotNone(selected_eval)
        self.assertEqual(selected_eval['plan_id'], "p2") # Highest score

        status = self.pdm.get_module_status()
        self.assertEqual(status['last_selected_plan_id'], "p2")

    def test_full_flow_create_evaluate_select(self):
        goal_b = {"description": "achieve_goal_B"} # Template has 3 steps, score 70
        goal_a = {"description": "achieve_goal_A"} # Template has 2 steps, score 80

        plans_b_list = self.pdm.create_plan(goal_b, {}, {})
        plans_a_list = self.pdm.create_plan(goal_a, {}, {})

        plan_b = plans_b_list[0]
        plan_a = plans_a_list[0]

        # Evaluate with mock world model (default complexity 0.5 -> factor 1.0)
        eval_b = self.pdm.evaluate_plan(plan_b, {}, {}, world_model_instance=self.mock_wm_instance)
        self.mock_wm_instance.env_property_calls = 0; self.mock_wm_instance.predict_calls = 0 # Reset counts for next eval

        eval_a = self.pdm.evaluate_plan(plan_a, {}, {}, world_model_instance=self.mock_wm_instance)

        # Scores with default mock WM (normal complexity, good predictions):
        # Plan B (3 steps): 100 - 30 = 70
        # Plan A (2 steps): 100 - 20 = 80
        self.assertAlmostEqual(eval_b['score'], 70.00)
        self.assertAlmostEqual(eval_a['score'], 80.00)

        selected_eval = self.pdm.select_action_or_plan([eval_b, eval_a])
        self.assertIsNotNone(selected_eval)
        self.assertEqual(selected_eval['plan_id'], plan_a['plan_id']) # Plan A has higher score


if __name__ == '__main__':
    unittest.main()
