"""
🛡️ UNIFIED SECURITY SYSTEM - CONSOLIDATED PROTECTION
The ultimate security system combining all features from previous systems

This consolidates:
- Advanced Security System (comprehensive detection)
- Autonomous Security (AI-powered protection)
- AI Enhanced Security (threat intelligence)
- Smart Moderation (progressive warnings)
- Security Commands (manual controls)

Features:
- Intelligent spam detection (3+ identical messages)
- Advanced threat intelligence with 2025 patterns
- Dynamic punishment with behavioral analysis
- Real-time autonomous protection
- Comprehensive manual override controls
- AI-powered toxicity detection
- Trust scoring and reputation system
- Evidence collection and forensic logging
"""

import asyncio
import logging
import time
import json
import re
import hashlib
import sqlite3
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict, field
from enum import Enum, IntEnum
from urllib.parse import urlparse
import discord
from discord.ext import commands, tasks

logger = logging.getLogger("astra.security.unified")


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED DATA MODELS - Single source of truth for all security data
# ═══════════════════════════════════════════════════════════════════════════════


class ViolationSeverity(IntEnum):
    """Violation severity levels matching punishment tiers"""

    LOW = 1  # Minor spam/single curse -> Warning/15min mute
    MEDIUM = 2  # Repeated spam/mild harassment -> 1hr/6hr/24hr mute
    HIGH = 3  # Dangerous links/targeted harassment -> 6hr/24hr/7day ban
    SEVERE = 4  # Threats/illegal content -> 7day/30day/permanent ban


class ViolationType(Enum):
    """Comprehensive violation types matching all rule categories"""

    # Spam violations (Low-Medium severity)
    SPAM_MESSAGES = "spam_messages"  # Repeated messages
    REPEATED_CONTENT = "repeated_content"  # Identical content
    MASS_MENTIONS = "mass_mentions"  # Mention spam
    LINK_SPAM = "link_spam"  # Repeated links
    CAPS_ABUSE = "caps_abuse"  # Excessive caps

    # Content violations (Medium severity)
    PROFANITY = "profanity"  # Server-specific profanity
    INAPPROPRIATE_CONTENT = "inappropriate_content"  # General inappropriate
    NSFW_CONTENT = "nsfw_content"  # NSFW where not allowed

    # Harassment violations (High severity)
    HARASSMENT = "harassment"  # Targeted abuse/bullying
    HATE_SPEECH = "hate_speech"  # Protected class targeting
    THREATS = "threats"  # Threats of violence
    DOXXING = "doxxing"  # Personal info sharing
    DARK_HUMOR_TARGETED = "dark_humor_targeted"  # Dark humor targeting groups

    # Security threats (High-Severe)
    UNSAFE_LINKS = "unsafe_links"  # Phishing/malware links
    HACKING_ATTEMPTS = "hacking_attempts"  # Exploit sharing
    SCAM_ATTEMPT = "scam_attempt"  # Fraud attempts

    # Behavioral violations (Medium-High)
    IMPERSONATION = "impersonation"  # Staff impersonation
    EVASION_ATTEMPT = "evasion_attempt"  # Alt accounts/rule evasion
    BOT_ABUSE = "bot_abuse"  # Multi-account/resource abuse
    RAID_PARTICIPATION = "raid_participation"  # Server raiding


class ThreatLevel(IntEnum):
    """Threat level classifications for autonomous protection"""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


@dataclass
class ViolationRecord:
    """Comprehensive violation record with confidence scoring"""

    user_id: int = 0
    guild_id: int = 0
    message_id: Optional[int] = None
    channel_id: int = 0
    violation_type: ViolationType = ViolationType.SPAM_MESSAGES
    severity: ViolationSeverity = ViolationSeverity.LOW
    timestamp: float = 0.0

    # Detection details
    heuristic_score: float = 0.0  # Rule-based confidence (0-1)
    ml_confidence: float = 0.0  # ML model confidence (0-1)
    final_confidence: float = 0.0  # Combined confidence score
    detection_method: str = "unknown"  # How violation was detected

    # Content evidence
    message_content: Optional[str] = None  # Original message (hashed if privacy)
    context_messages: List[str] = field(default_factory=list)  # Surrounding context
    evidence: Dict[str, Any] = field(default_factory=dict)

    # Action details
    action_taken: str = "pending"
    action_confidence: float = 0.0  # Confidence in action taken
    moderator_id: Optional[int] = None
    staff_reviewed: bool = False

    # Appeals
    resolved: bool = False
    appeal_status: Optional[str] = None  # pending, approved, denied
    appeal_reason: Optional[str] = None
    staff_notes: Optional[str] = None


@dataclass
class UserProfile:
    """Consolidated user profile with all security metrics"""

    user_id: int
    guild_id: int
    trust_score: float = 50.0
    violation_history: List[ViolationRecord] = field(default_factory=list)
    positive_contributions: int = 0
    punishment_level: int = 0
    is_trusted: bool = False
    is_quarantined: bool = False
    quarantine_reason: Optional[str] = None
    quarantine_until: Optional[float] = None

    # Behavioral patterns
    message_count: int = 0
    avg_message_length: float = 0.0
    channel_diversity: int = 0
    activity_pattern: str = "normal"
    last_activity: float = 0.0
    join_timestamp: float = 0.0

    # AI moderation preferences
    preferred_moderator_style: str = "balanced"
    violation_patterns: List[str] = field(default_factory=list)
    positive_interactions: int = 0

    # Autonomous protection data
    threat_level: int = 1
    automated_actions: List[str] = field(default_factory=list)
    last_threat_assessment: float = 0.0


@dataclass
class SecurityEvent:
    """Unified security event for logging and analysis"""

    event_id: str
    user_id: int
    guild_id: int
    event_type: str
    threat_level: int
    timestamp: float
    details: Dict[str, Any]
    automated_response: Optional[str] = None
    manual_override: bool = False


# ═══════════════════════════════════════════════════════════════════════════════
# THREAT INTELLIGENCE - AI-powered with 2025 threat patterns
# ═══════════════════════════════════════════════════════════════════════════════


class ThreatIntelligence:
    """Advanced threat intelligence with current 2025 patterns"""

    def __init__(self):
        self.threat_patterns_2025 = {
            # AI/Tech-related threats (emerging 2025)
            "ai_tech_scams": [
                r"chatgpt.*premium.*free",
                r"ai.*model.*access.*free",
                r"midjourney.*credits.*free",
                r"claude.*3.*access",
                r"gemini.*advanced.*free",
                r"github.*copilot.*premium",
                r"openai.*api.*unlimited",
                r"anthropic.*access.*free",
            ],
            # Crypto/NFT evolution (2024-2025 trends)
            "crypto_2025": [
                r"nft.*mint.*free",
                r"crypto.*airdrop.*claim",
                r"defi.*yield.*guaranteed",
                r"ethereum.*gas.*refund",
                r"bitcoin.*investment.*500%",
                r"solana.*staking.*rewards",
            ],
            # Discord-specific threats
            "discord_threats": [
                r"nitro.*free.*gift",
                r"discord.*premium.*hack",
                r"server.*boost.*generator",
                r"token.*grabber.*safe",
                r"discord.*account.*generator",
            ],
            # Social engineering
            "social_engineering": [
                r"urgent.*account.*suspended",
                r"verify.*identity.*immediate",
                r"click.*here.*avoid.*ban",
                r"limited.*time.*offer.*expires",
                r"congratulations.*you.*won",
            ],
        }

        self.malicious_domains = {
            "confirmed_malicious": [
                "discordnitro.info",
                "discord-gift.com",
                "steamcommunity.ru",
                "discord-app.net",
                "discordgift.site",
                "steam-rewards.com",
            ],
            "suspicious_tlds": [
                ".tk",
                ".ml",
                ".ga",
                ".cf",
                ".gq",
                ".pw",
                ".top",
                ".download",
            ],
            "trusted_domains": [
                "discord.com",
                "discord.gg",
                "youtube.com",
                "youtu.be",
                "github.com",
                "reddit.com",
                "wikipedia.org",
                "google.com",
                "twitch.tv",
                "twitter.com",
            ],
        }

    def analyze_threat_level(
        self, content: str, links: List[str]
    ) -> Tuple[int, List[str]]:
        """Analyze content for threat level and specific threats"""
        threats_found = []
        max_threat_level = 1

        content_lower = content.lower()

        # Check against 2025 threat patterns
        for category, patterns in self.threat_patterns_2025.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    threats_found.append(f"{category}: {pattern}")
                    max_threat_level = max(max_threat_level, 3)

        # Analyze links
        for link in links:
            try:
                domain = urlparse(link).netloc.lower()

                if domain in self.malicious_domains["confirmed_malicious"]:
                    threats_found.append(f"malicious_domain: {domain}")
                    max_threat_level = max(max_threat_level, 5)
                elif any(
                    domain.endswith(tld)
                    for tld in self.malicious_domains["suspicious_tlds"]
                ):
                    threats_found.append(f"suspicious_tld: {domain}")
                    max_threat_level = max(max_threat_level, 2)
                elif domain not in self.malicious_domains["trusted_domains"]:
                    threats_found.append(f"unknown_domain: {domain}")
                    max_threat_level = max(max_threat_level, 1)

            except Exception:
                threats_found.append(f"malformed_url: {link}")
                max_threat_level = max(max_threat_level, 2)

        return max_threat_level, threats_found


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED SECURITY SYSTEM - Main security engine
# ═══════════════════════════════════════════════════════════════════════════════


class UnifiedSecuritySystem:
    """
    Consolidated security system combining all previous security modules

    Features:
    - Advanced spam detection with intelligent pattern matching
    - Real-time threat assessment using 2025 intelligence
    - Dynamic punishment system with behavioral analysis
    - Autonomous protection with manual override capabilities
    - Comprehensive evidence collection and forensic logging
    - Trust scoring system with reputation management
    - AI-powered toxicity detection and response
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = bot.logger if hasattr(bot, "logger") else logger

        # Initialize components
        self.threat_intelligence = ThreatIntelligence()

        # User tracking
        self.user_profiles: Dict[str, UserProfile] = (
            {}
        )  # f"{guild_id}:{user_id}" -> UserProfile
        self.message_history: Dict[int, deque] = defaultdict(lambda: deque(maxlen=10))
        self.spam_tracking: Dict[int, List[float]] = defaultdict(list)
        self.muted_users: Set[int] = set()

        # Security events
        self.security_events: deque = deque(maxlen=1000)
        self.active_threats: Dict[int, SecurityEvent] = {}  # user_id -> latest threat

        # Configuration - Comprehensive moderation settings
        self.config = {
            # ML/AI Confidence Thresholds
            "warning_threshold_confidence": 0.55,  # Low confidence -> warning
            "mute_threshold_confidence": 0.75,  # Medium confidence -> mute
            "ban_threshold_confidence": 0.95,  # High confidence -> ban
            # Time Windows for Repeat Offenses
            "repeat_window_days": 30,  # Days to track repeat offenses
            "escalation_window_days": 90,  # Extended escalation window
            "escalation_multiplier": 2,  # Duration multiplier for repeats
            # Spam Detection
            "spam_threshold": 3,  # Messages count for spam
            "spam_timeframe": 30,  # Seconds
            "identical_message_limit": 3,  # Identical messages = violation
            "mention_spam_limit": 5,  # Mass mentions limit
            "caps_abuse_threshold": 0.8,  # Caps ratio for abuse
            # Content Detection
            "toxicity_threshold": 0.7,  # AI toxicity threshold
            "profanity_severity_threshold": 0.6,  # Profanity detection threshold
            "nsfw_confidence_threshold": 0.8,  # NSFW content threshold
            # Link Security
            "url_scan_enabled": True,  # Enable URL scanning
            "attachment_scan_enabled": True,  # Enable attachment scanning
            "unknown_domain_threshold": 0.3,  # Threshold for unknown domains
            # Behavioral Analysis
            "rate_limit_messages": 10,  # Messages per time window
            "rate_limit_window": 10,  # Rate limit window (seconds)
            "behavioral_anomaly_threshold": 0.8,  # Anomaly detection threshold
            # Privacy & Data Retention
            "hash_message_content": True,  # Hash sensitive content
            "log_retention_days": 90,  # Days to keep logs
            "purge_resolved_appeals_days": 30,  # Days to keep resolved appeals
            # Fail-safe Settings
            "prefer_lower_severity": True,  # When uncertain, use lower severity
            "require_human_review_threshold": 0.9,  # High confidence actions need review
            "auto_escalate_repeat_threshold": 3,  # Auto-escalate after N repeats
        }

        # Punishment Tiers - Exact specification implementation
        self.punishment_tiers = {
            ViolationSeverity.LOW: {
                "first_offense": {"action": "warning", "duration": 0},
                "second_offense": {"action": "mute", "duration": 900},  # 15 minutes
                "third_offense": {"action": "mute", "duration": 3600},  # 1 hour
                "permanent": {"action": "kick", "duration": 0},
            },
            ViolationSeverity.MEDIUM: {
                "first_offense": {"action": "mute", "duration": 3600},  # 1 hour
                "second_offense": {
                    "action": "mute",
                    "duration": 21600,
                },  # 6 hours + role removal
                "third_offense": {"action": "timeout", "duration": 86400},  # 24 hours
                "permanent": {"action": "kick", "duration": 0},
            },
            ViolationSeverity.HIGH: {
                "first_offense": {
                    "action": "mute",
                    "duration": 21600,
                },  # 6 hours + alert
                "second_offense": {"action": "timeout", "duration": 86400},  # 24 hours
                "third_offense": {"action": "ban", "duration": 604800},  # 7 days
                "permanent": {"action": "ban", "duration": 0},  # Permanent
            },
            ViolationSeverity.SEVERE: {
                "first_offense": {
                    "action": "ban",
                    "duration": 604800,
                },  # 7 days + alert
                "second_offense": {"action": "ban", "duration": 2592000},  # 30 days
                "third_offense": {"action": "ban", "duration": 0},  # Permanent
                "permanent": {"action": "ban", "duration": 0},  # Permanent
            },
        }

        # Database initialization
        self.db_path = "data/unified_security.db"
        self._init_database()

        # Performance tracking
        self.stats = {
            "messages_analyzed": 0,
            "violations_detected": 0,
            "automated_actions": 0,
            "manual_overrides": 0,
            "threat_assessments": 0,
        }

        self.logger.info(
            "🛡️ Unified Security System initialized - All features consolidated"
        )

    def _init_database(self):
        """Initialize unified security database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # User profiles table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    trust_score REAL DEFAULT 50.0,
                    punishment_level INTEGER DEFAULT 0,
                    is_trusted BOOLEAN DEFAULT FALSE,
                    is_quarantined BOOLEAN DEFAULT FALSE,
                    profile_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Violation records table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS violation_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    violation_type TEXT NOT NULL,
                    severity INTEGER NOT NULL,
                    timestamp REAL NOT NULL,
                    evidence TEXT,
                    action_taken TEXT,
                    moderator_id INTEGER,
                    resolved BOOLEAN DEFAULT FALSE
                )
            """
            )

            # Security events table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS security_events (
                    event_id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    threat_level INTEGER NOT NULL,
                    timestamp REAL NOT NULL,
                    details TEXT,
                    automated_response TEXT,
                    manual_override BOOLEAN DEFAULT FALSE
                )
            """
            )

            conn.commit()
            conn.close()

            self.logger.info("✅ Unified security database initialized")

        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise

    async def analyze_message_security(
        self, message: discord.Message
    ) -> Tuple[bool, List[ViolationRecord]]:
        """
        Comprehensive message analysis combining all detection methods
        Returns: (should_take_action, violations_detected)
        """
        if message.author.bot or not message.guild:
            return False, []

        # OWNER BYPASS: Skip all security checks for bot owner
        import os
        from config.unified_config import unified_config

        # Check if user is bot owner
        configured_owner_id = unified_config.get_owner_id()
        env_owner_id = os.getenv("OWNER_ID")

        is_owner = False
        if configured_owner_id and message.author.id == configured_owner_id:
            is_owner = True
        elif env_owner_id:
            try:
                if message.author.id == int(env_owner_id):
                    is_owner = True
            except ValueError:
                pass
        elif message.author.id == 1115739214148026469:  # Hardcoded fallback
            is_owner = True

        if is_owner:
            return False, []  # Skip all security checks for owner

        self.stats["messages_analyzed"] += 1
        violations = []

        user_id = message.author.id
        guild_id = message.guild.id
        content = message.content

        # Get or create user profile
        profile = await self.get_user_profile(user_id, guild_id)

        # Update activity tracking
        profile.last_activity = time.time()
        profile.message_count += 1

        # Track message history for spam detection
        self.message_history[user_id].append(
            {
                "content": content,
                "timestamp": time.time(),
                "channel_id": message.channel.id,
            }
        )

        # 1. SPAM DETECTION (Advanced pattern matching)
        spam_violations = await self._detect_spam(message, profile)
        violations.extend(spam_violations)

        # 2. THREAT INTELLIGENCE ANALYSIS
        threat_violations = await self._analyze_threats(message, profile)
        violations.extend(threat_violations)

        # 3. TOXICITY DETECTION
        toxicity_violations = await self._detect_toxicity(message, profile)
        violations.extend(toxicity_violations)

        # 4. BEHAVIORAL ANALYSIS
        behavioral_violations = await self._analyze_behavior(message, profile)
        violations.extend(behavioral_violations)

        # 5. AUTONOMOUS THREAT ASSESSMENT
        autonomous_violations = await self._autonomous_threat_assessment(
            message, profile
        )
        violations.extend(autonomous_violations)

        # Update profile based on violations
        if violations:
            self.stats["violations_detected"] += len(violations)
            profile.violation_history.extend(violations)

            # Adjust trust score
            severity_penalty = sum(v.severity.value * 5 for v in violations)
            profile.trust_score = max(0, profile.trust_score - severity_penalty)
            profile.is_trusted = profile.trust_score >= self.config["trusted_threshold"]

            # Check quarantine status
            if profile.trust_score <= self.config["quarantine_threshold"]:
                profile.is_quarantined = True
                profile.quarantine_reason = (
                    f"Trust score dropped to {profile.trust_score:.1f}"
                )

        # Store updated profile
        await self._save_user_profile(profile)

        # Determine if action should be taken
        should_act = len(violations) > 0 and self.config["auto_response_enabled"]

        return should_act, violations

    async def _detect_spam(
        self, message: discord.Message, profile: UserProfile
    ) -> List[ViolationRecord]:
        """Advanced spam detection with multiple pattern matching"""
        violations = []
        content = message.content
        user_id = message.author.id

        # Check for identical message spam
        recent_messages = [
            msg["content"] for msg in list(self.message_history[user_id])[-5:]
        ]
        identical_count = recent_messages.count(content)

        if identical_count >= self.config["identical_message_limit"]:
            violations.append(
                self.create_violation_record(
                    user_id=user_id,
                    guild_id=message.guild.id,
                    message=message,
                    violation_type=ViolationType.REPEATED_CONTENT,
                    severity=ViolationSeverity.MODERATE,
                    heuristic_score=0.8,
                    detection_method="identical_spam",
                    evidence={
                        "identical_messages": identical_count,
                        "message_content": content[:100],
                        "detection_method": "identical_spam",
                    },
                )
            )

        # Check message frequency spam
        now = time.time()
        spam_window = [
            t
            for t in self.spam_tracking[user_id]
            if now - t < self.config["spam_timeframe"]
        ]
        self.spam_tracking[user_id] = spam_window + [now]

        if len(spam_window) >= self.config["spam_threshold"]:
            violations.append(
                self.create_violation_record(
                    user_id=user_id,
                    guild_id=message.guild.id,
                    message=message,
                    violation_type=ViolationType.SPAM_MESSAGES,
                    severity=ViolationSeverity.MODERATE,
                    heuristic_score=0.9,
                    detection_method="frequency_spam",
                    evidence={
                        "message_frequency": len(spam_window),
                        "time_window": self.config["spam_timeframe"],
                        "detection_method": "frequency_spam",
                    },
                    action_taken="pending",
                )
            )

        # Check caps abuse
        if len(content) > 10:
            caps_ratio = sum(1 for c in content if c.isupper()) / len(content)
            if caps_ratio >= self.config["caps_abuse_threshold"]:
                violations.append(
                    ViolationRecord(
                        user_id=user_id,
                        guild_id=message.guild.id,
                        violation_type=ViolationType.CAPS_ABUSE,
                        severity=ViolationSeverity.MINOR,
                        timestamp=time.time(),
                        evidence={
                            "caps_ratio": caps_ratio,
                            "message_length": len(content),
                            "detection_method": "caps_abuse",
                        },
                        action_taken="pending",
                    )
                )

        # Check mention spam
        mentions = len(message.mentions) + len(message.role_mentions)
        if mentions >= self.config["mention_spam_limit"]:
            violations.append(
                self.create_violation_record(
                    user_id=user_id,
                    guild_id=message.guild.id,
                    message=message,
                    violation_type=ViolationType.MENTION_SPAM,
                    severity=ViolationSeverity.SERIOUS,
                    heuristic_score=0.9,
                    detection_method="mention_spam",
                    evidence={
                        "mention_count": mentions,
                        "user_mentions": len(message.mentions),
                        "role_mentions": len(message.role_mentions),
                        "detection_method": "mention_spam",
                    },
                    action_taken="pending",
                )
            )

        return violations

    async def _analyze_threats(
        self, message: discord.Message, profile: UserProfile
    ) -> List[ViolationRecord]:
        """Analyze message using 2025 threat intelligence"""
        violations = []
        content = message.content

        # Extract links
        url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        links = re.findall(url_pattern, content)

        # Analyze threat level
        threat_level, threats_found = self.threat_intelligence.analyze_threat_level(
            content, links
        )

        if threat_level >= 3:  # High threat or above
            severity_map = {
                3: ViolationSeverity.SERIOUS,
                4: ViolationSeverity.SEVERE,
                5: ViolationSeverity.CRITICAL,
            }

            violations.append(
                ViolationRecord(
                    user_id=message.author.id,
                    guild_id=message.guild.id,
                    violation_type=(
                        ViolationType.SUSPICIOUS_LINKS
                        if links
                        else ViolationType.SCAM_ATTEMPT
                    ),
                    severity=severity_map.get(threat_level, ViolationSeverity.SERIOUS),
                    timestamp=time.time(),
                    evidence={
                        "threat_level": threat_level,
                        "threats_detected": threats_found,
                        "links_found": links,
                        "detection_method": "threat_intelligence_2025",
                    },
                    action_taken="pending",
                )
            )

        return violations

    async def _detect_toxicity(
        self, message: discord.Message, profile: UserProfile
    ) -> List[ViolationRecord]:
        """AI-powered toxicity detection"""
        violations = []
        content = message.content.lower()

        # Basic toxicity patterns (can be enhanced with AI models)
        toxic_patterns = [
            r"\b(kill\s+yourself|kys)\b",
            r"\b(f[u*]ck\s+you|f[u*]ck\s+off)\b",
            r"\b(go\s+die|die\s+please)\b",
            r"\b(stupid|idiot|moron)\s+(ass|face)\b",
            r"\b(hate\s+you|i\s+hate)\b",
        ]

        toxicity_score = 0
        matched_patterns = []

        for pattern in toxic_patterns:
            if re.search(pattern, content):
                toxicity_score += 0.3
                matched_patterns.append(pattern)

        if toxicity_score >= self.config["toxicity_threshold"]:
            violations.append(
                ViolationRecord(
                    user_id=message.author.id,
                    guild_id=message.guild.id,
                    violation_type=ViolationType.TOXIC_LANGUAGE,
                    severity=(
                        ViolationSeverity.SERIOUS
                        if toxicity_score >= 0.9
                        else ViolationSeverity.MODERATE
                    ),
                    timestamp=time.time(),
                    evidence={
                        "toxicity_score": toxicity_score,
                        "matched_patterns": matched_patterns,
                        "detection_method": "pattern_toxicity",
                    },
                    action_taken="pending",
                )
            )

        return violations

    async def _analyze_behavior(
        self, message: discord.Message, profile: UserProfile
    ) -> List[ViolationRecord]:
        """Behavioral pattern analysis"""
        violations = []

        # Analyze message patterns
        content_length = len(message.content)

        # Update behavioral metrics
        if profile.message_count > 0:
            profile.avg_message_length = (
                profile.avg_message_length * (profile.message_count - 1)
                + content_length
            ) / profile.message_count
        else:
            profile.avg_message_length = content_length

        # Detect unusual behavior patterns
        if profile.message_count > 10:
            # Sudden change in message length (10x longer than average)
            if (
                content_length > profile.avg_message_length * 10
                and content_length > 500
            ):
                violations.append(
                    ViolationRecord(
                        user_id=message.author.id,
                        guild_id=message.guild.id,
                        violation_type=ViolationType.BOT_ABUSE,
                        severity=ViolationSeverity.MINOR,
                        timestamp=time.time(),
                        evidence={
                            "unusual_message_length": content_length,
                            "average_length": profile.avg_message_length,
                            "detection_method": "behavioral_analysis",
                        },
                        action_taken="pending",
                    )
                )

        return violations

    async def _autonomous_threat_assessment(
        self, message: discord.Message, profile: UserProfile
    ) -> List[ViolationRecord]:
        """Autonomous threat assessment system"""
        violations = []

        # Calculate dynamic threat level based on multiple factors
        threat_factors = {
            "trust_score_factor": max(
                0, (50 - profile.trust_score) / 50
            ),  # Lower trust = higher threat
            "violation_history_factor": min(len(profile.violation_history) / 10, 1.0),
            "account_age_factor": self._calculate_account_age_risk(message.author),
            "content_risk_factor": self._calculate_content_risk(message.content),
        }

        # Weighted threat calculation
        autonomous_threat_level = (
            threat_factors["trust_score_factor"] * 0.3
            + threat_factors["violation_history_factor"] * 0.25
            + threat_factors["account_age_factor"] * 0.2
            + threat_factors["content_risk_factor"] * 0.25
        )

        # If autonomous threat level is high, create security event
        if autonomous_threat_level >= 0.7:
            event = SecurityEvent(
                event_id=hashlib.md5(
                    f"{message.author.id}{message.id}{time.time()}".encode()
                ).hexdigest()[:8],
                user_id=message.author.id,
                guild_id=message.guild.id,
                event_type="autonomous_threat_detection",
                threat_level=int(autonomous_threat_level * 5) + 1,
                timestamp=time.time(),
                details={
                    "threat_factors": threat_factors,
                    "calculated_threat_level": autonomous_threat_level,
                    "message_content": message.content[:200],
                    "channel_id": message.channel.id,
                },
            )

            self.security_events.append(event)
            self.active_threats[message.author.id] = event

            # Create violation for high autonomous threat
            violations.append(
                ViolationRecord(
                    user_id=message.author.id,
                    guild_id=message.guild.id,
                    violation_type=ViolationType.EVASION_ATTEMPT,
                    severity=ViolationSeverity.SERIOUS,
                    timestamp=time.time(),
                    evidence={
                        "autonomous_threat_level": autonomous_threat_level,
                        "threat_factors": threat_factors,
                        "detection_method": "autonomous_assessment",
                    },
                    action_taken="pending",
                )
            )

        return violations

    def _calculate_account_age_risk(self, user: discord.Member) -> float:
        """Calculate risk factor based on account age"""
        account_age_days = (datetime.now(timezone.utc) - user.created_at).days

        if account_age_days < 1:
            return 1.0  # Very high risk
        elif account_age_days < 7:
            return 0.8  # High risk
        elif account_age_days < 30:
            return 0.4  # Medium risk
        else:
            return 0.1  # Low risk

    def _calculate_content_risk(self, content: str) -> float:
        """Calculate content risk factor"""
        risk_factors = 0.0

        # Check for URLs
        if re.search(r"http[s]?://", content):
            risk_factors += 0.2

        # Check for excessive emojis
        emoji_count = len(re.findall(r"[😀-🿿]|:[a-zA-Z0-9_]+:", content))
        if emoji_count > 5:
            risk_factors += 0.1

        # Check for promotional keywords
        promo_keywords = [
            "free",
            "win",
            "prize",
            "gift",
            "click",
            "link",
            "join",
            "server",
        ]
        keyword_matches = sum(
            1 for keyword in promo_keywords if keyword in content.lower()
        )
        if keyword_matches >= 3:
            risk_factors += 0.3

        return min(risk_factors, 1.0)

    async def handle_violations(
        self, message: discord.Message, violations: List[ViolationRecord]
    ) -> Dict[str, Any]:
        """Handle detected violations with dynamic punishment system"""
        if not violations:
            return {"action_taken": "none", "violations_detected": 0}

        user_id = message.author.id
        guild_id = message.guild.id
        profile = await self.get_user_profile(user_id, guild_id)

        # Determine punishment level based on violation history and severity
        total_severity = sum(v.severity.value for v in violations)
        current_punishment_level = min(
            profile.punishment_level + 1, len(self.config["punishment_escalation"]) - 1
        )

        # Apply punishment
        punishment_duration = self.config["punishment_escalation"][
            current_punishment_level
        ]
        action_taken = "warning"

        try:
            if punishment_duration == -1:  # Ban
                await message.author.ban(
                    reason=f"Security violation - Level {current_punishment_level}"
                )
                action_taken = "ban"
            elif punishment_duration > 0:  # Timeout
                timeout_until = datetime.now(timezone.utc) + timedelta(
                    seconds=punishment_duration
                )
                await message.author.timeout(
                    timeout_until,
                    reason=f"Security violation - Level {current_punishment_level}",
                )
                action_taken = f"timeout_{punishment_duration}s"
                self.muted_users.add(user_id)
            else:  # Warning only
                action_taken = "warning"

            # Update profile
            profile.punishment_level = current_punishment_level
            for violation in violations:
                violation.action_taken = action_taken

            # Save violations to database
            await self._save_violations(violations)
            await self._save_user_profile(profile)

            # Send security response
            await self._send_security_response(message, violations, action_taken)

            self.stats["automated_actions"] += 1

            return {
                "action_taken": action_taken,
                "violations_detected": len(violations),
                "punishment_level": current_punishment_level,
                "total_severity": total_severity,
            }

        except Exception as e:
            self.logger.error(f"Error handling violations for {user_id}: {e}")
            return {
                "action_taken": "error",
                "violations_detected": len(violations),
                "error": str(e),
            }

    async def _send_security_response(
        self,
        message: discord.Message,
        violations: List[ViolationRecord],
        action_taken: str,
    ):
        """Send appropriate security response message"""
        try:
            violation_types = [
                v.violation_type.value.replace("_", " ").title() for v in violations
            ]

            if action_taken == "warning":
                response = f"⚠️ {message.author.mention}, please avoid: {', '.join(violation_types)}. This is a warning."
            elif action_taken.startswith("timeout"):
                duration = action_taken.split("_")[1]
                response = f"🔇 {message.author.mention} has been timed out for {duration} due to: {', '.join(violation_types)}"
            elif action_taken == "ban":
                response = f"🔨 {message.author.mention} has been banned due to severe violations: {', '.join(violation_types)}"
            else:
                response = f"🛡️ Security action taken against {message.author.mention}: {action_taken}"

            await message.channel.send(response, delete_after=30)

        except Exception as e:
            self.logger.error(f"Error sending security response: {e}")

    async def get_user_profile(self, user_id: int, guild_id: int) -> UserProfile:
        """Get or create user profile"""
        profile_key = f"{guild_id}:{user_id}"

        if profile_key not in self.user_profiles:
            # Try loading from database
            profile = await self._load_user_profile(user_id, guild_id)
            if not profile:
                # Create new profile
                profile = UserProfile(user_id=user_id, guild_id=guild_id)

            self.user_profiles[profile_key] = profile

        return self.user_profiles[profile_key]

    async def _load_user_profile(
        self, user_id: int, guild_id: int
    ) -> Optional[UserProfile]:
        """Load user profile from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT profile_data FROM user_profiles WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id),
            )

            result = cursor.fetchone()
            conn.close()

            if result:
                profile_data = json.loads(result[0])
                profile = UserProfile(**profile_data)

                # Load violation history
                profile.violation_history = await self._load_user_violations(
                    user_id, guild_id
                )

                return profile

        except Exception as e:
            self.logger.error(f"Error loading user profile {user_id}: {e}")

        return None

    async def _save_user_profile(self, profile: UserProfile):
        """Save user profile to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Prepare profile data (exclude violation_history as it's stored separately)
            profile_dict = asdict(profile)
            profile_dict.pop("violation_history", None)  # Remove violation history

            profile_key = f"{profile.guild_id}:{profile.user_id}"

            cursor.execute(
                """
                INSERT OR REPLACE INTO user_profiles 
                (id, user_id, guild_id, trust_score, punishment_level, is_trusted, is_quarantined, profile_data, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
                (
                    profile_key,
                    profile.user_id,
                    profile.guild_id,
                    profile.trust_score,
                    profile.punishment_level,
                    profile.is_trusted,
                    profile.is_quarantined,
                    json.dumps(profile_dict),
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Error saving user profile {profile.user_id}: {e}")

    async def _save_violations(self, violations: List[ViolationRecord]):
        """Save violations to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for violation in violations:
                cursor.execute(
                    """
                    INSERT INTO violation_records 
                    (user_id, guild_id, violation_type, severity, timestamp, evidence, action_taken, moderator_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        violation.user_id,
                        violation.guild_id,
                        violation.violation_type.value,
                        violation.severity.value,
                        violation.timestamp,
                        json.dumps(violation.evidence),
                        violation.action_taken,
                        violation.moderator_id,
                    ),
                )

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Error saving violations: {e}")

    async def _load_user_violations(
        self, user_id: int, guild_id: int
    ) -> List[ViolationRecord]:
        """Load user violation history from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT user_id, guild_id, violation_type, severity, timestamp, evidence, action_taken, moderator_id, resolved, appeal_status
                FROM violation_records 
                WHERE user_id = ? AND guild_id = ?
                ORDER BY timestamp DESC
                LIMIT 50
            """,
                (user_id, guild_id),
            )

            results = cursor.fetchall()
            conn.close()

            violations = []
            for row in results:
                violations.append(
                    ViolationRecord(
                        user_id=row[0],
                        guild_id=row[1],
                        violation_type=ViolationType(row[2]),
                        severity=ViolationSeverity(row[3]),
                        timestamp=row[4],
                        evidence=json.loads(row[5]) if row[5] else {},
                        action_taken=row[6],
                        moderator_id=row[7],
                        resolved=bool(row[8]),
                        appeal_status=row[9],
                    )
                )

            return violations

        except Exception as e:
            self.logger.error(f"Error loading user violations {user_id}: {e}")
            return []

    def get_security_stats(self) -> Dict[str, Any]:
        """Get comprehensive security statistics"""
        total_users = len(self.user_profiles)
        trusted_users = sum(1 for p in self.user_profiles.values() if p.is_trusted)
        quarantined_users = sum(
            1 for p in self.user_profiles.values() if p.is_quarantined
        )

        avg_trust_score = 0.0
        if total_users > 0:
            avg_trust_score = (
                sum(p.trust_score for p in self.user_profiles.values()) / total_users
            )

        # Calculate recent violations
        now = time.time()
        recent_violations = sum(
            len([v for v in p.violation_history if now - v.timestamp < 86400])
            for p in self.user_profiles.values()
        )

        return {
            "total_tracked_users": total_users,
            "trusted_users": trusted_users,
            "quarantined_users": quarantined_users,
            "average_trust_score": avg_trust_score,
            "violations_last_24h": recent_violations,
            "total_violations_all_time": self.stats["violations_detected"],
            "protection_level": (
                "Maximum" if self.config["auto_response_enabled"] else "Manual"
            ),
            "system_status": "Active",
            "messages_analyzed": self.stats["messages_analyzed"],
            "automated_actions": self.stats["automated_actions"],
            "threat_assessments": self.stats["threat_assessments"],
        }

    async def get_user_security_report(
        self, user_id: int, guild_id: int = None
    ) -> Dict[str, Any]:
        """Get comprehensive security report for a user"""
        # Find user profile (search all guilds if guild_id not specified)
        profile = None
        if guild_id:
            profile = await self.get_user_profile(user_id, guild_id)
        else:
            # Search all profiles for this user
            for profile_key, p in self.user_profiles.items():
                if p.user_id == user_id:
                    profile = p
                    break

        if not profile:
            return {"error": "User not found in security system"}

        # Calculate recent violations
        now = time.time()
        recent_violations = [
            v for v in profile.violation_history if now - v.timestamp < 86400
        ]

        # Behavioral summary
        behavioral_summary = {
            "avg_message_length": profile.avg_message_length,
            "channel_diversity": profile.channel_diversity,
            "activity_pattern": profile.activity_pattern,
        }

        return {
            "user_id": user_id,
            "trust_score": profile.trust_score,
            "is_trusted": profile.is_trusted,
            "total_violations": len(profile.violation_history),
            "recent_violations_24h": len(recent_violations),
            "violation_streak": profile.punishment_level,
            "punishment_level": profile.punishment_level,
            "positive_contributions": profile.positive_contributions,
            "quarantine_status": "active" if profile.is_quarantined else "none",
            "behavioral_summary": behavioral_summary,
            "last_violation": max(
                (v.timestamp for v in profile.violation_history), default=None
            ),
        }

    async def manual_override(
        self, moderator_id: int, user_id: int, action: str, reason: str
    ) -> bool:
        """Allow manual override of security actions"""
        try:
            # Log manual override
            event = SecurityEvent(
                event_id=hashlib.md5(
                    f"{moderator_id}{user_id}{time.time()}".encode()
                ).hexdigest()[:8],
                user_id=user_id,
                guild_id=0,  # Will be updated with actual guild
                event_type="manual_override",
                threat_level=1,
                timestamp=time.time(),
                details={
                    "moderator_id": moderator_id,
                    "override_action": action,
                    "reason": reason,
                },
                manual_override=True,
            )

            self.security_events.append(event)
            self.stats["manual_overrides"] += 1

            # Remove from active threats if applicable
            if user_id in self.active_threats:
                del self.active_threats[user_id]

            self.logger.info(
                f"Manual override by {moderator_id}: {action} for user {user_id} - {reason}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Manual override failed: {e}")
            return False

    def create_violation_record(
        self,
        user_id: int,
        guild_id: int,
        message: Optional[discord.Message],
        violation_type: ViolationType,
        severity: ViolationSeverity,
        heuristic_score: float = 0.8,
        ml_confidence: float = 0.0,
        detection_method: str = "heuristic",
        evidence: Dict[str, Any] = None,
    ) -> ViolationRecord:
        """Helper method to create properly formatted ViolationRecord instances"""
        if evidence is None:
            evidence = {}

        return ViolationRecord(
            user_id=user_id,
            guild_id=guild_id,
            message_id=message.id if message else None,
            channel_id=message.channel.id if message else 0,
            violation_type=violation_type,
            severity=severity,
            timestamp=time.time(),
            heuristic_score=heuristic_score,
            ml_confidence=ml_confidence,
            final_confidence=max(heuristic_score, ml_confidence),
            detection_method=detection_method,
            message_content=message.content[:200] if message else "",
            evidence=evidence,
        )

    async def shutdown(self):
        """Graceful shutdown of security system"""
        self.logger.info("🔄 Shutting down Unified Security System...")

        # Save all user profiles
        for profile in self.user_profiles.values():
            await self._save_user_profile(profile)

        # Clear memory structures
        self.user_profiles.clear()
        self.message_history.clear()
        self.spam_tracking.clear()
        self.security_events.clear()
        self.active_threats.clear()

        self.logger.info("✅ Unified Security System shutdown complete")
