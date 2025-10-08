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
    performance_channel_id: int = (
        1420213631030661130  # New continuous performance monitoring
    )


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
        self.continuous_monitoring_task = None

        # Automatic data collection flags
        self.auto_capture_enabled = True
        self.realtime_streaming = True

        # Zero local storage policy - everything goes to Discord immediately
        self.zero_local_storage = True

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

            # Debug logging for performance channel
            if self.performance_channel:
                self.logger.info(
                    f"✅ Performance channel initialized: {self.performance_channel.name} (ID: {self.performance_channel.id})"
                )
            else:
                self.logger.error(
                    f"❌ Performance channel not found with ID: {self.config.performance_channel_id}"
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
            self.logger.error(f"Error sending daily summary: {e}")

    # =============================================
    # CONTINUOUS AUTOMATION SYSTEM
    # =============================================

    async def start_continuous_automation(self):
        """Start all continuous automation tasks"""
        if not self.auto_capture_enabled:
            return

        try:
            # Start all continuous tasks
            asyncio.create_task(self._continuous_system_monitoring())
            asyncio.create_task(self._continuous_bot_health_check())
            asyncio.create_task(self._continuous_performance_tracking())
            asyncio.create_task(self._continuous_error_monitoring())
            asyncio.create_task(self._continuous_storage_enforcement())

            await self.send_diagnostics(
                {
                    "event": "continuous_automation_started",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "message": "All continuous automation tasks initialized",
                    "zero_local_storage": self.zero_local_storage,
                    "realtime_streaming": self.realtime_streaming,
                },
                immediate=True,
            )

        except Exception as e:
            self.logger.error(f"Error starting continuous automation: {e}")

    async def _continuous_system_monitoring(self):
        """Continuously monitor and report system metrics every 2 minutes"""
        while self.auto_capture_enabled:
            try:
                await asyncio.sleep(120)  # 2 minutes

                # Capture current system state
                system_metrics = await self._capture_system_snapshot()
                await self.send_performance(
                    system_metrics, immediate=self.realtime_streaming
                )

                # Enforce zero local storage
                if self.zero_local_storage:
                    await self.enforce_zero_local_storage()

            except Exception as e:
                await self.auto_capture_error_event(e, "continuous_system_monitoring")
                await asyncio.sleep(60)  # Wait before retry

    async def _continuous_bot_health_check(self):
        """Continuously check bot health and report every 3 minutes"""
        while self.auto_capture_enabled:
            try:
                await asyncio.sleep(180)  # 3 minutes

                # Capture bot health metrics
                health_data = await self._capture_bot_health_snapshot()
                await self.send_diagnostics(
                    health_data, immediate=self.realtime_streaming
                )

            except Exception as e:
                await self.auto_capture_error_event(e, "continuous_bot_health_check")
                await asyncio.sleep(60)

    async def _continuous_performance_tracking(self):
        """Continuously track performance metrics every 1 minute"""
        while self.auto_capture_enabled:
            try:
                await asyncio.sleep(60)  # 1 minute

                # Capture performance snapshot
                perf_data = await self._capture_performance_snapshot()
                await self.send_performance(
                    perf_data, immediate=self.realtime_streaming
                )

            except Exception as e:
                await self.auto_capture_error_event(
                    e, "continuous_performance_tracking"
                )
                await asyncio.sleep(30)

    async def _continuous_error_monitoring(self):
        """Continuously monitor for errors and anomalies every 90 seconds"""
        while self.auto_capture_enabled:
            try:
                await asyncio.sleep(90)  # 1.5 minutes

                # Check for any system errors or anomalies
                error_check = await self._check_system_errors()
                if error_check.get("has_errors"):
                    await self.send_logs(error_check, immediate=True)

            except Exception as e:
                await self.auto_capture_error_event(e, "continuous_error_monitoring")
                await asyncio.sleep(45)

    async def _continuous_storage_enforcement(self):
        """Continuously enforce zero local storage every 30 seconds"""
        while self.auto_capture_enabled and self.zero_local_storage:
            try:
                await asyncio.sleep(30)  # 30 seconds
                await self.enforce_zero_local_storage()

            except Exception as e:
                await self.auto_capture_error_event(e, "continuous_storage_enforcement")
                await asyncio.sleep(15)

    async def _capture_system_snapshot(self) -> dict:
        """Capture a comprehensive system snapshot"""
        try:
            import psutil

            # Get CPU info
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()

            # Get memory info
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            # Get disk info
            disk = psutil.disk_usage("/")

            # Get network info
            network = psutil.net_io_counters()

            return {
                "event": "system_snapshot",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "cpu": {
                    "percent": cpu_percent,
                    "frequency": cpu_freq.current if cpu_freq else None,
                    "cores": psutil.cpu_count(),
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                },
                "swap": {
                    "total": swap.total,
                    "used": swap.used,
                    "percent": swap.percent,
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100,
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv,
                },
                "automatic_capture": True,
            }

        except Exception as e:
            return {
                "event": "system_snapshot_error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "automatic_capture": True,
            }

    async def _capture_bot_health_snapshot(self) -> dict:
        """Capture bot health metrics"""
        try:
            bot = self.bot

            return {
                "event": "bot_health_snapshot",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "bot_latency": round(bot.latency * 1000, 2),  # Convert to ms
                "guild_count": len(bot.guilds),
                "user_count": len(bot.users),
                "cog_count": len(bot.cogs),
                "command_count": len([cmd for cmd in bot.walk_commands()]),
                "is_ready": bot.is_ready(),
                "is_closed": bot.is_closed(),
                "uptime": (
                    str(datetime.now(timezone.utc) - bot.uptime)
                    if hasattr(bot, "uptime")
                    else "Unknown"
                ),
                "automatic_capture": True,
            }

        except Exception as e:
            return {
                "event": "bot_health_error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "automatic_capture": True,
            }

    async def _capture_performance_snapshot(self) -> dict:
        """Capture performance metrics"""
        try:
            import psutil
            import gc

            # Get process info
            process = psutil.Process()

            return {
                "event": "performance_snapshot",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "process": {
                    "cpu_percent": process.cpu_percent(),
                    "memory_percent": process.memory_percent(),
                    "memory_info": process.memory_info()._asdict(),
                    "num_threads": process.num_threads(),
                    "num_fds": (
                        process.num_fds() if hasattr(process, "num_fds") else None
                    ),
                },
                "python": {"gc_counts": gc.get_count(), "gc_stats": gc.get_stats()},
                "bot_latency": round(self.bot.latency * 1000, 2) if self.bot else None,
                "automatic_capture": True,
            }

        except Exception as e:
            return {
                "event": "performance_snapshot_error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "automatic_capture": True,
            }

    async def _check_system_errors(self) -> dict:
        """Check for system errors and anomalies"""
        try:
            import psutil

            errors = []

            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                errors.append(f"High CPU usage: {cpu_percent}%")

            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                errors.append(f"High memory usage: {memory.percent}%")

            # Check disk usage
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100
            if disk_percent > 90:
                errors.append(f"High disk usage: {disk_percent:.1f}%")

            # Check bot latency
            if self.bot and self.bot.latency > 1.0:  # 1 second
                errors.append(
                    f"High bot latency: {round(self.bot.latency * 1000, 2)}ms"
                )

            return {
                "event": "system_error_check",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "has_errors": len(errors) > 0,
                "errors": errors,
                "automatic_capture": True,
            }

        except Exception as e:
            return {
                "event": "system_error_check_failed",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "has_errors": True,
                "automatic_capture": True,
            }

    async def flush_analytics_buffer(self):
        """Flush analytics buffer to analytics channel"""
        if self.analytics_buffer:
            await self._send_batch_to_channel(
                self.analytics_channel,
                self.analytics_buffer.copy(),
                "📊 Analytics Batch Report",
            )
            self.analytics_buffer.clear()

    async def flush_logs_buffer(self):
        """Flush logs buffer to logs channel"""
        if self.logs_buffer:
            await self._send_batch_to_channel(
                self.logs_channel, self.logs_buffer.copy(), "📝 Logs Batch Report"
            )
            self.logs_buffer.clear()

    async def flush_diagnostics_buffer(self):
        """Flush diagnostics buffer to diagnostics channel"""
        if self.diagnostics_buffer:
            await self._send_batch_to_channel(
                self.diagnostics_channel,
                self.diagnostics_buffer.copy(),
                "🔬 Diagnostics Batch Report",
            )
            self.diagnostics_buffer.clear()

    async def flush_performance_buffer(self):
        """Flush performance buffer to performance channel"""
        if self.performance_buffer:
            await self._send_batch_to_channel(
                self.performance_channel,
                self.performance_buffer.copy(),
                "⚡ Performance Monitoring Batch Report",
            )
            self.performance_buffer.clear()

    async def flush_all_buffers(self):
        """Manually flush all buffers to their respective channels"""
        await asyncio.gather(
            self.flush_analytics_buffer(),
            self.flush_logs_buffer(),
            self.flush_diagnostics_buffer(),
            self.flush_performance_buffer(),
            return_exceptions=True,
        )

    def start_background_tasks(self):
        """Start background tasks for continuous automated reporting"""
        if not self.batch_send_task or self.batch_send_task.done():
            self.batch_send_task = asyncio.create_task(self._batch_send_loop())

        if not self.daily_report_task or self.daily_report_task.done():
            self.daily_report_task = asyncio.create_task(self._daily_report_loop())

        # Start continuous monitoring for automatic data capture
        if (
            not self.continuous_monitoring_task
            or self.continuous_monitoring_task.done()
        ):
            self.continuous_monitoring_task = asyncio.create_task(
                self._continuous_auto_capture()
            )

    def stop_background_tasks(self):
        """Stop all background tasks"""
        if self.batch_send_task and not self.batch_send_task.done():
            self.batch_send_task.cancel()

        if self.daily_report_task and not self.daily_report_task.done():
            self.daily_report_task.cancel()

        if (
            self.continuous_monitoring_task
            and not self.continuous_monitoring_task.done()
        ):
            self.continuous_monitoring_task.cancel()

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

    async def _continuous_auto_capture(self):
        """Continuous automatic data capture and streaming to Discord channels"""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute for comprehensive capture

                if not self.auto_capture_enabled:
                    continue

                # Auto-capture bot status and health
                await self._auto_capture_bot_status()

                # Auto-capture system metrics
                await self._auto_capture_system_metrics()

                # Auto-capture any pending logs or diagnostics
                await self._auto_flush_immediate_data()

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Continuous auto-capture error: {e}")

    async def _auto_capture_bot_status(self):
        """Automatically capture and send bot status data"""
        try:
            bot_status = {
                "event": "auto_bot_status_capture",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "bot_metrics": {
                    "guilds": (
                        len(self.bot.guilds) if hasattr(self.bot, "guilds") else 0
                    ),
                    "users": len(self.bot.users) if hasattr(self.bot, "users") else 0,
                    "latency_ms": (
                        round(self.bot.latency * 1000, 2)
                        if hasattr(self.bot, "latency")
                        else 0
                    ),
                    "is_ready": hasattr(self.bot, "is_ready") and self.bot.is_ready(),
                    "cogs_loaded": (
                        len(self.bot.cogs) if hasattr(self.bot, "cogs") else 0
                    ),
                    "uptime_seconds": (
                        (
                            datetime.now(timezone.utc) - self.bot.start_time
                        ).total_seconds()
                        if hasattr(self.bot, "start_time")
                        else 0
                    ),
                },
                "automatic_capture": True,
            }

            # Send directly to analytics for bot metrics
            await self.send_analytics(bot_status, immediate=False)

        except Exception as e:
            self.logger.error(f"Error in auto bot status capture: {e}")

    async def _auto_capture_system_metrics(self):
        """Automatically capture basic system metrics"""
        try:
            import psutil

            system_metrics = {
                "event": "auto_system_metrics_capture",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "system_health": {
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_percent": psutil.disk_usage("/").percent,
                    "boot_time": psutil.boot_time(),
                    "process_count": len(psutil.pids()),
                },
                "automatic_capture": True,
            }

            # Send to diagnostics channel for system health
            await self.send_diagnostics(system_metrics, immediate=False)

        except Exception as e:
            self.logger.error(f"Error in auto system metrics capture: {e}")

    async def _auto_flush_immediate_data(self):
        """Automatically flush any accumulated data to prevent local storage"""
        try:
            if self.zero_local_storage:
                # Force flush all buffers to ensure no local data accumulation
                await self.flush_all_buffers()

        except Exception as e:
            self.logger.error(f"Error in auto flush immediate data: {e}")

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

    async def send_performance(self, data: Dict[str, Any], immediate: bool = False):
        """Send performance data to performance channel (wrapper for send_continuous_performance)"""
        self.logger.debug(
            f"📊 Sending performance data - immediate: {immediate}, channel available: {self.performance_channel is not None}"
        )
        await self.send_continuous_performance(data, immediate)

    async def send_continuous_performance(
        self, detailed_metrics: Dict[str, Any], immediate: bool = False
    ):
        """Send detailed continuous performance monitoring data to dedicated performance channel"""
        performance_data = {
            "event": "continuous_performance_monitoring",
            "detailed_metrics": detailed_metrics,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if immediate:
            self.logger.debug(
                f"⚡ Sending immediate performance data to channel {self.performance_channel.id if self.performance_channel else 'None'}"
            )
            await self._send_to_channel(
                self.performance_channel,
                performance_data,
                "⚡ **CONTINUOUS PERFORMANCE MONITORING**",
            )
        else:
            self.logger.debug(
                f"📊 Adding performance data to buffer (current size: {len(self.performance_buffer)})"
            )
            self.performance_buffer.append(performance_data)

    async def _send_to_channel(
        self, channel: Optional[discord.TextChannel], data: Dict[str, Any], title: str
    ):
        """Send individual data entry to a Discord channel"""
        if not channel:
            self.logger.warning(f"⚠️ Cannot send data - channel is None for: {title}")
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

    # =============================================
    # AUTOMATIC EVENT CAPTURE SYSTEM
    # =============================================

    async def auto_capture_message_event(self, message: discord.Message):
        """Automatically capture message events and send to analytics"""
        if not self.auto_capture_enabled or message.author.bot:
            return

        try:
            message_data = {
                "event": "auto_message_capture",
                "guild_id": message.guild.id if message.guild else None,
                "guild_name": message.guild.name if message.guild else "DM",
                "channel_id": message.channel.id,
                "channel_name": getattr(message.channel, "name", "DM"),
                "user_id": message.author.id,
                "username": str(message.author),
                "message_length": len(message.content),
                "has_attachments": len(message.attachments) > 0,
                "has_embeds": len(message.embeds) > 0,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "automatic_capture": True,
            }

            await self.send_analytics(message_data, immediate=False)

        except Exception as e:
            self.logger.error(f"Error in auto message capture: {e}")

    async def auto_capture_command_event(
        self, ctx, command_name: str, success: bool = True, error: str = None
    ):
        """Automatically capture command events and send to analytics"""
        if not self.auto_capture_enabled:
            return

        try:
            command_data = {
                "event": "auto_command_capture",
                "command_name": command_name,
                "guild_id": ctx.guild.id if ctx.guild else None,
                "guild_name": ctx.guild.name if ctx.guild else "DM",
                "channel_id": ctx.channel.id,
                "user_id": ctx.author.id,
                "username": str(ctx.author),
                "success": success,
                "error": error,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "automatic_capture": True,
            }

            # Send to analytics for tracking, diagnostics if error
            if success:
                await self.send_analytics(command_data, immediate=success is False)
            else:
                await self.send_diagnostics(command_data, immediate=True)

        except Exception as e:
            self.logger.error(f"Error in auto command capture: {e}")

    async def auto_capture_error_event(
        self, error: Exception, context: str = "", immediate: bool = True
    ):
        """Automatically capture error events and send to logs"""
        if not self.auto_capture_enabled:
            return

        try:
            error_data = {
                "event": "auto_error_capture",
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context,
                "traceback": traceback.format_exc(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "automatic_capture": True,
            }

            await self.send_logs(error_data, immediate=immediate)

        except Exception as e:
            self.logger.error(f"Error in auto error capture: {e}")

    async def auto_capture_guild_event(self, guild: discord.Guild, event_type: str):
        """Automatically capture guild events (join/leave) and send to analytics"""
        if not self.auto_capture_enabled:
            return

        try:
            guild_data = {
                "event": "auto_guild_capture",
                "event_type": event_type,  # "join" or "leave"
                "guild_id": guild.id,
                "guild_name": guild.name,
                "member_count": guild.member_count,
                "owner_id": guild.owner_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "automatic_capture": True,
            }

            await self.send_analytics(guild_data, immediate=True)

        except Exception as e:
            self.logger.error(f"Error in auto guild capture: {e}")

    async def auto_capture_voice_event(self, member: discord.Member, before, after):
        """Automatically capture voice state changes and send to analytics"""
        if not self.auto_capture_enabled or member.bot:
            return

        try:
            voice_data = {
                "event": "auto_voice_capture",
                "guild_id": member.guild.id,
                "guild_name": member.guild.name,
                "user_id": member.id,
                "username": str(member),
                "before_channel": (
                    getattr(before.channel, "name", "DM") if before.channel else None
                ),
                "after_channel": (
                    getattr(after.channel, "name", "DM") if after.channel else None
                ),
                "event_type": self._determine_voice_event_type(before, after),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "automatic_capture": True,
            }

            await self.send_analytics(voice_data, immediate=False)

        except Exception as e:
            self.logger.error(f"Error in auto voice capture: {e}")

    def _determine_voice_event_type(self, before, after) -> str:
        """Determine the type of voice event"""
        if not before.channel and after.channel:
            return "voice_join"
        elif before.channel and not after.channel:
            return "voice_leave"
        elif before.channel and after.channel and before.channel != after.channel:
            return "voice_move"
        else:
            return "voice_update"

    async def auto_capture_member_event(self, member: discord.Member, event_type: str):
        """Automatically capture member events (join/leave) and send to analytics"""
        if not self.auto_capture_enabled:
            return

        try:
            member_data = {
                "event": "auto_member_capture",
                "event_type": event_type,  # "join" or "leave"
                "guild_id": member.guild.id,
                "guild_name": member.guild.name,
                "user_id": member.id,
                "username": str(member),
                "account_created": member.created_at.isoformat(),
                "is_bot": member.bot,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "automatic_capture": True,
            }

            await self.send_analytics(member_data, immediate=False)

        except Exception as e:
            self.logger.error(f"Error in auto member capture: {e}")

    async def auto_capture_reaction_event(self, payload):
        """Automatically capture reaction events and send to analytics"""
        if not self.auto_capture_enabled:
            return

        try:
            reaction_data = {
                "event": "auto_reaction_capture",
                "guild_id": payload.guild_id,
                "channel_id": payload.channel_id,
                "message_id": payload.message_id,
                "user_id": payload.user_id,
                "emoji": str(payload.emoji),
                "event_type": payload.event_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "automatic_capture": True,
            }

            await self.send_analytics(reaction_data, immediate=False)

        except Exception as e:
            self.logger.error(f"Error in auto reaction capture: {e}")

    # =============================================
    # ZERO LOCAL STORAGE ENFORCEMENT
    # =============================================

    async def enforce_zero_local_storage(self):
        """Enforce zero local storage policy by immediately flushing all data"""
        try:
            if self.zero_local_storage:
                # Immediately flush all buffers
                await self.flush_all_buffers()

                # Clear any potential local data accumulation
                self.analytics_buffer.clear()
                self.logs_buffer.clear()
                self.diagnostics_buffer.clear()
                self.performance_buffer.clear()

                # Send confirmation that no local data is stored
                await self.send_diagnostics(
                    {
                        "event": "zero_local_storage_enforcement",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "message": "All data immediately sent to Discord - zero local storage confirmed",
                        "buffers_cleared": True,
                    },
                    immediate=True,
                )

        except Exception as e:
            self.logger.error(f"Error enforcing zero local storage: {e}")

    async def test_performance_channel(self):
        """Test the performance channel with a simple message"""
        try:
            test_data = {
                "event": "performance_channel_test",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": "Testing performance channel connectivity",
                "channel_id": self.config.performance_channel_id,
                "channel_available": self.performance_channel is not None,
                "test_type": "connectivity_check",
            }

            self.logger.info(
                f"🧪 Testing performance channel - Channel available: {self.performance_channel is not None}"
            )
            await self.send_performance(test_data, immediate=True)
            self.logger.info("✅ Performance channel test completed")

        except Exception as e:
            self.logger.error(f"❌ Performance channel test failed: {e}")

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
