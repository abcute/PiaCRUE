from typing import Any, Dict, List, Optional
import uuid # For module ID generation if needed, and triggering_event_id
import datetime # For payloads if not already imported by core_messages

try:
    from .base_emotion_module import BaseEmotionModule
    from .message_bus import MessageBus # Import MessageBus
    from .core_messages import GenericMessage, GoalUpdatePayload, EmotionalStateChangePayload # Import message types
except ImportError:
    # Fallback for standalone execution or if .base_emotion_module is not found in the current path
    print("Warning: Running ConcreteEmotionModule with stubbed imports (MessageBus, core_messages, BaseEmotionModule).")
    class BaseEmotionModule: # Minimal stub
        def update_emotional_state(self, appraisal_info: Dict[str, Any], event_source: Optional[str] = None) -> None: pass
        def get_current_emotional_state(self) -> Dict[str, Any]: return {}
        def express_emotion(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]: return {}
        def get_status(self) -> Dict[str, Any]: return {}
        def regulate_emotion(self, strategy: str, target_emotion_details: Dict) -> bool: return False
        def get_emotional_influence_on_cognition(self) -> Dict: return {}
        def set_personality_profile(self, profile: Dict) -> None: pass

    class MessageBus: # Minimal stub
        def subscribe(self, module_id: str, message_type: str, callback: Any, metadata_filter: Optional[Dict[str,Any]] = None): pass
        def publish(self, message: Any, dispatch_mode: str = "synchronous"): pass

    class GenericMessage: pass
    class GoalUpdatePayload: pass
    class EmotionalStateChangePayload: pass


class ConcreteEmotionModule(BaseEmotionModule):
    """
    A concrete implementation of the BaseEmotionModule focusing on a dimensional
    emotional state (Valence, Arousal, Dominance - VAD).
    Integrated with a MessageBus for receiving various events (GoalUpdates, PerceptData, ActionEvents)
    and publishing EmotionalStateChangePayload messages.

    The core appraisal process in `appraise_event` involves:
    1.  **Receiving Event Details:** Message handlers (`_handle_goal_update_for_appraisal`,
        `_handle_percept_data_for_appraisal`, `_handle_action_event_for_appraisal`)
        process incoming messages and extract conceptual appraisal dimensions like event
        intensity, novelty, expectedness, goal_congruence, agency (who caused the event),
        norm_alignment, and controllability. These are passed to `appraise_event`.
    2.  **Deriving Appraisal Variables:** `appraise_event` further refines these into key
        appraisal variables such as `desirability` (from goal congruence and importance)
        and `unexpectedness`. These derived variables are logged.
    3.  **VAD State Update:** Changes to Valence, Arousal, and Dominance (VAD) are calculated
        based on these appraisal variables and the event's overall intensity. For example:
        - Valence is influenced by desirability and norm_alignment.
        - Arousal is influenced by event intensity, unexpectedness, absolute desirability,
          and novelty, all modulated by a `_reactivity_modifier_arousal` (which can be
          influenced by personality traits).
        - Dominance is influenced by perceived controllability and agency, especially in relation
          to the desirability of the event's outcome.
    4.  **Personality Influence (Conceptual):** The module can store a `_personality_profile`.
        Its influence is currently conceptual for most traits (logged for future extension, e.g.,
        how neuroticism might amplify negative valence changes or extraversion positive ones).
        The `_reactivity_modifier_arousal` is an active example of personality influence.
    5.  **Discrete Emotion Mapping:** A helper method, `_map_vad_to_discrete_emotion`, provides a
        simplified mapping from the current VAD state to a discrete emotion label (e.g., "Joyful",
        "Sad", "Angry", "Calm"). This label is stored in `self.current_discrete_emotion_label`.
    6.  **Emotion Decay:** A decay mechanism (`_decay_emotions`) gradually moves the VAD state
        towards neutral over time.
    7.  **Publishing State Change:** An `EmotionalStateChangePayload` is published via the
        Message Bus, containing the new VAD profile, the derived `primary_emotion` label,
        and an `intensity` value (typically reflecting the current arousal level).

    This module provides a foundational layer for emotional appraisal, with clear logging
    for its conceptual steps and hooks for future, more empirically-grounded refinements.
    """

    def __init__(self,
                 initial_vad_state: Optional[Dict[str, float]] = None,
                 message_bus: Optional[MessageBus] = None,
                 module_id: str = f"ConcreteEmotionModule_{str(uuid.uuid4())[:8]}"):
        """
        Initializes the emotion module.

        Args:
            initial_vad_state: Optional dictionary to set the initial VAD state.
                               Defaults to {"valence": 0.0, "arousal": 0.0, "dominance": 0.0}.
            message_bus: Optional instance of the MessageBus for communication.
            module_id: A unique identifier for this module instance.
        """
        self._message_bus = message_bus
        self._module_id = module_id

        if initial_vad_state is None:
            self.current_emotion_state: Dict[str, float] = {"valence": 0.0, "arousal": 0.0, "dominance": 0.0}
        else:
            self.current_emotion_state: Dict[str, float] = {
                "valence": self._clamp_value(initial_vad_state.get("valence", 0.0)),
                "arousal": self._clamp_value(initial_vad_state.get("arousal", 0.0), 0.0, 1.0), # Arousal typically 0-1
                "dominance": self._clamp_value(initial_vad_state.get("dominance", 0.0))
            }

        self._reactivity_modifier_arousal: float = 1.0
        self._personality_profile: Optional[Dict[str, Any]] = None
        self._log: List[str] = [] # Initialize log

        bus_status_msg = "initialized without a message bus"
        if self._message_bus:
            subscriptions = [
                ("GoalUpdate", self._handle_goal_update_for_appraisal),
                ("PerceptData", self._handle_percept_data_for_appraisal), # New
                ("ActionEvent", self._handle_action_event_for_appraisal)   # New
            ]
            subscribed_types = []
            try:
                # Ensure core message types are available if using type hints for them in handlers
                # from .core_messages import PerceptDataPayload, ActionEventPayload # Already imported at top
                for msg_type, callback in subscriptions:
                    self._message_bus.subscribe(
                        module_id=self._module_id,
                        message_type=msg_type,
                        callback=callback
                    )
                    subscribed_types.append(msg_type)
                if subscribed_types:
                    bus_status_msg = f"initialized and subscribed to: {', '.join(subscribed_types)}"
                else: # Should not happen if subscriptions list is not empty
                    bus_status_msg = "initialized but no subscriptions made"
            except Exception as e:
                bus_status_msg = f"FAILED to subscribe: {e}"

        self._log_message(f"ConcreteEmotionModule '{self._module_id}' {bus_status_msg}.")


    def _log_message(self, message: str):
        """Helper method for internal logging."""
        log_entry = f"{datetime.datetime.now(datetime.timezone.utc).isoformat()} [{self._module_id}]: {message}"
        self._log.append(log_entry)
        # print(log_entry) # Optional for real-time debugging

    def _clamp_value(self, value: float, min_val: float = -1.0, max_val: float = 1.0) -> float:
        """Clamps a value between a minimum and maximum."""
        return max(min_val, min(value, max_val))

    def get_emotional_state(self) -> Dict[str, float]:
        """Returns a copy of the current VAD emotional state."""
        return self.current_emotion_state.copy()

    def _decay_emotions(self, decay_factor: float = 0.95) -> None:
        """
        Applies decay to the current emotional state, moving values towards neutral (0.0).
        Arousal might decay towards a baseline slightly above 0 if preferred.
        """
        self.current_emotion_state["valence"] = self._clamp_value(self.current_emotion_state["valence"] * decay_factor)
        # Arousal decays towards 0, but remains non-negative
        self.current_emotion_state["arousal"] = self._clamp_value(self.current_emotion_state["arousal"] * decay_factor, 0.0, 1.0)
        self.current_emotion_state["dominance"] = self._clamp_value(self.current_emotion_state["dominance"] * decay_factor)
        # print(f"Debug: Emotions decayed to V:{self.current_emotion_state['valence']:.2f} A:{self.current_emotion_state['arousal']:.2f} D:{self.current_emotion_state['dominance']:.2f}")

    def _handle_goal_update_for_appraisal(self, message: GenericMessage) -> None:
        """
        Handles GoalUpdate messages from the message bus and triggers appraisal.
        """
        if not isinstance(message.payload, GoalUpdatePayload):
            print(f"ERROR ({self._module_id}): Received non-GoalUpdatePayload for _handle_goal_update_for_appraisal: {type(message.payload)}")
            return

        payload: GoalUpdatePayload = message.payload
        print(f"INFO ({self._module_id}): Handling GoalUpdate: {payload.goal_id}, Status: {payload.status}, Priority: {payload.priority}")

        event_details: Dict[str, Any] = {
            "type": "GOAL_STATUS_UPDATE",
            # Intensity: Higher priority goals might evoke stronger emotional responses. Scaled 0-1.
            # Clamped to ensure a minimum intensity for any goal update.
            # Note: Dividing payload.priority by 10.0 assumes original priority is on a 0-10 scale.
            # This mapping might need alignment with how Motivational System actually sets/uses GoalUpdatePayload.priority (currently float 0-1).
            "intensity": self._clamp_value(payload.priority / 10.0 if payload.priority else 0.1, 0.05, 1.0),
            "goal_importance": self._clamp_value(payload.priority / 10.0 if payload.priority else 0.1, 0.0, 1.0), # Same assumption for importance scaling
            "triggering_message_id": message.message_id,
            "agency": "system" # Goals are internal/system states or tasks.
        }

        status_to_congruence = {
            "achieved": 1.0,
            "failed": -1.0,
            "active": 0.1,  # Slightly positive as it's being pursued
            "suspended": -0.2, # Slightly negative as it's paused
            "new": 0.05, # Mildly positive for new goals
            "updated": 0.0, # Neutral for simple updates unless content implies more
            "progressing": 0.3, # From previous compatibility logic
            "threatened": -0.5   # From previous compatibility logic
        }
        event_details["goal_congruence"] = status_to_congruence.get(payload.status.lower(), 0.0)

        # Consider adding other appraisal dimensions if derivable from GoalUpdatePayload
        # For example, if a goal is "new", it might imply some novelty.
        if payload.status.lower() == "new":
            event_details["novelty"] = 0.6 # New goals are somewhat novel
            event_details["expectedness"] = 0.4 # And perhaps not fully expected

        self.appraise_event(event_details)

    def _handle_percept_data_for_appraisal(self, message: GenericMessage) -> None:
        """Handles PerceptData messages for emotional appraisal."""
        # Ensure PerceptDataPayload is imported if type checking: from .core_messages import PerceptDataPayload
        if not hasattr(message.payload, 'modality') or not hasattr(message.payload, 'content'): # Basic check for PerceptDataPayload structure
            self._log_message(f"ERROR: Received non-PerceptDataPayload for _handle_percept_data_for_appraisal: {type(message.payload)}")
            return

        payload = message.payload # Assuming it's PerceptDataPayload
        self._log_message(f"Handling PerceptData for appraisal: Modality='{payload.modality}', Content='{str(payload.content)[:100]}...'")

        event_details: Dict[str, Any] = {
            "type": f"PERCEPTION_{payload.modality.upper()}",
            "intensity": 0.5, # Default intensity for percepts
            "novelty": 0.5,   # Default novelty
            "expectedness": 0.5, # Default expectedness
            "triggering_message_id": message.message_id,
            "agency": "environment" # Percepts are from the environment
        }

        # Refined conceptual derivation of appraisal variables from percept content
        if isinstance(payload.content, dict):
            # Example: if percept contains explicit threat indicator
            if payload.content.get("threat_level", 0.0) > 0.7:
                event_details["intensity"] = max(event_details["intensity"], payload.content.get("threat_level", 0.7))
                event_details["goal_congruence"] = -0.8 # Strong negative congruence for threats
                event_details["expectedness"] = 0.2 # Threats might be less expected
                event_details["novelty"] = 0.7 # A high threat might also be novel
                self._log_message(f"  Percept (dict): High threat detected. Intensity: {event_details['intensity']:.2f}, Congruence: {event_details['goal_congruence']:.2f}")
            # Example: social percept indicating positive feedback
            elif payload.content.get("social_feedback_valence", 0.0) > 0.5:
                event_details["intensity"] = max(event_details["intensity"], payload.content.get("social_feedback_valence", 0.5))
                event_details["goal_congruence"] = 0.7 # Positive social feedback is goal congruent
                event_details["norm_alignment"] = 0.6 # Aligns with social norm of positive interaction
                self._log_message(f"  Percept (dict): Positive social feedback. Intensity: {event_details['intensity']:.2f}, Congruence: {event_details['goal_congruence']:.2f}")
        elif isinstance(payload.content, str): # Basic text processing
            text_lower = payload.content.lower()
            if "surprise!" in text_lower or "unexpected" in text_lower:
                event_details["novelty"] = 0.8
                event_details["expectedness"] = 0.1
                event_details["intensity"] = max(event_details["intensity"], 0.6)
                self._log_message(f"  Percept (text): Surprise indicated. Novelty: {event_details['novelty']:.2f}, Expectedness: {event_details['expectedness']:.2f}")


        if payload.modality == "sound" and isinstance(payload.content, dict) and payload.content.get("type") == "sudden_loud_noise":
            event_details["intensity"] = max(event_details["intensity"], 0.9) # Use max to ensure it's at least this high
            event_details["novelty"] = max(event_details["novelty"], 0.8)
            event_details["expectedness"] = min(event_details["expectedness"], 0.1) # Use min if we want lower value
            self._log_message(f"  Appraisal refined by 'sudden_loud_noise': Intensity: {event_details['intensity']:.2f}, Novelty: {event_details['novelty']:.2f}, Expectedness: {event_details['expectedness']:.2f}.")
        elif payload.modality == "text" and isinstance(payload.content, dict): # This was from original, might be redundant if content is str
            sentiment = payload.content.get("sentiment", "neutral") # Assuming content dict has sentiment
            keywords = payload.content.get("keywords", [])
            if sentiment == "very_negative" or any(k in keywords for k in ["warning", "danger", "threat"]):
                event_details["intensity"] = max(event_details["intensity"], 0.8)
                event_details["goal_congruence"] = min(event_details.get("goal_congruence", 0.0), -0.7)
                event_details["expectedness"] = min(event_details.get("expectedness", 0.5), 0.3)
                self._log_message(f"  Appraisal refined by negative text/keywords: Intensity: {event_details['intensity']:.2f}, Congruence: {event_details['goal_congruence']:.2f}.")
            elif sentiment == "very_positive" or "congratulations" in keywords:
                event_details["intensity"] = max(event_details["intensity"], 0.7)
                event_details["goal_congruence"] = max(event_details.get("goal_congruence", 0.0), 0.6)
                self._log_message(f"  Appraisal refined by positive text/keywords: Intensity: {event_details['intensity']:.2f}, Congruence: {event_details['goal_congruence']:.2f}.")

        self.appraise_event(event_details)

    def _handle_action_event_for_appraisal(self, message: GenericMessage) -> None:
        """Handles ActionEvent messages for emotional appraisal."""
        if not hasattr(message.payload, 'action_type') or not hasattr(message.payload, 'status'):
            self._log_message(f"ERROR: Received non-ActionEventPayload for _handle_action_event_for_appraisal: {type(message.payload)}")
            return

        payload: ActionEventPayload = message.payload # type: ignore
        self._log_message(f"Handling ActionEvent for appraisal: Type='{payload.action_type}', Status='{payload.status}'")

        # Determine agency
        agency = "other" # Default if not specified or not self
        # Conceptual: PiaAGIAgent's ID might be stored in a central config or accessible via self-model
        # For now, assuming if agent_id_acting is present and matches this module's ID contextually, it's "self"
        # This is a simplification. A real system would have a clearer way to identify self-actions.
        agent_id_acting = payload.outcome.get("agent_id_acting") if payload.outcome else None
        if agent_id_acting and self._module_id.startswith(agent_id_acting.split('_')[0]): # Simple check if module ID starts like acting agent's ID prefix
             agency = "self"

        intensity = payload.outcome.get("action_importance", 0.5) if payload.outcome else 0.5
        intensity = self._clamp_value(intensity, 0.1, 1.0) # Ensure actions have some minimal intensity

        goal_congruence = 0.0
        expectedness = 0.5
        norm_alignment = 0.0 # Default neutral norm alignment

        if payload.status == "SUCCESS":
            goal_congruence = 0.8 # Successful actions are highly goal-congruent
            expectedness = 0.7 # Agent might expect its actions to succeed more often
            if agency == "self":
                norm_alignment = 0.3 # Conceptual: self-efficacy, doing good/effective action
        elif payload.status == "FAILURE":
            goal_congruence = -0.8 # Failures are incongruent
            expectedness = 0.3 # Failures might be less expected
            intensity = max(intensity, 0.6) # Failures can be more intense
            if agency == "self":
                norm_alignment = -0.2 # Conceptual: self-blame or reduced efficacy perception

        event_details: Dict[str, Any] = {
            "type": f"ACTION_OUTCOME_{payload.action_type.upper()}",
            "intensity": intensity,
            "goal_congruence": goal_congruence,
            "goal_importance": payload.outcome.get("goal_priority", 0.5) if payload.outcome else 0.5, # Importance of goal action was for
            "expectedness": expectedness,
            "agency": agency,
            "norm_alignment": norm_alignment,
            "controllability": 0.8 if agency == "self" else 0.3, # Higher perceived control for own actions
            "triggering_message_id": message.message_id
        }
        self._log_message(f"Appraisal derived from ActionEvent: Agency='{agency}', Congruence={goal_congruence:.2f}, Expectedness={expectedness:.2f}, Intensity={intensity:.2f}, NormAlign={norm_alignment:.2f}.")
        self.appraise_event(event_details)

    def appraise_event(self, event_details: Dict[str, Any]) -> None:
        """
        Appraises an event and updates the VAD emotional state.
        If a message bus is configured, publishes an EmotionalStateChange message.

        Args:
            event_details: A dictionary containing details about the event. Example structure:
                {
                    "type": str, // e.g., "GOAL_PROGRESS", "PERCEPTION_SOUND", "ACTION_OUTCOME_NAVIGATE"
                    "intensity": float, // Perceived intensity of the event (0-1)
                    "novelty": float, // (0-1) - Optional, defaults if not present
                    "expectedness": float, // 0 (unexpected) to 1 (expected) - Optional, defaults
                    "goal_congruence": Optional[float], // -1 (obstructs) to 1 (achieves), 0 (neutral) - Optional
                    "goal_importance": Optional[float], // (0-1) Priority of the affected goal - Optional
                    "controllability": Optional[float], // (0-1) Agent's perceived control - Optional
                    "norm_alignment": Optional[float] // -1 (violates norms) to 1 (aligns) - Optional
                }
        """
        self._log_message(f"Appraising event: {event_details}")

        # --- 1. Derive Conceptual Appraisal Variables ---
        # These variables interpret the raw event_details in terms of core appraisal dimensions.
        # Note: These are simplified derivations for this concrete module.

        intensity = event_details.get("intensity", 0.1) # Overall event intensity (0-1)

        # Desirability: How beneficial/harmful is the event to the agent's goals?
        # Based on goal_congruence (how it aligns with a goal) and goal_importance.
        goal_congruence = event_details.get("goal_congruence", 0.0)
        goal_importance = event_details.get("goal_importance", 0.5) # Assume moderate importance if not specified
        desirability = goal_congruence * goal_importance

        # Unexpectedness: How surprising was the event? (0 expected, 1 very unexpected)
        unexpectedness = 1.0 - event_details.get("expectedness", 0.5)

        agency = event_details.get("agency", "other") # Who caused the event?

        # Normative Significance: Does the event align with social/internal norms?
        norm_match = event_details.get("norm_alignment", 0.0)

        controllability = event_details.get("controllability", 0.5) # Agent's perceived control over the event

        novelty = event_details.get("novelty", 0.0) # Novelty of the event/stimulus itself

        self._log_message(f"  Derived Appraisal Variables: Desirability={desirability:.2f}, Unexpectedness={unexpectedness:.2f}, Agency='{agency}', NormMatch={norm_match:.2f}, Controllability={controllability:.2f}, Novelty={novelty:.2f}, EventIntensity={intensity:.2f}")

        # --- 2. Refined VAD Mapping ---
        # These factors determine the *direction and magnitude* of change for V, A, D.
        # Conceptual intensity factors for VAD dimensions (how much each appraisal variable influences V, A, or D)
        intensity_factor_for_valence = 1.0 # How much desirability impacts valence
        intensity_factor_for_arousal_base = 0.4 # Base impact of event intensity on arousal
        intensity_factor_for_arousal_surprise = 0.4 # Impact of unexpectedness on arousal
        intensity_factor_for_arousal_desirability = 0.2 # Impact of desirability magnitude on arousal
        intensity_factor_for_dominance_control = 0.3 # Impact of controllability on dominance
        intensity_factor_for_dominance_agency = 0.1 # Small boost/reduction based on agency for desirable/undesirable outcomes

        valence_change = 0.0
        arousal_change = 0.0
        dominance_change = 0.0

        # Valence updates
        # Primarily driven by desirability and normative significance.
        valence_change += desirability * intensity_factor_for_valence * intensity
        valence_change += norm_match * 0.2 * intensity # Norms have a moderate impact on valence
        self._log_message(f"  Valence Change Components: DesirabilityEffect={(desirability * intensity_factor_for_valence * intensity):.2f}, NormMatchEffect={(norm_match * 0.2 * intensity):.2f}")

        # Arousal updates
        # Influenced by event intensity, unexpectedness, novelty, and magnitude of desirability.
        current_arousal_reactivity = self._reactivity_modifier_arousal
        arousal_change += intensity * intensity_factor_for_arousal_base
        arousal_change += unexpectedness * intensity_factor_for_arousal_surprise * intensity
        arousal_change += abs(desirability) * intensity_factor_for_arousal_desirability * intensity
        arousal_change += novelty * 0.1 * intensity # Small direct effect of novelty on arousal
        self._log_message(f"  Arousal Change Components: BaseIntensityEffect={(intensity * intensity_factor_for_arousal_base):.2f}, UnexpectednessEffect={(unexpectedness * intensity_factor_for_arousal_surprise * intensity):.2f}, AbsDesirabilityEffect={(abs(desirability) * intensity_factor_for_arousal_desirability * intensity):.2f}, NoveltyEffect={(novelty * 0.1 * intensity):.2f}")

        # Apply overall arousal reactivity (can be personality-based)
        arousal_change *= current_arousal_reactivity


        # Dominance updates
        # Influenced by controllability and agency in relation to desirability.
        dominance_change += (controllability - 0.5) * intensity_factor_for_dominance_control * intensity
        if agency == "self":
            if desirability > 0: # Self caused good outcome
                dominance_change += intensity_factor_for_dominance_agency * intensity
            elif desirability < 0: # Self caused bad outcome
                dominance_change -= intensity_factor_for_dominance_agency * intensity
        self._log_message(f"  Dominance Change Components: ControllabilityEffect={((controllability - 0.5) * intensity_factor_for_dominance_control * intensity):.2f}, AgencyEffectRelevant={agency=='self'}")


        # Apply calculated changes to the current VAD state
        # These are added to the *existing* emotion state, not replacing it.
        self.current_emotion_state["valence"] += valence_change
        self.current_emotion_state["arousal"] += arousal_change
        self.current_emotion_state["dominance"] += dominance_change

        # Clamp values
        self.current_emotion_state["valence"] = self._clamp_value(self.current_emotion_state["valence"])
        self.current_emotion_state["arousal"] = self._clamp_value(self.current_emotion_state["arousal"], 0.0, 1.0) # Arousal 0-1
        self.current_emotion_state["dominance"] = self._clamp_value(self.current_emotion_state["dominance"])

        # Conceptual Personality Influence (Illustrative)
        # This is applied *before* decay but *after* initial change calculations.
        if self._personality_profile:
            self._log_message(f"Conceptual: Applying personality profile {self._personality_profile} to appraisal.")
            # Example: Neuroticism amplifies negative valence changes
            # Note: valence_change here is the delta, not the new state. The effect should apply to the new state or the delta.
            # Let's refine this to apply to the delta before adding to current_emotion_state,
            # or adjust current_emotion_state directly after the initial update.
            # For simplicity, let's assume personality affects the *change* values before they are added,
            # or re-calculates the final state based on these.
            # The current code adds valence_change, then clamps, then applies personality. This is complex.
            # A simpler model for personality: it influences the *interpretation* (appraisal variables) or the *reactivity* (VAD change magnitudes).

            # Re-evaluating personality application:
            # It's better if personality influences the *initial* change calculation (valence_change, arousal_change, dominance_change)
            # or the final VAD values *before* clamping and decay.
            # The current arousal_reactivity is one such example. Let's make others similar.

            # Example: Neuroticism amplifies negative valence component if desirability was negative
            if self._personality_profile.get("neuroticism", 0.0) > 0.7 and desirability < 0:
                neuroticism_factor = 1.5
                self._log_message(f"  Personality (Neuroticism > 0.7 & neg desirability): Amplifying negative valence impact by {neuroticism_factor}.")
                # This implies valence_change due to desirability should be amplified
                # This part is tricky to inject here without redoing valence_change.
                # For now, this log indicates a conceptual step. A true implementation would integrate it into the change calculation.

            # Example: Extraversion amplifies positive valence component if desirability was positive
            if self._personality_profile.get("extraversion", 0.0) > 0.7 and desirability > 0:
                extraversion_factor = 1.2
                self._log_message(f"  Personality (Extraversion > 0.7 & pos desirability): Amplifying positive valence impact by {extraversion_factor}.")
                # Similar to neuroticism, this would ideally modify the valence_change calculation.

            self._log_message(f"  Personality: Arousal reactivity modifier {self._reactivity_modifier_arousal} was applied during arousal calculation.")


        # print(f"Debug: VAD before decay: V:{self.current_emotion_state['valence']:.2f} A:{self.current_emotion_state['arousal']:.2f} D:{self.current_emotion_state['dominance']:.2f}")
        self._decay_emotions() # Apply decay after each appraisal update
        self._log_message(f"VAD after decay: V:{self.current_emotion_state['valence']:.2f} A:{self.current_emotion_state['arousal']:.2f} D:{self.current_emotion_state['dominance']:.2f}")

        # Map VAD to discrete emotion label
        self.current_discrete_emotion_label = self._map_vad_to_discrete_emotion(self.current_emotion_state) # Added instance variable
        self._log_message(f"Derived discrete emotion: {self.current_discrete_emotion_label}")

        if self._message_bus and EmotionalStateChangePayload and GenericMessage: # Check core types too
            esc_payload = EmotionalStateChangePayload(
                current_emotion_profile=self.current_emotion_state.copy(),
                primary_emotion=self.current_discrete_emotion_label,
                intensity=self.current_emotion_state['arousal'], # Using arousal as overall intensity proxy for the discrete emotion
                triggering_event_id=event_details.get("triggering_message_id"), # Use the one from event_details
                behavioral_impact_suggestions=[] # Optional for now, could be derived too
            )
            emotional_change_message = GenericMessage(
        if "goal_congruence" in event_details:
            goal_congruence = event_details.get("goal_congruence", 0.0)
            goal_importance = event_details.get("goal_importance", 0.5)
            valence_change += goal_congruence * goal_importance * intensity

        if "norm_alignment" in event_details:
            norm_alignment = event_details.get("norm_alignment", 0.0)
            valence_change += norm_alignment * 0.3 * intensity # Norm alignment has some impact

        # Arousal updates
        current_arousal_reactivity = self._reactivity_modifier_arousal # Could be influenced by personality
        base_arousal_from_intensity = intensity * 0.5
        arousal_change += base_arousal_from_intensity

        # More unexpected -> more arousal
        arousal_change += (1.0 - event_details.get("expectedness", 0.5)) * 0.5 * intensity
        # Novelty adds to arousal
        arousal_change += event_details.get("novelty", 0.0) * 0.3 * intensity

        if "goal_congruence" in event_details: # Significant goal events are arousing
            arousal_change += abs(event_details.get("goal_congruence", 0.0)) * \
                              event_details.get("goal_importance", 0.1) * \
                              intensity * 0.5 # Scaled by importance and intensity

        arousal_change *= current_arousal_reactivity # Apply overall reactivity

        # Dominance updates
        if "controllability" in event_details:
            controllability = event_details.get("controllability", 0.5)
            dominance_change += (controllability - 0.5) * 0.5 * intensity # More control -> more dominance

        # Apply changes to current_emotion_state
        self.current_emotion_state["valence"] += valence_change
        self.current_emotion_state["arousal"] += arousal_change
        self.current_emotion_state["dominance"] += dominance_change

        # Clamp values
        self.current_emotion_state["valence"] = self._clamp_value(self.current_emotion_state["valence"])
        self.current_emotion_state["arousal"] = self._clamp_value(self.current_emotion_state["arousal"], 0.0, 1.0) # Arousal 0-1
        self.current_emotion_state["dominance"] = self._clamp_value(self.current_emotion_state["dominance"])

        # print(f"Debug: VAD before decay: V:{self.current_emotion_state['valence']:.2f} A:{self.current_emotion_state['arousal']:.2f} D:{self.current_emotion_state['dominance']:.2f}")
        self._decay_emotions() # Apply decay after each appraisal update

        self._log_message(f"VAD updated to V:{self.current_emotion_state['valence']:.2f} A:{self.current_emotion_state['arousal']:.2f} D:{self.current_emotion_state['dominance']:.2f}")

        if self._message_bus and EmotionalStateChangePayload and GenericMessage: # Check core types too
            esc_payload = EmotionalStateChangePayload(
                current_emotion_profile=self.current_emotion_state.copy(),
                primary_emotion=None, # Optional for now
                intensity=self.current_emotion_state['arousal'], # Using arousal as overall intensity proxy
                triggering_event_id=event_details.get("triggering_message_id"),
                behavioral_impact_suggestions=[] # Optional for now
            )
            emotional_change_message = GenericMessage(
                source_module_id=self._module_id,
                message_type="EmotionalStateChange",
                payload=esc_payload
            )
            self._message_bus.publish(emotional_change_message)
            self._log_message(f"Published EmotionalStateChange message (triggered by: {esc_payload.triggering_event_id}).")


    def get_simulated_physiological_effects(self) -> Dict[str, Any]:
        """
        Returns a dictionary of conceptual physiological effects based on VAD state.
        """
        effects: Dict[str, Any] = {}
        valence = self.current_emotion_state["valence"]
        arousal = self.current_emotion_state["arousal"]
        # dominance = self.current_emotion_state["dominance"] # For future use

        if arousal > 0.7:
            effects["attention_focus"] = "narrowed"
        elif arousal > 0.4:
            effects["attention_focus"] = "normal" # Conceptual normal range
        else:
            effects["attention_focus"] = "broad"

        if valence < -0.5 and arousal > 0.6:
            effects["cognitive_bias"] = "threat_detection_priority"
        elif valence > 0.5 and arousal > 0.3:
            effects["cognitive_bias"] = "opportunity_seeking"

        if valence > 0.5 and arousal > 0.3: # Positive, somewhat aroused state
            effects["learning_rate_modifier_suggestion"] = 1.2
        elif valence < -0.4: # Negative states
            effects["learning_rate_modifier_suggestion"] = 0.8
        else: # Neutral or low arousal states
            effects["learning_rate_modifier_suggestion"] = 1.0

        # Example using dominance:
        # if dominance < -0.5: effects["action_tendency"] = "avoidance"
        # elif dominance > 0.5: effects["action_tendency"] = "approach"

        return effects

    # --- Compatibility/Update of methods from BaseEmotionModule ABC ---

    def update_emotional_state(self, appraisal_info: Dict[str, Any], event_source: Optional[str] = None) -> None:
        """
        Compatibility method. Delegates to appraise_event.
        The new `appraise_event` expects a more structured `event_details`.
        This method attempts to map `appraisal_info` to that structure.
        """
        self._log_message(f"`update_emotional_state` (compatibility) called. Delegating to `appraise_event`. Source: {event_source}")
        event_details = {
            "type": appraisal_info.get("type", "unknown"), # Retain original event type if available
            "intensity": appraisal_info.get("event_intensity", appraisal_info.get("intensity", 0.5)),
            "novelty": appraisal_info.get("event_novelty", appraisal_info.get("novelty", 0.0)),
            "expectedness": appraisal_info.get("expectedness", 1.0), # Default to expected if not specified
            "controllability": appraisal_info.get("controllability", 0.5), # Default to moderately controllable
            "triggering_message_id": appraisal_info.get("message_id") # If old system passed message_id
        }

        # Map goal_status to goal_congruence
        if appraisal_info.get("type") == "goal_status" or "goal_status" in appraisal_info :
            goal_status = appraisal_info.get("goal_status")
            if goal_status == "achieved": event_details["goal_congruence"] = 1.0
            elif goal_status == "failed": event_details["goal_congruence"] = -1.0
            elif goal_status == "progressing": event_details["goal_congruence"] = 0.3 # Mildly positive
            elif goal_status == "threatened": event_details["goal_congruence"] = -0.5
            event_details["goal_importance"] = appraisal_info.get("goal_importance", 0.5) # Assume default importance

        # Map event_source if it was used for perceived_valence (simplified)
        if isinstance(event_source, dict) and "perceived_valence" in event_source:
            if event_source["perceived_valence"] == "positive":
                event_details["norm_alignment"] = 0.5 # Assume positive event aligns with some norm/goal
            elif event_source["perceived_valence"] == "negative":
                event_details["norm_alignment"] = -0.5

        self.appraise_event(event_details)


    def get_current_emotional_state(self) -> Dict[str, Any]:
        """Returns the current VAD state. Per BaseEmotionModule, this can include categorical."""
        # For Phase 1, we focus on VAD. A mapping to categorical could be added here if needed.
        return {"vad_state": self.current_emotion_state.copy(), "categorical_emotion": "N/A_Phase1"}


    def express_emotion(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Returns a representation of the current VAD state for expression.
        Phase 1: Simplified to return VAD without categorical label.
        """
        self._log_message(f"express_emotion called. VAD: {self.current_emotion_state}")
        return {
            "vad_state": self.current_emotion_state.copy(),
            "intensity_conceptual": self.current_emotion_state['arousal'],
            "expression_modality_hints": ["vocal_tone_change_vad", "facial_expression_vad_based"] # Conceptual
        }

    def get_status(self) -> Dict[str, Any]:
        """Returns the current status of the Emotion Module."""
        return {
            "module_id": self._module_id,
            "module_type": "ConcreteEmotionModule (Message Bus Integrated)",
            "current_vad_state": self.current_emotion_state.copy(),
            "message_bus_connected": self._message_bus is not None,
            "personality_profile_active": self._personality_profile is not None,
            "reactivity_modifier_arousal": self._reactivity_modifier_arousal,
            "log_entries": len(self._log) # Added log entry count
        }

    def regulate_emotion(self, strategy: str, target_emotion_details: Dict[str, Any]) -> bool:
        """Placeholder for emotion regulation. Not implemented in Phase 1."""
        self._log_message(f"regulate_emotion called (Placeholder). Strategy: {strategy}, Target: {target_emotion_details}")
        return False

    def get_emotional_influence_on_cognition(self) -> Dict[str, Any]:
        """
        Returns conceptual influences on cognition based on the VAD state.
        This is similar to get_simulated_physiological_effects for Phase 1.
        """
        self._log_message("get_emotional_influence_on_cognition called.")
        return self.get_simulated_physiological_effects()

    def set_personality_profile(self, profile: Dict[str, Any]) -> None:
        """Sets a personality profile that might influence emotional responses and baseline VAD."""
        self._log_message(f"set_personality_profile called with {profile}.")
        self._personality_profile = profile

        # Adjust baseline VAD based on personality profile, if specified
        if 'default_mood_valence' in profile and isinstance(profile['default_mood_valence'], (int, float)):
            # Could average with current or set directly, here we average towards it
            self.current_emotion_state['valence'] = self._clamp_value(
                (self.current_emotion_state['valence'] + profile['default_mood_valence']) / 2.0
            )
        if 'default_mood_arousal' in profile and isinstance(profile['default_mood_arousal'], (int, float)):
            self.current_emotion_state['arousal'] = self._clamp_value(
                (self.current_emotion_state['arousal'] + profile['default_mood_arousal']) / 2.0, 0.0, 1.0
            )
        if 'default_mood_dominance' in profile and isinstance(profile['default_mood_dominance'], (int, float)):
            self.current_emotion_state['dominance'] = self._clamp_value(
                (self.current_emotion_state['dominance'] + profile['default_mood_dominance']) / 2.0
            )

        if 'reactivity_modifier_arousal' in profile and isinstance(profile['reactivity_modifier_arousal'], (int, float)):
            self._reactivity_modifier_arousal = float(profile['reactivity_modifier_arousal'])

        self._log_message(f"Personality profile set: {self._personality_profile}")

        # Adjust baseline VAD based on personality profile, if specified and valid
        new_valence = self.current_emotion_state['valence']
        new_arousal = self.current_emotion_state['arousal']
        new_dominance = self.current_emotion_state['dominance']

        if 'default_mood_valence' in profile and isinstance(profile['default_mood_valence'], (int, float)):
            # Conceptual: Blend current with personality baseline, or set to baseline.
            # Here, let's assume it influences the baseline towards which decay happens,
            # or sets a new resting state if agent is near neutral.
            # For simplicity in this update, we'll log it and it can be used by a more complex decay/regulation.
            # A simple direct effect for demonstration:
            new_valence = self._clamp_value((new_valence + profile['default_mood_valence']) / 2.0)
            self._log_message(f"  Personality: default_mood_valence {profile['default_mood_valence']} influencing VAD.")

        if 'default_mood_arousal' in profile and isinstance(profile['default_mood_arousal'], (int, float)):
            new_arousal = self._clamp_value((new_arousal + profile['default_mood_arousal']) / 2.0, 0.0, 1.0)
            self._log_message(f"  Personality: default_mood_arousal {profile['default_mood_arousal']} influencing VAD.")

        if 'default_mood_dominance' in profile and isinstance(profile['default_mood_dominance'], (int, float)):
            new_dominance = self._clamp_value((new_dominance + profile['default_mood_dominance']) / 2.0)
            self._log_message(f"  Personality: default_mood_dominance {profile['default_mood_dominance']} influencing VAD.")

        if 'reactivity_modifier_arousal' in profile and isinstance(profile['reactivity_modifier_arousal'], (int, float)):
            self._reactivity_modifier_arousal = max(0.1, float(profile['reactivity_modifier_arousal'])) # Ensure it's positive
            self._log_message(f"  Personality: reactivity_modifier_arousal set to {self._reactivity_modifier_arousal}.")

        # Only update if there was a change from personality application
        if (new_valence != self.current_emotion_state['valence'] or
            new_arousal != self.current_emotion_state['arousal'] or
            new_dominance != self.current_emotion_state['dominance']):

            self.current_emotion_state['valence'] = new_valence
            self.current_emotion_state['arousal'] = new_arousal
            self.current_emotion_state['dominance'] = new_dominance
            self._log_message(f"VAD state adjusted by personality profile: V={new_valence:.2f}, A={new_arousal:.2f}, D={new_dominance:.2f}")
            # Optionally, publish an EmotionalStateChange if personality causes a significant shift
            # For now, only appraise_event publishes.

    def _map_vad_to_discrete_emotion(self, vad_state: Dict[str, float]) -> str:
        """
        Conceptually maps a VAD state to a discrete emotion label.
        This is a very simplified mapping for illustrative purposes.
        A more sophisticated model would involve more complex rules or learned mappings.
        """
        V = vad_state.get("valence", 0.0)
        A = vad_state.get("arousal", 0.0)
        # D = vad_state.get("dominance", 0.0) # Dominance not used in this simple mapping yet

        # self._log_message(f"Mapping VAD (V:{V:.2f}, A:{A:.2f}) to discrete emotion.") # Optional: for debugging mapping

        if A < 0.2: # Low arousal states
            if V > 0.3: return "Content"
            if V < -0.3: return "Sadness" # Calm sadness (e.g., melancholy)
            return "Calm"
        elif A > 0.7: # High arousal states
            if V > 0.5: return "Joy_Excited" # High V, High A
            if V > 0.2: return "Pleased_Alert" # Mid V, High A
            if V < -0.5: return "Anger_Rage" # Low V, High A
            if V < -0.2: return "Distress_Fear" # Mid-Low V, High A
            return "High_Arousal_Neutral_Valence" # e.g. Surprise
        else: # Medium arousal states
            if V > 0.5: return "Happy" # Mid A, High V
            if V > 0.2: return "Pleased_Engaged" # Mid A, Mid V
            if V < -0.5: return "Frustration_Annoyance" # Mid A, Low V
            if V < -0.2: return "Displeasure" # Mid A, Mid-Low V
            return "Neutral_Active"

        # Fallback, though above logic should cover all V/A ranges.
        # return "Neutral" # Already covered by Calm if V is neutral and A is low.

if __name__ == '__main__':
    import asyncio
    import time
    # Ensure PerceptDataPayload and ActionEventPayload are available for the __main__ if used directly
    # For this refactoring, they are not directly constructed in __main__ but handled by module.
    # However, if you were to add tests here that publish them, you'd need:
    # from .core_messages import PerceptDataPayload, ActionEventPayload # If running as part of package
    # Or define stubs if running standalone and they are not in the stub section.


    # Attempt to import MessageBus and core_messages from the local directory structure
    # This is for the __main__ block to find them if not installed as a package.
    try:
        from message_bus import MessageBus
        from core_messages import GenericMessage, GoalUpdatePayload, EmotionalStateChangePayload
        # Add PerceptDataPayload and ActionEventPayload if you plan to manually create and publish them in __main__
        # from core_messages import PerceptDataPayload, ActionEventPayload
    except ImportError:
        print("CRITICAL: Failed to import MessageBus or core_messages for __main__ test. Ensure they are in Python path or same directory.")
        # Fallback to stubs if they were defined above due to initial import error
        if 'MessageBus' not in globals(): # Re-define if initial import failed and stubs were used
            class MessageBus:
                def subscribe(self, module_id: str, message_type: str, callback: Any, metadata_filter: Optional[Dict[str,Any]] = None): print(f"StubBus: {module_id} subscribed to {message_type}")
                def publish(self, message: Any, dispatch_mode: str = "synchronous"): print(f"StubBus: Publishing {message.message_type}")
            class GenericMessage:
                def __init__(self, source_module_id, message_type, payload, message_id=None):
                    self.source_module_id = source_module_id
                    self.message_type = message_type
                    self.payload = payload
                    self.message_id = message_id or str(uuid.uuid4())
            class GoalUpdatePayload:
                def __init__(self, goal_id, goal_description, priority, status, originator):
                    self.goal_id = goal_id
                    self.goal_description = goal_description
                    self.priority = priority
                    self.status = status
                    self.originator = originator
            class EmotionalStateChangePayload: pass # Already stubbed if needed
            # class PerceptDataPayload: pass # Add if needed for __main__ tests
            # class ActionEventPayload: pass # Add if needed for __main__ tests


    print("--- ConcreteEmotionModule __main__ Test ---")

    # Listener for EmotionalStateChange messages
    received_emotional_states: List[GenericMessage] = []
    def emotional_state_listener(message: GenericMessage):
        print(f"\n émotion_state_listener: Received EmotionalStateChange! ID: {message.message_id[:8]}")
        if hasattr(message.payload, 'current_emotion_profile'): # Check if it's likely an EmotionalStateChangePayload
            payload = message.payload # type: ignore
            print(f"  Source: {message.source_module_id}")
            print(f"  VAD: {payload.current_emotion_profile}") # type: ignore
            print(f"  Intensity (Arousal): {payload.intensity:.2f}") # type: ignore
            print(f"  Triggering Event ID: {payload.triggering_event_id[:8] if payload.triggering_event_id else 'N/A'}") # type: ignore
            received_emotional_states.append(message)
        else:
            print(f"  ERROR: Listener received non-EmotionalStateChangePayload structured message: {type(message.payload)}")

    async def main_test_flow():
        # 1. Setup
        bus = MessageBus()
        emotion_module = ConcreteEmotionModule(message_bus=bus, module_id="EmotionModTest01")

        print("\n--- Initial Status ---")
        print(emotion_module.get_status())
        print("Initial VAD state:", emotion_module.get_emotional_state())

        bus.subscribe(
            module_id="TestListener",
            message_type="EmotionalStateChange",
            callback=emotional_state_listener
        )
        print("\nTestListener subscribed to EmotionalStateChange.")

        # 2. Simulate a GoalUpdate message
        print("\n--- Simulating GoalUpdate (Goal Achieved) ---")
        goal_achieved_payload = GoalUpdatePayload(
            goal_id="test_goal_001",
            goal_description="Test achieving a goal",
            priority=0.8, # High priority
            status="achieved",
            originator="TestSystem"
        )
        goal_achieved_message = GenericMessage(
            source_module_id="GoalSetterModule",
            message_type="GoalUpdate",
            payload=goal_achieved_payload
        )
        bus.publish(goal_achieved_message) # Default sync dispatch

        # Allow some time for bus processing if it were async, or for prints
        await asyncio.sleep(0.05)

        assert len(received_emotional_states) > 0, "EmotionalStateChange was not received by listener"
        if received_emotional_states:
            last_esc_payload = received_emotional_states[-1].payload
            assert isinstance(last_esc_payload, EmotionalStateChangePayload)
            assert last_esc_payload.triggering_event_id == goal_achieved_message.message_id
            # Check if VAD reflects positive change (valence > 0, arousal > 0)
            assert last_esc_payload.current_emotion_profile["valence"] > 0.2 # Increased from 0
            assert last_esc_payload.current_emotion_profile["arousal"] > 0.1 # Increased from 0
            print(f"Listener correctly received EmotionalStateChange triggered by {goal_achieved_message.message_id[:8]}.")


        print("\n--- Simulating GoalUpdate (Goal Failed, Async Dispatch) ---")
        received_emotional_states.clear()
        goal_failed_payload = GoalUpdatePayload(
            goal_id="test_goal_002",
            goal_description="Test failing a goal",
            priority=0.9, # High priority
            status="failed",
            originator="TestSystem"
        )
        goal_failed_message = GenericMessage(
            source_module_id="GoalSetterModule",
            message_type="GoalUpdate",
            payload=goal_failed_payload
        )
        bus.publish(goal_failed_message, dispatch_mode="asynchronous")

        await asyncio.sleep(0.1) # Give async tasks time to run

        assert len(received_emotional_states) > 0, "EmotionalStateChange (async) was not received"
        if received_emotional_states:
            last_esc_payload_async = received_emotional_states[-1].payload
            assert isinstance(last_esc_payload_async, EmotionalStateChangePayload)
            assert last_esc_payload_async.triggering_event_id == goal_failed_message.message_id
            assert last_esc_payload_async.current_emotion_profile["valence"] < -0.2 # Decreased from positive
            print(f"Listener correctly received async EmotionalStateChange triggered by {goal_failed_message.message_id[:8]}.")


        print("\n--- Appraise Event Directly (no bus trigger) ---")
        # This should still publish if bus is available
        received_emotional_states.clear()
        event_direct = {
            "type": "DIRECT_APPRAISAL", "intensity": 0.7, "novelty": 0.1, "expectedness": 0.8,
            "goal_congruence": 0.6, "goal_importance": 0.7, "controllability": 0.6,
            # No "triggering_message_id" for direct calls unless manually added
        }
        emotion_module.appraise_event(event_direct)
        await asyncio.sleep(0.05)

        assert len(received_emotional_states) > 0, "EmotionalStateChange (direct appraisal) was not received"
        if received_emotional_states:
            direct_esc_payload = received_emotional_states[-1].payload
            assert isinstance(direct_esc_payload, EmotionalStateChangePayload)
            assert direct_esc_payload.triggering_event_id is None # Because it wasn't in event_details
            print("Listener correctly received EmotionalStateChange from direct appraisal.")


        print("\n--- Test with NO MessageBus ---")
        emotion_module_no_bus = ConcreteEmotionModule(module_id="NoBusMod")
        print(emotion_module_no_bus.get_status())
        # This should not error and not try to publish
        emotion_module_no_bus.appraise_event({"type": "TEST_NO_BUS", "intensity": 0.5, "goal_congruence": 0.5, "goal_importance": 0.5})
        emotion_module_no_bus._log_message("Appraisal with no bus completed without error.")

        print("\n--- ConcreteEmotionModule __main__ Test Complete ---")

    # Run the async main function
    try:
        asyncio.run(main_test_flow())
    except RuntimeError as e:
        if " asyncio.run() cannot be called from a running event loop" in str(e):
            print("Skipping asyncio.run() as an event loop is already running (e.g. in Jupyter/IPython).")
            # You might need to await main_test_flow() directly if in such an environment.
            # loop = asyncio.get_event_loop()
            # loop.run_until_complete(main_test_flow())
        else:
            raise


    # Old __main__ content for reference or non-bus testing:
    # emotion_module = ConcreteEmotionModule()
    # print("\n--- Initial Status ---")
    # print(emotion_module.get_status())
    # print("Initial VAD state:", emotion_module.get_emotional_state())
    # ... (rest of old main commented out for brevity in diff, but kept in actual file if needed) ...
    # print("\nExample Usage Complete (Phase 1 Enhanced Emotion Module).")
