"""
Astra Discord Bot - Enhanced Main Application
A comprehensive AI-powered Discord bot for space exploration and server management

Author: x1ziad
Version: 2.0.0
Release Date: 2025-08-02 10:53:48 UTC
License: MIT

Features:
- Advanced AI capabilities with Azure OpenAI integration
- Comprehensive server management and analytics
- Real-time monitoring and health checks
- Graceful error handling and recovery
- Hot-reloadable configuration system
- Production-ready logging and metrics
"""

import asyncio
import logging
import os
import platform
import signal
import sys
import traceback
import psutil
import gc
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any, Callable
from dataclasses import dataclass, field
from contextlib import asynccontextmanager

import discord
from discord import app_commands
from discord.ext import commands, tasks
import aiohttp

# Core imports
from config.config_manager import config_manager, BotConfig
from logger.enhanced_logger import setup_enhanced_logger, log_performance
from utils.database import db
from utils.error_handler import ErrorHandler
from utils.permissions import PermissionLevel, has_permission

# Try to load optional dependencies
try:
    from dotenv import load_dotenv
    load_dotenv()
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False

try:
    import colorlog
    HAS_COLORLOG = True
except ImportError:
    HAS_COLORLOG = False


@dataclass
class BotStats:
    """Bot runtime statistics"""
    start_time: datetime = field(default_factory=datetime.utcnow)
    commands_executed: int = 0
    messages_processed: int = 0
    errors_handled: int = 0
    guilds_joined: int = 0
    guilds_left: int = 0
    uptime_seconds: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    
    def get_uptime(self) -> timedelta:
        """Get current uptime"""
        return datetime.utcnow() - self.start_time
    
    def update_system_stats(self):
        """Update system resource usage"""
        process = psutil.Process()
        self.memory_usage_mb = process.memory_info().rss / 1024 / 1024
        self.cpu_usage_percent = process.cpu_percent()
        self.uptime_seconds = self.get_uptime().total_seconds()


class AstraBot(commands.Bot):
    """Enhanced Astra Discord Bot with comprehensive features and monitoring"""

    def __init__(self):
        # Load configuration
        self.config: BotConfig = config_manager.get_bot_config()
        
        # Set up enhanced logging
        self.logger = setup_enhanced_logger(
            name="Astra",
            log_level="DEBUG" if self.config.debug else "INFO"
        )
        
        self.logger.info("=" * 80)
        self.logger.info(f"🚀 Initializing {self.config.name} v{self.config.version}")
        self.logger.info(f"📅 Build Date: 2025-08-02 10:53:48 UTC")
        self.logger.info(f"👤 Started by: {self._get_current_user()}")
        self.logger.info(f"🐍 Python: {platform.python_version()}")
        self.logger.info(f"💻 Platform: {platform.system()} {platform.release()}")
        self.logger.info("=" * 80)
        
        # Enhanced intents for comprehensive functionality
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.presences = True
        intents.voice_states = True
        intents.guild_reactions = True
        intents.guild_typing = True
        intents.dm_reactions = True
        intents.dm_typing = True
        
        # Initialize bot with enhanced settings
        super().__init__(
            command_prefix=self._get_dynamic_prefix,
            intents=intents,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="the cosmic frontier 🌌"
            ),
            status=discord.Status.online,
            allowed_mentions=discord.AllowedMentions(
                everyone=False,
                roles=False,
                users=True,
                replied_user=True
            ),
            help_command=None,  # Custom help system
            case_insensitive=True,
            strip_after_prefix=True,
            owner_id=self.config.owner_id
        )
        
        # Bot state and tracking
        self.stats = BotStats()
        self.session: Optional[aiohttp.ClientSession] = None
        self._tasks: Set[asyncio.Task] = set()
        self._ready = False
        self._shutdown_initiated = False
        
        # Feature tracking
        self.loaded_extensions: Dict[str, datetime] = {}
        self.failed_extensions: Dict[str, str] = {}
        self.extension_health: Dict[str, bool] = {}
        
        # Cache and performance
        self._command_cache: Dict[str, Any] = {}
        self._guild_configs: Dict[int, Dict[str, Any]] = {}
        
        # Error handling
        self.error_handler = ErrorHandler(self)
        
        # Create essential directories
        self._ensure_directories()
        
        self.logger.info("✅ Bot initialization completed")
    
    def _get_current_user(self) -> str:
        """Get current user with enhanced detection"""
        methods = [
            lambda: os.environ.get("USER"),
            lambda: os.environ.get("USERNAME"), 
            lambda: os.environ.get("LOGNAME"),
            lambda: os.getlogin(),
            lambda: "docker-container" if os.path.exists("/.dockerenv") else None,
            lambda: "container-user"
        ]
        
        for method in methods:
            try:
                result = method()
                if result:
                    return result
            except (OSError, AttributeError):
                continue
        
        return "unknown-user"
    
    def _ensure_directories(self):
        """Create all necessary directories"""
        directories = [
            "logs", "data", "data/ai", "data/ai/images", "data/ai/audio",
            "data/analytics", "data/analytics/daily_reports", 
            "data/guilds", "data/database", "config", "ai/personalities"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        self.logger.debug(f"📁 Created {len(directories)} essential directories")
    
    async def _get_dynamic_prefix(self, bot, message) -> List[str]:
        """Dynamic prefix system with guild-specific support"""
        prefixes = []
        
        # Always respond to mentions
        prefixes.extend([f"<@{self.user.id}> ", f"<@!{self.user.id}> "])
        
        # Guild-specific prefixes
        if hasattr(message, 'guild') and message.guild:
            guild_prefix = await db.get("guild_configs", str(message.guild.id), {}).get("prefix")
            if guild_prefix:
                prefixes.append(guild_prefix)
            else:
                prefixes.append(self.config.prefix)
        else:
            prefixes.append(self.config.prefix)
        
        return prefixes
    
    @log_performance
    async def setup_hook(self):
        """Enhanced setup hook with comprehensive initialization"""
        self.logger.info("🔧 Running enhanced setup hook...")
        
        # Initialize HTTP session with advanced configuration
        await self._setup_http_session()
        
        # Initialize database connections
        await self._initialize_database()
        
        # Load extensions with dependency management
        await self._load_extensions_with_dependencies()
        
        # Start background tasks
        self._start_background_tasks()
        
        # Register event handlers
        self._register_event_handlers()
        
        # Setup command tree error handling
        self.tree.error(self._handle_app_command_error)
        
        self.logger.info("✅ Enhanced setup hook completed successfully")
    
    async def _setup_http_session(self):
        """Setup HTTP session with advanced configuration"""
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=30,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=60,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(
            total=30,
            connect=10,
            sock_read=10
        )
        
        headers = {
            "User-Agent": f"{self.config.name}/{self.config.version} (Discord Bot)",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate"
        }
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers,
            raise_for_status=False
        )
        
        self.logger.info("🌐 HTTP session initialized with advanced configuration")
    
    async def _initialize_database(self):
        """Initialize database connections and create tables"""
        try:
            # Create essential tables
            essential_tables = [
                "guild_configs", "user_profiles", "command_stats", 
                "error_logs", "performance_metrics", "feature_flags"
            ]
            
            for table in essential_tables:
                await db.get_table(table)  # This creates the table if it doesn't exist
            
            self.logger.info(f"💾 Database initialized with {len(essential_tables)} tables")
            
        except Exception as e:
            self.logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    async def _load_extensions_with_dependencies(self):
        """Load extensions with proper dependency management and error recovery"""
        
        # Extension loading order with dependencies
        extension_groups = [
            # Core utilities (no dependencies)
            ["cogs.admin", "cogs.stats"],
            
            # AI and enhanced features (depend on core)
            ["cogs.ai_commands", "cogs.server_management"], 
            
            # Analytics and specialized features
            ["cogs.analytics", "cogs.roles"],
            
            # Game-specific and optional features
            ["cogs.quiz", "cogs.space"]
        ]
        
        total_loaded = 0
        total_failed = 0
        
        for group in extension_groups:
            self.logger.info(f"📦 Loading extension group: {', '.join(group)}")
            
            for extension in group:
                try:
                    await self.load_extension(extension)
                    self.loaded_extensions[extension] = datetime.utcnow()
                    self.extension_health[extension] = True
                    total_loaded += 1
                    self.logger.info(f"✅ Loaded {extension}")
                    
                except Exception as e:
                    error_msg = str(e)
                    self.failed_extensions[extension] = error_msg
                    self.extension_health[extension] = False
                    total_failed += 1
                    self.logger.error(f"❌ Failed to load {extension}: {error_msg}")
                    
                    # Log detailed traceback for debugging
                    self.logger.debug(f"Traceback for {extension}:\n{traceback.format_exc()}")
            
            # Small delay between groups to prevent overwhelming
            await asyncio.sleep(0.1)
        
        # Summary
        self.logger.info("=" * 60)
        self.logger.info(f"📦 Extension Loading Summary:")
        self.logger.info(f"   ✅ Loaded: {total_loaded}")
        self.logger.info(f"   ❌ Failed: {total_failed}")
        self.logger.info(f"   📊 Success Rate: {(total_loaded/(total_loaded+total_failed))*100:.1f}%")
        
        if self.failed_extensions:
            self.logger.warning("Failed extensions:")
            for ext, error in self.failed_extensions.items():
                self.logger.warning(f"   • {ext}: {error}")
        
        self.logger.info("=" * 60)
    
    def _start_background_tasks(self):
        """Start all background monitoring and maintenance tasks"""
        background_tasks = [
            self.monitor_system_health,
            self.update_statistics,
            self.cleanup_old_data,
            self.sync_guild_configs,
            self.monitor_extensions
        ]
        
        for task_func in background_tasks:
            task = self.create_task(task_func.start())
            self.logger.debug(f"🔄 Started background task: {task_func.__name__}")
        
        self.logger.info(f"🔄 Started {len(background_tasks)} background tasks")
    
    def _register_event_handlers(self):
        """Register enhanced event handlers"""
        
        @self.event
        async def on_ready():
            """Enhanced ready event with comprehensive initialization"""
            if self._ready:
                return  # Prevent multiple ready events
            
            self._ready = True
            
            # Calculate statistics
            total_members = sum(guild.member_count or 0 for guild in self.guilds)
            unique_members = len(set(member.id for guild in self.guilds for member in guild.members))
            
            # System information
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            # Log comprehensive ready information
            self.logger.info("=" * 80)
            self.logger.info(f"🎉 {self.config.name} v{self.config.version} is ONLINE!")
            self.logger.info(f"🤖 Bot: {self.user} (ID: {self.user.id})")
            self.logger.info(f"🏠 Guilds: {len(self.guilds):,}")
            self.logger.info(f"👥 Total Members: {total_members:,} ({unique_members:,} unique)")
            self.logger.info(f"⚡ WebSocket Latency: {self.latency * 1000:.2f}ms")
            self.logger.info(f"💾 Memory Usage: {memory_mb:.1f} MB")
            self.logger.info(f"🐍 Discord.py Version: {discord.__version__}")
            self.logger.info(f"⏱️ Startup Time: {self.stats.get_uptime().total_seconds():.2f}s")
            
            # Sync application commands if enabled
            if self.config.get("bot_settings.command_sync_on_ready", True):
                await self._sync_commands()
            
            # Update bot statistics
            self.stats.update_system_stats()
            
            # Log guild information
            self.logger.info("\n📋 Connected Guilds:")
            for guild in sorted(self.guilds, key=lambda g: g.member_count or 0, reverse=True):
                self.logger.info(f"   • {guild.name} ({guild.member_count:,} members) [ID: {guild.id}]")
            
            self.logger.info("=" * 80)
            self.logger.info("🎯 All systems operational and ready for action!")
            self.logger.info("=" * 80)
        
        @self.event
        async def on_guild_join(guild):
            """Enhanced guild join handling"""
            self.stats.guilds_joined += 1
            
            self.logger.info(f"🎉 Joined guild: {guild.name} (ID: {guild.id})")
            self.logger.info(f"   👥 Members: {guild.member_count:,}")
            self.logger.info(f"   📅 Created: {guild.created_at.strftime('%Y-%m-%d')}")
            self.logger.info(f"   👑 Owner: {guild.owner}")
            
            # Initialize guild configuration
            await self._initialize_guild_config(guild)
            
            # Sync commands if enabled
            if self.config.get("bot_settings.command_sync_on_join", True):
                try:
                    await self.tree.sync(guild=guild)
                    self.logger.info(f"✅ Synced commands for {guild.name}")
                except Exception as e:
                    self.logger.error(f"❌ Failed to sync commands for {guild.name}: {e}")
        
        @self.event
        async def on_guild_remove(guild):
            """Enhanced guild leave handling"""
            self.stats.guilds_left += 1
            
            self.logger.info(f"👋 Left guild: {guild.name} (ID: {guild.id})")
            
            # Cleanup guild data if configured
            if self.config.get("bot_settings.cleanup_on_leave", False):
                await self._cleanup_guild_data(guild.id)
        
        @self.event
        async def on_message(message):
            """Enhanced message processing with analytics"""
            if not self._ready or message.author.bot:
                return
            
            self.stats.messages_processed += 1
            
            # Process commands
            await self.process_commands(message)
        
        @self.event
        async def on_command(ctx):
            """Track command usage and performance"""
            self.stats.commands_executed += 1
            
            # Log command usage
            self.logger.info(
                f"💬 Command: {ctx.command.qualified_name} | "
                f"User: {ctx.author} | Guild: {getattr(ctx.guild, 'name', 'DM')}"
            )
            
            # Update command statistics
            await self._update_command_stats(ctx)
        
        @self.event
        async def on_command_error(ctx, error):
            """Enhanced command error handling"""
            await self.error_handler.handle_command_error(ctx, error)
            self.stats.errors_handled += 1
    
    async def _sync_commands(self):
        """Sync application commands with enhanced error handling"""
        try:
            self.logger.info("🔄 Syncing application commands...")
            start_time = datetime.utcnow()
            
            synced = await self.tree.sync()
            
            sync_time = (datetime.utcnow() - start_time).total_seconds()
            self.logger.info(f"✅ Synced {len(synced)} commands in {sync_time:.2f}s")
            
            # Log command details
            for cmd in synced:
                if isinstance(cmd, app_commands.Group):
                    subcmds = len(cmd.commands)
                    self.logger.debug(f"   📁 Group: {cmd.name} ({subcmds} subcommands)")
                else:
                    self.logger.debug(f"   🔧 Command: {cmd.name}")
            
        except discord.HTTPException as e:
            self.logger.error(f"❌ HTTP error syncing commands: {e}")
            if e.status == 429:
                self.logger.warning("⏰ Rate limited - commands will sync later")
        except Exception as e:
            self.logger.error(f"❌ Unexpected error syncing commands: {e}")
    
    async def _handle_app_command_error(self, interaction: discord.Interaction, error):
        """Enhanced application command error handling"""
        self.stats.errors_handled += 1
        
        # Log error details
        command_name = interaction.command.name if interaction.command else "unknown"
        self.logger.error(f"App command error in {command_name}: {error}")
        
        # Determine response method
        if interaction.response.is_done():
            send_func = interaction.followup.send
        else:
            send_func = interaction.response.send_message
        
        # Handle specific error types
        if isinstance(error, app_commands.CommandOnCooldown):
            await send_func(
                f"⏰ Command on cooldown! Try again in {error.retry_after:.1f} seconds.",
                ephemeral=True
            )
        elif isinstance(error, app_commands.MissingPermissions):
            await send_func(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
        elif isinstance(error, app_commands.CheckFailure):
            await send_func(
                "❌ You cannot use this command right now.",
                ephemeral=True
            )
        else:
            # Log unexpected errors
            self.logger.error(f"Unexpected app command error: {traceback.format_exc()}")
            await send_func(
                "❌ An unexpected error occurred. The issue has been logged.",
                ephemeral=True
            )
        
        # Save error to database for analysis
        await self._log_error_to_database(interaction, error)
    
    async def _initialize_guild_config(self, guild: discord.Guild):
        """Initialize configuration for a new guild"""
        config = {
            "guild_id": guild.id,
            "guild_name": guild.name,
            "joined_at": datetime.utcnow().isoformat(),
            "prefix": self.config.prefix,
            "features": self.config.features.copy(),
            "ai_personality": "default",
            "auto_moderation": False,
            "analytics_enabled": True
        }
        
        await db.set("guild_configs", str(guild.id), config)
        self.logger.debug(f"📋 Initialized config for guild: {guild.name}")
    
    async def _cleanup_guild_data(self, guild_id: int):
        """Clean up data for a guild that was left"""
        tables_to_clean = ["guild_configs", "user_profiles", "command_stats"]
        
        for table in tables_to_clean:
            await db.delete(table, str(guild_id))
        
        self.logger.debug(f"🧹 Cleaned up data for guild ID: {guild_id}")
    
    async def _update_command_stats(self, ctx):
        """Update command usage statistics"""
        stats_key = f"{ctx.guild.id if ctx.guild else 'dm'}_{ctx.command.qualified_name}"
        current_stats = await db.get("command_stats", stats_key, {"count": 0, "last_used": None})
        
        current_stats["count"] += 1
        current_stats["last_used"] = datetime.utcnow().isoformat()
        
        await db.set("command_stats", stats_key, current_stats)
    
    async def _log_error_to_database(self, interaction: discord.Interaction, error):
        """Log error details to database for analysis"""
        error_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "command": interaction.command.name if interaction.command else "unknown",
            "user_id": interaction.user.id,
            "guild_id": interaction.guild_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc()
        }
        
        error_key = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{interaction.user.id}"
        await db.set("error_logs", error_key, error_data)
    
    def create_task(self, coro, *, name: str = None) -> asyncio.Task:
        """Create and track async tasks for proper cleanup"""
        task = asyncio.create_task(coro, name=name)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task
    
    # Background Tasks
    @tasks.loop(minutes=5)
    async def monitor_system_health(self):
        """Monitor system health and performance"""
        try:
            self.stats.update_system_stats()
            
            # Check memory usage
            if self.stats.memory_usage_mb > 512:  # 512 MB threshold
                self.logger.warning(f"⚠️ High memory usage: {self.stats.memory_usage_mb:.1f} MB")
            
            # Check if any extensions are unhealthy
            unhealthy_extensions = [ext for ext, health in self.extension_health.items() if not health]
            if unhealthy_extensions:
                self.logger.warning(f"⚠️ Unhealthy extensions: {', '.join(unhealthy_extensions)}")
            
            # Force garbage collection periodically
            if self.stats.get_uptime().total_seconds() % 3600 < 300:  # Every hour
                collected = gc.collect()
                self.logger.debug(f"🗑️ Garbage collection: {collected} objects collected")
            
        except Exception as e:
            self.logger.error(f"Error in health monitoring: {e}")
    
    @tasks.loop(minutes=10)
    async def update_statistics(self):
        """Update and save bot statistics"""
        try:
            stats_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "uptime_seconds": self.stats.uptime_seconds,
                "commands_executed": self.stats.commands_executed,
                "messages_processed": self.stats.messages_processed,
                "errors_handled": self.stats.errors_handled,
                "guilds_count": len(self.guilds),
                "memory_usage_mb": self.stats.memory_usage_mb,
                "cpu_usage_percent": self.stats.cpu_usage_percent,
                "latency_ms": self.latency * 1000
            }
            
            await db.set("performance_metrics", datetime.utcnow().strftime("%Y%m%d_%H%M"), stats_data)
            
        except Exception as e:
            self.logger.error(f"Error updating statistics: {e}")
    
    @tasks.loop(hours=6)
    async def cleanup_old_data(self):
        """Clean up old data to prevent storage bloat"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            cutoff_str = cutoff_date.strftime("%Y%m%d")
            
            # Clean old performance metrics
            metrics = await db.get_table("performance_metrics")
            old_keys = [key for key in metrics.keys() if key < cutoff_str]
            
            for key in old_keys:
                await db.delete("performance_metrics", key)
            
            if old_keys:
                self.logger.info(f"🧹 Cleaned {len(old_keys)} old performance metrics")
            
        except Exception as e:
            self.logger.error(f"Error in data cleanup: {e}")
    
    @tasks.loop(minutes=30)
    async def sync_guild_configs(self):
        """Sync guild configurations and handle changes"""
        try:
            for guild in self.guilds:
                guild_config = await db.get("guild_configs", str(guild.id))
                if guild_config:
                    # Update guild name if changed
                    if guild_config.get("guild_name") != guild.name:
                        guild_config["guild_name"] = guild.name
                        await db.set("guild_configs", str(guild.id), guild_config)
                else:
                    # Initialize config for new guilds
                    await self._initialize_guild_config(guild)
            
        except Exception as e:
            self.logger.error(f"Error syncing guild configs: {e}")
    
    @tasks.loop(minutes=15)
    async def monitor_extensions(self):
        """Monitor extension health and attempt recovery"""
        try:
            for extension_name in list(self.loaded_extensions.keys()):
                try:
                    # Try to access the extension
                    ext = self.get_cog(extension_name.split('.')[-1].title().replace('_', ''))
                    if ext is None:
                        self.extension_health[extension_name] = False
                        self.logger.warning(f"⚠️ Extension {extension_name} appears to be unhealthy")
                    else:
                        self.extension_health[extension_name] = True
                except Exception as e:
                    self.extension_health[extension_name] = False
                    self.logger.error(f"❌ Extension {extension_name} health check failed: {e}")
            
        except Exception as e:
            self.logger.error(f"Error monitoring extensions: {e}")
    
    # Enhanced utility methods
    async def get_guild_config(self, guild_id: int) -> Dict[str, Any]:
        """Get configuration for a specific guild"""
        if guild_id in self._guild_configs:
            return self._guild_configs[guild_id]
        
        config = await db.get("guild_configs", str(guild_id), {})
        self._guild_configs[guild_id] = config
        return config
    
    async def update_guild_config(self, guild_id: int, key: str, value: Any):
        """Update a specific configuration value for a guild"""
        config = await self.get_guild_config(guild_id)
        config[key] = value
        await db.set("guild_configs", str(guild_id), config)
        self._guild_configs[guild_id] = config
    
    def get_extension_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all extensions"""
        status = {}
        for ext_name in self.loaded_extensions:
            status[ext_name] = {
                "loaded": True,
                "healthy": self.extension_health.get(ext_name, False),
                "loaded_at": self.loaded_extensions[ext_name].isoformat()
            }
        
        for ext_name, error in self.failed_extensions.items():
            status[ext_name] = {
                "loaded": False,
                "healthy": False,
                "error": error
            }
        
        return status
    
    async def reload_extension_safe(self, extension_name: str) -> bool:
        """Safely reload an extension with error handling"""
        try:
            await self.reload_extension(extension_name)
            self.extension_health[extension_name] = True
            self.loaded_extensions[extension_name] = datetime.utcnow()
            if extension_name in self.failed_extensions:
                del self.failed_extensions[extension_name]
            
            self.logger.info(f"🔄 Successfully reloaded {extension_name}")
            return True
            
        except Exception as e:
            self.extension_health[extension_name] = False
            self.failed_extensions[extension_name] = str(e)
            self.logger.error(f"❌ Failed to reload {extension_name}: {e}")
            return False
    
    async def close(self):
        """Enhanced cleanup with comprehensive resource management"""
        if self._shutdown_initiated:
            return
        
        self._shutdown_initiated = True
        self.logger.info("🔄 Initiating graceful shutdown...")
        
        try:
            # Stop background tasks
            tasks_to_stop = [
                self.monitor_system_health,
                self.update_statistics,
                self.cleanup_old_data,
                self.sync_guild_configs,
                self.monitor_extensions
            ]
            
            for task in tasks_to_stop:
                if task.is_running():
                    task.cancel()
                    self.logger.debug(f"🛑 Stopped task: {task.coro.__name__}")
            
            # Save final statistics
            await self.update_statistics()
            
            # Cancel user tasks
            if self._tasks:
                self.logger.info(f"🔄 Cancelling {len(self._tasks)} running tasks...")
                for task in self._tasks:
                    if not task.done():
                        task.cancel()
                
                # Wait for tasks to complete cancellation
                await asyncio.gather(*self._tasks, return_exceptions=True)
            
            # Close HTTP session
            if self.session and not self.session.closed:
                await self.session.close()
                self.logger.debug("🌐 HTTP session closed")
            
            # Log final statistics
            uptime = self.stats.get_uptime()
            self.logger.info("=" * 60)
            self.logger.info("📊 Final Statistics:")
            self.logger.info(f"   ⏱️ Uptime: {uptime}")
            self.logger.info(f"   💬 Commands Executed: {self.stats.commands_executed:,}")
            self.logger.info(f"   📨 Messages Processed: {self.stats.messages_processed:,}")
            self.logger.info(f"   ❌ Errors Handled: {self.stats.errors_handled:,}")
            self.logger.info(f"   🏠 Guilds Joined: {self.stats.guilds_joined}")
            self.logger.info(f"   👋 Guilds Left: {self.stats.guilds_left}")
            self.logger.info("=" * 60)
            
        except Exception as e:
            self.logger.error(f"❌ Error during shutdown: {e}")
        
        finally:
            # Call parent close
            await super().close()
            self.logger.info("👋 Astra bot shutdown completed")


# Global command registration
def register_global_commands(bot: AstraBot):
    """Register global utility commands"""
    
    @bot.tree.command(name="help", description="Show available commands and bot information")
    async def help_command(interaction: discord.Interaction):
        """Enhanced help command with categorized commands"""
        embed = discord.Embed(
            title=f"🚀 {bot.config.name} Help",
            description=f"Version {bot.config.version} - Your cosmic companion",
            color=config_manager.get_color("primary"),
            timestamp=datetime.utcnow()
        )
        
        # Get all commands organized by cogs
        cog_commands = {}
        for command in bot.tree.get_commands():
            if isinstance(command, app_commands.Group):
                cog_name = command.name.title()
                if cog_name not in cog_commands:
                    cog_commands[cog_name] = []
                for subcommand in command.commands:
                    cog_commands[cog_name].append(f"/{command.name} {subcommand.name}")
            else:
                cog_name = "Utility"
                if cog_name not in cog_commands:
                    cog_commands[cog_name] = []
                cog_commands[cog_name].append(f"/{command.name}")
        
        # Add fields for each category
        for cog_name, commands in cog_commands.items():
            if commands:
                embed.add_field(
                    name=f"📁 {cog_name}",
                    value="\n".join(commands[:10]) + ("..." if len(commands) > 10 else ""),
                    inline=True
                )
        
        # Add bot stats
        embed.add_field(
            name="📊 Bot Stats",
            value=f"Guilds: {len(bot.guilds)}\nUptime: {bot.stats.get_uptime()}",
            inline=True
        )
        
        embed.set_footer(
            text=f"Use /command to see specific options | {len(bot.tree.get_commands())} total commands"
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @bot.tree.command(name="ping", description="Check bot latency and system status")
    async def ping_command(interaction: discord.Interaction):
        """Enhanced ping command with system information"""
        start_time = datetime.utcnow()
        await interaction.response.defer()
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Determine color based on latency
        latency_ms = bot.latency * 1000
        if latency_ms < 100:
            color = config_manager.get_color("success")
            status = "🟢 Excellent"
        elif latency_ms < 300:
            color = config_manager.get_color("warning") 
            status = "🟡 Good"
        else:
            color = config_manager.get_color("error")
            status = "🔴 Poor"
        
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Connection Status: {status}",
            color=color,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📡 WebSocket Latency",
            value=f"{latency_ms:.2f}ms",
            inline=True
        )
        
        embed.add_field(
            name="⚡ Response Time", 
            value=f"{response_time:.2f}ms",
            inline=True
        )
        
        embed.add_field(
            name="💾 Memory Usage",
            value=f"{bot.stats.memory_usage_mb:.1f} MB",
            inline=True
        )
        
        embed.add_field(
            name="⏱️ Uptime",
            value=str(bot.stats.get_uptime()).split('.')[0],
            inline=True
        )
        
        embed.add_field(
            name="🏠 Guilds",
            value=f"{len(bot.guilds):,}",
            inline=True
        )
        
        embed.add_field(
            name="💬 Commands Used", 
            value=f"{bot.stats.commands_executed:,}",
            inline=True
        )
        
        await interaction.followup.send(embed=embed)
    
    @bot.tree.command(name="status", description="Show detailed bot status and health")
    async def status_command(interaction: discord.Interaction):
        """Detailed bot status command"""
        if not has_permission(interaction.user, PermissionLevel.MODERATOR):
            await interaction.response.send_message("❌ This command requires moderator permissions.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🔍 Bot Status Report",
            color=config_manager.get_color("info"),
            timestamp=datetime.utcnow()
        )
        
        # System stats
        embed.add_field(
            name="💻 System",
            value=f"Memory: {bot.stats.memory_usage_mb:.1f} MB\n"
                  f"CPU: {bot.stats.cpu_usage_percent:.1f}%\n"
                  f"Uptime: {bot.stats.get_uptime()}",
            inline=True
        )
        
        # Bot stats
        embed.add_field(
            name="🤖 Bot Activity",
            value=f"Commands: {bot.stats.commands_executed:,}\n"
                  f"Messages: {bot.stats.messages_processed:,}\n" 
                  f"Errors: {bot.stats.errors_handled:,}",
            inline=True
        )
        
        # Extension health
        healthy_extensions = sum(1 for health in bot.extension_health.values() if health)
        total_extensions = len(bot.extension_health)
        
        embed.add_field(
            name="🧩 Extensions",
            value=f"Healthy: {healthy_extensions}/{total_extensions}\n"
                  f"Failed: {len(bot.failed_extensions)}",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def main():
    """Enhanced main function with comprehensive error handling and monitoring"""
    
    # Initial logging setup
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s",
        datefmt="%H:%M:%S"
    )
    
    logger = logging.getLogger("Astra.Main")
    
    try:
        logger.info("=" * 80)
        logger.info("🚀 Starting Astra Discord Bot - Enhanced Edition")
        logger.info(f"📅 Build: 2025-08-02 10:53:48 UTC")
        logger.info(f"🐍 Python: {platform.python_version()}")
        logger.info(f"📦 Discord.py: {discord.__version__}")
        logger.info("=" * 80)
        
        # Environment validation
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            logger.critical("🚫 DISCORD_TOKEN environment variable not found!")
            logger.critical("Please set your Discord bot token in the environment variables.")
            return 1
        
        # Optional environment checks
        optional_vars = [
            "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_KEY", 
            "AZURE_SPEECH_KEY", "OPENAI_API_KEY"
        ]
        
        missing_optional = [var for var in optional_vars if not os.getenv(var)]
        if missing_optional:
            logger.warning(f"⚠️ Optional environment variables missing: {', '.join(missing_optional)}")
            logger.warning("Some AI features may not be available.")
        
        # Create bot instance
        async with AstraBot() as bot:
            
            # Register global commands
            register_global_commands(bot)
            
            # Set up signal handlers for graceful shutdown
            if hasattr(signal, 'SIGTERM'):
                loop = asyncio.get_running_loop()
                
                def signal_handler(signum, frame):
                    logger.info(f"🛑 Received signal {signum}, initiating graceful shutdown...")
                    asyncio.create_task(bot.close())
                
                for sig in (signal.SIGINT, signal.SIGTERM):
                    try:
                        loop.add_signal_handler(sig, lambda s=sig, f=None: signal_handler(s, f))
                    except NotImplementedError:
                        # Windows doesn't support signal handlers in asyncio
                        signal.signal(sig, signal_handler)
            
            # Start the bot
            logger.info("🎯 Starting bot connection...")
            await bot.start(token)
    
    except KeyboardInterrupt:
        logger.info("⌨️ Bot shutdown requested by user (Ctrl+C)")
        return 0
    
    except discord.LoginFailure:
        logger.critical("❌ Invalid Discord token! Please check your DISCORD_TOKEN.")
        return 1
    
    except discord.HTTPException as e:
        logger.critical(f"❌ Discord HTTP error: {e}")
        return 1
    
    except Exception as e:
        logger.critical(f"❌ Unexpected error during startup: {e}")
        logger.critical(traceback.format_exc())
        return 1
    
    finally:
        logger.info("👋 Main function completed")


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code or 0)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
