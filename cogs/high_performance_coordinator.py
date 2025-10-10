"""
🚀 HIGH-PERFORMANCE MESSAGE COORDINATOR
Integrates all existing message handlers with the concurrent processor

Optimized for 10+ simultaneous conversations:
- Security warnings (instant)
- AI conversations (natural)
- Question answering (accurate)
- Multitasking (seamless)

Performance targets:
- Under 100ms response time for security warnings
- Under 500ms response time for AI conversations
- 50+ concurrent message processing
- Zero message loss or delays
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import discord
from discord import app_commands
from discord.ext import commands

from core.concurrent_message_processor import (
    MessagePriority,
    initialize_processor,
    ConcurrentMessageProcessor,
)


class HighPerformanceCoordinator(commands.Cog):
    """
    🚀 ULTRA-HIGH PERFORMANCE Message Coordinator

    Orchestrates all message processing through the concurrent processor:
    - Security Manager (violations, warnings)
    - AI Companion (conversations, responses)
    - AI Moderation (automated warnings)
    - Analytics (usage tracking)
    - Advanced AI (context analysis)

    Optimized for maximum concurrency and minimal latency.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger("astra.coordinator")

        # Performance tracking
        self.start_time = time.time()
        self.processed_messages = 0
        self.concurrent_responses = 0
        self.max_concurrent_reached = 0

        # Handler references (will be populated on ready)
        self.security_manager = None
        self.ai_companion = None
        self.ai_moderation = None
        self.analytics = None
        self.advanced_ai = None

        # Response cache for immediate replies
        self.response_cache: Dict[str, str] = {}

        self.logger.info("🚀 High-Performance Message Coordinator initialized")

    async def cog_load(self):
        """Initialize the concurrent processor and register handlers"""
        # Initialize the concurrent message processor
        self.processor = await initialize_processor(self.bot)

        # Register our handlers
        await self._register_handlers()

        self.logger.info("⚡ Message Coordinator loaded and ready")

    async def cog_unload(self):
        """Cleanup on unload"""
        if hasattr(self, "processor") and self.processor:
            await self.processor.stop()

        self.logger.info("🛑 Message Coordinator unloaded")

    @commands.Cog.listener()
    async def on_ready(self):
        """Setup cog references when bot is ready"""
        await self._setup_cog_references()

    async def _setup_cog_references(self):
        """Get references to other cogs for direct handler access"""
        self.security_manager = self.bot.get_cog("SecurityManager")
        self.ai_companion = self.bot.get_cog("AICompanion")
        self.ai_moderation = self.bot.get_cog("AIModerationCog")
        self.analytics = self.bot.get_cog("Analytics")
        self.advanced_ai = self.bot.get_cog("AdvancedAICog")

        cog_status = {
            "SecurityManager": "✅" if self.security_manager else "❌",
            "AICompanion": "✅" if self.ai_companion else "❌",
            "AIModerationCog": "✅" if self.ai_moderation else "❌",
            "Analytics": "✅" if self.analytics else "❌",
            "AdvancedAICog": "✅" if self.advanced_ai else "❌",
        }

        self.logger.info("🔗 Cog References:")
        for cog_name, status in cog_status.items():
            self.logger.info(f"   {status} {cog_name}")

    async def _register_handlers(self):
        """Register all message processing handlers with the concurrent processor"""
        if not hasattr(self, "processor"):
            return

        # Register handlers with appropriate priorities
        self.processor.register_handler(
            "security_check", self._handle_security_check, "SecurityManager"
        )
        self.processor.register_handler(
            "ai_response", self._handle_ai_response, "AICompanion"
        )
        self.processor.register_handler(
            "support_response", self._handle_support_response, "AICompanion"
        )
        self.processor.register_handler(
            "conversation", self._handle_conversation, "AICompanion"
        )
        self.processor.register_handler(
            "analytics", self._handle_analytics, "Analytics"
        )
        self.processor.register_handler(
            "moderation", self._handle_moderation, "AIModerationCog"
        )

        self.logger.info("📝 All message handlers registered")

    # 🚀 TEMPORARILY DISABLED: Allow AI Companion to handle messages directly
    # @commands.Cog.listener()
    async def on_message_disabled(self, message: discord.Message):
        """
        🚀 MAIN MESSAGE ENTRY POINT
        Routes all messages through the concurrent processor for optimal performance
        """
        # Skip bot messages
        if message.author.bot:
            return

        # Track concurrent processing
        self.concurrent_responses += 1
        self.max_concurrent_reached = max(
            self.max_concurrent_reached, self.concurrent_responses
        )

        try:
            # Process through concurrent processor
            if hasattr(self, "processor") and self.processor:
                success = await self.processor.process_message(message)

                if success:
                    self.processed_messages += 1
                    self.logger.debug(
                        f"Message queued from {message.author} ({message.guild.name if message.guild else 'DM'})"
                    )
                else:
                    self.logger.debug(f"Message rate-limited from {message.author}")
            else:
                # Fallback to direct processing if processor not ready
                await self._fallback_processing(message)

        except Exception as e:
            self.logger.error(f"Message processing error: {e}")

        finally:
            self.concurrent_responses -= 1

    async def _fallback_processing(self, message: discord.Message):
        """Fallback processing when concurrent processor is not available"""
        try:
            # Process commands first
            await self.bot.process_commands(message)

            # Quick security check
            if self.security_manager and message.guild:
                await self._handle_security_check(message)

            # Basic AI response for mentions
            if self.bot.user in message.mentions or "astra" in message.content.lower():
                await self._handle_ai_response(message)

        except Exception as e:
            self.logger.error(f"Fallback processing error: {e}")

    # === CONCURRENT HANDLER METHODS ===

    async def _handle_security_check(self, message: discord.Message):
        """🛡️ Handle security violations with ultra-fast response"""
        if not self.security_manager or not message.guild:
            return

        try:
            # Use the security manager's existing message handler logic
            # But extract just the core security check
            guild_settings = self.security_manager.get_guild_settings(message.guild.id)
            if not guild_settings.get("security_enabled", True):
                return

            # Quick violation analysis
            should_act, violations = (
                await self.security_manager.security_system.analyze_message_security(
                    message
                )
            )

            if should_act and violations:
                # Handle violations immediately
                result = await self.security_manager.security_system.handle_violations(
                    message, violations
                )

                # Log and notify
                self.logger.info(
                    f"🛡️ FAST Security action: {message.author} - {result['action_taken']}"
                )

                # Notify moderators asynchronously (don't block)
                asyncio.create_task(
                    self.security_manager.notify_moderators_violation(
                        message, violations, result
                    )
                )

        except Exception as e:
            self.logger.error(f"Security check error: {e}")

    async def _handle_ai_response(self, message: discord.Message):
        """🤖 Handle AI responses with intelligent conversation flow"""
        if not self.ai_companion:
            return

        try:
            # Check for immediate response patterns
            content = message.content.lower().strip()

            # Instant responses for identity questions
            identity_patterns = [
                "who are you",
                "what are you",
                "who created you",
                "what can you do",
            ]

            for pattern in identity_patterns:
                if pattern in content:
                    await self._send_identity_response(message)
                    return

            # Handle mentions and direct questions
            if self.bot.user in message.mentions or "?" in content:
                await self._process_ai_conversation(message, priority="high")
            else:
                # Regular conversation processing
                await self._process_ai_conversation(message, priority="normal")

        except Exception as e:
            self.logger.error(f"AI response error: {e}")

    async def _handle_support_response(self, message: discord.Message):
        """🆘 Handle support requests with priority processing"""
        try:
            content = message.content.lower()

            # Quick support responses
            if "help" in content:
                embed = discord.Embed(
                    title="🆘 Quick Help",
                    description="I'm here to help! Use `/astra help` for all commands or mention me with your question.",
                    color=0x00FF00,
                )
                await message.channel.send(embed=embed)

            elif "error" in content or "issue" in content:
                embed = discord.Embed(
                    title="🔧 Technical Support",
                    description="I see you're having an issue. Please describe the problem and I'll help you resolve it!",
                    color=0xFFA500,
                )
                await message.channel.send(embed=embed)

            # Also process as AI response for detailed help
            await self._handle_ai_response(message)

        except Exception as e:
            self.logger.error(f"Support response error: {e}")

    async def _handle_conversation(self, message: discord.Message):
        """💬 Handle regular conversation with natural flow"""
        if not self.ai_companion:
            return

        try:
            # Use the AI companion's conversation logic
            await self._process_ai_conversation(message, priority="normal")

        except Exception as e:
            self.logger.error(f"Conversation error: {e}")

    async def _handle_analytics(self, message: discord.Message):
        """📊 Handle analytics tracking (background priority)"""
        if not self.analytics:
            return

        try:
            # Light analytics processing (don't block)
            asyncio.create_task(self._process_analytics_data(message))

        except Exception as e:
            self.logger.error(f"Analytics error: {e}")

    async def _handle_moderation(self, message: discord.Message):
        """🔨 Handle AI moderation checks"""
        if not self.ai_moderation:
            return

        try:
            # Quick moderation analysis
            violation = await self.ai_moderation._comprehensive_analysis(message)

            if violation:
                await self.ai_moderation._handle_violation_with_ai(message, violation)
            else:
                # Occasional positive reinforcement (async)
                asyncio.create_task(
                    self.ai_moderation._random_positive_reinforcement(message)
                )

        except Exception as e:
            self.logger.error(f"Moderation error: {e}")

    # === HELPER METHODS ===

    async def _send_identity_response(self, message: discord.Message):
        """Send instant identity response"""
        embed = discord.Embed(
            title="🌟 I'm Astra!",
            description="I'm an AI-powered Discord bot created by **x1ziad**. I can help with conversations, server management, space facts, and much more!",
            color=0x7C4DFF,
        )
        embed.add_field(
            name="🚀 What I Can Do",
            value="• Natural conversations\n• Server moderation\n• Space & astronomy facts\n• Quiz games\n• Analytics & insights",
            inline=False,
        )
        embed.set_footer(text="Use /astra help for all commands!")

        await message.channel.send(embed=embed)

    async def _process_ai_conversation(
        self, message: discord.Message, priority: str = "normal"
    ):
        """Process AI conversation with the companion cog"""
        if not self.ai_companion:
            return

        try:
            # Check if should respond based on AI companion logic
            content = message.content.lower()

            # Identity questions (handled above)
            identity_patterns = [
                "who are you",
                "what are you",
                "who created you",
                "what can you do",
            ]
            if any(pattern in content for pattern in identity_patterns):
                return  # Already handled

            # Check for conversation triggers
            should_respond = (
                self.bot.user in message.mentions
                or "astra" in content
                or "?" in content
                or message.channel.type == discord.ChannelType.private
                or priority == "high"
            )

            if should_respond:
                # Use AI companion's response generation
                if hasattr(self.ai_companion, "generate_contextual_response"):
                    response = await self.ai_companion.generate_contextual_response(
                        message
                    )
                    if response:
                        await message.channel.send(response)

        except Exception as e:
            self.logger.error(f"AI conversation error: {e}")

    async def _process_analytics_data(self, message: discord.Message):
        """Process analytics data in background"""
        if not self.analytics:
            return

        try:
            # Update message statistics
            if hasattr(self.analytics, "update_message_stats"):
                await self.analytics.update_message_stats(message)

        except Exception as e:
            self.logger.error(f"Analytics processing error: {e}")

    # === STATUS AND MONITORING ===

    @app_commands.command(
        name="processing_performance", description="Show message processing performance"
    )
    @app_commands.default_permissions(administrator=True)
    async def performance_status(self, interaction: discord.Interaction):
        """Show comprehensive performance statistics"""
        try:
            await interaction.response.defer()

            # Get processor stats
            if hasattr(self, "processor") and self.processor:
                embed = await self.processor.get_status_embed()

                # Add coordinator stats
                uptime = time.time() - self.start_time
                hours, remainder = divmod(int(uptime), 3600)
                minutes, seconds = divmod(remainder, 60)

                embed.add_field(
                    name="🎯 Coordinator Stats",
                    value=f"""
                    **Uptime:** {hours}h {minutes}m {seconds}s
                    **Messages Processed:** {self.processed_messages:,}
                    **Max Concurrent:** {self.max_concurrent_reached}
                    **Current Concurrent:** {self.concurrent_responses}
                    """,
                    inline=False,
                )
            else:
                embed = discord.Embed(
                    title="⚠️ Performance Monitor",
                    description="Concurrent processor not initialized",
                    color=0xFF0000,
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"❌ Error getting performance stats: {e}")

    @app_commands.command(
        name="test_concurrent", description="Test concurrent message processing"
    )
    @app_commands.default_permissions(administrator=True)
    async def test_concurrent_processing(
        self, interaction: discord.Interaction, count: int = 10
    ):
        """Test concurrent processing with simulated messages"""
        try:
            await interaction.response.defer()

            start_time = time.time()

            # Create test tasks
            tasks = []
            for i in range(count):
                task = asyncio.create_task(
                    self._simulate_message_processing(
                        interaction.user, f"Test message {i+1}"
                    )
                )
                tasks.append(task)

            # Run all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            end_time = time.time()
            processing_time = end_time - start_time

            # Calculate statistics
            successful = sum(1 for r in results if not isinstance(r, Exception))
            failed = count - successful

            embed = discord.Embed(
                title="🧪 Concurrent Processing Test Results",
                color=0x00FF00 if failed == 0 else 0xFFA500,
            )

            embed.add_field(
                name="📊 Results",
                value=f"""
                **Total Messages:** {count}
                **Successful:** {successful}
                **Failed:** {failed}
                **Processing Time:** {processing_time:.2f}s
                **Messages/Second:** {count/processing_time:.1f}
                """,
                inline=False,
            )

            if failed > 0:
                embed.add_field(
                    name="❌ Errors",
                    value=f"{failed} messages failed processing",
                    inline=False,
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"❌ Test error: {e}")

    async def _simulate_message_processing(self, user: discord.User, content: str):
        """Simulate message processing for testing"""

        # Create a mock message object
        class MockMessage:
            def __init__(self, user, content):
                self.author = user
                self.content = content
                self.guild = None
                self.channel = None

        mock_message = MockMessage(user, content)

        # Process through handlers
        await self._handle_analytics(mock_message)
        await asyncio.sleep(0.1)  # Simulate processing time

        return True


async def setup(bot):
    """Setup the High-Performance Coordinator cog"""
    await bot.add_cog(HighPerformanceCoordinator(bot))
