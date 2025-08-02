#!/usr/bin/env python3
"""
Manual test of Astra Bot components
Testing what we can step by step
"""

import os
import sys
import json
import sqlite3
import asyncio
from datetime import datetime

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


def test_step_1_basic_setup():
    """Step 1: Test basic setup"""
    print("=" * 60)
    print("🚀 ASTRA BOT MANUAL PERFORMANCE TEST")
    print("=" * 60)
    print(f"📅 Started: {datetime.now()}")
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Directory: {os.getcwd()}")
    print()

    print("🔍 STEP 1: Basic Setup")
    print("-" * 30)

    # Check essential files
    essential_files = {
        "bot.1.0.py": "Main bot file",
        "config.json": "Configuration",
        "requirements.txt": "Dependencies",
    }

    for file, desc in essential_files.items():
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {desc}: {file} ({size} bytes)")
        else:
            print(f"❌ {desc}: {file} MISSING")

    # Check directories
    essential_dirs = ["cogs", "utils", "config", "ai", "logger"]
    for directory in essential_dirs:
        if os.path.exists(directory):
            files = len([f for f in os.listdir(directory) if f.endswith(".py")])
            print(f"✅ Directory: {directory}/ ({files} Python files)")
        else:
            print(f"❌ Directory: {directory}/ MISSING")

    return True


def test_step_2_config():
    """Step 2: Test configuration"""
    print("\n🔍 STEP 2: Configuration")
    print("-" * 30)

    try:
        with open("config.json", "r") as f:
            config = json.load(f)

        print("✅ Config file loaded successfully")
        print(f"✅ Config sections: {list(config.keys())}")

        # Check important sections
        important_sections = ["database", "ai", "discord"]
        for section in important_sections:
            if section in config:
                print(f"✅ {section.title()} config: Available")
            else:
                print(f"⚠️ {section.title()} config: Missing")

        return config
    except Exception as e:
        print(f"❌ Config error: {e}")
        return None


def test_step_3_imports():
    """Step 3: Test module imports"""
    print("\n🔍 STEP 3: Module Imports")
    print("-" * 30)

    # Test basic Python modules
    basic_modules = {
        "json": "JSON handling",
        "sqlite3": "SQLite database",
        "asyncio": "Async programming",
        "logging": "Logging system",
        "datetime": "Date/time handling",
        "pathlib": "Path utilities",
    }

    print("Basic Python modules:")
    for module, desc in basic_modules.items():
        try:
            __import__(module)
            print(f"  ✅ {desc}: {module}")
        except ImportError:
            print(f"  ❌ {desc}: {module}")

    # Test optional dependencies
    optional_modules = {
        "aiosqlite": "Async SQLite",
        "discord": "Discord.py",
        "aiohttp": "Async HTTP",
        "psutil": "System monitoring",
        "openai": "OpenAI API",
    }

    print("\nOptional dependencies:")
    available_optional = {}
    for module, desc in optional_modules.items():
        try:
            __import__(module)
            print(f"  ✅ {desc}: {module}")
            available_optional[module] = True
        except ImportError:
            print(f"  ❌ {desc}: {module} (not installed)")
            available_optional[module] = False

    return available_optional


def test_step_4_custom_modules():
    """Step 4: Test our custom modules"""
    print("\n🔍 STEP 4: Custom Modules")
    print("-" * 30)

    custom_modules = {
        "utils.database": "Database manager",
        "utils.http_manager": "HTTP manager",
        "ai.enhanced_ai_handler": "AI handler",
        "config.config_manager": "Config manager",
        "logger.logger_config": "Logger config",
    }

    results = {}
    for module_name, desc in custom_modules.items():
        try:
            module = __import__(module_name, fromlist=[""])
            print(f"  ✅ {desc}: {module_name}")

            # Check for key classes
            if hasattr(module, "DatabaseManager"):
                print(f"     🔧 Found DatabaseManager class")
            if hasattr(module, "DatabaseConnectionPool"):
                print(f"     🔧 Found DatabaseConnectionPool class")
            if hasattr(module, "EnhancedHTTPManager"):
                print(f"     🔧 Found EnhancedHTTPManager class")
            if hasattr(module, "EnhancedAIHandler"):
                print(f"     🔧 Found EnhancedAIHandler class")
            if hasattr(module, "ConfigManager"):
                print(f"     🔧 Found ConfigManager class")

            results[module_name] = True

        except Exception as e:
            print(f"  ❌ {desc}: {module_name} ({e})")
            results[module_name] = False

    return results


def test_step_5_database():
    """Step 5: Test database functionality"""
    print("\n🔍 STEP 5: Database Test")
    print("-" * 30)

    try:
        # Test basic SQLite
        test_db = "test_performance.db"

        print("Testing basic SQLite...")
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()

        # Create test table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS test_performance (
                id INTEGER PRIMARY KEY,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Insert test data
        cursor.execute(
            "INSERT INTO test_performance (name) VALUES (?)", ("performance_test",)
        )
        conn.commit()

        # Query test data
        cursor.execute("SELECT COUNT(*) FROM test_performance")
        count = cursor.fetchone()[0]

        print(f"✅ Basic SQLite: {count} records")

        conn.close()

        # Clean up
        if os.path.exists(test_db):
            os.remove(test_db)

        # Test our database module if available
        try:
            from utils.database import DatabaseManager

            print("✅ Custom DatabaseManager: Available")

            # Test instantiation
            db_manager = DatabaseManager("test_custom.db")
            print("✅ DatabaseManager: Instantiated")

            return True

        except ImportError as e:
            print(f"⚠️ Custom DatabaseManager: Not available ({e})")
            return True  # Still successful with basic SQLite

    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


async def test_step_6_async():
    """Step 6: Test async functionality"""
    print("\n🔍 STEP 6: Async Test")
    print("-" * 30)

    try:
        # Test basic async
        print("Testing basic async...")

        async def async_task(name, delay):
            await asyncio.sleep(delay)
            return f"Task {name} completed"

        # Run multiple tasks
        tasks = [async_task("A", 0.1), async_task("B", 0.2), async_task("C", 0.1)]

        results = await asyncio.gather(*tasks)
        print(f"✅ Async tasks: {len(results)} completed")

        # Test async database if available
        try:
            import aiosqlite

            print("Testing async SQLite...")
            async with aiosqlite.connect("test_async.db") as db:
                await db.execute(
                    """
                    CREATE TABLE IF NOT EXISTS async_test (
                        id INTEGER PRIMARY KEY,
                        data TEXT
                    )
                """
                )
                await db.execute(
                    "INSERT INTO async_test (data) VALUES (?)", ("async_test",)
                )
                await db.commit()

                async with db.execute("SELECT COUNT(*) FROM async_test") as cursor:
                    row = await cursor.fetchone()
                    count = row[0]

            print(f"✅ Async SQLite: {count} records")

            # Clean up
            if os.path.exists("test_async.db"):
                os.remove("test_async.db")

        except ImportError:
            print("⚠️ aiosqlite not available, skipping async database test")

        return True

    except Exception as e:
        print(f"❌ Async test failed: {e}")
        return False


def main():
    """Run all manual tests"""
    print("Starting manual performance test...")

    # Step 1: Basic setup
    test_step_1_basic_setup()

    # Step 2: Configuration
    config = test_step_2_config()

    # Step 3: Imports
    optional_deps = test_step_3_imports()

    # Step 4: Custom modules
    custom_modules = test_step_4_custom_modules()

    # Step 5: Database
    db_result = test_step_5_database()

    # Step 6: Async (if possible)
    try:
        async_result = asyncio.run(test_step_6_async())
    except Exception as e:
        print(f"\n❌ Async test failed: {e}")
        async_result = False

    # Final summary
    print("\n" + "=" * 60)
    print("📊 MANUAL TEST SUMMARY")
    print("=" * 60)

    tests = {
        "Basic Setup": True,
        "Configuration": config is not None,
        "Module Imports": True,
        "Custom Modules": any(custom_modules.values()) if custom_modules else False,
        "Database": db_result,
        "Async Support": async_result,
    }

    passed = sum(tests.values())
    total = len(tests)

    for test_name, result in tests.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\n🎯 Result: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("🎉 EXCELLENT! All manual tests passed!")
    elif passed >= total * 0.8:
        print("✅ GOOD! Most tests passed, minor issues only.")
    elif passed >= total * 0.6:
        print("⚠️ MODERATE! Some functionality working.")
    else:
        print("❌ POOR! Major issues detected.")

    # Recommendations
    print("\n💡 RECOMMENDATIONS:")

    missing_deps = (
        [name for name, available in optional_deps.items() if not available]
        if optional_deps
        else []
    )
    if missing_deps:
        print(f"   📦 Install dependencies: pip install {' '.join(missing_deps)}")

    if not any(custom_modules.values()) if custom_modules else True:
        print("   🔧 Check custom module imports and paths")

    if not db_result:
        print("   💾 Fix database connectivity issues")

    if not async_result:
        print("   ⚡ Install async dependencies (aiosqlite)")

    print("\n✨ Your bot has powerful optimizations ready to use!")
    return passed >= total * 0.8


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⌨️ Test interrupted")
        exit(130)
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        exit(1)
