"""
Enhanced Cache Manager - High Performance
Provides hybrid memory/file caching with advanced TTL, compression, and optimization
"""

import json
import os
import time
import asyncio
import logging
import pickle
import hashlib
import gzip
from typing import Any, Dict, Optional, Union, Callable
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timezone
import threading
from collections import OrderedDict
import weakref

logger = logging.getLogger("astra.cache")


@dataclass
class CacheEntry:
    """Enhanced cache entry with metadata"""

    value: Any
    expires_at: float
    created_at: float
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    size_bytes: int = 0
    compressed: bool = False


@dataclass
class CacheStats:
    """Comprehensive cache statistics"""

    total_entries: int = 0
    memory_entries: int = 0
    file_entries: int = 0
    total_size_bytes: int = 0
    memory_size_bytes: int = 0
    file_size_bytes: int = 0
    hit_count: int = 0
    miss_count: int = 0
    eviction_count: int = 0
    cleanup_count: int = 0


class EnhancedCacheManager:
    """High-performance hybrid cache with memory and file storage"""

    def __init__(
        self,
        cache_dir: str = "temp/cache",
        default_ttl: int = 300,
        max_memory_entries: int = 1000,
        max_memory_size_bytes: int = 50 * 1024 * 1024,  # 50MB
        enable_compression: bool = True,
        compression_threshold: int = 1024,  # Compress items > 1KB
        enable_file_cache: bool = True,
        cleanup_interval: int = 300,  # 5 minutes
    ):

        self.cache_dir = Path(cache_dir)
        self.default_ttl = default_ttl
        self.max_memory_entries = max_memory_entries
        self.max_memory_size_bytes = max_memory_size_bytes
        self.enable_compression = enable_compression
        self.compression_threshold = compression_threshold
        self.enable_file_cache = enable_file_cache
        self.cleanup_interval = cleanup_interval

        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Memory cache (LRU-ordered)
        self._memory_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._memory_lock = asyncio.Lock()
        self._thread_lock = threading.RLock()

        # Statistics
        self.stats = CacheStats()

        # Background cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        self._initialize_cleanup_on_first_use = True

    def _start_cleanup_task(self):
        """Start background cleanup task (called when event loop is available)"""
        try:
            loop = asyncio.get_running_loop()
            if not self._cleanup_task or self._cleanup_task.done():
                self._cleanup_task = asyncio.create_task(self._background_cleanup())
                self._initialize_cleanup_on_first_use = False
        except RuntimeError:
            # No event loop running, defer until first async operation
            self._initialize_cleanup_on_first_use = True

    async def _background_cleanup(self):
        """Background cleanup of expired entries"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)

                # Clean memory cache
                await self._cleanup_memory_cache()

                # Clean file cache
                if self.enable_file_cache:
                    cleaned = await self._cleanup_file_cache()
                    if cleaned > 0:
                        logger.debug(f"Cleaned {cleaned} expired file cache entries")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")

    async def _cleanup_memory_cache(self):
        """Clean expired entries from memory cache"""
        current_time = time.time()
        expired_keys = []

        async with self._memory_lock:
            for key, entry in list(self._memory_cache.items()):
                if current_time > entry.expires_at:
                    expired_keys.append(key)

            for key in expired_keys:
                self._memory_cache.pop(key, None)
                self.stats.cleanup_count += 1

    async def _cleanup_file_cache(self) -> int:
        """Clean expired file cache entries"""
        cleaned = 0
        current_time = time.time()

        try:
            for cache_file in self.cache_dir.glob("*.cache"):
                try:
                    entry = await self._load_file_entry(cache_file)
                    if entry and current_time > entry.expires_at:
                        cache_file.unlink(missing_ok=True)
                        cleaned += 1
                except Exception:
                    # Remove corrupted files
                    cache_file.unlink(missing_ok=True)
                    cleaned += 1
        except Exception as e:
            logger.error(f"File cache cleanup error: {e}")

        return cleaned

    def _get_cache_key_hash(self, key: str) -> str:
        """Generate hash for cache key"""
        return hashlib.md5(key.encode()).hexdigest()

    def _get_cache_file(self, key: str) -> Path:
        """Get cache file path for key"""
        key_hash = self._get_cache_key_hash(key)
        return self.cache_dir / f"{key_hash}.cache"

    def _estimate_size(self, value: Any) -> int:
        """Estimate memory size of value"""
        try:
            if isinstance(value, (str, bytes)):
                return len(value)
            elif isinstance(value, (int, float)):
                return 8
            elif isinstance(value, (list, tuple)):
                return sum(self._estimate_size(item) for item in value)
            elif isinstance(value, dict):
                return sum(
                    self._estimate_size(k) + self._estimate_size(v)
                    for k, v in value.items()
                )
            else:
                # Fallback to pickle size
                return len(pickle.dumps(value))
        except Exception:
            return 1024  # Default estimate

    def _should_compress(self, value: Any) -> bool:
        """Determine if value should be compressed"""
        if not self.enable_compression:
            return False

        size = self._estimate_size(value)
        return size > self.compression_threshold

    def _compress_value(self, value: Any) -> bytes:
        """Compress value"""
        pickled = pickle.dumps(value)
        return gzip.compress(pickled)

    def _decompress_value(self, data: bytes) -> Any:
        """Decompress value"""
        decompressed = gzip.decompress(data)
        return pickle.loads(decompressed)

    async def _evict_memory_entries(self):
        """Evict old entries from memory cache"""
        while (
            len(self._memory_cache) >= self.max_memory_entries
            or self.stats.memory_size_bytes >= self.max_memory_size_bytes
        ):

            if not self._memory_cache:
                break

            # Remove oldest entry (LRU)
            key, entry = self._memory_cache.popitem(last=False)
            self.stats.memory_size_bytes -= entry.size_bytes
            self.stats.eviction_count += 1

            # Optionally save to file cache
            if self.enable_file_cache and entry.access_count > 1:
                try:
                    await self._save_file_entry(key, entry)
                except Exception as e:
                    logger.warning(f"Failed to save evicted entry to file: {e}")

    async def _save_file_entry(self, key: str, entry: CacheEntry):
        """Save entry to file cache"""
        cache_file = self._get_cache_file(key)

        try:
            if self._should_compress(entry.value):
                data = self._compress_value(
                    {
                        "value": entry.value,
                        "expires_at": entry.expires_at,
                        "created_at": entry.created_at,
                        "access_count": entry.access_count,
                        "compressed": True,
                    }
                )
            else:
                data = pickle.dumps(
                    {
                        "value": entry.value,
                        "expires_at": entry.expires_at,
                        "created_at": entry.created_at,
                        "access_count": entry.access_count,
                        "compressed": False,
                    }
                )

            # Use thread executor for file I/O to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._write_file_sync, cache_file, data)

        except Exception as e:
            logger.error(f"Failed to save file cache entry: {e}")

    def _write_file_sync(self, cache_file: Path, data: bytes):
        """Synchronous file write for executor"""
        with open(cache_file, "wb") as f:
            f.write(data)

    def _read_file_sync(self, cache_file: Path) -> bytes:
        """Synchronous file read for executor"""
        with open(cache_file, "rb") as f:
            return f.read()

    async def _load_file_entry(self, cache_file: Path) -> Optional[CacheEntry]:
        """Load entry from file cache"""
        try:
            # Use thread executor for file I/O to avoid blocking
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, self._read_file_sync, cache_file)

            # Try to decompress first
            try:
                cache_data = self._decompress_value(data)
                compressed = True
            except:
                cache_data = pickle.loads(data)
                compressed = cache_data.get("compressed", False)

            return CacheEntry(
                value=cache_data["value"],
                expires_at=cache_data["expires_at"],
                created_at=cache_data["created_at"],
                access_count=cache_data.get("access_count", 0),
                last_accessed=time.time(),
                size_bytes=len(data),
                compressed=compressed,
            )

        except Exception as e:
            logger.warning(f"Failed to load file cache entry: {e}")
            return None

    async def get(self, key: str) -> Optional[Any]:
        """Get cached value with intelligent retrieval"""
        # Initialize cleanup task if needed
        if self._initialize_cleanup_on_first_use:
            self._start_cleanup_task()

        current_time = time.time()

        # Check memory cache first
        async with self._memory_lock:
            if key in self._memory_cache:
                entry = self._memory_cache[key]

                # Check expiration
                if current_time > entry.expires_at:
                    self._memory_cache.pop(key)
                    self.stats.cleanup_count += 1
                else:
                    # Update access stats and move to end (LRU)
                    entry.access_count += 1
                    entry.last_accessed = current_time
                    self._memory_cache.move_to_end(key)
                    self.stats.hit_count += 1
                    return entry.value

        # Check file cache
        if self.enable_file_cache:
            cache_file = self._get_cache_file(key)
            if cache_file.exists():
                entry = await self._load_file_entry(cache_file)

                if entry and current_time <= entry.expires_at:
                    # Move back to memory cache
                    entry.access_count += 1
                    entry.last_accessed = current_time

                    async with self._memory_lock:
                        # Check if we need to evict
                        if len(self._memory_cache) >= self.max_memory_entries:
                            await self._evict_memory_entries()

                        self._memory_cache[key] = entry
                        self.stats.memory_size_bytes += entry.size_bytes

                    self.stats.hit_count += 1
                    return entry.value
                else:
                    # Remove expired file
                    cache_file.unlink(missing_ok=True)

        self.stats.miss_count += 1
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cached value with intelligent storage"""
        # Initialize cleanup task if needed
        if self._initialize_cleanup_on_first_use:
            self._start_cleanup_task()

        if ttl is None:
            ttl = self.default_ttl

        current_time = time.time()
        expires_at = current_time + ttl
        size_bytes = self._estimate_size(value)

        entry = CacheEntry(
            value=value,
            expires_at=expires_at,
            created_at=current_time,
            access_count=1,
            last_accessed=current_time,
            size_bytes=size_bytes,
            compressed=self._should_compress(value),
        )

        async with self._memory_lock:
            # Check if we need to evict before adding
            if (
                len(self._memory_cache) >= self.max_memory_entries
                or self.stats.memory_size_bytes + size_bytes
                >= self.max_memory_size_bytes
            ):
                await self._evict_memory_entries()

            # Add to memory cache
            self._memory_cache[key] = entry
            self.stats.memory_size_bytes += size_bytes
            self.stats.total_entries += 1
            self.stats.memory_entries += 1

        return True

    async def delete(self, key: str) -> bool:
        """Delete cached value from both memory and file"""
        deleted = False

        # Remove from memory cache
        async with self._memory_lock:
            if key in self._memory_cache:
                entry = self._memory_cache.pop(key)
                self.stats.memory_size_bytes -= entry.size_bytes
                self.stats.memory_entries -= 1
                deleted = True

        # Remove from file cache
        if self.enable_file_cache:
            cache_file = self._get_cache_file(key)
            if cache_file.exists():
                try:
                    cache_file.unlink()
                    self.stats.file_entries -= 1
                    deleted = True
                except OSError:
                    pass

        if deleted:
            self.stats.total_entries -= 1

        return deleted

    async def clear(self) -> int:
        """Clear all cache entries"""
        cleared = 0

        # Clear memory cache
        async with self._memory_lock:
            cleared += len(self._memory_cache)
            self._memory_cache.clear()
            self.stats.memory_size_bytes = 0
            self.stats.memory_entries = 0

        # Clear file cache
        if self.enable_file_cache:
            try:
                for cache_file in self.cache_dir.glob("*.cache"):
                    cache_file.unlink(missing_ok=True)
                    cleared += 1
                self.stats.file_entries = 0
            except Exception as e:
                logger.error(f"Error clearing file cache: {e}")

        self.stats.total_entries = 0
        return cleared

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        # Update file stats
        if self.enable_file_cache:
            file_entries = len(list(self.cache_dir.glob("*.cache")))
            file_size = sum(
                f.stat().st_size for f in self.cache_dir.glob("*.cache") if f.exists()
            )
            self.stats.file_entries = file_entries
            self.stats.file_size_bytes = file_size

        hit_rate = 0.0
        if self.stats.hit_count + self.stats.miss_count > 0:
            hit_rate = (
                self.stats.hit_count / (self.stats.hit_count + self.stats.miss_count)
            ) * 100

        return {
            "total_entries": len(self._memory_cache) + self.stats.file_entries,
            "memory_entries": len(self._memory_cache),
            "file_entries": self.stats.file_entries,
            "memory_size_bytes": self.stats.memory_size_bytes,
            "file_size_bytes": self.stats.file_size_bytes,
            "total_size_bytes": self.stats.memory_size_bytes
            + self.stats.file_size_bytes,
            "hit_count": self.stats.hit_count,
            "miss_count": self.stats.miss_count,
            "hit_rate_percent": round(hit_rate, 2),
            "eviction_count": self.stats.eviction_count,
            "cleanup_count": self.stats.cleanup_count,
            "max_memory_entries": self.max_memory_entries,
            "max_memory_size_mb": self.max_memory_size_bytes / (1024 * 1024),
            "cache_dir": str(self.cache_dir),
            "compression_enabled": self.enable_compression,
            "file_cache_enabled": self.enable_file_cache,
        }

    async def close(self):
        """Close cache manager and cleanup resources"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        # Final cleanup
        await self._cleanup_memory_cache()
        logger.info("Enhanced cache manager closed")


# Global enhanced cache instance
cache = EnhancedCacheManager()


# Decorator for caching function results
def cached(ttl: int = 300, key_func: Optional[Callable] = None):
    """Decorator to cache function results"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
                cache_key = ":".join(key_parts)

            # Check cache
            result = await cache.get(cache_key)
            if result is not None:
                return result

            # Execute function and cache result
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            await cache.set(cache_key, result, ttl)
            return result

        return wrapper

    return decorator


# Context manager for temporary cache settings
class TemporaryCacheSettings:
    """Context manager for temporary cache configuration"""

    def __init__(self, **settings):
        self.new_settings = settings
        self.old_settings = {}

    async def __aenter__(self):
        # Save old settings
        for key, value in self.new_settings.items():
            if hasattr(cache, key):
                self.old_settings[key] = getattr(cache, key)
                setattr(cache, key, value)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Restore old settings
        for key, value in self.old_settings.items():
            setattr(cache, key, value)


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
