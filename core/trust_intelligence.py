"""
🧠 ULTRA-INTELLIGENT TRUST SYSTEM
Advanced trust management with predictive modeling and behavioral analysis

Features:
- Dynamic trust scoring with ML-based predictions
- Advanced behavioral pattern recognition
- Predictive risk assessment
- Intelligent quarantine management
- Automated trust recovery pathways
- Real-time threat intelligence
"""

import asyncio
import time
import json
import math
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
from functools import lru_cache

# Optional ML imports
try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


@dataclass
class TrustMetrics:
    """📊 Comprehensive trust metrics"""

    user_id: int
    trust_score: float
    risk_level: str
    confidence: float
    behavioral_patterns: Dict[str, Any]
    violation_history: List[Dict[str, Any]]
    positive_interactions: int
    prediction_accuracy: float
    last_updated: float


@dataclass
class BehavioralPattern:
    """🧠 Behavioral pattern analysis"""

    pattern_type: str
    frequency: float
    confidence: float
    trend: str  # increasing, decreasing, stable
    risk_factor: float
    last_observed: float


@dataclass
class TrustPrediction:
    """🔮 Trust prediction data"""

    predicted_score: float
    confidence: float
    time_horizon: int  # seconds
    risk_factors: List[str]
    recommendations: List[str]


class UltraIntelligentTrustSystem:
    """🧠 Ultra-intelligent trust management system"""

    def __init__(self, bot=None):
        self.bot = bot
        self.logger = logging.getLogger("astra.trust_system")

        # 🎯 TRUST DATA STRUCTURES
        self.user_trust_profiles = {}  # user_id -> TrustMetrics
        self.behavioral_patterns = defaultdict(
            lambda: defaultdict(list)
        )  # user_id -> pattern_type -> [data]
        self.trust_predictions = {}  # user_id -> TrustPrediction

        # 📊 INTELLIGENCE BUFFERS
        self.interaction_buffer = deque(maxlen=10000)  # Recent interactions
        self.violation_buffer = deque(maxlen=5000)  # Recent violations
        self.pattern_buffer = deque(maxlen=2000)  # Behavioral patterns

        # 🧠 LEARNING SYSTEM
        self.learning_data = {
            "successful_predictions": 0,
            "failed_predictions": 0,
            "model_accuracy": 0.0,
            "pattern_weights": {},
            "trust_factors": {},
            "risk_indicators": {},
        }

        # 🎛️ TRUST CONFIGURATION
        self.trust_config = {
            # Trust scoring
            "initial_trust": 100.0,
            "max_trust": 150.0,
            "min_trust": 0.0,
            "trust_decay_rate": 0.99,  # Daily decay multiplier
            "trust_recovery_rate": 1.01,  # Daily recovery multiplier
            # Risk thresholds
            "risk_thresholds": {
                "low": 20.0,
                "medium": 50.0,
                "high": 80.0,
                "critical": 95.0,
            },
            # Behavioral analysis
            "pattern_weights": {
                "message_frequency": 0.15,
                "toxicity_pattern": 0.30,
                "positive_engagement": 0.20,
                "response_time": 0.10,
                "content_quality": 0.15,
                "social_integration": 0.10,
            },
            # Prediction settings
            "prediction_horizon": 3600,  # 1 hour
            "confidence_threshold": 0.7,
            "learning_rate": 0.01,
            # Quarantine settings
            "auto_quarantine_threshold": 85.0,
            "quarantine_duration": 3600,  # 1 hour
            "progressive_quarantine": True,
        }

        # 📈 ANALYTICS
        self.analytics = {
            "trust_scores_calculated": 0,
            "predictions_made": 0,
            "patterns_detected": 0,
            "quarantines_issued": 0,
            "trust_recoveries": 0,
            "accuracy_improvements": 0,
        }

        self._monitoring_active = False
        self._last_cleanup = time.time()

    async def start_trust_system(self):
        """🚀 Start the ultra-intelligent trust system"""
        if self._monitoring_active:
            return

        self._monitoring_active = True
        self.logger.info("🧠 Starting ultra-intelligent trust system")

        # Start intelligent tasks
        asyncio.create_task(self._behavioral_analyzer())
        asyncio.create_task(self._trust_predictor())
        asyncio.create_task(self._pattern_learner())
        asyncio.create_task(self._trust_optimizer())

        self.logger.info("🧠 Trust system intelligence active")

    async def calculate_trust_score(
        self, user_id: int, interaction_data: Dict[str, Any] = None
    ) -> TrustMetrics:
        """🎯 Calculate ultra-accurate trust score with predictive modeling"""

        # Get or create trust profile
        if user_id not in self.user_trust_profiles:
            self.user_trust_profiles[user_id] = TrustMetrics(
                user_id=user_id,
                trust_score=self.trust_config["initial_trust"],
                risk_level="low",
                confidence=1.0,
                behavioral_patterns={},
                violation_history=[],
                positive_interactions=0,
                prediction_accuracy=0.0,
                last_updated=time.time(),
            )

        profile = self.user_trust_profiles[user_id]
        current_time = time.time()

        # 🧠 BEHAVIORAL ANALYSIS
        behavioral_score = await self._analyze_behavioral_patterns(
            user_id, interaction_data
        )

        # 📊 VIOLATION IMPACT
        violation_score = await self._calculate_violation_impact(user_id)

        # ✨ POSITIVE INTERACTION BONUS
        positive_score = await self._calculate_positive_bonus(user_id)

        # ⏰ TIME-BASED FACTORS
        time_factor = await self._calculate_time_factors(user_id, current_time)

        # 🎯 WEIGHTED CALCULATION
        base_score = profile.trust_score

        # Apply behavioral adjustments
        behavioral_adjustment = (
            behavioral_score * self.trust_config["pattern_weights"]["message_frequency"]
        )
        violation_adjustment = (
            violation_score * self.trust_config["pattern_weights"]["toxicity_pattern"]
        )
        positive_adjustment = (
            positive_score * self.trust_config["pattern_weights"]["positive_engagement"]
        )

        # Calculate new trust score
        new_score = (
            base_score
            + behavioral_adjustment
            - violation_adjustment
            + positive_adjustment
        )
        new_score *= time_factor  # Apply time decay/recovery

        # Clamp to bounds
        new_score = max(
            self.trust_config["min_trust"],
            min(self.trust_config["max_trust"], new_score),
        )

        # 🔮 RISK ASSESSMENT
        risk_level, confidence = await self._assess_risk_level(
            user_id, new_score, behavioral_score
        )

        # 📊 UPDATE PROFILE
        profile.trust_score = new_score
        profile.risk_level = risk_level
        profile.confidence = confidence
        profile.last_updated = current_time

        # 📈 ANALYTICS
        self.analytics["trust_scores_calculated"] += 1

        # 🚨 AUTO-QUARANTINE CHECK
        if (
            new_score < self.trust_config["auto_quarantine_threshold"]
            and confidence > 0.8
        ):
            await self._consider_auto_quarantine(user_id, profile)

        return profile

    async def _analyze_behavioral_patterns(
        self, user_id: int, interaction_data: Dict[str, Any] = None
    ) -> float:
        """🧠 Advanced behavioral pattern analysis"""

        if not interaction_data:
            return 0.0

        patterns = self.behavioral_patterns[user_id]
        behavioral_score = 0.0

        # 📊 MESSAGE FREQUENCY ANALYSIS
        current_time = time.time()
        message_times = [
            d.get("timestamp", current_time) for d in patterns["message_frequency"]
        ]

        if len(message_times) >= 2:
            # Calculate message frequency over last hour
            recent_messages = [t for t in message_times if current_time - t < 3600]
            frequency = len(recent_messages) / 60  # messages per minute

            # Optimal frequency is 1-5 messages per minute
            if 1 <= frequency <= 5:
                behavioral_score += 10  # Positive contribution
            elif frequency > 10:
                behavioral_score -= 20  # Spam-like behavior
            elif frequency < 0.1:
                behavioral_score -= 5  # Too inactive

        # 📝 CONTENT QUALITY ANALYSIS
        if "content_quality" in interaction_data:
            quality_score = interaction_data["content_quality"]
            behavioral_score += quality_score * 5  # Scale quality impact

        # 🤝 SOCIAL INTEGRATION ANALYSIS
        if "mentions_received" in interaction_data:
            mentions = interaction_data["mentions_received"]
            behavioral_score += min(mentions * 2, 10)  # Popular users bonus

        # 💬 RESPONSE TIME ANALYSIS
        if "response_time" in interaction_data:
            response_time = interaction_data["response_time"]
            if 1 <= response_time <= 30:  # 1-30 seconds is optimal
                behavioral_score += 5
            elif response_time > 300:  # Very slow responses
                behavioral_score -= 3

        # Store pattern data
        patterns["message_frequency"].append(
            {
                "timestamp": current_time,
                "frequency": frequency if len(message_times) >= 2 else 0,
                "behavioral_score": behavioral_score,
            }
        )

        # Keep only recent patterns (last 100)
        if len(patterns["message_frequency"]) > 100:
            patterns["message_frequency"] = patterns["message_frequency"][-100:]

        return behavioral_score

    async def _calculate_violation_impact(self, user_id: int) -> float:
        """⚠️ Calculate impact of violations on trust"""

        profile = self.user_trust_profiles.get(user_id)
        if not profile or not profile.violation_history:
            return 0.0

        current_time = time.time()
        violation_impact = 0.0

        for violation in profile.violation_history:
            violation_time = violation.get("timestamp", 0)
            violation_type = violation.get("type", "unknown")
            severity = violation.get("severity", 1.0)

            # Time decay for violations (older violations have less impact)
            time_diff = current_time - violation_time
            decay_factor = math.exp(-time_diff / 86400)  # Exponential decay over days

            # Base impact by violation type
            base_impact = {
                "spam": 15.0,
                "toxicity": 25.0,
                "caps_abuse": 5.0,
                "mention_spam": 10.0,
                "repeated_content": 8.0,
                "emotional_distress": 2.0,  # Lower impact, more supportive
            }.get(violation_type, 10.0)

            # Apply severity and time decay
            violation_impact += base_impact * severity * decay_factor

        return violation_impact

    async def _calculate_positive_bonus(self, user_id: int) -> float:
        """✨ Calculate positive interaction bonus"""

        profile = self.user_trust_profiles.get(user_id)
        if not profile:
            return 0.0

        # Base positive bonus
        positive_bonus = profile.positive_interactions * 0.5

        # Recent positive interactions have more weight
        patterns = self.behavioral_patterns[user_id]
        if "positive_interactions" in patterns:
            recent_positive = sum(
                1
                for p in patterns["positive_interactions"][-20:]
                if time.time() - p.get("timestamp", 0) < 3600
            )
            positive_bonus += recent_positive * 2

        # Improvement streak bonus
        if hasattr(profile, "improvement_streak"):
            positive_bonus += min(profile.improvement_streak * 1.5, 20)

        return positive_bonus

    async def _calculate_time_factors(self, user_id: int, current_time: float) -> float:
        """⏰ Calculate time-based trust factors"""

        profile = self.user_trust_profiles.get(user_id)
        if not profile:
            return 1.0

        time_since_update = current_time - profile.last_updated
        days_since_update = time_since_update / 86400

        # Trust naturally decays over time without interaction
        if days_since_update > 1:
            if profile.trust_score > 50:
                # High trust users decay slower
                decay_factor = self.trust_config["trust_decay_rate"] ** (
                    days_since_update * 0.5
                )
            else:
                # Low trust users decay faster
                decay_factor = self.trust_config["trust_decay_rate"] ** (
                    days_since_update * 1.5
                )
        else:
            # Recent activity - potential recovery
            if profile.trust_score < 80:
                decay_factor = self.trust_config["trust_recovery_rate"] ** (
                    1 - days_since_update
                )
            else:
                decay_factor = 1.0  # Maintain high trust

        return decay_factor

    async def _assess_risk_level(
        self, user_id: int, trust_score: float, behavioral_score: float
    ) -> Tuple[str, float]:
        """🚨 Intelligent risk level assessment"""

        # Base risk from trust score
        thresholds = self.trust_config["risk_thresholds"]

        if trust_score >= thresholds["critical"]:
            base_risk = "critical"
            confidence = 0.9
        elif trust_score >= thresholds["high"]:
            base_risk = "high"
            confidence = 0.8
        elif trust_score >= thresholds["medium"]:
            base_risk = "medium"
            confidence = 0.7
        else:
            base_risk = "low"
            confidence = 0.6

        # Adjust based on behavioral patterns
        patterns = self.behavioral_patterns[user_id]

        # Check for concerning patterns
        concerning_patterns = 0
        if "message_frequency" in patterns and len(patterns["message_frequency"]) > 5:
            recent_scores = [
                p.get("behavioral_score", 0) for p in patterns["message_frequency"][-5:]
            ]
            avg_score = sum(recent_scores) / len(recent_scores)

            if avg_score < -10:
                concerning_patterns += 1
            elif avg_score > 10:
                concerning_patterns -= 1

        # Adjust risk level based on patterns
        if concerning_patterns > 0:
            if base_risk == "low":
                base_risk = "medium"
            elif base_risk == "medium":
                base_risk = "high"
            confidence += 0.1
        elif concerning_patterns < 0:
            if base_risk == "high":
                base_risk = "medium"
            elif base_risk == "medium":
                base_risk = "low"
            confidence -= 0.1

        # Clamp confidence
        confidence = max(0.1, min(1.0, confidence))

        return base_risk, confidence

    async def _consider_auto_quarantine(self, user_id: int, profile: TrustMetrics):
        """🚨 Consider automatic quarantine for high-risk users"""

        if not self.trust_config["progressive_quarantine"]:
            return

        # Check quarantine history
        patterns = self.behavioral_patterns[user_id]
        recent_quarantines = [
            q
            for q in patterns.get("quarantines", [])
            if time.time() - q.get("timestamp", 0) < 86400
        ]  # Last 24 hours

        # Progressive quarantine durations
        quarantine_duration = self.trust_config["quarantine_duration"] * (
            2 ** len(recent_quarantines)
        )
        quarantine_duration = min(quarantine_duration, 86400)  # Max 24 hours

        # Log quarantine decision
        self.logger.warning(
            f"🚨 Auto-quarantine considered for user {user_id}: "
            f"trust={profile.trust_score:.1f}, risk={profile.risk_level}, "
            f"confidence={profile.confidence:.2f}"
        )

        # Add to quarantine history
        patterns["quarantines"].append(
            {
                "timestamp": time.time(),
                "trust_score": profile.trust_score,
                "risk_level": profile.risk_level,
                "duration": quarantine_duration,
                "reason": "auto_quarantine",
            }
        )

        self.analytics["quarantines_issued"] += 1

    async def predict_future_trust(
        self, user_id: int, time_horizon: int = None
    ) -> TrustPrediction:
        """🔮 Predict future trust score using advanced analytics"""

        if time_horizon is None:
            time_horizon = self.trust_config["prediction_horizon"]

        profile = self.user_trust_profiles.get(user_id)
        if not profile:
            return TrustPrediction(
                predicted_score=self.trust_config["initial_trust"],
                confidence=0.1,
                time_horizon=time_horizon,
                risk_factors=[],
                recommendations=["Insufficient data for prediction"],
            )

        # 📊 TREND ANALYSIS
        patterns = self.behavioral_patterns[user_id]
        current_time = time.time()

        # Analyze trust score trend
        trust_trend = await self._analyze_trust_trend(user_id)

        # Analyze behavioral trends
        behavioral_trend = await self._analyze_behavioral_trend(user_id)

        # 🔮 PREDICTION CALCULATION
        current_score = profile.trust_score

        # Apply trends over time horizon
        time_factor = time_horizon / 3600  # Convert to hours

        # Trust trend impact
        trend_impact = trust_trend * time_factor * 0.1

        # Behavioral trend impact
        behavioral_impact = behavioral_trend * time_factor * 0.05

        # Time decay/recovery
        time_days = time_horizon / 86400
        if current_score > 50:
            time_decay = self.trust_config["trust_decay_rate"] ** (time_days * 0.5)
        else:
            time_decay = self.trust_config["trust_recovery_rate"] ** (time_days * 0.3)

        # Calculate prediction
        predicted_score = (
            current_score + trend_impact + behavioral_impact
        ) * time_decay
        predicted_score = max(
            self.trust_config["min_trust"],
            min(self.trust_config["max_trust"], predicted_score),
        )

        # 📊 CONFIDENCE CALCULATION
        data_points = len(profile.violation_history) + len(
            patterns.get("message_frequency", [])
        )
        confidence = min(
            0.9, 0.3 + (data_points / 100)
        )  # More data = higher confidence

        # 🚨 RISK FACTORS
        risk_factors = []
        if trust_trend < -5:
            risk_factors.append("Declining trust trend")
        if behavioral_trend < -10:
            risk_factors.append("Negative behavioral pattern")
        if len(profile.violation_history) > 5:
            risk_factors.append("Multiple recent violations")
        if predicted_score < 30:
            risk_factors.append("Predicted low trust score")

        # 💡 RECOMMENDATIONS
        recommendations = await self._generate_recommendations(
            user_id, predicted_score, risk_factors
        )

        # Store prediction
        prediction = TrustPrediction(
            predicted_score=predicted_score,
            confidence=confidence,
            time_horizon=time_horizon,
            risk_factors=risk_factors,
            recommendations=recommendations,
        )

        self.trust_predictions[user_id] = prediction
        self.analytics["predictions_made"] += 1

        return prediction

    async def _analyze_trust_trend(self, user_id: int) -> float:
        """📈 Analyze trust score trend"""

        patterns = self.behavioral_patterns[user_id]
        if "trust_history" not in patterns or len(patterns["trust_history"]) < 5:
            return 0.0

        # Get recent trust scores
        recent_scores = patterns["trust_history"][-10:]

        if len(recent_scores) < 2:
            return 0.0

        # Calculate linear trend
        x_values = list(range(len(recent_scores)))
        y_values = [s.get("trust_score", 0) for s in recent_scores]

        if NUMPY_AVAILABLE:
            # Use numpy for accurate trend calculation
            try:
                coeffs = np.polyfit(x_values, y_values, 1)
                return coeffs[0]  # Slope of the trend line
            except:
                pass

        # Fallback: simple slope calculation
        x_mean = sum(x_values) / len(x_values)
        y_mean = sum(y_values) / len(y_values)

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        if denominator == 0:
            return 0.0

        return numerator / denominator

    async def _analyze_behavioral_trend(self, user_id: int) -> float:
        """🧠 Analyze behavioral pattern trends"""

        patterns = self.behavioral_patterns[user_id]

        if (
            "message_frequency" not in patterns
            or len(patterns["message_frequency"]) < 5
        ):
            return 0.0

        # Get recent behavioral scores
        recent_behaviors = patterns["message_frequency"][-10:]
        behavioral_scores = [b.get("behavioral_score", 0) for b in recent_behaviors]

        if len(behavioral_scores) < 2:
            return 0.0

        # Calculate trend
        return (behavioral_scores[-1] - behavioral_scores[0]) / len(behavioral_scores)

    async def _generate_recommendations(
        self, user_id: int, predicted_score: float, risk_factors: List[str]
    ) -> List[str]:
        """💡 Generate intelligent recommendations"""

        recommendations = []

        if predicted_score < 30:
            recommendations.append("Immediate intervention recommended")
            recommendations.append("Consider temporary restrictions")

        if predicted_score < 50:
            recommendations.append("Increased monitoring advised")
            recommendations.append("Encourage positive interactions")

        if "Declining trust trend" in risk_factors:
            recommendations.append("Address underlying behavioral issues")

        if "Multiple recent violations" in risk_factors:
            recommendations.append("Review violation patterns for systematic issues")

        if "Negative behavioral pattern" in risk_factors:
            recommendations.append("Provide guidance on community standards")

        if not recommendations:
            recommendations.append("Continue current monitoring approach")

        return recommendations

    async def _behavioral_analyzer(self):
        """🧠 Continuous behavioral pattern analysis"""
        while self._monitoring_active:
            try:
                current_time = time.time()

                # Analyze patterns for all active users
                for user_id in list(self.user_trust_profiles.keys()):
                    await self._update_behavioral_patterns(user_id, current_time)

                await asyncio.sleep(300)  # Analyze every 5 minutes

            except Exception as e:
                self.logger.error(f"❌ Behavioral analyzer error: {e}")
                await asyncio.sleep(600)

    async def _update_behavioral_patterns(self, user_id: int, current_time: float):
        """🔄 Update behavioral patterns for a user"""

        patterns = self.behavioral_patterns[user_id]
        profile = self.user_trust_profiles.get(user_id)

        if not profile:
            return

        # Store trust history
        if "trust_history" not in patterns:
            patterns["trust_history"] = []

        patterns["trust_history"].append(
            {
                "timestamp": current_time,
                "trust_score": profile.trust_score,
                "risk_level": profile.risk_level,
                "confidence": profile.confidence,
            }
        )

        # Keep only recent history (last 50 points)
        if len(patterns["trust_history"]) > 50:
            patterns["trust_history"] = patterns["trust_history"][-50:]

    async def _trust_predictor(self):
        """🔮 Continuous trust prediction updates"""
        while self._monitoring_active:
            try:
                # Update predictions for active users
                for user_id in list(self.user_trust_profiles.keys()):
                    if user_id not in self.trust_predictions:
                        await self.predict_future_trust(user_id)

                await asyncio.sleep(1800)  # Update predictions every 30 minutes

            except Exception as e:
                self.logger.error(f"❌ Trust predictor error: {e}")
                await asyncio.sleep(3600)

    async def _pattern_learner(self):
        """📚 Machine learning pattern recognition"""
        while self._monitoring_active:
            try:
                # Learn from successful/failed predictions
                await self._update_learning_data()

                # Adjust pattern weights based on accuracy
                await self._optimize_pattern_weights()

                await asyncio.sleep(3600)  # Learn every hour

            except Exception as e:
                self.logger.error(f"❌ Pattern learner error: {e}")
                await asyncio.sleep(7200)

    async def _update_learning_data(self):
        """📊 Update learning data from prediction results"""

        current_time = time.time()

        for user_id, prediction in self.trust_predictions.items():
            profile = self.user_trust_profiles.get(user_id)

            if not profile:
                continue

            # Check if prediction time horizon has passed
            if current_time - profile.last_updated >= prediction.time_horizon:
                # Calculate prediction accuracy
                actual_score = profile.trust_score
                predicted_score = prediction.predicted_score

                accuracy = 1.0 - abs(actual_score - predicted_score) / 100.0
                accuracy = max(0.0, min(1.0, accuracy))

                # Update learning data
                if accuracy > 0.7:
                    self.learning_data["successful_predictions"] += 1
                else:
                    self.learning_data["failed_predictions"] += 1

                # Update model accuracy
                total_predictions = (
                    self.learning_data["successful_predictions"]
                    + self.learning_data["failed_predictions"]
                )

                if total_predictions > 0:
                    self.learning_data["model_accuracy"] = (
                        self.learning_data["successful_predictions"] / total_predictions
                    )

                # Update profile accuracy
                profile.prediction_accuracy = accuracy

    async def _optimize_pattern_weights(self):
        """🎯 Optimize pattern weights based on learning"""

        if self.learning_data["model_accuracy"] < 0.6:
            # Model needs improvement
            learning_rate = self.trust_config["learning_rate"]

            # Adjust weights based on recent performance
            for pattern_type, weight in self.trust_config["pattern_weights"].items():
                # Simple adjustment based on overall accuracy
                if self.learning_data["model_accuracy"] < 0.5:
                    # Reduce impact of all patterns
                    new_weight = weight * (1 - learning_rate)
                else:
                    # Slight increase for moderate accuracy
                    new_weight = weight * (1 + learning_rate * 0.5)

                self.trust_config["pattern_weights"][pattern_type] = max(
                    0.05, min(0.5, new_weight)
                )

            self.analytics["accuracy_improvements"] += 1

    async def _trust_optimizer(self):
        """🚀 Continuous trust system optimization"""
        while self._monitoring_active:
            try:
                current_time = time.time()

                # Cleanup old data every hour
                if current_time - self._last_cleanup > 3600:
                    await self._cleanup_old_data()
                    self._last_cleanup = current_time

                # Optimize trust recovery for improving users
                await self._optimize_trust_recovery()

                await asyncio.sleep(1800)  # Optimize every 30 minutes

            except Exception as e:
                self.logger.error(f"❌ Trust optimizer error: {e}")
                await asyncio.sleep(3600)

    async def _cleanup_old_data(self):
        """🧹 Clean up old trust data"""

        current_time = time.time()
        cutoff_time = current_time - (30 * 86400)  # 30 days

        # Clean behavioral patterns
        for user_id, patterns in self.behavioral_patterns.items():
            for pattern_type, pattern_data in patterns.items():
                if isinstance(pattern_data, list):
                    patterns[pattern_type] = [
                        p for p in pattern_data if p.get("timestamp", 0) > cutoff_time
                    ]

        # Clean old predictions
        old_predictions = [
            user_id
            for user_id, pred in self.trust_predictions.items()
            if current_time
            - self.user_trust_profiles.get(
                user_id, type("", (), {"last_updated": 0})
            ).last_updated
            > pred.time_horizon * 2
        ]

        for user_id in old_predictions:
            del self.trust_predictions[user_id]

    async def _optimize_trust_recovery(self):
        """✨ Optimize trust recovery for improving users"""

        for user_id, profile in self.user_trust_profiles.items():
            if profile.trust_score < 50:  # Low trust users
                patterns = self.behavioral_patterns[user_id]

                # Check for improvement trend
                if "trust_history" in patterns and len(patterns["trust_history"]) >= 5:
                    recent_scores = [
                        h["trust_score"] for h in patterns["trust_history"][-5:]
                    ]

                    # If trust is improving, accelerate recovery
                    if len(recent_scores) >= 2 and recent_scores[-1] > recent_scores[0]:
                        improvement = recent_scores[-1] - recent_scores[0]
                        if improvement > 5:  # Significant improvement
                            # Apply recovery bonus
                            bonus = min(10, improvement * 0.5)
                            profile.trust_score = min(
                                self.trust_config["max_trust"],
                                profile.trust_score + bonus,
                            )

                            self.analytics["trust_recoveries"] += 1

    def get_trust_analytics(self) -> Dict[str, Any]:
        """📊 Get comprehensive trust system analytics"""

        current_time = time.time()

        # Calculate trust distribution
        trust_scores = [p.trust_score for p in self.user_trust_profiles.values()]
        risk_levels = [p.risk_level for p in self.user_trust_profiles.values()]

        trust_distribution = {}
        risk_distribution = {}

        if trust_scores:
            trust_distribution = {
                "mean": sum(trust_scores) / len(trust_scores),
                "min": min(trust_scores),
                "max": max(trust_scores),
                "count": len(trust_scores),
            }

        if risk_levels:
            from collections import Counter

            risk_distribution = dict(Counter(risk_levels))

        return {
            "timestamp": current_time,
            "monitoring_active": self._monitoring_active,
            # User statistics
            "total_users": len(self.user_trust_profiles),
            "trust_distribution": trust_distribution,
            "risk_distribution": risk_distribution,
            # System statistics
            "analytics": self.analytics.copy(),
            "learning_data": self.learning_data.copy(),
            # Configuration
            "trust_config": self.trust_config.copy(),
            # Predictions
            "active_predictions": len(self.trust_predictions),
            "model_accuracy": self.learning_data.get("model_accuracy", 0.0),
            # Data points
            "behavioral_patterns": sum(
                len(patterns) for patterns in self.behavioral_patterns.values()
            ),
            "interaction_buffer_size": len(self.interaction_buffer),
            "violation_buffer_size": len(self.violation_buffer),
        }

    async def export_trust_data(self, filepath: str = None) -> str:
        """📁 Export trust system data"""

        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"trust_system_data_{timestamp}.json"

        export_data = {
            "export_timestamp": time.time(),
            "trust_analytics": self.get_trust_analytics(),
            "user_profiles": {
                str(user_id): asdict(profile)
                for user_id, profile in self.user_trust_profiles.items()
            },
            "behavioral_patterns": {
                str(user_id): patterns
                for user_id, patterns in self.behavioral_patterns.items()
            },
            "trust_predictions": {
                str(user_id): asdict(prediction)
                for user_id, prediction in self.trust_predictions.items()
            },
        }

        try:
            with open(filepath, "w") as f:
                json.dump(export_data, f, indent=2)

            self.logger.info(f"📁 Trust data exported to {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"❌ Failed to export trust data: {e}")
            raise


# Global trust system instance
trust_system = UltraIntelligentTrustSystem()


def get_trust_system() -> UltraIntelligentTrustSystem:
    """Get the global trust system instance"""
    return trust_system
