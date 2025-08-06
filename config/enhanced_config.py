"""
Enhanced Configuration Manager for Astra Bot
Provides centralized configuration management with environment variable support
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AIProviderConfig:
    """Configuration for AI providers"""

    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    max_tokens: int = 2000
    temperature: float = 0.7
    provider_name: Optional[str] = None


class EnhancedConfigManager:
    """Enhanced configuration manager with environment variable support"""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "config/config.json"
        self.config_data: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)

        # Load configuration
        self._load_config()

    def _load_config(self):
        """Load configuration from file and environment"""
        try:
            # Try to load from file first
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    self.config_data = json.load(f)
                    self.logger.info(f"Loaded configuration from {self.config_file}")
            else:
                self.logger.info(
                    f"Config file {self.config_file} not found, using environment variables only"
                )
                self.config_data = {}
        except Exception as e:
            self.logger.warning(f"Failed to load config file: {e}")
            self.config_data = {}

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting from environment variables or config file"""
        # First check environment variables
        env_value = os.getenv(key)
        if env_value is not None:
            # Try to parse as JSON for complex types
            try:
                return json.loads(env_value)
            except (json.JSONDecodeError, TypeError):
                return env_value

        # Then check config file
        if key in self.config_data:
            return self.config_data[key]

        # Return default
        return default

    def get_ai_provider_config(self, provider: str = "universal") -> AIProviderConfig:
        """Get AI provider configuration"""
        if provider == "universal":
            return AIProviderConfig(
                api_key=self.get_setting("AI_API_KEY")
                or self.get_setting("OPENROUTER_API_KEY"),
                base_url=self.get_setting(
                    "AI_BASE_URL", "https://openrouter.ai/api/v1"
                ),
                model=self.get_setting("AI_MODEL", "deepseek/deepseek-r1:nitro"),
                max_tokens=int(self.get_setting("AI_MAX_TOKENS", "2000")),
                temperature=float(self.get_setting("AI_TEMPERATURE", "0.7")),
                provider_name="universal",
            )
        elif provider == "openrouter":
            return AIProviderConfig(
                api_key=self.get_setting("OPENROUTER_API_KEY"),
                base_url=self.get_setting(
                    "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
                ),
                model=self.get_setting(
                    "OPENROUTER_MODEL", "deepseek/deepseek-r1:nitro"
                ),
                max_tokens=int(self.get_setting("OPENROUTER_MAX_TOKENS", "2000")),
                temperature=float(self.get_setting("OPENROUTER_TEMPERATURE", "0.7")),
                provider_name="openrouter",
            )
        elif provider == "openai":
            return AIProviderConfig(
                api_key=self.get_setting("OPENAI_API_KEY"),
                base_url=self.get_setting(
                    "OPENAI_BASE_URL", "https://api.openai.com/v1"
                ),
                model=self.get_setting("OPENAI_MODEL", "gpt-4"),
                max_tokens=int(self.get_setting("OPENAI_MAX_TOKENS", "2000")),
                temperature=float(self.get_setting("OPENAI_TEMPERATURE", "0.7")),
                provider_name="openai",
            )
        else:
            # Default configuration
            return AIProviderConfig()

    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return {
            "path": self.get_setting("DATABASE_PATH", "data/astra.db"),
            "conversation_db": self.get_setting(
                "CONVERSATION_DB_PATH", "data/conversations.db"
            ),
            "backup_interval": int(
                self.get_setting("DB_BACKUP_INTERVAL", "3600")
            ),  # 1 hour
        }

    def get_discord_config(self) -> Dict[str, Any]:
        """Get Discord configuration"""
        return {
            "token": self.get_setting("DISCORD_TOKEN"),
            "command_prefix": self.get_setting("DISCORD_PREFIX", "!"),
            "max_message_length": int(
                self.get_setting("DISCORD_MAX_MESSAGE_LENGTH", "2000")
            ),
            "owner_id": self.get_setting("BOT_OWNER_ID"),
        }

    def get_owner_id(self) -> Optional[int]:
        """Get bot owner Discord ID"""
        owner_id = self.get_setting("BOT_OWNER_ID")
        if owner_id:
            try:
                return int(owner_id)
            except ValueError:
                self.logger.warning(f"Invalid BOT_OWNER_ID format: {owner_id}")
        return None

    def get_cache_config(self) -> Dict[str, Any]:
        """Get cache configuration"""
        return {
            "redis_url": self.get_setting("REDIS_URL"),
            "cache_ttl": int(self.get_setting("CACHE_TTL", "3600")),  # 1 hour
            "max_memory_cache": int(self.get_setting("MAX_MEMORY_CACHE", "1000")),
        }

    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration"""
        return {
            "max_concurrent_requests": int(
                self.get_setting("MAX_CONCURRENT_REQUESTS", "10")
            ),
            "request_timeout": int(self.get_setting("REQUEST_TIMEOUT", "30")),
            "retry_attempts": int(self.get_setting("RETRY_ATTEMPTS", "3")),
            "rate_limit_requests": int(self.get_setting("RATE_LIMIT_REQUESTS", "100")),
            "rate_limit_window": int(self.get_setting("RATE_LIMIT_WINDOW", "60")),
        }

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            "level": self.get_setting("LOG_LEVEL", "INFO"),
            "file": self.get_setting("LOG_FILE", "logs/astra.log"),
            "max_size": self.get_setting("LOG_MAX_SIZE", "10MB"),
            "backup_count": int(self.get_setting("LOG_BACKUP_COUNT", "5")),
        }

    def is_development_mode(self) -> bool:
        """Check if running in development mode"""
        return self.get_setting("DEVELOPMENT_MODE", "false").lower() in (
            "true",
            "1",
            "yes",
        )

    def is_railway_environment(self) -> bool:
        """Check if running in Railway environment"""
        return self.get_setting("RAILWAY_ENVIRONMENT") is not None

    def save_config(self, config_data: Optional[Dict[str, Any]] = None):
        """Save configuration to file"""
        try:
            data_to_save = config_data or self.config_data

            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

            with open(self.config_file, "w") as f:
                json.dump(data_to_save, f, indent=2)

            self.logger.info(f"Configuration saved to {self.config_file}")

        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")

    def update_setting(self, key: str, value: Any):
        """Update a setting in the configuration"""
        self.config_data[key] = value
        self.logger.info(f"Updated setting {key}")

    def get_all_settings(self) -> Dict[str, Any]:
        """Get all current settings (for debugging)"""
        # Don't include sensitive information
        safe_settings = {}
        for key, value in self.config_data.items():
            if (
                "token" in key.lower()
                or "key" in key.lower()
                or "password" in key.lower()
            ):
                safe_settings[key] = "***HIDDEN***"
            else:
                safe_settings[key] = value
        return safe_settings


# Legacy compatibility
try:
    from config.config_manager import config_manager as legacy_config_manager

    # Create wrapper functions for backward compatibility
    def get_config(*args, **kwargs):
        """Backward compatibility wrapper"""
        enhanced_config = EnhancedConfigManager()
        if args:
            return enhanced_config.get_setting(args[0], kwargs.get("default"))
        return enhanced_config.get_all_settings()

    def get_database_path():
        """Backward compatibility wrapper"""
        enhanced_config = EnhancedConfigManager()
        return enhanced_config.get_database_config()["path"]

except ImportError:
    logger.warning("Legacy config manager not available")

# Global instance for convenience
enhanced_config_manager = EnhancedConfigManager()
