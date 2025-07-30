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
from datetime import datetime

class ConfigManager:
    """Advanced configuration manager with role-based permissions"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
        self.guild_configs = {}  # Per-guild configurations
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        if not self.config_file.exists():
            self.create_default_config()
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading config: {e}")
            return self.get_default_config()
    
    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def create_default_config(self):
        """Create default configuration file"""
        default_config = self.get_default_config()
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration structure"""
        return {
            "bot_settings": {
                "name": "Astra",
                "version": "1.0.0",
                "prefix": "!",
                "description": "An advanced Discord bot for space exploration and Stellaris roleplay",
                "activity": "the cosmos | !help",
                "color_palette": {
                    "primary": 0x5865F2,
                    "space": 0x1E1F23,
                    "stellaris": 0x6a0dad,
                    "success": 0x00FF00,
                    "error": 0xFF0000,
                    "warning": 0xFF9900,
                    "info": 0x0099FF
                }
            },
            "permissions": {
                "admin_roles": ["Admin", "Administrator", "Owner"],
                "moderator_roles": ["Mod", "Moderator", "Staff"],
                "quiz_master_roles": ["Quiz Master"],
                "space_expert_roles": ["Space Expert"],
                "stellaris_leader_roles": ["Empire Leader"]
            },
            "features": {
                "quiz_system": {"enabled": True},
                "space_content": {"enabled": True},
                "stellaris_features": {"enabled": True},
                "notion_integration": {"enabled": False}
            },
            "development": {
                "debug_mode": False
            },
            "ui_components": {
                "custom_emojis": {
                    "error": "❌",
                    "success": "✅",
                    "warning": "⚠️",
                    "info": "ℹ️"
                }
            }
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'bot_settings.name')"""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> bool:
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config_section = self.config
        
        try:
            for key in keys[:-1]:
                if key not in config_section:
                    config_section[key] = {}
                config_section = config_section[key]
            
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
            guild_channels = self.guild_configs[guild_id].get("allowed_channels", {}).get(feature, [])
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
                with open(guild_config_file, 'r') as f:
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
            "features": {},
            "created_at": datetime.utcnow().isoformat()
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
            with open(guild_config_file, 'w') as f:
                json.dump(self.guild_configs[guild_id], f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving guild config for {guild_id}: {e}")
            return False
    
    def set_guild_setting(self, guild_id: int, key_path: str, value: Any) -> bool:
        """Set guild-specific setting"""
        if guild_id not in self.guild_configs:
            self.load_guild_config(guild_id)
        
        keys = key_path.split('.')
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
    
    def get_guild_setting(self, guild_id: int, key_path: str, default: Any = None) -> Any:
        """Get guild-specific setting"""
        if guild_id not in self.guild_configs:
            self.load_guild_config(guild_id)
        
        keys = key_path.split('.')
        value = self.guild_configs.get(guild_id, {})
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def add_allowed_channel(self, guild_id: int, feature: str, channel_id: int) -> bool:
        """Add allowed channel for a feature"""
        current_channels = self.get_guild_setting(guild_id, f"allowed_channels.{feature}", [])
        if channel_id not in current_channels:
            current_channels.append(channel_id)
            return self.set_guild_setting(guild_id, f"allowed_channels.{feature}", current_channels)
        return True
    
    def remove_allowed_channel(self, guild_id: int, feature: str, channel_id: int) -> bool:
        """Remove allowed channel for a feature"""
        current_channels = self.get_guild_setting(guild_id, f"allowed_channels.{feature}", [])
        if channel_id in current_channels:
            current_channels.remove(channel_id)
            return self.set_guild_setting(guild_id, f"allowed_channels.{feature}", current_channels)
        return True
    
    def get_emoji(self, emoji_name: str) -> str:
        """Get emoji from configuration"""
        return self.get(f"ui_components.custom_emojis.{emoji_name}", "❓")
    
    def validate_permissions(self, ctx: commands.Context, required_permission: str) -> bool:
        """Validate if user has required permissions for command"""
        if not ctx.guild:
            return False
        
        member = ctx.author
        
        # Bot owner always has permission
        application_info = ctx.bot.application
        if application_info and application_info.owner and member.id == application_info.owner.id:
            return True
        
        # Check specific permission types
        if required_permission == "admin":
            return self.is_admin(member)
        elif required_permission == "moderator":
            return self.is_moderator(member)
        elif required_permission.endswith("_master"):
            return self.has_role_permission(member, required_permission.replace("_master", ""))
        
        return True  # Default to allow if no specific restriction
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        # Check basic settings
        if not self.get("bot_settings.prefix"):
            errors.append("Bot prefix is not set")
        
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
            "temp"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)


# Create global config manager instance
config_manager = ConfigManager()

# Decorator for role-based command restrictions
def require_permission(permission_type: str):
    """Decorator to require specific permissions for commands"""
    def decorator(func):
        async def wrapper(self, ctx: commands.Context, *args, **kwargs):
            if not config_manager.validate_permissions(ctx, permission_type):
                embed = discord.Embed(
                    title="🚫 Access Denied",
                    description=f"You need `{permission_type}` permissions to use this command.",
                    color=config_manager.get_color("error")
                )
                await ctx.send(embed=embed, delete_after=10)
                return
            
            return await func(self, ctx, *args, **kwargs)
        return wrapper
    return decorator

def require_channel(feature: str):
    """Decorator to restrict commands to specific channels"""
    def decorator(func):
        async def wrapper(self, ctx: commands.Context, *args, **kwargs):
            if not config_manager.is_channel_allowed(ctx.channel, feature):
                allowed_channels = config_manager.get_allowed_channels(feature, ctx.guild.id)
                if allowed_channels:
                    channel_mentions = [f"<#{channel_id}>" for channel_id in allowed_channels[:3]]
                    embed = discord.Embed(
                        title="🚫 Wrong Channel",
                        description=f"This command can only be used in: {', '.join(channel_mentions)}",
                        color=config_manager.get_color("warning")
                    )
                    await ctx.send(embed=embed, delete_after=10)
                    return
            
            return await func(self, ctx, *args, **kwargs)
        return wrapper
    return decorator

def feature_enabled(feature_path: str):
    """Decorator to check if feature is enabled"""
    def decorator(func):
        async def wrapper(self, ctx: commands.Context, *args, **kwargs):
            if not config_manager.is_feature_enabled(feature_path):
                embed = discord.Embed(
                    title="🚫 Feature Disabled",
                    description=f"The `{feature_path}` feature is currently disabled.",
                    color=config_manager.get_color("warning")
                )
                await ctx.send(embed=embed, delete_after=10)
                return
            
            return await func(self, ctx, *args, **kwargs)
        return wrapper
    return decorator