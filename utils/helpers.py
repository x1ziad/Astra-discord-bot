"""
Enhanced General Utility Functions for Astra Bot
Provides optimized sync/async utilities with caching and performance improvements
"""

import discord
import re
import json
import asyncio
from datetime import datetime, timezone, timedelta
import traceback
import logging
from typing import Dict, List, Any, Union, Optional, Tuple, Set
import random
from pathlib import Path
import functools
from dataclasses import dataclass
import hashlib

# Optional aiofiles import with fallback
try:
    import aiofiles

    HAS_AIOFILES = True
except ImportError:
    HAS_AIOFILES = False

logger = logging.getLogger("astra.helpers")


# Cache for frequently used calculations
_time_format_cache: Dict[int, str] = {}
_color_cache: Dict[int, discord.Color] = {}
_mention_cache: Dict[str, str] = {}


@dataclass
class FileStats:
    """File operation statistics"""

    reads: int = 0
    writes: int = 0
    errors: int = 0
    cache_hits: int = 0


_file_stats = FileStats()


def format_time(seconds: int) -> str:
    """Format seconds into a human-readable time string with caching"""
    # Check cache first
    if seconds in _time_format_cache:
        return _time_format_cache[seconds]

    if seconds < 60:
        result = f"{seconds} second{'s' if seconds != 1 else ''}"
    elif seconds < 3600:
        minutes, secs = divmod(seconds, 60)
        result = f"{minutes} minute{'s' if minutes != 1 else ''}"
        if secs > 0:
            result += f" {secs} second{'s' if secs != 1 else ''}"
    elif seconds < 86400:
        hours, remainder = divmod(seconds, 3600)
        minutes = remainder // 60
        result = f"{hours} hour{'s' if hours != 1 else ''}"
        if minutes > 0:
            result += f" {minutes} minute{'s' if minutes != 1 else ''}"
    else:
        days, remainder = divmod(seconds, 86400)
        hours = remainder // 3600
        result = f"{days} day{'s' if days != 1 else ''}"
        if hours > 0:
            result += f" {hours} hour{'s' if hours != 1 else ''}"

    # Cache result (limit cache size)
    if len(_time_format_cache) < 1000:
        _time_format_cache[seconds] = result

    return result


def format_datetime(dt: datetime) -> str:
    """Format datetime for display in Discord"""
    timestamp = int(dt.timestamp())
    return f"<t:{timestamp}:F>"


def format_relative_time(dt: datetime) -> str:
    """Format datetime as relative time for Discord"""
    timestamp = int(dt.timestamp())
    return f"<t:{timestamp}:R>"


def format_duration(start: datetime, end: Optional[datetime] = None) -> str:
    """Format duration between two datetimes"""
    if end is None:
        end = datetime.now(timezone.utc)

    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)

    duration = end - start
    return format_time(int(duration.total_seconds()))


def truncate_text(text: str, max_length: int = 2000, suffix: str = "...") -> str:
    """Truncate text to fit within Discord's limits"""
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def smart_truncate(
    text: str, max_length: int = 2000, preserve_words: bool = True
) -> str:
    """Intelligently truncate text preserving word boundaries"""
    if len(text) <= max_length:
        return text

    if not preserve_words:
        return text[: max_length - 3] + "..."

    # Find last space before limit
    truncate_at = max_length - 3
    while truncate_at > max_length // 2 and text[truncate_at] != " ":
        truncate_at -= 1

    if truncate_at <= max_length // 2:
        # No good break point found, hard truncate
        return text[: max_length - 3] + "..."

    return text[:truncate_at].rstrip() + "..."


# Compiled regex patterns for better performance
_markdown_pattern = re.compile(r"[*_~`|]")
_mention_patterns = {
    "user": re.compile(r"<@!?(\d+)>"),
    "role": re.compile(r"<@&(\d+)>"),
    "channel": re.compile(r"<#(\d+)>"),
}


def clean_text(text: str, preserve_mentions: bool = False) -> str:
    """Clean text by removing Markdown formatting and optionally mentions"""
    # Remove Markdown formatting
    text = _markdown_pattern.sub("", text)

    if not preserve_mentions:
        # Remove mentions
        text = _mention_patterns["user"].sub("@user", text)
        text = _mention_patterns["role"].sub("@role", text)
        text = _mention_patterns["channel"].sub("#channel", text)

    return text.strip()


def extract_mentions(text: str) -> Dict[str, List[int]]:
    """Extract all mentions from text"""
    mentions = {
        "users": [int(m) for m in _mention_patterns["user"].findall(text)],
        "roles": [int(m) for m in _mention_patterns["role"].findall(text)],
        "channels": [int(m) for m in _mention_patterns["channel"].findall(text)],
    }
    return mentions


async def load_json_file_async(filepath: Union[str, Path]) -> Dict[str, Any]:
    """Async load JSON data from file with error handling"""
    filepath = Path(filepath)

    if not HAS_AIOFILES:
        # Fallback to sync version in thread executor
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, load_json_file, filepath)

    try:
        async with aiofiles.open(filepath, "r", encoding="utf-8") as f:
            content = await f.read()
            _file_stats.reads += 1
            return json.loads(content)
    except FileNotFoundError:
        logger.debug(f"File not found: {filepath}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filepath}: {e}")
        _file_stats.errors += 1
        return {}
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        _file_stats.errors += 1
        return {}


def load_json_file(filepath: Union[str, Path]) -> Dict[str, Any]:
    """Sync load JSON data from file with error handling"""
    filepath = Path(filepath)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            _file_stats.reads += 1
            return json.load(f)
    except FileNotFoundError:
        logger.debug(f"File not found: {filepath}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filepath}: {e}")
        _file_stats.errors += 1
        return {}
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        _file_stats.errors += 1
        return {}


async def save_json_file_async(
    filepath: Union[str, Path],
    data: Dict[str, Any],
    indent: int = 2,
    ensure_dir: bool = True,
) -> bool:
    """Async save data to JSON file with error handling"""
    filepath = Path(filepath)

    if not HAS_AIOFILES:
        # Fallback to sync version in thread executor
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, save_json_file, filepath, data, indent, ensure_dir
        )

    try:
        if ensure_dir:
            filepath.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(filepath, "w", encoding="utf-8") as f:
            content = json.dumps(data, indent=indent, ensure_ascii=False)
            await f.write(content)
            _file_stats.writes += 1
            return True
    except Exception as e:
        logger.error(f"Error saving to {filepath}: {e}")
        _file_stats.errors += 1
        return False


def save_json_file(
    filepath: Union[str, Path],
    data: Dict[str, Any],
    indent: int = 2,
    ensure_dir: bool = True,
) -> bool:
    """Sync save data to JSON file with error handling"""
    filepath = Path(filepath)

    try:
        if ensure_dir:
            filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
            _file_stats.writes += 1
            return True
    except Exception as e:
        logger.error(f"Error saving to {filepath}: {e}")
        _file_stats.errors += 1
        return False


# Predefined color palette for better performance
_color_palette = [
    discord.Color.blue(),
    discord.Color.green(),
    discord.Color.red(),
    discord.Color.purple(),
    discord.Color.orange(),
    discord.Color.gold(),
    discord.Color.teal(),
    discord.Color.magenta(),
]


def get_random_color(seed: Optional[int] = None) -> discord.Color:
    """Get a random Discord color with optional seeding"""
    if seed is not None:
        # Use seed for consistent colors
        if seed in _color_cache:
            return _color_cache[seed]

        # Generate deterministic color
        random.seed(seed)
        color = discord.Color.from_rgb(
            random.randint(100, 255),  # Avoid too dark colors
            random.randint(100, 255),
            random.randint(100, 255),
        )
        random.seed()  # Reset seed

        if len(_color_cache) < 500:
            _color_cache[seed] = color
        return color

    # Return random color from palette or generate new one
    if random.random() < 0.7:  # 70% chance to use palette
        return random.choice(_color_palette)
    else:
        return discord.Color.from_rgb(
            random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)
        )


def get_dominant_role_color(member: discord.Member) -> discord.Color:
    """Get the dominant role color for a member with caching"""
    cache_key = f"{member.guild.id}:{member.id}"

    if cache_key in _color_cache:
        return _color_cache[cache_key]

    if not member.roles[1:]:  # No roles except @everyone
        color = discord.Color.default()
    else:
        # Find highest colored role
        roles_with_color = [
            role for role in member.roles if role.color != discord.Color.default()
        ]

        if not roles_with_color:
            color = discord.Color.default()
        else:
            color = max(roles_with_color, key=lambda r: r.position).color

    # Cache result
    if len(_color_cache) < 1000:
        _color_cache[cache_key] = color

    return color


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp value between minimum and maximum"""
    return max(minimum, min(value, maximum))


def format_number(num: Union[int, float], precision: int = 0) -> str:
    """Format a number with commas and optional precision"""
    if isinstance(num, float) and precision > 0:
        return f"{num:,.{precision}f}"
    return f"{int(num):,}"


def format_bytes(bytes_count: int) -> str:
    """Format bytes into human readable format"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} PB"


def format_percentage(value: float, total: float, precision: int = 1) -> str:
    """Format value as percentage of total"""
    if total == 0:
        return "0.0%"
    percentage = (value / total) * 100
    return f"{percentage:.{precision}f}%"


# Enhanced time parsing with more formats
_time_units = {
    "s": 1,
    "sec": 1,
    "second": 1,
    "seconds": 1,
    "m": 60,
    "min": 60,
    "minute": 60,
    "minutes": 60,
    "h": 3600,
    "hr": 3600,
    "hour": 3600,
    "hours": 3600,
    "d": 86400,
    "day": 86400,
    "days": 86400,
    "w": 604800,
    "week": 604800,
    "weeks": 604800,
    "mo": 2592000,
    "month": 2592000,
    "months": 2592000,
    "y": 31536000,
    "year": 31536000,
    "years": 31536000,
}


def parse_time_string(time_str: str) -> int:
    """Parse a time string (e.g., '1h30m', '2 days', '1 week 3 days') into seconds"""
    if not time_str:
        return 0

    total_seconds = 0
    time_str = time_str.lower().strip()

    # Handle formats like "1h30m" or "2d 3h 30m"
    # First try compact format (1h30m)
    compact_pattern = r"(\d+(?:\.\d+)?)([a-z]+)"
    matches = re.findall(compact_pattern, time_str)

    if matches:
        for value_str, unit in matches:
            value = float(value_str)
            if unit in _time_units:
                total_seconds += value * _time_units[unit]
    else:
        # Try spaced format (2 days 3 hours)
        spaced_pattern = r"(\d+(?:\.\d+)?)\s*([a-z]+)"
        matches = re.findall(spaced_pattern, time_str)

        for value_str, unit in matches:
            value = float(value_str)
            # Handle plural forms
            unit = unit.rstrip("s")
            if unit in _time_units:
                total_seconds += value * _time_units[unit]

    return int(total_seconds)


def get_channel_mention(channel_id: int) -> str:
    """Convert a channel ID to a channel mention with caching"""
    cache_key = f"channel:{channel_id}"
    if cache_key in _mention_cache:
        return _mention_cache[cache_key]

    mention = f"<#{channel_id}>"
    if len(_mention_cache) < 1000:
        _mention_cache[cache_key] = mention
    return mention


def get_user_mention(user_id: int) -> str:
    """Convert a user ID to a user mention with caching"""
    cache_key = f"user:{user_id}"
    if cache_key in _mention_cache:
        return _mention_cache[cache_key]

    mention = f"<@{user_id}>"
    if len(_mention_cache) < 1000:
        _mention_cache[cache_key] = mention
    return mention


def get_role_mention(role_id: int) -> str:
    """Convert a role ID to a role mention with caching"""
    cache_key = f"role:{role_id}"
    if cache_key in _mention_cache:
        return _mention_cache[cache_key]

    mention = f"<@&{role_id}>"
    if len(_mention_cache) < 1000:
        _mention_cache[cache_key] = mention
    return mention


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size"""
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_dict_get(d: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Safely get nested dictionary value using dot notation"""
    keys = path.split(".")
    value = d

    try:
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    except (KeyError, TypeError):
        return default


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries, later ones override earlier ones"""
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result


def generate_hash(text: str, length: int = 8) -> str:
    """Generate a short hash from text"""
    return hashlib.md5(text.encode()).hexdigest()[:length]


def fuzzy_match(text: str, candidates: List[str], threshold: float = 0.6) -> List[str]:
    """Simple fuzzy matching for text"""
    text_lower = text.lower()
    matches = []

    for candidate in candidates:
        candidate_lower = candidate.lower()

        # Exact match
        if text_lower == candidate_lower:
            matches.append(candidate)
            continue

        # Contains match
        if text_lower in candidate_lower or candidate_lower in text_lower:
            matches.append(candidate)
            continue

        # Simple similarity check
        common_chars = set(text_lower) & set(candidate_lower)
        similarity = len(common_chars) / max(len(text_lower), len(candidate_lower))

        if similarity >= threshold:
            matches.append(candidate)

    return matches


def get_file_stats() -> Dict[str, int]:
    """Get file operation statistics"""
    return {
        "reads": _file_stats.reads,
        "writes": _file_stats.writes,
        "errors": _file_stats.errors,
        "cache_hits": _file_stats.cache_hits,
    }


def clear_caches():
    """Clear all internal caches"""
    global _time_format_cache, _color_cache, _mention_cache
    _time_format_cache.clear()
    _color_cache.clear()
    _mention_cache.clear()
    logger.info("Helper function caches cleared")


# Async context manager for file operations
class AsyncFileManager:
    """Context manager for async file operations with automatic cleanup"""

    def __init__(
        self, filepath: Union[str, Path], mode: str = "r", encoding: str = "utf-8"
    ):
        self.filepath = Path(filepath)
        self.mode = mode
        self.encoding = encoding
        self.file = None

    async def __aenter__(self):
        if not HAS_AIOFILES:
            raise RuntimeError(
                "aiofiles not available, use sync file operations instead"
            )

        try:
            self.file = await aiofiles.open(
                self.filepath, self.mode, encoding=self.encoding
            )
            return self.file
        except Exception as e:
            logger.error(f"Failed to open file {self.filepath}: {e}")
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            await self.file.close()


# Performance decorator
def timed_function(func):
    """Decorator to time function execution"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = datetime.now()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = datetime.now() - start
            logger.debug(
                f"Function {func.__name__} took {duration.total_seconds():.3f}s"
            )

    return wrapper


# Backwards compatibility aliases
load_json = load_json_file
save_json = save_json_file
