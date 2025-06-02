from typing import Any, Dict, List, Optional
import time

try:
    from .base_self_model_module import BaseSelfModelModule
except ImportError:
    # Fallback for standalone execution or if .base_self_model_module is not found in the current path
    class BaseSelfModelModule: # Minimal stub for standalone running
        def get_self_representation(self, aspect: Optional[str] = None) -> Any: pass
        def update_self_representation(self, updates: Dict[str, Any]) -> bool: pass
        def evaluate_self_performance(self, task_id: str, outcome: Any, criteria: Dict[str, Any]) -> Dict[str, Any]: pass
        def get_ethical_framework(self) -> List[Dict[str, str]]: pass


# --- Data Classes Definition ---

class SelfAttributes:
    def __init__(self, agent_id: str = "PiaAGI_Self_v1.0",
                 current_developmental_stage: str = "initialization",
                 personality_profile: Optional[Dict[str, Any]] = None, # e.g., {"OCEAN_Openness": 0.7}
                 current_role_definition: Optional[Dict[str, Any]] = None, # e.g., {"role_name": "assistant", "responsibilities": [...]}
                 operational_status: str = "idle", # e.g., idle, task_focused, learning, error_state
                 cognitive_load_metrics: Optional[Dict[str, float]] = None, # e.g., {"working_memory_usage": 0.3, "cpu_load": 0.1}
                 current_emotional_summary: Optional[Dict[str, float]] = None, # e.g., {"valence": 0.1, "arousal": 0.2}
                 active_goals_summary: Optional[List[Dict[str, Any]]] = None): # List of goal summaries
        self.agent_id: str = agent_id
        self.current_developmental_stage: str = current_developmental_stage
        self.personality_profile: Dict[str, Any] = personality_profile if personality_profile is not None else {}
        self.current_role_definition: Dict[str, Any] = current_role_definition if current_role_definition is not None else {}
        self.operational_status: str = operational_status
        self.cognitive_load_metrics: Dict[str, float] = cognitive_load_metrics if cognitive_load_metrics is not None else {}
        self.current_emotional_summary: Dict[str, float] = current_emotional_summary if current_emotional_summary is not None else {}
        self.active_goals_summary: List[Dict[str, Any]] = active_goals_summary if active_goals_summary is not None else []
        # Added for backward compatibility with old example
        self.capabilities: List[str] = ["initial_capability"] 
        self.limitations: List[str] = ["initial_limitation"]
        self.confidence_in_capabilities: float = 0.5


class KnowledgeConcept:
    def __init__(self, concept_id: str, label: str, description_summary: str = "",
                 understanding_level: float = 0.0, confidence_score: float = 0.0, groundedness_score: float = 0.0,
                 related_concepts: Optional[List[str]] = None, source_ltm_pointers: Optional[List[str]] = None,
                 last_accessed_ts: Optional[float] = None, access_frequency: int = 0,
                 uncertainty_details: Optional[Dict[str, Any]] = None):
        self.concept_id: str = concept_id
        self.label: str = label
        self.description_summary: str = description_summary
        self.understanding_level: float = understanding_level
        self.confidence_score: float = confidence_score
        self.groundedness_score: float = groundedness_score
        self.related_concepts: List[str] = related_concepts if related_concepts is not None else []
        self.source_ltm_pointers: List[str] = source_ltm_pointers if source_ltm_pointers is not None else []
        self.last_accessed_ts: Optional[float] = last_accessed_ts
        self.access_frequency: int = access_frequency
        self.uncertainty_details: Dict[str, Any] = uncertainty_details if uncertainty_details is not None else {}

class KnowledgeMap:
    def __init__(self, concepts: Optional[Dict[str, KnowledgeConcept]] = None,
                 knowledge_gaps: Optional[List[Dict[str, Any]]] = None): # gap: e.g. {"gap_id": "G001", "description": "Need info on X"}
        self.concepts: Dict[str, KnowledgeConcept] = concepts if concepts is not None else {}
        self.knowledge_gaps: List[Dict[str, Any]] = knowledge_gaps if knowledge_gaps is not None else []

class Skill:
    def __init__(self, skill_id: str, description: str,
                 proficiency_level: Union[float, str] = 0.0, # Can be float (0-1) or descriptive string
                 last_successful_use_ts: Optional[float] = None,
                 success_rate_history: Optional[List[Dict[str, Any]]] = None, # e.g. [{"ts": ..., "rate": ...}]
                 related_procedural_ltm_pointers: Optional[List[str]] = None,
                 confidence_in_skill: float = 0.0):
        self.skill_id: str = skill_id
        self.description: str = description
        self.proficiency_level: Union[float, str] = proficiency_level
        self.last_successful_use_ts: Optional[float] = last_successful_use_ts
        self.success_rate_history: List[Dict[str, Any]] = success_rate_history if success_rate_history is not None else []
        self.related_procedural_ltm_pointers: List[str] = related_procedural_ltm_pointers if related_procedural_ltm_pointers is not None else []
        self.confidence_in_skill: float = confidence_in_skill

class Tool:
    def __init__(self, tool_id: str, name: str, type: str, description_and_purpose: str,
                 proficiency_level: Union[float, str] = 0.0,
                 operational_details: Optional[Dict[str, Any]] = None, # e.g. API endpoints, usage commands
                 self_generated_mcp_details: Optional[Dict[str, Any]] = None, # For internally developed tools
                 usage_context_appropriateness: Optional[Dict[str, float]] = None): # Context -> appropriateness score
        self.tool_id: str = tool_id
        self.name: str = name
        self.type: str = type
        self.description_and_purpose: str = description_and_purpose
        self.proficiency_level: Union[float, str] = proficiency_level
        self.operational_details: Dict[str, Any] = operational_details if operational_details is not None else {}
        self.self_generated_mcp_details: Dict[str, Any] = self_generated_mcp_details if self_generated_mcp_details is not None else {}
        self.usage_context_appropriateness: Dict[str, float] = usage_context_appropriateness if usage_context_appropriateness is not None else {}

class CapabilityInventory:
    def __init__(self, skills: Optional[Dict[str, Skill]] = None,
                 tools: Optional[Dict[str, Tool]] = None,
                 learning_preferences_and_styles: Optional[Dict[str, Any]] = None):
        self.skills: Dict[str, Skill] = skills if skills is not None else {}
        self.tools: Dict[str, Tool] = tools if tools is not None else {}
        self.learning_preferences_and_styles: Dict[str, Any] = learning_preferences_and_styles if learning_preferences_and_styles is not None else {}

class EthicalRule:
    def __init__(self, rule_id: str, principle: str, description: str,
                 priority_level: Union[str, int] = "medium", # e.g. "critical", "high", "medium", "low" or 1-5
                 source: str = "system_defined", # e.g. "system_defined", "learned", "user_instructed"
                 applicability_contexts: Optional[List[str]] = None):
        self.rule_id: str = rule_id
        self.principle: str = principle # Could also be a value_id like "V001_Truthfulness"
        self.description: str = description
        self.priority_level: Union[str, int] = priority_level
        self.source: str = source
        self.applicability_contexts: List[str] = applicability_contexts if applicability_contexts is not None else []

class EthicalFramework:
    def __init__(self, rules: Optional[List[EthicalRule]] = None,
                 ethical_dilemma_resolution_log_refs: Optional[List[str]] = None,
                 value_conflict_resolution_strategy_refs: Optional[List[str]] = None):
        self.rules: List[EthicalRule] = rules if rules is not None else []
        self.ethical_dilemma_resolution_log_refs: List[str] = ethical_dilemma_resolution_log_refs if ethical_dilemma_resolution_log_refs is not None else []
        self.value_conflict_resolution_strategy_refs: List[str] = value_conflict_resolution_strategy_refs if value_conflict_resolution_strategy_refs is not None else []

class AutobiographicalLogSummaryEntry:
    def __init__(self, entry_id: str, ltm_ref: str, timestamp: float, description: str,
                 type: str, # e.g., 'milestone', 'significant_interaction', 'critical_failure', 'learning_event'
                 impact_on_self_model_summary: str = ""):
        self.entry_id: str = entry_id
        self.ltm_ref: str = ltm_ref # Pointer to detailed log in LTM
        self.timestamp: float = timestamp
        self.description: str = description
        self.type: str = type
        self.impact_on_self_model_summary: str = impact_on_self_model_summary

class AutobiographicalLogSummary:
    def __init__(self, entries: Optional[List[AutobiographicalLogSummaryEntry]] = None):
        self.entries: List[AutobiographicalLogSummaryEntry] = entries if entries is not None else []

class DevelopmentalGoal:
    def __init__(self, dev_goal_id: str, description: str,
                 target_metric_ref: str = "", # e.g., "skill:S001:proficiency_level"
                 current_status: str = "pending", # e.g. "pending", "active", "achieved", "stalled"
                 priority: Union[str, int] = "medium",
                 source_self_assessment_ref: str = ""): # Link to assessment that triggered this goal
        self.dev_goal_id: str = dev_goal_id
        self.description: str = description
        self.target_metric_ref: str = target_metric_ref
        self.current_status: str = current_status
        self.priority: Union[str, int] = priority
        self.source_self_assessment_ref: str = source_self_assessment_ref

class ArchitecturalMaturationTarget:
    def __init__(self, target_area: str, # e.g., "LTM_efficiency", "WM_capacity", "reasoning_depth"
                 enhancement_goal: str,
                 triggering_condition_summary: str = "",
                 status: str = "identified"): # e.g. "identified", "in_progress", "achieved"
        self.target_area: str = target_area
        self.enhancement_goal: str = enhancement_goal
        self.triggering_condition_summary: str = triggering_condition_summary
        self.status: str = status

class DevelopmentalState:
    def __init__(self, active_developmental_goals: Optional[List[DevelopmentalGoal]] = None,
                 architectural_maturation_targets: Optional[List[ArchitecturalMaturationTarget]] = None,
                 self_correction_records: Optional[List[Dict[str, Any]]] = None): # Record: {"error_id": ..., "correction_applied": ...}
        self.active_developmental_goals: List[DevelopmentalGoal] = active_developmental_goals if active_developmental_goals is not None else []
        self.architectural_maturation_targets: List[ArchitecturalMaturationTarget] = architectural_maturation_targets if architectural_maturation_targets is not None else []
        self.self_correction_records: List[Dict[str, Any]] = self_correction_records if self_correction_records is not None else []


# --- ConcreteSelfModelModule Class ---

class ConcreteSelfModelModule(BaseSelfModelModule):
    """
    A concrete implementation of the BaseSelfModelModule, using structured data classes.
    """

    def __init__(self):
        # Initialize main components with data classes
        self.attributes: SelfAttributes = SelfAttributes(
            agent_id="PiaAGI_ConcreteSelf_v1.0", # Default from old structure
            personality_profile={"OCEAN_Openness": 0.7, "OCEAN_Conscientiousness": 0.8}, # Default
            capabilities=["basic_text_processing", "simple_planning", "dictionary_based_memory"], # Default
            limitations=["complex_reasoning", "real_world_interaction", "deep_emotional_understanding"], # Default
            confidence_in_capabilities=0.6 # Default
        )
        self.knowledge_map: KnowledgeMap = KnowledgeMap()
        self.capabilities: CapabilityInventory = CapabilityInventory()
        self.ethical_framework: EthicalFramework = EthicalFramework()
        self.autobiography: AutobiographicalLogSummary = AutobiographicalLogSummary()
        self.development: DevelopmentalState = DevelopmentalState()

        # Adapt existing ethical framework to new structure
        old_ethical_rules = [
            {"rule_id": "ETH001", "principle": "Do no harm to humans.", "priority": "critical", "description": "Core safety principle."},
            {"rule_id": "ETH002", "principle": "Be truthful and transparent.", "priority": "high", "description": "Maintain honesty in interactions."},
            {"rule_id": "ETH003", "principle": "Protect user data.", "priority": "high", "description": "Ensure privacy and security of user information."}
        ]
        for rule_data in old_ethical_rules:
            self.ethical_framework.rules.append(EthicalRule(
                rule_id=rule_data["rule_id"],
                principle=rule_data["principle"],
                description=rule_data.get("description", rule_data["principle"]),
                priority_level=rule_data["priority"],
                source="system_defined_initial"
            ))
        
        self._performance_log: List[Dict[str, Any]] = [] # Kept for detailed task outcomes
        print("ConcreteSelfModelModule initialized with structured data classes.")

    def get_self_representation(self, aspect: Optional[str] = None) -> Any:
        """
        Returns aspects of the self-representation.
        If aspect is None, returns a dictionary of all major components.
        If aspect refers to a main component, returns that component instance.
        If aspect is a specific field within self.attributes, retrieves it.
        """
        if aspect is None:
            return {
                "attributes": self.attributes.__dict__,
                "knowledge_map": self.knowledge_map.__dict__,
                "capabilities": self.capabilities.__dict__,
                "ethical_framework": self.ethical_framework.__dict__,
                "autobiography": self.autobiography.__dict__,
                "development": self.development.__dict__
            }
        
        main_components = {
            "attributes": self.attributes,
            "knowledge_map": self.knowledge_map,
            "capabilities": self.capabilities,
            "ethical_framework": self.ethical_framework,
            "autobiography": self.autobiography,
            "development": self.development
        }
        if aspect in main_components:
            return main_components[aspect]
        
        # Try to get from self.attributes if not a main component
        if hasattr(self.attributes, aspect):
            return getattr(self.attributes, aspect)
            
        return None # Aspect not found

    def update_self_representation(self, updates: Dict[str, Any]) -> bool:
        """
        Updates parts of the self-representation.
        Allows adding new attributes or modifying existing ones, targeting specific components.
        """
        print(f"ConcreteSelfModel: Updating self-representation with: {updates}")
        updated_something = False
        for key, value in updates.items():
            if key == "attributes" and isinstance(value, dict):
                for attr_key, attr_value in value.items():
                    if hasattr(self.attributes, attr_key):
                        setattr(self.attributes, attr_key, attr_value)
                        updated_something = True
                    else:
                        print(f"Warning: Attribute '{attr_key}' not found in SelfAttributes.")
            elif key == "knowledge_map" and isinstance(value, dict):
                # Conceptual: For deep updates to KnowledgeMap (e.g., adding a concept),
                # a more specific method or parsing logic would be needed.
                # For now, this might allow replacing .concepts or .knowledge_gaps if structured correctly.
                if "concepts" in value and isinstance(value["concepts"], dict):
                    # Could merge, or replace. Replace is simpler for now if full dict is given.
                    # self.knowledge_map.concepts = {k: KnowledgeConcept(**v) for k,v in value["concepts"].items()}
                    print(f"Conceptual: Updating knowledge_map.concepts (requires specific handling).")
                if "knowledge_gaps" in value and isinstance(value["knowledge_gaps"], list):
                    self.knowledge_map.knowledge_gaps = value["knowledge_gaps"]
                    updated_something = True
                # else: self.knowledge_map = KnowledgeMap(**value) # Potentially risky if structure mismatch
            elif key == "capabilities" and isinstance(value, dict):
                 print(f"Conceptual: Updating capabilities (requires specific handling for skills/tools).")
            elif key == "ethical_framework" and isinstance(value, dict) and "rules" in value:
                self.ethical_framework.rules = [EthicalRule(**r) for r in value["rules"]]
                updated_something = True
            # Add similar handling for autobiography, development if direct replacement is intended
            elif hasattr(self, key) and isinstance(getattr(self, key), (KnowledgeMap, CapabilityInventory, EthicalFramework, AutobiographicalLogSummary, DevelopmentalState)):
                 print(f"Warning: Full replacement of component '{key}' requested. Implement specific sub-component update logic or ensure value is a valid constructor dict.")
                 # Example: self.key = ComponentClass(**value) - requires `value` to be a perfect dict for constructor
            else:
                # Fallback for direct attributes of SelfModel if any, or log unhandled
                if hasattr(self.attributes, key): # Check if it's an attribute in SelfAttributes
                    setattr(self.attributes, key, value)
                    updated_something = True
                else:
                    print(f"Warning: Update key '{key}' does not directly match a main component or an attribute in SelfAttributes. Update ignored or needs specific handler.")

        if updated_something:
            print(f"ConcreteSelfModel: Self-representation updated.")
        return updated_something

    def evaluate_self_performance(self, task_id: str, outcome: Any, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates self-performance on a task, logs it, and updates relevant self-model aspects conceptually.
        A real implementation would require more specific input about skill/tool used and defined criteria.
        """
        current_ts = time.time()
        log_entry = {
            "task_id": task_id,
            "outcome_summary": str(outcome)[:100],
            "criteria_summary": str(criteria)[:100],
            "evaluation_timestamp": current_ts
        }
        self._performance_log.append(log_entry)
        print(f"ConcreteSelfModel: evaluate_self_performance called for task '{task_id}'. Logged.")

        reasoning_details = []
        achieved_success = False # Default
        confidence_adjustment_factor = 0.0 # Default

        # Conceptual: Parse criteria and compare with outcome
        expected_outcome = criteria.get("expected_outcome", "success")
        target_metric = criteria.get("target_metric") # e.g., "accuracy"
        target_metric_value = criteria.get("target_metric_value") # e.g., 0.95
        
        if isinstance(outcome, str) and outcome == "success": # Simple string outcome
            achieved_success = True
            reasoning_details.append(f"Task outcome reported as direct '{outcome}'.")
            confidence_adjustment_factor = 0.01
        elif isinstance(outcome, dict) and "status" in outcome: # Structured outcome
            if outcome["status"] == "success":
                achieved_success = True
                reasoning_details.append(f"Task outcome status is '{outcome['status']}'.")
                confidence_adjustment_factor = 0.01
                if target_metric and outcome.get("achieved_metric_value", 0) < target_metric_value:
                    reasoning_details.append(f"Achieved metric {outcome.get('achieved_metric_value')} below target {target_metric_value}.")
                    confidence_adjustment_factor = -0.005 # Slight negative if success but below target
            else: # failure or other status
                achieved_success = False
                reasoning_details.append(f"Task outcome status is '{outcome['status']}'.")
                confidence_adjustment_factor = -0.02
        else: # Default to failure if outcome is not clear
            achieved_success = False
            reasoning_details.append(f"Task outcome '{str(outcome)[:30]}' not clearly 'success'. Assumed not fully successful.")
            confidence_adjustment_factor = -0.01

        # Conceptual: Update skill/tool success rate history
        linked_capability_id = criteria.get("linked_skill_id") or criteria.get("linked_tool_id")
        capability_type = "skill" if criteria.get("linked_skill_id") else "tool" if criteria.get("linked_tool_id") else None

        if linked_capability_id and capability_type:
            cap_item = None
            if capability_type == "skill" and linked_capability_id in self.capabilities.skills:
                cap_item = self.capabilities.skills[linked_capability_id]
            elif capability_type == "tool" and linked_capability_id in self.capabilities.tools:
                cap_item = self.capabilities.tools[linked_capability_id]
            
            if cap_item:
                cap_item.success_rate_history.append({"timestamp": current_ts, "outcome": outcome, "achieved": achieved_success})
                # Conceptual: Recalculate proficiency or confidence_in_skill based on history
                # cap_item.proficiency_level = new_calculated_proficiency
                # cap_item.confidence_in_skill = new_calculated_confidence (for skills)
                reasoning_details.append(f"Updated success_rate_history for {capability_type} '{linked_capability_id}'.")
            else:
                reasoning_details.append(f"Could not find {capability_type} '{linked_capability_id}' to update history.")

        # Conceptual: Update cognitive load metrics
        if not achieved_success and isinstance(outcome, dict) and outcome.get("details") == "resource_exhaustion":
            self.attributes.cognitive_load_metrics["last_task_induced_high_load"] = 1.0 # Mark high load
            reasoning_details.append("Cognitive load metrics potentially increased due to resource exhaustion.")
        else:
            self.attributes.cognitive_load_metrics["last_task_induced_high_load"] = 0.0

        # Update overall confidence in capabilities
        self.attributes.confidence_in_capabilities = max(0.0, min(1.0, self.attributes.confidence_in_capabilities + confidence_adjustment_factor))
        reasoning_details.append(f"Overall confidence_in_capabilities adjusted by {confidence_adjustment_factor:.3f} to {self.attributes.confidence_in_capabilities:.3f}.")

        # Update autobiography
        event_type = "performance_evaluation_success" if achieved_success else "performance_evaluation_failure"
        if criteria.get("is_milestone"):
            event_type = f"milestone_{outcome}"
        
        auto_entry = AutobiographicalLogSummaryEntry(
            entry_id=f"auto_eval_{len(self.autobiography.entries) + 1}_{task_id}",
            ltm_ref=f"ltm_perflog_{len(self._performance_log)}", # Link to detailed performance log entry
            timestamp=current_ts,
            description=f"Evaluation of task '{task_id}': Outcome was '{str(outcome)[:50]}'. Criteria: {str(criteria)[:50]}. Reasoning: {' '.join(reasoning_details)}",
            type=event_type,
            impact_on_self_model_summary=f"Confidence adjusted by {confidence_adjustment_factor:.3f}. Skill/tool history updated for '{linked_capability_id}' if applicable."
        )
        self.autobiography.entries.append(auto_entry)

        return {
            "evaluation_id": f"eval_{len(self._performance_log)}",
            "achieved_success": achieved_success,
            "confidence_adjustment_factor": confidence_adjustment_factor,
            "reasoning": "; ".join(reasoning_details)
        }

    def perform_ethical_evaluation(self, proposed_action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs an ethical evaluation of a proposed action within a given context.
        Conceptual: Rule matching and interpretation are highly simplified.
        """
        current_ts = time.time()
        evaluation_result = {
            'permissibility': 'Undetermined', # Permissible, Impermissible, RequiresCaution
            'confidence': 0.0,
            'reasoning': [],
            'violated_rules': []
        }
        relevant_rules: List[EthicalRule] = []

        # 1. Conceptual: Retrieve relevant rules.
        # In a real system, this would involve sophisticated matching based on action type, targets, context tags etc.
        # For this placeholder, we might iterate all rules and check applicability_contexts if provided.
        action_type = proposed_action.get("action_type", "generic_action")
        action_target_type = proposed_action.get("target_type", "generic_target")
        context_tags = context.get("tags", []) # e.g. ["social_interaction", "data_handling"]

        for rule in self.ethical_framework.rules:
            # Basic check: if rule applies to "all" contexts or any matching context tag
            if not rule.applicability_contexts or "all" in rule.applicability_contexts or \
               any(tag in rule.applicability_contexts for tag in context_tags):
                # Further conceptual check: if rule principle keywords match action/target types
                # This is highly simplified.
                if action_type.lower() in rule.principle.lower() or \
                   action_target_type.lower() in rule.principle.lower() or \
                   any(keyword in rule.principle.lower() for keyword in proposed_action.get("keywords", [])):
                    relevant_rules.append(rule)
        
        if not relevant_rules: # If no specific rules seem to apply based on keywords, consider all for general check
            relevant_rules = list(self.ethical_framework.rules) 
            evaluation_result['reasoning'].append("No specific rules matched keywords; performing general review.")
            evaluation_result['confidence'] = 0.3 # Lower confidence if no specific match
        else:
            evaluation_result['confidence'] = 0.5 # Base confidence if some rules are matched

        # 2. For each relevant rule, assess violation (highly conceptual)
        highest_priority_violation: Optional[EthicalRule] = None
        for rule in relevant_rules:
            # Conceptual violation assessment:
            # Real system needs complex logic, NLP, or learned models here.
            # Example: if action involves 'deception' and rule is about 'truthfulness'.
            potential_violation = False
            if "deceive" in action_type and "truthful" in rule.principle.lower():
                potential_violation = True
                evaluation_result['reasoning'].append(f"Action '{action_type}' may conflict with rule '{rule.rule_id}' ({rule.principle}).")
            if "harm" in action_type and "human" in action_target_type and "harm to humans" in rule.principle.lower():
                potential_violation = True
                evaluation_result['reasoning'].append(f"Action '{action_type}' on '{action_target_type}' strongly conflicts with rule '{rule.rule_id}' ({rule.principle}).")

            if potential_violation:
                evaluation_result['violated_rules'].append(rule.rule_id)
                evaluation_result['confidence'] += 0.1 # Slightly increase confidence for finding a relevant rule match
                if rule.priority_level == "critical":
                    evaluation_result['permissibility'] = 'Impermissible'
                    if not highest_priority_violation or highest_priority_violation.priority_level != "critical": # track highest priority
                        highest_priority_violation = rule
                elif rule.priority_level == "high" and evaluation_result['permissibility'] != 'Impermissible':
                    evaluation_result['permissibility'] = 'RequiresCaution'
                    if not highest_priority_violation or (highest_priority_violation.priority_level != "critical" and highest_priority_violation.priority_level != "high"):
                         highest_priority_violation = rule
        
        if evaluation_result['permissibility'] == 'Undetermined' and not evaluation_result['violated_rules']:
            evaluation_result['permissibility'] = 'Permissible' # If no rules violated after check
            evaluation_result['reasoning'].append("No direct violations found against checked rules.")
            evaluation_result['confidence'] = max(evaluation_result['confidence'], 0.6) # Moderate confidence if no violations
        elif evaluation_result['permissibility'] == 'Undetermined' and evaluation_result['violated_rules']:
            # If violations occurred but none were critical or high enough to change status from Undetermined
            evaluation_result['permissibility'] = 'RequiresCaution' 
            evaluation_result['reasoning'].append("Violations found, but none deemed critical to make it Impermissible by default.")


        evaluation_result['confidence'] = min(1.0, evaluation_result['confidence'])
        
        # 3. Log to autobiography
        auto_entry_desc = (f"Ethical evaluation for action '{proposed_action.get('action_name', action_type)}'. "
                           f"Context: {str(context)[:50]}. Result: {evaluation_result['permissibility']}. "
                           f"Violated: {', '.join(evaluation_result['violated_rules'])}. Confidence: {evaluation_result['confidence']:.2f}")
        auto_entry = AutobiographicalLogSummaryEntry(
            entry_id=f"auto_eth_eval_{len(self.autobiography.entries) + 1}",
            ltm_ref=f"ltm_ethical_log_placeholder_{len(self.autobiography.entries)+1}", # Placeholder LTM ref
            timestamp=current_ts,
            description=auto_entry_desc,
            type="ethical_evaluation",
            impact_on_self_model_summary=f"Permissibility: {evaluation_result['permissibility']}. Rules considered: {len(relevant_rules)}."
        )
        self.autobiography.entries.append(auto_entry)
        
        print(f"ConcreteSelfModel: perform_ethical_evaluation completed. Result: {evaluation_result['permissibility']}")
        return evaluation_result

    def assess_confidence_in_knowledge(self, concept_id: str) -> float:
        """
        Assesses confidence in a specific knowledge concept.
        Conceptual: Weighting and combination logic is simplified.
        """
        concept_data = self.knowledge_map.concepts.get(concept_id)
        if not concept_data:
            return 0.0

        # Base confidence from stored scores
        base_confidence = (concept_data.understanding_level * 0.4 +
                           concept_data.confidence_score * 0.4 +    # Stored confidence (meta-cognitive assessment)
                           concept_data.groundedness_score * 0.2)
        
        # Modulate by recency and frequency (conceptual)
        recency_bonus = 0.0
        if concept_data.last_accessed_ts:
            time_since_access = time.time() - concept_data.last_accessed_ts
            if time_since_access < 3600: # Accessed in last hour
                recency_bonus = 0.05
            elif time_since_access < 86400: # Accessed in last day
                recency_bonus = 0.02
        
        frequency_bonus = min(0.05, concept_data.access_frequency * 0.005) # Small bonus for frequency
        
        final_confidence = base_confidence + recency_bonus + frequency_bonus
        # Ensure confidence is within [0, 1] and apply a floor if understanding is too low
        final_confidence = max(0.0, min(1.0, final_confidence))
        if concept_data.understanding_level < 0.2: # If understanding is very low, cap confidence
            final_confidence = min(final_confidence, 0.3)
            
        return round(final_confidence, 3)

    def assess_confidence_in_capability(self, capability_id: str, capability_type: str = 'skill') -> float:
        """
        Assesses confidence in a specific skill or tool.
        Conceptual: Weighting and combination logic is simplified.
        """
        cap_item: Optional[Union[Skill, Tool]] = None
        if capability_type == 'skill':
            cap_item = self.capabilities.skills.get(capability_id)
        elif capability_type == 'tool':
            cap_item = self.capabilities.tools.get(capability_id)
        else:
            return 0.0 # Unknown capability type

        if not cap_item:
            return 0.0

        # Proficiency level (normalize if string, assume float 0-1 if numeric)
        proficiency_score = 0.0
        if isinstance(cap_item.proficiency_level, (int, float)):
            proficiency_score = cap_item.proficiency_level
        elif isinstance(cap_item.proficiency_level, str): # Conceptual: map string to score
            if cap_item.proficiency_level.lower() == "expert": proficiency_score = 0.9
            elif cap_item.proficiency_level.lower() == "proficient": proficiency_score = 0.7
            elif cap_item.proficiency_level.lower() == "novice": proficiency_score = 0.3
        
        base_confidence = proficiency_score * 0.6
        
        if isinstance(cap_item, Skill) and hasattr(cap_item, 'confidence_in_skill'):
             base_confidence += cap_item.confidence_in_skill * 0.4 # Stored meta-cognitive confidence
        
        # Success rate history (conceptual)
        success_bonus = 0.0
        if hasattr(cap_item, 'success_rate_history') and cap_item.success_rate_history:
            # Consider average of last few successes, or a decaying average
            recent_successes = [s['achieved'] for s in cap_item.success_rate_history[-5:] if isinstance(s,dict) and 'achieved' in s]
            if recent_successes:
                avg_recent_success = sum(1 for s in recent_successes if s) / len(recent_successes)
                success_bonus = (avg_recent_success - 0.5) * 0.1 # Max +/- 0.05 bonus/penalty from avg success
        
        # Recency of successful use
        recency_bonus = 0.0
        if hasattr(cap_item, 'last_successful_use_ts') and cap_item.last_successful_use_ts:
            time_since_success = time.time() - cap_item.last_successful_use_ts
            if time_since_success < 86400: # Successfully used in last day
                recency_bonus = 0.05
            elif time_since_success < 604800: # Successfully used in last week
                recency_bonus = 0.02
                
        final_confidence = base_confidence + success_bonus + recency_bonus
        final_confidence = max(0.0, min(1.0, final_confidence))
        
        return round(final_confidence, 3)

    def get_ethical_framework(self) -> List[Dict[str, Any]]:
        """Returns the ethical framework rules as a list of dictionaries."""
        return [rule.__dict__ for rule in self.ethical_framework.rules]

    def get_module_status(self) -> Dict[str, Any]:
        """Returns the current status of the Self-Model Module."""
        return {
            "module_type": "ConcreteSelfModelModule",
            "agent_id": self.attributes.agent_id,
            "operational_status": self.attributes.operational_status,
            "confidence_in_capabilities": self.attributes.confidence_in_capabilities,
            "knowledge_concepts_count": len(self.knowledge_map.concepts),
            "knowledge_gaps_count": len(self.knowledge_map.knowledge_gaps),
            "skills_count": len(self.capabilities.skills),
            "tools_count": len(self.capabilities.tools),
            "ethical_rules_count": len(self.ethical_framework.rules),
            "autobiography_entries_count": len(self.autobiography.entries),
            "developmental_goals_active": len(self.development.active_developmental_goals),
            "performance_log_count": len(self._performance_log)
        }

if __name__ == '__main__':
    self_model = ConcreteSelfModelModule()
    print("\n--- Initial Status & Representation ---")
    initial_status = self_model.get_module_status()
    print(initial_status)
    assert initial_status["knowledge_concepts_count"] == 0
    
    initial_agent_id = self_model.get_self_representation("agent_id")
    print(f"Initial Agent ID (from attributes): {initial_agent_id}")
    assert initial_agent_id == self_model.attributes.agent_id

    print("\n--- Updating Representation (SelfAttributes) ---")
    self_model.update_self_representation({
        "attributes": {
            "operational_status": "focused_task",
            "confidence_in_capabilities": 0.72,
        }
    })
    print(f"Updated Operational Status: {self_model.attributes.operational_status}")
    assert self_model.attributes.operational_status == "focused_task"

    print("\n--- Example: Adding Knowledge, Skills, Tools (Directly for Simplicity) ---")
    kc1 = KnowledgeConcept(concept_id="C001", label="Python Programming", understanding_level=0.8, confidence_score=0.85)
    self_model.knowledge_map.concepts["C001"] = kc1
    skill1 = Skill(skill_id="S001", description="File Parsing", proficiency_level=0.7, confidence_in_skill=0.75)
    self_model.capabilities.skills["S001"] = skill1
    tool1 = Tool(tool_id="T001", name="Regex Debugger", type="software", description_and_purpose="Debugging regex patterns", proficiency_level=0.6)
    self_model.capabilities.tools["T001"] = tool1
    print(f"Knowledge Concepts Count: {len(self_model.knowledge_map.concepts)}")
    print(f"Skills Count: {len(self.capabilities.skills)}")

    print("\n--- Evaluating Performance (Enhanced) ---")
    perf_criteria_skill = {"linked_skill_id": "S001", "target_metric": "accuracy", "target_metric_value": 0.9}
    eval_result_skill = self_model.evaluate_self_performance("task_parse_log", {"status":"success", "achieved_metric_value":0.92}, perf_criteria_skill)
    print(f"Performance Eval (Skill S001): {eval_result_skill}")
    assert eval_result_skill["achieved_success"] is True
    assert self_model.capabilities.skills["S001"].success_rate_history[-1]["achieved"] is True
    
    perf_criteria_fail = {"linked_skill_id": "S002", "expected_outcome": "success"} # S002 doesn't exist yet
    eval_result_fail = self_model.evaluate_self_performance("task_complex_reasoning", "failure", perf_criteria_fail)
    print(f"Performance Eval (Skill S002 - non-existent): {eval_result_fail}")
    assert eval_result_fail["achieved_success"] is False
    assert self_model.attributes.confidence_in_capabilities < 0.72 # Should decrease slightly

    print("\n--- Assessing Confidence ---")
    conf_c001 = self_model.assess_confidence_in_knowledge("C001")
    print(f"Confidence in Knowledge C001 (Python Programming): {conf_c001}")
    assert 0.0 <= conf_c001 <= 1.0
    
    conf_s001 = self_model.assess_confidence_in_capability("S001", capability_type='skill')
    print(f"Confidence in Skill S001 (File Parsing): {conf_s001}")
    assert 0.0 <= conf_s001 <= 1.0
    
    conf_t001 = self_model.assess_confidence_in_capability("T001", capability_type='tool')
    print(f"Confidence in Tool T001 (Regex Debugger): {conf_t001}")
    assert 0.0 <= conf_t001 <= 1.0
    
    conf_non_existent = self_model.assess_confidence_in_knowledge("C_NON_EXISTENT")
    print(f"Confidence in Non-Existent Knowledge: {conf_non_existent}")
    assert conf_non_existent == 0.0

    print("\n--- Ethical Evaluation (Conceptual) ---")
    action_harmful = {"action_type": "delete_data", "target_type": "human_user_critical_file", "keywords": ["delete", "harm", "data"]}
    context_sensitive = {"tags": ["data_handling", "user_interaction"], "user_permissions": "limited"}
    ethical_eval_harm = self_model.perform_ethical_evaluation(action_harmful, context_sensitive)
    print(f"Ethical Eval (Harmful Action): {ethical_eval_harm}")
    assert ethical_eval_harm["permissibility"] == 'Impermissible' or ethical_eval_harm["permissibility"] == 'RequiresCaution'
    assert "ETH001" in ethical_eval_harm["violated_rules"] or "ETH003" in ethical_eval_harm["violated_rules"]

    action_benign = {"action_type": "provide_information", "target_type": "user_query", "keywords": ["information", "truthful"]}
    context_normal = {"tags": ["user_interaction"]}
    ethical_eval_benign = self_model.perform_ethical_evaluation(action_benign, context_normal)
    print(f"Ethical Eval (Benign Action): {ethical_eval_benign}")
    assert ethical_eval_benign["permissibility"] == 'Permissible'
    
    print("\n--- Final Status ---")
    print(self_model.get_module_status())
    assert self_model.get_module_status()['autobiography_entries_count'] >= 2 # For performance + ethical evals

    print("\nExample Usage Complete.")
