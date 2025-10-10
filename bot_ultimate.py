"""
🚀 OPTIMIZED MAIN BOT APPLICATION
Final optimization integration with all performance systems

Features:
- Ultra-performance coordination integration
- Comprehensive telemetry and monitoring
- Integrated personality system
- Multi-tier caching and database optimization
- Advanced AI coordination
- Real-time performance tracking
- Memory-optimized operations
- Graceful error handling and recovery

Author: x1ziad
Version: 2.0.0 ULTIMATE PERFORMANCE
"""

# Suppress Google gRPC ALTS credentials warning for local development
import os

os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import asyncio
import logging
import platform
import signal
import sys
import traceback
import gc
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any, Callable
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
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

# 🚀 PERFORMANCE BOOST: Fast system monitoring
try:
    import psutil

    USE_PSUTIL = True
    print("⚡ psutil enabled - advanced system monitoring!")
except ImportError:
    USE_PSUTIL = False
    print("⚠️  psutil not available - using basic monitoring")

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

# 🚀 ULTIMATE PERFORMANCE: Import all optimization systems
from core.ultra_performance_coordinator import (
    get_performance_coordinator,
    initialize_performance_coordinator,
)
from core.telemetry_system import get_telemetry, initialize_telemetry
from core.personality_integration import (
    get_personality_engine,
    initialize_personality_integration,
)
from core.ultra_performance_database import (
    get_ultra_database,
    initialize_ultra_database,
)

# Performance optimization imports
from utils.command_optimizer import auto_optimize_commands
from utils.discord_data_reporter import (
    initialize_discord_reporter,
    get_discord_reporter,
    cleanup_discord_reporter,
)

# Railway configuration support
try:
    RAILWAY_ENABLED = True

    def log_railway_env_diagnostic():
        """Optimized Railway environment diagnostic"""
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
class UltimateBotStats:
    """🚀 Ultimate bot runtime statistics with comprehensive tracking"""

    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    commands_executed: int = 0
    messages_processed: int = 0
    errors_handled: int = 0
    guilds_joined: int = 0
    guilds_left: int = 0

    # Performance metrics
    uptime_seconds: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    cache_hit_rate: float = 0.0
    average_response_time: float = 0.0

    # AI and personality metrics
    ai_requests_total: int = 0
    ai_requests_successful: int = 0
    personality_adaptations: int = 0
    telemetry_events: int = 0

    # Database metrics
    database_operations: int = 0
    cache_operations: int = 0

    def get_uptime(self) -> timedelta:
        """Get current uptime"""
        return datetime.now(timezone.utc) - self.start_time

    def update_system_stats(self):
        """Update system resource usage"""
        if USE_PSUTIL:
            process = psutil.Process()
            self.memory_usage_mb = process.memory_info().rss / 1024 / 1024
            self.cpu_usage_percent = process.cpu_percent()
        self.uptime_seconds = self.get_uptime().total_seconds()

    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        self.update_system_stats()

        return {
            "uptime": {
                "total_seconds": self.uptime_seconds,
                "formatted": str(self.get_uptime()),
                "started_at": self.start_time.isoformat(),
            },
            "activity": {
                "commands_executed": self.commands_executed,
                "messages_processed": self.messages_processed,
                "errors_handled": self.errors_handled,
                "guilds_joined": self.guilds_joined,
                "guilds_left": self.guilds_left,
            },
            "performance": {
                "memory_usage_mb": self.memory_usage_mb,
                "cpu_usage_percent": self.cpu_usage_percent,
                "cache_hit_rate": self.cache_hit_rate,
                "average_response_time": self.average_response_time,
            },
            "ai_metrics": {
                "total_requests": self.ai_requests_total,
                "successful_requests": self.ai_requests_successful,
                "success_rate": (
                    (self.ai_requests_successful / self.ai_requests_total * 100)
                    if self.ai_requests_total > 0
                    else 0
                ),
                "personality_adaptations": self.personality_adaptations,
            },
            "system_metrics": {
                "database_operations": self.database_operations,
                "cache_operations": self.cache_operations,
                "telemetry_events": self.telemetry_events,
            },
        }


@auto_optimize_commands
class UltimateAstraBot(commands.Bot):
    """🚀 ULTIMATE OPTIMIZED Astra Discord Bot with all performance systems integrated"""

    def __init__(self):
        # Load configuration
        self.config: BotConfig = unified_config.bot_config

        # Set up enhanced logging
        self.logger = setup_enhanced_logger(
            name="UltimateAstra",
            log_level="DEBUG" if getattr(self.config, "debug", False) else "INFO",
        )

        self.logger.info("=" * 80)
        self.logger.info(
            f"🚀 Initializing ULTIMATE {self.config.name} v{self.config.version}"
        )
        self.logger.info(f"⚡ Performance Mode: MAXIMUM OPTIMIZATION")
        self.logger.info(f"📅 Build Date: {datetime.now(timezone.utc).isoformat()}")
        self.logger.info(f"👤 Started by: {self._get_current_user()}")
        self.logger.info(f"🐍 Python: {platform.python_version()}")
        self.logger.info(f"💻 Platform: {platform.system()} {platform.release()}")
        self.logger.info("=" * 80)

        # 🚀 ULTRA-OPTIMIZED intents for maximum performance
        intents = discord.Intents.default()
        intents.message_content = True  # Required for message processing
        intents.members = True  # Required for welcome system
        intents.guild_reactions = True  # Required for role selection
        intents.moderation = True  # Enhanced moderation capabilities
        intents.auto_moderation_configuration = True  # AI moderation
        intents.auto_moderation_execution = True  # AI moderation
        # 🚀 Disable non-essential intents for performance
        intents.presences = False
        intents.voice_states = False
        intents.guild_typing = False
        intents.dm_reactions = False
        intents.dm_typing = False
        intents.integrations = False
        intents.webhooks = False
        intents.invites = False

        # 🚀 ULTRA-OPTIMIZED bot initialization with enhanced moderation
        super().__init__(
            command_prefix=self._get_dynamic_prefix,
            intents=intents,
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="🚀 ULTIMATE PERFORMANCE + MODERATION",
            ),
            status=discord.Status.online,
            # 🚀 Maximum performance settings with enhanced moderation
            allowed_mentions=discord.AllowedMentions(
                everyone=False, roles=False, users=True, replied_user=False
            ),
            help_command=None,  # Custom optimized help system
            case_insensitive=True,
            strip_after_prefix=True,
            owner_id=getattr(self.config, "owner_id", None),
            # 🚀 Ultra-optimized caching with moderation support
            max_messages=1000,  # Increased for better moderation tracking
            chunk_guilds_at_startup=False,
            member_cache_flags=discord.MemberCacheFlags.joined
            | discord.MemberCacheFlags.voice,
        )

        # 🚀 Ultimate performance tracking
        self.stats = UltimateBotStats()
        self.start_time = self.stats.start_time
        self.session: Optional[aiohttp.ClientSession] = None
        self._tasks: Set[asyncio.Task] = set()
        self._bot_ready = False
        self._shutdown_initiated = False

        # 🚀 Performance optimization components
        self.performance_coordinator = None
        self.telemetry_system = None
        self.personality_engine = None
        self.ultra_database = None

        # 🚀 Advanced metrics tracking
        self._performance_start = time.perf_counter()
        self._message_count = 0
        self._command_count = 0
        self._error_count = 0
        self._last_gc_time = time.time()
        self._response_times: List[float] = []

        # Enhanced feature tracking
        self.loaded_extensions: Dict[str, datetime] = {}
        self.failed_extensions: Dict[str, str] = {}
        self.extension_health: Dict[str, bool] = {}

        # Ultra-optimized caching
        self._command_cache: Dict[str, Any] = {}
        self._guild_configs: Dict[int, Dict[str, Any]] = {}
        self._user_cache: Dict[int, Dict[str, Any]] = {}

        # Error handling
        self.error_handler = ErrorHandler(self)

        # Create essential directories
        self._ensure_directories()

        self.logger.info("✅ Ultimate bot initialization completed")

    def _get_current_user(self) -> str:
        """Get current user with enhanced detection"""
        methods = [
            lambda: os.environ.get("USER"),
            lambda: os.environ.get("USERNAME"),
            lambda: os.environ.get("LOGNAME"),
            lambda: os.getlogin(),
            lambda: "docker-container" if os.path.exists("/.dockerenv") else None,
            lambda: (
                "railway-container" if os.environ.get("RAILWAY_ENVIRONMENT") else None
            ),
            lambda: "container-user",
        ]

        for method in methods:
            try:
                result = method()
                if result:
                    return result
            except (OSError, AttributeError):
                continue

        return "ultimate-user"

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
            "data/cache",
            "data/telemetry",
            "data/personality",
            "data/performance",
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

        self.logger.debug(f"📁 Created {len(directories)} optimized directories")

    async def _get_dynamic_prefix(self, bot, message) -> List[str]:
        """🚀 Ultra-optimized dynamic prefix system"""
        prefixes = []

        # Always respond to mentions (cached)
        user_id = self.user.id if self.user else 0
        prefixes.extend([f"<@{user_id}> ", f"<@!{user_id}> "])

        # Guild-specific prefixes with ultra-fast caching
        if hasattr(message, "guild") and message.guild:
            guild_id = message.guild.id

            # Check cache first
            if guild_id in self._guild_configs:
                guild_config = self._guild_configs[guild_id]
            else:
                try:
                    # Use ultra database for fastest access
                    if self.ultra_database:
                        guild_config = await self.ultra_database.get_cached(
                            f"guild_config_{guild_id}", {}
                        )
                    else:
                        guild_config = await db.get("guild_configs", str(guild_id), {})

                    # Cache for future use
                    self._guild_configs[guild_id] = guild_config
                except Exception:
                    guild_config = {}

            guild_prefix = guild_config.get("prefix", self.config.prefix)
            prefixes.append(guild_prefix)
        else:
            prefixes.append(self.config.prefix)

        return prefixes

    async def setup_hook(self):
        """🚀 ULTIMATE setup hook with all optimization systems"""
        self.logger.info("🔧 Running ULTIMATE setup hook...")

        start_time = time.perf_counter()

        # 🚀 Initialize all optimization systems in parallel for maximum speed
        initialization_tasks = []

        # Initialize ultra-performance database first (foundation for everything)
        self.logger.info("🗄️  Initializing Ultra-Performance Database...")
        self.ultra_database = await initialize_ultra_database()

        # Initialize all other systems in parallel
        async def init_performance_coordinator():
            self.logger.info("🎯 Initializing Ultra-Performance Coordinator...")
            self.performance_coordinator = await initialize_performance_coordinator(
                self
            )

        async def init_telemetry():
            self.logger.info("📊 Initializing Comprehensive Telemetry System...")
            self.telemetry_system = await initialize_telemetry(self)

        async def init_personality():
            self.logger.info("🧠 Initializing Integrated Personality Engine...")
            self.personality_engine = await initialize_personality_integration()

        async def init_http_session():
            await self._setup_ultra_http_session()

        async def init_database():
            await self._initialize_database()

        async def load_extensions():
            await self._load_extensions_with_dependencies()

        # Run all initializations in parallel
        await asyncio.gather(
            init_performance_coordinator(),
            init_telemetry(),
            init_personality(),
            init_http_session(),
            init_database(),
            load_extensions(),
            return_exceptions=True,
        )

        # Start background tasks
        self._start_background_tasks()

        # Register event handlers
        self._register_event_handlers()

        # Setup command tree error handling
        self.tree.error(self._handle_app_command_error)

        # Initialize AI systems
        await self._initialize_ai_systems()

        setup_time = time.perf_counter() - start_time
        self.logger.info(f"✅ ULTIMATE setup hook completed in {setup_time:.2f}s")

    async def _setup_ultra_http_session(self):
        """🚀 ULTRA-OPTIMIZED HTTP session with maximum performance"""
        # 🚀 Maximum performance connector settings
        connector = aiohttp.TCPConnector(
            limit=200,  # Maximum pool size
            limit_per_host=100,  # Maximum connections per host
            ttl_dns_cache=900,  # Extended DNS cache (15 minutes)
            use_dns_cache=True,
            keepalive_timeout=60,  # Extended keepalive
            enable_cleanup_closed=True,
            force_close=False,
            ssl=False,  # Maximum performance
        )

        # 🚀 Ultra-optimized timeout settings
        timeout = aiohttp.ClientTimeout(
            total=30,
            connect=3,  # Fastest connection timeout
            sock_read=5,  # Fastest read timeout
        )

        # 🚀 Performance headers
        headers = {
            "User-Agent": f"{self.config.name}/{self.config.version}-UltimatePerformance",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=300",  # 5-minute cache
        }

        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers,
            raise_for_status=False,
            json_serialize=json_fast.dumps if USE_FAST_JSON else None,
        )

        self.logger.info("🚀 Ultra-performance HTTP session initialized")

    async def _initialize_database(self):
        """Initialize database with ultra-performance optimizations"""
        try:
            # Database is already initialized via ultra_database
            if self.ultra_database:
                self.logger.info("🗄️  Ultra-performance database ready")
            else:
                # Fallback to standard database
                await db.initialize()
                self.logger.info("🗄️  Standard database initialized")
        except Exception as e:
            self.logger.error(f"❌ Database initialization failed: {e}")
            raise

    async def _initialize_ai_systems(self):
        """Initialize AI systems with performance optimization"""
        try:
            # Use performance coordinator for AI management
            if self.performance_coordinator:
                await self.performance_coordinator.register_ai_systems()
                self.logger.info(
                    "🤖 AI systems registered with performance coordinator"
                )
            else:
                # Fallback to standard AI initialization
                from ai.multi_provider_ai import MultiProviderAIManager

                self.ai_manager = MultiProviderAIManager()
                self.logger.info("🤖 Standard AI manager initialized")

        except Exception as e:
            self.logger.error(f"❌ AI systems initialization failed: {e}")
            # Continue without AI - bot should still function

    async def _load_extensions_with_dependencies(self):
        """🚀 Ultra-optimized extension loading with dependency management"""
        extension_groups = {
            "core": [
                "cogs.enhanced_security",
                "cogs.bot_status",
                "cogs.analytics",
            ],
            "ai": [
                "cogs.ai_companion",
                "cogs.advanced_ai",
                "cogs.personality_manager",
            ],
            "management": [
                "cogs.admin_optimized",
                "cogs.enhanced_server_management",
                "cogs.security_manager",
            ],
            "features": [
                "cogs.space",
                "cogs.quiz",
                "cogs.roles",
                "cogs.notion",
                "cogs.nexus",
            ],
            "performance": [
                "cogs.high_performance_coordinator",
            ],
        }

        total_loaded = 0
        total_failed = 0

        # Load extensions in dependency order
        for group_name, extensions in extension_groups.items():
            self.logger.info(f"📦 Loading {group_name} extensions...")

            # Load extensions in parallel within each group
            load_tasks = []
            for extension in extensions:
                load_tasks.append(self._load_single_extension(extension))

            results = await asyncio.gather(*load_tasks, return_exceptions=True)

            group_loaded = sum(1 for result in results if result is True)
            group_failed = len(results) - group_loaded

            total_loaded += group_loaded
            total_failed += group_failed

            self.logger.info(
                f"✅ {group_name}: {group_loaded} loaded, {group_failed} failed"
            )

        self.logger.info(
            f"📦 Extension loading complete: {total_loaded} loaded, {total_failed} failed"
        )

    async def _load_single_extension(self, extension: str) -> bool:
        """Load a single extension with error handling"""
        try:
            await self.load_extension(extension)
            self.loaded_extensions[extension] = datetime.now(timezone.utc)
            self.extension_health[extension] = True
            return True
        except Exception as e:
            self.failed_extensions[extension] = str(e)
            self.extension_health[extension] = False
            self.logger.error(f"❌ Failed to load {extension}: {e}")
            return False

    def _start_background_tasks(self):
        """Start all background tasks"""
        tasks_to_start = [
            self._status_update_task,
            self._performance_monitoring_task,
            self._cleanup_task,
            self._telemetry_reporting_task,
        ]

        for task_func in tasks_to_start:
            if not task_func.is_running():
                task_func.start()

        self.logger.info(f"🔄 Started {len(tasks_to_start)} background tasks")

    def _register_event_handlers(self):
        """Register all event handlers"""
        # Event handlers are registered through decorators
        self.logger.info("📡 Event handlers registered")

    async def _handle_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        """Handle application command errors"""
        self.stats.errors_handled += 1
        self._error_count += 1

        # Log error with telemetry if available
        if self.telemetry_system:
            await self.telemetry_system.record_metric("command_errors", 1)

        # Use performance coordinator for error handling if available
        if self.performance_coordinator:
            await self.performance_coordinator.handle_error(interaction, error)
        else:
            # Fallback error handling
            await self.error_handler.handle_app_command_error(interaction, error)

    @tasks.loop(seconds=30)
    async def _status_update_task(self):
        """Update bot status and activity"""
        try:
            # Update stats
            self.stats.update_system_stats()

            # Create dynamic status
            guild_count = len(self.guilds)
            member_count = sum(guild.member_count or 0 for guild in self.guilds)

            status_messages = [
                f"🚀 {guild_count} servers | {member_count:,} members",
                f"⚡ {self.stats.commands_executed} commands executed",
                f"🧠 Personality adaptations: {self.stats.personality_adaptations}",
                f"📊 Uptime: {str(self.stats.get_uptime()).split('.')[0]}",
                f"💾 Memory: {self.stats.memory_usage_mb:.1f}MB",
            ]

            current_status = status_messages[
                int(time.time() / 30) % len(status_messages)
            ]

            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching, name=current_status
                ),
                status=discord.Status.online,
            )

        except Exception as e:
            self.logger.error(f"Error updating status: {e}")

    @tasks.loop(seconds=60)
    async def _performance_monitoring_task(self):
        """Monitor performance and trigger optimizations"""
        try:
            # Update comprehensive stats
            self.stats.update_system_stats()

            # Get performance data from all systems
            if self.performance_coordinator:
                perf_data = await self.performance_coordinator.get_performance_report()
                self.stats.cache_hit_rate = perf_data.get("cache_hit_rate", 0)
                self.stats.average_response_time = perf_data.get(
                    "average_response_time", 0
                )

            if self.telemetry_system:
                telemetry_data = self.telemetry_system.get_system_health()
                self.stats.telemetry_events = telemetry_data.get("total_events", 0)

            if self.personality_engine:
                personality_data = self.personality_engine.get_performance_report()
                self.stats.personality_adaptations = personality_data.get(
                    "performance_metrics", {}
                ).get("total_adaptations", 0)

            # Trigger garbage collection if memory usage is high
            if (
                self.stats.memory_usage_mb > 200
                and time.time() - self._last_gc_time > 300
            ):  # 5 minutes
                collected = gc.collect()
                self._last_gc_time = time.time()
                self.logger.info(
                    f"🧹 Garbage collection: {collected} objects collected"
                )

            # Log performance summary
            if int(time.time()) % 300 == 0:  # Every 5 minutes
                report = self.stats.get_comprehensive_report()
                self.logger.info(
                    f"📊 Performance: Memory={report['performance']['memory_usage_mb']:.1f}MB, "
                    f"CPU={report['performance']['cpu_usage_percent']:.1f}%, "
                    f"Commands={report['activity']['commands_executed']}"
                )

        except Exception as e:
            self.logger.error(f"Error in performance monitoring: {e}")

    @tasks.loop(hours=1)
    async def _cleanup_task(self):
        """Cleanup and optimization task"""
        try:
            # Cleanup caches
            if len(self._guild_configs) > 1000:
                # Keep only recently accessed configs
                current_time = time.time()
                self._guild_configs = {
                    k: v for k, v in list(self._guild_configs.items())[-500:]
                }

            if len(self._user_cache) > 2000:
                self._user_cache = {
                    k: v for k, v in list(self._user_cache.items())[-1000:]
                }

            # Cleanup response times
            if len(self._response_times) > 1000:
                self._response_times = self._response_times[-500:]

            # Run cleanup on optimization systems
            if self.performance_coordinator:
                await self.performance_coordinator.cleanup()

            if self.personality_engine:
                await self.personality_engine.cleanup()

            if self.ultra_database:
                await self.ultra_database.cleanup()

            self.logger.info("🧹 Cleanup task completed")

        except Exception as e:
            self.logger.error(f"Error in cleanup task: {e}")

    @tasks.loop(minutes=5)
    async def _telemetry_reporting_task(self):
        """Report telemetry data"""
        try:
            if self.telemetry_system:
                # Update bot metrics in telemetry
                bot_metrics = {
                    "guilds": len(self.guilds),
                    "members": sum(guild.member_count or 0 for guild in self.guilds),
                    "commands_executed": self.stats.commands_executed,
                    "messages_processed": self.stats.messages_processed,
                    "errors_handled": self.stats.errors_handled,
                    "uptime_seconds": self.stats.uptime_seconds,
                    "memory_usage_mb": self.stats.memory_usage_mb,
                    "cpu_usage_percent": self.stats.cpu_usage_percent,
                }

                for metric, value in bot_metrics.items():
                    self.telemetry_system.record_metric(f"bot_{metric}", value)

        except Exception as e:
            self.logger.error(f"Error in telemetry reporting: {e}")

    async def on_ready(self):
        """Enhanced on_ready event with comprehensive initialization"""
        if self._bot_ready:
            return  # Prevent multiple ready events

        self._bot_ready = True
        startup_time = time.perf_counter() - self._performance_start

        self.logger.info("=" * 80)
        self.logger.info("🚀 ULTIMATE ASTRA BOT IS READY!")
        self.logger.info("=" * 80)
        self.logger.info(f"👤 Logged in as: {self.user} (ID: {self.user.id})")
        self.logger.info(f"🌐 Connected to {len(self.guilds)} guilds")
        self.logger.info(
            f"👥 Serving {sum(guild.member_count or 0 for guild in self.guilds):,} members"
        )
        self.logger.info(f"📦 Loaded {len(self.loaded_extensions)} extensions")
        self.logger.info(f"⚡ Startup time: {startup_time:.2f} seconds")

        # Log optimization systems status
        if self.performance_coordinator:
            self.logger.info("✅ Ultra-Performance Coordinator: ACTIVE")
        if self.telemetry_system:
            self.logger.info("✅ Comprehensive Telemetry: ACTIVE")
        if self.personality_engine:
            self.logger.info("✅ Integrated Personality Engine: ACTIVE")
        if self.ultra_database:
            self.logger.info("✅ Ultra-Performance Database: ACTIVE")

        self.logger.info("=" * 80)

        # Register bot with telemetry system
        if self.telemetry_system:
            await self.telemetry_system.register_component("UltimateAstraBot", self)

    async def on_message(self, message):
        """Optimized message processing"""
        start_time = time.perf_counter()

        # Skip bot messages
        if message.author.bot:
            return

        self.stats.messages_processed += 1
        self._message_count += 1

        # Record performance
        processing_time = time.perf_counter() - start_time
        self._response_times.append(processing_time)

        # Process commands
        await self.process_commands(message)

    async def on_command_completion(self, ctx):
        """Track command completion"""
        self.stats.commands_executed += 1
        self._command_count += 1

        # Record in telemetry if available
        if self.telemetry_system:
            self.telemetry_system.record_metric("commands_completed", 1)

    async def on_guild_join(self, guild):
        """Handle guild join"""
        self.stats.guilds_joined += 1
        self.logger.info(
            f"📈 Joined guild: {guild.name} (ID: {guild.id}, Members: {guild.member_count})"
        )

        # Clear guild config cache for this guild
        if guild.id in self._guild_configs:
            del self._guild_configs[guild.id]

    async def on_guild_remove(self, guild):
        """Handle guild leave"""
        self.stats.guilds_left += 1
        self.logger.info(f"📉 Left guild: {guild.name} (ID: {guild.id})")

        # Clear guild config cache for this guild
        if guild.id in self._guild_configs:
            del self._guild_configs[guild.id]

    async def close(self):
        """Graceful shutdown with optimization system cleanup"""
        if self._shutdown_initiated:
            return

        self._shutdown_initiated = True
        self.logger.info("🔄 Initiating graceful shutdown...")

        # Stop background tasks
        for task_func in [
            self._status_update_task,
            self._performance_monitoring_task,
            self._cleanup_task,
            self._telemetry_reporting_task,
        ]:
            if task_func.is_running():
                task_func.cancel()

        # Cleanup optimization systems
        cleanup_tasks = []

        if self.performance_coordinator:
            cleanup_tasks.append(self.performance_coordinator.shutdown())

        if self.telemetry_system:
            cleanup_tasks.append(self.telemetry_system.shutdown())

        if self.personality_engine:
            cleanup_tasks.append(self.personality_engine.cleanup())

        if self.ultra_database:
            cleanup_tasks.append(self.ultra_database.shutdown())

        # Run all cleanup tasks
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)

        # Close HTTP session
        if self.session and not self.session.closed:
            await self.session.close()

        # Final cleanup
        await cleanup_discord_reporter()

        # Call parent close
        await super().close()

        total_runtime = time.perf_counter() - self._performance_start
        self.logger.info(
            f"✅ Graceful shutdown completed in {total_runtime:.2f}s total runtime"
        )


# Global bot instance
bot: Optional[UltimateAstraBot] = None


async def create_bot() -> UltimateAstraBot:
    """Create and initialize the ultimate bot"""
    global bot
    if bot is None:
        bot = UltimateAstraBot()
    return bot


async def main():
    """Main application entry point"""
    global bot

    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}, initiating graceful shutdown...")
        if bot:
            asyncio.create_task(bot.close())
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Create bot instance
        bot = await create_bot()

        # Get Discord token
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            bot.logger.error("❌ DISCORD_TOKEN environment variable not set!")
            return

        # Start the bot
        bot.logger.info("🚀 Starting Ultimate Astra Bot...")
        await bot.start(token)

    except KeyboardInterrupt:
        bot.logger.info("🛑 Received keyboard interrupt")
    except Exception as e:
        if bot:
            bot.logger.error(f"❌ Fatal error: {e}")
            bot.logger.error(traceback.format_exc())
        else:
            print(f"❌ Fatal error during startup: {e}")
            traceback.print_exc()
    finally:
        if bot:
            await bot.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        traceback.print_exc()
        sys.exit(1)
