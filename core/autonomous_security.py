"""
Advanced Autonomous Server Protection System
Sophisticated AI-powered moderation capable of protecting entire servers independently
"""

import asyncio
import logging
import time
import json
import re
from typing import Dict, List, Optional, Set, Tuple, Any
from collections import defaultdict, deque
from datetime import datetime, timedelta
import hashlib
import base64
import discord
from discord.ext import commands, tasks

logger = logging.getLogger("astra.security.autonomous")


class ThreatLevel:
    """Threat level classifications"""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class SecurityEvent:
    """Security event data structure"""

    def __init__(
        self, user_id: int, event_type: str, threat_level: int, details: Dict[str, Any]
    ):
        self.user_id = user_id
        self.event_type = event_type
        self.threat_level = threat_level
        self.details = details
        self.timestamp = time.time()
        self.id = hashlib.md5(
            f"{user_id}{event_type}{self.timestamp}".encode()
        ).hexdigest()[:8]


class AutonomousServerProtection:
    """Advanced autonomous server protection system"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logger

        # Security databases
        self.threat_database = defaultdict(list)  # user_id -> [SecurityEvent]
        self.ip_tracking = defaultdict(set)  # approximate IP tracking via patterns
        self.message_fingerprints = defaultdict(deque)  # channel_id -> message hashes
        self.user_behavior_profiles = defaultdict(dict)  # user_id -> behavior profile
        self.suspicious_patterns = defaultdict(int)  # pattern -> count
        self.quarantined_users = set()  # Users under observation
        self.emergency_lockdown = False

        # Advanced detection patterns
        self.malicious_patterns = {
            # Phishing and scam patterns
            "phishing_keywords": [
                "free nitro",
                "discord nitro",
                "free discord",
                "click here for",
                "get free",
                "limited time",
                "expires soon",
                "claim now",
                "verify account",
                "suspended account",
                "unusual activity",
                "security alert",
                "immediate action",
                "click to verify",
            ],
            "suspicious_urls": [
                "bit.ly",
                "tinyurl.com",
                "short.link",
                "discord.gift",
                "discordapp.gift",
                "steam-community",
                "steamcommunity-",
                "steamcornrnunity",
                "discord-nitro",
            ],
            "social_engineering": [
                "admin here",
                "mod here",
                "developer here",
                "staff member",
                "discord employee",
                "need help with",
                "can you help",
                "quick question",
                "dont tell anyone",
                "send me your",
                "what is your",
                "verification required",
            ],
            "spam_indicators": [
                "join my server",
                "check out my",
                "subscribe to",
                "follow me on",
                "vote for my",
                "boost my server",
                "partnering with",
                "collaboration",
            ],
        }

        # Sophisticated detection algorithms
        self.detection_config = {
            "message_similarity_threshold": 0.85,
            "rapid_message_threshold": 8,  # messages per 30 seconds
            "mass_mention_threshold": 6,
            "suspicious_link_threshold": 2,
            "raid_detection_threshold": 5,  # new users in 2 minutes
            "pattern_match_threshold": 3,
            "behavior_anomaly_threshold": 0.7,
            "emergency_activation_threshold": 10,  # critical events in 5 minutes
        }

        # Behavioral analysis parameters
        self.behavioral_tracking = {
            "message_frequency": defaultdict(deque),
            "command_usage": defaultdict(list),
            "reaction_patterns": defaultdict(list),
            "voice_activity": defaultdict(list),
            "join_leave_patterns": defaultdict(list),
        }

        # Start protection systems
        self.threat_analysis_task.start()
        self.behavioral_analysis_task.start()
        self.emergency_monitoring_task.start()
        self.cleanup_task.start()

    async def analyze_message_threat(
        self, message: discord.Message
    ) -> Tuple[int, List[str]]:
        """Comprehensive message threat analysis"""
        if message.author.bot:
            return ThreatLevel.LOW, []

        threats_detected = []
        threat_level = ThreatLevel.LOW
        content = message.content.lower()

        # 1. Phishing and scam detection
        phishing_score = self._detect_phishing_patterns(content)
        if phishing_score > 3:
            threats_detected.append("phishing_attempt")
            threat_level = max(threat_level, ThreatLevel.HIGH)

        # 2. Malicious link detection
        malicious_links = self._detect_malicious_links(message.content)
        if malicious_links:
            threats_detected.append("malicious_links")
            threat_level = max(threat_level, ThreatLevel.HIGH)

        # 3. Social engineering detection
        social_eng_score = self._detect_social_engineering(content)
        if social_eng_score > 2:
            threats_detected.append("social_engineering")
            threat_level = max(threat_level, ThreatLevel.MEDIUM)

        # 4. Advanced spam detection
        spam_score = await self._advanced_spam_detection(message)
        if spam_score > 5:
            threats_detected.append("advanced_spam")
            threat_level = max(threat_level, ThreatLevel.MEDIUM)

        # 5. Mass mention abuse
        if len(message.mentions) >= self.detection_config["mass_mention_threshold"]:
            threats_detected.append("mass_mention_abuse")
            threat_level = max(threat_level, ThreatLevel.HIGH)

        # 6. Raid detection (coordinated attack)
        if self._detect_raid_pattern(message):
            threats_detected.append("raid_detected")
            threat_level = max(threat_level, ThreatLevel.CRITICAL)

        # 7. Behavioral anomaly detection
        anomaly_score = await self._detect_behavioral_anomaly(message)
        if anomaly_score > self.detection_config["behavior_anomaly_threshold"]:
            threats_detected.append("behavioral_anomaly")
            threat_level = max(threat_level, ThreatLevel.MEDIUM)

        # 8. Token/credential stealing attempt
        if self._detect_token_stealing(content):
            threats_detected.append("token_stealing_attempt")
            threat_level = max(threat_level, ThreatLevel.CRITICAL)

        # 9. Server disruption attempts
        if self._detect_server_disruption(message):
            threats_detected.append("server_disruption")
            threat_level = max(threat_level, ThreatLevel.HIGH)

        return threat_level, threats_detected

    def _detect_phishing_patterns(self, content: str) -> int:
        """Detect phishing patterns in message content"""
        score = 0

        # Check for known phishing keywords
        for keyword in self.malicious_patterns["phishing_keywords"]:
            if keyword in content:
                score += 2

        # Check for urgency indicators
        urgency_words = [
            "urgent",
            "immediate",
            "now",
            "quickly",
            "asap",
            "expire",
            "limited time",
        ]
        for word in urgency_words:
            if word in content:
                score += 1

        # Check for verification requests
        verification_patterns = [
            "verify",
            "confirm",
            "authenticate",
            "validate",
            "check",
        ]
        for pattern in verification_patterns:
            if pattern in content and ("account" in content or "security" in content):
                score += 3

        return score

    def _detect_malicious_links(self, content: str) -> List[str]:
        """Detect potentially malicious links"""
        malicious_links = []

        # Extract all URLs
        url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        urls = re.findall(url_pattern, content)

        for url in urls:
            # Check against known suspicious domains
            for suspicious_domain in self.malicious_patterns["suspicious_urls"]:
                if suspicious_domain in url.lower():
                    malicious_links.append(url)

            # Check for URL shorteners (potential obfuscation)
            shorteners = ["bit.ly", "tinyurl", "t.co", "short", "link"]
            for shortener in shorteners:
                if shortener in url.lower():
                    malicious_links.append(url)

            # Check for Discord impersonation
            if "discord" in url.lower() and "discord.com" not in url.lower():
                malicious_links.append(url)

        return malicious_links

    def _detect_social_engineering(self, content: str) -> int:
        """Detect social engineering attempts"""
        score = 0

        # Check for social engineering keywords
        for keyword in self.malicious_patterns["social_engineering"]:
            if keyword in content:
                score += 2

        # Check for authority claims
        authority_claims = [
            "admin",
            "moderator",
            "owner",
            "developer",
            "staff",
            "official",
        ]
        for claim in authority_claims:
            if claim in content:
                score += 2

        # Check for information requests
        info_requests = ["password", "token", "login", "email", "phone", "address"]
        for request in info_requests:
            if request in content:
                score += 3

        return score

    async def _advanced_spam_detection(self, message: discord.Message) -> int:
        """Advanced spam detection using multiple algorithms"""
        user_id = message.author.id
        score = 0

        # Update message frequency tracking
        self.behavioral_tracking["message_frequency"][user_id].append(time.time())

        # Clean old messages (keep last 60 seconds)
        current_time = time.time()
        while (
            self.behavioral_tracking["message_frequency"][user_id]
            and current_time - self.behavioral_tracking["message_frequency"][user_id][0]
            > 60
        ):
            self.behavioral_tracking["message_frequency"][user_id].popleft()

        # Check message frequency
        recent_messages = len(self.behavioral_tracking["message_frequency"][user_id])
        if recent_messages > self.detection_config["rapid_message_threshold"]:
            score += 5

        # Check message similarity with recent messages
        message_hash = hashlib.md5(message.content.encode()).hexdigest()
        channel_fingerprints = self.message_fingerprints[message.channel.id]

        for fingerprint in list(channel_fingerprints):
            similarity = self._calculate_message_similarity(
                message.content, fingerprint
            )
            if similarity > self.detection_config["message_similarity_threshold"]:
                score += 3

        # Add current message fingerprint
        channel_fingerprints.append(message.content)
        if len(channel_fingerprints) > 20:  # Keep last 20 messages
            channel_fingerprints.popleft()

        # Check for repeated patterns
        pattern_key = f"{user_id}:{len(message.content)}:{message.content[:20]}"
        self.suspicious_patterns[pattern_key] += 1
        if (
            self.suspicious_patterns[pattern_key]
            > self.detection_config["pattern_match_threshold"]
        ):
            score += 4

        return score

    def _detect_raid_pattern(self, message: discord.Message) -> bool:
        """Detect coordinated raid attacks"""
        guild_id = message.guild.id if message.guild else None
        if not guild_id:
            return False

        current_time = time.time()

        # Track new member messages
        if (
            message.author.joined_at
            and (current_time - message.author.joined_at.timestamp()) < 300
        ):  # 5 minutes
            pattern_key = f"new_member:{guild_id}"
            self.suspicious_patterns[pattern_key] += 1

            # Check if too many new members are active
            if (
                self.suspicious_patterns[pattern_key]
                > self.detection_config["raid_detection_threshold"]
            ):
                return True

        # Check for coordinated messaging patterns
        message_pattern = message.content[:50].lower()
        pattern_key = f"raid_pattern:{guild_id}:{message_pattern}"
        self.suspicious_patterns[pattern_key] += 1

        return self.suspicious_patterns[pattern_key] > 3

    async def _detect_behavioral_anomaly(self, message: discord.Message) -> float:
        """Detect behavioral anomalies using user profiling"""
        user_id = message.author.id

        # Initialize profile if not exists
        if user_id not in self.user_behavior_profiles:
            self.user_behavior_profiles[user_id] = {
                "avg_message_length": 0,
                "common_words": defaultdict(int),
                "activity_hours": defaultdict(int),
                "message_count": 0,
                "channels_used": set(),
                "last_seen": time.time(),
            }

        profile = self.user_behavior_profiles[user_id]
        anomaly_score = 0.0

        # Analyze message length deviation
        current_length = len(message.content)
        if profile["avg_message_length"] > 0:
            length_deviation = (
                abs(current_length - profile["avg_message_length"])
                / profile["avg_message_length"]
            )
            if length_deviation > 2.0:  # Message 200% different from average
                anomaly_score += 0.3

        # Analyze vocabulary deviation
        words = message.content.lower().split()
        common_word_score = sum(
            1 for word in words if profile["common_words"].get(word, 0) > 5
        )
        if words and common_word_score / len(words) < 0.3:  # Less than 30% common words
            anomaly_score += 0.2

        # Check activity time patterns
        current_hour = datetime.now().hour
        if (
            profile["activity_hours"][current_hour] < profile["message_count"] * 0.05
        ):  # Unusual activity time
            anomaly_score += 0.2

        # Update profile
        profile["message_count"] += 1
        profile["avg_message_length"] = (
            profile["avg_message_length"] * (profile["message_count"] - 1)
            + current_length
        ) / profile["message_count"]
        profile["activity_hours"][current_hour] += 1
        profile["channels_used"].add(message.channel.id)
        profile["last_seen"] = time.time()

        for word in words:
            profile["common_words"][word] += 1

        return anomaly_score

    def _detect_token_stealing(self, content: str) -> bool:
        """Detect token stealing attempts"""
        token_indicators = [
            "token",
            "mfa.",
            "authorization",
            "bearer",
            "oauth",
            "session",
            "cookie",
            "auth",
            "login",
            "credential",
        ]

        suspicious_requests = [
            "send me",
            "give me",
            "share your",
            "copy paste",
            "show me",
            "what is your",
            "need your",
        ]

        token_score = 0
        for indicator in token_indicators:
            if indicator in content.lower():
                token_score += 1

        request_score = 0
        for request in suspicious_requests:
            if request in content.lower():
                request_score += 1

        return token_score >= 2 and request_score >= 1

    def _detect_server_disruption(self, message: discord.Message) -> bool:
        """Detect server disruption attempts"""
        content = message.content.lower()

        # Check for disruption keywords
        disruption_keywords = [
            "crash the server",
            "lag the server",
            "ddos",
            "flood",
            "spam attack",
            "raid time",
            "everyone type",
            "mass ping",
        ]

        for keyword in disruption_keywords:
            if keyword in content:
                return True

        # Check for mass reaction attempts
        if "🚨" in message.content or "⚠️" in message.content:
            if any(word in content for word in ["everyone", "all", "mass", "spam"]):
                return True

        return False

    def _calculate_message_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two messages"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union if union > 0 else 0.0

    async def handle_security_threat(
        self, message: discord.Message, threat_level: int, threats: List[str]
    ):
        """Handle detected security threats with autonomous response"""
        user = message.author
        guild = message.guild

        # Create security event
        security_event = SecurityEvent(
            user_id=user.id,
            event_type="|".join(threats),
            threat_level=threat_level,
            details={
                "message_content": message.content[:200],
                "channel_id": message.channel.id,
                "guild_id": guild.id if guild else None,
                "threats": threats,
            },
        )

        self.threat_database[user.id].append(security_event)

        # Autonomous response based on threat level
        if threat_level >= ThreatLevel.CRITICAL:
            await self._handle_critical_threat(message, security_event)
        elif threat_level >= ThreatLevel.HIGH:
            await self._handle_high_threat(message, security_event)
        elif threat_level >= ThreatLevel.MEDIUM:
            await self._handle_medium_threat(message, security_event)

        # Log security event
        self.logger.critical(
            f"Security Event {security_event.id}: User {user} - Threats: {threats} - Level: {threat_level}"
        )

        # Check for emergency lockdown conditions
        await self._check_emergency_conditions(guild)

    async def _handle_critical_threat(
        self, message: discord.Message, event: SecurityEvent
    ):
        """Handle critical security threats"""
        user = message.author
        guild = message.guild

        try:
            # Immediate message deletion
            await message.delete()

            # Immediate timeout/ban
            if guild and user in guild.members:
                try:
                    # Try ban first for critical threats
                    await user.ban(
                        reason=f"Critical Security Threat: {event.event_type}"
                    )
                    self.logger.critical(
                        f"BANNED user {user} for critical threat: {event.event_type}"
                    )
                except:
                    # Fallback to timeout
                    await user.timeout(
                        discord.utils.utcnow() + timedelta(hours=24),
                        reason=f"Critical Security Threat: {event.event_type}",
                    )

            # Alert all moderators immediately
            await self._alert_moderators(guild, user, event, urgent=True)

            # Add to quarantine
            self.quarantined_users.add(user.id)

        except Exception as e:
            self.logger.error(f"Failed to handle critical threat: {e}")

    async def _handle_high_threat(self, message: discord.Message, event: SecurityEvent):
        """Handle high-level security threats"""
        user = message.author
        guild = message.guild

        try:
            # Delete message
            await message.delete()

            # Timeout for 12 hours
            if guild and user in guild.members:
                await user.timeout(
                    discord.utils.utcnow() + timedelta(hours=12),
                    reason=f"High Security Threat: {event.event_type}",
                )

            # Send warning to user
            await self._send_security_warning(user, event)

            # Alert moderators
            await self._alert_moderators(guild, user, event)

            # Add to watch list
            self.quarantined_users.add(user.id)

        except Exception as e:
            self.logger.error(f"Failed to handle high threat: {e}")

    async def _handle_medium_threat(
        self, message: discord.Message, event: SecurityEvent
    ):
        """Handle medium-level security threats"""
        user = message.author
        guild = message.guild

        try:
            # Delete message
            await message.delete()

            # Timeout for 1 hour
            if guild and user in guild.members:
                await user.timeout(
                    discord.utils.utcnow() + timedelta(hours=1),
                    reason=f"Security Threat: {event.event_type}",
                )

            # Send warning
            await self._send_security_warning(user, event)

        except Exception as e:
            self.logger.error(f"Failed to handle medium threat: {e}")

    async def _send_security_warning(self, user: discord.User, event: SecurityEvent):
        """Send security warning to user"""
        try:
            embed = discord.Embed(
                title="🚨 Security Violation Detected",
                description="Your recent activity has been flagged by our autonomous security system.",
                color=0xFF0000,
            )

            embed.add_field(
                name="Detected Threats",
                value=f"• {event.event_type.replace('|', chr(10) + '• ')}",
                inline=False,
            )

            embed.add_field(
                name="⚠️ Warning",
                value="Continued suspicious activity may result in permanent restrictions.",
                inline=False,
            )

            embed.set_footer(text=f"Event ID: {event.id}")

            await user.send(embed=embed)

        except:
            pass  # User may have DMs disabled

    async def _alert_moderators(
        self,
        guild: discord.Guild,
        user: discord.User,
        event: SecurityEvent,
        urgent: bool = False,
    ):
        """Alert moderators of security threats"""
        if not guild:
            return

        # Find moderation channel
        mod_channels = [
            discord.utils.get(guild.text_channels, name="mod-log"),
            discord.utils.get(guild.text_channels, name="security-log"),
            discord.utils.get(guild.text_channels, name="admin-log"),
            guild.system_channel,
        ]

        mod_channel = next((ch for ch in mod_channels if ch), None)
        if not mod_channel:
            return

        try:
            embed = discord.Embed(
                title="🚨 AUTONOMOUS SECURITY ALERT" if urgent else "⚠️ Security Event",
                description=f"**User:** {user.mention} ({user})\n**ID:** {user.id}",
                color=0xFF0000 if urgent else 0xFF9900,
            )

            embed.add_field(
                name="Threat Level",
                value=f"**Level {event.threat_level}** {'(CRITICAL)' if event.threat_level >= ThreatLevel.CRITICAL else ''}",
                inline=True,
            )

            embed.add_field(
                name="Detected Threats",
                value=f"• {event.event_type.replace('|', chr(10) + '• ')}",
                inline=False,
            )

            if event.details.get("message_content"):
                embed.add_field(
                    name="Message Content",
                    value=f"```{event.details['message_content'][:100]}...```",
                    inline=False,
                )

            embed.add_field(
                name="Autonomous Action Taken",
                value="✅ Message deleted\n✅ User sanctioned\n✅ Threat logged",
                inline=True,
            )

            embed.set_footer(text=f"Event ID: {event.id} | Powered by Astra Security")
            embed.timestamp = datetime.utcnow()

            await mod_channel.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Failed to alert moderators: {e}")

    async def _check_emergency_conditions(self, guild: discord.Guild):
        """Check if emergency lockdown should be activated"""
        if not guild or self.emergency_lockdown:
            return

        current_time = time.time()
        recent_critical_events = 0

        # Count critical events in last 5 minutes
        for user_events in self.threat_database.values():
            for event in user_events:
                if (
                    current_time - event.timestamp < 300
                    and event.threat_level >= ThreatLevel.CRITICAL
                ):
                    recent_critical_events += 1

        if (
            recent_critical_events
            >= self.detection_config["emergency_activation_threshold"]
        ):
            await self._activate_emergency_lockdown(guild)

    async def _activate_emergency_lockdown(self, guild: discord.Guild):
        """Activate emergency server lockdown"""
        self.emergency_lockdown = True

        try:
            # Find moderator role or create emergency permissions
            everyone_role = guild.default_role

            # Lock down all text channels
            for channel in guild.text_channels:
                try:
                    await channel.set_permissions(
                        everyone_role,
                        send_messages=False,
                        add_reactions=False,
                        reason="Emergency Security Lockdown - Autonomous Protection",
                    )
                except:
                    pass

            # Alert moderators
            mod_channel = (
                discord.utils.get(guild.text_channels, name="mod-log")
                or guild.system_channel
            )

            if mod_channel:
                embed = discord.Embed(
                    title="🚨 EMERGENCY LOCKDOWN ACTIVATED",
                    description="**Autonomous Security System has activated emergency lockdown due to multiple critical threats.**",
                    color=0xFF0000,
                )

                embed.add_field(
                    name="Actions Taken",
                    value="🔒 All channels locked\n🚫 Message sending disabled\n📊 Threat monitoring active",
                    inline=False,
                )

                embed.add_field(
                    name="Manual Override Required",
                    value="Use `/security unlock` to restore normal operations",
                    inline=False,
                )

                await mod_channel.send("@here", embed=embed)

            self.logger.critical(f"EMERGENCY LOCKDOWN ACTIVATED for guild {guild.name}")

        except Exception as e:
            self.logger.error(f"Failed to activate emergency lockdown: {e}")

    @tasks.loop(seconds=30)
    async def threat_analysis_task(self):
        """Continuous threat analysis and pattern detection"""
        try:
            current_time = time.time()

            # Analyze threat patterns
            for user_id, events in self.threat_database.items():
                # Remove old events (older than 24 hours)
                self.threat_database[user_id] = [
                    event for event in events if current_time - event.timestamp < 86400
                ]

                # Escalate users with multiple recent threats
                recent_events = [
                    event
                    for event in self.threat_database[user_id]
                    if current_time - event.timestamp < 3600  # Last hour
                ]

                if len(recent_events) >= 3:
                    self.quarantined_users.add(user_id)
                    self.logger.warning(
                        f"User {user_id} added to quarantine due to repeated threats"
                    )

            # Clean up old patterns
            for pattern_key in list(self.suspicious_patterns.keys()):
                if self.suspicious_patterns[pattern_key] < 2:
                    del self.suspicious_patterns[pattern_key]

        except Exception as e:
            self.logger.error(f"Threat analysis task error: {e}")

    @tasks.loop(minutes=5)
    async def behavioral_analysis_task(self):
        """Advanced behavioral pattern analysis"""
        try:
            current_time = time.time()

            # Clean old behavioral data
            for user_id in list(self.behavioral_tracking["message_frequency"].keys()):
                # Keep only last 10 minutes of data
                while (
                    self.behavioral_tracking["message_frequency"][user_id]
                    and current_time
                    - self.behavioral_tracking["message_frequency"][user_id][0]
                    > 600
                ):
                    self.behavioral_tracking["message_frequency"][user_id].popleft()

                # Remove empty entries
                if not self.behavioral_tracking["message_frequency"][user_id]:
                    del self.behavioral_tracking["message_frequency"][user_id]

        except Exception as e:
            self.logger.error(f"Behavioral analysis task error: {e}")

    @tasks.loop(minutes=1)
    async def emergency_monitoring_task(self):
        """Monitor for emergency conditions"""
        try:
            if self.emergency_lockdown:
                # Check if lockdown should be lifted (no critical events in last 10 minutes)
                current_time = time.time()
                recent_critical = False

                for user_events in self.threat_database.values():
                    for event in user_events:
                        if (
                            current_time - event.timestamp < 600
                            and event.threat_level >= ThreatLevel.CRITICAL
                        ):
                            recent_critical = True
                            break
                    if recent_critical:
                        break

                if not recent_critical:
                    # Consider auto-lifting lockdown after extended quiet period
                    pass

        except Exception as e:
            self.logger.error(f"Emergency monitoring task error: {e}")

    @tasks.loop(hours=1)
    async def cleanup_task(self):
        """Cleanup old data and optimize memory"""
        try:
            current_time = time.time()

            # Clean old message fingerprints
            for channel_id in list(self.message_fingerprints.keys()):
                # Keep only recent fingerprints
                if len(self.message_fingerprints[channel_id]) > 50:
                    self.message_fingerprints[channel_id] = deque(
                        list(self.message_fingerprints[channel_id])[-25:]
                    )

            # Clean old user behavior profiles for inactive users
            for user_id in list(self.user_behavior_profiles.keys()):
                profile = self.user_behavior_profiles[user_id]
                if current_time - profile.get("last_seen", 0) > 604800:  # 1 week
                    del self.user_behavior_profiles[user_id]

            # Remove users from quarantine after 24 hours of good behavior
            for user_id in list(self.quarantined_users):
                user_events = self.threat_database.get(user_id, [])
                recent_threats = [
                    event
                    for event in user_events
                    if current_time - event.timestamp < 86400
                ]

                if not recent_threats:
                    self.quarantined_users.discard(user_id)

            self.logger.info("Security system cleanup completed")

        except Exception as e:
            self.logger.error(f"Cleanup task error: {e}")

    def get_security_stats(self) -> Dict[str, Any]:
        """Get comprehensive security statistics"""
        current_time = time.time()

        # Count events by type and time
        total_events = sum(len(events) for events in self.threat_database.values())
        recent_events = 0
        critical_events = 0

        for user_events in self.threat_database.values():
            for event in user_events:
                if current_time - event.timestamp < 3600:  # Last hour
                    recent_events += 1
                if event.threat_level >= ThreatLevel.CRITICAL:
                    critical_events += 1

        return {
            "total_security_events": total_events,
            "recent_events_1h": recent_events,
            "critical_events_total": critical_events,
            "quarantined_users": len(self.quarantined_users),
            "tracked_users": len(self.user_behavior_profiles),
            "suspicious_patterns": len(self.suspicious_patterns),
            "emergency_lockdown_active": self.emergency_lockdown,
            "system_status": "EMERGENCY" if self.emergency_lockdown else "ACTIVE",
        }

    async def manual_threat_assessment(self, user_id: int) -> Dict[str, Any]:
        """Manual threat assessment for specific user"""
        user_events = self.threat_database.get(user_id, [])
        profile = self.user_behavior_profiles.get(user_id, {})

        current_time = time.time()
        recent_events = [
            event for event in user_events if current_time - event.timestamp < 86400
        ]

        threat_score = sum(event.threat_level for event in recent_events)

        return {
            "user_id": user_id,
            "total_events": len(user_events),
            "recent_events_24h": len(recent_events),
            "threat_score": threat_score,
            "is_quarantined": user_id in self.quarantined_users,
            "behavior_profile": {
                "message_count": profile.get("message_count", 0),
                "avg_message_length": profile.get("avg_message_length", 0),
                "channels_used": len(profile.get("channels_used", set())),
                "last_seen": profile.get("last_seen", 0),
            },
            "recent_threats": [
                {
                    "type": event.event_type,
                    "level": event.threat_level,
                    "timestamp": event.timestamp,
                }
                for event in recent_events
            ],
        }

    async def shutdown(self):
        """Shutdown security system"""
        self.threat_analysis_task.cancel()
        self.behavioral_analysis_task.cancel()
        self.emergency_monitoring_task.cancel()
        self.cleanup_task.cancel()

        self.logger.info("🔒 Autonomous Server Protection System shutdown")
