"""
Astra Discord Bot - Main Application File
A Discord bot for space exploration and Stellaris roleplay
"""

import asyncio
import logging
import os
import platform
import signal
import sys
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# Import configuration manager
from config.config_manager import config_manager

# Load environment variables from .env file if it exists
load_dotenv()

# Create necessary directories
Path("logs").mkdir(exist_ok=True)
Path("data").mkdir(exist_ok=True)
Path("data/space").mkdir(exist_ok=True)
Path("data/quiz").mkdir(exist_ok=True)
Path("data/guilds").mkdir(exist_ok=True)


class AstraBot(commands.Bot):
    """Custom Discord bot class with enhanced functionality"""

    def __init__(self):
        # Set up intents
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.presences = True

        # Initialize the bot with command prefix and intents
        super().__init__(
            command_prefix=config_manager.get("bot_settings.prefix", "/"),
            intents=intents,
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="the stars"
            ),
            status=discord.Status.online,
            allowed_mentions=discord.AllowedMentions(
                everyone=False, roles=False, users=True, replied_user=True
            ),
        )

        # Store configuration and start time
        self.config = config_manager
        self.start_time = datetime.utcnow()

        # Store running tasks for cleanup
        self._tasks: Set[asyncio.Task] = set()

        # Set up logging
        self.setup_logging()
        self.logger = logging.getLogger("Astra")

        # Get username in a container-friendly way
        try:
            # Try different methods to get username, with fallbacks
            username = os.environ.get("USER") or os.environ.get("USERNAME") or "unknown"
            # Only try getlogin as last resort since it often fails in containers
            if username == "unknown":
                try:
                    username = os.getlogin()
                except:
                    pass
        except Exception:
            username = "unknown"

        self.logger.info(
            f"Bot startup initiated by {username} at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        self.logger.info(f"Loading configuration from {config_manager.config_path}")

        # Remove default help command to use custom one
        self.remove_command("help")

        # Register bot events
        self.setup_events()

    def setup_logging(self):
        """Set up logging configuration"""
        # Create logs directory if it doesn't exist
        Path("logs").mkdir(exist_ok=True)

        # Configure the root logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        # Log format
        log_format = logging.Formatter(
            "%(asctime)s %(levelname)-8s %(name)s: %(message)s", datefmt="%H:%M:%S"
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)
        logger.addHandler(console_handler)

        # File handler (rotating)
        file_handler = RotatingFileHandler(
            filename="logs/bot.log",
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)
