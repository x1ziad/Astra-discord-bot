"""
Comprehensive Performance Testing & Command Analysis
Real-time performance monitoring and testing for all bot commands
"""

import asyncio
import logging
import time
import json
import statistics
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import discord
from discord.ext import commands

from utils.performance_optimizer import performance_optimizer
from utils.database import db

logger = logging.getLogger("astra.performance_tester")


@dataclass
class CommandPerformanceReport:
    """Performance report for a command"""

    command_name: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    avg_response_time: float = 0.0
    min_response_time: float = float("inf")
    max_response_time: float = 0.0
    last_called: Optional[datetime] = None
    error_rate: float = 0.0
    cache_hit_rate: float = 0.0
    optimization_score: float = 0.0


@dataclass
class SystemPerformanceReport:
    """Overall system performance report"""

    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    total_commands: int = 0
    commands_per_minute: float = 0.0
    avg_response_time: float = 0.0
    cache_efficiency: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    active_connections: int = 0
    error_rate: float = 0.0
    uptime_hours: float = 0.0


class PerformanceTester:
    """Comprehensive performance testing system"""

    def __init__(self, bot):
        self.bot = bot
        self.command_stats: Dict[str, CommandPerformanceReport] = {}
        self.system_stats: List[SystemPerformanceReport] = []
        self.monitoring_enabled = True
        self.test_results: Dict[str, Any] = {}
        self._start_time = datetime.now(timezone.utc)

        # Performance thresholds
        self.thresholds = {
            "fast_response": 0.5,  # < 0.5s is fast
            "acceptable_response": 2.0,  # < 2.0s is acceptable
            "slow_response": 5.0,  # > 5.0s is slow
            "high_error_rate": 0.1,  # > 10% error rate is concerning
            "low_cache_hit": 0.3,  # < 30% cache hit rate needs improvement
        }

    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive performance test of all bot systems"""
        logger.info("🚀 Starting comprehensive performance test...")

        test_start = time.time()
        results = {
            "test_metadata": {
                "started_at": datetime.now(timezone.utc).isoformat(),
                "bot_uptime_hours": (
                    datetime.now(timezone.utc) - self._start_time
                ).total_seconds()
                / 3600,
                "guild_count": len(self.bot.guilds),
                "user_count": len(self.bot.users) if hasattr(self.bot, "users") else 0,
            }
        }

        try:
            # 1. Test command discovery and analysis
            logger.info("📋 Discovering and analyzing all commands...")
            results["command_analysis"] = await self._analyze_all_commands()

            # 2. Test database performance
            logger.info("💾 Testing database performance...")
            results["database_performance"] = await self._test_database_performance()

            # 3. Test AI system performance
            logger.info("🤖 Testing AI system performance...")
            results["ai_performance"] = await self._test_ai_performance()

            # 4. Test cache effectiveness
            logger.info("🗂️ Testing cache systems...")
            results["cache_performance"] = await self._test_cache_performance()

            # 5. Test system resources
            logger.info("⚡ Testing system resource usage...")
            results["system_resources"] = await self._test_system_resources()

            # 6. Test optimization effectiveness
            logger.info("🔧 Testing optimization effectiveness...")
            results["optimization_effectiveness"] = (
                await self._test_optimization_effectiveness()
            )

            # 7. Generate recommendations
            logger.info("💡 Generating performance recommendations...")
            results["recommendations"] = await self._generate_recommendations(results)

        except Exception as e:
            logger.error(f"Performance test failed: {e}")
            results["error"] = str(e)

        # Calculate test duration
        test_duration = time.time() - test_start
        results["test_metadata"]["duration_seconds"] = test_duration
        results["test_metadata"]["completed_at"] = datetime.now(
            timezone.utc
        ).isoformat()

        # Generate and log comprehensive report
        await self._generate_performance_report(results)

        return results

    async def _analyze_all_commands(self) -> Dict[str, Any]:
        """Analyze all bot commands for performance characteristics"""
        command_analysis = {
            "total_commands": 0,
            "app_commands": 0,
            "text_commands": 0,
            "commands_by_cog": {},
            "optimization_status": {},
            "potential_optimizations": [],
        }

        # Analyze app commands
        for command in self.bot.tree.get_commands():
            command_analysis["total_commands"] += 1
            command_analysis["app_commands"] += 1

            # Check if command is optimized
            is_optimized = hasattr(command.callback, "_optimization_config")
            command_analysis["optimization_status"][command.name] = {
                "optimized": is_optimized,
                "type": "app_command",
                "cog": (
                    command.binding.__class__.__name__ if command.binding else "Global"
                ),
            }

            # Track commands by cog
            cog_name = (
                command.binding.__class__.__name__ if command.binding else "Global"
            )
            if cog_name not in command_analysis["commands_by_cog"]:
                command_analysis["commands_by_cog"][cog_name] = 0
            command_analysis["commands_by_cog"][cog_name] += 1

            # Suggest optimizations for unoptimized commands
            if not is_optimized:
                optimization_suggestion = self._suggest_command_optimization(
                    command.name
                )
                if optimization_suggestion:
                    command_analysis["potential_optimizations"].append(
                        {
                            "command": command.name,
                            "cog": cog_name,
                            "suggestions": optimization_suggestion,
                        }
                    )

        # Analyze text commands
        for command in self.bot.commands:
            command_analysis["total_commands"] += 1
            command_analysis["text_commands"] += 1

            is_optimized = hasattr(command.callback, "_optimization_config")
            command_analysis["optimization_status"][command.name] = {
                "optimized": is_optimized,
                "type": "text_command",
                "cog": command.cog.__class__.__name__ if command.cog else "Global",
            }

        return command_analysis

    def _suggest_command_optimization(self, command_name: str) -> List[str]:
        """Suggest optimizations for a command"""
        suggestions = []

        # AI-related commands should have rate limiting
        if any(
            keyword in command_name.lower()
            for keyword in ["chat", "ai", "analyze", "generate"]
        ):
            suggestions.append(
                "Apply rate limiting (AI commands are resource-intensive)"
            )

        # Info commands should be cacheable
        if any(
            keyword in command_name.lower()
            for keyword in ["info", "status", "help", "about"]
        ):
            suggestions.append("Apply caching (Info commands rarely change)")

        # Admin commands should have strict rate limiting
        if any(
            keyword in command_name.lower()
            for keyword in ["admin", "reload", "shutdown", "config"]
        ):
            suggestions.append(
                "Apply strict rate limiting (Admin commands are sensitive)"
            )

        # Data commands should be cached
        if any(
            keyword in command_name.lower()
            for keyword in ["stats", "leaderboard", "analytics"]
        ):
            suggestions.append(
                "Apply short-term caching (Data aggregation is expensive)"
            )

        return suggestions

    async def _test_database_performance(self) -> Dict[str, Any]:
        """Test database performance under various loads"""
        db_performance = {
            "connection_pool_stats": {},
            "query_performance": {},
            "cache_effectiveness": {},
            "optimization_recommendations": [],
        }

        try:
            # Get connection pool stats
            if hasattr(db, "get_performance_stats"):
                pool_stats = await db.get_performance_stats()
                db_performance["connection_pool_stats"] = pool_stats

            # Test query performance
            start_time = time.time()

            # Test writes
            write_times = []
            for i in range(20):
                write_start = time.time()
                await db.set_guild_setting(
                    999999, f"perf_test_{i}", {"test": True, "timestamp": time.time()}
                )
                write_times.append(time.time() - write_start)

            # Test reads
            read_times = []
            for i in range(20):
                read_start = time.time()
                await db.get_guild_setting(999999, f"perf_test_{i}", {})
                read_times.append(time.time() - read_start)

            db_performance["query_performance"] = {
                "avg_write_time": statistics.mean(write_times),
                "avg_read_time": statistics.mean(read_times),
                "max_write_time": max(write_times),
                "max_read_time": max(read_times),
                "total_test_time": time.time() - start_time,
            }

            # Cleanup test data
            for i in range(20):
                await db.delete("guild_configs", f"999999")

            # Analyze performance
            avg_write = db_performance["query_performance"]["avg_write_time"]
            avg_read = db_performance["query_performance"]["avg_read_time"]

            if avg_write > 0.1:
                db_performance["optimization_recommendations"].append(
                    "Write operations are slow - consider batch writes"
                )

            if avg_read > 0.05:
                db_performance["optimization_recommendations"].append(
                    "Read operations are slow - increase cache TTL or pool size"
                )

        except Exception as e:
            logger.error(f"Database performance test error: {e}")
            db_performance["error"] = str(e)

        return db_performance

    async def _test_ai_performance(self) -> Dict[str, Any]:
        """Test AI system performance"""
        ai_performance = {
            "ai_engine_available": False,
            "response_times": [],
            "cache_effectiveness": {},
            "optimization_applied": False,
            "recommendations": [],
        }

        try:
            # Test AI engine availability
            from ai.consolidated_ai_engine import get_engine

            ai_engine = get_engine()

            if ai_engine:
                ai_performance["ai_engine_available"] = True

                # Test AI response times
                test_prompts = [
                    "Hello, how are you?",
                    "What's the weather like?",
                    "Tell me a short story.",
                    "Explain quantum computing briefly.",
                    "What's your favorite color?",
                ]

                for prompt in test_prompts:
                    try:
                        start_time = time.time()

                        # Test with optimization
                        optimized_prompt, metadata = (
                            await performance_optimizer.ai_optimizer.optimize_ai_request(
                                prompt, 999999, 999999
                            )
                        )

                        response_time = time.time() - start_time
                        ai_performance["response_times"].append(response_time)

                        if metadata.get("optimization_applied"):
                            ai_performance["optimization_applied"] = True

                    except Exception as e:
                        logger.warning(f"AI test prompt failed: {e}")

                # Calculate statistics
                if ai_performance["response_times"]:
                    ai_performance["avg_response_time"] = statistics.mean(
                        ai_performance["response_times"]
                    )
                    ai_performance["max_response_time"] = max(
                        ai_performance["response_times"]
                    )
                    ai_performance["min_response_time"] = min(
                        ai_performance["response_times"]
                    )

                    # Generate recommendations
                    avg_time = ai_performance["avg_response_time"]
                    if avg_time > 3.0:
                        ai_performance["recommendations"].append(
                            "AI responses are slow - consider model optimization or caching"
                        )
                    elif avg_time > 1.5:
                        ai_performance["recommendations"].append(
                            "AI responses could be faster - consider response caching"
                        )

        except ImportError:
            logger.info("AI engine not available for performance testing")
        except Exception as e:
            logger.error(f"AI performance test error: {e}")
            ai_performance["error"] = str(e)

        return ai_performance

    async def _test_cache_performance(self) -> Dict[str, Any]:
        """Test cache system effectiveness"""
        cache_performance = {
            "command_cache": {},
            "ai_cache": {},
            "db_cache": {},
            "overall_efficiency": 0.0,
            "recommendations": [],
        }

        try:
            # Test command cache
            command_cache = performance_optimizer.command_optimizer.command_cache
            cache_performance["command_cache"] = command_cache.get_stats()

            # Test AI cache
            ai_cache = performance_optimizer.ai_optimizer.response_cache
            cache_performance["ai_cache"] = ai_cache.get_stats()

            # Test DB cache
            db_cache = performance_optimizer.db_optimizer.query_cache
            cache_performance["db_cache"] = db_cache.get_stats()

            # Calculate overall efficiency
            total_usage = (
                cache_performance["command_cache"].get("usage_ratio", 0)
                + cache_performance["ai_cache"].get("usage_ratio", 0)
                + cache_performance["db_cache"].get("usage_ratio", 0)
            ) / 3

            cache_performance["overall_efficiency"] = total_usage

            # Generate recommendations
            if total_usage < 0.3:
                cache_performance["recommendations"].append(
                    "Cache usage is low - consider increasing cache TTL or size"
                )
            elif total_usage > 0.9:
                cache_performance["recommendations"].append(
                    "Cache is near capacity - consider increasing cache size"
                )

        except Exception as e:
            logger.error(f"Cache performance test error: {e}")
            cache_performance["error"] = str(e)

        return cache_performance

    async def _test_system_resources(self) -> Dict[str, Any]:
        """Test system resource usage"""
        resource_performance = {
            "memory_usage": {},
            "connection_stats": {},
            "performance_score": 0.0,
            "recommendations": [],
        }

        try:
            import psutil

            process = psutil.Process()
            memory_info = process.memory_info()

            resource_performance["memory_usage"] = {
                "rss_mb": memory_info.rss / 1024 / 1024,
                "vms_mb": memory_info.vms / 1024 / 1024,
                "percent": process.memory_percent(),
                "available_mb": psutil.virtual_memory().available / 1024 / 1024,
            }

            resource_performance["cpu_usage"] = {
                "percent": process.cpu_percent(interval=1),
                "threads": process.num_threads(),
            }

            # Calculate performance score
            memory_score = min(
                100, max(0, 100 - resource_performance["memory_usage"]["percent"])
            )
            cpu_score = min(
                100, max(0, 100 - resource_performance["cpu_usage"]["percent"])
            )
            resource_performance["performance_score"] = (memory_score + cpu_score) / 2

            # Generate recommendations
            if resource_performance["memory_usage"]["percent"] > 75:
                resource_performance["recommendations"].append(
                    "High memory usage - consider increasing cache cleanup frequency"
                )

            if resource_performance["cpu_usage"]["percent"] > 80:
                resource_performance["recommendations"].append(
                    "High CPU usage - consider optimizing background tasks"
                )

        except ImportError:
            logger.warning("psutil not available for system resource testing")
        except Exception as e:
            logger.error(f"System resource test error: {e}")
            resource_performance["error"] = str(e)

        return resource_performance

    async def _test_optimization_effectiveness(self) -> Dict[str, Any]:
        """Test how effective the applied optimizations are"""
        optimization_test = {
            "optimized_commands": 0,
            "unoptimized_commands": 0,
            "cache_hit_improvement": 0.0,
            "response_time_improvement": 0.0,
            "recommendations": [],
        }

        try:
            # Count optimized vs unoptimized commands
            for command in self.bot.tree.get_commands():
                if hasattr(command.callback, "_optimization_config"):
                    optimization_test["optimized_commands"] += 1
                else:
                    optimization_test["unoptimized_commands"] += 1

            # Calculate optimization ratio
            total_commands = (
                optimization_test["optimized_commands"]
                + optimization_test["unoptimized_commands"]
            )
            if total_commands > 0:
                optimization_ratio = (
                    optimization_test["optimized_commands"] / total_commands
                )
                optimization_test["optimization_ratio"] = optimization_ratio

                if optimization_ratio < 0.3:
                    optimization_test["recommendations"].append(
                        "Low command optimization ratio - consider optimizing more commands"
                    )
                elif optimization_ratio > 0.8:
                    optimization_test["recommendations"].append(
                        "Excellent command optimization coverage!"
                    )

            # Get performance optimizer stats
            perf_report = performance_optimizer.get_performance_report()
            optimization_test["performance_optimizer_stats"] = perf_report

        except Exception as e:
            logger.error(f"Optimization effectiveness test error: {e}")
            optimization_test["error"] = str(e)

        return optimization_test

    async def _generate_recommendations(
        self, test_results: Dict[str, Any]
    ) -> List[str]:
        """Generate comprehensive performance recommendations"""
        recommendations = []

        try:
            # Database recommendations
            if "database_performance" in test_results:
                db_results = test_results["database_performance"]
                recommendations.extend(
                    db_results.get("optimization_recommendations", [])
                )

            # AI recommendations
            if "ai_performance" in test_results:
                ai_results = test_results["ai_performance"]
                recommendations.extend(ai_results.get("recommendations", []))

            # Cache recommendations
            if "cache_performance" in test_results:
                cache_results = test_results["cache_performance"]
                recommendations.extend(cache_results.get("recommendations", []))

            # System resource recommendations
            if "system_resources" in test_results:
                resource_results = test_results["system_resources"]
                recommendations.extend(resource_results.get("recommendations", []))

            # Optimization recommendations
            if "optimization_effectiveness" in test_results:
                opt_results = test_results["optimization_effectiveness"]
                recommendations.extend(opt_results.get("recommendations", []))

            # Command-specific recommendations
            if "command_analysis" in test_results:
                cmd_results = test_results["command_analysis"]
                unoptimized_count = cmd_results.get("total_commands", 0) - len(
                    [
                        cmd
                        for cmd, status in cmd_results.get(
                            "optimization_status", {}
                        ).items()
                        if status.get("optimized", False)
                    ]
                )

                if unoptimized_count > 0:
                    recommendations.append(
                        f"Consider optimizing {unoptimized_count} unoptimized commands for better performance"
                    )

            # Add general recommendations
            recommendations.extend(
                [
                    "Monitor performance metrics regularly",
                    "Adjust cache TTL based on usage patterns",
                    "Consider implementing response compression for large payloads",
                    "Use database connection pooling for high-load scenarios",
                    "Implement proper error handling to prevent performance degradation",
                ]
            )

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations.append(f"Error generating recommendations: {e}")

        return list(set(recommendations))  # Remove duplicates

    async def _generate_performance_report(self, test_results: Dict[str, Any]):
        """Generate and log comprehensive performance report"""
        logger.info("=" * 80)
        logger.info("📊 ASTRA BOT COMPREHENSIVE PERFORMANCE REPORT")
        logger.info("=" * 80)

        # Test metadata
        metadata = test_results.get("test_metadata", {})
        logger.info(
            f"🚀 Test Duration: {metadata.get('duration_seconds', 0):.2f} seconds"
        )
        logger.info(f"⏱️ Bot Uptime: {metadata.get('bot_uptime_hours', 0):.2f} hours")
        logger.info(f"🏠 Guilds: {metadata.get('guild_count', 0)}")
        logger.info(f"👥 Users: {metadata.get('user_count', 0)}")

        # Command analysis
        if "command_analysis" in test_results:
            cmd_analysis = test_results["command_analysis"]
            logger.info("\n📋 COMMAND ANALYSIS:")
            logger.info(f"   Total Commands: {cmd_analysis.get('total_commands', 0)}")
            logger.info(f"   App Commands: {cmd_analysis.get('app_commands', 0)}")
            logger.info(f"   Text Commands: {cmd_analysis.get('text_commands', 0)}")

            optimized_count = len(
                [
                    cmd
                    for cmd, status in cmd_analysis.get(
                        "optimization_status", {}
                    ).items()
                    if status.get("optimized", False)
                ]
            )
            total_commands = cmd_analysis.get("total_commands", 1)
            optimization_ratio = optimized_count / total_commands * 100
            logger.info(
                f"   Optimization Coverage: {optimization_ratio:.1f}% ({optimized_count}/{total_commands})"
            )

        # Database performance
        if "database_performance" in test_results:
            db_perf = test_results["database_performance"]
            if "query_performance" in db_perf:
                query_perf = db_perf["query_performance"]
                logger.info("\n💾 DATABASE PERFORMANCE:")
                logger.info(
                    f"   Avg Write Time: {query_perf.get('avg_write_time', 0):.4f}s"
                )
                logger.info(
                    f"   Avg Read Time: {query_perf.get('avg_read_time', 0):.4f}s"
                )
                logger.info(
                    f"   Max Write Time: {query_perf.get('max_write_time', 0):.4f}s"
                )

        # AI performance
        if "ai_performance" in test_results:
            ai_perf = test_results["ai_performance"]
            logger.info("\n🤖 AI SYSTEM PERFORMANCE:")
            logger.info(
                f"   AI Engine Available: {ai_perf.get('ai_engine_available', False)}"
            )
            if ai_perf.get("avg_response_time"):
                logger.info(
                    f"   Avg Response Time: {ai_perf['avg_response_time']:.3f}s"
                )
                logger.info(
                    f"   Optimization Applied: {ai_perf.get('optimization_applied', False)}"
                )

        # Cache performance
        if "cache_performance" in test_results:
            cache_perf = test_results["cache_performance"]
            logger.info("\n🗂️ CACHE PERFORMANCE:")
            logger.info(
                f"   Overall Efficiency: {cache_perf.get('overall_efficiency', 0):.1%}"
            )

            for cache_type, stats in cache_perf.items():
                if isinstance(stats, dict) and "usage_ratio" in stats:
                    logger.info(
                        f"   {cache_type.title()}: {stats['usage_ratio']:.1%} usage"
                    )

        # System resources
        if "system_resources" in test_results:
            resource_perf = test_results["system_resources"]
            logger.info("\n⚡ SYSTEM RESOURCES:")
            if "memory_usage" in resource_perf:
                memory = resource_perf["memory_usage"]
                logger.info(
                    f"   Memory Usage: {memory.get('rss_mb', 0):.1f} MB ({memory.get('percent', 0):.1f}%)"
                )
            if "cpu_usage" in resource_perf:
                cpu = resource_perf["cpu_usage"]
                logger.info(f"   CPU Usage: {cpu.get('percent', 0):.1f}%")
            logger.info(
                f"   Performance Score: {resource_perf.get('performance_score', 0):.1f}/100"
            )

        # Recommendations
        if "recommendations" in test_results:
            recommendations = test_results["recommendations"]
            logger.info("\n💡 PERFORMANCE RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations[:10], 1):  # Show top 10
                logger.info(f"   {i}. {rec}")

        # Overall assessment
        logger.info("\n🎯 OVERALL ASSESSMENT:")

        # Calculate overall score
        scores = []

        if "optimization_effectiveness" in test_results:
            opt_ratio = test_results["optimization_effectiveness"].get(
                "optimization_ratio", 0
            )
            scores.append(opt_ratio * 100)

        if "cache_performance" in test_results:
            cache_efficiency = test_results["cache_performance"].get(
                "overall_efficiency", 0
            )
            scores.append(cache_efficiency * 100)

        if "system_resources" in test_results:
            resource_score = test_results["system_resources"].get(
                "performance_score", 0
            )
            scores.append(resource_score)

        if scores:
            overall_score = sum(scores) / len(scores)

            if overall_score >= 85:
                status = "🎉 EXCELLENT"
                message = "Bot is performing exceptionally well!"
            elif overall_score >= 70:
                status = "👍 GOOD"
                message = "Bot performance is solid with room for minor improvements"
            elif overall_score >= 50:
                status = "⚠️ FAIR"
                message = "Bot performance is acceptable but needs optimization"
            else:
                status = "❌ NEEDS IMPROVEMENT"
                message = "Bot performance requires immediate attention"

            logger.info(f"   Status: {status}")
            logger.info(f"   Score: {overall_score:.1f}/100")
            logger.info(f"   Summary: {message}")

        logger.info("=" * 80)

        # Save report to file
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        report_file = f"data/performance_report_{timestamp}.json"

        try:
            with open(report_file, "w") as f:
                json.dump(test_results, f, indent=2, default=str)
            logger.info(f"📄 Detailed report saved to: {report_file}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")


# Global performance tester instance
performance_tester = None


def initialize_performance_tester(bot):
    """Initialize the performance tester with bot instance"""
    global performance_tester
    performance_tester = PerformanceTester(bot)
    return performance_tester
