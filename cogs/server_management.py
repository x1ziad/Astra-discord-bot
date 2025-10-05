"""
Server Management Commands for Astra Bot
Provides role management, user management, and server optimization features
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, List, Union, Dict, Any
import asyncio
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import colorsys
import re

from config.unified_config import unified_config
from utils.permissions import has_permission, PermissionLevel, check_user_permission


class ServerManagement(commands.GroupCog, name="server"):
    """Server management and optimization commands"""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.config = unified_config
        self.logger = bot.logger

        # Data directories
        self.data_dir = Path("data/guilds")
        self.data_dir.mkdir(parents=True, exist_ok=True)

    @app_commands.command(
        name="optimize", description="Analyze and optimize server settings"
    )
    @app_commands.default_permissions(manage_guild=True)
    async def optimize_server(self, interaction: discord.Interaction):
        """Analyze server and provide optimization recommendations"""
        if not await check_user_permission(
            interaction.user, PermissionLevel.MODERATOR, interaction.guild
        ):
            await interaction.response.send_message(
                "❌ You need moderator permissions for this command.", ephemeral=True
            )
            return

        await interaction.response.defer(thinking=True)

        try:
            guild = interaction.guild
            analysis = await self._analyze_server(guild)

            embed = discord.Embed(
                title="🔧 Server Optimization Analysis",
                description=f"Analysis for **{guild.name}**",
                color=self.config.get_color("info"),
                timestamp=datetime.now(timezone.utc),
            )

            # Server Stats
            embed.add_field(
                name="📊 Server Overview",
                value=f"**Members:** {guild.member_count:,}\n"
                f"**Channels:** {len(guild.channels)}\n"
                f"**Roles:** {len(guild.roles)}\n"
                f"**Emojis:** {len(guild.emojis)}/{guild.emoji_limit}",
                inline=True,
            )

            # Role Analysis
            role_issues = analysis.get("role_issues", [])
            if role_issues:
                embed.add_field(
                    name="⚠️ Role Issues",
                    value="\n".join([f"• {issue}" for issue in role_issues[:5]]),
                    inline=True,
                )
            else:
                embed.add_field(
                    name="✅ Roles", value="No issues detected", inline=True
                )

            # Channel Analysis
            channel_issues = analysis.get("channel_issues", [])
            if channel_issues:
                embed.add_field(
                    name="⚠️ Channel Issues",
                    value="\n".join([f"• {issue}" for issue in channel_issues[:5]]),
                    inline=True,
                )
            else:
                embed.add_field(
                    name="✅ Channels", value="No issues detected", inline=True
                )

            # Recommendations
            recommendations = analysis.get("recommendations", [])
            if recommendations:
                embed.add_field(
                    name="💡 Recommendations",
                    value="\n".join([f"• {rec}" for rec in recommendations[:5]]),
                    inline=False,
                )

            # Optimization Score
            score = analysis.get("optimization_score", 85)
            color_map = {(90, 100): "🟢", (75, 89): "🟡", (60, 74): "🟠", (0, 59): "🔴"}

            score_emoji = next(
                emoji
                for (min_score, max_score), emoji in color_map.items()
                if min_score <= score <= max_score
            )

            embed.add_field(
                name="📈 Optimization Score",
                value=f"{score_emoji} **{score}/100**",
                inline=True,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in server optimization: {e}")
            await interaction.followup.send(
                "❌ Error analyzing server. Please try again."
            )

    async def _analyze_server(self, guild: discord.Guild) -> Dict[str, Any]:
        """Analyze server for optimization opportunities"""
        analysis = {
            "role_issues": [],
            "channel_issues": [],
            "recommendations": [],
            "optimization_score": 100,
        }

        # Analyze roles
        duplicate_colors = {}
        unused_roles = []

        for role in guild.roles:
            if role.name != "@everyone":
                # Check for duplicate colors
                if role.color.value != 0:
                    color_key = role.color.value
                    if color_key in duplicate_colors:
                        duplicate_colors[color_key].append(role.name)
                    else:
                        duplicate_colors[color_key] = [role.name]

                # Check for unused roles (no members)
                if len(role.members) == 0 and not role.managed:
                    unused_roles.append(role.name)

        # Add role issues
        for color, roles in duplicate_colors.items():
            if len(roles) > 1:
                analysis["role_issues"].append(
                    f"Duplicate color: {', '.join(roles[:3])}"
                )

        if unused_roles:
            analysis["role_issues"].append(f"{len(unused_roles)} unused roles detected")

        # Analyze channels
        empty_categories = []
        for category in guild.categories:
            if len(category.channels) == 0:
                empty_categories.append(category.name)

        if empty_categories:
            analysis["channel_issues"].append(
                f"{len(empty_categories)} empty categories"
            )

        # Generate recommendations
        if len(guild.roles) > 50:
            analysis["recommendations"].append("Consider consolidating similar roles")

        if len(analysis["role_issues"]) > 0:
            analysis["recommendations"].append(
                "Optimize role colors and remove unused roles"
            )

        if len(analysis["channel_issues"]) > 0:
            analysis["recommendations"].append(
                "Clean up empty categories and unused channels"
            )

        # Calculate optimization score
        issues_count = len(analysis["role_issues"]) + len(analysis["channel_issues"])
        analysis["optimization_score"] = max(60, 100 - (issues_count * 5))

        return analysis

    @app_commands.command(name="roles", description="Manage server roles")
    @app_commands.describe(
        action="Action to perform",
        role="Target role",
        user="Target user",
        color="New color (hex format)",
    )
    @app_commands.default_permissions(manage_roles=True)
    async def manage_roles(
        self,
        interaction: discord.Interaction,
        action: str,
        role: Optional[discord.Role] = None,
        user: Optional[discord.Member] = None,
        color: Optional[str] = None,
    ):
        """Advanced role management"""
        if not await check_user_permission(
            interaction.user, PermissionLevel.MODERATOR, interaction.guild
        ):
            await interaction.response.send_message(
                "❌ You need moderator permissions for this command.", ephemeral=True
            )
            return

        await interaction.response.defer(thinking=True)

        try:
            if action.lower() == "list":
                await self._list_roles(interaction)
            elif action.lower() == "optimize_colors":
                await self._optimize_role_colors(interaction)
            elif action.lower() == "add" and role and user:
                await self._add_role_to_user(interaction, role, user)
            elif action.lower() == "remove" and role and user:
                await self._remove_role_from_user(interaction, role, user)
            elif action.lower() == "color" and role and color:
                await self._change_role_color(interaction, role, color)
            else:
                await interaction.followup.send(
                    "❌ Invalid action or missing parameters."
                )

        except Exception as e:
            self.logger.error(f"Error in role management: {e}")
            await interaction.followup.send(
                "❌ Error managing roles. Please try again."
            )

    async def _list_roles(self, interaction: discord.Interaction):
        """List all server roles with details"""
        guild = interaction.guild
        roles_data = []

        for role in sorted(guild.roles, key=lambda r: r.position, reverse=True):
            if role.name != "@everyone":
                color_hex = (
                    f"#{role.color.value:06x}" if role.color.value != 0 else "Default"
                )
                roles_data.append(
                    {
                        "name": role.name,
                        "members": len(role.members),
                        "color": color_hex,
                        "position": role.position,
                        "managed": role.managed,
                    }
                )

        # Create paginated embeds
        embeds = []
        chunk_size = 10

        for i in range(0, len(roles_data), chunk_size):
            chunk = roles_data[i : i + chunk_size]

            embed = discord.Embed(
                title=f"🎭 Server Roles ({i//chunk_size + 1}/{(len(roles_data)-1)//chunk_size + 1})",
                color=self.config.get_color("primary"),
                timestamp=datetime.now(timezone.utc),
            )

            for role_data in chunk:
                managed_text = " (Bot)" if role_data["managed"] else ""
                embed.add_field(
                    name=f"{role_data['name']}{managed_text}",
                    value=f"Members: {role_data['members']}\n"
                    f"Color: {role_data['color']}\n"
                    f"Position: {role_data['position']}",
                    inline=True,
                )

            embeds.append(embed)

        if embeds:
            from ui.ui_components import PaginatedView

            view = PaginatedView(embeds)
            await interaction.followup.send(embed=embeds[0], view=view)
        else:
            await interaction.followup.send("No roles found.")

    async def _optimize_role_colors(self, interaction: discord.Interaction):
        """Optimize role colors to avoid duplicates"""
        guild = interaction.guild
        roles_to_update = []
        used_colors = set()

        # Find roles with duplicate colors
        for role in guild.roles:
            if role.name != "@everyone" and not role.managed and role.color.value != 0:
                if role.color.value in used_colors:
                    roles_to_update.append(role)
                else:
                    used_colors.add(role.color.value)

        if not roles_to_update:
            embed = discord.Embed(
                title="✅ Role Colors Optimized",
                description="No duplicate role colors found!",
                color=self.config.get_color("success"),
            )
            await interaction.followup.send(embed=embed)
            return

        # Generate unique colors
        updated_roles = []
        for i, role in enumerate(roles_to_update):
            try:
                # Generate a unique color using HSV
                hue = (i * 137.5) % 360  # Golden angle approximation
                saturation = 0.7
                value = 0.9

                rgb = colorsys.hsv_to_rgb(hue / 360, saturation, value)
                color = discord.Color.from_rgb(
                    int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
                )

                await role.edit(color=color)
                updated_roles.append(role.name)
                await asyncio.sleep(1)  # Rate limiting

            except Exception as e:
                self.logger.error(f"Error updating role {role.name}: {e}")

        embed = discord.Embed(
            title="🎨 Role Colors Optimized",
            description=f"Updated {len(updated_roles)} roles with unique colors:",
            color=self.config.get_color("success"),
        )

        if updated_roles:
            embed.add_field(
                name="Updated Roles",
                value="\n".join([f"• {role}" for role in updated_roles[:10]]),
                inline=False,
            )

        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="move", description="Force move users to a specific channel"
    )
    @app_commands.describe(
        user="User to move (optional - move all if not specified)",
        channel="Voice channel to move to",
        reason="Reason for the move",
    )
    @app_commands.default_permissions(move_members=True)
    async def force_move(
        self,
        interaction: discord.Interaction,
        channel: discord.VoiceChannel,
        user: Optional[discord.Member] = None,
        reason: Optional[str] = "Moderator action",
    ):
        """Force move users to a specific voice channel"""
        if not await check_user_permission(
            interaction.user, PermissionLevel.MODERATOR, interaction.guild
        ):
            await interaction.response.send_message(
                "❌ You need moderator permissions for this command.", ephemeral=True
            )
            return

        await interaction.response.defer(thinking=True)

        try:
            moved_users = []

            if user:
                # Move specific user
                if user.voice and user.voice.channel:
                    await user.move_to(channel, reason=reason)
                    moved_users.append(user.display_name)
                else:
                    await interaction.followup.send(
                        f"❌ {user.display_name} is not in a voice channel."
                    )
                    return
            else:
                # Move all users from all voice channels
                for vc in interaction.guild.voice_channels:
                    if vc != channel:  # Don't move users already in target channel
                        members_to_move = vc.members.copy()
                        for member in members_to_move:
                            try:
                                await member.move_to(channel, reason=reason)
                                moved_users.append(member.display_name)
                                await asyncio.sleep(0.5)  # Rate limiting
                            except Exception as e:
                                self.logger.error(
                                    f"Error moving {member.display_name}: {e}"
                                )

            if moved_users:
                embed = discord.Embed(
                    title="🔄 Users Moved",
                    description=f"Moved {len(moved_users)} user(s) to {channel.mention}",
                    color=self.config.get_color("success"),
                    timestamp=datetime.now(timezone.utc),
                )

                if len(moved_users) <= 20:
                    embed.add_field(
                        name="Moved Users",
                        value="\n".join([f"• {name}" for name in moved_users]),
                        inline=False,
                    )

                embed.set_footer(text=f"Reason: {reason}")
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(
                    "❌ No users were moved. Check if users are in voice channels."
                )

        except Exception as e:
            self.logger.error(f"Error in force move: {e}")
            await interaction.followup.send("❌ Error moving users. Please try again.")


async def setup(bot):
    await bot.add_cog(ServerManagement(bot))
