import unittest
import os
import sys

# Adjust path to import from the parent directory (PiaCML)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from concrete_behavior_generation_module import ConcreteBehaviorGenerationModule
except ImportError:
    # Fallback for different execution contexts
    if 'ConcreteBehaviorGenerationModule' not in globals():
        from PiaAGI_Hub.PiaCML.concrete_behavior_generation_module import ConcreteBehaviorGenerationModule

class TestConcreteBehaviorGenerationModule(unittest.TestCase):

    def setUp(self):
        self.behavior_gen = ConcreteBehaviorGenerationModule()
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_initial_status(self):
        status = self.behavior_gen.get_status()
        self.assertEqual(status['active_generation_tasks'], 0)
        self.assertIn("linguistic_output", status['supported_behavior_types'])
        self.assertIn("api_call", status['supported_behavior_types'])
        self.assertIn("log_message", status['supported_behavior_types'])
        self.assertEqual(status['module_type'], 'ConcreteBehaviorGenerationModule')

    def test_generate_linguistic_behavior(self):
        action_plan = {
            "action_type": "communicate",
            "target_agent": "user_007",
            "final_message_content": "Test message",
            "target_interface": "chat_v2"
        }
        context = {"session_id": "sess_abc"}
        behavior_spec = self.behavior_gen.generate_behavior(action_plan, context)

        self.assertEqual(behavior_spec['behavior_type'], "linguistic_output")
        self.assertEqual(behavior_spec['original_plan'], action_plan)
        self.assertEqual(behavior_spec['details']['content'], "Test message")
        self.assertEqual(behavior_spec['details']['target_interface'], "chat_v2")
        self.assertEqual(behavior_spec['details']['recipient'], "user_007")
        self.assertEqual(behavior_spec['details']['generation_context'], context)

    def test_generate_linguistic_behavior_minimal_plan(self):
        action_plan = {"action_type": "communicate"}
        behavior_spec = self.behavior_gen.generate_behavior(action_plan)
        self.assertEqual(behavior_spec['behavior_type'], "linguistic_output")
        self.assertEqual(behavior_spec['details']['content'], "Error: No message content specified in plan.")
        self.assertEqual(behavior_spec['details']['target_interface'], "default_chat_interface")
        self.assertEqual(behavior_spec['details']['recipient'], "unknown_recipient")


    def test_generate_tool_use_behavior(self):
        action_plan = {
            "action_type": "use_tool",
            "tool_id": "calculator",
            "parameters": {"expr": "3*5"},
            "expected_result_type": "number"
        }
        behavior_spec = self.behavior_gen.generate_behavior(action_plan)

        self.assertEqual(behavior_spec['behavior_type'], "api_call")
        self.assertEqual(behavior_spec['original_plan'], action_plan)
        self.assertEqual(behavior_spec['details']['tool_id'], "calculator")
        self.assertEqual(behavior_spec['details']['parameters'], {"expr": "3*5"})
        self.assertEqual(behavior_spec['details']['expected_result_type'], "number")

    def test_generate_log_behavior(self):
        action_plan = {
            "action_type": "log_internal_state",
            "log_content": "System check complete.",
            "log_level": "INFO"
        }
        behavior_spec = self.behavior_gen.generate_behavior(action_plan)
        self.assertEqual(behavior_spec['behavior_type'], "log_message")
        self.assertEqual(behavior_spec['details']['message'], "System check complete.")
        self.assertEqual(behavior_spec['details']['level'], "INFO")


    def test_generate_unknown_action_type(self):
        action_plan = {"action_type": "perform_magic_trick"}
        behavior_spec = self.behavior_gen.generate_behavior(action_plan)
        self.assertEqual(behavior_spec['behavior_type'], "unknown")
        self.assertIn("error", behavior_spec['details'])
        self.assertTrue("Unsupported action_type: perform_magic_trick" in behavior_spec['details']['error'])

if __name__ == '__main__':
    unittest.main()
