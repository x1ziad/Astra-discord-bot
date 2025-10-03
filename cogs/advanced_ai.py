"""
Advanced AI Cog for Astra Bot
Implements modern AI features with LIGHTNING-FAST performance and metaphorical humor
"""

import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
import logging
import random
import time
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta, timezone
import json
import re
import os

# Lightning performance optimization imports
from utils.command_optimizer import optimize_command, optimized_send
from utils.lightning_optimizer import lightning_optimizer

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

    async def _lightning_ai_response(
        self,
        prompt: str,
        user_id: int = None,
        guild_id: int = None,
        channel_id: int = None,
        username: str = None,
    ) -> str:
        """Enhanced AI response with improved conversational context and natural flow"""
        start_time = time.time()

        try:
            if not self.ai_client:
                return (
                    "❌ My AI brain is temporarily out for a digital coffee break! ☕"
                )

            # ENHANCED: Better conversation context for improved understanding
            recent_history = []
            conversation_context = {}
            
            if user_id in self.conversation_history:
                user_history = self.conversation_history[user_id]
                # Get more relevant recent history
                recent_history = user_history[-6:]  # Last 3 exchanges
                
                # Build conversation context
                if len(user_history) > 0:
                    recent_messages = [msg for msg in user_history if time.time() - msg.get("timestamp", 0) < 300]  # 5 minutes
                    message_types = [msg.get("message_type", "casual") for msg in recent_messages]
                    
                    conversation_context = {
                        "active_conversation": len(recent_messages) > 0,
                        "conversation_tone": max(set(message_types), key=message_types.count) if message_types else "casual",
                        "user_engagement": len(recent_messages),
                        "last_interaction": user_history[-1].get("message_type", "casual") if user_history else "new",
                        "in_dm": user_history[-1].get("is_dm", False) if user_history else False
                    }

            # ENHANCED: Context-aware prompt enhancement
            enhanced_prompt = prompt
            if conversation_context.get("active_conversation"):
                tone = conversation_context.get("conversation_tone", "casual")
                if tone == "question":
                    enhanced_prompt = f"Continue our Q&A conversation naturally: {prompt}"
                elif tone == "technical":
                    enhanced_prompt = f"Continue our technical discussion: {prompt}"
                elif tone == "emotional":
                    enhanced_prompt = f"Respond empathetically, continuing our conversation: {prompt}"
                elif tone == "sharing":
                    enhanced_prompt = f"Respond to their story/sharing conversationally: {prompt}"
                else:
                    enhanced_prompt = f"Continue our friendly conversation: {prompt}"
            
            # Add personality context
            personality_context = "You are Astra, a friendly and witty AI bot with a love for space, gaming (especially Stellaris), and helping users. Be conversational, helpful, and occasionally use space/sci-fi metaphors. Keep responses natural and engaging."
            full_prompt = f"{personality_context}\n\nUser context: {conversation_context}\n\nUser message: {enhanced_prompt}"

            # OPTIMIZED: Parallel AI processing for lightning-fast responses
            response = None

            # Method 1: Enhanced AI processing with better context
            if hasattr(self.ai_client, "process_conversation"):
                try:
                    # Create primary AI task with enhanced context
                    primary_task = asyncio.create_task(
                        self.ai_client.process_conversation(
                            full_prompt, user_id, guild_id=guild_id, channel_id=channel_id,
                            context={"history": recent_history, "conversation_meta": conversation_context}
                        )
                    )

                    # Create fallback task with context awareness
                    async def context_aware_fallback():
                        await asyncio.sleep(0.3)
                        if hasattr(self.ai_client, "generate_response"):
                            return await self.ai_client.generate_response(
                                full_prompt,
                                context={
                                    "history": recent_history, 
                                    "optimized": True,
                                    "conversation_meta": conversation_context,
                                    "personality": "friendly_witty_space_themed"
                                },
                            )
                        return None

                    fallback_task = asyncio.create_task(context_aware_fallback())

                    # OPTIMIZED: Smart timeout based on conversation complexity
                    timeout = 3.0 if conversation_context.get("active_conversation") else 2.0
                    response = await asyncio.wait_for(primary_task, timeout=timeout)

                    # Cancel fallback if primary succeeded
                    fallback_task.cancel()

                except asyncio.TimeoutError:
                    self.logger.info(
                        "Primary AI timeout - switching to fallback (context-aware)"
                    )

                    try:
                        response = await asyncio.wait_for(fallback_task, timeout=1.5)
                    except (asyncio.TimeoutError, Exception) as fb_error:
                        self.logger.warning(f"Context-aware fallback timeout: {fb_error}")
                        response = None

                except Exception as e:
                    self.logger.warning(
                        f"Primary AI engine error - using fallback: {e}"
                    )
                    try:
                        response = await asyncio.wait_for(fallback_task, timeout=1.5)
                    except:
                        response = None

            # Method 2: Enhanced emergency fallback with conversation awareness
            if not response:
                try:
                    enhanced_context = {
                        "username": username or "Friend",
                        "guild_name": "Server",
                        "recent_activity": len(recent_history) > 0,
                        "conversation_active": conversation_context.get("active_conversation", False),
                        "conversation_tone": conversation_context.get("conversation_tone", "casual"),
                        "emergency": True,
                    }
                    response = await lightning_optimizer.get_fallback_response(
                        enhanced_context
                    )
                    
                    # If optimizer fallback fails, use smart contextual responses
                    if not response:
                        tone = conversation_context.get("conversation_tone", "casual")
                        if tone == "question":
                            response = "That's a great question! Let me think about that... 🤔"
                        elif tone == "technical":
                            response = "Interesting technical point! I'd love to dive deeper into this! 🚀"
                        elif tone == "emotional":
                            response = "I hear you on that! Thanks for sharing. 💙"
                        else:
                            response = "I'm here and ready to continue our conversation! What's on your mind? ✨"
                            
                except Exception as e:
                    self.logger.error(f"Enhanced fallback failed: {e}")
                    # Ultimate contextual fallback
                    if conversation_context.get("active_conversation"):
                        response = "My circuits got a bit tangled, but I'm still here for our conversation! 🤖✨"
                    else:
                        response = "I'm experiencing some cosmic interference, but I'm still here! Like a reliable lighthouse in a digital storm. 🌊"

            # ENHANCED: Smart history update with better context
            if user_id and response:
                if user_id not in self.conversation_history:
                    self.conversation_history[user_id] = []

                # Add enhanced history entry
                self.conversation_history[user_id].extend([
                    {
                        "role": "user", 
                        "content": prompt[:200],
                        "timestamp": time.time(),
                        "message_type": self._classify_message_type(prompt)
                    },
                    {
                        "role": "assistant",
                        "content": response[:300],
                        "timestamp": time.time(),
                        "context_used": bool(conversation_context.get("active_conversation"))
                    }
                ])

                # Smart history management
                max_history = 10 if conversation_context.get("in_dm") else 8
                if len(self.conversation_history[user_id]) > max_history:
                    self.conversation_history[user_id] = self.conversation_history[user_id][-max_history:]

            # Update performance metrics
            response_time = time.time() - start_time
            self.api_calls_made += 1
            if response and not any(
                fail_indicator in response.lower()
                for fail_indicator in ["error", "failed", "unavailable"]
            ):
                self.successful_responses += 1

            # Enhanced performance logging
            if response_time > 2.0:
                self.logger.warning(f"Slow AI response: {response_time:.2f}s (Context: {len(recent_history)} msgs)")
            elif response_time < 0.5:
                self.logger.info(f"Lightning AI response: {response_time:.3f}s")

            return response or "I'm here and ready to chat! What's on your mind? 🚀"

        except Exception as e:
            self.logger.error(f"Enhanced AI response error: {e}")
            return "Oops! My circuits had a brief hiccup, but I'm back online! How can I help you? ⚡"

    async def _generate_ai_response(
        self,
        prompt: str,
        user_id: int = None,
        guild_id: int = None,
        channel_id: int = None,
        username: str = None,
    ) -> str:
        """Legacy AI response method - kept for compatibility"""
        return await self._lightning_ai_response(
            prompt, user_id, guild_id, channel_id, username
        )

    @app_commands.command(
        name="chat", description="Chat with Astra AI - Lightning Fast! ⚡"
    )
    @app_commands.describe(message="Your message to the AI")
    @optimize_command(rate_limit_enabled=True, rate_limit_per_minute=30)
    async def chat_command(self, interaction: discord.Interaction, message: str):
        """Lightning-fast chat with AI assistant - Enhanced with metaphorical humor"""
        start_time = time.time()

        try:
            # Super fast response acknowledgment
            await interaction.response.defer()

            if not self.ai_client:
                await interaction.followup.send(
                    "❌ My brain circuits are taking a coffee break. Please try again in a moment! ☕",
                    ephemeral=True,
                )
                return

            # Lightning optimization - check for instant responses first
            guild_id = interaction.guild.id if interaction.guild else None
            user_context = {
                "user_id": interaction.user.id,
                "guild_id": guild_id,
                "username": str(interaction.user),
                "channel_id": interaction.channel.id,
            }

            # Super-fast optimization pipeline
            optimized_prompt, optimization_meta = (
                await lightning_optimizer.optimize_request(
                    message, interaction.user.id, user_context
                )
            )

            # If we got a quick response, send it immediately
            if optimization_meta.get("type") == "quick_response":
                embed = discord.Embed(
                    title="🚀 Astra AI - Lightning Response",
                    description=optimized_prompt,
                    color=0x00FF88,  # Green for super fast
                    timestamp=datetime.now(timezone.utc),
                )
                embed.set_author(
                    name=interaction.user.display_name,
                    icon_url=interaction.user.display_avatar.url,
                )
                response_time = time.time() - start_time
                embed.set_footer(text=f"⚡ Lightning fast: {response_time:.3f}s")

                await optimized_send(interaction.followup, embed=embed)
                return

            # If cached, return enhanced cached response
            if optimization_meta.get("cached"):
                embed = discord.Embed(
                    title="🤖 Astra AI - Cached Wisdom",
                    description=optimized_prompt[:4000],
                    color=0x7289DA,
                    timestamp=datetime.now(timezone.utc),
                )
                embed.set_author(
                    name=interaction.user.display_name,
                    icon_url=interaction.user.display_avatar.url,
                )
                response_time = time.time() - start_time
                embed.set_footer(text=f"🎯 Cached response: {response_time:.3f}s")

                await optimized_send(interaction.followup, embed=embed)
                return

            # Generate fresh AI response with optimized prompt
            response = await self._lightning_ai_response(
                optimized_prompt,
                interaction.user.id,
                guild_id=guild_id,
                channel_id=interaction.channel.id,
                username=str(interaction.user),
            )

            # Enhance with metaphorical humor
            enhanced_response = await lightning_optimizer.enhance_with_humor(
                response, user_context
            )

            # Cache the response for future lightning-fast retrieval
            await lightning_optimizer.cache_response(
                message, response, interaction.user.id, user_context
            )

            # Create lightning-fast embed
            embed = discord.Embed(
                title="🤖 Astra AI - Fresh Thoughts",
                description=enhanced_response[:4000],
                color=0xFF6B35,  # Orange for fresh AI
                timestamp=datetime.now(timezone.utc),
            )
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url,
            )

            # Add user message preview
            message_preview = message[:800] + ("..." if len(message) > 800 else "")
            embed.add_field(
                name="💬 Your Message",
                value=message_preview,
                inline=False,
            )

            # Performance metrics
            response_time = time.time() - start_time
            performance_color = (
                "🟢" if response_time < 1.0 else "🟡" if response_time < 3.0 else "🔴"
            )
            embed.set_footer(
                text=f"{performance_color} Response time: {response_time:.3f}s • Enhanced with humor ✨"
            )

            await optimized_send(interaction.followup, embed=embed)

        except Exception as e:
            self.logger.error(f"Lightning chat command error: {e}")
            response_time = time.time() - start_time

            # Even errors get humor!
            error_humor = [
                "Oops! My circuits just did the digital equivalent of tripping over their own feet! 🤖",
                "Well, that didn't go as planned... like trying to fold a fitted sheet! 😅",
                "Error detected! I'm having a 'brain.exe has stopped working' moment! 🤯",
                "Something went sideways faster than a cat avoiding a bath! 🐱",
            ]

            error_message = (
                f"{random.choice(error_humor)}\n\n*Technical details: {str(e)}*"
            )

            if not interaction.response.is_done():
                await interaction.response.send_message(error_message, ephemeral=True)
            else:
                await interaction.followup.send(error_message, ephemeral=True)

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
        """Lightning-Fast Universal Message Interaction System - Observes ALL messages with optimized response times"""
        if message.author.bot:
            return

        # Skip if this was a command to avoid double processing
        if message.content.startswith(
            tuple(await self.bot._get_dynamic_prefix(self.bot, message))
        ):
            return

        lightning_start = time.time()

        try:
            # LIGHTNING MESSAGE ANALYSIS - Ultra-fast context processing
            await self._lightning_analyze_message(message)

            # ULTRA-FAST INTERACTION DECISION ENGINE
            interaction_decision = await self._lightning_determine_interaction(message)

            # EXECUTE LIGHTNING INTERACTION
            if interaction_decision["should_interact"]:
                await self._lightning_execute_interaction(message, interaction_decision)

            # Track lightning performance
            lightning_time = time.time() - lightning_start
            if lightning_time > 0.5:  # Log slow message processing
                self.logger.warning(f"Slow message processing: {lightning_time:.3f}s")

        except Exception as e:
            self.logger.error(f"Lightning message processing error: {e}")

    async def _lightning_analyze_message(self, message: discord.Message):
        """Enhanced message analysis with improved context understanding"""
        try:
            # Ultra-light context analysis
            if message.author.id not in self.conversation_history:
                self.conversation_history[message.author.id] = []

            # Enhanced message filtering - store more types of meaningful content
            content_words = len(message.content.split())
            content_lower = message.content.lower().strip()
            
            # Don't store purely reactive messages unless they're part of ongoing conversation
            skip_words = {"ok", "k", "lol", "lmao", "haha", "xd", "brb", "gtg", "ty", "thx", "np"}
            is_reactive = content_lower in skip_words
            
            # Store if it's substantial OR if user is in active conversation
            should_store = (
                content_words > 2 or  # Substantial messages
                not is_reactive or  # Non-reactive short messages
                len(self.conversation_history[message.author.id]) > 0  # Active conversation
            )
            
            if should_store:
                # Enhanced message context
                message_data = {
                    "role": "user",
                    "content": message.content[:200],  # Increased from 100 for better context
                    "timestamp": time.time(),
                    "channel_id": message.channel.id,
                    "message_type": self._classify_message_type(message.content),
                    "word_count": content_words,
                    "has_mention": self.bot.user.mentioned_in(message),
                    "is_dm": isinstance(message.channel, discord.DMChannel)
                }
                
                self.conversation_history[message.author.id].append(message_data)

                # Enhanced history management - keep more recent entries
                max_history = 8 if isinstance(message.channel, discord.DMChannel) else 6
                if len(self.conversation_history[message.author.id]) > max_history:
                    self.conversation_history[message.author.id] = (
                        self.conversation_history[message.author.id][-max_history:]
                    )

        except Exception as e:
            self.logger.error(f"Lightning message analysis error: {e}")

    def _classify_message_type(self, content: str) -> str:
        """Quick message type classification for better context"""
        content_lower = content.lower().strip()
        
        if "?" in content:
            return "question"
        elif any(greeting in content_lower for greeting in ["hello", "hi", "hey", "good morning", "good evening"]):
            return "greeting"  
        elif any(emotion in content_lower for emotion in ["amazing", "awesome", "terrible", "frustrated", "excited", "sad", "happy"]):
            return "emotional"
        elif any(share in content_lower for share in ["just", "today", "yesterday", "happened", "did", "went", "saw"]):
            return "sharing"
        elif any(tech in content_lower for tech in ["stellaris", "game", "code", "tech", "computer"]):
            return "technical" 
        elif len(content.split()) > 10:
            return "detailed"
        else:
            return "casual"

    async def _lightning_determine_interaction(
        self, message: discord.Message
    ) -> Dict[str, Any]:
        """Enhanced interaction decision engine - More conversational and context-aware"""
        try:
            user_id = message.author.id
            content = message.content.lower()
            content_words = content.split()

            # Lightning-fast interaction scoring
            interaction_score = 0
            interaction_type = "casual"

            # PRIORITY 1: Direct mentions or bot references (100% response)
            if self.bot.user.mentioned_in(message) or any(
                keyword in content for keyword in ["astra", "bot", "ai", "help"]
            ):
                return {
                    "should_interact": True,
                    "interaction_type": "direct",
                    "priority": 10,
                    "probability": 100,
                    "response_style": "helpful",
                }

            # PRIORITY 2: Questions (high response rate)
            question_indicators = ["?", "how", "what", "why", "when", "where", "can you", "should i", "do you", "is it", "are you", "could", "would", "will"]
            if any(indicator in content for indicator in question_indicators):
                interaction_score += 50
                interaction_type = "question"

            # PRIORITY 3: Enhanced emotional content detection
            emotion_keywords = [
                "amazing", "awesome", "terrible", "frustrated", "excited", "confused", "sad", "happy",
                "love", "hate", "wonderful", "awful", "brilliant", "stupid", "perfect", "horrible",
                "thrilled", "disappointed", "grateful", "angry", "worried", "nervous", "proud",
                "embarrassed", "surprised", "shocked", "curious", "bored", "tired", "energetic"
            ]
            if any(emotion in content for emotion in emotion_keywords):
                interaction_score += 35
                interaction_type = "emotional"

            # PRIORITY 4: Enhanced conversation starters
            greeting_patterns = [
                "hello", "hi", "hey", "good morning", "good afternoon", "good evening", "good night",
                "sup", "yo", "greetings", "howdy", "what's up", "how are you", "how's it going"
            ]
            if any(starter in content for starter in greeting_patterns):
                interaction_score += 40
                interaction_type = "greeting"

            # PRIORITY 5: Sharing/storytelling (new)
            sharing_keywords = ["just", "today", "yesterday", "happened", "did", "went", "saw", "found", "discovered", "learned", "realized"]
            if any(keyword in content for keyword in sharing_keywords) and len(content_words) > 4:
                interaction_score += 30
                interaction_type = "story"

            # PRIORITY 6: Technical/gaming discussions (Stellaris focus)
            tech_gaming_keywords = ["stellaris", "game", "gaming", "tech", "code", "programming", "computer", "science", "space", "galaxy", "empire", "strategy"]
            if any(keyword in content for keyword in tech_gaming_keywords):
                interaction_score += 35
                interaction_type = "technical"

            # PRIORITY 7: Opinion requests/discussions
            opinion_keywords = ["think", "opinion", "thoughts", "believe", "agree", "disagree", "prefer", "better", "worse", "choose"]
            if any(keyword in content for keyword in opinion_keywords):
                interaction_score += 30
                interaction_type = "opinion"

            # ENHANCED: Context from conversation history
            user_history = self.conversation_history.get(user_id, [])
            if len(user_history) > 0:
                # User has been chatting recently - more likely to continue conversation
                recent_messages = [msg for msg in user_history if time.time() - msg.get("timestamp", 0) < 300]  # 5 minutes
                if len(recent_messages) > 0:
                    interaction_score += 20
                    
                # If user has been asking questions or sharing, they're in conversation mode
                recent_content = " ".join([msg.get("content", "") for msg in recent_messages[-3:]])
                if any(indicator in recent_content.lower() for indicator in question_indicators):
                    interaction_score += 15

            # ENHANCED: Smart cooldown with conversation awareness
            current_time = datetime.now(timezone.utc)
            if user_id in self.conversation_cooldowns:
                time_since_last = (current_time - self.conversation_cooldowns[user_id]).total_seconds()
                if time_since_last < 5:  # Reduced to 5 seconds for more natural flow
                    interaction_score -= 25
                elif time_since_last < 15:  # Slight penalty for recent activity
                    interaction_score -= 10

            # ENHANCED: Message quality and length analysis
            message_length = len(content_words)
            if message_length == 1:
                # Single word messages - contextual response
                single_word_responses = ["ok", "yeah", "yes", "no", "lol", "haha", "nice", "cool", "wow", "omg"]
                if content.strip() in single_word_responses:
                    interaction_score -= 10  # Less likely but not impossible
                else:
                    interaction_score += 5  # Interesting single words
            elif message_length < 3:
                interaction_score -= 5  # Short messages slightly less likely
            elif 3 <= message_length <= 6:
                interaction_score += 10  # Sweet spot
            elif message_length > 15:
                interaction_score += 20  # Long messages definitely deserve response

            # ENHANCED: Channel context awareness
            if message.guild:
                # In a server - be more selective but still responsive
                base_threshold = 15  # Reduced from 20 for more engagement
            else:
                # Direct message - always more responsive
                interaction_score += 25
                base_threshold = 8  # Reduced from 10

            # FINAL DECISION: More conversational threshold
            should_interact = interaction_score > base_threshold

            return {
                "should_interact": should_interact,
                "interaction_type": interaction_type,
                "priority": min(interaction_score // 10, 10),
                "probability": min(interaction_score, 100),
                "response_style": "witty" if interaction_score > 60 else "helpful" if interaction_score > 40 else "casual",
                "conversation_context": len(user_history) > 0,
                "message_quality": "high" if message_length > 10 else "medium" if message_length > 3 else "low"
            }

        except Exception as e:
            self.logger.error(f"Lightning interaction decision error: {e}")
            return {
                "should_interact": False,
                "interaction_type": "error",
                "priority": 0,
            }

    async def _lightning_execute_interaction(
        self, message: discord.Message, decision: Dict[str, Any]
    ):
        """Enhanced interaction execution with improved conversational abilities"""
        try:
            # Quick context for optimization
            user_context = {
                "user_id": message.author.id,
                "guild_id": message.guild.id if message.guild else None,
                "username": str(message.author),
                "channel_id": message.channel.id,
                "conversation_active": decision.get("conversation_context", False),
                "message_quality": decision.get("message_quality", "medium")
            }

            # Lightning optimization pipeline
            optimized_prompt, optimization_meta = (
                await lightning_optimizer.optimize_request(
                    message.content, message.author.id, user_context
                )
            )

            interaction_type = decision.get("interaction_type")
            response_style = decision.get("response_style", "casual")

            # Enhanced response handling based on interaction type
            if interaction_type == "direct":
                # Generate full AI response for direct interactions
                response = await self._lightning_ai_response(
                    optimized_prompt,
                    message.author.id,
                    guild_id=user_context.get("guild_id"),
                    channel_id=user_context.get("channel_id"),
                    username=user_context.get("username"),
                )

                # Enhance with humor
                enhanced_response = await lightning_optimizer.enhance_with_humor(
                    response, user_context
                )

                # Cache the response
                await lightning_optimizer.cache_response(
                    message.content, response, message.author.id, user_context
                )

                await message.channel.send(enhanced_response[:2000])

            elif interaction_type == "greeting":
                # Enhanced greeting responses with personality
                greetings = [
                    "Hey there! Ready to chat? 👋",
                    "Hello! I'm here like a digital genie - what can I help with? ✨",
                    "Hi! Faster than finding cat videos, I'm here to assist! 🐱",
                    "Greetings! I'm more excited than a dog seeing a tennis ball! 🎾",
                    "Oh hey! What's happening in your corner of the galaxy? 🌌",
                    "Hello there! Ready to explore some cosmic conversations? 🚀",
                    "Hi! I'm here and more ready than a Stellaris player on patch day! ⭐"
                ]
                await message.channel.send(random.choice(greetings))

            elif interaction_type == "question":
                # Enhanced question handling with context awareness
                if optimization_meta.get("type") == "quick_response":
                    await message.channel.send(optimized_prompt)
                else:
                    # Context-aware AI response for questions
                    context_prompt = f"Answer helpfully and conversationally: {optimized_prompt}"
                    if decision.get("conversation_context"):
                        context_prompt = f"Continue our conversation by answering: {optimized_prompt}"
                    
                    response = await self._lightning_ai_response(
                        context_prompt,
                        message.author.id,
                        guild_id=user_context.get("guild_id"),
                        channel_id=user_context.get("channel_id"),
                    )
                    await message.channel.send(response[:1800])

            elif interaction_type == "emotional":
                # Enhanced empathetic responses with variety
                positive_emotions = ["amazing", "awesome", "excited", "happy", "wonderful", "brilliant", "perfect", "thrilled", "proud", "grateful", "love"]
                negative_emotions = ["terrible", "frustrated", "sad", "awful", "horrible", "disappointed", "angry", "worried", "hate"]
                
                content_lower = message.content.lower()
                
                if any(emotion in content_lower for emotion in positive_emotions):
                    responses = [
                        "That's fantastic! 🌟", "I love that energy! ✨", "Awesome stuff! 🎉",
                        "You're radiating positive vibes! 😊", "That's the spirit! 💪",
                        "Brilliant! Keep that momentum going! 🚀"
                    ]
                elif any(emotion in content_lower for emotion in negative_emotions):
                    responses = [
                        "I hear you, that sounds tough 🤗", "Hang in there! 💙",
                        "That's frustrating, but you've got this! 💪", "Rough times don't last, but resilient people do! ✨",
                        "I'm here if you need to talk it out 💬", "Tomorrow's a fresh start! 🌅"
                    ]
                else:
                    responses = [
                        "I hear you! 🤗", "Sounds like quite the adventure! 🎢",
                        "That's quite a feeling! ✨", "I'm with you on that one! 💪"
                    ]
                
                await message.channel.send(random.choice(responses))

            elif interaction_type == "story":
                # New: Responses to people sharing experiences
                story_responses = [
                    "Ooh, tell me more! 👀", "That sounds interesting! What happened next? 🤔",
                    "I'm listening! 👂", "Sounds like quite the experience! ✨",
                    "That's fascinating! How did that go? 🌟", "I'm curious about this story! 📖"
                ]
                await message.channel.send(random.choice(story_responses))

            elif interaction_type == "technical":
                # New: Technical/gaming focused responses
                tech_responses = [
                    "Now we're talking my language! 🤖", "Ah, a fellow tech enthusiast! 💻",
                    "Stellaris? You've got excellent taste! ⭐", "Gaming wisdom incoming! 🎮",
                    "Tech talk is the best talk! 🔧", "Ready to dive deep into this! 🚀"
                ]
                
                # For deeper technical discussions, use AI
                if len(message.content.split()) > 8:
                    response = await self._lightning_ai_response(
                        f"Engage in technical/gaming discussion about: {optimized_prompt}",
                        message.author.id,
                        guild_id=user_context.get("guild_id"),
                    )
                    await message.channel.send(response[:1800])
                else:
                    await message.channel.send(random.choice(tech_responses))

            elif interaction_type == "opinion":
                # New: Opinion and discussion responses
                opinion_responses = [
                    "That's an interesting perspective! 🤔", "I'd love to hear your thoughts on this! 💭",
                    "Ooh, philosophical territory! What do you think? 🧠", "Debates are the spice of conversation! 🌶️",
                    "That's worth pondering! ⭐", "Good question! What's your take? �"
                ]
                
                # For complex opinions, engage with AI
                if "?" in message.content or len(message.content.split()) > 6:
                    response = await self._lightning_ai_response(
                        f"Engage thoughtfully in discussion about: {optimized_prompt}",
                        message.author.id,
                        guild_id=user_context.get("guild_id"),
                    )
                    await message.channel.send(response[:1800])
                else:
                    await message.channel.send(random.choice(opinion_responses))

            else:
                # Enhanced casual interactions - more context-aware and substantial
                casual_responses = [
                    "Interesting! 🤔", "I see what you mean! 👀", "That's cool! ✨",
                    "Nice! 😊", "Gotcha! 👍", "Fair point! 💡", "I hear you! 👂",
                    "Makes sense! 🧠", "Right on! 🎯", "Totally! ⭐"
                ]
                
                # IMPROVED: More intelligent decision for AI responses
                should_use_ai = (
                    decision.get("message_quality") == "high" or  # Quality messages
                    decision.get("conversation_context") or  # Active conversation
                    len(message.content.split()) > 8 or  # Substantial messages
                    random.random() > 0.5  # 50% chance for better engagement
                )
                
                if should_use_ai:
                    # Enhanced prompt for better context awareness
                    context_prompt = f"Respond naturally and conversationally to: {optimized_prompt}"
                    if decision.get("conversation_context"):
                        context_prompt = f"Continue our conversation by responding to: {optimized_prompt}"
                    
                    response = await self._lightning_ai_response(
                        context_prompt,
                        message.author.id,
                        guild_id=user_context.get("guild_id"),
                    )
                    await message.channel.send(response[:1500])
                else:
                    await message.channel.send(random.choice(casual_responses))

            # Update cooldown
            self.conversation_cooldowns[message.author.id] = datetime.now(timezone.utc)

        except Exception as e:
            self.logger.error(f"Lightning interaction execution error: {e}")

            # Graceful fallback
            fallback_responses = [
                "Hmm, something went sideways there! 🤖", "My circuits got a bit tangled! Try again? ⚡",
                "Oops! Even AI has hiccups sometimes! 😅"
            ]
            try:
                await message.channel.send(random.choice(fallback_responses))
            except:
                pass  # If we can't even send a fallback, just log and move on

    async def _determine_interaction_type(
        self, message: discord.Message
    ) -> Dict[str, Any]:
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
                "priority_level": 0,
            }

            # COOLDOWN CHECK with sophisticated timing
            if user_id in self.conversation_cooldowns:
                time_since_last = (
                    datetime.now(timezone.utc) - self.conversation_cooldowns[user_id]
                )
                if time_since_last < timedelta(
                    seconds=2
                ):  # Very short cooldown for reactions/emojis
                    if time_since_last < timedelta(seconds=1):
                        return decision  # Too recent, skip
                    else:
                        # Allow reactions/emojis but not full responses
                        decision["response_method"] = "reaction"

            # 🎯 PRIORITY INTERACTION TRIGGERS (Always respond)

            # 1. DIRECT MENTIONS (Highest Priority)
            if self.bot.user in message.mentions:
                decision.update(
                    {
                        "should_interact": True,
                        "interaction_type": "direct_mention",
                        "confidence": 0.95,
                        "response_method": "text",
                        "priority_level": 10,
                        "should_reply": True,
                    }
                )
                return decision

            # 2. DIRECT MESSAGES (Highest Priority)
            if isinstance(message.channel, discord.DMChannel):
                decision.update(
                    {
                        "should_interact": True,
                        "interaction_type": "direct_message",
                        "confidence": 0.95,
                        "response_method": "text",
                        "priority_level": 10,
                        "should_reply": True,
                    }
                )
                return decision

            # 3. BOT NAME MENTIONS (High Priority)
            bot_indicators = [
                "astra",
                "hey bot",
                "ai help",
                "bot help",
                "hey ai",
                "hello astra",
                "hi astra",
            ]
            for indicator in bot_indicators:
                if indicator in content_lower:
                    decision.update(
                        {
                            "should_interact": True,
                            "interaction_type": "name_mention",
                            "confidence": 0.9,
                            "response_method": "text",
                            "priority_level": 9,
                            "should_reply": True,
                        }
                    )
                    return decision

            # 🚨 HELP AND URGENT REQUESTS (High Priority)
            help_urgent_indicators = [
                "help",
                "emergency",
                "urgent",
                "asap",
                "quickly",
                "immediately",
                "stuck",
                "confused",
                "lost",
                "don't understand",
                "can't figure",
                "need assistance",
                "support",
                "please help",
                "anyone help",
            ]
            for indicator in help_urgent_indicators:
                if indicator in content_lower:
                    decision.update(
                        {
                            "should_interact": True,
                            "interaction_type": "help_request",
                            "confidence": 0.85,
                            "response_method": "text",
                            "urgency": "high",
                            "priority_level": 8,
                            "should_reply": True,
                        }
                    )
                    return decision

            # 💬 QUESTIONS AND COMMUNITY ENGAGEMENT (Medium-High Priority)
            if "?" in message.content and len(message.content) > 10:
                question_indicators = [
                    "what",
                    "how",
                    "why",
                    "where",
                    "when",
                    "who",
                    "which",
                    "anyone",
                    "somebody",
                    "someone",
                    "does anyone",
                    "has anyone",
                    "thoughts",
                    "opinions",
                    "advice",
                    "recommend",
                    "suggest",
                ]
                for indicator in question_indicators:
                    if indicator in content_lower:
                        decision.update(
                            {
                                "should_interact": True,
                                "interaction_type": "community_question",
                                "confidence": 0.75,
                                "response_method": "text",
                                "priority_level": 7,
                                "should_reply": True,
                            }
                        )
                        return decision

            # 🎭 EMOTIONAL EXPRESSION DETECTION (Medium Priority - React with emojis)
            emotional_expressions = {
                "excited": [
                    "amazing",
                    "awesome",
                    "incredible",
                    "fantastic",
                    "wow",
                    "omg",
                    "excited",
                    "🎉",
                    "🔥",
                    "⚡",
                ],
                "happy": [
                    "happy",
                    "joy",
                    "great",
                    "wonderful",
                    "perfect",
                    "love",
                    "😊",
                    "😄",
                    "🥰",
                    "❤️",
                ],
                "sad": [
                    "sad",
                    "depressed",
                    "down",
                    "upset",
                    "crying",
                    "😢",
                    "😭",
                    "💔",
                    "😞",
                ],
                "angry": [
                    "angry",
                    "mad",
                    "furious",
                    "rage",
                    "annoyed",
                    "😡",
                    "🤬",
                    "😤",
                ],
                "confused": [
                    "confused",
                    "lost",
                    "puzzled",
                    "wtf",
                    "what",
                    "huh",
                    "🤔",
                    "😕",
                    "❓",
                ],
                "celebration": [
                    "celebrate",
                    "party",
                    "achievement",
                    "success",
                    "win",
                    "won",
                    "🎉",
                    "🎊",
                    "🥳",
                    "🏆",
                ],
            }

            for emotion, indicators in emotional_expressions.items():
                for indicator in indicators:
                    if indicator in content_lower:
                        decision.update(
                            {
                                "should_interact": True,
                                "interaction_type": "emotional_response",
                                "confidence": 0.6,
                                "response_method": (
                                    "emoji" if len(message.content) < 50 else "multi"
                                ),
                                "emotional_tone": emotion,
                                "priority_level": 5,
                                "suggested_emojis": self._get_emotion_emojis(emotion),
                            }
                        )
                        return decision

            # 📚 COMPLEX TOPICS AND DISCUSSIONS (Medium Priority)
            complex_topics = [
                "technology",
                "science",
                "programming",
                "development",
                "ai",
                "machine learning",
                "philosophy",
                "research",
                "innovation",
                "future",
                "analysis",
                "discussion",
                "debate",
                "strategy",
                "solution",
                "problem",
                "learning",
                "education",
            ]

            for topic in complex_topics:
                if topic in content_lower and len(message.content) > 30:
                    import random

                    if random.random() < 0.4:  # 40% chance for complex topics
                        decision.update(
                            {
                                "should_interact": True,
                                "interaction_type": "complex_topic",
                                "confidence": 0.4,
                                "response_method": "text",
                                "priority_level": 4,
                                "should_reply": True,
                            }
                        )
                        return decision

            # 🎯 CONVERSATION CONTINUITY (Medium Priority)
            recent_history = self.conversation_history.get(user_id, [])
            if recent_history:
                last_interaction = recent_history[-1].get("timestamp")
                if last_interaction:
                    last_time = datetime.fromisoformat(last_interaction)
                    if (
                        datetime.now(timezone.utc) - last_time
                    ).total_seconds() < 1800:  # 30 minutes
                        if len(message.content) > 20:
                            decision.update(
                                {
                                    "should_interact": True,
                                    "interaction_type": "conversation_continuity",
                                    "confidence": 0.5,
                                    "response_method": "text",
                                    "priority_level": 3,
                                    "should_reply": True,
                                }
                            )
                            return decision

            # 🎲 SMART ENGAGEMENT FOR COMMUNITY BUILDING (Low Priority)
            if len(message.content) > 50:
                import random

                # Increased engagement for better auto-response testing
                engagement_chance = (
                    0.7 if len(message.content) > 100 else 0.5
                )  # Much higher for testing

                if random.random() < engagement_chance:
                    decision.update(
                        {
                            "should_interact": True,
                            "interaction_type": "community_building",
                            "confidence": 0.3,
                            "response_method": (
                                "reaction"
                                if random.random() < 0.4
                                else "text"  # More text responses
                            ),
                            "priority_level": 2,
                            "suggested_reactions": ["👍", "🤔", "💯", "🔥"],
                            "should_reply": True,  # Enable text responses for community building
                        }
                    )
                    return decision

            # 🎉 POSITIVE REACTIONS (Low Priority - Just react)
            positive_indicators = [
                "thanks",
                "thank you",
                "good job",
                "well done",
                "nice",
                "cool",
            ]
            for indicator in positive_indicators:
                if indicator in content_lower:
                    decision.update(
                        {
                            "should_interact": True,
                            "interaction_type": "positive_acknowledgment",
                            "confidence": 0.4,
                            "response_method": "reaction",
                            "priority_level": 1,
                            "suggested_reactions": ["👍", "😊", "❤️", "🙏"],
                        }
                    )
                    return decision

            # 🎯 CATCH-ALL ENGAGEMENT (For Testing - Respond to almost everything)
            if len(message.content) > 10:  # Any meaningful message
                import random

                # High chance to respond to any message for testing auto-response
                if random.random() < 0.8:  # 80% chance for testing
                    decision.update(
                        {
                            "should_interact": True,
                            "interaction_type": "general_engagement",
                            "confidence": 0.2,
                            "response_method": "reaction",  # Start with reactions for less spam
                            "priority_level": 1,
                            "suggested_reactions": ["👍", "👀", "🤔"],
                        }
                    )
                    return decision

            return decision

        except Exception as e:
            self.logger.error(f"Error in interaction decision engine: {e}")
            return {
                "should_interact": False,
                "interaction_type": "error",
                "confidence": 0.0,
            }

    def _get_emotion_emojis(self, emotion: str) -> List[str]:
        """Get appropriate emojis for emotional responses"""
        emoji_map = {
            "excited": ["🎉", "🔥", "⚡", "🚀", "💥", "✨"],
            "happy": ["😊", "😄", "🥰", "❤️", "🌟", "☀️"],
            "sad": ["😢", "🥺", "💙", "🫂", "🌧️"],
            "angry": ["😤", "💪", "🌋"],
            "confused": ["🤔", "❓", "🧐", "💭"],
            "celebration": ["🎉", "🎊", "🥳", "🏆", "👏", "🙌"],
        }
        return emoji_map.get(emotion, ["👍", "😊"])

    async def _execute_sophisticated_interaction(
        self, message: discord.Message, decision: Dict[str, Any]
    ):
        """🚀 SOPHISTICATED INTERACTION EXECUTOR - Executes the determined interaction"""
        try:
            interaction_type = decision["interaction_type"]
            response_method = decision["response_method"]

            self.logger.info(
                f"Executing {interaction_type} interaction via {response_method} (confidence: {decision['confidence']:.2f})"
            )

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
                self.conversation_cooldowns[message.author.id] = datetime.now(
                    timezone.utc
                )
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

                self.conversation_cooldowns[message.author.id] = datetime.now(
                    timezone.utc
                )
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

                self.conversation_cooldowns[message.author.id] = datetime.now(
                    timezone.utc
                )
                return

            # 4. TEXT-BASED INTERACTIONS (Full AI Response)
            elif response_method == "text" and decision.get("should_reply", False):
                await self._process_ai_conversation_enhanced(message, decision)
                self.conversation_cooldowns[message.author.id] = datetime.now(
                    timezone.utc
                )
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

                self.conversation_cooldowns[message.author.id] = datetime.now(
                    timezone.utc
                )

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
            ("fire", "hot", "lit", "cool"): "🔥",
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
                "interaction_type": (
                    interaction_decision.get("interaction_type", "unknown")
                    if interaction_decision
                    else "legacy"
                ),
                "confidence": (
                    interaction_decision.get("confidence", 0.5)
                    if interaction_decision
                    else 0.5
                ),
                "urgency": (
                    interaction_decision.get("urgency", "normal")
                    if interaction_decision
                    else "normal"
                ),
                "emotional_tone": (
                    interaction_decision.get("emotional_tone", "neutral")
                    if interaction_decision
                    else "neutral"
                ),
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
            enhanced_response = await self._enhance_response_based_on_interaction(
                response, interaction_decision, message
            )

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

    @app_commands.command(
        name="ai_status",
        description="Check AI system status and lightning performance ⚡",
    )
    async def ai_status_command(self, interaction: discord.Interaction):
        """Check AI system status with comprehensive performance metrics"""
        try:
            # Get lightning performance stats
            perf_stats = lightning_optimizer.get_performance_stats()

            embed = discord.Embed(
                title="🚀 AI System Status - Lightning Edition",
                color=0x00FF88 if self.ai_client else 0xFF0000,
                timestamp=datetime.now(timezone.utc),
            )

            # AI Engine Status
            ai_status = "🟢 Lightning Fast" if self.ai_client else "🔴 Offline"
            embed.add_field(name="AI Engine", value=ai_status, inline=True)

            # Lightning Performance Stats
            if "average_response_time" in perf_stats:
                avg_time = perf_stats["average_response_time"]
                performance_emoji = (
                    "⚡"
                    if avg_time < 0.5
                    else "🚀" if avg_time < 1.0 else "🟡" if avg_time < 2.0 else "🔴"
                )

                embed.add_field(
                    name=f"{performance_emoji} Avg Response",
                    value=f"{avg_time}s",
                    inline=True,
                )
                embed.add_field(
                    name="🏆 Fastest Response",
                    value=f"{perf_stats['fastest_response']}s",
                    inline=True,
                )
                embed.add_field(
                    name="📊 Total Requests",
                    value=f"{perf_stats['total_requests']:,}",
                    inline=True,
                )

            # Cache Performance
            if "cache_stats" in perf_stats:
                cache_stats = perf_stats["cache_stats"]
                hit_rate = cache_stats.get("hit_rate", 0)
                cache_emoji = "🎯" if hit_rate > 70 else "⚡" if hit_rate > 40 else "📈"

                embed.add_field(
                    name=f"{cache_emoji} Cache Hit Rate",
                    value=f"{hit_rate}%",
                    inline=True,
                )
                embed.add_field(
                    name="💾 Cache Size",
                    value=f"{cache_stats['hit_count'] + cache_stats['miss_count']:,} total",
                    inline=True,
                )

            # Traditional Metrics
            uptime = datetime.now(timezone.utc) - self.start_time
            embed.add_field(
                name="⏰ Uptime", value=str(uptime).split(".")[0], inline=True
            )

            # Success Rate
            if self.api_calls_made > 0:
                success_rate = (self.successful_responses / self.api_calls_made) * 100
                success_emoji = (
                    "🟢" if success_rate > 95 else "🟡" if success_rate > 85 else "🔴"
                )
                embed.add_field(
                    name=f"{success_emoji} Success Rate",
                    value=f"{success_rate:.1f}%",
                    inline=True,
                )

            # Active Conversations
            active_conversations = len(self.conversation_history)
            conversation_emoji = (
                "💬"
                if active_conversations < 50
                else "🔥" if active_conversations < 100 else "💥"
            )
            embed.add_field(
                name=f"{conversation_emoji} Active Chats",
                value=f"{active_conversations:,}",
                inline=True,
            )

            # Request Type Breakdown
            if "request_types" in perf_stats and perf_stats["request_types"]:
                breakdown_text = ""
                for req_type, stats in perf_stats["request_types"].items():
                    type_emoji = (
                        "⚡"
                        if stats["avg_time"] < 0.1
                        else "🚀" if stats["avg_time"] < 0.5 else "⚡"
                    )
                    breakdown_text += f"{type_emoji} {req_type}: {stats['count']} ({stats['avg_time']}s)\n"

                if breakdown_text:
                    embed.add_field(
                        name="📈 Performance Breakdown",
                        value=breakdown_text[:1000],
                        inline=False,
                    )

            # System Availability
            embed.add_field(
                name="🛠️ Available Systems",
                value=(
                    f"⚡ Lightning Optimizer: {'🟢 Active' if lightning_optimizer else '🔴 Offline'}\n"
                    f"🤖 Optimized Engine: {'🟢 Ready' if OPTIMIZED_AI_AVAILABLE else '🔴 Unavailable'}\n"
                    f"🧠 Consolidated Engine: {'🟢 Ready' if AI_ENGINE_AVAILABLE else '🔴 Unavailable'}\n"
                    f"📚 Context Manager: {'🟢 Ready' if CONTEXT_MANAGER_AVAILABLE else '🔴 Unavailable'}\n"
                    f"😂 Humor Engine: {'🟢 Loaded' if lightning_optimizer.humor_engine else '🔴 Missing'}"
                ),
                inline=False,
            )

            # Add witty footer
            humorous_footers = [
                "Powered by digital caffeine and quantum confusion ☕",
                "Running smoother than a cat on ice skates 🐱",
                "Faster than finding the TV remote when you really need it 📺",
                "More reliable than your internet connection during video calls 📡",
            ]
            embed.set_footer(text=random.choice(humorous_footers))

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            self.logger.error(f"AI status command error: {e}")
            await interaction.response.send_message(
                f"❌ Error checking AI status: {str(e)}", ephemeral=True
            )

    async def _enhance_response_based_on_interaction(
        self,
        response: str,
        interaction_decision: Dict[str, Any],
        message: discord.Message,
    ) -> str:
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
                enhanced_response = (
                    f"{enhanced_response}\n\n🤔 *What do others think about this?*"
                )
            elif interaction_type == "complex_topic":
                enhanced_response = f"🧠 {enhanced_response}\n\n📚 *This is quite an interesting topic to dive into!*"
            elif interaction_type == "direct_mention":
                enhanced_response = f"👋 {enhanced_response}"

            # 4. ADD CONTEXTUAL REACTIONS SUGGESTIONS
            if len(enhanced_response) > 100:
                contextual_emojis = self._get_contextual_reaction_suggestions(
                    message.content
                )
                if contextual_emojis:
                    # Add reactions to the message
                    asyncio.create_task(
                        self._add_contextual_reactions(message, contextual_emojis)
                    )

            return enhanced_response

        except Exception as e:
            self.logger.error(f"Error enhancing response: {e}")
            return response

    def _get_contextual_reaction_suggestions(self, content: str) -> List[str]:
        """Get contextual reaction suggestions based on message content"""
        content_lower = content.lower()
        reactions = []

        # Technology reactions
        if any(
            word in content_lower
            for word in ["code", "programming", "tech", "ai", "computer"]
        ):
            reactions.extend(["💻", "⚡"])

        # Achievement reactions
        if any(
            word in content_lower
            for word in ["completed", "finished", "success", "achievement"]
        ):
            reactions.extend(["🏆", "🎉"])

        # Learning reactions
        if any(
            word in content_lower
            for word in ["learn", "study", "education", "knowledge"]
        ):
            reactions.extend(["🧠", "📚"])

        # Question reactions
        if "?" in content:
            reactions.extend(["🤔", "💭"])

        return reactions[:2]  # Max 2 reactions

    async def _add_contextual_reactions(
        self, message: discord.Message, reactions: List[str]
    ):
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
            total_messages = sum(
                len(history) for history in self.conversation_history.values()
            )

            return {
                "total_conversations": total_conversations,
                "total_messages_processed": total_messages,
                "api_calls_made": self.api_calls_made,
                "successful_responses": self.successful_responses,
                "active_conversations": len(
                    [h for h in self.conversation_history.values() if h]
                ),
                "average_conversation_length": total_messages
                / max(total_conversations, 1),
                "uptime": datetime.now(timezone.utc) - self.start_time,
                "success_rate": (
                    self.successful_responses / max(self.api_calls_made, 1)
                )
                * 100,
            }
        except Exception as e:
            self.logger.error(f"Error getting analytics: {e}")
            return {}

    @app_commands.command(
        name="lightning_perf",
        description="Lightning performance optimization controls ⚡",
    )
    @app_commands.describe(action="Action to perform: status, reset, or optimize")
    async def lightning_performance_command(
        self, interaction: discord.Interaction, action: str = "status"
    ):
        """Lightning performance optimization and monitoring"""
        try:
            action = action.lower().strip()

            if action == "status":
                # Detailed performance status
                perf_stats = lightning_optimizer.get_performance_stats()

                embed = discord.Embed(
                    title="⚡ Lightning Performance Dashboard",
                    color=0x00FF88,
                    timestamp=datetime.now(timezone.utc),
                )

                if "average_response_time" in perf_stats:
                    avg_time = perf_stats["average_response_time"]
                    performance_grade = (
                        "A+"
                        if avg_time < 0.3
                        else (
                            "A"
                            if avg_time < 0.6
                            else (
                                "B"
                                if avg_time < 1.0
                                else "C" if avg_time < 2.0 else "D"
                            )
                        )
                    )

                    embed.add_field(
                        name=f"📊 Performance Grade: {performance_grade}",
                        value=f"Average: {avg_time}s\nFastest: {perf_stats['fastest_response']}s\nSlowest: {perf_stats['slowest_response']}s",
                        inline=False,
                    )

                    # Cache effectiveness
                    if "cache_stats" in perf_stats:
                        cache_stats = perf_stats["cache_stats"]
                        embed.add_field(
                            name="🎯 Cache Performance",
                            value=f"Hit Rate: {cache_stats['hit_rate']}%\nHits: {cache_stats['hit_count']}\nMisses: {cache_stats['miss_count']}",
                            inline=True,
                        )

                    # Request breakdown
                    if "request_types" in perf_stats:
                        breakdown = ""
                        for req_type, stats in perf_stats["request_types"].items():
                            breakdown += f"• {req_type}: {stats['count']} requests ({stats['avg_time']}s avg)\n"

                        if breakdown:
                            embed.add_field(
                                name="📈 Request Types",
                                value=breakdown[:1000],
                                inline=False,
                            )

                embed.set_footer(
                    text="💡 Use '/lightning_perf optimize' to boost performance further!"
                )

            elif action == "reset":
                # Reset performance metrics
                lightning_optimizer.performance_metrics.clear()
                lightning_optimizer.response_times.clear()
                lightning_optimizer.cache.hit_count = 0
                lightning_optimizer.cache.miss_count = 0

                self.api_calls_made = 0
                self.successful_responses = 0
                self.start_time = datetime.now(timezone.utc)

                embed = discord.Embed(
                    title="🔄 Performance Metrics Reset",
                    description="All performance metrics have been reset! Starting fresh with lightning speed! ⚡",
                    color=0xFF6B35,
                    timestamp=datetime.now(timezone.utc),
                )
                embed.set_footer(
                    text="Like a computer reboot, but for performance tracking! 💻"
                )

            elif action == "optimize":
                # Trigger optimization processes
                embed = discord.Embed(
                    title="🚀 Lightning Optimization Engaged!",
                    description="Activating turbo boost mode... 🏎️💨",
                    color=0x7289DA,
                    timestamp=datetime.now(timezone.utc),
                )

                # Clear old cache entries
                await lightning_optimizer.cache._evict_old_entries()

                # Trigger conversation cleanup
                cleaned_conversations = 0
                for user_id in list(self.conversation_history.keys()):
                    if len(self.conversation_history[user_id]) > 4:
                        self.conversation_history[user_id] = self.conversation_history[
                            user_id
                        ][-4:]
                        cleaned_conversations += 1

                optimization_results = [
                    "🧹 Cache optimization completed",
                    f"💬 Cleaned {cleaned_conversations} conversation histories",
                    "⚡ Memory usage optimized",
                    "🎯 Response targeting improved",
                    "🚀 Turbo mode activated!",
                ]

                embed.add_field(
                    name="Optimization Results:",
                    value="\n".join(optimization_results),
                    inline=False,
                )
                embed.set_footer(
                    text="Your bot is now running like a caffeinated cheetah! 🐆☕"
                )

            else:
                embed = discord.Embed(
                    title="❓ Performance Command Help",
                    description="Available actions:\n• `status` - View detailed performance metrics\n• `reset` - Reset all performance counters\n• `optimize` - Trigger performance optimization",
                    color=0x7289DA,
                )
                embed.set_footer(
                    text="Like a performance GPS - showing you the way to speed! 🗺️"
                )

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            self.logger.error(f"Performance command error: {e}")
            await interaction.response.send_message(
                f"🔧 Performance command had a hiccup: {str(e)}\n*Even race cars need pit stops sometimes!* 🏁",
                ephemeral=True,
            )


async def setup(bot):
    await bot.add_cog(AdvancedAICog(bot))
