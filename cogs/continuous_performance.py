"""
Advanced Continuous Performance Monitor
Provides detailed, real-time system performance monitoring with continuous logging
to Discord channel for comprehensive system health tracking.
"""

import asyncio
import psutil
import discord
from discord.ext import commands, tasks
import logging
import json
import traceback
import sys
import gc
import platform
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from collections import deque, defaultdict
import aiohttp

from utils.discord_data_reporter import get_discord_reporter
from utils.database import db

logger = logging.getLogger("astra.continuous_performance")


class ContinuousPerformanceMonitor(commands.Cog, name="ContinuousPerformance"):
    """Advanced continuous performance monitoring system"""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logger
        self.discord_reporter = None
        
        # Performance data collectors
        self.performance_history = deque(maxlen=1440)  # 24 hours of minute-by-minute data
        self.command_performance = defaultdict(list)
        self.network_latency_history = deque(maxlen=60)  # Last 60 network checks
        self.memory_usage_history = deque(maxlen=120)   # Last 2 hours of memory data
        self.cpu_usage_history = deque(maxlen=120)      # Last 2 hours of CPU data
        
        # Performance thresholds for alerts
        self.thresholds = {
            "memory_critical": 90,      # 90% memory usage
            "memory_warning": 75,       # 75% memory usage
            "cpu_critical": 85,         # 85% CPU usage
            "cpu_warning": 70,          # 70% CPU usage
            "response_critical": 5.0,   # 5 second response time
            "response_warning": 2.0,    # 2 second response time
            "network_critical": 500,    # 500ms network latency
            "network_warning": 200,     # 200ms network latency
        }
        
        # System information
        self.system_info = self._collect_system_info()
        
        # Start monitoring tasks
        self.start_monitoring_tasks()

    async def cog_load(self):
        """Initialize Discord reporter when cog loads"""
        await asyncio.sleep(3)  # Wait for bot to be ready
        self.discord_reporter = get_discord_reporter()
        if self.discord_reporter:
            self.logger.info("✅ Continuous Performance Monitor connected to Discord")
            # Send startup notification
            await self._send_startup_notification()
        else:
            self.logger.warning("⚠️ Discord Data Reporter not available")

    def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.stop_monitoring_tasks()

    def start_monitoring_tasks(self):
        """Start all monitoring background tasks"""
        if not self.detailed_system_monitor.is_running():
            self.detailed_system_monitor.start()
        if not self.network_performance_monitor.is_running():
            self.network_performance_monitor.start()
        if not self.memory_performance_monitor.is_running():
            self.memory_performance_monitor.start()
        if not self.command_performance_analyzer.is_running():
            self.command_performance_analyzer.start()
        if not self.comprehensive_health_report.is_running():
            self.comprehensive_health_report.start()

    def stop_monitoring_tasks(self):
        """Stop all monitoring background tasks"""
        self.detailed_system_monitor.cancel()
        self.network_performance_monitor.cancel()
        self.memory_performance_monitor.cancel()
        self.command_performance_analyzer.cancel()
        self.comprehensive_health_report.cancel()

    def _collect_system_info(self) -> Dict[str, Any]:
        """Collect comprehensive system information"""
        try:
            return {
                "platform": platform.platform(),
                "architecture": platform.architecture(),
                "processor": platform.processor(),
                "python_version": sys.version,
                "discord_py_version": discord.__version__,
                "total_memory": psutil.virtual_memory().total,
                "cpu_count": psutil.cpu_count(),
                "boot_time": psutil.boot_time(),
                "process_id": psutil.Process().pid,
            }
        except Exception as e:
            self.logger.error(f"Error collecting system info: {e}")
            return {"error": str(e)}

    async def _send_startup_notification(self):
        """Send startup notification with system information"""
        if not self.discord_reporter:
            return
            
        startup_data = {
            "event": "continuous_monitor_startup",
            "system_info": self.system_info,
            "monitoring_config": {
                "history_retention": "24 hours",
                "memory_samples": "2 hours",
                "cpu_samples": "2 hours", 
                "network_samples": "60 checks",
                "detailed_interval": "30 seconds",
                "network_interval": "60 seconds",
                "memory_interval": "60 seconds",
                "health_report_interval": "5 minutes"
            },
            "thresholds": self.thresholds,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        await self.discord_reporter.send_continuous_performance(startup_data, immediate=True)

    @tasks.loop(seconds=30)  # Detailed monitoring every 30 seconds
    async def detailed_system_monitor(self):
        """Comprehensive system performance monitoring"""
        try:
            if not self.discord_reporter:
                return

            # Get process information
            process = psutil.Process()
            
            # Collect comprehensive metrics
            performance_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "system_metrics": {
                    # CPU Information
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "cpu_count": psutil.cpu_count(),
                    "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                    "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
                    
                    # Memory Information
                    "memory": psutil.virtual_memory()._asdict(),
                    "swap": psutil.swap_memory()._asdict(),
                    
                    # Disk Information
                    "disk_usage": psutil.disk_usage('/')._asdict(),
                    "disk_io": psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else None,
                    
                    # Network Information
                    "network_io": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else None,
                },
                "bot_process_metrics": {
                    # Process-specific metrics
                    "memory_info": process.memory_info()._asdict(),
                    "memory_percent": process.memory_percent(),
                    "cpu_percent": process.cpu_percent(),
                    "num_threads": process.num_threads(),
                    "num_fds": process.num_fds() if hasattr(process, 'num_fds') else None,
                    "connections": len(process.connections()),
                    "open_files": len(process.open_files()),
                    "create_time": process.create_time(),
                    "status": process.status(),
                },
                "bot_metrics": {
                    # Discord bot metrics
                    "guild_count": len(self.bot.guilds),
                    "user_count": len(self.bot.users),
                    "channel_count": sum(len(guild.channels) for guild in self.bot.guilds),
                    "latency": round(self.bot.latency * 1000, 2),  # Convert to ms
                    "uptime_seconds": (datetime.now(timezone.utc) - self.bot.start_time).total_seconds() if hasattr(self.bot, 'start_time') else 0,
                    "cog_count": len(self.bot.cogs),
                    "command_count": len(self.bot.commands),
                    "extension_count": len(self.bot.extensions),
                },
                "python_metrics": {
                    # Python runtime metrics
                    "garbage_collected": gc.collect(),
                    "memory_objects": len(gc.get_objects()),
                    "reference_cycles": len(gc.garbage),
                    "gc_stats": gc.get_stats(),
                }
            }

            # Store in history
            self.performance_history.append(performance_data)
            
            # Check for performance alerts
            await self._check_performance_alerts(performance_data)
            
            # Send to Discord
            await self.discord_reporter.send_continuous_performance({
                "event": "detailed_system_monitoring",
                "data": performance_data
            }, immediate=False)

        except Exception as e:
            self.logger.error(f"Error in detailed system monitor: {e}")
            await self._send_error_alert("detailed_system_monitor", e)

    @tasks.loop(seconds=60)  # Network monitoring every minute
    async def network_performance_monitor(self):
        """Monitor network performance and response times"""
        try:
            if not self.discord_reporter:
                return

            # Test Discord API response time
            start_time = time.time()
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get('https://discord.com/api/v10/gateway') as response:
                        discord_api_time = (time.time() - start_time) * 1000
                        discord_api_status = response.status
            except Exception as e:
                discord_api_time = None
                discord_api_status = None

            # Test general internet connectivity
            start_time = time.time()
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get('https://httpbin.org/status/200', timeout=10) as response:
                        internet_time = (time.time() - start_time) * 1000
                        internet_status = response.status
            except Exception as e:
                internet_time = None
                internet_status = None

            network_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "discord_api": {
                    "response_time_ms": discord_api_time,
                    "status_code": discord_api_status,
                    "available": discord_api_status == 200 if discord_api_status else False
                },
                "internet": {
                    "response_time_ms": internet_time,
                    "status_code": internet_status,
                    "available": internet_status == 200 if internet_status else False
                },
                "bot_latency_ms": round(self.bot.latency * 1000, 2)
            }

            # Store in history
            self.network_latency_history.append(network_data)
            
            # Send to Discord
            await self.discord_reporter.send_continuous_performance({
                "event": "network_performance_monitoring",
                "data": network_data
            }, immediate=False)

        except Exception as e:
            self.logger.error(f"Error in network performance monitor: {e}")
            await self._send_error_alert("network_performance_monitor", e)

    @tasks.loop(seconds=60)  # Memory monitoring every minute
    async def memory_performance_monitor(self):
        """Monitor detailed memory usage patterns"""
        try:
            if not self.discord_reporter:
                return

            process = psutil.Process()
            memory_info = process.memory_info()
            virtual_memory = psutil.virtual_memory()
            
            memory_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "process_memory": {
                    "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size
                    "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size
                    "percent": process.memory_percent(),
                    "shared_mb": getattr(memory_info, 'shared', 0) / 1024 / 1024,
                    "data_mb": getattr(memory_info, 'data', 0) / 1024 / 1024,
                },
                "system_memory": {
                    "total_mb": virtual_memory.total / 1024 / 1024,
                    "available_mb": virtual_memory.available / 1024 / 1024,
                    "used_mb": virtual_memory.used / 1024 / 1024,
                    "free_mb": virtual_memory.free / 1024 / 1024,
                    "percent": virtual_memory.percent,
                    "cached_mb": getattr(virtual_memory, 'cached', 0) / 1024 / 1024,
                    "buffers_mb": getattr(virtual_memory, 'buffers', 0) / 1024 / 1024,
                },
                "garbage_collection": {
                    "objects_count": len(gc.get_objects()),
                    "collections": gc.get_count(),
                    "thresholds": gc.get_threshold(),
                }
            }

            # Store in history
            self.memory_usage_history.append(memory_data)
            
            # Send to Discord
            await self.discord_reporter.send_continuous_performance({
                "event": "memory_performance_monitoring", 
                "data": memory_data
            }, immediate=False)

        except Exception as e:
            self.logger.error(f"Error in memory performance monitor: {e}")
            await self._send_error_alert("memory_performance_monitor", e)

    @tasks.loop(seconds=180)  # Command analysis every 3 minutes
    async def command_performance_analyzer(self):
        """Analyze command performance and usage patterns"""
        try:
            if not self.discord_reporter:
                return

            # Collect command statistics
            command_stats = {}
            for command in self.bot.commands:
                command_stats[command.name] = {
                    "qualified_name": command.qualified_name,
                    "cog": command.cog.qualified_name if command.cog else None,
                    "enabled": command.enabled,
                    "hidden": command.hidden,
                    "aliases": list(command.aliases) if hasattr(command, 'aliases') else [],
                }

            # Collect cog statistics
            cog_stats = {}
            for cog_name, cog in self.bot.cogs.items():
                cog_stats[cog_name] = {
                    "command_count": len(cog.get_commands()),
                    "listener_count": len(cog.get_listeners()),
                    "qualified_name": cog.qualified_name,
                }

            command_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "command_statistics": {
                    "total_commands": len(self.bot.commands),
                    "total_cogs": len(self.bot.cogs),
                    "total_extensions": len(self.bot.extensions),
                    "commands_by_cog": {
                        cog_name: len(cog.get_commands()) 
                        for cog_name, cog in self.bot.cogs.items()
                    }
                },
                "detailed_command_info": command_stats,
                "detailed_cog_info": cog_stats,
                "extension_info": list(self.bot.extensions.keys())
            }

            # Send to Discord
            await self.discord_reporter.send_continuous_performance({
                "event": "command_performance_analysis",
                "data": command_data
            }, immediate=False)

        except Exception as e:
            self.logger.error(f"Error in command performance analyzer: {e}")
            await self._send_error_alert("command_performance_analyzer", e)

    @tasks.loop(minutes=5)  # Comprehensive health report every 5 minutes
    async def comprehensive_health_report(self):
        """Generate comprehensive system health report"""
        try:
            if not self.discord_reporter:
                return

            # Calculate averages from history
            recent_performance = list(self.performance_history)[-10:]  # Last 10 samples
            recent_network = list(self.network_latency_history)[-5:]   # Last 5 samples
            recent_memory = list(self.memory_usage_history)[-5:]       # Last 5 samples

            # Calculate health scores
            health_scores = await self._calculate_health_scores(
                recent_performance, recent_network, recent_memory
            )

            health_report = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "overall_health": {
                    "score": health_scores["overall"],
                    "status": self._get_health_status(health_scores["overall"]),
                    "uptime_hours": (datetime.now(timezone.utc) - self.bot.start_time).total_seconds() / 3600 if hasattr(self.bot, 'start_time') else 0,
                },
                "component_health": {
                    "cpu": {
                        "score": health_scores["cpu"],
                        "status": self._get_health_status(health_scores["cpu"]),
                        "average_usage": health_scores["cpu_avg"],
                    },
                    "memory": {
                        "score": health_scores["memory"],
                        "status": self._get_health_status(health_scores["memory"]),
                        "average_usage": health_scores["memory_avg"],
                    },
                    "network": {
                        "score": health_scores["network"],
                        "status": self._get_health_status(health_scores["network"]),
                        "average_latency": health_scores["network_avg"],
                    },
                    "discord_connection": {
                        "score": health_scores["discord"],
                        "status": self._get_health_status(health_scores["discord"]),
                        "bot_latency": round(self.bot.latency * 1000, 2),
                    }
                },
                "performance_trends": {
                    "memory_trend": self._calculate_trend([m["system_memory"]["percent"] for m in recent_memory]),
                    "cpu_trend": self._calculate_trend([p["system_metrics"]["cpu_percent"] for p in recent_performance if p.get("system_metrics", {}).get("cpu_percent")]),
                    "network_trend": self._calculate_trend([n["bot_latency_ms"] for n in recent_network if n.get("bot_latency_ms")]),
                },
                "recommendations": await self._generate_performance_recommendations(health_scores)
            }

            # Send comprehensive report
            await self.discord_reporter.send_continuous_performance({
                "event": "comprehensive_health_report",
                "data": health_report
            }, immediate=True)

        except Exception as e:
            self.logger.error(f"Error in comprehensive health report: {e}")
            await self._send_error_alert("comprehensive_health_report", e)

    async def _calculate_health_scores(self, performance_data, network_data, memory_data) -> Dict[str, float]:
        """Calculate health scores for different system components"""
        scores = {
            "cpu": 100.0,
            "memory": 100.0,
            "network": 100.0,
            "discord": 100.0,
            "overall": 100.0,
            "cpu_avg": 0.0,
            "memory_avg": 0.0,
            "network_avg": 0.0,
        }

        try:
            # Calculate CPU health
            if performance_data:
                cpu_values = [p["system_metrics"]["cpu_percent"] for p in performance_data if p.get("system_metrics", {}).get("cpu_percent")]
                if cpu_values:
                    avg_cpu = sum(cpu_values) / len(cpu_values)
                    scores["cpu_avg"] = avg_cpu
                    scores["cpu"] = max(0, 100 - (avg_cpu * 1.2))  # Penalize high CPU usage

            # Calculate Memory health
            if memory_data:
                memory_values = [m["system_memory"]["percent"] for m in memory_data if m.get("system_memory", {}).get("percent")]
                if memory_values:
                    avg_memory = sum(memory_values) / len(memory_values)
                    scores["memory_avg"] = avg_memory
                    scores["memory"] = max(0, 100 - (avg_memory * 1.1))  # Penalize high memory usage

            # Calculate Network health
            if network_data:
                latency_values = [n["bot_latency_ms"] for n in network_data if n.get("bot_latency_ms")]
                if latency_values:
                    avg_latency = sum(latency_values) / len(latency_values)
                    scores["network_avg"] = avg_latency
                    scores["network"] = max(0, 100 - (avg_latency / 10))  # Penalize high latency

            # Calculate Discord connection health
            scores["discord"] = 100 if self.bot.latency < 0.5 else max(0, 100 - (self.bot.latency * 100))

            # Calculate overall health
            scores["overall"] = (scores["cpu"] + scores["memory"] + scores["network"] + scores["discord"]) / 4

        except Exception as e:
            self.logger.error(f"Error calculating health scores: {e}")

        return scores

    def _get_health_status(self, score: float) -> str:
        """Convert health score to status string"""
        if score >= 90:
            return "🟢 Excellent"
        elif score >= 75:
            return "🟡 Good"
        elif score >= 50:
            return "🟠 Fair" 
        elif score >= 25:
            return "🔴 Poor"
        else:
            return "💀 Critical"

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from list of values"""
        if len(values) < 2:
            return "📊 Stable"
        
        # Simple linear trend calculation
        first_half = sum(values[:len(values)//2]) / (len(values)//2)
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        diff_percent = ((second_half - first_half) / first_half) * 100 if first_half > 0 else 0
        
        if diff_percent > 10:
            return "📈 Increasing"
        elif diff_percent < -10:
            return "📉 Decreasing" 
        else:
            return "📊 Stable"

    async def _generate_performance_recommendations(self, health_scores: Dict[str, float]) -> List[str]:
        """Generate performance recommendations based on health scores"""
        recommendations = []

        if health_scores["cpu"] < 70:
            recommendations.append("🔧 High CPU usage detected - consider optimizing background tasks")
        
        if health_scores["memory"] < 70:
            recommendations.append("🧠 High memory usage detected - run garbage collection or restart bot")
            
        if health_scores["network"] < 70:
            recommendations.append("🌐 High network latency detected - check internet connection")
            
        if health_scores["discord"] < 70:
            recommendations.append("🔗 Poor Discord connection - check Discord API status")
            
        if health_scores["overall"] > 90:
            recommendations.append("✨ System running optimally - all systems green!")

        return recommendations

    async def _check_performance_alerts(self, performance_data: Dict[str, Any]):
        """Check performance data against thresholds and send alerts"""
        try:
            alerts = []
            
            # Check memory usage
            memory_percent = performance_data["system_metrics"]["memory"]["percent"]
            if memory_percent > self.thresholds["memory_critical"]:
                alerts.append(f"🚨 CRITICAL: Memory usage at {memory_percent:.1f}%")
            elif memory_percent > self.thresholds["memory_warning"]:
                alerts.append(f"⚠️ WARNING: Memory usage at {memory_percent:.1f}%")

            # Check CPU usage
            cpu_percent = performance_data["system_metrics"]["cpu_percent"] 
            if cpu_percent > self.thresholds["cpu_critical"]:
                alerts.append(f"🚨 CRITICAL: CPU usage at {cpu_percent:.1f}%")
            elif cpu_percent > self.thresholds["cpu_warning"]:
                alerts.append(f"⚠️ WARNING: CPU usage at {cpu_percent:.1f}%")

            # Check bot latency
            bot_latency_ms = performance_data["bot_metrics"]["latency"]
            if bot_latency_ms > self.thresholds["response_critical"] * 1000:
                alerts.append(f"🚨 CRITICAL: Bot latency at {bot_latency_ms:.1f}ms")
            elif bot_latency_ms > self.thresholds["response_warning"] * 1000:
                alerts.append(f"⚠️ WARNING: Bot latency at {bot_latency_ms:.1f}ms")

            # Send alerts if any
            if alerts:
                alert_data = {
                    "event": "performance_alert",
                    "alerts": alerts,
                    "performance_snapshot": performance_data,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                await self.discord_reporter.send_continuous_performance(alert_data, immediate=True)

        except Exception as e:
            self.logger.error(f"Error checking performance alerts: {e}")

    async def _send_error_alert(self, monitor_name: str, error: Exception):
        """Send error alert when monitoring fails"""
        if not self.discord_reporter:
            return
        
        try:
            error_data = {
                "event": "monitor_error_alert",
                "monitor": monitor_name,
                "error": str(error),
                "traceback": traceback.format_exc(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            await self.discord_reporter.send_continuous_performance(error_data, immediate=True)
        except Exception as e:
            self.logger.error(f"Failed to send error alert: {e}")

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        """Track command performance on completion"""
        try:
            if hasattr(ctx, 'command_start_time'):
                execution_time = time.time() - ctx.command_start_time
                
                command_perf_data = {
                    "event": "command_performance_tracking",
                    "command": ctx.command.qualified_name,
                    "execution_time_ms": execution_time * 1000,
                    "guild_id": ctx.guild.id if ctx.guild else None,
                    "channel_type": str(ctx.channel.type),
                    "user_id": ctx.author.id,
                    "success": True,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                
                if self.discord_reporter:
                    await self.discord_reporter.send_continuous_performance(command_perf_data, immediate=False)
                    
        except Exception as e:
            self.logger.error(f"Error tracking command performance: {e}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Track command errors"""
        try:
            if hasattr(ctx, 'command_start_time'):
                execution_time = time.time() - ctx.command_start_time
                
                error_perf_data = {
                    "event": "command_error_tracking",
                    "command": ctx.command.qualified_name if ctx.command else "unknown",
                    "execution_time_ms": execution_time * 1000,
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                    "guild_id": ctx.guild.id if ctx.guild else None,
                    "channel_type": str(ctx.channel.type),
                    "user_id": ctx.author.id,
                    "success": False,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                
                if self.discord_reporter:
                    await self.discord_reporter.send_continuous_performance(error_perf_data, immediate=True)
                    
        except Exception as e:
            self.logger.error(f"Error tracking command error: {e}")

    @commands.Cog.listener()
    async def on_command(self, ctx):
        """Mark command start time for performance tracking"""
        ctx.command_start_time = time.time()


async def setup(bot):
    await bot.add_cog(ContinuousPerformanceMonitor(bot))