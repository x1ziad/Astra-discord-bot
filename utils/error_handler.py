"""
Enhanced error handling system for Astra Bot
Provides comprehensive error tracking, reporting, and recovery
"""

import discord
from discord.ext import commands
import traceback
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import sys
import os


class ErrorSeverity(Enum):
    """Error severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorReport:
    """Error report data structure"""

    error_id: str
    timestamp: datetime
    severity: ErrorSeverity
    error_type: str
    message: str
    traceback: str
    guild_id: Optional[int] = None
    user_id: Optional[int] = None
    command: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


class ErrorHandler:
    """Enhanced error handling and reporting system"""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("astra.errors")

        # Error tracking
        self.error_count = 0
        self.recent_errors: List[ErrorReport] = []
        self.error_patterns: Dict[str, int] = {}

        # Recovery mechanisms
        self.recovery_callbacks: Dict[str, Callable] = {}
        self.auto_restart_enabled = True
        self.max_errors_per_hour = 50

        # Rate limiting
        self.error_rate_limit: Dict[str, List[datetime]] = {}

    def add_recovery_callback(self, error_type: str, callback: Callable):
        """Add a recovery callback for specific error types"""
        self.recovery_callbacks[error_type] = callback
        self.logger.info(f"Added recovery callback for {error_type}")

    async def handle_error(
        self,
        error: Exception,
        context: Optional[Union[commands.Context, discord.Interaction]] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> ErrorReport:
        """Handle and log an error with context"""

        # Generate error ID
        error_id = (
            f"ERR_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{self.error_count:04d}"
        )
        self.error_count += 1

        # Extract context information
        guild_id = None
        user_id = None
        command = None

        if isinstance(context, commands.Context):
            guild_id = context.guild.id if context.guild else None
            user_id = context.author.id
            command = context.command.name if context.command else None
        elif isinstance(context, discord.Interaction):
            guild_id = context.guild.id if context.guild else None
            user_id = context.user.id
            command = context.command.name if context.command else None

        # Create error report
        error_report = ErrorReport(
            error_id=error_id,
            timestamp=datetime.utcnow(),
            severity=severity,
            error_type=type(error).__name__,
            message=str(error),
            traceback=traceback.format_exc(),
            guild_id=guild_id,
            user_id=user_id,
            command=command,
            context=additional_context or {},
        )

        # Store error
        self.recent_errors.append(error_report)
        if len(self.recent_errors) > 100:  # Keep only recent 100 errors
            self.recent_errors.pop(0)

        # Track error patterns
        error_key = f"{error_report.error_type}:{error_report.command or 'unknown'}"
        self.error_patterns[error_key] = self.error_patterns.get(error_key, 0) + 1

        # Log error based on severity
        log_msg = f"[{error_id}] {error_report.error_type}: {error_report.message}"

        if severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_msg, exc_info=error)
        elif severity == ErrorSeverity.HIGH:
            self.logger.error(log_msg, exc_info=error)
        elif severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_msg)
        else:
            self.logger.info(log_msg)

        # Attempt recovery
        await self._attempt_recovery(error_report)

        # Send user notification if context available
        if context and not self._is_rate_limited(error_key):
            await self._send_user_notification(context, error_report)

        return error_report

    async def _attempt_recovery(self, error_report: ErrorReport):
        """Attempt to recover from the error"""
        error_type = error_report.error_type

        if error_type in self.recovery_callbacks:
            try:
                await self.recovery_callbacks[error_type](error_report)
                self.logger.info(f"Recovery callback executed for {error_type}")
            except Exception as e:
                self.logger.error(f"Recovery callback failed for {error_type}: {e}")

    def _is_rate_limited(self, error_key: str) -> bool:
        """Check if error notifications are rate limited"""
        now = datetime.utcnow()
        if error_key not in self.error_rate_limit:
            self.error_rate_limit[error_key] = []

        # Clean old timestamps
        self.error_rate_limit[error_key] = [
            ts
            for ts in self.error_rate_limit[error_key]
            if now - ts < timedelta(minutes=5)
        ]

        # Check rate limit (max 3 notifications per 5 minutes)
        if len(self.error_rate_limit[error_key]) >= 3:
            return True

        self.error_rate_limit[error_key].append(now)
        return False

    async def _send_user_notification(
        self,
        context: Union[commands.Context, discord.Interaction],
        error_report: ErrorReport,
    ):
        """Send user-friendly error notification"""

        # Create user-friendly error embed
        embed = discord.Embed(
            title="❌ Something went wrong",
            color=0xF04747,
            timestamp=error_report.timestamp,
        )

        # Add appropriate message based on error type
        if error_report.error_type == "CommandNotFound":
            embed.description = (
                "That command doesn't exist. Use `/help` to see available commands."
            )
        elif error_report.error_type == "MissingPermissions":
            embed.description = "You don't have permission to use this command."
        elif error_report.error_type == "BotMissingPermissions":
            embed.description = (
                "I don't have the necessary permissions to execute this command."
            )
        elif error_report.error_type == "CommandOnCooldown":
            embed.description = "This command is on cooldown. Please try again later."
        else:
            embed.description = "An unexpected error occurred. The issue has been logged and will be investigated."

        embed.add_field(
            name="Error ID", value=f"`{error_report.error_id}`", inline=True
        )

        if error_report.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            embed.add_field(
                name="Status", value="🔧 Attempting automatic recovery...", inline=True
            )

        try:
            if isinstance(context, commands.Context):
                await context.send(embed=embed, delete_after=30)
            elif isinstance(context, discord.Interaction):
                if context.response.is_done():
                    await context.followup.send(embed=embed, ephemeral=True)
                else:
                    await context.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            self.logger.error(f"Failed to send error notification: {e}")

    async def handle_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        """Handle command-specific errors"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore command not found errors

        severity = ErrorSeverity.MEDIUM

        if isinstance(
            error, (commands.BotMissingPermissions, commands.MissingPermissions)
        ):
            severity = ErrorSeverity.LOW
        elif isinstance(error, commands.CommandInvokeError):
            severity = ErrorSeverity.HIGH
            error = error.original  # Get the original error

        await self.handle_error(error, ctx, severity)

    async def handle_app_command_error(
        self,
        interaction: discord.Interaction,
        error: discord.app_commands.AppCommandError,
    ):
        """Handle application command errors"""
        severity = ErrorSeverity.MEDIUM

        if isinstance(error, discord.app_commands.BotMissingPermissions):
            severity = ErrorSeverity.LOW
        elif isinstance(error, discord.app_commands.CommandInvokeError):
            severity = ErrorSeverity.HIGH
            error = error.original

        await self.handle_error(error, interaction, severity)

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        now = datetime.utcnow()
        recent_errors = [
            err
            for err in self.recent_errors
            if now - err.timestamp < timedelta(hours=1)
        ]

        return {
            "total_errors": self.error_count,
            "recent_errors_count": len(recent_errors),
            "error_patterns": dict(
                sorted(self.error_patterns.items(), key=lambda x: x[1], reverse=True)[
                    :10
                ]
            ),
            "most_recent_error": (
                self.recent_errors[-1].timestamp if self.recent_errors else None
            ),
        }

    async def cleanup(self):
        """Clean up error handler resources"""
        self.recent_errors.clear()
        self.error_patterns.clear()
        self.error_rate_limit.clear()
        self.logger.info("Error handler cleaned up")


# Global error handler setup function
async def setup_error_handler(bot) -> ErrorHandler:
    """Set up the global error handler for the bot"""
    error_handler = ErrorHandler(bot)

    # Set up error event handlers
    @bot.event
    async def on_command_error(ctx, error):
        await error_handler.handle_command_error(ctx, error)

    @bot.tree.error
    async def on_app_command_error(interaction, error):
        await error_handler.handle_app_command_error(interaction, error)

    return error_handler
