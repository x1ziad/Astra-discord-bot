"""
Optimized Image Generator for Astra Bot
Provides a high-level interface to the MagicHour.ai Image Generator
"""

import logging
from typing import Optional, Union, Dict, Any
import asyncio

# Import the MagicHour.ai Image Generator
try:
    from ai.magichour_image_generator import (
        MagicHourImageGenerator,
        ImageGenerationRequest,
        ImageSize,
        ImageStyle,
        get_magichour_generator,
        generate_image_simple,
    )

    MAGICHOUR_AVAILABLE = True
except ImportError as e:
    MAGICHOUR_AVAILABLE = False
    MagicHourImageGenerator = None
    ImageGenerationRequest = None
    ImageSize = None
    ImageStyle = None
    get_magichour_generator = None
    generate_image_simple = None

logger = logging.getLogger("astra.optimized_image")


class OptimizedImageGenerator:
    """Optimized wrapper around MagicHourImageGenerator"""

    def __init__(self):
        self.generator = None
        self._initialize()

    def _initialize(self):
        """Initialize the MagicHour.ai image generator"""
        if MAGICHOUR_AVAILABLE:
            try:
                self.generator = get_magichour_generator()
                logger.info(
                    "✅ Optimized Image Generator initialized with MagicHour.ai"
                )
            except Exception as e:
                logger.error(f"❌ Failed to initialize MagicHour.ai generator: {e}")
                self.generator = None
        else:
            logger.error("❌ MagicHour.ai Image Generator not available")

    def is_available(self) -> bool:
        """Check if the generator is available"""
        return self.generator is not None and self.generator.is_available()

    async def generate_image(
        self, prompt: str, user_id: int = 0, **kwargs
    ) -> Optional[bytes]:
        """
        Generate an image using the optimized generator

        Args:
            prompt: The image generation prompt
            user_id: Discord user ID
            **kwargs: Additional parameters (size, style, etc.)

        Returns:
            Image data as bytes, or None if generation failed
        """
        if not self.is_available():
            logger.error("❌ Generator not available")
            return None

        try:
            logger.info(f"🎨 Generating image: {prompt[:50]}...")

            # Extract parameters
            style = kwargs.get("style", "realistic")

            # Use the simple interface
            result = await generate_image_simple(
                prompt=prompt, user_id=user_id, style=style
            )

            if result["success"] and result["image_data"]:
                logger.info("✅ Image generation successful")
                return result["image_data"]
            else:
                logger.error(
                    f"❌ Image generation failed: {result.get('error', 'Unknown error')}"
                )
                return None

        except Exception as e:
            logger.error(f"❌ Image generation error: {e}")
            return None

    async def generate_image_advanced(
        self, prompt: str, user_id: int, channel_id: int, **kwargs
    ) -> Optional[bytes]:
        """
        Generate image using the advanced interface with full control

        Args:
            prompt: The image generation prompt
            user_id: Discord user ID
            channel_id: Discord channel ID
            **kwargs: Additional parameters

        Returns:
            Image data as bytes, or None if generation failed
        """
        if not self.is_available():
            logger.error("❌ Generator not available")
            return None

        try:
            # Extract and convert parameters
            size_str = kwargs.get("size", "1024x1024")
            style_str = kwargs.get("style", "realistic")

            # Convert to enums
            size_enum = ImageSize.SQUARE_HD  # Default
            if size_str == "768x1024":
                size_enum = ImageSize.PORTRAIT
            elif size_str == "1024x768":
                size_enum = ImageSize.LANDSCAPE
            elif size_str == "1024x576":
                size_enum = ImageSize.WIDE

            style_enum = ImageStyle.REALISTIC  # Default
            try:
                style_enum = ImageStyle(style_str.lower())
            except ValueError:
                pass

            # Create request
            request = ImageGenerationRequest(
                prompt=prompt,
                user_id=user_id,
                channel_id=channel_id,
                size=size_enum,
                style=style_enum,
                enhance_prompt=kwargs.get("enhance_prompt", True),
            )

            # Generate image
            result = await self.generator.generate_image(request)

            if result.success and result.image_data:
                logger.info("✅ Advanced image generation successful")
                return result.image_data
            else:
                logger.error(f"❌ Advanced image generation failed: {result.error}")
                return None

        except Exception as e:
            logger.error(f"❌ Advanced image generation error: {e}")
            return None

    async def generate_image_with_fallback(
        self, prompt: str, user_id: int = 0, **kwargs
    ) -> Optional[bytes]:
        """
        Generate image with fallback mechanisms
        """
        try:
            # First attempt
            result = await self.generate_image(prompt, user_id, **kwargs)
            if result:
                return result

            # Simplified prompt fallback
            simplified_prompt = prompt.split(",")[0]  # Take first part before comma
            logger.info(f"🔄 Retrying with simplified prompt: {simplified_prompt}")
            result = await self.generate_image(simplified_prompt, user_id, **kwargs)

            return result

        except Exception as e:
            logger.error(f"❌ Fallback generation failed: {e}")
            return None


# Global instance
_optimized_generator = None


def get_optimized_generator() -> OptimizedImageGenerator:
    """Get the global optimized image generator instance"""
    global _optimized_generator
    if _optimized_generator is None:
        _optimized_generator = OptimizedImageGenerator()
    return _optimized_generator


# For backwards compatibility
async def generate_optimized_image(
    prompt: str, user_id: int = 0, **kwargs
) -> Optional[bytes]:
    """Generate an image using the optimized generator"""
    generator = get_optimized_generator()
    return await generator.generate_image_with_fallback(prompt, user_id, **kwargs)
