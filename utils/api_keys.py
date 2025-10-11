"""
Enhanced API Key Management for Astra Bot
Provides secure API key handling with validation, rate limiting, and monitoring
"""

import os
import logging
import hashlib
from typing import Dict, Optional, Any, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import asyncio
import json
from pathlib import Path

logger = logging.getLogger("astra.api_keys")


@dataclass
class RateLimit:
    """Rate limiting configuration"""

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_limit: int = 10


@dataclass
class APIServiceConfig:
    """API service configuration"""

    key: str
    base_url: str
    rate_limit: RateLimit
    headers: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    last_validated: Optional[datetime] = None
    validation_failures: int = 0
    total_requests: int = 0
    successful_requests: int = 0


@dataclass
class KeyUsageStats:
    """API key usage statistics"""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limited_requests: int = 0
    last_request: Optional[datetime] = None
    average_response_time: float = 0.0


class SecureAPIKeyManager:
    """Enhanced API key management with security and monitoring"""

    def __init__(self):
        self.services: Dict[str, APIServiceConfig] = {}
        self.usage_stats: Dict[str, KeyUsageStats] = {}
        self._rate_limiters: Dict[str, Dict[str, List[datetime]]] = {}
        self._initialization_lock = asyncio.Lock()
        self._initialized = False

        # Load configurations
        self._load_api_configurations()

    def _load_api_configurations(self):
        """Load API configurations from environment and defaults"""

        # NASA API Configuration
        nasa_key = os.getenv("NASA_API_KEY", "DEMO_KEY")
        is_demo = nasa_key == "DEMO_KEY"

        self.services["nasa"] = APIServiceConfig(
            key=nasa_key,
            base_url="https://api.nasa.gov",
            rate_limit=RateLimit(
                requests_per_minute=5 if is_demo else 30,
                requests_per_hour=10 if is_demo else 1000,
                requests_per_day=50 if is_demo else 10000,
                burst_limit=2 if is_demo else 10,
            ),
            headers={"User-Agent": "AstraBot/2.0 Enhanced"},
            enabled=True,
        )

        # OpenAI API Configuration
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.services["openai"] = APIServiceConfig(
                key=openai_key,
                base_url="https://api.openai.com/v1",
                rate_limit=RateLimit(
                    requests_per_minute=60,
                    requests_per_hour=3000,
                    requests_per_day=100000,
                    burst_limit=20,
                ),
                headers={
                    "Authorization": f"Bearer {openai_key}",
                    "Content-Type": "application/json",
                },
            )

        # Anthropic API Configuration
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            self.services["anthropic"] = APIServiceConfig(
                key=anthropic_key,
                base_url="https://api.anthropic.com",
                rate_limit=RateLimit(
                    requests_per_minute=50,
                    requests_per_hour=2000,
                    requests_per_day=50000,
                ),
                headers={
                    "x-api-key": anthropic_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01",
                },
            )

        # Google Gemini API Configuration
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            self.services["google"] = APIServiceConfig(
                key=google_key,
                base_url="https://generativelanguage.googleapis.com/v1",
                rate_limit=RateLimit(
                    requests_per_minute=60,
                    requests_per_hour=1500,
                    requests_per_day=50000,
                ),
                headers={"Content-Type": "application/json"},
            )

        # Discord API Configuration (bot token)
        discord_token = os.getenv("DISCORD_TOKEN")
        if discord_token:
            self.services["discord"] = APIServiceConfig(
                key=discord_token,
                base_url="https://discord.com/api/v10",
                rate_limit=RateLimit(
                    requests_per_minute=300,
                    requests_per_hour=18000,
                    requests_per_day=432000,
                    burst_limit=50,
                ),
                headers={
                    "Authorization": f"Bot {discord_token}",
                    "Content-Type": "application/json",
                },
            )

        # GitHub API Configuration
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            self.services["github"] = APIServiceConfig(
                key=github_token,
                base_url="https://api.github.com",
                rate_limit=RateLimit(
                    requests_per_minute=60,
                    requests_per_hour=5000,
                    requests_per_day=120000,
                ),
                headers={
                    "Authorization": f"Bearer {github_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )

        # Initialize usage stats for all services
        for service_name in self.services:
            self.usage_stats[service_name] = KeyUsageStats()
            self._rate_limiters[service_name] = {"minute": [], "hour": [], "day": []}

        logger.info(f"Loaded {len(self.services)} API service configurations")

    def _mask_key(self, key: str, visible_chars: int = 4) -> str:
        """Mask API key for logging"""
        if not key or len(key) <= visible_chars * 2:
            return "***"
        return f"{key[:visible_chars]}...{key[-visible_chars:]}"

    def get_api_key(self, service: str) -> Optional[str]:
        """Get API key for a specific service"""
        if service in self.services and self.services[service].enabled:
            return self.services[service].key
        return None

    def get_service_config(self, service: str) -> Optional[APIServiceConfig]:
        """Get full service configuration"""
        return self.services.get(service)

    def get_service_url(self, service: str) -> Optional[str]:
        """Get base URL for a specific service"""
        if service in self.services:
            return self.services[service].base_url
        return None

    def get_service_headers(self, service: str) -> Dict[str, str]:
        """Get headers for a specific service"""
        if service in self.services:
            return self.services[service].headers.copy()
        return {}

    def _cleanup_rate_limit_history(self, service: str):
        """Clean up old rate limit entries"""
        now = datetime.utcnow()

        # Clean minute entries (older than 1 minute)
        minute_cutoff = now - timedelta(minutes=1)
        self._rate_limiters[service]["minute"] = [
            ts for ts in self._rate_limiters[service]["minute"] if ts > minute_cutoff
        ]

        # Clean hour entries (older than 1 hour)
        hour_cutoff = now - timedelta(hours=1)
        self._rate_limiters[service]["hour"] = [
            ts for ts in self._rate_limiters[service]["hour"] if ts > hour_cutoff
        ]

        # Clean day entries (older than 1 day)
        day_cutoff = now - timedelta(days=1)
        self._rate_limiters[service]["day"] = [
            ts for ts in self._rate_limiters[service]["day"] if ts > day_cutoff
        ]

    def check_rate_limit(self, service: str) -> Tuple[bool, str]:
        """Check if service is within rate limits"""
        if service not in self.services:
            return False, f"Unknown service: {service}"

        if not self.services[service].enabled:
            return False, f"Service {service} is disabled"

        config = self.services[service]
        rate_limit = config.rate_limit

        # Clean up old entries
        self._cleanup_rate_limit_history(service)

        # Check minute limit
        minute_count = len(self._rate_limiters[service]["minute"])
        if minute_count >= rate_limit.requests_per_minute:
            return (
                False,
                f"Rate limit exceeded: {minute_count}/{rate_limit.requests_per_minute} per minute",
            )

        # Check hour limit
        hour_count = len(self._rate_limiters[service]["hour"])
        if hour_count >= rate_limit.requests_per_hour:
            return (
                False,
                f"Rate limit exceeded: {hour_count}/{rate_limit.requests_per_hour} per hour",
            )

        # Check day limit
        day_count = len(self._rate_limiters[service]["day"])
        if day_count >= rate_limit.requests_per_day:
            return (
                False,
                f"Rate limit exceeded: {day_count}/{rate_limit.requests_per_day} per day",
            )

        return True, "OK"

    def record_request(
        self, service: str, success: bool = True, response_time: float = 0.0
    ):
        """Record an API request for rate limiting and stats"""
        if service not in self.services:
            return

        now = datetime.utcnow()

        # Update rate limit tracking
        self._rate_limiters[service]["minute"].append(now)
        self._rate_limiters[service]["hour"].append(now)
        self._rate_limiters[service]["day"].append(now)

        # Update usage stats
        stats = self.usage_stats[service]
        stats.total_requests += 1
        stats.last_request = now

        if success:
            stats.successful_requests += 1
        else:
            stats.failed_requests += 1

        # Update average response time
        if response_time > 0:
            total_time = (
                stats.average_response_time * (stats.total_requests - 1) + response_time
            )
            stats.average_response_time = total_time / stats.total_requests

    def get_service_status(self, service: str) -> Dict[str, Any]:
        """Get detailed status for a service"""
        if service not in self.services:
            return {"error": "Service not found"}

        config = self.services[service]
        stats = self.usage_stats[service]

        # Clean up rate limit history for accurate counts
        self._cleanup_rate_limit_history(service)

        return {
            "service": service,
            "enabled": config.enabled,
            "key_configured": bool(config.key and config.key != "DEMO_KEY"),
            "key_preview": self._mask_key(config.key) if config.key else None,
            "base_url": config.base_url,
            "rate_limits": {
                "per_minute": f"{len(self._rate_limiters[service]['minute'])}/{config.rate_limit.requests_per_minute}",
                "per_hour": f"{len(self._rate_limiters[service]['hour'])}/{config.rate_limit.requests_per_hour}",
                "per_day": f"{len(self._rate_limiters[service]['day'])}/{config.rate_limit.requests_per_day}",
            },
            "usage_stats": {
                "total_requests": stats.total_requests,
                "successful_requests": stats.successful_requests,
                "failed_requests": stats.failed_requests,
                "success_rate": (
                    stats.successful_requests / max(1, stats.total_requests)
                )
                * 100,
                "average_response_time": round(stats.average_response_time, 3),
                "last_request": (
                    stats.last_request.isoformat() if stats.last_request else None
                ),
            },
            "validation": {
                "last_validated": (
                    config.last_validated.isoformat() if config.last_validated else None
                ),
                "validation_failures": config.validation_failures,
            },
        }

    def get_all_services_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status for all configured services"""
        return {service: self.get_service_status(service) for service in self.services}

    def disable_service(self, service: str, reason: str = ""):
        """Disable a service (e.g., due to repeated failures)"""
        if service in self.services:
            self.services[service].enabled = False
            logger.warning(f"Disabled API service {service}: {reason}")

    def enable_service(self, service: str):
        """Re-enable a service"""
        if service in self.services:
            self.services[service].enabled = True
            logger.info(f"Enabled API service {service}")

    def validate_service_key(self, service: str) -> Tuple[bool, str]:
        """Validate if a service key appears to be properly configured"""
        if service not in self.services:
            return False, "Service not found"

        config = self.services[service]

        if not config.key:
            return False, "No API key configured"

        # Basic validation checks
        key = config.key

        # Check for obvious placeholder values
        if key in ["YOUR_API_KEY", "DEMO_KEY", "demo", "test", "placeholder"]:
            return False, "Placeholder API key detected"

        # Check minimum length (most API keys are at least 16 characters)
        if len(key) < 16:
            return False, "API key appears too short"

        # Service-specific validation
        if service == "openai" and not key.startswith("sk-"):
            return False, "OpenAI API key should start with 'sk-'"

        if service == "discord" and len(key) < 50:
            return False, "Discord token appears too short"

        config.last_validated = datetime.utcnow()
        return True, "Key appears valid"

    def get_usage_summary(self) -> Dict[str, Any]:
        """Get overall usage summary"""
        total_requests = sum(
            stats.total_requests for stats in self.usage_stats.values()
        )
        total_successful = sum(
            stats.successful_requests for stats in self.usage_stats.values()
        )
        total_failed = sum(stats.failed_requests for stats in self.usage_stats.values())

        return {
            "total_services": len(self.services),
            "enabled_services": sum(
                1 for config in self.services.values() if config.enabled
            ),
            "total_requests": total_requests,
            "successful_requests": total_successful,
            "failed_requests": total_failed,
            "overall_success_rate": (total_successful / max(1, total_requests)) * 100,
            "services": list(self.services.keys()),
        }

    def clear_rate_limits(self, service: Optional[str] = None):
        """Clear rate limit history for testing"""
        if service and service in self._rate_limiters:
            self._rate_limiters[service] = {"minute": [], "hour": [], "day": []}
        else:
            for svc in self._rate_limiters:
                self._rate_limiters[svc] = {"minute": [], "hour": [], "day": []}

        logger.info(f"Cleared rate limits for {service or 'all services'}")


# Global API key manager instance
api_manager = SecureAPIKeyManager()


# Backward compatibility functions
def get_api_key(service: str) -> Optional[str]:
    """Get API key for a specific service (backward compatibility)"""
    return api_manager.get_api_key(service)


def get_service_url(service: str) -> Optional[str]:
    """Get base URL for a specific service (backward compatibility)"""
    return api_manager.get_service_url(service)


def get_service_headers(service: str) -> Dict[str, str]:
    """Get headers for a specific service"""
    return api_manager.get_service_headers(service)


def check_rate_limit(service: str) -> Tuple[bool, str]:
    """Check if service is within rate limits"""
    return api_manager.check_rate_limit(service)


def record_api_request(service: str, success: bool = True, response_time: float = 0.0):
    """Record an API request"""
    return api_manager.record_request(service, success, response_time)


def get_api_status(service: Optional[str] = None) -> Dict[str, Any]:
    """Get API service status"""
    if service:
        return api_manager.get_service_status(service)
    return api_manager.get_all_services_status()


# Legacy API_KEYS dict for backward compatibility
API_KEYS = {
    service: {
        "key": config.key,
        "base_url": config.base_url,
        "rate_limit": {
            "hourly": config.rate_limit.requests_per_hour,
            "daily": config.rate_limit.requests_per_day,
        },
    }
    for service, config in api_manager.services.items()
}
