"""
Enhanced HTTP Session Manager for Astra Bot
Provides optimized HTTP session management with connection pooling and rate limiting
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
import weakref
from dataclasses import dataclass, field
import json

logger = logging.getLogger("astra.http")


@dataclass
class SessionStats:
    """HTTP session statistics"""

    requests_made: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    average_response_time: float = 0.0
    active_connections: int = 0
    failed_requests: int = 0
    cache_hits: int = 0
    rate_limit_hits: int = 0


@dataclass
class RateLimitInfo:
    """Rate limiting information"""

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    current_minute_count: int = 0
    current_hour_count: int = 0
    minute_reset: datetime = field(default_factory=datetime.utcnow)
    hour_reset: datetime = field(default_factory=datetime.utcnow)


class EnhancedHTTPManager:
    """High-performance HTTP session manager with advanced features"""

    def __init__(
        self,
        max_connections: int = 100,
        max_connections_per_host: int = 30,
        timeout: int = 30,
        enable_cache: bool = True,
        cache_ttl: int = 300,
    ):

        self.max_connections = max_connections
        self.max_connections_per_host = max_connections_per_host
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.enable_cache = enable_cache
        self.cache_ttl = cache_ttl

        # Session management
        self._session: Optional[aiohttp.ClientSession] = None
        self._session_lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None

        # Statistics and monitoring
        self.stats = SessionStats()
        self.rate_limits: Dict[str, RateLimitInfo] = {}

        # Response cache
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamps: Dict[str, datetime] = {}

        # Connection pool optimization
        self._connector_options = {
            "limit": max_connections,
            "limit_per_host": max_connections_per_host,
            "ttl_dns_cache": 300,
            "use_dns_cache": True,
            "keepalive_timeout": 60,
            "enable_cleanup_closed": True,
        }

    async def initialize(self):
        """Initialize the HTTP session with optimized settings"""
        if self._session and not self._session.closed:
            return

        async with self._session_lock:
            if self._session and not self._session.closed:
                return

            # Create optimized connector
            connector = aiohttp.TCPConnector(**self._connector_options)

            # Custom headers for better performance
            headers = {
                "User-Agent": "AstraBot/2.0 (Enhanced HTTP Manager)",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            }

            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=self.timeout,
                headers=headers,
                json_serialize=json.dumps,
                raise_for_status=False,  # Handle status codes manually
            )

            # Start background cleanup task
            if not self._cleanup_task:
                self._cleanup_task = asyncio.create_task(self._background_cleanup())

            logger.info("Enhanced HTTP session initialized with optimized settings")

    async def _background_cleanup(self):
        """Background task for cache cleanup and maintenance"""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute

                # Clean expired cache entries
                now = datetime.utcnow()
                expired_keys = [
                    key
                    for key, timestamp in self._cache_timestamps.items()
                    if (now - timestamp).total_seconds() > self.cache_ttl
                ]

                for key in expired_keys:
                    self._cache.pop(key, None)
                    self._cache_timestamps.pop(key, None)

                # Reset rate limit counters
                for service, rate_limit in self.rate_limits.items():
                    if now > rate_limit.minute_reset + timedelta(minutes=1):
                        rate_limit.current_minute_count = 0
                        rate_limit.minute_reset = now

                    if now > rate_limit.hour_reset + timedelta(hours=1):
                        rate_limit.current_hour_count = 0
                        rate_limit.hour_reset = now

                # Log statistics periodically
                if len(expired_keys) > 0:
                    logger.debug(f"Cleaned {len(expired_keys)} expired cache entries")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Background cleanup error: {e}")

    def _get_cache_key(
        self, method: str, url: str, params: Optional[Dict] = None
    ) -> str:
        """Generate cache key for request"""
        key_parts = [method.upper(), url]
        if params:
            sorted_params = sorted(params.items())
            key_parts.append(str(sorted_params))
        return "|".join(key_parts)

    def _check_rate_limit(self, service: str) -> bool:
        """Check if request is within rate limits"""
        if service not in self.rate_limits:
            self.rate_limits[service] = RateLimitInfo()

        rate_limit = self.rate_limits[service]
        now = datetime.utcnow()

        # Check minute limit
        if now > rate_limit.minute_reset + timedelta(minutes=1):
            rate_limit.current_minute_count = 0
            rate_limit.minute_reset = now

        # Check hour limit
        if now > rate_limit.hour_reset + timedelta(hours=1):
            rate_limit.current_hour_count = 0
            rate_limit.hour_reset = now

        # Verify limits
        if (
            rate_limit.current_minute_count >= rate_limit.requests_per_minute
            or rate_limit.current_hour_count >= rate_limit.requests_per_hour
        ):
            self.stats.rate_limit_hits += 1
            return False

        return True

    async def request(
        self,
        method: str,
        url: str,
        service: str = "default",
        use_cache: bool = None,
        **kwargs,
    ) -> aiohttp.ClientResponse:
        """Make HTTP request with advanced features"""

        if not self._session:
            await self.initialize()

        # Use cache setting or default
        if use_cache is None:
            use_cache = self.enable_cache and method.upper() == "GET"

        # Check cache first
        cache_key = None
        if use_cache:
            cache_key = self._get_cache_key(method, url, kwargs.get("params"))
            if cache_key in self._cache:
                cache_data = self._cache[cache_key]
                if (
                    datetime.utcnow() - self._cache_timestamps[cache_key]
                ).total_seconds() < self.cache_ttl:
                    self.stats.cache_hits += 1
                    # Return cached response (would need to create mock response)
                    logger.debug(f"Cache hit for {method} {url}")

        # Check rate limits
        if not self._check_rate_limit(service):
            rate_limit = self.rate_limits[service]
            wait_time = (
                61 - (datetime.utcnow() - rate_limit.minute_reset).total_seconds()
            )
            logger.warning(f"Rate limit hit for {service}, waiting {wait_time:.1f}s")
            await asyncio.sleep(max(1, wait_time))

        # Make request with timing
        start_time = datetime.utcnow()

        try:
            async with self._session.request(method, url, **kwargs) as response:
                # Update statistics
                self.stats.requests_made += 1

                # Update rate limits
                if service in self.rate_limits:
                    rate_limit = self.rate_limits[service]
                    rate_limit.current_minute_count += 1
                    rate_limit.current_hour_count += 1

                # Calculate response time
                response_time = (datetime.utcnow() - start_time).total_seconds()
                total_time = self.stats.average_response_time * (
                    self.stats.requests_made - 1
                )
                self.stats.average_response_time = (
                    total_time + response_time
                ) / self.stats.requests_made

                # Update byte counters
                if hasattr(response, "content_length") and response.content_length:
                    self.stats.bytes_received += response.content_length

                # Cache successful GET responses
                if (
                    use_cache
                    and cache_key
                    and response.status == 200
                    and method.upper() == "GET"
                ):
                    try:
                        response_data = await response.read()
                        self._cache[cache_key] = {
                            "status": response.status,
                            "headers": dict(response.headers),
                            "data": response_data,
                        }
                        self._cache_timestamps[cache_key] = datetime.utcnow()
                    except Exception as e:
                        logger.warning(f"Failed to cache response: {e}")

                # Handle error responses
                if response.status >= 400:
                    self.stats.failed_requests += 1
                    if response.status == 429:  # Rate limited
                        self.stats.rate_limit_hits += 1

                return response

        except Exception as e:
            self.stats.failed_requests += 1
            logger.error(f"HTTP request failed: {method} {url} - {e}")
            raise

    async def get(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Optimized GET request"""
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Optimized POST request"""
        return await self.request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Optimized PUT request"""
        return await self.request("PUT", url, **kwargs)

    async def delete(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Optimized DELETE request"""
        return await self.request("DELETE", url, **kwargs)

    async def download_file(self, url: str, chunk_size: int = 8192) -> bytes:
        """Optimized file download with progress tracking"""
        if not self._session:
            await self.initialize()

        data = bytearray()

        async with self._session.get(url) as response:
            response.raise_for_status()

            async for chunk in response.content.iter_chunked(chunk_size):
                data.extend(chunk)
                self.stats.bytes_received += len(chunk)

        return bytes(data)

    def get_stats(self) -> Dict[str, Any]:
        """Get detailed HTTP session statistics"""
        return {
            "requests_made": self.stats.requests_made,
            "bytes_sent": self.stats.bytes_sent,
            "bytes_received": self.stats.bytes_received,
            "average_response_time": round(self.stats.average_response_time, 3),
            "failed_requests": self.stats.failed_requests,
            "success_rate": (
                (self.stats.requests_made - self.stats.failed_requests)
                / max(1, self.stats.requests_made)
            )
            * 100,
            "cache_hits": self.stats.cache_hits,
            "cache_hit_rate": (self.stats.cache_hits / max(1, self.stats.requests_made))
            * 100,
            "rate_limit_hits": self.stats.rate_limit_hits,
            "cache_entries": len(self._cache),
            "active_rate_limits": len(self.rate_limits),
        }

    def configure_rate_limit(
        self, service: str, requests_per_minute: int = 60, requests_per_hour: int = 1000
    ):
        """Configure rate limits for a specific service"""
        if service not in self.rate_limits:
            self.rate_limits[service] = RateLimitInfo()

        rate_limit = self.rate_limits[service]
        rate_limit.requests_per_minute = requests_per_minute
        rate_limit.requests_per_hour = requests_per_hour

        logger.info(
            f"Rate limit configured for {service}: {requests_per_minute}/min, {requests_per_hour}/hour"
        )

    def clear_cache(self, pattern: Optional[str] = None):
        """Clear cache entries, optionally matching a pattern"""
        if pattern:
            keys_to_remove = [key for key in self._cache.keys() if pattern in key]
        else:
            keys_to_remove = list(self._cache.keys())

        for key in keys_to_remove:
            self._cache.pop(key, None)
            self._cache_timestamps.pop(key, None)

        logger.info(f"Cleared {len(keys_to_remove)} cache entries")

    async def close(self):
        """Close HTTP session and cleanup resources"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        if self._session and not self._session.closed:
            await self._session.close()

        # Clear cache
        self._cache.clear()
        self._cache_timestamps.clear()

        logger.info("Enhanced HTTP manager closed and cleaned up")


# Global HTTP manager instance
http_manager = EnhancedHTTPManager()

# Backwards compatibility aliases
HTTPClient = EnhancedHTTPManager


async def get_session():
    """Get the global HTTP session"""
    if not http_manager._session:
        await http_manager.initialize()
    return http_manager._session


async def get_json(url: str, **kwargs):
    """Get JSON from URL"""
    response = await http_manager.get(url, **kwargs)
    return await response.json()


async def post_json(url: str, data=None, **kwargs):
    """Post JSON to URL"""
    if data:
        kwargs["json"] = data
    response = await http_manager.post(url, **kwargs)
    return await response.json()


async def cleanup_http():
    """Cleanup HTTP resources"""
    await http_manager.close()
