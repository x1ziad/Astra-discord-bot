"""
Enhanced logging system for Astra Bot
Provides structured logging with file rotation and performance monitoring
"""

import asyncio
import logging
import logging.handlers
import sys
import time
import traceback
import functools
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    import colorlog

    COLORLOG_AVAILABLE = True
except ImportError:
    COLORLOG_AVAILABLE = False


class AstraFormatter(logging.Formatter):
    """Custom formatter for Astra Bot"""

    def __init__(self, include_colors: bool = False):
        self.include_colors = include_colors and COLORLOG_AVAILABLE

        if self.include_colors:
            # Colored format for console
            self.formatter = colorlog.ColoredFormatter(
                "%(log_color)s%(asctime)s | %(levelname)-8s | %(name)-15s | %(funcName)-20s:%(lineno)-4d | %(message)s",
                datefmt="%H:%M:%S",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                },
            )
        else:
            # Plain format for files
            super().__init__(
                "%(asctime)s | %(levelname)-8s | %(name)-15s | %(funcName)-20s:%(lineno)-4d | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

    def format(self, record):
        if self.include_colors:
            return self.formatter.format(record)
        else:
            return super().format(record)


def setup_enhanced_logger(
    name: str = "Astra",
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> logging.Logger:
    """Set up enhanced logger with file rotation and console output"""

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers to prevent duplicates
    logger.handlers.clear()

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(AstraFormatter(include_colors=True))
    logger.addHandler(console_handler)

    # File handler with rotation
    if log_file is None:
        log_file = f"logs/{name.lower()}.log"

    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.handlers.RotatingFileHandler(
        log_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(AstraFormatter(include_colors=False))
    logger.addHandler(file_handler)

    # Error file handler (errors only)
    error_file = log_path.parent / f"{log_path.stem}_errors.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(AstraFormatter(include_colors=False))
    logger.addHandler(error_handler)

    # Log startup info
    logger.info(f"Enhanced logger initialized for {name}")
    logger.info(f"Log level: {log_level}")
    logger.info(f"Log file: {log_path}")

    return logger


def log_performance(logger: logging.Logger):
    """Decorator to log function execution time and performance"""

    def decorator(func):
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
                    f"❌ {func.__name__} failed after {execution_time:.3f}s: {e}"
                )
                logger.debug(traceback.format_exc())
                raise
## for a new 
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
                    f"❌ {func.__name__} failed after {execution_time:.3f}s: {e}"
                )
                logger.debug(traceback.format_exc())
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator
