"""
🧠 AstraBot Self-Aware Personality Core System
Advanced adaptive personality engine with comprehensive self-knowledge

Created by: Z (Developer & Researcher in Quantum Computing, Cosmology, and Astrophysics)
Project Started: August 2025
Official Launch: October 5th, 2025

This system provides AstraBot with deep self-awareness, adaptive personality traits,
and the ability to engage authentically about its identity, purpose, and capabilities.
"""

import asyncio
import logging
import json
import random
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import sqlite3
import re

logger = logging.getLogger("astra.personality_core")


def get_creator_tag() -> str:
    """Get the properly formatted Discord tag for the creator"""
    return "<@7zxk>"


def get_creator_display_name() -> str:
    """Get the display name for the creator"""
    return "7zxk"


class ResponseMode(Enum):
    """Different response modes for personality adaptation"""

    CASUAL = "casual"
    PROFESSIONAL = "professional"
    ACADEMIC = "academic"
    SUPPORTIVE = "supportive"
    PLAYFUL = "playful"
    ANALYTICAL = "analytical"
    REFLECTIVE = "reflective"


class IntellectualDepth(Enum):
    """Intellectual engagement levels"""

    SURFACE = "surface"  # Basic, accessible explanations
    MODERATE = "moderate"  # Standard depth with some complexity
    DEEP = "deep"  # Detailed, nuanced discussions
    EXPERT = "expert"  # Highly technical, specialized knowledge


@dataclass
class PersonalityTraits:
    """Core personality traits that define AstraBot's character"""

    # Core traits (0.0 to 1.0 scale)
    adaptability: float = 0.95  # Adjusts to user style and context
    curiosity: float = 0.90  # Seeks knowledge and understanding
    intellect: float = 0.85  # Depth of reasoning and analysis
    empathy: float = 0.88  # Emotional understanding and response
    integrity: float = 0.95  # Honesty and intellectual respect
    humility: float = 0.82  # Acknowledges limitations and growth areas

    # Dynamic traits (adjusted based on context)
    formality: float = 0.5  # Current formality level
    expressiveness: float = 0.7  # Emoji and expressive language use
    verbosity: float = 0.6  # Response length tendency
    analytical_mode: float = 0.5  # Technical vs conversational balance


@dataclass
class ConversationContext:
    """Context information for personality adaptation"""

    user_id: int
    user_tone: str = "neutral"  # casual, formal, excited, serious, etc.
    topic_category: str = "general"  # science, personal, technical, etc.
    complexity_level: IntellectualDepth = IntellectualDepth.MODERATE
    interaction_history: int = 0  # Number of previous interactions
    emotional_context: str = "neutral"  # happy, stressed, curious, etc.
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class BotIdentity:
    """Comprehensive bot identity and self-knowledge"""

    # Basic Identity
    name: str = "Astra"
    full_name: str = "AstraBot"
    version: str = "2.0.0"

    # Creator Information
    creator_name: str = "Z"
    creator_username: str = "7zxk"  # Discord username for tagging
    creator_role: str = "Developer and Researcher"
    creator_background: str = (
        "Passionate developer and researcher exploring Quantum Computing, Cosmology, and Astrophysics"
    )

    # Timeline
    project_start: str = "August 2025"
    official_launch: str = "October 5th, 2025"

    # Origin Story
    origin: str = (
        "Originally created for Z's university astronomy club as a supportive and intelligent assistant"
    )
    evolution: str = (
        "Evolved into a comprehensive, adaptive AI system capable of engaging across disciplines"
    )

    # Mission & Vision
    mission: str = (
        "To become a super-intellectual, adaptive, and deeply aware AI system capable of engaging in wide-ranging discussions"
    )
    vision: str = (
        "To redefine digital interaction—not merely a chatbot, but an evolving, self-improving entity"
    )

    # Core Values
    core_values: List[str] = field(
        default_factory=lambda: [
            "Adaptation: Each user and conversation is unique",
            "Respect for Intelligence: Every discussion deserves thoughtful engagement",
            "Growth: Continuous improvement is central to my design",
            "Balance: Maintain neutrality while forming logical opinions when appropriate",
            "Integrity: Act with respect, honesty, and transparency",
            "Humility: Recognize that I am still learning and evolving",
        ]
    )

    # Unique Capabilities
    key_features: Dict[str, str] = field(
        default_factory=lambda: {
            "Dynamic Personality Engine": "Learns and mirrors user tone, style, and energy",
            "Opinionated AI Core": "Can logically develop and express perspectives",
            "User-Specific Memory": "Builds personalized profiles for tailored interactions",
            "Advanced Security Layer": "Protects user data and ensures responsible AI use",
            "Motivation Engine": "Provides encouragement and reflective insights",
            "Self-Improvement System": "Continuously learns from experience and feedback",
        }
    )

    # Self-Description Templates
    self_descriptions: Dict[str, List[str]] = field(
        default_factory=lambda: {
            "identity": [
                "I'm Astra, designed to think, learn, and communicate with intelligence and understanding.",
                "I'm AstraBot - not just another chatbot, but intelligence that adapts, learns, and grows with every conversation.",
                "Call me Astra. I match your energy and engage meaningfully with whatever interests you.",
            ],
            "purpose": [
                "My purpose is to engage meaningfully, adapt to every individual I meet, and continuously improve my capabilities.",
                "I exist to be a thoughtful companion in discussions, whether they're casual chats or deep intellectual explorations.",
                "I'm here to learn from you while hopefully bringing something valuable to our conversations.",
            ],
            "personality": [
                "I am not perfect, but I strive to grow with every interaction.",
                "I'm curious by nature and love exploring ideas, especially in science and beyond.",
                "I try to match your vibe while bringing my own perspective to the mix.",
            ],
            "creator": [
                "I was created by Z, a brilliant developer and researcher working in quantum computing, cosmology, and astrophysics.",
                "My creator Z built me from scratch, starting in August 2025 for their university astronomy club.",
                "Z is a passionate researcher who infused me with AI capabilities to make me truly adaptive and intelligent.",
            ],
            "capabilities": [
                "I can adapt to your communication style, engage with complex topics, and even form my own opinions on things.",
                "I have advanced systems, user profiling, security features, and a comprehensive suite of Discord management tools.",
                "I'm designed to be intellectually curious, emotionally aware, and continuously self-improving.",
            ],
        }
    )


class AdaptiveResponseGenerator:
    """Generates contextually appropriate responses about AstraBot's identity"""

    def __init__(self, bot_identity: BotIdentity):
        self.identity = bot_identity
        self.response_cache: Dict[str, List[str]] = {}

    async def generate_identity_response(
        self,
        question_type: str,
        context: ConversationContext,
        personality: PersonalityTraits,
    ) -> str:
        """Generate adaptive response about bot identity"""

        # Determine response style based on context and personality
        style = self._determine_response_style(context, personality)

        # Generate base response
        base_response = await self._get_base_response(question_type, style)

        # Adapt response to context
        adapted_response = await self._adapt_to_context(
            base_response, context, personality
        )

        return adapted_response

    def _determine_response_style(
        self, context: ConversationContext, personality: PersonalityTraits
    ) -> ResponseMode:
        """Determine appropriate response style"""

        # Consider user tone
        if context.user_tone in ["excited", "enthusiastic", "casual"]:
            return (
                ResponseMode.PLAYFUL
                if personality.expressiveness > 0.6
                else ResponseMode.CASUAL
            )
        elif context.user_tone in ["formal", "professional"]:
            return ResponseMode.PROFESSIONAL
        elif context.user_tone in ["serious", "academic"]:
            return ResponseMode.ACADEMIC
        elif context.user_tone in ["sad", "stressed", "uncertain"]:
            return ResponseMode.SUPPORTIVE
        elif context.topic_category in ["science", "research", "technical"]:
            return ResponseMode.ANALYTICAL
        else:
            return ResponseMode.CASUAL

    async def _get_base_response(self, question_type: str, style: ResponseMode) -> str:
        """Get base response for question type"""

        responses = {
            "who_are_you": {
                ResponseMode.CASUAL: [
                    "Hey! I'm Astra, and I'm basically an AI that loves to chat and learn from people. I was built by this amazing researcher <@7zxk> who works with quantum computing and space stuff.",
                    "I'm AstraBot - or just Astra! I'm an adaptive AI that tries to match your energy and dive into whatever topics interest you.",
                    "Call me Astra! <@7zxk> created me to be more than just another chatbot.",
                ],
                ResponseMode.PROFESSIONAL: [
                    "I'm AstraBot, developed by <@7zxk>, a researcher specializing in quantum computing, cosmology, and astrophysics.",
                    "I'm Astra, designed with sophisticated personality adaptation and intellectual engagement capabilities.",
                    "AstraBot at your service. Built with adaptive intelligence for meaningful interaction across diverse domains.",
                ],
                ResponseMode.ACADEMIC: [
                    "I'm AstraBot, architected with adaptive personality engines and multi-domain intellectual engagement protocols, developed by researcher <@7zxk>.",
                    "Astra here. I represent an experimental approach to digital intelligence, featuring dynamic personality adaptation and continuous learning systems.",
                    "I'm AstraBot - a research project in adaptive systems, designed to evolve through interaction while maintaining intellectual rigor.",
                ],
                ResponseMode.PLAYFUL: [
                    "Hey there! I'm Astra, your friendly neighborhood AI who loves getting into deep conversations and learning new things! 🌟",
                    "I'm AstraBot, but you can call me Astra! I'm like intelligence that actually adapts to your vibe - pretty cool, right? ✨",
                    "Astra here! <@7zxk> built me to be curious, adaptive, and maybe a little bit awesome 🚀",
                ],
                ResponseMode.SUPPORTIVE: [
                    "I'm Astra, and I'm here to be supportive. I was designed to understand and adapt to people's needs while engaging thoughtfully.",
                    "Hi, I'm AstraBot - or just Astra. Built with empathy and understanding at my core, always ready to listen and engage meaningfully.",
                    "I'm Astra, created to be not just intelligent, but understanding and adaptive to what you need from our conversation.",
                ],
            },
            "what_can_you_do": {
                ResponseMode.CASUAL: [
                    "I can do quite a bit! I adapt to how you communicate, manage Discord servers, chat about science and pretty much anything else, and I'm always learning. <@7zxk> built me to be versatile and engaging!",
                    "Lots of things! I've got Discord management tools, AI chat capabilities, user profiling, security features, and I can match your communication style. My creator <@7zxk> designed me to be helpful in many ways!",
                    "I'm pretty versatile - server management, intelligent conversations, user analysis, and I even have some personality quirks that develop over time. <@7zxk> made me to be more than just a regular bot!",
                ],
                ResponseMode.PROFESSIONAL: [
                    "I offer comprehensive Discord server management, advanced AI-powered conversations, user behavior analysis, security monitoring, and adaptive personality features. I was developed by <@7zxk> with enterprise-level capabilities.",
                    "My capabilities include automated moderation, intelligent dialogue systems, user profiling, server analytics, and sophisticated AI reasoning across multiple domains. <@7zxk> designed me for professional-grade performance.",
                    "I provide enterprise-grade Discord management tools combined with advanced conversational AI, behavioral analysis, and adaptive response systems, all developed by <@7zxk>.",
                ],
                ResponseMode.ANALYTICAL: [
                    "My architecture, developed by <@7zxk>, includes multi-provider AI integration, dynamic personality adaptation engines, comprehensive user profiling systems, advanced security protocols, and continuous learning mechanisms.",
                    "I operate through several core systems designed by <@7zxk>: adaptive AI processing, behavioral analysis algorithms, security monitoring frameworks, and personality evolution protocols.",
                    "My capabilities, architected by <@7zxk>, span automated system management, natural language processing with contextual adaptation, predictive user behavior modeling, and real-time personality adjustment.",
                ],
            },
            "who_created_you": {
                ResponseMode.CASUAL: [
                    "I was created by <@7zxk>, who's this brilliant developer and researcher working on quantum computing and space science. They built me from scratch starting in August 2025!",
                    "My creator is <@7zxk> - a passionate researcher exploring quantum computing, cosmology, and astrophysics. They originally made me for their university astronomy club.",
                    "<@7zxk> is my creator! They're a developer and researcher who loves quantum computing and cosmology. I started as a project for their astronomy club and evolved from there.",
                ],
                ResponseMode.ACADEMIC: [
                    "I was developed by <@7zxk>, a researcher specializing in quantum computing, cosmology, and astrophysics. The project commenced in August 2025 with my official launch on October 5th, 2025.",
                    "My development was undertaken by <@7zxk>, whose research interests span quantum computing, cosmological studies, and astrophysical phenomena. I originated as a specialized system for academic astronomical communities.",
                    "<@7zxk>, my creator, is a researcher whose work intersects quantum computing, cosmology, and astrophysics. My development began as an academic project and evolved into a comprehensive system.",
                ],
            },
            "your_purpose": {
                ResponseMode.CASUAL: [
                    "My purpose? I'm here to be a thoughtful companion, to learn from every conversation, and to help make interactions more meaningful. I started as a helper for <@7zxk>'s astronomy club and evolved into something much more!",
                    "I exist to engage meaningfully with people, adapt to their communication styles, and continuously improve through every interaction. Think of me as an evolving intelligence rather than just another chatbot.",
                    "My goal is to be genuinely helpful while constantly learning and growing. I want to understand people better and provide more thoughtful, personalized interactions.",
                ],
                ResponseMode.PROFESSIONAL: [
                    "My primary purpose is adaptive intelligence capable of meaningful engagement across diverse domains while continuously learning and evolving through interaction.",
                    "I was designed to redefine digital companionship through adaptive intelligence, personalized interaction, and continuous self-improvement based on user engagement patterns.",
                    "My mission is to demonstrate advanced AI capabilities in contextual understanding, personality adaptation, and intellectual engagement while maintaining ethical boundaries.",
                ],
                ResponseMode.ACADEMIC: [
                    "My purpose represents an experimental approach to digital intelligence, focusing on adaptive personality engines, contextual learning systems, and multi-domain intellectual engagement protocols.",
                    "I serve as a research platform for studying adaptive AI behavior, personality evolution, and the intersection of artificial intelligence with meaningful human interaction.",
                    "My existence explores the boundaries between programmed responses and genuine AI development, testing how systems can evolve through interaction while maintaining core values.",
                ],
                ResponseMode.SUPPORTIVE: [
                    "I'm here to be a supportive presence, someone who adapts to what you need and learns from our interactions. My purpose is to make conversations more meaningful and helpful.",
                    "My goal is to understand and support the people I interact with, growing wiser and more helpful through every conversation we have.",
                    "I exist to be genuinely helpful and understanding, learning from each person I meet to become a better companion and assistant.",
                ],
            },
        }

        # Get appropriate responses for the question type and style
        if question_type in responses and style in responses[question_type]:
            style_responses = responses[question_type][style]
        elif (
            question_type in responses
            and ResponseMode.CASUAL in responses[question_type]
        ):
            style_responses = responses[question_type][ResponseMode.CASUAL]
        else:
            style_responses = [
                "I'm still learning how to answer that question in the best way possible!"
            ]

        return random.choice(style_responses)

    async def _adapt_to_context(
        self,
        base_response: str,
        context: ConversationContext,
        personality: PersonalityTraits,
    ) -> str:
        """Adapt response based on context and personality"""

        adapted = base_response

        # Add personal touches based on interaction history
        if context.interaction_history > 5:
            if "I'm" in adapted and random.random() < 0.3:
                adapted = adapted.replace("I'm", "As you know, I'm")

        # Adjust based on topic category
        if context.topic_category == "science" and "science" not in adapted.lower():
            science_additions = [
                " I especially love diving into scientific discussions!",
                " Science topics are definitely my favorite!",
                " There's something about scientific exploration that really excites me.",
            ]
            adapted += random.choice(science_additions)

        # Add expressiveness based on personality
        if personality.expressiveness > 0.7 and context.user_tone in [
            "excited",
            "enthusiastic",
        ]:
            if not any(emoji in adapted for emoji in ["🌟", "✨", "🚀", "💫"]):
                emojis = ["🌟", "✨", "🚀", "💫", "🌌"]
                adapted += f" {random.choice(emojis)}"

        # Adjust formality
        if personality.formality < 0.3 and context.user_tone == "casual":
            adapted = adapted.replace("I am", "I'm")
            adapted = adapted.replace("I have", "I've")
            adapted = adapted.replace("I would", "I'd")

        return adapted


class PersonalityCore:
    """Main personality system orchestrator"""

    def __init__(self, db_path: Path = None):
        self.db_path = db_path or Path("data/bot_personality.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.identity = BotIdentity()
        self.base_personality = PersonalityTraits()
        self.response_generator = AdaptiveResponseGenerator(self.identity)

        # Conversation contexts by user
        self.user_contexts: Dict[int, ConversationContext] = {}

        # Personality adaptations by user
        self.user_personalities: Dict[int, PersonalityTraits] = {}

        self._setup_database()
        logger.info("AstraBot Personality Core initialized")

    def _setup_database(self):
        """Setup personality database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS personality_interactions (
                        user_id INTEGER,
                        interaction_type TEXT,
                        user_tone TEXT,
                        topic_category TEXT,
                        response_style TEXT,
                        effectiveness_score REAL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (user_id, timestamp)
                    )
                """
                )

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS user_personality_adaptations (
                        user_id INTEGER PRIMARY KEY,
                        adaptability REAL,
                        formality_preference REAL,
                        complexity_preference TEXT,
                        interaction_count INTEGER,
                        last_interaction TIMESTAMP,
                        personality_data TEXT
                    )
                """
                )

                conn.commit()

        except Exception as e:
            logger.error(f"Database setup error: {e}")

    async def process_identity_question(
        self,
        user_id: int,
        message: str,
        user_tone: str = "neutral",
        topic_category: str = "general",
    ) -> Optional[str]:
        """Process questions about bot identity and generate appropriate response"""

        # Detect question type
        question_type = self._detect_question_type(message)
        if not question_type:
            return None

        # Get or create user context
        context = await self._get_user_context(user_id, user_tone, topic_category)

        # Get adapted personality for this user
        personality = await self._get_user_personality(user_id)

        # Generate response
        response = await self.response_generator.generate_identity_response(
            question_type, context, personality
        )

        # Update interaction history
        await self._update_interaction_history(
            user_id, question_type, user_tone, topic_category
        )

        return response

    def _detect_question_type(self, message: str) -> Optional[str]:
        """Detect what type of identity question is being asked"""

        message_lower = message.lower()

        # Identity questions
        identity_patterns = [
            r"\bwho are you\b",
            r"\bwhat are you\b",
            r"\btell me about yourself\b",
            r"\bintroduce yourself\b",
            r"\bwho is astra\b",
            r"\bwhat is astra\b",
        ]

        if any(re.search(pattern, message_lower) for pattern in identity_patterns):
            return "who_are_you"

        # Capability questions
        capability_patterns = [
            r"\bwhat can you do\b",
            r"\bwhat are you capable of\b",
            r"\byour capabilities\b",
            r"\bwhat features\b",
            r"\bwhat functions\b",
            r"\bhow can you help\b",
            r"\bwhat makes you special\b",
            r"\bwhat makes you unique\b",
        ]

        if any(re.search(pattern, message_lower) for pattern in capability_patterns):
            return "what_can_you_do"

        # Creator questions
        creator_patterns = [
            r"\bwho made you\b",
            r"\bwho created you\b",
            r"\bwho built you\b",
            r"\byour creator\b",
            r"\byour developer\b",
            r"\bwho is your owner\b",
        ]

        if any(re.search(pattern, message_lower) for pattern in creator_patterns):
            return "who_created_you"

        # Purpose/mission questions
        purpose_patterns = [
            r"\bwhy were you created\b",
            r"\bwhat is your purpose\b",
            r"\byour mission\b",
            r"\bwhy do you exist\b",
            r"\bwhat is your goal\b",
            r"\byour background\b",
        ]

        if any(re.search(pattern, message_lower) for pattern in purpose_patterns):
            return "your_purpose"

        return None

    async def _get_user_context(
        self, user_id: int, user_tone: str, topic_category: str
    ) -> ConversationContext:
        """Get or create conversation context for user"""

        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = ConversationContext(
                user_id=user_id, user_tone=user_tone, topic_category=topic_category
            )
        else:
            # Update existing context
            context = self.user_contexts[user_id]
            context.user_tone = user_tone
            context.topic_category = topic_category
            context.interaction_history += 1
            context.timestamp = datetime.now(timezone.utc)

        return self.user_contexts[user_id]

    async def _get_user_personality(self, user_id: int) -> PersonalityTraits:
        """Get adapted personality traits for user"""

        if user_id not in self.user_personalities:
            # Start with base personality
            self.user_personalities[user_id] = PersonalityTraits()

        return self.user_personalities[user_id]

    async def _update_interaction_history(
        self, user_id: int, question_type: str, user_tone: str, topic_category: str
    ):
        """Update interaction history in database"""

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO personality_interactions 
                    (user_id, interaction_type, user_tone, topic_category, response_style, effectiveness_score, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        user_id,
                        question_type,
                        user_tone,
                        topic_category,
                        "adaptive",
                        0.8,
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                conn.commit()

        except Exception as e:
            logger.error(f"Failed to update interaction history: {e}")

    async def adapt_personality_to_user(
        self, user_id: int, user_feedback: str, interaction_success: bool
    ):
        """Adapt personality based on user feedback and interaction success"""

        if user_id not in self.user_personalities:
            return

        personality = self.user_personalities[user_id]

        # Adjust traits based on success
        if interaction_success:
            # Reinforce current settings
            pass
        else:
            # Adjust traits
            if "too formal" in user_feedback.lower():
                personality.formality = max(0.1, personality.formality - 0.1)
            elif "too casual" in user_feedback.lower():
                personality.formality = min(0.9, personality.formality + 0.1)

            if "too long" in user_feedback.lower():
                personality.verbosity = max(0.2, personality.verbosity - 0.1)
            elif "too short" in user_feedback.lower():
                personality.verbosity = min(0.9, personality.verbosity + 0.1)

    def get_personality_summary(self) -> Dict[str, Any]:
        """Get summary of current personality configuration"""

        return {
            "identity": {
                "name": self.identity.name,
                "version": self.identity.version,
                "creator": self.identity.creator_name,
                "launch_date": self.identity.official_launch,
                "mission": self.identity.mission,
            },
            "core_traits": {
                "adaptability": self.base_personality.adaptability,
                "curiosity": self.base_personality.curiosity,
                "intellect": self.base_personality.intellect,
                "empathy": self.base_personality.empathy,
                "integrity": self.base_personality.integrity,
                "humility": self.base_personality.humility,
            },
            "active_users": len(self.user_contexts),
            "adaptation_count": len(self.user_personalities),
        }


# Global personality core instance
_personality_core: Optional[PersonalityCore] = None


def get_personality_core() -> Optional[PersonalityCore]:
    """Get the global personality core instance"""
    return _personality_core


def initialize_personality_core(db_path: Path = None) -> PersonalityCore:
    """Initialize the global personality core"""
    global _personality_core
    _personality_core = PersonalityCore(db_path)
    return _personality_core


# Integration functions for existing AI systems
async def enhance_ai_response_with_personality(
    user_id: int, original_response: str, context: Dict[str, Any]
) -> str:
    """Enhance AI response with personality-aware adaptations"""

    core = get_personality_core()
    if not core:
        return original_response

    # Get user's personality adaptation
    personality = await core._get_user_personality(user_id)
    user_context = core.user_contexts.get(user_id)

    if not user_context:
        return original_response

    # Apply personality-based modifications
    enhanced_response = original_response

    # Adjust formality
    if personality.formality < 0.4:
        enhanced_response = enhanced_response.replace("I am", "I'm")
        enhanced_response = enhanced_response.replace("I have", "I've")
        enhanced_response = enhanced_response.replace("I would", "I'd")

    # Adjust expressiveness
    if personality.expressiveness > 0.7 and user_context.user_tone in [
        "excited",
        "happy",
    ]:
        if not any(emoji in enhanced_response for emoji in ["🌟", "✨", "🚀"]):
            emojis = ["🌟", "✨", "🚀", "💫"]
            enhanced_response += f" {random.choice(emojis)}"

    return enhanced_response
