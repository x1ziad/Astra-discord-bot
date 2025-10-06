"""
Google Gemini AI Client for Astra Bot
Provides Google Generative AI integration using the official Google GenAI SDK
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold

    GOOGLE_GENAI_AVAILABLE = True
except ImportError:
    GOOGLE_GENAI_AVAILABLE = False
    logging.warning("Google GenerativeAI library not available")

logger = logging.getLogger("astra.google_gemini_client")


class GoogleGeminiClient:
    """
    Google Gemini AI Client using the official Google GenerativeAI SDK
    Supports text generation with advanced safety settings and conversation context
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Google Gemini client"""
        self.api_key = (
            api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        )
        self.available = GOOGLE_GENAI_AVAILABLE and bool(self.api_key)
        self.model = None

        if self.available:
            try:
                # Configure the API key
                genai.configure(api_key=self.api_key)

                # Initialize the model with safety settings
                self.model = genai.GenerativeModel(
                    model_name="models/gemini-2.5-flash",
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    },
                )

                logger.info("✅ Google Gemini client initialized successfully")

            except Exception as e:
                logger.error(f"❌ Failed to initialize Google Gemini client: {e}")
                self.available = False
        else:
            logger.warning(
                "⚠️ Google Gemini client not available (missing API key or library)"
            )

    async def generate_response(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 8192,
        temperature: float = 0.7,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate a response using Google Gemini

        Args:
            prompt: The input prompt
            context: Conversation context (optional)
            max_tokens: Maximum tokens to generate
            temperature: Response creativity (0.0-1.0)
            **kwargs: Additional parameters

        Returns:
            Dict containing response and metadata
        """
        if not self.available:
            raise Exception("Google Gemini client not available")

        try:
            # Prepare the generation config
            # Ensure we have reasonable minimum output tokens for Google Gemini
            # Google Gemini needs at least 100 tokens to generate meaningful responses
            actual_max_tokens = max(max_tokens, 100)  # Minimum 100 tokens for output

            generation_config = genai.types.GenerationConfig(
                max_output_tokens=actual_max_tokens,
                temperature=temperature,
                top_p=kwargs.get("top_p", 0.95),
                top_k=kwargs.get("top_k", 64),
            )  # Build the full prompt with context if provided
            full_prompt = self._build_prompt_with_context(prompt, context)

            logger.info(
                f"🧠 Generating Gemini response (max_tokens: {max_tokens}, temp: {temperature})"
            )

            # Generate response using the model
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.model.generate_content(
                    full_prompt, generation_config=generation_config
                ),
            )

            # Handle response based on candidates structure
            finish_reason_map = {
                1: "stop",  # STOP
                2: "length",  # MAX_TOKENS
                3: "safety",  # SAFETY
                4: "recitation",  # RECITATION
                5: "other",  # OTHER
            }

            # Check if response has candidates and content
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                finish_reason_code = getattr(candidate, "finish_reason", 1)
                finish_reason = finish_reason_map.get(finish_reason_code, "unknown")

                # Get safety ratings from candidate
                safety_ratings = getattr(candidate, "safety_ratings", [])

                # Extract text content (don't use response.text when finish_reason=2)
                content = ""
                if hasattr(candidate, "content") and candidate.content:
                    if hasattr(candidate.content, "parts") and candidate.content.parts:
                        for part in candidate.content.parts:
                            if hasattr(part, "text") and part.text:
                                content += part.text

                # Only use response.text fallback if finish_reason is not MAX_TOKENS (2)
                if not content and finish_reason_code != 2:
                    try:
                        if hasattr(response, "text") and response.text:
                            content = response.text
                    except Exception as e:
                        logger.debug(f"Could not access response.text: {e}")

                content = content.strip()

                # Get usage information if available
                usage_metadata = {}
                if hasattr(response, "usage_metadata") and response.usage_metadata:
                    usage_metadata = {
                        "prompt_tokens": getattr(
                            response.usage_metadata, "prompt_token_count", 0
                        ),
                        "completion_tokens": getattr(
                            response.usage_metadata, "candidates_token_count", 0
                        ),
                        "total_tokens": getattr(
                            response.usage_metadata, "total_token_count", 0
                        ),
                    }

                # Handle different finish reasons
                if finish_reason == "length":
                    logger.warning(
                        f"⚠️ Gemini response truncated due to token limit (max_tokens: {max_tokens})"
                    )
                    # For MAX_TOKENS, provide a meaningful message if no content was returned
                    if not content:
                        content = "Response was cut off due to length limits. Please try a shorter prompt or increase max_tokens."
                elif finish_reason == "safety":
                    logger.warning(f"⚠️ Gemini response blocked by safety filters")
                    # Return safety message if no content
                    if not content:
                        content = "I apologize, but I cannot provide a response to that request due to safety guidelines."
                elif finish_reason == "stop":
                    logger.info(f"✅ Gemini response completed successfully")

                # Always return a response, even if content is empty
                if not content:
                    content = f"No response generated (finish_reason: {finish_reason})"

                if True:  # Always return response with content
                    result = {
                        "content": content,
                        "model": "models/gemini-1.5-flash",
                        "provider": "google",
                        "usage": usage_metadata,
                        "metadata": {
                            "temperature": temperature,
                            "max_tokens": max_tokens,
                            "finish_reason": finish_reason,
                            "safety_ratings": safety_ratings,
                            "created_at": datetime.now(timezone.utc).isoformat(),
                        },
                    }

                    logger.info(
                        f"✅ Gemini response generated ({len(content)} chars, finish_reason: {finish_reason})"
                    )
                    return result

            # Handle case where response was blocked or empty
            logger.warning(f"⚠️ Gemini response was empty or blocked")

            # Return a fallback response
            return {
                "content": "I apologize, but I cannot provide a response to that request. Please try rephrasing your question.",
                "model": "models/gemini-2.5-flash",
                "provider": "google",
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                },
                "metadata": {
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "finish_reason": "blocked",
                    "safety_ratings": safety_ratings,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "blocked": True,
                },
            }

        except Exception as e:
            error_str = str(e)

            # Handle quota exceeded errors gracefully
            if "429" in error_str and "quota" in error_str.lower():
                logger.warning(f"⚠️ Google Gemini quota exceeded: {error_str[:100]}...")
                return {
                    "content": "I'm temporarily unable to process requests due to API quota limits. Please try again later or use an alternative AI provider.",
                    "model": "models/gemini-2.5-flash",
                    "provider": "google",
                    "usage": {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0,
                    },
                    "metadata": {
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "finish_reason": "quota_exceeded",
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "error": "quota_exceeded",
                    },
                }

            logger.error(f"❌ Google Gemini API error: {e}")
            raise Exception(f"Google Gemini API error: {str(e)}")

    def _build_prompt_with_context(
        self, prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build a comprehensive prompt with context"""
        if not context:
            return prompt

        context_parts = []

        # Add system context if available
        if context.get("system_prompt"):
            context_parts.append(f"System Context: {context['system_prompt']}")

        # Add conversation history if available
        if context.get("conversation_history"):
            history = context["conversation_history"][-5:]  # Last 5 exchanges
            for exchange in history:
                if exchange.get("role") == "user":
                    context_parts.append(
                        f"Previous User: {exchange.get('content', '')}"
                    )
                elif exchange.get("role") == "assistant":
                    context_parts.append(
                        f"Previous Assistant: {exchange.get('content', '')}"
                    )

        # Add user context if available
        if context.get("user_info"):
            user_info = context["user_info"]
            if user_info.get("name"):
                context_parts.append(f"User Name: {user_info['name']}")
            if user_info.get("preferences"):
                context_parts.append(f"User Preferences: {user_info['preferences']}")

        # Combine context with prompt
        if context_parts:
            full_context = "\n".join(context_parts)
            return f"{full_context}\n\nCurrent Request: {prompt}"

        return prompt

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 8192,
        temperature: float = 0.7,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Chat completion interface compatible with OpenAI format

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Response creativity
            **kwargs: Additional parameters

        Returns:
            Dict containing response and metadata
        """
        if not self.available:
            raise Exception("Google Gemini client not available")

        try:
            # Convert messages to a single prompt
            prompt_parts = []

            for message in messages:
                role = message.get("role", "user")
                content = message.get("content", "")

                if role == "system":
                    prompt_parts.append(f"System: {content}")
                elif role == "user":
                    prompt_parts.append(f"Human: {content}")
                elif role == "assistant":
                    prompt_parts.append(f"Assistant: {content}")

            # Add the final instruction for the assistant to respond
            if prompt_parts:
                full_prompt = "\n\n".join(prompt_parts) + "\n\nAssistant:"
            else:
                full_prompt = "Human: Hello\n\nAssistant:"

            # Use the generate_response method
            return await self.generate_response(
                full_prompt, max_tokens=max_tokens, temperature=temperature, **kwargs
            )

        except Exception as e:
            logger.error(f"❌ Google Gemini chat completion error: {e}")
            raise Exception(f"Google Gemini chat completion error: {str(e)}")

    def get_available_models(self) -> List[str]:
        """Get list of available Gemini models"""
        if not self.available:
            return []

        try:
            # List available models
            models = []
            for model in genai.list_models():
                if "generateContent" in model.supported_generation_methods:
                    models.append(model.name.replace("models/", ""))
            return models
        except Exception as e:
            logger.warning(f"Could not fetch available models: {e}")
            return [
                "models/gemini-2.5-flash",
                "models/gemini-2.5-pro",
                "models/gemini-flash-latest",
            ]

    async def test_connection(self) -> bool:
        """Test the connection to Google Gemini API"""
        if not self.available:
            return False

        try:
            test_response = await self.generate_response(
                "Hello! Please respond with 'Connection successful' to test the API.",
                max_tokens=50,
                temperature=0.1,
            )

            success = "successful" in test_response.get("content", "").lower()
            logger.info(
                f"🧪 Google Gemini connection test: {'✅ PASSED' if success else '❌ FAILED'}"
            )
            return success

        except Exception as e:
            logger.error(f"❌ Google Gemini connection test failed: {e}")
            return False


# Global instance
google_gemini_client = GoogleGeminiClient()


async def get_gemini_response(
    prompt: str,
    context: Optional[Dict[str, Any]] = None,
    max_tokens: int = 8192,
    temperature: float = 0.7,
    **kwargs,
) -> Dict[str, Any]:
    """
    Convenience function for getting a Gemini response

    Args:
        prompt: The input prompt
        context: Optional conversation context
        max_tokens: Maximum tokens to generate
        temperature: Response creativity
        **kwargs: Additional parameters

    Returns:
        Response dictionary
    """
    return await google_gemini_client.generate_response(
        prompt=prompt,
        context=context,
        max_tokens=max_tokens,
        temperature=temperature,
        **kwargs,
    )


async def get_gemini_chat_completion(
    messages: List[Dict[str, str]],
    max_tokens: int = 8192,
    temperature: float = 0.7,
    **kwargs,
) -> Dict[str, Any]:
    """
    Convenience function for Gemini chat completion

    Args:
        messages: List of message dictionaries
        max_tokens: Maximum tokens to generate
        temperature: Response creativity
        **kwargs: Additional parameters

    Returns:
        Response dictionary
    """
    return await google_gemini_client.chat_completion(
        messages=messages, max_tokens=max_tokens, temperature=temperature, **kwargs
    )
