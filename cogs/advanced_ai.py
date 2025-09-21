"""
Advanced AI Cog for Astra Bot
Implements modern AI features with simplified, reliable architecture
"""

import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
import logging
import random
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta, timezone
import json
import re
import os

# Performance optimization imports
from utils.command_optimizer import optimize_command, optimized_send
from utils.performance_optimizer import performance_optimizer

logger = logging.getLogger("astra.advanced_ai")

# Import AI systems with proper error handling
AI_ENGINE_AVAILABLE = False
OPTIMIZED_AI_AVAILABLE = False

try:
    from ai.consolidated_ai_engine import get_engine, initialize_engine

    AI_ENGINE_AVAILABLE = True
    logger.info("✅ Consolidated AI Engine imported successfully")
except ImportError as e:
    logger.warning(f"❌ Consolidated AI Engine not available: {e}")

try:
    from ai.consolidated_ai_engine import ConsolidatedAIEngine as OptimizedAIEngine

    def get_optimized_engine():
        return OptimizedAIEngine()

    OPTIMIZED_AI_AVAILABLE = True
    logger.info("✅ Consolidated AI Engine imported successfully")
except ImportError as e:
    logger.warning(f"❌ Consolidated AI Engine not available: {e}")
    OPTIMIZED_AI_AVAILABLE = False

# Import context manager
try:
    from ai.universal_context_manager import (
        get_context_manager,
        initialize_context_manager,
    )

    CONTEXT_MANAGER_AVAILABLE = True
    logger.info("✅ Universal Context Manager imported successfully")
except ImportError as e:
    logger.warning(f"❌ Universal Context Manager not available: {e}")
    CONTEXT_MANAGER_AVAILABLE = False


class AdvancedAICog(commands.Cog):
    """Advanced AI features with simplified, reliable architecture"""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("astra.advanced_ai")

        # Initialize AI client
        self.ai_client = None
        self._setup_ai_client()

        # Simplified conversation tracking
        self.conversation_history: Dict[int, List[Dict[str, str]]] = {}
        self.conversation_cooldowns: Dict[int, datetime] = {}
        self.max_history_length = 5

        # Performance tracking
        self.api_calls_made = 0
        self.successful_responses = 0
        self.start_time = datetime.now(timezone.utc)

        # Start essential background tasks only
        if self.ai_client:
            self.conversation_cleanup_task.start()
            self.logger.info("✅ Advanced AI Cog initialized successfully")
        else:
            self.logger.error(
                "❌ Advanced AI Cog failed to initialize - no AI client available"
            )

    def _setup_ai_client(self):
        """Setup AI engine with fallback options"""
        try:
            # Try optimized engine first
            if OPTIMIZED_AI_AVAILABLE:
                self.ai_client = get_optimized_engine()
                if self.ai_client:
                    self.logger.info("✅ Using Optimized AI Engine")
                    return

            # Fallback to consolidated engine
            if AI_ENGINE_AVAILABLE:
                self.ai_client = get_engine()
                if self.ai_client:
                    self.logger.info("✅ Using Consolidated AI Engine")
                    return

            # Initialize engine if not available
            try:
                self.ai_client = initialize_engine(
                    {
                        "ai_api_key": os.getenv("AI_API_KEY"),
                        "ai_model": os.getenv("AI_MODEL", "deepseek/deepseek-r1:nitro"),
                        "openrouter_api_key": os.getenv("OPENROUTER_API_KEY"),
                    }
                )
                if self.ai_client:
                    self.logger.info("✅ Initialized new AI Engine")
                    return
            except Exception as e:
                self.logger.error(f"Failed to initialize AI engine: {e}")

            self.logger.error("❌ No AI Engine available!")
            self.ai_client = None

        except Exception as e:
            self.logger.error(f"Failed to setup AI client: {e}")
            self.ai_client = None

    async def _generate_ai_response(
        self,
        prompt: str,
        user_id: int = None,
        guild_id: int = None,
        channel_id: int = None,
        username: str = None,
    ) -> str:
        """Generate AI response with simplified error handling"""
        try:
            if not self.ai_client:
                return (
                    "❌ AI service is not configured. Please check the configuration."
                )

            # Get conversation history
            history = self.conversation_history.get(user_id, [])

            # Generate response using available AI engine
            if hasattr(self.ai_client, "process_conversation"):
                response = await self.ai_client.process_conversation(
                    prompt, user_id, guild_id=guild_id, channel_id=channel_id
                )
            elif hasattr(self.ai_client, "generate_response"):
                response = await self.ai_client.generate_response(
                    prompt, context={"history": history}
                )
            else:
                # Fallback for basic AI clients
                response = "I'm here to help! However, my AI capabilities are currently limited."

            # Update conversation history
            if user_id and response:
                if user_id not in self.conversation_history:
                    self.conversation_history[user_id] = []

                self.conversation_history[user_id].append(
                    {"role": "user", "content": prompt}
                )
                self.conversation_history[user_id].append(
                    {"role": "assistant", "content": response}
                )

                # Keep only recent messages
                if (
                    len(self.conversation_history[user_id])
                    > self.max_history_length * 2
                ):
                    self.conversation_history[user_id] = self.conversation_history[
                        user_id
                    ][-self.max_history_length * 2 :]

            self.api_calls_made += 1
            self.successful_responses += 1

            return response

        except Exception as e:
            self.logger.error(f"AI response generation error: {e}")
            return f"❌ I'm having trouble thinking right now. Please try again in a moment."

    @app_commands.command(name="chat", description="Chat with Astra AI")
    @app_commands.describe(message="Your message to the AI")
    @optimize_command(rate_limit_enabled=True, rate_limit_per_minute=20)
    async def chat_command(self, interaction: discord.Interaction, message: str):
        """Chat with AI assistant - Optimized for performance"""
        try:
            await interaction.response.defer()

            if not self.ai_client:
                await interaction.followup.send(
                    "❌ AI service is not available. Please try again later.",
                    ephemeral=True,
                )
                return

            # Optimize AI request
            guild_id = interaction.guild.id if interaction.guild else None
            optimized_prompt, metadata = (
                await performance_optimizer.ai_optimizer.optimize_ai_request(
                    message, interaction.user.id, guild_id
                )
            )

            # Generate AI response with optimization
            response = await self._generate_ai_response(
                optimized_prompt,
                interaction.user.id,
                guild_id=guild_id,
                channel_id=interaction.channel.id,
                username=str(interaction.user),
            )

            # Cache the response
            await performance_optimizer.ai_optimizer.cache_response(
                message, response, guild_id, metadata
            )

            # Create optimized embed
            embed = discord.Embed(
                title="🤖 Astra AI Chat",
                description=response[:4000],  # Ensure it fits in embed
                color=0x7289DA,
                timestamp=datetime.now(timezone.utc),
            )
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url,
            )

            # Add user message as field
            message_preview = message[:1000] + ("..." if len(message) > 1000 else "")
            embed.add_field(
                name="💬 Your Message",
                value=message_preview,
                inline=False,
            )

            # Add optimization info for debugging
            if metadata.get("optimization_applied"):
                embed.set_footer(
                    text=f"⚡ Optimized • Model: {metadata.get('model_selected', 'default')}"
                )

            await optimized_send(interaction.followup, embed=embed)

        except Exception as e:
            self.logger.error(f"Chat command error: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"❌ Error processing chat request: {str(e)}", ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"❌ Error processing chat request: {str(e)}", ephemeral=True
                )

    @app_commands.command(name="analyze", description="Analyze text or content with AI")
    @app_commands.describe(content="Content to analyze")
    async def analyze_command(self, interaction: discord.Interaction, content: str):
        """Analyze content with AI"""
        try:
            await interaction.response.defer()

            if not self.ai_client:
                await interaction.followup.send(
                    "❌ AI service is not available. Please try again later.",
                    ephemeral=True,
                )
                return

            analysis_prompt = f"Please analyze the following content and provide insights, key points, and summary:\n\n{content}"
            response = await self._generate_ai_response(
                analysis_prompt, interaction.user.id
            )

            embed = discord.Embed(
                title="🔍 AI Content Analysis",
                description=response[:4000],
                color=0x7289DA,
                timestamp=datetime.now(timezone.utc),
            )

            content_preview = content[:500] + ("..." if len(content) > 500 else "")
            embed.add_field(
                name="📝 Analyzed Content",
                value=content_preview,
                inline=False,
            )
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Analysis command error: {e}")
            await interaction.followup.send(
                f"❌ Error analyzing content: {str(e)}", ephemeral=True
            )

    @app_commands.command(name="summarize", description="Summarize long text with AI")
    @app_commands.describe(content="Content to summarize")
    async def summarize_command(self, interaction: discord.Interaction, content: str):
        """Summarize content with AI"""
        try:
            await interaction.response.defer()

            if not self.ai_client:
                await interaction.followup.send(
                    "❌ AI service is not available. Please try again later.",
                    ephemeral=True,
                )
                return

            summarize_prompt = f"Please provide a concise summary of the following content:\n\n{content}"
            response = await self._generate_ai_response(
                summarize_prompt, interaction.user.id
            )

            embed = discord.Embed(
                title="📋 AI Summary",
                description=response[:4000],
                color=0x7289DA,
                timestamp=datetime.now(timezone.utc),
            )

            content_preview = content[:500] + ("..." if len(content) > 500 else "")
            embed.add_field(
                name="📄 Original Content",
                value=content_preview,
                inline=False,
            )
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Summarize command error: {e}")
            await interaction.followup.send(
                f"❌ Error summarizing content: {str(e)}", ephemeral=True
            )

    @app_commands.command(
        name="translate", description="Translate text to another language"
    )
    @app_commands.describe(
        text="Text to translate",
        target_language="Target language (e.g., Spanish, French, German)",
    )
    async def translate_command(
        self, interaction: discord.Interaction, text: str, target_language: str
    ):
        """Translate text using AI"""
        try:
            await interaction.response.defer()

            if not self.ai_client:
                await interaction.followup.send(
                    "❌ AI service is not available. Please try again later.",
                    ephemeral=True,
                )
                return

            translate_prompt = (
                f"Translate the following text to {target_language}:\n\n{text}"
            )
            response = await self._generate_ai_response(
                translate_prompt, interaction.user.id
            )

            embed = discord.Embed(
                title="🌐 AI Translation",
                color=0x7289DA,
                timestamp=datetime.now(timezone.utc),
            )

            text_preview = text[:500] + ("..." if len(text) > 500 else "")
            embed.add_field(
                name="📝 Original Text",
                value=text_preview,
                inline=False,
            )
            embed.add_field(
                name=f"🔄 Translation ({target_language})",
                value=response[:1000] + ("..." if len(response) > 1000 else ""),
                inline=False,
            )
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Translation command error: {e}")
            await interaction.followup.send(
                f"❌ Error translating text: {str(e)}", ephemeral=True
            )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Sophisticated Universal Message Interaction System - Observes ALL messages and responds intelligently"""
        if message.author.bot:
            return

        # Skip if this was a command to avoid double processing
        if message.content.startswith(
            tuple(await self.bot._get_dynamic_prefix(self.bot, message))
        ):
            return

        try:
            # UNIVERSAL MESSAGE ANALYSIS - Process every single message
            await self._analyze_message_for_context(message)
            
            # SOPHISTICATED INTERACTION DECISION ENGINE
            interaction_decision = await self._determine_interaction_type(message)
            
            # EXECUTE INTERACTION BASED ON DECISION
            if interaction_decision["should_interact"]:
                await self._execute_sophisticated_interaction(message, interaction_decision)

        except Exception as e:
            self.logger.error(f"Error in sophisticated message processing: {e}")

    async def _determine_interaction_type(self, message: discord.Message) -> Dict[str, Any]:
        """🧠 SOPHISTICATED INTERACTION DECISION ENGINE - Determines how to interact with each message"""
        try:
            user_id = message.author.id
            content_lower = message.content.lower()
            
            # Initialize interaction decision
            decision = {
                "should_interact": False,
                "interaction_type": "none",
                "confidence": 0.0,
                "response_method": "text",  # text, reaction, emoji, multi
                "urgency": "normal",  # low, normal, high, urgent
                "emotional_tone": "neutral",
                "suggested_reactions": [],
                "suggested_emojis": [],
                "should_reply": False,
                "priority_level": 0
            }
            
            # COOLDOWN CHECK with sophisticated timing
            if user_id in self.conversation_cooldowns:
                time_since_last = datetime.now(timezone.utc) - self.conversation_cooldowns[user_id]
                if time_since_last < timedelta(seconds=2):  # Very short cooldown for reactions/emojis
                    if time_since_last < timedelta(seconds=1):
                        return decision  # Too recent, skip
                    else:
                        # Allow reactions/emojis but not full responses
                        decision["response_method"] = "reaction"
            
            # 🎯 PRIORITY INTERACTION TRIGGERS (Always respond)
            
            # 1. DIRECT MENTIONS (Highest Priority)
            if self.bot.user in message.mentions:
                decision.update({
                    "should_interact": True,
                    "interaction_type": "direct_mention",
                    "confidence": 0.95,
                    "response_method": "text",
                    "priority_level": 10,
                    "should_reply": True
                })
                return decision
            
            # 2. DIRECT MESSAGES (Highest Priority)
            if isinstance(message.channel, discord.DMChannel):
                decision.update({
                    "should_interact": True,
                    "interaction_type": "direct_message",
                    "confidence": 0.95,
                    "response_method": "text",
                    "priority_level": 10,
                    "should_reply": True
                })
                return decision
            
            # 3. BOT NAME MENTIONS (High Priority)
            bot_indicators = ["astra", "hey bot", "ai help", "bot help", "hey ai", "hello astra", "hi astra"]
            for indicator in bot_indicators:
                if indicator in content_lower:
                    decision.update({
                        "should_interact": True,
                        "interaction_type": "name_mention",
                        "confidence": 0.9,
                        "response_method": "text",
                        "priority_level": 9,
                        "should_reply": True
                    })
                    return decision
            
            # 🚨 HELP AND URGENT REQUESTS (High Priority)
            help_urgent_indicators = [
                "help", "emergency", "urgent", "asap", "quickly", "immediately", 
                "stuck", "confused", "lost", "don't understand", "can't figure",
                "need assistance", "support", "please help", "anyone help"
            ]
            for indicator in help_urgent_indicators:
                if indicator in content_lower:
                    decision.update({
                        "should_interact": True,
                        "interaction_type": "help_request",
                        "confidence": 0.85,
                        "response_method": "text",
                        "urgency": "high",
                        "priority_level": 8,
                        "should_reply": True
                    })
                    return decision
            
            # 💬 QUESTIONS AND COMMUNITY ENGAGEMENT (Medium-High Priority)
            if "?" in message.content and len(message.content) > 10:
                question_indicators = [
                    "what", "how", "why", "where", "when", "who", "which",
                    "anyone", "somebody", "someone", "does anyone", "has anyone",
                    "thoughts", "opinions", "advice", "recommend", "suggest"
                ]
                for indicator in question_indicators:
                    if indicator in content_lower:
                        decision.update({
                            "should_interact": True,
                            "interaction_type": "community_question",
                            "confidence": 0.75,
                            "response_method": "text",
                            "priority_level": 7,
                            "should_reply": True
                        })
                        return decision
            
            # 🎭 EMOTIONAL EXPRESSION DETECTION (Medium Priority - React with emojis)
            emotional_expressions = {
                "excited": ["amazing", "awesome", "incredible", "fantastic", "wow", "omg", "excited", "🎉", "🔥", "⚡"],
                "happy": ["happy", "joy", "great", "wonderful", "perfect", "love", "😊", "😄", "🥰", "❤️"],
                "sad": ["sad", "depressed", "down", "upset", "crying", "😢", "😭", "💔", "😞"],
                "angry": ["angry", "mad", "furious", "rage", "annoyed", "😡", "🤬", "😤"],
                "confused": ["confused", "lost", "puzzled", "wtf", "what", "huh", "🤔", "😕", "❓"],
                "celebration": ["celebrate", "party", "achievement", "success", "win", "won", "🎉", "🎊", "🥳", "🏆"]
            }
            
            for emotion, indicators in emotional_expressions.items():
                for indicator in indicators:
                    if indicator in content_lower:
                        decision.update({
                            "should_interact": True,
                            "interaction_type": "emotional_response",
                            "confidence": 0.6,
                            "response_method": "emoji" if len(message.content) < 50 else "multi",
                            "emotional_tone": emotion,
                            "priority_level": 5,
                            "suggested_emojis": self._get_emotion_emojis(emotion)
                        })
                        return decision
            
            # 📚 COMPLEX TOPICS AND DISCUSSIONS (Medium Priority)
            complex_topics = [
                "technology", "science", "programming", "development", "ai", "machine learning",
                "philosophy", "research", "innovation", "future", "analysis", "discussion",
                "debate", "strategy", "solution", "problem", "learning", "education"
            ]
            
            for topic in complex_topics:
                if topic in content_lower and len(message.content) > 30:
                    import random
                    if random.random() < 0.4:  # 40% chance for complex topics
                        decision.update({
                            "should_interact": True,
                            "interaction_type": "complex_topic",
                            "confidence": 0.4,
                            "response_method": "text",
                            "priority_level": 4,
                            "should_reply": True
                        })
                        return decision
            
            # 🎯 CONVERSATION CONTINUITY (Medium Priority)
            recent_history = self.conversation_history.get(user_id, [])
            if recent_history:
                last_interaction = recent_history[-1].get("timestamp")
                if last_interaction:
                    last_time = datetime.fromisoformat(last_interaction)
                    if (datetime.now(timezone.utc) - last_time).total_seconds() < 1800:  # 30 minutes
                        if len(message.content) > 20:
                            decision.update({
                                "should_interact": True,
                                "interaction_type": "conversation_continuity",
                                "confidence": 0.5,
                                "response_method": "text",
                                "priority_level": 3,
                                "should_reply": True
                            })
                            return decision
            
            # 🎲 SMART ENGAGEMENT FOR COMMUNITY BUILDING (Low Priority)
            if len(message.content) > 50:
                import random
                engagement_chance = 0.15 if len(message.content) > 100 else 0.08
                
                if random.random() < engagement_chance:
                    decision.update({
                        "should_interact": True,
                        "interaction_type": "community_building",
                        "confidence": 0.3,
                        "response_method": "reaction" if random.random() < 0.6 else "text",
                        "priority_level": 2,
                        "suggested_reactions": ["👍", "🤔", "💯", "🔥"]
                    })
                    return decision
            
            # 🎉 POSITIVE REACTIONS (Low Priority - Just react)
            positive_indicators = ["thanks", "thank you", "good job", "well done", "nice", "cool"]
            for indicator in positive_indicators:
                if indicator in content_lower:
                    decision.update({
                        "should_interact": True,
                        "interaction_type": "positive_acknowledgment",
                        "confidence": 0.4,
                        "response_method": "reaction",
                        "priority_level": 1,
                        "suggested_reactions": ["👍", "😊", "❤️", "🙏"]
                    })
                    return decision
            
            return decision
            
        except Exception as e:
            self.logger.error(f"Error in interaction decision engine: {e}")
            return {"should_interact": False, "interaction_type": "error", "confidence": 0.0}

    def _get_emotion_emojis(self, emotion: str) -> List[str]:
        """Get appropriate emojis for emotional responses"""
        emoji_map = {
            "excited": ["🎉", "🔥", "⚡", "🚀", "💥", "✨"],
            "happy": ["😊", "😄", "🥰", "❤️", "🌟", "☀️"],
            "sad": ["😢", "🥺", "💙", "🫂", "🌧️"],
            "angry": ["😤", "💪", "🌋"],
            "confused": ["🤔", "❓", "🧐", "💭"],
            "celebration": ["🎉", "🎊", "🥳", "🏆", "👏", "🙌"]
        }
        return emoji_map.get(emotion, ["👍", "😊"])

    async def _execute_sophisticated_interaction(self, message: discord.Message, decision: Dict[str, Any]):
        """🚀 SOPHISTICATED INTERACTION EXECUTOR - Executes the determined interaction"""
        try:
            interaction_type = decision["interaction_type"]
            response_method = decision["response_method"]
            
            self.logger.info(f"Executing {interaction_type} interaction via {response_method} (confidence: {decision['confidence']:.2f})")
            
            # 1. REACTION-BASED INTERACTIONS
            if response_method == "reaction":
                reactions = decision.get("suggested_reactions", ["👍"])
                for reaction in reactions[:2]:  # Max 2 reactions to avoid spam
                    try:
                        await message.add_reaction(reaction)
                        await asyncio.sleep(0.5)  # Small delay between reactions
                    except discord.HTTPException:
                        continue  # Skip if reaction fails
                
                # Update cooldown for reactions (shorter than text responses)
                self.conversation_cooldowns[message.author.id] = datetime.now(timezone.utc)
                return
            
            # 2. EMOJI-BASED INTERACTIONS
            elif response_method == "emoji":
                emojis = decision.get("suggested_emojis", ["😊"])
                emoji_response = " ".join(emojis[:3])  # Max 3 emojis
                
                try:
                    await message.channel.send(emoji_response)
                except discord.HTTPException:
                    # Fallback to reaction if sending fails
                    await message.add_reaction(emojis[0])
                
                self.conversation_cooldowns[message.author.id] = datetime.now(timezone.utc)
                return
            
            # 3. MULTI-METHOD INTERACTIONS (Reaction + Text/Emoji)
            elif response_method == "multi":
                # First add a reaction
                reactions = decision.get("suggested_reactions", ["🤔"])
                try:
                    await message.add_reaction(reactions[0])
                except discord.HTTPException:
                    pass
                
                # Then send appropriate response
                if decision.get("should_reply", False):
                    await self._process_ai_conversation_enhanced(message)
                else:
                    emojis = decision.get("suggested_emojis", ["😊"])
                    await message.channel.send(" ".join(emojis[:2]))
                
                self.conversation_cooldowns[message.author.id] = datetime.now(timezone.utc)
                return
            
            # 4. TEXT-BASED INTERACTIONS (Full AI Response)
            elif response_method == "text" and decision.get("should_reply", False):
                await self._process_ai_conversation_enhanced(message, decision)
                self.conversation_cooldowns[message.author.id] = datetime.now(timezone.utc)
                return
            
            # 5. CONTEXTUAL SMART REACTIONS
            else:
                # Intelligent contextual reaction based on message content
                smart_reaction = self._determine_smart_reaction(message.content)
                if smart_reaction:
                    try:
                        await message.add_reaction(smart_reaction)
                    except discord.HTTPException:
                        pass
                
                self.conversation_cooldowns[message.author.id] = datetime.now(timezone.utc)
            
        except Exception as e:
            self.logger.error(f"Error executing sophisticated interaction: {e}")

    def _determine_smart_reaction(self, content: str) -> str:
        """Determine smart contextual reaction based on message content"""
        content_lower = content.lower()
        
        # Smart reaction mapping
        reaction_map = {
            # Programming & Tech
            ("code", "programming", "python", "javascript", "tech"): "💻",
            ("bug", "error", "crash", "broken"): "🐛",
            ("deploy", "release", "launch", "ship"): "🚀",
            
            # Emotions & Celebrations
            ("birthday", "anniversary", "celebration"): "🎉",
            ("achievement", "success", "completed", "finished"): "🏆",
            ("love", "heart", "romantic"): "❤️",
            ("funny", "haha", "lol", "joke"): "😂",
            
            # Activities & Interests
            ("food", "cooking", "recipe", "eat"): "🍕",
            ("music", "song", "artist", "album"): "🎵",
            ("game", "gaming", "play", "level"): "🎮",
            ("travel", "vacation", "trip", "holiday"): "✈️",
            ("book", "reading", "novel", "story"): "📚",
            
            # General Positive
            ("good", "great", "awesome", "amazing"): "👍",
            ("thank", "thanks", "grateful"): "🙏",
            ("question", "help", "how", "what"): "🤔",
            ("fire", "hot", "lit", "cool"): "🔥"
        }
        
        for keywords, emoji in reaction_map.items():
            if any(keyword in content_lower for keyword in keywords):
                return emoji
        
        # Default reactions for different message lengths
        if len(content) > 200:
            return "📖"  # Long message
        elif "?" in content:
            return "🤔"  # Question
        else:
            return "👀"  # General attention

    async def _analyze_message_for_context(self, message: discord.Message):
        """Analyze every message for context building, regardless of response"""
        try:
            user_id = message.author.id

            # Update conversation history for context
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []

            # Add message to history
            self.conversation_history[user_id].append(
                {
                    "role": "user",
                    "content": message.content,
                    "timestamp": message.created_at.isoformat(),
                    "channel_id": message.channel.id,
                    "guild_id": message.guild.id if message.guild else None,
                    "has_mentions": len(message.mentions) > 0,
                    "is_question": "?" in message.content,
                    "length": len(message.content),
                }
            )

            # Keep reasonable history length
            if len(self.conversation_history[user_id]) > self.max_history_length * 3:
                self.conversation_history[user_id] = self.conversation_history[user_id][
                    -self.max_history_length * 2 :
                ]

            # Extract important information for long-term memory
            if self.ai_client and hasattr(self.ai_client, "_extract_important_facts"):
                try:
                    # This would store important facts for later use
                    facts = self.ai_client._extract_important_facts(
                        message.content, "", user_id
                    )
                    if facts:
                        self.logger.debug(
                            f"Extracted {len(facts)} facts from user {user_id}"
                        )
                except Exception as e:
                    self.logger.debug(f"Fact extraction failed: {e}")

        except Exception as e:
            self.logger.error(f"Error analyzing message context: {e}")

    async def _should_ai_respond_enhanced(self, message: discord.Message) -> bool:
        """Enhanced AI response determination with better context awareness"""
        user_id = message.author.id
        content_lower = message.content.lower()

        # Check cooldown
        if user_id in self.conversation_cooldowns:
            if datetime.now(timezone.utc) - self.conversation_cooldowns[
                user_id
            ] < timedelta(
                seconds=3
            ):  # Reduced cooldown for better engagement
                return False

        # Always respond to mentions and DMs
        if self.bot.user in message.mentions:
            return True

        if isinstance(message.channel, discord.DMChannel):
            return True

        # Respond to direct address
        bot_indicators = [
            "astra",
            "hey bot",
            "ai help",
            "bot help",
            "hey ai",
            f"<@{self.bot.user.id}>",
            f"<@!{self.bot.user.id}>",
        ]
        if any(indicator in content_lower for indicator in bot_indicators):
            return True

        # Respond to questions in active conversations
        if "?" in message.content:
            # Check if this is part of an active conversation
            recent_history = self.conversation_history.get(user_id, [])
            if recent_history:
                last_interaction = recent_history[-1].get("timestamp")
                if last_interaction:
                    last_time = datetime.fromisoformat(last_interaction)
                    if (
                        datetime.now(timezone.utc) - last_time
                    ).total_seconds() < 1800:  # 30 minutes
                        return True

            # Respond to questions that seem directed at the channel/community
            community_question_indicators = [
                "anyone",
                "somebody",
                "someone",
                "does anyone",
                "has anyone",
                "what do you",
                "how do you",
                "where can",
                "when should",
                "thoughts",
                "opinions",
                "advice",
                "help",
                "recommend",
            ]
            if any(
                indicator in content_lower
                for indicator in community_question_indicators
            ):
                return True

        # Respond to help requests
        help_indicators = [
            "help",
            "assistance",
            "support",
            "stuck",
            "confused",
            "lost",
            "don't understand",
            "can't figure",
            "need advice",
            "any ideas",
        ]
        if any(indicator in content_lower for indicator in help_indicators):
            return True

        # Respond to conversation starters or interesting topics
        engagement_indicators = [
            "what do you think",
            "your opinion",
            "thoughts on",
            "agree with",
            "disagree with",
            "interesting",
            "fascinating",
            "amazing",
            "wow",
            "check this out",
            "look at this",
            "share with you",
        ]
        if any(indicator in content_lower for indicator in engagement_indicators):
            return True

        # Context-aware responses: if user has been chatting recently with bot
        if user_id in self.conversation_history:
            recent_messages = self.conversation_history[user_id][-5:]  # Last 5 messages
            if recent_messages:
                last_message = recent_messages[-1]
                last_time = datetime.fromisoformat(last_message["timestamp"])

                # If user was recently talking to bot, continue conversation with higher probability
                if (
                    datetime.now(timezone.utc) - last_time
                ).total_seconds() < 600:  # 10 minutes
                    if len(message.content) > 20:  # Substantial message
                        return True

        # Smart engagement for community building
        if len(message.content) > 50:
            # Higher chance for longer, more thoughtful messages
            import random

            # Check if message contains complex topics
            complex_topics = [
                "technology",
                "science",
                "philosophy",
                "programming",
                "development",
                "learning",
                "education",
                "career",
                "future",
                "innovation",
                "research",
                "discussion",
                "debate",
                "analysis",
                "strategy",
                "solution",
                "problem",
            ]

            if any(topic in content_lower for topic in complex_topics):
                return random.random() < 0.3  # 30% chance for complex topics

            return random.random() < 0.1  # 10% chance for other long messages

        return False

    async def _process_ai_conversation_enhanced(
        self, message: discord.Message, interaction_decision=None
    ):
        """Enhanced AI conversation processing with sophisticated interaction awareness"""
        try:
            if not self.ai_client:
                return

            # Get enhanced conversation context
            user_id = message.author.id
            user_history = self.conversation_history.get(user_id, [])

            # Build enhanced context for AI including interaction decision
            enhanced_context = {
                "user_id": user_id,
                "username": str(message.author),
                "display_name": message.author.display_name,
                "guild_id": message.guild.id if message.guild else None,
                "guild_name": message.guild.name if message.guild else "Direct Message",
                "channel_id": message.channel.id,
                "channel_name": getattr(message.channel, "name", "DM"),
                "interaction_type": interaction_decision.get("interaction_type", "unknown") if interaction_decision else "legacy",
                "confidence": interaction_decision.get("confidence", 0.5) if interaction_decision else 0.5,
                "urgency": interaction_decision.get("urgency", "normal") if interaction_decision else "normal",
                "emotional_tone": interaction_decision.get("emotional_tone", "neutral") if interaction_decision else "neutral",
                "message_history": user_history[-10:],  # Last 10 messages
                "timestamp": message.created_at.isoformat(),
                "is_dm": isinstance(message.channel, discord.DMChannel),
                "has_mentions": len(message.mentions) > 0,
                "is_reply": message.reference is not None,
                "member_since": (
                    message.author.joined_at.isoformat()
                    if hasattr(message.author, "joined_at") and message.author.joined_at
                    else None
                ),
            }

            # Generate response using available AI engine with enhanced context
            if hasattr(self.ai_client, "process_conversation"):
                response = await self.ai_client.process_conversation(
                    message.content,
                    user_id,
                    guild_id=message.guild.id if message.guild else None,
                    channel_id=message.channel.id,
                )
            elif hasattr(self.ai_client, "generate_response"):
                # Build context dictionary for ConsolidatedAIEngine compatibility
                context_dict = {
                    "user_id": user_id,
                    "guild_id": message.guild.id if message.guild else None,
                    "channel_id": message.channel.id,
                    "username": str(message.author),
                    "channel_type": (
                        "dm"
                        if isinstance(message.channel, discord.DMChannel)
                        else "guild"
                    ),
                    "message_history": user_history[-5:],  # Last 5 messages for context
                }
                response = await self.ai_client.generate_response(
                    message.content, context_dict
                )
            else:
                # Basic response with context awareness
                context_hint = ""
                if user_history:
                    context_hint = f" (Based on our conversation, I remember we were discussing various topics.)"

                response = f"I understand you're saying: '{message.content[:100]}...' I'm here to help and engage in our conversation!{context_hint}"

            # Update conversation history
            if user_id and response:
                self.conversation_history[user_id].append(
                    {
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "channel_id": message.channel.id,
                        "guild_id": message.guild.id if message.guild else None,
                    }
                )

            # 🚀 SOPHISTICATED RESPONSE ENHANCEMENT
            enhanced_response = await self._enhance_response_based_on_interaction(response, interaction_decision, message)

            # Send response with smart chunking
            await self._send_response_chunks(message.channel, enhanced_response)

            # Update cooldown
            self.conversation_cooldowns[message.author.id] = datetime.now(timezone.utc)

        except Exception as e:
            self.logger.error(f"Enhanced AI conversation processing error: {e}")
            try:
                await message.channel.send(
                    "I'm processing a lot of conversations right now! Give me just a moment to catch up. 🤖✨"
                )
            except:
                pass  # Don't crash if we can't send error message

    async def _send_response_chunks(self, channel, response: str):
        """Send response in appropriately sized chunks"""
        try:
            if len(response) <= 2000:
                await channel.send(response)
                return

            # Split at sentence boundaries for better readability
            sentences = response.split(". ")
            chunks = []
            current_chunk = ""

            for sentence in sentences:
                # Add period back except for last sentence
                sentence_with_period = sentence + (
                    ". " if not sentence.endswith(".") else " "
                )

                if (
                    len(current_chunk + sentence_with_period) > 1800
                ):  # Leave room for formatting
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                        current_chunk = sentence_with_period
                    else:
                        # Single sentence too long, force split
                        chunks.append(sentence[:1800])
                        current_chunk = sentence[1800:] + ". "
                else:
                    current_chunk += sentence_with_period

            if current_chunk:
                chunks.append(current_chunk.strip())

            # Send chunks with minimal delay
            for i, chunk in enumerate(chunks):
                if i > 0:
                    await asyncio.sleep(0.5)  # Brief pause between chunks
                await channel.send(chunk)

        except Exception as e:
            self.logger.error(f"Error sending response chunks: {e}")
            # Fallback: send truncated response
            try:
                await channel.send(response[:1900] + "... *(response truncated)*")
            except:
                pass

    async def _should_ai_respond(self, message: discord.Message) -> bool:
        """Legacy AI response determination (kept for fallback compatibility)"""
        return await self._should_ai_respond_enhanced(message)

    async def _process_ai_conversation(self, message: discord.Message):
        """Legacy AI conversation processing (kept for fallback compatibility)"""
        await self._process_ai_conversation_enhanced(message)

    @tasks.loop(hours=1)
    async def conversation_cleanup_task(self):
        """Clean up old conversation data"""
        try:
            current_time = datetime.now(timezone.utc)

            # Clean up conversation cooldowns
            expired_cooldowns = [
                user_id
                for user_id, timestamp in self.conversation_cooldowns.items()
                if current_time - timestamp > timedelta(hours=1)
            ]
            for user_id in expired_cooldowns:
                del self.conversation_cooldowns[user_id]

            # Clean up old conversation history
            for user_id in list(self.conversation_history.keys()):
                if (
                    len(self.conversation_history[user_id])
                    > self.max_history_length * 2
                ):
                    self.conversation_history[user_id] = self.conversation_history[
                        user_id
                    ][-self.max_history_length * 2 :]

            self.logger.debug("Conversation cleanup completed")

        except Exception as e:
            self.logger.error(f"Conversation cleanup task error: {e}")

    def cog_unload(self):
        """Clean up when cog is unloaded"""
        try:
            self.conversation_cleanup_task.cancel()
            self.logger.info("Advanced AI Cog unloaded")
        except:
            pass

    @app_commands.command(name="ai_status", description="Check AI system status")
    async def ai_status_command(self, interaction: discord.Interaction):
        """Check AI system status"""
        try:
            embed = discord.Embed(
                title="🤖 AI System Status",
                color=0x00FF00 if self.ai_client else 0xFF0000,
                timestamp=datetime.now(timezone.utc),
            )

            # AI Engine Status
            ai_status = "✅ Online" if self.ai_client else "❌ Offline"
            embed.add_field(name="AI Engine", value=ai_status, inline=True)

            # Performance Stats
            uptime = datetime.now(timezone.utc) - self.start_time
            embed.add_field(name="Uptime", value=str(uptime).split(".")[0], inline=True)
            embed.add_field(
                name="API Calls", value=f"{self.api_calls_made:,}", inline=True
            )
            embed.add_field(
                name="Successful Responses",
                value=f"{self.successful_responses:,}",
                inline=True,
            )

            # Active Conversations
            active_conversations = len(self.conversation_history)
            embed.add_field(
                name="Active Conversations",
                value=f"{active_conversations:,}",
                inline=True,
            )

            # System Info
            embed.add_field(
                name="Available Systems",
                value=(
                    f"• Optimized Engine: {'✅' if OPTIMIZED_AI_AVAILABLE else '❌'}\n"
                    f"• Consolidated Engine: {'✅' if AI_ENGINE_AVAILABLE else '❌'}\n"
                    f"• Context Manager: {'✅' if CONTEXT_MANAGER_AVAILABLE else '❌'}"
                ),
                inline=False,
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            self.logger.error(f"AI status command error: {e}")
            await interaction.response.send_message(
                f"❌ Error checking AI status: {str(e)}", ephemeral=True
            )

    async def _enhance_response_based_on_interaction(self, response: str, interaction_decision: Dict[str, Any], message: discord.Message) -> str:
        """🎨 SOPHISTICATED RESPONSE ENHANCEMENT - Enhance response based on interaction type and context"""
        try:
            if not interaction_decision:
                return response
                
            interaction_type = interaction_decision.get("interaction_type", "unknown")
            emotional_tone = interaction_decision.get("emotional_tone", "neutral")
            urgency = interaction_decision.get("urgency", "normal")
            
            enhanced_response = response
            
            # 1. EMOTIONAL TONE ENHANCEMENT
            if emotional_tone == "excited":
                enhanced_response = f"🎉 {enhanced_response} ✨"
            elif emotional_tone == "happy":
                enhanced_response = f"😊 {enhanced_response}"
            elif emotional_tone == "sad":
                enhanced_response = f"🤗 {enhanced_response} 💙"
            elif emotional_tone == "celebration":
                enhanced_response = f"🎊 {enhanced_response} 🎉"
            
            # 2. URGENCY ENHANCEMENT
            if urgency == "high" or urgency == "urgent":
                enhanced_response = f"⚡ {enhanced_response}"
            
            # 3. INTERACTION TYPE SPECIFIC ENHANCEMENTS
            if interaction_type == "help_request":
                enhanced_response = f"🆘 {enhanced_response}\n\n💡 *I'm here to help - feel free to ask follow-up questions!*"
            elif interaction_type == "community_question":
                enhanced_response = f"{enhanced_response}\n\n🤔 *What do others think about this?*"
            elif interaction_type == "complex_topic":
                enhanced_response = f"🧠 {enhanced_response}\n\n📚 *This is quite an interesting topic to dive into!*"
            elif interaction_type == "direct_mention":
                enhanced_response = f"👋 {enhanced_response}"
            
            # 4. ADD CONTEXTUAL REACTIONS SUGGESTIONS
            if len(enhanced_response) > 100:
                contextual_emojis = self._get_contextual_reaction_suggestions(message.content)
                if contextual_emojis:
                    # Add reactions to the message
                    asyncio.create_task(self._add_contextual_reactions(message, contextual_emojis))
            
            return enhanced_response
            
        except Exception as e:
            self.logger.error(f"Error enhancing response: {e}")
            return response

    def _get_contextual_reaction_suggestions(self, content: str) -> List[str]:
        """Get contextual reaction suggestions based on message content"""
        content_lower = content.lower()
        reactions = []
        
        # Technology reactions
        if any(word in content_lower for word in ["code", "programming", "tech", "ai", "computer"]):
            reactions.extend(["💻", "⚡"])
        
        # Achievement reactions
        if any(word in content_lower for word in ["completed", "finished", "success", "achievement"]):
            reactions.extend(["🏆", "🎉"])
        
        # Learning reactions
        if any(word in content_lower for word in ["learn", "study", "education", "knowledge"]):
            reactions.extend(["🧠", "📚"])
        
        # Question reactions
        if "?" in content:
            reactions.extend(["🤔", "💭"])
        
        return reactions[:2]  # Max 2 reactions

    async def _add_contextual_reactions(self, message: discord.Message, reactions: List[str]):
        """Add contextual reactions to a message"""
        try:
            for reaction in reactions:
                await message.add_reaction(reaction)
                await asyncio.sleep(0.5)  # Small delay between reactions
        except discord.HTTPException:
            pass  # Ignore if reactions fail

    # 📊 SOPHISTICATED ANALYTICS AND MONITORING
    async def get_interaction_analytics(self) -> Dict[str, Any]:
        """Get comprehensive interaction analytics"""
        try:
            total_conversations = len(self.conversation_history)
            total_messages = sum(len(history) for history in self.conversation_history.values())
            
            return {
                "total_conversations": total_conversations,
                "total_messages_processed": total_messages,
                "api_calls_made": self.api_calls_made,
                "successful_responses": self.successful_responses,
                "active_conversations": len([h for h in self.conversation_history.values() if h]),
                "average_conversation_length": total_messages / max(total_conversations, 1),
                "uptime": datetime.now(timezone.utc) - self.start_time,
                "success_rate": (self.successful_responses / max(self.api_calls_made, 1)) * 100
            }
        except Exception as e:
            self.logger.error(f"Error getting analytics: {e}")
            return {}


async def setup(bot):
    await bot.add_cog(AdvancedAICog(bot))
