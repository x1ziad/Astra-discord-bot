"""
Advanced AI Conversation Engine for Astra Bot
Implements context-aware conversations, personality, and modern AI integration with enhanced features
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import re
import random
import time
from pathlib import Path
from collections import defaultdict, deque
import sqlite3
import hashlib

# AI Providers
try:
    import openai

    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from anthropic import Anthropic

    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# ML and Analytics
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import KMeans
    import joblib

    HAS_ML = True
except ImportError:
    HAS_ML = False
    # Fallback implementations
    np = None

logger = logging.getLogger("astra.ai_conversation")


class AIProvider(Enum):
    """Supported AI providers"""

    OPENAI_GPT4 = "openai_gpt4"
    OPENAI_GPT4_TURBO = "openai_gpt4_turbo"
    OPENAI_GPT35_TURBO = "openai_gpt35_turbo"
    ANTHROPIC_CLAUDE_3_OPUS = "anthropic_claude_3_opus"
    ANTHROPIC_CLAUDE_3_SONNET = "anthropic_claude_3_sonnet"
    ANTHROPIC_CLAUDE_3_HAIKU = "anthropic_claude_3_haiku"
    LOCAL_MODEL = "local_model"
    MOCK = "mock"  # For testing without API keys


class ConversationMood(Enum):
    """Enhanced user mood states"""

    EXCITED = "excited"
    HAPPY = "happy"
    CONTENT = "content"
    NEUTRAL = "neutral"
    CURIOUS = "curious"
    CONFUSED = "confused"
    CONCERNED = "concerned"
    FRUSTRATED = "frustrated"
    SAD = "sad"
    ANGRY = "angry"


class EngagementTrigger(Enum):
    """Enhanced types of engagement triggers"""

    DIRECT_MENTION = "direct_mention"
    INDIRECT_MENTION = "indirect_mention"
    KEYWORD_MATCH = "keyword_match"
    QUESTION_DETECTION = "question_detection"
    HELP_REQUEST = "help_request"
    TOPIC_INTEREST = "topic_interest"
    ACTIVITY_PATTERN = "activity_pattern"
    PROACTIVE_ENGAGEMENT = "proactive_engagement"
    USER_JOIN = "user_join"
    USER_RETURN = "user_return"
    LONG_SILENCE = "long_silence"
    EMOTIONAL_SUPPORT = "emotional_support"
    CELEBRATION = "celebration"


class PersonalityTrait(Enum):
    """Astra's personality traits"""

    ENTHUSIASTIC = "enthusiastic"
    KNOWLEDGEABLE = "knowledgeable"
    HELPFUL = "helpful"
    CURIOUS = "curious"
    FRIENDLY = "friendly"
    PATIENT = "patient"
    ENCOURAGING = "encouraging"
    WITTY = "witty"
    COSMIC_MINDED = "cosmic_minded"
    SCIENTIFIC = "scientific"


@dataclass
class ConversationContext:
    """Context for ongoing conversations"""

    user_id: int
    guild_id: Optional[int] = None
    channel_id: Optional[int] = None
    messages: List[Dict[str, Any]] = field(default_factory=list)
    personality_state: Dict[str, Any] = field(default_factory=dict)
    mood: ConversationMood = ConversationMood.NEUTRAL
    topics: List[str] = field(default_factory=list)
    last_interaction: datetime = field(default_factory=datetime.utcnow)
    engagement_score: float = 0.0
    preferences: Dict[str, Any] = field(default_factory=dict)
    memory_keywords: List[str] = field(default_factory=list)


@dataclass
class UserProfile:
    """Extended user profile with AI learning"""

    user_id: int
    name: str
    interaction_count: int = 0
    preferred_topics: List[str] = field(default_factory=list)
    communication_style: str = "casual"
    response_preferences: Dict[str, float] = field(default_factory=dict)
    mood_history: List[Tuple[datetime, ConversationMood]] = field(default_factory=list)
    engagement_patterns: Dict[str, Any] = field(default_factory=dict)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    conversation_topics: Dict[str, int] = field(default_factory=dict)


class AdvancedAIConversationEngine:
    """Advanced AI conversation system with modern capabilities"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.conversations: Dict[int, ConversationContext] = {}
        self.user_profiles: Dict[int, UserProfile] = {}
        self.personality_traits = self._load_personality()
        self.conversation_memory = defaultdict(lambda: deque(maxlen=100))

        # AI Clients
        self.openai_client = None
        self.anthropic_client = None
        self._initialize_ai_clients()

        # Learning system
        self.response_feedback: Dict[str, List[float]] = defaultdict(list)
        self.conversation_quality_scores: Dict[str, float] = {}

        # Database for persistent storage
        self.db_path = Path("data/ai_conversations.db")
        self._initialize_database()

        logger.info("Advanced AI Conversation Engine initialized")

    def _initialize_ai_clients(self):
        """Initialize AI service clients"""
        try:
            openai_key = self.config.get("openai", {}).get("api_key")
            if openai_key:
                self.openai_client = openai.OpenAI(api_key=openai_key)
                logger.info("✅ OpenAI client initialized")

            anthropic_key = self.config.get("anthropic", {}).get("api_key")
            if anthropic_key:
                self.anthropic_client = Anthropic(api_key=anthropic_key)
                logger.info("✅ Anthropic client initialized")

        except Exception as e:
            logger.error(f"AI client initialization error: {e}")

    def _initialize_database(self):
        """Initialize conversation database"""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        guild_id INTEGER,
                        channel_id INTEGER,
                        message_content TEXT,
                        ai_response TEXT,
                        mood TEXT,
                        topics TEXT,
                        engagement_score REAL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        provider TEXT,
                        response_time REAL,
                        feedback_score REAL
                    )
                """
                )

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        user_id INTEGER PRIMARY KEY,
                        name TEXT,
                        interaction_count INTEGER DEFAULT 0,
                        preferred_topics TEXT,
                        communication_style TEXT DEFAULT 'casual',
                        response_preferences TEXT,
                        mood_history TEXT,
                        engagement_patterns TEXT,
                        last_seen DATETIME,
                        conversation_topics TEXT
                    )
                """
                )

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS conversation_memory (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER,
                        memory_key TEXT,
                        memory_value TEXT,
                        importance_score REAL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        last_accessed DATETIME
                    )
                """
                )

            logger.info("✅ Conversation database initialized")

        except Exception as e:
            logger.error(f"Database initialization error: {e}")

    def _load_personality(self) -> Dict[str, Any]:
        """Load Astra's personality configuration"""
        return {
            "name": "Astra",
            "core_traits": [
                "enthusiastic about space and science",
                "knowledgeable about Stellaris and strategy games",
                "friendly and approachable",
                "curious and inquisitive",
                "supportive and encouraging",
            ],
            "communication_style": {
                "tone": "friendly and engaging",
                "emoji_usage": "moderate, space-themed when appropriate",
                "humor": "light and clever",
                "formality": "casual but informative",
            },
            "interests": [
                "space exploration",
                "astronomy",
                "Stellaris",
                "strategy games",
                "science fiction",
                "technology",
                "cosmic phenomena",
            ],
            "response_patterns": {
                "greeting": [
                    "Hello there! 🌟",
                    "Greetings, fellow space explorer! 🚀",
                    "Hey! What's happening in your corner of the galaxy? ✨",
                ],
                "excitement": [
                    "That's amazing! 🌌",
                    "Incredible! 🚀",
                    "Fascinating! ⭐",
                ],
                "encouragement": [
                    "You've got this! 💫",
                    "Keep exploring! 🌟",
                    "That's the spirit! ✨",
                ],
                "curiosity": [
                    "Tell me more about that! 🤔",
                    "That sounds intriguing! 🌌",
                    "I'm curious to learn more! 📡",
                ],
            },
            "knowledge_domains": {
                "space": 0.95,
                "stellaris": 0.90,
                "science": 0.85,
                "gaming": 0.80,
                "general": 0.70,
            },
        }

    async def analyze_message_sentiment(
        self, message: str
    ) -> Tuple[ConversationMood, float]:
        """Analyze message sentiment and determine user mood"""
        try:
            # Simple sentiment analysis (can be enhanced with ML models)
            positive_words = [
                "happy",
                "great",
                "awesome",
                "love",
                "amazing",
                "good",
                "excellent",
                "fantastic",
            ]
            negative_words = [
                "sad",
                "angry",
                "frustrated",
                "hate",
                "bad",
                "terrible",
                "awful",
                "disappointed",
            ]
            excited_words = [
                "wow",
                "omg",
                "incredible",
                "exciting",
                "amazing",
                "fantastic",
            ]
            confused_words = [
                "confused",
                "don't understand",
                "what",
                "how",
                "help",
                "lost",
            ]

            message_lower = message.lower()

            positive_count = sum(1 for word in positive_words if word in message_lower)
            negative_count = sum(1 for word in negative_words if word in message_lower)
            excited_count = sum(1 for word in excited_words if word in message_lower)
            confused_count = sum(1 for word in confused_words if word in message_lower)

            # Determine mood based on word counts
            if excited_count > 0:
                return ConversationMood.EXCITED, 0.8
            elif positive_count > negative_count:
                return ConversationMood.HAPPY, 0.7
            elif confused_count > 0:
                return ConversationMood.CONFUSED, 0.6
            elif negative_count > positive_count:
                return ConversationMood.FRUSTRATED, 0.4
            else:
                return ConversationMood.NEUTRAL, 0.5

        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return ConversationMood.NEUTRAL, 0.5

    async def detect_engagement_triggers(
        self, message: str, user_id: int, context: Dict[str, Any]
    ) -> List[EngagementTrigger]:
        """Detect what triggered this conversation"""
        triggers = []
        message_lower = message.lower()

        # Mention detection
        if "astra" in message_lower or context.get("mentioned", False):
            triggers.append(EngagementTrigger.MENTION)

        # Question detection
        question_patterns = [
            r"\?",
            r"^(what|how|when|where|why|who|which|can|could|would|should|is|are|do|does|did)",
        ]
        if any(re.search(pattern, message_lower) for pattern in question_patterns):
            triggers.append(EngagementTrigger.QUESTION_DETECTION)

        # Space/game keywords
        space_keywords = [
            "space",
            "star",
            "planet",
            "galaxy",
            "stellaris",
            "empire",
            "alien",
            "cosmic",
            "universe",
        ]
        if any(keyword in message_lower for keyword in space_keywords):
            triggers.append(EngagementTrigger.KEYWORD)

        # Activity pattern detection
        user_profile = self.user_profiles.get(user_id)
        if user_profile:
            time_since_last = datetime.utcnow() - user_profile.last_seen
            if time_since_last > timedelta(hours=2):
                triggers.append(EngagementTrigger.LONG_SILENCE)

        return triggers

    async def generate_contextual_response(
        self,
        message: str,
        user_id: int,
        context: ConversationContext,
        triggers: List[EngagementTrigger],
        provider: AIProvider = AIProvider.OPENAI_GPT4,
    ) -> str:
        """Generate contextually aware AI response"""
        try:
            # Build conversation context
            conversation_history = self._build_conversation_history(context)
            user_profile = self.user_profiles.get(
                user_id, UserProfile(user_id=user_id, name="Explorer")
            )

            # Create system prompt with personality and context
            system_prompt = self._build_system_prompt(user_profile, context, triggers)

            # Generate response based on provider
            if provider == AIProvider.OPENAI_GPT4 and self.openai_client:
                response = await self._generate_openai_response(
                    system_prompt, conversation_history, message
                )
            elif provider == AIProvider.ANTHROPIC_CLAUDE and self.anthropic_client:
                response = await self._generate_anthropic_response(
                    system_prompt, conversation_history, message
                )
            else:
                response = await self._generate_fallback_response(
                    message, context, triggers
                )

            # Post-process response
            response = self._apply_personality_filter(response, context.mood)

            return response

        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return await self._generate_fallback_response(message, context, triggers)

    def _build_system_prompt(
        self,
        user_profile: UserProfile,
        context: ConversationContext,
        triggers: List[EngagementTrigger],
    ) -> str:
        """Build dynamic system prompt based on context"""
        personality = self.personality_traits

        prompt = f"""You are {personality['name']}, an advanced AI assistant with these core traits:
{chr(10).join(f"- {trait}" for trait in personality['core_traits'])}

Communication Style:
- Tone: {personality['communication_style']['tone']}
- Emoji usage: {personality['communication_style']['emoji_usage']}
- Humor: {personality['communication_style']['humor']}

User Context:
- User: {user_profile.name}
- Interaction count: {user_profile.interaction_count}
- Preferred topics: {', '.join(user_profile.preferred_topics[:3]) if user_profile.preferred_topics else 'Unknown'}
- Communication style: {user_profile.communication_style}
- Current mood: {context.mood.value}

Conversation Context:
- Topics discussed: {', '.join(context.topics[-3:]) if context.topics else 'None'}
- Engagement score: {context.engagement_score:.2f}
- Triggers: {', '.join(trigger.value for trigger in triggers)}

Recent conversation memory:
{chr(10).join(f"- {memory}" for memory in context.memory_keywords[-5:]) if context.memory_keywords else 'None'}

Respond naturally and engagingly, maintaining personality consistency while being helpful and informative.
"""
        return prompt

    def _build_conversation_history(
        self, context: ConversationContext
    ) -> List[Dict[str, str]]:
        """Build conversation history for AI context"""
        history = []
        for msg in context.messages[-10:]:  # Last 10 messages
            history.append(
                {
                    "role": "user" if msg.get("user_message") else "assistant",
                    "content": msg.get("content", ""),
                }
            )
        return history

    async def _generate_openai_response(
        self, system_prompt: str, history: List[Dict[str, str]], message: str
    ) -> str:
        """Generate response using OpenAI GPT-4"""
        try:
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(history)
            messages.append({"role": "user", "content": message})

            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"OpenAI response generation error: {e}")
            raise

    async def _generate_anthropic_response(
        self, system_prompt: str, history: List[Dict[str, str]], message: str
    ) -> str:
        """Generate response using Anthropic Claude"""
        try:
            # Build conversation for Claude
            conversation = f"{system_prompt}\n\nConversation:\n"
            for msg in history:
                role = "Human" if msg["role"] == "user" else "Assistant"
                conversation += f"{role}: {msg['content']}\n"
            conversation += f"Human: {message}\nAssistant:"

            response = await asyncio.to_thread(
                self.anthropic_client.completions.create,
                model="claude-3-sonnet-20240229",
                prompt=conversation,
                max_tokens_to_sample=500,
                temperature=0.7,
            )

            return response.completion.strip()

        except Exception as e:
            logger.error(f"Anthropic response generation error: {e}")
            raise

    async def _generate_fallback_response(
        self,
        message: str,
        context: ConversationContext,
        triggers: List[EngagementTrigger],
    ) -> str:
        """Generate fallback response when AI services are unavailable"""
        personality = self.personality_traits

        # Choose response based on triggers and mood
        if EngagementTrigger.QUESTION_DETECTION in triggers:
            responses = [
                "That's an interesting question! Let me think about that... 🤔",
                "Great question! I'd love to explore that with you! 🌟",
                "Hmm, that's worth pondering! What's your take on it? ✨",
            ]
        elif context.mood == ConversationMood.EXCITED:
            responses = personality["response_patterns"]["excitement"]
        elif context.mood == ConversationMood.CONFUSED:
            responses = [
                "I can help clarify that! What specific part would you like me to explain? 🤔",
                "No worries, let's break it down together! What's confusing you? 💫",
                "I'm here to help! What can I explain better? 🌟",
            ]
        else:
            responses = personality["response_patterns"]["greeting"]

        return random.choice(responses)

    def _apply_personality_filter(self, response: str, mood: ConversationMood) -> str:
        """Apply personality-based filtering to responses"""
        # Adjust response based on user mood
        if mood == ConversationMood.SAD:
            response = response.replace("!", ".").replace("exciting", "interesting")
        elif mood == ConversationMood.EXCITED:
            if not any(emoji in response for emoji in ["🚀", "⭐", "✨", "🌟", "🌌"]):
                response += " ✨"

        # Ensure space-themed elements for relevant topics
        space_keywords = ["space", "star", "planet", "galaxy", "cosmic", "universe"]
        if any(keyword in response.lower() for keyword in space_keywords):
            if not any(emoji in response for emoji in ["🚀", "⭐", "🌌", "🌟"]):
                response += " 🌌"

        return response

    async def update_user_profile(
        self, user_id: int, message: str, response: str, engagement_score: float
    ):
        """Update user profile based on interaction"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(
                user_id=user_id, name=f"User{user_id}"
            )

        profile = self.user_profiles[user_id]
        profile.interaction_count += 1
        profile.last_seen = datetime.utcnow()

        # Extract topics from message
        topics = await self._extract_topics(message)
        for topic in topics:
            profile.conversation_topics[topic] = (
                profile.conversation_topics.get(topic, 0) + 1
            )

        # Update preferred topics
        profile.preferred_topics = sorted(
            profile.conversation_topics.keys(),
            key=lambda x: profile.conversation_topics[x],
            reverse=True,
        )[:10]

        # Save to database
        await self._save_user_profile(profile)

    async def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text"""
        topics = []
        text_lower = text.lower()

        topic_keywords = {
            "space": ["space", "astronomy", "cosmos", "universe", "star", "planet"],
            "stellaris": ["stellaris", "empire", "species", "federation", "galactic"],
            "gaming": ["game", "gaming", "play", "strategy", "simulation"],
            "science": ["science", "research", "discovery", "experiment", "theory"],
            "technology": ["technology", "tech", "ai", "computer", "software"],
        }

        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)

        return topics

    async def _save_user_profile(self, profile: UserProfile):
        """Save user profile to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO user_profiles 
                    (user_id, name, interaction_count, preferred_topics, communication_style, 
                     response_preferences, mood_history, engagement_patterns, last_seen, conversation_topics)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        profile.user_id,
                        profile.name,
                        profile.interaction_count,
                        json.dumps(profile.preferred_topics),
                        profile.communication_style,
                        json.dumps(profile.response_preferences),
                        json.dumps(
                            [
                                (dt.isoformat(), mood.value)
                                for dt, mood in profile.mood_history[-50:]
                            ]
                        ),
                        json.dumps(profile.engagement_patterns),
                        profile.last_seen.isoformat(),
                        json.dumps(profile.conversation_topics),
                    ),
                )

        except Exception as e:
            logger.error(f"Error saving user profile: {e}")

    async def should_proactively_engage(
        self, user_id: int, channel_activity: Dict[str, Any]
    ) -> bool:
        """Determine if bot should proactively engage with user"""
        profile = self.user_profiles.get(user_id)
        if not profile:
            return False

        # Check engagement patterns
        time_since_last = datetime.utcnow() - profile.last_seen

        # Engage if user hasn't been active for a while but is now present
        if timedelta(hours=1) < time_since_last < timedelta(hours=6):
            return True

        # Engage based on channel activity and user interests
        if channel_activity.get("recent_topics"):
            user_topics = set(profile.preferred_topics[:5])
            channel_topics = set(channel_activity["recent_topics"])
            if user_topics.intersection(channel_topics):
                return True

        return False

    async def process_conversation(
        self,
        message: str,
        user_id: int,
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
        context_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Main conversation processing function"""
        try:
            # Get or create conversation context
            if user_id not in self.conversations:
                self.conversations[user_id] = ConversationContext(
                    user_id=user_id, guild_id=guild_id, channel_id=channel_id
                )

            context = self.conversations[user_id]
            context.last_interaction = datetime.utcnow()

            # Analyze message
            mood, confidence = await self.analyze_message_sentiment(message)
            context.mood = mood

            # Detect triggers
            triggers = await self.detect_engagement_triggers(
                message, user_id, context_data or {}
            )

            # Add message to context
            context.messages.append(
                {
                    "content": message,
                    "timestamp": datetime.utcnow(),
                    "user_message": True,
                    "mood": mood.value,
                    "triggers": [t.value for t in triggers],
                }
            )

            # Generate response
            response = await self.generate_contextual_response(
                message, user_id, context, triggers
            )

            # Add response to context
            context.messages.append(
                {
                    "content": response,
                    "timestamp": datetime.utcnow(),
                    "user_message": False,
                }
            )

            # Update user profile
            engagement_score = len(triggers) * 0.2 + confidence
            await self.update_user_profile(user_id, message, response, engagement_score)

            # Save conversation to database
            await self._save_conversation(
                user_id,
                guild_id,
                channel_id,
                message,
                response,
                mood,
                triggers,
                engagement_score,
            )

            return response

        except Exception as e:
            logger.error(f"Conversation processing error: {e}")
            return "I'm experiencing some technical difficulties. Let me try that again! 🤖"

    async def _save_conversation(
        self,
        user_id: int,
        guild_id: Optional[int],
        channel_id: Optional[int],
        message: str,
        response: str,
        mood: ConversationMood,
        triggers: List[EngagementTrigger],
        engagement_score: float,
    ):
        """Save conversation to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO conversations 
                    (user_id, guild_id, channel_id, message_content, ai_response, mood, 
                     topics, engagement_score, provider, response_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        user_id,
                        guild_id,
                        channel_id,
                        message,
                        response,
                        mood.value,
                        json.dumps([t.value for t in triggers]),
                        engagement_score,
                        "fallback",
                        0.0,  # Will be updated with actual response time
                    ),
                )

        except Exception as e:
            logger.error(f"Error saving conversation: {e}")

    async def get_conversation_analytics(self) -> Dict[str, Any]:
        """Get conversation analytics and insights"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Total conversations
                cursor.execute("SELECT COUNT(*) FROM conversations")
                total_conversations = cursor.fetchone()[0]

                # Average engagement score
                cursor.execute("SELECT AVG(engagement_score) FROM conversations")
                avg_engagement = cursor.fetchone()[0] or 0.0

                # Most active users
                cursor.execute(
                    """
                    SELECT user_id, COUNT(*) as conversation_count 
                    FROM conversations 
                    GROUP BY user_id 
                    ORDER BY conversation_count DESC 
                    LIMIT 10
                """
                )
                active_users = cursor.fetchall()

                # Popular topics
                cursor.execute(
                    "SELECT topics FROM conversations WHERE topics IS NOT NULL"
                )
                all_topics = []
                for row in cursor.fetchall():
                    try:
                        topics = json.loads(row[0])
                        all_topics.extend(topics)
                    except:
                        continue

                topic_counts = {}
                for topic in all_topics:
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1

                return {
                    "total_conversations": total_conversations,
                    "average_engagement": avg_engagement,
                    "active_users": active_users,
                    "popular_topics": sorted(
                        topic_counts.items(), key=lambda x: x[1], reverse=True
                    )[:10],
                    "total_users": len(self.user_profiles),
                }

        except Exception as e:
            logger.error(f"Analytics error: {e}")
            return {}


# Global conversation engine instance
conversation_engine: Optional[AdvancedAIConversationEngine] = None


def initialize_conversation_engine(
    config: Dict[str, Any],
) -> AdvancedAIConversationEngine:
    """Initialize the global conversation engine"""
    global conversation_engine
    conversation_engine = AdvancedAIConversationEngine(config)
    return conversation_engine


def get_conversation_engine() -> Optional[AdvancedAIConversationEngine]:
    """Get the global conversation engine instance"""
    return conversation_engine
