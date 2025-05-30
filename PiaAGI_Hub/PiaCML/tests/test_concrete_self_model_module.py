import unittest
import os
import sys

# Adjust path to import from the parent directory (PiaCML)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from concrete_self_model_module import ConcreteSelfModelModule
except ImportError:
    if 'ConcreteSelfModelModule' not in globals(): # Fallback
        from PiaAGI_Hub.PiaCML.concrete_self_model_module import ConcreteSelfModelModule

class TestConcreteSelfModelModule(unittest.TestCase):

    def setUp(self):
        self.self_model = ConcreteSelfModelModule()
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w') # Suppress prints

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_initial_status_and_representation(self):
        status = self.self_model.get_module_status()
        self.assertEqual(status['module_type'], 'ConcreteSelfModelModule')
        self.assertEqual(status['current_operational_state'], 'idle')
        self.assertEqual(status['confidence_in_capabilities'], 0.6)
        self.assertEqual(status['ethical_rules_count'], 3) # Default rules
        self.assertEqual(status['performance_log_count'], 0)

        rep_all = self.self_model.get_self_representation()
        self.assertEqual(rep_all['agent_id'], "PiaAGI_ConcreteSelf_v0.1")
        self.assertIn("basic_text_processing", rep_all['capabilities'])

        caps = self.self_model.get_self_representation("capabilities")
        self.assertIn("simple_planning", caps)

    def test_update_self_representation_simple_values(self):
        update_data = {
            "current_operational_state": "testing_mode",
            "confidence_in_capabilities": 0.75,
            "new_attr": "custom_value"
        }
        self.self_model.update_self_representation(update_data)

        self.assertEqual(self.self_model.get_self_representation("current_operational_state"), "testing_mode")
        self.assertEqual(self.self_model.get_self_representation("confidence_in_capabilities"), 0.75)
        self.assertEqual(self.self_model.get_self_representation("new_attr"), "custom_value")

    def test_update_self_representation_list_append(self):
        # Test appending a new capability
        self.self_model.update_self_representation({"capabilities": ["advanced_math"]})
        caps = self.self_model.get_self_representation("capabilities")
        self.assertIn("basic_text_processing", caps) # Original
        self.assertIn("advanced_math", caps) # New

        # Test appending an existing capability (should not duplicate)
        initial_len = len(caps)
        self.self_model.update_self_representation({"capabilities": ["advanced_math"]})
        caps_after_dup_add = self.self_model.get_self_representation("capabilities")
        self.assertEqual(len(caps_after_dup_add), initial_len)

        # Test extending capabilities with a list
        self.self_model.update_self_representation({"capabilities": ["skill_x", "skill_y"]})
        caps_after_list_add = self.self_model.get_self_representation("capabilities")
        self.assertIn("skill_x", caps_after_list_add)
        self.assertIn("skill_y", caps_after_list_add)


    def test_update_self_representation_dict_update(self):
        update_personality = {"personality_traits_active": {"OCEAN_Openness": 0.9, "NEW_Trait": 0.5}}
        self.self_model.update_self_representation(update_personality)

        personality = self.self_model.get_self_representation("personality_traits_active")
        self.assertEqual(personality['OCEAN_Openness'], 0.9) # Updated
        self.assertEqual(personality['NEW_Trait'], 0.5)     # Added
        self.assertEqual(personality['OCEAN_Conscientiousness'], 0.8) # Original persisted

    def test_evaluate_self_performance_placeholder(self):
        result = self.self_model.evaluate_self_performance("task1", "success", {"accuracy": 0.99})
        self.assertTrue(result['evaluation_id'].startswith("eval_"))
        self.assertEqual(result['status'], "logged")

        status = self.self_model.get_module_status()
        self.assertEqual(status['performance_log_count'], 1)
        self.assertEqual(len(self.self_model._performance_log), 1)
        self.assertEqual(self.self_model._performance_log[0]['task_id'], "task1")

    def test_get_ethical_framework(self):
        framework = self.self_model.get_ethical_framework()
        self.assertEqual(len(framework), 3) # Default rules
        self.assertEqual(framework[0]['rule_id'], "ETH001")
        # Test that it's a copy
        framework.append({"rule_id": "ETH_TEST", "principle": "Test rule", "priority": "low"})
        self.assertEqual(len(self.self_model.get_ethical_framework()), 3)


if __name__ == '__main__':
    unittest.main()
