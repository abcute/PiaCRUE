import unittest
from typing import Dict, Any
import sys
import os

# Attempt to import the module from the correct location
try:
    from PiaAGI_Research_Tools.PiaCML.concrete_self_model_module import ConcreteSelfModelModule
except ImportError:
    # Fallback for cases where the test is run from a different CWD or structure
    # Add the parent directory of PiaAGI_Research_Tools to the Python path
    # This assumes the test file is in PiaAGI_Research_Tools/PiaCML/tests/
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pia_cml_dir = os.path.dirname(current_dir)
    research_tools_dir = os.path.dirname(pia_cml_dir)
    # For it to find PiaAGI_Research_Tools.PiaCML
    root_dir_for_import = os.path.dirname(research_tools_dir)
    if root_dir_for_import not in sys.path:
        sys.path.insert(0, root_dir_for_import)
    # Try importing again after path adjustment
    from PiaAGI_Research_Tools.PiaCML.concrete_self_model_module import ConcreteSelfModelModule


class TestConcreteSelfModelModule(unittest.TestCase):

    def setUp(self):
        """Set up a new ConcreteSelfModelModule instance for each test."""
        self.self_model = ConcreteSelfModelModule()
        self._original_stdout = sys.stdout
        # Suppress prints from the module during tests for cleaner output
        sys.stdout = open(os.devnull, 'w')

    def tearDown(self):
        """Restore stdout after each test."""
        sys.stdout.close()
        sys.stdout = self._original_stdout

    def test_initial_confidence_dictionaries_exist(self):
        """Test that confidence dictionaries are initialized."""
        self.assertTrue(hasattr(self.self_model, 'knowledge_confidence'))
        self.assertIsInstance(self.self_model.knowledge_confidence, Dict)
        self.assertTrue(hasattr(self.self_model, 'capability_confidence'))
        self.assertIsInstance(self.self_model.capability_confidence, Dict)

    def test_update_confidence_knowledge(self):
        """Test updating confidence for a knowledge item."""
        item_id = "concept_alpha"
        self.assertTrue(self.self_model.update_confidence(item_id, "knowledge", 0.75, "initial_learning"))
        self.assertEqual(self.self_model.knowledge_confidence.get(item_id), 0.75)

        self.assertTrue(self.self_model.update_confidence(item_id, "knowledge", 0.85, "successful_application"))
        self.assertEqual(self.self_model.knowledge_confidence.get(item_id), 0.85)

    def test_update_confidence_capability(self):
        """Test updating confidence for a capability item."""
        item_id = "skill_beta"
        self.assertTrue(self.self_model.update_confidence(item_id, "capability", 0.60, "training_completion"))
        self.assertEqual(self.self_model.capability_confidence.get(item_id), 0.60)

        self.assertTrue(self.self_model.update_confidence(item_id, "capability", 0.70, "consistent_success"))
        self.assertEqual(self.self_model.capability_confidence.get(item_id), 0.70)

    def test_update_confidence_invalid_type(self):
        """Test updating confidence with an invalid item_type."""
        self.assertFalse(self.self_model.update_confidence("item_gamma", "invalid_type", 0.5))
        self.assertIsNone(self.self_model.knowledge_confidence.get("item_gamma"))
        self.assertIsNone(self.self_model.capability_confidence.get("item_gamma"))

    def test_update_confidence_clamping(self):
        """Test that confidence values are clamped to the [0.0, 1.0] range."""
        # Test clamping for knowledge
        self.self_model.update_confidence("concept_clamp_high", "knowledge", 1.5, "test_high")
        self.assertEqual(self.self_model.knowledge_confidence.get("concept_clamp_high"), 1.0)

        self.self_model.update_confidence("concept_clamp_low", "knowledge", -0.5, "test_low")
        self.assertEqual(self.self_model.knowledge_confidence.get("concept_clamp_low"), 0.0)

        # Test clamping for capability
        self.self_model.update_confidence("skill_clamp_high", "capability", 2.0, "test_high_skill")
        self.assertEqual(self.self_model.capability_confidence.get("skill_clamp_high"), 1.0)

        self.self_model.update_confidence("skill_clamp_low", "capability", -1.0, "test_low_skill")
        self.assertEqual(self.self_model.capability_confidence.get("skill_clamp_low"), 0.0)

        # Test with exact bounds
        self.self_model.update_confidence("concept_exact_high", "knowledge", 1.0, "test_exact_high")
        self.assertEqual(self.self_model.knowledge_confidence.get("concept_exact_high"), 1.0)

        self.self_model.update_confidence("concept_exact_low", "knowledge", 0.0, "test_exact_low")
        self.assertEqual(self.self_model.knowledge_confidence.get("concept_exact_low"), 0.0)


    def test_get_confidence(self):
        """Test retrieving confidence scores."""
        self.self_model.update_confidence("concept_get", "knowledge", 0.88)
        self.assertEqual(self.self_model.get_confidence("concept_get", "knowledge"), 0.88)

        self.self_model.update_confidence("skill_get", "capability", 0.77)
        self.assertEqual(self.self_model.get_confidence("skill_get", "capability"), 0.77)

        # Test getting non-existent items
        self.assertIsNone(self.self_model.get_confidence("non_existent_concept", "knowledge"))
        self.assertIsNone(self.self_model.get_confidence("non_existent_skill", "capability"))

        # Test getting with invalid type
        self.assertIsNone(self.self_model.get_confidence("any_id", "invalid_type"))

    def test_log_self_assessment(self):
        """Test the log_self_assessment method for correct string output."""
        # Existing knowledge item
        self.self_model.update_confidence("concept_log", "knowledge", 0.91, "test_log")
        expected_log_k = "Self-assessment: Confidence in knowledge 'concept_log' is 0.91."
        self.assertEqual(self.self_model.log_self_assessment("concept_log", "knowledge"), expected_log_k)

        # Existing capability item
        self.self_model.update_confidence("skill_log", "capability", 0.67, "test_log")
        expected_log_c = "Self-assessment: Confidence in capability 'skill_log' is 0.67."
        self.assertEqual(self.self_model.log_self_assessment("skill_log", "capability"), expected_log_c)

        # Non-existent knowledge item
        expected_log_k_non = "Self-assessment: Confidence in knowledge 'non_existent_k' is not found."
        self.assertEqual(self.self_model.log_self_assessment("non_existent_k", "knowledge"), expected_log_k_non)

        # Non-existent capability item
        expected_log_c_non = "Self-assessment: Confidence in capability 'non_existent_c' is not found."
        self.assertEqual(self.self_model.log_self_assessment("non_existent_c", "capability"), expected_log_c_non)

        # Invalid item type
        expected_log_invalid_type = "Self-assessment: Cannot assess confidence for invalid item_type 'wrong_type' with ID 'item_x'."
        self.assertEqual(self.self_model.log_self_assessment("item_x", "wrong_type"), expected_log_invalid_type)


if __name__ == '__main__':
    # Note: When running tests via an IDE or test runner, this __main__ block might not be executed.
    # It's primarily for direct script execution.
    # Using unittest.main() with specific arguments can help if tests are discovered/run from here.
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
