"""
Enhanced Server Management with Astra Intelligence
Sophisticated server management with personalized responses and community building
"""

import discord
from discord import app_commands
from discord.ext import commands, tasks
from typing import Optional, List, Dict, Any, Union
import asyncio
import json
import time
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
import colorsys
import re

from config.unified_config import unified_config
from utils.permissions import has_permission, PermissionLevel, check_user_permission

try:
    from ai.multi_provider_ai import MultiProviderAIManager

    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

import logging

logger = logging.getLogger("astra.enhanced_server_management")


class CommunityHealth:
    """Track community health and engagement metrics"""

    def __init__(self):
        self.engagement_score = 100
        self.activity_trends = {}
        self.member_satisfaction = {}
        self.community_events = []
        self.positive_interactions = 0
        self.issues_resolved = 0
        self.last_assessment = time.time()


class EnhancedServerManagement(commands.GroupCog, name="server"):
    """Enhanced server management with Astra intelligence"""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.config = unified_config
        self.logger = bot.logger if hasattr(bot, "logger") else logger

        # Community tracking
        self.community_health = {}  # guild_id -> CommunityHealth
        self.member_welcomes = {}  # guild_id -> welcome_settings
        self.activity_tracking = {}  # guild_id -> activity_data

        # Astra intelligence features
        self.companion_settings = {
            "personality_adaptation": True,
            "proactive_assistance": True,
            "community_insights": True,
            "celebration_mode": True,
            "wellness_checks": True,
        }

        # Start background tasks
        self.health_monitoring.start()
        self.proactive_assistance.start()

    def cog_unload(self):
        self.health_monitoring.cancel()
        self.proactive_assistance.cancel()

    async def get_community_health(self, guild_id: int) -> CommunityHealth:
        """Get or create community health tracker"""
        if guild_id not in self.community_health:
            self.community_health[guild_id] = CommunityHealth()
        return self.community_health[guild_id]

    @app_commands.command(
        name="setup", description="🚀 Interactive server setup with AI guidance"
    )
    @app_commands.default_permissions(administrator=True)
    async def interactive_setup(self, interaction: discord.Interaction):
        """Interactive server setup with AI-powered recommendations"""
        if not await check_user_permission(
            interaction.user, PermissionLevel.ADMINISTRATOR, interaction.guild
        ):
            await interaction.response.send_message(
                "❌ You need administrator permissions for this command.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(thinking=True)

        try:
            guild = interaction.guild
            setup_data = await self._analyze_server_needs(guild)

            if AI_AVAILABLE:
                ai_recommendations = await self._generate_setup_recommendations(
                    guild, setup_data
                )
            else:
                ai_recommendations = self._generate_fallback_setup()

            # Create interactive setup embed
            embed = discord.Embed(
                title="🚀 Smart Server Setup Assistant",
                description=f"Hi {interaction.user.mention}! I'm Astra. Let me optimize **{guild.name}** for maximum engagement and community health! 🌟",
                color=0x00BFFF,
                timestamp=datetime.now(timezone.utc),
            )

            # Server analysis results
            embed.add_field(
                name="📊 Server Analysis",
                value=f"**Members:** {guild.member_count:,}\n"
                f"**Channels:** {len(guild.channels)}\n"
                f"**Roles:** {len(guild.roles)}\n"
                f"**Setup Score:** {setup_data.get('setup_score', 75)}/100",
                inline=True,
            )

            # AI recommendations
            embed.add_field(
                name="🤖 AI Recommendations",
                value=ai_recommendations.get(
                    "priority_recommendations",
                    "• Set up welcome system\n• Create moderation channels\n• Organize role structure",
                ),
                inline=True,
            )

            # Quick actions
            embed.add_field(
                name="⚡ Quick Actions Available",
                value="• `/server welcome` - Setup welcome system\n"
                "• `/server roles optimize` - Optimize role colors\n"
                "• `/server channels organize` - Channel organization\n"
                "• `/server community analyze` - Community health check",
                inline=False,
            )

            embed.set_footer(
                text="💡 Use the commands above to get started, or ask me for specific help!"
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Setup command error: {e}")
            await interaction.followup.send(
                "❌ Setup analysis failed. Please try again."
            )

    async def _analyze_server_needs(self, guild: discord.Guild) -> Dict[str, Any]:
        """Analyze server to determine setup needs"""
        analysis = {
            "setup_score": 100,
            "missing_features": [],
            "optimization_opportunities": [],
            "community_readiness": "good",
        }

        # Check essential channels
        has_welcome = any("welcome" in ch.name.lower() for ch in guild.text_channels)
        has_rules = any("rule" in ch.name.lower() for ch in guild.text_channels)
        has_general = any("general" in ch.name.lower() for ch in guild.text_channels)

        if not has_welcome:
            analysis["missing_features"].append("Welcome channel")
            analysis["setup_score"] -= 15
        if not has_rules:
            analysis["missing_features"].append("Rules channel")
            analysis["setup_score"] -= 10
        if not has_general:
            analysis["missing_features"].append("General chat")
            analysis["setup_score"] -= 5

        # Check role structure
        non_bot_roles = [
            r for r in guild.roles if not r.managed and r.name != "@everyone"
        ]
        if len(non_bot_roles) < 3:
            analysis["missing_features"].append("Role structure")
            analysis["setup_score"] -= 10

        # Check moderation setup
        has_mod_channel = any("mod" in ch.name.lower() for ch in guild.text_channels)
        if not has_mod_channel:
            analysis["missing_features"].append("Moderation channel")
            analysis["setup_score"] -= 10

        return analysis

    async def _generate_setup_recommendations(
        self, guild: discord.Guild, setup_data: Dict
    ) -> Dict[str, Any]:
        """Generate AI-powered setup recommendations"""
        try:
            prompt = f"""Server: {guild.name} ({guild.member_count} members). Score: {setup_data.get('setup_score', 75)}/100. Missing: {', '.join(setup_data.get('missing_features', [])[:3])}.

JSON:
{{
    "priority_recommendations": "• Top 3 priorities",
    "community_building": "Engagement tips",
    "technical_setup": "Config suggestions",
    "engagement_ideas": "Creative ideas"
}}"""

            ai_manager = MultiProviderAIManager()
            ai_response_obj = await ai_manager.generate_response(prompt)
            ai_response = (
                ai_response_obj.content
                if ai_response_obj.success
                else '{"insights": "Your server is well-managed!", "suggestions": "Keep up the great work!", "encouragement": "You\'re doing amazing!"}'
            )

            # Try to parse JSON response
            json_match = re.search(r"\{.*\}", ai_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

        except Exception as e:
            self.logger.error(f"AI setup recommendations failed: {e}")

        return self._generate_fallback_setup()

    def _generate_fallback_setup(self) -> Dict[str, Any]:
        """Fallback setup recommendations"""
        return {
            "priority_recommendations": "• Create welcome channel\n• Set up role system\n• Establish moderation tools",
            "community_building": "Host regular events and encourage member introductions",
            "technical_setup": "Configure auto-roles and channel permissions properly",
            "engagement_ideas": "Add reaction roles, fun bots, and member spotlights",
        }

    @app_commands.command(
        name="welcome", description="🎉 Setup AI-powered welcome system with personalized greetings"
    )
    @app_commands.describe(
        channel="Channel for welcome messages (defaults to configured welcome channel)",
        style="Welcome message style (friendly/professional/fun/enthusiastic)",
        auto_role="Role to assign to new members",
        enable_ai="Enable AI-powered personalized welcome messages",
    )
    @app_commands.default_permissions(manage_guild=True)
    async def setup_welcome(
        self,
        interaction: discord.Interaction,
        channel: Optional[discord.TextChannel] = None,
        style: Optional[str] = "friendly",
        auto_role: Optional[discord.Role] = None,
        enable_ai: Optional[bool] = True,
    ):
        """Setup AI-powered welcome system with personalized greetings and server introduction"""
        if not await check_user_permission(
            interaction.user, PermissionLevel.MODERATOR, interaction.guild
        ):
            await interaction.response.send_message(
                "❌ You need moderator permissions for this command.", ephemeral=True
            )
            return

        await interaction.response.defer(thinking=True)

        try:
            guild_id = interaction.guild.id
            
            # Use provided channel or default welcome channel (1399956513745014970)
            welcome_channel_id = channel.id if channel else 1399956513745014970
            welcome_channel = interaction.guild.get_channel(welcome_channel_id)
            
            if not welcome_channel:
                await interaction.followup.send(
                    f"❌ Welcome channel not found. Please specify a valid channel or ensure channel ID {welcome_channel_id} exists.",
                    ephemeral=True
                )
                return

            # Enhanced welcome settings with AI capabilities
            welcome_settings = {
                "channel_id": welcome_channel_id,
                "style": style,
                "auto_role_id": auto_role.id if auto_role else None,
                "enabled": True,
                "personalized_messages": True,
                "ai_generated": enable_ai and AI_AVAILABLE,
                "introduce_astra": True,
                "server_introduction": True,
                "member_count_celebration": True,
                "account_age_mention": True,
            }

            self.member_welcomes[guild_id] = welcome_settings

            # Generate sample welcome message
            if AI_AVAILABLE:
                sample_message = await self._generate_welcome_message(
                    interaction.user, style, interaction.guild
                )
            else:
                sample_message = f"Welcome to **{interaction.guild.name}**, {{user}}! We're excited to have you here! 🎉"

            embed = discord.Embed(
                title="🎉 Welcome System Configured!",
                description=f"Your intelligent welcome system is now active in {channel.mention}!",
                color=0x00FF7F,
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(
                name="⚙️ Settings",
                value=f"**Channel:** {channel.mention}\n"
                f"**Style:** {style.title()}\n"
                f"**Auto Role:** {auto_role.mention if auto_role else 'None'}\n"
                f"**AI Messages:** {'✅ Enabled' if AI_AVAILABLE else '❌ Disabled'}",
                inline=True,
            )

            embed.add_field(
                name="💬 Sample Message",
                value=(
                    sample_message[:200] + "..."
                    if len(sample_message) > 200
                    else sample_message
                ),
                inline=False,
            )

            embed.add_field(
                name="🤖 AI Features",
                value="• Personalized greetings based on user activity\n"
                "• Dynamic welcome messages that adapt\n"
                "• Community health insights\n"
                "• Engagement encouragement",
                inline=False,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Welcome setup error: {e}")
            await interaction.followup.send(
                "❌ Failed to setup welcome system. Please try again."
            )

    async def _generate_welcome_message(
        self, user: discord.Member, style: str, guild: discord.Guild
    ) -> str:
        """Generate AI-powered welcome message"""
        try:
            prompt = f"""Welcome message for {guild.name} ({guild.member_count} members). Style: {style}. Use {{user}} placeholder. Under 200 chars, emojis, engaging."""

            response = (
                ai_response_obj.content
                if ai_response_obj.success
                else "I'm processing that request for you! 🤖"
            )

            ai_manager = MultiProviderAIManager()

            ai_response_obj = await ai_manager.generate_response(prompt)

            return response.strip()

        except Exception:
            fallback_messages = {
                "friendly": "Hey {user}! 👋 Welcome to **{guild}**! We're so happy you joined our community! Feel free to introduce yourself and ask questions! 😊",
                "professional": "Welcome to **{guild}**, {user}. We're pleased to have you join our community. Please review our guidelines and don't hesitate to reach out if you need assistance.",
                "fun": "🎉 {user} has entered the chat! Welcome to **{guild}** - the coolest community on Discord! Let the fun begin! 🚀✨",
            }
            return fallback_messages.get(style, fallback_messages["friendly"]).format(
                user="{user}", guild=guild.name
            )

    @app_commands.command(
        name="community", description="📈 Advanced community analysis and insights"
    )
    @app_commands.describe(action="Analysis type (health/engagement/trends/insights)")
    @app_commands.default_permissions(manage_guild=True)
    async def community_analysis(
        self, interaction: discord.Interaction, action: str = "health"
    ):
        """Advanced community analysis with AI insights"""
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
            health = await self.get_community_health(guild.id)

            if action.lower() == "health":
                await self._analyze_community_health(interaction, guild, health)
            elif action.lower() == "engagement":
                await self._analyze_engagement(interaction, guild, health)
            elif action.lower() == "trends":
                await self._analyze_trends(interaction, guild, health)
            elif action.lower() == "insights":
                await self._generate_ai_insights(interaction, guild, health)
            else:
                await interaction.followup.send(
                    "❌ Invalid action. Use: health, engagement, trends, or insights"
                )

        except Exception as e:
            self.logger.error(f"Community analysis error: {e}")
            await interaction.followup.send("❌ Analysis failed. Please try again.")

    async def _analyze_community_health(
        self,
        interaction: discord.Interaction,
        guild: discord.Guild,
        health: CommunityHealth,
    ):
        """Analyze overall community health"""
        # Calculate metrics
        active_members = len(
            [
                m
                for m in guild.members
                if not m.bot and m.status != discord.Status.offline
            ]
        )
        member_ratio = (
            active_members / guild.member_count if guild.member_count > 0 else 0
        )

        # Health indicators
        health_indicators = []
        if member_ratio > 0.3:
            health_indicators.append("✅ High member activity")
        elif member_ratio > 0.1:
            health_indicators.append("🟡 Moderate member activity")
        else:
            health_indicators.append("🔴 Low member activity")

        if len(guild.text_channels) > 5:
            health_indicators.append("✅ Good channel diversity")
        else:
            health_indicators.append("🟡 Limited channel options")

        embed = discord.Embed(
            title="🏥 Community Health Report",
            description=f"Comprehensive health analysis for **{guild.name}**",
            color=0x00FF7F if member_ratio > 0.2 else 0xFFD700,
            timestamp=datetime.now(timezone.utc),
        )

        embed.add_field(
            name="📊 Key Metrics",
            value=f"**Total Members:** {guild.member_count:,}\n"
            f"**Active Members:** {active_members:,}\n"
            f"**Activity Ratio:** {member_ratio:.1%}\n"
            f"**Health Score:** {health.engagement_score}/100",
            inline=True,
        )

        embed.add_field(
            name="🔍 Health Indicators", value="\n".join(health_indicators), inline=True
        )

        # AI-powered recommendations if available
        if AI_AVAILABLE:
            try:
                recommendations = await self._generate_health_recommendations(
                    guild, health, member_ratio
                )
                embed.add_field(
                    name="🤖 AI Recommendations", value=recommendations, inline=False
                )
            except Exception as e:
                self.logger.error(f"AI health recommendations failed: {e}")

        await interaction.followup.send(embed=embed)

    async def _generate_health_recommendations(
        self, guild: discord.Guild, health: CommunityHealth, member_ratio: float
    ) -> str:
        """Generate AI-powered health recommendations"""
        prompt = f"""As Astra, analyze this Discord community and provide 3 specific recommendations to improve community health.

Community: {guild.name}
Members: {guild.member_count}
Active ratio: {member_ratio:.1%}
Health score: {health.engagement_score}/100

Provide 3 bullet points with actionable recommendations (under 200 chars total)."""

        try:
            response = (
                ai_response_obj.content
                if ai_response_obj.success
                else "I'm processing that request for you! 🤖"
            )
            ai_manager = MultiProviderAIManager()

            ai_response_obj = await ai_manager.generate_response(prompt)

            return response.strip()[:200]
        except Exception:
            return "• Host regular community events\n• Encourage member introductions\n• Create topic-specific channels"

    async def _analyze_engagement(
        self,
        interaction: discord.Interaction,
        guild: discord.Guild,
        health: CommunityHealth,
    ):
        """Analyze community engagement patterns"""
        # Calculate engagement metrics
        total_members = guild.member_count
        online_members = len([m for m in guild.members if m.status != discord.Status.offline])
        active_ratio = online_members / total_members if total_members > 0 else 0

        # Channel activity (simplified)
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        
        embed = discord.Embed(
            title="📊 Community Engagement Analysis",
            description=f"Engagement metrics for **{guild.name}**",
            color=0x00FF7F,
            timestamp=datetime.now(timezone.utc),
        )

        embed.add_field(
            name="👥 Member Engagement",
            value=f"• Total Members: **{total_members}**\n"
                  f"• Online Now: **{online_members}**\n"
                  f"• Activity Rate: **{active_ratio:.1%}**\n"
                  f"• Engagement Score: **{health.engagement_score}/100**",
            inline=True,
        )

        embed.add_field(
            name="💬 Channel Activity",
            value=f"• Text Channels: **{text_channels}**\n"
                  f"• Voice Channels: **{voice_channels}**\n"
                  f"• Avg per Member: **{(text_channels + voice_channels) / total_members:.2f}**",
            inline=True,
        )

        # Engagement recommendations
        if active_ratio < 0.3:
            embed.add_field(
                name="🚀 Engagement Boost",
                value="• Schedule interactive events\n• Create discussion prompts\n• Add reaction roles\n• Host voice activities",
                inline=False,
            )

        await interaction.followup.send(embed=embed)

    async def _analyze_trends(
        self,
        interaction: discord.Interaction,
        guild: discord.Guild,
        health: CommunityHealth,
    ):
        """Analyze community trends and patterns"""
        # Trend analysis (simplified for now)
        current_time = time.time()
        time_since_assessment = current_time - health.last_assessment
        hours_since = time_since_assessment / 3600

        embed = discord.Embed(
            title="📈 Community Trend Analysis",
            description=f"Growth and activity trends for **{guild.name}**",
            color=0xFF6B35,
            timestamp=datetime.now(timezone.utc),
        )

        # Basic trend indicators
        member_growth = "Stable" if guild.member_count > 10 else "Small Community"
        activity_trend = "Active" if len([m for m in guild.members if m.status != discord.Status.offline]) > guild.member_count * 0.2 else "Quiet"
        
        embed.add_field(
            name="📊 Growth Trends",
            value=f"• Member Growth: **{member_growth}**\n"
                  f"• Activity Trend: **{activity_trend}**\n"
                  f"• Assessment Age: **{hours_since:.1f}h**\n"
                  f"• Health Trend: **{health.engagement_score}/100**",
            inline=True,
        )

        # Channel trends
        channel_count = len(guild.channels)
        channel_ratio = channel_count / guild.member_count if guild.member_count > 0 else 0
        
        embed.add_field(
            name="🔄 Activity Patterns",
            value=f"• Total Channels: **{channel_count}**\n"
                  f"• Channel/Member Ratio: **{channel_ratio:.2f}**\n"
                  f"• Recent Events: **{len(health.community_events)}**\n"
                  f"• Positive Interactions: **{health.positive_interactions}**",
            inline=True,
        )

        # Trend predictions
        if channel_ratio > 1.0:
            trend_note = "🔥 High channel engagement potential"
        elif activity_trend == "Quiet":
            trend_note = "💤 Community may need activation"
        else:
            trend_note = "✅ Healthy community balance"

        embed.add_field(
            name="🎯 Trend Insights",
            value=f"• Current Status: **{trend_note}**\n"
                  f"• Growth Potential: **{'High' if guild.member_count < 100 else 'Established'}**\n"
                  f"• Engagement Focus: **{'Member retention' if activity_trend == 'Quiet' else 'Content creation'}**",
            inline=False,
        )

        await interaction.followup.send(embed=embed)

    async def _generate_ai_insights(
        self,
        interaction: discord.Interaction,
        guild: discord.Guild,
        health: CommunityHealth,
    ):
        """Generate AI-powered community insights"""
        try:
            # Gather comprehensive data for AI analysis
            total_members = guild.member_count
            online_members = len([m for m in guild.members if m.status != discord.Status.offline])
            text_channels = len(guild.text_channels)
            voice_channels = len(guild.voice_channels)
            roles_count = len(guild.roles) - 1  # Exclude @everyone
            
            # Create AI prompt for insights
            prompt = f"""As Astra, provide comprehensive community insights for this Discord server:

Server: {guild.name}
Members: {total_members}
Online: {online_members}
Text Channels: {text_channels}
Voice Channels: {voice_channels}
Roles: {roles_count}
Health Score: {health.engagement_score}/100
Events: {len(health.community_events)}

Provide 4 key insights with specific recommendations (each under 100 chars):
1. Community Strength
2. Growth Opportunity  
3. Engagement Strategy
4. Action Priority"""

            # Generate AI insights
            try:
                from ai.multi_provider_ai import MultiProviderAIManager
                ai_manager = MultiProviderAIManager()
                ai_response = await ai_manager.generate_response(prompt)
                insights = ai_response.content if hasattr(ai_response, 'content') else str(ai_response)
            except Exception as e:
                self.logger.error(f"AI insights generation failed: {e}")
                insights = self._generate_fallback_insights(guild, health)

            embed = discord.Embed(
                title="🤖 AI Community Insights",
                description=f"Advanced analysis for **{guild.name}**",
                color=0x7289DA,
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(
                name="💡 Astra's Analysis",
                value=insights[:1000] if len(insights) > 1000 else insights,
                inline=False,
            )

            # Add current metrics
            embed.add_field(
                name="📊 Current Metrics",
                value=f"• Health Score: **{health.engagement_score}/100**\n"
                      f"• Activity Rate: **{(online_members/total_members)*100:.1f}%**\n"
                      f"• Channel Diversity: **{text_channels + voice_channels}**\n"
                      f"• Role Structure: **{roles_count} roles**",
                inline=True,
            )

            embed.set_footer(text="💡 AI insights generated by Astra's community analysis engine")
            
        except Exception as e:
            self.logger.error(f"AI insights generation error: {e}")
            embed = discord.Embed(
                title="🤖 AI Community Insights",
                description="Analysis temporarily unavailable. Please try again.",
                color=0xFF6B6B,
            )

        await interaction.followup.send(embed=embed)

    def _generate_fallback_insights(self, guild: discord.Guild, health: CommunityHealth) -> str:
        """Generate fallback insights when AI is unavailable"""
        total_members = guild.member_count
        
        if total_members < 10:
            return "🌱 Growing Community: Focus on member retention and welcoming new users.\n📢 Boost engagement with interactive content and regular events.\n🎯 Priority: Build core community foundation."
        elif total_members < 100:
            return "🚀 Expanding Server: Great foundation, time to scale engagement strategies.\n💬 Create specialized channels for different interests.\n🎯 Priority: Enhance member interaction systems."
        else:
            return "🏰 Established Community: Maintain quality while fostering deeper connections.\n📊 Use analytics to optimize channel structure and events.\n🎯 Priority: Community leadership and moderation excellence."

    @app_commands.command(
        name="roles", description="🎭 Advanced role management with AI optimization"
    )
    @app_commands.describe(
        action="Action to perform (optimize/analyze/create/cleanup)",
        name="Role name (for create action)",
        color="Color hex code (for create action)",
    )
    @app_commands.default_permissions(manage_roles=True)
    async def advanced_roles(
        self,
        interaction: discord.Interaction,
        action: str,
        name: Optional[str] = None,
        color: Optional[str] = None,
    ):
        """Advanced role management with AI optimization"""
        if not await check_user_permission(
            interaction.user, PermissionLevel.MODERATOR, interaction.guild
        ):
            await interaction.response.send_message(
                "❌ You need moderator permissions for this command.", ephemeral=True
            )
            return

        await interaction.response.defer(thinking=True)

        try:
            if action.lower() == "optimize":
                await self._optimize_roles_ai(interaction)
            elif action.lower() == "analyze":
                await self._analyze_roles(interaction)
            elif action.lower() == "create" and name:
                await self._create_smart_role(interaction, name, color)
            elif action.lower() == "cleanup":
                await self._cleanup_roles(interaction)
            else:
                await interaction.followup.send(
                    "❌ Invalid action or missing parameters."
                )

        except Exception as e:
            self.logger.error(f"Advanced roles error: {e}")
            await interaction.followup.send(
                "❌ Role operation failed. Please try again."
            )

    async def _analyze_roles(self, interaction: discord.Interaction):
        """Analyze server roles with AI insights"""
        guild = interaction.guild

        # Collect role statistics
        total_roles = len(guild.roles) - 1  # Exclude @everyone
        managed_roles = sum(1 for role in guild.roles if role.managed)
        custom_roles = total_roles - managed_roles
        unused_roles = sum(
            1
            for role in guild.roles
            if len(role.members) == 0 and role.name != "@everyone"
        )

        # Color analysis
        color_conflicts = {}
        for role in guild.roles:
            if role.name != "@everyone" and role.color.value != 0:
                if role.color.value in color_conflicts:
                    color_conflicts[role.color.value].append(role)
                else:
                    color_conflicts[role.color.value] = [role]

        conflicts = sum(1 for roles in color_conflicts.values() if len(roles) > 1)

        embed = discord.Embed(
            title="🎭 Server Role Analysis",
            description=f"Comprehensive role analysis for **{guild.name}**",
            color=0x9932CC,
            timestamp=datetime.now(timezone.utc),
        )

        embed.add_field(
            name="📊 Role Statistics",
            value=f"• Total Roles: **{total_roles}**\n"
            f"• Custom Roles: **{custom_roles}**\n"
            f"• Managed Roles: **{managed_roles}**\n"
            f"• Unused Roles: **{unused_roles}**",
            inline=True,
        )

        embed.add_field(
            name="🎨 Color Analysis",
            value=f"• Unique Colors: **{len(color_conflicts)}**\n"
            f"• Color Conflicts: **{conflicts}**\n"
            f"• Default Color: **{total_roles - len(color_conflicts)}**",
            inline=True,
        )

        # Generate AI recommendations
        if unused_roles > 5 or conflicts > 3:
            embed.add_field(
                name="🤖 AI Recommendations",
                value="• Consider cleaning unused roles\n"
                "• Resolve color conflicts for better hierarchy\n"
                "• Use role templates for consistency",
                inline=False,
            )

        await interaction.followup.send(embed=embed)

    async def _optimize_roles_ai(self, interaction: discord.Interaction):
        """AI-powered role optimization"""
        guild = interaction.guild
        roles_to_optimize = []

        # Find optimization opportunities
        color_conflicts = {}
        unused_roles = []

        for role in guild.roles:
            if role.name != "@everyone" and not role.managed:
                # Track color conflicts
                if role.color.value != 0:
                    if role.color.value in color_conflicts:
                        color_conflicts[role.color.value].append(role)
                    else:
                        color_conflicts[role.color.value] = [role]

                # Find unused roles
                if len(role.members) == 0:
                    unused_roles.append(role)

        # Generate AI recommendations
        optimization_plan = await self._generate_role_optimization_plan(
            guild, color_conflicts, unused_roles
        )

        embed = discord.Embed(
            title="🎭 AI Role Optimization Plan",
            description=f"Smart optimization analysis for **{guild.name}**",
            color=0x9932CC,
            timestamp=datetime.now(timezone.utc),
        )

        # Color conflicts
        if color_conflicts:
            conflicts_text = []
            for color_value, roles in color_conflicts.items():
                if len(roles) > 1:
                    conflicts_text.append(
                        f"#{color_value:06x}: {', '.join([r.name for r in roles[:3]])}"
                    )

            if conflicts_text:
                embed.add_field(
                    name="🎨 Color Conflicts Found",
                    value="\n".join(conflicts_text[:5]),
                    inline=True,
                )

        # Unused roles
        if unused_roles:
            embed.add_field(
                name="🗑️ Unused Roles",
                value="\n".join([r.name for r in unused_roles[:5]]),
                inline=True,
            )

        # AI optimization suggestions
        embed.add_field(
            name="🤖 AI Optimization Plan", value=optimization_plan, inline=False
        )

        await interaction.followup.send(embed=embed)

    async def _generate_role_optimization_plan(
        self, guild: discord.Guild, color_conflicts: Dict, unused_roles: List
    ) -> str:
        """Generate AI-powered role optimization plan"""
        if not AI_AVAILABLE:
            return "• Fix color conflicts with unique colors\n• Remove unused roles\n• Organize role hierarchy"

        try:
            prompt = f"""Generate a role optimization plan for Discord server "{guild.name}".

Issues found:
- Color conflicts: {len([roles for roles in color_conflicts.values() if len(roles) > 1])}
- Unused roles: {len(unused_roles)}
- Total roles: {len(guild.roles)}

Provide 3-4 bullet points with specific optimization actions (under 200 chars total)."""

            response = (
                ai_response_obj.content
                if ai_response_obj.success
                else "I'm processing that request for you! 🤖"
            )
            ai_manager = MultiProviderAIManager()

            ai_response_obj = await ai_manager.generate_response(prompt)

            return response.strip()[:200]

        except Exception:
            return "• Assign unique colors to conflicting roles\n• Archive unused roles\n• Reorganize role hierarchy\n• Add member count tracking"

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Enhanced member join handling with AI-powered personalized welcomes"""
        guild_id = member.guild.id

        # Check if welcome system is enabled for this guild
        if (
            guild_id not in self.member_welcomes
            or not self.member_welcomes[guild_id]["enabled"]
        ):
            # Use default welcome system with configured welcome channel
            await self._handle_default_welcome(member)
            return

        settings = self.member_welcomes[guild_id]
        channel = member.guild.get_channel(settings["channel_id"])

        if not channel:
            # Fallback to default welcome channel
            await self._handle_default_welcome(member)
            return

        try:
            # Generate personalized welcome message with AI
            if settings.get("ai_generated", True) and AI_AVAILABLE:
                welcome_message = await self._generate_personalized_welcome(
                    member, settings
                )
            else:
                welcome_message = self._generate_fallback_welcome(member, settings)

            # Create comprehensive welcome embed
            embed = discord.Embed(
                title="🎉 Welcome to the Community!",
                description=welcome_message,
                color=0x00FF7F,
                timestamp=datetime.now(timezone.utc),
            )

            embed.set_thumbnail(
                url=member.avatar.url if member.avatar else member.default_avatar.url
            )
            
            # Add comprehensive getting started information
            embed.add_field(
                name="� Getting Started",
                value="• Explore our channels and find your interests\n• Check out our community guidelines\n• Introduce yourself and meet other members\n• Ask **Astra** (me!) anything you need help with!",
                inline=False,
            )
            
            # Add member information if enabled
            if settings.get("member_count_celebration", True):
                embed.add_field(
                    name="👥 Community Stats",
                    value=f"You're member **#{member.guild.member_count}** in our growing community!",
                    inline=True,
                )
            
            if settings.get("account_age_mention", True):
                account_age = (datetime.now(timezone.utc) - member.created_at).days
                embed.add_field(
                    name="📅 Account Info",
                    value=f"Discord account: {account_age} days old",
                    inline=True,
                )

            embed.set_footer(
                text="💫 Powered by Astra AI - Your friendly community companion!",
                icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
            )

            # Send welcome message with member mention
            await channel.send(content=f"🎉 {member.mention}", embed=embed)

            # Assign auto role if configured
            if settings.get("auto_role_id"):
                auto_role = member.guild.get_role(settings["auto_role_id"])
                if auto_role:
                    await member.add_roles(auto_role, reason="Auto-role assignment by Astra")
                    
            # Send follow-up tips after a short delay
            await asyncio.sleep(30)  # 30 seconds delay
            await self._send_welcome_tips(channel, member)

            # Update community health metrics
            try:
                health = await self.get_community_health(guild_id)
                health.positive_interactions += 1
            except:
                pass  # Don't fail welcome if health update fails

        except Exception as e:
            self.logger.error(f"Enhanced welcome system error for {member}: {e}")
            # Fallback to simple welcome
            await self._handle_default_welcome(member)

    async def _generate_personalized_welcome(
        self, member: discord.Member, settings: Dict
    ) -> str:
        """Generate comprehensive AI-powered welcome message with Astra introduction"""
        try:
            from ai.multi_provider_ai import MultiProviderAIManager
            
            # Analyze member for personalization hints
            account_age = (datetime.now(timezone.utc) - member.created_at).days
            is_new_to_discord = account_age < 30
            member_number = member.guild.member_count
            
            # Create comprehensive welcome prompt
            prompt = f"""Generate a warm, personalized welcome message for {member.display_name} who just joined {member.guild.name}.

Key Requirements:
- Style: {settings.get('style', 'friendly')} and welcoming
- Introduce yourself as "Astra", the intelligent bot managing this server
- Mention this is member #{member_number} in the community
- Account age context: {account_age} days old {'(new to Discord!)' if is_new_to_discord else '(experienced user)'}
- Include brief server introduction highlighting community aspects
- Encourage engagement and offer help
- Keep it warm but concise (under 200 characters)
- Use emojis appropriately

Example tone: Friendly, welcoming, helpful, and enthusiastic about the community."""

            ai_manager = MultiProviderAIManager()
            ai_response_obj = await ai_manager.generate_response(
                prompt, 
                max_tokens=150, 
                temperature=0.8
            )
            
            if ai_response_obj and ai_response_obj.success:
                return ai_response_obj.content.strip()
            else:
                # Enhanced fallback message
                return self._generate_fallback_welcome(member, settings)

        except Exception as e:
            self.logger.error(f"AI welcome generation failed: {e}")
            return self._generate_fallback_welcome(member, settings)
    
    def _generate_fallback_welcome(self, member: discord.Member, settings: Dict) -> str:
        """Generate fallback welcome message when AI is unavailable"""
        style = settings.get('style', 'friendly')
        member_num = member.guild.member_count
        
        style_messages = {
            'friendly': f"🎉 Welcome to **{member.guild.name}**, {member.mention}! I'm **Astra**! You're our #{member_num} member - so excited to have you! Feel free to explore and ask me anything! 🚀✨",
            'professional': f"Welcome to **{member.guild.name}**, {member.mention}. I'm **Astra**, managing this community. As member #{member_num}, we're pleased to have you join us. Let me know if you need assistance getting started.",
            'fun': f"🎊 WOOHOO! {member.mention} just dropped into **{member.guild.name}**! 🎉 I'm **Astra**, your fun AI buddy! You're lucky #{member_num} - let's make this community even more awesome together! Ready for some fun? 🚀🎮✨",
            'enthusiastic': f"🌟 AMAZING! Welcome {member.mention} to the incredible **{member.guild.name}** community! I'm **Astra**, your enthusiastic AI companion! As member #{member_num}, you're part of something special! Can't wait to chat and help you explore everything here! �🚀"
        }
        
        return style_messages.get(style, style_messages['friendly'])

    async def _handle_default_welcome(self, member: discord.Member):
        """Handle welcome for guilds without custom welcome setup using default channel"""
        try:
            # Use the configured default welcome channel
            welcome_channel = member.guild.get_channel(1399956513745014970)
            
            if not welcome_channel:
                # Fallback to system channel or first available text channel
                welcome_channel = member.guild.system_channel or next(
                    (ch for ch in member.guild.text_channels if ch.permissions_for(member.guild.me).send_messages), 
                    None
                )
            
            if not welcome_channel:
                return  # No suitable channel found
            
            # Generate simple but effective welcome
            welcome_message = f"🎉 Welcome to **{member.guild.name}**, {member.mention}! I'm **Astra**! Ready to help you explore and enjoy our community! Feel free to ask me anything! 🚀✨"
            
            embed = discord.Embed(
                title="🌟 New Member Alert!",
                description=welcome_message,
                color=0x00BFFF,
                timestamp=datetime.now(timezone.utc),
            )
            
            embed.set_thumbnail(
                url=member.avatar.url if member.avatar else member.default_avatar.url
            )
            
            embed.add_field(
                name="👥 You're Member #",
                value=f"**{member.guild.member_count}**",
                inline=True,
            )
            
            embed.add_field(
                name="🤖 Meet Astra",
                value="Astra - Ready to help!",
                inline=True,
            )
            
            embed.set_footer(text="Welcome to our community! 🎊")
            
            await welcome_channel.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Default welcome failed for {member}: {e}")
    
    async def _send_welcome_tips(self, channel: discord.TextChannel, member: discord.Member):
        """Send helpful tips to new members after welcome"""
        try:
            tips_embed = discord.Embed(
                title="💡 Quick Tips for New Members",
                description=f"Hey {member.mention}, here are some tips to get you started!",
                color=0x00BFFF,
            )
            
            tips_embed.add_field(
                name="🔍 Explore",
                value="Check out different channels to find topics you're interested in!",
                inline=False,
            )
            
            tips_embed.add_field(
                name="💬 Engage",
                value="Don't be shy! Jump into conversations and share your thoughts.",
                inline=False,
            )
            
            tips_embed.add_field(
                name="🤖 Ask Astra",
                value="I'm here 24/7 to help! Just mention me or ask questions.",
                inline=False,
            )
            
            tips_embed.set_footer(text="These tips will auto-delete in 2 minutes to keep the channel clean.")
            
            tips_message = await channel.send(embed=tips_embed)
            
            # Auto-delete tips after 2 minutes
            await asyncio.sleep(120)
            try:
                await tips_message.delete()
            except:
                pass  # Message might already be deleted
                
        except Exception as e:
            self.logger.error(f"Failed to send welcome tips: {e}")

    @tasks.loop(hours=6)
    async def health_monitoring(self):
        """Monitor community health and provide insights"""
        for guild_id, health in self.community_health.items():
            try:
                guild = self.bot.get_guild(guild_id)
                if not guild:
                    continue

                # Update health metrics
                await self._update_health_metrics(guild, health)

                # Check if intervention is needed
                if health.engagement_score < 50:
                    await self._suggest_community_improvements(guild, health)

            except Exception as e:
                self.logger.error(f"Health monitoring error for guild {guild_id}: {e}")

    @tasks.loop(hours=12)
    async def proactive_assistance(self):
        """Proactive assistance and community building suggestions"""
        if not self.companion_settings["proactive_assistance"]:
            return

        for guild_id in self.community_health.keys():
            try:
                guild = self.bot.get_guild(guild_id)
                if not guild:
                    continue

                # Occasionally provide proactive suggestions
                if random.randint(1, 10) == 1:  # 10% chance
                    await self._provide_proactive_suggestions(guild)

            except Exception as e:
                self.logger.error(
                    f"Proactive assistance error for guild {guild_id}: {e}"
                )

    async def _update_health_metrics(
        self, guild: discord.Guild, health: CommunityHealth
    ):
        """Update community health metrics"""
        # Calculate engagement metrics
        active_members = len(
            [
                m
                for m in guild.members
                if not m.bot and m.status != discord.Status.offline
            ]
        )
        activity_ratio = (
            active_members / guild.member_count if guild.member_count > 0 else 0
        )

        # Update engagement score
        base_score = min(100, activity_ratio * 200)  # Scale activity ratio
        health.engagement_score = int(base_score)
        health.last_assessment = time.time()

    async def _suggest_community_improvements(
        self, guild: discord.Guild, health: CommunityHealth
    ):
        """Suggest improvements for low-engagement communities"""
        if not AI_AVAILABLE:
            return

        # Find a suitable channel to send suggestions
        suggestion_channel = None
        for channel in guild.text_channels:
            if any(
                keyword in channel.name.lower()
                for keyword in ["general", "chat", "discussion"]
            ):
                if channel.permissions_for(guild.me).send_messages:
                    suggestion_channel = channel
                    break

        if not suggestion_channel:
            return

        try:
            # Generate improvement suggestions
            suggestions = await self._generate_improvement_suggestions(guild, health)

            embed = discord.Embed(
                title="💡 Community Builder Suggestions",
                description="Hi everyone! I've noticed our community could use a little boost. Here are some ideas to increase engagement:",
                color=0xFFD700,
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(
                name="🚀 Suggested Activities", value=suggestions, inline=False
            )

            embed.set_footer(text="💙 Astra - Your Community Companion")

            await suggestion_channel.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Improvement suggestions error: {e}")

    async def _generate_improvement_suggestions(
        self, guild: discord.Guild, health: CommunityHealth
    ) -> str:
        """Generate AI-powered community improvement suggestions"""
        try:
            prompt = f"""4 engagement ideas for {guild.name} ({guild.member_count} members, score {health.engagement_score}/100). Bullet points, actionable, fun."""

            ai_manager = MultiProviderAIManager()
            ai_response_obj = await ai_manager.generate_response(prompt)
            response = (
                ai_response_obj.content
                if ai_response_obj.success
                else "I'm processing that request for you! 🤖"
            )
            return response.strip()[:250]

        except Exception:
            return "• Host a community game night\n• Start daily discussion topics\n• Create member spotlights\n• Set up fun reaction roles"


async def setup(bot):
    await bot.add_cog(EnhancedServerManagement(bot))
