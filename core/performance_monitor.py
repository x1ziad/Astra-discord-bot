"""
🚀 ULTRA-HIGH-PERFORMANCE MONITORING SYSTEM
Advanced real-time performance tracking and optimization for Astra Bot

Features:
- Real-time metrics collection
- Automated performance optimization
- Memory usage tracking
- Threat detection analytics
- System health monitoring
- Performance bottleneck detection
"""

import asyncio
import time
import json
import logging
import threading
from typing import Dict, List, Any, Optional, Deque
from collections import defaultdict, deque
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from functools import lru_cache

# Optional performance monitoring imports
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


@dataclass
class PerformanceMetrics:
    """📊 Performance metrics data structure"""

    timestamp: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    messages_processed: int
    threats_detected: int
    actions_taken: int
    avg_response_time: float
    cache_hit_rate: float
    error_rate: float
    active_users: int
    system_load: float


class UltraPerformanceMonitor:
    """🚀 Ultra-high-performance monitoring system"""

    def __init__(self, bot=None):
        self.bot = bot
        self.logger = logging.getLogger("astra.performance")

        # 📊 PERFORMANCE DATA STRUCTURES
        self.metrics_history = deque(maxlen=1000)  # 1000 data points
        self.real_time_metrics = {}
        self.performance_alerts = deque(maxlen=100)

        # 🎯 OPTIMIZATION TRACKING
        self.optimization_history = deque(maxlen=50)
        self.bottleneck_detection = {}
        self.auto_optimization_enabled = True

        # 📈 ANALYTICS BUFFERS
        self.cpu_samples = deque(maxlen=60)  # 1 minute of samples
        self.memory_samples = deque(maxlen=60)
        self.response_time_samples = deque(maxlen=100)

        # 🔧 PERFORMANCE THRESHOLDS
        self.thresholds = {
            "cpu_critical": 80.0,  # 80% CPU
            "memory_critical": 512.0,  # 512MB memory
            "response_warning": 0.1,  # 100ms response time
            "response_critical": 0.5,  # 500ms response time
            "error_rate_warning": 0.01,  # 1% error rate
            "error_rate_critical": 0.05,  # 5% error rate
        }

        # 🚀 OPTIMIZATION SETTINGS
        self.optimization_settings = {
            "auto_gc_enabled": True,
            "cache_auto_cleanup": True,
            "memory_auto_optimize": True,
            "performance_auto_tune": True,
            "bottleneck_auto_fix": True,
        }

        # 📊 STATISTICS
        self.stats = {
            "total_optimizations": 0,
            "alerts_generated": 0,
            "bottlenecks_fixed": 0,
            "uptime_start": time.time(),
            "peak_memory": 0.0,
            "peak_cpu": 0.0,
        }

        self._monitoring_active = False
        self._last_optimization = time.time()

    async def start_monitoring(self):
        """🚀 Start ultra-high-performance monitoring"""
        if self._monitoring_active:
            return

        self._monitoring_active = True
        self.logger.info("🚀 Starting ultra-high-performance monitoring system")

        # Start monitoring tasks
        asyncio.create_task(self._real_time_monitor())
        asyncio.create_task(self._performance_analyzer())
        asyncio.create_task(self._auto_optimizer())

        self.logger.info("📊 Performance monitoring system active")

    async def stop_monitoring(self):
        """🛑 Stop performance monitoring"""
        self._monitoring_active = False
        self.logger.info("🛑 Performance monitoring stopped")

    async def _real_time_monitor(self):
        """⚡ Real-time metrics collection (every 5 seconds)"""
        while self._monitoring_active:
            try:
                metrics = await self._collect_system_metrics()

                # Store metrics
                self.metrics_history.append(metrics)
                self.real_time_metrics = asdict(metrics)

                # Update sample buffers
                self.cpu_samples.append(metrics.cpu_percent)
                self.memory_samples.append(metrics.memory_mb)
                self.response_time_samples.append(metrics.avg_response_time)

                # Update peaks
                self.stats["peak_memory"] = max(
                    self.stats["peak_memory"], metrics.memory_mb
                )
                self.stats["peak_cpu"] = max(
                    self.stats["peak_cpu"], metrics.cpu_percent
                )

                # Check for alerts
                await self._check_performance_alerts(metrics)

                await asyncio.sleep(5)  # 5-second intervals

            except Exception as e:
                self.logger.error(f"❌ Real-time monitoring error: {e}")
                await asyncio.sleep(10)  # Longer sleep on error

    async def _collect_system_metrics(self) -> PerformanceMetrics:
        """📊 Collect comprehensive system metrics"""
        current_time = time.time()

        # Default values
        cpu_percent = 0.0
        memory_mb = 0.0
        memory_percent = 0.0
        system_load = 0.0

        # Collect system metrics if available
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                cpu_percent = process.cpu_percent()
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024

                # System-wide metrics
                system_memory = psutil.virtual_memory()
                memory_percent = system_memory.percent
                system_load = (
                    psutil.getloadavg()[0] if hasattr(psutil, "getloadavg") else 0.0
                )

            except Exception as e:
                self.logger.debug(f"Failed to collect system metrics: {e}")

        # Collect bot-specific metrics
        bot_metrics = await self._collect_bot_metrics()

        return PerformanceMetrics(
            timestamp=current_time,
            cpu_percent=cpu_percent,
            memory_mb=memory_mb,
            memory_percent=memory_percent,
            messages_processed=bot_metrics.get("messages_processed", 0),
            threats_detected=bot_metrics.get("threats_detected", 0),
            actions_taken=bot_metrics.get("actions_taken", 0),
            avg_response_time=bot_metrics.get("avg_response_time", 0.0),
            cache_hit_rate=bot_metrics.get("cache_hit_rate", 0.0),
            error_rate=bot_metrics.get("error_rate", 0.0),
            active_users=bot_metrics.get("active_users", 0),
            system_load=system_load,
        )

    async def _collect_bot_metrics(self) -> Dict[str, Any]:
        """🤖 Collect bot-specific performance metrics"""
        metrics = {
            "messages_processed": 0,
            "threats_detected": 0,
            "actions_taken": 0,
            "avg_response_time": 0.0,
            "cache_hit_rate": 0.0,
            "error_rate": 0.0,
            "active_users": 0,
        }

        try:
            if self.bot:
                # Get AI moderation stats
                ai_mod_cog = self.bot.get_cog("AIModeration")
                if ai_mod_cog and hasattr(ai_mod_cog, "performance_stats"):
                    stats = ai_mod_cog.performance_stats
                    metrics["messages_processed"] = stats.get("messages_processed", 0)
                    metrics["threats_detected"] = stats.get("threats_detected", 0)
                    metrics["actions_taken"] = stats.get("actions_taken", 0)
                    metrics["avg_response_time"] = stats.get("avg_processing_time", 0.0)

                    # Calculate cache hit rate
                    cache_hits = stats.get("cache_hits", 0)
                    cache_misses = stats.get("cache_misses", 0)
                    if cache_hits + cache_misses > 0:
                        metrics["cache_hit_rate"] = (
                            cache_hits / (cache_hits + cache_misses) * 100
                        )

                # Get security command stats
                security_cog = self.bot.get_cog("SecurityCommands")
                if security_cog and hasattr(security_cog, "security_stats"):
                    sec_stats = security_cog.security_stats
                    metrics["threats_detected"] += sec_stats.get("threats_logged", 0)
                    metrics["actions_taken"] += sec_stats.get("lockdowns_triggered", 0)

                # Active users (rough estimate from guild members)
                if self.bot.guilds:
                    metrics["active_users"] = sum(
                        len([m for m in guild.members if not m.bot])
                        for guild in self.bot.guilds
                    )

        except Exception as e:
            self.logger.debug(f"Failed to collect bot metrics: {e}")

        return metrics

    async def _check_performance_alerts(self, metrics: PerformanceMetrics):
        """🚨 Check for performance alerts and trigger optimizations"""
        alerts = []

        # CPU usage alerts
        if metrics.cpu_percent > self.thresholds["cpu_critical"]:
            alerts.append(
                {
                    "type": "cpu_critical",
                    "value": metrics.cpu_percent,
                    "threshold": self.thresholds["cpu_critical"],
                    "timestamp": metrics.timestamp,
                }
            )

        # Memory usage alerts
        if metrics.memory_mb > self.thresholds["memory_critical"]:
            alerts.append(
                {
                    "type": "memory_critical",
                    "value": metrics.memory_mb,
                    "threshold": self.thresholds["memory_critical"],
                    "timestamp": metrics.timestamp,
                }
            )

        # Response time alerts
        if metrics.avg_response_time > self.thresholds["response_critical"]:
            alerts.append(
                {
                    "type": "response_critical",
                    "value": metrics.avg_response_time,
                    "threshold": self.thresholds["response_critical"],
                    "timestamp": metrics.timestamp,
                }
            )
        elif metrics.avg_response_time > self.thresholds["response_warning"]:
            alerts.append(
                {
                    "type": "response_warning",
                    "value": metrics.avg_response_time,
                    "threshold": self.thresholds["response_warning"],
                    "timestamp": metrics.timestamp,
                }
            )

        # Error rate alerts
        if metrics.error_rate > self.thresholds["error_rate_critical"]:
            alerts.append(
                {
                    "type": "error_critical",
                    "value": metrics.error_rate,
                    "threshold": self.thresholds["error_rate_critical"],
                    "timestamp": metrics.timestamp,
                }
            )

        # Process alerts
        for alert in alerts:
            self.performance_alerts.append(alert)
            self.stats["alerts_generated"] += 1

            # Log critical alerts
            if "critical" in alert["type"]:
                self.logger.warning(
                    f"🚨 PERFORMANCE ALERT: {alert['type']} = {alert['value']:.2f} "
                    f"(threshold: {alert['threshold']:.2f})"
                )

                # Trigger emergency optimization
                if self.auto_optimization_enabled:
                    asyncio.create_task(self._emergency_optimization(alert))

    async def _emergency_optimization(self, alert: Dict[str, Any]):
        """🆘 Emergency performance optimization"""
        alert_type = alert["type"]

        self.logger.critical(f"🆘 EMERGENCY OPTIMIZATION: {alert_type}")

        try:
            if "memory" in alert_type:
                await self._emergency_memory_cleanup()
            elif "cpu" in alert_type:
                await self._emergency_cpu_optimization()
            elif "response" in alert_type:
                await self._emergency_response_optimization()

            self.stats["total_optimizations"] += 1

        except Exception as e:
            self.logger.error(f"❌ Emergency optimization failed: {e}")

    async def _emergency_memory_cleanup(self):
        """🧹 Emergency memory cleanup"""
        import gc

        # Clear all caches
        if self.bot:
            for cog_name, cog in self.bot.cogs.items():
                if hasattr(cog, "_embed_cache"):
                    cog._embed_cache.clear()
                if hasattr(cog, "_user_cache"):
                    cog._user_cache.clear()
                if hasattr(cog, "_performance_cache"):
                    cog._performance_cache.clear()

        # Force garbage collection multiple times
        for _ in range(3):
            gc.collect()

        self.logger.warning("🧹 Emergency memory cleanup completed")

    async def _emergency_cpu_optimization(self):
        """⚡ Emergency CPU optimization"""
        # Reduce processing intervals
        if self.bot:
            for cog_name, cog in self.bot.cogs.items():
                if hasattr(cog, "settings") and isinstance(cog.settings, dict):
                    # Increase batch sizes to reduce CPU overhead
                    if "batch_size" in cog.settings:
                        cog.settings["batch_size"] = min(
                            50, cog.settings["batch_size"] * 2
                        )

                    # Reduce processing frequency
                    if "gc_frequency" in cog.settings:
                        cog.settings["gc_frequency"] = max(
                            50, cog.settings["gc_frequency"] // 2
                        )

        self.logger.warning("⚡ Emergency CPU optimization completed")

    async def _emergency_response_optimization(self):
        """🚀 Emergency response time optimization"""
        if self.bot:
            for cog_name, cog in self.bot.cogs.items():
                if hasattr(cog, "settings") and isinstance(cog.settings, dict):
                    # Enable aggressive optimization
                    cog.settings["aggressive_optimization"] = True

                    # Reduce cache TTL for faster turnover
                    if "cache_ttl" in cog.settings:
                        cog.settings["cache_ttl"] = max(
                            30, cog.settings["cache_ttl"] // 2
                        )

        self.logger.warning("🚀 Emergency response optimization completed")

    async def _performance_analyzer(self):
        """📈 Advanced performance analysis (every 60 seconds)"""
        while self._monitoring_active:
            try:
                if len(self.metrics_history) >= 5:  # Need at least 5 data points
                    analysis = await self._analyze_performance_trends()
                    await self._detect_bottlenecks(analysis)

                await asyncio.sleep(60)  # 1-minute intervals

            except Exception as e:
                self.logger.error(f"❌ Performance analysis error: {e}")
                await asyncio.sleep(120)  # Longer sleep on error

    async def _analyze_performance_trends(self) -> Dict[str, Any]:
        """📊 Analyze performance trends"""
        recent_metrics = list(self.metrics_history)[-20:]  # Last 20 data points

        if not recent_metrics:
            return {}

        analysis = {
            "cpu_trend": self._calculate_trend([m.cpu_percent for m in recent_metrics]),
            "memory_trend": self._calculate_trend(
                [m.memory_mb for m in recent_metrics]
            ),
            "response_trend": self._calculate_trend(
                [m.avg_response_time for m in recent_metrics]
            ),
            "throughput_trend": self._calculate_trend(
                [m.messages_processed for m in recent_metrics]
            ),
            "error_trend": self._calculate_trend(
                [m.error_rate for m in recent_metrics]
            ),
            "timestamp": time.time(),
        }

        return analysis

    def _calculate_trend(self, values: List[float]) -> str:
        """📈 Calculate trend direction"""
        if len(values) < 2:
            return "stable"

        # Simple trend calculation
        first_half = sum(values[: len(values) // 2]) / (len(values) // 2)
        second_half = sum(values[len(values) // 2 :]) / (len(values) - len(values) // 2)

        if second_half > first_half * 1.1:
            return "increasing"
        elif second_half < first_half * 0.9:
            return "decreasing"
        else:
            return "stable"

    async def _detect_bottlenecks(self, analysis: Dict[str, Any]):
        """🔍 Detect performance bottlenecks"""
        bottlenecks = []

        # Check for concerning trends
        if analysis.get("cpu_trend") == "increasing":
            bottlenecks.append("cpu_increasing")

        if analysis.get("memory_trend") == "increasing":
            bottlenecks.append("memory_leak")

        if analysis.get("response_trend") == "increasing":
            bottlenecks.append("response_degradation")

        if analysis.get("error_trend") == "increasing":
            bottlenecks.append("error_increase")

        # Store bottleneck information
        for bottleneck in bottlenecks:
            self.bottleneck_detection[bottleneck] = {
                "detected_at": time.time(),
                "severity": "medium",  # Could be calculated based on rate of increase
                "analysis": analysis,
            }

        # Log bottlenecks
        if bottlenecks:
            self.logger.warning(f"🔍 Bottlenecks detected: {bottlenecks}")

    async def _auto_optimizer(self):
        """🤖 Automatic performance optimization (every 10 minutes)"""
        while self._monitoring_active:
            try:
                current_time = time.time()

                # Run optimization every 10 minutes
                if current_time - self._last_optimization > 600:
                    await self._run_auto_optimization()
                    self._last_optimization = current_time

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                self.logger.error(f"❌ Auto-optimizer error: {e}")
                await asyncio.sleep(600)  # Longer sleep on error

    async def _run_auto_optimization(self):
        """🚀 Run automatic optimization routines"""
        if not self.auto_optimization_enabled:
            return

        optimizations_run = []

        try:
            # Memory optimization
            if self.optimization_settings["memory_auto_optimize"]:
                await self._auto_memory_optimization()
                optimizations_run.append("memory")

            # Cache optimization
            if self.optimization_settings["cache_auto_cleanup"]:
                await self._auto_cache_optimization()
                optimizations_run.append("cache")

            # Garbage collection
            if self.optimization_settings["auto_gc_enabled"]:
                await self._auto_garbage_collection()
                optimizations_run.append("gc")

            # Performance tuning
            if self.optimization_settings["performance_auto_tune"]:
                await self._auto_performance_tuning()
                optimizations_run.append("tuning")

            self.stats["total_optimizations"] += 1
            self.logger.info(f"🚀 Auto-optimization completed: {optimizations_run}")

        except Exception as e:
            self.logger.error(f"❌ Auto-optimization failed: {e}")

    async def _auto_memory_optimization(self):
        """🧹 Automatic memory optimization"""
        if self.bot:
            for cog_name, cog in self.bot.cogs.items():
                if hasattr(cog, "_cleanup_memory"):
                    try:
                        await cog._cleanup_memory()
                    except Exception as e:
                        self.logger.debug(f"Memory cleanup failed for {cog_name}: {e}")

    async def _auto_cache_optimization(self):
        """📦 Automatic cache optimization"""
        if self.bot:
            for cog_name, cog in self.bot.cogs.items():
                # Clear caches that are too large
                if hasattr(cog, "_embed_cache") and len(cog._embed_cache) > 100:
                    cog._embed_cache.clear()

                if (
                    hasattr(cog, "_performance_cache")
                    and len(cog._performance_cache) > 200
                ):
                    cog._performance_cache.clear()

    async def _auto_garbage_collection(self):
        """🗑️ Automatic garbage collection"""
        import gc

        # Collect garbage
        collected = gc.collect()

        # Log if significant cleanup occurred
        if collected > 100:
            self.logger.debug(f"🗑️ Garbage collection: {collected} objects cleaned")

    async def _auto_performance_tuning(self):
        """🎛️ Automatic performance tuning"""
        # Analyze current performance
        if len(self.response_time_samples) >= 10:
            avg_response = sum(self.response_time_samples) / len(
                self.response_time_samples
            )

            # Tune based on average response time
            if self.bot:
                for cog_name, cog in self.bot.cogs.items():
                    if hasattr(cog, "settings") and isinstance(cog.settings, dict):
                        # Adjust batch sizes based on performance
                        if avg_response > 0.1:  # Slow responses
                            if "batch_size" in cog.settings:
                                cog.settings["batch_size"] = max(
                                    1, cog.settings["batch_size"] - 1
                                )
                        elif avg_response < 0.05:  # Fast responses
                            if "batch_size" in cog.settings:
                                cog.settings["batch_size"] = min(
                                    20, cog.settings["batch_size"] + 1
                                )

    def get_performance_summary(self) -> Dict[str, Any]:
        """📊 Get comprehensive performance summary"""
        current_time = time.time()
        uptime = current_time - self.stats["uptime_start"]

        # Calculate averages from recent samples
        avg_cpu = (
            sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0
        )
        avg_memory = (
            sum(self.memory_samples) / len(self.memory_samples)
            if self.memory_samples
            else 0
        )
        avg_response = (
            sum(self.response_time_samples) / len(self.response_time_samples)
            if self.response_time_samples
            else 0
        )

        return {
            "timestamp": current_time,
            "uptime_hours": uptime / 3600,
            "monitoring_active": self._monitoring_active,
            # Current metrics
            "current_metrics": self.real_time_metrics,
            # Averages
            "avg_cpu_percent": avg_cpu,
            "avg_memory_mb": avg_memory,
            "avg_response_time": avg_response,
            # Peaks
            "peak_cpu_percent": self.stats["peak_cpu"],
            "peak_memory_mb": self.stats["peak_memory"],
            # Statistics
            "total_optimizations": self.stats["total_optimizations"],
            "alerts_generated": self.stats["alerts_generated"],
            "bottlenecks_detected": len(self.bottleneck_detection),
            # Health status
            "health_status": self._calculate_health_status(),
            # Recent alerts
            "recent_alerts": (
                list(self.performance_alerts)[-5:] if self.performance_alerts else []
            ),
            # Data points collected
            "metrics_collected": len(self.metrics_history),
        }

    def _calculate_health_status(self) -> str:
        """🏥 Calculate overall system health status"""
        if not self.real_time_metrics:
            return "unknown"

        # Check critical thresholds
        cpu = self.real_time_metrics.get("cpu_percent", 0)
        memory = self.real_time_metrics.get("memory_mb", 0)
        response_time = self.real_time_metrics.get("avg_response_time", 0)
        error_rate = self.real_time_metrics.get("error_rate", 0)

        if (
            cpu > self.thresholds["cpu_critical"]
            or memory > self.thresholds["memory_critical"]
            or response_time > self.thresholds["response_critical"]
            or error_rate > self.thresholds["error_rate_critical"]
        ):
            return "critical"

        if (
            cpu > self.thresholds["cpu_critical"] * 0.7
            or memory > self.thresholds["memory_critical"] * 0.7
            or response_time > self.thresholds["response_warning"]
            or error_rate > self.thresholds["error_rate_warning"]
        ):
            return "warning"

        return "healthy"

    async def export_metrics(self, filepath: str = None) -> str:
        """📁 Export performance metrics to JSON file"""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"performance_metrics_{timestamp}.json"

        export_data = {
            "export_timestamp": time.time(),
            "performance_summary": self.get_performance_summary(),
            "metrics_history": [asdict(m) for m in self.metrics_history],
            "optimization_history": list(self.optimization_history),
            "bottleneck_detection": self.bottleneck_detection,
            "thresholds": self.thresholds,
            "settings": self.optimization_settings,
        }

        try:
            with open(filepath, "w") as f:
                json.dump(export_data, f, indent=2)

            self.logger.info(f"📁 Performance metrics exported to {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"❌ Failed to export metrics: {e}")
            raise


# Global performance monitor instance
performance_monitor = UltraPerformanceMonitor()


def get_performance_monitor() -> UltraPerformanceMonitor:
    """Get the global performance monitor instance"""
    return performance_monitor
