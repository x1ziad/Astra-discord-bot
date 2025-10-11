"""
Core System Module - Streamlined bot functionality
All essential systems in one place - NO BLOAT
"""

# Import all core components
from .ai_handler import AIHandler
from .interactive_menus import InteractiveMenus
from .welcome_system import WelcomeSystem
from .event_manager import EventManager
from .concurrent_message_processor import ConcurrentMessageProcessor, MessagePriority, initialize_processor
from .personality_integration import PersonalityIntegration
from .security_integration import SecuritySystemIntegration

__all__ = [
    "AIHandler",
    "InteractiveMenus", 
    "WelcomeSystem",
    "EventManager",
    "ConcurrentMessageProcessor",
    "MessagePriority",
    "initialize_processor",
    "PersonalityIntegration",
    "SecuritySystemIntegration",
]
