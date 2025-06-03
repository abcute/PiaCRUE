from typing import Dict, Any, Optional, List

from ..core_engine.interfaces import AgentInterface, PerceptionData, ActionCommand, ActionResult, PiaSEEvent, BaseDataModel

# Attempt to import actual CML modules
# These paths assume a specific structure for PiaCML. Adjust if necessary.
# For example, if PiaCML is a sibling directory or installed package:
# from PiaCML.concrete_perception_module import ConcretePerceptionModule
# from PiaCML.perception_module import PerceptionModule

try:
    # Concrete Implementations
    from PiaAGI_Research_Tools.PiaCML.concrete_perception_module import ConcretePerceptionModule
    from PiaAGI_Research_Tools.PiaCML.concrete_working_memory_module import ConcreteWorkingMemoryModule
    from PiaAGI_Research_Tools.PiaCML.concrete_long_term_memory_module import ConcreteLongTermMemoryModule
    from PiaAGI_Research_Tools.PiaCML.concrete_attention_module import ConcreteAttentionModule
    from PiaAGI_Research_Tools.PiaCML.concrete_learning_module import ConcreteLearningModule
    from PiaAGI_Research_Tools.PiaCML.concrete_motivational_system_module import ConcreteMotivationalSystemModule
    from PiaAGI_Research_Tools.PiaCML.concrete_emotion_module import ConcreteEmotionModule
    from PiaAGI_Research_Tools.PiaCML.concrete_planning_decision_making_module import ConcretePlanningAndDecisionMakingModule
    from PiaAGI_Research_Tools.PiaCML.concrete_behavior_generation_module import ConcreteBehaviorGenerationModule
    from PiaAGI_Research_Tools.PiaCML.concrete_self_model_module import ConcreteSelfModelModule
    from PiaAGI_Research_Tools.PiaCML.concrete_tom_module import ConcreteTheoryOfMindModule
    from PiaAGI_Research_Tools.PiaCML.concrete_communication_module import ConcreteCommunicationModule
    from PiaAGI_Research_Tools.PiaCML.concrete_world_model import ConcreteWorldModel

    # Base Interfaces for Type Hinting
    from PiaAGI_Research_Tools.PiaCML.perception_module import PerceptionModule
    from PiaAGI_Research_Tools.PiaCML.working_memory_module import WorkingMemoryModule
    from PiaAGI_Research_Tools.PiaCML.long_term_memory_module import LongTermMemoryModule
    from PiaAGI_Research_Tools.PiaCML.attention_module import AttentionModule
    from PiaAGI_Research_Tools.PiaCML.base_learning_module import BaseLearningModule
    from PiaAGI_Research_Tools.PiaCML.motivational_system_module import MotivationalSystemModule
    from PiaAGI_Research_Tools.PiaCML.emotion_module import EmotionModule
    from PiaAGI_Research_Tools.PiaCML.planning_decision_making_module import PlanningAndDecisionMakingModule
    from PiaAGI_Research_Tools.PiaCML.behavior_generation_module import BehaviorGenerationModule
    from PiaAGI_Research_Tools.PiaCML.self_model_module import SelfModelModule
    from PiaAGI_Research_Tools.PiaCML.tom_module import TheoryOfMindModule
    from PiaAGI_Research_Tools.PiaCML.communication_module import CommunicationModule
    from PiaAGI_Research_Tools.PiaCML.base_world_model import BaseWorldModel
    CML_PLACEHOLDERS_USED = False
except ImportError as e:
    print(f"PiaAGIAgent: Error importing CML modules: {e}. Using placeholders. Ensure PiaCML is structured correctly or in PYTHONPATH.")
    CML_PLACEHOLDERS_USED = True

    class PlaceholderModule(BaseDataModel): # Inherit from BaseDataModel for Pydantic compatibility if needed
        config: Optional[Dict] = None
        agent_id: Optional[str] = None
        # Allow arbitrary additional keyword arguments for flexibility with different module signatures
        def __init__(self, config: Optional[Dict] = None, agent_id: Optional[str] = None, **kwargs):
            super().__init__() # Pydantic requires calling super's init
            self.config = config
            self.agent_id = agent_id
            self._kwargs = kwargs # Store other args
            # print(f"Placeholder {self.__class__.__name__} initialized with config: {config}, agent_id: {agent_id}, other_args: {kwargs}")

        def process_sensory_input(self, data: Any, **kwargs) -> Any: print(f"Placeholder {self.__class__.__name__} processing sensory input {data}"); return {"processed_percepts": "placeholder_data"}
        def update_from_perception(self, data: Any, **kwargs): print(f"Placeholder {self.__class__.__name__} updating from perception {data}")
        def update_workspace(self, **kwargs): print(f"Placeholder {self.__class__.__name__} updating workspace with {kwargs}")
        def process_event(self, data: Any, **kwargs): print(f"Placeholder {self.__class__.__name__} processing event {data}")
        def direct_attention(self, data: Any, **kwargs): print(f"Placeholder {self.__class__.__name__} directing attention to {data}")
        def get_active_goals(self, **kwargs) -> List: print(f"Placeholder {self.__class__.__name__} getting active goals"); return [{"goal_id": "placeholder_goal"}]
        def get_current_state(self, **kwargs) -> Dict: print(f"Placeholder {self.__class__.__name__} getting current_state"); return {"emotion": "neutral_placeholder"}
        def get_snapshot(self, **kwargs) -> Dict: print(f"Placeholder {self.__class__.__name__} getting snapshot"); return {"wm_snapshot": "placeholder_data"}
        def get_current_snapshot(self, **kwargs) -> Dict: print(f"Placeholder {self.__class__.__name__} getting_current_snapshot for world model"); return {"world_state": "placeholder_world"}
        def get_guidance(self, **kwargs) -> Dict: print(f"Placeholder {self.__class__.__name__} getting guidance"); return {"self_model_guidance": "placeholder_guidance"}
        def plan_for_goals(self, **kwargs) -> Any: print(f"Placeholder {self.__class__.__name__} planning for goals {kwargs}"); return {"action_primitive": "placeholder_action"}
        def translate_to_env_action(self, data: Any, **kwargs) -> ActionCommand: print(f"Placeholder {self.__class__.__name__} translating to env action {data}"); return ActionCommand(action_type="placeholder_wait", parameters={})
        def process_feedback(self, data: Any, **kwargs): print(f"Placeholder {self.__class__.__name__} processing feedback {data}")
        def update_from_experience(self, data: Any, **kwargs): print(f"Placeholder {self.__class__.__name__} updating from experience {data}")
        def update_model(self, data: Any, **kwargs): print(f"Placeholder {self.__class__.__name__} updating model with {data}")
        def appraise_outcome(self, data: Any, **kwargs): print(f"Placeholder {self.__class__.__name__} appraising outcome {data}")
        def update_goal_status_from_feedback(self, data: Any, **kwargs): print(f"Placeholder {self.__class__.__name__} updating goal status from feedback {data}")
        def get_salient_info(self, **kwargs) -> Dict: print(f"Placeholder {self.__class__.__name__} getting salient info"); return {"salient_info": "placeholder"}
        def set_ltm_reference(self, ltm_ref: Any): print(f"Placeholder {self.__class__.__name__} setting LTM reference.")
        def set_perception_reference(self, perc_ref: Any): print(f"Placeholder {self.__class__.__name__} setting Perception reference.")

        # Q-learning placeholders if learning module is a placeholder
        def initialize_q_table(self, state: Any, action_space: list): print(f"Placeholder {self.__class__.__name__} init_q_table")
        def get_q_value(self, state: Any, action: Any) -> float: print(f"Placeholder {self.__class__.__name__} get_q_value"); return 0.0
        def update_q_value(self, state: Any, action: Any, reward: float, next_state: Any, learning_rate: float, discount_factor: float, action_space: list): print(f"Placeholder {self.__class__.__name__} update_q_value")


    ConcretePerceptionModule = PerceptionModule = PlaceholderModule
    ConcreteWorkingMemoryModule = WorkingMemoryModule = PlaceholderModule
    ConcreteLongTermMemoryModule = LongTermMemoryModule = PlaceholderModule
    ConcreteAttentionModule = AttentionModule = PlaceholderModule
    ConcreteLearningModule = BaseLearningModule = PlaceholderModule
    ConcreteMotivationalSystemModule = MotivationalSystemModule = PlaceholderModule
    ConcreteEmotionModule = EmotionModule = PlaceholderModule
    ConcretePlanningAndDecisionMakingModule = PlanningAndDecisionMakingModule = PlaceholderModule
    ConcreteBehaviorGenerationModule = BehaviorGenerationModule = PlaceholderModule
    ConcreteSelfModelModule = SelfModelModule = PlaceholderModule
    ConcreteTheoryOfMindModule = TheoryOfMindModule = PlaceholderModule
    ConcreteCommunicationModule = CommunicationModule = PlaceholderModule
    ConcreteWorldModel = BaseWorldModel = PlaceholderModule


class PiaAGIAgent(AgentInterface):
    def __init__(self, agent_id: str, cml_module_configs: Optional[Dict[str, Optional[Dict]]] = None, shared_world_model: Optional[BaseWorldModel] = None):
        self.agent_id = agent_id
        self.cml_configs = cml_module_configs if cml_module_configs else {}

        # Instantiate CML modules based on config or use defaults
        wm_config = self.cml_configs.get("world_model")
        self.world_model: BaseWorldModel = shared_world_model if shared_world_model else ConcreteWorldModel(config=wm_config, agent_id=self.agent_id)

        # Pass references to other modules as needed during construction
        # This simplifies setup compared to many post-init connection calls.
        self.perception_module: PerceptionModule = ConcretePerceptionModule(config=self.cml_configs.get("perception"), agent_id=self.agent_id, world_model=self.world_model)
        self.working_memory: WorkingMemoryModule = ConcreteWorkingMemoryModule(config=self.cml_configs.get("working_memory"), agent_id=self.agent_id) # CE is part of WM
        self.ltm: LongTermMemoryModule = ConcreteLongTermMemoryModule(config=self.cml_configs.get("ltm"), agent_id=self.agent_id)
        self.attention_module: AttentionModule = ConcreteAttentionModule(config=self.cml_configs.get("attention"), agent_id=self.agent_id, working_memory=self.working_memory)
        self.learning_module: BaseLearningModule = ConcreteLearningModule(config=self.cml_configs.get("learning"), agent_id=self.agent_id, world_model=self.world_model, ltm=self.ltm)
        self.motivation_module: MotivationalSystemModule = ConcreteMotivationalSystemModule(config=self.cml_configs.get("motivation"), agent_id=self.agent_id, world_model=self.world_model)
        self.emotion_module: EmotionModule = ConcreteEmotionModule(config=self.cml_configs.get("emotion"), agent_id=self.agent_id)
        self.planning_module: PlanningAndDecisionMakingModule = ConcretePlanningAndDecisionMakingModule(
            config=self.cml_configs.get("planning"),
            agent_id=self.agent_id,
            world_model=self.world_model,
            ltm=self.ltm,
            working_memory=self.working_memory,
            motivation_module=self.motivation_module,
            emotion_module=self.emotion_module,
            self_model=None # self.self_model is not yet initialized
        )
        self.behavior_generation: BehaviorGenerationModule = ConcreteBehaviorGenerationModule(config=self.cml_configs.get("behavior_generation"), agent_id=self.agent_id)
        self.self_model: SelfModelModule = ConcreteSelfModelModule(config=self.cml_configs.get("self_model"), agent_id=self.agent_id)
        # Now update planning_module with self_model if it has a setter or re-init if truly needed (less ideal)
        if hasattr(self.planning_module, 'set_self_model_reference'):
            self.planning_module.set_self_model_reference(self.self_model)

        self.tom_module: TheoryOfMindModule = ConcreteTheoryOfMindModule(config=self.cml_configs.get("tom"), agent_id=self.agent_id, world_model=self.world_model)
        self.communication_module: CommunicationModule = ConcreteCommunicationModule(config=self.cml_configs.get("communication"), agent_id=self.agent_id, working_memory=self.working_memory, ltm=self.ltm)

        # Establish inter-module connections (simplified, more robust is via constructor injection)
        if hasattr(self.working_memory, 'set_ltm_reference') and self.ltm is not None:
            self.working_memory.set_ltm_reference(self.ltm)
        if hasattr(self.working_memory, 'set_perception_reference') and self.perception_module is not None:
            self.working_memory.set_perception_reference(self.perception_module)
        # Consider that Central Executive (CE) functions are partly in WM, partly orchestrated by PiaAGIAgent's methods.

        self.q_table: Dict[Any, Dict[Any, float]] = {} # For AgentInterface compatibility

        if CML_PLACEHOLDERS_USED:
             print("PiaAGIAgent initialized using one or more PLACEHOLDER CML modules due to import errors.")
        else:
             print("PiaAGIAgent initialized with successfully imported CML modules.")


    def set_id(self, agent_id: str):
        self.agent_id = agent_id
        # Update agent_id in modules if necessary
        for module_name in ["perception_module", "working_memory", "ltm", "attention_module",
                       "learning_module", "motivation_module", "emotion_module",
                       "planning_module", "behavior_generation", "self_model",
                       "tom_module", "communication_module", "world_model"]:
            module = getattr(self, module_name, None)
            if module and hasattr(module, 'agent_id'):
                module.agent_id = agent_id
            if module and hasattr(module, 'set_agent_id'): # If they have a setter
                module.set_agent_id(agent_id)


    def get_id(self) -> str:
        return self.agent_id

    def perceive(self, observation: PerceptionData, event: Optional[PiaSEEvent] = None):
        # 1. Route observation to PerceptionModule
        # Assuming process_sensory_input is the primary method in PerceptionModule
        structured_percepts = self.perception_module.process_sensory_input(observation)

        # 2. Update World Model with structured percepts from PerceptionModule
        # Assuming update_from_perception is the method to call in WorldModel
        self.world_model.update_from_perception(structured_percepts)

        # 3. Update Working Memory (which includes Central Executive functions)
        # WM integrates percepts, LTM context (retrieved based on percepts), emotional state, goals for current awareness
        current_goals = self.motivation_module.get_active_goals()
        current_emotion_state = self.emotion_module.get_current_state()

        # WM's update_workspace would be responsible for managing its internal state, potentially triggering LTM retrieval
        self.working_memory.update_workspace(
            percepts=structured_percepts,
            # ltm_context might be fetched by WM internally based on percepts, or passed if CE decides so.
            # retrieved_ltm_context=self.ltm.retrieve_relevant_context(structured_percepts),
            current_goals=current_goals,
            current_emotion=current_emotion_state
        )

        if event:
            # Handle specific PiaSEEvents, e.g., human feedback, direct commands
            # This could be routed to WM or a specific module like Learning or SelfModel
            self.working_memory.process_event(event)

        # Attention module might be invoked by WM/CE to focus on salient parts of WM or incoming percepts
        # The actual trigger for attention might come from within WM's update cycle.
        salient_information = self.working_memory.get_salient_info() # Or attention module decides this
        self.attention_module.direct_attention(salient_information)

    def act(self) -> ActionCommand:
        # Central Executive functions (orchestrated here and within WM) coordinate action selection:

        # 1. Retrieve necessary information for planning
        current_wm_snapshot = self.working_memory.get_snapshot() # Provides current conscious workspace
        active_goals = self.motivation_module.get_active_goals() # Current motivations/goals
        world_model_state = self.world_model.get_current_snapshot() # Current understanding of the world
        self_model_guidance = self.self_model.get_guidance() # Self-perceived capabilities, values, etc.

        # 2. Planning module formulates a plan or selects an action.
        # The planning module would internally query LTM, use heuristics, simulate outcomes, etc.
        selected_plan_or_action_primitive = self.planning_module.plan_for_goals(
            goals=active_goals,
            current_world_state=world_model_state,
            working_memory_context=current_wm_snapshot,
            self_model_guidance=self_model_guidance
            # Emotion state could also be passed if planning considers it:
            # current_emotion_state = self.emotion_module.get_current_state()
        )

        # 3. Behavior Generation translates the selected plan/action into an environment-specific ActionCommand
        if selected_plan_or_action_primitive:
            # If it's a high-level plan, BGM might take the first step or decompose further.
            # If it's already a concrete action primitive, BGM translates it to the ActionCommand format.
            action_command = self.behavior_generation.translate_to_env_action(selected_plan_or_action_primitive)
        else:
            # Default action if no plan is generated (e.g., wait, observe, explore by default)
            print(f"PiaAGIAgent {self.agent_id}: No specific plan generated, defaulting to 'wait'.")
            action_command = ActionCommand(action_type="wait", parameters={"duration": 1})

        # (Conceptual) Communication module might be involved if the action is communicative
        # For example, if plan_for_goals returns a "SPEAK" intent.
        # if hasattr(selected_plan_or_action_primitive, 'type') and selected_plan_or_action_primitive.type == "COMMUNICATE":
        #    action_command = self.communication_module.generate_utterance(selected_plan_or_action_primitive.content)

        return action_command

    def learn(self, feedback: ActionResult):
        # Feedback from the environment after an action is processed for learning and adaptation.

        # 1. Learning Module updates its internal models, policies, or knowledge.
        # It might need context from other modules (e.g., WM state when action was taken).
        self.learning_module.process_feedback(
            feedback=feedback,
            world_model_state=self.world_model.get_current_snapshot(), # State of the world when feedback received
            ltm_data_accessor=self.ltm # Learning module might query/update LTM
        )

        # 2. Self-Model updates based on performance, success/failure, or direct feedback.
        self.self_model.update_from_experience(feedback)

        # 3. World Model might be updated if the action's outcome revealed new information
        # not captured in the immediate next perception (e.g., "you opened the box and found it empty" - WM learns about box state).
        if feedback.details and feedback.details.get("world_model_update_info"):
             self.world_model.update_model(feedback.details["world_model_update_info"])

        # 4. Emotional state might be updated based on the outcome (appraisal).
        self.emotion_module.appraise_outcome(feedback)

        # 5. Motivational system might update goal status, priorities, or generate new goals.
        self.motivation_module.update_goal_status_from_feedback(feedback)

    # --- Q-learning specific methods (for AgentInterface compatibility) ---
    # These would typically delegate to the learning module if it implements Q-learning.

    def initialize_q_table(self, state: Any, action_space: list):
        if hasattr(self.learning_module, 'initialize_q_table'):
            self.learning_module.initialize_q_table(state, action_space)
        else:
            # Basic fallback for interface compliance if LearningModule is a placeholder or not Q-based
            s_tuple = self._to_hashable(state)
            if s_tuple not in self.q_table:
                self.q_table[s_tuple] = {self._to_hashable(a): 0.0 for a in action_space}

    def get_q_value(self, state: Any, action: Any) -> float:
        if hasattr(self.learning_module, 'get_q_value'):
            return self.learning_module.get_q_value(state, action)
        else:
            s_tuple = self._to_hashable(state)
            a_tuple = self._to_hashable(action)
            return self.q_table.get(s_tuple, {}).get(a_tuple, 0.0)

    def update_q_value(self, state: Any, action: Any, reward: float, next_state: Any, learning_rate: float, discount_factor: float, action_space: list):
        if hasattr(self.learning_module, 'update_q_value'):
            self.learning_module.update_q_value(state, action, reward, next_state, learning_rate, discount_factor, action_space)
        else:
            s_tuple = self._to_hashable(state)
            a_tuple = self._to_hashable(action)
            ns_tuple = self._to_hashable(next_state)

            if s_tuple not in self.q_table:
                self.initialize_q_table(state, action_space)
            if ns_tuple not in self.q_table:
                 self.initialize_q_table(next_state, action_space)

            current_q = self.q_table[s_tuple].get(a_tuple, 0.0) # Ensure action is in dict

            # Ensure next state's action dictionary is not empty before calling max
            next_q_values = self.q_table.get(ns_tuple, {}).values()
            max_future_q = max(next_q_values) if next_q_values else 0.0

            new_q = current_q + learning_rate * (reward + discount_factor * max_future_q - current_q)
            self.q_table[s_tuple][a_tuple] = new_q

    def _to_hashable(self, item: Any) -> Any:
        """Converts dicts to frozenset of items for use as Q-table keys."""
        if isinstance(item, dict):
            return frozenset(item.items())
        # TODO: Handle lists/other unhashable types if they appear in states/actions
        return item

```
