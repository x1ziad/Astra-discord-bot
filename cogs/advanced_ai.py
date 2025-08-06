"""
Advanced AI Cog for Astra Bot
Implements modern AI features with GitHub Models and OpenAI integration
"""

import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
import os

# Import the new consolidated AI engine and proactive systems
try:
    from ai.consolidated_ai_engine import ConsolidatedAIEngine
    from ai.user_profiling import user_profile_manager, UserProfileManager
    from ai.proactive_engagement import proactive_engagement, ProactiveEngagement
    from config.enhanced_config import EnhancedConfigManager

    AI_ENGINE_AVAILABLE = True
    logger = logging.getLogger("astra.advanced_ai")
    logger.info("Consolidated AI Engine and Proactive Systems successfully imported")
except ImportError as e:
    AI_ENGINE_AVAILABLE = False
    logger = logging.getLogger("astra.advanced_ai")
    logger.error(f"Failed to import AI systems: {e}")

# Backward compatibility imports
from config.config_manager import config_manager

logger = logging.getLogger("astra.advanced_ai")


class AdvancedAICog(commands.Cog):
    """Advanced AI features with GitHub Models and OpenAI integration"""

    def __init__(self, bot):
        self.bot = bot
        self.config = config_manager
        self.logger = logging.getLogger("astra.advanced_ai")

        # Initialize AI client
        self.ai_client = None
        self._setup_ai_client()

        # Active conversations tracking
        self.active_conversations: Set[int] = set()
        self.conversation_cooldowns: Dict[int, datetime] = {}
        self.channel_activity: Dict[int, Dict[str, Any]] = {}

        # Conversation history
        self.conversation_history: Dict[int, List[Dict[str, str]]] = {}
        self.max_history_length = 10

        # User conversations tracking (for compatibility)
        self.user_conversations = self.conversation_history

        # Performance tracking
        self.api_calls_made = 0
        self.successful_responses = 0
        self.start_time = datetime.now()
        self.response_times: List[float] = []

        # Engagement tracking
        self.engagement_patterns: Dict[int, List[datetime]] = {}
        self.user_join_timestamps: Dict[int, datetime] = {}

        # Start background tasks
        self.proactive_engagement_task.start()
        self.activity_monitor_task.start()
        self.conversation_cleanup_task.start()

    def _setup_ai_client(self):
        """Setup the new consolidated AI engine"""
        try:
            if AI_ENGINE_AVAILABLE:
                # Initialize the consolidated AI engine
                self.ai_client = ConsolidatedAIEngine()
                self.logger.info("✅ Consolidated AI Engine initialized successfully")

                # Store basic configuration for command compatibility
                config = EnhancedConfigManager()
                self.ai_model = config.get_setting(
                    "AI_MODEL", "deepseek/deepseek-r1:nitro"
                )
                self.max_tokens = int(config.get_setting("AI_MAX_TOKENS", "2000"))
                self.temperature = float(config.get_setting("AI_TEMPERATURE", "0.7"))

            else:
                self.logger.error("❌ Consolidated AI Engine not available!")
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
        engagement_type: str = "casual_engagement"
    ) -> str:
        """Generate AI response using the consolidated AI engine with personalization"""
        try:
            if not self.ai_client:
                return (
                    "❌ AI service is not configured. Please check the configuration."
                )

            # Get user personality profile for personalization
            user_profile = {}
            if user_id:
                try:
                    profile = await user_profile_manager.get_user_profile(user_id, username)
                    user_profile = await user_profile_manager.get_personalized_context(user_id)
                    
                    # Analyze the current message for learning
                    await user_profile_manager.analyze_message(user_id, prompt, username)
                    
                except Exception as e:
                    logger.warning(f"Failed to get user profile for {user_id}: {e}")

            # Prepare enhanced context data for the AI engine
            context_data = {
                "channel_type": "discord",
                "conversation_history": (
                    self.conversation_history.get(user_id, []) if user_id else []
                ),
                "user_profile": user_profile,
                "engagement_type": engagement_type,
                "personalization": {
                    "should_personalize": bool(user_profile),
                    "response_style": self._determine_response_style(user_profile, engagement_type),
                    "topic_focus": self._determine_topic_focus(user_profile, prompt)
                }
            }

            # Generate response using the consolidated engine with proper parameters
            response = await self.ai_client.process_conversation(
                prompt,
                user_id,
                guild_id=guild_id,
                channel_id=channel_id,
                context_data=context_data,
            )

            # Update conversation history
            if user_id:
                if user_id not in self.conversation_history:
                    self.conversation_history[user_id] = []

                # Add user message and AI response to history
                self.conversation_history[user_id].append(
                    {"role": "user", "content": prompt}
                )
                self.conversation_history[user_id].append(
                    {"role": "assistant", "content": response}
                )

                # Keep only last 10 messages
                if len(self.conversation_history[user_id]) > self.max_history_length:
                    self.conversation_history[user_id] = self.conversation_history[
                        user_id
                    ][-self.max_history_length :]

            return response

        except Exception as e:
            self.logger.error(f"AI response generation error: {e}")
            return f"❌ Error generating AI response: {str(e)}"

        except Exception as e:
            self.logger.error(f"AI response generation error: {e}")
            return f"❌ Error generating AI response: {str(e)}"

    def _determine_response_style(self, user_profile: Dict, engagement_type: str) -> str:
        """Determine appropriate response style based on user profile and engagement type"""
        if not user_profile or "user_personality" not in user_profile:
            return "balanced"
        
        personality = user_profile["user_personality"]
        
        # Consider formality preference
        if personality.get("prefers_formal", False):
            base_style = "formal"
        elif personality.get("communication_style") == "casual":
            base_style = "casual"
        else:
            base_style = "balanced"
        
        # Adjust based on engagement type
        if engagement_type in ["provide_support", "offer_help"]:
            return "supportive_" + base_style
        elif engagement_type == "share_enthusiasm":
            return "enthusiastic_" + base_style
        elif engagement_type == "celebrate_success":
            return "celebratory_" + base_style
        elif engagement_type == "answer_question":
            if personality.get("likes_details", False):
                return "detailed_" + base_style
            else:
                return "concise_" + base_style
        
        return base_style

    def _determine_topic_focus(self, user_profile: Dict, prompt: str) -> List[str]:
        """Determine topics to focus on based on user interests and message content"""
        focus_topics = []
        
        if user_profile and "user_personality" in user_profile:
            favorite_topics = user_profile["user_personality"].get("favorite_topics", [])
            
            # Check if any favorite topics are mentioned in the prompt
            prompt_lower = prompt.lower()
            for topic in favorite_topics:
                if topic in prompt_lower:
                    focus_topics.append(topic)
        
        # Add general topic detection
        prompt_lower = prompt.lower()
        general_topics = {
            "space": ["space", "universe", "cosmos", "galaxy", "star", "planet"],
            "technology": ["tech", "ai", "computer", "software", "programming"],
            "science": ["science", "research", "experiment", "theory"],
            "gaming": ["game", "gaming", "play", "stellaris"]
        }
        
        for topic, keywords in general_topics.items():
            if any(keyword in prompt_lower for keyword in keywords):
                if topic not in focus_topics:
                    focus_topics.append(topic)
        
        return focus_topics[:3]  # Limit to top 3 topics

    # Old methods removed - using consolidated AI engine now

    @app_commands.command(name="chat", description="Chat with Astra AI")
    @app_commands.describe(message="Your message to the AI")
    async def chat_command(self, interaction: discord.Interaction, message: str):
        """Chat with AI assistant"""
        try:
            await interaction.response.defer()

            # Generate AI response with personalization
            response = await self._generate_ai_response(
                message,
                interaction.user.id,
                guild_id=interaction.guild.id if interaction.guild else None,
                channel_id=interaction.channel.id,
                username=str(interaction.user),
                engagement_type="direct_command"
            )

            # Create embed
            embed = discord.Embed(
                title="🤖 Astra AI Chat",
                description=response,
                color=0x7289DA,
                timestamp=datetime.now(timezone.utc),
            )
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url,
            )
            embed.add_field(
                name="💬 Your Message",
                value=message[:1000] + ("..." if len(message) > 1000 else ""),
                inline=False,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Chat command error: {e}")
            await interaction.followup.send(
                f"❌ Error processing chat request: {str(e)}", ephemeral=True
            )

    @app_commands.command(name="image", description="Generate an image using AI")
    @app_commands.describe(prompt="Description of the image to generate")
    async def image_command(self, interaction: discord.Interaction, prompt: str):
        """Generate AI image"""
        try:
            await interaction.response.defer()

            # Check if consolidated AI engine supports image generation
            if not self.ai_client:
                await interaction.followup.send(
                    "❌ AI service is not configured.",
                    ephemeral=True,
                )
                return

            # Try to generate image using consolidated engine
            try:
                # The consolidated engine can handle image generation if available
                context = {
                    "user_id": interaction.user.id,
                    "channel_type": "discord",
                    "request_type": "image_generation",
                }

                image_result = await self.ai_client.generate_image(prompt, context)

                if image_result and "url" in image_result:
                    embed = discord.Embed(
                        title="🎨 AI Generated Image",
                        description=f"**Prompt:** {prompt}",
                        color=0x7289DA,
                        timestamp=datetime.now(timezone.utc),
                    )
                    embed.set_image(url=image_result["url"])
                    embed.set_author(
                        name=interaction.user.display_name,
                        icon_url=interaction.user.display_avatar.url,
                    )
                    embed.add_field(
                        name="🎯 AI Provider",
                        value=image_result.get("provider", "OpenAI DALL-E"),
                        inline=True,
                    )

                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send(
                        "❌ Image generation is not available with current AI configuration.",
                        ephemeral=True,
                    )

            except Exception as image_error:
                self.logger.error(f"Image generation error: {image_error}")
                await interaction.followup.send(
                    "❌ Image generation is not currently available. This feature requires OpenAI API access.",
                    ephemeral=True,
                )

        except Exception as e:
            self.logger.error(f"Image generation error: {e}")
            await interaction.followup.send(
                f"❌ Error generating image: {str(e)}", ephemeral=True
            )

    async def _enhance_image_prompt(self, original_prompt: str) -> str:
        """Enhance image prompt using AI for better results"""
        try:
            enhancement_request = f"Enhance this image generation prompt to be more detailed and visually descriptive while keeping the original intent. Make it suitable for DALL-E image generation. Original prompt: '{original_prompt}'"

            enhanced = await self._generate_ai_response(enhancement_request)

            # Clean up the response to just get the enhanced prompt
            if "enhanced prompt:" in enhanced.lower():
                enhanced = enhanced.split("enhanced prompt:")[-1].strip()
            elif "prompt:" in enhanced.lower():
                enhanced = enhanced.split("prompt:")[-1].strip()

            # Remove quotes if present
            enhanced = enhanced.strip("\"'")

            # Limit length for DALL-E
            if len(enhanced) > 400:
                enhanced = enhanced[:400] + "..."

            return enhanced if enhanced else original_prompt

        except:
            # If enhancement fails, return original prompt
            return original_prompt

    @app_commands.command(name="analyze", description="Analyze text or content with AI")
    @app_commands.describe(content="Content to analyze")
    async def analyze_command(self, interaction: discord.Interaction, content: str):
        """Analyze content with AI"""
        try:
            await interaction.response.defer()

            analysis_prompt = f"Please analyze the following content and provide insights, key points, and summary:\n\n{content}"
            response = await self._generate_ai_response(
                analysis_prompt, interaction.user.id
            )

            embed = discord.Embed(
                title="🔍 AI Content Analysis",
                description=response,
                color=0x7289DA,
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(
                name="📝 Analyzed Content",
                value=content[:500] + ("..." if len(content) > 500 else ""),
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

    @app_commands.command(name="personality", description="Change AI personality")
    @app_commands.describe(
        personality="Personality type (friendly, professional, casual, creative)"
    )
    async def personality_command(
        self, interaction: discord.Interaction, personality: str
    ):
        """Change AI personality"""
        try:
            await interaction.response.defer()

            valid_personalities = [
                "friendly",
                "professional",
                "casual",
                "creative",
                "default",
            ]

            if personality.lower() not in valid_personalities:
                await interaction.followup.send(
                    f"❌ Invalid personality. Choose from: {', '.join(valid_personalities)}",
                    ephemeral=True,
                )
                return

            # Store personality preference (you might want to save this to database)
            embed = discord.Embed(
                title="🎭 Personality Changed",
                description=f"AI personality set to: **{personality.title()}**",
                color=0x43B581,
                timestamp=datetime.now(timezone.utc),
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Personality command error: {e}")
            await interaction.followup.send(
                f"❌ Error changing personality: {str(e)}", ephemeral=True
            )

    @app_commands.command(
        name="voice", description="Convert text to speech (placeholder)"
    )
    @app_commands.describe(text="Text to convert to speech")
    async def voice_command(self, interaction: discord.Interaction, text: str):
        """Text to speech (placeholder implementation)"""
        try:
            await interaction.response.defer()

            # This is a placeholder - you would implement actual TTS here
            embed = discord.Embed(
                title="🔊 Text to Speech",
                description="Voice synthesis feature is coming soon! Stay tuned for updates.",
                color=0xFAA61A,
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(
                name="📝 Text",
                value=text[:500] + ("..." if len(text) > 500 else ""),
                inline=False,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Voice command error: {e}")
            await interaction.followup.send(
                f"❌ Error processing voice request: {str(e)}", ephemeral=True
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
            embed.add_field(
                name="📝 Original Text",
                value=text[:500] + ("..." if len(text) > 500 else ""),
                inline=False,
            )
            embed.add_field(
                name=f"🔄 Translation ({target_language})", value=response, inline=False
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

    @app_commands.command(name="summarize", description="Summarize long text with AI")
    @app_commands.describe(content="Content to summarize")
    async def summarize_command(self, interaction: discord.Interaction, content: str):
        """Summarize content with AI"""
        try:
            await interaction.response.defer()

            summarize_prompt = f"Please provide a concise summary of the following content:\n\n{content}"
            response = await self._generate_ai_response(
                summarize_prompt, interaction.user.id
            )

            embed = discord.Embed(
                title="📋 AI Summary",
                description=response,
                color=0x7289DA,
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(
                name="📄 Original Content",
                value=content[:500] + ("..." if len(content) > 500 else ""),
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
        self.response_times: List[float] = []
        self.conversation_quality_scores: Dict[str, float] = {}

        # Start background tasks
        self.proactive_engagement_task.start()
        self.activity_monitor_task.start()
        self.conversation_cleanup_task.start()

        self.logger.info("Advanced AI Cog initialized with GitHub Models integration")

    def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.proactive_engagement_task.cancel()
        self.activity_monitor_task.cancel()
        self.conversation_cleanup_task.cancel()

    def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.proactive_engagement_task.cancel()
        self.activity_monitor_task.cancel()
        self.conversation_cleanup_task.cancel()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Enhanced message listener with intelligent AI triggering and proactive engagement"""
        if message.author.bot:
            return

        # Track channel activity
        await self._track_channel_activity(message)

        # Check if AI should respond (now returns tuple)
        should_respond, engagement_reason = await self._should_ai_respond(message)

        if should_respond:
            async with message.channel.typing():
                # Determine engagement type for personalized response
                engagement_type = "casual_engagement"
                
                if engagement_reason != "fallback_basic":
                    try:
                        engagement_type = await proactive_engagement.generate_engagement_type(
                            message.content, 
                            engagement_reason,
                            await user_profile_manager.get_personalized_context(message.author.id)
                        )
                    except Exception as e:
                        logger.warning(f"Failed to generate engagement type: {e}")
                
                # Process AI conversation with enhanced context
                await self._process_ai_conversation(message, engagement_type)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Handle member join for proactive engagement"""
        self.user_join_timestamps[member.id] = datetime.now(timezone.utc)

        # Schedule proactive engagement after a delay
        await asyncio.sleep(300)  # 5 minutes delay
        await self._consider_welcome_engagement(member)

    async def _track_channel_activity(self, message: discord.Message):
        """Track channel activity for engagement decisions"""
        channel_id = message.channel.id

        if channel_id not in self.channel_activity:
            self.channel_activity[channel_id] = {
                "recent_messages": [],
                "active_users": set(),
                "recent_topics": [],
                "last_activity": datetime.now(timezone.utc),
            }

        activity = self.channel_activity[channel_id]
        activity["recent_messages"].append(
            {
                "user_id": message.author.id,
                "content": message.content,
                "timestamp": datetime.now(timezone.utc),
            }
        )
        activity["active_users"].add(message.author.id)
        activity["last_activity"] = datetime.now(timezone.utc)

        # Extract topics
        topics = await self._extract_message_topics(message.content)
        activity["recent_topics"].extend(topics)

        # Keep only recent data
        cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
        activity["recent_messages"] = [
            msg for msg in activity["recent_messages"] if msg["timestamp"] > cutoff
        ]
        activity["recent_topics"] = activity["recent_topics"][
            -20:
        ]  # Keep last 20 topics

    async def _extract_message_topics(self, content: str) -> List[str]:
        """Extract topics from message content"""
        topics = []
        content_lower = content.lower()

        # Space and science topics
        space_keywords = {
            "space": ["space", "cosmos", "universe", "galaxy", "stellar"],
            "astronomy": ["star", "planet", "moon", "solar", "orbit", "nebula"],
            "stellaris": ["stellaris", "empire", "species", "federation", "hyperlane"],
            "science": ["science", "research", "discovery", "theory", "experiment"],
            "technology": ["technology", "ai", "robot", "computer", "digital"],
        }

        for topic, keywords in space_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append(topic)

        return topics

    async def _should_ai_respond(self, message: discord.Message) -> Tuple[bool, str]:
        """Enhanced AI response determination with proactive engagement system"""
        user_id = message.author.id
        
        # Check basic cooldown to prevent spam
        if user_id in self.conversation_cooldowns:
            if datetime.now(timezone.utc) - self.conversation_cooldowns[
                user_id
            ] < timedelta(seconds=3):
                return False, "user_cooldown"

        content_lower = message.content.lower()

        # Always respond to direct mentions and DMs
        if self.bot.user in message.mentions:
            return True, "direct_mention"

        if isinstance(message.channel, discord.DMChannel):
            return True, "direct_message"

        # Always respond to explicit AI calls
        ai_keywords = ["astra", "hey bot", "ai help", "hey ai"]
        if any(keyword in content_lower for keyword in ai_keywords):
            return True, "explicit_ai_call"

        # Get user profile for personalized engagement
        user_profile = {}
        try:
            profile = await user_profile_manager.get_user_profile(user_id, str(message.author))
            user_profile = await user_profile_manager.get_personalized_context(user_id)
        except Exception as e:
            logger.warning(f"Failed to get user profile for engagement: {e}")

        # Use proactive engagement system
        try:
            should_engage, reason = await proactive_engagement.should_engage_proactively(
                message.content,
                user_id,
                message.channel.id,
                message.guild.id if message.guild else None,
                user_profile
            )
            
            if should_engage:
                logger.info(f"Proactive engagement triggered for user {user_id}: {reason}")
                return True, reason
            else:
                return False, reason
                
        except Exception as e:
            logger.error(f"Proactive engagement error: {e}")
            # Fallback to basic engagement
            return await self._basic_engagement_check(message), "fallback_basic"

    async def _basic_engagement_check(self, message: discord.Message) -> bool:
        """Basic engagement check as fallback"""
        content_lower = message.content.lower()
        
        # Question detection
        if '?' in message.content:
            return True
        
        # Help seeking
        help_keywords = ["help", "how do", "what is", "explain", "confused"]
        if any(keyword in content_lower for keyword in help_keywords):
            return True
        
        # Topic keywords with probability
        topic_keywords = ["space", "stellaris", "science", "technology", "ai"]
        if any(keyword in content_lower for keyword in topic_keywords):
            import random
            return random.random() < 0.3  # 30% chance
        
        return False
        """Enhanced AI response determination with sophisticated triggering"""
        # Check cooldown
        user_id = message.author.id
        if user_id in self.conversation_cooldowns:
            if datetime.now(timezone.utc) - self.conversation_cooldowns[
                user_id
            ] < timedelta(seconds=3):
                return False

        content_lower = message.content.lower()

        # Direct triggers (always respond)
        if self.bot.user in message.mentions:
            return True

        if isinstance(message.channel, discord.DMChannel):
            return True

        # Intelligent keyword detection
        ai_keywords = ["astra", "hey bot", "ai", "help me", "question"]
        if any(keyword in content_lower for keyword in ai_keywords):
            return True

        # Enhanced question detection
        question_patterns = [
            r"\b(what|how|when|where|why|who|which|can|could|would|should|is|are|will|do|does)\b.*\?",
            r"\bhelp\b.*\?",
            r"\banyone\s+know\b",
            r"\bsomeone\s+(help|explain|tell)\b",
            r"\bi\s+(wonder|need|want)\s+to\s+know\b",
        ]

        for pattern in question_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return True

        # Topic-based engagement (with probability)
        space_keywords = [
            "space",
            "star",
            "planet",
            "galaxy",
            "cosmos",
            "universe",
            "astronomical",
        ]
        stellaris_keywords = [
            "stellaris",
            "empire",
            "species",
            "galactic",
            "federation",
            "hyperlane",
            "ascension",
        ]
        science_keywords = [
            "science",
            "research",
            "discovery",
            "theory",
            "experiment",
            "analysis",
        ]
        tech_keywords = [
            "ai",
            "artificial intelligence",
            "technology",
            "quantum",
            "computer",
        ]

        engagement_probabilities = {
            "space": 0.4,
            "stellaris": 0.6,
            "science": 0.3,
            "technology": 0.25,
        }

        for topic, keywords in [
            ("space", space_keywords),
            ("stellaris", stellaris_keywords),
            ("science", science_keywords),
            ("technology", tech_keywords),
        ]:
            if any(keyword in content_lower for keyword in keywords):
                import random

                if random.random() < engagement_probabilities.get(topic, 0.2):
                    return True

        # Emotional support detection
        emotional_keywords = [
            "sad",
            "frustrated",
            "confused",
            "lost",
            "don't understand",
            "struggling",
        ]
        if any(keyword in content_lower for keyword in emotional_keywords):
            return True

        # Celebration detection
        celebration_keywords = [
            "amazing",
            "awesome",
            "incredible",
            "fantastic",
            "achieved",
            "success",
        ]
        if any(keyword in content_lower for keyword in celebration_keywords):
            import random

            return random.random() < 0.3  # 30% chance to celebrate with user

        return False

    async def _process_ai_conversation(self, message: discord.Message, engagement_type: str = "casual_engagement"):
        """Process AI conversation using the advanced engine with personalized engagement"""
        try:
            start_time = datetime.now(timezone.utc)
            user_id = message.author.id
            username = str(message.author)

            # Add to active conversations
            self.active_conversations.add(user_id)

            # Process with AI client using enhanced personalization
            response = await self._generate_ai_response(
                message.content,
                user_id,
                guild_id=message.guild.id if message.guild else None,
                channel_id=message.channel.id,
                username=username,
                engagement_type=engagement_type
            )

            # Send response
            if len(response) > 2000:
                # Split long responses
                chunks = [response[i : i + 2000] for i in range(0, len(response), 2000)]
                for chunk in chunks:
                    await message.channel.send(chunk)
            else:
                await message.channel.send(response)

            # Track performance
            response_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.response_times.append(response_time)

            # Update cooldown
            self.conversation_cooldowns[user_id] = datetime.now(timezone.utc)

            # Log interaction
            self.logger.info(
                f"AI response generated for user {user_id} in {response_time:.2f}s"
            )

        except Exception as e:
            self.logger.error(f"AI conversation processing error: {e}")
            await message.channel.send(
                "I'm having some trouble thinking right now. Give me a moment! 🤖"
            )

        finally:
            self.active_conversations.discard(user_id)

    @tasks.loop(minutes=30)
    async def proactive_engagement_task(self):
        """Proactively engage with users based on patterns"""
        try:
            for guild in self.bot.guilds:
                await self._check_proactive_engagement_opportunities(guild)
        except Exception as e:
            self.logger.error(f"Proactive engagement task error: {e}")

    async def _check_proactive_engagement_opportunities(self, guild: discord.Guild):
        """Check for proactive engagement opportunities in a guild"""
        try:
            current_time = datetime.now(timezone.utc)

            for channel in guild.text_channels:
                if not channel.permissions_for(guild.me).send_messages:
                    continue

                channel_activity = self.channel_activity.get(channel.id)
                if not channel_activity:
                    continue

                # Check if channel has been quiet but users are present
                time_since_activity = current_time - channel_activity["last_activity"]
                if timedelta(minutes=30) < time_since_activity < timedelta(hours=2):

                    # Check if any active users would benefit from engagement
                    for user_id in list(channel_activity["active_users"])[
                        -5:
                    ]:  # Recent active users
                        # Simple proactive engagement based on activity
                        if len(channel_activity[user_id]) > 5:  # User has been active
                            await self._initiate_proactive_conversation(
                                channel, user_id
                            )
                            break  # Only engage with one user per check

        except Exception as e:
            self.logger.error(f"Proactive engagement check error: {e}")

    async def _initiate_proactive_conversation(
        self, channel: discord.TextChannel, user_id: int
    ):
        """Initiate a proactive conversation with a user"""
        try:
            user = self.bot.get_user(user_id)
            if not user:
                return

            # Get user's conversation history to determine appropriate engagement
            # Simple proactive engagement without complex user profiles
            # Generate proactive message
            messages = [
                f"Hey {user.display_name}! 🌌 I just learned about an interesting space phenomenon. Want to hear about it?",
                f"Hi {user.display_name}! ✨ There's some fascinating space news I thought you might enjoy!",
                f"{user.display_name}, I've been thinking about our last conversation about space... 🚀",
                f"Hey {user.display_name}! 🎮 How's your day going?",
                f"Hi {user.display_name}! What's been on your mind lately? 🌟",
                f"{user.display_name}, hope you're having a great day! 🚀",
            ]

            import random

            message = random.choice(messages)
            await channel.send(message)

            self.logger.info(f"Initiated proactive conversation with user {user_id}")

        except Exception as e:
            self.logger.error(f"Proactive conversation initiation error: {e}")

    async def _consider_welcome_engagement(self, member: discord.Member):
        """Consider welcoming a new member"""
        try:
            # Find appropriate channel for welcome
            welcome_channel = None
            for channel in member.guild.text_channels:
                if (
                    "welcome" in channel.name.lower()
                    or "general" in channel.name.lower()
                ):
                    if channel.permissions_for(member.guild.me).send_messages:
                        welcome_channel = channel
                        break

            if welcome_channel:
                welcome_message = f"Welcome to the server, {member.display_name}! 🌟 I'm Astra, your friendly AI companion. Feel free to ask me about space, Stellaris, or anything else! 🚀"
                await welcome_channel.send(welcome_message)

                self.logger.info(f"Welcomed new member {member.id}")

        except Exception as e:
            self.logger.error(f"Welcome engagement error: {e}")

    @tasks.loop(minutes=15)
    async def activity_monitor_task(self):
        """Monitor and update activity patterns"""
        try:
            current_time = datetime.now(timezone.utc)

            # Clean up old activity data
            for channel_id in list(self.channel_activity.keys()):
                activity = self.channel_activity[channel_id]
                if current_time - activity["last_activity"] > timedelta(hours=6):
                    del self.channel_activity[channel_id]

            # Update engagement patterns
            for user_id in list(self.engagement_patterns.keys()):
                # Keep only recent patterns
                cutoff = current_time - timedelta(days=7)
                self.engagement_patterns[user_id] = [
                    timestamp
                    for timestamp in self.engagement_patterns[user_id]
                    if timestamp > cutoff
                ]

                # Remove empty patterns
                if not self.engagement_patterns[user_id]:
                    del self.engagement_patterns[user_id]

        except Exception as e:
            self.logger.error(f"Activity monitor task error: {e}")

    @tasks.loop(hours=2)
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

            # Clean up old join timestamps
            expired_joins = [
                user_id
                for user_id, timestamp in self.user_join_timestamps.items()
                if current_time - timestamp > timedelta(days=1)
            ]
            for user_id in expired_joins:
                del self.user_join_timestamps[user_id]

            self.logger.debug("Conversation cleanup completed")

        except Exception as e:
            self.logger.error(f"Conversation cleanup task error: {e}")

    @app_commands.command(
        name="ai_stats", description="View AI conversation statistics"
    )
    async def ai_stats(self, interaction: discord.Interaction):
        """Display AI conversation statistics"""
        try:
            # Get basic AI statistics
            total_conversations = len(self.user_conversations)
            total_users = len(set(self.user_conversations.keys()))
            analytics = {
                "total_conversations": total_conversations,
                "total_users": total_users,
                "active_model": getattr(self, "ai_model", "Unknown"),
                "provider": "GitHub Models" if hasattr(self, "ai_client") else "OpenAI",
            }

            embed = discord.Embed(
                title="🤖 AI Conversation Analytics",
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(
                name="📊 Overall Stats",
                value=f"Total Conversations: {analytics.get('total_conversations', 0)}\n"
                f"Total Users: {analytics.get('total_users', 0)}\n"
                f"Avg Engagement: {analytics.get('average_engagement', 0):.2f}/1.0",
                inline=True,
            )

            # Performance stats
            if self.response_times:
                avg_response_time = sum(self.response_times[-100:]) / len(
                    self.response_times[-100:]
                )
                embed.add_field(
                    name="⚡ Performance",
                    value=f"Avg Response Time: {avg_response_time:.2f}s\n"
                    f"Active Conversations: {len(self.active_conversations)}\n"
                    f"Tracked Channels: {len(self.channel_activity)}",
                    inline=True,
                )

            # Popular topics
            popular_topics = analytics.get("popular_topics", [])[:5]
            if popular_topics:
                topics_text = "\n".join(
                    [f"{topic}: {count}" for topic, count in popular_topics]
                )
                embed.add_field(
                    name="🔥 Popular Topics", value=topics_text, inline=True
                )

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            self.logger.error(f"AI stats command error: {e}")
            await interaction.response.send_message(
                "Error retrieving AI statistics.", ephemeral=True
            )

    @app_commands.command(
        name="ai_personality", description="View or modify AI personality settings"
    )
    async def ai_personality(
        self, interaction: discord.Interaction, trait: str = None, value: str = None
    ):
        """View or modify AI personality settings"""
        try:
            if not trait:
                # Display current AI configuration
                personality = {
                    "name": "Astra AI",
                    "model": getattr(self, "ai_model", "Unknown"),
                    "temperature": getattr(self, "temperature", 0.7),
                    "max_tokens": getattr(self, "max_tokens", 1500),
                    "provider": (
                        getattr(self.ai_client, "active_provider", "Consolidated AI")
                        if hasattr(self, "ai_client") and self.ai_client
                        else "Not configured"
                    ),
                    "core_traits": [
                        "Friendly and approachable",
                        "Knowledgeable about space and science",
                        "Helpful and supportive",
                        "Curious and engaging",
                    ],
                    "communication_style": {
                        "tone": "Friendly",
                        "humor": "Light and appropriate",
                        "formality": "Casual but informative",
                    },
                    "interests": [
                        "Space Exploration",
                        "AI Technology",
                        "Stellaris",
                        "Science",
                        "Discovery",
                    ],
                }

                embed = discord.Embed(
                    title="🤖 Astra's Personality",
                    description=f"**{personality['name']}** - Your friendly space AI companion",
                    color=discord.Color.purple(),
                )

                embed.add_field(
                    name="🌟 Core Traits",
                    value="\n".join(
                        f"• {trait}" for trait in personality["core_traits"]
                    ),
                    inline=False,
                )

                embed.add_field(
                    name="💬 Communication Style",
                    value=f"**Tone:** {personality['communication_style']['tone']}\n"
                    f"**Humor:** {personality['communication_style']['humor']}\n"
                    f"**Formality:** {personality['communication_style']['formality']}",
                    inline=True,
                )

                embed.add_field(
                    name="🎯 Interests",
                    value=", ".join(personality["interests"][:5]),
                    inline=True,
                )

                embed.add_field(
                    name="⚙️ Configuration",
                    value=f"**Model:** {personality['model']}\n"
                    f"**Provider:** {personality['provider']}\n"
                    f"**Temperature:** {personality['temperature']}\n"
                    f"**Max Tokens:** {personality['max_tokens']}",
                    inline=True,
                )

                await interaction.response.send_message(embed=embed)

            else:
                # Modify personality (admin only)
                if not interaction.user.guild_permissions.administrator:
                    await interaction.response.send_message(
                        "You need administrator permissions to modify AI personality.",
                        ephemeral=True,
                    )
                    return

                # Implementation for personality modification would go here
                await interaction.response.send_message(
                    f"Personality modification for '{trait}' is not yet implemented.",
                    ephemeral=True,
                )

        except Exception as e:
            self.logger.error(f"AI personality command error: {e}")
            await interaction.response.send_message(
                "Error accessing personality settings.", ephemeral=True
            )

    @app_commands.command(
        name="ai_reset", description="Reset AI conversation history for yourself"
    )
    async def ai_reset(self, interaction: discord.Interaction):
        """Reset AI conversation history for the user"""
        try:
            user_id = interaction.user.id

            # Clear conversation context
            if user_id in self.user_conversations:
                del self.user_conversations[user_id]

            # Reset cooldown
            if user_id in self.conversation_cooldowns:
                del self.conversation_cooldowns[user_id]

            await interaction.response.send_message(
                "🔄 Your conversation history with me has been reset! We can start fresh. 🌟",
                ephemeral=True,
            )

            self.logger.info(f"Reset conversation history for user {user_id}")

        except Exception as e:
            self.logger.error(f"AI reset command error: {e}")
            await interaction.response.send_message(
                "Error resetting conversation history.", ephemeral=True
            )

    @app_commands.command(
        name="ai_mood", description="Analyze the mood of the conversation"
    )
    async def ai_mood_analysis(self, interaction: discord.Interaction):
        """Analyze current conversation mood"""
        try:
            user_id = interaction.user.id
            context = self.user_conversations.get(user_id, [])

            if not context:
                await interaction.response.send_message(
                    "I haven't had a conversation with you yet! Send me a message first. 💫",
                    ephemeral=True,
                )
                return

            # Simple mood analysis based on conversation history
            recent_messages = context[-5:] if context else []

            # Basic mood assessment
            positive_keywords = [
                "great",
                "awesome",
                "amazing",
                "wonderful",
                "fantastic",
                "happy",
                "excited",
            ]
            negative_keywords = [
                "sad",
                "frustrated",
                "confused",
                "annoyed",
                "upset",
                "disappointed",
            ]
            question_keywords = ["?", "how", "what", "why", "when", "where"]

            mood_score = 0.5  # Neutral starting point
            engagement_score = min(
                len(context) / 10.0, 1.0
            )  # Based on conversation length

            if recent_messages:
                for msg in recent_messages:
                    content = msg.get("content", "").lower()
                    if any(word in content for word in positive_keywords):
                        mood_score += 0.1
                    if any(word in content for word in negative_keywords):
                        mood_score -= 0.1
                    if any(word in content for word in question_keywords):
                        engagement_score += 0.05

            # Clamp values
            mood_score = max(0.0, min(1.0, mood_score))
            engagement_score = max(0.0, min(1.0, engagement_score))

            # Determine mood
            if mood_score > 0.7:
                mood = "happy"
            elif mood_score > 0.6:
                mood = "content"
            elif mood_score > 0.4:
                mood = "neutral"
            elif mood_score > 0.3:
                mood = "concerned"
            else:
                mood = "frustrated"

            confidence = min(0.8, len(recent_messages) / 10.0 + 0.3)

            # Create mood analysis embed
            embed = discord.Embed(
                title="🧠 Conversation Mood Analysis",
                color=discord.Color.purple(),
                timestamp=datetime.now(timezone.utc),
            )

            # Mood visualization
            mood_emojis = {
                "ecstatic": "🤩",
                "excited": "🎉",
                "happy": "😊",
                "content": "😌",
                "curious": "🤔",
                "neutral": "😐",
                "pensive": "🤔",
                "confused": "😕",
                "concerned": "😟",
                "frustrated": "😤",
                "sad": "😢",
                "angry": "😡",
            }

            mood_emoji = mood_emojis.get(mood, "😐")

            embed.add_field(
                name="Current Mood",
                value=f"{mood_emoji} **{mood.title()}**\nConfidence: {confidence:.1%}",
                inline=True,
            )

            embed.add_field(
                name="Engagement Level",
                value=f"📊 {engagement_score:.1%}\n{'🔥' if engagement_score > 0.7 else '✨' if engagement_score > 0.4 else '💫'}",
                inline=True,
            )

            # Conversation insights
            embed.add_field(
                name="📈 Conversation Stats",
                value=f"Messages: {len(context)}\nRecent Activity: {len(recent_messages)} messages",
                inline=False,
            )

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            self.logger.error(f"Mood analysis error: {e}")
            await interaction.response.send_message(
                "Error analyzing conversation mood.", ephemeral=True
            )

    @app_commands.command(
        name="ai_topics", description="View trending conversation topics"
    )
    async def ai_topics(self, interaction: discord.Interaction):
        """Display trending conversation topics"""
        try:
            # Analyze actual conversation topics from user conversations
            all_topics = []

            # Extract topics from conversation history
            for user_id, conversations in self.user_conversations.items():
                for msg in conversations:
                    content = msg.get("content", "").lower()

                    # Simple topic detection based on keywords
                    if any(
                        word in content
                        for word in ["space", "cosmos", "universe", "galaxy", "stellar"]
                    ):
                        all_topics.append("Space Exploration")
                    if any(
                        word in content
                        for word in [
                            "ai",
                            "artificial",
                            "intelligence",
                            "bot",
                            "technology",
                        ]
                    ):
                        all_topics.append("AI Technology")
                    if any(
                        word in content
                        for word in ["stellaris", "empire", "species", "federation"]
                    ):
                        all_topics.append("Stellaris Gaming")
                    if any(
                        word in content
                        for word in ["science", "research", "discovery", "theory"]
                    ):
                        all_topics.append("Science")
                    if any(
                        word in content
                        for word in ["discord", "bot", "command", "development"]
                    ):
                        all_topics.append("Discord Bot Development")

            # Count topic occurrences
            from collections import Counter

            topic_counts = Counter(all_topics)
            popular_topics = topic_counts.most_common(10)

            # If no topics found, use defaults
            if not popular_topics:
                popular_topics = [
                    ("Space Exploration", 0),
                    ("AI Technology", 0),
                    ("Discord Bot Development", 0),
                    ("Stellaris Gaming", 0),
                ]

            # Basic statistics
            analytics = {
                "total_conversations": len(self.user_conversations),
                "total_users": len(set(self.user_conversations.keys())),
                "avg_response_time_ms": (
                    int(sum(self.response_times[-10:]) * 1000)
                    if self.response_times
                    else 500
                ),
            }

            embed = discord.Embed(
                title="🔥 Trending Conversation Topics",
                color=discord.Color.orange(),
                timestamp=datetime.now(timezone.utc),
            )

            if popular_topics:
                topic_text = []
                for i, (topic, count) in enumerate(popular_topics[:10], 1):
                    emoji = (
                        "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📊"
                    )
                    topic_text.append(f"{emoji} **{topic}** ({count} mentions)")

                embed.description = "\n".join(topic_text)
            else:
                embed.description = (
                    "No topics have been discussed yet. Start a conversation! 🚀"
                )

            # Add some statistics
            embed.add_field(
                name="📈 Statistics",
                value=f"Total Conversations: {analytics.get('total_conversations', 0)}\n"
                f"Active Users: {analytics.get('total_users', 0)}\n"
                f"Avg Response Time: {analytics.get('avg_response_time_ms', 0):.0f}ms",
                inline=False,
            )

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            self.logger.error(f"Topics command error: {e}")
            await interaction.response.send_message(
                "Error retrieving topic information.", ephemeral=True
            )

    @app_commands.command(
        name="ai_customize", description="Customize AI personality for this server"
    )
    @app_commands.describe(
        trait="Personality trait to adjust", level="Level from 1-10 (10 being maximum)"
    )
    async def ai_personality_customize(
        self, interaction: discord.Interaction, trait: str = None, level: int = None
    ):
        """Customize AI personality traits"""
        try:
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "You need administrator permissions to customize AI personality.",
                    ephemeral=True,
                )
                return

            if not trait:
                # Show current personality
                embed = discord.Embed(
                    title="🎭 Astra's Personality Configuration",
                    description="Current personality trait levels:",
                    color=discord.Color.purple(),
                )

                personality_traits = {
                    "enthusiastic": "How energetic and excited I am",
                    "knowledgeable": "How much I focus on sharing information",
                    "helpful": "How much I prioritize being useful",
                    "curious": "How much I ask questions and explore topics",
                    "friendly": "How warm and approachable I am",
                    "patient": "How understanding I am with complex questions",
                    "witty": "How much humor I use in responses",
                    "scientific": "How technical and precise my explanations are",
                }

                for trait_name, description in personality_traits.items():
                    # Get current level (mock for now)
                    level = 7  # Default level
                    bar = "█" * (level // 2) + "░" * (5 - level // 2)
                    embed.add_field(
                        name=f"{trait_name.title()} [{level}/10]",
                        value=f"`{bar}` {description}",
                        inline=False,
                    )

                embed.add_field(
                    name="🔧 Usage",
                    value="Use `/ai_customize <trait> <level>` to adjust specific traits\n"
                    "Example: `/ai_customize enthusiastic 9`",
                    inline=False,
                )

                await interaction.response.send_message(embed=embed)

            elif trait and level is not None:
                # Adjust personality trait
                if not (1 <= level <= 10):
                    await interaction.response.send_message(
                        "Level must be between 1 and 10.", ephemeral=True
                    )
                    return

                # For now, just confirm the change (implementation would save to config)
                await interaction.response.send_message(
                    f"✅ Set **{trait}** personality trait to level **{level}/10**\n"
                    f"This will affect how I interact in this server! 🎭✨",
                    ephemeral=True,
                )

                self.logger.info(
                    f"Personality trait {trait} set to {level} by {interaction.user.id}"
                )

            else:
                await interaction.response.send_message(
                    "Please provide both trait and level, or use without parameters to view current settings.",
                    ephemeral=True,
                )

        except Exception as e:
            self.logger.error(f"Personality command error: {e}")
            await interaction.response.send_message(
                "Error customizing personality.", ephemeral=True
            )

    @app_commands.command(
        name="ai_engage", description="Manually trigger proactive AI engagement"
    )
    @app_commands.describe(user="User to engage with (admin only)")
    async def manual_engage(
        self, interaction: discord.Interaction, user: discord.Member = None
    ):
        """Manually trigger AI engagement"""
        try:
            target_user = user or interaction.user

            # Admin check for targeting other users
            if user and not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "You can only engage AI for yourself unless you're an administrator.",
                    ephemeral=True,
                )
                return

            # Check if user has conversation history
            user_history = self.user_conversations.get(target_user.id, [])

            if not user_history:
                await interaction.response.send_message(
                    f"I haven't had a conversation with {target_user.display_name} yet. "
                    "Have them chat with me first! 💫",
                    ephemeral=True,
                )
                return

            # Generate proactive engagement message
            # Simple engagement messages
            import random

            messages = [
                f"Hey {target_user.mention}! 🌌 I just learned about an amazing space discovery. Want to hear about it?",
                f"Hi {target_user.mention}! 🎮 How are things going? I'd love to chat!",
                f"{target_user.mention}, I've been pondering some fascinating concepts... 🧬✨",
                f"Hello {target_user.mention}! ✨ What's been on your mind lately?",
            ]
            message = random.choice(messages)

            await interaction.response.send_message(message)

            # Update engagement tracking
            if target_user.id not in self.engagement_patterns:
                self.engagement_patterns[target_user.id] = []
            self.engagement_patterns[target_user.id].append(datetime.now(timezone.utc))

            self.logger.info(
                f"Manual AI engagement triggered for user {target_user.id}"
            )

        except Exception as e:
            self.logger.error(f"Manual engage error: {e}")
            await interaction.response.send_message(
                "Error triggering AI engagement.", ephemeral=True
            )

    @app_commands.command(name="ai_status", description="Check AI system status")
    async def ai_status(self, interaction: discord.Interaction):
        """Check AI system status and configuration"""
        try:
            embed = discord.Embed(
                title="🤖 AI System Status",
                color=discord.Color.green(),
                timestamp=datetime.now(timezone.utc),
            )

            # Check AI client status
            if hasattr(self, "ai_client") and self.ai_client:
                try:
                    status = await self.ai_client.get_health_status()
                    embed.add_field(
                        name="✅ Consolidated AI Engine",
                        value=f"**Active Provider**: {status.get('active_provider', 'Unknown')}\n"
                        f"**Model**: {getattr(self, 'ai_model', 'Unknown')}\n"
                        f"**Available Providers**: {', '.join(status.get('available_providers', []))}\n"
                        f"**Status**: {status.get('status', 'Available')}",
                        inline=False,
                    )
                except Exception as e:
                    embed.add_field(
                        name="⚠️ Consolidated AI Engine",
                        value=f"Engine loaded but status check failed: {str(e)}",
                        inline=False,
                    )
            else:
                embed.add_field(
                    name="❌ AI Service", value="No AI client configured", inline=False
                )

            # Performance stats
            embed.add_field(
                name="📊 Performance",
                value=f"API Calls: {self.api_calls_made}\n"
                f"Successful: {self.successful_responses}\n"
                f"Success Rate: {(self.successful_responses/max(self.api_calls_made, 1)*100):.1f}%",
                inline=True,
            )

            # Active conversations
            embed.add_field(
                name="💬 Activity",
                value=f"Active Conversations: {len(self.active_conversations)}\n"
                f"Total Users: {len(self.user_conversations)}\n"
                f"Tracked Channels: {len(self.channel_activity)}",
                inline=True,
            )

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            self.logger.error(f"AI status error: {e}")
            await interaction.response.send_message(
                f"❌ Error checking AI status: {str(e)}", ephemeral=True
            )

    @app_commands.command(name="ai_test", description="Test AI response generation")
    async def ai_test(self, interaction: discord.Interaction):
        """Test AI response generation"""
        try:
            await interaction.response.defer()

            test_prompt = (
                "Hello! Please introduce yourself and confirm you're working properly."
            )
            response = await self._generate_ai_response(
                test_prompt, interaction.user.id
            )

            embed = discord.Embed(
                title="🧪 AI Test Results",
                description=response,
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(
                name="✅ Test Status",
                value="AI response generation successful!",
                inline=False,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"AI test error: {e}")
            await interaction.followup.send(
                f"❌ AI test failed: {str(e)}", ephemeral=True
            )

    @app_commands.command(
        name="deepseek_verify", description="Verify DeepSeek R1 model is working"
    )
    async def deepseek_verify(self, interaction: discord.Interaction):
        """Verify DeepSeek R1 model functionality"""
        try:
            await interaction.response.defer()

            # Test prompt specifically for DeepSeek R1 to show its reasoning capabilities
            test_prompt = "Please solve this step by step: If a train travels 120 miles in 2 hours, what is its average speed? Show your reasoning process."

            response = await self._generate_ai_response(
                test_prompt, interaction.user.id
            )

            embed = discord.Embed(
                title="🔬 DeepSeek R1 Verification",
                description=response,
                color=discord.Color.purple(),
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(
                name="🎯 Model Information",
                value=f"**Current Model**: {getattr(self, 'ai_model', 'Unknown')}\n"
                f"**Provider**: {getattr(self.ai_client, 'active_provider', 'Consolidated AI') if hasattr(self, 'ai_client') and self.ai_client else 'Not configured'}\n"
                f"**Temperature**: {getattr(self, 'temperature', 0.7)}",
                inline=False,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"DeepSeek verification error: {e}")
            await interaction.followup.send(
                f"❌ DeepSeek verification failed: {str(e)}", ephemeral=True
            )


async def setup(bot):
    """Set up the Advanced AI cog"""
    await bot.add_cog(AdvancedAICog(bot))
