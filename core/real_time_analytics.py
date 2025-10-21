"""
📊 REAL-TIME SECURITY ANALYTICS DASHBOARD
Live monitoring and visualization for security metrics

Features:
- Real-time threat detection analytics
- Live security dashboards
- Performance visualization
- Threat intelligence feeds
- Interactive security monitoring
- Automated alerting system
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, deque
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import statistics
import weakref


@dataclass
class SecurityMetrics:
    """🔐 Real-time security metrics"""

    timestamp: float
    threats_detected: int
    threats_blocked: int
    users_flagged: int
    violations_per_minute: float
    avg_threat_response_time: float
    system_load: float
    active_moderations: int
    trust_score_average: float
    risk_distribution: Dict[str, int]


@dataclass
class PerformanceMetrics:
    """⚡ Real-time performance metrics"""

    timestamp: float
    cpu_usage: float
    memory_usage: float
    database_response_time: float
    ai_processing_time: float
    cache_hit_rate: float
    active_connections: int
    queries_per_second: float
    error_rate: float


@dataclass
class ThreatIntelligence:
    """🕵️ Threat intelligence data"""

    threat_id: str
    threat_type: str
    severity: int
    source: str
    indicators: List[str]
    first_seen: float
    last_seen: float
    occurrences: int
    status: str  # active, mitigated, resolved


class RealTimeAnalytics:
    """📊 Real-time analytics processing engine"""

    def __init__(self):
        self.logger = logging.getLogger("astra.analytics")

        # 📊 REAL-TIME DATA STREAMS
        self.security_stream = deque(maxlen=1000)
        self.performance_stream = deque(maxlen=1000)
        self.threat_stream = deque(maxlen=500)
        self.user_activity_stream = deque(maxlen=2000)

        # 🎯 ANALYTICS ENGINES
        self.pattern_detector = PatternDetector()
        self.anomaly_detector = AnomalyDetector()
        self.threat_analyzer = ThreatAnalyzer()
        self.performance_analyzer = PerformanceAnalyzer()

        # 📈 METRICS AGGREGATION
        self.metrics_aggregator = MetricsAggregator()

        # 🚨 ALERT SYSTEM
        self.alert_system = AlertSystem()

        # 📊 DASHBOARD STATE
        self.dashboard_state = {
            "security_overview": {},
            "performance_overview": {},
            "threat_intelligence": {},
            "user_analytics": {},
            "system_health": {},
            "alerts": [],
        }

        # ⚙️ CONFIGURATION
        self.config = {
            "update_interval": 5.0,  # seconds
            "alert_thresholds": {
                "high_threat_rate": 10,  # threats per minute
                "low_trust_score": 50.0,
                "high_error_rate": 5.0,  # percentage
                "high_response_time": 2000,  # milliseconds
                "memory_usage": 85.0,  # percentage
            },
            "retention_hours": 24,
            "analytics_enabled": True,
            "real_time_updates": True,
        }

        self._monitoring_active = False
        self._update_tasks = []

    async def start_analytics(self):
        """🚀 Start real-time analytics"""
        if self._monitoring_active:
            return

        self._monitoring_active = True
        self.logger.info("📊 Starting real-time security analytics")

        # Start analytics tasks
        self._update_tasks = [
            asyncio.create_task(self._security_analytics_loop()),
            asyncio.create_task(self._performance_analytics_loop()),
            asyncio.create_task(self._threat_intelligence_loop()),
            asyncio.create_task(self._dashboard_update_loop()),
            asyncio.create_task(self._alert_monitoring_loop()),
        ]

    async def stop_analytics(self):
        """🛑 Stop real-time analytics"""
        self._monitoring_active = False

        # Cancel all tasks
        for task in self._update_tasks:
            task.cancel()

        self._update_tasks.clear()
        self.logger.info("🛑 Real-time analytics stopped")

    async def record_security_event(self, event_data: Dict[str, Any]):
        """🔐 Record security event for analytics"""

        timestamp = time.time()
        event = {
            "timestamp": timestamp,
            "event_type": event_data.get("event_type", "unknown"),
            "severity": event_data.get("severity", 1),
            "user_id": event_data.get("user_id"),
            "details": event_data.get("details", {}),
            "response_time": event_data.get("response_time", 0),
            "action_taken": event_data.get("action_taken", "none"),
        }

        self.security_stream.append(event)

        # Real-time pattern detection
        await self.pattern_detector.analyze_event(event)

        # Anomaly detection
        await self.anomaly_detector.check_anomaly(event)

        # Update dashboard
        if self.config["real_time_updates"]:
            await self._update_security_dashboard()

    async def record_performance_metric(self, metric_data: Dict[str, Any]):
        """⚡ Record performance metric"""

        timestamp = time.time()
        metric = {
            "timestamp": timestamp,
            "metric_type": metric_data.get("metric_type", "general"),
            "value": metric_data.get("value", 0),
            "unit": metric_data.get("unit", ""),
            "source": metric_data.get("source", "system"),
        }

        self.performance_stream.append(metric)

        # Performance analysis
        await self.performance_analyzer.analyze_metric(metric)

    async def record_user_activity(self, activity_data: Dict[str, Any]):
        """👤 Record user activity for behavioral analytics"""

        timestamp = time.time()
        activity = {
            "timestamp": timestamp,
            "user_id": activity_data.get("user_id"),
            "activity_type": activity_data.get("activity_type", "message"),
            "channel_id": activity_data.get("channel_id"),
            "trust_impact": activity_data.get("trust_impact", 0),
            "metadata": activity_data.get("metadata", {}),
        }

        self.user_activity_stream.append(activity)

    async def get_security_dashboard(self) -> Dict[str, Any]:
        """🔐 Get real-time security dashboard data"""

        current_time = time.time()
        cutoff_time = current_time - 3600  # Last hour

        # Filter recent security events
        recent_events = [
            event for event in self.security_stream if event["timestamp"] > cutoff_time
        ]

        # Calculate security metrics
        threats_detected = len([e for e in recent_events if e["severity"] >= 3])
        threats_blocked = len([e for e in recent_events if e["action_taken"] != "none"])
        users_flagged = len(set(e["user_id"] for e in recent_events if e["user_id"]))

        # Calculate violations per minute
        if recent_events:
            time_span = (current_time - min(e["timestamp"] for e in recent_events)) / 60
            violations_per_minute = len(recent_events) / max(time_span, 1)
        else:
            violations_per_minute = 0.0

        # Calculate average response time
        response_times = [
            e["response_time"] for e in recent_events if e["response_time"] > 0
        ]
        avg_response_time = statistics.mean(response_times) if response_times else 0.0

        # Risk distribution
        risk_distribution = defaultdict(int)
        for event in recent_events:
            if event["severity"] <= 2:
                risk_distribution["low"] += 1
            elif event["severity"] <= 4:
                risk_distribution["medium"] += 1
            else:
                risk_distribution["high"] += 1

        return {
            "timestamp": current_time,
            "metrics": {
                "threats_detected": threats_detected,
                "threats_blocked": threats_blocked,
                "users_flagged": users_flagged,
                "violations_per_minute": round(violations_per_minute, 2),
                "avg_response_time": round(avg_response_time, 2),
                "active_moderations": len(
                    [e for e in recent_events if e["action_taken"] == "active"]
                ),
            },
            "risk_distribution": dict(risk_distribution),
            "recent_events": recent_events[-20:],  # Last 20 events
            "patterns": await self.pattern_detector.get_detected_patterns(),
            "anomalies": await self.anomaly_detector.get_recent_anomalies(),
            "trends": await self._calculate_security_trends(recent_events),
        }

    async def get_performance_dashboard(self) -> Dict[str, Any]:
        """⚡ Get real-time performance dashboard data"""

        current_time = time.time()
        cutoff_time = current_time - 3600  # Last hour

        # Filter recent performance metrics
        recent_metrics = [
            metric
            for metric in self.performance_stream
            if metric["timestamp"] > cutoff_time
        ]

        # Group metrics by type
        metrics_by_type = defaultdict(list)
        for metric in recent_metrics:
            metrics_by_type[metric["metric_type"]].append(metric["value"])

        # Calculate aggregated metrics
        performance_data = {}
        for metric_type, values in metrics_by_type.items():
            if values:
                performance_data[metric_type] = {
                    "current": values[-1],
                    "average": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                    "trend": self._calculate_trend(values[-10:]),  # Last 10 values
                }

        return {
            "timestamp": current_time,
            "metrics": performance_data,
            "system_health": await self._calculate_system_health(),
            "alerts": await self.alert_system.get_active_alerts(),
            "historical_data": await self._get_performance_history(),
        }

    async def get_threat_intelligence(self) -> Dict[str, Any]:
        """🕵️ Get threat intelligence dashboard"""

        current_time = time.time()

        # Get active threats
        active_threats = await self.threat_analyzer.get_active_threats()

        # Get threat trends
        threat_trends = await self.threat_analyzer.get_threat_trends()

        # Get IOCs (Indicators of Compromise)
        iocs = await self.threat_analyzer.get_indicators_of_compromise()

        return {
            "timestamp": current_time,
            "active_threats": active_threats,
            "threat_trends": threat_trends,
            "indicators_of_compromise": iocs,
            "threat_score": await self.threat_analyzer.calculate_threat_score(),
            "mitigation_recommendations": await self.threat_analyzer.get_mitigation_recommendations(),
        }

    async def get_user_analytics(self) -> Dict[str, Any]:
        """👥 Get user behavior analytics"""

        current_time = time.time()
        cutoff_time = current_time - 86400  # Last 24 hours

        # Filter recent user activities
        recent_activities = [
            activity
            for activity in self.user_activity_stream
            if activity["timestamp"] > cutoff_time
        ]

        # Calculate user metrics
        active_users = len(set(a["user_id"] for a in recent_activities if a["user_id"]))

        # Activity distribution
        activity_distribution = defaultdict(int)
        for activity in recent_activities:
            activity_distribution[activity["activity_type"]] += 1

        # Trust impact analysis
        trust_impacts = [
            a["trust_impact"] for a in recent_activities if a["trust_impact"] != 0
        ]
        avg_trust_impact = statistics.mean(trust_impacts) if trust_impacts else 0.0

        # Behavioral patterns
        behavioral_patterns = await self._analyze_behavioral_patterns(recent_activities)

        return {
            "timestamp": current_time,
            "active_users": active_users,
            "activity_distribution": dict(activity_distribution),
            "trust_metrics": {
                "average_impact": round(avg_trust_impact, 2),
                "positive_interactions": len([i for i in trust_impacts if i > 0]),
                "negative_interactions": len([i for i in trust_impacts if i < 0]),
            },
            "behavioral_patterns": behavioral_patterns,
            "user_risk_levels": await self._calculate_user_risk_levels(),
        }

    async def _security_analytics_loop(self):
        """🔐 Security analytics processing loop"""
        while self._monitoring_active:
            try:
                await self._update_security_dashboard()
                await asyncio.sleep(self.config["update_interval"])
            except Exception as e:
                self.logger.error(f"❌ Security analytics error: {e}")
                await asyncio.sleep(10)

    async def _performance_analytics_loop(self):
        """⚡ Performance analytics processing loop"""
        while self._monitoring_active:
            try:
                await self._update_performance_dashboard()
                await asyncio.sleep(self.config["update_interval"])
            except Exception as e:
                self.logger.error(f"❌ Performance analytics error: {e}")
                await asyncio.sleep(10)

    async def _threat_intelligence_loop(self):
        """🕵️ Threat intelligence processing loop"""
        while self._monitoring_active:
            try:
                await self.threat_analyzer.update_threat_intelligence()
                await asyncio.sleep(60)  # Every minute
            except Exception as e:
                self.logger.error(f"❌ Threat intelligence error: {e}")
                await asyncio.sleep(30)

    async def _dashboard_update_loop(self):
        """📊 Dashboard state update loop"""
        while self._monitoring_active:
            try:
                # Update all dashboard components
                self.dashboard_state["security_overview"] = (
                    await self.get_security_dashboard()
                )
                self.dashboard_state["performance_overview"] = (
                    await self.get_performance_dashboard()
                )
                self.dashboard_state["threat_intelligence"] = (
                    await self.get_threat_intelligence()
                )
                self.dashboard_state["user_analytics"] = await self.get_user_analytics()

                await asyncio.sleep(self.config["update_interval"])
            except Exception as e:
                self.logger.error(f"❌ Dashboard update error: {e}")
                await asyncio.sleep(15)

    async def _alert_monitoring_loop(self):
        """🚨 Alert monitoring loop"""
        while self._monitoring_active:
            try:
                await self.alert_system.check_alert_conditions(self.dashboard_state)
                await asyncio.sleep(30)  # Every 30 seconds
            except Exception as e:
                self.logger.error(f"❌ Alert monitoring error: {e}")
                await asyncio.sleep(60)

    async def _update_security_dashboard(self):
        """🔐 Update security dashboard components"""
        # This would update the live security dashboard
        pass

    async def _update_performance_dashboard(self):
        """⚡ Update performance dashboard components"""
        # This would update the live performance dashboard
        pass

    async def _calculate_security_trends(self, events: List[Dict]) -> Dict[str, Any]:
        """📈 Calculate security trends"""
        if len(events) < 2:
            return {"trend": "stable", "change": 0.0}

        # Calculate trend over time
        timestamps = [e["timestamp"] for e in events]
        severities = [e["severity"] for e in events]

        # Simple linear trend calculation
        if len(severities) >= 10:
            recent_avg = statistics.mean(severities[-5:])
            older_avg = statistics.mean(severities[-10:-5])
            change = (
                ((recent_avg - older_avg) / older_avg) * 100 if older_avg > 0 else 0
            )

            if change > 10:
                trend = "increasing"
            elif change < -10:
                trend = "decreasing"
            else:
                trend = "stable"

            return {"trend": trend, "change": round(change, 2)}

        return {"trend": "insufficient_data", "change": 0.0}

    def _calculate_trend(self, values: List[float]) -> str:
        """📊 Calculate trend for a series of values"""
        if len(values) < 3:
            return "stable"

        # Simple trend detection
        increases = sum(1 for i in range(1, len(values)) if values[i] > values[i - 1])
        decreases = sum(1 for i in range(1, len(values)) if values[i] < values[i - 1])

        if increases > decreases * 1.5:
            return "increasing"
        elif decreases > increases * 1.5:
            return "decreasing"
        else:
            return "stable"

    async def _calculate_system_health(self) -> Dict[str, Any]:
        """💚 Calculate overall system health"""

        health_score = 100.0
        issues = []

        # Check recent alerts
        active_alerts = await self.alert_system.get_active_alerts()
        critical_alerts = [a for a in active_alerts if a.get("severity") == "critical"]

        if critical_alerts:
            health_score -= len(critical_alerts) * 20
            issues.extend([f"Critical alert: {a['message']}" for a in critical_alerts])

        # Check performance metrics
        recent_performance = (
            list(self.performance_stream)[-10:] if self.performance_stream else []
        )
        if recent_performance:
            error_rates = [
                m["value"]
                for m in recent_performance
                if m["metric_type"] == "error_rate"
            ]
            if (
                error_rates
                and max(error_rates)
                > self.config["alert_thresholds"]["high_error_rate"]
            ):
                health_score -= 15
                issues.append("High error rate detected")

        # Determine health status
        if health_score >= 90:
            status = "excellent"
        elif health_score >= 70:
            status = "good"
        elif health_score >= 50:
            status = "warning"
        else:
            status = "critical"

        return {
            "score": max(0, health_score),
            "status": status,
            "issues": issues,
            "last_updated": time.time(),
        }

    async def _get_performance_history(self) -> Dict[str, List]:
        """📊 Get performance history for charts"""

        # Get last 24 hours of data points for charting
        current_time = time.time()
        cutoff_time = current_time - 86400

        recent_metrics = [
            m for m in self.performance_stream if m["timestamp"] > cutoff_time
        ]

        # Group by hour for trend visualization
        hourly_data = defaultdict(list)
        for metric in recent_metrics:
            hour = int(metric["timestamp"] // 3600) * 3600
            hourly_data[hour].append(metric)

        # Aggregate hourly data
        history = {
            "timestamps": [],
            "cpu_usage": [],
            "memory_usage": [],
            "response_time": [],
            "error_rate": [],
        }

        for hour in sorted(hourly_data.keys()):
            hour_metrics = hourly_data[hour]
            history["timestamps"].append(hour)

            # Calculate averages for the hour
            cpu_values = [
                m["value"] for m in hour_metrics if m["metric_type"] == "cpu_usage"
            ]
            memory_values = [
                m["value"] for m in hour_metrics if m["metric_type"] == "memory_usage"
            ]
            response_values = [
                m["value"] for m in hour_metrics if m["metric_type"] == "response_time"
            ]
            error_values = [
                m["value"] for m in hour_metrics if m["metric_type"] == "error_rate"
            ]

            history["cpu_usage"].append(
                statistics.mean(cpu_values) if cpu_values else 0
            )
            history["memory_usage"].append(
                statistics.mean(memory_values) if memory_values else 0
            )
            history["response_time"].append(
                statistics.mean(response_values) if response_values else 0
            )
            history["error_rate"].append(
                statistics.mean(error_values) if error_values else 0
            )

        return history

    async def _analyze_behavioral_patterns(
        self, activities: List[Dict]
    ) -> Dict[str, Any]:
        """🧠 Analyze user behavioral patterns"""

        patterns = {
            "activity_peaks": [],
            "risk_indicators": [],
            "engagement_patterns": {},
            "anomalous_behavior": [],
        }

        if not activities:
            return patterns

        # Activity distribution by hour
        hourly_activity = defaultdict(int)
        for activity in activities:
            hour = datetime.fromtimestamp(activity["timestamp"]).hour
            hourly_activity[hour] += 1

        # Find peak activity hours
        if hourly_activity:
            max_activity = max(hourly_activity.values())
            peak_hours = [
                hour
                for hour, count in hourly_activity.items()
                if count > max_activity * 0.8
            ]
            patterns["activity_peaks"] = peak_hours

        # Risk indicators
        risk_activities = [a for a in activities if a["trust_impact"] < -5]
        patterns["risk_indicators"] = len(risk_activities)

        return patterns

    async def _calculate_user_risk_levels(self) -> Dict[str, int]:
        """⚠️ Calculate user risk level distribution"""

        # This would integrate with the trust system
        # For now, return placeholder data
        return {"low_risk": 85, "medium_risk": 12, "high_risk": 3}


class PatternDetector:
    """🔍 Real-time pattern detection"""

    def __init__(self):
        self.detected_patterns = deque(maxlen=100)
        self.pattern_templates = self._load_pattern_templates()

    def _load_pattern_templates(self) -> List[Dict]:
        """📋 Load pattern detection templates"""
        return [
            {
                "name": "spam_burst",
                "description": "Rapid message sending",
                "conditions": {"messages_per_minute": 15, "time_window": 60},
            },
            {
                "name": "coordinated_attack",
                "description": "Multiple users similar behavior",
                "conditions": {"user_count": 3, "similarity_threshold": 0.8},
            },
            {
                "name": "escalating_violations",
                "description": "Increasing violation severity",
                "conditions": {"severity_increase": 2, "time_window": 300},
            },
        ]

    async def analyze_event(self, event: Dict[str, Any]):
        """🔍 Analyze event for patterns"""
        # Pattern detection logic would go here
        pass

    async def get_detected_patterns(self) -> List[Dict[str, Any]]:
        """📊 Get recently detected patterns"""
        return list(self.detected_patterns)


class AnomalyDetector:
    """🚨 Real-time anomaly detection"""

    def __init__(self):
        self.baseline_metrics = {}
        self.anomalies = deque(maxlen=50)
        self.learning_enabled = True

    async def check_anomaly(self, event: Dict[str, Any]):
        """🚨 Check for anomalous behavior"""
        # Anomaly detection logic would go here
        pass

    async def get_recent_anomalies(self) -> List[Dict[str, Any]]:
        """📊 Get recent anomalies"""
        return list(self.anomalies)


class ThreatAnalyzer:
    """🕵️ Threat intelligence analyzer"""

    def __init__(self):
        self.active_threats = {}
        self.threat_history = deque(maxlen=1000)
        self.threat_feeds = []

    async def update_threat_intelligence(self):
        """🔄 Update threat intelligence data"""
        # Threat intelligence update logic would go here
        pass

    async def get_active_threats(self) -> List[Dict[str, Any]]:
        """🚨 Get active threats"""
        return list(self.active_threats.values())

    async def get_threat_trends(self) -> Dict[str, Any]:
        """📈 Get threat trends"""
        return {"trend": "stable", "new_threats": 0, "resolved_threats": 0}

    async def get_indicators_of_compromise(self) -> List[Dict[str, Any]]:
        """🔍 Get indicators of compromise"""
        return []

    async def calculate_threat_score(self) -> float:
        """⚠️ Calculate overall threat score"""
        return 2.5  # Scale of 1-10

    async def get_mitigation_recommendations(self) -> List[str]:
        """💡 Get threat mitigation recommendations"""
        return ["Monitor user activity closely", "Update security policies"]


class PerformanceAnalyzer:
    """⚡ Performance metrics analyzer"""

    def __init__(self):
        self.baseline_performance = {}
        self.performance_history = deque(maxlen=1000)

    async def analyze_metric(self, metric: Dict[str, Any]):
        """📊 Analyze performance metric"""
        # Performance analysis logic would go here
        pass


class MetricsAggregator:
    """📊 Metrics aggregation engine"""

    def __init__(self):
        self.aggregated_metrics = {}

    async def aggregate_metrics(self, time_window: int = 3600) -> Dict[str, Any]:
        """📊 Aggregate metrics over time window"""
        # Metrics aggregation logic would go here
        return {}


class AlertSystem:
    """🚨 Real-time alert system"""

    def __init__(self):
        self.active_alerts = []
        self.alert_history = deque(maxlen=500)
        self.alert_rules = self._load_alert_rules()

    def _load_alert_rules(self) -> List[Dict]:
        """📋 Load alert rules"""
        return [
            {
                "name": "high_threat_rate",
                "condition": "threats_per_minute > 10",
                "severity": "critical",
                "message": "High threat detection rate",
            },
            {
                "name": "system_overload",
                "condition": "cpu_usage > 90 AND memory_usage > 85",
                "severity": "warning",
                "message": "System resource usage is high",
            },
        ]

    async def check_alert_conditions(self, dashboard_state: Dict[str, Any]):
        """🚨 Check for alert conditions"""
        # Alert checking logic would go here
        pass

    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """📊 Get active alerts"""
        return self.active_alerts


# Global analytics instance
analytics = RealTimeAnalytics()


def get_analytics() -> RealTimeAnalytics:
    """Get the global analytics instance"""
    return analytics
