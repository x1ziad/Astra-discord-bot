"""
Database utilities for Astra Bot
Provides SQLite database management with connection pooling
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

    # Add these methods to your DatabaseManager class:


async def get(self, table: str, key: str, default: dict = None) -> dict:
    """Get data from a table with key"""
    if default is None:
        default = {}

    if table == "guild_configs":
        return await self.get_guild_setting(int(key), "config", default)
    # Add other table mappings as needed
    return default


async def set(self, table: str, key: str, value: dict):
    """Set data in a table with key"""
    if table == "guild_configs":
        await self.set_guild_setting(int(key), "config", value)
    # Add other table mappings as needed


async def get_table(self, table: str) -> dict:
    """Get entire table (creates if doesn't exist)"""
    # This method should return table data or empty dict
    return {}


async def delete(self, table: str, key: str):
    """Delete entry from table"""
    # Implement deletion logic
    pass


# Global database instance
db = DatabaseManager()
