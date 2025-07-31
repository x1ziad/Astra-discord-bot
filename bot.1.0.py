"""
Enhanced Astra Discord Bot - Main Launcher
Modern implementation using Discord slash commands (/)
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import asyncio
import logging
import traceback
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json
from pathlib import Path
import aiohttp

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ ERROR: DISCORD_TOKEN not found in .env file")
    exit(1)

# Import our custom modules - fixed the import path
from logger.logger_setup import setup_logger
from config.config_manager import config_manager

# Setup enhanced logging
logger = setup_logger(
    "Astra", config_manager.get("development.debug_mode", False) and "DEBUG" or "INFO"
)

# Bot configuration with enhanced intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # Required for certain commands


class AstraBot(commands.Bot):
    """Custom bot class with enhanced functionality"""

    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned,  # Only respond to @mentions for text commands
            intents=intents,
            help_command=None,  # Disable default help command
            description=config_manager.get(
                "bot_settings.description", "Astra - Space exploration bot"
            ),
        )
        # Store bot start time for uptime tracking
        self.start_time = datetime.utcnow()
        self.config = config_manager
        self.logger = logger

        # Global cache for frequently accessed data
        self.user_cache = {}
        self.guild_cache = {}

    async def setup_hook(self):
        """Initial setup after bot is ready but before it connects to Discord"""
        # Ensure required directories exist
        self.config.ensure_directories()

        # Import UI components here to avoid circular imports
        try:
            from ui.ui_components import SetupModal, QuizView, EmpireRoleView

            self.logger.info("✅ UI components loaded")
        except ImportError as e:
            self.logger.error(f"❌ Failed to load UI components: {str(e)}")

        # Load all extensions
        await self.load_extensions()

        # Sync commands with Discord
        if self.config.get("development.command_sync_on_ready", False):
            self.logger.info("🔄 Syncing commands with Discord...")
            await self.tree.sync()
            self.logger.info("✅ Commands synced")

    async def on_ready(self):
        """Bot is connected and ready to use"""
        self.logger.info("=" * 60)
        self.logger.info(
            f"🚀 {self.config.get('bot_settings.name', 'Astra')} is online!"
        )

        # Bot information
        self.logger.info(f"🤖 Bot: {self.user} (ID: {self.user.id})")
        self.logger.info(f"🌐 Connected to {len(self.guilds)} guild(s)")

        total_members = len(set(self.get_all_members()))
        self.logger.info(f"👥 Serving {total_members} unique users")

        # Load guild configurations
        for guild in self.guilds:
            self.config.load_guild_config(guild.id)
            self.logger.info(f"📋 Loaded config for guild: {guild.name}")

        # Set bot activity
        activity_text = self.config.get("bot_settings.activity", "the cosmos | /help")
        activity = discord.Activity(
            type=discord.ActivityType.watching, name=activity_text
        )
        await self.change_presence(activity=activity)

        # Start background tasks
        self.start_scheduled_tasks()

        self.logger.info("🎯 All systems operational!")
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
        # Start space APOD task
        if self.config.is_feature_enabled("space_content.daily_apod"):
            if (
                not hasattr(self, "daily_apod_task")
                or not self.daily_apod_task.is_running()
            ):
                self.daily_apod_task.start()
                self.logger.info("✅ Started daily APOD task")

        # Start quiz reminder task
        if self.config.is_feature_enabled("quiz_system.daily_questions"):
            if (
                not hasattr(self, "daily_quiz_reminder")
                or not self.daily_quiz_reminder.is_running()
            ):
                self.daily_quiz_reminder.start()
                self.logger.info("✅ Started daily quiz reminder task")

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
                title="🚀 Astra Has Arrived!",
                description=f"Thank you for adding **{self.config.get('bot_settings.name')}** to {guild.name}!\n\n"
                "I'm here to help with space content, Stellaris gameplay, and interactive quizzes.",
                color=self.config.get_color("primary"),
            )

            embed.add_field(
                name="🎯 Getting Started",
                value="• Use `/help` to see all commands\n"
                "• Use `/setup` to configure the bot\n"
                "• Use `/empire` to choose your Stellaris role",
                inline=False,
            )
            
            embed.add_field(
                name="🔧 Setup Required",
                value="Administrators should run `/setup` to configure channels and permissions.",
                inline=False,
            )
            
            embed.set_footer(text="May your journey among the stars be prosperous! ⭐")
            
            try:
                await guild.system_channel.send(embed=embed)
            except discord.Forbidden:
                self.logger.warning(f"Cannot send welcome message in {guild.name} - no permissions")
    
    async def on_guild_remove(self, guild):
        """Handle bot leaving a guild"""
        self.logger.info(f"🏛️ Left guild: {guild.name} (ID: {guild.id})")
        
        # Clean up guild cache
        if guild.id in self.guild_cache:
            del self.guild_cache[guild.id]
    
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Global error handler for slash commands"""
        # Get the original error
        error = getattr(error, "original", error)
        
        # Log the error
        self.logger.error(f"Command error in {interaction.command.name}: {str(error)}")
        
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"⏱️ This command is on cooldown. Try again in {error.retry_after:.1f} seconds.",
                ephemeral=True
            )
        
        elif isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
        
        elif isinstance(error, app_commands.BotMissingPermissions):
            await interaction.response.send_message(
                f"❌ I'm missing required permissions: {', '.join(error.missing_permissions)}",
                ephemeral=True
            )
        
        elif isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
        
        elif isinstance(error, discord.Forbidden):
            await interaction.response.send_message(
                "❌ I don't have permission to do that.",
                ephemeral=True
            )
        
        else:
            # Send a generic error message for unhandled errors
            try:
                if not interaction.response.is_done():
                    embed = discord.Embed(
                        title=f"{self.config.get_emoji('error')} Error",
                        description="An unexpected error occurred. The error has been logged.",
                        color=self.config.get_color("error")
                    )
                    
                    # Include error details if debug mode is on
                    if self.config.get("development.debug_mode", False):
                        embed.add_field(name="Details", value=f"```{str(error)[:1000]}```")
                    
                    await interaction.response.send_message(embed=embed, ephemeral=True)
            except:
                # In case responding fails (e.g., interaction already responded to)
                pass
    
    @tasks.loop(time=datetime.time(hour=12, minute=0))  # Runs at 12:00 UTC every day
    async def daily_apod_task(self):
        """Task to post daily astronomy picture"""
        self.logger.info("🚀 Running daily APOD task")
        
        # Get guild configurations and process each enabled guild
        for guild_id, guild_config in self.config.guild_configs.items():
            # Check if APOD feature is enabled for this guild
            if not self.config.get_guild_setting(guild_id, "features.space_content.daily_apod", False):
                self.logger.debug(f"Skipping APOD for guild {guild_id}: feature disabled")
                continue
                
            # Get the configured space channel
            channel_id = self.config.get_guild_setting(guild_id, "channels.space_channel", None)
            if not channel_id:
                self.logger.debug(f"Skipping APOD for guild {guild_id}: no space channel configured")
                continue
                
            try:
                # Get channel object
                channel = self.get_channel(int(channel_id))
                if not channel:
                    self.logger.warning(f"Could not find channel {channel_id} for guild {guild_id}")
                    continue
                    
                # Fetch APOD data
                try:
                    async with aiohttp.ClientSession() as session:
                        url = "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY"
                        async with session.get(url) as response:
                            if response.status == 200:
                                data = await response.json()
                                
                                # Create embed with APOD data
                                embed = discord.Embed(
                                    title=f"🌌 {data['title']}",
                                    description=(data.get('explanation', 'No description available')[:1000] + 
                                                "..." if len(data.get('explanation', '')) > 1000 
                                                else data.get('explanation', 'No description available')),
                                    color=self.config.get_color("space"),
                                    timestamp=datetime.strptime(data['date'], "%Y-%m-%d") if 'date' in data else datetime.utcnow()
                                )
                                
                                if data.get('media_type') == 'image':
                                    embed.set_image(url=data['url'])
                                elif data.get('media_type') == 'video':
                                    embed.add_field(name="🎥 Video Link", value=f"[Watch Here]({data['url']})", inline=False)
                                
                                embed.set_footer(text="NASA Astronomy Picture of the Day")
                                
                                await channel.send(embed=embed)
                                self.logger.info(f"✅ Posted APOD in guild {guild_id}")
                            else:
                                self.logger.error(f"NASA API returned status {response.status}")
                except Exception as e:
                    self.logger.error(f"Error fetching APOD data: {str(e)}")
                    continue
                    
            except Exception as e:
                self.logger.error(f"❌ Error posting APOD in guild {guild_id}: {str(e)}")
    
    @tasks.loop(time=datetime.time(hour=15, minute=0))  # Runs at 15:00 UTC every day
    async def daily_quiz_reminder(self):
        """Task to post daily quiz reminders"""
        self.logger.info("🎮 Running daily quiz reminder task")
        
        # Process each guild configuration
        for guild_id, guild_config in self.config.guild_configs.items():
            # Check if quiz feature is enabled for this guild
            if not self.config.get_guild_setting(guild_id, "features.quiz_system.daily_questions", False):
                self.logger.debug(f"Skipping quiz reminder for guild {guild_id}: feature disabled")
                continue
                
            # Get the configured quiz channel
            channel_id = self.config.get_guild_setting(guild_id, "channels.quiz_channel", None)
            if not channel_id:
                self.logger.debug(f"Skipping quiz reminder for guild {guild_id}: no quiz channel configured")
                continue
                
            try:
                # Get channel object
                channel = self.get_channel(int(channel_id))
                if not channel:
                    self.logger.warning(f"Could not find channel {channel_id} for guild {guild_id}")
                    continue
                    
                # Create and send quiz reminder embed
                embed = discord.Embed(
                    title="🎯 Daily Quiz Available!",
                    description="Today's quiz is now available! Use `/quiz` to test your knowledge.",
                    color=self.config.get_color("primary")
                )
                
                embed.add_field(
                    name="💡 How to Play",
                    value="Use `/quiz` to get a random question or `/quiz category:space` for a space-themed question.",
                    inline=False
                )
                
                embed.add_field(
                    name="🏆 Leaderboard",
                    value="Check your ranking with `/leaderboard` or `/mystats`.",
                    inline=False
                )
                
                await channel.send(embed=embed)
                self.logger.info(f"✅ Posted quiz reminder in guild {guild_id}")
                    
            except Exception as e:
                self.logger.error(f"❌ Error posting quiz reminder in guild {guild_id}: {str(e)}")
    
    @daily_apod_task.before_loop
    @daily_quiz_reminder.before_loop
    async def before_tasks(self):
        """Wait until the bot is ready before starting tasks"""
        await self.wait_until_ready()


# Create bot instance
bot = AstraBot()

# Run the bot with proper error handling
async def main():
    """Main function to start and run the bot with proper error handling"""
    try:
        logger.info("🚀 Starting Astra Discord Bot...")
        await bot.start(TOKEN)
    except discord.LoginFailure:
        logger.critical("❌ Invalid token provided. Please check your .env file.")
    except discord.PrivilegedIntentsRequired:
        logger.critical("❌ Privileged intents are required but not enabled in the Discord Developer Portal.")
    except Exception as e:
        logger.critical(f"❌ Fatal error: {str(e)}")
        logger.critical(traceback.format_exc())
    finally:
        logger.info("👋 Bot is shutting down...")
        if not bot.is_closed():
            await bot.close()


# Entry point
if __name__ == "__main__":
    asyncio.run(main())
## main bot code
