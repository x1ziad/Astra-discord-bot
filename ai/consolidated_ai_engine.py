"""
Consolidated AI Engine for Astra Bot
Unified, high-performance AI system with advanced features and optimizations
"""

import asyncio
import logging
import time
import json
import re
import os
import random
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from collections import defaultdict, deque
import sqlite3
import hashlib
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import threading

# Cache imports with fallbacks
try:
    import redis.asyncio as redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# ML imports with fallbacks
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    np = None

# AI Provider imports
try:
    from ai.universal_ai_client import UniversalAIClient, AIResponse

    UNIVERSAL_AI_AVAILABLE = True
except ImportError:
    UNIVERSAL_AI_AVAILABLE = False

try:
    from ai.openrouter_client import OpenRouterClient

    OPENROUTER_AVAILABLE = True
except ImportError:
    OPENROUTER_AVAILABLE = False

logger = logging.getLogger("astra.consolidated_ai")


# Import the new advanced image generation system
try:
    from ai.image_generation_handler import ImageGenerationHandler, get_image_handler

    IMAGE_HANDLER_AVAILABLE = True
    logger.info("✅ Advanced Image Generation Handler imported successfully")
except ImportError as e:
    IMAGE_HANDLER_AVAILABLE = False
    logger.warning(f"❌ Image Generation Handler not available: {e}")

# Import the new Freepik API client
try:
    from ai.freepik_api_client import FreepikAPIClient, get_freepik_api_client

    FREEPIK_API_AVAILABLE = True
    logger.info("✅ Advanced Freepik API Client imported successfully")
except ImportError as e:
    FREEPIK_API_AVAILABLE = False
    logger.warning(f"❌ Freepik API Client not available: {e}")


# Legacy FreepikImageGenerator wrapper for backward compatibility
class FreepikImageGenerator:
    """Legacy wrapper for the new ImageGenerationHandler"""

    def __init__(self, api_key: str):
        if IMAGE_HANDLER_AVAILABLE:
            self.handler = ImageGenerationHandler(api_key)
            logger.info("🔄 Using advanced ImageGenerationHandler")
        else:
            self.handler = None
            logger.warning(
                "❌ ImageGenerationHandler not available - image generation disabled"
            )

    async def generate_image(self, prompt: str, user_id: int = None) -> Dict[str, Any]:
        """Generate image using advanced handler"""
        if self.handler:
            # Create context for the handler
            context = {
                "user_id": user_id or 0,
                "channel_id": 0,  # Default channel
                "guild_id": None,
                "request_type": "legacy_wrapper"
            }
            
            permissions = {
                "is_admin": True,  # Legacy calls assume admin permissions
                "is_mod": True
            }
            
            return await self.handler.generate_image(prompt, context, permissions)
        else:
            return {
                "success": False,
                "error": "Image generation handler not available",
                "message": "Image generation is not configured",
            }

    async def close(self):
        """Close the handler session"""
        if self.handler:
            await self.handler.close()

    def is_available(self) -> bool:
        """Check if image generation handler is available"""
        if not self.handler:
            return False
        
        # Avoid asyncio.run() in async context
        if hasattr(self.handler, 'is_available'):
            try:
                # Try to get current event loop
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # We're in an async context, return True (will be checked later)
                    return True
                else:
                    # Not in async context, safe to use asyncio.run()
                    return asyncio.run(self.handler.is_available())
            except RuntimeError:
                # No event loop, safe to use asyncio.run()
                return asyncio.run(self.handler.is_available())
        else:
            return True


class AIProvider(Enum):
    """Available AI providers in order of preference"""

    UNIVERSAL = "universal"
    OPENROUTER = "openrouter"
    OPENAI = "openai"
    MOCK = "mock"


class ConversationMood(Enum):
    """User emotional states with intensity levels"""

    ECSTATIC = "ecstatic"  # 0.9-1.0
    EXCITED = "excited"  # 0.8-0.9
    HAPPY = "happy"  # 0.7-0.8
    CONTENT = "content"  # 0.6-0.7
    CURIOUS = "curious"  # 0.5-0.6
    NEUTRAL = "neutral"  # 0.4-0.6
    CONFUSED = "confused"  # 0.3-0.5
    CONCERNED = "concerned"  # 0.2-0.4
    FRUSTRATED = "frustrated"  # 0.1-0.3
    SAD = "sad"  # 0.0-0.2
    ANGRY = "angry"  # 0.0-0.1


class EngagementTrigger(Enum):
    """Types of conversation triggers"""

    DIRECT_MENTION = "direct_mention"
    KEYWORD_MATCH = "keyword_match"
    QUESTION_ASKED = "question_asked"
    HELP_REQUEST = "help_request"
    TOPIC_EXPERTISE = "topic_expertise"
    EMOTIONAL_SUPPORT = "emotional_support"
    PROACTIVE_ENGAGEMENT = "proactive_engagement"
    CONVERSATION_CONTINUATION = "conversation_continuation"


@dataclass
class CacheConfig:
    """Cache configuration with intelligent defaults"""

    redis_url: Optional[str] = None
    ttl_short: int = 300  # 5 minutes for dynamic content
    ttl_medium: int = 1800  # 30 minutes for user profiles
    ttl_long: int = 3600  # 1 hour for static content
    max_memory_cache: int = 1000  # Max items in memory cache
    enable_compression: bool = True


@dataclass
class EmotionalContext:
    """Advanced emotional state tracking with momentum"""

    current_mood: ConversationMood = ConversationMood.NEUTRAL
    intensity: float = 0.5
    confidence: float = 0.5
    momentum: float = 0.0  # Rate of mood change
    history: deque = field(default_factory=lambda: deque(maxlen=10))
    triggers: List[str] = field(default_factory=list)

    def update_mood(self, mood: ConversationMood, intensity: float, confidence: float):
        """Update emotional state with momentum tracking"""
        # Calculate momentum
        old_intensity = self.intensity
        self.momentum = (intensity - old_intensity) * confidence

        # Update state
        self.current_mood = mood
        self.intensity = intensity
        self.confidence = confidence

        # Add to history
        self.history.append(
            {
                "mood": mood.value,
                "intensity": intensity,
                "confidence": confidence,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )


@dataclass
class UserProfile:
    """Comprehensive user profile with behavioral patterns"""

    user_id: int
    display_name: str = ""

    # Interaction patterns
    total_interactions: int = 0
    avg_response_time: float = 0.0
    preferred_times: List[int] = field(default_factory=lambda: [12, 18, 20])

    # Content preferences
    preferred_topics: Dict[str, float] = field(default_factory=dict)
    communication_style: str = "casual"
    response_length_preference: str = "medium"  # short, medium, long

    # Emotional profile
    emotional_baseline: float = 0.5
    empathy_responsiveness: float = 0.7
    mood_patterns: Dict[str, int] = field(default_factory=dict)

    # Engagement metrics
    engagement_score: float = 0.5
    interaction_frequency: float = 0.0  # messages per day
    last_interaction: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # Learning and adaptation
    response_feedback_scores: List[float] = field(default_factory=list)
    conversation_success_rate: float = 0.5

    def update_interaction(
        self,
        topic: str = None,
        response_time: float = None,
        engagement_delta: float = 0.0,
    ):
        """Update profile based on new interaction"""
        self.total_interactions += 1
        self.last_interaction = datetime.now(timezone.utc)

        if response_time:
            # Exponential moving average for response time
            alpha = 0.1
            self.avg_response_time = (
                alpha * response_time + (1 - alpha) * self.avg_response_time
            )

        if topic:
            # Update topic preferences with learning rate
            current_score = self.preferred_topics.get(topic, 0.5)
            learning_rate = 0.05
            self.preferred_topics[topic] = min(
                1.0, max(0.0, current_score + engagement_delta * learning_rate)
            )

        # Update engagement score with momentum
        momentum = 0.1
        self.engagement_score = min(
            1.0, max(0.0, self.engagement_score + engagement_delta * momentum)
        )


@dataclass
class ConversationContext:
    """Rich conversation context with intelligent memory management"""

    user_id: int
    guild_id: Optional[int] = None
    channel_id: Optional[int] = None

    # Message history with smart truncation
    messages: deque = field(default_factory=lambda: deque(maxlen=20))
    important_messages: List[Dict[str, Any]] = field(default_factory=list)

    # Context understanding
    active_topics: Set[str] = field(default_factory=set)
    conversation_theme: str = "general"
    context_embeddings: Optional[List[float]] = None

    # Emotional and engagement tracking
    emotional_context: EmotionalContext = field(default_factory=EmotionalContext)
    engagement_momentum: float = 0.0
    conversation_quality: float = 0.5

    # Timing and flow
    last_interaction: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    conversation_start: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    turn_count: int = 0

    # Memory anchors for important conversation points
    memory_anchors: List[Dict[str, Any]] = field(default_factory=list)

    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add message with intelligent importance scoring"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
            "importance_score": self._calculate_importance(content, role),
        }

        self.messages.append(message)
        self.turn_count += 1
        self.last_interaction = datetime.now(timezone.utc)

        # Archive important messages
        if message["importance_score"] > 0.7:
            self.important_messages.append(message)
            if len(self.important_messages) > 10:
                self.important_messages = self.important_messages[-10:]

    def _calculate_importance(self, content: str, role: str) -> float:
        """Calculate message importance for memory retention"""
        importance = 0.0

        # Length factor
        importance += min(0.3, len(content) / 500)

        # Question/answer pairs are important
        if "?" in content:
            importance += 0.2

        # User messages generally more important than AI responses
        if role == "user":
            importance += 0.1

        # Keywords that indicate important information
        important_keywords = [
            "help",
            "learn",
            "explain",
            "problem",
            "issue",
            "stellaris",
            "space",
            "strategy",
        ]
        keyword_matches = sum(
            1 for keyword in important_keywords if keyword.lower() in content.lower()
        )
        importance += min(0.3, keyword_matches * 0.1)

        return min(1.0, importance)


class IntelligentCache:
    """High-performance caching system with multiple backends"""

    def __init__(self, config: CacheConfig):
        self.config = config
        self.redis_client = None
        self.memory_cache: Dict[str, Any] = {}
        self.memory_timestamps: Dict[str, float] = {}
        self.cache_hits = 0
        self.cache_misses = 0

        # Initialize Redis if available
        if REDIS_AVAILABLE and config.redis_url:
            try:
                self.redis_client = redis.from_url(config.redis_url)
                logger.info("Redis cache initialized")
            except Exception as e:
                logger.warning(f"Redis initialization failed: {e}")

    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache with fallback hierarchy"""
        # Try memory cache first
        if key in self.memory_cache:
            if time.time() - self.memory_timestamps[key] < self.config.ttl_short:
                self.cache_hits += 1
                return self.memory_cache[key]
            else:
                del self.memory_cache[key]
                del self.memory_timestamps[key]

        # Try Redis cache
        if self.redis_client:
            try:
                value = await self.redis_client.get(key)
                if value:
                    self.cache_hits += 1
                    decoded_value = json.loads(value)
                    # Update memory cache
                    self._update_memory_cache(key, decoded_value)
                    return decoded_value
            except Exception as e:
                logger.warning(f"Redis get error: {e}")

        self.cache_misses += 1
        return default

    async def set(self, key: str, value: Any, ttl: int = None):
        """Set value in cache with intelligent TTL"""
        ttl = ttl or self.config.ttl_medium

        # Update memory cache
        self._update_memory_cache(key, value)

        # Update Redis cache
        if self.redis_client:
            try:
                serialized_value = json.dumps(value, default=str)
                await self.redis_client.setex(key, ttl, serialized_value)
            except Exception as e:
                logger.warning(f"Redis set error: {e}")

    def _update_memory_cache(self, key: str, value: Any):
        """Update memory cache with LRU eviction"""
        if len(self.memory_cache) >= self.config.max_memory_cache:
            # Remove oldest item
            oldest_key = min(
                self.memory_timestamps.keys(), key=lambda k: self.memory_timestamps[k]
            )
            del self.memory_cache[oldest_key]
            del self.memory_timestamps[oldest_key]

        self.memory_cache[key] = value
        self.memory_timestamps[key] = time.time()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "hit_rate": hit_rate,
            "total_hits": self.cache_hits,
            "total_misses": self.cache_misses,
            "memory_cache_size": len(self.memory_cache),
            "redis_available": self.redis_client is not None,
        }


class AdvancedSentimentAnalyzer:
    """High-performance sentiment analysis with ML enhancement"""

    def __init__(self):
        self.emotion_patterns = {
            ConversationMood.ECSTATIC: {
                "keywords": [
                    "amazing",
                    "incredible",
                    "fantastic",
                    "mind-blowing",
                    "phenomenal",
                ],
                "patterns": [r"!{2,}", r"wow+", r"omg+"],
                "intensity_base": 0.95,
            },
            ConversationMood.EXCITED: {
                "keywords": ["excited", "thrilled", "awesome", "great", "love"],
                "patterns": [r"!+", r"yay+", r"woohoo+"],
                "intensity_base": 0.85,
            },
            ConversationMood.HAPPY: {
                "keywords": ["happy", "glad", "pleased", "good", "nice"],
                "patterns": [r":\)", r"😊", r"😄"],
                "intensity_base": 0.75,
            },
            ConversationMood.CURIOUS: {
                "keywords": ["curious", "wonder", "interesting", "how", "why"],
                "patterns": [r"\?+", r"hmm+", r"🤔"],
                "intensity_base": 0.55,
            },
            ConversationMood.CONFUSED: {
                "keywords": ["confused", "lost", "unclear", "don't understand"],
                "patterns": [r"\?\?\?+", r"huh+", r"😕"],
                "intensity_base": 0.35,
            },
            ConversationMood.FRUSTRATED: {
                "keywords": ["frustrated", "annoyed", "ugh", "annoying"],
                "patterns": [r"argh+", r"grrr+", r"😤"],
                "intensity_base": 0.25,
            },
            ConversationMood.SAD: {
                "keywords": ["sad", "disappointed", "down", "upset"],
                "patterns": [r":\(", r"😢", r"😞"],
                "intensity_base": 0.15,
            },
        }

        self.intensity_modifiers = {
            "very": 1.5,
            "extremely": 2.0,
            "super": 1.8,
            "really": 1.3,
            "quite": 1.2,
            "somewhat": 0.8,
            "a bit": 0.7,
            "slightly": 0.6,
        }

    def analyze_sentiment(self, text: str) -> Tuple[ConversationMood, float, float]:
        """Analyze sentiment with mood, intensity, and confidence scores"""
        text_lower = text.lower()
        mood_scores = defaultdict(float)

        # Keyword and pattern matching
        for mood, patterns in self.emotion_patterns.items():
            score = patterns["intensity_base"]

            # Keyword matching
            keyword_matches = sum(
                1 for keyword in patterns["keywords"] if keyword in text_lower
            )
            if keyword_matches > 0:
                mood_scores[mood] += score * keyword_matches * 0.3

            # Pattern matching
            for pattern in patterns["patterns"]:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                if matches > 0:
                    mood_scores[mood] += score * matches * 0.2

        # Apply intensity modifiers
        for modifier, multiplier in self.intensity_modifiers.items():
            if modifier in text_lower:
                for mood in mood_scores:
                    mood_scores[mood] *= multiplier

        # Punctuation analysis
        exclamation_count = text.count("!")
        if exclamation_count > 0:
            mood_scores[ConversationMood.EXCITED] += exclamation_count * 0.1

        question_count = text.count("?")
        if question_count > 0:
            mood_scores[ConversationMood.CURIOUS] += question_count * 0.1

        # Determine dominant mood
        if mood_scores:
            dominant_mood = max(mood_scores.keys(), key=lambda k: mood_scores[k])
            intensity = min(1.0, mood_scores[dominant_mood])

            # Calculate confidence based on score distribution
            total_score = sum(mood_scores.values())
            confidence = (
                mood_scores[dominant_mood] / total_score if total_score > 0 else 0.5
            )
        else:
            dominant_mood = ConversationMood.NEUTRAL
            intensity = 0.5
            confidence = 0.3

        return dominant_mood, intensity, confidence


class ConversationFlowEngine:
    """Dynamic conversation flow system that adapts to user vibes without rigid personality constraints"""

    def __init__(self):
        # Base interaction principles instead of personality traits
        self.base_interaction_style = {
            "helpfulness": 0.9,  # Always try to be helpful
            "adaptability": 0.8,  # Adapt to user's communication style
            "contextual_awareness": 0.9,  # Understand conversation context
            "natural_flow": 0.8,  # Maintain natural conversation flow
            "conciseness": 0.7,  # Balance between concise and detailed
            "engagement": 0.8,  # Stay engaged but not forced
        }

    def get_conversation_style(
        self, context: ConversationContext, user_profile: UserProfile
    ) -> Dict[str, float]:
        """Get conversation style adapted to current context and user vibe"""
        style = self.base_interaction_style.copy()

        # Adapt based on user's recent communication patterns
        if context.messages:
            recent_user_messages = [
                msg for msg in list(context.messages)[-5:] if msg.get("role") == "user"
            ]

            if recent_user_messages:
                # Analyze user's current communication style
                avg_length = sum(
                    len(msg.get("content", "")) for msg in recent_user_messages
                ) / len(recent_user_messages)

                # Adjust conciseness based on user's message length
                if avg_length < 30:  # User sends short messages
                    style["conciseness"] = 0.9
                elif avg_length > 100:  # User sends long messages
                    style["conciseness"] = 0.4

                # Check for question patterns
                question_ratio = sum(
                    1 for msg in recent_user_messages if "?" in msg.get("content", "")
                ) / len(recent_user_messages)
                if question_ratio > 0.5:  # User asks lots of questions
                    style["helpfulness"] = 0.95

        # Mood-based adjustments (subtle, not forced)
        mood = context.emotional_context.current_mood
        if mood == ConversationMood.CONFUSED:
            style["helpfulness"] = 0.95
            style["conciseness"] = 0.6  # Be more detailed when explaining
        elif mood == ConversationMood.EXCITED:
            style["engagement"] = 0.9
        elif mood == ConversationMood.SAD:
            style["helpfulness"] = 0.9
            style["engagement"] = 0.7  # More supportive, less energetic

        # Topic-based adjustments (flexible, not rigid)
        if context.active_topics:
            # Technical topics might need more detail
            technical_topics = ["programming", "science", "technology", "stellaris"]
            if any(topic in technical_topics for topic in context.active_topics):
                style["conciseness"] = max(0.3, style["conciseness"] - 0.2)

        # User relationship adjustments
        if user_profile.total_interactions > 10:
            style["contextual_awareness"] = 0.95  # Better context understanding
            style["natural_flow"] = 0.9  # More natural conversation flow

        return style


class ConsolidatedAIEngine:
    """Main AI engine consolidating all advanced features"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logger

        # Initialize components
        self.cache = IntelligentCache(
            CacheConfig(
                redis_url=self.config.get("redis_url"),
                ttl_short=self.config.get("cache_ttl_short", 300),
                ttl_medium=self.config.get("cache_ttl_medium", 1800),
                ttl_long=self.config.get("cache_ttl_long", 3600),
            )
        )

        self.sentiment_analyzer = AdvancedSentimentAnalyzer()
        self.flow_engine = ConversationFlowEngine()

        # Image generation
        self.freepik_generator = None
        self._initialize_image_generation()

        # Image generation permissions
        self.image_config = {
            "default_channel_id": 1402666535696470169,  # Default channel for regular users
            "mod_anywhere": True,  # Mods can use image generation anywhere
            "admin_anywhere": True,  # Admins can use image generation anywhere
            "rate_limit": {
                "regular_users": 5,  # 5 images per hour for regular users
                "mods": 20,  # 20 images per hour for mods
                "admins": 50,  # 50 images per hour for admins
            },
        }

        # AI providers
        self.ai_providers: Dict[AIProvider, Any] = {}
        self.active_provider = None
        self._initialize_providers()

        # Conversation management
        self.conversations: Dict[int, ConversationContext] = {}
        self.user_profiles: Dict[int, UserProfile] = {}

        # Performance tracking
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "avg_response_time": 0.0,
            "cache_hits": 0,
            "provider_usage": defaultdict(int),
        }

        # Database
        self.db_path = Path("data/consolidated_ai.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

        # Thread pool for CPU-intensive operations
        self.thread_pool = ThreadPoolExecutor(max_workers=4)

        logger.info("Consolidated AI Engine initialized successfully")

    def _initialize_image_generation(self):
        """Initialize image generation with advanced handler"""
        freepik_api_key = self.config.get("freepik_api_key") or os.getenv(
            "FREEPIK_API_KEY"
        )

        if freepik_api_key and IMAGE_HANDLER_AVAILABLE:
            try:
                # Use the advanced image generation handler
                self.freepik_generator = FreepikImageGenerator(freepik_api_key)
                logger.info(
                    "✅ Image generation initialized with advanced handler"
                )
                logger.info(
                    f"🔑 API Key configured: {freepik_api_key[:10]}...{freepik_api_key[-4:]}"
                )
            except Exception as e:
                logger.error(f"❌ Image generation initialization failed: {e}")
                self.freepik_generator = None
        elif freepik_api_key and not IMAGE_HANDLER_AVAILABLE:
            logger.error(
                "❌ FREEPIK_API_KEY found but ImageGenerationHandler not available"
            )
            logger.error("🔧 Check ai/image_generation_handler.py import")
            self.freepik_generator = None
        else:
            logger.warning("⚠️  FREEPIK_API_KEY not found - image generation disabled")
            logger.warning("🌐 Get your key at: https://www.freepik.com/api")
            logger.warning("⚙️  Set FREEPIK_API_KEY in Railway environment variables")
            self.freepik_generator = None

    def _initialize_providers(self):
        """Initialize AI providers in order of preference"""
        # Universal AI (primary)
        if UNIVERSAL_AI_AVAILABLE:
            try:
                universal_client = UniversalAIClient(
                    api_key=self.config.get("ai_api_key") or os.getenv("AI_API_KEY"),
                    base_url=self.config.get("ai_base_url") or os.getenv("AI_BASE_URL"),
                    model=self.config.get("ai_model") or os.getenv("AI_MODEL"),
                )
                if universal_client.is_available():
                    self.ai_providers[AIProvider.UNIVERSAL] = universal_client
                    self.active_provider = AIProvider.UNIVERSAL
                    logger.info("Universal AI provider initialized")
            except Exception as e:
                logger.warning(f"Universal AI provider failed: {e}")

        # OpenRouter (secondary)
        if OPENROUTER_AVAILABLE:
            try:
                openrouter_client = OpenRouterClient(
                    openrouter_api_key=self.config.get("openrouter_api_key")
                    or os.getenv("OPENROUTER_API_KEY"),
                    openai_api_key=self.config.get("openai_api_key")
                    or os.getenv("OPENAI_API_KEY"),
                )
                if openrouter_client.is_available():
                    self.ai_providers[AIProvider.OPENROUTER] = openrouter_client
                    if not self.active_provider:
                        self.active_provider = AIProvider.OPENROUTER
                    logger.info("OpenRouter provider initialized")
            except Exception as e:
                logger.warning(f"OpenRouter provider failed: {e}")

        if not self.active_provider:
            logger.warning("No AI providers available - using mock responses")
            self.active_provider = AIProvider.MOCK

    def _initialize_database(self):
        """Initialize optimized database schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Conversations table with indexes
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        guild_id INTEGER,
                        channel_id INTEGER,
                        message_content TEXT NOT NULL,
                        response_content TEXT NOT NULL,
                        mood TEXT,
                        intensity REAL,
                        confidence REAL,
                        topics TEXT,
                        engagement_score REAL,
                        response_time_ms REAL,
                        provider TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Create indexes for conversations table
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations (user_id)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations (created_at)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_conversations_mood ON conversations (mood)"
                )

                # User profiles table
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        user_id INTEGER PRIMARY KEY,
                        display_name TEXT,
                        total_interactions INTEGER DEFAULT 0,
                        preferred_topics TEXT,
                        communication_style TEXT DEFAULT 'casual',
                        emotional_baseline REAL DEFAULT 0.5,
                        engagement_score REAL DEFAULT 0.5,
                        interaction_frequency REAL DEFAULT 0.0,
                        conversation_success_rate REAL DEFAULT 0.5,
                        last_interaction TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Create indexes for user_profiles table
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_user_profiles_last_interaction ON user_profiles (last_interaction)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_user_profiles_engagement_score ON user_profiles (engagement_score)"
                )

                # Performance metrics table
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_name TEXT NOT NULL,
                        metric_value REAL NOT NULL,
                        provider TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Create indexes for performance_metrics table
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_performance_metrics_metric_name ON performance_metrics (metric_name)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics (timestamp)"
                )

                # Image generations table
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS image_generations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        channel_id INTEGER NOT NULL,
                        prompt TEXT NOT NULL,
                        provider TEXT NOT NULL,
                        success BOOLEAN NOT NULL DEFAULT 0,
                        error_message TEXT,
                        image_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Create indexes for image_generations table
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_image_generations_user_id ON image_generations (user_id)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_image_generations_channel_id ON image_generations (channel_id)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_image_generations_created_at ON image_generations (created_at)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_image_generations_provider ON image_generations (provider)"
                )

                conn.commit()
                logger.info(
                    "Database initialized with optimized schema including image generations"
                )

        except Exception as e:
            logger.error(f"Database initialization failed: {e}")

    async def process_conversation(
        self,
        message: str,
        user_id: int,
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
        context_data: Dict[str, Any] = None,
    ) -> str:
        """Main conversation processing with full optimization"""
        start_time = time.time()

        try:
            # Get or create conversation context and user profile
            context = await self._get_conversation_context(
                user_id, guild_id, channel_id
            )
            user_profile = await self._get_user_profile(user_id)

            # Analyze sentiment with caching
            cache_key = f"sentiment:{hashlib.md5(message.encode()).hexdigest()}"
            sentiment_result = await self.cache.get(cache_key)

            if not sentiment_result:
                mood, intensity, confidence = self.sentiment_analyzer.analyze_sentiment(
                    message
                )
                sentiment_result = (mood, intensity, confidence)
                await self.cache.set(
                    cache_key, sentiment_result, ttl=self.cache.config.ttl_long
                )
            else:
                mood, intensity, confidence = sentiment_result
                mood = ConversationMood(mood) if isinstance(mood, str) else mood

            # Update emotional context
            context.emotional_context.update_mood(mood, intensity, confidence)

            # Extract topics
            topics = await self._extract_topics(message)
            context.active_topics.update(topics[:3])  # Keep top 3 topics

            # Add message to context
            context.add_message(
                "user",
                message,
                {
                    "mood": mood.value,
                    "intensity": intensity,
                    "confidence": confidence,
                    "topics": topics,
                },
            )

            # Generate AI response
            response = await self._generate_ai_response(context, user_profile, message)

            # Add response to context
            context.add_message("assistant", response)

            # Update user profile
            response_time = (time.time() - start_time) * 1000
            engagement_delta = self._calculate_engagement_delta(
                message, response, topics
            )
            user_profile.update_interaction(
                topic=topics[0] if topics else None,
                response_time=response_time,
                engagement_delta=engagement_delta,
            )

            # Update performance metrics
            self.performance_metrics["total_requests"] += 1
            self.performance_metrics["successful_requests"] += 1
            self.performance_metrics["avg_response_time"] = (
                self.performance_metrics["avg_response_time"]
                * (self.performance_metrics["total_requests"] - 1)
                + response_time
            ) / self.performance_metrics["total_requests"]

            # Save to database (async to avoid blocking)
            asyncio.create_task(
                self._save_conversation_async(
                    context,
                    message,
                    response,
                    mood,
                    intensity,
                    confidence,
                    topics,
                    engagement_delta,
                    response_time,
                )
            )

            return response

        except Exception as e:
            self.logger.error(f"Conversation processing error: {e}")
            return self._get_fallback_response(message, user_id)

    async def _get_conversation_context(
        self, user_id: int, guild_id: Optional[int], channel_id: Optional[int]
    ) -> ConversationContext:
        """Get or create conversation context with caching"""
        cache_key = f"context:{user_id}"
        cached_context = await self.cache.get(cache_key)

        if cached_context and user_id in self.conversations:
            return self.conversations[user_id]

        if user_id not in self.conversations:
            self.conversations[user_id] = ConversationContext(
                user_id=user_id, guild_id=guild_id, channel_id=channel_id
            )

        # Cache the context
        await self.cache.set(cache_key, True, ttl=self.cache.config.ttl_short)

        return self.conversations[user_id]

    async def _get_user_profile(self, user_id: int) -> UserProfile:
        """Get or create user profile with database persistence"""
        cache_key = f"profile:{user_id}"
        cached_profile = await self.cache.get(cache_key)

        if cached_profile:
            # Reconstruct profile from cache
            profile = UserProfile(**cached_profile)
            self.user_profiles[user_id] = profile
            return profile

        if user_id not in self.user_profiles:
            # Try loading from database
            profile_data = await self._load_user_profile_from_db(user_id)
            if profile_data:
                self.user_profiles[user_id] = profile_data
            else:
                self.user_profiles[user_id] = UserProfile(user_id=user_id)

        profile = self.user_profiles[user_id]

        # Cache the profile
        profile_dict = {
            "user_id": profile.user_id,
            "display_name": profile.display_name,
            "total_interactions": profile.total_interactions,
            "preferred_topics": profile.preferred_topics,
            "communication_style": profile.communication_style,
            "engagement_score": profile.engagement_score,
            "interaction_frequency": profile.interaction_frequency,
            "last_interaction": profile.last_interaction.isoformat(),
        }
        await self.cache.set(cache_key, profile_dict, ttl=self.cache.config.ttl_medium)

        return profile

    async def _load_user_profile_from_db(self, user_id: int) -> Optional[UserProfile]:
        """Load user profile from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT display_name, total_interactions, preferred_topics,
                           communication_style, emotional_baseline, engagement_score,
                           interaction_frequency, conversation_success_rate, last_interaction
                    FROM user_profiles WHERE user_id = ?
                """,
                    (user_id,),
                )

                row = cursor.fetchone()
                if row:
                    return UserProfile(
                        user_id=user_id,
                        display_name=row[0] or "",
                        total_interactions=row[1] or 0,
                        preferred_topics=json.loads(row[2]) if row[2] else {},
                        communication_style=row[3] or "casual",
                        emotional_baseline=row[4] or 0.5,
                        engagement_score=row[5] or 0.5,
                        interaction_frequency=row[6] or 0.0,
                        conversation_success_rate=row[7] or 0.5,
                        last_interaction=(
                            datetime.fromisoformat(row[8])
                            if row[8]
                            else datetime.now(timezone.utc)
                        ),
                    )
        except Exception as e:
            logger.warning(f"Failed to load user profile for {user_id}: {e}")

        return None

    async def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text with caching"""
        cache_key = f"topics:{hashlib.md5(text.encode()).hexdigest()}"
        cached_topics = await self.cache.get(cache_key)

        if cached_topics:
            return cached_topics

        # Topic extraction logic
        topic_keywords = {
            "stellaris": ["stellaris", "empire", "species", "galactic", "federation"],
            "space": ["space", "cosmos", "universe", "star", "planet", "galaxy"],
            "science": ["science", "research", "discovery", "experiment", "theory"],
            "gaming": ["game", "gaming", "play", "strategy", "multiplayer"],
            "technology": ["technology", "ai", "computer", "software", "algorithm"],
        }

        text_lower = text.lower()
        found_topics = []

        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                found_topics.append(topic)

        # Cache the result
        await self.cache.set(cache_key, found_topics, ttl=self.cache.config.ttl_long)

        return found_topics

    async def _generate_ai_response(
        self, context: ConversationContext, user_profile: UserProfile, message: str
    ) -> str:
        """Generate AI response with provider fallback"""
        # Get conversation style
        style = self.flow_engine.get_conversation_style(context, user_profile)

        # Build system prompt
        system_prompt = self._build_system_prompt(context, user_profile, style)

        # Prepare messages
        messages = self._prepare_messages(context, system_prompt)

        # Try providers in order
        for provider in [self.active_provider] + [
            p for p in self.ai_providers.keys() if p != self.active_provider
        ]:
            if provider in self.ai_providers:
                try:
                    client = self.ai_providers[provider]

                    # Check if this is our universal client pattern
                    if hasattr(client, "chat_completion"):
                        response = await client.chat_completion(messages)
                        response_text = (
                            response.content
                            if hasattr(response, "content")
                            else str(response)
                        )
                    else:
                        # Fallback for other client types
                        response_text = await client.generate_text(message)

                    # Track provider usage
                    self.performance_metrics["provider_usage"][provider.value] += 1

                    return self._post_process_response(response_text, context, style)

                except Exception as e:
                    logger.warning(f"Provider {provider.value} failed: {e}")
                    continue

        # All providers failed - use fallback
        return self._get_fallback_response(message, context.user_id)

    def _build_system_prompt(
        self,
        context: ConversationContext,
        user_profile: UserProfile,
        style: Dict[str, float],
    ) -> str:
        """Build dynamic system prompt based on user vibe and context"""

        # Core neutral prompt - no rigid personality constraints
        base_prompt = """You are an intelligent AI assistant that adapts naturally to conversations. You understand context, remember interactions, and respond authentically based on the flow of conversation.

Key principles:
- Match the user's communication style naturally
- Be concise but thorough when needed
- Understand emotional context without forcing personality
- Flow with the conversation rather than following rigid patterns
- Recognize each user as an individual with unique preferences"""

        # Adaptive context based on user interaction patterns
        if user_profile.total_interactions > 0:
            # Analyze user's typical interaction style
            if user_profile.communication_style == "casual":
                base_prompt += (
                    "\n\nThis user prefers relaxed, conversational interactions."
                )
            elif user_profile.communication_style == "formal":
                base_prompt += (
                    "\n\nThis user appreciates more structured, professional responses."
                )

            # User familiarity
            if user_profile.total_interactions > 20:
                base_prompt += f"\n\nYou've had {user_profile.total_interactions} interactions with this user. Build on your shared conversation history naturally."
            elif user_profile.total_interactions > 5:
                base_prompt += "\n\nYou're becoming familiar with this user. Reference past conversations when relevant."

        # Emotional context awareness (without forced responses)
        mood = context.emotional_context.current_mood
        mood_context = {
            ConversationMood.CONFUSED: "The user seems to need clarity. Provide clear, helpful explanations.",
            ConversationMood.EXCITED: "The user is enthusiastic. Share in their energy appropriately.",
            ConversationMood.SAD: "The user may need support. Be understanding and helpful.",
            ConversationMood.CURIOUS: "The user is interested and asking questions. Provide engaging, informative responses.",
            ConversationMood.FRUSTRATED: "The user seems frustrated. Be patient and solution-focused.",
        }

        if mood in mood_context:
            base_prompt += f"\n\n{mood_context[mood]}"

        # Topic awareness
        if context.active_topics:
            topics_str = ", ".join(context.active_topics)
            base_prompt += f"\n\nCurrent conversation involves: {topics_str}. Stay relevant to these topics."

        # Response length guidance based on context
        recent_messages = list(context.messages)[-3:] if context.messages else []
        if recent_messages:
            avg_user_message_length = sum(
                len(msg.get("content", ""))
                for msg in recent_messages
                if msg.get("role") == "user"
            ) / max(1, sum(1 for msg in recent_messages if msg.get("role") == "user"))

            if avg_user_message_length < 50:
                base_prompt += "\n\nUser tends to send short messages. Keep responses concise and conversational."
            elif avg_user_message_length > 200:
                base_prompt += "\n\nUser sends detailed messages. Feel free to provide comprehensive responses."

        base_prompt += "\n\nRespond naturally and authentically. No need for consistent personality quirks or forced characteristics."

        return base_prompt

    def _prepare_messages(
        self, context: ConversationContext, system_prompt: str
    ) -> List[Dict[str, str]]:
        """Prepare messages for AI provider with intelligent truncation"""
        messages = [{"role": "system", "content": system_prompt}]

        # Add important messages first
        for msg in context.important_messages[-3:]:  # Last 3 important messages
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Add recent conversation history
        recent_messages = list(context.messages)[-8:]  # Last 8 messages

        for msg in recent_messages:
            if msg not in [
                m for m in context.important_messages[-3:]
            ]:  # Avoid duplicates
                messages.append({"role": msg["role"], "content": msg["content"]})

        return messages

    def _post_process_response(
        self,
        response: str,
        context: ConversationContext,
        style: Dict[str, float],
    ) -> str:
        """Post-process AI response for natural conversation flow"""

        # Remove forced personality modifications - let the response be natural
        response = response.strip()

        # Only add context-appropriate elements based on user behavior
        if context.messages:
            # Check user's recent emoji usage
            recent_user_messages = [
                msg for msg in list(context.messages)[-5:] if msg.get("role") == "user"
            ]
            user_uses_emojis = any(
                any(ord(char) > 127 for char in msg.get("content", ""))
                for msg in recent_user_messages
            )

            # Only add emojis if user uses them naturally in conversation
            if user_uses_emojis and not any(ord(char) > 127 for char in response):
                # Add contextual emoji based on conversation topic, not forced themes
                if any(
                    word in response.lower()
                    for word in ["space", "universe", "cosmic", "stellar"]
                ):
                    response += " ✨"
                elif any(
                    word in response.lower() for word in ["help", "support", "assist"]
                ):
                    response += " 💫"
                elif "?" in response or any(
                    word in response.lower()
                    for word in ["interesting", "fascinating", "amazing"]
                ):
                    response += " 🌟"

        # Natural conversation flow adjustments
        if context.emotional_context.current_mood == ConversationMood.SAD:
            # Only add supportive language if not already present and if appropriate
            if not any(
                word in response.lower()
                for word in ["understand", "help", "support", "here"]
            ):
                if len(response) < 100:  # For shorter responses
                    response += " I'm here if you need to talk."

        # Remove any remaining artificial personality constraints
        # Let the AI respond naturally based on the conversation context

        return response

    def _get_fallback_response(self, message: str, user_id: int) -> str:
        """Generate fallback response when all providers fail"""
        fallback_responses = [
            "I'm having some technical issues at the moment, but I'm still here to help.",
            "Experiencing a brief connection issue, but let's keep the conversation going.",
            "Technical difficulties on my end, but I'm ready to continue our discussion.",
            "Having some system delays, but I'm available to chat.",
            "Brief technical hiccup, but I'm back and ready to help.",
        ]

        import random

        return random.choice(fallback_responses)

    def _calculate_engagement_delta(
        self, message: str, response: str, topics: List[str]
    ) -> float:
        """Calculate engagement score change"""
        delta = 0.0

        # Message quality factors
        if len(message) > 50:
            delta += 0.1
        if "?" in message:
            delta += 0.05
        if topics:
            delta += 0.1 * len(topics[:3])

        # Response quality factors
        if len(response) > 100:
            delta += 0.05
        if any(emoji in response for emoji in ["🚀", "✨", "🌌", "🌟"]):
            delta += 0.05

        return min(delta, 0.3)  # Cap at 0.3

    async def _save_conversation_async(
        self,
        context: ConversationContext,
        message: str,
        response: str,
        mood: ConversationMood,
        intensity: float,
        confidence: float,
        topics: List[str],
        engagement_delta: float,
        response_time: float,
    ):
        """Save conversation to database asynchronously"""
        try:

            def save_to_db():
                with sqlite3.connect(self.db_path) as conn:
                    # Save conversation
                    conn.execute(
                        """
                        INSERT INTO conversations 
                        (user_id, guild_id, channel_id, message_content, response_content,
                         mood, intensity, confidence, topics, engagement_score, 
                         response_time_ms, provider)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            context.user_id,
                            context.guild_id,
                            context.channel_id,
                            message,
                            response,
                            mood.value,
                            intensity,
                            confidence,
                            json.dumps(topics),
                            engagement_delta,
                            response_time,
                            (
                                self.active_provider.value
                                if self.active_provider
                                else "unknown"
                            ),
                        ),
                    )

                    # Update user profile
                    user_profile = self.user_profiles.get(context.user_id)
                    if user_profile:
                        conn.execute(
                            """
                            INSERT OR REPLACE INTO user_profiles
                            (user_id, display_name, total_interactions, preferred_topics,
                             communication_style, emotional_baseline, engagement_score,
                             interaction_frequency, conversation_success_rate, 
                             last_interaction, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                            (
                                user_profile.user_id,
                                user_profile.display_name,
                                user_profile.total_interactions,
                                json.dumps(user_profile.preferred_topics),
                                user_profile.communication_style,
                                user_profile.emotional_baseline,
                                user_profile.engagement_score,
                                user_profile.interaction_frequency,
                                user_profile.conversation_success_rate,
                                user_profile.last_interaction.isoformat(),
                                datetime.now(timezone.utc).isoformat(),
                            ),
                        )

                    conn.commit()

            # Run database operation in thread pool
            # Run database operation in thread pool
            await asyncio.get_event_loop().run_in_executor(self.thread_pool, save_to_db)

        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        cache_stats = self.cache.get_stats()

        return {
            "ai_performance": {
                "total_requests": self.performance_metrics["total_requests"],
                "successful_requests": self.performance_metrics["successful_requests"],
                "success_rate": (
                    self.performance_metrics["successful_requests"]
                    / max(1, self.performance_metrics["total_requests"])
                    * 100
                ),
                "avg_response_time_ms": self.performance_metrics["avg_response_time"],
                "active_provider": (
                    self.active_provider.value if self.active_provider else "none"
                ),
                "provider_usage": dict(self.performance_metrics["provider_usage"]),
            },
            "cache_performance": cache_stats,
            "conversation_stats": {
                "active_conversations": len(self.conversations),
                "total_users": len(self.user_profiles),
                "avg_engagement_score": (
                    sum(p.engagement_score for p in self.user_profiles.values())
                    / max(1, len(self.user_profiles))
                ),
            },
        }

    async def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old conversation data to maintain performance"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)

            def cleanup_db():
                with sqlite3.connect(self.db_path) as conn:
                    # Clean old conversations
                    conn.execute(
                        """
                        DELETE FROM conversations 
                        WHERE created_at < ?
                    """,
                        (cutoff_date.isoformat(),),
                    )

                    # Clean old performance metrics
                    conn.execute(
                        """
                        DELETE FROM performance_metrics 
                        WHERE timestamp < ?
                    """,
                        (cutoff_date.isoformat(),),
                    )

                    # Vacuum database to reclaim space
                    conn.execute("VACUUM")
                    conn.commit()

            await asyncio.get_event_loop().run_in_executor(self.thread_pool, cleanup_db)
            logger.info(f"Cleaned up data older than {days_to_keep} days")

        except Exception as e:
            logger.error(f"Data cleanup failed: {e}")

    async def generate_response(self, message: str, context: Dict[str, Any]) -> str:
        """
        Alternative interface for generating responses (backward compatibility)

        Args:
            message: The user's message
            context: Context dictionary containing user_id, channel_type, etc.

        Returns:
            AI response string
        """
        return await self.process_conversation(
            message=message,
            user_id=context.get("user_id", 0),
            guild_id=context.get("guild_id"),
            channel_id=context.get("channel_id"),
            context_data=context,
        )

    async def generate_image(
        self,
        prompt: str,
        context: Dict[str, Any],
        user_permissions: Dict[str, bool] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Generate an image using the advanced image generation handler

        Args:
            prompt: Description of the image to generate
            context: Context dictionary with user info, channel_id, etc.
            user_permissions: Dictionary with is_mod, is_admin flags

        Returns:
            Dictionary with image data or error information
        """
        try:
            # Use the advanced image generation handler directly
            if IMAGE_HANDLER_AVAILABLE:
                logger.info("🎨 Using advanced image generation handler")
                
                # Get the global image handler
                image_handler = get_image_handler()
                
                # Generate image using the handler
                result = await image_handler.generate_image(
                    prompt=prompt,
                    context=context,
                    user_permissions=user_permissions or {},
                    size="square_hd",
                    num_images=1
                )
                
                if result.get("success"):
                    logger.info(f"✅ Image generated successfully via handler")
                    return result
                else:
                    logger.warning(f"❌ Image generation failed via handler: {result.get('error')}")
                    # If handler fails, try fallback methods
            
            # Legacy fallback: Try the Freepik generator wrapper
            if self.freepik_generator and self.freepik_generator.is_available():
                logger.info("🔄 Falling back to legacy Freepik generator")
                
                user_id = context.get("user_id", 0)
                result = await self.freepik_generator.generate_image(prompt, user_id)

                if result.get("success"):
                    logger.info("✅ Image generated via legacy generator")
                    return result
                else:
                    logger.warning(f"❌ Legacy generator failed: {result.get('error')}")

            # Final fallback: Return comprehensive error
            logger.error("❌ All image generation methods failed")
            return {
                "success": False,
                "error": "No image generation providers available",
                "message": "Image generation is currently unavailable. Please try again later.",
                "details": {
                    "advanced_handler_available": IMAGE_HANDLER_AVAILABLE,
                    "legacy_generator_available": bool(self.freepik_generator),
                    "freepik_api_key_configured": bool(os.getenv("FREEPIK_API_KEY"))
                }
            }

        except Exception as e:
            logger.error(f"💥 Critical error in image generation: {e}")
            return {
                "success": False,
                "error": "Critical error",
                "message": f"An unexpected error occurred: {str(e)}",
            }

            # No image generation providers available
            return {
                "success": False,
                "error": "No image generation providers available",
                "message": "Image generation is currently unavailable. Please try again later.",
            }

        except Exception as e:
            logger.error(f"Error in generate_image: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "An error occurred while generating the image.",
            }

    async def _check_image_generation_permission(
        self, user_id: int, channel_id: int, user_permissions: Dict[str, bool]
    ) -> Dict[str, Any]:
        """Check if user has permission to generate images in this channel"""
        try:
            is_admin = user_permissions.get("is_admin", False)
            is_mod = user_permissions.get("is_mod", False)

            # Admins can use image generation anywhere
            if is_admin:
                return {"allowed": True, "reason": "admin_privilege"}

            # Mods can use image generation anywhere (but not admins)
            if is_mod:
                return {"allowed": True, "reason": "mod_privilege"}

            # Regular users can only use in the designated channel
            default_channel = self.image_config["default_channel_id"]
            if channel_id == default_channel:
                return {"allowed": True, "reason": "designated_channel"}
            else:
                return {
                    "allowed": False,
                    "message": f"Regular users can only generate images in <#{default_channel}>. Mods and admins can use this feature anywhere.",
                }

        except Exception as e:
            logger.error(f"Permission check error: {e}")
            return {
                "allowed": False,
                "message": "Permission check failed. Please try again.",
            }

    async def _check_image_rate_limit(
        self, user_id: int, user_permissions: Dict[str, bool]
    ) -> Dict[str, Any]:
        """Check if user has exceeded their image generation rate limit"""
        try:
            is_admin = user_permissions.get("is_admin", False)
            is_mod = user_permissions.get("is_mod", False)

            # Determine rate limit based on user role
            if is_admin:
                limit = self.image_config["rate_limit"]["admins"]
                role = "admin"
            elif is_mod:
                limit = self.image_config["rate_limit"]["mods"]
                role = "mod"
            else:
                limit = self.image_config["rate_limit"]["regular_users"]
                role = "user"

            # Check current usage from cache
            cache_key = f"image_rate_limit:{user_id}"
            current_usage = await self.cache.get(cache_key, 0)

            if current_usage >= limit:
                # Calculate reset time (1 hour from now)
                reset_time = datetime.now(timezone.utc) + timedelta(hours=1)
                return {
                    "allowed": False,
                    "message": f"Rate limit exceeded. {role.title()}s can generate {limit} images per hour. Try again in an hour.",
                    "reset_time": reset_time.isoformat(),
                    "current_usage": current_usage,
                    "limit": limit,
                }

            return {
                "allowed": True,
                "current_usage": current_usage,
                "limit": limit,
                "remaining": limit - current_usage,
            }

        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return {
                "allowed": True,  # Allow on error to avoid blocking users
                "message": "Rate limit check failed, proceeding with generation.",
            }

    async def _update_image_rate_limit(self, user_id: int):
        """Update user's image generation rate limit counter"""
        try:
            cache_key = f"image_rate_limit:{user_id}"
            current_usage = await self.cache.get(cache_key, 0)
            new_usage = current_usage + 1

            # Set with 1 hour TTL
            await self.cache.set(cache_key, new_usage, ttl=3600)

        except Exception as e:
            logger.error(f"Rate limit update error: {e}")

    async def _log_image_generation(
        self, user_id: int, channel_id: int, prompt: str, provider: str, success: bool
    ):
        """Log image generation attempt to database"""
        try:

            def log_to_db():
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        """
                        INSERT INTO image_generations 
                        (user_id, channel_id, prompt, provider, success, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            user_id,
                            channel_id,
                            prompt[:500],  # Truncate long prompts
                            provider,
                            success,
                            datetime.now(timezone.utc).isoformat(),
                        ),
                    )
                    conn.commit()

            # Run in thread pool to avoid blocking
            await asyncio.get_event_loop().run_in_executor(self.thread_pool, log_to_db)

        except Exception as e:
            logger.error(f"Image generation logging failed: {e}")

    async def get_health_status(self) -> Dict[str, Any]:
        """
        Get the health status of the AI engine and its providers

        Returns:
            Dictionary with status information
        """
        try:
            status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "available_providers": [],
                "active_provider": None,
                "cache_stats": self.cache.get_stats(),
                "performance_metrics": await self.get_performance_metrics(),
            }

            # Check each provider
            providers = ["universal", "openrouter", "openai"]

            for provider in providers:
                try:
                    # Check if provider has API key
                    provider_key = f"{provider}_api_key"
                    api_key = self.config.get(provider_key) or os.getenv(
                        f"{provider.upper()}_API_KEY"
                    )
                    if api_key:
                        status["available_providers"].append(provider)
                        if not status["active_provider"]:
                            status["active_provider"] = provider
                except Exception:
                    pass

            if not status["available_providers"]:
                status["status"] = "no_providers"
                status["message"] = "No AI providers configured"

            return status

        except Exception as e:
            self.logger.error(f"Error getting health status: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat(),
            }


# Global engine instance
_engine_instance: Optional[ConsolidatedAIEngine] = None


def initialize_engine(config: Dict[str, Any] = None) -> ConsolidatedAIEngine:
    """Initialize the global AI engine"""
    global _engine_instance
    _engine_instance = ConsolidatedAIEngine(config)
    return _engine_instance


def get_engine() -> Optional[ConsolidatedAIEngine]:
    """Get the global AI engine instance"""
    return _engine_instance


# Convenience functions for backward compatibility
async def process_conversation(message: str, user_id: int, **kwargs) -> str:
    """Process conversation using global engine"""
    engine = get_engine()
    if engine:
        return await engine.process_conversation(message, user_id, **kwargs)
    else:
        return "AI engine not initialized"


async def get_performance_metrics() -> Dict[str, Any]:
    """Get performance metrics from global engine"""
    engine = get_engine()
    if engine:
        return await engine.get_performance_metrics()
    else:
        return {"error": "AI engine not initialized"}
