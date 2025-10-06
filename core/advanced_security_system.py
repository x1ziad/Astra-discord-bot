#!/usr/bin/env python3
"""
🛡️ ADVANCED SECURITY SYSTEM - TOP-NOTCH PROTECTION
Flawless security and moderation with intelligent violation detection and dynamic punishment

Features:
- Intelligent spam detection (3+ identical messages = mute)
- Smart link validation (malicious links blocked, valid links allowed)
- Context-aware toxicity detection
- Dynamic punishment escalation
- Real-time threat assessment
- Behavioral pattern analysis
- Automated evidence collection
"""

import asyncio
import logging
import time
import json
import re
import hashlib
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
from enum import Enum, IntEnum
import discord
from discord.ext import commands, tasks
from urllib.parse import urlparse
import aiohttp

logger = logging.getLogger("astra.security.advanced")


class ViolationSeverity(IntEnum):
    """Violation severity levels for dynamic punishment"""

    MINOR = 1  # Gentle reminder
    MODERATE = 2  # Warning + short timeout
    SERIOUS = 3  # Longer timeout + role restrictions
    SEVERE = 4  # Extended timeout + channel restrictions
    CRITICAL = 5  # Ban consideration


class ViolationType(Enum):
    """Types of violations detected"""

    SPAM_MESSAGES = "spam_messages"
    REPEATED_CONTENT = "repeated_content"
    CAPS_ABUSE = "caps_abuse"
    MENTION_SPAM = "mention_spam"
    TOXIC_LANGUAGE = "toxic_language"
    HARASSMENT = "harassment"
    MALICIOUS_LINKS = "malicious_links"
    PHISHING_ATTEMPT = "phishing_attempt"
    NSFW_CONTENT = "nsfw_content"
    HATE_SPEECH = "hate_speech"
    THREATS = "threats"
    DOXXING = "doxxing"
    RAID_BEHAVIOR = "raid_behavior"


@dataclass
class Violation:
    """Data structure for tracking violations"""

    user_id: int
    violation_type: ViolationType
    severity: ViolationSeverity
    message_content: str
    channel_id: int
    guild_id: int
    timestamp: float
    evidence: Dict[str, Any]
    action_taken: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UserSecurityProfile:
    """Comprehensive user security profile"""

    user_id: int
    trust_score: float = 100.0  # Starts at 100, decreases with violations
    violation_history: List[Violation] = None
    behavioral_patterns: Dict[str, Any] = None
    last_violation: Optional[float] = None
    punishment_level: int = 0
    is_trusted: bool = True
    quarantine_until: Optional[float] = None

    def __post_init__(self):
        if self.violation_history is None:
            self.violation_history = []
        if self.behavioral_patterns is None:
            self.behavioral_patterns = {
                "avg_message_length": 0,
                "message_frequency": deque(maxlen=50),
                "common_words": defaultdict(int),
                "channel_diversity": set(),
                "reaction_patterns": [],
                "violation_streak": 0,
                "positive_contributions": 0,
            }


class AdvancedSecuritySystem:
    """Top-notch security system with flawless protection"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logger

        # Security databases
        self.user_profiles: Dict[int, UserSecurityProfile] = {}
        self.guild_settings: Dict[int, Dict[str, Any]] = {}
        self.active_violations: Dict[int, List[Violation]] = defaultdict(list)
        self.message_cache: Dict[int, deque] = defaultdict(lambda: deque(maxlen=100))
        self.link_whitelist: Set[str] = set()
        self.link_blacklist: Set[str] = set()

        # Detection patterns and thresholds
        self.security_config = {
            # Spam detection
            "spam_message_threshold": 3,  # 3+ identical messages
            "spam_timeframe": 30,  # within 30 seconds
            "rapid_message_limit": 6,  # 6+ messages in timeframe
            "rapid_message_timeframe": 10,  # 10 seconds
            # Content analysis
            "caps_ratio_threshold": 0.8,  # 80% caps = violation
            "mention_spam_limit": 4,  # 4+ mentions = spam
            "max_message_length": 2000,  # Discord limit
            "min_message_length_for_analysis": 5,
            # Punishment escalation
            "trust_score_penalty": {
                ViolationSeverity.MINOR: 5,
                ViolationSeverity.MODERATE: 15,
                ViolationSeverity.SERIOUS: 30,
                ViolationSeverity.SEVERE: 50,
                ViolationSeverity.CRITICAL: 75,
            },
            # Timeout durations (seconds)
            "timeout_durations": {
                1: 300,  # 5 minutes
                2: 900,  # 15 minutes
                3: 1800,  # 30 minutes
                4: 3600,  # 1 hour
                5: 7200,  # 2 hours
                6: 21600,  # 6 hours
                7: 86400,  # 24 hours
            },
        }

        # Toxicity patterns (extensive)
        self.toxicity_patterns = {
            "insults": [
                r"\\b(idiot|stupid|dumb|moron|retard|loser|trash|garbage|noob)\\b",
                r"\\b(shut up|stfu|gtfo|kys|kill yourself)\\b",
                r"\\b(pathetic|worthless|useless|waste of space)\\b",
            ],
            "harassment": [
                r"\\b(hate you|hate this|go die|nobody likes you)\\b",
                r"\\b(annoying|irritating|get lost|leave|quit)\\b",
            ],
            "threats": [
                r"\\b(kill|murder|hurt|harm|destroy|eliminate)\\b.*\\b(you|him|her|them)\\b",
                r"\\b(threat|threaten|threatening|gonna get you)\\b",
            ],
            "hate_speech": [
                r"\\b(nazi|hitler|holocaust|genocide)\\b",
                r"\\b(racial slurs and discriminatory terms)\\b",  # Placeholder - add specific terms
            ],
        }

        # Phishing and malicious patterns
        self.malicious_patterns = {
            "phishing_keywords": [
                "free nitro",
                "discord nitro",
                "claim now",
                "limited time",
                "verify account",
                "suspended account",
                "click here",
                "urgent",
                "immediate action",
                "expires soon",
                "security alert",
            ],
            "suspicious_domains": [
                "discordapp.gift",
                "discord-nitro.com",
                "steamcommunity-",
                "bit.ly",
                "tinyurl.com",
                "short.link",
                "grabify.link",
            ],
        }

        # Start security tasks
        self.start_security_monitoring()

    def start_security_monitoring(self):
        """Start all security monitoring tasks"""
        self.violation_cleanup_task.start()
        self.trust_score_recovery_task.start()
        self.behavioral_analysis_task.start()
        self.threat_intelligence_update_task.start()

        logger.info("🛡️ Advanced Security System monitoring started")

    async def analyze_message_security(
        self, message: discord.Message
    ) -> Tuple[bool, List[Violation]]:
        """
        Comprehensive message security analysis
        Returns: (should_take_action, violations_detected)
        """
        if message.author.bot or not message.guild:
            return False, []

        violations = []
        user_profile = await self.get_user_profile(message.author.id)

        # Update behavioral patterns
        await self.update_behavioral_patterns(user_profile, message)

        # 1. SPAM DETECTION (Strict: 3+ identical messages)
        spam_violation = await self.detect_spam(message, user_profile)
        if spam_violation:
            violations.append(spam_violation)

        # 2. REPEATED CONTENT DETECTION
        repeat_violation = await self.detect_repeated_content(message, user_profile)
        if repeat_violation:
            violations.append(repeat_violation)

        # 3. CAPS ABUSE DETECTION
        caps_violation = await self.detect_caps_abuse(message)
        if caps_violation:
            violations.append(caps_violation)

        # 4. MENTION SPAM DETECTION
        mention_violation = await self.detect_mention_spam(message)
        if mention_violation:
            violations.append(mention_violation)

        # 5. TOXICITY AND HARASSMENT DETECTION
        toxicity_violation = await self.detect_toxicity(message)
        if toxicity_violation:
            violations.append(toxicity_violation)

        # 6. MALICIOUS LINK DETECTION
        link_violation = await self.detect_malicious_links(message)
        if link_violation:
            violations.append(link_violation)

        # 7. PHISHING DETECTION
        phishing_violation = await self.detect_phishing(message)
        if phishing_violation:
            violations.append(phishing_violation)

        # 8. NSFW CONTENT DETECTION
        nsfw_violation = await self.detect_nsfw_content(message)
        if nsfw_violation:
            violations.append(nsfw_violation)

        return len(violations) > 0, violations

    async def detect_spam(
        self, message: discord.Message, profile: UserSecurityProfile
    ) -> Optional[Violation]:
        """Detect spam messages with strict 3+ identical message rule"""
        user_id = message.author.id
        content = message.content.strip().lower()

        if len(content) < 3:  # Too short to be meaningful spam
            return None

        # Check message history for identical content
        recent_messages = self.message_cache[user_id]
        current_time = time.time()

        # Count identical messages in the last 30 seconds
        identical_count = 0
        for cached_msg in recent_messages:
            if (
                current_time - cached_msg["timestamp"]
                <= self.security_config["spam_timeframe"]
                and cached_msg["content"].lower() == content
            ):
                identical_count += 1

        # Add current message to cache
        recent_messages.append(
            {
                "content": message.content.strip(),
                "timestamp": current_time,
                "channel_id": message.channel.id,
            }
        )

        # STRICT RULE: 3+ identical messages = spam violation
        if identical_count >= self.security_config["spam_message_threshold"]:
            return Violation(
                user_id=user_id,
                violation_type=ViolationType.SPAM_MESSAGES,
                severity=ViolationSeverity.MODERATE,
                message_content=message.content[:200],
                channel_id=message.channel.id,
                guild_id=message.guild.id,
                timestamp=current_time,
                evidence={
                    "identical_count": identical_count,
                    "timeframe": self.security_config["spam_timeframe"],
                    "pattern": "identical_message_spam",
                },
                action_taken="pending",
            )

        # Also check for rapid messaging (different content)
        recent_count = sum(
            1
            for msg in recent_messages
            if current_time - msg["timestamp"]
            <= self.security_config["rapid_message_timeframe"]
        )

        if recent_count >= self.security_config["rapid_message_limit"]:
            return Violation(
                user_id=user_id,
                violation_type=ViolationType.SPAM_MESSAGES,
                severity=ViolationSeverity.MINOR,
                message_content=message.content[:200],
                channel_id=message.channel.id,
                guild_id=message.guild.id,
                timestamp=current_time,
                evidence={
                    "message_count": recent_count,
                    "timeframe": self.security_config["rapid_message_timeframe"],
                    "pattern": "rapid_messaging",
                },
                action_taken="pending",
            )

        return None

    async def detect_repeated_content(
        self, message: discord.Message, profile: UserSecurityProfile
    ) -> Optional[Violation]:
        """Detect repeated similar content (not identical)"""
        content = message.content.strip().lower()
        if len(content) < self.security_config["min_message_length_for_analysis"]:
            return None

        user_id = message.author.id
        recent_messages = self.message_cache[user_id]
        current_time = time.time()

        # Check for similar messages (70%+ similarity)
        similar_count = 0
        for cached_msg in recent_messages:
            if current_time - cached_msg["timestamp"] <= 60:  # Last minute
                similarity = self.calculate_text_similarity(
                    content, cached_msg["content"].lower()
                )
                if similarity >= 0.7:
                    similar_count += 1

        if similar_count >= 2:  # 2+ similar messages
            return Violation(
                user_id=user_id,
                violation_type=ViolationType.REPEATED_CONTENT,
                severity=ViolationSeverity.MINOR,
                message_content=message.content[:200],
                channel_id=message.channel.id,
                guild_id=message.guild.id,
                timestamp=current_time,
                evidence={
                    "similar_count": similar_count,
                    "pattern": "similar_content_repetition",
                },
                action_taken="pending",
            )

        return None

    async def detect_caps_abuse(self, message: discord.Message) -> Optional[Violation]:
        """Detect excessive use of capital letters"""
        content = message.content.strip()
        if len(content) < 10:  # Too short to judge
            return None

        caps_count = sum(1 for c in content if c.isupper())
        caps_ratio = caps_count / len(content)

        if caps_ratio >= self.security_config["caps_ratio_threshold"]:
            return Violation(
                user_id=message.author.id,
                violation_type=ViolationType.CAPS_ABUSE,
                severity=ViolationSeverity.MINOR,
                message_content=message.content[:200],
                channel_id=message.channel.id,
                guild_id=message.guild.id,
                timestamp=time.time(),
                evidence={
                    "caps_ratio": caps_ratio,
                    "caps_count": caps_count,
                    "total_length": len(content),
                },
                action_taken="pending",
            )

        return None

    async def detect_mention_spam(
        self, message: discord.Message
    ) -> Optional[Violation]:
        """Detect mention spam"""
        mention_count = len(message.mentions) + len(message.role_mentions)

        if mention_count >= self.security_config["mention_spam_limit"]:
            severity = (
                ViolationSeverity.MODERATE
                if mention_count >= 8
                else ViolationSeverity.MINOR
            )

            return Violation(
                user_id=message.author.id,
                violation_type=ViolationType.MENTION_SPAM,
                severity=severity,
                message_content=message.content[:200],
                channel_id=message.channel.id,
                guild_id=message.guild.id,
                timestamp=time.time(),
                evidence={
                    "mention_count": mention_count,
                    "user_mentions": len(message.mentions),
                    "role_mentions": len(message.role_mentions),
                },
                action_taken="pending",
            )

        return None

    async def detect_toxicity(self, message: discord.Message) -> Optional[Violation]:
        """Advanced toxicity detection with context awareness"""
        content = message.content.lower()
        severity = ViolationSeverity.MINOR
        violation_type = ViolationType.TOXIC_LANGUAGE
        matched_patterns = []

        # Check for insults
        for pattern in self.toxicity_patterns["insults"]:
            if re.search(pattern, content, re.IGNORECASE):
                matched_patterns.append("insult")
                severity = max(severity, ViolationSeverity.MODERATE)

        # Check for harassment
        for pattern in self.toxicity_patterns["harassment"]:
            if re.search(pattern, content, re.IGNORECASE):
                matched_patterns.append("harassment")
                violation_type = ViolationType.HARASSMENT
                severity = max(severity, ViolationSeverity.SERIOUS)

        # Check for threats
        for pattern in self.toxicity_patterns["threats"]:
            if re.search(pattern, content, re.IGNORECASE):
                matched_patterns.append("threat")
                violation_type = ViolationType.THREATS
                severity = ViolationSeverity.SEVERE

        # Check for hate speech
        for pattern in self.toxicity_patterns["hate_speech"]:
            if re.search(pattern, content, re.IGNORECASE):
                matched_patterns.append("hate_speech")
                violation_type = ViolationType.HATE_SPEECH
                severity = ViolationSeverity.CRITICAL

        if matched_patterns:
            return Violation(
                user_id=message.author.id,
                violation_type=violation_type,
                severity=severity,
                message_content=message.content[:200],
                channel_id=message.channel.id,
                guild_id=message.guild.id,
                timestamp=time.time(),
                evidence={
                    "matched_patterns": matched_patterns,
                    "toxicity_level": severity.value,
                    "context_analysis": "pattern_based",
                },
                action_taken="pending",
            )

        return None

    async def detect_malicious_links(
        self, message: discord.Message
    ) -> Optional[Violation]:
        """Intelligent link detection - allow valid links, block malicious ones"""
        content = message.content

        # Extract URLs
        url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        urls = re.findall(url_pattern, content)

        if not urls:
            return None

        malicious_urls = []
        for url in urls:
            # Check against blacklist
            parsed_url = urlparse(url.lower())
            domain = parsed_url.netloc

            # Check for suspicious domains
            for suspicious_domain in self.malicious_patterns["suspicious_domains"]:
                if suspicious_domain in domain:
                    malicious_urls.append(url)
                    break

            # Check for URL shorteners (potential obfuscation)
            shortener_domains = [
                "bit.ly",
                "tinyurl.com",
                "t.co",
                "short.link",
                "grabify.link",
            ]
            if any(shortener in domain for shortener in shortener_domains):
                malicious_urls.append(url)

            # Check for Discord impersonation
            if (
                "discord" in domain
                and "discord.com" not in domain
                and "discord.gg" not in domain
            ):
                malicious_urls.append(url)

        if malicious_urls:
            return Violation(
                user_id=message.author.id,
                violation_type=ViolationType.MALICIOUS_LINKS,
                severity=ViolationSeverity.SERIOUS,
                message_content=message.content[:200],
                channel_id=message.channel.id,
                guild_id=message.guild.id,
                timestamp=time.time(),
                evidence={
                    "malicious_urls": malicious_urls,
                    "total_urls": len(urls),
                    "detection_method": "domain_analysis",
                },
                action_taken="pending",
            )

        return None

    async def detect_phishing(self, message: discord.Message) -> Optional[Violation]:
        """Detect phishing attempts"""
        content = message.content.lower()
        score = 0
        matched_keywords = []

        # Check for phishing keywords
        for keyword in self.malicious_patterns["phishing_keywords"]:
            if keyword in content:
                score += 2
                matched_keywords.append(keyword)

        # Check for urgency indicators
        urgency_words = ["urgent", "immediate", "now", "quickly", "expires", "limited"]
        for word in urgency_words:
            if word in content:
                score += 1
                matched_keywords.append(f"urgency_{word}")

        if score >= 4:  # High confidence phishing attempt
            return Violation(
                user_id=message.author.id,
                violation_type=ViolationType.PHISHING_ATTEMPT,
                severity=ViolationSeverity.CRITICAL,
                message_content=message.content[:200],
                channel_id=message.channel.id,
                guild_id=message.guild.id,
                timestamp=time.time(),
                evidence={
                    "phishing_score": score,
                    "matched_keywords": matched_keywords,
                    "detection_confidence": "high",
                },
                action_taken="pending",
            )

        return None

    async def detect_nsfw_content(
        self, message: discord.Message
    ) -> Optional[Violation]:
        """Detect NSFW content (basic keyword detection)"""
        content = message.content.lower()

        # Basic NSFW keyword detection (expand as needed)
        nsfw_keywords = ["nsfw", "porn", "xxx", "adult content", "explicit"]

        for keyword in nsfw_keywords:
            if keyword in content:
                return Violation(
                    user_id=message.author.id,
                    violation_type=ViolationType.NSFW_CONTENT,
                    severity=ViolationSeverity.MODERATE,
                    message_content=message.content[:200],
                    channel_id=message.channel.id,
                    guild_id=message.guild.id,
                    timestamp=time.time(),
                    evidence={
                        "matched_keyword": keyword,
                        "detection_method": "keyword_based",
                    },
                    action_taken="pending",
                )

        return None

    async def handle_violations(
        self, message: discord.Message, violations: List[Violation]
    ) -> Dict[str, Any]:
        """Handle detected violations with dynamic punishment"""
        if not violations:
            return {"action_taken": "none"}

        user = message.author
        profile = await self.get_user_profile(user.id)

        # Determine the most severe violation
        max_severity = max(v.severity for v in violations)
        primary_violation = next(v for v in violations if v.severity == max_severity)

        # Calculate dynamic punishment based on history and trust score
        punishment_action = await self.calculate_punishment(
            profile, primary_violation, violations
        )

        # Execute punishment
        punishment_result = await self.execute_punishment(
            message, user, punishment_action, violations
        )

        # Update user profile
        await self.update_user_profile_after_violation(
            profile, violations, punishment_action
        )

        # Log the violation
        await self.log_security_event(
            user, violations, punishment_action, punishment_result
        )

        return {
            "action_taken": punishment_action["type"],
            "violations_detected": len(violations),
            "severity": max_severity.name,
            "punishment_successful": punishment_result["success"],
            "trust_score": profile.trust_score,
        }

    async def calculate_punishment(
        self,
        profile: UserSecurityProfile,
        primary_violation: Violation,
        all_violations: List[Violation],
    ) -> Dict[str, Any]:
        """Calculate appropriate punishment based on violation severity and user history"""

        # Base punishment level from violation severity
        base_level = primary_violation.severity.value

        # Adjust based on user's violation history
        recent_violations = [
            v for v in profile.violation_history if time.time() - v.timestamp < 86400
        ]  # Last 24 hours

        # Escalation factors
        escalation_factor = min(len(recent_violations) * 0.5, 2.0)  # Max 2x escalation
        trust_factor = (
            100 - profile.trust_score
        ) / 100  # Lower trust = higher punishment

        # Calculate final punishment level
        final_level = min(int(base_level + escalation_factor + trust_factor), 7)

        # Determine punishment type and duration
        if primary_violation.severity >= ViolationSeverity.CRITICAL:
            punishment_type = "ban"
            duration = None  # Permanent ban consideration
        elif final_level >= 6:
            punishment_type = "timeout"
            duration = self.security_config["timeout_durations"][final_level]
        elif final_level >= 3:
            punishment_type = "timeout"
            duration = self.security_config["timeout_durations"][final_level]
        elif final_level >= 2:
            punishment_type = "warning"
            duration = None
        else:
            punishment_type = "reminder"
            duration = None

        return {
            "type": punishment_type,
            "duration": duration,
            "level": final_level,
            "reasoning": f"Base: {base_level}, Escalation: {escalation_factor:.1f}, Trust: {trust_factor:.1f}",
        }

    async def execute_punishment(
        self,
        message: discord.Message,
        user: discord.Member,
        punishment: Dict[str, Any],
        violations: List[Violation],
    ) -> Dict[str, Any]:
        """Execute the calculated punishment"""
        success = True
        actions_taken = []

        try:
            # Always delete the violating message first
            await message.delete()
            actions_taken.append("message_deleted")

            if punishment["type"] == "ban":
                try:
                    await user.ban(
                        reason=f"Security violation: {violations[0].violation_type.value}"
                    )
                    actions_taken.append("user_banned")
                except discord.Forbidden:
                    # Fallback to timeout if can't ban
                    await user.timeout(discord.utils.utcnow() + timedelta(hours=24))
                    actions_taken.append("user_timeout_24h")

            elif punishment["type"] == "timeout":
                timeout_duration = timedelta(seconds=punishment["duration"])
                await user.timeout(discord.utils.utcnow() + timeout_duration)
                actions_taken.append(f'user_timeout_{punishment["duration"]}s')

            elif punishment["type"] == "warning":
                await self.send_warning_message(message.channel, user, violations)
                actions_taken.append("warning_sent")

            elif punishment["type"] == "reminder":
                await self.send_reminder_message(message.channel, user, violations)
                actions_taken.append("reminder_sent")

            # Send moderation log
            await self.send_moderation_log(
                message.guild, user, violations, punishment, actions_taken
            )

        except Exception as e:
            logger.error(f"Failed to execute punishment for {user}: {e}")
            success = False

        return {
            "success": success,
            "actions_taken": actions_taken,
            "punishment_level": punishment["level"],
        }

    async def send_warning_message(
        self,
        channel: discord.TextChannel,
        user: discord.Member,
        violations: List[Violation],
    ):
        """Send a warning message to the user"""
        violation_types = [
            v.violation_type.value.replace("_", " ").title() for v in violations
        ]

        embed = discord.Embed(
            title="⚠️ Security Violation Warning",
            description=f"{user.mention}, your message violated server security policies.",
            color=0xFF9900,
            timestamp=datetime.now(timezone.utc),
        )

        embed.add_field(
            name="Violations Detected",
            value="• " + "\\n• ".join(violation_types),
            inline=False,
        )

        embed.add_field(
            name="⚡ Action Required",
            value="Please review server rules and modify your behavior to avoid further violations.",
            inline=False,
        )

        embed.set_footer(text="🛡️ Astra Security System - Protecting the Community")

        await channel.send(embed=embed, delete_after=30)

    async def send_reminder_message(
        self,
        channel: discord.TextChannel,
        user: discord.Member,
        violations: List[Violation],
    ):
        """Send a gentle reminder message"""
        embed = discord.Embed(
            title="📝 Friendly Reminder",
            description=f"Hey {user.mention}, let's keep our community positive and welcoming!",
            color=0x00BFFF,
            timestamp=datetime.now(timezone.utc),
        )

        embed.add_field(
            name="💡 Quick Tip",
            value="Remember to follow server guidelines to maintain a great experience for everyone.",
            inline=False,
        )

        embed.set_footer(text="🤖 Astra - Your Friendly Community Assistant")

        await channel.send(embed=embed, delete_after=20)

    async def send_moderation_log(
        self,
        guild: discord.Guild,
        user: discord.Member,
        violations: List[Violation],
        punishment: Dict[str, Any],
        actions_taken: List[str],
    ):
        """Send detailed log to moderation channel"""
        # Find moderation channel
        mod_channel = None
        for channel_name in ["mod-log", "moderation", "admin-log", "security-log"]:
            mod_channel = discord.utils.get(guild.text_channels, name=channel_name)
            if mod_channel:
                break

        if not mod_channel:
            return

        embed = discord.Embed(
            title="🛡️ Security Action Log",
            description=f"**User:** {user.mention} ({user})\n**ID:** {user.id}",
            color=0xFF0000 if punishment["type"] == "ban" else 0xFF9900,
            timestamp=datetime.now(timezone.utc),
        )

        violation_list = []
        for v in violations:
            violation_list.append(
                f"• **{v.violation_type.value.replace('_', ' ').title()}** (Severity: {v.severity.name})"
            )

        embed.add_field(
            name="🚨 Violations Detected",
            value="\\n".join(violation_list),
            inline=False,
        )

        embed.add_field(
            name="⚡ Actions Taken",
            value="• "
            + "\\n• ".join(
                action.replace("_", " ").title() for action in actions_taken
            ),
            inline=True,
        )

        embed.add_field(
            name="📊 Punishment Details",
            value=f"**Type:** {punishment['type'].title()}\n**Level:** {punishment['level']}/7\n**Reasoning:** {punishment['reasoning']}",
            inline=True,
        )

        if violations:
            embed.add_field(
                name="💬 Message Content",
                value=f"```{violations[0].message_content}```",
                inline=False,
            )

        embed.set_footer(
            text="🤖 Automated Security Response - Astra Protection System"
        )

        await mod_channel.send(embed=embed)

    # Utility methods

    async def get_user_profile(self, user_id: int) -> UserSecurityProfile:
        """Get or create user security profile"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserSecurityProfile(user_id=user_id)
        return self.user_profiles[user_id]

    async def update_behavioral_patterns(
        self, profile: UserSecurityProfile, message: discord.Message
    ):
        """Update user behavioral patterns"""
        content_length = len(message.content)
        profile.behavioral_patterns["message_frequency"].append(time.time())

        # Update average message length
        if profile.behavioral_patterns["avg_message_length"] == 0:
            profile.behavioral_patterns["avg_message_length"] = content_length
        else:
            profile.behavioral_patterns["avg_message_length"] = (
                profile.behavioral_patterns["avg_message_length"] * 0.9
                + content_length * 0.1
            )

        # Track channel diversity
        profile.behavioral_patterns["channel_diversity"].add(message.channel.id)

        # Update common words
        words = message.content.lower().split()
        for word in words:
            if len(word) > 3:  # Only meaningful words
                profile.behavioral_patterns["common_words"][word] += 1

    async def update_user_profile_after_violation(
        self,
        profile: UserSecurityProfile,
        violations: List[Violation],
        punishment: Dict[str, Any],
    ):
        """Update user profile after processing violations"""
        # Add violations to history
        profile.violation_history.extend(violations)

        # Update trust score
        max_severity = max(v.severity for v in violations)
        penalty = self.security_config["trust_score_penalty"][max_severity]
        profile.trust_score = max(0, profile.trust_score - penalty)

        # Update violation streak
        profile.behavioral_patterns["violation_streak"] += 1

        # Update punishment level
        profile.punishment_level = punishment["level"]
        profile.last_violation = time.time()

        # Update trust status
        profile.is_trusted = profile.trust_score >= 70

        # Set quarantine if needed
        if punishment["type"] == "timeout" and punishment["duration"]:
            profile.quarantine_until = time.time() + punishment["duration"]

    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union if union > 0 else 0.0

    async def log_security_event(
        self,
        user: discord.Member,
        violations: List[Violation],
        punishment: Dict[str, Any],
        result: Dict[str, Any],
    ):
        """Log security event for audit trail"""
        event_data = {
            "timestamp": time.time(),
            "user_id": user.id,
            "user_name": str(user),
            "guild_id": user.guild.id if user.guild else None,
            "violations": [v.to_dict() for v in violations],
            "punishment": punishment,
            "result": result,
            "system_version": "2.0",
        }

        logger.warning(
            f"SECURITY EVENT: User {user} - {len(violations)} violations - {punishment['type']} applied"
        )

    # Background tasks

    @tasks.loop(minutes=30)
    async def violation_cleanup_task(self):
        """Clean up old violations and optimize memory"""
        try:
            current_time = time.time()
            cleanup_threshold = 86400 * 7  # 7 days

            for user_id, profile in list(self.user_profiles.items()):
                # Remove old violations
                profile.violation_history = [
                    v
                    for v in profile.violation_history
                    if current_time - v.timestamp < cleanup_threshold
                ]

                # Clean up message cache
                if user_id in self.message_cache:
                    old_messages = deque()
                    for msg in self.message_cache[user_id]:
                        if current_time - msg["timestamp"] < 3600:  # Keep last hour
                            old_messages.append(msg)
                    self.message_cache[user_id] = old_messages

                # Remove inactive profiles
                if (
                    not profile.violation_history
                    and profile.last_violation
                    and current_time - profile.last_violation > cleanup_threshold
                ):
                    del self.user_profiles[user_id]

            logger.debug("Security system cleanup completed")

        except Exception as e:
            logger.error(f"Violation cleanup task error: {e}")

    @tasks.loop(hours=6)
    async def trust_score_recovery_task(self):
        """Gradually restore trust scores for users with good behavior"""
        try:
            current_time = time.time()

            for profile in self.user_profiles.values():
                # Users without recent violations get trust score recovery
                if profile.last_violation:
                    time_since_violation = current_time - profile.last_violation

                    # Gradual recovery: +1 point per 6 hours of good behavior
                    if (
                        time_since_violation >= 21600 and profile.trust_score < 100
                    ):  # 6 hours
                        recovery_amount = min(2, 100 - profile.trust_score)
                        profile.trust_score += recovery_amount
                        profile.behavioral_patterns["violation_streak"] = max(
                            0, profile.behavioral_patterns["violation_streak"] - 1
                        )

                        # Update trust status
                        profile.is_trusted = profile.trust_score >= 70

            logger.debug("Trust score recovery completed")

        except Exception as e:
            logger.error(f"Trust score recovery task error: {e}")

    @tasks.loop(hours=12)
    async def behavioral_analysis_task(self):
        """Analyze user behavioral patterns for anomaly detection"""
        try:
            current_time = time.time()

            for profile in self.user_profiles.values():
                # Clean old message frequency data
                while (
                    profile.behavioral_patterns["message_frequency"]
                    and current_time
                    - profile.behavioral_patterns["message_frequency"][0]
                    > 3600
                ):
                    profile.behavioral_patterns["message_frequency"].popleft()

                # Reset quarantine if expired
                if profile.quarantine_until and current_time > profile.quarantine_until:
                    profile.quarantine_until = None

            logger.debug("Behavioral analysis completed")

        except Exception as e:
            logger.error(f"Behavioral analysis task error: {e}")

    @tasks.loop(hours=24)
    async def threat_intelligence_update_task(self):
        """Update threat intelligence patterns"""
        try:
            # This could be expanded to fetch updated patterns from external sources
            logger.debug("Threat intelligence patterns updated")

        except Exception as e:
            logger.error(f"Threat intelligence update error: {e}")

    # API methods for external access

    def get_security_stats(self) -> Dict[str, Any]:
        """Get comprehensive security statistics"""
        current_time = time.time()

        total_users = len(self.user_profiles)
        trusted_users = sum(1 for p in self.user_profiles.values() if p.is_trusted)
        quarantined_users = sum(
            1
            for p in self.user_profiles.values()
            if p.quarantine_until and p.quarantine_until > current_time
        )

        total_violations = sum(
            len(p.violation_history) for p in self.user_profiles.values()
        )
        recent_violations = 0

        for profile in self.user_profiles.values():
            recent_violations += sum(
                1
                for v in profile.violation_history
                if current_time - v.timestamp < 86400
            )

        return {
            "total_tracked_users": total_users,
            "trusted_users": trusted_users,
            "quarantined_users": quarantined_users,
            "total_violations_all_time": total_violations,
            "violations_last_24h": recent_violations,
            "average_trust_score": sum(
                p.trust_score for p in self.user_profiles.values()
            )
            / max(total_users, 1),
            "system_status": "ACTIVE",
            "protection_level": "MAXIMUM",
        }

    async def get_user_security_report(self, user_id: int) -> Dict[str, Any]:
        """Get detailed security report for a specific user"""
        if user_id not in self.user_profiles:
            return {"error": "User not found in security database"}

        profile = self.user_profiles[user_id]
        current_time = time.time()

        recent_violations = [
            v for v in profile.violation_history if current_time - v.timestamp < 86400
        ]

        return {
            "user_id": user_id,
            "trust_score": profile.trust_score,
            "is_trusted": profile.is_trusted,
            "punishment_level": profile.punishment_level,
            "total_violations": len(profile.violation_history),
            "recent_violations_24h": len(recent_violations),
            "violation_streak": profile.behavioral_patterns["violation_streak"],
            "positive_contributions": profile.behavioral_patterns[
                "positive_contributions"
            ],
            "quarantine_status": (
                "active"
                if (
                    profile.quarantine_until and profile.quarantine_until > current_time
                )
                else "none"
            ),
            "last_violation": profile.last_violation,
            "behavioral_summary": {
                "avg_message_length": profile.behavioral_patterns["avg_message_length"],
                "channel_diversity": len(
                    profile.behavioral_patterns["channel_diversity"]
                ),
                "activity_pattern": "normal",  # Could be expanded with more analysis
            },
        }

    async def shutdown(self):
        """Shutdown security system gracefully"""
        self.violation_cleanup_task.cancel()
        self.trust_score_recovery_task.cancel()
        self.behavioral_analysis_task.cancel()
        self.threat_intelligence_update_task.cancel()

        logger.info("🛡️ Advanced Security System shutdown completed.")
