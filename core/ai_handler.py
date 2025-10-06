"""
Core AI Handler - Streamlined AI Processing
Handles all AI interactions without bloat - Maximum 300 lines
"""

import asyncio
import logging
import time
import re
from typing import Dict, Optional, Any
import discord
from discord.ext import commands

logger = logging.getLogger("astra.core.ai")

# Import personality integration
try:
    from ai.personality_integration import (
        check_for_identity_response,
        enhance_ai_chat_response,
        get_personality_integration,
    )

    PERSONALITY_INTEGRATION_AVAILABLE = True
    logger.info("✅ Personality Integration imported successfully")
except ImportError as e:
    logger.warning(f"❌ Personality Integration not available: {e}")
    PERSONALITY_INTEGRATION_AVAILABLE = False

# Language detection patterns
LANGUAGE_PATTERNS = {
    "arabic": re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+"),
    "french": re.compile(
        r"\b(qui|est|vous|que|comment|où|quand|pourquoi|êtes|bonjour|salut|merci)\b",
        re.IGNORECASE,
    ),
    "german": re.compile(
        r"\b(wer|ist|sind|was|wie|wo|wann|warum|hallo|danke|bitte)\b", re.IGNORECASE
    ),
    "spanish": re.compile(
        r"\b(quién|es|son|qué|cómo|dónde|cuándo|por qué|hola|gracias|por favor)\b",
        re.IGNORECASE,
    ),
    "italian": re.compile(
        r"\b(chi|è|sono|cosa|come|dove|quando|perché|ciao|grazie|prego)\b",
        re.IGNORECASE,
    ),
}


def detect_language(text: str) -> str:
    """Detect the language of the input text"""
    text_lower = text.lower()

    # Check for Arabic script
    if LANGUAGE_PATTERNS["arabic"].search(text):
        return "arabic"

    # Check other languages by keywords
    for lang, pattern in LANGUAGE_PATTERNS.items():
        if lang != "arabic" and pattern.search(text_lower):
            return lang

    # Default to English
    return "english"


class AIHandler:
    """Streamlined AI processing - no bloat, pure functionality"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ai_engine = None
        self.response_cache = {}
        self.conversation_history = {}

        # Initialize AI engine
        asyncio.create_task(self._initialize_ai())

    async def _initialize_ai(self):
        """Initialize AI engine connection"""
        try:
            from ai.multi_provider_ai import MultiProviderAIManager

            self.ai_engine = MultiProviderAIManager()
            logger.info("✅ AI Handler initialized with Multi-Provider AI Manager")
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI engine: {e}")

    async def process_message(self, message: discord.Message) -> Optional[str]:
        """
        Process message and generate AI response if needed
        Returns None if no response should be sent
        """
        if not message.content or message.author.bot:
            return None

        # Check if bot should respond (mentions, questions, etc.)
        should_respond = await self._should_respond(message)
        if not should_respond:
            return None

        # Generate AI response
        try:
            response = await self._generate_response(message)
            return response
        except Exception as e:
            logger.error(f"AI response error: {e}")
            return "I'm having a brief moment of digital confusion! Try again? 🤖"

    async def _should_respond(self, message: discord.Message) -> bool:
        """Determine if bot should respond to this message with enhanced identity question detection"""
        content = message.content.lower()

        # Always respond to mentions
        if self.bot.user.mentioned_in(message):
            return True

        # Respond in DMs
        if isinstance(message.channel, discord.DMChannel):
            return True

        # PRIORITY: Always respond to identity questions in any language
        identity_patterns = [
            # English
            "who are you",
            "what are you",
            "who created you",
            "who made you",
            "what can you do",
            "what are you capable of",
            "astra who are you",
            "astra what can you do",
            "astra what are you capable of",
            # Arabic
            "من أنت",
            "ما أنت",
            "من صنعك",
            "من خلقك",
            "ماذا تستطيع أن تفعل",
            # French
            "qui êtes-vous",
            "qui es-tu",
            "qui vous a créé",
            "que pouvez-vous faire",
            # German
            "wer bist du",
            "wer sind sie",
            "wer hat dich gemacht",
            "was kannst du",
            # Spanish
            "quién eres",
            "qué eres",
            "quién te creó",
            "qué puedes hacer",
        ]

        for pattern in identity_patterns:
            if pattern in content:
                return True

        # Respond to questions
        if "?" in content:
            return True

        # Respond to greetings and bot name mentions
        if any(
            word in content
            for word in [
                "astra",
                "hey",
                "hello",
                "help",
                "hi",
                "مرحبا",
                "salut",
                "bonjour",
                "hallo",
                "hola",
            ]
        ):
            return True

        return False

    async def _generate_response(self, message: discord.Message) -> str:
        """Generate AI response using personality integration and language detection"""
        # PRIORITY: Check for identity questions first using personality system
        if PERSONALITY_INTEGRATION_AVAILABLE:
            try:
                channel_context = getattr(message.channel, "name", "general")
                personality_response = await check_for_identity_response(
                    user_id=message.author.id,
                    message=message.content,
                    user_name=str(message.author),
                    channel_context=channel_context,
                )

                if personality_response:
                    logger.info(
                        f"🎭 Personality response generated for identity question"
                    )
                    return personality_response
            except Exception as e:
                logger.error(f"Personality integration error: {e}")

        # Detect language for multilingual support
        detected_language = detect_language(message.content)

        if not self.ai_engine:
            return await self._get_fallback_response(message, detected_language)

        try:
            # Get conversation context
            user_id = message.author.id
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []

            # Enhance prompt with personality context and language awareness
            enhanced_prompt = message.content
            if PERSONALITY_INTEGRATION_AVAILABLE:
                try:
                    enhanced_prompt = await enhance_ai_chat_response(
                        original_message=message.content,
                        user_id=user_id,
                        user_name=str(message.author),
                        conversation_history=self.conversation_history.get(user_id, []),
                    )
                except Exception as e:
                    logger.error(f"Response enhancement error: {e}")

            # Add language context to the prompt
            if detected_language != "english":
                language_names = {
                    "arabic": "Arabic",
                    "french": "French",
                    "german": "German",
                    "spanish": "Spanish",
                    "italian": "Italian",
                }
                lang_name = language_names.get(
                    detected_language, detected_language.title()
                )
                enhanced_prompt = f"User is communicating in {lang_name}. Please respond naturally in {lang_name}. {enhanced_prompt}"

            # Add timeout protection
            ai_response = await asyncio.wait_for(
                self.ai_engine.generate_response(enhanced_prompt), timeout=15.0
            )
            response = (
                ai_response.content
                if ai_response.success
                else await self._get_fallback_response(message, detected_language)
            )

            # Update conversation history
            self.conversation_history[user_id].append(
                {
                    "user": message.content[:200],
                    "bot": response[:200],
                    "timestamp": time.time(),
                    "language": detected_language,
                }
            )

            # Keep history manageable
            if len(self.conversation_history[user_id]) > 10:
                self.conversation_history[user_id] = self.conversation_history[user_id][
                    -5:
                ]

            return response

        except asyncio.TimeoutError:
            logger.warning("AI response timeout - using fallback")
            return await self._get_fallback_response(message, detected_language)
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            return await self._get_fallback_response(message, detected_language)

    async def _get_fallback_response(
        self, message: discord.Message, language: str = "english"
    ) -> str:
        """Smart fallback responses with multi-language support"""
        content = message.content.lower()

        # Multi-language fallback responses
        responses = {
            "english": {
                "greeting": "Hey there! I'm Astra, your AI companion created by <@7zxk>! Ready to help! 👋",
                "question": "That's a great question! I'm processing... 🤔",
                "help": "I'm here to help! What do you need assistance with? 🚀",
                "thanks": "You're welcome! Happy to help! ✨",
                "who": "I'm Astra, an advanced AI companion created by <@7zxk>! I'm here to help with anything you need! 🌟",
                "default": "I'm here and listening! What's on your mind? 🌟",
            },
            "arabic": {
                "greeting": "مرحباً! أنا أسترا، مساعدك الذكي الذي أنشأه <@7zxk>! مستعد للمساعدة! 👋",
                "question": "هذا سؤال رائع! أنا أعالج الأمر... 🤔",
                "help": "أنا هنا للمساعدة! بماذا تحتاج المساعدة؟ 🚀",
                "thanks": "على الرحب والسعة! سعيد بالمساعدة! ✨",
                "who": "أنا أسترا، مساعد ذكي متطور أنشأه <@7zxk>! أنا هنا لمساعدتك في أي شيء تحتاجه! 🌟",
                "default": "أنا هنا وأستمع! ما الذي يدور في ذهنك؟ 🌟",
            },
            "french": {
                "greeting": "Salut ! Je suis Astra, votre compagnon IA créé par <@7zxk> ! Prêt à aider ! 👋",
                "question": "C'est une excellente question ! Je traite... 🤔",
                "help": "Je suis là pour aider ! De quoi avez-vous besoin ? 🚀",
                "thanks": "De rien ! Heureux d'aider ! ✨",
                "who": "Je suis Astra, un compagnon IA avancé créé par <@7zxk> ! Je suis là pour vous aider ! 🌟",
                "default": "Je suis là et j'écoute ! Qu'avez-vous en tête ? 🌟",
            },
            "german": {
                "greeting": "Hallo! Ich bin Astra, dein KI-Begleiter, erstellt von <@7zxk>! Bereit zu helfen! 👋",
                "question": "Das ist eine großartige Frage! Ich verarbeite... 🤔",
                "help": "Ich bin hier um zu helfen! Womit brauchst du Hilfe? 🚀",
                "thanks": "Gern geschehen! Freue mich zu helfen! ✨",
                "who": "Ich bin Astra, ein fortgeschrittener KI-Begleiter, erstellt von <@7zxk>! Ich bin hier um zu helfen! 🌟",
                "default": "Ich bin hier und höre zu! Was beschäftigt dich? 🌟",
            },
        }

        # Get responses for the detected language, fallback to English
        lang_responses = responses.get(language, responses["english"])

        # Check for identity questions
        if any(
            word in content
            for word in [
                "who are you",
                "what are you",
                "من أنت",
                "qui êtes-vous",
                "wer bist du",
            ]
        ):
            return lang_responses["who"]
        elif any(
            word in content
            for word in ["hello", "hi", "مرحبا", "salut", "bonjour", "hallo"]
        ):
            return lang_responses["greeting"]
        elif "?" in content:
            return lang_responses["question"]
        elif any(word in content for word in ["help", "مساعدة", "aide", "hilfe"]):
            return lang_responses["help"]
        elif any(
            word in content for word in ["thanks", "thank", "شكرا", "merci", "danke"]
        ):
            return lang_responses["thanks"]
        else:
            return lang_responses["default"]

    async def ask_question(
        self, question: str, user_id: int, context: Dict[str, Any] = None
    ) -> str:
        """Direct AI question interface"""
        if not self.ai_engine:
            return "AI services are currently unavailable. Please try again later!"

        try:
            ai_response = await asyncio.wait_for(
                self.ai_engine.generate_response(question),
                timeout=15.0,
            )
            return (
                ai_response.content
                if ai_response.success
                else "I'm having trouble with that question. Please try again later!"
            )
        except asyncio.TimeoutError:
            return "That's a complex question! Let me think about it and get back to you. 🤔"
        except Exception as e:
            logger.error(f"Direct AI question error: {e}")
            return "I'm having trouble processing that question right now. Could you rephrase it?"

    def get_stats(self) -> Dict[str, Any]:
        """Get AI handler statistics"""
        return {
            "ai_engine_available": self.ai_engine is not None,
            "active_conversations": len(self.conversation_history),
            "cache_size": len(self.response_cache),
        }

    async def cleanup(self):
        """Cleanup resources"""
        self.conversation_history.clear()
        self.response_cache.clear()
        logger.info("🧹 AI Handler cleaned up")
