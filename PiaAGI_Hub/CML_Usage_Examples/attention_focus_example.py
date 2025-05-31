import sys
import os

# Adjust path to import from PiaAGI_Hub
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PiaCML.concrete_motivational_system_module import ConcreteMotivationalSystemModule
from PiaCML.concrete_attention_module import ConcreteAttentionModule
from PiaCML.concrete_working_memory_module import ConcreteWorkingMemoryModule
from PiaCML.concrete_perception_module import ConcretePerceptionModule # To generate mock percepts

def print_header(title):
    print(f"\n{'='*10} {title} {'='*10}")

def main():
    print_header("Initializing CML Modules for Attention Focus Example")

    motivation = ConcreteMotivationalSystemModule()
    attention = ConcreteAttentionModule()
    # Use a small WM capacity to see filtering effects more clearly
    working_memory = ConcreteWorkingMemoryModule(capacity=3)
    perception = ConcretePerceptionModule() # Used here to simulate incoming data stream

    print("\n--- Initial Module Statuses ---")
    print("Motivation Status:", motivation.get_module_status())
    print("Attention Status:", attention.get_module_status())
    print("Working Memory Status:", working_memory.get_module_status())

    # 1. Define a high-priority active goal
    print_header("Defining High-Priority Goal")
    goal_id = motivation.manage_goals(action="add", goal_data={
        "description": "Find information about 'Project Phoenix'",
        "type": "extrinsic",
        "priority": 0.9,
        "status": "active"
    })
    print(f"Added Goal ID: {goal_id} - Find information about 'Project Phoenix'")
    active_goals = motivation.get_active_goals(N=1)
    if not active_goals:
        print("Could not set active goal. Exiting.")
        return
    current_goal_desc = active_goals[0]['description'] # Will be used to direct attention

    # 2. Direct Attention based on the goal
    print_header("Directing Attention Based on Goal")
    # We'll use a keyword from the goal description as the focus target.
    # A more sophisticated system would extract entities or concepts.
    focus_target = "Project Phoenix"
    attention.direct_attention(focus_target=focus_target, priority=0.9, context={'source': 'motivation_goal'})
    print("Attention Status after directing:", attention.get_attentional_state())
    assert attention.get_attentional_state()['current_focus'] == focus_target

    # 3. Simulate a stream of perceived information
    print_header("Simulating Incoming Information Stream")
    # Use PerceptionModule to generate structured percepts for consistency
    raw_data_stream = [
        "News: Upcoming conference on AI ethics.",
        "Memo: All staff should read the Project Phoenix preliminary report.",
        "Email: Reminder about team lunch next Friday.",
        "Update: Project Phoenix timeline has been revised.",
        "Chat: Anyone see the game last night?",
        "Alert: System maintenance for Project Phoenix servers tonight."
    ]

    perceived_items = []
    for text_input in raw_data_stream:
        # For this example, we don't need to update a world model in perception
        percept = perception.process_sensory_input(text_input, "text", context={"source": "simulated_feed"})
        perceived_items.append(percept)
        print(f"  - Perceived: '{text_input}' -> Entities: {percept['processed_representation'].get('entities',[])}")

    # 4. Filter the perceived information using the Attention Module
    print_header("Filtering Information Stream via Attention Module")
    # The ConcreteAttentionModule's filter_information uses its internal _current_focus
    filtered_percepts = attention.filter_information(perceived_items)
    print(f"Attention module filtered {len(perceived_items)} items down to {len(filtered_percepts)} items.")
    for i, p_item in enumerate(filtered_percepts):
        print(f"  Filtered Item {i+1}: {p_item['raw_input']}")
    # Expected: Items containing "Project Phoenix" should pass the filter.

    # 5. Add filtered items to Working Memory
    print_header("Adding Filtered Items to Working Memory")
    for p_item in filtered_percepts:
        # Use a part of the raw input or a generated ID for content, and assign salience
        # Salience could also be influenced by the attention module or perception
        item_content = {"type": "filtered_percept", "original_raw": p_item['raw_input'], "details": p_item['processed_representation']}
        wm_id = working_memory.add_item_to_workspace(item_content, salience=0.8, context={"source": "attention_filtered"})
        if "error" in wm_id: # Check if WM is full
            print(f"  Could not add to WM (full?): {p_item['raw_input']}")
        else:
            print(f"  Added to WM (ID {wm_id}): {p_item['raw_input']}")

    print("\n--- Final Working Memory Status ---")
    print(working_memory.get_module_status())
    # Check contents to see which items made it through attention filter AND WM capacity.
    # Since WM capacity is 3, and we expect 3 "Project Phoenix" items, all should be there.
    wm_final_contents = working_memory.get_workspace_contents()
    phoenix_in_wm_count = 0
    for item in wm_final_contents:
        if "Project Phoenix" in item['content']['original_raw']:
            phoenix_in_wm_count+=1
    print(f"Count of 'Project Phoenix' related items in WM: {phoenix_in_wm_count}")
    assert phoenix_in_wm_count == 3 # Assuming all 3 Phoenix items passed filter and fit in WM

    # 6. Optionally, set focus in WM to one of the relevant items
    if wm_final_contents:
        # Let's try to focus on the first item that contains "Project Phoenix"
        focused_wm_item_id = None
        for item in wm_final_contents:
            if "Project Phoenix" in item['content']['original_raw']:
                focused_wm_item_id = item['id']
                break
        if focused_wm_item_id:
            print_header("Setting Active Focus in Working Memory")
            working_memory.set_active_focus(focused_wm_item_id)
            print("WM Status after setting focus:", working_memory.get_module_status())
            print("Focused WM Item:", working_memory.get_active_focus())


    print_header("Example Cycle Complete")

if __name__ == "__main__":
    main()
