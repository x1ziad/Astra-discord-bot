"""
Discord Rate Limiter for Astra Bot
Prevents Discord API rate limiting by managing request frequency
"""

import asyncio
import time
import logging
from typing import Dict, Optional
from collections import deque, defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger("astra.rate_limiter")


class DiscordRateLimiter:
    """Rate limiter for Discord API operations"""

    def __init__(self):
        # Rate limit tracking per endpoint/channel
        self.request_history = defaultdict(deque)  # Stores request timestamps
        self.rate_limits = {
            # Message sending limits
            "messages": {
                "limit": 5,
                "window": 5,
            },  # 5 messages per 5 seconds per channel
            "global_messages": {
                "limit": 50,
                "window": 60,
            },  # 50 messages per minute globally
            # Moderation limits
            "moderation": {
                "limit": 10,
                "window": 60,
            },  # 10 moderation actions per minute
            # General API limits
            "api_general": {
                "limit": 30,
                "window": 60,
            },  # 30 general API calls per minute
        }

        # Global counters
        self.global_message_count = 0
        self.global_window_start = time.time()

        # Backoff tracking
        self.backoff_until = {}

        # Statistics
        self.stats = {"requests_made": 0, "requests_delayed": 0, "backoff_events": 0}

    async def check_rate_limit(
        self, endpoint: str, identifier: str = "global"
    ) -> float:
        """
        Check if request is within rate limits
        Returns: delay in seconds (0 if no delay needed)
        """
        current_time = time.time()
        key = f"{endpoint}:{identifier}"

        # Check if we're in backoff period
        if key in self.backoff_until and current_time < self.backoff_until[key]:
            delay = self.backoff_until[key] - current_time
            logger.warning(
                f"⏸️  Rate limiter: backoff active for {key}, delay: {delay:.1f}s"
            )
            return delay

        # Get rate limit config
        if endpoint not in self.rate_limits:
            endpoint = "api_general"  # Default rate limit

        config = self.rate_limits[endpoint]
        limit = config["limit"]
        window = config["window"]

        # Clean old requests outside the window
        history = self.request_history[key]
        cutoff_time = current_time - window
        while history and history[0] < cutoff_time:
            history.popleft()

        # Check if we're at the limit
        if len(history) >= limit:
            # Calculate delay until oldest request expires
            delay = (history[0] + window) - current_time
            if delay > 0:
                self.stats["requests_delayed"] += 1
                logger.info(f"⏳ Rate limiter: delaying {key} for {delay:.1f}s")
                return delay

        return 0.0

    async def acquire(self, endpoint: str, identifier: str = "global") -> None:
        """
        Acquire rate limit permission (with delay if needed)
        """
        delay = await self.check_rate_limit(endpoint, identifier)
        if delay > 0:
            await asyncio.sleep(delay)

        # Record the request
        current_time = time.time()
        key = f"{endpoint}:{identifier}"
        self.request_history[key].append(current_time)
        self.stats["requests_made"] += 1

        # Update global message counter
        if endpoint == "messages":
            self._update_global_message_count()

    def _update_global_message_count(self):
        """Update global message counter with window reset"""
        current_time = time.time()

        # Reset window if needed
        if current_time - self.global_window_start >= 60:  # 1 minute window
            self.global_message_count = 0
            self.global_window_start = current_time

        self.global_message_count += 1

        # Check global limit
        if self.global_message_count >= 50:  # Global limit
            logger.warning(
                f"🚨 Approaching global message limit: {self.global_message_count}/50"
            )

    def set_backoff(self, endpoint: str, identifier: str, duration: float):
        """Set backoff period for specific endpoint"""
        key = f"{endpoint}:{identifier}"
        self.backoff_until[key] = time.time() + duration
        self.stats["backoff_events"] += 1
        logger.warning(f"🔄 Setting backoff for {key}: {duration:.1f}s")

    def handle_discord_rate_limit(
        self, retry_after: float, endpoint: str = "messages", identifier: str = "global"
    ):
        """Handle Discord rate limit response"""
        logger.warning(f"🚫 Discord rate limit hit: {retry_after}s retry-after")
        self.set_backoff(endpoint, identifier, retry_after + 1.0)  # Add 1s buffer

    def get_stats(self) -> Dict:
        """Get rate limiter statistics"""
        return {
            **self.stats,
            "active_backoffs": len(
                [k for k, v in self.backoff_until.items() if time.time() < v]
            ),
            "global_message_count": self.global_message_count,
            "window_remaining": max(0, 60 - (time.time() - self.global_window_start)),
        }

    async def smart_delay(self, priority: str = "normal") -> None:
        """Smart delay based on current load and priority"""
        delays = {
            "high": 0.1,  # High priority (security alerts)
            "normal": 0.5,  # Normal priority
            "low": 1.0,  # Low priority (analytics, etc.)
        }

        delay = delays.get(priority, 0.5)

        # Increase delay if we're hitting limits frequently
        if self.stats["requests_delayed"] > 10:
            delay *= 2

        if delay > 0.1:
            await asyncio.sleep(delay)


# Global rate limiter instance
discord_rate_limiter = DiscordRateLimiter()


# Decorator for rate-limited functions
def rate_limited(endpoint: str = "api_general", identifier_func=None):
    """Decorator to apply rate limiting to functions"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Determine identifier
            identifier = "global"
            if identifier_func:
                identifier = identifier_func(*args, **kwargs)
            elif len(args) > 0 and hasattr(args[0], "id"):
                identifier = str(args[0].id)

            # Apply rate limiting
            await discord_rate_limiter.acquire(endpoint, identifier)

            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Check if it's a rate limit error
                if hasattr(e, "status") and e.status == 429:
                    retry_after = getattr(e, "retry_after", 5.0)
                    discord_rate_limiter.handle_discord_rate_limit(
                        retry_after, endpoint, identifier
                    )
                raise

        return wrapper

    return decorator
