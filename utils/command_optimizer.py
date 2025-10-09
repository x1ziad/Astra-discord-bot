"""
Command Performance Wrapper
Automatically applies performance optimizations to bot commands
"""

import asyncio
import logging
import time
import functools
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timezone
import discord
from discord.ext import commands

logger = logging.getLogger("astra.command_wrapper")


# Simple in-memory cache and rate limiter
class SimpleCache:
    def __init__(self):
        self._cache = {}
        self._timestamps = {}

    async def get(self, key: str):
        if key in self._cache:
            timestamp, ttl, value = self._cache[key]
            if time.time() - timestamp < ttl:
                return value
            else:
                del self._cache[key]
                if key in self._timestamps:
                    del self._timestamps[key]
        return None

    async def set(self, key: str, value, ttl: int = 300):
        self._cache[key] = (time.time(), ttl, value)


class SimpleRateLimiter:
    def __init__(self):
        self._limits = {}

    def check_limit(self, key: str, calls_per_minute: int = 30) -> bool:
        now = time.time()
        if key not in self._limits:
            self._limits[key] = []

        # Remove old entries
        self._limits[key] = [t for t in self._limits[key] if now - t < 60]

        # Check limit
        if len(self._limits[key]) >= calls_per_minute:
            return False

        self._limits[key].append(now)
        return True


# Global instances
_command_cache = SimpleCache()
_rate_limiter = SimpleRateLimiter()


# Response Cache for compatibility with existing cogs
class ResponseCache:
    """Simple response cache for backwards compatibility"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache = {}
        self._timestamps = {}
        self._hits = 0
        self._misses = 0

    async def get(self, key: str):
        """Get cached response"""
        if key in self._cache:
            timestamp, ttl, value = self._cache[key]
            if time.time() - timestamp < ttl:
                self._hits += 1
                return value
            else:
                await self.delete(key)
        self._misses += 1
        return None

    async def set(self, key: str, value, ttl: int = None):
        """Set cached response"""
        if ttl is None:
            ttl = self.default_ttl

        # Simple cache size management
        if len(self._cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][0])
            await self.delete(oldest_key)

        self._cache[key] = (time.time(), ttl, value)

    async def delete(self, key: str):
        """Delete cached response"""
        if key in self._cache:
            del self._cache[key]
        if key in self._timestamps:
            del self._timestamps[key]

    async def clear(self):
        """Clear all cached responses"""
        self._cache.clear()
        self._timestamps.clear()

    def size(self) -> int:
        """Get cache size"""
        return len(self._cache)

    def get_stats(self) -> dict:
        """Get cache statistics"""
        current_size = len(self._cache)

        # Calculate hit rate (simplified - would need proper tracking for accuracy)
        # For now, we'll provide a basic implementation
        hit_rate = 0.0
        if hasattr(self, "_hits") and hasattr(self, "_misses"):
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

        return {
            "size": current_size,
            "max_size": self.max_size,
            "hit_rate": hit_rate,
            "ttl": self.default_ttl,
        }


class OptimizedCommand:
    """Wrapper for optimizing command performance"""

    def __init__(
        self,
        command_func: Callable,
        optimization_config: Optional[Dict[str, Any]] = None,
    ):
        self.original_func = command_func
        self.config = optimization_config or {}
        self.name = command_func.__name__
        self.call_count = 0
        self.total_time = 0.0
        self.last_optimization = datetime.now(timezone.utc)

    def __call__(self, *args, **kwargs):
        """Execute optimized command"""
        return self._execute_optimized(*args, **kwargs)

    async def _execute_optimized(self, *args, **kwargs):
        """Execute command with optimizations"""
        start_time = time.time()

        try:
            # Apply rate limiting if configured
            if self.config.get("rate_limit"):
                await self._check_rate_limit(*args, **kwargs)

            # Apply caching if configured
            if self.config.get("cacheable"):
                result = await self._execute_with_cache(*args, **kwargs)
            else:
                result = await self.original_func(*args, **kwargs)

            # Track performance
            execution_time = time.time() - start_time
            self._update_performance_stats(execution_time, success=True)

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            self._update_performance_stats(execution_time, success=False)
            logger.error(f"Command {self.name} failed: {e}")
            raise

    async def _execute_with_cache(self, *args, **kwargs):
        """Execute command with caching"""
        cache_key = self._generate_cache_key(*args, **kwargs)
        ttl = self.config.get("cache_ttl", 300)

        # Check cache
        cached_result = await _command_cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Cache hit for command {self.name}")
            return cached_result

        # Execute and cache
        result = await self.original_func(*args, **kwargs)

        if result is not None:
            await _command_cache.set(cache_key, result, ttl)

        return result

    async def _check_rate_limit(self, *args, **kwargs):
        """Check rate limiting"""
        rate_limit_config = self.config.get("rate_limit", {})
        calls_per_minute = rate_limit_config.get("calls_per_minute", 30)

        # Extract user ID from context
        user_id = None
        if args and hasattr(args[0], "user"):
            user_id = args[0].user.id
        elif args and hasattr(args[0], "author"):
            user_id = args[0].author.id

        if user_id:
            key = f"{self.name}:{user_id}"

            if not _rate_limiter.check_limit(key, calls_per_minute):
                raise commands.CommandOnCooldown(
                    commands.BucketType.user,
                    60,  # Retry after 60 seconds
                )

    def _generate_cache_key(self, *args, **kwargs) -> str:
        """Generate cache key for command"""
        key_parts = [self.name]

        # Add relevant args
        if args:
            # Skip context object
            relevant_args = args[1:] if len(args) > 1 else []
            for arg in relevant_args:
                if isinstance(arg, (str, int, float)):
                    key_parts.append(str(arg))
                elif hasattr(arg, "id"):
                    key_parts.append(str(arg.id))

        # Add relevant kwargs
        for key, value in kwargs.items():
            if isinstance(value, (str, int, float)):
                key_parts.append(f"{key}:{value}")

        return ":".join(key_parts)

    def _update_performance_stats(self, execution_time: float, success: bool):
        """Update performance statistics"""
        self.call_count += 1
        self.total_time += execution_time

        # Log performance metrics
        logger.debug(
            f"Command {self.name}: {execution_time:.3f}s ({'success' if success else 'failed'})"
        )

        if not success:
            logger.warning(f"Command {self.name} failed after {execution_time:.3f}s")


class CommandOptimizerDecorator:
    """Decorator factory for command optimization"""

    @staticmethod
    def optimize(
        cacheable: bool = False,
        cache_ttl: int = 300,
        rate_limit_per_minute: int = 30,
        rate_limit_enabled: bool = False,
    ):
        """Decorator to optimize command performance"""

        def decorator(func):
            optimization_config = {
                "cacheable": cacheable,
                "cache_ttl": cache_ttl,
                "rate_limit": (
                    {
                        "enabled": rate_limit_enabled,
                        "calls_per_minute": rate_limit_per_minute,
                    }
                    if rate_limit_enabled
                    else None
                ),
            }

            optimized_command = OptimizedCommand(func, optimization_config)

            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                return await optimized_command._execute_optimized(*args, **kwargs)

            # Add optimization metadata
            wrapper._optimization_config = optimization_config
            wrapper._optimized_command = optimized_command

            return wrapper

        return decorator


def auto_optimize_commands(bot_class):
    """Class decorator to automatically optimize all commands"""

    # Command optimization rules
    OPTIMIZATION_RULES = {
        # High-frequency, cacheable commands
        "info": {"cacheable": True, "cache_ttl": 600},
        "status": {"cacheable": True, "cache_ttl": 60},
        "help": {"cacheable": True, "cache_ttl": 1800},
        "avatar": {"cacheable": True, "cache_ttl": 900},
        "fact": {"cacheable": True, "cache_ttl": 3600},
        "lore": {"cacheable": True, "cache_ttl": 3600},
        # Rate-limited commands
        "chat": {"rate_limit_enabled": True, "rate_limit_per_minute": 20},
        "analyze": {"rate_limit_enabled": True, "rate_limit_per_minute": 10},
        "summarize": {"rate_limit_enabled": True, "rate_limit_per_minute": 15},
        "translate": {"rate_limit_enabled": True, "rate_limit_per_minute": 25},
        # Admin commands (strict rate limiting)
        "reload": {"rate_limit_enabled": True, "rate_limit_per_minute": 5},
        "shutdown": {"rate_limit_enabled": True, "rate_limit_per_minute": 2},
        "logs": {"rate_limit_enabled": True, "rate_limit_per_minute": 10},
        # Analytics (cacheable but short TTL)
        "overview": {"cacheable": True, "cache_ttl": 300},
        "leaderboard": {"cacheable": True, "cache_ttl": 180},
        "stats": {"cacheable": True, "cache_ttl": 300},
        # Quiz commands
        "quiz_stats": {"cacheable": True, "cache_ttl": 600},
        "quiz_leaderboard": {"cacheable": True, "cache_ttl": 300},
        "quiz_categories": {"cacheable": True, "cache_ttl": 3600},
        # Space commands (highly cacheable)
        "space_fact": {"cacheable": True, "cache_ttl": 7200},
        "apod": {"cacheable": True, "cache_ttl": 43200},  # 12 hours
        # Notion commands (medium caching)
        "notion_sync": {
            "cacheable": True,
            "cache_ttl": 300,
            "rate_limit_enabled": True,
            "rate_limit_per_minute": 3,
        },
    }

    def optimize_cog_commands(cog_class):
        """Optimize all commands in a cog"""
        for attr_name in dir(cog_class):
            attr = getattr(cog_class, attr_name)

            # Check if it's a command
            if hasattr(attr, "__wrapped__") and hasattr(attr.__wrapped__, "__name__"):

                command_name = attr.__wrapped__.__name__

                # Apply optimization rules
                if command_name in OPTIMIZATION_RULES:
                    rules = OPTIMIZATION_RULES[command_name]
                    logger.info(
                        f"Auto-optimizing command: {command_name} with rules: {rules}"
                    )

                    # Apply optimization decorator
                    optimized = CommandOptimizerDecorator.optimize(**rules)(
                        attr.__wrapped__
                    )
                    setattr(cog_class, attr_name, optimized)

        return cog_class

    # Apply to all cogs
    original_load_extension = bot_class.load_extension

    async def optimized_load_extension(self, name, *args, **kwargs):
        """Load extension with command optimization"""
        result = await original_load_extension(self, name, *args, **kwargs)

        # Get the loaded cog
        cog_name = name.split(".")[-1]
        cog = self.get_cog(cog_name)

        if cog:
            # Optimize the cog's commands
            optimize_cog_commands(cog.__class__)
            logger.info(f"Applied command optimizations to cog: {cog_name}")

        return result

    bot_class.load_extension = optimized_load_extension
    return bot_class


class ResponseOptimizer:
    """Optimize Discord responses and embeds"""

    @staticmethod
    def optimize_embed(embed: discord.Embed) -> discord.Embed:
        """Optimize embed for faster rendering"""
        # Limit field count for performance
        if len(embed.fields) > 25:
            embed.clear_fields()
            for field in embed.fields[:24]:
                embed.add_field(
                    name=field.name[:256],  # Limit field name length
                    value=field.value[:1024],  # Limit field value length
                    inline=field.inline,
                )
            embed.add_field(
                name="...", value="Results truncated for performance", inline=False
            )

        # Optimize description length
        if embed.description and len(embed.description) > 4096:
            embed.description = embed.description[:4093] + "..."

        # Optimize title length
        if embed.title and len(embed.title) > 256:
            embed.title = embed.title[:253] + "..."

        return embed

    @staticmethod
    def optimize_content(content: str) -> str:
        """Optimize message content"""
        # Limit message length
        if len(content) > 2000:
            content = content[:1997] + "..."

        return content

    @staticmethod
    async def send_optimized(
        ctx,
        content: Optional[str] = None,
        embed: Optional[discord.Embed] = None,
        **kwargs,
    ):
        """Send optimized Discord message"""
        if content:
            content = ResponseOptimizer.optimize_content(content)

        if embed:
            embed = ResponseOptimizer.optimize_embed(embed)

        return await ctx.send(content=content, embed=embed, **kwargs)


# Simple standalone decorators for compatibility
def cacheable(func):
    """Simple cache decorator"""
    return CommandOptimizerDecorator.optimize(cacheable=True, cache_ttl=300)(func)


def rate_limit(calls_per_minute: int = 30):
    """Simple rate limit decorator"""

    def decorator(func):
        return CommandOptimizerDecorator.optimize(
            rate_limit_enabled=True, rate_limit_per_minute=calls_per_minute
        )(func)

    return decorator


# Export optimization decorators
optimize_command = CommandOptimizerDecorator.optimize
optimized_send = ResponseOptimizer.send_optimized
