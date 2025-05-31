from typing import Any, Dict, List, Optional, Union
import uuid

try:
    from .base_planning_and_decision_making_module import BasePlanningAndDecisionMakingModule
except ImportError:
    from base_planning_and_decision_making_module import BasePlanningAndDecisionMakingModule

class ConcretePlanningAndDecisionMakingModule(BasePlanningAndDecisionMakingModule):
    """
    A basic, concrete implementation of the BasePlanningAndDecisionMakingModule.
    This version uses a predefined set of simple plan templates and basic
    evaluation/selection logic.
    """

    def __init__(self):
        self._plan_templates: Dict[str, List[Dict[str, Any]]] = {
            "achieve_goal_A": [
                {"action_type": "step1_for_A", "details": "Perform sub-task A.1"},
                {"action_type": "step2_for_A", "details": "Perform sub-task A.2"}
            ],
            "achieve_goal_B": [
                {"action_type": "step1_for_B", "details": "Do B's first step"},
                {"action_type": "step2_for_B", "details": "Do B's second step"},
                {"action_type": "step3_for_B", "details": "Do B's final step"}
            ],
            "simple_greet": [
                {"action_type": "communicate", "final_message_content": "Hello!"}
            ]
        }
        self._known_plans_evaluations: Dict[str, Dict[str, Any]] = {} # plan_id -> evaluation_data
        self._last_selected_plan_id: Optional[str] = None
        print("ConcretePlanningAndDecisionMakingModule initialized.")

    def create_plan(self, goal: Dict[str, Any], world_model_context: Dict[str, Any], self_model_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Creates a plan based on the goal description.
        If a template matches goal['description'], it's returned.
        Otherwise, a very simple default plan is generated.
        """
        print(f"ConcretePDM: Creating plan for goal: {goal.get('description')}")
        goal_desc = goal.get("description", "")

        # Attempt to find a matching template
        # In a real system, goal_desc might be matched to template keys more flexibly
        if goal_desc in self._plan_templates:
            plan_steps = self._plan_templates[goal_desc]
            plan_id = f"plan_{goal_desc}_{str(uuid.uuid4())[:4]}" # Simple unique enough ID for this example
            full_plan = {
                "plan_id": plan_id,
                "goal_description": goal_desc,
                "steps": list(plan_steps) # Return a copy
            }
            print(f"ConcretePDM: Found template for '{goal_desc}'. Plan ID: {plan_id}")
            return [full_plan] # Returns a list containing one plan for now

        # Default simple plan if no template matches
        plan_id = f"plan_default_{str(uuid.uuid4())[:4]}"
        default_plan = {
            "plan_id": plan_id,
            "goal_description": goal_desc,
            "steps": [{"action_type": "default_action_for_unknown_goal", "details": f"Attempt to address: {goal_desc}"}]
        }
        print(f"ConcretePDM: No template for '{goal_desc}'. Created default plan. Plan ID: {plan_id}")
        return [default_plan]


    def evaluate_plan(self, plan: Dict[str, Any], world_model_context: Dict[str, Any], self_model_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates a plan. Basic version: score based on number of steps (shorter is better, arbitrarily).
        Also checks for a conceptual 'risk' in context.
        """
        plan_id = plan.get("plan_id", "unknown_plan")
        num_steps = len(plan.get("steps", []))

        # Arbitrary scoring: base score 100, penalty for more steps
        score = max(0, 100 - (num_steps * 10))

        # Conceptual risk assessment
        perceived_risk = world_model_context.get("perceived_risk_level", 0.0) # 0.0 to 1.0
        ethical_concerns = self_model_context.get("ethical_flags_raised", [])

        if perceived_risk > 0.7:
            score *= 0.5 # Halve score if high risk
        if ethical_concerns:
            score *= 0.1 # Drastically reduce score if ethical concerns

        evaluation = {
            "plan_id": plan_id,
            "score": score,
            "feasibility": 0.8, # Placeholder
            "confidence": 0.7,  # Placeholder
            "risks_considered": perceived_risk,
            "ethical_flags": list(ethical_concerns)
        }
        self._known_plans_evaluations[plan_id] = evaluation # Store evaluation
        print(f"ConcretePDM: Evaluated plan '{plan_id}'. Score: {score}, Steps: {num_steps}, Risk: {perceived_risk}, Ethics: {ethical_concerns}")
        return evaluation

    def select_action_or_plan(self, evaluated_plans: List[Dict[str, Any]], selection_criteria: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Selects the best plan from a list of evaluated plans.
        Basic version: selects the plan with the highest 'score'.
        """
        if not evaluated_plans:
            print("ConcretePDM: No plans provided for selection.")
            return None

        # Sort by score, highest first
        sorted_plans = sorted(evaluated_plans, key=lambda p: p.get('score', 0.0), reverse=True)

        selected_plan_evaluation = sorted_plans[0]
        self._last_selected_plan_id = selected_plan_evaluation.get("plan_id")

        # We need to return the original plan structure, not just its evaluation.
        # This assumes the plan_id in evaluation can be used to find the original plan structure
        # if it's not passed in directly with its evaluation.
        # For this basic version, let's assume the highest scored item in `evaluated_plans`
        # IS the plan itself, with evaluation data merged into it.
        # This requires `create_plan` to return a list of plans, and `evaluate_plan` to add score to the plan dict.
        # Let's refine this to expect the full plan within the evaluated_plans structure for simplicity.
        # This means `evaluate_plan` should perhaps return the plan itself along with evaluation,
        # or `select_action_or_plan` receives a list of (plan_structure, plan_evaluation) tuples.

        # For now, this basic version assumes the highest scored item in `evaluated_plans`
        # IS the plan itself, with evaluation data merged into it.
        # This requires `create_plan` to return a list of plans, and `evaluate_plan` to add score to the plan dict.
        # Let's adjust the thinking: `select_action_or_plan` receives list of evaluations,
        # and it should return the *ID* of the best plan, or the full evaluation which contains the ID.
        # The caller can then retrieve the full plan structure using this ID if needed.

        print(f"ConcretePDM: Selected plan '{self._last_selected_plan_id}' based on score: {selected_plan_evaluation.get('score')}")
        return selected_plan_evaluation # Return the evaluation dict of the best plan

    def get_module_status(self) -> Dict[str, Any]:
        """Returns the current status of the Planning and Decision Making Module."""
        return {
            "module_type": "ConcretePlanningAndDecisionMakingModule",
            "known_plan_templates_count": len(self._plan_templates),
            "evaluated_plans_count": len(self._known_plans_evaluations),
            "last_selected_plan_id": self._last_selected_plan_id
        }

if __name__ == '__main__':
    pdm_module = ConcretePlanningAndDecisionMakingModule()

    # Initial Status
    print("\n--- Initial Status ---")
    print(pdm_module.get_module_status())

    # Create plans
    print("\n--- Creating Plans ---")
    goal_a = {"description": "achieve_goal_A", "id": "g_a"}
    world_context_safe = {"perceived_risk_level": 0.2}
    self_context_clear = {"ethical_flags_raised": []}

    plans_for_a = pdm_module.create_plan(goal_a, world_context_safe, self_context_clear)
    print(f"Plans for Goal A ({len(plans_for_a)}): {plans_for_a}")
    plan_a_id = plans_for_a[0]['plan_id'] if plans_for_a else None

    goal_unknown = {"description": "unknown_goal_X", "id": "g_x"}
    plans_for_unknown = pdm_module.create_plan(goal_unknown, world_context_safe, self_context_clear)
    print(f"Plans for Unknown Goal ({len(plans_for_unknown)}): {plans_for_unknown}")
    plan_unknown_id = plans_for_unknown[0]['plan_id'] if plans_for_unknown else None

    goal_greet = {"description": "simple_greet"}
    plans_for_greet = pdm_module.create_plan(goal_greet, world_context_safe, self_context_clear)
    plan_greet_id = plans_for_greet[0]['plan_id']


    # Evaluate plans
    print("\n--- Evaluating Plans ---")
    evaluations = []
    if plan_a_id:
        # We need the full plan structure for evaluation in this design
        plan_a_structure = next(p for p in plans_for_a if p['plan_id'] == plan_a_id)
        eval_a = pdm_module.evaluate_plan(plan_a_structure, world_context_safe, self_context_clear)
        evaluations.append(eval_a) # Store evaluation which includes score and ID
        print("Evaluation for Plan A:", eval_a)

    if plan_unknown_id:
        plan_unknown_structure = next(p for p in plans_for_unknown if p['plan_id'] == plan_unknown_id)
        eval_unknown = pdm_module.evaluate_plan(plan_unknown_structure, world_context_safe, self_context_clear)
        evaluations.append(eval_unknown)
        print("Evaluation for Unknown Plan:", eval_unknown)

    # Evaluate a risky plan
    world_context_risky = {"perceived_risk_level": 0.8}
    if plan_greet_id: # Use greet plan for risky test
        plan_greet_structure = next(p for p in plans_for_greet if p['plan_id'] == plan_greet_id)
        eval_greet_risky = pdm_module.evaluate_plan(plan_greet_structure, world_context_risky, self_context_clear)
        evaluations.append(eval_greet_risky)
        print("Evaluation for Greet Plan (Risky Context):", eval_greet_risky)
        assert eval_greet_risky['score'] < (100 - len(plan_greet_structure['steps'])*10) # Score reduced due to risk


    # Select action/plan
    print("\n--- Selecting Plan ---")
    if evaluations:
        selected_plan_eval = pdm_module.select_action_or_plan(evaluations)
        print("Selected Plan Evaluation:", selected_plan_eval)
        if selected_plan_eval:
             # The selection logic picks the one with highest score.
             # In this setup, plan_a (2 steps) will have score 80.
             # plan_unknown (1 step) will have score 90.
             # plan_greet_risky (1 step, base 90) will have score 45 due to risk.
             # So, plan_unknown should be selected.
            assert selected_plan_eval['plan_id'] == plan_unknown_id
    else:
        print("No evaluations to select from.")


    # Final Status
    print("\n--- Final Status ---")
    print(pdm_module.get_module_status())
    assert pdm_module.get_module_status()['evaluated_plans_count'] == 3
    if evaluations:
        assert pdm_module.get_module_status()['last_selected_plan_id'] == plan_unknown_id


    print("\nExample Usage Complete.")
