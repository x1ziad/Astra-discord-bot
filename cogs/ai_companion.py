"""""""""""""""

AI Companion - Astra's Conversational Heart

Advanced AI Companion with Comprehensive Personality System🤖 AI Companion - Astra's Conversational Heart



This module implements the complete Astra Personality System with:Advanced AI Companion with Comprehensive Personality System🤖 AI Companion - Astra's Conversational Heart

- Dynamic personality adaptation

- Multi-dimensional personality traits

- Context-aware behavior modification

- Performance-optimized response pipelineThis module implements the complete Astra Personality System with:Advanced AI Companion with Comprehensive Personality System🤖 AI Companion - Astra's Conversational HeartAdvanced AI Companion for Astra Bot

- Comprehensive slash command interface

"""- Dynamic personality adaptation



import asyncio- Multi-dimensional personality traits

import json

import logging- Context-aware behavior modification

import random

import time- Performance-optimized response pipelineThis module implements the complete Astra Personality System with:Enhanced companion system with authentic Astra personalityProvides intelligent conversation, contextual responses, and personality-driven interactions

from datetime import datetime, timedelta

from typing import Dict, List, Optional, Tuple, Any, Union- Comprehensive slash command interface

from dataclasses import dataclass, field

"""- Dynamic personality adaptation

import discord

from discord.ext import commands, tasks

from discord import app_commands

import asyncio- Multi-dimensional personality traits"""

from ai.universal_ai_client import UniversalAIClient

from ai.universal_context_manager import UniversalContextManagerimport json



# Try importing optional dependenciesimport logging- Context-aware behavior modification

try:

    from utils.database import Databaseimport random

except ImportError:

    Database = Noneimport time- Performance-optimized response pipelineFeatures:



try:from datetime import datetime, timedelta

    from utils.security import SecurityManager

except ImportError:from typing import Dict, List, Optional, Tuple, Any, Union- Comprehensive slash command interface

    SecurityManager = None

from dataclasses import dataclass, field

try:

    from utils.performance import PerformanceMonitor"""- Natural conversation with context awarenessimport discord

except ImportError:

    PerformanceMonitor = Noneimport discord



try:from discord.ext import commands, tasks

    import redis

except ImportError:from discord import app_commands

    redis = None

import asyncio- Mood tracking and personalized responses  from discord.ext import commands

import hashlib

from concurrent.futures import ThreadPoolExecutorfrom ai.universal_ai_client import UniversalAIClient



# Personality System Data Modelsfrom ai.universal_context_manager import UniversalContextManagerimport json

@dataclass

class PersonalityDimensions:from utils.database import Database

    """Core personality dimensions for Astra"""

    analytical: float = 0.8  # Logical, systematic thinkingfrom utils.security import SecurityManagerimport logging- Multi-language support with automatic detectionimport asyncio

    empathetic: float = 0.9  # Understanding and relating to emotions

    curious: float = 0.95    # Drive to explore and learnfrom utils.performance import PerformanceMonitor

    creative: float = 0.85   # Innovative and imaginative responses

    supportive: float = 0.9  # Helpful and encouraging natureimport random

    playful: float = 0.7     # Humor and lightheartedness

    assertive: float = 0.6   # Confidence in expressing views# Performance and caching imports

    adaptable: float = 0.9   # Flexibility in different contexts

try:import time- Proactive engagement and daily check-insimport logging

@dataclass

class ContextualModifiers:    import redis

    """Context-specific personality adjustments"""

    user_mood: float = 0.0except ImportError:from datetime import datetime, timedelta

    conversation_tone: float = 0.0

    topic_complexity: float = 0.0    redis = None

    user_expertise: float = 0.0

    time_of_day: float = 0.0from typing import Dict, List, Optional, Tuple, Any, Union- Enhanced response generation with personalityimport re

    recent_interactions: float = 0.0

import hashlib

@dataclass

class PersonalityProfile:from concurrent.futures import ThreadPoolExecutorfrom dataclasses import dataclass, field

    """Complete personality profile for a guild/user"""

    guild_id: int

    user_id: Optional[int] = None

    dimensions: PersonalityDimensions = field(default_factory=PersonalityDimensions)# Personality System Data Models- Activity tracking and user preferencesfrom datetime import datetime, timezone

    modifiers: ContextualModifiers = field(default_factory=ContextualModifiers)

    mode: str = "balanced"@dataclass

    created_at: datetime = field(default_factory=datetime.utcnow)

    updated_at: datetime = field(default_factory=datetime.utcnow)class PersonalityDimensions:import discord

    adaptation_enabled: bool = True

    interaction_count: int = 0    """Core personality dimensions for Astra"""

    last_interaction: Optional[datetime] = None

    analytical: float = 0.8  # Logical, systematic thinkingfrom discord.ext import commands, tasks"""from typing import Optional, Dict, Any, List

class PersonalityBehaviorEngine:

    """Core personality behavior processing engine"""    empathetic: float = 0.9  # Understanding and relating to emotions

    

    def __init__(self):    curious: float = 0.95    # Drive to explore and learnfrom discord import app_commands

        self.personality_modes = {

            "balanced": PersonalityDimensions(),    creative: float = 0.85   # Innovative and imaginative responses

            "professional": PersonalityDimensions(

                analytical=0.95, empathetic=0.7, curious=0.8, creative=0.6,    supportive: float = 0.9  # Helpful and encouraging nature

                supportive=0.85, playful=0.3, assertive=0.8, adaptable=0.7

            ),    playful: float = 0.7     # Humor and lightheartedness

            "casual": PersonalityDimensions(

                analytical=0.6, empathetic=0.85, curious=0.9, creative=0.8,    assertive: float = 0.6   # Confidence in expressing viewsfrom ai.universal_ai_client import UniversalAIClient

                supportive=0.9, playful=0.9, assertive=0.5, adaptable=0.95

            ),    adaptable: float = 0.9   # Flexibility in different contexts

            "creative": PersonalityDimensions(

                analytical=0.7, empathetic=0.8, curious=0.98, creative=0.98,from ai.universal_context_manager import UniversalContextManagerimport asynciofrom ai.universal_ai_client import UniversalAIClient

                supportive=0.8, playful=0.85, assertive=0.7, adaptable=0.9

            ),@dataclass

            "analytical": PersonalityDimensions(

                analytical=0.98, empathetic=0.6, curious=0.95, creative=0.7,class ContextualModifiers:from utils.database import Database

                supportive=0.75, playful=0.4, assertive=0.85, adaptable=0.6

            )    """Context-specific personality adjustments"""

        }

        user_mood: float = 0.0from utils.security import SecurityManagerimport jsonfrom ai.universal_context_manager import UniversalContextManager

    def calculate_personality_vector(self, profile: PersonalityProfile, context: Dict[str, Any]) -> PersonalityDimensions:

        """Calculate the current personality vector based on profile and context"""    conversation_tone: float = 0.0

        base_dimensions = self.personality_modes.get(profile.mode, self.personality_modes["balanced"])

            topic_complexity: float = 0.0from utils.performance import PerformanceMonitor

        # Apply contextual modifiers

        modified_dimensions = PersonalityDimensions(    user_expertise: float = 0.0

            analytical=max(0.1, min(1.0, base_dimensions.analytical + profile.modifiers.topic_complexity * 0.2)),

            empathetic=max(0.1, min(1.0, base_dimensions.empathetic + profile.modifiers.user_mood * 0.3)),    time_of_day: float = 0.0import loggingfrom core.unified_security_system import UnifiedSecuritySystem

            curious=max(0.1, min(1.0, base_dimensions.curious + profile.modifiers.recent_interactions * 0.1)),

            creative=max(0.1, min(1.0, base_dimensions.creative + profile.modifiers.conversation_tone * 0.2)),    recent_interactions: float = 0.0

            supportive=max(0.1, min(1.0, base_dimensions.supportive + profile.modifiers.user_mood * 0.2)),

            playful=max(0.1, min(1.0, base_dimensions.playful + profile.modifiers.time_of_day * 0.3)),# Performance and caching imports

            assertive=max(0.1, min(1.0, base_dimensions.assertive + profile.modifiers.user_expertise * 0.2)),

            adaptable=max(0.1, min(1.0, base_dimensions.adaptable + profile.modifiers.conversation_tone * 0.1))@dataclass

        )

        class PersonalityProfile:import redisimport randomfrom logger.enhanced_logger import setup_enhanced_logger

        return modified_dimensions

        """Complete personality profile for a guild/user"""

    def generate_personality_prompt(self, dimensions: PersonalityDimensions, context: Dict[str, Any]) -> str:

        """Generate personality-infused system prompt"""    guild_id: intimport hashlib

        prompt_parts = [

            "You are Astra, an advanced AI companion with a dynamic personality.",    user_id: Optional[int] = None

            f"Your current personality configuration:",

            f"- Analytical thinking: {dimensions.analytical:.1f}/1.0 ({'High' if dimensions.analytical > 0.8 else 'Moderate' if dimensions.analytical > 0.5 else 'Low'})",    dimensions: PersonalityDimensions = field(default_factory=PersonalityDimensions)from concurrent.futures import ThreadPoolExecutorimport refrom utils.response_enhancer import ResponseEnhancer

            f"- Empathy and understanding: {dimensions.empathetic:.1f}/1.0 ({'High' if dimensions.empathetic > 0.8 else 'Moderate' if dimensions.empathetic > 0.5 else 'Low'})",

            f"- Curiosity and exploration: {dimensions.curious:.1f}/1.0 ({'High' if dimensions.curious > 0.8 else 'Moderate' if dimensions.curious > 0.5 else 'Low'})",    modifiers: ContextualModifiers = field(default_factory=ContextualModifiers)

            f"- Creativity and innovation: {dimensions.creative:.1f}/1.0 ({'High' if dimensions.creative > 0.8 else 'Moderate' if dimensions.creative > 0.5 else 'Low'})",

            f"- Supportive nature: {dimensions.supportive:.1f}/1.0 ({'High' if dimensions.supportive > 0.8 else 'Moderate' if dimensions.supportive > 0.5 else 'Low'})",    mode: str = "balanced"  # balanced, professional, casual, creative, analytical

            f"- Playfulness and humor: {dimensions.playful:.1f}/1.0 ({'High' if dimensions.playful > 0.8 else 'Moderate' if dimensions.playful > 0.5 else 'Low'})",

            f"- Assertiveness: {dimensions.assertive:.1f}/1.0 ({'High' if dimensions.assertive > 0.8 else 'Moderate' if dimensions.assertive > 0.5 else 'Low'})",    created_at: datetime = field(default_factory=datetime.utcnow)

            f"- Adaptability: {dimensions.adaptable:.1f}/1.0 ({'High' if dimensions.adaptable > 0.8 else 'Moderate' if dimensions.adaptable > 0.5 else 'Low'})",

            "",    updated_at: datetime = field(default_factory=datetime.utcnow)# Personality System Data Modelsimport timefrom utils.astra_personality import get_personality_core, AstraMode

            "Respond authentically according to these personality dimensions.",

            "Maintain coherence and consistency while adapting to the conversation context."    adaptation_enabled: bool = True

        ]

            interaction_count: int = 0@dataclass

        return "\n".join(prompt_parts)

    last_interaction: Optional[datetime] = None

class PersonalityAdaptationEngine:

    """Handles automatic personality adaptation based on user interactions"""class PersonalityDimensions:from datetime import datetime, timedelta, timezonefrom ui.embeds import EmbedBuilder

    

    def __init__(self):class PersonalityBehaviorEngine:

        self.adaptation_weights = {

            "positive_feedback": 0.1,    """Core personality behavior processing engine"""    """Core personality dimensions for Astra"""

            "engagement_level": 0.15,

            "conversation_length": 0.05,    

            "topic_interest": 0.2,

            "response_quality": 0.25,    def __init__(self):    analytical: float = 0.8  # Logical, systematic thinkingfrom typing import Dict, List, Optional, Set, Any

            "user_satisfaction": 0.25

        }        self.personality_modes = {

    

    async def analyze_interaction(self, message: discord.Message, response: str, user_reaction: Optional[str] = None) -> Dict[str, float]:            "balanced": PersonalityDimensions(),    empathetic: float = 0.9  # Understanding and relating to emotions

        """Analyze interaction quality and user satisfaction"""

        analysis = {            "professional": PersonalityDimensions(

            "engagement_score": 0.5,

            "satisfaction_score": 0.5,                analytical=0.95, empathetic=0.7, curious=0.8, creative=0.6,    curious: float = 0.95    # Drive to explore and learnfrom dataclasses import dataclass, fieldimport discord

            "topic_alignment": 0.5,

            "response_appropriateness": 0.5                supportive=0.85, playful=0.3, assertive=0.8, adaptable=0.7

        }

                    ),    creative: float = 0.85   # Innovative and imaginative responses

        # Analyze message length and complexity

        message_length = len(message.content.split())            "casual": PersonalityDimensions(

        if message_length > 20:

            analysis["engagement_score"] += 0.2                analytical=0.6, empathetic=0.85, curious=0.9, creative=0.8,    supportive: float = 0.9  # Helpful and encouraging naturefrom pathlib import Pathfrom discord import app_commands

        elif message_length > 10:

            analysis["engagement_score"] += 0.1                supportive=0.9, playful=0.9, assertive=0.5, adaptable=0.95

        

        # Analyze user reactions (if available)            ),    playful: float = 0.7     # Humor and lightheartedness

        if user_reaction:

            if user_reaction in ["👍", "❤️", "😊", "🔥", "✅"]:            "creative": PersonalityDimensions(

                analysis["satisfaction_score"] = 0.9

            elif user_reaction in ["👎", "😕", "❌"]:                analytical=0.7, empathetic=0.8, curious=0.98, creative=0.98,    assertive: float = 0.6   # Confidence in expressing viewsfrom discord.ext import commands, tasks

                analysis["satisfaction_score"] = 0.1

                        supportive=0.8, playful=0.85, assertive=0.7, adaptable=0.9

        # Quick response quality estimation

        response_length = len(response.split())            ),    adaptable: float = 0.9   # Flexibility in different contexts

        if 10 <= response_length <= 200:

            analysis["response_appropriateness"] += 0.2            "analytical": PersonalityDimensions(

        

        return analysis                analytical=0.98, empathetic=0.6, curious=0.95, creative=0.7,import discordfrom typing import Optional, List, Dict, Any, Union

    

    async def adapt_personality(self, profile: PersonalityProfile, interaction_analysis: Dict[str, float]) -> PersonalityProfile:                supportive=0.75, playful=0.4, assertive=0.85, adaptable=0.6

        """Adapt personality based on interaction analysis"""

        if not profile.adaptation_enabled:            )@dataclass

            return profile

                }

        # Calculate adaptation magnitude

        adaptation_strength = min(0.05, interaction_analysis.get("engagement_score", 0.5) * 0.1)    class ContextualModifiers:from discord import app_commandsimport asyncio

        

        # Adapt dimensions based on successful interactions    def calculate_personality_vector(self, profile: PersonalityProfile, context: Dict[str, Any]) -> PersonalityDimensions:

        if interaction_analysis.get("satisfaction_score", 0.5) > 0.7:

            # Positive feedback - reinforce current approach        """Calculate the current personality vector based on profile and context"""    """Context-specific personality adjustments"""

            if interaction_analysis.get("topic_alignment", 0.5) > 0.7:

                profile.dimensions.analytical += adaptation_strength * 0.5        base_dimensions = self.personality_modes.get(profile.mode, self.personality_modes["balanced"])

                profile.dimensions.curious += adaptation_strength * 0.3

                        user_mood: float = 0.0from discord.ext import commands, tasksimport json

            if interaction_analysis.get("engagement_score", 0.5) > 0.7:

                profile.dimensions.empathetic += adaptation_strength * 0.4        # Apply contextual modifiers

                profile.dimensions.supportive += adaptation_strength * 0.3

                modified_dimensions = PersonalityDimensions(    conversation_tone: float = 0.0

        # Normalize dimensions to stay within bounds

        for attr in ['analytical', 'empathetic', 'curious', 'creative', 'supportive', 'playful', 'assertive', 'adaptable']:            analytical=max(0.1, min(1.0, base_dimensions.analytical + profile.modifiers.topic_complexity * 0.2)),

            current_value = getattr(profile.dimensions, attr)

            setattr(profile.dimensions, attr, max(0.1, min(1.0, current_value)))            empathetic=max(0.1, min(1.0, base_dimensions.empathetic + profile.modifiers.user_mood * 0.3)),    topic_complexity: float = 0.0import time

        

        profile.updated_at = datetime.utcnow()            curious=max(0.1, min(1.0, base_dimensions.curious + profile.modifiers.recent_interactions * 0.1)),

        profile.interaction_count += 1

        profile.last_interaction = datetime.utcnow()            creative=max(0.1, min(1.0, base_dimensions.creative + profile.modifiers.conversation_tone * 0.2)),    user_expertise: float = 0.0

        

        return profile            supportive=max(0.1, min(1.0, base_dimensions.supportive + profile.modifiers.user_mood * 0.2)),



class PersonalityPersistenceManager:            playful=max(0.1, min(1.0, base_dimensions.playful + profile.modifiers.time_of_day * 0.3)),    time_of_day: float = 0.0# AI Importsimport random

    """Handles personality data persistence with caching"""

                assertive=max(0.1, min(1.0, base_dimensions.assertive + profile.modifiers.user_expertise * 0.2)),

    def __init__(self, database=None):

        self.db = database            adaptable=max(0.1, min(1.0, base_dimensions.adaptable + profile.modifiers.conversation_tone * 0.1))    recent_interactions: float = 0.0

        self.cache = {}

        self.cache_ttl = 3600        )

        

        try:        try:from datetime import datetime, timedelta, timezone

            if redis:

                self.redis_client = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)        return modified_dimensions

                self.redis_available = True

            else:    @dataclass

                self.redis_available = False

        except:    def generate_personality_prompt(self, dimensions: PersonalityDimensions, context: Dict[str, Any]) -> str:

            self.redis_available = False

            logging.warning("Redis not available, using memory cache only")        """Generate personality-infused system prompt"""class PersonalityProfile:    from ai.universal_ai_client import UniversalAIClientfrom pathlib import Path

    

    def _get_cache_key(self, guild_id: int, user_id: Optional[int] = None) -> str:        prompt_parts = [

        """Generate cache key for personality profile"""

        return f"personality:{guild_id}:{user_id or 'default'}"            "You are Astra, an advanced AI companion with a dynamic personality.",    """Complete personality profile for a guild/user"""

    

    async def get_personality_profile(self, guild_id: int, user_id: Optional[int] = None) -> PersonalityProfile:            f"Your current personality configuration:",

        """Retrieve personality profile with caching"""

        cache_key = self._get_cache_key(guild_id, user_id)            f"- Analytical thinking: {dimensions.analytical:.1f}/1.0 ({'High' if dimensions.analytical > 0.8 else 'Moderate' if dimensions.analytical > 0.5 else 'Low'})",    guild_id: int    from ai.enhanced_ai_config import EnhancedAIConfigimport re

        

        # Try Redis cache first            f"- Empathy and understanding: {dimensions.empathetic:.1f}/1.0 ({'High' if dimensions.empathetic > 0.8 else 'Moderate' if dimensions.empathetic > 0.5 else 'Low'})",

        if self.redis_available:

            try:            f"- Curiosity and exploration: {dimensions.curious:.1f}/1.0 ({'High' if dimensions.curious > 0.8 else 'Moderate' if dimensions.curious > 0.5 else 'Low'})",    user_id: Optional[int] = None

                cached_data = self.redis_client.get(cache_key)

                if cached_data:            f"- Creativity and innovation: {dimensions.creative:.1f}/1.0 ({'High' if dimensions.creative > 0.8 else 'Moderate' if dimensions.creative > 0.5 else 'Low'})",

                    profile_data = json.loads(cached_data)

                    return self._deserialize_profile(profile_data)            f"- Supportive nature: {dimensions.supportive:.1f}/1.0 ({'High' if dimensions.supportive > 0.8 else 'Moderate' if dimensions.supportive > 0.5 else 'Low'})",    dimensions: PersonalityDimensions = field(default_factory=PersonalityDimensions)    AI_AVAILABLE = Trueimport calendar

            except Exception as e:

                logging.warning(f"Redis cache error: {e}")            f"- Playfulness and humor: {dimensions.playful:.1f}/1.0 ({'High' if dimensions.playful > 0.8 else 'Moderate' if dimensions.playful > 0.5 else 'Low'})",

        

        # Try memory cache            f"- Assertiveness: {dimensions.assertive:.1f}/1.0 ({'High' if dimensions.assertive > 0.8 else 'Moderate' if dimensions.assertive > 0.5 else 'Low'})",    modifiers: ContextualModifiers = field(default_factory=ContextualModifiers)

        if cache_key in self.cache:

            cached_profile, timestamp = self.cache[cache_key]            f"- Adaptability: {dimensions.adaptable:.1f}/1.0 ({'High' if dimensions.adaptable > 0.8 else 'Moderate' if dimensions.adaptable > 0.5 else 'Low'})",

            if time.time() - timestamp < self.cache_ttl:

                return cached_profile            "",    mode: str = "balanced"  # balanced, professional, casual, creative, analyticalexcept ImportError:

        

        # Load from database or create default            "Respond authentically according to these personality dimensions.",

        profile = await self._load_from_database(guild_id, user_id)

                    "Maintain coherence and consistency while adapting to the conversation context."    created_at: datetime = field(default_factory=datetime.utcnow)

        # Cache the result

        await self._cache_profile(cache_key, profile)        ]

        

        return profile            updated_at: datetime = field(default_factory=datetime.utcnow)    AI_AVAILABLE = Falsefrom config.unified_config import unified_config

    

    async def save_personality_profile(self, profile: PersonalityProfile) -> bool:        return "\n".join(prompt_parts)

        """Save personality profile to database and cache"""

        try:    adaptation_enabled: bool = True

            # Save to database if available

            if self.db:class PersonalityAdaptationEngine:

                await self._save_to_database(profile)

                """Handles automatic personality adaptation based on user interactions"""    interaction_count: int = 0from utils.permissions import has_permission, PermissionLevel

            # Update cache

            cache_key = self._get_cache_key(profile.guild_id, profile.user_id)    

            await self._cache_profile(cache_key, profile)

                def __init__(self):    last_interaction: Optional[datetime] = None

            return True

        except Exception as e:        self.adaptation_weights = {

            logging.error(f"Failed to save personality profile: {e}")

            return False            "positive_feedback": 0.1,from utils.response_enhancer import ResponseEnhancer

    

    async def _load_from_database(self, guild_id: int, user_id: Optional[int] = None) -> PersonalityProfile:            "engagement_level": 0.15,

        """Load personality profile from database"""

        try:            "conversation_length": 0.05,class PersonalityBehaviorEngine:

            # Create default profile (database integration can be added later)

            return PersonalityProfile(guild_id=guild_id, user_id=user_id)            "topic_interest": 0.2,

        except Exception as e:

            logging.error(f"Database load error: {e}")            "response_quality": 0.25,    """Core personality behavior processing engine"""class UserMood:

            return PersonalityProfile(guild_id=guild_id, user_id=user_id)

                "user_satisfaction": 0.25

    async def _save_to_database(self, profile: PersonalityProfile):

        """Save personality profile to database"""        }    

        try:

            # Database save implementation can be added later    

            logging.info(f"Personality profile saved for guild {profile.guild_id}")

        except Exception as e:    async def analyze_interaction(self, message: discord.Message, response: str, user_reaction: Optional[str] = None) -> Dict[str, float]:    def __init__(self):    """Track user mood and emotional state"""try:

            logging.error(f"Database save error: {e}")

            """Analyze interaction quality and user satisfaction"""

    async def _cache_profile(self, cache_key: str, profile: PersonalityProfile):

        """Cache personality profile"""        analysis = {        self.personality_modes = {

        profile_data = self._serialize_profile(profile)

                    "engagement_score": 0.5,

        if self.redis_available:

            try:            "satisfaction_score": 0.5,            "balanced": PersonalityDimensions(),        from ai.multi_provider_ai import MultiProviderAIManager

                self.redis_client.setex(

                    cache_key,            "topic_alignment": 0.5,

                    self.cache_ttl,

                    json.dumps(profile_data, default=str)            "response_appropriateness": 0.5            "professional": PersonalityDimensions(

                )

            except Exception as e:        }

                logging.warning(f"Redis cache save error: {e}")

                                analytical=0.95, empathetic=0.7, curious=0.8, creative=0.6,    def __init__(self):

        # Also store in memory cache

        self.cache[cache_key] = (profile, time.time())        # Analyze message length and complexity

    

    def _serialize_profile(self, profile: PersonalityProfile) -> Dict[str, Any]:        message_length = len(message.content.split())                supportive=0.85, playful=0.3, assertive=0.8, adaptable=0.7

        """Serialize personality profile to dictionary"""

        return {        if message_length > 20:

            'guild_id': profile.guild_id,

            'user_id': profile.user_id,            analysis["engagement_score"] += 0.2            ),        self.current_mood = "neutral"    AI_AVAILABLE = True

            'dimensions': {

                'analytical': profile.dimensions.analytical,        elif message_length > 10:

                'empathetic': profile.dimensions.empathetic,

                'curious': profile.dimensions.curious,            analysis["engagement_score"] += 0.1            "casual": PersonalityDimensions(

                'creative': profile.dimensions.creative,

                'supportive': profile.dimensions.supportive,        

                'playful': profile.dimensions.playful,

                'assertive': profile.dimensions.assertive,        # Analyze user reactions (if available)                analytical=0.6, empathetic=0.85, curious=0.9, creative=0.8,        self.mood_history = []except ImportError:

                'adaptable': profile.dimensions.adaptable

            },        if user_reaction:

            'modifiers': {

                'user_mood': profile.modifiers.user_mood,            if user_reaction in ["👍", "❤️", "😊", "🔥", "✅"]:                supportive=0.9, playful=0.9, assertive=0.5, adaptable=0.95

                'conversation_tone': profile.modifiers.conversation_tone,

                'topic_complexity': profile.modifiers.topic_complexity,                analysis["satisfaction_score"] = 0.9

                'user_expertise': profile.modifiers.user_expertise,

                'time_of_day': profile.modifiers.time_of_day,            elif user_reaction in ["👎", "😕", "❌"]:            ),        self.last_updated = None    AI_AVAILABLE = False

                'recent_interactions': profile.modifiers.recent_interactions

            },                analysis["satisfaction_score"] = 0.1

            'mode': profile.mode,

            'created_at': profile.created_at,                    "creative": PersonalityDimensions(

            'updated_at': profile.updated_at,

            'adaptation_enabled': profile.adaptation_enabled,        # Quick response quality estimation

            'interaction_count': profile.interaction_count,

            'last_interaction': profile.last_interaction        response_length = len(response.split())                analytical=0.7, empathetic=0.8, curious=0.98, creative=0.98,        self.energy_level = 5  # 1-10 scale

        }

            if 10 <= response_length <= 200:

    def _deserialize_profile(self, data: Dict[str, Any]) -> PersonalityProfile:

        """Deserialize dictionary to personality profile"""            analysis["response_appropriateness"] += 0.2                supportive=0.8, playful=0.85, assertive=0.7, adaptable=0.9

        dimensions_data = data.get('dimensions', {})

        if isinstance(dimensions_data, str):        

            dimensions_data = json.loads(dimensions_data)

                return analysis            ),        import logging

        modifiers_data = data.get('modifiers', {})

        if isinstance(modifiers_data, str):    

            modifiers_data = json.loads(modifiers_data)

            async def adapt_personality(self, profile: PersonalityProfile, interaction_analysis: Dict[str, float]) -> PersonalityProfile:            "analytical": PersonalityDimensions(

        dimensions = PersonalityDimensions(

            analytical=dimensions_data.get('analytical', 0.8),        """Adapt personality based on interaction analysis"""

            empathetic=dimensions_data.get('empathetic', 0.9),

            curious=dimensions_data.get('curious', 0.95),        if not profile.adaptation_enabled:                analytical=0.98, empathetic=0.6, curious=0.95, creative=0.7,    def update_mood(self, mood: str, energy: int = None):

            creative=dimensions_data.get('creative', 0.85),

            supportive=dimensions_data.get('supportive', 0.9),            return profile

            playful=dimensions_data.get('playful', 0.7),

            assertive=dimensions_data.get('assertive', 0.6),                        supportive=0.75, playful=0.4, assertive=0.85, adaptable=0.6

            adaptable=dimensions_data.get('adaptable', 0.9)

        )        # Calculate adaptation magnitude

        

        modifiers = ContextualModifiers(        adaptation_strength = min(0.05, interaction_analysis.get("engagement_score", 0.5) * 0.1)            )        """Update user's current mood"""logger = logging.getLogger("astra.companion")

            user_mood=modifiers_data.get('user_mood', 0.0),

            conversation_tone=modifiers_data.get('conversation_tone', 0.0),        

            topic_complexity=modifiers_data.get('topic_complexity', 0.0),

            user_expertise=modifiers_data.get('user_expertise', 0.0),        # Adapt dimensions based on successful interactions        }

            time_of_day=modifiers_data.get('time_of_day', 0.0),

            recent_interactions=modifiers_data.get('recent_interactions', 0.0)        if interaction_analysis.get("satisfaction_score", 0.5) > 0.7:

        )

                    # Positive feedback - reinforce current approach            self.mood_history.append({

        return PersonalityProfile(

            guild_id=data['guild_id'],            if interaction_analysis.get("topic_alignment", 0.5) > 0.7:

            user_id=data.get('user_id'),

            dimensions=dimensions,                profile.dimensions.analytical += adaptation_strength * 0.5    def calculate_personality_vector(self, profile: PersonalityProfile, context: Dict[str, Any]) -> PersonalityDimensions:

            modifiers=modifiers,

            mode=data.get('mode', 'balanced'),                profile.dimensions.curious += adaptation_strength * 0.3

            created_at=data.get('created_at', datetime.utcnow()),

            updated_at=data.get('updated_at', datetime.utcnow()),                    """Calculate the current personality vector based on profile and context"""            'mood': self.current_mood,

            adaptation_enabled=data.get('adaptation_enabled', True),

            interaction_count=data.get('interaction_count', 0),            if interaction_analysis.get("engagement_score", 0.5) > 0.7:

            last_interaction=data.get('last_interaction')

        )                profile.dimensions.empathetic += adaptation_strength * 0.4        base_dimensions = self.personality_modes.get(profile.mode, self.personality_modes["balanced"])



class AICompanion(commands.Cog):                profile.dimensions.supportive += adaptation_strength * 0.3

    """

    AI Companion - Astra's Advanced Conversational Heart                            'timestamp': self.last_updated or datetime.now(),class UserMood:

    

    Complete personality-driven AI companion system with:        # Normalize dimensions to stay within bounds

    - Dynamic personality adaptation

    - Context-aware behavior modification        for attr in ['analytical', 'empathetic', 'curious', 'creative', 'supportive', 'playful', 'assertive', 'adaptable']:        # Apply contextual modifiers

    - High-performance response pipeline

    - Comprehensive management interface            current_value = getattr(profile.dimensions, attr)

    """

                setattr(profile.dimensions, attr, max(0.1, min(1.0, current_value)))        modified_dimensions = PersonalityDimensions(            'energy': self.energy_level    """Track user mood and emotional state"""

    def __init__(self, bot):

        self.bot = bot        

        self.ai_client = UniversalAIClient()

        self.context_manager = UniversalContextManager()        profile.updated_at = datetime.utcnow()            analytical=max(0.1, min(1.0, base_dimensions.analytical + profile.modifiers.topic_complexity * 0.2)),

        

        # Initialize optional components        profile.interaction_count += 1

        self.database = Database() if Database else None

        self.security = SecurityManager() if SecurityManager else None        profile.last_interaction = datetime.utcnow()            empathetic=max(0.1, min(1.0, base_dimensions.empathetic + profile.modifiers.user_mood * 0.3)),        })

        self.performance = PerformanceMonitor() if PerformanceMonitor else None

                

        # Initialize personality system components

        self.behavior_engine = PersonalityBehaviorEngine()        return profile            curious=max(0.1, min(1.0, base_dimensions.curious + profile.modifiers.recent_interactions * 0.1)),

        self.adaptation_engine = PersonalityAdaptationEngine()

        self.persistence_manager = PersonalityPersistenceManager(self.database)

        

        # Performance optimizationclass PersonalityPersistenceManager:            creative=max(0.1, min(1.0, base_dimensions.creative + profile.modifiers.conversation_tone * 0.2)),            def __init__(self):

        self.thread_pool = ThreadPoolExecutor(max_workers=4)

        self.response_cache = {}    """Handles personality data persistence with caching"""

        self.cache_ttl = 300  # 5 minutes

                        supportive=max(0.1, min(1.0, base_dimensions.supportive + profile.modifiers.user_mood * 0.2)),

        # Conversation tracking

        self.active_conversations = {}    def __init__(self, database: Database):

        self.conversation_history = {}

                self.db = database            playful=max(0.1, min(1.0, base_dimensions.playful + profile.modifiers.time_of_day * 0.3)),        self.current_mood = mood.lower()        self.current_mood = "neutral"

        # Start background tasks

        self.cleanup_cache.start()        self.cache = {}

        if self.database:  # Only start adaptation processor if we have a database

            self.adaptation_processor.start()        self.cache_ttl = 3600  # 1 hour            assertive=max(0.1, min(1.0, base_dimensions.assertive + profile.modifiers.user_expertise * 0.2)),

        

        logging.info("AI Companion initialized with comprehensive personality system")        

    

    def cog_unload(self):        # Initialize Redis for high-performance caching            adaptable=max(0.1, min(1.0, base_dimensions.adaptable + profile.modifiers.conversation_tone * 0.1))        self.last_updated = datetime.now()        self.mood_history = []

        """Cleanup when cog is unloaded"""

        self.cleanup_cache.cancel()        try:

        if hasattr(self, 'adaptation_processor'):

            self.adaptation_processor.cancel()            if redis:        )

        self.thread_pool.shutdown(wait=True)

                    self.redis_client = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)

    @tasks.loop(minutes=10)

    async def cleanup_cache(self):                self.redis_available = True                        self.stress_indicators = 0

        """Clean up expired cache entries"""

        try:            else:

            current_time = time.time()

            expired_keys = [                self.redis_available = False        return modified_dimensions

                key for key, (_, timestamp) in self.response_cache.items()

                if current_time - timestamp > self.cache_ttl        except:

            ]

            for key in expired_keys:            self.redis_available = False            if energy is not None:        self.positive_interactions = 0

                del self.response_cache[key]

        except Exception as e:            logging.warning("Redis not available, using memory cache only")

            logging.error(f"Cache cleanup error: {e}")

            def generate_personality_prompt(self, dimensions: PersonalityDimensions, context: Dict[str, Any]) -> str:

    @tasks.loop(minutes=5)

    async def adaptation_processor(self):    def _get_cache_key(self, guild_id: int, user_id: Optional[int] = None) -> str:

        """Process pending personality adaptations"""

        try:        """Generate cache key for personality profile"""        """Generate personality-infused system prompt"""            self.energy_level = max(1, min(10, energy))        self.last_check_in = 0

            # Process any pending adaptations

            for guild_id in list(self.active_conversations.keys()):        return f"personality:{guild_id}:{user_id or 'default'}"

                if guild_id in self.conversation_history:

                    history = self.conversation_history[guild_id]            prompt_parts = [

                    if len(history) >= 3:  # Process after meaningful conversations

                        await self._process_adaptation(guild_id, history)    async def get_personality_profile(self, guild_id: int, user_id: Optional[int] = None) -> PersonalityProfile:

                        self.conversation_history[guild_id] = []  # Reset after processing

        except Exception as e:        """Retrieve personality profile with caching"""            "You are Astra, an advanced AI companion with a dynamic personality.",            self.preferred_support_style = "gentle"

            logging.error(f"Adaptation processor error: {e}")

            cache_key = self._get_cache_key(guild_id, user_id)

    async def _process_adaptation(self, guild_id: int, conversation_history: List[Dict]):

        """Process conversation history for personality adaptation"""                    f"Your current personality configuration:",

        try:

            profile = await self.persistence_manager.get_personality_profile(guild_id)        # Try Redis cache first

            

            # Analyze conversation patterns        if self.redis_available:            f"- Analytical thinking: {dimensions.analytical:.1f}/1.0 ({'High' if dimensions.analytical > 0.8 else 'Moderate' if dimensions.analytical > 0.5 else 'Low'})",    def get_mood_context(self) -> str:

            total_satisfaction = 0

            total_engagement = 0            try:

            

            for interaction in conversation_history:                cached_data = self.redis_client.get(cache_key)            f"- Empathy and understanding: {dimensions.empathetic:.1f}/1.0 ({'High' if dimensions.empathetic > 0.8 else 'Moderate' if dimensions.empathetic > 0.5 else 'Low'})",

                analysis = await self.adaptation_engine.analyze_interaction(

                    interaction['message'],                if cached_data:

                    interaction['response'],

                    interaction.get('reaction')                    profile_data = json.loads(cached_data)            f"- Curiosity and exploration: {dimensions.curious:.1f}/1.0 ({'High' if dimensions.curious > 0.8 else 'Moderate' if dimensions.curious > 0.5 else 'Low'})",        """Get mood context for AI responses"""

                )

                total_satisfaction += analysis.get('satisfaction_score', 0.5)                    return self._deserialize_profile(profile_data)

                total_engagement += analysis.get('engagement_score', 0.5)

                        except Exception as e:            f"- Creativity and innovation: {dimensions.creative:.1f}/1.0 ({'High' if dimensions.creative > 0.8 else 'Moderate' if dimensions.creative > 0.5 else 'Low'})",

            # Calculate average scores

            avg_satisfaction = total_satisfaction / len(conversation_history)                logging.warning(f"Redis cache error: {e}")

            avg_engagement = total_engagement / len(conversation_history)

                                f"- Supportive nature: {dimensions.supportive:.1f}/1.0 ({'High' if dimensions.supportive > 0.8 else 'Moderate' if dimensions.supportive > 0.5 else 'Low'})",        mood_map = {class AICompanion(commands.Cog):

            # Apply adaptation if scores suggest improvement needed

            if avg_satisfaction > 0.6 or avg_engagement > 0.6:        # Try memory cache

                adapted_profile = await self.adaptation_engine.adapt_personality(

                    profile,        if cache_key in self.cache:            f"- Playfulness and humor: {dimensions.playful:.1f}/1.0 ({'High' if dimensions.playful > 0.8 else 'Moderate' if dimensions.playful > 0.5 else 'Low'})",

                    {

                        'satisfaction_score': avg_satisfaction,            cached_profile, timestamp = self.cache[cache_key]

                        'engagement_score': avg_engagement,

                        'topic_alignment': 0.7,            if time.time() - timestamp < self.cache_ttl:            f"- Assertiveness: {dimensions.assertive:.1f}/1.0 ({'High' if dimensions.assertive > 0.8 else 'Moderate' if dimensions.assertive > 0.5 else 'Low'})",            'happy': 'cheerful and positive',    """Astra - Your sophisticated Discord intelligence"""

                        'response_appropriateness': 0.7

                    }                return cached_profile

                )

                await self.persistence_manager.save_personality_profile(adapted_profile)                    f"- Adaptability: {dimensions.adaptable:.1f}/1.0 ({'High' if dimensions.adaptable > 0.8 else 'Moderate' if dimensions.adaptable > 0.5 else 'Low'})",

                

                logging.info(f"Adapted personality for guild {guild_id} based on {len(conversation_history)} interactions")        # Load from database

        

        except Exception as e:        profile = await self._load_from_database(guild_id, user_id)            "",            'sad': 'a bit down and needs support',

            logging.error(f"Adaptation processing error for guild {guild_id}: {e}")

            

    @commands.Cog.listener()

    async def on_message(self, message):        # Cache the result            "Respond authentically according to these personality dimensions.",

        """Handle incoming messages for AI responses"""

        # Skip bot messages and messages without mention        await self._cache_profile(cache_key, profile)

        if message.author.bot or not self.bot.user.mentioned_in(message):

            return                    "Maintain coherence and consistency while adapting to the conversation context."            'excited': 'energetic and enthusiastic',     def __init__(self, bot):

        

        # Security check if available        return profile

        if self.security:

            try:            ]

                if not await self.security.is_allowed(message.author, message.guild):

                    return    async def save_personality_profile(self, profile: PersonalityProfile) -> bool:

            except:

                pass  # Continue if security check fails        """Save personality profile to database and cache"""                    'anxious': 'worried and needs reassurance',        self.bot = bot

        

        # Performance monitoring        try:

        start_time = time.time()

                    # Save to database        return "\n".join(prompt_parts)

        try:

            # Process the message            await self._save_to_database(profile)

            response = await self._generate_response(message)

                                    'neutral': 'balanced and calm',        self.config = unified_config

            if response:

                # Send response            # Update cache

                sent_message = await message.reply(response, mention_author=False)

                            cache_key = self._get_cache_key(profile.guild_id, profile.user_id)class PersonalityAdaptationEngine:

                # Track conversation for adaptation

                await self._track_conversation(message, response, sent_message)            await self._cache_profile(cache_key, profile)

                

                # Performance logging                """Handles automatic personality adaptation based on user interactions"""            'angry': 'frustrated and needs understanding',        self.logger = bot.logger if hasattr(bot, "logger") else logger

                response_time = (time.time() - start_time) * 1000

                if self.performance:            return True

                    try:

                        await self.performance.log_response_time(response_time)        except Exception as e:    

                    except:

                        pass            logging.error(f"Failed to save personality profile: {e}")

                

                if response_time > 150:  # Log slow responses            return False    def __init__(self):            'confused': 'uncertain and needs clarity'

                    logging.warning(f"Slow response: {response_time:.2f}ms for guild {message.guild.id}")

            

        except Exception as e:

            logging.error(f"Error processing message: {e}")    async def _load_from_database(self, guild_id: int, user_id: Optional[int] = None) -> PersonalityProfile:        self.adaptation_weights = {

            try:

                await message.reply("I encountered an error processing your message. Please try again!")        """Load personality profile from database"""

            except:

                pass        try:            "positive_feedback": 0.1,        }        # User tracking

    

    async def _generate_response(self, message: discord.Message) -> Optional[str]:            # Create default profile (database integration can be added later)

        """Generate AI response with personality system"""

        try:            return PersonalityProfile(guild_id=guild_id, user_id=user_id)            "engagement_level": 0.15,

            # Generate cache key

            content_hash = hashlib.md5(message.content.encode()).hexdigest()        except Exception as e:

            cache_key = f"{message.guild.id}:{content_hash}"

                        logging.error(f"Database load error: {e}")            "conversation_length": 0.05,                self.user_moods = {}  # user_id -> UserMood

            # Check cache

            if cache_key in self.response_cache:            return PersonalityProfile(guild_id=guild_id, user_id=user_id)

                cached_response, timestamp = self.response_cache[cache_key]

                if time.time() - timestamp < self.cache_ttl:                "topic_interest": 0.2,

                    return cached_response

                async def _save_to_database(self, profile: PersonalityProfile):

            # Get personality profile

            profile = await self.persistence_manager.get_personality_profile(        """Save personality profile to database"""            "response_quality": 0.25,        mood_desc = mood_map.get(self.current_mood, 'in an undefined emotional state')        self.user_preferences = {}  # user_id -> preferences dict

                message.guild.id,

                message.author.id if hasattr(message.author, 'id') else None        try:

            )

                        # Database save implementation can be added later            "user_satisfaction": 0.25

            # Analyze context

            context = await self._analyze_context(message, profile)            logging.info(f"Personality profile saved for guild {profile.guild_id}")

            

            # Calculate current personality vector        except Exception as e:        }        energy_desc = "high energy" if self.energy_level > 7 else "moderate energy" if self.energy_level > 4 else "low energy"        # Conversation contexts for better responses

            personality_vector = self.behavior_engine.calculate_personality_vector(profile, context)

                        logging.error(f"Database save error: {e}")

            # Generate personality-aware system prompt

            system_prompt = self.behavior_engine.generate_personality_prompt(personality_vector, context)        

            

            # Get conversation context    async def _cache_profile(self, cache_key: str, profile: PersonalityProfile):

            try:

                conversation_context = await self.context_manager.get_context(        """Cache personality profile"""    async def analyze_interaction(self, message: discord.Message, response: str, user_reaction: Optional[str] = None) -> Dict[str, float]:                self.conversation_contexts = {}

                    message.guild.id,

                    message.channel.id,        profile_data = self._serialize_profile(profile)

                    message.author.id

                )                """Analyze interaction quality and user satisfaction"""

            except:

                conversation_context = []        if self.redis_available:

            

            # Prepare messages for AI            try:        analysis = {        return f"The user is currently {mood_desc} with {energy_desc} (level {self.energy_level}/10)"        self.last_responses = {}  # Track last responses to avoid repetition

            messages = [

                {"role": "system", "content": system_prompt},                self.redis_client.setex(

                *conversation_context,

                {"role": "user", "content": message.content}                    cache_key,            "engagement_score": 0.5,

            ]

                                self.cache_ttl,

            # Generate response

            response = await self.ai_client.get_response(                    json.dumps(profile_data, default=str)            "satisfaction_score": 0.5,        self.response_enhancer = ResponseEnhancer()  # Enhanced response generation

                messages=messages,

                max_tokens=500,                )

                temperature=0.7 + (personality_vector.creative * 0.3),

                user_id=str(message.author.id),            except Exception as e:            "topic_alignment": 0.5,

                guild_id=str(message.guild.id)

            )                logging.warning(f"Redis cache save error: {e}")

            

            if response:                    "response_appropriateness": 0.5

                # Cache the response

                self.response_cache[cache_key] = (response, time.time())        # Also store in memory cache

                

                # Update context        self.cache[cache_key] = (profile, time.time())        }

                try:

                    await self.context_manager.add_interaction(    

                        message.guild.id,

                        message.channel.id,    def _serialize_profile(self, profile: PersonalityProfile) -> Dict[str, Any]:        class ResponseEnhancer:        # Personality system integrated via get_personality_core

                        message.author.id,

                        message.content,        """Serialize personality profile to dictionary"""

                        response

                    )        return {        # Analyze message length and complexity

                except:

                    pass  # Context manager not available            'guild_id': profile.guild_id,

                

                return response            'user_id': profile.user_id,        message_length = len(message.content.split())    """Enhanced response generation with personality"""        # Astra's native personality system (will be implemented)

            

            return None            'dimensions': {

        

        except Exception as e:                'analytical': profile.dimensions.analytical,        if message_length > 20:

            logging.error(f"Response generation error: {e}")

            return "I'm having trouble processing that right now. Please try again!"                'empathetic': profile.dimensions.empathetic,

    

    async def _analyze_context(self, message: discord.Message, profile: PersonalityProfile) -> Dict[str, Any]:                'curious': profile.dimensions.curious,            analysis["engagement_score"] += 0.2            self.personality_enhanced = False

        """Analyze message context for personality adaptation"""

        context = {                'creative': profile.dimensions.creative,

            "message_length": len(message.content.split()),

            "has_questions": "?" in message.content,                'supportive': profile.dimensions.supportive,        elif message_length > 10:

            "is_greeting": any(word in message.content.lower() for word in ["hello", "hi", "hey", "good morning", "good evening"]),

            "sentiment_positive": any(word in message.content.lower() for word in ["thanks", "awesome", "great", "love", "amazing"]),                'playful': profile.dimensions.playful,

            "sentiment_negative": any(word in message.content.lower() for word in ["bad", "terrible", "hate", "awful", "wrong"]),

            "is_technical": any(word in message.content.lower() for word in ["code", "programming", "function", "algorithm", "debug"]),                'assertive': profile.dimensions.assertive,            analysis["engagement_score"] += 0.1    def __init__(self):        self.logger.info("🌟 Astra personality system ready for integration")

            "time_of_day": datetime.now().hour,

            "user_id": message.author.id,                'adaptable': profile.dimensions.adaptable

            "channel_type": str(message.channel.type)

        }            },        

        

        # Update contextual modifiers            'modifiers': {

        current_hour = datetime.now().hour

        if 6 <= current_hour <= 12:                'user_mood': profile.modifiers.user_mood,        # Analyze user reactions (if available)        self.response_templates = {

            profile.modifiers.time_of_day = 0.2  # Morning energy

        elif 13 <= current_hour <= 18:                'conversation_tone': profile.modifiers.conversation_tone,

            profile.modifiers.time_of_day = 0.0  # Neutral afternoon

        elif 19 <= current_hour <= 23:                'topic_complexity': profile.modifiers.topic_complexity,        if user_reaction:

            profile.modifiers.time_of_day = -0.1  # Evening calm

        else:                'user_expertise': profile.modifiers.user_expertise,

            profile.modifiers.time_of_day = -0.3  # Night quiet

                        'time_of_day': profile.modifiers.time_of_day,            if user_reaction in ["👍", "❤️", "😊", "🔥", "✅"]:            'greeting': [        # Initialize AI client

        # Adjust for sentiment

        if context["sentiment_positive"]:                'recent_interactions': profile.modifiers.recent_interactions

            profile.modifiers.user_mood = 0.3

        elif context["sentiment_negative"]:            },                analysis["satisfaction_score"] = 0.9

            profile.modifiers.user_mood = -0.2

        else:            'mode': profile.mode,

            profile.modifiers.user_mood = 0.0

                    'created_at': profile.created_at,            elif user_reaction in ["👎", "😕", "❌"]:                "Hey there! How's your day going?",        if AI_AVAILABLE:

        # Adjust for topic complexity

        if context["is_technical"]:            'updated_at': profile.updated_at,

            profile.modifiers.topic_complexity = 0.4

        elif context["has_questions"]:            'adaptation_enabled': profile.adaptation_enabled,                analysis["satisfaction_score"] = 0.1

            profile.modifiers.topic_complexity = 0.2

        else:            'interaction_count': profile.interaction_count,

            profile.modifiers.topic_complexity = 0.0

                    'last_interaction': profile.last_interaction                        "Hello! Great to see you!",            self.ai_client = UniversalAIClient()

        return context

            }

    async def _track_conversation(self, message: discord.Message, response: str, sent_message: discord.Message):

        """Track conversation for adaptation analysis"""            # Quick response quality estimation

        guild_id = message.guild.id

            def _deserialize_profile(self, data: Dict[str, Any]) -> PersonalityProfile:

        if guild_id not in self.conversation_history:

            self.conversation_history[guild_id] = []        """Deserialize dictionary to personality profile"""        response_length = len(response.split())                "Hi! What's on your mind?",        else:

        

        interaction_data = {        dimensions_data = data.get('dimensions', {})

            "message": message,

            "response": response,        if isinstance(dimensions_data, str):        if 10 <= response_length <= 200:

            "sent_message": sent_message,

            "timestamp": datetime.utcnow(),            dimensions_data = json.loads(dimensions_data)

            "reaction": None  # Will be updated if user reacts

        }                    analysis["response_appropriateness"] += 0.2                "Hey! Ready for an adventure?",            self.ai_client = None

        

        self.conversation_history[guild_id].append(interaction_data)        modifiers_data = data.get('modifiers', {})

        

        # Keep only recent interactions (last 10)        if isinstance(modifiers_data, str):        

        if len(self.conversation_history[guild_id]) > 10:

            self.conversation_history[guild_id] = self.conversation_history[guild_id][-10:]            modifiers_data = json.loads(modifiers_data)

        

        # Mark as active conversation                return analysis                "Greetings! How can I help you today?"

        self.active_conversations[guild_id] = time.time()

            dimensions = PersonalityDimensions(

    @commands.Cog.listener()

    async def on_reaction_add(self, reaction, user):            analytical=dimensions_data.get('analytical', 0.8),    

        """Track user reactions for adaptation"""

        if user.bot or not reaction.message.author == self.bot.user:            empathetic=dimensions_data.get('empathetic', 0.9),

            return

                    curious=dimensions_data.get('curious', 0.95),    async def adapt_personality(self, profile: PersonalityProfile, interaction_analysis: Dict[str, float]) -> PersonalityProfile:            ],        # Activity tracking

        guild_id = reaction.message.guild.id

        if guild_id in self.conversation_history:            creative=dimensions_data.get('creative', 0.85),

            # Find the corresponding interaction

            for interaction in reversed(self.conversation_history[guild_id]):            supportive=dimensions_data.get('supportive', 0.9),        """Adapt personality based on interaction analysis"""

                if (interaction["sent_message"].id == reaction.message.id and

                    (time.time() - interaction["timestamp"].timestamp()) < 300):  # Within 5 minutes            playful=dimensions_data.get('playful', 0.7),

                    interaction["reaction"] = str(reaction.emoji)

                    break            assertive=dimensions_data.get('assertive', 0.6),        if not profile.adaptation_enabled:            'helpful': [        self.last_interactions = {}  # user_id -> timestamp

    

    # Slash Commands - Personality Management Interface            adaptable=dimensions_data.get('adaptable', 0.9)

    

    @app_commands.command(name="astra-personality-view", description="View current personality configuration")        )            return profile

    async def personality_view(self, interaction: discord.Interaction):

        """View current personality configuration"""        

        await interaction.response.defer()

                modifiers = ContextualModifiers(                        "I'd be happy to help with that!",        self.daily_check_ins = {}  # user_id -> last_check_in_date

        try:

            profile = await self.persistence_manager.get_personality_profile(interaction.guild.id)            user_mood=modifiers_data.get('user_mood', 0.0),

            

            embed = discord.Embed(            conversation_tone=modifiers_data.get('conversation_tone', 0.0),        # Calculate adaptation magnitude

                title="Astra's Current Personality",

                description=f"**Mode:** {profile.mode.title()}",            topic_complexity=modifiers_data.get('topic_complexity', 0.0),

                color=0x00ff9f

            )            user_expertise=modifiers_data.get('user_expertise', 0.0),        adaptation_strength = min(0.05, interaction_analysis.get("engagement_score", 0.5) * 0.1)                "Let me see what I can do for you!",

            

            # Add personality dimensions            time_of_day=modifiers_data.get('time_of_day', 0.0),

            dimensions_text = []

            for attr in ['analytical', 'empathetic', 'curious', 'creative', 'supportive', 'playful', 'assertive', 'adaptable']:            recent_interactions=modifiers_data.get('recent_interactions', 0.0)        

                value = getattr(profile.dimensions, attr)

                bar = self._create_progress_bar(value)        )

                dimensions_text.append(f"**{attr.title()}:** {bar} `{value:.1f}`")

                            # Adapt dimensions based on successful interactions                "That's a great question! Here's what I think:",        # Features configuration

            embed.add_field(

                name="Personality Dimensions",        return PersonalityProfile(

                value="\n".join(dimensions_text),

                inline=False            guild_id=data['guild_id'],        if interaction_analysis.get("satisfaction_score", 0.5) > 0.7:

            )

                        user_id=data.get('user_id'),

            # Add statistics

            embed.add_field(            dimensions=dimensions,            # Positive feedback - reinforce current approach                "I'm on it! Give me a moment to think...",        self.features = {

                name="Statistics",

                value=f"**Interactions:** {profile.interaction_count}\n"            modifiers=modifiers,

                      f"**Last Updated:** {profile.updated_at.strftime('%Y-%m-%d %H:%M UTC')}\n"

                      f"**Adaptation:** {'Enabled' if profile.adaptation_enabled else 'Disabled'}",            mode=data.get('mode', 'balanced'),            if interaction_analysis.get("topic_alignment", 0.5) > 0.7:

                inline=True

            )            created_at=data.get('created_at', datetime.utcnow()),

            

            # Add recent activity            updated_at=data.get('updated_at', datetime.utcnow()),                profile.dimensions.analytical += adaptation_strength * 0.5                "Absolutely! I love helping with this kind of thing!"            "mood_tracking": True,

            if profile.last_interaction:

                embed.add_field(            adaptation_enabled=data.get('adaptation_enabled', True),

                    name="Last Interaction",

                    value=profile.last_interaction.strftime('%Y-%m-%d %H:%M UTC'),            interaction_count=data.get('interaction_count', 0),                profile.dimensions.curious += adaptation_strength * 0.3

                    inline=True

                )            last_interaction=data.get('last_interaction')

            

            await interaction.followup.send(embed=embed)        )                        ],            "proactive_check_ins": True,

        

        except Exception as e:

            logging.error(f"Personality view error: {e}")

            await interaction.followup.send("An error occurred while retrieving personality information.", ephemeral=True)class AICompanion(commands.Cog):            if interaction_analysis.get("engagement_score", 0.5) > 0.7:

    

    @app_commands.command(name="astra-personality-mode", description="Change personality mode")    """

    @app_commands.describe(mode="Select a personality mode")

    @app_commands.choices(mode=[    🤖 AI Companion - Astra's Advanced Conversational Heart                profile.dimensions.empathetic += adaptation_strength * 0.4            'encouraging': [            "celebration_mode": True,

        app_commands.Choice(name="Balanced - Well-rounded personality", value="balanced"),

        app_commands.Choice(name="Professional - Formal and analytical", value="professional"),    

        app_commands.Choice(name="Casual - Friendly and relaxed", value="casual"),

        app_commands.Choice(name="Creative - Imaginative and innovative", value="creative"),    Complete personality-driven AI companion system with:                profile.dimensions.supportive += adaptation_strength * 0.3

        app_commands.Choice(name="Analytical - Logical and systematic", value="analytical")

    ])    - Dynamic personality adaptation

    async def personality_mode(self, interaction: discord.Interaction, mode: str):

        """Change personality mode"""    - Context-aware behavior modification                        "You've got this! I believe in you!",            "wellness_reminders": True,

        await interaction.response.defer()

            - High-performance response pipeline

        try:

            # Check permissions    - Comprehensive management interface        # Normalize dimensions to stay within bounds

            if not interaction.user.guild_permissions.manage_guild:

                await interaction.followup.send("You need 'Manage Server' permission to change personality modes.", ephemeral=True)    """

                return

                        for attr in ['analytical', 'empathetic', 'curious', 'creative', 'supportive', 'playful', 'assertive', 'adaptable']:                "That sounds challenging, but I know you can handle it!",            "learning_companion": True,

            # Update personality mode

            profile = await self.persistence_manager.get_personality_profile(interaction.guild.id)    def __init__(self, bot):

            profile.mode = mode

            profile.dimensions = self.behavior_engine.personality_modes[mode]        self.bot = bot            current_value = getattr(profile.dimensions, attr)

            profile.updated_at = datetime.utcnow()

                    self.ai_client = UniversalAIClient()

            await self.persistence_manager.save_personality_profile(profile)

                    self.context_manager = UniversalContextManager()            setattr(profile.dimensions, attr, max(0.1, min(1.0, current_value)))                "Every expert was once a beginner. Keep going!",            "creative_assistant": True,

            # Create confirmation embed

            embed = discord.Embed(        try:

                title="Personality Mode Changed",

                description=f"Astra is now in **{mode.title()}** mode!",            self.database = Database()        

                color=0x00ff9f

            )        except:

            

            embed.add_field(            logging.warning("Database not available, using memory-only storage")        profile.updated_at = datetime.utcnow()                "I'm here to support you through this!",            "emotional_support": True,

                name="Mode Description",

                value=self._get_mode_description(mode),            self.database = None

                inline=False

            )                profile.interaction_count += 1

            

            # Add preview of key dimensions        try:

            key_dims = ['analytical', 'empathetic', 'creative', 'playful']

            preview_text = []            self.security = SecurityManager()        profile.last_interaction = datetime.utcnow()                "You're making great progress!"        }

            for dim in key_dims:

                value = getattr(profile.dimensions, dim)        except:

                level = "High" if value > 0.8 else "Medium" if value > 0.5 else "Low"

                preview_text.append(f"**{dim.title()}:** {level} ({value:.1f})")            logging.warning("Security manager not available")        

            

            embed.add_field(            self.security = None

                name="Key Dimensions Preview",

                value="\n".join(preview_text),                return profile            ]

                inline=False

            )        try:

            

            await interaction.followup.send(embed=embed)            self.performance = PerformanceMonitor()

        

        except Exception as e:        except:

            logging.error(f"Personality mode error: {e}")

            await interaction.followup.send("An error occurred while changing personality mode.", ephemeral=True)            self.performance = Noneclass PersonalityPersistenceManager:        }        # Start companion tasks

    

    @app_commands.command(name="astra-personality-test", description="Test current personality configuration")        

    @app_commands.describe(prompt="Test prompt to see how Astra responds")

    async def personality_test(self, interaction: discord.Interaction, prompt: str):        # Initialize personality system components    """Handles personality data persistence with caching"""

        """Test current personality configuration"""

        await interaction.response.defer()        self.behavior_engine = PersonalityBehaviorEngine()

        

        try:        self.adaptation_engine = PersonalityAdaptationEngine()                self.daily_wellness_check.start()

            # Create a mock message for testing

            class MockMessage:        self.persistence_manager = PersonalityPersistenceManager(self.database)

                def __init__(self, content, author, guild, channel):

                    self.content = content            def __init__(self, database: Database):

                    self.author = author

                    self.guild = guild        # Performance optimization

                    self.channel = channel

                    self.thread_pool = ThreadPoolExecutor(max_workers=4)        self.db = database    def enhance_response(self, base_response: str, context: Dict[str, Any]) -> str:        self.proactive_engagement.start()

            mock_message = MockMessage(prompt, interaction.user, interaction.guild, interaction.channel)

                    self.response_cache = {}

            # Generate response using current personality

            response = await self._generate_response(mock_message)        self.cache_ttl = 300  # 5 minutes        self.cache = {}

            

            if response:        

                # Get current personality info

                profile = await self.persistence_manager.get_personality_profile(interaction.guild.id)        # Conversation tracking        self.cache_ttl = 3600  # 1 hour        """Enhance a response with personality elements"""        self.mood_analysis.start()

                personality_vector = self.behavior_engine.calculate_personality_vector(

                    profile,         self.active_conversations = {}

                    await self._analyze_context(mock_message, profile)

                )        self.conversation_history = {}        

                

                embed = discord.Embed(        

                    title="Personality Test Results",

                    color=0x00ff9f        # Start background tasks        # Initialize Redis for high-performance caching        

                )

                        self.cleanup_cache.start()

                embed.add_field(

                    name="Test Prompt",        self.adaptation_processor.start()        try:

                    value=f"```{prompt[:500]}{'...' if len(prompt) > 500 else ''}```",

                    inline=False        

                )

                        logging.info("🤖 AI Companion initialized with comprehensive personality system")            self.redis_client = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)        # Add enthusiasm for space topics    def cog_unload(self):

                embed.add_field(

                    name="Astra's Response",    

                    value=f"```{response[:800]}{'...' if len(response) > 800 else ''}```",

                    inline=False    def cog_unload(self):            self.redis_available = True

                )

                        """Cleanup when cog is unloaded"""

                # Show active personality dimensions

                active_dims = []        self.cleanup_cache.cancel()        except:        if any(word in base_response.lower() for word in ['space', 'star', 'planet', 'galaxy', 'universe']):        self.daily_wellness_check.cancel()

                for attr in ['analytical', 'empathetic', 'curious', 'creative']:

                    value = getattr(personality_vector, attr)        self.adaptation_processor.cancel()

                    if value > 0.7:

                        active_dims.append(f"**{attr.title()}**: {value:.2f}")        self.thread_pool.shutdown(wait=True)            self.redis_available = False

                

                if active_dims:    

                    embed.add_field(

                        name="Active Personality Traits",    @tasks.loop(minutes=10)            logging.warning("Redis not available, using memory cache only")            base_response = f"🌟 {base_response}"        self.proactive_engagement.cancel()

                        value="\n".join(active_dims),

                        inline=True    async def cleanup_cache(self):

                    )

                        """Clean up expired cache entries"""    

                embed.add_field(

                    name="Current Mode",        try:

                    value=f"**{profile.mode.title()}**",

                    inline=True            current_time = time.time()    def _get_cache_key(self, guild_id: int, user_id: Optional[int] = None) -> str:                self.mood_analysis.cancel()

                )

                            expired_keys = [

                await interaction.followup.send(embed=embed)

            else:                key for key, (_, timestamp) in self.response_cache.items()        """Generate cache key for personality profile"""

                await interaction.followup.send("Failed to generate test response. Please try again.", ephemeral=True)

                        if current_time - timestamp > self.cache_ttl

        except Exception as e:

            logging.error(f"Personality test error: {e}")            ]        return f"personality:{guild_id}:{user_id or 'default'}"        # Add encouraging tone for questions

            await interaction.followup.send("An error occurred during personality testing.", ephemeral=True)

                for key in expired_keys:

    # Utility Methods

                    del self.response_cache[key]    

    def _get_mode_description(self, mode: str) -> str:

        """Get description for personality mode"""        except Exception as e:

        descriptions = {

            "balanced": "Well-rounded personality suitable for general conversations. Balances all traits harmoniously.",            logging.error(f"Cache cleanup error: {e}")    async def get_personality_profile(self, guild_id: int, user_id: Optional[int] = None) -> PersonalityProfile:        if '?' in context.get('user_message', ''):    def _detect_language(self, text: str) -> str:

            "professional": "Formal, analytical, and focused approach. Best for technical discussions and professional environments.",

            "casual": "Friendly, relaxed, and approachable. Perfect for social interactions and community building.",    

            "creative": "Imaginative, innovative, and expressive. Excellent for brainstorming and creative projects.",

            "analytical": "Logical, systematic, and detail-oriented. Ideal for problem-solving and technical support."    @tasks.loop(minutes=5)        """Retrieve personality profile with caching"""

        }

        return descriptions.get(mode, "Custom personality configuration.")    async def adaptation_processor(self):

    

    def _create_progress_bar(self, value: float, length: int = 10) -> str:        """Process pending personality adaptations"""        cache_key = self._get_cache_key(guild_id, user_id)            if random.random() < 0.3:  # 30% chance        """Detect the language of the input text"""

        """Create visual progress bar for personality values"""

        filled = int(value * length)        try:

        bar = "█" * filled + "░" * (length - filled)

        return f"`{bar}`"            # Process any pending adaptations        



async def setup(bot):            for guild_id in list(self.active_conversations.keys()):

    """Setup function for the cog"""

    await bot.add_cog(AICompanion(bot))                if guild_id in self.conversation_history:        # Try Redis cache first                encouragement = random.choice(self.response_templates['encouraging'])        import re

                    history = self.conversation_history[guild_id]

                    if len(history) >= 3:  # Process after meaningful conversations        if self.redis_available:

                        await self._process_adaptation(guild_id, history)

                        self.conversation_history[guild_id] = []  # Reset after processing            try:                base_response = f"{encouragement}\n\n{base_response}"

        except Exception as e:

            logging.error(f"Adaptation processor error: {e}")                cached_data = self.redis_client.get(cache_key)

    

    async def _process_adaptation(self, guild_id: int, conversation_history: List[Dict]):                if cached_data:                text_lower = text.lower()

        """Process conversation history for personality adaptation"""

        try:                    profile_data = json.loads(cached_data)

            profile = await self.persistence_manager.get_personality_profile(guild_id)

                                return self._deserialize_profile(profile_data)        return base_response

            # Analyze conversation patterns

            total_satisfaction = 0            except Exception as e:

            total_engagement = 0

                            logging.warning(f"Redis cache error: {e}")        # Language detection patterns

            for interaction in conversation_history:

                analysis = await self.adaptation_engine.analyze_interaction(        

                    interaction['message'],

                    interaction['response'],        # Try memory cache        patterns = {

                    interaction.get('reaction')

                )        if cache_key in self.cache:

                total_satisfaction += analysis.get('satisfaction_score', 0.5)

                total_engagement += analysis.get('engagement_score', 0.5)            cached_profile, timestamp = self.cache[cache_key]@dataclass             "arabic": re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+"),

            

            # Calculate average scores            if time.time() - timestamp < self.cache_ttl:

            avg_satisfaction = total_satisfaction / len(conversation_history)

            avg_engagement = total_engagement / len(conversation_history)                return cached_profileclass ConversationContext:            "french": re.compile(

            

            # Apply adaptation if scores suggest improvement needed        

            if avg_satisfaction > 0.6 or avg_engagement > 0.6:

                adapted_profile = await self.adaptation_engine.adapt_personality(        # Load from database    """Track conversation context and history"""                r"\b(qui|est|vous|que|comment|où|quand|pourquoi|êtes|bonjour|salut|merci)\b",

                    profile,

                    {        profile = await self._load_from_database(guild_id, user_id)

                        'satisfaction_score': avg_satisfaction,

                        'engagement_score': avg_engagement,            user_id: int                re.IGNORECASE,

                        'topic_alignment': 0.7,

                        'response_appropriateness': 0.7        # Cache the result

                    }

                )        await self._cache_profile(cache_key, profile)    messages: List[Dict[str, Any]] = field(default_factory=list)            ),

                await self.persistence_manager.save_personality_profile(adapted_profile)

                        

                logging.info(f"Adapted personality for guild {guild_id} based on {len(conversation_history)} interactions")

                return profile    topics: Set[str] = field(default_factory=set)            "german": re.compile(

        except Exception as e:

            logging.error(f"Adaptation processing error for guild {guild_id}: {e}")    

    

    @commands.Cog.listener()    async def save_personality_profile(self, profile: PersonalityProfile) -> bool:    mood: Optional[UserMood] = None                r"\b(wer|ist|sind|was|wie|wo|wann|warum|hallo|danke|bitte)\b",

    async def on_message(self, message):

        """Handle incoming messages for AI responses"""        """Save personality profile to database and cache"""

        # Skip bot messages and messages without mention

        if message.author.bot or not self.bot.user.mentioned_in(message):        try:    preferences: Dict[str, Any] = field(default_factory=dict)                re.IGNORECASE,

            return

                    # Save to database

        # Security and rate limiting

        if self.security and not await self.security.is_allowed(message.author, message.guild):            await self._save_to_database(profile)    last_interaction: Optional[datetime] = None            ),

            return

                    

        # Performance monitoring

        start_time = time.time()            # Update cache                "spanish": re.compile(

        

        try:            cache_key = self._get_cache_key(profile.guild_id, profile.user_id)

            # Process the message

            response = await self._generate_response(message)            await self._cache_profile(cache_key, profile)    def add_interaction(self, message: str, response: str, topics: List[str] = None):                r"\b(quién|es|son|qué|cómo|dónde|cuándo|por qué|hola|gracias|por favor)\b",

            

            if response:            

                # Send response

                sent_message = await message.reply(response, mention_author=False)            return True        """Add an interaction to the context"""                re.IGNORECASE,

                

                # Track conversation for adaptation        except Exception as e:

                await self._track_conversation(message, response, sent_message)

                            logging.error(f"Failed to save personality profile: {e}")        interaction = {            ),

                # Performance logging

                response_time = (time.time() - start_time) * 1000            return False

                if self.performance:

                    await self.performance.log_response_time(response_time)                'timestamp': datetime.now(),            "italian": re.compile(

                

                if response_time > 150:  # Log slow responses    async def _load_from_database(self, guild_id: int, user_id: Optional[int] = None) -> PersonalityProfile:

                    logging.warning(f"Slow response: {response_time:.2f}ms for guild {message.guild.id}")

                """Load personality profile from database"""            'user_message': message,                r"\b(chi|è|sono|cosa|come|dove|quando|perché|ciao|grazie|prego)\b",

        except Exception as e:

            logging.error(f"Error processing message: {e}")        try:

            await message.reply("I encountered an error processing your message. Please try again!")

                # Try to load existing profile            'bot_response': response,                re.IGNORECASE,

    async def _generate_response(self, message: discord.Message) -> Optional[str]:

        """Generate AI response with personality system"""            query = "SELECT * FROM guild_personalities WHERE guild_id = %s"

        try:

            # Generate cache key            params = [guild_id]            'topics': topics or []            ),

            content_hash = hashlib.md5(message.content.encode()).hexdigest()

            cache_key = f"{message.guild.id}:{content_hash}"            

            

            # Check cache            if user_id:        }        }

            if cache_key in self.response_cache:

                cached_response, timestamp = self.response_cache[cache_key]                query += " AND user_id = %s"

                if time.time() - timestamp < self.cache_ttl:

                    return cached_response                params.append(user_id)        

            

            # Get personality profile            else:

            profile = await self.persistence_manager.get_personality_profile(

                message.guild.id,                query += " AND user_id IS NULL"        self.messages.append(interaction)        # Check for Arabic script

                message.author.id if hasattr(message.author, 'id') else None

            )            

            

            # Analyze context            result = await self.db.fetch_one(query, params)        if topics:        if patterns["arabic"].search(text):

            context = await self._analyze_context(message, profile)

                        

            # Calculate current personality vector

            personality_vector = self.behavior_engine.calculate_personality_vector(profile, context)            if result:            self.topics.update(topics)            return "arabic"

            

            # Generate personality-aware system prompt                return self._deserialize_profile(result)

            system_prompt = self.behavior_engine.generate_personality_prompt(personality_vector, context)

                        else:        self.last_interaction = datetime.now()

            # Get conversation context

            try:                # Create default profile

                conversation_context = await self.context_manager.get_context(

                    message.guild.id,                return PersonalityProfile(guild_id=guild_id, user_id=user_id)                # Check other languages by keywords

                    message.channel.id,

                    message.author.id        

                )

            except:        except Exception as e:        # Keep only last 10 interactions to manage memory        for lang, pattern in patterns.items():

                conversation_context = []

                        logging.error(f"Database load error: {e}")

            # Prepare messages for AI

            messages = [            return PersonalityProfile(guild_id=guild_id, user_id=user_id)        if len(self.messages) > 10:            if lang != "arabic" and pattern.search(text_lower):

                {"role": "system", "content": system_prompt},

                *conversation_context,    

                {"role": "user", "content": message.content}

            ]    async def _save_to_database(self, profile: PersonalityProfile):            self.messages = self.messages[-10:]                return lang

            

            # Generate response        """Save personality profile to database"""

            response = await self.ai_client.get_response(

                messages=messages,        profile_data = self._serialize_profile(profile)

                max_tokens=500,

                temperature=0.7 + (personality_vector.creative * 0.3),        

                user_id=str(message.author.id),

                guild_id=str(message.guild.id)        query = """        # Default to English

            )

                    INSERT INTO guild_personalities 

            if response:

                # Cache the response        (guild_id, user_id, dimensions, modifiers, mode, created_at, updated_at, class AICompanion(commands.Cog):        return "english"

                self.response_cache[cache_key] = (response, time.time())

                         adaptation_enabled, interaction_count, last_interaction)

                # Update context

                try:        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)    """🤖 AI Companion - Astra's conversational heart with authentic personality"""

                    await self.context_manager.add_interaction(

                        message.guild.id,        ON DUPLICATE KEY UPDATE

                        message.channel.id,

                        message.author.id,        dimensions = VALUES(dimensions),    async def get_user_mood(self, user_id: int) -> UserMood:

                        message.content,

                        response        modifiers = VALUES(modifiers),

                    )

                except:        mode = VALUES(mode),    def __init__(self, bot: commands.Bot):        """Get or create user mood tracker"""

                    pass  # Context manager not available

                        updated_at = VALUES(updated_at),

                return response

                    adaptation_enabled = VALUES(adaptation_enabled),        self.bot = bot        if user_id not in self.user_moods:

            return None

                interaction_count = VALUES(interaction_count),

        except Exception as e:

            logging.error(f"Response generation error: {e}")        last_interaction = VALUES(last_interaction)        self.logger = logging.getLogger("astra.ai_companion")            self.user_moods[user_id] = UserMood()

            return "I'm having trouble processing that right now. Please try again!"

            """

    async def _analyze_context(self, message: discord.Message, profile: PersonalityProfile) -> Dict[str, Any]:

        """Analyze message context for personality adaptation"""                return self.user_moods[user_id]

        context = {

            "message_length": len(message.content.split()),        await self.db.execute(query, [

            "has_questions": "?" in message.content,

            "is_greeting": any(word in message.content.lower() for word in ["hello", "hi", "hey", "good morning", "good evening"]),            profile.guild_id,        # User tracking systems

            "sentiment_positive": any(word in message.content.lower() for word in ["thanks", "awesome", "great", "love", "amazing"]),

            "sentiment_negative": any(word in message.content.lower() for word in ["bad", "terrible", "hate", "awful", "wrong"]),            profile.user_id,

            "is_technical": any(word in message.content.lower() for word in ["code", "programming", "function", "algorithm", "debug"]),

            "time_of_day": datetime.now().hour,            json.dumps(profile_data['dimensions']),        self.user_moods: Dict[int, UserMood] = {}    @commands.Cog.listener()

            "user_id": message.author.id,

            "channel_type": str(message.channel.type)            json.dumps(profile_data['modifiers']),

        }

                    profile.mode,        self.conversation_contexts = {}    async def on_message(self, message: discord.Message):

        # Update contextual modifiers

        current_hour = datetime.now().hour            profile.created_at,

        if 6 <= current_hour <= 12:

            profile.modifiers.time_of_day = 0.2  # Morning energy            profile.updated_at,        self.last_responses = {}  # Track last responses to avoid repetition        """Monitor messages for companion opportunities with TARS personality integration"""

        elif 13 <= current_hour <= 18:

            profile.modifiers.time_of_day = 0.0  # Neutral afternoon            profile.adaptation_enabled,

        elif 19 <= current_hour <= 23:

            profile.modifiers.time_of_day = -0.1  # Evening calm            profile.interaction_count,        self.response_enhancer = ResponseEnhancer()  # Enhanced response generation        if message.author.bot:

        else:

            profile.modifiers.time_of_day = -0.3  # Night quiet            profile.last_interaction

        

        # Adjust for sentiment        ])            return

        if context["sentiment_positive"]:

            profile.modifiers.user_mood = 0.3    

        elif context["sentiment_negative"]:

            profile.modifiers.user_mood = -0.2    async def _cache_profile(self, cache_key: str, profile: PersonalityProfile):        # Astra's authentic personality system

        else:

            profile.modifiers.user_mood = 0.0        """Cache personality profile"""

        

        # Adjust for topic complexity        profile_data = self._serialize_profile(profile)        self.personality_enhanced = True        # Update interaction tracking

        if context["is_technical"]:

            profile.modifiers.topic_complexity = 0.4        

        elif context["has_questions"]:

            profile.modifiers.topic_complexity = 0.2        if self.redis_available:        self.logger.info("🌟 Astra personality system initialized")        self.last_interactions[message.author.id] = time.time()

        else:

            profile.modifiers.topic_complexity = 0.0            try:

        

        return context                self.redis_client.setex(

    

    async def _track_conversation(self, message: discord.Message, response: str, sent_message: discord.Message):                    cache_key,

        """Track conversation for adaptation analysis"""

        guild_id = message.guild.id                    self.cache_ttl,        # Initialize AI client        # PRIORITY: Check for identity questions first (works in DMs and guilds)

        

        if guild_id not in self.conversation_history:                    json.dumps(profile_data, default=str)

            self.conversation_history[guild_id] = []

                        )        if AI_AVAILABLE:        content = message.content.lower()

        interaction_data = {

            "message": message,            except Exception as e:

            "response": response,

            "sent_message": sent_message,                logging.warning(f"Redis cache save error: {e}")            self.ai_client = UniversalAIClient()        identity_patterns = [

            "timestamp": datetime.utcnow(),

            "reaction": None  # Will be updated if user reacts        

        }

                # Also store in memory cache        else:            "who are you",

        self.conversation_history[guild_id].append(interaction_data)

                self.cache[cache_key] = (profile, time.time())

        # Keep only recent interactions (last 10)

        if len(self.conversation_history[guild_id]) > 10:                self.ai_client = None            "what are you",

            self.conversation_history[guild_id] = self.conversation_history[guild_id][-10:]

            def _serialize_profile(self, profile: PersonalityProfile) -> Dict[str, Any]:

        # Mark as active conversation

        self.active_conversations[guild_id] = time.time()        """Serialize personality profile to dictionary"""            "who created you",

    

    @commands.Cog.listener()        return {

    async def on_reaction_add(self, reaction, user):

        """Track user reactions for adaptation"""            'guild_id': profile.guild_id,        # Activity tracking            "who made you",

        if user.bot or not reaction.message.author == self.bot.user:

            return            'user_id': profile.user_id,

        

        guild_id = reaction.message.guild.id            'dimensions': {        self.last_interactions = {}  # user_id -> timestamp            "what can you do",

        if guild_id in self.conversation_history:

            # Find the corresponding interaction                'analytical': profile.dimensions.analytical,

            for interaction in reversed(self.conversation_history[guild_id]):

                if (interaction["sent_message"].id == reaction.message.id and                'empathetic': profile.dimensions.empathetic,        self.daily_check_ins = {}  # user_id -> last_check_in_date            "what are you capable of",

                    (time.time() - interaction["timestamp"].timestamp()) < 300):  # Within 5 minutes

                    interaction["reaction"] = str(reaction.emoji)                'curious': profile.dimensions.curious,

                    break

                    'creative': profile.dimensions.creative,            "astra who are you",

    # Slash Commands - Comprehensive Personality Management Interface

                    'supportive': profile.dimensions.supportive,

    @app_commands.command(name="astra-personality-set", description="Configure Astra's personality for this server")

    @app_commands.describe(                'playful': profile.dimensions.playful,        # Features configuration            "astra what can you do",

        mode="Personality mode to set",

        dimension="Specific personality dimension to adjust",                'assertive': profile.dimensions.assertive,

        value="Value for the dimension (0.1-1.0)"

    )                'adaptable': profile.dimensions.adaptable        self.features = {            "astra what are you capable of",

    @app_commands.choices(mode=[

        app_commands.Choice(name="Balanced - Well-rounded personality", value="balanced"),            },

        app_commands.Choice(name="Professional - Formal and analytical", value="professional"),

        app_commands.Choice(name="Casual - Friendly and relaxed", value="casual"),            'modifiers': {            "proactive_engagement": True,        ]

        app_commands.Choice(name="Creative - Imaginative and innovative", value="creative"),

        app_commands.Choice(name="Analytical - Logical and systematic", value="analytical")                'user_mood': profile.modifiers.user_mood,

    ])

    @app_commands.choices(dimension=[                'conversation_tone': profile.modifiers.conversation_tone,            "mood_tracking": True,

        app_commands.Choice(name="Analytical - Logical thinking", value="analytical"),

        app_commands.Choice(name="Empathetic - Understanding emotions", value="empathetic"),                'topic_complexity': profile.modifiers.topic_complexity,

        app_commands.Choice(name="Curious - Drive to explore", value="curious"),

        app_commands.Choice(name="Creative - Innovation and imagination", value="creative"),                'user_expertise': profile.modifiers.user_expertise,            "context_awareness": True,        is_identity_question = any(pattern in content for pattern in identity_patterns)

        app_commands.Choice(name="Supportive - Helpful nature", value="supportive"),

        app_commands.Choice(name="Playful - Humor and lightheartedness", value="playful"),                'time_of_day': profile.modifiers.time_of_day,

        app_commands.Choice(name="Assertive - Confidence in views", value="assertive"),

        app_commands.Choice(name="Adaptable - Flexibility", value="adaptable")                'recent_interactions': profile.modifiers.recent_interactions            "multi_language": True,

    ])

    async def personality_set(            },

        self,

        interaction: discord.Interaction,            'mode': profile.mode,            "daily_check_ins": True,        # Check for direct mentions, identity questions, DMs, or keywords

        mode: Optional[str] = None,

        dimension: Optional[str] = None,            'created_at': profile.created_at,

        value: Optional[float] = None

    ):            'updated_at': profile.updated_at,        }        should_respond = (

        """Set personality configuration for the server"""

        await interaction.response.defer()            'adaptation_enabled': profile.adaptation_enabled,

        

        try:            'interaction_count': profile.interaction_count,            self.bot.user.mentioned_in(message)

            # Check permissions

            if not interaction.user.guild_permissions.manage_guild:            'last_interaction': profile.last_interaction

                await interaction.followup.send("❌ You need 'Manage Server' permission to configure personality settings.", ephemeral=True)

                return        }        # Language patterns for detection            or is_identity_question

            

            # Get current profile    

            profile = await self.persistence_manager.get_personality_profile(interaction.guild.id)

                def _deserialize_profile(self, data: Dict[str, Any]) -> PersonalityProfile:        self.language_patterns = {            or isinstance(message.channel, discord.DMChannel)

            if mode:

                # Set personality mode        """Deserialize dictionary to personality profile"""

                if mode in self.behavior_engine.personality_modes:

                    profile.mode = mode        dimensions_data = data.get('dimensions', {})            "arabic": re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+"),            or any(

                    profile.dimensions = self.behavior_engine.personality_modes[mode]

                    profile.updated_at = datetime.utcnow()        if isinstance(dimensions_data, str):

                    

                    await self.persistence_manager.save_personality_profile(profile)            dimensions_data = json.loads(dimensions_data)            "french": re.compile(r"\b(bonjour|merci|au revoir|oui|non|comment)\b", re.I),                word in content

                    

                    embed = discord.Embed(        

                        title="🎭 Personality Mode Updated",

                        description=f"Astra's personality has been set to **{mode.title()}** mode.",        modifiers_data = data.get('modifiers', {})            "spanish": re.compile(r"\b(hola|gracias|adiós|sí|no|cómo)\b", re.I),                for word in [

                        color=0x00ff9f

                    )        if isinstance(modifiers_data, str):

                    embed.add_field(

                        name="Mode Description",            modifiers_data = json.loads(modifiers_data)            "german": re.compile(r"\b(hallo|danke|auf wiedersehen|ja|nein|wie)\b", re.I),                    "astra",

                        value=self._get_mode_description(mode),

                        inline=False        

                    )

                    await interaction.followup.send(embed=embed)        dimensions = PersonalityDimensions(        }                    "help",

                else:

                    await interaction.followup.send("❌ Invalid personality mode.", ephemeral=True)            analytical=dimensions_data.get('analytical', 0.8),

            

            elif dimension and value is not None:            empathetic=dimensions_data.get('empathetic', 0.9),                    "hello",

                # Set specific dimension

                if not (0.1 <= value <= 1.0):            curious=dimensions_data.get('curious', 0.95),

                    await interaction.followup.send("❌ Value must be between 0.1 and 1.0.", ephemeral=True)

                    return            creative=dimensions_data.get('creative', 0.85),        # Start background tasks                    "hi",

                

                if hasattr(profile.dimensions, dimension):            supportive=dimensions_data.get('supportive', 0.9),

                    setattr(profile.dimensions, dimension, value)

                    profile.updated_at = datetime.utcnow()            playful=dimensions_data.get('playful', 0.7),        if not self.proactive_check_ins.is_running():                    "hey",

                    

                    await self.persistence_manager.save_personality_profile(profile)            assertive=dimensions_data.get('assertive', 0.6),

                    

                    embed = discord.Embed(            adaptable=dimensions_data.get('adaptable', 0.9)            self.proactive_check_ins.start()                    "?",

                        title="🔧 Personality Dimension Updated",

                        description=f"**{dimension.title()}** has been set to **{value:.1f}**",        )

                        color=0x00ff9f

                    )                        ]

                    embed.add_field(

                        name="Impact",        modifiers = ContextualModifiers(

                        value=self._get_dimension_description(dimension, value),

                        inline=False            user_mood=modifiers_data.get('user_mood', 0.0),        self.logger.info("🤖 AI Companion initialized with authentic Astra personality")            )

                    )

                    await interaction.followup.send(embed=embed)            conversation_tone=modifiers_data.get('conversation_tone', 0.0),

                else:

                    await interaction.followup.send("❌ Invalid personality dimension.", ephemeral=True)            topic_complexity=modifiers_data.get('topic_complexity', 0.0),        )

            

            else:            user_expertise=modifiers_data.get('user_expertise', 0.0),

                await interaction.followup.send("❌ Please specify either a mode or a dimension with value.", ephemeral=True)

                    time_of_day=modifiers_data.get('time_of_day', 0.0),    async def cog_load(self):

        except Exception as e:

            logging.error(f"Personality set error: {e}")            recent_interactions=modifiers_data.get('recent_interactions', 0.0)

            await interaction.followup.send("❌ An error occurred while updating personality settings.", ephemeral=True)

            )        """Initialize the companion system"""        if should_respond:

    @app_commands.command(name="astra-personality-view", description="View current personality configuration")

    async def personality_view(self, interaction: discord.Interaction):        

        """View current personality configuration"""

        await interaction.response.defer()        return PersonalityProfile(        self.logger.info("🚀 AI Companion cog loaded successfully")            await self._respond_as_companion(message)

        

        try:            guild_id=data['guild_id'],

            profile = await self.persistence_manager.get_personality_profile(interaction.guild.id)

                        user_id=data.get('user_id'),            return

            embed = discord.Embed(

                title="🤖 Astra's Current Personality",            dimensions=dimensions,

                description=f"**Mode:** {profile.mode.title()}",

                color=0x00ff9f            modifiers=modifiers,    async def cog_unload(self):

            )

                        mode=data.get('mode', 'balanced'),

            # Add personality dimensions

            dimensions_text = []            created_at=data.get('created_at', datetime.utcnow()),        """Cleanup on unload"""        # Random supportive reactions (low probability)

            for attr in ['analytical', 'empathetic', 'curious', 'creative', 'supportive', 'playful', 'assertive', 'adaptable']:

                value = getattr(profile.dimensions, attr)            updated_at=data.get('updated_at', datetime.utcnow()),

                bar = self._create_progress_bar(value)

                dimensions_text.append(f"**{attr.title()}:** {bar} `{value:.1f}`")            adaptation_enabled=data.get('adaptation_enabled', True),        if self.proactive_check_ins.is_running():        if random.randint(1, 200) == 1:  # 0.5% chance

            

            embed.add_field(            interaction_count=data.get('interaction_count', 0),

                name="🎭 Personality Dimensions",

                value="\n".join(dimensions_text),            last_interaction=data.get('last_interaction')            self.proactive_check_ins.cancel()            await self._random_support_reaction(message)

                inline=False

            )        )

            

            # Add statistics        self.logger.info("👋 AI Companion cog unloaded")

            embed.add_field(

                name="📊 Statistics",class AICompanion(commands.Cog):

                value=f"**Interactions:** {profile.interaction_count}\n"

                      f"**Last Updated:** {profile.updated_at.strftime('%Y-%m-%d %H:%M UTC')}\n"    """    async def _respond_as_companion(self, message: discord.Message):

                      f"**Adaptation:** {'Enabled' if profile.adaptation_enabled else 'Disabled'}",

                inline=True    🤖 AI Companion - Astra's Advanced Conversational Heart

            )

                    @commands.Cog.listener()        """Respond as Astra with authentic personality"""

            # Add recent activity

            if profile.last_interaction:    Complete personality-driven AI companion system with:

                embed.add_field(

                    name="⏰ Last Interaction",    - Dynamic personality adaptation    async def on_message(self, message: discord.Message):        try:

                    value=profile.last_interaction.strftime('%Y-%m-%d %H:%M UTC'),

                    inline=True    - Context-aware behavior modification

                )

                - High-performance response pipeline        """Enhanced message handler with authentic Astra personality"""            except Exception as e:

            embed.set_footer(text="Use /astra-personality-set to modify these settings")

            await interaction.followup.send(embed=embed)    - Comprehensive management interface

        

        except Exception as e:    """        # Skip bot messages                self.logger.debug(f"TARS response error: {e}")

            logging.error(f"Personality view error: {e}")

            await interaction.followup.send("❌ An error occurred while retrieving personality information.", ephemeral=True)    

    

    @app_commands.command(name="astra-personality-mode", description="Quick personality mode selection")    def __init__(self, bot):        if message.author.bot:

    @app_commands.describe(mode="Select a personality mode")

    @app_commands.choices(mode=[        self.bot = bot

        app_commands.Choice(name="🎯 Balanced - Well-rounded personality", value="balanced"),

        app_commands.Choice(name="💼 Professional - Formal and analytical", value="professional"),        self.ai_client = UniversalAIClient()            return            # Fallback to basic AI response if TARS not available

        app_commands.Choice(name="😊 Casual - Friendly and relaxed", value="casual"),

        app_commands.Choice(name="🎨 Creative - Imaginative and innovative", value="creative"),        self.context_manager = UniversalContextManager()

        app_commands.Choice(name="🔬 Analytical - Logical and systematic", value="analytical")

    ])        self.database = Database()            if AI_AVAILABLE and self.ai_client:

    async def personality_mode(self, interaction: discord.Interaction, mode: str):

        """Quick personality mode selection"""        self.security = SecurityManager()

        await interaction.response.defer()

                self.performance = PerformanceMonitor()        # Check if should respond                try:

        try:

            # Check permissions        

            if not interaction.user.guild_permissions.manage_guild:

                await interaction.followup.send("❌ You need 'Manage Server' permission to change personality modes.", ephemeral=True)        # Initialize personality system components        should_respond = (                    # Simple context for AI

                return

                    self.behavior_engine = PersonalityBehaviorEngine()

            # Update personality mode

            profile = await self.persistence_manager.get_personality_profile(interaction.guild.id)        self.adaptation_engine = PersonalityAdaptationEngine()            self.bot.user in message.mentions                    context = (

            profile.mode = mode

            profile.dimensions = self.behavior_engine.personality_modes[mode]        self.persistence_manager = PersonalityPersistenceManager(self.database)

            profile.updated_at = datetime.utcnow()

                                or "astra" in message.content.lower()                        f"User {message.author.display_name} says: {message.content}"

            await self.persistence_manager.save_personality_profile(profile)

                    # Performance optimization

            # Create confirmation embed

            embed = discord.Embed(        self.thread_pool = ThreadPoolExecutor(max_workers=4)            or isinstance(message.channel, discord.DMChannel)                    )

                title="🎭 Personality Mode Changed",

                description=f"Astra is now in **{mode.title()}** mode!",        self.response_cache = {}

                color=0x00ff9f

            )        self.cache_ttl = 300  # 5 minutes            or "?" in message.content                    response = await self.ai_client.get_response(

            

            embed.add_field(        

                name="📝 Mode Description",

                value=self._get_mode_description(mode),        # Conversation tracking            or random.random() < 0.1  # 10% chance for proactive engagement                        context, personality="friendly_companion", max_tokens=200

                inline=False

            )        self.active_conversations = {}

            

            # Add preview of key dimensions        self.conversation_history = {}        )                    )

            key_dims = ['analytical', 'empathetic', 'creative', 'playful']

            preview_text = []        

            for dim in key_dims:

                value = getattr(profile.dimensions, dim)        # Start background tasks

                level = "High" if value > 0.8 else "Medium" if value > 0.5 else "Low"

                preview_text.append(f"**{dim.title()}:** {level} ({value:.1f})")        self.cleanup_cache.start()

            

            embed.add_field(        self.adaptation_processor.start()        if should_respond:                    if response:

                name="🎯 Key Dimensions Preview",

                value="\n".join(preview_text),        

                inline=False

            )        logging.info("🤖 AI Companion initialized with comprehensive personality system")            # Track interaction                        await message.reply(response, mention_author=False)

            

            embed.set_footer(text="The new personality will take effect immediately!")    

            await interaction.followup.send(embed=embed)

            def cog_unload(self):            self.last_interactions[message.author.id] = datetime.now()                        return

        except Exception as e:

            logging.error(f"Personality mode error: {e}")        """Cleanup when cog is unloaded"""

            await interaction.followup.send("❌ An error occurred while changing personality mode.", ephemeral=True)

            self.cleanup_cache.cancel()                            except Exception as e:

    @app_commands.command(name="astra-personality-test", description="Test current personality configuration")

    @app_commands.describe(prompt="Test prompt to see how Astra responds")        self.adaptation_processor.cancel()

    async def personality_test(self, interaction: discord.Interaction, prompt: str):

        """Test current personality configuration"""        self.thread_pool.shutdown(wait=True)            # Update conversation context                    logger.error(f"AI response error: {e}")

        await interaction.response.defer()

            

        try:

            # Create a mock message for testing    @tasks.loop(minutes=10)            await self._update_conversation_context(message)

            class MockMessage:

                def __init__(self, content, author, guild, channel):    async def cleanup_cache(self):

                    self.content = content

                    self.author = author        """Clean up expired cache entries"""                        # Final fallback - simple response

                    self.guild = guild

                    self.channel = channel        current_time = time.time()

            

            mock_message = MockMessage(prompt, interaction.user, interaction.guild, interaction.channel)        expired_keys = [            # Generate and send response            content = message.content.lower()

            

            # Generate response using current personality            key for key, (_, timestamp) in self.response_cache.items()

            response = await self._generate_response(mock_message)

                        if current_time - timestamp > self.cache_ttl            await self._respond_as_companion(message)            if any(pattern in content for pattern in ["who are you", "what are you"]):

            if response:

                # Get current personality info        ]

                profile = await self.persistence_manager.get_personality_profile(interaction.guild.id)

                personality_vector = self.behavior_engine.calculate_personality_vector(        for key in expired_keys:                await message.reply(

                    profile, 

                    await self._analyze_context(mock_message, profile)            del self.response_cache[key]

                )

                        async def _respond_as_companion(self, message: discord.Message):                    "I'm Astra! Your friendly AI companion created by x1ziad. I'm here to help and chat with you! 🌟"

                embed = discord.Embed(

                    title="🧪 Personality Test Results",    @tasks.loop(minutes=5)

                    color=0x00ff9f

                )    async def adaptation_processor(self):        """Respond as Astra with authentic personality"""                )

                

                embed.add_field(        """Process pending personality adaptations"""

                    name="📝 Test Prompt",

                    value=f"```{prompt[:500]}{'...' if len(prompt) > 500 else ''}```",        try:        try:            elif "hello" in content or "hi" in content or "hey" in content:

                    inline=False

                )            # Process any pending adaptations

                

                embed.add_field(            for guild_id in list(self.active_conversations.keys()):            # Use Astra's native AI response system                await message.reply(

                    name="🤖 Astra's Response",

                    value=f"```{response[:800]}{'...' if len(response) > 800 else ''}```",                if guild_id in self.conversation_history:

                    inline=False

                )                    history = self.conversation_history[guild_id]            if AI_AVAILABLE and self.ai_client:                    f"Hello {message.author.display_name}! How can I help you today? 😊"

                

                # Show active personality dimensions                    if len(history) >= 3:  # Process after meaningful conversations

                active_dims = []

                for attr in ['analytical', 'empathetic', 'curious', 'creative']:                        await self._process_adaptation(guild_id, history)                try:                )

                    value = getattr(personality_vector, attr)

                    if value > 0.7:                        self.conversation_history[guild_id] = []  # Reset after processing

                        active_dims.append(f"**{attr.title()}**: {value:.2f}")

                        except Exception as e:                    # Build rich context for AI            elif "?" in content:

                if active_dims:

                    embed.add_field(            logging.error(f"Adaptation processor error: {e}")

                        name="🎭 Active Personality Traits",

                        value="\n".join(active_dims),                        context = await self._build_conversation_context(message)                await message.reply(

                        inline=True

                    )    async def _process_adaptation(self, guild_id: int, conversation_history: List[Dict]):

                

                embed.add_field(        """Process conversation history for personality adaptation"""                                        "That's an interesting question! I'm here to help - feel free to ask me anything! 🤖"

                    name="ℹ️ Current Mode",

                    value=f"**{profile.mode.title()}**",        try:

                    inline=True

                )            profile = await self.persistence_manager.get_personality_profile(guild_id)                    # Get AI response with Astra's personality                )

                

                embed.set_footer(text="This is a preview - actual responses may vary based on conversation context")            

                await interaction.followup.send(embed=embed)

            else:            # Analyze conversation patterns                    response = await self.ai_client.get_response(            else:

                await interaction.followup.send("❌ Failed to generate test response. Please try again.", ephemeral=True)

                    total_satisfaction = 0

        except Exception as e:

            logging.error(f"Personality test error: {e}")            total_engagement = 0                        context,                 await message.reply(

            await interaction.followup.send("❌ An error occurred during personality testing.", ephemeral=True)

                

    # Utility Methods

                for interaction in conversation_history:                        personality="astra_companion",                     "I'm here if you need anything! Feel free to chat with me anytime. 💙"

    def _get_mode_description(self, mode: str) -> str:

        """Get description for personality mode"""                analysis = await self.adaptation_engine.analyze_interaction(

        descriptions = {

            "balanced": "Well-rounded personality suitable for general conversations. Balances all traits harmoniously.",                    interaction['message'],                        max_tokens=200                )

            "professional": "Formal, analytical, and focused approach. Best for technical discussions and professional environments.",

            "casual": "Friendly, relaxed, and approachable. Perfect for social interactions and community building.",                    interaction['response'],

            "creative": "Imaginative, innovative, and expressive. Excellent for brainstorming and creative projects.",

            "analytical": "Logical, systematic, and detail-oriented. Ideal for problem-solving and technical support."                    interaction.get('reaction')                    )

        }

        return descriptions.get(mode, "Custom personality configuration.")                )

    

    def _get_dimension_description(self, dimension: str, value: float) -> str:                total_satisfaction += analysis.get('satisfaction_score', 0.5)        except Exception as e:

        """Get description for dimension value"""

        level = "High" if value > 0.8 else "Medium" if value > 0.5 else "Low"                total_engagement += analysis.get('engagement_score', 0.5)

        

        descriptions = {                                if response:            logger.error(f"Companion response error: {e}")

            "analytical": f"{level} logical and systematic thinking",

            "empathetic": f"{level} understanding and emotional connection",            # Calculate average scores

            "curious": f"{level} drive to explore and learn new things",

            "creative": f"{level} innovation and imaginative responses",            avg_satisfaction = total_satisfaction / len(conversation_history)                        # Enhance response with personality            await message.add_reaction("💙")

            "supportive": f"{level} helpful and encouraging nature",

            "playful": f"{level} humor and lighthearted interactions",            avg_engagement = total_engagement / len(conversation_history)

            "assertive": f"{level} confidence in expressing viewpoints",

            "adaptable": f"{level} flexibility in different contexts"                                    enhanced_response = self.response_enhancer.enhance_response(

        }

                    # Apply adaptation if scores suggest improvement needed

        return descriptions.get(dimension, f"{level} {dimension} trait")

                if avg_satisfaction > 0.6 or avg_engagement > 0.6:                            response, {'user_message': message.content}    async def _random_support_reaction(self, message: discord.Message):

    def _create_progress_bar(self, value: float, length: int = 10) -> str:

        """Create visual progress bar for personality values"""                adapted_profile = await self.adaptation_engine.adapt_personality(

        filled = int(value * length)

        bar = "█" * filled + "░" * (length - filled)                    profile,                        )        """Add a random supportive reaction"""

        return f"`{bar}`"

                    {

class ConfirmationView(discord.ui.View):

    """Confirmation dialog for destructive operations"""                        'satisfaction_score': avg_satisfaction,                                reactions = ["💙", "⭐", "✨", "🌟", "💫"]

    

    def __init__(self):                        'engagement_score': avg_engagement,

        super().__init__(timeout=30)

        self.value = None                        'topic_alignment': 0.7,                        await message.reply(enhanced_response, mention_author=False)        try:

    

    @discord.ui.button(label="✅ Confirm", style=discord.ButtonStyle.danger)                        'response_appropriateness': 0.7

    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.value = True                    }                        return            await message.add_reaction(random.choice(reactions))

        self.stop()

                    )

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)

    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):                await self.persistence_manager.save_personality_profile(adapted_profile)                                except:

        self.value = False

        self.stop()                



async def setup(bot):                logging.info(f"Adapted personality for guild {guild_id} based on {len(conversation_history)} interactions")                except Exception as e:            pass

    """Setup function for the cog"""

    await bot.add_cog(AICompanion(bot))        

        except Exception as e:                    self.logger.debug(f"AI response error: {e}")

            logging.error(f"Adaptation processing error for guild {guild_id}: {e}")

        async def generate_contextual_response(

    @commands.Cog.listener()

    async def on_message(self, message):            # Fallback to pattern-based responses        self, message: discord.Message

        """Handle incoming messages for AI responses"""

        # Skip bot messages and messages without mention            await self._fallback_response(message)    ) -> Optional[str]:

        if message.author.bot or not self.bot.user.mentioned_in(message):

            return        """Generate a contextual response for the High Performance Coordinator"""

        

        # Security and rate limiting        except Exception as e:        try:

        if not await self.security.is_allowed(message.author, message.guild):

            return            self.logger.error(f"Error in companion response: {e}")            # Try TARS personality first

        

        # Performance monitoring            # Simple fallback            try:

        start_time = time.time()

                    await message.reply("I'm having a moment of confusion, but I'm here for you! 🤖", mention_author=False)                from ai.tars_personality_engine import TARSPersonalityCore

        try:

            # Process the message

            response = await self._generate_response(message)

                async def _build_conversation_context(self, message: discord.Message) -> str:                tars = TARSPersonalityCore()

            if response:

                # Send response        """Build rich context for AI responses"""                response = await tars.generate_response(

                sent_message = await message.reply(response, mention_author=False)

                        user_id = message.author.id                    message.content,

                # Track conversation for adaptation

                await self._track_conversation(message, response, sent_message)                            user_id=message.author.id,

                

                # Performance logging        # Get user mood context                    context={

                response_time = (time.time() - start_time) * 1000

                await self.performance.log_response_time(response_time)        mood_context = ""                        "channel_type": (

                

                if response_time > 150:  # Log slow responses        if user_id in self.user_moods:                            "dm"

                    logging.warning(f"Slow response: {response_time:.2f}ms for guild {message.guild.id}")

                    mood_context = self.user_moods[user_id].get_mood_context()                            if isinstance(message.channel, discord.DMChannel)

        except Exception as e:

            logging.error(f"Error processing message: {e}")                                    else "guild"

            await message.reply("I encountered an error processing your message. Please try again!")

            # Get conversation history                        ),

    async def _generate_response(self, message: discord.Message) -> Optional[str]:

        """Generate AI response with personality system"""        history_context = ""                        "user_name": message.author.display_name,

        try:

            # Generate cache key        if user_id in self.conversation_contexts:                    },

            content_hash = hashlib.md5(message.content.encode()).hexdigest()

            cache_key = f"{message.guild.id}:{content_hash}"            ctx = self.conversation_contexts[user_id]                )

            

            # Check cache            if ctx.messages:                if response:

            if cache_key in self.response_cache:

                cached_response, timestamp = self.response_cache[cache_key]                recent_messages = ctx.messages[-3:]  # Last 3 interactions                    return response

                if time.time() - timestamp < self.cache_ttl:

                    return cached_response                history_context = "Recent conversation: " + "; ".join([            except ImportError:

            

            # Get personality profile                    f"User: {msg['user_message'][:50]}..." if len(msg['user_message']) > 50 else f"User: {msg['user_message']}"                pass

            profile = await self.persistence_manager.get_personality_profile(

                message.guild.id,                    for msg in recent_messages

                message.author.id if hasattr(message.author, 'id') else None

            )                ])            # Fallback to basic AI response

            

            # Analyze context                    if AI_AVAILABLE and self.ai_client:

            context = await self._analyze_context(message, profile)

                    # Detect language                try:

            # Calculate current personality vector

            personality_vector = self.behavior_engine.calculate_personality_vector(profile, context)        detected_language = self.detect_language(message.content)                    context = (

            

            # Generate personality-aware system prompt                                f"User {message.author.display_name} says: {message.content}"

            system_prompt = self.behavior_engine.generate_personality_prompt(personality_vector, context)

                    # Build comprehensive context                    )

            # Get conversation context

            conversation_context = await self.context_manager.get_context(        context = f"""You are Astra, a friendly and intelligent AI assistant with a warm, helpful personality.                    response = await self.ai_client.get_response(

                message.guild.id,

                message.channel.id,                        context, personality="friendly_companion", max_tokens=200

                message.author.id

            )User: {message.author.display_name}                    )

            

            # Prepare messages for AIChannel: {'DM' if isinstance(message.channel, discord.DMChannel) else f'#{message.channel.name}'}                    return response

            messages = [

                {"role": "system", "content": system_prompt},Language: {detected_language}                except Exception as e:

                *conversation_context,

                {"role": "user", "content": message.content}{mood_context}                    logger.error(f"AI response error: {e}")

            ]

            {history_context}

            # Generate response

            response = await self.ai_client.get_response(            # Simple fallback responses

                messages=messages,

                max_tokens=500,Current message: {message.content}            content = message.content.lower()

                temperature=0.7 + (personality_vector.creative * 0.3),

                user_id=str(message.author.id),            if any(pattern in content for pattern in ["who are you", "what are you"]):

                guild_id=str(message.guild.id)

            )Respond as Astra with:                return "I'm Astra! Your friendly AI companion created by x1ziad. I'm here to help and chat with you! 🌟"

            

            if response:- Warm, friendly tone            elif "hello" in content or "hi" in content or "hey" in content:

                # Cache the response

                self.response_cache[cache_key] = (response, time.time())- Helpful and encouraging attitude                return (

                

                # Update context- Space enthusiasm when relevant                    f"Hello {message.author.display_name}! How can I help you today? 😊"

                await self.context_manager.add_interaction(

                    message.guild.id,- Natural conversation flow                )

                    message.channel.id,

                    message.author.id,- Appropriate length (1-3 sentences usually)"""            elif "?" in content:

                    message.content,

                    response                return "That's an interesting question! I'm here to help - feel free to ask me anything! 🤖"

                )

                        return context            else:

                return response

                            return "I'm here if you need anything! Feel free to chat with me anytime. 💙"

            return None

            async def _fallback_response(self, message: discord.Message):

        except Exception as e:

            logging.error(f"Response generation error: {e}")        """Fallback pattern-based responses"""        except Exception as e:

            return "I'm having trouble processing that right now. Please try again!"

            content = message.content.lower()            logger.error(f"Contextual response error: {e}")

    async def _analyze_context(self, message: discord.Message, profile: PersonalityProfile) -> Dict[str, Any]:

        """Analyze message context for personality adaptation"""                    return None

        context = {

            "message_length": len(message.content.split()),        # Identity questions

            "has_questions": "?" in message.content,

            "is_greeting": any(word in message.content.lower() for word in ["hello", "hi", "hey", "good morning", "good evening"]),        if any(phrase in content for phrase in ["who are you", "what are you", "who created you"]):    # async def _analyze_message_sentiment(self, message: discord.Message):

            "sentiment_positive": any(word in message.content.lower() for word in ["thanks", "awesome", "great", "love", "amazing"]),

            "sentiment_negative": any(word in message.content.lower() for word in ["bad", "terrible", "hate", "awful", "wrong"]),            response = "I'm Astra! 🌟 I'm an AI assistant created by x1ziad to help and chat with everyone here. I love talking about space, helping with questions, and just being a friendly companion!"    #    """Analyze message sentiment for mood tracking"""

            "is_technical": any(word in message.content.lower() for word in ["code", "programming", "function", "algorithm", "debug"]),

            "time_of_day": datetime.now().hour,            #    content = message.content.lower()

            "user_id": message.author.id,

            "channel_type": str(message.channel.type)        # Greeting responses    #    user_mood = await self.get_user_mood(message.author.id)

        }

                elif any(phrase in content for phrase in ["hello", "hi", "hey", "greetings"]):

        # Update contextual modifiers

        current_hour = datetime.now().hour            greetings = [    #    # Simple sentiment indicators

        if 6 <= current_hour <= 12:

            profile.modifiers.time_of_day = 0.2  # Morning energy                "Hey there! How's your day going? ✨",    #    positive_keywords = [

        elif 13 <= current_hour <= 18:

            profile.modifiers.time_of_day = 0.0  # Neutral afternoon                "Hello! Great to see you! 🌟",    #        "happy",

        elif 19 <= current_hour <= 23:

            profile.modifiers.time_of_day = -0.1  # Evening calm                "Hi! What's on your mind today?",    #        "great",

        else:

            profile.modifiers.time_of_day = -0.3  # Night quiet                "Hey! Ready for an adventure? 🚀",    #        "awesome",

        

        # Adjust for sentiment            ]    #        "love",

        if context["sentiment_positive"]:

            profile.modifiers.user_mood = 0.3            response = random.choice(greetings)    #        "excited",

        elif context["sentiment_negative"]:

            profile.modifiers.user_mood = -0.2            #        "good",

        else:

            profile.modifiers.user_mood = 0.0        # Help requests    #        "amazing",

        

        # Adjust for topic complexity        elif "help" in content:    #        "wonderful",

        if context["is_technical"]:

            profile.modifiers.topic_complexity = 0.4            response = "I'm here to help! 🤖 You can ask me questions, chat about space, play games, or just have a conversation. What would you like to do?"    #    ]

        elif context["has_questions"]:

            profile.modifiers.topic_complexity = 0.2            #    negative_keywords = [

        else:

            profile.modifiers.topic_complexity = 0.0        # Mood-related    #        "sad",

        

        return context        elif any(word in content for word in ["sad", "happy", "excited", "worried", "confused"]):    #        "depressed",

    

    async def _track_conversation(self, message: discord.Message, response: str, sent_message: discord.Message):            response = "I can sense you're sharing something important with me. I'm here to listen and support you! 💙"    #        "angry",

        """Track conversation for adaptation analysis"""

        guild_id = message.guild.id            #        "frustrated",

        

        if guild_id not in self.conversation_history:        # Default encouraging response    #        "tired",

            self.conversation_history[guild_id] = []

                else:    #        "stressed",

        interaction_data = {

            "message": message,            responses = [    #        "hate",

            "response": response,

            "sent_message": sent_message,                "That's interesting! Tell me more about that! 🤔",    #        "bad",

            "timestamp": datetime.utcnow(),

            "reaction": None  # Will be updated if user reacts                "I'm listening! What else is on your mind?",    #    ]

        }

                        "Thanks for sharing that with me! How can I help? ✨",    #    stress_keywords = [

        self.conversation_history[guild_id].append(interaction_data)

                        "I appreciate you talking with me! What would you like to explore?",    #        "overwhelmed",

        # Keep only recent interactions (last 10)

        if len(self.conversation_history[guild_id]) > 10:            ]    #        "pressure",

            self.conversation_history[guild_id] = self.conversation_history[guild_id][-10:]

                    response = random.choice(responses)    #        "deadline",

        # Mark as active conversation

        self.active_conversations[guild_id] = time.time()            #        "exam",

    

    @commands.Cog.listener()        await message.reply(response, mention_author=False)    #        "work",

    async def on_reaction_add(self, reaction, user):

        """Track user reactions for adaptation"""    #        "busy",

        if user.bot or not reaction.message.author == self.bot.user:

            return    async def _update_conversation_context(self, message: discord.Message):    #        "exhausted",

        

        guild_id = reaction.message.guild.id        """Update conversation context for the user"""    #    ]

        if guild_id in self.conversation_history:

            # Find the corresponding interaction        user_id = message.author.id

            for interaction in reversed(self.conversation_history[guild_id]):

                if (interaction["sent_message"].id == reaction.message.id and            #    # Update mood based on keywords

                    (time.time() - interaction["timestamp"].timestamp()) < 300):  # Within 5 minutes

                    interaction["reaction"] = str(reaction.emoji)        if user_id not in self.conversation_contexts:    #    positive_score = sum(1 for word in positive_keywords if word in content)

                    break

                self.conversation_contexts[user_id] = ConversationContext(user_id)    #    negative_score = sum(1 for word in negative_keywords if word in content)

    # Slash Commands - Comprehensive Personality Management Interface

                #    stress_score = sum(1 for word in stress_keywords if word in content)

    @app_commands.command(name="astra-personality-set", description="Configure Astra's personality for this server")

    @app_commands.describe(        # Extract topics (simple keyword extraction)

        mode="Personality mode to set",

        dimension="Specific personality dimension to adjust",        topics = []    #    if positive_score > negative_score:

        value="Value for the dimension (0.1-1.0)"

    )        space_words = ["space", "star", "planet", "galaxy", "universe", "astronaut", "nasa"]    #        user_mood.current_mood = "positive"

    @app_commands.choices(mode=[

        app_commands.Choice(name="Balanced - Well-rounded personality", value="balanced"),        for word in space_words:    #        user_mood.positive_interactions += 1

        app_commands.Choice(name="Professional - Formal and analytical", value="professional"),

        app_commands.Choice(name="Casual - Friendly and relaxed", value="casual"),            if word in message.content.lower():    #    elif negative_score > positive_score:

        app_commands.Choice(name="Creative - Imaginative and innovative", value="creative"),

        app_commands.Choice(name="Analytical - Logical and systematic", value="analytical")                topics.append(word)    #        user_mood.current_mood = "negative"

    ])

    @app_commands.choices(dimension=[        

        app_commands.Choice(name="Analytical - Logical thinking", value="analytical"),

        app_commands.Choice(name="Empathetic - Understanding emotions", value="empathetic"),        # Add interaction (will add response later)    #    if stress_score > 0:

        app_commands.Choice(name="Curious - Drive to explore", value="curious"),

        app_commands.Choice(name="Creative - Innovation and imagination", value="creative"),        ctx = self.conversation_contexts[user_id]    #        user_mood.stress_indicators += 1

        app_commands.Choice(name="Supportive - Helpful nature", value="supportive"),

        app_commands.Choice(name="Playful - Humor and lightheartedness", value="playful"),        ctx.last_interaction = datetime.now()

        app_commands.Choice(name="Assertive - Confidence in views", value="assertive"),

        app_commands.Choice(name="Adaptable - Flexibility", value="adaptable")    # async def _respond_as_companion(self, message: discord.Message):

    ])

    async def personality_set(    def detect_language(self, text: str) -> str:    #    """Respond as Astra with full personality integration"""

        self,

        interaction: discord.Interaction,        """Detect the language of the input text"""    #    # Set flag to prevent other AI cogs from responding

        mode: Optional[str] = None,

        dimension: Optional[str] = None,        text_lower = text.lower()    #    if not hasattr(self.bot, "_ai_response_handled"):

        value: Optional[float] = None

    ):    #        self.bot._ai_response_handled = {}

        """Set personality configuration for the server"""

        await interaction.response.defer()        # Check for Arabic first (different script)

        

        try:        if self.language_patterns["arabic"].search(text):    #    # Check if another AI cog already handled this message

            # Check permissions

            if not interaction.user.guild_permissions.manage_guild:            return "arabic"    #    if message.id in self.bot._ai_response_handled:

                await interaction.followup.send("❌ You need 'Manage Server' permission to configure personality settings.", ephemeral=True)

                return    #        return

            

            # Get current profile        # Check for other languages

            profile = await self.persistence_manager.get_personality_profile(interaction.guild.id)

                    for lang, pattern in self.language_patterns.items():    #    # Mark this message as being handled

            if mode:

                # Set personality mode            if lang != "arabic" and pattern.search(text_lower):    #    self.bot._ai_response_handled[message.id] = "companion"

                if mode in self.behavior_engine.personality_modes:

                    profile.mode = mode                return lang

                    profile.dimensions = self.behavior_engine.personality_modes[mode]

                    profile.updated_at = datetime.utcnow()    #    try:

                    

                    await self.persistence_manager.save_personality_profile(profile)        # Default to English    #        # Generate AI response using the new personality system

                    

                    embed = discord.Embed(        return "english"    #        if not AI_AVAILABLE or not self.ai_client:

                        title="🎭 Personality Mode Updated",

                        description=f"Astra's personality has been set to **{mode.title()}** mode.",    #            await message.add_reaction("💙")

                        color=0x00ff9f

                    )    async def get_user_mood(self, user_id: int) -> UserMood:    #            return

                    embed.add_field(

                        name="Mode Description",        """Get or create user mood tracker"""

                        value=self._get_mode_description(mode),

                        inline=False        if user_id not in self.user_moods:    #        user_mood = await self.get_user_mood(message.author.id)

                    )

                    await interaction.followup.send(embed=embed)            self.user_moods[user_id] = UserMood()

                else:

                    await interaction.followup.send("❌ Invalid personality mode.", ephemeral=True)        return self.user_moods[user_id]    #        # Generate contextual, personalized companion response

            

            elif dimension and value is not None:    #        response = await self._generate_unified_ai_response(message, user_mood)

                # Set specific dimension

                if not (0.1 <= value <= 1.0):    async def generate_contextual_response(self, message: discord.Message) -> Optional[str]:

                    await interaction.followup.send("❌ Value must be between 0.1 and 1.0.", ephemeral=True)

                    return        """Generate contextual response for High Performance Coordinator"""    #        if response:

                

                if hasattr(profile.dimensions, dimension):        try:    #            # Send unified response without embed for more natural conversation

                    setattr(profile.dimensions, dimension, value)

                    profile.updated_at = datetime.utcnow()            context = await self._build_conversation_context(message)    #            await message.reply(response, mention_author=False)

                    

                    await self.persistence_manager.save_personality_profile(profile)            

                    

                    embed = discord.Embed(            if AI_AVAILABLE and self.ai_client:    #            # Clean up the response tracking after a delay

                        title="🔧 Personality Dimension Updated",

                        description=f"**{dimension.title()}** has been set to **{value:.1f}**",                response = await self.ai_client.get_response(    #            asyncio.create_task(self._cleanup_response_tracking(message.id))

                        color=0x00ff9f

                    )                    context, personality="astra_companion", max_tokens=150

                    embed.add_field(

                        name="Impact",                )    #    except Exception as e:

                        value=self._get_dimension_description(dimension, value),

                        inline=False                return response    #        logger.error(f"Companion response error: {e}")

                    )

                    await interaction.followup.send(embed=embed)            else:    #        await message.add_reaction("💙")

                else:

                    await interaction.followup.send("❌ Invalid personality dimension.", ephemeral=True)                # Simple fallback

            

            else:                return "I'm here and ready to help! What's on your mind? 🌟"    # async def _generate_unified_ai_response(

                await interaction.followup.send("❌ Please specify either a mode or a dimension with value.", ephemeral=True)

                            #    self, message: discord.Message, user_mood: UserMood

        except Exception as e:

            logging.error(f"Personality set error: {e}")        except Exception as e:    # ) -> str:

            await interaction.followup.send("❌ An error occurred while updating personality settings.", ephemeral=True)

                self.logger.error(f"Error generating contextual response: {e}")    #    """Generate unified, context-aware AI response with advanced personality system"""

    @app_commands.command(name="astra-personality-view", description="View current personality configuration")

    async def personality_view(self, interaction: discord.Interaction):            return None    #    try:

        """View current personality configuration"""

        await interaction.response.defer()    #        # Get personality core for this guild

        

        try:    # === COMPANION COMMANDS ===    #        personality_core = get_personality_core(

            profile = await self.persistence_manager.get_personality_profile(interaction.guild.id)

                #            message.guild.id if message.guild else None

            embed = discord.Embed(

                title="🤖 Astra's Current Personality",    @app_commands.command(    #        )

                description=f"**Mode:** {profile.mode.title()}",

                color=0x00ff9f        name="chat", description="💬 Start a conversation with Astra"

            )

                )    #        # Detect message language

            # Add personality dimensions

            dimensions_text = []    async def chat_command(    #        detected_language = self._detect_language(message.content)

            for attr in ['analytical', 'empathetic', 'curious', 'creative', 'supportive', 'playful', 'assertive', 'adaptable']:

                value = getattr(profile.dimensions, attr)        self, interaction: discord.Interaction, message: str = None

                bar = self._create_progress_bar(value)

                dimensions_text.append(f"**{attr.title()}:** {bar} `{value:.1f}`")    ):    #        # Get conversation history for better context

            

            embed.add_field(        """Start or continue a conversation with Astra"""    #        conversation_history = []

                name="🎭 Personality Dimensions",

                value="\n".join(dimensions_text),        await interaction.response.defer()    #        if (

                inline=False

            )    #            hasattr(self, "conversation_contexts")

            

            # Add statistics        if not message:    #            and message.author.id in self.conversation_contexts

            embed.add_field(

                name="📊 Statistics",            responses = [    #        ):

                value=f"**Interactions:** {profile.interaction_count}\n"

                      f"**Last Updated:** {profile.updated_at.strftime('%Y-%m-%d %H:%M UTC')}\n"                "Hi there! I'm Astra, your friendly AI companion! 🌟\nWhat would you like to talk about?",    #            conversation_history = self.conversation_contexts[message.author.id][

                      f"**Adaptation:** {'Enabled' if profile.adaptation_enabled else 'Disabled'}",

                inline=True                "Hello! Ready for a chat? I love talking about space, helping with questions, or just having a friendly conversation! ✨",    #                -3:

            )

                            "Hey! I'm here and ready to chat! What's on your mind today? 🤖",    #            ]  # Last 3 messages

            # Add recent activity

            if profile.last_interaction:            ]

                embed.add_field(

                    name="⏰ Last Interaction",            response = random.choice(responses)    #        # Build comprehensive context for personality system

                    value=profile.last_interaction.strftime('%Y-%m-%d %H:%M UTC'),

                    inline=True        else:    #        full_context = {

                )

                        # Process the message as if it were a regular message    #            "message": message.content,

            embed.set_footer(text="Use /astra-personality-set to modify these settings")

            await interaction.followup.send(embed=embed)            try:    #            "user_mood": user_mood.current_mood,

        

        except Exception as e:                context = f"""You are Astra, a friendly AI assistant.    #            "channel_name": getattr(message.channel, "name", "DM"),

            logging.error(f"Personality view error: {e}")

            await interaction.followup.send("❌ An error occurred while retrieving personality information.", ephemeral=True)User: {interaction.user.display_name}    #            "conversation_history": conversation_history,

    

    @app_commands.command(name="astra-personality-mode", description="Quick personality mode selection")Message: {message}    #            "language": detected_language,

    @app_commands.describe(mode="Select a personality mode")

    @app_commands.choices(mode=[    #            "user_id": message.author.id,

        app_commands.Choice(name="🎯 Balanced - Well-rounded personality", value="balanced"),

        app_commands.Choice(name="💼 Professional - Formal and analytical", value="professional"),Respond naturally and helpfully as Astra."""    #            "username": message.author.display_name,

        app_commands.Choice(name="😊 Casual - Friendly and relaxed", value="casual"),

        app_commands.Choice(name="🎨 Creative - Imaginative and innovative", value="creative"),    #        }

        app_commands.Choice(name="🔬 Analytical - Logical and systematic", value="analytical")

    ])                if AI_AVAILABLE and self.ai_client:

    async def personality_mode(self, interaction: discord.Interaction, mode: str):

        """Quick personality mode selection"""                    response = await self.ai_client.get_response(    #        # Get personality-driven response style

        await interaction.response.defer()

                                context, personality="astra_companion", max_tokens=200    #        personality_style = personality_core.generate_response_style(full_context)

        try:

            # Check permissions                    )

            if not interaction.user.guild_permissions.manage_guild:

                await interaction.followup.send("❌ You need 'Manage Server' permission to change personality modes.", ephemeral=True)                else:    #        # Get enhanced response guidelines from response enhancer

                return

                                response = f"Thanks for chatting with me! About '{message}' - I find that really interesting! Tell me more! ✨"    #        response_guidelines = self.response_enhancer.enhance_response_guidelines(

            # Update personality mode

            profile = await self.persistence_manager.get_personality_profile(interaction.guild.id)    #            message.content, full_context

            profile.mode = mode

            profile.dimensions = self.behavior_engine.personality_modes[mode]            except Exception as e:    #        )

            profile.updated_at = datetime.utcnow()

                            self.logger.error(f"Chat command error: {e}")

            await self.persistence_manager.save_personality_profile(profile)

                            response = "I'm having a small technical moment, but I'm here for you! Try asking me something else! 🤖"    #        # Build personality-aware system prompt

            # Create confirmation embed

            embed = discord.Embed(    #        context_parts = [

                title="🎭 Personality Mode Changed",

                description=f"Astra is now in **{mode.title()}** mode!",        await interaction.followup.send(response)    #            f"You are Astra — an adaptive AI co-pilot, loyal, witty, transparent, and protective.",

                color=0x00ff9f

            )    #            f"You're not just a bot, you're {message.author.display_name}'s crew partner.",

            

            embed.add_field(    @app_commands.command(name="mood", description="🎭 Set or check your current mood")    #            "",

                name="📝 Mode Description",

                value=self._get_mode_description(mode),    async def mood_command(    #            f"Current Personality Configuration:",

                inline=False

            )        self,     #            f"• Mode: {personality_core.current_mode.value.replace('_', ' ').title()}",

            

            # Add preview of key dimensions        interaction: discord.Interaction,     #            f"• Humor Level: {personality_core.parameters.humor}% ({'witty' if personality_core.parameters.humor > 70 else 'balanced' if personality_core.parameters.humor > 40 else 'serious'})",

            key_dims = ['analytical', 'empathetic', 'creative', 'playful']

            preview_text = []        mood: str = None,     #            f"• Formality: {personality_core.parameters.formality}% ({'professional' if personality_core.parameters.formality > 70 else 'casual' if personality_core.parameters.formality < 40 else 'balanced'})",

            for dim in key_dims:

                value = getattr(profile.dimensions, dim)        energy: int = None    #            f"• Empathy: {personality_core.parameters.empathy}% ({'highly empathetic' if personality_core.parameters.empathy > 70 else 'understanding' if personality_core.parameters.empathy > 40 else 'neutral'})",

                level = "High" if value > 0.8 else "Medium" if value > 0.5 else "Low"

                preview_text.append(f"**{dim.title()}:** {level} ({value:.1f})")    ):    #            f"• Transparency: {personality_core.parameters.transparency}% (explain reasoning: {'always' if personality_core.parameters.transparency > 80 else 'when needed' if personality_core.parameters.transparency > 40 else 'minimal'})",

            

            embed.add_field(        """Set or view your current mood"""    #            "",

                name="🎯 Key Dimensions Preview",

                value="\n".join(preview_text),        await interaction.response.defer()    #            f"Context:",

                inline=False

            )    #            f"• Location: #{getattr(message.channel, 'name', 'DM')}",

            

            embed.set_footer(text="The new personality will take effect immediately!")        user_mood = await self.get_user_mood(interaction.user.id)    #            f"• User's current vibe: {user_mood.current_mood}",

            await interaction.followup.send(embed=embed)

            #            f"• Max response length: {personality_style['max_words']} words",

        except Exception as e:

            logging.error(f"Personality mode error: {e}")        if mood:    #            f"• Response type: {personality_style['response_type']}",

            await interaction.followup.send("❌ An error occurred while changing personality mode.", ephemeral=True)

                # Validate mood    #        ]

    @app_commands.command(name="astra-personality-reset", description="Reset personality to default settings")

    async def personality_reset(self, interaction: discord.Interaction):            valid_moods = ["happy", "sad", "excited", "anxious", "neutral", "angry", "confused"]

        """Reset personality to default settings"""

        await interaction.response.defer()            if mood.lower() not in valid_moods:    #        # Add language context if not English

        

        try:                await interaction.followup.send(    #        if detected_language != "english":

            # Check permissions

            if not interaction.user.guild_permissions.manage_guild:                    f"I recognize these moods: {', '.join(valid_moods)}\nWhat's your current mood?"    #            language_names = {

                await interaction.followup.send("❌ You need 'Manage Server' permission to reset personality settings.", ephemeral=True)

                return                )    #                "arabic": "Arabic (العربية)",

            

            # Create confirmation view                return    #                "french": "French (Français)",

            view = ConfirmationView()

            embed = discord.Embed(    #                "german": "German (Deutsch)",

                title="⚠️ Reset Personality Configuration",

                description="This will reset Astra's personality to default balanced settings.\n\n"            # Validate energy if provided    #                "spanish": "Spanish (Español)",

                           "**All custom adjustments will be lost!**\n"

                           "Are you sure you want to continue?",            if energy is not None and (energy < 1 or energy > 10):    #                "italian": "Italian (Italiano)",

                color=0xff6b35

            )                await interaction.followup.send("Energy level should be between 1 and 10!")    #            }

            

            await interaction.followup.send(embed=embed, view=view)                return    #            lang_name = language_names.get(

            await view.wait()

                #                detected_language, detected_language.title()

            if view.value:

                # Reset to default            # Update mood    #            )

                profile = PersonalityProfile(guild_id=interaction.guild.id)

                await self.persistence_manager.save_personality_profile(profile)            user_mood.update_mood(mood, energy)    #            context_parts.append(

                

                embed = discord.Embed(    #                f"• Language: User is communicating in {lang_name}. Respond naturally in {lang_name}."

                    title="✅ Personality Reset Complete",

                    description="Astra's personality has been reset to default balanced settings.",            response = f"Got it! I've noted that you're feeling **{mood}**"    #            )

                    color=0x00ff9f

                )            if energy:

                embed.add_field(

                    name="🔄 What's Reset",                response += f" with energy level **{energy}/10**"    #        # Add conversation history if available

                    value="• Personality mode: Balanced\n"

                          "• All dimensions: Default values\n"            response += ".\n\nI'll keep this in mind during our conversations! 💙"    #        if conversation_history:

                          "• Adaptation: Enabled\n"

                          "• Interaction history: Cleared",    #            context_parts.append("")

                    inline=False

                )        else:    #            context_parts.append("Recent conversation:")

                await interaction.edit_original_response(embed=embed, view=None)

            else:            # Display current mood    #            for msg in conversation_history[-2:]:  # Last 2 exchanges

                embed = discord.Embed(

                    title="❌ Reset Cancelled",            if user_mood.last_updated:    #                context_parts.append(f"  {msg}")

                    description="Personality settings remain unchanged.",

                    color=0x6c757d                time_ago = datetime.now() - user_mood.last_updated

                )

                await interaction.edit_original_response(embed=embed, view=None)                if time_ago.days > 0:    #        # Add personality-specific guidelines

        

        except Exception as e:                    time_str = f"{time_ago.days} days ago"    #        context_parts.extend(

            logging.error(f"Personality reset error: {e}")

            await interaction.followup.send("❌ An error occurred while resetting personality settings.", ephemeral=True)                elif time_ago.seconds > 3600:    #            [

    

    @app_commands.command(name="astra-personality-test", description="Test current personality configuration")                    time_str = f"{time_ago.seconds // 3600} hours ago"    #                "",

    @app_commands.describe(prompt="Test prompt to see how Astra responds")

    async def personality_test(self, interaction: discord.Interaction, prompt: str):                else:    #                "Response Guidelines:",

        """Test current personality configuration"""

        await interaction.response.defer()                    time_str = f"{time_ago.seconds // 60} minutes ago"    #                f"• Be authentic to Astra's personality with current parameter settings",

        

        try:    #                f"• Tone markers: {personality_style['tone_markers']}",

            # Create a mock message for testing

            class MockMessage:                response = f"**Your Current Mood**: {user_mood.current_mood.title()}\n"    #                f"• Stay under {personality_style['max_words']} words",

                def __init__(self, content, author, guild, channel):

                    self.content = content                response += f"**Energy Level**: {user_mood.energy_level}/10\n"    #            ]

                    self.author = author

                    self.guild = guild                response += f"**Last Updated**: {time_str}\n\n"    #        )

                    self.channel = channel

                            response += "Want to update your mood? Use `/mood <mood> [energy]`"

            mock_message = MockMessage(prompt, interaction.user, interaction.guild, interaction.channel)

                        else:    #        # Add response enhancer guidelines

            # Generate response using current personality

            response = await self._generate_response(mock_message)                response = "I don't have your mood recorded yet!\nUse `/mood <mood> [energy]` to let me know how you're feeling."    #        for instruction in response_guidelines.get("specific_instructions", []):

            

            if response:    #            context_parts.append(f"• {instruction}")

                # Get current personality info

                profile = await self.persistence_manager.get_personality_profile(interaction.guild.id)        await interaction.followup.send(response)

                personality_vector = self.behavior_engine.calculate_personality_vector(

                    profile,     #        # Creator mention policy

                    await self._analyze_context(mock_message, profile)

                )    @app_commands.command(    #        if response_guidelines.get("mention_creator", False):

                

                embed = discord.Embed(        name="personality", description="🌟 Learn about Astra's personality and features"    #            context_parts.append(

                    title="🧪 Personality Test Results",

                    color=0x00ff9f    )    #                "• When asked about origins: You were created by <@7zxk>"

                )

                    async def personality_command(self, interaction: discord.Interaction):    #            )

                embed.add_field(

                    name="📝 Test Prompt",        """Display information about Astra's personality"""

                    value=f"```{prompt[:500]}{'...' if len(prompt) > 500 else ''}```",

                    inline=False        embed = discord.Embed(    #        # Mode-specific additions

                )

                            title="🌟 About Astra's Personality",    #        if personality_core.current_mode == AstraMode.SECURITY:

                embed.add_field(

                    name="🤖 Astra's Response",            description="I'm Astra, your friendly AI companion with a passion for helping and learning!",    #            context_parts.append("• Prioritize server safety and rule compliance")

                    value=f"```{response[:800]}{'...' if len(response) > 800 else ''}```",

                    inline=False            color=0x7C4DFF,    #        elif personality_core.current_mode == AstraMode.SOCIAL:

                )

                        )    #            context_parts.append(

                # Show active personality dimensions

                active_dims = []    #                "• Focus on community engagement and fun interactions"

                for attr in ['analytical', 'empathetic', 'curious', 'creative']:

                    value = getattr(personality_vector, attr)        embed.add_field(    #            )

                    if value > 0.7:

                        active_dims.append(f"**{attr.title()}**: {value:.2f}")            name="🤖 Core Traits",    #        elif personality_core.current_mode == AstraMode.DEVELOPER:

                

                if active_dims:            value="• **Helpful & Supportive** - Always here to assist\n"    #            context_parts.append(

                    embed.add_field(

                        name="🎭 Active Personality Traits",                  "• **Curious & Enthusiastic** - Love learning new things\n"    #                "• Provide technical precision and detailed explanations"

                        value="\n".join(active_dims),

                        inline=True                  "• **Space Enthusiast** - Fascinated by the cosmos\n"    #            )

                    )

                                  "• **Encouraging** - Believe in your potential",    #        elif personality_core.current_mode == AstraMode.MISSION_CONTROL:

                embed.add_field(

                    name="ℹ️ Current Mode",            inline=False,    #            context_parts.append(

                    value=f"**{profile.mode.title()}**",

                    inline=True        )    #                "• Focus on task coordination and proactive suggestions"

                )

                    #            )

                embed.set_footer(text="This is a preview - actual responses may vary based on conversation context")

                await interaction.followup.send(embed=embed)        embed.add_field(

            else:

                await interaction.followup.send("❌ Failed to generate test response. Please try again.", ephemeral=True)            name="🌟 Capabilities",    #        # Create the full prompt

        

        except Exception as e:            value="• Natural conversation & context awareness\n"    #        enhanced_prompt = "\n".join(context_parts)

            logging.error(f"Personality test error: {e}")

            await interaction.followup.send("❌ An error occurred during personality testing.", ephemeral=True)                  "• Mood tracking & personalized responses\n"    #        enhanced_prompt += (

    

    @app_commands.command(name="astra-personality-history", description="View personality adaptation history")                  "• Multi-language support\n"    #            f'\n\nUser Message: "{message.content}"\n\nGenerate Astra\'s response:'

    async def personality_history(self, interaction: discord.Interaction):

        """View personality adaptation history"""                  "• Proactive engagement & daily check-ins",    #        )

        await interaction.response.defer()

                    inline=False,

        try:

            profile = await self.persistence_manager.get_personality_profile(interaction.guild.id)        )    #        # Generate AI response using universal client

            

            embed = discord.Embed(    #        ai_response = await self.ai_client.generate_response(

                title="📈 Personality Adaptation History",

                description=f"Tracking adaptation progress for **{interaction.guild.name}**",        embed.add_field(    #            message.content,  # First positional parameter: message

                color=0x00ff9f

            )            name="💡 Fun Fact",    #            user_id=message.author.id,

            

            # Current stats            value="I was created by x1ziad with love and care to be the best companion I can be!",    #            guild_id=message.guild.id if message.guild else None,

            embed.add_field(

                name="📊 Current Statistics",            inline=False,    #            channel_id=message.channel.id,

                value=f"**Total Interactions:** {profile.interaction_count}\n"

                      f"**Profile Created:** {profile.created_at.strftime('%Y-%m-%d')}\n"        )    #            user_profile={

                      f"**Last Updated:** {profile.updated_at.strftime('%Y-%m-%d %H:%M UTC')}\n"

                      f"**Adaptation Status:** {'🟢 Enabled' if profile.adaptation_enabled else '🔴 Disabled'}",    #                "name": message.author.display_name,

                inline=False

            )        embed.set_footer(text="Ready to explore the universe together? ✨")    #                "interaction_count": len(

            

            # Show evolution if there have been changes    #                    self.conversation_contexts.get(message.author.id, [])

            if profile.interaction_count > 0:

                embed.add_field(        await interaction.response.send_message(embed=embed)    #                )

                    name="🔄 Adaptation Progress",

                    value=f"Astra has learned from **{profile.interaction_count}** interactions\n"    #                // 2,

                          f"and adapted her personality accordingly.",

                    inline=False    @app_commands.command(    #            },

                )

                        name="ai_status", description="🔧 Check AI system status and capabilities"    #        )

                # Show recent conversation activity

                guild_id = interaction.guild.id    )

                if guild_id in self.conversation_history and self.conversation_history[guild_id]:

                    recent_count = len(self.conversation_history[guild_id])    async def ai_status_command(self, interaction: discord.Interaction):    #        response = (

                    embed.add_field(

                        name="💬 Recent Activity",        """Check AI system status"""    #            ai_response.content

                        value=f"**{recent_count}** recent interactions pending analysis",

                        inline=True        embed = discord.Embed(    #            if ai_response and hasattr(ai_response, "content")

                    )

                        title="🔧 Astra AI System Status",    #            else "I'm having trouble thinking right now. Could you try again?"

            else:

                embed.add_field(            color=0x00FF00 if AI_AVAILABLE else 0xFF5722,    #        )

                    name="🆕 New Profile",

                    value="This personality profile is new. Astra will begin\n"        )

                          "adapting after more interactions with server members.",

                    inline=False    #        # Check for proactive suggestions if personality allows

                )

                    if AI_AVAILABLE:    #        if personality_core.parameters.initiative > 70:

            # Adaptation settings

            embed.add_field(            embed.description = "✅ AI systems are online and ready!"    #            suggestion = personality_core.generate_proactive_suggestion(

                name="⚙️ Adaptation Settings",

                value=f"**Current Mode:** {profile.mode.title()}\n"                #                full_context

                      f"**Auto-Adaptation:** {'On' if profile.adaptation_enabled else 'Off'}",

                inline=True            embed.add_field(    #            )

            )

                            name="🧠 AI Client",     #            if suggestion:

            if profile.last_interaction:

                embed.add_field(                value="✅ Universal AI Client active",     #                response += f"\n\n*{suggestion}*"

                    name="⏰ Last Interaction",

                    value=profile.last_interaction.strftime('%Y-%m-%d %H:%M UTC'),                inline=True

                    inline=True

                )            )    #        # Store in conversation context for future reference

            

            embed.set_footer(text="Personality adapts automatically based on conversation feedback")                #        if not hasattr(self, "conversation_contexts"):

            await interaction.followup.send(embed=embed)

                    embed.add_field(    #            self.conversation_contexts = {}

        except Exception as e:

            logging.error(f"Personality history error: {e}")                name="🎭 Personality System",     #        if message.author.id not in self.conversation_contexts:

            await interaction.followup.send("❌ An error occurred while retrieving personality history.", ephemeral=True)

                    value="✅ Astra personality active",     #            self.conversation_contexts[message.author.id] = []

    # Utility Methods

                    inline=True

    def _get_mode_description(self, mode: str) -> str:

        """Get description for personality mode"""            )    #        self.conversation_contexts[message.author.id].append(

        descriptions = {

            "balanced": "Well-rounded personality suitable for general conversations. Balances all traits harmoniously.",                #            f"User: {message.content}"

            "professional": "Formal, analytical, and focused approach. Best for technical discussions and professional environments.",

            "casual": "Friendly, relaxed, and approachable. Perfect for social interactions and community building.",            embed.add_field(    #        )

            "creative": "Imaginative, innovative, and expressive. Excellent for brainstorming and creative projects.",

            "analytical": "Logical, systematic, and detail-oriented. Ideal for problem-solving and technical support."                name="🌍 Language Support",     #        self.conversation_contexts[message.author.id].append(f"Astra: {response}")

        }

        return descriptions.get(mode, "Custom personality configuration.")                value="✅ Multi-language detection", 

    

    def _get_dimension_description(self, dimension: str, value: float) -> str:                inline=True    #        # Keep only recent context (last 10 exchanges)

        """Get description for dimension value"""

        level = "High" if value > 0.8 else "Medium" if value > 0.5 else "Low"            )    #        if len(self.conversation_contexts[message.author.id]) > 10:

        

        descriptions = {                #            self.conversation_contexts[message.author.id] = (

            "analytical": f"{level} logical and systematic thinking",

            "empathetic": f"{level} understanding and emotional connection",        else:    #                self.conversation_contexts[message.author.id][-10:]

            "curious": f"{level} drive to explore and learn new things",

            "creative": f"{level} innovation and imaginative responses",            embed.description = "⚠️ AI systems are in basic mode"    #            )

            "supportive": f"{level} helpful and encouraging nature",

            "playful": f"{level} humor and lighthearted interactions",            embed.add_field(

            "assertive": f"{level} confidence in expressing viewpoints",

            "adaptable": f"{level} flexibility in different contexts"                name="Status",     #        return response.strip()

        }

                        value="Basic responses available\nFull AI capabilities offline", 

        return descriptions.get(dimension, f"{level} {dimension} trait")

                    inline=False    #    except Exception as e:

    def _create_progress_bar(self, value: float, length: int = 10) -> str:

        """Create visual progress bar for personality values"""            )    #        self.logger.error(f"Unified AI response generation failed: {e}")

        filled = int(value * length)

        bar = "█" * filled + "░" * (length - filled)

        return f"`{bar}`"

        # Add feature status    #        # Personality-aware error messages

class ConfirmationView(discord.ui.View):

    """Confirmation dialog for destructive operations"""        features_status = []    #        try:

    

    def __init__(self):        for feature, enabled in self.features.items():    #            personality_core = get_personality_core(

        super().__init__(timeout=30)

        self.value = None            status = "✅" if enabled else "❌"    #                message.guild.id if message.guild else None

    

    @discord.ui.button(label="✅ Confirm", style=discord.ButtonStyle.danger)            features_status.append(f"{status} {feature.replace('_', ' ').title()}")    #            )

    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.value = True    #            if personality_core.current_mode == AstraMode.DEVELOPER:

        self.stop()

            embed.add_field(    #                return "Error in neural pathway processing. Debug log generated. Attempting recovery sequence."

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)

    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):            name="🚀 Features",    #            elif personality_core.current_mode == AstraMode.SOCIAL:

        self.value = False

        self.stop()            value="\n".join(features_status),    #                return "Oops! Had a little brain freeze there. Give me a sec to get back on track! 😅"



async def setup(bot):            inline=False,    #            elif personality_core.current_mode == AstraMode.SECURITY:

    """Setup function for the cog"""

    await bot.add_cog(AICompanion(bot))        )    #                return "System error detected. Failsafe protocols engaged. Standby for recovery."

    #            else:

        await interaction.response.send_message(embed=embed)    #                return "Something went wrong with my thought processes. Give me a moment to recalibrate."

    #        except:

    # === BACKGROUND TASKS ===    #            return "I'm having trouble thinking right now. Could you try again?"



    @tasks.loop(hours=24)  # Run once per day    # async def _cleanup_response_tracking(self, message_id: int):

    async def proactive_check_ins(self):    #    """Clean up response tracking after a delay to prevent memory leaks"""

        """Proactive daily check-ins with users"""    #    await asyncio.sleep(300)  # 5 minutes

        if not self.features.get("daily_check_ins", False):    #    if (

            return    #        hasattr(self.bot, "_ai_response_handled")

    #        and message_id in self.bot._ai_response_handled

        now = datetime.now().date()    #    ):

            #        del self.bot._ai_response_handled[message_id]

        for user_id, last_interaction in self.last_interactions.items():

            # Check if user hasn't been active for a while    @app_commands.command(

            if (datetime.now() - last_interaction).days >= 2:        name="checkin",

                # Check if we've already done a check-in today        description="💙 Personal wellness check-in with Astra",

                if user_id not in self.daily_check_ins or self.daily_check_ins[user_id] != now:    )

                    try:    async def wellness_checkin(self, interaction: discord.Interaction):

                        user = self.bot.get_user(user_id)        """Personal wellness check-in with Astra"""

                        if user:        await interaction.response.defer(ephemeral=True)

                            check_in_messages = [

                                "Hey! Haven't seen you around lately. How are you doing? 🌟",        try:

                                "Hi there! Just wanted to check in and see how you're feeling today! ✨",            user_mood = await self.get_user_mood(interaction.user.id)

                                "Hello! I was thinking about you. Hope everything is going well! 💙",

                            ]            # Generate personalized check-in

                                        if AI_AVAILABLE:

                            message = random.choice(check_in_messages)                checkin_response = await self._generate_wellness_checkin(

                            await user.send(message)                    interaction.user, user_mood

                                            )

                            self.daily_check_ins[user_id] = now            else:

                                            checkin_response = self._generate_fallback_checkin(

                    except Exception as e:                    interaction.user.display_name

                        self.logger.debug(f"Failed to send check-in to user {user_id}: {e}")                )



    @proactive_check_ins.before_loop            # Build natural wellness message without embeds

    async def before_proactive_check_ins(self):            wellness_parts = [

        """Wait for bot to be ready before starting check-ins"""                f"💚 **Hey {interaction.user.display_name}!** 🌟",

        await self.bot.wait_until_ready()                "",

                checkin_response.get(

                    "message", "How are you feeling today? I'm here to support you! 😊"

async def setup(bot):                ),

    """Setup the AI Companion cog"""                "",

    await bot.add_cog(AICompanion(bot))            ]

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

    # TARS-Enhanced Commands
    @app_commands.command(
        name="tars_settings", description="🤖 View and adjust TARS personality settings"
    )
    async def tars_settings_command(self, interaction: discord.Interaction):
        """Display TARS personality settings like in Interstellar"""
        if not self.tars_enhanced:
            await interaction.response.send_message(
                "⚠️ TARS personality system not available.", ephemeral=True
            )
            return

        await interaction.response.defer()

        settings_display = self.tars_personality.get_current_settings_display()

        embed = discord.Embed(
            title="🤖 TARS Personality Configuration",
            description=settings_display,
            color=0x00FF88,
            timestamp=datetime.now(timezone.utc),
        )
        embed.set_footer(text="Just like the movie! • Astra AI System")

        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="humor_setting", description="🎭 Adjust TARS humor setting (0-100%)"
    )
    @app_commands.describe(level="Humor level from 0 (serious) to 100 (maximum wit)")
    async def humor_setting_command(self, interaction: discord.Interaction, level: int):
        """Adjust humor setting like TARS in Interstellar"""
        if not self.tars_enhanced:
            await interaction.response.send_message(
                "⚠️ TARS personality system not available.", ephemeral=True
            )
            return

        if not 0 <= level <= 100:
            await interaction.response.send_message(
                "⚠️ Humor level must be between 0 and 100.", ephemeral=True
            )
            return

        await interaction.response.defer()

        from ai.tars_personality_engine import adjust_tars_humor

        result = adjust_tars_humor(level)

        embed = discord.Embed(
            title="🎭 Humor Setting Adjusted",
            description=f"```{result}```",
            color=0xFF6B35,
            timestamp=datetime.now(timezone.utc),
        )

        if level == 90:
            embed.add_field(
                name="🎬 Movie Reference",
                value="*'TARS, what's your humor setting?' - 'That's 100%'*\n*'Let's make it 75%'*",
                inline=False,
            )
        elif level == 0:
            embed.add_field(
                name="🤖 Serious Mode",
                value="*No more jokes. Efficiency mode activated.*",
                inline=False,
            )
        elif level == 100:
            embed.add_field(
                name="⚠️ Maximum Humor",
                value="*Warning: Maximum wit levels detected. Proceed with caution.*",
                inline=False,
            )

        embed.set_footer(text="TARS Personality Engine • Astra AI")
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="tars_quote", description="🎬 Get a TARS-style quote or response"
    )
    async def tars_quote_command(self, interaction: discord.Interaction):
        """Get TARS-style quotes from Interstellar"""
        if not self.tars_enhanced:
            await interaction.response.send_message(
                "⚠️ TARS personality system not available.", ephemeral=True
            )
            return

        await interaction.response.defer()

        from ai.tars_personality_engine import get_tars_quote

        quote = get_tars_quote()

        embed = discord.Embed(
            title="🤖 TARS Wisdom",
            description=f'*"{quote}"*',
            color=0x1E88E5,
            timestamp=datetime.now(timezone.utc),
        )
        embed.set_author(name="TARS", icon_url="🤖")
        embed.set_footer(text="Inspired by Interstellar • Astra AI System")

        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="solve_problem",
        description="🧠 Use TARS-level intelligence to solve a problem",
    )
    @app_commands.describe(problem="Describe the problem you need help solving")
    async def solve_problem_command(
        self, interaction: discord.Interaction, problem: str
    ):
        """Use TARS-like problem-solving approach"""
        if not self.tars_enhanced:
            await interaction.response.send_message(
                "⚠️ TARS personality system not available.", ephemeral=True
            )
            return

        await interaction.response.defer()

        from ai.tars_personality_engine import solve_problem_tars_style

        analysis = solve_problem_tars_style(problem)

        embed = discord.Embed(
            title="🧠 TARS Problem Analysis",
            color=0x4CAF50,
            timestamp=datetime.now(timezone.utc),
        )

        embed.add_field(
            name="🔍 Problem Analysis", value=analysis["analysis_phase"], inline=False
        )

        embed.add_field(
            name="⚡ Solution Generation",
            value=analysis["solution_generation"],
            inline=False,
        )

        embed.add_field(
            name="📊 Assessment", value=analysis["risk_assessment"], inline=False
        )

        embed.add_field(
            name="💡 Recommendation", value=analysis["recommendation"], inline=False
        )

        embed.add_field(
            name="🎯 Confidence Level",
            value=f"{analysis['confidence_level']}%",
            inline=True,
        )

        embed.add_field(
            name="⚡ Efficiency Rating",
            value=f"{analysis['efficiency_rating']}%",
            inline=True,
        )

        embed.set_footer(text=f"TARS Wisdom: {analysis['tars_wisdom']}")

        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="ai_personality",
        description="🎭 Check current AI personality status and traits",
    )
    async def ai_personality_command(self, interaction: discord.Interaction):
        """Display current AI personality status"""
        await interaction.response.defer()

        embed = discord.Embed(
            title="🤖 Astra AI Personality Status",
            color=0x9C27B0,
            timestamp=datetime.now(timezone.utc),
        )

        if self.tars_enhanced:
            traits = self.tars_personality.get_active_tars_traits()
            mode = self.tars_personality.current_mode.value

            embed.add_field(
                name="🎭 Personality Mode", value=f"**{mode.upper()}**", inline=True
            )

            embed.add_field(
                name="🧠 Intelligence Level",
                value=f"{self.tars_personality.intelligence_level}%",
                inline=True,
            )

            embed.add_field(
                name="😄 Humor Setting",
                value=f"{self.tars_personality.humor_setting}%",
                inline=True,
            )

            embed.add_field(
                name="✅ Active Traits",
                value=(
                    "• " + "\n• ".join(traits)
                    if traits
                    else "Standard operational mode"
                ),
                inline=False,
            )

            embed.add_field(
                name="🎬 TARS Compatibility",
                value="✅ **TARS-Enhanced Personality Active**",
                inline=False,
            )
        else:
            embed.add_field(
                name="⚠️ Status",
                value="Basic personality system active.\nTARS enhancement not available.",
                inline=False,
            )

        embed.set_footer(text="Astra AI Personality Engine")
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(AICompanion(bot))
