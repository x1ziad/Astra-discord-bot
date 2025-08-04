"""
Universal AI Client for Astra Bot
Works with any OpenAI-compatible API endpoint
"""

import os
import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timezone

# Fallback to OpenAI for compatibility if needed
try:
    from openai import AsyncOpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger("astra.universal_ai")


@dataclass
class AIResponse:
    """Standardized AI response format"""

    content: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    finish_reason: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


class UniversalAIClient:
    """Universal AI client that works with any OpenAI-compatible API"""

    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        model: str = None,
        provider_name: str = "universal",
    ):
        self.logger = logging.getLogger("astra.universal_ai")

        # Universal configuration
        self.api_key = (
            api_key or os.getenv("AI_API_KEY") or os.getenv("UNIVERSAL_AI_KEY")
        )
        self.base_url = base_url or os.getenv(
            "AI_BASE_URL", "https://api.openai.com/v1"
        )
        self.model = model or os.getenv("AI_MODEL", "gpt-3.5-turbo")
        self.provider_name = provider_name

        # Ensure base_url ends with correct path
        if not self.base_url.endswith("/chat/completions"):
            if self.base_url.endswith("/v1"):
                self.base_url += "/chat/completions"
            elif self.base_url.endswith("/"):
                self.base_url += "v1/chat/completions"
            else:
                self.base_url += "/v1/chat/completions"

        # Configuration
        self.max_tokens = int(os.getenv("AI_MAX_TOKENS", "2000"))
        self.temperature = float(os.getenv("AI_TEMPERATURE", "0.7"))

        # Status
        self.available = bool(self.api_key)

        self.logger.info(f"Universal AI client initialized")
        self.logger.info(f"Provider: {self.provider_name}")
        self.logger.info(f"Endpoint: {self.base_url}")
        self.logger.info(f"Model: {self.model}")
        self.logger.info(f"Available: {self.available}")

    def is_available(self) -> bool:
        """Check if AI client is available"""
        return self.available

    def get_available_provider(self) -> Optional[str]:
        """Get the available provider"""
        return self.provider_name if self.available else None

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        max_tokens: int = None,
        temperature: float = None,
        **kwargs,
    ) -> AIResponse:
        """
        Generate chat completion using the universal API

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (optional)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            AIResponse object with generated content
        """
        if not self.available:
            raise RuntimeError("No AI provider available - missing API key")

        return await self._universal_chat_completion(
            messages, model, max_tokens, temperature, **kwargs
        )

    async def _universal_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        max_tokens: int = None,
        temperature: float = None,
        **kwargs,
    ) -> AIResponse:
        """Universal chat completion using aiohttp"""
        try:
            # Use provided parameters or defaults
            model = model or self.model
            max_tokens = max_tokens or self.max_tokens
            temperature = temperature or self.temperature

            # Prepare request headers
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            # Add optional headers if provided
            if "HTTP-Referer" in kwargs:
                headers["HTTP-Referer"] = kwargs["HTTP-Referer"]
            if "X-Title" in kwargs:
                headers["X-Title"] = kwargs["X-Title"]

            # Prepare request data
            data = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

            # Add any additional parameters
            for key, value in kwargs.items():
                if key not in ["HTTP-Referer", "X-Title"] and value is not None:
                    data[key] = value

            self.logger.debug(
                f"AI request: {model}, tokens: {max_tokens}, temp: {temperature}"
            )
            self.logger.debug(f"Endpoint: {self.base_url}")

            # Make async HTTP request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=45),  # Longer timeout for AI
                ) as response:

                    if response.status == 200:
                        result = await response.json()

                        # Extract response content
                        content = result["choices"][0]["message"]["content"]
                        finish_reason = result["choices"][0].get("finish_reason")
                        tokens_used = result.get("usage", {}).get("total_tokens")

                        return AIResponse(
                            content=content,
                            model=result.get("model", model),
                            provider=self.provider_name,
                            tokens_used=tokens_used,
                            finish_reason=finish_reason,
                        )
                    else:
                        error_text = await response.text()
                        self.logger.error(f"API Error {response.status}: {error_text}")
                        raise RuntimeError(
                            f"AI API error {response.status}: {error_text}"
                        )

        except Exception as e:
            self.logger.error(f"AI API error: {e}")
            raise RuntimeError(f"AI API error: {e}")

    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Simple text generation interface"""
        messages = [{"role": "user", "content": prompt}]
        response = await self.chat_completion(messages, **kwargs)
        return response.content

    async def analyze_text(
        self, text: str, analysis_type: str = "general", **kwargs
    ) -> str:
        """Analyze text with specific focus"""
        prompt = f"Please analyze the following text with focus on {analysis_type}:\n\n{text}"
        return await self.generate_text(prompt, **kwargs)

    def get_status(self) -> Dict[str, Any]:
        """Get client status information"""
        return {
            "provider": self.provider_name,
            "available": "Available" if self.available else "Not configured",
            "model": self.model,
            "endpoint": self.base_url,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

    async def test_connection(self) -> Dict[str, Any]:
        """Test the API connection"""
        if not self.available:
            return {
                "success": False,
                "error": "No API key configured",
                "status": "unavailable",
            }

        try:
            response = await self.generate_text(
                "Hello! Please respond with just 'Connection successful'"
            )
            return {"success": True, "response": response[:100], "status": "connected"}
        except Exception as e:
            return {"success": False, "error": str(e), "status": "error"}


# Global client instance
_global_client: Optional[UniversalAIClient] = None


def get_ai_client() -> UniversalAIClient:
    """Get global AI client instance"""
    global _global_client
    if _global_client is None:
        _global_client = UniversalAIClient()
    return _global_client


def initialize_ai_client(
    api_key: str = None,
    base_url: str = None,
    model: str = None,
    provider_name: str = "universal",
) -> UniversalAIClient:
    """Initialize global AI client with specific credentials"""
    global _global_client
    _global_client = UniversalAIClient(api_key, base_url, model, provider_name)
    return _global_client


# Convenience functions
async def chat(messages: List[Dict[str, str]], **kwargs) -> AIResponse:
    """Quick chat completion"""
    client = get_ai_client()
    return await client.chat_completion(messages, **kwargs)


async def ask(question: str, **kwargs) -> str:
    """Quick question asking"""
    client = get_ai_client()
    return await client.generate_text(question, **kwargs)


if __name__ == "__main__":
    # Test the client
    async def test_client():
        print("🧪 Testing Universal AI Client...")

        # Test with the provided API key
        test_key = (
            "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"
        )

        # Test different possible endpoints
        endpoints = [
            "https://openrouter.ai/api/v1",
            "https://api.openai.com/v1",
            "https://api.anthropic.com/v1",  # Example
        ]

        for endpoint in endpoints:
            print(f"\n🔍 Testing endpoint: {endpoint}")
            client = UniversalAIClient(
                api_key=test_key,
                base_url=endpoint,
                model="gpt-3.5-turbo",
                provider_name="test",
            )

            print(f"Status: {client.get_status()}")

            if client.is_available():
                try:
                    test_result = await client.test_connection()
                    if test_result["success"]:
                        print(f"✅ Connection successful!")
                        print(f"Response: {test_result['response']}")
                        break
                    else:
                        print(f"❌ Connection failed: {test_result['error']}")
                except Exception as e:
                    print(f"❌ Test error: {e}")
            else:
                print("❌ Client not available")

    asyncio.run(test_client())
