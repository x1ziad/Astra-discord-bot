#!/usr/bin/env python3
"""
Multi-Provider AI Management System
Manages 2 AI providers (Google Gemini, Groq) with intelligent fallback
"""
import asyncio
import os
import time
import logging
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger("astra.multi_provider_ai")


class AIProvider(Enum):
    """Supported AI providers"""

    GOOGLE = "google"
    GROQ = "groq"


@dataclass
class ProviderStatus:
    """Track provider health and availability"""

    provider: AIProvider
    available: bool = True
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    rate_limited_until: Optional[datetime] = None
    avg_response_time: float = 0.0
    total_requests: int = 0
    successful_requests: int = 0


@dataclass
class AIResponse:
    """Standardized AI response format"""

    content: str
    provider: str
    model: str
    usage: Dict[str, Any]
    metadata: Dict[str, Any]
    response_time: float
    success: bool = True


class MultiProviderAIManager:
    """Intelligent multi-provider AI management with fallback and load balancing"""

    def __init__(self):
        self.providers = {
            AIProvider.GOOGLE: ProviderStatus(AIProvider.GOOGLE),
            AIProvider.GROQ: ProviderStatus(AIProvider.GROQ),
        }

        # Load configuration
        self.fallback_order = self._get_fallback_order()
        self.auto_fallback = (
            os.getenv("AUTO_FALLBACK_ENABLED", "true").lower() == "true"
        )

        # Initialize provider clients
        self._initialize_clients()

    def _get_fallback_order(self) -> List[AIProvider]:
        """Get provider fallback order from environment"""
        fallback_str = os.getenv("FALLBACK_PROVIDERS", "google,groq")
        provider_names = [p.strip().lower() for p in fallback_str.split(",")]

        fallback_order = []
        for name in provider_names:
            try:
                fallback_order.append(AIProvider(name))
            except ValueError:
                logger.warning(f"Unknown provider in fallback order: {name}")

        return fallback_order

    def _initialize_clients(self):
        """Initialize all provider clients"""
        self.clients = {}

        # Google Gemini
        try:
            from ai.google_gemini_client import GoogleGeminiClient

            self.clients[AIProvider.GOOGLE] = GoogleGeminiClient()
            google_available = self.clients[AIProvider.GOOGLE].available
            self.providers[AIProvider.GOOGLE].available = google_available
            logger.info(
                f"Google Gemini client: {'Available' if google_available else 'Not Available'}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Google client: {e}")
            self.providers[AIProvider.GOOGLE].available = False



        # Groq
        try:
            groq_key = os.getenv("GROQ_API_KEY")
            if groq_key and groq_key.startswith("gsk_"):
                # Initialize Groq client
                self.clients[AIProvider.GROQ] = self._create_groq_client(groq_key)
                self.providers[AIProvider.GROQ].available = True
                logger.info("Groq client: Available")
            else:
                self.providers[AIProvider.GROQ].available = False
                logger.info("Groq client: Not Available (no API key)")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            self.providers[AIProvider.GROQ].available = False

    def _create_groq_client(self, api_key: str):
        """Create Groq client wrapper"""

        class GroqClient:
            def __init__(self, api_key):
                self.api_key = api_key
                self.base_url = "https://api.groq.com/openai/v1"

            async def generate_response(self, prompt: str, **kwargs):
                """Generate response using Groq API"""
                import aiohttp
                import json

                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }

                payload = {
                    "model": kwargs.get("model", "llama-3.1-8b-instant"),
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": kwargs.get("max_tokens", 8192),
                    "temperature": kwargs.get("temperature", 0.7),
                }

                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return {
                                "content": data["choices"][0]["message"]["content"],
                                "model": data["model"],
                                "usage": data.get("usage", {}),
                                "metadata": {
                                    "finish_reason": data["choices"][0].get(
                                        "finish_reason", "stop"
                                    ),
                                    "created_at": datetime.now().isoformat(),
                                },
                            }
                        else:
                            error_text = await response.text()
                            raise Exception(
                                f"Groq API error {response.status}: {error_text}"
                            )

        return GroqClient(api_key)

    def _is_provider_healthy(self, provider: AIProvider) -> bool:
        """Check if provider is healthy and available"""
        status = self.providers[provider]

        # Check if provider is available
        if not status.available:
            return False

        # Check rate limiting
        if status.rate_limited_until and datetime.now() < status.rate_limited_until:
            return False

        # Check consecutive failures (circuit breaker pattern)
        if status.consecutive_failures >= 3:
            # Allow retry after 5 minutes
            if status.last_failure and datetime.now() - status.last_failure < timedelta(
                minutes=5
            ):
                return False

        return True

    def _update_provider_status(
        self,
        provider: AIProvider,
        success: bool,
        response_time: float = 0.0,
        error: str = None,
    ):
        """Update provider status based on request outcome"""
        status = self.providers[provider]
        status.total_requests += 1

        if success:
            status.successful_requests += 1
            status.consecutive_failures = 0
            status.last_success = datetime.now()

            # Update average response time
            if status.avg_response_time == 0:
                status.avg_response_time = response_time
            else:
                status.avg_response_time = (status.avg_response_time * 0.8) + (
                    response_time * 0.2
                )
        else:
            status.consecutive_failures += 1
            status.last_failure = datetime.now()

            # Handle rate limiting
            if error and ("429" in error or "rate" in error.lower()):
                status.rate_limited_until = datetime.now() + timedelta(minutes=10)
                logger.warning(
                    f"Provider {provider.value} rate limited until {status.rate_limited_until}"
                )

    async def generate_response(self, prompt: str, **kwargs) -> AIResponse:
        """Generate response using intelligent provider selection with fallback"""

        # Try providers in fallback order
        last_error = None

        for provider in self.fallback_order:
            if not self._is_provider_healthy(provider):
                logger.debug(f"Skipping unhealthy provider: {provider.value}")
                continue

            try:
                logger.info(f"Attempting response with provider: {provider.value}")
                start_time = time.time()

                # Generate response based on provider type
                if provider == AIProvider.GOOGLE:
                    response = await self._generate_google_response(prompt, **kwargs)
                elif provider == AIProvider.GROQ:
                    response = await self._generate_groq_response(prompt, **kwargs)
                else:
                    continue

                response_time = time.time() - start_time

                # Update status on success
                self._update_provider_status(provider, True, response_time)

                logger.info(
                    f"✅ Response generated successfully with {provider.value} ({response_time:.2f}s)"
                )
                return response

            except Exception as e:
                error_str = str(e)
                response_time = time.time() - start_time

                # Update status on failure
                self._update_provider_status(provider, False, response_time, error_str)

                logger.warning(f"❌ Provider {provider.value} failed: {error_str}")
                last_error = e

                # Continue to next provider if auto_fallback is enabled
                if not self.auto_fallback:
                    break

        # All providers failed
        raise Exception(f"All AI providers failed. Last error: {last_error}")

    async def _generate_google_response(self, prompt: str, **kwargs) -> AIResponse:
        """Generate response using Google Gemini"""
        client = self.clients[AIProvider.GOOGLE]

        response = await client.generate_response(
            prompt=prompt,
            max_tokens=kwargs.get("max_tokens", 8192),
            temperature=kwargs.get("temperature", 0.7),
        )

        return AIResponse(
            content=response["content"],
            provider="google",
            model=response.get("model", "models/gemini-2.5-flash"),
            usage=response.get("usage", {}),
            metadata=response.get("metadata", {}),
            response_time=0.0,  # Will be set by caller
        )



    async def _generate_groq_response(self, prompt: str, **kwargs) -> AIResponse:
        """Generate response using Groq"""
        client = self.clients[AIProvider.GROQ]

        response = await client.generate_response(
            prompt=prompt,
            max_tokens=kwargs.get("max_tokens", 8192),
            temperature=kwargs.get("temperature", 0.7),
            model=kwargs.get("model", "llama-3.1-8b-instant"),
        )

        return AIResponse(
            content=response["content"],
            provider="groq",
            model=response.get("model", "llama-3.1-8b-instant"),
            usage=response.get("usage", {}),
            metadata=response.get("metadata", {}),
            response_time=0.0,  # Will be set by caller
        )

    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers"""
        status_report = {}

        for provider, status in self.providers.items():
            success_rate = (
                status.successful_requests / max(status.total_requests, 1)
            ) * 100

            status_report[provider.value] = {
                "available": status.available,
                "healthy": self._is_provider_healthy(provider),
                "success_rate": f"{success_rate:.1f}%",
                "avg_response_time": f"{status.avg_response_time:.2f}s",
                "total_requests": status.total_requests,
                "consecutive_failures": status.consecutive_failures,
                "last_success": (
                    status.last_success.isoformat() if status.last_success else None
                ),
                "rate_limited": status.rate_limited_until is not None
                and datetime.now() < status.rate_limited_until,
            }

        return status_report

    def get_best_provider(self) -> Optional[AIProvider]:
        """Get the best available provider based on performance metrics"""
        healthy_providers = [
            p for p in self.fallback_order if self._is_provider_healthy(p)
        ]

        if not healthy_providers:
            return None

        # Sort by success rate and response time
        def provider_score(provider):
            status = self.providers[provider]
            if status.total_requests == 0:
                return float("inf")  # No data, lowest priority

            success_rate = status.successful_requests / status.total_requests
            response_time_penalty = (
                status.avg_response_time * 0.1
            )  # 100ms = 0.01 penalty

            return (1 - success_rate) + response_time_penalty

        return min(healthy_providers, key=provider_score)


# Global instance
multi_provider_ai = MultiProviderAIManager()
