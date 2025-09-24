"""
🚀 ASTRABOT 2.0 - STREAMLINED EDITION
Lean, efficient Discord bot with AI conversation and interacti    # Load token from environment or config
    token = os.getenv('DISCORD_TOKEN')

    if not token:
        try:
            with open('config.json', 'r') as f:
                import json
                config = json.load(f)
                # Try multiple possible token locations in config
                token = (config.get('discord', {}).get('token') or
                        config.get('discord_token') or
                        config.get('token'))
        except FileNotFoundError:
            logger.error("❌ No config.json found and DISCORD_TOKEN not set")
            returnReplaces bloated bot.1.0.py with clean 100-line implementation
"""

import asyncio
import logging
import os
import sys
import discord
from discord.ext import commands

# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv()
    print("✅ Environment variables loaded from .env")
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment only")

# Import our streamlined core system
from core import startup_core

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    handlers=[logging.FileHandler("logs/astra.log"), logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("astra.main")


class AstraBot(commands.Bot):
    """Streamlined AstraBot with core system integration"""

    def __init__(self):
        # Bot configuration
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        intents.members = True

        super().__init__(
            command_prefix=self.get_prefix,
            intents=intents,
            help_command=None,
            case_insensitive=True,
        )

        self.core_system = None

    async def get_prefix(self, message):
        """Dynamic prefix - responds to mention or 'astra'"""
        prefixes = [
            f"<@{self.user.id}> ",
            f"<@!{self.user.id}> ",
            "astra ",
            "hey astra ",
            "!",
        ]
        return commands.when_mentioned_or(*prefixes)(self, message)

    async def setup_hook(self):
        """Initialize core systems on startup"""
        logger.info("🔧 Setting up AstraBot core systems...")

        try:
            # Initialize our streamlined core system
            self.core_system = await startup_core(self)

            # Load any additional cogs we want to keep
            essential_cogs = [
                "cogs.help",  # Keep help system
                "cogs.utilities",  # Keep basic utilities
                "cogs.stats",  # Keep stats tracking
            ]

            for cog in essential_cogs:
                try:
                    await self.load_extension(cog)
                    logger.info(f"✅ Loaded {cog}")
                except Exception as e:
                    logger.warning(f"⚠️  Could not load {cog}: {e}")

            logger.info("🚀 AstraBot setup complete!")

        except Exception as e:
            logger.error(f"💥 Setup failed: {e}")
            await self.close()

    async def on_ready(self):
        """Bot ready event - handled by core system"""
        logger.info(f"🤖 AstraBot 2.0 Online!")
        logger.info(
            f"📊 Serving {len(self.guilds)} guilds with {len(self.users)} users"
        )

        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="your conversations | Mention me to chat!",
        )
        await self.change_presence(activity=activity, status=discord.Status.online)

    async def close(self):
        """Graceful shutdown"""
        logger.info("🔄 Shutting down AstraBot...")

        if self.core_system:
            await self.core_system.shutdown()

        await super().close()
        logger.info("✅ AstraBot shutdown complete")


async def main():
    """Main bot launcher"""
    # Load token from environment (.env file) or config
    token = os.getenv("DISCORD_TOKEN")

    if not token:
        try:
            with open("config.json", "r") as f:
                import json

                config = json.load(f)
                token = config.get("discord", {}).get("token")
        except FileNotFoundError:
            logger.error("❌ No config.json found and DISCORD_TOKEN not set")
            return

    if not token or token == "YOUR_DISCORD_BOT_TOKEN_HERE":
        logger.error("❌ Discord token not found or is placeholder!")
        logger.error("   Please set DISCORD_TOKEN in .env file or config.json")
        return

    logger.info("🔑 Discord token loaded successfully!")

    # Create and run bot
    bot = AstraBot()

    try:
        logger.info("🚀 Starting AstraBot 2.0...")
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("👋 Received shutdown signal")
    except Exception as e:
        logger.error(f"💥 Bot crashed: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()


if __name__ == "__main__":
    # Run the bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Goodbye!")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)
