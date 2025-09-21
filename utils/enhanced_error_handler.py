"""
Enhanced Error Handling Utilities for Astra Bot
Provides comprehensive error handling decorators and utilities
"""

import discord
from discord.ext import commands
import logging
import traceback
import functools
from typing import Any, Callable, Optional
from datetime import datetime, timezone

logger = logging.getLogger("astra.error_handling")


def handle_command_errors(ephemeral: bool = True, log_errors: bool = True):
    """
    Decorator for handling command errors comprehensively

    Args:
        ephemeral: Whether error messages should be ephemeral
        log_errors: Whether errors should be logged
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract interaction from args
            interaction = None
            for arg in args:
                if isinstance(arg, discord.Interaction):
                    interaction = arg
                    break

            if not interaction:
                # Fallback to original function if no interaction found
                return await func(*args, **kwargs)

            try:
                return await func(*args, **kwargs)

            except discord.InteractionResponseError:
                # Handle case where interaction was already responded to
                if log_errors:
                    logger.error(f"Interaction already responded to in {func.__name__}")
                try:
                    if not interaction.response.is_done():
                        await interaction.response.send_message(
                            "❌ An interaction error occurred", ephemeral=ephemeral
                        )
                    else:
                        await interaction.followup.send(
                            "❌ An interaction error occurred", ephemeral=ephemeral
                        )
                except:
                    pass  # Don't crash on error handling

            except discord.Forbidden:
                if log_errors:
                    logger.warning(f"Missing permissions in {func.__name__}")
                try:
                    if not interaction.response.is_done():
                        await interaction.response.send_message(
                            "❌ I don't have permission to perform this action",
                            ephemeral=ephemeral,
                        )
                    else:
                        await interaction.followup.send(
                            "❌ I don't have permission to perform this action",
                            ephemeral=ephemeral,
                        )
                except:
                    pass

            except discord.NotFound:
                if log_errors:
                    logger.warning(f"Resource not found in {func.__name__}")
                try:
                    if not interaction.response.is_done():
                        await interaction.response.send_message(
                            "❌ The requested resource was not found",
                            ephemeral=ephemeral,
                        )
                    else:
                        await interaction.followup.send(
                            "❌ The requested resource was not found",
                            ephemeral=ephemeral,
                        )
                except:
                    pass

            except discord.HTTPException as e:
                if log_errors:
                    logger.error(f"Discord HTTP error in {func.__name__}: {e}")
                try:
                    if not interaction.response.is_done():
                        await interaction.response.send_message(
                            f"❌ Discord API error: {str(e)[:100]}", ephemeral=ephemeral
                        )
                    else:
                        await interaction.followup.send(
                            f"❌ Discord API error: {str(e)[:100]}", ephemeral=ephemeral
                        )
                except:
                    pass

            except Exception as e:
                if log_errors:
                    logger.error(f"Unexpected error in {func.__name__}: {e}")
                    logger.error(f"Traceback: {traceback.format_exc()}")

                try:
                    error_msg = f"❌ An unexpected error occurred: {str(e)[:100]}"
                    if not interaction.response.is_done():
                        await interaction.response.send_message(
                            error_msg, ephemeral=ephemeral
                        )
                    else:
                        await interaction.followup.send(error_msg, ephemeral=ephemeral)
                except:
                    # Last resort - try to log that we couldn't send error message
                    if log_errors:
                        logger.error(
                            f"Failed to send error message for {func.__name__}"
                        )

        return wrapper

    return decorator


def handle_listener_errors(log_errors: bool = True):
    """
    Decorator for handling event listener errors

    Args:
        log_errors: Whether errors should be logged
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(f"Error in listener {func.__name__}: {e}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                # Don't re-raise in listeners to prevent bot crashes

        return wrapper

    return decorator


class ErrorHandler:
    """Enhanced error handler for the bot"""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("astra.error_handler")

    async def handle_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        """Handle traditional command errors"""
        try:
            if isinstance(error, commands.CommandNotFound):
                return  # Ignore unknown commands

            elif isinstance(error, commands.MissingRequiredArgument):
                await ctx.send(
                    f"❌ Missing required argument: `{error.param.name}`\n"
                    f"Use `{ctx.prefix}help {ctx.command}` for usage information.",
                    delete_after=10,
                )

            elif isinstance(error, commands.BadArgument):
                await ctx.send(
                    f"❌ Invalid argument provided.\n"
                    f"Use `{ctx.prefix}help {ctx.command}` for usage information.",
                    delete_after=10,
                )

            elif isinstance(error, commands.CommandOnCooldown):
                await ctx.send(
                    f"⏰ Command on cooldown! Try again in {error.retry_after:.1f} seconds.",
                    delete_after=5,
                )

            elif isinstance(error, commands.MissingPermissions):
                perms = ", ".join(error.missing_permissions)
                await ctx.send(
                    f"❌ You need the following permissions: {perms}", delete_after=10
                )

            elif isinstance(error, commands.BotMissingPermissions):
                perms = ", ".join(error.missing_permissions)
                await ctx.send(
                    f"❌ I need the following permissions: {perms}", delete_after=10
                )

            elif isinstance(error, commands.NoPrivateMessage):
                await ctx.send("❌ This command cannot be used in DMs.", delete_after=5)

            elif isinstance(error, discord.Forbidden):
                await ctx.send(
                    "❌ I don't have permission to perform this action.",
                    delete_after=10,
                )

            elif isinstance(error, discord.NotFound):
                await ctx.send(
                    "❌ The requested resource was not found.", delete_after=10
                )

            else:
                # Log unexpected errors
                self.logger.error(f"Unexpected command error: {error}")
                self.logger.error(f"Traceback: {traceback.format_exc()}")

                await ctx.send(
                    "❌ An unexpected error occurred. The issue has been logged.",
                    delete_after=10,
                )

        except Exception as e:
            self.logger.error(f"Error in error handler: {e}")


# Utility functions for common error scenarios
async def safe_send_message(
    channel, content: str = None, embed: discord.Embed = None, **kwargs
):
    """Safely send a message with error handling"""
    try:
        return await channel.send(content=content, embed=embed, **kwargs)
    except discord.Forbidden:
        logger.warning(f"Missing permission to send message in {channel}")
    except discord.HTTPException as e:
        logger.error(f"HTTP error sending message: {e}")
    except Exception as e:
        logger.error(f"Unexpected error sending message: {e}")
    return None


async def safe_edit_message(
    message: discord.Message, content: str = None, embed: discord.Embed = None, **kwargs
):
    """Safely edit a message with error handling"""
    try:
        return await message.edit(content=content, embed=embed, **kwargs)
    except discord.Forbidden:
        logger.warning(f"Missing permission to edit message")
    except discord.NotFound:
        logger.warning(f"Message not found for editing")
    except discord.HTTPException as e:
        logger.error(f"HTTP error editing message: {e}")
    except Exception as e:
        logger.error(f"Unexpected error editing message: {e}")
    return None


async def safe_delete_message(message: discord.Message):
    """Safely delete a message with error handling"""
    try:
        await message.delete()
        return True
    except discord.Forbidden:
        logger.warning(f"Missing permission to delete message")
    except discord.NotFound:
        logger.warning(f"Message not found for deletion")
    except discord.HTTPException as e:
        logger.error(f"HTTP error deleting message: {e}")
    except Exception as e:
        logger.error(f"Unexpected error deleting message: {e}")
    return False
