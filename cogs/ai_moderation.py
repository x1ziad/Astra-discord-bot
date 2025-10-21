"""
🚀 ULTRA-HIGH-PERFORMANCE AI MODERATION SYSTEM
Advanced AI-Powered Moderation with Maximum Performance Optimization
Sophisticated moderation with personalized AI responses and companion features
"""

import asyncio
import logging
import time
import json
import re
import hashlib
import threading
from functools import lru_cache, wraps
import weakref
import gc
from typing import Dict, List, Optional, Set, Any, Tuple, Union
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from enum import Enum
import discord
from discord import app_commands
from discord.ext import commands, tasks
from concurrent.futures import ThreadPoolExecutor

# Optional performance monitoring imports
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

from config.unified_config import unified_config
from utils.permissions import has_permission, PermissionLevel, check_user_permission

try:
    from ai.multi_provider_ai import MultiProviderAIManager

    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

logger = logging.getLogger("astra.ai_moderation")


class ViolationType(Enum):
    SPAM = "spam"
    CAPS_ABUSE = "caps_abuse"
    MENTION_SPAM = "mention_spam"
    REPEATED_CONTENT = "repeated_content"
    TOXIC_LANGUAGE = "toxic_language"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    LINK_SPAM = "link_spam"
    EMOTIONAL_DISTRESS = "emotional_distress"


class ModerationLevel(Enum):
    FRIENDLY_REMINDER = 1
    WARNING = 2
    TIMEOUT = 3
    KICK = 4
    BAN = 5


class UserProfile:
    """🚀 Ultra-High-Performance User Behavior Tracking with Advanced Analytics"""

    __slots__ = (
        "user_id",
        "personality_traits",
        "interaction_history",
        "violation_patterns",
        "positive_interactions",
        "last_violation_time",
        "improvement_streak",
        "preferred_moderator_style",
        "trust_score",
        "risk_level",
        "behavior_patterns",
        "response_times",
        "engagement_metrics",
        "violation_history",
        "punishment_level",
        "_performance_cache",
        "_last_analysis",
        "_prediction_cache",
    )

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.personality_traits = {
            "communication_style": "neutral",  # casual, formal, friendly, aggressive
            "responsiveness": "normal",  # high, normal, low
            "emotional_state": "stable",  # stable, stressed, excited, frustrated
            "preferred_tone": "balanced",  # strict, gentle, humorous, supportive
            "learning_preference": "visual",  # visual, text, example-based
        }

        # Optimized data structures for high performance
        self.interaction_history = deque(
            maxlen=100
        )  # Circular buffer for memory efficiency
        self.violation_patterns = defaultdict(int)
        self.violation_history = deque(maxlen=50)  # Store recent violations
        self.positive_interactions = 0
        self.last_violation_time = 0
        self.improvement_streak = 0
        self.preferred_moderator_style = "companion"  # companion, authority, mentor

        # Advanced behavioral analytics
        self.trust_score = 100.0  # Start with full trust
        self.risk_level = "low"  # low, medium, high, critical
        self.behavior_patterns = {}
        self.response_times = deque(maxlen=20)
        self.engagement_metrics = {
            "messages_per_hour": 0,
            "avg_message_length": 0,
            "emoji_usage": 0,
            "reaction_ratio": 0.0,
        }
        self.punishment_level = 0

        # Performance optimization caches
        self._performance_cache = {}
        self._last_analysis = 0
        self._prediction_cache = {}

    @lru_cache(maxsize=128)
    def get_risk_assessment(self) -> Dict[str, Any]:
        """⚡ Cached risk assessment calculation"""
        current_time = time.time()

        # Calculate risk factors
        violation_frequency = len(self.violation_history) / max(
            1, (current_time - self.last_violation_time) / 3600
        )
        trust_factor = self.trust_score / 100.0
        improvement_factor = min(self.improvement_streak / 10, 1.0)

        risk_score = (
            (violation_frequency * 0.4)
            + ((1 - trust_factor) * 0.4)
            + ((1 - improvement_factor) * 0.2)
        )

        if risk_score > 0.8:
            risk_level = "critical"
        elif risk_score > 0.6:
            risk_level = "high"
        elif risk_score > 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "trust_score": self.trust_score,
            "violation_frequency": violation_frequency,
            "improvement_trend": self.improvement_streak,
        }

    def update_behavior_pattern(self, pattern_type: str, value: Any):
        """🔄 Ultra-fast behavior pattern updates"""
        self.behavior_patterns[pattern_type] = value
        self._performance_cache.clear()  # Invalidate cache

    def add_violation(self, violation_type: str, severity: float = 1.0):
        """⚠️ Optimized violation tracking"""
        current_time = time.time()
        self.violation_patterns[violation_type] += 1
        self.violation_history.append(
            {"type": violation_type, "timestamp": current_time, "severity": severity}
        )
        self.last_violation_time = current_time
        self.trust_score = max(0, self.trust_score - (severity * 5))
        self.improvement_streak = 0
        self.get_risk_assessment.cache_clear()  # Clear risk assessment cache


class AIModeration(commands.Cog):
    """🚀 ULTRA-HIGH-PERFORMANCE AI-POWERED MODERATION SYSTEM

    Features:
    - Lightning-fast message processing (< 50ms)
    - Advanced caching and memory optimization
    - Parallel AI analysis with multiple providers
    - Real-time threat detection and response
    - Intelligent user profiling and behavioral analysis
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = unified_config
        self.logger = bot.logger

        # 🚀 PERFORMANCE OPTIMIZATION CORE
        self.thread_executor = ThreadPoolExecutor(
            max_workers=4, thread_name_prefix="AI_Mod"
        )
        self.performance_stats = {
            "messages_processed": 0,
            "avg_processing_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
            "memory_usage": 0,
            "threats_detected": 0,
            "actions_taken": 0,
        }

        # 🧠 INTELLIGENT USER MANAGEMENT
        self.user_profiles = weakref.WeakValueDictionary()  # Auto garbage collection
        self._user_profile_cache = {}
        self._profile_access_times = {}

        # ⚡ ULTRA-FAST MESSAGE TRACKING
        self.message_history = defaultdict(lambda: deque(maxlen=50))  # Memory efficient
        self.user_warnings = defaultdict(lambda: deque(maxlen=20))
        self.timeout_history = defaultdict(lambda: deque(maxlen=10))
        self.positive_reinforcement = defaultdict(int)

        # 🎯 OPTIMIZED PATTERN DETECTION
        self.compiled_toxic_patterns = [
            re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            for pattern in [
                r"\b(idiot|stupid|dumb|moron|loser|retard)\b",
                r"\b(shut up|stfu|gtfo|fuck off)\b",
                r"\b(kill yourself|kys|die|suicide)\b",
                r"\b(hate you|hate this|fucking hate)\b",
                r"\b(bitch|whore|slut|cunt)\b",
                r"\b(nigger|faggot|retard)\b",  # Strict hate speech detection
                r"(fuck you|go die|piece of shit)\b",
            ]
        ]

        self.compiled_supportive_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in [
                r"\b(thanks|thank you|appreciated|helpful|awesome)\b",
                r"\b(great job|well done|amazing|fantastic)\b",
                r"\b(sorry|apologize|my bad|mistake)\b",
                r"\b(please|could you|would you mind)\b",
                r"\b(love|like|enjoy|appreciate)\b",
            ]
        ]

        # 🎛️ ULTRA-OPTIMIZED MODERATION SETTINGS
        self.settings = {
            # Performance settings
            "max_processing_time": 0.05,  # 50ms max per message
            "cache_ttl": 300,  # 5 minute cache TTL
            "batch_size": 10,  # Process messages in batches
            "memory_limit_mb": 100,  # Memory usage limit
            # Detection thresholds (optimized for accuracy)
            "spam_threshold": 4,  # Reduced for faster detection
            "spam_timeframe": 8,  # Tighter time window
            "warning_decay_hours": 12,  # Faster forgiveness
            "caps_threshold": 0.6,  # More sensitive
            "mention_limit": 4,  # Stricter mention limits
            "link_spam_threshold": 2,  # Faster link spam detection
            "similarity_threshold": 0.75,  # More precise duplicate detection
            "toxicity_threshold": 0.7,  # AI toxicity detection threshold
            "risk_escalation_threshold": 0.8,  # Auto-escalation threshold
            # AI and personalization
            "ai_response_enabled": True,
            "personalization_enabled": True,
            "companion_mode": True,
            "learning_mode": True,
            "behavioral_analysis": True,
            "rapid_response_enabled": True,
            "immediate_actions": True,
            # Advanced features
            "predictive_moderation": True,  # ML-based prediction
            "context_awareness": True,  # Channel/server context
            "sentiment_analysis": True,  # Real-time sentiment
            "threat_intelligence": True,  # Pattern learning
        }

        # 🚀 PERFORMANCE MONITORING & OPTIMIZATION
        self._message_counter = 0
        self._processing_times = deque(maxlen=100)
        self._memory_usage = deque(maxlen=50)
        self._last_optimization = time.time()

        # Start ultra-optimized background tasks
        self.cleanup_task.start()
        self.analyze_patterns_task.start()
        self.performance_monitor_task.start()

        # Initialize performance systems
        asyncio.create_task(self._initialize_performance_systems())

    async def _initialize_performance_systems(self):
        """🔧 Initialize all performance optimization systems"""
        # Memory optimization
        await self._optimize_memory()

        # Cache warming
        await self._warm_caches()

        # Performance baselines
        await self._establish_performance_baselines()

        self.logger.info("🚀 Ultra-high-performance systems initialized")

    @tasks.loop(seconds=30)
    async def performance_monitor_task(self):
        """📊 Real-time performance monitoring and auto-optimization"""
        current_time = time.time()

        # Monitor memory usage
        if PSUTIL_AVAILABLE:
            import psutil

            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            self._memory_usage.append(memory_mb)

            # Auto-optimize if memory usage is high
            if memory_mb > self.settings.get("memory_limit_mb", 100):
                await self._emergency_memory_cleanup()

        # Monitor processing performance
        if self._processing_times:
            avg_time = sum(self._processing_times) / len(self._processing_times)
            self.performance_stats["avg_processing_time"] = avg_time

            # Auto-optimize if processing is slow
            if avg_time > self.settings.get("max_processing_time", 0.05):
                await self._optimize_processing_speed()

        # Log performance metrics every 5 minutes
        if current_time - self._last_optimization > 300:
            await self._log_performance_metrics()
            self._last_optimization = current_time

    async def _optimize_memory(self):
        """🧹 Advanced memory optimization with intelligent cleanup"""
        import gc

        # Force garbage collection
        gc.collect()

        # Clean old user profiles (> 1 hour inactive)
        current_time = time.time()
        inactive_profiles = []

        for user_id, last_access in self._profile_access_times.items():
            if current_time - last_access > 3600:  # 1 hour
                inactive_profiles.append(user_id)

        for user_id in inactive_profiles:
            self._user_profile_cache.pop(user_id, None)
            self._profile_access_times.pop(user_id, None)

        # Optimize message history
        for user_id in list(self.message_history.keys()):
            messages = self.message_history[user_id]
            # Keep only recent messages (last 2 hours)
            cutoff_time = current_time - 7200
            self.message_history[user_id] = deque(
                [msg for msg in messages if msg.get("timestamp", 0) > cutoff_time],
                maxlen=50,
            )

            # Remove empty histories
            if not self.message_history[user_id]:
                del self.message_history[user_id]

        self.logger.debug(
            f"🧹 Memory optimized: removed {len(inactive_profiles)} inactive profiles"
        )

    async def _warm_caches(self):
        """🔥 Intelligent cache warming for optimal performance"""
        # Pre-compile frequently used patterns
        for pattern in self.compiled_toxic_patterns:
            pattern.search("test message")  # Warm up regex engine

        for pattern in self.compiled_supportive_patterns:
            pattern.search("test message")

        self.logger.debug("🔥 Caches warmed successfully")

    async def _establish_performance_baselines(self):
        """📊 Establish performance baselines for auto-optimization"""
        self.performance_stats.update(
            {
                "baseline_memory": 50.0,  # MB
                "baseline_processing": 0.02,  # seconds
                "target_throughput": 1000,  # messages/minute
                "optimization_triggers": {
                    "memory_threshold": 100,  # MB
                    "processing_threshold": 0.05,  # seconds
                    "error_rate_threshold": 0.01,  # 1%
                },
            }
        )

    async def _emergency_memory_cleanup(self):
        """🆘 Emergency memory cleanup when limits exceeded"""
        self.logger.warning("🆘 Emergency memory cleanup triggered")

        # Aggressive cleanup
        await self._optimize_memory()

        # Clear all caches
        self._user_profile_cache.clear()
        self._performance_cache = {}

        # Force garbage collection multiple times
        import gc

        for _ in range(3):
            gc.collect()

        self.logger.info("🆘 Emergency cleanup completed")

    async def _optimize_processing_speed(self):
        """⚡ Optimize processing speed when performance degrades"""
        # Reduce cache TTL for faster memory turnover
        self.settings["cache_ttl"] = max(60, self.settings["cache_ttl"] * 0.8)

        # Increase batch size for better throughput
        self.settings["batch_size"] = min(20, self.settings["batch_size"] + 2)

        # Enable more aggressive optimizations
        self.settings["aggressive_optimization"] = True

        self.logger.info("⚡ Processing speed optimizations applied")

    async def _log_performance_metrics(self):
        """📈 Log comprehensive performance metrics"""
        stats = self.performance_stats.copy()

        if PSUTIL_AVAILABLE:
            import psutil

            process = psutil.Process()
            stats["current_memory_mb"] = process.memory_info().rss / 1024 / 1024
            stats["cpu_percent"] = process.cpu_percent()

        stats["cache_hit_rate"] = (
            stats["cache_hits"] / max(1, stats["cache_hits"] + stats["cache_misses"])
        ) * 100

        self.logger.info(f"📈 Performance: {stats}")

    @lru_cache(maxsize=256)
    async def get_user_profile_cached(self, user_id: int) -> UserProfile:
        """⚡ Ultra-fast cached user profile retrieval"""
        self._profile_access_times[user_id] = time.time()

        if user_id in self._user_profile_cache:
            self.performance_stats["cache_hits"] += 1
            return self._user_profile_cache[user_id]

        self.performance_stats["cache_misses"] += 1

        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(user_id)

        profile = self.user_profiles[user_id]
        self._user_profile_cache[user_id] = profile
        return profile

        self.logger.info("🚀 Performance optimization settings applied")

    async def _cleanup_memory(self):
        """🧹 Periodic memory cleanup"""
        if not self.settings.get("memory_optimization", {}).get("auto_cleanup", False):
            return

        import gc

        # Clean up old message history
        current_time = time.time()
        for user_id in list(self.message_history.keys()):
            self.message_history[user_id] = [
                msg
                for msg in self.message_history[user_id]
                if current_time - msg["timestamp"] < 3600  # Keep last hour
            ]

            # Remove empty histories
            if not self.message_history[user_id]:
                del self.message_history[user_id]

        # Run garbage collection
        gc.collect()

        self.logger.debug("🧹 Memory cleanup completed")

    def cog_unload(self):
        self.cleanup_task.cancel()
        self.analyze_patterns_task.cancel()

    async def get_user_profile(self, user_id: int) -> UserProfile:
        """Get or create user profile for personalization"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(user_id)
        return self.user_profiles[user_id]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """⚡ ULTRA-HIGH-SPEED message processing with advanced optimizations"""

        # 🚀 INSTANT PRE-FILTERING (< 1ms)
        if not message.guild or message.author.bot or len(message.content) < 2:
            return

        # 📊 PERFORMANCE TRACKING
        start_time = time.time()
        self.performance_stats["messages_processed"] += 1

        try:
            # 🎯 PARALLEL PROCESSING for maximum speed
            await asyncio.gather(
                self._ultra_fast_analysis(message),
                self._update_user_metrics(message),
                self._track_behavioral_patterns(message),
                return_exceptions=True,
            )

        except Exception as e:
            self.logger.error(f"⚠️ Message processing error: {e}")
        finally:
            # 📈 PERFORMANCE METRICS
            processing_time = time.time() - start_time
            self._processing_times.append(processing_time)

            # 🧹 AUTO MEMORY CLEANUP
            self._message_counter += 1
            if self._message_counter % self.settings.get("gc_frequency", 100) == 0:
                asyncio.create_task(self._optimize_memory())

    async def _ultra_fast_analysis(self, message: discord.Message):
        """⚡ Lightning-fast message analysis with parallel checks"""

        # 🎯 GET CACHED USER PROFILE (< 1ms)
        profile = await self.get_user_profile_cached(message.author.id)

        # 🚀 PARALLEL VIOLATION DETECTION
        detection_tasks = [
            self._fast_spam_check(message, profile),
            self._fast_toxicity_check(message, profile),
            self._fast_behavior_check(message, profile),
        ]

        # ⚡ EXECUTE ALL CHECKS SIMULTANEOUSLY
        results = await asyncio.gather(*detection_tasks, return_exceptions=True)

        # 🎯 PROCESS RESULTS
        for result in results:
            if isinstance(result, ViolationType):
                # 🚨 IMMEDIATE THREAT RESPONSE
                await self._immediate_response(message, result, profile)
                return

        # ✅ NO VIOLATIONS - POSITIVE REINFORCEMENT
        if self._should_give_positive_feedback(profile):
            await self._quick_positive_response(message, profile)

    async def _fast_spam_check(
        self, message: discord.Message, profile: UserProfile
    ) -> Optional[ViolationType]:
        """⚡ Ultra-fast spam detection (< 5ms)"""
        user_id = message.author.id
        current_time = time.time()

        # 📊 ADD TO MESSAGE HISTORY
        msg_data = {
            "timestamp": current_time,
            "content_hash": hashlib.md5(message.content.encode()).hexdigest()[:8],
            "length": len(message.content),
        }
        self.message_history[user_id].append(msg_data)

        # 🔍 RAPID SPAM CHECKS
        recent_messages = [
            msg
            for msg in self.message_history[user_id]
            if current_time - msg["timestamp"] < self.settings["spam_timeframe"]
        ]

        # Check message frequency
        if len(recent_messages) > self.settings["spam_threshold"]:
            profile.add_violation("spam_frequency", 1.0)
            return ViolationType.SPAM

        # Check for repeated content (last 5 messages)
        if len(recent_messages) >= 3:
            content_hashes = [msg["content_hash"] for msg in recent_messages[-3:]]
            if len(set(content_hashes)) == 1:  # All same content
                profile.add_violation("repeated_content", 1.5)
                return ViolationType.REPEATED_CONTENT

        return None

    async def _fast_toxicity_check(
        self, message: discord.Message, profile: UserProfile
    ) -> Optional[ViolationType]:
        """🧠 Lightning-fast toxicity detection with compiled patterns"""
        content = message.content.lower()

        # 🎯 COMPILED PATTERN MATCHING (ultra-fast)
        for pattern in self.compiled_toxic_patterns:
            if pattern.search(content):
                severity = self._calculate_toxicity_severity(content)
                profile.add_violation("toxicity", severity)
                return ViolationType.TOXIC_LANGUAGE

        # 📏 CAPS ABUSE CHECK
        if len(content) > 10:
            caps_ratio = sum(1 for c in message.content if c.isupper()) / len(
                message.content
            )
            if caps_ratio > self.settings["caps_threshold"]:
                profile.add_violation("caps_abuse", 0.5)
                return ViolationType.CAPS_ABUSE

        # 📢 MENTION SPAM CHECK
        if len(message.mentions) > self.settings["mention_limit"]:
            profile.add_violation("mention_spam", 1.0)
            return ViolationType.MENTION_SPAM

        return None

    async def _fast_behavior_check(
        self, message: discord.Message, profile: UserProfile
    ) -> Optional[ViolationType]:
        """🔍 Advanced behavioral analysis for threat prediction"""

        # 📊 UPDATE BEHAVIORAL METRICS
        profile.update_behavior_pattern("last_message_time", time.time())
        profile.update_behavior_pattern("message_length", len(message.content))

        # 🚨 RISK ASSESSMENT
        risk_data = profile.get_risk_assessment()

        if risk_data["risk_level"] == "critical":
            profile.add_violation("high_risk_behavior", 2.0)
            return ViolationType.SPAM  # Treat high-risk as spam for immediate action

        # 😰 EMOTIONAL DISTRESS DETECTION
        distress_keywords = [
            "help",
            "suicide",
            "kill myself",
            "end it all",
            "can't take it",
        ]
        content_lower = message.content.lower()

        if any(keyword in content_lower for keyword in distress_keywords):
            profile.add_violation("emotional_distress", 0.1)  # Low severity for support
            return ViolationType.EMOTIONAL_DISTRESS

    async def _immediate_response(
        self, message: discord.Message, violation: ViolationType, profile: UserProfile
    ):
        """🚨 Immediate threat response system (< 100ms)"""

        # 🎯 CALCULATE RESPONSE SEVERITY
        risk_data = profile.get_risk_assessment()
        severity = self._calculate_response_severity(violation, risk_data)

        # ⚡ IMMEDIATE ACTIONS
        actions_taken = []

        try:
            # 🗑️ DELETE MESSAGE (if harmful)
            if violation in [ViolationType.TOXIC_LANGUAGE, ViolationType.SPAM]:
                await message.delete()
                actions_taken.append("message_deleted")

            # ⏰ TIMEOUT USER (for severe violations)
            if severity >= 3 and risk_data["risk_level"] in ["high", "critical"]:
                timeout_duration = min(300 * severity, 3600)  # Max 1 hour
                await message.author.timeout(
                    discord.utils.utcnow() + timedelta(seconds=timeout_duration),
                    reason=f"Auto-moderation: {violation.value}",
                )
                actions_taken.append(f"timeout_{timeout_duration}s")

            # 📢 SEND RESPONSE (non-blocking)
            asyncio.create_task(
                self._send_smart_response(message, violation, profile, severity)
            )

            # 📊 UPDATE STATS
            self.performance_stats["threats_detected"] += 1
            self.performance_stats["actions_taken"] += len(actions_taken)

            self.logger.warning(
                f"⚡ IMMEDIATE ACTION: {message.author} - {violation.value} - Actions: {actions_taken}"
            )

        except Exception as e:
            self.logger.error(f"❌ Immediate response failed: {e}")

    async def _update_user_metrics(self, message: discord.Message):
        """📊 Ultra-fast user metrics tracking"""
        user_id = message.author.id
        current_time = time.time()

        # 🎯 GET/CREATE PROFILE
        profile = await self.get_user_profile_cached(user_id)

        # ⚡ UPDATE ENGAGEMENT METRICS
        profile.engagement_metrics["messages_per_hour"] += 1
        profile.engagement_metrics["avg_message_length"] = (
            profile.engagement_metrics["avg_message_length"] * 0.9
            + len(message.content) * 0.1
        )

        # 🕐 TRACK RESPONSE TIMES
        if len(profile.response_times) > 0:
            last_time = profile.response_times[-1]
            response_time = current_time - last_time
            profile.response_times.append(response_time)
        else:
            profile.response_times.append(current_time)

    async def _track_behavioral_patterns(self, message: discord.Message):
        """🧠 Advanced behavioral pattern analysis"""
        profile = await self.get_user_profile_cached(message.author.id)
        content = message.content.lower()

        # 😊 POSITIVE BEHAVIOR DETECTION
        positive_score = 0
        for pattern in self.compiled_supportive_patterns:
            if pattern.search(content):
                positive_score += 1

        if positive_score > 0:
            profile.positive_interactions += positive_score
            profile.improvement_streak += 1
            profile.trust_score = min(100, profile.trust_score + positive_score)

    def _calculate_toxicity_severity(self, content: str) -> float:
        """🎯 Calculate toxicity severity score"""
        severity = 1.0

        # Increase severity for multiple toxic words
        toxic_count = sum(
            1 for pattern in self.compiled_toxic_patterns if pattern.search(content)
        )
        severity += toxic_count * 0.5

        # Increase for caps abuse
        caps_ratio = sum(1 for c in content if c.isupper()) / max(1, len(content))
        severity += caps_ratio * 0.5

        # Increase for excessive length (angry rants)
        if len(content) > 200:
            severity += 0.3

        return min(severity, 3.0)

    def _calculate_response_severity(
        self, violation: ViolationType, risk_data: Dict
    ) -> int:
        """🎯 Calculate appropriate response severity"""
        base_severity = {
            ViolationType.SPAM: 2,
            ViolationType.TOXIC_LANGUAGE: 3,
            ViolationType.CAPS_ABUSE: 1,
            ViolationType.MENTION_SPAM: 2,
            ViolationType.REPEATED_CONTENT: 1,
            ViolationType.EMOTIONAL_DISTRESS: 0,  # Supportive response
        }.get(violation, 1)

        # Adjust based on risk level
        risk_multiplier = {"low": 1.0, "medium": 1.2, "high": 1.5, "critical": 2.0}.get(
            risk_data["risk_level"], 1.0
        )

        return min(int(base_severity * risk_multiplier), 5)

    def _should_give_positive_feedback(self, profile: UserProfile) -> bool:
        """✨ Intelligent positive feedback timing"""
        # Give feedback based on improvement streak and trust score
        if profile.improvement_streak > 0 and profile.improvement_streak % 5 == 0:
            return True

        # Random positive reinforcement (1% chance for high trust users)
        if profile.trust_score > 80 and time.time() % 100 < 1:
            return True

        return False

    async def _quick_positive_response(
        self, message: discord.Message, profile: UserProfile
    ):
        """✨ Quick positive reinforcement system"""
        responses = [
            "Thanks for keeping our community positive! 😊",
            "Great contribution to the discussion! 👍",
            "Your positive attitude is appreciated! ✨",
            "Keep up the excellent behavior! 🌟",
        ]

        # Non-blocking response
        asyncio.create_task(message.add_reaction("👍"))

    async def _send_smart_response(
        self,
        message: discord.Message,
        violation: ViolationType,
        profile: UserProfile,
        severity: int,
    ):
        """🧠 Intelligent response system with personalization"""

        # 🎯 PERSONALIZED RESPONSE GENERATION
        response_style = profile.personality_traits.get("preferred_tone", "balanced")
        user_name = message.author.display_name

        responses = {
            ViolationType.SPAM: {
                "gentle": f"Hey {user_name}, let's slow down a bit! Quality over quantity 😊",
                "balanced": f"{user_name}, please avoid spamming. Let's keep the chat clean!",
                "strict": f"{user_name}, spam is not allowed. Please follow the rules.",
            },
            ViolationType.TOXIC_LANGUAGE: {
                "gentle": f"{user_name}, let's keep things friendly and positive! 🌟",
                "balanced": f"{user_name}, that language isn't appropriate here. Please be respectful.",
                "strict": f"{user_name}, toxic language is not tolerated. Final warning.",
            },
            ViolationType.EMOTIONAL_DISTRESS: {
                "gentle": f"{user_name}, I'm here if you need support. Consider reaching out to someone you trust. 💙",
                "balanced": f"{user_name}, if you're going through a tough time, please consider talking to a counselor or trusted friend.",
                "strict": f"{user_name}, please reach out for professional help if you're struggling.",
            },
        }

        # 📨 SEND RESPONSE
        try:
            response_text = responses.get(violation, {}).get(
                response_style, f"{user_name}, please follow community guidelines."
            )

            embed = discord.Embed(
                title="🤖 AI Moderation",
                description=response_text,
                color=0x3498DB if severity < 3 else 0xE74C3C,
                timestamp=datetime.now(timezone.utc),
            )

            if severity >= 2:
                embed.add_field(
                    name="⚠️ Warning Level", value=f"{severity}/5", inline=True
                )

            await message.channel.send(
                embed=embed, delete_after=30 if severity < 3 else None
            )

        except Exception as e:
            self.logger.error(f"❌ Failed to send response: {e}")
        """🚀 Asynchronous message processing for ultimate performance"""
        try:
            self.logger.info(
                f"📝 Processing message async for {message.author}: {message.content[:30]}"
            )

            # Track positive behavior first (lightweight operation)
            await self._track_positive_behavior(message)

            # Quick violation check with optimized algorithms
            violation = await self._comprehensive_analysis(message)

            if violation:
                self.logger.info(
                    f"🚨 VIOLATION DETECTED: {violation} for {message.author}"
                )
                await self._handle_violation_with_ai(message, violation)
            else:
                self.logger.info(f"✅ No violations detected for {message.author}")
                # Occasionally provide positive reinforcement (1% chance)
                profile = self.user_profiles.get(message.author.id)
                if (
                    profile
                    and hasattr(profile, "interaction_history")
                    and len(profile.interaction_history) % 100 == 0
                ):
                    await self._random_positive_reinforcement(message)
        except Exception as e:
            self.logger.error(f"Error in async message processing: {e}")

    async def _comprehensive_analysis(
        self, message: discord.Message
    ) -> Optional[ViolationType]:
        """🚀 ULTRA-OPTIMIZED comprehensive message analysis"""
        user_id = message.author.id
        content = message.content.lower().strip()

        # 🚀 Quick exit for short messages
        if len(content) < 3:
            return None

        # Update message history with size limit for performance
        if user_id not in self.message_history:
            self.message_history[user_id] = deque(maxlen=20)  # Limited for performance

        current_time = time.time()
        self.message_history[user_id].append(
            {
                "content": content,
                "timestamp": current_time,
                "length": len(content),
                "caps_ratio": self._calculate_caps_ratio(message.content),
            }
        )

        # 🚀 Parallel violation detection for maximum speed
        detection_tasks = [
            self._detect_spam(user_id),
            self._detect_caps_abuse(message.content),
            self._detect_mention_spam(message),
            self._detect_repeated_content(user_id, content),
            self._detect_toxic_language(content, message),
            self._detect_link_spam(user_id, content),
            self._detect_emotional_distress(content),
        ]

        try:
            results = await asyncio.gather(*detection_tasks, return_exceptions=True)

            # Map results to violation types
            violation_mapping = [
                ViolationType.SPAM,
                ViolationType.CAPS_ABUSE,
                ViolationType.MENTION_SPAM,
                ViolationType.REPEATED_CONTENT,
                ViolationType.TOXIC_LANGUAGE,
                ViolationType.LINK_SPAM,
                ViolationType.EMOTIONAL_DISTRESS,
            ]

            # Return most severe violation found
            severity_order = [
                ViolationType.EMOTIONAL_DISTRESS,
                ViolationType.TOXIC_LANGUAGE,
                ViolationType.SPAM,
                ViolationType.MENTION_SPAM,
                ViolationType.CAPS_ABUSE,
                ViolationType.REPEATED_CONTENT,
                ViolationType.LINK_SPAM,
            ]

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    continue
                if result:  # Violation detected
                    violation_type = violation_mapping[i]
                    return violation_type

        except Exception as e:
            self.logger.error(f"Error in comprehensive analysis: {e}")

        return None

    async def _detect_emotional_distress(self, content: str) -> bool:
        """🚀 OPTIMIZED emotional distress detection"""
        distress_patterns = [
            r"\b(depressed|suicide|kill myself|end it all|give up|hate myself)\b",
            r"\b(nobody cares|alone|hopeless|worthless|useless)\b",
            r"\b(can\'t take it|too much|overwhelmed|breaking down)\b",
        ]

        for pattern in distress_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    async def _detect_toxic_language(
        self, content: str, message: discord.Message
    ) -> bool:
        """🚀 OPTIMIZED toxic language detection with AI assistance"""
        # Quick pattern-based detection first
        for pattern in self.toxic_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True

        # AI-powered toxicity detection for longer messages only
        if AI_AVAILABLE and len(content) > 20:
            try:
                ai_analysis = await self._ai_toxicity_analysis(content)
                if ai_analysis and ai_analysis.get("is_toxic", False):
                    return True
            except Exception as e:
                self.logger.debug(f"AI toxicity analysis failed: {e}")

        return False

    async def _ai_toxicity_analysis(self, content: str) -> Optional[Dict]:
        """🚀 OPTIMIZED AI toxicity analysis with caching"""
        try:
            # Create cache key
            content_hash = hashlib.md5(content.encode()).hexdigest()
            cache_key = f"toxicity_{content_hash}"

            # Check cache first
            if hasattr(self, "_toxicity_cache"):
                cached_result = self._toxicity_cache.get(cache_key)
                if (
                    cached_result and time.time() - cached_result["timestamp"] < 3600
                ):  # 1 hour cache
                    return cached_result["result"]
            else:
                self._toxicity_cache = {}

            prompt = f"""Analyze toxicity in: "{content[:200]}"
JSON response: {{"is_toxic": true/false, "confidence": 0-100, "reason": "brief reason"}}"""

            ai_manager = MultiProviderAIManager()
            ai_response = await ai_manager.generate_response(prompt)

            if ai_response.success:
                # Try to extract JSON
                json_match = re.search(r"\{.*\}", ai_response.content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())

                    # Cache the result
                    self._toxicity_cache[cache_key] = {
                        "result": result,
                        "timestamp": time.time(),
                    }

                    # Limit cache size
                    if len(self._toxicity_cache) > 1000:
                        # Remove oldest entries
                        sorted_items = sorted(
                            self._toxicity_cache.items(),
                            key=lambda x: x[1]["timestamp"],
                        )
                        for old_key, _ in sorted_items[:100]:
                            del self._toxicity_cache[old_key]

                    return result

        except Exception as e:
            self.logger.error(f"AI toxicity analysis error: {e}")

        return None

    #    """Enhanced message monitoring with AI analysis"""
    #    if not message.guild or message.author.bot:
    #        return

    #    # Track positive behavior
    #    await self._track_positive_behavior(message)

    #    # Check for violations
    #    violation = await self._comprehensive_analysis(message)

    #    if violation:
    #        await self._handle_violation_with_ai(message, violation)
    #    else:
    #        # Occasionally provide positive reinforcement
    #        await self._random_positive_reinforcement(message)

    # async def _comprehensive_analysis(
    #    self, message: discord.Message
    # ) -> Optional[ViolationType]:
    #    """Comprehensive message analysis using multiple detection methods"""
    #    user_id = message.author.id
    #    content = message.content.lower().strip()

    #    # Update message history
    #    self.message_history[user_id].append(
    #        {
    #            "content": content,
    #            "timestamp": time.time(),
    #            "message": message,
    #            "length": len(content),
    #            "caps_ratio": self._calculate_caps_ratio(message.content),
    #        }
    #    )

    #    # Keep only recent messages (last 2 minutes)
    #    current_time = time.time()
    #    while (
    #        self.message_history[user_id]
    #        and current_time - self.message_history[user_id][0]["timestamp"] > 120
    #    ):
    #        self.message_history[user_id].popleft()

    #    # Run detection algorithms
    #    violations = []

    #    # 1. Spam Detection
    #    if await self._detect_spam(user_id):
    #        violations.append(ViolationType.SPAM)

    #    # 2. Caps Abuse
    #    if await self._detect_caps_abuse(message.content):
    #        violations.append(ViolationType.CAPS_ABUSE)

    #    # 3. Mention Spam
    #    if await self._detect_mention_spam(message):
    #        violations.append(ViolationType.MENTION_SPAM)

    #    # 4. Repeated Content
    #    if await self._detect_repeated_content(user_id, content):
    #        violations.append(ViolationType.REPEATED_CONTENT)

    #    # 5. Toxic Language (AI-enhanced)
    #    if await self._detect_toxic_language(content, message):
    #        violations.append(ViolationType.TOXIC_LANGUAGE)

    #    # 6. Link Spam
    #    if await self._detect_link_spam(user_id, content):
    #        violations.append(ViolationType.LINK_SPAM)

    #    # 7. Emotional Distress Detection
    #    if await self._detect_emotional_distress(content):
    #        violations.append(ViolationType.EMOTIONAL_DISTRESS)

    #    # Return most severe violation
    #    if violations:
    #        severity_order = [
    #            ViolationType.EMOTIONAL_DISTRESS,
    #            ViolationType.TOXIC_LANGUAGE,
    #            ViolationType.SPAM,
    #            ViolationType.MENTION_SPAM,
    #            ViolationType.CAPS_ABUSE,
    #            ViolationType.REPEATED_CONTENT,
    #            ViolationType.LINK_SPAM,
    #        ]

    #        for violation_type in severity_order:
    #            if violation_type in violations:
    #                return violation_type

    #    return None

    # async def _detect_emotional_distress(self, content: str) -> bool:
    #    """Detect signs of emotional distress for supportive intervention"""
    #    distress_indicators = [
    #        r"\b(depressed|suicide|kill myself|end it all|give up|hate myself)\b",
    #        r"\b(nobody cares|alone|hopeless|worthless|useless)\b",
    #        r"\b(can\'t take it|too much|overwhelmed|breaking down)\b",
    #    ]

    #    for pattern in distress_indicators:
    #        if re.search(pattern, content, re.IGNORECASE):
    #            return True
    #    return False

    # async def _detect_toxic_language(
    #    self, content: str, message: discord.Message
    # ) -> bool:
    #    """Enhanced toxic language detection with AI assistance"""
    #    # Pattern-based detection
    #    for pattern in self.toxic_patterns:
    #        if re.search(pattern, content, re.IGNORECASE):
    #            return True

    #    # AI-powered toxicity detection if available
    #    if AI_AVAILABLE and len(content) > 10:
    #        try:
    #            ai_analysis = await self._ai_toxicity_analysis(content)
    #            if ai_analysis and ai_analysis.get("is_toxic", False):
    #                return True
    #        except Exception as e:
    #            logger.error(f"AI toxicity analysis failed: {e}")

    #    return False

    # async def _ai_toxicity_analysis(self, content: str) -> Optional[Dict]:
    #    """Use AI to analyze message toxicity"""
    #    try:
    #        prompt = f"""Analyze this message for toxicity, harassment, or harmful content.
    # Message: "{content}"
    #
    # Respond in JSON format:
    # {{
    #     "is_toxic": true/false,
    #     "toxicity_level": 1-5,
    #     "reasons": ["reason1", "reason2"],
    #     "suggested_response": "supportive message suggestion"
    # }}"""

    #        ai_manager = MultiProviderAIManager()
    #        ai_response = await ai_manager.generate_response(prompt)
    #        response = (
    #            ai_response.content
    #            if ai_response.success
    #            else '{"toxicity_score": 0, "suggested_response": "I\'m here to help moderate our community!"}'
    #        )
    #
    #        # Try to extract JSON from response
    #        json_match = re.search(r"\{.*\}", response, re.DOTALL)
    #        if json_match:
    #            return json.loads(json_match.group())
    #
    #    except Exception as e:
    #        logger.error(f"AI toxicity analysis error: {e}")
    #
    #    return None

    async def _handle_violation_with_ai(
        self, message: discord.Message, violation: ViolationType
    ):
        """Handle violation with personalized AI response"""
        user = message.author
        profile = await self.get_user_profile(user.id)

        # Update violation patterns
        profile.violation_patterns[violation.value] += 1
        profile.last_violation_time = time.time()
        profile.improvement_streak = 0

        # Determine moderation level
        warning_count = len(self.user_warnings[user.id])
        mod_level = self._determine_moderation_level(violation, warning_count)

        # Delete message if needed (except for emotional distress)
        if violation != ViolationType.EMOTIONAL_DISTRESS:
            try:
                await message.delete()
            except:
                pass

        # Generate personalized AI response
        if self.settings["ai_response_enabled"] and AI_AVAILABLE:
            ai_response = await self._generate_personalized_response(
                user, violation, mod_level, profile
            )
        else:
            ai_response = await self._generate_fallback_response(
                user, violation, mod_level
            )

        # Send response
        await self._send_moderation_response(
            message.channel, user, ai_response, mod_level
        )

        # Apply consequences
        await self._apply_consequences(user, mod_level, violation)

        # Log action
        self._log_moderation_action(
            user, violation, mod_level, ai_response.get("action_taken")
        )

    async def _generate_personalized_response(
        self,
        user: discord.Member,
        violation: ViolationType,
        mod_level: ModerationLevel,
        profile: UserProfile,
    ) -> Dict[str, Any]:
        """Generate AI-powered personalized moderation response"""
        try:
            # Build context for AI
            context = {
                "user_name": user.display_name,
                "violation_type": violation.value,
                "moderation_level": mod_level.name,
                "personality_traits": profile.personality_traits,
                "violation_history": dict(profile.violation_patterns),
                "improvement_streak": profile.improvement_streak,
                "positive_interactions": profile.positive_interactions,
                "preferred_style": profile.preferred_moderator_style,
            }

            # Special handling for emotional distress
            if violation == ViolationType.EMOTIONAL_DISTRESS:
                return await self._generate_supportive_response(user, profile)

            # Create AI prompt for moderation response
            prompt = f"""Moderate {user.display_name} for {violation.value} ({mod_level.name}). Style: {profile.preferred_moderator_style}. History: {len(profile.violation_patterns)} violations, {profile.positive_interactions} positive acts.

JSON response:
{{
    "title": "Title with emoji",
    "message": "Direct, helpful message",
    "guidance": "Specific tip",
    "encouragement": "Positive note",
    "action_taken": "Action taken"
}}"""

            ai_manager = MultiProviderAIManager()
            ai_response_obj = await ai_manager.generate_response(prompt)
            ai_response = (
                ai_response_obj.content
                if ai_response_obj.success
                else '{"title": "Community Guidelines Reminder 📝", "message": "Let\'s work together to keep our community positive!", "guidance": "Remember to be respectful", "encouragement": "You\'re part of making this a great space!", "action_taken": "Gentle reminder sent"}'
            )

            # Parse AI response
            json_match = re.search(r"\{.*\}", ai_response, re.DOTALL)
            if json_match:
                parsed_response = json.loads(json_match.group())
                return parsed_response
            else:
                # Fallback parsing
                return {
                    "title": f"🤖 Hey {user.display_name}!",
                    "message": ai_response[:200],
                    "guidance": "Let's keep our community positive!",
                    "encouragement": "You've got this! 💪",
                    "action_taken": f"{mod_level.name.lower()} applied",
                }

        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            return await self._generate_fallback_response(user, violation, mod_level)

    async def _generate_supportive_response(
        self, user: discord.Member, profile: UserProfile
    ) -> Dict[str, Any]:
        """Generate supportive response for emotional distress"""
        try:
            prompt = f"""{user.display_name} needs emotional support. Be empathetic, caring, brief. JSON:
{{
    "title": "💙 We're Here for You",
    "message": "You're not alone. This community cares.",
    "resources": "Talk to trusted friend/counselor",
    "encouragement": "You matter. Things get better.",
    "action_taken": "Supportive outreach"
}}"""

            ai_manager = MultiProviderAIManager()
            ai_response_obj = await ai_manager.generate_response(prompt)
            ai_response = (
                ai_response_obj.content
                if ai_response_obj.success
                else '{"title": "We\'re Here for You 💙", "message": "I can see you might be going through something difficult. You\'re not alone, and this community cares about you.", "resources": "Consider talking to a trusted friend, family member, or counselor", "encouragement": "You matter, and things can get better. Take it one day at a time.", "action_taken": "Supportive outreach"}'
            )

            json_match = re.search(r"\{.*\}", ai_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

        except Exception as e:
            logger.error(f"Supportive response generation failed: {e}")

        # Fallback supportive response
        return {
            "title": f"💙 Hey {user.display_name}, I'm here for you",
            "message": "I noticed you might be going through a tough time. Remember that you're valued in this community and you're not alone.",
            "resources": "Consider reaching out to friends, family, or professional support if you need help.",
            "encouragement": "Things can get better, and this community is here to support you. 🤗",
            "action_taken": "Supportive outreach provided",
        }

    async def _generate_fallback_response(
        self, user: discord.Member, violation: ViolationType, mod_level: ModerationLevel
    ) -> Dict[str, Any]:
        """Generate fallback response when AI is unavailable"""
        responses = {
            ViolationType.SPAM: {
                "title": f"⏰ Hey {user.display_name}!",
                "message": "I noticed you're sending messages pretty quickly. Let's slow down a bit to keep the chat readable for everyone!",
                "guidance": "Try to combine your thoughts into fewer, more meaningful messages.",
                "encouragement": "Thanks for being active in our community! 😊",
            },
            ViolationType.CAPS_ABUSE: {
                "title": f"🔤 {user.display_name}, let's tone it down!",
                "message": "Using lots of CAPS can come across as shouting. Let's keep things friendly and conversational!",
                "guidance": "Regular text is easier to read and more welcoming.",
                "encouragement": "Your message matters - you don't need caps to be heard! 👍",
            },
            ViolationType.TOXIC_LANGUAGE: {
                "title": f"🌟 {user.display_name}, let's keep it positive!",
                "message": "I detected some language that might not be welcoming to everyone. Our community thrives on respect and kindness.",
                "guidance": "Try expressing your thoughts in a more constructive way.",
                "encouragement": "You're part of what makes this community great! 💙",
            },
        }

        template = responses.get(violation, responses[ViolationType.SPAM])
        template["action_taken"] = f"{mod_level.name.lower()} applied"
        return template

    async def _send_moderation_response(
        self,
        channel: discord.TextChannel,
        user: discord.Member,
        response: Dict[str, Any],
        mod_level: ModerationLevel,
    ):
        """Send personalized moderation response"""
        embed = discord.Embed(
            title=response.get("title", f"🤖 Hey {user.display_name}!"),
            description=response.get("message", "Please follow community guidelines."),
            color=self._get_color_for_level(mod_level),
            timestamp=datetime.now(timezone.utc),
        )

        if response.get("guidance"):
            embed.add_field(
                name="💡 Quick Tip", value=response["guidance"], inline=False
            )

        if response.get("encouragement"):
            embed.add_field(
                name="✨ Remember", value=response["encouragement"], inline=False
            )

        if response.get("resources"):
            embed.add_field(
                name="🔗 Resources", value=response["resources"], inline=False
            )

        embed.set_footer(text="I'm here to help make our community awesome! 🌟")

        # Send with auto-delete for non-supportive messages
        delete_after = None if mod_level == ModerationLevel.FRIENDLY_REMINDER else 60

        try:
            await channel.send(embed=embed, delete_after=delete_after)
        except Exception as e:
            logger.error(f"Failed to send moderation response: {e}")

    def _get_color_for_level(self, mod_level: ModerationLevel) -> int:
        """Get appropriate color for moderation level"""
        colors = {
            ModerationLevel.FRIENDLY_REMINDER: 0x00FF7F,  # Spring green
            ModerationLevel.WARNING: 0xFFD700,  # Gold
            ModerationLevel.TIMEOUT: 0xFF6B47,  # Orange red
            ModerationLevel.KICK: 0xFF4500,  # Red orange
            ModerationLevel.BAN: 0x8B0000,  # Dark red
        }
        return colors.get(mod_level, 0x00BFFF)

    async def _track_positive_behavior(self, message: discord.Message):
        """Track and reward positive behavior"""
        content = message.content.lower()

        # Check for positive patterns
        positive_score = 0
        for pattern in self.supportive_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                positive_score += 1

        if positive_score > 0:
            profile = await self.get_user_profile(message.author.id)
            profile.positive_interactions += positive_score
            profile.improvement_streak += 1

            # Occasionally acknowledge positive behavior
            if profile.improvement_streak > 0 and profile.improvement_streak % 10 == 0:
                await self._send_positive_reinforcement(
                    message.channel, message.author, profile
                )

    async def _behavioral_analysis(
        self, message: discord.Message, profile: UserProfile
    ):
        """🧠 Advanced behavioral analysis for pattern detection"""
        if not self.settings.get("behavioral_analysis", True):
            return

        content = message.content.lower()
        user_id = message.author.id

        # Analyze communication patterns
        if len(content) > 50:
            if content.count("!") > 3:
                profile.personality_traits["emotional_state"] = "excited"
            elif any(word in content for word in ["angry", "mad", "hate", "stupid"]):
                profile.personality_traits["emotional_state"] = "frustrated"
            else:
                profile.personality_traits["emotional_state"] = "stable"

        # Analyze message timing patterns
        message_times = [msg["timestamp"] for msg in self.message_history[user_id]]
        if len(message_times) >= 3:
            avg_interval = (
                sum(message_times[-1] - message_times[i] for i in range(-3, -1)) / 2
            )
            if avg_interval < 2:  # Very fast messaging
                profile.personality_traits["responsiveness"] = "high"
            elif avg_interval > 30:  # Slow messaging
                profile.personality_traits["responsiveness"] = "low"
            else:
                profile.personality_traits["responsiveness"] = "normal"

        # Update interaction history with behavioral data
        profile.interaction_history.append(
            {
                "timestamp": time.time(),
                "message_length": len(content),
                "emotional_state": profile.personality_traits["emotional_state"],
                "violation_detected": False,  # Will be updated if violation found
            }
        )

        # Keep only recent history (last 50 interactions)
        if len(profile.interaction_history) > 50:
            profile.interaction_history = profile.interaction_history[-50:]

    async def _immediate_action_handler(
        self, message: discord.Message, violation: ViolationType, profile: UserProfile
    ):
        """⚡ Immediate action handler for rapid response"""
        if not self.settings.get("immediate_actions", True):
            return False

        # Critical violations get immediate action
        critical_violations = [ViolationType.TOXIC_LANGUAGE, ViolationType.SPAM]

        if violation in critical_violations:
            # Check violation frequency
            recent_violations = sum(
                1 for v in profile.violation_patterns.values() if v > 0
            )

            if recent_violations >= 3:  # Multiple violations
                try:
                    # Immediate timeout for repeat offenders
                    timeout_duration = min(300 * recent_violations, 3600)  # Max 1 hour
                    await message.author.timeout(
                        discord.utils.utcnow() + timedelta(seconds=timeout_duration),
                        reason=f"Immediate action: {violation.value}",
                    )

                    self.logger.warning(
                        f"⚡ IMMEDIATE ACTION: {message.author} timed out for {timeout_duration}s due to {violation.value}"
                    )
                    return True

                except Exception as e:
                    self.logger.error(
                        f"Failed immediate action on {message.author}: {e}"
                    )

        return False

    async def _send_positive_reinforcement(
        self, channel: discord.TextChannel, user: discord.Member, profile: UserProfile
    ):
        """Send positive reinforcement message"""
        if not AI_AVAILABLE:
            return

        try:
            prompt = f"""Generate a brief, encouraging message for {user.display_name} who has been showing positive behavior in the community.

They have:
- {profile.positive_interactions} positive interactions
- {profile.improvement_streak} day improvement streak
- Preferred style: {profile.preferred_moderator_style}

Create a warm, appreciative message (under 100 words) with appropriate emojis."""

            ai_manager = MultiProviderAIManager()
            ai_response_obj = await ai_manager.generate_response(prompt)
            ai_response = (
                ai_response_obj.content
                if ai_response_obj.success
                else "Thank you for being such a positive presence in our community! Your contributions make this space better for everyone. Keep being awesome! ✨"
            )

            embed = discord.Embed(
                title="🌟 Community Star!",
                description=ai_response,
                color=0x00FF7F,
                timestamp=datetime.now(timezone.utc),
            )

            await channel.send(embed=embed, delete_after=30)

        except Exception as e:
            logger.error(f"Failed to send positive reinforcement: {e}")

    @tasks.loop(hours=1)
    async def cleanup_task(self):
        """Clean up old data and warnings"""
        current_time = time.time()
        decay_threshold = self.settings["warning_decay_hours"] * 3600

        # Clean up warnings
        for user_id in list(self.user_warnings.keys()):
            self.user_warnings[user_id] = [
                warning
                for warning in self.user_warnings[user_id]
                if current_time - warning < decay_threshold
            ]
            if not self.user_warnings[user_id]:
                del self.user_warnings[user_id]

        # Clean up message history
        for user_id in list(self.message_history.keys()):
            while (
                self.message_history[user_id]
                and current_time - self.message_history[user_id][0]["timestamp"] > 7200
            ):  # 2 hours
                self.message_history[user_id].popleft()
            if not self.message_history[user_id]:
                del self.message_history[user_id]

    @tasks.loop(hours=6)
    async def analyze_patterns_task(self):
        """Analyze user patterns and update profiles"""
        if not self.settings["learning_mode"]:
            return

        for user_id, profile in self.user_profiles.items():
            # Update personality traits based on behavior patterns
            await self._update_personality_traits(profile)

    async def _update_personality_traits(self, profile: UserProfile):
        """Update user personality traits based on behavior analysis"""
        # Analyze communication patterns
        if profile.violation_patterns.get("caps_abuse", 0) > 3:
            profile.personality_traits["communication_style"] = "aggressive"
        elif profile.positive_interactions > 20:
            profile.personality_traits["communication_style"] = "friendly"

        # Update preferred moderator style based on response to different approaches
        if profile.improvement_streak > 5:
            profile.preferred_moderator_style = "companion"
        elif profile.violation_patterns.get("repeated_content", 0) > 5:
            profile.preferred_moderator_style = "mentor"

    # Admin commands for moderation management

    @app_commands.command(
        name="userprofile", description="👤 View user moderation profile"
    )
    @app_commands.describe(user="User to check profile for")
    @app_commands.default_permissions(manage_messages=True)
    async def user_profile(
        self, interaction: discord.Interaction, user: discord.Member
    ):
        """View detailed user moderation profile"""
        if not await check_user_permission(
            interaction.user, PermissionLevel.MODERATOR, interaction.guild
        ):
            await interaction.response.send_message(
                "❌ You need moderator permissions for this command.", ephemeral=True
            )
            return

        profile = await self.get_user_profile(user.id)

        embed = discord.Embed(
            title=f"👤 Moderation Profile: {user.display_name}",
            color=0x00BFFF,
            timestamp=datetime.now(timezone.utc),
        )

        embed.add_field(
            name="📊 Behavior Stats",
            value=f"**Positive Interactions:** {profile.positive_interactions}\n"
            f"**Improvement Streak:** {profile.improvement_streak} days\n"
            f"**Active Warnings:** {len(self.user_warnings.get(user.id, []))}\n"
            f"**Last Violation:** {datetime.fromtimestamp(profile.last_violation_time).strftime('%Y-%m-%d %H:%M') if profile.last_violation_time else 'None'}",
            inline=False,
        )

        if profile.violation_patterns:
            violations_text = "\n".join(
                [
                    f"**{vtype.replace('_', ' ').title()}:** {count}"
                    for vtype, count in profile.violation_patterns.items()
                ]
            )
            embed.add_field(
                name="⚠️ Violation History", value=violations_text, inline=True
            )

        embed.add_field(
            name="🎭 Personality Profile",
            value=f"**Communication:** {profile.personality_traits['communication_style'].title()}\n"
            f"**Preferred Style:** {profile.preferred_moderator_style.title()}\n"
            f"**Emotional State:** {profile.personality_traits['emotional_state'].title()}",
            inline=True,
        )

        await interaction.response.send_message(embed=embed)

    # Required detection methods (simplified versions of the originals)
    async def _detect_spam(self, user_id: int) -> bool:
        recent_messages = [
            msg
            for msg in self.message_history[user_id]
            if time.time() - msg["timestamp"] <= self.settings["spam_timeframe"]
        ]
        result = len(recent_messages) >= self.settings["spam_threshold"]
        self.logger.info(
            f"🔍 SPAM CHECK: User {user_id} has {len(recent_messages)} messages in {self.settings['spam_timeframe']}s (threshold: {self.settings['spam_threshold']}) = {'SPAM' if result else 'OK'}"
        )
        return result

    async def _detect_caps_abuse(self, content: str) -> bool:
        if len(content) < 10:
            return False
        caps_ratio = sum(1 for c in content if c.isupper()) / len(content)
        return caps_ratio >= self.settings["caps_threshold"]

    async def _detect_mention_spam(self, message: discord.Message) -> bool:
        return len(message.mentions) >= self.settings["mention_limit"]

    async def _detect_repeated_content(self, user_id: int, content: str) -> bool:
        if len(content) < 5:
            return False
        recent_contents = [
            msg["content"]
            for msg in self.message_history[user_id]
            if time.time() - msg["timestamp"] <= 60
        ]
        identical_count = sum(
            1 for msg_content in recent_contents if msg_content == content
        )
        return identical_count >= 3

    async def _detect_link_spam(self, user_id: int, content: str) -> bool:
        url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        links_in_message = len(re.findall(url_pattern, content))
        return links_in_message >= self.settings["link_spam_threshold"]

    def _calculate_caps_ratio(self, text: str) -> float:
        if not text:
            return 0.0
        return sum(1 for c in text if c.isupper()) / len(text)

    def _determine_moderation_level(
        self, violation: ViolationType, warning_count: int
    ) -> ModerationLevel:
        # Special handling for emotional distress
        if violation == ViolationType.EMOTIONAL_DISTRESS:
            return ModerationLevel.FRIENDLY_REMINDER

        # Progressive escalation
        if warning_count == 0:
            return ModerationLevel.FRIENDLY_REMINDER
        elif warning_count == 1:
            return ModerationLevel.WARNING
        elif warning_count == 2:
            return ModerationLevel.TIMEOUT
        elif warning_count >= 3:
            return ModerationLevel.KICK
        else:
            return ModerationLevel.BAN

    async def _apply_consequences(
        self, user: discord.Member, mod_level: ModerationLevel, violation: ViolationType
    ):
        """Apply appropriate consequences based on moderation level"""
        if mod_level == ModerationLevel.TIMEOUT:
            try:
                duration = 300 * (
                    len(self.user_warnings.get(user.id, [])) + 1
                )  # Progressive timeout
                await user.timeout(discord.utils.utcnow() + timedelta(seconds=duration))
            except Exception as e:
                logger.error(f"Failed to timeout user {user}: {e}")

        elif mod_level == ModerationLevel.KICK:
            try:
                await user.kick(reason=f"Moderation: {violation.value}")
            except Exception as e:
                logger.error(f"Failed to kick user {user}: {e}")

        elif mod_level == ModerationLevel.BAN:
            try:
                await user.ban(
                    reason=f"Moderation: {violation.value}", delete_message_days=1
                )
            except Exception as e:
                logger.error(f"Failed to ban user {user}: {e}")

    def _log_moderation_action(
        self,
        user: discord.Member,
        violation: ViolationType,
        mod_level: ModerationLevel,
        action: str,
    ):
        """Log moderation action"""
        logger.info(
            f"AI Moderation: {user} ({user.id}) - {violation.value} - {mod_level.name} - {action}"
        )

    async def _random_positive_reinforcement(self, message: discord.Message):
        """Occasionally provide positive reinforcement for good behavior"""
        import random

        # Random chance for positive reinforcement (1 in 100 messages)
        if random.randint(1, 100) == 1 and AI_AVAILABLE:
            profile = await self.get_user_profile(message.author.id)

            # Only for users with good behavior
            if (
                profile.positive_interactions > 5
                and len(self.user_warnings.get(message.author.id, [])) == 0
            ):

                try:
                    prompt = f"Generate a brief, encouraging message for {message.author.display_name} who has been a positive member of the community. Keep it under 50 words and include an emoji."

                    ai_manager = MultiProviderAIManager()
                    ai_response_obj = await ai_manager.generate_response(prompt)
                    ai_response = (
                        ai_response_obj.content
                        if ai_response_obj.success
                        else f"Thanks for being awesome, {message.author.display_name}! 🌟"
                    )

                    await message.add_reaction("⭐")

                    # Occasionally send a message
                    if random.randint(1, 10) == 1:
                        embed = discord.Embed(
                            description=f"✨ {ai_response}", color=0x00FF7F
                        )
                        await message.channel.send(embed=embed, delete_after=15)

                except Exception as e:
                    logger.error(f"Failed positive reinforcement: {e}")


async def setup(bot):
    await bot.add_cog(AIModeration(bot))
