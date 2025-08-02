"""
Enhanced Configuration Module for Astra Bot
Provides advanced configuration management with validation and type checking
"""

import json
import os
from typing import Dict, Any, Optional, Union
from pathlib import Path
import logging

logger = logging.getLogger("astra.config")


class EnhancedConfig:
    """Enhanced configuration manager with validation and type safety"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._defaults = {
            "discord": {
                "token": "",
                "prefix": "!",
                "intents": {
                    "messages": True,
                    "guilds": True,
                    "members": True,
                    "reactions": True,
                },
            },
            "database": {
                "path": "data/astra.db",
                "backup_interval": 3600,
                "connection_pool_size": 15,
                "enable_wal_mode": True,
            },
            "ai": {
                "openai": {
                    "api_key": "",
                    "model": "gpt-4",
                    "max_tokens": 2000,
                    "temperature": 0.7,
                },
                "azure": {
                    "endpoint": "",
                    "api_key": "",
                    "speech_key": "",
                    "speech_region": "westus",
                },
            },
            "features": {
                "enable_ai": False,
                "enable_voice": False,
                "enable_moderation": True,
                "enable_analytics": True,
            },
            "performance": {
                "max_concurrent_tasks": 50,
                "cache_ttl": 300,
                "rate_limit_per_minute": 60,
                "memory_warning_threshold": 500,
                "memory_critical_threshold": 800,
            },
            "logging": {
                "level": "INFO",
                "max_file_size": "10MB",
                "backup_count": 5,
                "console_output": True,
            },
        }
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from file with fallback to defaults"""
        try:
            if self.config_path.exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    file_config = json.load(f)

                # Merge with defaults
                self._config = self._merge_configs(self._defaults, file_config)
                logger.info(f"✅ Configuration loaded from {self.config_path}")
            else:
                logger.warning(f"⚠️ Config file not found, using defaults")
                self._config = self._defaults.copy()
                self.save_config()

        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in config file: {e}")
            self._config = self._defaults.copy()
        except Exception as e:
            logger.error(f"❌ Error loading config: {e}")
            self._config = self._defaults.copy()

    def save_config(self) -> None:
        """Save current configuration to file"""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"❌ Error saving config: {e}")

    def _merge_configs(self, defaults: Dict, config: Dict) -> Dict:
        """Recursively merge configuration with defaults"""
        result = defaults.copy()

        for key, value in config.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support"""
        keys = key.split(".")
        value = self._config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """Set configuration value with dot notation support"""
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def get_discord_config(self) -> Dict[str, Any]:
        """Get Discord-specific configuration"""
        return self.get("discord", {})

    def get_database_config(self) -> Dict[str, Any]:
        """Get database-specific configuration"""
        return self.get("database", {})

    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI-specific configuration"""
        return self.get("ai", {})

    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance-specific configuration"""
        return self.get("performance", {})

    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled"""
        return self.get(f"features.{feature}", False)

    def validate_config(self) -> bool:
        """Validate configuration and return True if valid"""
        try:
            # Check required sections
            required_sections = ["discord", "database", "ai", "features", "performance"]
            for section in required_sections:
                if section not in self._config:
                    logger.error(f"❌ Missing required config section: {section}")
                    return False

            # Validate Discord token (if not empty)
            token = self.get("discord.token", "")
            if token and len(token) < 20:
                logger.warning("⚠️ Discord token appears to be invalid")

            # Validate database path
            db_path = self.get("database.path", "")
            if not db_path:
                logger.error("❌ Database path not configured")
                return False

            logger.info("✅ Configuration validation passed")
            return True

        except Exception as e:
            logger.error(f"❌ Configuration validation failed: {e}")
            return False

    @property
    def config(self) -> Dict[str, Any]:
        """Get the full configuration dictionary"""
        return self._config.copy()


# Global instance
enhanced_config = EnhancedConfig()

# Backward compatibility aliases
config = enhanced_config
get_config = enhanced_config.get
set_config = enhanced_config.set
