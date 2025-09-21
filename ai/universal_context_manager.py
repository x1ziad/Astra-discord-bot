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
    BOT_MENTIONED = "bot_mentioned"
    CONVERSATION_STARTER = "conversation_starter"
    OPINION_SHARING = "opinion_sharing"
    STORY_TELLING = "story_telling"
    FOLLOW_UP = "follow_up"
    COLLABORATIVE_DISCUSSION = "collaborative_discussion"
    REACTION_WORTHY = "reaction_worthy"


@dataclass
class MessageContext:
    """Context information for a message"""

    user_id: int
    content: str
    tone: ConversationTone = ConversationTone.CASUAL  # Default tone
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
                "console",
                "mobile game",
                "esports",
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
                "coding",
                "development",
                "app",
                "digital",
                "internet",
                "web",
            ],
            "entertainment": [
                "movie",
                "film",
                "tv show",
                "series",
                "music",
                "song",
                "album",
                "artist",
                "book",
                "novel",
                "anime",
                "manga",
                "podcast",
                "streaming",
                "netflix",
                "youtube",
                "video",
                "content",
            ],
            "lifestyle": [
                "food",
                "cooking",
                "recipe",
                "travel",
                "vacation",
                "hobby",
                "fitness",
                "workout",
                "health",
                "wellness",
                "fashion",
                "style",
                "photography",
                "art",
                "craft",
                "diy",
                "home",
                "garden",
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
                "relationship",
                "family",
                "social media",
                "dating",
            ],
            "education": [
                "learn",
                "study",
                "school",
                "college",
                "university",
                "course",
                "class",
                "teacher",
                "student",
                "education",
                "knowledge",
                "skill",
                "training",
                "tutorial",
                "exam",
                "homework",
                "research",
                "academic",
            ],
            "business": [
                "work",
                "job",
                "career",
                "business",
                "company",
                "office",
                "project",
                "meeting",
                "team",
                "management",
                "startup",
                "entrepreneur",
                "finance",
                "money",
                "investment",
                "marketing",
                "sales",
                "productivity",
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
                "data",
                "analysis",
                "statistics",
                "innovation",
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
                "astrology",
                "satellite",
            ],
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
                "4x game",
                "grand strategy",
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
                "question",
                "advice",
                "tip",
                "suggestion",
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

        # New patterns for enhanced conversation flow
        self.bot_mention_patterns = [
            r"\b(astra|bot|ai|assistant)\b",
            r"\b(hey (you|there)|talk to me|what do you think)\b",
            r"\b(your (opinion|thoughts|take))\b",
        ]

        self.conversation_starter_patterns = [
            r"^(so|well|anyway|btw|by the way)",
            r"\b(i think|i believe|in my opinion|personally)\b",
            r"\b(just wanted to say|wanted to share|thought you.*might)\b",
            r"\b(did you (know|hear|see)|have you (ever|tried))\b",
        ]

        self.opinion_patterns = [
            r"\b(i think|i believe|i feel|in my opinion|personally|imho)\b",
            r"\b(what.*think|your thoughts|any opinions)\b",
            r"\b(agree|disagree|thoughts on)\b",
        ]

        self.story_patterns = [
            r"\b(just happened|today i|yesterday|this morning|last night)\b",
            r"\b(funny story|guess what|you won't believe)\b",
            r"\b(so i was|i was just|i went to)\b",
        ]

        self.collaborative_patterns = [
            r"\b(let's|should we|we could|we should)\b",
            r"\b(anyone want|who wants|does anyone)\b",
            r"\b(together|team up|collaborate|work on)\b",
        ]

        self.reaction_worthy_patterns = [
            r"\b(wow|whoa|no way|really|seriously|omg)\b",
            r"\b(that's (crazy|wild|insane|cool|awesome))\b",
            r"\b(can't believe|mind blown|plot twist)\b",
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
        """Enhanced systematic tone detection based on multiple linguistic indicators"""
        text_lower = text.lower()
        text_len = len(text)

        # Initialize tone scoring system
        tone_scores = {
            ConversationTone.HUMOROUS: 0,
            ConversationTone.TECHNICAL: 0,
            ConversationTone.EMOTIONAL: 0,
            ConversationTone.EXCITED: 0,
            ConversationTone.QUESTIONING: 0,
            ConversationTone.SERIOUS: 0,
            ConversationTone.CASUAL: 0,
        }

        # 1. Humor Detection (highest priority)
        is_humorous, _, _ = HumorDetector().detect_humor(text)
        if is_humorous:
            tone_scores[ConversationTone.HUMOROUS] += 5

        # 2. Question Patterns
        question_indicators = 0
        for pattern in self.question_patterns:
            question_indicators += len(re.findall(pattern, text_lower))
        tone_scores[ConversationTone.QUESTIONING] += min(question_indicators * 2, 5)

        # 3. Technical Content Analysis
        tech_indicators = [
            "function",
            "algorithm",
            "code",
            "syntax",
            "error",
            "debug",
            "compile",
            "api",
            "database",
            "server",
            "framework",
            "library",
            "repository",
            "implementation",
            "configuration",
            "deployment",
            "optimization",
            "architecture",
            "protocol",
            "interface",
            "documentation",
            "version",
        ]
        tech_score = sum(1 for word in tech_indicators if word in text_lower)
        tone_scores[ConversationTone.TECHNICAL] += min(tech_score, 5)

        # 4. Excitement Indicators
        excitement_patterns = [
            r"\b(wow|awesome|amazing|incredible|fantastic|epic|stellar)\b",
            r"[!]{2,}",
            r"[A-Z]{3,}",
            r"😍|🤩|🔥|⚡|💯|🚀|🌟|✨",
            r"\b(omg|lol|lmao|rofl)\b",
        ]
        excitement_score = sum(
            len(re.findall(pattern, text_lower)) for pattern in excitement_patterns
        )
        tone_scores[ConversationTone.EXCITED] += min(excitement_score * 2, 5)

        # 5. Emotional Content
        emotional_indicators = [
            r"\b(love|hate|feel|emotion|heart|soul|pain|joy|sad|happy|angry|frustrated)\b",
            r"❤️|💔|😢|😭|😡|😤|😔|🥺|😊|😀|😃",
            r"\b(wonderful|terrible|devastating|beautiful|ugly|amazing)\b",
        ]
        emotional_score = sum(
            len(re.findall(pattern, text_lower)) for pattern in emotional_indicators
        )
        tone_scores[ConversationTone.EMOTIONAL] += min(emotional_score * 2, 5)

        # 6. Casual vs Formal Language Analysis
        casual_indicators = [
            "lol",
            "haha",
            "yeah",
            "nah",
            "gonna",
            "wanna",
            "sup",
            "hey",
            "yo",
            "dude",
            "bro",
            "man",
            "tbh",
            "ngl",
            "imo",
            "btw",
            "rn",
            "omg",
            "'ll",
            "'re",
            "'ve",
            "'d",
            "isn't",
            "won't",
            "can't",
            "don't",
        ]
        casual_score = sum(1 for word in casual_indicators if word in text_lower)
        tone_scores[ConversationTone.CASUAL] += min(casual_score, 5)

        # 7. Formal/Serious Language Indicators
        formal_indicators = [
            "therefore",
            "however",
            "furthermore",
            "nevertheless",
            "consequently",
            "additionally",
            "specifically",
            "particularly",
            "regarding",
            "concerning",
            "implementation",
            "consideration",
            "evaluation",
            "assessment",
            "analysis",
        ]
        formal_score = sum(1 for word in formal_indicators if word in text_lower)

        # Long, structured messages tend to be more serious
        if text_len > 150 and formal_score > 0:
            tone_scores[ConversationTone.SERIOUS] += 3
        elif text_len > 300:
            tone_scores[ConversationTone.SERIOUS] += 2

        # 8. Contextual Adjustments
        # Multiple punctuation suggests excitement or emotion
        if len(re.findall(r"[!?]{2,}", text)) > 0:
            tone_scores[ConversationTone.EXCITED] += 2

        # All caps words suggest emphasis/excitement
        caps_words = len(re.findall(r"\b[A-Z]{2,}\b", text))
        if caps_words > 0:
            tone_scores[ConversationTone.EXCITED] += caps_words

        # Short messages with minimal punctuation tend to be casual
        if text_len < 50 and not any(char in text for char in "!?"):
            tone_scores[ConversationTone.CASUAL] += 2

        # Return the tone with the highest score
        max_tone = max(tone_scores.items(), key=lambda x: x[1])

        # If no clear winner (all scores are low), default to casual
        if max_tone[1] <= 1:
            return ConversationTone.CASUAL

        return max_tone[0]

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

        # Bot mentions - NEW
        if any(re.search(pattern, text_lower) for pattern in self.bot_mention_patterns):
            triggers.append(ResponseTrigger.BOT_MENTIONED)

        # Conversation starters - NEW
        if any(
            re.search(pattern, text_lower)
            for pattern in self.conversation_starter_patterns
        ):
            triggers.append(ResponseTrigger.CONVERSATION_STARTER)

        # Opinion sharing - NEW
        if any(re.search(pattern, text_lower) for pattern in self.opinion_patterns):
            triggers.append(ResponseTrigger.OPINION_SHARING)

        # Story telling - NEW
        if any(re.search(pattern, text_lower) for pattern in self.story_patterns):
            triggers.append(ResponseTrigger.STORY_TELLING)

        # Collaborative discussion - NEW
        if any(
            re.search(pattern, text_lower) for pattern in self.collaborative_patterns
        ):
            triggers.append(ResponseTrigger.COLLABORATIVE_DISCUSSION)

        # Reaction worthy content - NEW
        if any(
            re.search(pattern, text_lower) for pattern in self.reaction_worthy_patterns
        ):
            triggers.append(ResponseTrigger.REACTION_WORTHY)

        # Topic matches
        if self._extract_topics(text):
            triggers.append(ResponseTrigger.TOPIC_MATCH)

        # Emotional support
        for emotion_patterns in self.emotion_patterns.values():
            if any(re.search(pattern, text_lower) for pattern in emotion_patterns):
                triggers.append(ResponseTrigger.EMOTIONAL_SUPPORT)
                break

        # Conversation flow detection - NEW
        # Detect if this message seems to be continuing an ongoing conversation
        if (
            len(text) > 20  # Substantial message
            and not any(
                re.search(pattern, text_lower) for pattern in self.greeting_patterns
            )  # Not a greeting
            and (text.count(".") > 0 or text.count(",") > 1)
        ):  # Has sentence structure
            triggers.append(ResponseTrigger.CONVERSATION_FLOW)

        return triggers

    def _calculate_response_probability(self, context: MessageContext) -> float:
        """Calculate probability that bot should respond (0.0 to 1.0)"""
        probability = 0.0

        # Base trigger probabilities - More responsive weights
        trigger_weights = {
            ResponseTrigger.QUESTION_ASKED: 0.95,
            ResponseTrigger.HELP_NEEDED: 0.9,
            ResponseTrigger.BOT_MENTIONED: 0.85,
            ResponseTrigger.GREETING: 0.8,  # Increased from 0.75
            ResponseTrigger.EMOTIONAL_SUPPORT: 0.8,
            ResponseTrigger.CELEBRATION: 0.7,  # Increased from 0.6
            ResponseTrigger.CONVERSATION_STARTER: 0.65,  # Increased from 0.6
            ResponseTrigger.COLLABORATIVE_DISCUSSION: 0.7,
            ResponseTrigger.OPINION_SHARING: 0.6,  # Increased from 0.5
            ResponseTrigger.HUMOR_DETECTED: 0.6,  # Increased from 0.5
            ResponseTrigger.REACTION_WORTHY: 0.55,  # Increased from 0.45
            ResponseTrigger.STORY_TELLING: 0.5,  # Increased from 0.4
            ResponseTrigger.TOPIC_MATCH: 0.5,  # Increased from 0.4
            ResponseTrigger.CONVERSATION_FLOW: 0.45,  # Increased from 0.35
        }

        # Calculate max probability from triggers
        for trigger in context.response_triggers:
            probability = max(probability, trigger_weights.get(trigger, 0.1))

        # Boost probability based on context - More generous
        if context.humor_score > 0.4:  # Lowered threshold from 0.5
            probability += 0.3  # Increased from 0.25

        if context.emotional_intensity > 0.6:  # Lowered threshold from 0.7
            probability += 0.25  # Increased from 0.2

        if len(context.topics) > 1:  # Multiple topics = more engagement
            probability += 0.2  # Increased from 0.15
        elif len(context.topics) == 1:  # Single topic still valuable
            probability += 0.1  # Increased from 0.05

        # Message length considerations - More responsive
        content_length = len(context.content)
        if (
            content_length > 80
        ):  # Reduced from 100 - Substantial messages deserve responses
            probability += 0.15  # Increased from 0.1
        elif content_length > 40:  # Reduced from 50
            probability += 0.1  # Increased from 0.05

        # Tone adjustments - More generous
        tone_modifiers = {
            ConversationTone.QUESTIONING: 0.3,  # Increased from 0.25
            ConversationTone.EMOTIONAL: 0.25,  # Increased from 0.2
            ConversationTone.EXCITED: 0.2,  # Increased from 0.15
            ConversationTone.HUMOROUS: 0.2,  # Increased from 0.15
            ConversationTone.CASUAL: 0.1,  # Increased from 0.05
            ConversationTone.TECHNICAL: 0.15,  # NEW: Encourage technical discussions
        }

        probability += tone_modifiers.get(context.tone, 0.0)

        # Encourage varied conversation - NEW
        # If multiple triggers are present, boost probability
        if len(context.response_triggers) > 2:
            probability += 0.1
        elif len(context.response_triggers) > 1:
            probability += 0.05

        return min(1.0, probability)

    def _suggest_response_style(self, context: MessageContext) -> str:
        """Enhanced systematic response style determination based on topic, tone, and triggers"""

        # Priority 1: Humor always takes precedence (highest engagement value)
        if context.humor_score > 0.4:
            return "humorous_companion"

        # Priority 2: Topic-based personality adaptation (most specific)
        if context.topics:
            primary_topic = context.topics[0]  # Use the first detected topic

            topic_personalities = {
                "gaming": "enthusiastic_gamer",  # Excited, competitive, uses gaming terminology
                "entertainment": "cultural_enthusiast",  # Knowledgeable about media, engaging, appreciative
                "technology": "tech_savvy_expert",  # Informative, forward-thinking, solution-oriented
                "lifestyle": "supportive_friend",  # Encouraging, personal, empathetic
                "education": "patient_mentor",  # Educational, structured, encouraging
                "business": "professional_advisor",  # Formal, strategic, solution-oriented
                "science": "curious_researcher",  # Analytical, fact-based, questioning
                "space": "cosmic_explorer",  # Wonder-filled, expansive, inspirational
                "stellaris": "strategic_advisor",  # Tactical, empire-focused, strategic
                "social": "social_connector",  # Warm, community-focused, inclusive
                "help": "helpful_guide",  # Patient, step-by-step, supportive
            }

            if primary_topic in topic_personalities:
                return topic_personalities[primary_topic]

        # Priority 3: Tone-based adaptation (medium specificity)
        tone_personality_map = {
            ConversationTone.TECHNICAL: "technical_expert",  # Clear, precise, in-depth
            ConversationTone.EMOTIONAL: "empathetic_supporter",  # Caring, understanding, validating
            ConversationTone.EXCITED: "energetic_enthusiast",  # High energy, matching excitement
            ConversationTone.HUMOROUS: "witty_companion",  # Already handled above, but backup
            ConversationTone.QUESTIONING: "patient_educator",  # Thorough, explanatory, helpful
            ConversationTone.SERIOUS: "thoughtful_advisor",  # Measured, professional, considered
            ConversationTone.CASUAL: "friendly_conversationalist",  # Relaxed, approachable, natural
        }

        if context.tone in tone_personality_map:
            return tone_personality_map[context.tone]

        # Priority 4: Response trigger-based personalities (general context)
        trigger_personality_map = {
            ResponseTrigger.HELP_NEEDED: "helpful_guide",
            ResponseTrigger.CELEBRATION: "celebratory_cheerleader",
            ResponseTrigger.BOT_MENTIONED: "engaging_responder",
            ResponseTrigger.CONVERSATION_STARTER: "conversation_catalyst",
            ResponseTrigger.OPINION_SHARING: "thoughtful_discussant",
            ResponseTrigger.STORY_TELLING: "interested_listener",
            ResponseTrigger.COLLABORATIVE_DISCUSSION: "collaborative_partner",
            ResponseTrigger.REACTION_WORTHY: "responsive_reactor",
            ResponseTrigger.GREETING: "warm_welcomer",
        }

        # Check triggers in order of priority
        for trigger in context.response_triggers:
            if trigger in trigger_personality_map:
                return trigger_personality_map[trigger]

        # Priority 5: Contextual fallbacks based on message characteristics
        # Complex multi-topic discussions
        if len(context.topics) > 2:
            return "multi_topic_synthesizer"

        # Detailed, analytical content
        if hasattr(context, "message_length") and context.message_length > 200:
            return "detailed_analyst"

        # Quick, brief interactions
        if hasattr(context, "message_length") and context.message_length < 30:
            return "quick_responder"

        # Default: balanced, adaptable personality
        return "balanced_assistant"


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

        # Configuration - More permissive for better conversation flow
        self.min_response_interval = timedelta(
            seconds=5  # Reduced from 8 seconds
        )  # Min time between responses to same user
        self.channel_response_interval = timedelta(
            seconds=15  # Reduced from 20 seconds
        )  # Min time between responses in same channel
        self.max_responses_per_hour = (
            40  # Increased from 30 - Max responses per hour per channel
        )

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

        # User-specific rate limiting - Relaxed for better conversation flow
        if context.user_id in self.last_responses:
            time_since_last = current_time - self.last_responses[context.user_id]
            if time_since_last < self.min_response_interval:
                # Allow immediate responses to high-priority triggers even during rate limit
                high_priority_override = [
                    ResponseTrigger.QUESTION_ASKED,
                    ResponseTrigger.HELP_NEEDED,
                    ResponseTrigger.BOT_MENTIONED,
                ]
                if not any(
                    trigger in context.response_triggers
                    for trigger in high_priority_override
                ):
                    return False, "user_rate_limit"

        # Channel-specific rate limiting - Relaxed
        if channel_id and channel_id in self.channel_last_response:
            time_since_last = current_time - self.channel_last_response[channel_id]
            if time_since_last < self.channel_response_interval:
                # Allow responses to very high priority triggers
                very_high_priority = [
                    ResponseTrigger.QUESTION_ASKED,
                    ResponseTrigger.HELP_NEEDED,
                    ResponseTrigger.BOT_MENTIONED,
                ]
                if not any(
                    trigger in context.response_triggers
                    for trigger in very_high_priority
                ):
                    return False, "channel_rate_limit"

        # Always respond to high-priority triggers
        high_priority_triggers = [
            ResponseTrigger.QUESTION_ASKED,
            ResponseTrigger.HELP_NEEDED,
            ResponseTrigger.BOT_MENTIONED,  # NEW: Always respond when bot is mentioned
        ]

        for trigger in high_priority_triggers:
            if trigger in context.response_triggers:
                return True, f"high_priority_trigger_{trigger.value}"

        # Always respond to very engaging content
        very_engaging_triggers = [
            ResponseTrigger.GREETING,
            ResponseTrigger.EMOTIONAL_SUPPORT,
            ResponseTrigger.COLLABORATIVE_DISCUSSION,
        ]

        for trigger in very_engaging_triggers:
            if trigger in context.response_triggers:
                # Higher chance for these triggers
                if random.random() < 0.8:  # 80% chance
                    return True, f"engaging_trigger_{trigger.value}"

        # Enhanced probability-based responses
        import random

        # Adjust probability based on user engagement
        user_state = self.user_states.get(context.user_id)
        adjusted_probability = context.response_probability

        if user_state:
            # Boost probability for engaged users
            if user_state.engagement_level > 0.7:
                adjusted_probability *= 1.4  # Increased from 1.3
            elif user_state.engagement_level < 0.3:
                adjusted_probability *= 0.95  # More lenient than 0.9

            # Recent conversation boost - More generous
            if (
                user_state.last_interaction
                and (current_time - user_state.last_interaction).seconds < 600
            ):  # Increased from 300 to 600 seconds (10 minutes)
                adjusted_probability *= 1.3  # Increased from 1.2

        # Context-specific boosts - Enhanced
        context_boosts = 0.0

        # Boost for conversation starters
        if ResponseTrigger.CONVERSATION_STARTER in context.response_triggers:
            context_boosts += 0.2  # Increased from 0.15

        # Boost for opinion sharing (encourage discussion)
        if ResponseTrigger.OPINION_SHARING in context.response_triggers:
            context_boosts += 0.15  # Increased from 0.1

        # Boost for story telling (show interest)
        if ResponseTrigger.STORY_TELLING in context.response_triggers:
            context_boosts += 0.15  # Increased from 0.1

        # Boost for reaction-worthy content
        if ResponseTrigger.REACTION_WORTHY in context.response_triggers:
            context_boosts += 0.2  # Increased from 0.15

        # Apply context boosts
        adjusted_probability += context_boosts
        adjusted_probability = min(1.0, adjusted_probability)

        # Lower threshold for some scenarios - More responsive
        # Be more responsive to conversation flow
        if (
            ResponseTrigger.CONVERSATION_FLOW in context.response_triggers
            and adjusted_probability > 0.2  # Lowered from 0.25
        ):
            adjusted_probability = max(adjusted_probability, 0.45)  # Increased from 0.4

        # Random check against probability
        random_value = random.random()
        if random_value < adjusted_probability:
            return (
                True,
                f"probability_trigger_{adjusted_probability:.2f}_rolled_{random_value:.2f}",
            )

        # Fallback: occasionally respond to maintain engagement - More generous
        # Small chance to respond even to low-probability messages to keep conversation alive
        if (
            len(context.content) > 20  # Reduced from 30 - Respond to shorter messages
            and len(context.response_triggers) > 0  # Has some triggers
            and random.random() < 0.15  # Increased from 0.1 (15% chance)
        ):
            return True, "engagement_maintenance"

        return False, f"probability_too_low_{adjusted_probability:.2f}"

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
