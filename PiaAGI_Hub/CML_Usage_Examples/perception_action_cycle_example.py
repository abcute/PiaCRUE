import sys
import os

# Adjust path to import from PiaAGI_Hub (assuming this script is in PiaAGI_Hub/CML_Usage_Examples/)
# This allows importing PiaCML modules.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PiaCML.concrete_perception_module import ConcretePerceptionModule
from PiaCML.concrete_world_model import ConcreteWorldModel
from PiaCML.concrete_working_memory_module import ConcreteWorkingMemoryModule
from PiaCML.concrete_motivational_system_module import ConcreteMotivationalSystemModule
from PiaCML.concrete_planning_decision_making_module import ConcretePlanningAndDecisionMakingModule
from PiaCML.concrete_behavior_generation_module import ConcreteBehaviorGenerationModule
from PiaCML.concrete_communication_module import ConcreteCommunicationModule # For final formatting

def print_header(title):
    print(f"\n{'='*10} {title} {'='*10}")

def main():
    print_header("Initializing CML Modules for Perception-Action Cycle Example")

    # 1. Initialize all required modules
    perception = ConcretePerceptionModule()
    world_model = ConcreteWorldModel()
    # For WM, let's give it a small capacity for this example
    working_memory = ConcreteWorkingMemoryModule(capacity=5)
    motivation = ConcreteMotivationalSystemModule()
    planning_pdm = ConcretePlanningAndDecisionMakingModule() # Renamed to avoid conflict
    behavior_gen = ConcreteBehaviorGenerationModule()
    communication = ConcreteCommunicationModule() # For formatting output

    print("\n--- Initial Module Statuses ---")
    print("Perception Status:", perception.get_module_status())
    print("World Model Status:", world_model.get_module_status())
    print("Working Memory Status:", working_memory.get_module_status())
    print("Motivation Status:", motivation.get_module_status())
    print("Planning Status:", planning_pdm.get_module_status())
    print("Behavior Gen Status:", behavior_gen.get_module_status())
    print("Communication Status:", communication.get_module_status())

    # 2. Define a goal
    print_header("Defining Goal")
    goal_desc = "simple_greet" # This template exists in ConcretePlanningAndDecisionMakingModule
    goal_id = motivation.manage_goals(action="add", goal_data={
        "description": goal_desc,
        "type": "extrinsic",
        "priority": 0.9,
        "status": "active" # Set it as active immediately
    })
    print(f"Added Goal ID: {goal_id} - {goal_desc}")
    print("Motivation Status:", motivation.get_module_status())

    # 3. Simulate a perception event (e.g., user says something that isn't directly relevant to the goal, to show focus)
    print_header("Simulating Perception Event")
    raw_user_input = "I see a red apple."
    # Pass world_model to perception module
    percept = perception.process_sensory_input(raw_user_input, "text", world_model=world_model)
    print("Generated Percept:", percept)
    print("World Model Status (after perception):", world_model.get_module_status())

    # 4. Add percept to Working Memory
    print_header("Updating Working Memory with Percept")
    # The content of the percept itself is the information for WM
    wm_item_id = working_memory.add_item_to_workspace(item_content=percept, salience=0.8, context={"source": "perception"})
    print(f"Added percept to WM with ID: {wm_item_id}")
    print("Working Memory Status:", working_memory.get_module_status())

    # 5. Retrieve active goal(s)
    print_header("Retrieving Active Goal")
    active_goals = motivation.get_active_goals(N=1) # Get the top active goal
    if not active_goals:
        print("No active goals. Ending example.")
        return
    current_goal = active_goals[0]
    print("Current Active Goal:", current_goal)

    # 6. Create a plan for the goal
    # Planning module's create_plan expects world_model_context and self_model_context (dictionaries)
    # We'll pass empty dicts for now, or basic info from our WM/WorldModel instances.
    print_header("Creating Plan")
    # Conceptual: world_model_context could be a summary from world_model.get_module_status() or specific queries
    # Conceptual: self_model_context would come from a SelfModel instance
    wm_contents_summary = working_memory.get_workspace_contents() # Simple context from WM
    world_model_summary_for_plan = {"entities_tracked": world_model.get_module_status()['entities_tracked']}

    plans = planning_pdm.create_plan(
        goal=current_goal,
        world_model_context=world_model_summary_for_plan, # Pass summary
        self_model_context={"capabilities": ["basic_communication"]} # Mock self-model
    )
    if not plans:
        print("No plans created. Ending example.")
        return
    plan_to_evaluate = plans[0] # Take the first plan generated
    print("Plan to Evaluate:", plan_to_evaluate)

    # 7. Evaluate the plan
    print_header("Evaluating Plan")
    # Pass the actual world_model instance to evaluate_plan
    plan_evaluation = planning_pdm.evaluate_plan(
        plan=plan_to_evaluate,
        world_model_context=world_model_summary_for_plan, # Still pass context dict
        self_model_context={"ethical_flags_raised": []}, # Mock
        world_model_instance=world_model # Pass instance
    )
    print("Plan Evaluation:", plan_evaluation)

    # 8. Select the plan (in this case, we only have one evaluation)
    print_header("Selecting Plan")
    selected_plan_eval = planning_pdm.select_action_or_plan([plan_evaluation])
    if not selected_plan_eval:
        print("No plan selected. Ending example.")
        return
    print("Selected Plan (Evaluation):", selected_plan_eval)

    # The selected_plan_eval contains the plan_id. We need the actual plan steps.
    # In our current PDM, the create_plan returns the full plan structure.
    # And select_action_or_plan returns the evaluation, which includes the plan_id.
    # We need to find the original plan structure.
    # For this example, plan_to_evaluate is the structure.

    final_plan_steps = plan_to_evaluate.get("steps")
    if not final_plan_steps:
        print("Selected plan has no steps. Ending example.")
        return

    # 9. Generate Behavior for the first step of the plan (assuming it's a communication action)
    # A real agent would loop through steps or have more complex execution logic.
    print_header("Generating Behavior for First Plan Step")
    first_step_action = final_plan_steps[0]
    print("First step to execute:", first_step_action)

    # This step is an abstract action, e.g., {"action_type": "communicate", "final_message_content": "Hello!"}
    # BehaviorGenerationModule takes this abstract action.
    # If the action is "communicate", it might pass it to CommunicationModule to get concrete content,
    # or CommunicationModule might have already prepared 'final_message_content'.
    # Our ConcretePlanningAndDecisionMakingModule's "simple_greet" template directly puts
    # "final_message_content" in the step.

    behavior_spec = behavior_gen.generate_behavior(first_step_action, context={"goal_id": current_goal['id']})
    print("Generated Behavior Specification:", behavior_spec)

    # 10. (Optional) Format linguistic output using CommunicationModule if behavior is linguistic
    if behavior_spec.get("behavior_type") == "linguistic_output":
        print_header("Formatting Linguistic Output (Conceptual)")
        # The ConcreteBehaviorGenerationModule already created the final string.
        # A more complex setup might have BehaviorGen output an abstract message spec,
        # and CommModule would then take that to do final NLG with nuance.
        # Here, we just print what BehaviorGen made.
        final_output_content = behavior_spec.get("details", {}).get("content")
        print(f"Final Output (from Behavior Gen): {final_output_content}")

        # If we wanted CommModule to do more, the flow would be:
        # PDM -> abstract_message_spec (e.g. {'intent': 'greet'})
        # CommModule.generate_outgoing(abstract_message_spec) -> formatted_message_dict
        # BehaviorGen.generate_behavior(formatted_message_dict) -> behavior_spec_for_actuator
        # For this example, the "simple_greet" plan from PDM is already quite concrete.

    print_header("Example Cycle Complete")

if __name__ == "__main__":
    main()
