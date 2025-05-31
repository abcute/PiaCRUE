import unittest
import os
import sys

# Adjust path to import from the parent directory (PiaCML)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from concrete_attention_module import ConcreteAttentionModule
except ImportError:
    # Fallback for different execution contexts
    if 'ConcreteAttentionModule' not in globals():
        from PiaAGI_Hub.PiaCML.concrete_attention_module import ConcreteAttentionModule

class TestConcreteAttentionModule(unittest.TestCase):

    def setUp(self):
        self.attention = ConcreteAttentionModule()
        # Suppress print statements from the module during tests
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_initial_state(self):
        state = self.attention.get_attentional_state()
        self.assertIsNone(state['current_focus'])
        self.assertEqual(state['current_priority'], 0.0)
        self.assertEqual(state['active_filters'], [])
        self.assertEqual(state['cognitive_load_level'], 0.0)
        self.assertEqual(state['module_type'], 'ConcreteAttentionModule')

    def test_direct_attention_initial(self):
        success = self.attention.direct_attention("TaskA", 0.8)
        self.assertTrue(success)
        state = self.attention.get_attentional_state()
        self.assertEqual(state['current_focus'], "TaskA")
        self.assertEqual(state['current_priority'], 0.8)

    def test_direct_attention_higher_priority(self):
        self.attention.direct_attention("TaskA", 0.5)
        success = self.attention.direct_attention("TaskB", 0.8)
        self.assertTrue(success)
        state = self.attention.get_attentional_state()
        self.assertEqual(state['current_focus'], "TaskB")
        self.assertEqual(state['current_priority'], 0.8)

    def test_direct_attention_lower_priority(self):
        self.attention.direct_attention("TaskA", 0.8)
        success = self.attention.direct_attention("TaskB", 0.5)
        self.assertFalse(success) # Should not switch
        state = self.attention.get_attentional_state()
        self.assertEqual(state['current_focus'], "TaskA") # Remains TaskA
        self.assertEqual(state['current_priority'], 0.8)

    def test_direct_attention_same_priority(self):
        self.attention.direct_attention("TaskA", 0.8)
        success = self.attention.direct_attention("TaskB", 0.8) # Same priority, should switch
        self.assertTrue(success)
        state = self.attention.get_attentional_state()
        self.assertEqual(state['current_focus'], "TaskB")
        self.assertEqual(state['current_priority'], 0.8)

    def test_filter_information_no_focus(self):
        stream = [{'id': '1', 'content': 'info1'}]
        filtered = self.attention.filter_information(stream)
        self.assertEqual(len(filtered), 1) # No focus, should return all

    def test_filter_information_with_focus_content(self):
        self.attention.direct_attention("apple", 0.8)
        stream = [
            {'id': '1', 'content': 'An apple a day.'},
            {'id': '2', 'content': 'A banana for lunch.'},
            {'id': '3', 'content': 'More apple facts.'}
        ]
        filtered = self.attention.filter_information(stream)
        self.assertEqual(len(filtered), 2)
        self.assertIn('1', [item['id'] for item in filtered])
        self.assertIn('3', [item['id'] for item in filtered])

    def test_filter_information_with_focus_tags(self):
        self.attention.direct_attention("urgent", 0.9)
        stream = [
            {'id': 'a', 'tags': ['urgent', 'work']},
            {'id': 'b', 'tags': ['home']},
            {'id': 'c', 'tags': ['urgent', 'personal']}
        ]
        filtered = self.attention.filter_information(stream)
        self.assertEqual(len(filtered), 2)
        self.assertIn('a', [item['id'] for item in filtered])
        self.assertIn('c', [item['id'] for item in filtered])

    def test_filter_information_with_focus_id(self):
        self.attention.direct_attention("id_xyz", 0.9)
        stream = [
            {'id': 'id_abc', 'content': 'some data'},
            {'id': 'id_xyz', 'content': 'target data'},
            {'id': 'id_123', 'content': 'other data'}
        ]
        filtered = self.attention.filter_information(stream)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['id'], 'id_xyz')

    def test_filter_information_with_override_focus(self):
        self.attention.direct_attention("apple", 0.8) # Initial focus
        stream = [
            {'id': '1', 'content': 'An apple a day.'},
            {'id': '2', 'content': 'A banana for lunch.'},
        ]
        filtered = self.attention.filter_information(stream, current_focus="banana")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['id'], '2')
        # Check that internal focus hasn't changed
        state = self.attention.get_attentional_state()
        self.assertEqual(state['current_focus'], "apple")


    def test_manage_cognitive_load_normal(self):
        thresholds = {'optimal': 0.7, 'overload': 0.9}
        result = self.attention.manage_cognitive_load(0.5, thresholds)
        self.assertEqual(result['action'], 'none')
        state = self.attention.get_attentional_state()
        self.assertEqual(state['cognitive_load_level'], 0.5)

    def test_manage_cognitive_load_optimal(self):
        thresholds = {'optimal': 0.7, 'overload': 0.9}
        result = self.attention.manage_cognitive_load(0.8, thresholds) # Above optimal, below overload
        self.assertEqual(result['action'], 'maintain_focus')
        state = self.attention.get_attentional_state()
        self.assertEqual(state['cognitive_load_level'], 0.8)

    def test_manage_cognitive_load_overload(self):
        thresholds = {'optimal': 0.7, 'overload': 0.9}
        result = self.attention.manage_cognitive_load(0.95, thresholds)
        self.assertEqual(result['action'], 'reduce_focus_strictness')
        state = self.attention.get_attentional_state()
        self.assertEqual(state['cognitive_load_level'], 0.95)

if __name__ == '__main__':
    unittest.main()
