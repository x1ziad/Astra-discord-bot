"""
Unified Configuration Manager for Astra Bot
Consolidates all configuration management into a single, optimized system
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, asdict, field
from pathlib import Path
import discord
from datetime import datetime

# Load environment variables early
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger("astra.unified_config")


@dataclass
class AIProviderConfig:
    """Configuration for AI providers"""

    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.7
    provider_name: Optional[str] = None
    use_concise_prompts: bool = True  # Optimized for faster responses


@dataclass
class BotConfig:
    """Bot configuration dataclass"""

    name: str = "Astra"
    version: str = "2.0.0"
    description: str = "Advanced AI-powered Discord bot"
    prefix: str = "!"
    status: str = "online"
    activity_type: str = "watching"
    activity_name: str = "the cosmos"
    owner_id: Optional[int] = None

    # Command sync settings
    command_sync_on_ready: bool = True
    command_sync_on_join: bool = False

    # Server management settings
    cleanup_on_leave: bool = True

    # Bot features
    features: Dict[str, bool] = field(
        default_factory=lambda: {
            "enable_ai": True,
            "enable_voice": False,
            "enable_moderation": True,
            "enable_analytics": True,
            "enable_auto_responses": True,
            "enable_slash_commands": True,
        }
    )


@dataclass
class DatabaseConfig:
    """Database configuration"""

    path: str = "data/astra.db"
    backup_enabled: bool = True
    backup_interval: int = 3600  # 1 hour
    connection_pool_size: int = 10


@dataclass
class CacheConfig:
    """Cache configuration"""

    enabled: bool = True
    default_ttl: int = 300
    max_size: int = 10000
    redis_enabled: bool = False
    redis_url: Optional[str] = None


@dataclass
class LoggingConfig:
    """Logging configuration"""

    level: str = "INFO"
    file_enabled: bool = True
    file_path: str = "logs/astra.log"
    console_enabled: bool = True
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5


class UnifiedConfigManager:
    """Unified configuration manager with all features consolidated"""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = Path(config_file or "config/config.json")
        self.config_dir = self.config_file.parent
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Initialize configs
        self.bot_config = BotConfig()
        self.ai_config = AIProviderConfig()
        self.db_config = DatabaseConfig()
        self.cache_config = CacheConfig()
        self.logging_config = LoggingConfig()

        # Guild-specific configs
        self.guild_configs: Dict[int, Dict[str, Any]] = {}

        # Load configuration
        self._load_config()
        self._load_environment_variables()

        # Railway deployment support
        self._setup_railway_config()

    def _load_config(self):
        """Load configuration from JSON file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    data = json.load(f)

                # Load bot config
                if "bot" in data:
                    bot_data = data["bot"]
                    self.bot_config = BotConfig(
                        **{
                            k: v
                            for k, v in bot_data.items()
                            if k in BotConfig.__dataclass_fields__
                        }
                    )

                # Load AI config
                if "ai" in data:
                    ai_data = data["ai"]
                    self.ai_config = AIProviderConfig(
                        **{
                            k: v
                            for k, v in ai_data.items()
                            if k in AIProviderConfig.__dataclass_fields__
                        }
                    )

                # Load other configs
                if "database" in data:
                    db_data = data["database"]
                    self.db_config = DatabaseConfig(
                        **{
                            k: v
                            for k, v in db_data.items()
                            if k in DatabaseConfig.__dataclass_fields__
                        }
                    )

                if "cache" in data:
                    cache_data = data["cache"]
                    self.cache_config = CacheConfig(
                        **{
                            k: v
                            for k, v in cache_data.items()
                            if k in CacheConfig.__dataclass_fields__
                        }
                    )

                if "logging" in data:
                    log_data = data["logging"]
                    self.logging_config = LoggingConfig(
                        **{
                            k: v
                            for k, v in log_data.items()
                            if k in LoggingConfig.__dataclass_fields__
                        }
                    )

                # Load guild configs
                if "guilds" in data:
                    self.guild_configs = data["guilds"]

        except Exception as e:
            logger.error(f"Error loading config: {e}")

    def _load_environment_variables(self):
        """Load configuration from environment variables"""
        # Bot token
        if token := os.getenv("DISCORD_TOKEN"):
            self.bot_token = token

        # Bot owner ID - with explicit fallback
        if owner_id := os.getenv("OWNER_ID"):
            try:
                self.bot_config.owner_id = int(owner_id)
                logger.info(
                    f"✅ Owner ID loaded from environment: {self.bot_config.owner_id}"
                )
            except ValueError:
                logger.warning(f"Invalid OWNER_ID value: {owner_id}")

        # Explicit fallback - if no owner ID set, use the known owner
        if self.bot_config.owner_id is None:
            self.bot_config.owner_id = 1115739214148026469
            logger.info(f"✅ Owner ID set to default: {self.bot_config.owner_id}")

        # AI configuration
        if api_key := os.getenv("AI_API_KEY", os.getenv("OPENROUTER_API_KEY")):
            self.ai_config.api_key = api_key

        if model := os.getenv("AI_MODEL"):
            self.ai_config.model = model

        if base_url := os.getenv("AI_BASE_URL"):
            self.ai_config.base_url = base_url

        # Database
        if db_path := os.getenv("DATABASE_PATH"):
            self.db_config.path = db_path

        # Cache
        if redis_url := os.getenv("REDIS_URL"):
            self.cache_config.redis_url = redis_url
            self.cache_config.redis_enabled = True

        # Logging
        if log_level := os.getenv("LOG_LEVEL"):
            self.logging_config.level = log_level

    def _setup_railway_config(self):
        """Setup Railway-specific configuration"""
        if os.getenv("RAILWAY_ENVIRONMENT"):
            # Railway deployment detected
            self.bot_config.name = "Astra (Railway)"

            # Use Railway's provided port if available
            if port := os.getenv("PORT"):
                self.port = int(port)

            # Enable production logging
            self.logging_config.level = "INFO"
            self.logging_config.console_enabled = True

    def save_config(self):
        """Save current configuration to file"""
        try:
            config_data = {
                "bot": asdict(self.bot_config),
                "ai": asdict(self.ai_config),
                "database": asdict(self.db_config),
                "cache": asdict(self.cache_config),
                "logging": asdict(self.logging_config),
                "guilds": self.guild_configs,
                "updated_at": datetime.now().isoformat(),
            }

            with open(self.config_file, "w") as f:
                json.dump(config_data, f, indent=2)

            logger.info(f"Configuration saved to {self.config_file}")

        except Exception as e:
            logger.error(f"Error saving config: {e}")

    def get_bot_token(self) -> str:
        """Get bot token from environment or config"""
        return getattr(self, "bot_token", os.getenv("DISCORD_TOKEN", ""))

    def get_bot_config(self) -> BotConfig:
        """Get bot configuration"""
        return self.bot_config

    def get_ai_config(self) -> AIProviderConfig:
        """Get AI configuration"""
        return self.ai_config

    def get_db_config(self) -> DatabaseConfig:
        """Get database configuration"""
        return self.db_config

    def get_cache_config(self) -> CacheConfig:
        """Get cache configuration"""
        return self.cache_config

    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration"""
        return self.logging_config

    def get_guild_config(self, guild_id: int) -> Dict[str, Any]:
        """Get guild-specific configuration"""
        return self.guild_configs.get(guild_id, {})

    def set_guild_config(self, guild_id: int, config: Dict[str, Any]):
        """Set guild-specific configuration"""
        self.guild_configs[guild_id] = config
        self.save_config()

    def update_guild_setting(self, guild_id: int, key: str, value: Any):
        """Update a specific guild setting"""
        if guild_id not in self.guild_configs:
            self.guild_configs[guild_id] = {}

        self.guild_configs[guild_id][key] = value
        self.save_config()

    def get_guild_setting(self, guild_id: int, key: str, default: Any = None) -> Any:
        """Get a specific guild setting"""
        guild_config = self.guild_configs.get(guild_id, {})
        return guild_config.get(key, default)

    def get_color(self, color_type: str) -> int:
        """Get color values for embeds"""
        colors = {
            "primary": 0x00BFFF,
            "success": 0x00FF00,
            "error": 0xFF0000,
            "warning": 0xFFFF00,
            "info": 0x0099FF,
            "secondary": 0x6C757D,
        }
        return colors.get(color_type, colors["primary"])

    def get_owner_id(self) -> Optional[int]:
        """Get bot owner ID"""
        # First try bot config, then environment, then guild setting
        if self.bot_config.owner_id is not None:
            return self.bot_config.owner_id

        if owner_id_env := os.getenv("OWNER_ID"):
            try:
                return int(owner_id_env)
            except ValueError:
                pass

        return self.get_guild_setting(0, "owner_id")

    def get_all_settings(self) -> Dict[str, Any]:
        """Get all configuration settings"""
        return {
            "bot": asdict(self.bot_config),
            "ai": asdict(self.ai_config),
            "database": asdict(self.db_config),
            "cache": asdict(self.cache_config),
            "logging": asdict(self.logging_config),
            "guild_count": len(self.guild_configs),
        }

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting from any config section"""
        # Try bot config first
        if hasattr(self.bot_config, key):
            return getattr(self.bot_config, key)

        # Try AI config
        if hasattr(self.ai_config, key):
            return getattr(self.ai_config, key)

        # Try other configs
        for config in [self.db_config, self.cache_config, self.logging_config]:
            if hasattr(config, key):
                return getattr(config, key)

        return default

    def update_setting(self, key: str, value: Any):
        """Update a setting in the appropriate config section"""
        # Try to update in the correct config section
        for config in [
            self.bot_config,
            self.ai_config,
            self.db_config,
            self.cache_config,
            self.logging_config,
        ]:
            if hasattr(config, key):
                setattr(config, key, value)
                self.save_config()
                return True

        return False

    # ------------------------------------------------------------------
    # Feature flag helpers
    # ------------------------------------------------------------------

    def _normalize_feature_key(self, feature_name: str) -> str:
        """Normalize feature keys for consistent lookups."""
        feature_name = feature_name or ""
        feature_name = feature_name.strip()

        # Allow callers to omit common prefixes like ``enable_``
        lowered = feature_name.lower()
        if lowered.startswith("enable_"):
            lowered = lowered[len("enable_") :]

        return lowered

    def is_feature_enabled(
        self, feature_name: str, default: bool = False, guild_id: Optional[int] = None
    ) -> bool:
        """Return whether a feature flag is enabled.

        Feature flags can be stored either globally on the bot configuration
        (``bot.features``) or inside a guild-specific configuration under the
        ``features`` key. This helper normalizes the feature key to support
        lookups like ``notion_integration`` or ``enable_notion_integration``
        transparently and falls back to the provided default when the flag is
        not explicitly set.
        """

        normalized_key = self._normalize_feature_key(feature_name)

        # 1) Guild-specific overrides take precedence
        if guild_id is not None:
            guild_config = self.guild_configs.get(guild_id, {})
            guild_features = guild_config.get("features", {}) or {}
            for key, value in guild_features.items():
                if self._normalize_feature_key(str(key)) == normalized_key:
                    return bool(value)

        # 2) Global bot features
        bot_features = getattr(self.bot_config, "features", {}) or {}
        for key, value in bot_features.items():
            if self._normalize_feature_key(str(key)) == normalized_key:
                return bool(value)

        return bool(default)

    def set_feature_flag(
        self,
        feature_name: str,
        enabled: bool,
        guild_id: Optional[int] = None,
        persist: bool = True,
    ):
        """Set a feature flag on the bot or for a specific guild."""

        normalized_key = self._normalize_feature_key(feature_name)

        if guild_id is not None:
            guild_config = self.guild_configs.setdefault(guild_id, {})
            guild_features = guild_config.setdefault("features", {})
            guild_features[normalized_key] = bool(enabled)
        else:
            bot_features = getattr(self.bot_config, "features", {})
            bot_features[normalized_key] = bool(enabled)
            self.bot_config.features = bot_features

        if persist:
            self.save_config()


# Global unified config manager instance
unified_config = UnifiedConfigManager()

# Backwards compatibility aliases
config_manager = unified_config
enhanced_config = unified_config
