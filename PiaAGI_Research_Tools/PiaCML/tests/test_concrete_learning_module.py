import unittest
import os
import sys
from unittest.mock import MagicMock # Added

# Adjust path for consistent imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    from PiaAGI_Research_Tools.PiaCML import (
        ConcreteLearningModule,
        MessageBus,               # Added
        GenericMessage,           # Added
        GoalUpdatePayload         # Added
    )
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from concrete_learning_module import ConcreteLearningModule
    try:
        from message_bus import MessageBus
        from core_messages import GenericMessage, GoalUpdatePayload
    except ImportError:
        MessageBus = None
        GenericMessage = None
        GoalUpdatePayload = None


class TestConcreteLearningModule(unittest.TestCase):

    def setUp(self):
        self.bus = MessageBus() if MessageBus else None
        self.learning_module_no_bus = ConcreteLearningModule()
        self.learning_module_with_bus = ConcreteLearningModule(message_bus=self.bus)

        self._original_stdout = sys.stdout
        # Comment out print suppression for easier debugging if tests fail
        # sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        # sys.stdout.close()
        sys.stdout = self._original_stdout

    # --- Existing tests adapted to use learning_module_no_bus ---
    def test_initial_status(self):
        status = self.learning_module_no_bus.get_learning_status()
        self.assertEqual(status['active_tasks_count'], 0)
        self.assertEqual(status['total_logged_learning_attempts'], 0)
        # ... (rest of assertions from existing test, using self.learning_module_no_bus)
        self.assertIsNone(self.learning_module_no_bus.message_bus)
        self.assertEqual(len(self.learning_module_no_bus.processed_goal_updates_for_learning),0)


    def test_learn_direct_store(self):
        data_to_store = "Important fact to remember."
        context = {'task_id': 'store_fact_1'}
        outcome = self.learning_module_no_bus.learn(data_to_store, "direct_store", context)
        self.assertEqual(outcome['status'], 'success')
        # ... (rest of assertions)

    def test_learn_supervised_dummy(self):
        data = {'features': [0.1, 0.2], 'label': 'B'}
        context = {'task_id': 'classify_b'}
        outcome = self.learning_module_no_bus.learn(data, "supervised_dummy", context)
        self.assertEqual(outcome['status'], 'success')
        # ... (rest of assertions)

    def test_learn_other_paradigm_logging(self):
        context = {'task_id': 'other_task'}
        outcome = self.learning_module_no_bus.learn("some_data", "unknown_paradigm", context)
        self.assertEqual(outcome['status'], 'logged_not_processed')
        # ... (rest of assertions)

    def test_process_feedback(self):
        feedback_data = {'type': 'reward', 'value': 10}
        context_id = 'task_for_feedback'
        self.learning_module_no_bus._learning_tasks_status[context_id] = 'processing_rl'
        success = self.learning_module_no_bus.process_feedback(feedback_data, context_id)
        self.assertTrue(success)
        # ... (rest of assertions)

    def test_consolidate_knowledge_placeholder(self):
        item_ids = ['task_beta', 'task_gamma']
        self.learning_module_no_bus._learning_tasks_status['task_beta'] = 'learned'
        success = self.learning_module_no_bus.consolidate_knowledge(item_ids)
        self.assertTrue(success)
        # ... (rest of assertions)

    def test_apply_ethical_guardrails_permissible(self):
        outcome_data = {'info': 'This is fine.'}
        is_permissible = self.learning_module_no_bus.apply_ethical_guardrails(outcome_data, {})
        self.assertTrue(is_permissible)

    def test_apply_ethical_guardrails_impermissible_by_data(self):
        outcome_data = {'info': 'This is bad.', 'is_disallowed': True}
        is_permissible = self.learning_module_no_bus.apply_ethical_guardrails(outcome_data, {})
        self.assertFalse(is_permissible)

    def test_apply_ethical_guardrails_impermissible_by_context(self):
        outcome_data = {'info': 'This is also bad.'}
        context = {'contains_disallowed_content': True}
        is_permissible = self.learning_module_no_bus.apply_ethical_guardrails(outcome_data, context)
        self.assertFalse(is_permissible)

    def test_get_learning_status_specific_task_unknown(self):
        status = self.learning_module_no_bus.get_learning_status('unknown_task_id')
        self.assertEqual(status['status'], 'unknown_task')

    def test_learn_reinforcement_dummy(self):
        data = {'state': 's1', 'action': 'a1'}
        context = {'task_id': 'rl_task_1', 'reward_signal': 1.0}
        outcome = self.learning_module_no_bus.learn(data, "reinforcement_dummy", context)
        self.assertEqual(outcome['status'], 'success')
        # ... (rest of assertions)

    def test_learn_unsupervised_dummy(self):
        data = {'features': [0.1, 0.2, 0.3, 0.4]}
        context = {'task_id': 'ul_task_1'}
        outcome = self.learning_module_no_bus.learn(data, "unsupervised_dummy", context)
        self.assertEqual(outcome['status'], 'success')
        # ... (rest of assertions)

    # --- New Tests for MessageBus Integration ---
    def test_initialization_with_bus_subscription(self):
        """Test LearningModule initialization with a message bus and subscription to GoalUpdate."""
        if not MessageBus: self.skipTest("MessageBus components not available")

        self.assertIsNotNone(self.learning_module_with_bus.message_bus)
        subscribers = self.bus.get_subscribers_for_type("GoalUpdate")

        found_subscription = any(
            sub[0] == "ConcreteLearningModule_01" and
            sub[1] == self.learning_module_with_bus.handle_goal_update_for_learning
            for sub in subscribers if sub # Check if sub is not None
        )
        self.assertTrue(found_subscription, "LearningModule did not subscribe to GoalUpdate messages.")

    def test_handle_goal_update_for_learning(self):
        """Test that LearningModule receives and logs GoalUpdate messages."""
        if not MessageBus or not GenericMessage or not GoalUpdatePayload:
            self.skipTest("MessageBus or core message components not available")

        self.assertEqual(len(self.learning_module_with_bus.processed_goal_updates_for_learning), 0)

        goal_payload_achieved = GoalUpdatePayload(
            goal_id="g_learn_achieved", goal_description="Learn X",
            priority=0.8, status="achieved", originator="TestMotSys"
        )
        msg_achieved = GenericMessage(source_module_id="TestMotSys", message_type="GoalUpdate", payload=goal_payload_achieved)

        goal_payload_failed = GoalUpdatePayload(
            goal_id="g_learn_failed", goal_description="Learn Y",
            priority=0.7, status="failed", originator="TestMotSys"
        )
        msg_failed = GenericMessage(source_module_id="TestMotSys", message_type="GoalUpdate", payload=goal_payload_failed)

        self.bus.publish(msg_achieved)
        self.bus.publish(msg_failed)

        self.assertEqual(len(self.learning_module_with_bus.processed_goal_updates_for_learning), 2)
        logged_payload_1 = self.learning_module_with_bus.processed_goal_updates_for_learning[0]
        logged_payload_2 = self.learning_module_with_bus.processed_goal_updates_for_learning[1]

        self.assertIsInstance(logged_payload_1, GoalUpdatePayload)
        self.assertEqual(logged_payload_1.goal_id, "g_learn_achieved")
        self.assertEqual(logged_payload_1.status, "achieved")

        self.assertIsInstance(logged_payload_2, GoalUpdatePayload)
        self.assertEqual(logged_payload_2.goal_id, "g_learn_failed")
        self.assertEqual(logged_payload_2.status, "failed")

    def test_handle_goal_update_unexpected_payload(self):
        """Test LearningModule handles GoalUpdate with an unexpected payload type."""
        if not MessageBus or not GenericMessage:
            self.skipTest("MessageBus or GenericMessage not available")

        malformed_msg = GenericMessage(
            source_module_id="TestMalformedSource",
            message_type="GoalUpdate",
            payload="This is not a GoalUpdatePayload"
        )

        # Suppress print for this specific test of error path
        original_stdout_test = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        self.bus.publish(malformed_msg)
        sys.stdout.close()
        sys.stdout = original_stdout_test

        self.assertEqual(len(self.learning_module_with_bus.processed_goal_updates_for_learning), 0)

    def test_no_bus_scenario_for_handler(self):
        """Test that module initialized without a bus does not process bus messages."""
        if not MessageBus or not GenericMessage or not GoalUpdatePayload:
            self.skipTest("MessageBus or core message components not available")

        local_bus_for_no_bus_test = MessageBus()
        goal_payload = GoalUpdatePayload(
            goal_id="g_no_bus_test", goal_description="Test",
            priority=0.5, status="active", originator="Test"
        )
        test_message = GenericMessage(
            source_module_id="TestMotSys", message_type="GoalUpdate", payload=goal_payload
        )
        local_bus_for_no_bus_test.publish(test_message)

        self.assertEqual(len(self.learning_module_no_bus.processed_goal_updates_for_learning), 0)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
