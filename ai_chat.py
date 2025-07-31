import json
import os
import logging
import asyncio
import discord
from typing import List, Dict, Optional, Union, Any
from datetime import datetime
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("astra.ai_chat")

# Load environment variables
load_dotenv()


class AIChatHandler:
    """Handles AI chat interactions for Astra Discord bot."""

    def __init__(self):
        # Initialize API keys from environment variables
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        # Set default API provider
        self.current_provider = "openai"

        # Load configuration
        self.config = self._load_config()

        # Set up API clients - UPDATED FOR OPENAI v1.0+
        if self.openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=self.openai_api_key)
        else:
            self.openai_client = None

        # Initialize conversation history storage
        self.conversation_history = {}

    def _load_config(self) -> Dict[str, Any]:
        """Load AI configuration from file."""
        try:
            with open("ai_config.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("AI config file not found. Using default settings.")
            return {
                "default_personality": "assistant",
                "max_history": 10,
                "temperature": 0.7,
                "max_tokens": 500,
            }

    def _save_config(self) -> None:
        """Save current configuration to file."""
        with open("ai_config.json", "w") as f:
            json.dump(self.config, f, indent=2)

    def load_personality(self, personality_name: str) -> Dict[str, Any]:
        """Load a personality profile from file."""
        try:
            path = f"personality_profiles/{personality_name}.json"
            with open(path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(
                f"Personality profile '{personality_name}' not found. Using default."
            )
            return {
                "system_prompt": "You are Astra, a helpful AI assistant for a Discord server.",
                "temperature": 0.7,
                "max_tokens": 500,
            }

    def list_personalities(self) -> List[str]:
        """List all available personality profiles."""
        profiles_dir = "personality_profiles"
        if not os.path.exists(profiles_dir):
            os.makedirs(profiles_dir)

        personalities = []
        for file in os.listdir(profiles_dir):
            if file.endswith(".json"):
                personalities.append(file[:-5])
        return personalities

    async def add_message_to_history(
        self,
        channel_id: int,
        user_id: int,
        username: str,
        content: str,
        is_bot: bool = False,
    ) -> None:
        """Add a message to the conversation history for a channel."""
        if channel_id not in self.conversation_history:
            self.conversation_history[channel_id] = []

        # Limit history size
        if len(self.conversation_history[channel_id]) >= self.config.get(
            "max_history", 10
        ):
            self.conversation_history[channel_id].pop(0)

        message = {
            "role": "assistant" if is_bot else "user",
            "name": username if not is_bot else "Astra",
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }

        self.conversation_history[channel_id].append(message)

    async def clear_history(self, channel_id: int) -> bool:
        """Clear the conversation history for a channel."""
        if channel_id in self.conversation_history:
            self.conversation_history[channel_id] = []
            return True
        return False

    async def get_ai_response(
        self, channel_id: int, personality: Optional[str] = None
    ) -> str:
        """Get a response from the AI based on conversation history."""
        if channel_id not in self.conversation_history:
            return "I don't have any conversation context yet."

        # Load personality profile
        if personality is None:
            personality = self.config.get("default_personality", "assistant")

        personality_profile = self.load_personality(personality)
        system_prompt = personality_profile.get(
            "system_prompt", "You are Astra, a helpful AI assistant."
        )

        # Format conversation for the API
        messages = [{"role": "system", "content": system_prompt}]
        for msg in self.conversation_history[channel_id]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        try:
            return await self._get_openai_response(messages, personality_profile)
        except Exception as e:
            logger.error(f"Error getting AI response: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}"

    async def _get_openai_response(
        self, messages: List[Dict], personality_profile: Dict
    ) -> str:
        """Get a response from OpenAI API."""
        if not self.openai_api_key or not self.openai_client:
            return "OpenAI API key is not configured. Please set OPENAI_API_KEY environment variable."

        try:
            # Get model preference from personality or default to GPT-4o-mini (cheaper)
            model = personality_profile.get("openai_model", "gpt-4o-mini")
            temperature = personality_profile.get(
                "temperature", self.config.get("temperature", 0.7)
            )
            max_tokens = personality_profile.get(
                "max_tokens", self.config.get("max_tokens", 500)
            )

            # UPDATED FOR OPENAI v1.0+ API
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return f"Sorry, I encountered an error with OpenAI: {str(e)}"

    async def set_personality(self, personality_name: str) -> bool:
        """Set the default personality for the bot."""
        if personality_name in self.list_personalities():
            self.config["default_personality"] = personality_name
            self._save_config()
            return True
        return False

    async def change_provider(self, provider: str) -> bool:
        """Change the AI provider."""
        valid_providers = ["openai"]  # Add others when implemented
        if provider in valid_providers:
            self.current_provider = provider
            self.config["provider"] = provider
            self._save_config()
            return True
        return False