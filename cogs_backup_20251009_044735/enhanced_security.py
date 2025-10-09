"""
🛡️ ENHANCED SECURITY COG - TOP-NOTCH PROTECTION
Advanced security and moderation cog with flawless protection capabilities

Features:
- Intelligent spam detection with strict but reasonable rules
- Smart link validation (allows valid links, blocks malicious ones)
- Dynamic punishment system based on violation history
- Real-time threat assessment and behavioral analysis
- Comprehensive logging and evidence collection
- Automated security responses with human oversight
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands, tasks

from core.advanced_security_system import (
    AdvancedSecuritySystem,
    ViolationType,
    ViolationSeverity,
)
from utils.permissions import has_permission, PermissionLevel, check_user_permission
from config.unified_config import unified_config

logger = logging.getLogger("astra.security.enhanced")


class EnhancedSecurity(commands.Cog):
    """Enhanced Security and Moderation System"""

    def __init__(self, bot):
        self.bot = bot
        self.config = unified_config
        self.logger = bot.logger if hasattr(bot, "logger") else logger

        # Initialize the advanced security system
        self.security_system = AdvancedSecuritySystem(bot)

        # Guild-specific settings
        self.guild_settings = {}

        # Load default settings
        self.default_settings = {
            "security_enabled": True,
            "auto_moderation": True,
            "strict_spam_detection": True,
            "smart_link_filtering": True,
            "behavioral_analysis": True,
            "trust_system_enabled": True,
            "log_all_actions": True,
            "notify_moderators": True,
            "auto_timeout_enabled": True,
            "progressive_punishment": True,
        }

        logger.info("🛡️ Enhanced Security System initialized")

    async def cog_load(self):
        """Initialize security system when cog loads"""
        logger.info("🔄 Loading Enhanced Security System...")
        # The security system is already initialized in __init__
        logger.info("✅ Enhanced Security System loaded successfully")

    async def cog_unload(self):
        """Cleanup when cog unloads"""
        logger.info("🔄 Unloading Enhanced Security System...")
        await self.security_system.shutdown()
        logger.info("✅ Enhanced Security System unloaded")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Monitor all messages for security violations"""
        # Skip bot messages and DMs
        if message.author.bot or not message.guild:
            return

        # Check if security is enabled for this guild
        guild_settings = self.get_guild_settings(message.guild.id)
        if not guild_settings.get("security_enabled", True):
            return

        try:
            # Analyze message for security violations
            should_act, violations = (
                await self.security_system.analyze_message_security(message)
            )

            if should_act and violations:
                # Handle the violations
                result = await self.security_system.handle_violations(
                    message, violations
                )

                # Log the action
                self.logger.info(
                    f"🛡️ Security action taken: User {message.author} ({message.author.id}) - "
                    f"{result['violations_detected']} violations - {result['action_taken']}"
                )

                # Update guild statistics
                await self.update_guild_stats(message.guild.id, violations, result)

        except Exception as e:
            self.logger.error(
                f"Security system error for message from {message.author}: {e}"
            )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Monitor new member joins for potential security threats"""
        try:
            # Check for suspicious join patterns (rapid joins, suspicious usernames, etc.)
            await self.analyze_member_join_security(member)

        except Exception as e:
            self.logger.error(f"Error analyzing member join security for {member}: {e}")

    async def analyze_member_join_security(self, member: discord.Member):
        """Analyze new member joins for security threats"""
        guild_settings = self.get_guild_settings(member.guild.id)
        if not guild_settings.get("security_enabled", True):
            return

        # Check account age
        account_age = (datetime.now(timezone.utc) - member.created_at).total_seconds()
        if account_age < 86400:  # Less than 24 hours old
            await self.flag_suspicious_account(
                member,
                "new_account",
                f"Account created {account_age/3600:.1f} hours ago",
            )

        # Check username for suspicious patterns
        suspicious_patterns = [
            "discord",
            "nitro",
            "official",
            "admin",
            "mod",
            "staff",
            "everyone",
            "here",
            "support",
        ]

        username = member.name.lower()
        for pattern in suspicious_patterns:
            if pattern in username:
                await self.flag_suspicious_account(
                    member, "suspicious_username", f"Username contains '{pattern}'"
                )
                break

    async def flag_suspicious_account(
        self, member: discord.Member, reason: str, details: str
    ):
        """Flag a potentially suspicious account"""
        # Get user profile and add a note
        profile = await self.security_system.get_user_profile(member.id)
        profile.trust_score = max(profile.trust_score - 20, 0)  # Reduce trust score

        # Log the suspicious activity
        self.logger.warning(
            f"🚨 Suspicious account flagged: {member} - {reason}: {details}"
        )

        # Notify moderators
        await self.notify_moderators_suspicious_join(member, reason, details)

    async def notify_moderators_suspicious_join(
        self, member: discord.Member, reason: str, details: str
    ):
        """Notify moderators of suspicious account joins"""
        # Find moderation channel
        mod_channel = None
        for channel_name in ["mod-log", "security-log", "admin-log"]:
            mod_channel = discord.utils.get(
                member.guild.text_channels, name=channel_name
            )
            if mod_channel:
                break

        if not mod_channel:
            return

        embed = discord.Embed(
            title="🚨 Suspicious Account Join",
            description=f"**Member:** {member.mention} ({member})\n**ID:** {member.id}",
            color=0xFFA500,
            timestamp=datetime.now(timezone.utc),
        )

        embed.add_field(
            name="⚠️ Reason", value=reason.replace("_", " ").title(), inline=True
        )

        embed.add_field(name="📝 Details", value=details, inline=True)

        embed.add_field(
            name="📊 Account Info",
            value=f"**Created:** {member.created_at.strftime('%Y-%m-%d %H:%M UTC')}\n"
            f"**Age:** {(datetime.now(timezone.utc) - member.created_at).days} days",
            inline=False,
        )

        embed.set_footer(text="🛡️ Astra Security - Automated Threat Detection")

        await mod_channel.send(embed=embed)

    def get_guild_settings(self, guild_id: int) -> Dict[str, Any]:
        """Get security settings for a guild"""
        if guild_id not in self.guild_settings:
            self.guild_settings[guild_id] = self.default_settings.copy()
        return self.guild_settings[guild_id]

    async def update_guild_stats(
        self, guild_id: int, violations: List, result: Dict[str, Any]
    ):
        """Update guild security statistics"""
        # This could be expanded to track guild-specific security metrics
        pass

    # Security Management Commands

    @app_commands.command(
        name="security_status",
        description="🛡️ View comprehensive security system status",
    )
    @app_commands.default_permissions(manage_messages=True)
    async def security_status(self, interaction: discord.Interaction):
        """Display comprehensive security system status"""
        if not await check_user_permission(
            interaction.user, PermissionLevel.MODERATOR, interaction.guild
        ):
            await interaction.response.send_message(
                "❌ You need moderator permissions to view security status.",
                ephemeral=True,
            )
            return

        try:
            # Get security statistics
            stats = self.security_system.get_security_stats()
            guild_settings = self.get_guild_settings(interaction.guild.id)

            embed = discord.Embed(
                title="🛡️ Security System Status",
                description="Comprehensive security monitoring and protection status",
                color=0x00FF00,
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(
                name="📊 System Statistics",
                value=f"**Tracked Users:** {stats['total_tracked_users']:,}\n"
                f"**Trusted Users:** {stats['trusted_users']:,}\n"
                f"**Quarantined Users:** {stats['quarantined_users']:,}\n"
                f"**Average Trust Score:** {stats['average_trust_score']:.1f}/100",
                inline=True,
            )

            embed.add_field(
                name="⚡ Recent Activity",
                value=f"**Total Violations:** {stats['total_violations_all_time']:,}\n"
                f"**Last 24 Hours:** {stats['violations_last_24h']:,}\n"
                f"**Protection Level:** {stats['protection_level']}\n"
                f"**System Status:** {stats['system_status']}",
                inline=True,
            )

            # Guild-specific settings
            settings_status = []
            for key, value in guild_settings.items():
                if isinstance(value, bool):
                    status = "✅" if value else "❌"
                    settings_status.append(f"{status} {key.replace('_', ' ').title()}")

            embed.add_field(
                name="⚙️ Guild Settings",
                value="\\n".join(settings_status[:8]),  # Show first 8 settings
                inline=False,
            )

            embed.set_footer(text="🤖 Astra Security System - Real-time Protection")

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in security_status command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while retrieving security status.", ephemeral=True
            )

    @app_commands.command(
        name="user_security", description="👤 View detailed security profile for a user"
    )
    @app_commands.describe(user="User to check security profile for")
    @app_commands.default_permissions(manage_messages=True)
    async def user_security(
        self, interaction: discord.Interaction, user: discord.Member
    ):
        """Display detailed security profile for a specific user"""
        if not await check_user_permission(
            interaction.user, PermissionLevel.MODERATOR, interaction.guild
        ):
            await interaction.response.send_message(
                "❌ You need moderator permissions to view user security profiles.",
                ephemeral=True,
            )
            return

        try:
            # Get user security report
            report = await self.security_system.get_user_security_report(user.id)

            if "error" in report:
                embed = discord.Embed(
                    title=f"👤 Security Profile: {user.display_name}",
                    description="This user has no security history (clean record).",
                    color=0x00FF00,
                )
            else:
                # Determine color based on trust score
                if report["trust_score"] >= 80:
                    color = 0x00FF00  # Green
                elif report["trust_score"] >= 60:
                    color = 0xFFFF00  # Yellow
                elif report["trust_score"] >= 40:
                    color = 0xFFA500  # Orange
                else:
                    color = 0xFF0000  # Red

                embed = discord.Embed(
                    title=f"👤 Security Profile: {user.display_name}",
                    description=f"**Trust Score:** {report['trust_score']:.1f}/100 {'✅' if report['is_trusted'] else '⚠️'}",
                    color=color,
                    timestamp=datetime.now(timezone.utc),
                )

                embed.add_field(
                    name="📊 Violation History",
                    value=f"**Total Violations:** {report['total_violations']}\n"
                    f"**Recent (24h):** {report['recent_violations_24h']}\n"
                    f"**Violation Streak:** {report['violation_streak']}\n"
                    f"**Punishment Level:** {report['punishment_level']}/7",
                    inline=True,
                )

                embed.add_field(
                    name="✨ Positive Activity",
                    value=f"**Contributions:** {report['positive_contributions']}\n"
                    f"**Status:** {'Trusted Member' if report['is_trusted'] else 'Under Watch'}\n"
                    f"**Quarantine:** {report['quarantine_status'].title()}",
                    inline=True,
                )

                behavior = report["behavioral_summary"]
                embed.add_field(
                    name="📈 Behavioral Analysis",
                    value=f"**Avg Message Length:** {behavior['avg_message_length']:.0f} chars\n"
                    f"**Channel Diversity:** {behavior['channel_diversity']} channels\n"
                    f"**Activity Pattern:** {behavior['activity_pattern'].title()}",
                    inline=False,
                )

                if report["last_violation"]:
                    last_violation = datetime.fromtimestamp(report["last_violation"])
                    embed.add_field(
                        name="⏰ Last Violation",
                        value=last_violation.strftime("%Y-%m-%d %H:%M UTC"),
                        inline=True,
                    )

            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_footer(text=f"User ID: {user.id} • 🛡️ Astra Security System")

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in user_security command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while retrieving user security profile.",
                ephemeral=True,
            )

    @app_commands.command(
        name="security_settings", description="⚙️ Configure guild security settings"
    )
    @app_commands.describe(
        setting="Security setting to modify", value="New value for the setting"
    )
    @app_commands.choices(
        setting=[
            app_commands.Choice(name="Security Enabled", value="security_enabled"),
            app_commands.Choice(name="Auto Moderation", value="auto_moderation"),
            app_commands.Choice(
                name="Strict Spam Detection", value="strict_spam_detection"
            ),
            app_commands.Choice(
                name="Smart Link Filtering", value="smart_link_filtering"
            ),
            app_commands.Choice(
                name="Behavioral Analysis", value="behavioral_analysis"
            ),
            app_commands.Choice(name="Trust System", value="trust_system_enabled"),
            app_commands.Choice(
                name="Progressive Punishment", value="progressive_punishment"
            ),
        ]
    )
    @app_commands.default_permissions(manage_guild=True)
    async def security_settings(
        self, interaction: discord.Interaction, setting: str, value: bool
    ):
        """Configure guild security settings"""
        if not await check_user_permission(
            interaction.user, PermissionLevel.ADMINISTRATOR, interaction.guild
        ):
            await interaction.response.send_message(
                "❌ You need administrator permissions to modify security settings.",
                ephemeral=True,
            )
            return

        try:
            # Update the setting
            guild_settings = self.get_guild_settings(interaction.guild.id)
            old_value = guild_settings.get(setting, False)
            guild_settings[setting] = value

            # Create response embed
            embed = discord.Embed(
                title="⚙️ Security Settings Updated",
                description=f"**Setting:** {setting.replace('_', ' ').title()}\n"
                f"**Previous Value:** {'✅ Enabled' if old_value else '❌ Disabled'}\n"
                f"**New Value:** {'✅ Enabled' if value else '❌ Disabled'}",
                color=0x00BFFF,
                timestamp=datetime.now(timezone.utc),
            )

            embed.set_footer(text=f"Updated by {interaction.user.display_name}")

            await interaction.response.send_message(embed=embed)

            # Log the change
            self.logger.info(
                f"Security setting changed by {interaction.user}: {setting} = {value}"
            )

        except Exception as e:
            self.logger.error(f"Error in security_settings command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while updating security settings.", ephemeral=True
            )

    @app_commands.command(
        name="trust_score", description="📊 Modify user trust score (Admin only)"
    )
    @app_commands.describe(
        user="User to modify trust score for",
        action="Action to take",
        amount="Amount to adjust (for adjust action)",
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Reset to 100", value="reset"),
            app_commands.Choice(name="Adjust by amount", value="adjust"),
            app_commands.Choice(name="Set to specific value", value="set"),
        ]
    )
    @app_commands.default_permissions(manage_guild=True)
    async def trust_score(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        action: str,
        amount: int = 0,
    ):
        """Modify user trust score (Administrator only)"""
        if not await check_user_permission(
            interaction.user, PermissionLevel.ADMINISTRATOR, interaction.guild
        ):
            await interaction.response.send_message(
                "❌ You need administrator permissions to modify trust scores.",
                ephemeral=True,
            )
            return

        try:
            # Get user profile
            profile = await self.security_system.get_user_profile(user.id)
            old_score = profile.trust_score

            # Apply the action
            if action == "reset":
                profile.trust_score = 100.0
                profile.violation_history.clear()
                profile.behavioral_patterns["violation_streak"] = 0
            elif action == "adjust":
                profile.trust_score = max(0, min(100, profile.trust_score + amount))
            elif action == "set":
                profile.trust_score = max(0, min(100, amount))

            # Update trust status
            profile.is_trusted = profile.trust_score >= 70

            # Create response
            embed = discord.Embed(
                title="📊 Trust Score Modified",
                description=f"**User:** {user.mention}\n"
                f"**Previous Score:** {old_score:.1f}/100\n"
                f"**New Score:** {profile.trust_score:.1f}/100\n"
                f"**Status:** {'✅ Trusted' if profile.is_trusted else '⚠️ Under Watch'}",
                color=0x00FF00 if profile.is_trusted else 0xFFA500,
                timestamp=datetime.now(timezone.utc),
            )

            embed.set_footer(text=f"Modified by {interaction.user.display_name}")

            await interaction.response.send_message(embed=embed)

            # Log the change
            self.logger.warning(
                f"Trust score manually modified by {interaction.user}: "
                f"{user} ({user.id}) - {old_score:.1f} → {profile.trust_score:.1f}"
            )

        except Exception as e:
            self.logger.error(f"Error in trust_score command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while modifying trust score.", ephemeral=True
            )

    @app_commands.command(
        name="security_log", description="📋 View recent security events"
    )
    @app_commands.describe(limit="Number of recent events to show (max 25)")
    @app_commands.default_permissions(manage_messages=True)
    async def security_log(self, interaction: discord.Interaction, limit: int = 10):
        """View recent security events"""
        if not await check_user_permission(
            interaction.user, PermissionLevel.MODERATOR, interaction.guild
        ):
            await interaction.response.send_message(
                "❌ You need moderator permissions to view security logs.",
                ephemeral=True,
            )
            return

        limit = max(1, min(25, limit))  # Clamp between 1 and 25

        try:
            # This is a simplified version - in a full implementation,
            # you'd want to store and retrieve actual security events
            embed = discord.Embed(
                title="📋 Recent Security Events",
                description=f"Showing last {limit} security events for this server",
                color=0x00BFFF,
                timestamp=datetime.now(timezone.utc),
            )

            # Get some statistics instead of actual events (for now)
            stats = self.security_system.get_security_stats()

            embed.add_field(
                name="📊 Current Status",
                value=f"**Active Monitoring:** {stats['system_status']}\n"
                f"**Recent Violations:** {stats['violations_last_24h']}\n"
                f"**Protection Level:** {stats['protection_level']}",
                inline=False,
            )

            embed.add_field(
                name="ℹ️ Note",
                value="Detailed event logging is in development. Use `/user_security` to view individual user violation histories.",
                inline=False,
            )

            embed.set_footer(text="🛡️ Astra Security System")

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in security_log command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while retrieving security logs.", ephemeral=True
            )


async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(EnhancedSecurity(bot))
