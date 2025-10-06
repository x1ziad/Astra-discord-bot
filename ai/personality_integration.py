"""
🔗 Personality Integration System
Integrates AstraBot's self-aware personality core with existing AI systems

This module provides seamless integration between the personality core and
existing AI chat systems, ensuring natural self-aware responses.
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Any
from ai.bot_personality_core import (
    get_personality_core,
    initialize_personality_core,
    enhance_ai_response_with_personality,
)

logger = logging.getLogger("astra.personality_integration")


class PersonalityIntegration:
    """Manages integration between personality core and AI systems"""

    def __init__(self):
        self.personality_core = None
        self.integration_active = False

    async def initialize(self):
        """Initialize personality integration"""
        try:
            self.personality_core = initialize_personality_core()
            self.integration_active = True
            logger.info("Personality integration initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize personality integration: {e}")
            self.integration_active = False

    async def process_message_for_identity(
        self,
        user_id: int,
        message: str,
        user_name: str = None,
        channel_context: str = "general",
    ) -> Optional[str]:
        """
        Check if message is asking about bot identity and generate appropriate response
        Returns None if not an identity question, otherwise returns personality response
        """

        if not self.integration_active or not self.personality_core:
            return None

        # Detect user tone from message
        user_tone = self._detect_user_tone(message)

        # Determine topic category
        topic_category = self._determine_topic_category(message, channel_context)

        # Check for identity questions and generate response
        response = await self.personality_core.process_identity_question(
            user_id=user_id,
            message=message,
            user_tone=user_tone,
            topic_category=topic_category,
        )

        return response

    def _detect_user_tone(self, message: str) -> str:
        """Detect user's tone from their message"""

        message_lower = message.lower()

        # Excited/enthusiastic tone
        if (
            any(
                indicator in message_lower
                for indicator in [
                    "awesome",
                    "amazing",
                    "wow",
                    "cool",
                    "fantastic",
                    "love",
                ]
            )
            or message.count("!") >= 2
        ):
            return "excited"

        # Formal/professional tone
        if any(
            indicator in message_lower
            for indicator in [
                "please",
                "could you",
                "would you",
                "i would like",
                "kindly",
            ]
        ) and not any(casual in message_lower for casual in ["hey", "yo", "sup"]):
            return "formal"

        # Casual tone
        if any(
            indicator in message_lower
            for indicator in [
                "hey",
                "hi",
                "yo",
                "sup",
                "what's up",
                "wassup",
                "lol",
                "haha",
            ]
        ):
            return "casual"

        # Serious/academic tone
        if any(
            indicator in message_lower
            for indicator in [
                "analyze",
                "explain",
                "describe",
                "define",
                "elaborate",
                "discuss",
            ]
        ):
            return "serious"

        # Uncertain/questioning tone
        if message.count("?") >= 2 or any(
            indicator in message_lower
            for indicator in ["not sure", "confused", "don't understand", "unclear"]
        ):
            return "uncertain"

        return "neutral"

    def _determine_topic_category(self, message: str, channel_context: str) -> str:
        """Determine topic category from message and context"""

        message_lower = message.lower()

        # Science/research topics
        if any(
            keyword in message_lower
            for keyword in [
                "science",
                "research",
                "quantum",
                "physics",
                "astronomy",
                "cosmology",
                "astrophysics",
                "space",
                "universe",
                "stars",
                "galaxies",
            ]
        ):
            return "science"

        # Technical topics
        if any(
            keyword in message_lower
            for keyword in [
                "code",
                "programming",
                "algorithm",
                "technical",
                "system",
                "architecture",
                "database",
                "api",
                "development",
            ]
        ):
            return "technical"

        # Personal/social topics
        if any(
            keyword in message_lower
            for keyword in [
                "feel",
                "think",
                "personal",
                "about you",
                "your life",
                "experience",
            ]
        ):
            return "personal"

        # Channel context influence
        if "science" in channel_context or "research" in channel_context:
            return "science"
        elif "tech" in channel_context or "dev" in channel_context:
            return "technical"

        return "general"

    async def enhance_regular_response(
        self, user_id: int, original_response: str, context: Dict[str, Any] = None
    ) -> str:
        """Enhance regular AI responses with personality awareness"""

        if not self.integration_active or not self.personality_core:
            return original_response

        try:
            enhanced = await enhance_ai_response_with_personality(
                user_id=user_id,
                original_response=original_response,
                context=context or {},
            )
            return enhanced
        except Exception as e:
            logger.error(f"Failed to enhance response with personality: {e}")
            return original_response

    def is_identity_question(self, message: str) -> bool:
        """Enhanced check for identity-related questions in multiple languages"""

        identity_keywords = [
            # English
            "who are you",
            "what are you",
            "who is astra",
            "what is astra",
            "tell me about yourself",
            "introduce yourself",
            "about you",
            "who made you",
            "who created you",
            "your creator",
            "your developer",
            "what can you do",
            "your capabilities",
            "what are you capable of",
            "why were you created",
            "your purpose",
            "your mission",
            "astra who are you",
            "astra what can you do",
            "astra what are you capable of",
            # Arabic
            "من أنت",
            "ما أنت",
            "من صنعك",
            "من خلقك",
            "من طورك",
            "ماذا تستطيع أن تفعل",
            "ما قدراتك",
            "ما إمكانياتك",
            "عرف نفسك",
            "تحدث عن نفسك",
            # French
            "qui êtes-vous",
            "qui es-tu",
            "qu'êtes-vous",
            "que vous êtes",
            "qui vous a créé",
            "qui t'a créé",
            "votre créateur",
            "que pouvez-vous faire",
            "vos capacités",
            "présentez-vous",
            # German
            "wer bist du",
            "wer sind sie",
            "was bist du",
            "was sind sie",
            "wer hat dich gemacht",
            "wer hat dich erstellt",
            "dein schöpfer",
            "was kannst du",
            "deine fähigkeiten",
            "stell dich vor",
            # Spanish
            "quién eres",
            "qué eres",
            "quién te creó",
            "quién te hizo",
            "tu creador",
            "qué puedes hacer",
            "tus capacidades",
            "preséntate",
            # Italian
            "chi sei",
            "cosa sei",
            "chi ti ha creato",
            "chi ti ha fatto",
            "il tuo creatore",
            "cosa puoi fare",
            "le tue capacità",
            "presentati",
        ]

        message_lower = message.lower()
        return any(keyword in message_lower for keyword in identity_keywords)

    async def get_personality_stats(self) -> Dict[str, Any]:
        """Get current personality system statistics"""

        if not self.integration_active or not self.personality_core:
            return {"status": "inactive"}

        return {
            "status": "active",
            "summary": self.personality_core.get_personality_summary(),
            "integration_active": self.integration_active,
        }


# Global integration instance
_personality_integration: Optional[PersonalityIntegration] = None


async def get_personality_integration() -> PersonalityIntegration:
    """Get or create personality integration instance"""
    global _personality_integration

    if _personality_integration is None:
        _personality_integration = PersonalityIntegration()
        await _personality_integration.initialize()

    return _personality_integration


async def check_for_identity_response(
    user_id: int, message: str, user_name: str = None, channel_context: str = "general"
) -> Optional[str]:
    """
    Convenient function to check for identity questions and get responses
    Use this in your existing AI chat systems
    """

    integration = await get_personality_integration()

    if not integration.is_identity_question(message):
        return None

    return await integration.process_message_for_identity(
        user_id=user_id,
        message=message,
        user_name=user_name,
        channel_context=channel_context,
    )


async def enhance_ai_chat_response(
    user_id: int, original_response: str, context: Dict[str, Any] = None
) -> str:
    """
    Enhance any AI response with personality awareness
    Use this to wrap your existing AI responses
    """

    integration = await get_personality_integration()
    return await integration.enhance_regular_response(
        user_id=user_id, original_response=original_response, context=context
    )
