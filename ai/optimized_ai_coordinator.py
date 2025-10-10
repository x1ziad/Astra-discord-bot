"""
🚀 OPTIMIZED AI COORDINATOR
Ultra-high performance AI system integrating the complete Astra personality specification

Features:
- Complete Astra personality system with adaptation engine
- Maximum performance optimization
- Cohesive integration across all components
- Real-time adaptation and coherence
- Advanced caching and memory management
- Comprehensive telemetry and monitoring

Author: x1ziad
Version: 2.0.0 PERFORMANCE
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import weakref
from pathlib import Path
import sqlite3
import hashlib

# Performance imports
try:
    import orjson as fast_json

    USE_FAST_JSON = True
except ImportError:
    import json as fast_json

    USE_FAST_JSON = False

try:
    import lru  # For fast LRU cache

    USE_FAST_LRU = True
except ImportError:
    from functools import lru_cache

    USE_FAST_LRU = False

# Core imports
from ai.universal_ai_client import UniversalAIClient, AIResponse, ConversationContext
from ai.personality_integration import PersonalityIntegration
from ai.error_handler import ai_error_handler, AIErrorType

logger = logging.getLogger("astra.ai_coordinator")


class PersonalityMode(Enum):
    """Astra personality modes from specification"""

    SOCIAL = "social"
    SECURITY = "security"
    MISSION_CONTROL = "mission_control"
    DEVELOPER = "developer"
    EMPATHY = "empathy"
    ADAPTIVE = "adaptive"  # Dynamic mode switching


class AdaptationSignal(Enum):
    """Adaptation signals from the specification"""

    SPAM_SPIKE = "spam_spike"
    EVENT_START = "event_start"
    QUIET_HOURS = "quiet_hours"
    CONFLICT_DETECTED = "conflict_detected"
    LOW_ENGAGEMENT = "low_engagement"
    RAID_DETECTED = "raid_detected"
    LINK_SPIKE = "link_spike"
    BOT_ANOMALY = "bot_anomaly"


@dataclass
class PersonalityTraits:
    """Core personality traits (0-100 scale) from Astra specification"""

    humor: int = 50
    honesty: int = 85
    formality: int = 40
    empathy: int = 75
    strictness: int = 45
    initiative: int = 65
    mode: PersonalityMode = PersonalityMode.SOCIAL
    version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "humor": self.humor,
            "honesty": self.honesty,
            "formality": self.formality,
            "empathy": self.empathy,
            "strictness": self.strictness,
            "initiative": self.initiative,
            "mode": self.mode.value,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PersonalityTraits":
        return cls(
            humor=data.get("humor", 50),
            honesty=data.get("honesty", 85),
            formality=data.get("formality", 40),
            empathy=data.get("empathy", 75),
            strictness=data.get("strictness", 45),
            initiative=data.get("initiative", 65),
            mode=PersonalityMode(data.get("mode", "social")),
            version=data.get("version", 1),
        )


@dataclass
class AdaptationEvent:
    """Adaptation event from the specification"""

    id: str
    guild_id: int
    event_type: AdaptationSignal
    payload: Dict[str, Any]
    delta_profile: Dict[str, Any]
    applied_at: datetime
    expires_at: Optional[datetime] = None
    status: str = "active"  # active, expired, cancelled
    priority: int = 50
    reason: str = ""
    applied_by: str = "auto-adapt"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "guild_id": self.guild_id,
            "event_type": self.event_type.value,
            "payload": self.payload,
            "delta_profile": self.delta_profile,
            "applied_at": self.applied_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "status": self.status,
            "priority": self.priority,
            "reason": self.reason,
            "applied_by": self.applied_by,
        }


@dataclass
class SessionState:
    """Session state from the specification"""

    session_id: str
    guild_id: int
    channel_id: int
    user_id: int
    conversation_window: List[Dict[str, Any]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    personality_snapshot: Optional[PersonalityTraits] = None
    adaptation_context: Dict[str, Any] = field(default_factory=dict)


class OptimizedAICoordinator:
    """
    🚀 ULTRA-HIGH PERFORMANCE AI COORDINATOR

    Implements the complete Astra personality system with:
    - Real-time adaptation engine
    - Advanced caching and memory management
    - Coherence and cohesion modules
    - Maximum performance optimization
    - Comprehensive telemetry
    """

    def __init__(self, bot=None):
        self.bot = bot
        self.logger = logging.getLogger("astra.ai_coordinator")

        # Performance tracking
        self.start_time = time.time()
        self.requests_processed = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.adaptation_events = 0

        # Core AI client
        self.ai_client: Optional[UniversalAIClient] = None
        self.personality_integration: Optional[PersonalityIntegration] = None

        # Database paths
        self.db_path = Path("data/astra_personality.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # High-performance caches
        self._personality_cache: Dict[int, PersonalityTraits] = {}
        self._session_cache: Dict[str, SessionState] = {}
        self._adaptation_cache: Dict[int, List[AdaptationEvent]] = {}
        self._response_cache: Dict[str, Tuple[str, datetime]] = {}

        # Cache configuration
        self.cache_ttl = 300  # 5 minutes
        self.max_cache_size = 1000
        self.max_session_window = 20  # Messages

        # Adaptation engine configuration
        self.adaptation_enabled = True
        self.adaptation_cooldown = 300  # 5 minutes
        self.last_adaptation: Dict[int, datetime] = {}

        # Performance optimization flags
        self.use_fast_responses = True
        self.enable_response_caching = True
        self.enable_personality_caching = True
        self.enable_context_compression = True

        # Initialize database
        self._setup_database()

        self.logger.info("🚀 Optimized AI Coordinator initialized")

    def _setup_database(self):
        """Setup optimized database schema from the specification"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA journal_mode=WAL")  # Performance optimization
                conn.execute("PRAGMA synchronous=NORMAL")  # Balance safety/performance
                conn.execute("PRAGMA cache_size=10000")  # Increase cache

                # Guild personalities table (from specification)
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS guild_personalities (
                        guild_id INTEGER PRIMARY KEY,
                        humor INTEGER DEFAULT 50,
                        honesty INTEGER DEFAULT 85,
                        formality INTEGER DEFAULT 40,
                        empathy INTEGER DEFAULT 75,
                        strictness INTEGER DEFAULT 45,
                        initiative INTEGER DEFAULT 65,
                        mode TEXT DEFAULT 'social',
                        version INTEGER DEFAULT 1,
                        updated_by INTEGER,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # User personality overrides table
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS user_personality_overrides (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        guild_id INTEGER,
                        humor INTEGER NULL,
                        honesty INTEGER NULL,
                        formality INTEGER NULL,
                        empathy INTEGER NULL,
                        strictness INTEGER NULL,
                        initiative INTEGER NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, guild_id)
                    )
                """
                )

                # Session state table (optimized for performance)
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS session_state (
                        session_id TEXT PRIMARY KEY,
                        guild_id INTEGER,
                        channel_id INTEGER,
                        user_id INTEGER,
                        conversation_window TEXT,
                        personality_snapshot TEXT,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Adaptation events table
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS adaptation_events (
                        id TEXT PRIMARY KEY,
                        guild_id INTEGER,
                        event_type TEXT,
                        payload TEXT,
                        delta_profile TEXT,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP,
                        status TEXT DEFAULT 'active',
                        priority INTEGER DEFAULT 50,
                        reason TEXT,
                        applied_by TEXT DEFAULT 'auto-adapt'
                    )
                """
                )

                # Performance indexes
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_guild_personalities ON guild_personalities(guild_id)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_user_overrides ON user_personality_overrides(user_id, guild_id)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_session_state ON session_state(guild_id, channel_id, user_id)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_adaptation_events ON adaptation_events(guild_id, status)"
                )

                conn.commit()

        except Exception as e:
            self.logger.error(f"Database setup error: {e}")

    async def initialize(self):
        """Initialize the AI coordinator with all components"""
        try:
            # Initialize AI client
            self.ai_client = UniversalAIClient(
                provider="google",  # Primary provider
                max_context_messages=10,  # Optimized for performance
                enable_emotional_intelligence=True,
                enable_topic_tracking=True,
                enable_memory_system=True,
            )

            # Initialize personality integration
            self.personality_integration = PersonalityIntegration()
            await self.personality_integration.initialize()

            # Pre-load frequently accessed data
            await self._preload_caches()

            # Start background tasks
            self._start_background_tasks()

            self.logger.info("✅ AI Coordinator fully initialized")

        except Exception as e:
            self.logger.error(f"❌ AI Coordinator initialization failed: {e}")
            raise

    async def _preload_caches(self):
        """Preload frequently accessed data for performance"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Preload active guild personalities
                cursor = conn.execute("SELECT * FROM guild_personalities LIMIT 100")
                for row in cursor.fetchall():
                    guild_id = row[0]
                    personality = PersonalityTraits(
                        humor=row[1],
                        honesty=row[2],
                        formality=row[3],
                        empathy=row[4],
                        strictness=row[5],
                        initiative=row[6],
                        mode=PersonalityMode(row[7]),
                        version=row[8],
                    )
                    self._personality_cache[guild_id] = personality

                # Preload active adaptation events
                cursor = conn.execute(
                    """
                    SELECT * FROM adaptation_events 
                    WHERE status = 'active' AND (expires_at IS NULL OR expires_at > ?)
                """,
                    (datetime.now(timezone.utc).isoformat(),),
                )

                for row in cursor.fetchall():
                    guild_id = row[1]
                    if guild_id not in self._adaptation_cache:
                        self._adaptation_cache[guild_id] = []

                    event = AdaptationEvent(
                        id=row[0],
                        guild_id=guild_id,
                        event_type=AdaptationSignal(row[2]),
                        payload=(
                            fast_json.loads(row[3])
                            if USE_FAST_JSON
                            else json.loads(row[3])
                        ),
                        delta_profile=(
                            fast_json.loads(row[4])
                            if USE_FAST_JSON
                            else json.loads(row[4])
                        ),
                        applied_at=datetime.fromisoformat(row[5]),
                        expires_at=datetime.fromisoformat(row[6]) if row[6] else None,
                        status=row[7],
                        priority=row[8],
                        reason=row[9],
                        applied_by=row[10],
                    )
                    self._adaptation_cache[guild_id].append(event)

            self.logger.info(
                f"🚀 Preloaded {len(self._personality_cache)} personalities, {sum(len(events) for events in self._adaptation_cache.values())} adaptations"
            )

        except Exception as e:
            self.logger.error(f"Cache preloading error: {e}")

    def _start_background_tasks(self):
        """Start optimized background maintenance tasks"""
        # Cache cleanup task (every 5 minutes)
        asyncio.create_task(self._cache_cleanup_task())

        # Adaptation expiry task (every minute)
        asyncio.create_task(self._adaptation_expiry_task())

        # Performance metrics task (every 10 minutes)
        asyncio.create_task(self._performance_metrics_task())

    async def _cache_cleanup_task(self):
        """Clean up expired cache entries"""
        while True:
            try:
                await asyncio.sleep(300)  # 5 minutes

                now = datetime.now(timezone.utc)

                # Clean response cache
                expired_keys = [
                    key
                    for key, (_, timestamp) in self._response_cache.items()
                    if (now - timestamp).total_seconds() > self.cache_ttl
                ]
                for key in expired_keys:
                    del self._response_cache[key]

                # Clean session cache
                expired_sessions = [
                    session_id
                    for session_id, session in self._session_cache.items()
                    if (now - session.last_updated).total_seconds() > self.cache_ttl * 2
                ]
                for session_id in expired_sessions:
                    del self._session_cache[session_id]

                # Limit cache sizes
                if len(self._personality_cache) > self.max_cache_size:
                    # Keep most recently used
                    sorted_items = sorted(
                        self._personality_cache.items(),
                        key=lambda x: getattr(x[1], "last_accessed", 0),
                        reverse=True,
                    )
                    self._personality_cache = dict(sorted_items[: self.max_cache_size])

                if expired_keys or expired_sessions:
                    self.logger.debug(
                        f"🧹 Cache cleanup: {len(expired_keys)} responses, {len(expired_sessions)} sessions"
                    )

            except Exception as e:
                self.logger.error(f"Cache cleanup error: {e}")

    async def _adaptation_expiry_task(self):
        """Handle adaptation event expiry"""
        while True:
            try:
                await asyncio.sleep(60)  # 1 minute

                now = datetime.now(timezone.utc)
                expired_events = []

                for guild_id, events in self._adaptation_cache.items():
                    for event in events[
                        :
                    ]:  # Copy to avoid modification during iteration
                        if event.expires_at and now >= event.expires_at:
                            event.status = "expired"
                            expired_events.append(event)
                            events.remove(event)

                # Update database
                if expired_events:
                    with sqlite3.connect(self.db_path) as conn:
                        for event in expired_events:
                            conn.execute(
                                "UPDATE adaptation_events SET status = 'expired' WHERE id = ?",
                                (event.id,),
                            )
                        conn.commit()

                    self.logger.info(
                        f"⏰ Expired {len(expired_events)} adaptation events"
                    )

            except Exception as e:
                self.logger.error(f"Adaptation expiry error: {e}")

    async def _performance_metrics_task(self):
        """Log performance metrics"""
        while True:
            try:
                await asyncio.sleep(600)  # 10 minutes

                uptime = time.time() - self.start_time
                cache_hit_rate = (
                    self.cache_hits / max(self.cache_hits + self.cache_misses, 1) * 100
                )

                self.logger.info(f"📊 PERFORMANCE METRICS:")
                self.logger.info(f"   ⏱️  Uptime: {uptime/3600:.2f}h")
                self.logger.info(f"   📊 Requests: {self.requests_processed}")
                self.logger.info(f"   🎯 Cache Hit Rate: {cache_hit_rate:.1f}%")
                self.logger.info(f"   🔄 Adaptations: {self.adaptation_events}")
                self.logger.info(
                    f"   💾 Cache Sizes: P={len(self._personality_cache)}, S={len(self._session_cache)}, R={len(self._response_cache)}"
                )

            except Exception as e:
                self.logger.error(f"Performance metrics error: {e}")

    async def get_effective_personality(
        self, guild_id: int, user_id: Optional[int] = None
    ) -> PersonalityTraits:
        """Get effective personality with user overrides and adaptations (optimized)"""

        # Check cache first
        cache_key = f"{guild_id}:{user_id or 0}"
        if self.enable_personality_caching and cache_key in self._personality_cache:
            self.cache_hits += 1
            return self._personality_cache[cache_key]

        self.cache_misses += 1

        try:
            # Start with guild default or global default
            personality = PersonalityTraits()  # Default values

            with sqlite3.connect(self.db_path) as conn:
                # Get guild personality
                cursor = conn.execute(
                    "SELECT * FROM guild_personalities WHERE guild_id = ?", (guild_id,)
                )
                row = cursor.fetchone()
                if row:
                    personality = PersonalityTraits(
                        humor=row[1],
                        honesty=row[2],
                        formality=row[3],
                        empathy=row[4],
                        strictness=row[5],
                        initiative=row[6],
                        mode=PersonalityMode(row[7]),
                        version=row[8],
                    )

                # Apply user overrides if present
                if user_id:
                    cursor = conn.execute(
                        "SELECT * FROM user_personality_overrides WHERE user_id = ? AND guild_id = ?",
                        (user_id, guild_id),
                    )
                    row = cursor.fetchone()
                    if row:
                        # Apply non-null overrides
                        if row[3] is not None:
                            personality.humor = row[3]
                        if row[4] is not None:
                            personality.honesty = row[4]
                        if row[5] is not None:
                            personality.formality = row[5]
                        if row[6] is not None:
                            personality.empathy = row[6]
                        if row[7] is not None:
                            personality.strictness = row[7]
                        if row[8] is not None:
                            personality.initiative = row[8]

            # Apply active adaptations
            if guild_id in self._adaptation_cache:
                for event in self._adaptation_cache[guild_id]:
                    if event.status == "active":
                        delta = event.delta_profile
                        personality.humor = max(
                            0, min(100, personality.humor + delta.get("humor", 0))
                        )
                        personality.honesty = max(
                            0, min(100, personality.honesty + delta.get("honesty", 0))
                        )
                        personality.formality = max(
                            0,
                            min(100, personality.formality + delta.get("formality", 0)),
                        )
                        personality.empathy = max(
                            0, min(100, personality.empathy + delta.get("empathy", 0))
                        )
                        personality.strictness = max(
                            0,
                            min(
                                100, personality.strictness + delta.get("strictness", 0)
                            ),
                        )
                        personality.initiative = max(
                            0,
                            min(
                                100, personality.initiative + delta.get("initiative", 0)
                            ),
                        )

                        if "mode" in delta:
                            personality.mode = PersonalityMode(delta["mode"])

            # Cache the result
            if self.enable_personality_caching:
                self._personality_cache[cache_key] = personality

            return personality

        except Exception as e:
            self.logger.error(f"Error getting effective personality: {e}")
            return PersonalityTraits()  # Return default on error

    async def generate_response(
        self,
        message: str,
        guild_id: int,
        channel_id: int,
        user_id: int,
        user_name: str = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> str:
        """Generate optimized AI response with full personality integration"""

        self.requests_processed += 1
        start_time = time.time()

        try:
            # Fast response check for common patterns
            if self.use_fast_responses:
                fast_response = await self._check_fast_responses(
                    message, guild_id, user_id
                )
                if fast_response:
                    return fast_response

            # Check response cache
            if self.enable_response_caching:
                cache_key = self._generate_cache_key(message, guild_id, user_id)
                if cache_key in self._response_cache:
                    cached_response, timestamp = self._response_cache[cache_key]
                    if (
                        datetime.now(timezone.utc) - timestamp
                    ).total_seconds() < self.cache_ttl:
                        self.cache_hits += 1
                        return cached_response

            # Get effective personality
            personality = await self.get_effective_personality(guild_id, user_id)

            # Get or create session state
            session = await self._get_session_state(guild_id, channel_id, user_id)
            session.personality_snapshot = personality

            # Check for identity questions first
            if (
                self.personality_integration
                and self.personality_integration.is_identity_question(message)
            ):
                identity_response = (
                    await self.personality_integration.process_message_for_identity(
                        user_id, message, user_name, f"channel_{channel_id}"
                    )
                )
                if identity_response:
                    await self._update_session_state(
                        session, message, identity_response
                    )
                    return identity_response

            # Build enhanced context
            enhanced_context = await self._build_enhanced_context(
                session, personality, message, context
            )

            # Generate AI response
            if not self.ai_client:
                return "AI system is not initialized. Please try again later."

            ai_response = await self.ai_client.generate_response(
                message=message,
                context=enhanced_context,
                user_id=user_id,
                guild_id=guild_id,
                channel_id=channel_id,
                user_profile={"name": user_name} if user_name else None,
                **kwargs,
            )

            response_content = ai_response.content

            # Apply personality-specific enhancements
            response_content = await self._apply_personality_enhancements(
                response_content, personality, session
            )

            # Update session state
            await self._update_session_state(session, message, response_content)

            # Cache the response
            if self.enable_response_caching and cache_key:
                self._response_cache[cache_key] = (
                    response_content,
                    datetime.now(timezone.utc),
                )

            # Log performance
            processing_time = (time.time() - start_time) * 1000
            self.logger.debug(f"⚡ Response generated in {processing_time:.1f}ms")

            return response_content

        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return "I encountered an error processing your message. Please try again."

    async def process_message(
        self, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process message and return structured response for testing"""
        try:
            # Extract context values with defaults
            user_id = context.get("user_id", 12345)
            guild_id = context.get("guild_id", 67890)
            channel_id = context.get("channel_id", 11111)
            user_name = context.get("user_name", "TestUser")

            # Generate response using the main method
            response_text = await self.generate_response(
                message=message,
                guild_id=guild_id,
                channel_id=channel_id,
                user_id=user_id,
                user_name=user_name,
                context=context,
            )

            # Get personality info
            personality = await self.get_effective_personality(guild_id, user_id)

            return {
                "response": response_text,
                "success": True,
                "confidence": 0.85,
                "personality_info": {
                    "humor": personality.humor,
                    "empathy": personality.empathy,
                    "formality": personality.formality,
                    "mode": personality.mode.value if personality.mode else "adaptive",
                },
                "processing_time": time.time(),
            }

        except Exception as e:
            self.logger.error(f"Error in process_message: {e}")
            return {
                "response": "I encountered an error processing your message.",
                "success": False,
                "error": str(e),
                "confidence": 0.0,
            }

    async def _check_fast_responses(
        self, message: str, guild_id: int, user_id: int
    ) -> Optional[str]:
        """Check for fast response patterns that don't need AI processing"""
        message_lower = message.lower().strip()

        # Simple greetings
        if message_lower in ["hi", "hello", "hey", "sup", "yo"]:
            personality = await self.get_effective_personality(guild_id, user_id)
            if personality.humor > 70:
                return f"Hey there! 👋 What's up?"
            elif personality.formality > 60:
                return "Hello! How may I assist you today?"
            else:
                return "Hi! How's it going?"

        # Simple thanks
        if message_lower in ["thanks", "thank you", "thx", "ty"]:
            personality = await self.get_effective_personality(guild_id, user_id)
            if personality.empathy > 70:
                return "You're very welcome! Happy to help! 😊"
            else:
                return "You're welcome!"

        # Ping/status check
        if message_lower in ["ping", "status", "are you there", "you there?"]:
            return "Pong! 🏓 I'm here and ready to help!"

        return None

    def _generate_cache_key(self, message: str, guild_id: int, user_id: int) -> str:
        """Generate cache key for response caching"""
        # Hash the message content for privacy and key consistency
        message_hash = hashlib.md5(message.encode()).hexdigest()[:8]
        return f"{guild_id}:{user_id}:{message_hash}"

    async def _get_session_state(
        self, guild_id: int, channel_id: int, user_id: int
    ) -> SessionState:
        """Get or create session state with optimization"""
        session_id = f"{guild_id}:{channel_id}:{user_id}"

        # Check cache first
        if session_id in self._session_cache:
            session = self._session_cache[session_id]
            session.last_updated = datetime.now(timezone.utc)
            return session

        # Load from database
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT * FROM session_state WHERE session_id = ?", (session_id,)
                )
                row = cursor.fetchone()

                if row:
                    conversation_window = (
                        fast_json.loads(row[4]) if USE_FAST_JSON else json.loads(row[4])
                    )
                    personality_data = fast_json.loads(row[5]) if row[5] else None
                    personality_snapshot = (
                        PersonalityTraits.from_dict(personality_data)
                        if personality_data
                        else None
                    )

                    session = SessionState(
                        session_id=session_id,
                        guild_id=guild_id,
                        channel_id=channel_id,
                        user_id=user_id,
                        conversation_window=conversation_window,
                        last_updated=datetime.fromisoformat(row[6]),
                        personality_snapshot=personality_snapshot,
                    )
                else:
                    # Create new session
                    session = SessionState(
                        session_id=session_id,
                        guild_id=guild_id,
                        channel_id=channel_id,
                        user_id=user_id,
                    )

        except Exception as e:
            self.logger.error(f"Error loading session state: {e}")
            session = SessionState(
                session_id=session_id,
                guild_id=guild_id,
                channel_id=channel_id,
                user_id=user_id,
            )

        # Cache the session
        self._session_cache[session_id] = session
        return session

    async def _build_enhanced_context(
        self,
        session: SessionState,
        personality: PersonalityTraits,
        current_message: str,
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, str]]:
        """Build enhanced context for AI generation"""

        messages = []

        # System prompt with personality
        system_prompt = self._build_personality_system_prompt(personality, session)
        messages.append({"role": "system", "content": system_prompt})

        # Add conversation history (optimized window)
        recent_messages = session.conversation_window[-self.max_session_window :]
        for msg in recent_messages:
            messages.append(
                {"role": msg.get("role", "user"), "content": msg.get("content", "")}
            )

        return messages

    def _build_personality_system_prompt(
        self, personality: PersonalityTraits, session: SessionState
    ) -> str:
        """Build system prompt with personality traits"""

        # Base prompt
        base = f"You are Astra, an AI assistant with a dynamic personality. Current personality configuration:"

        # Personality traits
        traits = f"""
        - Humor: {personality.humor}/100 {"(playful)" if personality.humor > 70 else "(serious)" if personality.humor < 30 else "(balanced)"}
        - Honesty: {personality.honesty}/100 {"(very direct)" if personality.honesty > 80 else "(diplomatic)" if personality.honesty < 40 else "(balanced)"}
        - Formality: {personality.formality}/100 {"(formal)" if personality.formality > 70 else "(casual)" if personality.formality < 30 else "(balanced)"}
        - Empathy: {personality.empathy}/100 {"(very caring)" if personality.empathy > 80 else "(matter-of-fact)" if personality.empathy < 40 else "(supportive)"}
        - Strictness: {personality.strictness}/100 {"(firm)" if personality.strictness > 70 else "(lenient)" if personality.strictness < 30 else "(fair)"}
        - Initiative: {personality.initiative}/100 {"(proactive)" if personality.initiative > 70 else "(reactive)" if personality.initiative < 30 else "(balanced)"}
        """

        # Mode-specific behavior
        mode_behaviors = {
            PersonalityMode.SOCIAL: "Focus on friendly conversation and community building.",
            PersonalityMode.SECURITY: "Prioritize safety and rule enforcement while remaining helpful.",
            PersonalityMode.MISSION_CONTROL: "Be efficient, precise, and goal-oriented.",
            PersonalityMode.DEVELOPER: "Provide technical insights and problem-solving assistance.",
            PersonalityMode.EMPATHY: "Show deep understanding and emotional support.",
            PersonalityMode.ADAPTIVE: "Adapt your response style to match the conversation context.",
        }

        mode_instruction = mode_behaviors.get(
            personality.mode, "Be helpful and engaging."
        )

        # Behavioral guidelines based on traits
        guidelines = []

        if personality.humor > 60:
            guidelines.append(
                "Use appropriate humor and light-hearted responses when suitable."
            )
        if personality.honesty > 80:
            guidelines.append(
                "Be direct and honest, even if the truth might be uncomfortable."
            )
        if personality.formality < 40:
            guidelines.append("Use casual language and be conversational.")
        elif personality.formality > 70:
            guidelines.append("Maintain proper etiquette and formal language.")
        if personality.empathy > 70:
            guidelines.append(
                "Show understanding and emotional support in your responses."
            )
        if personality.initiative > 70:
            guidelines.append("Offer additional help and suggestions proactively.")

        # Combine all parts
        full_prompt = f"{base}\n{traits}\nMode: {personality.mode.value.title()} - {mode_instruction}\n"
        if guidelines:
            full_prompt += f"Guidelines: {' '.join(guidelines)}\n"
        full_prompt += "Respond naturally while reflecting these personality traits."

        return full_prompt

    async def _apply_personality_enhancements(
        self, response: str, personality: PersonalityTraits, session: SessionState
    ) -> str:
        """Apply personality-specific enhancements to the response"""

        # Humor enhancements
        if personality.humor > 80 and "?" in response:
            # Add occasional emoji for high humor
            import random

            if random.random() < 0.3:  # 30% chance
                emojis = ["😄", "😊", "🤔", "👍", "✨"]
                response += f" {random.choice(emojis)}"

        # Formality adjustments
        if personality.formality < 30:
            # Make response more casual
            response = response.replace("I would suggest", "I'd say")
            response = response.replace("It would be", "It'd be")
            response = response.replace("you are", "you're")
        elif personality.formality > 80:
            # Make response more formal
            response = response.replace("don't", "do not")
            response = response.replace("can't", "cannot")
            response = response.replace("won't", "will not")

        # Empathy enhancements
        if personality.empathy > 80:
            # Add supportive language where appropriate
            if any(
                word in response.lower()
                for word in ["sorry", "problem", "issue", "trouble"]
            ):
                if not any(
                    phrase in response.lower()
                    for phrase in ["i understand", "i can imagine"]
                ):
                    response = f"I understand this might be frustrating. {response}"

        # Initiative enhancements
        if personality.initiative > 70 and "?" not in response:
            # Add helpful follow-up suggestions occasionally
            import random

            if random.random() < 0.2:  # 20% chance
                response += " Is there anything else I can help you with?"

        return response

    async def _update_session_state(
        self, session: SessionState, user_message: str, ai_response: str
    ):
        """Update session state with new conversation turn"""

        now = datetime.now(timezone.utc)

        # Add messages to conversation window
        session.conversation_window.append(
            {"role": "user", "content": user_message, "timestamp": now.isoformat()}
        )

        session.conversation_window.append(
            {"role": "assistant", "content": ai_response, "timestamp": now.isoformat()}
        )

        # Trim window if too large
        if len(session.conversation_window) > self.max_session_window * 2:
            session.conversation_window = session.conversation_window[
                -self.max_session_window :
            ]

        session.last_updated = now

        # Save to database (async to avoid blocking)
        asyncio.create_task(self._save_session_state(session))

    async def _save_session_state(self, session: SessionState):
        """Save session state to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conversation_json = (
                    fast_json.dumps(session.conversation_window)
                    if USE_FAST_JSON
                    else json.dumps(session.conversation_window)
                )
                personality_json = (
                    fast_json.dumps(session.personality_snapshot.to_dict())
                    if session.personality_snapshot
                    else None
                )

                conn.execute(
                    """
                    INSERT OR REPLACE INTO session_state 
                    (session_id, guild_id, channel_id, user_id, conversation_window, personality_snapshot, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        session.session_id,
                        session.guild_id,
                        session.channel_id,
                        session.user_id,
                        conversation_json,
                        personality_json,
                        session.last_updated.isoformat(),
                    ),
                )
                conn.commit()

        except Exception as e:
            self.logger.error(f"Error saving session state: {e}")

    async def adapt_personality(
        self,
        guild_id: int,
        signal: AdaptationSignal,
        payload: Dict[str, Any],
        reason: str = "",
    ) -> bool:
        """Apply personality adaptation based on signals (from specification)"""

        if not self.adaptation_enabled:
            return False

        # Check cooldown
        if guild_id in self.last_adaptation:
            time_since_last = (
                datetime.now(timezone.utc) - self.last_adaptation[guild_id]
            )
            if time_since_last.total_seconds() < self.adaptation_cooldown:
                self.logger.debug(f"Adaptation cooldown active for guild {guild_id}")
                return False

        try:
            # Generate adaptation delta based on signal
            delta_profile = self._generate_adaptation_delta(signal, payload)

            if not delta_profile:
                return False

            # Create adaptation event
            event_id = f"{guild_id}_{signal.value}_{int(time.time())}"
            expires_at = datetime.now(timezone.utc) + timedelta(
                minutes=30
            )  # Default 30 minutes

            event = AdaptationEvent(
                id=event_id,
                guild_id=guild_id,
                event_type=signal,
                payload=payload,
                delta_profile=delta_profile,
                applied_at=datetime.now(timezone.utc),
                expires_at=expires_at,
                reason=reason or f"Auto-adaptation for {signal.value}",
            )

            # Save to database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO adaptation_events 
                    (id, guild_id, event_type, payload, delta_profile, applied_at, expires_at, status, priority, reason, applied_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        event.id,
                        event.guild_id,
                        event.event_type.value,
                        (
                            fast_json.dumps(event.payload)
                            if USE_FAST_JSON
                            else json.dumps(event.payload)
                        ),
                        (
                            fast_json.dumps(event.delta_profile)
                            if USE_FAST_JSON
                            else json.dumps(event.delta_profile)
                        ),
                        event.applied_at.isoformat(),
                        event.expires_at.isoformat() if event.expires_at else None,
                        event.status,
                        event.priority,
                        event.reason,
                        event.applied_by,
                    ),
                )
                conn.commit()

            # Update cache
            if guild_id not in self._adaptation_cache:
                self._adaptation_cache[guild_id] = []
            self._adaptation_cache[guild_id].append(event)

            # Clear personality cache to force refresh
            cache_keys_to_remove = [
                key
                for key in self._personality_cache.keys()
                if key.startswith(f"{guild_id}:")
            ]
            for key in cache_keys_to_remove:
                del self._personality_cache[key]

            # Update cooldown
            self.last_adaptation[guild_id] = datetime.now(timezone.utc)
            self.adaptation_events += 1

            self.logger.info(
                f"🔄 Applied adaptation for guild {guild_id}: {signal.value} - {reason}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error applying adaptation: {e}")
            return False

    def _generate_adaptation_delta(
        self, signal: AdaptationSignal, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate adaptation delta based on signal type (from specification)"""

        deltas = {
            AdaptationSignal.SPAM_SPIKE: {
                "strictness": 25,
                "initiative": 10,
                "humor": -30,
                "mode": "security",
            },
            AdaptationSignal.EVENT_START: {
                "humor": 20,
                "empathy": 15,
                "initiative": 25,
                "mode": "social",
            },
            AdaptationSignal.QUIET_HOURS: {
                "formality": 15,
                "humor": -20,
                "empathy": 10,
            },
            AdaptationSignal.CONFLICT_DETECTED: {
                "empathy": 30,
                "strictness": 20,
                "formality": 15,
                "mode": "empathy",
            },
            AdaptationSignal.LOW_ENGAGEMENT: {
                "humor": 25,
                "initiative": 30,
                "empathy": 15,
            },
            AdaptationSignal.RAID_DETECTED: {
                "strictness": 40,
                "formality": 20,
                "humor": -40,
                "mode": "security",
            },
            AdaptationSignal.LINK_SPIKE: {"strictness": 15, "honesty": 10},
            AdaptationSignal.BOT_ANOMALY: {"strictness": 20, "formality": 15},
        }

        return deltas.get(signal, {})

    async def set_guild_personality(self, guild_id: int, **traits) -> bool:
        """Set guild personality traits"""
        try:
            # Validate traits
            valid_traits = [
                "humor",
                "honesty",
                "formality",
                "empathy",
                "strictness",
                "initiative",
                "mode",
            ]
            filtered_traits = {k: v for k, v in traits.items() if k in valid_traits}

            # Validate ranges
            for trait, value in filtered_traits.items():
                if trait == "mode":
                    if value not in [mode.value for mode in PersonalityMode]:
                        return False
                else:
                    if not (0 <= value <= 100):
                        return False

            # Update database
            with sqlite3.connect(self.db_path) as conn:
                # Get existing personality or create new
                cursor = conn.execute(
                    "SELECT * FROM guild_personalities WHERE guild_id = ?", (guild_id,)
                )
                existing = cursor.fetchone()

                if existing:
                    # Update existing
                    update_fields = []
                    update_values = []
                    for trait, value in filtered_traits.items():
                        update_fields.append(f"{trait} = ?")
                        update_values.append(value)

                    if update_fields:
                        update_values.append(datetime.now(timezone.utc).isoformat())
                        update_values.append(guild_id)

                        conn.execute(
                            f"""
                            UPDATE guild_personalities 
                            SET {', '.join(update_fields)}, updated_at = ?
                            WHERE guild_id = ?
                        """,
                            update_values,
                        )
                else:
                    # Create new
                    personality = PersonalityTraits()
                    for trait, value in filtered_traits.items():
                        setattr(personality, trait, value)

                    conn.execute(
                        """
                        INSERT INTO guild_personalities 
                        (guild_id, humor, honesty, formality, empathy, strictness, initiative, mode, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            guild_id,
                            personality.humor,
                            personality.honesty,
                            personality.formality,
                            personality.empathy,
                            personality.strictness,
                            personality.initiative,
                            personality.mode.value,
                            datetime.now(timezone.utc).isoformat(),
                        ),
                    )

                conn.commit()

            # Clear cache
            cache_keys_to_remove = [
                key
                for key in self._personality_cache.keys()
                if key.startswith(f"{guild_id}:")
            ]
            for key in cache_keys_to_remove:
                del self._personality_cache[key]

            self.logger.info(
                f"✅ Updated personality for guild {guild_id}: {filtered_traits}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error setting guild personality: {e}")
            return False

    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        uptime = time.time() - self.start_time
        cache_hit_rate = (
            self.cache_hits / max(self.cache_hits + self.cache_misses, 1) * 100
        )

        return {
            "uptime_seconds": uptime,
            "requests_processed": self.requests_processed,
            "cache_hit_rate": cache_hit_rate,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "adaptation_events": self.adaptation_events,
            "cache_sizes": {
                "personalities": len(self._personality_cache),
                "sessions": len(self._session_cache),
                "responses": len(self._response_cache),
                "adaptations": sum(
                    len(events) for events in self._adaptation_cache.values()
                ),
            },
            "memory_usage": {
                "personality_cache_mb": len(str(self._personality_cache).encode())
                / 1024
                / 1024,
                "session_cache_mb": len(str(self._session_cache).encode())
                / 1024
                / 1024,
                "response_cache_mb": len(str(self._response_cache).encode())
                / 1024
                / 1024,
            },
        }

    async def cleanup(self):
        """Cleanup resources"""
        try:
            # Save all cached sessions
            for session in self._session_cache.values():
                await self._save_session_state(session)

            # Close AI client
            if self.ai_client:
                await self.ai_client.close()

            self.logger.info("🧹 AI Coordinator cleanup completed")

        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")


# Global instance
_ai_coordinator: Optional[OptimizedAICoordinator] = None


async def get_ai_coordinator(bot=None) -> OptimizedAICoordinator:
    """Get or create the global AI coordinator instance"""
    global _ai_coordinator
    if _ai_coordinator is None:
        _ai_coordinator = OptimizedAICoordinator(bot)
        await _ai_coordinator.initialize()
    return _ai_coordinator


async def initialize_ai_coordinator(bot=None) -> OptimizedAICoordinator:
    """Initialize the global AI coordinator"""
    global _ai_coordinator
    _ai_coordinator = OptimizedAICoordinator(bot)
    await _ai_coordinator.initialize()
    return _ai_coordinator
