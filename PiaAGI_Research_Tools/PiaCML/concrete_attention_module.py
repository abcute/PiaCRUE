from typing import Any, List, Dict, Optional
import datetime # Added for AttentionFocusUpdatePayload timestamp

try:
    from .base_attention_module import BaseAttentionModule
    from .message_bus import MessageBus
    from .core_messages import (
        GenericMessage, GoalUpdatePayload, AttentionFocusUpdatePayload,
        EmotionalStateChangePayload # Added formal import
    )
except ImportError:
    from base_attention_module import BaseAttentionModule # type: ignore
    try:
        from message_bus import MessageBus # type: ignore
        from core_messages import ( # type: ignore
            GenericMessage, GoalUpdatePayload, AttentionFocusUpdatePayload, # type: ignore
            EmotionalStateChangePayload # type: ignore
        )
    except ImportError:
        MessageBus = None # type: ignore
        GenericMessage = None # type: ignore
        GoalUpdatePayload = None # type: ignore
        AttentionFocusUpdatePayload = None # type: ignore
        EmotionalStateChangePayload = None # type: ignore

class ConcreteAttentionModule(BaseAttentionModule):
    """
    A concrete implementation of the BaseAttentionModule.
    Manages current attentional focus, can publish focus updates,
    and subscribe to GoalUpdate and EmotionalStateChange messages to modulate attention.
    """
    def __init__(self, message_bus: Optional[MessageBus] = None):
        """
        Initializes the ConcreteAttentionModule.

        Args:
            message_bus: An optional instance of MessageBus for communication.
        """
        self.current_focus: Optional[AttentionFocusUpdatePayload] = None
        self._active_filters: List[Dict[str, Any]] = [] # Kept from original for filter_information method
        self._cognitive_load_level: float = 0.0 # Kept from original

        self.message_bus = message_bus
        self.handled_goal_updates_for_attention: List[GoalUpdatePayload] = []
        self.handled_emotion_updates_for_attention: List[Dict] = [] # Assuming dict for EmotionalStateChangePayload

        bus_status_msg = "not configured"
        if self.message_bus:
            if GenericMessage and GoalUpdatePayload and AttentionFocusUpdatePayload: # Check core imports
                try:
                    self.message_bus.subscribe(
                        module_id="ConcreteAttentionModule_01", # Example ID
                        message_type="GoalUpdate",
                        callback=self.handle_goal_update_for_attention
                    )
                    self.message_bus.subscribe(
                        module_id="ConcreteAttentionModule_01",
                        message_type="EmotionalStateChange", # Assuming this is the message type string
                        callback=self.handle_emotion_update_for_attention
                    )
                    bus_status_msg = "configured and subscribed to GoalUpdate & EmotionalStateChange"
                except Exception as e:
                    bus_status_msg = f"configured but FAILED to subscribe: {e}"
            else:
                bus_status_msg = "configured but core message types for subscription not available"

        print(f"ConcreteAttentionModule initialized. Message bus {bus_status_msg}.")

    def set_attention_focus(self, item_id: Optional[str], focus_type: str, intensity: float, source_trigger_id: Optional[str] = None) -> bool:
        """
        Sets the current attentional focus and publishes an update.
        The priority logic from the old direct_attention is removed; this method now directly sets the focus.
        Callers are responsible for deciding if a focus shift is warranted.
        """
        if not (AttentionFocusUpdatePayload and GenericMessage): # Check imports
            print("Error: AttentionFocusUpdatePayload or GenericMessage not available. Cannot set focus or publish.")
            return False

        clamped_intensity = max(0.0, min(1.0, intensity))
        self.current_focus = AttentionFocusUpdatePayload(
            focused_item_id=item_id,
            focus_type=focus_type,
            intensity=clamped_intensity,
            source_trigger_message_id=source_trigger_id
            # timestamp is handled by default_factory
        )
        print(f"ConcreteAttentionModule: Attention focus set to '{item_id}' (Type: {focus_type}, Intensity: {clamped_intensity:.2f}).")

        if self.message_bus:
            message = GenericMessage(
                source_module_id="ConcreteAttentionModule_01", # Example ID
                message_type="AttentionFocusUpdate",
                payload=self.current_focus
            )
            try:
                self.message_bus.publish(message)
                print(f"ConcreteAttentionModule: Published AttentionFocusUpdate for '{item_id}'.")
            except Exception as e:
                print(f"ConcreteAttentionModule: Error publishing AttentionFocusUpdate: {e}")
        return True

    def handle_goal_update_for_attention(self, message: GenericMessage):
        """Handles GoalUpdate messages to potentially shift attention."""
        if GoalUpdatePayload and isinstance(message.payload, GoalUpdatePayload):
            payload: GoalUpdatePayload = message.payload
            self.handled_goal_updates_for_attention.append(payload)
            # print(f"AttentionModule: Received GoalUpdate for {payload.goal_id}, Priority: {payload.priority}, Status: {payload.status}") # Optional

            # Example: High priority active goals grab attention
            if payload.priority > 0.7 and payload.status in ["new", "active", "PENDING", "ACTIVE", "updated"]:
                # print(f"  AttentionModule: High priority goal {payload.goal_id} detected. Shifting attention.")
                self.set_attention_focus(
                    item_id=f"goal_{payload.goal_id}",
                    focus_type="goal_directed_trigger",
                    intensity=payload.priority, # Use goal priority as attention intensity (scaled 0-1 if needed)
                    source_trigger_id=message.message_id
                )
        else:
            print(f"AttentionModule received GoalUpdate with unexpected payload type: {type(message.payload)}")

    def handle_emotion_update_for_attention(self, message: GenericMessage):
        """Handles EmotionalStateChange messages to potentially modulate attention."""
        if not (EmotionalStateChangePayload and isinstance(message.payload, EmotionalStateChangePayload)):
            print(f"AttentionModule received EmotionalStateChange with unexpected payload type: {type(message.payload)}")
            return

        payload: EmotionalStateChangePayload = message.payload
        # Store the raw payload if needed, or just relevant parts. Storing the dict for compatibility if old tests use it.
        self.handled_emotion_updates_for_attention.append(payload.current_emotion_profile)

        arousal = payload.current_emotion_profile.get("arousal", 0.0)
        valence = payload.current_emotion_profile.get("valence", 0.0) # For logging or more complex logic

        print(f"AttentionModule: Received EmotionalStateChange: V={valence:.2f}, A={arousal:.2f}, Intensity (from payload): {payload.intensity:.2f}")


        if arousal > 0.7: # Example: High arousal intensifies focus
            print(f"  AttentionModule: High arousal ({arousal:.2f}) detected. Conceptually intensifying current focus.")
            current_item_id = self.current_focus.focused_item_id if self.current_focus else "general_environment_due_to_high_arousal"
            current_intensity = self.current_focus.intensity if self.current_focus else 0.3 # Base intensity if no prior focus

            new_intensity = min(1.0, current_intensity + 0.1 + (arousal - 0.7) * 0.5) # Increase intensity based on arousal
            self.set_attention_focus(
                item_id=current_item_id,
                focus_type="emotion_triggered_intensity_increase",
                intensity=new_intensity,
                source_trigger_id=message.message_id
            )
        elif arousal < 0.2 and self.current_focus and self.current_focus.focus_type == "emotion_triggered_intensity_increase":
            # Example: If arousal drops significantly, and current focus was due to emotion, maybe reduce intensity
            print(f"  AttentionModule: Low arousal ({arousal:.2f}) detected. Reducing intensity of emotion-triggered focus.")
            new_intensity = max(0.1, self.current_focus.intensity * 0.7) # Reduce intensity
            self.set_attention_focus(
                item_id=self.current_focus.focused_item_id,
                focus_type=self.current_focus.focus_type, # Keep type or change to "relaxed"
                intensity=new_intensity,
                source_trigger_id=message.message_id
            )
        # else: # No significant attentional shift based purely on this arousal level
            # print(f"  AttentionModule: Arousal level {arousal:.2f} did not trigger major focus intensity shift.")


    def filter_information(self, information_stream: List[Dict[str, Any]], current_focus_override: Optional[Any] = None) -> List[Dict[str, Any]]:
        """Filters information based on current focus (or override) and active filters."""
        # Use focused_item_id from self.current_focus if it's set
        effective_focus_target = None
        if current_focus_override is not None:
            effective_focus_target = current_focus_override
        elif self.current_focus and self.current_focus.focused_item_id is not None:
            effective_focus_target = self.current_focus.focused_item_id

        # print(f"ConcreteAttentionModule: Filtering {len(information_stream)} items. Effective focus target: '{effective_focus_target}'. Active filters: {self._active_filters}")

        if effective_focus_target:
            focused_stream = []
            for item in information_stream:
                is_relevant = False
                # Assuming effective_focus_target is a string ID
                if isinstance(effective_focus_target, str):
                    if 'tags' in item and isinstance(item['tags'], list) and effective_focus_target in item['tags']:
                        is_relevant = True
                    elif 'content' in item and isinstance(item['content'], str) and effective_focus_target in item['content']: # Simple string match
                        is_relevant = True
                    elif item.get('id') == effective_focus_target:
                        is_relevant = True
                if is_relevant:
                    focused_stream.append(item)
        else:
            focused_stream = list(information_stream)

        # Apply active filters if any (original logic largely kept)
        if not self._active_filters:
            # print(f"ConcreteAttentionModule: No active filters. Filtered stream (by focus only) contains {len(focused_stream)} items.")
            return focused_stream

        stream_after_active_filters = list(focused_stream)
        for active_filter in self._active_filters: # Removed f_idx for simplicity
            # print(f"ConcreteAttentionModule: Applying filter: {active_filter}")
            next_filtered_stream = []
            filter_type = active_filter.get('type')
            filter_key = active_filter.get('key')
            for item in stream_after_active_filters:
                passes_filter = False
                if filter_type == 'value_equals' and item.get(filter_key) == active_filter.get('value'): passes_filter = True
                elif filter_type == 'value_gt' and item.get(filter_key, 0) > active_filter.get('threshold'): passes_filter = True
                elif filter_type == 'tag_present' and active_filter.get('tag') in item.get('tags', []): passes_filter = True
                elif not filter_type : passes_filter = True # No specific type, pass all? Or make it strict? For PoC, pass.
                else: print(f"ConcreteAttentionModule: Unknown or unhandled filter type '{filter_type}'.") # Passes by default

                if passes_filter: next_filtered_stream.append(item)
            stream_after_active_filters = next_filtered_stream
        # print(f"ConcreteAttentionModule: Filtered stream (focus + active filters) contains {len(stream_after_active_filters)} items.")
        return stream_after_active_filters

    def manage_cognitive_load(self, current_load: float, capacity_thresholds: Dict[str, float]) -> Dict[str, Any]:
        """Manages cognitive load by adjusting internal state or suggesting actions."""
        self._cognitive_load_level = current_load
        # print(f"ConcreteAttentionModule: Managing cognitive load. Current: {current_load}, Thresholds: {capacity_thresholds}")
        action_taken = {'action': 'none', 'details': 'Load within acceptable limits.'}
        if current_load >= capacity_thresholds.get('overload', 0.9):
            action_taken = {'action': 'reduce_focus_strictness', 'details': 'Cognitive overload.'}
        elif current_load >= capacity_thresholds.get('optimal', 0.7):
            action_taken = {'action': 'maintain_focus', 'details': 'Optimal load.'}
        return action_taken

    def get_attentional_state(self) -> Dict[str, Any]:
        """Returns the current attentional state."""
        return {
            'current_focus_payload': self.current_focus.__dict__ if self.current_focus else None,
            'active_filters_count': len(self._active_filters), # Simplified from full list
            'cognitive_load_level': self._cognitive_load_level,
            'module_type': 'ConcreteAttentionModule'
        }

    # BaseAttentionModule compatibility for direct_attention if needed by other old code
    # This now calls the new set_attention_focus method.
    def direct_attention(self, focus_target: Any, priority: float, context: Dict[str, Any] = None) -> bool:
        """
        Compatibility method for BaseAttentionModule's direct_attention.
        Focuses attention based on a target and priority, mapping to new set_attention_focus.
        """
        # print(f"ConcreteAttentionModule: `direct_attention` called for '{focus_target}' with priority {priority}.")
        focus_type = (context.get("type", "direct_call") if context else "direct_call")
        item_id = str(focus_target) if not isinstance(focus_target, str) else focus_target

        # The old direct_attention had logic to only shift if priority was higher.
        # The new set_attention_focus always sets and publishes.
        # For compatibility, we can decide if we want to retain the priority check here.
        # For this PoC, let's assume direct_attention implies an override or important update.
        return self.set_attention_focus(item_id=item_id, focus_type=focus_type, intensity=priority, source_trigger_id=context.get("source_message_id") if context else None)


if __name__ == '__main__':
    # Example with MessageBus
    bus = MessageBus() if MessageBus else None
    attention_module = ConcreteAttentionModule(message_bus=bus)

    print("\n--- Initial State (with Bus) ---")
    print(attention_module.get_attentional_state())

    print("\n--- Setting Attention Focus (will publish if bus) ---")
    attention_module.set_attention_focus(item_id="goal_alpha", focus_type="goal_directed", intensity=0.8, source_trigger_id="msg_goal_init")
    print(attention_module.get_attentional_state())

    if bus and GoalUpdatePayload and GenericMessage: # Check imports
        # Simulate receiving a high-priority goal update
        print("\n--- Simulating GoalUpdate Message Reception ---")
        mock_goal_payload = GoalUpdatePayload(
            goal_id="super_urgent_goal",
            goal_description="Defuse the situation immediately!",
            priority=0.95, # High priority
            status="ACTIVE",
            originator="CrisisSystem"
        )
        goal_message = GenericMessage(
            source_module_id="CrisisSystem",
            message_type="GoalUpdate",
            payload=mock_goal_payload,
            message_id="crisis_msg_001"
        )
        # Manually call handler or publish if bus is real (for __main__ test, direct call is fine)
        # attention_module.handle_goal_update_for_attention(goal_message)
        bus.publish(goal_message) # Publish to the bus the module is subscribed to

        print("State after high-priority goal update:")
        final_state = attention_module.get_attentional_state()
        print(final_state)
        assert final_state['current_focus_payload']['focused_item_id'] == "goal_super_urgent_goal"
        assert final_state['current_focus_payload']['intensity'] == 0.95

        # Simulate high arousal emotion
        print("\n--- Simulating EmotionalStateChange Message Reception ---")
        if EmotionalStateChangePayload: # Check if class is available
            mock_emotion_data = {"valence": -0.5, "arousal": 0.85, "dominance": -0.3}
            # Use arousal as intensity for this payload, or a separate field if EmotionalStateChangePayload defines it differently
            # The current EmotionalStateChangePayload uses payload.intensity for the overall event intensity.
            # Let's assume the .intensity field of the payload is what we care about for overall impact,
            # and current_emotion_profile["arousal"] is the specific dimension value.
            # The handler uses payload.current_emotion_profile.get("arousal", 0.0).
            mock_emotion_payload_obj = EmotionalStateChangePayload(
                current_emotion_profile=mock_emotion_data,
                intensity=mock_emotion_data["arousal"] # Using arousal as proxy for payload intensity here
            )
            emotion_message = GenericMessage(
                source_module_id="EmotionModule",
                message_type="EmotionalStateChange",
                payload=mock_emotion_payload_obj, # Use the dataclass instance
                message_id="emotion_flare_002"
            )
            bus.publish(emotion_message)
            print("State after high arousal emotion update:")
            final_state_after_emotion = attention_module.get_attentional_state()
            print(final_state_after_emotion)
            # Intensity calculation based on handler:
            # current_intensity (was 0.95 from goal)
            # arousal = 0.85
            # new_intensity = min(1.0, 0.95 + 0.1 + (0.85 - 0.7) * 0.5) = min(1.0, 0.95 + 0.1 + 0.15 * 0.5) = min(1.0, 0.95 + 0.1 + 0.075) = min(1.0, 1.125) = 1.0
            assert final_state_after_emotion['current_focus_payload']['intensity'] == 1.0
            assert final_state_after_emotion['current_focus_payload']['focus_type'] == "emotion_triggered_intensity_increase"
        else:
            print("Skipping EmotionalStateChange simulation in __main__ due to missing EmotionalStateChangePayload class.")

    print("\nExample Usage Complete.")
