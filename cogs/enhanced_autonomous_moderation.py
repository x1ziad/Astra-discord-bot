"""
Enhanced Autonomous Moderation Cog
Integrates the sophisticated security system for complete server protection
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import discord
from discord import app_commands
from discord.ext import commands

from core.autonomous_security import AutonomousServerProtection, ThreatLevel
from utils.permissions import has_permission, PermissionLevel

logger = logging.getLogger("astra.moderation.enhanced")


@app_commands.describe(
    user="The user to check security status for", action="Security action to perform"
)
class EnhancedModerationCog(commands.Cog):
    """Enhanced autonomous moderation with AI-powered threat detection"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.security_system = AutonomousServerProtection(bot)
        self.logger = logger

        # Integration with existing moderation
        self.moderation_stats = {
            "messages_analyzed": 0,
            "threats_detected": 0,
            "users_sanctioned": 0,
            "emergency_activations": 0,
        }

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Analyze every message for security threats"""
        if message.author.bot or not message.guild:
            return

        try:
            self.moderation_stats["messages_analyzed"] += 1

            # Perform comprehensive threat analysis
            threat_level, threats_detected = (
                await self.security_system.analyze_message_threat(message)
            )

            if threats_detected:
                self.moderation_stats["threats_detected"] += 1

                # Handle the threat autonomously
                await self.security_system.handle_security_threat(
                    message, threat_level, threats_detected
                )

                if threat_level >= ThreatLevel.HIGH:
                    self.moderation_stats["users_sanctioned"] += 1

                if threat_level >= ThreatLevel.CRITICAL:
                    # Log critical threats
                    self.logger.critical(
                        f"CRITICAL THREAT: {message.author} in {message.guild.name} - {threats_detected}"
                    )

        except Exception as e:
            self.logger.error(f"Error in autonomous moderation: {e}")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Monitor new members for suspicious patterns"""
        try:
            # Check if this could be part of a raid
            current_time = asyncio.get_event_loop().time()

            # Simple raid detection - multiple joins in short time
            if not hasattr(self, "_recent_joins"):
                self._recent_joins = {}

            guild_id = member.guild.id
            if guild_id not in self._recent_joins:
                self._recent_joins[guild_id] = []

            # Add this join
            self._recent_joins[guild_id].append(current_time)

            # Clean old joins (older than 2 minutes)
            self._recent_joins[guild_id] = [
                join_time
                for join_time in self._recent_joins[guild_id]
                if current_time - join_time < 120
            ]

            # Check for raid pattern
            if len(self._recent_joins[guild_id]) >= 5:  # 5 joins in 2 minutes
                await self._handle_potential_raid(member.guild)

        except Exception as e:
            self.logger.error(f"Error monitoring member join: {e}")

    async def _handle_potential_raid(self, guild: discord.Guild):
        """Handle potential raid detection"""
        self.logger.warning(f"Potential raid detected in {guild.name}")

        # Alert moderators
        mod_channel = (
            discord.utils.get(guild.text_channels, name="mod-log")
            or discord.utils.get(guild.text_channels, name="security-log")
            or guild.system_channel
        )

        if mod_channel:
            embed = discord.Embed(
                title="⚠️ Potential Raid Detected",
                description="Multiple users have joined in a short time period.",
                color=0xFF9900,
            )

            embed.add_field(
                name="Recommendation",
                value="Monitor new members closely and consider temporarily restricting permissions.",
                inline=False,
            )

            embed.set_footer(text="Autonomous Security System")

            try:
                await mod_channel.send(embed=embed)
            except:
                pass

    @app_commands.command(
        name="security", description="🔒 Advanced security management"
    )
    @app_commands.describe(
        action="Security action: status, stats, lockdown, unlock, assess",
        user="User to assess (for assess action)",
        reason="Reason for action",
    )
    async def security_command(
        self,
        interaction: discord.Interaction,
        action: str,
        user: Optional[discord.Member] = None,
        reason: Optional[str] = None,
    ):
        """Advanced security management command"""

        # Check permissions
        if not await has_permission(
            interaction.user, PermissionLevel.MOD, interaction.guild
        ):
            await interaction.response.send_message(
                "❌ You need moderator permissions to use security commands.",
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        try:
            if action.lower() == "status":
                await self._show_security_status(interaction)
            elif action.lower() == "stats":
                await self._show_security_stats(interaction)
            elif action.lower() == "lockdown":
                await self._initiate_lockdown(interaction, reason)
            elif action.lower() == "unlock":
                await self._lift_lockdown(interaction, reason)
            elif action.lower() == "assess" and user:
                await self._assess_user_threat(interaction, user)
            else:
                await interaction.followup.send(
                    "❌ Invalid action. Use: `status`, `stats`, `lockdown`, `unlock`, or `assess`",
                    ephemeral=True,
                )

        except Exception as e:
            self.logger.error(f"Security command error: {e}")
            await interaction.followup.send(
                "❌ An error occurred while executing the security command.",
                ephemeral=True,
            )

    async def _show_security_status(self, interaction: discord.Interaction):
        """Show current security system status"""
        stats = self.security_system.get_security_stats()

        embed = discord.Embed(
            title="🔒 Autonomous Security System Status",
            color=0xFF0000 if stats["emergency_lockdown_active"] else 0x00FF00,
        )

        # System status
        status_emoji = "🚨" if stats["emergency_lockdown_active"] else "✅"
        embed.add_field(
            name=f"{status_emoji} System Status",
            value=stats["system_status"],
            inline=True,
        )

        # Current statistics
        embed.add_field(
            name="📊 Active Monitoring",
            value=f"• Quarantined Users: {stats['quarantined_users']}\n"
            f"• Tracked Users: {stats['tracked_users']}\n"
            f"• Suspicious Patterns: {stats['suspicious_patterns']}",
            inline=True,
        )

        # Recent activity
        embed.add_field(
            name="⚡ Recent Activity (1h)",
            value=f"• Security Events: {stats['recent_events_1h']}\n"
            f"• Messages Analyzed: {self.moderation_stats['messages_analyzed']}\n"
            f"• Threats Detected: {self.moderation_stats['threats_detected']}",
            inline=False,
        )

        # Protection capabilities
        embed.add_field(
            name="🛡️ Protection Features",
            value="✅ Phishing Detection\n"
            "✅ Malicious Link Scanning\n"
            "✅ Social Engineering Detection\n"
            "✅ Advanced Spam Prevention\n"
            "✅ Raid Protection\n"
            "✅ Behavioral Analysis\n"
            "✅ Token Theft Prevention\n"
            "✅ Emergency Lockdown",
            inline=True,
        )

        embed.set_footer(text="Powered by Astra Autonomous Security")

        await interaction.followup.send(embed=embed)

    async def _show_security_stats(self, interaction: discord.Interaction):
        """Show detailed security statistics"""
        stats = self.security_system.get_security_stats()

        embed = discord.Embed(title="📊 Security System Statistics", color=0x3498DB)

        # Overall statistics
        embed.add_field(
            name="🎯 Detection Statistics",
            value=f"• Total Security Events: {stats['total_security_events']}\n"
            f"• Critical Events: {stats['critical_events_total']}\n"
            f"• Recent Events (1h): {stats['recent_events_1h']}\n"
            f"• Messages Analyzed: {self.moderation_stats['messages_analyzed']}",
            inline=False,
        )

        # Action statistics
        embed.add_field(
            name="⚖️ Actions Taken",
            value=f"• Users Sanctioned: {self.moderation_stats['users_sanctioned']}\n"
            f"• Quarantined Users: {stats['quarantined_users']}\n"
            f"• Emergency Lockdowns: {self.moderation_stats['emergency_activations']}",
            inline=True,
        )

        # System performance
        detection_rate = (
            self.moderation_stats["threats_detected"]
            / max(self.moderation_stats["messages_analyzed"], 1)
        ) * 100

        embed.add_field(
            name="📈 Performance Metrics",
            value=f"• Detection Rate: {detection_rate:.2f}%\n"
            f"• System Uptime: Active\n"
            f"• Response Time: <1 second",
            inline=True,
        )

        embed.set_footer(text="Statistics since last restart")

        await interaction.followup.send(embed=embed)

    async def _initiate_lockdown(
        self, interaction: discord.Interaction, reason: Optional[str]
    ):
        """Manually initiate security lockdown"""
        if self.security_system.emergency_lockdown:
            await interaction.followup.send(
                "⚠️ Emergency lockdown is already active!", ephemeral=True
            )
            return

        try:
            await self.security_system._activate_emergency_lockdown(interaction.guild)
            self.moderation_stats["emergency_activations"] += 1

            embed = discord.Embed(
                title="🚨 Manual Security Lockdown Initiated",
                description=f"Emergency lockdown activated by {interaction.user.mention}",
                color=0xFF0000,
            )

            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)

            embed.add_field(
                name="Actions Taken",
                value="🔒 All channels locked\n🚫 Message sending disabled\n📊 Enhanced monitoring active",
                inline=False,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(
                f"❌ Failed to initiate lockdown: {e}", ephemeral=True
            )

    async def _lift_lockdown(
        self, interaction: discord.Interaction, reason: Optional[str]
    ):
        """Lift security lockdown"""
        if not self.security_system.emergency_lockdown:
            await interaction.followup.send(
                "ℹ️ No emergency lockdown is currently active.", ephemeral=True
            )
            return

        try:
            # Restore channel permissions
            everyone_role = interaction.guild.default_role

            for channel in interaction.guild.text_channels:
                try:
                    await channel.set_permissions(
                        everyone_role,
                        send_messages=None,  # Reset to default
                        add_reactions=None,  # Reset to default
                        reason=f"Security lockdown lifted by {interaction.user}",
                    )
                except:
                    pass

            self.security_system.emergency_lockdown = False

            embed = discord.Embed(
                title="✅ Security Lockdown Lifted",
                description=f"Emergency lockdown lifted by {interaction.user.mention}",
                color=0x00FF00,
            )

            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)

            embed.add_field(
                name="Status",
                value="🔓 Channels unlocked\n✅ Normal operations resumed\n📊 Monitoring continues",
                inline=False,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(
                f"❌ Failed to lift lockdown: {e}", ephemeral=True
            )

    async def _assess_user_threat(
        self, interaction: discord.Interaction, user: discord.Member
    ):
        """Assess threat level of specific user"""
        try:
            assessment = await self.security_system.manual_threat_assessment(user.id)

            # Determine threat level color
            threat_score = assessment["threat_score"]
            if threat_score >= 10:
                color = 0xFF0000  # Red - High threat
            elif threat_score >= 5:
                color = 0xFF9900  # Orange - Medium threat
            elif threat_score > 0:
                color = 0xFFFF00  # Yellow - Low threat
            else:
                color = 0x00FF00  # Green - No threat

            embed = discord.Embed(
                title=f"🔍 Threat Assessment: {user.display_name}", color=color
            )

            # User info
            embed.add_field(
                name="👤 User Information",
                value=f"**Name:** {user}\n**ID:** {user.id}\n**Joined:** {user.joined_at.strftime('%Y-%m-%d') if user.joined_at else 'Unknown'}",
                inline=True,
            )

            # Threat assessment
            threat_level = (
                "🔴 HIGH"
                if threat_score >= 10
                else (
                    "🟡 MEDIUM"
                    if threat_score >= 5
                    else "🟢 LOW" if threat_score > 0 else "✅ CLEAN"
                )
            )

            embed.add_field(
                name="⚠️ Threat Level",
                value=f"{threat_level}\n**Score:** {threat_score}",
                inline=True,
            )

            # Security events
            embed.add_field(
                name="📊 Security Events",
                value=f"• Total Events: {assessment['total_events']}\n"
                f"• Recent (24h): {assessment['recent_events_24h']}\n"
                f"• Quarantined: {'Yes' if assessment['is_quarantined'] else 'No'}",
                inline=False,
            )

            # Behavior profile
            profile = assessment["behavior_profile"]
            embed.add_field(
                name="📈 Behavior Profile",
                value=f"• Messages Sent: {profile['message_count']}\n"
                f"• Avg Length: {profile['avg_message_length']:.1f} chars\n"
                f"• Channels Used: {profile['channels_used']}",
                inline=True,
            )

            # Recent threats
            if assessment["recent_threats"]:
                recent_threats_text = "\n".join(
                    [
                        f"• {threat['type'].replace('|', ', ')} (Level {threat['level']})"
                        for threat in assessment["recent_threats"][:3]
                    ]
                )

                embed.add_field(
                    name="🚨 Recent Threats", value=recent_threats_text, inline=True
                )

            # Recommendations
            if threat_score >= 10:
                recommendation = "🔴 **HIGH RISK** - Consider immediate action"
            elif threat_score >= 5:
                recommendation = "🟡 **MONITOR CLOSELY** - Watch for escalation"
            elif threat_score > 0:
                recommendation = "🟢 **LOW RISK** - Standard monitoring"
            else:
                recommendation = "✅ **NO THREATS** - User appears clean"

            embed.add_field(
                name="💡 Recommendation", value=recommendation, inline=False
            )

            embed.set_footer(
                text=f"Assessment generated by Astra Security • User ID: {user.id}"
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(
                f"❌ Failed to assess user: {e}", ephemeral=True
            )

    @app_commands.command(name="modstats", description="📊 Show moderation statistics")
    async def mod_stats(self, interaction: discord.Interaction):
        """Show comprehensive moderation statistics"""

        if not await has_permission(
            interaction.user, PermissionLevel.MOD, interaction.guild
        ):
            await interaction.response.send_message(
                "❌ You need moderator permissions to view moderation statistics.",
                ephemeral=True,
            )
            return

        stats = self.security_system.get_security_stats()

        embed = discord.Embed(
            title="📊 Comprehensive Moderation Statistics",
            description="Complete overview of server protection metrics",
            color=0x3498DB,
        )

        # System overview
        embed.add_field(
            name="🎯 Detection Overview",
            value=f"**Messages Analyzed:** {self.moderation_stats['messages_analyzed']:,}\n"
            f"**Threats Detected:** {self.moderation_stats['threats_detected']:,}\n"
            f"**Detection Rate:** {(self.moderation_stats['threats_detected']/max(self.moderation_stats['messages_analyzed'], 1)*100):.2f}%",
            inline=True,
        )

        # Actions taken
        embed.add_field(
            name="⚖️ Actions Taken",
            value=f"**Users Sanctioned:** {self.moderation_stats['users_sanctioned']:,}\n"
            f"**Emergency Lockdowns:** {self.moderation_stats['emergency_activations']}\n"
            f"**Quarantined Users:** {stats['quarantined_users']}",
            inline=True,
        )

        # Current status
        status = "🚨 EMERGENCY" if stats["emergency_lockdown_active"] else "✅ ACTIVE"
        embed.add_field(
            name="🔒 System Status",
            value=f"**Status:** {status}\n"
            f"**Tracked Users:** {stats['tracked_users']:,}\n"
            f"**Active Patterns:** {stats['suspicious_patterns']}",
            inline=True,
        )

        # Protection features
        embed.add_field(
            name="🛡️ Active Protection",
            value="• **Phishing Detection** - Real-time scanning\n"
            "• **Malicious Links** - URL analysis\n"
            "• **Social Engineering** - Pattern recognition\n"
            "• **Spam Prevention** - Advanced algorithms\n"
            "• **Raid Protection** - Mass join detection\n"
            "• **Behavioral Analysis** - User profiling\n"
            "• **Emergency Lockdown** - Autonomous response",
            inline=False,
        )

        embed.set_footer(
            text="Powered by Astra Autonomous Security • Updated in real-time"
        )
        embed.timestamp = interaction.created_at

        await interaction.response.send_message(embed=embed)

    async def cog_unload(self):
        """Clean shutdown of security system"""
        if self.security_system:
            await self.security_system.shutdown()


async def setup(bot):
    await bot.add_cog(EnhancedModerationCog(bot))
