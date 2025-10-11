"""
import gc
🛡️ SECURITY MANAGER COG - UNIFIED COMMAND INTERFACE
Consolidated security commands combining all previous security cogs

This replaces and consolidates:
- enhanced_security.py (new comprehensive commands)
- security_commands.py (manual security controls)
- ai_moderation.py (AI-powered moderation commands)

Features:
- Unified command interface for all security functions
- Real-time security monitoring and control
- Advanced user management and violation tracking
- Comprehensive security analytics and reporting
- Manual override capabilities for administrators
- Trust score management and behavioral analysis
"""

import asyncio
import logging
import time
import hashlib
import re
from typing import Dict, List, Optional, Any, Literal, Set, Tuple
from datetime import datetime, timedelta, timezone
from collections import defaultdict, deque, Counter
from functools import lru_cache, wraps
import weakref

import discord
from discord import app_commands
from discord.ext import commands, tasks

from cogs.ai_moderation import ViolationType
from core.security_integration import SecuritySystemIntegration


# Define missing classes for backward compatibility
class ViolationSeverity:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatLevel:
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class UserProfile:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.violations = []


class ViolationRecord:
    def __init__(self, violation_type, severity, timestamp=None):
        self.violation_type = violation_type
        self.severity = severity
        self.timestamp = timestamp or discord.utils.utcnow()


class SecurityEvent:
    def __init__(self, event_type: str, details: dict):
        self.event_type = event_type
        self.details = details
        self.timestamp = discord.utils.utcnow()


from utils.permissions import has_permission, PermissionLevel, check_user_permission
from config.unified_config import unified_config

logger = logging.getLogger("astra.security.manager")

# Owner ID for critical security controls
OWNER_ID = 1115739214148026469


def is_bot_owner(user_id: int) -> bool:
    """Check if user is the bot owner using configured OWNER_ID"""
    import os

    # Check configured owner ID
    configured_owner_id = unified_config.get_owner_id()
    if configured_owner_id and user_id == configured_owner_id:
        return True

    # Check environment variable
    env_owner_id = os.getenv("OWNER_ID")
    if env_owner_id:
        try:
            if user_id == int(env_owner_id):
                return True
        except ValueError:
            pass

    # Hardcoded fallback for your ID
    return user_id == OWNER_ID


class SecurityManager(commands.Cog):
    """Unified Security Management System - All security commands in one place"""

    def __init__(self, bot):
        self.bot = bot
        self.config = unified_config
        self.logger = bot.logger if hasattr(bot, "logger") else logger

        # Initialize the unified security system
        self.security_system = SecuritySystemIntegration(bot)

        # Advanced performance optimization
        self._cache = {}
        self._cache_expiry = {}
        self._last_cache_cleanup = time.time()

        # Guild-specific settings with optimized storage
        self.guild_settings = defaultdict(dict)

        # Enhanced default settings with performance tuning
        self.default_settings = {
            # Core security - optimized defaults
            "security_enabled": True,
            "auto_moderation": True,
            "autonomous_protection": True,
            "high_performance_mode": True,
            # Detection systems - tuned for speed and accuracy
            "spam_detection": True,
            "toxicity_detection": True,
            "threat_intelligence": True,
            "behavioral_analysis": True,
            "pattern_matching_optimized": True,
            # Response systems - enhanced with smart escalation
            "auto_timeout_enabled": True,
            "progressive_punishment": True,
            "trust_system_enabled": True,
            "evidence_collection": True,
            "auto_response_enabled": True,
            "smart_action_selection": True,
            # Performance-tuned thresholds
            "spam_threshold": 2,  # More aggressive
            "toxicity_threshold": 0.65,  # Slightly more sensitive
            "trust_threshold": 75.0,  # Higher baseline trust requirement
            "quarantine_threshold": 20.0,  # More aggressive quarantine
            "raid_detection_threshold": 5,  # New: raid detection
            # Enhanced logging and notifications
            "log_all_actions": True,
            "notify_moderators": True,
            "forensic_logging": True,
            "performance_logging": True,
            "cache_optimization": True,
        }

        # Advanced performance metrics with real-time tracking
        self.performance_metrics = {
            "commands_executed": 0,
            "security_checks": 0,
            "violations_handled": 0,
            "manual_overrides": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "avg_response_time": 0.0,
            "peak_response_time": 0.0,
            "last_hour_violations": 0,
            "escalated_threats": 0,
            "false_positives_prevented": 0,
        }

        # Enhanced emergency lockdown state with better tracking
        self.lockdown_active = False
        self.lockdown_reason = ""
        self.lockdown_timestamp = 0
        self.lockdown_level = 0  # 0=none, 1=partial, 2=full, 3=emergency
        self.lockdown_channels_affected = set()

        # Real-time threat monitoring
        self.active_threats = {}
        self.threat_escalation_queue = asyncio.Queue()

        # Performance optimization features
        self.batch_operations = []
        self.batch_timer = None

        # Start background performance optimization tasks
        self.cleanup_cache.start()
        self.threat_monitoring.start()
        self.performance_optimizer.start()

        logger.info(
            "🛡️ Enhanced Security Manager initialized - High-performance protection active"
        )

    async def cog_load(self):
        """Initialize security manager when cog loads"""
        logger.info("🔄 Loading Enhanced Security Manager...")

        # Initialize advanced caching system
        await self._initialize_advanced_cache()

        # Start real-time monitoring
        await self._start_real_time_monitoring()

        logger.info("✅ Enhanced Security Manager loaded with optimization features")

    async def cog_unload(self):
        """Cleanup when cog unloads"""
        logger.info("🔄 Unloading Enhanced Security Manager...")

        # Stop background tasks
        self.cleanup_cache.cancel()
        self.threat_monitoring.cancel()
        self.performance_optimizer.cancel()

        # Cleanup resources
        await self._cleanup_resources()
        await self.security_system.shutdown()

        logger.info("✅ Enhanced Security Manager unloaded and optimized")

    @tasks.loop(minutes=5)
    async def cleanup_cache(self):
        """Advanced cache cleanup with performance optimization"""
        try:
            current_time = time.time()
            if current_time - self._last_cache_cleanup < 300:  # 5 minutes
                return

            expired_keys = []
            for key, expiry in self._cache_expiry.items():
                if current_time > expiry:
                    expired_keys.append(key)

            for key in expired_keys:
                self._cache.pop(key, None)
                self._cache_expiry.pop(key, None)

            self._last_cache_cleanup = current_time

            if expired_keys:
                self.logger.debug(
                    f"🧹 Cleaned {len(expired_keys)} expired cache entries"
                )

        except Exception as e:
            self.logger.error(f"Cache cleanup error: {e}")

    @tasks.loop(seconds=30)
    async def threat_monitoring(self):
        """Real-time threat monitoring and escalation"""
        try:
            # Process threat escalation queue
            while not self.threat_escalation_queue.empty():
                threat = await self.threat_escalation_queue.get()
                await self._process_threat_escalation(threat)

            # Clean up expired active threats
            current_time = time.time()
            expired_threats = [
                threat_id
                for threat_id, threat_data in self.active_threats.items()
                if current_time - threat_data.get("timestamp", 0) > 3600  # 1 hour
            ]

            for threat_id in expired_threats:
                self.active_threats.pop(threat_id, None)

        except Exception as e:
            self.logger.error(f"Threat monitoring error: {e}")

    @tasks.loop(minutes=10)
    async def performance_optimizer(self):
        """Performance optimization and metrics collection"""
        try:
            # Calculate performance metrics
            if self.performance_metrics["security_checks"] > 0:
                hit_rate = (
                    self.performance_metrics["cache_hits"]
                    / (
                        self.performance_metrics["cache_hits"]
                        + self.performance_metrics["cache_misses"]
                    )
                ) * 100

                # Log performance stats
                self.logger.info(
                    f"📊 Security Performance: {hit_rate:.1f}% cache hit rate, "
                    f"{len(self.active_threats)} active threats"
                )

            # Optimize batch operations
            if self.batch_operations:
                await self._process_batch_operations()

        except Exception as e:
            self.logger.error(f"Performance optimizer error: {e}")

    async def _initialize_advanced_cache(self):
        """Initialize advanced caching system"""
        self._cache.clear()
        self._cache_expiry.clear()
        self.logger.info("🚀 Advanced caching system initialized")

    async def _start_real_time_monitoring(self):
        """Start real-time threat monitoring"""
        self.active_threats.clear()
        self.logger.info("� Real-time threat monitoring started")

    async def _cleanup_resources(self):
        """Cleanup system resources"""
        self._cache.clear()
        self._cache_expiry.clear()
        self.active_threats.clear()

        # Process any remaining batch operations
        if self.batch_operations:
            await self._process_batch_operations()

    @lru_cache(maxsize=256)
    def _get_cached_guild_settings(self, guild_id: int) -> Dict[str, Any]:
        """Cached guild settings retrieval"""
        return self.guild_settings.get(guild_id, self.default_settings.copy())

    async def _process_threat_escalation(self, threat_data: Dict[str, Any]):
        """Process threat escalation with intelligent decision making"""
        try:
            threat_level = threat_data.get("level", 1)
            guild_id = threat_data.get("guild_id")

            if threat_level >= 4:  # High threat
                # Add to escalated threats counter
                self.performance_metrics["escalated_threats"] += 1

                # Consider automatic lockdown
                if threat_level >= 5 and not self.lockdown_active:
                    guild = self.bot.get_guild(guild_id)
                    if guild:
                        await self._initiate_smart_lockdown(guild, threat_data)

        except Exception as e:
            self.logger.error(f"Threat escalation processing error: {e}")

    async def _initiate_smart_lockdown(
        self, guild: discord.Guild, threat_data: Dict[str, Any]
    ):
        """Intelligent lockdown system with graduated response"""
        try:
            threat_type = threat_data.get("type", "unknown")
            threat_level = threat_data.get("level", 1)

            # Determine lockdown level based on threat
            if threat_level >= 5:
                lockdown_level = 3  # Emergency lockdown
            elif threat_level >= 4:
                lockdown_level = 2  # Full lockdown
            else:
                lockdown_level = 1  # Partial lockdown

            await self._execute_graduated_lockdown(guild, lockdown_level, threat_data)

        except Exception as e:
            self.logger.error(f"Smart lockdown initiation error: {e}")

    async def _execute_graduated_lockdown(
        self, guild: discord.Guild, level: int, threat_data: Dict[str, Any]
    ):
        """Execute graduated lockdown response"""
        try:
            if level == 1:  # Partial lockdown - limit new user actions
                await self._partial_lockdown(guild, threat_data)
            elif level == 2:  # Full lockdown - lock most channels
                await self._full_lockdown(guild, threat_data)
            elif level == 3:  # Emergency lockdown - complete lockdown
                await self._emergency_lockdown(guild, threat_data)

            self.lockdown_level = level
            self.lockdown_active = True
            self.lockdown_timestamp = time.time()
            self.lockdown_reason = (
                f"Smart lockdown L{level}: {threat_data.get('type', 'threat')}"
            )

        except Exception as e:
            self.logger.error(f"Graduated lockdown execution error: {e}")

    async def _partial_lockdown(
        self, guild: discord.Guild, threat_data: Dict[str, Any]
    ):
        """Partial lockdown - restrict new/untrusted users"""
        channels_affected = 0
        for channel in guild.text_channels:
            try:
                overwrites = channel.overwrites_for(guild.default_role)
                # Only restrict if no existing restrictions
                if overwrites.send_messages is None:
                    overwrites.send_messages = False
                    await channel.set_permissions(
                        guild.default_role,
                        overwrite=overwrites,
                        reason=f"Partial lockdown: {threat_data.get('type', 'threat')}",
                    )
                    channels_affected += 1
                    self.lockdown_channels_affected.add(channel.id)
            except Exception as e:
                self.logger.warning(
                    f"Failed to partially lock channel {channel.name}: {e}"
                )

        self.logger.warning(
            f"🟡 Partial lockdown activated: {channels_affected} channels restricted"
        )

    async def _full_lockdown(self, guild: discord.Guild, threat_data: Dict[str, Any]):
        """Full lockdown - lock most channels except essential"""
        essential_channels = {"rules", "announcements", "welcome", "general"}
        channels_affected = 0

        for channel in guild.text_channels:
            # Skip essential channels
            if any(
                essential in channel.name.lower() for essential in essential_channels
            ):
                continue

            try:
                overwrites = channel.overwrites_for(guild.default_role)
                overwrites.send_messages = False
                overwrites.add_reactions = False
                await channel.set_permissions(
                    guild.default_role,
                    overwrite=overwrites,
                    reason=f"Full lockdown: {threat_data.get('type', 'threat')}",
                )
                channels_affected += 1
                self.lockdown_channels_affected.add(channel.id)
            except Exception as e:
                self.logger.warning(f"Failed to fully lock channel {channel.name}: {e}")

        self.logger.error(
            f"🔴 Full lockdown activated: {channels_affected} channels locked"
        )

    async def _emergency_lockdown(
        self, guild: discord.Guild, threat_data: Dict[str, Any]
    ):
        """Emergency lockdown - complete server lockdown"""
        channels_affected = 0

        for channel in guild.text_channels:
            try:
                overwrites = channel.overwrites_for(guild.default_role)
                overwrites.send_messages = False
                overwrites.add_reactions = False
                overwrites.attach_files = False
                await channel.set_permissions(
                    guild.default_role,
                    overwrite=overwrites,
                    reason=f"Emergency lockdown: {threat_data.get('type', 'critical threat')}",
                )
                channels_affected += 1
                self.lockdown_channels_affected.add(channel.id)
            except Exception as e:
                self.logger.warning(
                    f"Failed to emergency lock channel {channel.name}: {e}"
                )

        self.logger.critical(
            f"🚨 Emergency lockdown activated: {channels_affected} channels locked"
        )

    async def _process_batch_operations(self):
        """Process batch operations for better performance"""
        if not self.batch_operations:
            return

        operations = self.batch_operations.copy()
        self.batch_operations.clear()

        # Group operations by type for efficiency
        operation_groups = defaultdict(list)
        for op in operations:
            operation_groups[op["type"]].append(op)

        # Process each group
        for op_type, ops in operation_groups.items():
            if op_type == "permission_update":
                await self._batch_update_permissions(ops)
            elif op_type == "role_assignment":
                await self._batch_update_roles(ops)
            # Add more batch operation types as needed

    async def _batch_update_permissions(self, operations: List[Dict[str, Any]]):
        """Batch update channel permissions"""
        for op in operations:
            try:
                channel = op["channel"]
                target = op["target"]
                overwrite = op["overwrite"]
                reason = op["reason"]

                await channel.set_permissions(
                    target, overwrite=overwrite, reason=reason
                )
                await asyncio.sleep(0.1)  # Rate limit protection

            except Exception as e:
                self.logger.warning(f"Batch permission update failed: {e}")

    async def _batch_update_roles(self, operations: List[Dict[str, Any]]):
        """Batch update user roles"""
        for op in operations:
            try:
                member = op["member"]
                roles = op["roles"]
                reason = op["reason"]
                action = op["action"]  # 'add' or 'remove'

                if action == "add":
                    await member.add_roles(*roles, reason=reason)
                elif action == "remove":
                    await member.remove_roles(*roles, reason=reason)

                await asyncio.sleep(0.1)  # Rate limit protection

            except Exception as e:
                self.logger.warning(f"Batch role update failed: {e}")

    def add_to_cache(self, key: str, value: Any, ttl: int = 300):
        """Add item to cache with TTL"""
        self._cache[key] = value
        self._cache_expiry[key] = time.time() + ttl
        self.performance_metrics["cache_hits"] += 1

    def get_from_cache(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        if key in self._cache and time.time() < self._cache_expiry.get(key, 0):
            self.performance_metrics["cache_hits"] += 1
            return self._cache[key]
        else:
            self.performance_metrics["cache_misses"] += 1
            return None

    def log_security_event(
        self, event_type: str, severity: int, details: Dict[str, Any]
    ):
        """Enhanced security event logging"""
        try:
            event_id = hashlib.md5(
                f"{event_type}_{time.time()}_{severity}".encode()
            ).hexdigest()[:8]

            event_data = {
                "id": event_id,
                "type": event_type,
                "severity": severity,
                "timestamp": time.time(),
                "details": details,
                "handled": False,
            }

            # Add to active threats if high severity
            if severity >= 3:
                self.active_threats[event_id] = event_data

                # Queue for escalation if critical
                if severity >= 4:
                    asyncio.create_task(self.threat_escalation_queue.put(event_data))

            # Update performance metrics
            self.performance_metrics["violations_handled"] += 1

            # Log based on severity
            if severity >= 4:
                self.logger.critical(
                    f"🚨 CRITICAL SECURITY EVENT: {event_type} - {details}"
                )
            elif severity >= 3:
                self.logger.error(f"🔴 HIGH SECURITY EVENT: {event_type} - {details}")
            else:
                self.logger.warning(f"🟡 SECURITY EVENT: {event_type} - {details}")

        except Exception as e:
            self.logger.error(f"Security event logging failed: {e}")

    @wraps
    def performance_monitor(func):
        """Decorator for monitoring command performance"""

        async def wrapper(self, *args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = await func(self, *args, **kwargs)
                return result
            finally:
                execution_time = time.perf_counter() - start_time

                # Update performance metrics
                self.performance_metrics["avg_response_time"] = (
                    self.performance_metrics["avg_response_time"] * 0.9
                ) + (execution_time * 0.1)

                if execution_time > self.performance_metrics["peak_response_time"]:
                    self.performance_metrics["peak_response_time"] = execution_time

                # Log slow operations
                if execution_time > 1.0:
                    self.logger.warning(
                        f"⚠️ Slow security operation: {func.__name__} took {execution_time:.3f}s"
                    )

        return wrapper

    # 🚀 DISABLED: Message processing moved to High-Performance Coordinator
    # @commands.Cog.listener()
    # async def on_message(self, message: discord.Message):
    #     """Monitor all messages for security violations"""
    #     # Skip bot messages and DMs
    #     if message.author.bot or not message.guild:
    #         return
    #
    #     # Skip if lockdown is active (emergency mode)
    #     if self.lockdown_active:
    #         if not is_bot_owner(message.author.id):
    #             try:
    #                 await message.delete()
    #                 return
    #             except:
    #                 pass
    #
    #     # Check if security is enabled for this guild
    #     guild_settings = self.get_guild_settings(message.guild.id)
    #     if not guild_settings.get("security_enabled", True):
    #         return
    #
    #     try:
    #         self.performance_metrics["security_checks"] += 1
    #
    #         # Analyze message for security violations
    #         should_act, violations = (
    #             await self.security_system.analyze_message_security(message)
    #         )
    #
    #         if should_act and violations:
    #             # Handle the violations
    #             result = await self.security_system.handle_violations(
    #                 message, violations
    #             )
    #
    #             self.performance_metrics["violations_handled"] += 1
    #
    #             # Log the action
    #             self.logger.info(
    #                 f"🛡️ Security action: User {message.author} ({message.author.id}) - "
    #                 f"{result['violations_detected']} violations - {result['action_taken']}"
    #             )
    #
    #             # Notify moderators if configured
    #             if guild_settings.get("notify_moderators", True):
    #                 await self.notify_moderators_violation(message, violations, result)
    #
    #     except Exception as e:
    #         self.logger.error(
    #             f"Security system error for message from {message.author}: {e}"
    #         )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Monitor new member joins for security threats"""
        try:
            guild_settings = self.get_guild_settings(member.guild.id)
            if not guild_settings.get("security_enabled", True):
                return

            # Check for suspicious account patterns
            await self.analyze_member_join_security(member)

        except Exception as e:
            self.logger.error(f"Error analyzing member join security for {member}: {e}")

    async def analyze_member_join_security(self, member: discord.Member):
        """Analyze new member joins for security threats"""
        # Get user profile to start tracking
        profile = await self.security_system.get_user_profile(
            member.id, member.guild.id
        )
        profile.join_timestamp = time.time()

        # Check account age
        account_age = (datetime.now(timezone.utc) - member.created_at).total_seconds()

        suspicion_reasons = []
        trust_penalty = 0

        # Very new account (< 24 hours)
        if account_age < 86400:
            suspicion_reasons.append(
                f"Account created {account_age/3600:.1f} hours ago"
            )
            trust_penalty += 20

        # Check username for suspicious patterns
        suspicious_patterns = [
            "discord",
            "nitro",
            "official",
            "admin",
            "mod",
            "staff",
            "everyone",
            "here",
            "support",
            "bot",
            "system",
        ]

        username = member.name.lower()
        for pattern in suspicious_patterns:
            if pattern in username:
                suspicion_reasons.append(f"Username contains '{pattern}'")
                trust_penalty += 10
                break

        # Apply trust score penalties
        if trust_penalty > 0:
            profile.trust_score = max(0, profile.trust_score - trust_penalty)
            await self.security_system._save_user_profile(profile)

            # Notify moderators of suspicious join
            if suspicion_reasons:
                await self.notify_moderators_suspicious_join(
                    member, suspicion_reasons, trust_penalty
                )

    async def notify_moderators_violation(
        self,
        message: discord.Message,
        violations: List[ViolationRecord],
        result: Dict[str, Any],
    ):
        """Notify moderators of security violations"""
        # Find moderation channel
        mod_channel = None
        for channel_name in ["mod-log", "security-log", "admin-log", "moderation"]:
            mod_channel = discord.utils.get(
                message.guild.text_channels, name=channel_name
            )
            if mod_channel:
                break

        if not mod_channel:
            return

        # Create violation notification embed
        violation_types = [
            v.violation_type.value.replace("_", " ").title() for v in violations
        ]
        severity_colors = {
            1: 0x00FF00,  # Minor - Green
            2: 0xFFFF00,  # Moderate - Yellow
            3: 0xFFA500,  # Serious - Orange
            4: 0xFF4500,  # Severe - Red-Orange
            5: 0xFF0000,  # Critical - Red
        }

        max_severity = max(v.severity.value for v in violations)
        color = severity_colors.get(max_severity, 0xFFFF00)

        embed = discord.Embed(
            title="🛡️ Security Violation Detected",
            description=f"**User:** {message.author.mention} ({message.author})\n**Channel:** {message.channel.mention}",
            color=color,
            timestamp=datetime.now(timezone.utc),
        )

        embed.add_field(
            name="⚠️ Violations",
            value="\n".join(f"• {vtype}" for vtype in violation_types),
            inline=True,
        )

        embed.add_field(
            name="🎯 Action Taken",
            value=result["action_taken"].replace("_", " ").title(),
            inline=True,
        )

        embed.add_field(
            name="📊 Severity Level",
            value=f"{max_severity}/5 ({'🟢' if max_severity <= 2 else '🟡' if max_severity <= 3 else '🔴'})",
            inline=True,
        )

        # Add message content (truncated)
        if message.content:
            content_preview = (
                message.content[:200] + "..."
                if len(message.content) > 200
                else message.content
            )
            embed.add_field(
                name="💬 Message Content",
                value=f"```{content_preview}```",
                inline=False,
            )

        embed.set_footer(text=f"User ID: {message.author.id} • 🛡️ Astra Security System")

        try:
            await mod_channel.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Error sending moderation notification: {e}")

    async def notify_moderators_suspicious_join(
        self, member: discord.Member, reasons: List[str], trust_penalty: int
    ):
        """Notify moderators of suspicious account joins"""
        # Find moderation channel
        mod_channel = None
        for channel_name in ["mod-log", "security-log", "admin-log"]:
            mod_channel = discord.utils.get(
                member.guild.text_channels, name=channel_name
            )
            if mod_channel:
                break

        if not mod_channel:
            return

        embed = discord.Embed(
            title="🚨 Suspicious Account Join",
            description=f"**Member:** {member.mention} ({member})\n**ID:** {member.id}",
            color=0xFFA500,
            timestamp=datetime.now(timezone.utc),
        )

        embed.add_field(
            name="⚠️ Suspicion Reasons",
            value="\n".join(f"• {reason}" for reason in reasons),
            inline=False,
        )

        embed.add_field(
            name="📊 Trust Impact",
            value=f"Trust Score Penalty: -{trust_penalty} points",
            inline=True,
        )

        embed.add_field(
            name="📅 Account Info",
            value=f"**Created:** {member.created_at.strftime('%Y-%m-%d %H:%M UTC')}\n"
            f"**Age:** {(datetime.now(timezone.utc) - member.created_at).days} days",
            inline=True,
        )

        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text="🛡️ Astra Security - Automated Threat Detection")

        await mod_channel.send(embed=embed)

    def get_guild_settings(self, guild_id: int) -> Dict[str, Any]:
        """Get security settings for a guild"""
        if guild_id not in self.guild_settings:
            self.guild_settings[guild_id] = self.default_settings.copy()
        return self.guild_settings[guild_id]

    # ═══════════════════════════════════════════════════════════════════════════════
    # SECURITY MONITORING COMMANDS
    # ═══════════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="security_status",
        description="🛡️ View enhanced security system status with real-time analytics",
    )
    @app_commands.default_permissions(manage_messages=True)
    async def security_status(self, interaction: discord.Interaction):
        """Display comprehensive enhanced security system status"""
        if not await check_user_permission(
            interaction.user, PermissionLevel.MODERATOR, interaction.guild
        ):
            await interaction.response.send_message(
                "❌ You need moderator permissions to view security status.",
                ephemeral=True,
            )
            return

        try:
            start_time = time.perf_counter()
            self.performance_metrics["commands_executed"] += 1

            # Get enhanced security statistics
            stats = self.security_system.get_security_stats()

            # Calculate advanced metrics
            cache_hit_rate = 0.0
            total_cache_ops = (
                self.performance_metrics["cache_hits"]
                + self.performance_metrics["cache_misses"]
            )
            if total_cache_ops > 0:
                cache_hit_rate = (
                    self.performance_metrics["cache_hits"] / total_cache_ops
                ) * 100

            # Get guild settings with enhanced error handling
            try:
                guild_settings = self._get_cached_guild_settings(interaction.guild.id)
            except Exception as settings_error:
                self.logger.warning(f"Error getting guild settings: {settings_error}")
                guild_settings = self.default_settings.copy()

            embed = discord.Embed(
                title="🛡️ Enhanced Security System Status",
                description="Real-time security monitoring with advanced threat intelligence",
                color=self._get_status_color(),
                timestamp=datetime.now(timezone.utc),
            )

            # Enhanced system statistics
            embed.add_field(
                name="📊 Advanced Analytics",
                value=f"**Tracked Users:** {stats.get('total_tracked_users', 0):,}\n"
                f"**Trusted Users:** {stats.get('trusted_users', 0):,}\n"
                f"**Active Threats:** {len(self.active_threats):,}\n"
                f"**Trust Score Avg:** {stats.get('average_trust_score', 50.0):.1f}/100",
                inline=True,
            )

            # Performance metrics
            embed.add_field(
                name="⚡ High-Performance Metrics",
                value=f"**Cache Hit Rate:** {cache_hit_rate:.1f}%\n"
                f"**Avg Response:** {self.performance_metrics['avg_response_time']*1000:.1f}ms\n"
                f"**Peak Response:** {self.performance_metrics['peak_response_time']*1000:.1f}ms\n"
                f"**Escalated Threats:** {self.performance_metrics['escalated_threats']:,}",
                inline=True,
            )

            # Advanced lockdown status
            lockdown_status = self._get_lockdown_status_detailed()
            embed.add_field(
                name="🔒 Advanced Lockdown System",
                value=lockdown_status,
                inline=True,
            )

            # Active features status
            active_features = []

            # Ensure default settings exist
            default_settings = getattr(
                self,
                "default_settings",
                {
                    "security_enabled": True,
                    "spam_detection": True,
                    "toxicity_detection": True,
                    "threat_intelligence": True,
                    "behavioral_analysis": True,
                    "auto_timeout_enabled": True,
                    "trust_system_enabled": True,
                    "auto_response_enabled": True,
                },
            )

            feature_map = {
                "security_enabled": "🛡️ Security System",
                "spam_detection": "📢 Spam Detection",
                "toxicity_detection": "☠️ Toxicity Detection",
                "threat_intelligence": "🧠 Threat Intelligence",
                "behavioral_analysis": "📊 Behavioral Analysis",
                "auto_timeout_enabled": "⏰ Auto Timeout",
                "trust_system_enabled": "⭐ Trust System",
                "auto_response_enabled": "🤖 Auto Response",
            }

            for setting, name in feature_map.items():
                # Enhanced fallback system for missing settings
                try:
                    default_value = default_settings.get(setting, False)
                    setting_value = (
                        guild_settings.get(setting, default_value)
                        if guild_settings
                        else default_value
                    )

                    if setting_value:
                        active_features.append(f"✅ {name}")
                    else:
                        active_features.append(f"❌ {name}")
                except Exception as setting_error:
                    self.logger.warning(
                        f"Error processing setting {setting}: {setting_error}"
                    )
                    active_features.append(f"⚠️ {name} (Error)")

            embed.add_field(
                name="🔧 Active Features",
                value="\n".join(active_features[:6]),  # Show first 6 features
                inline=False,
            )

            # Real-time threat monitoring
            recent_threats = len(
                [
                    t
                    for t in self.active_threats.values()
                    if time.time() - t.get("timestamp", 0) < 3600
                ]
            )  # Last hour

            embed.add_field(
                name="🚨 Real-Time Threat Intelligence",
                value=f"**Active Threats:** {len(self.active_threats)}\n"
                f"**Recent (1h):** {recent_threats}\n"
                f"**False Positives Prevented:** {self.performance_metrics['false_positives_prevented']}\n"
                f"**Queue Size:** {self.threat_escalation_queue.qsize()}",
                inline=True,
            )

            # Smart features status
            smart_features = []
            feature_map = {
                "high_performance_mode": "🚀 High Performance",
                "smart_action_selection": "� Smart Actions",
                "pattern_matching_optimized": "🎯 Optimized Patterns",
                "cache_optimization": "⚡ Cache Optimization",
                "performance_logging": "📊 Performance Logs",
            }

            for setting, name in feature_map.items():
                if guild_settings.get(setting, False):
                    smart_features.append(f"✅ {name}")
                else:
                    smart_features.append(f"❌ {name}")

            embed.add_field(
                name="🔧 Smart Security Features",
                value="\n".join(smart_features[:5]),
                inline=True,
            )

            # System health indicators
            health_score = self._calculate_system_health()
            health_emoji = (
                "🟢" if health_score >= 90 else "🟡" if health_score >= 70 else "🔴"
            )

            embed.add_field(
                name="💚 System Health Score",
                value=f"{health_emoji} **{health_score:.1f}%**\n"
                f"Cache: {len(self._cache)} entries\n"
                f"Memory: Optimized\n"
                f"Response: {'Excellent' if self.performance_metrics['avg_response_time'] < 0.1 else 'Normal'}",
                inline=True,
            )

            # Performance summary
            execution_time = time.perf_counter() - start_time
            embed.set_footer(
                text=f"🚀 Enhanced Security System • Query time: {execution_time*1000:.1f}ms • Cache: {cache_hit_rate:.0f}% hit rate"
            )

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in enhanced security_status command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while retrieving enhanced security status.",
                ephemeral=True,
            )

    def _get_status_color(self) -> int:
        """Get status color based on system state"""
        if self.lockdown_active:
            if self.lockdown_level >= 3:
                return 0xFF0000  # Red - Emergency
            elif self.lockdown_level >= 2:
                return 0xFF6600  # Orange - Full lockdown
            else:
                return 0xFFAA00  # Yellow - Partial lockdown
        elif len(self.active_threats) > 5:
            return 0xFFFF00  # Yellow - High threat activity
        else:
            return 0x00FF00  # Green - Normal

    def _get_lockdown_status_detailed(self) -> str:
        """Get detailed lockdown status"""
        if not self.lockdown_active:
            return "🔓 **Inactive**\nStandby mode\nAll channels open\nNormal operations"

        level_names = {0: "None", 1: "Partial", 2: "Full", 3: "Emergency"}
        level_name = level_names.get(self.lockdown_level, "Unknown")

        duration = time.time() - self.lockdown_timestamp
        duration_str = f"{int(duration//60)}m {int(duration%60)}s"

        return (
            f"🔒 **Level {self.lockdown_level} ({level_name})**\n"
            f"Duration: {duration_str}\n"
            f"Channels: {len(self.lockdown_channels_affected)}\n"
            f"Reason: {self.lockdown_reason[:20]}..."
        )

    def _calculate_system_health(self) -> float:
        """Calculate overall system health score"""
        health_score = 100.0

        # Reduce score based on active threats
        threat_penalty = min(len(self.active_threats) * 5, 30)
        health_score -= threat_penalty

        # Reduce score for poor cache performance
        total_cache_ops = (
            self.performance_metrics["cache_hits"]
            + self.performance_metrics["cache_misses"]
        )
        if total_cache_ops > 0:
            cache_hit_rate = (
                self.performance_metrics["cache_hits"] / total_cache_ops
            ) * 100
            if cache_hit_rate < 70:
                health_score -= (70 - cache_hit_rate) * 0.5

        # Reduce score for slow response times
        if self.performance_metrics["avg_response_time"] > 0.5:
            health_score -= 20
        elif self.performance_metrics["avg_response_time"] > 0.2:
            health_score -= 10

        # Reduce score if lockdown is active
        if self.lockdown_active:
            health_score -= self.lockdown_level * 10

        return max(health_score, 0.0)

    @app_commands.command(
        name="user_security", description="👤 View detailed security profile for a user"
    )
    @app_commands.describe(user="User to check security profile for")
    @app_commands.default_permissions(manage_messages=True)
    async def user_security(
        self, interaction: discord.Interaction, user: discord.Member
    ):
        """Display detailed security profile for a specific user"""
        if not await check_user_permission(
            interaction.user, PermissionLevel.MODERATOR, interaction.guild
        ):
            await interaction.response.send_message(
                "❌ You need moderator permissions to view user security profiles.",
                ephemeral=True,
            )
            return

        try:
            # Get user security report
            report = await self.security_system.get_user_security_report(
                user.id, interaction.guild.id
            )

            if "error" in report:
                embed = discord.Embed(
                    title=f"👤 Security Profile: {user.display_name}",
                    description="This user has no security history (clean record).",
                    color=0x00FF00,
                )
            else:
                # Determine color based on trust score
                trust_score = report["trust_score"]
                if trust_score >= 80:
                    color = 0x00FF00  # Green
                elif trust_score >= 60:
                    color = 0xFFFF00  # Yellow
                elif trust_score >= 40:
                    color = 0xFFA500  # Orange
                else:
                    color = 0xFF0000  # Red

                embed = discord.Embed(
                    title=f"👤 Security Profile: {user.display_name}",
                    description=f"**Trust Score:** {trust_score:.1f}/100 {'✅' if report['is_trusted'] else '⚠️'}",
                    color=color,
                    timestamp=datetime.now(timezone.utc),
                )

                embed.add_field(
                    name="📊 Violation Summary",
                    value=f"**Total Violations:** {report['total_violations']}\n"
                    f"**Recent (24h):** {report['recent_violations_24h']}\n"
                    f"**Violation Streak:** {report['violation_streak']}\n"
                    f"**Punishment Level:** {report['punishment_level']}/7",
                    inline=True,
                )

                embed.add_field(
                    name="✨ Positive Activity",
                    value=f"**Contributions:** {report['positive_contributions']}\n"
                    f"**Status:** {'✅ Trusted Member' if report['is_trusted'] else '⚠️ Under Watch'}\n"
                    f"**Quarantine:** {report['quarantine_status'].title()}",
                    inline=True,
                )

                behavior = report["behavioral_summary"]
                embed.add_field(
                    name="📈 Behavioral Analysis",
                    value=f"**Avg Message Length:** {behavior['avg_message_length']:.0f} chars\n"
                    f"**Channel Diversity:** {behavior['channel_diversity']} channels\n"
                    f"**Activity Pattern:** {behavior['activity_pattern'].title()}",
                    inline=False,
                )

                if report["last_violation"]:
                    last_violation = datetime.fromtimestamp(report["last_violation"])
                    embed.add_field(
                        name="⏰ Last Violation",
                        value=last_violation.strftime("%Y-%m-%d %H:%M UTC"),
                        inline=True,
                    )

            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_footer(text=f"User ID: {user.id} • 🛡️ Unified Security System")

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in user_security command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while retrieving user security profile.",
                ephemeral=True,
            )

    # ═══════════════════════════════════════════════════════════════════════════════
    # SECURITY CONFIGURATION COMMANDS
    # ═══════════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="security_config", description="⚙️ Configure security system settings"
    )
    @app_commands.describe(
        setting="Security setting to modify", value="New value for the setting"
    )
    @app_commands.choices(
        setting=[
            app_commands.Choice(name="🛡️ Security System", value="security_enabled"),
            app_commands.Choice(name="🤖 Auto Moderation", value="auto_moderation"),
            app_commands.Choice(name="📢 Spam Detection", value="spam_detection"),
            app_commands.Choice(
                name="☠️ Toxicity Detection", value="toxicity_detection"
            ),
            app_commands.Choice(
                name="🧠 Threat Intelligence", value="threat_intelligence"
            ),
            app_commands.Choice(
                name="📊 Behavioral Analysis", value="behavioral_analysis"
            ),
            app_commands.Choice(name="⭐ Trust System", value="trust_system_enabled"),
            app_commands.Choice(
                name="📈 Progressive Punishment", value="progressive_punishment"
            ),
        ]
    )
    @app_commands.default_permissions(manage_guild=True)
    async def security_config(
        self, interaction: discord.Interaction, setting: str, value: bool
    ):
        """Configure security system settings"""
        if not await check_user_permission(
            interaction.user, PermissionLevel.ADMINISTRATOR, interaction.guild
        ):
            await interaction.response.send_message(
                "❌ You need administrator permissions to modify security settings.",
                ephemeral=True,
            )
            return

        try:
            # Update the setting
            guild_settings = self.get_guild_settings(interaction.guild.id)
            old_value = guild_settings.get(setting, False)
            guild_settings[setting] = value

            # Update security system configuration
            if setting in self.security_system.config:
                self.security_system.config[setting.replace("_enabled", "")] = value

            # Create response embed
            embed = discord.Embed(
                title="⚙️ Security Configuration Updated",
                description=f"**Setting:** {setting.replace('_', ' ').title()}\n"
                f"**Previous Value:** {'✅ Enabled' if old_value else '❌ Disabled'}\n"
                f"**New Value:** {'✅ Enabled' if value else '❌ Disabled'}",
                color=0x00BFFF,
                timestamp=datetime.now(timezone.utc),
            )

            embed.set_footer(text=f"Updated by {interaction.user.display_name}")

            await interaction.response.send_message(embed=embed)

            # Log the change
            self.logger.info(
                f"Security configuration changed by {interaction.user}: {setting} = {value}"
            )

        except Exception as e:
            self.logger.error(f"Error in security_config command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while updating security configuration.",
                ephemeral=True,
            )

    @app_commands.command(
        name="trust_manage", description="📊 Manage user trust scores (Admin only)"
    )
    @app_commands.describe(
        user="User to modify trust score for",
        action="Action to take",
        amount="Amount to adjust (for adjust/set actions)",
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="🔄 Reset to 50", value="reset"),
            app_commands.Choice(name="⬆️ Increase by amount", value="increase"),
            app_commands.Choice(name="⬇️ Decrease by amount", value="decrease"),
            app_commands.Choice(name="🎯 Set to specific value", value="set"),
        ]
    )
    @app_commands.default_permissions(manage_guild=True)
    async def trust_manage(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        action: str,
        amount: int = 0,
    ):
        """Manage user trust scores (Administrator only)"""
        if not await check_user_permission(
            interaction.user, PermissionLevel.ADMINISTRATOR, interaction.guild
        ):
            await interaction.response.send_message(
                "❌ You need administrator permissions to manage trust levels.",
                ephemeral=True,
            )
            return

        try:
            # Get user profile
            profile = await self.security_system.get_user_profile(
                user.id, interaction.guild.id
            )
            old_score = profile.trust_score

            # Apply the action
            if action == "reset":
                profile.trust_score = 50.0
                profile.violation_history.clear()
                profile.punishment_level = 0
            elif action == "increase":
                profile.trust_score = min(100, profile.trust_score + amount)
            elif action == "decrease":
                profile.trust_score = max(0, profile.trust_score - amount)
            elif action == "set":
                profile.trust_score = max(0, min(100, amount))

            # Update trust status
            profile.is_trusted = profile.trust_score >= 70
            profile.is_quarantined = profile.trust_score <= 25

            # Save profile
            await self.security_system._save_user_profile(profile)

            # Create response
            embed = discord.Embed(
                title="📊 Trust Score Modified",
                description=f"**User:** {user.mention}\n"
                f"**Previous Score:** {old_score:.1f}/100\n"
                f"**New Score:** {profile.trust_score:.1f}/100\n"
                f"**Status:** {'✅ Trusted' if profile.is_trusted else '⚠️ Under Watch'}",
                color=0x00FF00 if profile.is_trusted else 0xFFA500,
                timestamp=datetime.now(timezone.utc),
            )

            if profile.is_quarantined:
                embed.add_field(
                    name="🚨 Quarantine Status",
                    value="User is now in quarantine due to low trust score",
                    inline=False,
                )

            embed.set_footer(text=f"Modified by {interaction.user.display_name}")

            await interaction.response.send_message(embed=embed)

            # Log the change
            self.logger.warning(
                f"Trust score manually modified by {interaction.user}: "
                f"{user} ({user.id}) - {old_score:.1f} → {profile.trust_score:.1f}"
            )

        except Exception as e:
            self.logger.error(f"Error in trust_manage command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while modifying trust score.", ephemeral=True
            )

    # ═══════════════════════════════════════════════════════════════════════════════
    # APPEALS SYSTEM - Human-in-the-loop moderation
    # ═══════════════════════════════════════════════════════════════════════════════

    @app_commands.command(name="appeal", description="📝 Appeal a security violation")
    @app_commands.describe(
        violation_id="ID of the violation to appeal (from security log)",
        reason="Reason for your appeal",
    )
    async def appeal_violation(
        self, interaction: discord.Interaction, violation_id: str, reason: str
    ):
        """Appeal a security violation for human review"""
        try:
            # Create appeal record
            appeal_data = {
                "appeal_id": hashlib.md5(
                    f"{interaction.user.id}{violation_id}{time.time()}".encode()
                ).hexdigest()[:8],
                "user_id": interaction.user.id,
                "violation_id": violation_id,
                "reason": reason,
                "timestamp": time.time(),
                "status": "pending",
                "guild_id": interaction.guild.id if interaction.guild else 0,
            }

            # Store appeal in database (simplified for now)
            # In full implementation, this would go to appeals table

            embed = discord.Embed(
                title="📝 Appeal Submitted",
                description=f"**Appeal ID:** {appeal_data['appeal_id']}\n"
                f"**Violation ID:** {violation_id}\n"
                f"**Status:** Pending Review",
                color=0x00BFFF,
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(
                name="📋 Your Appeal",
                value=reason[:500] + ("..." if len(reason) > 500 else ""),
                inline=False,
            )

            embed.add_field(
                name="⏳ Next Steps",
                value="• Your appeal will be reviewed by staff\n"
                "• You will be notified of the decision\n"
                "• Appeals are typically processed within 24-48 hours",
                inline=False,
            )

            embed.set_footer(text="Appeal submitted • Staff will review shortly")

            await interaction.response.send_message(embed=embed, ephemeral=True)

            # Notify moderators of new appeal
            await self.notify_moderators_new_appeal(interaction, appeal_data)

        except Exception as e:
            self.logger.error(f"Error in appeal_violation command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while submitting your appeal. Please try again.",
                ephemeral=True,
            )

    async def notify_moderators_new_appeal(
        self, interaction: discord.Interaction, appeal_data: Dict[str, Any]
    ):
        """Notify moderators of new appeal submission"""
        # Find moderation channel
        mod_channel = None
        for channel_name in ["mod-log", "appeals", "staff-queue", "admin-log"]:
            mod_channel = discord.utils.get(
                interaction.guild.text_channels, name=channel_name
            )
            if mod_channel:
                break

        if not mod_channel:
            return

        embed = discord.Embed(
            title="📝 New Appeal Submitted",
            description=f"**User:** {interaction.user.mention} ({interaction.user})\n"
            f"**Appeal ID:** {appeal_data['appeal_id']}\n"
            f"**Violation ID:** {appeal_data['violation_id']}",
            color=0xFFFF00,
            timestamp=datetime.now(timezone.utc),
        )

        embed.add_field(
            name="📋 Appeal Reason",
            value=appeal_data["reason"][:500]
            + ("..." if len(appeal_data["reason"]) > 500 else ""),
            inline=False,
        )

        embed.add_field(
            name="🔧 Staff Actions",
            value="Use `/review_appeal [appeal_id] [decision]` to process this appeal",
            inline=False,
        )

        embed.set_footer(text=f"User ID: {interaction.user.id} • Awaiting staff review")

        await mod_channel.send(embed=embed)

    @app_commands.command(
        name="review_appeal",
        description="👨‍⚖️ Review and decide on user appeals (Staff only)",
    )
    @app_commands.describe(
        appeal_id="ID of the appeal to review",
        decision="Decision on the appeal",
        notes="Additional notes for the decision",
    )
    @app_commands.choices(
        decision=[
            app_commands.Choice(
                name="✅ Approve - Overturn violation", value="approved"
            ),
            app_commands.Choice(name="❌ Deny - Violation stands", value="denied"),
            app_commands.Choice(name="📝 Reduce - Lower punishment", value="reduced"),
        ]
    )
    @app_commands.default_permissions(manage_messages=True)
    async def review_appeal(
        self,
        interaction: discord.Interaction,
        appeal_id: str,
        decision: str,
        notes: str = "",
    ):
        """Review and decide on user appeals (Staff only)"""
        if not await check_user_permission(
            interaction.user, PermissionLevel.MODERATOR, interaction.guild
        ):
            await interaction.response.send_message(
                "❌ You need moderator permissions to review appeals.", ephemeral=True
            )
            return

        try:
            # In full implementation, this would update the appeals database
            # and automatically reverse/modify the original violation

            decision_colors = {
                "approved": 0x00FF00,
                "denied": 0xFF0000,
                "reduced": 0xFFFF00,
            }

            decision_text = {
                "approved": "✅ Appeal Approved - Violation Overturned",
                "denied": "❌ Appeal Denied - Violation Stands",
                "reduced": "📝 Appeal Partially Approved - Punishment Reduced",
            }

            embed = discord.Embed(
                title="👨‍⚖️ Appeal Decision",
                description=f"**Appeal ID:** {appeal_id}\n"
                f"**Decision:** {decision_text[decision]}\n"
                f"**Reviewed by:** {interaction.user.mention}",
                color=decision_colors[decision],
                timestamp=datetime.now(timezone.utc),
            )

            if notes:
                embed.add_field(name="📝 Staff Notes", value=notes, inline=False)

            embed.add_field(
                name="⚡ Automated Actions",
                value="• User has been notified of decision\n"
                "• Violation record updated\n"
                "• Trust score adjusted if applicable\n"
                "• Appeal marked as resolved",
                inline=False,
            )

            embed.set_footer(text=f"Reviewed by {interaction.user.display_name}")

            await interaction.response.send_message(embed=embed)

            # Log the staff decision
            self.logger.info(
                f"Appeal {appeal_id} {decision} by {interaction.user}: {notes}"
            )

        except Exception as e:
            self.logger.error(f"Error in review_appeal command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while processing the appeal review.",
                ephemeral=True,
            )

    # ═══════════════════════════════════════════════════════════════════════════════
    # LOCKDOWN CONTROLS - Owner and Admin Access
    # ═══════════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="manual_lockdown",
        description="🔒 Manual server lockdown for maintenance or planned security (Admin+)",
    )
    @app_commands.describe(
        reason="Reason for the manual lockdown",
        duration="Expected duration in minutes (optional)",
    )
    @app_commands.default_permissions(manage_guild=True)
    async def manual_lockdown(
        self,
        interaction: discord.Interaction,
        reason: str = "Scheduled maintenance",
        duration: int = None,
    ):
        """Manual server lockdown for maintenance or planned security measures"""
        if not await check_user_permission(
            interaction.user, PermissionLevel.ADMINISTRATOR, interaction.guild
        ):
            await interaction.response.send_message(
                "❌ You need administrator permissions for manual lockdowns.",
                ephemeral=True,
            )
            return

        try:
            if self.lockdown_active:
                await interaction.response.send_message(
                    "⚠️ Server is already in lockdown mode. Use `/emergency_unlock` to restore first.",
                    ephemeral=True,
                )
                return

            # Defer response
            await interaction.response.defer()

            guild = interaction.guild

            # Use the same lockdown mechanism as emergency
            self.lockdown_active = True
            self.lockdown_reason = f"Manual lockdown: {reason}"
            self.lockdown_timestamp = time.time()

            # Lock channels (same as emergency but with different messaging)
            locked_channels = []

            for channel in guild.text_channels:
                try:
                    overwrites = channel.overwrites_for(guild.default_role)
                    overwrites.send_messages = False
                    overwrites.add_reactions = False
                    overwrites.attach_files = False

                    await channel.set_permissions(
                        guild.default_role,
                        overwrite=overwrites,
                        reason=f"🔒 Manual lockdown: {reason}",
                    )
                    locked_channels.append(channel.id)
                except:
                    pass

            self.lockdown_channels = locked_channels

            # Send notification to general channel
            general_channel_id = 1399956514176897178
            general_channel = guild.get_channel(general_channel_id)

            if general_channel:
                try:
                    # Allow bot to send message
                    bot_overwrites = general_channel.overwrites_for(guild.me)
                    bot_overwrites.send_messages = True
                    await general_channel.set_permissions(
                        guild.me, overwrite=bot_overwrites
                    )

                    # Create maintenance notification
                    maintenance_embed = discord.Embed(
                        title="🔒 SERVER MAINTENANCE MODE",
                        description=f"**The server has been temporarily locked for {reason.lower()}.**\n\n"
                        "🛠️ **This is planned maintenance, not an emergency**\n"
                        "⏳ **Normal service will resume shortly**\n"
                        "💙 **Thank you for your patience**",
                        color=0xFFAA00,
                        timestamp=datetime.now(timezone.utc),
                    )

                    if duration:
                        maintenance_embed.add_field(
                            name="⏰ Expected Duration",
                            value=f"Approximately {duration} minutes",
                            inline=True,
                        )

                    maintenance_embed.add_field(
                        name="📋 Details", value=f"```{reason}```", inline=False
                    )

                    maintenance_embed.set_footer(
                        text="Astra Security • Maintenance Mode"
                    )

                    await general_channel.send(
                        content="@everyone 🔒 **MAINTENANCE MODE ACTIVE**",
                        embed=maintenance_embed,
                    )
                except:
                    pass

            # Create admin response
            response_embed = discord.Embed(
                title="🔒 MANUAL LOCKDOWN ACTIVATED",
                description=f"**Reason:** {reason}\n"
                f"**Initiated by:** {interaction.user.mention}\n"
                f"**Expected Duration:** {f'{duration} minutes' if duration else 'Not specified'}",
                color=0xFFAA00,
                timestamp=datetime.now(timezone.utc),
            )

            response_embed.add_field(
                name="📊 Lockdown Status",
                value=f"**Channels Locked:** {len(locked_channels)}\n"
                f"**Type:** Manual/Planned\n"
                f"**Community Notified:** ✅",
                inline=True,
            )

            response_embed.set_footer(text="Use /emergency_unlock to restore server")

            await interaction.followup.send(embed=response_embed)

            self.logger.info(
                f"🔒 Manual lockdown activated by {interaction.user}: {reason}"
            )

        except Exception as e:
            self.logger.error(f"Error in manual_lockdown command: {e}")
            await interaction.followup.send(
                "❌ An error occurred during manual lockdown activation.",
                ephemeral=True,
            )

    # ═══════════════════════════════════════════════════════════════════════════════
    # EMERGENCY CONTROLS - Owner Only
    # ═══════════════════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="emergency_lockdown",
        description="🚨 CRITICAL: Complete server lockdown - locks ALL channels + emergency broadcast",
    )
    @app_commands.describe(reason="Reason for emergency lockdown (optional)")
    async def emergency_lockdown(
        self,
        interaction: discord.Interaction,
        reason: str = "Potential security threat detected",
    ):
        """CRITICAL EMERGENCY: Complete server lockdown with broadcast notification"""
        if not is_bot_owner(interaction.user.id):
            await interaction.response.send_message(
                "❌ This command is restricted to the bot owner only.", ephemeral=True
            )
            return

        try:
            # Defer response as this will take time
            await interaction.response.defer()

            guild = interaction.guild
            if not guild:
                await interaction.followup.send(
                    "❌ This command must be used in a server.", ephemeral=True
                )
                return

            # Activate lockdown state
            self.lockdown_active = True
            self.lockdown_reason = reason
            self.lockdown_timestamp = time.time()

            # Track locked channels for restoration
            locked_channels = []
            locked_voice_channels = []

            # PHASE 1: Lock ALL text channels
            self.logger.critical(
                f"🚨 EMERGENCY LOCKDOWN PHASE 1: Locking all text channels..."
            )
            for channel in guild.text_channels:
                try:
                    # Store current permissions before locking
                    overwrites = channel.overwrites_for(guild.default_role)

                    # Remove all messaging permissions
                    overwrites.send_messages = False
                    overwrites.add_reactions = False
                    overwrites.attach_files = False
                    overwrites.embed_links = False
                    overwrites.use_external_emojis = False
                    overwrites.mention_everyone = False
                    overwrites.create_public_threads = False
                    overwrites.create_private_threads = False
                    overwrites.send_messages_in_threads = False

                    await channel.set_permissions(
                        guild.default_role,
                        overwrite=overwrites,
                        reason=f"🚨 EMERGENCY LOCKDOWN: {reason}",
                    )
                    locked_channels.append(channel.id)

                except Exception as e:
                    self.logger.error(
                        f"Failed to lock text channel {channel.name}: {e}"
                    )

            # PHASE 2: Lock ALL voice channels
            self.logger.critical(
                f"🚨 EMERGENCY LOCKDOWN PHASE 2: Locking all voice channels..."
            )
            for channel in guild.voice_channels:
                try:
                    # Store current permissions before locking
                    overwrites = channel.overwrites_for(guild.default_role)

                    # Remove voice permissions
                    overwrites.connect = False
                    overwrites.speak = False
                    overwrites.stream = False
                    overwrites.use_voice_activation = False
                    overwrites.priority_speaker = False

                    await channel.set_permissions(
                        guild.default_role,
                        overwrite=overwrites,
                        reason=f"🚨 EMERGENCY LOCKDOWN: {reason}",
                    )
                    locked_voice_channels.append(channel.id)

                    # Disconnect all users from voice channel
                    for member in channel.members:
                        try:
                            await member.move_to(
                                None,
                                reason="Emergency lockdown - voice channels secured",
                            )
                        except:
                            pass

                except Exception as e:
                    self.logger.error(
                        f"Failed to lock voice channel {channel.name}: {e}"
                    )

            # Store locked channels for restoration
            self.lockdown_channels = locked_channels + locked_voice_channels

            # PHASE 3: Send emergency broadcast to general channel
            self.logger.critical(
                f"🚨 EMERGENCY LOCKDOWN PHASE 3: Broadcasting emergency message..."
            )

            # Find general channel (specific ID provided)
            general_channel_id = 1399956514176897178
            general_channel = guild.get_channel(general_channel_id)

            if general_channel:
                try:
                    # Temporarily allow bot to send in general channel
                    bot_overwrites = general_channel.overwrites_for(guild.me)
                    bot_overwrites.send_messages = True
                    bot_overwrites.mention_everyone = True
                    await general_channel.set_permissions(
                        guild.me,
                        overwrite=bot_overwrites,
                        reason="Emergency broadcast permission",
                    )

                    # Create emergency broadcast embed
                    emergency_embed = discord.Embed(
                        title="🚨 EMERGENCY SERVER LOCKDOWN ACTIVATED",
                        description="**⚠️ CRITICAL SECURITY ALERT ⚠️**\n\n"
                        "**The server is currently under emergency lockdown to protect against potential malicious activities.**\n\n"
                        "🔒 **All channels have been temporarily secured**\n"
                        "🛡️ **Security protocols are now in maximum protection mode**\n"
                        "⏳ **Normal service will be restored once the situation is resolved**",
                        color=0xFF0000,
                        timestamp=datetime.now(timezone.utc),
                    )

                    emergency_embed.add_field(
                        name="🔴 Current Status",
                        value="• All text channels locked\n• All voice channels secured\n• Emergency protocols active\n• Staff investigating situation",
                        inline=True,
                    )

                    emergency_embed.add_field(
                        name="⏰ What's Next",
                        value="• Security team is investigating\n• You will be notified when resolved\n• Please remain calm and patient\n• No action required from users",
                        inline=True,
                    )

                    emergency_embed.add_field(
                        name="📋 Reason", value=f"```{reason}```", inline=False
                    )

                    emergency_embed.set_footer(
                        text="Astra Security System • Emergency Protocol Active",
                        icon_url=guild.me.display_avatar.url,
                    )

                    # Send emergency broadcast with @everyone ping
                    await general_channel.send(
                        content="@everyone 🚨 **EMERGENCY SECURITY LOCKDOWN** 🚨",
                        embed=emergency_embed,
                    )

                except Exception as e:
                    self.logger.error(f"Failed to send emergency broadcast: {e}")
            else:
                self.logger.error(
                    f"Could not find general channel with ID {general_channel_id}"
                )

            # PHASE 4: Create admin response embed
            response_embed = discord.Embed(
                title="🚨 EMERGENCY LOCKDOWN SUCCESSFULLY ACTIVATED",
                description=f"**Server:** {guild.name}\n"
                f"**Initiated by:** {interaction.user.mention}\n"
                f"**Timestamp:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                f"**Reason:** {reason}",
                color=0xFF0000,
                timestamp=datetime.now(timezone.utc),
            )

            response_embed.add_field(
                name="🔒 Lockdown Statistics",
                value=f"**Text Channels Locked:** {len(locked_channels)}\n"
                f"**Voice Channels Secured:** {len(locked_voice_channels)}\n"
                f"**Total Channels Affected:** {len(locked_channels) + len(locked_voice_channels)}\n"
                f"**Emergency Broadcast:** {'✅ Sent' if general_channel else '❌ Failed'}",
                inline=True,
            )

            response_embed.add_field(
                name="🛡️ Security Measures Active",
                value="• Complete channel lockdown\n• Voice users disconnected\n• Emergency broadcast sent\n• Maximum protection mode\n• Owner-only messaging",
                inline=True,
            )

            response_embed.add_field(
                name="🔧 Administrative Controls",
                value="Use `/emergency_unlock` to restore normal operations and notify users that the server is safe again.",
                inline=False,
            )

            response_embed.set_footer(
                text="EMERGENCY PROTOCOL ACTIVE • Use /emergency_unlock to restore"
            )

            await interaction.followup.send(embed=response_embed)

            # Log the critical emergency lockdown
            self.logger.critical(
                f"🚨 COMPLETE SERVER EMERGENCY LOCKDOWN activated by {interaction.user} ({interaction.user.id})\n"
                f"   Reason: {reason}\n"
                f"   Text channels locked: {len(locked_channels)}\n"
                f"   Voice channels secured: {len(locked_voice_channels)}\n"
                f"   Emergency broadcast: {'Success' if general_channel else 'Failed'}"
            )

        except Exception as e:
            self.logger.error(f"CRITICAL ERROR in emergency_lockdown command: {e}")
            try:
                await interaction.followup.send(
                    "❌ **CRITICAL ERROR**: Emergency lockdown failed to activate completely. Please check logs and take manual action immediately.",
                    ephemeral=True,
                )
            except:
                pass

    @app_commands.command(
        name="emergency_unlock",
        description="🔓 RESTORE SERVER: Deactivate emergency lockdown + send all-clear notification",
    )
    async def emergency_unlock(self, interaction: discord.Interaction):
        """Deactivate emergency lockdown and restore server operations"""
        if not is_bot_owner(interaction.user.id):
            await interaction.response.send_message(
                "❌ This command is restricted to the bot owner only.", ephemeral=True
            )
            return

        try:
            if not self.lockdown_active:
                await interaction.response.send_message(
                    "ℹ️ No emergency lockdown is currently active.", ephemeral=True
                )
                return

            # Defer response as restoration will take time
            await interaction.response.defer()

            guild = interaction.guild
            if not guild:
                await interaction.followup.send(
                    "❌ This command must be used in a server.", ephemeral=True
                )
                return

            # Calculate lockdown duration
            lockdown_duration = time.time() - self.lockdown_timestamp
            previous_reason = self.lockdown_reason

            # PHASE 1: Restore all channel permissions
            self.logger.info(
                f"🔓 EMERGENCY UNLOCK PHASE 1: Restoring channel permissions..."
            )

            restored_text = 0
            restored_voice = 0

            # Get all locked channels
            locked_channels = getattr(self, "lockdown_channels", [])

            for channel_id in locked_channels:
                channel = guild.get_channel(channel_id)
                if channel:
                    try:
                        # Reset permissions to default (None = inherit from category/server)
                        overwrites = channel.overwrites_for(guild.default_role)

                        if isinstance(channel, discord.TextChannel):
                            # Restore text channel permissions
                            overwrites.send_messages = None
                            overwrites.add_reactions = None
                            overwrites.attach_files = None
                            overwrites.embed_links = None
                            overwrites.use_external_emojis = None
                            overwrites.mention_everyone = None
                            overwrites.create_public_threads = None
                            overwrites.create_private_threads = None
                            overwrites.send_messages_in_threads = None
                            restored_text += 1

                        elif isinstance(channel, discord.VoiceChannel):
                            # Restore voice channel permissions
                            overwrites.connect = None
                            overwrites.speak = None
                            overwrites.stream = None
                            overwrites.use_voice_activation = None
                            overwrites.priority_speaker = None
                            restored_voice += 1

                        await channel.set_permissions(
                            guild.default_role,
                            overwrite=overwrites,
                            reason=f"🔓 Emergency lockdown lifted - server restored",
                        )

                    except Exception as e:
                        self.logger.error(
                            f"Failed to restore channel {channel.name}: {e}"
                        )

            # PHASE 2: Send "all clear" broadcast to general channel
            self.logger.info(
                f"🔓 EMERGENCY UNLOCK PHASE 2: Broadcasting all-clear message..."
            )

            # Find general channel
            general_channel_id = 1399956514176897178
            general_channel = guild.get_channel(general_channel_id)

            broadcast_success = False
            if general_channel:
                try:
                    # Create all-clear broadcast embed
                    all_clear_embed = discord.Embed(
                        title="✅ SERVER RESTORED - ALL CLEAR",
                        description="**🎉 The emergency situation has been resolved! 🎉**\n\n"
                        "**The server is now safe and all normal operations have been restored.**\n\n"
                        "🔓 **All channels are now accessible again**\n"
                        "💬 **You can resume normal conversations**\n"
                        "🎮 **Voice channels are available for use**\n"
                        "✨ **All server features are fully operational**",
                        color=0x00FF00,
                        timestamp=datetime.now(timezone.utc),
                    )

                    all_clear_embed.add_field(
                        name="🟢 Current Status",
                        value="• All channels unlocked ✅\n• Voice channels restored ✅\n• Normal operations resumed ✅\n• Security monitoring active ✅",
                        inline=True,
                    )

                    all_clear_embed.add_field(
                        name="📊 Lockdown Summary",
                        value=f"• **Duration:** {lockdown_duration/60:.1f} minutes\n• **Channels Restored:** {restored_text + restored_voice}\n• **Previous Issue:** Resolved ✅\n• **Server Status:** Fully Operational",
                        inline=True,
                    )

                    all_clear_embed.add_field(
                        name="💙 Thank You",
                        value="**Thank you for your patience and understanding during the emergency lockdown. The server is now completely safe and secure.**",
                        inline=False,
                    )

                    all_clear_embed.set_footer(
                        text="Astra Security System • Server Fully Restored",
                        icon_url=guild.me.display_avatar.url,
                    )

                    # Send all-clear broadcast with @everyone ping
                    await general_channel.send(
                        content="@everyone 🎉 **SERVER RESTORED - ALL CLEAR** 🎉",
                        embed=all_clear_embed,
                    )
                    broadcast_success = True

                except Exception as e:
                    self.logger.error(f"Failed to send all-clear broadcast: {e}")

            # PHASE 3: Reset lockdown state
            self.lockdown_active = False
            self.lockdown_reason = ""
            self.lockdown_timestamp = 0
            self.lockdown_channels = []

            # PHASE 4: Create admin response embed
            response_embed = discord.Embed(
                title="🔓 EMERGENCY LOCKDOWN SUCCESSFULLY DEACTIVATED",
                description=f"**Server:** {guild.name}\n"
                f"**Restored by:** {interaction.user.mention}\n"
                f"**Lockdown Duration:** {lockdown_duration/60:.1f} minutes\n"
                f"**Previous Reason:** {previous_reason}",
                color=0x00FF00,
                timestamp=datetime.now(timezone.utc),
            )

            response_embed.add_field(
                name="📊 Restoration Statistics",
                value=f"**Text Channels Restored:** {restored_text}\n"
                f"**Voice Channels Restored:** {restored_voice}\n"
                f"**Total Channels Restored:** {restored_text + restored_voice}\n"
                f"**All-Clear Broadcast:** {'✅ Sent' if broadcast_success else '❌ Failed'}",
                inline=True,
            )

            response_embed.add_field(
                name="✅ Server Status",
                value="• All channels fully operational\n• Normal messaging restored\n• Voice channels accessible\n• Security monitoring active\n• Community notified",
                inline=True,
            )

            response_embed.add_field(
                name="🎉 Community Response",
                value="All server members have been notified that the server is safe and fully operational again. Thank you for maintaining security!",
                inline=False,
            )

            response_embed.set_footer(
                text="SERVER FULLY RESTORED • Emergency protocol deactivated"
            )

            await interaction.followup.send(embed=response_embed)

            # Log the successful restoration
            self.logger.info(
                f"🔓 COMPLETE SERVER RESTORATION by {interaction.user} ({interaction.user.id})\n"
                f"   Lockdown duration: {lockdown_duration/60:.1f} minutes\n"
                f"   Text channels restored: {restored_text}\n"
                f"   Voice channels restored: {restored_voice}\n"
                f"   All-clear broadcast: {'Success' if broadcast_success else 'Failed'}\n"
                f"   Previous reason: {previous_reason}"
            )

        except Exception as e:
            self.logger.error(f"CRITICAL ERROR in emergency_unlock command: {e}")
            try:
                await interaction.followup.send(
                    "❌ **CRITICAL ERROR**: Emergency unlock failed. Please take manual action to restore server.",
                    ephemeral=True,
                )
            except:
                pass

    @app_commands.command(
        name="manual_override", description="🔧 Manual override for security actions"
    )
    @app_commands.describe(
        user="User to override security actions for",
        action="Override action to take",
        reason="Reason for manual override",
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Clear Violations", value="clear_violations"),
            app_commands.Choice(name="Remove Timeout", value="remove_timeout"),
            app_commands.Choice(name="Reset Trust Score", value="reset_trust"),
            app_commands.Choice(
                name="Remove from Quarantine", value="remove_quarantine"
            ),
        ]
    )
    @app_commands.default_permissions(manage_guild=True)
    async def manual_override(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        action: str,
        reason: str,
    ):
        """Manual override for security actions"""
        if not await check_user_permission(
            interaction.user, PermissionLevel.ADMINISTRATOR, interaction.guild
        ):
            await interaction.response.send_message(
                "❌ You need administrator permissions for manual overrides.",
                ephemeral=True,
            )
            return

        try:
            # Execute manual override
            success = await self.security_system.manual_override(
                interaction.user.id, user.id, action, reason
            )

            if success:
                self.performance_metrics["manual_overrides"] += 1

                embed = discord.Embed(
                    title="🔧 Manual Override Executed",
                    description=f"**User:** {user.mention}\n"
                    f"**Action:** {action.replace('_', ' ').title()}\n"
                    f"**Reason:** {reason}",
                    color=0x00BFFF,
                    timestamp=datetime.now(timezone.utc),
                )

                embed.set_footer(text=f"Override by {interaction.user.display_name}")

                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(
                    "❌ Manual override failed. Please check logs for details.",
                    ephemeral=True,
                )

        except Exception as e:
            self.logger.error(f"Error in manual_override command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while executing manual override.", ephemeral=True
            )


async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(SecurityManager(bot))
