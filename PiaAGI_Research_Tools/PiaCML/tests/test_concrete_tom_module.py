import unittest
import asyncio
import uuid
from typing import List, Any, Dict
from datetime import datetime, timezone

# Adjust path for consistent imports
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    from PiaAGI_Research_Tools.PiaCML.message_bus import MessageBus
    from PiaAGI_Research_Tools.PiaCML.core_messages import (
        GenericMessage, PerceptDataPayload, ToMInferenceUpdatePayload, EmotionalStateChangePayload
    )
    from PiaAGI_Research_Tools.PiaCML.concrete_tom_module import ConcreteTheoryOfMindModule
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from message_bus import MessageBus
    from core_messages import (
        GenericMessage, PerceptDataPayload, ToMInferenceUpdatePayload, EmotionalStateChangePayload
    )
    from concrete_tom_module import ConcreteTheoryOfMindModule

class TestConcreteToMModuleIntegration(unittest.TestCase):

    def setUp(self):
        self.bus = MessageBus()
        self.tom_module_id = f"TestToMModule_{str(uuid.uuid4())[:8]}"
        # Module instantiated per test method for a clean state
        self.received_tom_inferences: List[GenericMessage] = []
        self.test_observer_id = f"TestObserver_{str(uuid.uuid4())[:8]}"


    def _tom_inference_listener(self, message: GenericMessage):
        if isinstance(message.payload, ToMInferenceUpdatePayload):
            self.received_tom_inferences.append(message)

    def tearDown(self):
        self.received_tom_inferences.clear()

    # --- Test Subscriptions and Inference Triggering ---
    def test_handle_percept_data_triggers_inference_from_metadata(self):
        tom_module = ConcreteTheoryOfMindModule(message_bus=self.bus, module_id=self.tom_module_id)
        async def run_test_logic():
            self.bus.subscribe(self.test_observer_id, "ToMInferenceUpdate", self._tom_inference_listener)

            target_agent = "user_beta"
            percept_payload = PerceptDataPayload(
                percept_id="p_meta", modality="visual", content={"action": "waving_happily"},
                source_timestamp=datetime.now(timezone.utc),
                metadata={"observed_agent_id": target_agent}
            )
            bus_msg = GenericMessage("PerceptSys", "PerceptData", percept_payload, message_id="m_meta")

            self.bus.publish(bus_msg)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_tom_inferences), 1, "Inference from metadata not received")
            inference_msg = self.received_tom_inferences[0]
            self.assertEqual(inference_msg.source_module_id, self.tom_module_id)
            payload: ToMInferenceUpdatePayload = inference_msg.payload
            self.assertEqual(payload.target_agent_id, target_agent)
            # Assuming "waving_happily" might trigger happiness conjecture
            self.assertIn("happy", payload.inferred_state_type.lower() if payload.inferred_state_type else "")
            self.assertIn("m_meta", payload.source_evidence_ids)
            self.assertIn("p_meta", payload.source_evidence_ids)
        asyncio.run(run_test_logic())

    def test_handle_percept_data_triggers_inference_from_text_content(self):
        tom_module = ConcreteTheoryOfMindModule(message_bus=self.bus, module_id=self.tom_module_id)
        async def run_test_logic():
            self.bus.subscribe(self.test_observer_id, "ToMInferenceUpdate", self._tom_inference_listener)

            target_agent = "user_alpha"
            percept_content = f"{target_agent}: I am so sad today."
            percept_payload = PerceptDataPayload(
                percept_id="p_text", modality="text", content=percept_content,
                source_timestamp=datetime.now(timezone.utc)
            )
            bus_msg = GenericMessage("ChatSys", "PerceptData", percept_payload, message_id="m_text")

            self.bus.publish(bus_msg)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_tom_inferences), 1, "Inference from text content not received")
            inference_msg = self.received_tom_inferences[0]
            payload: ToMInferenceUpdatePayload = inference_msg.payload
            self.assertEqual(payload.target_agent_id, target_agent)
            self.assertEqual(payload.inferred_state_type, "emotion_sadness_conjecture")
        asyncio.run(run_test_logic())

    def test_handle_percept_data_triggers_inference_from_source_fallback(self):
        tom_module = ConcreteTheoryOfMindModule(message_bus=self.bus, module_id=self.tom_module_id)
        async def run_test_logic():
            self.bus.subscribe(self.test_observer_id, "ToMInferenceUpdate", self._tom_inference_listener)

            source_agent = "DistinctAgentSource"
            percept_payload = PerceptDataPayload(
                percept_id="p_fallback", modality="audio", content={"event": "sigh"},
                source_timestamp=datetime.now(timezone.utc)
            )
            bus_msg = GenericMessage(source_agent, "PerceptData", percept_payload)

            self.bus.publish(bus_msg)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_tom_inferences), 1, "Inference from source fallback not received")
            payload: ToMInferenceUpdatePayload = self.received_tom_inferences[0].payload
            self.assertEqual(payload.target_agent_id, source_agent)
            # "sigh" might not trigger a specific emotion in the simple logic, so check for general or low confidence
            self.assertTrue(payload.inferred_state_type == "general_state_conjecture" or payload.confidence < 0.3)
        asyncio.run(run_test_logic())

    def test_handle_percept_data_no_clear_target_agent(self):
        tom_module = ConcreteTheoryOfMindModule(message_bus=self.bus, module_id=self.tom_module_id)
        async def run_test_logic():
            self.bus.subscribe(self.test_observer_id, "ToMInferenceUpdate", self._tom_inference_listener)

            # Source is the ToM module itself, should be ignored for fallback. No other cues.
            percept_payload = PerceptDataPayload(
                percept_id="p_no_target", modality="general", content="ambient noise",
                source_timestamp=datetime.now(timezone.utc)
            )
            bus_msg = GenericMessage(self.tom_module_id, "PerceptData", percept_payload)

            initial_inference_count = tom_module._published_inferences_count
            self.bus.publish(bus_msg)
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_tom_inferences), 0, "Inference published when no clear target agent was expected.")
            self.assertEqual(tom_module._published_inferences_count, initial_inference_count)
        asyncio.run(run_test_logic())

    def test_handle_own_emotional_state_change_logs(self):
        tom_module = ConcreteTheoryOfMindModule(message_bus=self.bus, module_id=self.tom_module_id)
        async def run_test_logic():
            initial_handled_count = tom_module._handled_message_counts["EmotionalStateChange"]
            own_emotion_payload = EmotionalStateChangePayload(current_emotion_profile={"valence": -0.7, "arousal": 0.8})
            bus_msg = GenericMessage(self.tom_module_id, "EmotionalStateChange", own_emotion_payload) # Message from self

            self.bus.publish(bus_msg)
            await asyncio.sleep(0.01)

            self.assertEqual(tom_module._handled_message_counts["EmotionalStateChange"], initial_handled_count + 1)
            # Further checks could involve inspecting logs if the handler wrote specific log messages.
        asyncio.run(run_test_logic())

    # --- Test Direct infer_mental_state Publishing ---
    def test_direct_infer_mental_state_publishes(self):
        tom_module = ConcreteTheoryOfMindModule(message_bus=self.bus, module_id=self.tom_module_id)
        async def run_test_logic():
            self.bus.subscribe(self.test_observer_id, "ToMInferenceUpdate", self._tom_inference_listener)

            target_agent = "agent_direct_test"
            evidence = "Direct evidence of happiness"
            state_type = "emotion_happiness_conjecture"

            tom_module.infer_mental_state(target_agent, evidence, state_type, "direct_call_evidence_id")
            await asyncio.sleep(0.01)

            self.assertEqual(len(self.received_tom_inferences), 1)
            msg = self.received_tom_inferences[0]
            self.assertEqual(msg.source_module_id, self.tom_module_id)
            payload: ToMInferenceUpdatePayload = msg.payload
            self.assertEqual(payload.target_agent_id, target_agent)
            self.assertEqual(payload.inferred_state_type, state_type)
            self.assertIn("happy", payload.inferred_state_value.get("emotion", ""))
        asyncio.run(run_test_logic())

    def test_direct_infer_mental_state_no_bus(self):
        tom_no_bus = ConcreteTheoryOfMindModule(message_bus=None, module_id="NoBusToM")
        initial_inference_count = tom_no_bus._published_inferences_count
        try:
            tom_no_bus.infer_mental_state("agent_nobus", "evidence", "state")
        except Exception as e:
            self.fail(f"infer_mental_state raised an exception with no bus: {e}")
        self.assertEqual(tom_no_bus._published_inferences_count, initial_inference_count) # Should not increment as no bus to publish
        self.assertEqual(len(self.received_tom_inferences), 0)


    # --- Test get_status ---
    def test_get_module_status(self):
        tom_module = ConcreteTheoryOfMindModule(message_bus=self.bus, module_id=self.tom_module_id)
        status = tom_module.get_status()
        self.assertEqual(status["module_id"], self.tom_module_id)
        self.assertTrue(status["message_bus_configured"])
        self.assertEqual(status["agent_models_count"], 0)
        self.assertEqual(status["published_inferences_count"], 0)
        self.assertEqual(status["handled_perceptdata_count"], 0)

        # Simulate some activity
        async def run_activity():
            tom_module.infer_mental_state("agent1", "happy evidence", "emotion_happiness_conjecture")
            percept_payload = PerceptDataPayload("p1","text","user_x: hello", datetime.now(timezone.utc))
            self.bus.publish(GenericMessage(self.tom_module_id, "PerceptData", percept_payload))
            await asyncio.sleep(0.01) # Allow handler to run
        asyncio.run(run_activity())

        status_after = tom_module.get_status()
        self.assertEqual(status_after["published_inferences_count"], 1)
        self.assertEqual(status_after["handled_perceptdata_count"], 1)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

```
