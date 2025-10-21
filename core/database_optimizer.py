"""
🗃️ ULTRA-HIGH-PERFORMANCE DATABASE OPTIMIZATION SYSTEM
Advanced database operations with connection pooling, caching, and optimization

Features:
- Connection pooling for maximum efficiency
- Multi-layer caching system
- Optimized query patterns
- Automatic performance tuning
- Data persistence optimization
- Real-time performance monitoring
"""

import asyncio
import sqlite3
import json
import time
import logging
import threading
from typing import Dict, List, Any, Optional, Tuple, Union
from collections import defaultdict, deque
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from functools import lru_cache
import weakref
import hashlib


@dataclass
class DatabaseMetrics:
    """📊 Database performance metrics"""

    timestamp: float
    queries_executed: int
    avg_query_time: float
    cache_hit_rate: float
    connection_pool_size: int
    active_connections: int
    total_connections_created: int
    query_errors: int
    data_size_mb: float


class ConnectionPool:
    """🏊 High-performance database connection pool"""

    def __init__(
        self, database_path: str, max_connections: int = 10, timeout: float = 30.0
    ):
        self.database_path = database_path
        self.max_connections = max_connections
        self.timeout = timeout

        self._pool = deque()
        self._active_connections = set()
        self._lock = asyncio.Lock()
        self._created_connections = 0

        # Performance tracking
        self.metrics = {
            "connections_created": 0,
            "connections_reused": 0,
            "connection_errors": 0,
            "pool_exhausted_count": 0,
        }

    async def get_connection(self) -> sqlite3.Connection:
        """🔌 Get a database connection from the pool"""
        async with self._lock:
            # Try to reuse existing connection
            if self._pool:
                conn = self._pool.popleft()
                self._active_connections.add(conn)
                self.metrics["connections_reused"] += 1
                return conn

            # Create new connection if under limit
            if len(self._active_connections) < self.max_connections:
                try:
                    conn = sqlite3.connect(
                        self.database_path,
                        timeout=self.timeout,
                        check_same_thread=False,
                    )

                    # Optimize connection settings
                    conn.execute("PRAGMA journal_mode=WAL")
                    conn.execute("PRAGMA synchronous=NORMAL")
                    conn.execute("PRAGMA cache_size=10000")
                    conn.execute("PRAGMA temp_store=MEMORY")
                    conn.execute("PRAGMA mmap_size=268435456")  # 256MB

                    self._active_connections.add(conn)
                    self._created_connections += 1
                    self.metrics["connections_created"] += 1
                    return conn

                except Exception as e:
                    self.metrics["connection_errors"] += 1
                    raise

            # Pool exhausted
            self.metrics["pool_exhausted_count"] += 1
            raise Exception("Connection pool exhausted")

    async def return_connection(self, conn: sqlite3.Connection):
        """🔄 Return a connection to the pool"""
        async with self._lock:
            if conn in self._active_connections:
                self._active_connections.remove(conn)

                # Check if connection is still valid
                try:
                    conn.execute("SELECT 1")
                    self._pool.append(conn)
                except:
                    # Connection is broken, close it
                    try:
                        conn.close()
                    except:
                        pass

    async def close_all(self):
        """🚪 Close all connections"""
        async with self._lock:
            # Close active connections
            for conn in list(self._active_connections):
                try:
                    conn.close()
                except:
                    pass
            self._active_connections.clear()

            # Close pooled connections
            while self._pool:
                conn = self._pool.popleft()
                try:
                    conn.close()
                except:
                    pass


class QueryCache:
    """📦 Advanced query result caching system"""

    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self.max_size = max_size
        self.ttl = ttl

        self._cache = {}
        self._access_times = {}
        self._creation_times = {}

        # Performance metrics
        self.metrics = {"hits": 0, "misses": 0, "evictions": 0, "expired_entries": 0}

    def _generate_key(self, query: str, params: Tuple = ()) -> str:
        """🔑 Generate cache key for query"""
        query_hash = hashlib.md5(f"{query}{params}".encode()).hexdigest()
        return query_hash

    def get(self, query: str, params: Tuple = ()) -> Optional[Any]:
        """📖 Get cached query result"""
        key = self._generate_key(query, params)
        current_time = time.time()

        if key in self._cache:
            # Check if expired
            if current_time - self._creation_times[key] > self.ttl:
                self._remove_key(key)
                self.metrics["expired_entries"] += 1
                self.metrics["misses"] += 1
                return None

            # Update access time and return cached result
            self._access_times[key] = current_time
            self.metrics["hits"] += 1
            return self._cache[key]

        self.metrics["misses"] += 1
        return None

    def set(self, query: str, params: Tuple, result: Any):
        """💾 Cache query result"""
        key = self._generate_key(query, params)
        current_time = time.time()

        # Check if cache is full
        if len(self._cache) >= self.max_size and key not in self._cache:
            self._evict_oldest()

        self._cache[key] = result
        self._access_times[key] = current_time
        self._creation_times[key] = current_time

    def _remove_key(self, key: str):
        """🗑️ Remove key from cache"""
        self._cache.pop(key, None)
        self._access_times.pop(key, None)
        self._creation_times.pop(key, None)

    def _evict_oldest(self):
        """⏰ Evict least recently used entry"""
        if not self._access_times:
            return

        oldest_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        self._remove_key(oldest_key)
        self.metrics["evictions"] += 1

    def clear(self):
        """🧹 Clear all cached entries"""
        evicted = len(self._cache)
        self._cache.clear()
        self._access_times.clear()
        self._creation_times.clear()
        self.metrics["evictions"] += evicted

    def get_hit_rate(self) -> float:
        """📊 Calculate cache hit rate"""
        total = self.metrics["hits"] + self.metrics["misses"]
        return (self.metrics["hits"] / total * 100) if total > 0 else 0.0


class UltraHighPerformanceDatabase:
    """🚀 Ultra-high-performance database system"""

    def __init__(self, database_path: str = "astra_security.db"):
        self.database_path = database_path
        self.logger = logging.getLogger("astra.database")

        # 🏊 CONNECTION POOL
        self.connection_pool = ConnectionPool(database_path, max_connections=20)

        # 📦 MULTI-LAYER CACHING
        self.query_cache = QueryCache(max_size=2000, ttl=600)  # 10 minute TTL
        self.result_cache = QueryCache(max_size=1000, ttl=300)  # 5 minute TTL
        self.metadata_cache = {}

        # 📊 PERFORMANCE TRACKING
        self.metrics = DatabaseMetrics(
            timestamp=time.time(),
            queries_executed=0,
            avg_query_time=0.0,
            cache_hit_rate=0.0,
            connection_pool_size=0,
            active_connections=0,
            total_connections_created=0,
            query_errors=0,
            data_size_mb=0.0,
        )

        # 🎯 OPTIMIZATION SETTINGS
        self.optimization_settings = {
            "batch_size": 100,
            "auto_vacuum": True,
            "analyze_frequency": 3600,  # 1 hour
            "optimize_frequency": 86400,  # 24 hours
            "cache_warming_enabled": True,
            "query_optimization": True,
            "parallel_queries": True,
        }

        # 📈 ANALYTICS
        self.analytics = {
            "queries_by_type": defaultdict(int),
            "query_times": deque(maxlen=1000),
            "error_log": deque(maxlen=100),
            "optimization_history": deque(maxlen=50),
        }

        self._monitoring_active = False
        self._last_optimization = time.time()

        # Initialize database
        asyncio.create_task(self._initialize_database())

    async def _initialize_database(self):
        """🚀 Initialize high-performance database"""
        try:
            conn = await self.connection_pool.get_connection()

            # Create optimized tables
            await self._create_tables(conn)

            # Create indexes for performance
            await self._create_indexes(conn)

            # Optimize database settings
            await self._optimize_database_settings(conn)

            await self.connection_pool.return_connection(conn)

            self.logger.info("🚀 Ultra-high-performance database initialized")

        except Exception as e:
            self.logger.error(f"❌ Database initialization failed: {e}")
            raise

    async def _create_tables(self, conn: sqlite3.Connection):
        """📋 Create optimized database tables"""

        tables = [
            # User profiles table
            """
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER PRIMARY KEY,
                trust_score REAL NOT NULL DEFAULT 100.0,
                risk_level TEXT NOT NULL DEFAULT 'low',
                violation_count INTEGER NOT NULL DEFAULT 0,
                positive_interactions INTEGER NOT NULL DEFAULT 0,
                last_violation_time REAL,
                improvement_streak INTEGER NOT NULL DEFAULT 0,
                behavioral_data TEXT,  -- JSON data
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
            """,
            # Violations table
            """
            CREATE TABLE IF NOT EXISTS violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                violation_type TEXT NOT NULL,
                severity REAL NOT NULL DEFAULT 1.0,
                message_content TEXT,
                channel_id INTEGER,
                guild_id INTEGER,
                timestamp REAL NOT NULL,
                action_taken TEXT,
                resolved BOOLEAN NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )
            """,
            # Security events table
            """
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                severity INTEGER NOT NULL,
                user_id INTEGER,
                channel_id INTEGER,
                guild_id INTEGER,
                details TEXT,  -- JSON data
                timestamp REAL NOT NULL,
                resolved BOOLEAN NOT NULL DEFAULT 0
            )
            """,
            # Performance metrics table
            """
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_type TEXT NOT NULL,
                metric_value REAL NOT NULL,
                details TEXT,  -- JSON data
                timestamp REAL NOT NULL
            )
            """,
            # Trust predictions table
            """
            CREATE TABLE IF NOT EXISTS trust_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                predicted_score REAL NOT NULL,
                confidence REAL NOT NULL,
                time_horizon INTEGER NOT NULL,
                actual_score REAL,
                accuracy REAL,
                created_at REAL NOT NULL,
                evaluated_at REAL,
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )
            """,
            # Behavioral patterns table
            """
            CREATE TABLE IF NOT EXISTS behavioral_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,  -- JSON data
                confidence REAL NOT NULL,
                timestamp REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )
            """,
        ]

        for table_sql in tables:
            conn.execute(table_sql)

        conn.commit()

    async def _create_indexes(self, conn: sqlite3.Connection):
        """📇 Create performance indexes"""

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_user_profiles_trust_score ON user_profiles (trust_score)",
            "CREATE INDEX IF NOT EXISTS idx_user_profiles_risk_level ON user_profiles (risk_level)",
            "CREATE INDEX IF NOT EXISTS idx_user_profiles_updated_at ON user_profiles (updated_at)",
            "CREATE INDEX IF NOT EXISTS idx_violations_user_id ON violations (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_violations_timestamp ON violations (timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_violations_type ON violations (violation_type)",
            "CREATE INDEX IF NOT EXISTS idx_violations_severity ON violations (severity)",
            "CREATE INDEX IF NOT EXISTS idx_security_events_timestamp ON security_events (timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_security_events_type ON security_events (event_type)",
            "CREATE INDEX IF NOT EXISTS idx_security_events_severity ON security_events (severity)",
            "CREATE INDEX IF NOT EXISTS idx_security_events_user_id ON security_events (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_performance_timestamp ON performance_metrics (timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_performance_type ON performance_metrics (metric_type)",
            "CREATE INDEX IF NOT EXISTS idx_trust_predictions_user_id ON trust_predictions (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_trust_predictions_created_at ON trust_predictions (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_behavioral_patterns_user_id ON behavioral_patterns (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_behavioral_patterns_type ON behavioral_patterns (pattern_type)",
            "CREATE INDEX IF NOT EXISTS idx_behavioral_patterns_timestamp ON behavioral_patterns (timestamp)",
        ]

        for index_sql in indexes:
            conn.execute(index_sql)

        conn.commit()

    async def _optimize_database_settings(self, conn: sqlite3.Connection):
        """⚡ Optimize database for maximum performance"""

        optimizations = [
            "PRAGMA journal_mode=WAL",
            "PRAGMA synchronous=NORMAL",
            "PRAGMA cache_size=50000",  # 50MB cache
            "PRAGMA temp_store=MEMORY",
            "PRAGMA mmap_size=1073741824",  # 1GB memory map
            "PRAGMA page_size=32768",  # 32KB pages
            "PRAGMA auto_vacuum=INCREMENTAL",
            "PRAGMA wal_checkpoint_threshold=1000",
            "PRAGMA optimize",
        ]

        for optimization in optimizations:
            try:
                conn.execute(optimization)
            except Exception as e:
                self.logger.debug(f"Optimization '{optimization}' failed: {e}")

        conn.commit()

    async def execute_query(
        self, query: str, params: Tuple = (), fetch: str = None
    ) -> Any:
        """⚡ Execute optimized database query"""

        start_time = time.time()

        try:
            # Check cache first
            if fetch and self.optimization_settings["query_optimization"]:
                cached_result = self.query_cache.get(query, params)
                if cached_result is not None:
                    return cached_result

            # Get connection and execute query
            conn = await self.connection_pool.get_connection()

            try:
                cursor = conn.cursor()
                cursor.execute(query, params)

                result = None
                if fetch == "one":
                    result = cursor.fetchone()
                elif fetch == "all":
                    result = cursor.fetchall()
                elif fetch == "many":
                    result = cursor.fetchmany(self.optimization_settings["batch_size"])
                else:
                    conn.commit()
                    result = cursor.rowcount

                # Cache result if appropriate
                if fetch and result is not None:
                    self.query_cache.set(query, params, result)

                # Update metrics
                execution_time = time.time() - start_time
                self._update_query_metrics(query, execution_time, success=True)

                return result

            finally:
                await self.connection_pool.return_connection(conn)

        except Exception as e:
            execution_time = time.time() - start_time
            self._update_query_metrics(
                query, execution_time, success=False, error=str(e)
            )
            self.logger.error(f"❌ Query execution failed: {e}")
            raise

    def _update_query_metrics(
        self, query: str, execution_time: float, success: bool, error: str = None
    ):
        """📊 Update query performance metrics"""

        # Update general metrics
        self.metrics.queries_executed += 1

        # Update average query time
        self.analytics["query_times"].append(execution_time)
        if self.analytics["query_times"]:
            self.metrics.avg_query_time = sum(self.analytics["query_times"]) / len(
                self.analytics["query_times"]
            )

        # Update cache hit rate
        self.metrics.cache_hit_rate = self.query_cache.get_hit_rate()

        # Track query types
        query_type = query.strip().split()[0].upper()
        self.analytics["queries_by_type"][query_type] += 1

        # Track errors
        if not success:
            self.metrics.query_errors += 1
            self.analytics["error_log"].append(
                {
                    "timestamp": time.time(),
                    "query": query[:100],  # First 100 chars
                    "error": error,
                    "execution_time": execution_time,
                }
            )

    async def batch_execute(self, queries: List[Tuple[str, Tuple]]) -> List[Any]:
        """📦 Execute multiple queries in optimized batch"""

        if not queries:
            return []

        start_time = time.time()
        results = []

        try:
            conn = await self.connection_pool.get_connection()

            try:
                # Execute all queries in a single transaction
                conn.execute("BEGIN TRANSACTION")

                for query, params in queries:
                    cursor = conn.cursor()
                    cursor.execute(query, params)
                    results.append(cursor.rowcount)

                conn.commit()

                # Update metrics
                execution_time = time.time() - start_time
                self.logger.debug(
                    f"📦 Batch executed {len(queries)} queries in {execution_time:.3f}s"
                )

                return results

            except Exception as e:
                conn.rollback()
                raise
            finally:
                await self.connection_pool.return_connection(conn)

        except Exception as e:
            self.logger.error(f"❌ Batch execution failed: {e}")
            raise

    async def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """👤 Get user profile with caching"""

        query = """
        SELECT user_id, trust_score, risk_level, violation_count, positive_interactions,
               last_violation_time, improvement_streak, behavioral_data, created_at, updated_at
        FROM user_profiles WHERE user_id = ?
        """

        result = await self.execute_query(query, (user_id,), fetch="one")

        if result:
            return {
                "user_id": result[0],
                "trust_score": result[1],
                "risk_level": result[2],
                "violation_count": result[3],
                "positive_interactions": result[4],
                "last_violation_time": result[5],
                "improvement_streak": result[6],
                "behavioral_data": json.loads(result[7]) if result[7] else {},
                "created_at": result[8],
                "updated_at": result[9],
            }

        return None

    async def upsert_user_profile(self, user_data: Dict[str, Any]) -> bool:
        """💾 Insert or update user profile"""

        current_time = time.time()

        query = """
        INSERT OR REPLACE INTO user_profiles 
        (user_id, trust_score, risk_level, violation_count, positive_interactions,
         last_violation_time, improvement_streak, behavioral_data, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT created_at FROM user_profiles WHERE user_id = ?), ?), ?)
        """

        params = (
            user_data["user_id"],
            user_data.get("trust_score", 100.0),
            user_data.get("risk_level", "low"),
            user_data.get("violation_count", 0),
            user_data.get("positive_interactions", 0),
            user_data.get("last_violation_time"),
            user_data.get("improvement_streak", 0),
            json.dumps(user_data.get("behavioral_data", {})),
            user_data["user_id"],  # For COALESCE
            current_time,  # created_at fallback
            current_time,  # updated_at
        )

        try:
            await self.execute_query(query, params)
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to upsert user profile: {e}")
            return False

    async def log_violation(self, violation_data: Dict[str, Any]) -> bool:
        """⚠️ Log security violation"""

        query = """
        INSERT INTO violations 
        (user_id, violation_type, severity, message_content, channel_id, guild_id, 
         timestamp, action_taken, resolved)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            violation_data["user_id"],
            violation_data["violation_type"],
            violation_data.get("severity", 1.0),
            violation_data.get("message_content", ""),
            violation_data.get("channel_id"),
            violation_data.get("guild_id"),
            violation_data.get("timestamp", time.time()),
            violation_data.get("action_taken", ""),
            violation_data.get("resolved", False),
        )

        try:
            await self.execute_query(query, params)
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to log violation: {e}")
            return False

    async def get_user_violations(
        self, user_id: int, days: int = 30
    ) -> List[Dict[str, Any]]:
        """📊 Get user violations with time filter"""

        cutoff_time = time.time() - (days * 86400)

        query = """
        SELECT violation_type, severity, message_content, channel_id, guild_id,
               timestamp, action_taken, resolved
        FROM violations 
        WHERE user_id = ? AND timestamp > ?
        ORDER BY timestamp DESC
        """

        results = await self.execute_query(query, (user_id, cutoff_time), fetch="all")

        violations = []
        for result in results or []:
            violations.append(
                {
                    "violation_type": result[0],
                    "severity": result[1],
                    "message_content": result[2],
                    "channel_id": result[3],
                    "guild_id": result[4],
                    "timestamp": result[5],
                    "action_taken": result[6],
                    "resolved": bool(result[7]),
                }
            )

        return violations

    async def store_trust_prediction(self, prediction_data: Dict[str, Any]) -> bool:
        """🔮 Store trust prediction for validation"""

        query = """
        INSERT INTO trust_predictions 
        (user_id, predicted_score, confidence, time_horizon, created_at)
        VALUES (?, ?, ?, ?, ?)
        """

        params = (
            prediction_data["user_id"],
            prediction_data["predicted_score"],
            prediction_data["confidence"],
            prediction_data["time_horizon"],
            time.time(),
        )

        try:
            await self.execute_query(query, params)
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to store trust prediction: {e}")
            return False

    async def get_database_analytics(self) -> Dict[str, Any]:
        """📊 Get comprehensive database analytics"""

        # Update connection pool metrics
        self.metrics.connection_pool_size = len(self.connection_pool._pool)
        self.metrics.active_connections = len(self.connection_pool._active_connections)
        self.metrics.total_connections_created = (
            self.connection_pool._created_connections
        )

        # Calculate database size
        try:
            conn = await self.connection_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            self.metrics.data_size_mb = (page_count * page_size) / (1024 * 1024)
            await self.connection_pool.return_connection(conn)
        except Exception as e:
            self.logger.debug(f"Failed to calculate database size: {e}")

        return {
            "timestamp": time.time(),
            "metrics": asdict(self.metrics),
            "analytics": {
                "queries_by_type": dict(self.analytics["queries_by_type"]),
                "recent_query_times": list(self.analytics["query_times"])[-20:],
                "recent_errors": list(self.analytics["error_log"])[-5:],
                "optimization_history": list(self.analytics["optimization_history"])[
                    -10:
                ],
            },
            "cache_stats": {
                "query_cache": self.query_cache.metrics.copy(),
                "result_cache": self.result_cache.metrics.copy(),
            },
            "connection_pool_stats": self.connection_pool.metrics.copy(),
            "optimization_settings": self.optimization_settings.copy(),
        }

    async def start_monitoring(self):
        """📊 Start database performance monitoring"""
        if self._monitoring_active:
            return

        self._monitoring_active = True
        self.logger.info("📊 Starting database performance monitoring")

        # Start monitoring tasks
        asyncio.create_task(self._performance_monitor())
        asyncio.create_task(self._auto_optimizer())

    async def _performance_monitor(self):
        """📈 Monitor database performance"""
        while self._monitoring_active:
            try:
                # Update metrics timestamp
                self.metrics.timestamp = time.time()

                # Log performance metrics
                analytics = await self.get_database_analytics()
                self.logger.debug(f"📊 Database Performance: {analytics['metrics']}")

                await asyncio.sleep(300)  # Every 5 minutes

            except Exception as e:
                self.logger.error(f"❌ Performance monitoring error: {e}")
                await asyncio.sleep(600)

    async def _auto_optimizer(self):
        """🚀 Automatic database optimization"""
        while self._monitoring_active:
            try:
                current_time = time.time()

                # Run optimization every 24 hours
                if (
                    current_time - self._last_optimization
                    > self.optimization_settings["optimize_frequency"]
                ):
                    await self._optimize_database()
                    self._last_optimization = current_time

                await asyncio.sleep(3600)  # Check every hour

            except Exception as e:
                self.logger.error(f"❌ Auto-optimizer error: {e}")
                await asyncio.sleep(7200)

    async def _optimize_database(self):
        """⚡ Perform database optimization"""

        optimization_start = time.time()

        try:
            conn = await self.connection_pool.get_connection()

            # Analyze tables for query optimization
            conn.execute("ANALYZE")

            # Vacuum if enabled
            if self.optimization_settings["auto_vacuum"]:
                conn.execute("PRAGMA incremental_vacuum")

            # Optimize database
            conn.execute("PRAGMA optimize")

            # Clear old data (older than 90 days)
            cutoff_time = time.time() - (90 * 86400)

            # Clean old violations
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM violations WHERE timestamp < ? AND resolved = 1",
                (cutoff_time,),
            )
            violations_cleaned = cursor.rowcount

            # Clean old security events
            cursor.execute(
                "DELETE FROM security_events WHERE timestamp < ? AND resolved = 1",
                (cutoff_time,),
            )
            events_cleaned = cursor.rowcount

            # Clean old performance metrics
            cursor.execute(
                "DELETE FROM performance_metrics WHERE timestamp < ?", (cutoff_time,)
            )
            metrics_cleaned = cursor.rowcount

            conn.commit()
            await self.connection_pool.return_connection(conn)

            optimization_time = time.time() - optimization_start

            # Log optimization results
            optimization_result = {
                "timestamp": time.time(),
                "optimization_time": optimization_time,
                "violations_cleaned": violations_cleaned,
                "events_cleaned": events_cleaned,
                "metrics_cleaned": metrics_cleaned,
            }

            self.analytics["optimization_history"].append(optimization_result)

            self.logger.info(
                f"🚀 Database optimization completed in {optimization_time:.2f}s: "
                f"cleaned {violations_cleaned + events_cleaned + metrics_cleaned} old records"
            )

        except Exception as e:
            self.logger.error(f"❌ Database optimization failed: {e}")

    async def close(self):
        """🚪 Close database and cleanup resources"""
        self._monitoring_active = False

        # Clear caches
        self.query_cache.clear()
        self.result_cache.clear()
        self.metadata_cache.clear()

        # Close connection pool
        await self.connection_pool.close_all()

        self.logger.info("🚪 Database closed successfully")


# Global database instance
database = UltraHighPerformanceDatabase()


def get_database() -> UltraHighPerformanceDatabase:
    """Get the global database instance"""
    return database
