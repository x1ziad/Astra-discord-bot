"""
Welcome System - Automated new member onboarding
Handles greetings, role assignment, and server introduction - Maximum 200 lines
"""

import asyncio
import logging
from typing import Dict, List, Optional
import discord
from discord.ext import commands

logger = logging.getLogger("astra.core.welcome")


class WelcomeSystem:
    """Automated welcome and onboarding system"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.welcome_configs = {}  # guild_id -> config
        self.pending_setups = {}  # user_id -> setup_data

        # Default welcome configuration
        self.default_config = {
            "enabled": True,
            "channel_name": "welcome",
            "auto_role": None,
            "welcome_message": "👋 Welcome to **{guild_name}**, {user_mention}!\n\nI'm **Astra**, your AI companion. Feel free to ask me anything or just chat!\n\n🎭 **React below to choose your role and get started!**",
            "dm_welcome": False,
            "dm_message": "Welcome to {guild_name}! I'm Astra, ready to help you explore and have fun! 🚀",
        }

    async def handle_new_member(self, member: discord.Member):
        """Handle new member joining"""
        guild_id = member.guild.id
        config = self.welcome_configs.get(guild_id, self.default_config)

        if not config["enabled"]:
            return

        # Find welcome channel
        welcome_channel = await self._get_welcome_channel(member.guild, config)
        if not welcome_channel:
            return

        try:
            # Send welcome message
            await self._send_welcome_message(welcome_channel, member, config)

            # Auto-assign role if configured
            if config.get("auto_role"):
                await self._assign_auto_role(member, config["auto_role"])

            # Send DM if enabled
            if config.get("dm_welcome"):
                await self._send_dm_welcome(member, config)

            logger.info(f"Welcomed new member: {member} in {member.guild}")

        except Exception as e:
            logger.error(f"Welcome system error for {member}: {e}")

    async def _get_welcome_channel(
        self, guild: discord.Guild, config: Dict
    ) -> Optional[discord.TextChannel]:
        """Get or create welcome channel"""
        channel_name = config.get("channel_name", "welcome")

        # Try to find existing channel
        channel = discord.utils.get(guild.text_channels, name=channel_name)

        if not channel:
            # Try common alternatives
            alternatives = ["general", "main", "lobby", "entrance"]
            for alt_name in alternatives:
                channel = discord.utils.get(guild.text_channels, name=alt_name)
                if channel:
                    break

        if not channel:
            # Use system channel as fallback
            channel = guild.system_channel

        return channel

    async def _send_welcome_message(
        self, channel: discord.TextChannel, member: discord.Member, config: Dict
    ):
        """Send welcome message with interactive elements"""
        # Format welcome message
        message_text = config["welcome_message"].format(
            guild_name=member.guild.name,
            user_mention=member.mention,
            user_name=member.display_name,
        )

        # Create welcome embed
        embed = discord.Embed(
            title="🌟 **New Member Alert!**", description=message_text, color=0x00FF99
        )

        embed.set_thumbnail(
            url=member.avatar.url if member.avatar else member.default_avatar.url
        )
        embed.add_field(
            name="👥 **You're Member #**",
            value=f"{len(member.guild.members)}",
            inline=True,
        )
        embed.add_field(
            name="📅 **Account Created**",
            value=f"<t:{int(member.created_at.timestamp())}:R>",
            inline=True,
        )
        embed.set_footer(text=f"Welcome to {member.guild.name}! 🎉")

        # Send message
        welcome_msg = await channel.send(content=f"🎉 {member.mention}", embed=embed)

        # Import InteractiveMenus here to avoid circular imports
        from .interactive_menus import InteractiveMenus

        interactive = InteractiveMenus(self.bot)

        # Create role selection menu after a short delay
        await asyncio.sleep(2)
        await interactive.create_role_selection_menu(channel, member)

    async def _assign_auto_role(self, member: discord.Member, role_name: str):
        """Assign automatic role to new member"""
        try:
            role = discord.utils.get(member.guild.roles, name=role_name)
            if role:
                await member.add_roles(role, reason="Auto-role assignment")
                logger.info(f"Auto-assigned role {role_name} to {member}")
        except Exception as e:
            logger.error(f"Failed to assign auto-role to {member}: {e}")

    async def _send_dm_welcome(self, member: discord.Member, config: Dict):
        """Send welcome DM to new member"""
        try:
            dm_message = config["dm_message"].format(
                guild_name=member.guild.name, user_name=member.display_name
            )

            embed = discord.Embed(
                title=f"Welcome to {member.guild.name}! 🚀",
                description=dm_message,
                color=0x00FF99,
            )

            embed.add_field(
                name="🤖 **I'm Astra!**",
                value="Your AI companion ready to help with anything you need!",
                inline=False,
            )

            await member.send(embed=embed)

        except discord.Forbidden:
            logger.warning(f"Could not send DM to {member} - DMs disabled")
        except Exception as e:
            logger.error(f"DM welcome error for {member}: {e}")

    async def setup_welcome_for_guild(
        self, guild: discord.Guild, channel: discord.TextChannel
    ) -> discord.Message:
        """Set up welcome system for a guild interactively"""
        embed = discord.Embed(
            title="🎛️ **Welcome System Setup**",
            description="Configure how I'll welcome new members!",
            color=0x00FFFF,
        )

        embed.add_field(
            name="✅ **Current Settings**",
            value="• Welcome messages: **Enabled**\n• Welcome channel: **Auto-detect**\n• Role selection: **Interactive**\n• DM welcome: **Disabled**",
            inline=False,
        )

        embed.add_field(
            name="🔧 **Options**",
            value="⚙️ - Configure settings\n✅ - Enable welcome system\n❌ - Disable welcome system\n🔄 - Reset to defaults",
            inline=False,
        )

        embed.set_footer(text="React below to configure • Setup expires in 60 seconds")

        message = await channel.send(embed=embed)

        # Add reactions
        reactions = ["⚙️", "✅", "❌", "🔄"]
        for reaction in reactions:
            await message.add_reaction(reaction)

        return message

    def update_guild_config(self, guild_id: int, config_updates: Dict):
        """Update welcome configuration for a guild"""
        if guild_id not in self.welcome_configs:
            self.welcome_configs[guild_id] = self.default_config.copy()

        self.welcome_configs[guild_id].update(config_updates)

    def get_guild_config(self, guild_id: int) -> Dict:
        """Get welcome configuration for a guild"""
        return self.welcome_configs.get(guild_id, self.default_config.copy())

    async def create_welcome_channel(self, guild: discord.Guild) -> discord.TextChannel:
        """Create a dedicated welcome channel"""
        try:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(send_messages=False),
                guild.me: discord.PermissionOverwrite(
                    send_messages=True, manage_messages=True
                ),
            }

            channel = await guild.create_text_channel(
                "welcome",
                topic="Welcome new members to our community! 🎉",
                overwrites=overwrites,
                reason="Automated welcome channel creation",
            )

            # Send initial setup message
            embed = discord.Embed(
                title="🌟 **Welcome Channel Created!**",
                description="This channel will now welcome new members automatically!\n\nNew members will:\n• Receive a personalized welcome\n• Get interactive role selection\n• See member count and join info",
                color=0x00FF99,
            )

            await channel.send(embed=embed)
            return channel

        except Exception as e:
            logger.error(f"Failed to create welcome channel in {guild}: {e}")
            return None

    def get_stats(self) -> Dict:
        """Get welcome system statistics"""
        return {
            "configured_guilds": len(self.welcome_configs),
            "enabled_guilds": sum(
                1 for config in self.welcome_configs.values() if config["enabled"]
            ),
            "pending_setups": len(self.pending_setups),
        }
