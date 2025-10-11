#!/usr/bin/env python3
"""
Multi-Provider AI Management System
Manages 3 AI providers (Google Gemini, Groq, Mistral) with intelligent fallback
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
    MISTRAL = "mistral"


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
            AIProvider.MISTRAL: ProviderStatus(AIProvider.MISTRAL),
        }

        # Load configuration
        self.fallback_order = self._get_fallback_order()
        self.auto_fallback = (
            os.getenv("AUTO_FALLBACK_ENABLED", "true").lower() == "true"
        )

        # PERFORMANCE OPTIMIZATION: Enhanced caching and performance features
        self._response_cache = {}
        self._provider_performance_cache = {}
        self._fast_provider_order = None  # Cached optimal provider order
        self._personality_optimized = True
        self._max_cache_size = 500
        self._cache_ttl = 300  # 5 minutes

        # Initialize provider clients
        self.clients = {}
        self._initialize_clients()

    def _get_fallback_order(self) -> List[AIProvider]:
        """Get fallback order from environment or use default"""
        fallback_str = os.getenv("FALLBACK_PROVIDERS", "groq,google,mistral")
        provider_names = [name.strip() for name in fallback_str.split(",")]

        fallback_order = []
        for name in provider_names:
            try:
                fallback_order.append(AIProvider(name))
            except ValueError:
                logger.warning(f"Invalid provider in fallback order: {name}")

        return fallback_order

    def _initialize_clients(self):
        """Initialize all AI provider clients"""
        # Google Gemini
        try:
            from .google_gemini_client import GoogleGeminiClient

            self.clients[AIProvider.GOOGLE] = GoogleGeminiClient()
            google_available = self.clients[AIProvider.GOOGLE].available
            self.providers[AIProvider.GOOGLE].available = google_available

            if google_available:
                logger.info("Google Gemini client: Available")
            else:
                logger.info("Google Gemini client: Not Available")
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

        # Mistral Direct API
        try:
            mistral_key = os.getenv("MISTRAL_API_KEY")
            if mistral_key:
                # Initialize Mistral client directly
                self.clients[AIProvider.MISTRAL] = self._create_mistral_client(
                    mistral_key
                )
                self.providers[AIProvider.MISTRAL].available = True
                logger.info("Mistral client: Available")
            else:
                self.providers[AIProvider.MISTRAL].available = False
                logger.info("Mistral client: Not Available (no API key)")
        except Exception as e:
            logger.error(f"Failed to initialize Mistral client: {e}")
            self.providers[AIProvider.MISTRAL].available = False

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
                                "model": data.get("model", "llama-3.1-8b-instant"),
                                "usage": data.get("usage", {}),
                                "provider": "groq",
                            }
                        else:
                            error_text = await response.text()
                            raise Exception(f"HTTP {response.status}: {error_text}")

        return GroqClient(api_key)

    def _create_mistral_client(self, api_key: str):
        """Create Mistral client using direct API"""

        class MistralClient:
            def __init__(self, api_key):
                self.api_key = api_key
                from mistralai import Mistral

                self.client = Mistral(api_key=api_key)

            async def generate_response(self, prompt: str, **kwargs):
                """Generate response using direct Mistral API"""
                import asyncio

                def sync_generate():
                    try:
                        response = self.client.chat.complete(
                            model=kwargs.get("model", "mistral-large-latest"),
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=kwargs.get("max_tokens", 1000),
                            temperature=kwargs.get("temperature", 0.7),
                        )

                        choice = response.choices[0]
                        content = choice.message.content

                        return {
                            "content": content,
                            "model": kwargs.get("model", "mistral-large-latest"),
                            "usage": {
                                "prompt_tokens": response.usage.prompt_tokens,
                                "completion_tokens": response.usage.completion_tokens,
                                "total_tokens": response.usage.total_tokens,
                            },
                            "provider": "mistral",
                        }
                    except Exception as e:
                        raise Exception(f"Mistral API error: {str(e)}")

                # Run sync function in executor
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, sync_generate)

        return MistralClient(api_key)

    async def generate_response(
        self,
        prompt: str,
        max_tokens: int = 8192,
        temperature: float = 0.7,
        model: Optional[str] = None,
        **kwargs,
    ) -> AIResponse:
        """Generate AI response with intelligent provider fallback and performance optimization"""

        # PERFORMANCE: Check cache first for identical prompts
        cache_key = self._generate_cache_key(prompt, max_tokens, temperature, model)
        if cache_key in self._response_cache:
            cached_entry = self._response_cache[cache_key]
            if time.time() - cached_entry["timestamp"] < self._cache_ttl:
                logger.debug(
                    f"⚡ Returning cached response for prompt: {prompt[:50]}..."
                )
                return cached_entry["response"]

        # OPTIMIZATION: Use performance-optimized provider order
        provider_order = self._get_optimal_provider_order()

        for provider in provider_order:
            if not self._is_provider_available(provider):
                logger.debug(f"Skipping {provider.value}: not available")
                continue

            try:
                logger.info(f"Attempting generation with {provider.value}")
                start_time = time.time()

                # Generate response based on provider type
                if provider == AIProvider.GOOGLE:
                    response = await self._generate_google_response(prompt, **kwargs)
                elif provider == AIProvider.GROQ:
                    response = await self._generate_groq_response(prompt, **kwargs)
                elif provider == AIProvider.MISTRAL:
                    response = await self._generate_mistral_response(prompt, **kwargs)
                else:
                    continue

                response_time = time.time() - start_time

                # Update status on success
                self._update_provider_status(provider, True, response_time)

                logger.info(
                    f"Successfully generated response using {provider.value} in {response_time:.2f}s"
                )

                # Set actual response time
                response.response_time = response_time

                # PERFORMANCE: Cache successful response
                self._cache_response(cache_key, response)

                return response

            except Exception as e:
                response_time = time.time() - start_time
                self._update_provider_status(provider, False, response_time)

                logger.warning(f"Provider {provider.value} failed: {str(e)[:100]}...")

                # If this is the last provider, re-raise the exception
                if provider == self.fallback_order[-1]:
                    raise Exception(f"All AI providers failed. Last error: {str(e)}")

        raise Exception("No available AI providers")

    def _is_provider_available(self, provider: AIProvider) -> bool:
        """Check if a provider is available and healthy"""
        return self.providers[provider].available and self._is_provider_healthy(
            provider
        )

    def _is_provider_healthy(self, provider: AIProvider) -> bool:
        """Check if provider is healthy (not rate limited, not too many failures)"""
        status = self.providers[provider]

        # Check rate limiting
        if status.rate_limited_until and datetime.now() < status.rate_limited_until:
            return False

        # Check consecutive failures
        if status.consecutive_failures >= 3:
            return False

        return True

    def _update_provider_status(
        self, provider: AIProvider, success: bool, response_time: float
    ):
        """Update provider performance metrics"""
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
                status.avg_response_time = (
                    status.avg_response_time * 0.8 + response_time * 0.2
                )
        else:
            status.consecutive_failures += 1
            status.last_failure = datetime.now()

    async def _generate_google_response(self, prompt: str, **kwargs) -> AIResponse:
        """Generate response using Google Gemini"""
        client = self.clients[AIProvider.GOOGLE]

        result = await client.generate_response(
            prompt=prompt,
            max_tokens=kwargs.get("max_tokens", 8192),
            temperature=kwargs.get("temperature", 0.7),
        )

        return AIResponse(
            content=result["content"],
            provider="google",
            model=result["model"],
            usage=result["usage"],
            metadata={
                "provider_type": "google_gemini",
                "safety_ratings": result.get("safety_ratings", []),
            },
            response_time=0.0,  # Will be set by caller
        )

    async def _generate_groq_response(self, prompt: str, **kwargs) -> AIResponse:
        """Generate response using Groq"""
        client = self.clients[AIProvider.GROQ]

        result = await client.generate_response(prompt, **kwargs)

        return AIResponse(
            content=result["content"],
            provider="groq",
            model=result["model"],
            usage=result["usage"],
            metadata={
                "provider_type": "groq_llama",
                "via": "groq_api",
            },
            response_time=0.0,  # Will be set by caller
        )

    async def _generate_mistral_response(self, prompt: str, **kwargs) -> AIResponse:
        """Generate response using direct Mistral AI API"""
        client = self.clients[AIProvider.MISTRAL]

        try:
            result = await client.generate_response(prompt, **kwargs)

            return AIResponse(
                content=result["content"],
                provider="mistral",
                model=result["model"],
                usage=result["usage"],
                metadata={
                    "provider_type": "mistral_direct",
                    "via": "mistral_api",
                },
                response_time=0.0,  # Will be set by caller
            )
        except Exception as e:
            raise Exception(f"Mistral generation failed: {str(e)}")

    def _generate_cache_key(
        self, prompt: str, max_tokens: int, temperature: float, model: Optional[str]
    ) -> str:
        """Generate cache key for response caching"""
        import hashlib

        key_data = f"{prompt}:{max_tokens}:{temperature}:{model}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _get_optimal_provider_order(self) -> List[AIProvider]:
        """Get provider order optimized for performance"""
        if self._fast_provider_order and len(self._provider_performance_cache) > 0:
            # Use cached optimal order if available
            return self._fast_provider_order

        # Sort providers by performance (response time + success rate)
        provider_scores = []
        for provider in self.fallback_order:
            status = self.providers[provider]
            if status.total_requests > 0:
                success_rate = status.successful_requests / status.total_requests
                # Lower response time + higher success rate = better score
                score = status.avg_response_time / max(success_rate, 0.1)
                provider_scores.append((provider, score))

        if provider_scores:
            # Sort by score (lower is better)
            provider_scores.sort(key=lambda x: x[1])
            optimized_order = [provider for provider, _ in provider_scores]

            # Add any remaining providers not in scores
            for provider in self.fallback_order:
                if provider not in optimized_order:
                    optimized_order.append(provider)

            self._fast_provider_order = optimized_order
            return optimized_order

        return self.fallback_order

    def _cache_response(self, cache_key: str, response: AIResponse) -> None:
        """Cache response with TTL management"""
        # Clean old cache entries if cache is full
        if len(self._response_cache) >= self._max_cache_size:
            current_time = time.time()
            # Remove expired entries
            expired_keys = [
                key
                for key, entry in self._response_cache.items()
                if current_time - entry["timestamp"] > self._cache_ttl
            ]
            for key in expired_keys:
                del self._response_cache[key]

            # If still full, remove oldest entries
            if len(self._response_cache) >= self._max_cache_size:
                oldest_keys = sorted(
                    self._response_cache.keys(),
                    key=lambda k: self._response_cache[k]["timestamp"],
                )[
                    :10
                ]  # Remove 10 oldest
                for key in oldest_keys:
                    del self._response_cache[key]

        self._response_cache[cache_key] = {
            "response": response,
            "timestamp": time.time(),
        }

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
                "last_failure": (
                    status.last_failure.isoformat() if status.last_failure else None
                ),
            }

        return status_report

    def get_available_providers(self) -> List[str]:
        """Get list of currently available providers"""
        return [p.value for p in self.fallback_order if self._is_provider_healthy(p)]
