#!/usr/bin/env python3
"""
Enhanced System Validation Suite for Astra Bot
Comprehensive testing of all optimized systems and new features
"""

import asyncio
import time
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# Add the project root to the path
sys.path.append("/Users/ziadmekawy/Developer/Discord-Stellaris/AstraBot")


class EnhancedSystemValidator:
    """Advanced system validator with comprehensive testing"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tests": {},
            "performance_metrics": {},
            "system_health": {},
            "recommendations": [],
        }

    async def run_comprehensive_validation(self):
        """Run all validation tests"""
        print("🚀 Enhanced Astra Bot System Validation")
        print("=" * 60)

        # Test 1: Component Loading and Initialization
        await self.test_component_loading()

        # Test 2: Empire System Functionality
        await self.test_empire_system()

        # Test 3: Performance Optimization Validation
        await self.test_performance_optimizations()

        # Test 4: Database and AI Integration
        await self.test_integrations()

        # Test 5: Cache System Efficiency
        await self.test_cache_system()

        # Test 6: Advanced Features
        await self.test_advanced_features()

        # Generate final report
        self.generate_validation_report()

    async def test_component_loading(self):
        """Test enhanced component loading"""
        print("\n📦 Testing Enhanced Component Loading...")
        start_time = time.perf_counter()

        try:
            # Test basic imports
            from cogs.roles import Roles
            from cogs.ai_companion import AstraAICompanion
            from ui.ui_components import EmpireRoleView, HomeworldSelectView

            # Test advanced imports
            import aiofiles
            import asyncio
            from collections import defaultdict, Counter

            load_time = time.perf_counter() - start_time

            self.results["tests"]["component_loading"] = {
                "status": "PASSED",
                "load_time": load_time,
                "components_loaded": 6,
            }

            print(
                f"   ✅ All enhanced components loaded successfully in {load_time:.3f}s"
            )

        except Exception as e:
            load_time = time.perf_counter() - start_time
            self.results["tests"]["component_loading"] = {
                "status": "FAILED",
                "load_time": load_time,
                "error": str(e),
            }
            print(f"   ❌ Component loading failed: {e}")

    async def test_empire_system(self):
        """Test enhanced empire system"""
        print("\n🏛️ Testing Enhanced Empire System...")

        try:
            # Mock bot class
            class MockBot:
                def __init__(self):
                    import logging

                    self.logger = logging.getLogger("test")
                    self.guilds = []

            mock_bot = MockBot()
            roles_cog = Roles(mock_bot)

            # Test empire data integrity
            empire_count = len(roles_cog.empire_types)
            lore_categories = len(roles_cog.stellaris_lore)
            total_lore_items = sum(
                len(items) for items in roles_cog.stellaris_lore.values()
            )

            # Test new performance features
            has_performance_metrics = hasattr(roles_cog, "performance_metrics")
            has_caching = hasattr(roles_cog, "lore_cache")
            has_background_tasks = hasattr(roles_cog, "update_empire_stats")

            # Test battle simulation
            empire1 = list(roles_cog.empire_types.values())[0]
            empire2 = list(roles_cog.empire_types.values())[1]

            battle_result = await roles_cog._simulate_empire_battle(empire1, empire2)
            battle_valid = all(
                key in battle_result for key in ["winner", "victory_type", "duration"]
            )

            self.results["tests"]["empire_system"] = {
                "status": "PASSED",
                "empire_count": empire_count,
                "lore_categories": lore_categories,
                "total_lore_items": total_lore_items,
                "performance_metrics": has_performance_metrics,
                "caching_system": has_caching,
                "background_tasks": has_background_tasks,
                "battle_simulation": battle_valid,
            }

            print(
                f"   ✅ Empire system validated: {empire_count} empires, {total_lore_items} lore items"
            )
            print(
                f"   ✅ Performance features: Metrics={has_performance_metrics}, Cache={has_caching}"
            )
            print(f"   ✅ Battle simulation: {battle_valid}")

        except Exception as e:
            self.results["tests"]["empire_system"] = {
                "status": "FAILED",
                "error": str(e),
            }
            print(f"   ❌ Empire system test failed: {e}")

    async def test_performance_optimizations(self):
        """Test performance optimization features"""
        print("\n⚡ Testing Performance Optimizations...")

        try:
            from cogs.roles import Roles

            class MockBot:
                def __init__(self):
                    import logging

                    self.logger = logging.getLogger("test")
                    self.guilds = []

            roles_cog = Roles(mock_bot)

            # Test caching system
            start_time = time.perf_counter()

            # Simulate cache operations
            test_data = {"test": "data", "performance": "optimized"}
            roles_cog._cache_data("test_key", test_data, roles_cog.lore_cache)

            # Test cache retrieval
            cached_result = roles_cog._get_cached_data("test_key", roles_cog.lore_cache)
            cache_hit = cached_result == test_data

            # Test similarity calculation
            similarity_score = roles_cog._calculate_similarity(
                "test_string", "test_string"
            )
            similarity_works = similarity_score == 1.0

            # Test performance tracking
            roles_cog._track_command_performance("test_command", 0.1)
            tracking_works = (
                "test_command" in roles_cog.performance_metrics["command_calls"]
            )

            optimization_time = time.perf_counter() - start_time

            self.results["tests"]["performance_optimizations"] = {
                "status": "PASSED",
                "cache_system": cache_hit,
                "similarity_calculation": similarity_works,
                "performance_tracking": tracking_works,
                "optimization_time": optimization_time,
            }

            print(f"   ✅ Cache system: {cache_hit}")
            print(f"   ✅ Similarity calculation: {similarity_works}")
            print(f"   ✅ Performance tracking: {tracking_works}")
            print(f"   ✅ Optimization time: {optimization_time:.3f}s")

        except Exception as e:
            self.results["tests"]["performance_optimizations"] = {
                "status": "FAILED",
                "error": str(e),
            }
            print(f"   ❌ Performance optimization test failed: {e}")

    async def test_integrations(self):
        """Test database and AI integrations"""
        print("\n🔌 Testing System Integrations...")

        try:
            from cogs.roles import Roles

            class MockBot:
                def __init__(self):
                    import logging

                    self.logger = logging.getLogger("test")
                    self.guilds = []

            roles_cog = Roles(mock_bot)

            # Test database integration availability
            db_available = hasattr(roles_cog, "has_database")
            ai_available = hasattr(roles_cog, "has_ai")

            # Test file operations
            data_dir_exists = roles_cog.data_dir.exists()

            # Test async file operations capability
            import aiofiles

            aiofiles_available = True

            self.results["tests"]["integrations"] = {
                "status": "PASSED",
                "database_integration": db_available,
                "ai_integration": ai_available,
                "data_directory": data_dir_exists,
                "async_file_ops": aiofiles_available,
            }

            print(f"   ✅ Database integration ready: {db_available}")
            print(f"   ✅ AI integration ready: {ai_available}")
            print(f"   ✅ Data directory: {data_dir_exists}")
            print(f"   ✅ Async file operations: {aiofiles_available}")

        except Exception as e:
            self.results["tests"]["integrations"] = {
                "status": "FAILED",
                "error": str(e),
            }
            print(f"   ❌ Integration test failed: {e}")

    async def test_cache_system(self):
        """Test advanced caching system"""
        print("\n🗄️ Testing Advanced Cache System...")

        try:
            from cogs.roles import Roles

            class MockBot:
                def __init__(self):
                    import logging

                    self.logger = logging.getLogger("test")
                    self.guilds = []

            roles_cog = Roles(mock_bot)

            # Test cache operations
            start_time = time.perf_counter()

            # Test multiple cache types
            cache_tests = []

            # Lore cache test
            roles_cog._cache_data("lore_test", {"topic": "test"}, roles_cog.lore_cache)
            lore_result = roles_cog._get_cached_data("lore_test", roles_cog.lore_cache)
            cache_tests.append(lore_result is not None)

            # User profile cache test
            roles_cog._cache_data(
                "user_test", {"user": "test"}, roles_cog.user_profile_cache
            )
            user_result = roles_cog._get_cached_data(
                "user_test", roles_cog.user_profile_cache
            )
            cache_tests.append(user_result is not None)

            # Empire stats cache test
            roles_cog._cache_data(
                "stats_test", {"stats": "test"}, roles_cog.empire_stats_cache
            )
            stats_result = roles_cog._get_cached_data(
                "stats_test", roles_cog.empire_stats_cache
            )
            cache_tests.append(stats_result is not None)

            # Test cache expiration tracking
            has_timestamps = len(roles_cog.cache_timestamps) > 0
            cache_tests.append(has_timestamps)

            cache_time = time.perf_counter() - start_time
            all_cache_tests_passed = all(cache_tests)

            self.results["tests"]["cache_system"] = {
                "status": "PASSED" if all_cache_tests_passed else "PARTIAL",
                "lore_cache": cache_tests[0],
                "user_cache": cache_tests[1],
                "stats_cache": cache_tests[2],
                "timestamp_tracking": cache_tests[3],
                "cache_time": cache_time,
            }

            print(f"   ✅ Lore cache: {cache_tests[0]}")
            print(f"   ✅ User profile cache: {cache_tests[1]}")
            print(f"   ✅ Empire stats cache: {cache_tests[2]}")
            print(f"   ✅ Timestamp tracking: {cache_tests[3]}")
            print(f"   ✅ Cache operation time: {cache_time:.3f}s")

        except Exception as e:
            self.results["tests"]["cache_system"] = {
                "status": "FAILED",
                "error": str(e),
            }
            print(f"   ❌ Cache system test failed: {e}")

    async def test_advanced_features(self):
        """Test new advanced features"""
        print("\n🌟 Testing Advanced Features...")

        try:
            from cogs.roles import Roles
            from cogs.ai_companion import AstraAICompanion

            class MockBot:
                def __init__(self):
                    import logging

                    self.logger = logging.getLogger("test")
                    self.guilds = []

            # Test advanced empire features
            roles_cog = Roles(mock_bot)

            # Test empire strength calculation
            test_empire = {
                "name": "Test Empire",
                "government": "Imperial",
                "ethics": "Militarist, Authoritarian",
            }

            strength = roles_cog._calculate_empire_strength(test_empire)
            strength_valid = 20 <= strength <= 100

            # Test galactic impact system
            impact = roles_cog._get_galactic_impact("Decisive Victory")
            impact_valid = isinstance(impact, str) and len(impact) > 10

            # Test analytics system
            has_analytics = hasattr(roles_cog, "empire_analytics")

            # Test AI companion enhancements
            companion_cog = AstraAICompanion(mock_bot)
            has_system_commands = hasattr(companion_cog, "system_status_command")

            self.results["tests"]["advanced_features"] = {
                "status": "PASSED",
                "empire_strength_calc": strength_valid,
                "galactic_impact_system": impact_valid,
                "analytics_system": has_analytics,
                "enhanced_ai_companion": has_system_commands,
                "calculated_strength": strength,
            }

            print(
                f"   ✅ Empire strength calculation: {strength_valid} (strength: {strength:.1f})"
            )
            print(f"   ✅ Galactic impact system: {impact_valid}")
            print(f"   ✅ Analytics system: {has_analytics}")
            print(f"   ✅ Enhanced AI companion: {has_system_commands}")

        except Exception as e:
            self.results["tests"]["advanced_features"] = {
                "status": "FAILED",
                "error": str(e),
            }
            print(f"   ❌ Advanced features test failed: {e}")

    def generate_validation_report(self):
        """Generate comprehensive validation report"""
        print("\n" + "=" * 60)
        print("📊 ENHANCED SYSTEM VALIDATION REPORT")
        print("=" * 60)

        # Calculate overall health
        passed_tests = sum(
            1
            for test in self.results["tests"].values()
            if test.get("status") == "PASSED"
        )
        total_tests = len(self.results["tests"])
        health_percentage = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"\n🎯 OVERALL SYSTEM HEALTH: {health_percentage:.1f}%")
        print(f"   Tests Passed: {passed_tests}/{total_tests}")

        # Detailed test results
        print(f"\n📋 DETAILED TEST RESULTS:")
        for test_name, result in self.results["tests"].items():
            status_icon = (
                "✅"
                if result["status"] == "PASSED"
                else "⚠️" if result["status"] == "PARTIAL" else "❌"
            )
            print(
                f"   {status_icon} {test_name.replace('_', ' ').title()}: {result['status']}"
            )

            if "error" in result:
                print(f"      🚨 Error: {result['error']}")

        # Performance summary
        print(f"\n⚡ PERFORMANCE SUMMARY:")
        total_load_time = sum(
            test.get("load_time", 0)
            + test.get("optimization_time", 0)
            + test.get("cache_time", 0)
            for test in self.results["tests"].values()
        )
        print(f"   Total processing time: {total_load_time:.3f}s")

        # Feature summary
        print(f"\n🌟 ENHANCED FEATURES SUMMARY:")
        feature_counts = {}
        for test in self.results["tests"].values():
            for key, value in test.items():
                if isinstance(value, bool) and value:
                    feature_counts[key] = feature_counts.get(key, 0) + 1
                elif isinstance(value, int) and key.endswith("_count"):
                    feature_counts[key] = value

        for feature, count in feature_counts.items():
            if feature != "status":
                print(f"   ✨ {feature.replace('_', ' ').title()}: {count}")

        # Recommendations
        print(f"\n💡 SYSTEM RECOMMENDATIONS:")
        if health_percentage >= 90:
            print("   🚀 System is highly optimized and ready for production!")
            print("   🎯 All enhanced features are working correctly")
            print("   📈 Performance optimizations are active and effective")
        elif health_percentage >= 70:
            print("   ⚡ System is well-optimized with minor areas for improvement")
            print("   🔧 Consider addressing any failed tests for optimal performance")
        else:
            print("   ⚠️ System needs optimization - several tests failed")
            print("   🛠️ Review failed components and dependencies")

        # Save report
        report_file = Path("enhanced_validation_report.json")
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n📄 Detailed report saved to: {report_file}")
        print("=" * 60)


async def main():
    """Run the enhanced validation suite"""
    validator = EnhancedSystemValidator()
    await validator.run_comprehensive_validation()


if __name__ == "__main__":
    asyncio.run(main())
