"""
Core AI Handler - Streamlined AI Processing
Handles all AI interactions without bloat - Maximum 300 lines
"""

import asyncio
import logging
import time
from typing import Dict, Optional, Any
import discord
from discord.ext import commands

logger = logging.getLogger("astra.core.ai")


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
        """Determine if bot should respond to this message"""
        content = message.content.lower()

        # Always respond to mentions
        if self.bot.user.mentioned_in(message):
            return True

        # Respond to questions
        if "?" in content or any(
            word in content for word in ["astra", "hey", "hello", "help"]
        ):
            return True

        # Respond in DMs
        if isinstance(message.channel, discord.DMChannel):
            return True

        return False

    async def _generate_response(self, message: discord.Message) -> str:
        """Generate AI response using the consolidated engine"""
        if not self.ai_engine:
            return await self._get_fallback_response(message)

        try:
            # Get conversation context
            user_id = message.author.id
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []

            # Add timeout protection
            ai_response = await asyncio.wait_for(
                self.ai_engine.generate_response(message.content), timeout=15.0
            )
            response = (
                ai_response.content
                if ai_response.success
                else "I'm having trouble processing that. Could you try again?"
            )

            # Update conversation history
            self.conversation_history[user_id].append(
                {
                    "user": message.content[:200],
                    "bot": response[:200],
                    "timestamp": time.time(),
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
            return await self._get_fallback_response(message)
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            return await self._get_fallback_response(message)

    async def _get_fallback_response(self, message: discord.Message) -> str:
        """Smart fallback responses when AI is unavailable"""
        content = message.content.lower()

        if "hello" in content or "hi" in content:
            return "Hey there! I'm Astra, ready to help! 👋"
        elif "?" in content:
            return "That's a great question! I'm processing... 🤔"
        elif "help" in content:
            return "I'm here to help! What do you need assistance with? 🚀"
        elif "thanks" in content:
            return "You're welcome! Happy to help! ✨"
        else:
            return "I'm here and listening! What's on your mind? 🌟"

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
