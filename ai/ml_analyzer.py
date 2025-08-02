"""
Machine Learning Utilities for Astra Bot
Implements user behavior analysis and predictive engagement
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import sqlite3
import json
import logging
import re
from pathlib import Path
from collections import defaultdict, Counter
import asyncio

# Optional ML dependencies - graceful fallback if not available
try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    # Create mock classes for type hints
    class KMeans:
        def __init__(self, *args, **kwargs): pass
        def fit_predict(self, X): return [0] * len(X)
    
    class StandardScaler:
        def __init__(self): pass
        def fit_transform(self, X): return X
        def transform(self, X): return X
    
    class PCA:
        def __init__(self, *args, **kwargs): pass
        def fit_transform(self, X): return X
    
    class joblib:
        @staticmethod
        def dump(*args, **kwargs): pass
        @staticmethod
        def load(*args, **kwargs): return None

logger = logging.getLogger("astra.ml")


@dataclass
class UserBehaviorProfile:
    """User behavior profile with ML features"""
    user_id: int
    activity_patterns: Dict[str, float]  # Hour of day activity distribution
    topic_preferences: Dict[str, float]  # Topic engagement scores
    communication_patterns: Dict[str, float]  # Message length, emoji usage, etc.
    engagement_responsiveness: float  # How likely to respond to AI
    optimal_engagement_times: List[int]  # Best hours to engage (0-23)
    conversation_style_cluster: int  # ML cluster assignment
    sentiment_baseline: float  # Typical sentiment score
    interaction_frequency: float  # Messages per day average


class MLUserAnalyzer:
    """Machine Learning-based user behavior analyzer"""
    
    def __init__(self, db_path: str = "data/ai_conversations.db"):
        self.db_path = Path(db_path)
        self.user_profiles: Dict[int, UserBehaviorProfile] = {}
        self.scaler = StandardScaler()
        self.kmeans_model = None
        self.pca_model = None
        self.model_path = Path("data/ml_models")
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize models
        self._load_or_create_models()
    
    def _load_or_create_models(self):
        """Load existing ML models or create new ones"""
        try:
            scaler_path = self.model_path / "scaler.joblib"
            kmeans_path = self.model_path / "kmeans.joblib"
            pca_path = self.model_path / "pca.joblib"
            
            if all(path.exists() for path in [scaler_path, kmeans_path, pca_path]):
                self.scaler = joblib.load(scaler_path)
                self.kmeans_model = joblib.load(kmeans_path)
                self.pca_model = joblib.load(pca_path)
                logger.info("✅ ML models loaded successfully")
            else:
                logger.info("🔄 Creating new ML models")
                self._create_initial_models()
                
        except Exception as e:
            logger.error(f"ML model loading error: {e}")
            self._create_initial_models()
    
    def _create_initial_models(self):
        """Create initial ML models with default parameters"""
        self.scaler = StandardScaler()
        self.kmeans_model = KMeans(n_clusters=5, random_state=42, n_init=10)
        self.pca_model = PCA(n_components=0.95)  # Keep 95% of variance
    
    async def analyze_user_behavior(self, user_id: int) -> UserBehaviorProfile:
        """Analyze user behavior and create/update profile"""
        try:
            # Get user data from database
            user_data = await self._get_user_data(user_id)
            
            if not user_data:
                # Create default profile for new users
                return UserBehaviorProfile(
                    user_id=user_id,
                    activity_patterns={str(i): 0.0 for i in range(24)},
                    topic_preferences={},
                    communication_patterns={},
                    engagement_responsiveness=0.5,
                    optimal_engagement_times=[12, 18, 20],  # Default peak times
                    conversation_style_cluster=0,
                    sentiment_baseline=0.5,
                    interaction_frequency=0.0
                )
            
            # Extract features
            features = self._extract_behavioral_features(user_data)
            
            # Create behavior profile
            profile = UserBehaviorProfile(
                user_id=user_id,
                activity_patterns=features["activity_patterns"],
                topic_preferences=features["topic_preferences"],
                communication_patterns=features["communication_patterns"],
                engagement_responsiveness=features["engagement_responsiveness"],
                optimal_engagement_times=features["optimal_engagement_times"],
                conversation_style_cluster=features.get("cluster", 0),
                sentiment_baseline=features["sentiment_baseline"],
                interaction_frequency=features["interaction_frequency"]
            )
            
            # Store profile
            self.user_profiles[user_id] = profile
            
            return profile
            
        except Exception as e:
            logger.error(f"User behavior analysis error for {user_id}: {e}")
            return UserBehaviorProfile(user_id=user_id, activity_patterns={}, topic_preferences={}, communication_patterns={}, engagement_responsiveness=0.5, optimal_engagement_times=[], conversation_style_cluster=0, sentiment_baseline=0.5, interaction_frequency=0.0)
    
    async def _get_user_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user conversation data from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get conversations
                cursor.execute("""
                    SELECT message_content, ai_response, mood, topics, engagement_score, 
                           timestamp, response_time, feedback_score
                    FROM conversations 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 1000
                """, (user_id,))
                
                conversations = cursor.fetchall()
                
                if not conversations:
                    return None
                
                # Get user profile
                cursor.execute("""
                    SELECT name, interaction_count, preferred_topics, communication_style,
                           response_preferences, mood_history, engagement_patterns, 
                           last_seen, conversation_topics
                    FROM user_profiles 
                    WHERE user_id = ?
                """, (user_id,))
                
                profile_data = cursor.fetchone()
                
                return {
                    "conversations": conversations,
                    "profile": profile_data,
                    "user_id": user_id
                }
                
        except Exception as e:
            logger.error(f"Database query error for user {user_id}: {e}")
            return None
    
    def _extract_behavioral_features(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract behavioral features from user data"""
        conversations = user_data["conversations"]
        profile = user_data["profile"]
        
        features = {}
        
        # Activity patterns (hour of day distribution)
        hourly_activity = defaultdict(int)
        for conv in conversations:
            timestamp_str = conv[5]  # timestamp column
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                hourly_activity[timestamp.hour] += 1
            except:
                continue
        
        total_messages = sum(hourly_activity.values())
        features["activity_patterns"] = {
            str(hour): (count / total_messages if total_messages > 0 else 0.0)
            for hour, count in hourly_activity.items()
        }
        
        # Fill missing hours
        for hour in range(24):
            if str(hour) not in features["activity_patterns"]:
                features["activity_patterns"][str(hour)] = 0.0
        
        # Topic preferences
        topic_engagement = defaultdict(list)
        for conv in conversations:
            topics_str = conv[3]  # topics column
            engagement_score = conv[4]  # engagement_score column
            
            try:
                topics = json.loads(topics_str) if topics_str else []
                for topic in topics:
                    topic_engagement[topic].append(engagement_score)
            except:
                continue
        
        features["topic_preferences"] = {
            topic: np.mean(scores) for topic, scores in topic_engagement.items()
        }
        
        # Communication patterns
        message_lengths = []
        emoji_usage = 0
        question_count = 0
        
        for conv in conversations:
            message = conv[0]  # message_content
            if message:
                message_lengths.append(len(message))
                emoji_usage += len(re.findall(r'[😀-🙏]', message))
                if '?' in message:
                    question_count += 1
        
        features["communication_patterns"] = {
            "avg_message_length": np.mean(message_lengths) if message_lengths else 0.0,
            "emoji_per_message": emoji_usage / len(conversations) if conversations else 0.0,
            "question_ratio": question_count / len(conversations) if conversations else 0.0
        }
        
        # Engagement responsiveness
        engagement_scores = [conv[4] for conv in conversations if conv[4] is not None]
        features["engagement_responsiveness"] = np.mean(engagement_scores) if engagement_scores else 0.5
        
        # Optimal engagement times
        optimal_hours = sorted(
            hourly_activity.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]  # Top 3 hours
        features["optimal_engagement_times"] = [hour for hour, _ in optimal_hours]
        
        # Sentiment baseline
        mood_scores = []
        mood_mapping = {
            "happy": 0.8, "excited": 0.9, "neutral": 0.5,
            "confused": 0.4, "frustrated": 0.2, "sad": 0.1
        }
        
        for conv in conversations:
            mood = conv[2]  # mood column
            if mood in mood_mapping:
                mood_scores.append(mood_mapping[mood])
        
        features["sentiment_baseline"] = np.mean(mood_scores) if mood_scores else 0.5
        
        # Interaction frequency (messages per day)
        if conversations:
            first_conv = datetime.fromisoformat(conversations[-1][5])
            last_conv = datetime.fromisoformat(conversations[0][5])
            days_active = max(1, (last_conv - first_conv).days)
            features["interaction_frequency"] = len(conversations) / days_active
        else:
            features["interaction_frequency"] = 0.0
        
        return features
    
    async def cluster_users(self, min_interactions: int = 10) -> Dict[int, int]:
        """Cluster users based on behavior patterns"""
        try:
            # Get users with sufficient data
            eligible_users = [
                user_id for user_id, profile in self.user_profiles.items()
                if profile.interaction_frequency >= min_interactions / 30  # At least min_interactions per month
            ]
            
            if len(eligible_users) < 5:
                logger.warning("Not enough users for clustering")
                return {}
            
            # Prepare feature matrix
            feature_matrix = []
            user_ids = []
            
            for user_id in eligible_users:
                profile = self.user_profiles[user_id]
                
                # Create feature vector
                features = []
                
                # Activity pattern features (24 hours)
                features.extend([profile.activity_patterns.get(str(h), 0.0) for h in range(24)])
                
                # Communication pattern features
                comm_patterns = profile.communication_patterns
                features.extend([
                    comm_patterns.get("avg_message_length", 0.0),
                    comm_patterns.get("emoji_per_message", 0.0),
                    comm_patterns.get("question_ratio", 0.0)
                ])
                
                # Other behavioral features
                features.extend([
                    profile.engagement_responsiveness,
                    profile.sentiment_baseline,
                    profile.interaction_frequency
                ])
                
                feature_matrix.append(features)
                user_ids.append(user_id)
            
            # Convert to numpy array
            X = np.array(feature_matrix)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Apply PCA if we have enough features
            if X_scaled.shape[1] > 10:
                X_scaled = self.pca_model.fit_transform(X_scaled)
            
            # Perform clustering
            n_clusters = min(5, len(eligible_users) // 2)  # Adjust cluster count
            self.kmeans_model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = self.kmeans_model.fit_predict(X_scaled)
            
            # Update user profiles with cluster assignments
            user_clusters = {}
            for user_id, cluster in zip(user_ids, cluster_labels):
                self.user_profiles[user_id].conversation_style_cluster = int(cluster)
                user_clusters[user_id] = int(cluster)
            
            # Save models
            await self._save_models()
            
            logger.info(f"✅ Clustered {len(eligible_users)} users into {n_clusters} groups")
            return user_clusters
            
        except Exception as e:
            logger.error(f"User clustering error: {e}")
            return {}
    
    async def _save_models(self):
        """Save ML models to disk"""
        try:
            joblib.dump(self.scaler, self.model_path / "scaler.joblib")
            if self.kmeans_model:
                joblib.dump(self.kmeans_model, self.model_path / "kmeans.joblib")
            if self.pca_model:
                joblib.dump(self.pca_model, self.model_path / "pca.joblib")
            
            logger.debug("ML models saved successfully")
            
        except Exception as e:
            logger.error(f"Model saving error: {e}")
    
    def predict_engagement_success(self, user_id: int, current_hour: int, topic: str = None) -> float:
        """Predict probability of successful engagement"""
        try:
            profile = self.user_profiles.get(user_id)
            if not profile:
                return 0.5  # Default probability
            
            # Base probability from user's general responsiveness
            base_prob = profile.engagement_responsiveness
            
            # Time-based adjustment
            hour_activity = profile.activity_patterns.get(str(current_hour), 0.0)
            time_multiplier = 1.0 + (hour_activity * 2)  # Boost if it's their active time
            
            # Topic-based adjustment
            topic_multiplier = 1.0
            if topic and topic in profile.topic_preferences:
                topic_score = profile.topic_preferences[topic]
                topic_multiplier = 1.0 + (topic_score * 0.5)
            
            # Calculate final probability
            probability = base_prob * time_multiplier * topic_multiplier
            
            # Clamp to [0, 1] range
            return min(1.0, max(0.0, probability))
            
        except Exception as e:
            logger.error(f"Engagement prediction error for user {user_id}: {e}")
            return 0.5
    
    def get_optimal_engagement_strategy(self, user_id: int) -> Dict[str, Any]:
        """Get personalized engagement strategy for user"""
        try:
            profile = self.user_profiles.get(user_id)
            if not profile:
                return {
                    "best_times": [12, 18, 20],
                    "preferred_topics": ["general"],
                    "communication_style": "casual",
                    "engagement_frequency": "moderate"
                }
            
            # Determine communication style based on cluster
            cluster_styles = {
                0: "casual_friendly",
                1: "informative_detailed",
                2: "brief_efficient",
                3: "enthusiastic_emoji",
                4: "question_focused"
            }
            
            communication_style = cluster_styles.get(
                profile.conversation_style_cluster, "casual_friendly"
            )
            
            # Determine engagement frequency
            if profile.interaction_frequency > 5:
                frequency = "high"
            elif profile.interaction_frequency > 1:
                frequency = "moderate"
            else:
                frequency = "low"
            
            # Get top topics
            top_topics = sorted(
                profile.topic_preferences.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            
            preferred_topics = [topic for topic, _ in top_topics] if top_topics else ["general"]
            
            return {
                "best_times": profile.optimal_engagement_times,
                "preferred_topics": preferred_topics,
                "communication_style": communication_style,
                "engagement_frequency": frequency,
                "sentiment_approach": "positive" if profile.sentiment_baseline > 0.6 else "supportive"
            }
            
        except Exception as e:
            logger.error(f"Engagement strategy error for user {user_id}: {e}")
            return {
                "best_times": [12, 18, 20],
                "preferred_topics": ["general"],
                "communication_style": "casual",
                "engagement_frequency": "moderate"
            }
    
    async def update_user_feedback(self, user_id: int, interaction_success: bool, context: Dict[str, Any]):
        """Update user model based on interaction feedback"""
        try:
            profile = self.user_profiles.get(user_id)
            if not profile:
                return
            
            # Update engagement responsiveness based on feedback
            feedback_weight = 0.1  # Learning rate
            if interaction_success:
                profile.engagement_responsiveness = min(1.0, 
                    profile.engagement_responsiveness + feedback_weight)
            else:
                profile.engagement_responsiveness = max(0.0, 
                    profile.engagement_responsiveness - feedback_weight)
            
            # Update topic preferences if topic context provided
            if "topic" in context:
                topic = context["topic"]
                current_score = profile.topic_preferences.get(topic, 0.5)
                
                if interaction_success:
                    new_score = min(1.0, current_score + feedback_weight)
                else:
                    new_score = max(0.0, current_score - feedback_weight)
                
                profile.topic_preferences[topic] = new_score
            
            logger.debug(f"Updated feedback for user {user_id}: success={interaction_success}")
            
        except Exception as e:
            logger.error(f"User feedback update error for {user_id}: {e}")
    
    async def get_analytics_summary(self) -> Dict[str, Any]:
        """Get ML analytics summary"""
        try:
            total_users = len(self.user_profiles)
            
            if total_users == 0:
                return {"total_users": 0, "clusters": {}, "avg_engagement": 0.0}
            
            # Cluster distribution
            cluster_counts = defaultdict(int)
            engagement_scores = []
            
            for profile in self.user_profiles.values():
                cluster_counts[profile.conversation_style_cluster] += 1
                engagement_scores.append(profile.engagement_responsiveness)
            
            # Calculate statistics
            avg_engagement = np.mean(engagement_scores) if engagement_scores else 0.0
            
            # Most active hours across all users
            hourly_totals = defaultdict(float)
            for profile in self.user_profiles.values():
                for hour, activity in profile.activity_patterns.items():
                    hourly_totals[int(hour)] += activity
            
            peak_hours = sorted(hourly_totals.items(), key=lambda x: x[1], reverse=True)[:3]
            
            return {
                "total_users": total_users,
                "clusters": dict(cluster_counts),
                "avg_engagement": avg_engagement,
                "peak_hours": [hour for hour, _ in peak_hours],
                "model_status": {
                    "scaler_trained": self.scaler is not None,
                    "kmeans_trained": self.kmeans_model is not None,
                    "pca_trained": self.pca_model is not None
                }
            }
            
        except Exception as e:
            logger.error(f"Analytics summary error: {e}")
            return {"error": str(e)}


# Global ML analyzer instance
ml_analyzer: Optional[MLUserAnalyzer] = None


def initialize_ml_analyzer(db_path: str = "data/ai_conversations.db") -> MLUserAnalyzer:
    """Initialize the global ML analyzer"""
    global ml_analyzer
    ml_analyzer = MLUserAnalyzer(db_path)
    return ml_analyzer


def get_ml_analyzer() -> Optional[MLUserAnalyzer]:
    """Get the global ML analyzer instance"""
    return ml_analyzer
