from typing import Any, Dict, List, Optional
import uuid

try:
    from .base_planning_and_decision_making_module import BasePlanningAndDecisionMakingModule
    from .message_bus import MessageBus
    from .core_messages import GenericMessage, GoalUpdatePayload, ActionCommandPayload
    # Assuming Goal dataclass might be defined in motivational system or a shared types file
    # For this PoC, we'll work with GoalUpdatePayload which carries goal details.
    # If Goal object itself is needed, import path would need to be correct e.g.
    # from .concrete_motivational_system_module import Goal
except ImportError:
    from base_planning_and_decision_making_module import BasePlanningAndDecisionMakingModule
    try:
        from message_bus import MessageBus
        from core_messages import GenericMessage, GoalUpdatePayload, ActionCommandPayload
    except ImportError:
        MessageBus = None # type: ignore
        GenericMessage = None # type: ignore
        GoalUpdatePayload = None # type: ignore
        ActionCommandPayload = None # type: ignore

class ConcretePlanningAndDecisionMakingModule(BasePlanningAndDecisionMakingModule):
    """
    A concrete implementation of the BasePlanningAndDecisionMakingModule.
    This version can subscribe to GoalUpdate messages and publish ActionCommand messages.
    Planning logic is conceptual for this Proof-of-Concept.
    """

    def __init__(self, message_bus: Optional[MessageBus] = None):
        """
        Initializes the ConcretePlanningAndDecisionMakingModule.

        Args:
            message_bus: An optional instance of MessageBus for communication.
        """
        self._plan_templates: Dict[str, List[Dict[str, Any]]] = { # Kept for conceptual planning
            "achieve_goal_A": [{"action_type": "step1_for_A"}, {"action_type": "step2_for_A"}],
            "simple_greet": [{"action_type": "communicate", "parameters": {"message": "Hello!"}}]
        }
        self.message_bus = message_bus
        self.pending_goals: List[GoalUpdatePayload] = [] # Stores received GoalUpdatePayloads

        bus_status_msg = "not configured"
        if self.message_bus:
            if GenericMessage and GoalUpdatePayload: # Check if imports were successful
                try:
                    self.message_bus.subscribe(
                        module_id="ConcretePlanningAndDecisionMakingModule_01", # Example ID
                        message_type="GoalUpdate",
                        callback=self.handle_goal_update_message
                    )
                    bus_status_msg = "configured and subscribed to GoalUpdate"
                except Exception as e:
                    bus_status_msg = f"configured but FAILED to subscribe to GoalUpdate: {e}"
            else:
                bus_status_msg = "configured but core message types for subscription not available"

        print(f"ConcretePlanningAndDecisionMakingModule initialized. Message bus {bus_status_msg}.")

    def handle_goal_update_message(self, message: GenericMessage):
        """Handles GoalUpdate messages received from the message bus."""
        if GoalUpdatePayload and isinstance(message.payload, GoalUpdatePayload):
            payload: GoalUpdatePayload = message.payload
            # print(f"Planner received GoalUpdate: {payload.goal_id}, status: {payload.status}") # Optional

            if payload.status in ["new", "active", "updated", "PENDING", "ACTIVE"]: # Accept common active/new statuses
                # Remove existing goal with same ID to replace with updated info or avoid duplicate processing
                self.pending_goals = [g for g in self.pending_goals if g.goal_id != payload.goal_id]

                self.pending_goals.append(payload)
                # Keep sorted by priority (highest first)
                self.pending_goals.sort(key=lambda g: g.priority, reverse=True)
                # print(f"Planner: Goal '{payload.goal_id}' added/updated in pending_goals. Count: {len(self.pending_goals)}")
            elif payload.status in ["achieved", "failed", "BLOCKED", "paused"]:
                # If a goal is no longer active, remove it from pending goals
                removed_count = len(self.pending_goals)
                self.pending_goals = [g for g in self.pending_goals if g.goal_id != payload.goal_id]
                removed_count -= len(self.pending_goals)
                # if removed_count > 0:
                #     print(f"Planner: Goal '{payload.goal_id}' removed from pending_goals due to status '{payload.status}'.")
        else:
            print(f"Planner received GoalUpdate with unexpected payload type: {type(message.payload)}")

    def develop_and_dispatch_plan(self, goal_payload: GoalUpdatePayload) -> bool:
        """
        Conceptual: Develops a simple plan for the given goal and publishes ActionCommands.
        For PoC, it creates 1-2 conceptual ActionCommandPayloads based on goal description.
        """
        if not self.message_bus or not GenericMessage or not ActionCommandPayload:
            print("Warning: Planner has no message bus or core message types. Cannot dispatch plan.")
            return False

        print(f"Planner: Developing plan for goal '{goal_payload.goal_id}': {goal_payload.goal_description}")

        # Conceptual Plan Generation (example)
        action_payloads: List[ActionCommandPayload] = []
        if "greet" in goal_payload.goal_description.lower():
            action_payloads.append(ActionCommandPayload(
                action_type="linguistic_output",
                parameters={"message": f"Hello! This is a plan for '{goal_payload.goal_description}'."},
                priority=goal_payload.priority
            ))
        else:
            action_payloads.append(ActionCommandPayload(
                action_type="conceptual_step",
                parameters={"task": f"Step 1 for {goal_payload.goal_description}", "goal_id": goal_payload.goal_id},
                priority=goal_payload.priority,
                expected_outcome_summary="Complete step 1 of the plan."
            ))
            if goal_payload.priority > 0.7: # Add a second step for high priority goals
                 action_payloads.append(ActionCommandPayload(
                    action_type="conceptual_step",
                    parameters={"task": f"Step 2 for {goal_payload.goal_description}", "goal_id": goal_payload.goal_id},
                    priority=goal_payload.priority - 0.1, # Slightly lower priority for subsequent step
                    expected_outcome_summary="Complete step 2 of the plan."
                ))

        if not action_payloads:
            print(f"Planner: No actions generated for goal '{goal_payload.goal_id}'.")
            return False

        for ac_payload in action_payloads:
            action_message = GenericMessage(
                source_module_id="ConcretePlanningAndDecisionMakingModule_01", # Example ID
                message_type="ActionCommand",
                payload=ac_payload
            )
            self.message_bus.publish(action_message)
            print(f"Planner: Published ActionCommand '{ac_payload.action_type}' for goal '{goal_payload.goal_id}'. CMD_ID: {ac_payload.command_id}")

        # For PoC, mark goal as "planned" or remove from pending.
        # Here, we'll assume it's removed by process_one_pending_goal.
        # If called directly, the caller should handle its status or removal from a list.
        return True

    def process_one_pending_goal(self) -> bool:
        """
        Processes the highest priority pending goal by developing and dispatching a plan.
        Returns True if a goal was processed, False otherwise.
        """
        if not self.pending_goals:
            # print("Planner: No pending goals to process.") # Optional
            return False

        highest_priority_goal_payload = self.pending_goals.pop(0) # Get and remove from list
        print(f"Planner: Processing highest priority pending goal '{highest_priority_goal_payload.goal_id}'.")

        # Mark as "ACTIVE" or similar before planning, and publish this status update
        # For this PoC, we directly proceed to develop_and_dispatch_plan
        # A more robust implementation would update the goal's status in the MotivationalSystem
        # via a GoalStatusUpdateRequest message or similar, or the SMM might do this.

        return self.develop_and_dispatch_plan(highest_priority_goal_payload)

    # --- Existing conceptual methods (can be kept or adapted/removed later) ---
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
        # For this basic version, let's assume the caller has the original plan if they only got evaluations.
        # Or, more practically, the input `evaluated_plans` should contain enough info.
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
