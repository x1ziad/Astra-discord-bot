"""
🚀 AI RESPONSE PERFORMANCE OPTIMIZER
Ultra-high performance enhancements for Astra's AI response system
"""

import asyncio
import time
import hashlib
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import deque, OrderedDict
from functools import lru_cache
from dataclasses import dataclass
import weakref
import gc

logger = logging.getLogger("astra.ai.performance")


@dataclass
class ResponseMetrics:
    """Track AI response performance metrics"""

    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    avg_response_time: float = 0.0
    fastest_response: float = float("inf")
    slowest_response: float = 0.0
    provider_usage: Dict[str, int] = None
    error_count: int = 0

    def __post_init__(self):
        if self.provider_usage is None:
            self.provider_usage = {}


class AIResponseOptimizer:
    """Ultra-high performance AI response optimization system"""

    def __init__(self, max_cache_size: int = 5000, cache_ttl: int = 1800):
        # Performance caches
        self.response_cache = OrderedDict()  # LRU cache for responses
        self.context_cache = OrderedDict()  # LRU cache for contexts
        self.prompt_cache = OrderedDict()  # LRU cache for optimized prompts

        # Configuration
        self.max_cache_size = max_cache_size
        self.cache_ttl = cache_ttl

        # Performance metrics
        self.metrics = ResponseMetrics()
        self.response_times = deque(maxlen=1000)  # Track last 1000 response times

        # Optimization flags
        self.enable_aggressive_caching = True
        self.enable_prompt_optimization = True
        self.enable_context_compression = True
        self.enable_smart_truncation = True

        # Pre-compiled patterns for performance
        self._compile_performance_patterns()

        logger.info(
            "🚀 AI Response Optimizer initialized - Ultra performance mode active"
        )

    def _compile_performance_patterns(self):
        """Pre-compile regex patterns for maximum performance"""
        import re

        # Common patterns used in response optimization
        self.patterns = {
            "greeting": re.compile(
                r"\b(hello|hi|hey|good morning|good evening|greetings)\b", re.IGNORECASE
            ),
            "question": re.compile(
                r"[\?]|^(what|how|when|where|why|who|can you|could you|would you)",
                re.IGNORECASE,
            ),
            "urgent": re.compile(
                r"\b(urgent|asap|quickly|fast|emergency|help|now|immediately)\b",
                re.IGNORECASE,
            ),
            "casual": re.compile(
                r"\b(lol|haha|awesome|cool|nice|thanks|thx)\b", re.IGNORECASE
            ),
            "technical": re.compile(
                r"\b(code|programming|algorithm|function|api|database|server)\b",
                re.IGNORECASE,
            ),
        }

    def generate_cache_key(
        self, message: str, user_id: int = None, context_hash: str = None
    ) -> str:
        """Generate optimized cache key with collision resistance"""
        # Use first 100 chars of message + user context for caching
        key_components = [
            message.lower().strip()[:100],
            str(user_id) if user_id else "anon",
            context_hash or "no_context",
        ]

        key_string = "|".join(key_components)
        return hashlib.sha256(key_string.encode()).hexdigest()[
            :16
        ]  # 16 chars sufficient

    def get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Lightning-fast cache retrieval with LRU management"""
        if cache_key not in self.response_cache:
            self.metrics.cache_misses += 1
            return None

        cached_data = self.response_cache[cache_key]

        # Check TTL
        if time.time() - cached_data["timestamp"] > self.cache_ttl:
            del self.response_cache[cache_key]
            self.metrics.cache_misses += 1
            return None

        # Move to end (LRU)
        self.response_cache.move_to_end(cache_key)
        self.metrics.cache_hits += 1

        return cached_data["response"]

    def cache_response(self, cache_key: str, response: Any) -> None:
        """Cache response with automatic LRU eviction"""
        # Remove oldest if cache is full
        if len(self.response_cache) >= self.max_cache_size:
            self.response_cache.popitem(last=False)  # Remove oldest

        self.response_cache[cache_key] = {
            "response": response,
            "timestamp": time.time(),
        }

    def optimize_prompt(
        self, message: str, context: Optional[Dict] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Optimize prompt for maximum AI performance"""
        optimization_info = {
            "original_length": len(message),
            "optimizations_applied": [],
            "priority_level": "normal",
        }

        # Fast pattern matching for response type
        message_lower = message.lower()

        # Determine response priority and style
        if self.patterns["urgent"].search(message):
            optimization_info["priority_level"] = "urgent"
            optimization_info["optimizations_applied"].append("urgent_mode")

        if self.patterns["greeting"].search(message):
            optimization_info["response_type"] = "greeting"
            optimization_info["optimizations_applied"].append("greeting_optimization")

        elif self.patterns["question"].search(message):
            optimization_info["response_type"] = "question"
            optimization_info["optimizations_applied"].append("question_optimization")

        elif self.patterns["technical"].search(message):
            optimization_info["response_type"] = "technical"
            optimization_info["optimizations_applied"].append("technical_optimization")

        else:
            optimization_info["response_type"] = "conversational"

        # Smart message compression for long inputs
        optimized_message = message
        if len(message) > 2000 and self.enable_smart_truncation:
            # Keep first and last portions, summarize middle
            optimized_message = f"{message[:800]}...[content truncated for performance]...{message[-400:]}"
            optimization_info["optimizations_applied"].append("smart_truncation")

        optimization_info["optimized_length"] = len(optimized_message)

        return optimized_message, optimization_info

    def compress_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Compress context for maximum performance while preserving key information"""
        if not context or not self.enable_context_compression:
            return context

        compressed = {}

        # Keep only essential context elements
        essential_keys = [
            "user_profile",
            "emotional_context",
            "conversation_stage",
            "topics",
            "user_preferences",
        ]

        for key in essential_keys:
            if key in context:
                if key == "message_history" and len(context[key]) > 10:
                    # Keep only recent messages
                    compressed[key] = context[key][-10:]
                elif key == "topics" and len(context[key]) > 5:
                    # Keep only recent topics
                    compressed[key] = context[key][-5:]
                else:
                    compressed[key] = context[key]

        return compressed

    @lru_cache(maxsize=1000)
    def get_optimized_system_prompt(
        self, response_type: str, priority_level: str
    ) -> str:
        """Get cached optimized system prompt based on response type"""

        base_prompt = "You are Astra, an advanced AI assistant. "

        if response_type == "greeting":
            return (
                base_prompt
                + "Respond warmly and naturally to greetings. Be friendly but concise."
            )

        elif response_type == "question":
            return (
                base_prompt
                + "Answer questions directly and accurately. Be informative yet concise."
            )

        elif response_type == "technical":
            return (
                base_prompt
                + "Provide technical information clearly and accurately. Use precise language."
            )

        elif priority_level == "urgent":
            return (
                base_prompt
                + "Respond quickly and directly. Prioritize immediate helpfulness."
            )

        else:
            return (
                base_prompt
                + "Engage naturally in conversation. Be helpful, friendly, and authentic."
            )

    def track_response_time(self, response_time: float) -> None:
        """Track response time for performance analytics"""
        self.response_times.append(response_time)

        # Update metrics
        self.metrics.total_requests += 1
        self.metrics.fastest_response = min(
            self.metrics.fastest_response, response_time
        )
        self.metrics.slowest_response = max(
            self.metrics.slowest_response, response_time
        )

        # Calculate running average
        if self.response_times:
            self.metrics.avg_response_time = sum(self.response_times) / len(
                self.response_times
            )

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        cache_hit_rate = (
            (
                self.metrics.cache_hits
                / (self.metrics.cache_hits + self.metrics.cache_misses)
            )
            * 100
            if (self.metrics.cache_hits + self.metrics.cache_misses) > 0
            else 0
        )

        return {
            "cache_size": len(self.response_cache),
            "cache_hit_rate": f"{cache_hit_rate:.1f}%",
            "total_requests": self.metrics.total_requests,
            "avg_response_time": f"{self.metrics.avg_response_time:.3f}s",
            "fastest_response": f"{self.metrics.fastest_response:.3f}s",
            "slowest_response": f"{self.metrics.slowest_response:.3f}s",
            "recent_response_times": list(self.response_times)[-10:],
            "provider_usage": self.metrics.provider_usage,
            "error_count": self.metrics.error_count,
            "memory_usage": {
                "response_cache_mb": self._get_cache_size_mb(self.response_cache),
                "context_cache_mb": self._get_cache_size_mb(self.context_cache),
                "prompt_cache_mb": self._get_cache_size_mb(self.prompt_cache),
            },
        }

    def _get_cache_size_mb(self, cache: OrderedDict) -> float:
        """Estimate cache size in MB"""
        import sys

        total_size = sum(
            sys.getsizeof(key) + sys.getsizeof(value) for key, value in cache.items()
        )
        return total_size / (1024 * 1024)

    def optimize_for_peak_performance(self) -> None:
        """Apply peak performance optimizations"""
        # Force garbage collection
        gc.collect()

        # Optimize cache sizes based on usage patterns
        if self.metrics.cache_hits > self.metrics.cache_misses * 2:
            # High hit rate - increase cache size
            self.max_cache_size = min(self.max_cache_size * 1.2, 10000)
        elif self.metrics.cache_misses > self.metrics.cache_hits * 2:
            # Low hit rate - optimize cache
            self._optimize_cache()

        logger.info(
            f"🚀 Peak performance optimization applied - Cache size: {len(self.response_cache)}"
        )

    def _optimize_cache(self) -> None:
        """Optimize cache by removing less useful entries"""
        if len(self.response_cache) < 100:
            return

        # Remove oldest 25% of entries
        items_to_remove = len(self.response_cache) // 4
        for _ in range(items_to_remove):
            if self.response_cache:
                self.response_cache.popitem(last=False)


# Global optimizer instance
ai_response_optimizer = AIResponseOptimizer()


# Export for use in AI modules
__all__ = ["AIResponseOptimizer", "ai_response_optimizer", "ResponseMetrics"]
