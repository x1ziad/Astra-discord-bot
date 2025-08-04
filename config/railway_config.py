"""
Environment Configuration for Railway Deployment
Handles all environment variables and Railway-specific configurations
"""

import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path


class RailwayConfig:
    """Railway deployment configuration handler"""

    def __init__(self):
        self.logger = logging.getLogger("railway_config")
        self._config = self._load_environment()
        self._validate_required_vars()

    def _load_environment(self) -> Dict[str, Any]:
        """Load all environment variables with defaults"""
        return {
            # Core Discord Configuration
            "discord_token": self._get_env("DISCORD_TOKEN", required=True),
            "discord_client_id": self._get_env(
                "DISCORD_CLIENT_ID"
            ),  # Optional - not always needed
            "discord_client_secret": self._get_env("DISCORD_CLIENT_SECRET"),
            # AI Configuration - Support Multiple Providers  
            "ai_provider": self._get_env(
                "AI_PROVIDER", "universal"
            ),  # universal, openrouter, github, openai, azure
            
            # Universal AI Configuration (Primary - works with any OpenAI-compatible API)
            "ai_api_key": self._get_env("AI_API_KEY"),  # Primary universal API key
            "ai_base_url": self._get_env("AI_BASE_URL", "https://openrouter.ai/api/v1"), 
            "ai_model": self._get_env("AI_MODEL", "deepseek/deepseek-r1:nitro"),
            "ai_max_tokens": int(self._get_env("AI_MAX_TOKENS", "2000")),
            "ai_temperature": float(self._get_env("AI_TEMPERATURE", "0.7")),
            "ai_provider_name": self._get_env("AI_PROVIDER_NAME", "universal"),
            
            # Legacy OpenRouter Configuration (for backward compatibility)
            "openrouter_api_key": self._get_env(
                "OPENROUTER_API_KEY"
            ),  # Fallback to universal
            "openrouter_model": self._get_env(
                "OPENROUTER_MODEL", "deepseek/deepseek-r1:nitro"
            ),
            "openrouter_max_tokens": int(
                self._get_env("OPENROUTER_MAX_TOKENS", "2000")
            ),
            "openrouter_temperature": float(
                self._get_env("OPENROUTER_TEMPERATURE", "0.7")
            ),
            # GitHub Models Configuration
            "github_token": self._get_env(
                "GITHUB_TOKEN"
            ),  # Optional - fallback to OpenAI if not set
            "github_model": self._get_env("GITHUB_MODEL", "deepseek/DeepSeek-R1-0528"),
            "github_max_tokens": int(self._get_env("GITHUB_MAX_TOKENS", "2000")),
            "github_temperature": float(self._get_env("GITHUB_TEMPERATURE", "0.7")),
            # OpenAI Configuration (fallback)
            "openai_api_key": self._get_env("OPENAI_API_KEY"),
            "openai_model": self._get_env("OPENAI_MODEL", "gpt-4"),
            "openai_max_tokens": int(self._get_env("OPENAI_MAX_TOKENS", "2000")),
            "openai_temperature": float(self._get_env("OPENAI_TEMPERATURE", "0.7")),
            # NASA API
            "nasa_api_key": self._get_env("NASA_API_KEY", "DEMO_KEY"),
            # Notion Integration (Optional)
            "notion_token": self._get_env("NOTION_TOKEN"),
            "notion_database_id": self._get_env("NOTION_DATABASE_ID"),
            # Bot Configuration
            "bot_prefix": self._get_env("BOT_PREFIX", "!"),
            "debug_mode": self._get_env("DEBUG_MODE", "false").lower() == "true",
            "log_level": self._get_env("LOG_LEVEL", "INFO"),
            "database_url": self._get_env("DATABASE_URL", "sqlite:///data/astra.db"),
            # Security
            "encryption_key": self._get_env("ENCRYPTION_KEY"),
            "webhook_secret": self._get_env("WEBHOOK_SECRET"),
            # Performance
            "max_concurrent_requests": int(
                self._get_env("MAX_CONCURRENT_REQUESTS", "10")
            ),
            "request_timeout": int(self._get_env("REQUEST_TIMEOUT", "30")),
            "cache_ttl": int(self._get_env("CACHE_TTL", "3600")),
            # Railway Specific
            "railway_environment": self._get_env("RAILWAY_ENVIRONMENT", "production"),
            "railway_project_id": self._get_env("RAILWAY_PROJECT_ID"),
            "railway_service_id": self._get_env("RAILWAY_SERVICE_ID"),
            "port": int(self._get_env("PORT", "8000")),
            # Monitoring
            "sentry_dsn": self._get_env("SENTRY_DSN"),
            "webhook_url": self._get_env("WEBHOOK_URL"),
        }

    def _get_env(
        self, key: str, default: Optional[str] = None, required: bool = False
    ) -> str:
        """Get environment variable with validation"""
        value = os.getenv(key, default)

        if required and not value:
            self.logger.error(f"Required environment variable {key} is not set!")
            raise ValueError(f"Missing required environment variable: {key}")

        return value

    def _validate_required_vars(self):
        """Validate that all required environment variables are present"""
        required_vars = ["discord_token"]  # Only DISCORD_TOKEN is absolutely required

        missing_vars = []
        for var in required_vars:
            if not self._config.get(var):
                missing_vars.append(var.upper())

        if missing_vars:
            self.logger.error(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)

    def get_discord_config(self) -> Dict[str, str]:
        """Get Discord-specific configuration"""
        return {
            "token": self.get("discord_token"),
            "client_id": self.get("discord_client_id"),
            "client_secret": self.get("discord_client_secret"),
            "prefix": self.get("bot_prefix"),
        }

    def get_openai_config(self) -> Dict[str, Any]:
        """Get OpenAI-specific configuration"""
        return {
            "api_key": self.get("openai_api_key"),
            "model": self.get("openai_model"),
            "max_tokens": self.get("openai_max_tokens"),
            "temperature": self.get("openai_temperature"),
        }

    def get_openrouter_config(self) -> Dict[str, Any]:
        """Get OpenRouter-specific configuration"""
        return {
            "api_key": self.get("openrouter_api_key"),
            "model": self.get("openrouter_model"),
            "max_tokens": self.get("openrouter_max_tokens"),
            "temperature": self.get("openrouter_temperature"),
            "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        }

    def get_universal_ai_config(self) -> Dict[str, Any]:
        """Get Universal AI configuration (works with any OpenAI-compatible API)"""
        # Use AI_API_KEY or fallback to OPENROUTER_API_KEY for backward compatibility
        api_key = self.get("ai_api_key") or self.get("openrouter_api_key")
        
        return {
            "api_key": api_key,
            "base_url": self.get("ai_base_url"),
            "model": self.get("ai_model"),
            "max_tokens": self.get("ai_max_tokens"),
            "temperature": self.get("ai_temperature"),
            "provider_name": self.get("ai_provider_name"),
        }

    def get_github_config(self) -> Dict[str, Any]:
        """Get GitHub Models configuration"""
        return {
            "token": self.get("github_token"),
            "model": self.get("github_model"),
            "max_tokens": self.get("github_max_tokens"),
            "temperature": self.get("github_temperature"),
            "endpoint": "https://models.github.ai/inference",
        }

    def get_ai_provider(self) -> str:
        """Get the active AI provider"""
        return self.get("ai_provider", "universal")

    def get_active_ai_config(self) -> Dict[str, Any]:
        """Get configuration for the active AI provider"""
        provider = self.get_ai_provider()
        if provider == "universal":
            return self.get_universal_ai_config()
        elif provider == "openrouter":
            return self.get_openrouter_config()
        elif provider == "github":
            return self.get_github_config()
        elif provider == "openai":
            return self.get_openai_config()
        else:
            # Default to universal
            return self.get_universal_ai_config()

    def get_nasa_config(self) -> Dict[str, str]:
        """Get NASA API configuration"""
        return {"api_key": self.get("nasa_api_key")}

    def get_database_config(self) -> Dict[str, str]:
        """Get database configuration"""
        return {"url": self.get("database_url")}

    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.get("railway_environment") == "production"

    def is_debug(self) -> bool:
        """Check if debug mode is enabled"""
        return self.get("debug_mode", False)

    def get_log_level(self) -> str:
        """Get logging level"""
        return self.get("log_level", "INFO")

    def create_config_file(self):
        """Create configuration file from environment variables"""
        config_data = {
            "bot": {
                "name": "Astra",
                "version": "2.0.1",
                "description": "Advanced Discord bot with AI capabilities",
                "prefix": self.get("bot_prefix"),
                "debug": self.is_debug(),
            },
            "discord": self.get_discord_config(),
            "openai": self.get_openai_config(),
            "nasa": self.get_nasa_config(),
            "database": self.get_database_config(),
            "features": {
                "ai_chat": True,
                "space_content": True,
                "quiz_system": True,
                "analytics": True,
                "admin_commands": True,
                "auto_moderation": False,
                "voice_support": False,
            },
            "colors": {
                "primary": "#7289da",
                "success": "#43b581",
                "warning": "#faa61a",
                "error": "#f04747",
                "info": "#17a2b8",
            },
            "limits": {
                "max_concurrent_requests": self.get("max_concurrent_requests"),
                "request_timeout": self.get("request_timeout"),
                "cache_ttl": self.get("cache_ttl"),
            },
        }

        # Ensure config directory exists
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)

        # Write config file
        import json

        config_file = config_dir / "config.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f, indent=2)

        self.logger.info(f"Configuration file created: {config_file}")
        return config_file


# Global railway config instance
railway_config = RailwayConfig()


def setup_railway_logging():
    """Setup logging for Railway deployment"""
    log_level = getattr(logging, railway_config.get_log_level().upper())

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),  # Railway captures stdout
        ],
    )

    # Disable noisy loggers in production
    if railway_config.is_production():
        logging.getLogger("discord").setLevel(logging.WARNING)
        logging.getLogger("discord.http").setLevel(logging.WARNING)
        logging.getLogger("aiohttp").setLevel(logging.WARNING)


def get_railway_config() -> RailwayConfig:
    """Get the railway configuration instance"""
    return railway_config
