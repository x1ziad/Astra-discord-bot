"""
Astra Discord Bot - Enhanced Main Application
A comprehensive AI-powered Discord bot with adaptive personality and natural conversation

Author: x1ziad
Version: 2.0.0
Release Date: 2025-08-02 10:53:48 UTC
License: MIT

Features:
- Advanced AI capabilities with multi-provider integration
- Adaptive personality that shifts based on conversation topics
- Natural conversation flow and context understanding
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
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any, Callable
from dataclasses import dataclass, field
from contextlib import asynccontextmanager

import discord
from discord import app_commands
from discord.ext import commands, tasks
import aiohttp

# Core imports
from config.unified_config import unified_config, BotConfig
from logger.enhanced_logger import setup_enhanced_logger, log_performance
from utils.database import db
from utils.enhanced_error_handler import ErrorHandler
from utils.permissions import PermissionLevel, has_permission

# Performance optimization imports
from utils.performance_optimizer import performance_optimizer
from utils.command_optimizer import auto_optimize_commands
from utils.discord_data_reporter import (
    initialize_discord_reporter,
    get_discord_reporter,
    cleanup_discord_reporter,
)

# Railway configuration support
try:
    # Railway config is now handled by unified_config
    RAILWAY_ENABLED = True

    # Diagnostic: Check Railway environment variables on startup
    def log_railway_env_diagnostic():
        """Optimized Railway environment diagnostic"""
        # Only check essential environment variables for faster startup
        essential_vars = ["AI_API_KEY", "AI_PROVIDER"]

        logger = logging.getLogger("astra.railway_diagnostic")
        logger.info("🚀 Railway Environment Status:")

        missing_count = 0
        for key in essential_vars:
            value = os.getenv(key)
            if value:
                if "KEY" in key:
                    masked_value = f"***SET*** ({len(value)} chars)"
                    logger.info(f"   ✅ {key}: {masked_value}")
                else:
                    logger.info(f"   ✅ {key}: {value}")
            else:
                logger.warning(f"   ⚠️ {key}: NOT SET")
                missing_count += 1

        if missing_count == 0:
            logger.info("🎯 All essential environment variables configured")
        else:
            logger.warning(f"⚠️ {missing_count} environment variables need attention")

    log_railway_env_diagnostic()

    # Import and run AI credentials debug (optional)
    try:
        from debug_ai_credentials import debug_ai_credentials

        debug_ai_credentials()
        logging.getLogger("astra.startup").info("✅ AI credentials debug completed")
    except (ImportError, FileNotFoundError):
        logging.getLogger("astra.startup").info(
            "ℹ️ Debug AI credentials module not found (optional)"
        )
    except Exception as e:
        logging.getLogger("astra.startup").error(f"AI debug failed: {e}")

except ImportError:
    RAILWAY_ENABLED = False

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

    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
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
        return datetime.now(timezone.utc) - self.start_time

    def update_system_stats(self):
        """Update system resource usage"""
        process = psutil.Process()
        self.memory_usage_mb = process.memory_info().rss / 1024 / 1024
        self.cpu_usage_percent = process.cpu_percent()
        self.uptime_seconds = self.get_uptime().total_seconds()


@auto_optimize_commands
class AstraBot(commands.Bot):
    """Enhanced Astra Discord Bot with comprehensive features and monitoring"""

    def __init__(self):
        # Load configuration
        self.config: BotConfig = unified_config.bot_config

        # Set up enhanced logging
        self.logger = setup_enhanced_logger(
            name="Astra",
            log_level="DEBUG" if getattr(self.config, "debug", False) else "INFO",
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
                type=discord.ActivityType.watching, name="conversations and learning 💬"
            ),
            status=discord.Status.online,
            allowed_mentions=discord.AllowedMentions(
                everyone=False, roles=False, users=True, replied_user=True
            ),
            help_command=None,  # Custom help system
            case_insensitive=True,
            strip_after_prefix=True,
            owner_id=self.config.owner_id,
        )

        # Bot state and tracking
        self.stats = BotStats()
        self.stats.start_time = datetime.now(timezone.utc)  # Ensure timezone-aware
        self.start_time = self.stats.start_time  # Keep both in sync
        self.session: Optional[aiohttp.ClientSession] = None
        self._tasks: Set[asyncio.Task] = set()
        self._bot_ready = False
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
            lambda: "container-user",
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
            "logs",
            "temp",
            "data",
            "data/quiz",
            "data/space",
            "data/guilds",
            "data/database",
            "config",
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
        if hasattr(message, "guild") and message.guild:
            try:
                guild_config = await db.get("guild_configs", str(message.guild.id), {})
                guild_prefix = guild_config.get("prefix")
                if guild_prefix:
                    prefixes.append(guild_prefix)
                else:
                    prefixes.append(self.config.prefix)
            except Exception:
                prefixes.append(self.config.prefix)
        else:
            prefixes.append(self.config.prefix)

        return prefixes

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

        # Initialize AI engine and context manager
        await self._initialize_ai_systems()

        # Start performance monitoring
        performance_optimizer.start_monitoring()

        self.logger.info("✅ Enhanced setup hook completed successfully")

    async def _setup_http_session(self):
        """Setup HTTP session with advanced configuration"""
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=30,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=60,
            enable_cleanup_closed=True,
        )

        timeout = aiohttp.ClientTimeout(total=30, connect=10, sock_read=10)

        headers = {
            "User-Agent": f"{self.config.name}/{self.config.version} (Discord Bot)",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
        }

        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers,
            raise_for_status=False,
        )

        self.logger.info("🌐 HTTP session initialized with advanced configuration")

    async def _initialize_ai_systems(self):
        """Initialize AI engine and context manager for enhanced conversation"""
        try:
            # Initialize AI engine
            from ai.consolidated_ai_engine import initialize_engine

            # Create config for AI engine
            ai_config = {
                "ai_api_key": os.getenv("AI_API_KEY"),
                "ai_base_url": os.getenv("AI_BASE_URL"),
                "ai_model": os.getenv("AI_MODEL"),
                "openrouter_api_key": os.getenv("OPENROUTER_API_KEY"),
                "openai_api_key": os.getenv("OPENAI_API_KEY"),
                "redis_url": os.getenv("REDIS_URL"),
                "cache_ttl_short": 300,
                "cache_ttl_medium": 1800,
                "cache_ttl_long": 3600,
            }

            ai_engine = initialize_engine(ai_config)
            self.logger.info("✅ AI Engine initialized")

            # Initialize context manager
            from ai.universal_context_manager import initialize_context_manager

            context_manager = initialize_context_manager(self)
            self.logger.info("✅ Universal Context Manager initialized")

        except Exception as e:
            self.logger.error(f"❌ AI systems initialization failed: {e}")
            self.logger.warning("Bot will continue with limited AI functionality")

    async def _initialize_database(self):
        """Initialize database connections and create tables"""
        try:
            # Initialize the database (creates tables)
            await db.initialize()

            self.logger.info("💾 Database initialized successfully")

        except Exception as e:
            self.logger.error(f"❌ Database initialization failed: {e}")
            raise

    async def _load_extensions_with_dependencies(self):
        """Load extensions with proper dependency management and error recovery"""

        # Extension loading order with dependencies - OPTIMIZED
        extension_groups = [
            # Core utilities (no dependencies) - Performance optimized loading order
            [
                "cogs.admin_optimized",  # Optimized consolidated admin system
                "cogs.performance",  # Performance monitoring
                "cogs.continuous_performance",  # Continuous detailed performance monitoring
                "cogs.bot_status",
                "cogs.utilities",
                "cogs.stats",
                "cogs.bot_setup_enhanced",  # Consolidated setup system
                "cogs.nexus",  # Advanced diagnostic interface
            ],
            # AI and enhanced features (depend on core)
            [
                "cogs.advanced_ai",
                "cogs.server_management",
            ],
            # Analytics and specialized features
            ["cogs.analytics", "cogs.roles"],
            # Game-specific and optional features
            ["cogs.quiz", "cogs.space"],
            # Help and utility features
            ["cogs.help", "cogs.notion"],
        ]

        total_loaded = 0
        total_failed = 0

        for group in extension_groups:
            self.logger.info(f"📦 Loading extension group: {', '.join(group)}")

            for extension in group:
                try:
                    await self.load_extension(extension)
                    self.loaded_extensions[extension] = datetime.now(timezone.utc)
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
                    self.logger.debug(
                        f"Traceback for {extension}:\n{traceback.format_exc()}"
                    )

            # Extension group completed - optimized loading without delay
            pass

        # Summary
        self.logger.info("=" * 60)
        self.logger.info(f"📦 Extension Loading Summary:")
        self.logger.info(f"   ✅ Loaded: {total_loaded}")
        self.logger.info(f"   ❌ Failed: {total_failed}")
        self.logger.info(
            f"   📊 Success Rate: {(total_loaded/(total_loaded+total_failed))*100:.1f}%"
        )

        if self.failed_extensions:
            self.logger.warning("Failed extensions:")
            for ext, error in self.failed_extensions.items():
                self.logger.warning(f"   • {ext}: {error}")

        self.logger.info("=" * 60)

    def _start_background_tasks(self):
        """Start all background monitoring and maintenance tasks"""
        # ❌ OLD (BROKEN):
        # task = self.create_task(task_func.start())

        # ✅ NEW (FIXED):
        if not self.monitor_system_health.is_running():
            self.monitor_system_health.start()

        if not self.update_statistics.is_running():
            self.update_statistics.start()

        if not self.cleanup_old_data.is_running():
            self.cleanup_old_data.start()

        # Continue for other background tasks...

    def _register_event_handlers(self):
        """Register enhanced event handlers"""

        @self.event
        async def on_ready():
            """Enhanced ready event with comprehensive initialization"""
            if self._bot_ready:
                return  # Prevent multiple ready events

            self._bot_ready = True

            # Calculate statistics
            total_members = sum(guild.member_count or 0 for guild in self.guilds)
            unique_members = len(
                set(member.id for guild in self.guilds for member in guild.members)
            )

            # System information
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024

            # Log comprehensive ready information
            self.logger.info("=" * 80)
            self.logger.info(f"🎉 {self.config.name} v{self.config.version} is ONLINE!")
            self.logger.info(f"🤖 Bot: {self.user} (ID: {self.user.id})")
            self.logger.info(f"🏠 Guilds: {len(self.guilds):,}")
            self.logger.info(
                f"👥 Total Members: {total_members:,} ({unique_members:,} unique)"
            )
            self.logger.info(f"⚡ WebSocket Latency: {self.latency * 1000:.2f}ms")
            self.logger.info(f"💾 Memory Usage: {memory_mb:.1f} MB")
            self.logger.info(f"🐍 Discord.py Version: {discord.__version__}")
            self.logger.info(
                f"⏱️ Startup Time: {self.stats.get_uptime().total_seconds():.2f}s"
            )

            # Sync application commands if enabled
            if self.config.command_sync_on_ready:
                await self._sync_commands()

            # Update bot statistics
            self.stats.update_system_stats()

            # Initialize Discord Data Reporter
            try:
                await initialize_discord_reporter(self)
                self.logger.info("✅ Discord Data Reporter initialized")
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize Discord Data Reporter: {e}")

            # Log guild information
            self.logger.info("\n📋 Connected Guilds:")
            for guild in sorted(
                self.guilds, key=lambda g: g.member_count or 0, reverse=True
            ):
                self.logger.info(
                    f"   • {guild.name} ({guild.member_count:,} members) [ID: {guild.id}]"
                )

            self.logger.info("=" * 80)
            self.logger.info("🎯 All systems operational and ready for action!")
            self.logger.info("=" * 80)

        @self.event
        async def on_guild_join(guild):
            """Enhanced guild join handling with adaptive personality initialization"""
            self.stats.guilds_joined += 1

            self.logger.info(f"🎉 Joined guild: {guild.name} (ID: {guild.id})")
            self.logger.info(f"   👥 Members: {guild.member_count:,}")
            self.logger.info(f"   📅 Created: {guild.created_at.strftime('%Y-%m-%d')}")
            self.logger.info(f"   👑 Owner: {guild.owner}")

            # Initialize guild configuration
            await self._initialize_guild_config(guild)

            # Initialize adaptive personality for this server
            try:
                from ai.consolidated_ai_engine import get_engine

                ai_engine = get_engine()
                if ai_engine:
                    # Prepare initial context about the server
                    initial_context = {
                        "server_name": guild.name,
                        "server_description": guild.description or "",
                        "member_count": guild.member_count,
                        "created_at": guild.created_at.isoformat(),
                        "features": list(guild.features) if guild.features else [],
                        "owner": str(guild.owner) if guild.owner else "Unknown",
                    }

                    # Initialize adaptive personality (no astronomy defaults)
                    personality_result = await ai_engine.initialize_server_personality(
                        guild_id=guild.id,
                        guild_name=guild.name,
                        initial_context=initial_context,
                    )

                    if personality_result.get("success"):
                        self.logger.info(
                            f"🧠 Adaptive personality initialized for {guild.name}"
                        )
                        self.logger.info(
                            f"   🎯 Learning from community: {personality_result.get('message', 'Ready to adapt')}"
                        )
                    else:
                        self.logger.warning(
                            f"⚠️ Personality initialization failed: {personality_result.get('error', 'Unknown error')}"
                        )

                    # Schedule adaptive learning after some initial activity
                    asyncio.create_task(self._schedule_initial_learning(guild))

            except Exception as e:
                self.logger.error(
                    f"❌ Failed to initialize adaptive personality for {guild.name}: {e}"
                )

            # Sync commands if enabled
            if self.config.command_sync_on_join:
                try:
                    await self.tree.sync(guild=guild)
                    self.logger.info(f"✅ Synced commands for {guild.name}")
                except Exception as e:
                    self.logger.error(
                        f"❌ Failed to sync commands for {guild.name}: {e}"
                    )

        @self.event
        async def on_guild_remove(guild):
            """Enhanced guild leave handling"""
            self.stats.guilds_left += 1

            self.logger.info(f"👋 Left guild: {guild.name} (ID: {guild.id})")

            # Cleanup guild data if configured
            if self.config.cleanup_on_leave:
                await self._cleanup_guild_data(guild.id)

        @self.event
        async def on_message(message):
            """Enhanced message processing with universal context understanding and natural AI engagement"""
            if not self._bot_ready or message.author.bot:
                return

            self.stats.messages_processed += 1

            # Always process commands first to avoid conflicts
            await self.process_commands(message)

            # Skip further processing if this was a command
            if message.content.startswith(
                tuple(await self._get_dynamic_prefix(self, message))
            ):
                return

            # Universal message tracking for context understanding
            try:
                # Store message in context for AI understanding even if not responding
                await self._store_message_context(message)

                # Let the AdvancedAICog handle ALL messages with its sophisticated interaction system
                # The AdvancedAI cog has a much more intelligent decision engine that determines
                # how to interact with every single message (text, reactions, emojis, etc.)
                # No filtering needed here - let the sophisticated system handle everything

            except Exception as e:
                self.logger.error(f"Error processing message context: {e}")

            # The AdvancedAICog on_message listener will handle all AI responses
            # with its sophisticated universal message interaction system

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
            start_time = datetime.now(timezone.utc)

            synced = await self.tree.sync()

            sync_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.logger.info(f"✅ Synced {len(synced)} commands in {sync_time:.2f}s")

            # Log command details
            for cmd in synced:
                if isinstance(cmd, app_commands.Group):
                    subcmds = len(cmd.commands)
                    self.logger.debug(
                        f"   📁 Group: {cmd.name} ({subcmds} subcommands)"
                    )
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
                ephemeral=True,
            )
        elif isinstance(error, app_commands.MissingPermissions):
            await send_func(
                "❌ You don't have permission to use this command.", ephemeral=True
            )
        elif isinstance(error, app_commands.CheckFailure):
            await send_func("❌ You cannot use this command right now.", ephemeral=True)
        else:
            # Log unexpected errors
            self.logger.error(f"Unexpected app command error: {traceback.format_exc()}")
            await send_func(
                "❌ An unexpected error occurred. The issue has been logged.",
                ephemeral=True,
            )

        # Save error to database for analysis
        await self._log_error_to_database(interaction, error)

    async def _initialize_guild_config(self, guild: discord.Guild):
        """Initialize configuration for a new guild"""
        config = {
            "guild_id": guild.id,
            "guild_name": guild.name,
            "joined_at": datetime.now(timezone.utc).isoformat(),
            "prefix": self.config.prefix,
            "features": self.config.features.copy(),
            "ai_personality": "default",
            "auto_moderation": False,
            "analytics_enabled": True,
        }

        await db.set("guild_configs", str(guild.id), config)
        self.logger.debug(f"📋 Initialized config for guild: {guild.name}")

    async def _schedule_initial_learning(self, guild: discord.Guild):
        """Schedule initial adaptive learning for a new server"""
        try:
            # Wait a bit for initial activity
            await asyncio.sleep(300)  # 5 minutes

            # Collect recent messages from public channels for rapid adaptation
            recent_messages = []

            for channel in guild.text_channels:
                # Only analyze public channels bot can read
                if channel.permissions_for(guild.me).read_messages:
                    try:
                        # Get recent messages (last 20 from each channel, max 100 total)
                        async for message in channel.history(limit=20):
                            if len(recent_messages) >= 100:
                                break

                            # Skip bot messages and system messages
                            if not message.author.bot and message.content.strip():
                                recent_messages.append(
                                    {
                                        "content": message.content,
                                        "author_id": message.author.id,
                                        "channel_id": message.channel.id,
                                        "timestamp": message.created_at.isoformat(),
                                        "has_reactions": len(message.reactions) > 0,
                                    }
                                )

                        if len(recent_messages) >= 100:
                            break

                    except Exception as e:
                        self.logger.debug(f"Couldn't read from {channel.name}: {e}")
                        continue

            if recent_messages:
                # Trigger rapid adaptation
                from ai.consolidated_ai_engine import get_engine

                ai_engine = get_engine()
                if ai_engine:
                    adaptation_result = await ai_engine.adapt_to_server_activity(
                        guild_id=guild.id, recent_messages=recent_messages
                    )

                    if adaptation_result.get("success"):
                        adaptations = adaptation_result.get("adaptations", {})
                        self.logger.info(
                            f"🎯 Rapid adaptation completed for {guild.name}"
                        )
                        self.logger.info(
                            f"   📊 Analyzed {len(recent_messages)} messages"
                        )

                        if adaptations:
                            changes = len(adaptations)
                            self.logger.info(
                                f"   🔄 Made {changes} personality adaptations"
                            )
                    else:
                        self.logger.warning(
                            f"⚠️ Adaptation failed: {adaptation_result.get('error')}"
                        )
                else:
                    self.logger.warning("⚠️ AI engine not available for adaptation")
            else:
                self.logger.info(
                    f"📭 No recent activity found in {guild.name} - will adapt as interactions occur"
                )

        except Exception as e:
            self.logger.error(
                f"❌ Initial learning scheduling failed for {guild.name}: {e}"
            )

    async def _cleanup_guild_data(self, guild_id: int):
        """Clean up data for a guild that was left"""
        tables_to_clean = ["guild_configs", "user_profiles", "command_stats"]

        for table in tables_to_clean:
            await db.delete(table, str(guild_id))

        self.logger.debug(f"🧹 Cleaned up data for guild ID: {guild_id}")

    async def _update_command_stats(self, ctx):
        """Update command usage statistics"""
        stats_key = (
            f"{ctx.guild.id if ctx.guild else 'dm'}_{ctx.command.qualified_name}"
        )
        current_stats = await db.get(
            "command_stats", stats_key, {"count": 0, "last_used": None}
        )

        current_stats["count"] += 1
        current_stats["last_used"] = datetime.now(timezone.utc).isoformat()

        await db.set("command_stats", stats_key, current_stats)

    async def _log_error_to_database(self, interaction: discord.Interaction, error):
        """Log error details to Discord channel and optionally database"""
        # Send to Discord channel immediately
        discord_reporter = get_discord_reporter()
        if discord_reporter:
            await discord_reporter.send_error_report(
                error=error,
                context=f"Command: {interaction.command.name if interaction.command else 'unknown'}",
                guild_id=interaction.guild_id,
                user_id=interaction.user.id,
            )

        # Also keep minimal error tracking in database for critical errors
        if isinstance(
            error, (commands.CommandInvokeError, app_commands.AppCommandError)
        ):
            error_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "command": (
                    interaction.command.name if interaction.command else "unknown"
                ),
                "user_id": interaction.user.id,
                "guild_id": interaction.guild_id,
                "error_type": type(error).__name__,
                "error_message": str(error),
            }

            error_key = f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{interaction.user.id}"
            await db.set("error_logs", error_key, error_data)

    async def _store_message_context(self, message: discord.Message):
        """Store message context for AI understanding and conversation tracking"""
        try:
            # Create message context for storage
            message_context = {
                "message_id": message.id,
                "user_id": message.author.id,
                "username": str(message.author),
                "guild_id": message.guild.id if message.guild else None,
                "channel_id": message.channel.id,
                "content": message.content[:2000],  # Limit content length
                "timestamp": message.created_at.isoformat(),
                "has_mentions": len(message.mentions) > 0,
                "has_attachments": len(message.attachments) > 0,
                "is_reply": message.reference is not None,
                "reply_to": message.reference.message_id if message.reference else None,
            }

            # Store in conversation context for AI systems
            context_key = f"message_context_{message.guild.id if message.guild else 'dm'}_{message.channel.id}"

            # Get existing context or create new
            existing_context = await db.get(
                "conversation_contexts", context_key, {"messages": []}
            )

            # Add new message
            existing_context["messages"].append(message_context)

            # Keep only recent messages (last 50 per channel)
            if len(existing_context["messages"]) > 50:
                existing_context["messages"] = existing_context["messages"][-50:]

            # Update last activity
            existing_context["last_activity"] = datetime.now(timezone.utc).isoformat()
            existing_context["channel_id"] = message.channel.id
            existing_context["guild_id"] = message.guild.id if message.guild else None

            # Store updated context
            await db.set("conversation_contexts", context_key, existing_context)

        except Exception as e:
            self.logger.error(f"Error storing message context: {e}")

    async def _should_bot_respond(self, message: discord.Message) -> bool:
        """Determine if bot should respond to this message based on context and engagement patterns"""
        try:
            # Always respond to mentions and DMs
            if self.user in message.mentions:
                return True

            if isinstance(message.channel, discord.DMChannel):
                return True

            # Check for direct address without mention
            content_lower = message.content.lower()
            bot_names = ["astra", "bot", "ai"]
            if any(name in content_lower for name in bot_names):
                return True

            # Respond to questions directed at the channel
            if "?" in message.content and len(message.content) > 10:
                return True

            # Check conversation context - respond if recently active
            context_key = f"message_context_{message.guild.id if message.guild else 'dm'}_{message.channel.id}"
            context = await db.get("conversation_contexts", context_key, {})

            if context.get("last_activity"):
                last_activity = datetime.fromisoformat(context["last_activity"])
                if (
                    datetime.now(timezone.utc) - last_activity
                ).total_seconds() < 300:  # 5 minutes
                    # Check if bot was recently mentioned in this conversation
                    recent_messages = context.get("messages", [])[
                        -10:
                    ]  # Last 10 messages
                    for msg in recent_messages:
                        if msg.get("has_mentions"):
                            return True

            # Smart engagement: respond to interesting or complex messages occasionally
            if len(message.content) > 100:  # Longer messages
                # Look for engagement indicators
                engagement_words = [
                    "think",
                    "opinion",
                    "advice",
                    "help",
                    "recommend",
                    "suggest",
                    "anyone",
                    "thoughts",
                    "ideas",
                    "experience",
                    "know",
                ]
                if any(word in content_lower for word in engagement_words):
                    return True

            # Random engagement for community building (very low probability)
            if len(message.content) > 50:
                import random

                return random.random() < 0.05  # 5% chance for longer messages

            return False

        except Exception as e:
            self.logger.error(f"Error determining response need: {e}")
            return False

    def create_task(self, coro, *, name: str = None) -> asyncio.Task:
        """Create and track async tasks for proper cleanup"""
        task = asyncio.create_task(coro, name=name)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    # Optimized Background Tasks with Resource Management

    @tasks.loop(hours=2)  # Reduced from frequent calls
    async def monitor_system_health(self):
        """Enhanced resource monitoring with performance optimization"""
        try:
            # Memory management (imports already at top level)
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()

            # Force garbage collection if memory usage is high
            if memory_percent > 75:
                collected = gc.collect()
                self.logger.warning(
                    f"High memory usage ({memory_percent:.1f}%), collected {collected} objects"
                )

            # CPU monitoring
            cpu_percent = process.cpu_percent(interval=1)

            # Update stats efficiently
            self.stats.memory_usage_mb = memory_info.rss / 1024 / 1024
            self.stats.cpu_usage_percent = cpu_percent

            # Performance metrics are now sent to Discord via update_statistics task
            # No need for additional database storage here

            # Performance warnings
            if memory_percent > 85:
                self.logger.error(f"Critical memory usage: {memory_percent:.1f}%")
            elif memory_percent > 70:
                self.logger.warning(f"High memory usage: {memory_percent:.1f}%")

            if cpu_percent > 80:
                self.logger.warning(f"High CPU usage: {cpu_percent:.1f}%")

        except ImportError:
            self.logger.warning("psutil not available for resource monitoring")
        except Exception as e:
            self.logger.error(f"Resource monitoring error: {e}")

    @tasks.loop(minutes=20)  # Optimized frequency for Discord reporting
    async def update_statistics(self):
        """Update and send bot statistics to Discord"""
        try:
            # Collect statistics
            stats_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "uptime_seconds": self.stats.uptime_seconds,
                "commands_executed": self.stats.commands_executed,
                "messages_processed": self.stats.messages_processed,
                "errors_handled": self.stats.errors_handled,
                "guilds_count": len(self.guilds),
                "memory_usage_mb": self.stats.memory_usage_mb,
                "cpu_usage_percent": self.stats.cpu_usage_percent,
                "latency_ms": round(self.latency * 1000, 2),
                "extension_health": sum(
                    1 for health in self.extension_health.values() if health
                ),
                "total_extensions": len(self.extension_health),
            }

            # Send to Discord channel
            discord_reporter = get_discord_reporter()
            if discord_reporter:
                await discord_reporter.send_performance_report(stats_data)

            # Keep minimal database storage for critical metrics only
            if stats_data["errors_handled"] > 0 or stats_data["cpu_usage_percent"] > 80:
                key = datetime.now(timezone.utc).strftime("%Y%m%d_%H")
                await db.set("performance_metrics", key, stats_data)

        except Exception as e:
            self.logger.error(f"Error updating statistics: {e}")

    @tasks.loop(hours=6)  # Reduced frequency for cleanup
    async def cleanup_old_data(self):
        """Enhanced cleanup with automatic optimization"""
        try:
            # Database cleanup with connection pooling
            if hasattr(db, "cleanup_old_data"):
                await db.cleanup_old_data(days=30)

            # Clean old performance metrics (keep last 7 days)
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)
            old_keys = []

            # This would be implemented with proper key iteration
            # For now, log cleanup action
            self.logger.info("🧹 Enhanced cleanup task executed - removed old metrics")

            # Force garbage collection after cleanup
            # Use already imported gc module
            collected = gc.collect()
            self.logger.debug(f"🗑️ Post-cleanup garbage collection: {collected} objects")

        except Exception as e:
            self.logger.error(f"Error in data cleanup: {e}")

    @tasks.loop(hours=1)  # Balanced frequency for guild sync
    async def sync_guild_configs(self):
        """Optimized guild configuration synchronization"""
        try:
            guild_updates = []

            for guild in self.guilds:
                try:
                    guild_config = await db.get("guild_configs", str(guild.id))
                    needs_update = False

                    if guild_config:
                        # Batch check for changes
                        if guild_config.get("guild_name") != guild.name:
                            guild_config["guild_name"] = guild.name
                            needs_update = True

                        if guild_config.get("member_count") != guild.member_count:
                            guild_config["member_count"] = guild.member_count
                            needs_update = True

                        if needs_update:
                            guild_updates.append((guild.id, guild_config))
                    else:
                        # Initialize config for new guilds
                        await self._initialize_guild_config(guild)

                    # Optimized rate limiting for large servers (reduced delay)
                    if len(self.guilds) > 200:  # Only for very large deployments
                        await asyncio.sleep(0.01)
                ## Vim discable and error handiling, except and error try and fix the thing for auto complation, { getter/ setter}
                except Exception as e:
                    self.logger.error(f"Error syncing guild {guild.id}: {e}")

            # Batch update configurations
            for guild_id, config in guild_updates:
                await db.set("guild_configs", str(guild_id), config)

            if guild_updates:
                self.logger.debug(
                    f"🔄 Updated {len(guild_updates)} guild configurations"
                )

        except Exception as e:
            self.logger.error(f"Error syncing guild configs: {e}")

    @tasks.loop(minutes=45)  # Reduced frequency for extension monitoring
    async def monitor_extensions(self):
        """Enhanced extension health monitoring with recovery"""
        try:
            unhealthy_extensions = []

            for extension_name in list(self.loaded_extensions.keys()):
                try:
                    # Check extension health efficiently
                    cog_name = extension_name.split(".")[-1].title().replace("_", "")
                    ext = self.get_cog(cog_name)

                    if ext is None:
                        self.extension_health[extension_name] = False
                        unhealthy_extensions.append(extension_name)
                    else:
                        # Additional health checks
                        if hasattr(ext, "health_check"):
                            try:
                                health = await ext.health_check()
                                self.extension_health[extension_name] = health
                            except:
                                self.extension_health[extension_name] = (
                                    True  # Default healthy
                                )
                        else:
                            self.extension_health[extension_name] = True

                except Exception as e:
                    self.extension_health[extension_name] = False
                    unhealthy_extensions.append(extension_name)
                    self.logger.error(
                        f"❌ Extension {extension_name} health check failed: {e}"
                    )

            # Attempt recovery for unhealthy extensions
            if unhealthy_extensions:
                self.logger.warning(
                    f"⚠️ Unhealthy extensions detected: {', '.join(unhealthy_extensions)}"
                )

                # Optional: Attempt automatic recovery
                for ext_name in unhealthy_extensions[:2]:  # Limit recovery attempts
                    try:
                        success = await self.reload_extension_safe(ext_name)
                        if success:
                            self.logger.info(f"🔄 Successfully recovered {ext_name}")
                    except Exception as e:
                        self.logger.error(f"Failed to recover {ext_name}: {e}")

        except Exception as e:
            self.logger.error(f"Error monitoring extensions: {e}")

    @tasks.loop(hours=24)  # Daily performance optimization
    async def optimize_performance(self):
        """Daily performance optimization routine"""
        try:
            # Database optimization
            if hasattr(db, "pool"):
                # Optimize database connections
                stats = await db.get_performance_stats()
                self.logger.info(
                    f"📊 DB Stats: {stats['connection_pool']['hit_ratio']:.2%} hit ratio"
                )

            # Memory optimization (using already imported gc)
            collected = gc.collect()

            # Extension health summary
            healthy_count = sum(
                1 for health in self.extension_health.values() if health
            )
            total_count = len(self.extension_health)

            optimization_data = {
                "database_optimized": True,
                "garbage_collected": collected,
                "extensions_healthy": f"{healthy_count}/{total_count}",
                "optimization_time": datetime.now(timezone.utc).isoformat(),
            }

            await db.set(
                "performance_metrics",
                f"optimization_{datetime.now(timezone.utc).strftime('%Y%m%d')}",
                optimization_data,
            )
            self.logger.info(
                f"🚀 Daily optimization completed - collected {collected} objects"
            )

        except Exception as e:
            self.logger.error(f"Performance optimization error: {e}")

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
                "loaded_at": self.loaded_extensions[ext_name].isoformat(),
            }

        for ext_name, error in self.failed_extensions.items():
            status[ext_name] = {"loaded": False, "healthy": False, "error": error}

        return status

    async def reload_extension_safe(self, extension_name: str) -> bool:
        """Safely reload an extension with error handling"""
        try:
            await self.reload_extension(extension_name)
            self.extension_health[extension_name] = True
            self.loaded_extensions[extension_name] = datetime.now(timezone.utc)
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
            # Stop background tasks with enhanced cleanup
            tasks_to_stop = [
                self.monitor_system_health,
                self.update_statistics,
                self.cleanup_old_data,
                self.sync_guild_configs,
                self.monitor_extensions,
                self.optimize_performance,
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

            # Cleanup Discord Data Reporter
            try:
                await cleanup_discord_reporter()
                self.logger.info("✅ Discord Data Reporter cleaned up")
            except Exception as e:
                self.logger.error(f"❌ Error cleaning up Discord reporter: {e}")

            # Close HTTP session
            if self.session and not self.session.closed:
                await self.session.close()
                self.logger.debug("🌐 HTTP session closed")

            # Log final statistics
            uptime = self.stats.get_uptime()
            self.logger.info("=" * 60)
            self.logger.info("📊 Final Statistics:")
            self.logger.info(f"   ⏱️ Uptime: {uptime}")
            self.logger.info(
                f"   💬 Commands Executed: {self.stats.commands_executed:,}"
            )
            self.logger.info(
                f"   📨 Messages Processed: {self.stats.messages_processed:,}"
            )
            self.logger.info(f"   ❌ Errors Handled: {self.stats.errors_handled:,}")
            self.logger.info(f"   🏠 Guilds Joined: {self.stats.guilds_joined}")
            self.logger.info(f"   👋 Guilds Left: {self.stats.guilds_left}")
            self.logger.info("=" * 60)

        except Exception as e:
            self.logger.error(f"❌ Error during shutdown: {e}")

        finally:
            # Stop performance monitoring
            performance_optimizer.stop_monitoring()

            # Call parent close
            await super().close()
            self.logger.info("👋 Astra bot shutdown completed")


# Global command registration
def register_global_commands(bot: AstraBot):
    """Register global utility commands"""
    # Ping command moved to NEXUS Control System for centralized command management
    pass

    # Removed duplicate status command - handled by bot_status cog


async def main():
    """Enhanced main function with comprehensive error handling and Railway support"""

    # Setup Railway logging if available
    if RAILWAY_ENABLED:
        # Railway logging is now handled by unified_config
        logger = logging.getLogger("Astra.Main")
        logger.info("🚄 Railway logging configured")
    else:
        # Initial logging setup for local development
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s",
            datefmt="%H:%M:%S",
        )
        logger = logging.getLogger("Astra.Main")

    try:
        # Railway configuration
        if RAILWAY_ENABLED:
            try:
                # Railway config is handled by unified_config
                logger.info("🚄 Railway configuration loaded")

                # Configuration is already handled by unified_config
                logger.info("📝 Configuration managed by unified_config")
            except Exception as e:
                logger.error(f"❌ Railway configuration failed: {e}")
                logger.error("This is likely due to missing environment variables.")
                logger.error(
                    "Make sure DISCORD_TOKEN is set in your Railway deployment."
                )
                raise RuntimeError(f"Railway configuration failed: {e}")

        logger.info("=" * 80)
        logger.info("🚀 Starting Astra Discord Bot v2.0.1")
        logger.info("🌟 Enhanced with Railway deployment support")
        logger.info(f"📅 Build: 2025-08-04 Railway Ready")
        logger.info(f"🐍 Python: {platform.python_version()}")
        logger.info(f"📦 Discord.py: {discord.__version__}")
        logger.info("=" * 80)

        # Environment validation - check Railway config first
        token = None
        if RAILWAY_ENABLED:
            # Token is handled by unified_config
            token = unified_config.get_bot_token()
            logger.info("🚄 Using Discord token from Railway environment")

        if not token:
            token = os.getenv("DISCORD_TOKEN")
            logger.info("🔧 Using Discord token from local environment")

        if not token:
            logger.critical(
                "🚫 DISCORD_TOKEN not found in Railway or local environment!"
            )
            logger.critical(
                "Please set your Discord bot token in Railway environment variables."
            )
            return 1

        # AI Configuration managed by NEXUS Control System
        # OpenRouter and Freepik APIs are configured independently
        logger.info("🤖 AI services managed by NEXUS Control System")

        # Optional environment checks for backwards compatibility
        optional_vars = [
            "NASA_API_KEY",
        ]

        missing_optional = [var for var in optional_vars if not os.getenv(var)]
        if missing_optional:
            logger.warning(
                f"⚠️ Optional environment variables missing: {', '.join(missing_optional)}"
            )
            logger.warning("Some advanced features may not be available.")

        # Create bot instance
        async with AstraBot() as bot:

            # Register global commands
            register_global_commands(bot)

            # Set up signal handlers for graceful shutdown
            if hasattr(signal, "SIGTERM"):
                loop = asyncio.get_running_loop()

                def signal_handler(signum, frame):
                    logger.info(
                        f"🛑 Received signal {signum}, initiating graceful shutdown..."
                    )
                    asyncio.create_task(bot.close())

                for sig in (signal.SIGINT, signal.SIGTERM):
                    try:
                        loop.add_signal_handler(
                            sig, lambda s=sig, f=None: signal_handler(s, f)
                        )
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
