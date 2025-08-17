"""
ModelsLab Image Generator for Astra Bot
High-quality image generation using ModelsLab API
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
logger = logging.getLogger("astra.modelslab_image")


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
    provider: str = "ModelsLab"
    model: str = "flux"
    metadata: Dict[str, Any] = field(default_factory=dict)


class ModelsLabImageConfig:
    """Configuration for ModelsLab image generation"""

    def __init__(self):
        self.api_key = os.getenv("MODELSLAB_API_KEY")
        self.base_url = "https://modelslab.com/api/v6"
        self.model = "flux"  # ModelsLab flux model
        self.max_retries = 3
        self.retry_delay = 2.0
        self.timeout = 120.0  # ModelsLab can take longer
        self.rate_limit_per_minute = 10
        self.rate_limit_per_hour = 50
        self.max_prompt_length = 1000

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


class ModelsLabImageGenerator:
    """
    ModelsLab-based image generation system
    High-quality image generation with comprehensive error handling
    """

    def __init__(self, config: Optional[ModelsLabImageConfig] = None):
        self.config = config or ModelsLabImageConfig()
        self.logger = logging.getLogger("astra.modelslab_image")
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
        """Initialize the ModelsLab client"""
        try:
            if not self.config.api_key:
                self.logger.error("❌ MODELSLAB_API_KEY environment variable not set")
                return False

            self.is_initialized = True
            self.logger.info("✅ ModelsLab Image Generator initialized successfully")
            self.logger.info(
                f"🔑 API Key configured: {self.config.api_key[:8]}...{self.config.api_key[-4:]}"
            )
            self.logger.info(f"🤖 Model: {self.config.model}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to initialize ModelsLab client: {e}")
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
        Generate an image using ModelsLab API

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
                    error="ModelsLab Image Generator not available",
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

            # Generate image with ModelsLab
            result = await self._call_modelslab_api(final_prompt, request)

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

    async def _call_modelslab_api(
        self, prompt: str, request: ImageGenerationRequest
    ) -> ImageGenerationResult:
        """Make the actual API call to ModelsLab"""
        session = await self._get_session()

        # Parse size
        width, height = request.size.value.split("x")
        width, height = int(width), int(height)

        # Prepare request payload for v6 API
        payload = {
            "key": self.config.api_key,
            "prompt": prompt,
            "model_id": self.config.model,
            "width": width,
            "height": height,
            "samples": request.num_images,
            "num_inference_steps": 50,
            "guidance_scale": 7.5,
            "safety_checker": True,
            "enhance_prompt": True if request.enhance_prompt else False,
            "seed": None,
            "webhook": None,
            "track_id": None,
        }

        headers = {"Content-Type": "application/json"}

        try:
            # Make API request
            url = f"{self.config.base_url}/realtime/text2img"

            self.logger.info(f"🌐 Making request to ModelsLab: {url}")

            async with session.post(url, json=payload, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    self.logger.error(
                        f"❌ ModelsLab API error {response.status}: {error_text}"
                    )
                    return ImageGenerationResult(
                        success=False,
                        error=f"API error {response.status}: {error_text}",
                        error_code="API_ERROR",
                    )

                response_data = await response.json()
                self.logger.info(f"📦 ModelsLab response: {response_data}")

                # Check for errors in response
                if response_data.get("status") == "error":
                    error_msg = response_data.get("message", "Unknown error")
                    return ImageGenerationResult(
                        success=False,
                        error=f"ModelsLab error: {error_msg}",
                        error_code="GENERATION_ERROR",
                    )

                # Extract image URLs - v6 API format
                output = response_data.get("output", [])
                if not output:
                    return ImageGenerationResult(
                        success=False,
                        error="No images in response",
                        error_code="NO_IMAGES",
                    )

                # Download the first image
                image_url = output[0]
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
                        text_response=f"Generated with ModelsLab {self.config.model}",
                    )

        except asyncio.TimeoutError:
            return ImageGenerationResult(
                success=False, error="Request timed out", error_code="TIMEOUT"
            )
        except Exception as e:
            self.logger.error(f"❌ ModelsLab API call failed: {e}")
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
        """Test the connection to ModelsLab API"""
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
_global_generator: Optional[ModelsLabImageGenerator] = None


def get_modelslab_generator() -> ModelsLabImageGenerator:
    """Get the global ModelsLab image generator instance"""
    global _global_generator
    if _global_generator is None:
        _global_generator = ModelsLabImageGenerator()
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
    generator = get_modelslab_generator()

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
    """Example usage of the ModelsLab Image Generator"""
    # Test the generator
    generator = get_modelslab_generator()

    print("🧪 Testing ModelsLab Image Generator...")
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
            image.save("test_modelslab_image.png")
            print(f"✅ Image saved as test_modelslab_image.png")
            print(f"🔗 Image URL: {result.image_url}")
        else:
            print(f"❌ Generation failed: {result.error}")

    # Print statistics
    stats = generator.get_statistics()
    print(f"📊 Statistics: {stats}")

    # Close session
    await generator.close()


if __name__ == "__main__":
    asyncio.run(main())
