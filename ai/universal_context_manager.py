"""
Universal Context Manager for Astra Bot
Handles conversation context understanding, humor detection, and natural response triggers
"""

import asyncio
import logging
import random
import re
import json
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta, timezone
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
import sqlite3
from pathlib import Path

logger = logging.getLogger("astra.universal_context")


class ConversationTone(Enum):
    """Conversation tone detection"""

    HUMOROUS = "humorous"
    SERIOUS = "serious"
    CASUAL = "casual"
    TECHNICAL = "technical"
    EMOTIONAL = "emotional"
    QUESTIONING = "questioning"
    EXCITED = "excited"
    FRUSTRATED = "frustrated"
    SUPPORTIVE = "supportive"


class ResponseTrigger(Enum):
    """Types of response triggers"""

    HUMOR_DETECTED = "humor_detected"
    QUESTION_ASKED = "question_asked"
    HELP_NEEDED = "help_needed"
    TOPIC_MATCH = "topic_match"
    EMOTIONAL_SUPPORT = "emotional_support"
    CONVERSATION_FLOW = "conversation_flow"
    RANDOM_ENGAGEMENT = "random_engagement"
    GREETING = "greeting"
    CELEBRATION = "celebration"


@dataclass
class MessageContext:
    """Context information for a message"""

    user_id: int
    content: str
    tone: ConversationTone
    humor_score: float = 0.0
    emotional_intensity: float = 0.5
    topics: List[str] = field(default_factory=list)
    response_triggers: List[ResponseTrigger] = field(default_factory=list)
    response_probability: float = 0.0
    suggested_response_style: str = "casual"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class UserConversationState:
    """Track user's conversation state"""

    user_id: int
    recent_messages: deque = field(default_factory=lambda: deque(maxlen=15))
    conversation_themes: List[str] = field(default_factory=list)
    humor_frequency: float = 0.0
    typical_response_length: int = 50
    preferred_topics: Dict[str, float] = field(default_factory=dict)
    engagement_level: float = 0.5
    last_interaction: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    conversation_quality: float = 0.5


class HumorDetector:
    """Advanced humor detection with multiple patterns"""

    def __init__(self):
        self.humor_patterns = {
            "sarcasm": [
                r"oh (really|sure|great|wonderful)",
                r"wow.*so.*",
                r"thanks (a lot|so much)",
                r"(perfect|fantastic|amazing).*\.",
                r"because that's exactly what",
            ],
            "jokes": [
                r"why did.*",
                r"knock knock",
                r"what do you call.*",
                r".*walks into a bar",
                r"pun intended",
            ],
            "playful": [
                r"haha|hehe|lol|lmao|rofl",
                r"😂|🤣|😆|😄|😁",
                r"that's funny",
                r"made me laugh",
                r"good one",
            ],
            "wordplay": [
                r"pun|punny",
                r"play on words",
                r"clever.*word",
                r"double meaning",
            ],
            "memes": [
                r"among us|sus|impostor",
                r"poggers|pog|pogchamp",
                r"based|cringe",
                r"big brain|galaxy brain",
                r"this is the way",
                r"stonks|hodl",
            ],
        }

        self.humor_indicators = [
            "!",
            "?!",
            "lol",
            "haha",
            "😂",
            "🤣",
            "😆",
            "xd",
            "lmao",
        ]

    def detect_humor(self, text: str) -> Tuple[bool, float, str]:
        """
        Detect humor in text
        Returns: (is_humorous, humor_score, humor_type)
        """
        text_lower = text.lower()
        humor_score = 0.0
        humor_types = []

        # Check patterns
        for humor_type, patterns in self.humor_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    humor_score += 0.3
                    humor_types.append(humor_type)

        # Check indicators
        for indicator in self.humor_indicators:
            if indicator in text_lower:
                humor_score += 0.1

        # Punctuation analysis
        exclamation_count = text.count("!")
        if exclamation_count > 1:
            humor_score += min(0.2, exclamation_count * 0.05)

        # Emoji analysis
        emoji_count = len(re.findall(r"[😀-🙏]", text))
        if emoji_count > 0:
            humor_score += min(0.3, emoji_count * 0.1)

        # Caps analysis (playful caps)
        caps_ratio = sum(1 for c in text if c.isupper()) / max(1, len(text))
        if 0.3 < caps_ratio < 0.8:  # Partial caps (playful)
            humor_score += 0.1

        humor_score = min(1.0, humor_score)
        main_humor_type = humor_types[0] if humor_types else "general"

        return humor_score > 0.2, humor_score, main_humor_type


class ConversationAnalyzer:
    """Analyze conversation context and determine response strategies"""

    def __init__(self):
        self.topic_keywords = {
            "stellaris": [
                "stellaris",
                "empire",
                "species",
                "galactic",
                "federation",
                "ethics",
                "ascension",
                "hyperlane",
                "paradox",
                "strategy",
                "expansion",
                "diplomacy",
            ],
            "space": [
                "space",
                "cosmos",
                "universe",
                "galaxy",
                "star",
                "planet",
                "astronomy",
                "nebula",
                "black hole",
                "spacecraft",
                "rocket",
                "nasa",
                "spacex",
            ],
            "gaming": [
                "game",
                "gaming",
                "play",
                "player",
                "level",
                "achievement",
                "strategy",
                "multiplayer",
                "campaign",
                "mod",
                "dlc",
                "steam",
                "pc gaming",
            ],
            "technology": [
                "ai",
                "artificial intelligence",
                "machine learning",
                "robot",
                "tech",
                "computer",
                "software",
                "programming",
                "algorithm",
                "quantum",
            ],
            "science": [
                "science",
                "research",
                "discovery",
                "experiment",
                "theory",
                "physics",
                "chemistry",
                "biology",
                "mathematics",
                "scientific method",
            ],
            "help": [
                "help",
                "assistance",
                "support",
                "explain",
                "how to",
                "tutorial",
                "guide",
                "confused",
                "problem",
                "issue",
                "stuck",
                "error",
            ],
            "social": [
                "friend",
                "community",
                "together",
                "team",
                "group",
                "chat",
                "talk",
                "conversation",
                "discuss",
                "share",
                "opinion",
                "thoughts",
            ],
        }

        self.greeting_patterns = [
            r"^(hi|hello|hey|good morning|good evening|sup|what\'s up)",
            r"(morning|evening|afternoon) everyone",
            r"^greetings",
            r"^yo\b",
        ]

        self.question_patterns = [
            r"\?",
            r"^(what|how|when|where|why|who|which|can|could|would|should|is|are|will|do|does)\b",
            r"\b(anyone know|somebody know|does anyone|can someone)",
            r"\bhelp\b.*\?",
            r"\bwonder\b",
        ]

        self.celebration_patterns = [
            r"\b(yay|woohoo|awesome|amazing|incredible|fantastic|great|excellent)\b",
            r"\b(success|achievement|won|victory|completed|finished|done)\b",
            r"\b(celebrate|party|congratulations|congrats)\b",
        ]

        self.emotion_patterns = {
            "excited": [
                r"\b(excited|thrilled|pumped|hyped|stoked)\b",
                r"!{2,}",
                r"\b(can\'t wait|so ready|looking forward)\b",
            ],
            "frustrated": [
                r"\b(frustrated|annoyed|irritated|ugh|argh)\b",
                r"\b(this sucks|so annoying|hate this)\b",
                r"\b(why won\'t|doesn\'t work|broken)\b",
            ],
            "sad": [
                r"\b(sad|depressed|down|upset|disappointed)\b",
                r"\b(feel bad|feeling down|not good)\b",
                r":[\(\[]|😢|😞|😔",
            ],
            "confused": [
                r"\b(confused|lost|don\'t understand|unclear)\b",
                r"\b(what does.*mean|how does.*work)\b",
                r"\?\?\?+",
            ],
        }

    def analyze_message(
        self, text: str, user_id: int, channel_context: Dict = None
    ) -> MessageContext:
        """Analyze a message and return context information"""
        context = MessageContext(user_id=user_id, content=text)

        # Detect tone
        context.tone = self._detect_tone(text)

        # Detect humor
        is_humorous, humor_score, humor_type = HumorDetector().detect_humor(text)
        context.humor_score = humor_score
        if is_humorous:
            context.response_triggers.append(ResponseTrigger.HUMOR_DETECTED)

        # Extract topics
        context.topics = self._extract_topics(text)

        # Detect emotional intensity
        context.emotional_intensity = self._detect_emotional_intensity(text)

        # Determine response triggers
        context.response_triggers.extend(self._determine_response_triggers(text))

        # Calculate response probability
        context.response_probability = self._calculate_response_probability(context)

        # Suggest response style
        context.suggested_response_style = self._suggest_response_style(context)

        return context

    def _detect_tone(self, text: str) -> ConversationTone:
        """Detect the overall tone of the message"""
        text_lower = text.lower()

        # Check for humor first
        is_humorous, _, _ = HumorDetector().detect_humor(text)
        if is_humorous:
            return ConversationTone.HUMOROUS

        # Check for questions
        if any(re.search(pattern, text_lower) for pattern in self.question_patterns):
            return ConversationTone.QUESTIONING

        # Check for emotional content
        for emotion, patterns in self.emotion_patterns.items():
            if any(re.search(pattern, text_lower) for pattern in patterns):
                if emotion in ["excited"]:
                    return ConversationTone.EXCITED
                elif emotion in ["frustrated", "sad"]:
                    return ConversationTone.EMOTIONAL

        # Check for technical content
        tech_indicators = [
            "function",
            "algorithm",
            "code",
            "syntax",
            "error",
            "debug",
            "compile",
        ]
        if any(word in text_lower for word in tech_indicators):
            return ConversationTone.TECHNICAL

        # Check for casual indicators
        casual_indicators = ["lol", "haha", "yeah", "nah", "gonna", "wanna", "sup"]
        if any(word in text_lower for word in casual_indicators):
            return ConversationTone.CASUAL

        # Default to serious if formal language or longer explanations
        if len(text) > 100 and not any(
            pattern in text_lower for pattern in casual_indicators
        ):
            return ConversationTone.SERIOUS

        return ConversationTone.CASUAL

    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from the message"""
        text_lower = text.lower()
        found_topics = []

        for topic, keywords in self.topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                found_topics.append(topic)

        return found_topics

    def _detect_emotional_intensity(self, text: str) -> float:
        """Detect emotional intensity (0.0 to 1.0)"""
        intensity = 0.5  # baseline

        # Punctuation indicators
        exclamation_count = text.count("!")
        intensity += min(0.3, exclamation_count * 0.1)

        question_count = text.count("?")
        if question_count > 1:
            intensity += 0.1

        # Caps analysis
        caps_ratio = sum(1 for c in text if c.isupper()) / max(1, len(text))
        if caps_ratio > 0.5:
            intensity += 0.2

        # Emotional words
        high_emotion_words = [
            "amazing",
            "incredible",
            "fantastic",
            "terrible",
            "awful",
            "love",
            "hate",
            "excited",
            "furious",
            "devastated",
        ]

        for word in high_emotion_words:
            if word in text.lower():
                intensity += 0.15

        return min(1.0, intensity)

    def _determine_response_triggers(self, text: str) -> List[ResponseTrigger]:
        """Determine what should trigger a response"""
        text_lower = text.lower()
        triggers = []

        # Questions
        if any(re.search(pattern, text_lower) for pattern in self.question_patterns):
            triggers.append(ResponseTrigger.QUESTION_ASKED)

        # Help requests
        help_keywords = ["help", "assist", "support", "confused", "stuck", "problem"]
        if any(keyword in text_lower for keyword in help_keywords):
            triggers.append(ResponseTrigger.HELP_NEEDED)

        # Greetings
        if any(re.search(pattern, text_lower) for pattern in self.greeting_patterns):
            triggers.append(ResponseTrigger.GREETING)

        # Celebrations
        if any(re.search(pattern, text_lower) for pattern in self.celebration_patterns):
            triggers.append(ResponseTrigger.CELEBRATION)

        # Topic matches
        if self._extract_topics(text):
            triggers.append(ResponseTrigger.TOPIC_MATCH)

        # Emotional support
        for emotion_patterns in self.emotion_patterns.values():
            if any(re.search(pattern, text_lower) for pattern in emotion_patterns):
                triggers.append(ResponseTrigger.EMOTIONAL_SUPPORT)
                break

        return triggers

    def _calculate_response_probability(self, context: MessageContext) -> float:
        """Calculate probability that bot should respond (0.0 to 1.0)"""
        probability = 0.0

        # Base trigger probabilities
        trigger_weights = {
            ResponseTrigger.QUESTION_ASKED: 0.9,
            ResponseTrigger.HELP_NEEDED: 0.85,
            ResponseTrigger.HUMOR_DETECTED: 0.4,
            ResponseTrigger.GREETING: 0.6,
            ResponseTrigger.CELEBRATION: 0.5,
            ResponseTrigger.EMOTIONAL_SUPPORT: 0.7,
            ResponseTrigger.TOPIC_MATCH: 0.3,
        }

        # Calculate max probability from triggers
        for trigger in context.response_triggers:
            probability = max(probability, trigger_weights.get(trigger, 0.1))

        # Boost probability based on context
        if context.humor_score > 0.5:
            probability += 0.2

        if context.emotional_intensity > 0.7:
            probability += 0.15

        if len(context.topics) > 1:  # Multiple topics = more engagement
            probability += 0.1

        # Tone adjustments
        tone_modifiers = {
            ConversationTone.QUESTIONING: 0.2,
            ConversationTone.EMOTIONAL: 0.15,
            ConversationTone.EXCITED: 0.1,
            ConversationTone.HUMOROUS: 0.1,
        }

        probability += tone_modifiers.get(context.tone, 0.0)

        return min(1.0, probability)

    def _suggest_response_style(self, context: MessageContext) -> str:
        """Suggest appropriate response style"""
        if context.humor_score > 0.4:
            return "humorous"

        if context.tone == ConversationTone.TECHNICAL:
            return "informative"

        if context.tone == ConversationTone.EMOTIONAL:
            return "supportive"

        if context.tone == ConversationTone.EXCITED:
            return "enthusiastic"

        if ResponseTrigger.HELP_NEEDED in context.response_triggers:
            return "helpful"

        if ResponseTrigger.CELEBRATION in context.response_triggers:
            return "celebratory"

        return "casual"


class UniversalContextManager:
    """Main context manager for the bot"""

    def __init__(self, bot=None):
        self.bot = bot
        self.analyzer = ConversationAnalyzer()
        self.humor_detector = HumorDetector()

        # User state tracking
        self.user_states: Dict[int, UserConversationState] = {}
        self.channel_contexts: Dict[int, Dict[str, Any]] = {}

        # Response rate limiting
        self.last_responses: Dict[int, datetime] = {}  # user_id -> last response time
        self.channel_last_response: Dict[int, datetime] = (
            {}
        )  # channel_id -> last response time

        # Configuration
        self.min_response_interval = timedelta(
            seconds=10
        )  # Min time between responses to same user
        self.channel_response_interval = timedelta(
            seconds=30
        )  # Min time between responses in same channel
        self.max_responses_per_hour = 20  # Max responses per hour per channel

        # Database setup
        self.db_path = Path("data/context_manager.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._setup_database()

        logger.info("Universal Context Manager initialized")

    def _setup_database(self):
        """Setup database for context tracking"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS message_contexts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        channel_id INTEGER NOT NULL,
                        guild_id INTEGER,
                        content TEXT NOT NULL,
                        tone TEXT,
                        humor_score REAL,
                        emotional_intensity REAL,
                        topics TEXT,
                        response_triggers TEXT,
                        response_probability REAL,
                        bot_responded BOOLEAN DEFAULT 0,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS user_conversation_states (
                        user_id INTEGER PRIMARY KEY,
                        humor_frequency REAL DEFAULT 0.0,
                        typical_response_length INTEGER DEFAULT 50,
                        preferred_topics TEXT,
                        engagement_level REAL DEFAULT 0.5,
                        conversation_quality REAL DEFAULT 0.5,
                        last_interaction TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Create indexes
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_message_contexts_user_id ON message_contexts (user_id)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_message_contexts_timestamp ON message_contexts (timestamp)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_message_contexts_channel_id ON message_contexts (channel_id)"
                )

                conn.commit()
                logger.info("Context manager database initialized")

        except Exception as e:
            logger.error(f"Database setup error: {e}")

    async def analyze_message(
        self,
        message_content: str,
        user_id: int,
        channel_id: int = None,
        guild_id: int = None,
        user_display_name: str = None,
    ) -> MessageContext:
        """Analyze a message and return context"""

        # Get or create user state
        if user_id not in self.user_states:
            self.user_states[user_id] = UserConversationState(user_id=user_id)

        user_state = self.user_states[user_id]

        # Analyze the message
        context = self.analyzer.analyze_message(message_content, user_id)

        # Update user state
        user_state.recent_messages.append(
            {
                "content": message_content,
                "timestamp": datetime.now(timezone.utc),
                "topics": context.topics,
                "humor_score": context.humor_score,
            }
        )

        # Update user patterns
        await self._update_user_patterns(user_state, context)

        # Store context in database
        await self._store_context(context, channel_id, guild_id)

        return context

    async def should_respond(
        self, context: MessageContext, channel_id: int = None, guild_id: int = None
    ) -> Tuple[bool, str]:
        """
        Determine if the bot should respond to a message
        Returns: (should_respond, reason)
        """

        # Check rate limiting
        current_time = datetime.now(timezone.utc)

        # User-specific rate limiting
        if context.user_id in self.last_responses:
            time_since_last = current_time - self.last_responses[context.user_id]
            if time_since_last < self.min_response_interval:
                return False, "user_rate_limit"

        # Channel-specific rate limiting
        if channel_id and channel_id in self.channel_last_response:
            time_since_last = current_time - self.channel_last_response[channel_id]
            if time_since_last < self.channel_response_interval:
                return False, "channel_rate_limit"

        # Always respond to high-priority triggers
        high_priority_triggers = [
            ResponseTrigger.QUESTION_ASKED,
            ResponseTrigger.HELP_NEEDED,
        ]

        if any(
            trigger in context.response_triggers for trigger in high_priority_triggers
        ):
            return True, f"high_priority_trigger"

        # Use probability for other cases
        import random

        # Adjust probability based on user engagement
        user_state = self.user_states.get(context.user_id)
        adjusted_probability = context.response_probability

        if user_state:
            # Boost probability for engaged users
            if user_state.engagement_level > 0.7:
                adjusted_probability *= 1.2
            elif user_state.engagement_level < 0.3:
                adjusted_probability *= 0.8

        # Random check against probability
        if random.random() < adjusted_probability:
            return True, f"probability_trigger_{adjusted_probability:.2f}"

        return False, "probability_too_low"

    async def get_response_context(self, context: MessageContext) -> Dict[str, Any]:
        """Get context information for generating a response"""
        user_state = self.user_states.get(context.user_id)

        response_context = {
            "message_context": context,
            "suggested_style": context.suggested_response_style,
            "humor_detected": context.humor_score > 0.3,
            "humor_type": "general",  # Could be enhanced
            "emotional_intensity": context.emotional_intensity,
            "topics": context.topics,
            "response_triggers": [
                trigger.value for trigger in context.response_triggers
            ],
            "conversation_history": [],
            "user_preferences": {},
        }

        if user_state:
            # Add conversation history
            response_context["conversation_history"] = list(user_state.recent_messages)[
                -5:
            ]

            # Add user preferences
            response_context["user_preferences"] = {
                "humor_frequency": user_state.humor_frequency,
                "preferred_topics": user_state.preferred_topics,
                "typical_response_length": user_state.typical_response_length,
                "engagement_level": user_state.engagement_level,
            }

        return response_context

    async def mark_response_sent(self, context: MessageContext, channel_id: int = None):
        """Mark that a response was sent"""
        current_time = datetime.now(timezone.utc)

        # Update timing records
        self.last_responses[context.user_id] = current_time
        if channel_id:
            self.channel_last_response[channel_id] = current_time

        # Update database
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE message_contexts 
                    SET bot_responded = 1 
                    WHERE user_id = ? AND content = ? AND timestamp = ?
                """,
                    (context.user_id, context.content, context.timestamp.isoformat()),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error marking response in database: {e}")

    async def _update_user_patterns(
        self, user_state: UserConversationState, context: MessageContext
    ):
        """Update user conversation patterns"""

        # Update humor frequency
        if context.humor_score > 0:
            user_state.humor_frequency = (user_state.humor_frequency * 0.9) + (
                context.humor_score * 0.1
            )

        # Update preferred topics
        for topic in context.topics:
            current_score = user_state.preferred_topics.get(topic, 0.0)
            user_state.preferred_topics[topic] = min(1.0, current_score + 0.1)

        # Update engagement level based on message characteristics
        engagement_delta = 0.0

        if len(context.content) > 20:  # Longer messages = more engagement
            engagement_delta += 0.05

        if context.response_triggers:  # Having triggers = more engagement
            engagement_delta += 0.05

        if context.topics:  # Topic discussion = more engagement
            engagement_delta += 0.05

        user_state.engagement_level = max(
            0.0, min(1.0, user_state.engagement_level + engagement_delta)
        )
        user_state.last_interaction = datetime.now(timezone.utc)

    async def _store_context(
        self, context: MessageContext, channel_id: int = None, guild_id: int = None
    ):
        """Store context in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO message_contexts 
                    (user_id, channel_id, guild_id, content, tone, humor_score, 
                     emotional_intensity, topics, response_triggers, response_probability, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        context.user_id,
                        channel_id,
                        guild_id,
                        context.content,
                        context.tone.value,
                        context.humor_score,
                        context.emotional_intensity,
                        json.dumps(context.topics),
                        json.dumps(
                            [trigger.value for trigger in context.response_triggers]
                        ),
                        context.response_probability,
                        context.timestamp.isoformat(),
                    ),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error storing context: {e}")

    async def get_analytics(self) -> Dict[str, Any]:
        """Get analytics about conversation patterns"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Response rate
                cursor.execute("SELECT COUNT(*) FROM message_contexts")
                total_messages = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT COUNT(*) FROM message_contexts WHERE bot_responded = 1"
                )
                responded_messages = cursor.fetchone()[0]

                response_rate = (
                    (responded_messages / total_messages * 100)
                    if total_messages > 0
                    else 0
                )

                # Top topics
                cursor.execute(
                    """
                    SELECT topics, COUNT(*) as count 
                    FROM message_contexts 
                    WHERE topics != '[]' 
                    GROUP BY topics 
                    ORDER BY count DESC 
                    LIMIT 10
                """
                )
                top_topics = cursor.fetchall()

                # Humor statistics
                cursor.execute(
                    "SELECT AVG(humor_score) FROM message_contexts WHERE humor_score > 0"
                )
                avg_humor_score = cursor.fetchone()[0] or 0

                return {
                    "total_messages_analyzed": total_messages,
                    "total_responses_sent": responded_messages,
                    "response_rate_percent": round(response_rate, 2),
                    "average_humor_score": round(avg_humor_score, 3),
                    "active_users": len(self.user_states),
                    "top_topics": top_topics,
                    "users_with_high_engagement": len(
                        [
                            u
                            for u in self.user_states.values()
                            if u.engagement_level > 0.7
                        ]
                    ),
                }

        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {"error": str(e)}


# Global context manager instance
_context_manager: Optional[UniversalContextManager] = None


def get_context_manager() -> Optional[UniversalContextManager]:
    """Get the global context manager instance"""
    return _context_manager


def initialize_context_manager(bot=None) -> UniversalContextManager:
    """Initialize the global context manager"""
    global _context_manager
    _context_manager = UniversalContextManager(bot)
    return _context_manager
