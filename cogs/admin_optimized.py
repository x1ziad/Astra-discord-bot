"""
Optimized Admin Cog for Astra Bot
Consolidated administrative commands combining best features from admin.py and enhanced_admin.py
Includes performance optimizations, caching, and enhanced system monitoring
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

from config.unified_config import unified_config
from utils.performance_optimizer import ResponseCache
from utils.command_optimizer import auto_optimize_commands

try:
    from ai.consolidated_ai_engine import ConsolidatedAIEngine

    AI_ENGINE_AVAILABLE = True
except ImportError:
    AI_ENGINE_AVAILABLE = False


class OptimizedAdmin(commands.GroupCog, name="admin"):
    """Optimized administrative commands for bot management with enhanced performance"""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.config = unified_config
        self.legacy_config = unified_config
        self.logger = bot.logger if hasattr(bot, "logger") else None
        self.owner_id = self.config.get_owner_id()

        # Performance optimizations
        self.cache = ResponseCache(max_size=1000, default_ttl=300)  # 5-minute cache
        self._system_info_cache = {}
        self._cache_time = 0
        self._cache_duration = 60  # 1 minute

        # Rate limiting for heavy operations
        self._last_reload = 0
        self._reload_cooldown = 10  # 10 seconds between reloads

    async def is_owner(self, user_id: int) -> bool:
        """Check if user is the bot owner (cached)"""
        cache_key = f"owner_check_{user_id}"
        result = await self.cache.get(cache_key)

        if result is not None:
            return result

        # Check configured owner ID first
        if self.owner_id and user_id == self.owner_id:
            await self.cache.set(cache_key, True)
            return True

        # Fallback to Discord application info
        try:
            app_info = await self.bot.application_info()
            is_owner = user_id == app_info.owner.id
            await self.cache.set(cache_key, is_owner)
            return is_owner
        except Exception:
            await self.cache.set(cache_key, False)
            return False

    async def is_admin_or_owner(self, interaction: discord.Interaction) -> bool:
        """Check if user is admin or owner (optimized)"""
        if await self.is_owner(interaction.user.id):
            return True

        if interaction.guild and interaction.user.guild_permissions.administrator:
            return True

        return False

    @app_commands.command(
        name="shutdown", description="🔴 Shutdown or restart the bot (Owner only)"
    )
    @app_commands.describe(
        confirm="Type 'CONFIRM' to shutdown the bot",
        restart="Whether to restart instead of shutdown",
    )
    async def shutdown_command(
        self, interaction: discord.Interaction, confirm: str, restart: bool = False
    ):
        """Shutdown or restart the bot (Owner only)"""
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

    @app_commands.command(
        name="reload", description="🔄 Reload a cog or all cogs (with rate limiting)"
    )
    @app_commands.describe(cog="The cog to reload, or 'all' to reload all cogs")
    async def reload_command(self, interaction: discord.Interaction, cog: str):
        """Reload a specific cog or all cogs (Admin only) with optimizations"""
        if not await self.is_admin_or_owner(interaction):
            await interaction.response.send_message(
                "❌ This command requires administrator permissions or bot ownership.",
                ephemeral=True,
            )
            return

        # Rate limiting
        current_time = time.time()
        if current_time - self._last_reload < self._reload_cooldown:
            remaining = self._reload_cooldown - (current_time - self._last_reload)
            await interaction.response.send_message(
                f"⏰ Please wait {remaining:.1f} seconds before reloading again.",
                ephemeral=True,
            )
            return

        self._last_reload = current_time
        await interaction.response.defer(ephemeral=True)

        try:
            if cog.lower() == "all":
                # Reload all cogs with progress tracking
                success_cogs = []
                failed_cogs = []

                # Get all Python files in cogs directory
                cog_files = [
                    f.replace(".py", "")
                    for f in os.listdir("cogs")
                    if f.endswith(".py")
                    and not f.startswith("__")
                    and f != "admin_optimized.py"
                ]

                total_cogs = len(cog_files)

                for i, cog_name in enumerate(cog_files, 1):
                    ext_name = f"cogs.{cog_name}"
                    try:
                        await self.bot.reload_extension(ext_name)
                        success_cogs.append(cog_name)
                    except Exception as e:
                        failed_cogs.append(f"{cog_name}: {str(e)[:100]}")
                        if self.logger:
                            self.logger.error(
                                f"Failed to reload {ext_name}: {traceback.format_exc()}"
                            )

                    # Update progress every 5 cogs
                    if i % 5 == 0 or i == total_cogs:
                        try:
                            await interaction.edit_original_response(
                                content=f"🔄 Reloading cogs... {i}/{total_cogs} processed"
                            )
                        except:
                            pass

                # Create results embed
                embed = discord.Embed(
                    title="🔄 Mass Reload Results",
                    description=f"Processed **{total_cogs}** cog(s)",
                    color=0x00FF00 if not failed_cogs else 0xFFFF00,
                    timestamp=datetime.now(timezone.utc),
                )

                if success_cogs:
                    success_text = "\n".join(f"✅ {cog}" for cog in success_cogs)
                    if len(success_text) > 1000:
                        success_text = (
                            success_text[:1000]
                            + f"\n... and {len(success_cogs) - success_text.count('✅')} more"
                        )
                    embed.add_field(
                        name=f"Successfully Reloaded ({len(success_cogs)})",
                        value=success_text,
                        inline=False,
                    )

                if failed_cogs:
                    failed_text = "\n".join(f"❌ {cog}" for cog in failed_cogs[:10])
                    embed.add_field(
                        name=f"Failed ({len(failed_cogs)})",
                        value=failed_text,
                        inline=False,
                    )

                await interaction.followup.send(embed=embed)

            else:
                # Reload specific cog
                cog_name = cog if cog.startswith("cogs.") else f"cogs.{cog}"

                try:
                    await self.bot.reload_extension(cog_name)
                    embed = discord.Embed(
                        title="✅ Cog Reloaded",
                        description=f"Successfully reloaded `{cog_name}`",
                        color=0x00FF00,
                        timestamp=datetime.now(timezone.utc),
                    )
                    await interaction.followup.send(embed=embed)

                except Exception as e:
                    embed = discord.Embed(
                        title="❌ Reload Failed",
                        description=f"Error reloading `{cog_name}`:\n```\n{str(e)}\n```",
                        color=0xFF0000,
                        timestamp=datetime.now(timezone.utc),
                    )
                    await interaction.followup.send(embed=embed)
                    if self.logger:
                        self.logger.error(
                            f"Failed to reload {cog_name}: {traceback.format_exc()}"
                        )

        except Exception as e:
            await interaction.followup.send(
                f"❌ Unexpected error during reload: {str(e)}", ephemeral=True
            )

    @app_commands.command(
        name="system", description="📊 Show detailed system information"
    )
    async def system_command(self, interaction: discord.Interaction):
        """Show detailed system information with caching"""
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
            try:
                process = psutil.Process()
                system_info = {
                    "cpu_percent": psutil.cpu_percent(interval=0.5),
                    "memory": psutil.virtual_memory(),
                    "disk": psutil.disk_usage("/"),
                    "process_memory": process.memory_info(),
                    "process_cpu": process.cpu_percent(),
                    "uptime": time.time() - process.create_time(),
                    "python_version": sys.version,
                    "discord_py_version": discord.__version__,
                    "cogs_loaded": len(self.bot.cogs),
                    "commands_loaded": len(self.bot.tree.get_commands()),
                }
                self._system_info_cache = system_info
                self._cache_time = current_time
            except Exception as e:
                await interaction.followup.send(
                    f"❌ Error gathering system info: {str(e)}"
                )
                return

        # Create enhanced system info embed
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
            f"**Uptime:** {timedelta(seconds=int(system_info['uptime']))}\n"
            f"**Latency:** {self.bot.latency * 1000:.1f}ms",
            inline=False,
        )

        # Bot Statistics
        guild_count = len(self.bot.guilds)
        user_count = sum(guild.member_count or 0 for guild in self.bot.guilds)

        embed.add_field(
            name="📈 Bot Statistics",
            value=f"**Guilds:** {guild_count:,}\n"
            f"**Users:** {user_count:,}\n"
            f"**Cogs Loaded:** {system_info['cogs_loaded']}\n"
            f"**Commands:** {system_info['commands_loaded']}",
            inline=False,
        )

        # Version Information
        python_version = system_info["python_version"].split()[0]
        embed.add_field(
            name="🔧 Version Information",
            value=f"**Python:** {python_version}\n"
            f"**Discord.py:** {system_info['discord_py_version']}\n"
            f"**AI Engine:** {'✅ Available' if AI_ENGINE_AVAILABLE else '❌ Not Available'}",
            inline=False,
        )

        # Performance info
        cache_stats = (
            f"**Cache Size:** {len(self.cache._cache)}/{self.cache.max_size}\n"
        )
        cache_stats += f"**Cache Hit Rate:** {self.cache.hit_rate:.1%}"

        embed.add_field(
            name="⚡ Performance",
            value=cache_stats,
            inline=False,
        )

        embed.set_footer(text="Cache refreshes every 60 seconds")
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="sync", description="🔄 Sync application commands to Discord"
    )
    @app_commands.describe(
        scope="Where to sync commands to (guild or global)",
        clear="Clear all commands first",
    )
    async def sync_command(
        self,
        interaction: discord.Interaction,
        scope: Literal["guild", "global"] = "guild",
        clear: bool = False,
    ):
        """Sync application commands to Discord (Owner only)"""
        if not await self.is_owner(interaction.user.id):
            await interaction.response.send_message(
                "❌ This command can only be used by the bot owner.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        try:
            if scope == "guild":
                if clear:
                    self.bot.tree.clear_commands(guild=interaction.guild)
                    await self.bot.tree.sync(guild=interaction.guild)
                    await asyncio.sleep(2)

                synced = await self.bot.tree.sync(guild=interaction.guild)
                embed = discord.Embed(
                    title="✅ Commands Synced",
                    description=f"Successfully synced **{len(synced)}** commands to this server.",
                    color=0x00FF00,
                    timestamp=datetime.now(timezone.utc),
                )

            else:  # Global sync
                if clear:
                    self.bot.tree.clear_commands(guild=None)
                    await self.bot.tree.sync()
                    await asyncio.sleep(5)

                synced = await self.bot.tree.sync()
                embed = discord.Embed(
                    title="✅ Commands Synced",
                    description=f"Successfully synced **{len(synced)}** commands globally.\n\n⚠️ **Note:** Global commands may take up to 1 hour to update.",
                    color=0x00FF00,
                    timestamp=datetime.now(timezone.utc),
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="❌ Sync Failed",
                description=f"Error syncing commands:\n```\n{str(e)}\n```",
                color=0xFF0000,
                timestamp=datetime.now(timezone.utc),
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="logs", description="📋 View recent bot logs")
    @app_commands.describe(lines="Number of log lines to show (default: 50, max: 200)")
    async def logs_command(self, interaction: discord.Interaction, lines: int = 50):
        """View recent bot logs (Admin only)"""
        if not await self.is_admin_or_owner(interaction):
            await interaction.response.send_message(
                "❌ This command requires administrator permissions or bot ownership.",
                ephemeral=True,
            )
            return

        # Limit lines to prevent abuse
        lines = min(max(lines, 1), 200)

        await interaction.response.defer(ephemeral=True)

        try:
            log_files = ["logs/astra.log", "logs/bot.log", "astra.log", "bot.log"]
            log_file = None

            for file_path in log_files:
                if os.path.exists(file_path):
                    log_file = file_path
                    break

            if not log_file:
                await interaction.followup.send(
                    "❌ No log files found.", ephemeral=True
                )
                return

            # Read last N lines efficiently
            with open(log_file, "r", encoding="utf-8") as f:
                log_lines = f.readlines()

            recent_logs = log_lines[-lines:] if len(log_lines) > lines else log_lines
            log_content = "".join(recent_logs)

            # Truncate if too long for Discord
            if len(log_content) > 1900:
                log_content = log_content[-1900:]
                log_content = "...\n" + log_content[log_content.find("\n") + 1 :]

            embed = discord.Embed(
                title="📋 Recent Bot Logs",
                description=f"```\n{log_content}\n```",
                color=0x00BFFF,
                timestamp=datetime.now(timezone.utc),
            )
            embed.set_footer(text=f"Last {len(recent_logs)} lines from {log_file}")

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            await interaction.followup.send(
                f"❌ Error reading logs: {str(e)}", ephemeral=True
            )

    @app_commands.command(name="purge", description="🗑️ Delete multiple messages")
    @app_commands.describe(
        amount="Number of messages to delete (max 100)",
        user="Only delete messages from this user",
    )
    async def purge_command(
        self,
        interaction: discord.Interaction,
        amount: int,
        user: Optional[discord.Member] = None,
    ):
        """Delete multiple messages (Mod only)"""
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.", ephemeral=True
            )
            return

        if amount < 1 or amount > 100:
            await interaction.response.send_message(
                "❌ Please specify a number between 1 and 100.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        try:

            def check_messages(message):
                if user:
                    return message.author == user
                return True

            deleted = await interaction.channel.purge(
                limit=amount, check=check_messages, bulk=True
            )

            embed = discord.Embed(
                title="🗑️ Purge Complete",
                description=f"Successfully deleted **{len(deleted)}** message(s).",
                color=0x00FF00,
            )

            if user:
                embed.add_field(
                    name="Filter",
                    value=f"Messages from {user.mention} only",
                    inline=True,
                )

            await interaction.followup.send(embed=embed, ephemeral=True)

            if self.logger:
                self.logger.info(
                    f"Purge: {interaction.user} deleted {len(deleted)} messages in #{interaction.channel.name}"
                )

        except Exception as e:
            await interaction.followup.send(
                f"❌ Error deleting messages: {str(e)}", ephemeral=True
            )

    @app_commands.command(
        name="config", description="⚙️ View or change bot configuration"
    )
    @app_commands.describe(
        setting="Configuration setting to view/change",
        value="New value for the setting",
    )
    async def config_command(
        self,
        interaction: discord.Interaction,
        setting: str,
        value: Optional[str] = None,
    ):
        """View or change bot configuration (Admin only)"""
        if not await self.is_admin_or_owner(interaction):
            await interaction.response.send_message(
                "❌ This command requires administrator permissions or bot ownership.",
                ephemeral=True,
            )
            return

        guild_id = interaction.guild.id if interaction.guild else None

        if not guild_id:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.", ephemeral=True
            )
            return

        # Use enhanced config if available, fallback to legacy
        try:
            guild_config = self.config.get_guild_config(guild_id)
        except:
            guild_config = self.legacy_config.load_guild_config(guild_id)

        # If just viewing a setting
        if value is None:
            try:
                keys = setting.split(".")
                current_value = guild_config

                for key in keys:
                    current_value = current_value[key]

                embed = discord.Embed(
                    title=f"⚙️ Configuration: {setting}",
                    description=f"Current value for `{setting}`:",
                    color=0x00BFFF,
                    timestamp=datetime.now(timezone.utc),
                )

                # Format value based on type
                if isinstance(current_value, bool):
                    formatted_value = "✅ Enabled" if current_value else "❌ Disabled"
                elif isinstance(current_value, (list, dict)):
                    formatted_value = (
                        f"```json\n{json.dumps(current_value, indent=2)}\n```"
                    )
                else:
                    formatted_value = str(current_value)

                embed.add_field(name="Value", value=formatted_value, inline=False)
                await interaction.response.send_message(embed=embed)

            except (KeyError, TypeError):
                await interaction.response.send_message(
                    f"❌ Configuration setting `{setting}` not found.", ephemeral=True
                )

        else:
            # Setting a value - parse intelligently
            try:
                if value.lower() in ("true", "yes", "enable", "enabled", "on", "1"):
                    parsed_value = True
                elif value.lower() in (
                    "false",
                    "no",
                    "disable",
                    "disabled",
                    "off",
                    "0",
                ):
                    parsed_value = False
                elif value.lower() in ("null", "none"):
                    parsed_value = None
                elif value.startswith(("[", "{")):
                    parsed_value = json.loads(value)
                else:
                    try:
                        parsed_value = int(value) if value.isdigit() else float(value)
                    except:
                        parsed_value = value

                # Try enhanced config first
                try:
                    success = self.config.set_guild_setting(
                        guild_id, setting, parsed_value
                    )
                except:
                    success = self.legacy_config.set_guild_setting(
                        guild_id, setting, parsed_value
                    )

                if success:
                    embed = discord.Embed(
                        title="✅ Configuration Updated",
                        description=f"Successfully updated `{setting}`.",
                        color=0x00FF00,
                        timestamp=datetime.now(timezone.utc),
                    )
                    embed.add_field(
                        name="New Value", value=str(parsed_value), inline=False
                    )
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message(
                        f"❌ Failed to update the setting `{setting}`.", ephemeral=True
                    )

            except Exception as e:
                await interaction.response.send_message(
                    f"❌ Error updating configuration: {str(e)}", ephemeral=True
                )


async def setup(bot):
    await bot.add_cog(OptimizedAdmin(bot))
