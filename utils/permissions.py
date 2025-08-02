"""
Permission utilities for Astra Bot
Provides permission checking and role management
"""

import discord
from enum import Enum
from typing import Union, List, Optional


class PermissionLevel(Enum):
    """Permission levels for bot commands"""

    USER = 1
    MODERATOR = 2
    ADMINISTRATOR = 3
    OWNER = 4


def has_permission(
    user: Union[discord.Member, discord.User], required_level: PermissionLevel
) -> bool:
    """Check if user has required permission level"""
    if not isinstance(user, discord.Member):
        return False

    # Bot owner always has all permissions
    if user.id == user.guild.owner_id:
        return True

    # Check permission levels
    if required_level == PermissionLevel.USER:
        return True
    elif required_level == PermissionLevel.MODERATOR:
        return (
            user.guild_permissions.manage_messages
            or user.guild_permissions.kick_members
            or user.guild_permissions.manage_roles
        )
    elif required_level == PermissionLevel.ADMINISTRATOR:
        return user.guild_permissions.administrator
    elif required_level == PermissionLevel.OWNER:
        return user.id == user.guild.owner_id

    return False


def get_user_permission_level(
    user: Union[discord.Member, discord.User],
) -> PermissionLevel:
    """Get the highest permission level for a user"""
    if not isinstance(user, discord.Member):
        return PermissionLevel.USER

    if user.id == user.guild.owner_id:
        return PermissionLevel.OWNER
    elif user.guild_permissions.administrator:
        return PermissionLevel.ADMINISTRATOR
    elif (
        user.guild_permissions.manage_messages
        or user.guild_permissions.kick_members
        or user.guild_permissions.manage_roles
    ):
        return PermissionLevel.MODERATOR
    else:
        return PermissionLevel.USER


def has_role_hierarchy_permission(
    moderator: discord.Member, target: discord.Member
) -> bool:
    """Check if moderator can manage target based on role hierarchy"""
    if moderator.guild.owner_id == moderator.id:
        return True

    if moderator.guild.owner_id == target.id:
        return False

    return moderator.top_role > target.top_role


def can_manage_role(user: discord.Member, role: discord.Role) -> bool:
    """Check if user can manage a specific role"""
    if user.guild.owner_id == user.id:
        return True

    if not user.guild_permissions.manage_roles:
        return False

    return user.top_role > role


def get_manageable_roles(user: discord.Member) -> List[discord.Role]:
    """Get list of roles that user can manage"""
    if not user.guild_permissions.manage_roles:
        return []

    manageable = []
    for role in user.guild.roles:
        if role != user.guild.default_role and user.top_role > role:
            manageable.append(role)

    return manageable
