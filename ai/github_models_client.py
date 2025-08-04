"""
GitHub Models AI Client for Astra Bot
Integrates with GitHub Models API using DeepSeek R1 and other models
"""

import os
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime

# GitHub Models / Azure AI Inference
try:
    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
    from azure.core.credentials import AzureKeyCredential

    GITHUB_MODELS_AVAILABLE = True
except ImportError:
    GITHUB_MODELS_AVAILABLE = False

# Fallback to OpenAI
try:
    import openai

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
            self.timestamp = datetime.utcnow()


class GitHubModelsClient:
    """GitHub Models AI client with fallback support"""

    def __init__(self, github_token: str = None, openai_api_key: str = None):
        self.logger = logging.getLogger("astra.github_models")

        # GitHub Models configuration
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.github_endpoint = "https://models.github.ai/inference"
        self.github_model = "deepseek/DeepSeek-R1-0528"

        # OpenAI fallback configuration
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.openai_model = "gpt-4"

        # Client instances
        self.github_client = None
        self.openai_client = None

        # Initialize clients
        self._initialize_clients()

        # Configuration
        self.max_tokens = 2000
        self.temperature = 0.7
        self.default_provider = "github" if self.github_client else "openai"

        self.logger.info(
            f"GitHub Models client initialized (default: {self.default_provider})"
        )

    def _initialize_clients(self):
        """Initialize AI client connections"""
        # Try GitHub Models first
        if GITHUB_MODELS_AVAILABLE and self.github_token:
            try:
                self.github_client = ChatCompletionsClient(
                    endpoint=self.github_endpoint,
                    credential=AzureKeyCredential(self.github_token),
                )
                self.logger.info("✅ GitHub Models client initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize GitHub Models client: {e}")
                self.github_client = None

        # Initialize OpenAI fallback
        if OPENAI_AVAILABLE and self.openai_api_key:
            try:
                openai.api_key = self.openai_api_key
                self.openai_client = True  # OpenAI uses global config
                self.logger.info("✅ OpenAI fallback client initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI client: {e}")
                self.openai_client = None

    def is_available(self) -> bool:
        """Check if any AI client is available"""
        return self.github_client is not None or self.openai_client is not None

    def get_available_provider(self) -> Optional[str]:
        """Get the first available provider"""
        if self.github_client:
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
        if provider == "github" and self.github_client:
            return await self._github_chat_completion(
                messages, model, max_tokens, temperature
            )

        # Fall back to OpenAI
        elif provider == "openai" and self.openai_client:
            return await self._openai_chat_completion(
                messages, model, max_tokens, temperature
            )

        # Auto-fallback
        elif self.github_client:
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
        """GitHub Models chat completion"""
        try:
            # Convert messages to GitHub Models format
            ai_messages = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")

                if role == "system":
                    ai_messages.append(SystemMessage(content))
                elif role == "user":
                    ai_messages.append(UserMessage(content))
                elif role == "assistant":
                    ai_messages.append(AssistantMessage(content))

            # Use provided parameters or defaults
            model = model or self.github_model
            max_tokens = max_tokens or self.max_tokens
            temperature = temperature or self.temperature

            self.logger.debug(
                f"GitHub Models request: {model}, tokens: {max_tokens}, temp: {temperature}"
            )

            # Make API call
            response = self.github_client.complete(
                messages=ai_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                model=model,
            )

            # Extract response content
            content = response.choices[0].message.content
            finish_reason = getattr(response.choices[0], "finish_reason", None)

            # Calculate tokens used (approximate)
            tokens_used = getattr(response, "usage", {}).get("total_tokens", None)

            return AIResponse(
                content=content,
                model=model,
                provider="github",
                tokens_used=tokens_used,
                finish_reason=finish_reason,
            )

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

            # Make async API call
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            # Extract response content
            content = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason
            tokens_used = response.usage.total_tokens

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
            "github_available": self.github_client is not None,
            "openai_available": self.openai_client is not None,
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
