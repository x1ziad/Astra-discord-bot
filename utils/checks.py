"""
Custom check decorators for Astra Discord Bot
Includes feature checks, permission checks, and cooldown handling
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Callable, Union, TypeVar
import functools

from config.unified_config import unified_config as config_manager

T = TypeVar("T")


def feature_enabled(feature_path: str):
    """
    Check if a feature is enabled in configuration

    Args:
        feature_path: The path to the feature in config (e.g. "space_content.iss_tracking")

    Usage:
        @feature_enabled("space_content")
        @app_commands.command()
        async def space_command(self, interaction):
            ...
    """

    async def predicate(interaction) -> bool:
        if not config_manager.is_feature_enabled(feature_path):
            # Check if the user is an admin and in development mode
            if (
                config_manager.get("development.debug_mode", False)
                and interaction.user.guild_permissions.administrator
            ):
                return True

            # Feature is disabled
            feature_name = feature_path.split(".")[-1].replace("_", " ").title()
            raise app_commands.CheckFailure(
                f"The {feature_name} feature is currently disabled."
            )
        return True

    return app_commands.check(predicate)


def guild_admin_only():
    """Check that restricts commands to guild administrators only"""

    async def predicate(interaction) -> bool:
        if not interaction.guild:
            return False  # Not in a guild

        return interaction.user.guild_permissions.administrator

    return app_commands.check(predicate)


def bot_owner_only():
    """Check that restricts commands to the bot owner only"""

    async def predicate(interaction) -> bool:
        bot_owner_id = config_manager.get("bot_settings.owner_id")
        if bot_owner_id and str(interaction.user.id) == str(bot_owner_id):
            return True

        # Check application owner
        app = interaction.client.application
        if app and app.owner and app.owner.id == interaction.user.id:
            return True

        return False

    return app_commands.check(predicate)


def channel_only(feature_name: str):
    """
    Decorator that restricts commands to specific channels

    Args:
        feature_name: The feature to check allowed channels for
    """

    async def predicate(interaction) -> bool:
        # Check if the channel is allowed for this feature
        if not interaction.guild or not interaction.channel:
            return True  # Allow in DMs or when channel is None

        # Get the channel ID for this feature
        guild_id = interaction.guild.id if interaction.guild else None
        channel_id = config_manager.get_guild_setting(
            guild_id, f"channels.{feature_name}_channel"
        )
        allowed_channels = config_manager.get_guild_setting(
            guild_id, f"channels.allowed_channels.{feature_name}", []
        )

        # Allow if no restrictions are set or if current channel is allowed
        if not channel_id and not allowed_channels:
            return True

        if str(interaction.channel.id) == str(channel_id) or str(
            interaction.channel.id
        ) in map(str, allowed_channels):
            return True
        else:
            # Tell user where to use the command
            if channel_id:
                await interaction.response.send_message(
                    f"❌ This command can only be used in <#{channel_id}>",
                    ephemeral=True,
                )
            elif allowed_channels:
                channels_text = ", ".join([f"<#{ch}>" for ch in allowed_channels[:3]])
                if len(allowed_channels) > 3:
                    channels_text += f" and {len(allowed_channels) - 3} more channels"
                await interaction.response.send_message(
                    f"❌ This command can only be used in the following channels: {channels_text}",
                    ephemeral=True,
                )
            return False

    return app_commands.check(predicate)


# Custom cooldown for application commands
def cooldown(
    rate: int,
    per: float,
    key: Optional[Callable[[discord.Interaction], str]] = None,
    # Use commands.BucketType instead of app_commands.BucketType
    key_type: commands.BucketType = commands.BucketType.user,
):
    """
    Custom cooldown decorator for application commands
    Provides more flexibility than the built-in cooldown

    Args:
        rate: Number of calls allowed within period
        per: Cooldown period in seconds
        key: Optional function to customize the cooldown key
        key_type: Type of bucket to use for cooldown
    """
    # Use the built-in app_commands cooldown
    return app_commands.checks.cooldown(rate, per)


# For traditional commands
def traditional_cooldown(
    rate: int, per: float, bucket_type: commands.BucketType = commands.BucketType.user
):
    """Cooldown for traditional commands"""
    return commands.cooldown(rate, per, bucket_type)
