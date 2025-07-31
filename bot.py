"""
Astra Discord Bot - Main Application File
A Discord bot for space exploration and Stellaris roleplay
Created by x1ziad

Version: 1.0.0
Last updated: 2025-07-31
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
        self.logger.info(
            f"Bot startup initiated by {os.getlogin()} at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
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

    def create_task(self, coro):
        """Create and track a task to ensure proper cleanup"""
        task = asyncio.create_task(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    def setup_events(self):
        """Register bot event handlers"""

        @self.event
        async def on_ready():
            """Handle bot ready event"""
            try:
                # Get bot info
                bot_name = config_manager.get("bot_settings.name", "Astra")
                bot_version = config_manager.get("bot_settings.version", "1.0.0")

                # Calculate unique members across all guilds
                unique_members = set()
                for guild in self.guilds:
                    for member in guild.members:
                        unique_members.add(member.id)

                # Log bot stats
                self.logger.info(
                    "============================================================"
                )
                self.logger.info(f"🚀 {bot_name} v{bot_version} is online!")
                self.logger.info(
                    f"🤖 Bot: {self.user.name}#{self.user.discriminator} (ID: {self.user.id})"
                )
                self.logger.info(f"🌐 Connected to {len(self.guilds)} guild(s)")
                self.logger.info(
                    f"👥 Serving {sum(g.member_count for g in self.guilds)} total members ({len(unique_members)} unique)"
                )

                # Load guild configurations
                for guild in self.guilds:
                    self.logger.info(
                        f"📋 Loaded config for guild: {guild.name} (ID: {guild.id})"
                    )

                # Force sync all commands to fix registration issues
                if config_manager.get("bot_settings.command_sync_on_ready", True):
                    try:
                        self.logger.info("🔄 Syncing application commands...")
                        await self.tree.sync()
                        self.logger.info("✅ Application commands synchronized!")
                    except discord.HTTPException as e:
                        self.logger.error(f"❌ Failed to sync commands: {e}")
                    except Exception as e:
                        self.logger.error(f"❌ Unexpected error syncing commands: {e}")

                self.logger.info("🎯 All systems operational!")
                self.logger.info(
                    f"Started at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC"
                )
                self.logger.info(
                    "============================================================"
                )
            except Exception as e:
                self.logger.error(f"Error in on_ready event: {e}")
                self.logger.error(traceback.format_exc())

        @self.event
        async def on_guild_join(guild):
            """Called when the bot joins a new guild"""
            self.logger.info(
                f"🎉 Joined new guild: {guild.name} (ID: {guild.id}) with {guild.member_count} members"
            )

            # Auto-sync commands to the new guild
            if config_manager.get("bot_settings.command_sync_on_join", True):
                try:
                    await self.tree.sync(guild=guild)
                    self.logger.info(f"✅ Synced commands to guild: {guild.name}")
                except Exception as e:
                    self.logger.error(
                        f"❌ Failed to sync commands to guild {guild.name}: {e}"
                    )

        @self.event
        async def on_command_error(ctx, error):
            """Handle traditional command errors (non-slash commands)"""
            if isinstance(error, commands.CommandNotFound):
                return  # Ignore command not found errors

            if isinstance(error, commands.MissingRequiredArgument):
                await ctx.send(f"❌ Missing required argument: {error.param.name}")
                return

            self.logger.error(f"Command error in {ctx.command}: {error}")
            self.logger.error(traceback.format_exc())
            await ctx.send("❌ An error occurred while executing this command.")

        @self.tree.error
        async def on_app_command_error(interaction: discord.Interaction, error):
            """Handle application command errors"""
            error_str = str(error)

            # Determine whether to use response or followup
            if interaction.response.is_done():
                send_func = interaction.followup.send
            else:
                send_func = interaction.response.send_message

            if isinstance(error, app_commands.CommandOnCooldown):
                await send_func(
                    f"⏳ This command is on cooldown! Try again in {error.retry_after:.1f} seconds.",
                    ephemeral=True,
                )
                return

            if isinstance(error, app_commands.CheckFailure):
                # Feature disabled errors from our decorator
                if "feature" in error_str.lower() and "disabled" in error_str.lower():
                    await send_func(f"❌ {error_str}", ephemeral=True)
                    return

                # Permission errors
                await send_func(
                    "❌ You don't have permission to use this command.", ephemeral=True
                )
                return

            # Log unexpected errors
            command_name = (
                interaction.command.name if interaction.command else "unknown command"
            )
            self.logger.error(f"Command error in {command_name}: {error}")
            self.logger.error(f"Full traceback: {traceback.format_exc()}")

            # User-friendly error message
            await send_func(
                "❌ An error occurred while executing this command. The developers have been notified.",
                ephemeral=True,
            )

    async def setup_hook(self) -> None:
        """Setup hook that runs after bot initialization but before connecting to Discord"""
        bot_name = self.config.get("bot_settings.name", "Astra")
        bot_version = self.config.get("bot_settings.version", "1.0.0")
        self.logger.info(f"Running setup hook for {bot_name} v{bot_version}")

        # Load extensions (cogs)
        await self.load_extensions()

    async def load_extensions(self) -> None:
        """Load all extensions (cogs) from the cogs directory"""
        # Get list of extensions to load
        ext_list = [
            "cogs.admin",
            "cogs.roles",
            "cogs.quiz",
            "cogs.space",
            "cogs.notion",
            "cogs.stats",
        ]

        # Try to load debug cog if available
        try:
            if Path("cogs/debug.py").exists():
                ext_list.append("cogs.debug")
        except Exception:
            pass

        loaded = 0
        failed = 0

        # Load each extension
        for ext in ext_list:
            try:
                await self.load_extension(ext)
                self.logger.info(f"✅ Loaded extension: {ext}")
                loaded += 1
            except Exception as e:
                self.logger.error(f"❌ Failed to load {ext}: {e}")
                self.logger.error(f"Traceback: {traceback.format_exc()}")
                failed += 1

        self.logger.info(
            f"🎯 Extension loading complete: {loaded} loaded, {failed} failed"
        )

    async def close(self) -> None:
        """Clean up resources before the bot exits"""
        self.logger.info("🔄 Bot is shutting down, cleaning up resources...")

        # Cancel all running tasks
        for task in self._tasks:
            if not task.done() and not task.cancelled():
                task.cancel()

        # Give tasks time to complete cancellation
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

        # Close HTTP sessions
        try:
            from utils.http_client import close_session

            await close_session()
        except Exception as e:
            self.logger.error(f"Error closing HTTP sessions: {e}")

        # Call the parent close method to clean up Discord-related resources
        self.logger.info("👋 Bot is shutting down...")
        await super().close()


# Register global commands
def register_global_commands(bot):
    """Register global commands that aren't part of cogs"""

    @bot.tree.command(
        name="help", description="Show available commands and bot information"
    )
    async def help_command(interaction: discord.Interaction):
        """Help command to show all available commands"""
        # Get all registered commands
        commands = interaction.client.tree.get_commands()

        # Create categories
        categories = {
            "space": {"name": "🪐 Space Commands", "commands": []},
            "quiz": {"name": "🎮 Quiz Commands", "commands": []},
            "empire": {"name": "🏛️ Stellaris Commands", "commands": []},
            "stats": {"name": "📊 Statistics", "commands": []},
            "utility": {"name": "🛠️ Utility", "commands": []},
        }

        # Sort commands into categories
        for cmd in commands:
            if isinstance(cmd, app_commands.Group):
                parent_name = cmd.name
                for subcmd in cmd.commands:
                    if parent_name in categories:
                        categories[parent_name]["commands"].append(
                            f"/{parent_name} {subcmd.name} - {subcmd.description}"
                        )
            else:
                if cmd.name == "help":
                    categories["utility"]["commands"].append(
                        f"/{cmd.name} - {cmd.description}"
                    )
                elif cmd.name == "ping":
                    categories["utility"]["commands"].append(
                        f"/{cmd.name} - {cmd.description}"
                    )
                elif cmd.name == "invite":
                    categories["utility"]["commands"].append(
                        f"/{cmd.name} - {cmd.description}"
                    )
                elif cmd.name == "debug":
                    categories["utility"]["commands"].append(
                        f"/{cmd.name} - {cmd.description}"
                    )
                elif cmd.name in categories:
                    categories[cmd.name]["commands"].append(
                        f"/{cmd.name} - {cmd.description}"
                    )

        # Build help text
        help_text = (
            "🚀 **Astra Help**\nHere are the available commands and categories:\n"
        )

        for category_key, category_data in categories.items():
            if category_data["commands"]:
                help_text += f"\n**{category_data['name']}**\n"
                help_text += (
                    "\n".join([f"• {cmd}" for cmd in category_data["commands"]]) + "\n"
                )

        help_text += "\nUse the command to see specific options and parameters"

        await interaction.response.send_message(help_text)

    @bot.tree.command(name="ping", description="Check bot latency and response time")
    async def ping_command(interaction: discord.Interaction):
        """Simple ping command to check bot latency"""
        start_time = datetime.utcnow()
        await interaction.response.defer()
        end_time = datetime.utcnow()

        response_time = (end_time - start_time).total_seconds() * 1000
        bot_latency = interaction.client.latency * 1000

        if bot_latency < 100:
            color = config_manager.get_color("success")
        elif bot_latency < 300:
            color = config_manager.get_color("warning")
        else:
            color = config_manager.get_color("error")

        embed = discord.Embed(
            title="🏓 Pong!",
            color=color,
        )

        embed.add_field(
            name="📡 WebSocket Latency",
            value=f"{bot_latency:.2f}ms",
            inline=True,
        )

        embed.add_field(
            name="⚡ Response Time",
            value=f"{response_time:.2f}ms",
            inline=True,
        )

        await interaction.followup.send(embed=embed)

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
            manage_messages=True,
        )

        # Generate the invite link
        invite_url = discord.utils.oauth_url(
            interaction.client.user.id,
            permissions=permissions,
            scopes=("bot", "applications.commands"),
        )

        # Create embed
        embed = discord.Embed(
            title="🚀 Invite Me To Your Server!",
            description=f"Click the button below to add {config_manager.get('bot_settings.name')} to your server:",
            color=config_manager.get_color("primary"),
            timestamp=datetime.utcnow(),
        )

        # Create view with button
        class InviteView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.add_item(
                    discord.ui.Button(
                        label="Invite Bot",
                        url=invite_url,
                        style=discord.ButtonStyle.url,
                    )
                )

        await interaction.response.send_message(
            embed=embed, view=InviteView(), ephemeral=True
        )


# Setup HTTP client for shared sessions
async def setup_http_client():
    """Ensure the HTTP client is ready"""
    try:
        from utils.http_client import get_session

        await get_session()  # Initialize the session
    except ImportError:
        # Create the http_client.py file if it doesn't exist
        http_client_path = Path("utils/http_client.py")
        if not http_client_path.parent.exists():
            http_client_path.parent.mkdir(parents=True, exist_ok=True)

        http_client_content = '''"""
HTTP client utilities for Astra Discord bot
Handles proper creation and cleanup of aiohttp sessions
"""

import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("Astra")
_session: Optional[aiohttp.ClientSession] = None
_session_lock = asyncio.Lock()

async def get_session() -> aiohttp.ClientSession:
    """
    Get or create a shared aiohttp ClientSession
    Uses a singleton pattern to reuse the same session across the application
    """
    global _session
    
    async with _session_lock:
        if _session is None or _session.closed:
            _session = aiohttp.ClientSession(
                headers={"User-Agent": "Astra Discord Bot/1.0.0"},
                timeout=aiohttp.ClientTimeout(total=30)
            )
            logger.debug("Created new aiohttp ClientSession")
            
    return _session

async def close_session() -> None:
    """Close the shared aiohttp ClientSession"""
    global _session
    
    async with _session_lock:
        if _session is not None and not _session.closed:
            await _session.close()
            _session = None
            logger.debug("Closed aiohttp ClientSession")
'''
        with open(http_client_path, "w") as f:
            f.write(http_client_content)

        # Create __init__.py in utils directory
        with open(Path("utils/__init__.py"), "w") as f:
            f.write('"""Utility functions for Astra bot"""\n')

        # Now try to import again
        from utils.http_client import get_session

        await get_session()


# Main function
async def main():
    """Main function to start and run the bot with proper error handling"""
    try:
        # Set up initial logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        )
        logger = logging.getLogger("Astra")
        logger.info(
            f"🚀 Starting {config_manager.get('bot_settings.name', 'Astra')} Discord Bot v{config_manager.get('bot_settings.version', '1.0.0')}..."
        )

        # Create bot instance
        bot = AstraBot()

        # Set up signal handlers for graceful shutdown
        loop = asyncio.get_running_loop()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, lambda: asyncio.create_task(bot.close()))
            except NotImplementedError:
                # Windows doesn't support this signal handling
                pass

        # Register global commands
        register_global_commands(bot)

        # Setup HTTP client
        await setup_http_client()

        # Get token from environment variable
        token = os.environ.get("DISCORD_TOKEN")

        if not token:
            logger.critical(
                "🚫 Discord token not found. Please set the DISCORD_TOKEN environment variable."
            )
            return

        # Start the bot
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("👋 Bot has been shut down manually.")
        if "bot" in locals():
            await bot.close()
    except discord.LoginFailure:
        logger.critical(
            "❌ Invalid Discord token. Please check your token and try again."
        )
    except Exception as e:
        logger.critical(f"❌ An unexpected error occurred: {e}")
        logger.critical(traceback.format_exc())
        if "bot" in locals():
            await bot.close()


# Run the bot
if __name__ == "__main__":
    # Create a new event loop and run the main function
    asyncio.run(main())
