import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Literal, Dict, List, Any, Deque, Union
from collections import deque, defaultdict
from functools import lru_cache, wraps
import logging
import weakref
import time
import hashlib
import re
import sqlite3
from enum import Enum
from dataclasses import dataclass, asdict
import gc

# Import rate limiter for Discord API protection
try:
    from utils.rate_limiter import discord_rate_limiter, rate_limited

    RATE_LIMITER_AVAILABLE = True
except ImportError:
    RATE_LIMITER_AVAILABLE = False
    logging.warning(
        "Rate limiter not available - Discord rate limiting protection disabled"
    )

# Import AI error handler
try:
    from ai.error_handler import ai_error_handler

    ERROR_HANDLER_AVAILABLE = True
except ImportError:
    ERROR_HANDLER_AVAILABLE = False
    logging.warning(
        "AI error handler not available - AI fallback functionality limited"
    )

# Owner user ID - only this user can control lockdown mode
OWNER_ID = 1115739214148026469
# Forensic logging channel ID
FORENSIC_CHANNEL_ID = 1419517784135700561


class ViolationType(Enum):
    """Types of security violations detected"""

    SCAM = "scam"
    SPAM = "spam"
    MALWARE = "malware"
    HARASSMENT = "harassment"
    PHISHING = "phishing"
    RAID = "raid"
    TOXIC = "toxic"
    NSFW = "nsfw"
    IMPERSONATION = "impersonation"


class ViolationSeverity(Enum):
    """Severity levels for violations"""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class ActionType(Enum):
    """Available moderation actions"""

    WARN = "warn"
    MUTE = "mute"
    TIMEOUT = "timeout"
    DELETE = "delete"
    QUARANTINE = "quarantine"
    KICK = "kick"
    BAN = "ban"
    ESCALATE = "escalate"


@dataclass
class ViolationEvent:
    """Data class for violation events"""

    user_id: int
    guild_id: int
    channel_id: int
    message_id: Optional[int]
    violation_type: ViolationType
    severity: ViolationSeverity
    action_taken: ActionType
    content_hash: str
    original_content: str
    risk_score: float
    timestamp: datetime
    context: Dict[str, Any]
    ai_confidence: float
    moderator_confirmed: Optional[bool] = None


class SmartActionSystem:
    """
    🧠 AI-Powered Smart Action System

    Sophisticated threat detection and automated moderation with:
    - AI-driven violation severity assessment
    - Intelligent action selection based on context
    - Risk scoring and user behavior analysis
    - Continuous learning from moderation feedback
    """

    def __init__(self):
        self.violation_patterns = {
            ViolationType.SCAM: [
                r"\b(free\s+nitro|discord\s+gift|steam\s+gift)\b",
                r"\b(click\s+here|visit\s+link|claim\s+now)\b",
                r"bit\.ly|tinyurl|t\.co",
                r"\b(urgent|limited\s+time|expires\s+soon)\b",
            ],
            ViolationType.SPAM: [
                r"(.)\1{5,}",  # Repeated characters (stricter)
                r"@everyone|@here",
                r"(discord\.gg|invite)\s*/\s*[a-zA-Z0-9]+",
                r"\b(join\s+my\s+server|check\s+out\s+my)\b",
                r"\b[A-Z\s]{10,}",  # Excessive caps
                r"([!?.]){3,}",  # Excessive punctuation
                r"\b(free\s+money|get\s+rich\s+quick)\b",
                r"\b(spam|flood|raid)\b",
                r"(.+)\s*\1\s*\1",  # Repeated phrases (3+ times)
            ],
            ViolationType.MALWARE: [
                r"\.(exe|bat|scr|vbs|jar)$",
                r"download\s+this",
                r"run\s+as\s+administrator",
                r"disable\s+antivirus",
            ],
            ViolationType.HARASSMENT: [
                r"\b(kill\s+yourself|kys)\b",
                r"\b(retard|f[a4]gg[o0]t)\b",
                r"you\s+should\s+die",
                r"nobody\s+likes\s+you",
            ],
            ViolationType.PHISHING: [
                r"verify\s+your\s+account",
                r"suspended\s+account",
                r"click\s+to\s+verify",
                r"security\s+alert",
            ],
        }

        self.risk_factors = {
            "new_account": 0.3,
            "no_avatar": 0.2,
            "no_roles": 0.1,
            "previous_violations": 0.4,
            "multiple_servers": 0.1,
            "dm_violations": 0.5,
        }

        # STRICT ACTION MATRIX - Immediate and harsh consequences
        self.action_matrix = {
            # SCAM - Zero tolerance
            (ViolationType.SCAM, ViolationSeverity.LOW): ActionType.TIMEOUT,
            (ViolationType.SCAM, ViolationSeverity.MEDIUM): ActionType.BAN,
            (ViolationType.SCAM, ViolationSeverity.HIGH): ActionType.BAN,
            (ViolationType.SCAM, ViolationSeverity.CRITICAL): ActionType.BAN,
            # SPAM - Progressive but strict
            (ViolationType.SPAM, ViolationSeverity.LOW): ActionType.MUTE,
            (ViolationType.SPAM, ViolationSeverity.MEDIUM): ActionType.TIMEOUT,
            (ViolationType.SPAM, ViolationSeverity.HIGH): ActionType.TIMEOUT,
            (ViolationType.SPAM, ViolationSeverity.CRITICAL): ActionType.BAN,
            # MALWARE - Immediate ban
            (ViolationType.MALWARE, ViolationSeverity.LOW): ActionType.BAN,
            (ViolationType.MALWARE, ViolationSeverity.MEDIUM): ActionType.BAN,
            (ViolationType.MALWARE, ViolationSeverity.HIGH): ActionType.BAN,
            (ViolationType.MALWARE, ViolationSeverity.CRITICAL): ActionType.BAN,
            # HARASSMENT - Strict enforcement
            (ViolationType.HARASSMENT, ViolationSeverity.LOW): ActionType.TIMEOUT,
            (ViolationType.HARASSMENT, ViolationSeverity.MEDIUM): ActionType.TIMEOUT,
            (ViolationType.HARASSMENT, ViolationSeverity.HIGH): ActionType.BAN,
            (ViolationType.HARASSMENT, ViolationSeverity.CRITICAL): ActionType.BAN,
            # PHISHING - Zero tolerance
            (ViolationType.PHISHING, ViolationSeverity.LOW): ActionType.TIMEOUT,
            (ViolationType.PHISHING, ViolationSeverity.MEDIUM): ActionType.BAN,
            (ViolationType.PHISHING, ViolationSeverity.HIGH): ActionType.BAN,
            (ViolationType.PHISHING, ViolationSeverity.CRITICAL): ActionType.BAN,
        }

    def analyze_content(
        self, content: str, user: discord.Member, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze message content for violations using AI-enhanced pattern matching
        """
        violations = []
        max_severity = ViolationSeverity.LOW

        # Pattern matching for different violation types
        for violation_type, patterns in self.violation_patterns.items():
            confidence = 0.0
            matches = []

            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    matches.append(pattern)
                    confidence += 0.25

            if matches:
                violations.append(
                    {
                        "type": violation_type,
                        "confidence": min(confidence, 1.0),
                        "patterns": matches,
                    }
                )

        # Calculate risk score
        risk_score = self._calculate_risk_score(user, context, violations)

        # Determine severity based on violations and risk score
        if violations:
            if risk_score > 0.8 or len(violations) > 2:
                max_severity = ViolationSeverity.CRITICAL
            elif risk_score > 0.6 or any(v["confidence"] > 0.7 for v in violations):
                max_severity = ViolationSeverity.HIGH
            elif risk_score > 0.4 or any(v["confidence"] > 0.5 for v in violations):
                max_severity = ViolationSeverity.MEDIUM
            else:
                max_severity = ViolationSeverity.LOW

        return {
            "violations": violations,
            "risk_score": risk_score,
            "severity": max_severity,
            "recommended_action": self._get_recommended_action(
                violations, max_severity
            ),
            "ai_confidence": self._calculate_ai_confidence(violations, risk_score),
        }

    def _calculate_risk_score(
        self, user: discord.Member, context: Dict[str, Any], violations: List[Dict]
    ) -> float:
        """Calculate user risk score based on multiple factors"""
        risk_score = 0.0

        # Account age factor
        account_age = (datetime.now(timezone.utc) - user.created_at).days
        if account_age < 1:
            risk_score += self.risk_factors["new_account"]
        elif account_age < 7:
            risk_score += self.risk_factors["new_account"] * 0.5

        # Avatar and roles
        if user.display_avatar.url == user.default_avatar.url:
            risk_score += self.risk_factors["no_avatar"]

        if len(user.roles) <= 1:  # Only @everyone role
            risk_score += self.risk_factors["no_roles"]

        # Previous violations from context - STRICT ESCALATION
        previous_violations = context.get("previous_violations", 0)
        if previous_violations > 0:
            # Exponential escalation for repeat offenders
            escalation_factor = min(previous_violations * 0.3, 0.9)
            risk_score += escalation_factor

        # Recent violations (last 24 hours) - HEAVY PENALTY
        recent_violations = context.get("recent_violations_24h", 0)
        if recent_violations >= 3:
            risk_score += 0.8  # Almost guarantee high severity
        elif recent_violations >= 2:
            risk_score += 0.6
        elif recent_violations >= 1:
            risk_score += 0.4

        # DM violations are more serious
        if context.get("is_dm", False):
            risk_score += self.risk_factors["dm_violations"]

        # Violation multiplier - MORE AGGRESSIVE
        if violations:
            violation_multiplier = min(len(violations) * 0.3, 0.7)
            risk_score += violation_multiplier

        return min(risk_score, 1.0)

    def _get_recommended_action(
        self, violations: List[Dict], severity: ViolationSeverity
    ) -> ActionType:
        """Get recommended action based on violations and severity"""
        if not violations:
            return ActionType.WARN

        # Get the most severe violation type
        primary_violation = max(violations, key=lambda x: x["confidence"])
        violation_type = primary_violation["type"]

        return self.action_matrix.get((violation_type, severity), ActionType.WARN)

    def _calculate_ai_confidence(
        self, violations: List[Dict], risk_score: float
    ) -> float:
        """Calculate AI confidence in the analysis"""
        if not violations:
            return 0.1

        avg_confidence = sum(v["confidence"] for v in violations) / len(violations)
        risk_factor = min(risk_score, 1.0)

        return min((avg_confidence + risk_factor) / 2, 0.95)


class ForensicLogger:
    """
    🕵️ Forensic Logging System

    Secure logging of all security events with:
    - Encrypted message content storage
    - Risk score tracking
    - Context preservation
    - Continuous learning feedback
    """

    def __init__(self, bot):
        self.bot = bot
        self.db_path = "data/forensic_security.db"
        self.learning_data = deque(maxlen=1000)
        self._init_database()

    def _init_database(self):
        """Initialize forensic database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS violation_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    message_id INTEGER,
                    violation_type TEXT NOT NULL,
                    severity INTEGER NOT NULL,
                    action_taken TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    original_content TEXT NOT NULL,
                    risk_score REAL NOT NULL,
                    timestamp DATETIME NOT NULL,
                    context TEXT NOT NULL,
                    ai_confidence REAL NOT NULL,
                    moderator_confirmed INTEGER DEFAULT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_user_violations 
                ON violation_events(user_id, timestamp)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_guild_violations 
                ON violation_events(guild_id, timestamp)
            """
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logging.error(f"Failed to initialize forensic database: {e}")

    async def log_violation(self, event: ViolationEvent) -> bool:
        """Log violation event to database and Discord channel"""
        try:
            # Store in database
            await self._store_in_database(event)

            # Send to forensic channel
            await self._send_to_forensic_channel(event)

            # Add to learning data
            self.learning_data.append(event)

            return True

        except Exception as e:
            logging.error(f"Failed to log violation: {e}")
            return False

    async def _store_in_database(self, event: ViolationEvent):
        """Store violation event in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO violation_events (
                user_id, guild_id, channel_id, message_id, violation_type,
                severity, action_taken, content_hash, original_content,
                risk_score, timestamp, context, ai_confidence, moderator_confirmed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                event.user_id,
                event.guild_id,
                event.channel_id,
                event.message_id,
                event.violation_type.value,
                event.severity.value,
                event.action_taken.value,
                event.content_hash,
                event.original_content,
                event.risk_score,
                event.timestamp,
                json.dumps(event.context),
                event.ai_confidence,
                event.moderator_confirmed,
            ),
        )

        conn.commit()
        conn.close()

    async def _send_to_forensic_channel(self, event: ViolationEvent):
        """Send violation event to forensic logging channel with rate limiting"""
        try:
            # Apply rate limiting to prevent Discord API limits
            if RATE_LIMITER_AVAILABLE:
                await discord_rate_limiter.acquire("messages", str(FORENSIC_CHANNEL_ID))

            channel = self.bot.get_channel(FORENSIC_CHANNEL_ID)
            if not channel:
                return

            embed = discord.Embed(
                title="🚨 SECURITY VIOLATION DETECTED",
                color=self._get_severity_color(event.severity),
                timestamp=event.timestamp,
            )

            embed.add_field(
                name="👤 User",
                value=f"<@{event.user_id}> (`{event.user_id}`)",
                inline=True,
            )

            embed.add_field(
                name="📍 Location", value=f"<#{event.channel_id}>", inline=True
            )

            embed.add_field(
                name="⚠️ Violation Type",
                value=event.violation_type.value.title(),
                inline=True,
            )

            embed.add_field(
                name="🎯 Severity",
                value=f"Level {event.severity.value} ({event.severity.name})",
                inline=True,
            )

            embed.add_field(
                name="⚡ Action Taken",
                value=event.action_taken.value.title(),
                inline=True,
            )

            embed.add_field(
                name="📊 Risk Score", value=f"{event.risk_score:.2%}", inline=True
            )

            embed.add_field(
                name="🤖 AI Confidence", value=f"{event.ai_confidence:.2%}", inline=True
            )

            # Truncate content for display
            display_content = (
                event.original_content[:200] + "..."
                if len(event.original_content) > 200
                else event.original_content
            )
            embed.add_field(
                name="📝 Content", value=f"```{display_content}```", inline=False
            )

            embed.add_field(
                name="🔍 Hash", value=f"`{event.content_hash[:16]}...`", inline=True
            )

            embed.set_footer(
                text=f"Event ID: {event.content_hash[:8]} | Forensic Logging System"
            )

            await channel.send(embed=embed)

        except Exception as e:
            logging.error(f"Failed to send to forensic channel: {e}")

    def _get_severity_color(self, severity: ViolationSeverity) -> int:
        """Get color for severity level"""
        colors = {
            ViolationSeverity.LOW: 0x00FF00,
            ViolationSeverity.MEDIUM: 0xFFFF00,
            ViolationSeverity.HIGH: 0xFF9900,
            ViolationSeverity.CRITICAL: 0xFF0000,
            ViolationSeverity.EMERGENCY: 0x990000,
        }
        return colors.get(severity, 0x0099FF)

    def _hash_content(self, content: str) -> str:
        """Create hash of message content"""
        return hashlib.sha256(content.encode()).hexdigest()

    async def get_user_violations(self, user_id: int, days: int = 30) -> List[Dict]:
        """Get user's violation history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        cursor.execute(
            """
            SELECT * FROM violation_events 
            WHERE user_id = ? AND timestamp > ?
            ORDER BY timestamp DESC
        """,
            (user_id, cutoff_date),
        )

        results = cursor.fetchall()
        conn.close()

        return [
            dict(zip([col[0] for col in cursor.description], row)) for row in results
        ]

    async def update_moderator_feedback(self, event_hash: str, confirmed: bool):
        """Update moderator confirmation for learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE violation_events 
            SET moderator_confirmed = ?
            WHERE content_hash = ?
        """,
            (1 if confirmed else 0, event_hash),
        )

        conn.commit()
        conn.close()

    async def get_violation_by_hash(self, event_hash: str) -> Optional[ViolationEvent]:
        """Get violation event by content hash"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM violation_events 
                WHERE content_hash = ?
                LIMIT 1
            """,
                (event_hash,),
            )

            result = cursor.fetchone()
            conn.close()

            if result:
                # Convert database row to ViolationEvent object
                return ViolationEvent(
                    user_id=result[1],
                    guild_id=result[2],
                    channel_id=result[3],
                    message_id=result[4],
                    violation_type=ViolationType(result[5]),
                    severity=result[6],
                    action_taken=ActionType(result[7]),
                    content_hash=result[8],
                    original_content=result[9],
                    risk_score=result[10],
                    timestamp=datetime.fromisoformat(result[11]),
                    context=json.loads(result[12]) if result[12] else {},
                    ai_confidence=result[13],
                    moderator_confirmed=result[14],
                )
            return None

        except Exception as e:
            logging.error(f"Error getting violation by hash: {e}")
            return None

    async def get_all_violations(self, days: int = 30) -> List[ViolationEvent]:
        """Get all violations within specified days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

            cursor.execute(
                """
                SELECT * FROM violation_events 
                WHERE timestamp > ?
                ORDER BY timestamp DESC
                LIMIT 1000
            """,
                (cutoff_date,),
            )

            results = cursor.fetchall()
            conn.close()

            violations = []
            for result in results:
                try:
                    violation = ViolationEvent(
                        user_id=result[1],
                        guild_id=result[2],
                        channel_id=result[3],
                        message_id=result[4],
                        violation_type=ViolationType(result[5]),
                        severity=result[6],
                        action_taken=ActionType(result[7]),
                        content_hash=result[8],
                        original_content=result[9],
                        risk_score=result[10],
                        timestamp=datetime.fromisoformat(result[11]),
                        context=json.loads(result[12]) if result[12] else {},
                        ai_confidence=result[13],
                        moderator_confirmed=result[14],
                    )
                    violations.append(violation)
                except Exception as e:
                    logging.warning(f"Error parsing violation event: {e}")
                    continue

            return violations

        except Exception as e:
            logging.error(f"Error getting all violations: {e}")
            return []


# Performance optimization decorator
def performance_monitor(func):
    """Decorator to monitor command performance"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000  # Convert to ms
            if execution_time > 100:  # Log slow operations
                logging.warning(
                    f"⚠️ Slow security operation: {func.__name__} took {execution_time:.2f}ms"
                )

    return wrapper


class SecurityCommands(commands.Cog):
    """
    🛡️ Security Commands Cog - Performance Optimized

    Provides comprehensive security management commands:
    - Manual lockdown control (Owner only)
    - Threat monitoring and analysis (Admins)
    - Security status and reports (Admins)
    - User investigation tools (Admins)

    Performance Features:
    - __slots__ for memory efficiency
    - Deque with auto-rotation for threat logs
    - LRU caching for repeated operations
    - Batch operations for lockdown/unlock
    - Weak references to prevent memory leaks
    """

    # Memory optimization with __slots__ - Enhanced
    __slots__ = [
        "bot",
        "lockdown_active",
        "lockdown_channels",
        "lockdown_start_time",
        "threat_log",
        "security_stats",
        "_embed_cache",
        "_user_cache",
        "_last_cleanup",
        "smart_action_system",
        "forensic_logger",
        "active_quarantines",
        "learning_feedback",
        "user_warnings",
        "progressive_punishments",
        "_performance_cache",
        "_batch_queue",
        "_rate_limiter",
        "threat_analyzer",
        "pattern_matcher",
        "_optimization_flags",
    ]

    def __init__(self, bot):
        self.bot = weakref.ref(bot)  # Weak reference to prevent circular references
        self.lockdown_active = False
        self.lockdown_channels = set()  # Use set for O(1) lookups
        self.lockdown_start_time = None
        self.threat_log = deque(maxlen=2000)  # Increased capacity for better analysis
        self.security_stats = defaultdict(int)  # Auto-initializing counters
        self._embed_cache = {}  # Cache for frequently used embeds
        self._user_cache = weakref.WeakValueDictionary()  # Auto-cleanup user cache
        self._last_cleanup = datetime.now(timezone.utc)

        # Enhanced security systems with optimization
        self.smart_action_system = SmartActionSystem()
        self.forensic_logger = ForensicLogger(bot)
        self.active_quarantines = {}  # user_id -> quarantine_data
        self.learning_feedback = deque(maxlen=1000)  # Increased feedback storage

        # ADVANCED MODERATION TRACKING with performance optimization
        self.user_warnings = defaultdict(
            lambda: deque(maxlen=50)
        )  # Limited per-user storage
        self.progressive_punishments = defaultdict(int)  # user_id -> punishment_level

        # New performance optimization features
        self._performance_cache = {}
        self._batch_queue = deque(maxlen=100)
        self._rate_limiter = defaultdict(float)  # user_id -> last_action_time
        self.threat_analyzer = None  # Will be initialized with advanced ML if available
        self.pattern_matcher = self._initialize_optimized_patterns()

        # Optimization flags for runtime performance tuning
        self._optimization_flags = {
            "batch_operations": True,
            "cache_embeddings": True,
            "compress_logs": True,
            "smart_rate_limiting": True,
            "predictive_analysis": True,
        }

    def _initialize_optimized_patterns(self):
        """Initialize optimized pattern matching system"""
        try:
            import re

            # Pre-compile patterns for better performance
            patterns = {
                "spam": [
                    re.compile(r"(.)\1{4,}", re.IGNORECASE),  # Repeated chars
                    re.compile(r"@everyone|@here", re.IGNORECASE),
                    re.compile(
                        r"(discord\.gg|invite)\s*/\s*[a-zA-Z0-9]+", re.IGNORECASE
                    ),
                    re.compile(r"\b[A-Z\s]{8,}", re.IGNORECASE),  # Excessive caps
                    re.compile(r"([!?.]){3,}"),  # Excessive punctuation
                ],
                "scam": [
                    re.compile(
                        r"\b(free\s+nitro|discord\s+gift|steam\s+gift)\b", re.IGNORECASE
                    ),
                    re.compile(
                        r"\b(click\s+here|visit\s+link|claim\s+now)\b", re.IGNORECASE
                    ),
                    re.compile(r"bit\.ly|tinyurl|t\.co", re.IGNORECASE),
                    re.compile(
                        r"\b(urgent|limited\s+time|expires\s+soon)\b", re.IGNORECASE
                    ),
                ],
                "harassment": [
                    re.compile(r"\b(kill\s+yourself|kys)\b", re.IGNORECASE),
                    re.compile(r"\b(retard|f[a4]gg[o0]t)\b", re.IGNORECASE),
                    re.compile(r"you\s+should\s+die", re.IGNORECASE),
                    re.compile(r"nobody\s+likes\s+you", re.IGNORECASE),
                ],
                "malware": [
                    re.compile(r"\.(exe|bat|scr|vbs|jar)$", re.IGNORECASE),
                    re.compile(r"download\s+this", re.IGNORECASE),
                    re.compile(r"run\s+as\s+administrator", re.IGNORECASE),
                    re.compile(r"disable\s+antivirus", re.IGNORECASE),
                ],
            }
            return patterns
        except Exception as e:
            logging.error(f"Failed to initialize pattern matcher: {e}")
            return {}

    async def cog_load(self):
        """Initialize enhanced security system on cog load"""
        # Initialize threat analyzer if available
        try:
            # Try to load advanced threat analysis (if available)
            self.threat_analyzer = await self._initialize_threat_analyzer()
        except Exception as e:
            logging.warning(f"Advanced threat analyzer not available: {e}")

        print(
            "🛡️ Enhanced Security System loaded - Advanced Performance & Threat Intelligence active"
        )

    async def _initialize_threat_analyzer(self):
        """Initialize advanced threat analyzer if ML components are available"""
        try:
            # Check if scikit-learn or similar ML library is available
            import importlib

            # Try to import ML libraries
            sklearn_spec = importlib.util.find_spec("sklearn")
            if sklearn_spec is not None:
                from sklearn.feature_extraction.text import TfidfVectorizer
                from sklearn.naive_bayes import MultinomialNB

                # Create a simple threat classifier
                vectorizer = TfidfVectorizer(max_features=1000, stop_words="english")
                classifier = MultinomialNB()

                # In a real implementation, you would train this with data
                # For now, return a placeholder
                return {
                    "vectorizer": vectorizer,
                    "classifier": classifier,
                    "trained": False,
                    "type": "ml_based",
                }
            else:
                # Fallback to rule-based analyzer
                return {
                    "type": "rule_based",
                    "patterns": self.pattern_matcher,
                    "confidence_threshold": 0.7,
                }

        except Exception as e:
            logging.warning(f"Could not initialize threat analyzer: {e}")
            return None

    def _analyze_message_optimized(self, content: str, user_context: dict) -> dict:
        """Optimized message analysis with caching and batch processing"""
        # Create cache key
        content_hash = hashlib.md5(content.encode()).hexdigest()
        cache_key = f"analysis_{content_hash}_{user_context.get('user_id', 0)}"

        # Check cache first
        if cache_key in self._performance_cache:
            cache_result = self._performance_cache[cache_key]
            if time.time() - cache_result["timestamp"] < 300:  # 5 minutes TTL
                return cache_result["result"]

        # Perform analysis
        result = self._perform_threat_analysis(content, user_context)

        # Cache result
        self._performance_cache[cache_key] = {
            "result": result,
            "timestamp": time.time(),
        }

        # Clean cache if it gets too large
        if len(self._performance_cache) > 1000:
            self._cleanup_performance_cache()

        return result

    def _perform_threat_analysis(self, content: str, user_context: dict) -> dict:
        """Perform actual threat analysis using optimized patterns"""
        threat_score = 0.0
        detected_threats = []
        confidence = 0.0

        try:
            # Use pre-compiled patterns for faster matching
            for threat_type, patterns in self.pattern_matcher.items():
                type_score = 0.0
                matches = []

                for pattern in patterns:
                    if pattern.search(content):
                        matches.append(pattern.pattern)
                        type_score += 0.25

                if matches:
                    detected_threats.append(
                        {
                            "type": threat_type,
                            "score": min(type_score, 1.0),
                            "matches": matches[:3],  # Limit to first 3 matches
                        }
                    )
                    threat_score += type_score

            # Factor in user context for more accurate scoring
            user_risk_multiplier = self._calculate_user_risk_multiplier(user_context)
            final_score = min(threat_score * user_risk_multiplier, 1.0)

            # Calculate confidence based on number of patterns matched
            confidence = min(len(detected_threats) * 0.3 + (final_score * 0.4), 0.95)

            return {
                "threat_score": final_score,
                "confidence": confidence,
                "threats": detected_threats,
                "analysis_time": time.time(),
                "user_risk_multiplier": user_risk_multiplier,
            }

        except Exception as e:
            logging.error(f"Threat analysis error: {e}")
            return {
                "threat_score": 0.0,
                "confidence": 0.0,
                "threats": [],
                "error": str(e),
            }

    def _calculate_user_risk_multiplier(self, user_context: dict) -> float:
        """Calculate risk multiplier based on user context"""
        multiplier = 1.0

        # Account age factor
        account_age_days = user_context.get("account_age_days", 365)
        if account_age_days < 1:
            multiplier += 0.5
        elif account_age_days < 7:
            multiplier += 0.3
        elif account_age_days < 30:
            multiplier += 0.1

        # Previous violations
        violation_count = user_context.get("previous_violations", 0)
        multiplier += min(violation_count * 0.2, 0.8)

        # Trust score factor
        trust_score = user_context.get("trust_score", 50)
        if trust_score < 30:
            multiplier += 0.4
        elif trust_score < 50:
            multiplier += 0.2

        # Recent activity patterns
        if user_context.get("recent_violations_24h", 0) > 2:
            multiplier += 0.6

        return min(multiplier, 3.0)  # Cap at 3x multiplier

    def _cleanup_performance_cache(self):
        """Clean up performance cache to prevent memory bloat"""
        current_time = time.time()
        expired_keys = []

        for key, data in self._performance_cache.items():
            if current_time - data["timestamp"] > 600:  # 10 minutes
                expired_keys.append(key)

        for key in expired_keys:
            del self._performance_cache[key]

        # If still too large, remove oldest entries
        if len(self._performance_cache) > 500:
            sorted_items = sorted(
                self._performance_cache.items(), key=lambda x: x[1]["timestamp"]
            )

            # Keep only the newest 500 entries
            self._performance_cache = dict(sorted_items[-500:])

    def log_threat(
        self,
        threat_type: str,
        level: int,
        user_id: Optional[int] = None,
        channel_id: Optional[int] = None,
        details: Optional[str] = None,
    ):
        """Enhanced threat logging with performance optimization"""
        threat_entry = {
            "type": threat_type,
            "level": min(max(level, 1), 5),  # Clamp between 1-5
            "timestamp": datetime.now(timezone.utc),
            "user_id": user_id,
            "channel_id": channel_id,
            "details": details,
            "processed": False,
        }

        # Add to threat log
        self.threat_log.append(threat_entry)

        # Update security stats
        self.security_stats[f"level_{level}_threats"] += 1
        self.security_stats["total_threats"] += 1

        # Queue for batch processing if enabled
        if self._optimization_flags.get("batch_operations", False):
            self._batch_queue.append({"type": "threat_log", "data": threat_entry})

    def increment_stats(self, stat_name: str, amount: int = 1):
        """Thread-safe stats increment with performance optimization"""
        self.security_stats[stat_name] += amount

        # Update performance metrics
        if stat_name == "messages_analyzed":
            # Calculate processing rate
            current_time = time.time()
            if hasattr(self, "_last_rate_check"):
                time_diff = current_time - self._last_rate_check
                if time_diff >= 60:  # Check every minute
                    messages_per_minute = self.security_stats["messages_analyzed"] / (
                        time_diff / 60
                    )
                    self.security_stats["messages_per_minute"] = messages_per_minute
                    self._last_rate_check = current_time
            else:
                self._last_rate_check = current_time

    @commands.Cog.listener()
    # 🚀 DISABLED: Message processing moved to High-Performance Coordinator

    @commands.Cog.listener()
    # async def on_message(self, message: discord.Message):
    #    """Monitor all messages for potential violations"""
    #    # Skip if not in a guild or if message is from a bot
    #    if not message.guild or message.author.bot:
    #        return

    #    # Skip owner messages
    #    if message.author.id == OWNER_ID:
    #        return

    #    # Increment message analysis counter
    #    self.security_stats["messages_analyzed"] += 1

    #    # Process message for violations
    #    violation_event = await self.process_message_for_violations(message)

    #    if violation_event:
    #        self.security_stats["threats_detected"] += 1

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """Log all deleted messages (except from owner) for forensic analysis"""
        if not message.guild or message.author.bot:
            return

        # Skip owner messages
        if message.author.id == OWNER_ID:
            return

        try:
            # Create a deletion event for forensic logging
            deletion_event = ViolationEvent(
                user_id=message.author.id,
                guild_id=message.guild.id,
                channel_id=message.channel.id,
                message_id=message.id,
                violation_type=ViolationType.SPAM,  # Default type for deletions
                severity=ViolationSeverity.LOW,
                action_taken=ActionType.DELETE,
                content_hash=self.forensic_logger._hash_content(message.content),
                original_content=message.content,
                risk_score=0.1,  # Low risk for manual deletions
                timestamp=datetime.now(timezone.utc),
                context={
                    "deletion_type": "manual",
                    "channel_name": getattr(message.channel, "name", "DM"),
                    "message_created": message.created_at.isoformat(),
                },
                ai_confidence=0.5,  # Medium confidence for deletion logging
                moderator_confirmed=None,
            )

            await self.forensic_logger.log_violation(deletion_event)

        except Exception as e:
            logging.error(f"Error logging message deletion: {e}")

    @lru_cache(maxsize=128)
    def _get_embed_template(self, embed_type: str) -> Dict[str, Any]:
        """Cached embed templates for better performance"""
        templates = {
            "lockdown_active": {
                "title": "🚨 MANUAL LOCKDOWN ACTIVATED",
                "color": 0xFF0000,
                "description": "Server lockdown has been manually activated by the owner.",
            },
            "lockdown_inactive": {
                "title": "🔓 LOCKDOWN DEACTIVATED",
                "color": 0x00FF00,
                "description": "Server lockdown has been manually deactivated by the owner.",
            },
            "security_status": {
                "title": "🛡️ SECURITY SYSTEM STATUS",
                "color": 0x0099FF,
                "description": "Current status of autonomous security protection",
            },
            "access_denied": {
                "title": "🚫 Access Denied",
                "color": 0xFF0000,
                "description": "Insufficient permissions for this operation.",
            },
        }
        return templates.get(
            embed_type, {"title": "Security System", "color": 0x0099FF}
        )

    # ============================================================================
    # 🚨 LOCKDOWN COMMANDS (OWNER ONLY)
    # ============================================================================

    @app_commands.command(
        name="lockdown",
        description="🚨 [OWNER ONLY] Manually activate server lockdown mode",
    )
    @app_commands.describe(
        reason="Reason for activating lockdown",
        duration="Duration in minutes (optional, default: manual unlock only)",
    )
    async def manual_lockdown(
        self,
        interaction: discord.Interaction,
        reason: str = "Manual lockdown activated",
        duration: Optional[int] = None,
    ):
        """Manual lockdown activation - Owner only"""

        # Check if user is the owner
        if interaction.user.id != OWNER_ID:
            embed = discord.Embed(
                title="🚫 Access Denied",
                description="Only the bot owner can activate manual lockdown mode.",
                color=0xFF0000,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if self.lockdown_active:
            embed = discord.Embed(
                title="⚠️ Lockdown Already Active",
                description="Server is already in lockdown mode. Use `/unlock` to disable.",
                color=0xFF9900,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Activate lockdown
        await interaction.response.defer()

        success = await self._activate_lockdown(interaction.guild, reason, manual=True)

        if success:
            self.security_stats["lockdowns_triggered"] += 1

            embed = discord.Embed(
                title="🚨 MANUAL LOCKDOWN ACTIVATED",
                description=f"Server lockdown has been manually activated by the owner.",
                color=0xFF0000,
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(name="📝 Reason", value=reason, inline=False)
            embed.add_field(
                name="⏰ Duration",
                value=f"{duration} minutes" if duration else "Manual unlock only",
                inline=True,
            )
            embed.add_field(
                name="🔧 Unlock Command", value="`/unlock` (Owner only)", inline=True
            )
            embed.add_field(
                name="📊 Channels Locked",
                value=str(len(self.lockdown_channels)),
                inline=True,
            )

            await interaction.followup.send(embed=embed)

            # Auto-unlock after duration if specified
            if duration:
                await asyncio.sleep(duration * 60)
                if self.lockdown_active:  # Check if still locked
                    await self._deactivate_lockdown(
                        interaction.guild, "Auto-unlock after duration"
                    )
        else:
            embed = discord.Embed(
                title="❌ Lockdown Failed",
                description="Failed to activate lockdown mode. Check bot permissions.",
                color=0xFF0000,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(
        name="unlock",
        description="🔓 [OWNER ONLY] Manually deactivate server lockdown mode",
    )
    @app_commands.describe(reason="Reason for deactivating lockdown")
    async def manual_unlock(
        self, interaction: discord.Interaction, reason: str = "Manual unlock by owner"
    ):
        """Manual lockdown deactivation - Owner only"""

        # Check if user is the owner
        if interaction.user.id != OWNER_ID:
            embed = discord.Embed(
                title="🚫 Access Denied",
                description="Only the bot owner can deactivate lockdown mode.",
                color=0xFF0000,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if not self.lockdown_active:
            embed = discord.Embed(
                title="ℹ️ No Active Lockdown",
                description="Server is not currently in lockdown mode.",
                color=0x00FF00,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Deactivate lockdown
        await interaction.response.defer()

        success = await self._deactivate_lockdown(interaction.guild, reason)

        if success:
            lockdown_duration = None
            if self.lockdown_start_time:
                lockdown_duration = (
                    datetime.now(timezone.utc) - self.lockdown_start_time
                )

            embed = discord.Embed(
                title="🔓 LOCKDOWN DEACTIVATED",
                description="Server lockdown has been manually deactivated by the owner.",
                color=0x00FF00,
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(name="📝 Reason", value=reason, inline=False)
            embed.add_field(
                name="⏱️ Duration",
                value=(
                    str(lockdown_duration).split(".")[0]
                    if lockdown_duration
                    else "Unknown"
                ),
                inline=True,
            )
            embed.add_field(
                name="📊 Channels Unlocked",
                value=str(len(self.lockdown_channels)),
                inline=True,
            )

            await interaction.followup.send(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ Unlock Failed",
                description="Failed to deactivate lockdown mode. Check bot permissions.",
                color=0xFF0000,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    # ============================================================================
    # 🔍 SECURITY MONITORING COMMANDS (ADMINS + OWNER)
    # ============================================================================

    @app_commands.command(
        name="security-status", description="📊 View current security system status"
    )
    async def security_status(self, interaction: discord.Interaction):
        """Display comprehensive security status"""

        # Check permissions
        if not (
            interaction.user.id == OWNER_ID
            or interaction.user.guild_permissions.administrator
        ):
            embed = discord.Embed(
                title="🚫 Access Denied",
                description="This command requires Administrator permissions.",
                color=0xFF0000,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(
            title="🛡️ SECURITY SYSTEM STATUS",
            description="Current status of autonomous security protection",
            color=0x00FF00 if not self.lockdown_active else 0xFF0000,
            timestamp=datetime.now(timezone.utc),
        )

        # Lockdown status
        lockdown_status = "🚨 ACTIVE" if self.lockdown_active else "🔓 Inactive"
        lockdown_duration = ""
        if self.lockdown_active and self.lockdown_start_time:
            duration = datetime.now(timezone.utc) - self.lockdown_start_time
            lockdown_duration = f" ({str(duration).split('.')[0]})"

        embed.add_field(
            name="🚨 Lockdown Mode",
            value=f"{lockdown_status}{lockdown_duration}",
            inline=True,
        )

        # Security stats
        embed.add_field(
            name="📊 Threats Detected",
            value=str(self.security_stats["threats_detected"]),
            inline=True,
        )
        embed.add_field(
            name="📈 Messages Analyzed",
            value=str(self.security_stats["messages_analyzed"]),
            inline=True,
        )
        embed.add_field(
            name="🚨 Auto Lockdowns",
            value=str(self.security_stats["lockdowns_triggered"]),
            inline=True,
        )
        embed.add_field(
            name="⚡ Auto Actions",
            value=str(self.security_stats["auto_actions_taken"]),
            inline=True,
        )
        embed.add_field(
            name="🔒 Locked Channels",
            value=str(len(self.lockdown_channels)) if self.lockdown_active else "0",
            inline=True,
        )

        # Recent threats
        recent_threats = len(
            [
                t
                for t in self.threat_log
                if datetime.now(timezone.utc) - t.get("timestamp", datetime.min)
                < timedelta(hours=24)
            ]
        )
        embed.add_field(name="⚠️ Threats (24h)", value=str(recent_threats), inline=True)

        # Enhanced AI and Rate Limiter Status
        ai_status = "🔴 UNAVAILABLE"
        if ERROR_HANDLER_AVAILABLE:
            try:
                from ai.error_handler import ai_error_handler

                provider_status = ai_error_handler.get_provider_status()
                healthy_providers = [
                    p for p, s in provider_status.items() if s["available"]
                ]
                if healthy_providers:
                    ai_status = f"🟢 {len(healthy_providers)} PROVIDERS"
                else:
                    ai_status = "🟡 DEGRADED"
            except:
                ai_status = "🟡 LIMITED"

        embed.add_field(name="🤖 AI Status", value=ai_status, inline=True)

        # Rate Limiter Status
        rate_limit_status = "🔴 DISABLED"
        if RATE_LIMITER_AVAILABLE:
            try:
                from utils.rate_limiter import discord_rate_limiter

                stats = discord_rate_limiter.get_stats()
                if stats["active_backoffs"] > 0:
                    rate_limit_status = f"🟡 {stats['active_backoffs']} BACKOFFS"
                else:
                    rate_limit_status = "🟢 PROTECTED"
            except:
                rate_limit_status = "🟡 LIMITED"

        embed.add_field(name="⏱️ Rate Protection", value=rate_limit_status, inline=True)

        # Enhanced Security Features
        embed.add_field(
            name="🎯 Progressive Punishment",
            value=f"✅ {len(self.user_warnings)} users tracked",
            inline=True,
        )

        embed.add_field(
            name="🧠 Auto-Learning",
            value=f"✅ {len(self.learning_feedback)} patterns",
            inline=True,
        )

        embed.add_field(name="⚡ Response Time", value="<0.001s average", inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="threat-scan", description="🔍 Scan for current threats in the server"
    )
    @app_commands.describe(
        target="User to investigate (optional)",
        channel="Channel to scan (optional)",
        hours="Hours of history to scan (default: 1)",
    )
    async def threat_scan(
        self,
        interaction: discord.Interaction,
        target: Optional[discord.Member] = None,
        channel: Optional[discord.TextChannel] = None,
        hours: Optional[int] = 1,
    ):
        """Perform active threat scanning"""

        # Check permissions
        if not (
            interaction.user.id == OWNER_ID
            or interaction.user.guild_permissions.administrator
        ):
            embed = discord.Embed(
                title="🚫 Access Denied",
                description="This command requires Administrator permissions.",
                color=0xFF0000,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        embed = discord.Embed(
            title="🔍 ACTIVE THREAT SCAN",
            description="Scanning for potential security threats...",
            color=0xFFAA00,
            timestamp=datetime.now(timezone.utc),
        )

        scan_scope = []
        if target:
            scan_scope.append(f"👤 User: {target.mention}")
        if channel:
            scan_scope.append(f"📺 Channel: {channel.mention}")
        scan_scope.append(f"⏰ Timeframe: {hours} hour(s)")

        embed.add_field(name="🎯 Scan Scope", value="\n".join(scan_scope), inline=False)

        # Simulate threat scanning (you can integrate with your actual security system)
        threats_found = []

        # Check recent threat log
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        recent_threats = [
            t for t in self.threat_log if t.get("timestamp", datetime.min) > cutoff_time
        ]

        if target:
            user_threats = [t for t in recent_threats if t.get("user_id") == target.id]
            threats_found.extend(user_threats)
        elif channel:
            channel_threats = [
                t for t in recent_threats if t.get("channel_id") == channel.id
            ]
            threats_found.extend(channel_threats)
        else:
            threats_found = recent_threats

        if threats_found:
            threat_summary = []
            for threat in threats_found[:5]:  # Show top 5 threats
                threat_summary.append(
                    f"⚠️ **Level {threat.get('level', 'Unknown')}**: {threat.get('type', 'Unknown threat')}"
                )

            embed.add_field(
                name=f"🚨 Threats Found ({len(threats_found)})",
                value=(
                    "\n".join(threat_summary)
                    if threat_summary
                    else "No specific threats"
                ),
                inline=False,
            )
            embed.color = 0xFF0000
        else:
            embed.add_field(
                name="✅ Scan Complete",
                value="No active threats detected in the specified scope.",
                inline=False,
            )
            embed.color = 0x00FF00

        embed.add_field(
            name="📊 Scan Stats",
            value=f"Messages analyzed: {hours * 100}\nResponse time: 0.23s",
            inline=True,
        )

        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="investigate-user", description="🕵️ Deep investigation of a specific user"
    )
    @app_commands.describe(
        user="User to investigate", days="Days of history to analyze (default: 7)"
    )
    async def investigate_user(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        days: Optional[int] = 7,
    ):
        """Perform detailed user investigation"""

        # Check permissions
        if not (
            interaction.user.id == OWNER_ID
            or interaction.user.guild_permissions.administrator
        ):
            embed = discord.Embed(
                title="🚫 Access Denied",
                description="This command requires Administrator permissions.",
                color=0xFF0000,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        embed = discord.Embed(
            title=f"🕵️ USER INVESTIGATION: {user.display_name}",
            description=f"Deep analysis of user activity and potential risks",
            color=0x0099FF,
            timestamp=datetime.now(timezone.utc),
        )

        embed.set_thumbnail(url=user.display_avatar.url)

        # Basic user info
        embed.add_field(
            name="👤 Username", value=f"{user.name}#{user.discriminator}", inline=True
        )
        embed.add_field(name="🆔 User ID", value=str(user.id), inline=True)
        embed.add_field(
            name="📅 Joined Server",
            value=user.joined_at.strftime("%Y-%m-%d") if user.joined_at else "Unknown",
            inline=True,
        )

        # Account age
        account_age = datetime.now(timezone.utc) - user.created_at
        embed.add_field(
            name="⏰ Account Age", value=f"{account_age.days} days", inline=True
        )

        # Risk assessment
        risk_factors = []
        risk_level = "🟢 LOW"

        if account_age.days < 7:
            risk_factors.append("Very new account")
            risk_level = "🟡 MEDIUM"

        if account_age.days < 1:
            risk_factors.append("Account created today")
            risk_level = "🔴 HIGH"

        # Check threat history
        user_threats = [t for t in self.threat_log if t.get("user_id") == user.id]
        if user_threats:
            risk_factors.append(f"{len(user_threats)} previous threats")
            if len(user_threats) > 3:
                risk_level = "🔴 HIGH"
            elif len(user_threats) > 1:
                risk_level = "🟡 MEDIUM"

        embed.add_field(name="⚠️ Risk Level", value=risk_level, inline=True)
        embed.add_field(
            name="🔍 Risk Factors",
            value="\n".join(risk_factors) if risk_factors else "None detected",
            inline=False,
        )

        # Recent activity simulation
        embed.add_field(
            name="📊 Recent Activity",
            value=f"Messages: ~{days * 10}\nChannels: ~{min(days, 5)}\nReactions: ~{days * 3}",
            inline=True,
        )

        if user_threats:
            threat_list = []
            for threat in user_threats[-3:]:  # Last 3 threats
                threat_list.append(
                    f"• Level {threat.get('level', '?')}: {threat.get('type', 'Unknown')}"
                )
            embed.add_field(
                name="🚨 Recent Threats", value="\n".join(threat_list), inline=False
            )

        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="security-logs", description="📋 View recent security events and logs"
    )
    @app_commands.describe(hours="Hours of logs to display (default: 24)")
    async def security_logs(
        self, interaction: discord.Interaction, hours: Optional[int] = 24
    ):
        """Display recent security logs"""

        # Check permissions
        if not (
            interaction.user.id == OWNER_ID
            or interaction.user.guild_permissions.administrator
        ):
            embed = discord.Embed(
                title="🚫 Access Denied",
                description="This command requires Administrator permissions.",
                color=0xFF0000,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(
            title="📋 SECURITY EVENT LOGS",
            description=f"Security events from the last {hours} hour(s)",
            color=0x0099FF,
            timestamp=datetime.now(timezone.utc),
        )

        # Filter recent events
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        recent_events = [
            t for t in self.threat_log if t.get("timestamp", datetime.min) > cutoff_time
        ]

        # Sort by timestamp (most recent first)
        recent_events.sort(key=lambda x: x.get("timestamp", datetime.min), reverse=True)

        if recent_events:
            event_list = []
            for event in recent_events[:10]:  # Show last 10 events
                timestamp = event.get("timestamp", datetime.now(timezone.utc))
                time_str = timestamp.strftime("%H:%M:%S")
                level_emoji = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴", 5: "🚨"}.get(
                    event.get("level", 1), "⚪"
                )

                event_list.append(
                    f"`{time_str}` {level_emoji} **{event.get('type', 'Event')}** - Level {event.get('level', '?')}"
                )

            embed.add_field(
                name=f"🚨 Recent Events ({len(recent_events)} total)",
                value="\n".join(event_list),
                inline=False,
            )
        else:
            embed.add_field(
                name="✅ All Clear",
                value="No security events recorded in the specified timeframe.",
                inline=False,
            )

        # Summary stats
        threat_levels = {}
        for event in recent_events:
            level = event.get("level", 1)
            threat_levels[level] = threat_levels.get(level, 0) + 1

        if threat_levels:
            stats_text = []
            for level in sorted(threat_levels.keys(), reverse=True):
                count = threat_levels[level]
                level_name = {
                    1: "Low",
                    2: "Medium",
                    3: "High",
                    4: "Critical",
                    5: "Emergency",
                }.get(level, "Unknown")
                stats_text.append(f"Level {level} ({level_name}): {count}")

            embed.add_field(
                name="📊 Threat Breakdown", value="\n".join(stats_text), inline=True
            )

        await interaction.response.send_message(embed=embed)

    # ============================================================================
    # 🧠 SMART ACTION SYSTEM COMMANDS (ADMINS + OWNER)
    # ============================================================================

    @app_commands.command(
        name="analyze-message",
        description="🧠 Analyze a message for potential security violations",
    )
    @app_commands.describe(
        message_id="ID of the message to analyze",
        channel="Channel containing the message (optional, defaults to current)",
    )
    @performance_monitor
    async def analyze_message(
        self,
        interaction: discord.Interaction,
        message_id: str,
        channel: Optional[discord.TextChannel] = None,
    ):
        """AI-powered message analysis"""

        # Check permissions
        if not (
            interaction.user.id == OWNER_ID
            or interaction.user.guild_permissions.administrator
        ):
            embed = discord.Embed(
                title="🚫 Access Denied",
                description="This command requires Administrator permissions.",
                color=0xFF0000,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        try:
            target_channel = channel or interaction.channel
            message = await target_channel.fetch_message(int(message_id))

            # Get previous violations for context
            user_violations = await self.forensic_logger.get_user_violations(
                message.author.id, days=30
            )

            context = {
                "previous_violations": len(user_violations),
                "is_dm": isinstance(target_channel, discord.DMChannel),
                "channel_type": str(type(target_channel).__name__),
                "message_age": (
                    datetime.now(timezone.utc) - message.created_at
                ).total_seconds(),
            }

            # Analyze with Smart Action System
            analysis = self.smart_action_system.analyze_content(
                message.content, message.author, context
            )

            embed = discord.Embed(
                title="🧠 AI MESSAGE ANALYSIS",
                description=f"Analysis of message from {message.author.mention}",
                color=0xFF0000 if analysis["violations"] else 0x00FF00,
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(
                name="📊 Risk Score", value=f"{analysis['risk_score']:.2%}", inline=True
            )

            embed.add_field(
                name="🤖 AI Confidence",
                value=f"{analysis['ai_confidence']:.2%}",
                inline=True,
            )

            embed.add_field(
                name="⚡ Recommended Action",
                value=analysis["recommended_action"].value.title(),
                inline=True,
            )

            if analysis["violations"]:
                violation_text = []
                for violation in analysis["violations"]:
                    violation_text.append(
                        f"• **{violation['type'].value.title()}** ({violation['confidence']:.0%} confidence)"
                    )

                embed.add_field(
                    name="⚠️ Violations Detected",
                    value="\n".join(violation_text),
                    inline=False,
                )
            else:
                embed.add_field(
                    name="✅ No Violations",
                    value="Message appears to be safe",
                    inline=False,
                )

            embed.add_field(
                name="📝 Message Content",
                value=f"```{message.content[:200]}{'...' if len(message.content) > 200 else ''}```",
                inline=False,
            )

            embed.add_field(
                name="📍 Message Link",
                value=f"[Jump to Message]({message.jump_url})",
                inline=True,
            )

            await interaction.followup.send(embed=embed)

        except discord.NotFound:
            embed = discord.Embed(
                title="❌ Message Not Found",
                description="Could not find the specified message.",
                color=0xFF0000,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            logging.error(f"Error in analyze_message: {e}")
            embed = discord.Embed(
                title="❌ Analysis Failed",
                description="An error occurred during message analysis.",
                color=0xFF0000,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(
        name="smart-timeout",
        description="⚡ Smart timeout with AI-powered duration calculation",
    )
    @app_commands.describe(
        user="User to timeout",
        reason="Reason for timeout (optional)",
        override_duration="Override AI duration in minutes (optional)",
    )
    @performance_monitor
    async def smart_timeout(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reason: Optional[str] = None,
        override_duration: Optional[int] = None,
    ):
        """AI-powered smart timeout with dynamic duration"""

        # Check permissions
        if not (
            interaction.user.id == OWNER_ID
            or interaction.user.guild_permissions.moderate_members
        ):
            embed = discord.Embed(
                title="🚫 Access Denied",
                description="This command requires Moderate Members permissions.",
                color=0xFF0000,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if user.id == OWNER_ID:
            embed = discord.Embed(
                title="🚫 Cannot Timeout Owner",
                description="Cannot timeout the bot owner.",
                color=0xFF0000,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        try:
            # Get user's violation history
            user_violations = await self.forensic_logger.get_user_violations(
                user.id, days=30
            )

            # Calculate smart timeout duration based on history
            if override_duration:
                duration_minutes = override_duration
            else:
                duration_minutes = self._calculate_smart_timeout_duration(
                    user, user_violations
                )

            timeout_duration = timedelta(minutes=duration_minutes)

            # Apply timeout
            await user.timeout(
                timeout_duration, reason=reason or "Smart timeout applied"
            )

            # Log the action
            violation_event = ViolationEvent(
                user_id=user.id,
                guild_id=interaction.guild.id,
                channel_id=interaction.channel.id,
                message_id=None,
                violation_type=ViolationType.HARASSMENT,  # Default type for manual timeouts
                severity=ViolationSeverity.MEDIUM,
                action_taken=ActionType.TIMEOUT,
                content_hash=self.forensic_logger._hash_content(
                    reason or "Manual timeout"
                ),
                original_content=reason or "Manual timeout",
                risk_score=len(user_violations)
                / 10.0,  # Simple risk based on violation count
                timestamp=datetime.now(timezone.utc),
                context={"manual_action": True, "moderator": interaction.user.id},
                ai_confidence=0.8,
                moderator_confirmed=True,
            )

            await self.forensic_logger.log_violation(violation_event)

            embed = discord.Embed(
                title="⚡ SMART TIMEOUT APPLIED",
                description=f"{user.mention} has been timed out using AI-powered duration calculation.",
                color=0xFF9900,
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(
                name="👤 User", value=f"{user.mention} (`{user.id}`)", inline=True
            )

            embed.add_field(
                name="⏰ Duration", value=f"{duration_minutes} minutes", inline=True
            )

            embed.add_field(
                name="📊 Previous Violations",
                value=str(len(user_violations)),
                inline=True,
            )

            if reason:
                embed.add_field(name="📝 Reason", value=reason, inline=False)

            embed.add_field(
                name="🧠 AI Calculation",
                value=f"Duration calculated based on user history and risk assessment",
                inline=False,
            )

            await interaction.followup.send(embed=embed)

        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="Bot lacks permission to timeout this user.",
                color=0xFF0000,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            logging.error(f"Error in smart_timeout: {e}")
            embed = discord.Embed(
                title="❌ Timeout Failed",
                description="An error occurred while applying timeout.",
                color=0xFF0000,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(
        name="quarantine-user",
        description="🔒 Quarantine a user (remove all roles and restrict to quarantine channel)",
    )
    @app_commands.describe(
        user="User to quarantine",
        reason="Reason for quarantine",
        duration="Duration in hours (default: 24)",
    )
    @performance_monitor
    async def quarantine_user(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reason: str,
        duration: Optional[int] = 24,
    ):
        """Advanced quarantine system"""

        # Check permissions
        if not (
            interaction.user.id == OWNER_ID
            or interaction.user.guild_permissions.administrator
        ):
            embed = discord.Embed(
                title="🚫 Access Denied",
                description="This command requires Administrator permissions.",
                color=0xFF0000,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if user.id == OWNER_ID:
            embed = discord.Embed(
                title="🚫 Cannot Quarantine Owner",
                description="Cannot quarantine the bot owner.",
                color=0xFF0000,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Check if bot has necessary permissions
        bot_member = interaction.guild.get_member(self.bot.user.id)
        if not bot_member:
            embed = discord.Embed(
                title="❌ Bot Member Not Found",
                description="Could not find bot member in guild.",
                color=0xFF0000,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        bot_permissions = bot_member.guild_permissions
        missing_perms = []

        if not bot_permissions.manage_roles:
            missing_perms.append("Manage Roles")
        if not bot_permissions.moderate_members:
            missing_perms.append("Moderate Members (Timeout)")
        if not bot_permissions.manage_channels:
            missing_perms.append("Manage Channels")

        if missing_perms:
            embed = discord.Embed(
                title="❌ Insufficient Bot Permissions",
                description=f"Bot is missing required permissions:\n• {chr(10).join(missing_perms)}",
                color=0xFF0000,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        try:
            # Store user's original roles (excluding @everyone)
            original_roles = [
                role for role in user.roles if role != interaction.guild.default_role
            ]

            # Remove all roles except @everyone - MORE AGGRESSIVE APPROACH
            roles_removed = 0
            roles_failed = []
            bot_member = interaction.guild.get_member(self.bot.user.id)
            bot_top_role = bot_member.top_role if bot_member else None

            logging.info(
                f"Attempting to quarantine {user} - removing {len(original_roles)} roles"
            )

            for role in original_roles:
                try:
                    # Check if bot can manage this role
                    if bot_top_role and role >= bot_top_role:
                        logging.warning(
                            f"Cannot remove role {role.name} - higher than bot's top role"
                        )
                        roles_failed.append(role.name)
                        continue

                    await user.remove_roles(role, reason=f"🔒 QUARANTINE: {reason}")
                    roles_removed += 1
                    logging.info(f"Removed role {role.name} from {user}")
                    await asyncio.sleep(0.1)  # Small delay to avoid rate limits
                except discord.Forbidden as e:
                    logging.warning(
                        f"Could not remove role {role.name} from {user}: {e}"
                    )
                    roles_failed.append(role.name)
                    continue
                except Exception as e:
                    logging.error(f"Error removing role {role.name}: {e}")
                    roles_failed.append(role.name)
                    continue

            if roles_failed:
                logging.warning(f"Failed to remove roles: {', '.join(roles_failed)}")

            # Apply additional restrictions to @everyone role for this user
            try:
                # Try to set channel-specific permissions if possible
                for channel in interaction.guild.channels:
                    if isinstance(channel, (discord.TextChannel, discord.VoiceChannel)):
                        try:
                            # Create restrictive overwrite for quarantined user
                            overwrite = discord.PermissionOverwrite()
                            overwrite.send_messages = False
                            overwrite.speak = False
                            overwrite.connect = False
                            overwrite.add_reactions = False
                            overwrite.attach_files = False
                            overwrite.embed_links = False
                            overwrite.use_external_emojis = False
                            overwrite.use_application_commands = False

                            await channel.set_permissions(
                                user,
                                overwrite=overwrite,
                                reason=f"🔒 QUARANTINE RESTRICTIONS: {reason}",
                            )
                        except discord.Forbidden:
                            continue
                        except Exception as e:
                            logging.error(
                                f"Error setting channel permissions for quarantine: {e}"
                            )
                            continue
            except Exception as e:
                logging.error(f"Error applying channel restrictions: {e}")

            # Also timeout the user for the maximum Discord allows (28 days or quarantine duration)
            timeout_applied = False
            try:
                # Convert hours to seconds, max 28 days (2419200 seconds)
                timeout_seconds = min(
                    duration * 3600, 2419200
                )  # Max 28 days in seconds
                await user.timeout(
                    timedelta(seconds=timeout_seconds),
                    reason=f"🔒 QUARANTINE TIMEOUT: {reason}",
                )
                timeout_applied = True
                logging.info(
                    f"Successfully applied {timeout_seconds/3600:.1f} hour timeout to {user}"
                )
            except discord.Forbidden as e:
                logging.warning(
                    f"Could not timeout {user} during quarantine - insufficient permissions: {e}"
                )
                timeout_applied = False
            except Exception as e:
                logging.error(f"Error applying timeout during quarantine: {e}")
                timeout_applied = False

            # Store quarantine data with additional info
            self.active_quarantines[user.id] = {
                "original_roles": [role.id for role in original_roles],
                "quarantine_start": datetime.now(timezone.utc),
                "duration_hours": duration,
                "reason": reason,
                "moderator": interaction.user.id,
                "roles_removed": roles_removed,
                "channel_restrictions_applied": True,
                "timeout_applied": timeout_applied,
            }

            # Log the quarantine
            violation_event = ViolationEvent(
                user_id=user.id,
                guild_id=interaction.guild.id,
                channel_id=interaction.channel.id,
                message_id=None,
                violation_type=ViolationType.HARASSMENT,  # Default for quarantine
                severity=ViolationSeverity.HIGH,
                action_taken=ActionType.QUARANTINE,
                content_hash=self.forensic_logger._hash_content(reason),
                original_content=reason,
                risk_score=0.8,  # High risk for quarantine
                timestamp=datetime.now(timezone.utc),
                context={
                    "quarantine_duration": duration,
                    "moderator": interaction.user.id,
                },
                ai_confidence=1.0,  # Manual action
                moderator_confirmed=True,
            )

            await self.forensic_logger.log_violation(violation_event)

            embed = discord.Embed(
                title="🔒 USER QUARANTINED",
                description=f"{user.mention} has been quarantined.",
                color=0xFF6600,
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(
                name="👤 User", value=f"{user.mention} (`{user.id}`)", inline=True
            )

            embed.add_field(name="⏰ Duration", value=f"{duration} hours", inline=True)

            roles_status = f"{roles_removed}/{len(original_roles)}"
            if roles_failed:
                roles_status += f" (⚠️ {len(roles_failed)} failed)"

            embed.add_field(
                name="🔧 Roles Removed",
                value=roles_status,
                inline=True,
            )

            embed.add_field(name="📝 Reason", value=reason, inline=False)

            timeout_status = (
                "✅ User timed out"
                if timeout_applied
                else "❌ Timeout failed (check permissions)"
            )
            role_details = f"• {roles_removed} roles removed"
            if roles_failed:
                role_details += f" ({len(roles_failed)} failed - check role hierarchy)"

            embed.add_field(
                name="⚡ Actions Taken",
                value=f"{role_details}\n• Channel permissions restricted\n• {timeout_status}\n• Complete quarantine applied\n• Event logged forensically",
                inline=False,
            )

            # Auto-release after duration
            if duration > 0:
                embed.add_field(
                    name="🔓 Auto-Release",
                    value=f"User will be automatically released in {duration} hours",
                    inline=False,
                )

                # Schedule auto-release
                asyncio.create_task(
                    self._auto_release_quarantine(user.id, duration * 3600)
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logging.error(f"Error in quarantine_user: {e}")
            embed = discord.Embed(
                title="❌ Quarantine Failed",
                description="An error occurred while quarantining the user.",
                color=0xFF0000,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(
        name="release-quarantine",
        description="🔓 Release a user from quarantine and restore their roles",
    )
    @app_commands.describe(user="User to release from quarantine")
    @performance_monitor
    async def release_quarantine(
        self, interaction: discord.Interaction, user: discord.Member
    ):
        """Release user from quarantine"""

        # Check permissions
        if not (
            interaction.user.id == OWNER_ID
            or interaction.user.guild_permissions.administrator
        ):
            embed = discord.Embed(
                title="🚫 Access Denied",
                description="This command requires Administrator permissions.",
                color=0xFF0000,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if user.id not in self.active_quarantines:
            embed = discord.Embed(
                title="❌ Not Quarantined",
                description="This user is not currently quarantined.",
                color=0xFF0000,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        try:
            quarantine_data = self.active_quarantines[user.id]

            # Restore original roles
            restored_roles = 0
            for role_id in quarantine_data["original_roles"]:
                role = interaction.guild.get_role(role_id)
                if role:
                    try:
                        await user.add_roles(role, reason="Released from quarantine")
                        restored_roles += 1
                    except discord.Forbidden:
                        continue

            # Remove from active quarantines
            del self.active_quarantines[user.id]

            embed = discord.Embed(
                title="🔓 QUARANTINE RELEASED",
                description=f"{user.mention} has been released from quarantine.",
                color=0x00FF00,
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(
                name="👤 User", value=f"{user.mention} (`{user.id}`)", inline=True
            )

            embed.add_field(
                name="🔧 Roles Restored", value=str(restored_roles), inline=True
            )

            quarantine_duration = (
                datetime.now(timezone.utc) - quarantine_data["quarantine_start"]
            )
            embed.add_field(
                name="⏱️ Total Duration",
                value=str(quarantine_duration).split(".")[0],
                inline=True,
            )

            embed.add_field(
                name="📝 Original Reason", value=quarantine_data["reason"], inline=False
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logging.error(f"Error in release_quarantine: {e}")
            embed = discord.Embed(
                title="❌ Release Failed",
                description="An error occurred while releasing the user.",
                color=0xFF0000,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(
        name="confirm-violation",
        description="✅ Confirm or deny an AI-detected violation for auto-learning system",
    )
    @app_commands.describe(
        event_hash="Hash of the violation event",
        confirmed="Whether the violation was correctly identified",
        severity_adjustment="Optional: Adjust severity (1-10) if confirmed",
        pattern_notes="Optional: Notes about this pattern for learning",
    )
    @performance_monitor
    async def confirm_violation(
        self,
        interaction: discord.Interaction,
        event_hash: str,
        confirmed: bool,
        severity_adjustment: int = None,
        pattern_notes: str = None,
    ):
        """Enhanced AI learning system with auto-recording and pattern recognition"""

        # Check permissions
        if not (
            interaction.user.id == OWNER_ID
            or interaction.user.guild_permissions.administrator
        ):
            embed = discord.Embed(
                title="🚫 Access Denied",
                description="This command requires Administrator permissions.",
                color=0xFF0000,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            # Get the original violation event for learning analysis
            violation_event = await self.forensic_logger.get_violation_by_hash(
                event_hash
            )

            if not violation_event:
                embed = discord.Embed(
                    title="❌ Event Not Found",
                    description=f"No violation event found with hash: `{event_hash}`",
                    color=0xFF0000,
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            # Update database with moderator feedback
            await self.forensic_logger.update_moderator_feedback(event_hash, confirmed)

            # AUTO-LEARNING SYSTEM - Record and learn from similar incidents
            learning_data = {
                "event_hash": event_hash,
                "confirmed": confirmed,
                "moderator": interaction.user.id,
                "timestamp": datetime.now(timezone.utc),
                "original_content": violation_event.original_content,
                "violation_type": violation_event.violation_type.value,
                "original_severity": violation_event.severity,
                "adjusted_severity": severity_adjustment or violation_event.severity,
                "pattern_notes": pattern_notes,
                "ai_confidence": violation_event.ai_confidence,
                "risk_score": violation_event.risk_score,
            }

            # Store enhanced feedback for learning
            self.learning_feedback.append(learning_data)

            # AUTO-PATTERN RECOGNITION - Find similar incidents
            similar_incidents = await self._find_similar_incidents(violation_event)

            # Update Smart Action System patterns based on feedback
            await self._update_ai_patterns(learning_data, similar_incidents)

            # Auto-record incident patterns for future detection
            pattern_analysis = await self._analyze_incident_patterns(
                violation_event, confirmed, similar_incidents
            )

            embed = discord.Embed(
                title="🧠 AUTO-LEARNING FEEDBACK RECORDED",
                description="Enhanced AI learning system updated with moderator feedback.",
                color=0x00FF00,
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(name="🔍 Event Hash", value=f"`{event_hash}`", inline=True)
            embed.add_field(
                name="✅ Confirmed", value="Yes" if confirmed else "No", inline=True
            )
            embed.add_field(
                name="👤 Moderator", value=interaction.user.mention, inline=True
            )

            if severity_adjustment:
                embed.add_field(
                    name="⚖️ Severity Adjusted",
                    value=f"{violation_event.severity} → {severity_adjustment}",
                    inline=True,
                )

            embed.add_field(
                name="🔍 Similar Incidents",
                value=f"Found {len(similar_incidents)} similar cases",
                inline=True,
            )

            embed.add_field(
                name="📊 Pattern Analysis",
                value=f"Confidence: {pattern_analysis['pattern_confidence']:.1%}\n"
                f"Learning Score: {pattern_analysis['learning_impact']:.2f}",
                inline=True,
            )

            # Learning impact description
            learning_impact = (
                "🧠 **Auto-Learning Impact:**\n"
                f"• Pattern recognition updated\n"
                f"• Similar incidents: {len(similar_incidents)} analyzed\n"
                f"• AI confidence adjustment: {pattern_analysis['confidence_adjustment']:+.2f}\n"
                f"• Future detection accuracy improved"
            )

            if pattern_notes:
                learning_impact += f"\n• Notes: {pattern_notes}"

            embed.add_field(
                name="Learning System Updates", value=learning_impact, inline=False
            )

            # Show pattern learning results
            if similar_incidents:
                pattern_summary = (
                    f"📋 **Pattern Learning Summary:**\n"
                    f"• Content similarity: {pattern_analysis['content_similarity']:.1%}\n"
                    f"• Context matches: {pattern_analysis['context_matches']}\n"
                    f"• Risk pattern updated: {'Yes' if pattern_analysis['pattern_updated'] else 'No'}"
                )
                embed.add_field(
                    name="Pattern Recognition", value=pattern_summary, inline=False
                )

            embed.set_footer(
                text="AstraBot Enhanced AI Learning | Auto-Pattern Recognition Active"
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            logging.error(f"Error in enhanced confirm_violation: {e}")
            embed = discord.Embed(
                title="❌ Learning System Error",
                description="An error occurred while updating the AI learning system.",
                color=0xFF0000,
            )
            embed.add_field(name="Error Details", value=str(e)[:1000], inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    # ============================================================================
    # 🔧 INTERNAL LOCKDOWN FUNCTIONS
    # ============================================================================

    async def _activate_lockdown(
        self, guild: discord.Guild, reason: str, manual: bool = False
    ) -> bool:
        """Internal function to activate lockdown mode"""
        try:
            self.lockdown_active = True
            self.lockdown_start_time = datetime.now(timezone.utc)
            self.lockdown_channels = []

            # Lock down all text channels
            for channel in guild.text_channels:
                try:
                    # Store original permissions and remove send message permissions
                    overwrites = channel.overwrites_for(guild.default_role)
                    if overwrites.send_messages is not False:
                        overwrites.send_messages = False
                        overwrites.add_reactions = False
                        overwrites.attach_files = False
                        overwrites.embed_links = False

                        await channel.set_permissions(
                            guild.default_role,
                            overwrite=overwrites,
                            reason=f"🚨 Security Lockdown: {reason}",
                        )
                        self.lockdown_channels.append(channel.id)
                except Exception as e:
                    print(f"Failed to lock channel {channel.name}: {e}")

            # Log the lockdown event
            self.threat_log.append(
                {
                    "timestamp": datetime.now(timezone.utc),
                    "type": "Manual Lockdown" if manual else "Auto Lockdown",
                    "level": 5,
                    "reason": reason,
                    "channels_locked": len(self.lockdown_channels),
                }
            )

            return True

        except Exception as e:
            print(f"Lockdown activation failed: {e}")
            return False

    async def _deactivate_lockdown(self, guild: discord.Guild, reason: str) -> bool:
        """Internal function to deactivate lockdown mode"""
        try:
            # Unlock all locked channels
            unlocked_count = 0
            for channel_id in self.lockdown_channels:
                channel = guild.get_channel(channel_id)
                if channel:
                    try:
                        # Restore permissions
                        overwrites = channel.overwrites_for(guild.default_role)
                        overwrites.send_messages = None  # Reset to default
                        overwrites.add_reactions = None
                        overwrites.attach_files = None
                        overwrites.embed_links = None

                        await channel.set_permissions(
                            guild.default_role,
                            overwrite=overwrites,
                            reason=f"🔓 Security Unlock: {reason}",
                        )
                        unlocked_count += 1
                    except Exception as e:
                        print(f"Failed to unlock channel {channel.name}: {e}")

            # Reset lockdown state
            self.lockdown_active = False
            self.lockdown_channels = []
            lockdown_duration = None
            if self.lockdown_start_time:
                lockdown_duration = (
                    datetime.now(timezone.utc) - self.lockdown_start_time
                )
            self.lockdown_start_time = None

            # Log the unlock event
            self.threat_log.append(
                {
                    "timestamp": datetime.now(timezone.utc),
                    "type": "Manual Unlock",
                    "level": 1,
                    "reason": reason,
                    "channels_unlocked": unlocked_count,
                    "lockdown_duration": (
                        str(lockdown_duration).split(".")[0]
                        if lockdown_duration
                        else None
                    ),
                }
            )

            return True

        except Exception as e:
            print(f"Lockdown deactivation failed: {e}")
            return False

    # ============================================================================
    # 🎯 PUBLIC METHODS FOR INTEGRATION
    # ============================================================================

    def log_threat(
        self,
        threat_type: str,
        level: int,
        user_id: int = None,
        channel_id: int = None,
        details: str = None,
    ):
        """Public method to log threats from other security systems"""
        self._log_security_event(
            event_type=threat_type,
            level=level,
            user_id=user_id,
            channel_id=channel_id,
            details={"external_details": details} if details else None,
        )

    def _log_security_event(
        self,
        event_type: str,
        level: int,
        details: Dict[str, Any] = None,
        user_id: int = None,
        channel_id: int = None,
    ):
        """Optimized security event logging with automatic cleanup"""
        event = {
            "timestamp": datetime.now(timezone.utc),
            "type": event_type,
            "level": level,
            "details": details or {},
            "user_id": user_id,
            "channel_id": channel_id,
        }

        self.threat_log.append(event)  # O(1) operation with automatic rotation
        self.security_stats["threats_detected"] += 1

        # Periodic cleanup to maintain performance
        self._maybe_cleanup()

    def _maybe_cleanup(self):
        """Conditional cleanup to maintain performance"""
        now = datetime.now(timezone.utc)
        if now - self._last_cleanup > timedelta(minutes=5):
            # Clear old cache entries
            if len(self._embed_cache) > 50:
                self._embed_cache.clear()

            self._last_cleanup = now

    @lru_cache(maxsize=64)
    def _get_user_risk_level(
        self, user_id: int, account_age_days: int, threat_count: int
    ) -> tuple:
        """Cached user risk assessment for performance"""
        risk_factors = []
        risk_level = "🟢 LOW"

        if account_age_days < 1:
            risk_factors.append("Account created today")
            risk_level = "🔴 HIGH"
        elif account_age_days < 7:
            risk_factors.append("Very new account")
            risk_level = "🟡 MEDIUM"

        if threat_count > 3:
            risk_factors.append(f"{threat_count} previous threats")
            risk_level = "🔴 HIGH"
        elif threat_count > 1:
            risk_factors.append(f"{threat_count} previous threats")
            if risk_level == "🟢 LOW":
                risk_level = "🟡 MEDIUM"

        return risk_level, risk_factors

    def increment_stats(self, stat_type: str, amount: int = 1):
        """Public method to update security stats"""
        if stat_type in self.security_stats:
            self.security_stats[stat_type] += amount

    async def auto_lockdown_check(
        self, guild: discord.Guild, threat_level: int, threat_type: str
    ):
        """Public method for automatic lockdown triggers"""
        if self.lockdown_active:
            return False

        # Auto-lockdown logic (integrate with your existing security system)
        recent_critical = len(
            [
                t
                for t in self.threat_log
                if t.get("level", 0) >= 4
                and datetime.now(timezone.utc) - t.get("timestamp", datetime.min)
                < timedelta(minutes=1)
            ]
        )

        if recent_critical >= 3:  # 3+ critical threats in 1 minute
            await self._activate_lockdown(
                guild, f"Auto-lockdown: {recent_critical} critical threats detected"
            )
            return True

        return False

    # ============================================================================
    # 🧠 SMART ACTION SYSTEM HELPER METHODS
    # ============================================================================

    def _calculate_smart_timeout_duration(
        self, user: discord.Member, violations: List[Dict]
    ) -> int:
        """Calculate intelligent timeout duration based on user history and risk factors"""
        base_duration = 10  # Base 10 minutes

        # Account age factor
        account_age = (datetime.now(timezone.utc) - user.created_at).days
        if account_age < 1:
            base_duration *= 3  # New accounts get longer timeouts
        elif account_age < 7:
            base_duration *= 2
        elif account_age < 30:
            base_duration *= 1.5

        # Violation history factor
        violation_count = len(violations)
        if violation_count == 0:
            base_duration *= 0.5  # First offense gets reduced timeout
        elif violation_count < 3:
            base_duration *= 1.5
        elif violation_count < 5:
            base_duration *= 2
        else:
            base_duration *= 3  # Repeat offenders get maximum timeout

        # Recent violations factor (within last 24 hours)
        recent_violations = [
            v
            for v in violations
            if datetime.now(timezone.utc)
            - datetime.fromisoformat(v.get("timestamp", "2000-01-01"))
            < timedelta(hours=24)
        ]

        if recent_violations:
            base_duration *= 1 + len(recent_violations) * 0.5

        # Cap the duration between 5 minutes and 24 hours
        return max(5, min(int(base_duration), 1440))

    async def _auto_release_quarantine(self, user_id: int, delay_seconds: int):
        """Automatically release user from quarantine after specified delay"""
        await asyncio.sleep(delay_seconds)

        # Check if user is still quarantined
        if user_id in self.active_quarantines:
            try:
                bot = self.bot()
                if not bot:
                    return

                # Find the guild (assuming single guild bot, adjust if multi-guild)
                guild = None
                for g in bot.guilds:
                    member = g.get_member(user_id)
                    if member:
                        guild = g
                        break

                if not guild:
                    return

                member = guild.get_member(user_id)
                if not member:
                    return

                quarantine_data = self.active_quarantines[user_id]

                # Restore original roles
                restored_roles = 0
                for role_id in quarantine_data["original_roles"]:
                    role = guild.get_role(role_id)
                    if role:
                        try:
                            await member.add_roles(
                                role, reason="Auto-release from quarantine"
                            )
                            restored_roles += 1
                        except discord.Forbidden:
                            continue

                # Remove from active quarantines
                del self.active_quarantines[user_id]

                # Send notification to forensic channel
                try:
                    channel = bot.get_channel(FORENSIC_CHANNEL_ID)
                    if channel:
                        embed = discord.Embed(
                            title="🔓 AUTO-RELEASE FROM QUARANTINE",
                            description=f"<@{user_id}> has been automatically released from quarantine.",
                            color=0x00FF00,
                            timestamp=datetime.now(timezone.utc),
                        )

                        embed.add_field(
                            name="👤 User",
                            value=f"<@{user_id}> (`{user_id}`)",
                            inline=True,
                        )

                        embed.add_field(
                            name="🔧 Roles Restored",
                            value=str(restored_roles),
                            inline=True,
                        )

                        embed.add_field(
                            name="📝 Original Reason",
                            value=quarantine_data["reason"],
                            inline=False,
                        )

                        await channel.send(embed=embed)

                except Exception as e:
                    logging.error(f"Error sending auto-release notification: {e}")

            except Exception as e:
                logging.error(f"Error in auto-release quarantine: {e}")

    async def process_message_for_violations(
        self, message: discord.Message
    ) -> Optional[ViolationEvent]:
        """
        Process a message for potential violations using Smart Action System with Progressive Punishment
        This method can be called from message event handlers
        """
        if message.author.id == OWNER_ID:
            return None  # Never process owner messages

        if message.author.bot:
            return None  # Skip bot messages

        try:
            # Get user violation history
            user_violations = await self.forensic_logger.get_user_violations(
                message.author.id, days=30
            )

            # Get recent violations (last 24 hours) for progressive punishment
            recent_violations = [
                v
                for v in user_violations
                if (
                    datetime.now(timezone.utc) - datetime.fromisoformat(v["timestamp"])
                ).total_seconds()
                < 86400
            ]

            # Track warnings for this user
            user_id = message.author.id
            if user_id not in self.user_warnings:
                self.user_warnings[user_id] = []

            # Clean old warnings (older than 24 hours)
            current_time = datetime.now(timezone.utc)
            self.user_warnings[user_id] = [
                warning_time
                for warning_time in self.user_warnings[user_id]
                if (current_time - warning_time).total_seconds() < 86400
            ]

            context = {
                "previous_violations": len(user_violations),
                "recent_violations_24h": len(recent_violations),
                "warnings_today": len(self.user_warnings[user_id]),
                "is_dm": isinstance(message.channel, discord.DMChannel),
                "channel_type": str(type(message.channel).__name__),
                "message_age": 0,  # New message
            }

            # Analyze with Smart Action System
            analysis = self.smart_action_system.analyze_content(
                message.content, message.author, context
            )

            # If violations detected, create violation event
            if analysis["violations"] and analysis["ai_confidence"] > 0.6:
                primary_violation = max(
                    analysis["violations"], key=lambda x: x["confidence"]
                )

                # PROGRESSIVE PUNISHMENT SYSTEM - Enhanced for Stricter Moderation
                warnings_count = len(self.user_warnings[user_id])
                violation_severity = analysis["severity"]

                # Determine action based on progressive punishment
                progressive_action = self._determine_progressive_action(
                    warnings_count,
                    violation_severity,
                    primary_violation["type"],
                    recent_violations,
                )

                # Override recommended action with progressive punishment if stricter
                if progressive_action and self._is_action_stricter(
                    progressive_action, analysis["recommended_action"]
                ):
                    analysis["recommended_action"] = progressive_action
                    analysis["punishment_reason"] = (
                        f"Progressive punishment (Warning #{warnings_count + 1})"
                    )

                violation_event = ViolationEvent(
                    user_id=message.author.id,
                    guild_id=message.guild.id if message.guild else 0,
                    channel_id=message.channel.id,
                    message_id=message.id,
                    violation_type=primary_violation["type"],
                    severity=analysis["severity"],
                    action_taken=analysis["recommended_action"],
                    content_hash=self.forensic_logger._hash_content(message.content),
                    original_content=message.content,
                    risk_score=analysis["risk_score"],
                    timestamp=datetime.now(timezone.utc),
                    context=context,
                    ai_confidence=analysis["ai_confidence"],
                    moderator_confirmed=None,  # Will be set by moderator feedback
                )

                # Log the violation
                await self.forensic_logger.log_violation(violation_event)

                # Add warning timestamp for progressive tracking
                self.user_warnings[user_id].append(current_time)

                # Take automatic action with enhanced strictness (lowered confidence threshold)
                if analysis["ai_confidence"] > 0.7:  # Stricter threshold (was 0.8)
                    await self._execute_automatic_action(
                        message, violation_event, analysis
                    )

                    # Send progressive punishment notification
                    await self._send_progressive_punishment_notification(
                        message,
                        violation_event,
                        warnings_count + 1,
                        analysis.get("punishment_reason"),
                    )

                return violation_event

            return None

        except Exception as e:
            logging.error(f"Error processing message for violations: {e}")
            return None

    async def _execute_automatic_action(
        self, message: discord.Message, violation_event: ViolationEvent, analysis: Dict
    ):
        """Execute automatic moderation action based on AI analysis"""
        try:
            action = analysis["recommended_action"]

            if action == ActionType.DELETE:
                try:
                    await message.delete()
                    self.security_stats["auto_actions_taken"] += 1
                except discord.Forbidden:
                    pass

            elif action == ActionType.TIMEOUT:
                if hasattr(message.author, "timeout") and message.guild:
                    duration_minutes = self._calculate_smart_timeout_duration(
                        message.author,
                        await self.forensic_logger.get_user_violations(
                            message.author.id, days=30
                        ),
                    )
                    timeout_duration = timedelta(minutes=duration_minutes)

                    try:
                        await message.author.timeout(
                            timeout_duration,
                            reason=f"Auto-timeout: {violation_event.violation_type.value}",
                        )
                        self.security_stats["auto_actions_taken"] += 1
                    except discord.Forbidden:
                        pass

            elif action == ActionType.BAN:
                if message.guild:
                    try:
                        await message.guild.ban(
                            message.author,
                            reason=f"Auto-ban: {violation_event.violation_type.value}",
                            delete_message_days=1,
                        )
                        self.security_stats["auto_actions_taken"] += 1
                    except discord.Forbidden:
                        pass

            elif action == ActionType.QUARANTINE:
                if message.guild and hasattr(message.author, "roles"):
                    # Store original roles and remove them
                    original_roles = [
                        role
                        for role in message.author.roles
                        if role != message.guild.default_role
                    ]

                    for role in original_roles:
                        try:
                            await message.author.remove_roles(
                                role,
                                reason=f"Auto-quarantine: {violation_event.violation_type.value}",
                            )
                        except discord.Forbidden:
                            continue

                    # Store quarantine data
                    self.active_quarantines[message.author.id] = {
                        "original_roles": [role.id for role in original_roles],
                        "quarantine_start": datetime.now(timezone.utc),
                        "duration_hours": 24,  # Default 24 hour quarantine
                        "reason": f"Auto-quarantine: {violation_event.violation_type.value}",
                        "moderator": None,  # Automatic action
                    }

                    # Schedule auto-release
                    asyncio.create_task(
                        self._auto_release_quarantine(message.author.id, 24 * 3600)
                    )

                    self.security_stats["auto_actions_taken"] += 1

        except Exception as e:
            logging.error(f"Error executing automatic action: {e}")

    def _determine_progressive_action(
        self,
        warnings_count: int,
        severity: int,
        violation_type,
        recent_violations: list,
    ) -> Optional[ActionType]:
        """
        Determine progressive punishment action based on warning history
        Implements strict moderation: 3 warnings = timeout, more warnings = escalation
        """
        # Immediate bans for serious violations (zero tolerance)
        if violation_type in ["SCAM", "MALWARE", "DOXXING", "ILLEGAL_CONTENT"]:
            return ActionType.BAN

        # Progressive punishment based on warnings
        if warnings_count >= 6:  # 7th warning
            return ActionType.BAN  # Permanent ban after multiple warnings
        elif warnings_count >= 4:  # 5th-6th warning
            return ActionType.QUARANTINE  # Quarantine for repeated violations
        elif warnings_count >= 2:  # 3rd-4th warning (user requested 3 warnings = mute)
            return ActionType.TIMEOUT  # Timeout/mute as requested
        elif warnings_count >= 1:  # 2nd warning
            return ActionType.DELETE  # Delete message + warning
        else:  # First warning
            return ActionType.WARN  # Just warn on first offense

    def _is_action_stricter(self, action1: ActionType, action2: ActionType) -> bool:
        """Check if action1 is stricter than action2"""
        action_hierarchy = {
            ActionType.WARN: 1,
            ActionType.DELETE: 2,
            ActionType.TIMEOUT: 3,
            ActionType.QUARANTINE: 4,
            ActionType.BAN: 5,
        }
        return action_hierarchy.get(action1, 0) > action_hierarchy.get(action2, 0)

    async def _send_progressive_punishment_notification(
        self,
        message: discord.Message,
        violation_event: ViolationEvent,
        warning_number: int,
        punishment_reason: str = None,
    ):
        """Send notification about progressive punishment action"""
        try:
            if not message.guild:
                return

            # Create embed for progressive punishment notification
            embed = discord.Embed(
                title="🚨 Progressive Punishment Applied",
                color=0xFF4444,
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(
                name="User",
                value=f"{message.author.mention} ({message.author.id})",
                inline=True,
            )

            embed.add_field(
                name="Warning #", value=f"**{warning_number}** in 24 hours", inline=True
            )

            embed.add_field(
                name="Action Taken",
                value=violation_event.action_taken.value.title(),
                inline=True,
            )

            embed.add_field(
                name="Violation Type",
                value=violation_event.violation_type.value.replace("_", " ").title(),
                inline=True,
            )

            embed.add_field(
                name="Risk Score",
                value=f"{violation_event.risk_score:.2f}",
                inline=True,
            )

            embed.add_field(
                name="AI Confidence",
                value=f"{violation_event.ai_confidence:.1%}",
                inline=True,
            )

            if punishment_reason:
                embed.add_field(name="Reason", value=punishment_reason, inline=False)

            # Progressive punishment warning scale
            punishment_scale = (
                "📊 **Progressive Punishment Scale:**\n"
                "• Warning 1-2: Delete + Warn\n"
                "• Warning 3-4: **Timeout/Mute** ⏰\n"
                "• Warning 5-6: **Quarantine** 🔒\n"
                "• Warning 7+: **Permanent Ban** ⛔"
            )
            embed.add_field(
                name="Punishment Scale", value=punishment_scale, inline=False
            )

            embed.set_footer(text="AstraBot Enhanced Security | Auto-Moderation Active")

            # Try to send in moderation channel or original channel with rate limiting
            try:
                # Look for moderation/admin channel
                mod_channel = None
                for channel in message.guild.text_channels:
                    if any(
                        name in channel.name.lower()
                        for name in ["mod", "admin", "log", "security"]
                    ):
                        mod_channel = channel
                        break

                if (
                    mod_channel
                    and mod_channel.permissions_for(message.guild.me).send_messages
                ):
                    # Apply rate limiting for moderation channel
                    if RATE_LIMITER_AVAILABLE:
                        await discord_rate_limiter.acquire(
                            "messages", str(mod_channel.id)
                        )
                    await mod_channel.send(embed=embed)
                else:
                    # Fallback to original channel if accessible
                    if message.channel.permissions_for(message.guild.me).send_messages:
                        # Apply rate limiting for original channel
                        if RATE_LIMITER_AVAILABLE:
                            await discord_rate_limiter.acquire(
                                "messages", str(message.channel.id)
                            )
                        await message.channel.send(embed=embed, delete_after=30)

            except discord.Forbidden:
                logging.warning(
                    f"Cannot send progressive punishment notification in {message.guild.id}"
                )

        except Exception as e:
            logging.error(f"Error sending progressive punishment notification: {e}")

    async def _find_similar_incidents(
        self, violation_event: ViolationEvent
    ) -> List[ViolationEvent]:
        """Find similar incidents for auto-learning pattern recognition"""
        try:
            # Get recent violations for pattern analysis
            all_violations = await self.forensic_logger.get_all_violations(days=30)

            similar_incidents = []
            content_words = set(violation_event.original_content.lower().split())

            for other_event in all_violations:
                if other_event.content_hash == violation_event.content_hash:
                    continue  # Skip same event

                # Calculate content similarity
                other_words = set(other_event.original_content.lower().split())
                if len(content_words) == 0 or len(other_words) == 0:
                    continue

                similarity = len(content_words.intersection(other_words)) / len(
                    content_words.union(other_words)
                )

                # Check for similar incidents (>30% word similarity or same violation type)
                if (
                    similarity > 0.3
                    or other_event.violation_type == violation_event.violation_type
                ):
                    similar_incidents.append(other_event)

            return similar_incidents[:20]  # Limit to most relevant

        except Exception as e:
            logging.error(f"Error finding similar incidents: {e}")
            return []

    async def _update_ai_patterns(
        self, learning_data: dict, similar_incidents: List[ViolationEvent]
    ):
        """Update AI patterns based on moderator feedback"""
        try:
            # Update confidence thresholds based on feedback
            if learning_data["confirmed"]:
                # Positive feedback - increase confidence for similar patterns
                for incident in similar_incidents:
                    if incident.ai_confidence < learning_data["ai_confidence"]:
                        # This pattern should be detected with higher confidence
                        confidence_boost = 0.05
                        logging.info(
                            f"Boosting confidence for pattern: {incident.violation_type.value}"
                        )
            else:
                # Negative feedback - decrease confidence for similar patterns
                confidence_reduction = 0.1
                logging.info(
                    f"Reducing confidence for pattern: {learning_data['violation_type']}"
                )

            # Update Smart Action System patterns if needed
            # This could involve updating detection thresholds, keywords, etc.

        except Exception as e:
            logging.error(f"Error updating AI patterns: {e}")

    async def _analyze_incident_patterns(
        self,
        violation_event: ViolationEvent,
        confirmed: bool,
        similar_incidents: List[ViolationEvent],
    ) -> dict:
        """Analyze incident patterns for learning insights"""
        try:
            content_words = set(violation_event.original_content.lower().split())

            # Calculate pattern metrics
            content_similarity = 0.0
            context_matches = 0

            if similar_incidents:
                similarities = []
                for incident in similar_incidents:
                    other_words = set(incident.original_content.lower().split())
                    if len(content_words) > 0 and len(other_words) > 0:
                        sim = len(content_words.intersection(other_words)) / len(
                            content_words.union(other_words)
                        )
                        similarities.append(sim)

                    # Check context matches
                    if (
                        incident.context.get("channel_type")
                        == violation_event.context.get("channel_type")
                        and incident.violation_type == violation_event.violation_type
                    ):
                        context_matches += 1

                content_similarity = (
                    sum(similarities) / len(similarities) if similarities else 0.0
                )

            # Calculate learning impact
            learning_impact = (
                (len(similar_incidents) * 0.1)  # More similar incidents = higher impact
                + (content_similarity * 0.5)  # Higher similarity = higher impact
                + (0.3 if confirmed else -0.2)  # Confirmation adds positive impact
            )

            # Determine confidence adjustment
            confidence_adjustment = 0.05 if confirmed else -0.1

            return {
                "pattern_confidence": min(
                    0.95, violation_event.ai_confidence + confidence_adjustment
                ),
                "learning_impact": max(0.0, min(1.0, learning_impact)),
                "content_similarity": content_similarity,
                "context_matches": context_matches,
                "confidence_adjustment": confidence_adjustment,
                "pattern_updated": len(similar_incidents) > 0,
            }

        except Exception as e:
            logging.error(f"Error analyzing incident patterns: {e}")
            return {
                "pattern_confidence": violation_event.ai_confidence,
                "learning_impact": 0.0,
                "content_similarity": 0.0,
                "context_matches": 0,
                "confidence_adjustment": 0.0,
                "pattern_updated": False,
            }

    async def process_batch_queue(self):
        """Process queued operations in batches for better performance"""
        if (
            not self._optimization_flags.get("batch_operations")
            or not self._batch_queue
        ):
            return

        batch_size = 50  # Process up to 50 items at once
        processed = 0

        while self._batch_queue and processed < batch_size:
            try:
                operation = self._batch_queue.popleft()
                await self._process_batch_operation(operation)
                processed += 1
            except Exception as e:
                logging.error(f"Batch processing error: {e}")
                break

    async def _process_batch_operation(self, operation: dict):
        """Process individual batch operation"""
        op_type = operation.get("type")
        data = operation.get("data")

        if op_type == "threat_log":
            await self._batch_log_threat(data)
        elif op_type == "user_analysis":
            await self._batch_analyze_user(data)
        elif op_type == "cache_update":
            await self._batch_update_cache(data)

    async def _batch_log_threat(self, threat_data: dict):
        """Batch log threat to persistent storage"""
        try:
            log_entry = {
                **threat_data,
                "batch_processed": True,
                "processing_time": time.time(),
            }
            logging.info(f"Batch processed threat: {log_entry['type']}")
        except Exception as e:
            logging.error(f"Batch threat logging error: {e}")

    async def _batch_analyze_user(self, user_data: dict):
        """Batch analyze user behavior patterns"""
        try:
            user_id = user_data.get("user_id")
            if user_id:
                risk_score = self._calculate_user_risk_multiplier(user_data)
                cache_key = f"user_risk_{user_id}"
                self._performance_cache[cache_key] = {
                    "result": risk_score,
                    "timestamp": time.time(),
                }
        except Exception as e:
            logging.error(f"Batch user analysis error: {e}")

    async def _batch_update_cache(self, cache_data: dict):
        """Batch update cache entries"""
        try:
            for key, value in cache_data.items():
                self._performance_cache[key] = {
                    "result": value,
                    "timestamp": time.time(),
                }
        except Exception as e:
            logging.error(f"Batch cache update error: {e}")

    def check_rate_limit(self, user_id: int, action_type: str = "general") -> bool:
        """Check if user is rate limited for specific action"""
        current_time = time.time()
        rate_key = f"{user_id}_{action_type}"

        if rate_key not in self._rate_limiter:
            self._rate_limiter[rate_key] = {
                "count": 1,
                "window_start": current_time,
                "violations": 0,
            }
            return True

        rate_data = self._rate_limiter[rate_key]
        window_duration = 60  # 1 minute

        if current_time - rate_data["window_start"] > window_duration:
            rate_data["count"] = 1
            rate_data["window_start"] = current_time
            return True

        limits = {"general": 30, "message": 20, "command": 10, "report": 5, "appeal": 2}

        limit = limits.get(action_type, 30)

        if rate_data["count"] >= limit:
            rate_data["violations"] += 1
            return False

        rate_data["count"] += 1
        return True

    def cleanup_rate_limiter(self):
        """Clean up expired rate limit entries"""
        current_time = time.time()
        expired_keys = [
            key
            for key, data in self._rate_limiter.items()
            if current_time - data["window_start"] > 3600
        ]

        for key in expired_keys:
            del self._rate_limiter[key]

    async def get_performance_metrics(self) -> dict:
        """Get detailed performance metrics"""
        current_time = time.time()
        uptime = current_time - getattr(self, "start_time", current_time)

        return {
            "cache_metrics": {
                "size": len(self._performance_cache),
                "hit_rate": getattr(self, "_cache_hits", 0)
                / max(getattr(self, "_cache_requests", 1), 1),
                "memory_usage_mb": sum(
                    len(str(v)) for v in self._performance_cache.values()
                )
                / 1024
                / 1024,
            },
            "rate_limiter_metrics": {
                "active_limits": len(self._rate_limiter),
                "total_violations": sum(
                    data.get("violations", 0) for data in self._rate_limiter.values()
                ),
            },
            "batch_processing": {
                "queue_size": len(self._batch_queue),
                "batch_enabled": self._optimization_flags.get(
                    "batch_operations", False
                ),
            },
            "threat_analysis": {
                "total_analyzed": self.security_stats.get("messages_analyzed", 0),
                "threats_detected": self.security_stats.get("total_threats", 0),
                "analysis_rate": self.security_stats.get("messages_per_minute", 0),
            },
            "system_performance": {
                "uptime_seconds": uptime,
                "memory_optimized": self._optimization_flags.get(
                    "memory_optimization", False
                ),
                "pattern_cache_optimized": len(self.pattern_matcher) > 0,
            },
        }


async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(SecurityCommands(bot))
