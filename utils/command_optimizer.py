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

from utils.performance_optimizer import performance_optimizer, cacheable, rate_limit

logger = logging.getLogger("astra.command_wrapper")


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
        cached_result = await performance_optimizer.command_optimizer.command_cache.get(
            cache_key
        )
        if cached_result is not None:
            performance_optimizer.metrics.cache_hits += 1
            logger.debug(f"Cache hit for command {self.name}")
            return cached_result

        # Execute and cache
        result = await self.original_func(*args, **kwargs)
        performance_optimizer.metrics.cache_misses += 1

        if result is not None:
            await performance_optimizer.command_optimizer.command_cache.set(
                cache_key, result, ttl
            )

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
            now = time.time()

            if key not in performance_optimizer.command_optimizer.rate_limiter:
                performance_optimizer.command_optimizer.rate_limiter[key] = []

            rate_list = performance_optimizer.command_optimizer.rate_limiter[key]

            # Remove old entries
            rate_list[:] = [t for t in rate_list if now - t < 60]

            # Check limit
            if len(rate_list) >= calls_per_minute:
                raise commands.CommandOnCooldown(
                    commands.BucketType.user,
                    60 - (now - rate_list[0]) if rate_list else 60,
                )

            rate_list.append(now)

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

        # Update global metrics
        performance_optimizer.command_optimizer._update_command_stats(
            self.name, execution_time
        )

        if not success:
            performance_optimizer.metrics.optimization_applied["failed_commands"] += 1


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
        result = await original_load_extension(name, *args, **kwargs)

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


# Export optimization decorators
optimize_command = CommandOptimizerDecorator.optimize
optimized_send = ResponseOptimizer.send_optimized
