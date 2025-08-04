"""
Comprehensive Test Suite for Astra Discord Bot
Tests all components, performance, and functionality
"""

import asyncio
import os
import sys
import time
import traceback
import psutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import bot components
try:
    from config.config_manager import config_manager
    from utils.database import db
    from utils.permissions import PermissionManager, PermissionLevel, setup_permissions
    from utils.bot_invite import generate_bot_invite_url, get_full_permissions
    from logger.enhanced_logger import setup_enhanced_logger
    from utils.http_client import get_session
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class ComprehensiveTestSuite:
    """Complete test suite for Astra bot"""

    def __init__(self):
        self.logger = setup_enhanced_logger("TestSuite", "INFO")
        self.start_time = time.time()
        self.test_results = {}
        self.performance_metrics = {}

    async def run_all_tests(self):
        """Run all comprehensive tests"""
        print("=" * 80)
        print("🧪 ASTRA BOT COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Test categories
        test_categories = [
            ("🔧 Configuration Tests", self.test_configuration),
            ("💾 Database Tests", self.test_database),
            ("🛡️ Permission System Tests", self.test_permissions),
            ("🌐 HTTP Client Tests", self.test_http_client),
            ("🔗 Bot Invitation Tests", self.test_bot_invitation),
            ("📊 Performance Tests", self.test_performance),
            ("🎯 Integration Tests", self.test_integration),
            ("🚀 System Health Tests", self.test_system_health),
        ]

        total_tests = len(test_categories)
        passed_tests = 0

        for i, (category_name, test_func) in enumerate(test_categories, 1):
            print(f"[{i}/{total_tests}] {category_name}")
            print("-" * 60)

            try:
                start_time = time.time()
                result = await test_func()
                end_time = time.time()

                if result:
                    print(f"✅ {category_name} - PASSED ({end_time - start_time:.2f}s)")
                    passed_tests += 1
                else:
                    print(f"❌ {category_name} - FAILED ({end_time - start_time:.2f}s)")

                self.test_results[category_name] = {
                    "passed": result,
                    "duration": end_time - start_time,
                }

            except Exception as e:
                print(f"💥 {category_name} - CRASHED: {e}")
                self.test_results[category_name] = {
                    "passed": False,
                    "duration": 0,
                    "error": str(e),
                }

            print()

        # Generate final report
        await self.generate_final_report(passed_tests, total_tests)

    async def test_configuration(self) -> bool:
        """Test configuration management system"""
        try:
            # Test config loading
            config = config_manager.get_bot_config()
            if not config.name or not config.version:
                print("❌ Bot config missing name or version")
                return False

            print(f"✅ Bot config loaded: {config.name} v{config.version}")

            # Test feature flags
            features = config_manager.get_all_features()
            if not features:
                print("⚠️ No features configured")
            else:
                print(f"✅ Features loaded: {len(features)} features")

            # Test color system
            colors = ["success", "error", "warning", "info"]
            for color in colors:
                color_value = config_manager.get_color(color)
                if not color_value:
                    print(f"❌ Missing color: {color}")
                    return False

            print("✅ Color system working")

            # Test guild settings (mock)
            test_setting = config_manager.get_guild_setting(
                12345, "test_setting", "default"
            )
            if test_setting != "default":
                print("❌ Guild setting default not working")
                return False

            print("✅ Guild settings system working")
            return True

        except Exception as e:
            print(f"❌ Configuration test failed: {e}")
            return False

    async def test_database(self) -> bool:
        """Test database functionality"""
        try:
            # Initialize database
            await db.initialize()
            print("✅ Database initialized")

            # Test basic operations
            test_data = {"test": "value", "timestamp": datetime.now().isoformat()}

            # Test set operation
            await db.set("test_table", "test_key", test_data)
            print("✅ Database SET operation")

            # Test get operation
            retrieved_data = await db.get("test_table", "test_key")
            if retrieved_data != test_data:
                print("❌ Database GET operation failed")
                return False
            print("✅ Database GET operation")

            # Test performance metrics
            start_time = time.time()
            for i in range(100):
                await db.set("performance_test", f"key_{i}", {"value": i})
            set_time = time.time() - start_time

            start_time = time.time()
            for i in range(100):
                await db.get("performance_test", f"key_{i}")
            get_time = time.time() - start_time

            print(
                f"✅ Database performance: SET {100/set_time:.0f} ops/sec, GET {100/get_time:.0f} ops/sec"
            )

            # Cleanup test data
            await db.delete("test_table", "test_key")
            for i in range(100):
                await db.delete("performance_test", f"key_{i}")

            print("✅ Database cleanup completed")
            return True

        except Exception as e:
            print(f"❌ Database test failed: {e}")
            traceback.print_exc()
            return False

    async def test_permissions(self) -> bool:
        """Test permission system"""
        try:
            # Create mock bot object
            class MockBot:
                async def application_info(self):
                    class MockAppInfo:
                        class MockOwner:
                            id = 123456789

                        owner = MockOwner()

                    return MockAppInfo()

            # Create mock user and guild
            class MockUser:
                def __init__(self, user_id, is_admin=False):
                    self.id = user_id
                    self.guild_permissions = MockPermissions(is_admin)
                    self.roles = []

            class MockPermissions:
                def __init__(self, is_admin=False):
                    self.administrator = is_admin
                    self.manage_messages = is_admin
                    self.kick_members = is_admin

            class MockGuild:
                def __init__(self):
                    self.id = 987654321
                    self.owner_id = 111111111

                def get_member(self, user_id):
                    # Return the user as a member for testing
                    return MockUser(user_id, user_id == 222222222)  # Admin user

            # Test permission manager
            mock_bot = MockBot()
            perm_manager = PermissionManager(mock_bot)

            # Test owner check
            owner_user = MockUser(123456789)  # Same as bot owner
            guild = MockGuild()

            is_owner = await perm_manager.check_permission(
                owner_user, PermissionLevel.OWNER, guild
            )
            if not is_owner:
                print("❌ Owner permission check failed")
                return False
            print("✅ Owner permission check")

            # Test admin check
            admin_user = MockUser(222222222, is_admin=True)
            is_admin = await perm_manager.check_permission(
                admin_user, PermissionLevel.ADMINISTRATOR, guild
            )
            if not is_admin:
                print("❌ Admin permission check failed")
                return False
            print("✅ Admin permission check")

            # Test regular user
            regular_user = MockUser(333333333)
            is_regular = await perm_manager.check_permission(
                regular_user, PermissionLevel.EVERYONE, guild
            )
            if not is_regular:
                print("❌ Everyone permission check failed")
                return False
            print("✅ Everyone permission check")

            print("✅ Permission system working correctly")
            return True

        except Exception as e:
            print(f"❌ Permission test failed: {e}")
            traceback.print_exc()
            return False

    async def test_http_client(self) -> bool:
        """Test HTTP client functionality"""
        try:
            # Test session creation
            session = await get_session()
            if not session:
                print("❌ HTTP session creation failed")
                return False
            print("✅ HTTP session created")

            # Test basic HTTP request
            async with session.get("https://httpbin.org/get", timeout=10) as response:
                if response.status != 200:
                    print(f"❌ HTTP request failed: {response.status}")
                    return False
                data = await response.json()
                if not data:
                    print("❌ HTTP response parsing failed")
                    return False

            print("✅ HTTP GET request successful")

            # Test request with parameters
            params = {"test": "value", "timestamp": str(int(time.time()))}
            async with session.get(
                "https://httpbin.org/get", params=params, timeout=10
            ) as response:
                if response.status != 200:
                    print(f"❌ HTTP request with params failed: {response.status}")
                    return False
                data = await response.json()
                if not data.get("args"):
                    print("❌ HTTP parameters not received")
                    return False

            print("✅ HTTP request with parameters successful")

            # Performance test
            start_time = time.time()
            tasks = []
            for i in range(10):
                task = session.get("https://httpbin.org/get", timeout=5)
                tasks.append(task)

            responses = await asyncio.gather(
                *[task.__aenter__() for task in tasks], return_exceptions=True
            )
            for response in responses:
                if hasattr(response, "__aexit__"):
                    await response.__aexit__(None, None, None)

            end_time = time.time()
            requests_per_second = 10 / (end_time - start_time)

            print(f"✅ HTTP performance: {requests_per_second:.1f} requests/second")

            # Close session to prevent warnings
            if not session.closed:
                await session.close()

            return True

        except Exception as e:
            print(f"❌ HTTP client test failed: {e}")
            traceback.print_exc()
            return False

    async def test_bot_invitation(self) -> bool:
        """Test bot invitation URL generation"""
        try:
            # Test URL generation
            client_id = "123456789012345678"
            permissions = get_full_permissions()

            url = generate_bot_invite_url(client_id, permissions)
            if not url or "discord.com" not in url:
                print("❌ Bot invitation URL generation failed")
                return False

            print("✅ Bot invitation URL generated")

            # Verify URL components
            if f"client_id={client_id}" not in url:
                print("❌ Client ID missing from URL")
                return False

            if f"permissions={permissions}" not in url:
                print("❌ Permissions missing from URL")
                return False

            if (
                "scope=bot%20applications.commands" in url
                or "scope=bot applications.commands" in url
            ):
                print("✅ Correct scopes found in URL")
            else:
                print("❌ Correct scopes missing from URL")
                return False

            print("✅ Bot invitation URL components verified")

            # Test different permission levels
            from utils.bot_invite import (
                get_minimal_permissions,
                get_recommended_permissions,
            )

            minimal_url = generate_bot_invite_url(client_id, get_minimal_permissions())
            recommended_url = generate_bot_invite_url(
                client_id, get_recommended_permissions()
            )

            if not minimal_url or not recommended_url:
                print("❌ Permission level URLs failed")
                return False

            print("✅ Different permission level URLs generated")
            return True

        except Exception as e:
            print(f"❌ Bot invitation test failed: {e}")
            return False

    async def test_performance(self) -> bool:
        """Test system performance metrics"""
        try:
            # Memory usage test
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024

            if memory_mb > 500:  # Alert if using more than 500MB
                print(f"⚠️ High memory usage: {memory_mb:.1f} MB")
            else:
                print(f"✅ Memory usage: {memory_mb:.1f} MB")

            # CPU usage test
            cpu_percent = process.cpu_percent(interval=1)
            if cpu_percent > 50:  # Alert if using more than 50% CPU
                print(f"⚠️ High CPU usage: {cpu_percent:.1f}%")
            else:
                print(f"✅ CPU usage: {cpu_percent:.1f}%")

            # Async performance test
            async def dummy_task():
                await asyncio.sleep(0.001)
                return True

            start_time = time.time()
            tasks = [dummy_task() for _ in range(1000)]
            results = await asyncio.gather(*tasks)
            end_time = time.time()

            tasks_per_second = 1000 / (end_time - start_time)
            print(f"✅ Async performance: {tasks_per_second:.0f} tasks/second")

            # Store performance metrics
            self.performance_metrics = {
                "memory_mb": memory_mb,
                "cpu_percent": cpu_percent,
                "async_tasks_per_second": tasks_per_second,
                "timestamp": datetime.now().isoformat(),
            }

            return True

        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            return False

    async def test_integration(self) -> bool:
        """Test component integration"""
        try:
            # Test config + database integration
            config = config_manager.get_bot_config()
            await db.set(
                "integration_test", "config_version", {"version": config.version}
            )
            stored_data = await db.get("integration_test", "config_version")

            if stored_data.get("version") != config.version:
                print("❌ Config + Database integration failed")
                return False
            print("✅ Config + Database integration")

            # Test logging integration
            test_logger = setup_enhanced_logger("IntegrationTest", "INFO")
            test_logger.info("Integration test log message")
            print("✅ Logging integration")

            # Test permission + config integration
            features = config_manager.get_all_features()
            if features and "space_content" in features:
                print("✅ Permission + Config integration")
            else:
                print("⚠️ Limited feature configuration detected")

            # Cleanup
            await db.delete("integration_test", "config_version")

            return True

        except Exception as e:
            print(f"❌ Integration test failed: {e}")
            return False

    async def test_system_health(self) -> bool:
        """Test overall system health"""
        try:
            # Check file system
            required_dirs = ["logs", "data", "config", "cogs", "utils"]
            for directory in required_dirs:
                dir_path = Path(directory)
                if not dir_path.exists():
                    print(f"❌ Missing directory: {directory}")
                    return False
            print("✅ File system structure")

            # Check configuration files
            config_files = ["config/config.json"]
            for config_file in config_files:
                file_path = Path(config_file)
                if file_path.exists():
                    try:
                        with open(file_path, "r") as f:
                            json.load(f)
                        print(f"✅ Valid config file: {config_file}")
                    except json.JSONDecodeError:
                        print(f"❌ Invalid JSON in: {config_file}")
                        return False
                else:
                    print(f"⚠️ Missing config file: {config_file}")

            # Check environment variables
            env_vars = ["DISCORD_TOKEN"]
            for var in env_vars:
                if os.getenv(var):
                    print(f"✅ Environment variable: {var}")
                else:
                    print(f"⚠️ Missing environment variable: {var}")

            # Check Python packages
            required_packages = ["discord", "aiohttp", "psutil"]
            for package in required_packages:
                try:
                    __import__(package)
                    print(f"✅ Package available: {package}")
                except ImportError:
                    print(f"❌ Missing package: {package}")
                    return False

            return True

        except Exception as e:
            print(f"❌ System health test failed: {e}")
            return False

    async def generate_final_report(self, passed: int, total: int):
        """Generate comprehensive test report"""
        print("=" * 80)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 80)

        total_time = time.time() - self.start_time
        success_rate = (passed / total) * 100

        print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️ Total Duration: {total_time:.2f} seconds")
        print(f"🎯 Success Rate: {success_rate:.1f}% ({passed}/{total})")
        print()

        # Detailed results
        print("📋 DETAILED RESULTS:")
        print("-" * 60)
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result["passed"] else "❌ FAILED"
            duration = result["duration"]
            print(f"{status:<12} {test_name:<30} ({duration:.2f}s)")
            if "error" in result:
                print(f"             Error: {result['error']}")
        print()

        # Performance summary
        if self.performance_metrics:
            print("⚡ PERFORMANCE SUMMARY:")
            print("-" * 60)
            metrics = self.performance_metrics
            print(f"Memory Usage:     {metrics.get('memory_mb', 0):.1f} MB")
            print(f"CPU Usage:        {metrics.get('cpu_percent', 0):.1f}%")
            print(
                f"Async Performance: {metrics.get('async_tasks_per_second', 0):.0f} tasks/sec"
            )
            print()

        # Recommendations
        print("💡 RECOMMENDATIONS:")
        print("-" * 60)
        if success_rate >= 90:
            print("🎉 Excellent! System is performing well.")
        elif success_rate >= 75:
            print("👍 Good performance with minor issues to address.")
        elif success_rate >= 50:
            print("⚠️ Several issues detected. Review failed tests.")
        else:
            print("🚨 Critical issues detected. Immediate attention required.")

        if passed < total:
            print(f"🔧 {total - passed} test(s) failed - check logs for details")

        print()

        # Save report to file
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_duration": total_time,
            "success_rate": success_rate,
            "tests_passed": passed,
            "tests_total": total,
            "test_results": self.test_results,
            "performance_metrics": self.performance_metrics,
        }

        report_file = (
            Path("data")
            / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2, default=str)

        print(f"📄 Full report saved to: {report_file}")
        print("=" * 80)


async def main():
    """Run comprehensive test suite"""
    try:
        test_suite = ComprehensiveTestSuite()
        await test_suite.run_all_tests()
        return 0
    except KeyboardInterrupt:
        print("\n🛑 Test suite interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
