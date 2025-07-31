"""
Advanced command checks for Astra Bot
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Callable, TypeVar, Union, Optional

from config.config_manager import config_manager

T = TypeVar("T")


def is_owner_or_admin():
    """Check if user is the bot owner or a server admin"""

    async def predicate(interaction: discord.Interaction) -> bool:
        # Bot owner check
        if interaction.client.application:
            if interaction.user.id == interaction.client.application.owner.id:
                return True

        # Admin check
        if interaction.user.guild_permissions.administrator:
            return True

        # Role check
        admin_roles = config_manager.get("permissions.admin_roles", [])
        if any(role.name in admin_roles for role in interaction.user.roles):
            return True

        # Permission denied
        await interaction.response.send_message(
            "❌ This command requires administrator permissions.", ephemeral=True
        )
        return False

    return app_commands.check(predicate)


def is_moderator_or_above():
    """Check if user is a moderator, admin, or bot owner"""

    async def predicate(interaction: discord.Interaction) -> bool:
        # First check if user is owner or admin
        try:
            # Bot owner check
            if interaction.client.application:
                if interaction.user.id == interaction.client.application.owner.id:
                    return True

            # Admin check
            if interaction.user.guild_permissions.administrator:
                return True

            admin_roles = config_manager.get("permissions.admin_roles", [])
            if any(role.name in admin_roles for role in interaction.user.roles):
                return True

            # Mod check
            mod_roles = config_manager.get("permissions.moderator_roles", [])
            if any(role.name in mod_roles for role in interaction.user.roles):
                return True
        except:
            # If any error occurs, default to permissions check
            if interaction.user.guild_permissions.manage_messages:
                return True

        # Permission denied
        await interaction.response.send_message(
            "❌ This command requires moderator permissions.", ephemeral=True
        )
        return False

    return app_commands.check(predicate)


def has_role(role_name: str):
    """Check if user has a specific role"""

    async def predicate(interaction: discord.Interaction) -> bool:
        # Admin bypass
        if interaction.user.guild_permissions.administrator:
            return True

        if any(role.name == role_name for role in interaction.user.roles):
            return True

        # Permission denied
        await interaction.response.send_message(
            f"❌ This command requires the `{role_name}` role.", ephemeral=True
        )
        return False

    return app_commands.check(predicate)


def has_any_role(role_names: list):
    """Check if user has any of the specified roles"""

    async def predicate(interaction: discord.Interaction) -> bool:
        # Admin bypass
        if interaction.user.guild_permissions.administrator:
            return True

        if any(role.name in role_names for role in interaction.user.roles):
            return True

        # Permission denied
        await interaction.response.send_message(
            f"❌ This command requires one of these roles: {', '.join(role_names)}",
            ephemeral=True,
        )
        return False

    return app_commands.check(predicate)


def in_channel(channel_ids: Union[int, list]):
    """Check if command is used in specific channel(s)"""
    if isinstance(channel_ids, int):
        channel_ids = [channel_ids]

    async def predicate(interaction: discord.Interaction) -> bool:
        # Admin bypass
        if interaction.user.guild_permissions.administrator:
            return True

        if interaction.channel_id in channel_ids:
            return True

        # Get channel mentions for error message
        channel_mentions = []
        for channel_id in channel_ids:
            channel_mentions.append(f"<#{channel_id}>")

        # Permission denied
        await interaction.response.send_message(
            f"❌ This command can only be used in: {', '.join(channel_mentions)}",
            ephemeral=True,
        )
        return False

    return app_commands.check(predicate)


def is_feature_enabled(feature_path: str):
    """Check if a feature is enabled"""

    async def predicate(interaction: discord.Interaction) -> bool:
        # Admin bypass for testing
        if interaction.client.application:
            if interaction.user.id == interaction.client.application.owner.id:
                return True

        # Check global setting
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


def cooldown(
    rate: int,
    per: float,
    key_type: app_commands.BucketType = app_commands.BucketType.user,
):
    """Custom cooldown with better error message"""
    cooldown_mapping = app_commands.Cooldown(rate, per)

    async def predicate(interaction: discord.Interaction) -> bool:
        # Get the cooldown key based on type
        if key_type == app_commands.BucketType.user:
            key = interaction.user.id
        elif key_type == app_commands.BucketType.guild:
            key = interaction.guild.id
        elif key_type == app_commands.BucketType.channel:
            key = interaction.channel.id
        else:
            key = interaction.user.id

        # Try to acquire the cooldown
        retry_after = cooldown_mapping.get_retry_after()
        if retry_after:
            # Format the remaining time
            if retry_after < 1:
                time_str = f"{retry_after*1000:.0f} milliseconds"
            elif retry_after < 60:
                time_str = f"{retry_after:.1f} seconds"
            elif retry_after < 3600:
                minutes, seconds = divmod(retry_after, 60)
                time_str = f"{int(minutes)}m {int(seconds)}s"
            else:
                hours, remainder = divmod(retry_after, 3600)
                minutes, seconds = divmod(remainder, 60)
                time_str = f"{int(hours)}h {int(minutes)}m"

            # Send cooldown message
            await interaction.response.send_message(
                f"⏱️ Command on cooldown. Please wait {time_str}.", ephemeral=True
            )
            return False

        # Update the cooldown
        cooldown_mapping.update_rate_limit()
        return True

    return app_commands.check(predicate)
