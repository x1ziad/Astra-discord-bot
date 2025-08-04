"""
Quick Database Debug Test
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.database import db


async def debug_database():
    print("🔍 Database Debug Test")
    print("-" * 40)

    # Initialize
    await db.initialize()
    print("✅ Database initialized")

    # Test set
    test_data = {"test": "value", "timestamp": "2025-01-01"}
    await db.set("test_table", "test_key", test_data)
    print(f"✅ SET: {test_data}")

    # Test get
    retrieved = await db.get("test_table", "test_key")
    print(f"📥 GET: {retrieved}")
    print(f"🔄 Match: {retrieved == test_data}")

    # Debug what's actually stored
    if hasattr(db, "get_connection"):
        async with db.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table';"
            )
            tables = await cursor.fetchall()
            print(f"📋 Tables: {[t[0] for t in tables]}")

    print("-" * 40)


if __name__ == "__main__":
    asyncio.run(debug_database())
