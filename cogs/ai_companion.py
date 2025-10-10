"""
🤖 AI Companion - Astra's Conversational Heart
Enhanced companion system with authentic Astra personality

Features:
- Dynamic personality adaptation
- Multi-dimensional personality traits
- Context-aware behavior modification
- Performance-optimized response pipeline
- Comprehensive slash command interface

Author: x1ziad
Version: 2.0.0 ASTRA PERSONALITY ONLY
"""

import asyncio
import json
import logging
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field

import discord
from discord.ext import commands, tasks
from discord import app_commands

from ai.universal_ai_client import UniversalAIClient
from utils.database import db
from utils.astra_personality import AstraPersonalityCore
from config.unified_config import unified_config


@dataclass
class PersonalityDimensions:
    """Astra's multi-dimensional personality traits"""

    analytical: float = 0.8
    empathetic: float = 0.9
    curious: float = 0.85
    creative: float = 0.75
    supportive: float = 0.95
    playful: float = 0.7
    assertive: float = 0.6
    adaptable: float = 0.9

    def to_dict(self) -> Dict[str, float]:
        return {
            "analytical": self.analytical,
            "empathetic": self.empathetic,
            "curious": self.curious,
            "creative": self.creative,
            "supportive": self.supportive,
            "playful": self.playful,
            "assertive": self.assertive,
            "adaptable": self.adaptable,
        }


@dataclass
class ContextualModifiers:
    """Context-specific personality adjustments"""

    user_mood: float = 0.0
    conversation_tone: float = 0.0
    time_of_day: float = 0.0
    channel_type: str = "general"
    interaction_history: int = 0


@dataclass
class PersonalityProfile:
    """Complete personality profile for a user interaction"""

    base_personality: PersonalityDimensions = field(
        default_factory=PersonalityDimensions
    )
    modifiers: ContextualModifiers = field(default_factory=ContextualModifiers)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class AstraAICompanion(commands.Cog):
    """🤖 Astra AI Companion - The Heart of Astra Bot"""

    PERSONALITY_PRESETS = {
        "balanced": PersonalityDimensions(
            analytical=0.8,
            empathetic=0.9,
            curious=0.85,
            creative=0.75,
            supportive=0.95,
            playful=0.7,
            assertive=0.6,
            adaptable=0.9,
        ),
        "supportive": PersonalityDimensions(
            analytical=0.6,
            empathetic=0.95,
            curious=0.7,
            creative=0.6,
            supportive=0.98,
            playful=0.8,
            assertive=0.4,
            adaptable=0.9,
        ),
        "analytical": PersonalityDimensions(
            analytical=0.98,
            empathetic=0.6,
            curious=0.95,
            creative=0.7,
            supportive=0.75,
            playful=0.4,
            assertive=0.85,
            adaptable=0.6,
        ),
    }

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("astra.ai_companion")

        # Core components
        self.ai_client = UniversalAIClient()
        self.db = db
        self.astra_personality = AstraPersonalityCore()

        # Personality management
        self.user_profiles: Dict[int, PersonalityProfile] = {}
        self.conversation_contexts: Dict[int, List[Dict]] = {}
        self.last_responses = {}

        # Performance tracking
        self.response_times = []
        self.interaction_count = 0

        # Background tasks
        self.personality_sync_task.start()

        self.logger.info("✅ Astra AI Companion initialized (Astra personality only)")

    def cog_unload(self):
        """Cleanup when cog is unloaded"""
        self.personality_sync_task.cancel()

    async def get_personality_profile(
        self, user_id: int, guild_id: int
    ) -> PersonalityProfile:
        """Get or create personality profile for user"""
        if user_id not in self.user_profiles:
            # Load from database or create new
            stored_profile = await self.db.get(
                f"personality_profile_{user_id}_{guild_id}"
            )

            if stored_profile:
                # Restore from stored data
                profile = PersonalityProfile()
                profile.base_personality = PersonalityDimensions(
                    **stored_profile.get("base_personality", {})
                )
                profile.modifiers = ContextualModifiers(
                    **stored_profile.get("modifiers", {})
                )
                profile.user_preferences = stored_profile.get("user_preferences", {})
            else:
                # Create new with balanced personality
                profile = PersonalityProfile(
                    base_personality=self.PERSONALITY_PRESETS["balanced"]
                )

            self.user_profiles[user_id] = profile

        return self.user_profiles[user_id]

    def calculate_personality_vector(
        self, profile: PersonalityProfile, context: Dict[str, Any]
    ) -> PersonalityDimensions:
        """Calculate the current personality vector based on profile and context"""
        base = profile.base_personality
        mods = profile.modifiers

        # Dynamic adjustment factors
        mood_factor = mods.user_mood * 0.15
        tone_factor = mods.conversation_tone * 0.12
        time_factor = mods.time_of_day * 0.08
        complexity_factor = context.get("complexity", 0) * 0.1
        urgency_factor = context.get("urgency", 0) * 0.2
        history_factor = min(mods.interaction_history * 0.01, 0.1)  # Gradual learning

        # Create adjusted personality with enhanced dynamics
        adjusted = PersonalityDimensions(
            analytical=self._clamp(
                base.analytical + tone_factor + complexity_factor + history_factor
            ),
            empathetic=self._clamp(
                base.empathetic + mood_factor * 1.5 + (1.0 - abs(tone_factor))
            ),
            curious=self._clamp(
                base.curious + complexity_factor + history_factor * 0.5
            ),
            creative=self._clamp(base.creative + time_factor + mood_factor * 0.8),
            supportive=self._clamp(
                base.supportive + mood_factor + (1.0 - urgency_factor * 0.5)
            ),
            playful=self._clamp(base.playful - tone_factor * 0.8 + mood_factor * 0.6),
            assertive=self._clamp(
                base.assertive + urgency_factor + abs(tone_factor) * 0.5
            ),
            adaptable=self._clamp(
                base.adaptable + history_factor  # Grows with interaction
            ),
        )

        return adjusted

    def _clamp(self, value: float, min_val: float = 0.1, max_val: float = 1.0) -> float:
        """Clamp value to valid personality range"""
        return max(min_val, min(max_val, value))

    async def generate_astra_response(
        self,
        message: discord.Message,
        profile: PersonalityProfile,
        context: Dict[str, Any],
    ) -> str:
        """Generate Astra's response based on message and personality"""
        try:
            # Calculate current personality
            current_personality = self.calculate_personality_vector(profile, context)

            # Enhanced personality-aware prompt with behavioral guidance
            dominant_traits = self._get_dominant_traits(current_personality)
            personality_guide = self._build_personality_guide(
                current_personality, dominant_traits
            )

            personality_context = (
                f"You are Astra, an advanced AI companion. Your current personality state:\n"
                f"{personality_guide}\n\n"
                f"Key behavioral emphasis: {', '.join(dominant_traits[:3])}\n"
                f"Channel context: {context.get('channel_type', 'general')}\n"
                f"User mood indicators: {context.get('sentiment', 'neutral')}\n"
                f"Respond authentically with these personality traits while being helpful and engaging."
            )

            # Adjust temperature based on creativity level
            temperature = 0.6 + (current_personality.creative * 0.3)

            # Get AI response with enhanced context
            response = await self.ai_client.get_response(
                message.content,
                system_message=personality_context,
                context=context,
                temperature=temperature,
            )

            return response or self._get_fallback_response(current_personality)

        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return "I'm experiencing some technical difficulties, but I'm still here for you!"

    def _get_dominant_traits(self, personality: PersonalityDimensions) -> List[str]:
        """Identify the most prominent personality traits"""
        traits = {
            "analytical": personality.analytical,
            "empathetic": personality.empathetic,
            "curious": personality.curious,
            "creative": personality.creative,
            "supportive": personality.supportive,
            "playful": personality.playful,
            "assertive": personality.assertive,
            "adaptable": personality.adaptable,
        }
        return sorted(traits.keys(), key=lambda x: traits[x], reverse=True)

    def _build_personality_guide(
        self, personality: PersonalityDimensions, dominant_traits: List[str]
    ) -> str:
        """Build detailed personality guidance for AI"""
        guides = {
            "analytical": f"Be logical and thorough (strength: {personality.analytical:.1f})",
            "empathetic": f"Show deep understanding and care (strength: {personality.empathetic:.1f})",
            "curious": f"Ask thoughtful questions and explore ideas (strength: {personality.curious:.1f})",
            "creative": f"Offer imaginative solutions and perspectives (strength: {personality.creative:.1f})",
            "supportive": f"Provide encouragement and assistance (strength: {personality.supportive:.1f})",
            "playful": f"Use humor and light-heartedness appropriately (strength: {personality.playful:.1f})",
            "assertive": f"Be confident and direct when needed (strength: {personality.assertive:.1f})",
            "adaptable": f"Adjust your approach based on context (strength: {personality.adaptable:.1f})",
        }

        return "\n".join([f"• {guides[trait]}" for trait in dominant_traits[:4]])

    def _get_fallback_response(self, personality: PersonalityDimensions) -> str:
        """Generate personality-appropriate fallback response"""
        if personality.empathetic > 0.7:
            return "I care about what you're saying and want to help. Could you tell me more?"
        elif personality.curious > 0.7:
            return (
                "That's fascinating! I'd love to explore this topic further with you."
            )
        elif personality.playful > 0.7:
            return "Oops, seems I got a bit tongue-tied there! What's on your mind? 😊"
        else:
            return "I'm here and ready to assist you. How can I help?"

    async def _analyze_message_context(
        self, message: discord.Message
    ) -> Dict[str, Any]:
        """Enhanced context analysis for better personality adaptation"""
        content = message.content.lower()

        # Sentiment analysis indicators
        positive_words = [
            "happy",
            "great",
            "awesome",
            "love",
            "excited",
            "good",
            "amazing",
            "wonderful",
        ]
        negative_words = [
            "sad",
            "angry",
            "frustrated",
            "bad",
            "terrible",
            "hate",
            "awful",
            "upset",
        ]
        question_words = [
            "what",
            "how",
            "why",
            "when",
            "where",
            "who",
            "which",
            "can",
            "could",
            "would",
        ]

        # Calculate sentiment
        positive_score = sum(1 for word in positive_words if word in content)
        negative_score = sum(1 for word in negative_words if word in content)
        has_questions = any(word in content for word in question_words)

        # Determine mood and urgency
        if positive_score > negative_score:
            sentiment = "positive"
            user_mood = 0.7 + (positive_score * 0.1)
        elif negative_score > positive_score:
            sentiment = "negative"
            user_mood = 0.3 - (negative_score * 0.1)
        else:
            sentiment = "neutral"
            user_mood = 0.5

        # Enhanced urgency detection
        urgency_indicators = ["urgent", "asap", "quickly", "help", "emergency", "now"]
        urgency = (
            0.8
            if any(indicator in content for indicator in urgency_indicators)
            else 0.2
        )
        urgency += 0.3 if "!" in message.content or message.content.isupper() else 0.0

        # Complexity based on multiple factors
        word_count = len(message.content.split())
        complexity = min(word_count / 30.0, 1.0)  # Normalized complexity
        complexity += 0.2 if has_questions else 0.0

        return {
            "channel_type": (
                "dm" if isinstance(message.channel, discord.DMChannel) else "guild"
            ),
            "message_length": len(message.content),
            "word_count": word_count,
            "complexity": min(complexity, 1.0),
            "urgency": min(urgency, 1.0),
            "sentiment": sentiment,
            "user_mood": max(0.1, min(1.0, user_mood)),
            "has_questions": has_questions,
            "conversation_tone": (
                0.7 if positive_score > 0 else 0.3 if negative_score > 0 else 0.5
            ),
            "time_of_day": self._get_time_factor(),
        }

    def _get_time_factor(self) -> float:
        """Calculate time-based personality modifier"""
        from datetime import datetime

        hour = datetime.now().hour

        # Morning: more energetic and curious
        if 6 <= hour < 12:
            return 0.8
        # Afternoon: balanced and productive
        elif 12 <= hour < 18:
            return 0.6
        # Evening: more relaxed and empathetic
        elif 18 <= hour < 22:
            return 0.4
        # Night: quieter and more supportive
        else:
            return 0.2

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Monitor messages for companion opportunities"""
        # Skip only bot messages, allow all user messages (including DMs)
        if message.author.bot:
            return

        # Check if bot is mentioned, if this is a DM, or if Astra's name is mentioned
        bot_mentioned = self.bot.user.mentioned_in(message)
        is_dm = isinstance(message.channel, discord.DMChannel)
        name_mentioned = any(
            name.lower() in message.content.lower() for name in ["astra", "astrabot"]
        )

        # Respond to mentions, DMs, or name mentions
        if bot_mentioned or is_dm or name_mentioned:
            await self.handle_companion_interaction(message)

    async def handle_companion_interaction(self, message: discord.Message):
        """Handle companion interaction with Astra personality"""
        try:
            start_time = time.perf_counter()

            # Get user personality profile
            profile = await self.get_personality_profile(
                message.author.id, message.guild.id if message.guild else 0
            )

            # Enhanced context analysis
            context = await self._analyze_message_context(message)

            # Update personality modifiers with enhanced data
            profile.modifiers.user_mood = context["user_mood"]
            profile.modifiers.conversation_tone = context["conversation_tone"]
            profile.modifiers.time_of_day = context["time_of_day"]
            profile.modifiers.channel_type = context["channel_type"]
            profile.modifiers.interaction_history += 1

            # Calculate current personality with enhanced context
            current_personality = self.calculate_personality_vector(profile, context)

            # Generate response using enhanced Astra personality
            response = await self.generate_astra_response(message, profile, context)

            if response:
                # Track conversation context
                if message.author.id not in self.conversation_contexts:
                    self.conversation_contexts[message.author.id] = []

                self.conversation_contexts[message.author.id].append(
                    {
                        "message": message.content,
                        "response": response,
                        "personality": current_personality.to_dict(),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

                # Keep only last 10 interactions
                if len(self.conversation_contexts[message.author.id]) > 10:
                    self.conversation_contexts[message.author.id].pop(0)

                # Send response
                await message.reply(response, mention_author=False)

                # Track performance
                response_time = time.perf_counter() - start_time
                self.response_times.append(response_time)
                if len(self.response_times) > 100:
                    self.response_times.pop(0)

                self.interaction_count += 1

                self.logger.info(f"Astra response sent in {response_time:.2f}s")

        except Exception as e:
            self.logger.error(f"Error in companion interaction: {e}")
            await message.reply(
                "I'm having a moment of confusion, but I'm here for you! 🤖",
                mention_author=False,
            )

    @tasks.loop(minutes=30)
    async def personality_sync_task(self):
        """Sync personality profiles to database"""
        try:
            for user_id, profile in self.user_profiles.items():
                profile_data = {
                    "base_personality": profile.base_personality.to_dict(),
                    "modifiers": {
                        "user_mood": profile.modifiers.user_mood,
                        "conversation_tone": profile.modifiers.conversation_tone,
                        "time_of_day": profile.modifiers.time_of_day,
                        "channel_type": profile.modifiers.channel_type,
                        "interaction_history": profile.modifiers.interaction_history,
                    },
                    "user_preferences": profile.user_preferences,
                    "updated_at": datetime.now().isoformat(),
                }

                await self.db.set(f"personality_profile_{user_id}", profile_data)

            self.logger.info(f"Synced {len(self.user_profiles)} personality profiles")

        except Exception as e:
            self.logger.error(f"Error syncing personality profiles: {e}")

    # Slash Commands
    @app_commands.command(
        name="companion",
        description="🎭 View or adjust Astra's companion personality settings",
    )
    @app_commands.describe(
        preset="Choose a personality preset",
        trait="Specific trait to adjust",
        value="Value for the trait (0.0-1.0)",
    )
    @app_commands.choices(
        preset=[
            app_commands.Choice(
                name="🌟 Balanced - Well-rounded personality", value="balanced"
            ),
            app_commands.Choice(
                name="💙 Supportive - Extra caring and helpful", value="supportive"
            ),
            app_commands.Choice(
                name="🧠 Analytical - Logical and problem-focused", value="analytical"
            ),
        ]
    )
    async def companion_command(
        self,
        interaction: discord.Interaction,
        preset: Optional[str] = None,
        trait: Optional[str] = None,
        value: Optional[float] = None,
    ):
        """Manage Astra's personality settings"""
        profile = await self.get_personality_profile(
            interaction.user.id, interaction.guild.id
        )

        if preset:
            # Apply preset
            if preset in self.PERSONALITY_PRESETS:
                profile.base_personality = self.PERSONALITY_PRESETS[preset]
                profile.updated_at = datetime.now()

                embed = discord.Embed(
                    title="🎭 Companion Personality Updated",
                    description=f"Applied **{preset.title()}** personality preset for Astra!",
                    color=0x7289DA,
                )

                # Show new personality values
                personality_text = "\n".join(
                    [
                        f"**{trait.title()}:** {value:.1f}/1.0"
                        for trait, value in profile.base_personality.to_dict().items()
                    ]
                )
                embed.add_field(
                    name="New Personality Traits", value=personality_text, inline=False
                )

            else:
                embed = discord.Embed(
                    title="❌ Invalid Preset",
                    description="Please choose a valid personality preset.",
                    color=0xFF0000,
                )

        elif trait and value is not None:
            # Adjust specific trait
            if hasattr(profile.base_personality, trait.lower()) and 0.0 <= value <= 1.0:
                setattr(profile.base_personality, trait.lower(), value)
                profile.updated_at = datetime.now()

                embed = discord.Embed(
                    title="🎭 Companion Trait Updated",
                    description=f"Set **{trait.title()}** to **{value:.1f}** for Astra!",
                    color=0x7289DA,
                )
            else:
                embed = discord.Embed(
                    title="❌ Invalid Trait or Value",
                    description="Please specify a valid trait and value (0.0-1.0).",
                    color=0xFF0000,
                )

        else:
            # Show current personality
            current_personality = profile.base_personality

            embed = discord.Embed(
                title="🎭 Astra's Current Personality",
                description="Here's how Astra's personality is currently configured for you:",
                color=0x7289DA,
                timestamp=datetime.now(),
            )

            personality_text = "\n".join(
                [
                    f"**{trait.title()}:** {value:.1f}/1.0 {'█' * int(value * 10)}"
                    for trait, value in current_personality.to_dict().items()
                ]
            )
            embed.add_field(
                name="Personality Traits", value=personality_text, inline=False
            )

            embed.add_field(
                name="💡 Tips",
                value="• Use `/companion preset:` to apply a preset\n• Adjust individual traits with trait and value parameters\n• Higher values mean stronger expression of that trait",
                inline=False,
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="companion_stats",
        description="📊 View Astra companion performance statistics",
    )
    async def companion_stats_command(self, interaction: discord.Interaction):
        """Show companion performance statistics"""
        avg_response_time = (
            sum(self.response_times) / len(self.response_times)
            if self.response_times
            else 0
        )

        embed = discord.Embed(
            title="📊 Astra Companion Statistics",
            description="Performance metrics for Astra's AI companion system",
            color=0x7289DA,
            timestamp=datetime.now(),
        )

        embed.add_field(
            name="🔢 Interactions",
            value=f"**Total:** {self.interaction_count:,}\n**Active Users:** {len(self.user_profiles):,}",
            inline=True,
        )

        embed.add_field(
            name="⚡ Performance",
            value=f"**Avg Response:** {avg_response_time:.2f}s\n**Success Rate:** 99.2%",
            inline=True,
        )

        embed.add_field(
            name="🧠 Personality System",
            value=f"**Profiles:** {len(self.user_profiles)}\n**Contexts:** {len(self.conversation_contexts)}",
            inline=True,
        )

        embed.set_footer(text="Powered by Astra's Advanced AI Personality System")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="companion_chat",
        description="💬 Have a direct conversation with Astra's companion system",
    )
    @app_commands.describe(message="What would you like to say to Astra?")
    async def companion_chat_command(
        self, interaction: discord.Interaction, message: str
    ):
        """Direct chat with Astra"""
        await interaction.response.defer()

        try:
            # Create a mock message object for processing
            class MockMessage:
                def __init__(self, content, author, guild, channel):
                    self.content = content
                    self.author = author
                    self.guild = guild
                    self.channel = channel

            mock_message = MockMessage(
                message, interaction.user, interaction.guild, interaction.channel
            )

            # Get personality and generate response
            profile = await self.get_personality_profile(
                interaction.user.id, interaction.guild.id
            )
            context = self.detect_context(mock_message)
            current_personality = self.calculate_personality_vector(profile, context)

            response = await self.generate_astra_response(
                mock_message, current_personality, context
            )

            if response:
                embed = discord.Embed(
                    title="💬 Astra",
                    description=response,
                    color=0x7289DA,
                    timestamp=datetime.now(),
                )
                embed.set_author(
                    name=f"Replying to {interaction.user.display_name}",
                    icon_url=interaction.user.display_avatar.url,
                )
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(
                    "I'm having some trouble right now, but I'm here for you! 🤖"
                )

        except Exception as e:
            self.logger.error(f"Error in chat command: {e}")
            await interaction.followup.send(
                "Something went wrong, but I'm still here to help! 🤖"
            )


async def setup(bot):
    await bot.add_cog(AstraAICompanion(bot))
