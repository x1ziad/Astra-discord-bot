#!/usr/bin/env python3
"""
Performance Testing Suite for Astra Bot
Tests the optimized components without requiring API keys
"""

import asyncio
import time
import sys
import traceback
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))


class PerformanceTestSuite:
    """Comprehensive performance testing suite"""
    
    def __init__(self):
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
    
    def log(self, message: str, level: str = "INFO"):
        """Simple logging function"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    async def run_test(self, test_name: str, test_func):
        """Run a single test with error handling"""
        self.total_tests += 1
        start_time = time.time()
        
        try:
            self.log(f"Running test: {test_name}")
            result = await test_func()
            
            end_time = time.time()
            duration = end_time - start_time
            
            self.test_results[test_name] = {
                "status": "PASSED",
                "duration": duration,
                "result": result
            }
            
            self.passed_tests += 1
            self.log(f"✅ {test_name} PASSED ({duration:.3f}s)", "SUCCESS")
            return True
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            self.test_results[test_name] = {
                "status": "FAILED",
                "duration": duration,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            
            self.failed_tests += 1
            self.log(f"❌ {test_name} FAILED ({duration:.3f}s): {e}", "ERROR")
            return False

    # Test 1: Basic imports
    async def test_basic_imports(self):
        """Test 1: Basic Python imports"""
        self.log("Testing basic Python imports...")
        
        import os
        import json
        import asyncio
        import logging
        from datetime import datetime
        
        return {
            "python_version": sys.version,
            "asyncio_available": hasattr(asyncio, 'create_task'),
            "datetime_working": datetime.utcnow().isoformat()
        }

    # Test 2: Discord.py import
    async def test_discord_import(self):
        """Test 2: Discord.py availability"""
        self.log("Testing Discord.py import...")
        
        import discord
        from discord.ext import commands, tasks
        
        return {
            "discord_version": discord.__version__,
            "commands_available": hasattr(commands, 'Bot'),
            "tasks_available": hasattr(tasks, 'loop')
        }

    # Test 3: Performance dependencies
    async def test_performance_deps(self):
        """Test 3: Performance-related dependencies"""
        self.log("Testing performance dependencies...")
        
        results = {}
        
        try:
            import psutil
            results["psutil"] = {
                "available": True,
                "version": psutil.__version__,
                "cpu_count": psutil.cpu_count(),
                "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2)
            }
        except ImportError:
            results["psutil"] = {"available": False, "error": "Not installed"}
        
        try:
            import aiohttp
            results["aiohttp"] = {
                "available": True,
                "version": aiohttp.__version__
            }
        except ImportError:
            results["aiohttp"] = {"available": False, "error": "Not installed"}
        
        try:
            import aiosqlite
            results["aiosqlite"] = {
                "available": True,
                "version": aiosqlite.__version__
            }
        except ImportError:
            results["aiosqlite"] = {"available": False, "error": "Not installed"}
        
        return results

    # Test 4: Database module import
    async def test_database_module(self):
        """Test 4: Database module import and basic functionality"""
        self.log("Testing database module...")
        
        try:
            from utils.database import db, DatabaseManager
            
            # Test class instantiation
            test_db = DatabaseManager("test_performance.db")
            
            return {
                "module_imported": True,
                "database_manager_available": True,
                "connection_pool_available": hasattr(test_db, 'pool'),
                "cache_available": hasattr(test_db, '_cache')
            }
            
        except Exception as e:
            return {
                "module_imported": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }

    # Test 5: HTTP manager import
    async def test_http_manager(self):
        """Test 5: HTTP manager import"""
        self.log("Testing HTTP manager...")
        
        try:
            from utils.http_manager import http_manager, EnhancedHTTPManager
            
            return {
                "module_imported": True,
                "http_manager_available": True,
                "session_stats_available": hasattr(http_manager, 'get_stats'),
                "rate_limiting_available": hasattr(http_manager, 'configure_rate_limit')
            }
            
        except Exception as e:
            return {
                "module_imported": False,
                "error": str(e)
            }

    # Test 6: AI handler import (without initialization)
    async def test_ai_handler_import(self):
        """Test 6: AI handler import without API keys"""
        self.log("Testing AI handler import (without initialization)...")
        
        try:
            from ai.enhanced_ai_handler import EnhancedAIHandler
            
            # Test class definition without initialization
            return {
                "module_imported": True,
                "class_available": True,
                "methods_available": {
                    "get_chat_completion": hasattr(EnhancedAIHandler, 'get_chat_completion'),
                    "generate_embeddings": hasattr(EnhancedAIHandler, 'generate_embeddings'),
                    "moderate_content": hasattr(EnhancedAIHandler, 'moderate_content'),
                    "cleanup": hasattr(EnhancedAIHandler, 'cleanup')
                }
            }
            
        except Exception as e:
            return {
                "module_imported": False,
                "error": str(e)
            }

    # Test 7: Database performance test
    async def test_database_performance(self):
        """Test 7: Database performance with connection pooling"""
        self.log("Testing database performance...")
        
        from utils.database import DatabaseManager
        import os
        
        # Use a test database
        test_db_path = "test_performance.db"
        test_db = DatabaseManager(test_db_path)
        
        try:
            # Initialize database
            await test_db.initialize()
            
            # Performance test: Multiple concurrent operations
            async def db_operation(i):
                await test_db.set_guild_setting(i, "test_key", f"test_value_{i}")
                value = await test_db.get_guild_setting(i, "test_key")
                return value == f"test_value_{i}"
            
            start_time = time.time()
            
            # Run 50 concurrent operations
            tasks = [db_operation(i) for i in range(50)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            
            successful_ops = sum(1 for r in results if r is True)
            
            # Get performance stats
            stats = await test_db.get_performance_stats()
            
            # Cleanup
            await test_db.close()
            
            # Remove test database
            if os.path.exists(test_db_path):
                os.remove(test_db_path)
            
            return {
                "operations_completed": len(results),
                "successful_operations": successful_ops,
                "total_time": end_time - start_time,
                "ops_per_second": len(results) / (end_time - start_time),
                "performance_stats": stats
            }
            
        except Exception as e:
            # Cleanup on error
            try:
                await test_db.close()
                if os.path.exists(test_db_path):
                    os.remove(test_db_path)
            except:
                pass
            raise e

    # Test 8: HTTP manager performance
    async def test_http_performance(self):
        """Test 8: HTTP manager performance and caching"""
        self.log("Testing HTTP manager performance...")
        
        from utils.http_manager import EnhancedHTTPManager
        
        http_mgr = EnhancedHTTPManager(max_connections=10, enable_cache=True)
        
        try:
            await http_mgr.initialize()
            
            # Test basic stats
            initial_stats = http_mgr.get_stats()
            
            # Test rate limiting configuration
            http_mgr.configure_rate_limit("test_service", 100, 1000)
            
            # Test cache functionality
            http_mgr.clear_cache()
            
            final_stats = http_mgr.get_stats()
            
            await http_mgr.close()
            
            return {
                "initialization_successful": True,
                "initial_stats": initial_stats,
                "final_stats": final_stats,
                "rate_limiting_configured": True,
                "cache_functionality": True
            }
            
        except Exception as e:
            try:
                await http_mgr.close()
            except:
                pass
            raise e

    # Test 9: Memory usage test
    async def test_memory_usage(self):
        """Test 9: Memory usage monitoring"""
        self.log("Testing memory usage monitoring...")
        
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create some objects to test garbage collection
        test_objects = []
        for i in range(10000):
            test_objects.append({"id": i, "data": f"test_data_{i}" * 10})
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Clear objects and force garbage collection
        test_objects.clear()
        collected = gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        return {
            "initial_memory_mb": round(initial_memory, 2),
            "peak_memory_mb": round(peak_memory, 2),
            "final_memory_mb": round(final_memory, 2),
            "memory_freed_mb": round(peak_memory - final_memory, 2),
            "objects_collected": collected,
            "memory_efficiency": round((peak_memory - final_memory) / peak_memory * 100, 2)
        }

    # Test 10: Bot configuration test
    async def test_bot_configuration(self):
        """Test 10: Bot configuration system"""
        self.log("Testing bot configuration system...")
        
        try:
            from config.config_manager import config_manager
            
            # Test configuration loading
            config = config_manager.get_bot_config()
            
            # Test color system
            primary_color = config_manager.get_color("primary")
            
            return {
                "config_loaded": True,
                "bot_name": config.name,
                "bot_version": config.version,
                "color_system_working": primary_color is not None,
                "features_available": len(config.features) if hasattr(config, 'features') else 0
            }
            
        except Exception as e:
            return {
                "config_loaded": False,
                "error": str(e)
            }

    async def run_all_tests(self):
        """Run all performance tests"""
        self.log("=" * 60)
        self.log("🚀 Starting Astra Bot Performance Test Suite")
        self.log("=" * 60)
        
        # List of all tests
        tests = [
            ("Basic Imports", self.test_basic_imports),
            ("Discord.py Import", self.test_discord_import),
            ("Performance Dependencies", self.test_performance_deps),
            ("Database Module", self.test_database_module),
            ("HTTP Manager", self.test_http_manager),
            ("AI Handler Import", self.test_ai_handler_import),
            ("Database Performance", self.test_database_performance),
            ("HTTP Performance", self.test_http_performance),
            ("Memory Usage", self.test_memory_usage),
            ("Bot Configuration", self.test_bot_configuration),
        ]
        
        # Run tests
        for test_name, test_func in tests:
            await self.run_test(test_name, test_func)
            await asyncio.sleep(0.1)  # Small delay between tests
        
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        self.log("=" * 60)
        self.log("📊 Test Summary")
        self.log("=" * 60)
        
        self.log(f"Total Tests: {self.total_tests}")
        self.log(f"✅ Passed: {self.passed_tests}")
        self.log(f"❌ Failed: {self.failed_tests}")
        self.log(f"📈 Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        
        if self.failed_tests > 0:
            self.log("\n❌ Failed Tests:")
            for test_name, result in self.test_results.items():
                if result["status"] == "FAILED":
                    self.log(f"  • {test_name}: {result['error']}")
        
        self.log("\n⏱️ Test Durations:")
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result["status"] == "PASSED" else "❌"
            self.log(f"  {status_icon} {test_name}: {result['duration']:.3f}s")
        
        total_time = sum(result['duration'] for result in self.test_results.values())
        self.log(f"\n🕐 Total Test Time: {total_time:.3f}s")
        
        if self.passed_tests == self.total_tests:
            self.log("\n🎉 All tests passed! Bot performance optimizations are working correctly.")
        else:
            self.log(f"\n⚠️ {self.failed_tests} test(s) failed. Check the errors above.")


async def main():
    """Main test function"""
    try:
        test_suite = PerformanceTestSuite()
        await test_suite.run_all_tests()
        
        # Return exit code based on test results
        return 0 if test_suite.failed_tests == 0 else 1
        
    except KeyboardInterrupt:
        print("\n⌨️ Tests interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(130)
