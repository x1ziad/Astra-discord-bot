"""
General utility functions for Astra Bot
"""

import discord
import re
import json
from datetime import datetime, timezone
import traceback
from typing import Dict, List, Any, Union, Optional
import random


def format_time(seconds: int) -> str:
    """Format seconds into a human-readable time string"""
    if seconds < 60:
        return f"{seconds} second{'s' if seconds != 1 else ''}"

    minutes, seconds = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''} {seconds} second{'s' if seconds != 1 else ''}"

    hours, minutes = divmod(minutes, 60)
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"

    days, hours = divmod(hours, 24)
    return (
        f"{days} day{'s' if days != 1 else ''} {hours} hour{'s' if hours != 1 else ''}"
    )


def format_datetime(dt: datetime) -> str:
    """Format datetime for display in Discord"""
    timestamp = int(dt.timestamp())
    return f"<t:{timestamp}:F>"


def format_relative_time(dt: datetime) -> str:
    """Format datetime as relative time for Discord"""
    timestamp = int(dt.timestamp())
    return f"<t:{timestamp}:R>"


def truncate_text(text: str, max_length: int = 2000, suffix: str = "...") -> str:
    """Truncate text to fit within Discord's limits"""
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def clean_text(text: str) -> str:
    """Clean text by removing Markdown formatting and mentions"""
    # Remove Markdown formatting
    text = re.sub(r"[*_~`|]", "", text)
    # Remove mentions
    text = re.sub(r"<@!?[0-9]+>", "@user", text)
    text = re.sub(r"<@&[0-9]+>", "@role", text)
    text = re.sub(r"<#[0-9]+>", "#channel", text)

    return text


def load_json_file(filepath: str) -> Dict:
    """Load JSON data from file with error handling"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print(f"Error: {filepath} contains invalid JSON")
        return {}
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        traceback.print_exc()
        return {}


def save_json_file(filepath: str, data: Dict) -> bool:
    """Save data to JSON file with error handling"""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving to {filepath}: {e}")
        traceback.print_exc()
        return False


def get_random_color() -> discord.Color:
    """Get a random Discord color"""
    return discord.Color.from_rgb(
        random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
    )


def get_dominant_role_color(member: discord.Member) -> discord.Color:
    """Get the dominant role color for a member"""
    if not member.roles[1:]:  # No roles except @everyone
        return discord.Color.default()

    # Find highest colored role
    roles_with_color = [
        role for role in member.roles if role.color != discord.Color.default()
    ]

    if not roles_with_color:
        return discord.Color.default()

    return max(roles_with_color, key=lambda r: r.position).color


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp value between minimum and maximum"""
    return max(minimum, min(value, maximum))


def format_number(num: int) -> str:
    """Format a number with commas as thousands separators"""
    return f"{num:,}"


def parse_time_string(time_str: str) -> int:
    """Parse a time string (e.g., '1h30m') into seconds"""
    total_seconds = 0

    # Find all time components (e.g., 1d, 2h, 30m, 45s)
    time_components = re.findall(r"(\d+)([dhms])", time_str.lower())

    for value, unit in time_components:
        value = int(value)
        if unit == "d":
            total_seconds += value * 86400  # days to seconds
        elif unit == "h":
            total_seconds += value * 3600  # hours to seconds
        elif unit == "m":
            total_seconds += value * 60  # minutes to seconds
        elif unit == "s":
            total_seconds += value  # seconds

    return total_seconds


def get_channel_mention(channel_id: int) -> str:
    """Convert a channel ID to a channel mention"""
    return f"<#{channel_id}>"


def get_user_mention(user_id: int) -> str:
    """Convert a user ID to a user mention"""
    return f"<@{user_id}>"


def get_role_mention(role_id: int) -> str:
    """Convert a role ID to a role mention"""
    return f"<@&{role_id}>"
