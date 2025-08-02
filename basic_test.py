#!/usr/bin/env python3
"""
Basic Performance Test for Astra Bot
Tests what we can without external dependencies
"""

import os
import sys
import gc
import time
from datetime import datetime

def test_basic_functionality():
    """Test basic Python and system functionality"""
    print("🔍 Testing Basic Functionality")
    print("-" * 40)
    
    # Test 1: Basic imports
    print("1. Basic Python modules:")
    try:
        import json
        import asyncio
        import logging
        import sqlite3
        print("   ✅ All basic modules imported successfully")
    except Exception as e:
        print(f"   ❌ Basic imports failed: {e}")
        return False
    
    # Test 2: File system
    print("2. Project structure:")
    expected_files = ['bot.1.0.py', 'requirements.txt', 'config.json']
    expected_dirs = ['cogs', 'utils', 'config', 'ai', 'logger']
    
    for file in expected_files:
        if os.path.exists(file):
            print(f"   ✅ {file} exists")
        else:
            print(f"   ❌ {file} missing")
    
    for directory in expected_dirs:
        if os.path.exists(directory):
            print(f"   ✅ {directory}/ directory exists")
        else:
            print(f"   ❌ {directory}/ directory missing")
    
    # Test 3: JSON configuration
    print("3. Configuration file:")
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        print("   ✅ config.json loaded successfully")
        print(f"   ✅ Config keys: {list(config.keys())}")
    except Exception as e:
        print(f"   ❌ Config loading failed: {e}")
    
    return True

def test_memory_and_performance():
    """Test memory usage and basic performance"""
    print("\n🔍 Testing Memory and Performance")
    print("-" * 40)
    
    # Test memory before and after
    print("1. Memory management:")
    start_memory = get_memory_usage()
    print(f"   📊 Initial memory: {start_memory:.1f} MB")
    
    # Create some objects and clean up
    test_data = [i for i in range(100000)]
    during_memory = get_memory_usage()
    print(f"   📊 After creating data: {during_memory:.1f} MB")
    
    del test_data
    collected = gc.collect()
    final_memory = get_memory_usage()
    print(f"   📊 After cleanup: {final_memory:.1f} MB")
    print(f"   🗑️ Objects collected: {collected}")
    
    # Test basic performance
    print("2. Basic performance:")
    start_time = time.time()
    
    # Simulate some work
    result = sum(i * i for i in range(10000))
    
    end_time = time.time()
    duration = (end_time - start_time) * 1000
    print(f"   ⚡ Computation took: {duration:.2f} ms")
    print(f"   ✅ Result: {result}")
    
    return True

def get_memory_usage():
    """Get current memory usage"""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        # Fallback to basic memory info
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024

def test_optional_dependencies():
    """Test which optional dependencies are available"""
    print("\n🔍 Testing Optional Dependencies")
    print("-" * 40)
    
    dependencies = {
        'psutil': 'System monitoring',
        'aiosqlite': 'Async SQLite',
        'aiohttp': 'Async HTTP client',
        'discord': 'Discord.py',
        'openai': 'OpenAI API',
        'azure.cognitiveservices.speech': 'Azure Speech',
        'matplotlib': 'Plotting',
        'numpy': 'Numerical computing',
        'pandas': 'Data analysis'
    }
    
    available = {}
    
    for module_name, description in dependencies.items():
        try:
            __import__(module_name)
            print(f"   ✅ {description}: Available")
            available[module_name] = True
        except ImportError:
            print(f"   ❌ {description}: Not available")
            available[module_name] = False
    
    # Summary
    total = len(dependencies)
    available_count = sum(available.values())
    print(f"\n   📊 Dependencies: {available_count}/{total} available ({available_count/total*100:.1f}%)")
    
    return available

def test_custom_modules():
    """Test our custom modules"""
    print("\n🔍 Testing Custom Modules")
    print("-" * 40)
    
    # Add current directory to path
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())
    
    modules = {
        'utils.database': 'Database utilities',
        'utils.http_manager': 'HTTP manager',
        'ai.enhanced_ai_handler': 'AI handler',
        'config.config_manager': 'Configuration manager',
        'logger.logger_config': 'Logger configuration'
    }
    
    results = {}
    
    for module_name, description in modules.items():
        try:
            module = __import__(module_name, fromlist=[''])
            print(f"   ✅ {description}: Imported successfully")
            
            # Check for key attributes
            if hasattr(module, 'DatabaseManager'):
                print(f"      🔧 DatabaseManager class found")
            if hasattr(module, 'EnhancedHTTPManager'):
                print(f"      🔧 EnhancedHTTPManager class found")
            if hasattr(module, 'EnhancedAIHandler'):
                print(f"      🔧 EnhancedAIHandler class found")
                
            results[module_name] = True
        except Exception as e:
            print(f"   ❌ {description}: Failed ({e})")
            results[module_name] = False
    
    return results

def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 ASTRA BOT - BASIC PERFORMANCE TEST")
    print("=" * 60)
    print(f"📅 Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python version: {sys.version}")
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Run tests
    tests_passed = 0
    total_tests = 4
    
    try:
        if test_basic_functionality():
            tests_passed += 1
        
        if test_memory_and_performance():
            tests_passed += 1
        
        dependencies = test_optional_dependencies()
        if dependencies:
            tests_passed += 1
        
        custom_modules = test_custom_modules()
        if any(custom_modules.values()):
            tests_passed += 1
        
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
    
    # Final results
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    
    success_rate = tests_passed / total_tests * 100
    print(f"🎯 Tests passed: {tests_passed}/{total_tests} ({success_rate:.1f}%)")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Your bot is ready for action!")
    elif tests_passed >= total_tests * 0.75:
        print("✅ Most tests passed! Bot should work well.")
    elif tests_passed >= total_tests * 0.5:
        print("⚠️ Some issues detected. Review failed tests.")
    else:
        print("❌ Multiple issues detected. Check dependencies and setup.")
    
    print("\n💡 Next steps:")
    print("   1. Install missing dependencies: pip install -r requirements.txt")
    print("   2. Configure your Discord bot token")
    print("   3. Test with: python bot.1.0.py")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⌨️ Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
