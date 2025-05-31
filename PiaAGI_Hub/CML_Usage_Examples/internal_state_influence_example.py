import sys
import os

# Adjust path to import from PiaAGI_Hub
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PiaCML.concrete_emotion_module import ConcreteEmotionModule
from PiaCML.concrete_self_model_module import ConcreteSelfModelModule
from PiaCML.concrete_motivational_system_module import ConcreteMotivationalSystemModule
from PiaCML.concrete_working_memory_module import ConcreteWorkingMemoryModule

def print_header(title):
    print(f"\n{'='*10} {title} {'='*10}")

def main():
    print_header("Initializing CML Modules for Internal State Influence Example")

    emotion_module = ConcreteEmotionModule(initial_vad_state=(0.0, 0.2, 0.0)) # Neutral-ish, slightly alert
    self_model = ConcreteSelfModelModule()
    motivation_module = ConcreteMotivationalSystemModule()
    working_memory = ConcreteWorkingMemoryModule(capacity=5)

    print("\n--- Initial Module Statuses ---")
    print("Emotion Status:", emotion_module.get_module_status())
    print("Self Model Status:", self_model.get_module_status())
    print("Motivation Status:", motivation_module.get_module_status())

    # 1. Simulate an event that should cause a negative emotion (e.g., task failure feedback)
    print_header("Simulating a Negative Event (Task Failure)")
    failure_event = {"type": "goal_status", "goal_id": "g_alpha", "goal_status": "failed", "event_intensity": 0.8}
    # Add to WM to simulate it being processed before appraisal
    wm_id_failure = working_memory.add_item_to_workspace(failure_event, salience=0.9)

    # Appraise the situation
    appraisal_result = emotion_module.appraise_situation(failure_event, context={"source": "performance_monitor"})
    current_emotion = emotion_module.get_current_emotion()
    print("Appraisal Result:", appraisal_result)
    print("Current Emotion after failure:", current_emotion)
    # Expected: Negative valence, increased arousal (e.g., sadness, frustration, fear)

    # 2. Simulate Self-Model evaluating this failure
    print_header("Self-Model Evaluating Performance")
    # In a real system, outcome might be more complex. Here, just using the emotion as part of context.
    performance_outcome = "failure"
    eval_criteria = {"task_difficulty": "medium", "expected_outcome": "success"}
    self_eval = self_model.evaluate_self_performance(
        task_id="g_alpha_attempt_1",
        outcome=performance_outcome,
        criteria=eval_criteria
    )
    # Conceptual: Update self-representation based on failure
    self_model.update_self_representation({"confidence_in_capabilities": 0.55}) # Decrease confidence
    print("Self-Model performance evaluation log entry ID:", self_eval.get("evaluation_id"))
    print("Self-Model confidence updated:", self_model.get_self_representation("confidence_in_capabilities"))

    # 3. This negative emotion and lower confidence might influence motivation
    # For example, it might reduce drive for similar tasks or trigger a new goal.
    print_header("Motivation System Reacting to Internal State")

    # Let's define some initial goals
    goal1_id = motivation_module.manage_goals(action="add", goal_data={
        "description": "Attempt complex task X", "type": "intrinsic_competence",
        "priority": 0.8, "status": "pending"
    })
    goal2_id = motivation_module.manage_goals(action="add", goal_data={
        "description": "Perform routine maintenance", "type": "extrinsic_duty",
        "priority": 0.6, "status": "pending"
    })
    print("Initial goals:", motivation_module.manage_goals(action="list_all"))

    # Conceptual: A "Central Executive" or the Motivational System itself might now
    # re-evaluate goal priorities based on current emotion and self-model state.
    # For this example, let's simulate the Motivational System doing this.

    # Get current internal states
    current_emotion_state = emotion_module.get_current_emotion()
    current_self_confidence = self_model.get_self_representation("confidence_in_capabilities")

    # Simple rule: if emotion is negative and confidence is low, de-prioritize challenging intrinsic goals
    # and maybe add a new goal to "recover" or "analyze_failure".
    if current_emotion_state['vad_state']['valence'] < -0.3 and current_self_confidence < 0.6:
        print("Detected negative emotion and low confidence. Adjusting goals...")

        # De-prioritize "Attempt complex task X"
        # To do this, we need to find it, update its priority, and re-sort.
        # This is a bit complex for the current manage_goals, which takes ID.
        # A more advanced manage_goals could take a query.
        # For now, let's assume we know goal1_id and update it.
        if goal1_id:
            original_goal1 = next((g for g in motivation_module.manage_goals(action="list_all") if g['id'] == goal1_id), None)
            if original_goal1:
                updated_priority = original_goal1['priority'] * 0.5 # Halve priority
                motivation_module.manage_goals(action="update_goal_fields", goal_data={ # Hypothetical action
                                                 "id": goal1_id,
                                                 "priority": updated_priority,
                                                 "details": {"reason_for_deprioritization": "low_confidence_negative_emotion"}
                                             })
                # Note: concrete_motivational_system_module needs 'update_goal_fields' or similar
                # For now, this part is conceptual as `manage_goals` doesn't support field update.
                # Let's simulate by removing and re-adding with lower priority if it were active
                if original_goal1['status'] == 'active' or original_goal1['status'] == 'pending':
                    motivation_module.manage_goals(action="remove", goal_data={"id": goal1_id})
                    goal1_id_new = motivation_module.manage_goals(action="add", goal_data={
                        "description": original_goal1['description'],
                        "type": original_goal1['type'],
                        "priority": updated_priority, # Lowered priority
                        "status": "paused", # Pause it
                        "source": original_goal1['source'],
                        "details": {"reason_for_priority_change": "low_confidence_after_failure"}
                    })
                    print(f"Goal '{original_goal1['description']}' re-prioritized (new ID {goal1_id_new}) and paused.")


        # Add a new goal: "Analyze recent failure"
        analysis_goal_id = motivation_module.manage_goals(action="add", goal_data={
            "description": f"Analyze failure of task g_alpha",
            "type": "intrinsic_learning",
            "priority": 0.85, # Make this fairly high
            "status": "active", # Activate immediately
            "source": "self_model_reflection"
        })
        print(f"Added new goal: {analysis_goal_id} - Analyze failure")

    print("\n--- Final Motivation Status & Goals ---")
    print(motivation_module.get_module_status())
    print("All goals:", motivation_module.manage_goals(action="list_all"))
    active_goals = motivation_module.get_active_goals()
    print("Active goals:")
    for g in active_goals: print(f"  - {g['id']}: {g['description']} (Priority: {g['priority']})")
    # Expected: "Analyze recent failure" should be the top active goal.

    print_header("Example Cycle Complete")

if __name__ == "__main__":
    main()
