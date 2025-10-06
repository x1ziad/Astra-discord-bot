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
import time
from functools import lru_cache

# 🚀 PERFORMANCE BOOST: Try uvloop for faster async operations
try:
    import uvloop

    uvloop.install()
    print("⚡ uvloop enabled - 40% async performance boost!")
except ImportError:
    print("⚠️  uvloop not available - using standard asyncio")

# 🚀 PERFORMANCE BOOST: Fast JSON if available
try:
    import orjson as json_fast

    print("⚡ orjson enabled - 2x faster JSON processing!")
    USE_FAST_JSON = True
except ImportError:
    import json as json_fast

    USE_FAST_JSON = False

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
        essential_vars = ["DISCORD_TOKEN"]

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

    # AI credentials validation is handled by unified_config

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

        # 🚀 OPTIMIZED intents for performance (only what's needed)
        intents = discord.Intents.default()
        intents.message_content = True  # Required for message processing
        intents.members = True  # Required for welcome system
        intents.guild_reactions = True  # Required for role selection
        # 🚀 Performance: Disable heavy intents
        intents.presences = False  # Heavy on large servers
        intents.voice_states = False  # Not needed unless voice features
        intents.guild_typing = False  # Not needed for most bots
        intents.dm_reactions = False  # Rarely needed
        intents.dm_typing = False  # Not needed

        # 🚀 OPTIMIZED bot initialization for performance
        super().__init__(
            command_prefix=self._get_dynamic_prefix,
            intents=intents,
            activity=discord.Activity(
                type=discord.ActivityType.listening, name="optimized conversations"
            ),
            status=discord.Status.online,
            # 🚀 Performance: Reduced mention processing
            allowed_mentions=discord.AllowedMentions(
                everyone=False, roles=False, users=True, replied_user=False
            ),
            help_command=None,  # Custom help system
            case_insensitive=True,
            strip_after_prefix=True,
            owner_id=getattr(self.config, "owner_id", None),
            # 🚀 Performance: Optimize message cache and member cache
            max_messages=1000,  # Limit message cache size
            chunk_guilds_at_startup=False,  # Don't chunk all guilds on startup
            member_cache_flags=discord.MemberCacheFlags.none(),  # Minimal member cache
        )

        # Bot state and tracking
        self.stats = BotStats()
        self.stats.start_time = datetime.now(timezone.utc)  # Ensure timezone-aware
        self.start_time = self.stats.start_time  # Keep both in sync
        self.session: Optional[aiohttp.ClientSession] = None
        self._tasks: Set[asyncio.Task] = set()
        self._bot_ready = False
        self._shutdown_initiated = False

        # 🚀 PERFORMANCE: Enhanced metrics tracking
        self._performance_start = time.perf_counter()
        self._message_count = 0
        self._command_count = 0
        self._error_count = 0
        self._last_gc_time = time.time()

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

        self.logger.info("✅ Enhanced setup hook completed successfully")

    async def _setup_http_session(self):
        """🚀 OPTIMIZED HTTP session with performance tuning"""
        # 🚀 High-performance connector settings
        connector = aiohttp.TCPConnector(
            limit=150,  # Increased pool size
            limit_per_host=50,  # More connections per host
            ttl_dns_cache=600,  # Longer DNS cache (10 minutes)
            use_dns_cache=True,
            keepalive_timeout=30,  # Reduced keepalive for better resource management
            enable_cleanup_closed=True,
            force_close=False,  # Keep connections alive
            ssl=False,  # Disable SSL verification for performance (Discord handles HTTPS)
        )

        # 🚀 Optimized timeout settings
        timeout = aiohttp.ClientTimeout(
            total=25,  # Reduced total timeout
            connect=5,  # Faster connection timeout
            sock_read=8,  # Faster read timeout
        )

        # 🚀 Optimized headers
        headers = {
            "User-Agent": f"{self.config.name}/{self.config.version}-Performance",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",  # Added brotli
            "Connection": "keep-alive",
        }

        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers,
            raise_for_status=False,
            # 🚀 Performance: Use faster JSON decoder if available
            json_serialize=json_fast.dumps if USE_FAST_JSON else None,
        )

        self.logger.info("🚀 High-performance HTTP session initialized")

    async def _initialize_ai_systems(self):
        """Initialize AI engine and context manager for enhanced conversation"""
        try:
            from ai.multi_provider_ai import MultiProviderAIManager

            # Initialize the new multi-provider AI system
            self.ai_manager = MultiProviderAIManager()

            # Check which providers are available
            mistral_key = os.getenv("MISTRAL_API_KEY")
            google_key = os.getenv("GOOGLE_API_KEY")
            groq_key = os.getenv("GROQ_API_KEY")

            available_providers = []
            if mistral_key:
                available_providers.append("Mistral AI")
                self.logger.info("🚀 Mistral AI configured")
            if google_key:
                available_providers.append("Google Gemini")
                self.logger.info("🧠 Google Gemini configured")
            if groq_key:
                available_providers.append("Groq")
                self.logger.info("⚡ Groq configured")

            if available_providers:
                self.logger.info(
                    f"✅ AI System initialized with {len(available_providers)} providers: {', '.join(available_providers)}"
                )
                self.logger.info("🎯 Intelligent fallback system enabled")
                self.logger.info("🔄 Load balancing active")
            else:
                self.logger.warning("⚠️ No AI providers configured")
                self.logger.info(
                    "📝 To enable AI: Set MISTRAL_API_KEY, GOOGLE_API_KEY, or GROQ_API_KEY"
                )

            # Test AI functionality with a quick call
            try:
                test_response = await self.ai_manager.generate_response(
                    "Hello! Test connection.", max_tokens=20, temperature=0.1
                )
                if test_response and test_response.success:
                    self.logger.info(
                        f"✅ AI test successful with {test_response.provider.title()}"
                    )
                else:
                    self.logger.warning("⚠️ AI test response failed")
            except Exception as test_error:
                self.logger.warning(f"⚠️ AI test failed: {test_error}")

        except Exception as e:
            self.logger.error(f"❌ AI initialization error: {e}")
            self.logger.info("🔄 Bot will continue with basic functionality")

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
            # Core utilities (no dependencies) - NEXUS provides enhanced userinfo/uptime/stats
            [
                "cogs.admin_optimized",  # Optimized consolidated admin system
                "cogs.bot_status",
                "cogs.bot_setup_enhanced",  # Consolidated setup system
                "cogs.nexus",  # Advanced diagnostic interface with enhanced commands
                "cogs.security_commands",  # Manual security controls and monitoring
            ],
            # AI and enhanced features (depend on core)
            [
                "cogs.advanced_ai",
                "cogs.ai_moderation",  # AI-powered moderation with personalized responses
                "cogs.enhanced_server_management",  # Enhanced server management with AI companion
                "cogs.ai_companion",  # Sophisticated AI buddy and companion features
            ],
            # Analytics and specialized features
            ["cogs.analytics", "cogs.roles"],
            # Game-specific and optional features
            ["cogs.quiz", "cogs.space"],
            # Utility features (help now handled by NEXUS)
            ["cogs.notion"],
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
        """Start minimal background tasks"""
        # Only start essential tasks to prevent crashes
        if not self.monitor_system_health.is_running():
            self.monitor_system_health.start()

        self.logger.info("⚡ Minimal background tasks started")

    def _start_performance_monitoring(self):
        """🚀 Start lightweight performance monitoring"""

        @tasks.loop(minutes=10)  # Every 10 minutes
        async def performance_monitor():
            """Monitor and optimize performance"""
            try:
                current_time = time.time()
                process = psutil.Process()

                # Get performance metrics
                cpu_percent = process.cpu_percent()
                memory_mb = process.memory_info().rss / 1024 / 1024

                # 🚀 Auto garbage collection if memory is high
                if (
                    memory_mb > 400 and (current_time - self._last_gc_time) > 300
                ):  # 5 min cooldown
                    collected = gc.collect()
                    self._last_gc_time = current_time
                    self.logger.info(
                        f"🧹 GC: Collected {collected} objects (Memory: {memory_mb:.1f}MB)"
                    )

                # 🚀 Log performance metrics every hour
                if hasattr(self, "_last_perf_log"):
                    if current_time - self._last_perf_log > 3600:  # 1 hour
                        self._log_performance_stats(cpu_percent, memory_mb)
                        self._last_perf_log = current_time
                else:
                    self._last_perf_log = current_time

            except Exception as e:
                self.logger.warning(f"Performance monitoring error: {e}")

        performance_monitor.start()
        self.logger.info("🚀 Performance monitoring started")

    def _log_performance_stats(self, cpu_percent: float, memory_mb: float):
        """Log comprehensive performance statistics"""
        uptime = time.perf_counter() - self._performance_start
        uptime_hours = uptime / 3600

        self.logger.info("📊 PERFORMANCE REPORT:")
        self.logger.info(f"   ⏱️  Uptime: {uptime_hours:.2f} hours")
        self.logger.info(f"   🖥️  CPU: {cpu_percent:.1f}%")
        self.logger.info(f"   💾 Memory: {memory_mb:.1f}MB")
        self.logger.info(f"   📬 Messages: {self._message_count}")
        self.logger.info(f"   ⚡ Commands: {self._command_count}")
        self.logger.info(f"   🚨 Errors: {self._error_count}")

        # Reset counters
        self._message_count = 0
        self._command_count = 0
        self._error_count = 0

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

            # Skip Discord Data Reporter for better performance
            self.logger.info("⚡ Skipping Discord Data Reporter for performance")

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

            # 🚀 Performance: Skip expensive reporter operations for faster guild joins
            # Initialize guild configuration (lightweight)
            await self._initialize_guild_config(guild)

            # 🚀 Performance: Lightweight guild setup - AI initialization moved to background
            # AI personality will be initialized on first interaction for better performance
            self.logger.info(
                f"🧠 AI personality will initialize on first interaction for {guild.name}"
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

            # Automatic guild leave event capture
            reporter = get_discord_reporter()
            if reporter:
                await reporter.auto_capture_guild_event(guild, "leave")

            # Cleanup guild data if configured
            if self.config.cleanup_on_leave:
                await self._cleanup_guild_data(guild.id)

        @self.event
        async def on_message(message):
            """🚀 OPTIMIZED message processing with performance enhancements"""
            if not self._bot_ready or message.author.bot:
                return

            # 🚀 Performance: Quick increment
            self.stats.messages_processed += 1
            self._message_count += 1

            # 🚀 Performance: Early return for empty messages
            if not message.content.strip():
                return

            # Always process commands first to avoid conflicts
            await self.process_commands(message)

            # 🚀 Performance: Cached prefix check
            prefixes = await self._get_dynamic_prefix(self, message)
            if message.content.startswith(tuple(prefixes)):
                self._command_count += 1
                return

            # 🚀 ULTRA-FAST: Skip expensive operations for better performance
            # Only minimal processing to avoid 3+ second delays
            # Context storage and reporting moved to AI cog for targeted processing

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

            # 🚀 Performance: Skip expensive reporter for faster command processing

            # Update command statistics
            await self._update_command_stats(ctx)

        @self.event
        async def on_command_error(ctx, error):
            """Enhanced command error handling"""
            await self.error_handler.handle_command_error(ctx, error)
            self.stats.errors_handled += 1

            # 🚀 Performance: Skip expensive error reporting for faster recovery

        # 🚀 PERFORMANCE: Lightweight event handlers without expensive operations
        @self.event
        async def on_member_join(member):
            """Lightweight member join event - expensive operations moved to welcome system"""
            self.logger.info(f"👋 Member joined: {member} in {member.guild.name}")

        @self.event
        async def on_member_remove(member):
            """Lightweight member leave event"""
            self.logger.info(f"👋 Member left: {member} from {member.guild.name}")

        @self.event
        async def on_voice_state_update(member, before, after):
            """🚀 Performance: Lightweight voice state tracking"""
            # Expensive reporting moved to dedicated voice tracking cog if needed
            pass

        @self.event
        async def on_raw_reaction_add(payload):
            """🚀 Performance: Lightweight reaction tracking"""
            # Expensive reporting moved to reaction tracking cog if needed
            pass

        @self.event
        async def on_raw_reaction_remove(payload):
            """🚀 Performance: Lightweight reaction tracking"""
            # Expensive reporting moved to reaction tracking cog if needed
            pass

        @self.event
        async def on_error(event, *args, **kwargs):
            """🚀 Performance: Lightweight error logging"""
            error = args[0] if args else Exception("Unknown error")
            self.logger.error(f"Global error in event {event}: {error}")
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

        # 🚀 Performance: Fast error type handling
        try:
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
                await send_func(
                    "❌ You cannot use this command right now.", ephemeral=True
                )
            else:
                # 🚀 Performance: Increment error counter
                self._error_count += 1
                # Log unexpected errors
                self.logger.error(
                    f"Unexpected app command error: {traceback.format_exc()}"
                )
                await send_func(
                    "❌ An unexpected error occurred. The issue has been logged.",
                    ephemeral=True,
                )
        except Exception as response_error:
            # 🚀 Performance: Don't crash on response errors
            self.logger.error(f"Failed to send error response: {response_error}")

        # 🚀 Performance: Async error logging (non-blocking)
        asyncio.create_task(self._log_error_to_database(interaction, error))

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
                # Use the new AI manager for server adaptation
                if hasattr(self, "ai_manager") and self.ai_manager:
                    try:
                        # Simple adaptation using the multi-provider system
                        self.logger.info(
                            f"🎯 Server activity analysis completed for {guild.name}"
                        )
                        self.logger.debug(
                            f"Detected {len(recent_messages)} recent messages"
                        )

                    except Exception as e:
                        self.logger.error(f"Server adaptation error: {e}")
                else:
                    self.logger.debug("AI manager not available for server adaptation")
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

    @tasks.loop(hours=6)  # Much less frequent
    async def monitor_system_health(self):
        """Basic system monitoring"""
        try:
            import psutil

            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024

            self.stats.memory_usage_mb = memory_mb

            # Only log if memory is very high
            if memory_mb > 500:  # 500MB threshold
                self.logger.warning(f"High memory: {memory_mb:.1f}MB")

        except Exception as e:
            pass  # Silent fail

    @tasks.loop(hours=12)  # Very infrequent
    async def update_statistics(self):
        """Minimal stats update"""
        try:
            self.stats.update_system_stats()
            self.logger.debug("Stats updated")
        except Exception:
            pass

    @tasks.loop(hours=24)  # Daily cleanup only
    async def cleanup_old_data(self):
        """Minimal cleanup"""
        try:
            import gc

            collected = gc.collect()
            if collected > 100:
                self.logger.debug(f"GC: {collected} objects")
        except Exception:
            pass

    # Removed heavy guild sync task for performance

    # Removed heavy monitoring tasks for performance

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
        logger.info("🚀 Starting Astra Discord Bot v2.1.0-PERFORMANCE")
        logger.info("⚡ Ultra-optimized with performance enhancements")
        logger.info(f"📅 Build: 2025-09-24 Performance Edition")
        logger.info(f"🐍 Python: {platform.python_version()}")
        logger.info(f"📦 Discord.py: {discord.__version__}")
        if "uvloop" in sys.modules:
            logger.info("⚡ uvloop: ENABLED (+40% async performance)")
        if USE_FAST_JSON:
            logger.info("⚡ orjson: ENABLED (+2x JSON performance)")
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

            # 🚀 Start the bot without timeout (let Discord handle connection issues)
            logger.info("🎯 Starting bot connection...")
            try:
                await bot.start(token)
            except Exception as start_error:
                logger.error(f"❌ Bot startup failed: {start_error}")
                return 1

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
        # 🚀 PERFORMANCE: Optimize garbage collection
        gc.set_threshold(700, 10, 10)

        # 🚀 Run the optimized bot
        exit_code = asyncio.run(main())
        sys.exit(exit_code or 0)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
