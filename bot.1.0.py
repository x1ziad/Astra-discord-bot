"""
Enhanced Astra Discord Bot - Main Launcher
Integrates configuration management, UI components, and role-based permissions
"""

import discord
from discord.ext import commands, tasks
import os
import asyncio
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json
from pathlib import Path

# Import our custom modules
from enhanced_config import config_manager, require_permission, feature_enabled, require_channel
from ui_components import *
from logger import setup_logger

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Setup enhanced logging
logger = setup_logger(
    "Astra", config_manager.get("development.debug_mode", False) and "DEBUG" or "INFO"
)

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
    "cogs.admin",  # New admin cog
    "cogs.user_profiles",  # New user system cog
]

# Global cache for user data and other frequently accessed info
bot.user_cache = {}
bot.guild_cache = {}


async def load_extensions():
    """Load all cogs with enhanced error handling and logging"""
    loaded_count = 0
    failed_count = 0

    for ext in extensions:
        try:
            await bot.load_extension(ext)
            logger.info(f"✅ Loaded extension: {ext}")
            loaded_count += 1
        except FileNotFoundError:
            logger.warning(f"⚠️ Extension not found: {ext} - skipping")
        except Exception as e:
            logger.error(f"❌ Failed to load {ext}: {e}")
            failed_count += 1

    logger.info(
        f"🎯 Extension loading complete: {loaded_count} loaded, {failed_count} failed"
    )

# Task definitions
@tasks.loop(time=datetime.time(hour=12, minute=0))  # Runs at 12:00 UTC every day
async def daily_apod_task():
    """Task to post daily astronomy picture"""
    logger.info("🚀 Running daily APOD task")
    for guild_id, guild_config in bot.config.guild_configs.items():
        if not bot.config.get_guild_setting(guild_id, "features.space_content.daily_apod", False):
            continue
            
        channel_id = bot.config.get_guild_setting(guild_id, "channels.space_channel", None)
        if not channel_id:
            continue
            
        try:
            channel = bot.get_channel(int(channel_id))
            if not channel:
                continue
                
            # This would call a function from space cog to get APOD
            # For now, just send placeholder
            embed = discord.Embed(
                title="🌌 Astronomy Picture of the Day",
                description="Today's featured space image from NASA",
                color=bot.config.get_color("space")
            )
            
            await channel.send(embed=embed)
            logger.info(f"✅ Posted APOD in guild {guild_id}")
        except Exception as e:
            logger.error(f"❌ Error posting APOD in guild {guild_id}: {e}")


@tasks.loop(time=datetime.time(hour=15, minute=0))  # Runs at 15:00 UTC every day
async def daily_quiz_reminder():
    """Task to post daily quiz reminders"""
    logger.info("🎮 Running daily quiz reminder task")
    for guild_id, guild_config in bot.config.guild_configs.items():
        if not bot.config.get_guild_setting(guild_id, "features.quiz_system.daily_questions", False):
            continue
            
        channel_id = bot.config.get_guild_setting(guild_id, "channels.quiz_channel", None)
        if not channel_id:
            continue
            
        try:
            channel = bot.get_channel(int(channel_id))
            if not channel:
                continue
                
            embed = discord.Embed(
                title="🎯 Daily Quiz Available!",
                description="Today's quiz is now available! Use `!quiz` to test your knowledge.",
                color=bot.config.get_color("primary")
            )
            
            await channel.send(embed=embed)
            logger.info(f"✅ Posted quiz reminder in guild {guild_id}")
        except Exception as e:
            logger.error(f"❌ Error posting quiz reminder in guild {guild_id}: {e}")


@bot.event
async def on_ready():
    """Enhanced bot startup event with configuration validation"""
    logger.info("=" * 60)
    logger.info(
        f"🚀 {config_manager.get('bot_settings.name', 'Astra')} is initializing..."
    )

    # Validate configuration
    config_errors = config_manager.validate_config()
    if config_errors:
        logger.error("❌ Configuration errors found:")
        for error in config_errors:
            logger.error(f"   - {error}")
        return

    # Ensure required directories exist
    config_manager.ensure_directories()

    # Bot information
    logger.info(f"🤖 Bot: {bot.user} (ID: {bot.user.id})")
    logger.info(f"🌐 Connected to {len(bot.guilds)} guild(s)")

    total_members = len(set(bot.get_all_members()))
    logger.info(f"👥 Serving {total_members} unique users")

    # Load extensions
    await load_extensions()

    # Load guild configurations
    for guild in bot.guilds:
        config_manager.load_guild_config(guild.id)
        logger.info(f"📋 Loaded config for guild: {guild.name}")

    # Set bot activity
    activity_text = config_manager.get("bot_settings.activity", "the cosmos | !help")
    activity = discord.Activity(type=discord.ActivityType.watching, name=activity_text)
    await bot.change_presence(activity=activity)

    # Start background tasks
    if config_manager.is_feature_enabled("space_content.daily_apod"):
        if not daily_apod_task.is_running():
            daily_apod_task.start()

    if config_manager.is_feature_enabled("quiz_system.daily_questions"):
        if not daily_quiz_reminder.is_running():
            daily_quiz_reminder.start()

    logger.info("🎯 All systems operational!")
    logger.info("=" * 60)


@bot.event
async def on_guild_join(guild):
    """Handle bot joining a new guild"""
    logger.info(
        f"🏛️ Joined new guild: {guild.name} (ID: {guild.id}, Members: {guild.member_count})"
    )

    # Load/create guild configuration
    config_manager.load_guild_config(guild.id)

    # Send welcome message if possible
    if (
        guild.system_channel
        and guild.system_channel.permissions_for(guild.me).send_messages
    ):
        embed = discord.Embed(
            title="🚀 Astra Has Arrived!",
            description=f"Thank you for adding **{config_manager.get('bot_settings.name')}** to {guild.name}!\n\n"
            "I'm here to help with space content, Stellaris gameplay, and interactive quizzes.",
            color=config_manager.get_color("primary"),
        )

        embed.add_field(
            name="🎯 Getting Started",
            value="• Use `!help` to see all commands\n"
            "• Use `!setup` to configure the bot\n"
            "• Use `!empire` to choose your Stellaris role",
            inline=False,
        )

        embed.add_field(
            name="🔧 Setup Required",
            value="Administrators should run `!setup` to configure channels and permissions.",
            inline=False,
        )

        embed.set_footer(text="May your journey among the stars be prosperous! ⭐")

        try:
            await guild.system_channel.send(embed=embed)
        except discord.Forbidden:
            logger.warning(
                f"Cannot send welcome message in {guild.name} - no permissions"
            )


@bot.event
async def on_guild_remove(guild):
    """Handle bot leaving a guild"""
    logger.info(f"🏛️ Left guild: {guild.name} (ID: {guild.id})")

    # Clean up guild cache
    if guild.id in bot.guild_cache:
        del bot.guild_cache[guild.id]


@bot.event
async def on_command_error(ctx, error):
    """Enhanced global error handler with user-friendly messages"""
    # Don't handle errors for commands that have their own error handlers
    if hasattr(ctx.command, "on_error"):
        return

    error = getattr(error, "original", error)

    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title=f"{config_manager.get_emoji('error')} Command Not Found",
            description=f"The command `{ctx.invoked_with}` doesn't exist.\nUse `{ctx.prefix}help` to see available commands.",
            color=config_manager.get_color("error"),
        )
        await ctx.send(embed=embed, delete_after=10)

    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title=f"{config_manager.get_emoji('error')} Insufficient Permissions",
            description="You don't have permission to use this command.",
            color=config_manager.get_color("error"),
        )
        await ctx.send(embed=embed, delete_after=10)

    elif isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
            title=f"{config_manager.get_emoji('warning')} Command on Cooldown",
            description=f"Please wait **{error.retry_after:.1f} seconds** before using this command again.",
            color=config_manager.get_color("warning"),
        )
        await ctx.send(embed=embed, delete_after=10)

    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title=f"{config_manager.get_emoji('warning')} Missing Argument",
            description=f"Missing required argument: `{error.param.name}`\n\n"
            f"**Usage:** `{ctx.prefix}{ctx.command.qualified_name} {ctx.command.signature}`",
            color=config_manager.get_color("warning"),
        )
        await ctx.send(embed=embed, delete_after=15)

    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title=f"{config_manager.get_emoji('warning')} Invalid Argument",
            description=f"Invalid argument provided.\n\n"
            f"**Usage:** `{ctx.prefix}{ctx.command.qualified_name} {ctx.command.signature}`",
            color=config_manager.get_color("warning"),
        )
        await ctx.send(embed=embed, delete_after=15)

    elif isinstance(error, discord.Forbidden):
        embed = discord.Embed(
            title=f"{config_manager.get_emoji('error')} Permission Error",
            description="I don't have permission to perform this action. Please check my role permissions.",
            color=config_manager.get_color("error"),
        )
        await ctx.send(embed=embed, delete_after=10)

    else:
        # Log unknown errors
        logger.error(f"Unhandled error in {ctx.command}: {error}")

        # Send generic error message to user
        embed = discord.Embed(
            title=f"{config_manager.get_emoji('error')} Something Went Wrong",
            description="An unexpected error occurred. The error has been logged.",
            color=config_manager.get_color("error"),
        )

        if config_manager.get("development.debug_mode", False):
            embed.add_field(
                name="Debug Info", value=f"```{str(error)[:1000]}```", inline=False
            )

        await ctx.send(embed=embed, delete_after=15)


# Function to show category help
async def show_category_help(interaction, category):
    """Show detailed help for a specific command category"""
    categories = {
        "quiz": {
            "title": "🎮 Quiz Commands",
            "description": "Test your knowledge with interactive quizzes and track your progress.",
            "commands": {
                "quiz": "Start a new quiz on a random topic",
                "leaderboard": "View the quiz leaderboard",
                "mystats": "View your personal quiz statistics",
                "categories": "List available quiz categories"
            },
            "color": "primary"
        },
        "space": {
            "title": "🌌 Space Commands",
            "description": "Explore the cosmos with NASA data and space information.",
            "commands": {
                "apod": "Show NASA's Astronomy Picture of the Day",
                "fact": "Get a random space fact",
                "meteor": "Check upcoming meteor showers",
                "iss": "Track the International Space Station",
                "launch": "View upcoming space launches"
            },
            "color": "space"
        },
        "stellaris": {
            "title": "🏛️ Stellaris Empire Commands",
            "description": "Manage your galactic empire and role within the cosmos.",
            "commands": {
                "empire": "Choose your Stellaris empire role",
                "lore": "Get lore about your chosen empire",
                "rolecount": "View distribution of empire roles"
            },
            "color": "stellaris"
        },
        "stats": {
            "title": "📊 Server Statistics Commands",
            "description": "View various statistics about the server and bot.",
            "commands": {
                "stats": "View server statistics",
                "ping": "Check bot latency",
                "uptime": "Check bot uptime",
                "membercount": "View member count statistics"
            },
            "color": "info"
        }
    }
    
    if category not in categories:
        await interaction.response.send_message("Category not found.", ephemeral=True)
        return
        
    cat_info = categories[category]
    
    embed = discord.Embed(
        title=cat_info["title"],
        description=cat_info["description"],
        color=config_manager.get_color(cat_info["color"])
    )
    
    prefix = config_manager.get("bot_settings.prefix", "!")
    
    for cmd, desc in cat_info["commands"].items():
        embed.add_field(
            name=f"`{prefix}{cmd}`",
            value=desc,
            inline=False
        )
    
    embed.set_footer(text=f"Use {prefix}help <command> for detailed information on each command.")
    
    await interaction.response.edit_message(embed=embed, view=interaction.message.view)


@bot.command(name="help")
async def enhanced_help(ctx, *, command_or_category=None):
    """Enhanced help command with categorized commands and UI components"""

    if command_or_category:
        # Show help for specific command
        command = bot.get_command(command_or_category.lower())
        if command:
            embed = discord.Embed(
                title=f"📖 Help: {command.qualified_name}",
                description=command.help or "No description available.",
                color=config_manager.get_color("info"),
            )

            embed.add_field(
                name="Usage",
                value=f"`{ctx.prefix}{command.qualified_name} {command.signature}`",
                inline=False,
            )

            if command.aliases:
                embed.add_field(
                    name="Aliases",
                    value=", ".join([f"`{alias}`" for alias in command.aliases]),
                    inline=True,
                )

            await ctx.send(embed=embed)
            return

    # Main help embed with categories
    embed = discord.Embed(
        title=f"🚀 {config_manager.get('bot_settings.name')} Commands",
        description=config_manager.get('bot_settings.description'),
        color=config_manager.get_color("primary"),
    )

    # Add command categories
    categories = {
        "🎮 Quiz & Games": ["quiz", "leaderboard", "mystats", "categories"],
        "🌌 Space & Astronomy": ["apod", "fact", "meteor", "iss", "launch"],
        "🏛️ Stellaris Empire": ["empire", "lore", "rolecount"],
        "📊 Server Stats": ["stats", "ping", "uptime", "membercount"],
        "📓 Productivity": ["reminders", "todo"],
        "🔧 Configuration": ["setup", "config"],
    }

    for category, commands_list in categories.items():
        # Filter commands based on user permissions and enabled features
        available_commands = []
        for cmd_name in commands_list:
            cmd = bot.get_command(cmd_name)
            if cmd and config_manager.can_use_command(ctx.author, cmd_name):
                available_commands.append(f"`{cmd_name}`")

        if available_commands:
            embed.add_field(
                name=category, value=" • ".join(available_commands), inline=False
            )

    embed.add_field(
        name="💡 Tips",
        value=f"• Use `{ctx.prefix}help <command>` for detailed command info\n"
        f"• Join our support server for help and updates\n"
        f"• Use UI buttons and dropdowns for easier interaction!",
        inline=False,
    )

    embed.set_footer(
        text=f"🌟 {config_manager.get('bot_settings.name')} v{config_manager.get('bot_settings.version')} - Exploring the cosmos together"
    )

    # Add interactive view for command categories
    view = CategorySelectView(
        categories={
            "quiz": {
                "name": "Quiz Commands",
                "description": "Interactive quizzes and leaderboards",
                "emoji": "🎮",
            },
            "space": {
                "name": "Space Commands",
                "description": "NASA data and space content",
                "emoji": "🌌",
            },
            "stellaris": {
                "name": "Stellaris Commands",
                "description": "Empire roles and lore",
                "emoji": "🏛️",
            },
            "stats": {
                "name": "Server Commands",
                "description": "Statistics and server info",
                "emoji": "📊",
            },
        },
        callback=show_category_help,
        placeholder="Select a category for detailed commands...",
    )

    await ctx.send(embed=embed, view=view)


# Run the bot with proper error handling
async def main():
    async with bot:
        try:
            logger.info("🚀 Starting Astra Discord Bot...")
            await bot.start(TOKEN)
        except discord.LoginFailure:
            logger.critical("❌ Invalid token provided. Please check your .env file.")
        except discord.PrivilegedIntentsRequired:
            logger.critical("❌ Privileged intents are required but not enabled in the Discord Developer Portal.")
        except Exception as e:
            logger.critical(f"❌ Fatal error: {str(e)}")
        finally:
            logger.info("👋 Bot is shutting down...")

if __name__ == "__main__":
    asyncio.run(main())

## main bot code
