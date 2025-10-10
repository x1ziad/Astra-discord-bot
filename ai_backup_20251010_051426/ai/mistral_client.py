#!/usr/bin/env python3
"""
Mistral AI Client
Direct integration with Mistral AI using their official SDK
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from mistralai import Mistral

logger = logging.getLogger("astra.mistral_client")


@dataclass
class MistralResponse:
    """Mistral AI response wrapper"""

    content: str
    model: str
    usage: Dict[str, Any]
    finish_reason: str
    success: bool = True


class MistralClient:
    """Direct Mistral AI client using official SDK"""

    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment variables")

        self.client = Mistral(api_key=self.api_key)
        self.default_model = os.getenv("AI_MODEL", "mistral-large-latest")
        self.max_tokens = int(os.getenv("AI_MAX_TOKENS", "1000"))

        logger.info(f"Mistral client initialized with model: {self.default_model}")

    async def generate_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs,
    ) -> MistralResponse:
        """
        Generate response using Mistral AI

        Args:
            prompt: The input prompt
            model: Model to use (optional)
            max_tokens: Maximum tokens to generate
            temperature: Response creativity (0.0-1.0)

        Returns:
            MistralResponse with content and metadata
        """
        try:
            model = model or self.default_model
            max_tokens = max_tokens or self.max_tokens

            logger.debug(f"Generating response with model: {model}")

            # Prepare messages in the correct format
            messages = [
                {
                    "role": "user",
                    "content": prompt,
                }
            ]

            # Make the API call
            chat_response = self.client.chat.complete(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )

            # Extract response data
            choice = chat_response.choices[0]
            content = choice.message.content
            finish_reason = choice.finish_reason

            # Extract usage information
            usage = {
                "prompt_tokens": chat_response.usage.prompt_tokens,
                "completion_tokens": chat_response.usage.completion_tokens,
                "total_tokens": chat_response.usage.total_tokens,
            }

            logger.info(
                f"Mistral response generated successfully. Tokens: {usage['total_tokens']}"
            )

            return MistralResponse(
                content=content,
                model=model,
                usage=usage,
                finish_reason=finish_reason,
                success=True,
            )

        except Exception as e:
            logger.error(f"Mistral API error: {str(e)}")
            return MistralResponse(
                content=f"Error: {str(e)}",
                model=model or self.default_model,
                usage={},
                finish_reason="error",
                success=False,
            )

    def test_connection(self) -> bool:
        """Test the Mistral API connection"""
        try:
            response = self.client.chat.complete(
                model=self.default_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10,
            )
            return True
        except Exception as e:
            logger.error(f"Mistral connection test failed: {str(e)}")
            return False


# Async wrapper for compatibility
class AsyncMistralClient:
    """Async wrapper for Mistral client"""

    def __init__(self):
        self.client = MistralClient()

    async def generate_response(self, *args, **kwargs) -> MistralResponse:
        """Async wrapper for generate_response"""
        loop = asyncio.get_event_loop()

        # Run the sync method in a thread pool
        return await loop.run_in_executor(
            None, lambda: asyncio.run(self._sync_generate(*args, **kwargs))
        )

    def _sync_generate(self, *args, **kwargs) -> MistralResponse:
        """Sync wrapper for the actual generation"""
        return asyncio.run(self.client.generate_response(*args, **kwargs))


if __name__ == "__main__":
    # Test script
    async def test_mistral():
        client = AsyncMistralClient()
        response = await client.generate_response(
            "What is the best French cheese?", max_tokens=50
        )
        print(f"Response: {response.content}")
        print(f"Model: {response.model}")
        print(f"Usage: {response.usage}")

    asyncio.run(test_mistral())
