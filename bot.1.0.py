"""
Astra Discord Bot - Main Launcher
A modern Discord bot using slash commands for space exploration and Stellaris roleplay
Developed by: x1ziad
Version: 1.0.0
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import asyncio
import logging
import traceback
from dotenv import load_dotenv
from datetime import datetime, timedelta, time
import json
from pathlib import Path
import aiohttp
import sys

# Add the current directory to Python's path to enable proper imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ ERROR: DISCORD_TOKEN not found in .env file")
    exit(1)

# Import our custom modules
from config.config_manager import config_manager
from logger.logger import setup_logger, log_performance

# Get current date/time for startup logging
startup_time = datetime.utcnow()
startup_time_str = startup_time.strftime("%Y-%m-%d %H:%M:%S")

# Setup enhanced logging
logger = setup_logger(
    "Astra",
    config_manager.get("development.debug_mode", False) and "DEBUG" or "INFO",
    log_file=f"data/logs/astra_{startup_time.strftime('%Y%m%d')}.log",
)

# Log startup information with user and time
logger.info(
    f"Bot startup initiated by {os.getenv('USER', 'x1ziad')} at {startup_time_str}"
)
logger.info(f"Loading configuration from {config_manager.config_file}")

# Bot configuration with enhanced intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # Required for certain features
intents.presences = True  # For tracking user status


class AstraBot(commands.Bot):
    """Custom bot class with enhanced functionality"""

    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned,  # Only respond to @mentions for prefix commands
            intents=intents,
            help_command=None,  # Disable default help command
            description=config_manager.get(
                "bot_settings.description", "Astra - Space exploration bot"
            ),
            case_insensitive=True,
        )
        # Store bot start time for uptime tracking
        self.start_time = startup_time
        self.config = config_manager
        self.logger = logger

        # API session for shared connections
        self.session = None

        # Global cache for frequently accessed data
        self.user_cache = {}
        self.guild_cache = {}

        # Add version info
        self.version = self.config.get("bot_settings.version", "1.0.0")

    async def setup_hook(self):
        """Initial setup after bot is ready but before it connects to Discord"""
        self.logger.info(
            f"Running setup hook for {self.config.get('bot_settings.name')} v{self.version}"
        )

        # Create global aiohttp session
        self.session = aiohttp.ClientSession()

        # Ensure required directories exist
        self.config.ensure_directories()

        # Load all extensions
        await self.load_extensions()

        # Sync commands with Discord
        if self.config.get("development.command_sync_on_ready", False):
            self.logger.info("🔄 Syncing commands with Discord...")
            # Sync to test guild if specified
            test_guild_id = self.config.get("development.test_guild_id", None)
            if test_guild_id:
                test_guild = discord.Object(id=test_guild_id)
                self.tree.copy_global_to(guild=test_guild)
                await self.tree.sync(guild=test_guild)
                self.logger.info(
                    f"✅ Commands synced to test guild ID: {test_guild_id}"
                )
            else:
                # Global sync - takes up to an hour to propagate
                await self.tree.sync()
                self.logger.info(
                    "✅ Commands synced globally (may take up to 1 hour to propagate)"
                )

    async def on_ready(self):
        """Bot is connected and ready to use"""
        self.logger.info("=" * 60)
        self.logger.info(
            f"🚀 {self.config.get('bot_settings.name', 'Astra')} v{self.version} is online!"
        )

        # Bot information
        self.logger.info(f"🤖 Bot: {self.user} (ID: {self.user.id})")
        self.logger.info(f"🌐 Connected to {len(self.guilds)} guild(s)")

        total_members = sum(guild.member_count for guild in self.guilds)
        unique_members = len(set(self.get_all_members()))
        self.logger.info(
            f"👥 Serving {total_members} total members ({unique_members} unique)"
        )

        # Load guild configurations
        for guild in self.guilds:
            try:
                self.config.load_guild_config(guild.id)
                self.logger.info(
                    f"📋 Loaded config for guild: {guild.name} (ID: {guild.id})"
                )
            except Exception as e:
                self.logger.error(f"⚠️ Error loading config for guild {guild.name}: {e}")

        # Set bot activity
        activity_text = self.config.get("bot_settings.activity", "the cosmos | /help")
        activity = discord.Activity(
            type=discord.ActivityType.watching, name=activity_text
        )
        await self.change_presence(activity=activity, status=discord.Status.online)

        # Start background tasks
        self.start_scheduled_tasks()

        self.logger.info("🎯 All systems operational!")
        self.logger.info(f"Started at {startup_time_str} UTC")
        self.logger.info("=" * 60)

    async def load_extensions(self):
        """Load all cogs with enhanced error handling and logging"""
        # Define extensions to load
        extensions = [
            "cogs.admin",
            "cogs.roles",
            "cogs.quiz",
            "cogs.space",
            "cogs.notion",
            "cogs.stats",
            # Additional cogs - uncomment as they become available
            # "cogs.activity",
            # "cogs.music",
            # "cogs.mod",
            # "cogs.commands",
            # "cogs.feeds",
            # "cogs.join_leave",
            # "cogs.imagegen",
        ]

        loaded_count = 0
        failed_count = 0

        for ext in extensions:
            try:
                await self.load_extension(ext)
                self.logger.info(f"✅ Loaded extension: {ext}")
                loaded_count += 1
            except FileNotFoundError:
                self.logger.warning(f"⚠️ Extension not found: {ext} - skipping")
            except Exception as e:
                self.logger.error(f"❌ Failed to load {ext}: {str(e)}")
                self.logger.error(traceback.format_exc())
                failed_count += 1

        self.logger.info(
            f"🎯 Extension loading complete: {loaded_count} loaded, {failed_count} failed"
        )

    def start_scheduled_tasks(self):
        """Start all background tasks if they're enabled"""
        # Space content tasks
        if self.config.is_feature_enabled("space_content.daily_apod"):
            if (
                not hasattr(self, "_daily_apod_task")
                or not self._daily_apod_task.is_running()
            ):
                self._daily_apod_task.start()
                self.logger.info("✅ Started daily APOD task")

        # Quiz tasks
        if self.config.is_feature_enabled("quiz_system.daily_questions"):
            if (
                not hasattr(self, "_daily_quiz_reminder")
                or not self._daily_quiz_reminder.is_running()
            ):
                self._daily_quiz_reminder.start()
                self.logger.info("✅ Started daily quiz reminder task")

    @tasks.loop(time=time(hour=12, minute=0))  # Run at 12:00 UTC
    async def _daily_apod_task(self):
        """Task to post NASA's Astronomy Picture of the Day to configured channels"""
        self.logger.info("🚀 Running daily APOD task")

        try:
            # Get NASA API key from environment or use demo key
            nasa_api_key = os.getenv("NASA_API_KEY", "DEMO_KEY")

            # Fetch APOD data from NASA API
            if not self.session or self.session.closed:
                self.session = aiohttp.ClientSession()

            async with self.session.get(
                f"https://api.nasa.gov/planetary/apod?api_key={nasa_api_key}"
            ) as response:
                if response.status != 200:
                    self.logger.error(f"NASA API returned status {response.status}")
                    return

                data = await response.json()

            # Create embed with the APOD information
            embed = discord.Embed(
                title=f"🌌 {data.get('title', 'Astronomy Picture of the Day')}",
                description=data.get("explanation", "No description available")[
                    :4000
                ],  # Discord embed limit
                color=self.config.get_color("space"),
                timestamp=datetime.utcnow(),
            )

            # Add image or video
            if data.get("media_type") == "image":
                embed.set_image(url=data.get("hdurl", data.get("url")))
            elif data.get("media_type") == "video":
                embed.add_field(
                    name="🎥 Today's APOD is a video",
                    value=f"[Click here to view]({data.get('url')})",
                    inline=False,
                )

            if data.get("copyright"):
                embed.set_footer(
                    text=f"Image Credit & Copyright: {data.get('copyright')} • NASA APOD for {data.get('date')}"
                )
            else:
                embed.set_footer(text=f"Credit: NASA • APOD for {data.get('date')}")

            # Post to all configured channels
            for guild in self.guilds:
                try:
                    guild_id = guild.id
                    channel_id = self.config.get_guild_setting(
                        guild_id, "channels.space_channel"
                    )

                    if not channel_id:
                        continue

                    channel = self.get_channel(int(channel_id))
                    if channel and channel.permissions_for(guild.me).send_messages:
                        await channel.send(embed=embed)
                        self.logger.info(
                            f"Posted APOD to #{channel.name} in {guild.name}"
                        )
                except Exception as e:
                    self.logger.error(f"Error posting APOD to guild {guild.id}: {e}")

        except Exception as e:
            self.logger.error(f"Error in daily APOD task: {e}")
            self.logger.error(traceback.format_exc())

    @tasks.loop(time=time(hour=15, minute=0))  # Run at 15:00 UTC
    async def _daily_quiz_reminder(self):
        """Task to post daily quiz reminders to configured channels"""
        self.logger.info("🎮 Running daily quiz reminder task")

        try:
            # Build the quiz reminder embed
            embed = discord.Embed(
                title="🎯 Daily Quiz Available!",
                description="Today's quiz is now available! Use `/quiz start` to test your knowledge.",
                color=self.config.get_color("primary"),
                timestamp=datetime.utcnow(),
            )

            embed.add_field(
                name="💡 How to Play",
                value="Use `/quiz start` to get a random question\n"
                + "Use `/quiz start category:space` for space questions\n"
                + "Use `/quiz start category:stellaris` for Stellaris questions",
                inline=False,
            )

            embed.add_field(
                name="🏆 Leaderboard",
                value="Check your ranking with `/quiz leaderboard`",
                inline=False,
            )

            # Add a random space fact as a bonus
            space_facts = [
                "The Sun makes up 99.86% of the mass of our solar system.",
                "A day on Venus is longer than its year!",
                "The Great Red Spot on Jupiter has been swirling for at least 400 years.",
                "If you could fly a plane to Pluto, the trip would take more than 800 years.",
                "There are more stars in the universe than grains of sand on all Earth's beaches.",
            ]

            embed.add_field(
                name="🌠 Random Space Fact",
                value=f"*{random.choice(space_facts)}*",
                inline=False,
            )

            embed.set_footer(text="Take the quiz daily to improve your streak!")

            # Post to all configured channels
            for guild in self.guilds:
                try:
                    guild_id = guild.id
                    channel_id = self.config.get_guild_setting(
                        guild_id, "channels.quiz_channel"
                    )

                    if not channel_id:
                        continue

                    channel = self.get_channel(int(channel_id))
                    if channel and channel.permissions_for(guild.me).send_messages:
                        await channel.send(embed=embed)
                        self.logger.info(
                            f"Posted quiz reminder to #{channel.name} in {guild.name}"
                        )
                except Exception as e:
                    self.logger.error(
                        f"Error posting quiz reminder to guild {guild.id}: {e}"
                    )

        except Exception as e:
            self.logger.error(f"Error in daily quiz reminder task: {e}")
            self.logger.error(traceback.format_exc())

    @_daily_apod_task.before_loop
    @_daily_quiz_reminder.before_loop
    async def _before_tasks(self):
        """Wait for the bot to be ready before starting scheduled tasks"""
        await self.wait_until_ready()
        self.logger.info("Bot is ready, scheduled tasks can now start")

    @_daily_apod_task.error
    @_daily_quiz_reminder.error
    async def _task_error(self, error):
        """Handle errors in background tasks"""
        self.logger.error(f"Error in scheduled task: {error}")
        self.logger.error(traceback.format_exc())

    async def on_guild_join(self, guild):
        """Handle bot joining a new guild"""
        self.logger.info(
            f"🏛️ Joined new guild: {guild.name} (ID: {guild.id}, Members: {guild.member_count})"
        )

        # Load/create guild configuration
        self.config.load_guild_config(guild.id)

        # Send welcome message if possible
        if (
            guild.system_channel
            and guild.system_channel.permissions_for(guild.me).send_messages
        ):
            embed = discord.Embed(
                title=f"🚀 {self.config.get('bot_settings.name')} Has Arrived!",
                description=f"Thank you for adding **{self.config.get('bot_settings.name')}** to {guild.name}!\n\n"
                "I'm here to help with space content, Stellaris gameplay, and interactive quizzes.",
                color=self.config.get_color("primary"),
            )

            embed.add_field(
                name="🎯 Getting Started",
                value="• Use `/help` to see all commands\n"
                "• Use `/admin setup` to configure the bot\n"
                "• Use `/empire choose` to select your Stellaris role",
                inline=False,
            )

            embed.add_field(
                name="🔧 Setup Required",
                value="Administrators should run `/admin setup` to configure channels and permissions.",
                inline=False,
            )

            embed.set_footer(text="May your journey among the stars be prosperous! ⭐")

            try:
                await guild.system_channel.send(embed=embed)
            except discord.Forbidden:
                self.logger.warning(
                    f"Cannot send welcome message in {guild.name} - no permissions"
                )

    async def on_guild_remove(self, guild):
        """Handle bot leaving a guild"""
        self.logger.info(f"🏛️ Left guild: {guild.name} (ID: {guild.id})")

        # Clean up guild cache
        if guild.id in self.guild_cache:
            del self.guild_cache[guild.id]

    async def on_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        """Global error handler for slash commands"""
        # Get the original error
        error = getattr(error, "original", error)

        # Log the error
        if interaction.command:
            self.logger.error(
                f"Command error in {interaction.command.name}: {str(error)}"
            )
        else:
            self.logger.error(f"Command error: {str(error)}")

        try:
            if isinstance(error, app_commands.CommandOnCooldown):
                minutes, seconds = divmod(int(error.retry_after), 60)
                time_format = (
                    f"{seconds}s" if minutes == 0 else f"{minutes}m {seconds}s"
                )

                await interaction.response.send_message(
                    f"⏱️ This command is on cooldown. Try again in {time_format}.",
                    ephemeral=True,
                )

            elif isinstance(error, app_commands.MissingPermissions):
                await interaction.response.send_message(
                    "❌ You don't have permission to use this command.", ephemeral=True
                )

            elif isinstance(error, app_commands.BotMissingPermissions):
                await interaction.response.send_message(
                    f"❌ I'm missing required permissions: {', '.join(error.missing_permissions)}",
                    ephemeral=True,
                )

            elif isinstance(error, app_commands.CheckFailure):
                await interaction.response.send_message(
                    "❌ You don't have permission to use this command.", ephemeral=True
                )

            elif isinstance(error, discord.Forbidden):
                await interaction.response.send_message(
                    "❌ I don't have permission to do that.", ephemeral=True
                )

            elif isinstance(error, app_commands.CommandNotFound):
                # Silent fail for command not found
                pass

            else:
                # Send a generic error message for unhandled errors
                if not interaction.response.is_done():
                    embed = discord.Embed(
                        title=f"{self.config.get_emoji('error')} Error",
                        description="An unexpected error occurred. The error has been logged.",
                        color=self.config.get_color("error"),
                    )

                    # Include error details if debug mode is on
                    if self.config.get("development.debug_mode", False):
                        embed.add_field(
                            name="Details", value=f"```{str(error)[:1000]}```"
                        )

                    await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            # If even the error handler fails, log it but don't crash
            self.logger.error(f"Error in error handler: {e}")

    async def close(self):
        """Clean up resources when bot is shutting down"""
        self.logger.info("🔄 Bot is shutting down, cleaning up resources...")

        # Close aiohttp session if it exists
        if self.session:
            await self.session.close()

        # Cancel all tasks
        for task in asyncio.all_tasks():
            if task is not asyncio.current_task():
                task.cancel()

        await super().close()


# Create bot instance
bot = AstraBot()


# Add a simple test command
@bot.tree.command(name="ping", description="Check bot's latency")
@log_performance(logger)
async def ping_command(interaction: discord.Interaction):
    """Check the bot's latency"""
    start_time = datetime.utcnow()

    # Initial response
    await interaction.response.defer()

    # Calculate response time
    end_time = datetime.utcnow()
    response_time = (end_time - start_time).total_seconds() * 1000

    # Create embed with results
    embed = discord.Embed(
        title="🏓 Pong!",
        color=(
            config_manager.get_color("success")
            if bot.latency * 1000 < 100
            else (
                config_manager.get_color("warning")
                if bot.latency * 1000 < 200
                else config_manager.get_color("error")
            )
        ),
    )

    embed.add_field(
        name="📡 WebSocket Latency",
        value=f"{bot.latency * 1000:.2f}ms",
        inline=True,
    )

    embed.add_field(
        name="⚡ Response Time", value=f"{response_time:.2f}ms", inline=True
    )

    # Add status indicator
    if bot.latency * 1000 < 100:
        status = "🟢 Excellent"
    elif bot.latency * 1000 < 200:
        status = "🟡 Good"
    else:
        status = "🔴 Poor"

    embed.add_field(name="📊 Status", value=status, inline=True)

    # Add current time
    embed.set_footer(
        text=f"Current time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
    )

    await interaction.followup.send(embed=embed)


# Add after the existing ping_command and help_command but before the main() function


@bot.tree.command(name="invite", description="Get an invite link for the bot")
async def invite_command(interaction: discord.Interaction):
    """Generate an invite link for the bot"""
    permissions = discord.Permissions(
        send_messages=True,
        embed_links=True,
        attach_files=True,
        read_messages=True,
        read_message_history=True,
        add_reactions=True,
        use_external_emojis=True,
        manage_messages=True,  # For deleting command invocations, etc.
    )

    # Generate the invite link
    invite_url = discord.utils.oauth_url(
        bot.user.id, permissions=permissions, scopes=("bot", "applications.commands")
    )

    # Create embed
    embed = discord.Embed(
        title="🚀 Invite Me To Your Server!",
        description=f"Click the button below to add {bot.config.get('bot_settings.name')} to your server:",
        color=bot.config.get_color("primary"),
        timestamp=datetime.utcnow(),
    )

    # Create view with button
    class InviteView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
            self.add_item(
                discord.ui.Button(
                    label="Invite Bot", url=invite_url, style=discord.ButtonStyle.url
                )
            )

    await interaction.response.send_message(
        embed=embed, view=InviteView(), ephemeral=True
    )


# Quick help command
@bot.tree.command(name="help", description="View available commands and information")
async def help_command(interaction: discord.Interaction):
    """Basic help command"""
    embed = discord.Embed(
        title=f"🚀 {config_manager.get('bot_settings.name')} Help",
        description="Here are the available commands and categories:",
        color=config_manager.get_color("primary"),
    )

    # Command categories
    embed.add_field(
        name="🪐 Space Commands",
        value="• `/space apod` - NASA's Astronomy Picture of the Day\n"
        "• `/space fact` - Random space fact\n"
        "• `/space iss` - Track the ISS\n"
        "• `/space meteor` - Meteor shower information",
        inline=False,
    )

    embed.add_field(
        name="🎮 Quiz Commands",
        value="• `/quiz start` - Start a quiz\n"
        "• `/quiz leaderboard` - View leaderboard\n"
        "• `/quiz stats` - View your stats",
        inline=False,
    )

    embed.add_field(
        name="🏛️ Stellaris Commands",
        value="• `/empire choose` - Choose your empire type\n"
        "• `/empire lore` - Get Stellaris lore\n"
        "• `/empire homeworld` - Choose your homeworld",
        inline=False,
    )

    embed.add_field(
        name="📊 Statistics",
        value="• `/stats server` - Server statistics\n"
        "• `/stats ping` - Check bot latency\n"
        "• `/stats uptime` - Bot uptime",
        inline=False,
    )

    embed.set_footer(text="Use the command to see specific options and parameters")

    await interaction.response.send_message(embed=embed)


# Run the bot with proper error handling
async def main():
    """Main function to start and run the bot with proper error handling"""
    try:
        logger.info(
            f"🚀 Starting {config_manager.get('bot_settings.name', 'Astra')} Discord Bot v{config_manager.get('bot_settings.version', '1.0.0')}..."
        )
        await bot.start(TOKEN)
    except discord.LoginFailure:
        logger.critical("❌ Invalid token provided. Please check your .env file.")
    except discord.PrivilegedIntentsRequired:
        logger.critical(
            "❌ Privileged intents are required but not enabled in the Discord Developer Portal."
        )
    except Exception as e:
        logger.critical(f"❌ Fatal error: {str(e)}")
        logger.critical(traceback.format_exc())
    finally:
        logger.info("👋 Bot is shutting down...")
        if not bot.is_closed():
            await bot.close()


# Entry point
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped manually with keyboard interrupt")
    except Exception as e:
        logger.critical(f"Unhandled exception in main process: {e}")
        logger.critical(traceback.format_exc())
        sys.exit(1)
