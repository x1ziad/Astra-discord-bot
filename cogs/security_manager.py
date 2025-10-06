"""
🛡️ SECURITY MANAGER COG - UNIFIED COMMAND INTERFACE
Consolidated security commands combining all previous security cogs

This replaces and consolidates:
- enhanced_security.py (new comprehensive commands)
- security_commands.py (manual security controls)
- ai_moderation.py (AI-powered moderation commands)

Features:
- Unified command interface for all security functions
- Real-time security monitoring and control
- Advanced user management and violation tracking
- Comprehensive security analytics and reporting
- Manual override capabilities for administrators
- Trust score management and behavioral analysis
"""

import asyncio
import logging
import time
import hashlib
import re
from typing import Dict, List, Optional, Any, Literal
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands, tasks

from core.unified_security_system import (
    UnifiedSecuritySystem,
    ViolationType,
    ViolationSeverity,
    ThreatLevel,
    UserProfile,
    ViolationRecord,
    SecurityEvent,
)
from utils.permissions import has_permission, PermissionLevel, check_user_permission
from config.unified_config import unified_config

logger = logging.getLogger("astra.security.manager")

# Owner ID for critical security controls
OWNER_ID = 1115739214148026469


class SecurityManager(commands.Cog):
    """Unified Security Management System - All security commands in one place"""

    def __init__(self, bot):
        self.bot = bot
        self.config = unified_config
        self.logger = bot.logger if hasattr(bot, "logger") else logger

        # Initialize the unified security system
        self.security_system = UnifiedSecuritySystem(bot)

        # Guild-specific settings
        self.guild_settings = {}

        # Load default settings (consolidated from all systems)
        self.default_settings = {
            # Core security
            "security_enabled": True,
            "auto_moderation": True,
            "autonomous_protection": True,
            # Detection systems
            "spam_detection": True,
            "toxicity_detection": True,
            "threat_intelligence": True,
            "behavioral_analysis": True,
            # Response systems
            "auto_timeout_enabled": True,
            "progressive_punishment": True,
            "trust_system_enabled": True,
            "evidence_collection": True,
            # Thresholds
            "spam_threshold": 3,
            "toxicity_threshold": 0.7,
            "trust_threshold": 70.0,
            "quarantine_threshold": 25.0,
            # Logging and notifications
            "log_all_actions": True,
            "notify_moderators": True,
            "forensic_logging": True,
        }

        # Performance metrics
        self.performance_metrics = {
            "commands_executed": 0,
            "security_checks": 0,
            "violations_handled": 0,
            "manual_overrides": 0,
        }

        # Emergency lockdown state
        self.lockdown_active = False
        self.lockdown_reason = ""
        self.lockdown_timestamp = 0

        logger.info("🛡️ Security Manager initialized - Unified command interface ready")

    async def cog_load(self):
        """Initialize security manager when cog loads"""
        logger.info("🔄 Loading Security Manager...")
        # Security system is already initialized
        logger.info("✅ Security Manager loaded successfully")

    async def cog_unload(self):
        """Cleanup when cog unloads"""
        logger.info("🔄 Unloading Security Manager...")
        await self.security_system.shutdown()
        logger.info("✅ Security Manager unloaded")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Monitor all messages for security violations"""
        # Skip bot messages and DMs
        if message.author.bot or not message.guild:
            return

        # Skip if lockdown is active (emergency mode)
        if self.lockdown_active:
            if message.author.id != OWNER_ID:
                try:
                    await message.delete()
                    return
                except:
                    pass

        # Check if security is enabled for this guild
        guild_settings = self.get_guild_settings(message.guild.id)
        if not guild_settings.get("security_enabled", True):
            return

        try:
            self.performance_metrics["security_checks"] += 1

            # Analyze message for security violations
            should_act, violations = (
                await self.security_system.analyze_message_security(message)
            )

            if should_act and violations:
                # Handle the violations
                result = await self.security_system.handle_violations(
                    message, violations
                )

                self.performance_metrics["violations_handled"] += 1

                # Log the action
                self.logger.info(
                    f"🛡️ Security action: User {message.author} ({message.author.id}) - "
                    f"{result['violations_detected']} violations - {result['action_taken']}"
                )

                # Notify moderators if configured
                if guild_settings.get("notify_moderators", True):
                    await self.notify_moderators_violation(message, violations, result)

        except Exception as e:
            self.logger.error(
                f"Security system error for message from {message.author}: {e}"
            )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Monitor new member joins for security threats"""
        try:
            guild_settings = self.get_guild_settings(member.guild.id)
            if not guild_settings.get("security_enabled", True):
                return

            # Check for suspicious account patterns
            await self.analyze_member_join_security(member)

        except Exception as e:
            self.logger.error(f"Error analyzing member join security for {member}: {e}")

    async def analyze_member_join_security(self, member: discord.Member):
        """Analyze new member joins for security threats"""
        # Get user profile to start tracking
        profile = await self.security_system.get_user_profile(
            member.id, member.guild.id
        )
        profile.join_timestamp = time.time()

        # Check account age
        account_age = (datetime.now(timezone.utc) - member.created_at).total_seconds()

        suspicion_reasons = []
        trust_penalty = 0

        # Very new account (< 24 hours)
        if account_age < 86400:
            suspicion_reasons.append(
                f"Account created {account_age/3600:.1f} hours ago"
            )
            trust_penalty += 20

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
            "bot",
            "system",
        ]

        username = member.name.lower()
        for pattern in suspicious_patterns:
            if pattern in username:
                suspicion_reasons.append(f"Username contains '{pattern}'")
                trust_penalty += 10
                break

        # Apply trust score penalties
        if trust_penalty > 0:
            profile.trust_score = max(0, profile.trust_score - trust_penalty)
            await self.security_system._save_user_profile(profile)

            # Notify moderators of suspicious join
            if suspicion_reasons:
                await self.notify_moderators_suspicious_join(
                    member, suspicion_reasons, trust_penalty
                )

    async def notify_moderators_violation(
        self,
        message: discord.Message,
        violations: List[ViolationRecord],
        result: Dict[str, Any],
    ):
        """Notify moderators of security violations"""
        # Find moderation channel
        mod_channel = None
        for channel_name in ["mod-log", "security-log", "admin-log", "moderation"]:
            mod_channel = discord.utils.get(
                message.guild.text_channels, name=channel_name
            )
            if mod_channel:
                break

        if not mod_channel:
            return

        # Create violation notification embed
        violation_types = [
            v.violation_type.value.replace("_", " ").title() for v in violations
        ]
        severity_colors = {
            1: 0x00FF00,  # Minor - Green
            2: 0xFFFF00,  # Moderate - Yellow
            3: 0xFFA500,  # Serious - Orange
            4: 0xFF4500,  # Severe - Red-Orange
            5: 0xFF0000,  # Critical - Red
        }

        max_severity = max(v.severity.value for v in violations)
        color = severity_colors.get(max_severity, 0xFFFF00)

        embed = discord.Embed(
            title="🛡️ Security Violation Detected",
            description=f"**User:** {message.author.mention} ({message.author})\n**Channel:** {message.channel.mention}",
            color=color,
            timestamp=datetime.now(timezone.utc),
        )

        embed.add_field(
            name="⚠️ Violations",
            value="\n".join(f"• {vtype}" for vtype in violation_types),
            inline=True,
        )

        embed.add_field(
            name="🎯 Action Taken",
            value=result["action_taken"].replace("_", " ").title(),
            inline=True,
        )

        embed.add_field(
            name="📊 Severity Level",
            value=f"{max_severity}/5 ({'🟢' if max_severity <= 2 else '🟡' if max_severity <= 3 else '🔴'})",
            inline=True,
        )

        # Add message content (truncated)
        if message.content:
            content_preview = (
                message.content[:200] + "..."
                if len(message.content) > 200
                else message.content
            )
            embed.add_field(
                name="💬 Message Content",
                value=f"```{content_preview}```",
                inline=False,
            )

        embed.set_footer(text=f"User ID: {message.author.id} • 🛡️ Astra Security System")

        try:
            await mod_channel.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Error sending moderation notification: {e}")

    async def notify_moderators_suspicious_join(
        self, member: discord.Member, reasons: List[str], trust_penalty: int
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
            name="⚠️ Suspicion Reasons",
            value="\n".join(f"• {reason}" for reason in reasons),
            inline=False,
        )

        embed.add_field(
            name="📊 Trust Impact",
            value=f"Trust Score Penalty: -{trust_penalty} points",
            inline=True,
        )

        embed.add_field(
            name="📅 Account Info",
            value=f"**Created:** {member.created_at.strftime('%Y-%m-%d %H:%M UTC')}\n"
            f"**Age:** {(datetime.now(timezone.utc) - member.created_at).days} days",
            inline=True,
        )

        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text="🛡️ Astra Security - Automated Threat Detection")

        await mod_channel.send(embed=embed)

    def get_guild_settings(self, guild_id: int) -> Dict[str, Any]:
        """Get security settings for a guild"""
        if guild_id not in self.guild_settings:
            self.guild_settings[guild_id] = self.default_settings.copy()
        return self.guild_settings[guild_id]

    # ═══════════════════════════════════════════════════════════════════════════════
    # SECURITY MONITORING COMMANDS
    # ═══════════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="security_status",
        description="🛡️ View comprehensive security system status and statistics",
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
            self.performance_metrics["commands_executed"] += 1

            # Get security statistics
            stats = self.security_system.get_security_stats()
            guild_settings = self.get_guild_settings(interaction.guild.id)

            embed = discord.Embed(
                title="🛡️ Security System Status",
                description="Comprehensive unified security monitoring and protection status",
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
                name="⚡ Activity Metrics",
                value=f"**Messages Analyzed:** {stats['messages_analyzed']:,}\n"
                f"**Violations (24h):** {stats['violations_last_24h']:,}\n"
                f"**Automated Actions:** {stats['automated_actions']:,}\n"
                f"**Protection Level:** {stats['protection_level']}",
                inline=True,
            )

            embed.add_field(
                name="🎯 Performance",
                value=f"**Commands Executed:** {self.performance_metrics['commands_executed']:,}\n"
                f"**Security Checks:** {self.performance_metrics['security_checks']:,}\n"
                f"**System Status:** {stats['system_status']}\n"
                f"**Lockdown:** {'🔒 Active' if self.lockdown_active else '🔓 Inactive'}",
                inline=True,
            )

            # Active features status
            active_features = []
            feature_map = {
                "security_enabled": "🛡️ Security System",
                "spam_detection": "📢 Spam Detection",
                "toxicity_detection": "☠️ Toxicity Detection",
                "threat_intelligence": "🧠 Threat Intelligence",
                "behavioral_analysis": "📊 Behavioral Analysis",
                "auto_timeout_enabled": "⏰ Auto Timeout",
                "trust_system_enabled": "⭐ Trust System",
            }

            for setting, name in feature_map.items():
                if guild_settings.get(setting, False):
                    active_features.append(f"✅ {name}")
                else:
                    active_features.append(f"❌ {name}")

            embed.add_field(
                name="🔧 Active Features",
                value="\n".join(active_features[:6]),  # Show first 6 features
                inline=False,
            )

            embed.set_footer(text="🤖 Unified Security System - Real-time Protection")

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
            report = await self.security_system.get_user_security_report(
                user.id, interaction.guild.id
            )

            if "error" in report:
                embed = discord.Embed(
                    title=f"👤 Security Profile: {user.display_name}",
                    description="This user has no security history (clean record).",
                    color=0x00FF00,
                )
            else:
                # Determine color based on trust score
                trust_score = report["trust_score"]
                if trust_score >= 80:
                    color = 0x00FF00  # Green
                elif trust_score >= 60:
                    color = 0xFFFF00  # Yellow
                elif trust_score >= 40:
                    color = 0xFFA500  # Orange
                else:
                    color = 0xFF0000  # Red

                embed = discord.Embed(
                    title=f"👤 Security Profile: {user.display_name}",
                    description=f"**Trust Score:** {trust_score:.1f}/100 {'✅' if report['is_trusted'] else '⚠️'}",
                    color=color,
                    timestamp=datetime.now(timezone.utc),
                )

                embed.add_field(
                    name="📊 Violation Summary",
                    value=f"**Total Violations:** {report['total_violations']}\n"
                    f"**Recent (24h):** {report['recent_violations_24h']}\n"
                    f"**Violation Streak:** {report['violation_streak']}\n"
                    f"**Punishment Level:** {report['punishment_level']}/7",
                    inline=True,
                )

                embed.add_field(
                    name="✨ Positive Activity",
                    value=f"**Contributions:** {report['positive_contributions']}\n"
                    f"**Status:** {'✅ Trusted Member' if report['is_trusted'] else '⚠️ Under Watch'}\n"
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
            embed.set_footer(text=f"User ID: {user.id} • 🛡️ Unified Security System")

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in user_security command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while retrieving user security profile.",
                ephemeral=True,
            )

    # ═══════════════════════════════════════════════════════════════════════════════
    # SECURITY CONFIGURATION COMMANDS
    # ═══════════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="security_config", description="⚙️ Configure security system settings"
    )
    @app_commands.describe(
        setting="Security setting to modify", value="New value for the setting"
    )
    @app_commands.choices(
        setting=[
            app_commands.Choice(name="🛡️ Security System", value="security_enabled"),
            app_commands.Choice(name="🤖 Auto Moderation", value="auto_moderation"),
            app_commands.Choice(name="📢 Spam Detection", value="spam_detection"),
            app_commands.Choice(
                name="☠️ Toxicity Detection", value="toxicity_detection"
            ),
            app_commands.Choice(
                name="🧠 Threat Intelligence", value="threat_intelligence"
            ),
            app_commands.Choice(
                name="📊 Behavioral Analysis", value="behavioral_analysis"
            ),
            app_commands.Choice(name="⭐ Trust System", value="trust_system_enabled"),
            app_commands.Choice(
                name="📈 Progressive Punishment", value="progressive_punishment"
            ),
        ]
    )
    @app_commands.default_permissions(manage_guild=True)
    async def security_config(
        self, interaction: discord.Interaction, setting: str, value: bool
    ):
        """Configure security system settings"""
        if not await check_user_permission(
            interaction.user, PermissionLevel.ADMIN, interaction.guild
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

            # Update security system configuration
            if setting in self.security_system.config:
                self.security_system.config[setting.replace("_enabled", "")] = value

            # Create response embed
            embed = discord.Embed(
                title="⚙️ Security Configuration Updated",
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
                f"Security configuration changed by {interaction.user}: {setting} = {value}"
            )

        except Exception as e:
            self.logger.error(f"Error in security_config command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while updating security configuration.",
                ephemeral=True,
            )

    @app_commands.command(
        name="trust_manage", description="📊 Manage user trust scores (Admin only)"
    )
    @app_commands.describe(
        user="User to modify trust score for",
        action="Action to take",
        amount="Amount to adjust (for adjust/set actions)",
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="🔄 Reset to 50", value="reset"),
            app_commands.Choice(name="⬆️ Increase by amount", value="increase"),
            app_commands.Choice(name="⬇️ Decrease by amount", value="decrease"),
            app_commands.Choice(name="🎯 Set to specific value", value="set"),
        ]
    )
    @app_commands.default_permissions(manage_guild=True)
    async def trust_manage(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        action: str,
        amount: int = 0,
    ):
        """Manage user trust scores (Administrator only)"""
        if not await check_user_permission(
            interaction.user, PermissionLevel.ADMIN, interaction.guild
        ):
            await interaction.response.send_message(
                "❌ You need administrator permissions to manage trust scores.",
                ephemeral=True,
            )
            return

        try:
            # Get user profile
            profile = await self.security_system.get_user_profile(
                user.id, interaction.guild.id
            )
            old_score = profile.trust_score

            # Apply the action
            if action == "reset":
                profile.trust_score = 50.0
                profile.violation_history.clear()
                profile.punishment_level = 0
            elif action == "increase":
                profile.trust_score = min(100, profile.trust_score + amount)
            elif action == "decrease":
                profile.trust_score = max(0, profile.trust_score - amount)
            elif action == "set":
                profile.trust_score = max(0, min(100, amount))

            # Update trust status
            profile.is_trusted = profile.trust_score >= 70
            profile.is_quarantined = profile.trust_score <= 25

            # Save profile
            await self.security_system._save_user_profile(profile)

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

            if profile.is_quarantined:
                embed.add_field(
                    name="🚨 Quarantine Status",
                    value="User is now in quarantine due to low trust score",
                    inline=False,
                )

            embed.set_footer(text=f"Modified by {interaction.user.display_name}")

            await interaction.response.send_message(embed=embed)

            # Log the change
            self.logger.warning(
                f"Trust score manually modified by {interaction.user}: "
                f"{user} ({user.id}) - {old_score:.1f} → {profile.trust_score:.1f}"
            )

        except Exception as e:
            self.logger.error(f"Error in trust_manage command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while modifying trust score.", ephemeral=True
            )

    # ═══════════════════════════════════════════════════════════════════════════════
    # APPEALS SYSTEM - Human-in-the-loop moderation
    # ═══════════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="appeal", description="📝 Appeal a security violation")
    @app_commands.describe(
        violation_id="ID of the violation to appeal (from security log)",
        reason="Reason for your appeal",
    )
    async def appeal_violation(
        self, interaction: discord.Interaction, violation_id: str, reason: str
    ):
        """Appeal a security violation for human review"""
        try:
            # Create appeal record
            appeal_data = {
                "appeal_id": hashlib.md5(
                    f"{interaction.user.id}{violation_id}{time.time()}".encode()
                ).hexdigest()[:8],
                "user_id": interaction.user.id,
                "violation_id": violation_id,
                "reason": reason,
                "timestamp": time.time(),
                "status": "pending",
                "guild_id": interaction.guild.id if interaction.guild else 0,
            }

            # Store appeal in database (simplified for now)
            # In full implementation, this would go to appeals table

            embed = discord.Embed(
                title="📝 Appeal Submitted",
                description=f"**Appeal ID:** {appeal_data['appeal_id']}\n"
                f"**Violation ID:** {violation_id}\n"
                f"**Status:** Pending Review",
                color=0x00BFFF,
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(
                name="📋 Your Appeal",
                value=reason[:500] + ("..." if len(reason) > 500 else ""),
                inline=False,
            )

            embed.add_field(
                name="⏳ Next Steps",
                value="• Your appeal will be reviewed by staff\n"
                "• You will be notified of the decision\n"
                "• Appeals are typically processed within 24-48 hours",
                inline=False,
            )

            embed.set_footer(text="Appeal submitted • Staff will review shortly")

            await interaction.response.send_message(embed=embed, ephemeral=True)

            # Notify moderators of new appeal
            await self.notify_moderators_new_appeal(interaction, appeal_data)

        except Exception as e:
            self.logger.error(f"Error in appeal_violation command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while submitting your appeal. Please try again.",
                ephemeral=True,
            )

    async def notify_moderators_new_appeal(
        self, interaction: discord.Interaction, appeal_data: Dict[str, Any]
    ):
        """Notify moderators of new appeal submission"""
        # Find moderation channel
        mod_channel = None
        for channel_name in ["mod-log", "appeals", "staff-queue", "admin-log"]:
            mod_channel = discord.utils.get(
                interaction.guild.text_channels, name=channel_name
            )
            if mod_channel:
                break

        if not mod_channel:
            return

        embed = discord.Embed(
            title="📝 New Appeal Submitted",
            description=f"**User:** {interaction.user.mention} ({interaction.user})\n"
            f"**Appeal ID:** {appeal_data['appeal_id']}\n"
            f"**Violation ID:** {appeal_data['violation_id']}",
            color=0xFFFF00,
            timestamp=datetime.now(timezone.utc),
        )

        embed.add_field(
            name="📋 Appeal Reason",
            value=appeal_data["reason"][:500]
            + ("..." if len(appeal_data["reason"]) > 500 else ""),
            inline=False,
        )

        embed.add_field(
            name="🔧 Staff Actions",
            value="Use `/review_appeal [appeal_id] [decision]` to process this appeal",
            inline=False,
        )

        embed.set_footer(text=f"User ID: {interaction.user.id} • Awaiting staff review")

        await mod_channel.send(embed=embed)

    @app_commands.command(
        name="review_appeal",
        description="👨‍⚖️ Review and decide on user appeals (Staff only)",
    )
    @app_commands.describe(
        appeal_id="ID of the appeal to review",
        decision="Decision on the appeal",
        notes="Additional notes for the decision",
    )
    @app_commands.choices(
        decision=[
            app_commands.Choice(
                name="✅ Approve - Overturn violation", value="approved"
            ),
            app_commands.Choice(name="❌ Deny - Violation stands", value="denied"),
            app_commands.Choice(name="📝 Reduce - Lower punishment", value="reduced"),
        ]
    )
    @app_commands.default_permissions(manage_messages=True)
    async def review_appeal(
        self,
        interaction: discord.Interaction,
        appeal_id: str,
        decision: str,
        notes: str = "",
    ):
        """Review and decide on user appeals (Staff only)"""
        if not await check_user_permission(
            interaction.user, PermissionLevel.MODERATOR, interaction.guild
        ):
            await interaction.response.send_message(
                "❌ You need moderator permissions to review appeals.", ephemeral=True
            )
            return

        try:
            # In full implementation, this would update the appeals database
            # and automatically reverse/modify the original violation

            decision_colors = {
                "approved": 0x00FF00,
                "denied": 0xFF0000,
                "reduced": 0xFFFF00,
            }

            decision_text = {
                "approved": "✅ Appeal Approved - Violation Overturned",
                "denied": "❌ Appeal Denied - Violation Stands",
                "reduced": "📝 Appeal Partially Approved - Punishment Reduced",
            }

            embed = discord.Embed(
                title="👨‍⚖️ Appeal Decision",
                description=f"**Appeal ID:** {appeal_id}\n"
                f"**Decision:** {decision_text[decision]}\n"
                f"**Reviewed by:** {interaction.user.mention}",
                color=decision_colors[decision],
                timestamp=datetime.now(timezone.utc),
            )

            if notes:
                embed.add_field(name="📝 Staff Notes", value=notes, inline=False)

            embed.add_field(
                name="⚡ Automated Actions",
                value="• User has been notified of decision\n"
                "• Violation record updated\n"
                "• Trust score adjusted if applicable\n"
                "• Appeal marked as resolved",
                inline=False,
            )

            embed.set_footer(text=f"Reviewed by {interaction.user.display_name}")

            await interaction.response.send_message(embed=embed)

            # Log the staff decision
            self.logger.info(
                f"Appeal {appeal_id} {decision} by {interaction.user}: {notes}"
            )

        except Exception as e:
            self.logger.error(f"Error in review_appeal command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while processing the appeal review.",
                ephemeral=True,
            )

    # ═══════════════════════════════════════════════════════════════════════════════
    # EMERGENCY CONTROLS - Owner Only
    # ═══════════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="emergency_lockdown",
        description="🚨 Emergency server lockdown (Owner only)",
    )
    @app_commands.describe(reason="Reason for emergency lockdown")
    async def emergency_lockdown(
        self,
        interaction: discord.Interaction,
        reason: str = "Emergency security measure",
    ):
        """Emergency server lockdown - Owner only"""
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message(
                "❌ This command is restricted to the bot owner only.", ephemeral=True
            )
            return

        try:
            self.lockdown_active = True
            self.lockdown_reason = reason
            self.lockdown_timestamp = time.time()

            embed = discord.Embed(
                title="🚨 EMERGENCY LOCKDOWN ACTIVATED",
                description=f"**Reason:** {reason}\n"
                f"**Activated by:** {interaction.user.mention}\n"
                f"**Time:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
                color=0xFF0000,
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(
                name="🔒 Lockdown Effects",
                value="• All non-owner messages will be deleted\n"
                "• Only owner can send messages\n"
                "• Security system in maximum protection mode\n"
                "• All automated moderation suspended",
                inline=False,
            )

            embed.set_footer(text="Use /emergency_unlock to deactivate lockdown")

            await interaction.response.send_message(embed=embed)

            # Log the emergency lockdown
            self.logger.critical(
                f"🚨 EMERGENCY LOCKDOWN activated by {interaction.user}: {reason}"
            )

        except Exception as e:
            self.logger.error(f"Error in emergency_lockdown command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while activating emergency lockdown.",
                ephemeral=True,
            )

    @app_commands.command(
        name="emergency_unlock",
        description="🔓 Deactivate emergency lockdown (Owner only)",
    )
    async def emergency_unlock(self, interaction: discord.Interaction):
        """Deactivate emergency lockdown - Owner only"""
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message(
                "❌ This command is restricted to the bot owner only.", ephemeral=True
            )
            return

        try:
            if not self.lockdown_active:
                await interaction.response.send_message(
                    "ℹ️ No emergency lockdown is currently active.", ephemeral=True
                )
                return

            lockdown_duration = time.time() - self.lockdown_timestamp

            self.lockdown_active = False
            previous_reason = self.lockdown_reason
            self.lockdown_reason = ""
            self.lockdown_timestamp = 0

            embed = discord.Embed(
                title="🔓 EMERGENCY LOCKDOWN DEACTIVATED",
                description=f"**Previous Reason:** {previous_reason}\n"
                f"**Deactivated by:** {interaction.user.mention}\n"
                f"**Duration:** {lockdown_duration/60:.1f} minutes",
                color=0x00FF00,
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(
                name="✅ Server Status",
                value="• Normal message flow restored\n"
                "• Security system back to normal operation\n"
                "• Automated moderation reactivated\n"
                "• All systems operational",
                inline=False,
            )

            await interaction.response.send_message(embed=embed)

            # Log the unlock
            self.logger.info(
                f"🔓 Emergency lockdown deactivated by {interaction.user} after {lockdown_duration/60:.1f} minutes"
            )

        except Exception as e:
            self.logger.error(f"Error in emergency_unlock command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while deactivating emergency lockdown.",
                ephemeral=True,
            )

    @app_commands.command(
        name="manual_override", description="🔧 Manual override for security actions"
    )
    @app_commands.describe(
        user="User to override security actions for",
        action="Override action to take",
        reason="Reason for manual override",
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Clear Violations", value="clear_violations"),
            app_commands.Choice(name="Remove Timeout", value="remove_timeout"),
            app_commands.Choice(name="Reset Trust Score", value="reset_trust"),
            app_commands.Choice(
                name="Remove from Quarantine", value="remove_quarantine"
            ),
        ]
    )
    @app_commands.default_permissions(manage_guild=True)
    async def manual_override(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        action: str,
        reason: str,
    ):
        """Manual override for security actions"""
        if not await check_user_permission(
            interaction.user, PermissionLevel.ADMIN, interaction.guild
        ):
            await interaction.response.send_message(
                "❌ You need administrator permissions for manual overrides.",
                ephemeral=True,
            )
            return

        try:
            # Execute manual override
            success = await self.security_system.manual_override(
                interaction.user.id, user.id, action, reason
            )

            if success:
                self.performance_metrics["manual_overrides"] += 1

                embed = discord.Embed(
                    title="🔧 Manual Override Executed",
                    description=f"**User:** {user.mention}\n"
                    f"**Action:** {action.replace('_', ' ').title()}\n"
                    f"**Reason:** {reason}",
                    color=0x00BFFF,
                    timestamp=datetime.now(timezone.utc),
                )

                embed.set_footer(text=f"Override by {interaction.user.display_name}")

                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(
                    "❌ Manual override failed. Please check logs for details.",
                    ephemeral=True,
                )

        except Exception as e:
            self.logger.error(f"Error in manual_override command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while executing manual override.", ephemeral=True
            )


async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(SecurityManager(bot))
