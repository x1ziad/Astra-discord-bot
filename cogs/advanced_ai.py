"""
Advanced AI Cog for Astra Bot
Implements modern AI features with simplified, reliable architecture
"""

import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
import logging
import random
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta, timezone
import json
import re
import os

# Performance optimization imports
from utils.command_optimizer import optimize_command, optimized_send
from utils.performance_optimizer import performance_optimizer

logger = logging.getLogger("astra.advanced_ai")

# Import AI systems with proper error handling
AI_ENGINE_AVAILABLE = False
OPTIMIZED_AI_AVAILABLE = False

try:
    from ai.consolidated_ai_engine import get_engine, initialize_engine

    AI_ENGINE_AVAILABLE = True
    logger.info("✅ Consolidated AI Engine imported successfully")
except ImportError as e:
    logger.warning(f"❌ Consolidated AI Engine not available: {e}")

try:
    from ai.optimized_ai_engine import OptimizedAIEngine, get_optimized_engine

    OPTIMIZED_AI_AVAILABLE = True
    logger.info("✅ Optimized AI Engine imported successfully")
except ImportError as e:
    logger.warning(f"❌ Optimized AI Engine not available: {e}")

# Import context manager
try:
    from ai.universal_context_manager import (
        get_context_manager,
        initialize_context_manager,
    )

    CONTEXT_MANAGER_AVAILABLE = True
    logger.info("✅ Universal Context Manager imported successfully")
except ImportError as e:
    logger.warning(f"❌ Universal Context Manager not available: {e}")
    CONTEXT_MANAGER_AVAILABLE = False


class AdvancedAICog(commands.Cog):
    """Advanced AI features with simplified, reliable architecture"""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("astra.advanced_ai")

        # Initialize AI client
        self.ai_client = None
        self._setup_ai_client()

        # Simplified conversation tracking
        self.conversation_history: Dict[int, List[Dict[str, str]]] = {}
        self.conversation_cooldowns: Dict[int, datetime] = {}
        self.max_history_length = 5

        # Performance tracking
        self.api_calls_made = 0
        self.successful_responses = 0
        self.start_time = datetime.now(timezone.utc)

        # Start essential background tasks only
        if self.ai_client:
            self.conversation_cleanup_task.start()
            self.logger.info("✅ Advanced AI Cog initialized successfully")
        else:
            self.logger.error(
                "❌ Advanced AI Cog failed to initialize - no AI client available"
            )

    def _setup_ai_client(self):
        """Setup AI engine with fallback options"""
        try:
            # Try optimized engine first
            if OPTIMIZED_AI_AVAILABLE:
                self.ai_client = get_optimized_engine()
                if self.ai_client:
                    self.logger.info("✅ Using Optimized AI Engine")
                    return

            # Fallback to consolidated engine
            if AI_ENGINE_AVAILABLE:
                self.ai_client = get_engine()
                if self.ai_client:
                    self.logger.info("✅ Using Consolidated AI Engine")
                    return

            # Initialize engine if not available
            try:
                self.ai_client = initialize_engine(
                    {
                        "ai_api_key": os.getenv("AI_API_KEY"),
                        "ai_model": os.getenv("AI_MODEL", "deepseek/deepseek-r1:nitro"),
                        "openrouter_api_key": os.getenv("OPENROUTER_API_KEY"),
                    }
                )
                if self.ai_client:
                    self.logger.info("✅ Initialized new AI Engine")
                    return
            except Exception as e:
                self.logger.error(f"Failed to initialize AI engine: {e}")

            self.logger.error("❌ No AI Engine available!")
            self.ai_client = None

        except Exception as e:
            self.logger.error(f"Failed to setup AI client: {e}")
            self.ai_client = None

    async def _generate_ai_response(
        self,
        prompt: str,
        user_id: int = None,
        guild_id: int = None,
        channel_id: int = None,
        username: str = None,
    ) -> str:
        """Generate AI response with simplified error handling"""
        try:
            if not self.ai_client:
                return (
                    "❌ AI service is not configured. Please check the configuration."
                )

            # Get conversation history
            history = self.conversation_history.get(user_id, [])

            # Generate response using available AI engine
            if hasattr(self.ai_client, "process_conversation"):
                response = await self.ai_client.process_conversation(
                    prompt, user_id, guild_id=guild_id, channel_id=channel_id
                )
            elif hasattr(self.ai_client, "generate_response"):
                response = await self.ai_client.generate_response(
                    prompt, context={"history": history}
                )
            else:
                # Fallback for basic AI clients
                response = "I'm here to help! However, my AI capabilities are currently limited."

            # Update conversation history
            if user_id and response:
                if user_id not in self.conversation_history:
                    self.conversation_history[user_id] = []

                self.conversation_history[user_id].append(
                    {"role": "user", "content": prompt}
                )
                self.conversation_history[user_id].append(
                    {"role": "assistant", "content": response}
                )

                # Keep only recent messages
                if (
                    len(self.conversation_history[user_id])
                    > self.max_history_length * 2
                ):
                    self.conversation_history[user_id] = self.conversation_history[
                        user_id
                    ][-self.max_history_length * 2 :]

            self.api_calls_made += 1
            self.successful_responses += 1

            return response

        except Exception as e:
            self.logger.error(f"AI response generation error: {e}")
            return f"❌ I'm having trouble thinking right now. Please try again in a moment."

    @app_commands.command(name="chat", description="Chat with Astra AI")
    @app_commands.describe(message="Your message to the AI")
    @optimize_command(rate_limit_enabled=True, rate_limit_per_minute=20)
    async def chat_command(self, interaction: discord.Interaction, message: str):
        """Chat with AI assistant - Optimized for performance"""
        try:
            await interaction.response.defer()

            if not self.ai_client:
                await interaction.followup.send(
                    "❌ AI service is not available. Please try again later.",
                    ephemeral=True,
                )
                return

            # Optimize AI request
            guild_id = interaction.guild.id if interaction.guild else None
            optimized_prompt, metadata = (
                await performance_optimizer.ai_optimizer.optimize_ai_request(
                    message, interaction.user.id, guild_id
                )
            )

            # Generate AI response with optimization
            response = await self._generate_ai_response(
                optimized_prompt,
                interaction.user.id,
                guild_id=guild_id,
                channel_id=interaction.channel.id,
                username=str(interaction.user),
            )

            # Cache the response
            await performance_optimizer.ai_optimizer.cache_response(
                message, response, guild_id, metadata
            )

            # Create optimized embed
            embed = discord.Embed(
                title="🤖 Astra AI Chat",
                description=response[:4000],  # Ensure it fits in embed
                color=0x7289DA,
                timestamp=datetime.now(timezone.utc),
            )
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url,
            )

            # Add user message as field
            message_preview = message[:1000] + ("..." if len(message) > 1000 else "")
            embed.add_field(
                name="💬 Your Message",
                value=message_preview,
                inline=False,
            )

            # Add optimization info for debugging
            if metadata.get("optimization_applied"):
                embed.set_footer(
                    text=f"⚡ Optimized • Model: {metadata.get('model_selected', 'default')}"
                )

            await optimized_send(interaction.followup, embed=embed)

        except Exception as e:
            self.logger.error(f"Chat command error: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"❌ Error processing chat request: {str(e)}", ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"❌ Error processing chat request: {str(e)}", ephemeral=True
                )

    @app_commands.command(name="analyze", description="Analyze text or content with AI")
    @app_commands.describe(content="Content to analyze")
    async def analyze_command(self, interaction: discord.Interaction, content: str):
        """Analyze content with AI"""
        try:
            await interaction.response.defer()

            if not self.ai_client:
                await interaction.followup.send(
                    "❌ AI service is not available. Please try again later.",
                    ephemeral=True,
                )
                return

            analysis_prompt = f"Please analyze the following content and provide insights, key points, and summary:\n\n{content}"
            response = await self._generate_ai_response(
                analysis_prompt, interaction.user.id
            )

            embed = discord.Embed(
                title="🔍 AI Content Analysis",
                description=response[:4000],
                color=0x7289DA,
                timestamp=datetime.now(timezone.utc),
            )

            content_preview = content[:500] + ("..." if len(content) > 500 else "")
            embed.add_field(
                name="📝 Analyzed Content",
                value=content_preview,
                inline=False,
            )
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Analysis command error: {e}")
            await interaction.followup.send(
                f"❌ Error analyzing content: {str(e)}", ephemeral=True
            )

    @app_commands.command(name="summarize", description="Summarize long text with AI")
    @app_commands.describe(content="Content to summarize")
    async def summarize_command(self, interaction: discord.Interaction, content: str):
        """Summarize content with AI"""
        try:
            await interaction.response.defer()

            if not self.ai_client:
                await interaction.followup.send(
                    "❌ AI service is not available. Please try again later.",
                    ephemeral=True,
                )
                return

            summarize_prompt = f"Please provide a concise summary of the following content:\n\n{content}"
            response = await self._generate_ai_response(
                summarize_prompt, interaction.user.id
            )

            embed = discord.Embed(
                title="📋 AI Summary",
                description=response[:4000],
                color=0x7289DA,
                timestamp=datetime.now(timezone.utc),
            )

            content_preview = content[:500] + ("..." if len(content) > 500 else "")
            embed.add_field(
                name="📄 Original Content",
                value=content_preview,
                inline=False,
            )
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Summarize command error: {e}")
            await interaction.followup.send(
                f"❌ Error summarizing content: {str(e)}", ephemeral=True
            )

    @app_commands.command(
        name="translate", description="Translate text to another language"
    )
    @app_commands.describe(
        text="Text to translate",
        target_language="Target language (e.g., Spanish, French, German)",
    )
    async def translate_command(
        self, interaction: discord.Interaction, text: str, target_language: str
    ):
        """Translate text using AI"""
        try:
            await interaction.response.defer()

            if not self.ai_client:
                await interaction.followup.send(
                    "❌ AI service is not available. Please try again later.",
                    ephemeral=True,
                )
                return

            translate_prompt = (
                f"Translate the following text to {target_language}:\n\n{text}"
            )
            response = await self._generate_ai_response(
                translate_prompt, interaction.user.id
            )

            embed = discord.Embed(
                title="🌐 AI Translation",
                color=0x7289DA,
                timestamp=datetime.now(timezone.utc),
            )

            text_preview = text[:500] + ("..." if len(text) > 500 else "")
            embed.add_field(
                name="📝 Original Text",
                value=text_preview,
                inline=False,
            )
            embed.add_field(
                name=f"🔄 Translation ({target_language})",
                value=response[:1000] + ("..." if len(response) > 1000 else ""),
                inline=False,
            )
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Translation command error: {e}")
            await interaction.followup.send(
                f"❌ Error translating text: {str(e)}", ephemeral=True
            )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Enhanced message listener with context manager integration"""
        if message.author.bot:
            return

        # Skip if this was a command to avoid double processing
        if message.content.startswith(
            tuple(await self.bot._get_dynamic_prefix(self.bot, message))
        ):
            return

        try:
            # Use context manager if available
            if CONTEXT_MANAGER_AVAILABLE:
                context_manager = get_context_manager()
                if not context_manager:
                    context_manager = initialize_context_manager(self.bot)

                if context_manager:
                    # Analyze message with context manager
                    message_context = await context_manager.analyze_message(
                        message.content,
                        message.author.id,
                        message.channel.id,
                        message.guild.id if message.guild else None,
                        message.author.display_name,
                    )

                    # Check if bot should respond
                    should_respond, response_reason = (
                        await context_manager.should_respond(
                            message_context,
                            message.channel.id,
                            message.guild.id if message.guild else None,
                        )
                    )

                    if should_respond:
                        await self._process_ai_conversation(message)
                        await context_manager.mark_response_sent(
                            message_context, message.channel.id
                        )

                    return

            # Fallback to basic response logic
            should_respond = await self._should_ai_respond(message)
            if should_respond:
                await self._process_ai_conversation(message)

        except Exception as e:
            self.logger.error(f"Error in message processing: {e}")

    async def _should_ai_respond(self, message: discord.Message) -> bool:
        """Simplified AI response determination"""
        user_id = message.author.id
        content_lower = message.content.lower()

        # Check cooldown
        if user_id in self.conversation_cooldowns:
            if datetime.now(timezone.utc) - self.conversation_cooldowns[
                user_id
            ] < timedelta(seconds=5):
                return False

        # Always respond to mentions and DMs
        if self.bot.user in message.mentions:
            return True

        if isinstance(message.channel, discord.DMChannel):
            return True

        # Respond to AI keywords
        ai_keywords = ["astra", "hey bot", "ai help"]
        if any(keyword in content_lower for keyword in ai_keywords):
            return True

        # Respond to questions
        if "?" in message.content:
            return True

        # Random engagement (low probability)
        if len(message.content) > 30:
            return random.random() < 0.1  # 10% chance for longer messages

        return False

    async def _process_ai_conversation(self, message: discord.Message):
        """Process AI conversation with simplified logic"""
        try:
            if not self.ai_client:
                return

            # Generate response
            response = await self._generate_ai_response(
                message.content,
                message.author.id,
                guild_id=message.guild.id if message.guild else None,
                channel_id=message.channel.id,
                username=str(message.author),
            )

            # Send response (handle long messages)
            if len(response) > 2000:
                # Split at sentence boundaries
                sentences = response.split(". ")
                chunks = []
                current_chunk = ""

                for sentence in sentences:
                    if len(current_chunk + sentence + ". ") > 1900:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            current_chunk = sentence + ". "
                        else:
                            chunks.append(sentence[:1900])
                    else:
                        current_chunk += sentence + ". "

                if current_chunk:
                    chunks.append(current_chunk.strip())

                # Send chunks
                for chunk in chunks:
                    await message.channel.send(chunk)
                    await asyncio.sleep(0.5)  # Small delay between chunks
            else:
                await message.channel.send(response)

            # Update cooldown
            self.conversation_cooldowns[message.author.id] = datetime.now(timezone.utc)

        except Exception as e:
            self.logger.error(f"AI conversation processing error: {e}")
            try:
                await message.channel.send(
                    "I'm having some trouble thinking right now. Give me a moment! 🤖"
                )
            except:
                pass  # Don't crash if we can't send error message

    @tasks.loop(hours=1)
    async def conversation_cleanup_task(self):
        """Clean up old conversation data"""
        try:
            current_time = datetime.now(timezone.utc)

            # Clean up conversation cooldowns
            expired_cooldowns = [
                user_id
                for user_id, timestamp in self.conversation_cooldowns.items()
                if current_time - timestamp > timedelta(hours=1)
            ]
            for user_id in expired_cooldowns:
                del self.conversation_cooldowns[user_id]

            # Clean up old conversation history
            for user_id in list(self.conversation_history.keys()):
                if (
                    len(self.conversation_history[user_id])
                    > self.max_history_length * 2
                ):
                    self.conversation_history[user_id] = self.conversation_history[
                        user_id
                    ][-self.max_history_length * 2 :]

            self.logger.debug("Conversation cleanup completed")

        except Exception as e:
            self.logger.error(f"Conversation cleanup task error: {e}")

    def cog_unload(self):
        """Clean up when cog is unloaded"""
        try:
            self.conversation_cleanup_task.cancel()
            self.logger.info("Advanced AI Cog unloaded")
        except:
            pass

    @app_commands.command(name="ai_status", description="Check AI system status")
    async def ai_status_command(self, interaction: discord.Interaction):
        """Check AI system status"""
        try:
            embed = discord.Embed(
                title="🤖 AI System Status",
                color=0x00FF00 if self.ai_client else 0xFF0000,
                timestamp=datetime.now(timezone.utc),
            )

            # AI Engine Status
            ai_status = "✅ Online" if self.ai_client else "❌ Offline"
            embed.add_field(name="AI Engine", value=ai_status, inline=True)

            # Performance Stats
            uptime = datetime.now(timezone.utc) - self.start_time
            embed.add_field(name="Uptime", value=str(uptime).split(".")[0], inline=True)
            embed.add_field(
                name="API Calls", value=f"{self.api_calls_made:,}", inline=True
            )
            embed.add_field(
                name="Successful Responses",
                value=f"{self.successful_responses:,}",
                inline=True,
            )

            # Active Conversations
            active_conversations = len(self.conversation_history)
            embed.add_field(
                name="Active Conversations",
                value=f"{active_conversations:,}",
                inline=True,
            )

            # System Info
            embed.add_field(
                name="Available Systems",
                value=(
                    f"• Optimized Engine: {'✅' if OPTIMIZED_AI_AVAILABLE else '❌'}\n"
                    f"• Consolidated Engine: {'✅' if AI_ENGINE_AVAILABLE else '❌'}\n"
                    f"• Context Manager: {'✅' if CONTEXT_MANAGER_AVAILABLE else '❌'}"
                ),
                inline=False,
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            self.logger.error(f"AI status command error: {e}")
            await interaction.response.send_message(
                f"❌ Error checking AI status: {str(e)}", ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(AdvancedAICog(bot))
