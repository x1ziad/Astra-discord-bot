"""
Interactive Menus System - Emoji-based user interactions
Handles role selection, server setup, and interactive choices - Maximum 200 lines
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable
import discord
from discord.ext import commands

logger = logging.getLogger("astra.core.interactive")


class InteractiveMenus:
    """Emoji-based interactive menu system"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_menus = {}  # message_id -> menu_data
        self.role_configs = {
            "🎮": {"name": "Gaming Enthusiast", "color": 0x00FF00},
            "🚀": {"name": "Space Explorer", "color": 0x0099FF},
            "💻": {"name": "Tech Wizard", "color": 0xFF6600},
            "🎨": {"name": "Creative Soul", "color": 0xFF3399},
            "⚙️": {"name": "Bot Developer", "color": 0x9900FF},
            "🌟": {"name": "VIP Member", "color": 0xFFFF00},
        }

    async def create_role_selection_menu(
        self, channel: discord.TextChannel, user: discord.Member
    ) -> discord.Message:
        """Create interactive role selection menu"""
        embed = discord.Embed(
            title="🎭 **Role Selection Menu**",
            description=f"Hey {user.mention}! Choose your role by reacting with an emoji:\n\n",
            color=0x00FFFF,
        )

        # Add role options to embed
        for emoji, config in self.role_configs.items():
            embed.description += f"{emoji} - **{config['name']}**\n"

        embed.description += "\n*Click an emoji below to select your role!* ⬇️"
        embed.set_footer(text="React within 60 seconds • One role per user")

        # Send message and add reactions
        message = await channel.send(embed=embed)

        # Add all emoji reactions
        for emoji in self.role_configs.keys():
            await message.add_reaction(emoji)

        # Store menu data
        self.active_menus[message.id] = {
            "type": "role_selection",
            "user_id": user.id,
            "created_at": asyncio.get_event_loop().time(),
            "timeout": 60,
        }

        # Set up automatic cleanup
        asyncio.create_task(self._cleanup_menu_after_timeout(message.id, 60))

        return message

    async def handle_reaction(self, payload: discord.RawReactionActionEvent) -> bool:
        """Handle emoji reactions on interactive menus"""
        if payload.user_id == self.bot.user.id:
            return False

        menu_data = self.active_menus.get(payload.message_id)
        if not menu_data:
            return False

        # Check if this user can interact with this menu
        if menu_data["user_id"] != payload.user_id:
            return False

        # Handle based on menu type
        if menu_data["type"] == "role_selection":
            return await self._handle_role_selection(payload, menu_data)

        return False

    async def _handle_role_selection(
        self, payload: discord.RawReactionActionEvent, menu_data: Dict
    ) -> bool:
        """Handle role selection reaction"""
        emoji = str(payload.emoji)

        if emoji not in self.role_configs:
            return False

        try:
            # Get guild and member
            guild = self.bot.get_guild(payload.guild_id)
            if not guild:
                return False

            member = guild.get_member(payload.user_id)
            if not member:
                return False

            # Get or create role
            role_config = self.role_configs[emoji]
            role = discord.utils.get(guild.roles, name=role_config["name"])

            if not role:
                # Create role if it doesn't exist
                role = await guild.create_role(
                    name=role_config["name"],
                    color=discord.Color(role_config["color"]),
                    reason="Interactive role selection",
                )

            # Remove other interactive roles first
            for other_emoji, other_config in self.role_configs.items():
                if other_emoji != emoji:
                    other_role = discord.utils.get(
                        guild.roles, name=other_config["name"]
                    )
                    if other_role and other_role in member.roles:
                        await member.remove_roles(other_role, reason="Role change")

            # Add new role
            await member.add_roles(role, reason="Interactive role selection")

            # Send confirmation
            channel = guild.get_channel(payload.channel_id)
            if channel:
                embed = discord.Embed(
                    title="✅ **Role Updated!**",
                    description=f"{member.mention} is now a **{role_config['name']}**! {emoji}",
                    color=role_config["color"],
                )
                await channel.send(embed=embed, delete_after=10)

            # Clean up menu
            await self._cleanup_menu(payload.message_id)

            logger.info(f"Role assigned: {member} -> {role_config['name']}")
            return True

        except Exception as e:
            logger.error(f"Role selection error: {e}")
            return False

    async def create_custom_menu(
        self,
        channel: discord.TextChannel,
        title: str,
        options: Dict[str, str],
        callback: Callable,
        user: discord.Member = None,
        timeout: int = 60,
    ) -> discord.Message:
        """Create custom interactive menu"""
        embed = discord.Embed(title=title, color=0x00FFFF)

        description = ""
        for emoji, option in options.items():
            description += f"{emoji} - {option}\n"

        embed.description = description
        embed.set_footer(text=f"React within {timeout} seconds")

        message = await channel.send(embed=embed)

        # Add reactions
        for emoji in options.keys():
            await message.add_reaction(emoji)

        # Store menu data
        self.active_menus[message.id] = {
            "type": "custom",
            "user_id": user.id if user else None,
            "callback": callback,
            "options": options,
            "created_at": asyncio.get_event_loop().time(),
            "timeout": timeout,
        }

        asyncio.create_task(self._cleanup_menu_after_timeout(message.id, timeout))
        return message

    async def _cleanup_menu_after_timeout(self, message_id: int, timeout: int):
        """Clean up menu after timeout"""
        await asyncio.sleep(timeout)
        await self._cleanup_menu(message_id)

    async def _cleanup_menu(self, message_id: int):
        """Remove menu from active menus"""
        if message_id in self.active_menus:
            del self.active_menus[message_id]

        # Try to remove reactions from message
        try:
            for guild in self.bot.guilds:
                for channel in guild.text_channels:
                    try:
                        message = await channel.fetch_message(message_id)
                        if message and message.author == self.bot.user:
                            await message.clear_reactions()
                            break
                    except:
                        continue
        except:
            pass

    def get_stats(self) -> Dict:
        """Get interactive menu statistics"""
        return {
            "active_menus": len(self.active_menus),
            "available_roles": len(self.role_configs),
        }
