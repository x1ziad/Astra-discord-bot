"""
Centralized error handling for Astra Bot
"""

import logging
import traceback
from typing import Any, Optional
import discord
from discord.ext import commands

logger = logging.getLogger("astra.errors")


class ErrorHandler:
    """Centralized error handling"""

    @staticmethod
    async def handle_command_error(ctx: commands.Context, error: Exception):
        """Handle command errors with user-friendly messages"""

        error_messages = {
            commands.CommandNotFound: None,  # Ignore
            commands.CommandOnCooldown: f"⏰ Command on cooldown. Try again in {error.retry_after:.1f}s",
            commands.MissingPermissions: "❌ You don't have permission to use this command.",
            commands.MissingRequiredArgument: f"❌ Missing required argument: `{error.param.name}`",
            commands.BadArgument: "❌ Invalid argument provided.",
            commands.NoPrivateMessage: "❌ This command cannot be used in private messages.",
            commands.DisabledCommand: "❌ This command is currently disabled.",
        }

        message = error_messages.get(type(error))
        if message:
            await ctx.send(message)
        elif message is not None:  # Not CommandNotFound
            logger.error(f"Unhandled command error: {error}")
            await ctx.send("❌ An unexpected error occurred.")

    @staticmethod
    def log_error(error: Exception, context: str = "Unknown"):
        """Log error with context"""
        logger.error(f"Error in {context}: {error}")
        logger.debug(traceback.format_exc())
