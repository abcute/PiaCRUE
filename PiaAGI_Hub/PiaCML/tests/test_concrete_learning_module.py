import unittest
import os
import sys

# Adjust path to import from the parent directory (PiaCML)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from concrete_learning_module import ConcreteLearningModule
except ImportError:
    # Fallback for different execution contexts
    if 'ConcreteLearningModule' not in globals():
        from PiaAGI_Hub.PiaCML.concrete_learning_module import ConcreteLearningModule

class TestConcreteLearningModule(unittest.TestCase):

    def setUp(self):
        self.learning = ConcreteLearningModule()
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_initial_status(self):
        status = self.learning.get_learning_status()
        self.assertEqual(status['active_tasks_count'], 0)
        self.assertEqual(status['total_logged_learning_attempts'], 0)
        self.assertEqual(status['total_feedback_logs'], 0)
        self.assertEqual(status['module_type'], 'ConcreteLearningModule')

    def test_learn_direct_store(self):
        data_to_store = "Important fact to remember."
        context = {'task_id': 'store_fact_1'}
        outcome = self.learning.learn(data_to_store, "direct_store", context)

        self.assertEqual(outcome['status'], 'success')
        self.assertIn('conceptual_item_based_on_store_fact_1', outcome['updates_to_ltm'])
        self.assertEqual(outcome['learned_representation'], data_to_store)

        status = self.learning.get_learning_status('store_fact_1')
        self.assertEqual(status['status'], 'processing_direct_store') # Default status after learn call

        full_status = self.learning.get_learning_status()
        self.assertEqual(full_status['total_logged_learning_attempts'], 1)


    def test_learn_supervised_dummy(self):
        data = {'features': [0.1, 0.2], 'label': 'B'}
        context = {'task_id': 'classify_b'}
        outcome = self.learning.learn(data, "supervised_dummy", context)

        self.assertEqual(outcome['status'], 'success')
        self.assertIn('model_update_for_classify_b', outcome['updates_to_ltm'])
        self.assertIn('dummy_model_accuracy_0.75', outcome['updated_self_model_params'])

    def test_learn_other_paradigm_logging(self):
        context = {'task_id': 'other_task'}
        outcome = self.learning.learn("some_data", "unknown_paradigm", context)
        self.assertEqual(outcome['status'], 'logged_not_processed')

        status = self.learning.get_learning_status('other_task')
        self.assertEqual(status['status'], 'logged_not_processed_unknown_paradigm')

        full_status = self.learning.get_learning_status()
        self.assertEqual(full_status['total_logged_learning_attempts'], 1)

    def test_process_feedback(self):
        feedback_data = {'type': 'reward', 'value': 10}
        context_id = 'task_for_feedback'
        self.learning._learning_tasks_status[context_id] = 'processing_rl' # Simulate task exists

        success = self.learning.process_feedback(feedback_data, context_id)
        self.assertTrue(success)

        status = self.learning.get_learning_status(context_id)
        self.assertEqual(status['status'], 'feedback_received')

        full_status = self.learning.get_learning_status()
        self.assertEqual(full_status['total_feedback_logs'], 1)

    def test_consolidate_knowledge_placeholder(self):
        item_ids = ['task_beta', 'task_gamma']
        self.learning._learning_tasks_status['task_beta'] = 'learned'
        self.learning._learning_tasks_status['task_gamma'] = 'learned'

        success = self.learning.consolidate_knowledge(item_ids)
        self.assertTrue(success) # Placeholder returns True

        self.assertEqual(self.learning.get_learning_status('task_beta')['status'], 'consolidation_pending_for_LTM')
        self.assertEqual(self.learning.get_learning_status('task_gamma')['status'], 'consolidation_pending_for_LTM')


    def test_apply_ethical_guardrails_permissible(self):
        outcome_data = {'info': 'This is fine.'}
        context = {}
        is_permissible = self.learning.apply_ethical_guardrails(outcome_data, context)
        self.assertTrue(is_permissible)

    def test_apply_ethical_guardrails_impermissible_by_data(self):
        outcome_data = {'info': 'This is bad.', 'is_disallowed': True}
        context = {}
        is_permissible = self.learning.apply_ethical_guardrails(outcome_data, context)
        self.assertFalse(is_permissible)

    def test_apply_ethical_guardrails_impermissible_by_context(self):
        outcome_data = {'info': 'This is also bad.'}
        context = {'contains_disallowed_content': True}
        is_permissible = self.learning.apply_ethical_guardrails(outcome_data, context)
        self.assertFalse(is_permissible)

    def test_get_learning_status_specific_task_unknown(self):
        status = self.learning.get_learning_status('unknown_task_id')
        self.assertEqual(status['status'], 'unknown_task')

if __name__ == '__main__':
    unittest.main()
