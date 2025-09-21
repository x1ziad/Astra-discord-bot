"""
Performance Optimizer for Astra Bot
Implements comprehensive performance optimizations for faster bot responses
"""

import asyncio
import logging
import time
import json
import functools
import weakref
import re
from typing import Dict, List, Any, Optional, Callable, Tuple
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from collections import defaultdict, deque
import hashlib
import gc
import threading

logger = logging.getLogger("astra.performance_optimizer")


@dataclass
class PerformanceMetrics:
    """Performance metrics tracking"""

    command_times: Dict[str, List[float]] = field(
        default_factory=lambda: defaultdict(list)
    )
    cache_hits: int = 0
    cache_misses: int = 0
    db_query_times: List[float] = field(default_factory=list)
    ai_response_times: List[float] = field(default_factory=list)
    memory_usage: List[float] = field(default_factory=list)
    optimization_applied: Dict[str, int] = field(
        default_factory=lambda: defaultdict(int)
    )


class ResponseCache:
    """Advanced response caching system with improved memory management"""

    def __init__(self, max_size: int = 10000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, Any] = {}
        self._expiry: Dict[str, float] = {}
        self._access_times: Dict[str, float] = {}
        self._hit_count = 0
        self._miss_count = 0
        self._lock = asyncio.Lock()

        # Performance tracking
        self._memory_usage = 0
        self._last_cleanup = time.time()

    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()

    async def get(self, key: str) -> Optional[Any]:
        """Get cached value with hit/miss tracking"""
        async with self._lock:
            now = time.time()

            if key in self._cache:
                if now < self._expiry.get(key, 0):
                    self._access_times[key] = now
                    self._hit_count += 1
                    return self._cache[key]
                else:
                    # Expired
                    self._remove_key(key)

            self._miss_count += 1
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cached value"""
        async with self._lock:
            now = time.time()
            ttl = ttl or self.default_ttl

            # Remove old entries if cache is full
            if len(self._cache) >= self.max_size:
                await self._evict_lru()

            self._cache[key] = value
            self._expiry[key] = now + ttl
            self._access_times[key] = now

    def _remove_key(self, key: str):
        """Remove key from all data structures"""
        self._cache.pop(key, None)
        self._expiry.pop(key, None)
        self._access_times.pop(key, None)

    async def _evict_lru(self):
        """Evict least recently used entries"""
        if not self._access_times:
            return

        # Remove 10% of cache
        num_to_remove = max(1, len(self._cache) // 10)

        # Sort by access time
        sorted_keys = sorted(self._access_times.items(), key=lambda x: x[1])

        for key, _ in sorted_keys[:num_to_remove]:
            self._remove_key(key)

    async def clear_expired(self):
        """Clear expired entries"""
        async with self._lock:
            now = time.time()
            expired_keys = [
                key for key, expiry in self._expiry.items() if now >= expiry
            ]

            for key in expired_keys:
                self._remove_key(key)

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        total_requests = self._hit_count + self._miss_count
        hit_rate = (self._hit_count / total_requests) if total_requests > 0 else 0

        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "usage_ratio": len(self._cache) / self.max_size if self.max_size > 0 else 0,
            "hit_count": self._hit_count,
            "miss_count": self._miss_count,
            "hit_rate": hit_rate,
            "efficiency": hit_rate * 100,
            "memory_usage": self._memory_usage,
            "last_cleanup": self._last_cleanup,
        }


class CommandOptimizer:
    """Command execution optimizer"""

    def __init__(self):
        self.command_cache = ResponseCache(max_size=5000, default_ttl=60)
        self.rate_limiter = {}
        self.command_stats = defaultdict(
            lambda: {"count": 0, "total_time": 0.0, "avg_time": 0.0}
        )
        self._optimization_rules = {}

    def cacheable(self, ttl: int = 60, key_func: Optional[Callable] = None):
        """Decorator for cacheable command results"""

        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = f"{func.__name__}:{self.command_cache._generate_key(*args, **kwargs)}"

                # Try cache first
                cached_result = await self.command_cache.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_result

                # Execute function
                start_time = time.time()
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time

                # Cache result if successful
                if result is not None:
                    await self.command_cache.set(cache_key, result, ttl)

                # Update stats
                self._update_command_stats(func.__name__, execution_time)

                return result

            return wrapper

        return decorator

    def rate_limit(self, calls_per_minute: int = 30):
        """Decorator for rate limiting commands"""

        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                user_id = None

                # Extract user ID from context
                if args and hasattr(args[0], "user"):
                    user_id = args[0].user.id
                elif args and hasattr(args[0], "author"):
                    user_id = args[0].author.id

                if user_id:
                    key = f"{func.__name__}:{user_id}"
                    now = time.time()

                    # Initialize rate limiter for this key
                    if key not in self.rate_limiter:
                        self.rate_limiter[key] = deque()

                    # Remove old entries
                    while (
                        self.rate_limiter[key] and now - self.rate_limiter[key][0] > 60
                    ):
                        self.rate_limiter[key].popleft()

                    # Check rate limit
                    if len(self.rate_limiter[key]) >= calls_per_minute:
                        logger.warning(
                            f"Rate limit exceeded for {func.__name__} by user {user_id}"
                        )
                        return None

                    # Add current request
                    self.rate_limiter[key].append(now)

                return await func(*args, **kwargs)

            return wrapper

        return decorator

    def _update_command_stats(self, command_name: str, execution_time: float):
        """Update command performance statistics"""
        stats = self.command_stats[command_name]
        stats["count"] += 1
        stats["total_time"] += execution_time
        stats["avg_time"] = stats["total_time"] / stats["count"]

        # Log slow commands
        if execution_time > 2.0:
            logger.warning(
                f"Slow command detected: {command_name} took {execution_time:.2f}s"
            )

    def get_slow_commands(self, threshold: float = 1.0) -> List[Tuple[str, float]]:
        """Get commands that are consistently slow"""
        slow_commands = []

        for command, stats in self.command_stats.items():
            if stats["avg_time"] > threshold and stats["count"] > 3:
                slow_commands.append((command, stats["avg_time"]))

        return sorted(slow_commands, key=lambda x: x[1], reverse=True)


class AIResponseOptimizer:
    """AI response optimization"""

    def __init__(self):
        self.response_cache = ResponseCache(
            max_size=15000, default_ttl=1800
        )  # 30 min TTL
        self.context_cache = ResponseCache(max_size=5000, default_ttl=900)  # 15 min TTL
        self.model_selector = ModelSelector()
        self._conversation_patterns = defaultdict(list)

    async def optimize_ai_request(
        self, prompt: str, user_id: int, guild_id: int, context: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Optimize AI request with caching and smart routing"""

        # Generate cache key based on prompt content
        prompt_hash = hashlib.md5(prompt.lower().strip().encode()).hexdigest()
        cache_key = f"ai_response:{prompt_hash}:{guild_id}"

        # Check cache for similar prompts
        cached_response = await self.response_cache.get(cache_key)
        if cached_response:
            logger.debug("AI response cache hit")
            return cached_response["response"], cached_response["metadata"]

        # Optimize prompt
        optimized_prompt = self._optimize_prompt(prompt, context)

        # Select optimal model
        model_info = await self.model_selector.select_optimal_model(
            prompt=optimized_prompt, user_id=user_id, guild_id=guild_id
        )

        metadata = {
            "model_selected": model_info["model"],
            "optimization_applied": True,
            "prompt_optimized": len(optimized_prompt) != len(prompt),
            "cache_used": False,
        }

        return optimized_prompt, metadata

    def _optimize_prompt(self, prompt: str, context: Optional[str] = None) -> str:
        """Optimize prompt for better AI responses"""
        optimized = prompt.strip()

        # Remove excessive whitespace
        optimized = re.sub(r"\s+", " ", optimized)

        # Add context if provided and relevant
        if context and len(context) < 500:  # Only add short context
            optimized = f"Context: {context}\n\nUser: {optimized}"

        # Ensure prompt clarity
        if not optimized.endswith(("?", ".", "!", ":")):
            optimized += "."

        return optimized

    async def cache_response(
        self, prompt: str, response: str, guild_id: int, metadata: Dict[str, Any]
    ):
        """Cache AI response for future use"""
        prompt_hash = hashlib.md5(prompt.lower().strip().encode()).hexdigest()
        cache_key = f"ai_response:{prompt_hash}:{guild_id}"

        cache_data = {
            "response": response,
            "metadata": metadata,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Determine TTL based on response quality
        ttl = 1800  # Default 30 minutes
        if len(response) > 500:  # Longer responses cached longer
            ttl = 3600
        elif any(word in response.lower() for word in ["error", "sorry", "unable"]):
            ttl = 300  # Error responses cached shorter

        await self.response_cache.set(cache_key, cache_data, ttl)


class ModelSelector:
    """Intelligent model selection for optimal performance"""

    def __init__(self):
        self.model_performance = defaultdict(
            lambda: {"avg_time": 0.0, "success_rate": 100.0, "uses": 0}
        )
        self.user_preferences = defaultdict(str)
        self.guild_preferences = defaultdict(str)

    async def select_optimal_model(
        self, prompt: str, user_id: int, guild_id: int
    ) -> Dict[str, Any]:
        """Select the optimal model based on various factors"""

        # Analyze prompt characteristics
        prompt_length = len(prompt)
        prompt_complexity = self._analyze_prompt_complexity(prompt)

        # Default model selection logic
        if prompt_length < 100 and prompt_complexity < 0.5:
            recommended_model = "fast_model"
            reasoning = "Short, simple prompt - using fast model"
        elif prompt_complexity > 0.8:
            recommended_model = "advanced_model"
            reasoning = "Complex prompt - using advanced model"
        else:
            recommended_model = "balanced_model"
            reasoning = "Balanced prompt - using standard model"

        # Check guild preferences
        guild_pref = self.guild_preferences.get(guild_id)
        if guild_pref:
            recommended_model = guild_pref
            reasoning = f"Using guild preference: {guild_pref}"

        return {
            "model": recommended_model,
            "reasoning": reasoning,
            "prompt_length": prompt_length,
            "complexity_score": prompt_complexity,
        }

    def _analyze_prompt_complexity(self, prompt: str) -> float:
        """Analyze prompt complexity (0.0 = simple, 1.0 = complex)"""
        complexity_indicators = [
            len(prompt.split()) > 50,  # Long prompts
            len([w for w in prompt.split() if len(w) > 8]) > 3,  # Complex words
            any(
                keyword in prompt.lower()
                for keyword in ["analyze", "explain", "describe", "compare", "evaluate"]
            ),  # Complex tasks
            prompt.count("?") > 1,  # Multiple questions
            any(char in prompt for char in [";", ":", "(", ")"]),  # Complex structure
        ]

        return sum(complexity_indicators) / len(complexity_indicators)


class DatabaseOptimizer:
    """Database query optimization"""

    def __init__(self):
        self.query_cache = ResponseCache(max_size=8000, default_ttl=600)
        self.batch_operations = defaultdict(list)
        self.batch_timer = None
        self._batch_lock = asyncio.Lock()

    def cache_query(self, ttl: int = 600):
        """Decorator for caching database queries"""

        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = f"db:{func.__name__}:{self.query_cache._generate_key(*args, **kwargs)}"

                # Try cache first
                cached_result = await self.query_cache.get(cache_key)
                if cached_result is not None:
                    return cached_result

                # Execute query
                result = await func(*args, **kwargs)

                # Cache result
                await self.query_cache.set(cache_key, result, ttl)

                return result

            return wrapper

        return decorator

    async def batch_write(
        self, operation: str, data: Dict[str, Any], delay: float = 0.1
    ):
        """Batch write operations for better performance"""
        async with self._batch_lock:
            self.batch_operations[operation].append(data)

            # Set timer for batch execution
            if self.batch_timer is None:
                self.batch_timer = asyncio.create_task(
                    self._execute_batch_after_delay(delay)
                )

    async def _execute_batch_after_delay(self, delay: float):
        """Execute batched operations after delay"""
        await asyncio.sleep(delay)

        async with self._batch_lock:
            if self.batch_operations:
                # Execute all batched operations
                for operation, data_list in self.batch_operations.items():
                    if data_list:
                        await self._execute_batch_operation(operation, data_list)

                # Clear batch
                self.batch_operations.clear()

            self.batch_timer = None

    async def _execute_batch_operation(
        self, operation: str, data_list: List[Dict[str, Any]]
    ):
        """Execute a specific batch operation"""
        try:
            if operation == "analytics":
                # Batch analytics insertions
                from utils.database import db

                # Implementation would depend on specific database structure
                logger.info(f"Executing batch {operation} with {len(data_list)} items")

            elif operation == "command_usage":
                # Batch command usage logging
                logger.info(f"Executing batch {operation} with {len(data_list)} items")

        except Exception as e:
            logger.error(f"Batch operation {operation} failed: {e}")


class MemoryOptimizer:
    """Memory usage optimization"""

    def __init__(self):
        self.object_pools = {}
        self.weak_references = weakref.WeakSet()
        self._gc_threshold = 1000
        self._object_count = 0

    def get_pooled_object(self, obj_type: str, factory: Callable):
        """Get object from pool or create new one"""
        if obj_type not in self.object_pools:
            self.object_pools[obj_type] = []

        pool = self.object_pools[obj_type]

        if pool:
            return pool.pop()
        else:
            obj = factory()
            self.weak_references.add(obj)
            return obj

    def return_to_pool(self, obj_type: str, obj: Any):
        """Return object to pool for reuse"""
        if obj_type not in self.object_pools:
            self.object_pools[obj_type] = []

        # Reset object state if needed
        if hasattr(obj, "reset"):
            obj.reset()

        self.object_pools[obj_type].append(obj)

    def optimize_memory(self):
        """Perform memory optimization"""
        self._object_count += 1

        if self._object_count >= self._gc_threshold:
            # Force garbage collection
            collected = gc.collect()
            logger.debug(f"Memory optimization: collected {collected} objects")

            # Clear object pools if they're getting too large
            for obj_type, pool in self.object_pools.items():
                if len(pool) > 100:
                    # Keep only recent objects
                    self.object_pools[obj_type] = pool[-50:]

            self._object_count = 0


class PerformanceOptimizer:
    """Main performance optimization coordinator"""

    def __init__(self):
        self.metrics = PerformanceMetrics()
        self.command_optimizer = CommandOptimizer()
        self.ai_optimizer = AIResponseOptimizer()
        self.db_optimizer = DatabaseOptimizer()
        self.memory_optimizer = MemoryOptimizer()
        self._optimization_enabled = True
        self._performance_monitor_task = None

    def start_monitoring(self):
        """Start performance monitoring"""
        if self._performance_monitor_task is None:
            self._performance_monitor_task = asyncio.create_task(
                self._performance_monitor_loop()
            )
            logger.info("Performance monitoring started")

    def stop_monitoring(self):
        """Stop performance monitoring"""
        if self._performance_monitor_task:
            self._performance_monitor_task.cancel()
            self._performance_monitor_task = None
            logger.info("Performance monitoring stopped")

    async def _performance_monitor_loop(self):
        """Main performance monitoring loop"""
        while self._optimization_enabled:
            try:
                # Clear expired caches
                await self.command_optimizer.command_cache.clear_expired()
                await self.ai_optimizer.response_cache.clear_expired()
                await self.db_optimizer.query_cache.clear_expired()

                # Memory optimization
                self.memory_optimizer.optimize_memory()

                # Log performance metrics
                await self._log_performance_metrics()

                # Sleep for monitoring interval
                await asyncio.sleep(300)  # 5 minutes

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Performance monitor error: {e}")
                await asyncio.sleep(60)  # Shorter sleep on error

    async def _log_performance_metrics(self):
        """Log current performance metrics"""
        # Get cache stats
        command_cache_stats = self.command_optimizer.command_cache.get_stats()
        ai_cache_stats = self.ai_optimizer.response_cache.get_stats()
        db_cache_stats = self.db_optimizer.query_cache.get_stats()

        # Log cache efficiency
        total_cache_ratio = (
            command_cache_stats["usage_ratio"]
            + ai_cache_stats["usage_ratio"]
            + db_cache_stats["usage_ratio"]
        ) / 3

        logger.info(
            f"Performance: Cache efficiency {total_cache_ratio:.1%}, "
            f"Memory pools: {len(self.memory_optimizer.object_pools)}"
        )

        # Identify slow commands
        slow_commands = self.command_optimizer.get_slow_commands()
        if slow_commands:
            logger.warning(f"Slow commands detected: {slow_commands[:3]}")

    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        return {
            "caches": {
                "command_cache": self.command_optimizer.command_cache.get_stats(),
                "ai_cache": self.ai_optimizer.response_cache.get_stats(),
                "db_cache": self.db_optimizer.query_cache.get_stats(),
            },
            "command_stats": dict(self.command_optimizer.command_stats),
            "slow_commands": self.command_optimizer.get_slow_commands(),
            "memory_pools": {
                pool_type: len(pool)
                for pool_type, pool in self.memory_optimizer.object_pools.items()
            },
            "metrics": {
                "cache_hits": self.metrics.cache_hits,
                "cache_misses": self.metrics.cache_misses,
                "optimization_applied": dict(self.metrics.optimization_applied),
            },
        }


# Global optimizer instance
performance_optimizer = PerformanceOptimizer()


# Decorator shortcuts
cacheable = performance_optimizer.command_optimizer.cacheable
rate_limit = performance_optimizer.command_optimizer.rate_limit
cache_query = performance_optimizer.db_optimizer.cache_query
