import unittest
import os
import sys

# Adjust path to ensure PiaAGI_Research_Tools is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PiaAGI_Research_Tools.PiaCML.concrete_planning_decision_making_module import ConcretePlanningAndDecisionMakingModule


class TestConcretePlanningAndDecisionMakingModule(unittest.TestCase):

    def setUp(self):
        self.pdm = ConcretePlanningAndDecisionMakingModule()
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

    def test_generate_possible_actions_placeholder(self):
        actions = self.pdm.generate_possible_actions("some_state", [{"goal": "g1"}])
        self.assertEqual(actions, []) # Placeholder returns empty list

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
        evaluation = self.pdm.evaluate_plan(plan, {}, {})
        self.assertEqual(evaluation['plan_id'], "test_plan1")
        self.assertEqual(evaluation['score'], 70) # 100 - 3*10
        self.assertEqual(evaluation['risks_considered'], 0.0)
        self.assertEqual(len(evaluation['ethical_flags']), 0)

    def test_evaluate_plan_high_risk(self):
        plan = {"plan_id": "test_plan_risky", "steps": [{}]} # 1 step (base score 90)
        world_context = {"perceived_risk_level": 0.8}
        evaluation = self.pdm.evaluate_plan(plan, world_context, {})
        self.assertEqual(evaluation['score'], 45) # 90 * 0.5

    def test_evaluate_plan_ethical_flags(self):
        plan = {"plan_id": "test_plan_ethical", "steps": [{}]} # 1 step (base score 90)
        self_context = {"ethical_flags_raised": ["concern1"]}
        evaluation = self.pdm.evaluate_plan(plan, {}, self_context)
        self.assertEqual(evaluation['score'], 9) # 90 * 0.1

    def test_select_plan_empty_list(self): # Renamed
        self.assertIsNone(self.pdm.select_plan([])) # Renamed

    def test_select_plan_selects_highest_score(self): # Renamed
        eval_plan1 = {"plan_id": "p1", "score": 80, "steps_info_for_selection": []}
        eval_plan2 = {"plan_id": "p2", "score": 95, "steps_info_for_selection": []}
        eval_plan3 = {"plan_id": "p3", "score": 70, "steps_info_for_selection": []}

        selected_eval = self.pdm.select_plan([eval_plan1, eval_plan2, eval_plan3]) # Renamed
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

        eval_b = self.pdm.evaluate_plan(plan_b, {}, {})
        eval_a = self.pdm.evaluate_plan(plan_a, {}, {})

        self.assertEqual(eval_b['score'], 70)
        self.assertEqual(eval_a['score'], 80)

        selected_eval = self.pdm.select_plan([eval_b, eval_a]) # Renamed
        self.assertIsNotNone(selected_eval)
        self.assertEqual(selected_eval['plan_id'], plan_a['plan_id'])


if __name__ == '__main__':
    unittest.main()
