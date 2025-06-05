from typing import Any, Dict, List, Optional, Union, Deque
import uuid
from collections import deque
import asyncio # For __main__
import time # For __main__ timestamps

try:
    from .base_working_memory_module import BaseWorkingMemoryModule
    from .message_bus import MessageBus
    from .core_messages import (
        GenericMessage, PerceptDataPayload, LTMQueryResultPayload, MemoryItem,
        GoalUpdatePayload, EmotionalStateChangePayload, AttentionFocusUpdatePayload,
        LTMQueryPayload
    )
except ImportError:
    print("Warning: Running ConcreteWorkingMemoryModule with stubbed imports.")
    class BaseWorkingMemoryModule: pass
    MessageBus = None # type: ignore
    GenericMessage = object # type: ignore
    PerceptDataPayload = object # type: ignore
    LTMQueryResultPayload = object # type: ignore
    MemoryItem = object # type: ignore
    GoalUpdatePayload = object # type: ignore
    EmotionalStateChangePayload = object # type: ignore
    AttentionFocusUpdatePayload = object # type: ignore
    LTMQueryPayload = object # type: ignore


class ConcreteWorkingMemoryModule(BaseWorkingMemoryModule):
    """
    A concrete implementation of the BaseWorkingMemoryModule, integrated with a message bus.
    Manages a workspace of items with salience and capacity, and can interact with LTM.
    """

    DEFAULT_CAPACITY = 10 # Increased default capacity for more items from various sources

    def __init__(self,
                 capacity: int = DEFAULT_CAPACITY,
                 message_bus: Optional[MessageBus] = None,
                 module_id: str = f"WorkingMemoryModule_{str(uuid.uuid4())[:8]}"):
        self._module_id = module_id
        self._message_bus = message_bus
        self._workspace: List[Dict[str, Any]] = []
        self._capacity: int = capacity
        self._current_focus_id: Optional[str] = None
        self._item_counter: int = 0

        # For get_status reporting
        self._processed_message_counts: Dict[str, int] = {
            "PerceptData": 0, "LTMQueryResult": 0, "GoalUpdate": 0,
            "EmotionalStateChange": 0, "AttentionFocusUpdate": 0
        }
        self._ltm_queries_sent = 0

        bus_status_msg = "not configured"
        if self._message_bus:
            subscriptions = [
                ("PerceptData", self._handle_percept_data_message),
                ("LTMQueryResult", self._handle_ltm_query_result_message),
                ("GoalUpdate", self._handle_goal_update_message),
                ("EmotionalStateChange", self._handle_emotional_state_change_message),
                ("AttentionFocusUpdate", self._handle_attention_focus_update_message),
            ]
            subscribed_types = []
            try:
                core_types_available = all([GenericMessage, PerceptDataPayload, LTMQueryResultPayload,
                                            GoalUpdatePayload, EmotionalStateChangePayload, AttentionFocusUpdatePayload,
                                            LTMQueryPayload, MemoryItem])
                if core_types_available:
                    for msg_type, callback in subscriptions:
                        self._message_bus.subscribe(self._module_id, msg_type, callback)
                        subscribed_types.append(msg_type)
                    bus_status_msg = f"configured and subscribed to: {', '.join(subscribed_types)}"
                else:
                    bus_status_msg = "configured but core message types for subscription not available"
            except Exception as e:
                bus_status_msg = f"configured but FAILED to subscribe: {e}"
        print(f"ConcreteWorkingMemoryModule '{self._module_id}' initialized with capacity {self._capacity}. Message bus {bus_status_msg}.")

    def _generate_wm_id(self) -> str:
        self._item_counter += 1
        return f"wm_item_{self._module_id}_{self._item_counter}"

    # --- Message Handler Methods ---
    def _handle_percept_data_message(self, message: GenericMessage) -> None:
        if not isinstance(message.payload, PerceptDataPayload): return
        payload: PerceptDataPayload = message.payload
        self._processed_message_counts["PerceptData"] += 1
        item_content = {
            "type": "percept", "message_id": message.message_id,
            "modality": payload.modality, "content": payload.content,
            "id_from_source": payload.percept_id, "source_timestamp": payload.source_timestamp
        }
        # Percepts are generally high salience initially
        self.add_item_to_workspace(item_content, salience=0.8, context={"source": message.source_module_id})

    def _handle_ltm_query_result_message(self, message: GenericMessage) -> None:
        if not isinstance(message.payload, LTMQueryResultPayload): return
        payload: LTMQueryResultPayload = message.payload
        self._processed_message_counts["LTMQueryResult"] += 1
        # Summarize results to keep WM item manageable
        results_summary = [{"item_id": res.item_id, "content_preview": str(res.content)[:50]+"..."} for res in payload.results[:3]]
        item_content = {
            "type": "ltm_result", "message_id": message.message_id,
            "query_id": payload.query_id, "success": payload.success_status,
            "results_summary": results_summary, "result_count": len(payload.results),
            "error": payload.error_message
        }
        self.add_item_to_workspace(item_content, salience=0.7, context={"source": message.source_module_id})

    def _handle_goal_update_message(self, message: GenericMessage) -> None:
        if not isinstance(message.payload, GoalUpdatePayload): return
        payload: GoalUpdatePayload = message.payload
        self._processed_message_counts["GoalUpdate"] += 1
        item_content = {
            "type": "goal_info", "message_id": message.message_id,
            "goal_id": payload.goal_id, "description": payload.goal_description,
            "status": payload.status, "priority": payload.priority, "originator": payload.originator
        }
        # Update existing goal item or add new one. Goal priority affects salience.
        existing_item_id = None
        for item in self._workspace:
            if item.get("content", {}).get("type") == "goal_info" and item["content"].get("goal_id") == payload.goal_id:
                existing_item_id = item["id"]
                break
        if existing_item_id:
            self.update_item_in_workspace(existing_item_id, item_content, salience=0.6 + (payload.priority * 0.4))
        else:
            self.add_item_to_workspace(item_content, salience=0.6 + (payload.priority * 0.4), context={"source": message.source_module_id})


    def _handle_emotional_state_change_message(self, message: GenericMessage) -> None:
        if not isinstance(message.payload, EmotionalStateChangePayload): return
        payload: EmotionalStateChangePayload = message.payload
        self._processed_message_counts["EmotionalStateChange"] += 1
        item_content = {
            "type": "emotion_state", "message_id": message.message_id,
            "profile": payload.current_emotion_profile, "intensity": payload.intensity,
            "trigger_id": payload.triggering_event_id
        }
        # Emotion state might always be relevant, replace if exists or add
        existing_item_id = None
        for item in self._workspace:
            if item.get("content", {}).get("type") == "emotion_state":
                existing_item_id = item["id"]
                break
        if existing_item_id:
            self.update_item_in_workspace(existing_item_id, item_content, salience=0.9) # High salience
        else:
            self.add_item_to_workspace(item_content, salience=0.9, context={"source": message.source_module_id})


    def _handle_attention_focus_update_message(self, message: GenericMessage) -> None:
        if not isinstance(message.payload, AttentionFocusUpdatePayload): return
        payload: AttentionFocusUpdatePayload = message.payload
        self._processed_message_counts["AttentionFocusUpdate"] += 1
        item_content = {
            "type": "attention_focus", "message_id": message.message_id,
            "focused_item_id": payload.focused_item_id, "intensity": payload.intensity,
            "focus_type": payload.focus_type
        }
        # Store attention focus; could also be used to adjust salience of the focused_item_id if it's in WM
        # For now, just add/update the attention focus information itself.
        existing_item_id = None
        for item in self._workspace:
            if item.get("content", {}).get("type") == "attention_focus": # Assuming only one such item
                existing_item_id = item["id"]
                break
        if existing_item_id:
             self.update_item_in_workspace(existing_item_id, item_content, salience=0.95) # Very high salience
        else:
            self.add_item_to_workspace(item_content, salience=0.95, context={"source": message.source_module_id})

        if payload.focused_item_id:
            for item in self._workspace:
                # Check if focused_item_id matches a goal_id, percept_id, etc. within stored items
                if item["content"].get("goal_id") == payload.focused_item_id or \
                   item["content"].get("id_from_source") == payload.focused_item_id or \
                   item["id"] == payload.focused_item_id: # If WM item ID itself is the focus
                    new_salience = min(1.0, item.get("salience", 0.5) + (payload.intensity * 0.3)) # Boost based on attention intensity
                    self.update_item_in_workspace(item["id"], item["content"], new_salience)
                    print(f"WM ({self._module_id}): Boosted salience of item '{item['id']}' due to attention focus on '{payload.focused_item_id}'. New salience: {new_salience:.2f}")
                    break


    # --- LTM Querying ---
    def trigger_ltm_query_if_needed(self, item_id_in_wm: str, query_type: str = "semantic_details") -> Optional[str]:
        if not self._message_bus or not LTMQueryPayload or not GenericMessage:
            print(f"WM ({self._module_id}): MessageBus or LTMQueryPayload not available. Cannot trigger LTM query.")
            return None

        item = self.get_item_by_id(item_id_in_wm)
        if not item:
            print(f"WM ({self._module_id}): Item '{item_id_in_wm}' not found in workspace to trigger LTM query.")
            return None

        # Conceptual: Decide if more info is needed.
        # Example: if a percept is just a summary, or a goal needs elaboration.
        query_content_for_ltm: Any = None
        if item["content"].get("type") == "percept" and isinstance(item["content"].get("content"), dict):
            # If percept content is already detailed, maybe no query needed.
            # If it's a string, maybe query for its semantic meaning.
            if isinstance(item["content"]["content"], str):
                 query_content_for_ltm = item["content"]["content"] # Query about the text content
            elif isinstance(item["content"]["content"], dict) and item["content"]["content"].get("summary"):
                 query_content_for_ltm = item["content"]["content"].get("summary") # Query about summary
        elif item["content"].get("type") == "goal_info":
            query_content_for_ltm = item["content"]["description"] # Query about goal description

        if query_content_for_ltm:
            ltm_query_payload = LTMQueryPayload(
                requester_module_id=self._module_id,
                query_type=query_type,
                query_content=query_content_for_ltm,
                target_memory_type="semantic" if query_type == "semantic_details" else "episodic" # Example mapping
            )
            ltm_query_message = GenericMessage(
                source_module_id=self._module_id, message_type="LTMQuery", payload=ltm_query_payload
            )
            self._message_bus.publish(ltm_query_message)
            self._ltm_queries_sent +=1
            print(f"WM ({self._module_id}): Published LTMQuery (ID: {ltm_query_payload.query_id}) for WM item '{item_id_in_wm}', QueryType: '{query_type}'.")
            return ltm_query_payload.query_id
        else:
            print(f"WM ({self._module_id}): No LTM query triggered for item '{item_id_in_wm}'. Content not suitable or already detailed.")
            return None


    # --- Workspace Management Methods ---
    def add_item_to_workspace(self, item_content: Any, salience: float = 0.5, context: Optional[Dict[str, Any]] = None) -> str:
        wm_id = self._generate_wm_id()
        item = {'id': wm_id, 'content': item_content, 'salience': salience, 'timestamp': time.time(), 'context': context or {}}

        if len(self._workspace) >= self._capacity:
            self.manage_workspace_capacity_and_coherence(new_item_salience=salience)

        if len(self._workspace) < self._capacity:
            self._workspace.append(item)
            print(f"WM ({self._module_id}): Added item '{wm_id}' (Type: {item_content.get('type', 'N/A')}, Salience: {salience:.2f}). Size: {len(self._workspace)}/{self._capacity}")
            return wm_id
        else:
            print(f"WM ({self._module_id}): Add failed. Workspace full for item type '{item_content.get('type', 'N/A')}'. Size: {len(self._workspace)}/{self._capacity}")
            return "error_workspace_full"

    def update_item_in_workspace(self, item_id: str, new_content: Any, new_salience: Optional[float] = None) -> bool:
        for item in self._workspace:
            if item['id'] == item_id:
                item['content'] = new_content
                item['timestamp'] = time.time() # Update timestamp on modification
                if new_salience is not None:
                    item['salience'] = self._clamp_salience(new_salience)
                print(f"WM ({self._module_id}): Updated item '{item_id}'. New Salience: {item['salience']:.2f}")
                return True
        print(f"WM ({self._module_id}): Item '{item_id}' not found for update.")
        return False

    def _clamp_salience(self, salience: float) -> float:
        return max(0.0, min(1.0, salience))

    def remove_item_from_workspace(self, item_id: str) -> bool:
        original_len = len(self._workspace)
        self._workspace = [item for item in self._workspace if item['id'] != item_id]
        removed = len(self._workspace) < original_len
        if removed:
            if self._current_focus_id == item_id: self._current_focus_id = None
            print(f"WM ({self._module_id}): Removed item '{item_id}'.")
        return removed

    def get_workspace_contents(self) -> List[Dict[str, Any]]:
        return list(self._workspace) # Return a copy

    def get_item_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        for item in self._workspace:
            if item['id'] == item_id: return item
        return None

    def get_active_focus(self) -> Optional[Dict[str, Any]]:
        return self.get_item_by_id(self._current_focus_id) if self._current_focus_id else None

    def set_active_focus(self, item_id: str) -> bool:
        item = self.get_item_by_id(item_id)
        if item:
            self._current_focus_id = item_id
            item['salience'] = self._clamp_salience(item.get('salience', 0.5) + 0.1) # Boost focus
            self._workspace.sort(key=lambda x: x.get('salience', 0.0)) # Re-sort after salience change
            print(f"WM ({self._module_id}): Active focus set to item '{item_id}'.")
            return True
        return False

    def manage_workspace_capacity_and_coherence(self, new_item_salience: Optional[float] = None) -> None:
        self._workspace.sort(key=lambda x: x.get('salience', 0.0)) # Lowest first
        num_to_remove = 0
        if new_item_salience is not None and len(self._workspace) >= self._capacity:
            if self._workspace and self._workspace[0].get('salience', 0.0) < new_item_salience:
                num_to_remove = 1
        else:
            num_to_remove = len(self._workspace) - self._capacity

        for _ in range(min(num_to_remove, len(self._workspace))):
            removed_item = self._workspace.pop(0)
            if self._current_focus_id == removed_item['id']: self._current_focus_id = None
            print(f"WM ({self._module_id}): Removed item '{removed_item['id']}' (salience: {removed_item.get('salience')}) for capacity.")
        # Coherence placeholder

    def get_status(self) -> Dict[str, Any]:
        item_type_counts = {}
        for item in self._workspace:
            item_type = item.get("content", {}).get("type", "unknown")
            item_type_counts[item_type] = item_type_counts.get(item_type, 0) + 1

        return {
            "module_id": self._module_id,
            "module_type": "ConcreteWorkingMemoryModule (Message Bus Integrated)",
            "message_bus_configured": self._message_bus is not None,
            "current_size": len(self._workspace),
            "capacity": self._capacity,
            "current_focus_id": self._current_focus_id,
            "workspace_item_type_counts": item_type_counts,
            "processed_message_counts": dict(self._processed_message_counts),
            "ltm_queries_sent": self._ltm_queries_sent
        }

    # --- Adapting BaseMemoryModule methods ---
    def store(self, information: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        # 'information' is item_content, 'context' can contain salience.
        salience = (context or {}).get('salience', 0.5)
        return self.add_item_to_workspace(information, salience, context)

    def retrieve(self, query: Dict[str, Any], criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        # Simple query for WM: by 'id' or content key-value
        results: List[Dict[str, Any]] = []
        if "id" in query: results = [item for item in self._workspace if item["id"] == query["id"]]
        elif "content_query" in query and isinstance(query["content_query"], dict):
            cq = query["content_query"]
            key, val = cq.get("key"), cq.get("value")
            if key and val:
                results = [item for item in self._workspace if isinstance(item["content"], dict) and item["content"].get(key) == val]
        elif not query: return list(self._workspace) # Empty query returns all
        return results

    def delete_memory(self, memory_id: str) -> bool:
        return self.remove_item_from_workspace(memory_id)

    def manage_capacity(self) -> None: self.manage_workspace_capacity_and_coherence()
    def handle_forgetting(self, strategy: str = 'default') -> None: # Simplified
        if strategy == 'decay_salience':
            for item in self._workspace: item['salience'] = self._clamp_salience(item.get('salience',0.5) * 0.9)
            self._workspace.sort(key=lambda x: x.get('salience', 0.0))


if __name__ == '__main__':
    print("\n--- ConcreteWorkingMemoryModule __main__ Test ---")

    received_ltm_queries: List[GenericMessage] = []
    def ltm_query_listener(message: GenericMessage):
        print(f" ltm_query_listener: Received LTMQuery! Type: {message.payload.query_type}, Content: {message.payload.query_content}")
        received_ltm_queries.append(message)

    async def main_test_flow():
        bus = MessageBus()
        wm_module_id = "TestWM001"
        wm = ConcreteWorkingMemoryModule(message_bus=bus, module_id=wm_module_id, capacity=5)

        bus.subscribe(module_id="TestLTMQueryListener", message_type="LTMQuery", callback=ltm_query_listener)

        print(wm.get_status())

        print("\n--- Testing Subscriptions ---")
        # 1. PerceptData
        pd_payload = PerceptDataPayload(modality="text", content="User said hello", source_timestamp=datetime.now(timezone.utc))
        bus.publish(GenericMessage(source_module_id="TestPerceptSys", message_type="PerceptData", payload=pd_payload))
        await asyncio.sleep(0.01)
        assert any(item['content'].get('type') == 'percept' and item['content'].get('content') == "User said hello" for item in wm.get_workspace_contents())
        print("  WM received PerceptData.")

        # 2. LTMQueryResult
        ltm_res_payload = LTMQueryResultPayload(query_id="q_test_1", results=[MemoryItem(item_id="res1", content="LTM result content")], success_status=True)
        bus.publish(GenericMessage(source_module_id="TestLTMSys", message_type="LTMQueryResult", payload=ltm_res_payload))
        await asyncio.sleep(0.01)
        assert any(item['content'].get('type') == 'ltm_result' and item['content'].get('query_id') == "q_test_1" for item in wm.get_workspace_contents())
        print("  WM received LTMQueryResult.")

        # 3. GoalUpdate
        gu_payload = GoalUpdatePayload(goal_id="goal_explore", description="Explore surroundings", priority=0.8, status="ACTIVE", originator="MotSys")
        bus.publish(GenericMessage(source_module_id="TestMotSys", message_type="GoalUpdate", payload=gu_payload))
        await asyncio.sleep(0.01)
        assert any(item['content'].get('type') == 'goal_info' and item['content'].get('goal_id') == "goal_explore" for item in wm.get_workspace_contents())
        print("  WM received GoalUpdate.")

        # 4. EmotionalStateChange
        emo_payload = EmotionalStateChangePayload(current_emotion_profile={"v":0.2,"a":0.6,"d":0.1}, intensity=0.6)
        bus.publish(GenericMessage(source_module_id="TestEmoSys", message_type="EmotionalStateChange", payload=emo_payload))
        await asyncio.sleep(0.01)
        assert any(item['content'].get('type') == 'emotion_state' for item in wm.get_workspace_contents())
        print("  WM received EmotionalStateChange.")

        # 5. AttentionFocusUpdate
        attn_payload = AttentionFocusUpdatePayload(focused_item_id="goal_explore", focus_type="goal_directed", intensity=0.9, timestamp=datetime.now(timezone.utc))
        bus.publish(GenericMessage(source_module_id="TestAttnSys", message_type="AttentionFocusUpdate", payload=attn_payload))
        await asyncio.sleep(0.01)
        focus_item_in_wm = next((item for item in wm.get_workspace_contents() if item['content'].get('type') == 'attention_focus'), None)
        assert focus_item_in_wm is not None and focus_item_in_wm['content'].get('focused_item_id') == "goal_explore"
        # Check if salience of goal_explore was boosted
        goal_item_in_wm = next((item for item in wm.get_workspace_contents() if item['content'].get('type') == 'goal_info' and item['content'].get('goal_id') == "goal_explore"), None)
        assert goal_item_in_wm is not None and goal_item_in_wm['salience'] > (0.6 + (0.8*0.4)) # Original + boost
        print("  WM received AttentionFocusUpdate and boosted salience of focused goal.")

        print("\n--- Current WM Status ---")
        print(wm.get_status()) # Should show 5 items from subscriptions + 1 attention_focus item

        print("\n--- Testing trigger_ltm_query_if_needed ---")
        # Find the ID of the percept item in WM
        percept_wm_id = None
        for item in wm.get_workspace_contents():
            if item['content'].get('type') == 'percept':
                percept_wm_id = item['id']
                break
        assert percept_wm_id is not None, "Percept item not found in WM for LTM query test"

        query_id_sent = wm.trigger_ltm_query_if_needed(percept_wm_id, query_type="semantic_analysis")
        await asyncio.sleep(0.01)
        assert query_id_sent is not None, "LTM Query was not sent"
        assert len(received_ltm_queries) == 1
        assert received_ltm_queries[0].payload.query_id == query_id_sent
        assert received_ltm_queries[0].payload.query_content == "User said hello"
        assert received_ltm_queries[0].payload.requester_module_id == wm_module_id
        print("  LTMQuery successfully published by WM via trigger_ltm_query_if_needed.")

        print("\n--- Final WM Status ---")
        print(wm.get_status())
        assert wm.get_status()["ltm_queries_sent"] == 1
        assert wm.get_status()["processed_message_counts"]["PerceptData"] == 1

        print("\n--- ConcreteWorkingMemoryModule __main__ Test Complete ---")

    try:
        asyncio.run(main_test_flow())
    except RuntimeError as e:
        if " asyncio.run() cannot be called from a running event loop" in str(e):
            print("Skipping asyncio.run() as an event loop is already running.")
        else:
            raise
