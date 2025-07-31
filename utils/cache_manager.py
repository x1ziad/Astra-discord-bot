"""
Cache management for API responses
Handles storing and retrieving API data to reduce API calls
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("Astra")


class CacheManager:
    """Manager for API response caching"""

    def __init__(self, cache_dir: str):
        """Initialize with a cache directory"""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def get_cached_data(
        self, key: str, max_age_hours: int = 24
    ) -> Optional[Dict]:
        """
        Get cached data if available and not expired

        Args:
            key: Cache key
            max_age_hours: Maximum age in hours before cache is considered stale

        Returns:
            Cached data or None if not available or expired
        """
        cache_file = self.cache_dir / f"{key}.json"

        if not cache_file.exists():
            return None

        try:
            # Check file age
            file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
            if datetime.now() - file_time > timedelta(hours=max_age_hours):
                logger.debug(f"Cache for {key} expired")
                return None

            with open(cache_file, "r") as f:
                data = json.load(f)

            logger.debug(f"Using cached data for {key}")
            return data
        except Exception as e:
            logger.error(f"Error reading cache for {key}: {e}")
            return None

    async def cache_data(self, key: str, data: Any) -> bool:
        """
        Cache data to file

        Args:
            key: Cache key
            data: Data to cache (must be JSON serializable)

        Returns:
            True if successful, False otherwise
        """
        cache_file = self.cache_dir / f"{key}.json"

        try:
            with open(cache_file, "w") as f:
                json.dump(data, f)
            logger.debug(f"Cached data for {key}")
            return True
        except Exception as e:
            logger.error(f"Error caching data for {key}: {e}")
            return False

    async def clear_cache(self, key: Optional[str] = None) -> None:
        """
        Clear cache files

        Args:
            key: Specific key to clear, or None to clear all cache
        """
        try:
            if key:
                cache_file = self.cache_dir / f"{key}.json"
                if cache_file.exists():
                    os.remove(cache_file)
                    logger.debug(f"Cleared cache for {key}")
            else:
                # Clear all cache files
                for file in self.cache_dir.glob("*.json"):
                    os.remove(file)
                logger.debug("Cleared all cache files")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")


# Create a global instance for space data
space_cache = CacheManager("data/space")
