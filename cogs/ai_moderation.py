"""
Advanced AI-Powered Moderation System for Astra Bot
Sophisticated moderation with personalized AI responses and companion features
"""

import asyncio
import logging
import time
import json
import re
from typing import Dict, List, Optional, Set, Any, Tuple
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from enum import Enum
import discord
from discord import app_commands
from discord.ext import commands, tasks

from config.unified_config import unified_config
from utils.permissions import has_permission, PermissionLevel, check_user_permission

try:
    from ai.multi_provider_ai import MultiProviderAIManager

    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

logger = logging.getLogger("astra.ai_moderation")


class ViolationType(Enum):
    SPAM = "spam"
    CAPS_ABUSE = "caps_abuse"
    MENTION_SPAM = "mention_spam"
    REPEATED_CONTENT = "repeated_content"
    TOXIC_LANGUAGE = "toxic_language"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    LINK_SPAM = "link_spam"
    EMOTIONAL_DISTRESS = "emotional_distress"


class ModerationLevel(Enum):
    FRIENDLY_REMINDER = 1
    WARNING = 2
    TIMEOUT = 3
    KICK = 4
    BAN = 5


class UserProfile:
    """Track user behavior and personality for personalized responses"""

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.personality_traits = {
            "communication_style": "neutral",  # casual, formal, friendly, aggressive
            "responsiveness": "normal",  # high, normal, low
            "emotional_state": "stable",  # stable, stressed, excited, frustrated
            "preferred_tone": "balanced",  # strict, gentle, humorous, supportive
            "learning_preference": "visual",  # visual, text, example-based
        }
        self.interaction_history = []
        self.violation_patterns = defaultdict(int)
        self.positive_interactions = 0
        self.last_violation_time = 0
        self.improvement_streak = 0
        self.preferred_moderator_style = "companion"  # companion, authority, mentor


class AIModeration(commands.Cog):
    """Advanced AI-powered moderation with personalized responses"""

    def __init__(self, bot):
        self.bot = bot
        self.config = unified_config
        self.logger = bot.logger

        # User profiles for personalization
        self.user_profiles = {}

        # Enhanced tracking
        self.message_history = defaultdict(deque)
        self.user_warnings = defaultdict(list)
        self.timeout_history = defaultdict(list)
        self.positive_reinforcement = defaultdict(int)

        # AI-powered detection
        self.toxic_patterns = [
            r"\b(idiot|stupid|dumb|moron|loser)\b",
            r"\b(shut up|stfu|gtfo)\b",
            r"\b(kill yourself|kys)\b",
            r"\b(hate you|hate this)\b",
        ]

        self.supportive_patterns = [
            r"\b(thanks|thank you|appreciated|helpful)\b",
            r"\b(great job|well done|awesome|amazing)\b",
            r"\b(sorry|apologize|my bad|mistake)\b",
        ]

        # Moderation settings
        self.settings = {
            "spam_threshold": 5,
            "spam_timeframe": 10,
            "warning_decay_hours": 24,
            "caps_threshold": 0.7,
            "mention_limit": 5,
            "link_spam_threshold": 3,
            "similarity_threshold": 0.8,
            "ai_response_enabled": True,
            "personalization_enabled": True,
            "companion_mode": True,
            "learning_mode": True,
        }

        # Start background tasks
        self.cleanup_task.start()
        self.analyze_patterns_task.start()

    def cog_unload(self):
        self.cleanup_task.cancel()
        self.analyze_patterns_task.cancel()

    async def get_user_profile(self, user_id: int) -> UserProfile:
        """Get or create user profile for personalization"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(user_id)
        return self.user_profiles[user_id]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Enhanced message monitoring with AI analysis"""
        if not message.guild or message.author.bot:
            return

        # Track positive behavior
        await self._track_positive_behavior(message)

        # Check for violations
        violation = await self._comprehensive_analysis(message)

        if violation:
            await self._handle_violation_with_ai(message, violation)
        else:
            # Occasionally provide positive reinforcement
            await self._random_positive_reinforcement(message)

    async def _comprehensive_analysis(
        self, message: discord.Message
    ) -> Optional[ViolationType]:
        """Comprehensive message analysis using multiple detection methods"""
        user_id = message.author.id
        content = message.content.lower().strip()

        # Update message history
        self.message_history[user_id].append(
            {
                "content": content,
                "timestamp": time.time(),
                "message": message,
                "length": len(content),
                "caps_ratio": self._calculate_caps_ratio(message.content),
            }
        )

        # Keep only recent messages (last 2 minutes)
        current_time = time.time()
        while (
            self.message_history[user_id]
            and current_time - self.message_history[user_id][0]["timestamp"] > 120
        ):
            self.message_history[user_id].popleft()

        # Run detection algorithms
        violations = []

        # 1. Spam Detection
        if await self._detect_spam(user_id):
            violations.append(ViolationType.SPAM)

        # 2. Caps Abuse
        if await self._detect_caps_abuse(message.content):
            violations.append(ViolationType.CAPS_ABUSE)

        # 3. Mention Spam
        if await self._detect_mention_spam(message):
            violations.append(ViolationType.MENTION_SPAM)

        # 4. Repeated Content
        if await self._detect_repeated_content(user_id, content):
            violations.append(ViolationType.REPEATED_CONTENT)

        # 5. Toxic Language (AI-enhanced)
        if await self._detect_toxic_language(content, message):
            violations.append(ViolationType.TOXIC_LANGUAGE)

        # 6. Link Spam
        if await self._detect_link_spam(user_id, content):
            violations.append(ViolationType.LINK_SPAM)

        # 7. Emotional Distress Detection
        if await self._detect_emotional_distress(content):
            violations.append(ViolationType.EMOTIONAL_DISTRESS)

        # Return most severe violation
        if violations:
            severity_order = [
                ViolationType.EMOTIONAL_DISTRESS,
                ViolationType.TOXIC_LANGUAGE,
                ViolationType.SPAM,
                ViolationType.MENTION_SPAM,
                ViolationType.CAPS_ABUSE,
                ViolationType.REPEATED_CONTENT,
                ViolationType.LINK_SPAM,
            ]

            for violation_type in severity_order:
                if violation_type in violations:
                    return violation_type

        return None

    async def _detect_emotional_distress(self, content: str) -> bool:
        """Detect signs of emotional distress for supportive intervention"""
        distress_indicators = [
            r"\b(depressed|suicide|kill myself|end it all|give up|hate myself)\b",
            r"\b(nobody cares|alone|hopeless|worthless|useless)\b",
            r"\b(can\'t take it|too much|overwhelmed|breaking down)\b",
        ]

        for pattern in distress_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    async def _detect_toxic_language(
        self, content: str, message: discord.Message
    ) -> bool:
        """Enhanced toxic language detection with AI assistance"""
        # Pattern-based detection
        for pattern in self.toxic_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True

        # AI-powered toxicity detection if available
        if AI_AVAILABLE and len(content) > 10:
            try:
                ai_analysis = await self._ai_toxicity_analysis(content)
                if ai_analysis and ai_analysis.get("is_toxic", False):
                    return True
            except Exception as e:
                logger.error(f"AI toxicity analysis failed: {e}")

        return False

    async def _ai_toxicity_analysis(self, content: str) -> Optional[Dict]:
        """Use AI to analyze message toxicity"""
        try:
            prompt = f"""Analyze this message for toxicity, harassment, or harmful content. 
Message: "{content}"

Respond in JSON format:
{{
    "is_toxic": true/false,
    "toxicity_level": 1-5,
    "reasons": ["reason1", "reason2"],
    "suggested_response": "supportive message suggestion"
}}"""

            ai_manager = MultiProviderAIManager()
            ai_response = await ai_manager.generate_response(prompt)
            response = ai_response.content if ai_response.success else '{"toxicity_score": 0, "suggested_response": "I\'m here to help moderate our community!"}'

            # Try to extract JSON from response
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

        except Exception as e:
            logger.error(f"AI toxicity analysis error: {e}")

        return None

    async def _handle_violation_with_ai(
        self, message: discord.Message, violation: ViolationType
    ):
        """Handle violation with personalized AI response"""
        user = message.author
        profile = await self.get_user_profile(user.id)

        # Update violation patterns
        profile.violation_patterns[violation.value] += 1
        profile.last_violation_time = time.time()
        profile.improvement_streak = 0

        # Determine moderation level
        warning_count = len(self.user_warnings[user.id])
        mod_level = self._determine_moderation_level(violation, warning_count)

        # Delete message if needed (except for emotional distress)
        if violation != ViolationType.EMOTIONAL_DISTRESS:
            try:
                await message.delete()
            except:
                pass

        # Generate personalized AI response
        if self.settings["ai_response_enabled"] and AI_AVAILABLE:
            ai_response = await self._generate_personalized_response(
                user, violation, mod_level, profile
            )
        else:
            ai_response = await self._generate_fallback_response(
                user, violation, mod_level
            )

        # Send response
        await self._send_moderation_response(
            message.channel, user, ai_response, mod_level
        )

        # Apply consequences
        await self._apply_consequences(user, mod_level, violation)

        # Log action
        self._log_moderation_action(
            user, violation, mod_level, ai_response.get("action_taken")
        )

    async def _generate_personalized_response(
        self,
        user: discord.Member,
        violation: ViolationType,
        mod_level: ModerationLevel,
        profile: UserProfile,
    ) -> Dict[str, Any]:
        """Generate AI-powered personalized moderation response"""
        try:
            # Build context for AI
            context = {
                "user_name": user.display_name,
                "violation_type": violation.value,
                "moderation_level": mod_level.name,
                "personality_traits": profile.personality_traits,
                "violation_history": dict(profile.violation_patterns),
                "improvement_streak": profile.improvement_streak,
                "positive_interactions": profile.positive_interactions,
                "preferred_style": profile.preferred_moderator_style,
            }

            # Special handling for emotional distress
            if violation == ViolationType.EMOTIONAL_DISTRESS:
                return await self._generate_supportive_response(user, profile)

            # Create AI prompt for moderation response
            prompt = f"""You are Astra, a friendly and supportive Discord bot moderator. Generate a personalized moderation response.

Context:
- User: {user.display_name}
- Violation: {violation.value}
- Severity: {mod_level.name}
- User's preferred style: {profile.preferred_moderator_style}
- Communication style: {profile.personality_traits['communication_style']}
- Previous violations: {dict(profile.violation_patterns)}
- Positive interactions: {profile.positive_interactions}

Requirements:
1. Be {profile.preferred_moderator_style} in tone
2. Address the specific violation type
3. Provide constructive guidance
4. Use appropriate emojis
5. Keep it under 200 words
6. Be encouraging while firm

Respond in JSON format:
{{
    "title": "Response title with emoji",
    "message": "Main response message",
    "guidance": "Specific guidance or tip",
    "encouragement": "Positive/encouraging note",
    "action_taken": "What action was taken"
}}"""

            ai_manager = MultiProviderAIManager()
            ai_response_obj = await ai_manager.generate_response(prompt)
            ai_response = ai_response_obj.content if ai_response_obj.success else '{"title": "Community Guidelines Reminder 📝", "message": "Let\'s work together to keep our community positive!", "guidance": "Remember to be respectful", "encouragement": "You\'re part of making this a great space!", "action_taken": "Gentle reminder sent"}'

            # Parse AI response
            json_match = re.search(r"\{.*\}", ai_response, re.DOTALL)
            if json_match:
                parsed_response = json.loads(json_match.group())
                return parsed_response
            else:
                # Fallback parsing
                return {
                    "title": f"🤖 Hey {user.display_name}!",
                    "message": ai_response[:200],
                    "guidance": "Let's keep our community positive!",
                    "encouragement": "You've got this! 💪",
                    "action_taken": f"{mod_level.name.lower()} applied",
                }

        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            return await self._generate_fallback_response(user, violation, mod_level)

    async def _generate_supportive_response(
        self, user: discord.Member, profile: UserProfile
    ) -> Dict[str, Any]:
        """Generate supportive response for emotional distress"""
        try:
            prompt = f"""You are Astra, a compassionate AI companion. A user named {user.display_name} seems to be experiencing emotional distress. 

Generate a supportive, caring response that:
1. Shows empathy and understanding
2. Offers comfort without being preachy
3. Suggests positive resources or actions
4. Uses warm, caring language
5. Includes appropriate emojis
6. Keeps it under 150 words

Respond in JSON format:
{{
    "title": "Supportive title with emoji",
    "message": "Caring, empathetic response",
    "resources": "Helpful suggestions or resources",
    "encouragement": "Uplifting, hopeful message",
    "action_taken": "Supportive outreach"
}}"""

            ai_manager = MultiProviderAIManager()
            ai_response_obj = await ai_manager.generate_response(prompt)
            ai_response = ai_response_obj.content if ai_response_obj.success else '{"title": "We\'re Here for You 💙", "message": "I can see you might be going through something difficult. You\'re not alone, and this community cares about you.", "resources": "Consider talking to a trusted friend, family member, or counselor", "encouragement": "You matter, and things can get better. Take it one day at a time.", "action_taken": "Supportive outreach"}'

            json_match = re.search(r"\{.*\}", ai_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

        except Exception as e:
            logger.error(f"Supportive response generation failed: {e}")

        # Fallback supportive response
        return {
            "title": f"💙 Hey {user.display_name}, I'm here for you",
            "message": "I noticed you might be going through a tough time. Remember that you're valued in this community and you're not alone.",
            "resources": "Consider reaching out to friends, family, or professional support if you need help.",
            "encouragement": "Things can get better, and this community is here to support you. 🤗",
            "action_taken": "Supportive outreach provided",
        }

    async def _generate_fallback_response(
        self, user: discord.Member, violation: ViolationType, mod_level: ModerationLevel
    ) -> Dict[str, Any]:
        """Generate fallback response when AI is unavailable"""
        responses = {
            ViolationType.SPAM: {
                "title": f"⏰ Hey {user.display_name}!",
                "message": "I noticed you're sending messages pretty quickly. Let's slow down a bit to keep the chat readable for everyone!",
                "guidance": "Try to combine your thoughts into fewer, more meaningful messages.",
                "encouragement": "Thanks for being active in our community! 😊",
            },
            ViolationType.CAPS_ABUSE: {
                "title": f"🔤 {user.display_name}, let's tone it down!",
                "message": "Using lots of CAPS can come across as shouting. Let's keep things friendly and conversational!",
                "guidance": "Regular text is easier to read and more welcoming.",
                "encouragement": "Your message matters - you don't need caps to be heard! 👍",
            },
            ViolationType.TOXIC_LANGUAGE: {
                "title": f"🌟 {user.display_name}, let's keep it positive!",
                "message": "I detected some language that might not be welcoming to everyone. Our community thrives on respect and kindness.",
                "guidance": "Try expressing your thoughts in a more constructive way.",
                "encouragement": "You're part of what makes this community great! 💙",
            },
        }

        template = responses.get(violation, responses[ViolationType.SPAM])
        template["action_taken"] = f"{mod_level.name.lower()} applied"
        return template

    async def _send_moderation_response(
        self,
        channel: discord.TextChannel,
        user: discord.Member,
        response: Dict[str, Any],
        mod_level: ModerationLevel,
    ):
        """Send personalized moderation response"""
        embed = discord.Embed(
            title=response.get("title", f"🤖 Hey {user.display_name}!"),
            description=response.get("message", "Please follow community guidelines."),
            color=self._get_color_for_level(mod_level),
            timestamp=datetime.now(timezone.utc),
        )

        if response.get("guidance"):
            embed.add_field(
                name="💡 Quick Tip", value=response["guidance"], inline=False
            )

        if response.get("encouragement"):
            embed.add_field(
                name="✨ Remember", value=response["encouragement"], inline=False
            )

        if response.get("resources"):
            embed.add_field(
                name="🔗 Resources", value=response["resources"], inline=False
            )

        embed.set_footer(text="I'm here to help make our community awesome! 🌟")

        # Send with auto-delete for non-supportive messages
        delete_after = None if mod_level == ModerationLevel.FRIENDLY_REMINDER else 60

        try:
            await channel.send(embed=embed, delete_after=delete_after)
        except Exception as e:
            logger.error(f"Failed to send moderation response: {e}")

    def _get_color_for_level(self, mod_level: ModerationLevel) -> int:
        """Get appropriate color for moderation level"""
        colors = {
            ModerationLevel.FRIENDLY_REMINDER: 0x00FF7F,  # Spring green
            ModerationLevel.WARNING: 0xFFD700,  # Gold
            ModerationLevel.TIMEOUT: 0xFF6B47,  # Orange red
            ModerationLevel.KICK: 0xFF4500,  # Red orange
            ModerationLevel.BAN: 0x8B0000,  # Dark red
        }
        return colors.get(mod_level, 0x00BFFF)

    async def _track_positive_behavior(self, message: discord.Message):
        """Track and reward positive behavior"""
        content = message.content.lower()

        # Check for positive patterns
        positive_score = 0
        for pattern in self.supportive_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                positive_score += 1

        if positive_score > 0:
            profile = await self.get_user_profile(message.author.id)
            profile.positive_interactions += positive_score
            profile.improvement_streak += 1

            # Occasionally acknowledge positive behavior
            if profile.improvement_streak > 0 and profile.improvement_streak % 10 == 0:
                await self._send_positive_reinforcement(
                    message.channel, message.author, profile
                )

    async def _send_positive_reinforcement(
        self, channel: discord.TextChannel, user: discord.Member, profile: UserProfile
    ):
        """Send positive reinforcement message"""
        if not AI_AVAILABLE:
            return

        try:
            prompt = f"""Generate a brief, encouraging message for {user.display_name} who has been showing positive behavior in the community.

They have:
- {profile.positive_interactions} positive interactions
- {profile.improvement_streak} day improvement streak
- Preferred style: {profile.preferred_moderator_style}

Create a warm, appreciative message (under 100 words) with appropriate emojis."""

            ai_manager = MultiProviderAIManager()
            ai_response_obj = await ai_manager.generate_response(prompt)
            ai_response = ai_response_obj.content if ai_response_obj.success else "Thank you for being such a positive presence in our community! Your contributions make this space better for everyone. Keep being awesome! ✨"

            embed = discord.Embed(
                title="🌟 Community Star!",
                description=ai_response,
                color=0x00FF7F,
                timestamp=datetime.now(timezone.utc),
            )

            await channel.send(embed=embed, delete_after=30)

        except Exception as e:
            logger.error(f"Failed to send positive reinforcement: {e}")

    @tasks.loop(hours=1)
    async def cleanup_task(self):
        """Clean up old data and warnings"""
        current_time = time.time()
        decay_threshold = self.settings["warning_decay_hours"] * 3600

        # Clean up warnings
        for user_id in list(self.user_warnings.keys()):
            self.user_warnings[user_id] = [
                warning
                for warning in self.user_warnings[user_id]
                if current_time - warning < decay_threshold
            ]
            if not self.user_warnings[user_id]:
                del self.user_warnings[user_id]

        # Clean up message history
        for user_id in list(self.message_history.keys()):
            while (
                self.message_history[user_id]
                and current_time - self.message_history[user_id][0]["timestamp"] > 7200
            ):  # 2 hours
                self.message_history[user_id].popleft()
            if not self.message_history[user_id]:
                del self.message_history[user_id]

    @tasks.loop(hours=6)
    async def analyze_patterns_task(self):
        """Analyze user patterns and update profiles"""
        if not self.settings["learning_mode"]:
            return

        for user_id, profile in self.user_profiles.items():
            # Update personality traits based on behavior patterns
            await self._update_personality_traits(profile)

    async def _update_personality_traits(self, profile: UserProfile):
        """Update user personality traits based on behavior analysis"""
        # Analyze communication patterns
        if profile.violation_patterns.get("caps_abuse", 0) > 3:
            profile.personality_traits["communication_style"] = "aggressive"
        elif profile.positive_interactions > 20:
            profile.personality_traits["communication_style"] = "friendly"

        # Update preferred moderator style based on response to different approaches
        if profile.improvement_streak > 5:
            profile.preferred_moderator_style = "companion"
        elif profile.violation_patterns.get("repeated_content", 0) > 5:
            profile.preferred_moderator_style = "mentor"

    # Admin commands for moderation management

    @app_commands.command(
        name="userprofile", description="👤 View user moderation profile"
    )
    @app_commands.describe(user="User to check profile for")
    @app_commands.default_permissions(manage_messages=True)
    async def user_profile(
        self, interaction: discord.Interaction, user: discord.Member
    ):
        """View detailed user moderation profile"""
        if not await check_user_permission(
            interaction.user, PermissionLevel.MODERATOR, interaction.guild
        ):
            await interaction.response.send_message(
                "❌ You need moderator permissions for this command.", ephemeral=True
            )
            return

        profile = await self.get_user_profile(user.id)

        embed = discord.Embed(
            title=f"👤 Moderation Profile: {user.display_name}",
            color=0x00BFFF,
            timestamp=datetime.now(timezone.utc),
        )

        embed.add_field(
            name="📊 Behavior Stats",
            value=f"**Positive Interactions:** {profile.positive_interactions}\n"
            f"**Improvement Streak:** {profile.improvement_streak} days\n"
            f"**Active Warnings:** {len(self.user_warnings.get(user.id, []))}\n"
            f"**Last Violation:** {datetime.fromtimestamp(profile.last_violation_time).strftime('%Y-%m-%d %H:%M') if profile.last_violation_time else 'None'}",
            inline=False,
        )

        if profile.violation_patterns:
            violations_text = "\n".join(
                [
                    f"**{vtype.replace('_', ' ').title()}:** {count}"
                    for vtype, count in profile.violation_patterns.items()
                ]
            )
            embed.add_field(
                name="⚠️ Violation History", value=violations_text, inline=True
            )

        embed.add_field(
            name="🎭 Personality Profile",
            value=f"**Communication:** {profile.personality_traits['communication_style'].title()}\n"
            f"**Preferred Style:** {profile.preferred_moderator_style.title()}\n"
            f"**Emotional State:** {profile.personality_traits['emotional_state'].title()}",
            inline=True,
        )

        await interaction.response.send_message(embed=embed)

    # Required detection methods (simplified versions of the originals)
    async def _detect_spam(self, user_id: int) -> bool:
        recent_messages = [
            msg
            for msg in self.message_history[user_id]
            if time.time() - msg["timestamp"] <= self.settings["spam_timeframe"]
        ]
        return len(recent_messages) >= self.settings["spam_threshold"]

    async def _detect_caps_abuse(self, content: str) -> bool:
        if len(content) < 10:
            return False
        caps_ratio = sum(1 for c in content if c.isupper()) / len(content)
        return caps_ratio >= self.settings["caps_threshold"]

    async def _detect_mention_spam(self, message: discord.Message) -> bool:
        return len(message.mentions) >= self.settings["mention_limit"]

    async def _detect_repeated_content(self, user_id: int, content: str) -> bool:
        if len(content) < 5:
            return False
        recent_contents = [
            msg["content"]
            for msg in self.message_history[user_id]
            if time.time() - msg["timestamp"] <= 60
        ]
        identical_count = sum(
            1 for msg_content in recent_contents if msg_content == content
        )
        return identical_count >= 3

    async def _detect_link_spam(self, user_id: int, content: str) -> bool:
        url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        links_in_message = len(re.findall(url_pattern, content))
        return links_in_message >= self.settings["link_spam_threshold"]

    def _calculate_caps_ratio(self, text: str) -> float:
        if not text:
            return 0.0
        return sum(1 for c in text if c.isupper()) / len(text)

    def _determine_moderation_level(
        self, violation: ViolationType, warning_count: int
    ) -> ModerationLevel:
        # Special handling for emotional distress
        if violation == ViolationType.EMOTIONAL_DISTRESS:
            return ModerationLevel.FRIENDLY_REMINDER

        # Progressive escalation
        if warning_count == 0:
            return ModerationLevel.FRIENDLY_REMINDER
        elif warning_count == 1:
            return ModerationLevel.WARNING
        elif warning_count == 2:
            return ModerationLevel.TIMEOUT
        elif warning_count >= 3:
            return ModerationLevel.KICK
        else:
            return ModerationLevel.BAN

    async def _apply_consequences(
        self, user: discord.Member, mod_level: ModerationLevel, violation: ViolationType
    ):
        """Apply appropriate consequences based on moderation level"""
        if mod_level == ModerationLevel.TIMEOUT:
            try:
                duration = 300 * (
                    len(self.user_warnings.get(user.id, [])) + 1
                )  # Progressive timeout
                await user.timeout(discord.utils.utcnow() + timedelta(seconds=duration))
            except Exception as e:
                logger.error(f"Failed to timeout user {user}: {e}")

        elif mod_level == ModerationLevel.KICK:
            try:
                await user.kick(reason=f"Moderation: {violation.value}")
            except Exception as e:
                logger.error(f"Failed to kick user {user}: {e}")

        elif mod_level == ModerationLevel.BAN:
            try:
                await user.ban(
                    reason=f"Moderation: {violation.value}", delete_message_days=1
                )
            except Exception as e:
                logger.error(f"Failed to ban user {user}: {e}")

    def _log_moderation_action(
        self,
        user: discord.Member,
        violation: ViolationType,
        mod_level: ModerationLevel,
        action: str,
    ):
        """Log moderation action"""
        logger.info(
            f"AI Moderation: {user} ({user.id}) - {violation.value} - {mod_level.name} - {action}"
        )

    async def _random_positive_reinforcement(self, message: discord.Message):
        """Occasionally provide positive reinforcement for good behavior"""
        import random

        # Random chance for positive reinforcement (1 in 100 messages)
        if random.randint(1, 100) == 1 and AI_AVAILABLE:
            profile = await self.get_user_profile(message.author.id)

            # Only for users with good behavior
            if (
                profile.positive_interactions > 5
                and len(self.user_warnings.get(message.author.id, [])) == 0
            ):

                try:
                    prompt = f"Generate a brief, encouraging message for {message.author.display_name} who has been a positive member of the community. Keep it under 50 words and include an emoji."

                    ai_manager = MultiProviderAIManager()
                    ai_response_obj = await ai_manager.generate_response(prompt)
                    ai_response = ai_response_obj.content if ai_response_obj.success else f"Thanks for being awesome, {message.author.display_name}! 🌟"

                    await message.add_reaction("⭐")

                    # Occasionally send a message
                    if random.randint(1, 10) == 1:
                        embed = discord.Embed(
                            description=f"✨ {ai_response}", color=0x00FF7F
                        )
                        await message.channel.send(embed=embed, delete_after=15)

                except Exception as e:
                    logger.error(f"Failed positive reinforcement: {e}")


async def setup(bot):
    await bot.add_cog(AIModeration(bot))
