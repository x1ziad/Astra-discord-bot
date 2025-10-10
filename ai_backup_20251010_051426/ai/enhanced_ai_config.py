"""
Enhanced AI Configuration Manager
Provides optimized configuration management for the new AI architecture
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class AIProviderType(Enum):
    """Available AI provider types"""

    DEEPSEEK_R1 = "deepseek/deepseek-r1:nitro"
    DEEPSEEK_V3 = "deepseek/deepseek-v3"
    QWEN_QWQ = "qwen/qwq-32b-preview"
    GPT_4O_MINI = "openai/gpt-4o-mini"
    CLAUDE_HAIKU = "anthropic/claude-3.5-haiku"


@dataclass
class AIModelConfig:
    """Configuration for AI models"""

    name: str
    max_tokens: int
    temperature: float
    cost_per_1k_tokens: float
    quality_score: float
    speed_score: float

    def get_efficiency_score(self) -> float:
        """Calculate efficiency score (quality/cost ratio)"""
        return (self.quality_score * self.speed_score) / max(
            self.cost_per_1k_tokens, 0.001
        )


class EnhancedAIConfig:
    """Enhanced AI configuration manager with intelligent defaults"""

    def __init__(self):
        self.logger = logging.getLogger("astra.enhanced_ai_config")

        # Model configurations with performance metrics
        self.model_configs = {
            AIProviderType.DEEPSEEK_R1: AIModelConfig(
                name="DeepSeek R1",
                max_tokens=1000,
                temperature=0.7,
                cost_per_1k_tokens=0.003,  # Estimated cost
                quality_score=0.95,  # High quality reasoning
                speed_score=0.85,  # Good speed
            ),
            AIProviderType.DEEPSEEK_V3: AIModelConfig(
                name="DeepSeek V3",
                max_tokens=1000,
                temperature=0.7,
                cost_per_1k_tokens=0.002,  # Lower cost
                quality_score=0.85,  # Good quality
                speed_score=0.95,  # Very fast
            ),
            AIProviderType.QWEN_QWQ: AIModelConfig(
                name="Qwen QwQ 32B",
                max_tokens=1000,
                temperature=0.7,
                cost_per_1k_tokens=0.004,  # Higher cost
                quality_score=0.90,  # High quality
                speed_score=0.80,  # Moderate speed
            ),
            AIProviderType.GPT_4O_MINI: AIModelConfig(
                name="GPT-4O Mini",
                max_tokens=1000,
                temperature=0.7,
                cost_per_1k_tokens=0.015,  # OpenAI pricing
                quality_score=0.88,  # Good quality
                speed_score=0.90,  # Fast
            ),
            AIProviderType.CLAUDE_HAIKU: AIModelConfig(
                name="Claude 3.5 Haiku",
                max_tokens=1000,
                temperature=0.7,
                cost_per_1k_tokens=0.025,  # Anthropic pricing
                quality_score=0.92,  # Very good quality
                speed_score=0.88,  # Good speed
            ),
        }

        # Load configuration
        self.config = self._load_configuration()

        # Performance tracking
        self.model_performance_history: Dict[str, List[float]] = {}
        self.last_optimization = None

        self.logger.info("Enhanced AI configuration manager initialized")

    def _load_configuration(self) -> Dict[str, Any]:
        """Load configuration from environment and files"""
        config = {
            # Core AI settings
            "ai_provider": os.getenv("AI_PROVIDER", "deepseek_r1"),
            "ai_api_key": os.getenv("AI_API_KEY"),
            "ai_base_url": os.getenv("AI_BASE_URL", "https://openrouter.ai/api/v1"),
            # Model selection strategy
            "model_selection_strategy": os.getenv(
                "MODEL_SELECTION_STRATEGY", "efficiency"
            ),  # efficiency, quality, speed, cost
            "auto_model_switching": os.getenv("AUTO_MODEL_SWITCHING", "true").lower()
            == "true",
            "quality_threshold": float(os.getenv("QUALITY_THRESHOLD", "0.7")),
            # Token optimization
            "max_tokens": int(os.getenv("AI_MAX_TOKENS", "1000")),
            "temperature": float(os.getenv("AI_TEMPERATURE", "0.7")),
            "token_optimization": os.getenv("TOKEN_OPTIMIZATION", "true").lower()
            == "true",
            # Performance settings
            "response_caching": os.getenv("RESPONSE_CACHING", "true").lower() == "true",
            "cache_ttl": int(os.getenv("CACHE_TTL", "300")),
            "performance_monitoring": os.getenv(
                "PERFORMANCE_MONITORING", "true"
            ).lower()
            == "true",
            # Rate limiting and costs
            "daily_token_limit": int(os.getenv("DAILY_TOKEN_LIMIT", "100000")),
            "cost_monitoring": os.getenv("COST_MONITORING", "true").lower() == "true",
            "budget_alert_threshold": float(os.getenv("BUDGET_ALERT_THRESHOLD", "0.8")),
            # Conversation optimization
            "conversation_memory_optimization": os.getenv(
                "CONVERSATION_MEMORY_OPTIMIZATION", "true"
            ).lower()
            == "true",
            "context_window_optimization": os.getenv(
                "CONTEXT_WINDOW_OPTIMIZATION", "true"
            ).lower()
            == "true",
            "user_personalization": os.getenv("USER_PERSONALIZATION", "true").lower()
            == "true",
            # Fallback settings
            "fallback_models": [
                AIProviderType.DEEPSEEK_V3.value,
                AIProviderType.QWEN_QWQ.value,
                AIProviderType.GPT_4O_MINI.value,
            ],
            "graceful_degradation": os.getenv("GRACEFUL_DEGRADATION", "true").lower()
            == "true",
        }

        # Validate critical settings
        self._validate_configuration(config)

        return config

    def _validate_configuration(self, config: Dict[str, Any]):
        """Validate configuration settings"""
        if not config.get("ai_api_key"):
            self.logger.warning(
                "⚠️ AI_API_KEY not configured - AI features will be limited"
            )

        if config.get("max_tokens", 0) > 2000:
            self.logger.warning(
                f"⚠️ max_tokens ({config['max_tokens']}) is high - consider reducing for cost optimization"
            )

        if config.get("temperature", 0) > 1.0:
            self.logger.warning(
                f"⚠️ temperature ({config['temperature']}) is above 1.0 - may cause unpredictable responses"
            )

    def get_optimal_model(self, context: Dict[str, Any] = None) -> AIProviderType:
        """Get optimal model based on configuration and context"""
        strategy = self.config.get("model_selection_strategy", "efficiency")

        if strategy == "efficiency":
            return self._get_most_efficient_model()
        elif strategy == "quality":
            return self._get_highest_quality_model()
        elif strategy == "speed":
            return self._get_fastest_model()
        elif strategy == "cost":
            return self._get_cheapest_model()
        else:
            # Default to efficiency
            return self._get_most_efficient_model()

    def _get_most_efficient_model(self) -> AIProviderType:
        """Get model with best efficiency score"""
        best_model = AIProviderType.DEEPSEEK_R1
        best_score = 0

        for provider, config in self.model_configs.items():
            efficiency = config.get_efficiency_score()
            if efficiency > best_score:
                best_score = efficiency
                best_model = provider

        return best_model

    def _get_highest_quality_model(self) -> AIProviderType:
        """Get model with highest quality score"""
        return max(
            self.model_configs.keys(), key=lambda p: self.model_configs[p].quality_score
        )

    def _get_fastest_model(self) -> AIProviderType:
        """Get model with highest speed score"""
        return max(
            self.model_configs.keys(), key=lambda p: self.model_configs[p].speed_score
        )

    def _get_cheapest_model(self) -> AIProviderType:
        """Get model with lowest cost"""
        return min(
            self.model_configs.keys(),
            key=lambda p: self.model_configs[p].cost_per_1k_tokens,
        )

    def get_model_config(self, provider: AIProviderType) -> AIModelConfig:
        """Get configuration for specific model"""
        return self.model_configs.get(
            provider, self.model_configs[AIProviderType.DEEPSEEK_R1]
        )

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get configuration setting with default"""
        return self.config.get(key, default)

    def update_model_performance(self, provider: AIProviderType, quality_score: float):
        """Update model performance tracking"""
        provider_name = provider.value

        if provider_name not in self.model_performance_history:
            self.model_performance_history[provider_name] = []

        self.model_performance_history[provider_name].append(quality_score)

        # Keep only recent performance data
        if len(self.model_performance_history[provider_name]) > 100:
            self.model_performance_history[provider_name] = (
                self.model_performance_history[provider_name][-100:]
            )

        # Update model config with recent performance
        if len(self.model_performance_history[provider_name]) >= 10:
            avg_performance = (
                sum(self.model_performance_history[provider_name][-10:]) / 10
            )
            self.model_configs[provider].quality_score = (
                self.model_configs[provider].quality_score * 0.7 + avg_performance * 0.3
            )

    def should_switch_model(
        self, current_provider: AIProviderType, current_quality: float
    ) -> Optional[AIProviderType]:
        """Determine if model should be switched based on performance"""
        if not self.config.get("auto_model_switching", True):
            return None

        quality_threshold = self.config.get("quality_threshold", 0.7)

        # If current quality is below threshold, find better model
        if current_quality < quality_threshold:
            optimal_model = self.get_optimal_model()
            if optimal_model != current_provider:
                self.logger.info(
                    f"Switching from {current_provider.value} to {optimal_model.value} due to poor performance"
                )
                return optimal_model

        return None

    def get_token_optimization_settings(self) -> Dict[str, Any]:
        """Get token optimization settings"""
        return {
            "max_tokens": min(
                self.config.get("max_tokens", 1000), 1000
            ),  # Cap at 1000 for cost control
            "context_optimization": self.config.get(
                "context_window_optimization", True
            ),
            "memory_optimization": self.config.get(
                "conversation_memory_optimization", True
            ),
            "intelligent_truncation": True,
            "priority_message_preservation": True,
        }

    def get_caching_settings(self) -> Dict[str, Any]:
        """Get caching configuration"""
        return {
            "enabled": self.config.get("response_caching", True),
            "ttl": self.config.get("cache_ttl", 300),
            "max_cache_size": 1000,
            "intelligent_cache_keys": True,
            "context_aware_caching": True,
        }

    def get_cost_monitoring_settings(self) -> Dict[str, Any]:
        """Get cost monitoring configuration"""
        return {
            "enabled": self.config.get("cost_monitoring", True),
            "daily_limit": self.config.get("daily_token_limit", 100000),
            "budget_alert_threshold": self.config.get("budget_alert_threshold", 0.8),
            "cost_per_model": {
                provider.value: config.cost_per_1k_tokens
                for provider, config in self.model_configs.items()
            },
        }

    def get_performance_settings(self) -> Dict[str, Any]:
        """Get performance monitoring settings"""
        return {
            "monitoring_enabled": self.config.get("performance_monitoring", True),
            "quality_tracking": True,
            "response_time_tracking": True,
            "user_satisfaction_tracking": True,
            "automatic_optimization": self.config.get("auto_model_switching", True),
        }

    def get_conversation_settings(self) -> Dict[str, Any]:
        """Get conversation optimization settings"""
        return {
            "memory_optimization": self.config.get(
                "conversation_memory_optimization", True
            ),
            "user_personalization": self.config.get("user_personalization", True),
            "context_awareness": True,
            "intelligent_prompting": True,
            "adaptive_response_style": True,
            "emotional_intelligence": True,
        }

    def export_configuration(self) -> Dict[str, Any]:
        """Export current configuration for backup or analysis"""
        return {
            "config": self.config,
            "model_configs": {
                provider.value: {
                    "name": config.name,
                    "max_tokens": config.max_tokens,
                    "temperature": config.temperature,
                    "cost_per_1k_tokens": config.cost_per_1k_tokens,
                    "quality_score": config.quality_score,
                    "speed_score": config.speed_score,
                    "efficiency_score": config.get_efficiency_score(),
                }
                for provider, config in self.model_configs.items()
            },
            "performance_history": self.model_performance_history,
        }

    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommendations for configuration optimization"""
        recommendations = []

        # Token usage recommendations
        if self.config.get("max_tokens", 1000) > 1000:
            recommendations.append(
                {
                    "type": "cost_optimization",
                    "priority": "high",
                    "recommendation": "Reduce max_tokens to 1000 or less for better cost efficiency",
                    "current_value": self.config.get("max_tokens"),
                    "suggested_value": 1000,
                }
            )

        # Model selection recommendations
        current_model = self.get_optimal_model()
        efficiency_score = self.model_configs[current_model].get_efficiency_score()

        if efficiency_score < 30:  # Arbitrary threshold
            recommendations.append(
                {
                    "type": "model_optimization",
                    "priority": "medium",
                    "recommendation": f"Consider switching to a more efficient model",
                    "current_model": current_model.value,
                    "suggested_models": [self._get_most_efficient_model().value],
                }
            )

        # Caching recommendations
        if not self.config.get("response_caching", True):
            recommendations.append(
                {
                    "type": "performance_optimization",
                    "priority": "medium",
                    "recommendation": "Enable response caching for better performance",
                    "impact": "Reduces API calls and improves response times",
                }
            )

        # Budget recommendations
        daily_limit = self.config.get("daily_token_limit", 100000)
        if daily_limit > 200000:
            recommendations.append(
                {
                    "type": "budget_optimization",
                    "priority": "low",
                    "recommendation": "Consider setting a lower daily token limit for budget control",
                    "current_limit": daily_limit,
                    "suggested_limit": 100000,
                }
            )

        return recommendations


# Global enhanced config instance
_enhanced_config_instance: Optional[EnhancedAIConfig] = None


def get_enhanced_ai_config() -> EnhancedAIConfig:
    """Get or create global enhanced AI config instance"""
    global _enhanced_config_instance
    if _enhanced_config_instance is None:
        _enhanced_config_instance = EnhancedAIConfig()
    return _enhanced_config_instance


def initialize_enhanced_ai_config() -> EnhancedAIConfig:
    """Initialize global enhanced AI config instance"""
    global _enhanced_config_instance
    _enhanced_config_instance = EnhancedAIConfig()
    return _enhanced_config_instance


if __name__ == "__main__":
    # Test the enhanced config
    print("🧪 Testing Enhanced AI Configuration...")

    config = EnhancedAIConfig()

    # Test model selection
    optimal_model = config.get_optimal_model()
    print(f"Optimal model: {optimal_model.value}")

    # Test configuration export
    exported_config = config.export_configuration()
    print(f"Configuration exported: {len(exported_config)} sections")

    # Test recommendations
    recommendations = config.get_optimization_recommendations()
    print(f"Optimization recommendations: {len(recommendations)}")

    for rec in recommendations:
        print(f"- {rec['type']}: {rec['recommendation']}")

    print("✅ Enhanced AI Configuration test completed")
