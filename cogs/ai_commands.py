"""
Enhanced AI Commands for Astra Bot
Provides comprehensive AI features including chat, image generation, and TTS
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging
import asyncio
import aiohttp
import io
import os
import base64
import json
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from pathlib import Path
import re

from ai.enhanced_ai_handler import EnhancedAIHandler
from config.config_manager import config_manager

logger = logging.getLogger("astra.ai_commands")


class AICommands(commands.GroupCog, name="ai"):
    """Advanced AI commands for chat, image generation, and voice synthesis"""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.config = config_manager
        self.logger = bot.logger
        self.ai_handler = EnhancedAIHandler()

        # Load configuration
        self.dedicated_channels = self._load_dedicated_channels()
        self.active_conversations = {}  # Track active conversations
        self.conversation_cooldowns = {}  # Prevent spam

        # Initialize data directories
        Path("data/ai").mkdir(parents=True, exist_ok=True)
        Path("data/ai/images").mkdir(parents=True, exist_ok=True)
        Path("data/ai/audio").mkdir(parents=True, exist_ok=True)

        self.logger.info("Enhanced AI Commands cog initialized")

    def _load_dedicated_channels(self) -> List[int]:
        """Load dedicated AI channels from config"""
        return self.ai_handler.config.get("trigger_modes", {}).get(
            "dedicated_channels", []
        )

    async def _check_cooldown(self, user_id: int, cooldown_seconds: int = 3) -> bool:
        """Check if user is on cooldown"""
        now = datetime.utcnow()
        if user_id in self.conversation_cooldowns:
            if (now - self.conversation_cooldowns[user_id]).seconds < cooldown_seconds:
                return False
        self.conversation_cooldowns[user_id] = now
        return True

    @commands.Cog.listener()
    async def on_message(self, message):
        """Enhanced message listener with intelligent AI triggering"""
        # Ignore bot messages to prevent loops
        if message.author.bot:
            return

        # Check cooldown to prevent spam
        if not await self._check_cooldown(message.author.id):
            return

        trigger_modes = self.ai_handler.config.get("trigger_modes", {})
        should_respond = False
        response_type = "text"

        # Check various trigger conditions
        if trigger_modes.get("dm", True) and isinstance(
            message.channel, discord.DMChannel
        ):
            should_respond = True
        elif trigger_modes.get("mention", True) and self.bot.user in message.mentions:
            should_respond = True
        elif message.channel.id in self.dedicated_channels:
            should_respond = True
        elif (
            trigger_modes.get("keyword")
            and trigger_modes.get("keyword").lower() in message.content.lower()
        ):
            should_respond = True

        # Smart engagement patterns
        elif self._should_engage_proactively(message):
            should_respond = True

        if should_respond:
            await self._process_ai_message(message, response_type)

    def _should_engage_proactively(self, message) -> bool:
        """Determine if bot should proactively engage based on message patterns"""
        content = message.content.lower()

        # Engage on questions directed at the server
        question_patterns = [
            r"\b(what|who|where|when|why|how)\b.*\?",
            r"\b(anyone|somebody|someone)\b.*\?",
            r"\bhelp\b",
            r"\bquestion\b",
        ]

        for pattern in question_patterns:
            if re.search(pattern, content):
                return True

        # Engage on space/stellaris related topics
        space_keywords = [
            "space",
            "star",
            "planet",
            "galaxy",
            "stellaris",
            "empire",
            "alien",
        ]
        if any(keyword in content for keyword in space_keywords):
            return True

        return False

    async def _process_ai_message(self, message, response_type: str = "text"):
        """Process message and generate AI response"""
        try:
            async with message.channel.typing():
                # Add user message to history
                await self.ai_handler.add_message_to_history(
                    message.channel.id,
                    message.author.id,
                    str(message.author),
                    message.content,
                )

                # Get AI response
                response = await self.ai_handler.get_ai_response(
                    message.channel.id, response_type=response_type
                )

                if response_type == "text":
                    # Handle long responses with embeds
                    if len(response) > 2000:
                        embed = discord.Embed(
                            title="🤖 Astra AI Response",
                            description=response[:4000],
                            color=self.config.get_color("primary"),
                        )
                        await message.reply(embed=embed)
                    else:
                        await message.reply(response)

                # Add bot response to history
                await self.ai_handler.add_message_to_history(
                    message.channel.id, self.bot.user.id, "Astra", response, is_bot=True
                )

        except Exception as e:
            self.logger.error(f"Error processing AI message: {e}")
            await message.reply(
                "🚫 Sorry, I encountered an error processing your message."
            )

    @app_commands.command(name="chat", description="Have a conversation with Astra AI")
    @app_commands.describe(
        message="Your message to Astra", personality="Choose AI personality (optional)"
    )
    async def ai_chat(
        self,
        interaction: discord.Interaction,
        message: str,
        personality: Optional[str] = None,
    ):
        """Enhanced chat command with personality options"""
        await interaction.response.defer(thinking=True)

        try:
            # Set personality if specified
            if personality:
                await self.ai_handler.set_personality(personality)

            # Add message to history
            await self.ai_handler.add_message_to_history(
                interaction.channel_id,
                interaction.user.id,
                str(interaction.user),
                message,
            )

            # Get AI response
            response = await self.ai_handler.get_ai_response(interaction.channel_id)

            # Create rich embed response
            embed = discord.Embed(
                title="💬 Astra AI Chat",
                description=response,
                color=self.config.get_color("primary"),
                timestamp=datetime.utcnow(),
            )
            embed.set_footer(
                text=f"Personality: {personality or 'Default'} | Requested by {interaction.user.display_name}",
                icon_url=interaction.user.display_avatar.url,
            )

            await interaction.followup.send(embed=embed)

            # Add bot response to history
            await self.ai_handler.add_message_to_history(
                interaction.channel_id, self.bot.user.id, "Astra", response, is_bot=True
            )

        except Exception as e:
            self.logger.error(f"Error in AI chat: {e}")
            await interaction.followup.send(
                "🚫 Sorry, I encountered an error. Please try again later."
            )

    @app_commands.command(name="generate", description="Generate AI images with DALL-E")
    @app_commands.describe(
        prompt="Describe the image you want to generate",
        style="Art style for the image",
        size="Image size",
    )
    async def generate_image(
        self,
        interaction: discord.Interaction,
        prompt: str,
        style: Optional[str] = "realistic",
        size: Optional[str] = "1024x1024",
    ):
        """Generate images using AI"""
        await interaction.response.defer(thinking=True)

        try:
            # Generate image
            image_url, revised_prompt = await self.ai_handler.generate_image(
                prompt, style=style, size=size
            )

            if image_url:
                # Create embed with generated image
                embed = discord.Embed(
                    title="🎨 AI Generated Image",
                    description=f"**Original Prompt:** {prompt}\n**Revised Prompt:** {revised_prompt}",
                    color=self.config.get_color("success"),
                    timestamp=datetime.utcnow(),
                )
                embed.set_image(url=image_url)
                embed.set_footer(
                    text=f"Generated by {interaction.user.display_name} | Style: {style}",
                    icon_url=interaction.user.display_avatar.url,
                )

                await interaction.followup.send(embed=embed)

                # Log generation
                self.logger.info(
                    f"Image generated for user {interaction.user.id}: {prompt}"
                )

            else:
                await interaction.followup.send(
                    "🚫 Failed to generate image. Please try a different prompt."
                )

        except Exception as e:
            self.logger.error(f"Error generating image: {e}")
            await interaction.followup.send(
                "🚫 Image generation failed. Please try again later."
            )

    @app_commands.command(
        name="speak", description="Convert text to speech using AI TTS"
    )
    @app_commands.describe(text="Text to convert to speech", voice="Voice type for TTS")
    async def text_to_speech(
        self,
        interaction: discord.Interaction,
        text: str,
        voice: Optional[str] = "alloy",
    ):
        """Convert text to speech using AI TTS"""
        await interaction.response.defer(thinking=True)

        try:
            # Generate speech
            audio_data = await self.ai_handler.text_to_speech(text, voice=voice)

            if audio_data:
                # Save audio file
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                filename = f"tts_{interaction.user.id}_{timestamp}.mp3"
                filepath = Path("data/ai/audio") / filename

                with open(filepath, "wb") as f:
                    f.write(audio_data)

                # Create embed and send audio file
                embed = discord.Embed(
                    title="🔊 Text-to-Speech",
                    description=f"**Text:** {text[:500]}{'...' if len(text) > 500 else ''}",
                    color=self.config.get_color("primary"),
                    timestamp=datetime.utcnow(),
                )
                embed.set_footer(
                    text=f"Generated by {interaction.user.display_name} | Voice: {voice}",
                    icon_url=interaction.user.display_avatar.url,
                )

                await interaction.followup.send(
                    embed=embed,
                    file=discord.File(filepath, filename=f"astra_tts_{timestamp}.mp3"),
                )

                # Clean up file after a delay
                asyncio.create_task(self._cleanup_audio_file(filepath, delay=300))

            else:
                await interaction.followup.send(
                    "🚫 Failed to generate speech. Please try again."
                )

        except Exception as e:
            self.logger.error(f"Error in TTS: {e}")
            await interaction.followup.send(
                "🚫 Text-to-speech failed. Please try again later."
            )

    async def _cleanup_audio_file(self, filepath: Path, delay: int = 300):
        """Clean up audio file after delay"""
        await asyncio.sleep(delay)
        try:
            if filepath.exists():
                filepath.unlink()
        except Exception as e:
            self.logger.error(f"Error cleaning up audio file: {e}")

    @app_commands.command(
        name="personality", description="Manage AI personality settings"
    )
    @app_commands.describe(action="Action to perform", name="Personality name")
    async def manage_personality(
        self, interaction: discord.Interaction, action: str, name: Optional[str] = None
    ):
        """Manage AI personality profiles"""
        await interaction.response.defer(thinking=True)

        try:
            if action.lower() == "list":
                personalities = self.ai_handler.list_personalities()
                embed = discord.Embed(
                    title="🎭 Available AI Personalities",
                    description="\n".join([f"• {p}" for p in personalities])
                    or "No personalities found",
                    color=self.config.get_color("info"),
                )
                await interaction.followup.send(embed=embed)

            elif action.lower() == "set" and name:
                success = await self.ai_handler.set_personality(name)
                if success:
                    embed = discord.Embed(
                        title="✅ Personality Set",
                        description=f"AI personality changed to: **{name}**",
                        color=self.config.get_color("success"),
                    )
                else:
                    embed = discord.Embed(
                        title="❌ Personality Not Found",
                        description=f"Personality '{name}' not found",
                        color=self.config.get_color("error"),
                    )
                await interaction.followup.send(embed=embed)

            else:
                await interaction.followup.send(
                    "❌ Invalid action. Use 'list' or 'set <name>'"
                )

        except Exception as e:
            self.logger.error(f"Error managing personality: {e}")
            await interaction.followup.send("🚫 Error managing personality settings.")

    @app_commands.command(name="clear", description="Clear AI conversation history")
    async def clear_history(self, interaction: discord.Interaction):
        """Clear conversation history for current channel"""
        await interaction.response.defer(thinking=True)

        try:
            await self.ai_handler.clear_history(interaction.channel_id)

            embed = discord.Embed(
                title="🗑️ History Cleared",
                description="AI conversation history has been cleared for this channel",
                color=self.config.get_color("success"),
            )
            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error clearing history: {e}")
            await interaction.followup.send("🚫 Error clearing conversation history.")

    @app_commands.command(name="stats", description="Show AI usage statistics")
    async def ai_stats(self, interaction: discord.Interaction):
        """Show AI usage statistics"""
        await interaction.response.defer(thinking=True)

        try:
            stats = await self.ai_handler.get_usage_stats()

            embed = discord.Embed(
                title="📊 AI Usage Statistics",
                color=self.config.get_color("info"),
                timestamp=datetime.utcnow(),
            )

            embed.add_field(
                name="💬 Chat Messages",
                value=f"{stats.get('chat_messages', 0):,}",
                inline=True,
            )
            embed.add_field(
                name="🎨 Images Generated",
                value=f"{stats.get('images_generated', 0):,}",
                inline=True,
            )
            embed.add_field(
                name="🔊 TTS Requests",
                value=f"{stats.get('tts_requests', 0):,}",
                inline=True,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error getting AI stats: {e}")
            await interaction.followup.send("🚫 Error retrieving AI statistics.")


async def setup(bot):
    await bot.add_cog(AICommands(bot))
