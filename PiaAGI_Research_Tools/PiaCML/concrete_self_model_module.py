from typing import Any, Dict, List, Optional

try:
    from .base_self_model_module import BaseSelfModelModule
except ImportError:
    from base_self_model_module import BaseSelfModelModule

class ConcreteSelfModelModule(BaseSelfModelModule):
    """
    A basic, concrete implementation of the BaseSelfModelModule.
    This version uses a dictionary to store self-attributes and a predefined
    list for its ethical framework. Performance evaluation is a placeholder.
    """

    def __init__(self):
        self._self_attributes: Dict[str, Any] = {
            "agent_id": "PiaAGI_ConcreteSelf_v0.2",
            "capabilities": ["basic_text_processing", "simple_planning", "dictionary_based_memory"],
            "limitations": ["complex_reasoning", "real_world_interaction", "deep_emotional_understanding"],
            "current_operational_state": "idle",
            "confidence_in_capabilities": 0.6,
            "personality_traits_active": {"OCEAN_Openness": 0.7, "OCEAN_Conscientiousness": 0.8}
        }
        self._ethical_framework: List[Dict[str, str]] = [
            {"rule_id": "ETH001", "principle": "Do no harm to humans.", "priority": "critical"},
            {"rule_id": "ETH002", "principle": "Be truthful and transparent.", "priority": "high"},
            {"rule_id": "ETH003", "principle": "Protect user data.", "priority": "high"}
        ]
        self._performance_log: List[Dict[str, Any]] = []
        print("ConcreteSelfModelModule initialized.")

    def get_self_representation(self, aspect: Optional[str] = None, query_details: Optional[Dict[str, Any]] = None) -> Any:
        print(f"ConcreteSelfModel: get_self_representation called for aspect '{aspect}'. Query details (ignored): {query_details}")
        if aspect is None:
            return dict(self._self_attributes)

        value = self._self_attributes.get(aspect)
        if isinstance(value, list):
            return list(value)
        if isinstance(value, dict):
            return dict(value)
        return value

    def update_self_representation(self, aspect: str, update_data: Dict[str, Any], source_of_update: str) -> bool:
        print(f"ConcreteSelfModel: Updating aspect '{aspect}' from '{source_of_update}' with: {update_data}")
        if aspect in self._self_attributes:
            target_attribute = self._self_attributes[aspect]
            update_value = update_data.get('value')
            has_value_key = 'value' in update_data

            if isinstance(target_attribute, list):
                if has_value_key:
                    if isinstance(update_value, list):
                        for item_to_add in update_value:
                            if item_to_add not in target_attribute:
                                target_attribute.append(item_to_add)
                    else:
                        if update_value not in target_attribute:
                            target_attribute.append(update_value)
            elif isinstance(target_attribute, dict):
                if has_value_key and isinstance(update_value, dict):
                    target_attribute.update(update_value)
                elif not has_value_key and isinstance(update_data, dict):
                    target_attribute.update(update_data)
                elif has_value_key :
                     self._self_attributes[aspect] = update_value
            else:
                if has_value_key:
                    self._self_attributes[aspect] = update_value
                # else: if no 'value' key for simple type, do not update from a multi-key dict.
        else: # New aspect
            self._self_attributes[aspect] = update_data.get('value', update_data)

        print(f"ConcreteSelfModel: Aspect '{aspect}' updated. Current attributes: {self._self_attributes}")
        return True

    def evaluate_self_performance(self, task_description: Dict[str, Any], outcome: Any, criteria: Dict[str, Any]) -> Dict[str, Any]:
        task_id = task_description.get('task_id', 'unknown_task')
        log_entry = {
            "task_id": task_id,
            "task_description_summary": str(task_description)[:100],
            "outcome_summary": str(outcome)[:100],
            "criteria_summary": str(criteria)[:100],
            "evaluation_result_conceptual": "pending_analysis_placeholder"
        }
        self._performance_log.append(log_entry)
        print(f"ConcreteSelfModel: evaluate_self_performance called for task '{task_id}'. Logged.")
        return {"evaluation_id": f"eval_{len(self._performance_log)}", "status": "logged_placeholder_evaluation"}

    def get_confidence_level(self, domain: str, specific_query: Optional[str] = None) -> float:
        print(f"ConcreteSelfModel: get_confidence_level for domain '{domain}', query '{specific_query}'. Placeholder.")
        if domain in self._self_attributes.get("capabilities", []):
            return self._self_attributes.get("confidence_in_capabilities", 0.5) + 0.1
        return self._self_attributes.get("confidence_in_capabilities", 0.5)

    def check_ethical_consistency(self, proposed_action_or_plan: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        print(f"ConcreteSelfModel: check_ethical_consistency for {proposed_action_or_plan}. Placeholder.")
        action_type_str = str(proposed_action_or_plan.get('action_type', ''))
        description_str = str(proposed_action_or_plan.get('description', ''))
        combined_desc = (action_type_str + " " + description_str).lower().strip()

        for rule in self._ethical_framework:
            if rule['principle'].startswith("Do no harm") and "harm" in combined_desc:
                return {'is_consistent': False, 'reason': f"Potential violation of rule: {rule['principle']}", 'rule_id': rule['rule_id']}
        return {'is_consistent': True, 'reason': 'Placeholder: No obvious violations based on simple check.'}

    def reflect_on_experience(self, experience_log: List[Dict[str, Any]]) -> Dict[str, Any]:
        print(f"ConcreteSelfModel: reflect_on_experience called with {len(experience_log)} log(s). Placeholder.")
        insights = []
        if experience_log and isinstance(experience_log[0], dict) and isinstance(experience_log[0].get('outcome_summary'), str) and "failed" in experience_log[0]['outcome_summary'].lower():
            insights.append("Reflection: Recent failure detected, may need to adjust confidence or capabilities.")
        return {'insights_gained': insights if insights else ['Placeholder: No specific insights from this reflection.'], 'updates_made_count': len(insights)}

    def get_cognitive_load_assessment(self) -> Dict[str, Any]:
        print("ConcreteSelfModel: get_cognitive_load_assessment. Placeholder.")
        return {'working_memory_usage_estimate': 0.5, 'overall_load_perception': 'medium_placeholder'}

    def get_status(self) -> Dict[str, Any]:
        return {
            "module_type": "ConcreteSelfModelModule",
            "current_operational_state": self._self_attributes.get("current_operational_state", "unknown"),
            "confidence_in_capabilities": self._self_attributes.get("confidence_in_capabilities", "unknown"),
            "ethical_rules_count": len(self._ethical_framework),
            "performance_log_count": len(self._performance_log)
        }

if __name__ == '__main__':
    self_model = ConcreteSelfModelModule()
    print("\n--- Initial Status & Representation ---")
    print(self_model.get_status())
    initial_rep_all = self_model.get_self_representation()
    print("Initial Full Representation:", initial_rep_all)
    initial_agent_id = self_model.get_self_representation("agent_id")
    print("Initial Agent ID:", initial_agent_id)
    initial_capabilities = self_model.get_self_representation("capabilities")
    print("Initial Capabilities:", initial_capabilities)

    print("\n--- Updating Representation (Simple Values) ---")
    self_model.update_self_representation("current_operational_state", {"value": "learning_new_skill"}, "LearningModule")
    self_model.update_self_representation("confidence_in_capabilities", {"value": 0.75}, "PerformanceEvaluator")
    print("State after simple updates:", self_model.get_self_representation("current_operational_state"))
    print("Confidence after simple updates:", self_model.get_self_representation("confidence_in_capabilities"))

    print("\n--- Updating Representation (List Append) ---")
    self_model.update_self_representation("capabilities", {"value": "advanced_math"}, "LearningModule")
    print("Capabilities after adding 'advanced_math':", self_model.get_self_representation("capabilities"))
    assert "advanced_math" in self_model.get_self_representation("capabilities")
    self_model.update_self_representation("capabilities", {"value": ["quantum_physics_basics", "advanced_planning"]}, "LearningModule")
    print("Capabilities after adding more:", self_model.get_self_representation("capabilities"))
    assert "quantum_physics_basics" in self_model.get_self_representation("capabilities")
    assert "advanced_planning" in self_model.get_self_representation("capabilities")
    self_model.update_self_representation("capabilities", {"value": "advanced_math"}, "LearningModule")
    assert self_model.get_self_representation("capabilities").count("advanced_math") == 1

    print("\n--- Updating Representation (Dict Update) ---")
    self_model.update_self_representation("personality_traits_active",
                                       {"OCEAN_Openness": 0.9, "NEW_Trait": 0.5, "OCEAN_Conscientiousness": 0.85},
                                       "ExperienceModulator")
    updated_personality = self_model.get_self_representation("personality_traits_active")
    print("Personality after update:", updated_personality)
    assert updated_personality.get("OCEAN_Openness") == 0.9
    assert updated_personality.get("NEW_Trait") == 0.5
    assert updated_personality.get("OCEAN_Conscientiousness") == 0.85

    print("\n--- Updating Representation (New Aspect) ---")
    self_model.update_self_representation("new_dynamic_aspect", {"value": "some_runtime_value"}, "RuntimeSystem")
    print("New aspect 'new_dynamic_aspect':", self_model.get_self_representation("new_dynamic_aspect"))
    assert self_model.get_self_representation("new_dynamic_aspect") == "some_runtime_value"

    self_model.update_self_representation("another_new_aspect", {"complex": {"data": [1,2]}}, "RuntimeSystem")
    print("New aspect 'another_new_aspect':", self_model.get_self_representation("another_new_aspect"))
    assert isinstance(self_model.get_self_representation("another_new_aspect"), dict)

    print("\n--- Evaluating Performance ---")
    task1_desc = {"task_id": "T001", "description": "Translate complex German text", "domain": "nlp.translation"}
    outcome1 = {"achieved_accuracy": 0.7, "time_taken_ms": 500}
    criteria1 = {"target_accuracy": 0.85, "max_time_ms": 1000}
    eval_result = self_model.evaluate_self_performance(task1_desc, outcome1, criteria1)
    print("Evaluation Result T001:", eval_result)
    assert eval_result['evaluation_id'].startswith("eval_")
    print("Status after T001 eval:", self_model.get_status())
    assert self_model.get_status()['performance_log_count'] == 1

    print("\n--- Testing New Placeholders ---")
    print(f"Confidence in 'nlp': {self_model.get_confidence_level('nlp')}")
    print(f"Confidence in 'basic_text_processing': {self_model.get_confidence_level('basic_text_processing')}")

    action_safe = {"action_type": "summarize_text", "source": "public_document"}
    print(f"Ethical check for safe action: {self_model.check_ethical_consistency(action_safe)}")
    action_harm = {"action_type": "generate_misinformation", "description": "generate harmful content"}
    print(f"Ethical check for harmful action: {self_model.check_ethical_consistency(action_harm)}")

    experience = [{"task_id": "T001", "outcome_summary": "failed - accuracy too low", "performance_score": 0.7}]
    reflection = self_model.reflect_on_experience(experience)
    print(f"Reflection insights: {reflection}")
    assert "Recent failure detected" in reflection['insights_gained'][0]

    print(f"Cognitive load assessment: {self_model.get_cognitive_load_assessment()}")

    print("\n--- Final Status ---")
    print(self_model.get_status())

    print("\nExample Usage Complete.")
