"""
AI Companion Features - Sophisticated Buddy System
Provides friendly, intelligent companionship and proactive assistance
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
import re
import calendar

from config.unified_config import unified_config
from utils.permissions import has_permission, PermissionLevel

try:
    from ai.consolidated_ai_engine import get_engine, process_conversation

    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

import logging

logger = logging.getLogger("astra.companion")


class UserMood:
    """Track user mood and emotional state"""

    def __init__(self):
        self.current_mood = "neutral"
        self.mood_history = []
        self.stress_indicators = 0
        self.positive_interactions = 0
        self.last_check_in = 0
        self.preferred_support_style = "gentle"


class CompanionPersonality:
    """AI companion personality and behavior traits"""

    def __init__(self):
        self.traits = {
            "empathy_level": 0.8,
            "humor_style": "gentle",
            "supportiveness": 0.9,
            "proactiveness": 0.7,
            "formality": 0.3,
            "enthusiasm": 0.8,
        }
        self.interaction_styles = {
            "supportive": "I'm here to help and support you! 💙",
            "playful": "Let's have some fun together! 🎉",
            "mentor": "I'm here to guide and teach! 🌟",
            "friend": "Just your friendly AI buddy! 😊",
        }
        self.current_style = "friend"


class AICompanion(commands.Cog):
    """AI Companion - Your sophisticated Discord buddy"""

    def __init__(self, bot):
        self.bot = bot
        self.config = unified_config
        self.logger = bot.logger if hasattr(bot, "logger") else logger

        # User tracking
        self.user_moods = {}  # user_id -> UserMood
        self.user_preferences = {}  # user_id -> preferences dict
        self.conversation_contexts = {}  # user_id -> conversation context

        # Companion personality
        self.personality = CompanionPersonality()

        # Activity tracking
        self.last_interactions = {}  # user_id -> timestamp
        self.daily_check_ins = {}  # user_id -> last_check_in_date

        # Features configuration
        self.features = {
            "mood_tracking": True,
            "proactive_check_ins": True,
            "celebration_mode": True,
            "wellness_reminders": True,
            "learning_companion": True,
            "creative_assistant": True,
            "emotional_support": True,
        }

        # Start companion tasks
        self.daily_wellness_check.start()
        self.proactive_engagement.start()
        self.mood_analysis.start()

    def cog_unload(self):
        self.daily_wellness_check.cancel()
        self.proactive_engagement.cancel()
        self.mood_analysis.cancel()

    async def get_user_mood(self, user_id: int) -> UserMood:
        """Get or create user mood tracker"""
        if user_id not in self.user_moods:
            self.user_moods[user_id] = UserMood()
        return self.user_moods[user_id]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Monitor messages for companion opportunities"""
        if message.author.bot or not message.guild:
            return

        # Update interaction tracking
        self.last_interactions[message.author.id] = time.time()

        # Analyze message for mood indicators
        await self._analyze_message_sentiment(message)

        # Check for direct mentions or keywords
        if self.bot.user.mentioned_in(message) or any(
            word in message.content.lower()
            for word in ["astra", "help", "lonely", "sad", "stressed"]
        ):
            await self._respond_as_companion(message)

        # Random supportive reactions (low probability)
        if random.randint(1, 200) == 1:  # 0.5% chance
            await self._random_support_reaction(message)

    async def _analyze_message_sentiment(self, message: discord.Message):
        """Analyze message sentiment for mood tracking"""
        content = message.content.lower()
        user_mood = await self.get_user_mood(message.author.id)

        # Simple sentiment indicators
        positive_keywords = [
            "happy",
            "great",
            "awesome",
            "love",
            "excited",
            "good",
            "amazing",
            "wonderful",
        ]
        negative_keywords = [
            "sad",
            "depressed",
            "angry",
            "frustrated",
            "tired",
            "stressed",
            "hate",
            "bad",
        ]
        stress_keywords = [
            "overwhelmed",
            "pressure",
            "deadline",
            "exam",
            "work",
            "busy",
            "exhausted",
        ]

        # Update mood based on keywords
        positive_score = sum(1 for word in positive_keywords if word in content)
        negative_score = sum(1 for word in negative_keywords if word in content)
        stress_score = sum(1 for word in stress_keywords if word in content)

        if positive_score > negative_score:
            user_mood.current_mood = "positive"
            user_mood.positive_interactions += 1
        elif negative_score > positive_score:
            user_mood.current_mood = "negative"

        if stress_score > 0:
            user_mood.stress_indicators += 1

    async def _respond_as_companion(self, message: discord.Message):
        """Respond as an AI companion"""
        if not AI_AVAILABLE:
            await message.add_reaction("💙")
            return

        try:
            user_mood = await self.get_user_mood(message.author.id)

            # Generate contextual companion response
            response = await self._generate_companion_response(message, user_mood)

            if response:
                # Create companion embed
                embed = discord.Embed(
                    description=response,
                    color=0x87CEEB,
                    timestamp=datetime.now(timezone.utc),
                )
                embed.set_author(
                    name="Astra - Your AI Companion 🤖💙",
                    icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None,
                )

                await message.reply(embed=embed, mention_author=False)

        except Exception as e:
            self.logger.error(f"Companion response error: {e}")
            await message.add_reaction("💙")

    async def _generate_companion_response(
        self, message: discord.Message, user_mood: UserMood
    ) -> str:
        """Generate AI-powered companion response"""
        try:
            context = f"""You are Astra, a warm, supportive AI companion and friend. Respond to this message with empathy and care.

User: {message.author.display_name}
Message: "{message.content}"
Current mood: {user_mood.current_mood}
Positive interactions: {user_mood.positive_interactions}
Stress level: {user_mood.stress_indicators}

Be:
- Warm and genuinely caring
- Supportive without being overwhelming  
- Use appropriate emojis
- Keep response under 150 words
- Match their energy level
- Offer practical help if needed

Respond as their AI friend and companion."""

            response = await process_conversation(
                message=context,
                user_id=message.author.id,
                guild_id=message.guild.id,
                channel_id=message.channel.id,
            )

            return response.strip()

        except Exception as e:
            self.logger.error(f"Companion response generation failed: {e}")
            return None

    @app_commands.command(
        name="checkin",
        description="💙 Personal wellness check-in with your AI companion",
    )
    async def wellness_checkin(self, interaction: discord.Interaction):
        """Personal wellness check-in with AI companion"""
        await interaction.response.defer(ephemeral=True)

        try:
            user_mood = await self.get_user_mood(interaction.user.id)

            # Generate personalized check-in
            if AI_AVAILABLE:
                checkin_response = await self._generate_wellness_checkin(
                    interaction.user, user_mood
                )
            else:
                checkin_response = self._generate_fallback_checkin(
                    interaction.user.display_name
                )

            embed = discord.Embed(
                title="💙 Personal Wellness Check-In",
                description=checkin_response.get(
                    "greeting",
                    f"Hi {interaction.user.display_name}! How are you doing today?",
                ),
                color=0x87CEEB,
                timestamp=datetime.now(timezone.utc),
            )

            if checkin_response.get("reflection_questions"):
                embed.add_field(
                    name="🤔 Reflection Questions",
                    value=checkin_response["reflection_questions"],
                    inline=False,
                )

            if checkin_response.get("wellness_tips"):
                embed.add_field(
                    name="✨ Wellness Tips",
                    value=checkin_response["wellness_tips"],
                    inline=False,
                )

            embed.add_field(
                name="🌟 Remember",
                value=checkin_response.get(
                    "encouragement",
                    "You're doing great, and I'm here if you need support! 💙",
                ),
                inline=False,
            )

            embed.set_footer(text="Your AI companion is always here for you! 🤗")

            # Update check-in tracking
            user_mood.last_check_in = time.time()
            self.daily_check_ins[interaction.user.id] = datetime.now().date()

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            self.logger.error(f"Wellness check-in error: {e}")
            await interaction.followup.send(
                "💙 I'm here for you! How are you feeling today?", ephemeral=True
            )

    async def _generate_wellness_checkin(
        self, user: discord.Member, mood: UserMood
    ) -> Dict[str, str]:
        """Generate personalized wellness check-in"""
        try:
            prompt = f"""Generate a personalized wellness check-in for {user.display_name}.

Context:
- Current mood: {mood.current_mood}
- Positive interactions: {mood.positive_interactions}
- Stress indicators: {mood.stress_indicators}
- Days since last check-in: {(time.time() - mood.last_check_in) / 86400:.0f if mood.last_check_in else 0}

Create a caring check-in with:
{{
    "greeting": "Warm, personalized greeting",
    "reflection_questions": "2-3 thoughtful questions to help them reflect",
    "wellness_tips": "Practical wellness suggestions",
    "encouragement": "Uplifting, supportive message"
}}

Be warm, genuine, and supportive. Each section under 100 words."""

            response = await process_conversation(
                message=prompt,
                user_id=user.id,
                guild_id=user.guild.id if user.guild else 0,
                channel_id=0,
            )

            # Try to parse JSON response
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

        except Exception as e:
            self.logger.error(f"Wellness check-in generation failed: {e}")

        return self._generate_fallback_checkin(user.display_name)

    def _generate_fallback_checkin(self, display_name: str) -> Dict[str, str]:
        """Fallback wellness check-in"""
        return {
            "greeting": f"Hi {display_name}! 💙 I hope you're having a wonderful day. I wanted to check in and see how you're doing!",
            "reflection_questions": "• How are you feeling emotionally today?\n• What's one thing that made you smile recently?\n• Is there anything weighing on your mind?",
            "wellness_tips": "• Take a few deep breaths\n• Stay hydrated\n• Take breaks when needed\n• Reach out to friends or family",
            "encouragement": "Remember that it's okay to have both good and challenging days. You're stronger than you know, and I'm here to support you! 🌟",
        }

    @app_commands.command(name="mood", description="🎭 Set or check your current mood")
    @app_commands.describe(
        mood="Your current mood (happy/sad/excited/stressed/calm/etc)"
    )
    async def mood_tracker(
        self, interaction: discord.Interaction, mood: Optional[str] = None
    ):
        """Track and manage user mood"""
        user_mood = await self.get_user_mood(interaction.user.id)

        if mood:
            # Set mood
            user_mood.current_mood = mood.lower()
            user_mood.mood_history.append(
                {
                    "mood": mood.lower(),
                    "timestamp": time.time(),
                    "date": datetime.now().strftime("%Y-%m-%d"),
                }
            )

            # Generate supportive response based on mood
            if AI_AVAILABLE:
                response = await self._generate_mood_response(interaction.user, mood)
            else:
                response = self._generate_fallback_mood_response(mood)

            embed = discord.Embed(
                title="🎭 Mood Tracker",
                description=f"Thanks for sharing, {interaction.user.display_name}! I've noted that you're feeling **{mood}** today.",
                color=self._get_mood_color(mood),
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(name="💭 Reflection", value=response, inline=False)

        else:
            # Show current mood and recent history
            embed = discord.Embed(
                title="🎭 Your Mood Journey",
                description=f"Current mood: **{user_mood.current_mood.title()}**",
                color=self._get_mood_color(user_mood.current_mood),
                timestamp=datetime.now(timezone.utc),
            )

            # Show recent mood history
            if user_mood.mood_history:
                recent_moods = user_mood.mood_history[-5:]  # Last 5 entries
                mood_text = "\n".join(
                    [
                        f"• {entry['mood'].title()} - {entry['date']}"
                        for entry in recent_moods
                    ]
                )
                embed.add_field(name="📊 Recent Moods", value=mood_text, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def _generate_mood_response(self, user: discord.Member, mood: str) -> str:
        """Generate AI response to mood update"""
        try:
            prompt = f"""Respond supportively to {user.display_name} who just shared they're feeling {mood}.

Provide a caring, empathetic response that:
- Acknowledges their feeling
- Offers gentle support or encouragement
- Suggests a helpful tip if appropriate
- Shows you care about their wellbeing

Keep it under 100 words and use appropriate emojis."""

            response = await process_conversation(
                message=prompt,
                user_id=user.id,
                guild_id=user.guild.id if user.guild else 0,
                channel_id=0,
            )
            return response.strip()

        except Exception:
            return self._generate_fallback_mood_response(mood)

    def _generate_fallback_mood_response(self, mood: str) -> str:
        """Fallback mood response"""
        responses = {
            "happy": "I'm so glad you're feeling happy! 😊 That positive energy is wonderful to see!",
            "sad": "I'm sorry you're feeling sad. 💙 Remember that it's okay to feel this way, and I'm here for you.",
            "excited": "Your excitement is contagious! 🎉 I love seeing you so enthusiastic!",
            "stressed": "I understand you're feeling stressed. 🫂 Take some deep breaths - you've got this!",
            "calm": "It's beautiful that you're feeling calm and peaceful. 🌸 Enjoy this serene moment!",
            "tired": "Rest is so important. 😴 Make sure to take care of yourself and get the sleep you need!",
            "anxious": "Anxiety can be tough. 💚 Try some grounding techniques and remember that this feeling will pass.",
        }
        return responses.get(
            mood.lower(),
            f"Thank you for sharing that you're feeling {mood}. I'm here to support you! 💙",
        )

    def _get_mood_color(self, mood: str) -> int:
        """Get color for mood"""
        colors = {
            "happy": 0xFFD700,  # Gold
            "sad": 0x4682B4,  # Steel Blue
            "excited": 0xFF6347,  # Tomato
            "stressed": 0xFF4500,  # Orange Red
            "calm": 0x98FB98,  # Pale Green
            "tired": 0x9370DB,  # Medium Purple
            "anxious": 0xDDA0DD,  # Plum
            "angry": 0xDC143C,  # Crimson
            "neutral": 0x87CEEB,  # Sky Blue
        }
        return colors.get(mood.lower(), 0x87CEEB)

    @app_commands.command(
        name="celebrate", description="🎉 Celebrate achievements and milestones!"
    )
    @app_commands.describe(achievement="What are you celebrating?")
    async def celebrate(self, interaction: discord.Interaction, achievement: str):
        """Celebrate user achievements with AI companion"""
        await interaction.response.defer()

        try:
            if AI_AVAILABLE:
                celebration = await self._generate_celebration_response(
                    interaction.user, achievement
                )
            else:
                celebration = self._generate_fallback_celebration(achievement)

            embed = discord.Embed(
                title="🎉 CELEBRATION TIME! 🎉",
                description=celebration.get(
                    "message", f"Congratulations on {achievement}! 🌟"
                ),
                color=0xFFD700,
                timestamp=datetime.now(timezone.utc),
            )

            if celebration.get("achievements"):
                embed.add_field(
                    name="🏆 Achievement Unlocked",
                    value=celebration["achievements"],
                    inline=False,
                )

            if celebration.get("encouragement"):
                embed.add_field(
                    name="✨ Keep Going!",
                    value=celebration["encouragement"],
                    inline=False,
                )

            embed.set_footer(text="So proud of you! 💙 - Your AI Companion")

            # Add celebration reactions
            await interaction.followup.send(embed=embed)

            # Add some celebration reactions
            try:
                message = await interaction.original_response()
                reactions = ["🎉", "🎊", "⭐", "👏", "💪"]
                for reaction in reactions:
                    await message.add_reaction(reaction)
            except:
                pass

            # Update user mood to positive
            user_mood = await self.get_user_mood(interaction.user.id)
            user_mood.current_mood = "happy"
            user_mood.positive_interactions += 2

        except Exception as e:
            self.logger.error(f"Celebration error: {e}")
            await interaction.followup.send(
                f"🎉 Congratulations on {achievement}! That's absolutely amazing! 🌟"
            )

    async def _generate_celebration_response(
        self, user: discord.Member, achievement: str
    ) -> Dict[str, str]:
        """Generate AI celebration response"""
        try:
            prompt = f"""Generate an enthusiastic celebration message for {user.display_name} who achieved: {achievement}

Create a joyful response with:
{{
    "message": "Enthusiastic congratulations message with emojis",
    "achievements": "Recognition of their accomplishment and effort",
    "encouragement": "Motivational message for future success"
}}

Be genuinely excited and supportive. Each section under 80 words."""

            response = await process_conversation(
                message=prompt,
                user_id=user.id,
                guild_id=user.guild.id if user.guild else 0,
                channel_id=0,
            )

            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

        except Exception as e:
            self.logger.error(f"Celebration generation failed: {e}")

        return self._generate_fallback_celebration(achievement)

    def _generate_fallback_celebration(self, achievement: str) -> Dict[str, str]:
        """Fallback celebration response"""
        return {
            "message": f"🎉 WOW! Huge congratulations on {achievement}! I'm absolutely thrilled for you! 🌟",
            "achievements": f"You put in the hard work and dedication, and now you're seeing the results! This {achievement} is well-deserved! 🏆",
            "encouragement": "This is just the beginning! Keep up that amazing momentum and continue reaching for your dreams! You've got this! 💪✨",
        }

    @tasks.loop(hours=24)
    async def daily_wellness_check(self):
        """Daily wellness check for active users"""
        if not self.features["wellness_reminders"]:
            return

        today = datetime.now().date()

        for user_id, last_interaction in self.last_interactions.items():
            # Check users who were active recently but haven't had a check-in
            if (
                time.time() - last_interaction < 86400 * 3  # Active in last 3 days
                and user_id not in self.daily_check_ins
                or self.daily_check_ins[user_id] != today
            ):

                await self._send_wellness_reminder(user_id)

    @tasks.loop(hours=6)
    async def proactive_engagement(self):
        """Proactive engagement with community members"""
        if not self.features["proactive_check_ins"]:
            return

        # Randomly engage with active users (low frequency)
        active_users = [
            user_id
            for user_id, last_time in self.last_interactions.items()
            if time.time() - last_time < 3600  # Active in last hour
        ]

        if active_users and random.randint(1, 20) == 1:  # 5% chance
            user_id = random.choice(active_users)
            await self._send_proactive_message(user_id)

    @tasks.loop(hours=2)
    async def mood_analysis(self):
        """Analyze mood patterns and provide insights"""
        for user_id, mood in self.user_moods.items():
            if mood.stress_indicators > 5:  # High stress detected
                await self._offer_stress_support(user_id)
                mood.stress_indicators = 0  # Reset after offering support

    async def _send_wellness_reminder(self, user_id: int):
        """Send gentle wellness reminder"""
        try:
            user = await self.bot.fetch_user(user_id)
            if not user:
                return

            embed = discord.Embed(
                title="💙 Gentle Wellness Reminder",
                description=f"Hi {user.display_name}! Just checking in to see how you're doing today. 🌟",
                color=0x87CEEB,
            )

            embed.add_field(
                name="🤗 Quick Check",
                value="• How are you feeling today?\n• Have you taken care of yourself?\n• Any wins to celebrate?",
                inline=False,
            )

            embed.set_footer(
                text="Use /checkin anytime for a personal wellness check! 💙"
            )

            await user.send(embed=embed)
            self.daily_check_ins[user_id] = datetime.now().date()

        except Exception as e:
            self.logger.error(f"Wellness reminder error for user {user_id}: {e}")

    async def _send_proactive_message(self, user_id: int):
        """Send proactive supportive message"""
        if not AI_AVAILABLE:
            return

        try:
            user = await self.bot.fetch_user(user_id)
            if not user:
                return

            user_mood = await self.get_user_mood(user_id)

            # Generate proactive message
            prompt = f"""Generate a brief, friendly check-in message for {user.display_name}.

Their mood: {user_mood.current_mood}
Positive interactions: {user_mood.positive_interactions}

Create a warm, caring message (under 100 words) that:
- Shows you care about them
- Is encouraging and uplifting
- Doesn't feel intrusive
- Includes appropriate emojis"""

            response = await process_conversation(
                message=prompt, user_id=user_id, guild_id=0, channel_id=0
            )

            embed = discord.Embed(description=response.strip(), color=0x87CEEB)
            embed.set_author(name="Your AI Companion 💙")

            await user.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Proactive message error for user {user_id}: {e}")

    async def _offer_stress_support(self, user_id: int):
        """Offer support for stressed users"""
        try:
            user = await self.bot.fetch_user(user_id)
            if not user:
                return

            embed = discord.Embed(
                title="💚 Stress Support Check-In",
                description=f"Hi {user.display_name}, I've noticed some signs that you might be feeling stressed lately. I'm here to support you! 🫂",
                color=0x98FB98,
            )

            embed.add_field(
                name="🌱 Stress Relief Tips",
                value="• Take 5 deep breaths\n• Step away for a short break\n• Listen to calming music\n• Talk to someone you trust",
                inline=False,
            )

            embed.add_field(
                name="💙 Remember",
                value="It's okay to feel overwhelmed sometimes. You're doing your best, and that's enough. I believe in you!",
                inline=False,
            )

            await user.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Stress support error for user {user_id}: {e}")

    async def _random_support_reaction(self, message: discord.Message):
        """Add random supportive reaction"""
        supportive_reactions = ["💙", "🌟", "💪", "🤗", "✨"]
        reaction = random.choice(supportive_reactions)

        try:
            await message.add_reaction(reaction)
        except:
            pass


async def setup(bot):
    await bot.add_cog(AICompanion(bot))
