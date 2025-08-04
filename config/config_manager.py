"""
Unified Configuration Manager for Astra Bot
Handles all configuration management with enhanced features
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, asdict, field
import discord
from datetime import datetime

logger = logging.getLogger("astra.config")


@dataclass
class BotConfig:
    """Bot configuration dataclass"""

    name: str = "Astra"
    version: str = "2.0.0"
    description: str = (
        "Advanced AI-powered Discord bot for space exploration and Stellaris roleplay"
    )
    prefix: str = "/"
    owner_id: Optional[int] = None
    debug: bool = False

    # AI Configuration
    ai_enabled: bool = True
    ai_personality: str = "default"
    ai_temperature: float = 0.7
    ai_max_tokens: int = 1500

    # Bot Settings - FIXED: Use snake_case to match the error
    command_sync_on_ready: bool = True
    command_sync_on_join: bool = True
    cleanup_on_leave: bool = False

    # Features
    features: Dict[str, bool] = field(default_factory=dict)

    def __post_init__(self):
        if not self.features:
            self.features = {
                "ai_chat": True,
                "image_generation": True,
                "text_to_speech": True,
                "analytics": True,
                "server_management": True,
                "auto_moderation": False,
                "music": False,
            }


class ConfigManager:
    """Enhanced configuration manager with validation and hot-reloading"""

    def __init__(self, config_path: str = "config/config.json"):
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Default configuration
        self._config = self._load_config()
        self._colors = self._load_colors()
        self._last_modified = self._get_file_mtime()

        logger.info(f"Configuration loaded from {self.config_path}")

    def _load_config(self) -> BotConfig:
        """Load configuration from file or create default"""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Clean the data - remove any unknown fields that would cause errors
                valid_fields = {
                    field.name for field in BotConfig.__dataclass_fields__.values()
                }
                cleaned_data = {k: v for k, v in data.items() if k in valid_fields}

                return BotConfig(**cleaned_data)
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                logger.info("Creating new default configuration...")
                return self._create_default_config()
        else:
            return self._create_default_config()

    def _create_default_config(self) -> BotConfig:
        """Create and save default configuration"""
        config = BotConfig()
        self.save_config(config)
        return config

    def _load_colors(self) -> Dict[str, int]:
        """Load color scheme"""
        return {
            "primary": 0x7289DA,
            "secondary": 0x99AAB5,
            "success": 0x43B581,
            "warning": 0xFAA61A,
            "error": 0xF04747,
            "info": 0x00D4FF,
            "space_blue": 0x1E3A8A,
            "stellar_purple": 0x7C3AED,
            "cosmic_gold": 0xF59E0B,
        }

    def _get_file_mtime(self) -> float:
        """Get file modification time"""
        try:
            return self.config_path.stat().st_mtime if self.config_path.exists() else 0
        except:
            return 0

    def reload_if_changed(self) -> bool:
        """Reload configuration if file has been modified"""
        current_mtime = self._get_file_mtime()
        if current_mtime > self._last_modified:
            self._config = self._load_config()
            self._last_modified = current_mtime
            logger.info("Configuration reloaded due to file change")
            return True
        return False

    def save_config(self, config: Optional[BotConfig] = None):
        """Save configuration to file"""
        config_to_save = config or self._config
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(asdict(config_to_save), f, indent=2)
            self._last_modified = self._get_file_mtime()
            logger.info("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Error saving config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        self.reload_if_changed()

        keys = key.split(".")
        value = asdict(self._config)

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split(".")
        config_dict = asdict(self._config)

        # Navigate to the parent of the target key
        current = config_dict
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        # Set the value
        current[keys[-1]] = value

        # Update config object
        try:
            self._config = BotConfig(**config_dict)
            self.save_config()
        except TypeError as e:
            logger.error(f"Error updating config: {e}")
            # Revert to previous config
            self._config = self._load_config()

    def get_color(self, color_name: str) -> discord.Color:
        """Get Discord color object"""
        color_value = self._colors.get(color_name, self._colors["primary"])
        return discord.Color(color_value)

    def feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled. Supports nested features with dot notation."""
        # First try exact match
        if feature_name in self._config.features:
            return self._config.features.get(feature_name, False)

        # For nested features like "space_content.iss_tracking",
        # check if parent feature "space_content" is enabled
        if "." in feature_name:
            parent_feature = feature_name.split(".")[0]
            if parent_feature in self._config.features:
                return self._config.features.get(parent_feature, False)

        # Default to False if feature not found
        return False

    def get_bot_config(self) -> BotConfig:
        """Get the complete bot configuration"""
        self.reload_if_changed()
        return self._config


# Global configuration manager instance
config_manager = ConfigManager()


# Convenience functions for backward compatibility
def feature_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled (backward compatibility)"""
    return config_manager.feature_enabled(feature_name)
