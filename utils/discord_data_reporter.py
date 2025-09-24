"""
Discord Data Reporter
Sends diagnostics, reports, logs, and analytics data directly to Discord channels
instead of storing in local database files to improve performance.
"""

import asyncio
import json
import logging
import traceback
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from collections import defaultdict
from io import StringIO

import discord
from discord.ext import tasks

logger = logging.getLogger("astra.discord_reporter")


@dataclass
class ChannelConfig:
    """Configuration for Discord channel reporting"""

    diagnostics_channel_id: int = 1419516681427882115
    logs_channel_id: int = 1419517784135700561
    analytics_channel_id: int = 1419858425424253039
    performance_channel_id: int = 1420213631030661130  # New continuous performance monitoring


class DiscordDataReporter:
    """
    Manages sending all bot data, analytics, diagnostics, and logs
    directly to Discord channels instead of local file storage
    """

    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.config = ChannelConfig()
        self.logger = logger

        # Channel objects (will be loaded when bot is ready)
        self.diagnostics_channel: Optional[discord.TextChannel] = None
        self.logs_channel: Optional[discord.TextChannel] = None
        self.analytics_channel: Optional[discord.TextChannel] = None
        self.performance_channel: Optional[discord.TextChannel] = None

        # Data buffers for batching
        self.analytics_buffer: List[Dict[str, Any]] = []
        self.logs_buffer: List[Dict[str, Any]] = []
        self.diagnostics_buffer: List[Dict[str, Any]] = []
        self.performance_buffer: List[Dict[str, Any]] = []

        # Background tasks
        self.batch_send_task = None
        self.daily_report_task = None

    async def initialize(self):
        """Initialize the Discord channel reporter"""
        try:
            # Get channel objects
            self.diagnostics_channel = self.bot.get_channel(
                self.config.diagnostics_channel_id
            )
            self.logs_channel = self.bot.get_channel(self.config.logs_channel_id)
            self.analytics_channel = self.bot.get_channel(
                self.config.analytics_channel_id
            )
            self.performance_channel = self.bot.get_channel(
                self.config.performance_channel_id
            )

            # Verify channels exist
            channels_status = {
                "Diagnostics": self.diagnostics_channel is not None,
                "Logs": self.logs_channel is not None,
                "Analytics": self.analytics_channel is not None,
                "Performance": self.performance_channel is not None,
            }

            missing_channels = [
                name for name, exists in channels_status.items() if not exists
            ]

            if missing_channels:
                self.logger.warning(
                    f"⚠️ Could not find channels: {', '.join(missing_channels)}"
                )
            else:
                self.logger.info("✅ All reporting channels found and ready")

            # Start background tasks
            self.start_background_tasks()

            # Send initialization message
            await self.send_diagnostics(
                {
                    "event": "discord_reporter_initialized",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "channels_status": channels_status,
                    "message": "Discord Data Reporter is now active",
                }
            )

        except Exception as e:
            self.logger.error(f"Failed to initialize Discord reporter: {e}")

    def start_background_tasks(self):
        """Start background tasks for batched sending"""
        if not self.batch_send_task or self.batch_send_task.done():
            self.batch_send_task = asyncio.create_task(self._batch_send_loop())

        if not self.daily_report_task or self.daily_report_task.done():
            self.daily_report_task = asyncio.create_task(self._daily_report_loop())

    def stop_background_tasks(self):
        """Stop all background tasks"""
        if self.batch_send_task and not self.batch_send_task.done():
            self.batch_send_task.cancel()

        if self.daily_report_task and not self.daily_report_task.done():
            self.daily_report_task.cancel()

    async def _batch_send_loop(self):
        """Background task to send batched data every 2 minutes"""
        while True:
            try:
                await asyncio.sleep(120)  # 2 minutes
                await self.flush_all_buffers()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Batch send loop error: {e}")

    async def _daily_report_loop(self):
        """Background task for daily summary reports"""
        while True:
            try:
                # Wait until midnight UTC
                now = datetime.now(timezone.utc)
                tomorrow = now.replace(
                    hour=0, minute=0, second=0, microsecond=0
                ) + timedelta(days=1)
                sleep_seconds = (tomorrow - now).total_seconds()

                await asyncio.sleep(sleep_seconds)
                await self.send_daily_summary()

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Daily report loop error: {e}")

    async def send_analytics(self, data: Dict[str, Any], immediate: bool = False):
        """Send analytics data to analytics channel"""
        analytics_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "analytics",
            "data": data,
        }

        if immediate:
            await self._send_to_channel(
                self.analytics_channel, analytics_entry, "📊 Analytics Data"
            )
        else:
            self.analytics_buffer.append(analytics_entry)

    async def send_diagnostics(self, data: Dict[str, Any], immediate: bool = False):
        """Send diagnostics data to diagnostics channel"""
        diagnostics_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "diagnostics",
            "data": data,
        }

        if immediate:
            await self._send_to_channel(
                self.diagnostics_channel, diagnostics_entry, "🔬 Diagnostics Report"
            )
        else:
            self.diagnostics_buffer.append(diagnostics_entry)

    async def send_logs(self, data: Dict[str, Any], immediate: bool = False):
        """Send log data to logs channel"""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "log",
            "data": data,
        }

        if immediate:
            await self._send_to_channel(self.logs_channel, log_entry, "📝 Log Entry")
        else:
            self.logs_buffer.append(log_entry)

    async def send_error_report(
        self,
        error: Exception,
        context: str = "",
        guild_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ):
        """Send error report immediately to logs channel"""
        error_data = {
            "event": "error_report",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "guild_id": guild_id,
            "user_id": user_id,
            "traceback": traceback.format_exc(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        await self.send_logs(error_data, immediate=True)

    async def send_performance_report(self, metrics: Dict[str, Any]):
        """Send performance metrics to diagnostics channel"""
        performance_data = {
            "event": "performance_report",
            "metrics": metrics,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        await self.send_diagnostics(performance_data, immediate=False)

    async def send_command_usage(
        self,
        command_name: str,
        user_id: int,
        guild_id: Optional[int] = None,
        execution_time: float = 0.0,
        success: bool = True,
    ):
        """Send command usage analytics"""
        usage_data = {
            "event": "command_usage",
            "command_name": command_name,
            "user_id": user_id,
            "guild_id": guild_id,
            "execution_time": execution_time,
            "success": success,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        await self.send_analytics(usage_data, immediate=False)

    async def send_user_activity(
        self, guild_id: int, user_id: int, activity_type: str, details: Dict[str, Any]
    ):
        """Send user activity analytics"""
        activity_data = {
            "event": "user_activity",
            "guild_id": guild_id,
            "user_id": user_id,
            "activity_type": activity_type,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        await self.send_analytics(activity_data, immediate=False)

    async def send_continuous_performance(self, detailed_metrics: Dict[str, Any], immediate: bool = False):
        """Send detailed continuous performance monitoring data to dedicated performance channel"""
        performance_data = {
            "event": "continuous_performance_monitoring",
            "detailed_metrics": detailed_metrics,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if immediate:
            await self._send_to_channel(
                self.performance_channel,
                performance_data,
                "⚡ **CONTINUOUS PERFORMANCE MONITORING**"
            )
        else:
            self.performance_buffer.append(performance_data)

    async def flush_all_buffers(self):
        """Send all buffered data to respective channels"""
        try:
            # Send analytics buffer
            if self.analytics_buffer:
                await self._send_batch_to_channel(
                    self.analytics_channel,
                    self.analytics_buffer.copy(),
                    "📊 Analytics Batch Report",
                )
                self.analytics_buffer.clear()

            # Send logs buffer
            if self.logs_buffer:
                await self._send_batch_to_channel(
                    self.logs_channel, self.logs_buffer.copy(), "📝 Logs Batch Report"
                )
                self.logs_buffer.clear()

            # Send diagnostics buffer
            if self.diagnostics_buffer:
                await self._send_batch_to_channel(
                    self.diagnostics_channel,
                    self.diagnostics_buffer.copy(),
                    "🔬 Diagnostics Batch Report",
                )
                self.diagnostics_buffer.clear()

            # Send performance buffer
            if self.performance_buffer:
                await self._send_batch_to_channel(
                    self.performance_channel,
                    self.performance_buffer.copy(),
                    "⚡ Performance Monitoring Report",
                )
                self.performance_buffer.clear()

            self.logger.debug("All data buffers flushed to Discord channels")

        except Exception as e:
            self.logger.error(f"Error flushing buffers: {e}")

    async def _send_to_channel(
        self, channel: Optional[discord.TextChannel], data: Dict[str, Any], title: str
    ):
        """Send individual data entry to a Discord channel"""
        if not channel:
            return

        try:
            # Create embed for better formatting
            embed = discord.Embed(
                title=title,
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc),
            )

            # Add main data
            if "event" in data.get("data", {}):
                embed.add_field(name="Event", value=data["data"]["event"], inline=True)

            # Add data as JSON in code block (truncated if too long)
            json_data = json.dumps(data, indent=2, default=str)
            if len(json_data) > 1000:
                json_data = json_data[:997] + "..."

            embed.add_field(
                name="Data", value=f"```json\n{json_data}\n```", inline=False
            )

            await channel.send(embed=embed)

        except Exception as e:
            # Fallback to plain text if embed fails
            try:
                content = f"**{title}**\n```json\n{json.dumps(data, indent=2, default=str)[:1800]}\n```"
                await channel.send(content)
            except Exception as e2:
                self.logger.error(
                    f"Failed to send data to channel {channel.id}: {e}, {e2}"
                )

    async def _send_batch_to_channel(
        self,
        channel: Optional[discord.TextChannel],
        data_list: List[Dict[str, Any]],
        title: str,
    ):
        """Send batch of data entries to a Discord channel"""
        if not channel or not data_list:
            return

        try:
            # Create summary embed
            embed = discord.Embed(
                title=title,
                description=f"Batch of {len(data_list)} entries",
                color=discord.Color.green(),
                timestamp=datetime.now(timezone.utc),
            )

            # Add summary statistics
            event_counts = defaultdict(int)
            for item in data_list:
                event_type = item.get("data", {}).get(
                    "event", item.get("type", "unknown")
                )
                event_counts[event_type] += 1

            summary_text = "\n".join(
                [f"• {event}: {count}" for event, count in event_counts.items()]
            )
            embed.add_field(
                name="Event Summary", value=summary_text or "Mixed events", inline=False
            )

            await channel.send(embed=embed)

            # Send detailed data in file if batch is large
            if len(data_list) > 10:
                json_content = json.dumps(data_list, indent=2, default=str)
                file = discord.File(
                    fp=StringIO(json_content),
                    filename=f"batch_data_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json",
                )
                await channel.send("Detailed data:", file=file)
            else:
                # Send individual entries for small batches
                for i, item in enumerate(data_list[:5]):  # Limit to 5 to avoid spam
                    json_data = json.dumps(item, indent=2, default=str)
                    if len(json_data) > 1000:
                        json_data = json_data[:997] + "..."
                    await channel.send(f"```json\n{json_data}\n```")

        except Exception as e:
            self.logger.error(f"Failed to send batch to channel {channel.id}: {e}")

    async def send_daily_summary(self):
        """Send daily summary report to diagnostics channel"""
        try:
            summary_data = {
                "event": "daily_summary",
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "bot_stats": {
                    "guilds": len(self.bot.guilds),
                    "users": len(set(self.bot.get_all_members())),
                    "uptime": "calculated_runtime",  # Would be calculated from bot start time
                },
                "system_stats": await self._get_system_stats(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            await self.send_diagnostics(summary_data, immediate=True)

        except Exception as e:
            self.logger.error(f"Failed to send daily summary: {e}")

    async def _get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        try:
            import psutil

            process = psutil.Process()
            return {
                "cpu_percent": process.cpu_percent(),
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "threads": process.num_threads(),
                "connections": len(process.connections()),
                "uptime_seconds": (
                    datetime.now() - datetime.fromtimestamp(process.create_time())
                ).total_seconds(),
            }
        except Exception as e:
            return {"error": f"Could not collect system stats: {e}"}

    async def test_channels(self):
        """Test all configured channels by sending test messages"""
        test_data = {
            "event": "channel_test",
            "message": "Testing Discord Data Reporter channels",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        channels = [
            (self.analytics_channel, "Analytics"),
            (self.diagnostics_channel, "Diagnostics"), 
            (self.logs_channel, "Logs"),
            (self.performance_channel, "Performance"),
        ]

        results = {}
        for channel, name in channels:
            try:
                if channel:
                    await self._send_to_channel(
                        channel, {"data": test_data}, f"🧪 {name} Channel Test"
                    )
                    results[name] = "✅ Success"
                else:
                    results[name] = "❌ Channel not found"
            except Exception as e:
                results[name] = f"❌ Error: {str(e)}"

        return results


# Global instance
discord_reporter: Optional[DiscordDataReporter] = None


async def initialize_discord_reporter(bot: discord.Client):
    """Initialize the global Discord data reporter"""
    global discord_reporter

    try:
        discord_reporter = DiscordDataReporter(bot)
        await discord_reporter.initialize()
        logger.info("✅ Discord Data Reporter initialized successfully")
        return discord_reporter
    except Exception as e:
        logger.error(f"❌ Failed to initialize Discord Data Reporter: {e}")
        return None


def get_discord_reporter() -> Optional[DiscordDataReporter]:
    """Get the global Discord data reporter instance"""
    return discord_reporter


async def cleanup_discord_reporter():
    """Cleanup the Discord data reporter"""
    global discord_reporter

    if discord_reporter:
        try:
            # Flush any remaining data
            await discord_reporter.flush_all_buffers()

            # Stop background tasks
            discord_reporter.stop_background_tasks()

            logger.info("✅ Discord Data Reporter cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during Discord reporter cleanup: {e}")
        finally:
            discord_reporter = None
