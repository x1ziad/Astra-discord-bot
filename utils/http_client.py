"""
HTTP client utilities for Astra Bot
Provides a shared aiohttp session with retry logic and rate limiting
"""

import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any, Union
from datetime import datetime, timedelta
import json

logger = logging.getLogger("astra.http")


class HTTPClient:
    """Enhanced HTTP client with retry logic and rate limiting"""

    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self._session: Optional[aiohttp.ClientSession] = None
        self._rate_limits: Dict[str, datetime] = {}

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=30,
                ttl_dns_cache=300,
                use_dns_cache=True,
            )

            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=self.timeout,
                headers={
                    "User-Agent": "Astra-Discord-Bot/2.0.0 (https://github.com/x1ziad/Astra-discord-bot)"
                },
            )

        return self._session

    async def get(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make GET request with retry logic"""
        return await self._request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make POST request with retry logic"""
        return await self._request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make PUT request with retry logic"""
        return await self._request("PUT", url, **kwargs)

    async def delete(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make DELETE request with retry logic"""
        return await self._request("DELETE", url, **kwargs)

    async def _request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make HTTP request with retry logic"""
        session = await self._get_session()

        for attempt in range(self.max_retries + 1):
            try:
                # Check rate limit
                if self._is_rate_limited(url):
                    await asyncio.sleep(1)
                    continue

                async with session.request(method, url, **kwargs) as response:
                    # Handle rate limiting
                    if response.status == 429:
                        retry_after = int(response.headers.get("Retry-After", 60))
                        self._rate_limits[url] = datetime.utcnow() + timedelta(
                            seconds=retry_after
                        )

                        if attempt < self.max_retries:
                            await asyncio.sleep(min(retry_after, 60))
                            continue

                    # Log errors
                    if response.status >= 400:
                        logger.warning(f"HTTP {response.status} for {method} {url}")

                    return response

            except asyncio.TimeoutError:
                logger.warning(f"Timeout for {method} {url} (attempt {attempt + 1})")
                if attempt < self.max_retries:
                    await asyncio.sleep(2**attempt)  # Exponential backoff
                    continue
                raise

            except aiohttp.ClientError as e:
                logger.warning(
                    f"Client error for {method} {url}: {e} (attempt {attempt + 1})"
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(2**attempt)
                    continue
                raise

    def _is_rate_limited(self, url: str) -> bool:
        """Check if URL is rate limited"""
        if url in self._rate_limits:
            if datetime.utcnow() < self._rate_limits[url]:
                return True
            else:
                del self._rate_limits[url]
        return False

    async def get_json(self, url: str, **kwargs) -> Dict[str, Any]:
        """Get JSON response"""
        async with await self.get(url, **kwargs) as response:
            return await response.json()

    async def post_json(
        self, url: str, data: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        """Post JSON data and get JSON response"""
        kwargs["json"] = data
        kwargs.setdefault("headers", {})["Content-Type"] = "application/json"

        async with await self.post(url, **kwargs) as response:
            return await response.json()

    async def close(self):
        """Close the HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("HTTP client session closed")


# Global HTTP client instance
_http_client = HTTPClient()


async def get_session() -> aiohttp.ClientSession:
    """Get the global HTTP session"""
    return await _http_client._get_session()


async def get_json(url: str, **kwargs) -> Dict[str, Any]:
    """Convenient function to get JSON from URL"""
    return await _http_client.get_json(url, **kwargs)


async def post_json(url: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Convenient function to post JSON data"""
    return await _http_client.post_json(url, data, **kwargs)


async def cleanup_http():
    """Clean up HTTP resources"""
    await _http_client.close()
