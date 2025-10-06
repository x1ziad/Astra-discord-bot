"""
AI Module Package
=================
This package contains all AI-related components for the AstraBot system.

Components:
- multi_provider_ai: Modern Multi-Provider AI Management System
- universal_ai_client: Universal client for various AI services
- openrouter_client: Specialized OpenRouter API client
- advanced_intelligence: Advanced AI intelligence system
- user_profiling: User profiling and behavioral analysis
- enhanced_ai_config: AI configuration management
"""

from .multi_provider_ai import (
    MultiProviderAIManager,
    AIProvider,
    AIResponse,
    ProviderStatus,
)
from .universal_ai_client import UniversalAIClient as UAIClient
from .openrouter_client import OpenRouterClient
from .user_profiling import UserProfileManager

__all__ = [
    "MultiProviderAIManager",
    "AIProvider",
    "AIResponse",
    "ProviderStatus",
    "UAIClient",
    "OpenRouterClient",
    "UserProfileManager",
]

__version__ = "2.0.0"
__author__ = "AstraBot Development Team"
