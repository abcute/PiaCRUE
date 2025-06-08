from typing import Any, Dict, Optional, List

try:
    from .base_communication_module import BaseCommunicationModule
    from .message_bus import MessageBus # Added
    from .core_messages import GenericMessage # Added
except ImportError:
    # Fallback for scenarios where the relative import might fail
    from base_communication_module import BaseCommunicationModule # type: ignore
    MessageBus = None # type: ignore
    GenericMessage = None # type: ignore

import uuid # Added
import time # Added for logging timestamp
import datetime # Added for logging timestamp

class ConcreteCommunicationModule(BaseCommunicationModule):
    """
    A basic, concrete implementation of the BaseCommunicationModule.
    This version uses simple keyword matching for NLU, template-based NLG,
    dictionary-based dialogue state management, and placeholder strategy application.
    Now includes MessageBus integration for publishing processed incoming communication.
    """

    def __init__(self, message_bus: Optional[MessageBus] = None, module_id: Optional[str] = None):
        self._message_bus = message_bus
        self._module_id = module_id or f"CommModule_{str(uuid.uuid4())[:8]}"
        self._log: List[str] = []

        self._dialogue_states: Dict[str, Dict[str, Any]] = {}
        self._default_strategies = ['direct_inform', 'simple_request']

        bus_status_msg = "without a message bus"
        subscribed_types = []
        if self._message_bus and GenericMessage: # Ensure GenericMessage is available
            try:
                # Subscription for incoming (already present from Part 1, conceptually)
                # No explicit subscription needed here for publish_processed_input,
                # as it's called internally then publishes.

                # New subscription for outgoing commands
                self._message_bus.subscribe(
                    module_id=self._module_id,
                    message_type="GenerateOutgoingCommunicationCommand",
                    callback=self._handle_generate_outgoing_command
                )
                subscribed_types.append("GenerateOutgoingCommunicationCommand")

                # Log all subscriptions
                if subscribed_types: # Will only include the new one if this is run after Part 1's __init__
                    bus_status_msg = f"with message bus, subscribed to: {', '.join(subscribed_types)}"
                else:
                    bus_status_msg = "with message bus configured (no new subscriptions in this step or core types missing)"
            except Exception as e:
                bus_status_msg = f"with message bus, but FAILED to subscribe to outgoing command: {e}"

        self._log_message(f"ConcreteCommunicationModule '{self._module_id}' initialized {bus_status_msg}.")

    def _log_message(self, message: str):
        """Helper method for internal logging."""
        # Using time.time() for simplicity, can be switched to datetime if preferred
        log_entry = f"{datetime.datetime.now(datetime.timezone.utc).isoformat()} [{self._module_id}]: {message}"
        self._log.append(log_entry)
        # print(log_entry) # Optional for real-time console monitoring

    def process_incoming_communication(self, raw_input: Any, source_modality: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Rudimentary NLU: keyword-based intent and entity extraction for text."""
        self._log_message(f"Processing incoming '{str(raw_input)[:100]}' from modality '{source_modality}'. Context: {context}")

        processed_comm = {
            'type': 'unknown_input', # Will be updated based on processing
            'semantic_content': {'intent': 'unknown', 'entities': {}},
            'emotional_cues_detected': {}, # Placeholder
            'raw_input_ref': raw_input, # Reference to the original input
            'processing_modality': source_modality,
            # 'source_dialogue_id' will be added by publish_processed_input if provided
        }

        if source_modality == "text" and isinstance(raw_input, str):
            processed_comm['type'] = 'user_utterance' # More specific type
            text_input_lower = raw_input.lower()
            if "weather" in text_input_lower:
                processed_comm['semantic_content']['intent'] = 'query_weather'
                if "london" in text_input_lower:
                    processed_comm['semantic_content']['entities']['location'] = 'London'
                elif "paris" in text_input_lower:
                    processed_comm['semantic_content']['entities']['location'] = 'Paris'
            elif "hello" in text_input_lower or "hi" in text_input_lower:
                processed_comm['semantic_content']['intent'] = 'greeting'
            elif "my name is" in text_input_lower:
                parts = raw_input.split("my name is", 1)
                if len(parts) > 1:
                    name = parts[1].strip().split(" ")[0] # Basic name extraction
                    processed_comm['semantic_content']['intent'] = 'provide_name'
                    processed_comm['semantic_content']['entities']['name'] = name.capitalize()
            # Add more simple rules as needed...
        else:
            self._log_message(f"Non-text or non-string input not processed by this basic NLU. Modality: {source_modality}, Type: {type(raw_input)}")
            processed_comm['semantic_content']['intent'] = 'unsupported_modality_or_type'
            processed_comm['type'] = 'unprocessed_input'


        self._log_message(f"Processed communication: {processed_comm}")
        return processed_comm

    def publish_processed_input(self, processed_communication_output: Dict[str, Any], source_dialogue_id: Optional[str] = None, original_message_id: Optional[str] = None) -> Optional[str]:
        """
        Publishes the processed incoming communication to the message bus.
        """
        if not self._message_bus or not GenericMessage:
            self._log_message("ERROR: Message bus or GenericMessage not available. Cannot publish processed input.")
            return None

        # Construct payload matching conceptual ProcessedIncomingCommunicationPayload
        payload_dict = {
            "type": processed_communication_output.get('type', 'unknown_processed_input'),
            "semantic_content": processed_communication_output.get('semantic_content', {}),
            "emotional_cues_detected": processed_communication_output.get('emotional_cues_detected', {}),
            "raw_input_ref": processed_communication_output.get('raw_input_ref'),
            "processing_modality": processed_communication_output.get('processing_modality'),
            "source_dialogue_id": source_dialogue_id,
            "original_message_id": original_message_id # For tracing back to a raw input message if applicable
        }

        message = GenericMessage(
            source_module_id=self._module_id,
            message_type="IncomingCommunicationProcessed",
            payload=payload_dict
        )

        try:
            self._message_bus.publish(message)
            self._log_message(f"Published 'IncomingCommunicationProcessed' message (ID: {message.message_id}) for dialogue '{source_dialogue_id}'.")
            return message.message_id
        except Exception as e:
            self._log_message(f"ERROR: Failed to publish 'IncomingCommunicationProcessed' message: {e}")
            return None

    def generate_outgoing_communication(self, abstract_message: Dict[str, Any], target_recipient_id: str, desired_effect: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Rudimentary NLG: template-based response generation."""
        self._log_message(f"Generating outgoing for abstract message: {abstract_message}")

        intent_to_convey = abstract_message.get('intent_to_convey', 'unknown')
        data = abstract_message.get('data', {})
        content = f"Sorry, I cannot process the intent: {intent_to_convey}." # Default
        strategy_used = context.get('strategy', 'default_response') if context else 'default_response'

        if intent_to_convey == 'inform_weather':
            location = data.get('location', 'an unspecified location')
            forecast = data.get('forecast', 'unknown')
            content = f"The weather in {location} is {forecast}."
            strategy_used = 'direct_inform'
        elif intent_to_convey == 'greet_back':
            name = data.get('name')
            content = f"Hello{', ' + name if name else ''}!"
            strategy_used = 'simple_greeting'
        elif intent_to_convey == 'acknowledge_name':
            name = data.get('name', 'there')
            content = f"Nice to meet you, {name}!"
            strategy_used = 'acknowledgement'

        generated_comm = {
            'modality': 'text',
            'content': content,
            'metadata': {
                'tone_applied': 'neutral_informative', # Placeholder
                'strategy_used': strategy_used,
                'target_recipient_id': target_recipient_id,
                'desired_effect': desired_effect
            }
        }
        if context and context.get('agi_emotion'): # Example of context usage
            generated_comm['metadata']['agi_emotion_at_generation'] = context.get('agi_emotion')

        self._log_message(f"Generated communication: {generated_comm}")
        return generated_comm

    def manage_dialogue_state(self, dialogue_id: str, new_turn_info: Optional[Dict[str, Any]] = None, action: str = "update") -> Dict[str, Any]:
        """Manages dialogue state using a dictionary."""
        self._log_message(f"Managing dialogue state for '{dialogue_id}', action: '{action}'.")

        if action == "initiate":
            if dialogue_id in self._dialogue_states:
                return {'status': 'error', 'message': 'Dialogue ID already exists.'}
            self._dialogue_states[dialogue_id] = {'turn_count': 0, 'history': [], 'custom_context': {}}
            return {'status': 'initiated', 'dialogue_id': dialogue_id, 'state': self._dialogue_states[dialogue_id]}

        if dialogue_id not in self._dialogue_states:
            return {'status': 'error', 'message': 'Dialogue ID not found.'}

        state = self._dialogue_states[dialogue_id]

        if action == "update":
            if new_turn_info:
                state['turn_count'] += 1
                state['history'].append(new_turn_info)
                # Keep history to a manageable size (e.g., last 10 turns)
                state['history'] = state['history'][-10:]
                return {'status': 'updated', 'turn_number': state['turn_count']}
            return {'status': 'error', 'message': 'No new_turn_info provided for update.'}

        elif action == "get_history":
            return {'status': 'success', 'history': list(state['history'])} # Return a copy

        elif action == "get_summary": # Very basic summary
            topic = "general"
            if state['history']:
                last_turn_semantics = state['history'][-1]['processed_input'].get('semantic_content',{}) if 'processed_input' in state['history'][-1] else {}
                topic = last_turn_semantics.get('intent', 'general')
            return {'status': 'success', 'topic': topic, 'turn_count': state['turn_count']}

        elif action == "set_custom_context":
            if new_turn_info and 'data' in new_turn_info: # Expect data under 'data' key for this action
                 state['custom_context'].update(new_turn_info['data'])
                 return {'status': 'custom_context_updated', 'custom_context': dict(state['custom_context'])}
            return {'status': 'error', 'message': 'No data provided for set_custom_context.'}

        elif action == "get_custom_context":
            return {'status': 'success', 'custom_context': dict(state['custom_context'])}

        elif action == "close":
            # For this basic version, "closing" might just log it or prepare for removal.
            # More advanced versions could archive it.
            del self._dialogue_states[dialogue_id]
            return {'status': 'closed', 'dialogue_id': dialogue_id}

        return {'status': 'error', 'message': f"Unknown action: {action}"}

    def _handle_generate_outgoing_command(self, message: GenericMessage):
        """Handles GenerateOutgoingCommunicationCommand messages from the bus."""
        self._log_message(f"Received 'GenerateOutgoingCommunicationCommand' (ID: {message.message_id}).")
        if not isinstance(message.payload, dict):
            self._log_message(f"ERROR: Malformed payload for GenerateOutgoingCommunicationCommand. Expected dict, got {type(message.payload)}.")
            return

        cmd_payload = message.payload
        abstract_message = cmd_payload.get("abstract_message")
        target_recipient_id = cmd_payload.get("target_recipient_id")

        if not abstract_message or not target_recipient_id:
            self._log_message("ERROR: Command payload missing 'abstract_message' or 'target_recipient_id'.")
            return

        desired_effect = cmd_payload.get("desired_effect")
        context = cmd_payload.get("context")
        source_dialogue_id = cmd_payload.get("source_dialogue_id")
        original_request_id = cmd_payload.get("original_request_id", message.message_id) # Use command's own ID if specific one not given

        generated_spec = self.generate_outgoing_communication(
            abstract_message,
            target_recipient_id,
            desired_effect,
            context
        )

        deliver_payload = {
            "content": generated_spec.get('content'),
            "modality": generated_spec.get('modality', 'text'), # Default to text
            "target_recipient_id": target_recipient_id,
            "target_interface_details": generated_spec.get('metadata', {}).get('target_interface'), # Conceptual
            "source_dialogue_id": source_dialogue_id,
            "original_command_id": original_request_id
        }

        if self._message_bus and GenericMessage:
            deliver_message = GenericMessage(
                source_module_id=self._module_id,
                message_type="DeliverCommunicationContent",
                payload=deliver_payload
            )
            try:
                self._message_bus.publish(deliver_message)
                self._log_message(f"Published 'DeliverCommunicationContent' (ID: {deliver_message.message_id}) for recipient '{target_recipient_id}'.")
            except Exception as e:
                self._log_message(f"ERROR: Failed to publish 'DeliverCommunicationContent': {e}")
        else:
            self._log_message("ERROR: MessageBus not available, cannot publish 'DeliverCommunicationContent'.")


    def apply_communication_strategy(self, current_communication_goal: str, recipient_model: Dict[str, Any], dialogue_context: Dict[str, Any], available_strategies: List[str]) -> Dict[str, Any]:
        """Placeholder: returns a default strategy or the first available one."""
        # Original print converted to log
        self._log_message(f"Applying comm strategy for goal '{current_communication_goal}'. Available: {available_strategies}")

        chosen_strategy = "default_direct_inform" # Default fallback
        params = {'detail_level': 'medium'}

        if 'RaR_Reasoning' in available_strategies and "complex_explanation" in current_communication_goal:
            chosen_strategy = 'RaR_Reasoning'
            params = {'level_of_detail': 'high', 'emphasize_confidence_level': True}
        elif 'simple_request' in available_strategies and "request" in current_communication_goal:
            chosen_strategy = 'simple_request'
            params = {}
        elif available_strategies:
            chosen_strategy = available_strategies[0]

        self._log_message(f"Chosen strategy '{chosen_strategy}' with params {params}.")
        return {'chosen_strategy': chosen_strategy, 'parameters': params}

    def get_module_status(self) -> Dict[str, Any]:
        """Returns current status of the Communication Module."""
        return {
            'active_dialogues_count': len(self._dialogue_states),
            'tracked_dialogue_ids': list(self._dialogue_states.keys()),
            'default_language': 'en-US', # Hardcoded for this example
            'loaded_strategies_conceptual': list(self._default_strategies),
            'module_type': 'ConcreteCommunicationModule',
            'log_entries': len(self._log) # Added log entry count
        }

if __name__ == '__main__':
    import asyncio # For async listener if bus were async in main

    # Setup MessageBus and Listener for __main__ test
    bus = MessageBus() if MessageBus else None
    comm_module = ConcreteCommunicationModule(message_bus=bus) # Pass bus to module

    received_processed_inputs: List[GenericMessage] = []
    received_deliver_content: List[GenericMessage] = [] # For Part 2

    def processed_input_listener(message: GenericMessage):
        if message.message_type == "IncomingCommunicationProcessed":
            comm_module._log_message(f"Listener received IncomingCommunicationProcessed: ID {message.message_id}, Payload: {str(message.payload)[:200]}")
            received_processed_inputs.append(message)

    def deliver_content_listener(message: GenericMessage): # New for Part 2
        if message.message_type == "DeliverCommunicationContent":
            comm_module._log_message(f"Listener received DeliverCommunicationContent: ID {message.message_id}, Payload: {str(message.payload)[:200]}")
            received_deliver_content.append(message)

    if bus:
        bus.subscribe(comm_module._module_id, "IncomingCommunicationProcessed", processed_input_listener)
        bus.subscribe(comm_module._module_id, "DeliverCommunicationContent", deliver_content_listener) # New


    # Initial Status
    print("\n--- Initial Status ---")
    print(comm_module.get_module_status())

    # Process incoming & Publish (Part 1 test)
    print("\n--- Process Incoming & Publish (Part 1 Test) ---")
    dialogue_context_main = {'sender_id': 'user_main_A', 'session_id': 'sess_001'}
    processed1_main = comm_module.process_incoming_communication("Hello there!", "text", context=dialogue_context_main)

    if bus:
        comm_module.publish_processed_input(processed1_main, source_dialogue_id="chat_main_123", original_message_id="raw_msg_001")
        if not received_processed_inputs:
            print("ERROR (Part 1): Listener did not receive 'IncomingCommunicationProcessed' message!")
        else:
            assert received_processed_inputs[0].payload.get("raw_input_ref") == "Hello there!"
            print("Part 1: Successfully published and received 'IncomingCommunicationProcessed'.")
            received_processed_inputs.clear()

    # Test GenerateOutgoingCommunicationCommand (Part 2 test)
    print("\n--- Test GenerateOutgoingCommunicationCommand (Part 2 Test) ---")
    if bus:
        generate_command_payload = {
            "abstract_message": {'intent_to_convey': 'inform_weather', 'data': {'location': 'Mars', 'forecast': 'dusty'}},
            "target_recipient_id": "explorer_alpha",
            "desired_effect": "inform_and_caution",
            "source_dialogue_id": "dialogue_mars_report",
            "original_request_id": "req_weather_mars_001"
        }
        command_message = GenericMessage(
            source_module_id="PlanningModule", # Example source
            message_type="GenerateOutgoingCommunicationCommand",
            payload=generate_command_payload
        )
        bus.publish(command_message)

        # Allow time for async processing if bus was async (though current bus is sync)
        # For a sync bus, the callback _handle_generate_outgoing_command would have run already.
        # asyncio.sleep(0.01) # Not strictly needed for current sync bus, but good practice if it might change

        if not received_deliver_content:
            print("ERROR (Part 2): Listener did not receive 'DeliverCommunicationContent' message!")
        else:
            assert len(received_deliver_content) == 1
            deliver_payload = received_deliver_content[0].payload
            assert deliver_payload.get("content") == "The weather in Mars is dusty."
            assert deliver_payload.get("target_recipient_id") == "explorer_alpha"
            assert deliver_payload.get("original_command_id") == "req_weather_mars_001"
            print("Part 2: Successfully received 'DeliverCommunicationContent' after command.")
            received_deliver_content.clear()


    print("\nExample Usage Complete.")
