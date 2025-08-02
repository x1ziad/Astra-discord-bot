"""
Logger utilities for Astra Bot
Provides performance logging and other logging utilities
"""

import logging
import time
import functools
from typing import Callable, Any
from datetime import datetime

logger = logging.getLogger("astra.performance")


def log_performance(func_name: str = None):
    """Decorator to log function performance"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            name = func_name or f"{func.__module__}.{func.__name__}"

            try:
                result = await func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                logger.debug(f"⚡ {name} executed in {execution_time:.2f}ms")
                return result
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                logger.error(f"❌ {name} failed after {execution_time:.2f}ms: {e}")
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            name = func_name or f"{func.__module__}.{func.__name__}"

            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                logger.debug(f"⚡ {name} executed in {execution_time:.2f}ms")
                return result
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                logger.error(f"❌ {name} failed after {execution_time:.2f}ms: {e}")
                raise

        # Return appropriate wrapper based on whether function is async
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def log_command_usage(command_name: str, user_id: int, guild_id: int = None):
    """Log command usage for analytics"""
    timestamp = datetime.utcnow().isoformat()
    guild_info = f" in guild {guild_id}" if guild_id else " in DM"
    logger.info(
        f"📊 Command '{command_name}' used by user {user_id}{guild_info} at {timestamp}"
    )


def log_error(error: Exception, context: str = ""):
    """Log error with context"""
    context_info = f" ({context})" if context else ""
    logger.error(f"❌ Error{context_info}: {type(error).__name__}: {error}")


def log_api_request(
    api_name: str, endpoint: str, response_time: float, status_code: int = None
):
    """Log API request performance"""
    status_info = f" [{status_code}]" if status_code else ""
    logger.info(f"🌐 {api_name} API: {endpoint} - {response_time:.2f}ms{status_info}")
