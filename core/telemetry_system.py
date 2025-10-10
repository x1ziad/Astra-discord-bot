"""
🚀 COMPREHENSIVE TELEMETRY & MONITORING SYSTEM
Real-time performance monitoring and analytics for maximum system optimization

Features:
- Real-time performance metrics
- Component health monitoring
- Adaptive alerting system
- Performance trend analysis
- Resource utilization tracking
- Custom metrics collection
- Performance bottleneck detection
- Automated optimization suggestions

Author: x1ziad
Version: 2.0.0 PERFORMANCE
"""

import asyncio
import logging
import time
import threading
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, defaultdict
import statistics
import weakref

# Performance imports with fallbacks
try:
    import psutil

    USE_PSUTIL = True
except ImportError:
    USE_PSUTIL = False

try:
    import orjson as fast_json

    USE_FAST_JSON = True
except ImportError:
    import json as fast_json

    USE_FAST_JSON = False

import discord
from discord.ext import commands

logger = logging.getLogger("astra.telemetry")


class MetricType(Enum):
    """Types of metrics collected"""

    COUNTER = "counter"  # Incrementing values
    GAUGE = "gauge"  # Current value snapshots
    HISTOGRAM = "histogram"  # Distribution of values
    TIMER = "timer"  # Execution time measurements
    RATE = "rate"  # Events per time unit


class AlertLevel(Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ComponentHealth(Enum):
    """Component health states"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class MetricPoint:
    """Single metric data point"""

    timestamp: datetime
    value: Union[int, float]
    labels: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "labels": self.labels,
        }


@dataclass
class Alert:
    """System alert"""

    id: str
    level: AlertLevel
    component: str
    message: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "level": self.level.value,
            "component": self.component,
            "message": self.message,
            "created_at": self.created_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "metadata": self.metadata,
        }


@dataclass
class ComponentMetrics:
    """Comprehensive component metrics"""

    name: str
    health: ComponentHealth = ComponentHealth.UNKNOWN
    uptime_seconds: float = 0.0
    requests_total: int = 0
    requests_per_second: float = 0.0
    errors_total: int = 0
    error_rate: float = 0.0
    avg_response_time: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    custom_metrics: Dict[str, float] = field(default_factory=dict)

    def get_health_score(self) -> float:
        """Calculate overall health score (0-100)"""
        score = 100.0

        # Error rate impact
        if self.error_rate > 0:
            score -= min(self.error_rate * 100, 50)  # Max 50 point penalty

        # Response time impact
        if self.avg_response_time > 1.0:  # >1 second
            score -= min(
                (self.avg_response_time - 1.0) * 20, 30
            )  # Max 30 point penalty

        return max(0.0, score)


class PerformanceAnalyzer:
    """Advanced performance analysis and optimization suggestions"""

    def __init__(self):
        self.analysis_history: List[Dict[str, Any]] = []
        self.bottlenecks: List[Dict[str, Any]] = []
        self.optimization_suggestions: List[Dict[str, Any]] = []

    def analyze_performance_trends(
        self, metrics: Dict[str, ComponentMetrics]
    ) -> Dict[str, Any]:
        """Analyze performance trends and identify issues"""
        analysis = {
            "timestamp": datetime.now(timezone.utc),
            "overall_health": 0.0,
            "bottlenecks": [],
            "trends": {},
            "suggestions": [],
        }

        if not metrics:
            return analysis

        # Calculate overall system health
        health_scores = [m.get_health_score() for m in metrics.values()]
        analysis["overall_health"] = statistics.mean(health_scores)

        # Identify bottlenecks
        for name, metric in metrics.items():
            bottlenecks = []

            # High error rate
            if metric.error_rate > 0.05:  # >5%
                bottlenecks.append(
                    {
                        "type": "high_error_rate",
                        "severity": (
                            "critical" if metric.error_rate > 0.1 else "warning"
                        ),
                        "value": metric.error_rate,
                        "description": f"Error rate is {metric.error_rate:.1%}",
                    }
                )

            # Slow response times
            if metric.avg_response_time > 1.0:
                bottlenecks.append(
                    {
                        "type": "slow_response",
                        "severity": (
                            "critical" if metric.avg_response_time > 5.0 else "warning"
                        ),
                        "value": metric.avg_response_time,
                        "description": f"Average response time is {metric.avg_response_time:.2f}s",
                    }
                )

            # High memory usage
            if metric.memory_usage_mb > 500:
                bottlenecks.append(
                    {
                        "type": "high_memory",
                        "severity": "warning",
                        "value": metric.memory_usage_mb,
                        "description": f"Memory usage is {metric.memory_usage_mb:.1f}MB",
                    }
                )

            # High CPU usage
            if metric.cpu_usage_percent > 80:
                bottlenecks.append(
                    {
                        "type": "high_cpu",
                        "severity": (
                            "critical" if metric.cpu_usage_percent > 95 else "warning"
                        ),
                        "value": metric.cpu_usage_percent,
                        "description": f"CPU usage is {metric.cpu_usage_percent:.1f}%",
                    }
                )

            if bottlenecks:
                analysis["bottlenecks"].append(
                    {"component": name, "issues": bottlenecks}
                )

        # Generate optimization suggestions
        suggestions = self._generate_optimization_suggestions(analysis["bottlenecks"])
        analysis["suggestions"] = suggestions

        # Store analysis history
        self.analysis_history.append(analysis)
        if len(self.analysis_history) > 100:  # Keep last 100 analyses
            self.analysis_history = self.analysis_history[-100:]

        return analysis

    def _generate_optimization_suggestions(
        self, bottlenecks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate optimization suggestions based on bottlenecks"""
        suggestions = []

        for bottleneck in bottlenecks:
            component = bottleneck["component"]
            issues = bottleneck["issues"]

            for issue in issues:
                if issue["type"] == "high_error_rate":
                    suggestions.append(
                        {
                            "component": component,
                            "type": "error_handling",
                            "priority": "high",
                            "description": "Implement better error handling and retry logic",
                            "actions": [
                                "Add circuit breaker patterns",
                                "Implement exponential backoff",
                                "Add comprehensive error logging",
                            ],
                        }
                    )

                elif issue["type"] == "slow_response":
                    suggestions.append(
                        {
                            "component": component,
                            "type": "performance",
                            "priority": "high",
                            "description": "Optimize response times",
                            "actions": [
                                "Add caching layers",
                                "Optimize database queries",
                                "Implement request batching",
                                "Add response compression",
                            ],
                        }
                    )

                elif issue["type"] == "high_memory":
                    suggestions.append(
                        {
                            "component": component,
                            "type": "memory",
                            "priority": "medium",
                            "description": "Optimize memory usage",
                            "actions": [
                                "Implement memory pooling",
                                "Add periodic garbage collection",
                                "Optimize data structures",
                                "Implement memory limits",
                            ],
                        }
                    )

                elif issue["type"] == "high_cpu":
                    suggestions.append(
                        {
                            "component": component,
                            "type": "cpu",
                            "priority": "high",
                            "description": "Reduce CPU usage",
                            "actions": [
                                "Optimize algorithms",
                                "Implement async processing",
                                "Add request throttling",
                                "Use worker pools",
                            ],
                        }
                    )

        return suggestions


class TelemetryCollector:
    """
    🚀 COMPREHENSIVE TELEMETRY & MONITORING SYSTEM

    Real-time monitoring with:
    - Component health tracking
    - Performance metrics collection
    - Bottleneck detection
    - Automated alerting
    - Trend analysis
    - Optimization suggestions
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger("astra.telemetry")

        # System state
        self.start_time = time.time()
        self.enabled = True
        self.collection_interval = 30  # seconds

        # Metrics storage
        self.metrics: Dict[str, ComponentMetrics] = {}
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.custom_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))

        # Alerting system
        self.alerts: Dict[str, Alert] = {}
        self.alert_handlers: List[Callable[[Alert], None]] = []
        self.alert_thresholds = {
            "error_rate_warning": 0.05,  # 5%
            "error_rate_critical": 0.10,  # 10%
            "response_time_warning": 1.0,  # 1 second
            "response_time_critical": 5.0,  # 5 seconds
            "memory_warning": 500,  # 500MB
            "memory_critical": 800,  # 800MB
            "cpu_warning": 80,  # 80%
            "cpu_critical": 95,  # 95%
        }

        # Performance analysis
        self.analyzer = PerformanceAnalyzer()

        # Component tracking
        self.registered_components: Dict[str, weakref.ref] = {}
        self.component_start_times: Dict[str, float] = {}

        # Background tasks
        self.collection_task: Optional[asyncio.Task] = None
        self.analysis_task: Optional[asyncio.Task] = None
        self.alert_task: Optional[asyncio.Task] = None

        self.logger.info("🚀 Comprehensive Telemetry System initialized")

    async def initialize(self):
        """Initialize the telemetry system"""
        try:
            self.logger.info("🔧 Initializing Telemetry System...")

            # Start background collection tasks
            self.collection_task = asyncio.create_task(self._metric_collection_loop())
            self.analysis_task = asyncio.create_task(self._performance_analysis_loop())
            self.alert_task = asyncio.create_task(self._alert_processing_loop())

            # Register system components
            await self._register_system_components()

            # Setup system resource monitoring
            if USE_PSUTIL:
                await self._setup_system_monitoring()

            self.logger.info("✅ Telemetry System ready")

        except Exception as e:
            self.logger.error(f"❌ Telemetry initialization failed: {e}")
            raise

    async def _register_system_components(self):
        """Register bot components for monitoring"""
        # Get all loaded cogs
        for name, cog in self.bot.cogs.items():
            await self.register_component(name, cog)

        # Register core bot metrics
        await self.register_component("AstraBot", self.bot)

        self.logger.info(f"📊 Registered {len(self.metrics)} components for monitoring")

    async def register_component(self, name: str, component: Any):
        """Register a component for monitoring"""
        try:
            # Create component metrics
            metrics = ComponentMetrics(name=name, health=ComponentHealth.HEALTHY)

            self.metrics[name] = metrics
            self.registered_components[name] = weakref.ref(component)
            self.component_start_times[name] = time.time()

            self.logger.debug(f"📦 Registered component: {name}")

        except Exception as e:
            self.logger.error(f"Failed to register component {name}: {e}")

    async def _metric_collection_loop(self):
        """Main metric collection loop"""
        while self.enabled:
            try:
                await asyncio.sleep(self.collection_interval)

                # Collect metrics from all registered components
                await self._collect_all_metrics()

                # Store metrics in history
                self._store_metric_history()

            except Exception as e:
                self.logger.error(f"Metric collection error: {e}")

    async def _collect_all_metrics(self):
        """Collect metrics from all registered components"""
        current_time = datetime.now(timezone.utc)

        for name, metrics in self.metrics.items():
            try:
                # Update basic metrics
                metrics.last_updated = current_time

                if name in self.component_start_times:
                    metrics.uptime_seconds = (
                        time.time() - self.component_start_times[name]
                    )

                # Collect component-specific metrics
                component_ref = self.registered_components.get(name)
                if component_ref:
                    component = component_ref()
                    if component:
                        await self._collect_component_metrics(name, component, metrics)

                # Update health status
                self._update_component_health(metrics)

            except Exception as e:
                self.logger.error(f"Error collecting metrics for {name}: {e}")
                self.metrics[name].health = ComponentHealth.UNKNOWN

    async def _collect_component_metrics(
        self, name: str, component: Any, metrics: ComponentMetrics
    ):
        """Collect metrics from a specific component"""
        try:
            # Try to get metrics from component if it has a get_metrics method
            if hasattr(component, "get_metrics"):
                component_metrics = (
                    await component.get_metrics()
                    if asyncio.iscoroutinefunction(component.get_metrics)
                    else component.get_metrics()
                )

                if isinstance(component_metrics, dict):
                    metrics.requests_total = component_metrics.get(
                        "requests_total", metrics.requests_total
                    )
                    metrics.errors_total = component_metrics.get(
                        "errors_total", metrics.errors_total
                    )
                    metrics.avg_response_time = component_metrics.get(
                        "avg_response_time", metrics.avg_response_time
                    )
                    metrics.custom_metrics.update(
                        component_metrics.get("custom_metrics", {})
                    )

            # Calculate derived metrics
            if metrics.requests_total > 0:
                metrics.error_rate = metrics.errors_total / metrics.requests_total

            # System resource metrics (if available)
            if USE_PSUTIL and name == "AstraBot":
                process = psutil.Process()
                metrics.memory_usage_mb = process.memory_info().rss / 1024 / 1024
                metrics.cpu_usage_percent = process.cpu_percent()

        except Exception as e:
            self.logger.error(f"Error collecting metrics for component {name}: {e}")

    def _update_component_health(self, metrics: ComponentMetrics):
        """Update component health based on metrics"""
        health_score = metrics.get_health_score()

        if health_score >= 90:
            metrics.health = ComponentHealth.HEALTHY
        elif health_score >= 70:
            metrics.health = ComponentHealth.DEGRADED
        elif health_score >= 40:
            metrics.health = ComponentHealth.UNHEALTHY
        else:
            metrics.health = ComponentHealth.CRITICAL

    def _store_metric_history(self):
        """Store current metrics in history for trend analysis"""
        current_time = datetime.now(timezone.utc)

        for name, metrics in self.metrics.items():
            # Store key metrics
            self.metric_history[f"{name}_requests_total"].append(
                MetricPoint(current_time, metrics.requests_total, {"component": name})
            )
            self.metric_history[f"{name}_error_rate"].append(
                MetricPoint(current_time, metrics.error_rate, {"component": name})
            )
            self.metric_history[f"{name}_response_time"].append(
                MetricPoint(
                    current_time, metrics.avg_response_time, {"component": name}
                )
            )
            self.metric_history[f"{name}_memory_usage"].append(
                MetricPoint(current_time, metrics.memory_usage_mb, {"component": name})
            )

    async def _performance_analysis_loop(self):
        """Performance analysis and optimization suggestions loop"""
        while self.enabled:
            try:
                await asyncio.sleep(300)  # Every 5 minutes

                # Perform comprehensive analysis
                analysis = self.analyzer.analyze_performance_trends(self.metrics)

                # Log analysis results
                if analysis["bottlenecks"]:
                    self.logger.warning(
                        f"🚨 Performance bottlenecks detected: {len(analysis['bottlenecks'])}"
                    )
                    for bottleneck in analysis["bottlenecks"]:
                        self.logger.warning(
                            f"   {bottleneck['component']}: {len(bottleneck['issues'])} issues"
                        )

                if analysis["suggestions"]:
                    self.logger.info(
                        f"💡 Optimization suggestions: {len(analysis['suggestions'])}"
                    )
                    for suggestion in analysis["suggestions"][:3]:  # Log top 3
                        self.logger.info(
                            f"   {suggestion['component']}: {suggestion['description']}"
                        )

                # Log overall health
                health = analysis["overall_health"]
                health_emoji = "🟢" if health >= 90 else "🟡" if health >= 70 else "🔴"
                self.logger.info(f"{health_emoji} System Health: {health:.1f}%")

            except Exception as e:
                self.logger.error(f"Performance analysis error: {e}")

    async def _alert_processing_loop(self):
        """Process and manage alerts"""
        while self.enabled:
            try:
                await asyncio.sleep(60)  # Every minute

                # Check for alert conditions
                await self._check_alert_conditions()

                # Resolve expired alerts
                self._resolve_expired_alerts()

            except Exception as e:
                self.logger.error(f"Alert processing error: {e}")

    async def _check_alert_conditions(self):
        """Check metrics against alert thresholds"""
        current_time = datetime.now(timezone.utc)

        for name, metrics in self.metrics.items():
            # Error rate alerts
            if metrics.error_rate >= self.alert_thresholds["error_rate_critical"]:
                await self._create_alert(
                    f"{name}_error_rate_critical",
                    AlertLevel.CRITICAL,
                    name,
                    f"Critical error rate: {metrics.error_rate:.1%}",
                    {"error_rate": metrics.error_rate},
                )
            elif metrics.error_rate >= self.alert_thresholds["error_rate_warning"]:
                await self._create_alert(
                    f"{name}_error_rate_warning",
                    AlertLevel.WARNING,
                    name,
                    f"High error rate: {metrics.error_rate:.1%}",
                    {"error_rate": metrics.error_rate},
                )

            # Response time alerts
            if (
                metrics.avg_response_time
                >= self.alert_thresholds["response_time_critical"]
            ):
                await self._create_alert(
                    f"{name}_response_time_critical",
                    AlertLevel.CRITICAL,
                    name,
                    f"Critical response time: {metrics.avg_response_time:.2f}s",
                    {"response_time": metrics.avg_response_time},
                )
            elif (
                metrics.avg_response_time
                >= self.alert_thresholds["response_time_warning"]
            ):
                await self._create_alert(
                    f"{name}_response_time_warning",
                    AlertLevel.WARNING,
                    name,
                    f"Slow response time: {metrics.avg_response_time:.2f}s",
                    {"response_time": metrics.avg_response_time},
                )

            # Memory alerts
            if metrics.memory_usage_mb >= self.alert_thresholds["memory_critical"]:
                await self._create_alert(
                    f"{name}_memory_critical",
                    AlertLevel.CRITICAL,
                    name,
                    f"Critical memory usage: {metrics.memory_usage_mb:.1f}MB",
                    {"memory_mb": metrics.memory_usage_mb},
                )
            elif metrics.memory_usage_mb >= self.alert_thresholds["memory_warning"]:
                await self._create_alert(
                    f"{name}_memory_warning",
                    AlertLevel.WARNING,
                    name,
                    f"High memory usage: {metrics.memory_usage_mb:.1f}MB",
                    {"memory_mb": metrics.memory_usage_mb},
                )

            # CPU alerts (if available)
            if metrics.cpu_usage_percent >= self.alert_thresholds["cpu_critical"]:
                await self._create_alert(
                    f"{name}_cpu_critical",
                    AlertLevel.CRITICAL,
                    name,
                    f"Critical CPU usage: {metrics.cpu_usage_percent:.1f}%",
                    {"cpu_percent": metrics.cpu_usage_percent},
                )
            elif metrics.cpu_usage_percent >= self.alert_thresholds["cpu_warning"]:
                await self._create_alert(
                    f"{name}_cpu_warning",
                    AlertLevel.WARNING,
                    name,
                    f"High CPU usage: {metrics.cpu_usage_percent:.1f}%",
                    {"cpu_percent": metrics.cpu_usage_percent},
                )

    async def _create_alert(
        self,
        alert_id: str,
        level: AlertLevel,
        component: str,
        message: str,
        metadata: Dict[str, Any],
    ):
        """Create or update an alert"""
        if alert_id in self.alerts:
            # Alert already exists, update timestamp
            self.alerts[alert_id].metadata.update(metadata)
            return

        # Create new alert
        alert = Alert(
            id=alert_id,
            level=level,
            component=component,
            message=message,
            created_at=datetime.now(timezone.utc),
            metadata=metadata,
        )

        self.alerts[alert_id] = alert

        # Log alert
        level_emoji = {"info": "ℹ️", "warning": "⚠️", "error": "❌", "critical": "🚨"}
        self.logger.warning(
            f"{level_emoji.get(level.value, '🔔')} ALERT [{level.value.upper()}] {component}: {message}"
        )

        # Notify alert handlers
        for handler in self.alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                self.logger.error(f"Alert handler error: {e}")

    def _resolve_expired_alerts(self):
        """Resolve alerts that are no longer applicable"""
        current_time = datetime.now(timezone.utc)
        resolved_alerts = []

        for alert_id, alert in self.alerts.items():
            # Auto-resolve alerts older than 1 hour if conditions are no longer met
            if (current_time - alert.created_at).total_seconds() > 3600:  # 1 hour
                component_metrics = self.metrics.get(alert.component)
                if component_metrics and self._should_resolve_alert(
                    alert, component_metrics
                ):
                    alert.resolved_at = current_time
                    resolved_alerts.append(alert_id)

        # Remove resolved alerts
        for alert_id in resolved_alerts:
            del self.alerts[alert_id]
            self.logger.info(f"✅ Resolved alert: {alert_id}")

    def _should_resolve_alert(self, alert: Alert, metrics: ComponentMetrics) -> bool:
        """Check if an alert should be auto-resolved"""
        alert_type = alert.id.split("_")[-2] + "_" + alert.id.split("_")[-1]

        if alert_type == "error_rate_warning":
            return (
                metrics.error_rate < self.alert_thresholds["error_rate_warning"] * 0.8
            )
        elif alert_type == "error_rate_critical":
            return (
                metrics.error_rate < self.alert_thresholds["error_rate_critical"] * 0.8
            )
        elif alert_type == "response_time_warning":
            return (
                metrics.avg_response_time
                < self.alert_thresholds["response_time_warning"] * 0.8
            )
        elif alert_type == "response_time_critical":
            return (
                metrics.avg_response_time
                < self.alert_thresholds["response_time_critical"] * 0.8
            )
        elif alert_type == "memory_warning":
            return (
                metrics.memory_usage_mb < self.alert_thresholds["memory_warning"] * 0.8
            )
        elif alert_type == "memory_critical":
            return (
                metrics.memory_usage_mb < self.alert_thresholds["memory_critical"] * 0.8
            )
        elif alert_type == "cpu_warning":
            return (
                metrics.cpu_usage_percent < self.alert_thresholds["cpu_warning"] * 0.8
            )
        elif alert_type == "cpu_critical":
            return (
                metrics.cpu_usage_percent < self.alert_thresholds["cpu_critical"] * 0.8
            )

        return False

    async def _setup_system_monitoring(self):
        """Setup system resource monitoring"""
        if not USE_PSUTIL:
            return

        # Monitor system-wide resources
        system_metrics = ComponentMetrics(name="System")
        self.metrics["System"] = system_metrics

        self.logger.info("🖥️ System resource monitoring enabled")

    # Public API methods

    def record_metric(
        self,
        name: str,
        value: Union[int, float],
        metric_type: MetricType = MetricType.GAUGE,
        labels: Dict[str, str] = None,
    ):
        """Record a custom metric"""
        try:
            labels = labels or {}
            point = MetricPoint(
                timestamp=datetime.now(timezone.utc), value=value, labels=labels
            )

            self.custom_metrics[name].append(point)

        except Exception as e:
            self.logger.error(f"Error recording metric {name}: {e}")

    def record_timer(self, name: str, duration: float, labels: Dict[str, str] = None):
        """Record a timer metric"""
        self.record_metric(name, duration, MetricType.TIMER, labels)

    def increment_counter(
        self, name: str, value: int = 1, labels: Dict[str, str] = None
    ):
        """Increment a counter metric"""
        # Get the last value and increment
        if name in self.custom_metrics and self.custom_metrics[name]:
            last_value = self.custom_metrics[name][-1].value
            new_value = last_value + value
        else:
            new_value = value

        self.record_metric(name, new_value, MetricType.COUNTER, labels)

    def add_alert_handler(self, handler: Callable[[Alert], None]):
        """Add an alert handler"""
        self.alert_handlers.append(handler)

    def get_component_metrics(self, component: str) -> Optional[ComponentMetrics]:
        """Get metrics for a specific component"""
        return self.metrics.get(component)

    def get_all_metrics(self) -> Dict[str, ComponentMetrics]:
        """Get all component metrics"""
        return self.metrics.copy()

    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return list(self.alerts.values())

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health summary"""
        if not self.metrics:
            return {"health_score": 0, "status": "unknown", "components": 0}

        health_scores = [m.get_health_score() for m in self.metrics.values()]
        overall_health = statistics.mean(health_scores)

        healthy_components = sum(
            1 for m in self.metrics.values() if m.health == ComponentHealth.HEALTHY
        )

        status = "healthy"
        if overall_health < 70:
            status = "degraded"
        if overall_health < 40:
            status = "unhealthy"

        return {
            "health_score": overall_health,
            "status": status,
            "components_total": len(self.metrics),
            "components_healthy": healthy_components,
            "active_alerts": len(self.alerts),
            "uptime_seconds": time.time() - self.start_time,
        }

    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        analysis = self.analyzer.analyze_performance_trends(self.metrics)
        system_health = self.get_system_health()

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system_health": system_health,
            "performance_analysis": analysis,
            "active_alerts": [alert.to_dict() for alert in self.alerts.values()],
            "component_metrics": {
                name: {
                    "health": metrics.health.value,
                    "health_score": metrics.get_health_score(),
                    "uptime_seconds": metrics.uptime_seconds,
                    "requests_total": metrics.requests_total,
                    "error_rate": metrics.error_rate,
                    "avg_response_time": metrics.avg_response_time,
                    "memory_usage_mb": metrics.memory_usage_mb,
                    "cpu_usage_percent": metrics.cpu_usage_percent,
                }
                for name, metrics in self.metrics.items()
            },
        }

    async def shutdown(self):
        """Graceful shutdown of the telemetry system"""
        self.logger.info("🔄 Shutting down Telemetry System...")

        self.enabled = False

        # Cancel background tasks
        tasks = [self.collection_task, self.analysis_task, self.alert_task]
        for task in tasks:
            if task and not task.done():
                task.cancel()

        # Wait for tasks to complete
        if tasks:
            await asyncio.gather(
                *[t for t in tasks if t and not t.done()], return_exceptions=True
            )

        self.logger.info("✅ Telemetry System shutdown completed")


# Global instance
_telemetry: Optional[TelemetryCollector] = None


async def get_telemetry(bot: commands.Bot = None) -> TelemetryCollector:
    """Get or create the global telemetry instance"""
    global _telemetry
    if _telemetry is None:
        if bot is None:
            raise ValueError("Bot instance required for first initialization")
        _telemetry = TelemetryCollector(bot)
        await _telemetry.initialize()
    return _telemetry


async def initialize_telemetry(bot: commands.Bot) -> TelemetryCollector:
    """Initialize the global telemetry system"""
    global _telemetry
    _telemetry = TelemetryCollector(bot)
    await _telemetry.initialize()
    return _telemetry
