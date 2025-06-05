# This file makes PiaAGI_Research_Tools.PiaCML a Python package.

# Expose key classes at the package level for easier imports.

# Core message structures
from .core_messages import (
    GenericMessage,
    MemoryItem,
    PerceptDataPayload,
    GoalUpdatePayload,
    LTMQueryResultPayload,
    SelfKnowledgeConfidenceUpdatePayload, # Added
    LTMQueryPayload,                    # Added
    ActionCommandPayload,               # Added
    AttentionFocusUpdatePayload,        # Added
    ToMInferenceUpdatePayload           # Added
    # Add other specific payloads here as they are defined and needed for top-level access
)

# Message Bus
from .message_bus import MessageBus

# Base classes for modules (examples, add all as needed)
from .base_memory_module import BaseMemoryModule
from .base_long_term_memory_module import BaseLongTermMemoryModule
from .base_working_memory_module import BaseWorkingMemoryModule
from .base_emotion_module import BaseEmotionModule
from .base_motivational_system_module import BaseMotivationalSystemModule
# ... add other base modules

# Concrete module implementations (examples, add all as needed for direct import)
from .concrete_self_model_module import ConcreteSelfModelModule
from .concrete_long_term_memory_module import ConcreteLongTermMemoryModule
from .concrete_working_memory_module import ConcreteWorkingMemoryModule
from .concrete_emotion_module import ConcreteEmotionModule
from .concrete_motivational_system_module import ConcreteMotivationalSystemModule
# ... add other concrete modules

# Optional: Define __all__ if you want to control `from PiaAGI_Research_Tools.PiaCML import *`
__all__ = [
    "GenericMessage", "MemoryItem", "PerceptDataPayload", "GoalUpdatePayload",
    "LTMQueryResultPayload", "SelfKnowledgeConfidenceUpdatePayload",
    "LTMQueryPayload", "ActionCommandPayload",
    "AttentionFocusUpdatePayload", "ToMInferenceUpdatePayload", # Added
    "MessageBus",
    "BaseMemoryModule", "BaseLongTermMemoryModule", "BaseWorkingMemoryModule",
    "BaseEmotionModule", "BaseMotivationalSystemModule",
    "ConcreteSelfModelModule", "ConcreteLongTermMemoryModule", "ConcreteWorkingMemoryModule",
    "ConcreteEmotionModule", "ConcreteMotivationalSystemModule",
    # Add other exposed class names here
]
