"""
Simple JSON-based database handler for Astra Bot
For production, consider migrating to PostgreSQL or MongoDB
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger("astra.database")


class JSONDatabase:
    """Simple JSON-based database with async operations"""

    def __init__(self, db_path: str = "data/database"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        self._cache = {}
        self._locks = {}

    def _get_lock(self, table: str) -> asyncio.Lock:
        """Get or create lock for table"""
        if table not in self._locks:
            self._locks[table] = asyncio.Lock()
        return self._locks[table]

    async def get_table(self, table: str) -> Dict[str, Any]:
        """Get entire table data"""
        async with self._get_lock(table):
            if table not in self._cache:
                file_path = self.db_path / f"{table}.json"
                if file_path.exists():
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            self._cache[table] = json.load(f)
                    except Exception as e:
                        logger.error(f"Error loading table {table}: {e}")
                        self._cache[table] = {}
                else:
                    self._cache[table] = {}

            return self._cache[table].copy()

    async def save_table(self, table: str, data: Dict[str, Any]):
        """Save table data"""
        async with self._get_lock(table):
            try:
                file_path = self.db_path / f"{table}.json"
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, default=str)
                self._cache[table] = data.copy()
                logger.debug(f"Saved table {table}")
            except Exception as e:
                logger.error(f"Error saving table {table}: {e}")
                raise

    async def get(self, table: str, key: str, default: Any = None) -> Any:
        """Get value from table"""
        data = await self.get_table(table)
        return data.get(key, default)

    async def set(self, table: str, key: str, value: Any):
        """Set value in table"""
        data = await self.get_table(table)
        data[key] = value
        await self.save_table(table, data)

    async def delete(self, table: str, key: str) -> bool:
        """Delete key from table"""
        data = await self.get_table(table)
        if key in data:
            del data[key]
            await self.save_table(table, data)
            return True
        return False

    async def exists(self, table: str, key: str) -> bool:
        """Check if key exists in table"""
        data = await self.get_table(table)
        return key in data


# Global database instance
db = JSONDatabase()
