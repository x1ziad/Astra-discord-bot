"""
AI Module Package
=================
This package contains all AI-related components for the AstraBot system.

Components:
- consolidated_ai_engine: Main AI engine with multiple provider support
- universal_ai_client: Universal client for various AI services
- openrouter_client: Specialized OpenRouter API client
- advanced_intelligence: Advanced AI intelligence system
- user_profiling: User profiling and behavioral analysis
- enhanced_ai_config: AI configuration management
"""

from .consolidated_ai_engine import (
    ConsolidatedAIEngine,
    UniversalAIClient,
    AIResponse,
    ConversationContext,
)
from .universal_ai_client import UniversalAIClient as UAIClient, AIProvider
from .openrouter_client import OpenRouterClient
from .user_profiling import UserProfileManager

__all__ = [
    "ConsolidatedAIEngine",
    "UniversalAIClient",
    "UAIClient",
    "OpenRouterClient",
    "AIResponse",
    "ConversationContext",
    "AIProvider",
    "UserProfileManager",
]

__version__ = "2.0.0"
__author__ = "AstraBot Development Team"
