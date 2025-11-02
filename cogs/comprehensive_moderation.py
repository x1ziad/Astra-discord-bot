"""
🛡️ COMPREHENSIVE MODERATION SYSTEM
Ultra-optimized, full-featured moderation with configurable slash commands
Designed by Z (@7zxk) for AstraBot v2.0

Features:
- Complete moderation toolkit (warn, timeout, kick, ban, mute)
- Configurable settings via slash commands
- Auto-moderation with AI enhancement
- User history tracking and progressive punishment
- Spam, raid, and toxicity detection
- Mass moderation tools
- Comprehensive logging and appeals system
- Role-based permissions
"""

import asyncio
import discord
from discord import app_commands
from discord.ext import commands, tasks
import logging
import json
import time
import re
from typing import Dict, List, Optional, Union, Literal
from datetime import datetime, timedelta, timezone
from enum import Enum
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
import sqlite3
from pathlib import Path
from functools import wraps

logger = logging.getLogger("astra.comprehensive_moderation")


# ============================================================================
# PERFORMANCE DECORATOR
# ============================================================================


def performance_monitor(func):
    """Decorator to monitor command performance"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            elapsed = time.time() - start_time
            if elapsed > 1.0:  # Log slow commands
                logger.warning(f"⚠️ Slow command: {func.__name__} took {elapsed:.2f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"❌ Error in {func.__name__} after {elapsed:.2f}s: {e}", exc_info=True
            )
            raise

    return wrapper


# ============================================================================
# ENUMS & DATA CLASSES
# ============================================================================


class ViolationType(Enum):
    """Types of violations"""

    SPAM = "spam"
    TOXICITY = "toxicity"
    HARASSMENT = "harassment"
    NSFW = "nsfw"
    RAID = "raid"
    CAPS_ABUSE = "caps_abuse"
    MENTION_SPAM = "mention_spam"
    LINK_SPAM = "link_spam"
    SCAM = "scam"
    IMPERSONATION = "impersonation"
    OTHER = "other"


class ActionType(Enum):
    """Moderation actions"""

    WARN = "warn"
    TIMEOUT = "timeout"
    KICK = "kick"
    BAN = "ban"
    SOFTBAN = "softban"
    MUTE = "mute"
    UNMUTE = "unmute"
    QUARANTINE = "quarantine"
    RELEASE_QUARANTINE = "release_quarantine"


class SeverityLevel(Enum):
    """Severity levels for violations"""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ModerationConfig:
    """Server-specific moderation configuration"""

    guild_id: int

    # System toggles
    auto_moderation_enabled: bool = True
    spam_detection_enabled: bool = True
    toxicity_detection_enabled: bool = True
    raid_protection_enabled: bool = True
    link_filtering_enabled: bool = False
    caps_filtering_enabled: bool = True
    mention_spam_protection: bool = True
    trust_system_enabled: bool = True
    smart_timeout_enabled: bool = True

    # Thresholds
    spam_message_threshold: int = 5
    spam_time_window: int = 5  # seconds
    caps_percentage_threshold: int = 70
    mention_spam_threshold: int = 5
    max_warnings_before_timeout: int = 3
    max_timeouts_before_kick: int = 2
    max_kicks_before_ban: int = 2
    trust_score_threshold: float = 50.0
    quarantine_threshold: float = 20.0

    # Durations (in seconds)
    default_timeout_duration: int = 600  # 10 minutes
    default_mute_duration: int = 3600  # 1 hour
    progressive_timeout_multiplier: float = 2.0
    default_quarantine_hours: int = 24

    # Channels
    mod_log_channel_id: Optional[int] = None
    appeals_channel_id: Optional[int] = None
    quarantine_channel_id: Optional[int] = None

    # Roles
    muted_role_id: Optional[int] = None
    moderator_role_ids: List[int] = field(default_factory=list)

    # Whitelist
    whitelisted_user_ids: List[int] = field(default_factory=list)
    whitelisted_role_ids: List[int] = field(default_factory=list)
    trusted_link_domains: List[str] = field(default_factory=list)

    # Appeals
    allow_appeals: bool = True
    appeal_cooldown_hours: int = 24


@dataclass
class ModerationCase:
    """Individual moderation case"""

    case_id: int
    guild_id: int
    user_id: int
    moderator_id: int
    action: ActionType
    violation: ViolationType
    reason: str
    timestamp: datetime
    expires_at: Optional[datetime] = None
    active: bool = True
    severity: SeverityLevel = SeverityLevel.MEDIUM
    evidence: List[str] = field(default_factory=list)
    notes: str = ""
    appealed: bool = False
    appeal_status: Optional[str] = None


# ============================================================================
# MAIN COG
# ============================================================================


class ComprehensiveModeration(commands.Cog):
    """🛡️ Complete Moderation System"""

    def __init__(self, bot):
        self.bot = bot
        self.db_path = Path("data/moderation.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # In-memory caches for performance
        self.configs: Dict[int, ModerationConfig] = {}
        self.user_message_history: Dict[int, Dict[int, deque]] = defaultdict(
            lambda: defaultdict(lambda: deque(maxlen=10))
        )
        self.active_timeouts: Dict[int, Dict[int, datetime]] = defaultdict(dict)
        self.case_counter: Dict[int, int] = defaultdict(int)

        # Initialize database
        self._init_database()

        # Start cleanup task
        self.cleanup_expired_actions.start()

        logger.info("🛡️ Comprehensive Moderation System initialized")

    def _init_database(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS moderation_configs (
                    guild_id INTEGER PRIMARY KEY,
                    config_json TEXT NOT NULL
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS moderation_cases (
                    case_id INTEGER,
                    guild_id INTEGER,
                    user_id INTEGER,
                    moderator_id INTEGER,
                    action TEXT,
                    violation TEXT,
                    reason TEXT,
                    timestamp TEXT,
                    expires_at TEXT,
                    active INTEGER,
                    severity INTEGER,
                    evidence_json TEXT,
                    notes TEXT,
                    appealed INTEGER,
                    appeal_status TEXT,
                    PRIMARY KEY (guild_id, case_id)
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_warnings (
                    guild_id INTEGER,
                    user_id INTEGER,
                    warning_count INTEGER DEFAULT 0,
                    timeout_count INTEGER DEFAULT 0,
                    kick_count INTEGER DEFAULT 0,
                    last_violation TEXT,
                    PRIMARY KEY (guild_id, user_id)
                )
            """
            )

            # Trust score table for advanced security
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_trust_scores (
                    guild_id INTEGER,
                    user_id INTEGER,
                    trust_score REAL DEFAULT 100.0,
                    last_updated TEXT,
                    PRIMARY KEY (guild_id, user_id)
                )
            """
            )

            # Create indices for performance
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_cases_guild_user 
                ON moderation_cases(guild_id, user_id)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_cases_timestamp 
                ON moderation_cases(timestamp)
            """
            )

            conn.commit()

    def cog_unload(self):
        """Cleanup on unload"""
        self.cleanup_expired_actions.cancel()

    # ========================================================================
    # CONFIGURATION COMMANDS
    # ========================================================================

    @app_commands.command(
        name="mod_config", description="⚙️ Configure moderation settings"
    )
    @app_commands.describe(
        setting="Setting to configure", value="New value for the setting"
    )
    @app_commands.choices(
        setting=[
            app_commands.Choice(
                name="🤖 Auto-Moderation", value="auto_moderation_enabled"
            ),
            app_commands.Choice(
                name="📢 Spam Detection", value="spam_detection_enabled"
            ),
            app_commands.Choice(
                name="☠️ Toxicity Detection", value="toxicity_detection_enabled"
            ),
            app_commands.Choice(
                name="🛡️ Raid Protection", value="raid_protection_enabled"
            ),
            app_commands.Choice(
                name="🔗 Link Filtering", value="link_filtering_enabled"
            ),
            app_commands.Choice(
                name="📣 Caps Filtering", value="caps_filtering_enabled"
            ),
            app_commands.Choice(
                name="📝 Mention Spam Protection", value="mention_spam_protection"
            ),
            app_commands.Choice(
                name="📨 Spam Message Threshold", value="spam_message_threshold"
            ),
            app_commands.Choice(
                name="⏱️ Spam Time Window (seconds)", value="spam_time_window"
            ),
            app_commands.Choice(
                name="🔢 Max Warnings Before Timeout",
                value="max_warnings_before_timeout",
            ),
            app_commands.Choice(
                name="⏰ Default Timeout Duration (minutes)",
                value="default_timeout_duration",
            ),
        ]
    )
    @app_commands.default_permissions(manage_guild=True)
    async def mod_config(
        self, interaction: discord.Interaction, setting: str, value: str
    ):
        """Configure moderation settings"""
        config = await self.get_config(interaction.guild_id)

        try:
            # Convert value based on setting type
            if "enabled" in setting or "protection" in setting:
                new_value = value.lower() in ("true", "yes", "1", "on", "enable")
            elif "duration" in setting and setting == "default_timeout_duration":
                new_value = int(value) * 60  # Convert minutes to seconds
            else:
                new_value = int(value) if value.isdigit() else value

            # Update config
            setattr(config, setting, new_value)
            await self.save_config(config)

            # Format display value
            if isinstance(new_value, bool):
                display_value = "✅ Enabled" if new_value else "❌ Disabled"
            elif setting == "default_timeout_duration":
                display_value = f"{new_value // 60} minutes"
            else:
                display_value = str(new_value)

            embed = discord.Embed(
                title="⚙️ Moderation Config Updated",
                description=f"**{setting.replace('_', ' ').title()}** has been updated.",
                color=0x00FF00,
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(name="New Value", value=display_value, inline=False)
            embed.set_footer(text=f"Configured by {interaction.user}")

            await interaction.response.send_message(embed=embed)

        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid value. Please provide a valid input for this setting.",
                ephemeral=True,
            )

    @app_commands.command(
        name="mod_status", description="📊 View moderation system status"
    )
    @app_commands.default_permissions(manage_messages=True)
    async def mod_status(self, interaction: discord.Interaction):
        """Display moderation system status"""
        config = await self.get_config(interaction.guild_id)

        embed = discord.Embed(
            title="🛡️ Moderation System Status",
            description=f"**{interaction.guild.name}**",
            color=0x3498DB,
            timestamp=datetime.now(timezone.utc),
        )

        # System Status
        status_text = []
        status_text.append(
            f"🤖 Auto-Moderation: {'✅' if config.auto_moderation_enabled else '❌'}"
        )
        status_text.append(
            f"📢 Spam Detection: {'✅' if config.spam_detection_enabled else '❌'}"
        )
        status_text.append(
            f"☠️ Toxicity Detection: {'✅' if config.toxicity_detection_enabled else '❌'}"
        )
        status_text.append(
            f"🛡️ Raid Protection: {'✅' if config.raid_protection_enabled else '❌'}"
        )
        status_text.append(
            f"🔗 Link Filtering: {'✅' if config.link_filtering_enabled else '❌'}"
        )
        status_text.append(
            f"📣 Caps Filtering: {'✅' if config.caps_filtering_enabled else '❌'}"
        )

        embed.add_field(
            name="📊 System Features", value="\n".join(status_text), inline=True
        )

        # Thresholds
        threshold_text = []
        threshold_text.append(
            f"📨 Spam Messages: {config.spam_message_threshold} in {config.spam_time_window}s"
        )
        threshold_text.append(
            f"⚠️ Warnings → Timeout: {config.max_warnings_before_timeout}"
        )
        threshold_text.append(f"⏰ Timeouts → Kick: {config.max_timeouts_before_kick}")
        threshold_text.append(f"👢 Kicks → Ban: {config.max_kicks_before_ban}")

        embed.add_field(
            name="📏 Thresholds", value="\n".join(threshold_text), inline=True
        )

        # Get recent stats
        stats = await self.get_moderation_stats(interaction.guild_id, days=7)
        stats_text = []
        stats_text.append(f"⚠️ Warnings: {stats.get('warns', 0)}")
        stats_text.append(f"⏰ Timeouts: {stats.get('timeouts', 0)}")
        stats_text.append(f"👢 Kicks: {stats.get('kicks', 0)}")
        stats_text.append(f"🔨 Bans: {stats.get('bans', 0)}")

        embed.add_field(
            name="📈 Last 7 Days", value="\n".join(stats_text), inline=False
        )

        embed.set_footer(text="Use /mod_config to adjust settings")

        await interaction.response.send_message(embed=embed)

    # ========================================================================
    # AUTONOMOUS AUTO-MODERATION SYSTEM
    # ========================================================================

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """🤖 Autonomous message monitoring for auto-moderation"""
        # Ignore bots and DMs
        if not message.guild or message.author.bot:
            return

        # Ignore moderators and admins
        if message.author.guild_permissions.moderate_members:
            return

        guild_id = message.guild.id
        user_id = message.author.id
        config = await self.get_config(guild_id)

        # Skip if auto-moderation is disabled
        if not config.auto_moderation_enabled:
            return

        # Track message for spam detection
        self.user_message_history[guild_id][user_id].append(
            {"content": message.content, "timestamp": datetime.now(timezone.utc)}
        )

        try:
            # === SPAM DETECTION ===
            if config.spam_detection_enabled:
                await self._check_spam(message, config)

            # === CAPS ABUSE DETECTION ===
            if config.caps_filtering_enabled:
                await self._check_caps_abuse(message, config)

            # === MENTION SPAM DETECTION ===
            if config.mention_spam_protection:
                await self._check_mention_spam(message, config)

            # === LINK SPAM DETECTION ===
            if config.link_filtering_enabled:
                await self._check_link_spam(message, config)

            # === TOXICITY DETECTION ===
            if config.toxicity_detection_enabled:
                await self._check_toxicity(message, config)

        except Exception as e:
            logger.error(f"Auto-moderation error: {e}", exc_info=True)

    async def _check_spam(self, message: discord.Message, config: ModerationConfig):
        """Check for spam messages"""
        guild_id = message.guild.id
        user_id = message.author.id

        # Get recent messages
        recent_messages = list(self.user_message_history[guild_id][user_id])

        if len(recent_messages) < config.spam_message_threshold:
            return

        # Check if messages are within time window
        now = datetime.now(timezone.utc)
        time_window = timedelta(seconds=config.spam_time_window)

        recent_in_window = [
            msg for msg in recent_messages if now - msg["timestamp"] <= time_window
        ]

        if len(recent_in_window) >= config.spam_message_threshold:
            # SPAM DETECTED
            try:
                # Delete spam messages
                messages_to_delete = []
                async for msg in message.channel.history(limit=50):
                    if msg.author.id == user_id and now - msg.created_at <= time_window:
                        messages_to_delete.append(msg)

                await message.channel.delete_messages(messages_to_delete[:10])

                # Warn user
                reason = f"Spam detected: {len(recent_in_window)} messages in {config.spam_time_window}s"

                # Record warning
                case_id = await self.create_moderation_case(
                    guild_id=guild_id,
                    user_id=user_id,
                    moderator_id=self.bot.user.id,
                    action=ActionType.WARN.value,
                    reason=reason,
                    duration_minutes=None,
                )

                await self.increment_user_warning(guild_id, user_id)

                # Check if escalation needed
                counts = await self.get_user_violation_counts(guild_id, user_id)

                if counts["warning"] >= config.max_warnings_before_timeout:
                    # Auto-timeout
                    duration = timedelta(minutes=config.default_timeout_duration)
                    await message.author.timeout(
                        duration, reason="Auto-moderation: Excessive warnings"
                    )

                    # Log in mod channel
                    if config.mod_log_channel_id:
                        channel = message.guild.get_channel(config.mod_log_channel_id)
                        if channel:
                            embed = discord.Embed(
                                title="🤖 AUTO-MODERATION: Spam Timeout",
                                description=f"**User:** {message.author.mention}\n**Reason:** {reason}\n**Duration:** {config.default_timeout_duration} minutes",
                                color=0xFF9900,
                                timestamp=datetime.now(timezone.utc),
                            )
                            await channel.send(embed=embed)

                # Clear message history
                self.user_message_history[guild_id][user_id].clear()

            except Exception as e:
                logger.error(f"Spam handling error: {e}")

    async def _check_caps_abuse(
        self, message: discord.Message, config: ModerationConfig
    ):
        """Check for excessive caps usage"""
        content = message.content

        if len(content) < 10:  # Ignore short messages
            return

        # Count caps
        caps_count = sum(1 for c in content if c.isupper())
        caps_ratio = caps_count / len(content)

        if caps_ratio > 0.7:  # More than 70% caps
            try:
                await message.delete()

                # Send warning
                warning_msg = await message.channel.send(
                    f"⚠️ {message.author.mention} Please don't use excessive caps.",
                    delete_after=5,
                )

                # Record minor violation
                await self.create_moderation_case(
                    guild_id=message.guild.id,
                    user_id=message.author.id,
                    moderator_id=self.bot.user.id,
                    action=ActionType.WARN.value,
                    reason="Auto-moderation: Excessive caps usage",
                    duration_minutes=None,
                )

            except Exception as e:
                logger.error(f"Caps filtering error: {e}")

    async def _check_mention_spam(
        self, message: discord.Message, config: ModerationConfig
    ):
        """Check for mention spam"""
        mention_count = len(message.mentions) + len(message.role_mentions)

        if mention_count >= 5:  # 5+ mentions is spam
            try:
                await message.delete()

                # Timeout user immediately
                duration = timedelta(minutes=10)
                await message.author.timeout(
                    duration, reason="Auto-moderation: Mention spam"
                )

                # Log
                if config.mod_log_channel_id:
                    channel = message.guild.get_channel(config.mod_log_channel_id)
                    if channel:
                        embed = discord.Embed(
                            title="🤖 AUTO-MODERATION: Mention Spam",
                            description=f"**User:** {message.author.mention}\n**Mentions:** {mention_count}\n**Action:** 10-minute timeout",
                            color=0xFF0000,
                            timestamp=datetime.now(timezone.utc),
                        )
                        await channel.send(embed=embed)

            except Exception as e:
                logger.error(f"Mention spam handling error: {e}")

    async def _check_link_spam(
        self, message: discord.Message, config: ModerationConfig
    ):
        """Check for suspicious links"""
        # Common phishing/scam patterns
        suspicious_patterns = [
            r"discord\.gift",
            r"nitro\.com",
            r"steam-?community",
            r"free-?nitro",
            r"d[il]sc[o0]rd\.com",
            r"bit\.ly",
            r"tinyurl\.com",
        ]

        content_lower = message.content.lower()

        for pattern in suspicious_patterns:
            if re.search(pattern, content_lower):
                try:
                    await message.delete()

                    # Warn user
                    await message.channel.send(
                        f"⚠️ {message.author.mention} Suspicious link detected and removed.",
                        delete_after=10,
                    )

                    # Record
                    await self.create_moderation_case(
                        guild_id=message.guild.id,
                        user_id=message.author.id,
                        moderator_id=self.bot.user.id,
                        action=ActionType.WARN.value,
                        reason="Auto-moderation: Suspicious link detected",
                        duration_minutes=None,
                    )

                    # Log
                    if config.mod_log_channel_id:
                        channel = message.guild.get_channel(config.mod_log_channel_id)
                        if channel:
                            embed = discord.Embed(
                                title="🤖 AUTO-MODERATION: Suspicious Link",
                                description=f"**User:** {message.author.mention}\n**Pattern:** {pattern}\n**Action:** Message deleted",
                                color=0xFF9900,
                                timestamp=datetime.now(timezone.utc),
                            )
                            await channel.send(embed=embed)

                    return  # Stop after first match

                except Exception as e:
                    logger.error(f"Link filtering error: {e}")

    async def _check_toxicity(self, message: discord.Message, config: ModerationConfig):
        """Check for toxic/offensive content"""
        # Simple keyword-based toxicity detection
        toxic_keywords = [
            "idiot",
            "stupid",
            "dumb",
            "retard",
            "moron",
            "loser",
            "kill yourself",
            "kys",
            "die",
            "hate you",
        ]

        content_lower = message.content.lower()

        for keyword in toxic_keywords:
            if keyword in content_lower:
                try:
                    await message.delete()

                    # Warn user
                    warning = await message.channel.send(
                        f"⚠️ {message.author.mention} Please keep the chat respectful.",
                        delete_after=5,
                    )

                    # Record
                    await self.create_moderation_case(
                        guild_id=message.guild.id,
                        user_id=message.author.id,
                        moderator_id=self.bot.user.id,
                        action=ActionType.WARN.value,
                        reason="Auto-moderation: Toxic language detected",
                        duration_minutes=None,
                    )

                    await self.increment_user_warning(
                        message.guild.id, message.author.id
                    )

                    return  # Stop after first match

                except Exception as e:
                    logger.error(f"Toxicity filtering error: {e}")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """🛡️ Raid protection - Monitor new member joins"""
        guild_id = member.guild.id
        config = await self.get_config(guild_id)

        if not config.raid_protection_enabled:
            return

        # Track recent joins
        if not hasattr(self, "_recent_joins"):
            self._recent_joins = defaultdict(lambda: deque(maxlen=20))

        now = datetime.now(timezone.utc)
        self._recent_joins[guild_id].append(now)

        # Check for raid (10+ joins in 60 seconds)
        recent = [
            t for t in self._recent_joins[guild_id] if now - t <= timedelta(seconds=60)
        ]

        if len(recent) >= 10:
            # RAID DETECTED
            try:
                # Enable verification level
                await member.guild.edit(
                    verification_level=discord.VerificationLevel.high
                )

                # Log raid alert
                if config.mod_log_channel_id:
                    channel = member.guild.get_channel(config.mod_log_channel_id)
                    if channel:
                        embed = discord.Embed(
                            title="🚨 RAID DETECTED",
                            description=f"**{len(recent)} members** joined in the last 60 seconds.\n\n**Action:** Verification level increased.",
                            color=0xFF0000,
                            timestamp=datetime.now(timezone.utc),
                        )
                        await channel.send(embed=embed, content="@here")

            except Exception as e:
                logger.error(f"Raid protection error: {e}")

    # ========================================================================
    # MODERATION ACTION COMMANDS
    # ========================================================================

    @app_commands.command(name="warn", description="⚠️ Warn a user")
    @app_commands.describe(
        user="User to warn",
        reason="Reason for warning",
        silent="Send warning silently (DM only)",
    )
    @app_commands.default_permissions(moderate_members=True)
    async def warn_user(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reason: str,
        silent: bool = False,
    ):
        """Warn a user"""
        if not await self.can_moderate(interaction, user):
            return

        config = await self.get_config(interaction.guild_id)

        # Create case
        case = await self.create_case(
            guild_id=interaction.guild_id,
            user_id=user.id,
            moderator_id=interaction.user.id,
            action=ActionType.WARN,
            violation=ViolationType.OTHER,
            reason=reason,
            severity=SeverityLevel.LOW,
        )

        # Update warning count
        warning_count = await self.increment_violation_count(
            interaction.guild_id, user.id, "warning"
        )

        # Check if progressive punishment needed
        if warning_count >= config.max_warnings_before_timeout:
            timeout_duration = config.default_timeout_duration
            try:
                await user.timeout(
                    timedelta(seconds=timeout_duration),
                    reason=f"Exceeded warning threshold ({warning_count} warnings)",
                )
                escalation_msg = f"\n\n⚠️ **User automatically timed out** for {timeout_duration//60} minutes due to {warning_count} warnings."
            except:
                escalation_msg = (
                    f"\n\n⚠️ User has {warning_count} warnings and should be timed out."
                )
        else:
            escalation_msg = f"\n\n⚠️ User now has **{warning_count}** warnings."

        # Send DM to user
        try:
            dm_embed = discord.Embed(
                title="⚠️ Warning",
                description=f"You have been warned in **{interaction.guild.name}**.",
                color=0xFFAA00,
                timestamp=datetime.now(timezone.utc),
            )
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(
                name="Warning Count", value=str(warning_count), inline=True
            )
            dm_embed.add_field(name="Case ID", value=f"#{case.case_id}", inline=True)
            dm_embed.set_footer(
                text="Please follow server rules to avoid further action."
            )

            await user.send(embed=dm_embed)
        except:
            escalation_msg += "\n❌ Could not DM user."

        # Response embed
        embed = discord.Embed(
            title="⚠️ User Warned",
            description=f"{user.mention} has been warned.{escalation_msg}",
            color=0xFFAA00,
            timestamp=datetime.now(timezone.utc),
        )
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Case ID", value=f"#{case.case_id}", inline=True)
        embed.set_footer(text=f"User ID: {user.id}")

        await interaction.response.send_message(embed=embed, ephemeral=silent)

        # Log to mod channel
        if not silent:
            await self.log_moderation_action(interaction.guild, embed)

    @app_commands.command(name="timeout", description="⏰ Timeout a user")
    @app_commands.describe(
        user="User to timeout",
        duration="Duration (e.g., 10m, 1h, 1d)",
        reason="Reason for timeout",
    )
    @app_commands.default_permissions(moderate_members=True)
    @performance_monitor
    async def timeout_user(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        duration: str,
        reason: str = "No reason provided",
    ):
        """Timeout a user"""
        if not await self.can_moderate(interaction, user):
            return

        # Parse duration
        duration_seconds = self.parse_duration(duration)
        if not duration_seconds or duration_seconds > 2419200:  # Max 28 days
            await interaction.response.send_message(
                "❌ Invalid duration. Use format like: 10m, 1h, 2d (max 28 days)",
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        try:
            await user.timeout(
                timedelta(seconds=duration_seconds),
                reason=f"{reason} | By: {interaction.user}",
            )

            # Create case
            case = await self.create_case(
                guild_id=interaction.guild_id,
                user_id=user.id,
                moderator_id=interaction.user.id,
                action=ActionType.TIMEOUT,
                violation=ViolationType.OTHER,
                reason=reason,
                severity=SeverityLevel.MEDIUM,
                expires_at=datetime.now(timezone.utc)
                + timedelta(seconds=duration_seconds),
            )

            # Update timeout count
            timeout_count = await self.increment_violation_count(
                interaction.guild_id, user.id, "timeout"
            )

            # Send DM
            try:
                dm_embed = discord.Embed(
                    title="⏰ Timeout",
                    description=f"You have been timed out in **{interaction.guild.name}**.",
                    color=0xFF6600,
                    timestamp=datetime.now(timezone.utc),
                )
                dm_embed.add_field(
                    name="Duration",
                    value=self.format_duration(duration_seconds),
                    inline=True,
                )
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                dm_embed.add_field(
                    name="Case ID", value=f"#{case.case_id}", inline=True
                )

                await user.send(embed=dm_embed)
            except:
                pass

            # Response
            embed = discord.Embed(
                title="⏰ User Timed Out",
                description=f"{user.mention} has been timed out.",
                color=0xFF6600,
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(
                name="Duration",
                value=self.format_duration(duration_seconds),
                inline=True,
            )
            embed.add_field(
                name="Moderator", value=interaction.user.mention, inline=True
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Case ID", value=f"#{case.case_id}", inline=True)
            embed.add_field(name="Timeout Count", value=str(timeout_count), inline=True)
            embed.set_footer(text=f"User ID: {user.id}")

            await interaction.followup.send(embed=embed)
            await self.log_moderation_action(interaction.guild, embed)

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I don't have permission to timeout this user.", ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)

    @app_commands.command(name="untimeout", description="🔓 Remove timeout from a user")
    @app_commands.describe(user="User to remove timeout from")
    @app_commands.default_permissions(moderate_members=True)
    async def untimeout_user(
        self, interaction: discord.Interaction, user: discord.Member
    ):
        """Remove timeout from a user"""
        try:
            await user.timeout(None, reason=f"Timeout removed by {interaction.user}")

            embed = discord.Embed(
                title="🔓 Timeout Removed",
                description=f"Timeout removed from {user.mention}.",
                color=0x00FF00,
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(name="Moderator", value=interaction.user.mention)
            embed.set_footer(text=f"User ID: {user.id}")

            await interaction.response.send_message(embed=embed)
            await self.log_moderation_action(interaction.guild, embed)

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error: {str(e)}", ephemeral=True
            )

    @app_commands.command(name="kick", description="👢 Kick a user from the server")
    @app_commands.describe(user="User to kick", reason="Reason for kick")
    @app_commands.default_permissions(kick_members=True)
    @performance_monitor
    async def kick_user(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reason: str = "No reason provided",
    ):
        """Kick a user"""
        if not await self.can_moderate(interaction, user):
            return

        await interaction.response.defer()

        try:
            # Send DM before kicking
            try:
                dm_embed = discord.Embed(
                    title="👢 Kicked",
                    description=f"You have been kicked from **{interaction.guild.name}**.",
                    color=0xFF3300,
                    timestamp=datetime.now(timezone.utc),
                )
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                await user.send(embed=dm_embed)
            except:
                pass

            await user.kick(reason=f"{reason} | By: {interaction.user}")

            # Create case
            case = await self.create_case(
                guild_id=interaction.guild_id,
                user_id=user.id,
                moderator_id=interaction.user.id,
                action=ActionType.KICK,
                violation=ViolationType.OTHER,
                reason=reason,
                severity=SeverityLevel.HIGH,
            )

            kick_count = await self.increment_violation_count(
                interaction.guild_id, user.id, "kick"
            )

            embed = discord.Embed(
                title="👢 User Kicked",
                description=f"**{user}** (`{user.id}`) has been kicked.",
                color=0xFF3300,
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(
                name="Moderator", value=interaction.user.mention, inline=True
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Case ID", value=f"#{case.case_id}", inline=True)
            embed.add_field(name="Kick Count", value=str(kick_count), inline=True)

            await interaction.followup.send(embed=embed)
            await self.log_moderation_action(interaction.guild, embed)

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I don't have permission to kick this user.", ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)

    @app_commands.command(name="ban", description="🔨 Ban a user from the server")
    @app_commands.describe(
        user="User to ban",
        reason="Reason for ban",
        delete_messages="Delete messages from the last X days (0-7)",
    )
    @app_commands.default_permissions(ban_members=True)
    async def ban_user(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        reason: str = "No reason provided",
        delete_messages: int = 0,
    ):
        """Ban a user"""
        # Check if user is a member
        member = interaction.guild.get_member(user.id)
        if member and not await self.can_moderate(interaction, member):
            return

        if delete_messages < 0 or delete_messages > 7:
            await interaction.response.send_message(
                "❌ Delete messages must be between 0-7 days.", ephemeral=True
            )
            return

        await interaction.response.defer()

        try:
            # Send DM before banning (if member)
            if member:
                try:
                    dm_embed = discord.Embed(
                        title="🔨 Banned",
                        description=f"You have been banned from **{interaction.guild.name}**.",
                        color=0xFF0000,
                        timestamp=datetime.now(timezone.utc),
                    )
                    dm_embed.add_field(name="Reason", value=reason, inline=False)
                    await member.send(embed=dm_embed)
                except:
                    pass

            await interaction.guild.ban(
                user,
                reason=f"{reason} | By: {interaction.user}",
                delete_message_days=delete_messages,
            )

            # Create case
            case = await self.create_case(
                guild_id=interaction.guild_id,
                user_id=user.id,
                moderator_id=interaction.user.id,
                action=ActionType.BAN,
                violation=ViolationType.OTHER,
                reason=reason,
                severity=SeverityLevel.CRITICAL,
            )

            embed = discord.Embed(
                title="🔨 User Banned",
                description=f"**{user}** (`{user.id}`) has been banned.",
                color=0xFF0000,
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(
                name="Moderator", value=interaction.user.mention, inline=True
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Case ID", value=f"#{case.case_id}", inline=True)
            if delete_messages > 0:
                embed.add_field(
                    name="Messages Deleted",
                    value=f"Last {delete_messages} days",
                    inline=True,
                )

            await interaction.followup.send(embed=embed)
            await self.log_moderation_action(interaction.guild, embed)

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I don't have permission to ban this user.", ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)

    @app_commands.command(name="unban", description="🔓 Unban a user")
    @app_commands.describe(user_id="User ID to unban", reason="Reason for unban")
    @app_commands.default_permissions(ban_members=True)
    async def unban_user(
        self,
        interaction: discord.Interaction,
        user_id: str,
        reason: str = "No reason provided",
    ):
        """Unban a user"""
        await interaction.response.defer()

        try:
            user_id_int = int(user_id)
            user = await self.bot.fetch_user(user_id_int)

            await interaction.guild.unban(
                user, reason=f"{reason} | By: {interaction.user}"
            )

            embed = discord.Embed(
                title="🔓 User Unbanned",
                description=f"**{user}** (`{user.id}`) has been unbanned.",
                color=0x00FF00,
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(
                name="Moderator", value=interaction.user.mention, inline=True
            )
            embed.add_field(name="Reason", value=reason, inline=False)

            await interaction.followup.send(embed=embed)
            await self.log_moderation_action(interaction.guild, embed)

        except ValueError:
            await interaction.followup.send("❌ Invalid user ID.", ephemeral=True)
        except discord.NotFound:
            await interaction.followup.send(
                "❌ User not found or not banned.", ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)

    @app_commands.command(
        name="softban", description="🧹 Softban (ban + unban to delete messages)"
    )
    @app_commands.describe(
        user="User to softban",
        reason="Reason for softban",
        delete_days="Days of messages to delete (1-7)",
    )
    @app_commands.default_permissions(ban_members=True)
    async def softban_user(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reason: str = "No reason provided",
        delete_days: int = 1,
    ):
        """Softban a user (ban then immediately unban to delete messages)"""
        if not await self.can_moderate(interaction, user):
            return

        if delete_days < 1 or delete_days > 7:
            await interaction.response.send_message(
                "❌ Delete days must be between 1-7.", ephemeral=True
            )
            return

        await interaction.response.defer()

        try:
            await interaction.guild.ban(
                user,
                reason=f"SOFTBAN: {reason} | By: {interaction.user}",
                delete_message_days=delete_days,
            )
            await asyncio.sleep(1)
            await interaction.guild.unban(
                user, reason=f"SOFTBAN (auto-unban) | By: {interaction.user}"
            )

            # Create case
            case = await self.create_case(
                guild_id=interaction.guild_id,
                user_id=user.id,
                moderator_id=interaction.user.id,
                action=ActionType.SOFTBAN,
                violation=ViolationType.OTHER,
                reason=reason,
                severity=SeverityLevel.MEDIUM,
            )

            embed = discord.Embed(
                title="🧹 User Softbanned",
                description=f"**{user}** (`{user.id}`) has been softbanned (messages deleted).",
                color=0xFFA500,
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(
                name="Moderator", value=interaction.user.mention, inline=True
            )
            embed.add_field(
                name="Messages Deleted", value=f"Last {delete_days} days", inline=True
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Case ID", value=f"#{case.case_id}", inline=True)

            await interaction.followup.send(embed=embed)
            await self.log_moderation_action(interaction.guild, embed)

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I don't have permission to softban this user.", ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)

    # ========================================================================
    # MASS MODERATION COMMANDS
    # ========================================================================

    @app_commands.command(name="purge", description="🧹 Delete multiple messages")
    @app_commands.describe(
        amount="Number of messages to delete (1-100)",
        user="Only delete messages from this user (optional)",
        contains="Only delete messages containing this text (optional)",
    )
    @app_commands.default_permissions(manage_messages=True)
    async def purge_messages(
        self,
        interaction: discord.Interaction,
        amount: int,
        user: Optional[discord.Member] = None,
        contains: Optional[str] = None,
    ):
        """Bulk delete messages"""
        if amount < 1 or amount > 100:
            await interaction.response.send_message(
                "❌ Amount must be between 1-100.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        def check_message(message):
            if user and message.author != user:
                return False
            if contains and contains.lower() not in message.content.lower():
                return False
            return True

        try:
            deleted = await interaction.channel.purge(limit=amount, check=check_message)

            embed = discord.Embed(
                title="🧹 Messages Purged",
                description=f"Deleted **{len(deleted)}** messages.",
                color=0x00FF00,
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(
                name="Moderator", value=interaction.user.mention, inline=True
            )
            embed.add_field(
                name="Channel", value=interaction.channel.mention, inline=True
            )
            if user:
                embed.add_field(name="User Filter", value=user.mention, inline=True)
            if contains:
                embed.add_field(name="Text Filter", value=f"`{contains}`", inline=True)

            await interaction.followup.send(embed=embed, ephemeral=True)
            await self.log_moderation_action(interaction.guild, embed)

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I don't have permission to delete messages.", ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)

    @app_commands.command(name="lockdown", description="🔒 Lockdown a channel")
    @app_commands.describe(
        channel="Channel to lockdown (current channel if not specified)",
        reason="Reason for lockdown",
    )
    @app_commands.default_permissions(manage_channels=True)
    async def lockdown_channel(
        self,
        interaction: discord.Interaction,
        channel: Optional[discord.TextChannel] = None,
        reason: str = "No reason provided",
    ):
        """Lockdown a channel"""
        channel = channel or interaction.channel

        await interaction.response.defer()

        try:
            overwrite = channel.overwrites_for(interaction.guild.default_role)
            overwrite.send_messages = False
            await channel.set_permissions(
                interaction.guild.default_role,
                overwrite=overwrite,
                reason=f"Lockdown: {reason} | By: {interaction.user}",
            )

            embed = discord.Embed(
                title="🔒 Channel Locked",
                description=f"{channel.mention} has been locked down.",
                color=0xFF0000,
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(
                name="Moderator", value=interaction.user.mention, inline=True
            )
            embed.add_field(name="Reason", value=reason, inline=False)

            await interaction.followup.send(embed=embed)
            await channel.send(embed=embed)
            await self.log_moderation_action(interaction.guild, embed)

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I don't have permission to manage this channel.", ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)

    @app_commands.command(name="unlock", description="🔓 Unlock a channel")
    @app_commands.describe(
        channel="Channel to unlock (current channel if not specified)"
    )
    @app_commands.default_permissions(manage_channels=True)
    async def unlock_channel(
        self,
        interaction: discord.Interaction,
        channel: Optional[discord.TextChannel] = None,
    ):
        """Unlock a channel"""
        channel = channel or interaction.channel

        await interaction.response.defer()

        try:
            overwrite = channel.overwrites_for(interaction.guild.default_role)
            overwrite.send_messages = None
            await channel.set_permissions(
                interaction.guild.default_role,
                overwrite=overwrite,
                reason=f"Unlock by: {interaction.user}",
            )

            embed = discord.Embed(
                title="🔓 Channel Unlocked",
                description=f"{channel.mention} has been unlocked.",
                color=0x00FF00,
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(name="Moderator", value=interaction.user.mention)

            await interaction.followup.send(embed=embed)
            await channel.send(embed=embed)
            await self.log_moderation_action(interaction.guild, embed)

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I don't have permission to manage this channel.", ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)

    # ========================================================================
    # CASE MANAGEMENT COMMANDS
    # ========================================================================

    @app_commands.command(name="case", description="📋 View a moderation case")
    @app_commands.describe(case_id="Case ID to view")
    @app_commands.default_permissions(manage_messages=True)
    async def view_case(self, interaction: discord.Interaction, case_id: int):
        """View a specific moderation case"""
        case = await self.get_case(interaction.guild_id, case_id)

        if not case:
            await interaction.response.send_message(
                "❌ Case not found.", ephemeral=True
            )
            return

        user = await self.bot.fetch_user(case.user_id)
        moderator = await self.bot.fetch_user(case.moderator_id)

        embed = discord.Embed(
            title=f"📋 Case #{case.case_id}",
            color=self.get_action_color(case.action),
            timestamp=case.timestamp,
        )

        embed.add_field(name="User", value=f"{user.mention} (`{user.id}`)", inline=True)
        embed.add_field(name="Moderator", value=f"{moderator.mention}", inline=True)
        embed.add_field(name="Action", value=case.action.value.title(), inline=True)
        embed.add_field(
            name="Violation", value=case.violation.value.title(), inline=True
        )
        embed.add_field(name="Severity", value=case.severity.name, inline=True)
        embed.add_field(
            name="Status",
            value="✅ Active" if case.active else "❌ Inactive",
            inline=True,
        )
        embed.add_field(name="Reason", value=case.reason, inline=False)

        if case.expires_at:
            embed.add_field(
                name="Expires",
                value=f"<t:{int(case.expires_at.timestamp())}:R>",
                inline=True,
            )

        if case.notes:
            embed.add_field(name="Notes", value=case.notes, inline=False)

        if case.appealed:
            embed.add_field(
                name="Appeal Status", value=case.appeal_status or "Pending", inline=True
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="history", description="📜 View moderation history for a user"
    )
    @app_commands.describe(
        user="User to view history for", limit="Number of cases to show (default: 10)"
    )
    @app_commands.default_permissions(manage_messages=True)
    async def user_history(
        self, interaction: discord.Interaction, user: discord.User, limit: int = 10
    ):
        """View user's moderation history"""
        cases = await self.get_user_cases(interaction.guild_id, user.id, limit=limit)

        if not cases:
            await interaction.response.send_message(
                f"✅ {user.mention} has no moderation history.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"📜 Moderation History - {user}",
            description=f"Showing last {len(cases)} cases",
            color=0x3498DB,
            timestamp=datetime.now(timezone.utc),
        )

        for case in cases[:10]:  # Show max 10
            moderator = await self.bot.fetch_user(case.moderator_id)
            value = f"**{case.action.value.title()}** by {moderator.mention}\n"
            value += f"Reason: {case.reason[:100]}\n"
            value += f"Date: <t:{int(case.timestamp.timestamp())}:R>"

            embed.add_field(
                name=f"Case #{case.case_id} - {case.violation.value.title()}",
                value=value,
                inline=False,
            )

        # Get summary stats
        stats = await self.get_user_violation_counts(interaction.guild_id, user.id)
        summary = f"⚠️ Warnings: {stats['warning']} | ⏰ Timeouts: {stats['timeout']} | 👢 Kicks: {stats['kick']}"
        embed.set_footer(text=summary)

        await interaction.response.send_message(embed=embed)

    # ========================================================================
    # ADVANCED SECURITY FEATURES
    # ========================================================================

    @app_commands.command(
        name="quarantine",
        description="🔒 Quarantine a user (remove roles and restrict access)",
    )
    @app_commands.describe(
        user="User to quarantine",
        reason="Reason for quarantine",
        duration_hours="Duration in hours (default: 24)",
    )
    @app_commands.default_permissions(administrator=True)
    @performance_monitor
    async def quarantine_user(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reason: str,
        duration_hours: int = 24,
    ):
        """🔒 Advanced quarantine system with role removal and channel restrictions"""

        if not await self.can_moderate(interaction, user):
            return

        await interaction.response.defer()

        try:
            # Store original roles (exclude @everyone)
            original_roles = [
                role for role in user.roles if role != interaction.guild.default_role
            ]

            # Remove all roles
            roles_removed = 0
            roles_failed = []
            bot_member = interaction.guild.get_member(self.bot.user.id)
            bot_top_role = bot_member.top_role if bot_member else None

            for role in original_roles:
                try:
                    if bot_top_role and role >= bot_top_role:
                        roles_failed.append(role.name)
                        continue
                    await user.remove_roles(role, reason=f"🔒 QUARANTINE: {reason}")
                    roles_removed += 1
                    await asyncio.sleep(0.05)  # Rate limit protection
                except Exception as e:
                    logger.warning(f"Failed to remove role {role.name}: {e}")
                    roles_failed.append(role.name)

            # Apply channel restrictions
            for channel in interaction.guild.channels:
                if isinstance(channel, (discord.TextChannel, discord.VoiceChannel)):
                    try:
                        overwrite = discord.PermissionOverwrite(
                            send_messages=False,
                            speak=False,
                            connect=False,
                            add_reactions=False,
                            attach_files=False,
                            embed_links=False,
                            use_external_emojis=False,
                            use_application_commands=False,
                        )
                        await channel.set_permissions(
                            user, overwrite=overwrite, reason=f"🔒 QUARANTINE: {reason}"
                        )
                    except:
                        pass

            # Apply Discord timeout (max 28 days)
            timeout_applied = False
            try:
                timeout_seconds = min(duration_hours * 3600, 2419200)
                await user.timeout(
                    timedelta(seconds=timeout_seconds),
                    reason=f"🔒 QUARANTINE: {reason}",
                )
                timeout_applied = True
            except Exception as e:
                logger.warning(f"Timeout failed during quarantine: {e}")

            # Store quarantine data in database
            expires_at = datetime.now(timezone.utc) + timedelta(hours=duration_hours)
            case = await self.create_case(
                guild_id=interaction.guild_id,
                user_id=user.id,
                moderator_id=interaction.user.id,
                action=ActionType.QUARANTINE,
                violation=ViolationType.OTHER,
                reason=reason,
                severity=SeverityLevel.HIGH,
                expires_at=expires_at,
                evidence=[],
                notes=json.dumps(
                    {
                        "original_roles": [r.id for r in original_roles],
                        "roles_removed": roles_removed,
                        "roles_failed": roles_failed,
                        "timeout_applied": timeout_applied,
                    }
                ),
            )

            # Create response embed
            embed = discord.Embed(
                title="🔒 USER QUARANTINED",
                description=f"{user.mention} has been quarantined.",
                color=0xFF6600,
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(
                name="👤 User", value=f"{user.mention} (`{user.id}`)", inline=True
            )
            embed.add_field(
                name="⏰ Duration", value=f"{duration_hours} hours", inline=True
            )
            embed.add_field(
                name="🔧 Roles Removed",
                value=f"{roles_removed}/{len(original_roles)}",
                inline=True,
            )
            embed.add_field(name="📝 Reason", value=reason, inline=False)

            actions = [
                f"• {roles_removed} roles removed",
                "• Channel permissions restricted",
                f"• {'✅' if timeout_applied else '❌'} Timeout applied",
            ]
            if roles_failed:
                actions.append(f"• ⚠️ {len(roles_failed)} roles failed (hierarchy)")

            embed.add_field(
                name="⚡ Actions Taken", value="\n".join(actions), inline=False
            )
            embed.set_footer(
                text=f"Case #{case.case_id} | Auto-release in {duration_hours}h"
            )

            await interaction.followup.send(embed=embed)
            await self.log_moderation_action(interaction.guild, embed)

        except Exception as e:
            logger.error(f"Quarantine error: {e}", exc_info=True)
            await interaction.followup.send(
                f"❌ Error during quarantine: {str(e)}", ephemeral=True
            )

    @app_commands.command(
        name="release_quarantine",
        description="🔓 Release a user from quarantine and restore roles",
    )
    @app_commands.describe(user="User to release from quarantine")
    @app_commands.default_permissions(administrator=True)
    @performance_monitor
    async def release_quarantine(
        self, interaction: discord.Interaction, user: discord.Member
    ):
        """🔓 Release user from quarantine and restore original roles"""

        await interaction.response.defer()

        try:
            # Find quarantine case
            cases = await self.get_user_cases(interaction.guild_id, user.id, limit=50)
            quarantine_case = None

            for case in cases:
                if case.action == ActionType.QUARANTINE and case.active:
                    quarantine_case = case
                    break

            if not quarantine_case:
                await interaction.followup.send(
                    f"❌ {user.mention} is not currently quarantined.", ephemeral=True
                )
                return

            # Parse stored quarantine data
            try:
                quarantine_data = json.loads(quarantine_case.notes)
                original_role_ids = quarantine_data.get("original_roles", [])
            except:
                original_role_ids = []

            # Restore roles
            roles_restored = 0
            roles_failed = []

            for role_id in original_role_ids:
                role = interaction.guild.get_role(role_id)
                if role:
                    try:
                        await user.add_roles(role, reason="🔓 Released from quarantine")
                        roles_restored += 1
                        await asyncio.sleep(0.05)
                    except Exception as e:
                        logger.warning(f"Failed to restore role {role.name}: {e}")
                        roles_failed.append(role.name)

            # Remove channel restrictions
            for channel in interaction.guild.channels:
                if isinstance(channel, (discord.TextChannel, discord.VoiceChannel)):
                    try:
                        await channel.set_permissions(
                            user, overwrite=None, reason="🔓 Released from quarantine"
                        )
                    except:
                        pass

            # Remove timeout
            try:
                await user.timeout(None, reason="🔓 Released from quarantine")
            except:
                pass

            # Update case as inactive
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE moderation_cases SET active = 0 WHERE case_id = ? AND guild_id = ?",
                    (quarantine_case.case_id, interaction.guild_id),
                )
                conn.commit()

            # Calculate quarantine duration
            duration = datetime.now(timezone.utc) - quarantine_case.timestamp
            duration_str = str(duration).split(".")[0]

            # Create response embed
            embed = discord.Embed(
                title="🔓 QUARANTINE RELEASED",
                description=f"{user.mention} has been released from quarantine.",
                color=0x00FF00,
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(
                name="👤 User", value=f"{user.mention} (`{user.id}`)", inline=True
            )
            embed.add_field(name="⏱️ Duration", value=duration_str, inline=True)
            embed.add_field(
                name="🔧 Roles Restored",
                value=f"{roles_restored}/{len(original_role_ids)}",
                inline=True,
            )

            actions = [
                f"• {roles_restored} roles restored",
                "• Channel restrictions removed",
                "• Timeout removed",
            ]
            if roles_failed:
                actions.append(f"• ⚠️ {len(roles_failed)} roles failed")

            embed.add_field(
                name="⚡ Actions Taken", value="\n".join(actions), inline=False
            )
            embed.set_footer(text=f"Original Case #{quarantine_case.case_id}")

            await interaction.followup.send(embed=embed)
            await self.log_moderation_action(interaction.guild, embed)

        except Exception as e:
            logger.error(f"Release quarantine error: {e}", exc_info=True)
            await interaction.followup.send(
                f"❌ Error releasing from quarantine: {str(e)}", ephemeral=True
            )

    @app_commands.command(
        name="threat_scan",
        description="🔍 Scan for active threats in the server",
    )
    @app_commands.describe(
        target="Specific user to investigate (optional)",
        channel="Specific channel to scan (optional)",
        hours="Hours of history to scan (default: 1)",
    )
    @app_commands.default_permissions(manage_messages=True)
    @performance_monitor
    async def threat_scan(
        self,
        interaction: discord.Interaction,
        target: Optional[discord.Member] = None,
        channel: Optional[discord.TextChannel] = None,
        hours: int = 1,
    ):
        """🔍 Perform active threat scanning"""

        await interaction.response.defer()

        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

            # Query recent moderation cases
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT user_id, violation, severity, COUNT(*) as count
                    FROM moderation_cases
                    WHERE guild_id = ? AND timestamp >= ?
                """
                params = [interaction.guild_id, cutoff_time.isoformat()]

                if target:
                    query += " AND user_id = ?"
                    params.append(target.id)

                query += " GROUP BY user_id, violation ORDER BY count DESC LIMIT 10"

                cursor = conn.execute(query, params)
                threats = cursor.fetchall()

            # Create embed
            embed = discord.Embed(
                title="🔍 THREAT SCAN RESULTS",
                description=f"Scanning last {hours} hour(s) of activity",
                color=0xFFAA00 if threats else 0x00FF00,
                timestamp=datetime.now(timezone.utc),
            )

            scan_scope = []
            if target:
                scan_scope.append(f"👤 User: {target.mention}")
            if channel:
                scan_scope.append(f"📺 Channel: {channel.mention}")
            scan_scope.append(f"⏰ Timeframe: {hours} hour(s)")

            embed.add_field(
                name="🎯 Scan Scope", value="\n".join(scan_scope), inline=False
            )

            if threats:
                threat_list = []
                for user_id, violation, severity, count in threats[:5]:
                    try:
                        user = await self.bot.fetch_user(user_id)
                        threat_list.append(
                            f"⚠️ **{user.name}**: {count}x {violation} (Severity: {severity})"
                        )
                    except:
                        threat_list.append(
                            f"⚠️ **User {user_id}**: {count}x {violation} (Severity: {severity})"
                        )

                embed.add_field(
                    name=f"🚨 Threats Detected ({len(threats)})",
                    value="\n".join(threat_list) if threat_list else "Processing...",
                    inline=False,
                )
                embed.color = 0xFF0000
            else:
                embed.add_field(
                    name="✅ All Clear",
                    value="No active threats detected in scan scope.",
                    inline=False,
                )

            # Get total stats
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM moderation_cases WHERE guild_id = ? AND timestamp >= ?",
                    (interaction.guild_id, cutoff_time.isoformat()),
                )
                total_actions = cursor.fetchone()[0]

            embed.add_field(
                name="📊 Scan Statistics",
                value=f"Total actions: {total_actions}\nThreats found: {len(threats)}\nScan time: <1s",
                inline=False,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Threat scan error: {e}", exc_info=True)
            await interaction.followup.send(
                f"❌ Error during threat scan: {str(e)}", ephemeral=True
            )

    @app_commands.command(
        name="investigate_user",
        description="🕵️ Deep investigation of a specific user",
    )
    @app_commands.describe(
        user="User to investigate",
        days="Days of history to analyze (default: 7)",
    )
    @app_commands.default_permissions(manage_messages=True)
    @performance_monitor
    async def investigate_user(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        days: int = 7,
    ):
        """🕵️ Perform detailed user investigation"""

        await interaction.response.defer()

        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=days)

            # Get user's moderation history
            cases = await self.get_user_cases(interaction.guild_id, user.id, limit=100)
            recent_cases = [c for c in cases if c.timestamp >= cutoff_time]

            # Calculate account age
            account_age = datetime.now(timezone.utc) - user.created_at
            server_age = (
                datetime.now(timezone.utc) - user.joined_at
                if user.joined_at
                else timedelta(0)
            )

            # Get violation counts
            violation_counts = defaultdict(int)
            for case in recent_cases:
                violation_counts[case.violation.value] += 1

            # Create embed
            embed = discord.Embed(
                title=f"🕵️ USER INVESTIGATION: {user.display_name}",
                description=f"Deep analysis of user activity over {days} days",
                color=0x0099FF,
                timestamp=datetime.now(timezone.utc),
            )
            embed.set_thumbnail(url=user.display_avatar.url)

            # Basic info
            embed.add_field(
                name="👤 Username",
                value=f"{user.name} (`{user.id}`)",
                inline=True,
            )
            embed.add_field(
                name="📅 Account Age",
                value=f"{account_age.days} days",
                inline=True,
            )
            embed.add_field(
                name="📅 Server Join",
                value=f"{server_age.days} days ago" if user.joined_at else "Unknown",
                inline=True,
            )

            # Moderation history
            embed.add_field(
                name=f"📜 Recent Cases ({days}d)",
                value=f"{len(recent_cases)} total actions",
                inline=True,
            )
            embed.add_field(
                name="📈 Total History",
                value=f"{len(cases)} all-time cases",
                inline=True,
            )

            # Calculate risk score
            risk_score = min(len(recent_cases) * 10, 100)
            risk_emoji = "🟢" if risk_score < 30 else "🟡" if risk_score < 70 else "🔴"

            embed.add_field(
                name="⚠️ Risk Score",
                value=f"{risk_emoji} {risk_score}/100",
                inline=True,
            )

            # Violation breakdown
            if violation_counts:
                violations_str = "\n".join(
                    [
                        f"• {v.title()}: {c}x"
                        for v, c in list(violation_counts.items())[:5]
                    ]
                )
                embed.add_field(
                    name="🚨 Violation Breakdown",
                    value=violations_str,
                    inline=False,
                )

            # Roles
            if len(user.roles) > 1:
                roles_str = ", ".join([r.mention for r in user.roles[1:6]])
                if len(user.roles) > 6:
                    roles_str += f" +{len(user.roles) - 6} more"
                embed.add_field(name="🎭 Roles", value=roles_str, inline=False)

            # Recommendations
            recommendations = []
            if risk_score >= 70:
                recommendations.append(
                    "⚠️ **High risk user** - Consider increased monitoring"
                )
            if len(recent_cases) >= 3:
                recommendations.append("📝 May benefit from warning or timeout")
            if account_age.days < 7:
                recommendations.append(
                    "🆕 New account - Monitor for suspicious activity"
                )

            if recommendations:
                embed.add_field(
                    name="💡 Recommendations",
                    value="\n".join(recommendations),
                    inline=False,
                )

            embed.set_footer(text=f"Investigation Period: {days} days")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"User investigation error: {e}", exc_info=True)
            await interaction.followup.send(
                f"❌ Error during investigation: {str(e)}", ephemeral=True
            )

    @app_commands.command(
        name="smart_timeout",
        description="⚡ AI-powered smart timeout with calculated duration",
    )
    @app_commands.describe(
        user="User to timeout",
        reason="Reason for timeout",
        override_minutes="Override calculated duration (optional)",
    )
    @app_commands.default_permissions(moderate_members=True)
    @performance_monitor
    async def smart_timeout(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reason: str,
        override_minutes: Optional[int] = None,
    ):
        """⚡ Smart timeout with AI-calculated duration based on history"""

        if not await self.can_moderate(interaction, user):
            return

        await interaction.response.defer()

        try:
            config = await self.get_config(interaction.guild_id)

            # Get user's violation history
            cases = await self.get_user_cases(interaction.guild_id, user.id, limit=50)
            recent_timeouts = len([c for c in cases if c.action == ActionType.TIMEOUT])
            recent_violations = len(
                [
                    c
                    for c in cases
                    if c.timestamp >= datetime.now(timezone.utc) - timedelta(days=30)
                ]
            )

            # Calculate smart duration
            if override_minutes:
                duration_minutes = override_minutes
            else:
                # Base duration: 10 minutes
                base_duration = 10

                # Add 5 minutes per recent timeout
                timeout_penalty = recent_timeouts * 5

                # Add 3 minutes per recent violation
                violation_penalty = recent_violations * 3

                # Calculate final duration (max 24 hours = 1440 minutes)
                duration_minutes = min(
                    base_duration + timeout_penalty + violation_penalty, 1440
                )

            # Apply timeout
            timeout_duration = timedelta(minutes=duration_minutes)
            await user.timeout(timeout_duration, reason=reason)

            # Create case with expires_at
            expires_at = datetime.now(timezone.utc) + timeout_duration
            case = await self.create_case(
                guild_id=interaction.guild_id,
                user_id=user.id,
                moderator_id=interaction.user.id,
                action=ActionType.TIMEOUT,
                violation=ViolationType.OTHER,
                reason=reason,
                severity=SeverityLevel.MEDIUM,
                expires_at=expires_at,
                evidence=[],
                notes=json.dumps(
                    {
                        "smart_timeout": True,
                        "calculated_duration": duration_minutes,
                        "override": override_minutes is not None,
                        "recent_timeouts": recent_timeouts,
                        "recent_violations": recent_violations,
                    }
                ),
            )

            # Create response embed
            embed = discord.Embed(
                title="⚡ SMART TIMEOUT APPLIED",
                description=f"{user.mention} has been timed out using AI-calculated duration.",
                color=0xFF9900,
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(
                name="👤 User", value=f"{user.mention} (`{user.id}`)", inline=True
            )
            embed.add_field(
                name="⏰ Duration",
                value=f"{duration_minutes} minutes",
                inline=True,
            )
            embed.add_field(
                name="🧠 Calculation",
                value=f"Base: 10m\n+{recent_timeouts * 5}m (timeouts)\n+{recent_violations * 3}m (violations)",
                inline=True,
            )
            embed.add_field(name="📝 Reason", value=reason, inline=False)
            embed.set_footer(
                text=f"Case #{case.case_id} | Expires <t:{int((datetime.now(timezone.utc) + timeout_duration).timestamp())}:R>"
            )

            await interaction.followup.send(embed=embed)
            await self.log_moderation_action(interaction.guild, embed)

        except Exception as e:
            logger.error(f"Smart timeout error: {e}", exc_info=True)
            await interaction.followup.send(
                f"❌ Error applying smart timeout: {str(e)}", ephemeral=True
            )

    @app_commands.command(
        name="security_logs",
        description="📋 View recent security events and moderation logs",
    )
    @app_commands.describe(
        hours="Hours of logs to view (default: 24)",
        action_type="Filter by specific action type (optional)",
    )
    @app_commands.default_permissions(manage_messages=True)
    @performance_monitor
    async def security_logs(
        self,
        interaction: discord.Interaction,
        hours: int = 24,
        action_type: Optional[str] = None,
    ):
        """📋 View recent security events"""

        await interaction.response.defer()

        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

            # Query logs
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT case_id, user_id, moderator_id, action, violation, reason, timestamp
                    FROM moderation_cases
                    WHERE guild_id = ? AND timestamp >= ?
                """
                params = [interaction.guild_id, cutoff_time.isoformat()]

                if action_type:
                    query += " AND action = ?"
                    params.append(action_type)

                query += " ORDER BY timestamp DESC LIMIT 20"

                cursor = conn.execute(query, params)
                logs = cursor.fetchall()

            # Create embed
            embed = discord.Embed(
                title="📋 SECURITY LOGS",
                description=f"Recent moderation actions (last {hours} hours)",
                color=0x3498DB,
                timestamp=datetime.now(timezone.utc),
            )

            if logs:
                log_entries = []
                for (
                    case_id,
                    user_id,
                    mod_id,
                    action,
                    violation,
                    reason,
                    timestamp,
                ) in logs[:10]:
                    try:
                        user = await self.bot.fetch_user(user_id)
                        moderator = await self.bot.fetch_user(mod_id)
                        ts = datetime.fromisoformat(timestamp)

                        log_entries.append(
                            f"**#{case_id}** <t:{int(ts.timestamp())}:R>\n"
                            f"👤 {user.name} | 🛡️ {moderator.name}\n"
                            f"⚡ {action.upper()} - {violation}\n"
                            f"📝 {reason[:50]}{'...' if len(reason) > 50 else ''}\n"
                        )
                    except:
                        log_entries.append(
                            f"**#{case_id}** - {action.upper()} - {violation}\n"
                        )

                # Split into multiple fields if needed
                chunk_size = 1024
                current_chunk = ""
                field_num = 1

                for entry in log_entries:
                    if len(current_chunk) + len(entry) > chunk_size:
                        embed.add_field(
                            name=f"📜 Recent Actions ({field_num})",
                            value=current_chunk,
                            inline=False,
                        )
                        current_chunk = entry
                        field_num += 1
                    else:
                        current_chunk += entry + "\n"

                if current_chunk:
                    embed.add_field(
                        name=(
                            f"📜 Recent Actions ({field_num})"
                            if field_num > 1
                            else "📜 Recent Actions"
                        ),
                        value=current_chunk,
                        inline=False,
                    )
            else:
                embed.add_field(
                    name="ℹ️ No Logs Found",
                    value=f"No moderation actions in the last {hours} hours.",
                    inline=False,
                )

            # Add statistics
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT action, COUNT(*) as count
                    FROM moderation_cases
                    WHERE guild_id = ? AND timestamp >= ?
                    GROUP BY action
                    """,
                    (interaction.guild_id, cutoff_time.isoformat()),
                )
                stats = cursor.fetchall()

            if stats:
                stats_str = " | ".join(
                    [f"{action}: {count}" for action, count in stats]
                )
                embed.set_footer(text=f"Summary: {stats_str}")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Security logs error: {e}", exc_info=True)
            await interaction.followup.send(
                f"❌ Error retrieving security logs: {str(e)}", ephemeral=True
            )

    @app_commands.command(
        name="trust_score",
        description="📊 View or modify user trust score",
    )
    @app_commands.describe(
        user="User to check/modify",
        new_score="New trust score (0-100, optional)",
        reason="Reason for modification",
    )
    @app_commands.default_permissions(administrator=True)
    @performance_monitor
    async def trust_score(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        new_score: Optional[float] = None,
        reason: Optional[str] = None,
    ):
        """📊 View or modify user trust score"""

        await interaction.response.defer()

        try:
            config = await self.get_config(interaction.guild_id)

            if not config.trust_system_enabled:
                await interaction.followup.send(
                    "⚠️ Trust system is not enabled. Use `/mod_config` to enable it.",
                    ephemeral=True,
                )
                return

            # Get current trust score
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT trust_score, last_updated FROM user_trust_scores WHERE guild_id = ? AND user_id = ?",
                    (interaction.guild_id, user.id),
                )
                row = cursor.fetchone()

                if row:
                    current_score, last_updated = row
                else:
                    current_score = 100.0
                    last_updated = None

            # Modify if new score provided
            if new_score is not None:
                if not 0 <= new_score <= 100:
                    await interaction.followup.send(
                        "❌ Trust score must be between 0 and 100.", ephemeral=True
                    )
                    return

                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO user_trust_scores 
                        (guild_id, user_id, trust_score, last_updated)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            interaction.guild_id,
                            user.id,
                            new_score,
                            datetime.now(timezone.utc).isoformat(),
                        ),
                    )
                    conn.commit()

                # Create modification embed
                embed = discord.Embed(
                    title="📊 TRUST SCORE MODIFIED",
                    description=f"Trust score updated for {user.mention}",
                    color=(
                        0x00FF00
                        if new_score >= 70
                        else 0xFF9900 if new_score >= 40 else 0xFF0000
                    ),
                    timestamp=datetime.now(timezone.utc),
                )
                embed.add_field(
                    name="👤 User",
                    value=f"{user.mention} (`{user.id}`)",
                    inline=True,
                )
                embed.add_field(
                    name="📊 Previous Score",
                    value=f"{current_score:.1f}/100",
                    inline=True,
                )
                embed.add_field(
                    name="📈 New Score",
                    value=f"{new_score:.1f}/100",
                    inline=True,
                )

                if reason:
                    embed.add_field(name="📝 Reason", value=reason, inline=False)

                # Add trust level
                if new_score >= 80:
                    trust_level = "🟢 Trusted"
                elif new_score >= 60:
                    trust_level = "🟡 Neutral"
                elif new_score >= 30:
                    trust_level = "🟠 Suspicious"
                else:
                    trust_level = "🔴 High Risk"

                embed.add_field(name="⚠️ Trust Level", value=trust_level, inline=True)
                embed.set_footer(text=f"Modified by {interaction.user.name}")

                await interaction.followup.send(embed=embed)
                await self.log_moderation_action(interaction.guild, embed)

            else:
                # View only embed
                embed = discord.Embed(
                    title="📊 TRUST SCORE",
                    description=f"Trust score for {user.mention}",
                    color=(
                        0x00FF00
                        if current_score >= 70
                        else 0xFF9900 if current_score >= 40 else 0xFF0000
                    ),
                    timestamp=datetime.now(timezone.utc),
                )
                embed.add_field(
                    name="👤 User",
                    value=f"{user.mention} (`{user.id}`)",
                    inline=True,
                )
                embed.add_field(
                    name="📊 Current Score",
                    value=f"{current_score:.1f}/100",
                    inline=True,
                )

                # Trust level
                if current_score >= 80:
                    trust_level = "🟢 Trusted"
                elif current_score >= 60:
                    trust_level = "🟡 Neutral"
                elif current_score >= 30:
                    trust_level = "🟠 Suspicious"
                else:
                    trust_level = "🔴 High Risk"

                embed.add_field(name="⚠️ Trust Level", value=trust_level, inline=True)

                if last_updated:
                    try:
                        updated_dt = datetime.fromisoformat(last_updated)
                        embed.add_field(
                            name="🕐 Last Updated",
                            value=f"<t:{int(updated_dt.timestamp())}:R>",
                            inline=True,
                        )
                    except:
                        pass

                # Get violation history
                cases = await self.get_user_cases(
                    interaction.guild_id, user.id, limit=10
                )
                if cases:
                    embed.add_field(
                        name="📜 Recent History",
                        value=f"{len(cases)} moderation cases",
                        inline=True,
                    )

                embed.set_footer(text="Use /trust_score <user> <score> to modify")

                await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Trust score error: {e}", exc_info=True)
            await interaction.followup.send(
                f"❌ Error managing trust score: {str(e)}", ephemeral=True
            )

    # ========================================================================
    # UTILITY FUNCTIONS
    # ========================================================================

    async def can_moderate(
        self, interaction: discord.Interaction, target: discord.Member
    ) -> bool:
        """Check if moderator can moderate target"""
        if target.id == interaction.user.id:
            await interaction.response.send_message(
                "❌ You cannot moderate yourself.", ephemeral=True
            )
            return False

        if target.id == self.bot.user.id:
            await interaction.response.send_message(
                "❌ You cannot moderate me.", ephemeral=True
            )
            return False

        if (
            target.top_role >= interaction.user.top_role
            and interaction.user.id != interaction.guild.owner_id
        ):
            await interaction.response.send_message(
                "❌ You cannot moderate someone with equal or higher role.",
                ephemeral=True,
            )
            return False

        if target.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You cannot moderate administrators.", ephemeral=True
            )
            return False

        return True

    def parse_duration(self, duration_str: str) -> Optional[int]:
        """Parse duration string (10m, 1h, 2d) to seconds"""
        match = re.match(r"(\d+)([smhd])", duration_str.lower())
        if not match:
            return None

        value, unit = match.groups()
        value = int(value)

        multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        return value * multipliers.get(unit, 60)

    def format_duration(self, seconds: int) -> str:
        """Format seconds to human-readable duration"""
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            return f"{seconds // 60} minutes"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m" if minutes else f"{hours} hours"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days}d {hours}h" if hours else f"{days} days"

    def get_action_color(self, action: ActionType) -> int:
        """Get color for action type"""
        colors = {
            ActionType.WARN: 0xFFAA00,
            ActionType.TIMEOUT: 0xFF6600,
            ActionType.KICK: 0xFF3300,
            ActionType.BAN: 0xFF0000,
            ActionType.SOFTBAN: 0xFFA500,
            ActionType.MUTE: 0xFF9900,
            ActionType.UNMUTE: 0x00FF00,
        }
        return colors.get(action, 0x3498DB)

    async def get_config(self, guild_id: int) -> ModerationConfig:
        """Get or create moderation config for guild"""
        if guild_id in self.configs:
            return self.configs[guild_id]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT config_json FROM moderation_configs WHERE guild_id = ?",
                (guild_id,),
            )
            row = cursor.fetchone()

            if row:
                config_dict = json.loads(row[0])
                config = ModerationConfig(**config_dict)
            else:
                config = ModerationConfig(guild_id=guild_id)
                await self.save_config(config)

        self.configs[guild_id] = config
        return config

    async def save_config(self, config: ModerationConfig):
        """Save moderation config to database"""
        config_dict = asdict(config)
        config_json = json.dumps(config_dict)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO moderation_configs (guild_id, config_json) VALUES (?, ?)",
                (config.guild_id, config_json),
            )
            conn.commit()

        self.configs[config.guild_id] = config

    async def create_case(
        self,
        guild_id: int,
        user_id: int,
        moderator_id: int,
        action: ActionType,
        violation: ViolationType,
        reason: str,
        severity: SeverityLevel = SeverityLevel.MEDIUM,
        expires_at: Optional[datetime] = None,
        evidence: List[str] = None,
        notes: str = "",
    ) -> ModerationCase:
        """Create a new moderation case"""
        case_id = self.case_counter[guild_id] + 1
        self.case_counter[guild_id] = case_id

        case = ModerationCase(
            case_id=case_id,
            guild_id=guild_id,
            user_id=user_id,
            moderator_id=moderator_id,
            action=action,
            violation=violation,
            reason=reason,
            timestamp=datetime.now(timezone.utc),
            expires_at=expires_at,
            severity=severity,
            evidence=evidence or [],
        )

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO moderation_cases
                (case_id, guild_id, user_id, moderator_id, action, violation, reason, timestamp, expires_at, active, severity, evidence_json, notes, appealed, appeal_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    case.case_id,
                    case.guild_id,
                    case.user_id,
                    case.moderator_id,
                    case.action.value,
                    case.violation.value,
                    case.reason,
                    case.timestamp.isoformat(),
                    case.expires_at.isoformat() if case.expires_at else None,
                    1,
                    case.severity.value,
                    json.dumps(case.evidence),
                    case.notes,
                    0,
                    None,
                ),
            )
            conn.commit()

        return case

    async def get_case(self, guild_id: int, case_id: int) -> Optional[ModerationCase]:
        """Get a specific case"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM moderation_cases WHERE guild_id = ? AND case_id = ?",
                (guild_id, case_id),
            )
            row = cursor.fetchone()

            if not row:
                return None

            return ModerationCase(
                case_id=row[0],
                guild_id=row[1],
                user_id=row[2],
                moderator_id=row[3],
                action=ActionType(row[4]),
                violation=ViolationType(row[5]),
                reason=row[6],
                timestamp=datetime.fromisoformat(row[7]),
                expires_at=datetime.fromisoformat(row[8]) if row[8] else None,
                active=bool(row[9]),
                severity=SeverityLevel(row[10]),
                evidence=json.loads(row[11]) if row[11] else [],
                notes=row[12] or "",
                appealed=bool(row[13]),
                appeal_status=row[14],
            )

    async def get_user_cases(
        self, guild_id: int, user_id: int, limit: int = 10
    ) -> List[ModerationCase]:
        """Get user's moderation cases"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """SELECT * FROM moderation_cases 
                WHERE guild_id = ? AND user_id = ? 
                ORDER BY timestamp DESC LIMIT ?""",
                (guild_id, user_id, limit),
            )

            cases = []
            for row in cursor.fetchall():
                cases.append(
                    ModerationCase(
                        case_id=row[0],
                        guild_id=row[1],
                        user_id=row[2],
                        moderator_id=row[3],
                        action=ActionType(row[4]),
                        violation=ViolationType(row[5]),
                        reason=row[6],
                        timestamp=datetime.fromisoformat(row[7]),
                        expires_at=datetime.fromisoformat(row[8]) if row[8] else None,
                        active=bool(row[9]),
                        severity=SeverityLevel(row[10]),
                        evidence=json.loads(row[11]) if row[11] else [],
                        notes=row[12] or "",
                        appealed=bool(row[13]),
                        appeal_status=row[14],
                    )
                )

            return cases

    async def increment_violation_count(
        self, guild_id: int, user_id: int, violation_type: str
    ) -> int:
        """Increment violation count and return new count"""
        with sqlite3.connect(self.db_path) as conn:
            # Get current counts
            cursor = conn.execute(
                f"SELECT {violation_type}_count FROM user_warnings WHERE guild_id = ? AND user_id = ?",
                (guild_id, user_id),
            )
            row = cursor.fetchone()

            if row:
                new_count = row[0] + 1
                conn.execute(
                    f"""UPDATE user_warnings SET {violation_type}_count = ?, last_violation = ? 
                    WHERE guild_id = ? AND user_id = ?""",
                    (
                        new_count,
                        datetime.now(timezone.utc).isoformat(),
                        guild_id,
                        user_id,
                    ),
                )
            else:
                new_count = 1
                conn.execute(
                    f"""INSERT INTO user_warnings (guild_id, user_id, {violation_type}_count, last_violation)
                    VALUES (?, ?, 1, ?)""",
                    (guild_id, user_id, datetime.now(timezone.utc).isoformat()),
                )

            conn.commit()
            return new_count

    async def get_user_violation_counts(
        self, guild_id: int, user_id: int
    ) -> Dict[str, int]:
        """Get user's violation counts"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT warning_count, timeout_count, kick_count FROM user_warnings WHERE guild_id = ? AND user_id = ?",
                (guild_id, user_id),
            )
            row = cursor.fetchone()

            if row:
                return {"warning": row[0], "timeout": row[1], "kick": row[2]}
            return {"warning": 0, "timeout": 0, "kick": 0}

    async def get_moderation_stats(
        self, guild_id: int, days: int = 7
    ) -> Dict[str, int]:
        """Get moderation statistics"""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            for action in ["warn", "timeout", "kick", "ban"]:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM moderation_cases WHERE guild_id = ? AND action = ? AND timestamp >= ?",
                    (guild_id, action, cutoff.isoformat()),
                )
                stats[f"{action}s"] = cursor.fetchone()[0]

            return stats

    async def log_moderation_action(self, guild: discord.Guild, embed: discord.Embed):
        """Log moderation action to mod log channel"""
        config = await self.get_config(guild.id)

        if config.mod_log_channel_id:
            try:
                channel = guild.get_channel(config.mod_log_channel_id)
                if channel:
                    await channel.send(embed=embed)
            except:
                pass

    @tasks.loop(minutes=5)
    async def cleanup_expired_actions(self):
        """Cleanup expired timeouts and mutes"""
        now = datetime.now(timezone.utc)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """UPDATE moderation_cases SET active = 0 
                WHERE active = 1 AND expires_at IS NOT NULL AND expires_at <= ?""",
                (now.isoformat(),),
            )
            conn.commit()

    @cleanup_expired_actions.before_loop
    async def before_cleanup(self):
        await self.bot.wait_until_ready()


# ============================================================================
# SETUP
# ============================================================================


async def setup(bot):
    await bot.add_cog(ComprehensiveModeration(bot))
    logger.info("✅ Comprehensive Moderation System loaded")
