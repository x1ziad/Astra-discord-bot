"""
Universal AI Client for Astra Bot
Provides a unified interface for multiple AI providers with optimized performance and personality integration
"""

# 🔇 SUPPRESS: Google ALTS credentials warning for cleaner logs
import os

os.environ.setdefault("GRPC_PYTHON_LOG_LEVEL", "ERROR")
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS_JSON", "{}")

import asyncio
import logging
import aiohttp
import json
import time
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from functools import lru_cache

# Import error handler
try:
    from ai.error_handler import ai_error_handler, AIErrorType

    ERROR_HANDLER_AVAILABLE = True
except ImportError:
    ERROR_HANDLER_AVAILABLE = False
    logging.warning("AI Error Handler not available - fallback functionality limited")

# Import Google Gemini client
try:
    from ai.google_gemini_client import google_gemini_client

    GOOGLE_GEMINI_AVAILABLE = True
except ImportError:
    GOOGLE_GEMINI_AVAILABLE = False
    logging.warning("Google Gemini client not available")

# Import performance optimizer
try:
    from ai.response_optimizer import ai_response_optimizer

    PERFORMANCE_OPTIMIZER_AVAILABLE = True
    logging.info("🚀 AI Response Optimizer loaded - Maximum performance mode active")
except ImportError:
    PERFORMANCE_OPTIMIZER_AVAILABLE = False
    logging.warning("AI Response Optimizer not available - using standard performance")

# Import model mapping
try:
    from ai.model_mapping import normalize_model_id, get_model_display_name
except ImportError:
    # Fallback if model_mapping not available
    def normalize_model_id(model_id: str) -> str:
        """Fallback model normalization"""
        if not model_id:
            return "anthropic/claude-3-haiku"

        model_id = model_id.strip()

        # Handle the specific case that's causing issues
        if model_id == "xAI: Grok Code Fast 1":
            return "x-ai/grok-code-fast-1"

        # If it's already in API format, return as-is
        if "/" in model_id:
            return model_id

        return "anthropic/claude-3-haiku"  # Safe fallback

    def get_model_display_name(model_id: str) -> str:
        return model_id


logger = logging.getLogger("astra.universal_ai_client")


class AIProvider(Enum):
    """Supported AI providers"""

    OPENROUTER = "openrouter"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


@dataclass
class ConversationContext:
    """Enhanced conversation context with rich metadata"""

    user_id: int
    guild_id: Optional[int] = None
    channel_id: Optional[int] = None
    message_history: List[Dict[str, Any]] = None
    user_profile: Dict[str, Any] = None
    emotional_context: Dict[str, Any] = None
    topics: List[str] = None
    conversation_stage: str = "ongoing"  # greeting, ongoing, closing
    last_interaction: Optional[datetime] = None

    def __post_init__(self):
        if self.message_history is None:
            self.message_history = []
        if self.user_profile is None:
            self.user_profile = {}
        if self.emotional_context is None:
            self.emotional_context = {}
        if self.topics is None:
            self.topics = []


@dataclass
class AIResponse:
    """Standardized AI response format"""

    content: str
    model: str
    provider: str
    usage: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    context_used: Optional[ConversationContext] = None
    confidence_score: float = 0.0

    def __str__(self):
        return self.content


class UniversalAIClient:
    """Universal AI client supporting multiple providers"""

    def __init__(self, api_key: str = None, provider: str = "google", **kwargs):
        # Provider-specific API key resolution
        if not api_key:
            if provider == "google":
                self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv(
                    "GEMINI_API_KEY"
                )
            elif provider == "openai":
                self.api_key = os.getenv("OPENAI_API_KEY")
            elif provider == "openrouter":
                self.api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv(
                    "AI_API_KEY"
                )
            else:
                self.api_key = os.getenv("AI_API_KEY") or os.getenv(
                    "OPENROUTER_API_KEY"
                )
        else:
            self.api_key = api_key
        self.provider = AIProvider(provider) if isinstance(provider, str) else provider

        # Provider-specific configuration
        self.config = {
            AIProvider.OPENROUTER: {
                "base_url": "https://openrouter.ai/api/v1",
                "default_model": "anthropic/claude-3-haiku",
                "headers": {
                    "HTTP-Referer": "https://github.com/x1ziad/Astra-discord-bot",
                    "X-Title": "Astra Discord Bot",
                },
            },
            AIProvider.OPENAI: {
                "base_url": "https://api.openai.com/v1",
                "default_model": "gpt-4",
                "headers": {},
            },
            AIProvider.GOOGLE: {
                "base_url": "https://generativelanguage.googleapis.com/v1beta",
                "default_model": "models/gemini-2.5-flash",
                "headers": {},
            },
        }

        # Default parameters
        self.max_tokens = kwargs.get("max_tokens", 2000)
        self.temperature = kwargs.get("temperature", 0.7)
        raw_model = kwargs.get("model", self.config[self.provider]["default_model"])

        # Normalize model ID using mapping system
        self.model = normalize_model_id(raw_model)

        # Log model conversion if it was changed
        if raw_model != self.model:
            logger.info(f"Converted model ID '{raw_model}' to '{self.model}'")

        logger.info(f"Using model: {self.model}")

        # Enhanced context settings
        self.max_context_messages = kwargs.get(
            "max_context_messages", 8
        )  # Reduced for performance
        self.context_window_tokens = kwargs.get("context_window_tokens", 4000)
        self.enable_emotional_intelligence = kwargs.get(
            "enable_emotional_intelligence", True
        )
        self.enable_topic_tracking = kwargs.get("enable_topic_tracking", True)
        self.enable_memory_system = kwargs.get("enable_memory_system", True)

        # Memory for conversation contexts
        self.conversation_contexts: Dict[str, ConversationContext] = {}

        # Long-term memory system
        self.user_memories: Dict[int, Dict[str, Any]] = {}
        self.important_facts: Dict[str, List[Dict[str, Any]]] = {}

        # Last performance log time for periodic reporting
        self._last_performance_log = time.time()

        # PERFORMANCE OPTIMIZATION: Enhanced caching and performance features
        self._response_cache = {}
        self._performance_stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "timeout_fallbacks": 0,
            "ultra_fast_patterns": 0,
            "ai_responses": 0,
        }
        self._personality_cache = {}
        self._performance_mode = kwargs.get(
            "performance_mode", "balanced"
        )  # 'speed', 'balanced', 'quality'
        self._cache_enabled = kwargs.get("cache_enabled", True)
        self._max_cache_size = kwargs.get("max_cache_size", 1000)
        self._astra_personality_optimized = True

        # HTTP session
        self.session = None

        # Initialize logger
        self.logger = logging.getLogger("astra.universal_ai_client")

    def is_available(self) -> bool:
        """Check if the client is properly configured"""
        return bool(self.api_key) and self.provider in self.config

    def _generate_cache_key(
        self,
        message: str,
        user_id: Optional[int] = None,
        guild_id: Optional[int] = None,
    ) -> str:
        """Generate cache key for response caching"""
        import hashlib

        key_data = f"{message}:{user_id}:{guild_id}:{self._performance_mode}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _cleanup_cache(self) -> None:
        """🚀 ULTRA-FAST: Clean up old cache entries for maximum performance"""
        if not self._cache_enabled or len(self._response_cache) <= self._max_cache_size:
            return

        current_time = time.time()
        # Remove entries older than 5 minutes or if cache is too large
        expired_keys = [
            key
            for key, data in self._response_cache.items()
            if (current_time - data["timestamp"]) > 300  # 5 minutes
        ]

        for key in expired_keys:
            del self._response_cache[key]

        # If still too large, remove oldest entries
        if len(self._response_cache) > self._max_cache_size:
            sorted_items = sorted(
                self._response_cache.items(), key=lambda x: x[1]["timestamp"]
            )
            # Keep only the newest entries
            keep_items = sorted_items[-self._max_cache_size :]
            self._response_cache = dict(keep_items)

    def configure_personality(self, personality_config: Dict[str, Any]) -> None:
        """Configure AI personality for bot alignment"""
        self._personality_config = personality_config
        self._astra_personality_optimized = (
            personality_config.get("primary_personality") == "astra"
        )

        # Cache personality prompts for performance
        if self._cache_enabled:
            self._personality_cache.update(personality_config)

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        total_requests = self._performance_stats["total_requests"]
        if total_requests == 0:
            return self._performance_stats

        return {
            **self._performance_stats,
            "cache_hit_rate": (self._performance_stats["cache_hits"] / total_requests)
            * 100,
            "timeout_rate": (
                self._performance_stats["timeout_fallbacks"] / total_requests
            )
            * 100,
            "ultra_fast_rate": (
                self._performance_stats["ultra_fast_patterns"] / total_requests
            )
            * 100,
            "ai_response_rate": (
                self._performance_stats["ai_responses"] / total_requests
            )
            * 100,
        }

    def log_performance_stats_if_needed(self):
        """Log performance stats every 100 requests or 5 minutes"""
        current_time = time.time()
        total_requests = self._performance_stats["total_requests"]

        # Log every 100 requests or every 5 minutes
        if (total_requests % 100 == 0 and total_requests > 0) or (
            current_time - self._last_performance_log > 300
        ):
            stats = self.get_performance_stats()
            logger.info(
                f"🔥 AI Performance Stats: {total_requests} requests | "
                f"Cache: {stats['cache_hit_rate']:.1f}% | "
                f"Timeouts: {stats['timeout_rate']:.1f}% | "
                f"Ultra-fast: {stats['ultra_fast_rate']:.1f}% | "
                f"AI calls: {stats['ai_response_rate']:.1f}%"
            )
            self._last_performance_log = current_time

    def enable_caching(self, max_cache_size: int = 1000) -> None:
        """Enable response caching for performance"""
        self._cache_enabled = True
        self._max_cache_size = max_cache_size

    def set_performance_mode(self, mode: str) -> None:
        """Set performance mode: 'speed', 'balanced', 'quality'"""
        if mode in ["speed", "balanced", "quality"]:
            self._performance_mode = mode
            if mode == "speed":
                self.max_context_messages = 5  # Reduced context for speed
                self.context_window_tokens = 2000
            elif mode == "quality":
                self.max_context_messages = 15  # More context for quality
                self.context_window_tokens = 8000

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def _ensure_session(self):
        """Ensure HTTP session is available"""
        if not self.session:
            self.session = aiohttp.ClientSession()

    def _extract_important_facts(
        self, message: str, response: str, user_id: int
    ) -> List[Dict[str, Any]]:
        """Extract important facts from conversation for long-term memory"""
        facts = []
        message_lower = message.lower()

        # Personal information indicators
        personal_patterns = {
            "name": ["my name is", "i'm", "call me", "i am"],
            "location": ["i live in", "i'm from", "from", "located in"],
            "occupation": ["i work as", "my job", "i'm a", "work at"],
            "age": ["i'm", "years old", "my age"],
            "interests": ["i like", "i love", "i enjoy", "i'm into", "favorite"],
            "relationship": [
                "my",
                "girlfriend",
                "boyfriend",
                "wife",
                "husband",
                "partner",
            ],
            "achievement": ["i just", "i won", "i got", "i achieved", "i completed"],
            "problem": [
                "i'm having trouble",
                "i need help",
                "i'm struggling",
                "issue with",
            ],
            "goal": ["i want to", "i'm trying to", "my goal", "i plan to"],
        }

        current_time = datetime.now()

        for fact_type, patterns in personal_patterns.items():
            for pattern in patterns:
                if pattern in message_lower:
                    # Extract the relevant part of the message
                    start_idx = message_lower.find(pattern)
                    if start_idx != -1:
                        # Get the sentence containing this pattern
                        sentences = message.split(".")
                        for sentence in sentences:
                            if pattern in sentence.lower():
                                facts.append(
                                    {
                                        "type": fact_type,
                                        "content": sentence.strip(),
                                        "timestamp": current_time.isoformat(),
                                        "context": (
                                            message[:100] + "..."
                                            if len(message) > 100
                                            else message
                                        ),
                                        "confidence": (
                                            0.8
                                            if fact_type in ["name", "location"]
                                            else 0.6
                                        ),
                                    }
                                )
                                break

        # Extract mentioned preferences and dislikes
        if "hate" in message_lower or "don't like" in message_lower:
            facts.append(
                {
                    "type": "dislike",
                    "content": message,
                    "timestamp": current_time.isoformat(),
                    "confidence": 0.7,
                }
            )

        return facts

    def _update_user_memory(self, user_id: int, facts: List[Dict[str, Any]]):
        """Update long-term memory for a user"""
        if not self.enable_memory_system:
            return

        if user_id not in self.user_memories:
            self.user_memories[user_id] = {
                "facts": [],
                "preferences": {},
                "important_dates": [],
                "communication_patterns": {},
                "last_updated": datetime.now().isoformat(),
            }

        user_memory = self.user_memories[user_id]

        for fact in facts:
            # Avoid duplicates
            existing_facts = [f["content"] for f in user_memory["facts"]]
            if fact["content"] not in existing_facts:
                user_memory["facts"].append(fact)

        # Keep only recent and high-confidence facts
        user_memory["facts"] = sorted(
            user_memory["facts"],
            key=lambda x: (x["confidence"], x["timestamp"]),
            reverse=True,
        )[
            :50
        ]  # Keep top 50 facts

        user_memory["last_updated"] = datetime.now().isoformat()

    def _get_relevant_memories(
        self, user_id: int, current_message: str
    ) -> List[Dict[str, Any]]:
        """Get relevant memories for the current conversation"""
        if not self.enable_memory_system or user_id not in self.user_memories:
            return []

        user_memory = self.user_memories[user_id]
        relevant_facts = []

        # Get recent high-confidence facts
        for fact in user_memory["facts"][:10]:  # Top 10 facts
            if fact["confidence"] > 0.6:
                relevant_facts.append(fact)

        # Find contextually relevant facts
        message_words = set(current_message.lower().split())
        for fact in user_memory["facts"]:
            fact_words = set(fact["content"].lower().split())
            if len(message_words.intersection(fact_words)) > 1:  # Shared words
                if fact not in relevant_facts:
                    relevant_facts.append(fact)

        return relevant_facts[:5]  # Return top 5 relevant facts

    def _get_context_key(
        self,
        user_id: int,
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
    ) -> str:
        """Generate a unique key for conversation context"""
        if guild_id and channel_id:
            return f"{guild_id}:{channel_id}:{user_id}"
        elif guild_id:
            return f"{guild_id}:{user_id}"
        else:
            return f"dm:{user_id}"

    def _get_or_create_context(
        self,
        user_id: int,
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
    ) -> ConversationContext:
        """Get or create conversation context for a user"""
        context_key = self._get_context_key(user_id, guild_id, channel_id)

        if context_key not in self.conversation_contexts:
            self.conversation_contexts[context_key] = ConversationContext(
                user_id=user_id,
                guild_id=guild_id,
                channel_id=channel_id,
                last_interaction=datetime.now(),
            )

        return self.conversation_contexts[context_key]

    async def load_conversation_context_from_db(
        self,
        user_id: int,
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
        db_connection=None,
    ) -> Optional[ConversationContext]:
        """Load conversation context from database storage"""
        try:
            if not db_connection:
                # Try to import the database connection if available
                try:
                    from utils.database import db

                    db_connection = db
                except ImportError:
                    logger.warning(
                        "Database connection not available for context loading"
                    )
                    return None

            # Load from database using the same key format as the main bot
            context_db_key = (
                f"message_context_{guild_id if guild_id else 'dm'}_{channel_id}"
            )
            db_context = await db_connection.get(
                "conversation_contexts", context_db_key, {}
            )

            if not db_context or not db_context.get("messages"):
                return None

            # Convert database context to ConversationContext
            recent_messages = db_context.get("messages", [])[-20:]  # Last 20 messages

            # Build message history in the format expected by AI
            message_history = []
            for msg in recent_messages:
                role = "assistant" if msg.get("user_id") == "bot" else "user"
                message_history.append(
                    {
                        "role": role,
                        "content": msg.get("content", ""),
                        "timestamp": msg.get("timestamp", ""),
                    }
                )

            # Create conversation context
            context = ConversationContext(
                user_id=user_id,
                guild_id=guild_id,
                channel_id=channel_id,
                message_history=message_history,
                last_interaction=datetime.fromisoformat(
                    db_context.get("last_activity", datetime.now().isoformat())
                ),
            )

            # Extract topics from recent messages
            if self.enable_topic_tracking:
                all_content = " ".join(
                    [msg.get("content", "") for msg in recent_messages]
                )
                context.topics = self._extract_topics(all_content)

            # Store in memory cache
            context_key = self._get_context_key(user_id, guild_id, channel_id)
            self.conversation_contexts[context_key] = context

            return context

        except Exception as e:
            logger.error(f"Error loading conversation context from database: {e}")
            return None

    async def save_conversation_context_to_db(
        self, context: ConversationContext, db_connection=None
    ):
        """Save conversation context to database storage"""
        try:
            if not db_connection:
                try:
                    from utils.database import db

                    db_connection = db
                except ImportError:
                    logger.warning(
                        "Database connection not available for context saving"
                    )
                    return

            # Convert ConversationContext to database format
            context_db_key = f"message_context_{context.guild_id if context.guild_id else 'dm'}_{context.channel_id}"

            # Get existing context or create new
            existing_context = await db_connection.get(
                "conversation_contexts", context_db_key, {"messages": []}
            )

            # Add recent interactions to database format
            for msg in context.message_history[-5:]:  # Last 5 messages for performance
                db_message = {
                    "user_id": context.user_id if msg.get("role") == "user" else "bot",
                    "username": "Bot" if msg.get("role") == "assistant" else "User",
                    "content": msg.get("content", ""),
                    "timestamp": msg.get("timestamp", datetime.now().isoformat()),
                    "channel_id": context.channel_id,
                    "guild_id": context.guild_id,
                }

                # Check if message already exists (avoid duplicates)
                if not any(
                    existing_msg.get("content") == db_message["content"]
                    and existing_msg.get("timestamp") == db_message["timestamp"]
                    for existing_msg in existing_context["messages"]
                ):
                    existing_context["messages"].append(db_message)

            # Update metadata
            existing_context.update(
                {
                    "last_activity": (
                        context.last_interaction.isoformat()
                        if context.last_interaction
                        else datetime.now().isoformat()
                    ),
                    "channel_id": context.channel_id,
                    "guild_id": context.guild_id,
                    "topics": context.topics if context.topics else [],
                    "conversation_stage": context.conversation_stage,
                }
            )

            # Keep only recent messages
            if len(existing_context["messages"]) > 50:
                existing_context["messages"] = existing_context["messages"][-50:]

            # Save to database
            await db_connection.set(
                "conversation_contexts", context_db_key, existing_context
            )

        except Exception as e:
            logger.error(f"Error saving conversation context to database: {e}")

    async def store_conversation_context_to_db(self, conversation_context: list):
        """Store conversation context from list format to database"""
        try:
            # Extract context info from the conversation list
            if not conversation_context:
                return

            # Get database connection
            try:
                from utils.database import db

                db_connection = db
            except ImportError:
                logger.warning("Database connection not available for context storing")
                return

            # Extract identifiers from context (look for user info in messages)
            guild_id = None
            channel_id = None
            user_id = None

            # Try to extract IDs from message metadata if available
            for msg in conversation_context:
                if isinstance(msg, dict):
                    if "guild_id" in msg:
                        guild_id = msg["guild_id"]
                    if "channel_id" in msg:
                        channel_id = msg["channel_id"]
                    if "user_id" in msg:
                        user_id = msg["user_id"]

            # Create database key
            context_db_key = (
                f"conversation_context_{guild_id or 'dm'}_{channel_id or 'unknown'}"
            )

            # Get existing context or create new
            existing_context = await db_connection.get(
                "conversation_contexts", context_db_key, {"messages": []}
            )

            # Add conversation messages to database format
            for msg in conversation_context[-10:]:  # Last 10 messages for performance
                if isinstance(msg, dict) and "content" in msg:
                    db_message = {
                        "user_id": user_id if msg.get("role") == "user" else "bot",
                        "username": "User" if msg.get("role") == "user" else "Bot",
                        "content": msg.get("content", ""),
                        "timestamp": msg.get("timestamp", datetime.now().isoformat()),
                        "channel_id": channel_id,
                        "guild_id": guild_id,
                        "role": msg.get("role", "unknown"),
                    }

                    # Check if message already exists (avoid duplicates)
                    if not any(
                        existing_msg.get("content") == db_message["content"]
                        and existing_msg.get("timestamp") == db_message["timestamp"]
                        for existing_msg in existing_context["messages"]
                    ):
                        existing_context["messages"].append(db_message)

            # Update metadata
            existing_context.update(
                {
                    "last_activity": datetime.now().isoformat(),
                    "channel_id": channel_id,
                    "guild_id": guild_id,
                    "message_count": len(existing_context["messages"]),
                }
            )

            # Keep only recent messages
            if len(existing_context["messages"]) > 50:
                existing_context["messages"] = existing_context["messages"][-50:]

            # Save to database
            await db_connection.set(
                "conversation_contexts", context_db_key, existing_context
            )

            logger.debug(f"Stored conversation context to database: {context_db_key}")

        except Exception as e:
            logger.error(f"Error storing conversation context to database: {e}")

    def _analyze_emotional_context(self, message: str) -> Dict[str, Any]:
        """🚀 ULTRA-FAST: Simple emotional context analysis for maximum performance"""
        # Simplified for maximum performance - just return neutral analysis
        emotional_indicators = {
            "excited": {
                "keywords": [
                    "!",
                    "wow",
                    "amazing",
                    "awesome",
                    "excited",
                    "can't wait",
                    "yay",
                    "woohoo",
                    "fantastic",
                    "incredible",
                ],
                "patterns": ["!!!+", "WOW", "AMAZING", "SO GOOD", "LOVE IT"],
                "weight": 1.2,
            },
            "happy": {
                "keywords": [
                    "happy",
                    "glad",
                    "pleased",
                    "good",
                    "great",
                    "wonderful",
                    "nice",
                    "perfect",
                    "excellent",
                    "brilliant",
                ],
                "patterns": [":)", ":D", "😊", "😄", "🙂", "❤️", "💖"],
                "weight": 1.0,
            },
            "sad": {
                "keywords": [
                    "sad",
                    "down",
                    "depressed",
                    "unhappy",
                    "disappointed",
                    "upset",
                    "crying",
                    "tears",
                    "heartbroken",
                ],
                "patterns": [":(", "😢", "😭", "💔", "😞"],
                "weight": 1.3,
            },
            "angry": {
                "keywords": [
                    "angry",
                    "mad",
                    "frustrated",
                    "annoyed",
                    "upset",
                    "furious",
                    "pissed",
                    "irritated",
                    "rage",
                ],
                "patterns": [">:(", "😡", "😠", "🤬"],
                "weight": 1.5,
            },
            "confused": {
                "keywords": [
                    "confused",
                    "don't understand",
                    "unclear",
                    "help",
                    "lost",
                    "puzzled",
                    "what",
                    "how",
                    "why",
                ],
                "patterns": ["???", "??", "🤔", "😕"],
                "weight": 0.8,
            },
            "anxious": {
                "keywords": [
                    "worried",
                    "nervous",
                    "anxious",
                    "stressed",
                    "concerned",
                    "afraid",
                    "scared",
                    "panic",
                ],
                "patterns": ["😰", "😨", "😟", "😖"],
                "weight": 1.4,
            },
            "grateful": {
                "keywords": [
                    "thanks",
                    "thank you",
                    "grateful",
                    "appreciate",
                    "thankful",
                    "blessed",
                ],
                "patterns": ["🙏", "😊", "❤️"],
                "weight": 1.1,
            },
            "frustrated": {
                "keywords": [
                    "ugh",
                    "argh",
                    "sigh",
                    "frustrated",
                    "tired",
                    "exhausted",
                    "done",
                    "fed up",
                ],
                "patterns": ["😤", "😑", "🙄"],
                "weight": 1.2,
            },
        }

        message_lower = message.lower()
        detected_emotions = {}

        # Analyze keywords and patterns
        for emotion, data in emotional_indicators.items():
            score = 0

            # Check keywords
            for keyword in data["keywords"]:
                if keyword in message_lower:
                    score += 1

            # Check patterns (emojis, punctuation)
            for pattern in data["patterns"]:
                if pattern.lower() in message_lower:
                    score += 1.5  # Patterns have higher weight

            # Apply emotion weight
            if score > 0:
                detected_emotions[emotion] = score * data["weight"]

        # Determine dominant emotion and intensity
        dominant_emotion = "neutral"
        emotional_intensity = 0.0

        if detected_emotions:
            dominant_emotion = max(detected_emotions, key=detected_emotions.get)
            # Calculate intensity based on total emotional indicators
            total_score = sum(detected_emotions.values())
            emotional_intensity = min(total_score * 0.2, 1.0)

        # Additional context analysis
        message_length = len(message.split())
        caps_ratio = sum(1 for c in message if c.isupper()) / max(len(message), 1)

        # Adjust intensity based on message characteristics
        if caps_ratio > 0.3:  # Lots of caps = higher intensity
            emotional_intensity = min(emotional_intensity * 1.3, 1.0)

        if message_length > 50:  # Long messages often indicate higher investment
            emotional_intensity = min(emotional_intensity * 1.1, 1.0)

        # Detect conversation stage indicators
        conversation_stage = "ongoing"
        greeting_words = [
            "hello",
            "hi",
            "hey",
            "good morning",
            "good afternoon",
            "good evening",
            "greetings",
        ]
        farewell_words = [
            "goodbye",
            "bye",
            "see you",
            "talk later",
            "gotta go",
            "farewell",
        ]

        if any(word in message_lower for word in greeting_words):
            conversation_stage = "greeting"
        elif any(word in message_lower for word in farewell_words):
            conversation_stage = "farewell"

        return {
            "dominant_emotion": "neutral",
            "emotional_intensity": 0.5,
            "conversation_stage": "ongoing",
        }

    def _detect_urgency(self, message_lower: str) -> Dict[str, Any]:
        """🚀 ULTRA-FAST: Simple urgency detection for maximum performance"""
        return {
            "urgency_score": 0.5,
            "has_questions": "?" in message_lower,
            "expects_quick_response": True,
        }

    def _extract_topics(self, message: str) -> List[str]:
        """🚀 ULTRA-FAST: Simple topic extraction for maximum performance"""
        return []  # Return empty list for maximum performance

    def _get_ultra_fast_fallback_response(
        self, message: str, conversation_context: Optional[object] = None
    ) -> "AIResponse":
        """🚀 ULTRA-FAST FALLBACK: Generate immediate response when AI providers are slow/unavailable"""
        # Pattern-based instant responses for maximum speed
        message_lower = message.lower().strip()

        # Enhanced ultra-fast pattern matching with more responses
        instant_responses = {
            "hello": "Hello! How can I help you today?",
            "hi": "Hi there! What can I do for you?",
            "hey": "Hey! How's it going?",
            "thanks": "You're welcome! Happy to help!",
            "thank you": "My pleasure! Anything else I can do?",
            "how are you": "I'm doing great! Thanks for asking. How are you?",
            "what are you": "I'm Astra, your AI companion! How can I help?",
            "help": "I'm here to help! What do you need assistance with?",
            "ping": "Pong! ⚡ Ultra-fast response active.",
            "good morning": "Good morning! Hope you're having a great day!",
            "good afternoon": "Good afternoon! How's your day going?",
            "good evening": "Good evening! How can I assist you tonight?",
            "goodbye": "Goodbye! Have a wonderful day!",
            "bye": "See you later! Take care!",
            "ok": "Got it! Anything else I can help with?",
            "okay": "Perfect! What else would you like to know?",
            "cool": "Awesome! What else is on your mind?",
            "nice": "Thanks! Is there anything else you'd like to explore?",
        }

        # Check for exact matches first (fastest)
        if message_lower in instant_responses:
            response_content = instant_responses[message_lower]
        else:
            # Quick substring matching for common phrases
            for pattern, response in instant_responses.items():
                if pattern in message_lower:
                    response_content = response
                    break
            else:
                # Generic ultra-fast response
                response_content = "I'm processing your message as quickly as possible! How can I help you today?"

        # Create AIResponse object
        return AIResponse(
            content=response_content,
            model="astra-ultra-fast-fallback",
            provider="internal",
            usage={"tokens": 0, "cost": 0.0},
            metadata={"type": "ultra_fast_fallback", "response_time": "<10ms"},
            created_at=datetime.now(timezone.utc),
            context_used=conversation_context,
            confidence_score=0.8,  # High confidence for pattern matches
        )

    def _build_enhanced_context_messages(
        self, context: ConversationContext, current_message: str
    ) -> List[Dict[str, str]]:
        """Build enhanced context messages with conversation history and analysis"""
        messages = []

        # Add system message with rich context
        system_prompt = self._build_enhanced_system_prompt(context, current_message)
        messages.append({"role": "system", "content": system_prompt})

        # Add recent conversation history (sliding window)
        recent_messages = context.message_history[-self.max_context_messages :]
        for msg in recent_messages:
            messages.append(
                {"role": msg.get("role", "user"), "content": msg.get("content", "")}
            )

        return messages

    def _build_enhanced_system_prompt(
        self, context: ConversationContext, current_message: str
    ) -> str:
        """Build a system prompt - concise or detailed based on config"""
        from config.unified_config import unified_config

        # Check if concise prompts are enabled (default: True for performance)
        use_concise = unified_config.get_setting("use_concise_prompts", True)

        if use_concise:
            return self._build_concise_prompt(context, current_message)
        else:
            return self._build_detailed_prompt(context, current_message)

    def _build_concise_prompt(
        self, context: ConversationContext, current_message: str
    ) -> str:
        """Build a concise system prompt for faster responses"""
        base_prompt = "You are Astra, a helpful AI assistant for Discord. Be natural, engaging, and context-aware."

        prompt_parts = [base_prompt]

        # Add key user context only
        if context.user_profile:
            name = context.user_profile.get("name", "")
            if name:
                prompt_parts.append(f"User: {name}")

            # Simplified relationship level
            count = context.user_profile.get("interaction_count", 0)
            if count > 10:
                prompt_parts.append("Familiar user - be friendly")
            elif count > 3:
                prompt_parts.append("Getting to know them")

        # Essential emotional context only
        if context.emotional_context:
            emotion = context.emotional_context.get("dominant_emotion", "neutral")
            if emotion in ["sad", "angry", "anxious"]:
                prompt_parts.append(f"User seems {emotion} - be supportive")
            elif emotion in ["excited", "happy"]:
                prompt_parts.append(f"User is {emotion} - match their energy")

        # Recent topics (max 2)
        if context.topics:
            recent = context.topics[-2:]
            if recent:
                prompt_parts.append(f"Topics: {', '.join(recent)}")

        # Simple guidelines
        prompt_parts.append("Be helpful, natural, and conversational.")

        return " | ".join(prompt_parts)

    def _build_detailed_prompt(
        self, context: ConversationContext, current_message: str
    ) -> str:
        """Build a detailed system prompt (original version for when detail is needed)"""
        prompt_parts = [
            "You are Astra, an advanced AI assistant for a Discord community. You are helpful, engaging, and highly context-aware.",
            "You possess emotional intelligence and adapt your responses based on the user's emotional state, conversation history, and communication patterns.",
        ]

        # Add memory-based user context
        if context.user_id and self.enable_memory_system:
            relevant_memories = self._get_relevant_memories(
                context.user_id, current_message
            )
            if relevant_memories:
                prompt_parts.append("\nWhat you remember about this user:")
                for memory in relevant_memories[:2]:  # Top 2 most relevant
                    if memory["type"] in ["name", "occupation", "interests"]:
                        prompt_parts.append(f"- {memory['content']}")

        # Add user context
        if context.user_profile:
            name = context.user_profile.get("name", "")
            if name:
                prompt_parts.append(f"You're talking with {name}.")

            interaction_count = context.user_profile.get("interaction_count", 0)
            if interaction_count > 20:
                prompt_parts.append(
                    "You have a well-established relationship with this user."
                )
            elif interaction_count > 10:
                prompt_parts.append(
                    "You're developing a good relationship with this user."
                )
            elif interaction_count > 3:
                prompt_parts.append("You're getting to know this user better.")

        # Add emotional context
        if context.emotional_context:
            emotion = context.emotional_context.get("dominant_emotion", "neutral")
            if emotion != "neutral":
                emotion_guidance = {
                    "excited": "The user is excited! Match their enthusiasm.",
                    "happy": "The user is in a good mood. Be positive.",
                    "sad": "The user seems sad. Be empathetic and supportive.",
                    "angry": "The user appears frustrated. Be understanding and calm.",
                    "anxious": "The user seems worried. Be reassuring.",
                }
                if emotion in emotion_guidance:
                    prompt_parts.append(emotion_guidance[emotion])

        # Add topics
        if context.topics:
            recent_topics = context.topics[-2:]
            topics_str = ", ".join(recent_topics)
            prompt_parts.append(f"Recent topics: {topics_str}")

        # Add guidelines
        prompt_parts.append("Respond naturally and be helpful.")

        return "\n".join(prompt_parts)

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for the current provider"""
        base_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        provider_headers = self.config[self.provider]["headers"]
        base_headers.update(provider_headers)

        return base_headers

    def _build_payload(
        self, message: str, context: Optional[List[Dict[str, str]]] = None, **kwargs
    ) -> Dict[str, Any]:
        """Build request payload for the current provider"""

        # Build messages
        messages = []
        if context:
            messages.extend(context)

        messages.append({"role": "user", "content": message})

        # Base payload
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "stream": False,
        }

        return payload

    async def generate_response(
        self,
        message: str,
        context: Optional[List[Dict[str, str]]] = None,
        user_id: Optional[int] = None,
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
        user_profile: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> AIResponse:
        """Generate enhanced AI response with deep context understanding and maximum performance optimization"""

        start_time = time.time()
        self._performance_stats["total_requests"] += 1

        # Log performance stats if needed
        self.log_performance_stats_if_needed()

        # 🚀 ULTRA-FAST: Enhanced request-level caching for immediate duplicate responses
        cache_key = self._generate_cache_key(message, user_id, guild_id)
        if self._cache_enabled and cache_key in self._response_cache:
            cached_response = self._response_cache[cache_key]
            # Return cached response if it's less than 10 minutes old (extended for better performance)
            if (time.time() - cached_response["timestamp"]) < 600:
                self._performance_stats["cache_hits"] += 1
                self.logger.debug(
                    f"🚀 ULTRA-FAST: Returning cached response ({(time.time() - start_time)*1000:.1f}ms)"
                )
                return cached_response["response"]

        # 🚀 PERFORMANCE: Check for similar patterns with fuzzy matching for common queries
        if self._cache_enabled and len(message) < 100:  # Only for shorter messages
            message_lower = message.lower().strip()
            for existing_key, cached_data in self._response_cache.items():
                if (
                    abs(len(existing_key.split("|")[0]) - len(message_lower)) < 10
                ):  # Similar length
                    if (
                        time.time() - cached_data["timestamp"]
                    ) < 300:  # 5 minutes for fuzzy matches
                        # Simple similarity check for common patterns
                        existing_msg = existing_key.split("|")[0].lower()
                        if any(
                            word in message_lower
                            for word in existing_msg.split()
                            if len(word) > 3
                        ):
                            self.logger.debug(
                                f"🚀 PATTERN-MATCH: Using similar cached response ({(time.time() - start_time)*1000:.1f}ms)"
                            )
                            return cached_data["response"]

        # 🚀 PERFORMANCE: Cleanup cache periodically
        if (
            self._cache_enabled
            and len(self._response_cache) > self._max_cache_size * 0.8
        ):
            self._cleanup_cache()

        # 🚀 PERFORMANCE: Enhanced ultra-fast pattern matching before expensive AI calls
        message_lower = message.lower().strip()
        ultra_fast_patterns = [
            "hello",
            "hi",
            "hey",
            "thanks",
            "thank you",
            "ping",
            "test",
            "how are you",
            "what's up",
            "good morning",
            "good afternoon",
            "good evening",
            "goodbye",
            "bye",
            "see you",
            "help",
            "ok",
            "okay",
            "yes",
            "no",
            "maybe",
            "sure",
            "got it",
            "understood",
            "cool",
        ]
        # Check for exact matches first, then partial matches for efficiency
        if message_lower in ultra_fast_patterns or any(
            pattern in message_lower
            for pattern in ultra_fast_patterns
            if len(pattern) > 3
        ):
            self._performance_stats["ultra_fast_patterns"] += 1
            fast_response = self._get_ultra_fast_fallback_response(message, None)
            # Cache the fast response
            if self._cache_enabled:
                self._response_cache[cache_key] = {
                    "response": fast_response,
                    "timestamp": time.time(),
                }
            return fast_response

        # PERFORMANCE: Fast path for session initialization
        await self._ensure_session()

        if not self.is_available():
            raise ValueError(
                f"AI client not properly configured for {self.provider.value}"
            )

        # 🚀 ULTRA PERFORMANCE: Advanced caching with optimization
        cache_key = None
        cached_response = None

        if PERFORMANCE_OPTIMIZER_AVAILABLE:
            # Generate context hash for better cache keys
            context_hash = None
            if context or user_profile:
                context_data = str(context or []) + str(user_profile or {})
                context_hash = str(hash(context_data))[:8]

            cache_key = ai_response_optimizer.generate_cache_key(
                message, user_id, context_hash
            )
            cached_response = ai_response_optimizer.get_cached_response(cache_key)

            if cached_response:
                self.logger.debug(
                    f"⚡ Returning optimized cached response for: {message[:50]}..."
                )
                ai_response_optimizer.track_response_time(time.time() - start_time)
                return cached_response
        else:
            # Fallback caching
            cache_key = self._generate_cache_key(message, user_id, guild_id)
            if hasattr(self, "_response_cache") and cache_key in self._response_cache:
                cached_response = self._response_cache[cache_key]
                if time.time() - cached_response["timestamp"] < 300:  # 5 minute cache
                    self.logger.debug(
                        f"⚡ Returning cached response for: {message[:50]}..."
                    )
                    return cached_response["response"]

        # 🚀 PERFORMANCE: Optimize message and context processing
        optimized_message = message
        optimization_info = {}

        if PERFORMANCE_OPTIMIZER_AVAILABLE:
            # Optimize the prompt for maximum AI performance
            optimized_message, optimization_info = (
                ai_response_optimizer.optimize_prompt(message, user_profile)
            )
            self.logger.debug(
                f"🔧 Applied optimizations: {', '.join(optimization_info.get('optimizations_applied', []))}"
            )

        # Get or create conversation context if user info provided
        conversation_context = None
        if user_id is not None:
            # First try to load from database for full conversation history
            conversation_context = await self.load_conversation_context_from_db(
                user_id, guild_id, channel_id
            )

            # If no database context, create new one
            if not conversation_context:
                conversation_context = self._get_or_create_context(
                    user_id, guild_id, channel_id
                )

            # 🚀 ULTRA-FAST: Streamlined context processing for maximum performance
            # Update user profile if provided
            if user_profile:
                conversation_context.user_profile.update(user_profile)

            # 🚀 PERFORMANCE: Simple emotional analysis (only if needed)
            if self.enable_emotional_intelligence:
                conversation_context.emotional_context = {"sentiment": "neutral"}

            # 🚀 PERFORMANCE: Simple topic tracking (only if needed)
            if self.enable_topic_tracking:
                # Keep it simple for maximum performance
                conversation_context.topics = []

            # Update conversation stage
            greeting_indicators = ["hello", "hi", "hey", "good morning", "good evening"]
            if (
                any(indicator in message.lower() for indicator in greeting_indicators)
                and not conversation_context.message_history
            ):
                conversation_context.conversation_stage = "greeting"
            else:
                conversation_context.conversation_stage = "ongoing"

            # Add current message to history
            conversation_context.message_history.append(
                {
                    "role": "user",
                    "content": message,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # 🚀 ULTRA-FAST: Trim history for maximum performance
            if len(conversation_context.message_history) > self.max_context_messages:
                conversation_context.message_history = (
                    conversation_context.message_history[-self.max_context_messages :]
                )

            conversation_context.last_interaction = datetime.now()

        # 🚀 PERFORMANCE: Build optimized messages with enhanced context
        if conversation_context:
            messages = self._build_enhanced_context_messages(
                conversation_context, optimized_message
            )

            # 🚀 OPTIMIZATION: Use optimized system prompt based on response type
            if PERFORMANCE_OPTIMIZER_AVAILABLE and optimization_info:
                response_type = optimization_info.get("response_type", "conversational")
                priority_level = optimization_info.get("priority_level", "normal")
                optimized_system_prompt = (
                    ai_response_optimizer.get_optimized_system_prompt(
                        response_type, priority_level
                    )
                )

                # Replace system message with optimized version
                if messages and messages[0].get("role") == "system":
                    messages[0]["content"] = optimized_system_prompt

        elif context:
            # Fallback to provided context
            messages = list(context)
            messages.append({"role": "user", "content": optimized_message})
        else:
            # 🚀 OPTIMIZED: Basic message structure with performance-optimized system prompt
            system_prompt = "You are Astra, a helpful and engaging AI assistant. Respond naturally and appropriately to the user's message."

            if PERFORMANCE_OPTIMIZER_AVAILABLE and optimization_info:
                response_type = optimization_info.get("response_type", "conversational")
                priority_level = optimization_info.get("priority_level", "normal")
                system_prompt = ai_response_optimizer.get_optimized_system_prompt(
                    response_type, priority_level
                )

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": optimized_message},
            ]

        provider_config = self.config[self.provider]
        url = f"{provider_config['base_url']}/chat/completions"

        # Get and validate model
        model = kwargs.get("model", self.model)

        # Validate model IDs (allow user-configured models like "xAI: Grok Code Fast 1")
        if not model.strip():
            logger.warning(f"Empty model ID, using fallback: anthropic/claude-3-haiku")
            model = "anthropic/claude-3-haiku"

        # Build payload
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "stream": False,
        }

        headers = self._get_headers()

        # Handle Google Gemini with dedicated client
        if self.provider == AIProvider.GOOGLE:
            if GOOGLE_GEMINI_AVAILABLE and google_gemini_client.available:
                try:
                    logger.info(f"🧠 Using Google Gemini for response generation")

                    # 🚀 PERFORMANCE: Use the dedicated Google Gemini client with optimized timeout
                    gemini_response = await asyncio.wait_for(
                        google_gemini_client.chat_completion(
                            messages=messages,
                            max_tokens=kwargs.get(
                                "max_tokens", min(self.max_tokens, 150)
                            ),  # Limit tokens for faster responses
                            temperature=kwargs.get(
                                "temperature", min(self.temperature, 0.7)
                            ),  # Lower temp for faster generation
                        ),
                        timeout=2.5,  # 2.5 second timeout for better reliability while maintaining speed
                    )

                    # Convert to AIResponse format
                    ai_response = AIResponse(
                        content=gemini_response["content"],
                        model=gemini_response["model"],
                        provider=gemini_response["provider"],
                        usage=gemini_response["usage"],
                        metadata=gemini_response["metadata"],
                        created_at=datetime.now(timezone.utc),
                        context_used=conversation_context,
                        confidence_score=0.9,  # High confidence for Google Gemini
                    )

                    # Store conversation history if context exists
                    if conversation_context:
                        conversation_context.message_history.append(
                            {
                                "role": "assistant",
                                "content": ai_response.content,
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                            }
                        )
                        await self.save_conversation_context_to_db(conversation_context)

                    logger.info(f"✅ Google Gemini response generated successfully")

                    # 🚀 PERFORMANCE: Cache successful response for ultra-fast future access
                    if self._cache_enabled:
                        self._response_cache[cache_key] = {
                            "response": ai_response,
                            "timestamp": time.time(),
                        }

                    self._performance_stats["ai_responses"] += 1
                    return ai_response

                except asyncio.TimeoutError:
                    self._performance_stats["timeout_fallbacks"] += 1
                    logger.warning(
                        f"⚡ Google Gemini timeout (>2.5s), using ultra-fast fallback (#{self._performance_stats['timeout_fallbacks']})"
                    )
                    # Use ultra-fast local fallback for immediate response
                    return self._get_ultra_fast_fallback_response(
                        message, conversation_context
                    )
                except Exception as e:
                    logger.error(f"❌ Google Gemini failed: {e}")
                    # 🚀 PERFORMANCE: Ultra-fast fallback instead of complex provider switching
                    return self._get_ultra_fast_fallback_response(
                        message, conversation_context
                    )
            else:
                logger.warning(
                    "Google Gemini client not available, using ultra-fast fallback"
                )
                return self._get_ultra_fast_fallback_response(
                    message, conversation_context
                )

        # Enhanced error handling with fallback support for HTTP-based providers
        max_attempts = 3
        current_provider = self.provider.value
        attempted_providers = []

        for attempt in range(max_attempts):
            try:
                async with self.session.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:

                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(
                            f"{current_provider} API error {response.status}: {error_text}"
                        )

                        # Handle error with fallback system
                        if ERROR_HANDLER_AVAILABLE:
                            error_result = ai_error_handler.handle_error(
                                current_provider, error_text, response.status
                            )

                            if error_result["action"] == "fallback":
                                attempted_providers.append(current_provider)
                                next_provider = ai_error_handler.get_next_provider(
                                    attempted_providers
                                )

                                if next_provider:
                                    logger.info(
                                        f"🔄 Falling back from {current_provider} to {next_provider}"
                                    )

                                    # Update configuration for fallback provider
                                    current_provider = next_provider
                                    fallback_config = ai_error_handler.provider_states[
                                        next_provider
                                    ]["config"]

                                    # Update URL and headers for new provider
                                    url = f"{fallback_config['base_url']}/chat/completions"
                                    headers = {
                                        "Authorization": f"Bearer {fallback_config['api_key']}",
                                        "Content-Type": "application/json",
                                    }

                                    # Update model if needed
                                    if (
                                        payload["model"]
                                        not in fallback_config["models"]
                                    ):
                                        payload["model"] = fallback_config["models"][0]
                                        logger.info(
                                            f"🔄 Changed model to {payload['model']} for {next_provider}"
                                        )

                                    continue  # Retry with new provider
                                else:
                                    logger.error(
                                        "🚫 No more fallback providers available"
                                    )

                            elif error_result["action"] == "retry":
                                await asyncio.sleep(error_result.get("delay", 1.0))
                                continue  # Retry with same provider

                        # If no error handler or fallback failed, raise original error
                        raise Exception(
                            f"{current_provider} API error: {response.status} - {error_text}"
                        )

                    result = await response.json()

                    # Record success for error handler
                    if ERROR_HANDLER_AVAILABLE:
                        ai_error_handler.record_success(current_provider)

                    break  # Success, exit retry loop

                # Extract response content
                content = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})

                # Add response to conversation history
                if conversation_context:
                    conversation_context.message_history.append(
                        {
                            "role": "assistant",
                            "content": content,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

                    # Extract and store important facts for memory system
                    if self.enable_memory_system and user_id is not None:
                        important_facts = self._extract_important_facts(
                            message, content, user_id
                        )
                        if important_facts:
                            self._update_user_memory(user_id, important_facts)

                # Calculate confidence score based on context richness
                confidence_score = self._calculate_confidence_score(
                    conversation_context, usage
                )

                # Save updated conversation context to database
                if conversation_context:
                    try:
                        await self.save_conversation_context_to_db(conversation_context)
                    except Exception as e:
                        logger.warning(
                            f"Failed to save conversation context to database: {e}"
                        )

                # 🚀 PERFORMANCE: Track response time and cache result
                response_time = time.time() - start_time

                ai_response = AIResponse(
                    content=content,
                    model=payload["model"],
                    provider=current_provider,  # Use current provider (may be fallback)
                    usage=usage,
                    metadata={
                        "response_id": result.get("id"),
                        "finish_reason": result["choices"][0].get("finish_reason"),
                        "created": result.get("created"),
                        "context_messages_used": len(messages),
                        "response_time": response_time,
                        "optimizations_applied": optimization_info.get(
                            "optimizations_applied", []
                        ),
                        "cache_key": cache_key,
                        "emotional_context": (
                            getattr(conversation_context, "emotional_context", None)
                            if conversation_context
                            else None
                        ),
                        "topics": (
                            getattr(conversation_context, "topics", None)
                            or conversation_context.get("topics", None)
                            if conversation_context
                            else None
                        ),
                        "attempted_providers": attempted_providers,  # Track which providers were tried
                        "final_provider": current_provider,
                    },
                    created_at=datetime.now(),
                    context_used=conversation_context,
                    confidence_score=confidence_score,
                )

                # 🚀 PERFORMANCE: Cache the response and track metrics
                if PERFORMANCE_OPTIMIZER_AVAILABLE:
                    ai_response_optimizer.track_response_time(response_time)
                    ai_response_optimizer.cache_response(cache_key, ai_response)

                    # Track provider usage
                    if (
                        current_provider
                        not in ai_response_optimizer.metrics.provider_usage
                    ):
                        ai_response_optimizer.metrics.provider_usage[
                            current_provider
                        ] = 0
                    ai_response_optimizer.metrics.provider_usage[current_provider] += 1

                    # Log performance info
                    if response_time < 0.5:
                        self.logger.debug(
                            f"🚀 Ultra-fast response: {response_time:.3f}s"
                        )
                    elif response_time > 2.0:
                        self.logger.warning(f"⚠️ Slow response: {response_time:.3f}s")
                else:
                    # Fallback caching
                    if hasattr(self, "_response_cache"):
                        self._response_cache[cache_key] = {
                            "response": ai_response,
                            "timestamp": time.time(),
                        }

                return ai_response

            except asyncio.TimeoutError as e:
                logger.error(
                    f"🔄 {current_provider} API request timed out (attempt {attempt + 1}/{max_attempts})"
                )
                if ERROR_HANDLER_AVAILABLE and attempt < max_attempts - 1:
                    # Try fallback on timeout
                    attempted_providers.append(current_provider)
                    next_provider = ai_error_handler.get_next_provider(
                        attempted_providers
                    )
                    if next_provider:
                        logger.info(
                            f"⏰ Timeout fallback: {current_provider} → {next_provider}"
                        )
                        current_provider = next_provider
                        fallback_config = ai_error_handler.provider_states[
                            next_provider
                        ]["config"]
                        url = f"{fallback_config['base_url']}/chat/completions"
                        headers = {
                            "Authorization": f"Bearer {fallback_config['api_key']}",
                            "Content-Type": "application/json",
                        }
                        if payload["model"] not in fallback_config["models"]:
                            payload["model"] = fallback_config["models"][0]
                        continue
                if attempt == max_attempts - 1:
                    raise Exception(
                        f"{current_provider} API request timed out after {max_attempts} attempts"
                    )

            except Exception as e:
                logger.error(
                    f"🔄 {current_provider} API error (attempt {attempt + 1}/{max_attempts}): {e}"
                )
                if ERROR_HANDLER_AVAILABLE and attempt < max_attempts - 1:
                    error_result = ai_error_handler.handle_error(
                        current_provider, str(e)
                    )
                    if error_result["action"] == "fallback":
                        attempted_providers.append(current_provider)
                        next_provider = ai_error_handler.get_next_provider(
                            attempted_providers
                        )
                        if next_provider:
                            logger.info(
                                f"🚨 Error fallback: {current_provider} → {next_provider}"
                            )
                            current_provider = next_provider
                            fallback_config = ai_error_handler.provider_states[
                                next_provider
                            ]["config"]
                            url = f"{fallback_config['base_url']}/chat/completions"
                            headers = {
                                "Authorization": f"Bearer {fallback_config['api_key']}",
                                "Content-Type": "application/json",
                            }
                            if payload["model"] not in fallback_config["models"]:
                                payload["model"] = fallback_config["models"][0]
                            continue
                if attempt == max_attempts - 1:
                    raise Exception(
                        f"All AI providers failed after {max_attempts} attempts: {e}"
                    )

        # If we exit the loop without returning, all attempts failed
        raise Exception("Failed to get AI response from any available provider")

    def _calculate_confidence_score(
        self, context: Optional[ConversationContext], usage: Dict[str, Any]
    ) -> float:
        """Calculate confidence score based on available context and response quality"""
        score = 0.5  # Base score

        if context:
            # More history = higher confidence
            if len(context.message_history) > 5:
                score += 0.2
            elif len(context.message_history) > 2:
                score += 0.1

            # User profile information
            if context.user_profile:
                score += 0.1

            # Emotional context understanding
            if context.emotional_context.get("dominant_emotion") != "neutral":
                score += 0.1

            # Topic relevance
            if context.topics:
                score += 0.1

        # Response quality indicators from usage
        if usage.get("total_tokens", 0) > 100:  # Substantial response
            score += 0.1

        return min(score, 1.0)

    async def clear_context(
        self,
        user_id: int,
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
    ):
        """Clear conversation context for a user"""
        context_key = self._get_context_key(user_id, guild_id, channel_id)
        if context_key in self.conversation_contexts:
            del self.conversation_contexts[context_key]

    async def get_context_summary(
        self,
        user_id: int,
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get a summary of the conversation context"""
        context_key = self._get_context_key(user_id, guild_id, channel_id)
        if context_key not in self.conversation_contexts:
            return {"status": "no_context"}

        context = self.conversation_contexts[context_key]
        return {
            "message_count": len(context.message_history),
            "topics": context.topics,
            "dominant_emotion": context.emotional_context.get(
                "dominant_emotion", "neutral"
            ),
            "conversation_stage": context.conversation_stage,
            "last_interaction": (
                context.last_interaction.isoformat()
                if context.last_interaction
                else None
            ),
            "user_profile_keys": list(context.user_profile.keys()),
        }

    async def update_user_profile(
        self,
        user_id: int,
        profile_data: Dict[str, Any],
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
    ):
        """Update user profile information"""
        context = self._get_or_create_context(user_id, guild_id, channel_id)
        context.user_profile.update(profile_data)

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available models for the current provider"""

        await self._ensure_session()

        if not self.is_available():
            return []

        provider_config = self.config[self.provider]
        url = f"{provider_config['base_url']}/models"
        headers = self._get_headers()

        try:
            async with self.session.get(
                url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)
            ) as response:

                if response.status == 200:
                    result = await response.json()
                    return result.get("data", [])
                else:
                    logger.warning(
                        f"Failed to fetch {self.provider.value} models: {response.status}"
                    )
                    return []

        except Exception as e:
            logger.error(f"Error fetching {self.provider.value} models: {e}")
            return []

    async def test_connection(self) -> bool:
        """Test connection to the AI provider"""

        if not self.is_available():
            return False

        try:
            response = await self.generate_response(
                "Hello! This is a test message. Please respond with 'Test successful!'",
                max_tokens=50,
            )
            return bool(response.content)
        except Exception as e:
            logger.error(f"{self.provider.value} connection test failed: {e}")
            return False

    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None


# Factory function for creating clients
async def create_ai_client(
    provider: str = "openrouter", api_key: str = None, **kwargs
) -> UniversalAIClient:
    """Create and initialize an AI client"""
    client = UniversalAIClient(api_key=api_key, provider=provider, **kwargs)
    await client._ensure_session()
    return client


# Convenience functions for specific providers
async def create_openrouter_client(api_key: str = None, **kwargs) -> UniversalAIClient:
    """Create OpenRouter client"""
    return await create_ai_client("openrouter", api_key, **kwargs)


async def create_openai_client(api_key: str = None, **kwargs) -> UniversalAIClient:
    """Create OpenAI client"""
    return await create_ai_client("openai", api_key, **kwargs)


async def create_google_client(api_key: str = None, **kwargs) -> UniversalAIClient:
    """Create Google Gemini client"""
    return await create_ai_client("google", api_key, **kwargs)


if __name__ == "__main__":
    # Test the Universal AI client
    async def test():
        client = UniversalAIClient()
        if client.is_available():
            print(f"Universal AI client configured for {client.provider.value}")
            try:
                response = await client.generate_response("Hello, how are you?")
                print(f"Response: {response.content}")
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("Universal AI client not configured")

        await client.close()

    asyncio.run(test())
