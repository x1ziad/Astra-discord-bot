#!/usr/bin/env python3
"""
Debug script to test if AI moderation on_message handler is being called
"""

import asyncio
import discord
from discord.ext import commands
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("debug_message_handler")


class DebugBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def on_ready(self):
        logger.info(f"Debug bot ready: {self.user}")

        # Check if ai_moderation cog is loaded
        ai_mod_cog = self.get_cog("AIModerationCog")
        if ai_mod_cog:
            logger.info("✅ AI Moderation cog is loaded!")

            # Check if the on_message handler exists
            if hasattr(ai_mod_cog, "on_message"):
                logger.info("✅ on_message handler exists in AI moderation cog")
            else:
                logger.error("❌ on_message handler missing from AI moderation cog")
        else:
            logger.error("❌ AI Moderation cog is NOT loaded")

        # List all loaded cogs
        logger.info(f"Loaded cogs: {list(self.cogs.keys())}")

    async def on_message(self, message):
        logger.info(
            f"🔍 MAIN BOT on_message triggered: {message.author} in #{message.channel}: {message.content[:50]}"
        )
        await self.process_commands(message)


async def main():
    """Load the bot with ai_moderation cog and test message handling"""
    import os
    import sys

    # Add the current directory to the path so we can import the cogs
    sys.path.insert(0, "/Users/ziadmekawy/Developer/Discord-Stellaris/AstraBot")

    bot = DebugBot()

    try:
        # Load the AI moderation cog
        await bot.load_extension("cogs.ai_moderation")
        logger.info("✅ Successfully loaded ai_moderation cog")
    except Exception as e:
        logger.error(f"❌ Failed to load ai_moderation cog: {e}")
        return

    # Get token from environment or config
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        try:
            from config.unified_config import unified_config

            token = unified_config.get("bot_token")
        except:
            pass

    if not token:
        logger.error(
            "❌ No Discord token found! Set DISCORD_TOKEN environment variable or check config"
        )
        return

    logger.info("🚀 Starting debug bot...")
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("🛑 Debug bot stopped")
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
