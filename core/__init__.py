"""
Core System Module - Streamlined bot functionality
All essential systems in one place - NO BLOAT
"""

# Import all core components
from .ai_handler import AIHandler
from .interactive_menus import InteractiveMenus
from .smart_moderation import SmartModerator
from .welcome_system import WelcomeSystem
from .event_manager import EventManager
from .main import CoreSystem, initialize_core, get_core, startup_core

__all__ = [
    "AIHandler",
    "InteractiveMenus",
    "SmartModerator",
    "WelcomeSystem",
    "EventManager",
    "CoreSystem",
    "initialize_core",
    "get_core",
    "startup_core",
]

from .ai_handler import AIHandler
from .interactive_menus import InteractiveMenus
from .smart_moderation import SmartModerator
from .welcome_system import WelcomeSystem
from .event_manager import EventManager

__all__ = [
    "AIHandler",
    "InteractiveMenus",
    "SmartModerator",
    "WelcomeSystem",
    "EventManager",
]
