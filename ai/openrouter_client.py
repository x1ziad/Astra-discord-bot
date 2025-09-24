"""
OpenRouter AI Client for Astra Bot
Provides access to multiple AI models through OpenRouter API
Enhanced with context awareness and conversation understanding
"""

import asyncio
import logging
import aiohttp
import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

# Import model mapping
try:
    from ai.model_mapping import normalize_model_id, get_model_display_name
except ImportError:
    # Fallback if model_mapping not available
    def normalize_model_id(model_id: str) -> str:
        """Fallback model normalization"""
        if not model_id:
            return "anthropic/claude-3-haiku"
        
        model_id = model_id.strip()
        
        # Handle the specific case that's causing issues
        if model_id == "xAI: Grok Code Fast 1":
            return "x-ai/grok-code-fast-1"
        
        # If it's already in API format, return as-is
        if "/" in model_id:
            return model_id
        
        return "anthropic/claude-3-haiku"  # Safe fallback
    
    def get_model_display_name(model_id: str) -> str:
        return model_id

# Import the enhanced AIResponse from universal client
try:
    from ai.universal_ai_client import AIResponse, ConversationContext
except ImportError:
    # Fallback if universal client not available
    @dataclass
    class AIResponse:
        content: str
        model: str
        usage: Dict[str, Any]
        metadata: Dict[str, Any]
        created_at: datetime


logger = logging.getLogger("astra.openrouter_client")


class OpenRouterClient:
    """OpenRouter API client for AI interactions"""

    def __init__(self, openrouter_api_key: str = None, openai_api_key: str = None):
        self.openrouter_api_key = openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"

        # Default model configuration
        self.default_model = "anthropic/claude-3-haiku"
        self.max_tokens = 2000
        self.temperature = 0.7

        # Session for HTTP requests
        self.session = None

    def is_available(self) -> bool:
        """Check if the OpenRouter client is properly configured"""
        return bool(self.openrouter_api_key)

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def _ensure_session(self):
        """Ensure HTTP session is available"""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def generate_response(
        self,
        message: str,
        context: Optional[List[Dict[str, str]]] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        user_id: Optional[int] = None,
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
        **kwargs,
    ) -> AIResponse:
        """Generate AI response using OpenRouter API with enhanced context support"""

        await self._ensure_session()

        if not self.is_available():
            raise ValueError("OpenRouter API key not configured")

        # Prepare request
        raw_model = model or self.default_model
        normalized_model = normalize_model_id(raw_model)
        
        # Log model conversion if it was changed
        if raw_model != normalized_model:
            logger.info(f"Converted model ID '{raw_model}' to '{normalized_model}'")
        
        model = normalized_model
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature or self.temperature

        # Build messages array with enhanced context awareness
        messages = []

        # Add enhanced system prompt if context available
        if context:
            messages.extend(context)
        else:
            # Concise system message for faster responses
            messages.append(
                {
                    "role": "system",
                    "content": "You are Astra, a helpful AI assistant for Discord. Be natural, engaging, and context-aware.",
                }
            )

        messages.append({"role": "user", "content": message})

        # Request payload
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }

        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/x1ziad/Astra-discord-bot",
            "X-Title": "Astra Discord Bot",
        }

        try:
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:

                if response.status != 200:
                    error_text = await response.text()
                    logger.error(
                        f"OpenRouter API error {response.status}: {error_text}"
                    )
                    raise Exception(
                        f"OpenRouter API error: {response.status} - {error_text}"
                    )

                result = await response.json()

                # Extract response content
                content = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})

                # Enhanced metadata for better tracking
                metadata = {
                    "provider": "openrouter",
                    "response_id": result.get("id"),
                    "finish_reason": result["choices"][0].get("finish_reason"),
                    "context_messages_used": len(messages),
                    "model_used": model,
                    "temperature_used": temperature,
                    "max_tokens_used": max_tokens,
                }

                # Add user context to metadata if available
                if user_id:
                    metadata["user_id"] = user_id
                if guild_id:
                    metadata["guild_id"] = guild_id
                if channel_id:
                    metadata["channel_id"] = channel_id

                return AIResponse(
                    content=content,
                    model=model,
                    provider="openrouter",
                    usage=usage,
                    metadata=metadata,
                    created_at=datetime.now(),
                )

        except asyncio.TimeoutError:
            logger.error("OpenRouter API request timed out")
            raise Exception("OpenRouter API request timed out")
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            raise

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from OpenRouter"""

        await self._ensure_session()

        if not self.is_available():
            return []

        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with self.session.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:

                if response.status == 200:
                    result = await response.json()
                    return result.get("data", [])
                else:
                    logger.warning(f"Failed to fetch models: {response.status}")
                    return []

        except Exception as e:
            logger.error(f"Error fetching models: {e}")
            return []

    async def test_connection(self) -> bool:
        """Test connection to OpenRouter API"""

        if not self.is_available():
            return False

        try:
            response = await self.generate_response(
                "Hello! This is a test message. Please respond with 'Test successful!'",
                max_tokens=50,
            )
            return bool(response.content)
        except Exception as e:
            logger.error(f"OpenRouter connection test failed: {e}")
            return False

    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None


# Convenience function for backward compatibility
async def create_openrouter_client(api_key: str = None) -> OpenRouterClient:
    """Create and return an OpenRouter client"""
    client = OpenRouterClient(openrouter_api_key=api_key)
    await client._ensure_session()
    return client


if __name__ == "__main__":
    # Test the OpenRouter client
    async def test():
        client = OpenRouterClient()
        if client.is_available():
            print("OpenRouter client configured successfully")
            try:
                response = await client.generate_response("Hello, how are you?")
                print(f"Response: {response.content}")
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("OpenRouter API key not configured")

        await client.close()

    asyncio.run(test())
