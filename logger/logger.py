"""
Enhanced logging system for Astra Bot
Provides colored console output and file logging
"""

import logging
import colorlog
from pathlib import Path
from datetime import datetime
import sys
import os


class AstraLogger:
    """Custom logger class for Astra bot"""

    def __init__(self, name="Astra", log_level="INFO", log_file="data/logs/astra.log"):
        self.name = name
        self.log_level = getattr(logging, log_level.upper())
        self.log_file = Path(log_file)

        # Ensure logs directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)

        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # Setup handlers
        self._setup_console_handler()
        self._setup_file_handler()

    def _setup_console_handler(self):
        """Setup colored console logging"""
        console_handler = colorlog.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)

        # Color formatter
        color_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s %(levelname)-8s %(name)s: %(message)s",
            datefmt="%H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )

        console_handler.setFormatter(color_formatter)
        self.logger.addHandler(console_handler)

    def _setup_file_handler(self):
        """Setup file logging"""
        file_handler = logging.FileHandler(self.log_file, encoding="utf-8", mode="a")
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file

        # File formatter (no colors)
        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

    def get_logger(self):
        """Get the configured logger"""
        return self.logger

    def log_bot_start(self, bot_name, version):
        """Log bot startup information"""
        separator = "=" * 60
        self.logger.info(separator)
        self.logger.info(f"🚀 Starting {bot_name} v{version}")
        self.logger.info(
            f"📅 Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        self.logger.info(f"🐍 Python version: {sys.version.split()[0]}")
        self.logger.info(f"📁 Working directory: {os.getcwd()}")
        self.logger.info(separator)


# Global logger function
def setup_logger(name="Astra", log_level="INFO", log_file="data/logs/astra.log"):
    """Setup and return a logger instance"""
    logger_instance = AstraLogger(name, log_level, log_file)
    return logger_instance.get_logger()


# Performance decorator
def log_performance(logger):
    """Decorator to log function execution time"""

    def decorator(func):
        import functools
        import time

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.debug(f"⚡ {func.__name__} executed in {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"💥 {func.__name__} failed after {execution_time:.3f}s: {e}"
                )
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.debug(f"⚡ {func.__name__} executed in {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"💥 {func.__name__} failed after {execution_time:.3f}s: {e}"
                )
                raise

        if (
            hasattr(func, "__code__") and func.__code__.co_flags & 0x80
        ):  # Check if coroutine
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
