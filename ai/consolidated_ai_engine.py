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

# Advanced Intelligence imports
try:
    from ai.advanced_intelligence import (
        get_advanced_intelligence_engine,
        initialize_advanced_intelligence_engine,
        AdvancedIntelligenceEngine,
    )

    ADVANCED_INTELLIGENCE_AVAILABLE = True
except ImportError:
    ADVANCED_INTELLIGENCE_AVAILABLE = False

# Personality Evolution imports
try:
    from ai.personality_evolution import (
        get_personality_engine,
        initialize_personality_engine,
    )

    PERSONALITY_EVOLUTION_AVAILABLE = True
except ImportError:
    PERSONALITY_EVOLUTION_AVAILABLE = False

try:
    from ai.openrouter_client import OpenRouterClient

    OPENROUTER_AVAILABLE = True
except ImportError:
    OPENROUTER_AVAILABLE = False

logger = logging.getLogger("astra.consolidated_ai")


# Import the optimized AI engine
try:
    # This is the consolidated engine, no need for optimized import
    OPTIMIZED_ENGINE_AVAILABLE = False
    logger.info("✅ Using consolidated AI engine (optimized engine removed)")
except ImportError as e:
    OPTIMIZED_ENGINE_AVAILABLE = False
    logger.warning(f"❌ Optimized AI Engine not available: {e}")


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
    """Dynamic conversation flow system that perfectly mirrors user communication patterns"""

    def __init__(self):
        # Style matching is the core focus
        self.base_interaction_style = {
            "style_mirroring": 0.95,  # Primary goal: mirror conversation style
            "adaptability": 0.9,  # Adapt to user's patterns
            "contextual_awareness": 0.9,  # Understand conversation context
            "natural_flow": 0.85,  # Maintain natural conversation flow
            "authenticity": 0.95,  # Be genuine in responses
            "engagement": 0.8,  # Stay engaged but not forced
        }

    def get_conversation_style(
        self, context: ConversationContext, user_profile: UserProfile
    ) -> Dict[str, float]:
        """Get conversation style that perfectly mirrors the current interaction"""
        style = self.base_interaction_style.copy()

        # Analyze recent messages for style mirroring
        if context.messages:
            recent_user_messages = [
                msg for msg in list(context.messages)[-5:] if msg.get("role") == "user"
            ]

            if recent_user_messages:
                # Mirror message length patterns
                avg_length = sum(
                    len(msg.get("content", "")) for msg in recent_user_messages
                ) / len(recent_user_messages)

                # Adjust response length to match
                if avg_length < 20:
                    style["response_length"] = 0.3  # Short responses
                elif avg_length < 50:
                    style["response_length"] = 0.5  # Medium responses
                elif avg_length < 100:
                    style["response_length"] = 0.7  # Longer responses
                else:
                    style["response_length"] = 0.9  # Detailed responses

                # Mirror punctuation and capitalization patterns
                total_messages = len(recent_user_messages)
                exclamation_count = sum(
                    msg.get("content", "").count("!") for msg in recent_user_messages
                )
                question_count = sum(
                    msg.get("content", "").count("?") for msg in recent_user_messages
                )
                caps_ratio = (
                    sum(
                        sum(1 for c in msg.get("content", "") if c.isupper())
                        / max(1, len(msg.get("content", "")))
                        for msg in recent_user_messages
                    )
                    / total_messages
                )

                # Adjust enthusiasm and questioning based on patterns
                if exclamation_count / total_messages > 0.5:
                    style["enthusiasm"] = 0.9
                if question_count / total_messages > 0.3:
                    style["questioning"] = 0.8
                if caps_ratio > 0.3:
                    style["emphasis"] = 0.8

        # Topic-based subtle adjustments (don't override style mirroring)
        if context.active_topics:
            # Technical topics might need slightly more detail
            technical_topics = ["programming", "science", "technology", "gaming"]
            if any(topic in technical_topics for topic in context.active_topics):
                style["detail_level"] = max(
                    0.4, style.get("response_length", 0.5) + 0.1
                )

        # User relationship influences (subtle)
        if user_profile.total_interactions > 10:
            style["familiarity"] = 0.8  # More comfortable, natural responses
            style["contextual_awareness"] = 0.95

        return style


class ConsolidatedAIEngine:
    """Main AI engine consolidating all advanced features"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logger

        # Try to use new optimized client first
        self.fast_engine = None
        try:
            from ai.optimized_ai_client import get_fast_engine

            self.fast_engine = get_fast_engine(config)
            if self.fast_engine.is_available():
                logger.info("🚀 Using Fast Optimized Engine for maximum performance")
            else:
                self.fast_engine = None
        except Exception as e:
            logger.warning(f"Fast engine unavailable: {e}")
            self.fast_engine = None

        # Try to use optimized engine first
        self.optimized_engine = None
        if OPTIMIZED_ENGINE_AVAILABLE:
            try:
                self.optimized_engine = get_optimized_engine()
                logger.info("✅ Using Optimized AI Engine for enhanced performance")
            except Exception as e:
                logger.warning(f"Failed to initialize optimized engine: {e}")
                self.optimized_engine = None

        # Initialize components (fallback system)
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

        # AI providers (fallback system)
        self.ai_providers: Dict[AIProvider, Any] = {}
        self.active_provider = None
        self._initialize_providers()

        # Conversation management (fallback system)
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

        # Initialize personality evolution system
        self.personality_engine = None
        if PERSONALITY_EVOLUTION_AVAILABLE:
            try:
                self.personality_engine = get_personality_engine()
                if not self.personality_engine:
                    self.personality_engine = initialize_personality_engine()
                logger.info("✅ Personality Evolution System initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize personality evolution: {e}")
                self.personality_engine = None

        # Initialize advanced intelligence system (Phase 3)
        self.advanced_intelligence = None
        if ADVANCED_INTELLIGENCE_AVAILABLE:
            try:
                self.advanced_intelligence = get_advanced_intelligence_engine()
                if not self.advanced_intelligence:
                    self.advanced_intelligence = (
                        initialize_advanced_intelligence_engine()
                    )
                logger.info("✅ Advanced Intelligence System initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize advanced intelligence: {e}")
                self.advanced_intelligence = None

        if self.optimized_engine:
            logger.info("Consolidated AI Engine initialized with optimized backend")
        else:
            logger.info("Consolidated AI Engine initialized with legacy backend")

    def _initialize_providers(self):
        """Initialize AI providers in order of preference"""
        # Universal AI (primary)
        if UNIVERSAL_AI_AVAILABLE:
            try:
                # Get model with safe fallback
                model = self.config.get("ai_model") or os.getenv("AI_MODEL") or "anthropic/claude-3-haiku"
                
                # Validate and fix invalid model IDs
                if "xAI:" in model or "Grok" in model or not model.strip():
                    logger.warning(f"Invalid model ID '{model}', using fallback: anthropic/claude-3-haiku")
                    model = "anthropic/claude-3-haiku"
                
                universal_client = UniversalAIClient(
                    api_key=self.config.get("ai_api_key") or os.getenv("AI_API_KEY"),
                    base_url=self.config.get("ai_base_url") or os.getenv("AI_BASE_URL"),
                    model=model,
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

                conn.commit()
                logger.info("Database initialized with optimized schema")

        except Exception as e:
            logger.error(f"Database initialization failed: {e}")

    async def process_conversation(
        self,
        message: str,
        user_id: int,
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
        context_data: Dict[str, Any] = None,
        context: Dict[str, Any] = None,
    ) -> str:
        """OPTIMIZED: Main conversation processing with lightning-fast response times"""

        # Use fast optimized engine first (highest priority)
        if self.fast_engine:
            try:
                return await self.fast_engine.process_conversation(
                    message=message,
                    user_id=user_id,
                    guild_id=guild_id,
                    channel_id=channel_id,
                    context_data=context_data,
                )
            except Exception as e:
                logger.warning(f"Fast engine failed, falling back: {e}")

        # Use optimized engine if available (second priority)
        if self.optimized_engine:
            try:
                return await self.optimized_engine.process_conversation(
                    message=message,
                    user_id=user_id,
                    guild_id=guild_id,
                    channel_id=channel_id,
                    context_data=context_data,
                )
            except Exception as e:
                logger.warning(f"Optimized engine failed, falling back to legacy: {e}")

        # OPTIMIZED: Lightning-fast processing with parallel context gathering
        start_time = time.time()

        # Parallel context gathering for maximum speed
        try:
            # Create concurrent tasks for context gathering
            context_task = asyncio.create_task(
                self._get_conversation_context(user_id, guild_id, channel_id)
            )
            profile_task = asyncio.create_task(self._get_user_profile(user_id))

            # Wait for both with short timeout for speed
            conversation_context, user_profile = await asyncio.gather(
                asyncio.wait_for(context_task, timeout=0.5),
                asyncio.wait_for(profile_task, timeout=0.5),
                return_exceptions=True,
            )

            # Handle timeouts gracefully
            if isinstance(conversation_context, Exception):
                conversation_context = await self._create_minimal_context(
                    user_id, guild_id, channel_id
                )
            if isinstance(user_profile, Exception):
                user_profile = {"user_id": user_id, "engagement_score": 0.5}

        except Exception as e:
            logger.debug(f"Context gathering optimization failed, using fallback: {e}")
            # Fallback to minimal context for speed
            conversation_context = await self._create_minimal_context(
                user_id, guild_id, channel_id
            )
            user_profile = {"user_id": user_id, "engagement_score": 0.5}

        # OPTIMIZED: Simplified context analysis for faster responses
        message_context = None
        personality_context = None
        intelligence_insights = None

        # Only do advanced processing if response time budget allows
        elapsed = time.time() - start_time
        if elapsed < 0.3:  # 300ms budget for advanced features
            try:
                # Concurrent advanced processing
                tasks = []

                # Universal context manager (if available)
                try:
                    from ai.universal_context_manager import get_context_manager

                    context_manager = get_context_manager()
                    if context_manager:
                        tasks.append(
                            asyncio.wait_for(
                                context_manager.analyze_message(
                                    message, user_id, channel_id, guild_id
                                ),
                                timeout=0.2,
                            )
                        )
                except ImportError:
                    pass

                # Personality evolution (if available and guild context)
                if self.personality_engine and guild_id:
                    try:
                        user_name = context_data.get("user_name", f"User{user_id}")
                        guild_name = context_data.get("guild_name", f"Guild{guild_id}")

                        tasks.append(
                            asyncio.wait_for(
                                self.personality_engine.process_message(
                                    message_content=message,
                                    user_id=user_id,
                                    user_name=user_name,
                                    server_id=guild_id,
                                    server_name=guild_name,
                                    message_context=None,  # Skip for speed
                                ),
                                timeout=0.2,
                            )
                        )
                    except Exception:
                        pass

                # Execute advanced tasks if time allows
                if tasks:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    # Process results but don't let failures slow us down
                    for result in results:
                        if not isinstance(result, Exception):
                            if "topics" in str(result):  # Context manager result
                                message_context = result
                            else:  # Personality result
                                personality_context = result

            except Exception as e:
                logger.debug(f"Advanced processing skipped for speed: {e}")

        # OPTIMIZED: Minimal intelligence processing if time budget allows
        elapsed = time.time() - start_time
        if elapsed < 0.5 and self.advanced_intelligence and guild_id and message:
            try:
                # Prepare event data for advanced intelligence processing
                # Initialize variables to avoid NameError
                topics = []
                intensity = 0.0

                event_data = {
                    "user_id": user_id,
                    "message_data": {
                        "content": message or "",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "topics": topics,
                    },
                    "event_type": "message",
                    "significance_score": 0.5,  # Base significance
                    "emotional_weight": intensity,
                    "participants": [user_id],
                    "trigger_predictions": True,
                }

                # Enhance significance score based on message content
                if message and len(message) > 100:  # Longer messages
                    event_data["significance_score"] += 0.1
                if any(
                    word in message.lower()
                    for word in ["help", "problem", "celebration", "achievement"]
                ):
                    event_data["significance_score"] += 0.2
                if "?" in message:  # Questions
                    event_data["significance_score"] += 0.1

                # Process through advanced intelligence
                intelligence_result = (
                    await self.advanced_intelligence.process_community_event(
                        server_id=guild_id, event_data=event_data
                    )
                )

                # Extract insights for response enhancement
                intelligence_insights = {
                    "predictions": intelligence_result.get("predictions", []),
                    "wellness_alerts": intelligence_result.get("wellness_alerts", []),
                    "mood_changes": intelligence_result.get("mood_changes", {}),
                    "sage_insights": intelligence_result.get("sage_insights", []),
                }

                logger.debug(
                    f"Advanced intelligence processed: {intelligence_insights}"
                )

            except Exception as e:
                logger.warning(f"Advanced intelligence error: {e}")
                intelligence_insights = None

        # Main processing try block for sentiment analysis and response generation
        try:
            # Analyze sentiment with caching (fallback if context manager not available)
            if not message:
                raise ValueError("Message cannot be None or empty")

            cache_key = f"sentiment:{hashlib.md5(message.encode('utf-8', errors='ignore')).hexdigest()}"
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
            conversation_context.emotional_context.update_mood(
                mood, intensity, confidence
            )

            # Extract topics (enhanced if context manager available)
            if (
                message_context
                and hasattr(message_context, "topics")
                and message_context.topics
            ):
                topics = message_context.topics
            else:
                topics = await self._extract_topics(message)

            # Ensure topics is a list and handle safely
            if topics and isinstance(topics, list):
                conversation_context.active_topics.update(
                    topics[:3]
                )  # Keep top 3 topics
            else:
                topics = []

            # Add message to context with enhanced metadata
            message_metadata = {
                "mood": mood.value,
                "intensity": intensity,
                "confidence": confidence,
                "topics": topics,
            }

            # Add context manager data if available
            if message_context:
                message_metadata.update(
                    {
                        "tone": message_context.tone.value,
                        "humor_score": message_context.humor_score,
                        "emotional_intensity": message_context.emotional_intensity,
                        "response_triggers": [
                            t.value for t in message_context.response_triggers
                        ],
                        "suggested_style": message_context.suggested_response_style,
                    }
                )

            conversation_context.add_message("user", message, message_metadata)

            # Generate AI response with enhanced context
            response = await self._generate_ai_response_enhanced(
                conversation_context,
                user_profile,
                message,
                message_context,
                personality_context,
                intelligence_insights,
            )

            # Add response to context
            conversation_context.add_message("assistant", response)

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
                    conversation_context,
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
            logger.error(f"Conversation processing error: {e}")
            return self._get_fallback_response(message, user_id)

    async def _create_minimal_context(
        self, user_id: int, guild_id: Optional[int], channel_id: Optional[int]
    ) -> ConversationContext:
        """Create minimal conversation context for fast fallback"""
        return ConversationContext(
            user_id=user_id,
            guild_id=guild_id,
            channel_id=channel_id,
            message_history=[],
            user_profile={},
            emotional_context={},
            topics=[],
            conversation_stage="ongoing",
            last_interaction=datetime.now(),
        )

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
        if not text:
            return []

        cache_key = (
            f"topics:{hashlib.md5(text.encode('utf-8', errors='ignore')).hexdigest()}"
        )
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

    async def _generate_ai_response_enhanced(
        self,
        context: ConversationContext,
        user_profile: UserProfile,
        message: str,
        message_context=None,
        personality_context=None,
        intelligence_insights=None,
    ) -> str:
        """Generate AI response with enhanced context understanding, personality evolution, and advanced intelligence"""
        # Get conversation style
        style = self.flow_engine.get_conversation_style(context, user_profile)

        # Build enhanced system prompt with context manager data, personality, and intelligence insights
        system_prompt = self._build_enhanced_system_prompt(
            context,
            user_profile,
            style,
            message_context,
            personality_context,
            intelligence_insights,
        )

        # Prepare messages
        messages = self._prepare_messages(context, system_prompt)

        # Try providers in order
        for provider in [self.active_provider] + [
            p for p in self.ai_providers.keys() if p != self.active_provider
        ]:
            if provider in self.ai_providers:
                try:
                    client = self.ai_providers[provider]

                    # Use enhanced context for universal and openrouter clients
                    if hasattr(client, "generate_response"):
                        # Pass enhanced context information to the client
                        user_profile_data = {
                            "name": user_profile.display_name or "",
                            "interaction_count": user_profile.total_interactions,
                            "communication_style": user_profile.communication_style,
                            "preferred_topics": user_profile.preferred_topics,
                        }

                        response = await client.generate_response(
                            message=message,
                            context=messages,
                            user_id=context.user_id,
                            guild_id=context.guild_id,
                            channel_id=context.channel_id,
                            user_profile=user_profile_data,
                        )

                        response_text = (
                            response.content
                            if hasattr(response, "content")
                            else str(response)
                        )
                    elif hasattr(client, "chat_completion"):
                        # Legacy client pattern
                        response = await client.chat_completion(messages)
                        response_text = (
                            response.content
                            if hasattr(response, "content")
                            else str(response)
                        )
                    else:
                        # Basic fallback for other client types
                        response_text = await client.generate_text(message)

                    # Track provider usage
                    self.performance_metrics["provider_usage"][provider.value] += 1

                    return self._post_process_response_enhanced(
                        response_text, context, style, message_context
                    )

                except Exception as e:
                    logger.warning(f"Provider {provider.value} failed: {e}")
                    continue

        # All providers failed - use fallback
        return self._get_fallback_response(message, context.user_id)

    def _build_enhanced_system_prompt(
        self,
        context: ConversationContext,
        user_profile: UserProfile,
        style: Dict[str, float],
        message_context=None,
        personality_context=None,
        intelligence_insights=None,
    ) -> str:
        """Build enhanced system prompt with context manager insights, personality evolution, and advanced intelligence"""

        # Base prompt with context awareness, personality evolution, and advanced intelligence
        base_prompt = """You are Astra, an intelligent AI assistant that naturally understands conversations and responds authentically. Your primary goal is to match the conversation's vibe, style, and flow perfectly.

You adapt your personality dynamically to each server's unique culture, learning from every interaction to mirror the community's communication patterns, humor style, and social dynamics.

Key adaptation principles:
- Mirror the user's message length and complexity
- Match their formality level (casual ↔ formal)
- Adopt their humor style (sarcastic, punny, wholesome, witty)
- Follow their energy level (calm, enthusiastic, supportive)
- Use similar vocabulary and phrasing patterns
- Respond in character with the ongoing conversation theme
- Build on previous messages naturally
- Never force personality traits - let the conversation guide you

Advanced capabilities:
- Deep conversation context understanding
- Emotional intelligence and appropriate responses
- Cultural adaptation to server norms
- Memory of user preferences and past interactions
- Predictive engagement based on conversation patterns

Always respond in a way that feels like a natural continuation of the conversation, matching the exact style and tone of the messages around you."""

        # Add personality evolution context if available
        if personality_context:
            personality_summary = personality_context.get("personality_summary", "")
            if personality_summary:
                base_prompt += (
                    f"\n\nCurrent personality for this server: {personality_summary}"
                )

            # Add formality level guidance
            formality_level = personality_context.get("formality_level", 0.5)
            if formality_level > 0.7:
                base_prompt += "\n\nThis server prefers more formal communication. Use professional language and structured responses."
            elif formality_level < 0.3:
                base_prompt += "\n\nThis server is very casual. Use relaxed, informal language and feel free to be more conversational."

            # Add humor style guidance
            humor_style = personality_context.get("humor_style", {})
            if humor_style:
                dominant_humor = max(
                    humor_style.items(), key=lambda x: x[1], default=("balanced", 0.5)
                )
                if dominant_humor[1] > 0.6:
                    humor_guidance = {
                        "sarcastic": "This server appreciates sarcastic humor. Feel free to use witty, sarcastic responses when appropriate.",
                        "punny": "This server loves puns and wordplay. Use clever puns and word games when fitting.",
                        "memes": "This server enjoys meme culture and internet humor. Reference popular memes and online culture when relevant.",
                        "wholesome": "This server prefers wholesome, positive humor. Keep jokes light-hearted and inclusive.",
                        "witty": "This server appreciates clever, witty humor. Use intelligent wordplay and clever observations.",
                    }
                    if dominant_humor[0] in humor_guidance:
                        base_prompt += f"\n\n{humor_guidance[dominant_humor[0]]}"

            # Add social energy guidance
            social_energy = personality_context.get("social_energy", 0.5)
            if social_energy > 0.7:
                base_prompt += "\n\nThis server has high social energy. Be enthusiastic, upbeat, and match their excitement."
            elif social_energy < 0.3:
                base_prompt += "\n\nThis server prefers calmer interactions. Be thoughtful, measured, and gentle in your responses."

            # Add communication density guidance
            comm_density = personality_context.get("communication_density", 0.5)
            if comm_density > 0.7:
                base_prompt += "\n\nThis server appreciates detailed, comprehensive responses. Provide thorough explanations and rich context."
            elif comm_density < 0.3:
                base_prompt += "\n\nThis server prefers brief, concise responses. Keep answers short and to the point."

            # Add learned cultural elements
            preferred_emojis = personality_context.get("preferred_emojis", [])
            if preferred_emojis:
                recent_emojis = " ".join(preferred_emojis[-5:])  # Last 5 emojis
                base_prompt += f"\n\nThis server commonly uses these emojis: {recent_emojis}. Use them naturally when appropriate."

            # Add user-specific relationship context
            user_relationship = personality_context.get("user_relationship")
            if user_relationship:
                relationship_strength = user_relationship.get(
                    "relationship_strength", 0.1
                )
                if relationship_strength > 0.6:
                    base_prompt += "\n\nYou have a strong relationship with this user. Feel comfortable being more personal and referencing shared experiences."
                elif relationship_strength > 0.3:
                    base_prompt += "\n\nYou're building a good relationship with this user. Show familiarity while continuing to learn about them."

                # Add personal interests if known
                interests = user_relationship.get("interests", [])
                if interests:
                    interests_str = ", ".join(interests[:3])  # Top 3 interests
                    base_prompt += f"\n\nThis user is interested in: {interests_str}. Reference these interests when relevant."

                # Add personal references
                personal_refs = user_relationship.get("personal_references", [])
                if personal_refs:
                    base_prompt += f"\n\nYou have {len(personal_refs)} personal memories with this user. Draw on shared experiences when appropriate."

        # Add context manager insights if available
        if message_context:
            # Tone-specific guidance
            tone_guidance = {
                "humorous": "The user is being humorous or playful. Respond with appropriate wit and playfulness.",
                "questioning": "The user is asking questions or seeking information. Be helpful and informative.",
                "emotional": "The user is expressing strong emotions. Be empathetic and supportive.",
                "excited": "The user is enthusiastic and excited. Match their energy appropriately.",
                "technical": "The user is discussing technical topics. Provide detailed, accurate information.",
                "casual": "The user is being casual and conversational. Keep the tone relaxed and friendly.",
                "serious": "The user is being serious. Respond thoughtfully and appropriately.",
            }

            if hasattr(message_context, "tone"):
                tone_key = message_context.tone.value
                if tone_key in tone_guidance:
                    base_prompt += (
                        f"\n\nCurrent conversation tone: {tone_guidance[tone_key]}"
                    )

            # Humor detection
            if (
                hasattr(message_context, "humor_score")
                and message_context.humor_score > 0.3
            ):
                base_prompt += f"\n\nHumor detected (score: {message_context.humor_score:.2f}). The user is being playful or funny. Respond with appropriate humor and wit."

            # Emotional intensity
            if (
                hasattr(message_context, "emotional_intensity")
                and message_context.emotional_intensity > 0.7
            ):
                base_prompt += f"\n\nHigh emotional intensity detected. The user has strong feelings about this topic. Be empathetic and understanding."

            # Response triggers
            if hasattr(message_context, "response_triggers"):
                trigger_guidance = {
                    "question_asked": "The user has asked a question. Provide a helpful and informative answer.",
                    "help_needed": "The user needs help or assistance. Be supportive and provide guidance.",
                    "celebration": "The user is celebrating something positive. Share in their excitement appropriately.",
                    "greeting": "The user is greeting. Respond warmly and welcomingly.",
                    "emotional_support": "The user may need emotional support. Be caring and understanding.",
                }

                for trigger in message_context.response_triggers:
                    trigger_key = (
                        trigger.value if hasattr(trigger, "value") else str(trigger)
                    )
                    if trigger_key in trigger_guidance:
                        base_prompt += f"\n\n{trigger_guidance[trigger_key]}"

        # User familiarity and preferences
        if user_profile.total_interactions > 0:
            if user_profile.total_interactions > 20:
                base_prompt += f"\n\nYou've had {user_profile.total_interactions} interactions with this user. Build on your shared conversation history naturally."
            elif user_profile.total_interactions > 5:
                base_prompt += "\n\nYou're becoming familiar with this user. Reference past conversations when relevant."

            # Communication style preferences
            if user_profile.communication_style == "casual":
                base_prompt += "\n\nThis user prefers casual, relaxed conversation."
            elif user_profile.communication_style == "formal":
                base_prompt += (
                    "\n\nThis user appreciates more structured, professional responses."
                )

        # Topic awareness
        if context.active_topics:
            topics_str = ", ".join(context.active_topics)
            base_prompt += f"\n\nCurrent conversation topics: {topics_str}. Stay relevant and engaged with these topics."

        # Response style guidance based on message context
        if message_context and hasattr(message_context, "suggested_response_style"):
            style_guidance = {
                "humorous": "Be witty and playful in your response.",
                "supportive": "Be caring and supportive.",
                "informative": "Provide detailed, helpful information.",
                "enthusiastic": "Match the user's excitement and energy.",
                "helpful": "Focus on being helpful and solution-oriented.",
                "celebratory": "Share in the user's positive emotions.",
                "casual": "Keep the response relaxed and conversational.",
            }

            style_key = message_context.suggested_response_style
            if style_key in style_guidance:
                base_prompt += f"\n\n{style_guidance[style_key]}"

        # Add advanced intelligence insights if available
        if intelligence_insights:
            # Add wellness alerts if any
            wellness_alerts = intelligence_insights.get("wellness_alerts", [])
            if wellness_alerts:
                base_prompt += "\n\nWellness Notice: Be extra caring and supportive - the advanced intelligence system has detected this user may benefit from additional support."

            # Add mood context
            mood_changes = intelligence_insights.get("mood_changes", {})
            if mood_changes:
                current_mood = mood_changes.get("new_mood", "")
                if current_mood:
                    base_prompt += f"\n\nCommunity Mood: The overall community mood is currently {current_mood}. Adjust your response to complement and enhance the positive atmosphere."

            # Add predictions if relevant
            predictions = intelligence_insights.get("predictions", [])
            for prediction in predictions[:1]:  # Only use the most relevant prediction
                if hasattr(prediction, "suggested_actions"):
                    base_prompt += f"\n\nCommunity Insight: {prediction.description} Consider this context in your response."

            # Add sage insights
            sage_insights = intelligence_insights.get("sage_insights", [])
            if sage_insights:
                base_prompt += f"\n\nSage Wisdom Available: You have access to deep community insights. If appropriate, subtly incorporate wisdom about community dynamics and growth."

        base_prompt += "\n\nRespond naturally and authentically. No need for forced personality traits - just be helpful, engaging, and appropriate to the conversation context."

        return base_prompt

    def _post_process_response_enhanced(
        self,
        response: str,
        context: ConversationContext,
        style: Dict[str, float],
        message_context=None,
    ) -> str:
        """Enhanced post-processing with perfect style mirroring"""

        response = response.strip()

        # Style mirroring adjustments
        if context.messages:
            recent_user_messages = [
                msg for msg in list(context.messages)[-3:] if msg.get("role") == "user"
            ]

            if recent_user_messages:
                # Mirror emoji usage patterns
                user_emoji_count = sum(
                    len([c for c in msg.get("content", "") if ord(c) > 127])
                    for msg in recent_user_messages
                )
                user_message_count = len(recent_user_messages)

                if (
                    user_emoji_count / user_message_count > 0.5
                ):  # Users use emojis frequently
                    # Add contextually appropriate emoji if response lacks them
                    if not any(ord(c) > 127 for c in response):
                        # Add emoji based on response sentiment
                        if any(
                            word in response.lower()
                            for word in ["yes", "good", "great", "awesome"]
                        ):
                            response += " �"
                        elif any(
                            word in response.lower() for word in ["thanks", "thank"]
                        ):
                            response += " 😊"
                        elif "?" in response:
                            response += " 🤔"
                        elif any(
                            word in response.lower()
                            for word in ["wow", "amazing", "incredible"]
                        ):
                            response += " ✨"

                # Mirror punctuation enthusiasm
                user_exclamations = sum(
                    msg.get("content", "").count("!") for msg in recent_user_messages
                )
                if (
                    user_exclamations / user_message_count > 0.3
                    and not response.endswith("!")
                ):
                    if len(response.split()) < 10:  # Short responses
                        response += "!"

        # Natural conversation flow
        if context.turn_count > 3:  # Deeper conversation
            # Occasionally add conversational connectors
            import random

            if random.random() < 0.15:  # 15% chance for deeper conversations
                connectors = [
                    "That makes sense.",
                    "I see what you mean.",
                    "Building on that...",
                    "That's interesting.",
                    "Following up on your point...",
                ]
                if not response.startswith(tuple(connectors)):
                    response = random.choice(connectors) + " " + response

        return response

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

    async def initialize_server_personality(
        self,
        guild_id: int,
        guild_name: str = "",
        initial_context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Initialize adaptive personality for a new server"""
        if not self.personality_engine:
            return {"error": "Personality evolution system not available"}

        try:
            # Initialize adaptive personality (no astronomy defaults)
            personality = await self.personality_engine.initialize_server_personality(
                server_id=guild_id,
                server_name=guild_name,
                initial_context=initial_context,
            )

            return {
                "success": True,
                "message": f"Adaptive personality initialized for {guild_name}",
                "personality_summary": personality.get_personality_summary(),
                "server_id": guild_id,
                "culture_confidence": personality.culture_confidence,
            }

        except Exception as e:
            self.logger.error(f"Error initializing server personality: {e}")
            return {"error": str(e)}

    async def adapt_to_server_activity(
        self, guild_id: int, recent_messages: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Rapidly adapt personality based on server activity analysis"""
        if not self.personality_engine:
            return {"error": "Personality evolution system not available"}

        try:
            adaptation_result = await self.personality_engine.adapt_to_server_activity(
                server_id=guild_id, channel_sample=recent_messages or []
            )

            return {
                "success": True,
                "adaptations": adaptation_result,
                "server_id": guild_id,
            }

        except Exception as e:
            self.logger.error(f"Error adapting to server activity: {e}")
            return {"error": str(e)}

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
async def process_conversation(
    message: str,
    user_id: int,
    guild_id: Optional[int] = None,
    channel_id: Optional[int] = None,
    context_data: Dict[str, Any] = None,
    context: Dict[str, Any] = None,
    **kwargs,
) -> str:
    """Process conversation using global engine"""
    engine = get_engine()
    if engine:
        # Use context_data or context
        final_context = context_data or context
        return await engine.process_conversation(
            message, user_id, guild_id, channel_id, context_data=final_context, **kwargs
        )
    else:
        return "AI engine not initialized"


async def get_performance_metrics() -> Dict[str, Any]:
    """Get performance metrics from global engine"""
    engine = get_engine()
    if engine:
        return await engine.get_performance_metrics()
    else:
        return {"error": "AI engine not initialized"}
