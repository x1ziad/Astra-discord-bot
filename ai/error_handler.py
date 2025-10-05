"""
Enhanced AI Error Handler and Fallback System
Handles API failures, rate limiting, and provider fallbacks
"""

import asyncio
import logging
import time
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger("astra.ai_error_handler")


class AIErrorType(Enum):
    """Types of AI API errors"""

    INSUFFICIENT_CREDITS = "insufficient_credits"
    RATE_LIMITED = "rate_limited"
    INVALID_API_KEY = "invalid_api_key"
    MODEL_UNAVAILABLE = "model_unavailable"
    NETWORK_ERROR = "network_error"
    QUOTA_EXCEEDED = "quota_exceeded"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class ProviderStatus(Enum):
    """Provider status states"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"
    NO_CREDITS = "no_credits"


class AIErrorHandler:
    """Enhanced error handling and fallback system for AI providers"""

    def __init__(self):
        self.provider_states = {}
        self.fallback_providers = []
        self.rate_limiters = {}
        self.error_counts = {}
        self.last_errors = {}

        # Configuration
        self.max_retries = 3
        self.base_backoff = 1.0
        self.max_backoff = 300.0  # 5 minutes
        self.reset_threshold = 3600  # 1 hour

        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize provider configurations and states"""
        # Define available providers with their API keys
        providers = {
            "openrouter": {
                "api_key": os.getenv("OPENROUTER_API_KEY") or os.getenv("AI_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "models": [
                    "anthropic/claude-3-haiku",
                    "meta-llama/llama-3.1-8b-instruct:free",
                ],
                "priority": 1,
            },
            "openrouter_backup": {
                "api_key": os.getenv("OPENROUTER_BACKUP_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "models": [
                    "anthropic/claude-3-haiku",
                    "meta-llama/llama-3.1-8b-instruct:free",
                ],
                "priority": 2,
            },
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "base_url": "https://api.openai.com/v1",
                "models": ["gpt-4o-mini", "gpt-3.5-turbo"],
                "priority": 3,
            },
            "anthropic": {
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "base_url": "https://api.anthropic.com/v1",
                "models": ["claude-3-haiku-20240307"],
                "priority": 4,
            },
        }

        # Initialize only providers with valid API keys
        for name, config in providers.items():
            if config["api_key"]:
                self.provider_states[name] = {
                    "status": ProviderStatus.HEALTHY,
                    "config": config,
                    "failure_count": 0,
                    "last_failure": None,
                    "backoff_until": None,
                    "last_success": None,
                }
                self.error_counts[name] = 0
                self.rate_limiters[name] = {
                    "requests": 0,
                    "window_start": time.time(),
                    "limit": 60,  # 60 requests per minute default
                    "window": 60,
                }

        # Sort providers by priority
        self.fallback_providers = sorted(
            [name for name in self.provider_states.keys()],
            key=lambda x: self.provider_states[x]["config"]["priority"],
        )

        logger.info(f"Initialized AI providers: {', '.join(self.fallback_providers)}")

    def classify_error(
        self, error_message: str, status_code: int = None
    ) -> AIErrorType:
        """Classify error type from error message and status code"""
        error_lower = error_message.lower()

        if (
            status_code == 402
            or "insufficient credits" in error_lower
            or "never purchased credits" in error_lower
        ):
            return AIErrorType.INSUFFICIENT_CREDITS
        elif status_code == 429 or "rate limit" in error_lower:
            return AIErrorType.RATE_LIMITED
        elif (
            status_code == 401
            or "invalid api key" in error_lower
            or "unauthorized" in error_lower
        ):
            return AIErrorType.INVALID_API_KEY
        elif "quota exceeded" in error_lower:
            return AIErrorType.QUOTA_EXCEEDED
        elif "timeout" in error_lower:
            return AIErrorType.TIMEOUT
        elif "model" in error_lower and (
            "unavailable" in error_lower or "not found" in error_lower
        ):
            return AIErrorType.MODEL_UNAVAILABLE
        elif "network" in error_lower or "connection" in error_lower:
            return AIErrorType.NETWORK_ERROR
        else:
            return AIErrorType.UNKNOWN

    def handle_error(
        self, provider: str, error_message: str, status_code: int = None
    ) -> Dict[str, Any]:
        """Handle an error from a specific provider"""
        error_type = self.classify_error(error_message, status_code)

        if provider not in self.provider_states:
            return {"action": "fail", "reason": "Unknown provider"}

        state = self.provider_states[provider]
        current_time = time.time()

        # Update error tracking
        self.error_counts[provider] += 1
        self.last_errors[provider] = {
            "error": error_message,
            "type": error_type,
            "timestamp": current_time,
        }

        # Determine action based on error type
        if error_type == AIErrorType.INSUFFICIENT_CREDITS:
            state["status"] = ProviderStatus.NO_CREDITS
            state["backoff_until"] = current_time + 86400  # 24 hours
            logger.error(
                f"🚫 Provider {provider} has insufficient credits, backing off for 24 hours"
            )
            return {"action": "fallback", "reason": "No credits", "backoff": 86400}

        elif error_type == AIErrorType.RATE_LIMITED:
            state["status"] = ProviderStatus.RATE_LIMITED
            backoff_time = min(
                self.base_backoff * (2 ** state["failure_count"]), self.max_backoff
            )
            state["backoff_until"] = current_time + backoff_time
            logger.warning(
                f"⏳ Provider {provider} rate limited, backing off for {backoff_time:.1f}s"
            )
            return {
                "action": "fallback",
                "reason": "Rate limited",
                "backoff": backoff_time,
            }

        elif error_type == AIErrorType.INVALID_API_KEY:
            state["status"] = ProviderStatus.FAILED
            state["backoff_until"] = current_time + 3600  # 1 hour
            logger.error(
                f"🔑 Provider {provider} has invalid API key, backing off for 1 hour"
            )
            return {"action": "fallback", "reason": "Invalid API key", "backoff": 3600}

        else:
            # General error handling
            state["failure_count"] += 1
            if state["failure_count"] >= self.max_retries:
                state["status"] = ProviderStatus.FAILED
                backoff_time = min(
                    self.base_backoff * (2 ** state["failure_count"]), self.max_backoff
                )
                state["backoff_until"] = current_time + backoff_time
                logger.warning(
                    f"⚠️ Provider {provider} failed {state['failure_count']} times, backing off"
                )
                return {
                    "action": "fallback",
                    "reason": f"Multiple failures ({error_type.value})",
                    "backoff": backoff_time,
                }
            else:
                logger.warning(
                    f"🔄 Provider {provider} error, will retry ({state['failure_count']}/{self.max_retries})"
                )
                return {
                    "action": "retry",
                    "delay": self.base_backoff * state["failure_count"],
                }

    def get_next_provider(self, exclude: List[str] = None) -> Optional[str]:
        """Get the next available provider for fallback"""
        exclude = exclude or []
        current_time = time.time()

        for provider in self.fallback_providers:
            if provider in exclude:
                continue

            state = self.provider_states[provider]

            # Check if provider is available
            if state["backoff_until"] and current_time < state["backoff_until"]:
                continue

            # Check rate limiting
            if self._is_rate_limited(provider):
                continue

            # Reset failure count if enough time has passed
            if (
                state["last_failure"]
                and current_time - state["last_failure"] > self.reset_threshold
            ):
                state["failure_count"] = 0
                state["status"] = ProviderStatus.HEALTHY

            logger.info(f"🔄 Falling back to provider: {provider}")
            return provider

        return None

    def _is_rate_limited(self, provider: str) -> bool:
        """Check if provider is currently rate limited"""
        limiter = self.rate_limiters[provider]
        current_time = time.time()

        # Reset window if needed
        if current_time - limiter["window_start"] >= limiter["window"]:
            limiter["requests"] = 0
            limiter["window_start"] = current_time

        return limiter["requests"] >= limiter["limit"]

    def record_success(self, provider: str):
        """Record a successful request for a provider"""
        if provider in self.provider_states:
            state = self.provider_states[provider]
            state["status"] = ProviderStatus.HEALTHY
            state["failure_count"] = 0
            state["last_success"] = time.time()
            state["backoff_until"] = None

            # Update rate limiter
            limiter = self.rate_limiters[provider]
            limiter["requests"] += 1

    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers"""
        current_time = time.time()
        status = {}

        for provider, state in self.provider_states.items():
            is_available = (
                not state["backoff_until"] or current_time >= state["backoff_until"]
            )

            status[provider] = {
                "status": state["status"].value,
                "available": is_available,
                "failure_count": state["failure_count"],
                "error_count": self.error_counts[provider],
                "last_error": self.last_errors.get(provider),
                "backoff_remaining": max(
                    0, (state["backoff_until"] or 0) - current_time
                ),
            }

        return status

    def reset_provider(self, provider: str):
        """Reset a provider's error state"""
        if provider in self.provider_states:
            state = self.provider_states[provider]
            state["status"] = ProviderStatus.HEALTHY
            state["failure_count"] = 0
            state["backoff_until"] = None
            self.error_counts[provider] = 0
            logger.info(f"🔄 Reset provider {provider}")


# Global error handler instance
ai_error_handler = AIErrorHandler()
