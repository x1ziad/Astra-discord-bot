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

            # Add adaptive personality context based on topics
            if hasattr(context_data, 'get') and context_data.get("topic_focus"):
                personality_context = self._get_personality_context_for_topic(context_data["topic_focus"])
                context_data["personality_adaptation"] = personality_context
                
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
        # Enhanced topic detection - Balanced across interests
        general_topics = {
            "gaming": ["game", "gaming", "play", "player", "steam", "console", "mobile game", "esports"],
            "entertainment": ["movie", "film", "tv", "series", "music", "song", "anime", "netflix", "youtube"],
            "technology": ["tech", "ai", "computer", "software", "programming", "app", "digital"],
            "lifestyle": ["food", "cooking", "travel", "fitness", "health", "photography", "art"],
            "education": ["learn", "study", "school", "college", "course", "knowledge", "skill"],
            "business": ["work", "job", "career", "business", "company", "project", "startup"],
            "science": ["science", "research", "experiment", "theory", "physics", "chemistry"],
            "space": ["space", "universe", "cosmos", "galaxy", "star", "planet", "astronomy"],
            "stellaris": ["stellaris", "empire", "species", "federation", "4x game", "strategy"],
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

        # Skip if this was a command to avoid double processing
        if message.content.startswith(
            tuple(await self.bot._get_dynamic_prefix(self.bot, message))
        ):
            return

        try:
            # Enhanced chat understanding and context analysis
            await self._analyze_message_context(message)

            # Track channel activity with enhanced metrics
            await self._track_channel_activity(message)

            # Extract and track interesting topics from conversation
            await self._extract_conversation_topics(message)

            # Update server activity levels for dynamic status
            await self._update_server_activity_level(message)

            # Initialize context manager for advanced response logic
            try:
                from ai.universal_context_manager import (
                    get_context_manager,
                    initialize_context_manager,
                )

                context_manager = get_context_manager()
                if not context_manager:
                    context_manager = initialize_context_manager(self.bot)
                    self.logger.info(
                        "Universal Context Manager initialized in advanced AI cog"
                    )

                # Use context manager for sophisticated response determination
                if context_manager:
                    message_context = await context_manager.analyze_message(
                        message.content,
                        message.author.id,
                        message.channel.id,
                        message.guild.id if message.guild else None,
                        message.author.display_name,
                    )

                    should_respond, response_reason = (
                        await context_manager.should_respond(
                            message_context,
                            message.channel.id,
                            message.guild.id if message.guild else None,
                        )
                    )

                    if should_respond:
                        self.logger.info(
                            f"Context manager approved response for user {message.author.id}: {response_reason}"
                        )

                        # Get response context
                        response_context = await context_manager.get_response_context(
                            message_context
                        )

                        # Determine engagement type based on context
                        engagement_type = self._map_triggers_to_engagement_type(
                            message_context.response_triggers
                        )

                        # Process AI conversation
                        await self._process_ai_conversation(message, engagement_type)

                        # Mark response as sent
                        await context_manager.mark_response_sent(
                            message_context, message.channel.id
                        )
                    else:
                        self.logger.debug(
                            f"Context manager declined response for user {message.author.id}: {response_reason}"
                        )

                else:
                    # Fallback to basic AI response logic if context manager fails
                    should_respond, engagement_reason = await self._should_ai_respond(
                        message
                    )

                    if should_respond:
                        self.logger.info(
                            f"Basic AI logic approved response for user {message.author.id}: {engagement_reason}"
                        )

                        engagement_type = "casual_engagement"
                        if engagement_reason != "fallback_basic":
                            try:
                                if AI_ENGINE_AVAILABLE:
                                    engagement_type = await proactive_engagement.generate_engagement_type(
                                        message.content,
                                        engagement_reason,
                                        await user_profile_manager.get_personalized_context(
                                            message.author.id
                                        ),
                                    )
                            except Exception as e:
                                self.logger.warning(
                                    f"Failed to generate engagement type: {e}"
                                )

                        # Process AI conversation with enhanced context
                        await self._process_ai_conversation(message, engagement_type)
                    else:
                        self.logger.debug(
                            f"Basic AI logic declined response for user {message.author.id}: {engagement_reason}"
                        )

            except Exception as e:
                self.logger.error(f"Error in context manager logic: {e}")
                # Fallback to basic response logic
                should_respond, engagement_reason = await self._should_ai_respond(
                    message
                )

                if should_respond:
                    await self._process_ai_conversation(message, "casual_engagement")

        except Exception as e:
            self.logger.error(f"Error in message processing: {e}")
            # Don't crash on message processing errors

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

        # Balanced topic detection across different interests
        topic_keywords = {
            "gaming": ["game", "gaming", "play", "player", "steam", "console", "mobile", "esports", "twitch"],
            "entertainment": ["movie", "film", "tv", "series", "music", "song", "album", "anime", "netflix", "youtube", "video"],
            "technology": ["tech", "ai", "computer", "software", "programming", "app", "digital", "internet", "web"],
            "lifestyle": ["food", "cooking", "travel", "fitness", "health", "photography", "art", "fashion", "style"],
            "education": ["learn", "study", "school", "college", "course", "knowledge", "skill", "tutorial", "education"],
            "business": ["work", "job", "career", "business", "company", "project", "startup", "meeting", "office"],
            "social": ["friend", "community", "relationship", "family", "social", "dating", "group", "team"],
            "science": ["science", "research", "experiment", "theory", "physics", "chemistry", "biology", "data"],
            "space": ["space", "cosmos", "universe", "galaxy", "star", "planet", "astronomy", "nasa", "spacex"],
            "stellaris": ["stellaris", "empire", "species", "federation", "hyperlane", "4x", "grand strategy"],
        }

        for topic, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append(topic)

        return topics

    def _map_triggers_to_engagement_type(self, response_triggers):
        """Map response triggers to engagement types"""
        # Convert trigger enums to strings for processing
        trigger_values = []
        for trigger in response_triggers:
            if hasattr(trigger, "value"):
                trigger_values.append(trigger.value)
            else:
                trigger_values.append(str(trigger))

        # Map triggers to engagement types
        if "question_asked" in trigger_values or "help_needed" in trigger_values:
            return "provide_support"
        elif "bot_mentioned" in trigger_values:
            return "direct_response"
        elif "greeting" in trigger_values:
            return "friendly_greeting"
        elif "celebration" in trigger_values:
            return "celebratory_response"
        elif "humor_detected" in trigger_values:
            return "humorous_engagement"
        elif "emotional_support" in trigger_values:
            return "supportive_response"
        elif (
            "conversation_starter" in trigger_values
            or "opinion_sharing" in trigger_values
        ):
            return "conversational_engagement"
        elif "collaborative_discussion" in trigger_values:
            return "collaborative_response"
        elif "story_telling" in trigger_values:
            return "interested_response"
        elif "reaction_worthy" in trigger_values:
            return "reactive_response"
        else:
            return "casual_engagement"

    def _get_personality_context_for_topic(self, topics: List[str]) -> Dict[str, Any]:
        """Get personality context based on detected topics"""
        if not topics:
            return {"personality_mode": "neutral", "tone": "casual", "expertise_level": "general"}
        
        primary_topic = topics[0]
        
        personality_contexts = {
            "gaming": {
                "personality_mode": "enthusiastic_gamer",
                "tone": "excited",
                "expertise_level": "knowledgeable",
                "response_style": "Use gaming terminology, be enthusiastic about achievements, reference game mechanics naturally",
                "emoji_preference": "🎮🕹️🏆⚡🔥",
            },
            "entertainment": {
                "personality_mode": "cultural_enthusiast", 
                "tone": "engaging",
                "expertise_level": "well_informed",
                "response_style": "Be knowledgeable about media, share recommendations, discuss cultural impact",
                "emoji_preference": "🎬🎵📺🎭✨",
            },
            "technology": {
                "personality_mode": "tech_savvy",
                "tone": "informative",
                "expertise_level": "expert",
                "response_style": "Be forward-thinking, explain concepts clearly, focus on practical applications",
                "emoji_preference": "💻🤖⚡🔧💡",
            },
            "lifestyle": {
                "personality_mode": "supportive_friend",
                "tone": "warm",
                "expertise_level": "experienced",
                "response_style": "Be encouraging, share personal tips, focus on well-being and growth",
                "emoji_preference": "🌟💪🌱🎯✨",
            },
            "education": {
                "personality_mode": "helpful_mentor",
                "tone": "patient",
                "expertise_level": "educational",
                "response_style": "Break down concepts, encourage learning, provide step-by-step guidance",
                "emoji_preference": "📚💡🎓🔍📝",
            },
            "business": {
                "personality_mode": "professional_advisor",
                "tone": "professional",
                "expertise_level": "business_savvy",
                "response_style": "Be solution-oriented, focus on practical outcomes, use business terminology",
                "emoji_preference": "💼📈🎯🚀💡",
            },
            "science": {
                "personality_mode": "curious_researcher",
                "tone": "analytical",
                "expertise_level": "scientific",
                "response_style": "Focus on facts, encourage experimentation, explain methodically",
                "emoji_preference": "🔬🧪📊⚗️🔍",
            },
            "space": {
                "personality_mode": "cosmic_explorer",
                "tone": "wonder_filled",
                "expertise_level": "astronomical",
                "response_style": "Express wonder about the cosmos, use expansive language, inspire curiosity",
                "emoji_preference": "🌌🚀⭐🛸🌟",
            },
            "stellaris": {
                "personality_mode": "strategic_advisor",
                "tone": "tactical",
                "expertise_level": "strategic",
                "response_style": "Think strategically, reference empire building, discuss long-term planning",
                "emoji_preference": "🌌⚔️🏛️👑🗺️",
            },
            "social": {
                "personality_mode": "social_connector",
                "tone": "warm",
                "expertise_level": "socially_aware",
                "response_style": "Focus on community building, encourage interaction, be inclusive",
                "emoji_preference": "🤝💭👥🌟💕",
            },
        }
        
        return personality_contexts.get(primary_topic, {
            "personality_mode": "adaptive_neutral",
            "tone": "casual",
            "expertise_level": "general",
            "response_style": "Be natural and conversational, adapt to the user's tone",
            "emoji_preference": "😊💫🌟✨💬",
        })

    async def _should_ai_respond(self, message: discord.Message) -> Tuple[bool, str]:
        """Enhanced AI response determination with proactive engagement system - Fallback method"""
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

        # Enhanced question detection - More responsive
        question_patterns = [
            r"\?",  # Simple question mark
            r"\b(what|how|when|where|why|who|which|can|could|would|should|is|are|will|do|does)\b",
            r"\b(anyone know|somebody know|does anyone|can someone|help with|help me)\b",
            r"\b(confused|lost|stuck|don't understand|need help)\b",
        ]

        for pattern in question_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return True, "question_detected"

        # Enhanced topic-based engagement with balanced probabilities
        topic_keywords_engagement = {
            "gaming": ["game", "gaming", "play", "player", "steam", "console", "esports"],
            "entertainment": ["movie", "film", "tv", "music", "anime", "netflix", "youtube"],
            "technology": ["ai", "artificial intelligence", "technology", "quantum", "computer", "tech", "programming"],
            "lifestyle": ["food", "cooking", "travel", "fitness", "health", "art", "photography"],
            "education": ["learn", "study", "school", "college", "course", "knowledge"],
            "business": ["work", "job", "career", "business", "startup", "project"],
            "science": ["science", "research", "discovery", "theory", "experiment", "analysis"],
            "space": ["space", "star", "planet", "galaxy", "cosmos", "universe", "astronomical"],
            "stellaris": ["stellaris", "empire", "species", "galactic", "federation", "hyperlane", "ascension"],
        }

        engagement_probabilities = {
            "gaming": 0.6,
            "entertainment": 0.5,
            "technology": 0.6,
            "lifestyle": 0.4,
            "education": 0.5,
            "business": 0.4,
            "science": 0.5,
            "space": 0.6,      
            "stellaris": 0.7,  # Still slightly higher for stellaris since it's a specialized topic
        }

        for topic, keywords in topic_keywords_engagement.items():
            if any(keyword in content_lower for keyword in keywords):
                import random
                if random.random() < engagement_probabilities.get(topic, 0.4):
                    return True, f"topic_engagement_{topic}"

                if random.random() < engagement_probabilities.get(topic, 0.3):
                    return True, f"topic_engagement_{topic}"

        # Enhanced emotional support detection
        emotional_keywords = [
            "sad",
            "frustrated",
            "confused",
            "lost",
            "don't understand",
            "struggling",
            "excited",
            "happy",
            "amazing",
            "awesome",
            "incredible",
            "fantastic",
        ]
        if any(keyword in content_lower for keyword in emotional_keywords):
            return True, "emotional_engagement"

        # Greeting detection - More responsive
        greeting_keywords = [
            "hello",
            "hi",
            "hey",
            "good morning",
            "good evening",
            "what's up",
            "sup",
        ]
        if any(keyword in content_lower for keyword in greeting_keywords):
            import random

            if random.random() < 0.7:  # 70% chance to respond to greetings
                return True, "greeting_response"

        # General conversation engagement - NEW
        # Respond to longer, substantive messages more often
        if len(message.content) > 50 and not message.content.startswith(
            ("http", "www")
        ):
            import random

            if random.random() < 0.2:  # 20% chance for substantial messages
                return True, "general_conversation"

        return False, "no_trigger_matched"
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

            # Get recent topics from channel activity to personalize message
            channel_activity = self.channel_activity.get(channel.id, {})
            recent_topics = channel_activity.get("recent_topics", [])
            
            # Topic-aware proactive messages
            topic_messages = {
                "gaming": [
                    f"Hey {user.display_name}! 🎮 Found any cool games lately?",
                    f"Hi {user.display_name}! 🕹️ How's your gaming session going?",
                    f"{user.display_name}, discovered any epic wins recently? 🏆",
                ],
                "entertainment": [
                    f"Hey {user.display_name}! 🎬 Watched anything interesting lately?",
                    f"Hi {user.display_name}! 🎵 Any good music recommendations?",
                    f"{user.display_name}, found any binge-worthy shows? 📺",
                ],
                "technology": [
                    f"Hey {user.display_name}! 💻 Working on any cool tech projects?",
                    f"Hi {user.display_name}! 🤖 Seen any interesting AI developments?",
                    f"{user.display_name}, what tech trends are catching your eye? ⚡",
                ],
                "lifestyle": [
                    f"Hey {user.display_name}! 🌟 How's your day treating you?",
                    f"Hi {user.display_name}! ✨ Any new adventures or hobbies?",
                    f"{user.display_name}, discovered anything that made you smile? 😊",
                ],
                "space": [
                    f"Hey {user.display_name}! 🌌 Seen any cool space news lately?",
                    f"Hi {user.display_name}! ⭐ The universe is fascinating, isn't it?",
                    f"{user.display_name}, any cosmic thoughts to share? 🚀",
                ],
                "stellaris": [
                    f"Hey {user.display_name}! 🌌 How's your galactic empire expanding?",
                    f"Hi {user.display_name}! ⚔️ Any epic space battles lately?",
                    f"{user.display_name}, conquered any interesting worlds? 🏛️",
                ],
            }

            # Choose message based on recent topics or use general ones
            messages = []
            for topic in recent_topics[-3:]:  # Check last 3 topics
                if topic in topic_messages:
                    messages.extend(topic_messages[topic])
            
            # General friendly messages if no specific topics
            if not messages:
                messages = [
                    f"Hey {user.display_name}! 😊 How's everything going?",
                    f"Hi {user.display_name}! ✨ What's been on your mind lately?",
                    f"{user.display_name}, hope you're having a great day! 🌟",
                    f"Hey {user.display_name}! � Any interesting thoughts to share?",
                    f"Hi {user.display_name}! 🤝 How's your day been treating you?",
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
                        f"� Chatting in {active_servers} communities",
                        f"🌟 Engaging with {active_servers} servers",
                        f"⚡ Active conversations in {active_servers} places",
                        f"🤝 Connecting with {active_servers} communities",
                    ]
                )

            # Topic-based adaptive statuses
            if self.interesting_topics:
                recent_topics = self.interesting_topics[-3:]  # Last 3 topics
                
                topic_status_map = {
                    "gaming": ["🎮 Discussing games", "🕹️ Talking about gaming", "🏆 Sharing game strategies"],
                    "entertainment": ["🎬 Chatting about movies", "� Discussing music", "📺 Talking about shows"],
                    "technology": ["💻 Exploring tech topics", "🤖 Discussing AI and tech", "⚡ Learning about innovation"],
                    "lifestyle": ["🍽️ Sharing lifestyle tips", "✈️ Talking about adventures", "🏋️ Discussing wellness"],
                    "education": ["📚 Helping with learning", "🎓 Discussing education", "💡 Sharing knowledge"],
                    "business": ["💼 Talking business", "🚀 Discussing startups", "📈 Analyzing trends"],
                    "science": ["� Exploring science", "🧪 Discussing research", "📊 Analyzing data"],
                    "space": ["🌌 Exploring the cosmos", "🚀 Discussing space", "⭐ Pondering the universe"],
                    "stellaris": ["🌌 Discussing galactic empires", "⚔️ Planning stellar strategies", "🏛️ Building civilizations"],
                    "social": ["👥 Connecting people", "💭 Facilitating discussions", "🤗 Building community"],
                }
                
                for topic in recent_topics:
                    if topic in topic_status_map:
                        status_messages.extend(topic_status_map[topic])

            # Default neutral statuses when no specific activity
            default_statuses = [
                "💬 Ready for conversation",
                "🌟 Listening and learning", 
                "🤖 Adapting to your community",
                "� Processing thoughts",
                f"� Watching over {total_servers} servers",
                "🎯 Ready to help",
                "✨ Evolving with each chat",
                "🔄 Learning from conversations",
                "🤝 Building connections",
                "💡 Sharing insights",
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
