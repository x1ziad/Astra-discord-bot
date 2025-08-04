"""
GitHub Models AI Client for Astra Bot
Integrates with GitHub Models API using DeepSeek R1 and other models
"""

import os
import logging
import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timezone

# Fallback to OpenAI
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger("astra.github_models")


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


class GitHubModelsClient:
    """GitHub Models AI client with fallback support"""

    def __init__(self, github_token: str = None, openai_api_key: str = None):
        self.logger = logging.getLogger("astra.github_models")

        # GitHub Models configuration
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.github_endpoint = "https://models.github.ai/inference/chat/completions"
        self.github_model = "deepseek/DeepSeek-R1-0528"

        # OpenAI fallback configuration
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.openai_model = "gpt-4"

        # Client instances
        self.github_available = bool(self.github_token)
        self.openai_client = None

        # Initialize clients
        self._initialize_clients()

        # Configuration
        self.max_tokens = 2000
        self.temperature = 0.7
        self.default_provider = "github" if self.github_available else "openai"

        self.logger.info(
            f"GitHub Models client initialized (default: {self.default_provider})"
        )

    def _initialize_clients(self):
        """Initialize AI client connections"""
        # Check GitHub Models availability
        if self.github_token:
            self.github_available = True
            self.logger.info("✅ GitHub Models client configured")
        else:
            self.github_available = False
            self.logger.warning("❌ GitHub token not available")

        # Initialize OpenAI fallback
        if OPENAI_AVAILABLE and self.openai_api_key:
            try:
                self.openai_client = AsyncOpenAI(api_key=self.openai_api_key)
                self.logger.info("✅ OpenAI fallback client initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI client: {e}")
                self.openai_client = None
        else:
            self.logger.info("OpenAI not available (missing key or library)")

    def is_available(self) -> bool:
        """Check if any AI client is available"""
        return self.github_available or self.openai_client is not None

    def get_available_provider(self) -> Optional[str]:
        """Get the first available provider"""
        if self.github_available:
            return "github"
        elif self.openai_client:
            return "openai"
        return None

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        max_tokens: int = None,
        temperature: float = None,
        provider: str = None,
    ) -> AIResponse:
        """
        Generate chat completion using available AI provider

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (optional)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            provider: Force specific provider ('github' or 'openai')

        Returns:
            AIResponse object with generated content
        """
        # Determine provider
        if provider is None:
            provider = self.default_provider

        # Use GitHub Models if available and requested
        if provider == "github" and self.github_available:
            return await self._github_chat_completion(
                messages, model, max_tokens, temperature
            )

        # Fall back to OpenAI
        elif provider == "openai" and self.openai_client:
            return await self._openai_chat_completion(
                messages, model, max_tokens, temperature
            )

        # Auto-fallback
        elif self.github_available:
            return await self._github_chat_completion(
                messages, model, max_tokens, temperature
            )
        elif self.openai_client:
            return await self._openai_chat_completion(
                messages, model, max_tokens, temperature
            )

        else:
            raise RuntimeError("No AI provider available")

    async def _github_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        max_tokens: int = None,
        temperature: float = None,
    ) -> AIResponse:
        """GitHub Models chat completion using REST API"""
        try:
            # Use provided parameters or defaults
            model = model or self.github_model
            max_tokens = max_tokens or self.max_tokens
            temperature = temperature or self.temperature

            self.logger.debug(
                f"GitHub Models request: {model}, tokens: {max_tokens}, temp: {temperature}"
            )

            # Prepare request payload
            payload = {
                "messages": messages,
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.github_token}"
            }

            # Make HTTP request to GitHub Models API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.github_endpoint,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract response content
                        content = data["choices"][0]["message"]["content"]
                        finish_reason = data["choices"][0].get("finish_reason")
                        tokens_used = data.get("usage", {}).get("total_tokens")

                        return AIResponse(
                            content=content,
                            model=model,
                            provider="github",
                            tokens_used=tokens_used,
                            finish_reason=finish_reason,
                        )
                    else:
                        error_text = await response.text()
                        self.logger.error(f"GitHub Models API error {response.status}: {error_text}")
                        raise RuntimeError(f"GitHub Models API error {response.status}: {error_text}")

        except Exception as e:
            self.logger.error(f"GitHub Models API error: {e}")
            # Try OpenAI fallback if available
            if self.openai_client:
                self.logger.info("Falling back to OpenAI...")
                return await self._openai_chat_completion(
                    messages, model, max_tokens, temperature
                )
            else:
                raise RuntimeError(f"GitHub Models API error: {e}")

    async def _openai_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        max_tokens: int = None,
        temperature: float = None,
    ) -> AIResponse:
        """OpenAI chat completion (fallback)"""
        try:
            # Use provided parameters or defaults
            model = model or self.openai_model
            max_tokens = max_tokens or self.max_tokens
            temperature = temperature or self.temperature

            self.logger.debug(
                f"OpenAI request: {model}, tokens: {max_tokens}, temp: {temperature}"
            )

            # Make async API call using modern OpenAI client
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            # Extract response content
            content = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason
            tokens_used = response.usage.total_tokens if response.usage else None

            return AIResponse(
                content=content,
                model=model,
                provider="openai",
                tokens_used=tokens_used,
                finish_reason=finish_reason,
            )

        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"OpenAI API error: {e}")

    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Simple text generation interface"""
        messages = [{"role": "user", "content": prompt}]
        response = await self.chat_completion(messages, **kwargs)
        return response.content

    async def analyze_text(self, text: str, analysis_type: str = "general") -> str:
        """Analyze text with specific focus"""
        prompt = f"Please analyze the following text with focus on {analysis_type}:\n\n{text}"
        return await self.generate_text(prompt)

    def get_status(self) -> Dict[str, Any]:
        """Get client status information"""
        return {
            "github_models": "Available" if self.github_available else "Not configured",
            "openai": "Available" if self.openai_client else "Not configured",
            "default_provider": self.default_provider,
            "github_model": self.github_model,
            "openai_model": self.openai_model,
            "endpoint": self.github_endpoint,
        }


# Global client instance
_global_client: Optional[GitHubModelsClient] = None


def get_ai_client() -> GitHubModelsClient:
    """Get global AI client instance"""
    global _global_client
    if _global_client is None:
        _global_client = GitHubModelsClient()
    return _global_client


def initialize_ai_client(
    github_token: str = None, openai_api_key: str = None
) -> GitHubModelsClient:
    """Initialize global AI client with specific credentials"""
    global _global_client
    _global_client = GitHubModelsClient(github_token, openai_api_key)
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
        print("🧪 Testing GitHub Models Client...")

        client = GitHubModelsClient()
        print(f"Status: {client.get_status()}")

        if client.is_available():
            try:
                response = await client.generate_text("What is the capital of France?")
                print(f"✅ Response: {response}")
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print("❌ No AI providers available")

    asyncio.run(test_client())
