"""
Permission system for Astra Bot
Provides role-based access control and permission checking
"""

import discord
from discord.ext import commands
from enum import Enum
from typing import Union, List, Optional, Callable, Any
import logging

logger = logging.getLogger("astra.permissions")


class PermissionLevel(Enum):
    """Permission levels for commands and features"""

    EVERYONE = 0
    TRUSTED = 1
    MODERATOR = 2
    ADMINISTRATOR = 3
    OWNER = 4


class PermissionManager:
    """Manages permissions and access control"""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logger

        # Permission overrides per guild
        self.guild_permissions: dict = {}

        # Role mappings for permission levels
        self.default_role_mappings = {
            PermissionLevel.MODERATOR: ["moderator", "mod", "staff"],
            PermissionLevel.ADMINISTRATOR: ["administrator", "admin", "owner"],
        }

    async def check_permission(
        self,
        user: Union[discord.Member, discord.User],
        level: PermissionLevel,
        guild: Optional[discord.Guild] = None,
    ) -> bool:
        """Check if user has required permission level"""

        # Bot owner always has all permissions
        if await self.is_bot_owner(user):
            return True

        # DM context - only owner and trusted users
        if not guild:
            return level <= PermissionLevel.TRUSTED

        # Ensure user is a member of the guild
        if not isinstance(user, discord.Member):
            member = guild.get_member(user.id)
            if not member:
                return False
            user = member

        # Check permission level
        if level == PermissionLevel.EVERYONE:
            return True

        elif level == PermissionLevel.TRUSTED:
            return await self._check_trusted(user, guild)

        elif level == PermissionLevel.MODERATOR:
            return await self._check_moderator(user, guild)

        elif level == PermissionLevel.ADMINISTRATOR:
            return await self._check_administrator(user, guild)

        elif level == PermissionLevel.OWNER:
            return await self.is_bot_owner(user)

        return False

    async def is_bot_owner(self, user: Union[discord.Member, discord.User]) -> bool:
        """Check if user is the bot owner"""
        try:
            app_info = await self.bot.application_info()
            return user.id == app_info.owner.id
        except Exception as e:
            self.logger.error(f"Error checking bot owner: {e}")
            return False

    async def _check_trusted(self, user: discord.Member, guild: discord.Guild) -> bool:
        """Check if user has trusted permissions"""
        # Administrators and moderators are automatically trusted
        if await self._check_moderator(user, guild):
            return True

        # Check for specific trusted roles
        trusted_roles = await self._get_guild_permission_roles(
            guild.id, PermissionLevel.TRUSTED
        )
        user_role_names = [role.name.lower() for role in user.roles]

        return any(role.lower() in user_role_names for role in trusted_roles)

    async def _check_moderator(
        self, user: discord.Member, guild: discord.Guild
    ) -> bool:
        """Check if user has moderator permissions"""
        # Administrators are automatically moderators
        if await self._check_administrator(user, guild):
            return True

        # Check Discord permissions
        if (
            user.guild_permissions.manage_messages
            or user.guild_permissions.kick_members
        ):
            return True

        # Check for moderator roles
        mod_roles = await self._get_guild_permission_roles(
            guild.id, PermissionLevel.MODERATOR
        )
        user_role_names = [role.name.lower() for role in user.roles]

        return any(role.lower() in user_role_names for role in mod_roles)

    async def _check_administrator(
        self, user: discord.Member, guild: discord.Guild
    ) -> bool:
        """Check if user has administrator permissions"""
        # Check Discord permissions
        if user.guild_permissions.administrator:
            return True

        # Check if user is guild owner
        if user.id == guild.owner_id:
            return True

        # Check for admin roles
        admin_roles = await self._get_guild_permission_roles(
            guild.id, PermissionLevel.ADMINISTRATOR
        )
        user_role_names = [role.name.lower() for role in user.roles]

        return any(role.lower() in user_role_names for role in admin_roles)

    async def _get_guild_permission_roles(
        self, guild_id: int, level: PermissionLevel
    ) -> List[str]:
        """Get role names for a permission level in a guild"""
        # Get custom roles from database/config
        guild_perms = self.guild_permissions.get(guild_id, {})
        custom_roles = guild_perms.get(level.name.lower(), [])

        # Combine with default roles
        default_roles = self.default_role_mappings.get(level, [])

        return custom_roles + default_roles

    async def set_guild_permission_roles(
        self, guild_id: int, level: PermissionLevel, roles: List[str]
    ):
        """Set custom permission roles for a guild"""
        if guild_id not in self.guild_permissions:
            self.guild_permissions[guild_id] = {}

        self.guild_permissions[guild_id][level.name.lower()] = roles
        self.logger.info(f"Updated {level.name} roles for guild {guild_id}: {roles}")

    def get_user_permission_level(
        self,
        user: Union[discord.Member, discord.User],
        guild: Optional[discord.Guild] = None,
    ) -> PermissionLevel:
        """Get the highest permission level for a user"""
        if not guild or not isinstance(user, discord.Member):
            return PermissionLevel.EVERYONE

        # Check from highest to lowest
        for level in [
            PermissionLevel.OWNER,
            PermissionLevel.ADMINISTRATOR,
            PermissionLevel.MODERATOR,
            PermissionLevel.TRUSTED,
        ]:
            if asyncio.create_task(self.check_permission(user, level, guild)):
                return level

        return PermissionLevel.EVERYONE


# Global permission manager
permission_manager = None


def has_permission(level: PermissionLevel):
    """Decorator to check permissions for commands"""

    def predicate(ctx_or_interaction):
        if isinstance(ctx_or_interaction, commands.Context):
            user = ctx_or_interaction.author
            guild = ctx_or_interaction.guild
        else:  # Interaction
            user = ctx_or_interaction.user
            guild = ctx_or_interaction.guild

        if permission_manager is None:
            return True  # Allow if permission manager not set up

        return asyncio.create_task(
            permission_manager.check_permission(user, level, guild)
        )

    if hasattr(commands, "check"):
        return commands.check(predicate)
    else:
        # For app commands
        async def app_predicate(interaction):
            if permission_manager is None:
                return True
            return await permission_manager.check_permission(
                interaction.user, level, interaction.guild
            )

        return discord.app_commands.check(app_predicate)


def setup_permissions(bot):
    """Set up the global permission manager"""
    global permission_manager
    permission_manager = PermissionManager(bot)
    return permission_manager


# Permission check functions for backwards compatibility
async def is_owner(ctx_or_interaction) -> bool:
    """Check if user is bot owner"""
    if permission_manager is None:
        return False

    if isinstance(ctx_or_interaction, commands.Context):
        user = ctx_or_interaction.author
    else:
        user = ctx_or_interaction.user

    return await permission_manager.is_bot_owner(user)


async def is_admin(ctx_or_interaction) -> bool:
    """Check if user is administrator"""
    if permission_manager is None:
        return False

    if isinstance(ctx_or_interaction, commands.Context):
        user = ctx_or_interaction.author
        guild = ctx_or_interaction.guild
    else:
        user = ctx_or_interaction.user
        guild = ctx_or_interaction.guild

    return await permission_manager.check_permission(
        user, PermissionLevel.ADMINISTRATOR, guild
    )


async def is_moderator(ctx_or_interaction) -> bool:
    """Check if user is moderator"""
    if permission_manager is None:
        return False

    if isinstance(ctx_or_interaction, commands.Context):
        user = ctx_or_interaction.author
        guild = ctx_or_interaction.guild
    else:
        user = ctx_or_interaction.user
        guild = ctx_or_interaction.guild

    return await permission_manager.check_permission(
        user, PermissionLevel.MODERATOR, guild
    )
