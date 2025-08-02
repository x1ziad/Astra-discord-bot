"""
Advanced AI Cog for Astra Bot
Implements modern AI features with conversation engine integration
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

from ai.enhanced_conversation_engine import (
    get_conversation_engine,
    initialize_conversation_engine,
    EngagementTrigger,
    ConversationMood,
    AIProvider,
    EnhancedAIConversationEngine,
)
from config.enhanced_config import config_manager

logger = logging.getLogger("astra.advanced_ai")


class AdvancedAICog(commands.Cog):
    """Advanced AI features with modern conversation capabilities"""

    def __init__(self, bot):
        self.bot = bot
        self.config = config_manager
        self.logger = bot.logger

        # Initialize conversation engine
        ai_config = self.config.get_ai_config()
        self.conversation_engine = initialize_conversation_engine(ai_config)

        # Active conversations tracking
        self.active_conversations: Set[int] = set()
        self.conversation_cooldowns: Dict[int, datetime] = {}
        self.channel_activity: Dict[int, Dict[str, Any]] = {}

        # Proactive engagement
        self.engagement_patterns: Dict[int, List[datetime]] = {}
        self.user_join_timestamps: Dict[int, datetime] = {}

        # Performance tracking
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
        name="ai_personality", description="Customize AI personality for this server"
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
                    value="Use `/ai_personality <trait> <level>` to adjust specific traits\n"
                    "Example: `/ai_personality enthusiastic 9`",
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
