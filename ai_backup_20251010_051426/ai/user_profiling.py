"""
Enhanced User Profiling System for Astra Bot
Tracks user preferences, personality traits, and conversation patterns
"""

import json
import sqlite3
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import re
from collections import Counter, defaultdict


@dataclass
class UserPersonality:
    """User personality profile"""

    user_id: int
    username: str

    # Communication style
    formal_preference: float = 0.5  # 0.0 = casual, 1.0 = formal
    humor_appreciation: float = 0.5  # 0.0 = serious, 1.0 = loves humor
    detail_preference: float = 0.5  # 0.0 = brief, 1.0 = detailed
    technical_interest: float = 0.5  # 0.0 = non-technical, 1.0 = highly technical

    # Interests and topics
    favorite_topics: List[str] = None
    conversation_frequency: int = 0
    avg_message_length: float = 0.0

    # Interaction patterns
    active_hours: List[int] = None  # Hours when user is most active
    response_time_preference: str = "normal"  # "immediate", "normal", "patient"
    emoji_usage: float = 0.0  # Frequency of emoji usage

    # Learning data
    last_updated: str = None
    interaction_count: int = 0
    positive_feedback_count: int = 0
    negative_feedback_count: int = 0

    def __post_init__(self):
        if self.favorite_topics is None:
            self.favorite_topics = []
        if self.active_hours is None:
            self.active_hours = []
        if self.last_updated is None:
            self.last_updated = datetime.now(timezone.utc).isoformat()


class UserProfileManager:
    """Manages user personality profiles and learning"""

    def __init__(self, db_path: str = "data/user_profiles.db"):
        self.db_path = db_path
        self.profiles: Dict[int, UserPersonality] = {}
        self._setup_database()

    def _setup_database(self):
        """Initialize the user profiles database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        profile_data TEXT,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS conversation_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        message_content TEXT,
                        message_length INTEGER,
                        contains_emoji BOOLEAN,
                        hour_sent INTEGER,
                        topics TEXT,
                        sentiment REAL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                    )
                """
                )

                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_user_conversations 
                    ON conversation_history(user_id, timestamp)
                """
                )

        except Exception as e:
            print(f"Database setup error: {e}")

    async def get_user_profile(
        self, user_id: int, username: str = None
    ) -> UserPersonality:
        """Get or create user personality profile"""
        if user_id in self.profiles:
            return self.profiles[user_id]

        # Load from database
        profile = await self._load_profile_from_db(user_id, username)
        self.profiles[user_id] = profile
        return profile

    async def _load_profile_from_db(
        self, user_id: int, username: str = None
    ) -> UserPersonality:
        """Load user profile from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT username, profile_data FROM user_profiles WHERE user_id = ?",
                    (user_id,),
                )
                result = cursor.fetchone()

                if result:
                    stored_username, profile_json = result
                    profile_data = json.loads(profile_json)
                    profile = UserPersonality(**profile_data)

                    # Update username if provided and different
                    if username and username != stored_username:
                        profile.username = username
                        await self._save_profile_to_db(profile)

                    return profile
                else:
                    # Create new profile
                    profile = UserPersonality(
                        user_id=user_id, username=username or f"User{user_id}"
                    )
                    await self._save_profile_to_db(profile)
                    return profile

        except Exception as e:
            print(f"Error loading profile for {user_id}: {e}")
            return UserPersonality(
                user_id=user_id, username=username or f"User{user_id}"
            )

    async def _save_profile_to_db(self, profile: UserPersonality):
        """Save user profile to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                profile_json = json.dumps(asdict(profile))
                conn.execute(
                    """
                    INSERT OR REPLACE INTO user_profiles (user_id, username, profile_data, last_updated)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """,
                    (profile.user_id, profile.username, profile_json),
                )

        except Exception as e:
            print(f"Error saving profile for {profile.user_id}: {e}")

    async def analyze_message(
        self, user_id: int, message: str, username: str = None
    ) -> Dict[str, Any]:
        """Analyze a message and extract personality insights"""
        analysis = {
            "length": len(message),
            "word_count": len(message.split()),
            "contains_emoji": bool(re.search(r"[😀-🿿]|[👀-👿]|[💀-💿]", message)),
            "hour": datetime.now(timezone.utc).hour,
            "topics": await self._extract_topics(message),
            "sentiment": await self._analyze_sentiment(message),
            "formality": await self._analyze_formality(message),
            "technical_content": await self._analyze_technical_content(message),
        }

        # Store conversation data
        await self._store_conversation(user_id, message, analysis)

        # Update user profile
        await self._update_user_profile(user_id, analysis, username)

        return analysis

    async def _extract_topics(self, message: str) -> List[str]:
        """Extract topics from message"""
        message_lower = message.lower()
        topics = []

        topic_keywords = {
            "space": [
                "space",
                "universe",
                "cosmos",
                "galaxy",
                "star",
                "planet",
                "asteroid",
                "nebula",
            ],
            "stellaris": [
                "stellaris",
                "empire",
                "colony",
                "fleet",
                "technology",
                "research",
            ],
            "science": ["science", "research", "experiment", "theory", "discovery"],
            "technology": [
                "tech",
                "technology",
                "computer",
                "software",
                "AI",
                "machine",
            ],
            "gaming": ["game", "gaming", "play", "player", "level", "achievement"],
            "programming": [
                "code",
                "programming",
                "python",
                "javascript",
                "debug",
                "function",
            ],
            "personal": ["i", "me", "my", "myself", "feel", "think", "believe"],
            "questions": [
                "how",
                "what",
                "why",
                "when",
                "where",
                "can you",
                "could you",
            ],
            "emotions": [
                "happy",
                "sad",
                "excited",
                "frustrated",
                "confused",
                "amazing",
            ],
        }

        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                topics.append(topic)

        return topics

    async def _analyze_sentiment(self, message: str) -> float:
        """Basic sentiment analysis (positive = 1.0, negative = -1.0, neutral = 0.0)"""
        positive_words = [
            "good",
            "great",
            "awesome",
            "amazing",
            "excellent",
            "fantastic",
            "love",
            "like",
            "happy",
            "excited",
            "wonderful",
            "perfect",
            "brilliant",
            "outstanding",
        ]

        negative_words = [
            "bad",
            "terrible",
            "awful",
            "hate",
            "dislike",
            "sad",
            "angry",
            "frustrated",
            "confused",
            "difficult",
            "problem",
            "issue",
            "wrong",
            "error",
        ]

        message_lower = message.lower()
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)

        if positive_count == negative_count:
            return 0.0
        elif positive_count > negative_count:
            return min(1.0, (positive_count - negative_count) / 10.0)
        else:
            return max(-1.0, (positive_count - negative_count) / 10.0)

    async def _analyze_formality(self, message: str) -> float:
        """Analyze formality level (0.0 = casual, 1.0 = formal)"""
        formal_indicators = [
            "please",
            "thank you",
            "could you",
            "would you",
            "may i",
            "excuse me",
            "i would like",
            "i appreciate",
            "furthermore",
            "however",
            "therefore",
        ]

        casual_indicators = [
            "hey",
            "hi",
            "yo",
            "sup",
            "gonna",
            "wanna",
            "kinda",
            "sorta",
            "yeah",
            "yep",
            "nah",
            "lol",
            "omg",
            "btw",
            "tbh",
        ]

        message_lower = message.lower()
        formal_count = sum(
            1 for indicator in formal_indicators if indicator in message_lower
        )
        casual_count = sum(
            1 for indicator in casual_indicators if indicator in message_lower
        )

        # Punctuation and capitalization
        if message.count(".") > 0 and message[0].isupper():
            formal_count += 1

        if formal_count + casual_count == 0:
            return 0.5  # Neutral

        return formal_count / (formal_count + casual_count)

    async def _analyze_technical_content(self, message: str) -> float:
        """Analyze technical content level (0.0 = non-technical, 1.0 = highly technical)"""
        technical_terms = [
            "algorithm",
            "database",
            "server",
            "API",
            "function",
            "variable",
            "loop",
            "array",
            "object",
            "class",
            "method",
            "parameter",
            "return",
            "import",
            "library",
            "framework",
            "deployment",
            "configuration",
            "optimization",
        ]

        message_lower = message.lower()
        technical_count = sum(1 for term in technical_terms if term in message_lower)
        word_count = len(message.split())

        if word_count == 0:
            return 0.0

        return min(1.0, technical_count / word_count * 10)

    async def _store_conversation(
        self, user_id: int, message: str, analysis: Dict[str, Any]
    ):
        """Store conversation data for learning"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO conversation_history 
                    (user_id, message_content, message_length, contains_emoji, hour_sent, topics, sentiment)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        user_id,
                        message[:500],  # Truncate for storage
                        analysis["length"],
                        analysis["contains_emoji"],
                        analysis["hour"],
                        ",".join(analysis["topics"]),
                        analysis["sentiment"],
                    ),
                )
        except Exception as e:
            print(f"Error storing conversation: {e}")

    async def _update_user_profile(
        self, user_id: int, analysis: Dict[str, Any], username: str = None
    ):
        """Update user profile based on message analysis"""
        profile = await self.get_user_profile(user_id, username)

        # Update interaction count
        profile.interaction_count += 1

        # Update communication preferences (weighted average)
        weight = 0.1  # How much this single message affects the profile

        profile.formal_preference = (
            profile.formal_preference * (1 - weight) + analysis["formality"] * weight
        )

        profile.technical_interest = (
            profile.technical_interest * (1 - weight)
            + analysis["technical_content"] * weight
        )

        profile.emoji_usage = (
            profile.emoji_usage * (1 - weight)
            + (1.0 if analysis["contains_emoji"] else 0.0) * weight
        )

        # Update average message length
        profile.avg_message_length = (
            profile.avg_message_length * (profile.interaction_count - 1)
            + analysis["length"]
        ) / profile.interaction_count

        # Update favorite topics
        for topic in analysis["topics"]:
            if topic not in profile.favorite_topics:
                profile.favorite_topics.append(topic)

            # Keep only top 10 topics
            if len(profile.favorite_topics) > 10:
                profile.favorite_topics = profile.favorite_topics[-10:]

        # Update active hours
        current_hour = analysis["hour"]
        if current_hour not in profile.active_hours:
            profile.active_hours.append(current_hour)

        # Keep only recent active hours (sliding window)
        if len(profile.active_hours) > 24:
            profile.active_hours = profile.active_hours[-24:]

        profile.last_updated = datetime.now(timezone.utc).isoformat()

        # Save updated profile
        await self._save_profile_to_db(profile)
        self.profiles[user_id] = profile

    async def get_personalized_context(self, user_id: int) -> Dict[str, Any]:
        """Get personalized context for AI responses"""
        if user_id not in self.profiles:
            return {}

        profile = self.profiles[user_id]

        context = {
            "user_personality": {
                "prefers_formal": profile.formal_preference > 0.6,
                "appreciates_humor": profile.humor_appreciation > 0.6,
                "likes_details": profile.detail_preference > 0.6,
                "technical_interest": profile.technical_interest,
                "favorite_topics": profile.favorite_topics[:5],  # Top 5 topics
                "communication_style": (
                    "formal" if profile.formal_preference > 0.6 else "casual"
                ),
                "typical_message_length": (
                    "long" if profile.avg_message_length > 100 else "short"
                ),
                "uses_emojis": profile.emoji_usage > 0.3,
                "username": profile.username,
            },
            "interaction_history": {
                "total_interactions": profile.interaction_count,
                "positive_feedback": profile.positive_feedback_count,
                "negative_feedback": profile.negative_feedback_count,
            },
        }

        return context


# Global instance
user_profile_manager = UserProfileManager()
