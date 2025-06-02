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

    def test_direct_attention_with_filter_management(self):
        """Test adding and clearing filters via direct_attention context."""
        # Add a filter
        filter_to_add = {'type': 'salience_gt', 'key': 'salience', 'threshold': 0.7}
        self.attention.direct_attention("FocusWithFilter", 0.9, context={'add_filter': filter_to_add})
        state = self.attention.get_attentional_state()
        self.assertIn(filter_to_add, state['active_filters'])
        self.assertEqual(len(state['active_filters']), 1)

        # Add another filter
        filter_to_add_2 = {'type': 'value_equals', 'key': 'status', 'value': 'critical'}
        self.attention.direct_attention("FocusWithFilter2", 0.95, context={'add_filter': filter_to_add_2})
        state = self.attention.get_attentional_state()
        self.assertIn(filter_to_add, state['active_filters'])
        self.assertIn(filter_to_add_2, state['active_filters'])
        self.assertEqual(len(state['active_filters']), 2)

        # Clear filters
        self.attention.direct_attention("FocusClearFilter", 0.9, context={'clear_filters': True})
        state = self.attention.get_attentional_state()
        self.assertEqual(state['active_filters'], [])

    def test_filter_information_with_value_equals_filter(self):
        """Test filtering with a 'value_equals' active filter."""
        filter_def = {'type': 'value_equals', 'key': 'status', 'value': 'active'}
        # Clear any existing filters and set focus to None to ensure only active_filter applies
        self.attention.direct_attention(None, 0.0, context={'add_filter': filter_def, 'clear_filters': True})

        stream = [
            {'id': 'item1', 'status': 'active', 'content': 'content1'},
            {'id': 'item2', 'status': 'inactive', 'content': 'content2'},
            {'id': 'item3', 'status': 'active', 'content': 'content3'},
        ]

        filtered_items = self.attention.filter_information(stream)
        self.assertEqual(len(filtered_items), 2)
        self.assertTrue(all(item['status'] == 'active' for item in filtered_items))
        self.assertListEqual([item['id'] for item in filtered_items], ['item1', 'item3'])

    def test_filter_information_with_value_gt_filter(self):
        """Test filtering with a 'value_gt' active filter."""
        filter_def = {'type': 'value_gt', 'key': 'score', 'threshold': 0.5}
        self.attention.direct_attention(None, 0.0, context={'add_filter': filter_def, 'clear_filters': True})

        stream = [
            {'id': 'item1', 'score': 0.6, 'content': 'A'},
            {'id': 'item2', 'score': 0.4, 'content': 'B'},
            {'id': 'item3', 'score': 0.7, 'content': 'C'},
            {'id': 'item4', 'score': 0.5, 'content': 'D'}, # Should not pass (not strictly greater)
        ]
        filtered_items = self.attention.filter_information(stream)
        self.assertEqual(len(filtered_items), 2)
        self.assertTrue(all(item['score'] > 0.5 for item in filtered_items))
        self.assertListEqual([item['id'] for item in filtered_items], ['item1', 'item3'])

    def test_filter_information_with_tag_present_filter(self):
        """Test filtering with a 'tag_present' active filter."""
        filter_def = {'type': 'tag_present', 'tag': 'important'}
        self.attention.direct_attention(None, 0.0, context={'add_filter': filter_def, 'clear_filters': True})

        stream = [
            {'id': 'item1', 'tags': ['urgent', 'important'], 'content': 'A'},
            {'id': 'item2', 'tags': ['general'], 'content': 'B'},
            {'id': 'item3', 'tags': ['important'], 'content': 'C'},
            {'id': 'item4', 'content': 'D'}, # No tags
        ]
        filtered_items = self.attention.filter_information(stream)
        self.assertEqual(len(filtered_items), 2)
        self.assertTrue(all('important' in item.get('tags', []) for item in filtered_items))
        self.assertListEqual([item['id'] for item in filtered_items], ['item1', 'item3'])

    def test_filter_information_with_multiple_filters(self):
        """Test filtering with multiple active filters applied."""
        filter1 = {'type': 'value_gt', 'key': 'priority', 'threshold': 3}
        filter2 = {'type': 'tag_present', 'tag': 'projectX'}

        self.attention.direct_attention(None, 0.0, context={'clear_filters': True})
        self.attention.direct_attention(None, 0.0, context={'add_filter': filter1})
        self.attention.direct_attention(None, 0.0, context={'add_filter': filter2})

        stream = [
            {'id': 'item1', 'priority': 5, 'tags': ['projectX', 'alpha']}, # Passes both
            {'id': 'item2', 'priority': 2, 'tags': ['projectX']},          # Fails filter1 (priority)
            {'id': 'item3', 'priority': 6, 'tags': ['projectY']},          # Fails filter2 (tag)
            {'id': 'item4', 'priority': 4, 'tags': ['projectX', 'beta']},  # Passes both
            {'id': 'item5', 'priority': 1, 'tags': ['general']},           # Fails both
        ]

        filtered_items = self.attention.filter_information(stream)
        self.assertEqual(len(filtered_items), 2)
        self.assertListEqual([item['id'] for item in filtered_items], ['item1', 'item4'])
        for item in filtered_items:
            self.assertTrue(item['priority'] > 3)
            self.assertIn('projectX', item['tags'])

    def test_filter_information_with_focus_and_active_filters(self):
        """Test filtering with both a focus and active filters."""
        active_filter = {'type': 'value_equals', 'key': 'status', 'value': 'pending'}
        # Set focus and add filter. Clear any previous filters.
        self.attention.direct_attention("FocusTarget", 0.9, context={'add_filter': active_filter, 'clear_filters': True})

        stream = [
            {'id': 'itemA', 'content': 'Info about FocusTarget', 'status': 'pending', 'tags': ['FocusTarget']}, # Passes focus and filter
            {'id': 'itemB', 'content': 'Info about FocusTarget', 'status': 'done', 'tags': ['FocusTarget']},    # Passes focus, fails filter
            {'id': 'itemC', 'content': 'Other info', 'status': 'pending'},                                     # Fails focus
            {'id': 'itemD', 'content': 'More FocusTarget data', 'status': 'pending', 'tags': ['FocusTarget']},  # Passes focus and filter
            {'id': 'itemE', 'content': 'Irrelevant', 'status': 'active'},                                      # Fails focus
        ]

        filtered_items = self.attention.filter_information(stream) # Uses "FocusTarget" as focus
        self.assertEqual(len(filtered_items), 2)
        self.assertListEqual([item['id'] for item in filtered_items], ['itemA', 'itemD'])
        for item in filtered_items:
            # Check focus condition (tag presence for this test data)
            self.assertIn('FocusTarget', item.get('tags', []))
            # Check active filter condition
            self.assertEqual(item['status'], 'pending')

if __name__ == '__main__':
    unittest.main()
