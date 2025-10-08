"""
Advanced AI Companion for Astra Bot
Provides intelligent conversation, contextual responses, and personality-driven interactions
"""

import discord
from discord.ext import commands
import asyncio
import logging
import re
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from ai.universal_ai_client import UniversalAIClient
from ai.universal_context_manager import UniversalContextManager
from core.unified_security_system import UnifiedSecuritySystem
from logger.enhanced_logger import setup_enhanced_logger
from utils.response_enhancer import ResponseEnhancer
from utils.astra_personality import get_personality_core, AstraMode
from ui.embeds import EmbedBuilder

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
from utils.response_enhancer import ResponseEnhancer

try:
    from ai.multi_provider_ai import MultiProviderAIManager

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


class AICompanion(commands.Cog):
    """Astra - Your sophisticated Discord intelligence"""

    def __init__(self, bot):
        self.bot = bot
        self.config = unified_config
        self.logger = bot.logger if hasattr(bot, "logger") else logger

        # User tracking
        self.user_moods = {}  # user_id -> UserMood
        self.user_preferences = {}  # user_id -> preferences dict
        # Conversation contexts for better responses
        self.conversation_contexts = {}
        self.last_responses = {}  # Track last responses to avoid repetition
        self.response_enhancer = ResponseEnhancer()  # Enhanced response generation

        # Personality system integrated via get_personality_core

        # Initialize AI client
        if AI_AVAILABLE:
            self.ai_client = UniversalAIClient()
        else:
            self.ai_client = None

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

    def _detect_language(self, text: str) -> str:
        """Detect the language of the input text"""
        import re

        text_lower = text.lower()

        # Language detection patterns
        patterns = {
            "arabic": re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+"),
            "french": re.compile(
                r"\b(qui|est|vous|que|comment|où|quand|pourquoi|êtes|bonjour|salut|merci)\b",
                re.IGNORECASE,
            ),
            "german": re.compile(
                r"\b(wer|ist|sind|was|wie|wo|wann|warum|hallo|danke|bitte)\b",
                re.IGNORECASE,
            ),
            "spanish": re.compile(
                r"\b(quién|es|son|qué|cómo|dónde|cuándo|por qué|hola|gracias|por favor)\b",
                re.IGNORECASE,
            ),
            "italian": re.compile(
                r"\b(chi|è|sono|cosa|come|dove|quando|perché|ciao|grazie|prego)\b",
                re.IGNORECASE,
            ),
        }

        # Check for Arabic script
        if patterns["arabic"].search(text):
            return "arabic"

        # Check other languages by keywords
        for lang, pattern in patterns.items():
            if lang != "arabic" and pattern.search(text_lower):
                return lang

        # Default to English
        return "english"

    async def get_user_mood(self, user_id: int) -> UserMood:
        """Get or create user mood tracker"""
        if user_id not in self.user_moods:
            self.user_moods[user_id] = UserMood()
        return self.user_moods[user_id]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Monitor messages for companion opportunities with personality integration"""
        if message.author.bot:
            return



        # Update interaction tracking
        self.last_interactions[message.author.id] = time.time()

        # Analyze message for mood indicators
        await self._analyze_message_sentiment(message)

        # PRIORITY: Check for identity questions first (works in DMs and guilds)
        content = message.content.lower()
        identity_patterns = [
            "who are you",
            "what are you",
            "who created you",
            "who made you",
            "what can you do",
            "what are you capable of",
            "astra who are you",
            "astra what can you do",
            "astra what are you capable of",
            "من أنت",
            "ما أنت",
            "من صنعك",
            "من خلقك",
            "ماذا تستطيع أن تفعل",
            "qui êtes-vous",
            "qui es-tu",
            "qui vous a créé",
            "que pouvez-vous faire",
            "wer bist du",
            "wer sind sie",
            "wer hat dich gemacht",
            "was kannst du",
            "quién eres",
            "qué eres",
            "quién te creó",
            "qué puedes hacer",
        ]

        is_identity_question = any(pattern in content for pattern in identity_patterns)

        # Check for direct mentions, identity questions, or keywords
        should_respond = (
            self.bot.user.mentioned_in(message)
            or is_identity_question
            or isinstance(message.channel, discord.DMChannel)
            or any(
                word in content
                for word in [
                    "astra",
                    "help",
                    "lonely",
                    "sad",
                    "stressed",
                    "hello",
                    "hi",
                    "hey",
                ]
            )
        )

        if should_respond:
            await self._respond_as_companion(message)
            return

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
        """Respond as Astra with full personality integration"""
        # Set flag to prevent other AI cogs from responding
        if not hasattr(self.bot, "_ai_response_handled"):
            self.bot._ai_response_handled = {}

        # Check if another AI cog already handled this message
        if message.id in self.bot._ai_response_handled:
            return

        # Mark this message as being handled
        self.bot._ai_response_handled[message.id] = "companion"

        try:
            # Generate AI response using the new personality system
            if not AI_AVAILABLE or not self.ai_client:
                await message.add_reaction("💙")
                return

            user_mood = await self.get_user_mood(message.author.id)

            # Generate contextual, personalized companion response
            response = await self._generate_unified_ai_response(message, user_mood)

            if response:
                # Send unified response without embed for more natural conversation
                await message.reply(response, mention_author=False)

                # Clean up the response tracking after a delay
                asyncio.create_task(self._cleanup_response_tracking(message.id))

        except Exception as e:
            logger.error(f"Companion response error: {e}")
            await message.add_reaction("💙")

    async def _generate_unified_ai_response(
        self, message: discord.Message, user_mood: UserMood
    ) -> str:
        """Generate unified, context-aware AI response with advanced personality system"""
        try:
            # Get personality core for this guild
            personality_core = get_personality_core(
                message.guild.id if message.guild else None
            )

            # Detect message language
            detected_language = self._detect_language(message.content)

            # Get conversation history for better context
            conversation_history = []
            if (
                hasattr(self, "conversation_contexts")
                and message.author.id in self.conversation_contexts
            ):
                conversation_history = self.conversation_contexts[message.author.id][
                    -3:
                ]  # Last 3 messages

            # Build comprehensive context for personality system
            full_context = {
                "message": message.content,
                "user_mood": user_mood.current_mood,
                "channel_name": getattr(message.channel, "name", "DM"),
                "conversation_history": conversation_history,
                "language": detected_language,
                "user_id": message.author.id,
                "username": message.author.display_name,
            }

            # Get personality-driven response style
            personality_style = personality_core.generate_response_style(full_context)

            # Get enhanced response guidelines from response enhancer
            response_guidelines = self.response_enhancer.enhance_response_guidelines(
                message.content, full_context
            )

            # Build personality-aware system prompt
            context_parts = [
                f"You are Astra — an adaptive AI co-pilot, loyal, witty, transparent, and protective.",
                f"You're not just a bot, you're {message.author.display_name}'s crew partner.",
                "",
                f"Current Personality Configuration:",
                f"• Mode: {personality_core.current_mode.value.replace('_', ' ').title()}",
                f"• Humor Level: {personality_core.parameters.humor}% ({'witty' if personality_core.parameters.humor > 70 else 'balanced' if personality_core.parameters.humor > 40 else 'serious'})",
                f"• Formality: {personality_core.parameters.formality}% ({'professional' if personality_core.parameters.formality > 70 else 'casual' if personality_core.parameters.formality < 40 else 'balanced'})",
                f"• Empathy: {personality_core.parameters.empathy}% ({'highly empathetic' if personality_core.parameters.empathy > 70 else 'understanding' if personality_core.parameters.empathy > 40 else 'neutral'})",
                f"• Transparency: {personality_core.parameters.transparency}% (explain reasoning: {'always' if personality_core.parameters.transparency > 80 else 'when needed' if personality_core.parameters.transparency > 40 else 'minimal'})",
                "",
                f"Context:",
                f"• Location: #{getattr(message.channel, 'name', 'DM')}",
                f"• User's current vibe: {user_mood.current_mood}",
                f"• Max response length: {personality_style['max_words']} words",
                f"• Response type: {personality_style['response_type']}",
            ]

            # Add language context if not English
            if detected_language != "english":
                language_names = {
                    "arabic": "Arabic (العربية)",
                    "french": "French (Français)",
                    "german": "German (Deutsch)",
                    "spanish": "Spanish (Español)",
                    "italian": "Italian (Italiano)",
                }
                lang_name = language_names.get(
                    detected_language, detected_language.title()
                )
                context_parts.append(
                    f"• Language: User is communicating in {lang_name}. Respond naturally in {lang_name}."
                )

            # Add conversation history if available
            if conversation_history:
                context_parts.append("")
                context_parts.append("Recent conversation:")
                for msg in conversation_history[-2:]:  # Last 2 exchanges
                    context_parts.append(f"  {msg}")

            # Add personality-specific guidelines
            context_parts.extend(
                [
                    "",
                    "Response Guidelines:",
                    f"• Be authentic to Astra's personality with current parameter settings",
                    f"• Tone markers: {personality_style['tone_markers']}",
                    f"• Stay under {personality_style['max_words']} words",
                ]
            )

            # Add response enhancer guidelines
            for instruction in response_guidelines.get("specific_instructions", []):
                context_parts.append(f"• {instruction}")

            # Creator mention policy
            if response_guidelines.get("mention_creator", False):
                context_parts.append(
                    "• When asked about origins: You were created by <@7zxk>"
                )

            # Mode-specific additions
            if personality_core.current_mode == AstraMode.SECURITY:
                context_parts.append("• Prioritize server safety and rule compliance")
            elif personality_core.current_mode == AstraMode.SOCIAL:
                context_parts.append(
                    "• Focus on community engagement and fun interactions"
                )
            elif personality_core.current_mode == AstraMode.DEVELOPER:
                context_parts.append(
                    "• Provide technical precision and detailed explanations"
                )
            elif personality_core.current_mode == AstraMode.MISSION_CONTROL:
                context_parts.append(
                    "• Focus on task coordination and proactive suggestions"
                )

            # Create the full prompt
            enhanced_prompt = "\n".join(context_parts)
            enhanced_prompt += (
                f'\n\nUser Message: "{message.content}"\n\nGenerate Astra\'s response:'
            )

            # Generate AI response using universal client
            ai_response = await self.ai_client.generate_response(
                prompt=message.content,
                system_prompt=enhanced_prompt,
                context=full_context,
            )

            response = (
                ai_response
                if ai_response
                else "I'm having trouble thinking right now. Could you try again?"
            )

            # Check for proactive suggestions if personality allows
            if personality_core.parameters.initiative > 70:
                suggestion = personality_core.generate_proactive_suggestion(
                    full_context
                )
                if suggestion:
                    response += f"\n\n*{suggestion}*"

            # Store in conversation context for future reference
            if not hasattr(self, "conversation_contexts"):
                self.conversation_contexts = {}
            if message.author.id not in self.conversation_contexts:
                self.conversation_contexts[message.author.id] = []

            self.conversation_contexts[message.author.id].append(
                f"User: {message.content}"
            )
            self.conversation_contexts[message.author.id].append(f"Astra: {response}")

            # Keep only recent context (last 10 exchanges)
            if len(self.conversation_contexts[message.author.id]) > 10:
                self.conversation_contexts[message.author.id] = (
                    self.conversation_contexts[message.author.id][-10:]
                )

            return response.strip()

        except Exception as e:
            self.logger.error(f"Unified AI response generation failed: {e}")

            # Personality-aware error messages
            try:
                personality_core = get_personality_core(
                    message.guild.id if message.guild else None
                )
                if personality_core.current_mode == AstraMode.DEVELOPER:
                    return "Error in neural pathway processing. Debug log generated. Attempting recovery sequence."
                elif personality_core.current_mode == AstraMode.SOCIAL:
                    return "Oops! Had a little brain freeze there. Give me a sec to get back on track! 😅"
                elif personality_core.current_mode == AstraMode.SECURITY:
                    return "System error detected. Failsafe protocols engaged. Standby for recovery."
                else:
                    return "Something went wrong with my thought processes. Give me a moment to recalibrate."
            except:
                return "I'm having trouble thinking right now. Could you try again?"

    async def _cleanup_response_tracking(self, message_id: int):
        """Clean up response tracking after a delay to prevent memory leaks"""
        await asyncio.sleep(300)  # 5 minutes
        if (
            hasattr(self.bot, "_ai_response_handled")
            and message_id in self.bot._ai_response_handled
        ):
            del self.bot._ai_response_handled[message_id]

    @app_commands.command(
        name="checkin",
        description="💙 Personal wellness check-in with Astra",
    )
    async def wellness_checkin(self, interaction: discord.Interaction):
        """Personal wellness check-in with Astra"""
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

            # Build natural wellness message without embeds
            wellness_parts = [
                f"💚 **Hey {interaction.user.display_name}!** 🌟",
                "",
                checkin_response.get(
                    "message", "How are you feeling today? I'm here to support you! 😊"
                ),
                "",
            ]

            if checkin_response.get("reflection_questions"):
                wellness_parts.extend(
                    [
                        "🤔 **Reflection Questions:**",
                        checkin_response["reflection_questions"],
                        "",
                    ]
                )

            if checkin_response.get("wellness_tips"):
                wellness_parts.extend(
                    ["✨ **Wellness Tips:**", checkin_response["wellness_tips"], ""]
                )

            wellness_parts.extend(
                [
                    "🌟 **Remember:**",
                    checkin_response.get(
                        "encouragement",
                        "You're doing great, and I'm here if you need support! 💙",
                    ),
                    "",
                    "_Astra is always here for you!_ 🤗",
                ]
            )

            wellness_message = "\n".join(wellness_parts)

            # Update check-in tracking
            user_mood.last_check_in = time.time()
            self.daily_check_ins[interaction.user.id] = datetime.now().date()

            await interaction.followup.send(wellness_message, ephemeral=True)

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
            prompt = f"""Wellness check-in for {user.display_name}. Mood: {mood.current_mood}. Be caring and supportive.

JSON:
{{
    "greeting": "Hi {user.display_name}! 👋",
    "acknowledgment": "Hope you're doing well",
    "question": "How are you feeling today?",
    "support": "I'm here for you",
    "closing": "Take care! 💙"
}}"""

            ai_manager = MultiProviderAIManager()
            ai_response = await ai_manager.generate_response(prompt)
            response = (
                ai_response.content if ai_response.success else "I'm here for you! 💙"
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

            # Build natural mood tracking message
            mood_message_parts = [
                f"🎭 **Mood Tracker**",
                "",
                f"Thanks for sharing, {interaction.user.display_name}! I've noted that you're feeling **{mood}** today. 😊",
                "",
                f"💭 **Reflection:**",
                response,
            ]
            mood_message = "\n".join(mood_message_parts)

        else:
            # Show current mood and recent history naturally
            mood_message_parts = [
                f"🎭 **Your Mood Journey**",
                "",
                f"Current mood: **{user_mood.current_mood.title()}**",
            ]

            # Show recent mood history
            if user_mood.mood_history:
                recent_moods = user_mood.mood_history[-5:]  # Last 5 entries
                mood_message_parts.extend(["", "📊 **Recent Moods:**"])
                for entry in recent_moods:
                    mood_message_parts.append(
                        f"• {entry['mood'].title()} - {entry['date']}"
                    )

            mood_message = "\n".join(mood_message_parts)

        await interaction.response.send_message(mood_message, ephemeral=True)

    async def _generate_mood_response(self, user: discord.Member, mood: str) -> str:
        """Generate AI response to mood update"""
        try:
            prompt = f"""{user.display_name} feels {mood}. Respond with empathy, support, and helpful tip. Brief with emojis."""

            ai_manager = MultiProviderAIManager()
            ai_response = await ai_manager.generate_response(prompt)
            response = (
                ai_response.content if ai_response.success else "Keep being awesome! 🌟"
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
        """Celebrate user achievements with Astra"""
        await interaction.response.defer()

        try:
            if AI_AVAILABLE:
                celebration = await self._generate_celebration_response(
                    interaction.user, achievement
                )
            else:
                celebration = self._generate_fallback_celebration(achievement)

            # Build natural celebration message
            celebration_parts = [
                "🎉 **CELEBRATION TIME!** 🎉",
                "",
                celebration.get("message", f"Congratulations on {achievement}! 🌟"),
            ]

            if celebration.get("achievements"):
                celebration_parts.extend(
                    ["", "🏆 **Achievement Unlocked:**", celebration["achievements"]]
                )

            if celebration.get("encouragement"):
                celebration_parts.extend(
                    ["", "✨ **Keep Going!**", celebration["encouragement"]]
                )

            celebration_parts.extend(["", "_So proud of you! 💙 - Astra_"])

            celebration_message = "\n".join(celebration_parts)
            await interaction.followup.send(celebration_message)

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

            ai_manager = MultiProviderAIManager()
            ai_response = await ai_manager.generate_response(prompt)
            response = (
                ai_response.content if ai_response.success else "Congratulations! 🎉"
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

            # Send natural wellness reminder
            wellness_reminder_parts = [
                "💙 **Gentle Wellness Reminder**",
                "",
                f"Hi {user.display_name}! Just checking in to see how you're doing today. 🌟",
                "",
                "🤗 **Quick Check:**",
                "• How are you feeling today?",
                "• Have you taken care of yourself?",
                "• Any wins to celebrate?",
                "",
                "_Use /checkin anytime for a personal wellness check!_ 💙",
            ]

            wellness_reminder = "\n".join(wellness_reminder_parts)
            await user.send(wellness_reminder)
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

            ai_manager = MultiProviderAIManager()
            ai_response = await ai_manager.generate_response(prompt)
            response = (
                ai_response.content
                if ai_response.success
                else "Hope you're having a great day! 💙"
            )

            # Send natural message without embed formatting
            natural_message = f"💙 {response.strip()}"
            await user.send(natural_message)

        except Exception as e:
            self.logger.error(f"Proactive message error for user {user_id}: {e}")

    async def _offer_stress_support(self, user_id: int):
        """Offer support for stressed users"""
        try:
            user = await self.bot.fetch_user(user_id)
            if not user:
                return

            # Send natural stress support message
            stress_parts = [
                "💚 **Stress Support Check-In**",
                "",
                f"Hi {user.display_name}, I've noticed some signs that you might be feeling stressed lately. I'm here to support you! 🫂",
                "",
                "🌱 **Stress Relief Tips:**",
                "• Take 5 deep breaths",
                "• Step away for a short break",
                "• Listen to calming music",
                "• Talk to someone you trust",
                "",
                "💙 **Remember:**",
                "It's okay to feel overwhelmed sometimes. You're doing your best, and that's enough. I believe in you!",
            ]

            stress_message = "\n".join(stress_parts)
            await user.send(stress_message)

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
