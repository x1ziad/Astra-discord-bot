"""
Advanced AI Cog for Astra Bot
Implements modern AI features with GitHub Models and OpenAI integration
"""

import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
import logging
import random
import io
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
import os

# Import the new consolidated AI engine and proactive systems
try:
    from ai.consolidated_ai_engine import ConsolidatedAIEngine
    from ai.user_profiling import user_profile_manager, UserProfileManager
    from ai.proactive_engagement import proactive_engagement, ProactiveEngagement
    from config.enhanced_config import EnhancedConfigManager

    AI_ENGINE_AVAILABLE = True
    logger = logging.getLogger("astra.advanced_ai")
    logger.info("Consolidated AI Engine and Proactive Systems successfully imported")
except ImportError as e:
    AI_ENGINE_AVAILABLE = False
    logger = logging.getLogger("astra.advanced_ai")
    logger.error(f"Failed to import AI systems: {e}")

# Import optimized AI engine for enhanced performance
try:
    from ai.optimized_ai_engine import OptimizedAIEngine, get_optimized_engine

    OPTIMIZED_AI_AVAILABLE = True
    logger.info("✅ Optimized AI Engine imported successfully")
except ImportError as e:
    OPTIMIZED_AI_AVAILABLE = False
    logger.warning(f"❌ Optimized AI Engine not available: {e}")

# Backward compatibility imports
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

        # User conversations tracking (for compatibility)
        self.user_conversations = self.conversation_history

        # Performance tracking
        self.api_calls_made = 0
        self.successful_responses = 0
        self.start_time = datetime.now(timezone.utc)
        self.response_times: List[float] = []

        # Engagement tracking
        self.engagement_patterns: Dict[int, List[datetime]] = {}
        self.user_join_timestamps: Dict[int, datetime] = {}

        # Enhanced tracking for proactive features
        self.last_status_update = datetime.now(timezone.utc)
        self.server_activity_levels: Dict[int, str] = {}  # guild_id -> activity level
        self.interesting_topics: List[str] = []  # Track current interesting topics
        self.mentioned_users: Set[int] = set()  # Track recently mentioned users

        # Start background tasks
        self.proactive_engagement_task.start()
        self.activity_monitor_task.start()
        self.conversation_cleanup_task.start()
        self.dynamic_status_task.start()  # New dynamic status task

    def _setup_ai_client(self):
        """Setup the new consolidated AI engine"""
        try:
            # Try optimized engine first
            if OPTIMIZED_AI_AVAILABLE:
                try:
                    self.ai_client = get_optimized_engine()
                    self.logger.info("✅ Optimized AI Engine initialized successfully")

                    # Store basic configuration for command compatibility
                    config = EnhancedConfigManager()
                    self.ai_model = config.get_setting(
                        "AI_MODEL", "deepseek/deepseek-r1:nitro"
                    )
                    self.max_tokens = int(config.get_setting("AI_MAX_TOKENS", "1000"))
                    self.temperature = float(
                        config.get_setting("AI_TEMPERATURE", "0.7")
                    )
                    return
                except Exception as e:
                    self.logger.warning(
                        f"Optimized engine failed, falling back to consolidated: {e}"
                    )

            # Fallback to consolidated engine
            if AI_ENGINE_AVAILABLE:
                # Initialize the consolidated AI engine
                self.ai_client = ConsolidatedAIEngine()
                self.logger.info("✅ Consolidated AI Engine initialized successfully")

                # Store basic configuration for command compatibility
                config = EnhancedConfigManager()
                self.ai_model = config.get_setting(
                    "AI_MODEL", "deepseek/deepseek-r1:nitro"
                )
                self.max_tokens = int(config.get_setting("AI_MAX_TOKENS", "1000"))
                self.temperature = float(config.get_setting("AI_TEMPERATURE", "0.7"))

            else:
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
        engagement_type: str = "casual_engagement",
    ) -> str:
        """Generate AI response using the consolidated AI engine with personalization"""
        try:
            if not self.ai_client:
                return (
                    "❌ AI service is not configured. Please check the configuration."
                )

            # Get user communication preferences for personalization
            user_profile = {}
            if user_id:
                try:
                    profile = await user_profile_manager.get_user_profile(
                        user_id, username
                    )
                    user_profile = await user_profile_manager.get_personalized_context(
                        user_id
                    )

                    # Analyze the current message for learning
                    await user_profile_manager.analyze_message(
                        user_id, prompt, username
                    )

                except Exception as e:
                    logger.warning(f"Failed to get user profile for {user_id}: {e}")

            # Prepare enhanced context data for the AI engine
            context_data = {
                "channel_type": "discord",
                "conversation_history": (
                    self.conversation_history.get(user_id, []) if user_id else []
                ),
                "user_profile": user_profile,
                "engagement_type": engagement_type,
                "personalization": {
                    "should_personalize": bool(user_profile),
                    "response_style": self._determine_response_style(
                        user_profile, engagement_type
                    ),
                    "topic_focus": self._determine_topic_focus(user_profile, prompt),
                },
            }

            # Generate response using the consolidated engine with proper parameters
            response = await self.ai_client.process_conversation(
                prompt,
                user_id,
                guild_id=guild_id,
                channel_id=channel_id,
                context_data=context_data,
            )

            # Update conversation history
            if user_id:
                if user_id not in self.conversation_history:
                    self.conversation_history[user_id] = []

                # Add user message and AI response to history
                self.conversation_history[user_id].append(
                    {"role": "user", "content": prompt}
                )
                self.conversation_history[user_id].append(
                    {"role": "assistant", "content": response}
                )

                # Keep only last 10 messages
                if len(self.conversation_history[user_id]) > self.max_history_length:
                    self.conversation_history[user_id] = self.conversation_history[
                        user_id
                    ][-self.max_history_length :]

            return response

        except Exception as e:
            self.logger.error(f"AI response generation error: {e}")
            return f"❌ Error generating AI response: {str(e)}"

        except Exception as e:
            self.logger.error(f"AI response generation error: {e}")
            return f"❌ Error generating AI response: {str(e)}"

    def _determine_response_style(
        self, user_profile: Dict, engagement_type: str
    ) -> str:
        """Determine appropriate response style based on user communication preferences"""
        if not user_profile or "communication_preferences" not in user_profile:
            return "balanced"

        prefs = user_profile["communication_preferences"]

        # Get base communication style
        base_style = prefs.get("style", "balanced")

        # Adjust based on engagement type for natural response flow
        if engagement_type in ["provide_support", "offer_help"]:
            # Be supportive but maintain user's preferred style
            return (
                base_style + "_supportive" if base_style != "balanced" else "supportive"
            )
        elif engagement_type == "answer_question":
            # Respect user's detail preference
            detail_pref = prefs.get("detail_level", "balanced")
            if detail_pref == "detailed":
                return "detailed_" + base_style
            elif detail_pref == "concise":
                return "concise_" + base_style
            else:
                return base_style

        return base_style

    def _determine_topic_focus(self, user_profile: Dict, prompt: str) -> List[str]:
        """Determine topics to focus on based on user interests and message content"""
        focus_topics = []

        if user_profile and "interests" in user_profile:
            favorite_topics = user_profile["interests"].get("topics", [])

            # Check if any favorite topics are mentioned in the prompt
            prompt_lower = prompt.lower()
            for topic in favorite_topics:
                if topic in prompt_lower:
                    focus_topics.append(topic)

        # Add general topic detection
        prompt_lower = prompt.lower()
        general_topics = {
            "space": ["space", "universe", "cosmos", "galaxy", "star", "planet"],
            "technology": ["tech", "ai", "computer", "software", "programming"],
            "science": ["science", "research", "experiment", "theory"],
            "gaming": ["game", "gaming", "play", "stellaris"],
        }

        for topic, keywords in general_topics.items():
            if any(keyword in prompt_lower for keyword in keywords):
                if topic not in focus_topics:
                    focus_topics.append(topic)

        return focus_topics[:3]  # Limit to top 3 topics

    # Old methods removed - using consolidated AI engine now

    @app_commands.command(name="chat", description="Chat with Astra AI")
    @app_commands.describe(message="Your message to the AI")
    async def chat_command(self, interaction: discord.Interaction, message: str):
        """Chat with AI assistant"""
        try:
            await interaction.response.defer()

            # Generate AI response with personalization
            response = await self._generate_ai_response(
                message,
                interaction.user.id,
                guild_id=interaction.guild.id if interaction.guild else None,
                channel_id=interaction.channel.id,
                username=str(interaction.user),
                engagement_type="direct_command",
            )

            # Create embed
            embed = discord.Embed(
                title="🤖 Astra AI Chat",
                description=response,
                color=0x7289DA,
                timestamp=datetime.now(timezone.utc),
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
                timestamp=datetime.now(timezone.utc),
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

    @app_commands.command(
        name="communication_style", description="Set your preferred communication style"
    )
    @app_commands.describe(
        style="Communication style (detailed, concise, casual, formal)"
    )
    async def communication_style_command(
        self, interaction: discord.Interaction, style: str
    ):
        """Set communication style preference"""
        try:
            await interaction.response.defer()

            valid_styles = [
                "detailed",
                "concise",
                "casual",
                "formal",
                "balanced",
            ]

            if style.lower() not in valid_styles:
                await interaction.followup.send(
                    f"❌ Invalid style. Choose from: {', '.join(valid_styles)}",
                    ephemeral=True,
                )
                return

            # Store communication preference - this will be used by the flow engine
            user_id = str(interaction.user.id)
            # TODO: Store this in user profile or database

            embed = discord.Embed(
                title="💬 Communication Style Updated",
                description=f"I'll adapt my responses to be more **{style.lower()}** based on your preference.",
                color=0x43B581,
                timestamp=datetime.now(timezone.utc),
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
                timestamp=datetime.now(timezone.utc),
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
                title="🌐 AI Translation",
                color=0x7289DA,
                timestamp=datetime.now(timezone.utc),
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
                timestamp=datetime.now(timezone.utc),
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

        self.logger.info("Advanced AI Cog initialized with GitHub Models integration")

    def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.proactive_engagement_task.cancel()
        self.activity_monitor_task.cancel()
        self.conversation_cleanup_task.cancel()
        self.dynamic_status_task.cancel()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Enhanced message listener with intelligent AI triggering, chat understanding, and proactive engagement"""
        if message.author.bot:
            return

        # Enhanced chat understanding and context analysis
        await self._analyze_message_context(message)

        # Track channel activity with enhanced metrics
        await self._track_channel_activity(message)

        # Extract and track interesting topics from conversation
        await self._extract_conversation_topics(message)

        # Update server activity levels for dynamic status
        await self._update_server_activity_level(message)

        # Check if AI should respond (now returns tuple)
        should_respond, engagement_reason = await self._should_ai_respond(message)

        if should_respond:
            async with message.channel.typing():
                # Determine engagement type for personalized response
                engagement_type = "casual_engagement"

                if engagement_reason != "fallback_basic":
                    try:
                        engagement_type = (
                            await proactive_engagement.generate_engagement_type(
                                message.content,
                                engagement_reason,
                                await user_profile_manager.get_personalized_context(
                                    message.author.id
                                ),
                            )
                        )
                    except Exception as e:
                        logger.warning(f"Failed to generate engagement type: {e}")

                # Process AI conversation with enhanced context
                await self._process_ai_conversation(message, engagement_type)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Handle member join for proactive engagement"""
        self.user_join_timestamps[member.id] = datetime.now(timezone.utc)

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
                "last_activity": datetime.now(timezone.utc),
            }

        activity = self.channel_activity[channel_id]
        activity["recent_messages"].append(
            {
                "user_id": message.author.id,
                "content": message.content,
                "timestamp": datetime.now(timezone.utc),
            }
        )
        activity["active_users"].add(message.author.id)
        activity["last_activity"] = datetime.now(timezone.utc)

        # Extract topics
        topics = await self._extract_message_topics(message.content)
        activity["recent_topics"].extend(topics)

        # Keep only recent data
        cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
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

    async def _should_ai_respond(self, message: discord.Message) -> Tuple[bool, str]:
        """Enhanced AI response determination with proactive engagement system"""
        user_id = message.author.id

        # Check basic cooldown to prevent spam
        if user_id in self.conversation_cooldowns:
            if datetime.now(timezone.utc) - self.conversation_cooldowns[
                user_id
            ] < timedelta(seconds=3):
                return False, "user_cooldown"

        content_lower = message.content.lower()

        # Always respond to direct mentions and DMs
        if self.bot.user in message.mentions:
            return True, "direct_mention"

        if isinstance(message.channel, discord.DMChannel):
            return True, "direct_message"

        # Always respond to explicit AI calls
        ai_keywords = ["astra", "hey bot", "ai help", "hey ai"]
        if any(keyword in content_lower for keyword in ai_keywords):
            return True, "explicit_ai_call"

        # Get user profile for personalized engagement
        user_profile = {}
        try:
            profile = await user_profile_manager.get_user_profile(
                user_id, str(message.author)
            )
            user_profile = await user_profile_manager.get_personalized_context(user_id)
        except Exception as e:
            logger.warning(f"Failed to get user profile for engagement: {e}")

        # Use proactive engagement system
        try:
            should_engage, reason = (
                await proactive_engagement.should_engage_proactively(
                    message.content,
                    user_id,
                    message.channel.id,
                    message.guild.id if message.guild else None,
                    user_profile,
                )
            )

            if should_engage:
                logger.info(
                    f"Proactive engagement triggered for user {user_id}: {reason}"
                )
                return True, reason
            else:
                return False, reason

        except Exception as e:
            logger.error(f"Proactive engagement error: {e}")
            # Fallback to basic engagement
            return await self._basic_engagement_check(message), "fallback_basic"

    async def _basic_engagement_check(self, message: discord.Message) -> bool:
        """Basic engagement check as fallback"""
        content_lower = message.content.lower()

        # Question detection
        if "?" in message.content:
            return True

        # Help seeking
        help_keywords = ["help", "how do", "what is", "explain", "confused"]
        if any(keyword in content_lower for keyword in help_keywords):
            return True

        # Topic keywords with probability
        topic_keywords = ["space", "stellaris", "science", "technology", "ai"]
        if any(keyword in content_lower for keyword in topic_keywords):
            import random

            return random.random() < 0.3  # 30% chance

        return False
        """Enhanced AI response determination with sophisticated triggering"""
        # Check cooldown
        user_id = message.author.id
        if user_id in self.conversation_cooldowns:
            if datetime.now(timezone.utc) - self.conversation_cooldowns[
                user_id
            ] < timedelta(seconds=3):
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

    async def _process_ai_conversation(
        self, message: discord.Message, engagement_type: str = "casual_engagement"
    ):
        """Process AI conversation with enhanced features: user mentioning and smart responses"""
        try:
            start_time = datetime.now(timezone.utc)
            user_id = message.author.id
            username = str(message.author)

            # Add to active conversations
            self.active_conversations.add(user_id)


            # Process with AI client using enhanced personalization
            response = await self._generate_ai_response(
                message.content,
                user_id,
                guild_id=message.guild.id if message.guild else None,
                channel_id=message.channel.id,
                username=username,
                engagement_type=engagement_type,
            )

            # Enhance response with user mentions if relevant
            enhanced_response = await self._enhance_response_with_mentions(
                message, response
            )

            # Send response with smart formatting
            await self._send_enhanced_response(message.channel, enhanced_response)

            # Track performance
            response_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.response_times.append(response_time)

            # Update cooldown
            self.conversation_cooldowns[user_id] = datetime.now(timezone.utc)

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
            current_time = datetime.now(timezone.utc)

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
                        # Simple proactive engagement based on activity
                        if len(channel_activity[user_id]) > 5:  # User has been active
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
            # Simple proactive engagement without complex user profiles
            # Generate proactive message
            messages = [
                f"Hey {user.display_name}! 🌌 I just learned about an interesting space phenomenon. Want to hear about it?",
                f"Hi {user.display_name}! ✨ There's some fascinating space news I thought you might enjoy!",
                f"{user.display_name}, I've been thinking about our last conversation about space... 🚀",
                f"Hey {user.display_name}! 🎮 How's your day going?",
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

    # === ENHANCED CHAT UNDERSTANDING AND PROACTIVE FEATURES ===

    async def _analyze_message_context(self, message: discord.Message):
        """Analyze message context for better understanding and user mentioning"""
        try:
            content = message.content.lower()

            # Detect if users are being discussed (for potential mentioning)
            user_references = []

            # Look for user references in message
            words = content.split()
            user_indicating_words = [
                "user",
                "person",
                "someone",
                "anybody",
                "player",
                "member",
            ]

            # Check if message refers to users in a way that might warrant mentioning
            if any(
                word in content
                for word in ["help", "question", "ask", "know", "expert"]
            ):
                # Find relevant users based on message topics
                if message.guild:
                    relevant_users = await self._find_relevant_users(message)
                    if relevant_users:
                        user_references.extend(relevant_users)

            # Track users who might be relevant to mention
            if user_references:
                self.mentioned_users.update(user_references)

        except Exception as e:
            self.logger.error(f"Message context analysis error: {e}")

    async def _find_relevant_users(self, message: discord.Message) -> List[int]:
        """Find users relevant to the message topic who might be worth mentioning"""
        try:
            relevant_users = []
            content = message.content.lower()

            # Topic-based user expertise mapping
            topic_experts = {
                "stellaris": [],  # Will be populated with active stellaris players
                "space": [],  # Space enthusiasts
                "ai": [],  # AI/tech interested users
                "gaming": [],  # Gaming enthusiasts
                "science": [],  # Science interested users
            }

            # Look for recent active users in similar conversations
            if message.guild:
                for channel in message.guild.text_channels:
                    channel_activity = self.channel_activity.get(channel.id)
                    if channel_activity:
                        # Get users who recently talked about similar topics
                        for topic in channel_activity.get("recent_topics", []):
                            if any(keyword in content for keyword in topic.split()):
                                relevant_users.extend(
                                    list(channel_activity.get("active_users", set()))
                                )

            # Return top 2-3 most relevant users (avoid spam)
            return list(set(relevant_users))[:3]

        except Exception as e:
            self.logger.error(f"Relevant user finding error: {e}")
            return []

    async def _extract_conversation_topics(self, message: discord.Message):
        """Extract and track interesting topics from ongoing conversations"""
        try:
            content = message.content.lower()

            # Enhanced topic detection
            topics = await self._extract_message_topics(content)

            # Add to global interesting topics tracker
            for topic in topics:
                if topic not in self.interesting_topics:
                    self.interesting_topics.append(topic)

            # Keep only recent interesting topics (last 20)
            self.interesting_topics = self.interesting_topics[-20:]

        except Exception as e:
            self.logger.error(f"Topic extraction error: {e}")

    async def _update_server_activity_level(self, message: discord.Message):
        """Update server activity level for dynamic status updates"""
        try:
            if not message.guild:
                return

            guild_id = message.guild.id
            current_time = datetime.now(timezone.utc)

            # Count recent messages in the guild
            recent_messages = 0
            for channel_id, activity in self.channel_activity.items():
                if any(ch.id == channel_id for ch in message.guild.text_channels):
                    if current_time - activity.get(
                        "last_activity", current_time
                    ) < timedelta(minutes=10):
                        recent_messages += len(activity.get("recent_messages", []))

            # Determine activity level
            if recent_messages >= 20:
                activity_level = "very_active"
            elif recent_messages >= 10:
                activity_level = "active"
            elif recent_messages >= 3:
                activity_level = "moderate"
            else:
                activity_level = "quiet"

            self.server_activity_levels[guild_id] = activity_level

        except Exception as e:
            self.logger.error(f"Server activity update error: {e}")

    @tasks.loop(minutes=5)
    async def dynamic_status_task(self):
        """Dynamically update bot status based on activity and interesting topics"""
        try:
            current_time = datetime.now(timezone.utc)

            # Only update status every 5-15 minutes to avoid spam
            if current_time - self.last_status_update < timedelta(minutes=5):
                return

            # Determine status based on activity and topics
            status_messages = []

            # Activity-based statuses
            total_servers = len(self.bot.guilds)
            active_servers = sum(
                1
                for level in self.server_activity_levels.values()
                if level in ["active", "very_active"]
            )

            if active_servers > 0:
                status_messages.extend(
                    [
                        f"🚀 Exploring {active_servers} active galaxies",
                        f"🌟 Engaging with {active_servers} communities",
                        f"⚡ Active in {active_servers} servers",
                    ]
                )

            # Topic-based statuses
            if self.interesting_topics:
                recent_topics = self.interesting_topics[-3:]  # Last 3 topics
                if "stellaris" in recent_topics:
                    status_messages.append("🌌 Discussing galactic empires")
                if "space" in recent_topics:
                    status_messages.append("🛸 Exploring the cosmos")
                if "ai" in recent_topics:
                    status_messages.append("🤖 Pondering artificial intelligence")
                if "science" in recent_topics:
                    status_messages.append("🔬 Analyzing scientific concepts")

            # Default statuses when no specific activity
            default_statuses = [
                "🌟 Ready to explore the universe",
                "🚀 Waiting for cosmic conversations",
                "🌌 Observing the digital galaxy",
                "💫 Dreaming of distant stars",
                f"🌍 Watching over {total_servers} servers",
            ]

            # Choose status
            if status_messages:
                status = random.choice(status_messages)
            else:
                status = random.choice(default_statuses)

            # Update bot status
            activity = discord.Activity(type=discord.ActivityType.watching, name=status)
            await self.bot.change_presence(activity=activity)

            self.last_status_update = current_time
            self.logger.info(f"Updated bot status to: {status}")

        except Exception as e:
            self.logger.error(f"Dynamic status update error: {e}")


    async def _enhance_response_with_mentions(
        self, message: discord.Message, response: str
    ) -> str:
        """Enhance AI response with relevant user mentions when appropriate"""
        try:
            if not message.guild:
                return response

            # Check if response suggests getting help or mentions expertise
            help_indicators = [
                "expert",
                "ask someone",
                "check with",
                "maybe.*knows",
                "experienced.*with",
            ]

            should_mention = any(
                re.search(pattern, response.lower()) for pattern in help_indicators
            )

            if should_mention and len(self.mentioned_users) > 0:
                # Find relevant guild members from mentioned_users
                relevant_members = []
                for user_id in list(self.mentioned_users)[:3]:  # Max 3 mentions
                    member = message.guild.get_member(user_id)
                    if member and member != message.author and not member.bot:
                        relevant_members.append(member)

                if relevant_members:
                    mentions = " ".join([member.mention for member in relevant_members])
                    response += f"\n\n💡 {mentions} might be able to help with this!"

                    # Clear mentioned users after using them
                    self.mentioned_users.clear()

            return response

        except Exception as e:
            self.logger.error(f"Response enhancement error: {e}")
            return response

    async def _send_enhanced_response(
        self, channel: discord.TextChannel, response: str
    ):
        """Send response with smart formatting and splitting"""
        try:
            if len(response) > 2000:
                # Smart splitting at sentence boundaries
                chunks = []
                current_chunk = ""

                sentences = re.split(r"(?<=[.!?])\s+", response)

                for sentence in sentences:
                    if (
                        len(current_chunk + sentence) > 1900
                    ):  # Leave room for formatting
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            current_chunk = sentence
                        else:
                            # Single sentence too long, force split
                            chunks.append(sentence[:1900])
                            current_chunk = sentence[1900:]
                    else:
                        current_chunk += sentence + " "

                if current_chunk:
                    chunks.append(current_chunk.strip())

                # Send chunks with small delay
                for i, chunk in enumerate(chunks):
                    if i > 0:
                        await asyncio.sleep(0.5)  # Small delay between chunks
                    await channel.send(chunk)
            else:
                await channel.send(response)

        except Exception as e:
            self.logger.error(f"Enhanced response sending error: {e}")
            # Fallback to simple send
            await channel.send(response[:2000])

    @tasks.loop(minutes=15)
    async def activity_monitor_task(self):
        """Monitor and update activity patterns"""
        try:
            current_time = datetime.now(timezone.utc)

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
            current_time = datetime.now(timezone.utc)

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

    # Note: Redundant AI commands (ai_personality, ai_mood, ai_reset, ai_customize) removed
    # These commands were not adding value and creating maintenance overhead


async def setup(bot):
    await bot.add_cog(AdvancedAICog(bot))
