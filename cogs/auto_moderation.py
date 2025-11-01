"""
🤖 AUTO-MODERATION HANDLER
Advanced AI-powered auto-moderation that works with comprehensive_moderation.py
Designed by Z (@7zxk) for AstraBot v2.0

Features:
- Real-time message scanning
- Spam, raid, and toxicity detection
- AI-enhanced threat analysis
- Progressive punishment system
- Whitelist and bypass management
- Performance optimized with caching
"""

import asyncio
import discord
from discord.ext import commands, tasks
import logging
import re
import hashlib
import time
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta, timezone
from collections import defaultdict, deque
from dataclasses import dataclass

logger = logging.getLogger("astra.auto_moderation")

# Import from comprehensive_moderation
from cogs.comprehensive_moderation import ViolationType, SeverityLevel


@dataclass
class MessageData:
    """Message tracking data"""

    content_hash: str
    timestamp: float
    length: int
    caps_ratio: float
    mentions: int
    links: int


class AutoModeration(commands.Cog):
    """🤖 Automated Moderation Handler"""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("astra.auto_moderation")

        # Message tracking
        self.user_messages: Dict[int, Dict[int, deque]] = defaultdict(
            lambda: defaultdict(lambda: deque(maxlen=10))
        )
        self.user_violations: Dict[int, Dict[int, int]] = defaultdict(
            lambda: defaultdict(int)
        )

        # Cache for performance
        self.toxicity_cache: Dict[str, Tuple[bool, float]] = (
            {}
        )  # content_hash -> (is_toxic, timestamp)
        self.link_cache: Dict[str, Tuple[bool, float]] = {}

        # Compiled patterns for speed
        self.toxic_patterns = self._compile_toxic_patterns()
        self.link_pattern = re.compile(
            r"https?://[^\s]+|discord\.gg/[\w-]+", re.IGNORECASE
        )
        self.invite_pattern = re.compile(
            r"discord\.gg/[\w-]+|discord\.com/invite/[\w-]+", re.IGNORECASE
        )

        # Spam keywords
        self.spam_keywords = [
            "free nitro",
            "discord gift",
            "click here",
            "claim now",
            "check out my",
            "join my server",
            "dm me",
            "get rich",
            "free money",
        ]

        # Start cleanup task
        self.cleanup_caches.start()

        logger.info("🤖 Auto-Moderation Handler initialized")

    def _compile_toxic_patterns(self) -> List[re.Pattern]:
        """Compile toxic word patterns for faster matching"""
        patterns = [
            # Hate speech
            r"\b(n+[i1!]gg+[ea]+r*|f+[a4@]gg+[o0]+t+|r+[e3]+t+[a4@]+r+d+)\b",
            # Harassment
            r"\b(kill\s+yourself|kys|die|suicide|hang\s+yourself)\b",
            # Slurs
            r"\b(b+[i1!]+t+ch|wh+[o0]+r+e|sl+[u]+t+|c+[u]+n+t+)\b",
            # Aggressive insults
            r"\b(idiot|stupid|dumb|moron|loser|trash|garbage)\b",
            # Hate expressions
            r"\b(hate\s+you|fuck\s+you|fuck\s+off|stfu|gtfo|shut\s+up)\b",
        ]
        return [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in patterns]

    def cog_unload(self):
        """Cleanup on unload"""
        self.cleanup_caches.cancel()

    # ========================================================================
    # MESSAGE MONITORING
    # ========================================================================

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Monitor all messages for violations"""
        # Skip bots and DMs
        if message.author.bot or not message.guild:
            return

        # Skip if author is admin
        if message.author.guild_permissions.administrator:
            return

        try:
            # Get config from comprehensive_moderation
            comp_mod = self.bot.get_cog("ComprehensiveModeration")
            if not comp_mod:
                return

            config = await comp_mod.get_config(message.guild.id)

            # Check if auto-moderation is enabled
            if not config.auto_moderation_enabled:
                return

            # Check whitelists
            if message.author.id in config.whitelisted_user_ids:
                return

            if any(
                role.id in config.whitelisted_role_ids for role in message.author.roles
            ):
                return

            # Track message
            await self._track_message(message, config)

            # Run detection checks in parallel
            violation_checks = [
                self._check_spam(message, config),
                self._check_toxicity(message, config),
                self._check_caps_abuse(message, config),
                self._check_mention_spam(message, config),
                self._check_link_spam(message, config),
            ]

            results = await asyncio.gather(*violation_checks, return_exceptions=True)

            # Process results
            for result in results:
                if (
                    isinstance(result, tuple) and result[0]
                ):  # (is_violation, violation_type, severity, reason)
                    is_violation, violation_type, severity, reason = result
                    await self._handle_violation(
                        message, violation_type, severity, reason, comp_mod
                    )
                    break  # Only handle first violation found

        except Exception as e:
            self.logger.error(f"Error in auto-moderation: {e}", exc_info=True)

    # ========================================================================
    # DETECTION METHODS
    # ========================================================================

    async def _check_spam(
        self, message: discord.Message, config
    ) -> Tuple[bool, Optional[ViolationType], Optional[SeverityLevel], str]:
        """Check for spam"""
        if not config.spam_detection_enabled:
            return (False, None, None, "")

        guild_id = message.guild.id
        user_id = message.author.id
        current_time = time.time()

        # Get recent messages
        recent_messages = list(self.user_messages[guild_id][user_id])

        # Filter by time window
        recent_in_window = [
            msg
            for msg in recent_messages
            if current_time - msg.timestamp <= config.spam_time_window
        ]

        # Check message frequency
        if len(recent_in_window) >= config.spam_message_threshold:
            return (
                True,
                ViolationType.SPAM,
                SeverityLevel.MEDIUM,
                f"Sent {len(recent_in_window)} messages in {config.spam_time_window} seconds",
            )

        # Check for repeated content
        if len(recent_in_window) >= 3:
            hashes = [msg.content_hash for msg in recent_in_window[-3:]]
            if len(set(hashes)) == 1:
                return (
                    True,
                    ViolationType.SPAM,
                    SeverityLevel.HIGH,
                    "Repeated identical messages",
                )

        # Check for spam keywords
        content_lower = message.content.lower()
        spam_keyword_matches = [kw for kw in self.spam_keywords if kw in content_lower]
        if spam_keyword_matches:
            return (
                True,
                ViolationType.SCAM,
                SeverityLevel.HIGH,
                f"Spam keywords detected: {', '.join(spam_keyword_matches)}",
            )

        return (False, None, None, "")

    async def _check_toxicity(
        self, message: discord.Message, config
    ) -> Tuple[bool, Optional[ViolationType], Optional[SeverityLevel], str]:
        """Check for toxic language"""
        if not config.toxicity_detection_enabled:
            return (False, None, None, "")

        content = message.content
        content_hash = hashlib.md5(content.encode()).hexdigest()

        # Check cache
        if content_hash in self.toxicity_cache:
            is_toxic, cached_time = self.toxicity_cache[content_hash]
            if time.time() - cached_time < 3600:  # 1 hour cache
                if is_toxic:
                    return (
                        True,
                        ViolationType.TOXICITY,
                        SeverityLevel.HIGH,
                        "Toxic language detected",
                    )
                return (False, None, None, "")

        # Pattern matching
        matched_patterns = []
        for pattern in self.toxic_patterns:
            if pattern.search(content):
                matched_patterns.append(pattern.pattern[:30])

        if matched_patterns:
            # Cache result
            self.toxicity_cache[content_hash] = (True, time.time())

            # Determine severity based on number of matches
            if len(matched_patterns) >= 3:
                severity = SeverityLevel.CRITICAL
            elif len(matched_patterns) >= 2:
                severity = SeverityLevel.HIGH
            else:
                severity = SeverityLevel.MEDIUM

            return (
                True,
                ViolationType.TOXICITY,
                severity,
                f"Toxic language detected ({len(matched_patterns)} patterns matched)",
            )

        # Cache negative result
        self.toxicity_cache[content_hash] = (False, time.time())
        return (False, None, None, "")

    async def _check_caps_abuse(
        self, message: discord.Message, config
    ) -> Tuple[bool, Optional[ViolationType], Optional[SeverityLevel], str]:
        """Check for excessive caps"""
        if not config.caps_filtering_enabled:
            return (False, None, None, "")

        content = message.content

        # Need minimum length
        if len(content) < 10:
            return (False, None, None, "")

        # Calculate caps ratio
        caps_count = sum(1 for c in content if c.isupper())
        caps_ratio = (caps_count / len(content)) * 100

        if caps_ratio >= config.caps_percentage_threshold:
            return (
                True,
                ViolationType.CAPS_ABUSE,
                SeverityLevel.LOW,
                f"Excessive caps ({int(caps_ratio)}%)",
            )

        return (False, None, None, "")

    async def _check_mention_spam(
        self, message: discord.Message, config
    ) -> Tuple[bool, Optional[ViolationType], Optional[SeverityLevel], str]:
        """Check for mention spam"""
        if not config.mention_spam_protection:
            return (False, None, None, "")

        mention_count = len(message.mentions) + len(message.role_mentions)

        # Check for @everyone or @here abuse
        if message.mention_everyone:
            return (
                True,
                ViolationType.MENTION_SPAM,
                SeverityLevel.HIGH,
                "@everyone/@here abuse",
            )

        if mention_count >= config.mention_spam_threshold:
            return (
                True,
                ViolationType.MENTION_SPAM,
                SeverityLevel.MEDIUM,
                f"Excessive mentions ({mention_count} mentions)",
            )

        return (False, None, None, "")

    async def _check_link_spam(
        self, message: discord.Message, config
    ) -> Tuple[bool, Optional[ViolationType], Optional[SeverityLevel], str]:
        """Check for link/invite spam"""
        if not config.link_filtering_enabled:
            return (False, None, None, "")

        content = message.content

        # Find all links
        links = self.link_pattern.findall(content)
        invites = self.invite_pattern.findall(content)

        # Check for discord invites
        if invites:
            return (
                True,
                ViolationType.LINK_SPAM,
                SeverityLevel.HIGH,
                f"Unauthorized discord invites ({len(invites)} found)",
            )

        # Check for excessive links
        if len(links) > 3:
            return (
                True,
                ViolationType.LINK_SPAM,
                SeverityLevel.MEDIUM,
                f"Excessive links ({len(links)} found)",
            )

        # Check against trusted domains
        if links and config.trusted_link_domains:
            untrusted = []
            for link in links:
                is_trusted = any(
                    domain in link.lower() for domain in config.trusted_link_domains
                )
                if not is_trusted:
                    untrusted.append(link)

            if untrusted:
                return (
                    True,
                    ViolationType.LINK_SPAM,
                    SeverityLevel.MEDIUM,
                    f"Untrusted links detected ({len(untrusted)} links)",
                )

        return (False, None, None, "")

    # ========================================================================
    # VIOLATION HANDLING
    # ========================================================================

    async def _track_message(self, message: discord.Message, config):
        """Track message data"""
        guild_id = message.guild.id
        user_id = message.author.id

        # Create message data
        content_hash = hashlib.md5(message.content.encode()).hexdigest()[:8]
        caps_ratio = self._calculate_caps_ratio(message.content)

        msg_data = MessageData(
            content_hash=content_hash,
            timestamp=time.time(),
            length=len(message.content),
            caps_ratio=caps_ratio,
            mentions=len(message.mentions) + len(message.role_mentions),
            links=len(self.link_pattern.findall(message.content)),
        )

        self.user_messages[guild_id][user_id].append(msg_data)

    async def _handle_violation(
        self,
        message: discord.Message,
        violation_type: ViolationType,
        severity: SeverityLevel,
        reason: str,
        comp_mod,
    ):
        """Handle detected violation"""
        guild_id = message.guild.id
        user_id = message.author.id

        # Increment violation count
        self.user_violations[guild_id][user_id] += 1
        violation_count = self.user_violations[guild_id][user_id]

        # Delete message
        try:
            await message.delete()
            self.logger.info(
                f"🗑️ Deleted message from {message.author} ({violation_type.value}): {reason}"
            )
        except:
            pass

        # Get config
        config = await comp_mod.get_config(guild_id)

        # Determine action based on violation count and severity
        from cogs.comprehensive_moderation import ActionType

        action = None
        duration = None

        if severity == SeverityLevel.CRITICAL or violation_count >= 5:
            # Ban for critical violations or 5+ violations
            action = ActionType.BAN
        elif severity == SeverityLevel.HIGH or violation_count >= 3:
            # Timeout for high severity or 3+ violations
            action = ActionType.TIMEOUT
            duration = config.default_timeout_duration * (violation_count // 2)
        elif violation_count >= config.max_warnings_before_timeout:
            # Timeout after exceeding warnings
            action = ActionType.TIMEOUT
            duration = config.default_timeout_duration
        else:
            # Warn for first few violations
            action = ActionType.WARN

        # Apply action
        try:
            if action == ActionType.WARN:
                # Send warning DM
                try:
                    embed = discord.Embed(
                        title="⚠️ Auto-Moderation Warning",
                        description=f"Your message was removed in **{message.guild.name}**.",
                        color=0xFFAA00,
                        timestamp=datetime.now(timezone.utc),
                    )
                    embed.add_field(
                        name="Violation",
                        value=violation_type.value.replace("_", " ").title(),
                        inline=True,
                    )
                    embed.add_field(name="Reason", value=reason, inline=False)
                    embed.add_field(
                        name="Warning Count", value=str(violation_count), inline=True
                    )
                    embed.set_footer(
                        text="Please follow server rules to avoid further action."
                    )

                    await message.author.send(embed=embed)
                except:
                    pass

                # Create case
                await comp_mod.create_case(
                    guild_id=guild_id,
                    user_id=user_id,
                    moderator_id=self.bot.user.id,
                    action=action,
                    violation=violation_type,
                    reason=f"[AUTO] {reason}",
                    severity=severity,
                )

            elif action == ActionType.TIMEOUT:
                # Timeout user
                await message.author.timeout(
                    timedelta(seconds=duration),
                    reason=f"[AUTO] {violation_type.value}: {reason}",
                )

                # Send DM
                try:
                    embed = discord.Embed(
                        title="⏰ Auto-Moderation Timeout",
                        description=f"You have been timed out in **{message.guild.name}**.",
                        color=0xFF6600,
                        timestamp=datetime.now(timezone.utc),
                    )
                    embed.add_field(
                        name="Duration",
                        value=self._format_duration(duration),
                        inline=True,
                    )
                    embed.add_field(
                        name="Violation",
                        value=violation_type.value.replace("_", " ").title(),
                        inline=True,
                    )
                    embed.add_field(name="Reason", value=reason, inline=False)

                    await message.author.send(embed=embed)
                except:
                    pass

                # Create case
                await comp_mod.create_case(
                    guild_id=guild_id,
                    user_id=user_id,
                    moderator_id=self.bot.user.id,
                    action=action,
                    violation=violation_type,
                    reason=f"[AUTO] {reason}",
                    severity=severity,
                    expires_at=datetime.now(timezone.utc) + timedelta(seconds=duration),
                )

            elif action == ActionType.BAN:
                # Ban user
                await message.author.ban(
                    reason=f"[AUTO] {violation_type.value}: {reason}",
                    delete_message_days=1,
                )

                # Create case
                await comp_mod.create_case(
                    guild_id=guild_id,
                    user_id=user_id,
                    moderator_id=self.bot.user.id,
                    action=action,
                    violation=violation_type,
                    reason=f"[AUTO] {reason}",
                    severity=severity,
                )

            # Log to mod channel
            if config.mod_log_channel_id:
                channel = message.guild.get_channel(config.mod_log_channel_id)
                if channel:
                    log_embed = discord.Embed(
                        title="🤖 Auto-Moderation Action",
                        description=f"Action taken against {message.author.mention}",
                        color=0xFF0000,
                        timestamp=datetime.now(timezone.utc),
                    )
                    log_embed.add_field(
                        name="User",
                        value=f"{message.author} (`{user_id}`)",
                        inline=True,
                    )
                    log_embed.add_field(
                        name="Action", value=action.value.title(), inline=True
                    )
                    log_embed.add_field(
                        name="Violation",
                        value=violation_type.value.replace("_", " ").title(),
                        inline=True,
                    )
                    log_embed.add_field(name="Reason", value=reason, inline=False)
                    log_embed.add_field(
                        name="Violation Count", value=str(violation_count), inline=True
                    )
                    log_embed.set_footer(text=f"Channel: #{message.channel.name}")

                    await channel.send(embed=log_embed)

        except discord.Forbidden:
            self.logger.warning(
                f"Missing permissions to take action against {message.author}"
            )
        except Exception as e:
            self.logger.error(f"Error handling violation: {e}", exc_info=True)

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def _calculate_caps_ratio(self, text: str) -> float:
        """Calculate percentage of caps in text"""
        if not text:
            return 0.0
        caps_count = sum(1 for c in text if c.isupper())
        return (caps_count / len(text)) * 100

    def _format_duration(self, seconds: int) -> str:
        """Format seconds to readable duration"""
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            return f"{seconds // 60} minutes"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m" if minutes else f"{hours} hours"

    @tasks.loop(minutes=30)
    async def cleanup_caches(self):
        """Clean up old cache entries"""
        current_time = time.time()

        # Clean toxicity cache (older than 1 hour)
        to_remove = [
            key
            for key, (_, timestamp) in self.toxicity_cache.items()
            if current_time - timestamp > 3600
        ]
        for key in to_remove:
            del self.toxicity_cache[key]

        # Clean link cache (older than 1 hour)
        to_remove = [
            key
            for key, (_, timestamp) in self.link_cache.items()
            if current_time - timestamp > 3600
        ]
        for key in to_remove:
            del self.link_cache[key]

        # Clean old violation counts (reset after 24 hours)
        for guild_id in list(self.user_violations.keys()):
            for user_id in list(self.user_violations[guild_id].keys()):
                # Check last message time
                if (
                    guild_id in self.user_messages
                    and user_id in self.user_messages[guild_id]
                ):
                    messages = list(self.user_messages[guild_id][user_id])
                    if messages:
                        last_message_time = messages[-1].timestamp
                        if current_time - last_message_time > 86400:  # 24 hours
                            self.user_violations[guild_id][user_id] = 0

        logger.debug(
            f"🧹 Cleaned caches - Toxicity: {len(self.toxicity_cache)}, Links: {len(self.link_cache)}"
        )

    @cleanup_caches.before_loop
    async def before_cleanup(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(AutoModeration(bot))
    logger.info("✅ Auto-Moderation Handler loaded")
