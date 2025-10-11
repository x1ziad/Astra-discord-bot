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

        # Personality management (key format: "user_id_guild_id")
        self.user_profiles: Dict[str, PersonalityProfile] = {}
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
        profile_key = f"{user_id}_{guild_id}"

        if profile_key not in self.user_profiles:
            # Load from database or create new
            stored_profile = await self.db.get("user_profiles", profile_key)

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

            self.user_profiles[profile_key] = profile

        return self.user_profiles[profile_key]

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
            self.logger.debug(f"🔧 Starting response generation for: '{message.content[:30]}...'")
            
            # Calculate current personality
            current_personality = self.calculate_personality_vector(profile, context)

            # Enhanced personality-aware user profile for AI client
            dominant_traits = self._get_dominant_traits(current_personality)

            # Build user profile with personality context for AI client
            user_profile_data = {
                "name": message.author.display_name,
                "personality_traits": dominant_traits[:3],
                "dominant_emotion": context.get("sentiment", "neutral"),
                "channel_context": context.get("channel_type", "general"),
                "interaction_count": profile.modifiers.interaction_history,
                "current_mood": context.get("user_mood", 0.5),
                "personality_guide": self._build_personality_guide(
                    current_personality, dominant_traits
                ),
                "astra_context": "Astra AI companion with dynamic personality adaptation",
            }

            # Adjust temperature based on creativity level
            temperature = 0.6 + (current_personality.creative * 0.3)
            
            self.logger.debug(f"🎯 Calling AI client with temperature={temperature:.2f}")

            # Get AI response with enhanced context using UniversalAIClient
            ai_response = await self.ai_client.generate_response(
                message.content,
                user_id=message.author.id,
                guild_id=message.guild.id if message.guild else None,
                channel_id=message.channel.id,
                user_profile=user_profile_data,
                temperature=temperature,
            )
            
            self.logger.debug(f"🤖 AI response received: {ai_response is not None}")
            if ai_response:
                self.logger.debug(f"📝 AI response content length: {len(ai_response.content) if hasattr(ai_response, 'content') and ai_response.content else 0}")

            response = ai_response.content if ai_response and hasattr(ai_response, 'content') else None
            
            if not response:
                self.logger.warning(f"⚠️ AI client returned no response, using fallback")
                response = self._get_fallback_response(current_personality)

            return response

        except Exception as e:
            self.logger.error(f"❌ Error generating response: {e}")
            import traceback
            self.logger.error(f"📋 Traceback: {traceback.format_exc()}")
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
        
        # Enhanced trigger detection
        content_lower = message.content.lower()
        question_patterns = ["?", "who are you", "what are you", "help me", "can you help"]
        greeting_patterns = ["hey", "hi", "hello", "what's up", "how are you"]
        
        has_question = any(pattern in content_lower for pattern in question_patterns)
        has_greeting = any(content_lower.startswith(pattern) for pattern in greeting_patterns)

        # Debug logging
        self.logger.debug(f"Message from {message.author}: '{message.content[:50]}...'")
        self.logger.debug(f"Triggers - Mentioned: {bot_mentioned}, DM: {is_dm}, Name: {name_mentioned}, Question: {has_question}, Greeting: {has_greeting}")

        # Respond to mentions, DMs, name mentions, questions, or greetings
        if bot_mentioned or is_dm or name_mentioned or has_question or has_greeting:
            self.logger.info(f"🤖 Astra responding to {message.author} in {message.guild.name if message.guild else 'DM'}")
            await self.handle_companion_interaction(message)

    async def handle_companion_interaction(self, message: discord.Message):
        """Handle companion interaction with Astra personality"""
        try:
            start_time = time.perf_counter()
            self.logger.info(f"🎯 Processing companion interaction from {message.author}")

            # Get user personality profile
            profile = await self.get_personality_profile(
                message.author.id, message.guild.id if message.guild else 0
            )
            self.logger.debug(f"✅ Got personality profile for {message.author}")

            # Enhanced context analysis
            context = await self._analyze_message_context(message)
            self.logger.debug(f"✅ Analyzed message context: mood={context.get('user_mood', 'unknown')}")

            # Update personality modifiers with enhanced data
            profile.modifiers.user_mood = context["user_mood"]
            profile.modifiers.conversation_tone = context["conversation_tone"]
            profile.modifiers.time_of_day = context["time_of_day"]
            profile.modifiers.channel_type = context["channel_type"]
            profile.modifiers.interaction_history += 1

            # Calculate current personality with enhanced context
            current_personality = self.calculate_personality_vector(profile, context)
            self.logger.debug(f"✅ Calculated personality vector")

            # Generate response using enhanced Astra personality
            self.logger.info(f"🧠 Generating AI response for: '{message.content[:50]}...'")
            response = await self.generate_astra_response(message, profile, context)
            
            if response:
                self.logger.info(f"✅ Generated response: '{response[:50]}...'")
            else:
                self.logger.warning(f"❌ No response generated for message from {message.author}")

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
            self.logger.error(f"❌ Error in companion interaction: {e}")
            import traceback
            self.logger.error(f"📋 Full traceback: {traceback.format_exc()}")
            await message.reply(
                "I'm having a moment of confusion, but I'm here for you! 🤖",
                mention_author=False,
            )

    @tasks.loop(minutes=30)
    async def personality_sync_task(self):
        """Sync personality profiles to database"""
        try:
            for profile_key, profile in self.user_profiles.items():
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

                await self.db.set("user_profiles", profile_key, profile_data)

            self.logger.info(f"Synced {len(self.user_profiles)} personality profiles")

        except Exception as e:
            self.logger.error(f"Error syncing personality profiles: {e}")

    # Slash Commands
    @app_commands.command(
        name="test-astra",
        description="🧪 Test Astra's response system (debug command)",
    )
    async def test_astra(self, interaction: discord.Interaction, message: str = "Hello Astra!"):
        """Test Astra's AI response system"""
        try:
            await interaction.response.defer()
            self.logger.info(f"🧪 Testing Astra response system with: '{message}'")
            
            # Create a mock message object
            class MockMessage:
                def __init__(self, content, author, guild, channel):
                    self.content = content
                    self.author = author
                    self.guild = guild
                    self.channel = channel
            
            mock_message = MockMessage(message, interaction.user, interaction.guild, interaction.channel)
            
            # Get personality profile
            profile = await self.get_personality_profile(interaction.user.id, interaction.guild.id)
            context = await self._analyze_message_context(mock_message)
            
            # Generate response
            response = await self.generate_astra_response(mock_message, profile, context)
            
            embed = discord.Embed(
                title="🧪 Astra Response Test",
                color=0x7C4DFF,
                timestamp=datetime.now()
            )
            embed.add_field(name="Input", value=f"```{message}```", inline=False)
            embed.add_field(name="Output", value=f"```{response or 'No response generated'}```", inline=False)
            
            if response:
                embed.color = 0x00FF00
                embed.add_field(name="Status", value="✅ Success", inline=True)
            else:
                embed.color = 0xFF0000
                embed.add_field(name="Status", value="❌ Failed", inline=True)
                
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"❌ Test command error: {e}")
            import traceback
            self.logger.error(f"📋 Traceback: {traceback.format_exc()}")
            
            embed = discord.Embed(
                title="❌ Test Failed",
                description=f"Error: {str(e)}",
                color=0xFF0000
            )
            await interaction.followup.send(embed=embed)

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
            # Show current personality with enhanced system info
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

            # Add interaction history and system context
            interaction_count = profile.modifiers.interaction_history
            relationship_level = (
                "New Friend" if interaction_count < 5
                else "Good Friend" if interaction_count < 20
                else "Close Friend" if interaction_count < 50
                else "Best Friend"
            )
            
            embed.add_field(
                name="� Your Relationship with Astra",
                value=f"**Level:** {relationship_level}\n**Interactions:** {interaction_count}\n**Last Mood:** {profile.modifiers.user_mood:.1f}/1.0\n**Channel Preference:** {profile.modifiers.channel_type.title()}",
                inline=True,
            )
            
            # System awareness - show AI client status
            ai_status = "🟢 Online" if self.ai_client.is_available() else "🔴 Offline"
            ai_provider = self.ai_client.provider.value if hasattr(self.ai_client, 'provider') else "Unknown"
            
            embed.add_field(
                name="🤖 AI System Status",
                value=f"**Status:** {ai_status}\n**Provider:** {ai_provider}\n**Active Users:** {len(self.user_profiles)}\n**Total Commands:** {len(self.bot.tree.get_commands())}",
                inline=True,
            )

            embed.add_field(
                name="💡 Available Commands",
                value="• `/companion preset:` - Apply personality preset\n• `/ai_status` - Check AI system status\n• `/system_status` - Full system diagnostics\n• `/commands_list` - View all bot commands",
                inline=False,
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="system_status",
        description="🖥️ Comprehensive Astra system status and diagnostics",
    )
    async def system_status_command(self, interaction: discord.Interaction):
        """Show comprehensive system status and diagnostics"""
        await interaction.response.defer()
        
        try:
            # Gather system information
            start_time = time.perf_counter()
            
            # Get bot commands count
            bot_commands = self.bot.tree.get_commands()
            total_slash_commands = len(bot_commands)
            
            # Get loaded cogs and their commands
            loaded_cogs = list(self.bot.cogs.keys())
            cog_command_counts = {}
            for cog_name, cog in self.bot.cogs.items():
                cog_commands = [cmd for cmd in bot_commands if hasattr(cmd, 'callback') and cmd.callback.__module__.endswith(cog_name.lower())]
                cog_command_counts[cog_name] = len(cog_commands)
            
            # AI Client status
            ai_client_available = self.ai_client.is_available()
            ai_provider = self.ai_client.provider.value if hasattr(self.ai_client, 'provider') else "Unknown"
            ai_model = getattr(self.ai_client, 'model', 'Unknown')
            
            # Performance metrics
            avg_response_time = (
                sum(self.response_times) / len(self.response_times)
                if self.response_times
                else 0
            )
            
            # System performance
            try:
                import psutil
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                system_metrics_available = True
            except ImportError:
                cpu_percent = 0.0
                memory_percent = 0.0
                system_metrics_available = False
            
            # Database status
            try:
                db_healthy = await self._check_database_health()
            except:
                db_healthy = False
            
            embed = discord.Embed(
                title="�️ Astra System Status",
                description="Comprehensive system diagnostics and performance metrics",
                color=0x00FF00 if ai_client_available and db_healthy else 0xFFAA00,
                timestamp=datetime.now(),
            )
            
            # System Overview
            embed.add_field(
                name="🤖 Bot System",
                value=f"**Loaded Cogs:** {len(loaded_cogs)}\n**Total Commands:** {total_slash_commands}\n**Uptime:** {self._get_uptime()}\n**Latency:** {self.bot.latency*1000:.1f}ms",
                inline=True,
            )
            
            # AI System Status
            ai_status_icon = "🟢" if ai_client_available else "🔴"
            embed.add_field(
                name=f"{ai_status_icon} AI System",
                value=f"**Provider:** {ai_provider}\n**Model:** {ai_model}\n**Status:** {'Online' if ai_client_available else 'Offline'}\n**Avg Response:** {avg_response_time:.2f}s",
                inline=True,
            )
            
            # Database & Storage
            db_status_icon = "🟢" if db_healthy else "🔴"
            embed.add_field(
                name=f"{db_status_icon} Database",
                value=f"**Status:** {'Healthy' if db_healthy else 'Issues'}\n**Profiles:** {len(self.user_profiles)}\n**Contexts:** {len(self.conversation_contexts)}\n**Interactions:** {self.interaction_count:,}",
                inline=True,
            )
            
            # Performance Metrics
            perf_value = f"**Response Time:** {avg_response_time:.2f}s\n**Success Rate:** {self._calculate_success_rate():.1f}%"
            if system_metrics_available:
                perf_value = f"**CPU Usage:** {cpu_percent:.1f}%\n**Memory:** {memory_percent:.1f}%\n" + perf_value
            else:
                perf_value = "**System Metrics:** Unavailable\n" + perf_value
                
            embed.add_field(
                name="⚡ Performance",
                value=perf_value,
                inline=True,
            )
            
            # Top Cogs by Command Count
            top_cogs = sorted(cog_command_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            cog_stats = "\n".join([f"**{cog}:** {count} commands" for cog, count in top_cogs])
            embed.add_field(
                name="📊 Top Cogs",
                value=cog_stats if cog_stats else "No command data",
                inline=True,
            )
            
            # System Health Summary
            health_indicators = []
            if ai_client_available: health_indicators.append("🟢 AI Online")
            else: health_indicators.append("🔴 AI Offline")
            
            if db_healthy: health_indicators.append("🟢 DB Healthy")
            else: health_indicators.append("🔴 DB Issues")
            
            if cpu_percent < 80: health_indicators.append("🟢 CPU Good")
            else: health_indicators.append("🟡 CPU High")
            
            if memory_percent < 80: health_indicators.append("🟢 Memory Good")
            else: health_indicators.append("🟡 Memory High")
            
            embed.add_field(
                name="🏥 Health Status",
                value="\n".join(health_indicators),
                inline=True,
            )
            
            # Add footer with scan time
            scan_time = time.perf_counter() - start_time
            embed.set_footer(text=f"System scan completed in {scan_time:.3f}s • Astra v2.0.0")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in system_status command: {e}")
            error_embed = discord.Embed(
                title="❌ System Status Error",
                description=f"Unable to retrieve system status: {str(e)}",
                color=0xFF0000
            )
            await interaction.followup.send(embed=error_embed)

    async def _check_database_health(self) -> bool:
        """Check database connectivity and health"""
        try:
            # Simple connectivity test
            await self.db.get("health", "test", {})
            return True
        except:
            return False
    
    def _get_uptime(self) -> str:
        """Get bot uptime in human readable format"""
        try:
            # Try to get uptime from bot if available
            if hasattr(self.bot, 'start_time'):
                uptime = datetime.now() - self.bot.start_time
            else:
                # Fallback calculation
                uptime = timedelta(seconds=0)
            
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            if days > 0:
                return f"{days}d {hours}h {minutes}m"
            elif hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        except:
            return "Unknown"
    
    def _calculate_success_rate(self) -> float:
        """Calculate AI response success rate"""
        if self.interaction_count == 0:
            return 100.0
        
        # Estimate success rate based on response times (if we have responses, they were successful)
        if len(self.response_times) > 0:
            success_rate = (len(self.response_times) / max(self.interaction_count, len(self.response_times))) * 100
            return min(success_rate, 100.0)
        
        return 95.0  # Default estimate

    @app_commands.command(
        name="commands_list",
        description="📝 List all available bot commands by category",
    )
    async def commands_list_command(self, interaction: discord.Interaction):
        """Show comprehensive list of all bot commands"""
        await interaction.response.defer()
        
        try:
            # Get all slash commands
            bot_commands = self.bot.tree.get_commands()
            
            # Organize commands by cog
            cog_commands = {}
            uncategorized_commands = []
            
            for cmd in bot_commands:
                # Try to determine which cog the command belongs to
                cog_name = "Unknown"
                if hasattr(cmd, 'callback') and cmd.callback:
                    callback_module = cmd.callback.__module__
                    if 'cogs.' in callback_module:
                        cog_name = callback_module.split('cogs.')[1].replace('_', ' ').title()
                    
                    # Find the actual cog instance
                    for cog_key, cog_instance in self.bot.cogs.items():
                        if callback_module.endswith(cog_key.lower()) or cog_key.lower() in callback_module:
                            cog_name = cog_key
                            break
                
                if cog_name not in cog_commands:
                    cog_commands[cog_name] = []
                
                # Format command info
                cmd_info = f"`/{cmd.name}` - {cmd.description[:50]}{'...' if len(cmd.description) > 50 else ''}"
                cog_commands[cog_name].append(cmd_info)
            
            # Create embed with command categories
            embed = discord.Embed(
                title="📝 Astra Bot Commands",
                description=f"Complete list of {len(bot_commands)} available slash commands",
                color=0x7289DA,
                timestamp=datetime.now(),
            )
            
            # Add commands by cog (limit to prevent embed size issues)
            command_count = 0
            for cog_name, commands in sorted(cog_commands.items()):
                if command_count >= 20:  # Discord embed field limit
                    remaining_cogs = len(cog_commands) - len([c for c in cog_commands if c in [field.name for field in embed.fields]])
                    embed.add_field(
                        name="📋 Additional Commands",
                        value=f"**{remaining_cogs}** more command categories available.\nUse `/system_status` for detailed system info.",
                        inline=False
                    )
                    break
                
                if len(commands) > 0:
                    # Limit commands per cog to prevent oversized embeds
                    cmd_list = commands[:5]  # Show first 5 commands per cog
                    if len(commands) > 5:
                        cmd_list.append(f"... and {len(commands) - 5} more")
                    
                    embed.add_field(
                        name=f"🔧 {cog_name} ({len(commands)})",
                        value="\n".join(cmd_list),
                        inline=False
                    )
                    command_count += 1
            
            # Add summary footer
            total_cogs = len([cog for cog in self.bot.cogs.keys()])
            embed.set_footer(text=f"Total: {len(bot_commands)} commands across {total_cogs} modules • Use /help for detailed command info")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in commands_list command: {e}")
            error_embed = discord.Embed(
                title="❌ Commands List Error",
                description=f"Unable to retrieve commands list: {str(e)}",
                color=0xFF0000
            )
            await interaction.followup.send(embed=error_embed)

    @app_commands.command(
        name="ai_status",
        description="🤖 Detailed AI client status and configuration",
    )
    async def ai_status_command(self, interaction: discord.Interaction):
        """Show detailed AI client status and configuration"""
        try:
            embed = discord.Embed(
                title="🤖 Astra AI Client Status",
                description="Detailed information about the AI system configuration",
                color=0x00FF00 if self.ai_client.is_available() else 0xFF0000,
                timestamp=datetime.now(),
            )
            
            # Basic AI Status
            status_icon = "🟢" if self.ai_client.is_available() else "🔴"
            provider = self.ai_client.provider.value if hasattr(self.ai_client, 'provider') else "Unknown"
            model = getattr(self.ai_client, 'model', 'Unknown')
            
            embed.add_field(
                name=f"{status_icon} Connection Status",
                value=f"**Available:** {'Yes' if self.ai_client.is_available() else 'No'}\n**Provider:** {provider}\n**Model:** {model}",
                inline=True,
            )
            
            # AI Configuration
            temperature = getattr(self.ai_client, 'temperature', 0.7)
            max_tokens = getattr(self.ai_client, 'max_tokens', 2000)
            
            embed.add_field(
                name="⚙️ Configuration",
                value=f"**Temperature:** {temperature}\n**Max Tokens:** {max_tokens:,}\n**Context Messages:** {getattr(self.ai_client, 'max_context_messages', 8)}",
                inline=True,
            )
            
            # AI Features
            features = []
            if getattr(self.ai_client, 'enable_emotional_intelligence', False):
                features.append("🧠 Emotional Intelligence")
            if getattr(self.ai_client, 'enable_topic_tracking', False):
                features.append("📊 Topic Tracking")
            if getattr(self.ai_client, 'enable_memory_system', False):
                features.append("💾 Memory System")
            
            embed.add_field(
                name="✨ Features",
                value="\n".join(features) if features else "Basic AI responses",
                inline=True,
            )
            
            # Performance Stats
            total_contexts = len(getattr(self.ai_client, 'conversation_contexts', {}))
            total_memories = len(getattr(self.ai_client, 'user_memories', {}))
            
            embed.add_field(
                name="📊 AI Performance",
                value=f"**Active Contexts:** {total_contexts}\n**User Memories:** {total_memories}\n**Avg Response:** {sum(self.response_times) / len(self.response_times) if self.response_times else 0:.2f}s",
                inline=True,
            )
            
            # Provider-specific info
            if hasattr(self.ai_client, 'config') and provider in self.ai_client.config:
                config = self.ai_client.config[self.ai_client.provider]
                embed.add_field(
                    name="🔗 Provider Details",
                    value=f"**Base URL:** {config.get('base_url', 'Unknown')}\n**Default Model:** {config.get('default_model', 'Unknown')}",
                    inline=True,
                )
            
            # Health Check
            try:
                # Quick health check
                health_check_start = time.perf_counter()
                await self.ai_client.test_connection() if hasattr(self.ai_client, 'test_connection') else True
                health_check_time = time.perf_counter() - health_check_start
                health_status = f"🟢 Healthy ({health_check_time:.3f}s)"
            except:
                health_status = "🔴 Connection Issues"
            
            embed.add_field(
                name="🏥 Health Check",
                value=health_status,
                inline=True,
            )
            
            embed.set_footer(text="Astra AI Client • Real-time status")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            self.logger.error(f"Error in ai_status command: {e}")
            error_embed = discord.Embed(
                title="❌ AI Status Error",
                description=f"Unable to retrieve AI status: {str(e)}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

    @app_commands.command(
        name="companion_stats",
        description="�📊 View Astra companion performance statistics",
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
            value=f"**Avg Response:** {avg_response_time:.2f}s\n**Success Rate:** {self._calculate_success_rate():.1f}%",
            inline=True,
        )

        embed.add_field(
            name="🧠 Personality System",
            value=f"**Profiles:** {len(self.user_profiles)}\n**Contexts:** {len(self.conversation_contexts)}",
            inline=True,
        )

        # AI Client Information
        ai_status = "🟢 Online" if self.ai_client.is_available() else "🔴 Offline"
        ai_provider = self.ai_client.provider.value if hasattr(self.ai_client, 'provider') else "Unknown"
        embed.add_field(
            name="🤖 AI Client",
            value=f"**Status:** {ai_status}\n**Provider:** {ai_provider}",
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
            context = await self._analyze_message_context(mock_message)

            response = await self.generate_astra_response(
                mock_message, profile, context
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
