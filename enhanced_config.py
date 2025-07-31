"""
Enhanced Configuration Manager for Astra Discord Bot
Handles JSON configuration, role-based permissions, and guild-specific settings
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime


class ConfigManager:
    """Advanced configuration manager with role-based permissions"""

    def __init__(self, config_file: str = "config/config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
        self.guild_configs = {}  # Per-guild configurations

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        if not self.config_file.exists():
            self.create_default_config()

        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading config: {e}")
            return self.get_default_config()

    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def create_default_config(self):
        """Create default configuration file"""
        default_config = self.get_default_config()

        # Ensure directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_file, "w") as f:
            json.dump(default_config, f, indent=2)

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration structure"""
        return {
            "bot_settings": {
                "name": "Astra",
                "version": "1.0.0",
                "prefix": "/",  # Using slash commands now
                "description": "An advanced Discord bot for space exploration and Stellaris roleplay",
                "activity": "the cosmos | /help",
                "color_palette": {
                    "primary": 0x5865F2,
                    "space": 0x1E1F23,
                    "stellaris": 0x6A0DAD,
                    "success": 0x00FF00,
                    "error": 0xFF0000,
                    "warning": 0xFF9900,
                    "info": 0x0099FF,
                    "cosmic_blue": 0x117ACA,
                    "nebula_purple": 0x9000FF,
                    "stellar_gold": 0xFFD700,
                },
            },
            "permissions": {
                "admin_roles": ["Admin", "Administrator", "Owner", "Bot Manager"],
                "moderator_roles": ["Mod", "Moderator", "Staff", "Helper"],
                "quiz_master_roles": ["Quiz Master", "Educator", "Trivia Host"],
                "space_expert_roles": ["Space Expert", "Astronomer", "Scientist"],
                "stellaris_leader_roles": [
                    "Empire Leader",
                    "Grand Admiral",
                    "Stellaris Expert",
                ],
            },
            "features": {
                "quiz_system": {
                    "enabled": True,
                    "daily_questions": True,
                    "leaderboard_reset_monthly": False,
                },
                "space_content": {
                    "enabled": True,
                    "daily_apod": True,
                    "meteor_alerts": True,
                    "iss_tracking": True,
                },
                "stellaris_features": {
                    "enabled": True,
                    "empire_roles": True,
                    "lore_system": True,
                },
                "notion_integration": {"enabled": False, "auto_sync": False},
            },
            "development": {
                "debug_mode": False,
                "command_sync_on_ready": True,
                "test_guild_id": None,
            },
            "ui_components": {
                "custom_emojis": {
                    "error": "❌",
                    "success": "✅",
                    "warning": "⚠️",
                    "info": "ℹ️",
                    "loading": "⏳",
                    "rocket": "🚀",
                    "star": "⭐",
                }
            },
        }

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'bot_settings.name')"""
        keys = key_path.split(".")
        value = self.config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key_path: str, value: Any) -> bool:
        """Set configuration value using dot notation"""
        keys = key_path.split(".")
        config_section = self.config

        try:
            # Create the nested structure if it doesn't exist
            for key in keys[:-1]:
                if key not in config_section:
                    config_section[key] = {}
                config_section = config_section[key]

            # Set the value at the final key
            config_section[keys[-1]] = value
            return self.save_config()
        except Exception as e:
            print(f"Error setting config value: {e}")
            return False

    def is_admin(self, member: discord.Member) -> bool:
        """Check if member has admin permissions"""
        if member.guild_permissions.administrator:
            return True

        admin_roles = self.get("permissions.admin_roles", [])
        return any(role.name in admin_roles for role in member.roles)

    def is_moderator(self, member: discord.Member) -> bool:
        """Check if member has moderator permissions"""
        if self.is_admin(member):
            return True

        mod_roles = self.get("permissions.moderator_roles", [])
        return any(role.name in mod_roles for role in member.roles)

    def has_role_permission(self, member: discord.Member, permission_type: str) -> bool:
        """Check if member has specific role permission"""
        if self.is_admin(member):
            return True

        role_key = f"permissions.{permission_type}_roles"
        allowed_roles = self.get(role_key, [])
        return any(role.name in allowed_roles for role in member.roles)

    def can_use_command(self, member: discord.Member, command_name: str) -> bool:
        """Check if member can use a specific command"""
        # Check if command is restricted
        admin_only = self.get("guild_settings.restricted_commands.admin_only", [])
        mod_only = self.get("guild_settings.restricted_commands.mod_only", [])

        if command_name in admin_only:
            return self.is_admin(member)
        elif command_name in mod_only:
            return self.is_moderator(member)

        return True  # Default to allow if no specific restriction

    def get_color(self, color_name: str) -> int:
        """Get color from palette"""
        return self.get(f"bot_settings.color_palette.{color_name}", 0x5865F2)

    def is_feature_enabled(self, feature_path: str) -> bool:
        """Check if a feature is enabled"""
        return self.get(f"features.{feature_path}.enabled", False)

    def get_allowed_channels(self, feature: str, guild_id: int = None) -> List[int]:
        """Get allowed channels for a feature"""
        if guild_id and guild_id in self.guild_configs:
            guild_channels = (
                self.guild_configs[guild_id]
                .get("allowed_channels", {})
                .get(feature, [])
            )
            if guild_channels:
                return guild_channels

        return self.get(f"channels.allowed_channels.{feature}", [])

    def is_channel_allowed(self, channel: discord.TextChannel, feature: str) -> bool:
        """Check if channel is allowed for a feature"""
        allowed_channels = self.get_allowed_channels(feature, channel.guild.id)

        # If no restrictions, allow all channels
        if not allowed_channels:
            return True

        return channel.id in allowed_channels

    def load_guild_config(self, guild_id: int) -> Dict[str, Any]:
        """Load guild-specific configuration"""
        guild_config_file = Path(f"data/guilds/{guild_id}_config.json")

        if guild_config_file.exists():
            try:
                with open(guild_config_file, "r") as f:
                    config = json.load(f)
                    self.guild_configs[guild_id] = config
                    return config
            except Exception as e:
                print(f"Error loading guild config for {guild_id}: {e}")

        # Return default guild config
        default_config = {
            "guild_id": guild_id,
            "setup_completed": False,
            "allowed_channels": {},
            "custom_roles": [],
            "features": {
                "quiz_system": {"enabled": True, "daily_questions": True},
                "space_content": {"enabled": True, "daily_apod": True},
                "stellaris_features": {"enabled": True},
            },
            "channels": {
                "quiz_channel": None,
                "space_channel": None,
                "stellaris_channel": None,
                "log_channel": None,
            },
            "created_at": datetime.utcnow().isoformat(),
        }

        self.guild_configs[guild_id] = default_config
        self.save_guild_config(guild_id)  # Save the default config
        return default_config

    def save_guild_config(self, guild_id: int) -> bool:
        """Save guild-specific configuration"""
        if guild_id not in self.guild_configs:
            return False

        guild_config_file = Path(f"data/guilds/{guild_id}_config.json")
        guild_config_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(guild_config_file, "w") as f:
                json.dump(self.guild_configs[guild_id], f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving guild config for {guild_id}: {e}")
            return False

    def set_guild_setting(self, guild_id: int, key_path: str, value: Any) -> bool:
        """Set guild-specific setting"""
        if guild_id not in self.guild_configs:
            self.load_guild_config(guild_id)

        keys = key_path.split(".")
        config_section = self.guild_configs[guild_id]

        try:
            for key in keys[:-1]:
                if key not in config_section:
                    config_section[key] = {}
                config_section = config_section[key]

            config_section[keys[-1]] = value
            return self.save_guild_config(guild_id)
        except Exception as e:
            print(f"Error setting guild config value: {e}")
            return False

    def get_guild_setting(
        self, guild_id: int, key_path: str, default: Any = None
    ) -> Any:
        """Get guild-specific setting"""
        if guild_id not in self.guild_configs:
            self.load_guild_config(guild_id)

        keys = key_path.split(".")
        value = self.guild_configs.get(guild_id, {})

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def add_allowed_channel(self, guild_id: int, feature: str, channel_id: int) -> bool:
        """Add allowed channel for a feature"""
        current_channels = self.get_guild_setting(
            guild_id, f"allowed_channels.{feature}", []
        )
        if channel_id not in current_channels:
            current_channels.append(channel_id)
            return self.set_guild_setting(
                guild_id, f"allowed_channels.{feature}", current_channels
            )
        return True

    def remove_allowed_channel(
        self, guild_id: int, feature: str, channel_id: int
    ) -> bool:
        """Remove allowed channel for a feature"""
        current_channels = self.get_guild_setting(
            guild_id, f"allowed_channels.{feature}", []
        )
        if channel_id in current_channels:
            current_channels.remove(channel_id)
            return self.set_guild_setting(
                guild_id, f"allowed_channels.{feature}", current_channels
            )
        return True

    def get_emoji(self, emoji_name: str) -> str:
        """Get emoji from configuration"""
        return self.get(f"ui_components.custom_emojis.{emoji_name}", "❓")

    def validate_permissions(
        self, interaction: discord.Interaction, required_permission: str
    ) -> bool:
        """Validate if user has required permissions for command"""
        if not interaction.guild:
            return False

        member = interaction.user

        # Bot owner always has permission
        if interaction.client.application:
            if member.id == interaction.client.application.owner.id:
                return True

        # Check specific permission types
        if required_permission == "admin":
            return self.is_admin(member)
        elif required_permission == "moderator":
            return self.is_moderator(member)
        elif required_permission.endswith("_master"):
            return self.has_role_permission(
                member, required_permission.replace("_master", "")
            )

        return True  # Default to allow if no specific restriction

    def validate_config(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []

        # Check basic settings
        if not self.get("bot_settings.name"):
            errors.append("Bot name is not set")

        # Check required roles
        if not self.get("permissions.admin_roles"):
            errors.append("No admin roles defined")

        return errors

    def ensure_directories(self) -> None:
        """Create required directories if they don't exist"""
        directories = [
            "data/guilds",
            "data/quiz",
            "data/users",
            "logs",
            "temp",
            "temp/notion_cache",
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)


# Create global config manager instance
config_manager = ConfigManager()


# Permission check functions for slash commands
def admin_only():
    """Slash command check for admin permissions"""

    async def predicate(interaction: discord.Interaction) -> bool:
        # Bot owner always has permission
        if (
            interaction.client.application
            and interaction.user.id == interaction.client.application.owner.id
        ):
            return True

        # Administrator permission check
        if interaction.user.guild_permissions.administrator:
            return True

        # Role-based permission check
        admin_roles = config_manager.get("permissions.admin_roles", [])
        if any(role.name in admin_roles for role in interaction.user.roles):
            return True

        # Permission denied
        await interaction.response.send_message(
            "❌ You need administrator permissions to use this command.", ephemeral=True
        )
        return False

    return app_commands.check(predicate)


def mod_only():
    """Slash command check for moderator permissions"""

    async def predicate(interaction: discord.Interaction) -> bool:
        # Check admin permission first (includes bot owner)
        if (
            interaction.client.application
            and interaction.user.id == interaction.client.application.owner.id
        ):
            return True

        if interaction.user.guild_permissions.administrator:
            return True

        admin_roles = config_manager.get("permissions.admin_roles", [])
        if any(role.name in admin_roles for role in interaction.user.roles):
            return True

        # Check moderator roles
        mod_roles = config_manager.get("permissions.moderator_roles", [])
        if any(role.name in mod_roles for role in interaction.user.roles):
            return True

        # Permission denied
        await interaction.response.send_message(
            "❌ You need moderator permissions to use this command.", ephemeral=True
        )
        return False

    return app_commands.check(predicate)


def feature_enabled(feature_path: str):
    """Slash command check for feature toggle"""

    async def predicate(interaction: discord.Interaction) -> bool:
        # Check if feature is enabled globally
        if not config_manager.is_feature_enabled(feature_path):
            # Check guild-specific setting
            guild_enabled = config_manager.get_guild_setting(
                interaction.guild.id, f"features.{feature_path}.enabled", False
            )

            if not guild_enabled:
                await interaction.response.send_message(
                    f"❌ The `{feature_path}` feature is currently disabled.",
                    ephemeral=True,
                )
                return False

        return True

    return app_commands.check(predicate)


def channel_only(feature: str):
    """Slash command check for channel restrictions"""

    async def predicate(interaction: discord.Interaction) -> bool:
        # Admin bypass
        if config_manager.is_admin(interaction.user):
            return True

        # Check if channel is allowed
        allowed_channels = config_manager.get_allowed_channels(
            feature, interaction.guild.id
        )
        if allowed_channels and interaction.channel.id not in allowed_channels:
            channel_mentions = [
                f"<#{channel_id}>" for channel_id in allowed_channels[:3]
            ]

            await interaction.response.send_message(
                f"❌ This command can only be used in: {', '.join(channel_mentions)}",
                ephemeral=True,
            )
            return False

        return True

    return app_commands.check(predicate)
