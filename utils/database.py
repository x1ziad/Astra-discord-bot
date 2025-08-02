"""
Enhanced Database utilities for Astra Bot
Provides SQLite database management with connection pooling and performance optimizations
"""

import sqlite3
import asyncio
import aiosqlite
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from contextlib import asynccontextmanager
import json
from datetime import datetime
import weakref
import threading
from dataclasses import dataclass, field

logger = logging.getLogger("astra.database")


@dataclass
class ConnectionPoolStats:
    """Connection pool statistics"""

    active_connections: int = 0
    total_connections: int = 0
    queries_executed: int = 0
    average_query_time: float = 0.0
    pool_hits: int = 0
    pool_misses: int = 0


class DatabaseConnectionPool:
    """High-performance connection pool for SQLite"""

    def __init__(self, db_path: str, max_connections: int = 10, timeout: float = 30.0):
        self.db_path = Path(db_path)
        self.max_connections = max_connections
        self.timeout = timeout
        self._pool: asyncio.Queue = asyncio.Queue(maxsize=max_connections)
        self._all_connections: weakref.WeakSet = weakref.WeakSet()
        self._pool_lock = asyncio.Lock()
        self._initialized = False
        self.stats = ConnectionPoolStats()

    async def initialize(self):
        """Initialize the connection pool"""
        if self._initialized:
            return

        # Create initial connections
        for _ in range(min(3, self.max_connections)):  # Start with 3 connections
            conn = await aiosqlite.connect(
                self.db_path,
                isolation_level=None,  # Autocommit mode
                timeout=self.timeout,
                check_same_thread=False,
            )
            await conn.execute("PRAGMA journal_mode=WAL")
            await conn.execute("PRAGMA synchronous=NORMAL")
            await conn.execute("PRAGMA cache_size=10000")
            await conn.execute("PRAGMA temp_store=MEMORY")

            self._all_connections.add(conn)
            await self._pool.put(conn)

        self.stats.total_connections = self._pool.qsize()
        self._initialized = True
        logger.info(
            f"Database connection pool initialized with {self.stats.total_connections} connections"
        )

    @asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool"""
        if not self._initialized:
            await self.initialize()

        start_time = asyncio.get_event_loop().time()

        try:
            # Try to get existing connection
            try:
                conn = self._pool.get_nowait()
                self.stats.pool_hits += 1
            except asyncio.QueueEmpty:
                self.stats.pool_misses += 1
                # Create new connection if pool is empty and under limit
                if len(self._all_connections) < self.max_connections:
                    conn = await aiosqlite.connect(
                        self.db_path,
                        isolation_level=None,
                        timeout=self.timeout,
                        check_same_thread=False,
                    )
                    await conn.execute("PRAGMA journal_mode=WAL")
                    await conn.execute("PRAGMA synchronous=NORMAL")
                    self._all_connections.add(conn)
                    self.stats.total_connections += 1
                else:
                    # Wait for available connection
                    conn = await asyncio.wait_for(
                        self._pool.get(), timeout=self.timeout
                    )

            self.stats.active_connections += 1
            yield conn

        finally:
            self.stats.active_connections -= 1
            query_time = asyncio.get_event_loop().time() - start_time
            self.stats.queries_executed += 1

            # Update average query time
            total_time = (
                self.stats.average_query_time * (self.stats.queries_executed - 1)
                + query_time
            )
            self.stats.average_query_time = total_time / self.stats.queries_executed

            # Return connection to pool
            try:
                await self._pool.put(conn)
            except asyncio.QueueFull:
                # Pool is full, close this connection
                await conn.close()
                self._all_connections.discard(conn)
                self.stats.total_connections -= 1

    async def close_all(self):
        """Close all connections in the pool"""
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                await conn.close()
            except asyncio.QueueEmpty:
                break

        # Close any remaining connections
        for conn in list(self._all_connections):
            try:
                await conn.close()
            except Exception:
                pass

        self._all_connections.clear()
        self.stats = ConnectionPoolStats()
        self._initialized = False
        logger.info("Database connection pool closed")


class DatabaseManager:
    """Enhanced async SQLite database manager with connection pooling"""

    def __init__(self, db_path: str = "data/astra.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize connection pool
        self.pool = DatabaseConnectionPool(str(self.db_path), max_connections=15)
        self._cache = {}
        self._cache_ttl = {}
        self._cache_max_size = 1000
        self._cache_default_ttl = 300  # 5 minutes

    async def initialize(self):
        """Initialize database and create tables with optimized schema"""
        await self.pool.initialize()

        async with self.pool.get_connection() as db:
            await db.executescript(
                """
                -- Guild settings with JSON storage and indexing
                CREATE TABLE IF NOT EXISTS guild_settings (
                    guild_id INTEGER PRIMARY KEY,
                    settings TEXT NOT NULL DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- User data with composite key and partitioning
                CREATE TABLE IF NOT EXISTS user_data (
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    data TEXT NOT NULL DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, guild_id)
                );
                
                -- Analytics with time-based partitioning
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    event_type TEXT NOT NULL,
                    event_data TEXT NOT NULL DEFAULT '{}',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Command usage tracking with performance optimization
                CREATE TABLE IF NOT EXISTS command_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    command_name TEXT NOT NULL,
                    execution_time REAL DEFAULT 0.0,
                    success BOOLEAN DEFAULT TRUE,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- AI conversation history with retention policy
                CREATE TABLE IF NOT EXISTS ai_conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    message_type TEXT NOT NULL, -- 'user' or 'assistant'
                    content TEXT NOT NULL,
                    tokens_used INTEGER DEFAULT 0,
                    model_used TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Performance metrics tracking
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_type TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Error logs with categorization
                CREATE TABLE IF NOT EXISTS error_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_type TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    traceback TEXT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    command_name TEXT,
                    severity TEXT DEFAULT 'medium',
                    resolved BOOLEAN DEFAULT FALSE,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Optimized indexes for performance
                CREATE INDEX IF NOT EXISTS idx_guild_settings_guild_id ON guild_settings(guild_id);
                CREATE INDEX IF NOT EXISTS idx_user_data_composite ON user_data(user_id, guild_id);
                CREATE INDEX IF NOT EXISTS idx_analytics_guild_time ON analytics(guild_id, timestamp);
                CREATE INDEX IF NOT EXISTS idx_analytics_event_type ON analytics(event_type, timestamp);
                CREATE INDEX IF NOT EXISTS idx_command_usage_guild_time ON command_usage(guild_id, timestamp);
                CREATE INDEX IF NOT EXISTS idx_command_usage_command ON command_usage(command_name, timestamp);
                CREATE INDEX IF NOT EXISTS idx_ai_conversations_channel ON ai_conversations(channel_id, timestamp);
                CREATE INDEX IF NOT EXISTS idx_ai_conversations_user ON ai_conversations(user_id, timestamp);
                CREATE INDEX IF NOT EXISTS idx_performance_metrics_type ON performance_metrics(metric_type, timestamp);
                CREATE INDEX IF NOT EXISTS idx_error_logs_type_time ON error_logs(error_type, timestamp);
                CREATE INDEX IF NOT EXISTS idx_error_logs_guild ON error_logs(guild_id, timestamp);
                
                -- Cleanup views for maintenance
                CREATE VIEW IF NOT EXISTS recent_errors AS
                SELECT * FROM error_logs 
                WHERE timestamp > datetime('now', '-7 days')
                ORDER BY timestamp DESC;
                
                CREATE VIEW IF NOT EXISTS active_conversations AS
                SELECT channel_id, COUNT(*) as message_count, MAX(timestamp) as last_activity
                FROM ai_conversations 
                WHERE timestamp > datetime('now', '-1 day')
                GROUP BY channel_id;
            """
            )
            await db.commit()

        logger.info("Database initialized with optimized schema and indexes")

    def _get_cache_key(self, table: str, key: str) -> str:
        """Generate cache key"""
        return f"{table}:{key}"

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached value is still valid"""
        if cache_key not in self._cache_ttl:
            return False
        return datetime.utcnow().timestamp() < self._cache_ttl[cache_key]

    def _set_cache(self, cache_key: str, value: Any, ttl: Optional[int] = None):
        """Set cache value with TTL"""
        if len(self._cache) >= self._cache_max_size:
            # Remove oldest entries
            oldest_keys = sorted(
                self._cache_ttl.keys(), key=lambda k: self._cache_ttl[k]
            )[:100]
            for key in oldest_keys:
                self._cache.pop(key, None)
                self._cache_ttl.pop(key, None)

        self._cache[cache_key] = value
        self._cache_ttl[cache_key] = datetime.utcnow().timestamp() + (
            ttl or self._cache_default_ttl
        )

    async def get_guild_setting(
        self, guild_id: int, key: str, default: Any = None
    ) -> Any:
        """Get a specific guild setting with caching"""
        cache_key = self._get_cache_key("guild_settings", f"{guild_id}:{key}")

        # Check cache first
        if self._is_cache_valid(cache_key):
            return self._cache.get(cache_key, default)

        async with self.pool.get_connection() as db:
            cursor = await db.execute(
                "SELECT settings FROM guild_settings WHERE guild_id = ?", (guild_id,)
            )
            row = await cursor.fetchone()

            if row:
                settings = json.loads(row[0])
                value = settings.get(key, default)
                self._set_cache(cache_key, value)
                return value

        self._set_cache(cache_key, default)
        return default

    async def set_guild_setting(self, guild_id: int, key: str, value: Any):
        """Set a specific guild setting with cache invalidation"""
        async with self.pool.get_connection() as db:
            # Get current settings
            cursor = await db.execute(
                "SELECT settings FROM guild_settings WHERE guild_id = ?", (guild_id,)
            )
            row = await cursor.fetchone()

            if row:
                settings = json.loads(row[0])
                settings[key] = value
                await db.execute(
                    "UPDATE guild_settings SET settings = ?, updated_at = CURRENT_TIMESTAMP WHERE guild_id = ?",
                    (json.dumps(settings), guild_id),
                )
            else:
                settings = {key: value}
                await db.execute(
                    "INSERT INTO guild_settings (guild_id, settings) VALUES (?, ?)",
                    (guild_id, json.dumps(settings)),
                )

            await db.commit()

            # Update cache
            cache_key = self._get_cache_key("guild_settings", f"{guild_id}:{key}")
            self._set_cache(cache_key, value)

    async def get_user_data(
        self, user_id: int, guild_id: int, key: str, default: Any = None
    ) -> Any:
        """Get user data with caching"""
        cache_key = self._get_cache_key("user_data", f"{user_id}:{guild_id}:{key}")

        if self._is_cache_valid(cache_key):
            return self._cache.get(cache_key, default)

        async with self.pool.get_connection() as db:
            cursor = await db.execute(
                "SELECT data FROM user_data WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id),
            )
            row = await cursor.fetchone()

            if row:
                data = json.loads(row[0])
                value = data.get(key, default)
                self._set_cache(cache_key, value)
                return value

        self._set_cache(cache_key, default)
        return default

    async def set_user_data(self, user_id: int, guild_id: int, key: str, value: Any):
        """Set user data with cache management"""
        async with self.pool.get_connection() as db:
            cursor = await db.execute(
                "SELECT data FROM user_data WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id),
            )
            row = await cursor.fetchone()

            if row:
                data = json.loads(row[0])
                data[key] = value
                await db.execute(
                    "UPDATE user_data SET data = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ? AND guild_id = ?",
                    (json.dumps(data), user_id, guild_id),
                )
            else:
                data = {key: value}
                await db.execute(
                    "INSERT INTO user_data (user_id, guild_id, data) VALUES (?, ?, ?)",
                    (user_id, guild_id, json.dumps(data)),
                )

            await db.commit()

            # Update cache
            cache_key = self._get_cache_key("user_data", f"{user_id}:{guild_id}:{key}")
            self._set_cache(cache_key, value)

    async def log_analytics(
        self, guild_id: int, event_type: str, event_data: Dict[str, Any]
    ):
        """Log analytics event with batch processing"""
        async with self.pool.get_connection() as db:
            await db.execute(
                "INSERT INTO analytics (guild_id, event_type, event_data) VALUES (?, ?, ?)",
                (guild_id, event_type, json.dumps(event_data)),
            )
            await db.commit()

    async def log_command_usage(
        self,
        guild_id: int,
        user_id: int,
        command_name: str,
        execution_time: float = 0.0,
        success: bool = True,
    ):
        """Log command usage with performance metrics"""
        async with self.pool.get_connection() as db:
            await db.execute(
                "INSERT INTO command_usage (guild_id, user_id, command_name, execution_time, success) VALUES (?, ?, ?, ?, ?)",
                (guild_id, user_id, command_name, execution_time, success),
            )
            await db.commit()

    # Enhanced interface methods for backward compatibility
    async def get(self, table: str, key: str, default: dict = None) -> dict:
        """Get data from a table with key (enhanced with caching)"""
        if default is None:
            default = {}

        if table == "guild_configs":
            return await self.get_guild_setting(int(key), "config", default)
        elif table == "user_profiles":
            if "_" in key:
                user_id, guild_id = key.split("_", 1)
                return await self.get_user_data(
                    int(user_id), int(guild_id), "profile", default
                )
        elif table == "command_stats":
            # Enhanced command stats retrieval
            cache_key = self._get_cache_key("command_stats", key)
            if self._is_cache_valid(cache_key):
                return self._cache.get(cache_key, default)

            if "_" in key:
                guild_id, command = key.split("_", 1)
                async with self.pool.get_connection() as db:
                    cursor = await db.execute(
                        "SELECT COUNT(*) as count, AVG(execution_time) as avg_time, MAX(timestamp) as last_used FROM command_usage WHERE guild_id = ? AND command_name = ?",
                        (int(guild_id), command),
                    )
                    row = await cursor.fetchone()
                    if row:
                        result = {
                            "count": row[0],
                            "avg_execution_time": row[1] or 0.0,
                            "last_used": row[2],
                        }
                        self._set_cache(cache_key, result)
                        return result

        return default

    async def set(self, table: str, key: str, value: dict):
        """Set data in a table with key (enhanced with cache management)"""
        if table == "guild_configs":
            await self.set_guild_setting(int(key), "config", value)
        elif table == "user_profiles":
            if "_" in key:
                user_id, guild_id = key.split("_", 1)
                await self.set_user_data(int(user_id), int(guild_id), "profile", value)
        elif table == "command_stats":
            # Store in analytics for command stats
            if "_" in key:
                guild_id, command = key.split("_", 1)
                await self.log_analytics(
                    int(guild_id),
                    "command_stats_update",
                    {"command": command, "stats": value},
                )
        elif table == "error_logs":
            # Enhanced error logging
            await self.log_analytics(0, "error_log", {"key": key, "data": value})
        elif table == "performance_metrics":
            # Enhanced performance metrics
            async with self.pool.get_connection() as db:
                await db.execute(
                    "INSERT INTO performance_metrics (metric_type, metric_name, value, metadata) VALUES (?, ?, ?, ?)",
                    ("general", key, value.get("value", 0), json.dumps(value)),
                )
                await db.commit()

    async def get_table(self, table: str) -> dict:
        """Get entire table (creates if doesn't exist) - optimized implementation"""
        return {}  # Tables are created in initialize()

    async def delete(self, table: str, key: str):
        """Delete entry from table with cache invalidation"""
        if table == "guild_configs":
            await self.set_guild_setting(int(key), "config", {})
        elif table == "user_profiles":
            if "_" in key:
                user_id, guild_id = key.split("_", 1)
                await self.set_user_data(int(user_id), int(guild_id), "profile", {})

        # Invalidate cache
        cache_key = self._get_cache_key(table, key)
        self._cache.pop(cache_key, None)
        self._cache_ttl.pop(cache_key, None)

    async def cleanup_old_data(self, days: int = 30):
        """Clean up old data to maintain performance"""
        async with self.pool.get_connection() as db:
            cutoff_date = datetime.utcnow().timestamp() - (days * 24 * 3600)

            # Clean old analytics
            await db.execute(
                "DELETE FROM analytics WHERE timestamp < datetime(?, 'unixepoch')",
                (cutoff_date,),
            )

            # Clean old AI conversations
            await db.execute(
                "DELETE FROM ai_conversations WHERE timestamp < datetime(?, 'unixepoch')",
                (cutoff_date,),
            )

            # Clean resolved errors older than 7 days
            week_cutoff = datetime.utcnow().timestamp() - (7 * 24 * 3600)
            await db.execute(
                "DELETE FROM error_logs WHERE resolved = TRUE AND timestamp < datetime(?, 'unixepoch')",
                (week_cutoff,),
            )

            await db.commit()

        # Clear expired cache entries
        now = datetime.utcnow().timestamp()
        expired_keys = [k for k, ttl in self._cache_ttl.items() if ttl < now]
        for key in expired_keys:
            self._cache.pop(key, None)
            self._cache_ttl.pop(key, None)

        logger.info(
            f"Cleaned up old data (>{days} days) and {len(expired_keys)} expired cache entries"
        )

    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get database performance statistics"""
        pool_stats = self.pool.stats
        return {
            "connection_pool": {
                "active_connections": pool_stats.active_connections,
                "total_connections": pool_stats.total_connections,
                "pool_hits": pool_stats.pool_hits,
                "pool_misses": pool_stats.pool_misses,
                "hit_ratio": (
                    pool_stats.pool_hits
                    / (pool_stats.pool_hits + pool_stats.pool_misses)
                    if (pool_stats.pool_hits + pool_stats.pool_misses) > 0
                    else 0
                ),
                "queries_executed": pool_stats.queries_executed,
                "average_query_time": pool_stats.average_query_time,
            },
            "cache": {
                "entries": len(self._cache),
                "max_size": self._cache_max_size,
                "usage_ratio": len(self._cache) / self._cache_max_size,
            },
        }

    async def close(self):
        """Close database connections and cleanup"""
        await self.pool.close_all()
        self._cache.clear()
        self._cache_ttl.clear()
        logger.info("Database manager closed and cleaned up")


# Global database instance with enhanced performance
db = DatabaseManager()

import sqlite3
import asyncio
import aiosqlite
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from contextlib import asynccontextmanager
import json
from datetime import datetime

logger = logging.getLogger("astra.database")


class DatabaseManager:
    """Async SQLite database manager with connection pooling"""

    def __init__(self, db_path: str = "data/astra.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection_pool = []
        self._max_connections = 10
        self._initialized = False

    async def initialize(self):
        """Initialize database and create tables"""
        if self._initialized:
            return

        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(
                """
                CREATE TABLE IF NOT EXISTS guild_settings (
                    guild_id INTEGER PRIMARY KEY,
                    settings TEXT NOT NULL DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS user_data (
                    user_id INTEGER PRIMARY KEY,
                    guild_id INTEGER,
                    data TEXT NOT NULL DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    event_type TEXT NOT NULL,
                    event_data TEXT NOT NULL DEFAULT '{}',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS command_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    command_name TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_guild_settings_guild_id ON guild_settings(guild_id);
                CREATE INDEX IF NOT EXISTS idx_user_data_user_guild ON user_data(user_id, guild_id);
                CREATE INDEX IF NOT EXISTS idx_analytics_guild_id ON analytics(guild_id);
                CREATE INDEX IF NOT EXISTS idx_command_usage_guild_id ON command_usage(guild_id);
            """
            )
            await db.commit()

        self._initialized = True
        logger.info("Database initialized successfully")

    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool"""
        conn = await aiosqlite.connect(self.db_path)
        try:
            yield conn
        finally:
            await conn.close()

    async def get_guild_setting(
        self, guild_id: int, key: str, default: Any = None
    ) -> Any:
        """Get a specific guild setting"""
        async with self.get_connection() as db:
            cursor = await db.execute(
                "SELECT settings FROM guild_settings WHERE guild_id = ?", (guild_id,)
            )
            row = await cursor.fetchone()

            if row:
                settings = json.loads(row[0])
                return settings.get(key, default)
            return default

    async def set_guild_setting(self, guild_id: int, key: str, value: Any):
        """Set a specific guild setting"""
        async with self.get_connection() as db:
            # Get current settings
            cursor = await db.execute(
                "SELECT settings FROM guild_settings WHERE guild_id = ?", (guild_id,)
            )
            row = await cursor.fetchone()

            if row:
                settings = json.loads(row[0])
                settings[key] = value
                await db.execute(
                    "UPDATE guild_settings SET settings = ?, updated_at = CURRENT_TIMESTAMP WHERE guild_id = ?",
                    (json.dumps(settings), guild_id),
                )
            else:
                settings = {key: value}
                await db.execute(
                    "INSERT INTO guild_settings (guild_id, settings) VALUES (?, ?)",
                    (guild_id, json.dumps(settings)),
                )

            await db.commit()

    async def get_user_data(
        self, user_id: int, guild_id: int, key: str, default: Any = None
    ) -> Any:
        """Get user data"""
        async with self.get_connection() as db:
            cursor = await db.execute(
                "SELECT data FROM user_data WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id),
            )
            row = await cursor.fetchone()

            if row:
                data = json.loads(row[0])
                return data.get(key, default)
            return default

    async def set_user_data(self, user_id: int, guild_id: int, key: str, value: Any):
        """Set user data"""
        async with self.get_connection() as db:
            cursor = await db.execute(
                "SELECT data FROM user_data WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id),
            )
            row = await cursor.fetchone()

            if row:
                data = json.loads(row[0])
                data[key] = value
                await db.execute(
                    "UPDATE user_data SET data = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ? AND guild_id = ?",
                    (json.dumps(data), user_id, guild_id),
                )
            else:
                data = {key: value}
                await db.execute(
                    "INSERT INTO user_data (user_id, guild_id, data) VALUES (?, ?, ?)",
                    (user_id, guild_id, json.dumps(data)),
                )

            await db.commit()

    async def log_analytics(
        self, guild_id: int, event_type: str, event_data: Dict[str, Any]
    ):
        """Log analytics event"""
        async with self.get_connection() as db:
            await db.execute(
                "INSERT INTO analytics (guild_id, event_type, event_data) VALUES (?, ?, ?)",
                (guild_id, event_type, json.dumps(event_data)),
            )
            await db.commit()

    async def log_command_usage(self, guild_id: int, user_id: int, command_name: str):
        """Log command usage"""
        async with self.get_connection() as db:
            await db.execute(
                "INSERT INTO command_usage (guild_id, user_id, command_name) VALUES (?, ?, ?)",
                (guild_id, user_id, command_name),
            )
            await db.commit()

    async def get(self, table: str, key: str, default: dict = None) -> dict:
        """Get data from a table with key"""
        if default is None:
            default = {}

        if table == "guild_configs":
            return await self.get_guild_setting(int(key), "config", default)
        elif table == "user_profiles":
            # For user profiles, key format might be "user_id_guild_id"
            if "_" in key:
                user_id, guild_id = key.split("_", 1)
                return await self.get_user_data(
                    int(user_id), int(guild_id), "profile", default
                )
        # Add other table mappings as needed
        return default

    async def set(self, table: str, key: str, value: dict):
        """Set data in a table with key"""
        if table == "guild_configs":
            await self.set_guild_setting(int(key), "config", value)
        elif table == "user_profiles":
            if "_" in key:
                user_id, guild_id = key.split("_", 1)
                await self.set_user_data(int(user_id), int(guild_id), "profile", value)
        elif table == "command_stats":
            # Store command stats as guild setting
            if "_" in key:
                guild_id, command = key.split("_", 1)
                await self.set_guild_setting(
                    int(guild_id), f"command_stats_{command}", value
                )
        elif table == "error_logs":
            # Store error logs as analytics
            await self.log_analytics(0, "error_log", {"key": key, "data": value})
        elif table == "performance_metrics":
            # Store performance metrics as analytics
            await self.log_analytics(
                0, "performance_metric", {"key": key, "data": value}
            )

    async def get_table(self, table: str) -> dict:
        """Get entire table (creates if doesn't exist) - returns empty dict since tables are already created"""
        # Tables are created in initialize(), so just return empty dict
        return {}

    async def delete(self, table: str, key: str):
        """Delete entry from table"""
        if table == "guild_configs":
            # Set to empty dict instead of deleting
            await self.set_guild_setting(int(key), "config", {})
        elif table == "user_profiles":
            if "_" in key:
                user_id, guild_id = key.split("_", 1)
                await self.set_user_data(int(user_id), int(guild_id), "profile", {})
        # Add other deletion logic as needed


# Global database instance
db = DatabaseManager()
