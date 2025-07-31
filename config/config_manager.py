"""
Enhanced Configuration Manager for Astra Bot
Handles JSON configuration, role-based permissions, and guild-specific settings
"""

import json
import os
import shutil
import time
import threading
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
import discord
from discord import app_commands
from datetime import datetime


class ConfigManager:
    """Advanced configuration manager with role-based permissions"""

    # Configuration version for potential future migrations
    CONFIG_VERSION = "1.0.0"

    def __init__(self, config_file: str = "config/config.json"):
        self.config_file = Path(config_file)
        self.config_lock = threading.RLock()  # Thread safety for config operations
        self.guild_locks = {}  # Per-guild locks for thread safety

        # Setup logging
        self.logger = logging.getLogger("astra.config")

        # Load configuration
        self.config = self.load_config()
        self.guild_configs = {}  # Per-guild configurations

        # Last operation timestamps (for rate limiting)
        self.last_save_time = 0

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file with enhanced error handling"""
        if not self.config_file.exists():
            self.create_default_config()

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config_data = json.load(f)

                # Add version if not present
                if "version" not in config_data:
                    config_data["version"] = self.CONFIG_VERSION

                return config_data
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in config file: {e}")
            # Create backup of corrupted file
            self._backup_corrupted_file()
            return self.get_default_config()
        except FileNotFoundError as e:
            self.logger.error(f"Config file not found: {e}")
            return self.get_default_config()
        except Exception as e:
            self.logger.error(f"Unexpected error loading config: {e}")
            return self.get_default_config()

    def _backup_corrupted_file(self):
        """Create backup of corrupted configuration file"""
        if not self.config_file.exists():
            return

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.config_file.with_suffix(f".corrupted_{timestamp}.json")
            shutil.copy2(self.config_file, backup_path)
            self.logger.info(f"Created backup of corrupted config: {backup_path}")
        except Exception as e:
            self.logger.error(f"Failed to create backup of corrupted config: {e}")

    def save_config(self) -> bool:
        """Save current configuration to file with rate limiting and atomic writes"""
        # Rate limiting to prevent excessive writes
        current_time = time.time()
        if current_time - self.last_save_time < 1.0:  # Minimum 1 second between saves
            time.sleep(0.1)  # Small delay

        self.last_save_time = current_time

        with self.config_lock:
            try:
                # Ensure directory exists
                self.config_file.parent.mkdir(parents=True, exist_ok=True)

                # Write to temporary file first (atomic write)
                temp_file = self.config_file.with_suffix(".tmp")
                with open(temp_file, "w", encoding="utf-8") as f:
                    json.dump(self.config, f, indent=2)

                # Rename temporary file to actual file (atomic operation)
                temp_file.replace(self.config_file)
                return True
            except Exception as e:
                self.logger.error(f"Error saving config: {e}")
                return False

    def create_default_config(self):
        """Create default configuration file"""
        default_config = self.get_default_config()

        # Ensure directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2)

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration structure"""
        return {
            "version": self.CONFIG_VERSION,
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
        with self.config_lock:
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
        with self.config_lock:
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
                self.logger.error(f"Error setting config value: {e}")
                return False

    def is_admin(self, member: discord.Member) -> bool:
        """Check if member has admin permissions"""
        # Return True early if member has administrator permission
        if member.guild_permissions.administrator:
            return True

        # Otherwise check role names
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
        # Admins always have permission
        if self.is_admin(member):
            return True

        # Safely get role key
        role_key = f"permissions.{permission_type}_roles"
        allowed_roles = self.get(role_key, [])

        # Check if member has any of the allowed roles
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
        """Get color from palette with fallback to primary color"""
        default_color = 0x5865F2  # Discord Blurple as ultimate fallback
        primary_color = self.get("bot_settings.color_palette.primary", default_color)
        return self.get(f"bot_settings.color_palette.{color_name}", primary_color)

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
        # Safety check for None channel
        if not channel:
            return False

        allowed_channels = self.get_allowed_channels(feature, channel.guild.id)

        # If no restrictions, allow all channels
        if not allowed_channels:
            return True

        return channel.id in allowed_channels

    def _get_guild_lock(self, guild_id: int) -> threading.RLock:
        """Get or create a lock for guild-specific operations"""
        if guild_id not in self.guild_locks:
            self.guild_locks[guild_id] = threading.RLock()
        return self.guild_locks[guild_id]

    def load_guild_config(self, guild_id: int) -> Dict[str, Any]:
        """Load guild-specific configuration"""
        with self._get_guild_lock(guild_id):
            guild_config_file = Path(f"data/guilds/{guild_id}_config.json")

            if guild_config_file.exists():
                try:
                    with open(guild_config_file, "r", encoding="utf-8") as f:
                        config = json.load(f)
                        self.guild_configs[guild_id] = config
                        return config
                except json.JSONDecodeError as e:
                    self.logger.error(f"Invalid JSON in guild config {guild_id}: {e}")
                    # Create backup of corrupted guild config
                    self._backup_corrupted_guild_config(guild_id, guild_config_file)
                except Exception as e:
                    self.logger.error(f"Error loading guild config for {guild_id}: {e}")

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

    def _backup_corrupted_guild_config(self, guild_id: int, config_path: Path):
        """Create backup of corrupted guild configuration file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = config_path.with_suffix(f".corrupted_{timestamp}.json")
            shutil.copy2(config_path, backup_path)
            self.logger.info(
                f"Created backup of corrupted guild config {guild_id}: {backup_path}"
            )
        except Exception as e:
            self.logger.error(
                f"Failed to create backup of corrupted guild config {guild_id}: {e}"
            )

    def save_guild_config(self, guild_id: int) -> bool:
        """Save guild-specific configuration"""
        with self._get_guild_lock(guild_id):
            if guild_id not in self.guild_configs:
                return False

            guild_config_file = Path(f"data/guilds/{guild_id}_config.json")
            guild_config_file.parent.mkdir(parents=True, exist_ok=True)

            try:
                # Write to temporary file first (atomic write)
                temp_file = guild_config_file.with_suffix(f".{guild_id}.tmp")
                with open(temp_file, "w", encoding="utf-8") as f:
                    json.dump(self.guild_configs[guild_id], f, indent=2)

                # Rename temporary file to actual file (atomic operation)
                temp_file.replace(guild_config_file)
                return True
            except Exception as e:
                self.logger.error(f"Error saving guild config for {guild_id}: {e}")
                return False

    def set_guild_setting(self, guild_id: int, key_path: str, value: Any) -> bool:
        """Set guild-specific setting"""
        with self._get_guild_lock(guild_id):
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
                self.logger.error(f"Error setting guild config value: {e}")
                return False

    def get_guild_setting(
        self, guild_id: int, key_path: str, default: Any = None
    ) -> Any:
        """Get guild-specific setting"""
        with self._get_guild_lock(guild_id):
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
        with self._get_guild_lock(guild_id):
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
        with self._get_guild_lock(guild_id):
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
            if (
                interaction.client.application.owner
                and member.id == interaction.client.application.owner.id
            ):
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

        # Check color palette
        if not self.get("bot_settings.color_palette"):
            errors.append("Color palette is missing")

        # Check version
        if self.get("version") != self.CONFIG_VERSION:
            errors.append(
                f"Config version mismatch: expected {self.CONFIG_VERSION}, found {self.get('version', 'not set')}"
            )

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
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.logger.error(f"Failed to create directory {directory}: {e}")

    def create_backup(self) -> Tuple[bool, str]:
        """Create a backup of the current configuration"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)

            backup_file = backup_dir / f"config_backup_{timestamp}.json"

            with open(self.config_file, "r", encoding="utf-8") as src:
                with open(backup_file, "w", encoding="utf-8") as dst:
                    dst.write(src.read())

            return True, str(backup_file)
        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            return False, str(e)

    def repair_config(self) -> bool:
        """Attempt to repair configuration by filling in missing fields"""
        try:
            default_config = self.get_default_config()

            # Recursive function to update missing fields
            def update_missing(target, source):
                for key, value in source.items():
                    if key not in target:
                        target[key] = value
                    elif isinstance(value, dict) and isinstance(target[key], dict):
                        update_missing(target[key], value)

            with self.config_lock:
                update_missing(self.config, default_config)
                self.config["version"] = self.CONFIG_VERSION
                return self.save_config()
        except Exception as e:
            self.logger.error(f"Config repair failed: {e}")
            return False


# Create global config manager instance
config_manager = ConfigManager()
