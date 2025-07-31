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
import traceback
import sys

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
            try:
                embed.set_footer(
                    text=f"Shard ID: {interaction.guild.shard_id if hasattr(interaction.guild, 'shard_id') else 0}"
                )
            except:
                embed.set_footer(text="Shard info unavailable")

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

        # System information - different details based on user permissions
        is_admin = (
            interaction.user.guild_permissions.administrator
            if interaction.guild
            else False
        )
        is_mod = (
            (
                interaction.user.guild_permissions.manage_guild
                or interaction.user.guild_permissions.manage_messages
            )
            if interaction.guild
            else False
        )

        try:
            # Basic system stats for everyone
            embed.add_field(
                name="💻 System Stats",
                value=f"**Python:** {platform.python_version()}\n**discord.py:** {discord.__version__}",
                inline=True,
            )

            # More details for mods and admins
            if is_admin or is_mod:
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()

                # Add more detailed system info
                embed.add_field(
                    name="🖥️ Host Stats",
                    value=f"**CPU:** {cpu_percent}%\n**RAM:** {memory.percent}%\n**OS:** {platform.system()} {platform.release()}",
                    inline=True,
                )

                # Add process info for admins
                if is_admin:
                    process = psutil.Process(os.getpid())
                    mem_usage = process.memory_info().rss / 1024 / 1024  # Convert to MB

                    embed.add_field(
                        name="⚙️ Process Info",
                        value=f"**PID:** {os.getpid()}\n**Memory:** {mem_usage:.2f} MB\n**Threads:** {process.num_threads()}",
                        inline=True,
                    )
        except Exception as e:
            self.logger.error(f"Error getting system stats: {str(e)}")
            embed.add_field(
                name="💻 System Stats", value="Data unavailable", inline=True
            )

        embed.add_field(
            name="📊 Bot Stats",
            value=f"**Servers:** {len(self.bot.guilds):,}\n**Users:** {len(set(self.bot.get_all_members())):,}",
            inline=True,
        )

        # Show additional diagnostic info for admins
        if is_admin:
            embed.add_field(
                name="🧪 Diagnostics",
                value=f"**Cogs loaded:** {len(self.bot.cogs)}\n"
                f"**Commands:** {len(self.bot.tree.get_commands()):,}\n"
                f"**Events:** {len(self.bot.extra_events)}",
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

        try:
            # Calculate member statistics safely
            total_members = guild.member_count

            # Safely count online members
            online_members = 0
            bots = 0
            for member in guild.members:
                if member.bot:
                    bots += 1
                elif (
                    hasattr(member, "status")
                    and member.status != discord.Status.offline
                ):
                    online_members += 1

            humans = total_members - bots

            # Channel statistics
            text_channels = len(guild.text_channels)
            voice_channels = len(guild.voice_channels)
            categories = len(guild.categories)
            forums = (
                sum(1 for c in guild.channels if isinstance(c, discord.ForumChannel))
                if hasattr(discord, "ForumChannel")
                else 0
            )
            stage_channels = (
                sum(1 for c in guild.channels if isinstance(c, discord.StageChannel))
                if hasattr(discord, "StageChannel")
                else 0
            )

            # Role statistics
            total_roles = len(guild.roles) - 1  # Exclude @everyone

            # Server boost information
            boost_level = guild.premium_tier
            boost_count = guild.premium_subscription_count

            # Check user permissions to determine detail level
            is_admin = interaction.user.guild_permissions.administrator
            is_mod = (
                interaction.user.guild_permissions.manage_guild
                or interaction.user.guild_permissions.manage_messages
            )

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
            channels_value = f"**Text:** {text_channels}\n**Voice:** {voice_channels}\n**Categories:** {categories}"
            if forums > 0:
                channels_value += f"\n**Forums:** {forums}"
            if stage_channels > 0:
                channels_value += f"\n**Stages:** {stage_channels}"

            embed.add_field(
                name="📝 Channels",
                value=channels_value,
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

            # Features - expanded for admins and mods
            features = []
            feature_list = guild.features

            # Basic features everyone can see
            if "COMMUNITY" in feature_list:
                features.append("🌐 Community")
            if "PARTNERED" in feature_list:
                features.append("🤝 Partnered")
            if "VERIFIED" in feature_list:
                features.append("✅ Verified")
            if "VANITY_URL" in feature_list:
                features.append("🔗 Vanity URL")

            # More detailed features for mods/admins
            if is_admin or is_mod:
                if "ANIMATED_ICON" in feature_list:
                    features.append("🎭 Animated Icon")
                if "BANNER" in feature_list:
                    features.append("🏳️ Banner")
                if "WELCOME_SCREEN_ENABLED" in feature_list:
                    features.append("👋 Welcome Screen")
                if "MEMBER_VERIFICATION_GATE_ENABLED" in feature_list:
                    features.append("🔐 Membership Screening")
                if "THREADS_ENABLED" in feature_list:
                    features.append("🧵 Threads")

            if features:
                embed.add_field(
                    name="🎯 Features", value="\n".join(features[:8]), inline=True
                )

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

            # For admins, add extra stats
            if is_admin:
                emoji_count = len(guild.emojis)
                sticker_count = len(guild.stickers) if hasattr(guild, "stickers") else 0

                embed.add_field(
                    name="🎨 Assets",
                    value=f"**Emojis:** {emoji_count}/{guild.emoji_limit}\n**Stickers:** {sticker_count}/{guild.sticker_limit if hasattr(guild, 'sticker_limit') else '?'}",
                    inline=True,
                )

                # Add moderation stats if available
                if hasattr(guild, "explicit_content_filter"):
                    filter_levels = {
                        discord.ContentFilter.disabled: "Disabled",
                        discord.ContentFilter.no_role: "No Role",
                        discord.ContentFilter.all_members: "All Members",
                    }

                    embed.add_field(
                        name="🛡️ Moderation",
                        value=f"**Content Filter:** {filter_levels.get(guild.explicit_content_filter, 'Unknown')}",
                        inline=True,
                    )

            embed.set_footer(text=f"Server ID: {guild.id}")

        except Exception as e:
            self.logger.error(f"Error in server stats: {str(e)}")
            embed = discord.Embed(
                title="❌ Error Getting Server Stats",
                description="An error occurred while retrieving server statistics. Please try again later.",
                color=self.config.get_color("error"),
            )
            if self.config.get("development.debug_mode", False) and (
                is_admin or is_mod
            ):
                embed.add_field(name="Error Details", value=f"```{str(e)[:1000]}```")

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

        try:
            # Safely calculate member statistics
            online = idle = dnd = offline = 0
            bots = 0
            members_with_role = {}  # For admin view
            join_data = {"week": 0, "month": 0, "total": 0}  # For tracking join periods

            # Check if user is admin or mod
            is_admin = interaction.user.guild_permissions.administrator
            is_mod = (
                interaction.user.guild_permissions.manage_guild
                or interaction.user.guild_permissions.manage_messages
            )

            now = datetime.utcnow()
            week_ago = now - timedelta(days=7)
            month_ago = now - timedelta(days=30)

            # Get top roles for display
            if is_admin or is_mod:
                top_roles = sorted(
                    guild.roles[1:], key=lambda r: len(r.members), reverse=True
                )[:5]
                for role in top_roles:
                    members_with_role[role.name] = len(role.members)

            # Process member data
            for member in guild.members:
                # Count bots
                if member.bot:
                    bots += 1
                    continue

                # Track join dates
                joined_at = member.joined_at
                if joined_at:
                    join_data["total"] += 1
                    if joined_at > week_ago:
                        join_data["week"] += 1
                    if joined_at > month_ago:
                        join_data["month"] += 1

                # Count status if available
                try:
                    if hasattr(member, "status"):
                        status = str(member.status)
                        if status == "online":
                            online += 1
                        elif status == "idle":
                            idle += 1
                        elif status == "dnd":
                            dnd += 1
                        else:
                            offline += 1
                    else:
                        offline += 1
                except:
                    offline += 1

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

            # Add joining data for mods/admins
            if is_admin or is_mod:
                join_stats = f"**Last 7 days:** {join_data['week']} members\n**Last 30 days:** {join_data['month']} members"
                if is_admin:
                    # Calculate average joins per day
                    avg_daily = join_data["week"] / 7 if join_data["week"] > 0 else 0
                    join_stats += f"\n**Avg. Daily:** {avg_daily:.1f} members"

                embed.add_field(
                    name="📈 Join Activity",
                    value=join_stats,
                    inline=False,
                )

                # Show popular roles for admins/mods
                if members_with_role:
                    role_stats = "\n".join(
                        [
                            f"**{role}:** {count:,} members"
                            for role, count in members_with_role.items()
                        ]
                    )
                    embed.add_field(
                        name="🏷️ Popular Roles",
                        value=role_stats,
                        inline=False,
                    )

            embed.add_field(
                name="📈 Activity",
                value=f"**{online_percent:.1f}%** currently online",
                inline=False,
            )

            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)

        except Exception as e:
            self.logger.error(f"Error in member stats: {str(e)}")
            embed = discord.Embed(
                title="❌ Error Getting Member Stats",
                description="An error occurred while retrieving member statistics. Please try again later.",
                color=self.config.get_color("error"),
            )

            if self.config.get("development.debug_mode", False) and (
                is_admin or is_mod
            ):
                embed.add_field(name="Error Details", value=f"```{str(e)[:1000]}```")

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

        try:
            # Check if user is admin or mod
            is_admin = interaction.user.guild_permissions.administrator
            is_mod = (
                interaction.user.guild_permissions.manage_guild
                or interaction.user.guild_permissions.manage_roles
            )

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

                # Show permissions based on user role
                if is_admin or is_mod:
                    # Detailed permissions for admins/mods
                    if role.permissions.administrator:
                        perms = "Administrator (All Permissions)"
                    else:
                        key_perms = []
                        # Add important permissions
                        for perm, value in role.permissions:
                            if value and perm in [
                                "manage_guild",
                                "manage_channels",
                                "manage_roles",
                                "kick_members",
                                "ban_members",
                                "manage_messages",
                                "mention_everyone",
                                "manage_webhooks",
                                "moderate_members",
                            ]:
                                key_perms.append(perm.replace("_", " ").title())

                        perms = (
                            ", ".join(key_perms[:5])
                            if key_perms
                            else "No special permissions"
                        )
                        if len(key_perms) > 5:
                            perms += f" (+{len(key_perms) - 5} more)"
                else:
                    # Simplified permissions for regular users
                    if role.permissions.administrator:
                        perms = "Administrator"
                    elif any(
                        [
                            role.permissions.ban_members,
                            role.permissions.kick_members,
                            role.permissions.manage_messages,
                        ]
                    ):
                        perms = "Moderator"
                    elif role.permissions.mention_everyone:
                        perms = "Can mention everyone"
                    else:
                        perms = "Standard role"

                embed.add_field(name="🔑 Key Permissions", value=perms, inline=False)

                # For admins, show additional details
                if is_admin:
                    integration_info = (
                        "No"
                        if not hasattr(role, "managed") or not role.managed
                        else "Yes"
                    )
                    embed.add_field(
                        name="⚙️ Technical Details",
                        value=f"**Integration Role:** {integration_info}\n**ID:** {role.id}",
                        inline=False,
                    )
                else:
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

                for r in roles[:30]:  # Increased limit for admins/mods
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
                        + (
                            f" (+{len(mod_roles) - 5} more)"
                            if len(mod_roles) > 5
                            else ""
                        ),
                        inline=False,
                    )

                # Show more roles for admins/mods
                if is_admin or is_mod:
                    display_limit = 15
                else:
                    display_limit = 8

                if color_roles:
                    embed.add_field(
                        name="🎨 Color Roles",
                        value=", ".join(
                            [r.mention for r in color_roles[:display_limit]]
                        )
                        + (
                            f" (+{len(color_roles) - display_limit} more)"
                            if len(color_roles) > display_limit
                            else ""
                        ),
                        inline=False,
                    )

                # Show top roles by member count for admins/mods
                if (is_admin or is_mod) and other_roles:
                    top_member_roles = sorted(
                        roles, key=lambda r: len(r.members), reverse=True
                    )[:5]
                    embed.add_field(
                        name="👥 Most Common Roles",
                        value="\n".join(
                            [
                                f"{r.mention}: **{len(r.members)}** members"
                                for r in top_member_roles
                            ]
                        ),
                        inline=False,
                    )

                if len(roles) > 30 and (is_admin or is_mod):
                    embed.set_footer(
                        text=f"Showing top 30/{len(roles)} roles • Use /stats roleinfo @role for details"
                    )
                elif len(roles) > 20:
                    embed.set_footer(
                        text=f"Showing 20/{len(roles)} roles • Use /stats roleinfo @role for details"
                    )
                else:
                    embed.set_footer(
                        text="Use /stats roleinfo @role for details on a specific role"
                    )

        except Exception as e:
            self.logger.error(f"Error in role info: {str(e)}")
            embed = discord.Embed(
                title="❌ Error Getting Role Info",
                description="An error occurred while retrieving role information. Please try again later.",
                color=self.config.get_color("error"),
            )

            if self.config.get("development.debug_mode", False) and (
                is_admin or is_mod
            ):
                embed.add_field(name="Error Details", value=f"```{str(e)[:1000]}```")

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="info", description="Show information about the bot")
    @app_commands.checks.cooldown(1, 10)
    async def _bot_info_command(self, interaction: discord.Interaction):
        """Show information about the bot (fixed name to avoid discord.py conflicts)"""
        try:
            # Check if user is admin or mod
            is_admin = False
            is_mod = False
            if interaction.guild:
                is_admin = interaction.user.guild_permissions.administrator
                is_mod = (
                    interaction.user.guild_permissions.manage_guild
                    or interaction.user.guild_permissions.manage_messages
                )

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

            # Basic info for all users
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
                app_info = await self.bot.application.fetch()
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

            # Add enhanced stats for admins and mods
            if is_admin or is_mod:
                try:
                    # Get more detailed stats
                    process = psutil.Process(os.getpid())
                    memory_usage = process.memory_info().rss / 1024 / 1024  # MB

                    embed.add_field(
                        name="🖥️ Performance",
                        value=f"**Memory:** {memory_usage:.1f}MB\n**CPU:** {psutil.cpu_percent()}%\n**Commands:** {len(self.bot.tree.get_commands())}",
                        inline=True,
                    )

                    # Add shard info if applicable
                    if hasattr(self.bot, "shard_count") and self.bot.shard_count > 1:
                        embed.add_field(
                            name="📡 Sharding",
                            value=f"**Shards:** {self.bot.shard_count}\n**This Shard:** {interaction.guild.shard_id if interaction.guild else '0'}",
                            inline=True,
                        )
                except Exception as e:
                    self.logger.error(f"Error getting detailed stats: {str(e)}")

            # More technical information for admins
            if is_admin:
                try:
                    embed.add_field(
                        name="🧪 Technical",
                        value=f"**Platform:** {platform.system()} {platform.release()}\n"
                        f"**Process ID:** {os.getpid()}\n"
                        f"**Threads:** {threading.active_count()}",
                        inline=True,
                    )
                except:
                    pass

            embed.add_field(
                name="🔗 Links",
                value="[Support Server](https://discord.gg/astra) • [GitHub](https://github.com/astra-bot) • [Documentation](https://astra-bot.com)",
                inline=False,
            )

            embed.set_footer(text="Thanks for using Astra! 💫")

        except Exception as e:
            self.logger.error(f"Error in bot info: {str(e)}\n{traceback.format_exc()}")
            embed = discord.Embed(
                title="❌ Error Getting Bot Info",
                description="An error occurred while retrieving bot information. Please try again later.",
                color=self.config.get_color("error"),
            )

            if self.config.get("development.debug_mode", False) and (
                is_admin or is_mod
            ):
                embed.add_field(name="Error Details", value=f"```{str(e)[:1000]}```")

        await interaction.response.send_message(embed=embed)

    # Missing import for threading
    import threading


async def setup(bot):
    """Setup function to add the cog to the bot"""
    await bot.add_cog(Stats(bot))
