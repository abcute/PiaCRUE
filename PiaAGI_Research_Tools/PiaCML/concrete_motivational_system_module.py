from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import time
import uuid # For module_id generation

try:
    from .base_motivational_system_module import BaseMotivationalSystemModule
    from .message_bus import MessageBus
    from .core_messages import GenericMessage, GoalUpdatePayload, ActionEventPayload # Added ActionEventPayload
except ImportError:
    print("Warning: Running ConcreteMotivationalSystemModule with stubbed imports.")
    class BaseMotivationalSystemModule:
        def manage_goals(self, action: str, goal_data: Optional[Dict[str, Any]] = None) -> Any: pass
        def get_active_goals(self, N: int = 0, min_priority: float = 0.0) -> List[Dict[str, Any]]: return []
        def update_motivation_state(self, new_state_info: Dict[str, Any]) -> bool: return False

    try:
        from message_bus import MessageBus # type: ignore
        from core_messages import GenericMessage, GoalUpdatePayload, ActionEventPayload # type: ignore
    except ImportError:
        MessageBus = None # type: ignore
        GenericMessage = object # type: ignore # So isinstance checks don't fail immediately
        GoalUpdatePayload = object # type: ignore
        ActionEventPayload = object # type: ignore


@dataclass
class Goal:
    id: str
    description: str
    type: str  # e.g., "EXTRINSIC_TASK", "INTRINSIC_CURIOSITY", "INTRINSIC_COMPETENCE"
    priority: float  # Higher values mean higher priority
    status: str  # e.g., "PENDING", "ACTIVE", "ACHIEVED", "FAILED", "BLOCKED"
    creation_timestamp: float = field(default_factory=time.time)
    source_trigger: Optional[Dict[str, Any]] = None # Describes what triggered the goal
    parent_id: Optional[str] = None
    # sub_goals: List[str] = field(default_factory=list) # Example for future extension

class ConcreteMotivationalSystemModule(BaseMotivationalSystemModule):
    """
    A concrete implementation of the BaseMotivationalSystemModule using a structured Goal dataclass.
    Manages a list of goals and includes basic mechanisms for intrinsic motivation (curiosity).
    Can publish GoalUpdate messages to a MessageBus and react to ActionEvents.
    """

    def __init__(self,
                 message_bus: Optional[MessageBus] = None,
                 module_id: str = f"ConcreteMotivationalSystemModule_{str(uuid.uuid4())[:8]}"):
        """
        Initializes the ConcreteMotivationalSystemModule.

        Args:
            message_bus: An optional instance of MessageBus for publishing goal updates
                         and receiving action events.
            module_id: A unique identifier for this module instance.
        """
        self.goals: List[Goal] = []
        self.next_goal_id: int = 0
        self._message_bus = message_bus
        self._module_id = module_id
        bus_status = "configured" if self._message_bus else "not configured"
        print(f"ConcreteMotivationalSystemModule '{self._module_id}' initialized. Message bus {bus_status}.")

        if self._message_bus:
            self._message_bus.subscribe(
                module_id=self._module_id,
                message_type="ActionEvent",
                callback=self._handle_action_event
            )
            print(f"INFO ({self._module_id}): Subscribed to 'ActionEvent' messages.")

    def _generate_goal_id(self) -> str:
        """Generates a unique goal ID."""
        gid = f"goal_{self.next_goal_id}"
        self.next_goal_id += 1
        return gid

    def add_goal(self, description: str, goal_type: str, initial_priority: float,
                 source_trigger: Optional[Dict[str, Any]] = None,
                 parent_id: Optional[str] = None,
                 initial_status: str = "PENDING") -> str:
        """
        Adds a new goal to the system.

        Args:
            description: Textual description of the goal.
            goal_type: Type of goal (e.g., "EXTRINSIC_TASK", "INTRINSIC_CURIOSITY").
            initial_priority: Priority score (higher is more important).
            source_trigger: Optional dictionary describing what triggered the goal.
            parent_id: Optional ID of a parent goal.
            initial_status: Initial status of the goal, defaults to "PENDING".

        Returns:
            The ID of the newly created goal.
        """
        new_id = self._generate_goal_id()
        new_goal = Goal(
            id=new_id,
            description=description,
            type=goal_type,
            priority=initial_priority,
            status=initial_status,
            source_trigger=source_trigger,
            parent_id=parent_id
        )
        self.goals.append(new_goal)
        print(f"ConcreteMotSys ({self._module_id}): Added goal '{new_id}': {description} (Priority: {initial_priority}, Status: {new_goal.status})")

        if self._message_bus and GenericMessage and GoalUpdatePayload: # Check types to satisfy linter if fallback occurs
            payload = GoalUpdatePayload(
                goal_id=new_goal.id,
                goal_description=new_goal.description,
                priority=new_goal.priority,
                status=new_goal.status,
                originator=new_goal.source_trigger.get("originator", new_goal.type) if new_goal.source_trigger else new_goal.type,
                criteria_for_completion=getattr(new_goal, 'criteria_for_completion', None),
                associated_rewards_penalties=getattr(new_goal, 'associated_rewards_penalties', None),
                deadline=getattr(new_goal, 'deadline', None),
                parent_goal_id=new_goal.parent_id
            )
            goal_update_message = GenericMessage(
                source_module_id=self._module_id,
                message_type="GoalUpdate",
                payload=payload
            )
            self._message_bus.publish(goal_update_message)
            print(f"ConcreteMotSys ({self._module_id}): Published GoalUpdate for new goal '{new_id}'.")

        return new_id

    def get_goal(self, goal_id: str) -> Optional[Goal]:
        """Retrieves a goal by its ID."""
        for goal in self.goals:
            if goal.id == goal_id:
                return goal
        return None

    def update_goal_status(self, goal_id: str, new_status: str) -> bool:
        """Updates the status of an existing goal."""
        goal = self.get_goal(goal_id)
        if goal:
            old_status = goal.status
            goal.status = new_status
            print(f"ConcreteMotSys ({self._module_id}): Updated status of goal '{goal_id}' from '{old_status}' to '{new_status}'.")

            if self._message_bus and GenericMessage and GoalUpdatePayload:
                payload = GoalUpdatePayload(
                    goal_id=goal.id,
                    goal_description=goal.description,
                    priority=goal.priority,
                    status=goal.status,
                    originator=goal.source_trigger.get("originator", goal.type) if goal.source_trigger else goal.type,
                    criteria_for_completion=getattr(goal, 'criteria_for_completion', None),
                    associated_rewards_penalties=getattr(goal, 'associated_rewards_penalties', None),
                    deadline=getattr(goal, 'deadline', None),
                    parent_goal_id=goal.parent_id
                )
                goal_update_message = GenericMessage(
                    source_module_id=self._module_id,
                    message_type="GoalUpdate",
                    payload=payload
                )
                self._message_bus.publish(goal_update_message)
                print(f"ConcreteMotSys ({self._module_id}): Published GoalUpdate for status change of goal '{goal_id}'.")
            return True
        print(f"ConcreteMotSys ({self._module_id}): Goal '{goal_id}' not found for status update.")
        return False

    def update_goal_priority(self, goal_id: str, new_priority: float) -> bool:
        """Updates the priority of an existing goal and publishes an update."""
        goal = self.get_goal(goal_id)
        if goal:
            old_priority = goal.priority
            goal.priority = new_priority
            print(f"ConcreteMotSys ({self._module_id}): Updated priority of goal '{goal_id}' from {old_priority:.2f} to {new_priority:.2f}.")

            if self._message_bus and GenericMessage and GoalUpdatePayload:
                payload = GoalUpdatePayload(
                    goal_id=goal.id,
                    goal_description=goal.description,
                    priority=goal.priority,
                    status=goal.status,
                    originator=goal.source_trigger.get("originator", goal.type) if goal.source_trigger else goal.type,
                    criteria_for_completion=getattr(goal, 'criteria_for_completion', None),
                    associated_rewards_penalties=getattr(goal, 'associated_rewards_penalties', None),
                    deadline=getattr(goal, 'deadline', None),
                    parent_goal_id=goal.parent_id
                )
                goal_update_message = GenericMessage(
                    source_module_id=self._module_id,
                    message_type="GoalUpdate",
                    payload=payload
                )
                self._message_bus.publish(goal_update_message)
                print(f"ConcreteMotSys ({self._module_id}): Published GoalUpdate for priority change of goal '{goal_id}'.")
            return True
        print(f"ConcreteMotSys ({self._module_id}): Goal '{goal_id}' not found for priority update.")
        return False

    def get_active_goals(self) -> List[Goal]:
        """
        Returns a list of goals with status "PENDING" or "ACTIVE",
        sorted by priority (descending).
        """
        active_statuses = {"PENDING", "ACTIVE"}
        # Filter for active statuses first
        relevant_goals = [g for g in self.goals if g.status in active_statuses]
        # Sort by priority, descending
        relevant_goals.sort(key=lambda g: g.priority, reverse=True)
        return relevant_goals

    def assess_curiosity_triggers(self,
                                 knowledge_map_snapshot: Optional[Dict[str, Dict[str, Any]]] = None,
                                 world_event: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Assesses potential curiosity triggers from knowledge gaps or novel world events
        and generates intrinsic curiosity goals.

        Args:
            knowledge_map_snapshot: Snapshot of knowledge concepts and their confidence.
                                    e.g., `{"concept_X": {"confidence": 0.3, "last_explored_ts": ...}}`
            world_event: A dictionary describing a novel event.
                         e.g., `{"type": "NOVEL_STIMULUS", "id": "obj_123", "novelty_score": 0.9}`

        Returns:
            A list of IDs of newly created curiosity goals.
        """
        new_curiosity_goal_ids: List[str] = []

        if world_event and world_event.get("type") == "NOVEL_STIMULUS":
            novelty_score = world_event.get("novelty_score", 0.0)
            if novelty_score > 0.7:
                event_id_desc = world_event.get('id', world_event.get('description', 'unknown stimulus'))
                priority = novelty_score * 10.0 # Scale novelty to priority (0-10 for example)
                goal_id = self.add_goal(
                    description=f"Investigate novel event: {event_id_desc}",
                    goal_type="INTRINSIC_CURIOSITY",
                    initial_priority=min(10.0, priority), # Cap priority if needed
                    source_trigger=world_event
                )
                new_curiosity_goal_ids.append(goal_id)
                print(f"ConcreteMotSys ({self._module_id}): Curiosity goal '{goal_id}' added for novel event '{event_id_desc}'.")

        if knowledge_map_snapshot:
            for concept_id, data in knowledge_map_snapshot.items():
                confidence = data.get("confidence", 1.0)
                if confidence < 0.5:
                    # Check if a similar curiosity goal already exists and is active/pending
                    # This is a simple check; more sophisticated checks might be needed.
                    existing_goal_for_concept = any(
                        g.type == "INTRINSIC_CURIOSITY" and
                        g.source_trigger and g.source_trigger.get("concept_id") == concept_id and
                        g.status in ["PENDING", "ACTIVE"]
                        for g in self.goals
                    )
                    if not existing_goal_for_concept:
                        priority = (1.0 - confidence) * 10.0 # Higher priority for lower confidence
                        trigger_info = {"type": "KNOWLEDGE_GAP", "concept_id": concept_id, "confidence": confidence}
                        goal_id = self.add_goal(
                            description=f"Resolve uncertainty for concept: {concept_id}",
                            goal_type="INTRINSIC_CURIOSITY",
                            initial_priority=min(10.0, priority),
                            source_trigger=trigger_info
                        )
                        new_curiosity_goal_ids.append(goal_id)
                        print(f"ConcreteMotSys ({self._module_id}): Curiosity goal '{goal_id}' added for knowledge gap on '{concept_id}'.")

        return new_curiosity_goal_ids

    def suggest_highest_priority_goal(self) -> Optional[Goal]:
        """
        Suggests the highest priority goal that is currently "PENDING" or "ACTIVE".
        """
        active_goals = self.get_active_goals()
        if active_goals:
            return active_goals[0]
        return None

    def get_module_status(self) -> Dict[str, Any]:
        """Returns the current status of the Motivational System Module."""
        status_counts: Dict[str, int] = {}
        for goal in self.goals:
            status_counts[goal.status] = status_counts.get(goal.status, 0) + 1

        return {
            "module_id": self._module_id,
            "module_type": "ConcreteMotivationalSystemModule (Message Bus Integrated)",
            "total_goals": len(self.goals),
            "goals_by_status": status_counts,
            "message_bus_configured": self._message_bus is not None,
            "next_goal_id_counter": self.next_goal_id
        }


    def _handle_action_event(self, message: GenericMessage) -> None:
        """
        Handles ActionEvent messages from the message bus.
        Updates goal status based on action outcomes.
        """
        if not isinstance(message.payload, ActionEventPayload):
            print(f"ERROR ({self._module_id}): Received non-ActionEventPayload: {type(message.payload)}")
            return

        payload: ActionEventPayload = message.payload
        print(f"INFO ({self._module_id}): Handling ActionEvent for command '{payload.action_command_id}', Action: '{payload.action_type}', Status: {payload.status}")

        goal_id_from_outcome: Optional[str] = None
        new_status_from_outcome: Optional[str] = None

        if payload.outcome:
            goal_id_from_outcome = payload.outcome.get("goal_id")
            new_status_from_outcome = payload.outcome.get("new_status") # e.g. "ACHIEVED", "FAILED"

            # Alternative/supplemental logic: map ActionEvent.status to goal status
            if goal_id_from_outcome and not new_status_from_outcome: # If goal_id present but no explicit new_status
                if payload.status == "SUCCESS":
                    new_status_from_outcome = "ACHIEVED"
                elif payload.status == "FAILURE":
                    new_status_from_outcome = "FAILED"
                # Add more mappings if needed e.g. IN_PROGRESS -> ACTIVE (if not already)

        if goal_id_from_outcome and new_status_from_outcome:
            goal = self.get_goal(goal_id_from_outcome)
            if goal:
                print(f"INFO ({self._module_id}): ActionEvent outcome suggests updating goal '{goal_id_from_outcome}' to status '{new_status_from_outcome}'.")
                self.update_goal_status(goal_id_from_outcome, new_status_from_outcome)
            else:
                print(f"WARNING ({self._module_id}): Goal '{goal_id_from_outcome}' from ActionEvent outcome not found.")
        else:
            print(f"INFO ({self._module_id}): No actionable goal update found in ActionEvent outcome for command '{payload.action_command_id}'. Outcome: {payload.outcome}")


    def update_motivation_state(self, new_state_info: Dict[str, Any]) -> bool:
        """
        Placeholder for updating broader motivation state (e.g., drive levels).
        """
        print(f"ConcreteMotSys ({self._module_id}): update_motivation_state called with: {new_state_info}. (Placeholder)")
        return True


if __name__ == '__main__':
    import asyncio

    # Ensure MessageBus and core_messages are available for __main__
    # This is primarily for direct execution of this file.
    if MessageBus is None or GenericMessage is None or GoalUpdatePayload is None or ActionEventPayload is None:
        print("CRITICAL: MessageBus or core_messages not loaded correctly for __main__ test. Exiting.")
        exit(1)

    print("\n--- ConcreteMotivationalSystemModule __main__ Test ---")

    received_goal_updates: List[GenericMessage] = []
    def goal_update_listener(message: GenericMessage):
        print(f"\n goal_update_listener: Received GoalUpdate! ID: {message.message_id[:8]}")
        if isinstance(message.payload, GoalUpdatePayload):
            payload: GoalUpdatePayload = message.payload
            print(f"  Source: {message.source_module_id}")
            print(f"  Goal ID: {payload.goal_id}, Desc: '{payload.goal_description[:30]}...'")
            print(f"  Status: {payload.status}, Priority: {payload.priority:.2f}")
            print(f"  Originator: {payload.originator}")
            received_goal_updates.append(message)
        else:
            print(f"  ERROR: Listener received non-GoalUpdatePayload: {type(message.payload)}")


    async def main_test_flow():
        bus = MessageBus()
        module_id_for_test = "MotSysTest01"
        mot_sys = ConcreteMotivationalSystemModule(message_bus=bus, module_id=module_id_for_test)

        bus.subscribe(
            module_id="TestGoalListener",
            message_type="GoalUpdate",
            callback=goal_update_listener
        )
        print("\nTestGoalListener subscribed to GoalUpdate messages.")

        print("\n--- Initial Status ---")
        print(mot_sys.get_module_status())

        # --- Test Publishing on goal modifications ---
        print("\n--- Adding Goals (should publish GoalUpdates) ---")
        received_goal_updates.clear()
        g1_id = mot_sys.add_goal("Explore dataset Alpha", "INTRINSIC_CURIOSITY", 7.5, {"trigger": "new_data_signal", "originator": "CuriositySubsystem"})
        await asyncio.sleep(0.01) # Allow bus to process if async
        assert len(received_goal_updates) == 1, "GoalUpdate for add_goal (g1) not received"
        assert received_goal_updates[0].payload.goal_id == g1_id
        assert received_goal_updates[0].payload.status == "PENDING"
        assert received_goal_updates[0].source_module_id == module_id_for_test

        g2_id = mot_sys.add_goal("Process user request #123", "EXTRINSIC_TASK", 9.0, {"user_id": "user_x", "originator": "UserInteractionModule"})
        await asyncio.sleep(0.01)
        assert len(received_goal_updates) == 2, "GoalUpdate for add_goal (g2) not received"
        assert received_goal_updates[1].payload.goal_id == g2_id
        assert received_goal_updates[1].payload.originator == "UserInteractionModule"


        print("\n--- Updating Goal Status (should publish GoalUpdate) ---")
        received_goal_updates.clear()
        mot_sys.update_goal_status(g1_id, "ACTIVE")
        await asyncio.sleep(0.01)
        assert len(received_goal_updates) == 1, "GoalUpdate for status change not received"
        assert received_goal_updates[0].payload.goal_id == g1_id
        assert received_goal_updates[0].payload.status == "ACTIVE"

        print("\n--- Updating Goal Priority (should publish GoalUpdate) ---")
        received_goal_updates.clear()
        mot_sys.update_goal_priority(g2_id, 9.5)
        await asyncio.sleep(0.01)
        assert len(received_goal_updates) == 1, "GoalUpdate for priority change not received"
        assert received_goal_updates[0].payload.goal_id == g2_id
        assert received_goal_updates[0].payload.priority == 9.5


        # --- Test Subscribing to ActionEvent ---
        print("\n--- Simulating ActionEvent (goal success) ---")
        # Ensure g1 is in a state that can be achieved (e.g. ACTIVE)
        if mot_sys.get_goal(g1_id).status != "ACTIVE":
            mot_sys.update_goal_status(g1_id, "ACTIVE") # This will publish one update
            await asyncio.sleep(0.01) # let it publish
            received_goal_updates.clear() # Clear this update before testing the ActionEvent trigger

        action_event_success_payload = ActionEventPayload(
            action_command_id="cmd_abc_123",
            action_type="EXPLORE_DATASET",
            status="SUCCESS",
            outcome={"goal_id": g1_id, "new_status": "ACHIEVED", "details": "Exploration complete, insights found."}
        )
        action_event_msg_success = GenericMessage(
            source_module_id="ActionExecutorModule",
            message_type="ActionEvent",
            payload=action_event_success_payload
        )
        bus.publish(action_event_msg_success)
        await asyncio.sleep(0.01) # Allow _handle_action_event and subsequent publish

        assert len(received_goal_updates) > 0, "GoalUpdate not received after ActionEvent (SUCCESS)"
        if received_goal_updates: # Check the last message
            last_update = received_goal_updates[-1].payload
            assert last_update.goal_id == g1_id
            assert last_update.status == "ACHIEVED"
            print(f"  Listener correctly received GoalUpdate for '{g1_id}' status '{last_update.status}' triggered by ActionEvent.")


        print("\n--- Simulating ActionEvent (goal failure from outcome) ---")
        received_goal_updates.clear()
        # Ensure g2 is in a state that can be failed
        if mot_sys.get_goal(g2_id).status != "ACTIVE":
             mot_sys.update_goal_status(g2_id, "ACTIVE")
             await asyncio.sleep(0.01)
             received_goal_updates.clear()

        action_event_failure_payload = ActionEventPayload(
            action_command_id="cmd_def_456",
            action_type="PROCESS_USER_REQUEST",
            status="FAILURE", # Main status is failure
            outcome={"goal_id": g2_id, "new_status": "FAILED", "reason": "Resource unavailable"} # Specific new status in outcome
        )
        action_event_msg_failure = GenericMessage(
            source_module_id="ActionExecutorModule",
            message_type="ActionEvent",
            payload=action_event_failure_payload
        )
        bus.publish(action_event_msg_failure)
        await asyncio.sleep(0.01)

        assert len(received_goal_updates) > 0, "GoalUpdate not received after ActionEvent (FAILURE from outcome)"
        if received_goal_updates:
            last_update_fail = received_goal_updates[-1].payload
            assert last_update_fail.goal_id == g2_id
            assert last_update_fail.status == "FAILED"
            print(f"  Listener correctly received GoalUpdate for '{g2_id}' status '{last_update_fail.status}' triggered by ActionEvent.")


        print("\n--- Simulating ActionEvent (goal failure from status, no new_status in outcome) ---")
        g3_id = mot_sys.add_goal("Perform risky operation", "EXTRINSIC_TASK", 8.0, initial_status="ACTIVE")
        await asyncio.sleep(0.01)
        received_goal_updates.clear()

        action_event_failure_status_payload = ActionEventPayload(
            action_command_id="cmd_ghi_789",
            action_type="RISKY_OPERATION",
            status="FAILURE", # Main status implies goal failure
            outcome={"goal_id": g3_id, "reason": "Operation timed out"} # NO new_status in outcome
        )
        action_event_msg_failure_status = GenericMessage(
            source_module_id="ActionExecutorModule",
            message_type="ActionEvent",
            payload=action_event_failure_status_payload
        )
        bus.publish(action_event_msg_failure_status)
        await asyncio.sleep(0.01)

        assert len(received_goal_updates) > 0, "GoalUpdate not received after ActionEvent (FAILURE from status)"
        if received_goal_updates:
            last_update_fail_status = received_goal_updates[-1].payload
            assert last_update_fail_status.goal_id == g3_id
            assert last_update_fail_status.status == "FAILED" # Should map ActionEvent.status="FAILURE" to Goal.status="FAILED"
            print(f"  Listener correctly received GoalUpdate for '{g3_id}' status '{last_update_fail_status.status}' triggered by ActionEvent status.")


        print("\n--- Final Module Status ---")
        print(mot_sys.get_module_status())
        assert mot_sys.get_goal(g1_id).status == "ACHIEVED"
        assert mot_sys.get_goal(g2_id).status == "FAILED"
        assert mot_sys.get_goal(g3_id).status == "FAILED"

        print("\n--- ConcreteMotivationalSystemModule __main__ Test Complete ---")

    try:
        asyncio.run(main_test_flow())
    except RuntimeError as e:
        if " asyncio.run() cannot be called from a running event loop" in str(e):
            print("Skipping asyncio.run() as an event loop is already running (e.g. in Jupyter/IPython).")
        else:
            raise

    # Old __main__ content for reference:
    # mot_sys = ConcreteMotivationalSystemModule()
    # print("\n--- Initial Status ---")
    # print(mot_sys.get_module_status())
    # print("\n--- Adding Goals ---")
    # g1_id = mot_sys.add_goal("Explore dataset Alpha", "INTRINSIC_CURIOSITY", 7.5, {"trigger": "new_data_signal"})
    # ... rest of old main commented or removed for brevity ...
    # print("\nExample Usage Complete (Phase 1 Enhanced Motivational System).")
