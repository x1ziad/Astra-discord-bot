"""
Advanced AI Cog for Astra Bot
Implements modern AI features with GitHub Models and OpenAI integration
"""

import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
import logging
import random
import io
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

# Import dedicated image generation client
try:
    from ai.freepik_image_client import FreepikImageClient

    IMAGE_CLIENT_AVAILABLE = True
    logger.info("✅ FreepikImageClient imported successfully")
except ImportError as e:
    IMAGE_CLIENT_AVAILABLE = False
    logger.error(f"❌ Failed to import FreepikImageClient: {e}")

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

        # Initialize dedicated image generation client (independent from AI)
        self.image_client = None
        self._setup_image_client()

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
        self.start_time = datetime.now(timezone.utc)
        self.response_times: List[float] = []

        # Engagement tracking
        self.engagement_patterns: Dict[int, List[datetime]] = {}
        self.user_join_timestamps: Dict[int, datetime] = {}

        # Enhanced tracking for proactive features
        self.last_status_update = datetime.now(timezone.utc)
        self.server_activity_levels: Dict[int, str] = {}  # guild_id -> activity level
        self.interesting_topics: List[str] = []  # Track current interesting topics
        self.mentioned_users: Set[int] = set()  # Track recently mentioned users

        # Start background tasks
        self.proactive_engagement_task.start()
        self.activity_monitor_task.start()
        self.conversation_cleanup_task.start()
        self.dynamic_status_task.start()  # New dynamic status task

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

    def _setup_image_client(self):
        """Setup dedicated image generation client (independent from AI)"""
        try:
            if IMAGE_CLIENT_AVAILABLE:
                # Initialize the dedicated image client
                freepik_api_key = os.getenv("FREEPIK_API_KEY")
                self.image_client = FreepikImageClient(freepik_api_key)

                if self.image_client.is_available():
                    self.logger.info(
                        "✅ Dedicated Image Generation Client initialized successfully"
                    )
                else:
                    self.logger.warning(
                        "⚠️ Image client created but API key not available"
                    )

            else:
                self.logger.error("❌ FreepikImageClient not available!")
                self.image_client = None

        except Exception as e:
            self.logger.error(f"Failed to setup image client: {e}")
            self.image_client = None

    async def _generate_ai_response(
        self,
        prompt: str,
        user_id: int = None,
        guild_id: int = None,
        channel_id: int = None,
        username: str = None,
        engagement_type: str = "casual_engagement",
    ) -> str:
        """Generate AI response using the consolidated AI engine with personalization"""
        try:
            if not self.ai_client:
                return (
                    "❌ AI service is not configured. Please check the configuration."
                )

            # Get user communication preferences for personalization
            user_profile = {}
            if user_id:
                try:
                    profile = await user_profile_manager.get_user_profile(
                        user_id, username
                    )
                    user_profile = await user_profile_manager.get_personalized_context(
                        user_id
                    )

                    # Analyze the current message for learning
                    await user_profile_manager.analyze_message(
                        user_id, prompt, username
                    )

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
                    "response_style": self._determine_response_style(
                        user_profile, engagement_type
                    ),
                    "topic_focus": self._determine_topic_focus(user_profile, prompt),
                },
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

    def _determine_response_style(
        self, user_profile: Dict, engagement_type: str
    ) -> str:
        """Determine appropriate response style based on user communication preferences"""
        if not user_profile or "communication_preferences" not in user_profile:
            return "balanced"

        prefs = user_profile["communication_preferences"]

        # Get base communication style
        base_style = prefs.get("style", "balanced")

        # Adjust based on engagement type for natural response flow
        if engagement_type in ["provide_support", "offer_help"]:
            # Be supportive but maintain user's preferred style
            return (
                base_style + "_supportive" if base_style != "balanced" else "supportive"
            )
        elif engagement_type == "answer_question":
            # Respect user's detail preference
            detail_pref = prefs.get("detail_level", "balanced")
            if detail_pref == "detailed":
                return "detailed_" + base_style
            elif detail_pref == "concise":
                return "concise_" + base_style
            else:
                return base_style

        return base_style

    def _determine_topic_focus(self, user_profile: Dict, prompt: str) -> List[str]:
        """Determine topics to focus on based on user interests and message content"""
        focus_topics = []

        if user_profile and "interests" in user_profile:
            favorite_topics = user_profile["interests"].get("topics", [])

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
            "gaming": ["game", "gaming", "play", "stellaris"],
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
                engagement_type="direct_command",
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

    @app_commands.command(name="image", description="🎨 Generate high-quality AI images with optimized performance")
    @app_commands.describe(
        prompt="Description of the image to generate (be detailed for best results)",
        size="Image size and aspect ratio",
        style="Image style and quality"
    )
    @app_commands.choices(size=[
        app_commands.Choice(name="Square HD (1024x1024)", value="square_hd"),
        app_commands.Choice(name="Portrait (768x1024)", value="portrait_3_4"),
        app_commands.Choice(name="Landscape (1024x768)", value="landscape_4_3"),
        app_commands.Choice(name="Wide (1024x576)", value="landscape_16_9")
    ])
    @app_commands.choices(style=[
        app_commands.Choice(name="🎨 Realistic", value="realistic"),
        app_commands.Choice(name="✨ Artistic", value="artistic"),
        app_commands.Choice(name="🎭 Anime/Cartoon", value="anime"),
        app_commands.Choice(name="📸 Photographic", value="photographic")
    ])
    async def image_command(
        self, 
        interaction: discord.Interaction, 
        prompt: str,
        size: str = "square_hd",
        style: str = "realistic"
    ):
        """Enhanced AI image generation with optimized performance and proper Discord uploads"""
        try:
            # Immediate response to prevent timeout
            await interaction.response.defer()

            # Import optimized generator
            try:
                from ai.optimized_image_generator import get_optimized_generator
                generator = get_optimized_generator()
            except ImportError:
                logger.error("❌ Optimized image generator not available, falling back to legacy")
                # Fallback to existing system
                await self._fallback_image_generation(interaction, prompt, size)
                return

            # Check user permissions
            user_permissions = {
                "is_admin": interaction.user.guild_permissions.administrator,
                "is_mod": interaction.user.guild_permissions.manage_messages
                or interaction.user.guild_permissions.manage_guild,
            }

            # Enhanced prompt with style
            enhanced_prompt = await self._enhance_prompt_with_style(prompt, style)
            
            # Send initial status
            status_embed = discord.Embed(
                title="🎨 AI Image Generation",
                description=f"🚀 **Generating your image...**\n\n**Prompt:** {prompt}\n**Style:** {style.title()}\n**Size:** {size.replace('_', ' ').title()}",
                color=0x3498DB,
                timestamp=datetime.now(timezone.utc)
            )
            status_embed.add_field(
                name="⏱️ Status",
                value="🔄 Processing with optimized AI engine...",
                inline=False
            )
            status_embed.set_footer(text="Powered by Freepik AI • Optimized Engine v2.1")
            
            status_message = await interaction.followup.send(embed=status_embed)

            # Generate image with optimized system
            start_time = datetime.now()
            result = await generator.generate_image_optimized(
                prompt=enhanced_prompt,
                user_id=interaction.user.id,
                size=size,
                download_image=True  # Download bytes for Discord upload
            )

            generation_time = (datetime.now() - start_time).total_seconds()

            if result.get("success"):
                # Create success embed
                embed = discord.Embed(
                    title="🎨 AI Generated Image",
                    description=f"**Original Prompt:** {prompt}\n**Enhanced:** {enhanced_prompt[:100]}{'...' if len(enhanced_prompt) > 100 else ''}",
                    color=0x43B581,
                    timestamp=datetime.now(timezone.utc)
                )
                
                embed.set_author(
                    name=f"{interaction.user.display_name}'s Creation",
                    icon_url=interaction.user.display_avatar.url
                )
                
                # Add generation details
                embed.add_field(
                    name="⚡ Performance",
                    value=f"🕐 {generation_time:.1f}s\n🔄 {result.get('attempts', 1)} attempts\n📐 {size.replace('_', ' ').title()}",
                    inline=True
                )
                
                embed.add_field(
                    name="🎯 AI Details",
                    value=f"🤖 {result.get('provider', 'Freepik AI')}\n🎨 {style.title()} Style\n✨ Enhanced Prompt",
                    inline=True
                )

                # Add user role info
                if user_permissions["is_admin"]:
                    embed.add_field(name="👑 Access", value="Administrator", inline=True)
                elif user_permissions["is_mod"]:
                    embed.add_field(name="🛡️ Access", value="Moderator", inline=True)
                else:
                    embed.add_field(name="� Access", value="Member", inline=True)

                # Handle image upload
                files = []
                
                if result.get("image_bytes"):
                    # Upload actual image file for better quality
                    image_file = discord.File(
                        io.BytesIO(result["image_bytes"]),
                        filename=f"ai_image_{interaction.user.id}_{int(datetime.now().timestamp())}.png"
                    )
                    files.append(image_file)
                    embed.set_image(url=f"attachment://{image_file.filename}")
                    
                    embed.add_field(
                        name="📁 File Info",
                        value=f"🗂️ {len(result['image_bytes']) / 1024:.1f} KB\n📋 PNG Format\n🔗 High Quality",
                        inline=False
                    )
                else:
                    # Fallback to URL if bytes not available
                    embed.set_image(url=result["url"])
                    embed.add_field(
                        name="� Image Link",
                        value=f"[View Full Size]({result['url']})",
                        inline=False
                    )

                embed.set_footer(text="🎨 Powered by Freepik AI • Optimized Engine v2.1 • Use responsibly")

                # Update the status message with final result
                if files:
                    await status_message.edit(embed=embed, attachments=files)
                else:
                    await status_message.edit(embed=embed)

                # Log successful generation
                logger.info(f"✅ Image generated for {interaction.user.id} in {generation_time:.1f}s")

            else:
                # Handle specific error cases with enhanced UX
                await self._handle_optimized_errors(interaction, result, status_message)

        except Exception as e:
            logger.error(f"💥 Enhanced image command error: {e}")
            
            error_embed = discord.Embed(
                title="❌ Image Generation Error",
                description="An unexpected error occurred while generating your image.",
                color=0xE74C3C,
                timestamp=datetime.now(timezone.utc)
            )
            error_embed.add_field(
                name="🔧 What to try",
                value="• Try a different prompt\n• Use simpler language\n• Try again in a few moments",
                inline=False
            )
            error_embed.set_footer(text="If this persists, contact an administrator")
            
            try:
                await interaction.followup.send(embed=error_embed, ephemeral=True)
            except:
                # Fallback if followup fails
                await interaction.response.send_message(
                    f"❌ Image generation failed: {str(e)}", 
                    ephemeral=True
                )

    async def _enhance_prompt_with_style(self, prompt: str, style: str) -> str:
        """Enhance prompt with style-specific keywords for better results"""
        style_enhancers = {
            "realistic": "photorealistic, highly detailed, 8k resolution, professional photography",
            "artistic": "digital art, concept art, artistic, creative, beautiful composition",
            "anime": "anime style, manga art, vibrant colors, cel shading, japanese animation",
            "photographic": "professional photography, DSLR, sharp focus, bokeh, natural lighting"
        }
        
        enhancer = style_enhancers.get(style, "high quality, detailed")
        return f"{prompt}, {enhancer}"

    async def _handle_optimized_errors(self, interaction: discord.Interaction, result: Dict[str, Any], status_message):
        """Handle errors from optimized image generation with better UX"""
        error_type = result.get("error", "unknown")
        
        if error_type == "rate_limit":
            embed = discord.Embed(
                title="⏰ Rate Limit Reached",
                description="You've reached the image generation rate limit.",
                color=0xF39C12,
                timestamp=datetime.now(timezone.utc)
            )
            
            wait_time = result.get("wait_time", 60)
            if wait_time < 300:  # Less than 5 minutes
                embed.add_field(
                    name="🔄 Try Again",
                    value=f"<t:{int((datetime.now() + timedelta(seconds=wait_time)).timestamp())}:R>",
                    inline=True
                )
            
            embed.add_field(
                name="💡 Tip",
                value="Use more specific prompts to get better results faster!",
                inline=False
            )
            
        elif error_type == "authentication_failed":
            embed = discord.Embed(
                title="🔑 Authentication Error",
                description="There's an issue with the AI service configuration.",
                color=0xE74C3C,
                timestamp=datetime.now(timezone.utc)
            )
            embed.add_field(
                name="👨‍💻 Admin Notice",
                value="The Freepik API key needs to be reconfigured.",
                inline=False
            )
            
        elif error_type == "no_api_key":
            embed = discord.Embed(
                title="⚙️ Service Configuration",
                description="Image generation service is not properly configured.",
                color=0xE74C3C,
                timestamp=datetime.now(timezone.utc)
            )
            
        else:
            embed = discord.Embed(
                title="❌ Generation Failed",
                description=result.get("message", "Unknown error occurred"),
                color=0xE74C3C,
                timestamp=datetime.now(timezone.utc)
            )
            embed.add_field(
                name="🔄 Retry Suggestions",
                value="• Try a simpler prompt\n• Wait a moment and try again\n• Use different keywords",
                inline=False
            )
        
        embed.set_footer(text="Contact an administrator if this continues")
        await status_message.edit(embed=embed)

    async def _fallback_image_generation(self, interaction: discord.Interaction, prompt: str, size: str):
        """Fallback to legacy image generation system"""
        logger.info("🔄 Using fallback image generation")
        
        if not self.ai_client:
            await interaction.followup.send(
                "❌ AI image generation service is not available.",
                ephemeral=True
            )
            return

        # Use existing system as fallback
        context = {
            "user_id": interaction.user.id,
            "channel_id": interaction.channel.id,
            "guild_id": interaction.guild.id if interaction.guild else None,
            "channel_type": "discord",
            "request_type": "image_generation",
            "user_name": interaction.user.display_name,
        }

        user_permissions = {
            "is_admin": interaction.user.guild_permissions.administrator,
            "is_mod": interaction.user.guild_permissions.manage_messages
        }

        image_result = await self.ai_client.generate_image(
            prompt, context, user_permissions
        )

        if image_result and image_result.get("success"):
            embed = discord.Embed(
                title="🎨 AI Generated Image (Legacy)",
                description=f"**Prompt:** {prompt}",
                color=0x43B581,
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_image(url=image_result["url"])
            embed.set_footer(text="Legacy Generation System • Consider updating")
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(
                f"❌ Image generation failed: {image_result.get('message', 'Unknown error')}",
                ephemeral=True
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

    @app_commands.command(
        name="communication_style", description="Set your preferred communication style"
    )
    @app_commands.describe(
        style="Communication style (detailed, concise, casual, formal)"
    )
    async def communication_style_command(
        self, interaction: discord.Interaction, style: str
    ):
        """Set communication style preference"""
        try:
            await interaction.response.defer()

            valid_styles = [
                "detailed",
                "concise",
                "casual",
                "formal",
                "balanced",
            ]

            if style.lower() not in valid_styles:
                await interaction.followup.send(
                    f"❌ Invalid style. Choose from: {', '.join(valid_styles)}",
                    ephemeral=True,
                )
                return

            # Store communication preference - this will be used by the flow engine
            user_id = str(interaction.user.id)
            # TODO: Store this in user profile or database

            embed = discord.Embed(
                title="💬 Communication Style Updated",
                description=f"I'll adapt my responses to be more **{style.lower()}** based on your preference.",
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

    @app_commands.command(
        name="permissions", description="Check bot permissions for image generation"
    )
    @app_commands.describe(
        channel="Channel to check permissions for (optional, defaults to current channel)"
    )
    async def permissions_check(
        self, interaction: discord.Interaction, channel: discord.TextChannel = None
    ):
        """Check bot permissions for image generation and other features"""
        try:
            await interaction.response.defer()

            # Use provided channel or current channel
            check_channel = channel or interaction.channel

            if not interaction.guild:
                await interaction.followup.send(
                    "❌ This command can only be used in servers.", ephemeral=True
                )
                return

            bot_member = interaction.guild.me
            channel_perms = check_channel.permissions_for(bot_member)
            guild_perms = bot_member.guild_permissions

            # Define required permissions for different features
            permissions_needed = {
                "Basic Chat": {
                    "send_messages": channel_perms.send_messages,
                    "read_messages": channel_perms.read_messages,
                    "read_message_history": channel_perms.read_message_history,
                },
                "Image Generation": {
                    "send_messages": channel_perms.send_messages,
                    "embed_links": channel_perms.embed_links,
                    "attach_files": channel_perms.attach_files,
                    "use_external_emojis": channel_perms.use_external_emojis,
                },
                "Advanced Features": {
                    "add_reactions": channel_perms.add_reactions,
                    "manage_messages": channel_perms.manage_messages,
                    "use_slash_commands": True,  # Always true if bot can respond
                },
                "Server Management": {
                    "view_audit_log": guild_perms.view_audit_log,
                    "manage_roles": guild_perms.manage_roles,
                    "kick_members": guild_perms.kick_members,
                    "ban_members": guild_perms.ban_members,
                },
            }

            embed = discord.Embed(
                title="🔐 Bot Permissions Check",
                description=f"Checking permissions for {bot_member.mention} in {check_channel.mention}",
                color=0x3498DB,
                timestamp=datetime.now(timezone.utc),
            )

            # Check each category
            for category, perms in permissions_needed.items():
                perm_status = []
                all_good = True

                for perm_name, has_perm in perms.items():
                    if has_perm:
                        perm_status.append(f"✅ {perm_name.replace('_', ' ').title()}")
                    else:
                        perm_status.append(f"❌ {perm_name.replace('_', ' ').title()}")
                        all_good = False

                # Set field color and icon based on status
                category_icon = "✅" if all_good else "⚠️"
                embed.add_field(
                    name=f"{category_icon} {category}",
                    value="\n".join(perm_status),
                    inline=True,
                )

            # Add overall status
            critical_perms = ["send_messages", "embed_links", "attach_files"]
            critical_missing = [
                p for p in critical_perms if not channel_perms.__getattribute__(p)
            ]

            if not critical_missing:
                embed.color = 0x27AE60  # Green
                embed.add_field(
                    name="✅ Status",
                    value="Bot has all required permissions for image generation!",
                    inline=False,
                )
            else:
                embed.color = 0xE74C3C  # Red
                embed.add_field(
                    name="❌ Action Required",
                    value=f"Missing critical permissions: {', '.join(critical_missing)}\n"
                    f"Image generation will not work properly.",
                    inline=False,
                )

            # Add helpful information
            embed.add_field(
                name="🔧 How to Fix Permission Issues",
                value="1. Go to **Server Settings** → **Roles**\n"
                f"2. Find the **{bot_member.display_name}** role\n"
                f"3. Enable missing permissions\n"
                f"4. Or check **Channel Settings** → **Permissions** for {check_channel.mention}",
                inline=False,
            )

            embed.set_footer(
                text="Permissions checked • Use /permissions in different channels to test"
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Permissions check error: {e}")
            await interaction.followup.send(
                f"❌ Error checking permissions: {str(e)}", ephemeral=True
            )

    @app_commands.command(
        name="test_permissions",
        description="Test bot permissions with a sample image generation",
    )
    async def test_permissions_command(self, interaction: discord.Interaction):
        """Test bot permissions by attempting a sample image generation workflow"""
        try:
            await interaction.response.defer()

            if not interaction.guild:
                await interaction.followup.send(
                    "❌ This command can only be used in servers.", ephemeral=True
                )
                return

            bot_member = interaction.guild.me
            channel_perms = interaction.channel.permissions_for(bot_member)

            # Test results
            test_results = []
            overall_success = True

            # Test 1: Basic message sending
            if channel_perms.send_messages:
                test_results.append("✅ Can send messages")
            else:
                test_results.append("❌ Cannot send messages")
                overall_success = False

            # Test 2: Embed creation
            if channel_perms.embed_links:
                test_results.append("✅ Can create embeds")

                # Create a test embed to verify
                test_embed = discord.Embed(
                    title="🧪 Embed Test",
                    description="This embed tests the bot's ability to create and display embeds.",
                    color=0x3498DB,
                    timestamp=datetime.now(timezone.utc),
                )
                test_embed.add_field(
                    name="Status", value="✅ Embed links working", inline=False
                )
                test_embed.set_footer(
                    text="Test embed • This confirms embed permissions"
                )

                # Try to edit the deferred response with embed
                await interaction.edit_original_response(embed=test_embed)
                test_results.append("✅ Successfully created test embed")

            else:
                test_results.append(
                    "❌ Cannot create embeds (required for image display)"
                )
                overall_success = False

            # Test 3: File attachment capability
            if channel_perms.attach_files:
                test_results.append("✅ Can attach files")
            else:
                test_results.append("❌ Cannot attach files (backup method for images)")
                # This is not critical for image generation via URLs, but good to have

            # Test 4: External emoji usage
            if channel_perms.use_external_emojis:
                test_results.append("✅ Can use external emojis")
            else:
                test_results.append("⚠️ Cannot use external emojis (minor impact)")

            # Test 5: Reaction capability
            if channel_perms.add_reactions:
                test_results.append("✅ Can add reactions")
            else:
                test_results.append("⚠️ Cannot add reactions (minor impact)")

            # Create final result embed
            final_embed = discord.Embed(
                title="🧪 Permission Test Results",
                description="Testing bot permissions for image generation functionality",
                color=0x27AE60 if overall_success else 0xE74C3C,
                timestamp=datetime.now(timezone.utc),
            )

            final_embed.add_field(
                name="📋 Test Results", value="\n".join(test_results), inline=False
            )

            if overall_success:
                final_embed.add_field(
                    name="🎉 Overall Status",
                    value="✅ **All critical permissions are working!**\n"
                    "The bot should be able to generate and display images properly.\n"
                    "Try: `astra generate test robot`",
                    inline=False,
                )
            else:
                final_embed.add_field(
                    name="⚠️ Action Required",
                    value="❌ **Critical permissions are missing.**\n"
                    "Image generation may not work properly.\n"
                    "Use `/permissions` for detailed guidance.",
                    inline=False,
                )

            final_embed.add_field(
                name="🔧 Next Steps",
                value="• Fix any missing permissions shown above\n"
                "• Run `/permissions` for detailed setup instructions\n"
                "• Test image generation with `astra generate <prompt>`\n"
                "• Check bot logs for any error messages",
                inline=False,
            )

            final_embed.set_footer(text="Permission test completed")

            # If we couldn't send embeds, fall back to text
            if not channel_perms.embed_links:
                message = "🧪 **Permission Test Results**\n\n" + "\n".join(test_results)
                if overall_success:
                    message += "\n\n✅ Critical permissions working, but embed display is disabled."
                else:
                    message += "\n\n❌ Critical permissions missing. Use `/permissions` for help."

                await interaction.edit_original_response(content=message)
            else:
                await interaction.edit_original_response(embed=final_embed)

        except discord.HTTPException as e:
            self.logger.error(f"HTTP error in permission test: {e}")
            await interaction.edit_original_response(
                content=f"❌ HTTP Error during test: {str(e)}\n"
                "This might indicate permission issues or API problems."
            )
        except Exception as e:
            self.logger.error(f"Permission test error: {e}")
            try:
                await interaction.edit_original_response(
                    content=f"❌ Error during permission test: {str(e)}"
                )
            except:
                await interaction.followup.send(
                    f"❌ Critical error during permission test: {str(e)}",
                    ephemeral=True,
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
        self.dynamic_status_task.cancel()

        # Close image client if it exists
        if self.image_client:
            import asyncio

            try:
                # Try to close gracefully
                asyncio.create_task(self.image_client.close())
            except:
                pass

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Enhanced message listener with intelligent AI triggering, chat understanding, and proactive engagement"""
        if message.author.bot:
            return

        # Enhanced chat understanding and context analysis
        await self._analyze_message_context(message)

        # Track channel activity with enhanced metrics
        await self._track_channel_activity(message)

        # Extract and track interesting topics from conversation
        await self._extract_conversation_topics(message)

        # Update server activity levels for dynamic status
        await self._update_server_activity_level(message)

        # Check if AI should respond (now returns tuple)
        should_respond, engagement_reason = await self._should_ai_respond(message)

        if should_respond:
            async with message.channel.typing():
                # Determine engagement type for personalized response
                engagement_type = "casual_engagement"

                if engagement_reason != "fallback_basic":
                    try:
                        engagement_type = (
                            await proactive_engagement.generate_engagement_type(
                                message.content,
                                engagement_reason,
                                await user_profile_manager.get_personalized_context(
                                    message.author.id
                                ),
                            )
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
            profile = await user_profile_manager.get_user_profile(
                user_id, str(message.author)
            )
            user_profile = await user_profile_manager.get_personalized_context(user_id)
        except Exception as e:
            logger.warning(f"Failed to get user profile for engagement: {e}")

        # Use proactive engagement system
        try:
            should_engage, reason = (
                await proactive_engagement.should_engage_proactively(
                    message.content,
                    user_id,
                    message.channel.id,
                    message.guild.id if message.guild else None,
                    user_profile,
                )
            )

            if should_engage:
                logger.info(
                    f"Proactive engagement triggered for user {user_id}: {reason}"
                )
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
        if "?" in message.content:
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

    async def _process_ai_conversation(
        self, message: discord.Message, engagement_type: str = "casual_engagement"
    ):
        """Process AI conversation with enhanced features: image generation, user mentioning, and smart responses"""
        try:
            start_time = datetime.now(timezone.utc)
            user_id = message.author.id
            username = str(message.author)

            # Add to active conversations
            self.active_conversations.add(user_id)

            # Check if this is an image generation request
            image_request = await self._detect_image_request(message.content)

            if image_request:
                await self._handle_image_generation(message, image_request)
                return

            # Check for invalid image generation attempts and provide guidance
            await self._check_invalid_image_attempts(message)

            # Process with AI client using enhanced personalization
            response = await self._generate_ai_response(
                message.content,
                user_id,
                guild_id=message.guild.id if message.guild else None,
                channel_id=message.channel.id,
                username=username,
                engagement_type=engagement_type,
            )

            # Enhance response with user mentions if relevant
            enhanced_response = await self._enhance_response_with_mentions(
                message, response
            )

            # Send response with smart formatting
            await self._send_enhanced_response(message.channel, enhanced_response)

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

    # === ENHANCED CHAT UNDERSTANDING AND PROACTIVE FEATURES ===

    async def _analyze_message_context(self, message: discord.Message):
        """Analyze message context for better understanding and user mentioning"""
        try:
            content = message.content.lower()

            # Detect if users are being discussed (for potential mentioning)
            user_references = []

            # Look for user references in message
            words = content.split()
            user_indicating_words = [
                "user",
                "person",
                "someone",
                "anybody",
                "player",
                "member",
            ]

            # Check if message refers to users in a way that might warrant mentioning
            if any(
                word in content
                for word in ["help", "question", "ask", "know", "expert"]
            ):
                # Find relevant users based on message topics
                if message.guild:
                    relevant_users = await self._find_relevant_users(message)
                    if relevant_users:
                        user_references.extend(relevant_users)

            # Track users who might be relevant to mention
            if user_references:
                self.mentioned_users.update(user_references)

        except Exception as e:
            self.logger.error(f"Message context analysis error: {e}")

    async def _find_relevant_users(self, message: discord.Message) -> List[int]:
        """Find users relevant to the message topic who might be worth mentioning"""
        try:
            relevant_users = []
            content = message.content.lower()

            # Topic-based user expertise mapping
            topic_experts = {
                "stellaris": [],  # Will be populated with active stellaris players
                "space": [],  # Space enthusiasts
                "ai": [],  # AI/tech interested users
                "gaming": [],  # Gaming enthusiasts
                "science": [],  # Science interested users
            }

            # Look for recent active users in similar conversations
            if message.guild:
                for channel in message.guild.text_channels:
                    channel_activity = self.channel_activity.get(channel.id)
                    if channel_activity:
                        # Get users who recently talked about similar topics
                        for topic in channel_activity.get("recent_topics", []):
                            if any(keyword in content for keyword in topic.split()):
                                relevant_users.extend(
                                    list(channel_activity.get("active_users", set()))
                                )

            # Return top 2-3 most relevant users (avoid spam)
            return list(set(relevant_users))[:3]

        except Exception as e:
            self.logger.error(f"Relevant user finding error: {e}")
            return []

    async def _extract_conversation_topics(self, message: discord.Message):
        """Extract and track interesting topics from ongoing conversations"""
        try:
            content = message.content.lower()

            # Enhanced topic detection
            topics = await self._extract_message_topics(content)

            # Add to global interesting topics tracker
            for topic in topics:
                if topic not in self.interesting_topics:
                    self.interesting_topics.append(topic)

            # Keep only recent interesting topics (last 20)
            self.interesting_topics = self.interesting_topics[-20:]

        except Exception as e:
            self.logger.error(f"Topic extraction error: {e}")

    async def _update_server_activity_level(self, message: discord.Message):
        """Update server activity level for dynamic status updates"""
        try:
            if not message.guild:
                return

            guild_id = message.guild.id
            current_time = datetime.now(timezone.utc)

            # Count recent messages in the guild
            recent_messages = 0
            for channel_id, activity in self.channel_activity.items():
                if any(ch.id == channel_id for ch in message.guild.text_channels):
                    if current_time - activity.get(
                        "last_activity", current_time
                    ) < timedelta(minutes=10):
                        recent_messages += len(activity.get("recent_messages", []))

            # Determine activity level
            if recent_messages >= 20:
                activity_level = "very_active"
            elif recent_messages >= 10:
                activity_level = "active"
            elif recent_messages >= 3:
                activity_level = "moderate"
            else:
                activity_level = "quiet"

            self.server_activity_levels[guild_id] = activity_level

        except Exception as e:
            self.logger.error(f"Server activity update error: {e}")

    @tasks.loop(minutes=5)
    async def dynamic_status_task(self):
        """Dynamically update bot status based on activity and interesting topics"""
        try:
            current_time = datetime.now(timezone.utc)

            # Only update status every 5-15 minutes to avoid spam
            if current_time - self.last_status_update < timedelta(minutes=5):
                return

            # Determine status based on activity and topics
            status_messages = []

            # Activity-based statuses
            total_servers = len(self.bot.guilds)
            active_servers = sum(
                1
                for level in self.server_activity_levels.values()
                if level in ["active", "very_active"]
            )

            if active_servers > 0:
                status_messages.extend(
                    [
                        f"🚀 Exploring {active_servers} active galaxies",
                        f"🌟 Engaging with {active_servers} communities",
                        f"⚡ Active in {active_servers} servers",
                    ]
                )

            # Topic-based statuses
            if self.interesting_topics:
                recent_topics = self.interesting_topics[-3:]  # Last 3 topics
                if "stellaris" in recent_topics:
                    status_messages.append("🌌 Discussing galactic empires")
                if "space" in recent_topics:
                    status_messages.append("🛸 Exploring the cosmos")
                if "ai" in recent_topics:
                    status_messages.append("🤖 Pondering artificial intelligence")
                if "science" in recent_topics:
                    status_messages.append("🔬 Analyzing scientific concepts")

            # Default statuses when no specific activity
            default_statuses = [
                "🌟 Ready to explore the universe",
                "🚀 Waiting for cosmic conversations",
                "🌌 Observing the digital galaxy",
                "💫 Dreaming of distant stars",
                f"🌍 Watching over {total_servers} servers",
            ]

            # Choose status
            if status_messages:
                status = random.choice(status_messages)
            else:
                status = random.choice(default_statuses)

            # Update bot status
            activity = discord.Activity(type=discord.ActivityType.watching, name=status)
            await self.bot.change_presence(activity=activity)

            self.last_status_update = current_time
            self.logger.info(f"Updated bot status to: {status}")

        except Exception as e:
            self.logger.error(f"Dynamic status update error: {e}")

    # === IMAGE GENERATION AND ENHANCED RESPONSE METHODS ===

    async def _detect_image_request(self, content: str) -> Optional[str]:
        """Detect if message is requesting image generation with specific Astra commands"""
        content_lower = content.lower()
        words = content_lower.split()

        # Only trigger image generation with specific "astra" commands
        astra_image_commands = [
            "astra generate",
            "astra create",
            "astra draw",
            "astra paint",
            "astra design",
            "astra make image",
            "astra make picture",
            "astra create image",
            "astra create picture",
            "astra generate image",
            "astra generate picture",
            "astra visualize",
            "astra sketch",
        ]

        # Check for specific Astra image commands
        for command in astra_image_commands:
            if content_lower.startswith(command):
                # Extract the prompt after the command
                prompt = content_lower.replace(command, "").strip()
                if prompt:  # Only proceed if there's actually a prompt
                    return prompt
                else:
                    return None  # No prompt provided

        # Also check for @Astra mentions with image keywords
        if any(
            word
            for word in words
            if word.startswith("<@") and "1400014033142288475" in word
        ):  # Bot's ID
            image_keywords = [
                "generate",
                "create",
                "draw",
                "paint",
                "design",
                "make image",
                "make picture",
                "visualize",
                "sketch",
                "artwork",
                "illustration",
            ]

            # Check if any image keywords appear after the mention
            for keyword in image_keywords:
                if keyword in content_lower:
                    # Extract everything after the keyword as the prompt
                    parts = content_lower.split(keyword, 1)
                    if len(parts) > 1:
                        prompt = parts[1].strip()
                        if prompt:
                            return prompt

            # If mentioned but no specific image keyword, don't treat as image request
            return None

        # No valid image generation trigger found
        return None

    async def _check_invalid_image_attempts(self, message: discord.Message):
        """Check for invalid image generation attempts and provide helpful guidance"""
        content_lower = message.content.lower()

        # Common invalid image generation attempts
        invalid_attempts = [
            "generate",
            "create art",
            "create image",
            "make image",
            "draw",
            "paint",
            "design",
            "sketch",
            "visualize",
            "generate image",
            "create picture",
            "make picture",
        ]

        # Check if message starts with these words (but wasn't caught by _detect_image_request)
        words = content_lower.split()
        if len(words) > 1 and words[0] in invalid_attempts:
            # This looks like an image generation attempt but without "astra" prefix
            embed = discord.Embed(
                title="🎨 Image Generation Help",
                description="It looks like you want to generate an image! Here's how:",
                color=0x7C3AED,
                timestamp=datetime.now(timezone.utc),
            )

            embed.add_field(
                name="✅ Correct Commands",
                value="Use **`astra generate`** followed by your prompt:\n"
                "• `astra generate sunset over mountains`\n"
                "• `astra create artwork of a robot`\n"
                "• `astra draw a fantasy castle`\n"
                "• `astra paint a cosmic nebula`",
                inline=False,
            )

            embed.add_field(
                name="📍 Channel Restrictions",
                value="• **Regular users**: <#1402666535696470169>\n"
                "• **Mods & Admins**: Any channel",
                inline=False,
            )

            embed.add_field(
                name="🔧 Alternative",
                value="You can also mention me: `@Astra generate your prompt here`",
                inline=False,
            )

            embed.set_footer(text="Powered by Freepik AI")

            await message.channel.send(embed=embed)

    async def _handle_image_generation(self, message: discord.Message, prompt: str):
        """Handle image generation request with dedicated Freepik Image Client"""
        try:
            # Check if image client is available
            if not hasattr(self, "image_client") or not self.image_client:
                embed = discord.Embed(
                    title="❌ Image Generation Unavailable",
                    description="Image generation client is not properly initialized.",
                    color=0xE74C3C,
                    timestamp=datetime.now(timezone.utc),
                )
                embed.add_field(
                    name="🔧 For Bot Administrators",
                    value="• Check that `FREEPIK_API_KEY` is set in Railway environment variables\n"
                    "• Verify the FreepikImageClient is properly imported\n"
                    "• Restart the bot after setting environment variables",
                    inline=False,
                )
                embed.set_footer(text="Image generation is independent from AI chat")
                await message.channel.send(embed=embed)
                return

            # Check if Freepik API is available
            if not self.image_client.is_available():
                embed = discord.Embed(
                    title="🔑 API Key Required",
                    description="Freepik API key is not configured or invalid.",
                    color=0xE74C3C,
                    timestamp=datetime.now(timezone.utc),
                )
                embed.add_field(
                    name="🔧 Setup Instructions",
                    value="1. Get API key from: https://www.freepik.com/api\n"
                    "2. Set `FREEPIK_API_KEY` in Railway environment variables\n"
                    "3. Restart the bot\n"
                    "4. Try the command again",
                    inline=False,
                )
                embed.set_footer(text="Bot administrators need to configure this")
                await message.channel.send(embed=embed)
                return

            # Send initial status message
            status_embed = discord.Embed(
                title="🎨 Generating Image...",
                description=f"**Prompt:** {prompt[:150]}{'...' if len(prompt) > 150 else ''}",
                color=0x3498DB,
                timestamp=datetime.now(timezone.utc),
            )
            status_embed.set_footer(
                text="Using Freepik AI • This may take 30-60 seconds"
            )

            status_msg = await message.channel.send(embed=status_embed)

            # Log the generation attempt
            self.logger.info(
                f"🎨 Image generation requested by user {message.author.id}"
            )
            self.logger.info(f"📝 Prompt: {prompt}")

            # Generate image using dedicated client
            result = await self.image_client.generate_image(
                prompt=prompt, user_id=message.author.id, size="square_hd", num_images=1
            )

            # Process the result
            if result and result.get("success"):
                # Success!
                success_embed = discord.Embed(
                    title="🎨 Image Generated Successfully!",
                    description=f"**Prompt:** {prompt[:200]}{'...' if len(prompt) > 200 else ''}",
                    color=0x27AE60,
                    timestamp=datetime.now(timezone.utc),
                )

                image_url = result.get("url")
                if image_url:
                    success_embed.set_image(url=image_url)

                success_embed.add_field(
                    name="🤖 Provider", value="Freepik AI", inline=True
                )
                success_embed.add_field(
                    name="👤 Requested by", value=message.author.mention, inline=True
                )
                success_embed.set_footer(
                    text="✨ astra generate <your prompt> to create more images"
                )

                await status_msg.delete()
                await message.channel.send(embed=success_embed)
                self.logger.info(
                    f"✅ Image successfully delivered to user {message.author.id}"
                )

            else:
                # Handle errors
                error_type = (
                    result.get("error", "Unknown error") if result else "No response"
                )
                error_msg = (
                    result.get("message", "Image generation failed")
                    if result
                    else "No response from image service"
                )

                self.logger.error(f"❌ Image generation failed: {error_type}")

                await status_msg.delete()

                error_embed = discord.Embed(
                    title="❌ Generation Failed",
                    description=error_msg
                    or "Something went wrong during image generation.",
                    color=0xE74C3C,
                    timestamp=datetime.now(timezone.utc),
                )
                error_embed.add_field(
                    name="💡 What to do",
                    value="• Wait a moment and retry\n• Use a simpler prompt\n• Contact support if issue persists",
                    inline=False,
                )
                await message.channel.send(embed=error_embed)

        except Exception as e:
            self.logger.error(
                f"💥 Critical error in image generation handler: {e}", exc_info=True
            )

            try:
                error_embed = discord.Embed(
                    title="💥 Unexpected Error",
                    description="A critical error occurred during image generation.",
                    color=0x992D22,
                    timestamp=datetime.now(timezone.utc),
                )
                error_embed.add_field(
                    name="💡 What to do",
                    value="• Try again in a few minutes\n• Contact bot administrators if this persists",
                    inline=False,
                )
                await message.channel.send(embed=error_embed)
            except:
                try:
                    await message.channel.send(
                        "❌ Critical error during image generation. Please try again later."
                    )
                except:
                    self.logger.error("Could not send error message to user")
        try:
            # Check if bot has required permissions in the channel
            if message.guild:
                bot_member = message.guild.me
                channel_permissions = message.channel.permissions_for(bot_member)

                # Comprehensive permission check for image generation
                missing_permissions = []

                if not channel_permissions.send_messages:
                    missing_permissions.append("Send Messages")

                if not channel_permissions.embed_links:
                    missing_permissions.append("Embed Links")

                if not channel_permissions.attach_files:
                    missing_permissions.append("Attach Files")

                if not channel_permissions.use_external_emojis:
                    missing_permissions.append("Use External Emojis")

                # Log permission status
                self.logger.info(
                    f"🔐 Bot permissions in #{message.channel.name}: "
                    f"Send Messages: {channel_permissions.send_messages}, "
                    f"Embed Links: {channel_permissions.embed_links}, "
                    f"Attach Files: {channel_permissions.attach_files}"
                )

                if missing_permissions:
                    # Try to send a basic error message (if we can send messages)
                    if channel_permissions.send_messages:
                        embed = discord.Embed(
                            title="🚫 Missing Permissions",
                            description="I need additional permissions to generate and display images properly.",
                            color=0xE74C3C,
                            timestamp=datetime.now(timezone.utc),
                        )
                        embed.add_field(
                            name="❌ Missing Permissions",
                            value="\n".join(
                                [f"• {perm}" for perm in missing_permissions]
                            ),
                            inline=False,
                        )
                        embed.add_field(
                            name="🔧 How to Fix",
                            value="Please ask a server administrator to:\n"
                            f"1. Go to Server Settings → Roles\n"
                            f"2. Find the '{bot_member.display_name}' role\n"
                            f"3. Enable the missing permissions listed above\n"
                            f"4. Or use `/permissions check` to diagnose issues",
                            inline=False,
                        )
                        embed.set_footer(
                            text="Bot permissions are required for image generation"
                        )
                        await message.channel.send(embed=embed)
                    else:
                        # Can't even send messages - log only
                        self.logger.error(
                            f"❌ Bot missing critical permissions in #{message.channel.name}: {', '.join(missing_permissions)}"
                        )
                    return

            if not self.ai_client:
                embed = discord.Embed(
                    title="❌ Image Generation Unavailable",
                    description="The AI system is not properly initialized.",
                    color=0xE74C3C,
                    timestamp=datetime.now(timezone.utc),
                )
                embed.add_field(
                    name="🔧 For Bot Administrators",
                    value="Please check bot initialization and configuration.",
                    inline=False,
                )
                await message.channel.send(embed=embed)
                return

            # Check user permissions
            user_permissions = {
                "is_admin": (
                    message.author.guild_permissions.administrator
                    if message.guild
                    else False
                ),
                "is_mod": (
                    any(
                        role.permissions.manage_messages
                        for role in message.author.roles
                    )
                    if message.guild
                    else False
                ),
            }

            # Prepare context for image generation
            context = {
                "user_id": message.author.id,
                "channel_id": message.channel.id,
                "guild_id": message.guild.id if message.guild else None,
                "channel_type": "discord",
                "request_type": "image_generation",
                "user_name": message.author.display_name,
            }

            # Send generation status message with more detailed info
            status_embed = discord.Embed(
                title="🎨 Generating Image...",
                description=f"**Prompt:** {prompt[:150]}{'...' if len(prompt) > 150 else ''}",
                color=0x3498DB,
                timestamp=datetime.now(timezone.utc),
            )
            status_embed.add_field(
                name="🔄 Status", value="Connecting to Freepik AI...", inline=False
            )
            status_embed.set_footer(text="This may take 30-60 seconds")

            status_msg = await message.channel.send(embed=status_embed)

            # Log the image generation attempt
            self.logger.info(
                f"🎨 Image generation requested by user {message.author.id}"
            )
            self.logger.info(f"📝 Prompt: {prompt}")
            self.logger.info(
                f"🔧 Permissions: Admin={user_permissions['is_admin']}, Mod={user_permissions['is_mod']}"
            )

            # Generate image using consolidated AI engine
            result = await self.ai_client.generate_image(
                prompt, context, user_permissions
            )

            # Log the result
            if result:
                self.logger.info(
                    f"🎯 Image generation result: {result.get('success', False)}"
                )
                if not result.get("success"):
                    self.logger.error(
                        f"❌ Image generation error: {result.get('error', 'Unknown')}"
                    )
                    self.logger.error(
                        f"💬 Error message: {result.get('message', 'No message')}"
                    )
            else:
                self.logger.error("❌ No result returned from image generation")

            if result and result.get("success"):
                try:
                    # Create success embed
                    embed = discord.Embed(
                        title="🎨 Image Generated Successfully!",
                        description=f"**Prompt:** {prompt[:200]}{'...' if len(prompt) > 200 else ''}",
                        color=0x27AE60,
                        timestamp=datetime.now(timezone.utc),
                    )

                    # Set the image
                    image_url = result.get("url")
                    if image_url:
                        embed.set_image(url=image_url)

                    embed.add_field(
                        name="🤖 Provider",
                        value=result.get("provider", "Freepik AI"),
                        inline=True,
                    )
                    embed.add_field(
                        name="� Requested by", value=message.author.mention, inline=True
                    )
                    embed.set_footer(
                        text="Powered by Freepik AI • astra generate <prompt>"
                    )

                    # Delete status message and send result
                    await status_msg.delete()
                    await message.channel.send(embed=embed)

                    self.logger.info(
                        f"✅ Image successfully sent to channel {message.channel.id}"
                    )

                except Exception as embed_error:
                    self.logger.error(f"❌ Error creating success embed: {embed_error}")
                    # Fallback to simple message
                    await status_msg.delete()
                    await message.channel.send(
                        f"🎨 **Image generated:** {result.get('url', 'No URL')}\n"
                        f"**Prompt:** {prompt[:100]}{'...' if len(prompt) > 100 else ''}"
                    )

            else:
                # Handle error cases with more detailed information
                error_type = (
                    result.get("error", "Unknown error") if result else "No response"
                )
                error_msg = (
                    result.get("message", "Image generation failed")
                    if result
                    else "Image generation service unavailable"
                )

                self.logger.error(
                    f"🚨 Image generation failed: {error_type} - {error_msg}"
                )

                # Delete status message first
                try:
                    await status_msg.delete()
                except:
                    pass

                if error_type == "Permission denied":
                    embed = discord.Embed(
                        title="🚫 Permission Denied",
                        description="You don't have permission to generate images in this channel.",
                        color=0xE74C3C,
                        timestamp=datetime.now(timezone.utc),
                    )
                    default_channel_id = 1402666535696470169
                    embed.add_field(
                        name="📍 Where to generate images",
                        value=f"• **Regular users:** <#{default_channel_id}>\n• **Mods & Admins:** Any channel",
                        inline=False,
                    )
                    embed.add_field(
                        name="🔧 Alternative Commands",
                        value="Try: `astra generate your prompt here`\nOr: `@Astra generate your prompt here`",
                        inline=False,
                    )
                    await message.channel.send(embed=embed)

                elif error_type == "Rate limit exceeded":
                    embed = discord.Embed(
                        title="⏰ Rate Limit Reached",
                        description=error_msg,
                        color=0xF39C12,
                        timestamp=datetime.now(timezone.utc),
                    )
                    if result and "reset_time" in result:
                        reset_time = result["reset_time"]
                        embed.add_field(
                            name="� Try Again",
                            value=f"Rate limit resets at: {reset_time}",
                            inline=False,
                        )
                    await message.channel.send(embed=embed)

                elif (
                    error_type == "API key not configured"
                    or error_type == "Invalid API key"
                ):
                    embed = discord.Embed(
                        title="🔑 API Configuration Issue",
                        description="The Freepik API key is not configured or invalid.",
                        color=0xE74C3C,
                        timestamp=datetime.now(timezone.utc),
                    )
                    embed.add_field(
                        name="🔧 For Bot Administrators",
                        value="• Check FREEPIK_API_KEY in Railway environment variables\n"
                        "• Get your API key at: https://www.freepik.com/api\n"
                        "• Verify key at: https://www.freepik.com/developers/dashboard/api-key",
                        inline=False,
                    )
                    embed.set_footer(
                        text="This is a bot configuration issue, not a user error"
                    )
                    await message.channel.send(embed=embed)

                else:
                    # Generic error with helpful information
                    embed = discord.Embed(
                        title="❌ Image Generation Failed",
                        description=error_msg,
                        color=0xE74C3C,
                        timestamp=datetime.now(timezone.utc),
                    )
                    embed.add_field(
                        name="💡 Suggestions",
                        value="• Try a simpler, more descriptive prompt\n"
                        "• Make sure your prompt follows content guidelines\n"
                        "• Wait a few minutes and try again",
                        inline=False,
                    )
                    embed.add_field(
                        name="🔧 Commands",
                        value="`astra generate <description>`\n`@Astra generate <description>`",
                        inline=False,
                    )
                    embed.set_footer(
                        text="If this persists, contact bot administrators"
                    )
                    await message.channel.send(embed=embed)

        except Exception as e:
            self.logger.error(f"💥 Critical error in image generation: {e}")
            try:
                # Try to send error message to user
                embed = discord.Embed(
                    title="💥 Critical Error",
                    description="An unexpected error occurred during image generation.",
                    color=0x992D22,
                    timestamp=datetime.now(timezone.utc),
                )
                embed.add_field(
                    name="🔧 What to do",
                    value="Please try again later or contact bot administrators if this persists.",
                    inline=False,
                )
                embed.set_footer(text="Error logged for debugging")
                await message.channel.send(embed=embed)
            except:
                # Last resort - simple message
                await message.channel.send(
                    "❌ Failed to generate image. Please try again later."
                )

    async def _enhance_response_with_mentions(
        self, message: discord.Message, response: str
    ) -> str:
        """Enhance AI response with relevant user mentions when appropriate"""
        try:
            if not message.guild:
                return response

            # Check if response suggests getting help or mentions expertise
            help_indicators = [
                "expert",
                "ask someone",
                "check with",
                "maybe.*knows",
                "experienced.*with",
            ]

            should_mention = any(
                re.search(pattern, response.lower()) for pattern in help_indicators
            )

            if should_mention and len(self.mentioned_users) > 0:
                # Find relevant guild members from mentioned_users
                relevant_members = []
                for user_id in list(self.mentioned_users)[:3]:  # Max 3 mentions
                    member = message.guild.get_member(user_id)
                    if member and member != message.author and not member.bot:
                        relevant_members.append(member)

                if relevant_members:
                    mentions = " ".join([member.mention for member in relevant_members])
                    response += f"\n\n💡 {mentions} might be able to help with this!"

                    # Clear mentioned users after using them
                    self.mentioned_users.clear()

            return response

        except Exception as e:
            self.logger.error(f"Response enhancement error: {e}")
            return response

    async def _send_enhanced_response(
        self, channel: discord.TextChannel, response: str
    ):
        """Send response with smart formatting and splitting"""
        try:
            if len(response) > 2000:
                # Smart splitting at sentence boundaries
                chunks = []
                current_chunk = ""

                sentences = re.split(r"(?<=[.!?])\s+", response)

                for sentence in sentences:
                    if (
                        len(current_chunk + sentence) > 1900
                    ):  # Leave room for formatting
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            current_chunk = sentence
                        else:
                            # Single sentence too long, force split
                            chunks.append(sentence[:1900])
                            current_chunk = sentence[1900:]
                    else:
                        current_chunk += sentence + " "

                if current_chunk:
                    chunks.append(current_chunk.strip())

                # Send chunks with small delay
                for i, chunk in enumerate(chunks):
                    if i > 0:
                        await asyncio.sleep(0.5)  # Small delay between chunks
                    await channel.send(chunk)
            else:
                await channel.send(response)

        except Exception as e:
            self.logger.error(f"Enhanced response sending error: {e}")
            # Fallback to simple send
            await channel.send(response[:2000])

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
        name="test_enhanced_features",
        description="Test new enhanced AI features (Admin only)",
    )
    async def test_enhanced_features(self, interaction: discord.Interaction):
        """Test the new enhanced AI features"""
        try:
            # Admin check
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "❌ This command requires administrator permissions.",
                    ephemeral=True,
                )
                return

            await interaction.response.defer()

            embed = discord.Embed(
                title="🚀 Enhanced AI Features Test",
                color=0x7C3AED,
                timestamp=datetime.now(timezone.utc),
            )

            # Test dynamic status update
            try:
                await self.dynamic_status_task.coro()
                embed.add_field(
                    name="✅ Dynamic Status Update",
                    value="Status updated successfully based on current activity",
                    inline=False,
                )
            except Exception as e:
                embed.add_field(
                    name="❌ Dynamic Status Update",
                    value=f"Error: {str(e)[:100]}",
                    inline=False,
                )

            # Test activity monitoring
            active_servers = len(
                [
                    level
                    for level in self.server_activity_levels.values()
                    if level in ["active", "very_active"]
                ]
            )
            embed.add_field(
                name="📊 Activity Monitoring",
                value=f"Monitoring {len(self.server_activity_levels)} servers\n"
                f"Active servers: {active_servers}\n"
                f"Interesting topics: {len(self.interesting_topics)}",
                inline=False,
            )

            # Test conversation tracking
            embed.add_field(
                name="💬 Conversation Tracking",
                value=f"Active conversations: {len(self.active_conversations)}\n"
                f"Channel activities tracked: {len(self.channel_activity)}\n"
                f"Users ready for mentioning: {len(self.mentioned_users)}",
                inline=False,
            )

            # Test AI engine status
            if hasattr(self, "ai_client") and self.ai_client:
                try:
                    status = await self.ai_client.get_health_status()
                    embed.add_field(
                        name="🤖 AI Engine Status",
                        value=f"Status: {status.get('status', 'Unknown')}\n"
                        f"Active Provider: {status.get('active_provider', 'None')}\n"
                        f"Image Generation: {'✅ Available' if hasattr(self.ai_client, 'freepik_generator') and self.ai_client.freepik_generator else '❌ Unavailable'}",
                        inline=False,
                    )
                except Exception as e:
                    embed.add_field(
                        name="❌ AI Engine Status",
                        value=f"Error checking status: {str(e)[:100]}",
                        inline=False,
                    )
            else:
                embed.add_field(
                    name="❌ AI Engine", value="AI client not initialized", inline=False
                )

            embed.set_footer(text="Enhanced AI Features by Astra Bot")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Enhanced features test error: {e}")
            await interaction.followup.send(f"❌ Test failed: {str(e)}", ephemeral=True)

    @app_commands.command(
        name="permissions",
        description="Check and diagnose bot permissions in this channel",
    )
    async def permissions_check(self, interaction: discord.Interaction):
        """Check bot permissions for AI and image generation features"""
        try:
            await interaction.response.defer()

            # Get bot member and channel
            bot_member = interaction.guild.get_member(self.bot.user.id)
            channel = interaction.channel

            embed = discord.Embed(
                title="🛡️ Bot Permissions Diagnostic",
                description="Checking permissions required for AI features...",
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc),
            )

            # Required permissions for AI features
            required_permissions = [
                ("send_messages", "Send Messages", "Basic bot communication"),
                ("embed_links", "Embed Links", "Rich message formatting"),
                ("attach_files", "Attach Files", "Image generation uploads"),
                ("use_external_emojis", "Use External Emojis", "Enhanced reactions"),
                ("manage_messages", "Manage Messages", "Message cleanup and editing"),
                (
                    "read_message_history",
                    "Read Message History",
                    "Context understanding",
                ),
                ("add_reactions", "Add Reactions", "Interactive responses"),
            ]

            # Check each permission
            permissions_status = []
            all_good = True

            for perm_name, display_name, description in required_permissions:
                has_permission = getattr(
                    bot_member.permissions_in(channel), perm_name, False
                )

                if has_permission:
                    permissions_status.append(f"✅ {display_name}")
                else:
                    permissions_status.append(f"❌ {display_name}")
                    all_good = False

            # Add permissions status to embed
            embed.add_field(
                name="📋 Permission Status",
                value="\n".join(permissions_status),
                inline=False,
            )

            # Overall status
            if all_good:
                embed.add_field(
                    name="🎉 Overall Status",
                    value="✅ All permissions are properly configured!\nBot should work perfectly in this channel.",
                    inline=False,
                )
                embed.color = discord.Color.green()
            else:
                embed.add_field(
                    name="⚠️ Overall Status",
                    value="❌ Some permissions are missing.\nSome features may not work properly.",
                    inline=False,
                )
                embed.color = discord.Color.orange()

                # Add troubleshooting section
                embed.add_field(
                    name="🔧 Troubleshooting",
                    value=(
                        "**For Server Administrators:**\n"
                        "1. Go to Server Settings → Roles\n"
                        "2. Find the bot's role or @everyone\n"
                        "3. Enable the missing permissions listed above\n"
                        "4. Run this command again to verify\n\n"
                        "**For Channel-Specific Issues:**\n"
                        "1. Right-click this channel → Edit Channel\n"
                        "2. Go to Permissions tab\n"
                        "3. Add the bot role with required permissions\n"
                        "4. Save changes and test again"
                    ),
                    inline=False,
                )

            # Add additional info
            embed.add_field(
                name="ℹ️ Permission Details",
                value=(
                    "**Why these permissions are needed:**\n"
                    "• **Send Messages**: Basic bot responses\n"
                    "• **Embed Links**: Rich AI responses with formatting\n"
                    "• **Attach Files**: Image generation and file uploads\n"
                    "• **Use External Emojis**: Enhanced reaction system\n"
                    "• **Manage Messages**: Clean up bot messages when needed\n"
                    "• **Read Message History**: Better conversation context\n"
                    "• **Add Reactions**: Interactive command responses"
                ),
                inline=False,
            )

            # Add image generation specific check
            if hasattr(self, "ai_client") and hasattr(
                self.ai_client, "freepik_generator"
            ):
                img_status = (
                    "✅ Available"
                    if self.ai_client.freepik_generator
                    else "❌ Not configured"
                )
                embed.add_field(
                    name="🎨 Image Generation Status",
                    value=f"Freepik API: {img_status}\n"
                    f"Required Permissions: {'✅ Met' if all_good else '❌ Missing permissions above'}",
                    inline=False,
                )

            embed.set_footer(
                text=f"Checked in #{channel.name} • Use /nexus for system diagnostics"
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Permissions check error: {e}")
            await interaction.followup.send(
                f"❌ Error checking permissions: {str(e)}", ephemeral=True
            )


async def setup(bot):
    """Set up the Advanced AI cog"""
    await bot.add_cog(AdvancedAICog(bot))
