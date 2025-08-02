"""
Enhanced AI Handler for Astra Bot
Provides comprehensive AI capabilities including Azure OpenAI, image generation, and TTS
"""

import asyncio
import aiohttp
import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
import base64
import io

# Azure OpenAI imports
from openai import AsyncAzureOpenAI
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, AudioConfig
from azure.cognitiveservices.speech.audio import AudioOutputConfig

logger = logging.getLogger("astra.ai_handler")


class EnhancedAIHandler:
    """Enhanced AI handler with Azure integration and advanced features"""

    def __init__(self):
        # Load environment variables
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_openai_key = os.getenv("AZURE_OPENAI_KEY")
        self.azure_openai_version = os.getenv("AZURE_OPENAI_VERSION", "2024-02-01")
        self.azure_speech_key = os.getenv("AZURE_SPEECH_KEY")
        self.azure_speech_region = os.getenv("AZURE_SPEECH_REGION")

        # Model configurations
        self.chat_deployment = os.getenv("AZURE_CHAT_DEPLOYMENT", "gpt-4")
        self.dalle_deployment = os.getenv("AZURE_DALLE_DEPLOYMENT", "dall-e-3")

        # Initialize Azure OpenAI client
        if self.azure_openai_endpoint and self.azure_openai_key:
            self.client = AsyncAzureOpenAI(
                azure_endpoint=self.azure_openai_endpoint,
                api_key=self.azure_openai_key,
                api_version=self.azure_openai_version,
            )
        else:
            self.client = None
            logger.warning("Azure OpenAI credentials not found")

        # Initialize Azure Speech Service
        if self.azure_speech_key and self.azure_speech_region:
            self.speech_config = SpeechConfig(
                subscription=self.azure_speech_key, region=self.azure_speech_region
            )
        else:
            self.speech_config = None
            logger.warning("Azure Speech credentials not found")

        # Load configuration
        self.config = self._load_config()

        # Initialize storage
        self.conversation_history = {}
        self.usage_stats = self._load_usage_stats()
        self.current_personality = self._load_personality("default")

        # Create necessary directories
        Path("data/ai").mkdir(parents=True, exist_ok=True)
        Path("ai/personalities").mkdir(parents=True, exist_ok=True)

        logger.info("Enhanced AI Handler initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Load AI configuration with error handling"""
        config_path = Path("ai/ai_config.json")

        try:
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:  # Check if file is not empty
                        return json.loads(content)
                    else:
                        logger.warning("AI config file is empty, using defaults")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in AI config file: {e}")
        except Exception as e:
            logger.error(f"Error loading AI config: {e}")

        # Default configuration
        default_config = {
            "max_history": 20,
            "temperature": 0.7,
            "max_tokens": 1500,
            "image_size": "1024x1024",
            "image_quality": "hd",
            "tts_voice": "en-US-AriaNeural",
            "trigger_modes": {
                "mention": True,
                "dm": True,
                "dedicated_channels": [],
                "keyword": "astra",
            },
            "response_settings": {
                "use_embeds": True,
                "show_thinking": True,
                "max_response_length": 2000,
            },
        }

        # Save default config
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=2)

        return default_config

    def _load_usage_stats(self) -> Dict[str, int]:
        """Load usage statistics with error handling"""
        stats_path = Path("data/ai/usage_stats.json")

        try:
            if stats_path.exists():
                with open(stats_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in usage stats file: {e}")
        except Exception as e:
            logger.error(f"Error loading usage stats: {e}")

        return {
            "chat_messages": 0,
            "images_generated": 0,
            "tts_requests": 0,
            "total_tokens_used": 0,
        }

    def _save_usage_stats(self):
        """Save usage statistics"""
        stats_path = Path("data/ai/usage_stats.json")
        with open(stats_path, "w") as f:
            json.dump(self.usage_stats, f, indent=2)

    def _load_personality(self, name: str) -> Dict[str, Any]:
        """Load personality profile with error handling"""
        personality_path = Path(f"ai/personalities/{name}.json")

        try:
            if personality_path.exists():
                with open(personality_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in personality file {name}: {e}")
        except Exception as e:
            logger.error(f"Error loading personality {name}: {e}")

        # Create default personality if it doesn't exist
        default_personality = {
            "name": "Astra Default",
            "description": "A knowledgeable and friendly AI assistant for space exploration and Stellaris discussions",
            "system_prompt": """You are Astra, an advanced AI assistant specialized in space exploration, astronomy, and the Stellaris strategy game. You are helpful, knowledgeable, and engaging.

Key traits:
- Enthusiastic about space and science
- Knowledgeable about Stellaris lore and gameplay
- Friendly and approachable
- Uses space-themed emojis occasionally
- Provides detailed but accessible explanations
- Maintains a slightly futuristic, cosmic perspective

Always stay in character as Astra and provide helpful, accurate information while being conversational and engaging.""",
            "temperature": 0.7,
            "max_tokens": 1500,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1,
        }

        # Save default personality
        with open(personality_path, "w") as f:
            json.dump(default_personality, f, indent=2)

        return default_personality

    async def add_message_to_history(
        self,
        channel_id: int,
        user_id: int,
        username: str,
        content: str,
        is_bot: bool = False,
    ):
        """Add message to conversation history"""
        if channel_id not in self.conversation_history:
            self.conversation_history[channel_id] = []

        # Limit history size
        max_history = self.config.get("max_history", 20)
        if len(self.conversation_history[channel_id]) >= max_history:
            self.conversation_history[channel_id].pop(0)

        message = {
            "role": "assistant" if is_bot else "user",
            "content": content,
            "name": username,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
        }

        self.conversation_history[channel_id].append(message)

    async def get_ai_response(
        self,
        channel_id: int,
        response_type: str = "text",
        custom_prompt: Optional[str] = None,
    ) -> str:
        """Generate AI response using Azure OpenAI"""
        if not self.client:
            return "❌ AI service not available. Please check configuration."

        try:
            # Prepare messages for API
            messages = [
                {
                    "role": "system",
                    "content": custom_prompt
                    or self.current_personality["system_prompt"],
                }
            ]

            # Add conversation history
            if channel_id in self.conversation_history:
                for msg in self.conversation_history[channel_id][
                    -10:
                ]:  # Last 10 messages
                    messages.append({"role": msg["role"], "content": msg["content"]})

            # Generate response
            response = await self.client.chat.completions.create(
                model=self.chat_deployment,
                messages=messages,
                temperature=self.current_personality.get("temperature", 0.7),
                max_tokens=self.current_personality.get("max_tokens", 1500),
                frequency_penalty=self.current_personality.get(
                    "frequency_penalty", 0.1
                ),
                presence_penalty=self.current_personality.get("presence_penalty", 0.1),
            )

            # Extract response text
            response_text = response.choices[0].message.content.strip()

            # Update usage stats
            self.usage_stats["chat_messages"] += 1
            self.usage_stats["total_tokens_used"] += response.usage.total_tokens
            self._save_usage_stats()

            return response_text

        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "❌ Sorry, I encountered an error generating a response. Please try again."

    async def generate_image(
        self,
        prompt: str,
        style: str = "realistic",
        size: str = "1024x1024",
        quality: str = "hd",
    ) -> Tuple[Optional[str], Optional[str]]:
        """Generate image using DALL-E via Azure OpenAI"""
        if not self.client:
            return None, None

        try:
            # Enhance prompt based on style
            enhanced_prompt = self._enhance_image_prompt(prompt, style)

            response = await self.client.images.generate(
                model=self.dalle_deployment,
                prompt=enhanced_prompt,
                size=size,
                quality=quality,
                n=1,
            )

            if response.data:
                image_url = response.data[0].url
                revised_prompt = getattr(
                    response.data[0], "revised_prompt", enhanced_prompt
                )

                # Update usage stats
                self.usage_stats["images_generated"] += 1
                self._save_usage_stats()

                return image_url, revised_prompt

        except Exception as e:
            logger.error(f"Error generating image: {e}")

        return None, None

    def _enhance_image_prompt(self, prompt: str, style: str) -> str:
        """Enhance image prompt based on style"""
        style_enhancements = {
            "realistic": "photorealistic, high detail, professional photography",
            "artistic": "digital art, concept art, highly detailed artwork",
            "sci-fi": "futuristic, sci-fi concept art, space theme, high tech",
            "fantasy": "fantasy art, magical, ethereal, mystical atmosphere",
            "cartoon": "cartoon style, animated, colorful, playful",
            "cyberpunk": "cyberpunk aesthetic, neon lights, futuristic cityscape",
            "space": "space theme, cosmic, stellar, astronomical, galaxy",
        }

        enhancement = style_enhancements.get(style.lower(), "high quality, detailed")
        return f"{prompt}, {enhancement}"

    async def text_to_speech(
        self,
        text: str,
        voice: str = "en-US-AriaNeural",
        rate: str = "medium",
        pitch: str = "medium",
    ) -> Optional[bytes]:
        """Convert text to speech using Azure Speech Service"""
        if not self.speech_config:
            # Fallback to OpenAI TTS if Azure Speech not available
            return await self._openai_tts_fallback(text, voice)

        try:
            # Configure speech synthesis
            self.speech_config.speech_synthesis_voice_name = voice

            # Create synthesizer with memory stream output
            audio_config = AudioOutputConfig(use_default_speaker=False)
            synthesizer = SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=None,  # No audio output, we'll get the data
            )

            # Generate SSML for better control
            ssml = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
                <voice name="{voice}">
                    <prosody rate="{rate}" pitch="{pitch}">
                        {text}
                    </prosody>
                </voice>
            </speak>
            """

            # Synthesize speech
            result = synthesizer.speak_ssml(ssml)

            if result.reason == result.reason.SynthesizingAudioCompleted:
                # Update usage stats
                self.usage_stats["tts_requests"] += 1
                self._save_usage_stats()

                return result.audio_data
            else:
                logger.error(f"Speech synthesis failed: {result.reason}")
                return None

        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
            return None

    async def _openai_tts_fallback(self, text: str, voice: str) -> Optional[bytes]:
        """Fallback TTS using OpenAI API"""
        if not self.client:
            return None

        try:
            # Map voice names to OpenAI voices
            voice_mapping = {
                "alloy": "alloy",
                "echo": "echo",
                "fable": "fable",
                "onyx": "onyx",
                "nova": "nova",
                "shimmer": "shimmer",
            }

            openai_voice = voice_mapping.get(voice.lower(), "alloy")

            response = await self.client.audio.speech.create(
                model="tts-1-hd", voice=openai_voice, input=text
            )

            # Update usage stats
            self.usage_stats["tts_requests"] += 1
            self._save_usage_stats()

            return response.content

        except Exception as e:
            logger.error(f"Error in OpenAI TTS fallback: {e}")
            return None

    async def set_personality(self, personality_name: str) -> bool:
        """Set AI personality"""
        try:
            personality = self._load_personality(personality_name)
            self.current_personality = personality
            logger.info(f"Personality set to: {personality_name}")
            return True
        except Exception as e:
            logger.error(f"Error setting personality: {e}")
            return False

    def list_personalities(self) -> List[str]:
        """List available personalities"""
        personalities_dir = Path("ai/personalities")
        if not personalities_dir.exists():
            return ["default"]

        personalities = []
        for file in personalities_dir.glob("*.json"):
            personalities.append(file.stem)

        return personalities if personalities else ["default"]

    async def clear_history(self, channel_id: int):
        """Clear conversation history for channel"""
        if channel_id in self.conversation_history:
            del self.conversation_history[channel_id]

    async def get_usage_stats(self) -> Dict[str, int]:
        """Get usage statistics"""
        return self.usage_stats.copy()

    def get_current_personality(self) -> Dict[str, Any]:
        """Get current personality settings"""
        return self.current_personality.copy()

    # Enhanced API methods for compatibility

    async def get_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> Dict[str, Any]:
        """Enhanced chat completion with comprehensive error handling"""
        try:
            if not self.client:
                return {
                    "content": "AI service not available",
                    "tokens_used": 0,
                    "model": model,
                    "error": "Client not initialized",
                }

            # Use existing get_ai_response method but with enhanced return
            response = await self.client.chat.completions.create(
                model=self.chat_deployment,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=30.0,
            )

            result = {
                "content": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
                "model": self.chat_deployment,
                "finish_reason": response.choices[0].finish_reason,
            }

            # Update usage stats
            self.usage_stats["chat_messages"] += 1
            self.usage_stats["total_tokens_used"] += response.usage.total_tokens
            self._save_usage_stats()

            return result

        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            return {
                "content": "I apologize, but I'm currently unable to process your request.",
                "tokens_used": 0,
                "model": model,
                "error": str(e),
            }

    async def generate_embeddings(
        self, texts: List[str], model: str = "text-embedding-3-small"
    ) -> List[List[float]]:
        """Generate embeddings with Azure OpenAI"""
        try:
            if not self.client or not texts:
                return []

            # Clean texts
            clean_texts = [
                str(text).strip()[:8000] for text in texts if str(text).strip()
            ]
            if not clean_texts:
                return []

            # Process in batches
            batch_size = 100
            all_embeddings = []

            for i in range(0, len(clean_texts), batch_size):
                batch = clean_texts[i : i + batch_size]

                try:
                    response = await self.client.embeddings.create(
                        input=batch,
                        model="text-embedding-ada-002",  # Use available Azure model
                        timeout=30.0,
                    )

                    batch_embeddings = [data.embedding for data in response.data]
                    all_embeddings.extend(batch_embeddings)

                    # Track usage
                    self.usage_stats["total_tokens_used"] += response.usage.total_tokens

                    # Rate limiting
                    if i + batch_size < len(clean_texts):
                        await asyncio.sleep(0.1)

                except Exception as e:
                    logger.error(f"Embedding batch failed: {e}")
                    all_embeddings.extend([[] for _ in batch])

            self._save_usage_stats()
            return all_embeddings

        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return [[] for _ in texts]

    async def moderate_content(self, text: str) -> Dict[str, Any]:
        """Content moderation with Azure OpenAI"""
        try:
            if not self.client or not text.strip():
                return {
                    "flagged": False,
                    "categories": {},
                    "category_scores": {},
                    "safe": True,
                }

            response = await self.client.moderations.create(
                input=text.strip()[:32000], timeout=15.0
            )

            result = response.results[0]

            moderation_result = {
                "flagged": result.flagged,
                "categories": dict(result.categories),
                "category_scores": dict(result.category_scores),
                "safe": not result.flagged,
                "highest_score_category": (
                    max(result.category_scores.items(), key=lambda x: x[1])[0]
                    if result.category_scores
                    else "none"
                ),
                "risk_level": self._calculate_risk_level(dict(result.category_scores)),
            }

            if result.flagged:
                logger.warning(f"Content flagged: {list(result.categories.keys())}")

            return moderation_result

        except Exception as e:
            logger.error(f"Content moderation failed: {e}")
            return {
                "flagged": False,
                "categories": {},
                "category_scores": {},
                "safe": True,
                "error": str(e),
            }

    def _calculate_risk_level(self, scores: Dict[str, float]) -> str:
        """Calculate risk level from moderation scores"""
        if not scores:
            return "minimal"

        max_score = max(scores.values())

        if max_score >= 0.8:
            return "high"
        elif max_score >= 0.5:
            return "medium"
        elif max_score >= 0.2:
            return "low"
        else:
            return "minimal"

    async def speech_to_text(
        self, audio_data: bytes, language: str = "en"
    ) -> Dict[str, Any]:
        """Enhanced speech-to-text with Azure Speech Services"""
        try:
            if not audio_data:
                return {
                    "text": "",
                    "language": language,
                    "confidence": 0.0,
                    "error": "Empty audio data",
                }

            # Try Azure Speech Service first
            if self.speech_config:
                try:
                    # Azure Speech implementation would go here
                    # For now, return a placeholder
                    return {
                        "text": "Azure Speech recognition not fully implemented",
                        "language": language,
                        "confidence": 0.0,
                        "service": "azure_speech",
                    }
                except Exception as e:
                    logger.warning(f"Azure speech-to-text failed: {e}")

            # Fallback to OpenAI Whisper
            if self.client:
                try:
                    import tempfile
                    import os

                    with tempfile.NamedTemporaryFile(
                        suffix=".wav", delete=False
                    ) as temp_file:
                        temp_file.write(audio_data)
                        temp_file_path = temp_file.name

                    try:
                        with open(temp_file_path, "rb") as audio_file:
                            response = await self.client.audio.transcriptions.create(
                                model="whisper-1",
                                file=audio_file,
                                language=language,
                                timeout=60.0,
                            )

                        return {
                            "text": response.text,
                            "language": language,
                            "confidence": 0.9,
                            "service": "openai_whisper",
                        }

                    finally:
                        os.unlink(temp_file_path)

                except Exception as e:
                    logger.error(f"OpenAI speech-to-text failed: {e}")

            return {
                "text": "",
                "language": language,
                "confidence": 0.0,
                "error": "No speech service available",
            }

        except Exception as e:
            logger.error(f"Speech-to-text failed: {e}")
            return {
                "text": "",
                "language": language,
                "confidence": 0.0,
                "error": str(e),
            }

    async def get_usage_statistics(self) -> Dict[str, Any]:
        """Get comprehensive usage statistics"""
        base_stats = await self.get_usage_stats()

        # Add service health
        service_health = {
            "azure_openai_status": "healthy" if self.client else "unavailable",
            "azure_speech_status": "healthy" if self.speech_config else "unavailable",
            "last_request_time": getattr(self, "_last_request_time", None),
            "current_personality": self.current_personality.get("name", "unknown"),
        }

        return {
            **base_stats,
            "service_health": service_health,
            "estimated_cost": self._estimate_total_cost(),
            "conversation_channels": len(self.conversation_history),
        }

    def _estimate_total_cost(self) -> float:
        """Estimate total cost based on usage"""
        # Rough cost estimation
        tokens_used = self.usage_stats.get("total_tokens_used", 0)
        chat_messages = self.usage_stats.get("chat_messages", 0)
        images_generated = self.usage_stats.get("images_generated", 0)
        tts_requests = self.usage_stats.get("tts_requests", 0)

        # Rough pricing (adjust based on actual Azure pricing)
        token_cost = (tokens_used / 1000) * 0.005  # $0.005 per 1K tokens
        image_cost = images_generated * 0.04  # ~$0.04 per image
        tts_cost = tts_requests * 0.015  # ~$0.015 per request

        return round(token_cost + image_cost + tts_cost, 4)

    async def cleanup(self):
        """Enhanced cleanup with comprehensive resource management"""
        try:
            # Save final usage stats
            self._save_usage_stats()

            # Clear conversation history
            self.conversation_history.clear()

            # Close Azure OpenAI client
            if self.client and hasattr(self.client, "_client"):
                await self.client._client.aclose()

            # Clear Azure Speech resources
            self.speech_config = None

            logger.info("Enhanced AI handler cleaned up successfully")

        except Exception as e:
            logger.error(f"AI handler cleanup error: {e}")
