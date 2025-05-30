from typing import Any, Dict, Optional, List

try:
    from .base_communication_module import BaseCommunicationModule
except ImportError:
    # Fallback for scenarios where the relative import might fail
    from base_communication_module import BaseCommunicationModule

class ConcreteCommunicationModule(BaseCommunicationModule):
    """
    A basic, concrete implementation of the BaseCommunicationModule.
    This version uses simple keyword matching for NLU, template-based NLG,
    dictionary-based dialogue state management, and placeholder strategy application.
    """

    def __init__(self):
        self._dialogue_states: Dict[str, Dict[str, Any]] = {}
        # Example: self._dialogue_states['chat_123'] = {'turn_count': 2, 'history': [...]}
        self._default_strategies = ['direct_inform', 'simple_request']
        print("ConcreteCommunicationModule initialized.")

    def process_incoming_communication(self, raw_input: Any, source_modality: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Rudimentary NLU: keyword-based intent and entity extraction for text."""
        print(f"ConcreteCommModule: Processing incoming '{raw_input}' from modality '{source_modality}'.")

        processed_comm = {
            'type': 'unknown_input',
            'semantic_content': {'intent': 'unknown', 'entities': {}},
            'emotional_cues_detected': {}, # Placeholder
            'raw_input_ref': raw_input,
            'processing_modality': source_modality
        }

        if source_modality == "text" and isinstance(raw_input, str):
            processed_comm['type'] = 'user_utterance'
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
                    name = parts[1].strip().split(" ")[0]
                    processed_comm['semantic_content']['intent'] = 'provide_name'
                    processed_comm['semantic_content']['entities']['name'] = name.capitalize()
            # Add more simple rules as needed...
        else:
            print(f"ConcreteCommModule: Non-text or non-string input not processed by this basic NLU.")
            processed_comm['semantic_content']['intent'] = 'unsupported_modality_or_type'

        print(f"ConcreteCommModule: Processed communication: {processed_comm}")
        return processed_comm

    def generate_outgoing_communication(self, abstract_message: Dict[str, Any], target_recipient_id: str, desired_effect: Optional[str] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Rudimentary NLG: template-based response generation."""
        print(f"ConcreteCommModule: Generating outgoing for abstract message: {abstract_message}")

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
        if context and context.get('agi_emotion'):
            generated_comm['metadata']['agi_emotion_at_generation'] = context.get('agi_emotion')

        print(f"ConcreteCommModule: Generated communication: {generated_comm}")
        return generated_comm

    def manage_dialogue_state(self, dialogue_id: str, new_turn_info: Optional[Dict[str, Any]] = None, action: str = "update") -> Dict[str, Any]:
        """Manages dialogue state using a dictionary."""
        print(f"ConcreteCommModule: Managing dialogue state for '{dialogue_id}', action: '{action}'.")

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


    def apply_communication_strategy(self, current_communication_goal: str, recipient_model: Dict[str, Any], dialogue_context: Dict[str, Any], available_strategies: List[str]) -> Dict[str, Any]:
        """Placeholder: returns a default strategy or the first available one."""
        print(f"ConcreteCommModule: Applying comm strategy for goal '{current_communication_goal}'.")

        chosen_strategy = "default_direct_inform" # Default fallback
        params = {'detail_level': 'medium'}

        if 'RaR_Reasoning' in available_strategies and "complex_explanation" in current_communication_goal:
            chosen_strategy = 'RaR_Reasoning'
            params = {'level_of_detail': 'high', 'emphasize_confidence_level': True}
        elif 'simple_request' in available_strategies and "request" in current_communication_goal:
            chosen_strategy = 'simple_request'
            params = {}
        elif available_strategies:
            chosen_strategy = available_strategies[0] # Just pick the first one if specific conditions not met

        print(f"ConcreteCommModule: Chosen strategy '{chosen_strategy}' with params {params}.")
        return {'chosen_strategy': chosen_strategy, 'parameters': params}

    def get_module_status(self) -> Dict[str, Any]:
        """Returns current status of the Communication Module."""
        return {
            'active_dialogues_count': len(self._dialogue_states),
            'tracked_dialogue_ids': list(self._dialogue_states.keys()),
            'default_language': 'en-US', # Hardcoded for this example
            'loaded_strategies_conceptual': list(self._default_strategies), # Conceptual
            'module_type': 'ConcreteCommunicationModule'
        }

if __name__ == '__main__':
    comm_module = ConcreteCommunicationModule()

    # Initial Status
    print("\n--- Initial Status ---")
    print(comm_module.get_module_status())

    # Process incoming
    print("\n--- Process Incoming ---")
    processed1 = comm_module.process_incoming_communication("Hello there!", "text", {'sender_id': 'user_A'})
    print("Processed 1:", processed1)
    processed2 = comm_module.process_incoming_communication("What's the weather in London?", "text")
    print("Processed 2:", processed2)
    processed3 = comm_module.process_incoming_communication("My name is Alex.", "text")
    print("Processed 3:", processed3)

    # Manage Dialogue State
    print("\n--- Manage Dialogue State ---")
    dialogue_id = "chat_xyz"
    comm_module.manage_dialogue_state(dialogue_id, action="initiate")
    print("State after init:", comm_module._dialogue_states.get(dialogue_id))

    turn1_info = {'processed_input': processed1, 'generated_output_abstract': {'intent_to_convey': 'greet_back'}}
    comm_module.manage_dialogue_state(dialogue_id, new_turn_info=turn1_info, action="update")
    print("State after turn 1:", comm_module._dialogue_states.get(dialogue_id))

    turn2_info = {'processed_input': processed2, 'generated_output_abstract': {'intent_to_convey': 'inform_weather', 'data': {'location': 'London', 'forecast': 'cloudy'}}}
    comm_module.manage_dialogue_state(dialogue_id, new_turn_info=turn2_info, action="update")

    print("History for chat_xyz:", comm_module.manage_dialogue_state(dialogue_id, action="get_history"))
    print("Summary for chat_xyz:", comm_module.manage_dialogue_state(dialogue_id, action="get_summary"))

    comm_module.manage_dialogue_state(dialogue_id, new_turn_info={'data': {'user_mood_estimated': 'neutral'}}, action="set_custom_context")
    print("Custom context for chat_xyz:", comm_module.manage_dialogue_state(dialogue_id, action="get_custom_context"))


    # Generate outgoing
    print("\n--- Generate Outgoing ---")
    abstract_msg1 = {'intent_to_convey': 'inform_weather', 'data': {'location': 'Paris', 'forecast': 'sunny'}}
    generated1 = comm_module.generate_outgoing_communication(abstract_msg1, "user_A", context={'agi_emotion': 'pleasant'})
    print("Generated 1:", generated1)

    abstract_msg2 = {'intent_to_convey': 'acknowledge_name', 'data': {'name': 'Alex'}}
    generated2 = comm_module.generate_outgoing_communication(abstract_msg2, "user_A")
    print("Generated 2:", generated2)


    # Apply communication strategy
    print("\n--- Apply Communication Strategy ---")
    strategy_choice = comm_module.apply_communication_strategy(
        current_communication_goal="clarify_ambiguity",
        recipient_model={'inferred_knowledge_level': 'expert'}, # Mock ToM data
        dialogue_context=comm_module.manage_dialogue_state(dialogue_id, action="get_summary").get('summary_data',{}), # Mock dialogue context
        available_strategies=['simple_request', 'RaR_Reasoning', 'CSIM_Schema_Bridging']
    )
    print("Strategy Choice:", strategy_choice)

    strategy_choice_complex = comm_module.apply_communication_strategy(
        current_communication_goal="explain_complex_topic_A",
        recipient_model={'inferred_knowledge_level': 'novice'},
        dialogue_context={},
        available_strategies=['RaR_Reasoning', 'direct_inform']
    )
    print("Strategy Choice (Complex):", strategy_choice_complex)


    # Close dialogue
    print("\n--- Close Dialogue ---")
    print(comm_module.manage_dialogue_state(dialogue_id, action="close"))
    print("Status after close:", comm_module.get_module_status())

    print("\nExample Usage Complete.")
