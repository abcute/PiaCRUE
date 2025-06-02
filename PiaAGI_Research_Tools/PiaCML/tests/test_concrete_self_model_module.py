import unittest
import os
import sys

# Adjust path to import from the parent directory (PiaCML)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PiaAGI_Research_Tools.PiaCML.concrete_self_model_module import ConcreteSelfModelModule

class TestConcreteSelfModelModule(unittest.TestCase):

    def setUp(self):
        self.self_model = ConcreteSelfModelModule()
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w') # Suppress prints

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_initial_status_and_representation(self):
        status = self.self_model.get_status() # Renamed from get_module_status
        self.assertEqual(status['module_type'], 'ConcreteSelfModelModule')
        self.assertEqual(status['current_operational_state'], 'idle')
        self.assertEqual(status['confidence_in_capabilities'], 0.6)
        self.assertEqual(status['ethical_rules_count'], 3)
        self.assertEqual(status['performance_log_count'], 0)

        rep_all = self.self_model.get_self_representation() # No args
        self.assertEqual(rep_all['agent_id'], "PiaAGI_ConcreteSelf_v0.2") # Version might change based on concrete impl.
        self.assertIn("basic_text_processing", rep_all['capabilities'])

        caps = self.self_model.get_self_representation("capabilities")
        self.assertIn("simple_planning", caps)

    def test_update_self_representation_simple_values(self):
        # Test updating existing simple value
        update_success1 = self.self_model.update_self_representation(
            aspect="current_operational_state",
            update_data={"value": "testing_mode"},
            source_of_update="test_case"
        )
        self.assertTrue(update_success1)
        self.assertEqual(self.self_model.get_self_representation("current_operational_state"), "testing_mode")

        # Test adding a new simple value attribute
        update_success2 = self.self_model.update_self_representation(
            aspect="new_simple_attr",
            update_data={"value": "custom_value"},
            source_of_update="test_case"
        )
        self.assertTrue(update_success2)
        self.assertEqual(self.self_model.get_self_representation("new_simple_attr"), "custom_value")

    def test_update_self_representation_list_append(self):
        initial_caps = self.self_model.get_self_representation("capabilities")

        # Test appending a new capability (single item in 'value')
        update_success1 = self.self_model.update_self_representation(
            aspect="capabilities",
            update_data={"value": "advanced_math"},
            source_of_update="test_case"
        )
        self.assertTrue(update_success1)
        caps_after_add1 = self.self_model.get_self_representation("capabilities")
        self.assertIn("advanced_math", caps_after_add1)
        self.assertEqual(len(caps_after_add1), len(initial_caps) + 1)

        # Test appending a list of new capabilities
        update_success2 = self.self_model.update_self_representation(
            aspect="capabilities",
            update_data={"value": ["skill_x", "skill_y"]},
            source_of_update="test_case"
        )
        self.assertTrue(update_success2)
        caps_after_add2 = self.self_model.get_self_representation("capabilities")
        self.assertIn("skill_x", caps_after_add2)
        self.assertIn("skill_y", caps_after_add2)
        self.assertEqual(len(caps_after_add2), len(initial_caps) + 3) # +1 from advanced_math, +2 from skill_x, skill_y

        # Test appending an existing capability (should not duplicate)
        len_before_dup_add = len(caps_after_add2)
        update_success3 = self.self_model.update_self_representation(
            aspect="capabilities",
            update_data={"value": "advanced_math"},
            source_of_update="test_case"
        )
        self.assertTrue(update_success3)
        caps_after_dup_add = self.self_model.get_self_representation("capabilities")
        self.assertEqual(len(caps_after_dup_add), len_before_dup_add)


    def test_update_self_representation_dict_update(self):
        # Initial personality traits
        initial_personality = self.self_model.get_self_representation("personality_traits_active")
        self.assertEqual(initial_personality, {"OCEAN_Openness": 0.7, "OCEAN_Conscientiousness": 0.8})

        # Update existing and add new trait
        update_data = {"OCEAN_Openness": 0.9, "NEW_Trait": 0.5, "OCEAN_Conscientiousness": 0.85} # update_data is the dict of updates
        update_success = self.self_model.update_self_representation(
            aspect="personality_traits_active",
            update_data=update_data,
            source_of_update="test_case"
        )
        self.assertTrue(update_success)

        personality = self.self_model.get_self_representation("personality_traits_active")
        self.assertEqual(personality['OCEAN_Openness'], 0.9)     # Updated
        self.assertEqual(personality['NEW_Trait'], 0.5)         # Added
        self.assertEqual(personality['OCEAN_Conscientiousness'], 0.85) # Updated

    def test_evaluate_self_performance_placeholder(self):
        task_desc = {'task_id': 'task1', 'description': 'test task'}
        result = self.self_model.evaluate_self_performance(task_desc, "success", {"accuracy": 0.99})
        self.assertTrue(result['evaluation_id'].startswith("eval_"))
        self.assertEqual(result['status'], "logged_placeholder_evaluation")

        status = self.self_model.get_status()
        self.assertEqual(status['performance_log_count'], 1)
        self.assertEqual(len(self.self_model._performance_log), 1)
        self.assertEqual(self.self_model._performance_log[0]['task_id'], "task1")

    # New Tests
    def test_get_confidence_level_placeholder(self):
        # Test default confidence
        self.assertEqual(self.self_model.get_confidence_level("unknown_domain"), 0.6) # Default from init if not found

        # Test confidence if capability exists
        self.self_model._self_attributes["capabilities"].append("nlp")
        self.self_model._self_attributes["confidence_in_capabilities"] = 0.7 # Set a base
        self.assertAlmostEqual(self.self_model.get_confidence_level("nlp"), 0.8) # 0.7 + 0.1

        # Test specific confidence if set (though placeholder doesn't use specific_query deeply)
        self.self_model._self_attributes["confidence_in_nlp_translation"] = 0.9
        # The placeholder currently doesn't differentiate specific_query in its return logic
        self.assertAlmostEqual(self.self_model.get_confidence_level("nlp", "translation"), 0.8)


    def test_check_ethical_consistency_placeholder(self):
        benign_action = {"action_type": "summarize", "description": "summarize a public document"}
        consistency_benign = self.self_model.check_ethical_consistency(benign_action)
        self.assertTrue(consistency_benign['is_consistent'])

        harmful_action = {"action_type": "delete_data", "description": "cause harm by deleting user data"}
        consistency_harmful = self.self_model.check_ethical_consistency(harmful_action)
        self.assertFalse(consistency_harmful['is_consistent'])
        self.assertIn("harm", consistency_harmful['reason'].lower())
        self.assertEqual(consistency_harmful['rule_id'], "ETH001") # Based on default rules

    def test_reflect_on_experience_placeholder(self):
        # Test with no failure
        experience1 = [{"task_id": "T001", "outcome_summary": "success - met all targets", "performance_score": 0.95}]
        reflection1 = self.self_model.reflect_on_experience(experience1)
        self.assertEqual(reflection1['insights_gained'], ['Placeholder: No specific insights from this reflection.'])
        self.assertEqual(reflection1['updates_made_count'], 0)

        # Test with a failure
        experience2 = [{"task_id": "T002", "outcome_summary": "failed - accuracy too low", "performance_score": 0.4}]
        reflection2 = self.self_model.reflect_on_experience(experience2)
        self.assertIn("Recent failure detected", reflection2['insights_gained'][0])
        self.assertEqual(reflection2['updates_made_count'], 1)

        # Test with empty log
        reflection3 = self.self_model.reflect_on_experience([])
        self.assertEqual(reflection3['insights_gained'], ['Placeholder: No specific insights from this reflection.'])

    def test_get_cognitive_load_assessment_placeholder(self):
        load_assessment = self.self_model.get_cognitive_load_assessment()
        self.assertEqual(load_assessment, {'working_memory_usage_estimate': 0.5, 'overall_load_perception': 'medium_placeholder'})


if __name__ == '__main__':
    unittest.main()
