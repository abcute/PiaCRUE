from typing import Any, Dict, Optional, List

try:
    from .base_theory_of_mind_module import BaseTheoryOfMindModule
except ImportError:
    # Fallback for scenarios where the relative import might fail
    from base_theory_of_mind_module import BaseTheoryOfMindModule

class ConcreteTheoryOfMindModule(BaseTheoryOfMindModule):
    """
    A basic, concrete implementation of the BaseTheoryOfMindModule.
    This version uses a dictionary to store models of other agents and applies
    simple rule-based logic for inferring mental states.
    """

    def __init__(self):
        self._agent_models: Dict[str, Dict[str, Any]] = {}
        # Example: self._agent_models['user_001'] = {'inferred_beliefs': {'likes_red': True}, 'interaction_count': 5}
        print("ConcreteTheoryOfMindModule initialized.")

    def infer_mental_state(self, agent_id: str, observable_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Infers mental state based on observable data and simple rules.
        This is a very rudimentary implementation.
        """
        print(f"ConcreteToMModule: Inferring mental state for agent '{agent_id}' with data: {observable_data}")

        inferred_state = {
            'belief_state': {},
            'desire_state': {},
            'intention_state': {},
            'emotional_state_inferred': {'type': 'neutral', 'intensity': 0.5}, # Default
            'confidence_of_inference': 0.3 # Low confidence for this basic model
        }

        utterance = observable_data.get('utterance', "").lower()
        expression = observable_data.get('expression', "").lower()
        affective_cues = observable_data.get('affective_cues', [])

        # Simple rule: if user says "want X" and points, infer desire and intention for X
        if "want" in utterance and "pointing" in expression:
            parts = utterance.split("want", 1)
            if len(parts) > 1:
                target_object = parts[1].strip().split(" ")[0] # very naive parsing
                inferred_state['desire_state'] = {'goal': f"obtain_{target_object}", 'strength': 0.7}
                inferred_state['intention_state'] = {'action': f"request_{target_object}", 'confidence': 0.6}
                inferred_state['belief_state'][f"wants_{target_object}"] = True
                inferred_state['confidence_of_inference'] = 0.5

        if "happy" in affective_cues or "smiling" in expression:
            inferred_state['emotional_state_inferred'] = {'type': 'positive_generic', 'intensity': 0.6}
            inferred_state['confidence_of_inference'] = max(0.4, inferred_state['confidence_of_inference'])
        elif "sad" in affective_cues or "frowning" in expression:
            inferred_state['emotional_state_inferred'] = {'type': 'negative_generic', 'intensity': 0.6}
            inferred_state['confidence_of_inference'] = max(0.4, inferred_state['confidence_of_inference'])

        # Update or retrieve existing model for more context (rudimentary)
        if agent_id in self._agent_models:
            self._agent_models[agent_id].setdefault('inferred_mental_states_log', []).append(inferred_state)
            self._agent_models[agent_id]['interaction_count'] = self._agent_models[agent_id].get('interaction_count', 0) + 1
        else:
            # Create a basic model if none exists
            self._agent_models[agent_id] = {
                'inferred_mental_states_log': [inferred_state],
                'interaction_count': 1
            }

        print(f"ConcreteToMModule: Inferred state for '{agent_id}': {inferred_state}")
        return inferred_state

    def update_agent_model(self, agent_id: str, new_data: Dict[str, Any]) -> bool:
        """
        Updates the stored model for a specific agent.
        Merges new_data into the agent's model.
        """
        print(f"ConcreteToMModule: Updating model for agent '{agent_id}' with data: {new_data}")
        if agent_id not in self._agent_models:
            self._agent_models[agent_id] = {}
            print(f"ConcreteToMModule: Created new model for agent '{agent_id}'.")

        # Simple dictionary update/merge
        for key, value in new_data.items():
            if isinstance(value, dict) and isinstance(self._agent_models[agent_id].get(key), dict):
                self._agent_models[agent_id][key].update(value)
            else:
                self._agent_models[agent_id][key] = value

        # Ensure interaction_count is present if not already
        self._agent_models[agent_id].setdefault('interaction_count', 0)

        print(f"ConcreteToMModule: Model for '{agent_id}' updated. Current model: {self._agent_models[agent_id]}")
        return True

    def get_agent_model(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves the model for a specific agent."""
        print(f"ConcreteToMModule: Retrieving model for agent '{agent_id}'.")
        return self._agent_models.get(agent_id) # Returns None if agent_id not found

if __name__ == '__main__':
    tom_module = ConcreteTheoryOfMindModule()

    # Initial state
    print("\n--- Initial State (No Models) ---")
    print("Model for user1:", tom_module.get_agent_model("user1"))

    # Update agent model directly
    print("\n--- Updating Agent Model (user1) ---")
    tom_module.update_agent_model("user1", {"known_preference": "likes_tea", "last_mood": "neutral"})
    print("Model for user1 after update:", tom_module.get_agent_model("user1"))
    tom_module.update_agent_model("user1", {"known_preference": "likes_coffee", "interaction_count": 5}) # Overwrite and add
    print("Model for user1 after second update:", tom_module.get_agent_model("user1"))


    # Infer mental state for a new agent (user2)
    print("\n--- Inferring Mental State (user2) ---")
    observables_user2 = {'utterance': "I want that shiny red ball!", 'expression': 'pointing', 'affective_cues': ['excited']}
    inferred_user2 = tom_module.infer_mental_state("user2", observables_user2, context={'situation': 'playground'})
    print("Inferred state for user2:", inferred_user2)
    print("Model for user2 after inference:", tom_module.get_agent_model("user2"))

    # Another inference for user2
    observables_user2_sad = {'utterance': "I lost the ball.", 'affective_cues': ['sad', 'crying']}
    inferred_user2_sad = tom_module.infer_mental_state("user2", observables_user2_sad)
    print("Second inferred state for user2:", inferred_user2_sad)
    print("Model for user2 after second inference:", tom_module.get_agent_model("user2"))

    # Infer mental state for existing agent (user1)
    print("\n--- Inferring Mental State (user1) ---")
    observables_user1 = {'utterance': "I am happy today.", 'expression': 'smiling', 'affective_cues': ['happy']}
    inferred_user1 = tom_module.infer_mental_state("user1", observables_user1)
    print("Inferred state for user1:", inferred_user1)
    print("Model for user1 after inference:", tom_module.get_agent_model("user1"))


    # Get non-existent agent model
    print("\n--- Get Non-existent Model (user3) ---")
    print("Model for user3:", tom_module.get_agent_model("user3"))

    print("\nExample Usage Complete.")
