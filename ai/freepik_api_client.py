"""
Advanced Freepik API Client with Multiple Authentication Methods
Completely rewritten to handle Freepik API authentication correctly
"""

import os
import logging
import aiohttp
import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

logger = logging.getLogger("astra.freepik_api")


class FreepikAPIClient:
    """
    Advanced Freepik API client with proper authentication handling
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("FREEPIK_API_KEY")
        self.base_url = "https://api.freepik.com/v1"
        self.session = None
        
        # Enhanced logging for debugging
        if self.api_key:
            # More detailed API key validation
            key_length = len(self.api_key.strip())
            logger.info(f"✅ Freepik API Client initialized")
            logger.info(f"🔑 API Key length: {key_length} characters")
            logger.info(f"🔑 API Key format: {self.api_key[:8]}...{self.api_key[-8:]}")
            
            # Validate key format
            if not self.api_key.startswith(('FPSX', 'fpsx', 'FPS')):
                logger.warning(f"⚠️  API Key format may be incorrect - expected to start with 'FPSX' or 'FPS'")
            
        else:
            logger.error("❌ CRITICAL: No Freepik API key found!")
            logger.error("🔧 Set FREEPIK_API_KEY in Railway environment variables")
            logger.error("🌐 Get your key at: https://www.freepik.com/api")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session with proper headers"""
        if self.session is None or self.session.closed:
            # Set up headers for all requests
            headers = {
                'User-Agent': 'AstraBot/2.0 (Discord Bot)',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            timeout = aiohttp.ClientTimeout(
                total=90,      # 90 second total timeout
                connect=10,    # 10 second connection timeout
                sock_read=30   # 30 second read timeout
            )
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout
            )
            
        return self.session

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers - try multiple formats"""
        if not self.api_key:
            return {}
        
        # Freepik API documentation suggests different formats
        # Let's try the most common ones
        headers = {
            # Method 1: Standard Bearer token
            'Authorization': f'Bearer {self.api_key}',
            # Method 2: X-Freepik-API-Key header (some APIs use this)
            'X-Freepik-API-Key': self.api_key,
            # Method 3: X-API-Key header
            'X-API-Key': self.api_key,
            # Method 4: Direct API key in Authorization
            'X-Authorization': self.api_key
        }
        
        return headers

    async def test_api_connection(self) -> Dict[str, Any]:
        """Test API connection with multiple authentication methods"""
        if not self.api_key:
            return {
                "success": False,
                "error": "No API key configured",
                "message": "FREEPIK_API_KEY environment variable not set"
            }

        logger.info("🧪 Testing Freepik API connection...")
        
        session = await self._get_session()
        auth_headers = self._get_auth_headers()
        
        # Test endpoints to try
        test_endpoints = [
            "/ai/text-to-image",  # Main endpoint
            "/user/profile",      # Profile endpoint (if available)
            "/credits"            # Credits endpoint (if available)
        ]
        
        for endpoint in test_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                logger.info(f"🔍 Testing endpoint: {url}")
                
                # Try a simple GET request first
                async with session.get(url, headers=auth_headers) as response:
                    logger.info(f"📡 Response Status: {response.status}")
                    logger.info(f"📋 Response Headers: {dict(response.headers)}")
                    
                    response_text = await response.text()
                    logger.info(f"📄 Response Body: {response_text[:500]}")
                    
                    if response.status == 200:
                        return {
                            "success": True,
                            "message": "API connection successful",
                            "endpoint": endpoint,
                            "status": response.status
                        }
                    elif response.status == 401:
                        logger.warning(f"🔐 Authentication failed for {endpoint}")
                        continue
                    elif response.status == 405:
                        logger.info(f"📝 Method not allowed for {endpoint} (trying POST)")
                        # Try POST for image generation
                        if endpoint == "/ai/text-to-image":
                            return await self._test_image_generation()
                    else:
                        logger.warning(f"⚠️  Unexpected status {response.status} for {endpoint}")
                        
            except Exception as e:
                logger.error(f"❌ Error testing {endpoint}: {e}")
                continue
        
        return {
            "success": False,
            "error": "All test endpoints failed",
            "message": "Could not establish connection with any authentication method"
        }

    async def _test_image_generation(self) -> Dict[str, Any]:
        """Test image generation specifically"""
        try:
            logger.info("🎨 Testing image generation endpoint...")
            
            test_payload = {
                "prompt": "a simple test image",
                "num_images": 1,
                "image": {
                    "size": "square_hd"
                }
            }
            
            result = await self.generate_image_raw(
                prompt="a simple test image",
                size="square_hd",
                num_images=1
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "message": "Image generation test successful",
                    "endpoint": "/ai/text-to-image"
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"❌ Image generation test failed: {e}")
            return {
                "success": False,
                "error": "Image generation test failed",
                "message": str(e)
            }

    async def generate_image_raw(
        self, 
        prompt: str, 
        size: str = "square_hd", 
        num_images: int = 1
    ) -> Dict[str, Any]:
        """Raw image generation with multiple authentication methods"""
        
        if not self.api_key:
            return {
                "success": False,
                "error": "API key not configured",
                "message": "FREEPIK_API_KEY environment variable not set"
            }
            
        logger.info(f"🎨 Starting raw image generation with multi-auth")
        logger.info(f"📝 Prompt: {prompt}")
        logger.info(f"📐 Size: {size}")
        logger.info(f"🔢 Number of images: {num_images}")
        
        session = await self._get_session()
        
        # Prepare payload
        payload = {
            "prompt": prompt,
            "num_images": num_images,
            "image": {
                "size": size
            }
        }
        
        base_url = f"{self.base_url}/ai/text-to-image"
        
        logger.info(f"🚀 Making multi-auth request to: {base_url}")
        logger.info(f"📦 Payload: {json.dumps(payload, indent=2)}")
        
        # Try multiple authentication methods
        auth_methods = [
            # Method 1: X-Freepik-API-Key header (most likely to work)
            {
                "name": "X-Freepik-API-Key Header",
                "url": base_url,
                "headers": {
                    "X-Freepik-API-Key": self.api_key,
                    "Content-Type": "application/json",
                    "User-Agent": "AstraBot/2.0",
                    "Accept": "application/json"
                }
            },
            # Method 2: Custom freepikkey header
            {
                "name": "freepikkey Header",
                "url": base_url,
                "headers": {
                    "freepikkey": self.api_key,
                    "Content-Type": "application/json",
                    "User-Agent": "AstraBot/2.0",
                    "Accept": "application/json"
                }
            },
            # Method 3: API key in URL parameters
            {
                "name": "URL Parameter",
                "url": f"{base_url}?api_key={self.api_key}",
                "headers": {
                    "Content-Type": "application/json",
                    "User-Agent": "AstraBot/2.0",
                    "Accept": "application/json"
                }
            },
            # Method 4: Authorization with API prefix
            {
                "name": "API Authorization",
                "url": base_url,
                "headers": {
                    "Authorization": f"API {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "AstraBot/2.0",
                    "Accept": "application/json"
                }
            },
            # Method 5: Bearer token (fallback)
            {
                "name": "Bearer Token",
                "url": base_url,
                "headers": {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "AstraBot/2.0",
                    "Accept": "application/json"
                }
            },
            # Method 6: Combined headers (kitchen sink approach)
            {
                "name": "Combined Headers",
                "url": base_url,
                "headers": {
                    "Authorization": f"Bearer {self.api_key}",
                    "X-Freepik-API-Key": self.api_key,
                    "X-API-Key": self.api_key,
                    "freepikkey": self.api_key,
                    "Content-Type": "application/json",
                    "User-Agent": "AstraBot/2.0",
                    "Accept": "application/json"
                }
            }
        ]
        
        # Try each authentication method
        for i, method in enumerate(auth_methods, 1):
            logger.info(f"🧪 Trying method {i}/{len(auth_methods)}: {method['name']}")
            
            try:
                async with session.post(
                    method['url'], 
                    headers=method['headers'], 
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    
                    logger.info(f"📡 {method['name']} - Status: {response.status}")
                    
                    if response.status == 200:
                        response_text = await response.text()
                        logger.info(f"✅ SUCCESS with {method['name']}!")
                        logger.info(f"� Response: {response_text}")
                        
                        try:
                            response_data = json.loads(response_text)
                            
                            if response_data.get("data") and len(response_data["data"]) > 0:
                                image_data = response_data["data"][0]
                                
                                # Store successful method for future use
                                logger.info(f"🔑 Storing successful auth method: {method['name']}")
                                
                                return {
                                    "success": True,
                                    "url": image_data.get("url"),
                                    "provider": "Freepik AI",
                                    "auth_method": method['name'],
                                    "raw_response": response_data
                                }
                            else:
                                logger.warning(f"❌ {method['name']} - No image data in response")
                                return {
                                    "success": False,
                                    "error": "No image data in response",
                                    "auth_method": method['name'],
                                    "raw_response": response_data
                                }
                                
                        except json.JSONDecodeError as e:
                            logger.error(f"❌ {method['name']} - JSON decode error: {e}")
                            return {
                                "success": False,
                                "error": "Invalid JSON response",
                                "auth_method": method['name'],
                                "raw_response": response_text
                            }
                    
                    elif response.status == 401:
                        response_text = await response.text()
                        logger.warning(f"❌ {method['name']} - Authentication failed (401)")
                        logger.debug(f"📄 Error response: {response_text}")
                        
                        # Continue to next method on 401
                        continue
                        
                    else:
                        # For non-401 errors, return immediately as they're not auth-related
                        response_text = await response.text()
                        logger.error(f"❌ {method['name']} - HTTP {response.status}: {response_text}")
                        
                        # Parse error if possible
                        try:
                            error_data = json.loads(response_text)
                            error_message = error_data.get("message", response_text)
                        except:
                            error_message = response_text
                        
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}",
                            "message": error_message,
                            "status_code": response.status,
                            "auth_method": method['name']
                        }
            
            except asyncio.TimeoutError:
                logger.warning(f"⏰ {method['name']} - Request timed out")
                continue
                
            except aiohttp.ClientError as e:
                logger.warning(f"🌐 {method['name']} - Network error: {e}")
                continue
                
            except Exception as e:
                logger.warning(f"💥 {method['name']} - Unexpected error: {e}")
                continue
        
        # If all methods failed with 401, return authentication error
        logger.error("❌ All authentication methods failed!")
        return {
            "success": False,
            "error": "Authentication failed",
            "message": "All authentication methods failed. Please verify your API key at https://www.freepik.com/developers/dashboard/api-key",
            "status_code": 401,
            "attempted_methods": [method['name'] for method in auth_methods]
        }

    async def generate_image_with_retries(
        self,
        prompt: str,
        user_id: int = None,
        size: str = "square_hd",
        num_images: int = 1,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Generate image with retry logic"""
        
        logger.info(f"🎨 Image generation with retries for user {user_id}")
        logger.info(f"📝 Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
        
        for attempt in range(max_retries):
            logger.info(f"🔄 Attempt {attempt + 1}/{max_retries}")
            
            result = await self.generate_image_raw(prompt, size, num_images)
            
            if result.get("success"):
                logger.info(f"✅ Image generation successful on attempt {attempt + 1}")
                result.update({
                    "user_id": user_id,
                    "prompt": prompt,
                    "attempts": attempt + 1
                })
                return result
            
            elif result.get("status_code") == 401:
                # Don't retry authentication failures
                logger.error("❌ Authentication failure - not retrying")
                return result
                
            elif result.get("status_code") == 400:
                # Don't retry bad requests
                logger.error("❌ Bad request - not retrying")
                return result
                
            else:
                logger.warning(f"⚠️  Attempt {attempt + 1} failed: {result.get('error', 'Unknown')}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # Exponential backoff: 2, 4, 6 seconds
                    logger.info(f"⏳ Waiting {wait_time} seconds before retry...")
                    await asyncio.sleep(wait_time)
                    
        logger.error(f"❌ All {max_retries} attempts failed")
        return result  # Return the last failed result

    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information to verify API key"""
        if not self.api_key:
            return {
                "success": False,
                "error": "No API key configured"
            }
            
        session = await self._get_session()
        auth_headers = self._get_auth_headers()
        
        # Try different account info endpoints
        endpoints_to_try = [
            "/user/profile",
            "/account",
            "/user",
            "/credits"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                url = f"{self.base_url}{endpoint}"
                async with session.get(url, headers=auth_headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "data": data,
                            "endpoint": endpoint
                        }
            except Exception as e:
                logger.debug(f"Failed to get account info from {endpoint}: {e}")
                continue
                
        return {
            "success": False,
            "error": "Could not retrieve account information"
        }

    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("🔒 Freepik API client session closed")

    def __del__(self):
        """Cleanup on deletion"""
        if hasattr(self, 'session') and self.session and not self.session.closed:
            logger.warning("⚠️  Session not properly closed - use async close() method")


# Global instance
_freepik_api_client: Optional[FreepikAPIClient] = None


def get_freepik_api_client(api_key: str = None) -> FreepikAPIClient:
    """Get global Freepik API client instance"""
    global _freepik_api_client
    if _freepik_api_client is None:
        _freepik_api_client = FreepikAPIClient(api_key)
    return _freepik_api_client


# Testing function
async def test_freepik_api_comprehensive():
    """Comprehensive API test"""
    logger.info("🧪 Starting comprehensive Freepik API test...")
    
    client = FreepikAPIClient()
    
    # Test 1: Check API key
    if not client.api_key:
        logger.error("❌ No API key found")
        return False
        
    # Test 2: Test connection
    connection_result = await client.test_api_connection()
    logger.info(f"🔍 Connection test: {connection_result}")
    
    if not connection_result.get("success"):
        logger.error("❌ Connection test failed")
        return False
        
    # Test 3: Generate test image
    logger.info("🎨 Testing image generation...")
    image_result = await client.generate_image_with_retries(
        prompt="a simple blue star in space",
        user_id=0
    )
    
    logger.info(f"🎨 Image generation result: {image_result}")
    
    await client.close()
    
    return image_result.get("success", False)


if __name__ == "__main__":
    asyncio.run(test_freepik_api_comprehensive())
