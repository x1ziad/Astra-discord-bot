"""
MagicHour.ai Image Generator for Astra Bot
High-quality image generation using MagicHour.ai API
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

# Set up logging
logger = logging.getLogger("astra.magichour_image")


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
    provider: str = "MagicHour.ai"
    model: str = "flux-schnell"
    metadata: Dict[str, Any] = field(default_factory=dict)


class MagicHourImageConfig:
    """Configuration for MagicHour.ai image generation"""

    def __init__(self):
        self.api_key = os.getenv("MAGICHOUR_API_KEY")
        self.base_url = "https://api.magichour.ai"
        self.model = "flux-schnell"  # MagicHour.ai's fast model
        self.max_retries = 3
        self.retry_delay = 2.0
        self.timeout = 120.0
        self.rate_limit_per_minute = 20
        self.rate_limit_per_hour = 200
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


class MagicHourImageGenerator:
    """
    MagicHour.ai-based image generation system
    High-quality image generation with comprehensive error handling
    """

    def __init__(self, config: Optional[MagicHourImageConfig] = None):
        self.config = config or MagicHourImageConfig()
        self.logger = logging.getLogger("astra.magichour_image")
        self.session = None
        self.is_initialized = False

        # Rate limiting
        self.request_times: List[datetime] = []
        self.hourly_requests: List[datetime] = []

        # Statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_generation_time = 0.0

        # Initialize
        self._initialize_client()

    def _initialize_client(self) -> bool:
        """Initialize the MagicHour.ai client"""
        try:
            if not self.config.api_key:
                self.logger.error("❌ MAGICHOUR_API_KEY environment variable not set")
                return False

            self.is_initialized = True
            self.logger.info("✅ MagicHour.ai Image Generator initialized successfully")
            self.logger.info(
                f"🔑 API Key configured: {self.config.api_key[:16]}...{self.config.api_key[-8:]}"
            )
            self.logger.info(f"🤖 Model: {self.config.model}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to initialize MagicHour.ai client: {e}")
            self.is_initialized = False
            return False

    def is_available(self) -> bool:
        """Check if the generator is available and properly configured"""
        return self.is_initialized and self.config.api_key is not None

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

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session

    async def generate_image(
        self, request: ImageGenerationRequest
    ) -> ImageGenerationResult:
        """
        Generate an image using MagicHour.ai API

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
                    error="MagicHour.ai Image Generator not available",
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

            # Generate image with MagicHour.ai
            result = await self._call_magichour_api(final_prompt, request)

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

    async def _call_magichour_api(
        self, prompt: str, request: ImageGenerationRequest
    ) -> ImageGenerationResult:
        """Make the actual API call to MagicHour.ai"""
        session = await self._get_session()

        # Parse size
        width, height = request.size.value.split("x")
        width, height = int(width), int(height)

        # Prepare request payload for MagicHour.ai
        payload = {
            "prompt": prompt,
            "model": self.config.model,
            "width": width,
            "height": height,
            "num_inference_steps": 4,  # Fast generation with flux-schnell
            "guidance_scale": 0.0,  # flux-schnell doesn't use guidance
            "num_images": request.num_images,
            "output_format": "png",
        }

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        try:
            # Make API request
            url = f"{self.config.base_url}/generate"

            self.logger.info(f"🌐 Making request to MagicHour.ai: {url}")

            async with session.post(url, json=payload, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    self.logger.error(
                        f"❌ MagicHour.ai API error {response.status}: {error_text}"
                    )
                    return ImageGenerationResult(
                        success=False,
                        error=f"API error {response.status}: {error_text}",
                        error_code="API_ERROR",
                    )

                response_data = await response.json()
                self.logger.info(
                    f"📦 MagicHour.ai response structure: {list(response_data.keys())}"
                )

                # Check for errors in response
                if "error" in response_data:
                    error_msg = response_data["error"].get("message", "Unknown error")
                    return ImageGenerationResult(
                        success=False,
                        error=f"MagicHour.ai error: {error_msg}",
                        error_code="GENERATION_ERROR",
                    )

                # Extract image data - try different response formats
                image_data = None
                image_url = None

                # Check for base64 image data
                if "image" in response_data:
                    try:
                        # Remove data URL prefix if present
                        base64_data = response_data["image"]
                        if base64_data.startswith("data:image"):
                            base64_data = base64_data.split(",")[1]

                        image_data = base64.b64decode(base64_data)
                        self.logger.info(
                            f"✅ Received base64 image data: {len(image_data)} bytes"
                        )

                        return ImageGenerationResult(
                            success=True,
                            image_data=image_data,
                            text_response=f"Generated with MagicHour.ai {self.config.model}",
                        )
                    except Exception as e:
                        self.logger.error(f"❌ Failed to decode base64 image: {e}")

                # Check for image URL
                if "url" in response_data:
                    image_url = response_data["url"]
                    self.logger.info(f"📥 Downloading image from: {image_url}")

                    async with session.get(image_url) as img_response:
                        if img_response.status != 200:
                            return ImageGenerationResult(
                                success=False,
                                error=f"Failed to download image: {img_response.status}",
                                error_code="DOWNLOAD_ERROR",
                            )

                        image_data = await img_response.read()

                        return ImageGenerationResult(
                            success=True,
                            image_data=image_data,
                            image_url=image_url,
                            text_response=f"Generated with MagicHour.ai {self.config.model}",
                        )

                # Check for images array
                if "images" in response_data and response_data["images"]:
                    first_image = response_data["images"][0]

                    # Try base64 from images array
                    if isinstance(first_image, str):
                        try:
                            if first_image.startswith("data:image"):
                                first_image = first_image.split(",")[1]
                            image_data = base64.b64decode(first_image)

                            return ImageGenerationResult(
                                success=True,
                                image_data=image_data,
                                text_response=f"Generated with MagicHour.ai {self.config.model}",
                            )
                        except Exception as e:
                            self.logger.error(
                                f"❌ Failed to decode image from array: {e}"
                            )

                    # Try URL from images array
                    elif isinstance(first_image, dict) and "url" in first_image:
                        image_url = first_image["url"]
                        async with session.get(image_url) as img_response:
                            if img_response.status == 200:
                                image_data = await img_response.read()
                                return ImageGenerationResult(
                                    success=True,
                                    image_data=image_data,
                                    image_url=image_url,
                                    text_response=f"Generated with MagicHour.ai {self.config.model}",
                                )

                return ImageGenerationResult(
                    success=False,
                    error="No valid image data found in response",
                    error_code="NO_IMAGE_DATA",
                )

        except asyncio.TimeoutError:
            return ImageGenerationResult(
                success=False, error="Request timed out", error_code="TIMEOUT"
            )
        except Exception as e:
            self.logger.error(f"❌ MagicHour.ai API call failed: {e}")
            return ImageGenerationResult(
                success=False,
                error=f"API call failed: {str(e)}",
                error_code="API_ERROR",
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
        """Test the connection to MagicHour.ai API"""
        try:
            if not self.is_available():
                return {
                    "success": False,
                    "error": "Generator not available",
                    "details": {
                        "api_key_set": bool(self.config.api_key),
                        "initialized": self.is_initialized,
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
                "image_url": result.image_url,
            }

        except Exception as e:
            return {"success": False, "error": f"Test failed: {str(e)}"}

    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()


# Global instance
_global_generator: Optional[MagicHourImageGenerator] = None


def get_magichour_generator() -> MagicHourImageGenerator:
    """Get the global MagicHour.ai image generator instance"""
    global _global_generator
    if _global_generator is None:
        _global_generator = MagicHourImageGenerator()
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
    generator = get_magichour_generator()

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
        "image_url": result.image_url,
        "text_response": result.text_response,
        "error": result.error,
        "generation_time": result.generation_time,
        "provider": result.provider,
        "model": result.model,
    }


# Example usage and testing
async def main():
    """Example usage of the MagicHour.ai Image Generator"""
    # Test the generator
    generator = get_magichour_generator()

    print("🧪 Testing MagicHour.ai Image Generator...")
    test_result = await generator.test_connection()
    print(f"Test result: {test_result}")

    if test_result.get("success"):
        print("✅ MagicHour.ai connection successful!")

        # Get statistics
        stats = generator.get_statistics()
        print(f"📊 Statistics: {stats}")
    else:
        print(f"❌ Connection failed: {test_result.get('error')}")

    # Close session
    await generator.close()


if __name__ == "__main__":
    asyncio.run(main())
