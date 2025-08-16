"""
Gemini Image Generator for Astra Bot
Isolated, robust image generation system using Google's Gemini AI
"""

import asyncio
import logging
import os
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timezone, timedelta
from io import BytesIO
import base64
import aiohttp
from PIL import Image
from dataclasses import dataclass, field
from enum import Enum
import json

# Google Gemini imports
try:
    from google import genai
    from google.genai import types

    GEMINI_AVAILABLE = True
except ImportError as e:
    GEMINI_AVAILABLE = False
    genai = None
    types = None

# Set up logging
logger = logging.getLogger("astra.gemini_image")


class ImageSize(Enum):
    """Supported image sizes"""

    SQUARE_HD = "1024x1024"
    PORTRAIT = "768x1024"
    LANDSCAPE = "1024x768"
    WIDE = "1024x576"


class ImageStyle(Enum):
    """Image generation styles"""

    REALISTIC = "realistic"
    ARTISTIC = "artistic"
    CARTOON = "cartoon"
    ANIME = "anime"
    PHOTOGRAPHIC = "photographic"
    ABSTRACT = "abstract"
    VINTAGE = "vintage"


@dataclass
class ImageGenerationRequest:
    """Image generation request data"""

    prompt: str
    user_id: int
    channel_id: int
    guild_id: Optional[int] = None
    size: ImageSize = ImageSize.SQUARE_HD
    style: ImageStyle = ImageStyle.REALISTIC
    num_images: int = 1
    enhance_prompt: bool = True
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ImageGenerationResult:
    """Image generation result data"""

    success: bool
    image_data: Optional[bytes] = None
    image_url: Optional[str] = None
    text_response: Optional[str] = None
    prompt_used: Optional[str] = None
    generation_time: Optional[float] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    provider: str = "Gemini"
    model: str = "gemini-2.0-flash-preview-image-generation"
    metadata: Dict[str, Any] = field(default_factory=dict)


class GeminiImageConfig:
    """Configuration for Gemini image generation"""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = "gemini-2.0-flash-preview-image-generation"
        self.max_retries = 3
        self.retry_delay = 2.0
        self.timeout = 60.0
        self.rate_limit_per_minute = 15
        self.rate_limit_per_hour = 100
        self.max_prompt_length = 2000

        # Style enhancement prompts
        self.style_prompts = {
            ImageStyle.REALISTIC: "photorealistic, highly detailed, sharp focus, professional photography, 8k resolution",
            ImageStyle.ARTISTIC: "artistic masterpiece, creative composition, vibrant colors, digital art, concept art",
            ImageStyle.CARTOON: "cartoon style, animated, colorful, friendly, cel-shaded, disney-style",
            ImageStyle.ANIME: "anime art style, manga aesthetic, vibrant colors, japanese animation style",
            ImageStyle.PHOTOGRAPHIC: "professional photography, DSLR quality, natural lighting, bokeh effect",
            ImageStyle.ABSTRACT: "abstract art, creative interpretation, modern art style, artistic composition",
            ImageStyle.VINTAGE: "vintage aesthetic, retro style, classic composition, nostalgic atmosphere",
        }


class GeminiImageGenerator:
    """
    Robust Gemini-based image generation system
    Isolated from main AI system with comprehensive error handling
    """

    def __init__(self, config: Optional[GeminiImageConfig] = None):
        self.config = config or GeminiImageConfig()
        self.logger = logging.getLogger("astra.gemini_image")
        self.client = None
        self.is_initialized = False

        # Rate limiting
        self.request_times: List[datetime] = []
        self.hourly_requests: List[datetime] = []

        # Statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_generation_time = 0.0

        # Initialize client
        self._initialize_client()

    def _initialize_client(self) -> bool:
        """Initialize the Gemini client"""
        try:
            if not GEMINI_AVAILABLE:
                self.logger.error(
                    "❌ Google Gemini SDK not available. Install with: pip install google-genai"
                )
                return False

            if not self.config.api_key:
                self.logger.error("❌ GEMINI_API_KEY environment variable not set")
                return False

            # Initialize Gemini client
            self.client = genai.Client(api_key=self.config.api_key)
            self.is_initialized = True

            self.logger.info("✅ Gemini Image Generator initialized successfully")
            self.logger.info(
                f"🔑 API Key configured: {self.config.api_key[:8]}...{self.config.api_key[-4:]}"
            )
            self.logger.info(f"🤖 Model: {self.config.model}")

            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Gemini client: {e}")
            self.is_initialized = False
            return False

    def is_available(self) -> bool:
        """Check if the generator is available and properly configured"""
        return self.is_initialized and self.client is not None and GEMINI_AVAILABLE

    def _check_rate_limits(self) -> Tuple[bool, Optional[str]]:
        """Check if request is within rate limits"""
        now = datetime.now(timezone.utc)

        # Clean old requests (older than 1 minute)
        self.request_times = [
            t for t in self.request_times if (now - t).total_seconds() < 60
        ]

        # Clean old hourly requests
        self.hourly_requests = [
            t for t in self.hourly_requests if (now - t).total_seconds() < 3600
        ]

        # Check per-minute limit
        if len(self.request_times) >= self.config.rate_limit_per_minute:
            return (
                False,
                f"Rate limit exceeded: {self.config.rate_limit_per_minute} requests per minute",
            )

        # Check per-hour limit
        if len(self.hourly_requests) >= self.config.rate_limit_per_hour:
            return (
                False,
                f"Rate limit exceeded: {self.config.rate_limit_per_hour} requests per hour",
            )

        return True, None

    def _enhance_prompt(self, prompt: str, style: ImageStyle) -> str:
        """Enhance the prompt with style-specific keywords"""
        if not prompt.strip():
            return prompt

        # Get style enhancement
        style_enhancement = self.config.style_prompts.get(style, "")

        # Combine prompt with style
        enhanced = f"{prompt.strip()}"
        if style_enhancement:
            enhanced += f", {style_enhancement}"

        # Ensure proper length
        if len(enhanced) > self.config.max_prompt_length:
            enhanced = enhanced[: self.config.max_prompt_length].rstrip()

        return enhanced

    async def generate_image(
        self, request: ImageGenerationRequest
    ) -> ImageGenerationResult:
        """
        Generate an image using Gemini AI

        Args:
            request: ImageGenerationRequest containing all generation parameters

        Returns:
            ImageGenerationResult with image data or error information
        """
        start_time = time.time()
        self.total_requests += 1

        try:
            # Validate request
            if not self.is_available():
                return ImageGenerationResult(
                    success=False,
                    error="Gemini Image Generator not available",
                    error_code="SERVICE_UNAVAILABLE",
                )

            # Check rate limits
            rate_ok, rate_error = self._check_rate_limits()
            if not rate_ok:
                return ImageGenerationResult(
                    success=False, error=rate_error, error_code="RATE_LIMITED"
                )

            # Validate prompt
            if not request.prompt.strip():
                return ImageGenerationResult(
                    success=False,
                    error="Prompt cannot be empty",
                    error_code="INVALID_PROMPT",
                )

            # Enhance prompt if requested
            final_prompt = request.prompt
            if request.enhance_prompt:
                final_prompt = self._enhance_prompt(request.prompt, request.style)

            self.logger.info(f"🎨 Generating image for user {request.user_id}")
            self.logger.info(f"📝 Original prompt: {request.prompt[:100]}...")
            self.logger.info(f"✨ Enhanced prompt: {final_prompt[:100]}...")

            # Record request for rate limiting
            now = datetime.now(timezone.utc)
            self.request_times.append(now)
            self.hourly_requests.append(now)

            # Generate image with Gemini
            result = await self._call_gemini_api(final_prompt)

            generation_time = time.time() - start_time
            self.total_generation_time += generation_time

            if result.success:
                self.successful_requests += 1
                self.logger.info(
                    f"✅ Image generated successfully in {generation_time:.2f}s"
                )
            else:
                self.failed_requests += 1
                self.logger.error(f"❌ Image generation failed: {result.error}")

            # Add metadata
            result.generation_time = generation_time
            result.prompt_used = final_prompt
            result.metadata.update(
                {
                    "original_prompt": request.prompt,
                    "enhanced_prompt": final_prompt,
                    "style": request.style.value,
                    "size": request.size.value,
                    "user_id": request.user_id,
                    "channel_id": request.channel_id,
                    "guild_id": request.guild_id,
                    "timestamp": now.isoformat(),
                    "model": self.config.model,
                }
            )

            return result

        except Exception as e:
            self.failed_requests += 1
            self.logger.error(
                f"💥 Critical error in image generation: {e}", exc_info=True
            )

            return ImageGenerationResult(
                success=False,
                error=f"Critical error: {str(e)}",
                error_code="CRITICAL_ERROR",
                generation_time=time.time() - start_time,
            )

    async def _call_gemini_api(self, prompt: str) -> ImageGenerationResult:
        """Make the actual API call to Gemini"""
        try:
            # Create the API request
            response = await asyncio.get_event_loop().run_in_executor(
                None, self._sync_gemini_call, prompt
            )

            if not response or not hasattr(response, "candidates"):
                return ImageGenerationResult(
                    success=False,
                    error="No response from Gemini API",
                    error_code="NO_RESPONSE",
                )

            # Extract image and text from response
            image_data = None
            text_response = None

            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    text_response = part.text
                elif part.inline_data is not None:
                    # Convert image data to bytes
                    image_data = part.inline_data.data

            if not image_data:
                return ImageGenerationResult(
                    success=False,
                    error="No image data in response",
                    error_code="NO_IMAGE_DATA",
                    text_response=text_response,
                )

            return ImageGenerationResult(
                success=True, image_data=image_data, text_response=text_response
            )

        except Exception as e:
            self.logger.error(f"❌ Gemini API call failed: {e}")
            return ImageGenerationResult(
                success=False,
                error=f"API call failed: {str(e)}",
                error_code="API_ERROR",
            )

    def _sync_gemini_call(self, prompt: str):
        """Synchronous Gemini API call (run in executor)"""
        return self.client.models.generate_content(
            model=self.config.model,
            contents=prompt,
            config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get generator statistics"""
        avg_time = (
            self.total_generation_time / self.successful_requests
            if self.successful_requests > 0
            else 0
        )

        success_rate = (
            self.successful_requests / self.total_requests * 100
            if self.total_requests > 0
            else 0
        )

        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": f"{success_rate:.2f}%",
            "average_generation_time": f"{avg_time:.2f}s",
            "total_generation_time": f"{self.total_generation_time:.2f}s",
            "is_available": self.is_available(),
            "rate_limits": {
                "per_minute": len(self.request_times),
                "per_hour": len(self.hourly_requests),
                "max_per_minute": self.config.rate_limit_per_minute,
                "max_per_hour": self.config.rate_limit_per_hour,
            },
        }

    async def test_connection(self) -> Dict[str, Any]:
        """Test the connection to Gemini API"""
        try:
            if not self.is_available():
                return {
                    "success": False,
                    "error": "Generator not available",
                    "details": {
                        "gemini_sdk": GEMINI_AVAILABLE,
                        "api_key_set": bool(self.config.api_key),
                        "client_initialized": self.is_initialized,
                    },
                }

            # Test with a simple prompt
            test_request = ImageGenerationRequest(
                prompt="A simple test image of a blue circle",
                user_id=0,
                channel_id=0,
                enhance_prompt=False,
            )

            result = await self.generate_image(test_request)

            return {
                "success": result.success,
                "error": result.error,
                "generation_time": result.generation_time,
                "model": self.config.model,
                "has_image_data": bool(result.image_data),
            }

        except Exception as e:
            return {"success": False, "error": f"Test failed: {str(e)}"}


# Global instance
_global_generator: Optional[GeminiImageGenerator] = None


def get_gemini_generator() -> GeminiImageGenerator:
    """Get the global Gemini image generator instance"""
    global _global_generator
    if _global_generator is None:
        _global_generator = GeminiImageGenerator()
    return _global_generator


async def generate_image_simple(
    prompt: str, user_id: int = 0, style: str = "realistic"
) -> Dict[str, Any]:
    """
    Simple interface for image generation

    Args:
        prompt: Text description of the image
        user_id: Discord user ID
        style: Image style (realistic, artistic, cartoon, etc.)

    Returns:
        Dictionary with success status and image data or error
    """
    generator = get_gemini_generator()

    # Convert string style to enum
    try:
        style_enum = ImageStyle(style.lower())
    except ValueError:
        style_enum = ImageStyle.REALISTIC

    request = ImageGenerationRequest(
        prompt=prompt, user_id=user_id, channel_id=0, style=style_enum
    )

    result = await generator.generate_image(request)

    return {
        "success": result.success,
        "image_data": result.image_data,
        "text_response": result.text_response,
        "error": result.error,
        "generation_time": result.generation_time,
        "provider": result.provider,
        "model": result.model,
    }


# Example usage and testing
async def main():
    """Example usage of the Gemini Image Generator"""
    # Test the generator
    generator = get_gemini_generator()

    print("🧪 Testing Gemini Image Generator...")
    test_result = await generator.test_connection()
    print(f"Test result: {test_result}")

    if test_result.get("success"):
        # Generate a test image
        request = ImageGenerationRequest(
            prompt="A majestic dragon flying over a cyberpunk city at night",
            user_id=12345,
            channel_id=67890,
            style=ImageStyle.ARTISTIC,
        )

        result = await generator.generate_image(request)

        if result.success and result.image_data:
            # Save the image
            image = Image.open(BytesIO(result.image_data))
            image.save("test_gemini_image.png")
            print(f"✅ Image saved as test_gemini_image.png")
            print(f"📝 Text response: {result.text_response}")
        else:
            print(f"❌ Generation failed: {result.error}")

    # Print statistics
    stats = generator.get_statistics()
    print(f"📊 Statistics: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
