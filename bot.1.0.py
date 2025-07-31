"""
Astra Discord Bot - Main Application File
A Discord bot for space exploration and Stellaris roleplay
Created by x1ziad
"""

import asyncio
import logging
import os
import platform
import sys
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

# Import configuration manager
from config.config_manager import config_manager


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

    def setup_events(self):
        """Register bot event handlers"""

        @self.event
        async def on_ready():
            """Handle bot ready event"""
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
                self.logger.info("🔄 Syncing application commands...")
                await self.tree.sync()
                self.logger.info("✅ Application commands synchronized!")

            self.logger.info("🎯 All systems operational!")
            self.logger.info(
                f"Started at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC"
            )
            self.logger.info(
                "============================================================"
            )

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
            self.logger.error(
                f"Command error in {interaction.command.name if interaction.command else 'unknown command'}: {error}"
            )
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
        except:
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


# Help command
@discord.app_commands.command(
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
    help_text = "🚀 **Astra Help**\nHere are the available commands and categories:\n"

    for category_key, category_data in categories.items():
        if category_data["commands"]:
            help_text += f"\n**{category_data['name']}**\n"
            help_text += (
                "\n".join([f"• {cmd}" for cmd in category_data["commands"]]) + "\n"
            )

    help_text += "\nUse the command to see specific options and parameters"

    await interaction.response.send_message(help_text)


# Ping command
@discord.app_commands.command(
    name="ping", description="Check bot latency and response time"
)
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


# Invite command
@discord.app_commands.command(
    name="invite", description="Get an invite link for the bot"
)
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
                    label="Invite Bot", url=invite_url, style=discord.ButtonStyle.url
                )
            )

    await interaction.response.send_message(
        embed=embed, view=InviteView(), ephemeral=True
    )


# Run the bot with proper error handling
async def main():
    """Main function to start and run the bot with proper error handling"""
    try:
        logger = logging.getLogger("Astra")
        logger.info(
            f"🚀 Starting {config_manager.get('bot_settings.name', 'Astra')} Discord Bot v{config_manager.get('bot_settings.version', '1.0.0')}..."
        )

        # Create bot instance
        bot = AstraBot()

        # Register the commands
        bot.tree.add_command(help_command)
        bot.tree.add_command(ping_command)
        bot.tree.add_command(invite_command)

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
    except discord.LoginFailure:
        logger.critical(
            "❌ Invalid Discord token. Please check your token and try again."
        )
    except Exception as e:
        logger.critical(f"❌ An unexpected error occurred: {e}")
        logger.critical(traceback.format_exc())


# Run the bot
if __name__ == "__main__":
    # Create a new event loop and run the main function
    asyncio.run(main())
