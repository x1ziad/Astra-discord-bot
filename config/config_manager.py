"""
Enhanced configuration management system for Astra Discord Bot
Handles loading, validation, access to configuration, and feature flags
"""

import json
import os
import logging
import discord
from typing import Any, Dict, List, Union, Optional
from datetime import datetime
from pathlib import Path


class ConfigManager:
    """
    Configuration management system that handles loading, validation,
    and access to bot configuration with support for features and colors
    """

    def __init__(self, config_path: str = "config/config.json"):
        """Initialize the configuration manager with the specified config file"""
        self.config_path = config_path
        self.config_data = {}
        self.logger = logging.getLogger("Astra")
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from file with fallbacks"""
        try:
            # First try the specified path
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config_data = json.load(f)
                    self.logger.info(f"Configuration loaded from {self.config_path}")
                    return

            # Fallbacks in case the primary config is not found
            fallback_paths = [
                "config/iconfig.json",
                "iconfig.json",
                "config.json",
                "data/config.json",
            ]

            for path in fallback_paths:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        self.config_data = json.load(f)
                        # Update the config_path to the successful path
                        self.config_path = path
                        self.logger.info(
                            f"Configuration loaded from fallback path: {path}"
                        )
                        return

            # If no config is found, use default minimal config
            self.logger.warning(
                "No configuration file found, using default configuration"
            )
            self._use_default_config()

        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            self._use_default_config()

    def _use_default_config(self) -> None:
        """Use default configuration when loading fails"""
        self.config_data = {
            "bot_settings": {
                "name": "Astra",
                "version": "1.0.0",
                "description": "A Discord bot for space exploration and Stellaris roleplay",
                "prefix": "/",
                "command_sync_on_ready": True,
            },
            "features": {
                "space_content": True,
                "space_content.iss_tracking": True,
                "space_content.launch_notifications": True,
                "quiz_system": True,
                "roles_management": True,
                "notion_integration": False,
            },
            "colors": {
                "primary": "0x7289da",
                "success": "0x43b581",
                "warning": "0xfaa61a",
                "error": "0xf04747",
                "space": "0x000033",
            },
            "development": {"debug_mode": True, "enable_all_features": True},
        }

        # Try to save the default config
        try:
            self.save_config()
            self.logger.info("Default configuration created and saved")
        except:
            self.logger.warning("Could not save default configuration")

    def save_config(self) -> bool:
        """Save the current configuration to file"""
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=2)

            self.logger.info(f"Configuration saved to {self.config_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value by its path
        Example: get('bot_settings.name')
        """
        keys = key_path.split(".")
        value = self.config_data

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key_path: str, value: Any) -> None:
        """
        Set a configuration value by its path
        Example: set('bot_settings.name', 'Astra')
        """
        keys = key_path.split(".")
        target = self.config_data

        # Navigate to the last nested dictionary
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]

        # Set the value at the final key
        target[keys[-1]] = value

    def get_color(self, color_name: str) -> discord.Color:
        """Get a color from the configuration, with fallback to default discord colors"""
        color_value = self.get(f"colors.{color_name}")

        if not color_value:
            # Default color mapping
            defaults = {
                "primary": discord.Color.blurple(),
                "success": discord.Color.green(),
                "warning": discord.Color.yellow(),
                "error": discord.Color.red(),
                "space": discord.Color(0x000033),
                "brand": discord.Color(0x5865F2),
            }
            return defaults.get(color_name, discord.Color.blurple())

        # Parse hex color value
        try:
            if isinstance(color_value, str):
                # Remove '0x' prefix if present and convert to int
                if color_value.startswith("0x"):
                    color_value = int(color_value, 16)
                else:
                    color_value = int(color_value, 16)
            return discord.Color(color_value)
        except (ValueError, TypeError):
            self.logger.warning(f"Invalid color value for {color_name}: {color_value}")
            return discord.Color.blurple()

    def is_feature_enabled(self, feature_path: str) -> bool:
        """
        Check if a feature is enabled in the configuration
        Example: is_feature_enabled('space_content.iss_tracking')

        This method supports hierarchical features, so if 'space_content' is False,
        'space_content.iss_tracking' will also return False regardless of its own setting.
        """
        # Always enable features in debug mode if configured
        if self.get("development.debug_mode", False) and self.get(
            "development.enable_all_features", False
        ):
            return True

        # Check feature parts hierarchically
        parts = feature_path.split(".")

        # Start with the first part and check each level
        current_path = parts[0]
        if not self.get(f"features.{current_path}", True):
            return False

        # Check each subsequent level
        for i in range(1, len(parts)):
            current_path = ".".join(parts[: i + 1])
            if not self.get(f"features.{current_path}", True):
                return False

        return True

    def get_guild_setting(
        self, guild_id: Optional[int], setting_path: str, default: Any = None
    ) -> Any:
        """Get a guild-specific setting"""
        if guild_id is None:
            return default

        return self.get(f"guilds.{guild_id}.{setting_path}", default)

    def set_guild_setting(self, guild_id: int, setting_path: str, value: Any) -> None:
        """Set a guild-specific setting"""
        self.set(f"guilds.{guild_id}.{setting_path}", value)
        self.save_config()

    def is_channel_allowed(self, channel: discord.TextChannel, feature: str) -> bool:
        """Check if a feature is allowed in this channel"""
        if not channel or not channel.guild:
            return True  # Allow in DMs

        guild_id = channel.guild.id

        # Check dedicated channel for this feature
        dedicated_channel = self.get_guild_setting(
            guild_id, f"channels.{feature}_channel", None
        )
        if dedicated_channel and str(channel.id) == str(dedicated_channel):
            return True

        # Check allowed channels list
        allowed_channels = self.get_guild_setting(
            guild_id, f"channels.allowed_channels.{feature}", []
        )
        if allowed_channels and str(channel.id) in [str(c) for c in allowed_channels]:
            return True

        # If no restrictions are configured, allow anywhere
        if not dedicated_channel and not allowed_channels:
            return True

        return False

    def get_allowed_channels(self, feature: str, guild_id: Optional[int]) -> List[str]:
        """Get list of channels where a feature is allowed"""
        if guild_id is None:
            return []

        result = []

        # Check dedicated channel
        dedicated = self.get_guild_setting(guild_id, f"channels.{feature}_channel")
        if dedicated:
            result.append(str(dedicated))

        # Check allowed channels list
        allowed = self.get_guild_setting(
            guild_id, f"channels.allowed_channels.{feature}", []
        )
        result.extend([str(c) for c in allowed])

        return result

    def get_all_features(self) -> Dict[str, bool]:
        """Get all configured features and their status"""
        features_dict = {}
        features_section = self.get("features", {})

        # Extract all features from the config
        def extract_features(prefix: str, data: Dict):
            for key, value in data.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    extract_features(full_key, value)
                else:
                    features_dict[full_key] = bool(value)

        extract_features("", features_section)
        return features_dict

    def reset_guild_config(self, guild_id: int) -> bool:
        """Reset a guild's configuration to defaults"""
        try:
            if (
                "guilds" in self.config_data
                and str(guild_id) in self.config_data["guilds"]
            ):
                del self.config_data["guilds"][str(guild_id)]
                self.save_config()
                self.logger.info(f"Reset configuration for guild {guild_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error resetting guild config: {e}")
            return False

    def get_prefix(self, guild_id: Optional[int] = None) -> str:
        """Get command prefix for a guild, or the default prefix"""
        if guild_id:
            return self.get_guild_setting(
                guild_id, "prefix", self.get("bot_settings.prefix", "/")
            )
        return self.get("bot_settings.prefix", "/")


# Create a global instance
config_manager = ConfigManager()
