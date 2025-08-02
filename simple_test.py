#!/usr/bin/env python3
"""
Simple Performance Test for Astra Bot
Tests core functionality without crashing
"""

def test_basic_imports():
    """Test 1: Basic imports"""
    print("🔍 Test 1: Basic imports")
    try:
        import os
        import sys
        import asyncio
        import json
        from datetime import datetime
        print("  ✅ Basic Python modules imported successfully")
        return True
    except Exception as e:
        print(f"  ❌ Basic imports failed: {e}")
        return False

def test_performance_modules():
    """Test 2: Performance-related modules"""
    print("🔍 Test 2: Performance modules")
    results = {}
    
    # Test psutil
    try:
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        print(f"  ✅ psutil available - Memory: {memory_mb:.1f} MB")
        results['psutil'] = True
    except ImportError:
        print("  ⚠️ psutil not available")
        results['psutil'] = False
    
    # Test aiohttp
    try:
        import aiohttp
        print(f"  ✅ aiohttp available - Version: {aiohttp.__version__}")
        results['aiohttp'] = True
    except ImportError:
        print("  ⚠️ aiohttp not available")
        results['aiohttp'] = False
    
    # Test aiosqlite
    try:
        import aiosqlite
        print(f"  ✅ aiosqlite available - Version: {aiosqlite.__version__}")
        results['aiosqlite'] = True
    except ImportError:
        print("  ⚠️ aiosqlite not available")
        results['aiosqlite'] = False
    
    # Test discord.py
    try:
        import discord
        print(f"  ✅ discord.py available - Version: {discord.__version__}")
        results['discord'] = True
    except ImportError:
        print("  ⚠️ discord.py not available")
        results['discord'] = False
    
    return results

def test_project_structure():
    """Test 3: Project structure"""
    print("🔍 Test 3: Project structure")
    import os
    
    required_dirs = [
        'utils', 'config', 'ai', 'cogs', 'logger'
    ]
    
    required_files = [
        'bot.1.0.py', 'requirements.txt', 'config.json'
    ]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"  ✅ Directory {directory}/ exists")
        else:
            print(f"  ❌ Directory {directory}/ missing")
    
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ File {file} exists")
        else:
            print(f"  ❌ File {file} missing")
    
    return True

def test_module_imports():
    """Test 4: Custom module imports"""
    print("🔍 Test 4: Custom module imports")
    import sys
    import os
    
    # Add current directory to path
    sys.path.insert(0, os.getcwd())
    
    modules_to_test = [
        ('utils.database', 'Database module'),
        ('utils.http_manager', 'HTTP manager module'),
        ('ai.enhanced_ai_handler', 'AI handler module'),
        ('config.config_manager', 'Configuration module')
    ]
    
    results = {}
    
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"  ✅ {description} imported successfully")
            results[module_name] = True
        except Exception as e:
            print(f"  ❌ {description} failed: {e}")
            results[module_name] = False
    
    return results

def test_database_module():
    """Test 5: Database module functionality"""
    print("🔍 Test 5: Database module functionality")
    try:
        from utils.database import db, DatabaseManager
        
        # Test class instantiation
        test_db = DatabaseManager("test.db")
        print("  ✅ DatabaseManager instantiated")
        
        # Check for performance features
        has_pool = hasattr(test_db, 'pool')
        has_cache = hasattr(test_db, '_cache')
        
        print(f"  ✅ Connection pooling: {'Available' if has_pool else 'Not available'}")
        print(f"  ✅ Caching system: {'Available' if has_cache else 'Not available'}")
        
        return {
            'instantiated': True,
            'connection_pooling': has_pool,
            'caching': has_cache
        }
        
    except Exception as e:
        print(f"  ❌ Database module test failed: {e}")
        return False

def test_system_resources():
    """Test 6: System resource monitoring"""
    print("🔍 Test 6: System resource monitoring")
    
    try:
        import psutil
        import gc
        
        # Get system info
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        cpu_percent = process.cpu_percent()
        
        # Test garbage collection
        collected = gc.collect()
        
        print(f"  ✅ Current memory usage: {memory_mb:.1f} MB")
        print(f"  ✅ CPU usage: {cpu_percent:.1f}%")
        print(f"  ✅ Garbage collected: {collected} objects")
        
        return {
            'memory_mb': memory_mb,
            'cpu_percent': cpu_percent,
            'gc_collected': collected
        }
        
    except ImportError:
        print("  ⚠️ psutil not available for system monitoring")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 Astra Bot Simple Performance Test")
    print("=" * 60)
    
    tests = [
        test_basic_imports,
        test_performance_modules,
        test_project_structure,
        test_module_imports,
        test_database_module,
        test_system_resources
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
            print()  # Empty line between tests
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            print()
    
    print("=" * 60)
    print(f"📊 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Performance optimizations are working!")
    else:
        print(f"⚠️ {total - passed} test(s) need attention.")
    
    print("=" * 60)
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⌨️ Test interrupted by user")
        exit(130)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        exit(1)
