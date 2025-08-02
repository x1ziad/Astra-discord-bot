#!/usr/bin/env python3
"""
Test script to verify bot initialization without connecting to Discord
"""

import asyncio
import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))


async def test_bot_initialization():
    """Test bot initialization without starting"""
    try:
        # Import the bot module
        import importlib.util

        spec = importlib.util.spec_from_file_location("bot", "bot.1.0.py")
        bot_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bot_module)

        print("✅ Bot module loaded successfully")

        # Test AstraBot class instantiation
        bot = bot_module.AstraBot()
        print("✅ AstraBot instance created successfully")

        # Test database initialization
        from utils.database import db

        await db.initialize()
        print("✅ Database initialization successful")

        # Clean up
        await bot.close()
        print("✅ Bot cleanup successful")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_bot_initialization())
    sys.exit(0 if success else 1)
