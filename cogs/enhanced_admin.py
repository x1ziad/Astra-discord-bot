"""
Enhanced Admin Cog for Astra Bot
Provides advanced bot management, AI system controls, and owner-only commands
"""

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import traceback
import psutil
import sys
import time
from datetime import datetime, timedelta, timezone
import json
import os
from typing import Optional, List, Literal, Dict, Any

from config.enhanced_config import EnhancedConfigManager
from config.config_manager import config_manager

try:
    from ai.consolidated_ai_engine import ConsolidatedAIEngine

    AI_ENGINE_AVAILABLE = True
except ImportError:
    AI_ENGINE_AVAILABLE = False


class EnhancedAdmin(commands.GroupCog, name="admin"):
    """Enhanced administrative commands for bot management"""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.config = EnhancedConfigManager()
        self.legacy_config = config_manager
        self.logger = bot.logger if hasattr(bot, "logger") else None
        self.owner_id = self.config.get_owner_id()

        # Cache for better performance
        self._system_info_cache = {}
        self._cache_time = 0
        self._cache_duration = 60  # 1 minute

    async def is_owner(self, user_id: int) -> bool:
        """Check if user is the bot owner"""
        # Check configured owner ID first
        if self.owner_id and user_id == self.owner_id:
            return True

        # Fallback to Discord application info
        try:
            app_info = await self.bot.application_info()
            return user_id == app_info.owner.id
        except Exception:
            return False

    async def is_admin_or_owner(self, interaction: discord.Interaction) -> bool:
        """Check if user is admin or owner"""
        if await self.is_owner(interaction.user.id):
            return True

        if interaction.guild and interaction.user.guild_permissions.administrator:
            return True

        return False

    @app_commands.command(
        name="shutdown", description="🔴 Shutdown the bot (Owner only)"
    )
    @app_commands.describe(
        confirm="Type 'CONFIRM' to shutdown the bot",
        restart="Whether to restart instead of shutdown",
    )
    async def shutdown_command(
        self, interaction: discord.Interaction, confirm: str, restart: bool = False
    ):
        """Shutdown the bot (Owner only)"""
        if not await self.is_owner(interaction.user.id):
            await interaction.response.send_message(
                "❌ **ACCESS DENIED**\n"
                "This command can only be used by the bot owner.\n"
                f"👤 Your ID: `{interaction.user.id}`\n"
                f"🔐 Owner ID: `{self.owner_id or 'Not configured'}`",
                ephemeral=True,
            )
            return

        if confirm.upper() != "CONFIRM":
            await interaction.response.send_message(
                "⚠️ **Confirmation Required**\n"
                f"To {'restart' if restart else 'shutdown'} the bot, please run:\n"
                f"`/admin shutdown confirm:CONFIRM restart:{restart}`",
                ephemeral=True,
            )
            return

        action = "restarting" if restart else "shutting down"
        embed = discord.Embed(
            title=f"🔴 Bot {action.title()}",
            description=f"Bot is {action}...",
            color=0xFF6B6B if not restart else 0xFFA500,
            timestamp=datetime.now(timezone.utc),
        )
        embed.add_field(
            name="👤 Initiated by",
            value=f"{interaction.user.mention} (`{interaction.user.id}`)",
            inline=False,
        )
        embed.add_field(
            name="⏰ Timestamp", value=f"<t:{int(time.time())}:F>", inline=False
        )

        await interaction.response.send_message(embed=embed)

        # Log the action
        if self.logger:
            self.logger.critical(
                f"Bot {action} initiated by {interaction.user} ({interaction.user.id})"
            )

        # Give time for the message to send
        await asyncio.sleep(2)

        if restart:
            # Restart the process
            python = sys.executable
            os.execl(python, python, *sys.argv)
        else:
            # Graceful shutdown
            await self.bot.close()
            sys.exit(0)

    @app_commands.command(name="reload", description="🔄 Reload a cog or all cogs")
    @app_commands.describe(cog="The cog to reload, or 'all' to reload all cogs")
    async def reload_command(self, interaction: discord.Interaction, cog: str):
        """Reload a specific cog or all cogs (Admin only)"""
        if not await self.is_admin_or_owner(interaction):
            await interaction.response.send_message(
                "❌ This command requires administrator permissions or bot ownership.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        try:
            if cog.lower() == "all":
                # Reload all cogs
                success_cogs = []
                failed_cogs = []

                # Get all loaded cogs
                cogs_to_reload = list(self.bot.cogs.keys())

                for cog_name in cogs_to_reload:
                    try:
                        await self.bot.reload_extension(f"cogs.{cog_name.lower()}")
                        success_cogs.append(cog_name)
                    except Exception as e:
                        failed_cogs.append(f"{cog_name}: {str(e)}")

                embed = discord.Embed(
                    title="🔄 Mass Cog Reload Results",
                    color=0x00FF00 if not failed_cogs else 0xFFFF00,
                    timestamp=datetime.now(timezone.utc),
                )

                if success_cogs:
                    embed.add_field(
                        name="✅ Successfully Reloaded",
                        value="\n".join(f"• {cog}" for cog in success_cogs),
                        inline=False,
                    )

                if failed_cogs:
                    embed.add_field(
                        name="❌ Failed to Reload",
                        value="\n".join(f"• {cog}" for cog in failed_cogs[:10]),
                        inline=False,
                    )

                await interaction.followup.send(embed=embed)
            else:
                # Reload specific cog
                cog_path = f"cogs.{cog.lower()}"
                await self.bot.reload_extension(cog_path)

                embed = discord.Embed(
                    title="✅ Cog Reloaded Successfully",
                    description=f"**{cog}** has been reloaded.",
                    color=0x00FF00,
                    timestamp=datetime.now(timezone.utc),
                )
                await interaction.followup.send(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="❌ Reload Failed",
                description=f"Failed to reload **{cog}**:\n```\n{str(e)}\n```",
                color=0xFF0000,
                timestamp=datetime.now(timezone.utc),
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="system", description="📊 Show system information")
    async def system_command(self, interaction: discord.Interaction):
        """Show detailed system information"""
        if not await self.is_admin_or_owner(interaction):
            await interaction.response.send_message(
                "❌ This command requires administrator permissions or bot ownership.",
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        # Use cached system info if recent
        current_time = time.time()
        if (
            current_time - self._cache_time
        ) < self._cache_duration and self._system_info_cache:
            system_info = self._system_info_cache
        else:
            # Gather fresh system information
            process = psutil.Process()
            system_info = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": psutil.virtual_memory(),
                "disk": psutil.disk_usage("/"),
                "process_memory": process.memory_info(),
                "process_cpu": process.cpu_percent(),
                "uptime": time.time() - process.create_time(),
                "python_version": sys.version,
                "discord_py_version": discord.__version__,
            }
            self._system_info_cache = system_info
            self._cache_time = current_time

        # Create system info embed
        embed = discord.Embed(
            title="📊 System Information",
            color=0x00BFFF,
            timestamp=datetime.now(timezone.utc),
        )

        # System Resources
        embed.add_field(
            name="💻 System Resources",
            value=f"**CPU Usage:** {system_info['cpu_percent']:.1f}%\n"
            f"**Memory:** {system_info['memory'].percent:.1f}% "
            f"({system_info['memory'].used / 1024**3:.1f}GB / "
            f"{system_info['memory'].total / 1024**3:.1f}GB)\n"
            f"**Disk:** {system_info['disk'].percent:.1f}% "
            f"({system_info['disk'].used / 1024**3:.1f}GB / "
            f"{system_info['disk'].total / 1024**3:.1f}GB)",
            inline=False,
        )

        # Bot Process
        embed.add_field(
            name="🤖 Bot Process",
            value=f"**Memory Usage:** {system_info['process_memory'].rss / 1024**2:.1f}MB\n"
            f"**CPU Usage:** {system_info['process_cpu']:.1f}%\n"
            f"**Uptime:** {timedelta(seconds=int(system_info['uptime']))}",
            inline=False,
        )

        # Bot Statistics
        guild_count = len(self.bot.guilds)
        user_count = sum(guild.member_count for guild in self.bot.guilds)

        embed.add_field(
            name="📈 Bot Statistics",
            value=f"**Guilds:** {guild_count:,}\n"
            f"**Users:** {user_count:,}\n"
            f"**Latency:** {self.bot.latency * 1000:.1f}ms",
            inline=False,
        )

        # Version Information
        python_version = system_info["python_version"].split()[0]
        embed.add_field(
            name="🔧 Version Information",
            value=f"**Python:** {python_version}\n"
            f"**Discord.py:** {system_info['discord_py_version']}\n"
            f"**AI Engine:** {'Available' if AI_ENGINE_AVAILABLE else 'Not Available'}",
            inline=False,
        )

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="ai_control", description="🧠 Control AI system")
    @app_commands.describe(
        action="Action to perform on AI system",
        provider="AI provider to switch to (for switch action)",
    )
    async def ai_control_command(
        self,
        interaction: discord.Interaction,
        action: Literal[
            "status", "restart", "clear_cache", "switch_provider", "health_check"
        ],
        provider: Optional[
            Literal["universal", "openrouter", "github", "openai"]
        ] = None,
    ):
        """Control AI system operations (Admin only)"""
        if not await self.is_admin_or_owner(interaction):
            await interaction.response.send_message(
                "❌ This command requires administrator permissions or bot ownership.",
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        if not AI_ENGINE_AVAILABLE:
            await interaction.followup.send(
                "❌ **AI Engine Not Available**\n"
                "The consolidated AI engine is not loaded or available.",
                ephemeral=True,
            )
            return

        try:
            # Get AI client from advanced_ai cog
            ai_cog = self.bot.get_cog("AdvancedAICog")
            if not ai_cog or not ai_cog.ai_client:
                await interaction.followup.send(
                    "❌ **AI Client Not Found**\n"
                    "The AI client is not initialized in the AdvancedAI cog.",
                    ephemeral=True,
                )
                return

            ai_client = ai_cog.ai_client

            if action == "status":
                # Get AI system status
                if hasattr(ai_client, "get_health_status"):
                    status = await ai_client.get_health_status()

                    embed = discord.Embed(
                        title="🧠 AI System Status",
                        color=(
                            0x00FF00 if status.get("status") == "healthy" else 0xFF6B6B
                        ),
                        timestamp=datetime.now(timezone.utc),
                    )

                    embed.add_field(
                        name="🟢 Health Status",
                        value=f"**Status:** {status.get('status', 'Unknown').title()}\n"
                        f"**Active Provider:** {status.get('active_provider', 'None')}\n"
                        f"**Available Providers:** {', '.join(status.get('available_providers', []))}",
                        inline=False,
                    )

                    if "performance_metrics" in status:
                        metrics = status["performance_metrics"]["ai_performance"]
                        embed.add_field(
                            name="📊 Performance Metrics",
                            value=f"**Total Requests:** {metrics.get('total_requests', 0):,}\n"
                            f"**Success Rate:** {metrics.get('success_rate', 0):.1f}%\n"
                            f"**Avg Response Time:** {metrics.get('avg_response_time_ms', 0):.1f}ms",
                            inline=False,
                        )

                    if "cache_stats" in status:
                        cache = status["cache_stats"]
                        embed.add_field(
                            name="💾 Cache Performance",
                            value=f"**Hit Rate:** {cache.get('hit_rate', 0):.1f}%\n"
                            f"**Total Hits:** {cache.get('total_hits', 0):,}\n"
                            f"**Memory Cache Size:** {cache.get('memory_cache_size', 0):,}",
                            inline=False,
                        )

                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send(
                        "❌ AI client doesn't support health status checks."
                    )

            elif action == "health_check":
                # Perform comprehensive health check
                embed = discord.Embed(
                    title="🏥 AI System Health Check",
                    description="Performing comprehensive system diagnostics...",
                    color=0xFFA500,
                    timestamp=datetime.now(timezone.utc),
                )

                # Test basic AI response
                try:
                    test_response = await ai_client.process_conversation(
                        "Health check test", 999999999  # Test user ID
                    )
                    ai_test = "✅ AI Response Generation Working"
                except Exception as e:
                    ai_test = f"❌ AI Response Generation Failed: {str(e)[:100]}"

                # Test cache system
                try:
                    if hasattr(ai_client, "cache"):
                        cache_stats = ai_client.cache.get_stats()
                        cache_test = f"✅ Cache System Working (Hit Rate: {cache_stats.get('hit_rate', 0):.1f}%)"
                    else:
                        cache_test = "⚠️ Cache System Not Available"
                except Exception as e:
                    cache_test = f"❌ Cache System Error: {str(e)[:100]}"

                # Test database
                try:
                    if hasattr(ai_client, "db_path") and os.path.exists(
                        ai_client.db_path
                    ):
                        db_test = "✅ Database Connection OK"
                    else:
                        db_test = "⚠️ Database Not Found"
                except Exception as e:
                    db_test = f"❌ Database Error: {str(e)[:100]}"

                embed.add_field(
                    name="🔍 Diagnostic Results",
                    value=f"{ai_test}\n{cache_test}\n{db_test}",
                    inline=False,
                )

                await interaction.followup.send(embed=embed)

            elif action == "clear_cache":
                # Clear AI system cache
                if hasattr(ai_client, "cache"):
                    old_stats = ai_client.cache.get_stats()
                    ai_client.cache.memory_cache.clear()
                    ai_client.cache.memory_timestamps.clear()

                    embed = discord.Embed(
                        title="🧹 Cache Cleared",
                        description="AI system cache has been cleared successfully.",
                        color=0x00FF00,
                        timestamp=datetime.now(timezone.utc),
                    )
                    embed.add_field(
                        name="📊 Previous Cache Stats",
                        value=f"**Hit Rate:** {old_stats.get('hit_rate', 0):.1f}%\n"
                        f"**Memory Items:** {old_stats.get('memory_cache_size', 0):,}",
                        inline=False,
                    )
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("❌ Cache system not available.")

            else:
                await interaction.followup.send(
                    f"❌ Action '{action}' not yet implemented."
                )

        except Exception as e:
            embed = discord.Embed(
                title="❌ AI Control Error",
                description=f"Failed to execute AI control action:\n```\n{str(e)}\n```",
                color=0xFF0000,
                timestamp=datetime.now(timezone.utc),
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="logs", description="📋 View recent bot logs")
    @app_commands.describe(lines="Number of log lines to show (default: 20, max: 100)")
    async def logs_command(self, interaction: discord.Interaction, lines: int = 20):
        """View recent bot logs (Owner only)"""
        if not await self.is_owner(interaction.user.id):
            await interaction.response.send_message(
                "❌ This command can only be used by the bot owner.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        try:
            lines = max(1, min(lines, 100))  # Clamp between 1 and 100

            # Try to find log file
            log_paths = ["logs/astra.log", "astra.log", "discord.log", "bot.log"]

            log_file = None
            for path in log_paths:
                if os.path.exists(path):
                    log_file = path
                    break

            if not log_file:
                await interaction.followup.send(
                    "❌ **Log File Not Found**\n"
                    f"Searched paths: {', '.join(log_paths)}"
                )
                return

            # Read last N lines
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:]

            log_content = "".join(recent_lines)

            # Truncate if too long for Discord
            if len(log_content) > 1900:
                log_content = log_content[-1900:] + "\n... (truncated)"

            embed = discord.Embed(
                title=f"📋 Recent Bot Logs ({lines} lines)",
                description=f"```\n{log_content}\n```",
                color=0x00BFFF,
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(
                name="📁 Log File",
                value=f"`{log_file}` ({len(all_lines):,} total lines)",
                inline=False,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(
                f"❌ **Error Reading Logs**\n```\n{str(e)}\n```"
            )

    @app_commands.command(name="config", description="⚙️ Manage bot configuration")
    @app_commands.describe(
        action="Configuration action to perform",
        key="Configuration key (for get/set actions)",
        value="New value (for set action)",
    )
    async def config_command(
        self,
        interaction: discord.Interaction,
        action: Literal["show", "get", "set", "reload"],
        key: Optional[str] = None,
        value: Optional[str] = None,
    ):
        """Manage bot configuration (Owner only)"""
        if not await self.is_owner(interaction.user.id):
            await interaction.response.send_message(
                "❌ This command can only be used by the bot owner.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        try:
            if action == "show":
                # Show all configuration (safely)
                config_data = self.config.get_all_settings()

                embed = discord.Embed(
                    title="⚙️ Bot Configuration",
                    color=0x00BFFF,
                    timestamp=datetime.now(timezone.utc),
                )

                # Split config into chunks for display
                config_items = []
                for k, v in config_data.items():
                    if len(str(v)) > 50:
                        v = str(v)[:47] + "..."
                    config_items.append(f"**{k}:** `{v}`")

                # Split into multiple fields if needed
                chunk_size = 10
                for i in range(0, len(config_items), chunk_size):
                    chunk = config_items[i : i + chunk_size]
                    field_name = (
                        f"Configuration ({i+1}-{min(i+chunk_size, len(config_items))})"
                    )
                    embed.add_field(
                        name=field_name, value="\n".join(chunk), inline=False
                    )

                await interaction.followup.send(embed=embed)

            elif action == "get":
                if not key:
                    await interaction.followup.send(
                        "❌ Key parameter required for 'get' action."
                    )
                    return

                value = self.config.get_setting(key)

                embed = discord.Embed(
                    title=f"⚙️ Configuration: {key}",
                    description=f"**Value:** `{value}`",
                    color=0x00FF00,
                    timestamp=datetime.now(timezone.utc),
                )
                await interaction.followup.send(embed=embed)

            elif action == "set":
                if not key or value is None:
                    await interaction.followup.send(
                        "❌ Both key and value parameters required for 'set' action."
                    )
                    return

                old_value = self.config.get_setting(key)
                self.config.update_setting(key, value)
                self.config.save_config()

                embed = discord.Embed(
                    title=f"✅ Configuration Updated: {key}",
                    color=0x00FF00,
                    timestamp=datetime.now(timezone.utc),
                )
                embed.add_field(name="Old Value", value=f"`{old_value}`", inline=True)
                embed.add_field(name="New Value", value=f"`{value}`", inline=True)

                await interaction.followup.send(embed=embed)

            elif action == "reload":
                # Reload configuration
                self.config._load_config()

                embed = discord.Embed(
                    title="🔄 Configuration Reloaded",
                    description="Configuration has been reloaded from file and environment variables.",
                    color=0x00FF00,
                    timestamp=datetime.now(timezone.utc),
                )
                await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(
                f"❌ **Configuration Error**\n```\n{str(e)}\n```"
            )


async def setup(bot):
    """Setup function for the enhanced admin cog"""
    await bot.add_cog(EnhancedAdmin(bot))
