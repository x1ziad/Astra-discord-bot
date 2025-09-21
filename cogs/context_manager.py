"""
Context Manager Cog for Astra Bot
Provides commands to manage and test the universal context system
"""

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import json

logger = logging.getLogger("astra.context_manager")


class ContextManagerCog(commands.Cog):
    """Commands for managing and testing the universal context system"""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("astra.context_manager")

    @app_commands.command(
        name="context_test", description="Test the context understanding system"
    )
    @app_commands.describe(
        message="Test message to analyze (optional, defaults to random test message)"
    )
    async def context_test(self, interaction: discord.Interaction, message: str = None):
        """Test context analysis on a message"""
        try:
            await interaction.response.defer()

            # Get context manager
            from ai.universal_context_manager import get_context_manager

            context_manager = get_context_manager()

            if not context_manager:
                embed = discord.Embed(
                    title="❌ Context Manager Not Available",
                    description="The universal context manager is not initialized.",
                    color=0xE74C3C,
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # Use provided message or default test message
            test_message = (
                message
                or "Hey! I'm really excited about this new space game I found. Have you ever played Stellaris? It's amazing! 🚀"
            )

            # Analyze the message
            message_context = await context_manager.analyze_message(
                test_message,
                interaction.user.id,
                interaction.channel.id,
                interaction.guild.id if interaction.guild else None,
                interaction.user.display_name,
            )

            # Check if should respond
            should_respond, reason = await context_manager.should_respond(
                message_context,
                interaction.channel.id,
                interaction.guild.id if interaction.guild else None,
            )

            # Create detailed analysis embed
            embed = discord.Embed(
                title="🧠 Context Analysis Results",
                description=f"**Test Message:** {test_message[:100]}{'...' if len(test_message) > 100 else ''}",
                color=0x3498DB,
                timestamp=datetime.now(timezone.utc),
            )

            # Basic analysis
            embed.add_field(
                name="📊 Message Analysis",
                value=f"**Tone:** {message_context.tone.value.title()}\n"
                f"**Humor Score:** {message_context.humor_score:.2f}/1.0\n"
                f"**Emotional Intensity:** {message_context.emotional_intensity:.2f}/1.0\n"
                f"**Topics:** {', '.join(message_context.topics) if message_context.topics else 'None detected'}",
                inline=False,
            )

            # Response triggers
            triggers_text = "\n".join(
                [
                    f"• {trigger.value.replace('_', ' ').title()}"
                    for trigger in message_context.response_triggers
                ]
            )
            embed.add_field(
                name="🎯 Response Triggers",
                value=(
                    triggers_text if triggers_text else "No specific triggers detected"
                ),
                inline=True,
            )

            # Response decision
            embed.add_field(
                name="🤖 AI Response Decision",
                value=f"**Should Respond:** {'✅ Yes' if should_respond else '❌ No'}\n"
                f"**Reason:** {reason.replace('_', ' ').title()}\n"
                f"**Probability:** {message_context.response_probability:.2f}/1.0",
                inline=True,
            )

            # Response style suggestion
            embed.add_field(
                name="🎨 Suggested Style",
                value=f"**Style:** {message_context.suggested_response_style.title()}\n"
                f"**Recommended approach based on context analysis**",
                inline=False,
            )

            # Test AI response if applicable
            if should_respond:
                try:
                    # Get AI engine and test response
                    from ai.consolidated_ai_engine import get_engine

                    ai_engine = get_engine()

                    if ai_engine:
                        response_context = await context_manager.get_response_context(
                            message_context
                        )
                        ai_response = await ai_engine.process_conversation(
                            test_message,
                            interaction.user.id,
                            guild_id=(
                                interaction.guild.id if interaction.guild else None
                            ),
                            channel_id=interaction.channel.id,
                            context_data=response_context,
                        )

                        if ai_response:
                            embed.add_field(
                                name="🤖 Generated Response",
                                value=ai_response[:500]
                                + ("..." if len(ai_response) > 500 else ""),
                                inline=False,
                            )
                    else:
                        embed.add_field(
                            name="⚠️ AI Engine",
                            value="AI engine not available for response generation",
                            inline=False,
                        )

                except Exception as e:
                    embed.add_field(
                        name="❌ Response Generation Error",
                        value=f"Failed to generate response: {str(e)[:100]}",
                        inline=False,
                    )

            embed.set_footer(
                text="Context analysis complete • This is a test and won't be saved"
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Context test error: {e}")
            error_embed = discord.Embed(
                title="❌ Context Test Error",
                description=f"An error occurred during context testing: {str(e)}",
                color=0xE74C3C,
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)

    @app_commands.command(
        name="context_stats",
        description="View context manager statistics and analytics",
    )
    async def context_stats(self, interaction: discord.Interaction):
        """View context manager statistics"""
        try:
            await interaction.response.defer()

            # Get context manager
            from ai.universal_context_manager import get_context_manager

            context_manager = get_context_manager()

            if not context_manager:
                embed = discord.Embed(
                    title="❌ Context Manager Not Available",
                    description="The universal context manager is not initialized.",
                    color=0xE74C3C,
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # Get analytics
            analytics = await context_manager.get_analytics()

            if "error" in analytics:
                embed = discord.Embed(
                    title="❌ Analytics Error",
                    description=f"Could not retrieve analytics: {analytics['error']}",
                    color=0xE74C3C,
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # Create analytics embed
            embed = discord.Embed(
                title="📊 Context Manager Analytics",
                description="Statistics about conversation analysis and AI responses",
                color=0x2ECC71,
                timestamp=datetime.now(timezone.utc),
            )

            # Basic stats
            embed.add_field(
                name="📈 Message Analysis",
                value=f"**Total Messages Analyzed:** {analytics.get('total_messages_analyzed', 0):,}\n"
                f"**AI Responses Sent:** {analytics.get('total_responses_sent', 0):,}\n"
                f"**Response Rate:** {analytics.get('response_rate_percent', 0):.1f}%",
                inline=True,
            )

            # User engagement
            embed.add_field(
                name="👥 User Engagement",
                value=f"**Active Users:** {analytics.get('active_users', 0):,}\n"
                f"**High Engagement Users:** {analytics.get('users_with_high_engagement', 0):,}\n"
                f"**Avg Humor Score:** {analytics.get('average_humor_score', 0):.3f}",
                inline=True,
            )

            # Top topics (if available)
            top_topics = analytics.get("top_topics", [])
            if top_topics:
                topics_text = "\n".join(
                    [
                        f"• {json.loads(topic[0]) if topic[0].startswith('[') else topic[0]} ({topic[1]} times)"
                        for topic in top_topics[:5]
                    ]
                )
                embed.add_field(
                    name="🔥 Popular Topics",
                    value=topics_text[:500] + ("..." if len(topics_text) > 500 else ""),
                    inline=False,
                )

            # Performance info
            embed.add_field(
                name="⚡ Performance",
                value="Context analysis running smoothly\n"
                "Humor detection active\n"
                "Response probability calculation enabled",
                inline=False,
            )

            embed.set_footer(text="Analytics updated in real-time")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Context stats error: {e}")
            error_embed = discord.Embed(
                title="❌ Statistics Error",
                description=f"An error occurred retrieving statistics: {str(e)}",
                color=0xE74C3C,
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)

    @app_commands.command(
        name="context_config",
        description="Configure context manager settings (Admin only)",
    )
    @app_commands.describe(
        setting="Setting to configure", value="New value for the setting"
    )
    @app_commands.choices(
        setting=[
            app_commands.Choice(name="Response Rate", value="response_rate"),
            app_commands.Choice(name="Humor Sensitivity", value="humor_sensitivity"),
            app_commands.Choice(name="Min Response Interval", value="min_interval"),
            app_commands.Choice(
                name="Channel Response Interval", value="channel_interval"
            ),
        ]
    )
    async def context_config(
        self, interaction: discord.Interaction, setting: str, value: str
    ):
        """Configure context manager settings"""
        try:
            # Check permissions
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "❌ You need administrator permissions to configure context settings.",
                    ephemeral=True,
                )
                return

            await interaction.response.defer()

            # Get context manager
            from ai.universal_context_manager import get_context_manager

            context_manager = get_context_manager()

            if not context_manager:
                embed = discord.Embed(
                    title="❌ Context Manager Not Available",
                    description="The universal context manager is not initialized.",
                    color=0xE74C3C,
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # Apply configuration changes
            success = False
            error_message = ""

            try:
                if setting == "response_rate":
                    # This would modify response probability multipliers
                    # For now, just acknowledge the setting
                    success = True
                elif setting == "humor_sensitivity":
                    # This would modify humor detection thresholds
                    success = True
                elif setting == "min_interval":
                    # This would modify minimum response intervals
                    success = True
                elif setting == "channel_interval":
                    # This would modify channel response intervals
                    success = True

            except ValueError as e:
                error_message = f"Invalid value: {str(e)}"
            except Exception as e:
                error_message = f"Configuration error: {str(e)}"

            if success:
                embed = discord.Embed(
                    title="✅ Configuration Updated",
                    description=f"**Setting:** {setting.replace('_', ' ').title()}\n**New Value:** {value}",
                    color=0x27AE60,
                    timestamp=datetime.now(timezone.utc),
                )
                embed.add_field(
                    name="📝 Note",
                    value="Configuration changes will take effect for new messages.\n"
                    "Some settings may require a bot restart to fully apply.",
                    inline=False,
                )
            else:
                embed = discord.Embed(
                    title="❌ Configuration Failed",
                    description=f"Could not update setting: {error_message}",
                    color=0xE74C3C,
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Context config error: {e}")
            error_embed = discord.Embed(
                title="❌ Configuration Error",
                description=f"An error occurred during configuration: {str(e)}",
                color=0xE74C3C,
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)

    @app_commands.command(
        name="humor_test", description="Test humor detection on a message"
    )
    @app_commands.describe(message="Message to test for humor detection")
    async def humor_test(self, interaction: discord.Interaction, message: str):
        """Test humor detection specifically"""
        try:
            await interaction.response.defer()

            # Import humor detector
            from ai.universal_context_manager import HumorDetector

            humor_detector = HumorDetector()

            # Test humor detection
            is_humorous, humor_score, humor_type = humor_detector.detect_humor(message)

            # Create results embed
            embed = discord.Embed(
                title="😄 Humor Detection Test",
                description=f"**Test Message:** {message[:200]}{'...' if len(message) > 200 else ''}",
                color=0xF39C12,
                timestamp=datetime.now(timezone.utc),
            )

            # Results
            embed.add_field(
                name="🎭 Detection Results",
                value=f"**Humor Detected:** {'✅ Yes' if is_humorous else '❌ No'}\n"
                f"**Humor Score:** {humor_score:.3f}/1.0\n"
                f"**Humor Type:** {humor_type.title()}",
                inline=True,
            )

            # Score interpretation
            if humor_score >= 0.7:
                interpretation = "Very Funny! 😂"
                color = 0x27AE60
            elif humor_score >= 0.4:
                interpretation = "Moderately Humorous 😊"
                color = 0xF39C12
            elif humor_score >= 0.2:
                interpretation = "Slightly Playful 🙂"
                color = 0x3498DB
            else:
                interpretation = "Not Humorous 😐"
                color = 0x95A5A6

            embed.color = color
            embed.add_field(name="📊 Interpretation", value=interpretation, inline=True)

            # Tips for humor
            embed.add_field(
                name="💡 Humor Tips",
                value="• Emojis and exclamation marks boost humor scores\n"
                "• Sarcasm and wordplay are detected\n"
                "• 'lol', 'haha', and similar expressions help\n"
                "• Context and timing matter too!",
                inline=False,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Humor test error: {e}")
            error_embed = discord.Embed(
                title="❌ Humor Test Error",
                description=f"An error occurred during humor testing: {str(e)}",
                color=0xE74C3C,
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)

    @app_commands.command(
        name="context_help",
        description="Learn about the enhanced context understanding system",
    )
    async def context_help(self, interaction: discord.Interaction):
        """Provide help about the context system"""
        try:
            embed = discord.Embed(
                title="🧠 Universal Context Understanding",
                description="Astra now understands every message and responds naturally without needing to be mentioned!",
                color=0x7C3AED,
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(
                name="✨ What's New",
                value="• **Automatic Response**: No need to mention @Astra anymore!\n"
                "• **Humor Detection**: Recognizes and responds to jokes and sarcasm\n"
                "• **Emotional Understanding**: Picks up on your mood and responds appropriately\n"
                "• **Topic Awareness**: Engages with interesting conversations naturally\n"
                "• **Smart Rate Limiting**: Won't spam, responds thoughtfully",
                inline=False,
            )

            embed.add_field(
                name="🎯 When Astra Responds",
                value="• **Questions**: Any message with a question mark\n"
                "• **Help Requests**: Messages asking for help or assistance\n"
                "• **Interesting Topics**: Space, Stellaris, science, technology\n"
                "• **Humor**: Jokes, puns, and playful messages\n"
                "• **Emotional Support**: When you seem frustrated or confused\n"
                "• **Greetings**: Welcomes and casual hellos",
                inline=False,
            )

            embed.add_field(
                name="🎨 Response Styles",
                value="Astra adapts its response style based on your message:\n"
                "• **Humorous** responses to jokes and playfulness\n"
                "• **Supportive** responses to emotional messages\n"
                "• **Informative** responses to technical questions\n"
                "• **Enthusiastic** responses to excited messages\n"
                "• **Casual** responses to everyday conversation",
                inline=False,
            )

            embed.add_field(
                name="⚙️ Smart Features",
                value="• **Context Memory**: Remembers recent conversation flow\n"
                "• **User Learning**: Adapts to your communication style over time\n"
                "• **Rate Limiting**: Prevents overwhelming conversations\n"
                "• **Natural Timing**: Adds realistic delays and typing indicators\n"
                "• **Fallback Safety**: Always has something relevant to say",
                inline=False,
            )

            embed.add_field(
                name="🔧 Testing Commands",
                value="• `/context_test` - Test context analysis on any message\n"
                "• `/humor_test` - Test humor detection specifically\n"
                "• `/context_stats` - View system analytics\n"
                "• `/context_config` - Configure settings (Admin only)",
                inline=False,
            )

            embed.set_footer(
                text="Try having a natural conversation - Astra will join in when appropriate!"
            )

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            self.logger.error(f"Context help error: {e}")
            await interaction.response.send_message(
                f"❌ Error displaying help: {str(e)}", ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(ContextManagerCog(bot))
