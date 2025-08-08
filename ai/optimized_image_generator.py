"""
Optimized Image Generation System for AstraBot
Enhanced performance, proper image handling, and robust error management
"""

import os
import io
import logging
import aiohttp
import asyncio
import json
import hashlib
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timezone, timedelta
from pathlib import Path

logger = logging.getLogger("astra.optimized_image")


class OptimizedImageGenerator:
    """
    High-performance image generation system with:
    - Image caching and compression
    - Proper file handling and Discord uploads
    - Smart retry logic with exponential backoff
    - Connection pooling and session reuse
    - Enhanced error handling and rate limiting
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("FREEPIK_API_KEY")
        self.base_url = "https://api.freepik.com/v1"
        
        # Session with connection pooling
        self.session = None
        self._session_lock = asyncio.Lock()
        
        # Performance caching
        self.image_cache = {}
        self.cache_dir = Path("data/image_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Rate limiting
        self.rate_limits = {
            "requests_per_minute": 30,
            "requests_per_hour": 200,
            "daily_requests": 1000
        }
        self.request_history = []
        
        # Performance metrics
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "average_response_time": 0.0,
            "total_images_generated": 0
        }

        logger.info("🚀 Optimized Image Generator initialized")
        if self.api_key:
            logger.info(f"🔑 API Key configured: {self.api_key[:10]}...{self.api_key[-6:]}")
        else:
            logger.error("❌ No API key configured!")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get optimized session with connection pooling"""
        async with self._session_lock:
            if self.session is None or self.session.closed:
                # Optimized connector with connection pooling
                connector = aiohttp.TCPConnector(
                    limit=20,  # Total connection pool size
                    limit_per_host=10,  # Per-host limit
                    ttl_dns_cache=300,  # DNS cache TTL
                    use_dns_cache=True,
                    keepalive_timeout=60,
                    enable_cleanup_closed=True
                )
                
                # Optimized timeout configuration
                timeout = aiohttp.ClientTimeout(
                    total=120,  # Total timeout
                    connect=30,  # Connection timeout
                    sock_read=60  # Socket read timeout
                )
                
                self.session = aiohttp.ClientSession(
                    connector=connector,
                    timeout=timeout,
                    headers={
                        'User-Agent': 'AstraBot/2.1 (Optimized)',
                        'Accept': 'application/json',
                        'Cache-Control': 'no-cache'
                    }
                )
                logger.info("🔗 Optimized session created with connection pooling")
            
            return self.session

    def _generate_cache_key(self, prompt: str, size: str, num_images: int) -> str:
        """Generate cache key for image requests"""
        content = f"{prompt}_{size}_{num_images}"
        return hashlib.md5(content.encode()).hexdigest()

    async def _check_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Check if image exists in cache"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            if cache_file.exists():
                # Check if cache is still valid (24 hours)
                cache_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if datetime.now() - cache_time < timedelta(hours=24):
                    with open(cache_file, 'r') as f:
                        cached_data = json.load(f)
                    
                    self.stats["cache_hits"] += 1
                    logger.info(f"🎯 Cache hit for key: {cache_key}")
                    return cached_data
                else:
                    # Remove expired cache
                    cache_file.unlink(missing_ok=True)
            
            return None
        except Exception as e:
            logger.warning(f"⚠️ Cache check failed: {e}")
            return None

    async def _save_to_cache(self, cache_key: str, data: Dict[str, Any]) -> None:
        """Save image data to cache"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            logger.info(f"💾 Cached result for key: {cache_key}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to save cache: {e}")

    async def _check_rate_limits(self) -> Dict[str, Any]:
        """Advanced rate limiting check"""
        now = datetime.now()
        
        # Clean old requests
        self.request_history = [
            req_time for req_time in self.request_history 
            if now - req_time < timedelta(hours=1)
        ]
        
        # Check limits
        minute_requests = len([
            req_time for req_time in self.request_history 
            if now - req_time < timedelta(minutes=1)
        ])
        
        hour_requests = len(self.request_history)
        
        if minute_requests >= self.rate_limits["requests_per_minute"]:
            return {
                "allowed": False,
                "reason": "minute_limit",
                "wait_time": 60,
                "message": "Rate limit: 30 requests per minute exceeded"
            }
        
        if hour_requests >= self.rate_limits["requests_per_hour"]:
            return {
                "allowed": False,
                "reason": "hour_limit", 
                "wait_time": 3600,
                "message": "Rate limit: 200 requests per hour exceeded"
            }
        
        return {"allowed": True}

    async def _download_image(self, image_url: str) -> Optional[bytes]:
        """Download image and return bytes for Discord upload"""
        try:
            session = await self._get_session()
            
            async with session.get(image_url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    logger.info(f"📥 Downloaded image: {len(image_data)} bytes")
                    return image_data
                else:
                    logger.error(f"❌ Failed to download image: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Image download error: {e}")
            return None

    async def generate_image_optimized(
        self,
        prompt: str,
        user_id: int = None,
        size: str = "square_hd",
        num_images: int = 1,
        download_image: bool = True
    ) -> Dict[str, Any]:
        """
        Optimized image generation with caching and proper file handling
        
        Args:
            prompt: Image description
            user_id: Discord user ID
            size: Image size
            num_images: Number of images
            download_image: Whether to download image bytes for Discord
            
        Returns:
            Dict with success status, image data, and optional bytes
        """
        
        start_time = datetime.now()
        self.stats["total_requests"] += 1
        
        try:
            if not self.api_key:
                return {
                    "success": False,
                    "error": "no_api_key",
                    "message": "Freepik API key not configured"
                }

            # Generate cache key
            cache_key = self._generate_cache_key(prompt, size, num_images)
            
            # Check cache first
            cached_result = await self._check_cache(cache_key)
            if cached_result and not download_image:
                logger.info("⚡ Returning cached result")
                return cached_result

            # Check rate limits
            rate_check = await self._check_rate_limits()
            if not rate_check["allowed"]:
                return {
                    "success": False,
                    "error": "rate_limit",
                    "message": rate_check["message"],
                    "wait_time": rate_check["wait_time"]
                }

            # Record request
            self.request_history.append(datetime.now())

            # Prepare optimized payload
            payload = {
                "prompt": prompt.strip(),
                "num_images": min(num_images, 4),  # Freepik limit
                "image": {
                    "size": size
                },
                "model": "flux"  # Use best model
            }

            # Get session
            session = await self._get_session()
            
            # Enhanced headers for better success rate
            headers = {
                "X-Freepik-API-Key": self.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "AstraBot/2.1 (Discord Bot)",
                "Cache-Control": "no-cache"
            }

            logger.info(f"🎨 Generating image: {prompt[:50]}...")
            logger.info(f"📊 Request {self.stats['total_requests']}")

            # Make API request with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    async with session.post(
                        f"{self.base_url}/ai/text-to-image",
                        headers=headers,
                        json=payload
                    ) as response:
                        
                        logger.info(f"📡 API Response: {response.status} (attempt {attempt + 1})")
                        
                        if response.status == 200:
                            data = await response.json()
                            
                            if data.get("data") and len(data["data"]) > 0:
                                image_info = data["data"][0]
                                image_url = image_info.get("url")
                                
                                if not image_url:
                                    raise ValueError("No image URL in response")

                                # Prepare result
                                result = {
                                    "success": True,
                                    "url": image_url,
                                    "provider": "Freepik AI",
                                    "prompt": prompt,
                                    "user_id": user_id,
                                    "size": size,
                                    "generation_time": datetime.now(timezone.utc).isoformat(),
                                    "response_time_ms": (datetime.now() - start_time).total_seconds() * 1000,
                                    "attempts": attempt + 1,
                                    "cache_key": cache_key
                                }

                                # Download image if requested
                                if download_image:
                                    image_bytes = await self._download_image(image_url)
                                    if image_bytes:
                                        result["image_bytes"] = image_bytes
                                        result["image_size"] = len(image_bytes)
                                        logger.info(f"✅ Image ready: {len(image_bytes)} bytes")
                                    else:
                                        logger.warning("⚠️ Failed to download image, URL only")

                                # Cache result (without bytes)
                                cache_data = {k: v for k, v in result.items() if k != "image_bytes"}
                                await self._save_to_cache(cache_key, cache_data)

                                # Update stats
                                self.stats["successful_generations"] += 1
                                self.stats["total_images_generated"] += 1
                                
                                # Update average response time
                                response_time = (datetime.now() - start_time).total_seconds() * 1000
                                self.stats["average_response_time"] = (
                                    (self.stats["average_response_time"] * (self.stats["successful_generations"] - 1) + response_time) 
                                    / self.stats["successful_generations"]
                                )

                                logger.info(f"🎉 Image generated successfully in {response_time:.1f}ms")
                                return result
                            
                            else:
                                raise ValueError("No image data in API response")

                        elif response.status == 401:
                            error_text = await response.text()
                            logger.error(f"🚨 Authentication failed: {error_text}")
                            self.stats["failed_generations"] += 1
                            return {
                                "success": False,
                                "error": "authentication_failed",
                                "message": "Invalid API key. Please check your Freepik API configuration.",
                                "status_code": 401
                            }
                        
                        elif response.status == 429:
                            # Rate limited by API
                            logger.warning("⏰ API rate limit hit")
                            if attempt < max_retries - 1:
                                wait_time = (attempt + 1) * 10  # 10, 20, 30 seconds
                                logger.info(f"⏳ Waiting {wait_time}s before retry...")
                                await asyncio.sleep(wait_time)
                                continue
                            else:
                                self.stats["failed_generations"] += 1
                                return {
                                    "success": False,
                                    "error": "rate_limited",
                                    "message": "API rate limit exceeded. Please try again later.",
                                    "status_code": 429
                                }
                        
                        elif response.status >= 500:
                            # Server error - retry
                            error_text = await response.text()
                            logger.warning(f"🔄 Server error {response.status}, retrying... {error_text}")
                            if attempt < max_retries - 1:
                                await asyncio.sleep((attempt + 1) * 2)  # 2, 4, 6 seconds
                                continue
                        
                        else:
                            # Other errors
                            error_text = await response.text()
                            logger.error(f"❌ API Error {response.status}: {error_text}")
                            self.stats["failed_generations"] += 1
                            return {
                                "success": False,
                                "error": f"api_error_{response.status}",
                                "message": f"API error: {error_text}",
                                "status_code": response.status
                            }

                except asyncio.TimeoutError:
                    logger.warning(f"⏰ Request timeout (attempt {attempt + 1})")
                    if attempt < max_retries - 1:
                        await asyncio.sleep((attempt + 1) * 3)  # 3, 6, 9 seconds
                        continue
                except Exception as e:
                    logger.error(f"💥 Request error (attempt {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep((attempt + 1) * 2)
                        continue

            # All retries failed
            self.stats["failed_generations"] += 1
            return {
                "success": False,
                "error": "max_retries_exceeded",
                "message": f"Failed after {max_retries} attempts. Please try again later.",
                "attempts": max_retries
            }

        except Exception as e:
            logger.error(f"💥 Unexpected error in image generation: {e}")
            self.stats["failed_generations"] += 1
            return {
                "success": False,
                "error": "unexpected_error",
                "message": f"Unexpected error: {str(e)}"
            }

    async def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        cache_hit_rate = (
            (self.stats["cache_hits"] / max(self.stats["total_requests"], 1)) * 100
        )
        
        success_rate = (
            (self.stats["successful_generations"] / max(self.stats["total_requests"], 1)) * 100
        )
        
        return {
            **self.stats,
            "cache_hit_rate_percent": round(cache_hit_rate, 2),
            "success_rate_percent": round(success_rate, 2),
            "api_key_configured": bool(self.api_key),
            "session_active": self.session and not self.session.closed,
            "cached_images": len(list(self.cache_dir.glob("*.json")))
        }

    async def clear_cache(self, older_than_hours: int = 24) -> Dict[str, Any]:
        """Clear old cache files"""
        try:
            cleared = 0
            cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
            
            for cache_file in self.cache_dir.glob("*.json"):
                if datetime.fromtimestamp(cache_file.stat().st_mtime) < cutoff_time:
                    cache_file.unlink()
                    cleared += 1
            
            logger.info(f"🧹 Cleared {cleared} cache files older than {older_than_hours} hours")
            return {"cleared_files": cleared, "success": True}
            
        except Exception as e:
            logger.error(f"❌ Cache cleanup failed: {e}")
            return {"success": False, "error": str(e)}

    async def close(self):
        """Close session and cleanup"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("🔚 Optimized image generator session closed")

    def __del__(self):
        """Cleanup on deletion"""
        if hasattr(self, 'session') and self.session and not self.session.closed:
            # Can't await in __del__, just close
            try:
                import asyncio
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.session.close())
            except:
                pass


# Global instance
_optimized_generator: Optional[OptimizedImageGenerator] = None


def get_optimized_generator(api_key: str = None) -> OptimizedImageGenerator:
    """Get global optimized generator instance"""
    global _optimized_generator
    if _optimized_generator is None:
        _optimized_generator = OptimizedImageGenerator(api_key)
    return _optimized_generator


async def generate_image_fast(
    prompt: str,
    user_id: int = None,
    size: str = "square_hd",
    download_bytes: bool = True
) -> Dict[str, Any]:
    """Quick optimized image generation"""
    generator = get_optimized_generator()
    return await generator.generate_image_optimized(
        prompt=prompt,
        user_id=user_id,
        size=size,
        download_image=download_bytes
    )


async def get_generation_stats() -> Dict[str, Any]:
    """Get performance statistics"""
    generator = get_optimized_generator()
    return await generator.get_stats()


if __name__ == "__main__":
    # Test the optimized generator
    async def test_optimized():
        generator = OptimizedImageGenerator()
        
        print("🧪 Testing optimized image generation...")
        
        # Test stats
        stats = await generator.get_stats()
        print(f"📊 Initial stats: {stats}")
        
        # Test generation
        result = await generator.generate_image_optimized(
            "a simple test image of a cute robot",
            user_id=12345,
            download_image=True
        )
        
        print(f"🎨 Generation result: {result.get('success')}")
        if result.get("image_bytes"):
            print(f"📥 Downloaded {len(result['image_bytes'])} bytes")
        
        # Final stats
        final_stats = await generator.get_stats()
        print(f"📈 Final stats: {final_stats}")
        
        await generator.close()

    import asyncio
    asyncio.run(test_optimized())
