"""
Advanced Image Generation Handler for Astra Bot
Completely separate from AI conversation system
Uses the new FreepikAPIClient with enhanced error handling
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from .freepik_api_client import FreepikAPIClient, get_freepik_api_client

logger = logging.getLogger("astra.image_handler")


class ImageGenerationHandler:
    """
    Advanced image generation handler with comprehensive error handling
    Completely separate from AI conversation system
    """

    def __init__(self, api_key: str = None):
        self.freepik_client = FreepikAPIClient(api_key)
        self.generation_stats = {
            "total_requests": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "auth_failures": 0,
            "rate_limit_hits": 0,
        }

        logger.info("🎨 Image Generation Handler initialized")

    async def is_available(self) -> bool:
        """Check if image generation is available"""
        try:
            if not self.freepik_client.api_key:
                logger.warning("❌ Image generation unavailable - no API key")
                return False

            # Quick connection test
            test_result = await self.freepik_client.test_api_connection()
            available = test_result.get("success", False)

            if available:
                logger.info("✅ Image generation is available")
            else:
                logger.warning(
                    f"❌ Image generation unavailable: {test_result.get('message', 'Unknown error')}"
                )

            return available

        except Exception as e:
            logger.error(f"❌ Error checking image generation availability: {e}")
            return False

    async def generate_image(
        self,
        prompt: str,
        context: Dict[str, Any],
        user_permissions: Dict[str, bool],
        size: str = "square_hd",
        num_images: int = 1,
    ) -> Dict[str, Any]:
        """
        Generate image with comprehensive error handling and permissions

        Args:
            prompt: Image description
            context: Request context (user_id, channel_id, etc.)
            user_permissions: User permission flags
            size: Image size
            num_images: Number of images to generate

        Returns:
            Dictionary with generation result
        """

        self.generation_stats["total_requests"] += 1

        try:
            user_id = context.get("user_id")
            channel_id = context.get("channel_id")
            guild_id = context.get("guild_id")

            logger.info(f"🎨 Image generation request from user {user_id}")
            logger.info(
                f"📝 Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}"
            )
            logger.info(f"📍 Channel: {channel_id}, Guild: {guild_id}")
            logger.info(f"🔑 Permissions: {user_permissions}")

            # Check if service is available
            if not await self.is_available():
                self.generation_stats["failed_generations"] += 1
                return {
                    "success": False,
                    "error": "Service unavailable",
                    "message": "Image generation service is currently unavailable. Please check API configuration.",
                    "user_friendly": True,
                }

            # Permission check (if needed)
            permission_result = await self._check_permissions(context, user_permissions)
            if not permission_result["allowed"]:
                self.generation_stats["failed_generations"] += 1
                return {
                    "success": False,
                    "error": "Permission denied",
                    "message": permission_result["message"],
                    "user_friendly": True,
                }

            # Validate and clean prompt
            cleaned_prompt = await self._validate_and_clean_prompt(prompt)
            if not cleaned_prompt:
                self.generation_stats["failed_generations"] += 1
                return {
                    "success": False,
                    "error": "Invalid prompt",
                    "message": "The image prompt contains invalid content or is too short.",
                    "user_friendly": True,
                }

            # Generate image with retries
            logger.info("🚀 Starting image generation...")
            generation_result = await self.freepik_client.generate_image_with_retries(
                prompt=cleaned_prompt,
                user_id=user_id,
                size=size,
                num_images=num_images,
                max_retries=3,
            )

            # Process result
            if generation_result.get("success"):
                self.generation_stats["successful_generations"] += 1
                logger.info(f"✅ Image generation successful for user {user_id}")

                return {
                    "success": True,
                    "url": generation_result.get("url"),
                    "provider": "Freepik AI",
                    "prompt": cleaned_prompt,
                    "user_id": user_id,
                    "generation_time": datetime.now(timezone.utc).isoformat(),
                    "attempts": generation_result.get("attempts", 1),
                }

            else:
                # Handle specific error types
                error_type = generation_result.get("error", "Unknown error")
                status_code = generation_result.get("status_code")

                logger.error(f"❌ Image generation failed: {error_type}")

                # Update stats based on error type
                if status_code == 401:
                    self.generation_stats["auth_failures"] += 1
                elif status_code == 429:
                    self.generation_stats["rate_limit_hits"] += 1

                self.generation_stats["failed_generations"] += 1

                # Return user-friendly error
                return await self._format_error_response(generation_result)

        except Exception as e:
            logger.error(f"💥 Critical error in image generation: {e}")
            self.generation_stats["failed_generations"] += 1
            return {
                "success": False,
                "error": "Critical error",
                "message": "An unexpected error occurred during image generation.",
                "user_friendly": True,
            }

    async def _check_permissions(
        self, context: Dict[str, Any], user_permissions: Dict[str, bool]
    ) -> Dict[str, Any]:
        """Check if user has permission to generate images"""

        # For now, allow all users (can be customized per server)
        # In the future, this could check:
        # - Channel restrictions
        # - User roles
        # - Rate limits
        # - Server-specific rules

        channel_id = context.get("channel_id")
        guild_id = context.get("guild_id")
        user_id = context.get("user_id")

        # Example: Restrict to specific channel for non-admins/mods
        restricted_channel_id = 1402666535696470169

        is_admin = user_permissions.get("is_admin", False)
        is_mod = user_permissions.get("is_mod", False)

        # If user is admin or mod, allow anywhere
        if is_admin or is_mod:
            return {"allowed": True, "message": "Permission granted (admin/mod)"}

        # For regular users, check channel restrictions
        if guild_id and channel_id != restricted_channel_id:
            return {
                "allowed": False,
                "message": f"Regular users can only generate images in <#{restricted_channel_id}>. Mods and admins can use any channel.",
            }

        return {"allowed": True, "message": "Permission granted"}

    async def _validate_and_clean_prompt(self, prompt: str) -> Optional[str]:
        """Validate and clean the image prompt"""

        if not prompt or len(prompt.strip()) < 3:
            logger.warning("❌ Prompt too short")
            return None

        cleaned = prompt.strip()

        # Remove potentially harmful content
        blocked_terms = [
            # Add any terms that should be blocked
            # This is a basic implementation
        ]

        for term in blocked_terms:
            if term.lower() in cleaned.lower():
                logger.warning(f"❌ Blocked term found in prompt: {term}")
                return None

        # Limit length
        if len(cleaned) > 500:
            cleaned = cleaned[:500].strip()
            logger.info(f"✂️  Truncated long prompt to 500 characters")

        return cleaned

    async def _format_error_response(
        self, generation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format error response for user consumption"""

        error_type = generation_result.get("error", "Unknown error")
        status_code = generation_result.get("status_code")
        raw_message = generation_result.get("message", "")

        # Create user-friendly error messages
        if status_code == 401:
            return {
                "success": False,
                "error": "API key invalid",
                "message": "The Freepik API key is invalid or expired. Please contact bot administrators.",
                "user_friendly": True,
                "technical_details": {
                    "status_code": status_code,
                    "raw_message": raw_message,
                    "suggestions": generation_result.get("suggestions", []),
                },
            }

        elif status_code == 429:
            return {
                "success": False,
                "error": "Rate limit exceeded",
                "message": "Too many image generation requests. Please wait a few minutes and try again.",
                "user_friendly": True,
                "technical_details": {
                    "status_code": status_code,
                    "raw_message": raw_message,
                },
            }

        elif status_code == 400:
            return {
                "success": False,
                "error": "Invalid request",
                "message": "The image prompt or parameters are invalid. Please try a different description.",
                "user_friendly": True,
                "technical_details": {
                    "status_code": status_code,
                    "raw_message": raw_message,
                },
            }

        elif error_type == "Network error":
            return {
                "success": False,
                "error": "Connection failed",
                "message": "Failed to connect to the image generation service. Please try again later.",
                "user_friendly": True,
            }

        elif error_type == "Request timeout":
            return {
                "success": False,
                "error": "Request timeout",
                "message": "Image generation took too long. Please try again with a simpler prompt.",
                "user_friendly": True,
            }

        else:
            return {
                "success": False,
                "error": "Generation failed",
                "message": "Image generation failed. Please try again later or contact bot administrators.",
                "user_friendly": True,
                "technical_details": generation_result,
            }

    async def get_stats(self) -> Dict[str, Any]:
        """Get generation statistics"""
        total = self.generation_stats["total_requests"]
        success_rate = (
            (self.generation_stats["successful_generations"] / total * 100)
            if total > 0
            else 0
        )

        return {
            **self.generation_stats,
            "success_rate": round(success_rate, 2),
            "api_available": await self.is_available(),
        }

    async def test_generation(self) -> Dict[str, Any]:
        """Test image generation with a simple prompt"""
        logger.info("🧪 Testing image generation...")

        test_context = {
            "user_id": 0,
            "channel_id": 1402666535696470169,  # Default test channel
            "guild_id": 0,
            "request_type": "test",
        }

        test_permissions = {"is_admin": True, "is_mod": True}

        result = await self.generate_image(
            prompt="a simple test image of a blue star",
            context=test_context,
            user_permissions=test_permissions,
        )

        logger.info(f"🧪 Test result: {result.get('success', False)}")
        return result

    async def close(self):
        """Close the handler and clean up resources"""
        if self.freepik_client:
            await self.freepik_client.close()
        logger.info("🔒 Image Generation Handler closed")


# Global handler instance
_image_handler: Optional[ImageGenerationHandler] = None


def get_image_handler(api_key: str = None) -> ImageGenerationHandler:
    """Get global image generation handler"""
    global _image_handler
    if _image_handler is None:
        _image_handler = ImageGenerationHandler(api_key)
    return _image_handler


# Convenience function for quick image generation
async def generate_image_quick(
    prompt: str,
    user_id: int,
    channel_id: int,
    guild_id: int = None,
    is_admin: bool = False,
    is_mod: bool = False,
) -> Dict[str, Any]:
    """Quick image generation function"""

    handler = get_image_handler()

    context = {
        "user_id": user_id,
        "channel_id": channel_id,
        "guild_id": guild_id,
        "request_type": "quick_generation",
    }

    permissions = {"is_admin": is_admin, "is_mod": is_mod}

    return await handler.generate_image(prompt, context, permissions)


# Testing function
async def test_image_handler():
    """Test the image handler"""
    logger.info("🧪 Testing Image Generation Handler...")

    handler = ImageGenerationHandler()

    # Test availability
    available = await handler.is_available()
    logger.info(f"📊 Availability: {available}")

    if available:
        # Test generation
        result = await handler.test_generation()
        logger.info(f"🎨 Generation test: {result}")

    # Get stats
    stats = await handler.get_stats()
    logger.info(f"📈 Stats: {stats}")

    await handler.close()
    return available


if __name__ == "__main__":
    asyncio.run(test_image_handler())
