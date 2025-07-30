"""
Enhanced Astra Discord Bot - Main Launcher with Debug Logging
"""

import discord
from discord.ext import commands, tasks
import os
import asyncio
import logging
import sys
import traceback
from dotenv import load_dotenv
from datetime import datetime
import json
from pathlib import Path

print("🔍 Starting bot with debug logging...")

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

print(f"🔍 TOKEN exists: {bool(TOKEN)}")
print(f"🔍 TOKEN length: {len(TOKEN) if TOKEN else 0}")

# Import our custom modules with error handling
try:
    from enhanced_config import config_manager, require_permission, feature_enabled
    print("✅ Successfully imported enhanced_config")
except ImportError as e:
    print(f"❌ Failed to import enhanced_config: {e}")
    sys.exit(1)

try:
    from ui_components import *
    print("✅ Successfully imported ui_components")
except ImportError as e:
    print(f"❌ Failed to import ui_components: {e}")
    sys.exit(1)

try:
    from logger import setup_logger
    print("✅ Successfully imported logger")
except ImportError as e:
    print(f"❌ Failed to import logger: {e}")
    sys.exit(1)

# Setup enhanced logging
try:
    logger = setup_logger(
        "Astra", config_manager.get("development.debug_mode", False) and "DEBUG" or "INFO"
    )
    print("✅ Logger setup successful")
except Exception as e:
    print(f"❌ Logger setup failed: {e}")
    # Fallback to basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

# Bot configuration with enhanced intents
intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix=config_manager.get("bot_settings.prefix", "!"),
    intents=intents,
    help_command=None,
    case_insensitive=True,
    description=config_manager.get(
        "bot_settings.description", "Astra - Space exploration bot"
    ),
)

print("✅ Bot instance created")

# Store bot start time for uptime tracking
bot.start_time = datetime.utcnow()
bot.config = config_manager

# Define extensions to load
extensions = [
    "cogs.quiz",
    "cogs.roles",
    "cogs.space",
    "cogs.notion",
    "cogs.stats",
    "cogs.admin",
    "cogs.user_profiles",
]

# Global cache for user data and other frequently accessed info
bot.user_cache = {}
bot.guild_cache = {}

print("✅ Bot configuration complete")

async def load_extensions():
    """Load all cogs with enhanced error handling and logging"""
    loaded_count = 0
    failed_count = 0

    for ext in extensions:
        try:
            await bot.load_extension(ext)
            logger.info(f"✅ Loaded extension: {ext}")
            print(f"✅ Loaded extension: {ext}")
            loaded_count += 1
        except FileNotFoundError:
            logger.warning(f"⚠️ Extension not found: {ext} - skipping")
            print(f"⚠️ Extension not found: {ext} - skipping")
        except Exception as e:
            logger.error(f"❌ Failed to load {ext}: {e}")
            print(f"❌ Failed to load {ext}: {e}")
            traceback.print_exc()
            failed_count += 1

    logger.info(
        f"🎯 Extension loading complete: {loaded_count} loaded, {failed_count} failed"
    )
    print(f"🎯 Extension loading complete: {loaded_count} loaded, {failed_count} failed")

@bot.event
async def on_ready():
    """Enhanced bot startup event with configuration validation"""
    print("🚀 Bot on_ready event triggered")
    logger.info("=" * 60)
    logger.info(
        f"🚀 {config_manager.get('bot_settings.name', 'Astra')} is initializing..."
    )

    # Validate configuration
    try:
        config_errors = config_manager.validate_config()
        if config_errors:
            logger.error("❌ Configuration errors found:")
            for error in config_errors:
                logger.error(f"   - {error}")
            return
        print("✅ Configuration validation passed")
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        logger.error(f"Configuration validation error: {e}")

    # Ensure required directories exist
    try:
        config_manager.ensure_directories()
        print("✅ Directories ensured")
    except Exception as e:
        print(f"❌ Directory creation failed: {e}")
        logger.error(f"Directory creation error: {e}")

    # Bot information
    logger.info(f"🤖 Bot: {bot.user} (ID: {bot.user.id})")
    logger.info(f"🌐 Connected to {len(bot.guilds)} guild(s)")
    print(f"🤖 Bot: {bot.user} (ID: {bot.user.id})")
    print(f"🌐 Connected to {len(bot.guilds)} guild(s)")

    total_members = len(set(bot.get_all_members()))
    logger.info(f"👥 Serving {total_members} unique users")
    print(f"👥 Serving {total_members} unique users")

    # Load extensions
    try:
        await load_extensions()
        print("✅ Extensions loading completed")
    except Exception as e:
        print(f"❌ Extension loading failed: {e}")
        logger.error(f"Extension loading error: {e}")
        traceback.print_exc()

    # Load guild configurations
    try:
        for guild in bot.guilds:
            config_manager.load_guild_config(guild.id)
            logger.info(f"📋 Loaded config for guild: {guild.name}")
        print("✅ Guild configurations loaded")
    except Exception as e:
        print(f"❌ Guild config loading failed: {e}")
        logger.error(f"Guild config loading error: {e}")

    # Set bot activity
    try:
        activity_text = config_manager.get("bot_settings.activity", "the cosmos | !help")
        activity = discord.Activity(type=discord.ActivityType.watching, name=activity_text)
        await bot.change_presence(activity=activity)
        print("✅ Bot activity set")
    except Exception as e:
        print(f"❌ Activity setting failed: {e}")
        logger.error(f"Activity setting error: {e}")

    # Start background tasks
    try:
        if config_manager.is_feature_enabled("space_content.daily_apod"):
            if 'daily_apod_task' in globals():
                daily_apod_task.start()
                print("✅ Daily APOD task started")
            else:
                print("⚠️ daily_apod_task not defined, skipping")

        if config_manager.is_feature_enabled("quiz_system.daily_questions"):
            if 'daily_quiz_reminder' in globals():
                daily_quiz_reminder.start()
                print("✅ Daily quiz reminder started")
            else:
                print("⚠️ daily_quiz_reminder not defined, skipping")
    except Exception as e:
        print(f"❌ Background task startup failed: {e}")
        logger.error(f"Background task error: {e}")

    logger.info("🎯 All systems operational!")
    print("🎯 All systems operational!")
    logger.info("=" * 60)

@bot.event
async def on_guild_join(guild):
    """Handle bot joining a new guild"""
    logger.info(
        f"🏛️ Joined new guild: {guild.name} (ID: {guild.id}, Members: {guild.member_count})"
    )
    print(f"🏛️ Joined new guild: {guild.name}")

    # Load/create guild configuration
    try:
        config_manager.load_guild_config(guild.id)
    except Exception as e:
        logger.error(f"Failed to load guild config: {e}")

    # Send welcome message if possible
    if (
        guild.system_channel
        and guild.system_channel.permissions_for(guild.me).send_messages
    ):
        try:
            embed = discord.Embed(
                title="🚀 Astra Has Arrived!",
                description=f"Thank you for adding **{config_manager.get('bot_settings.name')}** to {guild.name}!",
                color=config_manager.get_color("primary"),
            )
            await guild.system_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Failed to send welcome message: {e}")

@bot.event
async def on_command_error(ctx, error):
    """Enhanced global error handler with user-friendly messages"""
    # Don't handle errors for commands that have their own error handlers
    if hasattr(ctx.command, "on_error"):
        return

    error = getattr(error, "original", error)
    
    # Log all errors for debugging
    logger.error(f"Command error: {error}")
    print(f"❌ Command error: {error}")

    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="❌ Command Not Found",
            description=f"The command `{ctx.invoked_with}` doesn't exist.\nUse `{ctx.prefix}help` to see available commands.",
            color=0xff0000,
        )
        await ctx.send(embed=embed, delete_after=10)
    else:
        # Send generic error message
        embed = discord.Embed(
            title="❌ Something Went Wrong",
            description="An error occurred. The error has been logged.",
            color=0xff0000,
        )
        await ctx.send(embed=embed, delete_after=15)

@bot.command(name="test")
async def test_command(ctx):
    """Test command to verify bot is working"""
    embed = discord.Embed(
        title="✅ Bot Test",
        description="Bot is working correctly!",
        color=0x00ff00,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="Latency", value=f"{bot.latency * 1000:.2f}ms", inline=True)
    embed.add_field(name="Guilds", value=len(bot.guilds), inline=True)
    await ctx.send(embed=embed)

if __name__ == "__main__":
    print("🔍 Checking token...")
    if not TOKEN:
        print("❌ DISCORD_TOKEN not found in environment variables!")
        logger.error("❌ DISCORD_TOKEN not found in environment variables!")
        exit(1)
    
    print("✅ Token found, starting bot...")
    
    try:
        print("🚀 Calling bot.run()...")
        bot.run(TOKEN, log_handler=None)  # Disable discord.py's default logging
    except discord.LoginFailure:
        print("❌ Invalid bot token!")
        logger.error("❌ Invalid bot token!")
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        logger.error(f"❌ Failed to start bot: {e}")
        traceback.print_exc()


# this code for debugging purposes only        