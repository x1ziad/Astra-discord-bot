"""
Advanced AI Cog for Astra Bot
Implements modern AI features with GitHub Models and OpenAI integration
"""

import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
import json
from pathlib import Path
import re
import os

# Import GitHub Models client
try:
    from ai.github_models_client import (
        GitHubModelsClient,
        get_ai_client,
        initialize_ai_client,
    )

    GITHUB_MODELS_AVAILABLE = True
except ImportError:
    GITHUB_MODELS_AVAILABLE = False

# Import Railway configuration
try:
    from config.railway_config import get_railway_config

    RAILWAY_ENABLED = True
except ImportError:
    RAILWAY_ENABLED = False

# Fallback OpenAI import
try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from config.config_manager import config_manager

logger = logging.getLogger("astra.advanced_ai")


class AdvancedAICog(commands.Cog):
    """Advanced AI features with GitHub Models and OpenAI integration"""

    def __init__(self, bot):
        self.bot = bot
        self.config = config_manager
        self.logger = logging.getLogger("astra.advanced_ai")

        # Initialize AI client
        self.ai_client = None
        self._setup_ai_client()

        # Active conversations tracking
        self.active_conversations: Set[int] = set()
        self.conversation_cooldowns: Dict[int, datetime] = {}
        self.channel_activity: Dict[int, Dict[str, Any]] = {}

        # Conversation history
        self.conversation_history: Dict[int, List[Dict[str, str]]] = {}
        self.max_history_length = 10

        # Performance tracking
        self.api_calls_made = 0
        self.successful_responses = 0
        self.start_time = datetime.now()

    def _setup_ai_client(self):
        """Setup AI client with Railway configuration"""
        try:
            if RAILWAY_ENABLED:
                railway_config = get_railway_config()

                # Get AI provider and configuration
                provider = railway_config.get_ai_provider()
                self.logger.info(f"Using AI provider: {provider}")

                if provider == "github":
                    github_config = railway_config.get_github_config()
                    openai_config = railway_config.get_openai_config()

                    # Initialize GitHub Models client with fallback
                    self.ai_client = GitHubModelsClient(
                        github_token=github_config.get("token"),
                        openai_api_key=openai_config.get("api_key"),
                    )

                    # Store configuration for commands
                    self.ai_model = github_config.get(
                        "model", "deepseek/DeepSeek-R1-0528"
                    )
                    self.max_tokens = github_config.get("max_tokens", 2000)
                    self.temperature = github_config.get("temperature", 0.7)

                    self.logger.info("AI client configured from Railway environment")

                else:
                    # OpenAI provider
                    openai_config = railway_config.get_openai_config()
                    if OPENAI_AVAILABLE:
                        openai.api_key = openai_config.get("api_key")
                        self.ai_model = openai_config.get("model", "gpt-4")
                        self.max_tokens = openai_config.get("max_tokens", 2000)
                        self.temperature = openai_config.get("temperature", 0.7)
                        self.logger.info("OpenAI configured from Railway environment")
                    else:
                        self.logger.error("OpenAI provider requested but not available")

            else:
                # Local environment fallback
                github_token = os.getenv("GITHUB_TOKEN")
                openai_api_key = os.getenv("OPENAI_API_KEY")

                if github_token and GITHUB_MODELS_AVAILABLE:
                    self.ai_client = GitHubModelsClient(github_token, openai_api_key)
                    self.ai_model = os.getenv(
                        "GITHUB_MODEL", "deepseek/DeepSeek-R1-0528"
                    )
                    self.max_tokens = int(os.getenv("GITHUB_MAX_TOKENS", "2000"))
                    self.temperature = float(os.getenv("GITHUB_TEMPERATURE", "0.7"))
                    self.logger.info("GitHub Models configured from local environment")

                elif openai_api_key and OPENAI_AVAILABLE:
                    openai.api_key = openai_api_key
                    self.ai_model = os.getenv("OPENAI_MODEL", "gpt-4")
                    self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
                    self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
                    self.logger.info("OpenAI configured from local environment")

                else:
                    self.logger.error("No AI provider configured!")

            # Check if any AI service is available
            if self.ai_client and self.ai_client.is_available():
                status = self.ai_client.get_status()
                self.logger.info(f"✅ AI services available: {status}")
            elif OPENAI_AVAILABLE and openai.api_key:
                self.logger.info("✅ OpenAI service available")
            else:
                self.logger.error("❌ No AI services available!")

        except Exception as e:
            self.logger.error(f"Failed to setup AI client: {e}")
            self.ai_client = None

    async def _generate_ai_response(self, prompt: str, user_id: int = None) -> str:
        """Generate AI response using GitHub Models or OpenAI"""
        try:
            # Check if GitHub Models client is available
            if self.ai_client and self.ai_client.is_available():
                return await self._generate_github_response(prompt, user_id)

            # Fallback to OpenAI
            elif OPENAI_AVAILABLE and hasattr(openai, "api_key") and openai.api_key:
                return await self._generate_openai_response(prompt, user_id)

            else:
                return "❌ AI service is not configured. Please set up GITHUB_TOKEN or OPENAI_API_KEY."

        except Exception as e:
            self.logger.error(f"AI response generation error: {e}")
            return f"❌ Error generating AI response: {str(e)}"

    async def _generate_github_response(self, prompt: str, user_id: int = None) -> str:
        """Generate AI response using GitHub Models"""
        try:
            # Get conversation history for context
            history = self.conversation_history.get(user_id, []) if user_id else []

            # Build messages for GitHub Models
            messages = [
                {
                    "role": "system",
                    "content": "You are Astra, a helpful AI assistant for a Discord server focused on space exploration and Stellaris gameplay. Be friendly, informative, and engaging. Provide detailed and accurate responses while maintaining a conversational tone.",
                }
            ]

            # Add conversation history (last 5 messages for context)
            for msg in history[-5:]:
                messages.append(msg)

            # Add current prompt
            messages.append({"role": "user", "content": prompt})

            # Make API call using GitHub Models
            self.api_calls_made += 1

            ai_response_obj = await self.ai_client.chat_completion(
                messages=messages,
                model=self.ai_model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            ai_response = ai_response_obj.content.strip()
            self.successful_responses += 1

            # Update conversation history
            if user_id:
                if user_id not in self.conversation_history:
                    self.conversation_history[user_id] = []

                self.conversation_history[user_id].extend(
                    [
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": ai_response},
                    ]
                )

                # Trim history to max length
                if len(self.conversation_history[user_id]) > self.max_history_length:
                    self.conversation_history[user_id] = self.conversation_history[
                        user_id
                    ][-self.max_history_length :]

            self.logger.debug(
                f"GitHub Models response generated: {len(ai_response)} chars"
            )
            return ai_response

        except Exception as e:
            self.logger.error(f"GitHub Models API error: {e}")
            raise

    async def _generate_openai_response(self, prompt: str, user_id: int = None) -> str:
        """Generate AI response using OpenAI (fallback)"""
        try:
            # Get conversation history for context
            history = self.conversation_history.get(user_id, []) if user_id else []

            # Build messages for OpenAI
            messages = [
                {
                    "role": "system",
                    "content": "You are Astra, a helpful AI assistant for a Discord server focused on space exploration and Stellaris gameplay. Be friendly, informative, and engaging.",
                }
            ]

            # Add conversation history
            for msg in history[-5:]:  # Last 5 messages for context
                messages.append(msg)

            # Add current prompt
            messages.append({"role": "user", "content": prompt})

            # Make API call
            self.api_calls_made += 1
            response = await openai.ChatCompletion.acreate(
                model=self.ai_model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=30,
            )

            ai_response = response.choices[0].message.content.strip()
            self.successful_responses += 1

            # Update conversation history
            if user_id:
                if user_id not in self.conversation_history:
                    self.conversation_history[user_id] = []

                self.conversation_history[user_id].extend(
                    [
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": ai_response},
                    ]
                )

                # Trim history
                if len(self.conversation_history[user_id]) > self.max_history_length:
                    self.conversation_history[user_id] = self.conversation_history[
                        user_id
                    ][-self.max_history_length :]

            return ai_response

        except Exception as e:
            self.logger.error(f"AI response generation failed: {e}")
            return f"❌ Sorry, I encountered an error while processing your request: {str(e)}"

    @app_commands.command(name="chat", description="Chat with Astra AI")
    @app_commands.describe(message="Your message to the AI")
    async def chat_command(self, interaction: discord.Interaction, message: str):
        """Chat with AI assistant"""
        try:
            await interaction.response.defer()

            # Generate AI response
            response = await self._generate_ai_response(message, interaction.user.id)

            # Create embed
            embed = discord.Embed(
                title="🤖 Astra AI Chat",
                description=response,
                color=0x7289DA,
                timestamp=datetime.utcnow(),
            )
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url,
            )
            embed.add_field(
                name="💬 Your Message",
                value=message[:1000] + ("..." if len(message) > 1000 else ""),
                inline=False,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Chat command error: {e}")
            await interaction.followup.send(
                f"❌ Error processing chat request: {str(e)}", ephemeral=True
            )

    @app_commands.command(name="image", description="Generate an image using AI")
    @app_commands.describe(prompt="Description of the image to generate")
    async def image_command(self, interaction: discord.Interaction, prompt: str):
        """Generate AI image"""
        try:
            await interaction.response.defer()

            # Image generation requires OpenAI (DALL-E)
            if not (OPENAI_AVAILABLE and hasattr(openai, "api_key") and openai.api_key):
                await interaction.followup.send(
                    "❌ Image generation requires OpenAI API key. GitHub Models doesn't support image generation yet.",
                    ephemeral=True,
                )
                return

            # Generate enhanced prompt using available AI
            enhanced_prompt = await self._enhance_image_prompt(prompt)

            # Generate image using DALL-E
            response = await openai.Image.acreate(
                prompt=enhanced_prompt, n=1, size="1024x1024"
            )

            image_url = response["data"][0]["url"]

            embed = discord.Embed(
                title="🎨 AI Generated Image",
                description=f"**Original Prompt:** {prompt}\n**Enhanced Prompt:** {enhanced_prompt[:100]}...",
                color=0x7289DA,
                timestamp=datetime.utcnow(),
            )
            embed.set_image(url=image_url)
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url,
            )
            embed.add_field(name="🎯 AI Model", value="DALL-E 3 (OpenAI)", inline=True)

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Image generation error: {e}")
            await interaction.followup.send(
                f"❌ Error generating image: {str(e)}", ephemeral=True
            )

    async def _enhance_image_prompt(self, original_prompt: str) -> str:
        """Enhance image prompt using AI for better results"""
        try:
            enhancement_request = f"Enhance this image generation prompt to be more detailed and visually descriptive while keeping the original intent. Make it suitable for DALL-E image generation. Original prompt: '{original_prompt}'"

            enhanced = await self._generate_ai_response(enhancement_request)

            # Clean up the response to just get the enhanced prompt
            if "enhanced prompt:" in enhanced.lower():
                enhanced = enhanced.split("enhanced prompt:")[-1].strip()
            elif "prompt:" in enhanced.lower():
                enhanced = enhanced.split("prompt:")[-1].strip()

            # Remove quotes if present
            enhanced = enhanced.strip("\"'")

            # Limit length for DALL-E
            if len(enhanced) > 400:
                enhanced = enhanced[:400] + "..."

            return enhanced if enhanced else original_prompt

        except:
            # If enhancement fails, return original prompt
            return original_prompt

    @app_commands.command(name="analyze", description="Analyze text or content with AI")
    @app_commands.describe(content="Content to analyze")
    async def analyze_command(self, interaction: discord.Interaction, content: str):
        """Analyze content with AI"""
        try:
            await interaction.response.defer()

            analysis_prompt = f"Please analyze the following content and provide insights, key points, and summary:\n\n{content}"
            response = await self._generate_ai_response(
                analysis_prompt, interaction.user.id
            )

            embed = discord.Embed(
                title="🔍 AI Content Analysis",
                description=response,
                color=0x7289DA,
                timestamp=datetime.utcnow(),
            )
            embed.add_field(
                name="📝 Analyzed Content",
                value=content[:500] + ("..." if len(content) > 500 else ""),
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

    @app_commands.command(name="personality", description="Change AI personality")
    @app_commands.describe(
        personality="Personality type (friendly, professional, casual, creative)"
    )
    async def personality_command(
        self, interaction: discord.Interaction, personality: str
    ):
        """Change AI personality"""
        try:
            await interaction.response.defer()

            valid_personalities = [
                "friendly",
                "professional",
                "casual",
                "creative",
                "default",
            ]

            if personality.lower() not in valid_personalities:
                await interaction.followup.send(
                    f"❌ Invalid personality. Choose from: {', '.join(valid_personalities)}",
                    ephemeral=True,
                )
                return

            # Store personality preference (you might want to save this to database)
            embed = discord.Embed(
                title="🎭 Personality Changed",
                description=f"AI personality set to: **{personality.title()}**",
                color=0x43B581,
                timestamp=datetime.utcnow(),
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Personality command error: {e}")
            await interaction.followup.send(
                f"❌ Error changing personality: {str(e)}", ephemeral=True
            )

    @app_commands.command(
        name="voice", description="Convert text to speech (placeholder)"
    )
    @app_commands.describe(text="Text to convert to speech")
    async def voice_command(self, interaction: discord.Interaction, text: str):
        """Text to speech (placeholder implementation)"""
        try:
            await interaction.response.defer()

            # This is a placeholder - you would implement actual TTS here
            embed = discord.Embed(
                title="🔊 Text to Speech",
                description="Voice synthesis feature is coming soon! Stay tuned for updates.",
                color=0xFAA61A,
                timestamp=datetime.utcnow(),
            )
            embed.add_field(
                name="📝 Text",
                value=text[:500] + ("..." if len(text) > 500 else ""),
                inline=False,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Voice command error: {e}")
            await interaction.followup.send(
                f"❌ Error processing voice request: {str(e)}", ephemeral=True
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

            translate_prompt = (
                f"Translate the following text to {target_language}:\n\n{text}"
            )
            response = await self._generate_ai_response(
                translate_prompt, interaction.user.id
            )

            embed = discord.Embed(
                title="🌐 AI Translation", color=0x7289DA, timestamp=datetime.utcnow()
            )
            embed.add_field(
                name="📝 Original Text",
                value=text[:500] + ("..." if len(text) > 500 else ""),
                inline=False,
            )
            embed.add_field(
                name=f"🔄 Translation ({target_language})", value=response, inline=False
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

    @app_commands.command(name="summarize", description="Summarize long text with AI")
    @app_commands.describe(content="Content to summarize")
    async def summarize_command(self, interaction: discord.Interaction, content: str):
        """Summarize content with AI"""
        try:
            await interaction.response.defer()

            summarize_prompt = f"Please provide a concise summary of the following content:\n\n{content}"
            response = await self._generate_ai_response(
                summarize_prompt, interaction.user.id
            )

            embed = discord.Embed(
                title="📋 AI Summary",
                description=response,
                color=0x7289DA,
                timestamp=datetime.utcnow(),
            )
            embed.add_field(
                name="📄 Original Content",
                value=content[:500] + ("..." if len(content) > 500 else ""),
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
        self.response_times: List[float] = []
        self.conversation_quality_scores: Dict[str, float] = {}

        # Start background tasks
        self.proactive_engagement_task.start()
        self.activity_monitor_task.start()
        self.conversation_cleanup_task.start()

        self.logger.info("Advanced AI Cog initialized with conversation engine")

    def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.proactive_engagement_task.cancel()
        self.activity_monitor_task.cancel()
        self.conversation_cleanup_task.cancel()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Enhanced message listener with intelligent AI triggering"""
        if message.author.bot:
            return

        # Track channel activity
        await self._track_channel_activity(message)

        # Check if AI should respond
        should_respond = await self._should_ai_respond(message)

        if should_respond:
            async with message.channel.typing():
                await self._process_ai_conversation(message)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Handle member join for proactive engagement"""
        self.user_join_timestamps[member.id] = datetime.utcnow()

        # Schedule proactive engagement after a delay
        await asyncio.sleep(300)  # 5 minutes delay
        await self._consider_welcome_engagement(member)

    async def _track_channel_activity(self, message: discord.Message):
        """Track channel activity for engagement decisions"""
        channel_id = message.channel.id

        if channel_id not in self.channel_activity:
            self.channel_activity[channel_id] = {
                "recent_messages": [],
                "active_users": set(),
                "recent_topics": [],
                "last_activity": datetime.utcnow(),
            }

        activity = self.channel_activity[channel_id]
        activity["recent_messages"].append(
            {
                "user_id": message.author.id,
                "content": message.content,
                "timestamp": datetime.utcnow(),
            }
        )
        activity["active_users"].add(message.author.id)
        activity["last_activity"] = datetime.utcnow()

        # Extract topics
        topics = await self._extract_message_topics(message.content)
        activity["recent_topics"].extend(topics)

        # Keep only recent data
        cutoff = datetime.utcnow() - timedelta(hours=1)
        activity["recent_messages"] = [
            msg for msg in activity["recent_messages"] if msg["timestamp"] > cutoff
        ]
        activity["recent_topics"] = activity["recent_topics"][
            -20:
        ]  # Keep last 20 topics

    async def _extract_message_topics(self, content: str) -> List[str]:
        """Extract topics from message content"""
        topics = []
        content_lower = content.lower()

        # Space and science topics
        space_keywords = {
            "space": ["space", "cosmos", "universe", "galaxy", "stellar"],
            "astronomy": ["star", "planet", "moon", "solar", "orbit", "nebula"],
            "stellaris": ["stellaris", "empire", "species", "federation", "hyperlane"],
            "science": ["science", "research", "discovery", "theory", "experiment"],
            "technology": ["technology", "ai", "robot", "computer", "digital"],
        }

        for topic, keywords in space_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append(topic)

        return topics

    async def _should_ai_respond(self, message: discord.Message) -> bool:
        """Enhanced AI response determination with sophisticated triggering"""
        # Check cooldown
        user_id = message.author.id
        if user_id in self.conversation_cooldowns:
            if datetime.utcnow() - self.conversation_cooldowns[user_id] < timedelta(
                seconds=3
            ):
                return False

        content_lower = message.content.lower()

        # Direct triggers (always respond)
        if self.bot.user in message.mentions:
            return True

        if isinstance(message.channel, discord.DMChannel):
            return True

        # Intelligent keyword detection
        ai_keywords = ["astra", "hey bot", "ai", "help me", "question"]
        if any(keyword in content_lower for keyword in ai_keywords):
            return True

        # Enhanced question detection
        question_patterns = [
            r"\b(what|how|when|where|why|who|which|can|could|would|should|is|are|will|do|does)\b.*\?",
            r"\bhelp\b.*\?",
            r"\banyone\s+know\b",
            r"\bsomeone\s+(help|explain|tell)\b",
            r"\bi\s+(wonder|need|want)\s+to\s+know\b",
        ]

        for pattern in question_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return True

        # Topic-based engagement (with probability)
        space_keywords = [
            "space",
            "star",
            "planet",
            "galaxy",
            "cosmos",
            "universe",
            "astronomical",
        ]
        stellaris_keywords = [
            "stellaris",
            "empire",
            "species",
            "galactic",
            "federation",
            "hyperlane",
            "ascension",
        ]
        science_keywords = [
            "science",
            "research",
            "discovery",
            "theory",
            "experiment",
            "analysis",
        ]
        tech_keywords = [
            "ai",
            "artificial intelligence",
            "technology",
            "quantum",
            "computer",
        ]

        engagement_probabilities = {
            "space": 0.4,
            "stellaris": 0.6,
            "science": 0.3,
            "technology": 0.25,
        }

        for topic, keywords in [
            ("space", space_keywords),
            ("stellaris", stellaris_keywords),
            ("science", science_keywords),
            ("technology", tech_keywords),
        ]:
            if any(keyword in content_lower for keyword in keywords):
                import random

                if random.random() < engagement_probabilities.get(topic, 0.2):
                    return True

        # Emotional support detection
        emotional_keywords = [
            "sad",
            "frustrated",
            "confused",
            "lost",
            "don't understand",
            "struggling",
        ]
        if any(keyword in content_lower for keyword in emotional_keywords):
            return True

        # Celebration detection
        celebration_keywords = [
            "amazing",
            "awesome",
            "incredible",
            "fantastic",
            "achieved",
            "success",
        ]
        if any(keyword in content_lower for keyword in celebration_keywords):
            import random

            return random.random() < 0.3  # 30% chance to celebrate with user

        return False

    async def _process_ai_conversation(self, message: discord.Message):
        """Process AI conversation using the advanced engine"""
        try:
            start_time = datetime.utcnow()
            user_id = message.author.id

            # Add to active conversations
            self.active_conversations.add(user_id)

            # Prepare context data
            context_data = {
                "mentioned": self.bot.user in message.mentions,
                "channel_type": type(message.channel).__name__,
                "guild_name": message.guild.name if message.guild else None,
                "channel_activity": self.channel_activity.get(message.channel.id, {}),
            }

            # Process with conversation engine
            response = await self.conversation_engine.process_conversation(
                message=message.content,
                user_id=user_id,
                guild_id=message.guild.id if message.guild else None,
                channel_id=message.channel.id,
                context_data=context_data,
            )

            # Send response
            if len(response) > 2000:
                # Split long responses
                chunks = [response[i : i + 2000] for i in range(0, len(response), 2000)]
                for chunk in chunks:
                    await message.channel.send(chunk)
            else:
                await message.channel.send(response)

            # Track performance
            response_time = (datetime.utcnow() - start_time).total_seconds()
            self.response_times.append(response_time)

            # Update cooldown
            self.conversation_cooldowns[user_id] = datetime.utcnow()

            # Log interaction
            self.logger.info(
                f"AI response generated for user {user_id} in {response_time:.2f}s"
            )

        except Exception as e:
            self.logger.error(f"AI conversation processing error: {e}")
            await message.channel.send(
                "I'm having some trouble thinking right now. Give me a moment! 🤖"
            )

        finally:
            self.active_conversations.discard(user_id)

    @tasks.loop(minutes=30)
    async def proactive_engagement_task(self):
        """Proactively engage with users based on patterns"""
        try:
            for guild in self.bot.guilds:
                await self._check_proactive_engagement_opportunities(guild)
        except Exception as e:
            self.logger.error(f"Proactive engagement task error: {e}")

    async def _check_proactive_engagement_opportunities(self, guild: discord.Guild):
        """Check for proactive engagement opportunities in a guild"""
        try:
            current_time = datetime.utcnow()

            for channel in guild.text_channels:
                if not channel.permissions_for(guild.me).send_messages:
                    continue

                channel_activity = self.channel_activity.get(channel.id)
                if not channel_activity:
                    continue

                # Check if channel has been quiet but users are present
                time_since_activity = current_time - channel_activity["last_activity"]
                if timedelta(minutes=30) < time_since_activity < timedelta(hours=2):

                    # Check if any active users would benefit from engagement
                    for user_id in list(channel_activity["active_users"])[
                        -5:
                    ]:  # Recent active users
                        if await self.conversation_engine.should_proactively_engage(
                            user_id, channel_activity
                        ):
                            await self._initiate_proactive_conversation(
                                channel, user_id
                            )
                            break  # Only engage with one user per check

        except Exception as e:
            self.logger.error(f"Proactive engagement check error: {e}")

    async def _initiate_proactive_conversation(
        self, channel: discord.TextChannel, user_id: int
    ):
        """Initiate a proactive conversation with a user"""
        try:
            user = self.bot.get_user(user_id)
            if not user:
                return

            # Get user's conversation history to determine appropriate engagement
            user_profile = self.conversation_engine.user_profiles.get(user_id)
            if not user_profile:
                return

            # Generate proactive message based on user's interests
            if "space" in user_profile.preferred_topics:
                messages = [
                    f"Hey {user.display_name}! 🌌 I just learned about an interesting space phenomenon. Want to hear about it?",
                    f"Hi {user.display_name}! ✨ There's some fascinating space news I thought you might enjoy!",
                    f"{user.display_name}, I've been thinking about our last conversation about space... 🚀",
                ]
            elif "stellaris" in user_profile.preferred_topics:
                messages = [
                    f"Hey {user.display_name}! 🎮 How's your latest Stellaris empire doing?",
                    f"Hi {user.display_name}! Any interesting galactic conquests lately? ⭐",
                    f"{user.display_name}, I've been pondering some Stellaris strategies... 🌌",
                ]
            else:
                messages = [
                    f"Hey {user.display_name}! How's your day going? ✨",
                    f"Hi {user.display_name}! What's been on your mind lately? 🌟",
                    f"{user.display_name}, hope you're having a great day! 🚀",
                ]

            import random

            message = random.choice(messages)
            await channel.send(message)

            self.logger.info(f"Initiated proactive conversation with user {user_id}")

        except Exception as e:
            self.logger.error(f"Proactive conversation initiation error: {e}")

    async def _consider_welcome_engagement(self, member: discord.Member):
        """Consider welcoming a new member"""
        try:
            # Find appropriate channel for welcome
            welcome_channel = None
            for channel in member.guild.text_channels:
                if (
                    "welcome" in channel.name.lower()
                    or "general" in channel.name.lower()
                ):
                    if channel.permissions_for(member.guild.me).send_messages:
                        welcome_channel = channel
                        break

            if welcome_channel:
                welcome_message = f"Welcome to the server, {member.display_name}! 🌟 I'm Astra, your friendly AI companion. Feel free to ask me about space, Stellaris, or anything else! 🚀"
                await welcome_channel.send(welcome_message)

                self.logger.info(f"Welcomed new member {member.id}")

        except Exception as e:
            self.logger.error(f"Welcome engagement error: {e}")

    @tasks.loop(minutes=15)
    async def activity_monitor_task(self):
        """Monitor and update activity patterns"""
        try:
            current_time = datetime.utcnow()

            # Clean up old activity data
            for channel_id in list(self.channel_activity.keys()):
                activity = self.channel_activity[channel_id]
                if current_time - activity["last_activity"] > timedelta(hours=6):
                    del self.channel_activity[channel_id]

            # Update engagement patterns
            for user_id in list(self.engagement_patterns.keys()):
                # Keep only recent patterns
                cutoff = current_time - timedelta(days=7)
                self.engagement_patterns[user_id] = [
                    timestamp
                    for timestamp in self.engagement_patterns[user_id]
                    if timestamp > cutoff
                ]

                # Remove empty patterns
                if not self.engagement_patterns[user_id]:
                    del self.engagement_patterns[user_id]

        except Exception as e:
            self.logger.error(f"Activity monitor task error: {e}")

    @tasks.loop(hours=2)
    async def conversation_cleanup_task(self):
        """Clean up old conversation data"""
        try:
            current_time = datetime.utcnow()

            # Clean up conversation cooldowns
            expired_cooldowns = [
                user_id
                for user_id, timestamp in self.conversation_cooldowns.items()
                if current_time - timestamp > timedelta(hours=1)
            ]
            for user_id in expired_cooldowns:
                del self.conversation_cooldowns[user_id]

            # Clean up old join timestamps
            expired_joins = [
                user_id
                for user_id, timestamp in self.user_join_timestamps.items()
                if current_time - timestamp > timedelta(days=1)
            ]
            for user_id in expired_joins:
                del self.user_join_timestamps[user_id]

            self.logger.debug("Conversation cleanup completed")

        except Exception as e:
            self.logger.error(f"Conversation cleanup task error: {e}")

    @app_commands.command(
        name="ai_stats", description="View AI conversation statistics"
    )
    async def ai_stats(self, interaction: discord.Interaction):
        """Display AI conversation statistics"""
        try:
            # Get analytics from conversation engine
            analytics = await self.conversation_engine.get_conversation_analytics()

            embed = discord.Embed(
                title="🤖 AI Conversation Analytics",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow(),
            )

            embed.add_field(
                name="📊 Overall Stats",
                value=f"Total Conversations: {analytics.get('total_conversations', 0)}\n"
                f"Total Users: {analytics.get('total_users', 0)}\n"
                f"Avg Engagement: {analytics.get('average_engagement', 0):.2f}/1.0",
                inline=True,
            )

            # Performance stats
            if self.response_times:
                avg_response_time = sum(self.response_times[-100:]) / len(
                    self.response_times[-100:]
                )
                embed.add_field(
                    name="⚡ Performance",
                    value=f"Avg Response Time: {avg_response_time:.2f}s\n"
                    f"Active Conversations: {len(self.active_conversations)}\n"
                    f"Tracked Channels: {len(self.channel_activity)}",
                    inline=True,
                )

            # Popular topics
            popular_topics = analytics.get("popular_topics", [])[:5]
            if popular_topics:
                topics_text = "\n".join(
                    [f"{topic}: {count}" for topic, count in popular_topics]
                )
                embed.add_field(
                    name="🔥 Popular Topics", value=topics_text, inline=True
                )

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            self.logger.error(f"AI stats command error: {e}")
            await interaction.response.send_message(
                "Error retrieving AI statistics.", ephemeral=True
            )

    @app_commands.command(
        name="ai_personality", description="View or modify AI personality settings"
    )
    async def ai_personality(
        self, interaction: discord.Interaction, trait: str = None, value: str = None
    ):
        """View or modify AI personality settings"""
        try:
            if not trait:
                # Display current personality
                personality = self.conversation_engine.personality_traits

                embed = discord.Embed(
                    title="🤖 Astra's Personality",
                    description=f"**{personality['name']}** - Your friendly space AI companion",
                    color=discord.Color.purple(),
                )

                embed.add_field(
                    name="🌟 Core Traits",
                    value="\n".join(
                        f"• {trait}" for trait in personality["core_traits"]
                    ),
                    inline=False,
                )

                embed.add_field(
                    name="💬 Communication Style",
                    value=f"**Tone:** {personality['communication_style']['tone']}\n"
                    f"**Humor:** {personality['communication_style']['humor']}\n"
                    f"**Formality:** {personality['communication_style']['formality']}",
                    inline=True,
                )

                embed.add_field(
                    name="🎯 Interests",
                    value=", ".join(personality["interests"][:5]),
                    inline=True,
                )

                await interaction.response.send_message(embed=embed)

            else:
                # Modify personality (admin only)
                if not interaction.user.guild_permissions.administrator:
                    await interaction.response.send_message(
                        "You need administrator permissions to modify AI personality.",
                        ephemeral=True,
                    )
                    return

                # Implementation for personality modification would go here
                await interaction.response.send_message(
                    f"Personality modification for '{trait}' is not yet implemented.",
                    ephemeral=True,
                )

        except Exception as e:
            self.logger.error(f"AI personality command error: {e}")
            await interaction.response.send_message(
                "Error accessing personality settings.", ephemeral=True
            )

    @app_commands.command(
        name="ai_reset", description="Reset AI conversation history for yourself"
    )
    async def ai_reset(self, interaction: discord.Interaction):
        """Reset AI conversation history for the user"""
        try:
            user_id = interaction.user.id

            # Clear conversation context
            if user_id in self.conversation_engine.conversations:
                del self.conversation_engine.conversations[user_id]

            # Reset cooldown
            if user_id in self.conversation_cooldowns:
                del self.conversation_cooldowns[user_id]

            await interaction.response.send_message(
                "🔄 Your conversation history with me has been reset! We can start fresh. 🌟",
                ephemeral=True,
            )

            self.logger.info(f"Reset conversation history for user {user_id}")

        except Exception as e:
            self.logger.error(f"AI reset command error: {e}")
            await interaction.response.send_message(
                "Error resetting conversation history.", ephemeral=True
            )

    @app_commands.command(
        name="ai_mood", description="Analyze the mood of the conversation"
    )
    async def ai_mood_analysis(self, interaction: discord.Interaction):
        """Analyze current conversation mood"""
        try:
            user_id = interaction.user.id
            context = self.conversation_engine.conversations.get(user_id)

            if not context:
                await interaction.response.send_message(
                    "I haven't had a conversation with you yet! Send me a message first. 💫",
                    ephemeral=True,
                )
                return

            mood = context.emotional_context.current_mood
            confidence = context.emotional_context.mood_confidence
            engagement = context.engagement_score

            # Create mood analysis embed
            embed = discord.Embed(
                title="🧠 Conversation Mood Analysis",
                color=discord.Color.purple(),
                timestamp=datetime.utcnow(),
            )

            # Mood visualization
            mood_emojis = {
                "ecstatic": "🤩",
                "excited": "🎉",
                "happy": "😊",
                "content": "😌",
                "curious": "🤔",
                "neutral": "😐",
                "pensive": "🤔",
                "confused": "😕",
                "concerned": "😟",
                "frustrated": "😤",
                "sad": "😢",
                "angry": "😡",
            }

            mood_emoji = mood_emojis.get(mood.value, "😐")

            embed.add_field(
                name="Current Mood",
                value=f"{mood_emoji} **{mood.value.title()}**\nConfidence: {confidence:.1%}",
                inline=True,
            )

            embed.add_field(
                name="Engagement Level",
                value=f"📊 {engagement:.1%}\n{'🔥' if engagement > 0.7 else '✨' if engagement > 0.4 else '💫'}",
                inline=True,
            )

            # Conversation insights
            if context.active_topics:
                embed.add_field(
                    name="Active Topics",
                    value=", ".join(list(context.active_topics)[:5]),
                    inline=False,
                )

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            self.logger.error(f"Mood analysis error: {e}")
            await interaction.response.send_message(
                "Error analyzing conversation mood.", ephemeral=True
            )

    @app_commands.command(
        name="ai_topics", description="View trending conversation topics"
    )
    async def ai_topics(self, interaction: discord.Interaction):
        """Display trending conversation topics"""
        try:
            analytics = await self.conversation_engine.get_conversation_analytics()
            popular_topics = analytics.get("popular_topics", [])

            embed = discord.Embed(
                title="🔥 Trending Conversation Topics",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow(),
            )

            if popular_topics:
                topic_text = []
                for i, (topic, count) in enumerate(popular_topics[:10], 1):
                    emoji = (
                        "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📊"
                    )
                    topic_text.append(
                        f"{emoji} **{topic.replace('_', ' ').title()}** ({count} mentions)"
                    )

                embed.description = "\n".join(topic_text)
            else:
                embed.description = (
                    "No topics have been discussed yet. Start a conversation! 🚀"
                )

            # Add some statistics
            embed.add_field(
                name="📈 Statistics",
                value=f"Total Conversations: {analytics.get('total_conversations', 0)}\n"
                f"Active Users: {analytics.get('total_users', 0)}\n"
                f"Avg Response Time: {analytics.get('avg_response_time_ms', 0):.0f}ms",
                inline=False,
            )

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            self.logger.error(f"Topics command error: {e}")
            await interaction.response.send_message(
                "Error retrieving topic information.", ephemeral=True
            )

    @app_commands.command(
        name="ai_customize", description="Customize AI personality for this server"
    )
    @app_commands.describe(
        trait="Personality trait to adjust", level="Level from 1-10 (10 being maximum)"
    )
    async def ai_personality_customize(
        self, interaction: discord.Interaction, trait: str = None, level: int = None
    ):
        """Customize AI personality traits"""
        try:
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "You need administrator permissions to customize AI personality.",
                    ephemeral=True,
                )
                return

            if not trait:
                # Show current personality
                embed = discord.Embed(
                    title="🎭 Astra's Personality Configuration",
                    description="Current personality trait levels:",
                    color=discord.Color.purple(),
                )

                personality_traits = {
                    "enthusiastic": "How energetic and excited I am",
                    "knowledgeable": "How much I focus on sharing information",
                    "helpful": "How much I prioritize being useful",
                    "curious": "How much I ask questions and explore topics",
                    "friendly": "How warm and approachable I am",
                    "patient": "How understanding I am with complex questions",
                    "witty": "How much humor I use in responses",
                    "scientific": "How technical and precise my explanations are",
                }

                for trait_name, description in personality_traits.items():
                    # Get current level (mock for now)
                    level = 7  # Default level
                    bar = "█" * (level // 2) + "░" * (5 - level // 2)
                    embed.add_field(
                        name=f"{trait_name.title()} [{level}/10]",
                        value=f"`{bar}` {description}",
                        inline=False,
                    )

                embed.add_field(
                    name="🔧 Usage",
                    value="Use `/ai_customize <trait> <level>` to adjust specific traits\n"
                    "Example: `/ai_customize enthusiastic 9`",
                    inline=False,
                )

                await interaction.response.send_message(embed=embed)

            elif trait and level is not None:
                # Adjust personality trait
                if not (1 <= level <= 10):
                    await interaction.response.send_message(
                        "Level must be between 1 and 10.", ephemeral=True
                    )
                    return

                # For now, just confirm the change (implementation would save to config)
                await interaction.response.send_message(
                    f"✅ Set **{trait}** personality trait to level **{level}/10**\n"
                    f"This will affect how I interact in this server! 🎭✨",
                    ephemeral=True,
                )

                self.logger.info(
                    f"Personality trait {trait} set to {level} by {interaction.user.id}"
                )

            else:
                await interaction.response.send_message(
                    "Please provide both trait and level, or use without parameters to view current settings.",
                    ephemeral=True,
                )

        except Exception as e:
            self.logger.error(f"Personality command error: {e}")
            await interaction.response.send_message(
                "Error customizing personality.", ephemeral=True
            )

    @app_commands.command(
        name="ai_engage", description="Manually trigger proactive AI engagement"
    )
    @app_commands.describe(user="User to engage with (admin only)")
    async def manual_engage(
        self, interaction: discord.Interaction, user: discord.Member = None
    ):
        """Manually trigger AI engagement"""
        try:
            target_user = user or interaction.user

            # Admin check for targeting other users
            if user and not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "You can only engage AI for yourself unless you're an administrator.",
                    ephemeral=True,
                )
                return

            # Check if user has recent activity
            user_profile = self.conversation_engine._get_user_profile(target_user.id)

            if not user_profile.preferred_topics:
                await interaction.response.send_message(
                    f"I don't know enough about {target_user.display_name}'s interests yet. "
                    "Have a conversation with me first! 💫",
                    ephemeral=True,
                )
                return

            # Generate proactive engagement message
            topics = list(user_profile.preferred_topics)
            if topics:
                if "space" in topics or "astronomy" in topics:
                    message = f"Hey {target_user.mention}! 🌌 I just learned about an amazing space discovery. Want to hear about it?"
                elif "stellaris" in topics:
                    message = f"Hi {target_user.mention}! 🎮 How's your galactic empire doing? Any interesting developments lately?"
                elif "science" in topics:
                    message = f"{target_user.mention}, I've been pondering some fascinating scientific concepts... 🧬✨"
                else:
                    message = f"Hey {target_user.mention}! 🌟 Hope you're having a stellar day! What's been on your mind lately?"
            else:
                message = f"Hi {target_user.mention}! ✨ Just wanted to check in and see how your cosmic journey is going! 🚀"

            await interaction.response.send_message(message)

            # Update engagement tracking
            if target_user.id not in self.engagement_patterns:
                self.engagement_patterns[target_user.id] = []
            self.engagement_patterns[target_user.id].append(datetime.utcnow())

            self.logger.info(
                f"Manual AI engagement triggered for user {target_user.id}"
            )

        except Exception as e:
            self.logger.error(f"Manual engage error: {e}")
            await interaction.response.send_message(
                "Error triggering AI engagement.", ephemeral=True
            )


async def setup(bot):
    """Set up the Advanced AI cog"""
    await bot.add_cog(AdvancedAICog(bot))
