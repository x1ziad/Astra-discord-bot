#!/usr/bin/env python3
"""
Comprehensive Performance Analysis for Astra Bot
Analyzes AI performance, system metrics, and bot efficiency
"""

import asyncio
import json
import sqlite3
import time
import psutil
import sys
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import traceback

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import analysis modules
try:
    from ai.consolidated_ai_engine import ConsolidatedAIEngine, get_engine
    from ai.user_profiling import user_profile_manager
    from ai.proactive_engagement import proactive_engagement
    from config.enhanced_config import enhanced_config_manager

    AI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  AI modules import warning: {e}")
    AI_AVAILABLE = False


class PerformanceAnalyzer:
    """Comprehensive performance analysis system"""

    def __init__(self):
        self.start_time = time.time()
        self.results = {
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "system_info": {},
            "ai_performance": {},
            "database_performance": {},
            "memory_analysis": {},
            "response_time_analysis": {},
            "user_engagement_metrics": {},
            "proactive_ai_performance": {},
            "configuration_analysis": {},
            "recommendations": [],
        }

    async def run_full_analysis(self) -> Dict[str, Any]:
        """Run comprehensive performance analysis"""
        print("🔍 Starting Comprehensive Performance Analysis")
        print("=" * 60)

        try:
            # System performance
            print("📊 Analyzing System Performance...")
            await self._analyze_system_performance()

            # Database analysis
            print("🗄️  Analyzing Database Performance...")
            await self._analyze_database_performance()

            # AI performance analysis
            if AI_AVAILABLE:
                print("🤖 Analyzing AI Performance...")
                await self._analyze_ai_performance()

                print("👤 Analyzing User Profiling Performance...")
                await self._analyze_user_profiling()

                print("⚡ Analyzing Proactive Engagement...")
                await self._analyze_proactive_engagement()
            else:
                print("⚠️  Skipping AI analysis - modules not available")

            # Configuration analysis
            print("⚙️  Analyzing Configuration...")
            await self._analyze_configuration()

            # Memory analysis
            print("🧠 Analyzing Memory Usage...")
            await self._analyze_memory_usage()

            # Generate recommendations
            print("💡 Generating Performance Recommendations...")
            await self._generate_recommendations()

            # Calculate total analysis time
            self.results["analysis_duration_seconds"] = time.time() - self.start_time

            print(
                f"✅ Analysis completed in {self.results['analysis_duration_seconds']:.2f}s"
            )

            return self.results

        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            traceback.print_exc()
            self.results["error"] = str(e)
            return self.results

    async def _analyze_system_performance(self):
        """Analyze system performance metrics"""
        try:
            process = psutil.Process()
            system_info = {
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_total_gb": psutil.virtual_memory().total / (1024**3),
                "memory_available_gb": psutil.virtual_memory().available / (1024**3),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage_percent": psutil.disk_usage("/").percent,
                "process_memory_mb": process.memory_info().rss / (1024**2),
                "process_cpu_percent": process.cpu_percent(),
                "open_files": len(process.open_files()),
                "threads": process.num_threads(),
            }

            self.results["system_info"] = system_info

            # Performance scoring
            performance_score = 100
            if system_info["cpu_percent"] > 80:
                performance_score -= 20
            if system_info["memory_percent"] > 80:
                performance_score -= 15
            if system_info["disk_usage_percent"] > 90:
                performance_score -= 10

            self.results["system_performance_score"] = max(0, performance_score)

        except Exception as e:
            print(f"System analysis error: {e}")
            self.results["system_info"] = {"error": str(e)}

    async def _analyze_database_performance(self):
        """Analyze database performance"""
        db_analysis = {
            "databases_found": [],
            "total_size_mb": 0,
            "query_performance": {},
            "table_counts": {},
            "index_analysis": {},
        }

        try:
            data_dir = Path("data")
            if data_dir.exists():
                for db_file in data_dir.glob("*.db"):
                    db_info = await self._analyze_single_database(db_file)
                    db_analysis["databases_found"].append(db_info)
                    db_analysis["total_size_mb"] += db_info.get("size_mb", 0)

            self.results["database_performance"] = db_analysis

        except Exception as e:
            print(f"Database analysis error: {e}")
            self.results["database_performance"] = {"error": str(e)}

    async def _analyze_single_database(self, db_path: Path) -> Dict[str, Any]:
        """Analyze a single SQLite database"""
        try:
            db_info = {
                "name": db_path.name,
                "size_mb": db_path.stat().st_size / (1024**2),
                "tables": {},
                "query_times": {},
            }

            with sqlite3.connect(db_path) as conn:
                # Get table information
                tables = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()

                for (table_name,) in tables:
                    try:
                        # Count records
                        start_time = time.time()
                        count = conn.execute(
                            f"SELECT COUNT(*) FROM {table_name}"
                        ).fetchone()[0]
                        query_time = (time.time() - start_time) * 1000

                        db_info["tables"][table_name] = {
                            "record_count": count,
                            "query_time_ms": query_time,
                        }
                    except Exception as e:
                        db_info["tables"][table_name] = {"error": str(e)}

                # Test query performance
                start_time = time.time()
                conn.execute("SELECT 1").fetchone()
                db_info["simple_query_time_ms"] = (time.time() - start_time) * 1000

            return db_info

        except Exception as e:
            return {"name": db_path.name, "error": str(e)}

    async def _analyze_ai_performance(self):
        """Analyze AI system performance"""
        if not AI_AVAILABLE:
            self.results["ai_performance"] = {"available": False}
            return

        ai_analysis = {
            "available": True,
            "engine_status": "not_initialized",
            "provider_analysis": {},
            "response_time_tests": {},
            "conversation_analysis": {},
        }

        try:
            # Check if engine exists
            engine = get_engine()
            if engine:
                ai_analysis["engine_status"] = "initialized"

                # Get performance metrics
                try:
                    metrics = await engine.get_performance_metrics()
                    ai_analysis["performance_metrics"] = metrics
                except Exception as e:
                    ai_analysis["metrics_error"] = str(e)

                # Test response time
                test_messages = [
                    "Hello, how are you?",
                    "What is the universe?",
                    "Explain quantum physics briefly.",
                ]

                response_times = []
                for i, message in enumerate(test_messages):
                    try:
                        start_time = time.time()
                        response = await engine.process_conversation(
                            message, user_id=999999 + i  # Test user IDs
                        )
                        response_time = (time.time() - start_time) * 1000

                        response_times.append(
                            {
                                "message": message,
                                "response_time_ms": response_time,
                                "response_length": len(response),
                                "response_preview": (
                                    response[:100] + "..."
                                    if len(response) > 100
                                    else response
                                ),
                            }
                        )
                    except Exception as e:
                        response_times.append({"message": message, "error": str(e)})

                ai_analysis["response_time_tests"] = response_times

                # Calculate average performance
                valid_times = [
                    rt["response_time_ms"]
                    for rt in response_times
                    if "response_time_ms" in rt
                ]
                if valid_times:
                    ai_analysis["avg_response_time_ms"] = sum(valid_times) / len(
                        valid_times
                    )
                    ai_analysis["max_response_time_ms"] = max(valid_times)
                    ai_analysis["min_response_time_ms"] = min(valid_times)
            else:
                ai_analysis["engine_status"] = "not_found"

            self.results["ai_performance"] = ai_analysis

        except Exception as e:
            print(f"AI analysis error: {e}")
            ai_analysis["error"] = str(e)
            self.results["ai_performance"] = ai_analysis

    async def _analyze_user_profiling(self):
        """Analyze user profiling system performance"""
        profiling_analysis = {
            "available": True,
            "database_status": "unknown",
            "profile_count": 0,
            "conversation_count": 0,
            "analysis_performance": {},
        }

        try:
            # Check database
            db_path = Path("data/user_profiles.db")
            if db_path.exists():
                profiling_analysis["database_status"] = "exists"
                profiling_analysis["database_size_mb"] = db_path.stat().st_size / (
                    1024**2
                )

                # Count profiles
                with sqlite3.connect(db_path) as conn:
                    try:
                        profile_count = conn.execute(
                            "SELECT COUNT(*) FROM user_profiles"
                        ).fetchone()[0]
                        profiling_analysis["profile_count"] = profile_count
                    except:
                        pass

                    try:
                        conv_count = conn.execute(
                            "SELECT COUNT(*) FROM conversation_history"
                        ).fetchone()[0]
                        profiling_analysis["conversation_count"] = conv_count
                    except:
                        pass
            else:
                profiling_analysis["database_status"] = "not_found"

            # Test profile creation performance
            test_start = time.time()
            test_profile = await user_profile_manager.get_user_profile(
                999999, "TestUser"
            )
            profiling_analysis["profile_creation_time_ms"] = (
                time.time() - test_start
            ) * 1000

            # Test message analysis performance
            test_messages = [
                "I love space exploration!",
                "This is confusing, can you help?",
                "Amazing discovery about black holes!",
            ]

            analysis_times = []
            for message in test_messages:
                start_time = time.time()
                try:
                    analysis = await user_profile_manager.analyze_message(
                        999999, message, "TestUser"
                    )
                    analysis_time = (time.time() - start_time) * 1000
                    analysis_times.append(
                        {
                            "message": message,
                            "analysis_time_ms": analysis_time,
                            "topics_found": len(analysis.get("topics", [])),
                            "sentiment": analysis.get("sentiment", 0),
                        }
                    )
                except Exception as e:
                    analysis_times.append({"message": message, "error": str(e)})

            profiling_analysis["message_analysis_tests"] = analysis_times

            if analysis_times:
                valid_times = [
                    at["analysis_time_ms"]
                    for at in analysis_times
                    if "analysis_time_ms" in at
                ]
                if valid_times:
                    profiling_analysis["avg_analysis_time_ms"] = sum(valid_times) / len(
                        valid_times
                    )

            self.results["user_profiling_performance"] = profiling_analysis

        except Exception as e:
            print(f"User profiling analysis error: {e}")
            profiling_analysis["error"] = str(e)
            self.results["user_profiling_performance"] = profiling_analysis

    async def _analyze_proactive_engagement(self):
        """Analyze proactive engagement system"""
        engagement_analysis = {
            "available": True,
            "engagement_tests": [],
            "performance_metrics": {},
        }

        try:
            test_scenarios = [
                ("I love space exploration and galaxies!", "high_engagement_expected"),
                ("What is the meaning of life?", "question_engagement"),
                ("I'm so confused about this topic", "emotional_support"),
                ("Hello everyone", "low_engagement_expected"),
                ("The weather is nice today", "minimal_engagement"),
            ]

            engagement_times = []
            for message, scenario in test_scenarios:
                start_time = time.time()
                try:
                    should_engage, reason = (
                        await proactive_engagement.should_engage_proactively(
                            message, 999999, 1000, 1, {}
                        )
                    )
                    analysis_time = (time.time() - start_time) * 1000

                    engagement_times.append(
                        {
                            "scenario": scenario,
                            "message": message,
                            "should_engage": should_engage,
                            "reason": reason,
                            "analysis_time_ms": analysis_time,
                        }
                    )
                except Exception as e:
                    engagement_times.append(
                        {"scenario": scenario, "message": message, "error": str(e)}
                    )

            engagement_analysis["engagement_tests"] = engagement_times

            # Calculate performance metrics
            valid_times = [
                et["analysis_time_ms"]
                for et in engagement_times
                if "analysis_time_ms" in et
            ]
            if valid_times:
                engagement_analysis["avg_analysis_time_ms"] = sum(valid_times) / len(
                    valid_times
                )
                engagement_analysis["max_analysis_time_ms"] = max(valid_times)
                engagement_analysis["engagement_accuracy"] = len(
                    [et for et in engagement_times if et.get("should_engage")]
                ) / len(engagement_times)

            self.results["proactive_engagement_performance"] = engagement_analysis

        except Exception as e:
            print(f"Proactive engagement analysis error: {e}")
            engagement_analysis["error"] = str(e)
            self.results["proactive_engagement_performance"] = engagement_analysis

    async def _analyze_configuration(self):
        """Analyze configuration setup"""
        config_analysis = {
            "config_manager_available": True,
            "environment_variables": {},
            "ai_providers_configured": {},
            "database_config": {},
            "performance_config": {},
        }

        try:
            config = enhanced_config_manager

            # Check AI providers
            providers = ["universal", "openrouter", "openai"]
            for provider in providers:
                try:
                    provider_config = config.get_ai_provider_config(provider)
                    config_analysis["ai_providers_configured"][provider] = {
                        "api_key_configured": bool(provider_config.api_key),
                        "model": provider_config.model,
                        "max_tokens": provider_config.max_tokens,
                        "temperature": provider_config.temperature,
                    }
                except Exception as e:
                    config_analysis["ai_providers_configured"][provider] = {
                        "error": str(e)
                    }

            # Database config
            config_analysis["database_config"] = config.get_database_config()

            # Performance config
            config_analysis["performance_config"] = config.get_performance_config()

            # Environment checks
            important_env_vars = [
                "DISCORD_TOKEN",
                "AI_API_KEY",
                "OPENROUTER_API_KEY",
                "OPENAI_API_KEY",
                "FREEPIK_API_KEY",
                "RAILWAY_ENVIRONMENT",
            ]

            for var in important_env_vars:
                config_analysis["environment_variables"][var] = bool(os.getenv(var))

            self.results["configuration_analysis"] = config_analysis

        except Exception as e:
            print(f"Configuration analysis error: {e}")
            config_analysis["error"] = str(e)
            self.results["configuration_analysis"] = config_analysis

    async def _analyze_memory_usage(self):
        """Analyze memory usage patterns"""
        memory_analysis = {
            "current_usage": {},
            "process_details": {},
            "memory_efficiency": {},
        }

        try:
            process = psutil.Process()
            memory_info = process.memory_info()

            memory_analysis["current_usage"] = {
                "rss_mb": memory_info.rss / (1024**2),
                "vms_mb": memory_info.vms / (1024**2),
                "percent": process.memory_percent(),
                "available_system_memory_gb": psutil.virtual_memory().available
                / (1024**3),
            }

            # Detailed memory breakdown
            try:
                memory_analysis["process_details"] = {
                    "open_files": len(process.open_files()),
                    "connections": len(process.connections()),
                    "threads": process.num_threads(),
                    "cpu_times": process.cpu_times()._asdict(),
                }
            except Exception as e:
                memory_analysis["process_details"] = {"error": str(e)}

            # Calculate efficiency score
            efficiency_score = 100
            if memory_analysis["current_usage"]["rss_mb"] > 500:  # >500MB
                efficiency_score -= 20
            if memory_analysis["current_usage"]["percent"] > 10:  # >10% of system
                efficiency_score -= 15

            memory_analysis["memory_efficiency"]["score"] = max(0, efficiency_score)
            memory_analysis["memory_efficiency"]["rating"] = (
                "excellent"
                if efficiency_score > 90
                else (
                    "good"
                    if efficiency_score > 70
                    else "moderate" if efficiency_score > 50 else "poor"
                )
            )

            self.results["memory_analysis"] = memory_analysis

        except Exception as e:
            print(f"Memory analysis error: {e}")
            memory_analysis["error"] = str(e)
            self.results["memory_analysis"] = memory_analysis

    async def _generate_recommendations(self):
        """Generate performance recommendations"""
        recommendations = []

        try:
            # System performance recommendations
            if self.results.get("system_info", {}).get("cpu_percent", 0) > 80:
                recommendations.append(
                    {
                        "category": "system",
                        "priority": "high",
                        "issue": "High CPU usage detected",
                        "recommendation": "Consider optimizing CPU-intensive operations or upgrading hardware",
                        "impact": "Response times may be slower",
                    }
                )

            if self.results.get("system_info", {}).get("memory_percent", 0) > 80:
                recommendations.append(
                    {
                        "category": "system",
                        "priority": "high",
                        "issue": "High memory usage detected",
                        "recommendation": "Optimize memory usage or increase available RAM",
                        "impact": "May cause system instability",
                    }
                )

            # AI performance recommendations
            ai_perf = self.results.get("ai_performance", {})
            if ai_perf.get("avg_response_time_ms", 0) > 5000:  # >5 seconds
                recommendations.append(
                    {
                        "category": "ai",
                        "priority": "medium",
                        "issue": "AI response times are slow",
                        "recommendation": "Consider using faster AI models or implementing response caching",
                        "impact": "Users may experience delays in AI responses",
                    }
                )

            # Database recommendations
            db_perf = self.results.get("database_performance", {})
            if db_perf.get("total_size_mb", 0) > 100:  # >100MB
                recommendations.append(
                    {
                        "category": "database",
                        "priority": "low",
                        "issue": "Database size is growing large",
                        "recommendation": "Implement data cleanup routines for old conversations",
                        "impact": "Query performance may degrade over time",
                    }
                )

            # Configuration recommendations
            config_analysis = self.results.get("configuration_analysis", {})
            providers_configured = config_analysis.get("ai_providers_configured", {})
            configured_count = sum(
                1 for p in providers_configured.values() if p.get("api_key_configured")
            )

            if configured_count < 2:
                recommendations.append(
                    {
                        "category": "configuration",
                        "priority": "medium",
                        "issue": "Limited AI provider redundancy",
                        "recommendation": "Configure multiple AI providers for better reliability",
                        "impact": "Single point of failure for AI functionality",
                    }
                )

            # Memory recommendations
            memory_analysis = self.results.get("memory_analysis", {})
            if memory_analysis.get("memory_efficiency", {}).get("score", 100) < 70:
                recommendations.append(
                    {
                        "category": "memory",
                        "priority": "medium",
                        "issue": "Memory efficiency could be improved",
                        "recommendation": "Implement memory optimization and garbage collection",
                        "impact": "Better system stability and performance",
                    }
                )

            # Performance optimizations
            user_profiling = self.results.get("user_profiling_performance", {})
            if user_profiling.get("avg_analysis_time_ms", 0) > 100:  # >100ms
                recommendations.append(
                    {
                        "category": "performance",
                        "priority": "low",
                        "issue": "User message analysis is slow",
                        "recommendation": "Optimize sentiment analysis algorithms or implement caching",
                        "impact": "Faster personality learning and response personalization",
                    }
                )

            self.results["recommendations"] = recommendations

        except Exception as e:
            print(f"Recommendation generation error: {e}")
            self.results["recommendations"] = [{"error": str(e)}]

    def generate_report(self) -> str:
        """Generate a formatted performance report"""
        report = []
        report.append("🚀 ASTRA BOT PERFORMANCE ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"📅 Analysis Date: {self.results['analysis_timestamp']}")
        report.append(
            f"⏱️  Analysis Duration: {self.results.get('analysis_duration_seconds', 0):.2f}s"
        )
        report.append("")

        # System Performance
        system_info = self.results.get("system_info", {})
        if system_info and "error" not in system_info:
            report.append("🖥️  SYSTEM PERFORMANCE")
            report.append("-" * 30)
            report.append(f"CPU Usage: {system_info.get('cpu_percent', 0):.1f}%")
            report.append(f"Memory Usage: {system_info.get('memory_percent', 0):.1f}%")
            report.append(
                f"Process Memory: {system_info.get('process_memory_mb', 0):.1f} MB"
            )
            report.append(
                f"Performance Score: {self.results.get('system_performance_score', 0)}/100"
            )
            report.append("")

        # AI Performance
        ai_perf = self.results.get("ai_performance", {})
        if ai_perf.get("available"):
            report.append("🤖 AI PERFORMANCE")
            report.append("-" * 30)
            report.append(f"Engine Status: {ai_perf.get('engine_status', 'unknown')}")
            report.append(
                f"Average Response Time: {ai_perf.get('avg_response_time_ms', 0):.1f}ms"
            )
            report.append(
                f"Response Tests: {len(ai_perf.get('response_time_tests', []))}"
            )
            report.append("")

        # Database Performance
        db_perf = self.results.get("database_performance", {})
        if db_perf and "error" not in db_perf:
            report.append("🗄️  DATABASE PERFORMANCE")
            report.append("-" * 30)
            report.append(f"Databases Found: {len(db_perf.get('databases_found', []))}")
            report.append(f"Total Size: {db_perf.get('total_size_mb', 0):.1f} MB")
            for db in db_perf.get("databases_found", []):
                if "error" not in db:
                    table_count = len(db.get("tables", {}))
                    report.append(
                        f"  • {db['name']}: {table_count} tables, {db.get('size_mb', 0):.1f}MB"
                    )
            report.append("")

        # Memory Analysis
        memory_analysis = self.results.get("memory_analysis", {})
        if memory_analysis and "error" not in memory_analysis:
            report.append("🧠 MEMORY ANALYSIS")
            report.append("-" * 30)
            current = memory_analysis.get("current_usage", {})
            report.append(f"Current Usage: {current.get('rss_mb', 0):.1f} MB")
            report.append(
                f"Memory Efficiency: {memory_analysis.get('memory_efficiency', {}).get('rating', 'unknown')}"
            )
            report.append("")

        # Recommendations
        recommendations = self.results.get("recommendations", [])
        if recommendations:
            report.append("💡 RECOMMENDATIONS")
            report.append("-" * 30)
            for rec in recommendations:
                if "error" not in rec:
                    priority_emoji = (
                        "🔴"
                        if rec["priority"] == "high"
                        else "🟡" if rec["priority"] == "medium" else "🟢"
                    )
                    report.append(
                        f"{priority_emoji} [{rec['category'].upper()}] {rec['issue']}"
                    )
                    report.append(f"   → {rec['recommendation']}")
                    report.append("")

        # Summary
        report.append("📊 PERFORMANCE SUMMARY")
        report.append("-" * 30)

        # Calculate overall performance score
        scores = []
        if self.results.get("system_performance_score"):
            scores.append(self.results["system_performance_score"])
        if memory_analysis.get("memory_efficiency", {}).get("score"):
            scores.append(memory_analysis["memory_efficiency"]["score"])

        overall_score = sum(scores) / len(scores) if scores else 0

        report.append(f"Overall Performance Score: {overall_score:.1f}/100")

        if overall_score >= 90:
            report.append("Status: 🟢 Excellent Performance")
        elif overall_score >= 70:
            report.append("Status: 🟡 Good Performance")
        elif overall_score >= 50:
            report.append("Status: 🟠 Moderate Performance")
        else:
            report.append("Status: 🔴 Performance Issues Detected")

        report.append("")
        report.append("Analysis completed! 🎉")

        return "\n".join(report)


async def main():
    """Main analysis function"""
    analyzer = PerformanceAnalyzer()

    try:
        # Run analysis
        results = await analyzer.run_full_analysis()

        # Generate and display report
        report = analyzer.generate_report()
        print("\n" + report)

        # Save detailed results
        results_file = (
            f"data/performance_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        os.makedirs("data", exist_ok=True)

        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n📄 Detailed results saved to: {results_file}")

        # Save report
        report_file = (
            f"data/performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        with open(report_file, "w") as f:
            f.write(report)

        print(f"📄 Report saved to: {report_file}")

        return results

    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        traceback.print_exc()
        return {"error": str(e)}


if __name__ == "__main__":
    asyncio.run(main())
