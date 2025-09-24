"""
Performance-optimized Universal AI Client
Focuses on speed, connection pooling, and reduced latency
"""

import asyncio
import aiohttp
import json
import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import weakref

logger = logging.getLogger("astra.optimized_ai_client")

# Global session pool for connection reuse
_session_pool: Optional[aiohttp.ClientSession] = None
_session_refs = weakref.WeakSet()


async def get_shared_session() -> aiohttp.ClientSession:
    """Get or create shared HTTP session with optimized settings"""
    global _session_pool

    if _session_pool is None or _session_pool.closed:
        # Optimized connector settings
        connector = aiohttp.TCPConnector(
            limit=100,  # Total connection pool size
            limit_per_host=30,  # Per-host connection limit
            ttl_dns_cache=300,  # DNS cache TTL
            use_dns_cache=True,
            keepalive_timeout=30,  # Keep connections alive
            enable_cleanup_closed=True,
        )

        # Optimized timeout settings
        timeout = aiohttp.ClientTimeout(
            total=15,  # Reduced from 30s
            connect=5,  # Connection timeout
            sock_read=10,  # Socket read timeout
        )

        _session_pool = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                "User-Agent": "AstraBot-Optimized/2.0",
                "Connection": "keep-alive",
            },
        )

        _session_refs.add(_session_pool)
        logger.info("🚀 Created optimized HTTP session with connection pooling")

    return _session_pool


async def cleanup_session():
    """Cleanup global session - call on bot shutdown"""
    global _session_pool
    if _session_pool and not _session_pool.closed:
        await _session_pool.close()
        logger.info("🧹 Cleaned up HTTP session")


@dataclass
class OptimizedAIResponse:
    """Lightweight response object"""

    content: str
    usage: Dict[str, int] = None
    response_time: float = 0
    provider: str = "openrouter"


class OptimizedUniversalAIClient:
    """High-performance AI client with aggressive optimizations"""

    def __init__(self, api_key: str = None, model: str = None, **kwargs):
        self.api_key = api_key
        self.model = model or "anthropic/claude-3-haiku"  # Fast model default

        # Performance settings
        self.max_tokens = kwargs.get("max_tokens", 1000)  # Reduced for speed
        self.temperature = kwargs.get("temperature", 0.7)

        # Optimized settings for speed
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/x1ziad/Astra-discord-bot",
            "X-Title": "Astra Discord Bot",
            "Content-Type": "application/json",
        }

        # Lightweight context management
        self.context_cache = {}
        self.max_context_size = 6  # Reduced for speed

        logger.info("⚡ Optimized AI Client initialized")

    def is_available(self) -> bool:
        """Quick availability check"""
        return bool(self.api_key)

    def _build_lightweight_messages(
        self, message: str, user_id: int = None
    ) -> List[Dict[str, str]]:
        """Build minimal message structure for speed"""
        messages = []

        # Minimal system prompt for speed
        messages.append(
            {
                "role": "system",
                "content": "You are Astra, a helpful AI assistant. Respond concisely and naturally.",
            }
        )

        # Add lightweight context if available
        if user_id and user_id in self.context_cache:
            recent_context = self.context_cache[user_id][-2:]  # Last 2 messages only
            messages.extend(recent_context)

        # Current message
        messages.append({"role": "user", "content": message})

        return messages

    def _update_context(self, user_id: int, user_msg: str, ai_response: str):
        """Lightweight context update"""
        if user_id not in self.context_cache:
            self.context_cache[user_id] = []

        context = self.context_cache[user_id]
        context.extend(
            [
                {"role": "user", "content": user_msg},
                {"role": "assistant", "content": ai_response},
            ]
        )

        # Keep only recent messages for speed
        if len(context) > self.max_context_size:
            self.context_cache[user_id] = context[-self.max_context_size :]

    async def generate_response(
        self,
        message: str,
        context: Dict[str, Any] = None,
        user_id: int = None,
        **kwargs,
    ) -> OptimizedAIResponse:
        """Generate AI response with maximum speed optimization"""

        start_time = time.time()

        # Validate input
        if not message or not isinstance(message, str):
            raise ValueError("Message must be a non-empty string")

        if not self.api_key:
            raise ValueError("API key is required for AI responses")

        # Get shared session for connection reuse
        session = await get_shared_session()

        # Build minimal payload for speed
        messages = self._build_lightweight_messages(message, user_id)

        payload = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "stream": False,
            # Speed optimizations
            "top_p": 0.9,  # Faster sampling
            "frequency_penalty": 0,
            "presence_penalty": 0,
        }

        url = f"{self.base_url}/chat/completions"

        try:
            # Use session with connection pooling
            async with session.post(
                url, json=payload, headers=self.headers
            ) as response:

                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"API error {response.status}: {error_text}")
                    raise Exception(f"API error: {response.status}")

                result = await response.json()

                # Safely extract content with proper validation
                if not result or not isinstance(result, dict):
                    raise Exception("Invalid API response format")

                choices = result.get("choices", [])
                if not choices or not isinstance(choices, list) or len(choices) == 0:
                    raise Exception("No choices in API response")

                first_choice = choices[0]
                if not isinstance(first_choice, dict):
                    raise Exception("Invalid choice format in API response")

                message_data = first_choice.get("message", {})
                if not isinstance(message_data, dict):
                    raise Exception("Invalid message format in API response")

                content = message_data.get("content", "")
                usage = result.get("usage", {})

                response_time = (time.time() - start_time) * 1000

                # Update lightweight context
                if user_id:
                    self._update_context(user_id, message, content)

                logger.debug(f"⚡ Response generated in {response_time:.0f}ms")

                return OptimizedAIResponse(
                    content=content,
                    usage=usage,
                    response_time=response_time,
                    provider="openrouter-optimized",
                )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"AI request failed after {response_time:.0f}ms: {e}")
            raise


class FastConsolidatedEngine:
    """Ultra-fast consolidated engine using optimized client"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

        # Initialize optimized client
        api_key = self.config.get("openrouter_api_key") or self.config.get("ai_api_key")

        if api_key:
            self.client = OptimizedUniversalAIClient(
                api_key=api_key,
                model="anthropic/claude-3-haiku",  # Fast model
                max_tokens=800,  # Reduced for speed
            )
            logger.info("🚀 Fast Consolidated Engine initialized")
        else:
            self.client = None
            logger.warning("⚠️ No API key - Fast engine unavailable")

    def is_available(self) -> bool:
        """Check if fast engine is ready"""
        return self.client and self.client.is_available()

    async def process_conversation(
        self,
        message: str,
        user_id: int,
        guild_id: int = None,
        channel_id: int = None,
        **kwargs,
    ) -> str:
        """Process conversation with maximum speed"""

        if not self.is_available():
            return "AI service temporarily unavailable"

        try:
            response = await self.client.generate_response(
                message=message, user_id=user_id, **kwargs
            )

            return response.content

        except Exception as e:
            logger.error(f"Fast conversation processing failed: {e}")
            return "I'm having trouble processing that request right now."


# Global optimized engine instance
_optimized_engine: Optional[FastConsolidatedEngine] = None


def get_fast_engine(config: Dict[str, Any] = None) -> FastConsolidatedEngine:
    """Get or create optimized engine instance"""
    global _optimized_engine

    if _optimized_engine is None:
        _optimized_engine = FastConsolidatedEngine(config)

    return _optimized_engine


async def cleanup_optimized_resources():
    """Cleanup function for bot shutdown"""
    await cleanup_session()
    logger.info("🧹 Optimized AI resources cleaned up")
