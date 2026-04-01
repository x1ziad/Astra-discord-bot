"""
Security and Performance Configuration for Astra Bot
Contains security best practices, rate limiting limits, and performance thresholds

This file centralizes all security and performance settings for easy management
"""

from typing import Dict, Any
from dataclasses import dataclass

# 🔒 SECURITY SETTINGS
SECURITY_CONFIG = {
    # ✅ SSL/TLS Configuration
    "ssl": {
        "enabled": True,  # ALWAYS enabled for production
        "verify_certificates": True,
        "min_tls_version": "1.2",
        "ca_bundle": None,  # Uses system default certifi
    },
    # ⏳ Rate Limiting Configuration
    "rate_limiting": {
        # User-level rate limiting
        "user": {
            "max_commands_per_minute": 30,
            "max_ai_calls_per_minute": 10,
            "max_api_calls_per_hour": 1000,
        },
        # Guild-level rate limiting
        "guild": {
            "max_commands_per_minute": 100,
            "max_concurrent_operations": 50,
        },
        # Specific command limits
        "commands": {
            "companion": {
                "max_per_minute": 10,
                "cooldown_seconds": 5,
            },
            "test_astra": {
                "max_per_minute": 5,
                "cooldown_seconds": 10,
            },
            "admin_help": {
                "max_per_minute": 20,
                "cooldown_seconds": 2,
            },
        },
    },
    # 🔐 Prompt Injection Protection
    "prompt_injection": {
        "enabled": True,
        "max_input_length": 2000,
        "dangerous_patterns": [
            r"\bignore\s+previous",
            r"\bforget\s+",
            r"\bsystem:\s*",
            r"\badmin:\s*",
            r"\bpretend\s+to\s+be",
            r"\bact\s+as",
            r"\byou\s+are\s+now",
            r"\bdisregard",
            r"\boverride",
        ],
    },
    # 🛡️ Input Validation
    "input_validation": {
        "enabled": True,
        "max_message_length": 4000,
        "max_embed_fields": 25,
        "sanitize_mentions": True,
    },
    # 🔑 API Credentials
    "credentials": {
        "require_env_vars": [
            "DISCORD_TOKEN",
        ],
        "optional_env_vars": [
            "MISTRAL_API_KEY",
            "GOOGLE_API_KEY",
            "GROQ_API_KEY",
            "OPENAI_API_KEY",
        ],
    },
}

# ⚡ PERFORMANCE SETTINGS
PERFORMANCE_CONFIG = {
    # 🔄 Caching Configuration
    "cache": {
        "enabled": True,
        "default_ttl": 600,  # 10 minutes
        "max_size": 10000,  # Maximum cache entries
        "strategies": {
            "user_profiles": {
                "ttl": 1800,  # 30 minutes
                "max_size": 5000,
            },
            "guild_configs": {
                "ttl": 3600,  # 1 hour
                "max_size": 1000,
            },
            "ai_responses": {
                "ttl": 300,  # 5 minutes
                "max_size": 2000,
            },
        },
    },
    # 📊 Database Configuration
    "database": {
        "pool_size": 15,
        "min_pool_size": 3,
        "max_overflow": 20,
        "query_timeout": 30.0,  # seconds
        "enable_wal": True,  # Write-Ahead Logging
        "enable_pragma_optimization": True,
        "slow_query_threshold": 0.5,  # Log queries > 500ms
    },
    # 🎯 Message Processing
    "message_processing": {
        "max_concurrent_tasks": 50,
        "batch_size": 10,
        "queue_timeout": 30.0,
        "priority_levels": {
            "urgent": 0,
            "high": 1,
            "normal": 2,
            "low": 3,
        },
    },
    # 💾 Memory Management
    "memory": {
        "gc_interval": 300,  # Run GC every 5 minutes
        "max_memory_mb": 1024,  # Alert if exceeds 1GB
        "enable_memory_profiling": False,
    },
    # ⚙️ Async Configuration
    "async": {
        "use_uvloop": True,  # 40% performance boost
        "use_fast_json": True,  # orjson for 2x JSON speed
        "timeout_default": 25.0,  # HTTP request timeout
    },
    # 📈 Monitor and Logging
    "monitoring": {
        "enable_performance_logging": True,
        "slow_response_threshold": 3.0,  # Log if response > 3s
        "enable_metrics": True,
        "metrics_interval": 300,  # Collect metrics every 5 minutes
    },
}

# 🚀 LAUNCH CONFIGURATION
LAUNCH_CONFIG = {
    # 🎮 Discord Configuration
    "discord": {
        "intents": {
            "default": True,
            "message_content": True,
            "members": True,
            "guild_reactions": True,
            "presences": False,  # Heavy - disabled
            "voice_states": False,  # Not needed
            "guild_typing": False,
            "dm_reactions": False,
            "dm_typing": False,
        },
        "member_cache": {
            "enabled": False,  # Minimal cache to reduce API calls
            "strategy": "none",  # Use on-demand fetching
        },
        "max_messages": 1000,
        "chunk_guilds_at_startup": False,
    },
    # 🌐 HTTP Configuration
    "http": {
        "connector": {
            "limit": 150,  # Connection pool size
            "limit_per_host": 50,
            "ttl_dns_cache": 600,
            "keepalive_timeout": 30,
        },
        "timeout": {
            "total": 25.0,
            "connect": 5.0,
            "sock_read": 8.0,
        },
    },
    # 🤖 AI Configuration
    "ai": {
        "providers": ["mistral", "google", "groq"],  # Fallback order
        "timeout": 30.0,
        "max_retries": 3,
        "retry_delay": 1.0,
    },
}

# 📋 MAINTENANCE TASKS
MAINTENANCE_CONFIG = {
    "tasks": {
        "cleanup_cache": {
            "enabled": True,
            "interval": 600,  # 10 minutes
        },
        "prune_database": {
            "enabled": True,
            "interval": 3600,  # 1 hour
            "max_age_days": 30,
        },
        "health_check": {
            "enabled": True,
            "interval": 300,  # 5 minutes
        },
        "memory_optimization": {
            "enabled": True,
            "interval": 300,  # 5 minutes
        },
    },
}

# 🎯 MONITORING ALERTS
ALERTS_CONFIG = {
    "performance": {
        "response_time_threshold_ms": 5000,
        "memory_threshold_mb": 1024,
        "cpu_threshold_percent": 80,
    },
    "security": {
        "rate_limit_alerts": True,
        "failed_auth_alerts": True,
        "suspicious_pattern_alerts": True,
    },
    "availability": {
        "api_error_threshold": 10,  # Per 5 minutes
        "timeout_threshold": 5,  # Per 5 minutes
    },
}


@dataclass
class SecuritySettings:
    """Dataclass for type-safe security settings access"""

    ssl_enabled: bool = SECURITY_CONFIG["ssl"]["enabled"]
    rate_limiting_enabled: bool = True
    prompt_injection_protection_enabled: bool = SECURITY_CONFIG["prompt_injection"][
        "enabled"
    ]
    input_validation_enabled: bool = SECURITY_CONFIG["input_validation"]["enabled"]

    def __post_init__(self):
        """Validate settings on initialization"""
        if not self.ssl_enabled:
            import logging

            logger = logging.getLogger("astra.security")
            logger.critical("🔴 SSL IS DISABLED - This is a security vulnerability!")


# 🔒 Validate security settings on import
_security = SecuritySettings()

if not _security.ssl_enabled:
    import logging

    logging.getLogger("astra.security").critical(
        "🔴 SSL VERIFICATION IS DISABLED - ENABLE IMMEDIATELY"
    )
