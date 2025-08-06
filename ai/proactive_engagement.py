"""
Proactive AI Engagement System for Astra Bot
Smart conversation participation and proactive responses
"""

import random
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
import re

class ProactiveEngagement:
    """Handles proactive AI conversation engagement"""
    
    def __init__(self):
        self.conversation_cooldowns: Dict[int, datetime] = {}  # Channel-based cooldowns
        self.user_engagement_history: Dict[int, List[datetime]] = {}  # User engagement tracking
        
    async def should_engage_proactively(
        self, 
        message_content: str, 
        user_id: int, 
        channel_id: int, 
        guild_id: int = None,
        user_profile: Dict = None
    ) -> Tuple[bool, str]:
        """
        Determine if AI should proactively engage in conversation
        Returns: (should_engage, engagement_reason)
        """
        
        # Check cooldown - don't spam channels
        if await self._is_on_cooldown(channel_id):
            return False, "cooldown"
        
        message_lower = message_content.lower()
        engagement_score = 0.0
        reasons = []
        
        # 1. Topic-based engagement
        topic_score, topic_reasons = await self._analyze_topic_interest(message_lower, user_profile)
        engagement_score += topic_score
        reasons.extend(topic_reasons)
        
        # 2. Emotional context engagement
        emotion_score, emotion_reasons = await self._analyze_emotional_context(message_lower)
        engagement_score += emotion_score
        reasons.extend(emotion_reasons)
        
        # 3. Question or help-seeking engagement
        help_score, help_reasons = await self._analyze_help_seeking(message_lower)
        engagement_score += help_score
        reasons.extend(help_reasons)
        
        # 4. User-specific engagement preferences
        personal_score, personal_reasons = await self._analyze_personal_engagement(
            user_id, user_profile
        )
        engagement_score += personal_score
        reasons.extend(personal_reasons)
        
        # 5. Conversation context engagement
        context_score, context_reasons = await self._analyze_conversation_context(
            message_content, channel_id
        )
        engagement_score += context_score
        reasons.extend(context_reasons)
        
        # 6. Random engagement for natural conversation flow
        if engagement_score > 0.3 and random.random() < 0.15:
            engagement_score += 0.2
            reasons.append("natural_conversation_flow")
        
        # Engagement threshold
        should_engage = engagement_score >= 0.4
        
        if should_engage:
            await self._set_cooldown(channel_id)
            await self._track_user_engagement(user_id)
        
        return should_engage, ", ".join(reasons) if reasons else "low_score"
    
    async def _is_on_cooldown(self, channel_id: int) -> bool:
        """Check if channel is on engagement cooldown"""
        if channel_id not in self.conversation_cooldowns:
            return False
        
        cooldown_end = self.conversation_cooldowns[channel_id]
        return datetime.now(timezone.utc) < cooldown_end
    
    async def _set_cooldown(self, channel_id: int):
        """Set engagement cooldown for channel"""
        # Random cooldown between 1-5 minutes to feel natural
        cooldown_minutes = random.randint(1, 5)
        cooldown_end = datetime.now(timezone.utc) + timedelta(minutes=cooldown_minutes)
        self.conversation_cooldowns[channel_id] = cooldown_end
    
    async def _track_user_engagement(self, user_id: int):
        """Track user engagement for personalization"""
        if user_id not in self.user_engagement_history:
            self.user_engagement_history[user_id] = []
        
        self.user_engagement_history[user_id].append(datetime.now(timezone.utc))
        
        # Keep only last 50 engagements
        if len(self.user_engagement_history[user_id]) > 50:
            self.user_engagement_history[user_id] = self.user_engagement_history[user_id][-50:]
    
    async def _analyze_topic_interest(
        self, 
        message_lower: str, 
        user_profile: Dict = None
    ) -> Tuple[float, List[str]]:
        """Analyze if message contains interesting topics"""
        score = 0.0
        reasons = []
        
        # High-interest topics (always engage)
        high_interest_topics = {
            "space": ["space", "universe", "cosmos", "galaxy", "star", "planet", "black hole", "nasa", "spacex"],
            "stellaris": ["stellaris", "empire", "colony", "fleet", "paradox", "galaxy", "species"],
            "science": ["science", "research", "discovery", "experiment", "theory", "physics", "chemistry"],
            "technology": ["ai", "artificial intelligence", "machine learning", "programming", "tech"],
            "philosophy": ["philosophy", "meaning", "existence", "consciousness", "reality", "truth"]
        }
        
        for topic, keywords in high_interest_topics.items():
            if any(keyword in message_lower for keyword in keywords):
                score += 0.4
                reasons.append(f"high_interest_{topic}")
        
        # User's favorite topics (from profile)
        if user_profile and "user_personality" in user_profile:
            favorite_topics = user_profile["user_personality"].get("favorite_topics", [])
            for topic in favorite_topics:
                if topic in message_lower:
                    score += 0.3
                    reasons.append(f"user_favorite_{topic}")
        
        # Trending/current topics
        trending_keywords = [
            "breakthrough", "discovery", "announcement", "news", "update",
            "launch", "mission", "exploration", "innovation"
        ]
        
        if any(keyword in message_lower for keyword in trending_keywords):
            score += 0.2
            reasons.append("trending_topic")
        
        return min(score, 1.0), reasons
    
    async def _analyze_emotional_context(self, message_lower: str) -> Tuple[float, List[str]]:
        """Analyze emotional context for engagement"""
        score = 0.0
        reasons = []
        
        # Strong emotions (high engagement)
        strong_emotions = {
            "excitement": ["amazing", "incredible", "fantastic", "awesome", "mind-blowing", "wow"],
            "confusion": ["confused", "don't understand", "unclear", "lost", "puzzled"],
            "frustration": ["frustrated", "annoying", "difficult", "struggling", "stuck"],
            "curiosity": ["wonder", "curious", "interesting", "fascinating", "how does", "why does"],
            "achievement": ["achieved", "accomplished", "success", "completed", "finished", "solved"]
        }
        
        for emotion, keywords in strong_emotions.items():
            if any(keyword in message_lower for keyword in keywords):
                score += 0.4
                reasons.append(f"emotion_{emotion}")
        
        # Support-seeking indicators
        support_keywords = [
            "help", "advice", "guidance", "suggestions", "recommendations",
            "what should", "how can", "need to know"
        ]
        
        if any(keyword in message_lower for keyword in support_keywords):
            score += 0.3
            reasons.append("support_seeking")
        
        return min(score, 1.0), reasons
    
    async def _analyze_help_seeking(self, message_lower: str) -> Tuple[float, List[str]]:
        """Analyze if user is seeking help or asking questions"""
        score = 0.0
        reasons = []
        
        # Direct questions
        question_starters = [
            "how", "what", "why", "when", "where", "who", "which",
            "can you", "could you", "would you", "do you know"
        ]
        
        if any(message_lower.startswith(starter) for starter in question_starters):
            score += 0.5
            reasons.append("direct_question")
        
        # Question marks
        if "?" in message_lower:
            score += 0.3
            reasons.append("question_mark")
        
        # Help-seeking language
        help_patterns = [
            "i need", "i'm looking for", "can anyone", "does anyone know",
            "how do i", "what's the best way", "any suggestions"
        ]
        
        if any(pattern in message_lower for pattern in help_patterns):
            score += 0.4
            reasons.append("help_seeking")
        
        return min(score, 1.0), reasons
    
    async def _analyze_personal_engagement(
        self, 
        user_id: int, 
        user_profile: Dict = None
    ) -> Tuple[float, List[str]]:
        """Analyze user-specific engagement factors"""
        score = 0.0
        reasons = []
        
        if not user_profile:
            return 0.0, []
        
        personality = user_profile.get("user_personality", {})
        
        # Users who appreciate AI interaction
        if personality.get("technical_interest", 0) > 0.6:
            score += 0.2
            reasons.append("tech_interested_user")
        
        # Active users get more engagement
        total_interactions = user_profile.get("interaction_history", {}).get("total_interactions", 0)
        if total_interactions > 50:
            score += 0.15
            reasons.append("active_user")
        
        # Users with positive feedback history
        positive_feedback = user_profile.get("interaction_history", {}).get("positive_feedback", 0)
        total_feedback = (positive_feedback + 
                         user_profile.get("interaction_history", {}).get("negative_feedback", 0))
        
        if total_feedback > 0 and positive_feedback / total_feedback > 0.7:
            score += 0.2
            reasons.append("positive_feedback_history")
        
        # Recent engagement frequency
        if user_id in self.user_engagement_history:
            recent_engagements = [
                eng for eng in self.user_engagement_history[user_id]
                if eng > datetime.now(timezone.utc) - timedelta(hours=24)
            ]
            
            # Don't over-engage with same user
            if len(recent_engagements) > 5:
                score -= 0.3
                reasons.append("too_frequent_engagement")
            elif len(recent_engagements) == 0:
                score += 0.1
                reasons.append("first_daily_engagement")
        
        return max(0.0, min(score, 1.0)), reasons
    
    async def _analyze_conversation_context(
        self, 
        message_content: str, 
        channel_id: int
    ) -> Tuple[float, List[str]]:
        """Analyze conversation context"""
        score = 0.0
        reasons = []
        
        # Long messages suggest deeper engagement
        if len(message_content) > 200:
            score += 0.2
            reasons.append("detailed_message")
        
        # Messages with multiple sentences
        sentence_count = len([s for s in message_content.split('.') if s.strip()])
        if sentence_count > 2:
            score += 0.15
            reasons.append("multi_sentence_message")
        
        # Technical or complex language
        complex_words = [
            "algorithm", "implementation", "optimization", "architecture",
            "methodology", "analysis", "synthesis", "comprehensive"
        ]
        
        if any(word in message_content.lower() for word in complex_words):
            score += 0.2
            reasons.append("complex_language")
        
        return min(score, 1.0), reasons
    
    async def generate_engagement_type(
        self, 
        message_content: str, 
        engagement_reason: str,
        user_profile: Dict = None
    ) -> str:
        """Generate the type of engagement based on context"""
        
        reasons = engagement_reason.split(", ")
        message_lower = message_content.lower()
        
        # Question response
        if "direct_question" in reasons or "question_mark" in reasons:
            return "answer_question"
        
        # Help and support
        if "help_seeking" in reasons or "support_seeking" in reasons:
            return "offer_help"
        
        # Emotional support
        if any(r.startswith("emotion_") for r in reasons):
            if "emotion_excitement" in reasons:
                return "share_enthusiasm"
            elif "emotion_confusion" in reasons or "emotion_frustration" in reasons:
                return "provide_support"
            elif "emotion_achievement" in reasons:
                return "celebrate_success"
            else:
                return "acknowledge_emotion"
        
        # Topic discussion
        if any(r.startswith("high_interest_") for r in reasons):
            return "discuss_topic"
        
        # Personal engagement
        if "user_favorite" in engagement_reason:
            return "personal_interest"
        
        # Default conversational engagement
        return "casual_engagement"


# Global instance
proactive_engagement = ProactiveEngagement()
