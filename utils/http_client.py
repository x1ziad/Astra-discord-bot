"""
HTTP client utilities for Astra Discord bot
Handles proper creation and cleanup of aiohttp sessions
"""

import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("Astra")
_session: Optional[aiohttp.ClientSession] = None
_session_lock = asyncio.Lock()


async def get_session() -> aiohttp.ClientSession:
    """
    Get or create a shared aiohttp ClientSession
    Uses a singleton pattern to reuse the same session across the application
    """
    global _session

    async with _session_lock:
        if _session is None or _session.closed:
            _session = aiohttp.ClientSession(
                headers={"User-Agent": "Astra Discord Bot/1.0.0"},
                timeout=aiohttp.ClientTimeout(total=30),
            )
            logger.debug("Created new aiohttp ClientSession")

    return _session


async def close_session() -> None:
    """Close the shared aiohttp ClientSession"""
    global _session

    async with _session_lock:
        if _session is not None and not _session.closed:
            await _session.close()
            _session = None
            logger.debug("Closed aiohttp ClientSession")
