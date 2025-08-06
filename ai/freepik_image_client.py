"""
Dedicated Freepik Image Generation Client for Astra Bot
Separated from AI conversation to fix API call issues
"""

import os
import logging
import aiohttp
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger("astra.freepik_client")


class FreepikImageClient:
    """
    Dedicated Freepik API client for image generation
    Completely separate from AI conversation system
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("FREEPIK_API_KEY")
        self.base_url = "https://api.freepik.com/v1"
        self.session = None
        
        # Log initialization status
        if self.api_key:
            logger.info("✅ Freepik Image Client initialized with API key")
            logger.info(f"🔑 API Key present: {self.api_key[:10]}...{self.api_key[-4:]}")
        else:
            logger.error("❌ Freepik Image Client initialization FAILED - NO API KEY")
            logger.error("🔧 Please set FREEPIK_API_KEY in Railway environment variables")
            logger.error("🌐 Get your key at: https://www.freepik.com/api")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    def is_available(self) -> bool:
        """Check if Freepik API is available"""
        available = bool(self.api_key and len(self.api_key.strip()) > 10)
        if not available:
            logger.warning("🚫 Freepik API not available - missing or invalid API key")
        return available

    async def generate_image(
        self, 
        prompt: str, 
        user_id: int = None,
        size: str = "square_hd",
        num_images: int = 1
    ) -> Dict[str, Any]:
        """
        Generate image using Freepik API
        
        Args:
            prompt: Image description
            user_id: Discord user ID for logging
            size: Image size (square_hd, landscape_4_3, portrait_3_4, etc.)
            num_images: Number of images to generate (1-4)
        
        Returns:
            Dictionary with success status and image data or error info
        """
        try:
            if not self.is_available():
                return {
                    "success": False,
                    "error": "API key not configured",
                    "message": "FREEPIK_API_KEY environment variable not set in Railway",
                    "setup_url": "https://www.freepik.com/api"
                }

            logger.info(f"🎨 Starting Freepik image generation for user {user_id}")
            logger.info(f"📝 Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")

            session = await self._get_session()

            # Prepare headers
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "AstraBot/1.0"
            }

            # Prepare payload
            payload = {
                "prompt": prompt,
                "num_images": num_images,
                "image": {
                    "size": size
                }
            }

            logger.info(f"🚀 Making Freepik API request to: {self.base_url}/ai/text-to-image")
            logger.info(f"📦 Payload: {payload}")

            # Make the API request
            async with session.post(
                f"{self.base_url}/ai/text-to-image",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)  # 60 second timeout for image generation
            ) as response:
                
                # Log response details
                logger.info(f"📡 Freepik API Response Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Freepik API Success Response: {data}")
                    
                    if data.get("data") and len(data["data"]) > 0:
                        image_data = data["data"][0]
                        result = {
                            "success": True,
                            "url": image_data.get("url"),
                            "provider": "Freepik AI",
                            "prompt": prompt,
                            "user_id": user_id,
                            "size": size,
                            "api_response": data
                        }
                        
                        logger.info(f"🎉 Image generated successfully: {result['url']}")
                        return result
                    else:
                        logger.error(f"❌ Freepik API returned no image data: {data}")
                        return {
                            "success": False,
                            "error": "No image data in response",
                            "api_response": data
                        }
                
                else:
                    # Handle error responses
                    error_text = await response.text()
                    logger.error(f"❌ Freepik API Error {response.status}: {error_text}")
                    
                    # Parse error message if possible
                    error_details = {
                        "success": False,
                        "error": f"API Error: {response.status}",
                        "details": error_text,
                        "status_code": response.status
                    }
                    
                    # Specific error handling
                    if response.status == 401:
                        logger.error("🚨 FREEPIK API AUTHENTICATION ERROR!")
                        logger.error(f"🔑 API Key used: {self.api_key[:10]}...{self.api_key[-4:]}")
                        logger.error("🔧 Check your Freepik API key at: https://www.freepik.com/developers/dashboard/api-key")
                        logger.error("⚙️  Make sure FREEPIK_API_KEY is set in Railway environment variables")
                        
                        error_details.update({
                            "error": "Invalid API key",
                            "message": "Your Freepik API key is invalid or expired. Please check your key at https://www.freepik.com/developers/dashboard/api-key",
                            "setup_required": True
                        })
                    
                    elif response.status == 429:
                        logger.error("⏰ Freepik API rate limit exceeded")
                        error_details.update({
                            "error": "Rate limit exceeded",
                            "message": "Too many requests to Freepik API. Please wait before trying again."
                        })
                    
                    elif response.status == 400:
                        logger.error("📝 Invalid prompt or parameters")
                        error_details.update({
                            "error": "Invalid request",
                            "message": "The image prompt or parameters are invalid. Please try a different description."
                        })
                    
                    return error_details

        except asyncio.TimeoutError:
            logger.error("⏰ Freepik API request timed out")
            return {
                "success": False,
                "error": "Request timeout",
                "message": "Image generation took too long. Please try again with a simpler prompt."
            }
        
        except aiohttp.ClientError as e:
            logger.error(f"🌐 Network error with Freepik API: {e}")
            return {
                "success": False,
                "error": "Network error",
                "message": "Failed to connect to Freepik API. Please try again later."
            }
        
        except Exception as e:
            logger.error(f"💥 Unexpected error in Freepik image generation: {e}")
            return {
                "success": False,
                "error": "Unexpected error",
                "message": f"An unexpected error occurred: {str(e)}"
            }

    async def test_connection(self) -> Dict[str, Any]:
        """
        Test the Freepik API connection
        
        Returns:
            Dictionary with test results
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "API key not configured",
                "message": "FREEPIK_API_KEY environment variable not set"
            }

        try:
            logger.info("🧪 Testing Freepik API connection...")
            
            # Try a simple test generation
            test_result = await self.generate_image(
                prompt="A simple test image of a blue star",
                user_id=0
            )
            
            if test_result.get("success"):
                logger.info("✅ Freepik API connection test successful!")
                return {
                    "success": True,
                    "message": "Freepik API is working correctly",
                    "test_image_url": test_result.get("url")
                }
            else:
                logger.error(f"❌ Freepik API connection test failed: {test_result.get('error')}")
                return {
                    "success": False,
                    "error": test_result.get("error"),
                    "message": test_result.get("message", "Connection test failed")
                }

        except Exception as e:
            logger.error(f"💥 Freepik API connection test error: {e}")
            return {
                "success": False,
                "error": "Test failed",
                "message": f"Connection test failed: {str(e)}"
            }

    async def get_status(self) -> Dict[str, Any]:
        """Get Freepik client status"""
        return {
            "available": self.is_available(),
            "api_key_configured": bool(self.api_key),
            "api_key_length": len(self.api_key) if self.api_key else 0,
            "endpoint": f"{self.base_url}/ai/text-to-image",
            "session_active": self.session is not None and not self.session.closed
        }

    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("🔒 Freepik client session closed")

    def __del__(self):
        """Cleanup on deletion"""
        if hasattr(self, 'session') and self.session and not self.session.closed:
            # Can't use await in __del__, so we'll just log it
            logger.warning("⚠️  Freepik session not properly closed - use async close() method")


# Global client instance
_freepik_client: Optional[FreepikImageClient] = None


def get_freepik_client(api_key: str = None) -> FreepikImageClient:
    """Get global Freepik client instance"""
    global _freepik_client
    if _freepik_client is None:
        _freepik_client = FreepikImageClient(api_key)
    return _freepik_client


# Convenience functions
async def generate_image(prompt: str, user_id: int = None, **kwargs) -> Dict[str, Any]:
    """Quick image generation using global client"""
    client = get_freepik_client()
    return await client.generate_image(prompt, user_id, **kwargs)


async def test_freepik_api() -> Dict[str, Any]:
    """Test Freepik API connection using global client"""
    client = get_freepik_client()
    return await client.test_connection()


if __name__ == "__main__":
    # Test the client
    async def main():
        print("🧪 Testing Freepik Image Client...")
        
        client = FreepikImageClient()
        
        # Check status
        status = await client.get_status()
        print(f"📊 Status: {status}")
        
        if client.is_available():
            # Test connection
            test_result = await client.test_connection()
            print(f"🔍 Test Result: {test_result}")
        else:
            print("❌ Client not available - check FREEPIK_API_KEY environment variable")
        
        await client.close()

    asyncio.run(main())
