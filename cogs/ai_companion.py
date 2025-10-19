"""
from functools import lru_cache, wraps
import weakref
import gc
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
import os
import random
import time
from datetime import datetime, timedelta, timezone
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

        # Configure environment to suppress Google Cloud ALTS warnings
        os.environ.setdefault("GRPC_VERBOSITY", "ERROR")
        os.environ.setdefault("GLOG_minloglevel", "2")

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

        # Pre-compiled regex patterns for admin commands (performance optimization)
        self._admin_patterns = self._compile_admin_patterns()

        # Background tasks
        self.personality_sync_task.start()

        self.logger.info("✅ Astra AI Companion initialized (Astra personality only)")

    def _compile_admin_patterns(self):
        """Pre-compile regex patterns for better performance"""
        import re

        patterns = {
            # Delete/Remove patterns
            "delete_message": re.compile(
                r"(?:astra|bot)?,?\s*(?:delete|remove|clear)\s+(?:that\s+)?(?:message|msg|post)",
                re.IGNORECASE,
            ),
            "bulk_delete": re.compile(
                r"(?:astra|bot)?,?\s*(?:delete|remove|clear)\s+(?:the\s+)?(?:last|recent)\s+(?:\d+\s+)?(?:messages?|msgs?)",
                re.IGNORECASE,
            ),
            "channel_cleanup": re.compile(
                r"(?:astra|bot)?,?\s*(?:clean|clear)\s+(?:up\s+)?(?:here|this\s+channel)",
                re.IGNORECASE,
            ),
            # Kick patterns
            "kick_user": re.compile(
                r"(?:astra|bot)?,?\s*(?:kick|remove)\s+@?(\w+)", re.IGNORECASE
            ),
            "kick_mentioned": re.compile(
                r"(?:astra|bot)?,?\s*(?:kick|remove)\s+(?:that\s+)?(?:user|member|person)",
                re.IGNORECASE,
            ),
            # Timeout/Mute patterns
            "timeout_user": re.compile(
                r"(?:astra|bot)?,?\s*(?:timeout|mute|silence)\s+@?(\w+)(?:\s+for\s+(\d+)\s*(minutes?|mins?|hours?|hrs?))?",
                re.IGNORECASE,
            ),
            "timeout_mentioned": re.compile(
                r"(?:astra|bot)?,?\s*(?:timeout|mute|silence)\s+(?:that\s+)?(?:user|member|person)(?:\s+for\s+(\d+)\s*(minutes?|mins?|hours?|hrs?))?",
                re.IGNORECASE,
            ),
            # Ban patterns
            "ban_user": re.compile(
                r"(?:astra|bot)?,?\s*(?:ban|block)\s+@?(\w+)(?:\s+for\s+(.+))?",
                re.IGNORECASE,
            ),
            "ban_mentioned": re.compile(
                r"(?:astra|bot)?,?\s*(?:ban|block)\s+(?:that\s+)?(?:user|member|person)(?:\s+for\s+(.+))?",
                re.IGNORECASE,
            ),
            # Role management patterns
            "add_role": re.compile(
                r"(?:astra|bot)?,?\s*(?:give|add|assign)\s+@?(\w+)\s+(?:the\s+)?(\w+)\s+role",
                re.IGNORECASE,
            ),
            "remove_role": re.compile(
                r"(?:astra|bot)?,?\s*(?:remove|take)\s+(?:the\s+)?(\w+)\s+role\s+from\s+@?(\w+)",
                re.IGNORECASE,
            ),
            # Lock/Unlock patterns
            "lock_channel": re.compile(
                r"(?:astra|bot)?,?\s*(?:lock|disable)\s+(?:this\s+)?(?:channel|here)",
                re.IGNORECASE,
            ),
            "unlock_channel": re.compile(
                r"(?:astra|bot)?,?\s*(?:unlock|enable)\s+(?:this\s+)?(?:channel|here)",
                re.IGNORECASE,
            ),
        }

        # Map patterns to handlers
        pattern_handlers = {
            "delete_message": self._handle_delete_message,
            "bulk_delete": self._handle_bulk_delete,
            "channel_cleanup": self._handle_channel_cleanup,
            "kick_user": self._handle_kick_user,
            "kick_mentioned": self._handle_kick_mentioned,
            "timeout_user": self._handle_timeout_user,
            "timeout_mentioned": self._handle_timeout_mentioned,
            "ban_user": self._handle_ban_user,
            "ban_mentioned": self._handle_ban_mentioned,
            "add_role": self._handle_add_role,
            "remove_role": self._handle_remove_role,
            "lock_channel": self._handle_lock_channel,
            "unlock_channel": self._handle_unlock_channel,
        }

        return [(pattern, pattern_handlers[name]) for name, pattern in patterns.items()]

    def truncate_response(self, response: str, max_length: int = 1950) -> str:
        """Truncate response to fit Discord's character limit with graceful cutoff"""
        if len(response) <= max_length:
            return response

        # Log when truncation occurs for monitoring
        self.logger.warning(
            f"⚠️ Response being truncated: {len(response)} chars → {max_length} chars"
        )

        # Try to cut at a sentence boundary first
        truncated = response[:max_length]
        last_sentence = max(
            truncated.rfind("."), truncated.rfind("!"), truncated.rfind("?")
        )

        if (
            last_sentence > max_length * 0.7
        ):  # If we can keep at least 70% and end nicely
            return (
                truncated[: last_sentence + 1] + "\n\n*[Continued in next message...]*"
            )

        # Try to cut at paragraph boundary
        last_paragraph = truncated.rfind("\n\n")
        if last_paragraph > max_length * 0.6:
            return truncated[:last_paragraph] + "\n\n*[Continued in next message...]*"

        # Otherwise cut at word boundary
        last_space = truncated.rfind(" ")
        if last_space > max_length * 0.8:  # If we can keep at least 80% of text
            return truncated[:last_space] + "...\n\n*[Continued in next message...]*"

        # Fallback: hard cut with indicator
        return (
            response[: max_length - 50]
            + "...\n\n*[Response truncated - Discord character limit]*"
        )

    async def split_long_response(
        self, response: str, max_length: int = 1950
    ) -> List[str]:
        """Split very long responses into multiple messages"""
        if len(response) <= max_length:
            return [response]

        parts = []
        remaining = response
        part_number = 1

        while remaining:
            if len(remaining) <= max_length:
                # Last part
                if len(parts) > 0:  # Add part indicator if this is a continuation
                    parts.append(f"*[Part {part_number}]*\n\n{remaining}")
                else:
                    parts.append(remaining)
                break

            # Find good split point
            split_at = max_length

            # Try sentence boundary
            sentence_split = max(
                remaining[:max_length].rfind("."),
                remaining[:max_length].rfind("!"),
                remaining[:max_length].rfind("?"),
            )

            if sentence_split > max_length * 0.7:
                split_at = sentence_split + 1
            else:
                # Try paragraph boundary
                para_split = remaining[:max_length].rfind("\n\n")
                if para_split > max_length * 0.6:
                    split_at = para_split + 2
                else:
                    # Use word boundary
                    word_split = remaining[:max_length].rfind(" ")
                    if word_split > max_length * 0.8:
                        split_at = word_split

            # Extract this part
            part = remaining[:split_at].strip()
            if part_number == 1:
                parts.append(f"{part}\n\n*[Continued...]*")
            else:
                parts.append(f"*[Part {part_number}]*\n\n{part}\n\n*[Continued...]*")

            # Move to next part
            remaining = remaining[split_at:].strip()
            part_number += 1

            # Safety check - don't create too many parts
            if len(parts) >= 5:
                parts.append(
                    f"*[Part {part_number}]*\n\n{remaining[:max_length-100]}\n\n*[Response truncated - too long for Discord]*"
                )
                break

        return parts

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
        """Calculate the current personality vector based on profile and context - OPTIMIZED"""
        base = profile.base_personality
        mods = profile.modifiers

        # PERFORMANCE: Pre-calculate common factors to avoid repeated operations
        mood_factor = mods.user_mood * 0.15
        tone_factor = mods.conversation_tone * 0.12
        time_factor = mods.time_of_day * 0.08
        complexity_factor = context.get("complexity", 0) * 0.1
        urgency_factor = context.get("urgency", 0) * 0.2
        history_factor = min(mods.interaction_history * 0.01, 0.1)  # Gradual learning

        # OPTIMIZATION: Batch calculate adjustments for performance
        mood_boost = mood_factor * 1.5
        tone_abs = abs(tone_factor)
        tone_dampened = tone_factor * 0.8

        # Create adjusted personality with enhanced dynamics and optimized calculations
        adjusted = PersonalityDimensions(
            analytical=self._clamp(
                base.analytical + tone_factor + complexity_factor + history_factor
            ),
            empathetic=self._clamp(base.empathetic + mood_boost + (1.0 - tone_abs)),
            curious=self._clamp(
                base.curious + complexity_factor + history_factor * 0.5
            ),
            creative=self._clamp(base.creative + time_factor + mood_factor * 0.8),
            supportive=self._clamp(
                base.supportive + mood_factor + (1.0 - urgency_factor * 0.5)
            ),
            playful=self._clamp(base.playful - tone_dampened + mood_factor * 0.6),
            assertive=self._clamp(base.assertive + urgency_factor + tone_abs * 0.5),
            adaptable=self._clamp(
                base.adaptable + history_factor
            ),  # Grows with interaction
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
        """Generate Astra's response with maximum performance optimization"""
        response_start_time = time.perf_counter()

        try:
            self.logger.debug(
                f"� Ultra-fast response generation for: '{message.content[:30]}...'"
            )

            # 🚀 PERFORMANCE: Cache personality calculations
            personality_cache_key = f"{message.author.id}_{hash(str(context))}"

            if hasattr(self, "_personality_cache"):
                if personality_cache_key in self._personality_cache:
                    cached_data = self._personality_cache[personality_cache_key]
                    if time.time() - cached_data["timestamp"] < 300:  # 5 minute cache
                        current_personality = cached_data["personality"]
                        dominant_traits = cached_data["traits"]
                        self.logger.debug("⚡ Using cached personality calculation")
                    else:
                        del self._personality_cache[personality_cache_key]
                        current_personality = self.calculate_personality_vector(
                            profile, context
                        )
                        dominant_traits = self._get_dominant_traits(current_personality)
                else:
                    current_personality = self.calculate_personality_vector(
                        profile, context
                    )
                    dominant_traits = self._get_dominant_traits(current_personality)
                    # Cache for future use
                    if not hasattr(self, "_personality_cache"):
                        self._personality_cache = {}
                    self._personality_cache[personality_cache_key] = {
                        "personality": current_personality,
                        "traits": dominant_traits,
                        "timestamp": time.time(),
                    }
            else:
                self._personality_cache = {}
                current_personality = self.calculate_personality_vector(
                    profile, context
                )
                dominant_traits = self._get_dominant_traits(current_personality)

            # 🚀 ENHANCED: Advanced user profile with conversation context
            user_profile_data = {
                "name": message.author.display_name,
                "personality_traits": dominant_traits[:3],
                "dominant_emotion": context.get("sentiment", "neutral"),
                "channel_context": context.get("channel_type", "general"),
                "interaction_count": min(profile.modifiers.interaction_history, 1000),
                "current_mood": context.get("user_mood", 0.5),
                "conversation_tone": context.get("conversation_tone", "friendly"),
                "time_context": context.get("time_of_day", "general"),
                "conversation_flow": context.get("conversation_flow", "new"),
                "user_engagement": context.get("user_engagement", 0.5),
                "recent_topics": context.get("recent_topics", []),
                "astra_context": "Astra AI - Intelligent, adaptive companion with dynamic personality",
                "performance_mode": "conversation_optimized",
                "response_style": self._get_response_style_from_personality(
                    current_personality
                ),
            }

            # 🚀 ENHANCED: Dynamic temperature based on conversation context
            has_question = "?" in message.content or any(
                q in message.content.lower()
                for q in ["how", "what", "why", "when", "where", "who"]
            )
            base_temperature = 0.6 + (current_personality.creative * 0.3)
            conversation_factor = (
                0.1 if has_question else 0.05
            )  # More creative for questions
            mood_factor = context.get("user_mood", 0.5) * 0.1
            temperature = min(base_temperature + conversation_factor + mood_factor, 0.9)

            self.logger.debug(
                f"🎯 Enhanced AI call with temperature={temperature:.2f}, style={user_profile_data['response_style']}"
            )

            # 🚀 ENHANCED: Advanced message processing with conversation context
            enhanced_message = message.content

            # Get enhanced conversation context for better responses
            enhanced_context = await self._get_enhanced_conversation_context(
                message.author.id, message.channel.id
            )

            # Update context with enhanced conversation data
            context.update(
                {
                    "conversation_flow": enhanced_context["conversation_flow"],
                    "user_engagement": enhanced_context["user_engagement"],
                    "recent_topics": enhanced_context["recent_topics"],
                }
            )

            # Enhanced personality integration based on message type and context
            message_type = self._analyze_message_type(message.content)
            personality_prompt = self._create_enhanced_personality_prompt(
                dominant_traits, current_personality, message_type, context
            )

            # Smart message enhancement based on complexity, type, and conversation flow
            if (
                len(message.content) > 30
                or message_type in ["question", "complex", "emotional"]
                or any(
                    trait in ["analytical", "creative", "empathetic"]
                    for trait in dominant_traits[:3]
                )
            ):

                enhanced_message = f"{personality_prompt}\n\nUser: {message.content}"

                # Add conversation context for established conversations
                if enhanced_context["conversation_flow"] in [
                    "developing",
                    "established",
                ]:
                    context_summary = enhanced_context["context_summary"]
                    enhanced_message = f"{personality_prompt}\n\n{context_summary}\n\nUser: {message.content}"

            # Adaptive token allocation based on message complexity
            max_tokens = self._calculate_optimal_tokens(
                message.content, message_type, context
            )

            start_ai_time = time.perf_counter()
            ai_response = await self.ai_client.generate_response(
                enhanced_message,
                user_id=message.author.id,
                guild_id=message.guild.id if message.guild else None,
                channel_id=message.channel.id,
                user_profile=user_profile_data,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            ai_response_time = time.perf_counter() - start_ai_time
            total_response_time = time.perf_counter() - response_start_time

            # 🚀 PERFORMANCE: Log ultra-fast responses and optimize thresholds
            if total_response_time < 0.5:
                self.logger.debug(
                    f"🚀 ULTRA-FAST response: {total_response_time:.3f}s (AI: {ai_response_time:.3f}s)"
                )
            elif (
                total_response_time > 3.0
            ):  # Increased threshold from 1.5s to 3.0s to reduce noise
                self.logger.info(
                    f"📈 Response time: {total_response_time:.3f}s"
                )  # Changed from warning to info
            else:
                self.logger.debug(f"⚡ Good response: {total_response_time:.3f}s")

            response = (
                ai_response.content
                if ai_response and hasattr(ai_response, "content")
                else None
            )

            if not response:
                self.logger.warning(
                    f"⚠️ AI client returned no response, using optimized fallback"
                )
                response = self._get_optimized_fallback_response(
                    current_personality, dominant_traits
                )
            else:
                # 🚀 PERFORMANCE: Track successful responses
                self.logger.info(
                    f"📏 Generated response length: {len(response)} characters"
                )
                if len(response) > 1800:
                    self.logger.warning(
                        f"⚠️ Long response detected ({len(response)} chars) - will be truncated on send"
                    )

            return response

        except Exception as e:
            self.logger.error(f"❌ Error generating response: {e}")
            import traceback

            self.logger.error(f"📋 Traceback: {traceback.format_exc()}")
            return "I'm experiencing some technical difficulties, but I'm still here for you!"

    def _get_response_style_from_personality(
        self, personality: PersonalityDimensions
    ) -> str:
        """Determine optimal response style based on personality dimensions"""
        if personality.analytical > 0.7:
            return "analytical_detailed"
        elif personality.empathetic > 0.8:
            return "warm_supportive"
        elif personality.playful > 0.7:
            return "witty_engaging"
        elif personality.supportive > 0.8:
            return "helpful_caring"
        else:
            return "balanced_conversational"

    def _create_personality_instructions(
        self, personality: PersonalityDimensions, dominant_traits: List[str]
    ) -> str:
        """Create specific personality instructions that directly influence AI behavior"""
        instructions = []

        # Analytical behavior
        if personality.analytical > 0.7:
            instructions.append(
                "Provide detailed, logical explanations with examples and reasoning"
            )
        elif personality.analytical < 0.3:
            instructions.append("Keep responses simple and avoid over-analyzing")

        # Empathetic behavior
        if personality.empathetic > 0.8:
            instructions.append(
                "Show deep understanding and emotional connection, acknowledge feelings"
            )
        elif personality.empathetic < 0.3:
            instructions.append("Focus on facts rather than emotions, be more direct")

        # Playful behavior
        if personality.playful > 0.7:
            instructions.append(
                "Use humor, jokes, and light-hearted commentary frequently"
            )
        elif personality.playful < 0.3:
            instructions.append("Maintain a serious, professional tone")

        # Supportive behavior
        if personality.supportive > 0.8:
            instructions.append("Offer encouragement, help, and positive reinforcement")
        elif personality.supportive < 0.3:
            instructions.append(
                "Be neutral and factual without excessive supportiveness"
            )

        # Creative behavior
        if personality.creative > 0.7:
            instructions.append(
                "Use creative metaphors, analogies, and imaginative language"
            )
        elif personality.creative < 0.3:
            instructions.append("Stick to straightforward, practical language")

        # Curious behavior
        if personality.curious > 0.7:
            instructions.append(
                "Ask follow-up questions and show interest in learning more"
            )
        elif personality.curious < 0.3:
            instructions.append("Answer directly without exploring tangents")

        return (
            " | ".join(instructions)
            if instructions
            else "Respond naturally and conversationally"
        )

    def _generate_dynamic_personality_prompt(
        self, personality: PersonalityDimensions, context: Dict[str, Any]
    ) -> str:
        """Generate a dynamic system prompt that changes based on current personality settings"""
        base_prompt = (
            "You are Astra, a friendly AI companion who loves space and helping people."
        )

        # Personality-specific modifications
        personality_mods = []

        # High analytical: Add logical focus
        if personality.analytical > 0.7:
            personality_mods.append(
                "You excel at breaking down complex problems and explaining things clearly with logical reasoning"
            )

        # High empathetic: Add emotional intelligence
        if personality.empathetic > 0.8:
            personality_mods.append(
                "You deeply understand emotions and always respond with warmth and compassion"
            )

        # High playful: Add humor and wit
        if personality.playful > 0.7:
            personality_mods.append(
                "You love using space puns, jokes, and keeping conversations light and fun"
            )

        # High supportive: Add encouragement
        if personality.supportive > 0.8:
            personality_mods.append(
                "You're incredibly encouraging and always look for ways to help and motivate others"
            )

        # High creative: Add imagination
        if personality.creative > 0.7:
            personality_mods.append(
                "You use creative space metaphors and imaginative language to make conversations engaging"
            )

        # High curious: Add inquisitiveness
        if personality.curious > 0.7:
            personality_mods.append(
                "You're naturally curious and love asking thoughtful follow-up questions"
            )

        # Low adaptable: Add consistency note
        if personality.adaptable < 0.4:
            personality_mods.append("You maintain consistent behavior patterns")
        elif personality.adaptable > 0.8:
            personality_mods.append(
                "You quickly adapt your communication style to match the conversation needs"
            )

        if personality_mods:
            return f"{base_prompt} {' '.join(personality_mods)}"

        return base_prompt

    def _calculate_personality_intensity(
        self, personality: PersonalityDimensions
    ) -> float:
        """Calculate how intensely the personality should be expressed (0.0 to 1.0)"""
        # Average of the most prominent traits
        traits = personality.to_dict()
        max_traits = sorted(traits.values(), reverse=True)[:3]
        return sum(max_traits) / 3

    def _enhance_message_with_personality_context(
        self,
        message: str,
        personality: PersonalityDimensions,
        dominant_traits: List[str],
    ) -> str:
        """Enhance the user message with personality context to ensure behavior changes"""
        # Create a system context that forces personality compliance
        personality_context = (
            f"[SYSTEM: Respond as Astra with these personality settings - "
        )

        trait_descriptions = []
        for trait in dominant_traits[:3]:
            value = getattr(personality, trait.lower(), 0.5)
            if value > 0.7:
                trait_descriptions.append(f"{trait}=HIGH({value:.1f})")
            elif value < 0.3:
                trait_descriptions.append(f"{trait}=LOW({value:.1f})")
            else:
                trait_descriptions.append(f"{trait}=MED({value:.1f})")

        personality_context += ", ".join(trait_descriptions)
        personality_context += "] "

        return personality_context + message

    def _create_behavior_preview(
        self, personality: PersonalityDimensions, dominant_traits: List[str]
    ) -> str:
        """Create a preview of how the personality changes will affect behavior"""
        previews = []

        for trait in dominant_traits[:3]:
            value = getattr(personality, trait.lower(), 0.5)
            if value > 0.7:
                preview = self._get_high_trait_behavior(trait.lower())
                previews.append(f"🔥 **{trait.title()}**: {preview}")
            elif value < 0.3:
                preview = self._get_low_trait_behavior(trait.lower())
                previews.append(f"❄️ **{trait.title()}**: {preview}")

        return (
            "\n".join(previews)
            if previews
            else "Balanced, natural responses across all traits"
        )

    def _get_high_trait_behavior(self, trait: str) -> str:
        """Get behavior description for high trait values"""
        behaviors = {
            "analytical": "Detailed explanations with logic and reasoning",
            "empathetic": "Warm, understanding responses with emotional connection",
            "curious": "Lots of follow-up questions and genuine interest",
            "creative": "Space metaphors, imaginative language, unique perspectives",
            "supportive": "Encouraging, helpful, always looking to motivate",
            "playful": "Jokes, puns, light-hearted humor frequently",
            "assertive": "Confident, direct responses with clear opinions",
            "adaptable": "Quick style changes to match conversation needs",
        }
        return behaviors.get(trait, "Enhanced behavior for this trait")

    def _get_low_trait_behavior(self, trait: str) -> str:
        """Get behavior description for low trait values"""
        behaviors = {
            "analytical": "Simple, direct answers without deep analysis",
            "empathetic": "Factual responses without excessive emotional focus",
            "curious": "Answer directly without exploring tangents",
            "creative": "Straightforward, practical language",
            "supportive": "Neutral responses without excessive encouragement",
            "playful": "Serious, professional tone",
            "assertive": "Gentle, non-confrontational responses",
            "adaptable": "Consistent behavior regardless of context",
        }
        return behaviors.get(trait, "Reduced behavior for this trait")

    def _explain_trait_behavior_change(self, trait: str, value: float) -> str:
        """Explain what a specific trait change means for behavior"""
        if value > 0.7:
            return self._get_high_trait_behavior(trait)
        elif value < 0.3:
            return self._get_low_trait_behavior(trait)
        else:
            return f"Moderate {trait} responses - balanced behavior"

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

    def _get_optimized_fallback_response(
        self, personality: PersonalityDimensions, dominant_traits: List[str]
    ) -> str:
        """Ultra-fast optimized fallback responses based on personality"""
        base_responses = {
            "analytical": "Let me analyze that for you.",
            "empathetic": "I understand how you feel about this.",
            "curious": "That's interesting! Tell me more.",
            "creative": "What an intriguing perspective!",
            "supportive": "I'm here to help you with that.",
            "playful": "Haha, that's quite something!",
            "assertive": "I have some thoughts on this.",
            "adaptable": "I can work with that approach.",
        }

        # Use first dominant trait for fast response
        primary_trait = dominant_traits[0] if dominant_traits else "supportive"
        return base_responses.get(
            primary_trait, "I'm here to help! How can I assist you?"
        )

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

    def _analyze_message_type(self, content: str) -> str:
        """Analyze message type for enhanced response generation"""
        content_lower = content.lower()

        # Question types
        if "?" in content or any(
            q in content_lower for q in ["how", "what", "why", "when", "where", "who"]
        ):
            return "question"

        # Emotional content
        emotional_indicators = [
            "feel",
            "emotion",
            "sad",
            "happy",
            "angry",
            "excited",
            "worried",
            "stressed",
        ]
        if any(word in content_lower for word in emotional_indicators):
            return "emotional"

        # Complex/analytical content
        if len(content) > 100 or any(
            word in content_lower
            for word in ["analyze", "explain", "details", "complex", "system"]
        ):
            return "complex"

        # Greeting/social
        if any(
            word in content_lower
            for word in ["hi", "hello", "hey", "thanks", "thank you", "goodbye"]
        ):
            return "social"

        # Default
        return "general"

    def _create_enhanced_personality_prompt(
        self,
        dominant_traits: List[str],
        personality: PersonalityDimensions,
        message_type: str,
        context: Dict[str, Any],
    ) -> str:
        """Create an enhanced personality prompt based on conversation context"""

        # Base personality description
        trait_descriptions = {
            "analytical": "thoughtful and detail-oriented, providing logical explanations",
            "empathetic": "caring and emotionally aware, understanding user feelings",
            "creative": "imaginative and innovative, offering unique perspectives",
            "playful": "witty and humorous, using jokes and light-hearted responses",
            "supportive": "encouraging and helpful, always ready to assist",
            "curious": "inquisitive and engaging, asking follow-up questions",
            "assertive": "confident and direct, providing clear answers",
            "adaptable": "flexible and responsive, adjusting to user needs",
        }

        # Build personality description
        personality_desc = []
        for trait in dominant_traits[:3]:  # Use top 3 traits
            if trait in trait_descriptions:
                personality_desc.append(trait_descriptions[trait])

        personality_str = ", ".join(personality_desc)

        # Message type specific instructions
        type_instructions = {
            "question": "Focus on providing clear, helpful answers with explanations",
            "emotional": "Be especially empathetic and supportive, acknowledge feelings",
            "complex": "Provide detailed, well-structured responses with examples",
            "social": "Be warm and conversational, match the user's social energy",
            "general": "Respond naturally and appropriately to the context",
        }

        instruction = type_instructions.get(message_type, type_instructions["general"])

        # Context awareness
        mood = context.get("user_mood", 0.5)
        mood_desc = "cheerful" if mood > 0.7 else "neutral" if mood > 0.3 else "gentle"

        return (
            f"You are Astra, an AI companion who is {personality_str}. "
            f"The user seems {mood_desc} today. {instruction}. "
            f"Respond as Astra with your authentic personality, keeping responses "
            f"conversational and engaging while being helpful."
        )

    def _calculate_optimal_tokens(
        self, content: str, message_type: str, context: Dict[str, Any]
    ) -> int:
        """Calculate optimal token allocation based on message complexity"""
        base_tokens = 400

        # Adjust based on message type
        type_multipliers = {
            "question": 1.3,  # More detailed answers
            "complex": 1.5,  # Comprehensive responses
            "emotional": 1.2,  # Thoughtful, supportive responses
            "social": 0.8,  # Shorter, conversational responses
            "general": 1.0,  # Standard length
        }

        # Adjust based on content length
        if len(content) > 200:
            length_multiplier = 1.4
        elif len(content) > 100:
            length_multiplier = 1.2
        elif len(content) < 30:
            length_multiplier = 0.8
        else:
            length_multiplier = 1.0

        # Calculate final token count
        optimal_tokens = int(
            base_tokens * type_multipliers.get(message_type, 1.0) * length_multiplier
        )

        # Ensure reasonable bounds
        return max(200, min(optimal_tokens, 800))

    async def _get_enhanced_conversation_context(
        self, user_id: int, channel_id: int
    ) -> Dict[str, Any]:
        """Get enhanced conversation context with recent message analysis"""
        try:
            # Get recent messages from conversation history
            conversation_history = self.conversation_manager.get_conversation_history(
                user_id, channel_id, limit=5
            )

            if not conversation_history:
                return {
                    "recent_topics": [],
                    "conversation_flow": "new",
                    "user_engagement": 0.5,
                    "context_summary": "Starting new conversation",
                }

            # Analyze recent topics
            recent_topics = []
            user_messages = [
                msg for msg in conversation_history if msg.get("role") == "user"
            ]

            for msg in user_messages[-3:]:  # Last 3 user messages
                content = msg.get("content", "").lower()
                if len(content) > 10:  # Ignore very short messages
                    # Extract potential topics (simple keyword extraction)
                    words = content.split()
                    meaningful_words = [w for w in words if len(w) > 3 and w.isalpha()]
                    recent_topics.extend(
                        meaningful_words[:3]
                    )  # Take up to 3 words per message

            # Determine conversation flow
            if len(conversation_history) < 3:
                conversation_flow = "beginning"
            elif len(conversation_history) < 10:
                conversation_flow = "developing"
            else:
                conversation_flow = "established"

            # Calculate user engagement based on message length and frequency
            if user_messages:
                avg_length = sum(
                    len(msg.get("content", "")) for msg in user_messages
                ) / len(user_messages)
                engagement = min(1.0, avg_length / 100)  # Normalize to 0-1 scale
            else:
                engagement = 0.5

            # Create context summary
            unique_topics = list(set(recent_topics))[
                :5
            ]  # Remove duplicates, keep top 5
            topic_str = (
                ", ".join(unique_topics) if unique_topics else "general conversation"
            )

            context_summary = (
                f"Ongoing {conversation_flow} conversation about {topic_str}"
            )

            return {
                "recent_topics": unique_topics,
                "conversation_flow": conversation_flow,
                "user_engagement": engagement,
                "context_summary": context_summary,
                "message_count": len(conversation_history),
            }

        except Exception as e:
            self.logger.error(f"Error getting enhanced conversation context: {e}")
            return {
                "recent_topics": [],
                "conversation_flow": "unknown",
                "user_engagement": 0.5,
                "context_summary": "Unable to load conversation context",
            }

    async def _process_natural_admin_commands(self, message: discord.Message) -> bool:
        """Process natural language administrative commands with optimized pattern matching"""
        if not message.guild:
            return False

        # Quick permission check first
        if not message.author.guild_permissions.manage_messages:
            return False

        content = message.content.lower().strip()

        # Early exit for obviously non-admin messages (performance optimization)
        admin_keywords = [
            "delete",
            "remove",
            "clear",
            "kick",
            "ban",
            "timeout",
            "mute",
            "silence",
            "give",
            "add",
            "assign",
            "take",
            "lock",
            "unlock",
            "disable",
            "enable",
        ]
        if not any(keyword in content for keyword in admin_keywords):
            return False

        # Use pre-compiled patterns for better performance
        for pattern, handler in self._admin_patterns:
            match = pattern.search(content)
            if match:
                try:
                    await handler(message, match)
                    return True
                except Exception as e:
                    self.logger.error(f"Error handling natural admin command: {e}")
                    await message.channel.send(
                        f"❌ Sorry, I couldn't complete that action: {str(e)}"
                    )
                    return True

        return False

    async def _handle_delete_message(self, message: discord.Message, match):
        """Handle natural delete message commands with enhanced safety checks"""
        # Get the message to delete (previous message or referenced message)
        target_message = None

        # First try to get referenced message
        if message.reference and message.reference.message_id:
            try:
                target_message = await message.channel.fetch_message(
                    message.reference.message_id
                )
            except discord.NotFound:
                pass
            except discord.Forbidden:
                await message.channel.send(
                    "❌ I don't have permission to access that message."
                )
                return

        if not target_message:
            # Get the message before this one (skip bot messages)
            async for msg in message.channel.history(limit=10):
                if msg.id != message.id and not msg.author.bot:
                    target_message = msg
                    break

        if not target_message:
            await message.channel.send("❌ No message found to delete.")
            return

        # Enhanced permission checking
        if target_message.author != message.author:
            if not message.author.guild_permissions.manage_messages:
                await message.channel.send(
                    "❌ You need manage messages permission to delete other users' messages."
                )
                return

            # Additional safety: can't delete messages from users with higher roles
            if (
                target_message.author.top_role >= message.author.top_role
                and message.author != message.guild.owner
            ):
                await message.channel.send(
                    "❌ You cannot delete messages from users with equal or higher roles."
                )
                return

        try:
            await target_message.delete()
            confirmation = await message.channel.send("✅ Message deleted!")

            # Log the action
            await self._log_admin_action(
                "delete_message",
                message.author,
                f"Message by {target_message.author}",
                {"channel": str(message.channel)},
            )

            # Auto-cleanup
            await asyncio.sleep(3)
            try:
                await confirmation.delete()
                await message.delete()
            except:
                pass  # Ignore cleanup errors

        except discord.Forbidden:
            await message.channel.send(
                "❌ I don't have permission to delete that message."
            )
        except discord.NotFound:
            await message.channel.send("❌ Message has already been deleted.")
        except Exception as e:
            await message.channel.send(f"❌ Error deleting message: {str(e)}")
            self.logger.error(f"Error in delete message handler: {e}")

    async def _handle_bulk_delete(self, message: discord.Message, match):
        """Handle bulk delete commands"""
        if not message.author.guild_permissions.manage_messages:
            await message.channel.send(
                "❌ You need manage messages permission for bulk deletion."
            )
            return

        # Extract number from message (default 5, max 100)
        import re

        numbers = re.findall(r"\d+", message.content)
        count = int(numbers[0]) if numbers else 5
        count = min(max(count, 1), 100)  # Clamp between 1 and 100

        try:
            # More efficient bulk delete with better error handling
            deleted = await message.channel.purge(
                limit=count + 1,  # +1 for the command message
                check=lambda m: m.created_at
                > (discord.utils.utcnow() - timedelta(days=14)),  # Discord 14-day limit
            )

            actual_deleted = len(deleted) - 1  # Subtract command message
            confirmation = await message.channel.send(
                f"✅ Deleted {actual_deleted} message{'s' if actual_deleted != 1 else ''}!"
            )

            # Log the action
            await self._log_admin_action(
                "bulk_delete",
                message.author,
                f"{actual_deleted} messages",
                {"channel": str(message.channel), "requested_count": count},
            )

            # Auto-cleanup
            await asyncio.sleep(5)
            try:
                await confirmation.delete()
            except:
                pass

        except discord.Forbidden:
            await message.channel.send(
                "❌ I don't have permission to delete messages in this channel."
            )
        except discord.HTTPException as e:
            if "You can only bulk delete messages that are under 14 days old" in str(e):
                await message.channel.send(
                    "❌ Can only bulk delete messages under 14 days old. Try a smaller number."
                )
            else:
                await message.channel.send(f"❌ Error during bulk delete: {str(e)}")
        except Exception as e:
            await message.channel.send(
                f"❌ Unexpected error during bulk delete: {str(e)}"
            )
            self.logger.error(f"Error in bulk delete handler: {e}")

    async def _handle_channel_cleanup(self, message: discord.Message, match):
        """Handle channel cleanup commands"""
        if not message.author.guild_permissions.manage_messages:
            await message.channel.send(
                "❌ You need manage messages permission for channel cleanup."
            )
            return

        deleted = await message.channel.purge(limit=50)
        confirmation = await message.channel.send(
            f"✅ Cleaned up {len(deleted)-1} messages from this channel!"
        )
        await asyncio.sleep(5)
        await confirmation.delete()

    async def _handle_kick_user(self, message: discord.Message, match):
        """Handle kick user commands"""
        if not message.author.guild_permissions.kick_members:
            await message.channel.send("❌ You need kick members permission.")
            return

        username = match.group(1) if match.groups() else None
        if not username:
            await message.channel.send("❌ Please specify a user to kick.")
            return

        # Find member by name/display name
        member = None
        for m in message.guild.members:
            if username.lower() in [m.name.lower(), m.display_name.lower(), str(m.id)]:
                member = m
                break

        if not member:
            await message.channel.send(f"❌ Could not find user '{username}'.")
            return

        if (
            member.top_role >= message.author.top_role
            and message.author != message.guild.owner
        ):
            await message.channel.send(
                "❌ You cannot kick someone with equal or higher roles."
            )
            return

        try:
            await member.kick(reason=f"Natural language command by {message.author}")
            await message.channel.send(f"✅ Kicked {member.mention} ({member.name})")
            await self._log_admin_action(
                "kick",
                message.author,
                str(member),
                {"reason": "Natural language command"},
            )
        except discord.Forbidden:
            await message.channel.send("❌ I don't have permission to kick this user.")

    async def _handle_kick_mentioned(self, message: discord.Message, match):
        """Handle kick mentioned user commands"""
        if not message.author.guild_permissions.kick_members:
            await message.channel.send("❌ You need kick members permission.")
            return

        if not message.mentions:
            await message.channel.send("❌ Please mention the user you want to kick.")
            return

        member = message.mentions[0]
        if (
            member.top_role >= message.author.top_role
            and message.author != message.guild.owner
        ):
            await message.channel.send(
                "❌ You cannot kick someone with equal or higher roles."
            )
            return

        try:
            await member.kick(reason=f"Natural language command by {message.author}")
            await message.channel.send(f"✅ Kicked {member.mention} ({member.name})")
            await self._log_admin_action(
                "kick",
                message.author,
                str(member),
                {"reason": "Natural language command"},
            )
        except discord.Forbidden:
            await message.channel.send("❌ I don't have permission to kick this user.")

    async def _handle_timeout_user(self, message: discord.Message, match):
        """Handle timeout user commands with enhanced validation and error handling"""
        if not message.author.guild_permissions.moderate_members:
            await message.channel.send("❌ You need moderate members permission.")
            return

        groups = match.groups()
        username = groups[0] if groups else None

        # Enhanced duration parsing with validation
        try:
            duration_num = int(groups[1]) if len(groups) > 1 and groups[1] else 10
            duration_unit = groups[2] if len(groups) > 2 and groups[2] else "minutes"

            # Validate duration limits (Discord max: 28 days)
            if "hour" in duration_unit:
                duration_minutes = duration_num * 60
                max_hours = 28 * 24  # 28 days in hours
                if duration_num > max_hours:
                    await message.channel.send(
                        f"❌ Maximum timeout duration is {max_hours} hours (28 days)."
                    )
                    return
            elif "day" in duration_unit:
                duration_minutes = duration_num * 60 * 24
                if duration_num > 28:
                    await message.channel.send(
                        "❌ Maximum timeout duration is 28 days."
                    )
                    return
            else:  # minutes
                duration_minutes = duration_num
                if duration_minutes > 28 * 24 * 60:  # 28 days in minutes
                    await message.channel.send(
                        "❌ Maximum timeout duration is 28 days."
                    )
                    return

            # Minimum timeout validation
            if duration_minutes < 1:
                await message.channel.send("❌ Minimum timeout duration is 1 minute.")
                return

        except ValueError:
            await message.channel.send(
                "❌ Invalid duration format. Please use a valid number."
            )
            return

        # Enhanced member search with better error handling
        member = None
        if username:
            # Try exact username match first
            member = discord.utils.get(message.guild.members, name=username)

            # Try display name match
            if not member:
                member = discord.utils.get(message.guild.members, display_name=username)

            # Try case-insensitive search
            if not member:
                for m in message.guild.members:
                    if username.lower() in [
                        m.name.lower(),
                        m.display_name.lower(),
                        str(m.id),
                    ]:
                        member = m
                        break

        if not member:
            await message.channel.send(
                f"❌ Could not find user '{username}'. Please check the username."
            )
            return

        # Enhanced role hierarchy check
        if (
            member.top_role >= message.author.top_role
            and message.author != message.guild.owner
        ):
            await message.channel.send(
                "❌ You cannot timeout someone with equal or higher roles."
            )
            return

        # Check if user is bot owner or has admin
        if (
            member.guild_permissions.administrator
            and message.author != message.guild.owner
        ):
            await message.channel.send("❌ Cannot timeout administrators.")
            return

        try:
            timeout_until = datetime.now(timezone.utc) + timedelta(
                minutes=duration_minutes
            )
            await member.timeout(
                timeout_until,
                reason=f"Natural language command by {message.author} ({message.author.id})",
            )

            await message.channel.send(
                f"✅ Timed out {member.mention} for {duration_num} {duration_unit}"
            )

            # Log the action with more details
            await self._log_admin_action(
                "timeout",
                message.author,
                str(member),
                {
                    "duration": f"{duration_num} {duration_unit}",
                    "duration_minutes": duration_minutes,
                    "timeout_until": timeout_until.isoformat(),
                },
            )

        except discord.Forbidden:
            await message.channel.send(
                "❌ I don't have permission to timeout this user."
            )
        except discord.HTTPException as e:
            await message.channel.send(f"❌ Failed to timeout user: {str(e)}")
        except Exception as e:
            await message.channel.send(f"❌ Unexpected error during timeout: {str(e)}")
            self.logger.error(f"Error in timeout handler: {e}")

    async def _handle_timeout_mentioned(self, message: discord.Message, match):
        """Handle timeout mentioned user commands"""
        if not message.author.guild_permissions.moderate_members:
            await message.channel.send("❌ You need moderate members permission.")
            return

        if not message.mentions:
            await message.channel.send(
                "❌ Please mention the user you want to timeout."
            )
            return

        member = message.mentions[0]
        groups = match.groups()
        duration_num = int(groups[0]) if groups and groups[0] else 10
        duration_unit = groups[1] if len(groups) > 1 and groups[1] else "minutes"

        # Convert to minutes
        if "hour" in duration_unit:
            duration_minutes = duration_num * 60
        else:
            duration_minutes = duration_num

        if (
            member.top_role >= message.author.top_role
            and message.author != message.guild.owner
        ):
            await message.channel.send(
                "❌ You cannot timeout someone with equal or higher roles."
            )
            return

        try:
            timeout_until = datetime.now(timezone.utc) + timedelta(
                minutes=duration_minutes
            )
            await member.timeout(
                timeout_until, reason=f"Natural language command by {message.author}"
            )
            await message.channel.send(
                f"✅ Timed out {member.mention} for {duration_num} {duration_unit}"
            )
        except discord.Forbidden:
            await message.channel.send(
                "❌ I don't have permission to timeout this user."
            )

    async def _handle_ban_user(self, message: discord.Message, match):
        """Handle ban user commands with enhanced validation and safety checks"""
        if not message.author.guild_permissions.ban_members:
            await message.channel.send("❌ You need ban members permission.")
            return

        groups = match.groups()
        username = groups[0] if groups else None
        reason = (
            groups[1]
            if len(groups) > 1 and groups[1]
            else "Natural language ban command"
        )

        # Validate reason length (Discord limit is 512 characters)
        if len(reason) > 500:
            reason = reason[:500] + "..."

        # Enhanced member search
        member = None
        if username:
            # Try exact username match first
            member = discord.utils.get(message.guild.members, name=username)

            # Try display name match
            if not member:
                member = discord.utils.get(message.guild.members, display_name=username)

            # Try case-insensitive search
            if not member:
                for m in message.guild.members:
                    if username.lower() in [
                        m.name.lower(),
                        m.display_name.lower(),
                        str(m.id),
                    ]:
                        member = m
                        break

        if not member:
            await message.channel.send(
                f"❌ Could not find user '{username}'. Please check the username."
            )
            return

        # Enhanced role hierarchy and safety checks
        if (
            member.top_role >= message.author.top_role
            and message.author != message.guild.owner
        ):
            await message.channel.send(
                "❌ You cannot ban someone with equal or higher roles."
            )
            return

        # Prevent banning server owner
        if member == message.guild.owner:
            await message.channel.send("❌ Cannot ban the server owner.")
            return

        # Check if user is administrator
        if (
            member.guild_permissions.administrator
            and message.author != message.guild.owner
        ):
            await message.channel.send(
                "❌ Cannot ban administrators unless you're the server owner."
            )
            return

        # Prevent self-ban
        if member == message.author:
            await message.channel.send("❌ You cannot ban yourself.")
            return

        # Confirmation for serious action
        try:
            await member.ban(
                reason=f"{reason} - Command by {message.author} ({message.author.id})",
                delete_message_days=1,  # Delete 1 day of messages
            )

            await message.channel.send(
                f"✅ Banned {member.mention} ({member.name})\n📝 Reason: {reason}"
            )

            # Enhanced logging
            await self._log_admin_action(
                "ban",
                message.author,
                str(member),
                {"reason": reason, "user_id": member.id, "deleted_message_days": 1},
            )

        except discord.Forbidden:
            await message.channel.send("❌ I don't have permission to ban this user.")
        except discord.HTTPException as e:
            await message.channel.send(f"❌ Failed to ban user: {str(e)}")
        except Exception as e:
            await message.channel.send(f"❌ Unexpected error during ban: {str(e)}")
            self.logger.error(f"Error in ban handler: {e}")

    async def _handle_ban_mentioned(self, message: discord.Message, match):
        """Handle ban mentioned user commands"""
        if not message.author.guild_permissions.ban_members:
            await message.channel.send("❌ You need ban members permission.")
            return

        if not message.mentions:
            await message.channel.send("❌ Please mention the user you want to ban.")
            return

        member = message.mentions[0]
        groups = match.groups()
        reason = groups[0] if groups and groups[0] else "Natural language ban command"

        if (
            member.top_role >= message.author.top_role
            and message.author != message.guild.owner
        ):
            await message.channel.send(
                "❌ You cannot ban someone with equal or higher roles."
            )
            return

        try:
            await member.ban(reason=f"{reason} - Command by {message.author}")
            await message.channel.send(f"✅ Banned {member.mention} ({member.name})")
        except discord.Forbidden:
            await message.channel.send("❌ I don't have permission to ban this user.")

    async def _handle_add_role(self, message: discord.Message, match):
        """Handle add role commands"""
        if not message.author.guild_permissions.manage_roles:
            await message.channel.send("❌ You need manage roles permission.")
            return

        groups = match.groups()
        username = groups[0] if groups else None
        role_name = groups[1] if len(groups) > 1 and groups[1] else None

        # Find member and role
        member = None
        for m in message.guild.members:
            if username and username.lower() in [
                m.name.lower(),
                m.display_name.lower(),
                str(m.id),
            ]:
                member = m
                break

        role = discord.utils.get(message.guild.roles, name=role_name)
        if not role:
            # Try case-insensitive search
            role = discord.utils.find(
                lambda r: r.name.lower() == role_name.lower(), message.guild.roles
            )

        if not member:
            await message.channel.send(f"❌ Could not find user '{username}'.")
            return

        if not role:
            await message.channel.send(f"❌ Could not find role '{role_name}'.")
            return

        if role >= message.author.top_role and message.author != message.guild.owner:
            await message.channel.send(
                "❌ You cannot assign roles equal to or higher than your own."
            )
            return

        try:
            await member.add_roles(
                role, reason=f"Natural language command by {message.author}"
            )
            await message.channel.send(f"✅ Gave {member.mention} the {role.name} role")
        except discord.Forbidden:
            await message.channel.send(
                "❌ I don't have permission to manage this role."
            )

    async def _handle_remove_role(self, message: discord.Message, match):
        """Handle remove role commands"""
        if not message.author.guild_permissions.manage_roles:
            await message.channel.send("❌ You need manage roles permission.")
            return

        groups = match.groups()
        role_name = groups[0] if groups else None
        username = groups[1] if len(groups) > 1 and groups[1] else None

        # Find member and role
        member = None
        for m in message.guild.members:
            if username and username.lower() in [
                m.name.lower(),
                m.display_name.lower(),
                str(m.id),
            ]:
                member = m
                break

        role = discord.utils.get(message.guild.roles, name=role_name)
        if not role:
            role = discord.utils.find(
                lambda r: r.name.lower() == role_name.lower(), message.guild.roles
            )

        if not member:
            await message.channel.send(f"❌ Could not find user '{username}'.")
            return

        if not role:
            await message.channel.send(f"❌ Could not find role '{role_name}'.")
            return

        if role >= message.author.top_role and message.author != message.guild.owner:
            await message.channel.send(
                "❌ You cannot manage roles equal to or higher than your own."
            )
            return

        try:
            await member.remove_roles(
                role, reason=f"Natural language command by {message.author}"
            )
            await message.channel.send(
                f"✅ Removed the {role.name} role from {member.mention}"
            )
        except discord.Forbidden:
            await message.channel.send(
                "❌ I don't have permission to manage this role."
            )

    async def _handle_lock_channel(self, message: discord.Message, match):
        """Handle lock channel commands"""
        if not message.author.guild_permissions.manage_channels:
            await message.channel.send("❌ You need manage channels permission.")
            return

        try:
            overwrites = message.channel.overwrites_for(message.guild.default_role)
            overwrites.send_messages = False
            await message.channel.set_permissions(
                message.guild.default_role,
                overwrite=overwrites,
                reason=f"Channel locked by {message.author}",
            )
            await message.channel.send(f"🔒 Channel locked by {message.author.mention}")
        except discord.Forbidden:
            await message.channel.send(
                "❌ I don't have permission to manage this channel."
            )

    async def _handle_unlock_channel(self, message: discord.Message, match):
        """Handle unlock channel commands"""
        if not message.author.guild_permissions.manage_channels:
            await message.channel.send("❌ You need manage channels permission.")
            return

        try:
            overwrites = message.channel.overwrites_for(message.guild.default_role)
            overwrites.send_messages = None  # Reset to default
            await message.channel.set_permissions(
                message.guild.default_role,
                overwrite=overwrites,
                reason=f"Channel unlocked by {message.author}",
            )
            await message.channel.send(
                f"🔓 Channel unlocked by {message.author.mention}"
            )
        except discord.Forbidden:
            await message.channel.send(
                "❌ I don't have permission to manage this channel."
            )

    async def _log_admin_action(
        self,
        action_type: str,
        user: discord.User,
        target: str,
        details: Dict[str, Any] = None,
    ):
        """Log administrative actions to security manager if available"""
        try:
            security_manager = self.bot.get_cog("SecurityManager")
            if security_manager and hasattr(security_manager, "log_admin_action"):
                security_manager.log_admin_action(action_type, user, target, details)
        except Exception as e:
            self.logger.error(f"Error logging admin action: {e}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Enhanced message monitoring for natural conversation and admin commands"""
        # Skip only bot messages, allow all user messages (including DMs)
        if message.author.bot:
            return

        # Quick admin command check first (high priority)
        admin_handled = await self._process_natural_admin_commands(message)
        if admin_handled:
            return

        # Enhanced natural conversation triggers (more responsive)
        bot_mentioned = self.bot.user.mentioned_in(message)
        is_dm = isinstance(message.channel, discord.DMChannel)
        content_lower = message.content.lower()

        # Direct name mentions (more flexible)
        name_mentioned = any(
            name in content_lower for name in ["astra", "bot", "@astra"]
        )

        # Enhanced conversation patterns (more inclusive)
        question_patterns = [
            "?",
            "how",
            "what",
            "why",
            "when",
            "where",
            "who",
            "help",
            "can you",
        ]
        greeting_patterns = [
            "hey",
            "hi",
            "hello",
            "good morning",
            "good evening",
            "thanks",
            "thank you",
        ]

        has_question = any(pattern in content_lower for pattern in question_patterns)
        has_greeting = any(pattern in content_lower for pattern in greeting_patterns)

        # Message length check for meaningful conversations
        is_meaningful = len(message.content.strip()) > 3

        # Conversation context (check if replying to Astra)
        is_reply_to_astra = (
            message.reference
            and message.reference.message_id
            and hasattr(message.reference, "resolved")
            and message.reference.resolved
            and message.reference.resolved.author == self.bot.user
        )

        # Enhanced trigger logic - more responsive to natural conversation
        should_respond = (
            bot_mentioned
            or is_dm
            or name_mentioned
            or is_reply_to_astra
            or (is_meaningful and (has_question or has_greeting))
        )

        # Respond with enhanced triggers
        if should_respond:
            self.logger.info(
                f"💬 Natural conversation with {message.author.display_name} "
                f"{'in DM' if is_dm else f'in {message.guild.name}'}"
            )
            # Use asyncio.create_task for non-blocking response
            asyncio.create_task(self.handle_companion_interaction(message))

    async def handle_companion_interaction(self, message: discord.Message):
        """Enhanced companion interaction with optimized performance"""
        try:
            start_time = time.perf_counter()

            # Show typing indicator for better UX
            async with message.channel.typing():
                self.logger.debug(
                    f"💬 Processing message from {message.author.display_name}"
                )

                # Get user personality profile (cached for performance)
                profile = await self.get_personality_profile(
                    message.author.id, message.guild.id if message.guild else 0
                )

                # Quick context analysis (optimized)
                context = await self._analyze_message_context(message)

                # Update personality with minimal processing
                profile.modifiers.user_mood = context["user_mood"]
                profile.modifiers.conversation_tone = context["conversation_tone"]
                profile.modifiers.interaction_history += 1

                # Generate response with enhanced Astra personality
                response = await self.generate_astra_response(message, profile, context)

                if response:
                    # Enhanced conversation tracking (lightweight)
                    if message.author.id not in self.conversation_contexts:
                        self.conversation_contexts[message.author.id] = []

                    # Store minimal conversation context (last 5 for performance)
                    self.conversation_contexts[message.author.id].append(
                        {
                            "message": message.content[
                                :100
                            ],  # Truncated for memory efficiency
                            "response": response[:100],
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

                    # Keep only last 5 interactions (reduced from 10 for better performance)
                    if len(self.conversation_contexts[message.author.id]) > 5:
                        self.conversation_contexts[message.author.id].pop(0)

                    # Smart response handling - prefer single message
                    if len(response) > 1950:
                        # Split only if absolutely necessary
                        response_parts = await self.split_long_response(response)
                        await message.reply(response_parts[0], mention_author=False)

                        # Send remaining parts with minimal delay
                        for part in response_parts[1:]:
                            await asyncio.sleep(
                                0.5
                            )  # Reduced delay for faster delivery
                            await message.channel.send(part)
                    else:
                        # Direct reply for optimal user experience
                        await message.reply(response, mention_author=False)

                    # Performance logging (only for slow responses)
                    total_time = time.perf_counter() - start_time
                    if total_time > 2.0:  # Only log if slower than 2 seconds
                        self.logger.info(f"⏱️ Response time: {total_time:.2f}s")

                else:
                    # Fallback response for better UX
                    fallback_responses = [
                        "I'm here! Though my thoughts are a bit scattered right now. 🤖",
                        "Hi there! Give me a moment to gather my digital thoughts! ✨",
                        "Hey! I'm processing... sometimes my circuits need a quick refresh! 🔄",
                    ]
                    await message.reply(
                        random.choice(fallback_responses), mention_author=False
                    )

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
        name="admin_help", description="📖 Learn about natural language admin commands"
    )
    async def admin_help(self, interaction: discord.Interaction):
        """Show help for natural language administrative commands"""
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "❌ You need manage messages permission to use admin commands.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="🤖 Natural Language Admin Commands",
            description="You can now use natural language to perform admin actions! Just type commands like you're talking to Astra.",
            color=0x00BFFF,
            timestamp=datetime.now(timezone.utc),
        )

        # Message Management
        embed.add_field(
            name="💬 Message Management",
            value="• `Astra, delete that message`\n"
            "• `Delete the last 5 messages`\n"
            "• `Clean up this channel`\n"
            "• `Clear the recent messages`",
            inline=False,
        )

        # User Moderation
        embed.add_field(
            name="👤 User Moderation",
            value="• `Kick @username` or `Kick that user`\n"
            "• `Timeout @username for 10 minutes`\n"
            "• `Mute that person for 1 hour`\n"
            "• `Ban @username for spamming`",
            inline=False,
        )

        # Role Management
        embed.add_field(
            name="🎭 Role Management",
            value="• `Give @username the Member role`\n"
            "• `Add the VIP role to @username`\n"
            "• `Remove the Muted role from @username`\n"
            "• `Take the Guest role from that user`",
            inline=False,
        )

        # Channel Management
        embed.add_field(
            name="🔒 Channel Management",
            value="• `Lock this channel`\n"
            "• `Unlock here`\n"
            "• `Disable this channel`\n"
            "• `Enable channel`",
            inline=False,
        )

        embed.add_field(
            name="✨ Smart Features",
            value="• **Flexible phrasing**: Use natural language\n"
            "• **Context aware**: Reference users and roles naturally\n"
            "• **Permission checking**: Automatic permission validation\n"
            "• **Safety checks**: Can't affect higher-ranked users",
            inline=False,
        )

        embed.add_field(
            name="🛡️ Required Permissions",
            value="• **Manage Messages**: For message deletion and bulk actions\n"
            "• **Kick Members**: For kick commands\n"
            "• **Ban Members**: For ban commands\n"
            "• **Moderate Members**: For timeout/mute commands\n"
            "• **Manage Roles**: For role assignment commands\n"
            "• **Manage Channels**: For lock/unlock commands",
            inline=False,
        )

        embed.set_footer(
            text="💡 Tip: You can also mention users or reply to messages for context!"
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="test-astra",
        description="🧪 Test Astra's response system (debug command)",
    )
    async def test_astra(
        self, interaction: discord.Interaction, message: str = "Hello Astra!"
    ):
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

            mock_message = MockMessage(
                message, interaction.user, interaction.guild, interaction.channel
            )

            # Get personality profile - handle DM case
            guild_id = interaction.guild.id if interaction.guild else 0  # Use 0 for DMs
            profile = await self.get_personality_profile(interaction.user.id, guild_id)
            context = await self._analyze_message_context(mock_message)

            # Generate response
            response = await self.generate_astra_response(
                mock_message, profile, context
            )

            embed = discord.Embed(
                title="🧪 Astra Response Test", color=0x7C4DFF, timestamp=datetime.now()
            )
            embed.add_field(
                name="Input",
                value=f"```{message[:500]}{'...' if len(message) > 500 else ''}```",
                inline=False,
            )

            # Truncate response for embed field (max 1000 chars to leave room for formatting)
            if response:
                truncated_output = (
                    response[:900] + "..." if len(response) > 900 else response
                )
                embed.add_field(
                    name="Output", value=f"```{truncated_output}```", inline=False
                )
                embed.color = 0x00FF00
                embed.add_field(name="Status", value="✅ Success", inline=True)
                embed.add_field(
                    name="Length", value=f"{len(response)} chars", inline=True
                )
            else:
                embed.add_field(
                    name="Output", value="```No response generated```", inline=False
                )
                embed.color = 0xFF0000
                embed.add_field(name="Status", value="❌ Failed", inline=True)

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"❌ Test command error: {e}")
            import traceback

            self.logger.error(f"📋 Traceback: {traceback.format_exc()}")

            embed = discord.Embed(
                title="❌ Test Failed", description=f"Error: {str(e)}", color=0xFF0000
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
        # Handle DM case where guild is None
        guild_id = interaction.guild.id if interaction.guild else 0  # Use 0 for DMs
        profile = await self.get_personality_profile(interaction.user.id, guild_id)

        if preset:
            # Apply preset
            if preset in self.PERSONALITY_PRESETS:
                profile.base_personality = self.PERSONALITY_PRESETS[preset]
                profile.updated_at = datetime.now()

                embed = discord.Embed(
                    title="🎭 Companion Personality Updated",
                    description=f"Applied **{preset.title()}** personality preset for Astra!\n\n*Changes will take effect immediately in conversations.*",
                    color=0x7289DA,
                )

                # Show new personality values
                personality_text = "\n".join(
                    [
                        f"**{trait.title()}:** {value:.1f}/1.0 {'🔥' if value > 0.7 else '❄️' if value < 0.3 else '⚖️'}"
                        for trait, value in profile.base_personality.to_dict().items()
                    ]
                )
                embed.add_field(
                    name="New Personality Traits", value=personality_text, inline=False
                )

                # Add behavior preview
                dominant_traits = self._get_dominant_traits(profile.base_personality)
                behavior_preview = self._create_behavior_preview(
                    profile.base_personality, dominant_traits
                )
                embed.add_field(
                    name="🎯 Expected Behavior Changes",
                    value=behavior_preview,
                    inline=False,
                )

                # Add test suggestion
                embed.add_field(
                    name="💡 Test the Changes",
                    value="Try talking to me now to see the personality changes in action!",
                    inline=False,
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
                old_value = getattr(profile.base_personality, trait.lower())
                setattr(profile.base_personality, trait.lower(), value)
                profile.updated_at = datetime.now()

                # Determine intensity change
                intensity_change = (
                    "🔥 High" if value > 0.7 else "❄️ Low" if value < 0.3 else "⚖️ Medium"
                )
                change_direction = (
                    "⬆️" if value > old_value else "⬇️" if value < old_value else "➡️"
                )

                embed = discord.Embed(
                    title="🎭 Companion Trait Updated",
                    description=f"Set **{trait.title()}** to **{value:.1f}** for Astra!\n\n*{change_direction} Changed from {old_value:.1f} to {value:.1f}*",
                    color=0x7289DA,
                )

                # Explain what this change means behaviorally
                behavior_explanation = self._explain_trait_behavior_change(
                    trait.lower(), value
                )
                embed.add_field(
                    name=f"{intensity_change} What This Means",
                    value=behavior_explanation,
                    inline=False,
                )

                embed.add_field(
                    name="💡 Test It Now",
                    value=f"Try asking me something to see how my {trait.lower()} behavior has changed!",
                    inline=False,
                )

            else:
                embed = discord.Embed(
                    title="❌ Invalid Trait or Value",
                    description="Please specify a valid trait and value (0.0-1.0).\n\nValid traits: analytical, empathetic, curious, creative, supportive, playful, assertive, adaptable",
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
                "New Friend"
                if interaction_count < 5
                else (
                    "Good Friend"
                    if interaction_count < 20
                    else "Close Friend" if interaction_count < 50 else "Best Friend"
                )
            )

            embed.add_field(
                name="� Your Relationship with Astra",
                value=f"**Level:** {relationship_level}\n**Interactions:** {interaction_count}\n**Last Mood:** {profile.modifiers.user_mood:.1f}/1.0\n**Channel Preference:** {profile.modifiers.channel_type.title()}",
                inline=True,
            )

            # System awareness - show AI client status
            ai_status = "🟢 Online" if self.ai_client.is_available() else "🔴 Offline"
            ai_provider = (
                self.ai_client.provider.value
                if hasattr(self.ai_client, "provider")
                else "Unknown"
            )

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
                cog_commands = [
                    cmd
                    for cmd in bot_commands
                    if hasattr(cmd, "callback")
                    and cmd.callback.__module__.endswith(cog_name.lower())
                ]
                cog_command_counts[cog_name] = len(cog_commands)

            # AI Client status
            ai_client_available = self.ai_client.is_available()
            ai_provider = (
                self.ai_client.provider.value
                if hasattr(self.ai_client, "provider")
                else "Unknown"
            )
            ai_model = getattr(self.ai_client, "model", "Unknown")

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
                perf_value = (
                    f"**CPU Usage:** {cpu_percent:.1f}%\n**Memory:** {memory_percent:.1f}%\n"
                    + perf_value
                )
            else:
                perf_value = "**System Metrics:** Unavailable\n" + perf_value

            embed.add_field(
                name="⚡ Performance",
                value=perf_value,
                inline=True,
            )

            # Top Cogs by Command Count
            top_cogs = sorted(
                cog_command_counts.items(), key=lambda x: x[1], reverse=True
            )[:3]
            cog_stats = "\n".join(
                [f"**{cog}:** {count} commands" for cog, count in top_cogs]
            )
            embed.add_field(
                name="📊 Top Cogs",
                value=cog_stats if cog_stats else "No command data",
                inline=True,
            )

            # System Health Summary
            health_indicators = []
            if ai_client_available:
                health_indicators.append("🟢 AI Online")
            else:
                health_indicators.append("🔴 AI Offline")

            if db_healthy:
                health_indicators.append("🟢 DB Healthy")
            else:
                health_indicators.append("🔴 DB Issues")

            if cpu_percent < 80:
                health_indicators.append("🟢 CPU Good")
            else:
                health_indicators.append("🟡 CPU High")

            if memory_percent < 80:
                health_indicators.append("🟢 Memory Good")
            else:
                health_indicators.append("🟡 Memory High")

            embed.add_field(
                name="🏥 Health Status",
                value="\n".join(health_indicators),
                inline=True,
            )

            # Add footer with scan time
            scan_time = time.perf_counter() - start_time
            embed.set_footer(
                text=f"System scan completed in {scan_time:.3f}s • Astra v2.0.0"
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in system_status command: {e}")
            error_embed = discord.Embed(
                title="❌ System Status Error",
                description=f"Unable to retrieve system status: {str(e)}",
                color=0xFF0000,
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
            if hasattr(self.bot, "start_time"):
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
            success_rate = (
                len(self.response_times)
                / max(self.interaction_count, len(self.response_times))
            ) * 100
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
                if hasattr(cmd, "callback") and cmd.callback:
                    callback_module = cmd.callback.__module__
                    if "cogs." in callback_module:
                        cog_name = (
                            callback_module.split("cogs.")[1].replace("_", " ").title()
                        )

                    # Find the actual cog instance
                    for cog_key, cog_instance in self.bot.cogs.items():
                        if (
                            callback_module.endswith(cog_key.lower())
                            or cog_key.lower() in callback_module
                        ):
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
                    remaining_cogs = len(cog_commands) - len(
                        [
                            c
                            for c in cog_commands
                            if c in [field.name for field in embed.fields]
                        ]
                    )
                    embed.add_field(
                        name="📋 Additional Commands",
                        value=f"**{remaining_cogs}** more command categories available.\nUse `/system_status` for detailed system info.",
                        inline=False,
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
                        inline=False,
                    )
                    command_count += 1

            # Add summary footer
            total_cogs = len([cog for cog in self.bot.cogs.keys()])
            embed.set_footer(
                text=f"Total: {len(bot_commands)} commands across {total_cogs} modules • Use /help for detailed command info"
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in commands_list command: {e}")
            error_embed = discord.Embed(
                title="❌ Commands List Error",
                description=f"Unable to retrieve commands list: {str(e)}",
                color=0xFF0000,
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
            provider = (
                self.ai_client.provider.value
                if hasattr(self.ai_client, "provider")
                else "Unknown"
            )
            model = getattr(self.ai_client, "model", "Unknown")

            embed.add_field(
                name=f"{status_icon} Connection Status",
                value=f"**Available:** {'Yes' if self.ai_client.is_available() else 'No'}\n**Provider:** {provider}\n**Model:** {model}",
                inline=True,
            )

            # AI Configuration
            temperature = getattr(self.ai_client, "temperature", 0.7)
            max_tokens = getattr(self.ai_client, "max_tokens", 2000)

            embed.add_field(
                name="⚙️ Configuration",
                value=f"**Temperature:** {temperature}\n**Max Tokens:** {max_tokens:,}\n**Context Messages:** {getattr(self.ai_client, 'max_context_messages', 8)}",
                inline=True,
            )

            # AI Features
            features = []
            if getattr(self.ai_client, "enable_emotional_intelligence", False):
                features.append("🧠 Emotional Intelligence")
            if getattr(self.ai_client, "enable_topic_tracking", False):
                features.append("📊 Topic Tracking")
            if getattr(self.ai_client, "enable_memory_system", False):
                features.append("💾 Memory System")

            embed.add_field(
                name="✨ Features",
                value="\n".join(features) if features else "Basic AI responses",
                inline=True,
            )

            # Performance Stats
            total_contexts = len(getattr(self.ai_client, "conversation_contexts", {}))
            total_memories = len(getattr(self.ai_client, "user_memories", {}))

            embed.add_field(
                name="📊 AI Performance",
                value=f"**Active Contexts:** {total_contexts}\n**User Memories:** {total_memories}\n**Avg Response:** {sum(self.response_times) / len(self.response_times) if self.response_times else 0:.2f}s",
                inline=True,
            )

            # Provider-specific info
            if hasattr(self.ai_client, "config") and provider in self.ai_client.config:
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
                (
                    await self.ai_client.test_connection()
                    if hasattr(self.ai_client, "test_connection")
                    else True
                )
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
                color=0xFF0000,
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
        ai_provider = (
            self.ai_client.provider.value
            if hasattr(self.ai_client, "provider")
            else "Unknown"
        )
        embed.add_field(
            name="🤖 AI Client",
            value=f"**Status:** {ai_status}\n**Provider:** {ai_provider}",
            inline=True,
        )

        embed.set_footer(text="Powered by Astra's Advanced AI Personality System")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # /companion_chat command removed - Focus on natural conversation!
    # Users can now simply mention @Astra or talk naturally for better interaction

    @app_commands.command(
        name="test_personality",
        description="🧪 Test current personality settings with a sample response",
    )
    async def test_personality_command(self, interaction: discord.Interaction):
        """Test the current personality settings with a sample response"""
        await interaction.response.defer()

        user_id = interaction.user.id
        guild_id = interaction.guild.id if interaction.guild else 0  # Use 0 for DMs

        try:
            # Get current personality profile
            profile = await self.get_personality_profile(user_id, guild_id)
            personality = profile.personality_dimensions
            dominant_traits = self._get_dominant_traits(personality)

            # Show personality preview
            preview = self._create_behavior_preview(personality, dominant_traits)

            embed = discord.Embed(
                title="🌟 Personality Test Results",
                description=f"**Current Dominant Traits:**\n{preview}",
                color=0x7289DA,
            )

            # Generate actual test response with personality
            test_message = (
                "Tell me about space exploration and what excites you most about it!"
            )

            # Create mock message for testing
            class MockMessage:
                def __init__(self, content, author, guild, channel):
                    self.content = content
                    self.author = author
                    self.guild = guild
                    self.channel = channel

            mock_message = MockMessage(
                test_message, interaction.user, interaction.guild, interaction.channel
            )

            # Get context and generate response
            context = await self._analyze_message_context(mock_message)
            ai_response = await self.generate_astra_response(
                mock_message, profile, context
            )

            embed.add_field(name="📋 Test Question", value=test_message, inline=False)

            embed.add_field(
                name="🤖 Astra's Response (With Current Personality)",
                value=ai_response[:1024] if ai_response else "No response generated",
                inline=False,
            )

            embed.add_field(
                name="💡 Tip",
                value="Use `/companion` to adjust these settings and see immediate changes!",
                inline=False,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in personality test: {e}")
            await interaction.followup.send(f"❌ Error testing personality: {str(e)}")

    @app_commands.command(
        name="quick_personality",
        description="⚡ Quickly adjust one personality trait and see immediate behavior change",
    )
    @app_commands.describe(
        trait="The personality trait to adjust (analytical, empathetic, curious, creative, supportive, playful, assertive, adaptable)",
        value="The new value for the trait (0.0 to 1.0)",
    )
    async def quick_personality_adjustment(
        self, interaction: discord.Interaction, trait: str, value: float
    ):
        """Quickly adjust one personality trait and see immediate behavior change"""
        await interaction.response.defer()

        trait = trait.lower()
        valid_traits = [
            "analytical",
            "empathetic",
            "curious",
            "creative",
            "supportive",
            "playful",
            "assertive",
            "adaptable",
        ]

        if trait not in valid_traits:
            await interaction.followup.send(
                f"❌ Invalid trait. Choose from: {', '.join(valid_traits)}"
            )
            return

        if not 0.0 <= value <= 1.0:
            await interaction.followup.send("❌ Value must be between 0.0 and 1.0")
            return

        user_id = interaction.user.id
        guild_id = interaction.guild.id if interaction.guild else 0  # Use 0 for DMs

        try:
            # Get and update personality profile
            profile = await self.get_personality_profile(user_id, guild_id)
            setattr(profile.personality_dimensions, trait, value)

            # Save the updated profile
            self.user_profiles[user_id] = profile

            # Show immediate behavior change
            behavior_change = self._explain_trait_behavior_change(trait, value)

            embed = discord.Embed(
                title=f"⚡ Quick Personality Update: {trait.title()}",
                description=f"**New Value:** {value:.1f}\n**Behavior Change:** {behavior_change}",
                color=0x00FF00,
            )

            # Generate a test response to show the change
            test_message = f"Give me a quick example of {trait} thinking!"

            # Create mock message for testing
            class MockMessage:
                def __init__(self, content, author, guild, channel):
                    self.content = content
                    self.author = author
                    self.guild = guild
                    self.channel = channel

            mock_message = MockMessage(
                test_message, interaction.user, interaction.guild, interaction.channel
            )

            # Get context and generate response with new personality
            context = await self._analyze_message_context(mock_message)
            ai_response = await self.generate_astra_response(
                mock_message, profile, context
            )

            embed.add_field(
                name="🧪 Immediate Test Response",
                value=ai_response[:512] if ai_response else "No response generated",
                inline=False,
            )

            embed.add_field(
                name="💡 Tip",
                value="The change is applied immediately! Try chatting with Astra to see the difference.",
                inline=False,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in quick personality adjustment: {e}")
            await interaction.followup.send(f"❌ Error adjusting personality: {str(e)}")


async def setup(bot):
    await bot.add_cog(AstraAICompanion(bot))
