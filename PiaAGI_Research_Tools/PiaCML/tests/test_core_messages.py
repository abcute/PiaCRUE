import unittest
import uuid
import datetime
from dataclasses import is_dataclass, fields

# Adjust path for consistent imports
# This assumes tests are in PiaAGI_Research_Tools/PiaCML/tests/
# and modules are in PiaAGI_Research_Tools/PiaCML/
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    from PiaAGI_Research_Tools.PiaCML.core_messages import (
        MemoryItem,
        GenericMessage,
        PerceptDataPayload,
        GoalUpdatePayload,
        LTMQueryResultPayload,
        LTMQueryPayload,      # Added
        ActionCommandPayload  # Added
    )
except ModuleNotFoundError as e:
    print(f"Import error in test_core_messages.py: {e}")
    print(f"Current sys.path: {sys.path}")
    # As a fallback, try importing directly if the path adjustment didn't catch it
    # (e.g., if CWD is already PiaAGI_Research_Tools/PiaCML)
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from core_messages import (
        MemoryItem,
        GenericMessage,
        PerceptDataPayload,
        GoalUpdatePayload,
        LTMQueryResultPayload,
        LTMQueryPayload,      # Added
        ActionCommandPayload  # Added
    )


class TestCoreMessages(unittest.TestCase):

    def test_memory_item_creation(self):
        """Test MemoryItem creation with default and provided values."""
        # Test with default values
        item_default = MemoryItem(content="Default content")
        self.assertTrue(is_dataclass(item_default))
        self.assertIsInstance(item_default.item_id, str)
        self.assertIsNotNone(uuid.UUID(item_default.item_id)) # Check if valid UUID
        self.assertEqual(item_default.content, "Default content")
        self.assertEqual(item_default.metadata, {})
        self.assertIsInstance(item_default.timestamp, datetime.datetime)
        self.assertEqual(item_default.timestamp.tzinfo, datetime.timezone.utc)

        # Test with provided values
        custom_id = str(uuid.uuid4())
        custom_ts = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
        custom_meta = {"source": "test_case"}
        item_provided = MemoryItem(
            item_id=custom_id,
            content=[1, 2, 3],
            metadata=custom_meta,
            timestamp=custom_ts
        )
        self.assertEqual(item_provided.item_id, custom_id)
        self.assertEqual(item_provided.content, [1, 2, 3])
        self.assertEqual(item_provided.metadata, custom_meta)
        self.assertEqual(item_provided.timestamp, custom_ts)

    def test_generic_message_creation(self):
        """Test GenericMessage creation."""
        payload_content = {"data": "simple_payload"}
        msg = GenericMessage(
            source_module_id="TestModuleSource",
            message_type="TEST_MESSAGE",
            payload=payload_content
        )
        self.assertTrue(is_dataclass(msg))
        self.assertIsInstance(msg.message_id, str)
        self.assertIsNotNone(uuid.UUID(msg.message_id))
        self.assertEqual(msg.source_module_id, "TestModuleSource")
        self.assertEqual(msg.message_type, "TEST_MESSAGE")
        self.assertEqual(msg.payload, payload_content)
        self.assertIsInstance(msg.timestamp, datetime.datetime)
        self.assertEqual(msg.timestamp.tzinfo, datetime.timezone.utc)
        self.assertIsNone(msg.target_module_id) # Default
        self.assertEqual(msg.metadata, {}) # Default

        msg_targeted = GenericMessage(
            source_module_id="AnotherModule",
            message_type="TARGETED_INFO",
            payload="info string",
            target_module_id="SpecificReceiver",
            metadata={"priority": 1}
        )
        self.assertEqual(msg_targeted.target_module_id, "SpecificReceiver")
        self.assertEqual(msg_targeted.metadata, {"priority": 1})


    def test_percept_data_payload_creation(self):
        """Test PerceptDataPayload creation."""
        source_ts = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=5)
        pdp = PerceptDataPayload(
            modality="audio",
            content={"features": [0.1, 0.2, 0.3]},
            source_timestamp=source_ts,
            metadata={"device": "mic_array_01"}
        )
        self.assertTrue(is_dataclass(pdp))
        self.assertIsInstance(pdp.percept_id, str)
        self.assertEqual(pdp.modality, "audio")
        self.assertEqual(pdp.content, {"features": [0.1, 0.2, 0.3]})
        self.assertEqual(pdp.source_timestamp, source_ts)
        self.assertIsInstance(pdp.processing_timestamp, datetime.datetime)
        self.assertTrue(pdp.processing_timestamp > pdp.source_timestamp)
        self.assertEqual(pdp.metadata, {"device": "mic_array_01"})

    def test_goal_update_payload_creation(self):
        """Test GoalUpdatePayload creation with required and optional fields."""
        deadline_ts = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
        gup = GoalUpdatePayload(
            goal_id="goal_learn_python",
            goal_description="Learn Python programming language for AGI development.",
            priority=0.85,
            status="ACTIVE",
            originator="SelfModel_DevelopmentPlan",
            criteria_for_completion="Complete 3 online courses and build 2 projects.",
            associated_rewards_penalties={"reward_on_completion": 10.0},
            deadline=deadline_ts,
            parent_goal_id="goal_become_agi_expert"
        )
        self.assertTrue(is_dataclass(gup))
        self.assertEqual(gup.goal_id, "goal_learn_python")
        self.assertEqual(gup.priority, 0.85)
        self.assertEqual(gup.status, "ACTIVE")
        self.assertEqual(gup.originator, "SelfModel_DevelopmentPlan")
        self.assertEqual(gup.criteria_for_completion, "Complete 3 online courses and build 2 projects.")
        self.assertEqual(gup.associated_rewards_penalties, {"reward_on_completion": 10.0})
        self.assertEqual(gup.deadline, deadline_ts)
        self.assertEqual(gup.parent_goal_id, "goal_become_agi_expert")

        # Test with only required fields
        gup_minimal = GoalUpdatePayload(
            goal_id="goal_simple",
            goal_description="A simple task.",
            priority=0.5,
            status="PENDING",
            originator="UserRequest"
        )
        self.assertEqual(gup_minimal.goal_id, "goal_simple")
        self.assertIsNone(gup_minimal.criteria_for_completion)
        self.assertIsNone(gup_minimal.parent_goal_id)


    def test_ltm_query_result_payload_creation(self):
        """Test LTMQueryResultPayload creation."""
        item1 = MemoryItem(content="First LTM result")
        item2 = MemoryItem(content="Second LTM result", metadata={"relevance": 0.9})

        ltm_res = LTMQueryResultPayload(
            query_id="ltm_query_789",
            results=[item1, item2],
            success_status=True,
            metadata={"retrieval_time_ms": 55}
        )
        self.assertTrue(is_dataclass(ltm_res))
        self.assertEqual(ltm_res.query_id, "ltm_query_789")
        self.assertEqual(len(ltm_res.results), 2)
        self.assertIsInstance(ltm_res.results[0], MemoryItem)
        self.assertEqual(ltm_res.results[1].metadata["relevance"], 0.9)
        self.assertTrue(ltm_res.success_status)
        self.assertIsNone(ltm_res.error_message) # Default
        self.assertEqual(ltm_res.metadata, {"retrieval_time_ms": 55})

        ltm_res_fail = LTMQueryResultPayload(
            query_id="ltm_query_error",
            results=[],
            success_status=False,
            error_message="Database connection timed out."
        )
        self.assertFalse(ltm_res_fail.success_status)
        self.assertEqual(ltm_res_fail.error_message, "Database connection timed out.")
        self.assertEqual(len(ltm_res_fail.results), 0)

    def test_ltm_query_payload_creation(self):
        """Test LTMQueryPayload creation."""
        # Test with required fields
        query1 = LTMQueryPayload(
            requester_module_id="TestMod1",
            query_type="semantic_node_retrieval",
            query_content="node_id_test"
        )
        self.assertTrue(is_dataclass(query1))
        self.assertIsInstance(query1.query_id, str) # Default factory
        self.assertIsNotNone(uuid.UUID(query1.query_id))
        self.assertEqual(query1.requester_module_id, "TestMod1")
        self.assertEqual(query1.query_type, "semantic_node_retrieval")
        self.assertEqual(query1.query_content, "node_id_test")
        self.assertIsNone(query1.target_memory_type) # Default
        self.assertEqual(query1.parameters, {}) # Default factory

        # Test with all fields
        custom_query_id = str(uuid.uuid4())
        params = {"max_results": 10, "min_confidence": 0.7}
        query2 = LTMQueryPayload(
            query_id=custom_query_id,
            requester_module_id="TestMod2",
            query_type="episodic_keyword_search",
            query_content=["keyword1", "keyword2"],
            target_memory_type="episodic",
            parameters=params
        )
        self.assertEqual(query2.query_id, custom_query_id)
        self.assertEqual(query2.target_memory_type, "episodic")
        self.assertEqual(query2.parameters, params)

    def test_action_command_payload_creation(self):
        """Test ActionCommandPayload creation."""
        # Test with required fields
        cmd1_params = {"target_location": "kitchen"}
        cmd1 = ActionCommandPayload(
            action_type="NAVIGATE",
            parameters=cmd1_params
        )
        self.assertTrue(is_dataclass(cmd1))
        self.assertIsInstance(cmd1.command_id, str) # Default factory
        self.assertIsNotNone(uuid.UUID(cmd1.command_id))
        self.assertEqual(cmd1.action_type, "NAVIGATE")
        self.assertEqual(cmd1.parameters, cmd1_params)
        self.assertEqual(cmd1.priority, 0.5) # Default
        self.assertIsNone(cmd1.target_object_or_agent) # Default
        self.assertIsNone(cmd1.expected_outcome_summary) # Default

        # Test with all fields
        custom_cmd_id = str(uuid.uuid4())
        cmd2_params = {"tool_name": "calculator", "input_values": [5, 7]}
        cmd2 = ActionCommandPayload(
            command_id=custom_cmd_id,
            action_type="TOOL_USE",
            parameters=cmd2_params,
            priority=0.9,
            target_object_or_agent="ToolManager",
            expected_outcome_summary="Result of 5+7"
        )
        self.assertEqual(cmd2.command_id, custom_cmd_id)
        self.assertEqual(cmd2.priority, 0.9)
        self.assertEqual(cmd2.target_object_or_agent, "ToolManager")
        self.assertEqual(cmd2.expected_outcome_summary, "Result of 5+7")


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
