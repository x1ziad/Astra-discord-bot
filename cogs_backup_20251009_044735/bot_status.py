"""
Bot Status Management Cog
Provides enhanced bot status, performance monitoring, and utility commands
"""

import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List, Any
import os
import gc
import psutil
import sys

from config.unified_config import unified_config
from utils.command_optimizer import optimize_command
from utils.command_optimizer import ResponseCache


class BotStatus(commands.Cog):
    """Enhanced bot status and monitoring commands"""

    def __init__(self, bot):
        self.bot = bot
        self.config = unified_config
        self.start_time = time.time()
        self.command_stats = {}

        # Performance optimization
        self.cache = ResponseCache(
            max_size=200, default_ttl=60
        )  # 1-minute cache for status data

        self.performance_data = {
            "uptime": 0,
            "memory_usage": [],
            "cpu_usage": [],
            "command_count": 0,
            "error_count": 0,
            "last_updated": time.time(),
        }

        # Start background tasks
        self.update_status.start()
        self.collect_performance_data.start()

    def cog_unload(self):
        """Cleanup when cog is unloaded"""
        self.update_status.cancel()
        self.collect_performance_data.cancel()

    @tasks.loop(minutes=5)
    async def update_status(self):
        """Update bot status with current stats"""
        try:
            guild_count = len(self.bot.guilds)
            user_count = sum(guild.member_count for guild in self.bot.guilds)

            # Cycle through different status messages
            statuses = [
                f"🌌 Monitoring {guild_count} galaxies",
                f"👥 Serving {user_count:,} space explorers",
                f"🧠 AI systems: Online",
                f"⚡ Uptime: {self._format_uptime()}",
                f"🚀 Ready for exploration!",
            ]

            status_index = int(time.time() // 300) % len(
                statuses
            )  # Change every 5 minutes
            activity = discord.Activity(
                type=discord.ActivityType.watching, name=statuses[status_index]
            )

            await self.bot.change_presence(
                status=discord.Status.online, activity=activity
            )

        except Exception as e:
            print(f"Error updating status: {e}")

    @update_status.before_loop
    async def before_update_status(self):
        """Wait for bot to be ready before starting status updates"""
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=1)
    async def collect_performance_data(self):
        """Collect performance metrics"""
        try:
            process = psutil.Process()

            # Memory usage in MB
            memory_mb = process.memory_info().rss / 1024 / 1024
            self.performance_data["memory_usage"].append(memory_mb)

            # CPU usage percentage
            cpu_percent = process.cpu_percent()
            self.performance_data["cpu_usage"].append(cpu_percent)

            # Keep only last 60 data points (1 hour)
            if len(self.performance_data["memory_usage"]) > 60:
                self.performance_data["memory_usage"].pop(0)
            if len(self.performance_data["cpu_usage"]) > 60:
                self.performance_data["cpu_usage"].pop(0)

            self.performance_data["uptime"] = time.time() - self.start_time
            self.performance_data["last_updated"] = time.time()

        except Exception as e:
            print(f"Error collecting performance data: {e}")

    @collect_performance_data.before_loop
    async def before_collect_performance_data(self):
        """Wait for bot to be ready before collecting data"""
        await self.bot.wait_until_ready()

    def _format_uptime(self) -> str:
        """Format uptime as human readable string"""
        uptime_seconds = int(time.time() - self.start_time)
        return str(timedelta(seconds=uptime_seconds))

    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics"""
        memory_data = self.performance_data["memory_usage"]
        cpu_data = self.performance_data["cpu_usage"]

        return {
            "uptime": self._format_uptime(),
            "memory": {
                "current": memory_data[-1] if memory_data else 0,
                "average": sum(memory_data) / len(memory_data) if memory_data else 0,
                "peak": max(memory_data) if memory_data else 0,
            },
            "cpu": {
                "current": cpu_data[-1] if cpu_data else 0,
                "average": sum(cpu_data) / len(cpu_data) if cpu_data else 0,
                "peak": max(cpu_data) if cpu_data else 0,
            },
            "commands_executed": self.performance_data.get("command_count", 0),
            "errors_encountered": self.performance_data.get("error_count", 0),
        }

    @app_commands.command(
        name="performance", description="📈 Show detailed performance metrics"
    )
    async def performance_command(self, interaction: discord.Interaction):
        """Show detailed performance metrics and charts"""
        await interaction.response.defer()

        try:
            perf = self._get_performance_summary()

            embed = discord.Embed(
                title="📈 Performance Metrics",
                description="Detailed system performance over the last hour",
                color=0x1E90FF,
                timestamp=datetime.now(timezone.utc),
            )

            # Memory statistics
            embed.add_field(
                name="💾 Memory Usage",
                value=f"**Current:** {perf['memory']['current']:.1f}MB\n"
                f"**Average:** {perf['memory']['average']:.1f}MB\n"
                f"**Peak:** {perf['memory']['peak']:.1f}MB",
                inline=True,
            )

            # CPU statistics
            embed.add_field(
                name="🖥️ CPU Usage",
                value=f"**Current:** {perf['cpu']['current']:.1f}%\n"
                f"**Average:** {perf['cpu']['average']:.1f}%\n"
                f"**Peak:** {perf['cpu']['peak']:.1f}%",
                inline=True,
            )

            # Activity statistics
            embed.add_field(
                name="📊 Activity Stats",
                value=f"**Commands:** {perf['commands_executed']:,}\n"
                f"**Errors:** {perf['errors_encountered']:,}\n"
                f"**Uptime:** {perf['uptime']}",
                inline=True,
            )

            # System resources
            system_memory = psutil.virtual_memory()
            embed.add_field(
                name="🖥️ System Resources",
                value=f"**System Memory:** {system_memory.percent:.1f}%\n"
                f"**Available:** {system_memory.available / 1024**3:.1f}GB\n"
                f"**Total:** {system_memory.total / 1024**3:.1f}GB",
                inline=True,
            )

            # Garbage collection stats
            gc_stats = gc.get_stats()
            total_objects = sum(stat["objects"] for stat in gc_stats)

            embed.add_field(
                name="🗑️ Memory Management",
                value=f"**Objects:** {total_objects:,}\n"
                f"**Collections:** {gc.get_count()}\n"
                f"**GC Enabled:** {'✅' if gc.isenabled() else '❌'}",
                inline=True,
            )

            # Performance trends
            memory_trend = (
                "📈"
                if len(self.performance_data["memory_usage"]) > 1
                and self.performance_data["memory_usage"][-1]
                > self.performance_data["memory_usage"][-2]
                else "📉"
            )
            cpu_trend = (
                "📈"
                if len(self.performance_data["cpu_usage"]) > 1
                and self.performance_data["cpu_usage"][-1]
                > self.performance_data["cpu_usage"][-2]
                else "📉"
            )

            embed.add_field(
                name="📊 Trends",
                value=f"**Memory:** {memory_trend}\n"
                f"**CPU:** {cpu_trend}\n"
                f"**Data Points:** {len(self.performance_data['memory_usage'])}",
                inline=True,
            )

            embed.set_footer(text="Performance data collected over the last hour")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Performance Check Failed",
                description=f"Unable to retrieve performance metrics:\n```\n{str(e)}\n```",
                color=0xFF0000,
                timestamp=datetime.now(timezone.utc),
            )
            await interaction.followup.send(embed=error_embed)

    @app_commands.command(
        name="health", description="🏥 Comprehensive system health check"
    )
    async def health_command(self, interaction: discord.Interaction):
        """Perform comprehensive system health check"""
        await interaction.response.defer()

        embed = discord.Embed(
            title="🏥 System Health Check",
            description="Performing comprehensive diagnostics...",
            color=0xFFA500,
            timestamp=datetime.now(timezone.utc),
        )

        health_checks = []

        # Bot connection health
        try:
            if not self.bot.is_closed() and self.bot.latency < 1.0:
                health_checks.append("✅ Discord Connection: Healthy")
            else:
                health_checks.append("⚠️ Discord Connection: Issues detected")
        except:
            health_checks.append("❌ Discord Connection: Failed")

        # Database health
        try:
            if os.path.exists("data/astra.db"):
                health_checks.append("✅ Database: Available")
            else:
                health_checks.append("⚠️ Database: Not found")
        except:
            health_checks.append("❌ Database: Error accessing")

        # AI system health
        try:
            ai_cog = self.bot.get_cog("AdvancedAICog")
            if ai_cog and hasattr(ai_cog, "ai_client"):
                health_checks.append("✅ AI System: Online")
            else:
                health_checks.append("❌ AI System: Offline")
        except:
            health_checks.append("❌ AI System: Error")

        # Memory health
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024

            if memory_mb < 500:
                health_checks.append(f"✅ Memory Usage: {memory_mb:.1f}MB (Healthy)")
            elif memory_mb < 1000:
                health_checks.append(f"⚠️ Memory Usage: {memory_mb:.1f}MB (Elevated)")
            else:
                health_checks.append(f"❌ Memory Usage: {memory_mb:.1f}MB (High)")
        except:
            health_checks.append("❌ Memory Check: Failed")

        # Cog health
        try:
            loaded_cogs = len(self.bot.cogs)
            expected_cogs = 8  # Approximate expected number

            if loaded_cogs >= expected_cogs:
                health_checks.append(
                    f"✅ Extensions: {loaded_cogs}/{expected_cogs} loaded"
                )
            else:
                health_checks.append(
                    f"⚠️ Extensions: {loaded_cogs}/{expected_cogs} loaded"
                )
        except:
            health_checks.append("❌ Extension Check: Failed")

        # Command sync health
        try:
            command_count = len([cmd for cmd in self.bot.tree.walk_commands()])
            if command_count > 0:
                health_checks.append(f"✅ Commands: {command_count} registered")
            else:
                health_checks.append("❌ Commands: None registered")
        except:
            health_checks.append("❌ Command Check: Failed")

        # Update embed with results
        healthy_count = sum(1 for check in health_checks if check.startswith("✅"))
        warning_count = sum(1 for check in health_checks if check.startswith("⚠️"))
        error_count = sum(1 for check in health_checks if check.startswith("❌"))

        if error_count == 0 and warning_count == 0:
            embed.color = 0x00FF00
            embed.title = "✅ System Health: Excellent"
        elif error_count == 0:
            embed.color = 0xFFFF00
            embed.title = "⚠️ System Health: Good"
        else:
            embed.color = 0xFF6B6B
            embed.title = "❌ System Health: Issues Detected"

        embed.description = f"**Health Summary:** {healthy_count} ✅ | {warning_count} ⚠️ | {error_count} ❌"

        # Add health checks to embed
        embed.add_field(
            name="🔍 Diagnostic Results", value="\n".join(health_checks), inline=False
        )

        # Add system recommendations
        recommendations = []
        if error_count > 0:
            recommendations.append("• Check logs for error details")
            recommendations.append("• Consider restarting affected components")
        if warning_count > 0:
            recommendations.append("• Monitor system resources")
        if healthy_count == len(health_checks):
            recommendations.append("• All systems operating normally")

        if recommendations:
            embed.add_field(
                name="💡 Recommendations",
                value="\n".join(recommendations),
                inline=False,
            )

        await interaction.followup.send(embed=embed)

    @commands.Cog.listener()
    async def on_app_command_completion(
        self, interaction: discord.Interaction, command
    ):
        """Track command usage for statistics"""
        self.performance_data["command_count"] = (
            self.performance_data.get("command_count", 0) + 1
        )

        # Track individual command stats
        cmd_name = (
            command.qualified_name
            if hasattr(command, "qualified_name")
            else str(command)
        )
        self.command_stats[cmd_name] = self.command_stats.get(cmd_name, 0) + 1

    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error):
        """Track command errors for statistics"""
        self.performance_data["error_count"] = (
            self.performance_data.get("error_count", 0) + 1
        )


async def setup(bot):
    """Setup function for the bot status cog"""
    await bot.add_cog(BotStatus(bot))
