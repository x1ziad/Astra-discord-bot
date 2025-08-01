"""
Statistics and information commands for Astra Bot
Provides server stats, bot info, and system monitoring
"""

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import platform
import os
import psutil
from typing import Optional, Dict, List, Any, Union
import threading
import traceback

# Use the new config_manager import
from config.config_manager import config_manager


class Stats(commands.GroupCog, name="stats"):
    """Server and bot statistics commands"""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.config = config_manager
        self.logger = bot.logger

    @app_commands.command(
        name="ping", description="Check bot latency and response time"
    )
    @app_commands.checks.cooldown(1, 5)
    async def ping_command(self, interaction: discord.Interaction):
        """Check bot latency and response time"""
        start_time = datetime.utcnow()

        # Initial response
        await interaction.response.defer()

        # Calculate response time
        end_time = datetime.utcnow()
        response_time = (end_time - start_time).total_seconds() * 1000

        # Create embed with results
        embed = discord.Embed(
            title="🏓 Pong!",
            color=(
                self.config.get_color("success")
                if self.bot.latency * 1000 < 100
                else (
                    self.config.get_color("warning")
                    if self.bot.latency * 1000 < 200
                    else self.config.get_color("error")
                )
            ),
        )

        embed.add_field(
            name="📡 WebSocket Latency",
            value=f"{self.bot.latency * 1000:.2f}ms",
            inline=True,
        )

        embed.add_field(
            name="⚡ Response Time", value=f"{response_time:.2f}ms", inline=True
        )

        # Add status indicator
        if self.bot.latency * 1000 < 100:
            status = "🟢 Excellent"
        elif self.bot.latency * 1000 < 200:
            status = "🟡 Good"
        else:
            status = "🔴 Poor"

        embed.add_field(name="📊 Status", value=status, inline=True)

        # Add shard info if applicable
        if interaction.guild:
            embed.set_footer(text=f"Shard ID: {interaction.guild.shard_id}")

        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="uptime", description="Show bot uptime and system information"
    )
    @app_commands.checks.cooldown(1, 10)
    async def uptime_command(self, interaction: discord.Interaction):
        """Show bot uptime and system information"""
        current_time = datetime.utcnow()
        uptime_duration = current_time - self.bot.start_time

        # Format uptime
        days = uptime_duration.days
        hours, remainder = divmod(uptime_duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"

        embed = discord.Embed(
            title=f"⏰ {self.config.get('bot_settings.name', 'Astra')} Uptime",
            color=self.config.get_color("primary"),
            timestamp=current_time,
        )

        embed.add_field(
            name="🚀 Online Since",
            value=f"<t:{int(self.bot.start_time.timestamp())}:F>",
            inline=False,
        )

        embed.add_field(name="⏱️ Total Uptime", value=uptime_str, inline=True)

        # System information
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()

            embed.add_field(
                name="💻 System Stats",
                value=f"**CPU:** {cpu_percent}%\n**RAM:** {memory.percent}%\n**Python:** {platform.python_version()}",
                inline=True,
            )
        except:
            embed.add_field(
                name="💻 System Stats", value="Data unavailable", inline=True
            )

        embed.add_field(
            name="📊 Bot Stats",
            value=f"**Servers:** {len(self.bot.guilds)}\n**Users:** {len(set(self.bot.get_all_members()))}",
            inline=True,
        )

        embed.set_footer(
            text=f"Version: {self.config.get('bot_settings.version', '1.0.0')}"
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="server", description="Display comprehensive server statistics"
    )
    @app_commands.checks.cooldown(1, 30)
    async def server_stats_command(self, interaction: discord.Interaction):
        """Display comprehensive server statistics"""
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message(
                "This command can only be used in a server!", ephemeral=True
            )
            return

        await interaction.response.defer()

        # Calculate member statistics
        total_members = guild.member_count
        online_members = sum(
            1
            for member in guild.members
            if member.status != discord.Status.offline
            if hasattr(member, "status")
        )
        bots = sum(1 for member in guild.members if member.bot)
        humans = total_members - bots

        # Channel statistics
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)

        # Role statistics
        total_roles = len(guild.roles) - 1  # Exclude @everyone

        # Server boost information
        boost_level = guild.premium_tier
        boost_count = guild.premium_subscription_count

        embed = discord.Embed(
            title=f"📊 {guild.name} Statistics",
            color=self.config.get_color("primary"),
            timestamp=datetime.utcnow(),
        )

        # Set server icon as thumbnail
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        # Member statistics
        embed.add_field(
            name="👥 Members",
            value=f"**Total:** {total_members:,}\n**Humans:** {humans:,}\n**Bots:** {bots:,}\n**Online:** {online_members:,}",
            inline=True,
        )

        # Channel statistics
        embed.add_field(
            name="📝 Channels",
            value=f"**Text:** {text_channels}\n**Voice:** {voice_channels}\n**Categories:** {categories}",
            inline=True,
        )

        # Server information
        owner_mention = guild.owner.mention if guild.owner else "Unknown"
        embed.add_field(
            name="🏛️ Server Info",
            value=f"**Created:** <t:{int(guild.created_at.timestamp())}:R>\n**Owner:** {owner_mention}\n**Roles:** {total_roles}",
            inline=True,
        )

        # Boost information
        if boost_count > 0:
            embed.add_field(
                name="✨ Nitro Boosts",
                value=f"**Level:** {boost_level}\n**Boosts:** {boost_count}",
                inline=True,
            )

        # Features
        features = []
        if "COMMUNITY" in guild.features:
            features.append("🌐 Community")
        if "PARTNERED" in guild.features:
            features.append("🤝 Partnered")
        if "VERIFIED" in guild.features:
            features.append("✅ Verified")
        if "VANITY_URL" in guild.features:
            features.append("🔗 Vanity URL")

        if features:
            embed.add_field(name="🎯 Features", value="\n".join(features), inline=True)

        # Verification level
        verification_levels = {
            discord.VerificationLevel.none: "None",
            discord.VerificationLevel.low: "Low",
            discord.VerificationLevel.medium: "Medium",
            discord.VerificationLevel.high: "High",
            discord.VerificationLevel.highest: "Highest",
        }

        embed.add_field(
            name="🔒 Security",
            value=f"**Verification:** {verification_levels.get(guild.verification_level, 'Unknown')}",
            inline=True,
        )

        embed.set_footer(text=f"Server ID: {guild.id}")

        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="members", description="Show a detailed member count breakdown"
    )
    @app_commands.checks.cooldown(1, 10)
    async def member_count_command(self, interaction: discord.Interaction):
        """Show a detailed member count breakdown"""
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message(
                "This command can only be used in a server!", ephemeral=True
            )
            return

        await interaction.response.defer()

        # Count members by status
        try:
            online = sum(
                1 for member in guild.members if str(member.status) == "online"
            )
            idle = sum(1 for member in guild.members if str(member.status) == "idle")
            dnd = sum(1 for member in guild.members if str(member.status) == "dnd")
            offline = sum(
                1 for member in guild.members if str(member.status) == "offline"
            )
        except:
            # Fallback if status checking fails
            online = idle = dnd = 0
            offline = guild.member_count

        # Count bots vs humans
        bots = sum(1 for member in guild.members if member.bot)
        humans = guild.member_count - bots

        embed = discord.Embed(
            title="👥 Member Count Breakdown",
            color=self.config.get_color("success"),
            timestamp=datetime.utcnow(),
        )

        embed.add_field(
            name="📊 Total Members",
            value=f"**{guild.member_count:,}** members",
            inline=False,
        )

        embed.add_field(
            name="🟢 Status Breakdown",
            value=f"🟢 Online: **{online:,}**\n🟡 Idle: **{idle:,}**\n🔴 DND: **{dnd:,}**\n⚫ Offline: **{offline:,}**",
            inline=True,
        )

        embed.add_field(
            name="🤖 Type Breakdown",
            value=f"👤 Humans: **{humans:,}**\n🤖 Bots: **{bots:,}**",
            inline=True,
        )

        # Calculate percentages
        online_percent = (
            (online / guild.member_count) * 100 if guild.member_count > 0 else 0
        )
        embed.add_field(
            name="📈 Activity",
            value=f"**{online_percent:.1f}%** currently online",
            inline=False,
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="roleinfo", description="Get information about server roles"
    )
    @app_commands.describe(role="The role to get information about (optional)")
    @app_commands.checks.cooldown(1, 15)
    async def role_info_command(
        self, interaction: discord.Interaction, role: Optional[discord.Role] = None
    ):
        """Get information about server roles or a specific role"""
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message(
                "This command can only be used in a server!", ephemeral=True
            )
            return

        await interaction.response.defer()

        if role:
            # Show specific role info
            embed = discord.Embed(
                title=f"🏷️ Role: {role.name}",
                color=(
                    role.color
                    if role.color != discord.Color.default()
                    else self.config.get_color("primary")
                ),
                timestamp=datetime.utcnow(),
            )

            embed.add_field(
                name="📊 Info",
                value=f"**Members:** {len(role.members)}\n**Position:** {role.position}\n**Mentionable:** {'Yes' if role.mentionable else 'No'}\n**Hoisted:** {'Yes' if role.hoist else 'No'}",
                inline=True,
            )

            embed.add_field(
                name="🎨 Appearance",
                value=f"**Color:** {str(role.color) if role.color != discord.Color.default() else 'Default'}\n**Created:** <t:{int(role.created_at.timestamp())}:R>",
                inline=True,
            )

            # Show some permissions if they exist
            if role.permissions.administrator:
                perms = "Administrator (All Permissions)"
            else:
                key_perms = []
                if role.permissions.manage_guild:
                    key_perms.append("Manage Server")
                if role.permissions.manage_channels:
                    key_perms.append("Manage Channels")
                if role.permissions.manage_roles:
                    key_perms.append("Manage Roles")
                if role.permissions.kick_members:
                    key_perms.append("Kick Members")
                if role.permissions.ban_members:
                    key_perms.append("Ban Members")

                perms = (
                    ", ".join(key_perms[:3]) if key_perms else "No special permissions"
                )
                if len(key_perms) > 3:
                    perms += f" (+{len(key_perms) - 3} more)"

            embed.add_field(name="🔑 Key Permissions", value=perms, inline=False)

            embed.set_footer(text=f"Role ID: {role.id}")
            await interaction.followup.send(embed=embed)

        else:
            # Show all roles overview
            roles = sorted(
                guild.roles[1:], key=lambda r: r.position, reverse=True
            )  # Exclude @everyone

            embed = discord.Embed(
                title="🎭 Server Roles Overview",
                description=f"This server has **{len(roles)}** roles",
                color=self.config.get_color("primary"),
                timestamp=datetime.utcnow(),
            )

            # Group roles by type
            admin_roles = []
            mod_roles = []
            color_roles = []
            other_roles = []

            for r in roles[:20]:  # Limit to prevent embed overflow
                if r.permissions.administrator:
                    admin_roles.append(r)
                elif (
                    r.permissions.kick_members
                    or r.permissions.ban_members
                    or r.permissions.manage_messages
                ):
                    mod_roles.append(r)
                elif r.color != discord.Color.default() and len(r.name) <= 12:
                    color_roles.append(r)
                else:
                    other_roles.append(r)

            if admin_roles:
                embed.add_field(
                    name="🔑 Admin Roles",
                    value=", ".join([r.mention for r in admin_roles[:5]])
                    + (
                        f" (+{len(admin_roles) - 5} more)"
                        if len(admin_roles) > 5
                        else ""
                    ),
                    inline=False,
                )

            if mod_roles:
                embed.add_field(
                    name="🛡️ Moderation Roles",
                    value=", ".join([r.mention for r in mod_roles[:5]])
                    + (f" (+{len(mod_roles) - 5} more)" if len(mod_roles) > 5 else ""),
                    inline=False,
                )

            if color_roles:
                embed.add_field(
                    name="🎨 Color Roles",
                    value=", ".join([r.mention for r in color_roles[:8]])
                    + (
                        f" (+{len(color_roles) - 8} more)"
                        if len(color_roles) > 8
                        else ""
                    ),
                    inline=False,
                )

            if len(roles) > 20:
                embed.set_footer(
                    text=f"Showing 20/{len(roles)} roles • Use /stats roleinfo @role for details"
                )
            else:
                embed.set_footer(
                    text="Use /stats roleinfo @role for details on a specific role"
                )

            await interaction.followup.send(embed=embed)

    # RENAMED: This method was causing the error - renamed from bot_info_command to _info_command
    @app_commands.command(name="info", description="Show information about the bot")
    @app_commands.checks.cooldown(1, 10)
    async def _info_command(self, interaction: discord.Interaction):
        """Show information about the bot"""
        bot_name = self.config.get("bot_settings.name", "Astra")
        bot_version = self.config.get("bot_settings.version", "1.0.0")

        embed = discord.Embed(
            title=f"🤖 {bot_name} Information",
            description=self.config.get(
                "bot_settings.description",
                "A Discord bot for space exploration and Stellaris roleplay",
            ),
            color=self.config.get_color("primary"),
            timestamp=datetime.utcnow(),
        )

        # Set bot avatar as thumbnail
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)

        # Uptime
        uptime_duration = datetime.utcnow() - self.bot.start_time
        days = uptime_duration.days
        hours, remainder = divmod(uptime_duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"

        embed.add_field(
            name="⚙️ System",
            value=f"**Version:** {bot_version}\n**Python:** {platform.python_version()}\n**discord.py:** {discord.__version__}\n**Uptime:** {uptime_str}",
            inline=True,
        )

        embed.add_field(
            name="📊 Stats",
            value=f"**Servers:** {len(self.bot.guilds):,}\n**Users:** {len(set(self.bot.get_all_members())):,}\n**Channels:** {sum(len(g.channels) for g in self.bot.guilds):,}",
            inline=True,
        )

        # Try to get owner info
        try:
            app_info = await self.bot.application_info()
            if app_info.team:
                owner = "Team: " + app_info.team.name
            else:
                owner = str(app_info.owner)
        except:
            owner = "Unknown"

        embed.add_field(
            name="👑 Creator",
            value=f"{owner}",
            inline=True,
        )

        embed.add_field(
            name="🔗 Links",
            value="[Support Server](https://discord.gg/astra) • [GitHub](https://github.com/astra-bot) • [Documentation](https://astra-bot.com)",
            inline=False,
        )

        embed.set_footer(text="Thanks for using Astra! 💫")

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    """Setup function to add the cog to the bot"""
    await bot.add_cog(Stats(bot))
